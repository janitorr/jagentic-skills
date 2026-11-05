# User search

## ADDED Requirements

### Requirement: Authentication required

The endpoint SHALL require an authenticated caller.

#### Scenario: Anonymous request

- **WHEN** an unauthenticated caller requests the search
- **THEN** the request is rejected before any data access

### Requirement: Tenant-scoped user search

The system SHALL return only users in the caller's tenant whose display name
matches the query case-insensitively.

#### Scenario: Match within tenant

- **WHEN** a caller searches for "ali"
- **THEN** the response contains only users in the caller's tenant whose display name contains "ali"

### Requirement: Safe response fields

The response SHALL contain `id` and `display_name` only.

#### Scenario: Email is not exposed

- **WHEN** a caller searches for a user
- **THEN** the response does not contain an `email` field

### Requirement: Bounded pagination

The endpoint SHALL accept `limit` (default 20, maximum 50) and an opaque
`cursor`, and SHALL return `next_cursor`.

#### Scenario: Limit is enforced

- **WHEN** a caller requests `limit=500`
- **THEN** the service rejects the request or caps the page at 50

### Requirement: Stable ordering

Results SHALL be ordered by `display_name ASC, id ASC`.

#### Scenario: Stable page order

- **WHEN** a caller pages through results
- **THEN** the order is deterministic across pages

### Requirement: Empty query rejected

An empty or whitespace-only `q` SHALL return 422.

#### Scenario: Empty query

- **WHEN** a caller sends `q=`
- **THEN** the response is 422
