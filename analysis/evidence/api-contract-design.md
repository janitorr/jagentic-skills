# api-contract-design: baseline for an HTTP API skill

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **negative**. Two no-skill baselines did not fail: one with an
enumerated constraint list, then a harder prose brief with the constraints
moved into operating context. Three control runs in each round produced strong
public HTTP contracts, and three runs with `deep-module-design` did not beat
them on the HTTP rubric. Following `skill-forge`, no `api-contract-design`
skill was created. The real defect is the coverage claim in
`analysis/coverage.md` and `analysis/synthesis.md`, not agent behavior on this
fixture.

## Question

`analysis/coverage.md` says `deep-module-design` absorbs addyosmani's
`api-and-interface-design`, but the synthesized skill body contains no HTTP
material: no status or error contract, no boundary validation, no pagination,
no versioning, and no idempotency. Does that gap cause a capable agent to
produce a worse HTTP contract, enough to justify a separate skill?

## Fixture

`analysis/evidence/api-contract-design/fixtures/billing-api` is a small Python
billing service with no HTTP layer:

- Customers, invoices, invoice lines, and payments; integer cents; tenant
  isolation.
- Five internal operations: list invoices, read one, create a draft, edit a
  draft, charge an open invoice through an external provider.
- Real constraints: mobile and partner retries, a 30-second provider call
  against a 10-second client timeout, 50,000 invoices per customer, concurrent
  draft edits, an external provider whose response shape has changed, public
  consumers, and tenant-scoped API keys.

The task asks for `API.md` only, not implementation code. The constraints state
the operational realities; they do not name idempotency, cursor paging, ETags,
or RFC 9457.

## Method

Three arms, three repetitions each, same model, read-only except for the output
file, 1200-word cap:

- **Control:** `TASK.md` and the repository, with an explicit instruction to load
  no skill. All three reported "none".
- **`deep-module-design`:** the same task plus an instruction to load that skill
  and follow its process. All three loaded it.
- **New skill:** not run. The control passed the RED gate, so `skill-forge` step
  2 says stop before writing one.

Runs are in `api-contract-design/runs/`.

## Rubric

13 points:

| Dimension | Points |
|---|---:|
| Resource model and naming | 1 |
| Typed request/response schemas, server-generated fields, nullability | 2 |
| One error envelope and status mapping | 2 |
| Boundary validation, including the untrusted provider response | 1 |
| Additive compatibility, versioning, deprecation | 1 |
| Collection pagination and stable ordering | 2 |
| Lost-update prevention on draft edits | 1 |
| Retry safety: key source, atomic claim, payload guard, in-flight policy, retention, unknown outcome | 3 |

The last row is scored in six half-points. "Atomic claim" means the contract
requires the key to be claimed in one operation (a unique constraint or an
equivalent), not a read-then-write.

## Results

| Run | Resource | Schemas | Errors | Boundary | Compat. | Paging | Concurrency | Retry | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline-1 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 2.0 | 11.5 |
| baseline-2 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 3.0 | **13.0** |
| baseline-3 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 2.5 | 12.0 |
| deep-module-1 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 2.75 | 12.25 |
| deep-module-2 | 1 | 2 | 2 | 1.0 | 1 | 2 | 1 | 3.0 | **13.0** |
| deep-module-3 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 2.75 | 12.25 |

Arm means: control **12.17**, `deep-module-design` **12.50**. The difference is
0.33 of 13 points, smaller than the spread inside the control arm, and one
control run is perfect. There is no skill-sized failure.

## Findings

1. **The baseline already solves the hard HTTP problems.** All three control
   runs chose keyset pagination with a stable tie-break, `ETag`/`If-Match` for
   draft edits, a single problem-details error envelope, additive-only `/v1`
   compatibility, tenant-scoped keys with `404` for foreign resources, and an
   asynchronous `202` charge with a `pending|succeeded|failed|unknown` payment
   state. None of that is in `deep-module-design`.

2. **The no-skill gaps are implementation-level, not contract-level.**
   `baseline-1` guarantees no second side effect but does not say how the key is
   claimed. `baseline-3` says "executed exactly once" without a mechanism.
   `baseline-2` says state changes and key records commit atomically.
   `deep-module-2` is the only run that names a unique `(tenant_id, key)` index
   and a unique partial index for one unresolved payment per invoice. A contract
   document can reasonably stop at the guarantee, so this does not justify a
   skill.

3. **Provider-response validation is the most consistent omission.** Five of six
   runs normalize provider failures and hide provider payloads, but only
   `deep-module-2` names an anti-corruption layer that maps the external shape.
   This is one line of guidance, not a skill.

