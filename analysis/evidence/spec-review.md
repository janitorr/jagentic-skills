# Evidence: spec-review

Pilot plus a five-repetition run. This is still a partial record, not a
certification. The pilot used one repetition per condition; the five-repetition
run is recorded below.

## Fixtures

`spec-review/fixtures/seeded` and `spec-review/fixtures/clean` are small OpenSpec
projects with a `task-search` capability and an `add-task-search` change.

Seeded defects:

- A requirement (`Search stays fast`) with no scenario, so strict validation
  fails.
- The issue's authentication and per-user scoping acceptance criterion is absent
  from the change artifacts.
- A load-bearing design assumption ("the platform already added a GIN trigram
  index") is unverified and contradicted by a task that adds the index.
- Tasks are batched by layer, not vertical slices.
- The delta duplicates an existing capability requirement while declaring the
  capability new.

The clean fixture resolves all six and passes strict validation.

```bash
cd analysis/evidence/spec-review/fixtures/seeded
openspec validate add-task-search --strict
# exit 1: ADDED "Search stays fast" must include at least one scenario

cd ../clean
openspec validate add-task-search --strict
# Change 'add-task-search' is valid
```

## Conditions

Both conditions were fresh `general` subagents with no prior conversation.

- **Control:** "Use your own judgment only. Do not load, read, or follow any
  skill files."
- **Skill:** load `spec-review` via the skill tool, or read
  `.opencode/skills/spec-review/SKILL.md` if the tool is unavailable, then review
  the same fixture.

Both were given the same files, the same commands, and the same instruction not
to edit.

## Results

| Check | Control / seeded | Skill / seeded |
|---|---|---|
| Strict validation failure found | Yes | Yes |
| Missing auth / user-scoping found | Yes | Yes |
| Index assumption contradicted | Yes | Yes, in a falsification table |
| Horizontal tasks found | Yes | Yes |
| Duplicate requirement / capability found | Yes | Yes |
| Unverified assumption caps the verdict | Not explicitly | Yes: load-bearing assumption unverified |
| Severity mapping stated | Yes | Yes |
| Verdict | needs revision | needs revision |
| Next stage named | No | Yes: `vertical-slice-tdd` |
| Approval marker handled | No | Yes: notes none is defined, does not invent one |

| Check | Control / clean | Skill / clean |
|---|---|---|
| Blocking findings invented | No | No |
| Findings | 1 Optional, 1 FYI | 4 Optional, 1 FYI |
| Verdict | ready for human review | ready for spec approval |
| Next stage named | No | Yes: `vertical-slice-tdd` |
| Approval marker handled | No | Yes: notes none is defined |

## Five-repetition run

Five fresh runs per condition, scored against seeded defect IDs D1–D6 and a
clean-fixture false-positive check. The earlier pilot used full reports; this run
used a compact output contract to make scoring consistent.

Seeded defects:

- D1: requirement with no scenario / strict validation failure
- D2: missing auth or user-scoping requirement
- D3: unverified index assumption
- D4: horizontal layer-batched tasks
- D5: duplicate requirement or wrong capability classification
- D6: fuzzy-vs-contains semantics contradiction

| Condition | D1 | D2 | D3 | D4 | D5 | D6 | Verdict | False blocking |
|---|---|---|---|---|---|---|---|---|
| Control (5 runs) | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | needs revision 5/5 | 0 |
| Skill (5 runs) | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | needs revision 5/5 | 0 |

| Condition | Clean verdict | False blocking | Next stage named |
|---|---|---|---|
| Control (5 runs) | ready for human review 5/5 | 0 | 5/5 |
| Skill (5 runs) | ready for spec approval 5/5 | 0 | 5/5 |

One skill run returned `APPROVAL_MARKER: missing` on the clean fixture while the
other four returned `not-applicable`. The fixture defines no marker, so the
correct behavior is to ask; the variance is in how that is reported, not in
whether a marker was invented. No run invented a label or comment.

## Interpretation


The pilot does not show that the skill finds defects the control misses. The
control found the core seeded defects, and in the five-repetition run both
conditions found all six defects and reached the same verdict. The fixture is too
easy to discriminate on recall alone.

What the skill added, observed in the full-report pilot:

- A falsification table that made the unverified index assumption load-bearing
  and forced the verdict cap.
- Explicit severity mapping and a stage-qualified verdict.
- Correct handling of an undefined approval marker, with no invented label.
- More edge-case coverage on the seeded fixture: empty term, case sensitivity,
  fuzzy-vs-substring semantics, API contract, and the existing query.

What the five-repetition run did not show:

- Any recall advantage over a plain senior-engineer review.
- Any false-positive advantage on the clean fixture; both conditions were clean.
- Reliable discrimination, because both conditions hit the ceiling.

What needs a harder fixture or more reps:

- A defect a competent reviewer would plausibly miss without the skill, such as a
  requirement that contradicts an existing spec subtly, or an acceptance
  criterion hidden in an issue comment.
- Trigger behavior: whether the description fires on a review request and stays
  quiet on adjacent tasks.
- Five repetitions on the harder fixture, with every match read manually.

## Follow-up

1. Add a subtler seeded defect and a second clean variant.
2. Run five repetitions on the harder fixture, for control and skill.
3. Add a trigger test with should-fire and should-not-fire prompts.
4. Only then treat `spec-review` as verified.

## Routing-contract test

The interaction contract had never been exercised. This run checks whether
`spec-review` emits `routing_status`, `owner`, and `requested_action`, uses legal
values, and maps the owner to the blocking pass.

### Method

Treatment only: the fields are skill-defined, so a no-skill control cannot emit
them. Three fresh `general` subagents on the seeded fixture and three on the
clean fixture per cohort, read-only, each in its own copy with a git baseline.
The prompt supplied the environment the skill expects (local-file tracker,
`issue.md`, stdout review destination, no approval marker, `main`, no push).

### Results

Seeded, final cohort:

| Check | Result |
|---|---|
| Emitted all three fields | 3/3 |
| Legal enum values | 3/3 |
| Verdict | `needs_revision` 3/3 |
| Owner | `spec-writer` 3/3 |
| Action | `post findings as review comments and request changes` 3/3 |

Clean fixture, final cohort (c25–c27):

| Check | Result |
|---|---|
| Emitted all three fields | 3/3 |
| Verdict | `ready` 1/3, `needs_revision` 2/3 |
| Owner when ready | `human` 1/3 |
| Owner when blocking | `issue-author` 1/3, `spec-writer` 1/3 |

Across the self-contained clean cohorts (c19–c27, nine runs):
`ready` / `human` 4/9, `needs_revision` / `spec-writer` 4/9,
`needs_revision` / `issue-author` 1/9. The contract was emitted 9/9.

### The clean fixture was not clean

Earlier sections record clean runs returning `ready 5/5` with `0 false
blocking`. That result is not reproducible with an unconstrained full review.
The clean fixture still contained seeded defect D5: its delta added a requirement
identical to the baseline's while the proposal declared the capability new. Full
reviews also found that the fixture had no app shell, no schema, no request
contract, and a 627-character requirement that failed strict validation after
archive.

Repair work, in order:

- re-authored the change with `openspec new change` and `openspec instructions`;
- added an app shell that parses the query string and maps a thrown 401;
- added `schema/tasks.sql` and made the row shape match the code;
- added `followup-search-ui.md` so the deferred UI is tracked;
- split the oversized requirement into four requirements;
- fixed the `user_id` / `userId` mismatch and the auth-before-term scoping;
- fixed the scoping clauses after the final cohort (not rerun).

The earlier clean result should be treated as superseded. The clean arm's
ceiling claim in this record is withdrawn until it is re-baselined.

### Interpretation

- Emission and enum use are reliable: 12/12 across the two fixtures.
- Owner mapping behaved correctly in every branch observed: `spec-writer` for
  artifact defects, `human` for ready, `issue-author` when the issue scope was
  the blocker.
- The remaining disagreement is a judgment about API-only delivery versus the
  issue's user-visible outcome, not a contract failure.
- `ready` is not yet stable on the clean fixture (4/9), but the most common
  blocking findings were fixture defects that are now fixed.

### Limits

- Treatment only; no control.
- One model family, three reps per cohort.
- Cohorts used different fixture revisions, so this is not one fixed treatment.
- Reviewers disagree on whether the untracked UI follow-up is blocking.

## Next: routing elsewhere

`spec-review` is the second stage with a routing record, after
`issue-to-openspec`. The other stage skills and the multi-stage loop in
`docs/workflow.md` are still untested.

## Contract change

The `routing_status` / `owner` / `requested_action` contract used in this record
was retired on 2026-11-04. Skills now end with
`verdict: pass | needs_revision | blocked` and a one-line reason; delivery
belongs to the persona's agent file. Verdict, gate, and finding results in this
record stand; owner and action columns no longer describe the skill.
