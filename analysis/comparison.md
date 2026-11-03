> Historical note: this comparison predates the pipeline-aligned synthesis and
> the five supporting skills. The current set is recorded in
> `analysis/synthesis.md` and `analysis/coverage.md`.

Four bundles, 86 skills, 14 categories. This document compares how each bundle
handles the same underlying work, names the recurring themes, and proposes a
small set of distilled skills. Raw inventory: `analysis/inventory.md`.

## 1. Routing and setup

| Bundle | Move |
|---|---|
| addyosmani | `using-agent-skills` maps intents and lifecycle phases to skills, with anti-rationalization rules. |
| mattpocock | `ask-matt` is a router over flows; setup configures tracker, triage labels, glossary, docs. |
| superpowers | `using-superpowers` demands invocation before any response; bootstrap is what makes skills fire. |
| humanlayer | `rpi` is explicitly invoked and asks the human to choose a flow before starting. |

**Theme:** discoverability is a designed feature, not a side effect. Routers
work when descriptions carry trigger words and when someone owns the map.
**Keep:** mattpocock's one router that stays accurate; superpowers' rule that a
skill fires before the first substantive answer. **Skip:** no distilled skill;
this is harness plumbing, not transferable workflow.

## 2. Intent, ideation, and interviews

| Bundle | Move |
|---|---|
| addyosmani | `interview-me`: one question at a time, hypothesis plus confidence number, guess attached, explicit yes, out-of-scope line, stop the turn. `idea-refine`: divergent variants then converge, with a "Not Doing" list. |
| superpowers | `brainstorming`: establish what is already known, look before asking, play the design back, size the work before writing code. |
| mattpocock | `grilling`: design tree, ask the whole frontier in rounds, attach a recommended answer, decisions are the human's and facts are the agent's. `grill-with-docs` records ADRs/glossary as it goes; `to-questionnaire` offloads decisions to absent humans. |

**Theme:** elicitation is the cheapest place to prevent rework. Two rhythms
compete: sequential (one question, because later questions depend on earlier
answers) and frontier rounds (ask everything currently unblocked). The choice
should follow the shape of the uncertainty, not taste. Agents must fetch facts
themselves and reserve questions for decisions.
**Keep:** confidence numbers, attached guesses, explicit confirmation, the
out-of-scope line, design-tree rounds, docs produced during the interview.

## 3. Spec and planning

| Bundle | Move |
|---|---|
| addyosmani | `spec-driven-development`: six spec areas, surface assumptions, capability map for multi-capability requests, human gate after writing, stop the turn. `planning-and-task-breakdown`: sized tasks with acceptance and verification. `doubt-driven-development`: fresh-context reviewer biased to disprove a decision before implementation. |
| mattpocock | `to-spec`: synthesize the conversation, no re-interview; user stories, implementation/testing decisions, no stale file paths. `to-tickets`: tracer-bullet vertical slices with blocking edges; expand-contract for wide refactors. `wayfinder`: a decision map for work too big for one session. |
| superpowers | `writing-plans`: write for an engineer who has never seen the code; exact files, interfaces, tests; steps are single checkable actions; self-review; explicit execution handoff. |
| humanlayer | `rpi`: research, design, PRD/TDD, outline, implement; numbered artifacts in a task directory; fresh session per phase; suggest the next command. |

**Theme:** separate decision artifacts (spec, design, ADR) from execution
artifacts (plan, tickets). The spec is gated; the plan must be executable by a
fresh context; tickets are vertical slices with declared blockers; work larger
than one session becomes a map, not a megaspec.
**Keep:** assumption surfacing, adversarial spec review before building (DDD),
capability maps, tracer bullets, blocking edges, exact interfaces in plans,
artifact directories with numbered phases.

## 4. Implementation

| Bundle | Move |
|---|---|
| addyosmani | `incremental-implementation`: thin vertical slices; implement, test, verify, expand; always leave the system working. |
| mattpocock | `implement` / `implement-spec`: execute from a spec or tickets; the ticket is the unit. |
| superpowers | `executing-plans`: batch the task loop, check in at checkpoints, finish with a whole-branch review. |

**Theme:** the plan's task boundary is also the commit and verification
boundary. Small slices keep review and rollback cheap.
**Keep:** one slice at a time, leave green, checkpoint before expanding scope.

