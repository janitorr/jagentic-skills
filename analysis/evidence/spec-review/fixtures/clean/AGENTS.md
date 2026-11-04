# Project instructions

## Commands
- Test: `node --test`
- Build: `node --check src/app.js && node --check src/api.js && node --check src/auth.js && node --check src/search.js`

## Conventions
- Every search endpoint requires authentication.
- Search results are scoped to the authenticated user.
