# Proposal

## Why

On-call cannot tell which route failed or how long it took, because requests are
not traced. The load balancer also has no health endpoint, so a failing database
or cache dependency keeps traffic on the instance.

## What Changes

- Add a custom ASGI `TracingMiddleware` that records route, method, status, and
  duration per request, including failed requests.
- Add a custom `GET /health` route that reports database and cache readiness,
  returning `200` when both are ready and `503` when either is not.
- Keep the existing `opentelemetry-instrumentation-fastapi` and `fastapi-health`
  dependencies pinned but do not wire their automatic instrumentation.

## Capabilities

### New Capabilities

- `observability`: request tracing and dependency health reporting for the
  service.

### Modified Capabilities

None. The orders listing requirement is unaffected.

## Impact

- `app/main.py`: tracing middleware and `/health` route wiring.
- `app/checks.py`: existing readiness checks reused by the route.
- Dependencies: no new packages; the approved approach uses the pinned
  `opentelemetry-instrumentation-fastapi` and `fastapi-health` only as
  dependencies, not as the implementation.
- Observability backend and deployment configuration remain external and out of
  scope. No authentication is added to `/health`.
