# Agent files: next session

Status: **not defined**. The five stage skills are environment-agnostic; they
expect a persona or agent file to supply the environment. This is the resume
point for defining those files.

## What is missing

`docs/workflow.md` names the boundary but no agent file exists in this repo:

| Layer | Owns |
|---|---|
| Skill | Stage process, completion criteria, findings, and the verdict |
| Persona / agent file | Role, task, tools, tracker and review operations, approval marker, workspace and push policy |
| Workflow | Stage order, loop limits, escalation, and human gates |

The stage skills end with `verdict: pass | needs_revision | blocked` and a
reason. They do not name labels, comments, commits, or pull requests.

## What to define

For each stage persona:

1. Role and task: what it is responsible for and what it must not do.
2. Tools: tracker read/create/amend, review destination, workspace access.
3. Approval marker: label, comment, file, or other. It must invalidate when the
   spec reopens.
4. Review destination: PR comment, issue comment, chat, or file.
5. Workspace and delivery policy: base branch, isolation, temp location, push
   and pull-request rules.
6. Model and variant: pin them so an eval is reproducible.

Then map each verdict to the environment action:

- `pass` advances, or asks for the human gate.
- `needs_revision` returns to the owning stage with the reason.
- `blocked` waits for the named human or upstream input.

## Order

1. Decide the topology: one orchestrator plus stage personas, or one persona per
   stage. Keep it minimal; the skills already own the process.
2. Write one persona end to end and test it before defining the next.
3. Record which persona produced which verdict in the evidence file when an eval
   uses it.

## Boundaries

- Do not put tracker commands, labels, or PR mechanics into a skill.
- Supporting skills are invoked directly and need no agent file.
- OpenSpec remains fixed; personas do not reimplement its commands.

## References

- `docs/workflow.md`: stage graph, verdict semantics, delivery mapping.
- `analysis/synthesis.md`: "Environment boundary".
- `AGENTS.md`: project instructions and skill ownership.
