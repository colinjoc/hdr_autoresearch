# Adversarial Paper Review: Heat Mortality / Night-Time Wet-Bulb Hypothesis

## Summary verdict

This paper attempts a strong negative claim -- that night-time wet-bulb temperature should not be used as the primary indicator in heat-health early warning systems -- and backs it with a methodologically inventive HDR loop framework. The dataset (30 cities, 13 years, ~9,300 city-weeks) is respectable. However, several critical design choices severely limit the strength of the refutation: the weekly aggregation grain almost certainly destroys the diurnal signal the hypothesis concerns; the cross-validation scheme leaks temporal information; the binary label construction is partially tautological with the top-ranked feature; and the paper's headline language ("refuted") is far too strong for what is actually shown ("not detectable at this aggregation scale with this methodology"). The robustness battery is commendably broad but every specification shares the same structural weaknesses. The result is an interesting null finding wrapped in overclaiming.

## Findings

### 1. Claims vs evidence

**1a. "The hypothesis is refuted" (title, abstract, Section 5.10, Section 7).** The paper shows that night-time wet-bulb features do not improve MAE or AUC over a baseline that already contains daytime wet-bulb, Tmax, Tmin, Tavg, and dewpoint at weekly aggregation. This is evidence of non-detectability at this scale, not a refutation of the physiological hypothesis. The paper acknowledges this distinction in the Discussion (Section 6.1) but the title, abstract, and headline box (Section 5.10) do not carry the qualifier. **Severity: CRITICAL.**

**1b. Keep/revert threshold of 0.5 deaths as a noise floor.** The paper states this is the noise floor but provides no empirical justification for it. No bootstrap confidence intervals, no permutation-based null distribution, no repeated CV with different seeds. The actual CV variance is never reported. If the fold-to-fold MAE standard deviation is, say, 3.0 deaths/week, then most of the 22 flagship features' deltas are well within noise regardless of whether 0.5 is the right floor. Conversely, if fold variance is 0.2 deaths, the floor is too generous and real signals are being discarded. This is a foundational methodological gap. **Severity: CRITICAL.**

**1c. Phase 2 MAE improvement from 47.49 to 40.33 claimed as 15.1% relative improvement.** The arithmetic checks out (7.15/47.49 = 15.05%). However, the bulk of this improvement comes from autocorrelation features (prior_week_pscore, prior_4w_mean_pscore) which introduce severe information leakage in a shuffled KFold setting (see 1d). **Severity: MAJOR.**

**1d. Shuffled KFold with autocorrelation features.** The paper uses KFold(shuffle=True) while including lag-1 and lag-4 p-score features. In a shuffled split, the held-out fold will contain weeks whose prior-week p-score was computed from the training data, creating direct temporal leakage. The paper acknowledges shuffled vs temporal splits in Section 6.5 but does not acknowledge that the autocorrelation features specifically exacerbate this. The 15% MAE improvement is almost certainly inflated. **Severity: CRITICAL.**

**1e. AUC 0.9696 for the minimal detector.** The paper claims 98.9% of the full model's AUC from just 2 features. One of these features is `consecutive_days_above_p95_tmax`, which is a direct component of the binary label definition (`label_lethal_heatwave = (p_score >= 0.10) AND (consecutive_days_above_p95_tmax >= 1)`). A classifier that perfectly predicts one of the two AND conditions will trivially achieve near-perfect AUC. This is a label-leakage tautology and the paper's own Section 6.3 partially acknowledges it -- but then proceeds to use the AUC as evidence against the night-time wet-bulb hypothesis anyway. If the label includes the feature, the AUC is not evidence of anything except label construction. **Severity: CRITICAL.**

**1f. Counterfactual EWS miss rates (Section 5.9.4).** The EWS comparison uses a rank-based top-5%-of-weeks alert rule, but the specific ranking method for each configuration is not fully specified. How is the "literature tw_night_c_max rank" rule operationalised? Is it a simple rank on the raw value, a percentile exceedance, or a threshold crossing? Different implementations of "the literature rule" could yield very different miss rates. The claim that night-Tw is "strictly worse" depends on this implementation detail. **Severity: MAJOR.**

**1g. No confidence intervals on any reported metric.** MAE, RMSE, R-squared, AUC, Brier score, miss rates, false-alarm rates -- none carry uncertainty estimates. For a paper whose central claim rests on the inability of features to cross a threshold, the absence of statistical uncertainty quantification is a fundamental omission. **Severity: CRITICAL.**

### 2. Scope vs framing

**2a. Title says "Refuting" -- Discussion says "not detectable at this aggregation scale."** The title "Refuting the Night-Time Wet-Bulb Hypothesis" is not supported by the paper's own caveats. The Discussion (Sections 6.1, 6.6) correctly notes that (a) weekly aggregation washes out the diurnal cycle, (b) the appropriate test is individual-level cohort data, and (c) the physiological measurements are not contradicted. The title should say something like "Night-time wet-bulb temperature does not improve population-week mortality prediction" or similar. **Severity: CRITICAL.**

