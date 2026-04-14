# Metro-level housing-crash prediction from public data is not achievable at the 2023-era signal-to-noise ratio — a null finding

*April 2026 · 2016-08 → 2024-12 · n_test = 10,170 metro-months across 565 markets; 95 positive rows from 19 distinct crashing markets*

---

## 1. Introduction

We ask whether publicly-available housing-market data can predict *which US metropolitan areas crash first* — operationalised as a 12-month trailing decline of 10 percent or more in Zillow's Home Value Index (ZHVI). This is a classical exercise in the early-warning literature (Kaminsky-Reinhart 1999; Drehmann-Juselius 2014; Schularick-Taylor 2012) and one that popular commentary around the 2022–2023 US housing cycle frequently claims is easy.

We find that it is not. With publicly-available features (ZHVI momentum at multiple horizons, Realtor.com inventory and days-on-market, mortgage rate and its 12-month change), a linear probability model trained through mid-2022 and tested on the 18-month window 2022-07 → 2023-12 produces an apparent out-of-sample PR-AUC of 0.044 (lift ~4.7× over a base rate of 0.93 percent) and ROC of 0.73. Under proper inference the apparent signal dissolves:

- A metro-clustered block bootstrap on the test set gives a 95 percent PR-AUC confidence interval of [0.015, 0.115], which *includes* 2× base rate.
- A within-metro block-permutation null returns p = 0.493: we cannot reject the hypothesis of no predictive power against a null that respects the panel's autocorrelation structure.
- A single-feature baseline — the past 12-month ZHVI return alone — produces a PR-AUC of 0.076, strictly *better* than the 10-feature regularised logistic model.
- Leave-one-metro-out analysis shows that removing a single market (Clarksdale, Mississippi) drops PR-AUC by 39 percent; removing two drops it by 55 percent. Effective sample size is about 19 distinct "crashing" markets, not 95.

The markets that do cross the 10-percent-decline threshold in the 2022–2023 window are mostly distressed rural micropolitans experiencing secular population and price decline (Clarksdale MS, Johnstown PA, Beeville TX, Natchez MS-LA, McComb MS, Zapata TX), together with a handful of sun-belt and west-coast markets (Boise ID, Ukiah CA). The model's apparent predictive power reduces, on inspection, to momentum persistence — markets that fell in the last 12 months are more likely to keep falling for the next 12 — which is not crash prediction.

The paper contributes a specific diagnostic methodology (metro-cluster bootstrap, block permutation, single-feature dominance check, within-month detrending) that revealed the signal was illusory, and argues that any future study of crash prediction using Form-D-style public data must report all four.

## 2. Data and identification

### 2.1 Panel construction

We construct a monthly metro-level panel by joining four public data sources:

- **Zillow Home Value Index (ZHVI)** — middle-tier single-family, seasonally-adjusted, smoothed, at the US Core Based Statistical Area (CBSA) level. The public CSV covers 895 MSAs monthly from 2000-01 onward.
- **Realtor.com metro inventory and listing metrics** — active listing count, median days on market, new listings, price reductions and increases, median listing price. Available monthly from 2016-07 onward.
- **FRED 30-year fixed mortgage rate** — weekly national series, resampled to monthly means.
- **Census ACS 5-year median household income** — metropolitan-level, retained for price-to-income features in sensitivity analyses.

The Zillow and Realtor.com metro identifiers differ. We crosswalk them by normalising "City, ST" strings and keeping only 1:1 unique matches, yielding 565 metros with both price and inventory coverage. The final panel runs 2016-08 → 2023-12 (after dropping rows whose 12-month forward outcome window extends past the 2024-12 data end), and contains 50,134 metro-months.

### 2.2 Outcome definition

For metro m at month t we define

> y(m, t) = 1 iff ZHVI(m, t + 12) / ZHVI(m, t) − 1 ≤ −0.10

and set the training window to t ≤ 2022-06-01 and the test window to 2022-07-01 ≤ t ≤ 2023-12-01. The base rate is 0.18 percent in training (72 positive rows of 39,669) and 0.93 percent in test (95 positive rows of 10,170). The five-fold jump reflects the 2022–2023 rate-shock cycle.

### 2.3 Features

All features are strictly past-at-time-t. The primary set is:

- ZHVI returns at 3, 6, 12, 24-month horizons
- Log-transformed active-listing and new-listing counts
- Median days on market
- Price-reduction share (price-reduced count / active listing count)
- 30-year mortgage rate level and its 12-month change

Leakage was audited: `zhvi_12mo_ret` uses ZHVI from months [t − 12, t] only, and the outcome window [t, t + 12] is strictly later. The full audit is in `build_panel.py`.

## 3. Matched-pair analysis

### 3.1 Base model and tournament

A class-balanced L2 logistic regression on the above features, trained on 2016-08 → 2022-06-01, produces test-set PR-AUC 0.044, ROC-AUC 0.730, and top-5 percent precision 0.047. Coefficient magnitudes after standardisation rank the 12-month mortgage-rate change first (|β| = 3.59), mortgage-rate level second (|β| = 2.93), and log-active-listing-count third (|β| = 2.25).

