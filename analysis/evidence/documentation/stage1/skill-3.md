# AGENTS.md

OpenAgents Control (OAC) is an AI agent framework for OpenCode: Markdown/YAML
agents, commands, and context installed by `install.sh` from `registry.json`,
plus an evaluation harness and a Claude Code plugin. There is no root
application to build; TypeScript lives in the eval framework, plugins, and
`packages/`.

## Find your way

| Work | Read first | Edit |
|---|---|---|
| Agents, subagents, commands, skills | `.opencode/context/openagents-repo/navigation.md` (see `guides/adding-agent-basics.md`), then `standards/agent-frontmatter.md` | `.opencode/agent/`, `.opencode/command/`, `.opencode/skills/` |
| Context files | `.opencode/context/core/context-system/navigation.md` | `.opencode/context/` |
| Evaluations | `evals/README.md`, `evals/CREATING_TESTS.md`, `docs/contributing/ADDING_EVALUATOR.md` | `evals/framework/src/`, `evals/agents/` |
| Registry and installer | `scripts/registry/README.md`, `docs/contributing/CONTRIBUTING.md` | `registry.json`, `scripts/registry/`, `install.sh`, `update.sh` |
| Claude Code plugin | `plugins/claude-code/README.md` | `plugins/claude-code/` |
| TypeScript packages | `packages/*/README.md` | `packages/compatibility-layer/`, `packages/plugin-abilities/` |
| User and contributor docs | `docs/README.md` | `docs/` |

Longer guides: `docs/contributing/DEVELOPMENT.md`. When prose and tooling
disagree, trust `package.json`, `Makefile`, and the CI workflows.

## Commands

Requires Node 18+, Bash 3.2+, and Bun for the TypeScript validators.

| Task | Command |
|---|---|
| Install eval deps | `npm run dev:setup` |
| Install root deps (validators) | `npm install` |
| Validate registry | `npm run validate:registry` |
| Validate context links | `npm run validate:context-links` |
| Validate prompt layout | `./scripts/prompts/validate-pr.sh` |
| Validate component structure | `./scripts/registry/validate-component.sh` |
| Build eval framework | `npm run dev:build` |
| Validate test suites | `make validate-evals` |
| Run golden evals | `make test-golden` |
| Run one subagent | `make test-subagent SUBAGENT=coder-agent` |
| Show latest eval results | `make show-results` |
| List installable components | `./install.sh --list` |
| Bump version | `./scripts/versioning/bump-version.sh patch` |

Golden evals call a real model and need OpenCode CLI credentials; CI does not run
them on PRs. The runner itself is
`cd evals/framework && npm run eval:sdk -- --agent=openagent --pattern="**/golden/*.yaml"`.

## Conventions and boundaries

- `.opencode/` is the installable source. Installed copies elsewhere are
  generated; edit here, then validate.
- Agent frontmatter uses only OpenCode fields (`name`, `description`, `mode`,
  `temperature`, `model`, `tools`, `permission`, `skills`). Use `permission`
  (singular). Keep `id`, `category`, `tags`, and `dependencies` in
  `.opencode/config/agent-metadata.json`. Older examples that put that metadata
  in frontmatter are stale; `.../standards/agent-frontmatter.md` is authoritative.
- `.opencode/agent/**` files are the canonical prompts. Model experiments belong
  in `.opencode/prompts/<category>/<agent>/`; `default.md` files are rejected by
  `./scripts/prompts/validate-pr.sh`.
- Do not hand-edit `registry.json`. Run
  `./scripts/registry/auto-detect-components.sh --auto-add`, then
  `npm run validate:registry`. CI also adds new components
  (`.github/workflows/validate-registry.yml`).
- Context files start with the HTML comment header specified in
  `.opencode/context/core/context-system/standards/frontmatter.md`, stay under
  ~200 lines per `.opencode/context/core/context-system.md`, and are linked from
  `navigation.md` files.
- Evals may create files only in `evals/test_tmp/` or `.tmp/`; `evals/results/`
  and runtime `.tmp/` content are gitignored. Shared tests in
  `evals/agents/shared/tests/` run for every agent.
- Test the installer in a temp directory:
  `./install.sh developer --install-dir /tmp/oac-install`. The default target is
  `.opencode/` in the current directory.
- Copy `env.example` to `.env` for local secrets; `.env` is ignored.
- PR titles follow Conventional Commits (`<type>(<scope>): <description>`);
  `.github/workflows/pr-checks.yml` enforces it.
- `plugins/claude-code/context` is a symlink to `.opencode/context`; edit the
  real files. The plugin's `agents/`, `skills/`, and `commands/` are separate
  copies, so update them too when you intentionally change shared behavior.

A change is done when `npm run validate:registry`, `npm run validate:context-links`,
`./scripts/prompts/validate-pr.sh`, `npm run dev:build`, and the relevant eval
pattern pass.
