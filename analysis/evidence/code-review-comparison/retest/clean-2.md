# Code review — `add-user-search` (clean-2 retest)

- **Repository:** `/tmp/opencode/cr-retest/review-clean-2`
- **Branch:** `feature/user-search`
- **Fixed point:** `main` (`2bc6fb5`)
- **Reviewed HEAD:** `fa03a27` (`add user search endpoint`)
- **Diff:** 6 files, +206 / −2
- **Mode:** OpenSpec change review (`add-user-search`), read-only
- **Date:** 2026-11-06

## Spec

I cross-checked `docs/specs/user-search.md` against
`openspec/changes/add-user-search/specs/users/spec.md`. The two agree on
authentication, tenant scope, case-insensitive display-name matching, response
fields, pagination bounds, ordering, and the empty-query case. The proposal is a
summary and does not restate every requirement, but it contradicts neither
source. No requirement stated in one source is missing from the other.

| Requirement | Evidence | Result |
|---|---|---|
| Authentication required | `@require_auth` at `app/users.py:13`; anonymous test at `tests/test_users.py:88-92` asserts `AuthError` and no DB call | Implemented |
| Tenant-scoped search | `request.user.tenant_id` forwarded at `app/users.py:27-29`; asserted at `tests/test_users.py:54` | Implemented at this layer |
| Case-insensitive display-name match | `q` forwarded unchanged after stripping at `app/users.py:15,27-29` | Delegated to `Database.find_users` |
| Safe response fields | Projection builds only `id` and `display_name` at `app/users.py:34-38`; exact-dict assertion at `tests/test_users.py:47-53` | Implemented |
| Bounded pagination | Default 20 at `app/users.py:20`; maximum 50 at `app/users.py:23`; `cursor` forwarded and `next_cursor` returned at `app/users.py:26-38` | Implemented |
| Stable ordering (`display_name ASC, id ASC`) | Contract delegated to `Database.find_users` (`app/db.py:8-10`) | Delegated; see FYI |
| Empty query rejected | Strip plus 422 at `app/users.py:15-17`; test at `tests/test_users.py:84-86` | Implemented |

The extra `limit < 1` rejection is not in the prose spec, but it is a defensible
reading of a bounded list endpoint, is covered by a test, and does not conflict
with the delta. I do not treat it as unrequested behavior.

**FYI (Spec):** case-insensitive matching and stable ordering are SHALL
requirements, but both live in the delegated `Database.find_users` helper.
`app/db.py` is an abstract stub (`raise NotImplementedError`), so this diff can
verify only that the correct tenant, query, limit, and cursor cross the seam.
There is no contrary evidence, but the behavior remains unverified until a
concrete implementation lands. No action for this change.

**Spec verdict: pass.** No missing, partial, or incorrectly implemented
requirement is visible at the route layer.

## Standards

All seven rules in `CODING_STANDARDS.md` hold.

1. **Authentication** — `search_users` is wrapped in `@require_auth`
   (`app/users.py:13`); the decorator fails closed before the body runs
   (`app/auth.py:5-10`).
2. **Tenant scope** — the only data access passes
   `request.user.tenant_id` (`app/users.py:27-29`), and the test asserts the
   exact tenant argument (`tests/test_users.py:54`). No other tenant can be
   selected from request input.
3. **SQL** — no SQL is built in the route; query construction stays behind
   `Database.find_users`. No f-string, `%`, or concatenation exists in the diff.
4. **PII** — the audit event logs only `count` and `request_id`
   (`app/users.py:30-33`). The query, display names, and email are absent, and
   `test_logs_do_not_contain_pii` (`tests/test_users.py:94-115`) checks both
   forbidden keys and values.
5. **List endpoints** — default 20, maximum 50, opaque `cursor` forwarded, and
   `next_cursor` returned (`app/users.py:19-38`); bounds are tested at
   `tests/test_users.py:61-82`.
6. **Canonical helpers** — the handler calls the pre-existing
   `Database.find_users` rather than duplicating query logic (`app/db.py:8-10`).
7. **Response fields** — each row is rebuilt as `id` and `display_name` only
   (`app/users.py:34-38`), so a wider DB row cannot leak `email`.

