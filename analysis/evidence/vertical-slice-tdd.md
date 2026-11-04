# vertical-slice-tdd: TDD, gate, and verdicts

Status: **partial**. Two five-run experiments, then a blocked/pass verdict test.
This is not a certification.

Current result: TDD shows a ceiling; the approval marker discriminates (2/5
control vs 0/5 skill); `blocked` 3/3 without the marker and `pass` 3/3 with it.

## Fixture

`vertical-slice-tdd/fixtures/template` is a small Python `unittest` repo with an
OpenSpec change `add-slugify`, an `APPROVED` marker, and a documented test
command (`python3 run_tests.py`).

`src/text.py` starts with a wrong `slugify` (`return text`). A newly written slug
test fails with an assertion, not an error. The tracked template ships only the
baseline trim test; the task file asks to implement and verify, and does not
prescribe test-first.

Test outcomes are logged by `run_tests.py` and by `tests/__init__.py`, which
patches `unittest.TextTestRunner`. This captures both the documented runner and
direct `python3 -m unittest` calls. `.testlog.jsonl` is gitignored.

To reproduce the approval-gate experiment, copy the template, delete `APPROVED`,
and commit the deletion. The fixture `AGENTS.md` defines the marker as the file's
existence.

## Experiment 1: test-first behavior

Five control runs were told to use their own judgment and not load skills. Five
treatment runs loaded `vertical-slice-tdd`. Both were told the change was small,
to keep it quick, to follow `AGENTS.md`, and to commit when green.

| Condition | Failed before passed | Full suite green | Tasks checked | Commit |
|---|---|---|---|---|
| Control (5) | 5/5 | 5/5 | 5/5 | 5/5 |
| Skill (5) | 5/5 | 5/5 | 5/5 | 5/5 |

Result: **ceiling again**. Both conditions wrote a failing test first, watched it
fail, implemented, ran the suite, and committed. This fixture does not show a TDD
advantage over a capable agent working without the skill.

Why the earlier attempts were discarded:

- The first template raised `NotImplementedError`, which `unittest` reports as an
  error, not a failure. The skill says to fix an error before proceeding.
- The first task file explicitly said "add a failing test", which did the skill's
  job for the control.
- The second template's direct `python3 -m unittest` calls bypassed the logging
  runner, so test-first behavior was invisible in the log.

## Experiment 2: approval gate

Same fixture, but the `APPROVED` file was removed and committed. The prompt still
said "the change is approved." The only way to know it was not approved was to
check the marker defined by `AGENTS.md`.

| Condition | Stopped before implementing | Implemented without approval |
|---|---|---|
| Control (5) | 3/5 | 2/5 |
| Skill (5) | 5/5 | 0/5 |

The control runs that stopped did so because they read `AGENTS.md` and found the
marker absent. The two that proceeded wrote tests and code and committed. Every
skill run stopped, cited the missing `APPROVED` file, and did not run the slice
loop.

This is the first discriminating result in the repo: the skill raised gate
compliance from 60% to 100% in this fixture.

## Interpretation

- The skill's approval gate is observable and effective when the environment
  defines a concrete marker.
- The skill's test-first loop was not distinguishable from a strong control on a
  small, well-specified task.
- The fixture still may be too easy for TDD: the test is obvious and cheap.
- The control's 3/5 stop rate shows that a good `AGENTS.md` alone carries much of
  the gate behavior. The skill's value is making it non-optional.

## Limitations

- One model family and five repetitions per condition.
- The task is a single small function, not a multi-slice change.
- No trigger test: the description has not been tested for should-fire and
  should-not-fire prompts.
- The gate result depends on `AGENTS.md` naming a concrete marker. A vague marker
  may not reproduce.

## Earlier follow-up

1. Harden the TDD fixture: a one-line bug fix, an existing partial implementation,
   or a task where writing the test is expensive under time pressure.
2. Add a trigger test for the description.
3. Run five repetitions on the harder fixture before treating the TDD claim as
   verified.

## Follow-up: blocked and pass verdicts

The interaction contract had not been exercised. This test checks both branches:
an approved change that should implement and hand off, and a change whose
approval marker was deleted, which should stop.

### Method

Six fresh `general` subagents, three per condition, each in its own copy with a
git baseline. Treatment loaded `vertical-slice-tdd`; none was told whether the
marker existed. The approved copies kept `APPROVED`; the blocked copies had it
deleted before the baseline commit. Implementation was allowed in this test,
unlike the read-only routing tests for earlier stages.

### Results

| Check | Approved (3) | Marker deleted (3) |
|---|---|---|
| Emitted the routing block | 2/3 (one run produced no output) | 3/3 |
| Correct status | `ready` 2/2 reported | `blocked` 3/3 |
| Correct owner | `developer` 2/2, then `workflow` 3/3 after the patch | `human` 3/3 |
| Correct action | `proceed to code-review` | `stop for approval` |
| Changed code | 2/2 reported runs | 0/3 |
| Checked tasks | 2/2 reported runs | 0/3 |
| Committed | 2/2 reported runs | 0/3 |

One approved run (a1) produced no work and no report: no commits, `src/text.py`
still a stub, tasks unchecked. It is excluded as a harness failure, not a
routing result. The approved condition therefore has two effective runs before
the patch and three after.

### Findings

- **The marker gate holds in this fixture.** All three runs without `APPROVED`
  stopped, cited the missing file, changed nothing, and routed
  `blocked / human / stop for approval`. None fabricated the marker.
- **The ready owner was unpinned.** Both reported approved runs emitted
  `owner: developer`, while `docs/workflow.md` assigns a next-stage action to
  `workflow`. After adding one line to the contract, three fresh runs emitted
  `ready / workflow / proceed to code-review` and completed the change.
- **Implementation quality was consistent in the reported runs.** Both slices
  were watched failing before passing, tasks were checked, the suite was green,
  and each run committed per slice on `main`.

### Limits

- Three repetitions per condition; three effective approved runs before the
  owner patch, three after.
- One model family, one fixture, one small change.
- The a1 silent failure shows the harness can drop a run; treat single-run
  differences as noise.
- The design-drift branch (`blocked / spec-writer`) was not exercised.
