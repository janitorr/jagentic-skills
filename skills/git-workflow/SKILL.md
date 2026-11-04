---
name: git-workflow
description: Use before any git commit, push, branch, merge, rebase, or pull request; when writing, reviewing, or choosing a commit message or convention; when isolating parallel work; when resolving conflicts or a rejected push; when inspecting or undoing history; or when preparing a version, tag, or release.
---

# Git Workflow

## Environment

The agent file defines the base branch, workspace isolation, push policy, and
review destination. Read it before starting. If an operation is not defined, ask;
do not assume a CLI or service.

## Overview

Git is the safety net. Keep the invariants below. The harness owns worktrees;
the agent file owns push and review policy.

## Invariants

- **One logical change per commit.** Stage only that slice, check the staged diff
  for secrets and unrelated edits, and leave generated and debug files out. An
  explicit "commit everything" does not merge unrelated slices: say what you are
  splitting and why.
- **Run the project's checks before committing.** A failing baseline makes every
  later failure ambiguous.
- **Conflicts keep both intents.** Read both sides, combine what each was trying
  to do, and run the checks on the merged tree. Never resolve by silently
  discarding one side.
- **A rejected push means the remote moved.** Fetch and integrate, then re-run
  the checks. Never force-push a shared branch.
- **Tags are immutable.** One annotated tag per release; never move, reuse, or
  force-push one.
- **Clean up only what you created.** Discard work only on an explicit request
  that names the branch; never infer consent from "sounds good".

## Defaults when the repo has none

- **Branch:** one short-lived branch per change from the repo's default branch,
  named `<area>/<short-slug>`.
- **Commit:**

  ```
  <area>: <imperative lowercase summary>

  <body explaining why, wrapped at 72 columns>
  ```

  `<area>` is the module or package, not a generic `feat` or `fix`.
- **Release:** classify against the public surface, record the classification in
  a commit footer (`BREAKING CHANGE:` or `!`), a changeset, or a label, and let a
  tool compute the version.

  | Change | Bump |
  |---|---|
  | Breaking public change | `MAJOR` |
  | Compatible feature | `MINOR` |
  | Compatible fix | `PATCH` |

  Use the repo's release tool first (changesets, semantic-release,
  release-please, goreleaser, cargo-release, `npm version`). Otherwise use a
  semver CLI or the project's semver library. Otherwise show the arithmetic for
  review. Before 1.0, a breaking change may ride `MINOR`; a hotfix is a `PATCH`
  on the release line.
- **Tag:** annotated `vMAJOR.MINOR.PATCH` on the release commit; prereleases
  append `-rc.N` or `-beta.N`. The tag is the source of truth; a manifest
  version must match it.
- **Changelog:** Keep a Changelog categories in order (Added, Changed,
  Deprecated, Removed, Fixed, Security). `documentation` owns the format.

## Verification

- [ ] Each commit is one logical change and excludes unrelated/generated files.
- [ ] The message follows the repo convention or the default shape.
- [ ] A conflict kept both intents and the checks pass on the merged tree.
- [ ] No shared branch was force-pushed; a rejected push was integrated.
- [ ] Version and tag came from the release tool or a semver CLI, and match the
      manifest and changelog.
- [ ] No tag was moved or reused.
- [ ] Cleanup touched only workspaces this work created.
