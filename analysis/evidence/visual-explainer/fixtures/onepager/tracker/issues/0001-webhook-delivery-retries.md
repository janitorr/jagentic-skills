## Problem

Outbound webhook delivery makes exactly one HTTP attempt (`src/delivery.py`, `WebhookSender.send`). A partner timeout, 429, or 5xx therefore loses the event: the error propagates and nothing retries. Support only learns about the loss when the partner reports a missing event, then replays it by hand. The same single-attempt path carries `order.created`, `invoice.paid`, and `refund.issued` (`src/notifications.py`).

## Outcome

Transient partner failures recover without human involvement. An event that succeeds on a later attempt is never seen as missing by the partner, and support stops replaying those events.

## In scope

- Retry inside `WebhookSender.send`, so all three notifiers inherit it unchanged.
- Retry on request timeout, HTTP 429, and HTTP 5xx.
- Four total attempts per delivery, exponential backoff of roughly 1s, 2s, 4s.
- Synchronous execution: the caller waits through the retry window, bounded at roughly 7 seconds before the final result.
- On final failure, one structured error log carrying the event id, target URL, and last status, then re-raise the last error.
- Unit tests for the retry path, and updates to existing tests that assume a single attempt.

## Out of scope

- Durable queue, event store, or any persistence of pending deliveries.
- Surviving a process crash, restart, or deploy: events mid-retry at that moment are still lost.
- Scheduled or automatic later replay after the retry window expires.
- Dead-letter store, dashboard, alerting, or metrics.
- Partner-facing retry configuration or per-partner policies.
- Idempotency on the receiving side; the payload already carries an event id and at-least-once duplicates are accepted.
- Changing which events are sent, or any notifier's payload shape.

## Acceptance criteria

- [ ] A delivery that returns 503, 429, or times out, then succeeds on a later attempt, returns that success status and the partner receives the event.
- [ ] A delivery that keeps failing uses at most four total attempts with backoff approximating 1s/2s/4s.
- [ ] A 4xx other than 429 is attempted once and raises immediately, with no retry.
- [ ] After the final attempt fails, exactly one structured error is logged containing the event id, URL, and last status, and the last error is re-raised.
- [ ] `OrderNotifier`, `InvoiceNotifier`, and `RefundNotifier` are unchanged and their deliveries go through the retry path.
- [ ] `python3 -m unittest discover -s tests -v` passes; the existing 503 test is updated to supply four failing responses, and new tests cover success-after-retry, exhaustion, 429, and no-retry on 400.

## Context

- `src/delivery.py` — single POST, 5-second timeout, `raise_for_status()`, no retry or logging.
- `src/notifications.py` — three notifiers sharing the one sender.
- `tests/test_delivery.py` — `test_send_posts_once` and `test_send_raises_on_http_error`; the latter supplies one status code and will need four.
- No issue template exists in this repo; default sections are used.

## Open questions

- Long partner outages still exceed the retry window, so those events remain manually replayable via the logged event id. Accepted as the residual, decided by you in this interview.
- Backoff values are approximate; whoever implements may adjust them within the four-attempt bound without reopening scope.
