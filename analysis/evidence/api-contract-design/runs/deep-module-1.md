# Billing API v1

## Responsibility and seam

This HTTP surface is the module: **one tenant-scoped contract for invoices and
payments that is safe to retry and safe to edit concurrently.** Callers are the
web frontend, the mobile app, partner servers, and support tooling. The deletion
test: remove it and tenant isolation, idempotency, optimistic concurrency, and
provider-response normalization must be reimplemented in four clients — the
surface earns its keep. Provider JSON is an implementation detail behind the
service; the API exposes only normalized payment states.

Alternatives considered: (A) offset pagination with a synchronous charge — loses
stability at 50k invoices and cannot survive a 10 s client timeout against a 30 s
charge. (B) client-supplied natural charge id as the idempotency key — partners
cannot reliably derive stable ids, and it conflates distinct actions. (C) chosen:
cursor lists, asynchronous charge, required `Idempotency-Key`, `If-Match` edits.

## Assumptions and gaps

- `open` is reached by an out-of-scope back-office transition. **Gap:** without
  it, an API-created draft can never be charged; specify it before launch.
- `service.update_draft` mentions "description", but the schema has no
  invoice-level description. Assumption: it means line descriptions. No
  invoice-level description is exposed.
- API keys are issued out of band and map to exactly one tenant.
- Money is integer cents; currency is uppercase ISO 4217 and immutable after
  creation. Times are RFC 3339 UTC with millisecond precision.

## Conventions

- Base path `/v1`. `Authorization: Bearer <api_key>` over TLS. Missing or invalid
  key: `401`. Tenant comes only from the key; there is no tenant field in any
  path or body.
- A resource belonging to another tenant returns `404`, never `403`.
- Errors are `application/problem+json` (RFC 9457) with `type`, `title`,
  `status`, `code`, `detail`, `request_id`, and `errors[]` (`pointer`, `code`,
  `message`) for field failures.
- Unknown **request** fields are rejected (`400 unknown_field`). Clients must
  ignore unknown **response** fields.
- All POSTs require `Idempotency-Key`; omitting it is `400
  idempotency_key_required`.

## Resources

`Invoice`: `id`, `object`, `customer_id`, `status` (`draft|open|paid|void`),
`currency`, `amount_due_cents` (sum of `quantity * unit_amount_cents`),
`version`, `created_at`, `updated_at`, `lines[]`. List items omit `lines` and
carry `line_count` instead.

`Line`: `id`, `description` (1–500 chars), `quantity` (integer ≥ 1),
`unit_amount_cents` (integer ≥ 0), `amount_cents`, `position` (0-based).

`Payment`: `id`, `object`, `invoice_id`, `amount_cents`, `currency`, `status`
(`pending|succeeded|failed|unknown`), `created_at`, `updated_at`. Provider ids
and raw provider payloads are never exposed.

## Operations

### `GET /v1/invoices`

Filters: `customer_id`, `status` (repeatable), `created_from`, `created_to`
(half-open `[from, to)`), `limit` (1–100, default 25), `cursor`.

Order is `created_at DESC, id DESC` — newest first with a stable tie-break.
Response: `{ "data": [...], "next_cursor": "...", "has_more": true }`.
`next_cursor` is opaque base64url, HMAC-signed, and bound to the tenant and the
filter set. Changing filters while reusing a cursor is `400 invalid_cursor`.
Offset and total counts are not offered: at 50k rows they are both unstable and
expensive. Keyset paging stays correct under concurrent inserts. Target p95
300 ms with an index on `(tenant_id, created_at DESC, id)` plus status and
customer indexes.

### `GET /v1/invoices/{invoice_id}`

Returns the full invoice with lines. `ETag: "v{version}"`; `If-None-Match`
yields `304`. `404` if absent or another tenant's.

### `POST /v1/invoices`

Creates a draft. Body: `customer_id`, `currency`, `lines[]` (may be empty).
`201`, `Location`, `ETag`. The customer must belong to the caller's tenant; the
body never carries a tenant.

