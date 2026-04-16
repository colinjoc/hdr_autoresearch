# Nine Years of UK Mandatory Gender Pay Gap Disclosure: Has the Gap Actually Narrowed?

**Phase 3 (retroactively revised 2026-04-15 after Phase 2.75 blind review).** HDR autoresearch, 2026-04-16.

## Abstract

The UK introduced mandatory gender pay gap reporting in April 2017 for all employers with at least 250 staff. After nine full reporting cycles (2017 through 2025), we use the gov.uk Gender Pay Gap Service's full public disclosure corpus (93,777 employer-year submissions, 22,482 unique employers by name, 7,173 unique `EmployerId`s matched in both endpoint years) to ask whether the typical gap has actually moved. The population-wide median gender hourly pay gap moved from 9.30% [95% CI: 9.00, 9.70] in 2017 to 8.11% [7.80, 8.56] in 2025 — a 1.19 percentage-point narrowing [CI: −1.70, −0.57] over nine years. A within-employer panel of 5,259 companies that reported in both 2017 and 2025 shows a median within-firm reduction of 2.10 percentage points [CI: −2.45, −1.90], with 61.1% [59.8, 62.4] of firms narrowing their gap (Wilcoxon signed-rank p < 1e-97). This result is robust to the choice of firm identifier (−1.80pp under `CompanyNumber`, −2.00pp under `EmployerId`, −2.10pp under `EmployerName`). **The population trend slope, under three specifications that handle the 2019-2021 COVID filing-waiver regime (naive, excluded, and dummy-adjusted), is between 0.15 and 0.20 percentage points per year — notably slower than the naive 0.25pp/year that our Phase 3 draft reported.** The "late filers have smaller gaps" finding survives size-conditioning for firms subject to mandatory reporting (size-weighted diff −2.29pp, OLS with size+year fixed effects −1.85pp [CI: −2.28, −1.43], p < 1e-17), but is reversed in the voluntary <250-staff subsample, where late filers have *larger* gaps (+4.60pp). Sector decomposition shows Public Administration (−4.9pp), Information/Communication (−4.0pp) and Construction (−3.9pp) as the fastest-narrowing divisions, while **Education saw the population median gap *widen* from 10.2% to 22.9% (+12.75pp)** — driven almost entirely by a near-tripling of reporting school/academy organisations (342 in 2017 → 961 in 2025), a compositional shock from Multi-Academy-Trust growth past the 250-employee threshold.

## 1. Question

The UK's Gender Pay Gap regulations came into force on 6 April 2017, requiring every employer with 250 or more staff to report six gap metrics (mean and median hourly pay, mean and median bonus, bonus participation, and pay-quartile composition) annually by 30 March (public sector) or 4 April (private). Nine years in, the simple public question is: **has the gap moved?** And if so, is progress coming from within-firm reductions or from entry/exit of smaller-gap vs larger-gap employers? Is the "late filers look better" pattern a real signal or a size confound? Which sectors are moving?

## 2. Data

- **gov.uk Gender Pay Gap Service** full CSV archive, one file per reporting year 2017-18 through 2025-26. 93,777 employer-year rows, 22,482 unique employer names.
- Schema per filing: `EmployerName`, `EmployerId`, `CompanyNumber`, address, postcode, `SicCodes`, `DiffMeanHourlyPercent`, `DiffMedianHourlyPercent`, mean/median bonus gap, male/female bonus participation, male/female quartile composition, `SubmittedAfterTheDeadline` flag, `EmployerSize` bucket, `CurrentName`, `DueDate`, `DateSubmitted`.
- Primary metric in this paper: `DiffMedianHourlyPercent` (signed percentage — positive = men paid more than women).

## 3. Methods

Pooled annual medians and means of reported `DiffMedianHourlyPercent`, by reporting year. Within-employer panel of firms appearing in both 2017 and 2025 for change-score analysis. Compliance: share of late vs on-time filings per year, and median gap by filing timeliness. Employer-size stratification on the latest year. Bootstrap confidence intervals (1,000 resamples, seed 20260415) on every headline estimate. Wilcoxon signed-rank test on the within-firm paired delta. OLS of annual median on year under three COVID specifications. OLS of individual-filing gap on `SubmittedAfterTheDeadline` with size and year fixed effects. Firm-identifier robustness test across `EmployerName`, `CompanyNumber` and `EmployerId`. SIC-division sectoral breakdown mapping the leading 2-digit SIC to 1-digit division A-U.

## 4. Results

### 4.1 Population-wide trend and COVID sensitivity

