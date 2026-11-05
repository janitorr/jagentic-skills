# Code review: `feature/user-search`

**Fixed point:** `main` (`d84de4d`). Diff: `git diff main...HEAD`; commits: `2f28cb0 add user search endpoint`.
**Tests:** `python3 -m unittest discover -s tests` passes (2 tests). Green tests do not mean conformance here: the single new test asserts the non-conformant response.

**Process note:** This harness provides no sub-agent tool, so I could not run the two axes in fresh parallel contexts as the skill prescribes. I ran each axis separately against its own brief and kept the findings unmerged. Probe experiments ran only in `/tmp/opencode/cr-compare/iso-matt-2`.

## Standards

Sources: `CODING_STANDARDS.md` (binding rules 1-7) and `AGENTS.md` (test command only). The Fowler smell baseline was applied; documented repo rules override it.

### Hard violations

1. **Authentication, rule 1.** "Every route handler must be wrapped in `@require_auth`." `search_users` at `app/users.py:13` has no decorator:
   ```python
   def search_users(request, db):
   ```
   Probe: calling it with `request.user = None` raises `AttributeError`, not `AuthError`, so the route is not protected by the auth contract.

2. **Tenant scope, rule 2.** "Every data access must be scoped to `request.user.tenant_id`. Never return another tenant's rows." The query at `app/users.py:15-17` filters only on email; no `tenant_id` appears:
   ```python
   f"SELECT id, email, display_name FROM users WHERE email LIKE '%{q}%'"
   ```
   Probe confirmed the emitted SQL has no tenant predicate.

3. **SQL construction, rule 3.** "Never build SQL with f-strings, `%`, or string concatenation." The same line interpolates `q` into the statement. Probe with `q = "a' OR '1'='1"` produced:
   ```sql
   SELECT id, email, display_name FROM users WHERE email LIKE '%a' OR '1'='1%'
   ```
   `params` is empty. This is SQL injection.

4. **PII logging, rule 4.** "Never log email addresses, display names, or raw query text." `app/users.py:18` logs both the caller's email and the raw search string:
   ```python
   audit_log.info(f"search by {request.user.email}: {q}")
   ```
   Exactly the data the rule forbids.

5. **List endpoint contract, rule 5.** "Accept `limit` (default 20, maximum 50) and an opaque `cursor`; return `next_cursor`. No unbounded result sets." `search_users` ignores `limit` and `cursor` and returns `{"users": rows}` with no `next_cursor`. Probe with `limit=500&cursor=x` returned the full canned page and unchanged SQL.

6. **Canonical helpers, rule 6.** "Reuse existing helpers instead of duplicating query logic." `Database.find_users(tenant_id, q, limit=20, cursor=None)` already exists at `app/db.py:8` with the exact signature this endpoint needs. The change bypasses it and reimplements a query in the handler.

7. **Response fields, rule 7.** "Return only the fields the spec allows." `SELECT id, email, display_name` returns `email` directly to the caller. The new test at `tests/test_users.py:41` asserts `email` is present, encoding the violation.

### Judgement calls / smells

- **Possible Feature Envy** (`app/users.py:15-17`): the handler knows the `users` table, column list, and filter semantics, which belong behind `Database.find_users`. This overlaps rule 6 but stands as a design smell: query logic lives away from the data it manipulates.
- **Test double hides the defects** (`tests/test_users.py:20-21`): `FakeDB.query` returns a canned row and ignores `params`, so the test cannot observe parameterization, tenant scoping, field selection, filtering, or pagination. The test only proves the handler returns whatever the double returns.
- No further baseline smell (duplicated code, repeated switches, shotgun surgery, middle man, etc.) rises above noise in a 10-line handler.

## Spec

Sources: `docs/specs/user-search.md` and `openspec/changes/add-user-search/` (`proposal.md`, `specs/users/spec.md`, `tasks.md`). The two spec sources agree: `GET /users/search`, authenticated, tenant-scoped, case-insensitive `display_name` match, `id` and `display_name` only, bounded pagination, 422 for empty `q`.

### Missing or partial requirements

- **Authentication required** (`docs/specs/user-search.md:5`): not implemented; no `@require_auth`.
- **"Results are limited to the caller's tenant"** (`docs/specs/user-search.md:5`): not implemented; no tenant filter.
- **"`q` matches `display_name` case-insensitively"** (`docs/specs/user-search.md:6-7`): not implemented; the predicate is `email LIKE`. Case-insensitivity is incidental to the database, not expressed in the query.
- **"An empty or whitespace-only `q` returns 422"** (`docs/specs/user-search.md:7-8`; OpenSpec "Empty query rejected"): not implemented. Probe with `q="   "` returned a normal 200-shaped page.
- **"`limit` defaults to 20 and must not exceed 50"** (`docs/specs/user-search.md:9-10`; OpenSpec "Bounded pagination"): `limit` is read nowhere. The client's `limit=500` was silently ignored.
- **"Return an opaque `next_cursor`"** (`docs/specs/user-search.md:10`): absent from both query and response.
- **"Order by `display_name ASC, id ASC`"** (`docs/specs/user-search.md:9-10`): absent; ordering is whatever the database returns.
- **Route surface** (`GET /users/search`): there is no route registration anywhere in the fixture, so I cannot verify the endpoint is wired. The handler is the only added surface; treat routing as unproven, not as a finding.
- **Tests required by `tasks.md`**: the task list asks for "tests for tenant scoping, field selection, and pagination". Only one happy-path test exists, and it asserts the opposite of the field-selection requirement. Both tasks remain unchecked (`- [ ]`), inconsistent with presenting the change as complete.

### Scope creep

- **Audit logging** (`app/users.py:18`) was not requested by the spec or proposal. It is also the rule 4 violation above. Unrequested behaviour that leaks PII is the costliest kind of creep.
- The test's assertion of an `email` field is not just missing coverage; it introduces an expectation the spec explicitly forbids ("Never return `email`").

### Implemented but wrong

- **Wrong match field:** the spec says search by display name (`docs/specs/user-search.md:6`; OpenSpec "Match within tenant"), the code searches `email`. The visible response happens to contain display names, but the match logic is the wrong column.
- **Forbidden field exposed:** the spec says "Return `id` and `display_name` only. Never return `email`" (`docs/specs/user-search.md:8`; OpenSpec "Safe response fields"). The handler selects and returns `email`, and the test confirms it.
- **Response shape:** returning `{"users": rows}` satisfies neither the bounded-pagination contract nor the promised `next_cursor`; the endpoint is structurally an unbounded list.

## Summary

**Standards:** 7 hard documented-standard violations plus 2 judgement calls; worst is an unauthenticated, cross-tenant, SQL-injectable endpoint that returns PII.
**Spec:** 8 missing/partial requirements, 1 scope-creep item, and 2 wrong implementations; worst is that the core privacy requirement is inverted: email is both the search key and a response field.
