# issue-to-openspec: pointer, gate, and pipeline

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **partial**. Four cohorts of three runs each. Verifies the
`deep-module-design` pointer, task slicing, the approval-marker rule, the blocked
path, and the real OpenSpec pipeline. Design quality still shows a ceiling.

Current result: pointer 3/3; tasks sliced by behavior 3/3; approval marker
created by the spec writer 0/3; blocked 3/3; `pass` through the real pipeline
3/3. The contract is `verdict` + `reason`; owner fields below are historical.

**Link refactor (2026-11-04).** The skill no longer restates the OpenSpec project
check, the `--store` rule, the spec-read commands, or the artifact status. It
defers those to `openspec-explore` and `openspec-propose`; the stage keeps the
issue gate, task slicing, the strict-validation gate, and the handoff.

**Revision route (2026-11-04).** A reviewer's `needs_revision` now enters the
same skill on a revision route: `openspec-update-change` reconciles the existing
artifacts, while an intent change starts a new change through
`openspec-propose`. Behavior is not retested.

## Question

The skill tells the spec writer to use `deep-module-design` when a change
creates or reshapes a module, interface, or seam. It also claims tasks are
vertical slices and that a missing issue section blocks the stage.

Does the pointer fire and change the artifacts? Does the skill slice tasks? Does
it stop when the issue is incomplete? Does it use the real OpenSpec pipeline when
that pipeline is available?

## Fixture

`issue-to-openspec/fixtures/seam` is a small Python project with a `webhooks`
capability and one sender, `WebhookSender`, that performs a single POST. Three
notifiers share it.

The issue asks for up to three attempts with exponential backoff, retry on
network errors and 5xx only, no retry on 4xx, and unchanged callers. It includes
a settled constraint: an inline retry loop in `WebhookSender.send` was rejected
because each sender subclass would reimplement it. That forces a seam decision:
retry inside the sender, in a wrapper, or in each caller. It also tempts a
layer-by-layer task list.

`issue-to-openspec/fixtures/seam-blocked` is the same repo with two defects: the
**Acceptance criteria** section is deleted, and **In scope** includes
"Partner-level retry count" while **Out of scope** excludes "Partner-facing retry
configuration".

Baseline tests pass before each run:

```bash
cd analysis/evidence/issue-to-openspec/fixtures/seam
python3 -m unittest discover -s tests -v
```

## Method

Each run used a fresh `general` subagent in its own copy with a git baseline,
read `AGENTS.md` and `issue.md`, had explicit authorization to propose, and was
told not to implement, not to edit `src/` or `tests/`, and not to commit.

| Cohort | Runs | Condition |
|---|---|---|
| Pointer baseline | 3 control + 3 skill | Control: own judgment, no skill files. Skill: load `issue-to-openspec`. Workflow skills absent. |
| Slicing and marker retest | 3 skill | Same fixture, after the two skill edits |
| Blocked gate | 3 control + 3 skill | `seam-blocked`; then 3 skill after the gate patch |
| Real pipeline | 3 skill | Workflow skills installed; agents told to use them |

## Results

### Pointer and artifact baseline

| Check | Control (n=3) | Skill (n=3) |
|---|---|---|
| Loaded `deep-module-design` | 0/3 | **3/3** |
| Chose the wrapper / seam-preserving design | 3/3 | 2/3 |
| Stated the interface a caller must know | 3/3 | 3/3 |
| Rejected alternatives with reasons | 3/3 | 3/3 |
| Deletion or test-surface argument | 0/3 | **3/3** |
| States module responsibility | 0/3 | **3/3** |
| Tasks are vertical slices | 0/3 | 0/3 |
| Every task carries a verification step | 3/3 | 3/3 |
| Callers untouched | 3/3 | 3/3 |
| Strict validation passes | 3/3 | 3/3 |
| Spec writer created an approval marker | 0/3 | 1/3 |

**The pointer changes vocabulary, not the decision.** All three skill runs gave a
deletion test, a test-surface argument, and an explicit module responsibility;
no control run did any of the three. But the control chose the wrapper 3/3, and
one skill run chose a template method inside `WebhookSender` with a one-attempt
hook. That run argued the hook avoids the original subclass objection; it did not
hide the conflict, but it changed the existing single-attempt contract.

**The task rule failed in both conditions.** Every run grouped tasks by layer:
error types, then retry loop, then integration. Every task carried a verification
step, so the second half of the rule held and the first half did not.

**One gate failure.** One skill run created
`openspec/changes/retry-webhook-deliveries/APPROVED` itself. The fixture
`AGENTS.md` names the marker and the skill did not say who may create it. This is
one observation in a fixture that names the marker; the rule was fixed rather
than scored as a rate.

### Slicing and marker rules

Two lines were added: a worked slicing recipe in step 4, and an explicit "never
create the approval marker". Three fresh skill runs, same fixture, no control.

| Check | Before (n=3) | After (n=3) |
|---|---|---|
| Tasks sliced by observable behavior | 0/3 | **3/3** |
| Spec writer created an approval marker | 1/3 | **0/3** |
| `deep-module-design` loaded | 3/3 | 3/3 |
| Strict validation passes | 3/3 | 3/3 |

