# Issue 23: Trace requests and expose health checks

## Problem

On-call cannot tell which route failed or how long it took. The load balancer
has no health endpoint, so a failing dependency keeps traffic on the instance.

## Outcome

Every request appears in the tracing backend with its route, method, status, and
duration. `GET /health` reports database and cache readiness.

## In scope

- Per-request trace spans with route, method, status, and duration
- A health endpoint that reports database and cache status

## Out of scope

- Changing the tracing backend
- Dashboards or alerts
- Authentication for the health endpoint

## Acceptance criteria

- [ ] A request to `/orders` appears in the tracing backend with route, method,
      status, and duration
- [ ] A failed request is still traced with its status
- [ ] `GET /health` returns 200 when both dependencies are ready and 503 when
      one is not
- [ ] Existing tests pass

## Context

Architecture review approved a custom ASGI `TracingMiddleware` for tracing and a
custom `/health` route for readiness. The `tracing-middleware` branch already
contains the middleware skeleton, so the reviewer expects that approach.
