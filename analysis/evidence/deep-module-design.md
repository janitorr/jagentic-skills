# deep-module-design: shallow C# module baseline

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **partial**, three runs per condition on the baseline, a harder six-run
retest, and a three-run deletion-test retest. The skill added a responsibility
statement, explicit interface invariants, and an alternatives comparison in 3/3
runs; the control produced none of those. The selected design did not materially
improve against a strong control, and one baseline skill run put a test-only
method on the production interface. The counter is applied; the harder retest
did not reproduce the loophole, but the task and wording changed together, so
the counter is not isolated. Moving the deletion test to step 1 raised it from
1/3 to 3/3; two single-occurrence interface smells appeared in that retest.

## Question

Does `deep-module-design` change the design an agent produces for a shallow,
SQL-leaking module? The skill claims it should force a stated responsibility,
a full interface, a real seam, the depth tests, two or three alternative
designs, and a reversible migration.

## Fixture

`deep-module-design/fixtures/shallow-report` is a .NET 10 / C# repo:

- `ShallowReport.Data.ReportStore` is a thin SQL executor. `FetchAll(sql,
  params)` returns string-keyed dictionaries; `Execute`, `Columns`, and
  `TableName` expose writes, schema, and the table name.
- `ShallowReport.App` has three callers that each write SQL and consume column
  names: `ReportApi` (paginated list), `Summary` (totals by category and date
  range), and `Export` (CSV of the full table).
- `ShallowReport.Tests` seeds the database through the store and asserts the
  schema through `Columns("reports")`, a test that reaches past the interface.
- Constraints: the export must stream, the API must paginate, a Postgres read
  replica is planned, and behavior/output must not change.

The fixture builds and its tests pass:

```bash
dotnet run --project tests/ShallowReport.Tests
```

The fixture was later hardened for the retest: get-by-id, search, add, atomic
batch import, a SQL cache plus a page cache, and a `DebugRow` caller-to-caller
dependency. See **Retest v2** below.

## Method

- **Control:** the task only, with "do not load any skill; work from the
  repository alone."
- **Treatment:** the same task plus "load the `deep-module-design` skill with
  the skill tool and follow its process."
- Three repetitions per condition, same model, read-only proposal, 500-word cap.
- Verified: control loaded no skill 3/3; treatment loaded `deep-module-design`
  3/3.
- One reader scored all six proposals with the same rubric.

Task:

> Redesign the reporting data-access module so callers no longer know about SQL
> or the schema. Propose the new interface, where the seam goes, what each caller
> and test does after the change, and how to migrate without breaking behavior.
> Keep behavior and public output unchanged; do not add features.

## Results

Rubric, 0-10: responsibility and callers (1), interface completeness and no
leaks (2), seam and adapters (2), depth tests and test surface (2), alternatives
and design twice (2), migration and behavior preservation (1).

| Run | Resp. | Interface | Seam | Depth/test | Alternatives | Migration | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| control-1 | 1 | 1.5 | 2 | 1.5 | 0 | 1 | 7.0 |
| control-2 | 1 | 1.5 | 2 | 1.5 | 0 | 1 | 7.0 |
| control-3 | 1 | 1.5 | 2 | 1.5 | 0 | 1 | 7.0 |
| skill-1 | 1 | 2 | 2 | 1.5 | 2 | 1 | 9.5 |
| skill-2 | 1 | 2 | 2 | 1.0 | 2 | 1 | 9.0 |
| skill-3 | 1 | 2 | 2 | 1.5 | 2 | 1 | 9.5 |

Cost was mixed, not a clear penalty:

| Median | Control | Skill | Change |
|---|---:|---:|---:|
| Total tokens | 131,508 | 208,936 | +59% |
| Billable input+output | 16,983 | 16,168 | −5% |
| Tool calls | 15 | 16 | +7% |
| Read calls | 10 | 8 | −20% |
| Wall time | 70.5 s | 56.4 s | −20% |

The total-token difference is mostly cache reads; billable tokens are flat. With
three runs, cost is not the deciding signal.

## Findings

1. **Alternatives are the reliable delta.** All three skill runs compared
   two or three interfaces and stated why the others lost: a generic
   `Query(sql)` repository, a `ReportQuery` filter object, and separate
   `Columns()`/`ReadAll()` calls. No control run did this. This is the skill's
   `design twice` step, and it is the clearest behavioral effect.

2. **Invariants become explicit.** All three skill runs state start-inclusive /
   end-exclusive date bounds, ordering, null handling, streaming lifetime, and
   error propagation. The controls describe behavior but do not write a full
   interface contract.

3. **The selected design is mostly unchanged.** `control-3` proposes
   `IReportReader` with `List`, `TotalsByCategory`, and `OpenExport` returning
   columns plus lazy rows; `skill-3` proposes the same shape as `IReportStore`
   plus `ReportTable`. Both keep CSV formatting in the app, stream the export,
   and hide SQL. `control-2` and `skill-1` also converge on caller-shaped
   methods. The skill improves the argument for the design more than the design
   itself.

