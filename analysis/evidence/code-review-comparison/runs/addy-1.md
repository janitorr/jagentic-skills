# Review: add user search endpoint (`feature/user-search` → `main`)

## Context

`GET /users/search?q=&limit=&cursor=` for support staff, per `docs/specs/user-search.md` and
`openspec/changes/add-user-search`. Intent is clear and the spec is unusually precise: authenticated,
tenant-scoped, case-insensitive match on `display_name`, `id` + `display_name` only, `limit`
default 20 / max 50, opaque `cursor`/`next_cursor`, empty `q` → 422.

The implementation in `app/users.py:13-19` does essentially none of that. Diff is small (98 lines),
and the failure is not a size problem — it is that the code contradicts every binding rule in
`CODING_STANDARDS.md` (auth, tenant scope, SQL, PII, list endpoints, canonical helpers, response
fields).

## Verdict: Request changes — do not merge

This is a security regression, not a style disagreement. The new handler replaces the repository's
own stated contract with a tenant-wide (cross-tenant, actually) PII dump reachable by an
unauthenticated caller.

## Critical

### 1. SQL injection — `app/users.py:15-17`

```python
rows = db.query(f"SELECT id, email, display_name FROM users WHERE email LIKE '%{q}%'")
```

`q` is interpolated into the statement. `?q=' OR '1'='1` returns every row; `?q=' UNION SELECT
id,email,display_name FROM users --` reads the table. This violates `CODING_STANDARDS.md` #3
("Never build SQL with f-strings...") and is a textbook injection.

Remedy: parameterize through the existing canonical helper:

```python
rows = db.find_users(request.user.tenant_id, q, limit=limit, cursor=cursor)
```

`Database.find_users(tenant_id, q, limit=20, cursor=None)` already exists in `app/db.py:8` with the
docstring "tenant-scoped users matching q with a stable page order". The handler should not be
composing SQL at all.

### 2. No authentication — `app/users.py:13`

`get_user` is decorated with `@require_auth`; `search_users` is not. `CODING_STANDARDS.md` #1 says
every route handler must be wrapped. The audit line at :18 dereferences `request.user.email`, so an
unauthenticated request either crashes with `AttributeError` (500) or, if `args`/logging is
reordered, leaks data to anonymous callers. Add `@require_auth`.

### 3. No tenant scoping — `app/users.py:15-17`

`WHERE email LIKE ...` has no `tenant_id` predicate and `request.user.tenant_id` never appears. The
first requirement in the OpenSpec delta ("Tenant-scoped user search") and `CODING_STANDARDS.md` #2
("Never return another tenant's rows") are both violated: the query returns users from all tenants.
This is an authorization bypass, not merely a missing filter.

### 4. Email returned to the caller — `app/users.py:16,19`

The query selects `email` and returns rows verbatim. Spec: "Return `id` and `display_name` only.
Never return `email`." Standards #7: "Return only the fields the spec allows." The test at
`tests/test_users.py:39-45` asserts that `email` **is** present, so the suite actively enshrines the
leak (see evidence below). Project the fields in the handler or, better, in `find_users`:

```python
return {"users": [{"id": r["id"], "display_name": r["display_name"]} for r in rows], "next_cursor": ...}
```

### 5. PII written to the audit log — `app/users.py:18`

```python
audit_log.info(f"search by {request.user.email}: {q}")
```

`CODING_STANDARDS.md` #4: "Never log email addresses, display names, or raw query text. Log counts,
IDs, and request IDs only." This line logs two prohibited values — the **caller's** email and the raw
query, which is itself PII in a user-search context. It also permits log forging via newlines in `q`.
Log a count and a request ID instead (e.g. `audit_log.info("user_search", extra={"count":
len(rows), "request_id": ...})`).

### 6. Unbounded, unpaginated result set — `app/users.py:14-19`

`limit` and `cursor` are ignored and no `next_cursor` is returned. Spec requires limit default 20,
max 50, stable `display_name ASC, id ASC` order, and an opaque cursor. `CODING_STANDARDS.md` #5
requires the same. Combined with `q=%` (a single `%` wildcard matches everything) and the missing
tenant filter, one request can dump the whole `users` table. This is the unbounded-fetch case the
performance axis calls out, and here it is also a data-exfiltration vector.

## Required

