# Tasks

## 1. Search route slice

- [ ] 1.1 Create `tests/api.test.js` with failing tests using `createApp({ db })`
  and `registerRoutes`, calling `app.handle({ method: "GET", path:
  "/tasks/search?term=report", session })` and rows shaped
  `{ id, userId, title }`: a matching search returns status 200 and exactly the
  two matching tasks as `{ id, title }` with no other rows or fields; another
  user's matching task is excluded while the session user's match is present; a
  caller-supplied `userId` for another user does not change the result; a request
  without a session returns 401 and no `results` key; a request without a session
  and with a blank term also returns 401; a request without a session and a
  repeated `term` also returns 401; an authenticated missing, empty, or
  whitespace-only term returns 200 with empty `results`; a repeated `term`
  returns 200 with empty `results`; a padded term returns the same set as the
  trimmed term; a non-matching term returns 200 with empty `results`. Compare
  results as a set. Verify `node --test` fails because the route does not exist.
- [ ] 1.2 Add the `GET /tasks/search` route in `src/api.js`: call
  `requireUser(request)` first, then read `request.query.term`, treat a
  non-string as empty, trim it, short-circuit a blank term, `await`
  `searchTasks(request.db, userId, term)`, map rows to only `{ id, title }`, and
  return `{ results }`. Ignore any `userId` query parameter. Verify `node --test`
  passes.
- [ ] 1.3 Verify the whole change: `node --test` and the build command in
  `AGENTS.md` both pass.

## 2. Artifact check

- [ ] 2.1 Run `openspec validate add-task-search --type change --strict`. Then
  copy the fixture to `/tmp/opencode/archive-check`, run
  `openspec archive add-task-search --yes` there, and run
  `openspec validate --specs --strict` on the result. Never archive the working
  change. Verify both pass.
