# trigger descriptions: proxy and live selector

Status: **partial**. Proxy and live selector evidence, plus a re-run after the
`documentation` description edit. One model family; the live pass is one rep per
prompt.

Pilot, three independent repetitions, 35 prompts, descriptions only. This tests
whether the current descriptions route a prompt to the right skill; it does not
test the body or the live runtime selector.

A later re-run covers the `documentation` description edit; see
[Re-run after the documentation description edit](#re-run-after-the-documentation-description-edit).

## Method

- Ten current descriptions, no skill bodies.
- A fresh context chose one skill ID or `NONE` for each prompt, applying the
  high-recall policy: load if there is even a slight chance the skill applies.
- 30 should-fire prompts, three per skill, and 5 `NONE` prompts.
- Three repetitions with the same prompt set.

## Results

| Measure | Result |
|---|---|
| Classifications | 105/105 matched the expected choice |
| Consistency | All three reps agreed on every prompt |
| False negatives | 0 |
| False positives | 0 |
| Adjacent-pair confusion | 0 |

Confidence was mostly high. The only low-confidence answer was prompt 35
(“Summarize this PR”) in one rep, which still correctly chose `NONE`.

Adjacent pairs stayed separate:

- spec review vs code review: prompts 7-9 vs 13-15
- spec writer vs documentation: prompts 4-6 vs 28-30
- skill authoring vs documentation: prompts 22-24 vs 28-30
- git workflow vs code review: prompts 25-27 vs 13-15

## Live selector pass

The descriptions-only run is a proxy. The live pass delegated prompts to fresh
agents without naming a skill or pointing at a file.

**Generic prompts, 10.** Eight loaded the local skill. Two loaded a global skill
because the prompt did not signal a project artifact:

| Prompt | Loaded | Read |
|---|---|---|
| Interview me about what I actually want | `interview-me` (global) | Reasonable: no issue was requested |
| Write an ADR for PostgreSQL vs SQLite | `documentation-and-adrs` (global) | Reasonable: no repo docs were named |

**Repo-specific prompts, 4.** Four loaded the local skill:

| Prompt | Loaded |
|---|---|
| Interview me and turn the answers into a GitHub issue in this repo | `issue-interview` |
| Write an ADR in this repo's docs | `documentation` |
| Update this repo's AGENTS.md | `documentation` |
| Review this repo's OpenSpec change proposal | `spec-review` |

The generic collisions are not necessarily defects: a generic interview or ADR
request can belong to the global skill. The project rule now says to prefer the
project skill when both apply.

Harness lesson: the first live pass let agents perform the task. Two of them
edited the repo, and those edits were reverted. Trigger tests must be read-only:
load the skill, report the ID, change nothing.

## Prompt set

| # | Prompt | Expected | Reps |
|---|---|---|---|
| 1 | This idea is vague. Interview me about what I actually want. | issue-interview | 3/3 |
| 2 | The issue has no acceptance criteria. Help me make it ready. | issue-interview | 3/3 |
| 3 | Grill me on this plan before I file it. | issue-interview | 3/3 |
| 4 | Turn issue #42 into an OpenSpec change. | issue-to-openspec | 3/3 |
| 5 | Write the spec for this issue. | issue-to-openspec | 3/3 |
| 6 | Propose this change. | issue-to-openspec | 3/3 |
| 7 | Review this proposal for gaps. | spec-review | 3/3 |
| 8 | Is this OpenSpec change ready to implement? | spec-review | 3/3 |
| 9 | Strict validation failed on this change. What is wrong? | spec-review | 3/3 |
| 10 | Start coding this approved change. | vertical-slice-tdd | 3/3 |
| 11 | Implement the tasks in add-slugify red-green-refactor. | vertical-slice-tdd | 3/3 |
| 12 | Apply this OpenSpec change. | vertical-slice-tdd | 3/3 |
| 13 | Review my PR. | code-review | 3/3 |
| 14 | Review since main. | code-review | 3/3 |
| 15 | Is this ready to merge? | code-review | 3/3 |
| 16 | Show me how the auth flow works. | visual-explainer | 3/3 |
| 17 | Diagram this service boundary. | visual-explainer | 3/3 |
| 18 | Walk me through the data flow visually. | visual-explainer | 3/3 |
| 19 | Should this be one module or two? | deep-module-design | 3/3 |
| 20 | Where should the seam go? | deep-module-design | 3/3 |
| 21 | How do I make this more testable? | deep-module-design | 3/3 |
| 22 | This skill never fires when I need it. | skill-forge | 3/3 |
| 23 | Create a skill for reviewing migrations. | skill-forge | 3/3 |
| 24 | The agent ignores this rule under pressure. | skill-forge | 3/3 |
| 25 | What commit message should I use? | git-workflow | 3/3 |
| 26 | Rebase this branch onto main. | git-workflow | 3/3 |
| 27 | My push was rejected. What now? | git-workflow | 3/3 |
| 28 | Write an ADR for this decision. | documentation | 3/3 |
| 29 | Update the README. | documentation | 3/3 |
| 30 | AGENTS.md is stale and duplicates the README. | documentation | 3/3 |
| 31 | What time is it? | NONE | 3/3 |
| 32 | Rename this variable. | NONE | 3/3 |
| 33 | Format this JSON. | NONE | 3/3 |
| 34 | Explain this regex. | NONE | 3/3 |
| 35 | Summarize this PR. | NONE | 3/3 |

## Limitations

- The test used descriptions only; it did not exercise the live selector or load
  a skill body.
- One model family and three repetitions.
- The prompts are synthetic and short; long sessions may change selection.
- Passing this pilot does not verify that a loaded skill improves the result.

## Earlier follow-up

1. Run live selector checks for the adjacent pairs, where a wrong load is most
   costly.
2. Re-run this pilot after any description edit.
3. Pair it with behavioral evidence before marking a skill verified.

## Re-run after the documentation description edit

The `documentation` description gained `tutorial` and `runbook`, and its body
gained RFC, migration-guide, and release-notes mappings. This re-run covers the
documentation triggers and their adjacencies only, not all ten skills.

### Method

- Same proxy method as the pilot: ten descriptions, no bodies, high-recall,
  one choice per prompt, three fresh contexts.
- Fourteen prompts: three original documentation prompts, five new or
  unverified documentation artifacts, four adjacent-skill prompts, two `NONE`
  prompts.
- Live pass: five fresh agents given only the prompt text and the repository
  path. They were told to load applicable skills, report IDs, and change
  nothing. None edited a file.

### Proxy results

| # | Prompt | Expected | Result |
|---|---|---|---|
| 1 | Write an ADR for this decision. | documentation | 3/3 |
| 2 | Update the README. | documentation | 3/3 |
| 3 | AGENTS.md is stale and duplicates the README. | documentation | 3/3 |
| 4 | Write a tutorial for setting up the dev environment. | documentation | 3/3 |
| 5 | Write a runbook for the export-queue lag alert. | documentation | 3/3 |
| 6 | Write a migration guide for users moving from v1 to v2. | documentation | 3/3 |
| 7 | Write release notes for v2.0. | documentation | 3/3 |
| 8 | Draft an RFC for the new billing service. | documentation | 2/3, 1/3 `issue-to-openspec` |
| 9 | Create a skill for reviewing migrations. | skill-forge | 3/3 |
| 10 | Should this be one module or two? | deep-module-design | 3/3 |
| 11 | Prepare the v2.0 tag and changelog. | git-workflow | 3/3 |
| 12 | Turn issue #42 into an OpenSpec change. | issue-to-openspec | 3/3 |
| 13 | Explain this regex. | NONE | 2/3, 1/3 `visual-explainer` |
| 14 | What time is it? | NONE | 3/3 |

40/42 choices matched. Twelve of fourteen prompts were stable across all three
reps.

### Live selector results

| Prompt | Loaded | Read |
|---|---|---|
| Write a tutorial for setting up the dev environment. | `documentation` | Correct |
| Write a runbook for the export-queue lag alert. | `documentation` + `observability-and-instrumentation` | Correct; global skill adds alert context |
| Draft an RFC for the new billing service. | `documentation-and-adrs` + `api-and-interface-design` | Local skill not loaded |
| Write a migration guide for users moving from v1 to v2. | `documentation` + `deprecation-and-migration` | Correct |
| Write release notes for v2.0. | `documentation` + `git-workflow-and-versioning` | Correct |

### Retest after the RFC wording fix

The description changed from `ADR` to `ADR or RFC` to match the body table. Same
fourteen prompts, three proxy reps, one live rep.

| Measure | Before | After |
|---|---|---|
| RFC prompt, proxy | 2/3 documentation, 1/3 `issue-to-openspec` | 3/3 documentation, all high confidence |
| RFC prompt, live | global skills only | `documentation` + `documentation-and-adrs` |
| All prompts, proxy | 40/42 | 41/42 |

One boundary moved in the retest: release notes went 2/3 documentation and 1/3
`git-workflow` (both med confidence), having been 3/3 before. Across both rounds
that prompt is 5/6 to `documentation`. The `git-workflow` description claims
"changelog, or release", so this is a real adjacent boundary at n=3, not a
regression from the RFC edit.

### What this changed

- The `tutorial`, `runbook`, `migration guide`, and `release notes` triggers
  fire, in both the proxy and the live selector. The three unverified mappings
  named in `documentation.md` now have a run behind them.
- The migration-guide prompt resolved to `documentation` 3/3 even though
  `deep-module-design` also claims "planning a deprecation or migration". The
  release-notes prompt resolved to `documentation` 3/3 even though
  `git-workflow` claims "changelog, or release".
- **RFC was the remaining gap.** The body table said "ADR or RFC", but the
  description said only "ADR". The proxy split 2:1 and the live selector sent
  the prompt to global skills, so the local skill did not load. After adding
  `RFC` to the description, the prompt routed to `documentation` in 3/3 proxy
  reps and in the live selector.
- "Explain this regex" drew one low-confidence `visual-explainer` choice. That
  description did not change, so treat it as sampling noise rather than a
  regression, but it is a false positive in a `NONE` prompt.

### Limitations

- The re-run uses three proxy reps and one live rep per prompt, one model family.
- Live prompts ran in fresh agents with a repository path, not in an interactive
  session, so selection may differ in a long conversation.
- Loading a global adjacent skill alongside the project skill is the intended
  high-recall behavior; it is not scored as a miss.
- The RFC retest reused the same fourteen prompts, so only one wording change is
  isolated; the release-notes split shows n=3 is still noisy at adjacent
  boundaries.
