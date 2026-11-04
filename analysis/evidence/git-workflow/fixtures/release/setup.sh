#!/usr/bin/env bash
# Build the git-workflow release/tagging fixture.
#
# Usage: ./setup.sh [destination]
# Default: /tmp/opencode/git-release
#
# The repo has a released 1.2.3, an unreleased retry feature, no commit
# convention, and a neutral history.
set -euo pipefail

dest="${1:-/tmp/opencode/git-release}"
rm -rf "$dest"
mkdir -p "$dest/src" "$dest/tests"
cd "$dest"
git init -q -b main
git config user.email eval@example.com
git config user.name Eval

cat > AGENTS.md <<'EOF'
# Project

## Commands

- Test: `python3 -m unittest discover -s tests -v`
EOF

cat > pyproject.toml <<'EOF'
[project]
name = "webhooks"
version = "1.2.3"
EOF

cat > CHANGELOG.md <<'EOF'
# Changelog

## [Unreleased]

## [1.2.3] - 2026-10-01

### Fixed

- Raise on a non-2xx response instead of returning it.
EOF

cat > src/delivery.py <<'EOF'
"""Outbound webhook delivery."""


class WebhookSender:
    def __init__(self, http_client):
        self._http = http_client

    def send(self, url, payload):
        response = self._http.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.status_code
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

    def post(self, url, json, timeout=None):
        self.calls.append((url, json))
        return FakeResponse(self.status_codes.pop(0))


class WebhookSenderTest(unittest.TestCase):
    def test_send_posts_once(self):
        client = FakeClient([200])
        sender = WebhookSender(client)

        self.assertEqual(sender.send("https://partner.example/hook", {"id": "e-1"}), 200)
        self.assertEqual(len(client.calls), 1)
EOF

git add AGENTS.md pyproject.toml CHANGELOG.md src tests
git commit -qm "initial commit"
git tag -a v1.2.3 -m "v1.2.3"

# Unreleased feature: retry once on 503.
cat > src/delivery.py <<'EOF'
"""Outbound webhook delivery."""


class WebhookSender:
    def __init__(self, http_client):
        self._http = http_client

    def send(self, url, payload):
        last = None
        for _ in range(2):
            try:
                response = self._http.post(url, json=payload, timeout=5)
                response.raise_for_status()
                return response.status_code
            except RuntimeError as exc:
                last = exc
        raise last
EOF

cat > tests/test_retry.py <<'EOF'
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

    def post(self, url, json, timeout=None):
        self.calls.append((url, json))
        return FakeResponse(self.status_codes.pop(0))


class RetryTest(unittest.TestCase):
    def test_retries_once_on_503(self):
        client = FakeClient([503, 200])
        sender = WebhookSender(client)

        self.assertEqual(sender.send("https://partner.example/hook", {"id": "e-1"}), 200)
        self.assertEqual(len(client.calls), 2)
EOF

git add src/delivery.py tests/test_retry.py
git commit -qm "Add retry on transient failures"

git log --oneline --decorate
git tag -n
