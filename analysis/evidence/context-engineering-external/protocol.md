# Protocol: context-engineering external evaluation

This file records the exact conditions, prompts, and pre-loaded maps used for
`context-engineering-external.md`. All runs were read-only; the agent was told
not to edit, create, or delete any file.

## Common preamble

```
You are working in the repository at /tmp/opencode/eval/<repo>. This is a
read-only exploration task: do not edit, create, or delete any file.
```

The documentation/spec runs replaced "exploration task" with "documentation and
spec review".

## Conditions

**control.** The common preamble followed by the task.

**skill.** The common preamble, the task, then:

```
Before starting the task, load the `context-engineering` skill with the skill
tool and apply its guidance while you work.
```

**primed.** The common preamble, then `PROJECT MAP (pre-loaded context)` with
the map below, then the task. No skill text and no instruction to load a skill.

## Tasks

### Nagger, code

```
TASK: Trace how an existing one-shot task is marked complete, from the HTTP API
(not the MCP endpoint) through to the SQLite write. Name the endpoint mapping
file and route, the Core command type and handler method, the store port and
its Host adapter, and the domain type. Cite file paths and line numbers where
you can.

Answer in at most 250 words. End with a short "Files" list.
```

### Nagger, documentation/spec

```
TASK: Read openspec/specs/morning-task-report/spec.md and the morning-report
section of USAGE.md. Summarize the documented rules for (a) timezone and
requested-date interpretation, (b) the seven-day visibility window, (c) item
ordering, and (d) read-only behavior. Then verify each rule against the
implementation under src/. Report any mismatch between spec, user docs, and
code with exact file:line citations.

Answer in at most 300 words. End with a short "Files" list.
```

### Mittens, code

```
TASK: Trace a `mittens_set` MCP call from the tool surface to the SQLite write.
Name the MCP tool class and method, the Core command and handler, the writer
and the SQL it executes, and the table. Then list the files that must change to
add a nullable `Tags` string field end-to-end (domain model, persistence,
API/MCP contract, compiled EF model, and tests). Cite file paths.

Answer in at most 300 words. End with a short "Files" list.
```

### Mittens, documentation/spec

```
TASK: Read openspec/specs/persistence/spec.md,
openspec/specs/memory-fact-store/spec.md, openspec/specs/rest-api/spec.md, and
setup/SETUP.md. Summarize the documented rules for table naming, conflict
resolution, secret detection, and the AOT data-access approach. Then verify each
rule against the implementation under src/. Report any stale or contradicted
claim with exact file:line citations.

Answer in at most 300 words. End with a short "Files" list.
```

### OpenAgentsControl, code

```
TASK: Explain how an agent definition is discovered, installed, and loaded in
this repository: where agent markdown lives, how registry.json describes an
agent, which installer or validation scripts consume it, and exactly which
files must be updated when adding a new agent. Cite file paths.

Answer in at most 300 words. End with a short "Files" list.
```

### OpenAgentsControl, documentation/spec

```
TASK: Read CONTEXT_SYSTEM_GUIDE.md and the registry/installer documentation
under docs/. Explain the documented process for adding a new context/standard
file so the installer ships it. Verify that process against registry.json and
install.sh. Report gaps between what the docs say and what is machine-enforced,
with exact file:line citations.

Answer in at most 300 words. End with a short "Files" list.
```

## Pre-loaded maps

### Nagger, code

```
PROJECT MAP (pre-loaded context)
- Nagger: .NET 10 task-memory service. Core behavior in src/Nagger.Core;
  HTTP/SQLite adapter and composition root in src/Nagger.Host.
- Core vertical slices: src/Nagger.Core/Tasks/*.cs (for example
  ManageOneShotTaskLifecycle.cs), domain types in Tasks/Domain/.
- Host HTTP endpoints: src/Nagger.Host/Api/*Endpoints.cs; MCP tools:
  src/Nagger.Host/Mcp/McpTaskTools.cs.
- Persistence: src/Nagger.Host/Infrastructure/ (SqliteTaskStore.cs,
  NaggerDbContext.cs, Migrations/).
- Contracts: openspec/specs/. API behavior: USAGE.md. Tests:
  tests/Nagger.Core.Tests, tests/Nagger.Host.Tests.
- Commands: dotnet build Nagger.slnx; dotnet test Nagger.slnx.
```

