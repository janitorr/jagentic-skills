# Synthesis record

Five skills, one per pipeline stage. Each is original text that combines
mechanisms from several bundles; this file records what came from where and
what was deliberately left out.

## Pipeline

```
/issue-interview
  -> GitHub issue(s)            source of truth for scope and acceptance
/issue-to-openspec
  -> openspec-explore (always)
  -> openspec-propose
  -> openspec/changes/<change>  proposal, specs delta, design, tasks
/spec-review
  -> read-only findings
  -> human gate
/vertical-slice-tdd
  -> tasks executed as vertical slices, test-first, evidence
/code-review
  -> read-only findings across spec, standards, quality
  -> human gate
```

OpenSpec owns artifact creation and task tracking. These skills own the
decisions OpenSpec deliberately leaves out: when the issue is ready, when
exploration is done, whether the artifacts hold up, how to slice and test, and
what a review must prove.

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

## Deliberate omissions

- No routing skill. `/command` names and repo workflows are the router.
- No agent-delegation skill. The command or workflow constructs the brief; each
  stage skill states the minimum context a fresh agent needs.
- No visual-explainer skill. It is a `/command` called when useful; review
  outputs prefer a small diagram or table over prose.
- No commit, PR, archive, or deploy workflow. Those belong to the repo and to
  OpenSpec `apply` / `archive`.
- No duplicated OpenSpec commands. The skills reference `openspec-explore`,
  `openspec-propose`, and `openspec-apply-change` rather than reimplementing
  their scaffolding, validation, or checkbox rules.

## Gates

1. Issue publication requires an explicit human yes.
2. Explore always runs before propose, even when the issue looks complete.
3. Spec review is read-only. Implementation starts only after the human sets the
   `ready-for-dev` label on the issue or PR.
4. Tasks are checked only when the specified behavior is fully implemented;
   deferred tasks stay unchecked with a reason.
5. Code review is read-only; fixes happen in a separate pass after human review.
6. Implementation commits once per green slice. This is an explicit override of
   `openspec-apply`'s default single commit at run completion.
