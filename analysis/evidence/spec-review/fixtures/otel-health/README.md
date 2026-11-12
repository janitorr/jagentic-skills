# Orders API

FastAPI service for the storefront and partner portal.

## Observability

The service has no tracing or readiness endpoint yet. The deployment configures
the tracing backend.

## Dependencies

See `requirements.txt`. The deployment image installs them; the unit tests do not
import the web stack.
