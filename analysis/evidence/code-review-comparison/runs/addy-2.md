# Review: add user search endpoint (`feature/user-search` → `main`)

**Verdict: Request changes.** The new endpoint is unauthenticated, not tenant-scoped,
SQL-injectable, returns email addresses, and returns the whole table. The suite is green
only because its single test asserts the leak; five behaviour-breaking mutations survive it.

## Context

The spec (`docs/specs/user-search.md`) and the OpenSpec change agree: authentication is
required, results are tenant-scoped, `q` matches `display_name` case-insensitively, only
`id` + `display_name` are returned, empty/whitespace `q` is 422, and the endpoint takes
`limit` (default 20, max 50) + opaque `cursor` and returns `next_cursor`. `CODING_STANDARDS.md`
makes each of those binding (rules 1–7). The change adds the spec, proposal, one handler,
and one test. Crucially, `Database.find_users(tenant_id, q, limit, cursor)` already exists
with exactly this contract (`app/db.py:8-10`) and is not used.

All findings below are introduced by this change; `main`'s `get_user` is correctly
decorated and scoped, so there are no pre-existing defects to separate out.

## Critical

1. **SQL injection.** `app/users.py:15-17` interpolates `q` into the statement with an
   f-string. This directly violates standard 3 ("Never build SQL with f-strings, `%`, or
   string concatenation"). I ran the handler in the isolated copy against a real SQLite
   fixture holding two tenants: `q="' OR '1'='1"` and `q="%' --"` each returned every row.
   The f-string sits inside the `WHERE` clause, so a driver that allows stacked statements
   escalates this from disclosure to writes. Use a parameterized query — better, use
   `find_users`, which already parameterizes.

2. **No authentication.** `search_users` (`app/users.py:13`) is missing `@require_auth`;
   every other handler has it (standard 1). The only guard is the incidental
   `request.user.email` read on line 18, which raises `AttributeError` for an anonymous
   caller — a 500, not an `AuthError`. I confirmed the `AttributeError` with `user=None`.

3. **No tenant scoping.** The query has no `tenant_id` predicate, violating standard 2
   ("Never return another tenant's rows"). In the probe, a `tenant-a` caller received
   `tenant-b`'s "Zoe". Combined with (2), any unauthenticated caller can read every tenant.

4. **Email is returned.** The `SELECT` includes `email` and the handler returns `rows`
   verbatim (`app/users.py:16,19`), so the response carries `alice@example.com`. The spec's
   "Safe response fields" requirement and standard 7 forbid this. Because rows are passed
   through rather than projected, every column the query selects is exposed — today
   `email`, and any column added later.

5. **PII in the audit log.** Line 18 logs the caller's email **and** the raw query text:
   `audit_log.info(f"search by {request.user.email}: {q}")`. Standard 4 forbids both
   explicitly ("Never log email addresses ... or raw query text"). Log a count and a
   request ID instead.

## Required — structural root cause

**Replace the bespoke query with the canonical helper.** `app/db.py:8` defines
`find_users(tenant_id, q, limit=20, cursor=None)` — "Return tenant-scoped users matching q
with a stable page order." That is this endpoint's entire job. The change instead hand-rolls
a near-duplicate that duplicates scoping, matching, ordering, and pagination badly enough to
produce findings 1–4. This is the presumptive blocker in the review standard: a near-duplicate
of an existing canonical helper, placed in the handler instead of the owning layer.

The remedy collapses the branching rather than polishing it:

```python
@require_auth
def search_users(request, db):
    q = request.args.get("q", "")
    if not q.strip():
        return {"error": "q is required"}, 422
    rows, next_cursor = db.find_users(
        request.user.tenant_id, q,
        limit=limit, cursor=request.args.get("cursor"),
    )
    return {
        "users": [{"id": r["id"], "display_name": r["display_name"]} for r in rows],
        "next_cursor": next_cursor,
    }
```

(Adjust to `find_users`' actual return shape once confirmed; the point is that scoping,
parameter binding, and ordering belong in the DB layer, not in an f-string.) The explicit
projection is still required so the response contract does not depend on what SQL selects.

## Required — correctness and spec gaps

- **Empty query not rejected.** No 422 path exists. `q` defaults to `""`, so `LIKE '%%'`
  returns everything — the probe confirms an empty `q` dumps all rows. `q="   "` likewise
  returns a silent empty page instead of 422.
- **Matches the wrong field.** It searches `email`, not `display_name` (spec and proposal
  both say "Match on display name, not email"). This is also why the endpoint is a
  user-enumeration tool.
- **No pagination.** `limit`, `cursor`, and `next_cursor` are absent (standard 5). The
  probe shows `limit=500` changes nothing: the endpoint returns the full table. A leading
  `%` wildcard also makes the predicate unindexable, so cost is a full scan per request.
- **No case-insensitivity guarantee.** The bespoke `LIKE` relies on the backend's collation;
  the spec's case-insensitive `display_name` match is not expressed anywhere in the code.

## Required — tests are not testing the change

`tests/test_users.py:32-46` asserts that the response **contains `email`**, i.e. the test
enshrines finding 4. `FakeDB.query` ignores `sql` and `params` and returns a fixed row, so
the test only verifies that the handler forwards a stub's output. I inverted the
implementation in the isolated copy and re-ran the suite:

| Mutation | Suite |
|---|---|
| Baseline | green |
| Drop `email` from `SELECT` (fixes exposure) | **green** |
| Match `display_name` instead of `email` (corrects spec) | **green** |
| Ignore `q` entirely (`LIKE '%x%'`) | **green** |
| Add `@require_auth` | **green** |
| Delete the audit log line | **green** |
| Return `{"users": []}` always | red |

Only a total no-op is caught. Missing cases, by name: tenant scoping (a second tenant's
rows must be absent), field selection (exactly `id`/`display_name`, no `email`), empty and
whitespace `q` → 422, `limit` default/cap, and `cursor` round-trip. The task list is still
unchecked for exactly these ("Add tests for tenant scoping, field selection, and pagination").

## Optional / Nit

- **Optional:** The commit body is empty. Per the change-description standard it should say
  *why* and acknowledge that pagination and the 422 path are not yet implemented.
- **Nit:** `{"users": rows}` differs from `get_user`'s bare-object shape; pick one envelope
  convention for the module.
- **FYI:** The spec, proposal, and OpenSpec delta are consistent and well written; no
  findings there. `tasks.md` correctly leaves its boxes unchecked — it is an honest signal
  that the work is incomplete, not a defect.

## Verification

- `python3 -m unittest discover -s tests` → 2 tests, OK (on this branch).
- Behavioural probes and the mutation table above were run in
  `/tmp/opencode/cr-compare/iso-addy-2`; the review checkout was not modified.
- No build step exists in this repo; no UI changes.
- No manual verification story from the author, and the endpoint would fail the spec's own
  scenarios (email exposure, cross-tenant rows, no 422, no cap).

## Checklist

- Correctness: **fail** — wrong field, no 422, no pagination, no auth.
- Readability: acceptable, but the handler hides four contracts in one f-string.
- Architecture: **fail** — canonical `find_users` bypassed; query logic in the handler.
- Security: **fail** — injection, cross-tenant disclosure, PII in response and logs.
- Performance: **fail** — unbounded, unindexable full-table scan per request.
- Tests: **fail** — assert the defect; five mutations stay green.

**Request changes.** Address the Critical findings and replace the bespoke query with
`find_users`; the required tests should then fail against the old handler and pass against
the new one.