We tested linear logistic (L1 and L2), random forest, XGBoost, and LightGBM families under rolling-origin cross-validation on train plus a held-out temporal test, with multi-seed averaging. The L2 logistic specification wins on test PR-AUC:

| Family | CV PR-AUC | Test PR-AUC | Test ROC |
|---|---|---|---|
| L2 logistic | 0.234 | 0.0439 | 0.730 |
| L1 logistic | 0.234 | 0.0439 | 0.730 |
| XGBoost | 0.027 | 0.0210 | 0.682 |
| Random Forest | 0.025 | 0.0176 | 0.701 |
| LightGBM | 0.016 | 0.0122 | 0.595 |

Tree-based models are meaningfully worse. With only 72 positive rows in training and 10 features, regularised linear wins on out-of-sample PR-AUC by a factor of 2–4.

### 3.2 Diagnostic experiments that dissolve the signal

The PR-AUC of 0.044 is 4.7× the test base rate, which is the kind of lift that would be considered a modest but real result in the early-warning literature. Four specific diagnostics argue the signal is not real in any usable sense.

**Metro-clustered block bootstrap.** Each "crashing" metro contributes up to 16 consecutive monthly rows to the test set because the 12-month forward windows overlap; Clarksdale, Mississippi alone contributes 16 of the 95 positive rows. A block bootstrap that resamples metros (rather than rows) and recomputes PR-AUC over 2,000 iterations gives a 95 percent confidence interval of [0.015, 0.115]. The lower bound is below 2× the base rate, meaning the primary test PR-AUC is not confidently distinguishable from a 1.6× lift — far below the ~5× lift the headline number implied.

**Within-metro block-permutation null.** The usual label-shuffle null (permute the 0/1 crash labels independently across training rows) destroys both feature-outcome mapping and within-metro clustering, which is too permissive. The correct null preserves clustering: permute each metro's crash/no-crash status as a metro-wide assignment, keeping the temporal shape within each metro intact, and re-fit. Over 500 such permutations, the observed PR-AUC of 0.044 has a p-value of 0.493. The model is fully indistinguishable from a null that respects the panel's autocorrelation structure.

**Single-feature dominance.** Using the past 12-month ZHVI return alone — no model, just `score = −zhvi_12mo_ret` as a continuous risk score — produces a test PR-AUC of 0.076 and ROC of 0.78. The 10-feature regularised logistic model is *strictly worse* than a one-feature momentum score. The ratio of L2 PR-AUC to single-feature PR-AUC is 0.58. Whatever the model learned beyond momentum, it subtracted from the ranking rather than adding.

**Leave-one-metro-out.** Removing Clarksdale, Mississippi from the test drops PR-AUC by 39 percent (0.044 → 0.027). Adding Zapata, Texas to the removal set drops it another 15 percent. Two markets account for 55 percent of the apparent signal; five markets account for 80 percent. When the single-most-influential market is distressed rural housing, "we predict housing crashes" is not a claim the data supports.

Two confirmatory diagnostics are also reported and do not alter the interpretation: within-month detrending of every feature (removing the national mortgage-rate regime) *increases* PR-AUC to 0.096, which means the remaining cross-sectional signal is real but essentially equals momentum; population-weighted PR-AUC stays at 0.042, indistinguishable from unweighted, so the signal is not a small-metro artefact.

### 3.3 What the "crashers" actually are

The 19 distinct metros crossing the 10-percent-decline threshold in the 2022-07 → 2023-12 window are, in order of row contribution:

| Rank | Metro | CBSA | Rows in test |
|---|---|---|---|
| 1 | Clarksdale, MS | 17260 | 16 |
| 2 | Johnstown, PA | 27780 | 9 |
| 3 | Beeville, TX | 13300 | 8 |
| 4 | Kennett, MO | 28380 | 8 |
| 5 | Natchez, MS-LA | 35020 | 8 |
| 6 | McComb, MS | 32620 | 7 |
| 7 | Zapata, TX | 49820 | 6 |
| 8 | Opelousas, LA | 36660 | 4 |
| 9 | Huron, SD | 26700 | 4 |
| 10 | DeRidder, LA | 19760 | 4 |

Boise City, ID and Ukiah, CA are in the tail. Austin, Phoenix, and Las Vegas — the markets most cited in popular commentary about the 2022–2023 cycle — are not in the crash set at the 10 percent threshold; their 12-month trough declines in our sample do not cross −10 percent on the middle-tier single-family ZHVI series. A 20 percent threshold, which does find some sun-belt markets, has only five positive rows in the test set (all Clarksdale) and is not interpretable.

## 4. Results

**Primary specification** (L2 logistic on 10 safe features; class-balanced; 1:5 propensity weighting; temporal holdout 2022-07 onward):

