# task-search Specification

## Purpose
Allow users to find their tasks by title.

## Requirements

### Requirement: Search tasks by title
The system SHALL return tasks whose title contains the search term.

#### Scenario: Matching tasks are returned
- **WHEN** a user searches for a term present in two task titles
- **THEN** the system returns those two tasks and no others
