"""Write dashboard events to the shared outbox."""

import json
from pathlib import Path

OUTBOX = Path("var/outbox.jsonl")


def emit(event_type: str, payload: dict) -> None:
    """Append one event to the outbox."""
    OUTBOX.parent.mkdir(parents=True, exist_ok=True)
    event = {"type": event_type, "payload": payload}
    with OUTBOX.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
