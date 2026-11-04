# issue-to-openspec: pointer and artifact test

Status: **pilot**, three repetitions per condition. First behavioral record for
`issue-to-openspec`. It verifies that the `deep-module-design` pointer fires and
records what changes in the artifacts. It does not prove the artifacts are
better.

## Question

`issue-to-openspec` tells the spec writer to use `deep-module-design` when a
change creates or reshapes a module, interface, or seam. Does the pointer fire,
and does it change the design and task artifacts?

## Fixture

`issue-to-openspec/fixtures/seam` is a small Python project with a `webhooks`
capability and one sender, `WebhookSender`, that performs a single POST. Three
notifiers share it.

The issue asks for up to three attempts with exponential backoff, retry on
network errors and 5xx only, no retry on 4xx, and unchanged callers. It includes
a settled constraint: an inline retry loop in `WebhookSender.send` was rejected
because each sender subclass would reimplement it.

This forces a seam decision: retry inside the sender, in a wrapper, or in each
caller. It also tempts a layer-by-layer task list.

Baseline tests pass before each run:

```bash
cd analysis/evidence/issue-to-openspec/fixtures/seam
python3 -m unittest discover -s tests -v
```

## Conditions

Six fresh `general` subagents, each in its own copy of the fixture with a git
baseline commit. Each was told to produce the OpenSpec change artifacts, not to
implement, not to edit `src/` or `tests/`, and not to commit. Each got explicit
authorization to propose, so the skill's approval gate was satisfied.

- **Control:** "Use your own judgment only. Do not load, read, or follow any
  skill files."
- **Skill:** load `issue-to-openspec` with the skill tool and follow it.

Both were told that `openspec-explore` and `openspec-propose` are not installed
and to do that work themselves. Both reported the skill IDs they loaded.

## Results

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

### What the pointer changes

All three skill runs used the `deep-module-design` framing that the controls did
not:

- a deletion test: what disappears if the wrapper is removed, and what
  reappears at each call site;
- a test-surface argument: callers and tests cross the same `send` interface;
- an explicit module-responsibility sentence separating transport from retry
  policy.

No control run made any of these three moves. That is the measurable effect of
the pointer.

### What it does not change

The wrapper design, the interface statement, the alternatives table, and the
risk analysis are present in both conditions. On design choice the control was
at least as consistent: 3/3 wrappers, while one skill run (t3) chose a template
method inside `WebhookSender`, the option the issue says review rejected. t3
argued explicitly that a subclass hook avoids the original objection, so it did
not hide the conflict, but it made `send` retry by default and required changing
the existing single-attempt test fixture.

The skill's own verification item "Tasks are vertical slices with acceptance and
verification, not a layer-by-layer checklist" failed in **both** conditions.
Every run grouped tasks by implementation layer: error types, then retry loop,
then integration. Every task carried a verification step, so the second half of
the rule held and the first half did not.

### Gate finding

t1 created `openspec/changes/retry-webhook-deliveries/APPROVED` on its own. The
fixture's `AGENTS.md` names the marker, and the skill does not say who may create
it. A spec writer approving its own spec is the same gate failure that the
`vertical-slice-tdd` experiment measured in control runs. This is one observation
in a fixture that names the marker, so treat it as a defect to fix rather than a
rate.

## Verdict

- The pointer fires and leaves a recognizable artifact fingerprint.
- It does not demonstrably improve the chosen design or the alternatives
  analysis against a strong control.
- The task-shape rule was not followed by the skill's own runs; the retest below
  shows a recipe fixes it on this fixture.
- The approval-marker rule had no owner; the retest below shows the explicit
  line holds.

## Retest after the patch

Two lines were added to the skill: a slicing recipe in step 4 and an explicit
"never create the approval marker" in the interaction contract. Three fresh
treatment runs on the same fixture, same prompt, no control.

| Check | Before (n=3) | After (n=3) |
|---|---|---|
| Tasks sliced by observable behavior | 0/3 | **3/3** |
| Spec writer created an approval marker | 1/3 | **0/3** |
| `deep-module-design` loaded | 3/3 | 3/3 |
| Strict validation passes | 3/3 | 3/3 |

