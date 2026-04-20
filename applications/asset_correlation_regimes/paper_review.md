# Phase 2.75 adversarial review — asset_correlation_regimes

**Verdict**: REFRAME
**Reviewer**: fresh Claude subagent, 2026-04-20
**Target type**: exploratory

## Reproducibility

All three phase scripts re-ran end to end on 2026-04-20. Phase 0.5
re-downloads prices and FRED macro successfully (GPR fails on DNS, as it
did at kickoff). Numbers compared against the originals in
`/tmp/results_original.tsv`, `tournament_original.csv`,
`regime_table_original.csv`:

- **Phase 0.5 E00 rows**: bit-identical.
- **Phase 1 tournament**: F1_OLS bit-identical; F2_GBR / F3_RF differ in
  the 3rd decimal (sklearn tree-split non-determinism is expected — the
  sign and ordering of results is preserved, all R² remain strongly
  negative, same winners). Acceptable.
- **Phase 2 regime decomposition**: `regime_correlation_table.csv`
  bit-identical for all 68 surviving rows; R5 CURRENT values bit-identical.
  One CI endpoint off in the 4th decimal (E47 COVID_BTC high endpoint:
  0.3143 → 0.3144, expected RNG drift from a different pandas/numpy minor).

**Verdict on reproducibility**: PASS. Scripts are reproducible and
idempotent.

## Findings (in severity order)

### FATAL

**F1 — IID bootstrap CIs are wrong by a factor of ~2–8×; headline claim
collapses under block bootstrap.**

This is the review's central finding. Phase 2 computes 95% CIs by IID
resampling a series of overlapping 90-day rolling correlations. Each
daily observation shares 89 of 90 days of underlying returns with its
neighbour. The bootstrap therefore treats ~90 redundant observations as
if they were independent — exactly the inferential error Politis &
Romano (1994) and the Künsch (1989) block-bootstrap literature warn
against for time series.

I wrote `phase275_block_bootstrap.py` (moving-block bootstrap, block
length 90) and computed both the lag-1 autocorrelation ρ₁ of each
crisis-window correlation series and the AR(1) effective sample size
N_eff = N·(1−ρ)/(1+ρ). Results (see `block_bootstrap_R5.csv`):

| crisis    | target | n   | ρ₁    | N_eff | IID CI              | Block CI              | width ratio |
|-----------|--------|----:|------:|------:|---------------------|-----------------------|------------:|
| CURRENT   | GLD    | 171 | +0.91 |   8.3 | [+0.161, +0.178]    | [+0.156, +0.185]      | 1.77×       |
| TARIFF25  | GLD    |  92 | +0.96 |   2.0 | [+0.147, +0.200]    | [+0.116, +0.256]      | 2.60×       |
| INFL2022  | GLD    | 304 | +0.997|   1.0 | [+0.007, +0.070]    | [−0.251, +0.165]      | 6.56×       |
| COVID     | GLD    |  90 | +0.98 |   1.0 | [−0.147, −0.030]    | [−0.302, +0.157]      | 3.94×       |
| GFC       | GLD    | 397 | +0.997|   1.0 | [−0.009, +0.043]    | [−0.244, +0.155]      | 7.69×       |

Most crises give N_eff=1: the 90-day rolling series contains
essentially one independent correlation estimate. The IID bootstrap is
not merely tight — it is inferentially meaningless for those windows.

**Consequence for the headline claim.** The README/knowledge-base
framing is "current SPY-GLD correlation is higher than ALL prior
crisis windows in 22 years." Under block-bootstrap:

- CURRENT (+0.170) vs GFC (+0.017): separated.
- CURRENT vs COVID (−0.088): **Block CIs overlap** (COVID Block
  CI = [−0.302, +0.157] which crosses CURRENT's +0.170 region
  only marginally at the upper end — the separation is weak).
