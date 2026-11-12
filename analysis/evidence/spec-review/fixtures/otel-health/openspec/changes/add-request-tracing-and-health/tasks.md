# Tasks

## 1. Request tracing middleware

- [ ] 1.1 Add an ASGI tracing middleware in `app/main.py` that starts one span per HTTP request, records `http.route` (falling back to the request path), `http.method`, and the status captured from the response, and marks the span errored when the app raises; verify with `python3 -m py_compile app/main.py`.
- [ ] 1.2 Pass non-HTTP scopes through unchanged and forward `receive`/`send` without altering the response body; verify the middleware leaves the lifespan startup and shutdown paths working when running the app.
- [ ] 1.3 Do not wire `FastAPIInstrumentor`; verify with `grep -rn "instrument_app" app/` returning no matches.
- [ ] 1.4 Add tests covering a successful `/orders` request and a failing request, asserting each produces one span with the route, method, status, and a positive duration; verify with `python3 -m unittest discover -s tests -v` in an environment with `requirements.txt` installed.
- [ ] 1.5 Update the Observability section of `README.md` to describe the request middleware; verify the README matches the code in `app/main.py`.

## 2. Dependency health endpoint

- [ ] 2.1 Add an explicit `GET /health` route that calls `database_ready()` and `cache_ready()`, returns `200` when both are true, and returns `503` with per-dependency status when either is false; verify with `python3 -m py_compile app/main.py`.
- [ ] 2.2 Do not mount the `fastapi-health` handler; verify with `grep -rn "fastapi_health" app/` returning no matches.
- [ ] 2.3 Add tests asserting `GET /health` returns `200` when both checks pass and `503` when either check fails, with both dependency states in the body; verify with `python3 -m unittest discover -s tests -v` in an environment with `requirements.txt` installed.
- [ ] 2.4 Update the Observability section of `README.md` to describe the `/health` status mapping; verify the README matches the route in `app/main.py`.

## 3. Full verification

- [ ] 3.1 Run the complete test suite with `python3 -m unittest discover -s tests -v` and confirm every pre-existing test still passes.
- [ ] 3.2 Run `python3 -m py_compile app/main.py app/routes.py app/config.py app/checks.py` and confirm the tracing and health changes compile cleanly.

## Workflow follow-up

- Archive the change after the implementation is reviewed and the acceptance criteria are verified.
