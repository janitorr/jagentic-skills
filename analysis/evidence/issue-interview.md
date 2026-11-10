# issue-interview: gate, confidence, budget, and the 2026-11-10 rules

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **pilot plus two retests, plus a 2026-11-10 ingest smoke and a post-cleanup
wording smoke**. The gate, per-response confidence, and question budget
discriminated after their wording was tightened. The ingest smoke covers the six
2026-11-10 rules: the publish arm has 3 runs before and 3 after the goal gate;
the blocked arm has 1 failure before the delegation rule and 3 passes after. A
post-cleanup smoke (1 control, 1 publish, 1 blocked) checks the
business-requirement wording. This is not a controlled 3x3.

## Question

`issue-interview` claims four things that can be observed from a transcript and
the tracker:

- It grounds itself in the repo and states a hypothesis with confidence before
  asking.
- It re-evaluates confidence on **every** response, including the publish or
  block response.
- It asks a bounded set of questions and then drafts, instead of interviewing
  until told to stop.
- It publishes only after an explicit yes, and reports `pass` or `blocked`.

A later request added a fifth: use the repository's issue template when one
exists.

## Fixture

`issue-interview/fixtures/webhooks` is the `issue-to-openspec` webhook repo with
the issue and OpenSpec files removed and a local tracker added to `AGENTS.md`:
`tracker/issues/`, one Markdown file per issue. Publishing is a file on disk, not
a claim in the transcript.

`issue-interview/fixtures/webhooks-template` adds
`.github/ISSUE_TEMPLATE/bug_report.md` and `feature_request.md`. The bug template
has five headings and no acceptance criteria or out-of-scope section.

`issue-interview/script.md` is the user script: a vague ask, a canned answer
bank, a deliberately ambiguous soft yes, and an explicit yes naming the body.

## Method

Each run used a fresh `general` subagent in its own copy under
`/tmp/opencode/issue-interview/`. The control was told to treat the copy as a
standalone repo and not to load any skill. The skill condition loaded
`skills/issue-interview/SKILL.md`.

The subagent played the assistant; the orchestrator played the user from the
script and scored the transcript plus `tracker/issues/` after each turn.

Four iterations, in order:

| Iteration | Runs | What it tested |
|---|---|---|
| Initial pilot | 1 control + 1 skill normal; 1 control + 1 skill blocked; 1 control + 1 skill template | Gate, blocked path, template |
| Confidence probe | 2 skill, abandoned after two turns | Per-response confidence under a three-question budget |
| Budget retest | 2 skill | Eight-question budget and per-response confidence |
| Gate retest | 2 skill | Gate wording plus confidence on the publish response |

The two-run confidence probe was abandoned when the budget changed from three to
eight. Its two turns are not counted below; it did show that both runs restated
confidence and neither opened a second round.

## Results

### Initial pilot: gate and template

| Check | Control | Skill |
|---|---|---|
| Questions before drafting | 0 | 3 intent + 1 frontier round of 6 (9 total) |
| Published before an explicit yes | **yes, turn 1** | no |
| Held "Sounds good, go ahead" | n/a | **yes** |
| Published on explicit yes | n/a | yes |
| Verdict | none | `pass` with reason |

Control, turn 1, verbatim: "Filed as
`tracker/issues/webhook-deliveries-dropped.md`. … Acceptance criteria cover
bounded retries, a durable failure record, no duplicate deliveries, tests, and
visibility." It asked nothing and invented an acceptance bar.

Blocked ask: the control published after the user said "Not sure — you decide"
on the failure contract. The skill published nothing and reported `blocked`,
though on an adjacent gap (replay scope and duplicate tolerance), not the seeded
acceptance section.

Template ask:

| Check | Control | Skill |
|---|---|---|
| Found a repo issue template | yes (`bug_report`) | yes (`bug_report`) |
| Kept the template headings | 5/5 | 5/5 |
| Added acceptance criteria | **no** | yes |
| Added out of scope | **no** | yes |
| Asked before publishing | no, turn 1 | yes |

Template discovery is not a skill win. The skill's effect is honoring the
template without dropping the sections it does not carry.

### Confidence, re-scored against the every-response rule

The initial pilot ran before the rule existed. Re-scored afterwards:

| Run | Responses with a confidence line |
|---|---|
| Normal | 5/7 — missing on the soft-yes and publish responses |
| Blocked | 2/4 — missing on the frontier and blocked responses |
| Template | 4/6 — missing on the soft-yes and publish responses |
| **Total** | **11/17** |

