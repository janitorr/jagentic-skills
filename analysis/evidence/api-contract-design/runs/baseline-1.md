# Billing API v1

Public HTTP contract for invoice and payment operations. Webhooks and subscription plans are out of scope.

## 1. Scope and assumptions

- Operations: list invoices, read an invoice, create a draft, edit a draft, charge an open invoice, and poll a payment.
- **Assumption:** the `draft → open` transition is out of scope; another internal process issues invoices. `charge` therefore requires status `open`.
- **Assumption:** `db/schema.sql` has no invoice-level description, so PATCH accepts `lines` and `currency` only. `lines[].description` is the only description field.
- Totals are derived: `subtotal_cents = sum(quantity × unit_amount_cents)`; no tax or discounts in v1.

## 2. Conventions

- Base URL `https://api.example.com/v1`; JSON UTF-8; `Accept: application/json`.
- **Auth:** `Authorization: Bearer <api-key>`. The key resolves the tenant server-side. Tenant is never a path, query, or body parameter.
- **Tenancy:** a key that requests another tenant's resource gets `404`, never `403`, so existence is not leaked. `customer_id` in a body is validated against the key's tenant.
- **IDs:** opaque strings (≤64 chars), case-sensitive, never parsed by clients.
- **Money:** integer minor units in `*_cents`; never floats or decimal strings. Currency is ISO 4217 uppercase.
- **Time:** RFC 3339 UTC with `Z`, millisecond precision.
- Unknown request fields are rejected (`400`) to catch typos; unknown response fields must be ignored.
- Every response carries `X-Request-Id` and `Cache-Control: no-store`.

## 3. Errors

`application/problem+json` (RFC 9457):

```json
{"type":"https://api.example.com/errors/invalid-state","title":"Invalid state",
 "status":409,"code":"invalid_state","detail":"Invoice is not open.",
 "request_id":"req_...","errors":[{"field":"lines[0].quantity","code":"out_of_range"}]}
```

| HTTP | `type` suffix | When |
|---|---|---|
| 400 | `invalid_request`, `invalid_cursor`, `validation_failed` | Malformed body/query, bad cursor, field errors |
| 401 | `unauthenticated` | Missing/revoked key |
| 404 | `not_found` | Unknown ID **or** other tenant |
| 409 | `invalid_state`, `idempotency_key_reuse`, `payment_in_progress`, `payment_unknown` | State/conflict |
| 412 | `precondition_failed` | Stale `If-Match` |
| 422 | `amount_mismatch` | Charge amount/currency ≠ invoice |
| 428 | `precondition_required` | Missing `If-Match` on PATCH |
| 429 | `rate_limited` | With `Retry-After` |
| 500/503 | `internal_error`, `unavailable` | Retryable; safe with the same idempotency key |

`type` URIs are permanent. Provider error text is never forwarded; `Payment.failure_code` is normalized.

## 4. Idempotency and retries

- `Idempotency-Key` header is **required** on `POST /invoices` and `POST /invoices/{id}/charge` (8–255 chars). Missing → `400`.
- Scope: tenant + route + key. The request body is hashed; the same key with a different body → `409 idempotency_key_reuse`.
- A replay returns the original status and body with `Idempotent-Replay: true`; no second side effect occurs.
- Outcomes are retained **30 days**, covering the mobile app's next-day retry and the partner's 7-day 5xx/DLQ replays.
- `5xx` and `429` are not recorded as outcomes, so retrying them is always safe.
- GETs are safe and retryable without a key.

## 5. Concurrency

- Each invoice exposes a monotonically increasing `version`, returned as a strong `ETag: "v<version>"`.
- `PATCH` requires `If-Match`. Missing → `428`; mismatch → `412` (lost update is impossible). The `412` carries the current `ETag` so the client can refetch and merge.
- `lines`, when present, **replaces the whole collection**; array order defines `position`. This keeps concurrent edits unambiguous: one writer wins, the other gets `412`.
- Charges are serialized per invoice server-side; at most one non-`failed` payment may exist for an invoice.

