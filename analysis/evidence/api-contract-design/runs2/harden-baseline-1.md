# Billing API v1

Public HTTP contract for the web app, mobile app, and partner batch importer. Clients should be able to implement against this document alone. HTTPS, JSON UTF-8, `snake_case`. Base URL: `https://billing.example.com/v1`.

## Conventions

- **IDs** are opaque strings: never parse, sort, or construct them.
- **Money** is an integer count of minor units (`amount_cents`); never floats or strings. `currency` is uppercase ISO 4217.
- **Timestamps** are RFC 3339 UTC with `Z`.
- **Unknown request fields are rejected** with `400`. Unknown response fields and enum values must be tolerated; both are used for additive change.

## Authentication and tenancy

Send `Authorization: Bearer <api_key>`. The key determines the tenant; **no endpoint accepts a tenant id** and any `tenant_id` field is rejected. Another tenant's resource returns `404`, not `403`, so existence is not leaked. `X-Request-Id` is optional and echoed; errors carry `request_id`.

| Header | Where | Notes |
|---|---|---|
| `Authorization` | all | required |
| `Idempotency-Key` | all `POST` | required; see below |
| `If-Match` | `PATCH` | required |

## Resources

### Invoice

```json
{
  "id": "inv_8Qd2",
  "customer_id": "cus_3Kp1",
  "status": "draft",
  "currency": "USD",
  "version": 3,
  "created_at": "2026-11-01T09:00:00Z",
  "updated_at": "2026-11-05T11:20:04Z",
  "lines": [
    {"id": "lin_1", "description": "Seats", "quantity": 12, "unit_amount_cents": 1500, "position": 0}
  ],
  "totals": {"subtotal_cents": 18000, "total_cents": 18000}
}
```

`status` is `draft | open | paid | void`. `version` increments on every successful write and is the concurrency token. `totals` are server-computed; `total_cents` equals `subtotal_cents` in v1. `position` is server-assigned and read-only.

### Payment

```json
{"id": "pay_7Hq9", "invoice_id": "inv_8Qd2", "amount_cents": 18000, "currency": "USD",
 "status": "pending", "created_at": "2026-11-05T14:03:11Z", "updated_at": "2026-11-05T14:03:11Z"}
```

`status` is `pending | succeeded | failed | unknown`. Provider payloads, charge ids, and card data are **never** returned. Payments are immutable once terminal.

## Endpoints

### `GET /invoices`

Newest first. Query: `status`, `customer_id`, `created_from` (inclusive), `created_before` (exclusive), `limit` (1–200, default 50), `cursor`.

```json
{"data": [ /* Invoice */ ], "has_more": true, "next_cursor": "eyJjIjoiMjAyNi0xMS0wNVQxMToyMDowNFoiLCJpIjoiaW52XzhRZDIifQ"}
```

Ordering is `created_at` descending, then `id` descending, stable across pages. `cursor` is opaque: pass `next_cursor` verbatim and change nothing else between pages. Offset paging is not offered — it drifts at this scale.

### `GET /invoices/{id}`

`200` with an Invoice, including all lines.

### `POST /invoices`

Creates a `draft`. Body: `customer_id`, `currency`, `lines[]` (`description`, `quantity`, `unit_amount_cents`; `id` and `position` read-only).

`201` with the Invoice and `Location`. Validation: 1–200 lines; `quantity` 1–10000; `unit_amount_cents` 0–100000000; `description` 1–500 characters after trim. `customer_id` must exist in the caller's tenant, else `422`.

### `PATCH /invoices/{id}`

Edits a `draft` only; `409 invoice_not_editable` otherwise. Body is a partial Invoice: `currency` and/or `lines`. If `lines` is present it **replaces the full list**: an entry with a known `id` updates that line, one without `id` creates a line, omitted lines are deleted. `currency` is immutable once a payment exists (`409 currency_locked`).

Requires `If-Match: "<version>"` from the last read. Missing → `428`; stale → `412` with the current Invoice in the body so the client can merge and resubmit. This is how two support agents editing one draft avoid overwriting each other.

`200` with the updated Invoice and a new `version`.

### `POST /invoices/{id}/charge`

```json
{"amount_cents": 18000, "currency": "USD", "payment_method_token": "pm_9xK"}
```

