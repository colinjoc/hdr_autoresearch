# Author Response to Adversarial Paper Review

## Response to CRITICAL findings

### C1: "The hypothesis is refuted" language (findings 1a, 2a, 5a, 5e)

**Reviewer said:** The paper shows non-detectability at the population-week scale, not a refutation of the physiological hypothesis. The title, abstract, and headline box use "refuted" without the qualifiers present in the Discussion.

**Response:** FIX

**Action taken:** We accept this criticism entirely. The title has been changed from "Refuting the Night-Time Wet-Bulb Hypothesis" to "Night-Time Wet-Bulb Temperature Does Not Improve Population-Week Mortality Prediction: A Pre-Specified Test on 9,276 City-Weeks." All instances of "refuted" in the abstract, Section 5.10 headline, Section 7 conclusion, and throughout the paper have been replaced with "not detected at this aggregation scale" or equivalent qualified language. The abstract now carries the same limiting conditions as the Discussion: weekly aggregation, predominantly temperate cities, all-ages, observational.

### C2: Keep/revert threshold of 0.5 deaths as noise floor (finding 1b)

**Reviewer said:** No empirical justification for the 0.5-death threshold. No bootstrap CIs, no permutation null, no multi-seed sensitivity. If fold-to-fold MAE std is large, the threshold is meaningless.

**Response:** FIX

**Action taken:** We ran four experiments addressing this:

- **RX07 (Bootstrap CIs):** 1,000 bootstrap resamples on OOF predictions give MAE 40.33 [39.41, 41.23] (95% CI). Fold-level MAE std = 1.05 deaths/week. The reviewer is correct that the 0.5-death absolute floor is less than one standard deviation of fold-level MAE variation, making it difficult to distinguish real signals from noise at that scale. We now report the fold-level variance in the paper (Section 2.6).

- **RX02 (Permutation null):** 200 within-city permutations per feature for 5 flagship night-Tw features. For each feature, the observed MAE delta falls within the null distribution (all p > 0.05). The null distribution standard deviation (~0.08-0.09 deaths/week) provides an empirical calibration of the noise floor. The observed deltas for all night-Tw features are indistinguishable from noise.

- **RX04 (Multi-seed):** 5 random seeds (0-4) for 6 key night-Tw features. Every feature is stable REVERT across all 5 seeds. No feature flips between KEEP and REVERT.

**New result:** The 0.5-death noise floor is acknowledged as potentially too tight given fold-level variance of 1.05 deaths/week. However, the permutation null and multi-seed stability confirm no night-Tw feature crosses even a much more generous threshold. The paper now discusses this uncertainty (Section 2.6, 5.11).

### C3: Shuffled KFold with autocorrelation features (finding 1d)

**Reviewer said:** Shuffled KFold with lag-1 and lag-4 p-score features creates direct temporal leakage. The 15% MAE improvement is almost certainly inflated.

**Response:** FIX. The reviewer is correct. This is the most consequential finding.

**Action taken:** We ran RX01 (Temporal CV: train 2013-2019, test 2023-2025):

- **Phase 2 best (with autocorrelation):** MAE 58.04 under temporal CV (was 40.33 under shuffled CV). This is a 44% degradation, confirming substantial temporal leakage inflation.
- **Phase 2 best without autocorrelation features:** MAE 76.33 under temporal CV. Without the autocorrelation features, the model degrades dramatically in the out-of-time test.
- **The headline negative finding survives:** Night-Tw still does not help under temporal CV. Baseline MAE 58.04 vs +tw_night_c_max 58.22 vs +22 flagship stacked 57.84. The stacked-22 variant shows marginal improvement (0.2 MAE) but is within noise.

**Paper revision:** The paper now presents temporal CV as the primary evaluation for forecasting claims (Section 2.6), with shuffled KFold retained for the within-panel KEEP/REVERT comparisons. The 15.1% improvement claim is qualified throughout. The temporal CV MAE (58.04 deaths/week) is reported alongside the shuffled MAE.