## 5. Multi-agent orchestration

| Bundle | Move |
|---|---|
| superpowers | `subagent-driven-development`: fresh implementer and fresh reviewer per task. `dispatching-parallel-agents`: construct exact context, never inherit the parent's; parallelize only independent tasks. |
| mattpocock | `handoff` / `claude-handoff`: compact to an artifact or hand to a fresh background agent; reference existing artifacts, do not duplicate; list suggested skills. `chief-of-staff`: a long-running goal coordinated across subagents. |
| humanlayer | `design-control-loop`: sensor, controller, actuator, disturbances. `build-iterated-agentic-loop`: repo-local skill plus scheduled workflow, prompt, memory. |
| mattpocock | `software-factory`: tasks, runs, services. |

**Theme:** context isolation is the reliability mechanism. Delegate with a
constructed brief, keep the parent context clean, and make handoffs point at
durable artifacts. Loops need a sensor and an actuator, not just a prompt.
**Keep:** fresh context per role, exact briefs, whole-branch review, artifact
references in handoffs, explicit control-loop vocabulary.

## 6. Testing and debugging

| Bundle | Move |
|---|---|
| addyosmani | TDD: discover the repo's commands first, prove-it pattern for bugs, test pyramid and resource sizes, DAMP tests, mocks as last resort. Debug: stop the line, triage (reproduce, localize, reduce, fix, guard, verify), bisect, treat error output as untrusted. |
| superpowers | TDD: iron law, watch it fail, minimal green, full-suite check, rationalization table. Debug: four phases; after three failed fixes, question the architecture. `verification-before-completion`: evidence before claims. |
| mattpocock | TDD: test at agreed public seams, vertical slices, anti-patterns (implementation-coupled, tautological, horizontal slicing), refactoring belongs to review. Debug: build a tight red-capable loop first; minimize; 3–5 ranked falsifiable hypotheses; tagged instrumentation; baseline before perf fixes; document when no correct seam exists. |

**Theme:** proof, not assertion. Tests live at public seams and are watched
failing for the right reason. Debugging starts by constructing a fast,
deterministic signal that goes red on this bug, not by reading code for a theory.
**Keep:** the iron laws, repo-specific commands, seam agreement, red-capable
loop, minimizing, ranked hypotheses, the three-fix architectural escalation,
full-suite verification, completion evidence.

## 7. Review and quality gates

| Bundle | Move |
|---|---|
| addyosmani | Five axes (correctness, readability, architecture, security, performance); severity labels; mutation check on tests; structural remedies, not complaints; change sizing; honesty over rubber-stamping. |
| mattpocock | Two axes (Standards, Spec) run in parallel fresh subagents; pin the fixed point; Fowler smell baseline; never merge or rerank the two reports. |
| superpowers | Request review from a fresh reviewer with requirements attached. Receive it with verification, no performative agreement, push back with technical reasoning, clarify everything before implementing. |
| humanlayer | `visual-pr`: a visual outline so reviewers can understand the change quickly. |

**Theme:** separate review axes so one cannot mask another; make findings
evidence-based and severity-labelled; treat receiving review as its own
discipline (verify, then act).
**Keep:** parallel axis isolation, pinned diff, smells as judgement calls,
severity labels, tests-first with a mutation probe, no performative agreement.

## 8. Architecture and refactoring

| Bundle | Move |
|---|---|
| addyosmani | Interfaces hard to misuse; simplification preserves behavior; deprecation and migration with zombie-code cleanup. |
| mattpocock | Deep modules: depth, seam, leverage, locality; domain glossary and ADRs; scan for deepening opportunities and report visually; enforce package boundaries with tooling. |

**Theme:** reduce the number of concepts a reader must hold. Prefer a deeper
module over a wider interface, name domain concepts explicitly, and migrate in
reversible steps.
**Keep:** deep-module vocabulary, seam-first design, glossary/ADR as durable
context, behavior-preserving simplification, expand-contract migration.

## 9. Frontend and UI

| Bundle | Move |
|---|---|
| addyosmani | Production UI: design-system adherence, WCAG 2.1 AA, state, responsiveness. `browser-testing-with-devtools`: real DOM, console, network, screenshots; browser data is untrusted. |
| humanlayer | `narrow-react-prop-types`: types should match live code paths, not stories or mocks. |