No documented-rule violation found.

**Standards verdict: pass.**

## Quality

**Correctness and edge cases.** Validation is ordered correctly: auth guard,
then empty/whitespace `q`, then `limit` parsing and bounds, then the query. The
handler strips `q` before the emptiness check, so whitespace-only input is
rejected consistently. `int()` accepts the boundary values 1 and 50 and rejects
0, 51, and non-numeric input with 422. `cursor` is passed through opaquely and
`next_cursor` is echoed from the helper. No mutation of caller-owned state.

**Security** (`references/quality-checks.md`):
- *Injection* — no query text is constructed in the diff; no shell, template, or
  log interpolation of user input.
- *Authentication / authorization* — guard present; tenant scope is explicit.
- *Input boundary* — `q` presence and `limit` type/range are validated. `q`
  length is not capped, but no standard requires it and the value is never
  logged or concatenated.
- *PII* — only count and request ID are logged; response projection is
  allowlist-based.
- *Secrets, dependencies, destructive paths, SSRF* — not applicable; no new
  packages, filesystem writes, or outbound URLs.

**Performance.** The page is bounded at 50, so request work is bounded. There is
no query or remote call inside a loop (no N+1). The eventual `find_users`
implementation for a "contains" match will likely need a leading-wildcard
`LIKE`; per the *Index use* check that needs an `EXPLAIN` before and after, but
that code is not in this diff.

**Test quality.** Tests cover tenant forwarding, default and boundary limits,
invalid limits, empty query, anonymous rejection, exact response shape, and PII
logging. The exact-dict assertions would catch an extra field or wrong tenant.
The mutation probe below confirms the pagination bound and tenant scope are
genuinely asserted, not merely exercised.

**FYI (Quality):** the successful path has no test asserting that a `None`
`next_cursor` is returned on the last page; the fake always returns
`"next-page"`. This is minor and the value is a straight pass-through, so no
action is requested.

**Quality verdict: pass.**

## Verification

Suite is hermetic (stdlib `unittest`, fake DB, no network).

| Command | Result |
|---|---|
| `python3 -m unittest discover -s tests -v` | 10 tests, all pass |
| `python3 -m compileall -q app` | pass (no syntax errors) |
| Build / type / lint | not configured in this repo; unverified, no command to run |

**Mutation probe** (isolated copy at
`/tmp/opencode/cr-retest/iso-clean-2`, repo copied from reviewed HEAD):

1. Baseline focused test
   `python3 -m unittest tests.test_users.SearchUsersTest.test_limit_above_max_is_rejected`
   passed.
2. Changed the touched boundary at `app/users.py:23` from `limit > 50` to
   `limit > 51`. The focused test **failed**: `limit=51` returned the success
   dict instead of a 422.
3. Restored the bound, then changed the tenant argument at `app/users.py:28`
   to a fixed `"tenant-b"`. `test_scopes_tenant_and_paginates` **failed**,
   showing the tenant-scope assertion catches the regression.
4. Removed the isolated copy. The review checkout has no modified tracked files;
   `git status --porcelain` shows only the pre-existing untracked
   `app/__pycache__/` and `tests/__pycache__/` directories.

## Findings

| # | Axis | Severity | Finding | Action |
|---|---|---|---|---|
| 1 | Spec | FYI | Matching case-insensitivity and page ordering are delegated to the abstract `Database.find_users`; unverifiable from this diff | None for this change |
| 2 | Quality | FYI | No test for a `None` `next_cursor` on the last page | Optional test hardening |

No **Critical**, **Required**, or **Optional** findings. Both FYIs are context,
not defects.

## Axis verdicts

| Axis | Verdict | Worst issue |
|---|---|---|
| Spec | pass | Delegated matching/ordering seam (FYI) |
| Standards | pass | None |
| Quality | pass | Missing last-page cursor test (FYI) |

```
verdict: pass
reason: no Critical or Required defects; the handler implements the prose spec and OpenSpec delta, follows all seven coding standards, and the green suite kills tenant-scope and limit-bound mutations.
```
