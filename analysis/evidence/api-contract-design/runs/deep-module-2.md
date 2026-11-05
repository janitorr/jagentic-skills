# Billing API v1

## Scope and assumptions

Operations: list invoices, read one, create a draft, edit a draft, charge an open invoice, poll the payment. Webhooks, plans, refunds, and partial captures are out.

Assumptions:

- Issuance (`draft` → `open`) happens outside v1; v1 charges open invoices. Add issuance later if partners need it.
- One currency per invoice; integer cents; no tax or discount. TLS only; one primary database, so reads are read-your-writes.
- A charge is one full-amount attempt; no partial capture or retry of a failed attempt.
- Keys are per tenant with scopes `invoices:read`, `invoices:write`, `payments:charge`.

## Shape

One seam between three clients (web, mobile, partner) and billing. Responsibility: tenant-scoped invoice and payment lifecycle with exactly-once mutations, conflict-safe edits, and provider-independent outcomes. Delete it and those concerns reappear in every client, so it earns its keep. Rejected: RPC verbs (state machine in URLs, not additively evolvable) and an all-async API (reads pay polling costs). Chosen: resources with an async payment sub-resource.

## Conventions

**Auth and tenancy.** `Authorization: Bearer <key>`. The tenant comes only from the key; never accept `tenant_id`; filter every lookup by tenant. Another tenant's id returns `404`, not `403`, so existence does not leak. A missing scope returns `403 insufficient_scope`.

**Ids.** Opaque. Prefixes (`inv_`, `pay_`, `cus_`, `lin_`) aid debugging only; clients must not parse or construct them.

**Money.** Integer `*_cents`; `currency` is uppercase ISO 4217. Line `amount_cents` = `quantity * unit_amount_cents`; `total_cents` is the sum. Never floats.

**Time.** RFC 3339 UTC with `Z`, millisecond precision, server-generated. Clients never send timestamps.

**Errors.** Every non-2xx body:

```json
{"error":{"type":"conflict","code":"payment_unresolved","message":"...","param":null,"request_id":"req_..."}}
```

`code` is the stable machine-readable contract; `message` is not. Clients must tolerate new codes. `type` is one per status: `invalid_request`, `unauthenticated`, `forbidden`, `not_found`, `conflict`, `precondition_failed`, `precondition_required`, `rate_limited`, `internal`, `unavailable`.

**Compatibility.** `/v1` is frozen. Evolution is additive: new optional fields and enum values may appear; clients must ignore unknown fields and enums. Fields are never removed, renamed, retyped, or made required; new required request fields or changed semantics need `/v2`. Deprecation uses `Deprecation`/`Sunset` headers with 12 months' notice.

## Resources

Invoice:

```json
{"id":"inv_01H","customer_id":"cus_01H","status":"draft","currency":"USD","version":7,"created_at":"2026-11-05T09:00:00.000Z","updated_at":"2026-11-05T09:04:12.000Z","lines":[{"id":"lin_1","description":"Seats","quantity":2,"unit_amount_cents":1500,"amount_cents":3000,"position":0}],"total_cents":3000}
```

`status` is `draft`, `open`, `paid`, or `void`. `draft` is editable; `open` is chargeable; `paid`/`void` are terminal. `version` rises on every accepted change and is the concurrency token and strong `ETag` (`"7"`).

Payment:

```json
{"id":"pay_01H","invoice_id":"inv_01H","amount_cents":3000,"currency":"USD","status":"pending","failure_code":null,"created_at":"2026-11-05T09:05:00.000Z","updated_at":"2026-11-05T09:05:00.000Z"}
```

`status` is `pending`, `succeeded`, `failed`, or `unknown`. `failure_code` is a stable enum (`card_declined`, `insufficient_funds`, `expired_card`, `provider_error`, `unknown`), `null` unless `failed`. Provider payloads are never exposed; an anti-corruption layer maps them into this shape.

## Operations

### GET /v1/invoices

Query: `limit` (1–100, default 25), `cursor`, `status` (repeatable), `customer_id`, `created_from`, `created_to` (RFC 3339, half-open `[from, to)`), with `created_from <= created_to`.

```json
{"data":[Invoice],"next_cursor":"eyJ...","has_more":true}
```

Sort is fixed `created_at desc, id desc`. Keyset pagination only; offset degrades at 50,000 rows and skips rows under concurrent inserts. `next_cursor` is `null` when `has_more` is false. Cursors are opaque, bound to tenant and a filter fingerprint; changed filters → `400 cursor_filter_mismatch`, malformed or foreign cursor → `400 invalid_cursor`. No total count; it needs a full scan.

### GET /v1/invoices/{invoice_id}

`200` Invoice with `ETag`; `If-None-Match` → `304`. Unknown or foreign id → `404`.

### POST /v1/invoices