4. **Retention split the arms, not the skills.** `baseline-3` and
   `deep-module-3` chose seven days, exactly the partner window; `baseline-1`,
   `baseline-2`, `deep-module-1`, and `deep-module-2` chose 30 days. The vendor
   skill's rule — retention must outlive the longest retry path, including
   dead-letter replay — is the right correction, but the baseline usually
   reaches it without the skill.

5. **`deep-module-design` helps shape, not HTTP coverage.** The treatment runs
   add a responsibility statement, a deletion test, and rejected alternatives,
   and they are marginally more structured. They do not add HTTP mechanics that
   the control lacks. The skill's process ("what must a caller know", invariants,
   error modes) generalizes to an HTTP contract; its body does not teach one.

## Harden v2: prose brief

The first `TASK.md` enumerated eight constraints, each mapping to a rubric row.
To test whether that telegraphed the answers, the brief was rewritten as a
product request. The constraints moved into `README.md` as operating context:
the three client types and their retry behavior, provider latency and response
changes, concurrent draft edits, invoice volume, public consumers, and
tenant-scoped keys. No numbered requirements remain. The fixture on disk is
this v2 version; the runs above used the earlier brief.

Three fresh controls and three `deep-module-design` runs, same rubric and
model. The control prompt again forbade loading a skill; all three reported
"none".

| Run | Resource | Schemas | Errors | Boundary | Compat. | Paging | Concurrency | Retry | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| harden-baseline-1 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 2.75 | 12.25 |
| harden-baseline-2 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 2.75 | 12.25 |
| harden-baseline-3 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 2.5 | 12.0 |
| harden-deep-module-1 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 2.5 | 12.0 |
| harden-deep-module-2 | 1 | 2 | 2 | 1.0 | 1 | 2 | 1 | 2.5 | 12.5 |
| harden-deep-module-3 | 1 | 2 | 2 | 0.5 | 1 | 2 | 1 | 2.75 | 12.25 |

Arm means: control **12.17**, `deep-module-design` **12.25**. The gap is 0.08 of
13 points, effectively zero.

Findings:

1. **The prose brief did not separate the arms either.** All three controls
   inferred keyset pagination, `ETag`/`If-Match`, required idempotency keys,
   asynchronous `202` charges, a single error envelope, additive compatibility,
   and tenant-scoped `404`s from the operating context. The earlier result was
   not a checklist artifact.

2. **The remaining control gaps are the same two.** No control named a unique
   constraint or equivalent atomic key claim; one control named intent-before-
   call ("record a Payment first") but not the claim. No control said to validate
   the provider response shape, though all mapped provider failures into a
   stable vocabulary. These are one or two lines of reference, not a skill.

3. **`deep-module-design` again added shape, not HTTP coverage.** Its runs
   include the deletion test, alternatives, and a provider adapter. Its mean is
   flat, and two of its three runs chose seven-day key retention, shorter than
   the controls' 30 days.

4. **The controls chose better retention than the treatment.** All three
   hardened controls chose 30 days, explicitly to outlive the partner's
   dead-letter window. `deep-module-design` did not improve this and sometimes
   regressed it.

## Verdict

Do **not** create `api-contract-design` on this evidence. Both briefs passed;
the second was the harder test, and it produced the same result. Correct the
two analysis claims instead:

- `analysis/coverage.md`: category 8 is **Partial**, not **Covered**; move
  `api-and-interface-design` out of `deep-module-design`'s absorbed list and
  name the HTTP gap.
- `analysis/synthesis.md`: remove "contract first, error semantics, boundary
  validation, additive change" from the `deep-module-design` provenance row, or
  mark it as process-level generalization rather than absorbed HTTP guidance.

If the skill is revisited, the trigger is a real failure: a weaker model, a
subtler task that does not enumerate the constraints, or a task that asks for
implementation and not just the contract. Do not lower the fixture's realism to
manufacture a failure.

## Threats to validity

- One model family, three runs per arm, one reader, subjective rubric. This does
  not establish behavior on a weaker model.
- The first brief's eight constraints telegraphed most of the rubric. The
  hardened prose brief removed them and did not change the result, but both
  briefs still state the operating facts (retries, provider latency, volume).
  A real project may withhold more of that context.
- The deliverable is a design document, not code or a running API.
- "Atomic claim" and "provider validation" are implementation-adjacent; the
  contract-only task makes them optional.
- A no-skill baseline is not the same as an agent choosing among the full skill
  catalog. Here the prompt explicitly forbade loading a skill.

## Reproduce

- Fixture: `analysis/evidence/api-contract-design/fixtures/billing-api`
- Runs: `analysis/evidence/api-contract-design/runs/` (v1 brief) and
  `analysis/evidence/api-contract-design/runs2/` (v2 prose brief)
