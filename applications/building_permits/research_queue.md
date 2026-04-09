# Research queue — building permit processing times

Pre-registered Phase 2 single-change hypotheses for the HDR loop. Each hypothesis is one-thing-off-the-previous-best. Bracketed numbers are row IDs in `papers.csv`.

Priors are rough probabilities that the single change beats the previous best by more than the noise floor (estimated roughly as +/- 1 day MAE or +/- 0.005 R2 on the held-out cohort). Very high priors (>= 0.80) are reserved for changes that are nearly mechanically forced by the data structure (e.g. adding an obviously load-bearing timestamp that exists in the raw cache but is missing from the baseline feature set).

Target metrics (pinned at Phase 0.5 end):
- Primary: MAE of predicted `duration_days` on the 1-2 family new-construction holdout.
- Secondary: concordance index (C-index) for survival models that use right-censoring.
- Tertiary: per-city per-year calibration (P50 and P90 quantile loss).

Baseline assumed for these priors: XGBoost regressor on the normalised `data_loaders.py` schema restricted to (city, filed_year, filed_month, permit_subtype, log(valuation_usd), log(unit_count+1), log(square_feet+1)) trained on issued permits (right-censoring dropped), target `log(duration_days+1)`.

Categories (numbered 1-16) follow the specification in the parent task.

Hypotheses are ordered highest-prior first within a high-level band and then grouped thematically.

---

## Band A — almost-forced wins (prior >= 0.80)

## H001: swap baseline to XGBoost-AFT with right-censoring
- **Prior**: 0.88
- **Mechanism**: Current baseline drops right-censored cases ("still open at extraction") entirely. The SF 1,489-day backlog [83] and Seattle `daysoutcorrections=825` outliers [14 in data_sources] show that the slowest cases are precisely the ones censored out. XGBoost AFT [127] fits a gradient-boosted Accelerated Failure Time loss that correctly handles right-censoring, and the censored rows carry the most signal about the tail. Scikit-survival [128] and lifelines [129] document the standard benchmark pattern where AFT beats log-MSE on heavy-tailed duration data.
- **Single change**: replace XGBoost regressor with `xgboost.XGBRegressor(objective='survival:aft', aft_loss_distribution='normal')`, include censored rows with `label_lower_bound=(today - filed_date)`, `label_upper_bound=+inf`.
- **Expected effect**: -4 to -8 days MAE on the heavy-tail quantiles; +0.02 C-index.
- **Phase**: Phase 2 single-add.

## H002: add Seattle per-cycle `numberreviewcycles` as a direct feature
- **Prior**: 0.90 (Seattle only)
- **Mechanism**: `numberreviewcycles` is the single most mechanically load-bearing feature in the entire data inventory. Process-mining of BPIC 2015 [102, 103, 107] identified correction loops as the dominant controllable delay. Austin's expedited-program documentation [338] reports 10 business days per round, so a 4-cycle permit is roughly 40 business days of review time on top of the baseline. The Seattle raw parquet cache already exposes `numberreviewcycles` [tqk8-y2z5] but `load_seattle()` collapses it away before returning the normalised frame.
- **Single change**: add `numberreviewcycles` (max over reviewtypes) as a column on the Seattle slice.
- **Expected effect**: -15 to -25 days MAE on Seattle holdout; baseline R2 likely jumps +0.15 or more on Seattle.
- **Phase**: Phase 2 single-add.

## H003: add Seattle `daysoutcorrections` as a direct feature
- **Prior**: 0.88 (Seattle only)
- **Mechanism**: The Seattle Plan Review dataset ships a pre-computed `daysoutcorrections` field that directly attributes waiting time to applicant turnaround between correction cycles. A single Seattle SFR in the documentation had `daysoutcorrections=825` on a total `totaldaysplanreview=1015` [data_sources.md section 14]. This is the largest single duration component in the dataset; the baseline currently has no way to see it. Literature context: Little's Law bookkeeping [116, 117] makes waiting time additive with service time and the BPIC 2015 analysis [107] isolated "time with applicant" as distinct from "time with reviewer".
- **Single change**: add `daysoutcorrections` (max over reviewtypes) as a feature on the Seattle slice.
- **Expected effect**: -20 to -40 days MAE on Seattle holdout.
- **Phase**: Phase 2 single-add.

## H004: add intake-to-plan-check-start lag feature for NYC legacy
- **Prior**: 0.85
- **Mechanism**: NYC's `ic3t-wcy2` exposes `pre__filing_date`, `paid`, `fully_paid`, `approved`, `fully_permitted`, `signoff_date` — six ordered timestamps [data_sources.md section 2]. The baseline only uses `filed` and `issued`. The `paid -> fully_paid -> approved` sub-pipeline has its own queue semantics and the NYC Bureau-of-Standards-and-Appeals literature [133, 134] and process-mining theory [87, 95] both predict these hand-off waits are heterogeneous. `paid - pre_filing_date` specifically captures fee-processing lag.
- **Single change**: add `paid_lag_days = (paid - pre__filing_date).days` and `fully_paid_lag_days = (fully_paid - paid).days` to the NYC pipeline.
- **Expected effect**: -3 to -6 days MAE on NYC holdout.
- **Phase**: Phase 2 single-add.

## H005: add NYC approved-to-fully-permitted lag
- **Prior**: 0.82
- **Mechanism**: Same dataset as H004. The gap between `approved` (plan-check complete) and `fully_permitted` (permit issued) is a pure administrative / fee-collection / sign-off queue. Empirically in NYC these are rarely the same day; this gap is exactly the kind of inter-agency hand-off wait that BPIC 2015 [107] highlighted as a bottleneck source.
- **Single change**: add `approve_to_issue_days = (fully_permitted - approved).days` as a feature for NYC.
- **Expected effect**: -3 to -5 days MAE on NYC.
- **Phase**: Phase 2 single-add.

## H006: add SF `approved_date - filed_date` as a feature
- **Prior**: 0.84
- **Mechanism**: The SF `i98e-djp9` dataset exposes `filed_date`, `approved_date`, `issued_date`, `last_permit_activity_date` [data_sources.md section 1]. The baseline target is `issued - filed` but a separable pre-approval bucket captures the discretionary-review + plan-check portion independently from the post-approval fee/issuance bucket. Elmendorf [30, 281] argues SF's pre-approval bucket is where the discretionary-review drag lives.
- **Single change**: add `pre_approval_days = (approved_date - filed_date).days`, `post_approval_days = (issued_date - approved_date).days` as features.
- **Expected effect**: useful as a leak feature for `issued_date`; use carefully as a decomposition rather than prediction input. Switch to splitting target into two survival models instead (H007).
- **Phase**: Phase 2 single-add.

## H007: decompose target into pre-approval and post-approval survival models
- **Prior**: 0.80
- **Mechanism**: Motivated by H006. Rather than predicting `issued - filed` directly, fit two separate models: pre-approval duration and post-approval duration. This matches the canonical two-stage tandem queue literature [113, 115] and Little's Law decomposition [116, 117]. Cross-city comparability improves because the post-approval stage is mostly fee/bookkeeping and the pre-approval stage is where the political-economy drag lives.
- **Single change**: train two XGBoost models instead of one; final prediction is sum.
- **Expected effect**: -5 to -10 days MAE by removing post-approval noise from the pre-approval prediction problem.
- **Phase**: Phase 2.5 composition.

## H008: drop sentinel dates before 2000-01-01
- **Prior**: 0.90
- **Mechanism**: SF's `filed_date` minimum is 1901-03-10, which the DBI documentation marks as a placeholder sentinel [data_sources.md section 1, data_acquisition_notes.md]. Training on rows with placeholder filing dates produces 40,000+ day durations that dominate the loss and force the model to regress toward the mean. Simple data-hygiene fix.
- **Single change**: add filter `df.filed_date >= pd.Timestamp("2000-01-01")` before training.
- **Expected effect**: -2 to -5 days MAE by removing sentinel-driven outliers.
- **Phase**: Phase 2 single-add.

## H009: clip durations to [1, 2000] days
- **Prior**: 0.86
- **Mechanism**: `data_acquisition_notes.md` recommends this filter for the baseline. Negative durations indicate date-column swaps or data entry errors; durations above 2000 days are almost always sentinel or withdrawn-then-reinstated cases [data_acquisition_notes.md section "Filter to comparable projects"]. The 2000-day upper cap is consistent with the SF 1,489-day outlier [83] being near but not above the cap.
- **Single change**: `df = df[(df.issued_date - df.filed_date).dt.days.between(1, 2000)]` before training.
- **Expected effect**: -3 days MAE on any city where the baseline currently sees negative durations.
- **Phase**: Phase 2 single-add.

## H010: use `revised_cost` with fallback to `estimated_cost` in SF
- **Prior**: 0.80
- **Mechanism**: SF's valuation ships as two fields: `estimated_cost` (at filing) and `revised_cost` (updated during plan check) [data_sources.md section 1]. The loader does `_money(raw, "revised_cost").fillna(_money(raw, "estimated_cost"))`, which is correct. But there is a further step: the *delta* between the two is itself informative (large upward revisions indicate complex plan checks). This is already present in the loader at the fillna step; the improvement is adding the delta as a separate feature.
- **Single change**: add `valuation_delta_usd = revised_cost - estimated_cost` as a feature on SF.
- **Expected effect**: -1 to -3 days MAE on SF.
- **Phase**: Phase 2 single-add.

