# issue-interview: gate, confidence, and budget

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **pilot plus two retests**. The gate, per-response confidence, and the
question budget all discriminated after their wording was tightened. Two runs
per condition on the final wording; still not a ceiling.

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

Changes 2, 3, and 4 came from a real-use report as well as the transcript: on
another model the confidence line was dropped and the interview kept asking
until told to stop. The fixture did not reproduce the endless interview — the
initial skill drafted after one frontier round — so the budget is driven by the
report, not by an observed loop here.

## Limitations

- Two runs on the final wording. The gate now holds 2/2 and confidence 12/12,
  but the control was not rerun against the final wording; its baseline is the
  initial prompt.
- The human was scripted by the orchestrator. Answers came from a frozen bank,
  but matching an answer to a question is a judgement call.
- The blocked arm is one run and blocked on an adjacent gap. The
  acceptance-only path is still untested.
- Eight is a preference from real use, not a measured optimum.
- One model family.
- Template evidence is n=1 per condition.

## Next

- Fix the blocked fixture so acceptance criteria are the only withheld section,
  then run three skill reps.
- Run three final-word reps, including one control, to confirm the gate and the
  confidence line survive variance.
- Check the budget against a genuinely underspecified ask, where the design tree
  is larger than this fixture's.
