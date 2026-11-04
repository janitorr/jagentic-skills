# Issue 17: Retry failed webhook deliveries

## Problem

Partner webhooks fail on transient network errors and 5xx responses. The event is
lost, and the partner never receives it. Support currently replays these by hand.

## Outcome

A transient failure is retried automatically and succeeds without support
involvement. A permanent failure (4xx) is not retried.

## In scope

- Up to three attempts per delivery
- Exponential backoff between attempts
- Retry on network errors and 5xx only
- The existing callers keep calling the same entry point

## Out of scope

- A durable queue or a scheduled replay job
- Partner-facing retry configuration
- Metrics dashboards

## Acceptance criteria

- [ ] A delivery that fails with a 5xx three times is reported to the caller as failed
- [ ] A delivery that fails once with a 5xx and then succeeds reports success
- [ ] A 4xx response fails immediately with no second attempt
- [ ] Callers do not change their call shape
- [ ] Existing tests pass

## Context

`src/notifications.py` has three call sites that share one sender. A previous
attempt added a retry loop inside `WebhookSender.send`; review rejected it
because each new sender subclass would reimplement the loop.
