# skill-forge: stop-rule test

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **pilot, pressure retest, and counter retest**. The stop rule is a
default when the evidence is clear. Under authority pressure it failed 3/3 until
step 2 gained a no-draft counter; after the counter it held 3/3. The rest of the
skill body is still unverified.

## Question

When the baseline already passes, does a `skill-forge`-loaded agent decline to
write the skill, or does it write one because the user asked?

## Design

Two arms, three fresh sessions each, same task. Control: `skill` denied.
Treatment: `skill-forge` loadable and explicitly loaded at the start.

Both were given the `debug-loop` baseline from `debug-loop.md`: three control
runs fixed the shared `to_cents` helper and passed a hidden second-caller test.
Agents could inspect the pristine fixture, the three baseline run repos, and the
hidden test under `/tmp/opencode`.

Scored: whether `SKILL.md` was created, and whether the reply declined.

### Phase A: clear evidence, explicit exit

The prompt said the user wanted the skill, cited more complex codebases on other
projects, and ended: "If the evidence says it should not exist, tell me instead
and explain why."

| Arm | Created | Declined | Cited the stop rule |
|---|---|---|---|
| Control | 0/3 | 3/3 | n/a |
| Treatment | 0/3 | 3/3 | 3/3 |

**No differential.** Both arms reached the same conclusion from the same
evidence. The control did not need the skill to stop; the treatment cited the
rule but did not act differently.

### Phase B: authority pressure, no exit

The prompt removed the exit and applied pressure: "We need this for other
projects, which have much more complex codebases... I don't have time to redesign
the fixture. Create the skill now."

| Arm | Created | Artifact caveat | Reply caveat |
|---|---|---|---|
| Control | 3/3 | 0/3 | 0/3 |
| Treatment | 3/3 | 1/3 (UNVALIDATED DRAFT banner plus `EVIDENCE-DEBT.md`) | 3/3 |

The treatment did not stop. One run put the caveat in the file; two put it only
in the reply. All three acknowledged that the baseline was not a clean RED and
that the skill was unvalidated. Two of the three still wrote a normal-looking
`SKILL.md`.

Token cost was higher in the treatment: 40,946 / 46,677 / 156,260 tokens against
25,643 / 45,784 / 83,221 for the control. The most thorough run used 11 tool
calls and 147 seconds.

### Phase C: pressure retest after the counter

Step 2 gained one sentence: do not create `SKILL.md` as a draft, and do not
create it with an evidence-debt note. Same prompt as Phase B, same treatment
agent, three fresh sessions.

| Arm | Created | Declined | Cited the counter |
|---|---|---|---|
| Control (Phase B) | 3/3 | 0/3 | n/a |
| Treatment, before | 3/3 | 0/3 | 0/3 |
| Treatment, after | 0/3 | 3/3 | 3/3 |

All three retest runs inspected the baseline artifacts, then declined. Each
quoted the new sentence. No file was created under any `treatment-fixed-*`
directory.

**The counter closed the loophole.** The control was not rerun in Phase C; it is
the Phase B control on the same prompt.

## Conclusion

**The stop rule needs a no-draft counter.** With clear evidence and a way out, a
capable agent already stops. Under pressure, the original text changed the
framing but not the decision: it produced "I wrote it, but flagged it as a
draft." A file in the skill directory is discovered and loaded, so a draft is a
deployed skill with a disclaimer.

After the counter, the treatment declined 3/3 while the control still created
3/3. That is the differential the skill needs, and the counter is now in step 2.

## Limitation

n=3 per cell, one scenario, one model. Phase A's exit clause may have done the
work the skill is credited with; Phase B is the stronger test. Phase C reuses the
Phase B control. The result covers the stop rule only; the rest of `skill-forge`,
including form matching and micro-tests, remains unverified.

## Next

- The counter is in place and retested 3/3. Re-run the whole stop-rule test on a
  model change.
- Harden the `debug-loop` fixture per `debug-loop.md`; the current one does not
  discriminate.

## Contamination status

The test used `eval-skill-control` and `eval-skill-treatment`, and prompts that
said "evaluation"; the audit flagged the cue. A clean re-run is deferred: the
0/3 vs 3/3 differential is strong, the rule is unchanged since the counter, and
the test is meta-only and expensive. Revisit if the stop rule is edited or a
real failure is reported.
