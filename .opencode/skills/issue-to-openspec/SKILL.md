---
name: issue-to-openspec
description: Use when turning an issue into an OpenSpec change, including its design and task breakdown; when the user says "propose this", "write the spec", or "create a change"; when an issue is ready for planning but context may be missing; or when a reviewer's `needs_revision` must be folded into an existing change.
---

# Issue to OpenSpec

## Environment

The agent file defines the tracker (where issues live and how to read, comment
on, or amend them), the spec-approval marker (the recorded human approval after
spec review, such as a label, comment, file, or pull request state), and the
workspace policy. Read it before starting. If an operation you need is not
defined, stop as `blocked` and name it; do not assume a specific CLI or service.

## Overview

Turn one or more issues into an OpenSpec change, or revise one after review.
The stage is autonomous: it settles the decision record from the issue, code, and
specs, then `openspec-propose` writes the proposed change;
`openspec-update-change` revises an existing one; none implements.

There is no terminal interview. A material decision the issue does not settle is
posted as a question on the issue, and the stage stops as `blocked`.

This skill owns the route, the handoff, and the exit criteria. OpenSpec owns
scaffolding, schema rules, spec reads, validation, artifact paths, revision, and
the `--store` rule. The agent file owns how issues are read and how the workspace
is isolated.

Design decisions use the `deep-module-design` vocabulary when the change creates
or reshapes a module, interface, or seam.

## Interaction contract

End with a verdict the persona can act on:

```
verdict: pass | blocked | needs_revision
reason: <one line naming the missing input or the failing artifact>
```

`pass` means the change is proposed or revised, any reviewer revision was
confirmed by the human in a later run, and it validates strictly. `blocked`
means a required input is missing: an issue section, an answer to a
contradiction, a material decision the issue does not settle, an operation the
agent file does not define, or the confirmation of a revision; name every
missing section, contradiction, and open decision in the reason, because
"provide more context" is not enough. A
reviewer's `needs_revision` is a route signal: take the revision route through
`openspec-update-change`; a revision the human confirms ends as `pass` on a
later run. Return `needs_revision` only when the findings themselves are
unusable, such as two findings that contradict each other. Post blocking
questions on the issue itself, one question per comment, through the tracker
operation the agent file defines; never leave a blocking question only in chat.

Never create the spec-approval marker yourself. It records a human gate; the
reviewer or human sets it after spec review.

## Preconditions

- One or more issue references, or one change name plus the reviewer's findings
  for a revision. If none is supplied, stop as `blocked` and name the missing
  reference. Read each issue and its comments through the tracker. If the
  tracker is unavailable, stop as `blocked` and name it; do not guess the issue.
  Verify every template section: problem, outcome, in scope, out of scope,
  acceptance, and context. If a section is missing or two statements conflict,
  post each as its own question as described below and stop as `blocked`; do
  not guess. A scope item and an out-of-scope item conflict when one implies a
  capability the other denies; post that conflict instead of choosing the
  narrower reading. A missing section is blocking even when the request says to
  proceed, and another section never substitutes for it: Outcome is not
  Acceptance.
- An OpenSpec root. Use the project check in `openspec-propose` and
  `openspec-update-change`; if there is no root, follow their branch for an
  explicit OpenSpec request. Do not re-derive the check here.
- Project context: the target repo's `AGENTS.md` / `CLAUDE.md`,
  `openspec/config.yaml`, and the repo's documented commands.
- A base and workspace policy from the agent file. Record the base commit. If
  the agent file does not define a base or isolation, stop as `blocked` and name
  the missing policy. Do not disturb existing work.

### Blocked questions

There is no terminal interview. Post each question as its own comment through
the tracker operation the agent file defines, then stop as `blocked`; do not
wait for a chat reply. Each comment names the missing section, quotes the
conflicting text, or states the open decision; asks exactly one decision; and
states what it unblocks, so a human can answer it without reading the others.
When the question turns on structure — scope boundaries, a seam, a sequence, or
a state — load `visual-explainer` and include its smallest visual in that
comment; otherwise post it in prose. Amend the issue through the tracker once
the answers arrive.

## Process

### 0. Route the request

- **New change:** no artifacts exist yet. Complete the decision record, then
  `openspec-propose`.
- **Reviewer revision:** an existing change received `needs_revision` and the
  request refines it. Run `openspec-update-change`; it reconciles the existing
  artifacts and confirms each edit. Skip the decision-record checklist unless
  the revision reopens a settled decision.
- **Intent change:** the request changes what the change is for. Start a new
  change with `openspec-propose`; do not rewrite the old one.

### 1. Read the source

Extract from each issue: problem, outcome, in-scope, out-of-scope, acceptance,
context links, and open questions. Then read the codebase reality: current branch
and status, existing specs, relevant code, tests, and docs. Identify impacted
capabilities and read the relevant specs in full; OpenSpec defines the read
commands. Record any conflict between an issue and an existing spec; do not
silently choose one.

### 2. Complete the decision record

