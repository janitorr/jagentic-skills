# Task

Design the public v1 HTTP API for the billing service, for the web app, the
mobile app, and the partner batch importer.

Write `API.md` at the path given by the operator. It must be a contract a client
team can implement against without reading the Python service.

Cover invoice and payment operations: list invoices, read one invoice, create a
draft, edit a draft, and charge an open invoice. Webhooks, subscription plans,
refunds, and partial payments are out of scope.

Use the operating context in `README.md`. Do not write implementation code.
State assumptions where the repository is silent.