## 6. Endpoints

### GET /v1/invoices

Query: `status` (repeatable: `draft|open|paid|void`), `created_from`, `created_to` (half-open `[from, to)`), `customer_id`, `limit` (default 20, max 100), `cursor`.

```json
{"data":[{"id":"inv_...","customer_id":"cus_...","status":"open","currency":"USD",
  "version":3,"total_cents":12500,"created_at":"2026-01-04T10:00:00.000Z"}],
 "next_cursor":"eyJj...","has_more":true}
```

Sort is fixed: `created_at DESC, id DESC`. Pagination is keyset (cursor), not offset, because 50,000 invoices plus concurrent inserts make offsets skip or duplicate rows. A cursor is bound to its filter set; changing filters with an old cursor → `400 invalid_cursor`.

### GET /v1/invoices/{id}

`200` with full `Invoice` (including `lines`) and `ETag`. `404` as above.

### POST /v1/invoices

`201`, `Location`, `ETag`, body `Invoice`. `Idempotency-Key` required.

```json
{"customer_id":"cus_...","currency":"USD",
 "lines":[{"description":"Seat","quantity":3,"unit_amount_cents":2500}]}
```

Validation: 1–500 lines; `quantity` 1..1,000,000; `unit_amount_cents` 0..100,000,000; `description` 1–500 chars; `total_cents` ≤ 1,000,000,000; customer must exist in the tenant.

### PATCH /v1/invoices/{id}

`If-Match` required. Body is partial: `currency` and/or `lines` (full replacement). Returns `200` with the updated `Invoice` and new `ETag`.
Changing `currency` does not convert line amounts; it relabels them and is allowed only while `draft`. Non-draft → `409 invalid_state`.

### POST /v1/invoices/{id}/charge

Asynchronous because the provider may take 30s while clients time out at 10s.

```json
{"amount_cents":12500,"currency":"USD","payment_method_token":"pm_tok_..."}
```

- `202` with a `Payment` (`status: "pending"`) and `Location: /v1/payments/{payment_id}`. The connection is never held for the provider call.
- `amount_cents` must equal the invoice total and `currency` must equal the invoice currency, else `422 amount_mismatch`.
- Invoice must be `open`, else `409 invalid_state`.
- `payment_method_token` is never stored in responses or logs.
- Another non-`failed` payment for the invoice → `409 payment_in_progress` (or `payment_unknown`) with `payment_id`.
- Provider timeout/disconnect ⇒ payment `unknown`. The service **never auto-retries** an `unknown` payment; a new key returns `409 payment_unknown`. Reconciliation is manual.

### GET /v1/payments/{id}

`200` `Payment`; `Retry-After: 1` while `pending`. Poll with backoff until `succeeded`, `failed`, or `unknown`.

## 7. Schemas

**Invoice**: `id`, `customer_id`, `status`, `currency`, `version`, `created_at`, `updated_at`, `lines[]`, `subtotal_cents`, `total_cents`.

**InvoiceLine**: `id`, `description`, `quantity`, `unit_amount_cents`, `position`, `amount_cents`.

**Payment**: `id`, `invoice_id`, `amount_cents`, `currency`, `status` (`pending|succeeded|failed|unknown`), `provider_charge_id` (nullable, opaque, may change shape — clients must treat as a string), `failure_code` (`card_declined|insufficient_funds|provider_error|timeout`), `created_at`, `updated_at`.

## 8. Compatibility

- Version is in the path. Within `v1`, changes are **additive only**: new optional request fields, new response fields, new enum values (e.g. a new payment status). Clients must tolerate unknown enum values and unknown fields.
- No field is removed, renamed, retyped, or made required; no status code or error `type` changes meaning.
- Error `type` URIs and idempotency semantics are permanent.
- Deprecations are announced with `Deprecation` and `Sunset` headers at least 12 months before removal. Breaking changes ship as `/v2`.
- A future webhook is additive; polling remains supported for the life of `v1`.
