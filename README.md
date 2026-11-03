# agentic-skills

A lab repo for comparing third-party agent skill bundles and synthesizing
new skills that combine the strongest ideas from each.

## Layout

```
vendor/     # upstream bundles, cloned (not tracked - see sync.sh)
analysis/   # category inventory, cross-bundle comparison, synthesis notes
skills/     # synthesized skills produced by the analysis
scripts/    # inventory generator
sync.sh     # clone/update every bundle listed in bundles.txt
bundles.txt # one "<name> <git-url>" per line
```

## Bundle workflow

1. List bundles in `bundles.txt`.
2. `./sync.sh` - clone or fast-forward each bundle into `vendor/`.
3. `python3 scripts/inventory.py` - regenerate `analysis/inventory.md`.
4. Compare bundles per category in `analysis/comparison.md`.
5. Record what was combined, and what was left out, in `analysis/synthesis.md`.

`scripts/inventory.py` has the authoritative category map. It exits non-zero if
a vendored skill is unmapped, so the inventory cannot silently go stale.

## Current synthesis

Five pipeline skills around OpenSpec, each invoked by `/command`:

| Stage | Skill | Output |
|---|---|---|
| 1 | `issue-interview` | GitHub issue(s) |
| 2 | `issue-to-openspec` | OpenSpec change (explore first, then propose) |
| 3 | `spec-review` | Read-only findings, then human gate |
| 4 | `vertical-slice-tdd` | Implemented tasks with test evidence |
| 5 | `code-review` | Read-only findings, then human gate |

The reviews never fix what they find; remediation is a separate pass after the
human reviews the report. Spec review hands off through the `ready-for-dev`
label, which the human sets after accepting the findings. Implementation commits
once per green slice.
