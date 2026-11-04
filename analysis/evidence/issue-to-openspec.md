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
- The task-shape rule in the skill is not followed by the skill's own runs, so
  the body needs a slicing recipe, not another checklist item.
- The approval-marker rule needs an explicit owner.

## Threats to validity

- Three repetitions per condition, one model family.
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