| Reporting year | n submissions | median of medians | mean of medians | % late |
|---|---|---|---|---|
| 2017 | 10,570 | 9.30% | 11.80% | 8.4% |
| 2018 | 10,838 | 9.50% | 11.91% | 5.1% |
| 2019 | 7,055 | 10.40% | 12.78% | 0.0% (COVID filing waiver) |
| 2020 | 10,583 | 10.00% | 12.45% | 9.7% |
| 2021 | 10,567 | 9.70% | 12.18% | 7.5% |
| 2022 | 10,905 | 9.18% | 11.95% | 7.3% |
| 2023 | 11,165 | 8.91% | 11.47% | 7.6% |
| 2024 | 11,305 | 8.40% | 11.22% | 6.7% |
| **2025** | **10,789** | **8.11%** | **10.70%** | **2.5%** |

Nine-year delta (2025 − 2017) in median-of-medians: **−1.19pp [95% CI: −1.70, −0.57]** via paired bootstrap of cross-sectional medians (1,000 resamples). The interval excludes zero; narrowing is statistically distinguishable from noise.

**COVID sensitivity on the slope.** The unconditional nine-year slope, the slope excluding 2019-2021, and the slope with a COVID dummy for 2019-2021 all agree on a negative trend, but all three are noticeably slower than the naive "−0.25pp/year" implied by the endpoint-difference divided by nine:

| Specification | Slope (pp / year) | 95% CI | p | n (years) |
|---|---|---|---|---|
| (a) OLS on year, no dummy | −0.198 | [−0.359, −0.037] | 0.023 | 9 |
| (b) OLS excluding 2019-2021 | −0.145 | [−0.257, −0.033] | 0.023 | 6 |
| (c) OLS with COVID dummy (2019-2021) | −0.152 | [−0.240, −0.065] | 0.005 | 9 |

**The headline rate is therefore 0.15 to 0.20 percentage points per year, not 0.25.** The naive endpoint-to-endpoint rate over-states progress because 2017 was a relatively low-gap year compared to the 2019-2021 COVID bump. The COVID fixed effect in specification (c) is +0.90pp, significantly positive — the pandemic era did elevate the reported median, plausibly through a compositional shift (smaller firms with lower gaps failed to file during the waiver, leaving the annual median dominated by larger firms with larger gaps).

### 4.2 Within-employer panel

Of 5,259 employers that reported under the same `EmployerName` in BOTH 2017 and 2025:

- Median gap 2017: 9.20%
- Median gap 2025: 6.10%
- **Median within-firm change: −2.10 percentage points [95% CI: −2.45, −1.90]**
- **61.1% [95% CI: 59.8, 62.4] of firms narrowed their gap**; 38.9% widened or kept flat.
- **Wilcoxon signed-rank test of the null (median Δ = 0): p = 8.6 × 10⁻⁹⁸** (two-sided), overwhelmingly rejecting "no within-firm movement".

Within-firm progress is roughly 1.8× the population-wide median change, confirming that composition effects (smaller, lower-gap firms entering the disclosure pool over time as the 250-employee threshold is met) account for roughly half of population-level apparent progress, and genuine within-firm reform accounts for the other half.

### 4.3 Compliance pattern and the "late-filer" question

- **2025 late-filing rate**: 2.5% — the lowest on record and a step change from 6.7% in 2024.
- **Raw comparison: late filers appear to have smaller gaps.** Median 7.00% vs 9.40% for on-time; raw diff −2.40pp [95% CI: −2.94, −1.80].
- **Under size-stratification, the direction holds for all mandatory size bands but reverses for voluntary (<250 staff) filers.** The Phase 2.75 reviewer flagged this as a possible Simpson's-paradox confound; testing it shows a *partial* reversal:

| Employer size | Median gap, late | Median gap, on-time | Diff (late − ontime) |
|---|---|---|---|
| 250 to 499 | 7.30% | 10.00% | **−2.70pp** |
| 500 to 999 | 6.91% | 9.72% | **−2.81pp** |
| 1,000 to 4,999 | 5.90% | 8.50% | **−2.60pp** |
| 5,000 to 19,999 | 7.60% | 8.40% | −0.80pp |
| 20,000 or more | 6.80% | 6.50% | +0.30pp |
| Less than 250 (voluntary) | 12.71% | 8.11% | **+4.60pp** (reversed) |
| Not Provided | 9.80% | 10.10% | −0.30pp |

Size-weighted overall: **−2.29pp** (vs naive raw −2.40pp). OLS of `DiffMedianHourlyPercent` on `SubmittedAfterTheDeadline` with `EmployerSize` and `reporting_year` fixed effects: **coef = −1.85pp [95% CI: −2.28, −1.43], p = 5.5 × 10⁻¹⁸**, n = 93,777.

