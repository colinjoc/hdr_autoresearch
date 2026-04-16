# Irish Gender Pay Gap Reporting 2022-2025: A Within-Firm Narrowing, Not Yet Distinguishable From Noise at the Population Level

**Phase 3 (retroactively revised 2026-04-15 after Phase 2.75 reviewer cycle).** HDR autoresearch.

## Abstract

Ireland's Gender Pay Gap Information Act 2021 brought mandatory annual reporting into force for employers with 250+ staff from 2022, with the threshold phasing down to 150 staff (2024) and 50 staff (2026). Using the independent-maintained paygap.ie archive of employer filings (3,991 employer-year submissions across 2022-2025, 1,712 unique employers), the population median hourly pay gap fell from 7.00% (2022) to 6.22% (2025), an annualised rate of **−0.26 percentage points per year (95% CI −0.60 to +0.14 pp/yr; cluster-bootstrap over firms)**. With only three years of post-regime data, the population-level rate is **not yet statistically distinguishable from zero**. The within-firm panel (623 firms reporting in both 2022 and 2025) is the most defensible estimator and shows a median narrowing of **−0.87 pp with 56.5% of firms narrowing** — and a Blinder-Oaxaca-style decomposition attributes essentially all of the population −0.78pp shift to this within-firm component (−0.90 pp), with entrant-firm composition contributing only +0.02 pp and exit contributing +0.10 pp. The **Ireland-vs-UK "nearly 2×" headline from the original draft does not survive reviewer scrutiny**: when the UK window is matched to Ireland's (first three years post-regime, 2017-2020), the UK gap *widened* by +0.23 pp/yr against a COVID-disrupted baseline, and when the UK window is matched to the same calendar years as Ireland's (2022-2025), the UK narrowed at −0.36 pp/yr — faster than Ireland. The policy-relevant finding that does survive is sector dispersion: a 28-point range between Real Estate (28.6%, n=7, 95% CI [22, 40]) and Water/Waste (−3.0%, n=5), with Construction (21.5%), Finance (14.3%) and Manufacturing (7.6%) persistently high and Public Administration and Human Health at or below zero.

## 1. Question

Ireland's mandatory-disclosure regime is three years old in 2025. Has the population gender pay gap moved? Is that movement real within-firm reform or a composition artefact of the threshold phase-down bringing smaller (generally lower-gap) firms into the reporting pool? And how does Ireland's pace compare to an equivalent-duration window of the UK's regime?

## 2. Data

**paygap.ie**: an independent public-service portal that has scraped and aggregated Irish employer gender-pay-gap (GPG) reports since 2022 while awaiting a central government portal. Full CSV archive 2022-2025, 3,991 employer-years across 1,712 unique companies. Schema: company name, NACE section/letter/division, mean and median hourly gap, bonus gap, part-time and part-temp gap, bonus and benefit-in-kind participation, quartile composition, link to underlying report.

The Gender Pay Gap Information Act 2021 initial reporting threshold (2022) was 250+ employees; from 2024 the threshold is 150+, and from 2026 it will be 50+. The population sample therefore grew from 709 (2022) to 1,580 (2025) through a mix of threshold phase-down and genuine new-firm entry.

**UK comparator**: the UK Office for National Statistics EMP-02 regime, mandatory since 2017 for employers with 250+ staff. Annual medians extracted from the sibling `uk_gender_pay_gap` project (Phase 3) across 2017-2025.

## 3. Methods