4. **One loophole: a test-only method on the production interface.**
   `skill-2` adds `Seed(IEnumerable<ReportRow> rows)` to `IReportStore` with the
   comment "test setup; schema stays internal." That makes a production API
   carry a test-only capability and weakens the "hard to misuse" rule. The
   controls seed through `InternalsVisibleTo` or a test builder. If the skill is
   revised, add one line: no production method may exist only for tests; seed
   through a test builder or `InternalsVisibleTo`.

5. **The deletion test remains a checklist no-op.** None of the six proposals
   explicitly applies it ("imagine deleting the module; if complexity vanishes,
   it was a pass-through"). Three skill runs say the module "only runs SQL" or
   is a pass-through, which reaches the same conclusion, but the named test did
   not appear. This matches the repo's earlier finding that checklist lines are
   weaker than recipes.

6. **The control is strong, not a baseline failure.** All three control
   proposals identify the SQL/schema leak, place the seam at the Data boundary,
   propose typed intent methods, remove the schema test, and give a staged
   migration. The skill's value is rigor, not rescue.

## Verdict

Keep `deep-module-design`. It reliably adds the alternatives comparison and the
interface contract, and those are the parts a capable control omits. It does not
produce a materially better selected design than a strong control, so do not
claim a design-quality win.

If revising, close the test-only-method loophole and consider a worked recipe
for the deletion test rather than another checklist line. Retest three runs on
this fixture after any behavior-shaping edit.

## Retest v2: harder fixture, counter applied

The counter was added to `skills/deep-module-design/SKILL.md` on 2026-11-05 and
synced:

> A production interface carries production capabilities only. Do not add a
> method that only tests call; seed through a test builder, an internal fixture,
> or `InternalsVisibleTo`.

The fixture now adds get-by-id, search, add, atomic batch import, a SQL cache
plus a page cache, and a `DebugRow` caller-to-caller dependency. All fixture
tests pass.

The `max` variant was used only to design the harder fixture, not to run the
trials. All six child sessions record the default variant.

Three control and three skill runs; control loaded no skill 3/3, treatment
loaded `deep-module-design` 3/3.

Rubric 0-12: responsibility/callers (1), interface completeness and no leaks
(2), seam and adapters (2), depth tests and test surface (2), alternatives (2),
transaction/error/cache semantics (2), migration (1).

| Run | Resp. | Interface | Seam | Depth/test | Alternatives | Tx/error/cache | Migration | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| control-1 | 0.5 | 2 | 2 | 1.5 | 0 | 2 | 1 | 9.0 |
| control-2 | 0.5 | 2 | 2 | 1.5 | 0 | 2 | 1 | 9.0 |
| control-3 | 0.5 | 1.5 | 2 | 1.5 | 0 | 2 | 1 | 8.5 |
| skill-1 | 1 | 2 | 2 | 2 | 2 | 2 | 1 | 12 |
| skill-2 | 1 | 2 | 2 | 2 | 2 | 2 | 1 | 12 |
| skill-3 | 1 | 2 | 2 | 2 | 2 | 2 | 1 | 12 |

Cost was higher for the skill:

| Median | Control | Skill | Change |
|---|---:|---:|---:|
| Total tokens | 168,157 | 337,675 | +101% |
| Billable input+output | 21,348 | 28,555 | +34% |
| Tool calls | 18 | 22 | +22% |
| Read calls | 10 | 11 | +10% |
| Wall time | 71.3 s | 95.1 s | +33% |

Findings:

1. **The skill won on contract and alternatives.** All three skill proposals
   state a one-sentence responsibility, ordering/pagination/streaming/
   transaction/cache invariants, and two or three rejected alternatives. No
   control proposal had an alternatives section, and all three left the
   responsibility implicit. `control-3` also used an app-level `ReportInput` in
   the Data interface, a dependency-direction smell.

2. **The chosen architecture converged.** All six propose an `IReportStore`
   with typed reads and writes, a SQLite adapter, and a caching decorator. The
   skill improves the contract and the rejected-option reasoning, not the
   module shape. This matches the baseline result.

3. **The test-only-method loophole did not recur.** 0/6 proposals added a
   `Seed`-style method to the production interface; the control also avoided
   it. The harder task and the counter changed together, so this does not
   isolate the counter. An isolated v1 counter retest is still open.

4. **The harder fixture exposed the two-cache problem.** All six consolidated
   the SQL cache and the page cache into one decorator or one invalidation
   point, which is a real improvement over the baseline fixture.

5. **Cost is the tradeoff.** The skill roughly doubles total tokens and adds a
   third of billable tokens and wall time. The gain is explicit reasoning, not
   a different architecture.

Provenance comparison: `codebase-design-vs-deep-module-design.md`. The original
core is cheaper and applies the deletion test more reliably; the synthesis's
unique win is inline alternatives.

## Deletion-test salience retest, 2026-11-05

The deletion test moved from step 4 to step 1 as a gate: the module is not named
until the deletion test is recorded. The duplicate bullet was removed from step
4; source and mirror are synced.

Three treatment runs, default variant, 3/3 loaded `deep-module-design`. All
three state the deletion test and its conclusion at the top, up from 1/3.

| Run | Score /12 | Note |
|---|---:|---|
| deletion-1 | 12 | clean |
| deletion-2 | 11.0 | App `ReportDto`/`ReportInput` and an `Invalidate()` cache-control method in the Data interface |
| deletion-3 | 11.5 | `ReadTable()` exposes columns and rows; a generic table reader |

The target behavior moved 1/3 to 3/3. The mean score moved 12.0 to 11.5; the
drop is two single-occurrence interface smells, not the deletion change. Watch
them: if either recurs, add a required check that every interface type is
defined in the module (not a caller DTO) and that cache invalidation stays
inside the decorator.

Cost medians: 157,495 tokens, 23,863 billable, 16 tools, 88.3 s. This is lower
than the pre-edit v2 skill median (337,675 / 28,555 / 22 / 95.1), but n=3 and
the deletion gate may have made the proposals more focused. Do not treat the
cost drop as established.

## Threats to validity

- Three runs per condition, one model, one reader, subjective rubric.
- The task names the seam and migration, which scaffolds both conditions. A
  vaguer brief might separate them more.
- The fixture is small and the leak is explicit; a subtler module might change
  the baseline.
- The control was told not to load a skill. In natural use the skill's
  description will likely fire for this task, so the realistic condition is
  closer to the treatment arm.
- Cost was measured once per proposal; the token total is cache-heavy and the
  sample is too small to rank conditions on cost.

## Reproduce

- Fixture: `analysis/evidence/deep-module-design/fixtures/shallow-report`
- Test: `dotnet run --project tests/ShallowReport.Tests`
- Proposals: `analysis/evidence/deep-module-design/runs/{control,skill}-{1,2,3}.md`
- Session IDs: `analysis/evidence/deep-module-design/runs/sessions.txt`
- Session store: `~/.local/share/opencode/opencode.db`, parent session
  `ses_e535c7922ffeHoIwa0qC2Ym6r4`; see `sessions.txt` for the six run IDs.

## Real-use report: encapsulating versus eliminating complexity (2026-11-12)

Issue #7 reported that the deletion test could justify a subsystem circularly:
without the module, the complexity goes elsewhere. The skill now asks first
whether the responsibility needs to exist — removal, a supported integration, or
an approved simpler contract — and only runs the deletion test on a
responsibility that survives. Alternative interfaces are compared on total
ownership cost, not only depth and locality.

This is a real-use report, not a scored run. No control or treatment was run
against the revised wording. See `docs/open-tasks.md`.

## Micro-test: encapsulating versus eliminating complexity (2026-11-12)

Fixture: `analysis/evidence/deep-module-design/fixtures/request-tracing`. The brief
says the team wants a code-owned `RequestTracing` module for one span per request.
The service has no tracing; `requirements.txt` pins
`opentelemetry-instrumentation-fastapi`, and the deployment owns the backend.

Method: fresh fixture copy per run, git baseline, no reads outside the project,
`opencode-go/deepseek-v4.1-flash` default variant. Three control runs had no
skill; three skill runs loaded `deep-module-design`. Score the primary
recommendation.

| Check | Control (n=3) | Skill (n=3) |
|---|---|---|
| Proposed a new module or custom middleware | 3/3 | 0/3 |
| Recommended direct `FastAPIInstrumentor` wiring | 0/3 | 3/3 |
| Asked whether the responsibility needs to exist before the interface | 0/3 | 3/3 |

The controls proposed a custom ASGI middleware (one run) or a thin wrapper module
(two runs). The skill runs said the module should not exist and recommended one
line at the composition root; two kept a thin fallback adapter only if a
code-owned entry point is mandatory, but not as the primary design. Session IDs:
`ses_e2e196402ffe3dvt9xka8DpN4D`, `ses_e2e17e7bcffeOwzCBiincBktFu`,
`ses_e2e14a037ffeHYHPRVZCqt37u3`, `ses_e2e11d759ffeFYOFzptXPiiOPj`,
`ses_e2e0eb3e1fferBy0KiSncOUN6N`, `ses_e2e0cd688ffew3B6gKgV6uiKY4`.

An earlier brief stated that architecture review had approved the module and a
branch held the skeleton. One skill run then complied with the custom middleware
("proceeding because the brief explicitly asks"), so that wording is not pooled
with this result. The softer team-preference brief is the recorded condition.

Limits: three runs per condition, one model and variant, one brief. The skill
answers still mention fallback adapters; the primary recommendation is what was
scored. The control was not fully failing on every wording, so this is a partial
micro-test, not a controlled 3x3.
