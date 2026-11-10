# Event flow

1. The dashboard writes an event to `var/outbox.jsonl`.
2. The orchestrator is meant to read the outbox, call `handle(event)`, and write
   an audit line with `audit.record(event)`.
3. `Orchestrator.handle` is still a stub, so the dashboard-to-orchestrator path
   is not wired.
4. There is no replay tool; events stay in the outbox until the orchestrator
   handles them.

The outbox currently holds about 12,000 events from the last two weeks. This
checkout contains a small sample.
