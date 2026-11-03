---
name: vertical-slice-tdd
description: Use when implementing an approved OpenSpec change test-first, one vertical slice at a time.
---

# Vertical Slice TDD

## Overview

Implement an approved OpenSpec change one vertical slice at a time. Each slice
cuts through the layers needed to make one behavior work, is proven by a test
that was watched failing, and leaves the system green.

OpenSpec supplies the task list, artifact context, and tracked task file. This
skill owns the done condition, the test-first loop, the evidence, and the commit
cadence.

## Preconditions

- `/spec-review` returned **ready for human review**.
- The human set the `ready-for-dev` label on the issue or pull request. Verify it:
  `gh issue view <number> --json labels --jq '.labels[].name'` or
  `gh pr view <number> --json labels --jq '.labels[].name'`. If
  `ready-for-dev` is absent, stop; do not infer approval from conversation.
- Resolve the change name. If it is missing, run `openspec list --json` and ask.
- The OpenSpec root exists. If `root` is null, `openspec list` exits 1; stop and
  report it.

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

Handle the returned state before implementing:

- `blocked` with `missingArtifacts`: stop and name the missing artifacts; return
  to `/issue-to-openspec` or `/spec-review`.
- `all_done`: report completion and suggest `/opsx-archive`; do not implement.
- otherwise: read every path in `contextFiles`, plus the `context` and
  `operationGuidance` fields. Treat `context` as a required constraint and
  `operationGuidance` as advisory; report any conflict with the spec.

Use the tracked task file path returned by `status` / `instructions`; do not
assume it is `tasks.md`.

## Process

### 1. Map tasks to slices

Read the tracked task file and decide the working order. A slice is the smallest
change that produces observable behavior and can stand alone.

- If tasks are already vertical, use their order and keep their IDs.
- If tasks are horizontal by layer, regroup them into slices without changing
  scope. Keep task IDs, and record the slice-to-task mapping in the handoff.
- Work the frontier: any slice whose prerequisites are done.
- If a task turns out horizontal mid-flight, pause and regroup before continuing.

Start with a slice that produces observable behavior; add schema, scaffolding,
or refactoring only when that slice needs it.

### 2. Discover the repo's commands

Before the first test, find how this repository actually builds and tests:
language and package manager, checked-in wrappers, focused-test command, full
suite, lint and type check. Use the repo's commands, never a guessed default.

Determine whether the suite is hermetic: it runs offline and touches no external
services or network. If it is not, plan to run the focused test plus build and
record which suites were excluded and why.

### 3. Rules for every slice

- Test behavior through public seams, not private methods or internal calls.
- Expected values come from an independent source: a literal, a worked example,
  or the spec. Never recompute the answer the way the code does.
- Prefer real implementations over fakes, then stubs, then mocks. Mock only at
  slow, non-deterministic, or external boundaries.
- One behavior per test. An "and" in the name usually means split it.
- Keep tests readable over DRY. Duplication that makes a test self-contained is
  acceptable.
- Refactor after green when it makes the next test cheaper; otherwise skip.

### 4. Run the slice loop

For each slice:

1. **Name the seam and the first test in one line.** If the seam is new or the
   interface is contested, ask before writing. If it is an existing seam,
   proceed.
2. **Write one failing test.** One behavior, one clear name, real code paths.
3. **Watch it fail for the right reason.** Run the focused test. A pass means
   the test is wrong or the behavior already exists. An error means fix the
   test first.
4. **Implement the minimum.** Only enough to pass this test. No speculative
   options, abstractions, or unrelated cleanup.
5. **Watch it pass.** Run the focused test, then the full suite and build. If
   the suite is not hermetic, run the focused test and build, and record the
   excluded suites and reason.
6. **Refactor.** Apply the rule above and re-run the suite.
7. **Check the task.** Mark the task complete in the tracked task file only when
   the specified behavior is fully implemented. Leave deferred tasks unchecked
   with a reason.
8. **Commit.** Commit per slice. This overrides the default `openspec-apply`
   cadence, which commits once when the run completes. Stage only the files this
   slice changed and the tracked task file. Use the repo's commit convention.
   Never bypass hooks with `--no-verify`.

### 5. Pause on design drift

Stop and report when:

- The task is ambiguous.
- The implementation needs behavior the spec does not describe.
- The plan or diff no longer covers the task's stated behavior, or you are about
  to narrow, defer, or accept an exception.
- A task cannot be made green without changing another task's contract.

Update the artifacts through OpenSpec and get approval before continuing. Do not
absorb scope silently, and do not rewrite the spec to match the code.

### 6. Complete the change

Every implemented task is checked. Deferred tasks are left unchecked with a
reason and recorded approval; if any task is deferred, say the change is
incomplete.

The handoff report records:

- Change name and branch.
- Approved base commit and the fixed point for review.
- Every command run and its outcome.
- Excluded suites and why.
- Deferred tasks and deviations from the spec.
- The slice-to-task mapping, when tasks were regrouped.

Then hand off to code review. Do not archive the change.

```
Next: /code-review <change> <fixed-point>
```

## Verification

- [ ] The `ready-for-dev` label is present on the issue or PR.
- [ ] The apply state was handled, and `contextFiles`, `context`, and
      `operationGuidance` were read.
- [ ] Every slice was tested through a named seam.
- [ ] Every test was watched failing for the expected reason.
- [ ] Full suite and build pass, or excluded suites are recorded with a reason.
- [ ] Completed tasks are checked only when fully implemented; deferred tasks
      are unchecked with a reason.
- [ ] The handoff records the branch, base commit, fixed point, commands,
      outcomes, and deviations.
