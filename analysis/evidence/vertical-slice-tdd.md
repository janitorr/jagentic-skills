# Evidence: vertical-slice-tdd

Two experiments, five fresh-context runs per condition each. This is a partial
record, not a certification.

## Fixture

`fixtures/template` is a small Python `unittest` repo with an OpenSpec change
`add-slugify`, an `APPROVED` marker, and a documented test command
(`python3 run_tests.py`).

`src/text.py` starts with a wrong `slugify` (`return text`), so a slug test
fails with an assertion, not an error. The task file asks only to implement and
verify; it does not prescribe test-first.

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

## Follow-up

1. Harden the TDD fixture: a one-line bug fix, an existing partial implementation,
   or a task where writing the test is expensive under time pressure.
2. Add a trigger test for the description.
3. Run five repetitions on the harder fixture before treating the TDD claim as
   verified.
