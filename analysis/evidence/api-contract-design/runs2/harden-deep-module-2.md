# Billing API v1

Contract between the billing service and its clients: the web app, the offline-first
mobile app (retries on reconnect and by hand), and the partner batch importer (nightly
runs, retried batches, multi-day dead-letter replay). Third parties implement against
this document without reading the Python service.

## Conventions

- **Base URL:** `https://api.example.com/v1`. JSON, UTF-8. Optional `X-Request-Id` is
  echoed on every response.
- **Auth:** `Authorization: Bearer <api-key>`. The key identifies one tenant.
  `tenant_id` is never accepted from a client. Other-tenant resources return
  `404 not_found`, identical to nonexistent ones.
- **Money:** `*_cents` are integers, never floats or strings. `currency` is ISO 4217
  uppercase.
- **Time:** RFC 3339 UTC, e.g. `2026-03-01T12:00:00Z`, server-generated.
- **IDs:** opaque strings; clients must not parse them.
- **Unknown fields** in request bodies are rejected with `422 validation_failed`.

## Objects

```json
Invoice {
  "id": "inv_01HX", "customer_id": "cus_01HX",
  "status": "draft",                // draft | open | paid | void
  "currency": "USD", "version": 3,
  "lines": [ Line, ... ],           // ordered by position
  "total_cents": 35000,             // sum of line amount_cents, server-computed
  "created_at": "...", "updated_at": "..."
}
Line {
  "id": "line_01HX", "description": "Seats", "quantity": 25,
  "unit_amount_cents": 1200, "amount_cents": 30000, "position": 1
}
Payment {
  "id": "pay_01HX", "invoice_id": "inv_01HX",
  "amount_cents": 35000, "currency": "USD",
  "status": "pending",              // pending | succeeded | failed | unknown
  "failure_code": null,             // card_declined | insufficient_funds | expired_card
                                    // | invalid_token | provider_error | null
  "created_at": "...", "updated_at": "..."
}
```

`total_cents` and line `amount_cents` are derived; sending them is an error. Provider
identifiers and raw payloads are not part of this contract.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/invoices` | List the tenant's invoices, newest first |
| `GET` | `/invoices/{invoice_id}` | Read one invoice with all lines |
| `POST` | `/invoices` | Create a draft |
| `PATCH` | `/invoices/{invoice_id}` | Replace a draft's lines |
| `POST` | `/invoices/{invoice_id}/charge` | Start one collection attempt |
| `GET` | `/payments/{payment_id}` | Read a charge attempt |

### GET /invoices

Query: `status` (one of four), `customer_id`, `created_after` (inclusive),
`created_before` (exclusive), `limit` (1–100, default 25), `cursor` (opaque).

```json
{ "data": [ Invoice, ... ], "next_cursor": "eyJjcmVhdGVkX2F0Ijoi..." }
```

Order is `created_at` descending, `id` descending as tiebreak. `next_cursor` is `null`
on the last page. Cursors are stable: pages do not repeat or skip rows that existed when
the cursor was issued, and later inserts do not shift them. An unparseable cursor is
`400 invalid_cursor`; re-list from the start. No total count is returned; counting tens
of thousands of rows per request is out of contract.

### GET /invoices/{invoice_id}

Returns the invoice, all lines, and `ETag: "3"` (quoted `version`). Unknown or
other-tenant id → `404 not_found`.

### POST /invoices

Requires `Idempotency-Key`. Returns `201` with `Location` and `ETag`.

```json
{ "customer_id": "cus_01HX", "currency": "USD",
  "lines": [ { "description": "Seats", "quantity": 25, "unit_amount_cents": 1200 } ] }
```

`lines` is required, 1–100 entries; `quantity` ≥ 1, `unit_amount_cents` ≥ 0,
`description` 1–500 chars. Currency must match the tenant's configured currency. The
draft is created at `version: 1` with positions 1..n in array order and server-assigned
line ids.

### PATCH /invoices/{invoice_id}

Replaces a draft's line set. Requires `If-Match: "<version>"` (missing → `428 precondition_required`);
send an `Idempotency-Key` too, since a replay returns the original `200`, not a `412`.

```json
{ "lines": [
    { "id": "line_01HX", "description": "Seats", "quantity": 30, "unit_amount_cents": 1200 },
    { "description": "Onboarding", "quantity": 1, "unit_amount_cents": 50000 } ] }
