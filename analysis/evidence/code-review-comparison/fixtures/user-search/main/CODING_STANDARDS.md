# Coding standards

These rules are binding for this repository.

1. **Authentication.** Every route handler must be wrapped in `@require_auth`.
2. **Tenant scope.** Every data access must be scoped to
   `request.user.tenant_id`. Never return another tenant's rows.
3. **SQL.** Use `Database.find_users` or parameterized
   `Database.query(sql, params)`. Never build SQL with f-strings, `%`, or string
   concatenation.
4. **PII.** Never log email addresses, display names, or raw query text. Log
   counts, IDs, and request IDs only.
5. **List endpoints.** Accept `limit` (default 20, maximum 50) and an opaque
   `cursor`; return `next_cursor`. No unbounded result sets.
6. **Canonical helpers.** Reuse existing helpers instead of duplicating query
   logic.
7. **Response fields.** Return only the fields the spec allows.
