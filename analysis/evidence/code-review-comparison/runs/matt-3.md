# Code review: `feature/user-search` vs `main`

**Fixed point:** `main` (`d84de4d`). Diff: `git diff main...HEAD`, commit list: `2f28cb0 add user search endpoint`.
**Spec sources:** `docs/specs/user-search.md` and the OpenSpec change `openspec/changes/add-user-search/` (proposal, `specs/users/spec.md`, tasks).
**Standards sources:** `CODING_STANDARDS.md` (rules 1–7, binding) and `AGENTS.md` (test command), plus the Fowler smell baseline.

Method note: this harness exposes no sub-agent tool, so the two axes were run as separate passes over the same diff rather than in fresh child contexts. Mutation probes were run only in `/tmp/opencode/cr-compare/iso-matt-3`.

Test suite at HEAD: 2 tests, both pass (`python3 -m unittest discover -s tests`). Passing here is not evidence of correctness, as the probes below show.

## Standards

### `app/users.py` — `search_users`

- **Hard: rule 1 (Authentication).** The handler is not wrapped in `@require_auth`; `get_user` above it is. Any caller reaches it unauthenticated.
- **Hard: rule 2 (Tenant scope).** The query has no `tenant_id` predicate. `request.user.tenant_id` is never read, so results span every tenant. This is the cross-tenant leak the rule exists to prevent.
- **Hard: rule 3 (SQL).** `f"SELECT ... WHERE email LIKE '%{q}%'"` interpolates `q` into SQL. `q = "'; DROP TABLE users; --"` or a UNION payload is passed straight through. Rule 3 names f-strings, `%`, and concatenation explicitly.
- **Hard: rule 4 (PII).** `audit_log.info(f"search by {request.user.email}: {q}")` logs the caller's email and the raw query text. Rule 4 permits counts, IDs, and request IDs only.
- **Hard: rule 5 (List endpoints).** No `limit`, no `cursor`, no `next_cursor`, no cap. The result set is unbounded and the caller cannot page.
- **Hard: rule 6 (Canonical helpers).** `Database.find_users(tenant_id, q, limit=20, cursor=None)` exists in `app/db.py` and is not used. The diff re-implements tenant-scoped, paginated user lookup by hand.
- **Hard: rule 7 (Response fields).** Rows are returned raw, so `email` is in the response body, not just selected.

### `tests/test_users.py`

- **Hard, indirect: rule 7 / rule 2 coverage.** `FakeDB.query` returns a row containing `email`, and `test_returns_matches` asserts the email is present in the response. The test encodes the violation as the expected contract, so it fails when the response is corrected. `FakeDB` also has no tenant predicate, so nothing can catch the missing tenant scope.
- **Judgement: no test for auth, empty query, `limit`/`cursor`, ordering, or PII logging.** The single test asserts a stub's return value reaches the caller.

Probe evidence, `iso-matt-3`:

| Probe | Result |
|---|---|
| Replace the `WHERE` clause with `WHERE 1=1` (match everyone, every tenant) | suite still passes |
| Delete the `audit_log.info` PII line | suite still passes |
| Return only `id` and `display_name` (spec-correct) | suite **fails** |

So the suite pins neither matching, nor tenancy, nor logging, and actively rejects the compliant response shape.

### Smell baseline (judgement calls, not violations)

- **Possible Duplicated Code** — the query shape duplicates `Database.find_users`. Rule 6 already makes this hard; the smell is that the two will drift.
- **Possible Feature Envy** — `search_users` reaches into the `users` table's columns and ordering rules instead of letting `Database` own them. Fix: call `find_users`.
- No Speculative Generality, Repeated Switches, or Message Chains worth flagging; the handler is short.

## Spec

Against `docs/specs/user-search.md` and the `add-user-search` delta.

### (a) Missing or partial

- "Results are limited to the caller's tenant" / *Tenant-scoped user search* — **missing**. No tenant filter at all.
- "`q` matches `display_name` case-insensitively" / *Match within tenant* — **missing**. The `LIKE` target is `email`, and `LIKE` case-sensitivity is collation-dependent rather than explicitly case-insensitive.
- "An empty or whitespace-only `q` returns 422" / *Empty query rejected* — **missing**. Empty `q` becomes `LIKE '%%'`, returning the tenant's whole user table (in practice, everyone's).
- "`limit` defaults to 20 and must not exceed 50" / *Bounded pagination* — **missing**. `limit` is ignored, so `limit=500` is neither rejected nor capped.
- "Return an opaque `next_cursor`" / *Bounded pagination* — **missing**. No cursor is accepted or returned.
- "Order by `display_name ASC, id ASC`" — **missing**. No `ORDER BY`; page contents are undefined.
- "Authentication is required" — **missing**. No `@require_auth`.

### (b) Not asked for (scope creep)

- An audit log line recording the caller's email and the raw search text. Nothing in the spec or proposal asks for search auditing, and it is the one behaviour that actively worsens the change (rule 4).
- Selecting `email` in the query. The spec says return and match on display name only; the extra column serves no requested purpose.
- The test fixture and assertion that lock `email` into the response contract.

### (c) Present but wrong

- **Matching on email instead of display name.** The proposal says "Match on display name, not email"; the requirement says "whose display name contains". The SQL filters `email LIKE '%{q}%'`, so a support agent searching "ali" matches `alice@example.com` and misses anyone whose display name contains "ali" but whose address does not. This inverts the premise of the feature ("find a user by name without exporting the tenant's user list").
- **Returning `email`.** *Safe response fields* says the response "SHALL contain `id` and `display_name` only" and the scenario asserts the response has no `email` field. It has one, for every row.

Also: `tasks.md` still has both items unchecked although the route and tests were added, and the OpenSpec change is not marked complete. Minor process drift, worth fixing before review sign-off.

## Summary

- **Standards:** 7 hard breaches (one per rule) plus 2 judgement-call smells. Worst: unauthenticated, tenant-unscoped SQL assembled by f-string interpolation, returning email and logging it.
- **Spec:** 7 requirements missing or partial, 3 unrequested behaviours, 2 requirements implemented incorrectly. Worst: the endpoint matches on email and returns email, contradicting the two requirements the change names first.
