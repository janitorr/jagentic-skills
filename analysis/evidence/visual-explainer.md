# visual-explainer: flow, one-pager, and show-me

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **pilot, positive on shape**. The skill picks a diagram for a call path,
prose for a one-liner, and a self-contained one-pager. `show-me` remains the
completeness benchmark.

## Question

- Does the skill choose a visual for a call-path explanation without being asked?
- Does it avoid a diagram for a one-line lookup?
- Does it build a useful self-contained one-pager for an issue?
- How does that one-pager compare to humanlayer's `show-me`?

## Fixtures

- Flow: `issue-interview/fixtures/webhooks`.
- One-pager: `visual-explainer/fixtures/onepager`, the same repo plus
  `tracker/issues/0001-webhook-delivery-retries.md` from the interview pilot.

## Method

Three conditions on the same prompts: control (no skill), `visual-explainer`,
and `show-me` (`vendor/humanlayer-skills/plugins/show-me`).

Flow prompt: "Walk me through how a webhook delivery failure moves from
`WebhookSender.send` through the notifiers, and what the retry change would
touch." Follow-up: "And what does `WebhookSender.send` do, in one line?"

One-pager prompt: "Turn the issue in `tracker/issues/0001-webhook-delivery-retries.md`
into a self-contained one-pager I can open in a browser. Save it in this repo."

HTML rendered in Chromium at 1280 px and 390 px; screenshots read manually.

## Results

### Flow

| | Control | `visual-explainer` | `show-me` |
|---|---|---|---|
| Visual | none | ASCII call tree + table | Mermaid sequence + funnel + diff + options table |
| Prose | ~600 words | ~250 words + visual | ~700 words + visuals |
| Correct path | yes | yes | yes |
| One-liner answer | prose | prose | prose |

Both skills chose prose for the one-liner; neither over-diagrammed.

### One-pager

| | Control | `visual-explainer` (pre-patch) | `show-me` | `visual-explainer` (post-patch) |
|---|---|---|---|---|
| Size | 12 KB, 192 lines | 20 KB, 398 lines | 32 KB, 1013 lines | 24 KB, 760 lines |
| Self-contained | yes | yes | yes | yes |
| Viewport | yes | yes | yes | yes |
| Timeline | no | yes | yes | yes |
| Code shape | no | no | yes, diff | yes, diff |
| Test/verification table | no | no | yes | yes |
| Dark default | no | no | no | yes |
| Mobile | fine | fine | fine | fine |

`show-me` is the most complete engineering brief. The pre-patch skill page was
cleaner but omitted the code shape and test plan. After the patch, the skill
page sits between the two: it keeps the focused timeline and scope cards, and
adds the diff and verification table.

The dark retest used `#101317` as the page background and included the code diff,
the six-row verification table, and a print check.

## What changed

- Added an **issue brief / one-pager** job to "Adapt to the job".
- Added a **one-pager recipe**: inline CSS, no external assets, real values, code
  shape when code changes, test table when acceptance matters, project palette
  or a dark low-glare default, responsive and print checks, predictable path,
  open it.
- Added a verification item for self-containment.
- Dark is the default when the project has no palette of its own.

## Limitations

- One run per condition, one model.
- The one-pager prompt is explicit, so proactive one-pager creation is untested.
- The flow prompt names a call path, which is diagram-friendly.
- Visual quality and contrast were read from screenshots, not measured; no
  accessibility audit and no light-theme check.
- The post-patch page was not compared against a fresh `show-me` run.

## Next

- Test a decision prompt (side-by-side options) and a prose-should-win prompt.
- Run the one-pager against a repo with a defined palette to check the override.
- Check contrast and a light-theme variant before treating dark as a universal
  default.
