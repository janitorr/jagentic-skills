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

## Change

`skills/skill-forge/SKILL.md`, step 2:

> **Blind the run first.** An agent that notices it is being evaluated changes
> its behavior. Keep `eval`, `test`, `benchmark`, `control`, `treatment`,
> `baseline`, and `fixture` out of agent IDs, system prompts, workspace paths,
> and task text. Name the workspace like a real project and phrase the task like
> a real request. Do not leave sibling runs, scoring scripts, or an evidence
> directory in view. `/tmp/eval/run-2` is a tell; `/tmp/work/orders-api` is not.

Steps 5 and 6 point back to step 2 so the rule applies to trigger tests and
wording micro-tests as well.

## Evidence status

The confound is observed; its effect size is not measured. This is recorded as
debt, not as a verified behavior change. Close it on the next skill eval by
running the same authoring task once with `eval`/`control` names and once with
neutral names, and compare whether the agent writes the skill or stops.
