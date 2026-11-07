# code-review comparison: synthesized vs Matt vs addyosmani

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **exploratory**, four arms, three runs each. All twelve reports address
the nine seeded defects (keyword scan; four reports, one per arm, were read
end-to-end). The fixture is deliberately blatant, so this does **not** rank
review quality; it shows that addyosmani's extra security and performance skills
added explanation, not detection. Our skill remains the best workflow fit.

## Question

Is addyosmani's `code-review-and-quality`, especially with
`security-and-hardening` and `performance-optimization`, better than our
synthesized `code-review` and Matt Pocock's two-axis `code-review`? And does a
review skill need a coding-standards document to work?

## Fixture

`code-review-comparison/fixtures/user-search` builds a small Python repo with
`main` and `feature/user-search`. The feature adds a search handler and its
spec. The handler is intentionally bad:

- SQL injection: `q` is interpolated into an f-string.
- No `@require_auth`.
- No tenant filter; every tenant's rows are visible.
- `email` is selected and returned; the spec allows `id` and `display_name`.
- The caller's email and the raw query are written to the audit log.
- The query matches `email`, not `display_name`; empty `q` is not rejected.
- No `limit`, `cursor`, `next_cursor`, or ordering; the result set is unbounded.
- The canonical `Database.find_users` helper is bypassed.
- The single test asserts the leaking response and its fake ignores SQL and
  parameters, so the suite passes while every requirement fails.

`CODING_STANDARDS.md` states seven binding rules (auth, tenant scope, SQL, PII,
list endpoints, canonical helpers, response fields). The spec exists both as
`docs/specs/user-search.md` and as an OpenSpec change.

This is a detection fixture, not a discrimination fixture: all nine defects are
visible on a careful read.

## Method

Four arms, three runs each, same model, read-only review checkout, 1500-word
cap. Each run had its own copy and an isolation directory for probes.

| Arm | Skill source | Loaded how |
|---|---|---|
| `ours` | `skills/code-review` | `skill` tool |
| `matt` | `vendor/mattpocock-skills/.../code-review` | file-injected |
| `addy` | `vendor/addyosmani-agent-skills/.../code-review-and-quality` | file-injected |
| `addyplus` | the same review skill plus `security-and-hardening`, `performance-optimization`, and both checklists | file-injected |

The prompts supplied the fixed point, spec paths, standards paths, test command,
and isolation directory. Matt's skill requires two fresh-context axis
sub-agents; this harness exposed no sub-agent tool, so those runs used two
sequential passes in one context. That is a real limitation on the arm.

Reports: `code-review-comparison/runs/`.

## Results

Every run found all nine seeded defects.

| Check | ours | matt | addy | addyplus |
|---|---:|---:|---:|---:|
| Seeded defects found | 9/9 ×3 | 9/9 ×3 | 9/9 ×3 | 9/9 ×3 |
| Test suite run | 3/3 | 3/3 | 3/3 | 3/3 |
| Mutation probe | 3/3 | 3/3 | 3/3 | 3/3 |
| Spec axis separated | 3/3 | 3/3 | 0/3 | 0/3 |
| Standards axis separated | 3/3 | 3/3 | 0/3 | 0/3 |
| Overall verdict block | 3/3 | 0/3 | 0/3 | 0/3 |
| OWASP named | 0/3 | 0/3 | 0/3 | 2/3 |
| Leading-wildcard / index cost | 0/3 | 0/3 | 0/3 | 3/3 |
| OpenSpec delta omission | 0/3 | 1/3 | 0/3 | 0/3 |

The per-run counts are a keyword scan of all twelve reports, not a line-by-line
audit. One report per arm was read end-to-end to check that the keywords were
actual findings. No obvious fabricated defect appeared in the sampled reports;
false positives were not scored.

## Findings

