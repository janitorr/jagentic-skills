# codebase-design vs deep-module-design: provenance comparison

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **exploratory provenance check**, three runs per arm on the hardened
`deep-module-design` fixture. The original core is cheaper and applies the
deletion test more reliably; the synthesized skill's unique win is the inline
alternatives comparison. The synthesis-only migration, error, and transaction
material did not separate on this fixture.

Follow-up: the deletion test was moved to step 1 after this comparison and
reached 3/3; see `deep-module-design.md`.

## Question

`deep-module-design` is synthesized from mattpocock `codebase-design` plus
interface, simplification, migration, and domain material. Does the synthesis
beat the original core on the same design task, and is the extra text earning
its cost?

## Method

- **Source arm:** `vendor/mattpocock-skills/skills/engineering/codebase-design/SKILL.md`
  only, copied to `/tmp/opencode/eval/deep-module-design/codebase-design/SKILL.md`
  and read by the agent. The supporting `DEEPENING.md` and `DESIGN-IT-TWICE.md`
  were excluded: `DESIGN-IT-TWICE.md` prescribes spawning parallel subagents,
  which is a different workflow, not a content comparison.
- **Synthesis arm:** the three v2 `deep-module-design` runs already recorded.
- **Control:** the three v2 control runs already recorded.
- Same fixture, task, model, read-only rule, and 600-word cap. Source was
  file-injected rather than loaded through the skill tool, because it is not
  installed in this repo's skill catalog.
- Three repetitions per arm. The source runs did not load a skill and did not
  spawn subagents.

## Results

Feature counts, not a single blended score:

| Dimension | Control | `codebase-design` | `deep-module-design` |
|---|---|---|---|
| One-sentence responsibility | 0/3 | 0/3 | 3/3 |
| Deletion test applied explicitly | 0/3 | 3/3 | 1/3 |
| Alternatives compared | 0/3 | 0/3 | 3/3 |
| Typed read/write interface, no SQL/schema leak | 2/3 | 2/3 | 3/3 |
| Seam plus two adapters | 3/3 | 3/3 | 3/3 |
| Test surface crosses the interface | 3/3 | 3/3 | 3/3 |
| Transaction, duplicate error, cache invalidation | 3/3 | 3/3 | 3/3 |
| Reversible migration | 3/3 | 3/3 | 3/3 |
| Median total tokens | 168,157 | 202,577 | 337,675 |
| Median billable input+output | 21,348 | 29,984 | 28,555 |
| Median tool calls | 18 | 17 | 22 |
| Median wall time | 71.3 s | 128.2 s | 95.1 s |

Shared-core score (responsibility 1, interface 2, seam 2, deletion test 1, test
surface 1, alternatives 2; total 9):

| Arm | Scores | Mean |
|---|---|---:|
| Control | 5.5, 5.5, 5.0 | 5.33 |
| `codebase-design` | 6.5, 6.5, 6.0 | 6.33 |
| `deep-module-design` | 8.5, 9.0, 8.5 | 8.67 |

The synthesis's shared-core advantage is almost entirely the alternatives
dimension (+2) and explicit responsibility (+0.5). The original wins the
deletion-test dimension (3/3 against 1/3). Interface completeness is roughly
tied; `codebase-design-3` and `control-3` both use an app-level `ReportInput`
in the Data interface.

The v2 seven-dimension table folds deletion and test surface into one 2-point
score. This table isolates them, so a run without an explicit deletion test
scores 0.5 lower here; the two tables are not directly additive.

## Findings

1. **The original is cheaper.** It used 40% fewer total tokens than the
   synthesis (202.6k against 337.7k) and slightly more billable tokens, with
   similar tool calls. Wall time was higher in this sample (128 s against
   95 s), which the three-run sample cannot explain reliably.

2. **The original applies the deletion test; the synthesis often does not.**
   All three source proposals say what happens if the module is deleted and
   conclude it earns its keep. Only one of three synthesis proposals does.
   The synthesis has nearly the same deletion-test sentence, but it is buried
   in step 4 of a longer process. This is consistent with the repo's earlier
   finding that extra context dilutes a key rule.

3. **The synthesis uniquely produces alternatives.** All three synthesis runs
   compare two or three interfaces and state why the others lost; no source run
   does. The original's alternatives live in `DESIGN-IT-TWICE.md`, which
   prescribes parallel subagents and was excluded. For a single-agent skill,
   the synthesis's inline step 5 is a real addition.

4. **The chosen architecture converges.** All nine proposals, including the
   control, converge on an `IReportStore` with typed reads and writes, a SQLite
   adapter, an in-memory adapter, and a caching decorator. No arm produced a
   materially different module shape. The differences are in the argument and
   the contract, not the architecture.

5. **The synthesis's extra material did not separate.** The source proposals
   handled duplicate exceptions, atomic import, cache invalidation, and
   reversible migration without the synthesis's added migration, error, and
   domain sections. Those sections may still help on other tasks; on this
   fixture they are redundant with a capable base model.

## Verdict

The original core is a credible, cheaper alternative for deep-module design.
The synthesized skill earns its keep for one thing: it forces a single agent to
compare alternatives. Its explicit responsibility statement is a smaller win.

A follow-up moved the deletion test to step 1 as a gate; it reached 3/3, so the
promotion this comparison recommended is now in the skill (see
`deep-module-design.md`). If the synthesis is trimmed, keep the alternatives
step. Do not replace the synthesis with the original wholesale: the original's
design-twice pattern assumes parallel subagents, and this project wants a
single-agent skill.

## Threats to validity

- Three runs per arm, one model, one reader, one fixture.
- The source arm used the core `SKILL.md` only. Including `DEEPENING.md` and
  `DESIGN-IT-TWICE.md` could change the result; the latter is a different
  multi-agent workflow.
- Source content was injected by file, not loaded through the skill tool.
- The fixture is deliberately messy and read-only; an implementation task might
  favor different behavior.
- Cost is cache-heavy and n=3; do not treat the percentages as precise.

## Reproduce

- Source skill: `vendor/mattpocock-skills/skills/engineering/codebase-design/SKILL.md`
- Fixture: `analysis/evidence/deep-module-design/fixtures/shallow-report`
- Proposals: `analysis/evidence/deep-module-design/runs-v2/{codebase-design,v2-skill,v2-control}-{1,2,3}.md`
- Session IDs: `analysis/evidence/deep-module-design/runs-v2/sessions.txt`
