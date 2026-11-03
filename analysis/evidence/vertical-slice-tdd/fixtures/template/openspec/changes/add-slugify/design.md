## Context

`src/text.py` already provides `trim`. `slugify` is missing.

## Decisions

- Implement `slugify` in `src/text.py`.
- Use a regular expression to collapse whitespace and strip punctuation.

## Risks

- Unicode input is out of scope for this change.