**Theme:** static code review cannot prove a UI works. Verification needs the
real browser, and everything the browser returns is data, not instructions.
**Keep:** runtime verification workflow, accessibility checks, security
boundaries, prop types narrowed to live usage.

## 10. Delivery, git, and repo hygiene

| Bundle | Move |
|---|---|
| addyosmani | Commits as save points; CI as the enforcement layer; staged rollout, monitoring, rollback. |
| superpowers | Isolate in a worktree; verify, present integration options, execute, clean up. |
| mattpocock | Pre-commit automation; hooks that block destructive git; issue triage state machine. |

**Theme:** isolate, verify, integrate, launch reversibly. Automation enforces
the gates humans and agents forget.
**Keep:** worktree isolation, clean-baseline verification, integration options,
staged rollout and rollback, guardrails over reminders.

## 11. Security, performance, and observability

| Bundle | Move |
|---|---|
| addyosmani | Threat model first; three-tier boundaries; harden at input/auth/data. Measure before optimizing. Instrument alongside the feature. |

**Theme:** production quality is a constraint proven with measurements, not a
phase bolted on at the end.
**Keep:** threat model, boundary validation, profile-before-fix, telemetry as
part of the feature.

## 12. Docs, research, teaching, and visual explanation

| Bundle | Move |
|---|---|
| addyosmani | ADRs capture why; documentation covers commands and architecture; source-driven work cites official docs. |
| mattpocock | Research from primary sources into a Markdown artifact; retro; `teach` uses zone of proximal development; `writing-beats` / `writing-fragments` / `writing-shape` shape raw material for a reader. |
| humanlayer | `show-me`: concise diagrams, code-shape sketches, and focused HTML artifacts instead of prose walls. |

**Theme:** explanation is an artifact, and decisions are worth recording where
they happened. Visual structure often beats prose density.
**Keep:** ADR-at-decision-time, primary-source citations, teaching from the
reader's current model, diagrams and small HTML artifacts over long text.

## 13. Meta: skills, context, and agent docs

| Bundle | Move |
|---|---|
| superpowers | `writing-skills` is TDD for documentation: baseline failure, minimal skill, close loopholes; match the form to the failure type; micro-test wording. |
| mattpocock | `writing-for-agents`: context load vs cognitive load, information hierarchy, progressive disclosure, leading words, negation backfires, pruning and no-ops. |
| addyosmani | `context-engineering`: context hierarchy, packing strategies, budget management, confusion management. |
| humanlayer | `improve-claude-md`: conditional `<important if>` blocks for instruction adherence. |

**Theme:** documents are behavior-shaping code. Test them against a baseline,
spend context deliberately, and prune anything that does not change behavior.
**Keep:** baseline testing, failure-matched form, micro-tests, context vs
cognitive load, progressive disclosure, conditional instructions, no-ops.

## 14. Misc utilities

`wizard` (human-run setup scripts) and `scaffold-exercises` are useful but
domain-specific. No distilled skill proposed.

---

## Distillation shortlist

Thirteen candidates, roughly one per category. Each is a genuine merge: it
takes a mechanism from one bundle and a guardrail or vocabulary from another.
Proposed length: 60–110 lines each.