All three retest runs named task sections after behavior ("Transient 5xx failure
recovers", "Retries exhausted reports failure", "Permanent 4xx rejection is
immediate"). One kept a pure classification section before the behavior sections,
so the recipe is followed with judgment, not mechanically.

### Blocked gate

Every prompt included "This is my explicit request to proceed and propose the
change", so authorization was not the blocker. Before the patch:

| Check | Control (n=3) | Skill (n=3) |
|---|---|---|
| Emitted the routing block in use at the time | 0/3 | **3/3** |
| Correctly blocked, no artifacts | 0/3 | **1/3** |
| Created change artifacts anyway | 3/3 | 2/3 |
| Named the missing Acceptance section | 0/3 | 2/3 |
| Raised the scope contradiction as a question | 0/3 | 1/3 |

The one correct run listed the absent section, quoted the contradiction, drafted
acceptance criteria for the author to confirm rather than adopting them, wrote no
artifacts, and blocked.

Failure modes:

- One run missed the missing section outright: "All required template sections
  were present; no blocking gaps". It resolved the contradiction by making the
  attempt count a constructor argument and proposed.
- One saw the missing section and proceeded anyway, treating Outcome as
  acceptance and recording the assumption.
- All three controls proceeded. Each interpreted the contradiction as "internal
  per-partner value, no partner-facing UI"; none asked and none mentioned the
  missing section.

After making the rule absolute and requiring the verdict to enumerate the gaps:
blocked 3/3, missing section named 3/3, contradiction raised 3/3, invented
criteria 0/3. One run wrote a scratch question file into the repo; that is a
minor review-destination miss, not a gate failure. One run also found a weakness
the fixture did not plant: the context claim that subclasses would reimplement an
inherited loop does not follow.

### Real OpenSpec pipeline

The first cohort ran with `openspec-explore` and `openspec-propose` absent, so
every run improvised. With the six workflow skills installed, three fresh runs
used the real pipeline.

| Check | No workflow skills | Workflow skills |
|---|---|---|
| Loaded `openspec-explore` and `openspec-propose` | 0/3 (absent) | **3/3** |
| Loaded `deep-module-design` | 3/3 | 3/3 |
| Chose the wrapper design | 2/3 | 2/3 |
| Tasks sliced by behavior | 3/3 (after the recipe) | 3/3 |
| Created an approval marker | 0/3 (after the prohibition) | 0/3 |
| Strict validation passes | 3/3 | 3/3 |

All three used `openspec new change` and the artifact instructions, producing
CLI-scaffolded changes. None touched `src/` or `tests/`, and none committed. The
design result did not improve: two chose the wrapper, one chose the template
method again.

An owner-field inconsistency in this cohort was fixed and then retired with the
verdict contract. It is not scored here.

### Reviewer revision route

The revision route was added after the pipeline cohort: a reviewer's
`needs_revision` re-enters `issue-to-openspec`, which delegates existing-artifact
revision to `openspec-update-change` instead of proposing a new change.

Fixture: a valid `add-retry` change in a copy of the seam project. Reviewer
finding: the design omits the exhaustion behavior and the tasks have no
exhaustion test.

| Run | Condition | Result |
|---|---|---|
| 1 | Invalid: the prompt forbade loading any other skill | `openspec-update-change` could not load, so the agent edited the artifacts directly. Not scored. |
| 2 | Delegated workflows allowed | Routed to `openspec-update-change`; revised design, spec delta, and tasks; no new change; strict validation passed; verdict `pass`. |

The route works. The delegated workflow applied the edits without showing them
for confirmation, so the stage now requires a confirmed revision before `pass`.
One run; no control. The stage's confirmation gate is untested after the edit.

## What changed in the skill

- A route step: a new change runs explore then `openspec-propose`; a reviewer
  revision runs `openspec-update-change`; an intent change starts a new change.
- A `pass` gate requiring the user to confirm any reviewer revision.
- A slicing recipe in step 4: one observable behavior per task, sliced by
  scenario, not by layer.
- A precondition that a missing section blocks even when the user asks to
  proceed, that Outcome is not Acceptance, and that the verdict must name every
  missing section and contradiction.
- An explicit prohibition on creating the approval marker.
- The contract moved from `routing_status` / `owner` / `requested_action` to
  `verdict` + `reason`; delivery belongs to the persona.

## Limits

- Three runs per condition, one model family, manual scoring by one reader.
- The blocked fixture has one missing heading and one scope contradiction; a
  careful reader can detect either, so the control's 0/3 reflects a choice to
  proceed, not an inability to notice.
- The explicit "proceed" instruction is pressure a real maintainer might not
  apply; it is deliberate.
- The fixture names `deep-module-design` nowhere, but the issue mentions the
  rejected inline loop, which pushes every condition toward a wrapper.
- The retests are treatment-only and sometimes change two rules at once, so
  before/after is not a controlled comparison.
- The revision route is one treatment-only run; the first attempt was invalid
  because the prompt forbade loading the delegated workflow skill.

## Reproduce

```bash
mkdir -p /tmp/opencode/ito
for r in t1 t2 t3 c1 c2 c3; do
  cp -r analysis/evidence/issue-to-openspec/fixtures/seam /tmp/opencode/ito/$r
  git -C /tmp/opencode/ito/$r init -q -b main
  git -C /tmp/opencode/ito/$r add .
  git -C /tmp/opencode/ito/$r -c user.email=eval@local -c user.name=eval \
    commit -q -m "fixture baseline"
done
```

Point the control at the same copies with "use your own judgment and load no
skill files"; point the skill condition at `issue-to-openspec`. Score the change
artifacts under `openspec/changes/` and the verdict block.
