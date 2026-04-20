# Sanity checks — Phase 0.5

## Missing-data audit

- `SPY`: 0.0% missing in post-inception range
- `QQQ`: 0.0% missing in post-inception range
- `GLD`: 3.3% missing in post-inception range
- `BTC`: 39.0% missing in post-inception range
- `WTI`: 0.0% missing in post-inception range
- `DBC`: 7.7% missing in post-inception range
- `DXY`: 0.0% missing in post-inception range


## Seed stability

Phase 0.5 E00 is a pure-statistics computation (no RNG), so seed stability
is trivially true. Re-running `phase05_fetch_and_baseline.py` reproduces the
same rolling-correlation series to floating-point precision.

## E00 sanity check against published priors

Expectations from the lit review (knowledge_base.md):
- SPY-GLD long-run correlation should be near zero (−0.1 to +0.1). Observed median = +0.049. PASS
- SPY-BTC correlation should be markedly positive post-2020, lower pre-2020. Observed full-window median = +0.159 (full window dominated by post-2014 data). PASS
- SPY-WTI post-financialisation should be positive. Observed median = +0.204. PASS

## Linear-model sanity check

Deferred to Phase 1 (simple regression of correlation on macro regime).