- Annual median-of-medians across employer-year submissions (population-level).
- **Threshold-invariant subsample**: restrict to the cohort of firms that reported in 2022 (a proxy for ≥250 employees at the original regulatory threshold, since the 2022 filing population is, by regulation, the ≥250 cohort). Track median gap on this stable cohort across 2022-2025. 705 firms in 2022, 623 still reporting in 2025.
- **Within-firm panel**: companies appearing in both 2022 and 2025 (n=623), change-score analysis with share-narrowing.
- **Bootstrap 95% CI**: cluster-bootstrap over firms (1,000 replicates), recompute yearly median-of-medians and annualised rate per replicate.
- **Blinder-Oaxaca-style decomposition**: decompose the population change `m25_full − m22_full` into a within-firm component (`m25_persistent − m22_persistent`), an entrant component (`m25_full − m25_persistent`), and an exit component (`m22_persistent − m22_full`). The three sum exactly to the observed total.
- **NACE-sector stratification on 2025** with bootstrap 95% CI per section.
- **Cross-country rate-of-narrowing comparison** against the UK EMP-02 annual trajectory, computed across three matched windows: UK 2017-2025 (full), UK 2017-2020 (regime-age-matched to IE 2022-2025), and UK 2022-2025 (calendar-year-matched).

## 4. Results

### 4.1 Annual population trajectory

| Year | n submissions | median of medians | mean of medians |
|---|---|---|---|
| 2022 |   709 |  7.00% | 10.60% |
| 2023 |   740 |  6.60% |  9.80% |
| 2024 |   962 |  6.40% | 10.00% |
| 2025 | 1,580 | **6.22%** |  9.58% |

Three-year population-level narrowing: median −0.78 pp, mean −1.02 pp. Submission count roughly doubled as the threshold phased down.

**Bootstrap 95% CI on the annualised rate**: −0.26 pp/yr [−0.60, +0.14]. With three post-regime years the point estimate is suggestive of narrowing but *not statistically distinguishable from zero* at the 5% level. Claims of "the Irish regime is narrowing the gap" must be conditioned on this uncertainty until a longer window accrues.

### 4.2 Threshold-invariant subsample (≥250 cohort, via firms-first-reported-2022)

| Year | n | median gap |
|---|---|---|
| 2022 | 705 | 7.00% |
| 2023 | 676 | 6.28% |
| 2024 | 648 | 6.13% |
| 2025 | 623 | 6.20% |

Annualised rate: **−0.267 pp/yr, 95% CI [−0.60, +0.10]**. The threshold-invariant cohort narrows at essentially the same rate as the full population (and also remains statistically indistinguishable from zero at 95%). This is reassuring for interpretation: the phase-down of the reporting threshold did *not* drive the headline narrowing; **the narrowing is happening inside firms that were always in the reporting pool**.

### 4.3 Within-firm panel (2022 + 2025, n=623)

- Median gap 2022: 7.10%
- Median gap 2025: 6.20%
- **Median within-firm change: −0.87 pp**
- **56.5% of firms narrowed** their gap.

### 4.4 Blinder-Oaxaca-style decomposition of the population −0.78 pp shift

| Component | pp contribution to 2022→2025 median shift |
|---|---|
| Within persistent firms (n=623)          | **−0.90** |
| Entry (new firms 2023-2025, n=935)       |   +0.02 |
| Exit (firms in 2022 only, n=82)          |   +0.10 |
| **Total (= observed m25_full − m22_full)** | **−0.78** |

**Essentially all of the population-level narrowing is within-firm reform.** Entrant firms coming in under the reduced threshold were (marginally) slightly *higher-gap* than the persistent set at their time of entry, contributing a tiny +0.02 pp offset. Exiting firms were also marginally higher-gap in 2022 than the persistent set, contributing +0.10 pp. Neither composition channel is quantitatively important. The regulatory phase-down has not mechanically lowered the headline.

### 4.5 Sector dispersion (2025) with bootstrap 95% CI

**Worst five sectors** by median 2025 hourly gap:

| NACE Section | n | Median | 95% CI | Flag |
|---|---|---|---|---|
| Real Estate Activities                | 7   | 28.64% | [22.00, 40.00] | n<10 |
| Mining and Quarrying                  | 3   | 23.72% | [19.80, 27.00] | n<10 |
| Construction                          | 58  | 21.53% | [15.99, 24.90] |  |
| Electricity Gas Steam A/C Supply      | 22  | 18.10% | [ 9.25, 25.66] |  |
| Financial and Insurance Activities    | 168 | 14.30% | [12.00, 16.25] |  |

