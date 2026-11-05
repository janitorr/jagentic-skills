# Code review: `feature/user-search` against `main`

**Fixed point:** `main` = `d84de4d`. **HEAD:** `2f28cb0` ("add user search endpoint").
Diff command: `git diff main...HEAD` (6 files, +98/-1). One commit on the branch.

**Spec sources:** `docs/specs/user-search.md`; OpenSpec change
`openspec/changes/add-user-search/` (`proposal.md`, `specs/users/spec.md`,
`tasks.md`).

**Standards sources:** `CODING_STANDARDS.md` (binding rules 1-7); `AGENTS.md`
(test command only, no style rules). The Fowler smell baseline was applied on
top; documented repo rules override it.

**Method note:** this harness exposes no sub-agent dispatch tool, so the two
axes were reviewed as separate passes in one context rather than parallel fresh
contexts. The test suite passes (2 tests). Behavioural probes ran only in
`/tmp/opencode/cr-compare/iso-matt-1` (untracked copy); no tracked files were
modified. The probes confirmed SQL injection, cross-tenant rows, email
exposure, unbounded results, PII in logs, and a missing auth decorator.

## Standards

### Documented-standard violations (hard)

1. **Rule 1, Authentication.** `app/users.py:13` `search_users` is not wrapped
   in `@require_auth`; only `get_user` is. Calling it with `request.user=None`
   raised `AttributeError` at the logging line, not `AuthError`.
2. **Rule 2, Tenant scope.** `app/users.py:15-17` has no `tenant_id` predicate
   and never reads `request.user.tenant_id`. A probe as a `tenant-a` caller
   returned `tenant-b`'s Bob. This is a cross-tenant data leak.
3. **Rule 3, SQL.** The query is built with an f-string:
   `f"SELECT ... WHERE email LIKE '%{q}%'"`. The rule forbids f-strings, `%`,
   and concatenation. Probe input `q="' OR '1'='1' --"` returned every row.
   Use `db.query(sql, params)` with bound parameters.
4. **Rule 4, PII.** `app/users.py:18` logs the caller's email and raw query
   text: `f"search by {request.user.email}: {q}"`. Probe output contained
   `agent@example.com` and each search term. The rule permits counts, IDs, and
   request IDs only.
5. **Rule 5, List endpoints.** No `limit`, `cursor`, or `next_cursor` handling.
   `limit=500` was ignored and the endpoint returned the full result set, which
   is unbounded.
6. **Rule 6, Canonical helpers.** `Database.find_users(tenant_id, q,
   limit=20, cursor=None)` exists at `app/db.py:8` specifically for this, and is
   unused. `search_users` re-implements the query instead.
7. **Rule 7, Response fields.** The `SELECT` includes `email`, and rows are
   returned raw. Probe responses contained `alice@example.com`; the spec allows
   `id` and `display_name` only.

### Test quality (judgement call, no documented test rule)

`tests/test_users.py:39-43` asserts the violating response shape, including
`"email": "alice@example.com"`, locking in the rule 7 breach. `FakeDB.query`
(`tests/test_users.py:22-23`) ignores the SQL and params and returns a constant
row, so the test cannot detect the missing tenant filter, the injection, or the
field projection. It passes while the endpoint breaks every checklist item.

### Smell baseline

**Duplicated Code:** the search query duplicates the intended `find_users`
behaviour. This is already a hard rule 6 breach, and the repo standard wins, so
no separate action. No other baseline smell rises above the documented rules;
there is no speculative abstraction to flag. **Feature Envy** (judgement): the
handler reaches into `request.user.email` solely to log it, but removing the
logging removes the envy.

## Spec

### (a) Requirements missing or partial

- *"Authentication is required."* Not enforced: no `@require_auth` on
  `search_users`; an unauthenticated caller crashes rather than receiving an
  auth error.
- *"Results are limited to the caller's tenant."* Not implemented: no tenant
  predicate or use of `request.user.tenant_id`.
- *"`q` matches `display_name` case-insensitively."* Wrong column: the query
  matches `email`. Probe: `q=Dana` (a display-name match) returned `[]`;
  `q=example.com` returned a user whose display name does not match.
- *"An empty or whitespace-only `q` returns 422."* Missing. Probe: `q=""`
  returned every row; `q="   "` returned `200` with `[]`.
- *"Return `id` and `display_name` only. Never return `email`."* Violated:
  `email` is selected and returned.
- *"`limit` defaults to 20 and must not exceed 50."* Missing: `limit` is never
  parsed; `limit=500` returned all rows.
- *"Order by `display_name ASC, id ASC`."* Missing: no `ORDER BY`.
- *"Return an opaque `next_cursor`."* Missing, along with the entire bounded
  pagination requirement.

### (b) Behaviour not asked for (scope creep)

- Matching on `email` is the opposite of the proposal's *"Match on display
  name, not email."*
- Returning `email` is explicitly excluded by both spec sources.
- Audit logging of the caller email and raw query is not requested and
  contradicts the repo's PII rule.

### (c) Implemented but wrong

- The single new test (`test_returns_matches`) asserts the email-bearing
  response and uses a fake DB that ignores the query. It passes while the
  endpoint violates every spec bullet, giving false confidence. There are no
  tests for 422, tenant scoping, field selection, ordering, limit, or cursor.
- `openspec/changes/add-user-search/tasks.md` is entirely unchecked
  (`openspec list` reports `0/2 tasks`), so the change does not claim
  completion. The handler is also not registered on any route; the repo has no
  router, so this is noted rather than counted as a defect.
- The OpenSpec delta omits the authentication and ordering requirements that
  `docs/specs/user-search.md` states. Both sources agree on tenant scope,
  allowed fields, pagination, and the 422, and the implementation fails those
  regardless.

## Summary

- **Standards:** 7 hard violations (rules 1-7) plus one test-quality
  judgement call. Worst: f-string SQL injection (rule 3), which also enables
  cross-tenant reads.
- **Spec:** 8 missing/partial requirements, 3 scope-creep behaviours, and
  broken/absent tests. Worst: the endpoint exposes other tenants' users and
  email addresses, the exact leak the spec exists to prevent.
