# Code review — `feature/user-search` (clean-3)

- Repository: `/tmp/opencode/cr-retest/review-clean-3`
- Fixed point: `main` = `2bc6fb5` (`git rev-parse main`)
- Head: `fa03a27` ("add user search endpoint")
- Diff: `git diff main...HEAD` — 6 files, +206/-2; non-empty
- Working tree: `git status --porcelain` shows only untracked `app/__pycache__/` and
  `tests/__pycache__/`. No tracked file changed; `git diff --stat` is empty.
- Sources read: `docs/specs/user-search.md`; OpenSpec `add-user-search`
  (`proposal.md`, `specs/users/spec.md`, `tasks.md`); `CODING_STANDARDS.md`;
  `AGENTS.md`; touched code and tests.

## Verification

| Command | Outcome |
|---|---|
| `python3 -m unittest discover -s tests -v` | 10 tests, **OK** |
| `python3 -m py_compile app/*.py tests/test_users.py` | **OK** |
| build / lint / type check | none configured in the repo |

Mutation probes were run in an isolated clone at
`/tmp/opencode/cr-retest/iso-clean-3` (checked out at `fa03a27`):

1. Boundary: changed `if limit < 1 or limit > 50:` to `if limit < 0 ...` in
   `app/users.py:23`; focused `test_limit_below_min_is_rejected` **FAILED**
   (`limit=0` was accepted). Mutation killed.
2. Tenant scope: replaced `request.user.tenant_id` with `"tenant-b"` at
   `app/users.py:28`; focused `test_scopes_tenant_and_paginates` **FAILED**
   (`db.calls` showed `tenant-b`). Mutation killed.

The isolated copy was left only with test-run caches; the review checkout has no
tracked changes.

## Spec

Cross-check of the prose spec and the OpenSpec delta: the two agree on auth,
tenant scope, case-insensitive display-name matching, field allowlist ("Never
return `email`"), limit default/max, opaque cursor, 422 on empty `q`, and order
`display_name ASC, id ASC`. No requirement appears in one source and is omitted
from the other.

| Requirement | Evidence | Result |
|---|---|---|
| Auth required, rejected before data access | `@require_auth` at `app/users.py:13`; `test_anonymous_is_rejected` asserts `AuthError` and `db.calls == []` | Met |
| Tenant scoping | `request.user.tenant_id` passed at `app/users.py:28`; asserted in `test_scopes_tenant_and_paginates` | Met |
| Match display name, case-insensitive | `q` stripped (`app/users.py:15`) and delegated to `db.find_users` | Delegated |
| Empty/whitespace `q` → 422 | `app/users.py:16-17`; `test_empty_query_is_rejected` | Met |
| Only `id` and `display_name` returned | `app/users.py:34-39`; exact-dict assertion despite FakeDB row containing `email` (`tests/test_users.py:29-32,47-53`) | Met |
| `limit` default 20, max 50 | `app/users.py:19-24`; boundary tests at 0, 1, 50, 51, non-integer | Met |
| Opaque `cursor` in, `next_cursor` out | `app/users.py:26-29,38`; passed through unchanged | Met |
| Stable ordering `display_name ASC, id ASC` | Not exercised: `Database.find_users` is abstract (`app/db.py:8-10`) and `FakeDB.find_users` returns a fixed row | **Delegated, unverified** |

**Optional (Spec coverage) — stable ordering and matching are not tested.**
`docs/specs/user-search.md:9-10` and the OpenSpec "Stable ordering" requirement
say order is deterministic, but no test asserts order and the fake DB cannot
prove it. The tasks file only claims tests for "tenant scoping, field selection,
and pagination". Impact: a regression in `find_users` ordering or case
sensitivity would pass this suite. Fix: add a test at the DB seam that returns
rows in an unstable order and asserts the endpoint/DB contract yields
`display_name ASC, id ASC`, or record ordering as a DB-implementation task.

**FYI — route wiring is not in the diff.** The spec names
`GET /users/search`, but the repo has no router/registration; only the handler
function exists. Path and verb cannot be verified from this change.

## Standards

All seven `CODING_STANDARDS.md` rules are satisfied:

1. Authentication — `@require_auth` at `app/users.py:13`, fail-closed.
2. Tenant scope — `request.user.tenant_id` at `app/users.py:28`.
3. SQL — no SQL built in the handler; it calls `Database.find_users`
   (`app/users.py:27-29`), satisfying the canonical-helper rule too.
4. PII — the audit record logs only `count` and `request_id`
   (`app/users.py:30-33`); no email, display name, or raw `q`.
5. List endpoints — limit default 20, max 50, opaque cursor, `next_cursor`
   (`app/users.py:19-29,38`).
6. Canonical helpers — reuses `find_users` rather than duplicating query logic.
7. Response fields — only `id` and `display_name` (`app/users.py:35-37`).

No Standards findings.

## Quality

**Optional (Injection — log injection).** `app/users.py:32` logs
`getattr(request, "request_id", "-")` without sanitizing control characters. In
the isolated copy, a request_id of `"abc\nINFO:audit:user_search count=999"` with
a formatter that prints the field produced a second, forged log line. Impact:
audit-log forging or truncation if `request_id` is copied from a client header
by middleware. Fix: constrain `request_id` to a safe character set (or strip
`\r\n` and control chars) before logging; add a test that sets the
`request.request_id` attribute (not `args`) to `"x\nforged"` and asserts one
record.

The existing `test_logs_do_not_contain_pii` (`tests/test_users.py:94-115`)
places the hostile `request_id` inside `args` (`:98`) rather than on the request
attribute, and then asserts the attribute default `"req-1"` (`:105`). It is
therefore effective at proving query args are not logged, but it does not
exercise the attribute path above. This is the reason the finding is Optional,
not Required: the unguarded input is plausibly middleware-owned.

**Optional (Input boundary — length).** `q` has no maximum length
(`app/users.py:15`); an arbitrarily large query string is forwarded to the
search helper. Impact: an expensive `contains` search or memory amplification
once `find_users` is implemented. Fix: cap `q` (for example 100 characters) and
return 422.

**FYI (Index use).** The spec's "contains" semantics imply a leading-wildcard
`LIKE`; `Database.find_users` is abstract (`app/db.py:8-10`), so no query plan
exists to inspect. When implemented, capture `EXPLAIN` before/after and avoid a
full tenant scan. Not a defect in this diff.

Positive checks: pagination is bounded (no unbounded result set), no N+1 or
remote call in a loop, authentication fails closed before `db.find_users`, and
field selection is enforced by construction rather than by trusting row keys.
The tenant-scope and limit-boundary mutation probes both failed the focused
tests, so the suite is not merely decorative at those seams.

## Axis verdicts

- **Spec: pass** — every stated requirement is implemented; worst issue is
  Optional (ordering/matching unverified at the abstract DB seam).
- **Standards: pass** — all seven documented rules met.
- **Quality: pass** — worst issue is Optional (unsanitized `request_id` in the
  audit log; no Critical or Required defect).

```
verdict: pass
reason: No Critical or Required findings; optional hardening is request_id sanitization, a q length cap, and DB-seam ordering/matching coverage.
```
