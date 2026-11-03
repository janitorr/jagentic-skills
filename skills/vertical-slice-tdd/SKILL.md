---
name: vertical-slice-tdd
description: Use when the user invokes /vertical-slice-tdd, or after an OpenSpec change passes spec review and human approval. Implements tasks as vertical slices, test-first, with evidence.
disable-model-invocation: true
---

# Vertical Slice TDD

## Overview

Implement an approved OpenSpec change one vertical slice at a time. Each slice
cuts through the layers needed to make one behavior work, is proven by a test
that was watched failing, and leaves the system green.

This skill supplies the execution discipline. OpenSpec supplies the task list,
artifact context, and checkbox state.

## Preconditions

- The change passed `/spec-review`.
- Human approval is recorded in a durable place: an issue or PR comment, a
  label, or an explicit instruction. Do not infer approval from earlier
  conversation.
- Read the change before touching code:

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

Read every file in `contextFiles`, not just `tasks.md`.

## Process

### 1. Map tasks to slices

Read `tasks.md` and decide the working order. A slice is the smallest change
that produces observable behavior and can stand alone.

- If tasks are already vertical, use their order.
- If tasks are horizontal by layer, regroup them into slices without changing
  scope, and state the mapping.
- Note blocking edges and dependencies. Work the frontier: any slice whose
  prerequisites are done.

Do not start with schema, scaffolding, or refactoring unless a slice needs it to
be demonstrable.

### 2. Discover the repo's commands

Before the first test, find how this repository actually builds and tests:
language and package manager, checked-in wrappers, focused-test command, full
suite, lint and type check. Use the repo's commands, never a guessed default.

### 3. Run the slice loop

For each slice:

1. **Agree the seam.** Name the public interface the slice is tested through.
   Prefer an existing seam; if a new one is needed, put it as high as practical.
2. **Write one failing test.** One behavior, one clear name, real code paths.
3. **Watch it fail for the right reason.** Run the focused test. A pass means
   the test is wrong or the behavior already exists. An error means fix the
   test first.
4. **Implement the minimum.** Only enough to pass this test. No speculative
   options, abstractions, or unrelated cleanup.
5. **Watch it pass.** Run the focused test, then the full suite and build.
6. **Update the task checkbox.** Change `- [ ]` to `- [x]` only when the
   specified behavior is fully implemented, not when it is partially done or
   deferred.
7. **Commit.** Stage only the files this slice changed and the tracking file.
   Use the repo's commit convention. Never bypass hooks with `--no-verify`.

### 4. Pause on design drift

Stop and report when:

- The task is ambiguous.
- The implementation needs behavior the spec does not describe.
- You are tempted to narrow, defer, or accept an exception to specified behavior.
- A task cannot be made green without changing another task's contract.

Update the artifacts through OpenSpec and get approval before continuing. Do not
absorb scope silently, and do not rewrite the spec to match the code.

### 5. Complete the change

All tasks checked, full suite and build green, and the verification evidence is
recorded. Report the commands run, their outcomes, and any skipped tasks with
reasons. Then hand off to `/code-review`. Do not archive the change.

## Test rules

- Test behavior through public seams, not private methods or internal calls.
- Expected values come from an independent source: a literal, a worked example,
  or the spec. Never recompute the answer the way the code does.
- Prefer real implementations over fakes, then stubs, then mocks. Mock only at
  slow, non-deterministic, or external boundaries.
- One behavior per test. An "and" in the name usually means split it.
- Keep tests readable over DRY. Duplication that makes a test self-contained is
  acceptable.
- Refactoring belongs to the review pass; do not expand the slice to clean
  unrelated code.

## Red Flags

- Code written before its test.
- A test that passes on the first run.
- A test that asserts on mock interactions rather than observable behavior.
- Updating several checkboxes at once.
- Running the focused test but not the full suite.
- Silently dropping a requirement to make the task fit.
- Claiming done without showing the command output.
- Committing unrelated working-tree changes.

## Verification

- [ ] Human approval was recorded before the first code change.
- [ ] Every slice was tested through an agreed seam.
- [ ] Every test was watched failing for the expected reason.
- [ ] Full suite and build pass with the repo's own commands.
- [ ] Each checked task reflects fully implemented behavior.
- [ ] No spec drift was absorbed silently.
- [ ] The handoff to `/code-review` includes commands and evidence.