**Smallest and negative gaps**:

| NACE Section | n | Median | 95% CI | Flag |
|---|---|---|---|---|
| Agriculture Forestry Fishing          |  12 |  1.80% | [−3.71,  3.91] |  |
| Accommodation and Food Service        | 131 |  1.47% | [ 1.00,  2.00] |  |
| Human Health and Social Work          | 114 |  0.00% | [−1.15,  0.70] |  |
| Public Administration and Defence     | 114 | −0.08% | [−2.40,  2.00] |  |
| Water Supply Sewerage Waste           |   5 | −2.98% | [−26.09, 12.61] | n<10 |

Real Estate (n=7), Mining (n=3), and Water/Waste (n=5) have wide CIs and should be treated as suggestive only — Water/Waste's CI spans 39 points. Construction, Finance, Manufacturing, and Professional/Scientific/Technical (collectively ~575 firms) are the robust high-gap sectors.

### 4.6 Cross-country comparison (window-matched)

| Country / Window | First | Last | Years | pp/year |
|---|---|---|---|---|
| UK 2017-2025 (full regime to date)                 | 9.30% | 8.11% | 8 | −0.149 |
| **UK 2017-2020** (regime-age-matched to IE)        | 9.30% | 10.00% | 3 | **+0.233** |
| **UK 2022-2025** (calendar-year-matched to IE)     | 9.18% |  8.11% | 3 | **−0.357** |
| **IE 2022-2025**                                   | 7.00% |  6.22% | 3 | **−0.260** (95% CI [−0.60, +0.14]) |

The original draft's "Ireland is narrowing at nearly 2× the UK rate" headline compared IE's 3-year rate to the UK's 8-year average. Both legitimate window-matched comparators undermine that claim:

- **UK 2017-2020** (same regime age as IE 2022-2025): UK *widened* during its first three years, dominated by the 2019 data gap and the 2020-2021 COVID distortion. This is not a useful baseline for Ireland's 2022-2025 performance — both regimes have run against very different macroeconomic backdrops.
- **UK 2022-2025** (same calendar years as IE): the UK narrowed *faster* than Ireland over the same 2022-2025 window (−0.357 vs −0.260 pp/yr). The Irish rate is within the UK's uncertainty band and vice-versa.

There is no defensible "Ireland beats the UK" claim in the available data. The honest statement is: both regimes are delivering within-firm narrowing on the order of a quarter to a third of a percentage point per year, with wide uncertainty over short windows, and there is no evidence that one is structurally outperforming the other.

## 5. Discussion

### 5.1 What the data shows

1. **Within persistent Irish firms, gaps are narrowing.** 623 firms reporting in both 2022 and 2025, median change −0.87 pp, 56.5% narrowing. The population-level −0.78 pp shift is essentially all attributable to this within-firm channel, not to the entry of new (smaller) firms under the phased-down threshold.
2. **Population-level rate is not yet distinguishable from zero.** 95% CI on the annualised rate is [−0.60, +0.14] pp/yr. One or two bad years could wipe out the apparent trend. This is a finding, not a failure — three years is short.
3. **Sector dispersion is very large and robust.** Construction, Finance, Manufacturing, Professional/Scientific/Technical, and Energy are persistently high-gap (all with n≥20). Public Administration, Human Health, Accommodation/Food, and Wholesale/Retail are persistently low-gap. This is the most policy-relevant finding.
4. **Cross-country comparison to the UK is inconclusive.** No matched window supports a "faster Irish narrowing" claim.

### 5.2 What it does not show

- **Not causal.** No pre-regime Irish counterfactual; no synthetic control. We cannot attribute the within-firm narrowing to the regime as opposed to the underlying secular trend.
- **Not statistically significant at the population level** over the three-year window.
- **Not complete coverage.** Only mandatorily-reporting employers (250+ in 2022, 150+ from 2024, 50+ by 2026). See §Caveats on coverage audit.
- **Not intersectional.** Gender binary only; no ethnicity or disability breakdown in the regulations.

