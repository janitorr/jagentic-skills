## ADDED Requirements

### Requirement: Slugify task titles
The system SHALL provide `slugify(text)` that lowercases the input, trims outer whitespace, replaces whitespace runs with one hyphen, and removes punctuation.

#### Scenario: Basic slug
- **WHEN** `slugify(" Hello, World! ")` is called
- **THEN** it returns `"hello-world"`

#### Scenario: Repeated whitespace
- **WHEN** `slugify("A  B")` is called
- **THEN** it returns `"a-b"`
