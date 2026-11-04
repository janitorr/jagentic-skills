# Evidence and evals

Status: **opportunistic**. Targeted tests run when a skill or behavior warrants
it; there is no standing eval suite. Four skills have partial behavioral
evidence; one skill has an exploratory format probe; all ten descriptions passed
a trigger pilot, and the `documentation` description was re-tested after its
edit; five skills are still unverified for behavior.

This note is the place to resume. Do not treat the absence of evidence as proof
that a skill works.

**Contract change (2026-11-04).** Skills now end with
`verdict: pass | needs_revision | blocked` and a one-line reason. The
`routing_status` / `owner` / `requested_action` contract was retired because
delivery belongs to the persona's agent file, not the skill. Owner-based results
in the records below are superseded; verdict, gate, and finding results stand.

## What exists

| Skill | Evidence | Status |
|---|---|---|
| `spec-review` | `analysis/evidence/spec-review.md` plus fixtures | Pilot plus five repetitions per condition; verdict 3/3 on seeded, 4/9 pass on the repaired clean fixture; clean ceiling withdrawn |
| `vertical-slice-tdd` | `analysis/evidence/vertical-slice-tdd.md` plus fixture | TDD ceiling; approval gate discriminates; verdict blocked 3/3 and pass 3/3 |
| `documentation` | `analysis/evidence/documentation.md` plus `documentation/headings.txt` | Exploratory format probe (n=1 per type) plus post-patch retest (n=3 per changed type); retest has no control |
| `documentation` vs `writing-for-agents` | `analysis/evidence/documentation-vs-writing-for-agents.md` plus `documentation-vs-writing-for-agents/headings.txt` | Exploratory n=3 comparison of README and AGENTS.md output; document shape only |
| All ten descriptions | `analysis/evidence/trigger-tests.md` | Proxy 105/105; live 8/10 generic, 4/4 repo-specific |
| `documentation` description | `analysis/evidence/trigger-tests.md#re-run-after-the-documentation-description-edit` | 3 proxy reps, 14 prompts: 40/42, then 41/42 after the RFC fix; live 5/5 after |
| `issue-to-openspec` | `analysis/evidence/issue-to-openspec.md` plus fixture | Pilot, 3 reps per condition; pointer fires, design-quality ceiling; slicing and marker rules retested 3/3; blocked verdict 3/3, gate 1/3 then 3/3; real pipelines 3/3; pass 3/3 |
| `code-review` | `analysis/evidence/code-review.md` plus fixture | 3 reps per condition; clean → pass 3/3, seeded defect → needs_revision 3/3 |
| Five other skills | none for behavior | Unverified behavior |

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
inline-loop option. `issue-to-openspec/fixtures/seam-blocked` is the same repo
with the Acceptance section removed and the scope sections in conflict.

The `code-review` fixture is built by
`code-review/fixtures/slugify/setup.sh` from the vertical-slice-tdd template:
`main` is the stub, `feature/add-slugify` is the implementation, and `SEED=1`
narrows the whitespace regex so the suite passes while the spec is violated.

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
- The same runs found that the skill's "tasks are vertical slices" rule was not
  followed in either condition: 0/6 runs sliced by behavior, though every task
  carried a verification step. Adding a slicing recipe moved the treatment to
  3/3 on a retest.
- One `issue-to-openspec` run created its own `APPROVED` marker, which the skill
  never assigns to the spec writer. After adding an explicit prohibition, 0/3
  retest runs created one.
- On an issue missing its Acceptance section and contradicting itself on scope,
  the skill emitted the routing block 3/3 but only blocked 1/3; two runs let the
  user's "proceed" instruction override the missing section. After making the
  rule absolute and requiring the block to enumerate gaps, 3/3 blocked and named
  every gap. The control blocked 0/3.
- `spec-review` emitted the routing block 12/12 across the seeded and clean
  fixtures. Seeded was `needs_revision` 3/3. The clean fixture reached `pass`
  4/9 across repaired cohorts; the other runs blocked on fixture defects or on
  the untracked UI follow-up.
- The earlier clean `5/5 ready, 0 false blocking` result was not reproducible.
  The "clean" fixture still carried a seeded duplicate-requirement defect and
  had no app shell, schema, or request contract. It has since been repaired;
  that ceiling claim is withdrawn.
- With `openspec-explore` and `openspec-propose` installed, all three
  `issue-to-openspec` runs used the real pipeline and produced strict-valid
  artifacts. The pointer and the design ceiling did not move. One run emitted
  `owner: human` with `proceed to spec-review`; that field was later retired
  with the verdict contract, so the owner fix is historical.
- `vertical-slice-tdd` stopped 3/3 when the `APPROVED` marker was deleted, with
  no code changes and no fabricated marker. All approved runs implemented, kept
  the suite green, and committed per slice.
- One approved `vertical-slice-tdd` run produced no work and no report. It is
  recorded as a harness failure, not a routing result.
- `code-review` returned `pass` 3/3 on a clean diff and `needs_revision` 3/3 on
  a seeded whitespace defect. The clean diff produced only Optional findings;
  the seeded one was found by every run, including the missing non-space
  whitespace test.

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
`spec-review`, `vertical-slice-tdd`, `issue-to-openspec`, and `code-review` have
partial behavioral records; `documentation` has an exploratory probe plus a
no-control retest. The other five are behavior-shaping documents with no observed
behavior behind them. That is accepted temporary debt, not a completed
verification.

Pending trigger work: the proxy and live selector passes are recorded, including
the re-run after the `documentation` edit and the RFC retest. The remaining work
is to check that the project-skill precedence rule wins when a generic and a
project skill both apply.

Pending verdict-contract test: four stages are recorded. `issue-to-openspec`
reported `blocked` 3/3 on the blocked fixture; the gate held 1/3, then 3/3 after
the precondition fix; `pass` 3/3 with the real pipeline. `spec-review` reported
`needs_revision` 3/3 on seeded and `pass` 4/9 on the repaired clean fixture.
`vertical-slice-tdd` reported `blocked` 3/3 without the marker and `pass` 3/3
with it. `code-review` reported `pass` 3/3 on a clean diff and `needs_revision`
3/3 on a seeded defect. `issue-interview` has no record, and the multi-stage loop
in `docs/workflow.md` remains untested. Owner-based routing tests are retired
with the contract.

Pending cross-skill test: none. The `issue-to-openspec` pointer to
`deep-module-design` is recorded in `issue-to-openspec.md`: it fires, and its
artifact effect is vocabulary, not design quality.
