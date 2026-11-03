---
name: code-review
description: Use when the user invokes /code-review, or before human sign-off on a completed OpenSpec change. Read-only review across spec, standards, and quality axes.
disable-model-invocation: true
---

# Code Review

## Overview

Review the diff from a fixed point to `HEAD` before human sign-off. Keep three
questions separate:

- **Spec:** does the change faithfully implement the approved OpenSpec change
  and its originating issue?
- **Standards:** does it follow this repository's documented conventions?
- **Quality:** is it correct, tested, well-structured, secure, and fast enough?

Separate axes stop a clean diff from hiding a wrong implementation, and stop a
correct implementation from hiding unreadable or unsafe code.

**Stance:** read-only, evidence-first, no rubber stamp. Zero findings is valid.

## Inputs

- The change name, or the issue and PR.
- A fixed point: the merge-base with the default branch, or a commit, tag, or
  branch supplied by the user.
- The OpenSpec artifacts and the originating issue.

## Process

### 1. Pin the diff

```bash
git rev-parse <fixed-point>
git diff <fixed-point>...HEAD
git log <fixed-point>..HEAD --oneline
```

Confirm the ref resolves and the diff is non-empty before reviewing. If there is
no fixed point, ask for one; do not invent a base.

### 2. Load the sources

- Spec source: the change artifacts (`proposal.md`, spec deltas, `design.md`,
  `tasks.md`) and the issue.
- Standards sources: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
  `CODING_STANDARDS.md`, and any documented conventions. A documented repo
  standard overrides generic taste.
- Tests and source at the touched seams.

### 3. Review the three axes

| Axis | Check |
|---|---|
| Spec | Requirements missing or partial; behavior not asked for; requirements implemented incorrectly. Quote the artifact line. |
| Standards | Documented-rule violations with the rule cited. Use the Fowler smell baseline as labelled judgement calls: mysterious name, duplicated code, feature envy, data clumps, primitive obsession, repeated switches, shotgun surgery, divergent change, speculative generality, message chains, middle man, refused bequest. Skip anything tooling enforces. |
| Quality | Correctness and edge cases; error paths; test quality; architecture and coupling; security boundaries; N+1, unbounded work, and hot-path cost. |

For Quality, check whether the tests would catch a regression. Reading them is
not enough: if safe, invert one condition in a scratch copy, run the suite,
confirm it goes red, and restore the file. A mutation that stays green is a
missing test.

### 4. Run the verification

Run the repo's own test, build, and type/lint commands. Record the exact commands
and outcomes. A green suite makes "tests pass" evidence; not running it makes it
a claim.

### 5. Report findings

Label every finding:

| Label | Meaning |
|---|---|
| **Critical** | Blocks merge: security, data loss, broken functionality, wrong spec behavior |
| **Required** | Must be addressed before merge |
| **Optional** | Worth considering |
| **Nit** | Minor or stylistic; author may ignore |
| **FYI** | Context only |

Each finding states file and line, evidence, impact, and a fix direction. Lead
with leverage: correctness and security first, then structural issues, then
nits. A structural problem is the review; do not bury it under cosmetics.

Report each axis separately. Do not merge them into one score or pick a single
winner across axes.

### 6. Verdict and gate

End with a per-axis verdict (**pass** or **changes required**), the worst issue
within each axis, and the overall handoff: **ready for human review** or
**remediation required**.

Then stop. Do not edit code, apply fixes, or rerun implementation. Fixes are a
separate pass after the human reviews the findings.

## Red Flags

- Reviewing only whether tests pass.
- "LGTM" without commands, quotes, or evidence.
- Reviewing code without reading the spec or issue.
- Merging axes so a spec failure disappears behind passing standards.
- Reporting a style preference as Required.
- Inflating nitpicks into a long list while missing the structural issue.
- Editing files while reviewing.
- Accepting "I'll clean it up later."

## Verification

- [ ] The fixed point resolves and the diff is non-empty.
- [ ] The change artifacts and issue were read.
- [ ] Documented standards were checked, not just general taste.
- [ ] Tests, build, and type/lint ran, with commands and outcomes recorded.
- [ ] Test sensitivity was checked, by mutation or an explicit reason it was
      unsafe.
- [ ] Every finding cites evidence and carries a severity.
- [ ] Axes are reported separately, with a verdict for each.
- [ ] No files were modified; the human gate is explicit.
