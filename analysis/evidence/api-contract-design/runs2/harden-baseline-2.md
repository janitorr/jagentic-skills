# Billing API v1

Contract for the web app, mobile app, and partner batch importer. JSON over HTTPS. Base URL `https://api.example.com/v1` (assumed; operator supplies the real host).

## Scope

In scope: list invoices, read an invoice, create a draft, edit a draft, charge an open invoice, read a payment. Out of scope: webhooks, subscription plans, refunds, partial payments, customer CRUD, and the draft-to-open transition (assumed to be performed by an internal process; clients cannot issue invoices in v1).

## Conventions

- **Auth:** `Authorization: Bearer <api-key>`. The key identifies the tenant; never accept a tenant ID from the client.
- **Tenancy:** a resource outside the caller's tenant returns `404`, never `403`, to avoid enumeration.
- **IDs:** opaque strings. Do not parse or construct them.
- **Money:** integer cents, never floats or strings. `currency` is ISO 4217, uppercase.
- **Time:** RFC 3339 UTC with `Z`, e.g. `2026-11-05T10:15:30Z`.
- **Unknown enum values:** clients must tolerate new `status`, `failure_code`, and error `code` values; treat an unknown payment status as non-terminal.
- **Unknown request fields:** rejected with `400 invalid_request`. `Content-Type: application/json` is required, otherwise `415`.
- **Request tracing:** clients may send `X-Request-Id`; the server echoes it and includes it in every error.

## Errors

```json
{"error":{"type":"conflict","code":"invoice_not_open",
  "message":"Only open invoices can be charged.",
  "request_id":"req_8f2","details":{"status":"draft"}}}
```

| HTTP | `type` | Used for |
|---|---|---|
| 400 | `invalid_request` | Malformed JSON, unknown field, bad cursor, bad filter |
| 401 | `unauthenticated` | Missing or invalid key |
| 403 | `forbidden` | Key lacks the required scope |
| 404 | `not_found` | Unknown or other-tenant resource |
| 409 | `conflict` | Wrong invoice state, amount mismatch, charge in progress, idempotency key reused with a different body |
| 412 | `precondition_failed` | Stale `If-Match` on draft edit |
| 422 | `unprocessable` | Semantically invalid lines or money |
| 428 | `precondition_required` | `PATCH` without `If-Match` |
| 429 | `rate_limited` | Includes `Retry-After` seconds |
| 500/503 | `server_error` / `unavailable` | Safe to retry per the rules below |

Never expose provider payloads, provider error text, or `payment_method_token` in responses or logs.

## Idempotency

`Idempotency-Key` is **required** on `POST /invoices` and `POST /invoices/{id}/charge`, and optional but recommended on `PATCH`. Rules:

- Key is scoped to tenant + method + path; 1–255 characters; a UUID is recommended.
- Same key + same body: replay the original response, including status code, with `Idempotent-Replay: true`.
- Same key + different body: `409 idempotency_key_reuse`.
- Same key while the first request is still executing: `409 idempotency_key_in_progress` with `Retry-After: 1`; retry with the same key.
- Keys and responses are retained for **30 days** (assumption), covering nightly batch replays from the dead-letter queue.

Retries are only safe with the *same* key. A new key is a new operation.

## Resources

**Invoice (summary):** `id`, `customer_id`, `status` (`draft|open|paid|void`), `currency`, `total_cents`, `version`, `created_at`, `updated_at`.

**Invoice (detail):** summary plus `lines[]`: `id`, `description`, `quantity`, `unit_amount_cents`, `position` (0-based, server-assigned), and line `total_cents`.

`total_cents = sum(quantity * unit_amount_cents)`; no tax or discounts. The server computes it and ignores any client-supplied total.

**Payment:** `id`, `invoice_id`, `amount_cents`, `currency`, `status` (`pending|succeeded|failed|unknown`), `failure_code` (nullable; `card_declined|insufficient_funds|expired_card|provider_unavailable`), `created_at`, `updated_at`. The provider's charge ID is internal and is not exposed.

