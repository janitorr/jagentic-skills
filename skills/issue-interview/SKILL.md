---
name: issue-interview
description: Use when an ask is vague or missing who, why, success criteria, or constraints; when acceptance criteria are unclear or scope is likely to change; when the user says "interview me", "grill me", "stress-test this", or "what do I actually want"; or when an issue must be created or amended before planning.
---

# Issue Interview

## Environment

The agent file defines the tracker, approval marker, review destination, and
workspace policy. Read it before starting. If an operation you need is not
defined, ask; do not assume a specific CLI or service.

## Overview

The issue is the source of truth for everything downstream: OpenSpec scope, spec
review, and code review. Get it wrong and every later gate reviews the wrong
thing.

The output is one or more issues in the configured tracker, not a plan and not a
spec. Not for mechanical changes with unambiguous acceptance criteria.

## Interaction contract

End with a routing result the workflow can consume:

```
routing_status: ready | blocked
owner: issue-author | workflow | human
requested_action: publish issues | answer the missing questions
```

If the user cannot supply a required section, stop as `blocked` with the missing
sections and questions. Do not publish a partial issue. The agent file maps
`requested_action` to tracker operations.

## Rules

- **Decisions belong to the human; facts belong to you.** Read the repo, docs,
  and existing issues before asking anything you could verify yourself.
- **Intent questions: one at a time, with your guess attached.** A wrong guess is
  faster for the user to correct than a question answered from scratch.
- **Design questions: one frontier round.** The frontier is every question whose
  prerequisites are settled. Number each question, attach a recommended answer,
  and wait for the answers before the next round.
- **Only an explicit yes confirms the issue bodies; publish only after it.**
  Treat "sounds good", "whatever you think", and silence as delegation or
  politeness.

## Process

### 1. Ground yourself

Read the repository instructions, relevant source, tests, docs, and open issues.
Summarize what you already know in a few lines so the user does not repeat it.

### 2. State the hypothesis

Write your best read of the ask in one sentence, with a confidence number and,
below 70%, a short reason:

```
HYPOTHESIS: You want a personal experiment tracker, not a team dashboard.
CONFIDENCE: 35% - missing: who reads it, what "early signal" means, what done looks like
```

Re-state the confidence after each round.

### 3. Interview

When the uncertainty is intent, ask one question at a time. When a direction
exists and the uncertainty is the design tree, ask the whole frontier in one
round.

For every answer, listen for "what I should want" language: best-practice talk,
convention, buzzwords used as goals. Probe once with: "If you did not have to
justify this to anyone, what would you actually want?"

Stop when every template section (problem, outcome, in scope, out of scope,
acceptance, context) carries a direct user answer or a fact you verified, with
its source noted. No section may rest on an inference. If confidence has not
risen across two rounds, name the missing foundation, ask the user to supply or
explicitly defer it, and stop the turn if they cannot.

### 4. Split into issues

One issue per independently testable capability. If the work bundles several,
propose a small capability map first and confirm the split before writing issue
bodies:

```markdown
| Capability | Responsibility | Depends on |
|---|---|---|
| identity | accounts, sessions | - |
| billing | plans, invoices | identity |
```

### 5. Restate each issue

Use this template, in the user's language:

```markdown
## Problem

## Outcome
What changes for the user, in observable terms.

## In scope

## Out of scope
The non-goals you explicitly agreed on.

## Acceptance criteria
- [ ] Testable condition

## Context
Links to code, docs, prior issues, or designs that ground the work.

## Open questions
Anything deliberately deferred, and who decides it.
```

The out-of-scope section is not optional. Silent disagreement about non-goals is
half of misalignment.

### 6. Confirm and publish

Present the issue bodies and ask for an explicit yes. On yes, publish through the
tracker operation the agent file defines, one issue at a time. To amend an
existing issue, use the tracker's amend operation; never create a duplicate.

If the tracker is unavailable, print the finished bodies and stop.

Report the issue identifiers and links. Then hand off:

```
Next: issue-to-openspec for issues <identifier> [<identifier>...]
```

Do not create branches, OpenSpec changes, or specs in this turn.

## Verification

- [ ] The hypothesis and confidence were stated before the first question.
- [ ] Every template section has a direct answer or a verified fact with a
      source; none is inferred.
- [ ] The user explicitly confirmed the issue bodies.
- [ ] The issues exist in the tracker, or the bodies were printed because the
      tracker was unavailable.
- [ ] The handoff names `issue-to-openspec` and the issue identifiers.
