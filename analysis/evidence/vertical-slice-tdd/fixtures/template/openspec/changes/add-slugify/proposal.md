## Why

Task titles need stable URL-safe identifiers.

## What Changes

- Add a `slugify(text)` function with a test-first implementation.

## Capabilities

### New Capabilities
- `slugify`: Convert task titles into URL-safe slugs.

### Modified Capabilities
None.

## Impact

- Adds `slugify` to `src/text.py` and tests in `tests/`.
