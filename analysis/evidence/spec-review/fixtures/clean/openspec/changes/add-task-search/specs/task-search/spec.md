## ADDED Requirements

### Requirement: Search returns matches
The system SHALL return tasks whose title contains the search term.

#### Scenario: Matching tasks are returned
- **WHEN** a user searches for a term present in two task titles
- **THEN** the system returns those two tasks and no others

### Requirement: Search is scoped to the authenticated user
The system SHALL return only tasks owned by the authenticated user.

#### Scenario: Another user's tasks are excluded
- **WHEN** a user searches for a term that also appears in another user's task
- **THEN** the response excludes the other user's task
