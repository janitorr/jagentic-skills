# Evidence and evals

Status: **opportunistic**. Targeted tests run when a skill or behavior warrants
it; there is no standing eval suite. Eight skills have partial behavioral
evidence; one skill has an exploratory format probe; all ten descriptions passed
a trigger pilot, and the `documentation` description was re-tested after its
edit and after its evaluation-report edit; `skill-forge` is still unverified for
behavior. A proposed `api-contract-design` skill was evaluated and not created;
see "Evaluated but not created" below.

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
| All ten descriptions | `analysis/evidence/trigger-tests.md` | Proxy 105/105; live 8/10 generic, 4/4 repo-specific; change-list retest 24/24 proxy, live docs 1/1; evaluation-report retest 21/21 proxy, live 2/2 |
| `documentation` description | `analysis/evidence/trigger-tests.md#re-run-after-the-documentation-description-edit` | 3 proxy reps, 14 prompts: 40/42, then 41/42 after the RFC fix; live 5/5 after; evidence-report retest 21/21 proxy, live 1/1 |
| `issue-to-openspec` | `analysis/evidence/issue-to-openspec.md` plus fixture | Pilot, 3 reps per condition; pointer fires, design-quality ceiling; slicing and marker rules retested 3/3; blocked verdict 3/3, gate 1/3 then 3/3; real pipelines 3/3; pass 3/3; revision route 1/1 after an invalid first run |
| `code-review` | `analysis/evidence/code-review.md` plus fixture | 3 reps per condition; clean → pass 3/3, seeded defect → needs_revision 3/3 |
| `issue-interview` | `analysis/evidence/issue-interview.md` plus fixtures | Pilot plus two retests; final gate 2/2, confidence 12/12 responses, 6 questions per run; template n=1 |
| `git-workflow` | `analysis/evidence/git-workflow.md` plus fixtures | Pilot; trimmed to 80 lines of invariants and defaults; trim retest split under pressure with no `AGENTS.md`; conflict/push/release tested on the longer version |
| `visual-explainer` | `analysis/evidence/visual-explainer.md` plus fixture | Pilot, positive; diagram for a call path, prose for a one-liner; one-pager compared with `show-me` |
| `deep-module-design` | `analysis/evidence/deep-module-design.md` plus fixture | Partial; skill adds alternatives and contract, chosen design parity; deletion test moved to step 1 (3/3); provenance vs `codebase-design` |
| `skill-forge` | none for behavior | Unverified behavior |

**Evaluated but not created.** `api-contract-design`:
`analysis/evidence/api-contract-design.md` plus the `billing-api` fixture and
two run sets. Two baseline rounds (3 control + 3 `deep-module-design` runs each,
an enumerated brief and a prose brief) produced strong public HTTP contracts;
`deep-module-design` did not beat them. `skill-forge` says stop when the baseline
passes, so the HTTP gap is recorded as analysis debt, not a skill. Revisit only
on a demonstrated failure or a weaker model.

### External skill evaluations

- `context-engineering` (external, addyosmani bundle):
  `context-engineering-external.md`. 54 read-only runs across three repos and
  two task types. Negative as a loaded skill: 0/36 spontaneous loads, and
  +23-26% tokens plus +7-44% tool calls when forced. Positive as an applied
  practice: a pre-built project map cut tokens 13-37% and reads 20-36% with
  equal quality.

### Provenance comparisons

- `deep-module-design` vs mattpocock `codebase-design`:
  `codebase-design-vs-deep-module-design.md`. The original core is cheaper and
  applied the deletion test 3/3 while the pre-move synthesis managed 1/3; after
  moving the test, the synthesis reached 3/3. The synthesis's unique win is
  inline alternatives 3/3. The added migration and error material did not
  separate on the fixture.

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

The `issue-interview` fixtures are `issue-interview/fixtures/webhooks`, the
webhook repo with a local `tracker/issues/` tracker and no issue, and
`webhooks-template`, the same repo with `bug_report` and `feature_request`
templates under `.github/ISSUE_TEMPLATE/`. Runs replay
`issue-interview/script.md`; publishing is a file on disk.

The `git-workflow` fixture is built by `git-workflow/fixtures/setup.sh`: a repo
with a timeout fix, a whitespace-only reflow, and an untracked `debug.log`, with
or without a stated commit convention.

The `visual-explainer` one-pager fixture is
`visual-explainer/fixtures/onepager`: the webhook repo plus the issue from the
interview pilot. The flow runs reuse `issue-interview/fixtures/webhooks`.

## Evaluation environment

Every evaluation run recorded in this repository used `deepseek-v4.1-flash` via
provider `opencode-go`, default variant. Every session in this repository's
directory in the local OpenCode store is recorded under that model; other
models in the store belong to other projects. Each evidence file names the
model at the top.

A model change is a reason to re-baseline. A result from one model generation
does not establish behavior on another.

## Collecting run metrics

The local OpenCode store is the source of truth for model, tokens, tools, and
timing. Use `scripts/session_metrics.py`:

```bash
# Every child run of an evaluation session
python3 scripts/session_metrics.py --parent <parent-session-id>

# The ten most recent leaf sessions in this repository
python3 scripts/session_metrics.py --recent 10 --leaves \
  --directory /home/jani/code/jagentic-skills

# Specific sessions, as JSON or CSV
python3 scripts/session_metrics.py <id> [<id> ...] --json
python3 scripts/session_metrics.py --parent <id> --csv > runs.csv
```

It prints model/provider/variant, input/output/cache tokens, total and billable
tokens, cost, wall time, tool and read counts, distinct files read, skill calls,
and the tool mix. It prints no assistant answers. `--db` overrides the default
`~/.local/share/opencode/opencode.db`. Use `--leaves` so `--recent` does not
include the parent evaluation session.

## What we learned

These are stable findings. Each skill file keeps the method, tables, and
reproduction steps.

- **Review recall has a ceiling.** Seeded `spec-review` and TDD runs matched a
  strong control on recall; the fixtures do not show a skill advantage there.
- **Gates discriminate.** The approval marker changed behavior: 2/5 control TDD
  runs implemented without it, 0/5 with the skill. After the absolute
  preconditions, `issue-to-openspec` blocked 3/3 and fabricated no marker.
- **Blocked paths are testable.** A missing Acceptance section plus a scope
  contradiction moved from 1/3 correct blocks to 3/3 after the rule was made
  absolute and the verdict had to enumerate the gaps.
- **Pointers leave a fingerprint, not a better decision.** `issue-to-openspec`
  loaded `deep-module-design` 3/3 and added a deletion test, a test-surface
  argument, and a module responsibility; the chosen design did not improve.
- **`deep-module-design` adds alternatives, not a better chosen design.** On a
  shallow C# `ReportStore`, the skill produced a responsibility statement,
  interface invariants, and two or three alternatives 3/3; the control produced
  none of those but chose essentially the same interface. A harder read/write,
  transaction, and cache fixture reproduced the pattern 3/3. One baseline skill
  run put a test-only `Seed` method on the production interface; the added
  counter did not reproduce it, but the task changed at the same time, so the
  counter is not isolated. See [deep-module-design.md](deep-module-design.md).
- **The original `codebase-design` is cheaper and more reliable on the deletion
  test.** On the same fixture, the source core used 40% fewer total tokens than
  the synthesis and applied the deletion test 3/3 against the pre-move
  synthesis's 1/3. The synthesis's unique win is forcing a single agent to
  compare alternatives 3/3 against 0/3; its added migration and error material
  did not separate. See
  [codebase-design-vs-deep-module-design.md](codebase-design-vs-deep-module-design.md).
- **Trigger phrases need both the artifact noun and the verb.** `documentation`
  fired for "write up a report" but not for "record results/evidence"; adding
  "evaluation/evidence report" and "what an experiment showed" fixed the miss
  3/3 without pulling the skill into code review, TDD, or skill authoring.
- **Move a key test to the gate; do not add another bullet.** The synthesis had
  nearly the source's deletion-test sentence but buried it in step 4. Moving it
  to step 1 and requiring a one-line result raised it from 1/3 to 3/3. Two
  single-occurrence interface smells appeared in that retest; the mean score
  moved 12.0 to 11.5, so the salience gain is real but not free.
- **Recipes beat checklist lines.** The task-slicing rule was ignored 0/6 until
  a worked recipe was added; then 3/3. The marker rule moved 1/3 to 0/3 the same
  way.
- **`code-review` separates clean from broken.** A seeded whitespace defect the
  suite passed was found 3/3; clean diffs produced only Optional findings and
  passed 3/3.
- **The interview gate needs its examples.** A control published a fabricated
  issue on turn 1 from a vague ask. The first pilot held "Sounds good, go ahead"
  2/2, but after the confidence rule one of two runs published on the same line.
  Naming "go ahead" as non-confirming and requiring a yes that names the body
  held 2/2.
- **Confidence needs a per-response slot.** Before the rule said "every
  response", the skill restated confidence on 11/17 turns and dropped it on the
  soft-yes and publish replies. After the rule, 12/12, including the publish
  reply.
- **An unbounded interview needs a cap.** One pilot run asked 9 questions; six
  was enough in the retests. The cap is eight, with "draft when the next answer
  would not change the body" as the semantic stop.
- **A question turn is not a stage verdict.** Two runs emitted `blocked` after
  asking a question until the skill said a question turn is not the end of the
  stage.
- **Commit discipline may already be a default.** With a stated convention the
  control split the slices and excluded the debug file; the skill added nothing.
  Without one, both mixed a whitespace reflow with the timeout fix. Conflict,
  rejected push, and release also showed no baseline failure: the control
  resolved both sides, rebased without force, and cut `1.3.0` with an annotated
  tag and changelog. The only difference was the default commit shape
  (`release: 1.3.0` against `Release 1.3.0`). Both hand-computed the version;
  the skill now prefers repo release tooling or a semver CLI and records the
  bump decision in a footer, changeset, or label.