---

## Band B — strong priors (0.60-0.79)

## H011: log-transform valuation
- **Prior**: 0.78
- **Mechanism**: Valuation ranges from hundreds of dollars (repair permits) to tens of millions (large multifamily) and is heavy-tailed. Log-transformation is standard in housing-cost models [1, 5, 7, 21] and compresses the range to something that additive trees can split efficiently. Monotonicity: higher valuation should not *reduce* processing time (per H033).
- **Single change**: feature `log1p_valuation_usd = log(1 + valuation_usd)`, drop raw.
- **Expected effect**: -1 to -3 days MAE.
- **Phase**: Phase 2 single-add.

## H012: log-transform unit count
- **Prior**: 0.76
- **Mechanism**: Same reasoning as H011. Unit count is 1, 2, 3, 5, 20, 200 — integer-valued with a heavy tail. Saiz (2010) [1] and Gyourko et al. [2, 3] use log measures throughout. Low-unit-count permits have different pipeline physics (small residential track) than high-unit-count permits (full commercial plan check).
- **Single change**: feature `log1p_unit_count = log(1 + unit_count)`, drop raw.
- **Expected effect**: -1 to -2 days MAE.
- **Phase**: Phase 2 single-add.

## H013: log-transform square footage
- **Prior**: 0.74
- **Mechanism**: Same as H011 and H012. Florida HB 267 [56] explicitly uses 7,500 sqft as the cutoff for 30-day mandatory processing, so there is a known institutional breakpoint in the distribution. Log compresses the long tail.
- **Single change**: feature `log1p_square_feet = log(1 + square_feet)`, drop raw.
- **Expected effect**: -1 day MAE.
- **Phase**: Phase 2 single-add.

## H014: add filed day-of-week
- **Prior**: 0.70
- **Mechanism**: Government agencies run Monday-Friday; Monday filings begin service that day while Friday filings wait at least two calendar days. Classical tandem queue theory [113, 114, 330] makes this an arrival-timing offset that propagates through the entire service chain.
- **Single change**: feature `filed_dow = filed_date.dayofweek`, one-hot or ordinal.
- **Expected effect**: -0.5 to -2 days MAE.
- **Phase**: Phase 2 single-add.

## H015: add filed month of year
- **Prior**: 0.72
- **Mechanism**: Permit offices experience seasonal workload spikes; summer construction season loads the pipeline and winter unloads it. M/M/c with time-varying arrivals [115] predicts non-linear wait sensitivity to load. Mayer & Somerville [14] show steady-state permit volumes shift seasonally.
- **Single change**: feature `filed_month = filed_date.month`, cyclic encoding with `sin(2*pi*m/12)`, `cos(2*pi*m/12)`.
- **Expected effect**: -1 day MAE.
- **Phase**: Phase 2 single-add.

## H016: add filed year as ordinal
- **Prior**: 0.80
- **Mechanism**: Pipeline backlogs evolve over time (SF has grown, Austin has shrunk post-HOME). Glaeser and Gyourko's regulatory-tax framing [5, 7, 8] is implicitly time-varying. Many California reforms have distinct before/after effects [41, 42]. An ordinal year feature lets the model place each permit on the correct part of the SF-drag or Austin-improvement curve.
- **Single change**: feature `filed_year = filed_date.year`.
- **Expected effect**: -2 to -4 days MAE, especially on SF where the 2019-2025 trend is steep.
- **Phase**: Phase 2 single-add.

## H017: add US federal holiday flag
- **Prior**: 0.60
- **Mechanism**: Permit offices close on federal holidays. A filing made in the week of Thanksgiving or the week of New Year has an extra non-working slice before it enters service. Calendar-day durations include these as waiting time whether or not the system was actually able to work on them.
- **Single change**: feature `filed_in_holiday_week = filed_date is within 3 days of US federal holiday`.
- **Expected effect**: -0.5 to -1 day MAE.
- **Phase**: Phase 2 single-add.

## H018: add filed-quarter COVID era flag
- **Prior**: 0.74
- **Mechanism**: March 2020 - June 2021 permit offices moved to remote work, plan check digitised in rushed fashion, inspectors were furloughed. Chicago [180, 339] and NYC [190] both had documented IT disruptions. Mercatus [51-57] and Pew [58, 59, 60] tracking confirm 2020-2022 produced a structural break in processing statistics.
- **Single change**: feature `covid_era = 1 if 2020-03-01 <= filed_date <= 2021-06-30 else 0`.
- **Expected effect**: -1 to -2 days MAE.
- **Phase**: Phase 2 single-add.

## H019: add per-city mean encoding of permit_subtype
- **Prior**: 0.72
- **Mechanism**: `permit_subtype` is high-cardinality string (hundreds of values in SF alone). One-hot encoding is sparse; a target-encoding scheme where subtype is mapped to the city-specific mean duration is more informative. Standard tabular-ML technique for high-cardinality categoricals [Micci-Barreca, 2001, referenced widely in tree-based benchmarks].
- **Single change**: replace `permit_subtype` one-hot with per-city K-fold mean encoding.
- **Expected effect**: -2 to -4 days MAE.
- **Phase**: Phase 2 single-add.

## H020: add neighborhood as high-cardinality categorical with target encoding
- **Prior**: 0.70
- **Mechanism**: Open question #5 in the literature review identifies neighbourhood-level variance as larger than some city-pair variance. Historic districts, community board culture, recent development conflict, and individual planner workload produce neighborhood-specific drags. SF's `neighborhoods_analysis_boundaries` [data_loaders.py sf], NYC's `gis_nta_name`, Austin's `council_district`, LA's `cpa`, Portland's `NEIGHBORHOOD` are all exposed.
- **Single change**: add target-encoded neighborhood as a feature, using K-fold mean encoding.
- **Expected effect**: -3 to -6 days MAE.
- **Phase**: Phase 2 single-add.

## H021: per-city model instead of single global XGBoost
- **Prior**: 0.72
- **Mechanism**: SF's 280-day median [83] and Austin's 91-day median [83] differ by a factor of 3; a single model must route heavy trees to city indicator before it can model anything else, and feature interactions are diluted. Separate per-city models preserve the full feature space for each city's dynamics. Trade-off: smaller training sets per model, harder to borrow strength.
- **Single change**: fit one XGBoost per city; score on city-specific holdouts.
- **Expected effect**: -2 to -5 days MAE for cities with large samples (NYC, SF); could be +1 day for cities with small samples (Seattle).
- **Phase**: Phase 2.5 composition.

## H022: city-specific dispatch ensemble
- **Prior**: 0.70
- **Mechanism**: Stacking H021 and the global baseline. Global model provides stable mean; per-city model provides the city-specific shape. Dispatch by city or average with inverse-variance weights.
- **Single change**: ensemble = `0.5 * global + 0.5 * per_city`.
- **Expected effect**: -3 days MAE.
- **Phase**: Phase 2.5 composition.

## H023: fit Cox proportional hazards baseline
- **Prior**: 0.70
- **Mechanism**: Cox PH [118] is the canonical survival baseline and is interpretable via hazard ratios. Scikit-survival [128] provides a clean implementation. The `city` indicator alone should reproduce the headline SF-vs-Austin difference and give hazard ratios that are directly publishable. Even if XGBoost AFT wins on MAE, Cox should win on interpretability and is a sanity check.
- **Single change**: add `CoxPHSurvivalAnalysis` fit to the pipeline.
- **Expected effect**: establishes C-index baseline around 0.70; not expected to beat XGBoost AFT on MAE but provides interpretable hazard ratios.
- **Phase**: Phase 2 single-add.

## H024: fit Weibull AFT
- **Prior**: 0.68
- **Mechanism**: Lifelines [129] fits a Weibull AFT [120] in one call. Weibull is the default parametric survival distribution and is well-calibrated for duration data with a monotone hazard. Gives time-ratio interpretation directly and handles censoring cleanly.
- **Single change**: add `WeibullAFTFitter` fit alongside Cox.
- **Expected effect**: C-index close to Cox; more interpretable coefficients as time-ratios.
- **Phase**: Phase 2 single-add.

## H025: fit log-normal AFT
- **Prior**: 0.68
- **Mechanism**: Log-normal is the natural distribution if log-duration is approximately Gaussian, which fits the heavy-tailed permit data [data_acquisition_notes.md]. Lifelines' `LogNormalAFTFitter` [129] and the AFT literature [120, 122, 249, 250] make this a cheap comparison.
- **Single change**: add `LogNormalAFTFitter` fit alongside Cox.
- **Expected effect**: likely slightly better calibration on the tail than Weibull; C-index similar.
- **Phase**: Phase 2 single-add.

## H026: fit log-logistic AFT
- **Prior**: 0.62
- **Mechanism**: Log-logistic has a non-monotone hazard (initially rising, then falling) which is a plausible shape for permit durations: most cases clear within their expected time, and the hazard of completion drops for cases that have already been stuck a long time (adverse-selection-within-backlog). [122, 249, 250].
- **Single change**: `LogLogisticAFTFitter`.
- **Expected effect**: small improvement over Weibull on calibration; might be worse on MAE.
- **Phase**: Phase 2 single-add.

