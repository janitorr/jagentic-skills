# Billing API v1

Contract for the web app, mobile app, and partner batch importer. Implementable
without reading `src/billing/`.

## 1. What this module is

One responsibility: expose tenant-scoped invoice and payment operations over HTTP
so clients can retry safely, edit concurrently, and page large result sets
without knowing the database or the payment provider.

**Deletion test.** Without this layer every client would re-implement
idempotent retries, cursor paging, draft version checks, provider-response
normalization, and unknown-charge reconciliation. That complexity would reappear
three times, so the layer earns its keep. It is intentionally *not* a
pass-through of `BillingService`: the public interface drops `offset`, drops the
charge amount, adds idempotency and version preconditions, and never exposes
`tenant_id` or `provider_charge_id`.

**Alternatives rejected.** (a) Mirror the Python methods one-to-one — offset
paging double-counts under concurrent writes, and a 30-second charge with no
attempt record cannot be retried safely. (b) A generic job API
(`POST /operations`) — pushes resource semantics, filtering, and polling
conventions into every client and hides nothing useful. The chosen resource API
puts the three hard guarantees (idempotency, optimistic concurrency, payment as
attempt-of-record) at the seam where clients already work.

**Seam.** JSON over HTTPS under `/v1`; the adapters are the three clients.

## 2. Conventions

- `Authorization: Bearer <api_key>`. The key resolves the tenant; `tenant_id` is
  never accepted or returned. Missing/invalid key: `401`.
- Cross-tenant or unknown id: `404` (never `403`), so existence does not leak.
- JSON, `snake_case`, RFC 3339 UTC timestamps (`2026-11-05T10:00:00Z`). Integer
  cents; ISO 4217 uppercase currency. Ids are opaque strings — never parse them.
- Unknown **request** fields are rejected (`422 unknown_field`); unknown
  **response** fields must be ignored. Additive changes are non-breaking; breaking
  changes require `/v2`.

## 3. Representations

**invoice**

| field | type | notes |
|---|---|---|
| `id` | string | opaque |
| `customer_id` | string | supplied on create |
| `status` | enum | `draft`, `open`, `paid`, `void` |
| `currency` | string | ISO 4217 |
| `version` | integer | starts at 1, +1 per accepted write; drives `ETag` |
| `created_at`, `updated_at` | timestamp | |
| `lines` | array | only on single-invoice reads and writes |
| `total_cents` | integer | server-computed `sum(quantity * unit_amount_cents)` |

**line**: `id`, `description` (1–500 chars), `quantity` (1–1,000,000),
`unit_amount_cents` (0–100,000,000), `position` (0-based, assigned as sent).
Lines are read-only objects; they are replaced, never patched individually.

**payment**: `id`, `invoice_id`, `amount_cents`, `currency`,
`status` (`pending`, `succeeded`, `failed`, `unknown`), `failure_reason`
(absent unless failed; open enum ending in `other` — tolerate new values),
`created_at`, `updated_at`. Provider identifiers and provider JSON are never
exposed; the service normalizes them.

## 4. Endpoints

### GET /v1/invoices

Newest first, fixed order `created_at desc, id desc`. Query: `status`,
`customer_id`, `created_from`, `created_to` (inclusive, RFC 3339), `limit`
(1–200, default 50), `cursor` (opaque).

```json
{"data": [{"id":"inv_1","customer_id":"cus_1","status":"open","currency":"EUR",
  "version":3,"created_at":"...","updated_at":"...","total_cents":4200}],
 "has_more": true, "next_cursor": "eyJjIjoiLi4uIn0"}
```

`next_cursor` is `null` when `has_more` is `false`. Offset paging is not offered.
Invalid or expired cursor: `400 invalid_cursor`. Page sizes are stable under
inserts; a client paging to the end may still see items created mid-scan, and
must de-duplicate by `id`.

### GET /v1/invoices/{invoice_id}

Returns the full invoice including `lines`. Response carries
`ETag: "<version>"`.

### POST /v1/invoices

Creates a draft. Body: `customer_id`, `currency`,
`lines` (1–200 items, same line fields minus `id`/`position`). At least one line
is required; an invoice with no lines is unrepresentable.

`201` + `Location: /v1/invoices/{id}` + `ETag`, body is the full invoice.
Errors: `404` unknown customer, `422` validation, `409` `idempotency_key_reuse`.

