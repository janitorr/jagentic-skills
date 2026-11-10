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

- **`quality-constraints` skill.** addyosmani's `constraint-driven-development`
  fills the written quality-contract gap in `analysis/coverage.md` row 7:
  `CONSTRAINTS.md`, a floor, dimensions with a command each, ratchets, exceptions,
  and a diff guard against weakened checks. Revisit after the stage retests. It
  overlaps `ci-cd`, `code-review`, `vertical-slice-tdd`, and `documentation`;
  synthesize a lean, environment-agnostic version rather than copying the
  319-line source.
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

## Retest after the 2026-11-10 skill edits

Four skills changed behavior; two changed only terminology. The descriptions did
not change, so no trigger retest is required. Full evals were not re-run. Do one
skill at a time per `skill-forge`; record a smoke pass as smoke-only, not as
verified evidence.

### `issue-interview`

- [x] **Fixture:** `analysis/evidence/issue-interview/fixtures/ingest` and
      `script-ingest.md` used for the 2026-11-10 smoke; three pilot gaps
      (steady-state pruning, initialization, runner) were added to the bank.
- [x] **Smoke:** publish arm 3/3 after the goal gate; controls published on turn
      1 4/4. See `analysis/evidence/issue-interview.md`.
- [x] **Blocked:** 3/3 after the delegation rule; the pre-rule run decided the
      backlog and was the baseline failure.
- [x] **Full:** 3 publish + 3 blocked treatment; 3 publish + 1 blocked control.
      This is a smoke/micro-test, not a controlled 3x3; the final draft-check
      wording is n=1.
- [x] **Business-level cleanup:** outcome/who/constraints wording smoke 1/1
      publish and 1/1 blocked; the control published on turn 1. n=1, not a full
      matrix.

### `issue-to-openspec`

- [x] **Fixture:** `seam-blocked` now has `questions.md` and a `Questions:`
      operation in its `AGENTS.md`.
- [x] **Smoke:** 3/3 blocked, one question per section, no review destination,
      no artifacts. See `analysis/evidence/issue-to-openspec.md`.
- [ ] **Full:** add a control and re-run the blocked path; recheck the revision
      route after the precondition rewording.

### `vertical-slice-tdd`

- [ ] **Smoke:** an approved-change run. Check the run never invokes or attempts
      spec review and treats only the spec-approval marker as the gate.
- [ ] **Full:** add a "no spec-review attempt" check to
      `analysis/evidence/vertical-slice-tdd.md` and re-run the blocked/pass pair.

### `documentation`

- [ ] **Smoke:** a disposable repo with two or three existing ADRs plus
      "preserve historical ADRs". Check no current-status block is added, the
      original decisions stay intact, and current guidance links forward or
      supersedes.
- [ ] **Full:** add a multi-ADR fixture or brief and a historical-frame criterion
      to `analysis/evidence/documentation.md`; run n=3 with a control.

### `spec-review`

- [ ] No behavior retest. The Environment now defines tracker, spec-approval
      marker, and review destination; the process is unchanged. Read through for
      terminology only.

### `code-review`

- [ ] No behavior retest. The unused approval marker was removed from
      Environment; tracker and review destination are now defined. Read through
      for terminology only.

### Unchanged

The other five skills and every description are unchanged; no retest.

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
- [ ] The 2026-11-10 skill edits: per-skill retest list in "Retest after the
      2026-11-10 skill edits" above. No full eval has run.
- [ ] `issue-interview`: the 2026-11-10 ingest smoke is not a controlled 3x3;
      the final goal and draft-check wording has n=3 and n=1. Re-run a
      controlled matrix if strict wording matters.
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
