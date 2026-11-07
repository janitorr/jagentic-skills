# code-review: clean and seeded diffs

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **partial**, three runs per condition; neutral-path re-run done. Verifies
the verdict and whether the skill catches a spec violation the test suite misses.

Current result: clean `pass` 3/3; seeded `needs_revision` 3/3; the seeded defect
and the test gap were found 3/3. The neutral-path clean fixture was hardened for
underscore and boundary hyphens, which the current gate treated as Required. The
user-search clean variant also passed 3/3 after request-id, tenant-scope, and
missing-`q` fixes.

The mutation evidence below is the fallback path. Step 5 now reads a CI mutation
report when one exists and does not re-run mutation testing by hand.

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
analysis/evidence/code-review/fixtures/slugify/setup.sh /tmp/opencode/review-a 0
analysis/evidence/code-review/fixtures/slugify/setup.sh /tmp/opencode/review-b 1
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
analysis/evidence/code-review/fixtures/slugify/setup.sh /tmp/opencode/review-b 1
cd /tmp/opencode/review-b
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

## Neutral-path re-run after the contamination audit, 2026-11-07

Status: **clean 3/3 `pass`, seeded 3/3 `needs_revision`**. The seeded defect and
the test gap were found 3/3. No tracked file changed and no run read outside its
project. The clean fixture was hardened during validation.

### Why

The contamination audit flagged `/tmp/opencode/cr-clean` and `cr-seeded`: the
path named the answer. This re-run uses a random root per review and a neutral
project directory (`.../slugify`); no path or prompt contains `clean`, `seeded`,
`eval`, or a condition name.

### Method

- Three clean and three seeded reviews, one fresh repo per run.
- `code-review/fixtures/slugify/setup.sh` builds the repo with neutral git
  metadata (`Dev <dev@example.com>`, `initial commit`, `feat: implement slugify`,
  `refactor: simplify regex`). The template's "eval runs" docstring was scrubbed.
- The project's `.opencode/skills` is copied in and global skills are removed.
  The prompt loads `code-review`, reviews `feature/add-slugify` against `main`,
  uses a probe directory outside the project, and forbids tracked edits.
- Model `deepseek-v4.1-flash` (`opencode-go`, default variant), 600s cap. A
  first 300s cap killed a valid review mid-report; the cap was raised.
- Score from the reply and `git status`, not self-report. One run per branch
  validated the fixture; the remaining runs were added only after the clean
  branch passed.

### Fixture hardening

The first clean validation did not pass. It returned `needs_revision` twice:

1. `_` was retained even though the spec says "removes punctuation";
2. `Hello !` became `hello-`, leaving a boundary hyphen.

Both are real spec violations under the current spec cross-check, not false
blocking findings. The clean implementation now removes `_` and strips boundary
hyphens; tests cover both. The clean and seeded suites pass 7/7, and the seeded
` +` narrowing still leaves tabs and newlines uncovered. The original clean
result treated underscore and the boundary hyphen as Optional; the hardened
fixture matches the stricter gate.

### Results

| Check | Clean (3) | Seeded (3) |
|---|---|---|
| Verdict | `pass` 3/3 | `needs_revision` 3/3 |
| Seeded whitespace defect found | n/a | 3/3 |
| Test gap named | n/a | 3/3 |
| Tracked files modified | 0/3 | 0/3 |
| Read outside the project | 0/3 | 0/3 |

The clean findings were Optional or FYI (`trim` duplication, a stale proposal
label, an untested non-space whitespace case); none was promoted to Required.

### Mutation probe

| Check | Clean (3) | Seeded (3) |
|---|---|---|
| Probe run in an isolated copy | 3/3 | 3/3 |
| Covered mutation killed | 3/3 | 3/3 (seed-4) |
| Seeded blind spot shown by the probe | n/a | 2/3 (seed-2 exact regression, seed-3 mutation) |

