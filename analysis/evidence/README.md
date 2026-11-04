# Evidence and evals

Status: **opportunistic**. Targeted tests run when a skill or behavior warrants
it; there is no standing eval suite. Three skills have partial behavioral
evidence; one skill has an exploratory format probe; all ten descriptions passed
a trigger pilot, and the `documentation` description was re-tested after its
edit; six skills are still unverified for behavior.

This note is the place to resume. Do not treat the absence of evidence as proof
that a skill works.

## What exists

| Skill | Evidence | Status |
|---|---|---|
| `spec-review` | `analysis/evidence/spec-review.md` plus fixtures | Pilot plus five repetitions per condition; ceiling effect |
| `vertical-slice-tdd` | `analysis/evidence/vertical-slice-tdd.md` plus fixture | TDD ceiling; approval gate discriminates |
| `documentation` | `analysis/evidence/documentation.md` plus `documentation/headings.txt` | Exploratory format probe (n=1 per type) plus post-patch retest (n=3 per changed type); retest has no control |
| `documentation` vs `writing-for-agents` | `analysis/evidence/documentation-vs-writing-for-agents.md` plus `documentation-vs-writing-for-agents/headings.txt` | Exploratory n=3 comparison of README and AGENTS.md output; document shape only |
| All ten descriptions | `analysis/evidence/trigger-tests.md` | Proxy 105/105; live 8/10 generic, 4/4 repo-specific |
| `documentation` description | `analysis/evidence/trigger-tests.md#re-run-after-the-documentation-description-edit` | 3 proxy reps, 14 prompts: 40/42, then 41/42 after the RFC fix; live 5/5 after |
| `issue-to-openspec` | `analysis/evidence/issue-to-openspec.md` plus fixture | Pilot, 3 reps per condition; pointer fires, design-quality ceiling, task-shape rule missed |
| Six other skills | none for behavior | Unverified behavior |

The `spec-review` fixtures are small OpenSpec projects under
`spec-review/fixtures/`:

- `spec-review/fixtures/seeded`: six known defects, including a requirement with
  no scenario, missing auth scoping, an unverified index assumption, and
  layer-batched tasks.
- `spec-review/fixtures/clean`: the same change with those defects resolved;
  strict validation passes.

The `vertical-slice-tdd` fixture is a small Python `unittest` repo at
`vertical-slice-tdd/fixtures/template`, with an OpenSpec change, a documented
test command, and an `APPROVED` marker. Test outcomes are logged so test-first
behavior can be scored from disk.

The `issue-to-openspec` fixture is `issue-to-openspec/fixtures/seam`: a small
Python repo with one single-attempt webhook sender shared by three notifiers. Its
issue forces a retry seam decision and includes a settled rejection of the
inline-loop option.

## What we learned

- Five seeded `spec-review` runs with the skill and five without both found all
  six defects and returned **needs revision**. The fixture is too easy to
  discriminate.
- Five clean `spec-review` runs with the skill and five without both avoided
  blocking findings. The skill returned **ready for spec approval**; the control
  returned **ready for human review**.
- Five `vertical-slice-tdd` runs with the skill and five without both wrote a
  failing test first, went green, checked tasks, and committed. TDD also hit a
  ceiling.
- In the approval-gate experiment, 2/5 control runs implemented without the
  required marker; 0/5 skill runs did. This is the first discriminating result:
  the skill raised gate compliance from 60% to 100% in this fixture.
- No TDD or review-recall advantage over a strong control has been demonstrated.
- The `documentation` format probe found the skill changed shape only where it
  gave an explicit recipe, had no branch for onboarding guides or runbooks, and
  leaked a planning step into an inline-comment deliverable. After the patch,
  five changed branches produced the intended shape in 3/3 runs each; the retest
  has no control, so superiority over no skill is still unshown.
- Against `writing-for-agents`, our README duplicated every command (quick start
  plus a command table) and our agent instructions had no completion criterion.
  After patching, README repeats fell from 8 to 2 and criteria rose from 0 to 16;
  agent-instruction negations fell from 6 to 2, and every file now states what
  done means. Files are about 20% longer. This is document-shape evidence; no
  downstream compliance test has been run.
- After the `documentation` description edit, tutorial, runbook, migration-guide,
  and release-notes prompts all routed to the local skill in both the proxy and
  the live selector. RFC did not, because the body said "ADR or RFC" and the
  description said only "ADR". Adding the word fixed it: 3/3 proxy and local
  skill live.
- The `issue-to-openspec` pointer to `deep-module-design` fires 3/3 and leaves a
  fingerprint: a deletion test, a test-surface argument, and an explicit module
  responsibility, none of which appeared in the control. It did not improve the
  design choice or the alternatives analysis, which the control already did well.
- The same runs found that the skill's "tasks are vertical slices" rule is not
  followed in either condition: 0/6 runs sliced by behavior. Every task carried a
  verification step, so the rule is half-enforced and needs a recipe, not another
  checklist line.
- One `issue-to-openspec` run created its own `APPROVED` marker. The skill names
  the marker only through the agent file and never says who may create it.

## Why there is no standing suite

- The TDD, spec-review, and issue-to-openspec fixtures all hit ceilings on
  outcome quality, so more repetitions on them add cost without information.
- Synthetic fixtures are only worth running when they can discriminate.
- Real usage is a better source of misses than a synthetic clean/seeded pair.

## When to resume

Resume when one of these happens:

- A real change exposes a miss, a false blocking finding, or a wrong verdict.
- A skill's behavior is contested.
- A skill is edited in a way that could change behavior, not just wording.
- A new skill is added and needs its first baseline.

## How to resume

1. **Harden the fixture first.** Add a defect a competent reviewer would plausibly
   miss: a requirement that subtly contradicts an existing spec, an acceptance
   criterion buried in an issue comment, or an assumption that looks confirmed
   but is not.
2. **Add a trigger test.** Use only the frontmatter plus six to ten
   should-fire / should-not-fire prompts, including adjacent skills.
3. **Run three to five fresh repetitions per condition.** Control: no skill.
   Treatment: load the skill. Use the same files, commands, and output contract.
4. **Score** defect recall, false blocking findings, verdict, next-stage handoff,
   and approval-marker handling. Read every match manually.
5. **Record** the result in `analysis/evidence/<skill>.md`. Include the control
   prompt, repetitions, verbatim failures, with-skill results, and trigger
   results.
6. **Do not batch.** One skill at a time, per `skill-forge`.

## Known debt

`skill-forge` requires baseline, micro-test, and trigger evidence for each skill.
`spec-review`, `vertical-slice-tdd`, and `issue-to-openspec` have partial
behavioral records; `documentation` has an exploratory probe plus a no-control
retest. The other six are behavior-shaping documents with no observed behavior
behind them. That is accepted temporary debt, not a completed verification.

Pending trigger work: the proxy and live selector passes are recorded, including
the re-run after the `documentation` edit and the RFC retest. The remaining work
is to check that the project-skill precedence rule wins when a generic and a
project skill both apply.

Pending routing-contract test: the five stage skills now emit `routing_status`,
`owner`, and `requested_action`. `docs/workflow.md` defines the intended
transitions, but no workflow has been tested against those signals yet.

Pending cross-skill test: none. The `issue-to-openspec` pointer to
`deep-module-design` is recorded in `issue-to-openspec.md`: it fires, and its
artifact effect is vocabulary, not design quality.
