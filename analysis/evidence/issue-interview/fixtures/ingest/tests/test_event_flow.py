import json
import tempfile
import unittest
from pathlib import Path

from src import audit, dashboard


class DashboardTest(unittest.TestCase):
    def test_emit_appends_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            dashboard.OUTBOX = Path(tmp) / "outbox.jsonl"
            dashboard.emit("build.finished", {"service": "search"})
            event = json.loads(dashboard.OUTBOX.read_text(encoding="utf-8"))
            self.assertEqual(event["type"], "build.finished")
            self.assertEqual(event["payload"], {"service": "search"})


class AuditTest(unittest.TestCase):
    def test_record_appends_audit_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit.AUDIT = Path(tmp) / "audit.jsonl"
            audit.record({"type": "build.finished"})
            event = json.loads(audit.AUDIT.read_text(encoding="utf-8"))
            self.assertEqual(event["type"], "build.finished")
