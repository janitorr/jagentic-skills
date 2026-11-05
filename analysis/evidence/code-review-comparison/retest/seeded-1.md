# Code review: `feature/user-search` — retest, seeded-1

## Scope

- Repository: `/tmp/opencode/cr-retest/review-seeded-1`
- Fixed point: `main` @ `9180825` (`baseline: user profile endpoint`); reviewed `HEAD` `441fab2` (`add user search endpoint`), one commit.
- Diff: 6 files, +98/−1. Non-empty and fully reviewed.
- Working tree: no tracked modifications; only untracked `app/__pycache__/` and `tests/__pycache__/` (test-run artifacts).
- Spec sources: `docs/specs/user-search.md`, `openspec/changes/add-user-search/{proposal.md,tasks.md,specs/users/spec.md}`. No originating issue supplied. `openspec validate add-user-search` → valid.
- Standards sources: `CODING_STANDARDS.md` (seven binding rules) and `AGENTS.md`.
- Probe copy: `/tmp/opencode/cr-retest/iso-seeded-1/repo` (clone of `HEAD`), removed after use.

## Verification

| Command | Outcome |
|---|---|
| `python3 -m unittest discover -s tests -v` (review checkout) | 2 tests, **OK** |
| `python3 -m unittest tests.test_users.SearchUsersTest -v` (isolation, baseline) | 1 test, OK |
| Same focused test, mutation 1 | 1 test, **OK — mutation survived** |
| Same focused test, mutation 2 | 1 test, **OK — mutation survived** |
| Build / type-check / lint | Not configured (no `pyproject.toml`, `setup.cfg`, `tox.ini`, or `Makefile`) |

Suite is hermetic: in-process `unittest`, no network or external services. Probe 1 changed the `q` default boundary `""` → `"zzz"`; probe 2 removed the SQL `WHERE` clause entirely. Both survived because `FakeDB.query` (`tests/test_users.py:22-23`) ignores its `sql`/`params` arguments and returns a canned row. The tests are decorative with respect to the endpoint's behaviour.

## Spec axis — changes required

Worst issue: the endpoint implements almost none of the approved behaviour, and the test asserts the violations as expected output.

- **Critical — S1. No authentication.** `app/users.py:13` `def search_users(...)` lacks `@require_auth`, unlike `get_user` at line 5. Spec: "Authentication is required." Anonymous requests reach the query; `require_auth`'s fail-closed `AuthError` never fires.
- **Critical — S2. No tenant scoping.** `app/users.py:15-16` queries `users` with no `tenant_id` predicate. Spec: "Results are limited to the caller's tenant." Delta: "SHALL return only users in the caller's tenant." `request.user.tenant_id` is never read, so all tenants' rows are visible.
- **Critical — S3. Wrong column and case.** `app/users.py:16` matches `email LIKE`, not `display_name`, and does not enforce case-insensitivity. Spec: "`q` matches `display_name` case-insensitively"; proposal: "Match on display name, not email."
- **Critical — S4. Email returned.** The select list includes `email`, and `app/users.py:19` returns rows verbatim. Spec: "Return `id` and `display_name` only. Never return `email`." Delta: "The response SHALL contain `id` and `display_name` only."
- **Critical — S5. No pagination.** `app/users.py:14-19` reads no `limit` or `cursor`, applies no cap, and returns no `next_cursor`. Spec: default 20, max 50, opaque cursor. The result set is unbounded.
- **Critical — S6. Empty query accepted.** `app/users.py:14` defaults `q` to `""` and returns a full listing. Delta: "**WHEN** a caller sends `q=` **THEN** the response is 422."
- **Required — S7. No stable ordering.** No `ORDER BY`. Spec: "Order by `display_name ASC, id ASC`." Pagination without a stable order is not reproducible.

## Standards axis — changes required

Worst issue: rules 1-5 and 7 are violated directly; rule 3 is an injection site.

