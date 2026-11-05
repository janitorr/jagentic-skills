# Billing service

A small internal billing service for a SaaS product. It manages customers,
monthly invoices, invoice lines, and payments. The service is a Python package
with no HTTP layer yet.

## Domain

- A **customer** belongs to one tenant. Tenants are isolated.
- An **invoice** belongs to a customer and has a status: `draft`, `open`,
  `paid`, or `void`.
- An **invoice line** is a quantity, a unit amount in integer cents, and a
  description. Lines belong to an invoice.
- A **payment** records one attempt to collect an open invoice through the
  external payment provider. Money is integer cents; currency is ISO 4217.

## Current internal service

`src/billing/service.py` exposes Python methods used by an internal admin tool:

- `list_invoices(customer_id=None, status=None, limit=100, offset=0)`
- `get_invoice(invoice_id)`
- `create_draft(customer_id, lines)`
- `update_draft(invoice_id, patch)`
- `charge(invoice_id, amount_cents, currency, payment_method_token)`

The database schema is in `db/schema.sql`. There is no HTTP layer, no API
documentation, and no client SDK.

## Operating context

The web app and the mobile app will use the API directly. The mobile app is
offline-first and retries a request when connectivity returns; users also retry
actions by hand after a failure. A partner runs a nightly batch importer, reruns
failed batches, and replays them from a dead-letter queue for several days.

A charge calls the external payment provider and can take up to 30 seconds. The
provider has changed its response shape before without warning. A timeout does
not tell the service whether the charge was applied.

Support agents edit draft invoices. Two agents can have the same draft open at
once. Some tenants have tens of thousands of invoices, and the UI shows the
newest first, filtered by status and creation-date range.

Third parties will build against this API. API keys identify a tenant.
