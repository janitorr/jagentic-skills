---
name: vertical-slice-tdd
description: Use when implementing or applying an approved OpenSpec change; when the user says "implement this", "start coding", "apply the change", or "red-green-refactor"; or when about to write production code before a failing test.
---

# Vertical Slice TDD

## Environment

The agent file defines the tracker, approval marker, review destination, and
workspace policy. Read it before starting. If an operation you need is not
defined, ask; do not assume a specific CLI or service.

## Overview

Implement an approved OpenSpec change one vertical slice at a time. Each slice
cuts through the layers needed to make one behavior work, is proven by a test
that was watched failing, and leaves the system green.

OpenSpec supplies the task list, artifact context, and tracked task file. This
skill owns the done condition, the test-first loop, the evidence, and the commit
cadence. The agent file owns the workspace, push, and pull-request policy.

## Interaction contract

End with a routing result the workflow can consume:

```
routing_status: ready | blocked
owner: developer | spec-writer | workflow | human
requested_action: proceed to code-review | update the artifacts | stop for approval
```

Design drift is `blocked` with `owner: spec-writer`; do not continue
implementation. A missing approval marker is `blocked` with `owner: human` and
`stop for approval`. On `ready`, use `owner: workflow` with
`proceed to code-review`; use `developer` only when a developer must act before
the next stage can run. The agent file maps the action to tracker or PR
operations.

## Preconditions

- `spec-review` returned **ready for spec approval**.
- The approval marker defined by the agent file is present on the issue, pull
  request, or change. Check it the way the agent file defines. If it is absent,
  stop; do not infer approval from conversation.
- Resolve the change name. If it is missing, run `openspec list --json` and ask.
- The OpenSpec root exists. If `root` is null, `openspec list` exits 1; stop and
  report it.

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

Handle the returned state before implementing:

- `blocked` with `missingArtifacts`: stop and name the missing artifacts; return
  to `issue-to-openspec` or `spec-review`.
- `all_done`: report completion and hand off to the OpenSpec archive workflow; do
  not implement.
- otherwise: read every path in `contextFiles`, plus the `context` and
  `operationGuidance` fields. Treat `context` as a required constraint and
  `operationGuidance` as advisory; report any conflict with the spec.

Use the tracked task file path returned by `status` / `instructions`; do not
assume it is `tasks.md`.

Use the base branch and workspace isolation defined by the agent file. If either
is undefined, ask. Record the base commit for the review handoff.

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

Determine whether the suite is hermetic: it runs offline, starts no external
services, and its config and commands contain no network or service dependency.
Check the test config and commands; if the environment supports it, run the
focused test with network disabled and record the evidence. If the suite is not
hermetic, plan to run the focused test plus build and record which suites were
excluded and why.

### 3. Rules for every slice

- Test behavior through public seams, not private methods or internal calls.
- Expected values come from an independent source: a literal, a worked example,
  or the spec. Never recompute the answer the way the code does.
- Prefer real implementations over fakes, then stubs, then mocks. Mock only at
  slow, non-deterministic, or external boundaries.
- One behavior per test. An "and" in the name usually means split it.
- Keep tests readable over DRY. Duplication that makes a test self-contained is
  acceptable.
- Refactor after green when it makes the next test cheaper and stays inside the
  slice; commit it with the slice. Standalone refactoring is a separate change.

### 4. Run the slice loop

For each slice:

1. **Name the seam and the first test in one line.** If the seam is new or the
   interface is contested, ask before writing; use `deep-module-design` to place
   it. If it is an existing seam, proceed.
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
8. **Commit.** Commit per slice using the `git-workflow` skill. This skill
   overrides only the cadence: one commit per green slice instead of
   `openspec-apply-change`'s single commit at run completion. `git-workflow` owns
   staging, message, hooks, and pre-commit checks. Push or open a pull request
   only as the agent file's delivery policy allows.

### 5. Pause on design drift

Stop and report when:

- The task is ambiguous.
- The implementation needs behavior the spec does not describe.
- The plan or diff no longer covers the task's stated behavior, or you are about
  to narrow, defer, or accept an exception.
- A task cannot be made green without changing another task's contract.

Update the artifacts through OpenSpec and return to `spec-review`. Implementation
resumes only when the approval marker is present again. Do not absorb scope
silently, and do not rewrite the spec to match the code.

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

Post the handoff to the review destination defined by the agent file. Then hand
off to code review. Do not archive the change.

```
Next: code-review for change <name> at <fixed-point>
```

## Verification

- [ ] The approval marker defined by the agent file is present.
- [ ] The apply state was handled, and `contextFiles`, `context`, and
      `operationGuidance` were read.
- [ ] Every slice was tested through a named seam.
- [ ] Every test was watched failing for the expected reason.
- [ ] Full suite and build pass, or excluded suites are recorded with a reason.
- [ ] Completed tasks are checked only when fully implemented; deferred tasks
      are unchecked with a reason.
- [ ] The handoff records the branch, base commit, fixed point, commands,
      outcomes, and deviations at the configured review destination.