## Endpoints

### GET /v1/invoices

Filters: `status`, `customer_id`, `created_from` (inclusive), `created_to` (exclusive), `limit` (default 20, max 100), `cursor`.

Ordering is newest first: `created_at DESC, id DESC`. Pagination is cursor-based; `offset` is not supported because the dataset is large and changes concurrently. Response:

```json
{"data":[Invoice...],"next_cursor":"eyJjIjoi..."}
```

`next_cursor` is `null` on the last page. Cursors are opaque, expire after 24 hours (`400 cursor_expired`), and do not guarantee a frozen snapshot: newly created invoices may appear on later pages. Clients deduplicate by `id`.

### GET /v1/invoices/{id}

Returns the invoice detail and `ETag: "<version>"`. Honors `If-None-Match` with `304`. Missing or other-tenant IDs return `404`.

### POST /v1/invoices

Requires `Idempotency-Key`. Body: `customer_id`, `currency`, `lines[]` with `description`, `quantity` (integer 1–1,000,000), `unit_amount_cents` (integer ≥ 0). At most 500 lines. Lines are ordered as sent. Returns `201`, `Location`, and the detail plus `ETag`.

### PATCH /v1/invoices/{id}

Edits a draft. Requires `If-Match: "<version>"`; missing returns `428`, stale returns `412`. Body may contain `currency` and/or `lines` (full replacement, same rules as create). Omitted fields are unchanged. A currency change is allowed only while the invoice is `draft`. On `412`, re-read the invoice, merge changes, and retry; never blindly retry. Returns `200` with the new detail and `ETag`. Editing a non-draft returns `409 invoice_not_draft`.

Both support agents editing the same draft get one success and one `412`, so edits are never silently lost.

### POST /v1/invoices/{id}/charge

Requires `Idempotency-Key`. Body: `amount_cents`, `currency`, `payment_method_token`. The invoice must be `open`, otherwise `409 invoice_not_open`. `amount_cents` must equal the invoice `total_cents` and `currency` must match the invoice; otherwise `409 amount_mismatch` with `details.total_cents` and `details.currency`. Partial payments are unsupported.

The provider call may take 30 seconds, so the endpoint is asynchronous: it returns `202` with `Location: /v1/payments/{payment_id}` and a **Payment** whose initial status is `pending`. The invoice becomes `paid` only after a `succeeded` payment. A failed payment leaves the invoice `open`. While a payment is `pending` or `unknown`, further charge attempts for that invoice return `409 charge_in_progress`; the same idempotency key returns the original payment.

### GET /v1/payments/{id}

Returns the payment. Poll with exponential backoff (start at 1s, cap at 30s, honor `Retry-After`). `succeeded` and `failed` are terminal. `unknown` means the provider outcome is undetermined; the server reconciles automatically. Do not start a new charge while `unknown` — poll, and after 24 hours stop and escalate to support with the payment ID and request ID.

## Retry playbook

- **Mobile (offline-first, manual retries):** retry the same request with the same `Idempotency-Key` after connectivity returns, within the 30-day window. A replay is safe even if the original succeeded.
- **Partner batch:** derive one stable key per source row (for example a hash of batch ID plus row ID) and reuse it across reruns and dead-letter replays. A replayed row returns the original invoice or payment rather than creating a duplicate.
- **Charge timeout:** never generate a new key; retry with the same key or poll the payment ID. Because the outcome is ambiguous, a new key could double-charge.
- **429/503:** back off per `Retry-After`.

## Assumptions

The host, API-key format, and tenant default currency are operator-supplied. Invoice-level `description` does not exist in the schema, so `PATCH` accepts only `currency` and `lines`. `draft → open` and `open → void` are internal operations. v1 changes are additive only; removing a field, changing a type, or changing existing semantics requires `/v2`. Scopes (`invoices:read`, `invoices:write`, `payments:write`) are assumed.
