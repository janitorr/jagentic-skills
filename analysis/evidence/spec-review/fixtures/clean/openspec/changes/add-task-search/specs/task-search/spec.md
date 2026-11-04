## MODIFIED Requirements

### Requirement: Search tasks by title
The system SHALL return tasks whose title contains the search term, limited to
tasks owned by the authenticated user.

#### Scenario: Matching tasks are returned
- **WHEN** an authenticated user searches for a term present in two of their task titles
- **THEN** the response has status 200 and `results` contains exactly those two tasks

#### Scenario: Another user's tasks are excluded
- **WHEN** a user searches for a term that also appears in another user's task title
- **THEN** the response has status 200, contains the session user's matching task, and excludes the other user's task

#### Scenario: Caller-supplied user id is ignored
- **WHEN** an authenticated user supplies a different user's id as the `userId` query parameter
- **THEN** the response has status 200 and contains only the session user's matching tasks

#### Scenario: Non-matching term returns no tasks
- **WHEN** an authenticated user searches for a term that matches none of their tasks
- **THEN** the response has status 200 and an empty `results` array

## ADDED Requirements

### Requirement: Search endpoint authentication
For `GET /tasks/search`, the system SHALL reject a request without an
authenticated user with status 401 and no task data, regardless of the term.

#### Scenario: Unauthenticated request is rejected
- **WHEN** a request without an authenticated session supplies a term
- **THEN** the response has status 401 and contains no `results` or task data

#### Scenario: Authentication is checked before the term
- **WHEN** a request without an authenticated session supplies a missing or blank term
- **THEN** the response has status 401 and contains no task data

### Requirement: Search term normalization
For an authenticated request, the system SHALL trim surrounding whitespace from
the term. For an authenticated request whose term is missing, empty, whitespace
only, or not a single string, the system SHALL return status 200 with an empty
`results` array.

#### Scenario: Missing or blank term returns no tasks
- **WHEN** an authenticated user supplies a missing, empty, or whitespace-only term
- **THEN** the response has status 200 and an empty `results` array

#### Scenario: Non-string term returns no tasks
- **WHEN** an authenticated request supplies a repeated `term` parameter
- **THEN** the response has status 200 and an empty `results` array

#### Scenario: Surrounding whitespace is ignored
- **WHEN** an authenticated user searches for a term with leading or trailing whitespace
- **THEN** the response contains the same set of results as the trimmed term

### Requirement: Search response shape
For a successful response, the system SHALL return a JSON object with a
`results` array whose entries contain exactly the task's `id` and `title`.

#### Scenario: Results contain only id and title
- **WHEN** a search returns matching tasks
- **THEN** each entry in `results` has exactly the keys `id` and `title`
