---
name: issue-interview
description: Use when the user invokes /issue-interview, when an ask is underspecified, or when work needs GitHub issue(s) before an OpenSpec change. Interviews one decision at a time and publishes issues only after explicit confirmation.
disable-model-invocation: true
---

# Issue Interview

## Overview

The issue is the source of truth for everything downstream: OpenSpec scope,
spec review, and code review. Get it wrong and every later gate reviews the
wrong thing.

The output is one or more GitHub issues, not a plan and not a spec. Each issue
carries the problem, the outcome, scope, non-goals, acceptance criteria, and
links to the code and docs that ground it.

## When to Use

- The user invokes `/issue-interview`.
- The ask is missing who it is for, why now, what success looks like, or the
  binding constraint.
- A direction is chosen but the boundaries are still fuzzy.
- You are about to plan work and no issue exists yet.

**When NOT to use:** mechanical changes with unambiguous acceptance criteria,
pure information requests, or any context without a responsive human.

## Rules

- **Decisions belong to the human; facts belong to you.** Read the repo, docs,
  and existing issues before asking anything you could verify yourself.
- **One question at a time when intent is unclear.** Attach your guess and the
  reasoning behind it. A wrong guess is faster for the user to correct than a
  question answered from scratch.
- **Switch to rounds when a direction exists.** If the uncertainty is a design
  tree, number every currently unblocked question, attach a recommended answer,
  and wait for the answers before the next round. A question that depends on
  another open question belongs to a later round.
- **Silence is not agreement.** "Sounds good", "whatever you think", and "sure,
  let's go" are delegation or politeness, not confirmation.
- **Do not publish until the user says yes.**

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

### 3. Interview

Choose the rhythm from the shape of the uncertainty:

| Uncertainty | Rhythm |
|---|---|
| Intent: who, why, success, constraint | One question at a time, guess attached |
| Design: several decisions hang off one direction | Frontier rounds, every question with a recommendation |
| A fact you can look up | Do not ask; inspect, then state what you found |

For every answer, listen for "what I should want" language: best-practice talk,
convention, buzzwords used as goals. Probe once with: "If you did not have to
justify this to anyone, what would you actually want?"

Stop when you can predict the user's reaction to the next three questions you
would ask. If several rounds pass without confidence rising, say so and step
back; something foundational is missing.

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

Do not split a single capability just to make more issues.

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

Present the issue bodies and ask for an explicit yes. On yes, publish with
`gh issue create --title "<title>" --body-file <path>`, one issue at a time, and
report the URLs. Apply labels only when the repository has a documented
convention.

Then stop. Do not create branches, OpenSpec changes, or specs in the same turn.

## Red Flags

- Three or more questions in one message when intent is still unclear.
- A question without your guess attached.
- Accepting a sophistication-signaling answer without probing.
- Publishing before an explicit yes.
- An issue with no out-of-scope section or no testable acceptance criterion.
- Starting OpenSpec work in the same turn as the interview.

## Verification

- [ ] The hypothesis and confidence were stated before the first question.
- [ ] Every factual question you could answer yourself was answered by
      inspection instead.
- [ ] Every issue states problem, outcome, in scope, out of scope, acceptance,
      and context.
- [ ] The user explicitly confirmed the issue bodies.
- [ ] Each issue is independently testable and traceable to one capability.
- [ ] The turn ended after publishing; no downstream work started.