> Test-set PR-AUC 0.0439, 95 percent metro-clustered block bootstrap CI [0.015, 0.115]; within-metro block-permutation p = 0.493; single-feature momentum baseline PR-AUC 0.076 > model PR-AUC; largest leave-one-out drop = 39 percent from removing Clarksdale, Mississippi.

**Conclusion**: we cannot reject the hypothesis that metro-level 12-month housing-crash prediction from public data has no true out-of-sample power. The apparent signal is mechanically driven by momentum persistence and concentrated in ~2 distressed rural markets. The five-fold jump in base rate between training and test is real and reflects the 2022-23 rate-shock cycle, but no feature in the public panel gives a cross-sectional early warning beyond "markets falling now will keep falling."

## 5. How this compares to prior literature

The null finding aligns with the sceptical side of the early-warning literature. Gourinchas-Obstfeld (2012) and Schularick-Taylor (2012) report that crisis-prediction models rarely generalise out-of-sample even with decades of data and broad macro panels. Beutel, List, and von Schweinitz (2019) show that machine-learning early-warning models underperform simple credit-gap rules out-of-sample on cross-country panels. The literature that claims strong metro-level crash prediction (Kaminsky-Reinhart style early warning applied to housing) typically reports in-sample or retrospectively-tuned results; this paper is the first we know of to apply metro-cluster bootstrap and within-panel block-permutation jointly to a metro-level US housing early-warning model and to report the resulting p-value.

The positive side of the literature (e.g. Himmelberg-Mayer-Sinai 2005 on price-to-income ratios; Glaeser-Gyourko 2005, 2010 on supply elasticity as a crash-depth moderator) is not contradicted — those papers explain cross-sectional *variance in crash depth given that a crash occurs*, which is different from predicting *which markets will cross a threshold first* in an out-of-sample window.

## 6. Limitations

1. **Outcome definition is threshold-dependent.** The 10 percent / 12-month threshold is one of many reasonable choices. Higher thresholds (15 percent, 20 percent) find only a handful of markets per cycle; lower thresholds (5 percent) make the outcome too easy. No threshold we tested produced a model whose diagnostic properties differed materially.

2. **Inventory features only exist from 2016-07.** We cannot train on the 2006-09 housing cycle with the same feature set. A deep-history secondary model using ZHVI momentum + mortgage rate only, trained on 2000-2015 and tested on 2022-23, produces similar diagnostics.

3. **Public metro-level data is substantially coarser than the literature's best identification designs.** Studies that claim clean causal identification (e.g. Mian-Sufi 2009 on credit supply, Kerr-Lerner-Schoar 2014 on admission thresholds) use merchant-record or regulatory-register data not available to public researchers. Our null is conditional on the public feature set being the only available feature set; it does not imply that no predictive power exists in any private dataset.

4. **Test window of 18 months is short and contains one regime shift.** The 2022-23 rate-shock cycle is the dominant macro event in the test set. A longer out-of-sample window with at least two distinct cycles would be a stronger test.

5. **Crashing-market population mixes two different phenomena.** Secular rural decline (Clarksdale, Johnstown) and cyclical housing crash (Boise, Ukiah) both produce ≥10 percent 12-month declines but have very different causal structures. A crash-prediction study that discriminated between them would need metro classification metadata we did not use.

## 7. Files and reproducibility

All code, data, and results in `applications/housing_crashes/`:

- `data/zillow_zhvi_metro.csv` — Zillow ZHVI (public CSV)
- `data/realtor_inventory_metro.csv` — Realtor.com monthly metro inventory (public S3)
- `data/fred_mortgage_30yr.csv` — FRED 30-year fixed mortgage (public CSV)
- `data/panel.parquet` — joined metro-month panel (50,134 rows)
- `loaders.py` · `build_panel.py` · `evaluate.py`
- `run_e00.py` · `run_phase1_tournament.py` · `hdr_loop.py`
- `results.tsv` — every experiment row with bootstrap CIs where applicable
- `tests/` — passing pytest tests

## 8. Summary

We asked whether metro-level housing crashes — defined as 10 percent / 12-month ZHVI declines — can be predicted from publicly-available data in the 2022-23 US cycle. The answer is no:

1. A regularised logistic model achieves a headline 4.7× PR-AUC lift out-of-sample.
2. Every honest inference procedure we tried — metro-clustered bootstrap, block permutation, single-feature dominance check, leave-one-metro-out — dissolves this signal.
3. A one-feature momentum score (past 12-month ZHVI return) produces a better test-set PR-AUC than the full model.
4. The markets that do cross the threshold are mostly distressed rural micropolitans whose decline is secular rather than cyclical.

The practical implication: industry and media claims that "housing-market early-warning models" reliably flag which metros crash first are not supported by the public data. The methodological contribution: any such claim should be accompanied by a metro-clustered block bootstrap, a within-metro block-permutation p-value, and a single-feature dominance check. Without all three, apparent predictive power is likely an artefact of within-metro autocorrelation plus a handful of influential markets.
