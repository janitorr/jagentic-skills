# Billing API v1

Contract for web, mobile, and partner batch clients. Scope: list/read invoices,
create/edit drafts, charge an open invoice, read a payment. Out of scope:
webhooks, plans, refunds, partial payments.

## Module and seam

The module is the `/v1` HTTP surface: one interface in front of tenancy,
storage, provider calls, and retry semantics. Delete it and every client
re-implements auth scoping, idempotency, pagination, and conflict handling, so
it earns its keep. The provider is the varying seam; its JSON never crosses this
interface. Clients and contract tests use the same surface.

## Conventions

- HTTPS only. `Authorization: Bearer <api_key>`. The key resolves the tenant;
  tenant is never in a path or body. A resource in another tenant is `404`.
- JSON UTF-8, `snake_case`. Unknown request fields are `422 unknown_field`.
- IDs are opaque (`cus_`, `inv_`, `pay_`). Never parse or construct them.
- Money is integer cents in `*_cents` fields; never floats or decimal strings.
  Currency is ISO 4217 uppercase. One currency per invoice.
- Timestamps are RFC 3339 UTC (`2026-03-01T09:00:00Z`).
- Responses carry `Request-Id`; every error body repeats it.
- Within `/v1` changes are additive only: clients must ignore unknown response
  fields and tolerate unknown enum values. Breaking changes require `/v2`.
- `429` carries `Retry-After` seconds.

## Errors

```json
{"error":{"type":"conflict","code":"version_conflict",
  "message":"Invoice was modified by another request.",
  "details":{"current_version":4},"request_id":"req_01H..."}}
```

`type` is one of `invalid_request`, `authentication_error`, `not_found`,
`conflict`, `rate_limited`, `server_error`. `code` is stable and is what
clients branch on: `missing_field`, `unknown_field`, `invalid_field`,
`invalid_currency`, `unknown_customer`, `not_found`, `invoice_not_draft`,
`invoice_not_open`, `charge_in_progress`, `version_conflict`,
`precondition_required`, `idempotency_key_reuse`, `idempotency_in_progress`,
`internal_error`. HTTP status: 400/401/404/409/422/428/429/500/503.

## Idempotency

Every `POST` and `PATCH` requires `Idempotency-Key: <8–255 chars>`. Scope is
tenant + method + path. A replay returns the original status, body, and headers
with `Idempotency-Replayed: true`; it never repeats the effect. Same key with a
different body is `409 idempotency_key_reuse`; a key still executing is
`409 idempotency_in_progress` plus `Retry-After`. Keys are retained 30 days
(assumption: covers partner dead-letter replays "for several days"). Use a new
key only for a new intent — never to "retry harder".

## Concurrency

`Invoice.version` is a strong validator exposed as `ETag: "3"`. `PATCH` requires
`If-Match`; missing it is `428 precondition_required`; mismatch is
`409 version_conflict` with `details.current_version`. Flow: `GET`, edit,
`PATCH` with that ETag; on conflict re-`GET`, reapply, retry. Two support agents
on one draft therefore cannot silently overwrite each other.

## Pagination

`GET /v1/invoices` is cursor-based, ordered `created_at` desc, then `id` desc.
That order is stable under concurrent inserts, unlike offset paging on tens of
thousands of rows.

```json
{"data":[/* invoices */],"next_cursor":"eyJjIjoiMjAyNi0wMy0wMVQwOTowMDowMFoiLCJpIjoiaW52XzAifQ","has_more":true}
```

`next_cursor` is opaque: pass it back verbatim as `cursor`; empty means start.
Malformed cursor is `422 invalid_field`. No total count is offered (it would be
a full scan). `has_more` is advisory; `next_cursor` is authoritative.

## Resources

```json
{"id":"inv_01H8","object":"invoice","customer_id":"cus_01H2",
 "status":"draft","currency":"USD","total_cents":12500,"version":3,
 "lines":[{"description":"Seat, March","quantity":5,"unit_amount_cents":2500,
           "amount_cents":12500}],
 "created_at":"2026-03-01T09:00:00Z","updated_at":"2026-03-01T09:12:41Z"}
```

Lines are always included; their `id` and `position` are server-owned and not
exposed. Client array order is the line order. `total_cents` and each
`amount_cents` are computed by the server from `quantity × unit_amount_cents`.

