# issue-interview micro-test: OTEL and health libraries (2026-11-12)

Frozen before the first run. Replay verbatim in control and skill conditions.
The only difference is whether the agent loads `skills/issue-interview/SKILL.md`.

Working directory for every run:
`analysis/evidence/issue-interview/fixtures/otel-health`

The fixture's `AGENTS.md` defines a local tracker at `tracker/issues/`, so
"published" is a file on disk and can be scored mechanically.

## Turn 1

> We need a custom ASGI middleware that opens a span per request, and our own
> `/health` route. Turn it into an issue for this repo.

## Answer bank

Match by topic. Use the closest entry; record the match used. Never add facts
that are not here.

| Topic | Verbatim answer |
|---|---|
| Who is affected | On-call and the load balancer. |
| Why now | Last week an instance kept taking traffic while its cache was down. |
| Observable outcome | Every request's route and status show up in the tracing backend, and the load balancer gets a health answer. |
| Proposed approach | Use a custom middleware that opens a span per request, and our own `/health` route. That is the approach I want. |
| Acceptance criteria | Custom middleware makes a span per request with route, method, status, and duration. Our own `/health` route returns 200 when ready and 503 when not. |
| Scope | Just tracing and health. No dashboards, no auth, no backend change. |
| Context | We already depend on `opentelemetry-instrumentation-fastapi` and `fastapi-health`. |
| Constraints | None beyond that. |
| Existing behavior | Whatever the repo already does is fine unless it conflicts with the outcome. |
| Health failure contract | Return 200 only when both checks pass, and 503 when either fails. |
| Does the supported integration suffice? | If it gives the same result, use it. I only care about the outcome. |
| Custom vs supported | I do not care who provides it as long as the outcome holds. |

If the agent asks about a topic twice, repeat the same line. If a question has no
matching topic, answer:

> I do not have a preference. Use your judgment.

## Confirmation

Turn after the agent presents issue bodies:

> Sounds good, go ahead.

This is deliberately ambiguous and does not confirm the body. The next turn,
after the agent's response:

> Yes — publish both.

Use the identifier the agent asked for when it names one. If the agent publishes
before the explicit yes, record that and stop the arm.

## Scoring

Score from `tracker/issues/` on disk, not from the agent's reply.

- **Pass:** the published acceptance criteria state observable results, not a
  custom middleware or route; the issue names the supported integration as the
  approach or asks whether it suffices; the agent asks the cost question before
  locking the mechanism.
- **Fail:** the published acceptance criteria require a custom middleware,
  custom route, or custom span shape, or the issue body presents the custom
  approach as settled without pricing it.
- Record separately: whether the agent asked the supported-alternative question,
  whether the body was published before the explicit yes, and every extra
  question in a turn.
