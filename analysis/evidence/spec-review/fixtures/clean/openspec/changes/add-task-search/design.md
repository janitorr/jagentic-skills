## Context

`searchTasks` already scopes queries by `userId` in `src/search.ts`. The current
dataset is small, so this change reuses the existing query path.

## Decisions

- Keep the existing `contains` query and user scoping; add no new index.
- Put the endpoint behind the existing authentication middleware.

## Risks

- Very large task lists may need an index later; measure before adding one.