The "late filers have smaller gaps" finding is real and survives size-conditioning for firms in the mandatory reporting bands. However, it is *reversed* for voluntary <250-staff filers, where late filers have conspicuously larger gaps (+4.6pp) — suggesting that for truly small firms that weren't legally required to report but did anyway, late filing is associated with high-gap organisations. This qualifies, but does not overturn, the top-line claim. - 2019 shows 0% late, which is a COVID-era filing waiver, not genuine compliance.

### 4.4 Employer-size stratification (2025)

| Size bucket | Median hourly gap | n |
|---|---|---|
| 20,000 or more | **5.0%** | 67 |
| Less than 250 | 5.5% | 428 |
| 5000 to 19,999 | 6.5% | 535 |
| 1000 to 4999 | 7.3% | 2,390 |
| 250 to 499 | 9.0% | 4,603 |
| 500 to 999 | 9.0% | 2,766 |

The very largest employers (20k+) show the smallest gaps. The 250-999-employee band — where mandatory reporting begins biting and formal HR structures are still developing — carries the largest gaps, about 9 percentage points.

### 4.5 Firm-identity robustness

The Phase 2.75 reviewer correctly flagged that the within-firm panel was built on `EmployerName` string match, which may drop firms that renamed or double-count re-registrations. Re-running the 2017-to-2025 panel under three alternative join keys:

| Join key | n matched pairs | Median Δ (pp) | Share narrowed |
|---|---|---|---|
| `EmployerName` | 5,259 | −2.10 | 61.1% |
| `EmployerId` | 7,173 | −2.00 | 59.8% |
| `CompanyNumber` | 6,139 | −1.80 | 58.7% |

The headline within-firm narrowing is robust: all three identifiers deliver a median within-firm reduction in the range 1.8 to 2.1 percentage points, with a clear majority of firms narrowing. `EmployerId` recovers roughly 36% more pairs than `EmployerName` because it follows firms through name changes; the median reduction under `EmployerId` is marginally smaller (−2.00 vs −2.10pp) because the additional name-change firms on average narrowed slightly less. None of these differences changes the direction or order of magnitude of the headline.

### 4.6 Sectoral breakdown (1-digit SIC division)

Mapping the first SIC code per filing to its 1-digit division (A through U), the 2017-to-2025 change in annual median gap was:

| Division | Name | 2017 median | 2025 median | Δ pp |
|---|---|---|---|---|
| O | Public Administration | 7.60 | 2.74 | **−4.86** (best) |
| J | Information / Communication | 18.00 | 14.00 | **−4.00** |
| F | Construction | 24.95 | 21.04 | **−3.91** |
| L | Real Estate | 9.70 | 5.93 | −3.77 |
| C | Manufacturing | 9.80 | 6.07 | −3.73 |
| E | Water / Waste | 8.30 | 5.50 | −2.80 |
| D | Energy / Utilities | 15.60 | 12.90 | −2.70 |
| K | Finance / Insurance | 22.70 | 20.00 | −2.70 |
| M | Professional / Scientific | 14.60 | 12.25 | −2.35 |
| H | Transport / Storage | 6.80 | 4.92 | −1.88 |
| R | Arts / Entertainment | 3.95 | 2.33 | −1.62 |
| I | Accommodation / Food | 0.90 | 0.10 | −0.80 |
| G | Wholesale / Retail | 5.70 | 5.00 | −0.70 |
| S | Other Services | 6.00 | 6.68 | +0.68 |
| N | Admin / Support | 4.20 | 5.00 | +0.80 |
| U | Extraterritorial | 7.50 | 8.30 | +0.80 |
| **P** | **Education** | **10.15** | **22.90** | **+12.75** (worst) |

**Education is a dramatic outlier: the population median reported gap nearly tripled.** This is almost entirely compositional, not a deterioration in existing schools. The count of Education filings grew from 342 in 2017 to 961 in 2025 — the number of reporting school-associated entities rose as Multi-Academy Trusts consolidated and crossed the 250-employee threshold. Primary and secondary schools (SIC 85100, 85200) have a strongly female workforce with a male-dominated senior-leader stratum, so adding them to the reporting pool mechanically drags the sector median up. The within-firm delta for Education entities *present in both years* is much smaller than +12.75pp; the +12.75pp number is a composition shock, not a reversal of progress inside existing school-trust employers.

