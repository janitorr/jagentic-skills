# documentation: exploratory format probe

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **exploratory**, n=1 per condition for the original probe, plus a
post-patch conformance retest at three repetitions per changed type. This is not
a behavioral verification: the retest has no control arm, so it shows that the
edited wording produces the intended shape, not that it beats a strong baseline.

## Question

Is `skills/documentation/SKILL.md` comprehensive across common document types,
and does loading it change the *shape* of what an agent produces?

## Method

- Eight artifact types, each run twice: treatment (read `SKILL.md`, treat it as
  the only guidance) and control (no files, no guidance).
- One fresh `general` subagent per cell, default model, single sample.
- Identical fictional brief per type. Subagents were told not to inspect the
  filesystem, so output reflects the brief plus guidance only.
- Subagents wrote the document to a file and returned only the artifact type and
  heading list. Shape was scored from the files, not the self-report.

Types: six the skill names or owns (ADR, README, API reference, changelog,
AGENTS.md, inline comment) and two it does not own (onboarding guide, runbook).

## Results

| Type | Treatment shape | Control shape | Attributable difference |
|---|---|---|---|
| ADR | Status, Date, Context, Decision, Alternatives considered, Consequences | Metadata block, Context, Decision, Consequences (alternatives inside Decision) | Yes, follows the skill template |
| README | Identity, Quick start, Commands, Configuration, Architecture, Contributing, License | Identity, Installation, Usage, Configuration, Development, License | Yes, skill order; control leads with the problem |
| API reference | Auth, Request body, Response, Errors, Example | Auth, Request body, Responses per status, Lifecycle, Error table | Minor; both complete |
| Changelog | Keep a Changelog headings | Keep a Changelog headings | **None**; outputs are near-identical |
| AGENTS.md | Map, Commands, Rules in `<important if>` blocks, Deployment | Layout, Commands, Rules as H3, Formatting, Deployment | Yes; conditionals used, tool-enforced rule dropped |
| Inline comment | Meta wrapper ("Audience and job", code, "Constraints the comments defend") | Heading, code only | Yes, and it is **wrong for the artifact** |
| Onboarding guide | Sections by job (what, repos, week, run, deploy, on-call, reading) | Day-by-day plan plus checklist | Improvised; no skill branch exists |
| Runbook | State table, triage, per-cause fixes, drain caveats, verification, "Confidence and open gaps" | At a glance, architecture, diagnosis, causes, drain, verification | Improvised; no skill branch exists |

Heading lists are reproduced in `documentation/headings.txt`.

## Findings

1. **Coverage gap: the artifact table is closed.** Step 2 offers six branches.
   Tutorial/how-to, runbook, postmortem, RFC/design doc, migration guide,
   release notes, and troubleshooting have no branch. An agent asked for one
   either mis-maps it or improvises. Both improvised outputs here were
   reasonable, but that is model prior, not skill guidance.
2. **Description promises an artifact the process does not own.** "Onboarding
   guide" is in the frontmatter and has no step. The agent built it from the
   audience table. Nothing states what onboarding must contain (access
   prerequisites, first task, escalation path, glossary), so coverage varies.
3. **Process leaks into the deliverable.** The inline-comment task produced a
   standalone document with "Audience and job" and a "Constraints the comments
   defend" table around the code. Step 1 says to identify the audience; the
   agent wrote that analysis into the artifact. The skill never says the
   audience/job decision is a planning step, or that it may be omitted.
4. **Changelog is a no-op.** Both conditions produced the same Keep a Changelog
   entry. The skill says only "`git-workflow` owns release timing" and defers
   format to repository convention. It contributes nothing when no convention
   exists.
5. **Where the skill did change shape, it was terse and concrete.** ADR
   template, README section order, and the AGENTS.md conditional form were all
   followed closely. These are the steps with an explicit recipe.
6. **Over-application is possible in AGENTS.md.** The treatment dropped the
   formatting rule (as instructed) and, with it, the "run from the repo root"
   and CI-gate details. The rule is defensible; losing useful operating context
   is a cost worth watching.

## Patch and retest, 2026-11-04

The skill was edited in five places:

- Step 1 marks audience/job as planning, not a default section.
- Step 2 adds RFC, release notes, and three procedural branches, with the rule
  that a document fitting no branch is two documents.
- Step 3 adds the RFC status and a changelog recipe.
- New step 5 gives the reference-page order and forbids inventing behavior.
- New step 6 gives the shared procedural spine plus per-type additions.
- Step 7 now limits inline output to one annotated stub.

Retest: three fresh runs per changed type, treatment only, same briefs.

| Type | Runs | Result |
|---|---|---|
| Inline comment | 6 total | Leak gone 3/3 after the step-1 change; 2/3 still added a heading or split the stub, so step 7 was tightened; after that, 3/3 returned a single bare stub |
| Onboarding guide | 3 | 3/3 led with access prerequisites, then repo map, first task, deployment risk, escalation |
| Runbook | 3 | 3/3 put prerequisites and diagnosis before any drain, one fix per cause, warnings beside destructive steps, verification and escalation |
| API reference | 3 | 3/3 used the prescribed order; all marked unspecified fields instead of inventing them |
| Changelog | 3 | 3/3 used the same category order and recorded Security as `None` |

Heading sequences for the retest are appended to `documentation/headings.txt`.

The retest shows the wording is followed. It does not show the skill is better
than no skill, because there is no control at n=3. The frontmatter description
changed after that retest; the trigger re-run is recorded in `trigger-tests.md`.

## Stage 1: AGENTS.md map probe, 2026-11-05

A real-repository test of the project-map practice suggested by the external
`context-engineering` evaluation. OpenAgentsControl has no root `AGENTS.md`,
so the artifact had to be created rather than copied.

Method: three control runs (explicitly told not to load a skill) and three
treatment runs (told to load `documentation`), same brief, same model. The
brief asked for a one-screen `AGENTS.md` covering identity, where to look
first, commands, and boundaries, with real paths and commands only. Control
loaded no skill 3/3; treatment loaded `documentation` 3/3. Artifacts are under
`documentation/stage1/`.

| Metric (median) | Control | `documentation` | Change |
|---|---:|---:|---:|
| Total tokens | 1,517,243 | 2,671,818 | +76% |
| Billable input+output | 96,315 | 101,639 | +6% |
| Tool calls | 58 | 57 | −2% |
| Wall time | 112.1 s | 161.9 s | +44% |
| Lines | 73 | 84 | +15% |
| Distinct files read | 20 | 8 | −60% |
| Key-pointer coverage | 8/10 | 9/10 | +1 |
| Map score (0-10) | 9.00 | 9.33 | +0.33 |

The map score is a five-dimension evaluator score (0-2 each): key-pointer
coverage, command accuracy, task-to-path table, repo-specific boundaries, and
concision. All six maps cited only existing paths and commands; the single
flagged `make validate-registry` string in `skill-1` is a deliberate warning
that the target does not exist. Every map used a work-to-path table.

The distinctive treatment behaviors were one `<important if>` block
(`skill-2`), one stale-doc warning (`skill-1`), and one read-first/edit-second
table (`skill-3`). The control maps were equally specific: `control-1` and
`control-3` included verified command lists, canonical-prompt rules, registry
tooling, Bash compatibility, and PR conventions.