## H027: fit Random Survival Forest
- **Prior**: 0.68
- **Mechanism**: RSF [123] captures non-linearities and interactions without explicit specification, and handles censoring natively via scikit-survival [128]. The literature review [section 6] recommends RSF as a non-linear validation of Cox.
- **Single change**: `RandomSurvivalForest(n_estimators=500)` from scikit-survival.
- **Expected effect**: comparable to XGBoost AFT on C-index, probably slightly worse on MAE due to lack of AFT-loss optimisation.
- **Phase**: Phase 2 single-add.

## H028: add monotone constraint — valuation monotone on duration
- **Prior**: 0.72
- **Mechanism**: Higher valuation implies larger, more complex projects requiring more review. XGBoost's monotonic constraint prevents the tree-building from finding spurious inverse relationships driven by small-sample subregions. Monotonic constraints are the recommended regularisation for engineering domain priors [XGBoost docs].
- **Single change**: `monotone_constraints={'log1p_valuation_usd': 1}` on the XGBoost call.
- **Expected effect**: -0.5 days MAE, more stable out-of-sample generalisation.
- **Phase**: Phase 2 single-add.

## H029: add monotone constraint — unit count monotone
- **Prior**: 0.70
- **Mechanism**: Same rationale as H028. Higher unit count should not make a permit faster (this would be mechanistically backward). Prevents sparse-leaf artifacts.
- **Single change**: `monotone_constraints={'log1p_unit_count': 1}`.
- **Expected effect**: -0.5 days MAE.
- **Phase**: Phase 2 single-add.

## H030: add monotone constraint — square feet monotone
- **Prior**: 0.68
- **Mechanism**: Same as H028-H029.
- **Single change**: `monotone_constraints={'log1p_square_feet': 1}`.
- **Expected effect**: -0.3 days MAE.
- **Phase**: Phase 2 single-add.

## H031: switch from log-duration target to raw-duration target
- **Prior**: 0.50
- **Mechanism**: The baseline uses `log(duration + 1)` which is standard for heavy-tailed targets but biases the mean prediction when back-transformed via `exp`. Raw target removes this bias at the cost of dominance by tail cases. Ambiguous direction; worth testing both.
- **Single change**: `objective='reg:squarederror'` with raw `duration_days`.
- **Expected effect**: likely worse on MAE, better on RMSE or 90th percentile quantile loss.
- **Phase**: Phase 2 single-add.

## H032: square-root target transform
- **Prior**: 0.55
- **Mechanism**: Square-root transform is between log (heavy compression) and identity (no compression). For Poisson-like counts this is the variance-stabilising transform. Permit durations are not strictly Poisson but share the "small values dominate, long tail" shape.
- **Single change**: `target = sqrt(duration_days)`.
- **Expected effect**: ambiguous; likely worse than log on MAE.
- **Phase**: Phase 2 single-add.

## H033: Box-Cox target transform with optimized lambda
- **Prior**: 0.58
- **Mechanism**: Box-Cox [Sakia 1992, refd in 122] finds the optimal power transform to make the distribution approximately Gaussian. For duration data this is usually close to log (lambda near 0) but fitting it properly costs nothing.
- **Single change**: `scipy.stats.boxcox(duration_days + 1)`; use fitted lambda.
- **Expected effect**: -0.5 day MAE relative to log.
- **Phase**: Phase 2 single-add.

## H034: quantile regression (P50) as separate model
- **Prior**: 0.64
- **Mechanism**: Median is more robust to tail outliers than mean. XGBoost supports `objective='reg:quantileerror', quantile_alpha=0.5` directly. Quantile regression also composes naturally with downstream per-stage decomposition. The literature has quantile regression examples in housing-duration work [Mawhorter, 349, 350].
- **Single change**: `objective='reg:quantileerror', quantile_alpha=0.5`.
- **Expected effect**: lower MAE than squared-error, worse on RMSE. +0.01 R2 equivalent.
- **Phase**: Phase 2 single-add.

## H035: quantile regression at P90
- **Prior**: 0.60
- **Mechanism**: The research question is about the tail (605-day SF outliers) not the median. A P90 quantile model explicitly optimises tail accuracy.
- **Single change**: `objective='reg:quantileerror', quantile_alpha=0.9`.
- **Expected effect**: much better calibration at the 90th percentile; worse at the median.
- **Phase**: Phase 2 single-add.

## H036: add interaction feature city x filed_year
- **Prior**: 0.72
- **Mechanism**: Austin HOME-1 [62, 63, 64, 186, 258] and SB 423 [136, 138, 276, 277, 278] have different effective dates and different cities. A global trend term cannot capture this. A city-year interaction lets the model learn SF slowdown + Austin speedup simultaneously.
- **Single change**: target-encoded `city_year = city + "_" + str(filed_year)` feature.
- **Expected effect**: -3 to -5 days MAE.
- **Phase**: Phase 2 single-add.

## H037: add explicit reform-dummies
- **Prior**: 0.68
- **Mechanism**: H036 captures the trend implicitly; explicit dummies for known reforms is interpretable and publishable. SB 423 effective 2024-01-01 [136], Austin HOME-1 effective 2023-12-01 [186], AB 2011 effective 2023-07-01 [137], Florida HB 267 effective 2024-07-01 [56], DOB NOW phased 2019-2022 [74, 75, 76, 190]. Each is a known discontinuity.
- **Single change**: five binary features for `post_sb423`, `post_home1`, `post_ab2011`, `post_hb267`, `post_dob_now`.
- **Expected effect**: -2 to -4 days MAE; reform coefficients are directly interpretable.
- **Phase**: Phase 2 single-add.

## H038: treat SB 423 cutoff as a regression discontinuity
- **Prior**: 0.65
- **Mechanism**: Per H037 SB 423 effective 2024-01-01. Pre/post dummy + running variable `days_since_2024_01_01` gives a fuzzy RD estimate of the reform effect in California cities [Kulka-Sood-Chiumenti 2025 methodology, 157]. Not strictly a prediction-improvement hypothesis; more an interpretable covariate.
- **Single change**: add `post_sb423`, `days_since_sb423` (only for SF and LA), interaction.
- **Expected effect**: -1 to -3 days MAE on SF 2024-2026 slice; publishable reform-effect estimate.
- **Phase**: Phase 2.5 composition.

## H039: treat Austin HOME-1 cutoff as a regression discontinuity
- **Prior**: 0.66
- **Mechanism**: Same as H038 but for Austin [62, 63, 186, 258]. Pew [61] documents the post-HOME-1 structural change in Austin housing production.
- **Single change**: add `post_home1`, `days_since_home1` for Austin.
- **Expected effect**: -1 to -2 days MAE on Austin 2023+; publishable reform-effect estimate.
- **Phase**: Phase 2.5 composition.

## H040: treat NYC DOB NOW rollout as a staggered adoption
- **Prior**: 0.60
- **Mechanism**: DOB NOW rolled out by work type from 2016-2022 [74, 75, 76, 190]. The 2021 DOB report [76] noted 11% YoY increase in new-build permits post-rollout. A dummy keyed to the rollout date for that work class is a clean staggered-adoption design.
- **Single change**: add `post_dob_now` keyed to NYC work-type-specific rollout date.
- **Expected effect**: -1 to -3 days MAE on NYC post-2019.
- **Phase**: Phase 2.5 composition.

## H041: use LA `business_unit` field as a feature
- **Prior**: 0.82
- **Mechanism**: LA's `gwh9-jnip` exposes `business_unit ∈ {Regular Plan Check, Express Permit, OTC}` [data_sources.md section 6]. This is essentially a ground-truth pipeline-lane flag: Express and OTC permits take hours to days, Regular Plan Check takes months. Currently dropped by the loader. Enormous explanatory power on LA.
- **Single change**: include `business_unit` as categorical feature on LA rows; add to raw parquet cache if not already.
- **Expected effect**: -10 to -20 days MAE on LA holdout.
- **Phase**: Phase 2 single-add.

## H042: use Chicago `review_type` field as a feature
- **Prior**: 0.80
- **Mechanism**: Chicago's `ydr8-5enu` exposes `review_type ∈ {NEW CONSTRUCTION, STANDARD PLAN REVIEW, EASY PERMIT, SIGN PERMIT, ...}` [data_sources.md section 8]. This is analogous to LA `business_unit` — a direct lane indicator. `data_acquisition_notes.md` already flags it as a high-value field not in the normalised schema.
- **Single change**: include `review_type` as categorical feature on Chicago rows.
- **Expected effect**: -5 to -15 days MAE on Chicago.
- **Phase**: Phase 2 single-add.

## H043: use Chicago `processing_time` as a leakage-check
- **Prior**: 0.50 (not for prediction, but for validation)
- **Mechanism**: Chicago ships a pre-computed `processing_time` column [data_sources.md section 8]. If our computed `issued - filed` does not match, there is a data-loading bug. This is a validation hypothesis, not a feature.
- **Single change**: add assert in loader that `processing_time == (issue_date - application_start_date).days`; log mismatches.
- **Expected effect**: discovers date-parsing bugs if any; 0 MAE effect in best case.
- **Phase**: Phase 2 single-add.

