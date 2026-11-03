# Evidence and evals

Status: **paused deliberately**. One skill has a behavioral baseline; the other
nine are unverified.

This note is the place to resume. Do not treat the absence of evidence as proof
that a skill works.

## What exists

| Skill | Evidence | Status |
|---|---|---|
| `spec-review` | `analysis/evidence/spec-review.md` plus fixtures | Pilot plus five repetitions per condition |
| All other skills | none | Unverified |

The `spec-review` fixtures are small OpenSpec projects:

- `fixtures/seeded`: six known defects, including a requirement with no
  scenario, missing auth scoping, an unverified index assumption, and
  layer-batched tasks.
- `fixtures/clean`: the same change with those defects resolved; strict
  validation passes.

## What we learned

- Five seeded runs with the skill and five without both found all six defects and
  returned **needs revision**. The fixture is too easy to discriminate.
- Five clean runs with the skill and five without both avoided blocking findings.
  The skill returned **ready for spec approval**; the control returned **ready for
  human review**.
- The full-report pilot showed the skill's real contribution: a falsification
  table, a verdict capped by an unverified load-bearing assumption, a
  stage-qualified verdict, and correct handling of an undefined approval marker.
- No recall advantage over a plain senior-engineer review has been demonstrated.

## Why we paused

- The fixture hit a ceiling, so more repetitions on it add cost without
  information.
- Twenty fresh-context runs produced no discriminating result.
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
Only `spec-review` has a partial record. The other nine are behavior-shaping
documents with no observed behavior behind them. That is accepted temporary debt,
not a completed verification.

Pending trigger test: `visual-explainer` added the user phrases "show me",
"visualize", "make it visual", "draw", "diagram", "sketch", "chart", and "map
this out". The description has not been tested for should-fire or should-not-fire
behavior.
