---
name: issue-interview
description: Use when an ask is underspecified (missing who, why, success, or constraint), when the user says "interview me" or "grill me", or when work needs a GitHub issue before planning.
---

# Issue Interview

## Overview

The issue is the source of truth for everything downstream: OpenSpec scope, spec
review, and code review. Get it wrong and every later gate reviews the wrong
thing.

The output is one or more GitHub issues, not a plan and not a spec. Not for
mechanical changes with unambiguous acceptance criteria.

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
risen across two rounds, name the missing foundation and step back; do not keep
grinding.

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

Present the issue bodies and ask for an explicit yes. On yes:

1. Check `gh auth status` and that the repository has a GitHub remote. If either
   is unavailable, print the finished bodies and stop.
2. Write each body to `${TMPDIR:-/tmp}/issue-<slug>.md`.
3. Publish with `gh issue create --title "<title>" --body-file <path>`, one
   issue at a time.
4. To amend an existing issue instead, use
   `gh issue edit <number> --body-file <path>`. Never create a duplicate.

Report the issue numbers and URLs. Then end with the next command:

```
Next: /issue-to-openspec <number> [<number>...]
```

Do not create branches, OpenSpec changes, or specs in this turn.

## Verification

- [ ] The hypothesis and confidence were stated before the first question.
- [ ] Every template section has a direct answer or a verified fact with a
      source; none is inferred.
- [ ] The user explicitly confirmed the issue bodies.
- [ ] The issues exist on GitHub, or the bodies were printed because `gh` or the
      remote was unavailable.
- [ ] The next `/issue-to-openspec` command lists the issue numbers.
