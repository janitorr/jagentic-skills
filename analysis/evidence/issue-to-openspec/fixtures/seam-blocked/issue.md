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
- Partner-level retry count, so each partner can choose three or five attempts
- The existing callers keep calling the same entry point

## Out of scope

- A durable queue or a scheduled replay job
- Partner-facing retry configuration
- Metrics dashboards

## Context

`src/notifications.py` has three call sites that share one sender. A previous
attempt added a retry loop inside `WebhookSender.send`; review rejected it
because each new sender subclass would reimplement the loop.
