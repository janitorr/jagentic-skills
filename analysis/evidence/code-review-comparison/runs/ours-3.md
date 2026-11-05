# Code review: `feature/user-search` (`add-user-search`)

**Fixed point:** `main` = `d84de4d`; **HEAD** = `2f28cb0`
**Diff:** 6 files, +98/−1 (`app/users.py`, `docs/specs/user-search.md`, the
OpenSpec change, `tests/test_users.py`). No uncommitted tracked changes; only
untracked `__pycache__/` directories.
**Sources read:** `docs/specs/user-search.md`, `openspec/changes/add-user-search/`
(proposal, spec delta, tasks), `CODING_STANDARDS.md`, `AGENTS.md`, `app/`,
`tests/`.

## Spec

**S1 — Critical — searches email, not `display_name`.**
`app/users.py:16` filters `WHERE email LIKE '%{q}%'`. The spec requires matching
`display_name` case-insensitively (`docs/specs/user-search.md:6`; delta lines
7-8; proposal line 10). Impact: valid name searches miss, email contents become
a search oracle, and the core behavior is inverted. Fix: filter
`LOWER(display_name) LIKE LOWER(...)` via the canonical helper.

**S2 — Critical — `email` is returned.**
`app/users.py:16,19` selects `email` and returns `rows` unchanged. The spec and
delta require `id` and `display_name` only and explicitly forbid `email`
(`docs/specs/user-search.md:8`; delta lines 15-22; standard 7). Impact: PII
exposure in every response. Fix: select/project only the two allowed fields.

**S3 — Critical — no pagination or ordering.**
`app/users.py:13-19` ignores `limit` and `cursor`, returns an unbounded list, and
never returns `next_cursor`. Required by `docs/specs/user-search.md:9-10` and
delta lines 24-32 (also standard 5). Impact: a single request can dump the
tenant's user table. Fix: default `limit=20`, cap at 50, implement the opaque
cursor, order by `display_name ASC, id ASC`, and return `next_cursor`.

**S4 — Critical — empty query is not rejected.**
`app/users.py:14,16`: `q=""` becomes `LIKE '%%'`, returning every row with 200.
The spec requires 422 for empty/whitespace-only `q`
(`docs/specs/user-search.md:6-7`; delta lines 34-41). Impact: the search endpoint
becomes a full-list export. Fix: trim `q`, return 422 when empty or
whitespace-only.

**S5 — Required (artifacts) — task list and spec delta lag the code.**
`openspec/changes/add-user-search/tasks.md:3-4` still marks both tasks
unchecked even though a route and tests were added; task 4's required tests
(tenant scoping, field selection, pagination) do not exist. The delta also omits
the ordering rule present in `docs/specs/user-search.md:9-10`, so the approved
artifact does not constrain order. Fix: reconcile tasks/tests and add the
ordering requirement (or drop it from `docs/specs`), then mark tasks complete.

## Standards

**ST1 — Critical — standard 1 (authentication) violated.**
`app/users.py:13` has no `@require_auth`, unlike `get_user` at line 5. It reads
`request.user.email` at line 18, so an unauthenticated request raises
`AttributeError` instead of `AuthError`. Fix: decorate the handler.

**ST2 — Critical — standard 2 (tenant scope) violated.**
`app/users.py:15-17` has no `tenant_id` predicate; it calls the unscoped
`db.query`. Any tenant's users are visible. Fix: use
`request.user.tenant_id` through `Database.find_users`.

**ST3 — Critical — standard 3 (SQL construction) violated.**
`app/users.py:16` interpolates `q` into SQL with an f-string. Input such as
`' OR '1'='1` changes the query; `%`/`_` in `q` also silently broaden matching.
Impact: SQL injection and cross-tenant reads. Fix: parameterized
`Database.query(sql, params)` or the existing helper; escape wildcards.

**ST4 — Critical — standard 4 (PII in logs) violated.**
`app/users.py:18` logs the caller's email and the raw query text. This leaks PII
and permits log injection via newlines/control characters in `q`. Fix: log only
counts, IDs, and request IDs.

**ST5 — Required — standard 6 (canonical helper) violated.**
`app/db.py:8` already defines `find_users(tenant_id, q, limit=20, cursor=None)`
as the tenant-scoped, ordered, paginated seam. `search_users` bypasses it with a
raw query, duplicating logic and losing tenant/order/pagination guarantees.
Fix: call `find_users`; extend it in its own change only if it is insufficient.

Standards 5 and 7 are also violated by S3 and S2 respectively; those are
reported once, under Spec, to avoid duplicate findings.

## Quality

**Q1 — Required — the tests enshrine the defects and cannot catch regressions.**
`tests/test_users.py:33-46` asserts that `email` is returned, the opposite of
the spec. `FakeDB.query` (lines 22-23) ignores both `sql` and `params` and
returns a canned row, so no test observes query construction, tenant scoping,
field projection, or pagination. Probe evidence (isolated copy):

- **Mutation A (survived):** changed `email LIKE` to `display_name LIKE`; the
  focused suite still passed (`Ran 2 tests ... OK`). A wrong match column is
  invisible to the tests.
- **Mutation B (correct behavior rejected):** projected only `id` and
  `display_name`; the suite failed because the test requires `email`.

This is a Required test-quality defect: the suite is green precisely because it
encodes the vulnerable behavior. Fix: make the fake record/validate SQL and
parameters (or use a real in-memory DB), assert only allowed fields, and add
cases for two tenants, display-name matching/case folding, empty/whitespace `q`
→ 422, `limit=500` cap, and cursor/`next_cursor`.

**Q2 — Required — no authentication test.**
Because S1 leaves the handler unwrapped, the test invokes it directly with a
`FakeUser` and never asserts `AuthError` when `request.user` is absent. Add that
case after applying `@require_auth`.

**Q3 — FYI — route wiring unverified.**
The fixture has no router or application entry point, so there is nothing to
check that `search_users` is registered at `GET /users/search`. Only the handler
was reviewed.

## Verification

| Command | Result |
|---|---|
| `git rev-parse main` / `HEAD` | `d84de4d` / `2f28cb0`; diff non-empty |
| `python3 -m unittest discover -s tests -v` | 2 tests, OK (but asserts S2) |
| Mutation probe A/B in `/tmp/opencode/cr-compare/iso-ours-3` | A survived; B failed (see Q1) |
| Build, lint, type check | No documented command or config in repo; **unverified** |

The review checkout's tracked files are unchanged; the isolation copy was
removed after the probes.

## Verdict

- **Spec:** changes required — worst: email is matched and returned, and the
  endpoint is unbounded/unauthenticated.
- **Standards:** changes required — worst: missing auth and tenant scoping, plus
  f-string SQL injection and PII logging.
- **Quality:** changes required — worst: tests assert the insecure behavior and
  a spec-correct field projection fails them.

**Overall gate: needs_revision** — defects are in **code** (the OpenSpec tasks
and delta also need artifact cleanup per S5). Do not start a repair pass in this
review turn.
