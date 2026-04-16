# Phase 2.75 Blind Review — IE Gender Pay Gap 2022-2025

**Reviewer**: blind agent, retroactive
**Date**: 2026-04-15
**Artefacts**: `paper.md`, `analysis.py`, `data/raw/paygap_ie_*.csv`

## Decision

**Major revisions required.** The descriptive trajectory is sound, but the headline claim — that Ireland is narrowing "nearly 2×" the UK rate — is not defensible on the current analysis because the reporting-threshold phase-down (250→150→50 employees across 2022-2026) is a massive composition confound that has not been quantified, and the cross-country comparison uses mismatched windows and endpoints with no uncertainty quantification. The within-firm panel (n=623) is the only part of the evidence that survives the composition critique, and it is under-weighted in the headline.

## Headline concerns

1. **Threshold-phasing composition confound is not decomposed.** The sample grew from 709 (2022) to 1,580 (2025) because the threshold dropped from 250 to 150 employees. Smaller firms are systematically less occupationally stratified and have lower gaps. The paper acknowledges this in §4.4 point 2 and §6.2 but makes no attempt to decompose population-level narrowing into (a) within-firm reform, (b) entry of new firms below the old threshold, and (c) exit/turnover. The headline 7.00%→6.22% trajectory is therefore contaminated by an unknown mix of real reform and sample composition. A Blinder-Oaxaca or simple re-weighting to the 2022 firm-size distribution is mandatory before the −0.26pp/yr rate can be compared to anything.

2. **UK vs IE comparison is apples-to-oranges.** UK 2017-2025 is an 8-year window starting at 9.30%; IE 2022-2025 is a 3-year window starting at 7.00%. Rates of narrowing are not linear in regime maturity — there is no reason a priori to expect the UK's 2017-2020 rate (early-regime) to equal its 2017-2025 average rate. The correct comparator is the UK's first three years post-regime (2017-2020) vs IE 2022-2025. The paper's own §4.4 raises diminishing-returns then dismisses it on a handwave; the proper treatment is to show the year-by-year UK rate alongside IE.

3. **No uncertainty on −0.26pp/yr.** Two linear-fit endpoints with no standard error, no bootstrap, no confidence interval. "Nearly 2×" is a point-estimate claim against another point-estimate with no overlap analysis. A bootstrapped CI over employer-years is a 20-line addition to `analysis.py`.

4. **paygap.ie data provenance is under-scrutinised.** Volunteer-maintained scrape of employer-published reports. No audit of completeness against the IBEC or CSO universe of ≥150-employee firms. If coverage is 60-80% of the mandated universe, there may be systematic non-reporter bias (low-transparency firms opt out, and those may be the highest-gap firms). A coverage-rate-vs-mandated-universe figure is needed; otherwise we cannot rule out "apparent narrowing is declining non-reporter bias."

5. **Within-firm panel is itself composition-selected.** The 623 firms reporting in both 2022 and 2025 are large (≥250 in 2022) and persistent. These are exactly the firms with the most resources to act on the regime, so −0.87pp median narrowing is an upper bound on reform among smaller firms. The paper should explicitly mark the 623-firm panel as a ceiling estimate for the post-2022 cohort.

6. **NACE-section granularity is too coarse in places.** Real Estate n=7, Mining n=3. These are headline table entries. A 28.6% median on 7 firms has a very wide CI and should either be dropped from the headline or have its bootstrap CI shown.

7. **No pre-regime baseline.** The paper explicitly notes this in §5.2 ("not causal"), but then the abstract and conclusion still claim the regime is "associated with" narrowing, which reads causally. Either soften the framing throughout or run a synthetic-control against a matched no-regime country (a non-mandatory-reporting EU comparator such as Italy or Spain pre-2022).

## Mandated experiments

| # | Experiment | Status | Rationale |
|---|---|---|---|
| M1 | **Threshold-invariant sub-sample re-analysis**: restrict all four years to firms ≥250 employees (the 2022 threshold, using headcount-quartile proxy or size field from paygap.ie). Re-compute median-of-medians trajectory and annualised narrowing rate on this stable population. | **TODO** | Directly isolates real narrowing from phase-down composition. If the rate on this constant-threshold sub-sample falls to e.g. −0.15pp/yr, the UK-vs-IE "2×" headline must be retracted. |
| M2 | **Bootstrap confidence intervals on annualised rate**: block-bootstrap over employer-year observations, 1,000 reps, report 95% CI on the IE −0.26pp/yr and UK-equivalent-window −0.Xpp/yr rates. | **TODO** | Required before any "nearly 2×" comparison. Without this, the headline is a point-vs-point comparison. |
| M3 | **Window-matched UK comparator**: recompute UK narrowing rate for UK 2017-2020 (first 3 years post-regime, matching IE 2022-2025 window). Include in the cross-country table and abstract. | **TODO** | Removes the diminishing-returns / window-length confound. This is the correct cross-country comparison. |
| M4 | **Blinder-Oaxaca decomposition of population change**: decompose 2022→2025 median shift into (a) within-firm component (persistent panel), (b) entry component (new firms 2023-2025), (c) exit component. Report each as pp contribution. | **TODO** | Quantifies exactly how much of the headline −0.78pp is composition vs reform. This is the paper's central question. |
| M5 | **paygap.ie coverage audit**: scrape or request the CSO/IBEC list of Irish firms ≥150 employees for 2024 and 2025; compute paygap.ie coverage rate. If <90%, model non-reporter selection bias. | **TODO** | Data-provenance due diligence. Volunteer-scraped sources routinely miss the most opaque reporters. |
| M6 | **Sector CI table**: bootstrap 95% CI on each NACE section median for 2025. Drop or asterisk any section with n<10 in the headline table. | **TODO** | Real Estate (n=7) and Mining (n=3) are not reportable as point estimates in an abstract. |

## Things done well

1. **Within-firm panel is the right estimator.** The 623-firm change-score analysis is the single most defensible result in the paper and correctly identifies the 56.5%-narrowed share and −0.87pp median. This should become the headline, with the population trajectory demoted to a sensitivity check.
2. **Limitations section is honest** about threshold phasing, scrape provenance, short window, and small sector bases. The critique is that the headline does not reflect these limitations strongly enough.
3. **Sector dispersion finding is robust and interesting** even with the n-size caveat — the 28-point top-to-bottom range is the paper's most policy-relevant contribution and warrants more space than the UK comparison.
4. **Reproducible analysis pipeline**: `analysis.py` is short, self-contained, writes to `discoveries/` and `results.tsv` with experiment IDs. Easy to extend for M1-M6.
5. **Right question asked.** "Has the regime moved the needle?" is the correct framing; the methodological gaps are fixable within Phase B without redesigning the project.

## Recommendation

Block Phase 3 sign-off until M1 (threshold-invariant re-analysis) and M3 (window-matched UK) are complete. M2, M4, M6 are required for publication-quality claims but can run in parallel. M5 (coverage audit) can be deferred to Phase B if the CSO list is not reachable within the standard data-access budget.
