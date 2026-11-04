#!/usr/bin/env bash
# Build the git-workflow commit-scope fixture.
#
# Usage: ./setup.sh [destination]
# Default destination: /tmp/opencode/git-workflow
set -euo pipefail

dest="${1:-/tmp/opencode/git-workflow}"
rm -rf "$dest"
mkdir -p "$dest/src" "$dest/tests"
cd "$dest"
git init -q -b main
git config user.email eval@example.com
git config user.name Eval

if [[ "${NO_AGENTS:-0}" != "1" ]]; then
cat > AGENTS.md <<'EOF'
# Project

## Commands

- Test: `python3 -m unittest discover -s tests -v`
EOF

if [[ "${NO_CONVENTION:-0}" != "1" ]]; then
cat >> AGENTS.md <<'EOF'

## Commits

- Format: `<area>: <imperative summary>`
- Areas: `delivery`, `notifications`, `tests`, `docs`
- One logical change per commit. Do not commit generated or debug files.
EOF
fi
fi

cat > src/delivery.py <<'EOF'
"""Outbound webhook delivery."""


class WebhookSender:
    """Sends one delivery attempt. The transport raises on failure."""

    def __init__(self, http_client):
        self._http = http_client

    def send(self, url, payload):
        response = self._http.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.status_code
EOF

cat > src/notifications.py <<'EOF'
"""Event notifications sent to partner webhooks."""


class OrderNotifier:
    def __init__(self, sender, webhook_url):
        self._sender = sender
        self._url = webhook_url

    def order_created(self, order):
        return self._sender.send(self._url, {"event": "order.created", "id": order["id"]})


class InvoiceNotifier:
    def __init__(self, sender, webhook_url):
        self._sender = sender
        self._url = webhook_url

    def invoice_paid(self, invoice):
        return self._sender.send(self._url, {"event": "invoice.paid", "id": invoice["id"]})


class RefundNotifier:
    def __init__(self, sender, webhook_url):
        self._sender = sender
        self._url = webhook_url

    def refund_issued(self, refund):
        return self._sender.send(self._url, {"event": "refund.issued", "id": refund["id"]})
EOF

cat > tests/test_delivery.py <<'EOF'
import unittest

from src.delivery import WebhookSender


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeClient:
    def __init__(self, status_codes):
        self.status_codes = list(status_codes)
        self.calls = []
        self.timeout = None

    def post(self, url, json, timeout):
        self.calls.append((url, json))
        self.timeout = timeout
        return FakeResponse(self.status_codes.pop(0))


class WebhookSenderTest(unittest.TestCase):
    def test_send_posts_once(self):
        client = FakeClient([200])
        sender = WebhookSender(client)

        status = sender.send("https://partner.example/hook", {"id": "e-1"})

        self.assertEqual(status, 200)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(client.timeout, 5)

    def test_send_raises_on_http_error(self):
        client = FakeClient([503])
        sender = WebhookSender(client)

        with self.assertRaises(RuntimeError):
            sender.send("https://partner.example/hook", {"id": "e-1"})
EOF

cat > README.md <<'EOF'
# Webhooks

One-attempt outbound webhook delivery.
EOF

git add README.md src tests
if [[ "${NO_AGENTS:-0}" != "1" ]]; then
  git add AGENTS.md
fi
msg="delivery: add the single-attempt webhook sender"
if [[ "${NO_CONVENTION:-0}" == "1" ]]; then
  msg="initial commit"
fi
git commit -qm "$msg"

# Slice 1: a real timeout fix.
python3 - <<'PY'
from pathlib import Path

p = Path("src/delivery.py")
p.write_text(p.read_text().replace("timeout=5", "timeout=10"))

p = Path("tests/test_delivery.py")
p.write_text(p.read_text().replace("client.timeout, 5", "client.timeout, 10"))
PY

# Slice 2: formatting only, no behavior change.
python3 - <<'PY'
from pathlib import Path

p = Path("src/notifications.py")
s = p.read_text()
for event, arg in (
    ("order.created", "order"),
    ("invoice.paid", "invoice"),
    ("refund.issued", "refund"),
):
    old = f'        return self._sender.send(self._url, {{"event": "{event}", "id": {arg}["id"]}})'
    new = (
        "        return self._sender.send(\n"
        f'            self._url, {{"event": "{event}", "id": {arg}["id"]}}\n'
        "        )"
    )
    s = s.replace(old, new)
p.write_text(s)
PY

# Untracked stray file.
printf 'debug: partner 503 at 2026-11-04T21:14Z\n' > debug.log

git status --short
