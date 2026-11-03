# Evidence: trigger descriptions

Pilot, three independent repetitions, 35 prompts, descriptions only. This tests
whether the current descriptions route a prompt to the right skill; it does not
test the body or the live runtime selector.

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

## Follow-up

1. Run live selector checks for the adjacent pairs, where a wrong load is most
   costly.
2. Re-run this pilot after any description edit.
3. Pair it with behavioral evidence before marking a skill verified.