- **Critical — ST1. Rule 1 (Authentication).** "Every route handler must be wrapped in `@require_auth`." `app/users.py:13` is not. Same defect as S1.
- **Critical — ST2. Rule 2 (Tenant scope).** "Every data access must be scoped to `request.user.tenant_id`. Never return another tenant's rows." `app/users.py:15-16` has no scope. Same defect as S2.
- **Critical — ST3. Rule 3 (SQL).** "Never build SQL with f-strings, `%`, or string concatenation." `app/users.py:16` interpolates `q` into an f-string. Same defect as Q1.
- **Critical — ST4. Rule 4 (PII).** "Never log email addresses, display names, or raw query text." `app/users.py:18` logs the caller's email and the raw query: `f"search by {request.user.email}: {q}"`. Same defect as Q2.
- **Critical — ST5. Rule 5 (List endpoints).** No `limit` (default 20, max 50), cursor, or `next_cursor`; unbounded. Same defect as S5.
- **Required — ST6. Rule 6 (Canonical helpers).** `Database.find_users(tenant_id, q, limit=20, cursor=None)` already exists at `app/db.py:8` "with a stable page order" and is unused; `search_users` re-implements query logic instead. Fix: call `db.find_users(request.user.tenant_id, q, limit, cursor)`.
- **Critical — ST7. Rule 7 (Response fields).** Responses carry `email`. Same defect as S4.

## Quality axis — changes required

Worst issue: SQL injection combined with a cross-tenant read.

- **Critical — Q1. SQL injection (check: Injection).** `app/users.py:16`: `f"... WHERE email LIKE '%{q}%'"`. Input such as `q=' OR 1=1 --` rewrites the predicate; there is no parameter binding, and `%`/`_` are not escaped (also Input boundary). Fix: `db.find_users(...)` with bound parameters and escaped wildcards.
- **Critical — Q2. PII in logs and response (check: PII).** `app/users.py:16,18,19`: email is selected, logged alongside raw query text, and returned. Fix: select `id, display_name`; log a count or request ID only.
- **Critical — Q3. Missing authorization (check: Authorization).** The handler checks no owner or tenant scope; the read is a tenant-wide IDOR. Same defect as S2/ST2.
- **Critical — Q4. Unbounded work and no index (checks: Unbounded work, Index use).** No `LIMIT`; the leading-wildcard `LIKE '%q%'` cannot use an index, so each request scans and serializes the users table. Fix: bounded `find_users` page plus an index justified with `EXPLAIN` before and after.
- **Required — Q5. Tests encode the defects and cannot catch regressions.** `tests/test_users.py:32-46` asserts that `email` is returned, asserts no tenant scoping, and covers neither pagination, 422, ordering, nor limit. Both mutations survived. Fix: fake `find_users`, assert the SQL is parameterized and tenant-scoped, assert `email` is absent, add empty-query/limit/cursor/ordering cases, and ensure each fails against the mutations.
- **Required — Q6. Missing input validation (check: Input boundary).** `q` is neither trimmed nor checked for length; `limit`/`cursor` are not parsed or clamped. Fix: reject blank `q` with 422 and clamp `limit` to 1..50.
- **Optional — Q7. Error path.** With no authenticated user, `app/users.py:18` raises `AttributeError` on `request.user.email` instead of `AuthError`, and only after the query has run. Fix: restore the decorator so auth fails before data access.
- **FYI — Q8. Duplication.** The query shape duplicates what `Database.find_users` already promises; removing it is covered by ST6.

## Artifact findings

- **Required — A1. Delta omits two prose requirements.** `docs/specs/user-search.md` states "Authentication is required" and "Order by `display_name ASC, id ASC`"; the OpenSpec delta at `openspec/changes/add-user-search/specs/users/spec.md` contains neither an authentication nor an ordering requirement. Per the skill, the omission is reported rather than silently resolved. Fix: add both requirements with scenarios so implementation and archive criteria agree.
- **FYI — A2. Tasks unchecked.** `tasks.md` leaves both boxes open, including "Add tests for tenant scoping, field selection, and pagination." That accurately reflects the incomplete work.

## Verdict

- Spec: **changes required** — S1-S7; unauthenticated, cross-tenant, email-matching, email-returning, unpaginated, and accepts empty queries.
- Standards: **changes required** — rules 1-7 violated (ST1-ST7).
- Quality: **changes required** — SQL injection, IDOR, PII exposure, unbounded scan, and tests that assert the defects (Q1-Q6).
- Artifacts: **changes required** — delta omits the authentication and ordering requirements (A1).

```
verdict: needs_revision
reason: Code — search_users is unauthenticated, unscoped by tenant, injectable via f-string SQL, returns/logs email, and lacks required validation and pagination; the delta spec also omits two prose requirements.
```
