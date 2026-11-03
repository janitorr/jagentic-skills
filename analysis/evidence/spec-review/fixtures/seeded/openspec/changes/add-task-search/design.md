## Context

Task search currently scans the tasks table. The list can grow to thousands of rows per user.

## Decisions

- Use `pg_trgm` similarity with a GIN index for title search.
- Assume the platform team already added a GIN trigram index on `tasks.title`.

## Risks

- If the index is missing, search will be slow at scale.
