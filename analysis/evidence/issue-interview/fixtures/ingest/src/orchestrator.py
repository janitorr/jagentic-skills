"""Consume dashboard events."""

import json
from pathlib import Path

OUTBOX = Path("var/outbox.jsonl")


def handle(event: dict) -> None:
    """Handle one event."""
    raise NotImplementedError("orchestrator does not consume events yet")


def consume() -> None:
    """Read every event in the outbox and hand it to handle."""
    if not OUTBOX.exists():
        return
    with OUTBOX.open(encoding="utf-8") as stream:
        for line in stream:
            handle(json.loads(line))