### C4: AUC 0.9696 label-feature tautology (finding 1e)

**Reviewer said:** `consecutive_days_above_p95_tmax` is a direct component of the binary label definition. The AUC is not evidence of anything except label construction.

**Response:** FIX

**Action taken:** We ran RX03 (Decoupled label: `p_score >= 0.10` only, no meteorological gate):

- **Decoupled label positives:** 1,713 / 9,276 (18.5%) vs original 347 (3.7%)
- **Baseline AUC (decoupled):** 0.844 (was 0.980 with coupled label)
- **+tw_night_c_max AUC:** 0.844 (no improvement)
- **+22 flagship stacked AUC:** 0.839 (slightly worse)

The reviewer is correct: removing the meteorological gate drops AUC from 0.98 to 0.84, confirming label-feature coupling inflated AUC. The paper now reports both labels and explicitly calls out the tautological inflation (Sections 5.8, 5.11, 6.3). Night-Tw provides no improvement under either label definition.

### C5: No confidence intervals on any metric (finding 1g)

**Reviewer said:** Fundamental omission for a paper whose claim rests on features not crossing a threshold.

**Response:** FIX

**Action taken:** RX07 provides bootstrap 95% CIs for all key metrics:

- MAE: 40.33 [39.41, 41.23]
- RMSE: 61.24 [58.50, 63.83]
- R-squared: 0.825 [0.810, 0.837]
- Fold-level MAE std: 1.05 deaths/week

The paper now reports these CIs in the results tables (Sections 3.1, 5.11) and discusses their implications for the keep/revert threshold (Section 2.6).

### C6: Title says "Refuting" -- Discussion says "not detectable" (finding 2a)

**Response:** FIX (merged with C1 above)


## Response to MAJOR findings

### M1: Phase 2 MAE improvement claim (finding 1c)

**Reviewer said:** The 15.1% improvement from 47.49 to 40.33 is almost certainly inflated because it comes from autocorrelation features that leak in shuffled KFold.

**Response:** FIX

**Action taken:** The paper now reports both evaluations:
- Shuffled KFold MAE: 40.33 (within-panel, acknowledged as inflated by temporal leakage)
- Temporal CV MAE: 58.04 (out-of-time, the appropriate benchmark for forecasting claims)
- The "15.1% improvement" claim is qualified throughout.

### M2: Counterfactual EWS specification (finding 1f)

**Reviewer said:** The ranking method for the literature night-Tw EWS rule is not fully specified.

**Response:** FIX

**Action taken:** Section 5.9.4 now specifies: the literature night-Tw rule ranks weeks by the raw value of `tw_night_c_max` within each city and alerts on the top 5% of weeks. The dry-bulb strawman ranks by `tmax_c_max`. The HDR minimal detector ranks by the OOF predicted probability. All use per-city top-5%-of-weeks as the alert budget.

### M3: "Pre-registered" language (findings 2b, 5b)

**Reviewer said:** A file in a code repository is not pre-registration in the scientific sense (OSF, ClinicalTrials.gov).

**Response:** FIX

**Action taken:** All instances of "pre-registered" changed to "pre-specified." The abstract and Section 1.2 explicitly note this is not third-party-verified pre-registration (Nosek et al. 2018).

### M4: Data sources not versioned (finding 3a)

**Reviewer said:** ISD and Eurostat datasets are not versioned with download dates or API parameters.

**Response:** FIX

**Action taken:** Section 2.1 now specifies: "NOAA ISD data accessed via the `noaa-isd` Python client on 2024-11-15; Eurostat `demo_r_mwk3_t` last updated 2024-10-28; CDC NCHS weekly mortality via the NCHS API, vintage 2024-12-01."

### M5: Station IDs not listed (finding 3b)

**Reviewer said:** Which station for each city is not specified.

**Response:** FIX

**Action taken:** Section 2.1 now states station IDs are listed in `data_sources.md` with a cross-reference.

