# Review: add user search endpoint (`feature/user-search` → `main`)

## Context

`GET /users/search?q=&limit=&cursor=` for support staff, per `docs/specs/user-search.md`
and `openspec/changes/add-user-search`. The spec is precise: authenticated, tenant-scoped,
case-insensitive match on `display_name`, `id` + `display_name` only, `limit` default 20 /
max 50, opaque `cursor`/`next_cursor`, empty `q` → 422.

The implementation (`app/users.py:13-19`) does none of that. The diff is small (98 lines),
so size is not the problem: the code contradicts every binding rule in `CODING_STANDARDS.md`
(#1 auth, #2 tenant, #3 SQL, #4 PII, #5 list endpoints, #6 canonical helpers, #7 response
fields).

## Verdict: Request changes — do not merge

This is a security regression, not a style disagreement: a cross-tenant PII dump reachable
without authentication.

## Critical

### 1. SQL injection — `app/users.py:15-17`

```python
rows = db.query(f"SELECT id, email, display_name FROM users WHERE email LIKE '%{q}%'")
```

`q` is interpolated into the statement. Confirmed by probing the handler with a recording
fake DB: `q="a' OR '1'='1"` produced
`... WHERE email LIKE '%a' OR '1'='1%'`, and `params` was `()`. Directly violates
`CODING_STANDARDS.md` #3 ("Never build SQL with f-strings, `%`, or string concatenation").

Remedy: call the canonical helper that already exists —
`db.find_users(request.user.tenant_id, q, limit=limit, cursor=cursor)`.

### 2. No authentication — `app/users.py:13`

`get_user` carries `@require_auth`; `search_users` does not. Standards #1 requires it on
every route handler. Probing with `request.user = None` reached the query and only crashed
at the audit line (`AttributeError`), i.e. the unauth path is a 500 today and an anonymous
data path the moment the logging line moves or is removed.

### 3. No tenant scoping — `app/users.py:15-17`

The SQL has no `tenant_id` predicate, and `request.user.tenant_id` never appears. This
violates the OpenSpec "Tenant-scoped user search" requirement, standards #2, and OWASP A01.
It is an authorization bypass, not a missing filter.

### 4. Email returned to the caller — `app/users.py:16,19`

The query selects `email` and returns `rows` verbatim. Spec: "Return `id` and
`display_name` only. Never return `email`." Standards #7 agrees. Project explicitly:

```python
return {"users": [{"id": r["id"], "display_name": r["display_name"]} for r in rows],
        "next_cursor": ...}
```

### 5. PII written to the audit log — `app/users.py:18`

```python
audit_log.info(f"search by {request.user.email}: {q}")
```

Standards #4 forbids logging email addresses and raw query text. This logs both, and the
free-form `q` also enables log forging via newlines. Log a count and a request ID instead.

## Required

### 6. Unbounded, unpaginated result set — `app/users.py:14-19`

`limit`, `cursor`, and `next_cursor` are ignored; probing `?limit=500` produced a plain
match-all query with no `LIMIT`. Spec and standards #5 require default 20, max 50, stable
`display_name ASC, id ASC` order, and an opaque cursor. A lone `%` in `q` matches the whole
table. The leading-wildcard `LIKE '%q%'` also cannot use a B-tree index, so this is a
sequential scan over every tenant's users on every request — a performance problem that is
here primarily a data-exfiltration vector.

### 7. Empty/whitespace `q` accepted — `app/users.py:14`

`q = request.args.get("q", "")` accepts `""` and `"   "` and runs a match-all search; probing
`q="   "` produced `WHERE email LIKE '%   %'` and a normal result. Spec requires 422.
Validate and strip before querying.

### 8. Wrong match field, and case sensitivity unaddressed — `app/users.py:16`

