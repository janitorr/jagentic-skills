---
name: issue-to-openspec
description: Use when the user invokes /issue-to-openspec, or when ready GitHub issue(s) need OpenSpec planning artifacts. Always explores before proposing; stops before implementation.
disable-model-invocation: true
---

# Issue to OpenSpec

## Overview

Turn one or more GitHub issues into an OpenSpec change. **Explore always runs
first**, even when the issue looks complete. Explore resolves decisions;
`openspec-propose` writes the artifacts; neither implements.

This skill owns the handoff and the exit criteria. OpenSpec owns scaffolding,
schema rules, validation, and artifact paths.

## Preconditions

- A GitHub issue reference. Read it, including comments:
  `gh issue view <number> --json number,title,body,comments`.
- An OpenSpec root. Run `openspec list --json`; if `root` is null, stop and ask
  whether to initialize, target a store, or continue without OpenSpec.
- Project context: `AGENTS.md` / `CLAUDE.md`, `openspec/config.yaml`, and the
  repo's documented commands.
- A clean enough working tree to branch from fresh `main`. Do not stash, merge,
  rebase, or discard the user's work.

## Process

### 1. Read the source

Extract from the issue: problem, outcome, in-scope, out-of-scope, acceptance
criteria, context links, and open questions. Note anything missing; missing
acceptance criteria are a reason to return to `/issue-interview`, not to guess.

Then read the codebase reality: current branch and status, existing specs
(`openspec list --specs --json`), relevant specs in full
(`openspec show "<spec-id>" --type spec`), integration points, nearby tests, and
docs. Record conflicts between the issue and the existing specs.

### 2. Explore (mandatory)

Invoke the `openspec-explore` skill, or `/opsx-explore`, with the brief below.
Do not substitute your own analysis for it, and do not skip it because there
"seems to be enough context". Explore is where scope and design decisions get
settled with the human.

If several issues touch the same capability, explore them together. If one issue
needs multiple independently shippable changes, say so and propose a change
order.

### 3. Exit explore only when the record is complete

- [ ] Scope and non-goals are explicit.
- [ ] Externally observable behavior and acceptance criteria are settled.
- [ ] Impacted capabilities and existing specs are identified.
- [ ] Material design decisions are made, or explicitly deferred with an owner.
- [ ] Risks, unknowns, and rollback or migration concerns are recorded.

If the user wants to stop earlier, write down what remains open and stop without
proposing. Do not let an incomplete exploration become an artifact.

### 4. Propose

Invoke `openspec-propose`, or `/opsx-propose`. It creates the branch and all
required artifacts in dependency order, then commits them. Do not hand-create
artifact files, and do not write a parallel spec format.

If proposal writing exposes a material ambiguity that exploration missed, pause
and return to explore. Do not resolve a scope question inside the artifact.

### 5. Verify before handing off

```bash
openspec status --change "<name>" --json
openspec validate "<name>" --type change --strict
```

Confirm:

- Every required artifact is `done` or deliberately `skipped` with a stated
  reason. Use `requires` edges, not status alone.
- `proposal.md` links or cites the originating issue(s).
- The spec delta states added, modified, and removed requirements with
  testable scenarios.
- `design.md` exists when a material decision needs justification.
- Tasks are vertical slices with acceptance and verification, not a layer-by-layer
  checklist.
- No artifact contains invented APIs, stale file paths, or copied project
  context.

### 6. Stop at the boundary

Report the change name, branch, artifacts, validation result, and any deferred
questions. Then stop. Do not implement, do not run apply, and do not archive.
The next step is `/spec-review`.

## Explore brief

```markdown
## Issue
<number, title, link>

## Problem and outcome
<from the issue>

## Current state
<relevant code, existing specs, constraints>

## Decisions already made
<settled by the issue or the user>

## Open questions
<what explore must resolve>

## Boundaries
No implementation. No code edits. Artifacts only if the user explicitly asks.
```

## Red Flags

- Proposing without exploring, or treating exploration as a formality.
- Writing artifacts by hand instead of using `openspec-propose`.
- Implementing, running apply, or creating a PR in this workflow.
- A task list that is horizontal by layer.
- A spec delta with no scenarios, or acceptance criteria that cannot be tested.
- Silently choosing between conflicting requirements.

## Verification

- [ ] The issue and all comments were read.
- [ ] Explore ran before propose and produced a settled decision record.
- [ ] Required artifacts exist, validate strictly, and trace to the issue.
- [ ] Tasks are vertical slices with verification.
- [ ] No implementation happened.
- [ ] The handoff names `/spec-review` as the next step.
