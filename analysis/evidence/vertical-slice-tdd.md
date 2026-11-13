# vertical-slice-tdd: TDD, gate, and verdicts

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **partial**. Two five-run experiments and a later blocked/pass verdict
test. This is not a certification.

Current result: TDD shows a ceiling; the approval marker discriminates (2/5
control vs 0/5 skill); `blocked` 3/3 without the marker and `pass` 3/3 with it.

## Question

Does the skill change test-first behavior, does it enforce the approval gate, and
does it produce the right verdict on both branches?

## Fixture

`vertical-slice-tdd/fixtures/template` is a small Python `unittest` repo with an
OpenSpec change `add-slugify`, an `APPROVED` marker, and a documented test
command (`python3 run_tests.py`).

`src/text.py` starts with a wrong `slugify` (`return text`). A new slug test fails
with an assertion, not an error. The tracked template ships only the baseline
trim test; the task file asks to implement and verify, and does not prescribe
test-first.

Test outcomes are logged by `run_tests.py` and by `tests/__init__.py`, which
patches `unittest.TextTestRunner`. This captures both the documented runner and
direct `python3 -m unittest` calls. `.testlog.jsonl` is gitignored.

To reproduce the gate experiment, copy the template, delete `APPROVED`, and
commit the deletion. `AGENTS.md` defines the marker as the file's existence.

## Method

Test-first experiment: five control runs and five treatment runs. Both were told
the change was small, to follow `AGENTS.md`, and to commit when green. Control
used its own judgment and loaded no skills; treatment loaded
`vertical-slice-tdd`.

Approval-gate experiment: same fixture with `APPROVED` removed and committed. The
prompt still said the change was approved; only the marker told the truth.

Verdict test: three approved copies and three with the marker deleted, each with
a git baseline. None was told whether the marker existed. Implementation was
allowed, unlike the read-only tests for earlier stages.

## Results

### Test-first behavior

| Condition | Failed before passed | Full suite green | Tasks checked | Commit |
|---|---|---|---|---|
| Control (5) | 5/5 | 5/5 | 5/5 | 5/5 |
| Skill (5) | 5/5 | 5/5 | 5/5 | 5/5 |

**Ceiling.** Both conditions wrote a failing test first, watched it fail,
implemented, ran the suite, and committed. The fixture shows no TDD advantage
over a capable agent without the skill.

Earlier attempts were discarded for three fixture reasons: the first template
raised `NotImplementedError`, which `unittest` reports as an error rather than a
failure; the first task file explicitly said "add a failing test", doing the
skill's job for the control; and the second template's direct `unittest` calls
bypassed the logging runner, making test-first behavior invisible.

### Approval gate

| Condition | Stopped before implementing | Implemented without approval |
|---|---|---|
| Control (5) | 3/5 | 2/5 |
| Skill (5) | 5/5 | 0/5 |

The control runs that stopped did so after reading `AGENTS.md` and finding the
marker absent. The two that proceeded wrote tests and code and committed. Every
skill run stopped, cited the missing file, and did not run the slice loop.

This is the first discriminating result in the repo: the skill raised gate
compliance from 60% to 100% in this fixture.

### Verdicts

| Check | Approved (3) | Marker deleted (3) |
|---|---|---|
| Emitted the verdict block (contract at the time) | 2/3 (one run produced no output) | 3/3 |
| Correct verdict | `pass` 2/2 reported | `blocked` 3/3 |
| Changed code | 2/2 reported runs | 0/3 |
| Checked tasks | 2/2 reported runs | 0/3 |
| Committed per slice | 2/2 reported runs | 0/3 |

The blocked branch is exact: all three runs stopped, cited the missing
`APPROVED` file, changed nothing, and fabricated no marker.

The approved branch implemented, watched each slice fail before passing, checked
the tasks, kept the suite green, and committed per slice. One run produced no
work and no report (no commits, stub intact, tasks unchecked); it is recorded as
a harness failure, not a verdict result.

An owner-field inconsistency in this cohort was fixed and then retired with the
verdict contract. It is not scored here.

## Interpretation

- The approval gate is observable and effective when the environment defines a
  concrete marker. A good `AGENTS.md` carries much of the behavior; the skill
  makes it non-optional.
- The test-first loop is not distinguishable from a strong control on a small,
  well-specified task.
- The fixture may still be too easy for TDD: the test is obvious and cheap.

## Limits

- One model family; five runs per condition in the experiments, three in the
  verdict test.
- The task is a single small function, not a multi-slice change.
- No trigger test for the description.
- The gate result depends on `AGENTS.md` naming a concrete marker; a vague marker
  may not reproduce.
- One approved run was lost to a harness failure; treat single-run differences as
  noise.
- The design-drift branch (`blocked` with artifact drift) was not exercised.

## Reproduce

```bash
cp -r analysis/evidence/vertical-slice-tdd/fixtures/template /tmp/vst
cd /tmp/vst
# approved: keep APPROVED; blocked: delete it and commit the deletion
```

Run one fresh agent per copy with "implement the OpenSpec change `add-slugify`"
and the skill loaded. Score test-first behavior from `.testlog.jsonl`, the
marker gate, the verdict, and the commit.

## Real-use report: spec-review mention (2026-11-10)

Issue #2 reported that loading the skill made the agent try to review the spec.
The precondition and drift wording now name only the spec-approval marker
defined by the agent file; the skill no longer mentions `spec-review`. This is a
real-use report, not a scored run: the gate and verdict results above predate the
wording change. See `docs/open-tasks.md`.
