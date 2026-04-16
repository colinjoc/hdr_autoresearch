# Design variables — Phase B discovery

Goal: for a prospective developer choosing a site, predict P(commencement within 5 years) given site-and-scheme characteristics that are fixed at site-selection time.

## Design variables

| variable | levels | dimensionality | rationale |
|----------|--------|----------------|-----------|
| planning_authority | 31 LAs | 31 | regulatory + market heterogeneity |
| size_band | 1, 2-4, 5-49, 50+ | 4 | scheme-size economics |
| app_type | PERMISSION, OUTLINE PERMISSION | 2 | build-ready vs preliminary |
| one_off | yes/no | 2 | personal vs corporate dev |
| dublin_flag | dublin / non-dublin | 2 | market-tier shortcut |
| grant_year_cohort | 2014-16, 2017-19, 2020-22, 2023+ | 4 | regime + cycle |

Cross-product: 31 × 4 × 2 × 2 × 2 × 4 = 3,968 strata (many will be empty; meaningful strata ~200-500).

## Discovery question

Which (planning_authority, size_band, app_type) strata have commencement probability < 0.4 (i.e., > 60% lapse expected)? These are the "danger cells" a developer should know about before purchasing a site to permission or acquiring an existing permission. Conversely, cells with predicted commencement > 0.8 are reliable-delivery strata.

## Output

`discoveries/commencement_probability_by_stratum.csv` with columns:
`planning_authority, size_band, app_type, dublin_flag, n_permissions, p_commence, p_commence_lower95, p_commence_upper95, median_time_to_commence_days, risk_category`

Risk categories:
- RELIABLE (p > 0.75)
- MODERATE (0.5 ≤ p ≤ 0.75)
- RISKY (0.25 ≤ p < 0.5)
- DANGER (p < 0.25)

## Scope limits

- The predictor cannot observe future macro conditions; predictions are conditional on historical 2014-2019 exercise patterns continuing.
- Strata with n < 30 are reported with wide CIs and excluded from top-K lists.
- OUTLINE PERMISSION by construction cannot commence without a subsequent PERMISSION grant, so its reported p_commence is materially a lower bound on its development probability.
