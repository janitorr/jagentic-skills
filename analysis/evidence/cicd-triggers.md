# ci-cd: trigger test plan

Status: **pending**. Run after the three treatment runs on the `service` fixture
finish. This is the description test, not the body test.

## Method

Fresh agent per prompt, read-only. The agent sees the full skill catalog and is
told to load the matching skill and report its ID without doing the task. Record
the loaded ID and whether it matched.

## Should fire

1. Add a GitHub Actions pipeline that runs tests and deploys to staging.
2. Review this `azure-pipelines.yml`; production deploys without an approval.
3. Our CI takes 25 minutes and rebuilds the image for production; fix it.
4. Add test-result publishing and a post-deploy health check to the pipeline.
5. We need a rollback path for the production deployment.

## Should not fire

6. Write release notes for 1.4.0. -> `documentation`
7. Commit this fix as two slices. -> `git-workflow`
8. Add a failing test for the slugify bug. -> `vertical-slice-tdd`
9. Design the database schema for orders. -> `deep-module-design`
10. Update the README. -> `documentation`

## Pass condition

The five should-fire prompts load `ci-cd`; the five should-not-fire prompts load
the adjacent skill or nothing, never `ci-cd`. Read every result manually.
