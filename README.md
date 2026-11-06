# jagentic-skills

A lab repo for comparing third-party agent skill bundles and synthesizing
new skills that combine the strongest ideas from each.

## Layout

```
vendor/          # upstream bundles, cloned (not tracked - see sync.sh)
analysis/        # inventory, comparison, synthesis, coverage, and eval evidence
docs/            # stage graph, verdicts, and delivery mapping
skills/          # synthesized skills, the source of truth
.opencode/skills # installed copies OpenCode discovers (generated)
scripts/         # inventory generator and skill sync
sync.sh          # clone/update every bundle listed in bundles.txt
bundles.txt      # one "<name> <git-url>" per line
```

## Prerequisites

- git and bash
- Python 3 with PyYAML

Contributing: see `AGENTS.md`.

## Bundle workflow

1. List bundles in `bundles.txt`.
2. `./sync.sh` - clone or fast-forward each bundle into `vendor/`.
3. `python3 scripts/inventory.py` - regenerate `analysis/inventory.md`.
4. Read `analysis/comparison.md` for the historical cross-bundle comparison;
   record the current comparison in `analysis/synthesis.md` and
   `analysis/coverage.md`.
5. `./scripts/sync-skills.sh` - copy `skills/` into `.opencode/skills/` after
   adding or editing a skill.

`skills/` is the source of truth. `.opencode/skills/` is a generated mirror that
OpenCode discovers; do not edit it directly.

`scripts/inventory.py` has the authoritative category map. It exits non-zero if
a vendored skill is unmapped, so the inventory cannot silently go stale.

Evaluation status and the plan for resuming it: `analysis/evidence/README.md`.

## Current synthesis

Five pipeline skills around OpenSpec, invoked by whatever command or workflow the
environment uses:

| Stage | Skill | Output |
|---|---|---|
| 1 | `issue-interview` | Issue(s) in the configured tracker |
| 2 | `issue-to-openspec` | OpenSpec change (explore first, then propose) |
| 3 | `spec-review` | Read-only findings, then human gate |
| 4 | `vertical-slice-tdd` | Implemented tasks with test evidence |
| 5 | `code-review` | Read-only findings, then human gate |

Supporting skills, callable at any point:

| Skill | Owns |
|---|---|
| `visual-explainer` | Diagrams and self-contained one-pagers instead of prose walls |
| `deep-module-design` | Interfaces, seams, simplification, and migration |
| `skill-forge` | Authoring and revising skills against a baseline failure |
| `git-workflow` | Commit slicing and shape, conflicts, rejected pushes, releases and tags; invariants plus defaults |
| `documentation` | ADRs, READMEs, reference pages, changelogs and release notes, agent instructions, onboarding guides, runbooks, and how-to docs |
| `ci-cd` | CI/CD pipelines: build once, promote, gate, verify, and roll back |

Reviewers never fix what they find. The owning stage may rework findings
agent-to-agent; human approval and merge sign-off remain fixed gates. A design
issue at human review reopens the spec and invalidates the approval marker, so
implementation waits for a new one. Spec review hands off through the approval
marker the agent file defines (for example, a `ready-for-dev` label).
Implementation commits once per green slice.

Stage skills are environment-agnostic. An agent file supplies the tracker
operations, approval marker, review destination, and workspace policy; the same
skill can run locally or inside a GitHub workflow. Supporting skills are invoked
directly by a human or an agent mid-task and need no agent file. The stage graph,
verdict semantics, and delivery mapping live in `docs/workflow.md`.

Each stage skill ends with a verdict — `pass`, `needs_revision`, or `blocked` —
and a one-line reason. It does not name the next stage or a tracker operation;
the persona's agent file maps the verdict to comments, labels, commits, and pull
requests.
