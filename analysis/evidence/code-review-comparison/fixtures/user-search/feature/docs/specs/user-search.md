# User search

`GET /users/search?q=&limit=&cursor=`

- Authentication is required. Results are limited to the caller's tenant.
- `q` matches `display_name` case-insensitively. An empty or whitespace-only
  `q` returns 422.
- Return `id` and `display_name` only. Never return `email`.
- `limit` defaults to 20 and must not exceed 50. Order by
  `display_name ASC, id ASC`. Return an opaque `next_cursor`.
