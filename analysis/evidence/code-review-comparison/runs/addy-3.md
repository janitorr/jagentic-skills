# Review: `feature/user-search` vs `main`

**Change:** `2f28cb0 add user search endpoint` — 98 lines across 6 files (handler, tests, spec, OpenSpec artifacts).
**Intent:** tenant-scoped, paginated user search by display name, returning `id`/`display_name` only.
**Verdict: Request changes.** The handler implements almost none of the spec, and its green test locks in the worst violation.

## Context

The base `app/users.py` already demonstrates the intended pattern: `@require_auth`, `db.find_user(request.user.tenant_id, ...)`, and a response projected to `id`/`display_name`. `app/db.py` also ships `Database.find_users(tenant_id, q, limit=20, cursor=None)` — the canonical helper for exactly this endpoint. `CODING_STANDARDS.md` is binding, and rules 1–7 map one-to-one onto the spec. The change satisfies none of the seven as written.

## Critical

**Critical: SQL injection via f-string interpolation.** `app/users.py:16-18` builds `"... LIKE '%{q}%'"` from raw `request.args["q"]`. A `q` of `x' OR '1'='1` becomes `LIKE '%x' OR '1'='1%'`, returning every row; `'; DROP ...` is reachable depending on driver. This breaks standards rule 3 directly. Fix: call `db.find_users(request.user.tenant_id, q, limit=limit, cursor=cursor)` — the helper already exists, so no SQL needs writing at all.

**Critical: no tenant scoping.** The query has no `tenant_id` predicate, so the endpoint returns users from every tenant (standards rule 2, OpenSpec "Tenant-scoped user search"). This is a cross-tenant data leak, not a style issue. The same fix — delegating to `find_users` — removes it.

**Critical: `email` is returned.** `SELECT id, email, display_name` is passed straight back as the response, violating the spec ("Never return `email`"), proposal, and standards rule 7. Worse, `tests/test_users.py` asserts the email in the expected payload, so the test certifies the leak. Fix: project `id`/`display_name` and change the test to assert email is absent.

**Critical: no `@require_auth`.** Standards rule 1 says every route handler must be wrapped. `search_users` reads `request.user.email` and `request.user.tenant_id` unguarded: an unauthenticated request either raises `AttributeError` (500) or reaches user lookup depending on the wiring. Same defect class as the base handler, which the change should have copied.

## Required

**Required: no pagination, unbounded result set.** `limit` and `cursor` are ignored and no `next_cursor` is returned, violating standards rule 5 and the spec's bounded-pagination requirement. Fix: parse `limit` (default 20, cap 50, reject otherwise), pass it and `cursor` to `find_users`, and return `next_cursor`.

**Required: PII written to the audit log.** `audit_log.info(f"search by {request.user.email}: {q}")` logs both the actor's email and the raw search text. Standards rule 4 forbids logging emails, display names, or raw query text; log the result count and a request ID instead. Note the import at line 2 exists only for this line, so it should change shape, not merely move.

**Required: empty/whitespace `q` returns all users instead of 422.** `request.args.get("q", "")` plus `LIKE '%%'` is a full-table dump, and the spec requires 422 for empty or whitespace-only input. Validate after `strip()`.

**Required: matches the wrong column and ignores case semantics.** The spec says match `display_name` case-insensitively; the query matches `email`. This is not a nit: it changes both the result set and the privacy posture. `find_users` owns this behavior.

**Required: bypasses the canonical helper.** `Database.find_users` exists with the exact signature (tenant, q, limit, cursor) and docstring "tenant-scoped users matching q with a stable page order". Hand-rolling a second query path in the same module is the near-duplicate-helper smell the standards call out (rule 6). Structural remedy: delete the bespoke SQL and delegate.

**Required: tests do not verify the contract.** `FakeDB.query(sql, params)` discards both arguments and always returns one hard-coded row containing `email`, so every query-level property is untested. Mutation probes on `/tmp/opencode/cr-compare/iso-addy-3` (original restored after each):

| Probe | Result |
|---|---|
| Always return `{"users": []}` | caught (fails) |
| Ignore `q` (`q = "fixed"`) | **still green** |
| Match `display_name` instead of `email` | **still green** |
| Drop `email` from the `SELECT` | **still green** |
| Add tenant predicate + parameters | **still green** |
| Delete the audit-log line | **still green** |

The last row means even the PII logging is unobserved. Missing tests: cross-tenant exclusion, email absence, `limit` default/cap, `next_cursor`, empty/whitespace `q` → 422, and unauthenticated access. Rewrite `FakeDB` to record `(sql, params)` or, better, fake `find_users` and assert it was called with the caller's tenant, `limit`, and `cursor`.

## Optional / Nit

**Optional:** `tasks.md` is committed with both items unchecked even though the task claims completion; update it or leave it out of the change. The second item ("tests for tenant scoping, field selection, and pagination") is in fact not done, so unticking is honest — but it should block merge.

**Nit:** commit subject is a fine standalone imperative, but there is no body explaining behavior or known gaps. Given the diff, a body acknowledging follow-up work would help.

**FYI:** `docs/specs/user-search.md` and the OpenSpec delta agree with each other and are well-scoped; the problem is entirely on the implementation side. The 422, cursor, and case-insensitive requirements are unambiguous, so there is no spec ambiguity to resolve.

## Verification

`python3 -m unittest discover -s tests` passes (2 tests). The suite is green for the wrong reasons: it asserts the spec-violating response and never inspects the SQL or the auth wrapper. A green run here provides no evidence for any requirement in the change.

## Recommendation

Request changes. The smallest correct implementation is roughly:

```python
@require_auth
def search_users(request, db):
    q = request.args.get("q", "").strip()
    if not q:
        return {"error": "q is required"}, 422
    limit = min(int(request.args.get("limit", 20)), 50)
    users, next_cursor = db.find_users(request.user.tenant_id, q, limit, request.args.get("cursor"))
    audit_log.info("user search returned %d results", len(users))
    return {"users": [{"id": u["id"], "display_name": u["display_name"]} for u in users],
            "next_cursor": next_cursor}
```

That version deletes the bespoke SQL rather than polishing it, satisfies rules 1–7, and makes the existing tests meaningful once they assert the contract instead of the bug.