**2b. Abstract claims "pre-registered."** The paper defines "pre-registered" as "the 116 hypotheses were specified in research_queue.md before the Phase 2 loop was run." This is not pre-registration in the standard scientific sense (e.g., OSF, ClinicalTrials.gov, or AsPredicted). A file in a code repository is not an immutable, timestamped, third-party-verified pre-registration. The paper should either use a different term (e.g., "pre-specified") or provide evidence of genuine pre-registration. **Severity: MAJOR.**

**2c. "9,276 city-weeks across 30 cities" framing suggests large sample.** But 9,276 / 30 = ~309 weeks per city on average, London has only 114. The effective sample for testing a per-city night-time signal is 100-470 weeks depending on city. For rare events (lethal heat weeks at 3.7% base rate), this is approximately 4-17 lethal events per city. The paper acknowledges sparse per-city counts in Section 6.5 but the headline framing emphasises the pooled 9,276 number. **Severity: MINOR.**

### 3. Reproducibility

**3a. Data sources are named but not versioned.** The paper references "NOAA Integrated Surface Database (ISD)" and "Eurostat demo_r_mwk3_t" and "CDC NCHS" without specifying exact download dates, API query parameters, or dataset version numbers. ISD is a living database that receives updates and corrections. A reader attempting replication in 2027 may get different data. **Severity: MAJOR.**

**3b. Station assignment ("primary airport GHCN-H station") is underspecified.** Which station for each city? Station IDs are not listed. For cities with multiple airports (New York: JFK, LGA, EWR; Chicago: ORD, MDW; London: Heathrow, Gatwick, City), the choice matters for overnight temperatures. **Severity: MAJOR.**

**3c. CDC state-to-city scaling method.** The paper notes "We scale state-level data to city population shares" but does not specify the population source, vintage, or whether static or time-varying shares are used. State-level weekly mortality scaled to city population is a substantial approximation for 15 of the 30 cities. **Severity: MAJOR.**

**3d. The code snippets reference internal modules** (`data_loaders.py`, `model.build_clean_dataset`, `evaluate.py::cross_validate`, `build_phase2_cache.py`) that are part of a private repository. The standalone code block in Section 3.2 requires a pre-built `panel` DataFrame whose construction is not fully specified in the paper. **Severity: MINOR.**

**3e. Wet-bulb computation precision.** The paper says Stull (2011) is accurate to ~0.3-0.7 C. For features like `tw_night_c_max` where the hypothesis concerns thresholds near 24-30 C, a 0.7 C error could matter. The paper tests Davies-Jones as R03 and finds no flip, but R03 operates "at the weekly aggregate level" -- was the hourly computation also swapped? If not, the weekly aggregate of an inaccurate hourly series and the weekly aggregate of an accurate hourly series may not differ much. **Severity: MINOR.**

### 4. Missing experiments

1. **Temporal cross-validation.** Train on 2013-2019, test on 2023-2025 (excluding pandemic). This is essential for validating the autocorrelation-heavy Phase 2 best model and for any forecasting claim. The shuffled KFold inflates performance of temporally-leaking features.

2. **Bootstrap or permutation null distribution for the keep/revert threshold.** Run 1,000 permutations of each flagship night-Tw feature (shuffle feature values within city-season strata) and compute the MAE delta distribution. Report where the observed deltas fall relative to this null. Without this, "noise floor" is an assertion, not a measurement.

3. **Remove label-feature coupling from the binary target.** Define lethal weeks as `p_score >= 0.10` only (without the `consecutive_days_above_p95_tmax >= 1` meteorological gate). Re-run R09, the minimal detector, and the counterfactual EWS. This eliminates the tautological AUC inflation.

4. **Hourly or daily resolution analysis.** The paper's own Discussion identifies weekly aggregation as the most likely reason for the null finding. Even a sub-analysis at daily resolution for a subset of cities would dramatically strengthen or weaken the claim.

5. **Interaction terms.** Test night-Tw x vulnerability indicators (e.g., city heat-acclimatization proxy, latitude, baseline mortality level). The current single-change protocol tests marginal additions but not interactions, which is how the epidemiological literature frames the night-time effect.

6. **Matched case-crossover design within the panel.** For each lethal heat-wave week, match to 3-4 control weeks in the same city and same month of a different year. Test whether night-Tw differs between cases and controls after conditioning on daytime Tmax. This is closer to the epidemiological standard (Achebak et al. 2022) than a regression approach.

7. **Multi-seed sensitivity.** Re-run the full Phase 2 loop with random_state = {0, 1, 2, 3, 4} and report the distribution of KEEP/REVERT decisions. If any of the 22 flagship features flip between KEEP and REVERT across seeds, the paper's deterministic conclusion is fragile.

