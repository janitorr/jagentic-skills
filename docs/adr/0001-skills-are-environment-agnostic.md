# ADR 0001: Skills stay environment-agnostic; agent files own delivery

- **Status:** accepted
- **Date:** 2026-11-10
- **Supersedes:** none

## Context

The synthesized pipeline is eleven skills: five stage skills
(`issue-interview`, `issue-to-openspec`, `spec-review`, `vertical-slice-tdd`,
`code-review`) and six supporting skills. The same skill files are meant to run
in different repositories, with different trackers, review destinations, and
workspace policies. OpenSpec is fixed as the artifact system.

An early version of the stage skills emitted `routing_status`, `owner`, and
`requested_action`. That put delivery policy inside the skill: two skills needed
an explicit "ready means workflow" rule to agree with `docs/workflow.md`, and the
rule could not be tested against a real persona. Skills also risked naming
labels, comments, commits, and pull requests directly, which ties the text to one
tracker and makes it wrong in every other environment.

The project needs a stable seam between "what must happen" and "how it happens
here".

## Decision

Split ownership across three layers, and keep the seam narrow:

| Layer | Owns |
|---|---|
| Skill | Stage process, completion criteria, findings, and a verdict: `pass`, `needs_revision`, or `blocked`, with a one-line reason |
| Persona / agent file | Role, task, tools, tracker and review operations, approval marker, workspace and push policy, pinned model and variant |
| Workflow (`docs/workflow.md`) | Stage order, loop limits, escalation, human gates |

Specifically:

- A stage skill ends with `verdict` plus `reason` and nothing else. That pair is
  the whole interaction contract.
- A stage skill never names a label, comment format, commit, pull request, or
  tracker CLI, and never invokes another stage skill. It may invoke OpenSpec and
  the named supporting skills.
- A skill that needs an environment operation that is not defined asks instead of
  assuming a command.
- Supporting skills are invoked directly by a human or an agent mid-task. They
  read the repository's instructions and fall back to this skill's defaults; no
  agent file is required.
- OpenSpec is fixed. Personas do not reimplement its commands and the artifact
  system is not abstracted behind an interface.

See `AGENTS.md` ("When adding or changing a synthesized skill"),
`docs/workflow.md` ("Boundary"), `docs/agent-files.md` ("Boundaries"), and
`analysis/synthesis.md` ("Environment boundary").

## Alternatives considered

**Keep `routing_status`, `owner`, and `requested_action` in every stage skill.**
Rejected: delivery policy would be duplicated per stage, and the "ready means
workflow" rule existed only to keep those fields consistent with
`docs/workflow.md`. It had no environment to be tested against.

**Move all routing to an external orchestrator and remove it from skills.**
Rejected: the persona already is the orchestrator. Removing routing entirely
leaves a skill unable to report "blocked because a required input is missing",
which is a stage finding, not a delivery decision.

**Let skills inline concrete tracker operations (`gh issue create`, label names,
PR review verbs).** Rejected: the text becomes environment-specific, cannot be
tested without that tracker, and is wrong in any repository that uses a different
one.

**Abstract the artifact system so OpenSpec is pluggable.** Rejected: there is one
implementation and no second one planned. An abstraction would add a contract
with no consumer and push OpenSpec's semantics into every skill.

## Consequences

Positive:

- The skills are portable across repositories and trackers without edits.
- There is one testable contract (`verdict` + `reason`) per stage.
- A skill can be evaluated without a live tracker or PR.
- Delivery mechanics can change without touching skill text.

Negative:

- The five stage skills cannot act on their own: an agent file must supply the
  environment. No agent file exists yet, so the pipeline is not runnable
  end-to-end (`docs/agent-files.md`, `docs/open-tasks.md`).
- Delivery policy can drift from the examples in `docs/workflow.md` until a real
  persona is written and tested.
- `pass | needs_revision | blocked` is a hard interface. Renaming or adding a
  verdict is a breaking change for every persona.
- The boundary lives in four documents (`AGENTS.md`, `docs/workflow.md`,
  `docs/agent-files.md`, `analysis/synthesis.md`), so it must be updated in all
  of them if it changes.

Follow-up work: choose the persona topology, write one stage persona end to end,
map each verdict to an environment action, and test it before defining the next
one. These are tracked in `docs/open-tasks.md` and `docs/agent-files.md`.