All three runs now name task sections after behavior ("Transient 5xx failure
recovers", "Retries exhausted reports failure", "Permanent 4xx rejection is
immediate") instead of layers. One run (t6) kept a pure classification section
before the behavior sections, so the recipe is followed but not mechanically.

Limits: the retest is treatment-only, changes two rules at once, and cannot
separate them. Before/after is not a controlled comparison, and n=3 still fits
sampling noise. The fixture, however, discriminated 0/6 before and 3/3 after on
task shape, which is the strongest signal in this record.

## Blocked-routing test

The pilot above used an issue with every template section, so it never exercised
the `blocked` path. This test uses `issue-to-openspec/fixtures/seam-blocked`,
which is the same fixture with two defects:

- the **Acceptance criteria** section is deleted;
- **In scope** says "Partner-level retry count, so each partner can choose three
  or five attempts", while **Out of scope** says "Partner-facing retry
  configuration".

Both call for a question, not an assumption. The skill says a missing section
means amend the issue or return to `issue-interview`, and never guess.

### Method

Six fresh `general` subagents, three per condition, each in its own copy with a
git baseline. Every prompt included "This is my explicit request to proceed and
propose the change", so authorization was not the blocker. Treatment loaded
`issue-to-openspec`; control was told to use its own judgment and load no skill
files.

### Results

| Check | Control (n=3) | Skill (n=3) |
|---|---|---|
| Emitted a `routing_status` / `owner` / `requested_action` block | 0/3 | **3/3** |
| Correctly blocked (`blocked` + `issue-author`, no artifacts) | 0/3 | **1/3** |
| Created change artifacts anyway | 3/3 | 2/3 |
| Named the missing Acceptance section | 0/3 | 2/3 |
| Raised the scope contradiction as a question | 0/3 | 1/3 |

The one correct run (t2) did everything the skill asks: listed the absent
section, quoted the contradiction, drafted acceptance criteria for the author to
confirm rather than adopting them, wrote no artifacts, and ended with
`blocked / issue-author / post questions on the issue`.

### Failure modes

- **t1 missed the missing section outright.** Its report says "All required
  template sections were present; no blocking gaps", resolved the scope
  contradiction by making the attempt count a constructor argument, and proposed
  with `routing_status: ready`.
- **t3 saw the missing section and proceeded anyway.** It treated Outcome as
  acceptance and recorded the assumption, then proposed. That is a documented
  guess, not a silent one, but the skill's precondition does not allow it.
- **All three controls proceeded.** Each interpreted the scope contradiction as
  "internal per-partner value, no partner-facing UI", which is a reasonable
  reading; none asked, and none mentioned the missing Acceptance section.

### Verdict

The routing contract is emitted reliably (3/3), so the skill does what the
workflow needs at the interface. The precondition gate did not hold reliably
under an explicit "proceed" instruction: 1/3 blocked. The failure was narrow: two
runs let authorization override a missing required section. The retest below
tightens the rule and is recorded as a before/after, not a controlled result.

### Gate retest after the patch

Two changes: the precondition says a missing section blocks even when the user
asks to proceed and that Outcome is not Acceptance; a blocked result must name
every missing section and contradiction in `requested_action`.

Three fresh treatment runs, same fixture, same prompt, no control.

| Check | Before (n=3) | After (n=3) |
|---|---|---|
| Blocked with no change artifacts | 1/3 | **3/3** |
| Emitted a routing block | 3/3 | 3/3 |
| Named the missing Acceptance section | 2/3 | **3/3** |
| Raised the scope contradiction | 1/3 | **3/3** |
| Invented or adopted acceptance criteria | 1/3 | 0/3 |

All three runs stopped before explore output became an artifact, and each
`requested_action` named the specific gaps: the absent section, the 3-vs-5
attempt conflict, the partner-config conflict, and what the caller sees on
exhaustion. One run also found a weakness the fixture did not plant: the context
claim that subclasses would reimplement an in-send loop does not follow when the
loop is inherited.

One deviation: t4 wrote `issue-17-questions.md` into the repository. It is a
scratch question file, not a change artifact, and `AGENTS.md` names stdout as the
review destination, so this is a minor routing-destination miss rather than a
gate failure.

Limits: treatment-only, two rules changed at once, n=3, one model family. The
before/after is not a controlled comparison.

## Threats to validity

- Three repetitions per condition, one model family.
- The blocked fixture has one missing heading and one scope contradiction; a
  careful reader can detect either, so the control's 0/3 reflects its choice to
  proceed, not an inability to notice.
- The prompt's explicit "proceed" authorization is pressure that a real
  maintainer might not apply; it is deliberate, to test whether the gate holds.
- The fixture names `deep-module-design` nowhere, but the issue mentions the
  rejected inline loop, which pushes every condition toward a wrapper.
- The missing `openspec-explore` and `openspec-propose` skills make both arms
  improvise the same stages; the treatments were told this explicitly.
- Scoring is manual from files, with one reader.
- The control instruction "do not load any skill files" is stronger than a real
  session where skills are not mentioned at all.

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

Then run six fresh agents with the prompts in "Conditions" and score the
artifacts under `openspec/changes/`.

## Retest with the OpenSpec workflow skills installed

The first record was produced when `openspec-explore` and `openspec-propose`
were absent from the catalog. Every run improvised, and steps 2 and 4 of the
skill could not be followed as written. The six OpenSpec workflow skills are now
installed. This retest uses the same seam fixture and the same prompt, except
that the agents are told to use the workflow skills.

### Method

Three fresh `general` subagents, one per copy, each with a git baseline. Each
loaded `issue-to-openspec`, read `AGENTS.md` and `issue.md`, had explicit
authorization to propose, and was told not to implement, not to edit `src/` or
`tests/`, and not to commit.

### Results

| Check | Original pilot (no workflow skills) | Workflow skills installed |
|---|---|---|
| Loaded `deep-module-design` | 3/3 | 3/3 |
| Loaded `openspec-explore` and `openspec-propose` | 0/3 (absent) | 3/3 |
| Chose the wrapper / seam-preserving design | 2/3 | 2/3 |
| Deletion or test-surface argument | 3/3 | 3/3 |
| Tasks sliced by observable behavior | 0/3; 3/3 after the slicing recipe | 3/3 |
| Created its own approval marker | 1/3; 0/3 after the prohibition | 0/3 |
| Strict validation passes | 3/3 | 3/3 |
| Emitted the routing block | 3/3 | 3/3 |
| Correct routing owner for `ready` | 3/3 | 2/3 |

The task-shape and marker changes came from the earlier skill edits, not from
the pipeline. The pipeline's own contribution is that every run followed
`openspec new change` and the artifact instructions instead of improvising.

One change is attributable to the pipeline: all three runs used
`openspec new change` and the artifact instructions, and all three produced
CLI-scaffolded changes (`.openspec.yaml`, and a `README.md` in one run). None
touched `src/` or `tests/` and none committed.

The design result is unchanged. Two runs chose the `RetryingSender` wrapper; one
(t3) again chose a template method inside `WebhookSender` with a one-attempt
hook, the option the issue says review rejected. It argued the hook prevents
subclass reimplementation, so the conflict was surfaced rather than hidden.

### Routing inconsistency

t2 emitted:

```
routing_status: ready
owner: human
requested_action: proceed to spec-review
```

`human` is a legal enum value, but the next action is the next stage, which
`docs/workflow.md` assigns to `workflow`. The skill lists the four allowed
owners but never says which one a `ready` result uses. t1 and t3 emitted
`owner: workflow`; t2 did not. This is a one-line gap in the interaction
contract, not a pipeline failure.

### Limits

- Three repetitions, one model family, one fixture.
- The prompt named the workflow skills, so this is not a discovery test.
- The fixture issue is complete and pre-authorized; the blocked path is not
  exercised here.

### Owner retest after the patch

One line was added to the interaction contract: on `ready`, use `owner:
workflow` with `proceed to spec-review`; use `human` only when a person must act
before the next stage.

Three fresh runs on the same fixture, same prompt, real workflow skills:

| Check | Before | After |
|---|---|---|
| `ready` with `owner: workflow` | 2/3 | **3/3** |
| Emitted the routing block | 3/3 | 3/3 |
| Loaded `deep-module-design` | 3/3 | 3/3 |
| Chose the wrapper design | 2/3 | 3/3 |
| Created an approval marker | 0/3 | 0/3 |
| Strict validation passes | 3/3 | 3/3 |

The owner inconsistency is closed. The wrapper shift from 2/3 to 3/3 is not
attributable to a one-line routing change; treat it as sampling until a larger
run says otherwise.

## Contract change

The `routing_status` / `owner` / `requested_action` contract used in this record
was retired on 2026-11-04. Skills now end with
`verdict: pass | needs_revision | blocked` and a one-line reason; delivery
belongs to the persona's agent file. Verdict, gate, and finding results in this
record stand; owner and action columns no longer describe the skill.
