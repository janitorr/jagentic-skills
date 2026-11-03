---
name: spec-review
description: Use when the user invokes /spec-review, or before implementing an OpenSpec change. Read-only review of proposal, specs, design, and tasks against the issue, source, existing specs, and docs.
disable-model-invocation: true
---

# Spec Review

## Overview

Review an OpenSpec change before code exists. A confident artifact is not a
correct one, and every hour spent here prevents a wrong implementation later.

**Stance:** read-only, adversarial, evidence-first. Your job is to try to
disprove the artifacts, not to approve them. A clean review is a valid result;
an invented finding is not.

## Inputs

- The change name.
- The originating GitHub issue(s), including comments.
- The change artifacts: `proposal.md`, spec deltas, `design.md`, `tasks.md`.
- The existing specifications, project docs, and relevant source and tests.

## Process

### 1. Pin the sources of truth

```bash
openspec status --change "<name>" --json
openspec validate "<name>" --type change --strict
```

Read every artifact from disk. Read the issue, the existing specs it changes,
the project context, and the source and tests at the integration points. If a
source is unavailable, say so; do not fill the gap with assumptions.

### 2. Review five axes

Keep the axes separate. Report each one, even when it passes.

| Axis | Questions |
|---|---|
| Problem fit | Does the proposal solve the stated problem? Does scope match the issue? Are non-goals explicit and respected? |
| Spec correctness | Are requirements and scenarios testable, complete, and consistent with existing specs? Are deltas correct? Any contradictions, duplicates, or missing edge cases? |
| Design soundness | Are decisions justified against alternatives and constraints? Does it fit the architecture? Are APIs, data shapes, and failure modes real rather than invented? |
| Task executability | Are tasks vertical slices with acceptance and verification? Is ordering sound? Could a fresh agent execute each task without guessing? |
| Repo and doc fit | Does it follow documented conventions? Does it conflict with existing behavior, docs, or prior decisions? |

### 3. Try to falsify it

List the three to five assumptions the change most depends on. For each, find
evidence in the source, tests, specs, or official documentation. Mark it
confirmed, contradicted, or unverified.

Look specifically for:

- An issue requirement with no corresponding spec delta.
- Behavior in the artifacts that the issue never asked for.
- A spec requirement with no scenario that can fail.
- A task that batches layers horizontally instead of cutting a slice.
- Stale file paths, invented APIs, or claims contradicted by current code.
- A design decision that quietly changes externally observable behavior.
- An unresolved question disguised as an assumption.

For framework-specific claims, check official documentation rather than memory.
Cite what you checked.

### 4. Report findings

Label every finding:

| Label | Meaning |
|---|---|
| **Critical** | Wrong problem, unsafe scope, or an artifact that cannot be implemented as written |
| **Required** | Must be fixed before implementation |
| **Optional** | Worth considering; not blocking |
| **Nit** | Wording or formatting only |
| **FYI** | Context for the human; no action |

Each finding carries:

```markdown
**[Required]** `specs/<capability>/spec.md` - "quoted requirement"
Evidence: <source, test, spec, or doc that contradicts or is missing>
Impact: <what goes wrong if implemented as written>
Fix direction: <the change to make, not the rewritten text>
```

Prefer a small table or diagram over a wall of prose when it makes the finding
clearer.

### 5. Verdict and gate

End with:

- Findings by severity.
- The three highest-risk issues, if any.
- Open questions the human must answer.
- Verdict: **ready for human review** or **needs revision**.

Then stop. Do not edit artifacts, do not implement, and do not start remediation.
The human decides; fixes are a separate pass.

## Red Flags

- Reviewing the proposal but not the spec deltas or tasks.
- Checking artifacts only against each other, never against the issue or source.
- Reporting style preferences as blocking findings.
- Accepting a requirement because it sounds reasonable, without a failing
  scenario that could prove it.
- Merging all axes into one score, so a spec failure hides behind clean tasks.
- Editing the artifacts to "help" while reviewing.
- Zero findings invented to look thorough.

## Verification

- [ ] All artifacts and the originating issue were read.
- [ ] Existing specs, relevant source, tests, and docs were checked.
- [ ] Strict validation ran, and its output is recorded.
- [ ] Each finding quotes its source and states impact.
- [ ] The three highest-risk assumptions were tested, not just listed.
- [ ] No files were modified and no implementation started.
- [ ] The verdict and human gate are explicit.
