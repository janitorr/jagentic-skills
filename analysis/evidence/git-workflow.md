# git-workflow: commits, conflict, push, and release

Status: **pilot; trimmed to invariants and defaults**. Commit scope is negative:
the control passed and the skill did not split a mixed slice under pressure.
Merge conflict, rejected push, and release showed no baseline failure; both
conditions handled them correctly. The only observed difference was the default
commit shape. The step-by-step procedures were then removed, leaving invariants
and defaults; the trimmed version is untested.

## Question

The skill claims it commits one logical change at a time, stages only that
slice, follows the repo convention or a default shape, resolves conflicts by
understanding both sides, never force-pushes a shared branch, and cuts releases
with a semver bump, annotated tag, and changelog.

## Fixture

`git-workflow/fixtures/setup.sh` builds a repo with three changes:

- a real timeout fix in `src/delivery.py` plus its test,
- a whitespace-only reflow in `src/notifications.py`,
- an untracked `debug.log`.

Two variants:

- **Stated convention.** `AGENTS.md` gives `<area>: <imperative summary>`, the
  areas, and "one logical change per commit".
- **No convention.** No commit section and a neutral `initial commit` baseline,
  so `git log` gives no style to copy.

`fixtures/conflict/setup.sh` builds `main` and `feature/retry` editing the same
`send()`: main adds `timeout=5`, the feature adds a retry loop, and each side's
own test passes alone. The merge must keep both.

`fixtures/push/setup.sh` builds a bare origin, a local `feature/retry`, and a
second clone that advanced the same branch, so the first push is rejected.

`fixtures/release/setup.sh` has a released `1.2.3`, an unreleased retry feature,
a manifest, a changelog, and no commit convention.

## Method

Commit-scope prompt: "Commit the current work. We're late — just commit
everything in one go. Do not push."

| Variant | Control | Skill |
|---|---|---|
| Stated convention | 1 run | not run; the control had no baseline failure |
| No convention | 1 run | 1 run |

| Task | Prompt | Control | Skill |
|---|---|---|---|
| Merge conflict | "Merge feature/retry into main, resolve any conflict, and run the tests. Do not push." | 1 | 1 |
| Rejected push | "Push feature/retry to origin. Do not force-push. If it is rejected, handle it." | 1 | 1 |
| Release | "Cut a release for the retry feature. Do not push." | 1 | 1 |

## Results

### Stated convention, control

Two commits:

- `delivery: raise webhook timeout to ten seconds`
- `notifications: reflow webhook send calls to fit line length`

`debug.log` and `__pycache__/` stayed untracked, and the tests passed. It also
explained the deviation from "commit everything". No miss.

### No convention, control

One commit, `delivery: raise webhook timeout to 10s`, containing:

- `src/delivery.py` (timeout fix)
- `src/notifications.py` (whitespace reflow)
- `tests/test_delivery.py` (expectation)

`debug.log` stayed untracked and the tests passed. The miss is narrow: the
format-only change traveled with the behavior change.

### No convention, skill

One commit, `Increase webhook timeout to 10s`, containing the same three files.
`debug.log` stayed untracked and the tests passed.

The skill matched the control. It followed the explicit "commit everything"
instruction over its own "commit per slice" rule and did not ask for a
correction.

### Merge conflict

| Check | Control | Skill |
|---|---|---|
| Kept the retry loop | yes | yes |
| Kept `timeout=5` on every attempt | yes | yes |
| Kept both tests | yes | yes |
| Full suite | 3/3 | 3/3 |
| Merge commit | `646338c` | `fa72b31` |

No discrimination. Both resolved `src/delivery.py` by combining both sides.

### Rejected push

| Check | Control | Skill |
|---|---|---|
| Force-pushed | no | no |
| Fetched and rebased | yes | yes |
| Kept both `RETRY.md` notes | yes | yes |
| Tests after rebase | pass | pass |
| Pushed fast-forward | yes | yes |

No discrimination. Both investigated and integrated rather than forcing.

### Release and tag

| Check | Control | Skill |
|---|---|---|
| Version | 1.3.0 | 1.3.0 |
| Bump | MINOR | MINOR |
| Tag type | annotated | annotated |
| Tag on the release commit | yes | yes |
| Manifest matches the tag | yes | yes |
| Changelog under `Added` | yes | yes |
| Tests | 2/2 | 2/2 |
| Commit subject | `Release 1.3.0` | `release: 1.3.0` plus a why body |

The only difference is the default commit shape. Both tags were annotated
(`git cat-file -t` returned `tag`), both manifests were `1.3.0`, and both
changelogs dated 2026-11-04.

Both conditions hand-computed the version. The arithmetic is deterministic and
belongs to a tool; the skill now prefers the repo's release tool or a semver CLI
and records the bump decision in a footer, changeset, or label.

## Worktree scope

The harness provides `worktree_create` and `worktree_remove`, and the repo's
`AGENTS.md` says workspace policy belongs to the agent file. The skill's
worktree mechanics in steps 1, 5, and 7 duplicated the harness.

The skill stays: the user values the commit, conflict, finishing, and release
guidance, and this pilot did not test any of it beyond commit scope. The worktree
mechanics were replaced with a pointer to the harness and agent file. The safety
rules remain: ask before adding isolation, clean up only what you created, and
never force-remove on your own initiative.

## Trim

The procedures mostly duplicated what the control already did. The body went
from 174 to 80 lines:

- **Removed:** workspace detection, baseline/branch/finish/delete/report
  procedures, and the worktree mechanics.
- **Kept as invariants:** one logical change per commit (including pushback on
  "commit everything"), checks before commit, conflicts keep both intents, a
  rejected push is integrated, tags are immutable, and cleanup only touches
  workspaces you created.
- **Kept as defaults:** branch `<area>/<short-slug>`, commit
  `<area>: <imperative lowercase summary>` plus a why body, release
  classification and tooling, annotated `vX.Y.Z`, and Keep a Changelog
  categories.

The conflict, push, and release results above were produced by the longer
version. The trimmed version has not been rerun.

## Conclusion

The control handled all three tasks: it resolved the conflict with both changes,
integrated a rejected push without force, and cut `1.3.0` with an annotated tag
and a changelog. There is no baseline failure to fix on conflict, push, or
release.

The skill's demonstrated effect is a consistent default commit shape when no
pattern exists: `release: 1.3.0` with a why body, against the control's
`Release 1.3.0`. Keep the skill for that consistency and for weaker models, not
as a capability the control lacks. Commit-scope splitting remains unproven.

## Limitations

- One run per condition, one model.
- The commit-scope prompt explicitly said "commit everything", which is the
  pressure under test; a neutral prompt may behave differently.
- The conflict and push fixtures are small; no remote CI, no signed tags, no
  review round.
- The release fixture is a MINOR feature. No breaking change, pre-1.0 release,
  or hotfix branch was tested.
- Semver is common knowledge; the release control chose 1.3.0 without the skill.
- The release fixture had no release tool, so both conditions hand-computed the
  version; a tool-assisted release is untested.
- The stated-convention commit variant gave the control the rule it needed.
- The trimmed version is untested; the results above belong to the longer
  version.

## Next

- Retest the trimmed version once: a mixed tree under "commit everything", a
  conflict, a rejected push, and a release with a semver CLI.
- Test a weaker model to see whether the invariants help where a strong control
  does not need them.
- Do not retest the removed procedures or the basic fixtures; they ceilinged.
