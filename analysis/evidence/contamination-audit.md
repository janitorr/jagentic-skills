# Contamination audit: earlier skill evals

Status: **first pass, static**. The CI/CD test exposed several cue classes that
can change agent behavior. This file records which earlier evidence files show
them and what to re-run. It does not claim the results are wrong; it records
exposure. The actionable list is in `docs/open-tasks.md`.

## Cue classes

1. Eval words in agent IDs or system prompts (`eval-*`, "evaluation control").
2. Condition words in task text (`control`, `treatment`, "no skill").
3. Fixture or condition names in paths (`cr-clean`, `cr-seeded`,
   `/tmp/opencode/eval/...`, `/tmp/opencode/debug-loop/run-N`).
4. Sibling runs visible in one parent directory.
5. The lab, evidence, or skill source visible to the agent.
6. Capability grants or research hints a real request would not give
   ("you may consult the official docs").
7. Trigger selectors with filesystem access.

Capability asymmetry is separate from contamination: a control told "do not load
any skill" is not the agent's default behavior. It measures the target skill
against a bare agent, not against the agent's normal toolkit.

## Risk table

| Evidence | Cue observed | Risk | Re-run? |
|---|---|---|---|
| `trigger-tests.md` | live selectors had repo access; one run found the lab today | High | Yes, with `trigger-selector` (skill tool only) |
| `skill-forge-stop-rule.md` | `eval-skill-control` and `eval-skill-treatment`; system prompts said "evaluation" | High | Yes, neutral agents |
| `debug-loop.md` | `eval-debug-control`; `/tmp/opencode/debug-loop/...`; evaluation system prompt | High | Yes, on a real codebase; synthetic fixtures are already too easy |
| `code-review.md` | `/tmp/opencode/cr-clean` and `cr-seeded`; the path names the answer | High | Yes, neutral paths |
| `issue-interview.md` | control told "do not load any skill"; canned script; `/tmp/opencode/issue-interview/` | High | Yes, gate and publish subset |
| `spec-review.md` | control prompt: "Do not load, read, or follow any..."; condition labels | High | Yes, verdict subset |
| `vertical-slice-tdd.md` | five control vs five treatment; control "loaded no skills" | High | Yes, gate and verdict subset |
| `issue-to-openspec.md` | control "no skill files"; skill "load the skill"; `/tmp/opencode/ito` | High | Yes, blocked/gate subset |
| `deep-module-design.md` | control "do not load any skill"; treatment "load the skill" | High | Yes, design-quality subset |
| `api-contract-design.md` | control told explicitly to load no skill | High | Only if the HTTP gap is revisited |
| `codebase-design-vs-deep-module-design.md` | source copied to `/tmp/opencode/eval/...`; arms from v2 | High | Exploratory; lower priority |
| `code-review-comparison.md` | `/tmp/opencode/cr-compare/seeded`; arms loaded different skills | High | Exploratory; lower priority |
| `documentation.md` | treatment/control labels; told not to inspect the filesystem | Medium | Shape probe with neutral prompts |
| `git-workflow.md` | control/skill tables; condition prompts likely | Medium | Commit-split pressure subset |
| `visual-explainer.md` | control / `visual-explainer` / `show-me` arms | Medium | Shape probe |
| `documentation-vs-writing-for-agents.md` | control and named arms | Medium | Shape comparison |
| `context-engineering-external.md` | conditions `control`, `skill`, `primed`; the skill prompt intentionally loads the skill | Medium | Metrics only; lower priority |
| `cicd.md` clean phase | neutral agents, random roots, no doc cue, no-read rule | Low | Done |

## Priority

1. **Trigger tests.** Routing is used by every skill. Re-run the 105 proxy and
   live prompts with `trigger-selector`, which has only the `skill` tool.
2. **`skill-forge-stop-rule`.** The meta-skill's stop rule was shaped by a test
   whose agents were named `eval-*` and told they were controls.
3. **`code-review`.** The `cr-seeded` path is a direct answer leak.
4. **The gate and verdict evals:** `spec-review`, `vertical-slice-tdd`,
   `issue-to-openspec`, `issue-interview`. Their conclusions drive the workflow.
5. **The design-quality evals:** `deep-module-design`, `api-contract-design`.
6. **The shape evals:** `documentation`, `git-workflow`, `visual-explainer`.
7. **The exploratory comparisons.** Lower value; re-run only if the conclusion
   is contested.

## Clean re-run method

- Neutral agent IDs and system prompts: a role, not a condition.
- One random root per run; no sibling runs; explicit no-read rule.
- Control: do not say "no skills." Let the agent use its normal judgment; deny
  the target skill silently if the harness needs to. The baseline is the
  agent's default, not a bare agent.
- Treatment: "use this skill," never "treatment."
- No doc or research hints unless the skill itself provides them.
- Trigger selectors: only the `skill` tool.
- Pin the model and variant; record the agent ID, system prompt, path, and model
  in the evidence file.
- Score from disk, not from the agent's self-report.

## What this audit cannot tell

Whether a cue changed the outcome. That needs the transcripts. The local
OpenCode store has the sessions; next session, extract the system prompt and
tool calls for the high-risk runs and look for "I am being evaluated," a test
framing, or reads of the evidence directory. A clean re-run is the only way to
measure the effect.
