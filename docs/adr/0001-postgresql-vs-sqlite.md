# ADR 0001: PostgreSQL vs SQLite

- Status: proposed
- Date: 2026-11-12
- Scope: any service or tool in this project that adds a relational store

## Context

There is no database decision on record yet. This ADR sets a default for a
service that needs a relational store and names the conditions under which the
default stops applying.

Assumptions, unconfirmed. The decision changes if they do:

- One deployable application instance owns the data.
- Peak concurrent writers are few and writes are not the bottleneck.
- The host provides durable local disk that survives restarts and redeploys.
- There is no requirement for managed high availability, point-in-time
  recovery, or cross-region replication.
- A small team operates the system; operational simplicity outranks raw
  throughput.
- The data fits comfortably on one node.

The forces that matter are not SQL features. They are the operating model:
latency and deployment simplicity favor an in-process database; concurrency,
availability, and independent scaling favor a client/server database.

## Decision

Use SQLite by default. Move to PostgreSQL only when one of these triggers is
observed, not merely anticipated:

- A second application instance must read and write the same data.
- Write contention appears in production: sustained lock waits or write latency
  that a single writer cannot absorb.
- The host cannot guarantee durable local disk, for example an ephemeral
  container filesystem or a serverless platform.
- Operations require managed failover, point-in-time recovery, or read
  replicas.
- The workload needs a PostgreSQL-only capability: an extension such as PostGIS
  or pgvector, row-level security, logical replication, or `LISTEN`/`NOTIFY`.
- Data or query volume outgrows one node.

Until a trigger fires, do not run PostgreSQL for anticipated scale.

## Alternatives considered

- **PostgreSQL from the start.** Rejected for now, not permanently. It adds a
  server, a network hop, connection pooling, backups, upgrades, and monitoring
  before the workload requires them. Revisit when a trigger above fires.
- **SQLite with no migration path.** Rejected. It forces an emergency migration
  under load. Keep the schema portable and the data-access layer free of
  SQLite-specific behavior where doing so is cheap.
- **MySQL or MariaDB.** Rejected. No advantage over PostgreSQL for this
  workload, and a smaller extension ecosystem.
- **A document or key-value store.** Rejected. The data is relational and needs
  transactions and joins.

## Consequences

Positive:

- No network hop, no database server to operate, and one file to back up.
- Local development and tests use the same engine as production.
- Deployments stay small; there is no connection pool or server tuning to own.

Negative:

- SQLite allows one writer at a time. WAL mode permits concurrent readers, but
  write throughput has a ceiling.
- There is no built-in replication, failover, or point-in-time recovery;
  continuity depends on external backup tooling.
- The database file must sit on durable local disk, which rules out many
  serverless and multi-instance deployments.
- Some schema changes require rebuilding a table, because SQLite cannot change
  a column's type or constraints in place.

Follow-ups:

- Enable WAL mode, a busy timeout, and foreign-key enforcement on every
  connection.
- Back up with the SQLite backup API or a continuous replication tool such as
  Litestream, and verify a restore. Copying a live database file is not a safe
  backup.
- Keep migrations within SQLite's `ALTER TABLE` limits.
- Review these triggers when load, deployment topology, or availability
  requirements change.

## References

- SQLite, "Appropriate Uses For SQLite": https://www.sqlite.org/whentouse.html
- SQLite, "Write-Ahead Logging": https://www.sqlite.org/wal.html
- SQLite, "ALTER TABLE": https://www.sqlite.org/lang_altertable.html
- PostgreSQL documentation: https://www.postgresql.org/docs/current/
