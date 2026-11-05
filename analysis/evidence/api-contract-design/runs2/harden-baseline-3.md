# Billing API v1

Public HTTP contract for the web app, mobile app, and partner batch importer.
Scope: list/read invoices, create and edit drafts, charge an open invoice.
Out of scope: webhooks, subscription plans, refunds, partial payments.

## Conventions

- Base URL: `https://api.example.com/v1` (assumption; no host is fixed in the repo).
- JSON, UTF-8. Timestamps are RFC 3339 UTC (`2026-11-05T14:03:00Z`), server-set.
- Money is an integer number of cents plus an uppercase ISO 4217 currency. Floats are invalid.
- IDs are opaque strings, at most 64 characters. Never parse them.
- Clients **must** ignore unknown response fields. The server rejects unknown request fields with `422`.

## Authentication and tenancy

Every request carries `Authorization: Bearer <api-key>`. A key identifies exactly one tenant; resources of other tenants do not exist for that key. A request for another tenant's invoice returns `404`, never `403`, so IDs cannot be probed. Key issuance and rotation happen out of band (assumption). Missing or invalid key: `401`; a key that lacks the endpoint's permission: `403`.

## Errors

Errors use `application/problem+json` (RFC 9457):

```json
{"type":"https://api.example.com/problems/version-conflict","title":"Version conflict",
 "status":412,"code":"version_conflict","detail":"Invoice changed since version 7.",
 "request_id":"req_...","errors":[{"field":"lines[0].quantity","code":"invalid_range","detail":"Must be >= 1."}]}
```

Stable `code` values: `invalid_request`, `unauthorized`, `forbidden`, `not_found`, `invalid_state`, `version_conflict`, `precondition_required`, `amount_mismatch`, `currency_mismatch`, `idempotency_key_reuse`, `rate_limited`, `internal`. Clients branch on `code`, display `detail`, and log `request_id`. `500` and `503` are retryable.

## Resources

**Invoice**: `id`, `customer_id`, `status` (`draft|open|paid|void`), `currency`, `version` (integer, starts at 1), `created_at`, `updated_at`, `total_cents`, and on detail reads `lines[]`.

**InvoiceLine**: `id`, `description` (1–500 chars), `quantity` (integer >= 1), `unit_amount_cents` (integer >= 0), `position` (0-based, assigned by the server from array order), `amount_cents` (derived: quantity × unit amount).

**Payment**: `id`, `invoice_id`, `amount_cents`, `currency`, `status` (`pending|succeeded|failed|unknown`), `created_at`, `updated_at`. Provider payloads and provider IDs are never exposed; the provider response shape is external and has changed before, so clients must rely only on these fields.

`total_cents` is the sum of line amounts. It is server-computed and read-only.

## Endpoints

### `GET /v1/invoices`

Query: `status`, `customer_id`, `created_from`, `created_to` (half-open `[from, to)`), `limit` (1–200, default 50), `cursor`.

Results are ordered newest first by `(created_at DESC, id DESC)`. Pagination is keyset-based:

```json
{"data":[ /* invoice summaries, no lines */ ], "next_cursor":"eyJj...", "has_more":true}
```

Pass `next_cursor` verbatim as `cursor`; `null` means the end. Cursors are opaque and expire after 24 hours (`422 invalid_request` if unusable). Offset paging is deliberately absent: with tens of thousands of invoices and new rows arriving, offsets skip and duplicate rows. List responses omit `lines`; use the detail endpoint.

### `GET /v1/invoices/{invoice_id}`

`200` with full invoice and `ETag: "v<version>"`. Supports `If-None-Match` → `304`. Unknown or other-tenant ID → `404`.

### `POST /v1/invoices` — create draft

Requires `Idempotency-Key`. Body:

```json
{"customer_id":"cus_123","currency":"EUR","lines":[{"description":"Seats","quantity":3,"unit_amount_cents":1200}]}
```

`lines` may be empty. `201`, `Location: /v1/invoices/{id}`, `ETag: "v1"`, body is the full invoice. Unknown `customer_id` for the tenant → `422 invalid_request`.

### `PATCH /v1/invoices/{invoice_id}` — edit draft

Requires `If-Match`. Body contains only changed fields:

```json
{"currency":"EUR","lines":[{"description":"Seats","quantity":4,"unit_amount_cents":1200}]}
```

`lines`, when present, **replaces the entire line set**; it is not a merge, and client-supplied line IDs are ignored. Position follows array order. Allowed only while `status` is `draft`; otherwise `409 invalid_state`. Missing `If-Match` → `428 precondition_required`. Stale version → `412 version_conflict`, with the current `version` and full invoice in the body so the client can re-apply. Success: `200`, incremented `version`, new `ETag`.

Two support agents editing the same draft therefore cannot silently overwrite each other; the second write fails with `412` and must re-read. `version` increments on every mutation, including charge.

### `POST /v1/invoices/{invoice_id}/charges` — charge open invoice

Requires `Idempotency-Key`. Body:

```json
{"amount_cents":3600,"currency":"EUR","payment_method_token":"pm_tok_..."}
```

`amount_cents` must equal the invoice `total_cents` (`422 amount_mismatch` otherwise) and `currency` must match (`422 currency_mismatch`); partial payments are out of scope. Only `status: open` may be charged, else `409 invalid_state`.

The provider call can take 30 seconds and its outcome can be unknowable on timeout, so the endpoint does not block: it returns `202 Accepted`, `Location: /v1/payments/{payment_id}`, and a `pending` payment. A worker performs the provider call and settles the payment to `succeeded`, `failed`, or `unknown`. Clients must poll; there are no webhooks in v1.

- Replaying the same key returns the existing payment with its current status (`202` while `pending`, `200` once settled) and `Idempotent-Replay: true`.
- A second charge with a *different* key while a payment is `pending`, `succeeded`, or `unknown` returns `409 invalid_state`.
- After `failed`, the invoice stays `open` and a new key may retry.
- After `unknown`, the service reconciles with the provider. **Clients must never re-charge an `unknown` payment**; poll instead.

### `GET /v1/payments/{payment_id}`

Returns the payment. `unknown` may resolve to `succeeded` or `failed` later. Poll with backoff from 1s doubling to a 30s cap; after 24 hours escalate with the `payment_id`. This read endpoint is required to resolve charge outcomes and is the only completion channel in v1.

## Idempotency and retries

`Idempotency-Key` is mandatory on both POSTs: a client-generated UUIDv4, at most 128 characters, unique per logical operation. Keys are scoped to tenant + route and retained 30 days, covering multi-day dead-letter replays.

- Same key and byte-identical body → replay stored response, no new side effect.
- Same key and different body → `422 idempotency_key_reuse`.

The mobile app queues operations with a key generated at enqueue time, not at send time, so a reconnect after a failed send is safe.

Retry rules: `GET` is safe to retry freely. `PATCH` may be retried with the same `If-Match`; a `412` means re-read and re-apply. `POST` may be retried only with the same key. `429` and `503` include `Retry-After`; the batch importer should cap concurrency and honor it.

## Assumptions where the repo is silent

1. Draft-to-`open` issuance is done by the existing internal admin tool; v1 exposes no issue endpoint. If clients need it, add `POST /v1/invoices/{id}/issue` under the same `If-Match` rules.
2. `void`, customer CRUD, and payment-method storage are out of scope; `payment_method_token` is opaque and supplied by the client's provider SDK.
3. Invoice `currency` is mutable only while `draft`.
4. Deletes do not exist; drafts are abandoned, not removed.
5. The invoice-level `version` column is the concurrency token; it is exposed as both `ETag` and `version`.