### `PATCH /v1/invoices/{invoice_id}`

Edits a draft only (`409 invoice_not_draft` otherwise). Requires `If-Match`;
missing is `428 precondition_required`, stale is `412 version_mismatch` with
`current_version` so the agent can refetch and reapply. A lost update is
therefore impossible.

Body fields are optional: `currency` (only while no payment exists) and `lines`.
Supplying `lines` **replaces the entire list**; this avoids per-line patch
ambiguity and gives one atomic unit of change. Returns `200` with the new
`ETag`. Conflicts never merge silently.

### `POST /v1/invoices/{invoice_id}/charge`

Requires `Idempotency-Key`. Body: `amount_cents`, `currency`,
`payment_method_token`. `amount_cents` must equal `amount_due_cents` (`409
amount_mismatch`), and `currency` must match the invoice (`422`). The token is
never logged, stored, or echoed. Only `open` invoices are chargeable.

Returns `202` with a `Payment` and `Location: /v1/payments/{id}`. The request
returns in under 1 s regardless of provider latency; provider timeouts become
`Payment.status = "unknown"`, **not** a 5xx, so partners do not replay a charge
that may have succeeded. Retrying with the same key returns the same payment;
an in-flight duplicate gets the same `202` plus `Retry-After: 1`.

### `GET /v1/payments/{payment_id}`

Poll for the charge outcome. `200` with `Retry-After` while `pending`; poll at
1 s then back off to 10 s. Client guidance: never issue a new
`Idempotency-Key` for the same user action, and never auto-recharge an
`unknown` payment — surface it to support.

## Idempotency and retries

Keys are tenant- and endpoint-scoped, and retained **30 days** (minimum 7 days
after the last replay, covering the partner DLQ window). The key record is
committed before any side effect, so a crash mid-charge still replays the
recorded outcome.

- Same key, same body: replay the stored status and body, add
  `Idempotent-Replay: true`.
- Same key, different body: `409 idempotency_key_reuse`.
- Concurrent duplicate: `409 idempotency_in_progress` with `Retry-After`, except
  charge which returns the existing `202`.

Clients retry only on timeouts, `429`, and `5xx`, with jittered exponential
backoff (1 s, 2 s, 4 s, capped 30 s); retry a `409` only after `Retry-After`.
`4xx` other than `409` is final.

## Status codes and errors

| HTTP | `code` | Meaning |
|---|---|---|
| 400 | `invalid_request`, `unknown_field`, `invalid_cursor`, `invalid_filter`, `idempotency_key_required` | Malformed or unusable request |
| 401 | `unauthenticated` | Missing/invalid key |
| 404 | `not_found` | Absent or other tenant |
| 409 | `invoice_not_draft`, `invoice_not_open`, `amount_mismatch`, `idempotency_key_reuse`, `idempotency_in_progress` | State or key conflict |
| 412 | `version_mismatch` | `If-Match` did not match |
| 422 | `validation_failed` | Field or business-rule violation |
| 428 | `precondition_required` | PATCH without `If-Match` |
| 429 | `rate_limited` | Includes `Retry-After` |
| 500 | `internal` | Safe to retry with the same key |

## Validation

`quantity` and all cent amounts are JSON integers, never floats or strings.
Reject negative amounts, non-positive quantities, totals above 1,000,000,000
cents, more than 500 lines, unknown currencies, and `currency` changes after a
payment exists. Validation failures return every offending field in `errors[]`,
not just the first.

## Compatibility

`/v1` is frozen. Only additive changes ship inside it: new optional request
fields, new response fields, new error codes. Invoice and payment `status` are
closed sets; a new value requires `/v2`. Fields are never removed or retyped,
and clients must not branch on `title` or `detail` text — only `code`. Breaking
changes ship as `/v2` after a 12-month deprecation window announced with
`Deprecation` and `Sunset` headers, with both versions served in parallel.
