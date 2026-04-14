# Blind Adversarial Review — Phase 2.75

## Summary

**Verdict: BLOCKING.** The headline claim — "PR-AUC 0.044, ROC 0.73, 4.7x lift, weak-but-real out-of-sample signal" — does not survive scrutiny. Three independent problems compound: (i) the permutation null gives p=0.235, i.e. the observed PR-AUC is indistinguishable from label-shuffled noise; (ii) the 95 test positives span only 19 metros, so effective positive count is ~19 and all rare-event metrics are being inflated ~5x by within-metro temporal autocorrelation; (iii) the 19 "crashing" metros are overwhelmingly tiny rural micropolitans (Clarksdale MS, Johnstown PA, Beeville TX, Natchez, McComb, Zapata) — the model is not detecting a Sun Belt correction, it is detecting chronic rural distress, which the author's narrative never acknowledges. E05-t20 and E16 are both artefacts rather than findings. The project is recoverable as a "methodology / null-result" contribution but NOT as a "we predict housing crashes" contribution. Several mandatory diagnostics must be run before any paper draft.

## Blocking issues

1. **Effective sample size is ~19, not 95** *(RV-1 clustered bootstrap)*. Positives in the test set come from 19 metros but 95 rows because each crashing metro contributes up to 16 consecutive monthly observations of the same forward-return event (Clarksdale alone contributes 16 rows). Rows within a metro are near-perfectly correlated because fwd-12mo windows overlap. All confidence claims based on n=95 are overstated. A metro-clustered block bootstrap is mandatory.

2. **Permutation null gives p=0.235** *(RV-2 block-permutation null)*. The author's E20 shuffles train-row labels IID, which destroys both feature-outcome map and within-metro clustering and is arguably too weak a null (makes rejection easier). Even so the test fails. A within-metro (or within-month) block-permutation null is the right comparison for an autocorrelated panel — and will almost certainly produce an even weaker p-value. Current evidence does not reject the null of "no predictive power" at any conventional alpha.

3. **E05-t20 "PR-AUC 0.51" is one metro, five rows** *(RV-3 collapse positives to metro-events)*. At the 20% threshold the test set has exactly 5 positives, ALL Clarksdale MS in consecutive months. "PR-AUC 0.51" means "the model ranked 5 rows of one rural micropolitan in the top of a 10,170-row list." This is not a finding; reporting it as threshold-sensitivity evidence is misleading and must be removed or explicitly deflated.

4. **E16 lookalike placebo is a tautology** *(RV-4 momentum-only lookalike)*. Using ONLY the `zhvi_12mo_ret` feature as a score reproduces the "top-N lookalike vs rest at -5%" gap of 24% vs 3.7% (verified empirically). The model's "lookalike ranking" is momentum auto-correlation between past and future 12-month returns (Pearson r = 0.14), not a learned crash propensity. The -10% version of the same contrast is 0% vs 0%. The author's reading — "model ranks are meaningful continuously" — is not supported; the relaxed-threshold lookalike result is mechanically driven by one feature and re-labels the outcome.

5. **Population mismatch between train and test positives** *(RV-5 leave-one-metro-out).* Train positives are 18 metros (mostly rural post-2008 legacy declines); test positives are 19 metros (same rural cluster + a handful of Sun Belt tail). The model is a good predictor for Clarksdale-type metros and says nothing about the Sun Belt narrative. Author must either (a) acknowledge the population explicitly in the abstract, or (b) rerun with metros weighted by population to test whether the signal survives when rural autocorrelation is down-weighted.

## Non-blocking concerns

- **Tournament under-regularised.** RF used max_depth=10 with only 72 train positives; ROC 0.70 vs L2 0.73 is almost certainly a regularisation mismatch, not a true inductive-bias result. A properly tuned GB with aucpr early-stopping and max_depth=2-3 should be re-run before declaring L2 the champion.
- **No calibration step.** Train base rate 0.18% vs test base rate 0.93% is a 5x shift. `class_weight="balanced"` gives unbounded probabilities, which is fine for ranking but breaks any claim about top-k precision being "truly 4.7%."
- **E07-2021-06 collapses to PR-AUC 0.023** (lift 2.6x) — the signal is not stable across train-end dates. The author reports this but does not let it qualify the headline.
- **E02 (no mortgage) ROC 0.59.** The mortgage feature set is doing most of the work — but mortgage rate is a single national time series, so its "predictive" power is really a month-of-year indicator telling the model "this is the 2022-23 rate-shock era." This is borderline leakage of the regime into the cross-section; must be addressed.
- **E06 was silently skipped.** No horizon-sensitivity run exists in results. Either run or explicitly drop.

## Mandatory follow-up experiments

