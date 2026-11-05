# Code review: `add-user-search` (branch `feature/user-search`)

**Reviewer framework:** addyosmani `code-review-and-quality`, with `security-and-hardening` and `performance-optimization` plus their checklists.
**Change:** `f664357 add user search endpoint` — 6 files, +98/−1.
**Spec:** `docs/specs/user-search.md`, OpenSpec change `add-user-search`.
**Standards:** `CODING_STANDARDS.md`, `AGENTS.md`.
**Verdict: Blocked — request changes.** The implementation does not satisfy the spec on five of its seven clauses, and it introduces four security defects that the tests actively lock in.

## Context

Support needs to find a user by display name without exporting the tenant user list. Spec requires: auth, tenant scope, case-insensitive `display_name` match, `q` empty/whitespace → 422, `id` + `display_name` only (never `email`), `limit` default 20 / max 50, opaque `cursor`, `next_cursor`, order `display_name ASC, id ASC`.

The change adds `search_users` to `app/users.py` plus spec/proposal/tasks and one test. Tests run green: `python3 -m unittest discover -s tests` → 2 passed. The green suite is the problem, not the reassurance: it asserts the wrong contract and is blind to every security property.

## Critical findings

**Critical: No authentication on the route.** `search_users` is the only handler in the module without `@require_auth` (`app/users.py:13`). Standards §1 says every route handler must be wrapped. This is not only an auth bypass: an unauthenticated request reaches `request.user.email` on the audit line and raises `AttributeError` → 500 (reproduced by calling `search_users(FakeRequest({"q": "a"}, None), FakeDB())`). So the endpoint either serves anonymous callers or crashes, depending on how the framework populates `user`.

**Critical: SQL injection.** `app/users.py:15-17` builds the statement with an f-string:
```python
f"SELECT id, email, display_name FROM users WHERE email LIKE '%{q}%'"
```
`q = ' OR '1'='1` broadens the predicate and can read across tenants and columns — the exact vector standards §3 forbids ("never build SQL with f-strings, `%`, or string concatenation"). Unescaped `%`/`_` in `q` also become wildcards.

**Critical: No tenant scoping.** `db.query` is called with no `tenant_id` and no params, so results are global. Standards §2 and the spec's first requirement ("only users in the caller's tenant") are both violated. Combined with the injection above, this is cross-tenant data disclosure.

**Critical: Email exposure and PII logging.** The query selects `email` and the endpoint returns `{"users": rows}` verbatim, so `email` reaches the response — explicitly forbidden ("Return `id` and `display_name` only. Never return `email`."; standards §7). The audit line logs the caller's email **and** the raw query text: `audit_log.info(f"search by {request.user.email}: {q}")`. Standards §4 bans logging emails and raw query text; log counts, IDs, request IDs only. This writes PII into the audit trail, which is harder to purge than a field in a response.

## Required findings

**Wrong search field.** The spec and proposal both say match `display_name`. The code matches `email`, so even with injection and scoping fixed it answers a different question.

**No pagination.** No `limit`, no `cursor`, no `next_cursor`, no cap. `db.query` returns the full table. Standards §5 and the spec's "Bounded pagination" requirement are unmet, and "limit=500 → reject or cap at 50" has no implementation at all. This is also the unbounded-fetch anti-pattern in the performance checklist.

**Empty query not rejected.** `request.args.get("q", "")` treats missing/blank `q` as a match-everything query instead of returning 422. Whitespace-only is not trimmed.

**Canonical helper bypassed.** `Database.find_users(tenant_id, q, limit=20, cursor=None)` exists in `app/db.py:8` precisely for this and is documented as tenant-scoped with a stable page order. The change hand-rolls a near-duplicate query instead (standards §6, "reuse existing helpers"). Deleting the bespoke SQL also deletes the injection, scoping, and pagination defects in one move — this is the structural remedy, not four separate patches.

**Tests encode the defect.** `SearchUsersTest` asserts the response includes `email` and passes a `FakeDB` whose `query` ignores its arguments, so it cannot detect SQL or tenancy errors. `FakeDB` has no `find_users`, so switching to the canonical helper fails the suite for the wrong reason (`AttributeError`). Per the review skill, "would the tests catch a regression" must be answered by experiment:

| Probe (in `/tmp/opencode/cr-compare/iso-addyplus-3`) | Result |
|---|---|
| Add `@require_auth` to `search_users` | still 2 passed — no auth test |
| Replace with compliant impl using `db.find_users` | `AttributeError: 'FakeDB' has no attribute 'find_users'` — double cannot exercise the canonical path |
| Remove `email` from the fake row (i.e. fix the leak) | **FAIL** — the test demands the leaked field |
| Parameterize + add tenant filter, keep returning `email` | still 2 passed — suite cannot see SQL or tenancy |

The one test that reacts, reacts to the *fix*; the defects pass silently. Missing cases: unauthenticated → `AuthError`, cross-tenant row excluded, `email` absent, `limit` cap, `next_cursor`, `q=""` → 422, case-insensitivity.

**Task tracking.** `tasks.md` still has both items unchecked (`- [ ] Add the search route.`, `- [ ] Add tests for …`) while the route is committed. Ticking the route task would be honest; the test task genuinely is not done.

## Nits

- **Nit:** lazy logging is preferred (`audit_log.info("search tenant=%s count=%d", …)`) so formatting is skipped when the level is off — moot until the PII is removed.
- **Nit:** the commit subject is fine (`<area>: <imperative>`), but the body has no spec link or rationale; the review skill asks for a body that explains "why" and any known shortfall.
- **Nit:** `docs/specs/user-search.md` and the OpenSpec delta duplicate the same four requirements; acceptable as spec + change delta, but keep them in sync if the requirement text changes.

## Other axes

**Readability:** small and easy to follow; naming is consistent. The problem is contract, not legibility.

**Architecture:** one new function bolted onto `users.py` with no shared model; reusing `find_users` removes the duplication. File is small, no size concern.

**Performance:** the leading-wildcard `LIKE '%q%'` cannot use a B-tree index (needs trigram/full-text), and the query is unbounded — the two largest back-end anti-patterns on the checklist. Nothing here was measured, so no performance claim is made beyond the structural defects.

**Security checklist walk:** auth ✗, authorization/tenant scope ✗, parameterized SQL ✗, field allowlist ✗, PII in logs ✗, bounded input ✗. No secrets, headers, CORS, uploads, SSRF, or LLM surface in scope.

## Remediation

One change, in this order:

1. Decorate with `@require_auth`.
2. Trim `q`; return `422` when empty.
3. Parse and clamp `limit` (default 20, max 50) and pass `cursor`.
4. Call `db.find_users(request.user.tenant_id, q, limit=…, cursor=…)`; return only `id` and `display_name` plus `next_cursor`.
5. Log tenant + result count only.
6. Extend `FakeDB` with `find_users`, and add the tests listed above — each should fail before the fix.

## Verdict

**Request changes.** Deliverable is blocked by four Critical defects (auth, injection, tenant scope, PII/field exposure) and five required gaps. The helper `find_users` already embodies the correct contract, so the fix is a deletion-and-reuse, not a rewrite. Re-review after the tests fail against the current implementation and pass against the corrected one.

**Verification story:** suite run (2 passed); four mutation probes above; unauthenticated-call probe. No manual/browser verification applicable.