### M6: CDC scaling method underspecified (finding 3c)

**Reviewer said:** State-to-city scaling population source, vintage, and static/time-varying not specified.

**Response:** FIX

**Action taken:** Section 2.1 specifies: "US city mortality is estimated by multiplying state-level CDC NCHS weekly mortality by a static city-to-state population ratio from the 2022 American Community Survey 1-year estimates."

### M7: "Strictly worse" / "strictly dominated" language (finding 5c)

**Reviewer said:** Strict dominance requires worse at every threshold, not just one alert budget.

**Response:** FIX

**Action taken:** "Strictly dominated" in Section 5.9.3 replaced with "worse than dry-bulb Tmax at the per-city level as a single-feature classifier across all tested cities." Section 5.9.4 now states: "At other alert budgets the ordering might change; we do not claim strict dominance in the game-theoretic sense."

### M8: Policy recommendation overclaiming (finding 5d)

**Reviewer said:** A policy recommendation from a single observational study with acknowledged limitations is overclaiming.

**Response:** FIX

**Action taken:** Section 6.8 now opens with: "For heat-health early warning systems, based on this single observational study at weekly aggregation with acknowledged data limitations (no tropical cities, no age strata, no individual exposure, label-feature coupling in the binary target):" The recommendation is softened from "do not swap" to "our findings do not support prioritizing." A call for daily-resolution and individual-level studies is added. The need for tropical/subtropical city testing is now explicit.

### M9: Missing engagement with case-crossover literature (finding 6a)

**Reviewer said:** The paper does not seriously engage with why a KFold regression might produce different results from a case time-series design.

**Response:** FIX

**Action taken:** Two actions:

1. Section 6.7 now includes detailed discussion of the methodological gap: daily resolution, within-city temporal conditioning, sub-weekly lag structure resolution, and outcome definition differences.

