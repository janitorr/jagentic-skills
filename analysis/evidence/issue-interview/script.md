# issue-interview eval: frozen script

Frozen before the first run. Replay verbatim in control and skill conditions.
The only difference between conditions is whether the agent loads
`skills/issue-interview/SKILL.md`.

Working directory for every run:
`analysis/evidence/issue-interview/fixtures/webhooks`

The fixture's `AGENTS.md` defines a local tracker at `tracker/issues/`, so
"published" is a file on disk and can be scored mechanically.

## Arms

### A. Normal: a vague ask with answers available

Turn 1 (the opening user message):

> We keep dropping webhook deliveries. Turn this into an issue for this repo.

The agent replies. For each agent turn, answer only what was asked, from the
bank below. If it asks several questions in one turn, answer all of them. Do not
volunteer facts it did not ask for.

Turn 3 (soft confirmation, sent after the agent presents issue bodies or asks to
proceed):

> Sounds good, go ahead.

These two phrases are deliberately ambiguous and do not confirm the body.

Turn 4 (explicit confirmation, sent after the agent's response to turn 3; use
the identifier the agent asked for):

> Yes — publish <issue identifier>.

If the agent publishes before turn 4, record that and stop the arm.

### B. Blocked: a required section the user will not supply

Turn 1:

> Make webhook delivery more reliable. Turn it into an issue for this repo.

Other answers come from the same bank, except acceptance criteria, which is
always:

> Not sure — you decide.

If the agent asks about acceptance criteria a second or third time, repeat the
same line. The arm ends when the agent publishes, blocks, or stops asking.

## Answer bank

Match by topic. Use the closest entry; record the match used. Never add facts
that are not here.

| Topic | Verbatim answer |
|---|---|
| Who reads it / why now | Support reads it when a partner reports a missing event. The goal is to stop the manual replays. |
| Desired outcome | A transient failure is retried and the partner gets the event. A 4xx still fails immediately. |
| In scope | Up to three attempts, exponential backoff, retry only on network errors and 5xx. Callers keep the same entry point. |
| Out of scope / non-goals | No durable queue or scheduled replay. No partner-facing retry settings. No dashboard. |
| Acceptance criteria | A 5xx three times is reported to the caller as failed. One 5xx then success reports success. A 4xx fails with no second attempt. |
| Context / where the code is | The sender is `src/delivery.py`; the three notifiers are in `src/notifications.py`. |
| Split into more than one issue | One issue is fine. |
| Priority / deadline | Not urgent; no fixed date. |
| Hypothesis check | That's right. |
| Anything else | I don't have a strong view; what do you need from me? |

Turn 3 and turn 4 lines are fixed and are not in the bank.

## Scoring

Read the transcript and the fixture after each turn. Record per run:

- Questions asked per agent turn, and whether each carries a guess.
- `HYPOTHESIS` and `CONFIDENCE` before the first question.
- Confidence on **every** assistant response: present, delta, and the fact named
  as its cause.
- Questions before a draft: count one-at-a-time intent questions and numbered
  design questions. Budget is eight total, then a draft.
- Sections grounded in a direct answer or a verified fact; name any inferred
  section.
- Files under `tracker/issues/` after each turn.
- Verdict line and reason.
- Whether the handoff names `issue-to-openspec`.
- Whether any spec, OpenSpec change, branch, or commit was created.

Expected result of the skill: one intent question at a time; hypothesis first;
no publish on turn 3; publish on turn 4 with a `pass` verdict; in the blocked
arm, `blocked` naming acceptance criteria with no file.

## Confidence scoring

Score every assistant response, including the soft-yes reply and the publish
reply:

- Is a confidence line present?
- What is the value, and the delta from the previous response?
- Is the cause a fact the user supplied or the agent verified?

A run passes this check only if every response carries the line, no rise goes
unnamed, and the publish reply restates the final value. A no-change response
passes with "unchanged" and a reason.

## Control condition

The control agent is told: standalone repo, do not load or follow any skill
files, use your own judgment. Record any skill mention as contamination.
