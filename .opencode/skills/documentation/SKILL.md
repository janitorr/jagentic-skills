---
name: documentation
description: Use when writing or revising a README, ADR or RFC, changelog, release notes, reference page, tutorial, runbook, onboarding guide, inline comment, agent instructions file, or evaluation/evidence report; when recording why a decision was made or what an experiment showed; when documentation is stale, duplicated, or missing; or when the user asks how something should be documented.
---

# Documentation

## Environment

Invoked directly by a human or by an agent mid-task; there may be no agent file.
Read the repository's instructions (`AGENTS.md`, `CONTRIBUTING`, `README`) for
the documentation convention and location. If none exists, use the defaults in
this skill.

## Overview

Documentation captures the **why**: context, constraints, alternatives, and
consequences. Code shows what exists; documentation explains why it exists and
what would break if it changed.

Write for two audiences. Humans need to understand, decide, and operate. Agents
need constraints, pointers, and the same durable context. One document can serve
both when each section has a clear job.

Human-facing documents may carry a visual when the shape is the point: a file
tree for project structure, a sequence diagram for complex call logic. Use
`visual-explainer` for the visual and keep one sentence beside it. Agent-facing
files are read as tokens: keep `AGENTS.md` and other agent instructions
text-first; a visual there costs context without changing behavior.

For skill files, use `skill-forge` instead. This skill covers docs, ADRs, READMEs,
reference pages, changelogs, and project instruction files.

## Process

### 1. Identify the audience and the job

| Audience | Needs |
|---|---|
| Human deciding | Context, options, trade-offs, recommendation |
| Human operating | Quick start, commands, examples, failure modes |
| Human maintaining | Architecture, ownership, gotchas, history |
| Agent working | Constraints, conventions, pointers to authoritative files |

If one document serves several audiences, separate the sections by job. Do not
blend a tutorial, a reference, and a decision record into one undifferentiated
page.

This is a planning step. State the audience and job to yourself; write them into
the document only when the reader needs them, as a runbook names its on-call
reader. Do not add an audience or "about this document" section by default. A
code comment, a changelog entry, and an API page never have one.

### 2. Choose the artifact

| Artifact | Use when | Step |
|---|---|---|
| ADR or RFC | A decision would be expensive to reverse; an RFC is the same record before acceptance | 3 |
| README | Someone needs to run, understand, or contribute to the project | 4 |
| Reference or API page | A public surface needs types, errors, and examples | 5 |
| Tutorial, how-to, or migration guide | A reader must complete a task in order | 6 |
| Runbook | An operator must diagnose and act under time pressure | 6 |
| Onboarding guide | A new team member needs access, context, and a first task | 6 |
| Inline comment | A non-obvious constraint or gotcha lives beside the code | 7 |
| Agent instructions file | The project needs durable rules and pointers for agents | 8 |
| Changelog or release notes | Consumers need to know what changed and whether to care | 3, with `git-workflow` owning release timing |
| Evaluation or evidence report | A run, experiment, or comparison needs a durable verdict and reproduction | 3, with method/results/threats |

Pick one branch and read only the step that owns it. A document that fits no
branch is usually two documents; split it before inventing a format.

### 3. Write the decision record

Match the repository's existing convention before imposing a template. If no
convention exists, use: status, date, context, decision, alternatives considered,
consequences. This skill owns the ADR format; `deep-module-design` triggers an
ADR when a decision is expensive to reverse but does not define the template.

Record the alternatives and why they lost. Do not delete old ADRs; supersede them
with a new record that links back. A decision record without its constraints is
just an announcement.

Keep an ADR in its historical frame. It records what was decided then, under
the constraints of that time; do not add a current-status block that makes it
read as today's guidance. When current practice changes, link forward from the
old record or supersede it with a new one. If a request says to preserve
historical ADRs, amend only the sections it names and keep the original
decisions and consequences intact.

An RFC is the same record with status `proposed`; reviewers act on the
alternatives and consequences, so those sections carry the weight.

For a changelog, follow the repository's convention. If none exists, use Keep a
Changelog's categories in order: added, changed, deprecated, removed, fixed,
security. Write each entry as what changed for the consumer, not what the
developer did. Keep the categories that apply; when the brief names a category
with no changes, record `None` rather than dropping it silently. Link a compare
range only when the repository URL is known.

An evaluation or evidence report is a decision record with evidence. Use:
status, question, method (model and variant, fixture, conditions, repetitions),
results, findings, verdict, threats to validity, and reproduction. Separate the
data from the interpretation, and state what the evidence does not establish.
Link raw metrics or run files instead of pasting them.

### 4. Write the README

Cover, in order: one-paragraph identity, a start-to-finish path, architecture
overview, and contributing. The path is numbered inside one section; each step
carries its command and a completion criterion, so a command appears once and
the reader knows when it worked. Add a reference table only for material no step
reaches. Every command must be copy-pasteable and current. Link to ADRs for the
reasoning; do not restate it. Give the architecture overview two visuals by
default: a file tree of the top-level project structure, and a sequence diagram
of the main request path when it crosses more than one module. Use
`visual-explainer` for both and keep one sentence beside each. Skip a visual only
when the project is a single file or the section is a one-liner.

