# Billing API v1

Public HTTP contract. Base URL `https://api.example.com/v1`. JSON UTF-8 only; TLS required. All timestamps are RFC 3339 UTC (`Z`). All money is an integer in the currency's minor unit (cents); floats are invalid.

## Authentication and tenant isolation

Send `Authorization: Bearer <api-key>`. The key resolves to exactly one tenant server-side. Requests never carry a `tenant_id`; if one is supplied it is rejected. Every read and write is scoped to the key's tenant. An ID belonging to another tenant returns `404 not_found`, never `403`, so existence is not leaked. Missing, invalid, or revoked key: `401 unauthorized`. Valid key without the required permission: `403 forbidden`.

## Resources

**Invoice**

| Field | Type | Notes |
|---|---|---|
| `id` | string | Opaque, stable, URL-safe. |
| `customer_id` | string | Immutable after creation. |
| `status` | enum | `draft`, `open`, `paid`, `void`. Read-only. |
| `currency` | string | ISO 4217, uppercase. |
| `version` | integer | Starts at 1; increments on every persisted change. |
| `created_at`, `updated_at` | string | Server-set, immutable. |
| `lines` | array | Detail responses only; absent from list items. |
| `total_amount_cents` | integer | Sum of line `amount_cents`. |

**InvoiceLine**: `id` (string), `description` (string), `quantity` (integer), `unit_amount_cents` (integer), `position` (integer, 0-based, array order), `amount_cents` (integer, `quantity * unit_amount_cents`).

**Payment**: `id` (string), `invoice_id` (string), `amount_cents` (integer), `currency` (string), `status` (`pending`, `succeeded`, `failed`, `unknown`), `failure_code` (string or null), `created_at`, `updated_at`.

