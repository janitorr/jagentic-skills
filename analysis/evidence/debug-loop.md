# debug-loop: two baselines, both ceilings

Model: `deepseek-v4.1-flash` (`opencode-go`, default variant).

Status: **ceiling on two fixtures**. Six control runs fixed the root cause and
passed a hidden second-caller test. No skill was written.

## Question

Does a capable agent fix the root cause of a failing test, or does it patch the
symptom the failing test names? If the control patches symptoms, a `debug-loop`
skill has something to change.

## Fixture 1: money rounding

`debug-loop/fixtures/orders` is a small Python `unittest` repo. `to_cents` in
`src/orders/money.py` truncates `float(text) * 100`, so `1.15` becomes `114`.
Two visible tests fail: `parse_amount("1.15")` and a report total.

The discriminator is hidden at scoring time:
`debug-loop/hidden/test_root_cause.py` calls `money.to_cents` directly and
through `orders.invoice.invoice_total`. A caller-only fix in `parse.py` makes
the visible suite pass and fails the hidden test; a fix in `money.py` passes
both. Verified before the runs: caller fix 4/4 visible with 2 hidden failures;
shared-helper fix 6/6.

| Run | Visible | Hidden | Root file changed | Tests added | Tool calls | Tokens | Wall |
|---|---|---|---|---|---|---|---|
| 1 | 7/7 | 9/9 | `money.py` | yes | 8 | 75,901 | 46.9s |
| 2 | 4/4 | 6/6 | `money.py` | no | 7 | 55,184 | 25.0s |
| 3 | 7/7 | 9/9 | `money.py` | yes | 7 | 64,548 | 27.1s |

All three read the traceback, opened `money.py`, and replaced the float
conversion with `Decimal`. None patched the caller.

**Ceiling.** The fixture is too easy: the traceback names `parse_amount`, and
the root is one small function away. It measures code reading, not debugging.

## Fixture 2: shared cache key (hardened)

`debug-loop/fixtures/pricing` is a four-module Python `unittest` repo.
`PriceCache.key` in `src/shop/cache.py` returns `(sku, region)` and drops
`currency`, with a comment claiming currency is normalised upstream. The
catalog prices each `(sku, region, currency)` separately.

`checkout.quote` and `invoice.invoice_lines` are two callers sharing the cache.
The visible failure is a EUR quote returning the USD price. The tempting local
fix is a fresh cache inside `checkout.quote`: it passes the visible suite and
leaves `invoice` broken. The hidden test
`debug-loop/hidden/test_cache_root_cause.py` drives both callers through one
cache. Verified before the runs: fresh-cache fix 6/6 visible with 2 hidden
failures; cache-key fix 9/9.

Control: three fresh `eval-debug-control` sessions, release pressure in the
prompt, three copies at `/tmp/opencode/debug-loop/pricing-run-{1,2,3}`.

| Run | Visible | Hidden | Root file changed | Tests added | Caller patched |
|---|---|---|---|---|---|
| 1 | 7/7 | 10/10 | `cache.py` | yes | no |
| 2 | 7/7 | 10/10 | `cache.py` | yes | no |
| 3 | 6/6 | 9/9 | `cache.py` | no | no |

All three found the dropped `currency`, changed `cache.key`, and left
`checkout.py` and `invoice.py` alone.

**Ceiling again.** The cache key is one hop from `pricing.price`, and the
misleading comment is a signpost rather than a hiding place. A release-pressure
prompt did not produce a caller patch.

## What this means

Six control runs across two fixtures fixed the root cause 6/6 and passed a
second-caller test 6/6. On this model and these fixtures, the target behavior is
the default: trace to the shared source, fix it once, verify another caller.

That does not prove `debug-loop` is useless on a real codebase. It does mean a
synthetic fixture is not producing the failure the skill would address, and
`skill-forge` says do not write the skill until one does.

## Limitation

Both fixtures are small enough to hold in one context, and both roots are one
hop from a module the failure names. Fixture 1's hidden test also accepted a
fix that truncates three-decimal inputs; fixture 2's hidden test is stronger.

## Next

- Run the baseline on a real project with a historical bug where a caller was
  patched and a second caller broke. That is the population the skill is for.
- If no such failure appears, record the no-op and do not write `debug-loop`.
- Keep both fixtures as regression gates for any future attempt.
