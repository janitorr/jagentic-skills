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

- [x] **Trigger tests.** Re-ran the proxy and live prompts with a blind live
      pass plus a descriptions-only proxy. Proxy 101/105; live 13/14. The live
      miss is `Update this repo's AGENTS.md` -> no skill, 4/5 on retest; not
      stable. High.
- [x] **`code-review`.** Neutral paths (random roots, never `seeded` in a
      path). Re-ran 3 clean + 3 seeded: clean `pass` 3/3, seeded
      `needs_revision` 3/3, defect/test gap 3/3; clean fixture hardened. High.
- [ ] **`debug-loop`.** Run on a real codebase with a historical caller-patch
      bug; do not add another synthetic fixture. High.
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

## Deferred

- **`skill-forge` stop rule.** Not re-run after the contamination audit. The
  existing differential is 0/3 treatment vs 3/3 control; `skill-forge` is a
  meta-skill, the rule is unchanged since the counter, and the full test needs a
  baseline artifact plus six pressure runs. Revisit if the rule is edited or a
  real failure is reported.

## CI/CD

- [x] Score the caching smoke at `/tmp/opencode/orders.Ne9h6x`: 31/32,
      `Cache@2` 3/3, JUnit 1/1, coverage not added.
- [x] Keep `ci-cd` and commit the caching line, the trigger results, and the
      eleven-skill docs.
- [ ] Confirm the coverage wording does not suppress coverage when the repo
      already has a coverage tool. The clean phase predates that edit.

## Known debt

- [ ] `skill-forge` body: form matching and micro-tests; the trigger-test
      rewrite is observed but not separately tested.
- [ ] `documentation`: `Update this repo's AGENTS.md` retested 4/5. If the 1/5
      matters, add the literal `AGENTS.md` to the description and retest; do not
      change on this sample alone.
- [ ] `documentation` visuals: n=1 probe; architecture overview produced a file
      tree + Mermaid sequence, a feature section stayed prose. Re-test with 3-5
      reps and a control before calling it verified.
- [ ] `ci-cd`: the trigger test still used the retired selector; re-run with
      the blind live method if the local/global boundary is contested.
- [x] `code-review`: the user-search clean fixture was re-run under the stricter
      gate; 3/3 `pass` after request-id, tenant-scope, and missing-`q` fixes.
- [x] `code-review`: the CI-mutation-report preference was micro-tested n=1;
      the report was read and cited, the survivor was blocked, and no hand probe
      ran.
- [ ] `issue-interview`: rerun the control against the final wording.
- [x] `issue-interview`: reran the one-question scenario with 3 treatment runs
      plus a control; 0 walls, 3/3 complete issues, control published on turn 1.
- [ ] `issue-interview`: one run joined two decisions in a turn; add a
      one-decision counter and re-test if strict single-question shape matters.
- [ ] `git-workflow`: conflict, push, and release on the trimmed version.
- [ ] `documentation`: the n=3 retest still has no control.
- [ ] `visual-explainer`: one run per condition.
- [ ] `deep-module-design`: the test-only-method counter is applied but not
      isolated from a task change.
- [ ] `api-contract-design`: revisit only on a demonstrated HTTP failure or a
      weaker model.
- [ ] `ci-cd`: the clean phase predates the caching and coverage wording; one
      smoke covers caching, not the full set.
- [ ] `issue-to-openspec`: the revision-route confirmation gate is a one-run
      pilot.
- [ ] The multi-stage loop in `docs/workflow.md` is untested.

## Clean re-run rules

- Neutral agent IDs and prompts: a role, not a condition.
- One random root per run; no sibling runs; explicit no-read rule.
- Control: leave its normal judgment intact; silently deny only the target
  skill. Do not say "do not load any skill."
- Treatment: "use this skill," never "treatment."
- No doc or research hints a real request would not give.
- Trigger tests: a blind live pass with normal tools in a disposable project;
  a descriptions-only no-tool proxy is not behavioral evidence. Do not build a
  selection-only selector.
- Recreate the harness agents per run; do not commit them.
- Pin the model and variant; record the agent ID, system prompt, path, and model
  in the evidence file.
- Score from disk, not from the agent's self-report.