### 7. Empty/whitespace `q` is not rejected — `app/users.py:14`

`q = request.args.get("q", "")` accepts `""` and `"   "` and runs a match-all search. Spec and the
OpenSpec scenario require 422. Validate before querying:

```python
q = (request.args.get("q") or "").strip()
if not q:
    return {"error": "q is required"}, 422
```

### 8. Wrong field and no case-insensitive match — `app/users.py:16`

The spec says `q` matches **`display_name`** case-insensitively; the query matches `email`. This is
a functional miss independent of the injection: searching a name returns nothing useful, and
searching an email prefix confirms/denies an address (an enumeration oracle). Also, `LIKE` on
Postgres is case-sensitive, so "case-insensitively" needs `lower(display_name) LIKE lower(...)` or
the helper's semantics — verify `find_users` does this, and add a test either way.

### 9. Tests encode the spec violation and constrain nothing — `tests/test_users.py:22-23,32-46`

The `FakeDB.query` stub ignores `sql` and `params` and returns a hard-coded row containing `email`;
`test_returns_matches` then asserts that exact dict, including `email`. Consequences, verified by
mutation probe:

- Replace the entire query with `db.query("SELECT 1")` → **suite stays green**. The test exercises
  no SQL, no parameters, no tenant filter, and no `q` handling. It cannot catch injection, a
  cross-tenant read, or the missing 422.
- Make the handler spec-compliant (strip `email` from the response) → **suite goes red**. The
  correct fix breaks the test, so the test is a regression guard for the bug.

The `FakeDB` must record `(sql, params)` so tests can assert parameterization and tenant scoping, or
(consistent with the standards) the handler should call `find_users` and the fake should implement
that method and assert `tenant_id` was passed. Missing cases: no-auth (`AuthError`), `q=` / `q="  "`
→ 422, email absent from response, `limit=500` capped/rejected, `next_cursor` present, tenant A
never sees tenant B.

### 10. Tasks claim work that is undone — `openspec/changes/add-user-search/tasks.md`

Both tasks are unchecked, and the second ("tests for tenant scoping, field selection, and
pagination") is exactly the coverage that is absent. Either the change is not complete or the
tracker is stale; neither should merge as-is. Tick them only when the tests above exist and pass.

## Nit

- Commit `2f28cb0 "add user search endpoint"` has no body. Standards follow `git-workflow`:
  `<area>: <imperative summary>` plus why. "add user search endpoint" states the what only; the
  spec link and the tenant/PII constraints belong in the body.
- `request.args.get("q", "")` vs `get_user`'s `request.args["id"]` are inconsistent access styles;
  not worth changing in this diff, but the validation in #7 should settle on one.

## What is good

- The spec, proposal, and OpenSpec delta are coherent, specific, and testable — rare and valuable.
  The scenarios map cleanly to the missing tests.
- Change size is right (~100 lines), and `get_user` is untouched; no collateral refactoring.
- The endpoint name and handler location match existing structure.

## Verification story

- `python3 -m unittest discover -s tests` → 2 passed. Green, but not meaningful: the search test
  asserts the wrong contract (evidence above). No auth, 422, pagination, tenant, or PII assertions.
- No manual verification. There is no router/framework in this fixture, so no live call was possible;
  the handler was assessed directly.
- Mutation probes run in the isolated copy (`/tmp/opencode/cr-compare/iso-addy-1` at the time),
  never in the review tree. Probe 1: query replaced with `SELECT 1` → green. Probe 2: email stripped
  → red. Probe 3: `@require_auth` added → green (no test can detect auth either way).

## Checklist

- Correctness: ✗ wrong field, missing 422, no pagination, no tenant filter
- Readability: ✓ small and readable — the problem is what it does, not how it reads
- Architecture: ✗ duplicates/bypasses `Database.find_users`, the canonical helper
- Security: ✗ injection, no auth, cross-tenant read, PII in response and logs
- Performance: ✗ unbounded list endpoint, no limit/cursor
- Tests: ✗ pass while asserting the defect; would not catch a regression
- Build/verification: tests green only because their oracle is wrong

Fix order: auth + `find_users` call (kills #1–#3, #6, #8) → response projection (#4) → logging (#5)
→ 422 (#7) → rewrite the search test as a behavior test (#9) → tick tasks (#10).
