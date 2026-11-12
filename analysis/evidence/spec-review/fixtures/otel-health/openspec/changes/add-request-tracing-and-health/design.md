# Design

## Context

See `proposal.md - Why`. Current state that shapes the approach:

- `app/main.py` builds the FastAPI app and includes the orders router. It does
  not trace requests and does not expose a health endpoint.
- `app/checks.py` provides `database_ready()` and `cache_ready()` from the
  `DATABASE_READY` and `CACHE_READY` environment flags.
- `requirements.txt` pins `opentelemetry-instrumentation-fastapi` and
  `fastapi-health`.
- Architecture review approved a custom ASGI `TracingMiddleware` and a custom
  `/health` route; a branch contains the middleware skeleton.
- The tracing backend is configured by the deployment, not this repository.

## Goals / Non-Goals

**Goals:**

- Emit exactly one request span per HTTP request with route, method, status, and
  duration, including for failed requests.
- Make `/health` return `200` only when both dependency checks pass and `503`
  when either fails, with per-dependency status in the body.
- Keep the existing orders behavior and test suite unchanged.

**Non-Goals:**

- Configuring exporters, collectors, sampling, or the tracing backend.
- Adding dashboards, alerts, or health-endpoint authentication.
- Implementing real database or cache clients; the existing readiness callables
  remain the integration point.
- Changing the orders API or its routing.

## Decisions

### Use an explicit ASGI middleware for tracing

Add an ASGI middleware that opens a span with `opentelemetry.trace.get_tracer`,
records `http.route`, `http.method`, and `http.status_code`, and lets the span's
own start/end timestamps represent duration. It wraps the downstream app in
`try/except/finally`, records exceptions and marks the span as errored, and
captures the response status by wrapping `send`.

Rationale: the approved approach, and an explicit span keeps the required
attributes under our control for both successful and failed requests.

Alternatives considered:

- Wire `FastAPIInstrumentor.instrument_app(app)` and use its automatic spans.
  Rejected because the approved design wants explicit, predictable attributes on
  failures.
- Add the custom middleware while also wiring `instrument_app`. Rejected because
  it would produce duplicate spans.

### Implement `/health` as an explicit route

Add a `GET /health` route that calls `database_ready()` and `cache_ready()`,
returns `200` when both are true, and returns `503` otherwise. The body reports
each dependency.

Rationale: the approved approach gives a stable response shape and makes the
mapping from checks to status codes obvious.

Alternatives considered:

- Mount the installed `fastapi-health` handler over the same checks. Rejected
  because the approved design wants an explicit route and a per-dependency body.

## Risks / Trade-offs

- Missing or duplicate spans → keep the middleware as the only span source and
  test success and failure paths.
- Route is not available for unmatched or early failures → fall back to the raw
  path and record the status once `send` reports it.
- Middleware mistakes can break streaming or non-HTTP traffic → pass through
  non-HTTP scopes and forward `send`/`receive` unchanged.
- Web dependencies are not installed in the unit-test environment → keep the
  existing import-light tests green, and verify the middleware and `/health` in
  an environment with `requirements.txt` installed.

## Migration Plan

Deploy the application normally. The tracing backend and load balancer need no
change; the load balancer can start using `GET /health` once the new version is
live. Roll back by restoring the previous `app/main.py`; no data migration is
involved.

## Open Questions

None.
