# Quality checks

Apply these while reviewing the Quality axis. They are prompts, not a second
standards document: the target repo's rules override them, and skip anything
tooling already enforces. Name the check in the finding.

## Security

- **Injection.** SQL, NoSQL, shell, template, and log injection. User input is
  parameterized or escaped; no f-string, `%`, or concatenated query.
- **Authentication.** Every route or handler has the auth guard; anonymous
  access fails closed.
- **Authorization.** Check the specific resource, not just authentication.
  Tenant and owner scope on every read and write; no IDOR.
- **Input boundary.** Validate type, shape, length, enum, and format where
  external data enters. Treat third-party responses, files, and model output as
  untrusted.
- **Secrets.** None in code, logs, errors, or the diff. Configuration comes from
  the environment.
- **PII.** No email addresses, names, tokens, or raw query text in logs or
  responses. Return only the fields the contract allows.
- **Errors.** Generic to the caller; details and stack traces stay in server
  logs.
- **Dependencies.** New or upgraded packages: known advisories, maintenance,
  licence, install scripts, and lockfile diff.
- **Destructive paths.** Allowlisted root, resolved target, minimum depth, and
  ownership evidence before a delete, move, or overwrite.
- **SSRF.** User-influenced URLs: allowlist scheme and host, reject private and
  reserved addresses, and disable redirects.

## Performance

- **N+1.** A query or remote call inside a loop over rows; batch or join it.
- **Unbounded work.** List endpoints paginate with a stable order and enforce a
  limit; no full-table scan driven by user input.
- **Index use.** Leading-wildcard `LIKE`, a function on an indexed column, or a
  low-selectivity predicate needs a query plan. Do not add an index without
  `EXPLAIN` before and after.
- **Hot path.** Large allocations, repeated serialization, and synchronous work
  that belongs off the request path.
- **Caching.** Cache expensive, read-heavy data only. The key includes every
  input that changes the response; state the staleness window and invalidation.
- **Connection pools.** One per process, sized under the database ceiling; do
  not raise the pool to hide a leak.
- **Verification.** An optimization needs a before/after measurement beyond
  noise, or it is reverted.

## Reporting

For each hit, name the check, quote the line, state the impact, and give a fix
direction. A check that does not apply is not a finding; do not invent one.
