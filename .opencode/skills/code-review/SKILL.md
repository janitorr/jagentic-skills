---
name: code-review
description: Use before merging an OpenSpec change, or when the user asks to review a diff or pull request.
---

# Code Review

## Environment

The agent file defines the tracker, approval marker, review destination, and
workspace policy. Read it before starting. If an operation you need is not
defined, ask; do not assume a specific CLI or service.

## Overview

Review the diff from a fixed point to `HEAD` before human sign-off. Keep three
questions separate:

- **Spec:** does the change faithfully implement the approved OpenSpec change
  and its originating issue?
- **Standards:** does it follow this repository's documented conventions?
- **Quality:** is it correct, tested, well-structured, secure, and fast enough?

**Stance:** read-only, evidence-first, no rubber stamp. Read-only means no
tracked source file changes; test and build commands may write caches, and the
mutation probe runs in the isolation location defined by the agent file.

## Process

### 1. Resolve the change and pin the diff

- If a change name is supplied, use it.
- For a pull request or issue, use the tracker operation defined by the agent
  file to resolve it to an OpenSpec change. If the result is ambiguous or absent,
  ask.
- If the work has no OpenSpec change, use diff-only mode: review Standards and
  Quality, mark Spec **not applicable**, and say why.

Use the base commit recorded by `vertical-slice-tdd` as the fixed point.
Otherwise use the default branch defined by the agent file. If neither exists,
ask.

```bash
git rev-parse <fixed-point>
git diff <fixed-point>...HEAD
git log <fixed-point>..HEAD --oneline
```

Confirm the ref resolves and the diff is non-empty before reviewing. Run
`git status --porcelain`. If uncommitted changes exist, include them explicitly
with `git diff` or stop and ask; `HEAD` alone does not cover them.

### 2. Load the sources

- Spec source: the change artifacts (`proposal.md`, spec deltas, `design.md`,
  the tracked task file) and the originating issue.
- Standards sources: the target repo's `AGENTS.md`, `CLAUDE.md`,
  `CONTRIBUTING.md`, `CODING_STANDARDS.md`, and documented conventions. Ignore
  vendored copies of another repo's instructions unless the user names them.
- Tests and source at the touched seams.

### 3. Discover the commands

Find the repo's focused-test, full-suite, build, and type/lint commands. Note
whether the suite is hermetic: it runs offline and touches no external services
or network.

### 4. Review the three axes

Use three headings and keep them separate.

| Axis | Check |
|---|---|
| Spec | Requirements missing or partial; behavior not asked for; requirements implemented incorrectly. Quote the artifact line. |
| Standards | Documented-rule violations with the rule cited. Apply the smell baseline in `references/smells.md` as labelled judgement calls; a documented repo standard overrides it; skip anything tooling enforces. |
| Quality | Correctness and edge cases; error paths; test quality; architecture and coupling; security boundaries; N+1, unbounded work, and hot-path cost. Use `deep-module-design` for module, interface, and seam findings. |

### 5. Probe the tests

Reading tests is not enough; check whether they would catch a regression. If the
suite is hermetic, run the probe in the isolation location the agent file defines
(a temporary worktree, container, or copy outside the review checkout):

1. Create an isolated copy of the reviewed `HEAD`.
2. Either invert one branch condition or change one boundary value at a touched
   seam.
3. Run the focused test for the behavior that mutation targets.
4. Remove the isolated copy and confirm no tracked source file in the review
   checkout changed.

The focused test must **fail** against the mutation. If it passes, record a
**Required** finding: the mutation survived. If the suite is not hermetic or the
environment cannot support an isolated copy, mark the test-quality axis
**unverified** and name the skip in the verdict. Do not return **ready for merge
sign-off** without human acceptance of that gap.

### 6. Run the verification

Run the focused tests, full suite, build, and type/lint where available. Record
the exact commands and outcomes. A green suite makes "tests pass" evidence; not
running it makes it a claim. Record any command you could not run as unverified.

### 7. Report findings

Label every finding and state its action:

| Label | Meaning | Action |
|---|---|---|
| **Critical** | Wrong spec behavior, security issue, data loss, or broken functionality | Stop the merge and escalate |
| **Required** | Must be addressed before merge | Fix before merge |
| **Optional** | Worth considering | Author decides |
| **Nit** | Minor or stylistic | Author may ignore |
| **FYI** | Context only | None |

Each finding states file and line, evidence, impact, and a fix direction. Within
each axis, order by leverage: correctness and security first, then structural
issues, then nits. Report each finding under one axis, with a verdict per axis.
When a visual would make a finding clearer, use `visual-explainer` and post it
with the report.

Post the report to the review destination defined by the agent file.

### 8. Verdict and gate

Map severity to the gate:

- Any **Critical** or **Required** finding: **needs revision**.
- Only **Optional**, **Nit**, or **FYI** findings: **ready for merge sign-off**.

End with a verdict for each axis (**pass** or **changes required**), the worst
issue within each axis, and the overall gate. The severity labels are scoped to
merge review, not to spec review.

Then stop. Do not edit code or apply fixes.

- On **ready for merge sign-off**, hand off to the human for sign-off. After
  sign-off, the change owner archives it with the `openspec-archive-change` skill.
- On **needs revision**, name the remediation path: artifact problems return to
  `spec-review`, code problems return to `vertical-slice-tdd`. Do not start
  either pass in this turn.

```
Next: human sign-off, then openspec-archive-change
      or vertical-slice-tdd for code fixes
```

## Verification

- [ ] The change resolved, and the fixed point came from the implementation
      handoff or the agent file's default branch.
- [ ] The diff is non-empty, and every artifact and issue was read.
- [ ] Standards came from the target repo, not a vendored copy.
- [ ] Tests, build, and type/lint ran, with commands and outcomes recorded.
- [ ] The probe either produced a failing test or has a recorded skip reason.
- [ ] No tracked source file in the review checkout changed.
- [ ] Every finding cites evidence and carries a severity and action.
- [ ] The report reached the configured review destination.
- [ ] The verdict follows the severity mapping, with per-axis results and a named
      remediation or archive path.
