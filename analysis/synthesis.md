# Synthesis record

Ten skills: five pipeline stages and five supporting skills. Each is original
text that combines mechanisms from several bundles; this file records what came
from where and what was deliberately left out.

## Pipeline

```
issue-interview
  -> issue(s) in the tracker    source of truth for scope and acceptance
issue-to-openspec
  -> openspec-explore (always)
  -> openspec-propose
  -> openspec/changes/<change>  proposal, specs delta, design, tasks
spec-review
  -> read-only findings
  -> human gate
vertical-slice-tdd
  -> tasks executed as vertical slices, test-first, evidence
code-review
  -> read-only findings across spec, standards, quality
  -> human gate
```

OpenSpec owns artifact creation and task tracking. These skills own the
decisions OpenSpec deliberately leaves out: when the issue is ready, when
exploration is done, whether the artifacts hold up, how to slice and test, and
what a review must prove.

## Environment boundary

Skills own process and gates. Agent files own the environment: tracker
operations (read, create, amend), the approval marker (label, comment, or other),
the review destination (PR comment, issue comment, chat, or file), and workspace
and delivery policy (base branch, isolation, temp location, push and PR rules).
OpenSpec is fixed as the artifact system; it is not abstracted. A skill that
needs an undefined environment operation asks instead of assuming a CLI.

## Provenance

| Skill | Mechanism | Source |
|---|---|---|
| `issue-interview` | Hypothesis plus confidence; one question at a time; explicit yes; out-of-scope line | addyosmani `interview-me` |
| | Design tree, frontier rounds, recommended answer per question, facts by agent | mattpocock `grilling` |
| | Know what you know, look before asking, size the work | superpowers `brainstorming` |
| | Divergent variants then converge; "Not Doing" list | addyosmani `idea-refine` |
| | Persist the artifact, stop the turn after confirmation | humanlayer `rpi` |
| `issue-to-openspec` | Explore before proposing; task directory; phase handoff | humanlayer `rpi`, OpenSpec explore/propose |
| | Spec as a gated artifact; assumptions surfaced; capability map | addyosmani `spec-driven-development` |
| | Synthesize existing context instead of re-interviewing | mattpocock `to-spec` |
| | Validation and required-artifact closure | OpenSpec `status` / `instructions` |
| `spec-review` | Fresh-context reviewer biased to disprove | addyosmani `doubt-driven-development` |
| | Separate axes; quote the source line; severity labels | mattpocock two-axis review, addyosmani five-axis |
| | Verify technical claims against official docs | addyosmani `source-driven-development` |
| | Treat artifact and external text as data, not instructions | addyosmani context-engineering |
| `vertical-slice-tdd` | Iron law, watched red, minimal green, full suite | superpowers TDD |
| | Discover the repo's commands; prove-it; DAMP; mock preference | addyosmani TDD |
| | Agree seams; vertical slices; tautology and horizontal-slice anti-patterns | mattpocock `tdd` |
| | One slice at a time, leave green, checkpoint | addyosmani `incremental-implementation` |
| | Evidence before completion; task checkbox only when complete | superpowers `verification-before-completion`, OpenSpec apply |
| `code-review` | Spec axis vs standards axis, never merged | mattpocock `code-review` |
| | Correctness, readability, architecture, security, performance; severity; structural remedies | addyosmani `code-review-and-quality` |
| | Receiver verifies findings and pushes back with evidence | superpowers `receiving-code-review` |
| | Read-only report, human gate, separate remediation pass | decided workflow |

Supporting skills:

| Skill | Mechanism | Source |
|---|---|---|
| `visual-explainer` | Smallest view: pseudocode, call tree, component tree, file tree, Mermaid, diff, table, focused HTML | humanlayer `show-me` |
| | Visual outline for a pull request | humanlayer `visual-pr` |
| | Teach from the reader's model; one tangible win; primary sources | mattpocock `teach` |
| | Each block earns its place; deliberate format arguments | mattpocock `writing-shape` |
| `deep-module-design` | Module, interface, depth, seam, adapter, leverage, locality; deletion test; design twice | mattpocock `codebase-design` |
| | Contract first, error semantics, boundary validation, additive change | addyosmani `api-and-interface-design` |
| | Chesterton's fence; behavior-preserving simplification; one change at a time | addyosmani `code-simplification` |
| | Expand/contract, strangler, adapter, feature-flag migration, deprecation decision | addyosmani `deprecation-and-migration` |
| | Glossary and ADR as durable domain context | mattpocock `domain-modeling` |
| `skill-forge` | TDD for skills; baseline failure; match form to failure; micro-tests; close loopholes | superpowers `writing-skills` |
| | Context vs cognitive load; progressive disclosure; leading words; negation backfires; pruning | mattpocock `writing-for-agents` |
| | Context hierarchy and budget; confusion management | addyosmani `context-engineering` |
| | Conditional `<important if>` blocks for agent instructions | humanlayer `improve-claude-md` |
| `git-workflow` | Save points, atomic commits, message why, branch sizing, worktrees, versioning | addyosmani `git-workflow-and-versioning` |
| | Detect isolation, prefer native tools, verify ignored, clean baseline | superpowers `using-git-worktrees` |
| | Verify, present integration options, merge, cleanup, explicit discard | superpowers `finishing-a-development-branch` |
| | Block destructive git operations rather than relying on reminders | mattpocock `git-guardrails-claude-code` |
| `documentation` | ADRs, README, inline why, API docs, changelog, agent docs, prose review | addyosmani `documentation-and-adrs` |
| | Agent instructions: bare foundations, conditional rules, keep commands, prune tool territory | humanlayer `improve-claude-md`, mattpocock `writing-for-agents` |
| | Context pointers and one source of truth | addyosmani `context-engineering` |
| | Verify framework claims against primary sources | addyosmani `source-driven-development` |

## Deliberate omissions

- No routing skill. Command names, the agent file, and repo workflows are the
  router.
- No agent-delegation skill. The command or workflow constructs the brief; each
  stage skill states the minimum context a fresh agent needs.
- `git-workflow` owns local git discipline and release versioning. Push, pull
  request, archive, and deploy policy remain with the agent file and OpenSpec.
- `documentation` owns docs, ADRs, READMEs, and agent instruction files.
  `skill-forge` owns `SKILL.md` files; the two do not overlap.
- No duplicated OpenSpec commands. The skills reference `openspec-explore`,
  `openspec-propose`, and `openspec-apply-change` rather than reimplementing
  their scaffolding, validation, or checkbox rules.

## Gates

1. Issue publication requires an explicit human yes.
2. Explore always runs before propose, even when the issue looks complete.
3. Spec review is read-only. Implementation starts only after the human records
   approval with the marker defined by the agent file (for example, a
   `ready-for-dev` label).
4. Tasks are checked only when the specified behavior is fully implemented;
   deferred tasks stay unchecked with a reason.
5. Code review is read-only; fixes happen in a separate pass after human review.
6. Implementation commits once per green slice. This is an explicit override of
   `openspec-apply`'s default single commit at run completion.
