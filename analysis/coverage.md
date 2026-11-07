# Coverage against the inventory categories

Eleven synthesized skills: five pipeline stages plus six supporting skills. This
file maps the inventory categories to them and names what is still missing.

Status: **Covered** (a skill owns it), **Partial** (some mechanisms are absorbed,
others absent), **Missing** (no skill owns it), **Skipped** (deliberately owned by
commands or agent files).

| # | Category | Covered by | Status | Gap |
|---|---|---|---|---|
| 1 | Routing and setup | commands, agent files | Skipped | Invocation is the router. |
| 2 | Intent, ideation, interviews | `issue-interview` | Partial | Interview, grilling, and brainstorming are absorbed. Divergent option generation (`idea-refine`) is not. |
| 3 | Spec and planning | `issue-to-openspec`, `spec-review` | Covered | OpenSpec supplies artifacts and tasks. No map for work larger than one change (`wayfinder`). |
| 4 | Implementation | `vertical-slice-tdd` | Covered | — |
| 5 | Multi-agent orchestration | commands, agent files | Skipped | Fresh-context dispatch is environmental. No shared fan-out, merge, or handoff pattern. |
| 6 | Testing and debugging | `vertical-slice-tdd`, `code-review` | Partial | Test-first is covered. Root-cause debugging has no named loop; two synthetic baselines hit a ceiling (6/6 control fixed the root), so no skill was added. |
| 7 | Review and quality gates | `spec-review`, `code-review` | Partial | Giving review is covered. Receiving review and a written quality contract are not. |
| 8 | Architecture and refactoring | `deep-module-design` | Partial | Module depth, seams, simplification, and migration are covered. HTTP wire contracts — status and error semantics, boundary validation, pagination, versioning, and idempotency — are not in the skill body. Two baseline rounds (3 control + 3 `deep-module-design` runs each) found no behavioral failure, so no HTTP skill was added; see `analysis/evidence/api-contract-design.md`. |
| 9 | Frontend and UI | — | Missing | No accessibility, design-system, or real-browser verification skill. |
| 10 | Delivery, git, repo hygiene | `git-workflow`, `ci-cd` | Partial | Commits, conflicts, pushes, and releases are covered. CI/CD pipelines have a narrow supporting skill (`ci-cd`), 31/32 against 26-28 control; the Azure caching smoke and trigger test are complete (`cicd.md`). Worktree mechanics belong to the harness; issue triage is not covered. |
| 11 | Security, performance, observability | `code-review` axes | Partial | Review has a compact security/performance checklist (`references/quality-checks.md`); no skill owns threat modeling, profiling, or instrumentation. |
| 12 | Docs, research, teaching, visual explanation | `documentation`, `visual-explainer` | Partial | ADRs, READMEs, reference pages, changelogs, agent instructions, onboarding guides, runbooks, and how-to docs are covered. Human-facing docs delegate diagrams and one-pagers to `visual-explainer`; agent instructions stay text-first. Research and multi-session teaching are not. |
| 13 | Meta: skills, context, agent docs | `skill-forge`, `documentation` | Covered | Skill authoring and agent docs have owners. |
| 14 | Misc utilities | — | Skipped | Too narrow to generalize. |

## Supporting skills added

| Skill | Covers | Absorbs |
|---|---|---|
| `visual-explainer` | Diagrams, diffs, component trees, HTML artifacts, teaching views | show-me, visual-pr, teach, writing-shape |
| `deep-module-design` | Depth, seams, interfaces, domain terms, simplification, migration | codebase-design, code-simplification, deprecation-and-migration, domain-modeling |
| `skill-forge` | Skill authoring, baseline testing, wording micro-tests, pruning | writing-skills, writing-for-agents, context-engineering, improve-claude-md |
| `git-workflow` | Commits, branches, worktrees, conflicts, finishing, versioning | git-workflow-and-versioning, using-git-worktrees, finishing-a-development-branch, git-guardrails |
| `documentation` | ADRs, READMEs, reference pages, changelogs, agent instructions, onboarding guides, runbooks, how-to docs | documentation-and-adrs, writing-for-agents, improve-claude-md, context-engineering |
| `ci-cd` | CI/CD pipelines, build-once promotion, environment gates, deployment verification, rollback | ci-cd-and-automation, shipping-and-launch |

`api-and-interface-design` overlaps `deep-module-design` at the module-interface
level, but its HTTP material is not absorbed. See the row 8 gap and the negative
evaluation in `analysis/evidence/api-contract-design.md`.

## Remaining gaps

| Candidate | Category | Why it is still open |
|---|---|---|
| `debug-loop` | Testing and debugging | The only missing lifecycle stage. Two synthetic baselines hit a ceiling (6/6 control fixed the root); try a real codebase before writing it. |
| `production-readiness` | Security, performance, observability | Review axes exist, but no runnable gate for threat modeling, profiling, or instrumentation. |
| `browser-verified-ui` | Frontend and UI | Only if UI work is in scope. |
| `review-reception` | Review | How to verify findings, push back with evidence, and implement one at a time. Could be folded into `code-review` instead. |
| `ship-and-verify` | Delivery | Release mechanics beyond git: staged rollout, rollback, and triage. A narrow `ci-cd` skill now covers pipelines (31/32 vs 26-28 control). |
| `agent-delegation` | Multi-agent orchestration | Fresh-context briefs, fan-out, merge, and handoff. Only if those patterns should be shared. |
| `http-api-contract` | Architecture and refactoring | The artifact gap is real, but two baseline rounds (3 control + 3 `deep-module-design` runs each) found no behavioral failure. Revisit only on a demonstrated failure or a weaker model. |
| `idea-refine` / `wayfinder` | Intent / planning | Add only when a real multi-option or multi-change initiative appears. |

Not recommended as new skills: routing, misc utilities, and a separate
`production-readiness` skill if the security, performance, and observability
checks remain inside review.