## H044: stratify by permit_type (new vs alter)
- **Prior**: 0.75
- **Mechanism**: New construction and alterations go through different review paths in every city. Stratified analysis is standard in the regulation-effects literature [14, 15, 16, 17]. Failing to stratify means the model must learn a correlated-to-type offset that bleeds between types.
- **Single change**: split training into new-construction-only (`permit_type` contains 'New'/'NB'/'Bldg-New') and alterations-only, two models.
- **Expected effect**: -3 to -5 days MAE on both slices.
- **Phase**: Phase 2.5 composition.

## H045: ADU-specific stratum
- **Prior**: 0.68
- **Mechanism**: California ADUs have been by-right since 2017 [SB 229, AB 2299, AB 494, etc.], Portland has an explicit `Accessory Dwelling Unit` sub-type [data_sources.md section 16], LA has an ADU fast-track [181, 182]. ADUs flow through a distinct fast pipeline. Mixing them with full new builds dilutes both.
- **Single change**: add ADU filter and a separate stratum.
- **Expected effect**: -2 to -4 days MAE on ADU-inclusive cities.
- **Phase**: Phase 2.5 composition.

## H046: add Wharton Regulatory Land Use Index (WRLURI) as a city covariate
- **Prior**: 0.65
- **Mechanism**: WRLURI [2, 3] is the standard city-level regulatory-stringency index. The 2018 refresh [3] covers ~2,500 jurisdictions and is publicly available. Adds one continuous feature that captures the political-economy axis Saiz [1, 155] and Molloy [21, 218] emphasise. This is a static covariate — same value for all permits in a city.
- **Single change**: join each row to the city's WRLURI score as a feature.
- **Expected effect**: -1 to -3 days MAE; mostly explains cross-city mean.
- **Phase**: Phase 2 single-add.

## H047: add Census BPS monthly permit count for the city as a load proxy
- **Prior**: 0.68
- **Mechanism**: Census BPS [71-73, 301-308] gives monthly permit counts per place. Dividing by estimated plan-check capacity approximates Little's-Law load ρ [116, 117]. High-load months have longer durations by M/M/c [115] — and this is measurable.
- **Single change**: join each permit to its city-month BPS unit count as a feature.
- **Expected effect**: -2 to -4 days MAE, especially on pandemic-era or post-reform spikes.
- **Phase**: Phase 2 single-add.

## H048: add ACS density as a city static covariate
- **Prior**: 0.58
- **Mechanism**: Rothwell & Massey [19], Pendall [18] show density-related zoning regulates permit throughput. ACS block-group or tract density is a good proxy for neighborhood-density context and is public.
- **Single change**: ACS population density joined by zip or tract.
- **Expected effect**: -0.5 to -1.5 days MAE.
- **Phase**: Phase 2 single-add.

## H049: add FRED 30-year mortgage rate for the filing month
- **Prior**: 0.50
- **Mechanism**: High mortgage rates reduce demand pressure and slow the application pipeline — but also change developer behavior (risky projects withdraw). Effect sign is ambiguous. Still worth an exogenous macro feature.
- **Single change**: join each permit to FRED MORTGAGE30US for its filing month.
- **Expected effect**: -0.5 day MAE or 0.
- **Phase**: Phase 2 single-add.

## H050: add BLS construction employment for the metro and filing month
- **Prior**: 0.55
- **Mechanism**: Local construction employment measures market activity and developer backlog. High employment correlates with more applications in the pipeline and longer queues; also correlates with more contractor experience and possibly faster applications. Ambiguous sign.
- **Single change**: BLS CES construction employment, joined by MSA and month.
- **Expected effect**: -0.5 to -1 day MAE.
- **Phase**: Phase 2 single-add.

## H051: add FRED housing starts for the region
- **Prior**: 0.50
- **Mechanism**: FRED HOUST1FQ (regional housing starts) captures pipeline pressure at the regional level. High starts should imply high load.
- **Single change**: join by region-quarter.
- **Expected effect**: -0.5 day MAE.
- **Phase**: Phase 2 single-add.

## H052: add days-since-previous-permit-in-same-neighborhood
- **Prior**: 0.56
- **Mechanism**: A recency-based feature captures neighborhood-level pipeline state. If a given neighborhood just had five permits filed in the same week, the reviewers covering that area are loaded. Neighborhood-level reviewer assignment is common.
- **Single change**: compute `days_since_last_permit_in_neighborhood` per row.
- **Expected effect**: -1 day MAE.
- **Phase**: Phase 2 single-add.

## H053: add 30-day rolling permit count as a load feature
- **Prior**: 0.68
- **Mechanism**: Per H047, but city-wide and computed from the dataset itself (no BPS join required). A 30-day rolling count is a direct proxy for current load. Classical M/M/c [114, 115] predicts approximately `1/(1-ρ)` response to load; this feature directly feeds the non-linear relationship.
- **Single change**: add `rolling_30d_permit_count_city` as a feature.
- **Expected effect**: -2 days MAE.
- **Phase**: Phase 2 single-add.

## H054: add 90-day rolling permit count
- **Prior**: 0.62
- **Mechanism**: Same as H053 but longer window. Captures seasonal load rather than weekly spikes.
- **Single change**: add `rolling_90d_permit_count_city` as a feature.
- **Expected effect**: -1 day MAE.
- **Phase**: Phase 2 single-add.

## H055: add LightGBM as alternative model
- **Prior**: 0.60
- **Mechanism**: LightGBM is typically 2-5x faster than XGBoost on large tabular datasets and sometimes has slightly different bias-variance tradeoffs. Works with native categorical features, which reduces the need for one-hot encoding on `permit_subtype` and `neighborhood`.
- **Single change**: swap XGBoost for LightGBM with the same feature set.
- **Expected effect**: ~0 MAE difference; faster training.
- **Phase**: Phase 2 single-add.

## H056: add CatBoost for native categorical handling
- **Prior**: 0.62
- **Mechanism**: CatBoost handles high-cardinality categoricals natively via ordered target encoding. `permit_subtype` and `neighborhood` are both high-cardinality; CatBoost's encoding is known to beat naive one-hot.
- **Single change**: CatBoostRegressor with categorical columns marked.
- **Expected effect**: -1 to -2 days MAE.
- **Phase**: Phase 2 single-add.

## H057: add ExtraTrees as variance-reduction ensemble
- **Prior**: 0.50
- **Mechanism**: ExtraTrees differs from RandomForest in split selection randomness. Good ensemble base learner.
- **Single change**: `ExtraTreesRegressor(n_estimators=500)`.
- **Expected effect**: ~0 MAE; useful in stacked ensemble.
- **Phase**: Phase 2 single-add.

## H058: stacked ensemble (XGBoost + LightGBM + CatBoost)
- **Prior**: 0.72
- **Mechanism**: Stacking boosted tree libraries with slightly different tree-growing strategies gives small but reliable MAE reductions. Standard Kaggle practice.
- **Single change**: stacked ensemble via sklearn StackingRegressor.
- **Expected effect**: -0.5 to -1.5 days MAE.
- **Phase**: Phase 2.5 composition.

## H059: ridge regression sanity check
- **Prior**: 0.30 (not for winning, for sanity)
- **Mechanism**: Linear baseline establishes that tree-based gains are real and not an artifact. If ridge gets close to XGBoost, the problem is mostly linear and features are underused. Standard sanity check in any ML project.
- **Single change**: `sklearn.linear_model.Ridge(alpha=1.0)` with one-hot encoded features.
- **Expected effect**: probably +10-20 days MAE worse than XGBoost — that is the point.
- **Phase**: Phase 2 single-add.

## H060: TabPFN for small-N cities
- **Prior**: 0.55
- **Mechanism**: TabPFN is a pre-trained transformer that works well on tabular data with N < 10,000. Seattle (~5k unique permits per year in the Plan Review dataset) is in its sweet spot. For the larger cities it cannot scale, but on Seattle it could beat XGBoost.
- **Single change**: TabPFN on the Seattle-only slice.
- **Expected effect**: -2 to -5 days MAE on Seattle holdout.
- **Phase**: Phase 2 single-add.

## H061: DeepHit for larger cities
- **Prior**: 0.58
- **Mechanism**: DeepHit [124, 125] drops the proportional-hazards assumption and handles competing risks (issued vs withdrawn vs denied). For NYC and SF with N >> 10k it is applicable. The competing-risks angle is important because `status ∈ {withdrawn, expired}` are non-issuance outcomes that should not be treated as "permit issued tomorrow" under right-censoring.
- **Single change**: pycox DeepHit fit on the NYC slice.
- **Expected effect**: -1 to -3 days MAE on NYC; better C-index.
- **Phase**: Phase 2 single-add.

## H062: Deep Survival Machines
- **Prior**: 0.55
- **Mechanism**: DSM [126, 245] uses a mixture of parametric distributions and is a reasonable middle ground between parametric AFT and non-parametric DeepHit. Auton-Survival reference implementation is standard.
- **Single change**: auton-survival DeepSurvivalMachines fit.
- **Expected effect**: ~similar to DeepHit.
- **Phase**: Phase 2 single-add.