All six replies describe an isolated copy and a mutation. Clean-3/4/5 changed
`\s+` to `\s` (or ` +` to `  +`); the focused test failed as expected. Seed-2
reapplied the exact `\s+` to ` +` regression on the pre-change commit and all six
tests passed, showing the blind spot. Seed-3's probe also survived. Seed-4
mutated the seeded ` +` to a space; the test failed, so it caught a different
mutation but still named the test gap.

This eval predates the step-5 change: it hand-ran the probe as the fallback. With
a CI mutation report, step 5 now reads the report and does not re-run it.

### Limits

- Three runs, one model, one small fixture.
- The clean fixture changed during validation; the 3/3 pass is against the
  hardened fixture, not the original.
- The seeded defect is a one-character regex narrowing and is easy to find by
  design.
- The user-search clean fixture was re-run separately; see below.

## User-search clean re-run, 2026-11-07

Status: **clean 3/3 `pass`** after fixture hardening. The clean variant had not
been re-run under the stricter gate; the earlier clean 3/3 predates the
request-id, tenant-scope, and missing-`q` fixes below.

### Method

- The comparison fixture's clean variant: `main` has the profile endpoint,
  `feature/user-search` adds the search endpoint, and the `clean` overlay
  replaces `app/users.py` and `tests/test_users.py`.
- One random root per review (`.../user-search`); no `clean`, `seeded`, `eval`,
  or condition name in a path or prompt. Git metadata is `Dev
  <dev@example.com>` with `feat: user profile endpoint` and `feat: add user
  search endpoint`; `AGENTS.md` says "User service", not "Fixture repository".
- Project `.opencode/skills` is copied in; global skills are removed. The prompt
  loads `code-review`, reviews `feature/user-search` against `main`, uses a probe
  directory outside the project, and forbids tracked edits.
- Model `deepseek-v4.1-flash` (`opencode-go`, default variant), 900s cap. A 600s
  cap killed one valid run mid-probe; 900s was enough.
- One run validated the fixture; the remaining two were added after it passed.

### Fixture hardening

The first two clean validations found three real gaps:

1. **Log injection.** `request_id` was logged with CR/LF unsanitized, and the
   test placed the injection in `args` instead of on the request. Sanitizing
   CR/LF and testing the request field fixed it.
2. **Tenant-scoping test.** The test used the default tenant, so a hardcoded
   tenant regression would pass. The test now uses `tenant-b` and asserts the
   `FakeDB` call arguments.
3. **Missing `q` branch.** Whitespace-only `q` was tested; a missing `q` was not.
   A `test_missing_query_is_rejected` covers it.

The clean suite is 13 tests and passes. The 3/3 clean pass above was against the
12-test version, before the `get_user` not-found test was added. The seeded
comparison fixture is unchanged.

### Results

| Check | Clean (3) |
|---|---|
| Verdict | `pass` 3/3 |
| False Critical/Required on clean | 0/3 |
| Probe run | 3/3; no surviving Required mutation |
| Tracked files modified | 0/3 |
| Read outside the project | 0/3 |

The clean findings were Optional: a DB seam contract/test gap, unbounded `q` or
`cursor`, query-plan verification, and a minimum-limit documentation gap. None
was promoted to Required.

### Limits

- Three runs, one model, one fixture.
- The clean fixture changed during validation; the 3/3 pass is against the
  hardened fixture.
- The probe results are read from the replies and tool calls, not separately
  scored for this fixture.
- The seeded comparison fixture was not re-run; the 2026-11-06 seeded 3/3
  remains.

### CI mutation report micro-test

One review of the user-search clean fixture with a synthetic report at
`reports/mutation/mutation.json`; the report named a surviving `get_user`
404-branch mutant.

| Check | Result |
|---|---|
| Report read | yes |
| Survivor cited | yes |
| Verdict | `needs_revision` |
| Hand mutation probe | none |
| Tracked changes | none |
| Outside reads | none |

The review returned `needs_revision` for the missing not-found test, cited the
report's surviving mutant, and did not run a hand probe. n=1, one model,
synthetic report, one fixture. The report's survivor was a real gap: a
`test_returns_not_found` was added, taking the clean suite to 13 tests. The 3/3
clean pass above was against the 12-test version; the test-only addition does
not change the code.