8. **True age-stratified analysis.** The paper repeatedly notes R02 is a proxy. Eurostat does provide age-stratified weekly mortality (`demo_r_mweek3` with age bands). This is a must-have before a policy recommendation to abandon night-time wet-bulb monitoring.

9. **Tropical and subtropical city extension.** The paper's city set is largely temperate. The wet-bulb hypothesis is most relevant where Tw regularly approaches 28-32 C (South/Southeast Asia, Gulf states, West Africa). Testing on only temperate cities and concluding the hypothesis is "refuted" globally is a scope mismatch.

10. **Separate summer-only analysis.** The full-year panel includes winter weeks where night-time wet-bulb is irrelevant. A June-September (Northern Hemisphere) restriction would give the night-time hypothesis its best chance and reduce dilution from cold-season data.

### 5. Overclaiming and language

**5a. "Refuted" (title, abstract, Sections 5.10, 7).** This is the language of deductive logic or controlled experiment. What was shown is "not supported by this observational analysis at weekly aggregation." The paper should use "not supported," "not detected," or "does not improve prediction" rather than "refuted." **Severity: CRITICAL.**

**5b. "Pre-registered" (abstract, Section 1.3).** As noted in 2b, specifying hypotheses in a code file before running them is pre-specification, not pre-registration. The term "pre-registered" carries specific methodological meaning in the social and health sciences (e.g., Nosek et al. 2018). **Severity: MAJOR.**

**5c. "Strictly worse" (Section 5.9.4, Section 6.8).** The night-Tw EWS rule is described as "strictly worse" and "strictly dominated." Strict dominance has a precise game-theoretic meaning (worse in every dimension). The paper shows it is worse in miss rate and false-alarm rate at one specific alert budget (top 5% of weeks). At other alert budgets, the ordering might change. "Worse at the tested alert budget" is accurate; "strictly dominated" requires showing it is worse at every possible threshold, which was not done. **Severity: MAJOR.**

**5d. "The recommendation to heat-health early warning system developers is to focus on dry-bulb extremes" (Section 7).** A policy recommendation based on a single observational study at weekly aggregation with acknowledged data limitations (no tropical cities, no age strata, no individual exposure, label-feature coupling) is overclaiming. The appropriate recommendation is "our findings do not support prioritizing night-time wet-bulb over dry-bulb indicators at the population-week scale, and further investigation at finer temporal and individual-level resolution is warranted." **Severity: MAJOR.**

**5e. "The hypothesis is refuted" appears in the abstract without any qualifier.** The abstract should carry the same limiting conditions as the Discussion: weekly aggregation, temperate cities, all-ages, observational. **Severity: CRITICAL.**

### 6. Literature positioning

**6a. Missing engagement with the case-crossover and time-series crossover literature.** Achebak et al. (2022) and Roye et al. (2021) use case time-series and distributed-lag designs, not regression with shuffled KFold. The paper notes the "difference in statistical model" (Section 6.7) but does not seriously engage with why a KFold regression might produce different results from a case time-series design. The methodological gap between the cited literature's approach and this paper's approach is substantial and under-discussed. **Severity: MAJOR.**

**6b. Selective citation of Gasparrini et al.** The paper cites Gasparrini et al. (2015) for the lag structure finding but does not cite Gasparrini and Armstrong (2011) "The impact of heat waves on mortality" or Gasparrini et al. (2017) "Projections of temperature-related excess mortality," both of which discuss humidity's modifying role. The literature review, while reasonable, is narrower than the 100+ citations appropriate for a paper making a strong negative claim against a substantial body of work. The reference list has only 17 entries. **Severity: MAJOR.**

**6c. No citation of Di Napoli et al. (2022) Universal Thermal Climate Index (UTCI) literature.** The UTCI is the operational heat-stress index used by several European NHSs (ZAMG, DWD) and integrates radiation, wind, humidity, and clothing. It is conspicuously absent from a paper about which heat index EWSs should use. **Severity: MINOR.**

**6d. No citation of the ISO 7243 WBGT standard or Liljegren et al. (2008).** Wet-bulb globe temperature is the occupational heat standard and the military standard. A paper about wet-bulb temperature in EWSs should position itself relative to WBGT. **Severity: MINOR.**

**6e. Claim of novelty for testing the night-Tw hypothesis on a multi-city panel.** The MCC Network (Gasparrini et al. 2015 and subsequent papers) has tested many heat metrics across 700+ locations. While the specific HDR loop framework is novel, the act of testing night-time temperature metrics on multi-city panels is not unprecedented. The novelty claim should be more precisely scoped to the HDR methodology and the specific comparison at the weekly aggregation level. **Severity: MINOR.**

## Severity summary
- CRITICAL: 6
- MAJOR: 10
- MINOR: 7
