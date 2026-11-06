# Open tasks

Status: **open**. This is the project resume point. Each task names the artifact
that motivates it and the evidence to update when it is done.

## Agent files

Source: `docs/agent-files.md`.

- [ ] Choose the persona topology: one orchestrator plus stage personas, or one
      persona per stage.
- [ ] Write one stage persona end to end: role, tools, tracker operations,
      approval marker, review destination, workspace and push policy, and a
      pinned model and variant.
- [ ] Map each verdict (`pass`, `needs_revision`, `blocked`) to the environment
      action.
- [ ] Test that persona before defining the next one.

## Contamination re-runs

Source: `analysis/evidence/contamination-audit.md`.

- [ ] **Trigger tests.** Re-run the proxy and live prompts with
      `trigger-selector` (only the `skill` tool). High.
- [ ] **`skill-forge` stop rule.** Neutral agents, no `eval`/`control`/
      `treatment` names or prompts. High.
- [ ] **`debug-loop`.** Run on a real codebase with a historical caller-patch
      bug; do not add another synthetic fixture. High.
- [ ] **`code-review`.** Neutral paths (`cr-a`, `cr-b`), never `seeded` in a
      path. High.
- [ ] **Gate and verdict evals.** `spec-review`, `vertical-slice-tdd`,
      `issue-to-openspec`, `issue-interview`: re-run the gate/verdict subset and
      leave the control to its normal judgment instead of "do not load any
      skill." High.
- [ ] **Design-quality evals.** `deep-module-design`, `api-contract-design`:
      re-run only if the conclusion still matters. High/medium.
- [ ] **Shape evals.** `documentation`, `git-workflow`, `visual-explainer`:
      neutral prompts. Medium.
- [ ] **Exploratory comparisons.** `documentation-vs-writing-for-agents`,
      `codebase-design-vs-deep-module-design`, `code-review-comparison`: only if
      contested. Medium/low.
- [ ] **`context-engineering-external`.** Metrics only; lowest priority.

## CI/CD

- [ ] Score the caching smoke at `/tmp/opencode/orders.Ne9h6x`; update
      `analysis/evidence/cicd.md`.
- [ ] If the smoke passes, keep `ci-cd` and commit the caching line, the trigger
      results, and the eleven-skill docs. If it fails, revise before deploying.
- [ ] If the smoke is skipped, record the caching line as debt instead of
      claiming it verified.

## Known debt

- [ ] `skill-forge` body: form matching, micro-tests, and trigger wording beyond
      the stop rule.
- [ ] `issue-interview`: rerun the control against the final wording.
- [ ] `git-workflow`: conflict, push, and release on the trimmed version.
- [ ] `documentation`: the n=3 retest still has no control.
- [ ] `visual-explainer`: one run per condition.
- [ ] `deep-module-design`: the test-only-method counter is applied but not
      isolated from a task change.
- [ ] `api-contract-design`: revisit only on a demonstrated HTTP failure or a
      weaker model.

## Clean re-run rules

- Neutral agent IDs and prompts: a role, not a condition.
- One random root per run; no sibling runs; explicit no-read rule.
- Control: leave its normal judgment intact; silently deny only the target
  skill. Do not say "do not load any skill."
- Treatment: "use this skill," never "treatment."
- No doc or research hints a real request would not give.
- Trigger selectors: only the `skill` tool.
- Pin the model and variant; record the agent ID, system prompt, path, and model
  in the evidence file.
- Score from disk, not from the agent's self-report.
