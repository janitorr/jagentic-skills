---
name: visual-explainer
description: Use when the user says "show me", "visualize", "make it visual", "draw", "diagram", "sketch", "chart", "map this out", "walk me through", or "show the flow"; when explaining architecture, control flow, a diff, options, or a review; when teaching or debugging; or whenever a diagram would land faster than a paragraph, even if the user did not ask for one.
---

# Visual Explainer

## Environment

Invoked directly by a human or by an agent mid-task; there may be no agent file.
Read the repository's instructions for where artifacts live. If none exists, use
`docs/` or the task folder.

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
- **Issue brief or one-pager:** a standalone page for one issue. Lead with the
  problem and outcome, then one timeline, call path, or decision table, then
  scope, acceptance, and residual risk. Include the code shape when the issue
  changes code, and a short test or verification table when acceptance matters.

### One-pager recipe

A one-pager is one self-contained HTML file for one issue:

- Inline CSS; no external scripts, fonts, or network requests.
- Use the issue's real values: file paths, attempt counts, statuses, dates.
- Lead with the question and the smallest visual, then support it with scope,
  acceptance, and residual risk. Add the code shape and a test table when the
  issue has them.
- Match the project's palette and type when they exist; otherwise default to a
  dark, low-glare neutral, not a full-page white sheet.
- Set a viewport, check desktop and mobile widths, and add print styles.
- Save it at a predictable path the repository allows, and open it.

### 6. Save, show, verify

Save the artifact where the repository's convention allows, or in `docs/` when
there is none. Open it if the environment supports that. If a browser or
renderer is available, verify ASCII alignment, Mermaid syntax, and HTML layout at
desktop and mobile widths; otherwise state that the artifact is unverified. When
the visual supports a review, post it with the review report; the review skill
owns the destination.

## Verification

- [ ] The visual answers one named question.
- [ ] The form is the smallest one that carries the point.
- [ ] Names, paths, values, and commands are real.
- [ ] Nothing unchanged or irrelevant is included.
- [ ] A short paragraph states what the visual means.
- [ ] The artifact renders correctly in its target medium.
- [ ] A one-pager is self-contained: no external scripts, fonts, or network
      requests.
