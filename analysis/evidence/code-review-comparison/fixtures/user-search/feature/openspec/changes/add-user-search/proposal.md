# Add user search

## Why

Support needs to find a user by name without exporting the tenant's user list.

## What Changes

- Add `GET /users/search`.
- Match on display name, not email.
- Return only `id` and `display_name`.
- Paginate with `limit` and `cursor`.
