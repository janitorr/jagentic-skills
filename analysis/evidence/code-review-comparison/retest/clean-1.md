# Code review: `add-user-search`

- Repository: `/tmp/opencode/cr-retest/review-clean-1` (read-only)
- Branch: `feature/user-search`
- Fixed point: `main` @ `2bc6fb5`; reviewed `HEAD` @ `fa03a27`
- Diff: 6 files, +206 / -2 (`git diff main...HEAD`)
- Change: OpenSpec `add-user-search`; prose spec `docs/specs/user-search.md`
- Workspace: clean apart from pre-existing untracked `__pycache__/`; no tracked
  file changed by this review.

## Sources loaded

- `openspec/changes/add-user-search/{proposal.md,specs/users/spec.md,tasks.md}`
- `docs/specs/user-search.md`
- `CODING_STANDARDS.md`, `AGENTS.md` (target repo)
- Touched code: `app/users.py`, `tests/test_users.py`; contracts in `app/db.py`,
  `app/auth.py`, `app/audit.py`
- `openspec validate add-user-search --strict` → valid

## Verification

| Command | Outcome |
|---|---|
| `python3 -m unittest discover -s tests` | 10 tests, OK (hermetic; fakes only) |
| `python3 -m py_compile app/*.py tests/*.py` | OK |
| `openspec validate add-user-search --strict` | valid |
| `git status --porcelain` / `git diff` | only untracked `__pycache__/`; no tracked diff |

No build or lint command is documented: `AGENTS.md` defines only the test
command, and no lint tool/config is present. Build is not applicable to this
Python fixture; lint is **unverified** (nothing configured).

Mutation probe ran in the designated copy
`/tmp/opencode/cr-retest/iso-clean-1` (clone of reviewed `HEAD`), then the copy
was emptied:

1. Boundary mutation `limit > 50` → `limit > 500` (`app/users.py:23`):
   `test_limit_above_max_is_rejected` **FAILED** (mutation killed).
2. Tenant mutation `request.user.tenant_id` → `"tenant-b"`
   (`app/users.py:28`): `test_scopes_tenant_and_paginates` **FAILED**
   (mutation killed).

## Spec

**Verdict: pass.**

Every delta requirement is implemented at the handler seam:

- Auth before data access: `@require_auth` (`app/users.py:13`) and
  `AuthError` on an anonymous caller; tested at `tests/test_users.py:89-93`.
- Tenant scope and case-insensitive matching: `request.user.tenant_id` and
  stripped `q` are passed to `find_users` (`app/users.py:27-29`); tested with a
  tenant assertion at `tests/test_users.py:44-55`.
- Safe fields: response maps only `id`/`display_name` (`app/users.py:35-37`);
  the fake row carries `email` to prove it is dropped.
- Bounded pagination: default 20, max 50, pass-through `cursor`, returned
  `next_cursor` (`app/users.py:19-29`); boundary, non-integer, and default tests.
- Stable ordering: delegated to `Database.find_users`, whose contract states a
  stable page order (`app/db.py:8-10`).
- Empty/whitespace `q` → 422 (`app/users.py:15-17`); tested.

The prose spec and the OpenSpec delta agree; no omission was found. The delta's
"rejects or caps" latitude for `limit=500` is taken as reject (422), which the
prose spec's "must not exceed 50" permits.

**FYI — DB-level guarantees are outside this diff.** The delta says "The system
SHALL return only users in the caller's tenant whose display name matches the
query case-insensitively" and "Results SHALL be ordered by `display_name ASC,
id ASC`." Those behaviours, plus cursor semantics and SQL safety, live behind
`Database.find_users`, which is declared but raises `NotImplementedError`
(`app/db.py:8-10`). This matches the pre-existing `find_user` pattern, so it is
not a defect in this change, but matching, ordering, and tenant filtering are
not exercised end to end. Fix direction: add DB-level tests when the
implementation lands.

**Nit — minimum limit is extra behaviour.** The delta/prose specify only
"default 20, maximum 50"; `app/users.py:23` also rejects `limit < 1`. Rejecting
zero is defensible, but it is beyond the written contract. Either keep it as an
explicit, tested choice (it is tested) or align the spec.

## Standards

**Verdict: pass.**

- Rule 1 (auth): handler is wrapped in `@require_auth` (`app/users.py:13`).
- Rule 2 (tenant scope): every access uses `request.user.tenant_id`
  (`app/users.py:28`); no unscoped read.
- Rule 3 (SQL): no SQL is constructed; the canonical `find_users` helper is
  used (`app/users.py:27-29`).
- Rule 4 (PII): the only audit fields are count and request ID
  (`app/users.py:30-33`); `q`, display names, and emails are not logged.
- Rule 5 (list endpoints): default 20, maximum 50, opaque cursor, and
  `next_cursor` are all present.
- Rule 6 (canonical helpers): `find_users` is reused rather than re-querying.
- Rule 7 (response fields): only `id` and `display_name` are returned.

No smell-baseline item rises above a nit; the handler is a small, single-purpose
function with no duplicated logic or speculative abstraction.

## Quality

**Verdict: pass.**

Correctness and edge cases are covered: whitespace-only `q`, absent/empty/
non-integer/out-of-range `limit`, missing cursor, anonymous caller, and dropped
extra row fields. Error replies are generic `{"error": ...}` messages with no
server detail. The full suite passes and both targeted mutations were killed, so
the tests are sensitive to boundary and tenant regressions.

### Optional — unbounded query length

- **Check:** Input boundary.
- **Evidence:** `app/users.py:15` accepts `q` of any length and passes it to the
  data layer; nothing in `CODING_STANDARDS.md` or the spec caps it.
- **Impact:** an oversized `q` reaches the database and any query plan on it;
  the request path can be made arbitrarily expensive.
- **Fix direction:** apply a documented maximum (e.g. 100 characters) with a
  422, or record that the DB layer owns the limit.

### Optional — the log-safety test does not exercise the logged sink

- **Check:** Injection (log injection).
- **Evidence:** `tests/test_users.py:94-115` builds
  `FakeRequest({"q": "ali", "request_id": "x\nforged"}, FakeUser())`. The
  `request_id` lives in `args`, which the handler never reads; the handler logs
  `request.request_id` (`app/users.py:32`), which is the default `"req-1"`. The
  assertions about `"forged"` therefore cannot fail for the real sink.
- **Impact:** if `request.request_id` can be client-influenced (header or
  proxy value), newline injection is unguarded and the test gives false
  assurance. The current code is not demonstrably unsafe on the `q` path,
  which is not logged.
- **Fix direction:** pass the forged value as the attribute
  (`FakeRequest(..., request_id="x\nforged")`), assert the sanitisation
  expected, or log only a server-generated ID.

### FYI — query cost is unverified

- **Check:** Index use / unbounded work.
- **Evidence:** name search will normally be implemented as `LIKE '%q%'` in the
  missing `Database.find_users`; the handler correctly bounds page size
  (`app/users.py:23-24`).
- **Impact:** a leading-wildcard scan could be slow on a large tenant table,
  but no implementation exists in this diff to inspect.
- **Fix direction:** capture `EXPLAIN` before/after when `find_users` lands, and
  avoid adding an index without that evidence.

## Probe and workspace confirmation

Both mutations produced the required failing focused test. The isolation copy
was returned to an empty directory. The review checkout has no tracked diff
(`git diff` empty); only pre-existing untracked `__pycache__/` directories
remain.

```text
verdict: pass
reason: handler meets every spec and standards rule with passing, mutation-killed tests; remaining notes are optional input-length and test-sink hardening
```