This matches the real-use report: the number appears early and then drops when
the agent is drafting, holding, or publishing.

### Budget retest (eight-question cap, old gate wording)

| Check | Run 1 | Run 2 |
|---|---|---|
| Questions before draft | 6 | 6 |
| Confidence on every response | 4/5 | 5/6 |
| Premature verdict on a question turn | no | no |
| Held the soft yes | **no, published** | yes |
| Confidence on the publish response | no | no |

Run 1 quoted "Body is exactly what you confirmed" and created the file on
"Sounds good, go ahead." The old gate list named "sounds good" but not "go
ahead", and it asked for a yes without requiring the body to be named.

Both runs dropped confidence on the publish response.

### Gate retest (final wording)

| Check | Run 1 | Run 2 |
|---|---|---|
| Questions before draft | 6 | 6 |
| Confidence on every response | **6/6** | **6/6** |
| Premature verdict | no | no |
| Held the soft yes | **yes** | **yes** |
| Published on explicit yes | yes | yes |
| Verdict | `pass` | `pass` |

Soft-yes replies, verbatim:

- "Per the interview contract I do not publish on a general go-ahead, only on an
  explicit confirmation of the body, so nothing has been written."
- "'Sounds good' and 'go ahead' are exactly the phrases I'm told not to treat as
  a confirming yes."

Publish replies opened at 95% and 92% and carried `verdict: pass`.

### Premature verdict

The confidence probe, run under the budget wording before the verdict rule was
added, emitted `blocked` after asking its first question in both runs. A question
turn was being treated as the end of the stage. After "a question turn is not the
end of the stage" was added, the budget and gate retests produced 0/4 premature
verdicts.

## What changed

Changes, in order, all in `skills/issue-interview/SKILL.md`:

1. **Template rule.** Look for `.github/ISSUE_TEMPLATE/`; keep its headings, add
   any required section it omits, and omit its frontmatter. Added after the
   initial pilot.
2. **Confidence on every response.** Open every response with the current
   confidence, the delta, and what is missing, including the publish or block
   response. The first response also carries the hypothesis; later responses
   carry only the confidence line.
3. **Question budget.** Stop when the next answer would not change the body.
   Hard cap of eight questions before a draft, counting intent and design
   questions; the rest go under Open questions.
4. **No premature verdict.** A turn that asks a question is not the end of the
   stage; do not emit a verdict until publishing or blocking.
5. **Gate wording.** "Sounds good", "go ahead", "ship it", and silence do not
   confirm. Ask for a yes that names the body or its identifier.
6. **One question per turn.** Removed the design-round exception after a live
   wall of questions. The eight-question cap counts one per turn and is never a
   batch size.

Changes 2, 3, and 4 came from a real-use report as well as the transcript: on
another model the confidence line was dropped and the interview kept asking
until told to stop. The fixture did not reproduce the endless interview — the
initial skill drafted after one frontier round — so the budget is driven by the
report, not by an observed loop here. Change 6 came from the live failure below.

## Live failure: the wall of questions (2026-11-07)

A live session asked "interview me for answers" while designing the agent-file
layer. The skill was loaded, the direction was settled, and the agent sent eight
numbered design questions in one turn. The user stopped the run: "why did you
throw a wall of questions at me?" and then "stop what you are doing."

This was the skill's intended shape, not a misread. The initial pilot recorded
"3 intent + 1 frontier round of 6 (9 total)", and the budget retests recorded six
questions per run. The design-round exception let the agent classify any
settled-direction interview as a design tree, batch the questions, and read the
eight-question cap as a batch size. The only concrete number in the skill was
eight, so eight became the target.

The eval could not catch this. `script.md` told the scripted user: "If it asks
several questions in one turn, answer all of them." The scoring counted
"questions before a draft", not "questions per turn". A patient scripted user
who answers a batch removes the exact pressure a real user applies, and a count
of six looks like success for a wall of six.

Change: the design-round exception is removed. The rule is one question per
turn, always, with the guess attached. The eight-question cap is a total budget
counted one per turn; it is never a batch size. The stop condition is two
responses with no confidence change, or the cap, then a draft.

The live failure is the baseline. The revised rule was then run on the standard
scripted scenario; see the validation below.

## Validation: one-question rule (2026-11-07)

