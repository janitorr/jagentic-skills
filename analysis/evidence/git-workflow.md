# git-workflow: commit scope under pressure

Status: **pilot, negative**. The control passed when the repo stated its
convention, and the skill did not split a mixed slice when the repo did not.

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
worktree mechanics in steps 1, 5, and 7 duplicate the harness. Keep only the
decision rules (when to isolate, clean up only what you created, ask before a
forced removal), or drop the section.

## Conclusion

No demonstrated behavior in this harness. The one discriminator — a mixed slice
without a stated convention — was not fixed. The skill is a candidate for
retirement or a short policy note; more commit-scope reps would not add
information.

## Limitations

- One run per condition, one model.
- The prompt explicitly said "commit everything", which is the pressure under
  test; a neutral prompt may behave differently.
- No remote, so push and PR policy were not exercised.
- The stated-convention variant gave the control the rule it needed.

## Next

Decide: retire the skill, or narrow it to release/versioning and conflict
resolution and test those instead. Do not rerun this fixture.