Creates a draft. Requires `Idempotency-Key`.

```json
{"customer_id":"cus_01H","currency":"USD","lines":[{"description":"Seats","quantity":2,"unit_amount_cents":1500}]}
```

Server assigns line ids and `position` from array order, sets `status: "draft"`, `version: 1`, timestamps, and `total_cents`. `201` with `Location` and `ETag`. Unknown or foreign customer → `404`; unknown request field → `400 unknown_field`.

### PATCH /v1/invoices/{invoice_id}

Edits a draft. Requires `If-Match: "7"` and `Idempotency-Key`. Body may contain `currency` and/or `lines` (full replacement array); omitted fields are unchanged. Only `draft` is editable; otherwise `409 invalid_state`. Missing `If-Match` → `428`; stale version → `412` with the current Invoice so the agent can rebase. Success returns `200`, the Invoice, and the new `ETag`.

### POST /v1/invoices/{invoice_id}/payments

Charges an open invoice. Requires `Idempotency-Key`.

```json
{"payment_method_token":"pm_tok_..."}
```

Amount and currency come from the immutable open invoice; no amount field is accepted. The provider takes up to 30 seconds, so the call is asynchronous: `202` with a `pending` Payment, `Location: /v1/payments/{id}`, `Retry-After: 2`. It returns in under a second. `409 invalid_state` if not open or the total is below 1 cent; `409 payment_unresolved` if any payment is `pending`/`unknown`, preventing a second charge while the first outcome is unknown.

### GET /v1/payments/{payment_id}

Returns the Payment. Poll every 2–5 seconds with backoff, honouring `Retry-After`. `succeeded`/`failed` are terminal. `unknown` means the provider outcome is unresolved; it is not a failure and may resolve later, so clients must not charge again with a new key. `404` if unknown or foreign.

### GET /v1/payments?invoice_id={id}

Same pagination and shape as the invoice list, for support tooling. `invoice_id` required; also `status`, `limit`, `cursor`.

## Retries and idempotency

- `Idempotency-Key` is required on every `POST`/`PATCH`: a client-generated unique string, 8–255 characters, scoped to `(tenant, method, path)`.
- Same key and body replays the original status/body with `Idempotent-Replayed: true`. Same key, different body → `409 idempotency_key_reuse`. A concurrent duplicate → `409 request_in_progress` with `Retry-After: 1`.
- Records are persisted and written in the same transaction as the effect, surviving restarts and deploys. Retention is 30 days, covering the partner's seven days of retries and dead-letter replays plus the mobile user's next-day retry.
- A `5xx` never means "not applied". Any `5xx`, `429`, or timeout is retried with the same key and body, so mobile's three attempts and the partner's seven days are safe for every operation, including charge.
- Charge retries must reuse the original key. A new key while a payment is `pending`/`unknown` → `409 payment_unresolved`.

## Concurrency

The invoice is the only conflict unit. `PATCH` requires `If-Match`; version check and write are atomic. A stale writer gets `412` plus the winning invoice, so lost updates are impossible. `POST` creates its own version. Charge needs no `If-Match`: open invoices are immutable and the unresolved-payment guard serializes attempts.

## Validation

- `description` 1–500 characters; `quantity` 1–100,000; `unit_amount_cents` 0–100,000,000; 1–500 lines; `total_cents` ≤ 1,000,000,000,000.
- `currency` is three uppercase letters, a supported ISO 4217 code. `payment_method_token` is 1–255 characters and is never logged or echoed.
- Ids are 1–64 characters, `[A-Za-z0-9_-]`.
- Unknown request fields → `400 unknown_field`; unknown response fields must be ignored.
- Failures are `400 invalid_request` with `param` naming the path, never `5xx`.

## Status codes

| Code | Meaning |
|---|---|
| 200 | Read, patch, or poll succeeded |
| 201 | Draft created |
| 202 | Charge accepted; poll the payment |
| 304 | Conditional GET unchanged |
| 400 | Malformed request, bad cursor, or validation failure |
| 401 | Missing, malformed, or revoked key |
| 403 | Key lacks the required scope |
| 404 | Unknown id, or another tenant's id |
| 409 | Invalid state, unresolved payment, or idempotency conflict |
| 412 | `If-Match` version stale |
| 428 | `If-Match` missing |
| 429 | Rate limited; honour `Retry-After` |
| 500, 503 | Retryable with the same key |

## Required persistence

A tenant-scoped idempotency table with unique `(tenant_id, key)`; indexes on `(tenant_id, created_at desc, id desc)` and `(tenant_id, status, created_at desc)`; a unique partial index allowing one `pending`/`unknown` payment per invoice; a durable job and reconciliation for `unknown` payments; and an opaque cursor encoding `(created_at, id, filter_hash, tenant)`.