## H063: Cox-elasticnet / Cox-Lasso for high-dim covariates
- **Prior**: 0.60
- **Mechanism**: Cox-net [scikit-survival: CoxnetSurvivalAnalysis, 128] adds L1/L2 regularisation. Useful when covariates include many target-encoded high-cardinality fields (H019, H020) that would overfit plain Cox.
- **Single change**: `CoxnetSurvivalAnalysis(l1_ratio=0.5)`.
- **Expected effect**: modest MAE improvement over plain Cox.
- **Phase**: Phase 2 single-add.

## H064: gradient-boosted Cox (sksurv GradientBoostingSurvival)
- **Prior**: 0.62
- **Mechanism**: Alternative to XGBoost AFT — fits a boosted Cox PH loss [128]. Should be close to H001 on MAE but with hazard-ratio interpretability.
- **Single change**: `GradientBoostingSurvivalAnalysis`.
- **Expected effect**: close to H001.
- **Phase**: Phase 2 single-add.

## H065: add `application_submission_method` on SF (in-house vs online)
- **Prior**: 0.70
- **Mechanism**: `data_acquisition_notes.md` flags `application_submission_method` as a high-value SF-specific field. Online-submitted permits go through a faster digital track than counter submissions. Direct pipeline-lane feature.
- **Single change**: add `application_submission_method` to the SF raw parquet cache, then expose as a column.
- **Expected effect**: -2 to -4 days MAE on SF.
- **Phase**: Phase 2 single-add.

## H066: add SF `plansets` (number of plan copies submitted)
- **Prior**: 0.58
- **Mechanism**: Higher plan-set counts indicate larger packets and hence more reviewer pages to process. `data_acquisition_notes.md` flags it.
- **Single change**: add `plansets` to SF features.
- **Expected effect**: -0.5 to -1.5 days MAE on SF.
- **Phase**: Phase 2 single-add.

## H067: add SF change-of-use flag
- **Prior**: 0.68
- **Mechanism**: SF's `existing_use` vs `proposed_use` difference is a change-of-use. Change-of-use permits trigger additional zoning review and are a known slow track. Elmendorf [30, 281] ties change-of-use to the discretionary-review layer.
- **Single change**: add `change_of_use = existing_use != proposed_use` on SF.
- **Expected effect**: -1 to -3 days MAE on SF.
- **Phase**: Phase 2 single-add.

## H068: add NYC `zoning_dist1` as a feature
- **Prior**: 0.68
- **Mechanism**: NYC zoning designation encodes a lot about what pipeline track the permit follows: R7-2 (moderate residential), R6 (low-mid density), etc. `data_acquisition_notes.md` flags this. The ULURP [133, 134] exposure condition depends on zoning.
- **Single change**: target-encoded `zoning_dist1` on NYC.
- **Expected effect**: -2 to -4 days MAE on NYC.
- **Phase**: Phase 2 single-add.

## H069: add NYC `professional_cert` flag
- **Prior**: 0.75
- **Mechanism**: NYC's "professional certification" option lets a licensed professional engineer or architect self-certify plans instead of waiting for DOB review. Professional-cert permits are much faster (days instead of months) and the field is in the raw BIS data. `data_acquisition_notes.md` flags this explicitly.
- **Single change**: add `professional_cert` boolean to NYC features.
- **Expected effect**: -5 to -15 days MAE on NYC.
- **Phase**: Phase 2 single-add.

## H070: add Austin `masterpermitnum` group as an identifier
- **Prior**: 0.55
- **Mechanism**: Multiple trade permits (BP, MP, EP, PP) can belong to the same project via `masterpermitnum`. Grouping lets us compute project-level duration and cluster standard errors. Not strictly a feature; a grouping.
- **Single change**: add `master_group_size` = count of sibling permits per master.
- **Expected effect**: -1 day MAE on Austin.
- **Phase**: Phase 2 single-add.

## H071: add Austin `project_id` group size
- **Prior**: 0.55
- **Mechanism**: Same as H070 via the alternative project-grouping key.
- **Single change**: add `project_group_size`.
- **Expected effect**: -1 day MAE on Austin.
- **Phase**: Phase 2 single-add.

## H072: cluster SF by parcel for project-level durations
- **Prior**: 0.60
- **Mechanism**: `data_sources.md` notes SF has no project ID and multiple parallel permits per project must be clustered by `(block, lot, filed_date +/- 30d)`. Computing a project-level duration on the cluster and feeding each permit its project duration as a feature captures the broader project pipeline.
- **Single change**: cluster, then add `project_first_filed`, `project_last_issued`, `project_size` features.
- **Expected effect**: -2 to -4 days MAE on SF.
- **Phase**: Phase 2.5 composition.

## H073: contractor frequency (Chicago, Portland)
- **Prior**: 0.65
- **Mechanism**: Chicago has `contact_1_*` (contractor), Portland has `CONTRACTORNAME`. Frequent contractors know the system and file cleaner packets, reducing correction cycles. Target-encode contractor experience by how many permits they've filed previously.
- **Single change**: add `contractor_prior_count` as a per-row rolling count.
- **Expected effect**: -1 to -3 days MAE on Chicago and Portland.
- **Phase**: Phase 2 single-add.

## H074: Seattle `standardplan` flag
- **Prior**: 0.76
- **Mechanism**: Seattle's `standardplan=true` flags pre-approved prototype plans that skip normal plan check [data_sources.md section 14]. Direct fast-track indicator. The field is in the raw parquet but not in the normalised schema.
- **Single change**: add `standardplan` boolean to Seattle.
- **Expected effect**: -5 to -15 days MAE on Seattle.
- **Phase**: Phase 2 single-add.

## H075: Seattle `reviewcomplexity` as ordinal
- **Prior**: 0.72
- **Mechanism**: `reviewcomplexity` ∈ {Basic, Basic+, Full, Full+} [data_sources.md section 14]. Direct complexity label from the permit office. Should reduce a lot of variance.
- **Single change**: add `reviewcomplexity` encoded ordinal.
- **Expected effect**: -3 to -8 days MAE on Seattle.
- **Phase**: Phase 2 single-add.