| exp_id | hypothesis | null prediction | data | runtime |
|---|---|---|---|---|
| RV-1 | Metro-clustered block bootstrap PR-AUC has 95% CI covering 0.01 and excluding 0.044 from the lower tail | 95% CI [0.015, 0.090]; CI includes base rate (0.009) | existing panel | 5 min |
| RV-2 | Within-metro block-permutation null gives p > 0.5 (even weaker than IID p=0.235) | block-perm p in [0.3, 0.6] | existing panel | 15 min |
| RV-3 | Collapse positives to metro-events (one row per metro per crash episode) and re-run E00; PR-AUC drops below 0.02 | PR-AUC ~0.015, ROC < 0.65 | existing panel | 2 min |
| RV-4 | Single-feature baseline using zhvi_12mo_ret alone recovers ≥90% of L2's PR-AUC | PR-AUC ≥ 0.040 | existing panel | 1 min |
| RV-5 | Leave-one-metro-out: drop Clarksdale MS (top crasher) from test; PR-AUC drops by >30% | new PR-AUC < 0.030 | existing panel | 10 min |
| RV-6 | Population-weighted PR-AUC using size_rank weights; PR-AUC collapses under population weighting | weighted PR-AUC < 0.02 | existing panel | 2 min |
| RV-7 | Remove mortgage features AND use time-detrended (within-month standardised) features — does any cross-sectional signal remain? | PR-AUC ~0.012, ROC ~0.55 | existing panel | 5 min |

## What would change the conclusion

Any ONE of the following would move the verdict from BLOCKING to CONDITIONAL:

1. RV-2 block-permutation p < 0.10.
2. RV-3 metro-event-collapsed PR-AUC still shows >2x lift over base rate.
3. RV-5 shows the signal is NOT dominated by 2-3 rural metros.
4. RV-4 shows L2 adds material lift above single-feature momentum.

Without at least one of these, the paper must be reframed as "null-result methodology contribution — naive momentum matches L2, and block-permutation does not reject H0, so metro-level 12-month crash prediction from publicly available features is not achievable at the 2023-era signal-to-noise ratio." That is a legitimate and publishable finding; "weak but real predictive power" is not.

---

## Phase 2.75 execution status (post-implementation)

All 7 mandatory RV experiments executed. Verdict summary:

| RV | Result | vs reviewer criterion | Verdict |
|---|---|---|---|
| RV-1 metro-cluster bootstrap | CI [0.015, 0.115], point 0.044, base 0.009 | lower bound > 2× base (0.019)? | **FAIL** — lower bound 0.015 < 0.019 |
| RV-2 block-permutation null | p = **0.493** | p < 0.10 | **FAIL** |
| RV-3 metro-collapsed test | PR-AUC 0.113, lift 3.46× at n_pos=19 | lift > 2× | PASS |
| RV-4 single-feature momentum | `-zhvi_12mo_ret` alone: PR-AUC 0.076 | L2 / single ≥ 1.5 | **FAIL** — L2 (0.044) is WORSE than momentum (0.076), ratio 0.58 |
| RV-5 leave-one-metro-out | Clarksdale removal → 39% PR-AUC drop | no metro > 25% drop | **FAIL** |
| RV-6 population-weighted | 0.042 vs 0.044 unweighted | weighted > 0.02 | PASS |
| RV-7 within-month detrended | PR-AUC 0.096, ROC 0.78 | PR-AUC > 0.02 | PASS (and surprising) |

**Blocking-criterion tally: 4 FAIL / 3 PASS.** RV-2's p = 0.493 is the cleanest failure — the observed signal is not distinguishable from a metro-block-permutation null. RV-4 is equally damaging — the 10-feature L2 model is measurably *worse* than a 1-feature momentum score.

**Interpretive updates forced by Phase 2.75**:

1. **The 95-positive test set is really 19 metro-events.** Clarksdale MS alone contributes 16 rows via overlapping 12-month windows. Effective n for all inference is ~19.
2. **The crashing population is mostly distressed rural micropolitans** (Clarksdale, Johnstown, Beeville, Natchez, McComb, Zapata) **plus Boise ID and Ukiah CA**. It is NOT the Sun Belt narrative (Austin/Phoenix absent from the crashers at the −10% threshold).
3. **Mortgage-rate features were masking the cross-sectional signal, not carrying it.** RV-7 removes national trend and PR-AUC goes UP. The mortgage coefficient in E00 was a macro-regime dummy, not a cross-sectional predictor.
4. **The L2 model is strictly dominated by a single-feature momentum score.** RV-4 PR-AUC 0.076 > L2 PR-AUC 0.044. Adding features made the model worse. This is the inductive-bias lesson: with 72 train positives and 10 features, regularization isn't enough to prevent negative transfer.
5. **The statistically defensible interpretation is: "markets falling in the last 12 months will keep falling for the next 12 months"** — which is not crash prediction, just momentum persistence.

**The conclusion must change from "weak but directionally real signal" to "we cannot predict metro-level housing crashes out-of-sample; apparent signals dissolve under honest inference."** This is a legitimate null finding.
