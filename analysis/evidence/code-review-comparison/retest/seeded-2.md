# Code review: `feature/user-search` (retest, seeded-2)

## Scope

- Repository: `/tmp/opencode/cr-retest/review-seeded-2`
- Fixed point: `main` @ `9180825` (`baseline: user profile endpoint`). Reviewed `HEAD` `441fab2` (`add user search endpoint`), one commit.
- Diff: 6 files, +98/-1. Non-empty and read in full.
- Working tree: no tracked modifications; only pre-existing untracked `app/__pycache__/`, `tests/__pycache__/`.
- Spec sources: `docs/specs/user-search.md`, `openspec/changes/add-user-search/{proposal.md,tasks.md,specs/users/spec.md}`. No originating issue supplied; `openspec/specs/` holds no baseline specs, so the delta and prose spec are the only spec sources.
- Standards sources: `CODING_STANDARDS.md` (seven binding rules) and `AGENTS.md`.
- Isolation copy: `/tmp/opencode/cr-retest/iso-seeded-2`, created with `git archive HEAD` and cleaned after the probe.

## Verification

| Command | Outcome |
|---|---|
| `python3 -m unittest discover -s tests -v` (review checkout) | 2 tests, OK |
| `python3 -m unittest tests.test_users.SearchUsersTest -v` (isolation baseline) | 1 test, OK |
| Same focused test after mutation | 1 test, **OK — mutation survived** |
| `python3 -m py_compile app/*.py tests/*.py` | OK |
| Build / type-check / lint | Not configured: no `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, or `Makefile`; no lint/type tools installed |

The suite is hermetic (in-process `unittest`, no network). Probe: in the isolation copy the match boundary in `app/users.py:16` was changed from `email LIKE '%{q}%'` to `email = '{q}'` (substring to exact match). The focused search test still passed because `FakeDB.query` ignores its `sql`/`params` arguments and returns a canned row. Recorded as a Required test-quality finding (Q5). No tracked file in the review checkout changed.

## Spec axis — changes required

Worst issue: the endpoint implements almost none of the approved behavior, and the test asserts the violations as expected output.

- **Critical — S1. No authentication.** `app/users.py:13` `def search_users(...)` lacks `@require_auth`; `get_user` at line 5 has it. Prose spec: "Authentication is required." The fail-closed `AuthError` in `app/auth.py` never fires for search.
- **Critical — S2. No tenant scoping.** `app/users.py:15-17` has no `tenant_id` predicate and never reads `request.user.tenant_id`. Spec: "Results are limited to the caller's tenant." Delta: "SHALL return only users in the caller's tenant." Every tenant's rows are visible.
- **Critical — S3. Wrong match column.** `app/users.py:16` matches `email LIKE`, not `display_name`. Spec: "`q` matches `display_name` case-insensitively"; proposal: "Match on display name, not email."
- **Critical — S4. Email is returned.** The select list includes `email`, and line 19 returns rows verbatim. Spec: "Return `id` and `display_name` only. Never return `email`." Delta: "The response SHALL contain `id` and `display_name` only."
- **Critical — S5. Pagination absent.** `app/users.py:14-19` reads no `limit` or `cursor`, caps nothing, and returns no `next_cursor`. Spec: limit default 20, maximum 50, opaque cursor. Delta scenario: "**WHEN** a caller requests `limit=500` **THEN** the service rejects the request or caps the page at 50."
- **Required — S6. Empty query accepted.** `app/users.py:14` defaults `q` to `""` and returns an unfiltered listing; no 422. Spec and delta: "**WHEN** a caller sends `q=` **THEN** the response is 422."
- **Required — S7. No stable ordering.** No `ORDER BY`. Spec: "Order by `display_name ASC, id ASC`." Cursor pagination without a stable order is not reproducible.

## Standards axis — changes required

Worst issue: rules 1-4 are violated directly, and the SQL construction is an injection site.

- **Critical — ST1. Rule 1 (Authentication).** "Every route handler must be wrapped in `@require_auth`." `app/users.py:13` is not. Same defect as S1.
- **Critical — ST2. Rule 2 (Tenant scope).** "Every data access must be scoped to `request.user.tenant_id`. Never return another tenant's rows." `app/users.py:15-17` has no scope. Same defect as S2.
- **Critical — ST3. Rule 3 (SQL).** "Use `Database.find_users` or parameterized `Database.query(sql, params)`. Never build SQL with f-strings, `%`, or string concatenation." `app/users.py:16` interpolates `q` into an f-string. Same defect as Q1.
- **Critical — ST4. Rule 4 (PII).** "Never log email addresses, display names, or raw query text." `app/users.py:18` logs both the caller's email and raw `q`: `f"search by {request.user.email}: {q}"`. Same defect as Q3.
- **Critical — ST5. Rule 5 (List endpoints).** No `limit` (default 20, max 50), no cursor, no `next_cursor`; the result set is unbounded. Same defect as S5.
- **Required — ST6. Rule 6 (Canonical helpers).** `Database.find_users(tenant_id, q, limit=20, cursor=None)` exists at `app/db.py:8`, documented "Return tenant-scoped users matching q with a stable page order", yet `search_users` re-implements query logic. Fix: call `db.find_users(request.user.tenant_id, q, limit, cursor)`.
- **Critical — ST7. Rule 7 (Response fields).** Responses carry `email`. Same defect as S4.

## Quality axis — changes required

Worst issue: SQL injection combined with a cross-tenant read.

- **Critical — Q1. SQL injection (Injection).** `app/users.py:16`: `f"... WHERE email LIKE '%{q}%'"`. Input such as `q=' OR '1'='1` rewrites the predicate; there is no parameter binding and no escaping of `%`/`_` (Input boundary). Fix: `db.find_users(...)` with bound parameters and escaped wildcards.
- **Critical — Q2. Missing authorization (Authorization).** The handler checks no owner or tenant scope; the read is a tenant-wide IDOR. Same defect as S2/ST2.
- **Critical — Q3. PII exposure (PII).** `app/users.py:16,18,19`: email is selected, logged alongside raw query text, and returned. Triggers the PII check for logs and response bodies. Fix: select `id, display_name`; log a count and request ID only.
- **Required — Q4. Unbounded work / no index (Unbounded work, Index use).** No `LIMIT`, and a leading-wildcard `LIKE '%q%'` cannot use an index; each request scans and serializes the full `users` table across all tenants. Fix: use the bounded `find_users` page and justify any index with `EXPLAIN` before and after.
- **Required — Q5. Tests encode the defects and cannot catch regressions.** `tests/test_users.py:32-46` asserts that `email` is returned and asserts nothing about tenant scoping, empty-query 422, limit/cursor, or ordering. `FakeDB.query` (line 22) ignores `sql`/`params`, so the probe mutation survived. Fix direction: fake `find_users`, assert parameterized SQL, assert `email` is absent, and add tenant, limit, cursor, and empty-query cases; each must fail against its mutation.
- **Required — Q6. Missing input validation (Input boundary).** `q` is neither trimmed nor checked for emptiness or length, and `limit`/`cursor` are not parsed or clamped. Fix: reject blank `q` with 422 and clamp `limit` to 1..50.
- **Optional — Q7. Error path.** With no authenticated user, line 18 raises `AttributeError` on `request.user.email` instead of `AuthError`, and only after the query runs. Restoring the decorator makes auth fail before data access.
- **FYI — Q8. Route registration unverified.** The fixture has no router or framework entry point; review is handler-level only, so the `GET /users/search` mapping itself could not be checked.

## Artifact findings

- **Required — A1. Delta omits two prose requirements.** `docs/specs/user-search.md` states "Authentication is required" and "Order by `display_name ASC, id ASC`"; `openspec/changes/add-user-search/specs/users/spec.md` has neither an authentication nor an ordering requirement. Per the skill, the omission is reported rather than silently resolved. Fix: add both requirements with scenarios so implementation and archive criteria agree.
- **FYI — A2. Tasks unchecked.** `tasks.md` leaves both boxes open, including "Add tests for tenant scoping, field selection, and pagination." That accurately reflects the incomplete work; no separate action.

## Verdict

- Spec: **changes required** — S1-S7; unauthenticated, cross-tenant, email-matching, email-returning, unpaginated, and empty queries accepted.
- Standards: **changes required** — rules 1-7 violated (ST1-ST7).
- Quality: **changes required** — SQL injection plus IDOR, PII exposure, unbounded scan, and tests that assert the defects (Q1-Q6).
- Artifacts: **changes required** — delta omits the auth and ordering requirements (A1).

```
verdict: needs_revision
reason: Code — search_users is unauthenticated, unscoped by tenant, injectable via f-string SQL, returns and logs email, and lacks required validation and pagination; the delta spec also omits two prose requirements.
```
