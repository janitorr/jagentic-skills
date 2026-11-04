# Design

## Context

See `proposal.md` for motivation. The repo has a small app shell:

- `createApp({ db })` in `src/app.js` parses the query string from
  `request.path` into `request.query` (a string per key, or an array for a
  repeated key), routes on the exact `${method} ${path}` key, passes `db` to
  route handlers, and turns a thrown error with a `status` into a response.
- `registerRoutes(app)` in `src/api.js` currently registers `/health`.
- `requireUser(request)` in `src/auth.js` reads `request.session.userId` and
  throws a 401 error when absent.
- `searchTasks(db, userId, term)` in `src/search.js` runs a user-scoped title
  `contains` query and returns task rows.
- `schema/tasks.sql` defines `tasks(id, userId, title)`.

`tests/app.test.js`, `tests/auth.test.js`, and `tests/search.test.js` cover the
shell, the auth helper, and the query. They pass at baseline. The session
object is supplied by the caller; session trust is outside this repository.

## Goals / Non-Goals

**Goals:**

- One authenticated route that reuses the existing query and auth helper.
- A request and response contract the route tests can assert without guessing.

**Non-Goals:**

- The UI search box and the HTTP transport that supplies `request.session`.
- Full-text search across descriptions and saved searches.
- Case, fuzzy, or ranking changes to matching.
- An index and any result ordering guarantee.

## Decisions

### Route and term transport

Add `GET /tasks/search` to `registerRoutes`. Read the term from
`request.query.term`; the shell already parses the query string, and the route
path stays exactly `/tasks/search`.

Alternatives rejected: a path segment (`/tasks/search/:term`) forces a router
change and cannot express a missing term; a request body is wrong for a GET;
parsing the URL inside the route duplicates the shell.

### Authentication before the term

Call `requireUser(request)` first and keep its returned id. Its 401 error is
already mapped to a response by `createApp`. Ignore any `userId` query
parameter; the route never reads it.

Alternatives rejected: reading `request.session` in the route duplicates the
auth gate; accepting a `userId` query parameter would let a caller choose
another user's tasks; checking the term first would return 200 for an
unauthenticated blank request.

### Term normalization

Read `request.query.term`. The shell yields a string, an array for a repeated
key, or `undefined`. If the value is not a string, treat it as empty. Trim it. A
missing, empty, or whitespace-only term returns `{ "results": [] }` without
calling `searchTasks`.

Alternatives rejected: putting the guard inside `searchTasks` changes an
exported function's behavior for every caller; throwing on a non-string turns a
malformed request into a 500; returning 400 for a blank term would make an empty
search box an error, which the UI follow-up needs to treat as "no results".

### Result mapping

Map each row to exactly `{ id, title }` before responding, using the columns in
`schema/tasks.sql`.

Alternatives rejected: returning raw rows leaks `userId` and couples the API to
the table; returning titles alone loses the key the UI follow-up needs.

### Matching and envelope

Pass the trimmed term to the existing `contains` query and return
`{ "results": [...] }`. Do not change case, fuzzy, or ranking behavior. Case
behavior is a property of the data layer; the repository's test double is
case-sensitive, and the route adds no guarantee.

Alternatives rejected: case-insensitive or fuzzy matching changes observable
behavior the issue did not request; a bare array leaves no room for later
metadata.

### Result order

The order is unspecified. Tests compare results as a set.

Alternatives rejected: adding `orderBy` needs a field choice and a spec change
the issue did not ask for.

### No index

Add no index. Measure before adding one.

Alternatives rejected: a trigram index now, without a measured problem, adds a
migration and an extension dependency.

## Risks / Trade-offs

- Large task lists may need an index later. → Measure, then add one in a
  separate change.
- Case behavior depends on the data layer and is not enforced here. → Documented;
  changing it needs a spec change and a data-layer decision.
- Results are unordered. → Clients must not rely on order; tests compare sets.
- A broad term returns every match with no limit. → Accepted for this slice;
  pagination is a separate change, and the UI follow-up must not assume a cap.
- The endpoint is API-only until the UI change lands. → `followup-search-ui.md`
  tracks it, not silently dropped.
- Session trust is only as strong as the caller-provided session. → Out of scope
  here; the route never accepts a caller-supplied user id.

## Migration Plan

Additive route. Roll back by removing it; no data, schema, or dependency change.