## 6. Caveats and deferred work

1. **paygap.ie coverage vs CSO/IBEC universe (reviewer-mandated experiment R5)** was deferred. The CSO Business Demography (BIS-02) size-class table and IBEC member list for 2024/2025 are the correct universe denominators for a coverage audit; neither was reachable in the Phase 2.75 cycle without live network access. Until this is done, selection-bias from non-reporters (plausibly higher-gap) cannot be ruled out. Flagged for Phase B.
2. **Small-n sectors** (Real Estate n=7, Mining n=3, Water/Waste n=5) have wide 95% CI and are reported for completeness but are not load-bearing for the headline.
3. **Within-firm panel is composition-selected**: the 623 persistent firms are large (≥250 in 2022) and survived to 2025. Narrowing among this cohort is an upper bound on reform in the 2024-entry cohort, for which we do not yet have three years of longitudinal data.
4. **Threshold-invariant cohort** uses "first reported in 2022" as a proxy for ≥250 employees. paygap.ie does not publish headcount explicitly. A firm that grew past 250 between 2022 and 2023 would be misclassified; the opposite case (firms that fell below 250 but continued voluntary reporting) is also possible. These misclassifications are thought to be small.

## 7. Conclusions

Three years of Irish mandatory gender pay gap disclosure are associated with a ~0.8-point population-level median narrowing — essentially all of which is accounted for by within-firm reform among the 623 firms persistently in the reporting pool, *not* by composition changes as the threshold phased down. The annualised population rate of −0.26 pp/yr has a 95% CI spanning [−0.60, +0.14], so no statistical-significance claim about population-level narrowing is warranted at this window length. The reviewer-mandated comparison to the UK over matched windows produces no evidence that Ireland is narrowing faster than the UK: on 2022-2025 calendar-matched data the UK is narrowing slightly faster (−0.36 vs −0.26 pp/yr).

The policy-relevant and durable findings are (a) within-firm change of −0.87 pp median with 56.5% of persistent firms narrowing, suggesting the regime is reaching inside reporting organisations; and (b) sector dispersion of ~28 points between Real Estate / Construction / Finance / Energy at one end and Public Administration / Health / Accommodation-Food at the other, with the high-gap sectors being the appropriate targets for sector-specific action-plan scrutiny.

The natural Phase-B extension is a synthetic-control difference-in-differences with Ireland as the 2022 treated unit and a non-mandatory-reporting Eurozone donor pool, to identify the regime's own effect net of the European 2022-2025 labour-market backdrop. A paygap.ie coverage audit against the CSO BIS-02 universe is a prerequisite for that work.

## 8. Change log (Phase 2.75 reviewer cycle)

The Phase 2.75 blind reviewer demanded six experiments (R1-R6). Five were executed; one was deferred for data-access reasons. The results of the executed five overturned the original "Ireland narrows nearly 2× the UK rate" headline, and the paper has been rewritten accordingly. Original paper (pre-revision) asserted a faster-than-UK narrowing as a headline finding; the revised paper retracts that claim and foregrounds the within-firm panel plus the inconclusive cross-country comparison.

| Review item | Status | Outcome |
|---|---|---|
| R1 threshold-invariant subsample      | Done | −0.267 pp/yr — essentially identical to full sample; composition is not the story |
| R2 bootstrap CI on annualised rates   | Done | IE 95% CI [−0.60, +0.14], not distinguishable from zero |
| R3 UK window-matched comparator       | Done | UK 2022-2025 narrows faster than IE (−0.36 vs −0.26 pp/yr); "nearly 2×" headline retracted |
| R4 within/entry/exit decomposition    | Done | Within-firm = −0.90 pp, entry = +0.02, exit = +0.10 — within-firm is the entire story |
| R5 paygap.ie coverage audit           | Deferred | CSO BIS-02 / IBEC universe not reachable in cycle; flagged in §Caveats |
| R6 sector CI table                    | Done | Real Estate, Mining, Water/Waste flagged small-n (n<10); headline table updated |
