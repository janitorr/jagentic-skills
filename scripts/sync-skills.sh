#!/usr/bin/env bash
# Copy the synthesized skills into the project directory OpenCode discovers.
# Source of truth: skills/. Generated mirror: .opencode/skills/.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p .opencode/skills
cp -R skills/. .opencode/skills/
echo "synced $(find skills -name SKILL.md | wc -l) skills to .opencode/skills"
