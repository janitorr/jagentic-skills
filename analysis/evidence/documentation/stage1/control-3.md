# AGENTS.md

OpenAgents Control (OAC) is an OpenCode extension for plan-first, approval-gated coding. It packages markdown-defined agents, commands, skills, and context (`.opencode/`), an installer and component registry (`install.sh`, `registry.json`), a TypeScript eval framework (`evals/`), and conversion/plugin packages (`packages/`). The npm package is `@nextsystems/oac`; the current version is in `VERSION` and `package.json` (0.7.1).

Start with `.opencode/context/openagents-repo/quick-start.md` for a two-minute orientation, then `docs/contributing/DEVELOPMENT.md` for workflows. User-facing docs live in `docs/`; agent-facing standards live in `.opencode/context/core/`.

## Where to look first

| Work | Start here |
|---|---|
| Change agent behavior | `.opencode/agent/core/openagent.md`, `.opencode/agent/core/opencoder.md`; category agents under `.opencode/agent/{content,data,meta}/` |
| Work on a subagent | `.opencode/agent/subagents/{core,code,planning,development,system-builder,test,utils}/` |
| Add an agent | `.opencode/context/openagents-repo/guides/adding-agent-basics.md` and `.opencode/command/openagents/new-agents/` |
| Add a model-specific prompt variant | `.opencode/prompts/<category>/<agent>/`; canonical defaults stay in `.opencode/agent/` |
| Add a command or skill | `.opencode/command/`; `.opencode/skills/<name>/SKILL.md` |
| Change standards/context | `.opencode/context/` (index: `.opencode/context/navigation.md`) |
| Write or fix evals | Framework: `evals/framework/src/`; suites: `evals/agents/{category}/{agent}/tests/`; golden: `evals/agents/shared/tests/golden/` |
| Registry or installer work | `registry.json`, `scripts/registry/`, `install.sh`, `update.sh`, profiles in `.opencode/profiles/` |
| Claude Code plugin | `plugins/claude-code/` |
| TypeScript packages | `packages/compatibility-layer/` and `packages/plugin-abilities/` (independent package.json files) |
| Docs and release history | `docs/`, `README.md`, `CONTEXT_SYSTEM_GUIDE.md`, `CHANGELOG.md`, `VERSION` |

## Commands

Prerequisites: OpenCode CLI, Node 18+, Git, Bash 3.2+. The installer also needs `jq`; registry and link validation use `bun`.

```bash
# Evals (run from evals/framework)
cd evals/framework && npm install
npm run eval:sdk -- --agent=openagent --pattern="**/golden/*.yaml"
npm test                         # framework unit tests (vitest)
npm run build
npm run validate:suites:all

# Root shortcuts
make test-golden                 # golden suite
make test-evals                  # build + validate suites + golden
make show-results                # summary of evals/results/latest.json

# Validation (from repo root)
npm run validate:registry        # Bun; or ./scripts/registry/validate-registry.sh
npm run validate:context-links   # Bun
./scripts/prompts/validate-pr.sh
./scripts/registry/auto-detect-components.sh --auto-add
./scripts/registry/validate-component.sh

# Installer
./install.sh --list
./install.sh developer --install-dir ~/.config/opencode
bash -n install.sh
bash scripts/tests/test-non-interactive.sh
bash scripts/tests/test-e2e-install.sh
bash scripts/tests/test-compatibility.sh

# Packages (each has its own package.json)
cd packages/compatibility-layer && npm test
cd packages/plugin-abilities && bun test

# Version bump (updates VERSION via npm scripts)
npm run version:bump:patch       # also minor, major, alpha, beta, rc
```

## Boundaries and conventions

- Markdown components need YAML frontmatter with a `description`. Use kebab-case filenames, PascalCase TypeScript types, camelCase variables.
- Context files follow the MVI limits: total file under 200 lines (concepts <100, guides <150, examples <80). Keep new context files small and update the relevant `navigation.md`.
- `.opencode/agent/**` holds the canonical defaults. Put model-specific experiments only in `.opencode/prompts/<category>/<agent>/`, test them, and document results. `scripts/prompts/validate-pr.sh` runs in CI and fails if canonical defaults were replaced.
- `registry.json` is maintained by tooling. After adding, moving, or deleting components run `./scripts/registry/auto-detect-components.sh --auto-add`; do not hand-edit it. CI updates it automatically for internal PRs, but fork PRs must commit the update themselves.
- `install.sh` and `update.sh` must stay compatible with Bash 3.2+ on Linux, macOS, and Git Bash, and must pass ShellCheck plus `bash -n`. Keep installer tests in `scripts/tests/` passing.
- PR titles must follow Conventional Commits: `<type>(<scope>): <summary>` with `feat`, `fix`, `docs`, `test`, `chore`, `ci`, `refactor`, `perf`, `build`, or `revert`; `!` marks a breaking change. Target `main` or `dev`.
- Full agent evals need the OpenCode CLI and a model. The `pr-checks` workflow (`.github/workflows/pr-checks.yml`) only builds the framework and validates suites; it does not run full agent evals. Run the relevant eval locally before claiming agent behavior changed.
- Keep `VERSION`, `package.json`, and `CHANGELOG.md` in sync. Treat `VERSION` as authoritative; the version block in `docs/README.md` can lag behind it.
