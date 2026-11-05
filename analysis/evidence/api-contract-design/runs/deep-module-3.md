# Billing API v1

Public HTTP contract for invoices and payments.

## Scope and assumptions

Operations: list invoices, read one, create a draft, edit a draft, charge an
open invoice. Issuing a draft (making it `open`), voiding, webhooks, and plans
are out of scope for v1 — absent by decision, not omission.

Assumptions: draft→open and →void happen in an internal tool; currency is set
at creation and immutable; invoices are paid in full; the caller supplies a
payment-method token minted elsewhere; the service owns money arithmetic.

## Why this shape

The module is "invoice and payment access for external tenants". **Deletion
test:** without it, every caller re-implements tenant scoping, keyset paging,
retry de-duplication, optimistic concurrency, and provider-uncertainty
handling, so it earns its keep. **Depth:** five operations hide tenancy,
pagination, versioning, idempotency, a payment state machine, and an unstable
provider. **Seam:** the HTTP boundary, crossed by three real callers (web,
mobile, partner); the provider seam stays internal, its response shape outside
this contract.

Alternatives: (A) thin CRUD mirroring the service — offset paging, synchronous
charge, no preconditions; provider latency leaks into a 10-second client
timeout. (B) one `POST /v1/rpc` with an action field — callers must learn
action names and HTTP retry semantics stop applying. (C) this design: (A) is
shallow, (B) hides its interface in payload strings, (C) wins.

## Conventions

Base path `/v1`; JSON only. IDs are opaque. Timestamps are RFC 3339 UTC (`Z`).
Money is integer minor units (`amount_cents`) plus ISO 4217 `currency`; no
floats. `tenant_id` never appears — it comes from the API key. Unknown request
fields are rejected (`422`) so typos fail loudly; unknown response fields must
be ignored.

## Authentication and tenancy

`Authorization: Bearer <api-key>`. Missing or invalid → `401 INVALID_API_KEY`.
Every query is tenant-scoped at the storage layer. Another tenant's resource
returns `404 NOT_FOUND`, identical to a nonexistent one; `403` is only for a
valid key lacking a scope. Keys are per-tenant and per-environment.

## Resources

**Invoice** — `id`, `customer_id`, `status` (`draft|open|paid|void`),
`currency`, `version`, `created_at`, `updated_at`, `lines`, `total_cents`.

```json
{ "id": "inv_8f2", "customer_id": "cus_41", "status": "draft",
  "currency": "EUR", "version": 3,
  "created_at": "2026-11-01T09:00:00Z", "updated_at": "2026-11-05T10:12:00Z",
  "lines": [{ "id": "ln_1", "description": "Seats", "quantity": 3,
              "unit_amount_cents": 1500, "position": 0 }],
  "total_cents": 4500 }
```

`total_cents` is Σ `quantity × unit_amount_cents`, read-only, never sent by
clients. **Payment** — `id`, `invoice_id`, `amount_cents`, `currency`,
`status` (`pending|succeeded|failed|unknown`), `failure_code` (stable token
such as `card_declined`, or null), `created_at`, `updated_at`. The provider's
charge id and raw payload are not exposed; they change shape and belong to
internal reconciliation.

## Operations

### GET /v1/invoices

Query: `customer_id`, `status`, `created_from` (inclusive), `created_to`
(exclusive), `limit` (1–100, default 25), `cursor`. Fixed order
`created_at DESC, id DESC`.

```json
{ "data": [ /* invoices, without lines */ ],
  "next_cursor": "eyJjIjoiMjAyNi0xMS0wNVQxMDowMDowMFoiLCJpIjoiaW52XzhmMiJ9",
  "has_more": true }
```

`cursor` is opaque, signed, valid only with the same filter set; changing
filters means dropping it. Bad or mismatched cursor → `400 INVALID_CURSOR`. No
total count: counting 50,000 rows per page is not worth the latency. List items
omit `lines` to keep pages small.

### GET /v1/invoices/{invoice_id}

→ `200`, invoice body, `ETag: "3"`. `404` if absent or foreign.

### POST /v1/invoices

Creates a draft; requires `Idempotency-Key`.

```json
{ "customer_id": "cus_41", "currency": "EUR",
  "lines": [{ "description": "Seats", "quantity": 3, "unit_amount_cents": 1500 }] }
```

→ `201`, `Location: /v1/invoices/inv_8f2`, `ETag: "1"`, invoice body.
Unknown or foreign customer → `404 CUSTOMER_NOT_FOUND`.

### PATCH /v1/invoices/{invoice_id}

Edits a draft; requires `If-Match` and `Idempotency-Key`. Send only changed
fields: `currency` (draft only, before any payment) and/or `lines`. Lines
replace wholesale when present; an entry may carry its existing `id` to keep
identity. Status is not editable here.