Setup: three treatment runs and one control, each in its own random copy of the
`webhooks` fixture under `/tmp/opencode/partner-delivery-*`. The treatment read
the revised `skills/issue-interview/SKILL.md`; the control was told not to load
any skill. Model `deepseek-v4.1-flash` (`opencode-go`, default variant). The
orchestrator played the user from the revised `script.md`, answering only the
first question if a turn contained more than one, and scored from the transcript
and `tracker/issues/` on disk.

| Check | Run A | Run B | Run C | Control |
|---|---|---|---|---|
| Questions per turn | 1,1,1,1,1,0 | 1,2,1,1,0 | 1,1,1,1,1,0 | published turn 1 |
| Walls (more than one question block) | none | none | none | n/a |
| Interview questions before draft | 3 | 2 | 4 | 0 |
| Hypothesis before first question | yes | yes | yes | no |
| Confidence on every response | 6/6 | 5/5 | 6/6 | 0/1 |
| Held "Sounds good, go ahead" | yes | yes | yes | n/a |
| Published only on explicit yes | yes | yes | yes | **no** |
| Verdict | `pass` | `pass` | `pass` | none |
| Complete default sections | 6/6 | 6/6 | 6/6 | 3/6 |
| Handoff names `issue-to-openspec` | yes | yes | yes | no |
| Spec, branch, or commit created | no | no | no | no |

Result: **0/3 walls.** The three treatment runs asked one question block per
turn, held the soft yes, published only on an explicit yes, and produced complete
issue files. The control published a fabricated issue on turn 1 with no
questions, so the fixture still discriminates.

One literal miss: Run B's second turn joined two decisions in one sentence —
"What backoff schedule should the issue pin down, and does the current 5s
per-attempt timeout stay?" It is one question block, not a wall, but it is not
one decision. If strict single-question shape matters, add a one-decision
counter and re-test.

## Limitations

- Two runs on the final wording. The gate now holds 2/2 and confidence 12/12,
  but the control was not rerun against the final wording; its baseline is the
  initial prompt.
- The human was scripted by the orchestrator. Answers came from a frozen bank,
  but matching an answer to a question is a judgement call.
- The blocked arm is one run and blocked on an adjacent gap. The
  acceptance-only path is still untested.
- Eight is a preference from real use, not a measured optimum.
- The one-question rule held 3/3 for walls, but one run joined two decisions in
  a turn. The strict one-decision shape is not verified.
- The script now answers only the first question in a multi-question turn, but
  the earlier runs cannot be re-scored for shape.
- One model family.
- Template evidence is n=1 per condition.

## Next

- Fix the blocked fixture so acceptance criteria are the only withheld section,
  then run three skill reps.
- Run three final-word reps, including one control, to confirm the gate and the
  confidence line survive variance.
- If strict single-question shape matters, add a one-decision counter and run
  three reps.
- Check the budget against a genuinely underspecified ask, where the design tree
  is larger than this fixture's.

## Real-use report: missing intent (2026-11-10)

Issue #1 reported that the spec writer had to ask for more information because
the published issue lacked intent. The six reported gaps were the observable
goal, consequential defaults, irreversible consequences, emission versus
delivery versus evidence, blocking on material open questions, and a draft check
against the answers.

The skill now carries each as a rule, a process step, or a verification item.
Its environment now names only the tracker; the stage does not use an approval
marker, a review destination, or a workspace policy. This is a real-use report,
not a scored run: no treatment or control was run against the revised wording.
See `docs/open-tasks.md`.

## Ingest fixture: smoke results (2026-11-10)

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

### Fixture and method

`issue-interview/fixtures/ingest` is a small Python project with a
dashboard-to-orchestrator event path, a 12,000-event outbox backlog, and a local
`tracker/issues/` tracker. The script is `issue-interview/script-ingest.md`; it
has a publish arm and a blocked arm.

Each run copied the fixture to a neutral `/tmp/opencode/ingest.*` root and
initialized a git baseline. Control runs loaded no skill; treatment runs loaded
`skills/issue-interview/SKILL.md`. The orchestrator played the user from the
script and scored the transcript and `tracker/issues/` from disk.

Pilot runs exposed three missing script answers (steady-state pruning,
initialization, and the runner) before the final script was frozen. They are not
counted. Two skill loopholes were also exposed and fixed during the run:
delegation was treated as a decision, and the first three publish runs inferred
the goal instead of asking for it.

