# Billing API v1

HTTP/JSON contract for invoices and payments. Base URL: `https://api.example.com/v1`.
Webhooks and subscription plans are out of scope.

## Assumptions

1. A draft is moved to `open` by a finalize step that is **not part of this
   contract**. `charge` therefore requires `status = open`.
2. One invoice has no invoice-level description column; "description" in a patch
   refers to line descriptions. Assumption recorded, not invented as a field.
3. Amounts are integer cents; currency is ISO 4217. Line amount is
   `quantity * unit_amount_cents`; invoice `total_cents` is the sum of lines.
   Negative amounts are out of scope. IDs are opaque and must not be parsed.
4. Timestamps are RFC 3339 UTC with `Z`.

## Authentication and tenancy

Every request sends `Authorization: Bearer <api-key>`. The key resolves to
exactly one tenant. All reads and writes are scoped to that tenant. A resource
belonging to another tenant is indistinguishable from a missing one: **404**.
`tenant_id` is never accepted from a client and never returned.

Missing/invalid key: **401** `unauthenticated`. Key valid but lacking the
operation's scope: **403** `forbidden`.

## Conventions

- Requests and responses are `application/json`; errors are
  `application/problem+json` (RFC 9457) with a stable `code` plus `detail`.
- Clients **must ignore unknown response fields** and **must tolerate unknown
  enum values** (for example a future `status`). Servers reject unknown request
  fields with **400** `unknown_field`.
- Every response carries `X-Request-Id`; support refers to it.
- Compatibility: `/v1` accepts only additive changes (new optional fields, new
  enum values, new endpoints). See *Compatibility*.

## Resources

### Invoice

```json
{
  "id": "inv_01H...",
  "customer_id": "cus_01H...",
  "status": "draft",
  "currency": "USD",
  "version": 3,
  "total_cents": 12500,
  "created_at": "2026-01-31T10:00:00Z",
  "updated_at": "2026-01-31T10:04:12Z",
  "lines": [
    {"id": "il_01H...", "description": "Seats", "quantity": 5,
     "unit_amount_cents": 2500, "amount_cents": 12500, "position": 1}
  ]
}
```

`status` ∈ `draft | open | paid | void`. When `status` is `draft` the invoice
is mutable; otherwise it is immutable.

### Payment

```json
{
  "id": "pay_01H...",
  "invoice_id": "inv_01H...",
  "amount_cents": 12500,
  "currency": "USD",
  "status": "pending",
  "failure_code": null,
  "created_at": "2026-01-31T10:05:00Z",
  "updated_at": "2026-01-31T10:05:00Z"
}
```

`status` ∈ `pending | succeeded | failed | unknown`. `failure_code` ∈
`card_declined | expired_card | insufficient_funds | processing_error` or null.
The external provider's payload and identifiers are never exposed.

## Operations

### `GET /invoices`

Query: `limit` (1–100, default 25), `cursor`, `status` (repeatable), `customer_id`,
`created_after`, `created_before` (RFC 3339, inclusive bounds).

Order is fixed: `created_at` descending, then `id` descending. Keyset pagination;
`cursor` is opaque. Response:

```json
{"data": [ ...invoices... ], "has_more": true, "next_cursor": "eyJ..."}
```

`next_cursor` is null on the last page. Invalid cursor/filter: **400**
`invalid_query`. A cursor is bound to the filters that produced it; reuse with
different filters is **400** `cursor_filter_mismatch`.

### `GET /invoices/{invoice_id}`

**200** with `ETag: "<version>"`. Unknown or foreign id: **404** `invoice_not_found`.

### `POST /invoices`

Creates a draft. Optional `Idempotency-Key`.

```json
{"customer_id": "cus_01H...", "currency": "USD",
 "lines": [{"description": "Seats", "quantity": 5, "unit_amount_cents": 2500}]}
```

A line may carry a client-generated `id` (recommended: UUID) so retries address
the same line; otherwise the server assigns one. `quantity` ≥ 1;
`unit_amount_cents` ≥ 0; max 500 lines; description 1–500 chars.

**201** with `Location: /v1/invoices/{id}` and the invoice. Unknown customer in
this tenant: **422** `customer_not_found`. No lines: **422** `empty_invoice`.

### `PATCH /invoices/{invoice_id}`

Requires `If-Match: "<version>"`; missing header is **428**
`precondition_required`. Body fields are optional: `currency`, and `lines` as a
whole-list replacement (existing `id` updated, no `id` created, omitted lines
deleted). `currency` may change only while `draft` and only with no payments.