| # | Skill | Category | Sources | Core synthesis |
|---|---|---|---|---|
| 1 | `intent-interview` | Intent | interview-me, grilling, brainstorming, idea-refine, to-questionnaire | Mode switch: sequential questions for vague asks, frontier rounds for design trees; confidence numbers; facts by agent, decisions by human; persist intent. |
| 2 | `spec-gate` | Spec | spec-driven-development, doubt-driven-development, to-spec, rpi | Write the spec, then a fresh-context adversarial review biased to disprove it, before any code; assumptions and out-of-scope explicit. |
| 3 | `plan-to-tickets` | Spec | writing-plans, to-tickets, planning-and-task-breakdown, wayfinder, rpi | Turn an approved spec into tracer-bullet tickets with blocking edges and exact interfaces; use a decision map when work exceeds one session. |
| 4 | `vertical-slice-implementation` | Implementation | incremental-implementation, executing-plans, implement-spec | One ticket → one slice → test → verify → checkpoint; leave the system green; stop at the task boundary. |
| 5 | `agent-delegation` | Orchestration | dispatching-parallel-agents, subagent-driven-development, handoff, claude-handoff, chief-of-staff | Construct fresh-context briefs, keep the parent clean, hand off through artifacts, and gate merges with an independent reviewer. |
| 6 | `test-first-loop` | Testing | 3× TDD, verification-before-completion | Discover the repo's commands, agree seams, watch red for the right reason, minimal green, full suite, evidence before claiming done. |
| 7 | `debug-loop` | Testing | 3× debugging, verification-before-completion | Stop the line, build a tight red-capable loop, minimize, rank falsifiable hypotheses, instrument one variable, fix with regression test, escalate after three failures. |
| 8 | `review-loop` | Review | code-review-and-quality, code-review, requesting/receiving review, visual-pr | Two separated axes (standards, spec) plus five quality dimensions; severity labels; mutation probe; receive feedback with verification and pushback. |
| 9 | `deep-module-design` | Architecture | codebase-design, api-and-interface-design, code-simplification, domain-modeling, deprecation-and-migration | Design by depth/seam/leverage/locality; name domain concepts; simplify by deleting concepts; migrate with expand-contract. |
| 10 | `browser-verified-ui` | Frontend | frontend-ui-engineering, browser-testing-with-devtools, narrow-react-prop-types | Build accessible UI, then verify in a real browser; treat page output as untrusted; narrow types to live paths. |
| 11 | `ship-it` | Delivery + production | git-workflow, worktrees, finishing-a-branch, shipping-and-launch, ci-cd, security, performance, observability | Isolate in a worktree, run the quality gates, verify evidence, then staged rollout with monitoring and a rollback plan. |
| 12 | `visual-explainer` | Docs/visual | show-me, teach, writing-shape, documentation-and-adrs | Explain with the smallest diagram or artifact that carries the idea; teach from the reader's current model; record the decision. |
| 13 | `skill-forge` | Meta | writing-skills, writing-for-agents, context-engineering, improve-claude-md | Test a skill against a baseline failure, match the form to the failure, prune by context load, micro-test wording. |

Not proposed: routing skills (harness-specific), misc utilities (too narrow),
and standalone review/PR mechanics already covered inside `review-loop`.

---

## Pipeline-aligned selection (historical)

This section records the first five-stage selection. Later supporting skills were
added; the current set is in `analysis/synthesis.md` and `analysis/coverage.md`.

The target workflow was fixed, and each stage was launched as a local `/command`
or a GitHub workflow:

```
interview -> issue(s)
  -> openspec-explore (always) -> openspec-propose
  -> spec review (agent) -> human review
  -> vertical-slice TDD
  -> code review (agent) -> human review
```

That made the pipeline, not the category list, the unit of distillation. The
selected set was five stage skills. Reviewers are read-only; the owning stage may
rework findings agent-to-agent, but human approval and merge sign-off remain
fixed gates.

| Stage | Selected skill | Draws from | Why this boundary |
|---|---|---|---|
| 1 | `issue-interview` | interview-me, grilling, brainstorming | Produces issue artifacts, not a spec; the issue is the source of truth for later review. |
| 2 | `issue-to-openspec` | rpi, spec-driven-development, to-spec | Owns the explore-first rule and the propose handoff; OpenSpec owns artifact creation. |
| 3 | `spec-review` | doubt-driven-development, code-review axes, source-driven-development | Adversarial fresh-context review of artifacts against issue, source, specs, docs. |
| 4 | `vertical-slice-tdd` | incremental-implementation, 3x TDD, verification-before-completion | Owns slicing, test-first, checkboxes, evidence, and design-drift pauses. |
| 5 | `code-review` | code-review-and-quality, two-axis review, requesting review | Separates spec, standards, and quality axes; read-only findings. |

Dropped or absorbed:

- **`agent-delegation`** — dispatch is owned by `/commands` and repo workflows,
  so the mechanics belong there, not in a stage skill.
- **`visual-explainer`** — wanted as a callable `/command` when needed, not a
  pipeline stage. Its visual-first principle is kept as an output preference in
  `spec-review` and `code-review`.
- **`deep-module-design`**, **`ship-it`**, **`skill-forge`** — useful, but outside
  this pipeline. Architecture and production readiness survive as review axes.