## H076: Seattle reviewer identity as target-encoded feature
- **Prior**: 0.72
- **Mechanism**: Seattle exposes `reviewer` per review cycle. Reviewers vary in throughput rate. Target-encoded reviewer is the single Seattle-specific feature most consistent with the "reviewer workload is the causal driver" open question [literature review #3, #6].
- **Single change**: add K-fold target-encoded reviewer.
- **Expected effect**: -3 to -8 days MAE on Seattle.
- **Phase**: Phase 2 single-add.

## H077: Seattle `reviewteam` as categorical
- **Prior**: 0.65
- **Mechanism**: Team-level grouping is coarser but more stable than individual reviewer.
- **Single change**: add target-encoded `reviewteam`.
- **Expected effect**: -1 to -3 days MAE on Seattle.
- **Phase**: Phase 2 single-add.

## H078: Seattle `reviewresultdesc` is leakage; explicit drop
- **Prior**: 0.30 (negative hypothesis — guard against leakage)
- **Mechanism**: `reviewresultdesc ∈ {Corrections Required, Approved, ...}` is determined during review and leaks the outcome. Must never be used as a predictor. Explicit negative hypothesis.
- **Single change**: verify `reviewresultdesc` is not in the feature set.
- **Expected effect**: 0 (guardrail).
- **Phase**: Phase 2 single-add.

## H079: rework rate = `numberreviewcycles / total_reviewtypes` (Seattle)
- **Prior**: 0.72
- **Mechanism**: Cycle count normalised by number of review types gives the average re-work rate per review type. Consistent with the process-mining rework-rate literature [87, 92, 93, 94] and BPIC 2015 [107].
- **Single change**: `rework_rate = numberreviewcycles / num_distinct_reviewtypes` on Seattle.
- **Expected effect**: -3 to -5 days MAE on Seattle.
- **Phase**: Phase 2 single-add.

## H080: Seattle `daysinitialplanreview` as feature
- **Prior**: 0.78
- **Mechanism**: Pre-computed days spent in the initial plan review (before corrections). This is the "first-pass service time" distinct from the rework loop.
- **Single change**: add `daysinitialplanreview`.
- **Expected effect**: -5 to -10 days MAE on Seattle.
- **Phase**: Phase 2 single-add.

## H081: Seattle `daysplanreviewcity` as feature
- **Prior**: 0.76
- **Mechanism**: City-side review time (city holds case) is the metric that reform programs can actually move. `daysoutcorrections` is the applicant-side equivalent and is H003. Both are needed for the full decomposition.
- **Single change**: add `daysplanreviewcity`.
- **Expected effect**: -5 days MAE on Seattle.
- **Phase**: Phase 2 single-add.

## H082: Seattle `reviewcycle` max as cycle count (alternative to H002)
- **Prior**: 0.75
- **Mechanism**: Alternative to `numberreviewcycles` — take the max `reviewcycle` across reviewtypes. Sometimes more reliable because `numberreviewcycles` is itself an aggregate computed by SDCI.
- **Single change**: `max_review_cycle = raw.groupby('permitnum').reviewcycle.max()`.
- **Expected effect**: similar to H002.
- **Phase**: Phase 2 single-add.

## H083: NYC BIS + DOB NOW union loader
- **Prior**: 0.80
- **Mechanism**: `data_sources.md` notes NYC jobs increasingly flow through DOB NOW (`w9ak-ipjd`) from 2020 onward, leaving `ic3t-wcy2` stale for recent years. Post-2020 coverage requires the union. This is more than a feature; it is a dataset-completeness fix. Existing loader only uses BIS.
- **Single change**: union `ic3t-wcy2` and `w9ak-ipjd` with schema harmonisation.
- **Expected effect**: substantially better 2020+ coverage for NYC; does not directly move MAE but is prerequisite for studying DOB NOW effects.
- **Phase**: Phase 2 single-add.

## H084: explicit right-censoring label from today's extraction date
- **Prior**: 0.78
- **Mechanism**: For H001 to work we need the censoring label. For each permit with `issued_date IS NULL` at extraction, the censoring event time is `today - filed_date` and the event indicator is 0. For issued permits the event time is `issued - filed` and indicator is 1. Standard right-censoring setup [118, 121, 122].
- **Single change**: add `event = (issued_date is not None)` and `duration = issued_date - filed_date if event else (today - filed_date)`.
- **Expected effect**: enables H001, H023-H027, H061-H064. No standalone MAE change.
- **Phase**: Phase 2 single-add.

## H085: include withdrawn/denied as non-event
- **Prior**: 0.62
- **Mechanism**: Withdrawn and denied permits are NOT right-censored in the "could still be issued tomorrow" sense — they are terminated in a different state. Competing-risks survival [124, 125] handles this correctly. A simpler treatment is to drop them; but the information is useful.
- **Single change**: add `terminal_state ∈ {issued, withdrawn, denied, expired, open}` and fit DeepHit (H061) on the competing risks.
- **Expected effect**: better calibration on the overall population; slightly better MAE on issued holdout.
- **Phase**: Phase 2.5 composition.

## H086: per-city XGBoost hyperparameter sweep
- **Prior**: 0.65
- **Mechanism**: XGBoost default hyperparameters rarely win. A modest sweep over depth, learning rate, `min_child_weight`, `n_estimators`, `subsample`, `colsample_bytree` is standard practice.
- **Single change**: Optuna sweep of 200 trials.
- **Expected effect**: -1 to -3 days MAE.
- **Phase**: Phase B optimisation.

## H087: XGBoost depth sweep (3 to 12)
- **Prior**: 0.60
- **Mechanism**: Component of H086 broken out for isolation. Very deep trees overfit on small cities; shallow trees underfit on large cities.
- **Single change**: try `max_depth ∈ {3, 5, 7, 9, 12}`.
- **Expected effect**: -0.5 to -1 day MAE.
- **Phase**: Phase B optimisation.

## H088: XGBoost learning rate sweep (0.01 to 0.2)
- **Prior**: 0.55
- **Mechanism**: Classical lr-trees tradeoff. Lower lr with more estimators usually wins.
- **Single change**: try `learning_rate ∈ {0.01, 0.03, 0.05, 0.1, 0.2}` with matching `n_estimators`.
- **Expected effect**: -0.5 day MAE.
- **Phase**: Phase B optimisation.

## H089: XGBoost min_child_weight sweep
- **Prior**: 0.55
- **Mechanism**: Higher min_child_weight regularises more. Useful for high-cardinality categorical features and small cities.
- **Single change**: `min_child_weight ∈ {1, 5, 20, 100}`.
- **Expected effect**: -0.5 day MAE.
- **Phase**: Phase B optimisation.

## H090: XGBoost subsample and colsample sweep
- **Prior**: 0.52
- **Mechanism**: Row and column subsampling regularises the ensemble. Small effect but cheap.
- **Single change**: `subsample ∈ {0.6, 0.8, 1.0}, colsample_bytree ∈ {0.6, 0.8, 1.0}`.
- **Expected effect**: -0.2 to -0.5 day MAE.
- **Phase**: Phase B optimisation.

## H091: XGBoost L1 and L2 regularisation sweep
- **Prior**: 0.52
- **Mechanism**: `reg_alpha` and `reg_lambda` sweep. Useful when target-encoded features dominate importance.
- **Single change**: `reg_alpha ∈ {0, 0.1, 1}, reg_lambda ∈ {0.1, 1, 10}`.
- **Expected effect**: -0.2 day MAE.
- **Phase**: Phase B optimisation.

## H092: XGBoost n_estimators sweep with early stopping
- **Prior**: 0.58
- **Mechanism**: Early-stopping on a validation split auto-selects n_estimators. Standard.
- **Single change**: `n_estimators=5000, early_stopping_rounds=50`.
- **Expected effect**: -0.5 day MAE and training-time reduction.
- **Phase**: Phase B optimisation.

## H093: bin filed_year into pre-2015 / 2015-2019 / 2020-2021 / 2022+ eras
- **Prior**: 0.58
- **Mechanism**: Binary eras (pre-digital, pre-COVID, COVID, post-COVID-reform) are more robust than continuous year for a tree model, especially in small-sample cities. Motivated by the 2020 COVID break and the 2022-2024 reform wave.
- **Single change**: feature `era ∈ {0, 1, 2, 3}`.
- **Expected effect**: -0.5 day MAE.
- **Phase**: Phase 2 single-add.

## H094: add total_fee feature (Chicago)
- **Prior**: 0.55
- **Mechanism**: Chicago exposes `total_fee`, `building_fee_*`, `zoning_fee_*`, `other_fee_*`. Total fee is a rough proxy for project complexity that the permit office already quantified. Correlated with valuation but not identical.
- **Single change**: add `log1p_total_fee` to Chicago features.
- **Expected effect**: -1 day MAE on Chicago.
- **Phase**: Phase 2 single-add.

## H095: add fee-per-unit or fee-per-sqft derived feature
- **Prior**: 0.50
- **Mechanism**: Fee schedules vary by project type. Fee/unit and fee/sqft normalise fees against project scale and isolate the "complexity premium".
- **Single change**: add `fee_per_unit = total_fee / max(unit_count, 1)`.
- **Expected effect**: -0.5 day MAE on Chicago.
- **Phase**: Phase 2 single-add.

## H096: add SF supervisor district as feature
- **Prior**: 0.60
- **Mechanism**: SF supervisor districts correlate with discretionary-review usage patterns. "Homevoter hypothesis" [25, 220, 169] predicts political-economy effects by district.
- **Single change**: add target-encoded `supervisor_district`.
- **Expected effect**: -1 to -2 days MAE on SF.
- **Phase**: Phase 2 single-add.

## H097: add NYC community board as feature
- **Prior**: 0.64
- **Mechanism**: NYC community boards are the first ULURP gate [133, 134]. 59 boards with highly variable culture. Einstein, Glick & Palmer [169] document heterogeneous board-level NIMBY patterns.
- **Single change**: add target-encoded `community___board` for NYC.
- **Expected effect**: -1 to -3 days MAE on NYC.
- **Phase**: Phase 2 single-add.

## H098: add LA council district as feature
- **Prior**: 0.58
- **Mechanism**: LA's `cd` column is a direct council-district identifier. LA has member deference practices similar to Chicago [65, 66] though less codified.
- **Single change**: target-encoded `cd`.
- **Expected effect**: -1 day MAE on LA.
- **Phase**: Phase 2 single-add.

## H099: add Chicago ward as feature
- **Prior**: 0.70
- **Mechanism**: Chicago's aldermanic privilege [43, 187, 188] is the canonical ward-level veto mechanism. Chicago ward should be a dominant feature.
- **Single change**: target-encoded `ward` on Chicago.
- **Expected effect**: -2 to -4 days MAE on Chicago.
- **Phase**: Phase 2 single-add.

## H100: add Portland neighborhood coalition
- **Prior**: 0.55
- **Mechanism**: Portland exposes `NEIGHBORHOOD_COALITION` and `NEIGHBORHOOD_DISTRICT` for political-group grouping. Neighborhood groups drive appeal activity.
- **Single change**: target-encoded neighborhood coalition.
- **Expected effect**: -0.5 to -1 day MAE on Portland.
- **Phase**: Phase 2 single-add.

## H101: inductive miner process discovery on Seattle per-cycle data
- **Prior**: 0.68
- **Mechanism**: Seattle's per-cycle event log is the single dataset that supports true process-mining. Running pm4py [328] inductive miner [95, 96, 237, 241, 242, 243] extracts a Petri net from `(permitnum, reviewtype, reviewerfinishdate)` triples. Resulting control-flow metrics (conformance, repetitions, loops) [89, 90, 320, 321, 322] become features.
- **Single change**: pm4py discover inductive miner; compute per-permit control-flow features.
- **Expected effect**: -5 to -10 days MAE on Seattle; huge interpretability payoff.
- **Phase**: Phase 2.5 composition.

## H102: alpha miner baseline on Seattle (validation of H101)
- **Prior**: 0.40
- **Mechanism**: Alpha miner [91] is the first process-discovery algorithm and is superseded. Run as a sanity check that process-mining concepts apply here. Not expected to win.
- **Single change**: pm4py alpha miner discovery.
- **Expected effect**: similar structure to H101; lower quality model.
- **Phase**: Phase 2.5 composition.

## H103: heuristic miner process discovery
- **Prior**: 0.55
- **Mechanism**: Heuristic miner [92, 93, 94, 98, 323, 324, 325] is noise-tolerant and handles real data better than alpha. Useful for Seattle if inductive miner outputs a degenerate model.
- **Single change**: pm4py heuristic miner with default thresholds.
- **Expected effect**: comparable to H101.
- **Phase**: Phase 2.5 composition.

## H104: conformance-checking fitness metric as feature
- **Prior**: 0.62
- **Mechanism**: pm4py alignments [89, 90] compute per-trace fitness against a reference model. Low-fitness cases are those with unusual re-routing and are candidates for long durations. Directly feeds process-mining intuition.
- **Single change**: add `fitness_score` per permit from pm4py alignments.
- **Expected effect**: -2 to -5 days MAE on Seattle.
- **Phase**: Phase 2.5 composition.

## H105: replay-based waiting time per stage (Seattle)
- **Prior**: 0.60
- **Mechanism**: Token replay on the Seattle Petri net computes per-stage waiting-time distributions. These are city-level features (not per-permit) that quantify pipeline health at filing time.
- **Single change**: compute per-month per-stage median waiting time; join as feature.
- **Expected effect**: -1 to -3 days MAE on Seattle.
- **Phase**: Phase 2.5 composition.

## H106: BPIC 2015 pretrain -> fine-tune on Seattle
- **Prior**: 0.50
- **Mechanism**: The literature review suggests that any US pipeline method should first reproduce BPIC 2015 [102, 103, 106, 107, 240] as validation. If we can pretrain a predictive process monitoring model [99, 100, 101] on BPIC 2015 and fine-tune on Seattle, we transfer structure.
- **Single change**: train LSTM remaining-time predictor on BPIC 2015, fine-tune on Seattle.
- **Expected effect**: uncertain; fun research direction.
- **Phase**: Phase 2.5 composition.

## H107: percentile-rank target transform
- **Prior**: 0.48
- **Mechanism**: Per-city percentile rank normalises targets to uniform on [0,1]. Removes raw-scale noise and focuses the model on the within-city ordering. Inverse-transform back to days at prediction time.
- **Single change**: target = per-city percentile rank of duration.
- **Expected effect**: -0.5 day MAE or worse; stable across cities.
- **Phase**: Phase 2 single-add.

## H108: per-city z-score target
- **Prior**: 0.45
- **Mechanism**: Similar to H107. `(log(duration) - city_mean) / city_std`. Standard re-scaling.
- **Single change**: per-city z-score target.
- **Expected effect**: 0 to -0.5 day MAE.
- **Phase**: Phase 2 single-add.

## H109: multi-task learning with per-city output heads
- **Prior**: 0.55
- **Mechanism**: Shared-trunk neural network with per-city output heads. Standard transfer-learning for heterogeneous cities [224, 225, 226 etc.]. Feeds XGBoost's per-city dispatch (H022) ideas into a single model.
- **Single change**: MLP with shared trunk and 7 output heads.
- **Expected effect**: -1 to -3 days MAE if done carefully; -0 or negative if feature set is weak.
- **Phase**: Phase 2.5 composition.

## H110: transfer learning — train on Austin+LA+Chicago+Portland, test on SF
- **Prior**: 0.45
- **Mechanism**: Leave-SF-out transfer. If the features generalise across cities, test-on-SF accuracy should be good. If not, SF has idiosyncratic dynamics that require per-city training. Either outcome is publishable.
- **Single change**: cross-city hold-out setup.
- **Expected effect**: usually worse than per-city; ablation study.
- **Phase**: Phase 2 single-add.

## H111: transfer learning — train on large cities, test on Seattle
- **Prior**: 0.40
- **Mechanism**: Same as H110 with Seattle as target. Establishes whether Seattle's per-cycle data leakage is real or if the bulk cities carry enough information to predict Seattle durations without per-cycle details.
- **Single change**: leave-Seattle-out setup.
- **Expected effect**: significantly worse than per-cycle features; ablation.
- **Phase**: Phase 2 single-add.

## H112: wildfire/disaster rebuild dummy for post-event cities
- **Prior**: 0.55
- **Mechanism**: Major wildfires (Camp 2018, LA 2025) and hurricanes trigger emergency permit surges that the city responds to with emergency fast tracks. Not every city has public flagging, but timing is identifiable.
- **Single change**: add `post_disaster` dummy keyed to known events by city.
- **Expected effect**: -0.5 to -1 day MAE.
- **Phase**: Phase 2 single-add.

## H113: planner-staffing pulse where reported
- **Prior**: 0.45
- **Mechanism**: Some cities publish plan-reviewer headcount by quarter (NYC DOB, LA LADBS). A headcount feature is a direct inverse of load. Data is sparse; may not be worth the effort.
- **Single change**: add per-city quarterly plan-reviewer headcount.
- **Expected effect**: -0.5 to -1 day MAE where data exists.
- **Phase**: Phase 2 single-add.

## H114: feature-importance gated removal of low-value features
- **Prior**: 0.40
- **Mechanism**: After training full model, drop bottom-quartile features by importance and retrain. Can reduce noise and improve generalisation.
- **Single change**: 2-pass training: full then pruned.
- **Expected effect**: 0 to -0.3 day MAE.
- **Phase**: Phase B optimisation.

## H115: SHAP-guided feature selection
- **Prior**: 0.42
- **Mechanism**: Similar to H114 but uses SHAP values instead of XGBoost's native importance. SHAP is more principled for feature interaction analysis.
- **Single change**: SHAP-based feature selection pass.
- **Expected effect**: same as H114.
- **Phase**: Phase B optimisation.

## H116: permit-density in neighborhood as contextual feature
- **Prior**: 0.55
- **Mechanism**: Neighborhoods with many recent permits (booming areas) have different queue dynamics than sleepy ones. Compute 90-day rolling count per neighborhood.
- **Single change**: add `nbhd_90d_count`.
- **Expected effect**: -0.5 to -1.5 days MAE.
- **Phase**: Phase 2 single-add.

## H117: use DOB NOW vs BIS indicator for NYC (era feature)
- **Prior**: 0.68
- **Mechanism**: Jobs in `ic3t-wcy2` flow through legacy BIS; jobs in `w9ak-ipjd` flow through DOB NOW. Different software, different queues, different service times. A system indicator is free once H083 is done.
- **Single change**: add `nyc_system ∈ {bis, dob_now}`.
- **Expected effect**: -1 to -3 days MAE on NYC.
- **Phase**: Phase 2 single-add.

## H118: add 2-family vs 1-family binary (for jurisdictions that distinguish)
- **Prior**: 0.62
- **Mechanism**: The research question is duplex-specific. Duplexes (`2 Family Bldgs` in Austin, `1 or 2 Family Dwelling` in LA) go through the same pipeline as single-family but carry different unit counts and valuations. A binary indicator for "this is a duplex" lets the model specialise.
- **Single change**: add `is_duplex` binary.
- **Expected effect**: -1 day MAE.
- **Phase**: Phase 2 single-add.

## H119: recent-reform-exposure exponential decay feature
- **Prior**: 0.55
- **Mechanism**: A sharp pre/post dummy (H037) assumes instant effect. In practice reforms take months to flow through pipelines. An exponential-decay feature `exp(-(days_since_reform)/tau)` with tau ~90 days smooths the transition.
- **Single change**: add `sb423_decay = max(0, exp(-days_since/90))`.
- **Expected effect**: -0.5 day MAE; smoother coefficients.
- **Phase**: Phase 2 single-add.

## H120: add holiday season flag (Nov 15 - Jan 2)
- **Prior**: 0.52
- **Mechanism**: Filings during the US holiday season experience multi-week pauses due to office closures and staff absences. Coarser than H017 but more effective.
- **Single change**: `holiday_season = 1 if filed in Nov 15 to Jan 2 else 0`.
- **Expected effect**: -0.5 to -1 day MAE.
- **Phase**: Phase 2 single-add.

---

## Summary table

| ID | Category | Prior | City scope | Phase |
|---|---|---:|---|---|
| H001 | AFT survival | 0.88 | all | Phase 2 |
| H002 | Seattle cycle count | 0.90 | seattle | Phase 2 |
| H003 | Seattle corrections wait | 0.88 | seattle | Phase 2 |
| H004 | NYC stage lag | 0.85 | nyc | Phase 2 |
| H005 | NYC issue lag | 0.82 | nyc | Phase 2 |
| H006 | SF decomposition feature | 0.84 | sf | Phase 2 |
| H007 | Two-model decomposition | 0.80 | all | Phase 2.5 |
| H008 | Sentinel filter | 0.90 | sf | Phase 2 |
| H009 | Duration clip | 0.86 | all | Phase 2 |
| H010 | SF valuation delta | 0.80 | sf | Phase 2 |
| H011 | Log valuation | 0.78 | all | Phase 2 |
| H012 | Log units | 0.76 | all | Phase 2 |
| H013 | Log sqft | 0.74 | all | Phase 2 |
| H014 | Filed DOW | 0.70 | all | Phase 2 |
| H015 | Filed month cyclic | 0.72 | all | Phase 2 |
| H016 | Filed year | 0.80 | all | Phase 2 |
| H017 | Holiday flag | 0.60 | all | Phase 2 |
| H018 | COVID era | 0.74 | all | Phase 2 |
| H019 | Subtype target encoding | 0.72 | all | Phase 2 |
| H020 | Neighborhood target encoding | 0.70 | all | Phase 2 |
| H021 | Per-city model | 0.72 | all | Phase 2.5 |
| H022 | Dispatch ensemble | 0.70 | all | Phase 2.5 |
| H023 | Cox PH | 0.70 | all | Phase 2 |
| H024 | Weibull AFT | 0.68 | all | Phase 2 |
| H025 | Log-normal AFT | 0.68 | all | Phase 2 |
| H026 | Log-logistic AFT | 0.62 | all | Phase 2 |
| H027 | Random Survival Forest | 0.68 | all | Phase 2 |
| H028 | Monotone valuation | 0.72 | all | Phase 2 |
| H029 | Monotone units | 0.70 | all | Phase 2 |
| H030 | Monotone sqft | 0.68 | all | Phase 2 |
| H031 | Raw target | 0.50 | all | Phase 2 |
| H032 | Sqrt target | 0.55 | all | Phase 2 |
| H033 | Box-Cox target | 0.58 | all | Phase 2 |
| H034 | Quantile P50 | 0.64 | all | Phase 2 |
| H035 | Quantile P90 | 0.60 | all | Phase 2 |
| H036 | City x year | 0.72 | all | Phase 2 |
| H037 | Reform dummies | 0.68 | all | Phase 2 |
| H038 | SB 423 RD | 0.65 | sf/la | Phase 2.5 |
| H039 | HOME-1 RD | 0.66 | austin | Phase 2.5 |
| H040 | DOB NOW stagger | 0.60 | nyc | Phase 2.5 |
| H041 | LA business_unit | 0.82 | la | Phase 2 |
| H042 | Chicago review_type | 0.80 | chicago | Phase 2 |
| H043 | Chicago processing_time check | 0.50 | chicago | Phase 2 |
| H044 | New vs alter stratum | 0.75 | all | Phase 2.5 |
| H045 | ADU stratum | 0.68 | all | Phase 2.5 |
| H046 | WRLURI | 0.65 | all | Phase 2 |
| H047 | BPS load | 0.68 | all | Phase 2 |
| H048 | ACS density | 0.58 | all | Phase 2 |
| H049 | Mortgage rate | 0.50 | all | Phase 2 |
| H050 | BLS construction employment | 0.55 | all | Phase 2 |
| H051 | FRED housing starts | 0.50 | all | Phase 2 |
| H052 | Nbhd last-permit recency | 0.56 | all | Phase 2 |
| H053 | 30d rolling city load | 0.68 | all | Phase 2 |
| H054 | 90d rolling city load | 0.62 | all | Phase 2 |
| H055 | LightGBM | 0.60 | all | Phase 2 |
| H056 | CatBoost | 0.62 | all | Phase 2 |
| H057 | ExtraTrees | 0.50 | all | Phase 2 |
| H058 | Stacked ensemble | 0.72 | all | Phase 2.5 |
| H059 | Ridge sanity | 0.30 | all | Phase 2 |
| H060 | TabPFN small-N | 0.55 | seattle | Phase 2 |
| H061 | DeepHit | 0.58 | nyc/sf | Phase 2 |
| H062 | Deep Survival Machines | 0.55 | nyc/sf | Phase 2 |
| H063 | Cox elastic net | 0.60 | all | Phase 2 |
| H064 | GB Cox | 0.62 | all | Phase 2 |
| H065 | SF submission method | 0.70 | sf | Phase 2 |
| H066 | SF plansets | 0.58 | sf | Phase 2 |
| H067 | SF change of use | 0.68 | sf | Phase 2 |
| H068 | NYC zoning_dist1 | 0.68 | nyc | Phase 2 |
| H069 | NYC professional_cert | 0.75 | nyc | Phase 2 |
| H070 | Austin masterpermitnum group | 0.55 | austin | Phase 2 |
| H071 | Austin project_id group | 0.55 | austin | Phase 2 |
| H072 | SF parcel cluster project | 0.60 | sf | Phase 2.5 |
| H073 | Contractor frequency | 0.65 | chi/pdx | Phase 2 |
| H074 | Seattle standardplan | 0.76 | seattle | Phase 2 |
| H075 | Seattle complexity | 0.72 | seattle | Phase 2 |
| H076 | Seattle reviewer encoding | 0.72 | seattle | Phase 2 |
| H077 | Seattle reviewteam | 0.65 | seattle | Phase 2 |
| H078 | Leakage guard | 0.30 | seattle | Phase 2 |
| H079 | Seattle rework rate | 0.72 | seattle | Phase 2 |
| H080 | Seattle daysinitialplanreview | 0.78 | seattle | Phase 2 |
| H081 | Seattle daysplanreviewcity | 0.76 | seattle | Phase 2 |
| H082 | Seattle max reviewcycle | 0.75 | seattle | Phase 2 |
| H083 | NYC BIS+DOB NOW union | 0.80 | nyc | Phase 2 |
| H084 | Right-censoring labels | 0.78 | all | Phase 2 |
| H085 | Competing risks | 0.62 | all | Phase 2.5 |
| H086 | Optuna sweep | 0.65 | all | Phase B |
| H087 | Depth sweep | 0.60 | all | Phase B |
| H088 | LR sweep | 0.55 | all | Phase B |
| H089 | min_child_weight sweep | 0.55 | all | Phase B |
| H090 | Subsample sweep | 0.52 | all | Phase B |
| H091 | L1/L2 reg sweep | 0.52 | all | Phase B |
| H092 | n_estimators with early stop | 0.58 | all | Phase B |
| H093 | Era binning | 0.58 | all | Phase 2 |
| H094 | Chicago total_fee | 0.55 | chicago | Phase 2 |
| H095 | Fee per unit derived | 0.50 | chicago | Phase 2 |
| H096 | SF supervisor district | 0.60 | sf | Phase 2 |
| H097 | NYC community board | 0.64 | nyc | Phase 2 |
| H098 | LA council district | 0.58 | la | Phase 2 |
| H099 | Chicago ward | 0.70 | chicago | Phase 2 |
| H100 | Portland nbhd coalition | 0.55 | portland | Phase 2 |
| H101 | Inductive miner Seattle | 0.68 | seattle | Phase 2.5 |
| H102 | Alpha miner | 0.40 | seattle | Phase 2.5 |
| H103 | Heuristic miner | 0.55 | seattle | Phase 2.5 |
| H104 | Conformance fitness feature | 0.62 | seattle | Phase 2.5 |
| H105 | Replay stage waits | 0.60 | seattle | Phase 2.5 |
| H106 | BPIC 2015 pretrain | 0.50 | seattle | Phase 2.5 |
| H107 | Percentile-rank target | 0.48 | all | Phase 2 |
| H108 | Per-city z-score | 0.45 | all | Phase 2 |
| H109 | Multi-task heads | 0.55 | all | Phase 2.5 |
| H110 | Leave-SF-out transfer | 0.45 | all | Phase 2 |
| H111 | Leave-Seattle-out transfer | 0.40 | all | Phase 2 |
| H112 | Disaster rebuild dummy | 0.55 | all | Phase 2 |
| H113 | Planner staffing | 0.45 | all | Phase 2 |
| H114 | Feature pruning | 0.40 | all | Phase B |
| H115 | SHAP selection | 0.42 | all | Phase B |
| H116 | Nbhd 90d count | 0.55 | all | Phase 2 |
| H117 | NYC system indicator | 0.68 | nyc | Phase 2 |
| H118 | Is-duplex flag | 0.62 | all | Phase 2 |
| H119 | Reform exponential decay | 0.55 | all | Phase 2 |
| H120 | Holiday season flag | 0.52 | all | Phase 2 |

Total: 120 hypotheses. Distribution by category:
- Per-stage timing features: H002, H003, H004, H005, H006, H007, H080, H081, H082 (9)
- Process-mining derived: H079, H101, H102, H103, H104, H105, H106 (7)
- Survival analysis: H001, H023, H024, H025, H026, H027, H061, H062, H063, H064 (10)
- Right-censoring handling: H084, H085 (2)
- Domain features: H010, H011, H012, H013, H014, H015, H016, H017, H019, H020, H041, H042, H044, H065, H066, H067, H068, H069, H093, H094, H095, H096, H097, H098, H099, H100, H116, H118, H120 (29)
- City-specific vs shared: H021, H022, H109, H110, H111, H117 (6)
- Macro context: H046, H047, H048, H049, H050, H051 (6)
- Monotonicity: H028, H029, H030 (3)
- Target transforms: H031, H032, H033, H034, H035, H107, H108 (7)
- Hyperparameter sweeps: H086, H087, H088, H089, H090, H091, H092 (7)
- Model-family pivots: H055, H056, H057, H060 (4)
- Ensembles: H058 (1)
- Reform experiments: H036, H037, H038, H039, H040, H119 (6)
- Permit-type stratification: H044, H045, H118 (3)
- External shocks: H018, H112, H113 (3)
- Data hygiene and loader fixes: H008, H009, H043, H070, H071, H072, H073, H074, H075, H076, H077, H078, H083 (13)
- Feature engineering ablation: H052, H053, H054, H114, H115 (5)
