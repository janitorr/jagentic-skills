# code-review: clean and seeded diffs

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