→ `200`, invoice body, new `ETag`. Not a draft → `409 NOT_DRAFT`. Missing
`If-Match` → `428 PRECONDITION_REQUIRED`. Stale version → `412
VERSION_CONFLICT` with `details.current_version`. Concurrent support agents
cannot lose an update: the second write fails instead of overwriting, and the
agent re-reads, re-applies, retries.

### POST /v1/invoices/{invoice_id}/charge

Requires `Idempotency-Key`. Body: `{ "payment_method_token": "pm_..." }`.
Amount and currency come from the invoice, so a mismatched amount is
impossible.

→ `202`, payment body, `Location: /v1/payments/pay_77`. Returns in
milliseconds; collection runs asynchronously. Unknown or foreign invoice →
`404`. `409 INVOICE_NOT_OPEN` for `draft|paid|void`, with
`details.payment_id` when a payment exists. `422` for a malformed token or zero
total.

### GET /v1/payments/{payment_id}

→ `200`, payment body, `Retry-After: 2` while `pending`. Poll with exponential
backoff; resolution is usually under 35 seconds but not guaranteed. This read
keeps payment state out of the invoice body.

## Charge state machine

`pending` → `succeeded` | `failed` | `unknown`. Settled states are terminal.
`unknown` means the provider timed out or answered ambiguously and the charge
may or may not have been applied; it is never retried automatically — the
client shows "confirming" and support reconciles.

At most one non-`failed` payment exists per invoice. A second charge request,
even with a fresh key, returns the existing payment (`202` if `pending`, `200`
if settled) instead of creating another. Double-charging becomes structurally
impossible. After `failed`, a new charge with a new key is allowed; after
`unknown`, it is not.

## Idempotency and retries

`Idempotency-Key` (UUIDv4 per user action) is required on create, patch, and
charge. Scope is (tenant, endpoint, key).

- Same key, same body → replay the stored status and body with
  `Idempotent-Replayed: true`, so a mobile retry or partner dead-letter replay
  gets the original payment.
- Same key, different body → `422 IDEMPOTENCY_KEY_REUSED`.
- Concurrent duplicate on create/patch → `409 IDEMPOTENCY_IN_PROGRESS` with
  `Retry-After: 1`. Charge never hits this: its response is recorded before
  the provider call starts.

Keys are retained **7 days**, covering the partner's seven-day window and the
mobile app's next-day retry. After expiry a charge replay is still safe: the
invoice is closed or the existing payment is returned.

`GET` is always safe. Retry `429` and `5xx` after `Retry-After` or with
backoff; never retry other `4xx`. Never blind-retry `412` — re-read, re-apply.
A network timeout is not a failure: retry with the same key.

## Errors

```json
{ "error": { "code": "VERSION_CONFLICT", "message": "Invoice was modified.",
             "details": { "current_version": 4 }, "request_id": "req_9c1" } }
```

`code` is stable; `message` may change. Clients branch on `code`.

| Status | Codes |
|---|---|
| 400 | `INVALID_REQUEST`, `INVALID_CURSOR` |
| 401 | `INVALID_API_KEY` |
| 403 | `INSUFFICIENT_SCOPE` |
| 404 | `NOT_FOUND`, `CUSTOMER_NOT_FOUND` |
| 409 | `NOT_DRAFT`, `INVOICE_NOT_OPEN`, `IDEMPOTENCY_IN_PROGRESS` |
| 412 | `VERSION_CONFLICT` |
| 422 | `VALIDATION_FAILED`, `IDEMPOTENCY_KEY_REUSED` |
| 428 | `PRECONDITION_REQUIRED` |
| 429 | `RATE_LIMITED` (with `Retry-After`) |
| 5xx | `INTERNAL_ERROR`, `UNAVAILABLE` |

`422 VALIDATION_FAILED` carries `details.fields: [{field, code, message}]`.
Limits: description 1–500 chars; quantity 1–1,000,000; unit_amount_cents
0–100,000,000; 1–200 lines; uppercase ISO 4217 currency.

## Compatibility

`/v1` is frozen at launch. Only additive change: new optional fields,
endpoints, enum values, error codes. Fields and codes are never removed,
renamed, retyped, repurposed, or reused. Clients ignore
unknown fields and tolerate unknown enum values — treat an unknown
`payment.status` as non-terminal and keep polling. Breaking changes ship as
`/v2`, with `/v1` supported 12 months after a `Deprecation`/`Sunset` header
announcement. `X-Request-Id` is echoed for support correlation, not
idempotency.

## Decisions to record

ADRs: asynchronous charge (reversal breaks every client); amount derived from
the invoice; seven-day key retention sized to the partner window; cursor paging
at 50,000 rows.
