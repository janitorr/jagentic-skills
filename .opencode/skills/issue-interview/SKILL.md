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

End with a verdict the persona can act on:

```
verdict: pass | blocked
reason: <one line>
```

`pass` means the issue bodies are confirmed and ready to publish. If the user
cannot supply a required section, stop as `blocked` and name the missing
sections and questions. Do not publish a partial issue. Publishing is the
persona's action.

A turn that asks a question is not the end of the stage. Do not emit a verdict
until you publish or block.

## Rules

- **Decisions belong to the human; facts belong to you.** Read the repo, docs,
  and existing issues before asking anything you could verify yourself.
- **One question per turn, with your guess attached.** Ask the single question
  whose answer most changes the issue body, attach a recommended answer, and
  wait. Never send a numbered list of questions, even when the direction is
  settled or the questions look independent; a wall of questions is a form, not
  an interview. A wrong guess is faster for the user to correct than a question
  answered from scratch.
- **Budget the interview.** Stop when the next answer would not change the body.
  Hard cap: eight questions before a draft, counted one per turn. At eight, draft
  and park the rest under Open questions.
- **Only an explicit yes to the body confirms it; publish only after it.**
  "Sounds good", "go ahead", "ship it", "whatever you think", and silence are
  delegation or politeness. Ask for a yes that names the body or its identifier.

## Process

### 1. Ground yourself

Read the repository instructions, relevant source, tests, docs, and open issues.
Look for the repository's issue template (`.github/ISSUE_TEMPLATE/`, or wherever
the repo docs name one) and pick the one that fits the ask. Summarize what you
already know in a few lines so the user does not repeat it.

### 2. State the hypothesis

Write your best read of the ask in one sentence, with a confidence number and,
below 70%, a short reason:

```
HYPOTHESIS: You want a personal experiment tracker, not a team dashboard.
CONFIDENCE: 35% - missing: who reads it, what "early signal" means, what done looks like
```

Open every response with the current confidence, what moved it since the last
response, and what is still missing — including the publish or block response.
If nothing moved, say so. The first response also carries the hypothesis; later
responses carry only the confidence line.

```
CONFIDENCE: 55% (was 40%; support reports are the trigger) - missing: how replay works
```

### 3. Interview

Ask one question per turn: the one whose answer most changes the body, with your
guess attached. Wait for the answer before choosing the next question. Do not
batch questions, even when the direction is settled and the questions look
independent.

For every answer, listen for "what I should want" language: best-practice talk,
convention, buzzwords used as goals. Probe once with: "If you did not have to
justify this to anyone, what would you actually want?"

Stop when every template section (problem, outcome, in scope, out of scope,
acceptance, context) carries a direct user answer or a fact you verified, with
its source noted. No section may rest on an inference. Confidence is the exit
signal: draft when another answer would not change the body. After two responses
with no confidence change, draft and move the remaining questions to Open
questions. If a required section is still missing, block and name it.

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

Use the repository's issue template when one exists: keep its headings and
required fields, add any required section the template omits, and omit its
frontmatter. Otherwise use this template, in the user's language:

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

Report the issue identifiers and links. Then stop. Do not create branches,
OpenSpec changes, or specs in this turn.

## Verification

- [ ] Every response opened with the current confidence, including the publish
      or block response.
- [ ] The interview asked one question per turn and stayed within the budget.
- [ ] No response contained more than one question.
- [ ] The hypothesis and confidence were stated before the first question.
- [ ] Every template section has a direct answer or a verified fact with a
      source; none is inferred.
- [ ] The repository's issue template was used when one exists; otherwise the
      default sections were used.
- [ ] The user explicitly confirmed the issue bodies.
- [ ] The issues exist in the tracker, or the bodies were printed because the
      tracker was unavailable.
- [ ] The handoff names `issue-to-openspec` and the issue identifiers.