Provider payloads and charge IDs are never exposed. `failure_code` is a stable enum: `card_declined`, `insufficient_funds`, `expired_card`, `provider_rejected`, `other`; unmapped provider reasons become `other`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/invoices` | List invoices |
| POST | `/invoices` | Create a draft |
| GET | `/invoices/{invoice_id}` | Read one invoice |
| PATCH | `/invoices/{invoice_id}` | Edit a draft |
| POST | `/invoices/{invoice_id}/charge` | Charge an open invoice |
| GET | `/payments/{payment_id}` | Poll a payment |

### List invoices

`GET /invoices?customer_id=&status=&created_after=&created_before=&limit=&cursor=`

- All filters optional; `status` is one of the four values.
- `created_after` is inclusive, `created_before` exclusive.
- Sort is `created_at DESC, id DESC` (stable tie-break).
- `limit` is 1-100, default 25.
- Response: `{ "data": [Invoice without lines], "next_cursor": string|null }`.
- `cursor` is opaque, signed, and bound to the filter set and sort. Reusing it with different filters returns `400 invalid_cursor`. Tampering returns the same.
- Keyset pagination: existing rows are neither skipped nor duplicated while paging. Rows created after the first page are seen by refreshing the first page.

### Create draft

`POST /invoices`, headers `Idempotency-Key` (required), `Content-Type: application/json`.

```json
{"customer_id":"cus_123","currency":"USD","lines":[{"description":"Seats","quantity":5,"unit_amount_cents":1200}]}
```

`lines` may be empty. `position` is assigned from array order. Returns `201` with the Invoice, `Location: /v1/invoices/{id}`, and `ETag: "v1"`. Unknown or cross-tenant `customer_id`: `404 customer_not_found`.

### Read invoice

`GET /invoices/{invoice_id}` returns `200` with the full Invoice and `ETag: "v{version}"`.

### Edit draft

`PATCH /invoices/{invoice_id}`, headers `If-Match` and `Idempotency-Key` (both required), `Content-Type: application/json`.

Body may contain `currency` and/or `lines`. Omitted fields are unchanged; `lines`, when present, replaces the entire line collection. `null` is invalid. Line IDs may change after replacement. If `currency` changes while lines exist, `lines` must be included in the same request, otherwise `422 currency_change_requires_lines`; amounts are never converted. Invoice-level description does not exist; descriptions belong to lines.

Only `draft` invoices are editable; otherwise `409 invalid_state`. Missing `If-Match`: `428 precondition_required`. Stale ETag: `412 precondition_failed`, with `meta.current_version`. Success returns `200`, the updated Invoice, and a new `ETag`.

### Charge open invoice

`POST /invoices/{invoice_id}/charge`, headers `If-Match` and `Idempotency-Key` (both required).

```json
{"amount_cents":6000,"currency":"USD"}
```

`amount_cents` must equal the invoice `total_amount_cents` at the matched version and `currency` must match, else `422 amount_mismatch`. Empty or zero-total invoices cannot be charged. Only `open` invoices are chargeable.

The provider call may take 30 seconds, so this endpoint never waits for it. It validates, atomically records a Payment with status `pending`, queues the provider call, and returns `202` with the Payment and `Location: /v1/payments/{payment_id}` plus `Retry-After: 2`. Poll the payment URL until `succeeded`, `failed`, or `unknown`. `unknown` means the outcome is indeterminate; it is not failure. Support reconciles it, after which it becomes `succeeded` or `failed`.

Safety rules: a `pending` or `unknown` payment blocks a new charge with a different key (`409 payment_in_flight`); a `succeeded` payment yields `409 invoice_already_paid`; a `failed` payment permits a new key. This prevents double charges even when clients misuse keys.

### Poll payment

`GET /payments/{payment_id}` returns `200` with the Payment. Cross-tenant and unknown IDs both return `404`.

## Idempotency and retries

Idempotency keys are scoped to tenant plus endpoint, retained 30 days, and must be 16-128 printable characters. The server stores a fingerprint of method, path, and normalized body. Replaying the same key and body returns the original status and body (with `Idempotency-Replayed: true`), even if state later changed. Reusing a key with a different body returns `409 idempotency_key_reuse`. A concurrent duplicate of a still-running create or edit returns `409 idempotency_in_progress` with `Retry-After: 1`; charge duplicates return the same `202` Payment. `5xx` and `429` are not stored; state changes and key records commit atomically, so committed writes always replay and retries are safe. `4xx` validation responses are stored.

- Retry `429` and `5xx` with the **same** key, exponential backoff, and jitter; honor `Retry-After`.
- Never retry other `4xx`. On `412`, re-read the invoice and reapply the user's change.
- Clients must persist the key across app restarts and reuse it until a terminal outcome. Only a genuinely new action, or a retry after a confirmed `failed` payment, gets a new key.
- The 30-day retention covers the mobile app's next-day retry and the partner's seven-day retry and dead-letter replays. The payment safety rules remain the final duplicate guard after expiry.

## Error format

Errors use `application/problem+json`:

```json
{"type":"https://api.example.com/problems/validation-failed","title":"Validation failed","status":422,"code":"validation_failed","detail":"quantity must be at least 1","request_id":"req_123","errors":[{"field":"lines[0].quantity","code":"min_value"}]}
```

`code` is stable and machine-readable; `detail` is not. Statuses: `400` malformed input/cursor, `401`, `403`, `404`, `409` state/idempotency conflict, `412`, `415`, `422` validation, `428`, `429`, `500`, `503`.

## Validation

`quantity` is 1-1,000,000; `unit_amount_cents` is 0 to 100,000,000; `description` is 1-500 characters; at most 500 lines; request body at most 1 MB. `amount_cents` is a positive int64. Unknown request fields return `422 unknown_field`.

## Compatibility

The path is versioned (`/v1`). Within v1 only additive changes are allowed: new optional request fields, new response fields, new endpoints. No field is renamed, removed, retyped, or made required. The four invoice statuses, four payment statuses, and `failure_code` values are closed in v1; adding an enum value is breaking and requires `/v2`. Error codes are stable. Deprecations are announced at least 12 months ahead with `Deprecation` and `Sunset` headers; nothing is removed from v1.

## Assumptions

- Issuing (draft to open) and voiding are internal operations outside this public v1 scope; this API only charges invoices already `open`.
- V1 supports full-balance charges only; partial payments, tax, discounts, and credit notes are out of scope.
- Customers are created elsewhere; this API only references existing `customer_id` values.
- Drafts may be empty. Line amounts are nonnegative. One currency applies to the whole invoice.
- Key issuance, scopes, quotas, and rotation are outside this contract.
- Webhooks and subscription plans are out of scope.