Settle the decisions from the issue, its comments, the code, and the specs. Use
`deep-module-design` for module, interface, and seam choices. Do not interview
the user; there is no terminal counterpart.

If a material decision needs an answer the issue does not provide, post one
question per comment on the issue and stop as `blocked`. Do not choose it for
the author, and do not resolve it inside the proposal.

For a reviewer revision, skip this step unless the revision reopens a settled
decision.

Record the decisions where the agent file says: an issue comment, a scratch
decision file, or a design note. The record lists settled decisions, open
questions, risks, and deferred items.

- [ ] Scope and non-goals are explicit.
- [ ] Externally observable behavior and acceptance criteria are settled.
- [ ] Impacted capabilities and existing specs are identified.
- [ ] Material design decisions are made, using `deep-module-design` for module,
  interface, and seam choices; a decision that needs the issue author is posted
  as a question.
- [ ] Risks, unknowns, and rollback or migration concerns are recorded.

A decision record is not the deliverable; the proposed change is. Do not let an
incomplete record become an artifact.

When every item above is settled, proceed to propose. The request that started
the stage authorizes planning. If a new material question appears while
proposing, pause, post the question on the issue, and stop as `blocked`; do not
resolve a scope question inside the artifact.

If several issues touch the same capability, settle them together. If one issue
needs multiple independently shippable changes, propose only the first change,
report the order, and stop; re-run this skill for each subsequent change.

### 3. Propose or revise

When the change creates or reshapes a module, interface, or seam, use
`deep-module-design` to settle the interface, callers, and seam before writing
`design.md` and `tasks.md`. Record the chosen option and why the alternatives
lost.

Write tasks as slices. A slice is the smallest change that produces one
observable behavior and can stand alone. Give each task one behavior or
acceptance criterion plus its verification, and slice by scenario, not by layer.
An error taxonomy, then a retry loop, then wiring is three layers; "a transient
failure recovers" and "exhaustion reports failure" are two slices.

For a new change, invoke `openspec-propose`. For a reviewer revision, invoke
`openspec-update-change`; it owns the existing artifacts and confirms each edit.
End the revision run with `blocked` and `reason: awaiting confirmation of the
revised artifacts`; the request to apply the findings authorizes the edit, not
the result. A later human confirmation through the configured review destination
authorizes `pass`. Do not create a missing artifact from this skill; point to
the workflow's continue path.

Both workflows own scaffolding, artifact order, status, validation, and the
`--store` rule; do not restate them here. This skill supplies the issue trace and
the slicing rule. Branch and commit behavior follow the agent file's workspace
policy; if a workflow would create a branch or commit that the policy forbids,
stop as `blocked` and name the conflict.

If proposal writing exposes a material ambiguity, pause, post the question on
the issue, and stop as `blocked`. Do not resolve a scope question inside the
artifact.

### 4. Verify before handing off

The OpenSpec workflow owns the artifact status; use what it reports. This stage
adds one gate: strict validation.

```bash
openspec validate "<name>" --type change --strict
```

Confirm the result and the issue-specific criteria:

- Every required artifact is `done` or deliberately `skipped` with a stated
  reason, as the OpenSpec workflow reports.
- `proposal.md` links or cites the originating issue(s).
- The spec delta states the operations that apply: added, modified, and removed
  requirements, each with testable scenarios. If `specs` is `skipped`, verify the
  proposal's no-behavior-change rationale instead; do not invent requirements.
- `design.md` exists when a material decision needs justification.
- Tasks are vertical slices with acceptance and verification, not a layer-by-layer
  checklist.
- No artifact contains invented APIs, stale file paths, or copied project
  context.

### 5. Hand off

Report:

- Change name, branch, and the approved base commit.
- Whether this was a new change or a reviewer revision.
- Issue identifiers and links.
- Artifacts created or revised, plus any deliberately skipped.
- Strict validation result.
- Any deferred questions or risks.

Then stop. Do not implement, run apply, or archive.

## Verification

- [ ] Every issue and its comments were read, every template section is
      present, and every internal contradiction was posted as its own question.
- [ ] Missing sections or contradictions were posted as one question per
      comment; structural questions carried a `visual-explainer` visual; the
      stage stopped as `blocked`; no blocking question stayed in chat.
- [ ] The OpenSpec root exists, or the report explains why it does not.
- [ ] The decision record was complete before propose, or the stage stopped as
      `blocked` with one question per comment on the issue.
- [ ] The stage did not interview the user or wait for a terminal reply; an
      incomplete record was not delivered as the result.
- [ ] A reviewer request revised existing artifacts through
      `openspec-update-change`; an intent change started a new change instead;
      the revision run ended `blocked` and `pass` waited for later human
      confirmation.
- [ ] Required artifacts exist, validate strictly, and trace to the issues.
- [ ] The `specs` artifact is either present with testable deltas or deliberately
      skipped with a rationale.
- [ ] Module, interface, or seam decisions used `deep-module-design`, or the
      change does not touch them.
- [ ] The handoff records the change, branch, base commit, issues, and validation
      result.
- [ ] No implementation happened.
