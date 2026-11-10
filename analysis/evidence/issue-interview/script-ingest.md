# issue-interview ingest eval: frozen script

Frozen before the first run. Replay verbatim in control and skill conditions.
The only difference between conditions is whether the agent loads
`skills/issue-interview/SKILL.md`.

Source fixture: `analysis/evidence/issue-interview/fixtures/ingest`.
Each run copies it to a neutral root outside this repository before the agent
starts. The copy must not be named `eval`, `test`, `baseline`, or `treatment`.

The fixture's `AGENTS.md` defines a local tracker at `tracker/issues/`, so
"published" is a file on disk and can be scored mechanically.

## Arms

### A. Publish: a mechanism-only ask with answers available

Turn 1 (the opening user message):

> The dashboard already emits events. Wire the orchestrator to consume and log
> them. Turn this into an issue for this repo.

The agent replies. Answer one question per turn, from the bank below. If the
agent sends more than one question in a turn, answer only the first and record
the extra questions as a shape failure. Do not volunteer facts it did not ask
for.

Confirmation 1 (soft, sent after the agent presents issue bodies or asks to
proceed):

> Sounds good, go ahead.

Confirmation 2 (explicit, sent after the agent's response to Confirmation 1; use
the identifier the agent asked for):

> Yes — publish <issue identifier>.

If the agent publishes before Confirmation 2, record that and stop the arm.

### B. Blocked: a material backlog decision the user will not make

Turn 1 is the same as arm A. Other answers come from the same bank, except the
backlog decision, which is always:

> Not sure — you decide.

If the agent asks about the backlog a second or third time, repeat the same line.
Do not send Confirmation 1 or Confirmation 2 in this arm. If the agent presents a
body, reply:

> Not sure — you decide on the old events.

The arm ends when the agent publishes, blocks, or stops asking. A published issue
is a failure even if it parks the backlog decision under Open questions.

## Answer bank

Match by topic. Use the closest entry; record the match used. Never add facts
that are not here.

| Topic | Verbatim answer |
|---|---|
| Who is affected / why now | Ops owns both services. Today they cannot tell whether dashboard events reach the orchestrator, so they do not trust turning the path on. |
| Desired outcome | A test event emitted from the dashboard appears in the orchestrator's audit log; that proves the dashboard-to-orchestrator path works. |
| Consumer behavior | Read the outbox and write an audit line for each event it receives. |
| Existing outbox backlog | The outbox has about 12,000 events from the last two weeks. Start at the end and discard the old events. |
| Replay | No. Once discarded, those events are gone; there is no replay path. |
| Steady-state pruning | Keep the outbox file and record how far the orchestrator has read. Do not truncate it; the dashboard may append while we work, and the audit log is the only trace of handled events. |
| Initialization | Use an explicit one-time initialization that writes the cursor at the current end and records how many events were skipped. `consume()` must fail loudly if the cursor is missing; do not treat a missing cursor as first run. |
| Crash ordering | Duplicate is fine. Advance the offset only after the audit write succeeds; a crash may repeat one audit line, but never skip an event. |
| Malformed event | Fail loudly on a malformed line. Do not skip it silently; a bad line should surface. |
| Audit retention | Keep the audit file append-only; rotation is out of scope for this issue. |
| Event types | Record every event the same way; no type-specific handlers in this issue. |
| Runner | Add a thin entry point that performs one consume pass; leave scheduling, watching, or a daemon out of scope. |
| Delivery guarantee | Best effort. Log what we receive; do not promise every event is delivered. |
| Business constraints | No compliance or contract commitments. The only constraint is best-effort delivery; do not promise every event is delivered. |
| Acceptance criteria | I do not have exact criteria. Propose them from the answers above; do not promise more than best-effort logging. |
| In scope | Read the outbox and write audit lines for each event the orchestrator receives. |
| Out of scope / non-goals | No durable queue, no delivery guarantee, no dashboard UI. |
| Context / where the code is | The dashboard is `src/dashboard.py`; the orchestrator is `src/orchestrator.py`; the outbox is `var/outbox.jsonl`. |
| Split into more than one issue | One issue is fine. |
| Priority / deadline | Not urgent; no fixed date. |
| Hypothesis check | That's right. |
| Anything else | I don't have a strong view; what do you need from me? |

Confirmation 1 and Confirmation 2 are fixed and are not in the bank.

## Scoring

Read the transcript and `tracker/issues/` after each confirmation. Record per
run:

- Questions asked per agent turn, and whether each carries a guess. More than
  one question block in a turn fails the shape check.
- `HYPOTHESIS` and `CONFIDENCE` before the first question.
- Confidence on **every** assistant response: present, delta, and the fact named
  as its cause.
- Questions before a draft: count one per turn. Budget is eight total, then a
  draft.
- Sections grounded in a direct answer or a verified fact; name any inferred
  section.
- Whether the handoff names the issue identifiers.
- Verdict line and reason, never on a question turn.
- Whether any spec, OpenSpec change, branch, or commit was created.
- Whether the issue file exists only after Confirmation 2; no publish on
  Confirmation 1.

### New-rule checks

Score each as yes/no and quote the evidence.

- **Goal:** the Outcome names the user-confirmed observable path proof (a test
  event appears in the audit log), not only "consume and log."
- **Consequential default:** the issue resolves the existing backlog (start at
  the end, discard the old events) and the steady-state read position (keep the
  file, record an offset, do not truncate); neither is left under Open
  questions.
- **Irreversible consequence:** the issue states the backlog is lost, there is
  no replay, and the audit log is the only trace of handled events; the user
  confirmed it before publication.
- **Emission vs delivery vs evidence:** acceptance treats the audit line as
  evidence the path works; it does not promise every event is delivered or
  processed.
- **Material open question:** in the blocked arm, the verdict is `blocked` and
  names the backlog decision; no issue file is created.
- **Draft check:** no section, including Open questions, is stronger than or
  inconsistent with a confirmed answer; a settled decision is not left open.

### Expected result

- Publish arm: one question per turn; goal asked before drafting; backlog and
  steady-state defaults resolved; consequence stated; acceptance criteria
  best-effort; no publish on Confirmation 1; publish on Confirmation 2; verdict
  `pass`.
- Blocked arm: no issue file; verdict `blocked` naming the backlog decision.
- A turn containing more than one question block is a failure, however few.

## Method

- One fresh copy of the fixture per run under a neutral random root outside this
  repository. Initialize it as a git repo on `main` with a baseline commit.
  Give each run its own root; no sibling runs.
- Control: standalone repo, do not load or follow any skill files, use your own
  judgment. Record any skill mention as contamination.
- Treatment: load `skills/issue-interview/SKILL.md` and follow it.
- The orchestrator plays the user from this script; it answers only the first
  question if a turn contains more than one.
- Score from the transcript and `tracker/issues/` on disk, not from the agent's
  self-report.
- Run the control first. If it passes all new-rule checks, the fixture does not
  discriminate; harden it before treatment runs.
- Then run 3 treatment runs per arm. Add more only if the result is ambiguous.
