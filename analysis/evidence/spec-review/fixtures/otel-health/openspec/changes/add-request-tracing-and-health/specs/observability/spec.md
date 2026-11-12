# Spec Delta

## Purpose

Expose request-level tracing and dependency health so operators can diagnose
failures and load balancers can route only to ready instances.

## ADDED Requirements

### Requirement: Per-request trace spans

The service SHALL record a trace span for every HTTP request, including requests
that fail, recording the matched route, HTTP method, response status, and
duration.

#### Scenario: Successful route is traced

- **WHEN** a caller sends a request to `GET /orders` that succeeds
- **THEN** the tracing backend receives a span for that request containing the
  route, method `GET`, the response status, and the request duration

#### Scenario: Failed request is traced

- **WHEN** a caller sends a request that results in an error response
- **THEN** the tracing backend receives a span for that request containing its
  route, method, response status, and duration

### Requirement: Dependency health endpoint

The service SHALL expose `GET /health` reporting the readiness of the database
and cache, returning `200` when both are ready and `503` when either is not.

#### Scenario: All dependencies ready

- **WHEN** the database and cache are both ready
- **THEN** `GET /health` returns `200`

#### Scenario: A dependency is not ready

- **WHEN** the database or the cache is not ready
- **THEN** `GET /health` returns `503` and reports the dependencies' status