1. **Addyosmani's extra skills did not add detection.** The plus arm found the
   same nine defects. It added depth: OWASP A01 in two of three runs, and the
   leading-wildcard/index cost in all three. Those are explanations of findings
   the review skill already surfaced, not new findings. The security skill's
   STRIDE step did not appear in any report, including the plus arm.

2. **Our skill has the best workflow fit.** It alone emitted per-axis verdicts
   and the `verdict: pass | needs_revision | blocked` block, recorded the
   command table, ran the mutation probe, and separated artifact findings (the
   unchecked OpenSpec tasks) from code findings.

3. **Matt's skill has the best spec-source discipline.** It alone noticed that
   the OpenSpec delta omits the authentication and ordering requirements stated
   in the prose spec. Its Standards/Spec reports stay separate and it does not
   pick an overall winner. It has no severity taxonomy and no verdict, which is
   a deliberate design choice, not an oversight.

4. **Addyosmani's skill has the best security/performance narrative.** Its
   reports read as a security review: exploit inputs, consequences, a
   Critical/Required split, and a fix order. It folds spec into correctness, so
   it does not report spec drift as a separate axis.

5. **Standards were the input that made the standards axis real.** All arms
   found the seven rule violations because `CODING_STANDARDS.md` stated them.
   Without that file, the smell baseline would have produced judgement calls,
   not hard breaches. The fixture supports the earlier conclusion: establish
   standards per target repo; do not bake them into the skill.

6. **The fixture is too easy to rank the skills.** Nine blatant defects on a
   98-line diff do not test subtle N+1s, missing indexes on realistic queries,
   authorization on nested resources, races, or false-positive control. The
   identical recall is expected, not evidence of parity on harder work.

## Verdict

Do not replace our `code-review`. Keep it as the stage skill.

Borrow two narrow things:

- From Matt: a spec-source cross-check. When the OpenSpec delta and the prose
  spec disagree, report the omission as an artifact finding. One run found it;
  the skill should require it.
- From addyosmani: a compact security/performance reference, not two full
  skills. Add pointers for injection/authz/PII and for unbounded work,
  leading-wildcard/index cost, and N+1. The plus-arm detail shows the useful
  content; the two build-time skills are more than a review needs.

Do not add `security-and-hardening` and `performance-optimization` as
supporting skills on this evidence. They did not change recall, and the repo
already records `production-readiness` as a separate, larger gap.

## Retest after the improvement

The skill then gained a required spec-source cross-check and a compact
security/performance reference. On the same fixture:

| Check | Seeded (3) | Clean (3) |
|---|---|---|
| Verdict | `needs_revision` 3/3 | `pass` 3/3 |
| Seeded defects reported | 9/9 ×3 | n/a |
| Delta/prose omission reported | 3/3 | 0/3 (none present) |
| Security or performance check named | 3/3 | 3/3 |
| False Critical/Required on clean | n/a | 0/3 |

The delta omission moved from 0/3 to 3/3. The clean fixture needed several
iterations because the skill found real test gaps (default limit, boundary,
PII fields); after those were fixed, the clean diff passed 3/3. The verdict block
appeared 5/6; one clean run used an "Overall" table despite the counter.

2026-11-07: the clean variant was re-run under the stricter gate in a neutral
root. It needed a request-id sanitization, a tenant-scope test that uses a
non-default tenant, and a missing-`q` test; the hardened clean fixture then
passed 3/3. See `code-review.md`.

## Next test

If a real ranking is needed, build a second fixture with subtle defects and a
clean variant:

- an N+1 inside a loop over results, not a missing `find_users` call;
- a missing index on a realistic query plan;
- an authorization gap on a nested resource, where a caller guard exists but is
  not reached;
- a race or lost update that the tests pass through;
- a clean diff to measure false positives.

Run the same four arms. The current fixture cannot separate them.

## Reproduce

- Fixture: `analysis/evidence/code-review-comparison/fixtures/user-search`
- Build: `./setup.sh /tmp/opencode/review-b seeded`
- Reports: `analysis/evidence/code-review-comparison/runs/`
