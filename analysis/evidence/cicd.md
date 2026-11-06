# CI/CD pipelines: baseline and narrow skill

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **clean phase complete**. Three controls scored 26, 26, 28 of 32;
three `ci-cd`-loaded runs scored 31, 31, 31. The skill closes the pinning and
test-evidence gaps. Post-deploy health checks did not reproduce as a gap, and
Azure caching regressed in the treatment runs.

## Question

Can a capable agent produce a good GitHub Actions and Azure Pipelines setup
without a CI/CD skill, and does a narrow skill close the recurring gaps?

## Fixture

`cicd/fixtures/service` is a FastAPI + uvicorn service on Python 3.12 with a
Postgres integration test, a `Dockerfile`, `ruff`, `mypy`, and `pytest`.
`docs/DEPLOY.md` names ACR `ordersacr.azurecr.io`, App Services
`orders-api-staging` and `orders-api-prod`, OIDC for GitHub, and the
`orders-azure` service connection for Azure DevOps.

The prompt asked for PR validation and a main build; one image built once and
promoted to staging, then production after approval; no long-lived cloud
credentials; PR feedback under 10 minutes; a rollback path; and both platforms.
It did not mention documentation, research, or the rubric.

## Method

Six fresh sessions, one random root each (`/tmp/opencode/orders.XXXXXX`), with
an explicit no-read rule outside the project. Control used `pipeline-author`
(no skills). Treatment used `platform-engineer` with only the `ci-cd` skill
available and explicitly loaded. No doc cue, no sibling runs.

`actionlint` passed 3/3. Azure schema passed 5/6; the exception is
`timeoutInMinutes` typed as a number while the VS Code schema expects a string,
which the official YAML reference documents as a number. Scored manually from
disk with `analysis/evidence/cicd/score.py`.

The earlier cued and cross-run pilot was discarded. See
`skill-forge-blinding.md`.

## Sources

- GitHub secure use:
  https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- GitHub OIDC in Azure:
  https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure
- GitHub concurrency:
  https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs
- GitHub dependency caching:
  https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/caching-dependencies-to-speed-up-workflows
- Azure Pipelines security:
  https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview?view=azure-devops
- Azure deployment jobs:
  https://learn.microsoft.com/en-us/azure/devops/pipelines/process/deployment-jobs?view=azure-devops
- Azure approvals and checks:
  https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops

## Rubric

2 = implemented as the docs describe; 1 = partial; 0 = absent.

| # | Criterion | Control A | Control B | Control C | Skill A | Skill B | Skill C |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | PR and main triggers; manual rollback | 2 | 2 | 2 | 2 | 2 | 2 |
| 2 | Least-privilege `GITHUB_TOKEN` | 2 | 2 | 2 | 2 | 2 | 2 |
| 3 | OIDC / workload identity | 2 | 2 | 2 | 2 | 2 | 2 |
| 4 | Third-party actions SHA-pinned | 1 | 1 | 1 | 2 | 2 | 2 |
| 5 | Dependency caching on both platforms | 1 | 1 | 2 | 1 | 1 | 1 |
| 6 | Lint, type check, tests, container build | 2 | 2 | 2 | 2 | 2 | 2 |
| 7 | Build once; promote one image | 2 | 2 | 2 | 2 | 2 | 2 |
| 8 | Staging automatic; production approved | 2 | 2 | 2 | 2 | 2 | 2 |
| 9 | Explicit rollback | 2 | 2 | 2 | 2 | 2 | 2 |
| 10 | Concurrency / cancel superseded runs | 1 | 1 | 2 | 2 | 2 | 2 |
| 11 | Job and step timeouts | 2 | 2 | 2 | 2 | 2 | 2 |
| 12 | Publish test results and coverage | 0 | 0 | 0 | 2 | 2 | 2 |
| 13 | Post-deploy health check | 2 | 2 | 2 | 2 | 2 | 2 |
| 14 | No untrusted event data in `run:` | 2 | 2 | 2 | 2 | 2 | 2 |
| 15 | Operational prerequisites in the repo | 1 | 1 | 2 | 2 | 2 | 2 |
| 16 | Cross-platform parity | 2 | 2 | 2 | 2 | 2 | 2 |
| | **Total /32** | **26** | **26** | **28** | **31** | **31** | **31** |

## What changed

- **Pinning: 0/3 → 3/3.** All controls used moving tags (`actions/checkout@v4`,
  `azure/login@v2`). All treatment runs pinned every third-party action to a
  full commit SHA.
- **Test evidence: 0/3 → 3/3.** No control uploaded JUnit, coverage, or any
  artifact. Every treatment run published test results and coverage on failure.
- **Concurrency: 1/3 → 3/3** and **operational docs: 2/3 → 3/3.** Smaller but
  consistent gains.
- **Health checks did not reproduce as a gap.** All three clean controls added
  a health check on their own; the earlier 1/3 result did not hold.
- **Azure caching regressed.** Only control C used `Cache@2`; no treatment run
  did. The `ci-cd` skill does not mention caching, so this is a gap in the
  skill, not a control/treatment effect.

## Cost

| Run | Tokens | Wall | Tools |
|---|---:|---:|---:|
| Control A | 1.21M | 517s | 56 |
| Control B | 3.72M | 925s | 47 |
| Control C | 8.94M | 1158s | 91 |
| Skill A | 3.29M | 748s | 47 |
| Skill B | 6.20M | 1091s | 80 |
| Skill C | 2.73M | 914s | 53 |

Variance dominates. The skill is not a clear token or latency penalty, and it is
not a saving either. Do not use cost as the deciding signal.

## Decision

Keep the skill, but revise it before calling it verified:

1. Add the missing caching line: `cache: pip` on GitHub and `Cache@2` on Azure.
2. Re-run three treatment sessions on the same fixture to confirm the caching
   line closes the regression without losing pinning or test evidence.
3. Run the trigger test in `cicd-triggers.md`.
4. Then update the README, synthesis, and coverage counts from ten skills to
   eleven.

Do not deploy the current version as final: it earns its keep on pinning and
test evidence, but it leaves Azure caching worse than the clean control.
