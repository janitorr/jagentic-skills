# Code review — `feature/user-search` vs `main`

- **Change:** `add-user-search` (OpenSpec), issue-less fixture.
- **Fixed point:** `main` = `d84de4d`. **HEAD:** `2f28cb0`.
- **Diff:** 6 files, +98/−1. Working tree clean apart from untracked `__pycache__/`.
- **Sources read:** `docs/specs/user-search.md`, `openspec/changes/add-user-search/{proposal.md,specs/users/spec.md,tasks.md}`, `CODING_STANDARDS.md`, `AGENTS.md`, `app/*.py`, `tests/test_users.py`.
- `openspec validate add-user-search --strict` → valid.

## Spec

**Critical — Tenant scope missing.** `app/users.py:15-17`. The query has no
tenant predicate and rows are returned unmodified. This contradicts the spec
line "Results are limited to the caller's tenant" and the requirement
"Tenant-scoped user search". Impact: a caller can read every tenant's users.
Fix: route through `db.find_users(request.user.tenant_id, q, limit, cursor)`.

**Critical — `email` returned.** `app/users.py:16,19`. `SELECT id, email,
display_name` is serialized wholesale. The spec says "Return `id` and
`display_name` only. Never return `email`." Impact: PII disclosure that the
change exists to prevent. Fix: project only the two allowed fields.

**Critical — No authentication.** `app/users.py:13`. `search_users` lacks
`@require_auth`, unlike `get_user` at line 5. The spec requires authentication;
`CODING_STANDARDS.md` §1 makes the decorator mandatory. Because line 18 reads
`request.user.email`, an unauthenticated call raises `AttributeError` rather
than failing cleanly. Fix: decorate the handler and test it.

**Required — Empty/whitespace `q` returns everything, not 422.**
`app/users.py:14`. `q` defaults to `""`, producing `LIKE '%%'`. Violates the
"Empty query rejected" requirement and turns the missing pagination into a
full-table read. Fix: strip and return 422 when empty.

**Required — Pagination absent.** `app/users.py:13-19`. No `limit` (default 20,
max 50), no `cursor`, no `next_cursor`, no `ORDER BY display_name ASC, id ASC`.
Violates "Bounded pagination", the docs spec, and standards §5. Impact:
unbounded result set. Fix: parse, clamp, and delegate to the helper.

**Required — Searches `email`, not `display_name`.** `app/users.py:16`
(`WHERE email LIKE`). The proposal says "Match on display name, not email."
Impact: wrong results plus PII matching. Fix: match `display_name`
case-insensitively.

## Standards

**Critical — SQL built by f-string.** `app/users.py:15-17`:
`f"SELECT ... WHERE email LIKE '%{q}%'"`. `CODING_STANDARDS.md` §3 explicitly
forbids f-strings, `%`, and concatenation. Impact: SQL injection; `q=' OR
'1'='1` or a `UNION SELECT` escapes the predicate. Fix: parameterized
`db.query(sql, (param,))` or the provided helper.

**Required — PII in the audit log.** `app/users.py:18` logs the caller's email
and the raw query. §4 says never log emails, display names, or raw query text;
log counts, IDs, and request IDs. Impact: PII in logs and attacker-controlled
text written to the audit stream. Fix: log the result count plus tenant/request
ID.

**Required — Canonical helper bypassed.** `app/db.py:8` already defines
`Database.find_users(tenant_id, q, limit=20, cursor=None)`; `app/users.py:15`
hand-rolls an inferior query instead. §6 requires reuse. Fix: call the helper.

Rule coverage for items reported under Spec: §1 → auth finding, §2 → tenant
finding, §5 → pagination finding, §7 → response-field finding.

## Quality

**Required — Mutation survived.** In `/tmp/opencode/cr-compare/iso-ours-2` I
changed the matching column `email` → `id` at `app/users.py:16`; the focused
`tests.test_users.SearchUsersTest` still passed. `FakeDB.query`
(`tests/test_users.py:22-23`) ignores SQL and parameters and returns one
hardcoded row, so the test cannot detect a wrong column, a missing tenant
predicate, or injection.

**Required — The test encodes the email leak.** Making the response
spec-compliant (projecting `id`/`display_name` only) makes the focused test
fail: `tests/test_users.py:39-44` asserts `email: alice@example.com`. The suite
therefore pins the violation, and a correct fix breaks the build. Fix: assert
only the allowed fields and assert the SQL/params the fake received.

**Required — Requirements untested.** No tests for tenant scoping,
authentication, empty-`q` 422, `limit` default/cap, cursor/`next_cursor`, or
ordering. `FakeDB` has no `find_users`, so the helper path the fix should use
cannot be exercised. Test quality is unverified for every requirement except a
hardcoded happy path.

**Optional — Artifact drift.** `tasks.md` leaves both boxes unchecked although
the code is committed, and no task covers the empty-query requirement. Mark
tasks with evidence (or leave unchecked and say the work is incomplete).

## Verification

| Command | Outcome |
|---|---|
| `git rev-parse main feature/user-search` | `d84de4d`, `2f28cb0` |
| `git diff main...HEAD` | non-empty, reviewed in full |
| `git status --porcelain` | only untracked `__pycache__/` |
| `python3 -m unittest discover -s tests -v` | 2 tests, OK |
| `openspec validate add-user-search --strict` | valid |
| Mutation: `email` → `id` match column | focused test **passed** (survived) |
| Probe: strip `email` from response | focused test **failed** (pins leak) |

The suite is hermetic (unittest with fakes, no network). No build, type, or lint
target exists (no `pyproject.toml`, `setup.cfg`, `tox.ini`, `Makefile`), so that
axis is **unverified — not configured**. The isolation copy was removed after
the probe; `git diff` in the review checkout is empty.

## Verdict

- **Spec: changes required.** Worst: cross-tenant reads and `email` exposure.
- **Standards: changes required.** Worst: f-string SQL injection.
- **Quality: changes required.** Worst: tests encode the violation and the
  mutation survived.

```
verdict: needs_revision
reason: user search is tenant-unsafe, unauthenticated, SQL-injectable, and returns email; defects are in code, with minor tasks.md artifact drift.
```

No code or artifacts were modified, and the change was not archived.
