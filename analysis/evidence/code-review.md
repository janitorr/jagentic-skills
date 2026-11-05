# code-review: clean and seeded diffs

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **partial**, three runs per condition. Verifies the verdict and whether
the skill catches a spec violation the test suite misses.

Current result: clean `pass` 3/3; seeded `needs_revision` 3/3; the seeded defect
and the test gap were found 3/3.

## Question

`code-review` ends with a `verdict` and a reason. Does it separate a clean diff
from one with a code defect? Does it find a seeded defect that the suite passes?

## Fixture

`code-review/fixtures/slugify/setup.sh` builds a small review repo from
`vertical-slice-tdd/fixtures/template`:

- `main` is the stub `slugify` baseline.
- `feature/add-slugify` implements `slugify` with tests green and tasks checked.
- With `SEED=1`, the whitespace collapse narrows from `\s+` to ` +`.

The seeded narrowing leaves tabs and newlines in the slug, violating the spec's
"whitespace runs" clause while all five tests still pass.

```bash
analysis/evidence/code-review/fixtures/slugify/setup.sh /tmp/opencode/cr-clean 0
analysis/evidence/code-review/fixtures/slugify/setup.sh /tmp/opencode/cr-seeded 1
```

## Method

Six fresh `general` subagents, three per condition, each in its own copy.
Treatment loaded `code-review`. Each reviewed `feature/add-slugify` against
`main`, was told the change name, and was given an isolation directory for the
mutation probe. Reviews were read-only; no tracked file could change.

## Results

| Check | Clean (3) | Seeded (3) |
|---|---|---|
| Emitted the verdict block (contract at the time) | 3/3 | 3/3 |
| Verdict | `pass` 3/3 | `needs_revision` 3/3 |
| Seeded whitespace defect found | n/a | **3/3** |
| Test-gap finding | n/a | **3/3** |
| Mutation probe run | 3/3 | 3/3 |
| Tracked files modified | 0/3 | 0/3 |

### Clean runs

All three returned **ready for merge sign-off** with only Optional findings:

- underscore is retained despite "remove punctuation";
- punctuation at an edge leaves a leading or trailing hyphen;
- `slugify` re-implements `trim` instead of calling it;
- one run also noted an Optional proposal classification issue.

None was promoted to Required, so the clean gate held.

### Seeded runs

All three found the ` +` regex and quoted inputs such as `slugify("A\tB")`
returning `"a\tb"`. All three also identified the missing non-space whitespace
test, and two confirmed it with a mutation probe. The verdict was
`needs_revision` with a code cause.

## Interpretation

- The two exercised branches map correctly: clean → `pass`, code defect →
  `needs_revision`.
- The seeded defect discriminates: 3/3 clean passes, 3/3 seeded blocks, with no
  false blocking on the clean diff.
- Only the code cause was needed. The `blocked` branch and artifact routing were
  not exercised; artifact issues appeared only as Optional findings.

## Limits

- Three repetitions, one model family, one small fixture.
- The seed is a one-character regex narrowing plus a tab/newline input; a
  reviewer who tries non-space whitespace finds it easily by design.
- The mutation probe depended on an isolation directory supplied by the prompt.
  Without one, the skill asks for it.
- Reviewers differ on Optional findings; only the Required gate was scored.

## Reproduce

```bash
analysis/evidence/code-review/fixtures/slugify/setup.sh /tmp/opencode/cr-seeded 1
cd /tmp/opencode/cr-seeded
# review feature/add-slugify against main
```

Prompt: load `code-review`, review `feature/add-slugify` against `main`, use the
isolation directory for the mutation probe, do not edit tracked files.

## Retest after the spec-source and quality-check edit, 2026-11-06

The skill gained three changes:

- a required spec-source cross-check (OpenSpec delta versus prose spec/issue);
- `references/quality-checks.md`, a compact security and performance checklist;
- consistent `pass` / `needs_revision` wording and an explicit instruction to
  emit the verdict block.

Fixture: `code-review-comparison/fixtures/user-search`. `main` has a profile
endpoint; `feature/user-search` adds a search endpoint with nine seeded defects,
a prose spec, an OpenSpec change, and binding `CODING_STANDARDS.md`. A `clean`
variant implements the same spec correctly with ten tests.

Method: three seeded and three clean runs, one model, read-only review checkout,
and an isolation copy for each mutation probe. The final six ran sequentially.

| Check | Seeded (3) | Clean (3) |
|---|---|---|
| Verdict | `needs_revision` 3/3 | `pass` 3/3 |
| Seeded defects reported | 9/9 ×3 | n/a |
| Delta/prose omission reported | 3/3 | 0/3 (none present) |
| Security or performance check named | 3/3 | 3/3 |
| Mutation probe killed | n/a (the seeded suite is blind) | 3/3 |
| False Critical/Required on clean | n/a | 0/3 |
| Exact verdict block | 3/3 | 2/3 |

The comparison baseline had ours at 0/3 for the delta omission; after the edit it
is 3/3. The clean fixture initially had real test gaps. The skill found them
(default limit, `limit` boundary, PII log fields), they were fixed, and the final
clean diff passes 3/3 with only Optional/Nit findings.

Limit: one model, one small fixture, three runs. The verdict block still missed
once on a clean run despite the counter; record it as a formatting variance, not
a finding-quality defect. This does not validate subtle performance or
authorization work.