`payment_method_token` is a provider token; never send raw card numbers.

Preconditions: invoice status `open` (`409 invoice_not_chargeable`); `amount_cents` equals `totals.total_cents` (`422 amount_mismatch`) and `currency` matches (`422 currency_mismatch`).

**This call can take 30 seconds and is not safe to retry blindly.** Behaviour:

- Record a Payment first, then call the provider. The `Idempotency-Key` maps to that Payment, so a retry with the same key returns the **same** payment and never charges twice.
- `201` — new payment with a terminal outcome.
- `202` — accepted, outcome not yet known (`pending` or `unknown`). Poll `GET /payments/{id}`; do not create another charge.
- `200` — replay of an earlier request with this key; returns the stored payment.
- Provider timeouts, provider 5xx, and unparseable responses yield `202` with `status: "unknown"`, not an error. `unknown` means "the provider did not tell us"; the service reconciles to a terminal state. Never resend without the original key.

### `GET /payments/{id}`

`200` with a Payment. Poll with backoff (1s, 2s, 4s, cap 30s) until `succeeded` or `failed`. One still `unknown` after 15 minutes should be escalated, not retried.

### `GET /invoices/{id}/payments`

Newest first, same cursor rules and envelope as `GET /invoices`. Webhooks are out of scope, so this is how a client reconciles an invoice after an ambiguous charge.

## Idempotency

`Idempotency-Key` is required on every `POST`; a UUIDv4 or ULID is recommended. Scope is `(tenant, key)`, independent of path.

- Same key, same body → original status and response replayed, `200` replacing the success code. Nothing is reprocessed.
- Same key, different body → `409 idempotency_key_reuse`.
- Key still in flight → `409 idempotency_key_in_flight`; retry once it resolves.
- Keys are retained **30 days**, then forgotten.

This makes offline-first sync, manual retries, batch reruns, and multi-day DLQ replays safe. The importer must derive a stable key per logical item (`batch-2026-11-04/item-0042`) and reuse it across reruns; a rerun that mints fresh keys will duplicate invoices and charges.

## Errors

```json
{"error": {"type": "conflict", "code": "invoice_not_editable",
 "message": "Invoice inv_8Qd2 is paid and cannot be edited.",
 "details": null, "request_id": "req_5c1"}}
```

`type` is stable and small: `invalid_request`, `unauthorized`, `not_found`, `conflict`, `precondition_failed`, `unprocessable`, `rate_limited`, `internal`. Branch on `code`, never on `message`. `details` is an array of `{"field","code"}` for validation failures, else `null`.

| Status | Meaning | Safe to retry? |
|---|---|---|
| `400` | malformed body, unknown field | no |
| `401` | missing/invalid key | no |
| `404` | absent in this tenant | no |
| `409` | state or idempotency conflict | no |
| `412` | `If-Match` stale | re-read, then yes |
| `422` | validation or amount mismatch | no |
| `428` | `If-Match` missing | yes, with header |
| `429` | rate limited | yes, after `Retry-After` |
| `500`/`503` | internal; include `request_id` | yes, same key |

Reads (`GET`) are always safe to retry. Writes are retryable only with the original `Idempotency-Key`.

## Versioning

The major version is in the path. Within `v1`, new optional response fields, endpoints, and enum values may appear at any time and must not break clients. Removing fields, tightening validation, or changing status codes requires `/v2` with a migration window. The payment provider has silently changed its response shape before, so its vocabulary is mapped to these fixed enums at the boundary and cannot alter this contract.

## Assumptions (repository is silent)

1. Only `draft` creation is exposed. No service method moves `draft → open`, `open → paid`, or to `void`; those happen internally, so clients treat `status` as read-only.
2. Invoice `description` appears in the service docstring but not in `db/schema.sql` or the model, so it is excluded. Adding it later is additive.
3. `position` is server-assigned from array order; clients reorder by resending `lines`.
4. Totals are derived from lines; no tax, discount, or rounding rules exist.
5. Idempotency retention is 30 days to exceed the importer's multi-day replay window.
6. Rate limits are unspecified; published values are placeholders pending product input.
7. `customer_id` is accepted, but no customer endpoints are in v1.
