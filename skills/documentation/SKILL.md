---
name: documentation
description: Use when writing or revising a README, ADR, changelog, reference page, tutorial, runbook, onboarding guide, inline comment, or agent instructions file; when recording why a decision was made or changing a public API; when documentation is stale, duplicated, or missing; or when the user asks how something should be documented.
---

# Documentation

## Environment

The agent file defines the tracker, approval marker, review destination, and
workspace policy. Read it before starting. If an operation you need is not
defined, ask; do not assume a specific CLI or service. Documentation lives where
the repository's convention says.

## Overview

Documentation captures the **why**: context, constraints, alternatives, and
consequences. Code shows what exists; documentation explains why it exists and
what would break if it changed.

Write for two audiences. Humans need to understand, decide, and operate. Agents
need constraints, pointers, and the same durable context. One document can serve
both when each section has a clear job.

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

An RFC is the same record with status `proposed`; reviewers act on the
alternatives and consequences, so those sections carry the weight.

For a changelog, follow the repository's convention. If none exists, use Keep a
Changelog's categories in order: added, changed, deprecated, removed, fixed,
security. Write each entry as what changed for the consumer, not what the
developer did. Keep the categories that apply; when the brief names a category
with no changes, record `None` rather than dropping it silently. Link a compare
range only when the repository URL is known.

### 4. Write the README

Cover, in order: one-paragraph identity, quick start, commands, architecture
overview, and contributing. Every command must be copy-pasteable and current.
Link to ADRs for the reasoning; do not restate it.

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

### 9. Write for the reader

Lead with the decision or the answer. Use concrete names, values, paths, and
commands. Preserve qualifiers, units, and uncertainty. Replace stock
introductions and promotional adjectives with information. When the original
wording is the point, quote it; otherwise paraphrase.

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

Post the result to the review destination defined by the agent file. For a change
description, update the pull request or issue; do not create a parallel report.
This skill owns changelog content and format; `git-workflow` owns when a release
needs one.

## Verification

- [ ] The artifact matches its branch: ADR or RFC, README, reference, procedural
      document, comment, agent rules, or changelog.
- [ ] Audience and job shaped the document without becoming a default section.
- [ ] Decision records include context, alternatives, and consequences.
- [ ] Reference pages document observed behavior and include one complete example.
- [ ] Procedural documents give prerequisites, ordered steps, expected results,
      and a failure path.
- [ ] Commands, paths, and examples were verified.
- [ ] Agent rules use observable conditions, keep commands, and omit
      tool-enforceable style rules.
- [ ] Each meaning has one authoritative source; duplicates were replaced with
      pointers.
- [ ] Stale pages, dead links, and commented-out code were removed.
- [ ] The result reached the configured review destination.
