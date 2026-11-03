# Issue 7: Add slugify

## Problem
Task titles need stable URL-safe identifiers.

## Outcome
`slugify(text)` returns a lowercase, hyphen-separated slug with punctuation removed.

## In scope
- Lowercase
- Trim
- Whitespace runs become one hyphen
- Remove punctuation

## Out of scope
- Unicode transliteration
- Uniqueness checks

## Acceptance criteria
- [ ] `slugify(" Hello, World! ")` returns `hello-world`
- [ ] `slugify("A  B")` returns `a-b`
