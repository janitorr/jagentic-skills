# skill-forge: blinding the run

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **observed confound, not a controlled test**. `skill-forge` now tells the
author to blind baseline, trigger, and micro-test runs.

## What happened

The first CI/CD baseline used an agent named `eval-cicd`, a system prompt that
said "You are an evaluation control," and workspace paths under
`/tmp/opencode/cicd-eval/run-N`. The agents inspected the paths and treated the
setup as an evaluation before doing the task. Those runs were discarded.

The repeat used an agent named `pipeline-author`, a neutral system prompt, and
workspace paths under `/tmp/opencode/work/orders-api-N`. The three repeat runs
completed as normal engineering tasks.

That repeat still leaked: the runs sat in numbered sibling directories, and at
least one agent read another run's output. Those runs were discarded. The next
batch used one random root per run (`/tmp/opencode/orders.XXXXXX`) with an
explicit no-read rule outside the project.

The trigger test leaked too: the selector inherited the repository as its
working directory, and one run explored the lab before loading the skill. The
selector now gets only the `skill` tool, with filesystem and shell denied.

## Change

`skills/skill-forge/SKILL.md`, step 2:

> **Blind the run first.** An agent that notices it is being evaluated changes
> its behavior. Keep `eval`, `test`, `benchmark`, `control`, `treatment`,
> `baseline`, and `fixture` out of agent IDs, system prompts, workspace paths,
> and task text. Name the workspace like a real project and phrase the task like
> a real request. Do not leave sibling runs, scoring scripts, or an evidence
> directory in view. Give each sample its own random root, and tell the agent
> not to read or list anything outside its project; a numbered sibling is one
> `ls` away. `/tmp/eval/run-2` is a tell; `/tmp/work/orders-api` is not. Do not
> grant capabilities a real request would not grant: "you may consult the
> official docs" tells the agent to do research it should decide on itself. If
> research matters, let the skill carry the instruction.

Steps 5 and 6 point back to step 2 so the rule applies to trigger tests and
wording micro-tests as well.

## Evidence status

The confound is observed; its effect size is not measured. This is recorded as
debt, not as a verified behavior change. Close it on the next skill eval by
running the same authoring task once with `eval`/`control` names and once with
neutral names, and compare whether the agent writes the skill or stops.

## Trigger-test omissions (2026-11-07)

The clean trigger re-run exposed four omissions in step 5. The run is recorded in
`trigger-tests.md`; this note covers the rule change.

1. **The selector was still an eval.** The first clean attempt created a
   `trigger-selector` with only the `skill` tool, a system prompt saying "you
   select a skill... report the loaded skill ID," and task text "report the
   loaded skill ID only." That removes filesystem access but leaves a
   selection-only role and a restricted toolset, which are themselves tells.
2. **The workspace content leaked.** The disposable project was a copy of the
   `spec-review` clean fixture; its `package.json` still said
   `"name": "task-search-fixture"` and an OpenSpec task said "copy the fixture."
   Scrubbing the path is not enough.
3. **The first smoke run inherited the repository.** The subagent ran in the lab
   directory, read lab files, and loaded a global skill. The session store's
   `directory` field caught it; the prompt did not.
4. **Global skills masked local routing.** With global skills present, generic
   prompts loaded `interview-me` and `documentation-and-adrs`; removing them was
   necessary to test the local descriptions.

Change: step 2 now says to scrub workspace contents and verify the recorded
working directory; step 5 now separates a blind live run from a
descriptions-only proxy and forbids a selection-only selector.

Evidence status: the omissions are observed; the rewrite has no separate
micro-test. This is recorded as debt, not a verified behavior change. Close it by
running a trigger test from the new step 5 with a second agent and checking that
it does not build a `trigger-selector`.