- **Procedures capable agents already follow are no-ops.** After five git
  pilots, the skill kept only the invariants and the defaults a repo without a
  convention needs. The step-by-step staging, branch, finish, and worktree
  procedures were removed.
- **The trimmed git skill holds the pressure case.** With no `AGENTS.md` and a
  mixed tree, it split the timeout fix from the reflow, excluded `debug.log`, and
  used the default commit shape. The longer version had bundled them.
- **Reviewer revisions route, but confirmation is the weak point.** The stage
  reached `openspec-update-change` and revised the existing change; the workflow
  wrote without showing the edits, so the stage now gates `pass` on a confirmed
  revision.
- **Change lists route to documentation.** Removing "changelog" from
  `git-workflow` and adding "release notes" to `documentation` split eight
  prompts 24/24 in the proxy; the live changelog prompt loaded `documentation`.
  The release/tag prompt loaded the global `git-workflow-and-versioning`, which
  is adjacent but not the local skill.
- **A one-pager needs the code shape.** Control and the first skill page omitted
  the diff; `show-me` included it and was more useful. The patched skill page
  adds the diff and a verification table and sits between the two.
- **Dark beats a white sheet for a page read at night.** The one-pager recipe
  now defaults to a dark, low-glare neutral unless the project has a palette.
- **Worktrees are harness-owned.** The skill's worktree mechanics duplicate
  `worktree_create` and `worktree_remove`; workspace policy belongs to the agent
  file.
- **Templates are found, not followed completely.** Both conditions found the
  repo's `bug_report` template. Only the skill added the acceptance criteria and
  out-of-scope sections the template omitted.
- **The clean `spec-review` fixture was not clean.** It carried a seeded
  duplicate-requirement defect and had no app shell or schema. The old
  `5/5 ready` result is withdrawn; see `spec-review.md`.
- **Descriptions route, with one gap.** Tutorial, runbook, migration-guide, and
  release-notes prompts reached `documentation`; RFC did not until the word was
  added.
- **Documentation shape follows explicit recipes.** The format probe changed
  shape only where the skill gave a recipe; the retest has no control.
- **Skills report a verdict, not delivery fields.** `pass`, `needs_revision`,
  and `blocked` plus a reason; the persona owns tracker operations. Owner-based
  results are historical.

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
4. **Score** defect recall, false blocking findings, verdict and reason, and
   approval-marker handling. Read every match manually.
5. **Record** the result in `analysis/evidence/<skill>.md`. Include the control
   prompt, repetitions, verbatim failures, with-skill results, and trigger
   results.
6. **Do not batch.** One skill at a time, per `skill-forge`.

## Known debt

`skill-forge` requires baseline, micro-test, and trigger evidence for each skill.
`spec-review`, `vertical-slice-tdd`, `issue-to-openspec`, `code-review`,
`issue-interview`, `git-workflow`, and `visual-explainer` have partial behavioral
records; `documentation` has an exploratory probe plus a no-control retest.
`deep-module-design` now has a three-per-condition baseline. `skill-forge` is a
behavior-shaping document with no observed behavior behind it. That is accepted
temporary debt, not a completed verification. `issue-interview` is a pilot plus two retests: the final
gate and confidence line held 2/2, but the control was not rerun against the
final wording. `git-workflow` is an 80-line invariants-and-defaults document; the
trim retest covers commit scope, while conflict, push, and release results belong
to the longer version. `issue-to-openspec` has a one-run revision-route pilot; its
confirmation gate is untested. `visual-explainer` is a one-run-per-condition
pilot.

Trigger work is complete. The proxy and live selector passes are recorded,
including the re-run after the `documentation` edit and the RFC retest. The
earlier "project-skill precedence" item was misframed: same-name collisions are
resolved by the loader, so that is harness behavior, not a skill. The two generic
prompts that loaded global skills named no project artifact, and repo-specific
phrasing loaded the local skill 4/4. The change-list boundary was retested after
the description split: 24/24 proxy, and the live changelog prompt loaded
`documentation`. No trigger eval is pending.

Pending verdict-contract test: four stages are recorded and one is a pilot.
`issue-to-openspec` reported `blocked` 3/3 on the blocked fixture; the gate held
1/3, then 3/3 after the precondition fix; `pass` 3/3 with the real pipeline.
`spec-review` reported `needs_revision` 3/3 on seeded and `pass` 4/9 on the
repaired clean fixture. `vertical-slice-tdd` reported `blocked` 3/3 without the
marker and `pass` 3/3 with it. `code-review` reported `pass` 3/3 on a clean diff
and `needs_revision` 3/3 on a seeded defect. `issue-interview` held the gate and reported `pass` 2/2 in the final retest;
the control published on turn 1 in the pilot. Its `blocked` result came from a
deferred design decision, not the seeded acceptance gap. The multi-stage loop in
`docs/workflow.md` remains untested. Owner-based routing tests are retired with
the contract.

Pending cross-skill test: none. The `issue-to-openspec` pointer to
`deep-module-design` is recorded in `issue-to-openspec.md`: it fires, and its
artifact effect is vocabulary, not design quality.
