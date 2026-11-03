# Evidence: spec-review

Pilot baseline, one repetition per condition. This is not the five-repetition
evidence `skill-forge` asks for, and it does not certify the skill. It checks
whether the current text behaves plausibly before investing in a full eval.

## Fixtures

`fixtures/seeded` and `fixtures/clean` are small OpenSpec projects with a
`task-search` capability and an `add-task-search` change.

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

The clean fixture resolves all five and passes strict validation.

```bash
cd fixtures/seeded && openspec validate add-task-search --strict
# exit 1: ADDED "Search stays fast" must include at least one scenario
cd fixtures/clean && openspec validate add-task-search --strict
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

## Interpretation

The pilot does not show that the skill finds defects the control misses. The
control found the core seeded defects, which means the fixture is too easy to
discriminate on recall alone.

What the skill added:

- A falsification table that made the unverified index assumption load-bearing
  and forced the verdict cap.
- Explicit severity mapping and a stage-qualified verdict.
- A named next stage and correct handling of an undefined approval marker.
- More edge-case coverage on the seeded fixture: empty term, case sensitivity,
  fuzzy-vs-substring semantics, API contract, and the existing query.

What needs a harder fixture or more reps:

- A defect a competent reviewer would plausibly miss without the skill, such as a
  requirement that contradicts an existing spec subtly, or an acceptance
  criterion hidden in an issue comment.
- Trigger behavior: whether the description fires on a review request and stays
  quiet on adjacent tasks.
- Five repetitions and a no-guidance control per `skill-forge`, with every match
  read manually.

## Follow-up

1. Add a subtler seeded defect and a second clean variant.
2. Run five repetitions of seeded and clean for control and skill.
3. Add a trigger test with should-fire and should-not-fire prompts.
4. Only then treat `spec-review` as verified.
