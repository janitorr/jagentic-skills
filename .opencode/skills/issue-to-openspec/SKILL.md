---
name: issue-to-openspec
description: Use when turning an issue into an OpenSpec change; when the user says "propose this", "write the spec", "explore this issue", or "create a change"; or when an issue is ready for planning but context may be missing.
---

# Issue to OpenSpec

## Environment

The agent file defines the tracker, approval marker, review destination, and
workspace policy. Read it before starting. If an operation you need is not
defined, ask; do not assume a specific CLI or service.

## Overview

Turn one or more issues into an OpenSpec change. Explore always runs first, even
when the issue looks complete. Explore resolves decisions; `openspec-propose`
writes the artifacts; neither implements.

This skill owns the handoff and the exit criteria. OpenSpec owns scaffolding,
schema rules, validation, artifact paths, and the `--store` rule. The agent file
owns how issues are read and how the workspace is isolated.

## Interaction contract

End with a routing result the workflow can consume:

```
routing_status: ready | blocked | needs_revision
owner: issue-author | spec-writer | workflow | human
requested_action: post questions on the issue | update the spec artifacts | proceed to spec-review
```

Missing issue context is `blocked` with `owner: issue-author`; the agent file
posts the questions and marks the issue awaiting information. Artifact changes
after review are `needs_revision` with `owner: spec-writer`. Never leave a
blocking question only in chat.

## Preconditions

- One or more issue references. If none is supplied, ask. Read each issue and its
  comments through the tracker. If the tracker is unavailable, ask the user to
  paste the issue bodies. Verify every template section: problem, outcome, in
  scope, out of scope, acceptance, and context. Missing sections mean amend the
  issue through the tracker or return to `issue-interview`; do not guess.
- An OpenSpec root. Run `openspec list --json`. If `root` is null, the command
  exits 1; that is the answer, not a CLI failure. Stop and ask whether to
  initialize or target a store.
- Project context: the target repo's `AGENTS.md` / `CLAUDE.md`,
  `openspec/config.yaml`, and the repo's documented commands.
- A base and workspace policy from the agent file. Record the base commit. If
  the agent file does not define a base or isolation, ask. Do not disturb
  existing work.

If the project uses an OpenSpec store, append `--store <id>` to the OpenSpec
commands below as its store rule requires.

## Process

### 1. Read the source

Extract from each issue: problem, outcome, in-scope, out-of-scope, acceptance,
context links, and open questions. Then read the codebase reality: current branch
and status, existing specs (`openspec list --specs --json`), relevant specs in
full (`openspec show "<spec-id>" --type spec`), integration points, nearby tests,
and docs. Record any conflict between an issue and an existing spec; do not
silently choose one.

### 2. Explore

Invoke the `openspec-explore` skill with the brief below. Explore owns the
exploration and runs even when the issue looks complete.

```markdown
## Issues
<identifiers, titles, links>

## Problem and outcome
<from the issues>

## Current state
<relevant code, existing specs, constraints>

## Decisions already made
<settled by the issues or the user>

## Open questions
<what explore must resolve>

## Boundaries
No implementation. No code edits. Artifacts only if the user explicitly asks.
```

If several issues touch the same capability, explore them together. If one issue
needs multiple independently shippable changes, propose only the first change,
report the order, and stop; re-run this skill for each subsequent change.

### 3. Exit explore only when the decision record is complete

Record the exploration where the agent file's review destination says: an issue
comment, a scratch decision file, or a design note. The record lists settled
decisions, open questions, risks, and deferred items.

- [ ] Scope and non-goals are explicit.
- [ ] Externally observable behavior and acceptance criteria are settled.
- [ ] Impacted capabilities and existing specs are identified.
- [ ] Material design decisions are made, or explicitly deferred with an owner.
- [ ] Risks, unknowns, and rollback or migration concerns are recorded.

If the user wants to stop earlier, write the partial record to the same place and
stop without proposing. Do not let an incomplete exploration become an artifact.

Before proposing, ask for an explicit request to proceed, such as "propose it".
Exploration alone does not authorize artifact creation.

### 4. Propose

Invoke the `openspec-propose` skill. OpenSpec creates the artifacts. Branch and
commit behavior follow the agent file's workspace policy; if propose would create
a branch or commit that the policy forbids, stop and ask.

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
- The spec delta states the operations that apply: added, modified, and removed
  requirements, each with testable scenarios. If `specs` is `skipped`, verify the
  proposal's no-behavior-change rationale instead; do not invent requirements.
- `design.md` exists when a material decision needs justification.
- Tasks are vertical slices with acceptance and verification, not a layer-by-layer
  checklist.
- No artifact contains invented APIs, stale file paths, or copied project
  context.

### 6. Hand off

Report:

- Change name, branch, and the approved base commit.
- Issue identifiers and links.
- Artifacts created, plus any deliberately skipped.
- Strict validation result.
- Any deferred questions or risks.

Then stop. Do not implement, run apply, or archive. Hand off:

```
Next: spec-review for change <name>
```

## Verification

- [ ] Every issue and its comments were read, and every template section is
      present.
- [ ] The OpenSpec root exists, or the report explains why it does not.
- [ ] Explore ran before propose, and the decision record exists and the user
      explicitly asked to proceed.
- [ ] Required artifacts exist, validate strictly, and trace to the issues.
- [ ] The `specs` artifact is either present with testable deltas or deliberately
      skipped with a rationale.
- [ ] The handoff records the change, branch, base commit, issues, and validation
      result.
- [ ] No implementation happened.