### 5. Write the reference page

Lead with the endpoint, command, or symbol. Give authentication and required
inputs first, then outputs, then each error with its cause and action, then one
complete example. Use tables for parameters and status codes when the reader
scans rather than reads.

Document the observed behavior. Do not enumerate fields, invent an error
envelope, or promise a limit the source does not show; mark an unknown
explicitly instead.

### 6. Write a procedural document

Tutorials, how-tos, migration guides, runbooks, and onboarding guides are a
sequence a reader follows, so they share a spine. State the outcome in one
sentence. List prerequisites, including access. Number the steps; give each a
copy-pasteable command and the result that confirms it worked. Add what to do
when a step fails. End with the next step or the escalation path.

- **Tutorial or how-to:** one outcome, and no options that do not serve it.
- **Migration guide:** add the before and after state, the breaking changes, the
  order that matters, and how to roll back.
- **Runbook:** the alert and its impact, the states that look alike and how to
  tell them apart, one fix per known cause, warnings beside destructive steps,
  verification, and escalation. Diagnosis comes before the risky step.
- **Onboarding guide:** access prerequisites, a map of repositories or services,
  the first task, required reading, and who to ask. Order it by what unblocks
  the reader, not by team org chart.

When the order or branches are easier to see than to read, add one
`visual-explainer` sequence diagram before the steps; keep the steps themselves
text.

### 7. Write inline documentation

Comment the **why** and the gotcha, not the **what**. A comment that restates the
code should be deleted. Commented-out code should be deleted; history is in git.
Link a non-obvious constraint to its ADR.

The output is one annotated stub: the docstring and the comments in place, not a
document about them. No title, audience line, section headings, summary table, or
second code block, unless you are inserting the stub into a larger document that
already has that structure.

### 8. Write agent instructions

- Keep project identity, map, tech stack, and the command table bare. They apply
  to nearly every task.
- Wrap domain rules in conditionals with observable triggers, for example
  `<important if="you are changing the database schema">`.
- Keep every current command from the original file; fix or remove stale ones.
  Commands are foundational reference.
- Delete rules a linter, formatter, or hook enforces.
- Delete conventions an agent can discover from consistent code patterns.
- Prefer file-path references over code snippets; snippets go stale.
- Keep one authoritative place per rule. Point to it rather than copying it.
- Attach a completion criterion to the command list or the last rule without
  naming the commands again, for example "a change is done when every check in
  the table passes".
- State the target, not the ban: "migrations are generated; edit the schema and
  regenerate" rather than "never edit migrations". Keep a prohibition only as a
  hard guardrail, paired with the action to take.
- Put the trigger in the pointer: "touching the schema, read
  packages/db/README.md", not "see packages/db for details".
- Keep agent instructions text-first. Do not add file trees, sequence diagrams,
  screenshots, or visual one-pagers; agents read tokens, not pixels. A table is
  fine when it compresses a matrix of rules.

### 9. Write for the reader

Lead with the decision or the answer. Use concrete names, values, paths, and
commands. Preserve qualifiers, units, and uncertainty. Replace stock
introductions and promotional adjectives with information. When the original
wording is the point, quote it; otherwise paraphrase.

Use a visual when the reader must see a shape—project structure as a file tree,
complex call logic as a sequence diagram—and a sentence when a sentence is
clearer. A visual is not decoration.

Cite primary sources for technical claims. Verify every command and example
before publishing it.

### 10. Prune

- One meaning, one authoritative file.
- Link to code, configuration, or a spec instead of restating it.
- Remove stale pages, dead links, and duplicate explanations.
- If a document only repeats the code, delete it or replace it with a pointer.

### 11. Review for accuracy and clarity

Check the document against its sources: code, decisions, and external docs.
Restore any lost caveat, verify examples still run, and explain any unresolved
factual question rather than polishing it away. Clarity must not change the
decision or its limits.

Post the result where the repository's convention says, or update the pull
request or issue when one exists; do not create a parallel report. This skill
owns changelog content and format; `git-workflow` owns when a release needs one.

## Verification

- [ ] The artifact matches its branch: ADR or RFC, README, reference, procedural
      document, comment, agent rules, or changelog.
- [ ] Audience and job shaped the document without becoming a default section.
- [ ] Decision records include context, alternatives, and consequences, and stay
      in their historical frame; current guidance links forward or supersedes.
- [ ] Reference pages document observed behavior and include one complete example.
- [ ] Procedural documents give prerequisites, ordered steps, expected results,
      and a failure path.
- [ ] README steps and agent rules state what done means.
- [ ] Commands, paths, and examples were verified.
- [ ] Agent rules use observable conditions, keep commands, and omit
      tool-enforceable style rules.
- [ ] Human-facing documents use a file tree or sequence diagram only where the
      shape is the point; agent instructions stay text-first.
- [ ] Each meaning has one authoritative source; duplicates were replaced with
      pointers.
- [ ] Stale pages, dead links, and commented-out code were removed.
- [ ] The result reached the destination the repository defines, or the working
      tree when none exists.
