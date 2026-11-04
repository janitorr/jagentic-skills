## Why

Users cannot find tasks once the list grows beyond a screen.

## What Changes

- Add an authenticated title search endpoint scoped to the current user.
- Define the request contract: the term arrives in the query string, is trimmed,
  and matching semantics stay those of the existing query.
- Define the response: a JSON object with a `results` array whose entries carry
  `id` and `title`.
- Reject unauthenticated requests with 401 before reading the term; return an
  empty result set for a missing, empty, whitespace-only, or non-string term.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `task-search`: Add authentication, user scoping, trimming, the empty-term
  case, and the response envelope to the existing title search.

## Impact

- Adds one route to `registerRoutes` in `src/api.js`, reusing `searchTasks` in
  `src/search.js` and `requireUser` in `src/auth.js`.
- No schema change and no index change.
- The search box is not delivered here; `followup-search-ui.md` tracks it. This
  repository has no UI.
