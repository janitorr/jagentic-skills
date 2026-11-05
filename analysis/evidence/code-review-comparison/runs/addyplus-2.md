# Review: add user search endpoint (`feature/user-search` → `main`)

## Context

`GET /users/search?q=&limit=&cursor=` lets support staff find a user by name
(`docs/specs/user-search.md`, `openspec/changes/add-user-search`). The spec is
specific: authenticated, tenant-scoped, case-insensitive match on
`display_name`; `id` and `display_name` only; `limit` default 20 / max 50;
opaque `cursor`/`next_cursor`; order `display_name ASC, id ASC`; empty or
whitespace-only `q` → 422.

The change is small (98 lines), so size is not the issue. The problem is that
`search_users` (`app/users.py:13-19`) contradicts every binding rule in
`CODING_STANDARDS.md` (#1 auth, #2 tenant, #3 SQL, #4 PII, #5 list endpoints,
#6 canonical helpers, #7 response fields) and most of the spec delta.

## Verdict: Request changes — do not merge

This is a security regression, not a style disagreement: an unauthenticated,
cross-tenant PII dump with a SQL-injection entry point. It cannot be fixed by
nits; the handler should be rewritten around the canonical helper.

## Critical

### 1. SQL injection — `app/users.py:15-17`

```python
rows = db.query(f"SELECT id, email, display_name FROM users WHERE email LIKE '%{q}%'")
```

`q` comes straight from `request.args` and is interpolated into the statement.
Probed with a recording fake DB: `q="a' OR '1'='1"` emitted
`... WHERE email LIKE '%a' OR '1'='1%'` with `params == ()`. Violates standards
#3 ("Never build SQL with f-strings, `%`, or string concatenation") and OWASP
A03. Remedy: `db.find_users(request.user.tenant_id, q, limit=limit, cursor=cursor)`.
The helper already exists and is parameterized by contract (`app/db.py:8`).

### 2. No authentication — `app/users.py:13`

`get_user` carries `@require_auth`; `search_users` does not. Standards #1
requires it on every route handler. Probing with `request.user = None` reached
the query and only failed later at the audit line (`AttributeError`), so the
unauthenticated path today executes the query and returns 500; remove or move
the logging line and it becomes an anonymous data endpoint. Reaching user data
before any auth check is the defect, not the eventual exception.

### 3. No tenant scoping — `app/users.py:15-17`

There is no `tenant_id` predicate and `request.user.tenant_id` never appears.
This violates the OpenSpec "Tenant-scoped user search" requirement, standards
#2, and OWASP A01 (IDOR). Search results are drawn from every tenant's rows.

### 4. Email returned to the caller — `app/users.py:16,19`

The query selects `email` and returns `rows` verbatim. Spec and standards #7:
return `id` and `display_name` **only**, never `email`. This is a direct PII
disclosure regardless of the injection.

### 5. PII written to the audit log — `app/users.py:18`

```python
audit_log.info(f"search by {request.user.email}: {q}")
```

Standards #4 forbids logging email addresses, display names, and raw query
text. This logs the caller's email and the raw `q`; free-form `q` also permits
log forging via newlines. Log a result count and request ID instead, and use
lazy `%`-formatting.

## Required

### 6. Wrong match column — `app/users.py:16`

The spec matches `display_name` case-insensitively; the query matches `email`.
The OpenSpec proposal reinforces "Match on display name, not email." This is a
correctness failure independent of the injection, and it makes the endpoint
useless for its stated purpose.

### 7. Pagination and ordering are absent — `app/users.py:14-19`

`limit`, `cursor`, and `next_cursor` are ignored. Probed `?limit=500`: the
handler builds a match-all query with no `LIMIT`. Standards #5 and the spec
require default 20, max 50, stable `display_name ASC, id ASC` order, and an
opaque cursor. An empty `q` degenerates to `LIKE '%%'` — the whole table. This
is unbounded fetching (memory/timeout risk) and, combined with finding 3, a
bulk cross-tenant export.

### 8. Empty/whitespace `q` accepted — `app/users.py:14`

`q = request.args.get("q", "")` defaults to empty and is never validated.
Spec and the "Empty query rejected" requirement: 422. Today `q=` or `q=%20`
returns every row, so validation is also what closes the match-all path.

### 9. Bespoke query duplicates the canonical helper — `app/users.py:15`

`Database.find_users(tenant_id, q, limit, cursor)` exists precisely for this
feature (`app/db.py:8`). The change writes a near-duplicate that re-implements
(incorrectly) tenant scope, ordering, and paging. Standards #6 requires reusing
the helper. This is also the structural remedy: delete the raw query rather
than patching it, and the auth/tenant/pagination concerns move to one place.

### 10. Tests encode the defect and verify nothing — `tests/test_users.py:22-46`

`FakeDB.query` ignores `sql` and returns a hard-coded row, then
`test_returns_matches` asserts the response *includes* `email`. Consequences,
confirmed by mutation probes in the isolated copy:

| Probe | Expected if tests were meaningful | Actual |
|---|---|---|
| Replace the SQL with `SELECT 1 FROM users WHERE 1=0` | fail | **passes** — query text and params never asserted |
| Drop `email` from the response (spec-compliant shape) | pass | **fails** — test asserts the leak |
| Strip tenant/auth/limit handling | fail | **passes** — none is exercised |

The suite is green (`Ran 2 tests ... OK`) but would not catch a regression in
any requirement this change adds. The test asserts current output, not behavior.
Missing cases: unauthenticated access raises `AuthError`; only caller-tenant
rows returned; `email` absent; `q=""`/`"  "` → 422; `limit=500` capped at 50;
`next_cursor` and stable order; `q` containing `'` is parameterized. The fake DB
should record `(sql, params)` and return tenant-scoped rows so the query can be
asserted.

### 11. OpenSpec change is not implemented and not reflected

`openspec/changes/add-user-search/tasks.md` leaves both tasks unchecked, and
the proposal ("Match on display name, not email", pagination) contradicts the
code. Either the tasks are stale or the change is being claimed complete while
unimplemented; neither is mergeable. If this is a partial slice, say so in the
description and do not ship the endpoint enabled.

## Optional / Nit

- **Performance (leading wildcard):** `LIKE '%q%'` cannot use a B-tree index and
  forces a scan of every tenant's users. Once tenant-scoped and paginated, this
  still needs a trigram/full-text index or a documented measurement; do not add
  a plain index and call it done.
- **Change description:** the commit subject is fine; add a body naming the
  endpoint, the spec link, and the verification performed. There is no
  verification story here beyond unit tests that assert the wrong shape.
- **Audit logging:** besides removing PII, consider logging a security event
  (who, count, request ID) rather than free-form text, so log forging and
  PII leakage cannot recur.

## Verification performed

- `python3 -m unittest discover -s tests` — 2 tests pass. Passing here is not
  evidence of correctness: the tests assert the spec-violating shape.
- Mutation probes in `/tmp/opencode/cr-compare/iso-addyplus-2` (isolated copy,
  restored after each): SQL→`WHERE 1=0` stayed green; spec-compliant response
  shape went red; injection probe emitted interpolated SQL with empty params;
  unauthenticated call reached the query before the audit `AttributeError`.
- `git diff main...feature/user-search`: 98 insertions across handler, spec,
  OpenSpec proposal/spec/tasks, and tests. No secrets, no dependency changes.

## Bottom line

The shape of the fix is not in question: decorate with `@require_auth`, call
`db.find_users(request.user.tenant_id, q, limit=limit, cursor=cursor)`, validate
and bound `limit`, reject blank `q` with 422, project the response to
`{id, display_name}` plus `next_cursor`, and log a count instead of PII. Then
rewrite the tests so each spec requirement has a failing-first case. Approving
this as-is would ship a cross-tenant data leak behind an injectable query.