The spec matches `display_name` case-insensitively; the query matches `email`. This is a
functional miss independent of the injection, and searching an email prefix turns the
endpoint into an address-enumeration oracle. Plain `LIKE` is case-sensitive on Postgres, so
"case-insensitively" needs `lower(...)` on both sides (or the helper's defined semantics).

### 9. Canonical helper bypassed — `app/users.py:15`

`Database.find_users(tenant_id, q, limit=20, cursor=None)` exists in `app/db.py:8` with the
docstring "tenant-scoped users matching q with a stable page order". Standards #6 says reuse
it rather than duplicating query logic. The bespoke query duplicates it and gets it wrong.
Note the helper signature already answers #3, #6, and #8; the handler should contain almost
no query code.

### 10. Tests enshrine the defect and catch nothing — `tests/test_users.py:32-46`

`FakeDB.query` ignores `sql` and `params` and returns a hard-coded row containing `email`;
`test_returns_matches` asserts that exact dict, email included. Verified by mutation in the
isolated copy:

| Probe | Result |
|---|---|
| Replace the whole query with `WHERE 1=0` (zero results) | green |
| Delete the audit-log line | green |
| Replace `q` with a constant | green |
| Remove `@require_auth` from `get_user` | green |
| Strip `email` from the response (spec-correct) | **red** |

So every security-relevant behavior can change without a failure, while the correct fix
breaks the suite. That is a regression guard for the bug. The fake should record
`(sql, params)` — or the handler should call `find_users` and the fake should assert
`tenant_id` — and the suite needs cases for: no auth → `AuthError`, `q=` / `q="  "` → 422,
`email` absent, `limit=500` capped/rejected, `next_cursor` present, and tenant A never
seeing tenant B.

### 11. Tasks claim undone work — `openspec/changes/add-user-search/tasks.md:3-4`

Both tasks are unticked, and task 2 ("tests for tenant scoping, field selection, and
pagination") is exactly the missing coverage. Either the change is incomplete or the
tracker is stale; either way it should not merge as-is.

## Nit

- Commit `f664357 "add user search endpoint"` has no body and omits the `<area>:` prefix
  the repo's `git-workflow` convention asks for. The why (support lookup without exporting
  the tenant user list) and the tenant/PII constraints belong in the message.
- `request.args.get("q", "")` vs `get_user`'s `request.args["id"]` is inconsistent access
  style; settle on one while implementing the validation in #7.

## What is good

- The spec, proposal, and OpenSpec delta are coherent, specific, and testable; the scenarios
  map cleanly onto the missing tests.
- Change size is right (~100 lines) and `get_user` is untouched — no collateral refactoring.
- Handler name and location match the existing module structure.

## Verification

- `python3 -m unittest discover -s tests` → 2 passed. Green but not meaningful: the search
  test asserts the wrong contract.
- No router/framework exists in this fixture, so no live HTTP call was possible; the handler
  was exercised directly with a recording fake DB (`search_users` returned `{"users": []}`
  and the recorded SQL/params are quoted above).
- Mutation probes ran only in the isolated copy `/tmp/opencode/cr-compare/iso-addyplus-1`;
  the review tree was left clean (`git status` empty before and after).

## Checklist

- Correctness: ✗ wrong field, no 422, no pagination, no ordering, no tenant filter
- Readability: ✓ small and readable — the problem is behavior, not expression
- Architecture: ✗ bypasses `Database.find_users`, the canonical helper
- Security: ✗ injection, no auth, cross-tenant read, PII in response and logs
- Performance: ✗ unbounded list, no limit, unindexed leading-wildcard scan
- Tests: ✗ green while asserting the defect; would not catch a regression
- Build: tests green only because the oracle is wrong

Fix order: `@require_auth` + `find_users` call (kills #1–#3, #6, #8, #9) → response
projection (#4) → logging (#5) → 422 (#7) → rewrite the search test as a behavior test
(#10) → tick tasks (#11).

## Skills followed

- `vendor/addyosmani-agent-skills/skills/code-review-and-quality/SKILL.md`
- `vendor/addyosmani-agent-skills/skills/security-and-hardening/SKILL.md`
- `vendor/addyosmani-agent-skills/skills/performance-optimization/SKILL.md`
- `vendor/addyosmani-agent-skills/references/security-checklist.md`
- `vendor/addyosmani-agent-skills/references/performance-checklist.md`