- **200** with the new invoice and new `ETag`.
- **412** `version_conflict` when the version moved; the body's `current` field
  carries the latest invoice so the client can re-apply without a round trip.
- **409** `invoice_not_draft` if status is not `draft`.
- **422** `invoice_has_payments` for a currency change after a payment attempt.

Concurrent edits are serialized by the version check; a lost update is
impossible.

### `POST /invoices/{invoice_id}/charges`

`Idempotency-Key` is **required** (8–255 chars, client-generated; reuse the same
key for every retry of the same user action). Body:

```json
{"payment_method_token": "pm_01H...", "amount_cents": 12500, "currency": "USD"}
```

`amount_cents` and `currency` are optional; when omitted the invoice total and
currency are used. When supplied they must match, else **422** `amount_mismatch`.
The server computes the authoritative amount and never trusts the client's.

Because a provider call can take 30 seconds, this endpoint is asynchronous:

- **202** with `Location: /v1/payments/{payment_id}`, `Retry-After: 2`, and the
  payment in `pending`. The charge is then executed exactly once for that key.

Preconditions: invoice `open` (**409** `invoice_not_open` otherwise); a payment
in `pending` or `unknown` already exists for it (**409** `payment_in_progress` /
`payment_state_unknown`) — never start a second charge while one is unresolved.

### `GET /payments/{payment_id}`

Polls a charge. **200** with the payment; `Retry-After: 2` while `pending`.
`succeeded` and `failed` are terminal; `unknown` means the provider outcome
could not be determined and is reconciled server-side. Poll with backoff (2 s to
30 s), not in a tight loop.

## Idempotency

`Idempotency-Key` is required on `POST /charges` and honoured on `POST /invoices`
and `PATCH /invoices/{id}`.

- Stored per tenant for **7 days**, which covers the mobile retry-after-a-day and
  the partner's 7-day dead-letter replays.
- Same key + same request fingerprint: replay of the original status, body and
  `Location`, with `Idempotent-Replay: true`.
- Same key + different body: **422** `idempotency_key_reuse`.
- Same key while the first attempt is still running: **409**
  `idempotency_key_in_flight` with `Retry-After`.
- After 7 days a key may be forgotten; a client retrying an old charge must
  first read the invoice (it is `paid` if the earlier attempt succeeded).

## Errors

| Status | `code` examples | Meaning |
|---|---|---|
| 400 | `invalid_query`, `malformed_json`, `unknown_field` | Bad request |
| 401 | `unauthenticated` | Missing/invalid key |
| 403 | `forbidden` | Key lacks scope |
| 404 | `invoice_not_found`, `payment_not_found` | Missing or other tenant |
| 409 | `invoice_not_open`, `invoice_not_draft`, `payment_in_progress`, `payment_state_unknown`, `idempotency_key_in_flight` | State conflict |
| 412 | `version_conflict` | Stale `If-Match` |
| 422 | `validation_failed`, `amount_mismatch`, `customer_not_found`, `idempotency_key_reuse` | Semantically invalid |
| 428 | `precondition_required` | `If-Match` missing |
| 429 | `rate_limited` | Includes `Retry-After` |
| 500/503 | `internal_error`, `unavailable` | Safe to retry with same idempotency key |

Body: `{"type": "...", "title": "...", "status": 412, "code": "version_conflict",
"detail": "...", "request_id": "...", "errors": [{"field": "lines[0].quantity",
"code": "must_be_positive"}]}`. `errors` appears only for validation failures.

## Retry matrix

| Situation | Retry? |
|---|---|
| Network timeout on any GET | Yes, immediately |
| Timeout on `POST /charges` | Yes, same `Idempotency-Key`; then poll the payment |
| Timeout on create/patch | Yes, same key (or re-read with ETag for patch) |
| 429 / 503 | Yes, honour `Retry-After`, exponential backoff with jitter |
| 4xx other than 429 | No |

## Compatibility

- `/v1` will not change existing field names, types, status codes, or error
  codes; changes are additive only. New endpoints and optional request fields
  may appear.
- New enum values may appear; clients must fall back gracefully rather than
  crash (treat an unknown status as non-terminal and re-read).
- Deprecations are announced with `Deprecation` and `Sunset` headers at least 12
  months ahead; a `/v2` ships alongside `/v1`, never in place of it.
- The provider's response shape is internal: provider changes can only surface
  as a mapped `failed` or `unknown` payment, never as a schema change here.