**Finding: do not add a project-map recipe to `documentation` on this
evidence.** The current step 8 already elicits the practice ("keep project
identity, map, tech stack, and the command table bare"; "attach a completion
criterion"; "put the trigger in the pointer"). Quality was at parity and the
skill cost more. The external win came from **pre-loading** a map, not from
authoring one, so the missing piece is a workflow that ships and loads
`AGENTS.md`, not more text in the skill.

## Threats to validity

- n=1 per cell. Five reps are the project standard; one sample cannot separate
  wording effects from sampling noise.
- Briefs said "no existing docs", which removes the skill's main instruction
  ("match the repository's convention") and maximizes improvisation.
- Treatment subagents were told to use the skill, so this does not test
  triggering. Trigger behavior is covered separately in `trigger-tests.md`.
- One model, one agent configuration, fictional briefs. Real repositories
  supply conventions that may dominate the skill.

## Scope: one skill, not one per document type

Nine artifact branches live in one skill because they share the audience, reader,
pruning, and verification core; the per-artifact parts are shape recipes of 9 to
21 lines. Splitting would duplicate the core, add trigger boundaries, and add
skills with no behavioral evidence.

Split when a branch meets one of these:

- it needs its own verification, such as running commands or dry-running a
  runbook;
- it grows past about 30 lines, or the whole file past about 250 lines;
- loading the skill costs more than the branch saves.

If that happens, cut by reader job, not by artifact list: `documentation`
(README, changelog, comments, agent files), `decision-records` (ADR/RFC),
`procedures` (tutorial, how-to, runbook, onboarding).

## Next

- Trigger test re-run is recorded in
  `trigger-tests.md#re-run-after-the-documentation-description-edit`. The
  tutorial, runbook, migration-guide, and release-notes mappings all routed to
  `documentation` in the proxy and the live selector. RFC initially did not,
  because the body named it and the description did not; adding `RFC` to the
  description fixed it at 3/3 proxy and in the live selector.
- Run a controlled comparison for the procedural branch at five repetitions
  before claiming it beats a strong control.

## Reproduce

Verbatim briefs, shared by both conditions (treatment prepends "read
`skills/documentation/SKILL.md` and treat it as your only guidance"; control
prepends "do not read any files or guidance").

- **adr**: Write an architecture decision record for this project. Fernweh is a
  12-person Django 5 travel-planning app. Last month we replaced stateless JWT
  session tokens with server-side sessions stored in Redis, after two incidents
  where access tokens leaked through logs. We considered (a) short-lived JWTs
  with refresh-token rotation and (b) mTLS between browser and edge. We chose
  server-side sessions because logout must be immediate and we already run
  Redis. Cost: an extra Redis hop per request; consequences for the mobile
  client later. Decision made 2026-10-14 by the backend team.
- **readme**: Write the README for geoshard, a Python 3.12 CLI that splits large
  GeoJSON FeatureCollections into region-sized tiles for web map loading.
  Install with `pipx install geoshard`. Commands: `geoshard split input.geojson
  --regions regions.json --out tiles/`, `geoshard validate tiles/`, `geoshard
  merge tiles/ --out merged.geojson`. Config comes from `geoshard.toml` with
  keys `max_features`, `simplify_tolerance`, `crs`. MIT licensed, contributions
  via PRs, tests with `pytest`. No existing docs.
- **api**: Write the reference page for the HTTP endpoint `POST /v1/exports` in
  a REST API for a reporting product. Request body: `report_id` (string,
  required), `format` (enum csv|xlsx|pdf, default csv), `date_range` (object
  with `from`/`to` ISO-8601 dates, required), `filters` (array of objects,
  optional). Responses: 202 with `{export_id, status_url}`, 400
  `invalid_date_range`, 404 `report_not_found`, 409 `export_already_running`,
  429 with `Retry-After`. Auth is a bearer token with scope `exports:write`.
  Exports are async and expire after 7 days.
- **changelog**: Write the changelog entry for version 2.4.0 of `banksy`, a
  Python payments client library, released 2026-11-02. Added: an async client
  (`banksy.AsyncClient`) supporting all existing methods; `idempotency_key` on
  `Charge.create`. Changed: default retry count raised from 3 to 5 for 5xx
  responses. Deprecated: `fetch_sync`, to be removed in 3.0; replacement is
  `fetch`. Fixed: retries duplicated the request body when a 502 followed a
  timeout. Security: none. This project follows Keep a Changelog and SemVer.
  Previous version was 2.3.1.
- **agents**: Write the AGENTS.md for a TypeScript monorepo called dockyard.
  Layout: `apps/web` (Next.js 15), `apps/api` (Fastify), `packages/ui`,
  `packages/db` (Prisma). Package manager pnpm 9 with workspaces; tests use
  vitest, run with `pnpm test`; lint with `pnpm lint`; typecheck with `pnpm
  typecheck`. Rules that matter: never hand-edit files under
  `packages/db/migrations/` (generated by `pnpm db:migrate`); every API change
  needs an OpenAPI update in `apps/api/openapi.yaml`; do not add dependencies to
  the root package.json. Deployment is via GitHub Actions to Fly.io. Formatting
  is enforced by Prettier and ESLint, run in a pre-commit hook. New services
  follow the structure in `apps/api/src/modules/<name>`.
- **inline**: Write the inline documentation (docstring and comments) for this
  Python function, which is fictional. `ingest_batch(path, *, max_rows=10_000)`
  reads a newline-delimited JSON file, validates each record against a schema,
  and writes valid records to a Postgres table via COPY. Subtle constraint: the
  COPY buffer must be flushed before the function re-reads the file's offset,
  otherwise the checkpoint is written ahead of durable rows and a crash loses
  data. It retries 3 times on `psycopg.OperationalError` with 100ms/400ms/1600ms
  backoff, but never retries partial batches. It returns a tuple `(accepted,
  rejected)`. This is new code with no comments yet.
- **onboarding**: Write an onboarding guide for a new backend engineer joining
  the team that owns 'Atlas', an order-management service. The service spans 6
  repositories: atlas-api (Go), atlas-worker, atlas-schema, atlas-infra
  (Terraform), atlas-webhooks, atlas-docs. First week: get staging credentials
  from the platform team, run the local stack with `make up`, pair on one
  ticket, shadow the on-call rotation for two days, read the two ADRs about
  event ordering and idempotency. Staging deploys use `./scripts/deploy staging
  <service>`; production deploys require a second reviewer. On-call uses
  PagerDuty, runbooks in `atlas-docs/runbooks/`. There is no existing onboarding
  document.
- **runbook**: Write an operational runbook for this alert: 'Export queue lag
  exceeds 10 minutes'. The system is a Celery-based export pipeline:
  `export-scheduler` enqueues jobs to Redis, 8 `export-worker` pods consume
  them, results go to S3, clients poll `GET /v1/exports/<id>`. Known causes seen
  before: a poison job that crashes workers on retry, S3 throttling in
  eu-west-1, and a scheduler bug that enqueues duplicates after a Redis
  failover. Steps the team uses: check `celery -A export inspect active` and the
  Grafana dashboard 'Exports / Queue Depth', drain with `kubectl scale
  deploy/export-worker --replicas=0` then back to 8, find poison jobs with
  `redis-cli lrange export_queue 0 50`, and escalate to #team-data-platform.
  There is no existing runbook.

## Human-facing visual guidance probe

Status: **exploratory shape probe, n=1 per prompt**. This is not a behavioral
verification: there is no control and one sample per prompt. It checks that the
new human-versus-agent visual guidance changes the output shape.

### Method

One disposable copy of the `spec-review` clean fixture per prompt, global skills
removed, `deepseek-v4.1-flash` (`opencode-go`, default variant), 150s cap,
`documentation` loaded from the project mirror. The agent wrote `README.md` or
edited `AGENTS.md`; shape was scored from the write/edit content in the session
event stream, not from the reply.

### Results

| Prompt | Skills loaded | Output | Visual |
|---|---|---|---|
| Write the README architecture overview for this project. | `documentation`, `visual-explainer` | 5,338-char `README.md` | file tree (`├── src/...`) and a Mermaid `sequenceDiagram`; one sentence beside each |
| Write the README section describing the search feature. | `documentation` | 1,436-char `README.md` | prose; no visual, as expected for a feature section |
| Update this repo's AGENTS.md | none | 1,565-char `AGENTS.md` | text plus the command table; no diagram |

The first guidance was conditional ("when the shape is the point"). It produced
no visual for the feature-section prompt and was not run on the
architecture-overview prompt. The positive recipe — the architecture overview
gets a file tree and a sequence diagram by default — produced both visuals. The
feature section staying prose is the intended scope, not a miss. The `AGENTS.md`
run did not load `documentation`, so it does not test the new text-first rule;
the output was text-first anyway.

### Limits

- n=1 per prompt, no control, one model, one project.
- The `AGENTS.md` text-first rule is not tested with the skill loaded.
- The README test asked for an architecture overview; it does not show that a
  generic document request will add visuals.
