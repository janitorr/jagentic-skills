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
