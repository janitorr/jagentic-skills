"""Write orchestrator audit lines."""

import json
from pathlib import Path

AUDIT = Path("var/audit.jsonl")


def record(event: dict) -> None:
    """Append one audit line."""
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
