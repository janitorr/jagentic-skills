# documentation vs writing-for-agents: README and AGENTS.md

Status: exploratory comparison, n=3 per cell. Three conditions, two artifacts.
No downstream behavioral test: this scores the documents, not whether an agent
later complies with them.

## Question

Does `skills/documentation` produce documents meaningfully optimized for both
human and agent readers, compared with mattpocock's `writing-for-agents`?

## Method

- Conditions: `ours` (`skills/documentation`), `pocock`
  (`vendor/mattpocock-skills/skills/productivity/writing-for-agents/SKILL.md`),
  `control` (no guidance).
- Artifacts: the geoshard README and the dockyard `AGENTS.md` briefs, unchanged
  from `documentation.md`.
- Three fresh `general` subagents per cell, one sample each, same model.
- Guidance was copied to `/tmp` before the runs so the vendor `CLAUDE.md` was
  not auto-injected into the pocock condition.
- Subagents wrote the document and returned headings only.

Caveat on the comparison: `writing-for-agents` is a reference skill for
agent-consumed documents. It has no README structure guidance, so any README
effect comes from its general levers (hierarchy, leading words, pruning,
completion criteria), not from artifact-specific advice.

## Measurements

Averages over three runs.

| Metric | ours | pocock | control |
|---|---|---|---|
| README words | 498 | 363 | 335 |
| README repeated command mentions (of 6 commands checked per run) | 8 total | 3 total | 6 total |
| README completion criteria ("done when...") | 0 | 11 | 0 |
| AGENTS.md words | 232 | 232 | 404 |
| AGENTS.md completion criteria | 0 | 3 | 0 |
| AGENTS.md negations (never/don't/do not/avoid/must not) | 6 total | 0 | 22 total |
| AGENTS.md `<important if>` blocks | 3-4 per file | 0 | 0 |

Heading sequences are in `documentation-vs-writing-for-agents/headings.txt`.

## Findings

1. **Our README recipe causes duplication.** Step 4 orders "quick start" then
   "commands", so every run lists `split`/`validate` twice: once in the quick
   start, once in a command table. Two to three of six commands repeat per run.
   The skill's own step 10 says one meaning, one authoritative place. Pocock's
   hierarchy puts reference in the step that needs it; one run repeated nothing
   and had five completion criteria.

2. **Our README is 37% longer for the same brief** (498 vs 363 words) and adds
   an architecture section the other conditions usually omit. That is not
   automatically worse: our runs explain how tiling and `merge` relate, which is
   the "why" a human maintainer needs. The cost is time-to-first-action.

3. **Agent instructions: equal length, different leverage.** Our AGENTS.md and
   Pocock's are the same average length (232 words). Ours is consistently
   Layout / Commands / Rules with `<important if>` blocks. Pocock's varies but
   carries three levers ours does not:
   - a completion criterion: "A change is done when `pnpm lint`, `pnpm
     typecheck`, and `pnpm test` all pass";
   - positive framing: "`packages/db/migrations/` is generated output. Change
     the Prisma schema, run `pnpm db:migrate`" instead of "never hand-edit";
   - pointers with a branch: "Touching the schema or a query → read
     `packages/db/README.md` before the first edit."
   Our runs produce 0 completion criteria and 6 negations across three files;
   Pocock's produce 3 criteria and 0 negations.

4. **Control is the failure mode both skills avoid.** Un-guided runs average 404
   words, 22 negations, and a command table that restates scripts. Both skills
   prune; Pocock prunes harder and converts prohibitions into consequences.

5. **Our `<important if>` convention is borrowed and environment-specific.**
   The tag comes from humanlayer's `improve-claude-md`, whose rationale is a
   Claude Code system reminder. `AGENTS.md` requires skills to stay
   environment-agnostic; Pocock reaches the same conditional structure with
   plain headings and a triggering sentence. Our tag is unverified in this
   harness and every block costs tokens on every turn.

6. **Both invent facts when the brief is thin.** Pocock's README runs invented
   two incompatible `regions.json` schemas (bbox array in r1, polygon rings in
   r2). Our runs invented `validate` exit behavior and config precedence. Our
   skill's "mark an unknown" rule sits in the reference-page step, not the
   README or agent-instruction steps, so it did not fire.

## Post-patch retest, 2026-11-04

Steps 4 and 8 were patched with borrowings 1-4, then retested in three rounds as
the wording failed:

| Round | Change | Result |
|---|---|---|
| v2 | README path with per-step criteria; agents get a done criterion and positive framing | README duplication fell from 8 to 1 and criteria rose 0 to 16; AGENTS.md grew to 326 words and added a second copy of the gate commands (3 repeats per run); README heading count rose to as many as 11 |
| v3 | "numbered inside one section" | README headings fell to 5-6; duplication stayed near zero; AGENTS.md still repeated the gate commands 3/3 |
| v4 | done criterion must not name the commands again | AGENTS.md repeats fell to 1/3, average 280 words, negations 2 total across three runs |

Final treatment numbers, three runs each:

| Metric | before patch | after patch | pocock | control |
|---|---|---|---|---|
| README words | 498 | 597 | 363 | 335 |
| README repeated commands (total of 6 checks/run) | 8 | 2 | 3 | 6 |
| README completion criteria (total) | 0 | 16 | 11 | 0 |
| AGENTS.md words | 232 | 280 | 232 | 404 |
| AGENTS.md repeated commands (total) | 0 | 3 | 0 | 9 |
| AGENTS.md completion criteria (total) | 0 | 3 | 3 | 0 |
| AGENTS.md negations (total) | 6 | 2 | 0 | 22 |

Net: the README now carries one command per step with a done condition, and the
agent instructions gained a finish line and mostly positive phrasing. The costs
are ~20% more words and one run in three still restating the gate commands. The
remaining duplication comes from keeping a command table and asking for a done
criterion: Pocock avoids it only because he has no table. Dropping our table is
a boundary decision against humanlayer's "keep commands bare", not a wording
fix, so it was left alone.

## What to borrow

Concrete, ordered by evidence strength:

1. **README: fold reference into the sequence.** Applied in step 4.
2. **Agent instructions: add a done criterion.** Applied in step 8.
3. **Agent instructions: state the target, not the ban.** Applied in step 8.
4. **Pointers: name the branch.** Applied in step 8.
5. **Do not invent facts.** Not applied. Extend the reference-page rule to every
   artifact: when the brief is silent about a format, default, or exit code, say
   so rather than supplying a plausible one.

## Limits

- n=3, single model, fictional briefs with no repository convention to match.
  The skill's main instruction, "match the existing convention", was inoperative.
- The metrics measure document properties. They do not show that an agent
  following the Pocock-shaped file complies more often.
- Pocock's runs were more variable in structure (5-9 headings, three different
  README shapes). Our recipe buys determinism; the comparison does not price
  that in.

## Next

- Apply borrowing 5 (do not invent) to the README and agent-instruction steps,
  then re-run the two artifacts.
- Test one file that adds a done criterion and positive phrasing against a
  control, scoring downstream compliance rather than document shape. The current
  evidence is still document shape only.
- Decide whether the command table in agent instructions earns its context load,
  or whether commands should live in the verification list as in the pocock runs.
