#!/usr/bin/env python3
"""Regenerate analysis/inventory.md from the vendored skill bundles.

Categories are editorial, so they live in CATEGORIES below. Every SKILL.md
found under vendor/ must be mapped, or the script exits non-zero.
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"
OUT = ROOT / "analysis" / "inventory.md"

BUNDLE_LABELS = {
    "addyosmani-agent-skills": "addyosmani",
    "humanlayer-skills": "humanlayer",
    "mattpocock-skills": "mattpocock",
    "obra-superpowers": "superpowers",
}

CATEGORIES = {
    "Routing and setup": [
        "addyosmani-agent-skills/using-agent-skills",
        "mattpocock-skills/ask-matt",
        "mattpocock-skills/setup-matt-pocock-skills",
        "obra-superpowers/using-superpowers",
    ],
    "Intent, ideation, and interviews": [
        "addyosmani-agent-skills/interview-me",
        "addyosmani-agent-skills/idea-refine",
        "obra-superpowers/brainstorming",
        "mattpocock-skills/grilling",
        "mattpocock-skills/grill-me",
        "mattpocock-skills/grill-with-docs",
        "mattpocock-skills/loop-me",
        "mattpocock-skills/to-questionnaire",
        "mattpocock-skills/wait-what",
        "mattpocock-skills/prototype",
    ],
    "Spec and planning": [
        "addyosmani-agent-skills/spec-driven-development",
        "addyosmani-agent-skills/planning-and-task-breakdown",
        "mattpocock-skills/to-spec",
        "mattpocock-skills/to-tickets",
        "mattpocock-skills/wayfinder",
        "obra-superpowers/writing-plans",
        "humanlayer-skills/rpi",
        "addyosmani-agent-skills/doubt-driven-development",
    ],
    "Implementation": [
        "addyosmani-agent-skills/incremental-implementation",
        "mattpocock-skills/implement",
        "mattpocock-skills/implement-spec",
        "obra-superpowers/executing-plans",
    ],
    "Multi-agent orchestration": [
        "obra-superpowers/subagent-driven-development",
        "obra-superpowers/dispatching-parallel-agents",
        "mattpocock-skills/chief-of-staff",
        "mattpocock-skills/claude-handoff",
        "mattpocock-skills/handoff",
        "humanlayer-skills/build-iterated-agentic-loop",
        "humanlayer-skills/design-control-loop",
        "mattpocock-skills/software-factory",
    ],
    "Testing and debugging": [
        "addyosmani-agent-skills/test-driven-development",
        "mattpocock-skills/tdd",
        "obra-superpowers/test-driven-development",
        "obra-superpowers/verification-before-completion",
        "addyosmani-agent-skills/debugging-and-error-recovery",
        "mattpocock-skills/diagnosing-bugs",
        "obra-superpowers/systematic-debugging",
        "obra-superpowers/diagnosing-superpowers",
    ],
    "Review and quality gates": [
        "addyosmani-agent-skills/code-review-and-quality",
        "mattpocock-skills/code-review",
        "obra-superpowers/requesting-code-review",
        "obra-superpowers/receiving-code-review",
        "mattpocock-skills/pr",
        "humanlayer-skills/visual-pr",
        "addyosmani-agent-skills/constraint-driven-development",
    ],
    "Architecture and refactoring": [
        "addyosmani-agent-skills/api-and-interface-design",
        "mattpocock-skills/codebase-design",
        "mattpocock-skills/domain-modeling",
        "mattpocock-skills/improve-codebase-architecture",
        "addyosmani-agent-skills/code-simplification",
        "addyosmani-agent-skills/deprecation-and-migration",
        "mattpocock-skills/setup-ts-deep-modules",
        "mattpocock-skills/migrate-to-shoehorn",
    ],
    "Frontend and UI": [
        "addyosmani-agent-skills/frontend-ui-engineering",
        "addyosmani-agent-skills/browser-testing-with-devtools",
        "humanlayer-skills/narrow-react-prop-types",
    ],
    "Delivery, git, and repo hygiene": [
        "addyosmani-agent-skills/git-workflow-and-versioning",
        "obra-superpowers/using-git-worktrees",
        "obra-superpowers/finishing-a-development-branch",
        "addyosmani-agent-skills/ci-cd-and-automation",
        "addyosmani-agent-skills/shipping-and-launch",
        "mattpocock-skills/setup-pre-commit",
        "mattpocock-skills/git-guardrails-claude-code",
        "mattpocock-skills/triage",
    ],
    "Security, performance, and observability": [
        "addyosmani-agent-skills/security-and-hardening",
        "addyosmani-agent-skills/performance-optimization",
        "addyosmani-agent-skills/observability-and-instrumentation",
    ],
    "Docs, research, teaching, and visual explanation": [
        "addyosmani-agent-skills/documentation-and-adrs",
        "addyosmani-agent-skills/source-driven-development",
        "mattpocock-skills/research",
        "mattpocock-skills/retro",
        "mattpocock-skills/teach",
        "mattpocock-skills/writing-beats",
        "mattpocock-skills/writing-fragments",
        "mattpocock-skills/writing-shape",
        "humanlayer-skills/show-me",
    ],
    "Meta: skills, context, and agent docs": [
        "mattpocock-skills/writing-for-agents",
        "obra-superpowers/writing-skills",
        "addyosmani-agent-skills/context-engineering",
        "humanlayer-skills/improve-claude-md",
    ],
    "Misc utilities": [
        "mattpocock-skills/wizard",
        "mattpocock-skills/scaffold-exercises",
    ],
}


def frontmatter(text: str) -> dict:
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    if not match:
        return {}
    raw = match.group(1)
    try:
        return yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        parsed = {}
        for line in raw.splitlines():
            field = re.match(r"^(name|description):\s*(.*)$", line)
            if field:
                parsed[field.group(1)] = field.group(2).strip().strip("\"'")
        return parsed


def one_line(description: str, limit: int = 150) -> str:
    description = " ".join(str(description).split())
    if len(description) <= limit:
        return description
    cut = description[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"


def discover() -> dict[str, dict]:
    found = {}
    for path in sorted(VENDOR.glob("**/SKILL.md")):
        bundle = path.relative_to(VENDOR).parts[0]
        meta = frontmatter(path.read_text())
        name = meta.get("name") or path.parent.name
        found[f"{bundle}/{name}"] = {
            "bundle": bundle,
            "name": name,
            "description": one_line(meta.get("description", "")),
            "path": path.relative_to(ROOT),
        }
    return found


def main() -> int:
    found = discover()
    mapped = {key for keys in CATEGORIES.values() for key in keys}
    missing = sorted(set(found) - mapped)
    unknown = sorted(mapped - set(found))
    if missing or unknown:
        for key in missing:
            print(f"unmapped skill: {key}", file=sys.stderr)
        for key in unknown:
            print(f"unknown mapping: {key}", file=sys.stderr)
        return 1

    lines = [
        "# Skill inventory",
        "",
        f"{len(found)} skills across {len(BUNDLE_LABELS)} bundles, grouped by category.",
        "Generated by `scripts/inventory.py`; categories are editorial.",
        "",
        "| Bundle | Skills |",
        "|---|---:|",
    ]
    for bundle, label in BUNDLE_LABELS.items():
        count = sum(1 for item in found.values() if item["bundle"] == bundle)
        lines.append(f"| {label} | {count} |")

    for category, keys in CATEGORIES.items():
        lines += ["", f"## {category} ({len(keys)})", "", "| Skill | Bundle | What it does |", "|---|---|---|"]
        for key in keys:
            item = found[key]
            lines.append(
                f"| `{item['name']}` | {BUNDLE_LABELS[item['bundle']]} | {item['description']} |"
            )

    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(found)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
