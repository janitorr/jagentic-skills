---
name: spec-review
description: Use before implementing or archiving an OpenSpec change; when the user asks to review, validate, or find gaps in a proposal, spec deltas, design, or tasks; when strict validation fails; or when asking whether a change is ready for implementation.
---

# Spec Review

## Environment

The agent file defines the tracker, approval marker, review destination, and
workspace policy. Read it before starting. If an operation you need is not
defined, ask; do not assume a specific CLI or service.

## Overview

Review an OpenSpec change before code exists. A confident artifact is not a
correct one.

**Stance:** read-only, adversarial, evidence-first. Your job is to falsify the
artifacts, not to approve them. A clean review is a valid result; an invented
finding is not.

## Interaction contract

End with a verdict the persona can act on:

```
verdict: pass | needs_revision | blocked
reason: <one line naming the defect and the stage that owns it>
```

`pass` means ready for spec approval. `needs_revision` names the failing artifact
and the stage that owns it: the issue, the spec artifacts, the design, or the
tasks. When the root cause is the issue, say so in the reason; when the spec is
wrong, name the artifact. `blocked` means a required source is unavailable. The
persona posts findings and requests changes. This skill never edits the
artifacts.

## Process

### 1. Pin and read the sources

If the change name is missing, run `openspec list --json` and ask which change.
If `root` is null, the command exits 1; that is the answer, not a CLI failure.
Stop and report that OpenSpec is not initialized. If the change list is empty,
stop; there is nothing to review.

```bash
openspec status --change "<name>" --json
openspec validate "<name>" --type change --strict
```

Read every artifact that exists, the originating issue(s) and comments through
the tracker, the existing specs the change modifies, the target repo's docs and
config, and the source and tests at the integration points. Judge `design.md` by
whether a material decision needs justification, not by whether the file exists.
If a source is unavailable, say so; do not fill the gap with assumptions.

### 2. Review five axes

Keep the axes separate. Report each one, even when it passes.

| Axis | Questions | Evidence to look for |
|---|---|---|
| Problem fit | Does the proposal solve the stated problem? Does scope match the issue? Are non-goals explicit and respected? | An issue requirement with no corresponding artifact; behavior the issue never asked for |
| Spec correctness | Are requirements and scenarios testable, complete, and consistent with existing specs? Are deltas correct? | A requirement with no scenario that can fail; contradictions, duplicates, or missing edge cases |
| Design soundness | Are decisions justified against alternatives and constraints? Does it fit the architecture? | Invented APIs, unexplained data shapes, changed observable behavior, unstated failure modes. Use `deep-module-design` for module, interface, and seam terms. |
| Task executability | Are tasks vertical slices with acceptance and verification? Could a fresh agent execute each without guessing? | Horizontal layer batching; missing acceptance; stale file paths; ordering that blocks |
| Repo and doc fit | Does it follow documented conventions? Does it conflict with existing behavior, docs, or prior decisions? | Convention drift; conflict with current code or a prior ADR |

### 3. Falsify

List the load-bearing assumptions the change most depends on, typically three to
five. Do not pad the list to reach a count. For each, find evidence in the
source, tests, specs, or official documentation. Mark it confirmed, contradicted,
or unverified.

For framework-specific claims, check official documentation rather than memory.
Cite what you checked.

### 4. Report findings

Report each finding under one axis, so the same defect does not appear twice.
Label every finding and state its remedy:

| Label | Meaning | Remedy |
|---|---|---|
| **Critical** | Wrong problem, unsafe scope, or an artifact that cannot be implemented as written | Return to the issue or explore |
| **Required** | Must be fixed before implementation | Fix the artifact |
| **Optional** | Worth considering; not blocking | Author decides |
| **Nit** | Wording or formatting only | Author decides |
| **FYI** | Context for the human; no action | None |

Each finding carries:

```markdown
**[Required]** `specs/<capability>/spec.md` - "quoted requirement"
Evidence: <source, test, spec, or doc that contradicts or is missing>
Impact: <what goes wrong if implemented as written>
Fix direction: <the change to make, not the rewritten text>
```

Prefer a small table or diagram over a wall of prose when it makes the finding
clearer. When a visual would carry the point, use `visual-explainer` and post it
with the report. Post the report to the review destination defined by the agent
file.

### 5. Verdict and gate

The verdict is capped by the evidence:

- Any **Critical** or **Required** finding: **needs revision**.
- Any load-bearing assumption still **unverified**: at least a **Required**
  finding, and **needs revision**.
- A failed strict validation, or an unavailable required source: **needs
  revision**.
- Only **Optional**, **Nit**, or **FYI** findings, with every load-bearing
  assumption confirmed or contradicted: **ready for spec approval**.

End with findings by severity, the three highest-risk issues, any questions the
human must answer, and the verdict.

Then stop. Do not edit artifacts, implement, or start remediation.

On **ready for spec approval**, do not record approval yourself. Say that human
approval is needed and name the marker the agent file defines; if it defines
none, say which marker is needed rather than inventing one. Then stop.

On **needs revision**, name the artifact pass that owns each blocking finding
(return to the issue, return to explore, or update the change artifacts) and
stop. Do not implement.

## Verification

- [ ] The change and every existing artifact were read.
- [ ] The issue, existing specs, relevant source, tests, and docs were checked.
- [ ] Strict validation ran, and its output is recorded.
- [ ] Each finding quotes its source and states impact and remedy.
- [ ] The highest-risk assumptions were confirmed or contradicted with evidence.
- [ ] A load-bearing unverified assumption, failed strict validation, or
      unavailable required source capped the verdict at **needs revision**.
- [ ] The report was posted to the configured review destination.
- [ ] No files were modified and no implementation started.
- [ ] The verdict follows the severity mapping, and the approval marker or
      blocking remediation path is explicit.
