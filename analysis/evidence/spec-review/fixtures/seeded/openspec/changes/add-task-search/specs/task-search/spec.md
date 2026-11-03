## ADDED Requirements

### Requirement: Search returns matches
The system SHALL return tasks whose title contains the search term.

#### Scenario: Matching tasks are returned
- **WHEN** a user searches for a term present in two task titles
- **THEN** the system returns those two tasks and no others

### Requirement: Search stays fast
The system SHALL keep search fast as the number of tasks grows.