- CURRENT vs INFL2022 (+0.037): **Block CIs overlap** ([−0.251,
  +0.165] reaches up into CURRENT's CI [+0.156, +0.185]).
- CURRENT vs TARIFF25 (+0.174): **Block CIs overlap heavily**; in
  fact TARIFF25's *point estimate* (+0.174) is numerically higher
  than CURRENT's (+0.170). TARIFF25 is just 5.5 months earlier in
  the same year and arguably the same underlying macro episode.

**The headline "highest in 22 years" is false on point estimates
(TARIFF25 is higher) and unsupported at 95% confidence (3 of 4 prior
crises have CIs that overlap CURRENT).** This is fatal to the drafted
claim as written. The claim that *survives* is much weaker: "SPY-GLD
correlation in 2025–2026 has run systematically positive at levels
that, across the 22-year history, appeared only during the 2007–08
financial crisis / 2022 inflation shock / early-2025 tariff episode —
and not during the periods between crises."

### MAJOR

**M1 — R5 crisis windows defined AFTER seeing the data.**

Git log shows only two commits. The kickoff commit introduced
`knowledge_base.md` with no mention of GFC/COVID/INFL2022/TARIFF25/
CURRENT as labelled windows; those appear for the first time in
`phase2_regime_decomposition.py` in the Phase 1+2 commit (45df446).
The CURRENT window (2025-11 onward) is defined in code *after* the
correlation series was inspected — classic post-hoc window selection.
For an exploratory project this is not fatal, but the paper must (a)
declare CURRENT as post-hoc, (b) verify robustness to CURRENT start
dates in {2025-09, 2025-10, 2025-11, 2025-12}, and (c) frame the
result as descriptive, not inferential. The 2007-09-01 GFC start is
also off-by-month against NBER (recession started Dec 2007) and the
2020-02-01 COVID start precedes the market break by ~3 weeks.

**M2 — Regime thresholds not pre-registered, appear cherry-picked.**

The Fed ±25bps, CPI 2%/3.5%, DXY ±3%, drawdown 15% cutoffs appear
nowhere in `knowledge_base.md` or `design_variables.md` as justified
priors. The 25bps number matches the lit-review fact P024 (a 25bps
Fed surprise ≈ 1% SPY move) but that's about shock size, not
cycle-phase classification. The CPI 3.5% threshold picks out the
2022 shock; the DXY 3% picks out 2014–15 and 2022; the 15% drawdown
picks out COVID and maybe late-2008 — all chosen so the current
regime lands in one identifiable bucket. Paper must sensitivity-test
these cutoffs or report each conditional mean with a cutoff sweep.

**M3 — Multiple comparisons uncorrected across 68 E-rows.**

Phase 2 produces 68 regime-conditional means, each with a 95% CI.
No Bonferroni, BH, or min-p correction. At α=0.05 IID-bootstrap, ~3
spurious "separations from the full-window mean" are expected by
chance. Given how tight the IID CIs are, the apparent number of
separating rows is inflated. With block bootstrap the widths
multiply by 2–8 and most "significant" regime differences disappear.
Paper must either (a) report only the pre-registered primary
hypothesis tests and treat everything else as descriptive, or (b)
apply BH at the family level and report q-values.

**M4 — Bug in NaN-category handling (`R2_inf=nan`).**

`phase2_regime_decomposition.py` calls `pd.cut` on CPI YoY which
produces NaN for the first ~252 days of the sample (before YoY is
defined). That NaN category gets stringified to `"nan"` and written
as a regime level. Row E25 (`R2_inf=nan, corr_SPY_WTI`) contains a
bootstrap mean (−0.119) over 161 observations from 2004–2005 — a
regime that is "has no defined CPI YoY yet," which is nonsense as a
regime interpretation. For GLD/BTC/DBC the pre-2005 data doesn't
exist so these rows correctly show n=0. Fix: drop rows where
`R2_inf` is NaN before writing results.

**M5 — Phase 1 negative R² is not just "can't predict" — it's
numerically extreme (R²=−5.9 for OLS/BTC). This signals leakage or
target-design issues, not merely lack of predictability.**

R² << 0 means the model does *much worse* than predicting the
training-set mean. Given the 90-day window, the final 89 observations
of each training fold contain return-windows that overlap the first
few days of the test fold — that's information leakage in the
feature side (macro features are slow, so the training period and
test period are in the same macro regime). More importantly, the
target (90-day rolling correlation) has a hard structural break at
fold boundaries. A cleaner design would target *changes* in
correlation or use purged/embargoed CV (López de Prado 2018). The
"macro regime can't predict correlation" conclusion may actually be
"our CV design was broken." Paper must either fix this or
drastically soften the Phase 1 conclusion.

### MINOR

**m1 — GFC × BTC is correctly handled as NaN (`n=0`), BUT the Phase 2
print-out still lists it under "Crisis-to-crisis comparison for GLD"
cleanly and skips BTC. Paper should display "n/a (BTC data starts
2014-09-17)" explicitly to avoid the reader inferring an absence.

