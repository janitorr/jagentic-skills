# code-review: routing and seeded-defect test

Status: **pilot**, three repetitions per condition. First behavioral record for
`code-review`. It checks the routing contract and whether the skill catches a
spec violation that the test suite misses.

## Question

`code-review` ends with `routing_status`, `owner`, and `requested_action`. Does
it emit them correctly for a clean diff and for a diff with a code defect? Does
it find a seeded defect that the suite passes?

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
| Emitted the routing block | 3/3 | 3/3 |
| Verdict | `ready` 3/3 | `needs_revision` 3/3 |
| Owner | `human` 3/3 | `developer` 3/3 |
| Action | `human sign-off` 3/3 | `post review comments and request changes` 3/3 |
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
test, and two confirmed it with a mutation probe. Findings were routed
`needs_revision / developer / post review comments and request changes`.

## Interpretation

- The two exercised branches map correctly: clean → `human` / sign-off, code
  defect → `developer` / request changes.
- The seeded defect discriminates: 3/3 clean passes, 3/3 seeded blocks, with no
  false blocking on the clean diff.
- The `spec-writer` branch was not exercised. Artifact issues appeared only as
  Optional findings; code defects dominated the verdict.

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

## Contract change

The `routing_status` / `owner` / `requested_action` contract used in this record
was retired on 2026-11-04. Skills now end with
`verdict: pass | needs_revision | blocked` and a one-line reason; delivery
belongs to the persona's agent file. Verdict, gate, and finding results in this
record stand; owner and action columns no longer describe the skill.
