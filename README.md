# jagentic-skills

A lab repo for comparing third-party agent skill bundles and synthesizing
new skills that combine the strongest ideas from each.

## Layout

```
vendor/          # upstream bundles, cloned (not tracked - see sync.sh)
analysis/        # category inventory, cross-bundle comparison, synthesis notes
skills/          # synthesized skills, the source of truth
.opencode/skills # installed copies OpenCode discovers (generated)
scripts/         # inventory generator and skill sync
sync.sh          # clone/update every bundle listed in bundles.txt
bundles.txt      # one "<name> <git-url>" per line
```

## Bundle workflow

1. List bundles in `bundles.txt`.
2. `./sync.sh` - clone or fast-forward each bundle into `vendor/`.
3. `python3 scripts/inventory.py` - regenerate `analysis/inventory.md`.
4. Compare bundles per category in `analysis/comparison.md`.
5. Record what was combined, and what was left out, in `analysis/synthesis.md`.
6. `./scripts/sync-skills.sh` - copy `skills/` into `.opencode/skills/` after
   adding or editing a skill.

`skills/` is the source of truth. `.opencode/skills/` is a generated mirror that
OpenCode discovers; do not edit it directly.

`scripts/inventory.py` has the authoritative category map. It exits non-zero if
a vendored skill is unmapped, so the inventory cannot silently go stale.

Evaluation status and the plan for resuming it: `analysis/evidence/README.md`.
`spec-review` and `vertical-slice-tdd` have partial behavioral evidence; the other
eight are unverified.

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
| `visual-explainer` | Diagrams and focused artifacts instead of prose walls |
| `deep-module-design` | Interfaces, seams, simplification, and migration |
| `skill-forge` | Authoring and revising skills against a baseline failure |
| `git-workflow` | Commits, branches, worktrees, conflicts, finishing, releases |
| `documentation` | ADRs, READMEs, reference pages, changelogs, and agent instructions |

The reviews never fix what they find; remediation is a separate pass after the
human reviews the report. Spec review hands off through the approval marker the
agent file defines (for example, a `ready-for-dev` label). Implementation commits
once per green slice.

Skills are environment-agnostic. An agent file supplies the tracker operations,
approval marker, review destination, and workspace policy; the same skill can run
locally or inside a GitHub workflow.