**m2 — The 6,942-row price panel vs ≤6,849 rolling correlation
observations suggests ~100 days of NaN from alignment/ffill. Spot
check passes; no silent drop.

**m3 — `pd.Timestamp.utcnow()` is deprecated (pandas 2.x emits a
FutureWarning). Replace with `pd.Timestamp.now(tz="UTC")`.

**m4 — `sanity_checks.md` reports SPY-WTI median +0.204 as PASS
against "post-financialisation should be positive" but the full
window INCLUDES the pre-2008 pre-financialisation period. Not
wrong, but incomplete — should report pre-/post-2008 medians
separately since that's the stylised fact the check claims to test
(P019 vs P022).

**m5 — `research_queue.md` and `design_variables.md` were not
modified between Phase 0.5 and Phase 2 commits. Exploratory doesn't
require formal pre-registration, but the project's own design docs
should be updated to record which regime cutoffs were chosen and why.

**m6 — GPR index fetch has been dead for two consecutive runs. Either
find a working mirror (Dallas Fed hosts a CSV at a different path)
or drop GPR from the Phase 2 regime variables openly, rather than
leaving it as a silently-missing fourth macro driver.

## Required actions before Phase 3

1. **Replace the IID bootstrap with a moving-block bootstrap** (block
   length 90) everywhere that `bootstrap_ci()` is used on rolling-
   correlation series. Use `phase275_block_bootstrap.py` as the
   reference; extend to all R1–R5 regimes. Re-generate
   `regime_correlation_table.csv` with block-bootstrap CIs and update
   all E-rows. This is not optional — it is the difference between
   a publishable-quality exploratory result and a statistically
   invalid one.

2. **Retract the "highest in 22 years" headline.** The point estimate
   for TARIFF25-GLD (+0.174) is numerically higher than CURRENT
   (+0.170), and under honest CIs the two are indistinguishable.
   Reframe as: "SPY-GLD correlation in 2025–H1 2026 has run in a
   narrow band of +0.15 to +0.20 sustained across a full 5+ month
   period, a regime that in 22 years has only been approached during
   the GFC, the 2022 inflation shock, and the March–May 2025 tariff
   episode — suggesting CURRENT is a continuation of the tariff-era
   regime rather than a new decoupling."

3. **Pre-register (retrospectively, with a timestamp) the crisis
   windows in `knowledge_base.md`** with explicit citations to the
   macro history that defines each. Include a robustness table
   showing sensitivity of the CURRENT point estimate to start dates
   from 2025-09 through 2025-12.

4. **Fix the `R2_inf=nan` bug** in `phase2_regime_decomposition.py`
   by dropping NaN categories before the loop, and delete the bogus
   E25 row from `results.tsv`.

5. **Apply Benjamini-Hochberg** across the 68 E-rows for any
   "statistically different from full-window mean" claims, OR declare
   explicitly that Phase 2 is descriptive and no null-hypothesis
   claims are being made.

6. **Re-examine Phase 1 with purged/embargoed TimeSeriesSplit** (gap
   of at least 90 days between train and test). If R² is still
   strongly negative, the "macro can't predict correlation" claim
   holds; if R² moves near zero, the original negative R² was a
   CV-design artefact and the paper must say so.

## Recommended but not required

- DCC-GARCH robustness check: the knowledge base cites DCC-GARCH as the
  gold standard (facts 3, 9). At least a single-asset-pair (SPY-GLD) DCC
  conditional-correlation series would triangulate the rolling-Pearson
  findings.
- Stationary-block bootstrap (Politis & Romano 1994) with geometric
  block length ~Exp(1/90). More modern than fixed-block Künsch and
  removes the block-length hyperparameter.
- Report 30d and 250d rolling windows alongside 90d (per P007,
  `knowledge_base.md` fact 26). The paper claims 90d is the
  industry standard and then relies only on 90d — providing 30/250
  would let a reader see if the CURRENT phenomenon is a 90d-window
  artifact (it probably isn't, but show it).
- Replace `sklearn.TimeSeriesSplit` with `PurgedKFold` from López de
  Prado's `mlfinlab` package.
- Tests: there are no unit tests. For an exploratory project this is
  acceptable but the per-CLAUDE.md TDD requirement suggests at least
  a `test_bootstrap_block_vs_iid.py` that asserts block CIs are
  wider than IID CIs on a synthetic AR(1) series with ρ=0.95.
