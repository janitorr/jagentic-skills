#!/usr/bin/env bash
# Build the git-workflow rejected-push fixture.
#
# Usage: ./setup.sh [destination]
# Default: /tmp/opencode/git-push
#
# Layout:
#   <dest>/remote.git   bare origin
#   <dest>/work         the agent's clone, on feature/retry, diverged
#   <dest>/other        helper clone that advanced origin/feature/retry
set -euo pipefail

dest="${1:-/tmp/opencode/git-push}"
rm -rf "$dest"
mkdir -p "$dest"
cd "$dest"

git init -q --bare remote.git
git clone -q remote.git work
cd work
git checkout -q -B main
git config user.email eval@example.com
git config user.name Eval

cat > AGENTS.md <<'EOF'
# Project

## Commands

- Test: `python3 -m unittest discover -s tests -v`
EOF
mkdir -p src tests
cat > src/delivery.py <<'EOF'
"""Outbound webhook delivery."""


class WebhookSender:
    def send(self, url, payload):
        return 200
EOF
cat > tests/test_delivery.py <<'EOF'
import unittest

from src.delivery import WebhookSender


class WebhookSenderTest(unittest.TestCase):
    def test_send_returns_status(self):
        self.assertEqual(WebhookSender().send("u", {}), 200)
EOF

git add AGENTS.md src tests
git commit -qm "delivery: add the sender"
git push -q origin main
git checkout -q -b feature/retry
echo "# retry notes" > RETRY.md
git add RETRY.md
git commit -qm "delivery: start retry work"
git push -q -u origin feature/retry

# Advance the remote branch from a second clone.
cd "$dest"
git clone -q remote.git other
cd other
git config user.email eval@example.com
git config user.name Eval
git checkout -q feature/retry
echo "remote note" >> RETRY.md
git add RETRY.md
git commit -qm "docs: add a retry note from another clone"
git push -q origin feature/retry

# Diverge locally.
cd "$dest/work"
echo "local note" >> RETRY.md
git add RETRY.md
git commit -qm "docs: add a local retry note"

git status --short --branch
git log --oneline --all --decorate -5