### PATCH /v1/invoices/{invoice_id}

Edits a draft. Requires `If-Match: "<version>"`; absent → `428
version_required`, stale → `412 version_conflict` with
`details.current` holding the current invoice so the editor can merge. Only
`draft` invoices are editable; otherwise `409 invalid_state`.

Body may contain `currency` and/or `lines`. `lines`, when present, is the
**complete replacement** list in display order (no line-id choreography, no
partial line ops); omitted fields are unchanged. Empty body → `422
empty_patch`. `200` with the new invoice and `ETag` on success.

Retries matter here: a retried PATCH would otherwise see its own write and fail
`412`, so PATCH also requires `Idempotency-Key`; a replay returns the original
`200`.

### POST /v1/invoices/{invoice_id}/charge

Creates one payment attempt for the invoice's full outstanding total. Body:
`payment_method_token` only — `amount_cents` and `currency` are derived, because
partial payments are out of scope and a client-chosen amount is a misuse surface.
Requires `Idempotency-Key`.

| outcome | status | body |
|---|---|---|
| provider confirmed | `200` | payment, `status: succeeded`; invoice becomes `paid` |
| provider declined | `200` | payment, `status: failed` + `failure_reason` |
| not yet known | `202` | payment, `status: pending` or `unknown`, `Retry-After: 5` |

`202` is a recorded attempt, not an error: the client must poll, not re-charge.
`409 payment_in_flight` (with `details.payment_id`) if a `pending`/`unknown`
payment already exists for the invoice. `409 invalid_state` if the invoice is not
`open`. Provider timeouts are mapped to `unknown`; the API never returns `5xx`
for a charge whose attempt was recorded.

### GET /v1/payments/{payment_id}

Returns the payment. Poll after `202` at 2s, 5s, 10s, then every 30s, for up to
24h. `unknown` may become `succeeded` or `failed`; it never reverts. Only after a
terminal `failed` may the client start a new charge with a **new**
`Idempotency-Key`.

## 5. Idempotency

`Idempotency-Key` is required on all `POST`/`PATCH` (8–255 printable chars).
Scope: tenant + method + path.

- Same key, same body, original response recorded → replay that status and body
  with `Idempotent-Replay: true`.
- Same key, different body → `409 idempotency_key_reuse`.
- Same key, first request still running → `409 request_in_progress`,
  `Retry-After: 1`.
- Retain keys and responses for **7 days**, covering mobile offline retries and
  the importer's multi-day dead-letter replays. `2xx` and semantic `4xx`
  responses are stored; `5xx` responses are not, so a retry is always safe.

## 6. Errors

```json
{"error": {"code": "version_conflict", "message": "Invoice was modified.",
  "request_id": "req_...", "details": {"current": {}}}}
```

`400 invalid_request | invalid_cursor`, `401 unauthorized`, `404 not_found`,
`409 invalid_state | payment_in_flight | idempotency_key_reuse |
request_in_progress`, `412 version_conflict`, `422 validation_failed |
unknown_field | empty_patch`, `428 version_required`, `429 rate_limited`
(+`Retry-After`), `500 internal_error`, `503 unavailable`. Clients branch on
`code`, never on `message`. Echo `request_id` in support requests.

## 7. Assumptions (repository is silent)

1. **A1** API keys are Bearer tokens; provisioning/rotation is out of scope.
2. **A2** There is **no invoice-level description**. `update_draft`'s docstring
   mentions one, but `invoices` has no such column; only lines have
   `description`. The contract omits it rather than promising an unpersisted
   field.
3. **A3** Draft → open transition is out of scope (the admin tool does it
   today). Until `POST /v1/invoices/{id}/open` exists, clients can list, read,
   create, and edit drafts but cannot charge one they just created.
4. **A4** Charge is full-total only; partial payments, refunds, voiding, plans,
   webhooks, and payment listing are out of scope.
5. **A5** Customers are not exposed in v1; `customer_id` comes from an
   out-of-band source and is validated on create.
6. **A6** `currency` is editable only while `draft`; no re-denomination of
   existing payments occurs.
7. **A7** `total_cents` is informational and excludes tax/discount; there is no
   tax model.
8. **A8** Idempotency retention is 7 days and cursors may expire earlier; both
   are configurable but guaranteed no shorter than stated.
9. **A9** A charge confirmed `succeeded` pays the invoice in full; there is no
   overpayment path.
