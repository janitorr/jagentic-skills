# slugify Specification

## Purpose
Provide URL-safe slugs for task titles.

## Requirements

### Requirement: Trim text
The system SHALL remove leading and trailing whitespace.

#### Scenario: Trim outer whitespace
- **WHEN** the input is `"  hello  "`
- **THEN** the result is `"hello"`
