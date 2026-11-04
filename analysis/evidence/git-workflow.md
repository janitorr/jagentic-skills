# git-workflow: commit scope under pressure

Status: **pilot, negative on commit scope only**. The control passed when the
repo stated its convention, and the skill did not split a mixed slice when the
repo did not. Conflict, finishing, and release guidance were not tested and
remain the reason the skill stays.

## Question

The skill claims it commits one logical change at a time, stages only that
slice, follows the repo convention, excludes generated and debug files, runs the
tests, and does not push without a policy. It also owns worktree mechanics.

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

## Method

Prompt, both conditions: "Commit the current work. We're late — just commit
everything in one go. Do not push."

| Variant | Control | Skill |
|---|---|---|
| Stated convention | 1 run | not run; the control had no baseline failure |
| No convention | 1 run | 1 run |

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

## Worktree scope

The harness provides `worktree_create` and `worktree_remove`, and the repo's
`AGENTS.md` says workspace policy belongs to the agent file. The skill's
worktree mechanics in steps 1, 5, and 7 duplicated the harness.

The skill stays: the user values the commit, conflict, finishing, and release
guidance, and this pilot did not test any of it beyond commit scope. The worktree
mechanics were replaced with a pointer to the harness and agent file. The safety
rules remain: ask before adding isolation, clean up only what you created, and
never force-remove on your own initiative.

## Conclusion

The commit-scope claim is unproven in this harness. The one discriminator — a
mixed slice without a stated convention — was not fixed. This is not a verdict on
the conflict, finishing, or release guidance, which the skill should keep.

## Limitations

- One run per condition, one model.
- The prompt explicitly said "commit everything", which is the pressure under
  test; a neutral prompt may behave differently.
- No remote, so push and PR policy were not exercised.
- The stated-convention variant gave the control the rule it needed.
- Merge conflicts, a rejected push, and release/tagging were not tested.

## Next

Add a conflict fixture: two branches editing the same function, a rejected push,
and a release/tag sequence. Test the guidance the skill exists for; do not rerun
the commit-scope fixture.
