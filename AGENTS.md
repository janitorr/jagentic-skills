# AGENTS.md

Lab for comparing third-party agent skill bundles and synthesizing new skills
from the strongest parts. Markdown skills, Python 3 with PyYAML, and Bash.
OpenSpec is the fixed artifact system for the synthesized pipeline.

## Project map

- `analysis/` - inventory, comparison, synthesis, coverage, and eval evidence.
- `docs/` - workflow state machine and GitHub mapping.
- `skills/` - source of truth for the ten synthesized skills.
- `.opencode/skills/` - generated mirror OpenCode discovers.
- `scripts/` - inventory generator and skill sync.
- `vendor/` - cloned upstream bundles, untracked, never edited.
- `bundles.txt` and `sync.sh` - upstream bundle list and sync.

`skills/` is the source of truth. `.opencode/skills/` is generated; do not edit
it directly.

## Commands

| Command | What it does |
|---|---|
| `./sync.sh` | Clone or fast-forward every bundle in `bundles.txt` into `vendor/`. |
| `python3 scripts/inventory.py` | Regenerate `analysis/inventory.md` from `vendor/`. Fails if a skill is unmapped. |
| `./scripts/sync-skills.sh` | Copy `skills/` into `.opencode/skills/`. |

## Git commit messages

Follow `git-workflow`. Use `<area>: <imperative, lowercase summary>` with areas
`skills`, `workflow`, `analysis`, `docs`, `scripts`, `eval`. The body explains
why.

## When adding or changing a synthesized skill

- Edit `skills/<skill-id>/SKILL.md`, then run `./scripts/sync-skills.sh`.
- Follow the `skill-forge` skill. A behavior-shaping change needs a baseline or
  micro-test record, or an explicit debt note in `analysis/evidence/README.md`.
- Keep skills environment-agnostic. Tracker operations, the approval marker, the
  review destination, and workspace/push policy belong to agent files, not
  skills. OpenSpec remains fixed.
- Update `README.md` and `analysis/synthesis.md` when the skill set or boundary
  changes.

## When adding or updating a vendored bundle

- Add the name and URL to `bundles.txt`, then run `./sync.sh`.
- Never edit files under `vendor/`; they are upstream copies.
- Map every new skill in `scripts/inventory.py`, then rerun the inventory. The
  script exits non-zero until the mapping is complete.

## When updating the analysis

- Categories are editorial and live in `scripts/inventory.py`; `analysis/inventory.md`
  is generated, not hand-edited.
- `analysis/comparison.md` is a historical cross-bundle comparison.
  `analysis/synthesis.md` and `analysis/coverage.md` describe the current set.
- Keep claims traceable to a vendored file, the repo, or recorded evidence.

## When changing stage routing or loop rules

- Update `docs/workflow.md` for transitions, owners, and GitHub artifacts.
- Keep `routing_status`, `owner`, and `requested_action` semantic in skills. Do
  not hardcode labels, `gh` commands, or PR review mechanics there.
- If a skill's interaction contract changes, run `./scripts/sync-skills.sh` and
  record evidence or debt in `analysis/evidence/README.md`.

## When running an eval

- Read `analysis/evidence/README.md` first. It records what is verified, why
  evals are paused, and how to resume.
- One skill at a time, per `skill-forge`. Do not batch untested skills.
- Do not present an unverified skill as passing. Eight of the ten have no
  behavioral evidence.
