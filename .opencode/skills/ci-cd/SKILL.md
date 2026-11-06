---
name: ci-cd
description: Design or review CI/CD pipelines for GitHub Actions and Azure Pipelines. Use when adding or changing build, test, or deployment pipelines; when a change must reach staging or production; or when a pipeline needs gated promotion, deployment verification, or rollback.
---

# CI/CD Pipelines

## Overview

A pipeline is a promotion machine: build one artifact, prove it, promote it,
verify it, and keep it reversible. The platform is syntax; the promotion model
is the design.

## When to Use

- Adding CI/CD to a service for the first time.
- Changing triggers, gates, deployment, or rollback.
- Reviewing a pipeline that runs but does not prove or verify enough.

Not for commit slicing (`git-workflow`), release notes (`documentation`), or
application tests (`vertical-slice-tdd`).

## Process

### 1. Shape the promotion

- PR: lint, type check, unit and integration tests, and a no-push container build.
- Main: build the image once, push it with an immutable tag, and record the digest.
- Staging deploys automatically from main. Production deploys the same digest
  after an environment approval.

Done when staging and production reference the same digest and no deploy job
rebuilds the image.

### 2. Secure the path

- GitHub: `permissions: contents: read`; add `id-token: write` only to deploy
  jobs; use `azure/login` with OIDC; pin every third-party action to a full
  commit SHA (or use a workflow lockfile).
- Azure: use a workload identity federation service connection; set
  `persistCredentials: false` on `AzureCLI@2`; keep secrets in variable groups
  or Key Vault, never YAML; use `parameters` for user input.
- Never interpolate `github.event.*` into `run:`; pass it through `env`.

Done when no client secret, registry password, or publish profile is in the
repo, and every `uses:` is SHA-pinned.

### 3. Publish evidence

- Upload JUnit results and coverage on every run, including failures
  (`if: always()` on GitHub; `condition: succeededOrFailed()` on Azure).
- Add `concurrency` with `cancel-in-progress` for PRs; Azure `pr.autoCancel`.
- Set a timeout on every job.

Done when a failed run still leaves a downloadable test report.

### 4. Verify the deployment

- After each deploy, poll the health endpoint until it returns 200 within a
  bounded window; fail on timeout.
- Rollback redeploys the previous digest through the same environment gate.
  Never use `:latest`.

Done when staging and production each have a health check and a rollback path.

### 5. Get the conditions right

Azure `condition:` is a runtime expression:

```yaml
condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
```

Use `${{ }}` for compile-time parameter expansion inside a value, not around the
whole condition. A stage that reads `condition: ${{ ... }}` is fragile.

Done when no stage or job condition is wrapped in `${{ }}`.

### 6. Record the prerequisites

Commit the one-time setup: OIDC subjects and RBAC for GitHub, the service
connection and approvals for Azure, required checks and branch policy, and the
rollback command. Done when a new maintainer can configure the environments
from the repo.

## Example: health check in an Azure deployment job

```yaml
- deployment: DeployStaging
  environment: staging
  strategy:
    runOnce:
      deploy:
        steps:
          - task: AzureWebAppContainer@1
            inputs:
              appName: orders-api-staging
              containers: $(registry)/$(image)@$(digest)
      postRouteTraffic:
        steps:
          - script: |
              for i in {1..30}; do
                curl -fsS https://orders-api-staging.azurewebsites.net/health && exit 0
                sleep 5
              done
              exit 1
```

## Verification

- [ ] One image built and promoted by digest; no rebuild per environment.
- [ ] Least privilege, OIDC, SHA-pinned actions, no secrets in YAML.
- [ ] JUnit and coverage published on pass and fail.
- [ ] Concurrency and timeouts set.
- [ ] Health check after every deploy.
- [ ] Rollback to a previous digest behind the same gate.
- [ ] Azure conditions use runtime syntax.
- [ ] Environment prerequisites committed.

## Reference

- GitHub secure use: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- Azure deployment jobs: https://learn.microsoft.com/en-us/azure/devops/pipelines/process/deployment-jobs?view=azure-devops
