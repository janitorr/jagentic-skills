# Evidence and evals

Status: **opportunistic**. Targeted tests run when a skill or behavior warrants
it; there is no standing eval suite. Two skills have partial behavioral evidence;
eight are unverified.

This note is the place to resume. Do not treat the absence of evidence as proof
that a skill works.

## What exists

| Skill | Evidence | Status |
|---|---|---|
| `spec-review` | `analysis/evidence/spec-review.md` plus fixtures | Pilot plus five repetitions per condition; ceiling effect |
| `vertical-slice-tdd` | `analysis/evidence/vertical-slice-tdd.md` plus fixture | TDD ceiling; approval gate discriminates |
| All other skills | none | Unverified |

The `spec-review` fixtures are small OpenSpec projects:

- `fixtures/seeded`: six known defects, including a requirement with no
  scenario, missing auth scoping, an unverified index assumption, and
  layer-batched tasks.
- `fixtures/clean`: the same change with those defects resolved; strict
  validation passes.

The `vertical-slice-tdd` fixture is a small Python `unittest` repo with an
OpenSpec change, a documented test command, and an `APPROVED` marker. Test
outcomes are logged so test-first behavior can be scored from disk.

## What we learned

- Five seeded `spec-review` runs with the skill and five without both found all
  six defects and returned **needs revision**. The fixture is too easy to
  discriminate.
- Five clean `spec-review` runs with the skill and five without both avoided
  blocking findings. The skill returned **ready for spec approval**; the control
  returned **ready for human review**.
- Five `vertical-slice-tdd` runs with the skill and five without both wrote a
  failing test first, went green, checked tasks, and committed. TDD also hit a
  ceiling.
- In the approval-gate experiment, 2/5 control runs implemented without the
  required marker; 0/5 skill runs did. This is the first discriminating result:
  the skill raised gate compliance from 60% to 100% in this fixture.
- No TDD or review-recall advantage over a strong control has been demonstrated.

## Why we paused

- Both TDD and spec-review fixtures hit ceilings, so more repetitions on them add
  cost without information.
- Synthetic fixtures are only worth running when they can discriminate.
- Real usage is a better source of misses than a synthetic clean/seeded pair.

## When to resume

Resume when one of these happens:

- A real change exposes a miss, a false blocking finding, or a wrong verdict.
- A skill's behavior is contested.
- A skill is edited in a way that could change behavior, not just wording.
- A new skill is added and needs its first baseline.

## How to resume

1. **Harden the fixture first.** Add a defect a competent reviewer would plausibly
   miss: a requirement that subtly contradicts an existing spec, an acceptance
   criterion buried in an issue comment, or an assumption that looks confirmed
   but is not.
2. **Add a trigger test.** Use only the frontmatter plus six to ten
   should-fire / should-not-fire prompts, including adjacent skills.
3. **Run three to five fresh repetitions per condition.** Control: no skill.
   Treatment: load the skill. Use the same files, commands, and output contract.
4. **Score** defect recall, false blocking findings, verdict, next-stage handoff,
   and approval-marker handling. Read every match manually.
5. **Record** the result in `analysis/evidence/<skill>.md`. Include the control
   prompt, repetitions, verbatim failures, with-skill results, and trigger
   results.
6. **Do not batch.** One skill at a time, per `skill-forge`.

## Known debt

`skill-forge` requires baseline, micro-test, and trigger evidence for each skill.
Only `spec-review` and `vertical-slice-tdd` have partial records. The other eight
are behavior-shaping documents with no observed behavior behind them. That is
accepted temporary debt, not a completed verification.

Pending trigger test: `visual-explainer` added the user phrases "show me",
"visualize", "make it visual", "draw", "diagram", "sketch", "chart", and "map
this out". The description has not been tested for should-fire or should-not-fire
behavior.

Pending trigger test: `git-workflow` now names commit messages, commit and
changelog conventions, push, and pull requests explicitly. The description has
not been tested for should-fire or should-not-fire behavior.

Pending routing-contract test: the five stage skills now emit `routing_status`,
`owner`, and `requested_action`. `docs/workflow.md` defines the intended
transitions, but no workflow has been tested against those signals yet.
