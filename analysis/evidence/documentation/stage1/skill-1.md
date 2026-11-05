# AGENTS.md

OpenAgents Control (OAC) is an OpenCode agent framework: plan-first, approval-gated
markdown agents plus subagents, slash commands, skills, and just-in-time context files,
installed into a user's `.opencode/` directory. The npm package `@nextsystems/oac`
(CLI `oac`, version in `VERSION` and `package.json`) ships those components and the
installer; this repo adds the component registry and a YAML-driven eval harness. Agent
behavior lives in Markdown with no build step; the eval harness and compatibility
packages are TypeScript.

## Where to look first

| Work | Start at |
|---|---|
| Orient in this repo | `.opencode/context/openagents-repo/quick-start.md`, then `navigation.md` |
| Agent behavior | `.opencode/agent/<category>/` (`core`, `content`, `data`, `meta`); subagents in `.opencode/agent/subagents/` |
| Agent frontmatter | `.opencode/context/openagents-repo/standards/agent-frontmatter.md` |
| Slash commands | `.opencode/command/` |
| Skills | `.opencode/skills/<skill>/SKILL.md` |
| Runtime context | `.opencode/context/` |
| Agent tests | `evals/agents/<category>/<agent>/tests/` and `config/config.yaml` |
| Eval engine / evaluators | `evals/framework/src/`; `docs/contributing/ADDING_EVALUATOR.md` |
| Installer and upgrade | `install.sh`, `update.sh`, `bin/oac.js` |
| Component catalog | `registry.json` (tool-maintained) |
| Contributor guides | `docs/contributing/DEVELOPMENT.md`, `CONTRIBUTING.md` |

## Commands

Requires Node 18+ and Bun.

```bash
# One-time setup
bun install --frozen-lockfile
(cd evals/framework && npm ci)

# Component checks (repo root)
bun run validate:registry
bun run validate:context-links
./scripts/prompts/validate-pr.sh
./scripts/registry/auto-detect-components.sh --dry-run   # --auto-add to write
./install.sh --list

# Evals (from evals/framework/)
npm run build
npm run validate:suites:all
npm run eval:sdk -- --agent=openagent --pattern="**/golden/*.yaml"
npm test
```

Older docs may mention `make validate-registry`; that target does not exist — use the
`bun run` commands above.

## Boundaries

- **Agent files are the canonical prompts.** Model-specific experiments belong in
  `.opencode/prompts/<category>/<agent>/`; do not switch `.opencode/agent/**` to a
  variant in a PR. `scripts/prompts/validate-pr.sh` enforces this.
- **Frontmatter must be valid OpenCode fields only.** Put extra metadata in
  `.opencode/config/agent-metadata.json`; follow `standards/agent-frontmatter.md` before
  editing any agent.
- **`registry.json` is maintained by tooling.** Do not hand-edit it; run
  `./scripts/registry/auto-detect-components.sh --auto-add` and validate.
- **New agents need tests.** Add YAML tests and `config/config.yaml` under
  `evals/agents/<category>/<agent>/`; CI validates suites on eval changes but does not
  run full agent evals on PRs.
- **`docs/` is for humans; `.opencode/context/` is loaded by agents at runtime.** Put
  behavioral instructions in context files, not only in `docs/`.
- **PR titles must be conventional commits** (`feat(scope): ...`, `fix(scope): ...`),
  enforced by `.github/workflows/pr-checks.yml`.
- **`packages/compatibility-layer` and `packages/plugin-abilities` are independent
  TypeScript packages** with their own manifests and tests; run checks in each directory.

Done means the validators above pass and the eval suite matching the change passes.
