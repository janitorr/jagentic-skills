---
name: visual-explainer
description: Use when prose would be slower than a diagram, when explaining architecture, control flow, a diff, or options, when writing a review or PR summary, when teaching a concept, or when debugging where expected and actual diverge.
---

# Visual Explainer

## Environment

The agent file defines the tracker, approval marker, review destination, and
workspace policy. Read it before starting. If an operation you need is not
defined, ask; do not assume a specific CLI or service.

## Overview

One visual that answers the current question beats a page of prose. Pick the
smallest view that makes the point, put it beside the sentence it supports, and
cut the prose that repeats it.

A visual is not decoration. If a sentence is clearer, write the sentence.

## When to Use

- Explaining an architecture, data flow, state machine, or call path.
- Summarizing a diff or pull request for a reviewer.
- Comparing options where the trade-offs are structural.
- Teaching a concept the reader is meeting for the first time.
- A review finding is easier to see than to describe.

## Process

### 1. Name the question

Write the question the visual must answer in one line. "How does a request reach
the database?" and "What changed in this module?" need different views. Do not
draw the system; draw the answer.

### 2. Pick the smallest form

| The point is | Use |
|---|---|
| Logic or an algorithm | Pseudocode |
| Runtime control flow | Call tree |
| UI structure, state, or ownership | Component tree with file paths |
| File responsibility or a refactor | Shallow file tree |
| Interaction, sequence, or data flow | Mermaid sequence or flow diagram |
| What changed, when the shape already exists | Diff of the smallest shape |
| The same fields repeating three or more times | Table |
| Layout, visual state, or density that text cannot carry | One focused HTML artifact |

Use one form, or a few when the question genuinely has several parts. Do not use
all of them.

### Worked example

Question: "How does a request reach the database?"

Form: call tree, because the point is runtime order.

```text
POST /tasks
  validate
    parse body
    reject invalid
  TaskService.create
    insert
  respond 201
```

Paragraph: "The request is validated at the edge, then one service call inserts
it; invalid input never reaches the database."

Nothing else is shown: no unrelated endpoints, no full module tree, no prose
restating each line.

### 3. Ground it

- Use real names, files, commands, and values from the code or the discussion.
- Match the project's vocabulary; do not invent a parallel naming scheme.
- Omit anything the current question does not need: unchanged branches, unrelated
  files, decorative styling.
- For terminal output, use plain ASCII so alignment survives fonts and locales.
  Use Mermaid for relationships and HTML for spatial layouts.

### 4. Pair it with one short paragraph

State what the reader is looking at and what it means. Place the visual next to
that text, not in an appendix. If the paragraph repeats every label, delete the
paragraph; if the visual needs a legend, simplify the visual.

### 5. Adapt to the job

- **Review or PR summary:** show why the change exists and the shape of the
  implementation. Prefer diff views for changes to an existing shape. Omit
  categories that did not change.
- **Decision:** show the options side by side, with the constraint that separates
  them. Recommend one.
- **Teaching:** start from what the reader already knows. Give one tangible win,
  then point to a primary source for depth. Do not teach the whole subject in one
  visual.
- **Debugging:** show the failing path and the boundary where expected and actual
  diverge.

### 6. Save, show, verify

Save the artifact where the agent file's workspace policy allows. Open it if the
environment supports that. If a browser or renderer is available, verify ASCII
alignment, Mermaid syntax, and HTML layout at desktop and mobile widths;
otherwise state that the artifact is unverified. When the visual supports a
review, post it with the review report; the review skill owns the destination.

## Verification

- [ ] The visual answers one named question.
- [ ] The form is the smallest one that carries the point.
- [ ] Names, paths, values, and commands are real.
- [ ] Nothing unchanged or irrelevant is included.
- [ ] A short paragraph states what the visual means.
- [ ] The artifact renders correctly in its target medium.
