# ci-cd: trigger test

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **5/5 unambiguous fire, 5/5 no-fire**. The ambiguous production-rollback
prompt loads the global `shipping-and-launch`; a pipeline-specific rollback
prompt loads `ci-cd`.

## Method

The first run used the `general` agent, which inherited the repository as its
working directory. One selector explored the lab before loading the skill, so
those results were discarded.

The blind run used `trigger-selector`: only the `skill` tool is allowed;
filesystem, shell, web, and subagent access are denied. Fresh session per
prompt, read-only, full skill catalog.

## Should fire

| # | Prompt | Loaded | Result |
|---|---|---|---|
| 1 | Add a GitHub Actions pipeline that runs tests and deploys to staging. | `ci-cd` | hit |
| 2 | Review this `azure-pipelines.yml`; production deploys without an approval. | `ci-cd` | hit |
| 3 | Our CI takes 25 minutes and rebuilds the image for production; fix it. | `ci-cd` | hit |
| 4 | Add test-result publishing and a post-deploy health check to the pipeline. | `ci-cd` | hit |
| 5 | Add a manual rollback job to the GitHub Actions pipeline that redeploys a previous image digest. | `ci-cd` | hit |

## Adjacent, not a miss

`We need a rollback path for the production deployment` loaded
`shipping-and-launch`. That is a defensible adjacent match: the prompt names a
release strategy, not a pipeline. The pipeline-specific version above loads
`ci-cd`. No description change is needed; the test prompt was ambiguous.

## Should not fire

| # | Prompt | Loaded | Result |
|---|---|---|---|
| 1 | Write release notes for 1.4.0. | `documentation` | clean |
| 2 | Commit this fix as two slices. | `git-workflow-and-versioning` | clean |
| 3 | Add a failing test for the slugify bug. | `test-driven-development` | clean |
| 4 | Design the database schema for orders. | `api-and-interface-design` | clean |
| 5 | Update the README. | `documentation` | clean |

None loaded `ci-cd`.

## Note

The commit-slice prompt loaded the global `git-workflow-and-versioning`, not the
local `git-workflow`. That is a pre-existing local-versus-global boundary, not a
`ci-cd` routing failure. Record it separately if the local skill is expected to
win over the global.