```

Rules: an `id` must already belong to this invoice (`422 line_not_in_invoice`); no `id`
means a new line; an omitted existing line is deleted; ids are unique in the array;
array order becomes `position`. Only `lines` is patchable — `currency` is immutable
after creation and the schema has no invoice description.

Outcomes: `200` with the invoice and new `ETag`; `409 invoice_not_draft`;
`412 precondition_failed` on a stale `ETag` — re-read and re-apply, never blind-retry.
Concurrent editors lose exactly one update.

### POST /invoices/{invoice_id}/charge

Requires `Idempotency-Key`. Body:

```json
{ "payment_method_token": "pm_tok_..." }
```

Amount and currency are **not** request fields; they are derived from the invoice
(partial payments are out of scope). Responses:

- `202 Accepted` with the `Payment` in the body and `Retry-After: 2`. The attempt is
  recorded and reconciled asynchronously; the provider call may take 30 s.
- `409 invoice_not_open` if not `open`.
- `409 invoice_empty` if `total_cents` is 0.
- `409 charge_in_progress` if a payment is `pending` or `unknown`.
- `422 validation_failed` for a missing or malformed token.

`202` means *the attempt exists*, not that money moved. A timeout or dropped connection
is never evidence a charge was not applied. Poll `GET /payments/{payment_id}`; the same
key returns the same payment, so never mint a new key to retry until the attempt is
`failed`.

`succeeded` and `failed` are terminal. `pending` may still change; `unknown` means the
provider outcome is unconfirmed and being reconciled, and may also become `succeeded`
or `failed`. While either is unresolved the invoice stays `open` and rejects new
attempts. To retry after `failed`, send a new `Idempotency-Key`.

### GET /payments/{payment_id}

Returns the payment, tenant-scoped. Non-terminal statuses carry `Retry-After: 2`.
Webhooks are out of scope, so polling is the only notification path.

## Idempotency

`Idempotency-Key` is a client-generated opaque string, 8–255 characters, unique per
logical operation. Keys are scoped to tenant + endpoint and retained **7 days**
(assumption: longer than the importer's dead-letter replay window; the minimum is
contractual). A replay returns the original status, body, and headers plus
`Idempotent-Replay: true`. Same key with a different body → `409 idempotency_key_reuse`.
A duplicate while the first runs → `409 idempotency_in_progress` with `Retry-After`.

## Errors

```json
{ "error": { "type": "conflict", "code": "invoice_not_draft",
  "message": "Invoice inv_01HX is open, not draft.",
  "details": [ { "field": "lines[0].quantity", "issue": "must be >= 1" } ],
  "request_id": "req_01HX" } }
```

`type` is a stable class (`invalid_request`, `authentication`, `not_found`, `conflict`,
`precondition`, `validation`, `rate_limited`, `server_error`). Branch on `code`, not
`message`. `429` carries `Retry-After`; `GET`s are safe to retry, writes only with the
same idempotency key.

## Design notes

**Module.** One deep module: the v1 HTTP surface. Callers are the two apps, the
importer, and third parties; tests cross the seam through HTTP fixtures only. Deleting
it moves retry safety, charge ambiguity, edit races, and tenant scoping into every
client — the complexity reappears, so it earns its keep.

**Alternatives.** (A) A thin RPC mirror of `BillingService`: amount and currency on
charge, offset paging, synchronous charge. It leaks internal invariants and forces each
client to resolve timeout ambiguity. (B) Chosen: resource model, server-derived money,
cursor paging, conditional writes, charge as an asynchronous attempt. It removes error
classes (amount mismatch, skipped pages, lost updates, double charges) rather than
documenting them. (C) Synchronous charge with a 35 s timeout: lost on mobile drops and
`unknown` outcomes.

**Seam.** The provider adapter normalizes status and failures into the enums above;
provider shape changes stay behind it, and no provider field crosses it.

**Assumptions** (repository is silent): invoices are opened by an internal process, not
this API; the tenant currency is fixed and drafts inherit it; keys carry tenant scope
only; `lines` replacement is the edit model, so invoice-level `description` is not
exposed; `version` increments on every successful mutation; lists need an index on
`(tenant_id, created_at DESC, id DESC)` and filtered variants.