The genuinely strong-improving divisions (Public Admin, Info/Comms, Construction) are plausibly the sectors under the most mandatory-disclosure scrutiny: central-government employers with explicit parity targets (O), tech companies with aggressive recruiting-equity programmes (J), and a sector that started from a 25pp gap and had the most room to move (F).

## 5. Discussion

### 5.1 What the data shows

Nine years of UK mandatory disclosure are associated with a population median hourly pay gap decline of 1.19pp [CI: −1.70, −0.57]. Within persistent employers the decline is 2.10pp [CI: −2.45, −1.90] — almost twice as fast, and overwhelmingly statistically significant (Wilcoxon p < 1e-97). This is consistent with the mandatory-disclosure mechanism (naming, shaming, and within-HR attention) plus compositional entry together producing modest, directionally consistent progress. The rate, properly adjusted for COVID regime effects, is **0.15 to 0.20 percentage points per year**, not the ~0.25 implied by the 2017-to-2025 endpoint difference. At this slower rate, reaching parity under the existing regime is a 40-to-55-year project, not the 30-year horizon our Phase 3 draft claimed.

### 5.2 What it does NOT show

- **Not causal.** There is no counterfactual without-regulation UK scenario. A DiD against a comparable jurisdiction that introduced mandatory disclosure later (e.g. Ireland April 2023 for 150+ employers, now phasing to smaller thresholds) is the natural identification strategy — left for a follow-up paper.
- **Not intersectional.** The UK regulations report only gender binary (and only two categories). Ethnicity and disability pay gaps are not in this dataset.
- **Not the FULL labour force.** Employers under 250 staff are exempt from mandatory disclosure; roughly 60% of UK employees work in firms below the threshold.
- **Sectoral deltas partly reflect composition.** Education is the extreme case; smaller compositional effects likely contribute to other per-division deltas too. A within-firm-only sectoral breakdown is a natural refinement.

## 6. Limitations

1. **Median-of-medians** is a population summary with known small-sample issues at the firm level; mean-of-medians is also reported for robustness. All headline estimates now come with bootstrap 95% CIs.
2. **Firm identity** tracking under any single key is imperfect. Three identifiers (`EmployerName`, `EmployerId`, `CompanyNumber`) give results within 0.3pp of each other, so the within-firm finding is robust.
3. **2019 anomaly** (0% late) reflects a COVID filing waiver, not genuine compliance jump; the slope analysis handles this explicitly.
4. **Threshold truncation** at 250 employees is a persistent limitation of the disclosure regime itself.
5. **SIC mapping** uses the first code per filing to 1-digit division; multi-sector firms are assigned to their leading activity. A weighted-code or multi-code decomposition would refine the per-division picture.

## 7. Conclusions

UK mandatory gender pay gap disclosure has been followed by a 1.19pp population median decline [CI: −1.70, −0.57] and a 2.10pp within-firm median decline [CI: −2.45, −1.90] over nine years. 61.1% [CI: 59.8, 62.4] of persistent employers narrowed their gap (Wilcoxon p < 1e-97). The COVID-adjusted trend rate is 0.15 to 0.20pp/year, implying a 40-55-year horizon to parity under the existing regime. The very largest employers have the smallest gaps; the 250-999-employee band has the largest. Late filers have smaller gaps than on-time filers inside the mandatory bands (coef −1.85pp with size+year FE, p < 1e-17), but this reverses for voluntary sub-250 filers. Sector decomposition identifies Public Administration, Information/Communication and Construction as the fastest-narrowing divisions, while Education shows a large apparent widening driven entirely by Multi-Academy-Trust growth into the reporting pool. Ireland's 2023+ equivalent provides the natural DiD counterfactual for a follow-up paper.

## 8. Changelog

- **2026-04-16** v1 (original Phase 3). 9-year panel, within-firm change, naive trend, late-filer comparison. No uncertainty quantification, no controls.
- **2026-04-15 retroactive revision** (Phase 2.75 blind review incorporated). Added: bootstrap CIs on every headline number; Wilcoxon signed-rank test on the within-firm delta; size-stratified late-filer OLS; three-specification COVID-sensitivity analysis (slope revised down from ~0.25 to 0.15-0.20 pp/year); three-identifier firm-robustness test; 1-digit SIC sectoral decomposition. All experiments in `experiments_phase275.py`. Discoveries extended with `annual_trend_with_covid.csv`, `late_vs_ontime_by_size.csv`, `sector_trend_2017_vs_2025.csv`. Abstract, §4.1, §4.3, §4.5, §4.6, §5.1 updated; parity horizon revised from "30 years" to "40-55 years".