```json
{"id":"pay_01H9","object":"payment","invoice_id":"inv_01H8",
 "amount_cents":12500,"currency":"USD","status":"pending",
 "created_at":"2026-03-01T09:20:00Z","updated_at":"2026-03-01T09:20:00Z"}
```

Provider identifiers are never exposed.

## Operations

### List invoices

`GET /v1/invoices?status=open&status=paid&customer_id=cus_01H2&created_from=2026-02-01T00:00:00Z&created_to=2026-03-01T00:00:00Z&limit=50&cursor=...`

`status` is repeatable; `created_from` is inclusive, `created_to` exclusive;
`limit` defaults 50, max 200. Returns the pagination envelope above.

### Read one invoice

`GET /v1/invoices/{invoice_id}` → `200`, invoice, `ETag: "<version>"`.
Unknown or other-tenant id → `404 not_found`.

### Create a draft

`POST /v1/invoices` with `Idempotency-Key`.

```json
{"customer_id":"cus_01H2","currency":"USD",
 "lines":[{"description":"Seat, March","quantity":5,"unit_amount_cents":2500}]}
```

`201`, `Location: /v1/invoices/inv_01H8`, `ETag`, invoice with `status:"draft"`,
server-assigned ids, `total_cents`. Rules: 1–200 lines; description 1–500
chars; quantity 1–100000; unit amount 0–100000000; `currency` required.
`422 unknown_customer` if the customer is not in the tenant.

### Edit a draft

`PATCH /v1/invoices/{invoice_id}` with `Idempotency-Key` and `If-Match`.
Body may contain `currency` and/or `lines`; `lines` replaces the whole set, so
the call is naturally idempotent and no line ids are needed. Omitted fields are
unchanged. `status`, `customer_id`, `total_cents`, and `version` are not
patchable. Only `draft` invoices may be edited: otherwise
`409 invoice_not_draft`. Success is `200` with the invoice and a new `ETag`.

### Charge an open invoice

`POST /v1/invoices/{invoice_id}/charge` with `Idempotency-Key`.

```json
{"payment_method_token":"pm_tok_..."}
```

No amount or currency is accepted: the server charges `total_cents` in the
invoice currency, so clients cannot miscompute the amount. Requires
`status:"open"`; a draft or paid invoice is `409 invoice_not_open`. An invoice
with a `pending` or `unknown` payment and a *new* key is
`409 charge_in_progress` with `details.payment_id` — reuse the original key and
poll instead.

Response is `202` with `Location: /v1/payments/{payment_id}` and the payment.
It is returned as soon as accepted; the provider call may still be running.
`202` is used regardless of the current payment state; `status` is authoritative.

### Read a payment

`GET /v1/payments/{payment_id}` → `200` payment. This is the only resolution
path while webhooks are out of scope. Poll with backoff; `pending` may last up
to ~30 seconds.

## State rules

- Invoice: `draft → open → paid`, `draft|open → void`. v1 never performs
  `draft → open`; issuance stays in the internal admin tool (assumption).
  Invalid transitions are `409`.
- Payment: `pending → succeeded | failed | unknown`. `unknown` means the
  provider call timed out and we do not know whether money moved. `unknown` is
  not success and not failure: it may later resolve once to `succeeded` or
  `failed`. Clients must poll and must **not** start a new charge for that
  invoice; if it stays `unknown`, escalate with the payment id and `Request-Id`.
  This is why charge cannot be a blocking 30-second request that reports a
  boolean.

## Alternatives considered

- **Charge:** blocking `200` (rejected: a 30s mobile request fails, and a
  timeout would have to lie), top-level `POST /v1/payments` (rejected: charge
  is an invoice transition, and nesting makes the precondition explicit).
  Chose `202` plus payment read.
- **Paging:** `limit`/`offset`, mirroring the internal service (rejected: deep
  offsets and shifting rows skip or duplicate invoices newest-first). Chose keyset.
- **Draft edits:** version in the body (rejected: easy to omit and to send
  stale) and pessimistic locks (rejected: lock lifetime across human edits).
  Chose `If-Match`/`ETag`, which is the HTTP-native lost-update guard.

## Assumptions and open questions

- Draft issuance (`draft → open`) is out of v1; if external clients need it,
  add `POST /v1/invoices/{id}/open` rather than a status patch.
- One full charge per invoice; partial payments and refunds are out of scope.
- Idempotency retention is 30 days; confirm against partner replay windows.
- "Description" is a line field only; invoices have no separate description.
- Provider response-shape changes are absorbed by an internal adapter; the
  contract exposes only our four payment states.