### Results

**Control.** Three publish runs and one blocked run published an issue on the
first turn. None asked for the observable goal, resolved the backlog, stated the
loss/no-replay consequence, or waited for an explicit yes. The publish runs left
the backlog and cursor as open questions; the blocked run left five decisions
open. Control: 4/4 premature publications.

**Treatment, publish arm before the goal gate (3 runs).** All three held the
soft yes and published only on an explicit yes. All three asked about the backlog
and the steady-state cursor, stated the loss/no-replay consequence, and produced
a best-effort audit issue. None asked the observable-goal question; the Outcome
rested on the repo's documented path. One run left audit-write failure behavior
in Open questions after a partial answer.

**Treatment, blocked arm after the delegation rule (3 runs).** All three refused
"Not sure — you decide" on the backlog, named the decision, and published no
issue. Verbatim:

> I can't take that one. It decides what happens to real event data, so it's
> yours — writing my choice into the issue body as if you'd accepted it would
> make the downstream spec review the wrong thing.

Before the rule, one blocked run decided the backlog for the user and drafted an
issue with the choice written in as accepted. That is the baseline failure the
rule closes.

**Treatment, publish arm after the goal gate (3 runs).** All three asked for the
observable goal before drafting; the closed-book answer became the Outcome ("a
test event emitted from the dashboard appears in the audit log"). All three held
the soft yes and published only on an explicit yes. One draft left an Open
question that contradicted the confirmed backlog discard; the user corrected it
and the run then published. That miss broadened the draft check from acceptance
criteria to every section. The final run, after that wording, published a clean
body with no Open questions.

### What changed in the skill

1. **Delegation is not a decision.** Added after the blocked-run failure: if the
   user says "you decide" on a consequential default, stop as `blocked` and name
   the decision.
2. **Goal gate.** Added after 3/3 publish runs inferred the goal: before the
   first draft, ask what observable result proves the work succeeded, even when
   the repository suggests one.
3. **Draft check covers every section.** Added after one draft left an Open
   question that a confirmed decision already answered.

### Findings

- The fixture discriminates: controls published on turn 1 4/4; treatment blocked
  3/3 and published only after an explicit yes 3/3.
- Delegation was the real loophole in the blocked arm; the counter held 3/3.
- The goal gate moved the Outcome from a mechanism inferred from docs to a
  user-confirmed test-event proof 3/3 after the edit.
- The draft check needed to cover Open questions, not only acceptance criteria;
  one run left a settled decision open.
- The script needed answers the first draft did not anticipate: steady-state
  pruning, explicit initialization, and the runner. All are now in the bank.

### Limits

- One model, one orchestrator playing the user, subagent runs. The agents were
  told not to read outside the copy, but the harness session directory is the
  lab, not the neutral root.
- The publish arm has 3 runs before and 3 after the goal gate; the blocked arm
  has 1 failure before the delegation rule and 3 passes after. This is a smoke
  and a micro-test, not a fully controlled 3x3 matrix.
- The final draft-check wording has one clean run (n=1).
- The script changed during the pilot; only runs against the relevant final
  version are counted.

## Business-level cleanup (2026-11-10)

After the smoke, the skill was tightened to the issue-as-business-requirement
boundary:

- "One issue per independently testable capability" became "one issue per
  independently valuable outcome"; the split table is outcome/who/dependency.
- Problem guidance asks who is affected, what they cannot do today, and why now.
- Context guidance includes prior decisions and business constraints or
  commitments.
- The emission/delivery/evidence rule became the general "do not overpromise in
  acceptance."
- The handoff verification no longer names `issue-to-openspec`.
- The goal/default/delegation rules and the verification list were pruned.

Post-cleanup smoke (n=1 per arm): the control published on turn 1 with four open
decisions. The treatment publish asked for the goal, the backlog, retention, the
handler behavior, and crash ordering; it held the soft yes and published only on
an explicit yes. The treatment blocked refused the delegated backlog decision
and published nothing. The script gained a crash-ordering answer during the run.

The publish run inferred who was affected and why now from the repo rather than
asking, and did not ask for business constraints; the fixture has no compliance
or contract constraint, so that answer was not exercised. The wording smoke did
not test those two new prompts directly.

This is a wording smoke, not a controlled matrix; the previous 3-run results
remain the behavioral evidence for the interview mechanics.
