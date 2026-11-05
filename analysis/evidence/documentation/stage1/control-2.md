# AGENTS.md

OpenAgents Control (OAC) is an OpenCode-based agent framework: markdown agent
prompts, commands, and context under `.opencode/`, plus an evaluation harness in
`evals/`. Published as `@nextsystems/oac`; the `oac` CLI (`bin/oac.js`) wraps
`install.sh`. Agents are prompt files, not compiled code.

## Start here

| Work | Location |
|---|---|
| Agent behavior | `.opencode/agent/core/openagent.md`, `opencoder.md`, `.opencode/agent/meta/system-builder.md` |
| Subagents | `.opencode/agent/subagents/{code,core,planning,development,test,system-builder,utils}/` |
| Slash commands | `.opencode/command/` |
| Context and standards | `.opencode/context/`; repo-specific guidance in `.opencode/context/openagents-repo/` |
| Model-specific prompt variants | `.opencode/prompts/{category}/{agent}/` |
| Tests | `evals/agents/{category}/{agent}/tests/`; framework in `evals/framework/src/` |
| Registry and installer | `registry.json`, `install.sh`, `scripts/registry/` |
| Contributor docs | `docs/contributing/DEVELOPMENT.md`, `docs/contributing/CONTRIBUTING.md` |
| Claude Code plugin | `plugins/claude-code/` (separate from the OpenCode tree) |

OpenCode config is `.opencode/opencode.json`; agent and command files use YAML
frontmatter (`description` required; agents add `mode`, `model`, `tools`,
`permissions`).

## Commands

```bash
npm ci                                   # root deps (bun.lock also used by CI)
cd evals/framework && npm install        # eval framework deps
cd evals/framework && npm run build
cd evals/framework && npm run validate:suites:all
make test-smoke                          # 1 golden test (~30s)
make test-golden                         # all golden tests
cd evals/framework && npm run eval:sdk -- --agent=openagent --pattern="**/golden/*.yaml"
npm run validate:registry                # bun run scripts/registry/validate-registry.ts
npm run validate:context-links           # bun run scripts/validation/validate-markdown-links.ts
./scripts/registry/validate-component.sh  # frontmatter and structure
./scripts/prompts/validate-pr.sh         # agents must still use default prompts
./install.sh --list                      # profiles: essential, developer, business, advanced, full
./install.sh developer                   # local install
npm run version:bump:patch               # also :minor :major :alpha :beta :rc
```

Prerequisites: Node 18+, Bash 3.2+, OpenCode CLI for eval runs, Bun for the
registry and markdown-link validators.

## Conventions and boundaries

- `.opencode/agent/**` holds the canonical default prompts. Experiment in
  `.opencode/prompts/` instead; never let a prompt-variant PR change defaults.
  Run `./scripts/prompts/validate-pr.sh` before submitting prompt changes.
- Reference agents by category path and subagents by group:
  `core/openagent` (`opencoder.md`), `subagents/development/frontend-specialist`.
  Use kebab-case filenames, PascalCase TypeScript types, camelCase functions, and
  `set -e` in Bash scripts.
- `registry.json` is maintained by CI from `scripts/registry/auto-detect-components.sh`.
  Add the file and validate the component; do not hand-edit the registry as a shortcut.
- Bump versions with the scripts (updates `package.json` and `VERSION`) and update
  `CHANGELOG.md`; do not edit only one version file by hand.
- Context follows MVI: small single-topic files, lazy-loaded. Context links are
  CI-validated.
- PR titles must be Conventional Commits (`feat(scope): ...`, `fix: ...`,
  `docs: ...`, `[alpha] ...` for prereleases). Explain what, why, how, and testing.
- Generated or temporary: `evals/results/`, `.tmp/`, `dist/`, `node_modules/`.
  Do not edit results or session scratch files as source. Do not commit secrets;
  `env.example` documents optional environment variables.
