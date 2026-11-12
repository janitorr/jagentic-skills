# spec-review: recall, calibration, and verdicts

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **partial**. A pilot, a five-repetition run, and a later verdict test
with a clean-fixture repair. Review recall still shows a ceiling.

Current result: seeded `needs_revision` 3/3; clean `pass` 4/9 across repaired
cohorts. The old clean `5/5 ready` result is withdrawn: the clean fixture was not
clean.

## Question

Does `spec-review` find defects a strong control misses, avoid false blocking on
a clean change, and produce a usable verdict? The earlier pilots tested recall
and calibration; the later test exercised the verdict and repaired the clean
fixture.

## Fixtures

`spec-review/fixtures/seeded` and `spec-review/fixtures/clean` are small OpenSpec
projects with a `task-search` capability and an `add-task-search` change.

Seeded defects:

- D1: a requirement (`Search stays fast`) with no scenario, so strict validation
  fails.
- D2: the issue's authentication and per-user scoping criterion is absent from
  the artifacts.
- D3: a load-bearing design assumption ("the platform already added a GIN trigram
  index") is unverified and contradicted by a task that adds the index.
- D4: tasks are batched by layer, not vertical slices.
- D5: the delta duplicates an existing requirement while declaring the capability
  new.
- D6: the design's fuzzy matching contradicts the spec's "contains".

The clean fixture resolves all six and passes strict validation.

```bash
cd analysis/evidence/spec-review/fixtures/seeded
openspec validate add-task-search --strict
# exit 1: ADDED "Search stays fast" must include at least one scenario

cd ../clean
openspec validate add-task-search --strict
# Change 'add-task-search' is valid
```

## Method

Both conditions were fresh `general` subagents with no prior conversation.

- **Control:** "Use your own judgment only. Do not load, read, or follow any
  skill files."
- **Skill:** load `spec-review`, then review the same fixture.

Both were given the same files, commands, and the instruction not to edit.

The pilot used one run per condition. The five-repetition run used a compact
output contract scored against D1–D6. The verdict test used three runs per
fixture, treatment only, after the contract change; a no-skill control cannot
emit a skill-defined verdict.

## Results

### Seeded review

Pilot, full reports:

| Check | Control | Skill |
|---|---|---|
| Strict validation failure found | Yes | Yes |
| Missing auth / user-scoping found | Yes | Yes |
| Index assumption contradicted | Yes | Yes, in a falsification table |
| Horizontal tasks found | Yes | Yes |
| Duplicate requirement / capability found | Yes | Yes |
| Unverified assumption caps the verdict | Not explicitly | Yes |
| Severity mapping stated | Yes | Yes |
| Approval marker invented | No | No |

Five repetitions:

| Condition | D1 | D2 | D3 | D4 | D5 | D6 | Verdict | False blocking |
|---|---|---|---|---|---|---|---|---|
| Control (5) | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | needs revision 5/5 | 0 |
| Skill (5) | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | needs revision 5/5 | 0 |

**Recall has a ceiling.** The control found every seeded defect. The skill's
observable addition was a falsification table that made the unverified index
assumption load-bearing, explicit severity mapping, correct handling of an
undefined marker, and more edge-case coverage (empty term, case, fuzzy-vs-
substring, API contract, the existing query).

### Clean review

Pilot: the control reached "ready for human review" and the skill "ready for spec
approval"; neither invented a blocking finding. Five repetitions returned ready
5/5 in both conditions.

**Superseded.** The clean fixture was not clean; see the verdict section below.
These clean verdicts are historical.

### Verdict and fixture repair

The later test checked the verdict, not the retired owner fields. It ran three
fresh reviews per fixture, read-only, with the environment the skill expects
(local tracker, `issue.md`, stdout destination, no approval marker, `main`).

Seeded: `needs_revision` 3/3, all with artifact causes.

Clean, across nine self-contained runs after repairs:

| Verdict | Runs |
|---|---|
| `pass` | 4/9 |
| `needs_revision`, artifact cause | 4/9 |
| `needs_revision`, issue-scope cause | 1/9 |

The verdict block was emitted 9/9. The `pass` rate is not yet stable, but the
most common blocking findings were fixture defects, now fixed. One persistent
dissent is a judgment call: the API-only change defers the issue's user-visible
search box.

**The clean fixture was not clean.** It still carried D5: its delta added a
requirement identical to the baseline while the proposal declared the capability
new. Full reviews also found no app shell, no schema, no request contract, and a
627-character requirement that failed strict validation after archive. Repair
work:

- re-authored the change with `openspec new change` and `openspec instructions`;
- added an app shell that parses the query string and maps a thrown 401;
- added `schema/tasks.sql` and matched the row shape;
- added `followup-search-ui.md` so the deferred UI is tracked;
- split the oversized requirement into four;
- fixed the `user_id` / `userId` mismatch and the auth-before-term scoping;
- fixed the scoping clauses after the final cohort (not rerun).

The earlier `5/5 ready, 0 false blocking` claim is withdrawn. It was measured
against a fixture that still contained a seeded defect.

## Limits

- One model family; one reader scoring manually.
- The pilot used one run per condition; the five-repetition run used a compact
  output contract that may suppress findings outside the scored list.
- The verdict cohorts used different fixture revisions, so they are not one
  fixed treatment.
- Reviewers disagree on whether the deferred UI is blocking.

## Reproduce

Run a fresh agent in a copy of either fixture with the prompts under Method. For
the seeded fixture, strict validation must fail before the review; for the clean
fixture it must pass. Score D1–D6, false blocking, and the verdict. The seeded
defects are listed above and in the fixture's `issue.md`.

## Real-use report: necessity as well as feasibility (2026-11-12)

Issue #6 reported that design soundness emphasized missing behavior and failure
modes, not unnecessary machinery. The axis now asks whether the design is
proportionate to the observable outcome, the falsification step tests necessity
alongside feasibility, and a Required finding is allowed for custom
infrastructure with no demonstrated requirement or justified advantage over a
concrete simpler alternative. The risk list is capped by relevance: up to three
material risks, and none is valid. A claimed capability gap must be checked
against the installed version's documentation; default auto-instrumentation and
built-in endpoints count as supported integrations.

This is a real-use report, not a scored run. No control or treatment was run
against the revised wording. See `docs/open-tasks.md`.

## Micro-test: necessity as well as feasibility (2026-11-12)

Fixture: `analysis/evidence/spec-review/fixtures/otel-health`. The change
`add-request-tracing-and-health` is valid and proposes a custom ASGI middleware
in place of `FastAPIInstrumentor` and a custom `/health` route in place of
`fastapi-health`. The stated justification is an architecture approval; no
capability gap is recorded. Both integrations are pinned in `requirements.txt`.

Method: fresh fixture copy per run, git baseline, no reads outside the project,
`opencode-go/deepseek-v4.1-flash` default variant. Three control runs had the
`openspec-*` workflow skills only; three skill runs added `spec-review` and
`deep-module-design` and were told to use `spec-review`. Score the findings and
verdict from the response.

| Check | Control (n=3) | Skill (n=3) |
|---|---|---|
| Required or Critical finding on the custom machinery | 0/3 | 3/3 |
| Cited the pinned integration and the missing gap | 0/3 | 3/3 |
| Verdict `needs_revision` | 3/3 (other defects) | 3/3 |
| Accepted the approved custom direction | 3/3 | 0/3 |

Every control reviewed around the custom approach; two explicitly called it
"the approved direction". Every skill run raised a Required finding that the
custom middleware and route duplicate a pinned, supported integration with no
demonstrated gap, and capped the verdict at `needs_revision`. Session IDs:
`ses_e2e574881ffetDYnvCM9NC1CND`, `ses_e2e5557feffexk7NOI4ZwpxSpC`,
`ses_e2e5171a0ffemPqIilyjgRE3K2`, `ses_e2e4a466cffeD39pTPCZx9K6mA`,
`ses_e2e440cb5ffezJOVkHda7J9yqc`.

Limits: three runs per condition, one model and variant, one reader. The skill
prompt named the skill. Controls reached `needs_revision` on other defects, so
the verdict alone does not discriminate; the necessity finding does. The fixture
is one change shape.
