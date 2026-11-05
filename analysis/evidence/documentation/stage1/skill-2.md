# AGENTS.md

OpenAgents Control (OAC) is a plan-first, approval-gated AI agent framework built
on OpenCode. It ships markdown agents, commands, skills, and context; an eval
framework for testing agent behavior; a component registry; and an installer.
The npm package is `@nextsystems/oac`.

Start with `.opencode/context/openagents-repo/quick-start.md` and
`.opencode/context/openagents-repo/navigation.md`. Contribution rules are in
`docs/contributing/CONTRIBUTING.md`; the longer guide is
`docs/contributing/DEVELOPMENT.md`.

## Where to look first

Paths such as `guides/...` and `standards/...` below are under
`.opencode/context/openagents-repo/`.

| Work | Start here |
|---|---|
| Change a core agent | `.opencode/agent/core/openagent.md`, `opencoder.md`; read `.opencode/context/openagents-repo/standards/agent-frontmatter.md` |
| Add an agent | `.opencode/agent/<category>/`; `guides/adding-agent-basics.md`; tests under `evals/agents/<category>/<agent>/` |
| Add or change a subagent | `.opencode/agent/subagents/<group>/`; `standards/subagent-structure.md`, `guides/creating-subagents.md` |
| Add a command or skill | `.opencode/command/*.md`; `.opencode/skills/<name>/SKILL.md`; `guides/creating-skills.md` |
| Change context or standards | `.opencode/context/`; repo-specific pages in `.opencode/context/openagents-repo/`; project patterns in `.opencode/context/project-intelligence/` |
| Change eval behavior or tests | `evals/agents/<category>/<agent>/tests/*.yaml`; framework source in `evals/framework/src/`; see `evals/framework/README.md`; new evaluators: `docs/contributing/ADDING_EVALUATOR.md` |
| Change registry or installer | `registry.json`, `install.sh`, `scripts/registry/`; see `core-concepts/registry.md`, `guides/updating-registry.md` |
| Work on a package | `packages/compatibility-layer/README.md` or `packages/plugin-abilities/README.md` |
| Work on the Claude Code plugin | `plugins/claude-code/README.md` |

`packages/*` are standalone packages with their own lockfiles and build/test
commands; the root workspace only includes `evals/framework`.

## Commands

Prerequisites: OpenCode CLI, Node 18+, npm, Git, Bash 3.2+, jq, and make.

```bash
# Eval framework setup
cd evals/framework && npm install && npm run build

# Validation (run from repo root)
./scripts/registry/validate-component.sh
./scripts/registry/validate-registry.sh
./scripts/prompts/validate-pr.sh              # when agents or prompts change
cd evals/framework && npm run validate:suites:all

# Evals (from repo root unless noted)
npm run test:openagent:core                   # OpenAgent core suite
npm run test:ci                               # fast CI evals
make test-golden                              # shared golden tests
cd evals/framework && npm run eval:sdk -- --agent=opencoder
cd evals/framework && npm run eval:sdk -- --subagent=coder-agent
cd evals/framework && npm test                # framework unit tests

# Registry and installer
./scripts/registry/auto-detect-components.sh --auto-add
./install.sh --list
bash scripts/tests/test-compatibility.sh
bash scripts/tests/test-non-interactive.sh

# Version bump
./scripts/versioning/bump-version.sh patch
```

## Conventions and boundaries

- Agent and command markdown uses YAML frontmatter. Agent frontmatter accepts
  only OpenCode keys (`name`, `description`, `mode`, `temperature`, `model`,
  `maxSteps`, `disable`, `hidden`, `prompt`, `tools`, `permission`, `skills`).
  Put `id`, `category`, `tags`, and dependencies in
  `.opencode/config/agent-metadata.json`. File names are kebab-case.
- `.opencode/agent/**` holds the canonical agent prompts. Model-specific
  variants live in `.opencode/prompts/<category>/<agent>/`; do not replace the
  canonical prompt with a variant in a PR.
- `registry.json` is maintained by automation. Register new components with
  `./scripts/registry/auto-detect-components.sh --auto-add`; do not hand-edit it.
- Context files follow the MVI rule: keep them under 200 lines. Local
  `.opencode/context/` wins over `~/.config/opencode/context/`; project
  intelligence stays local.
- Eval results (`evals/results/`) and `.tmp/` are scratch and gitignored. Tests
  belong with their agent under `evals/agents/`.
- PR titles use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, ...).
  Describe what, why, how, and testing in the body. Squash merge drives version
  bumps.

<important if="you edit install.sh, update.sh, or scripts/tests/*.sh">
Keep Bash 3.2 compatibility. Run `bash -n install.sh`, `bash -n update.sh`, and
`bash scripts/tests/test-compatibility.sh`.
</important>

Update `docs/` and the relevant `.opencode/context/openagents-repo/` page when
behavior or component layout changes. A change is done when the validation
commands relevant to it pass and its PR title is conventional.