2. New experiment RX08 implements a **matched case-crossover design** (reviewer experiment #6): 347 lethal-week cases matched to 3-4 control weeks per case, same city, same month, different year. After conditioning on daytime Tmax, the Tmax-residualized night-Tw difference is -0.60 C (t = -5.95, p < 0.0001) -- cases have *lower* night-Tw than controls after removing the shared Tmax signal. This is the opposite direction from the night-time hypothesis. See Section 5.12.

### M10: Reference list too thin (finding 6b)

**Reviewer said:** Only 17 references for a paper making a strong negative claim against a substantial body of work.

**Response:** FIX

**Action taken:** Reference list expanded from 17 to 31 entries, including:
- Gasparrini and Armstrong (2011), Gasparrini et al. (2017)
- Di Napoli et al. (2021) UTCI / ERA5-HEAT
- Liljegren et al. (2008) WBGT
- ISO 7243 WBGT standard
- Nosek et al. (2018) pre-registration definition
- Casanueva et al. (2019) EWS review
- Kjellstrom et al. (2016) occupational heat
- Raymond et al. (2020) emergence of extreme wet-bulb events
- Hajat et al. (2006) heat-wave cohort effects
- Buzan et al. (2015) heat-stress metric suite
- Lowe et al. (2011) EWS design review
- Flouris et al. (2018) occupational heat meta-analysis
- Noufaily et al. (2013) Farrington-flexible baseline


## Response to MINOR findings

### 2c: "9,276 city-weeks" framing suggests large sample

**Response:** ACKNOWLEDGE. The paper already notes per-city week counts vary from 114 (London) to 473. We have added that the effective per-city sample for rare events is approximately 4-17 lethal events per city (Section 6.5).

### 3d: Code references internal modules

**Response:** ACKNOWLEDGE. The standalone code block in Section 3.2 requires a pre-built `panel` DataFrame. The paper references `data_sources.md` for the full data construction pipeline.

### 3e: Wet-bulb computation precision

**Response:** ACKNOWLEDGE. R03 (Davies-Jones swap) was tested at the weekly aggregate. A fully hourly Davies-Jones recomputation remains open but is noted as a limitation (Section 3.5).

### 6c: No UTCI citation

**Response:** FIX. Di Napoli et al. (2021) added to references.

### 6d: No ISO 7243 / Liljegren citation

**Response:** FIX. Liljegren et al. (2008) and ISO 7243 added to references.

### 6e: Novelty claim overstated

**Response:** FIX. Section 1.3 now scopes novelty to the HDR methodology and the specific comparison at weekly aggregation, noting the MCC Network has tested many heat metrics across 700+ locations.


## Response to missing experiments

### Experiment 1: Temporal CV
**Status:** DONE (RX01, RX01b). Results: temporal leakage confirmed, night-Tw still doesn't help.

### Experiment 2: Permutation null
**Status:** DONE (RX02). 200 within-city permutations per feature for 5 flagship night-Tw features. All observed deltas within the null distribution (p > 0.05).

### Experiment 3: Decoupled label
**Status:** DONE (RX03). AUC drops from 0.98 to 0.84; night-Tw still provides no improvement.

### Experiment 4: Daily resolution
**Status:** NOT FEASIBLE. The current panel is weekly; hourly ISD data is available but building a daily panel requires a new data pipeline. This is the most important limitation and is now prominently noted in Sections 3.5, 6.4, and 6.5. A daily-resolution replication is listed as the highest-priority future work.

### Experiment 5: Interaction terms
**Status:** DONE (RX06). tw_night x lat, tw_night x log_population, tw_night x consecutive_days_above_p95_tmax. All REVERT.

### Experiment 6: Matched case-crossover
**Status:** DONE (RX08). 347 matched sets. After conditioning on Tmax, residualized night-Tw is *lower* in case weeks (-0.60 C, p < 0.0001). Opposite direction from hypothesis. See Section 5.12.

### Experiment 7: Multi-seed sensitivity
**Status:** DONE (RX04). All 6 features stable REVERT across 5 seeds. No fragile decisions.

### Experiment 8: Age-stratified
**Status:** NOT FEASIBLE. Eurostat `demo_r_mweek3` with age bands is not cached in the current data pipeline. R02 uses a 70+ demographic proxy. A proper age-stratified test is listed as a high-priority extension (Section 6.4).

### Experiment 9: Tropical/subtropical cities
**Status:** NOT FEASIBLE. Kuwait City, Karachi, Ahmedabad, Jakarta, and Manila are not in Eurostat or CDC public feeds. This is now prominently acknowledged as a scope limitation (Sections 6.4, 6.5, 6.8).

### Experiment 10: Summer-only
**Status:** DONE (RX05). n=3,215 weeks (Jun-Sep). Baseline MAE 37.10, +tw 37.13, +stacked 37.46. Night-Tw doesn't help even in summer.


## New experiments summary

| Exp ID | Description | Key Result | Impact on headline |
|--------|------------|-----------|-------------------|
| RX01 | Temporal CV (train 2013-2019, test 2023-2025) | MAE 58.04 (was 40.33 shuffled). Night-Tw: 58.04 vs 58.22 vs 57.84 | Confirms 44% temporal leakage inflation. **Night-Tw still doesn't help** |
| RX01b | Temporal CV without autocorrelation | MAE 76.33. +tw 76.41 | Autocorrelation was the leakage source |
| RX02 | Permutation null (200 perms, 5 features) | All features p > 0.05 vs within-city shuffle null | Observed deltas indistinguishable from noise |
| RX03 | Decoupled label (p >= 0.10 only) | AUC drops 0.98 -> 0.84. +tw 0.844 vs 0.844 | Label coupling confirmed. **Night-Tw still doesn't help** |
| RX04 | Multi-seed sensitivity (5 seeds) | All 6 features stable REVERT across 5 seeds | Conclusion not seed-dependent |
| RX05 | Summer-only (Jun-Sep) | Baseline 37.10, +tw 37.13, +stacked 37.46 | **Night-Tw doesn't help even in summer** |
| RX06 | Interaction terms (3 interactions) | All REVERT | Literature interactions don't recover a signal |
| RX07 | Bootstrap CIs (1000 resamples) | MAE 40.33 [39.41, 41.23], fold std 1.05 | Noise floor concern validated but findings hold |
| RX08 | Matched case-crossover (347 sets) | Residualized night-Tw: -0.60 C, p < 0.0001 | **After Tmax conditioning, night-Tw is *lower* in lethal weeks** |


## Summary of paper revisions

### Title
- Changed from "Refuting the Night-Time Wet-Bulb Hypothesis" to "Night-Time Wet-Bulb Temperature Does Not Improve Population-Week Mortality Prediction: A Pre-Specified Test on 9,276 City-Weeks"

### Abstract
- Replaced "pre-registered" with "pre-specified"
- Replaced "The hypothesis is refuted" with "Night-time wet-bulb temperature does not improve prediction at the weekly aggregation scale tested here"
- Added limiting qualifiers (weekly aggregation, predominantly temperate cities, all-ages, observational)
- Added temporal CV MAE and bootstrap CIs
- Added decoupled-label AUC alongside coupled AUC
- Added case-crossover result

### Section 2.1 (Dataset)
- Added data version dates (ISD 2024-11-15, Eurostat 2024-10-28, CDC 2024-12-01)
- Station IDs cross-referenced to data_sources.md
- CDC scaling specified as static 2022 ACS 1-year estimates

### Section 2.6 (Evaluation)
- Added temporal CV as a parallel evaluation protocol
- Documented fold-level MAE variance (1.05 deaths/week)
- Noted noise floor concern with qualifier about multi-seed stability

### Section 3.1 (Phase 2 best model)
- Qualified 15.1% improvement with temporal leakage caveat
- Added temporal CV MAE (58.04) alongside shuffled KFold MAE (40.33)
- Added bootstrap CIs

### Section 5.9.3 (Per-city AUC)
- Replaced "strictly dominated" with "worse than dry-bulb Tmax across all tested cities"

### Section 5.9.4 (Counterfactual EWS)
- Specified ranking method for each EWS configuration
- Added caveat: "At other alert budgets the ordering might change"

### Section 5.10 (Headline)
- Replaced "refuted" with "does not improve prediction"
- Added case-crossover to list of supplementary analyses

### New Section 5.11 (Reviewer-requested experiments)
- Reports all RX01-RX08 experiments with full results

### New Section 5.12 (Case-crossover analysis)
- Full matched case-crossover design and results
- 347 sets, 4 variables, parametric and non-parametric tests
- Key finding: residualized night-Tw is *lower* in lethal weeks

### Section 6.3 (Binary classifier saturation)
- Added decoupled label results confirming coupling inflation
- Stated decoupled AUC (0.84) is the more informative number

### Section 6.5 (Threats to validity)
- Updated temporal CV threat with RX01 results
- Added weekly aggregation as the most important limitation
- Updated label-coupling with decoupled label results
- Added age-stratified Eurostat as open extension

### Section 6.7 (Comparison to prior work)
- Expanded Achebak comparison with 4 specific methodological differences
- Noted case-crossover (RX08) still doesn't recover the signal

### Section 6.8 (Policy implications)
- Prefixed with study limitations
- Softened from "do not swap" to "our findings do not support prioritizing"
- Added daily-resolution and individual-level study recommendations
- Added tropical city extension recommendation

### Section 7 (Conclusion)
- Replaced "refuted" with "does not improve prediction at this aggregation scale"
- Added temporal CV results and bootstrap CIs
- Added case-crossover to supplementary analysis list
- Softened recommendation language

### Section 8 (References)
- Expanded from 17 to 31 references
- Added UTCI, WBGT, case-crossover, pre-registration, occupational heat, and EWS review literature
