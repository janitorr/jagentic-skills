---
name: skill-forge
description: Use when creating or revising a skill, when a skill fails to fire, or when an agent follows a skill's letter but misses its intent.
---

# Skill Forge

## Environment

The agent file defines the tracker, approval marker, review destination, and
workspace policy. Read it before starting. If an operation you need is not
defined, ask; do not assume a specific CLI or service. Skills live where the
repository's convention or the agent file says.

## Overview

A skill is behavior-shaping code, not prose. Writing one is test-driven
development applied to documentation: watch an agent fail without it, write the
smallest text that changes that failure, then close the loopholes.

If you did not watch an agent fail without the skill, you do not know whether the
skill teaches the right thing.

## When to Use

- Creating a skill for a reusable, non-obvious technique or workflow.
- Revising a skill that fires at the wrong time, or does not fire.
- An agent follows the letter of a skill but produces the wrong shape.
- A skill has grown long and you need to prune it without losing behavior.

Do not create a skill for a one-off solution, a rule a linter can enforce, or a
project-specific convention that belongs in that project's instructions. This
skill is for `SKILL.md` files; for READMEs, ADRs, or `AGENTS.md`, use
`documentation`.

## Process

### 1. Justify the skill

Answer all three:

- Would you reference this again across projects?
- Is the behavior non-obvious to a capable agent?
- Does it apply beyond one repository or one workflow?

If any answer is no, write a note or a project rule instead.

### 2. Run the baseline (RED)

Run the scenario **without** the skill:

- **Discipline skill** (a rule the agent knows but violates under pressure): use
  a pressure scenario combining time, sunk cost, authority, or exhaustion.
- **Technique skill** (a how-to): use an application scenario and an edge case.
- **Reference skill**: use a retrieval scenario and a gap test.

Capture the exact rationalizations and wrong shapes, verbatim. If the baseline
does not fail, stop; there is nothing to fix.

### 3. Match the form to the failure

| Baseline failure | Write |
|---|---|
| Skips or violates a rule under pressure | Prohibition, rationalization table, stop signals |
| Complies but the output has the wrong shape | Positive recipe: state what the output is, its parts, in order |
| Omits a required element | Required slot in the template the agent fills in |
| Behavior depends on a condition | Conditional keyed to an observable predicate |

For a shaping problem, a prohibition often backfires: it names the unwanted
behavior and gives the agent something to negotiate with. State the target shape
instead.

### 4. Write the minimal skill

- **Name:** letters, numbers, hyphens.
- **Description:** triggers and symptoms, not a workflow summary. An agent that
  reads the summary may skip the body.
- **Overview:** one core principle.
- **Steps:** ordered actions, each with a checkable completion criterion.
- **One excellent example.** One real example beats five mediocre ones. Do not
  translate the same example into five languages.
- **Supporting files:** only for heavy reference or reusable tools. Invoke scripts
  through their interpreter, not by bare path.

### 5. Test the trigger

Test the frontmatter separately from the body. Write six to ten prompts: half
should load the skill, half should not, including prompts that belong to adjacent
skills. Load only the description and check which skill the model selects. Fix
the wording until the should-fire set lands and the should-not-fire set does not.
A skill that never fires passes every body test.

### 6. Micro-test the wording

Before a full scenario run:

1. Use one fresh-context sample per call.
2. Include a no-guidance control. If the control does not fail, stop.
3. Run five or more repetitions per variant.
4. Read every flagged match manually; automated counts overstate both failure
   and success.
5. Treat variance as a metric. If five reps produce five interpretations, tighten
   the wording before adding words.

### 6. Prune

- One meaning, one authoritative place. Delete duplicates rather than syncing
  them.
- Remove no-ops: instructions the agent already follows by default.
- Remove lines that no longer affect behavior.
- Keep reference beside the step that needs it. Disclose heavy reference behind a
  pointer, not material every branch needs.
- Prefer a leading word over a repeated sentence. Define a coined term once.
- Cut sprawl: every extra line is one more to keep relevant.

### 7. Re-test and close loopholes (GREEN, REFACTOR)

Run the same scenarios with the skill. The agent must comply. If it finds a new
rationalization, add one counter and re-test.

Record the evidence where the repo keeps evaluation artifacts: the control
prompt, five repetitions, verbatim baseline failures, with-skill results, and
trigger results. An explained skip names the reason and gets human sign-off;
otherwise the skill is not deployed.

### 8. Deploy one skill at a time

Place the skill in the configured skill directory. If the repository has a
router, index, or docs page, update it in the same change. Report the baseline
failure, the wording that fixed it, and the verification you ran. Do not batch
several untested skills.

## Verification

- [ ] The skill is reusable, non-obvious, and not tool-enforceable.
- [ ] The baseline failure was observed and captured without the skill.
- [ ] The guidance form matches the failure type.
- [ ] The description gives triggers, not a workflow summary.
- [ ] Trigger prompts were tested, including should-not-fire prompts for adjacent
      skills.
- [ ] Every step has a checkable completion criterion.
- [ ] Wording was micro-tested against a no-guidance control, or the skip has a
      named reason and human sign-off.
- [ ] The revised skill passes the same scenario that failed at baseline.
- [ ] The evidence record exists: control, repetitions, baseline failures,
      with-skill results, and trigger results.
- [ ] Duplicates, no-ops, and stale lines were pruned.
- [ ] Router, index, or docs were updated.
- [ ] One skill was deployed and verified before starting the next.
