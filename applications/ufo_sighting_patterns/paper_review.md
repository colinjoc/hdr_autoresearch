# Blind Review: Phase 2.75

## Summary

The paper analyzes 147,890 NUFORC reports across temporal, spatial, categorical, and predictive dimensions. The descriptive analyses are thorough and the framing as reporting-behavior sociology is appropriate. However, several claims lack adequate statistical support, and two key results are potentially misleading.

## Major Issues

### M1. "Peak 2014 tracks internet adoption" -- asserted, not tested

Section 6.1 states the 14.4% CAGR "mirrors internet adoption" but presents zero quantitative evidence. No internet penetration time series is correlated with sighting volume. The claim could be tested by correlating annual sighting counts with ITU/World Bank internet adoption rates for the US. Without this, the causal framing is speculation. The post-2014 decline is attributed to "platform fragmentation" with equally no evidence.

**Required**: Add E30 -- correlate annual sighting counts with US internet adoption (% households with broadband, readily available from NTIA/Census). Report Pearson r and p-value for growth phase (1990-2014).

### M2. Starlink +25% formation increase is fractional, not absolute -- misleading

The paper headlines "25% increase in formation reports" (DISC02), but this is the fractional share within a declining total. E11 shows the absolute formation rate only increased 1.07x (15.1/mo to 16.2/mo). The fractional increase is largely an artifact of non-formation categories declining faster. The paper must report both absolute and fractional rates and explain the discrepancy. Furthermore, no baseline trend control exists: formation fraction was already variable pre-Starlink (ranging 1.0% to 7.9% monthly). A proper test would use interrupted time series analysis (ITS) or at minimum compare the pre-Starlink trend slope to the post-Starlink slope.

**Required**: Add E31 -- interrupted time series or segmented regression on monthly formation fraction, testing whether the post-Starlink intercept shift is significant after controlling for pre-existing trend. Report both absolute and fractional rates in the paper.

### M3. Poisson regression ignores overdispersion

T05 uses standard Poisson regression (coefficient 0.66, 57.3% deviance explained) but reports no overdispersion diagnostic. With state-level count data, overdispersion is virtually guaranteed (Pearson chi2 / df >> 1). If the Pearson chi2 in the results is large relative to n-p, standard errors are underestimated and the z=242.5 is inflated. A negative binomial or quasi-Poisson model should be compared.

**Required**: Add E32 -- fit negative binomial regression alongside Poisson. Report dispersion parameter (alpha), compare AIC/BIC. If alpha > 0 (overdispersed), report NB coefficients as primary and note Poisson SEs are invalid.

### M4. Classifier F1=0.33 -- paper understates the failure

The paper says F1=0.33 "substantially outperform[s]" the other models, but 0.33 is functionally useless for prediction. The discussion acknowledges limitations but Section 5.5 frames this as a genuine finding rather than a null result. With 200:1 class imbalance and year-of-report dominating at 71.7%, the classifier is essentially learning "recent reports get explanations" -- it has no predictive power for explainability per se. The paper should explicitly state this is a null result for intrinsic-feature prediction.

**Required**: Revise Section 5.5 to explicitly frame F1=0.33 as a practical null result. Add: "The classifier cannot distinguish inherently explainable from unexplainable sightings; it merely detects the recency of the annotation program."

### M5. "Cultural archetype shift" (disk to orb) -- untestable as stated

Section 6.2 claims shape evolution "tracks cultural archetype shifts" but provides no measurement of cultural archetypes. This could be partially tested by correlating shape fractions with media depiction data (e.g., Google Ngrams for "flying saucer" vs "orb" vs "UFO orb"). Without any cultural indicator, this is interpretive commentary, not a finding.

**Required**: Add E33 -- download Google Ngrams data for "flying saucer", "UFO orb", "UFO triangle" and correlate annual frequency with NUFORC shape fractions. Report correlation coefficients. If data access fails, reframe Section 6.2 as hypothesis rather than finding.

### M6. Geocoded dataset ends 2013 -- spatial analysis misses Starlink era

The geocoded subset (80,332 reports through 2013) is used for all spatial analyses (clustering, infrastructure proximity, Poisson regression) but cannot address the most interesting spatial question: where do Starlink-era formation reports cluster? This is acknowledged in limitations (Section 6.4) but the paper doesn't attempt geocoding from the city/state text fields in the primary dataset, which would be straightforward for US reports.

**Required**: Add E34 -- geocode state-level formation reports from the primary dataset (text-based state field already parsed) and test whether post-Starlink formation reports concentrate in states with better satellite-viewing conditions (higher latitude, lower light pollution). This does not require exact coordinates -- state centroids suffice.

## Minor Issues

### m1. E11 vs DISC02 inconsistency
Results.tsv shows E11 formation_rate_ratio = 1.07 but DISC02 = 1.25. The paper only reports 1.25. Both should be reported with clear labeling (absolute vs fractional).

### m2. Permutation test E24 reports p=1.0
This is suspicious -- a permutation of day-of-week labels should not change the chi-square much since permutation reshuffles individual observations (not aggregates), making the test invalid. The test permutes individual-level labels, which preserves the marginal distribution. This is not a meaningful permutation test. Remove or replace with a proper block-bootstrap test.

### m3. Clock-hour rounding decline
The 47.6% to 23.3% decline is well-documented but the paper does not test whether this correlates with smartphone adoption specifically. This is a minor point but the smartphone explanation is asserted without evidence.

### m4. Infrastructure proximity without population control
Acknowledged in limitations but should be more prominent. The 6% near military bases and 11.6% near airports are meaningless without population-density baselines.

## Verdict

**Major revision required.** The descriptive patterns are solid, but five of six major issues involve claims that are asserted without quantitative support. The Starlink analysis conflates fractional and absolute rates. The Poisson model likely has invalid standard errors. The cultural-shift and internet-adoption claims need at minimum correlational evidence.

Priority order: M2 (Starlink ITS) > M3 (overdispersion) > M1 (internet correlation) > M4 (null result framing) > M5 (Ngrams) > M6 (state-level spatial).