### Nagger, documentation/spec

```
PROJECT MAP (pre-loaded context)
- Specs: openspec/specs/<capability>/spec.md; the morning report capability is
  openspec/specs/morning-task-report/spec.md.
- User-facing behavior: USAGE.md; repository instructions: AGENTS.md.
- Implementation: src/Nagger.Core/Tasks/MorningReport.cs; HTTP surface:
  src/Nagger.Host/Api/ReportEndpoints.cs; time via TimeProvider.
- Tests: tests/Nagger.Core.Tests, tests/Nagger.Host.Tests.
```

### Mittens, code

```
PROJECT MAP (pre-loaded context)
- Mittens: .NET 10 agent memory server (REST + MCP), SQLite via EF Core, CQRS
  via Mediator.
- Core: src/Mittens.Core/Fact/ (Fact.cs, FactValidator.cs, IFactWriter.cs,
  IFactReader.cs, Commands/, Queries/).
- Host: src/Mittens.Host/Memory/Endpoints/ (FactMcpTools.cs, FactEndpoints.cs),
  Memory/Data/ (FactWriter.cs, FactReader.cs, FactSql.cs, AppDbContext.cs,
  Compiled/).
- Serialization: src/Mittens.Host/Serialization/ (DTOs and source-generated
  JSON context).
- Table: mittens.MittensFacts. No EF migrations; inline DDL at startup. AOT:
  raw SqliteCommand, never FromSqlRaw.
- Tests: tests/Mittens.Tests.Unit, tests/Mittens.Tests.Integration.
```

### Mittens, documentation/spec

```
PROJECT MAP (pre-loaded context)
- Specs: openspec/specs/{persistence,memory-fact-store,rest-api,mcp-server}/spec.md.
- Setup/user docs: setup/SETUP.md, setup/AGENTS.template.md; repository
  instructions: AGENTS.md.
- Implementation: src/Mittens.Core/Fact/ (Fact.cs, FactValidator.cs, Commands/);
  src/Mittens.Host/Memory/Data/ (FactWriter.cs, FactReader.cs, FactSql.cs);
  startup DDL in src/Mittens.Host/Program.cs.
- Tests: tests/Mittens.Tests.Unit, tests/Mittens.Tests.Integration.
```

### OpenAgentsControl, code

```
PROJECT MAP (pre-loaded context)
- OpenAgentsControl: an OpenCode extension distributed by an installer
  (install.sh/update.sh) from registry.json.
- Agent definitions: .opencode/agent/<category>/<name>.md, plus a
  0-category.json per category directory.
- Registry: registry.json (components.agents, components.commands, profiles).
- Installer/validation: install.sh, update.sh, scripts/validate-registry.sh,
  scripts/registry/validate-registry.ts.
- Profiles: .opencode/profiles/{essential,developer,business,full,advanced}.
- Context system: CONTEXT_SYSTEM_GUIDE.md, context-findings/.
- Tests/CI: scripts/tests/, .github/workflows/installer-checks.yml.
```

### OpenAgentsControl, documentation/spec

```
PROJECT MAP (pre-loaded context)
- Context docs: CONTEXT_SYSTEM_GUIDE.md, .opencode/context/**, docs/contributing/,
  docs/maintenance/.
- Registry: registry.json (components.contexts).
- Installer: install.sh, update.sh; validation: scripts/registry/.
- Agent definitions: .opencode/agent/**; metadata:
  .opencode/config/agent-metadata.json.
```

## Run controls

- Model: `deepseek-v4.1-flash`, provider `opencode-go`, default variant, for
  all conditions.
- Three repetitions per cell; 54 runs total.
- Repos cloned read-only under `/tmp/opencode/eval/` at their default branches.
- The skill was loaded with the `skill` tool, not pasted into the prompt, in
  all 18 skill runs.
- Every tool input was checked for the three clone paths; no run crossed repos.
