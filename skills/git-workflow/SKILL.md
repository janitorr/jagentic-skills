---
name: git-workflow
description: Use before any git commit, push, branch, merge, rebase, or pull request; when writing, reviewing, or choosing a commit message or convention; when isolating parallel work; when resolving conflicts or a rejected push; when inspecting or undoing history; or when preparing a version, tag, changelog, or release.
---

# Git Workflow

## Environment

The agent file defines the tracker, approval marker, review destination, and
workspace policy. It also defines the base branch, workspace isolation, and
whether to push or open a pull request. Read it before starting. If an operation
you need is not defined, ask; do not assume a specific CLI or service.

## Overview

Git is the safety net. Commits are save points, branches are sandboxes, and
history is documentation. The commit discipline matters more than the branching
model.

This skill owns commit mechanics (staging, message, hooks, pre-commit checks),
conflict resolution, branch finishing, and releases. Other skills point here
rather than restating them.

## Process

### 1. Detect the workspace

Before creating anything, check the workspace state. The harness or agent file
defines how to isolate a stream and whether to create a worktree; use that
mechanism, and ask before adding isolation the user did not request. If
isolation is blocked, work in place and say so.

### 2. Verify a clean baseline

Run the project's test suite before the first change. A failing baseline makes
every later failure ambiguous. Report failures and ask whether to proceed or
investigate.

### 3. Branch from the approved base

Create one short-lived branch per change, from the base the agent file or the
user defines. Use the repository's naming convention. Confirm the base before
merging; merging into the wrong base is expensive to undo.

Prefer feature flags over long-lived branches. Release branches are acceptable
when a release must stabilize while the main line moves.

### 4. Commit per slice

A commit is one logical change, made after its tests pass:

1. Stage only the files this slice changed. Never `git add -A` when unrelated
   work is present.
2. Read `git diff --staged`. Check for secrets and unrelated edits.
3. Run the focused tests, full suite, lint, and type check that the repo defines.
4. Read recent commits (`git log --oneline -20`) and match the repository's
   area or type, scopes, subject casing, and body style. If a documented
   convention exists, it wins; do not impose a generic one.
5. Write a message that explains **why**, not what the diff already shows. Match
   the convention you found, for example `feat:`, `fix:`, `refactor:`, `test:`,
   `docs:`, `chore:`, or a domain scope such as `host:`.
6. Commit without bypassing hooks. If a hook fails, fix the cause.

Keep standalone refactoring separate from feature work. Slice-local refactoring
that makes the next test cheaper may travel with the slice commit. Target roughly
100 changed lines per commit; split changes over about 1,000 lines. Commit each
green slice rather than accumulating a large uncommitted tree.

### 5. Work in parallel streams

Use the harness's isolation mechanism for independent streams so agents do not
switch branches under each other. Each stream gets its own branch and its own
baseline test run.

Clean up only the workspaces you created. If cleanup is refused because
uncommitted files exist, show the files and ask what to do; never force-remove on
your own initiative.

### 6. Handle conflicts and rejected pushes

Fetch and update from the base before integrating. Resolve conflicts by
understanding both sides, then re-run the tests. Never force-push a shared branch
without an explicit request. A rejected push means the remote moved; investigate
rather than forcing.

### 7. Finish the branch

1. Run the full suite on the tree you are about to integrate.
2. Detect the workspace state: normal checkout, named branch, or detached HEAD.
3. Present the integration choices: merge locally, push and open a pull request,
   or keep the branch as-is. Let the human choose. The agent file defines whether
   pushing or opening a pull request is allowed.
4. If merging, verify the merged result is green before deleting anything.
5. Keep the workspace while a pull request is under review.
6. Delete the branch and clean up the workspace only after a green merge, and
   only for workspaces you own.

Discard work only when the human explicitly asks. Ask them to type
`discard <branch-name>` exactly, and accept only that string; never infer consent
from "sounds good".

### 8. Record the change

Report files changed, files deliberately not touched, and any concerns. The
"did not touch" list proves scope discipline and catches wrong assumptions.

### 9. Version and release

For anything with consumers:

- Bump `MAJOR` for a breaking change, `MINOR` for compatible functionality, and
  `PATCH` for a compatible fix.
- Tag the release and let the tag be the source of truth; do not hand-edit a
  version that can drift from it.
- Write the changelog entry with the change, grouped by impact
  (`Added`, `Changed`, `Fixed`, `Deprecated`, `Removed`, `Security`), in the
  consumer's language. Use `documentation` for the changelog format; this skill
  owns the version bump and tag. A changelog is not a raw commit log.

## Verification

- [ ] The workspace state is known, and isolation was approved.
- [ ] Baseline tests ran before the first change.
- [ ] Each commit is atomic, tested, and stages only its own files.
- [ ] No secrets, generated output, or unrelated changes were committed.
- [ ] Commit messages explain why and follow the repo convention.
- [ ] No shared branch was force-pushed.
- [ ] The integration choice was the human's, and the merged result passed tests.
- [ ] Cleanup touched only worktrees this work created.
- [ ] Version, tag, and changelog agree for any release.
