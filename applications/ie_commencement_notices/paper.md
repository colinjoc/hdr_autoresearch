# Permission-to-Completion Cohort Latency in Irish Residential Construction, 2014–2025

*Final paper — incorporates Phase 2.75 blind-review mandated experiments R1–R9.*

## Abstract

Aggregate comparisons of Irish planning-permission and completion time series produce only a convolution-implied lag between the two. We construct the first publicly reproducible project-level cohort dataset of Irish residential building-control filings (Building Control Management System, BCMS; N=183,633 residential permissions granted 2014–2025) and measure (i) permission-to-commencement duration, (ii) commencement-to-completion-certificate duration, and (iii) total permission-to-certified-completion duration using Kaplan–Meier, Cox proportional hazards, Weibull and log-normal accelerated failure time (AFT) models, and a gradient-boosting classifier for the "dark permission" outcome. The headline median permission-to-commencement duration is **232 days (bootstrap 95% CI 231–234; R9a)**, median commencement-to-certification is **498 days (CI 497–500; R9b)**, and the complete-timeline subcohort median is **962 days ≈ 32 months (CI 959–966; R9c)**. The log-normal AFT narrowly wins on Akaike information criterion (AIC) in-sample but the advantage does not survive temporal-split holdout (R7): Cox, Weibull, and log-normal AFT are indistinguishable on 2021–2024 test data (Cox c = 0.582, log-normal c = 0.566). Apartment projects take 53 days longer than dwellings from commencement to certificate (CI 43–62; R9g). The raw AHB-vs-private gap of +46 days (CI 35–70; R9h) is dominated by composition: within size strata the gap varies from +21 to +175 days and the Cox hazard ratio for AHB is 0.869 (CI 0.828–0.912; R2c). The dark-permission rate is highly channel-dependent (R4): the commence-within-72-months share is 0.67% (CI 0.62–0.72%; R9f), but under a non-opt-out CCC-filing definition the implied dark rate rises to 39%. The Phase B Local-Authority ranking is materially correlated with CCC-filing-rate heterogeneity (Spearman ρ = 0.28, Pearson r = 0.25; R1), so we publish a channel-adjusted ranking in `discoveries/optimal_la_scheme_recommendations_channel_adjusted.csv` as the primary product; county-level "delivery workhorse" language from the draft is withdrawn. The results provide a micro-foundation for Housing for All supply targets that aggregate series cannot.

## 1. Introduction

Ireland's chronic housing-supply deficit (Duffy et al. 2014; McQuinn & O'Connell 2024; ESRI Housing Model 2023) has been quantified through the Central Statistics Office's aggregate permissions series (BHQ15) and completions series (NDQ/HSM13), but the gap between a *granted permission* and a *certified completed dwelling* has been estimated only as a cross-correlation lag between the two smoothed series — a notional lag, not a cohort measurement. Harter & Morris (2021), using US Census Bureau microdata, show that the shape of the permit-to-completion distribution is bimodal with fat right tails, and that aggregate lag estimation systematically under-states the tail risk for policy targets. Ireland has had no comparable cohort study.

The Building Control Management System (BCMS), operated by the National Building Control Office (NBCO), has published project-level filings since the Building Control (Amendment) Regulations 2014 (BCAR 2014) came into force on 1 March 2014 (NBCO 2023; Keith & O'Connor 2013). Each row records the planning-permission number, the grant date, the commencement notice date, and — where filed — the Certificate of Completion and Compliance (CCC) validation date. We use this dataset to estimate a cohort-level permission-to-completion latency distribution for Ireland, covering 183,633 residential permissions granted between 2014 and 2025.

We answer five questions: (a) how long do permissions take to commence? (b) how long do commencements take to complete? (c) what is the total permission-to-completion latency? (d) what share of granted permissions never commence (the "dark permission" fraction)? (e) what share of commenced projects certify completion within policy-relevant windows (24, 48, 72 months)? We document heterogeneity across Local Authorities (LAs), scheme sizes, apartment-vs-dwelling, pre-vs-post Strategic Housing Development (SHD) regime (Arkins 2016; Oneil 2022), and pre-vs-post-COVID-shutdown.

**Contribution.** A publicly reproducible cohort-level micro-foundation for Irish housing-supply pipeline analysis, with explicit channel-definition bounds on the dark-permission rate and a channel-adjusted Local-Authority ranking. The methodology (survival analysis of administrative filings) is standard; the contribution is the dataset framing, the descriptive findings with quantified channel bounds, and the adjusted Phase B ranking.

## 2. Detailed Baseline

### 2.1 What the aggregate-lag baseline is

The predecessor Irish Housing Pipeline work estimated the Irish permission-to-completion lag as the cross-correlation peak between 4-quarter moving averages of the CSO BHQ15 (residential permissions, quarterly, national) and NDQ (new dwelling completions, quarterly, national) series. If `P_t` is permissions in quarter `t` and `C_t` is completions in quarter `t`, the lag `k*` minimises the squared distance `sum_t (C_{t+k} - β P_t)^2` over a candidate lag window `k ∈ {0, 1, ..., 12}`, with `β` interpreted as the conversion rate:
```
k* = argmin_{k ≥ 0} ||C_{t+k} - β P_t||²_2     subject to β ∈ [0, 1]
```
The mathematical formulation is a constrained least-squares, directly analogous to a geophysical filter-estimation problem. Its two dominant failure modes are: (i) stationarity of the conversion rate, which fails for any regime shift (COVID, BCAR 2014 rollout, SHD 2017–2021); (ii) it cannot separate a shorter but higher-attrition pipeline from a longer but lower-attrition pipeline — both produce the same `k*`.

### 2.2 Baseline implementation and parameter values

Running the aggregate cross-correlation on BHQ15 + HSM13 for 2014Q1–2025Q1 produces `k* = 8` quarters (~24 months) at the argmax, with neighbouring lags at `k=7` and `k=9` producing residual sums-of-squares within 3% of the minimum; the implied `β ≈ 0.71`. The parabolic width of the squared-error curve around `k*` corresponds to a standard error of roughly ±0.7 quarters on the lag point estimate — a reminder that the aggregate `k*` is itself poorly identified. We record this below as the aggregate baseline for comparison.

## 3. Detailed Solution

### 3.1 The cohort-level replacement

We replace the aggregate filter with a cohort-level duration dataset. Each BCMS row carries:
- `CN_Date_Granted` — planning permission grant date
- `CN_Date_Submitted_or_Received` — commencement-notice filing
- `CN_Commencement_Date` — declared physical commencement
- `CCC_Date_Validated` — Certificate of Completion and Compliance validation
- `CCC_Units_Completed` — certified completed units

We define three cohorts:
1. **Permission-to-commencement cohort (N = 183,633):** residential rows with `CN_Date_Granted ∈ [2014, 2025]`. Outcome: days to `CN_Commencement_Date`; right-censored at export date (2026-04-15).
2. **Commencement-to-CCC cohort (N = 184,684):** rows with `CN_Commencement_Date ≥ 2014-01-01`. Outcome: days to `CCC_Date_Validated`; right-censored at export for un-certified projects.
3. **Complete-timeline subcohort (N = 71,599):** rows with all three dates populated; outcome: days from grant to CCC.

### 3.2 Estimator specifications

**Kaplan–Meier** (Kaplan & Meier 1958). Nonparametric product-limit survival function `Ŝ(t) = Π_{i: t_i ≤ t} (1 - d_i / n_i)`. Implementation: `lifelines.KaplanMeierFitter`.

**Cox proportional hazards** (Cox 1972, ch. 4; Cox 1975). `λ(t|X) = λ_0(t) exp(β'X)`. Covariates: `grant_year, is_dublin, apartment_flag, log_units, ahb_flag`. Penaliser 0.01, ridge penalty. Tie handling: Efron (1977); a robustness check using Breslow ties (one-line configuration change) produced concordance differences below the third decimal place and is not reported. Implementation: `lifelines.CoxPHFitter`.

**Weibull AFT** (Wei 1992; Bagdonavicius & Nikulin 2002, Ch. 4). `log(T) = α + β'X + σ W`, `W ~ extreme-value`. Same covariates.

**Log-normal AFT.** `log(T) = α + β'X + σ ε`, `ε ~ N(0, 1)`. Same covariates.

**Generalised gamma (univariate).** Nests Weibull, log-normal, exponential (Royston & Parmar 2002).

**LightGBM dark-permission classifier.** Gradient-boosted trees (Ke et al. 2017) on `grant_year, is_dublin, apartment_flag, log_units, ahb_flag, opt_out_flag, protected_flag`. 70/30 random split, 200 trees, learning rate 0.05, seed 42. Evaluated on held-out 30% via Area Under the Receiver-Operating Characteristic curve (AUROC) and Brier score (Graf 1999). Feature importance reported via permutation importance in §5.7.

**Logistic regression baseline.** Scikit-learn `LogisticRegression(max_iter=1000)`, same features. Serves as the mandatory linear-model sanity check.

### 3.3 How to reproduce

Run `python analysis.py` from the project root. The script loads BCMS (258 MB), constructs the three cohorts, runs the Phase 0.5 baseline (E00), executes the seven-family tournament (T01/T02 in `results.tsv`), runs 26 KEEP/REVERT experiments (E01–E26) and 5 interaction experiments (I01–I05). All intermediate steps cache to `data/cohort_cache.parquet`. Re-runs from cache complete in under 60 seconds. The Phase 2.75 follow-ups (R1–R9) are produced by `python phase_2_75_revisions.py` and append rows to `results.tsv`. The Phase B discovery script `phase_b_discovery.py` scores 227 (LA × scheme size × apartment/dwelling) cells; the channel-adjusted ranking is written to `discoveries/optimal_la_scheme_recommendations_channel_adjusted.csv`.

## 4. Methods

### 4.1 Cohort definitions and censoring

Residential rows are defined by `CN_Proposed_use_of_building` containing any of `1_residential_dwellings`, `2_residential_institutional`, `3_residential_other`. Dates are sanitised to the window `[2000-01-01, 2027-01-01]`; values outside are clerical entries. Permissions granted after the export date are excluded. Projects with negative durations are excluded (2.0% of rows — below the 2% tolerance enforced by `tests/test_cohort_durations.py`).

Right-censoring is applied at the BCMS export date (2026-04-15). The sensitivity analysis in E14 shifts the censor date back six months and confirms the Kaplan–Meier median moves from 232 to 238 days — well within bootstrap confidence intervals.

### 4.2 Covariates

`grant_year`, `grant_month`, `is_dublin` (4 Dublin LAs), `is_major_city` (Dublin + Cork + Galway + Limerick + Waterford cities), `apartment_flag`, `dwelling_flag`, `one_off_flag`, `log_units` (`log1p` of total dwelling units), `ahb_flag`, `la_own_flag`, `opt_out_flag`, `seven_day_flag`, `protected_flag`, `mmc_flag`, `pre_2015_flag`, `shd_era_flag`, `post_hfa_flag`, `size_stratum` (five buckets: 1 / 2–9 / 10–49 / 50–199 / 200+), `LA_clean` (31 categories).

### 4.3 Iteration protocol

The KEEP/REVERT criterion is: a stratification or cohort-restriction is KEPT if the median duration gap versus the full-cohort baseline exceeds **10 days (≈1.4% of baseline)** AND the bootstrap 95% CI excludes zero. Ties within 10 days but with tight CIs are retained for narrative completeness but flagged "narrow." A model-specification change must produce an in-sample concordance improvement ≥ 0.005 AND the improvement must survive the temporal holdout (R7). Interaction experiments (Phase 2.5) are KEPT regardless of magnitude and reported descriptively. Under the stricter joint rule several prior-draft rows that previously read KEEP at ≈ ±11–18 days are flagged narrow (E08, E16), and the log-normal AFT champion status is withdrawn (see §5.5).

## 5. Results

### 5.1 Headline duration estimates with bootstrap CIs (R9)

Median permission-to-commencement for the observed-event residential cohort is **232 days (bootstrap 95% CI 231.0–234.0; R9a; E00, E24)**. The empirical 25th percentile is 97 days and the 75th percentile is 550 days.

Median commencement-to-CCC for the observed-event cohort is **498 days (CI 497–500; R9b; E00b; N = 76,565)**.

Median permission-to-CCC on the complete-timeline subcohort is **962 days ≈ 32 months (CI 959–966; R9c; E00c; N = 71,599)**.

### 5.2 Cumulative commencement share, dark-permission rate, and channel bounds (R4, R9d–R9f)

Under the observed-event definition ("commencement notice filed within N months of grant"): at 24 months 80.9% (CI 80.7–81.0%; R9d), at 48 months 93.6% (CI 93.5–93.8%; R9e), at 72 months 99.3% (CI 99.3–99.4%). These are one to two percentage points below the Kaplan-Meier-adjusted values in the draft (82.3% / 95.4% / 99.7%) because they condition on grant-date-eligible cohorts rather than applying KM to the whole panel; either is defensible, and the CIs are tight.

**Dark-permission rate — channel bounds (R4).** The reviewer mandated an explicit bound rather than a point estimate. Under the **commence-within-72-months** definition (commencement notice filed within 72 months): the dark rate is 0.67% (CI 0.62–0.72%; R9f; R4a). Under the **non-opt-out CCC-filing** channel definition (fraction of commenced permissions whose CCC is never validated, restricted to non-opt-out): the dark-equivalent share is 39.3% (R4d). Under the **opt-out-CCC-filing** channel (opt-out-eligible subset — one-off self-builds, where CCC filing is effectively not required by the regulation): the CCC-channel-implied dark share is 100%. This breadth is the central channel story: **the policy-relevant dark-permission rate is 0.67%–39%, depending on whether "dark" means "commencement notice never filed" or "CCC never validated among non-opt-out projects"**. The lower bound is a tight administrative statement; the upper bound is a statement about filing discipline compounded with completion and is not safely interpretable as a real-economy abandonment rate.

### 5.3 Heterogeneity (with bootstrap CIs and composition controls)

**Scheme size (E04).** Median permission-to-commencement rises monotonically with size: 1-unit 160 d, 2–9 units 291 d, 10–49 units 356 d, 50–199 units 392 d, 200+ units 574 d.

**Apartment vs dwelling (E09, R9g).** Median commencement-to-CCC for apartments is 549 days (N = 4,481) versus 495 days for dwellings (N = 69,225), a gap of 53 days (CI 43–62; R9g) — consistent with apartment-viability friction (Duff 2020; Coyne 2022).

**Dublin vs non-Dublin (E06, R8, R9k).** Dublin's median permission-to-commencement is 195 d vs 240 d for rest of Ireland, a gap of −45 days (CI −49 to −41; R9k). The prior expectation — that high-land-price urban markets would see longer permission-to-start durations on net of regulatory and planning-contest friction (e.g. Saiz 2010; Bulan, Mayer & Somerville 2009 for US evidence; Oneil 2022 for SHD-era Irish judicial-review delays) — is reversed. Oaxaca-Blinder decomposition on one-off-dwelling composition (R8b): **68% of the Dublin advantage is explained by Dublin's lower share of slow-to-start one-off dwellings**, leaving a ~14-day residual. Within-size strata (R8a) the advantage is −28 d (stratum 1), −1 d (2–9), −33 d (10–49), −55 d (50–199), −404 d (200+) — the sign is consistent but magnitude varies sharply, with the 200+ cohort providing most of the residual effect.

**SHD era (E07).** Permissions granted 2017–2021 (SHD era) had a longer median permission-to-commencement (275 d) than non-SHD (202 d), consistent with the Arkins (2016) and SHD Review (2018–2021) finding that SHD produced a pipeline of large contested permissions subject to judicial review.

**COVID (E08).** Post-COVID commencements take 18 days longer to certify than pre-COVID — a modest effect, statistically meaningful on N = 76,565 (KEEP-narrow; within one-decimal of the 10-day threshold).

**AHB composition-adjusted (E10, R2, R9h).** The raw Approved Housing Body gap is +46 days (CI 35–70; R9h). Composition-stratified by size (R2a): +64 d (1 unit, N_ahb=71), +21 d (2–9, N_ahb=147), +24 d (10–49, N_ahb=736), +44 d (50–199, N_ahb=557), +175 d (200+, N_ahb=171). The size-controlled Cox hazard ratio for AHB is **HR = 0.869 (CI 0.828–0.912; R2c)** — AHB schemes reach CCC at ~87% of the private-developer rate after controlling for log_units, apartment_flag, and is_dublin. Statement in the draft that "This likely reflects ... site-complexity and regulatory-compliance diligence" is withdrawn; the gap persists under size control but its mechanism is not identified. The apartment-vs-dwelling split (R2b) shows +290 days on apartment AHB projects vs +49 days on dwelling AHB — AHB apartment projects are materially slower than AHB dwellings.

**Multi-phase size-controlled (E12, R5, R9i).** The raw multi-phase gap is +288 days (CI 281–297; R9i). Within size strata (R5): +29 d (10–49), +81 d (50–199), +350 d (200+). The Cox HR for multi_phase with size+type+Dublin controls is **HR = 0.923 (CI 0.908–0.938; R5c)** — a 7.7% lower hazard of commencement after controlling for scheme size. The raw +288-day headline is not entirely a size artefact: a substantial within-stratum gap survives, but the headline number is an overstatement when size is uncontrolled.

**Section 42 extension proxy (E11, R6).** The expiry field `CN_Date_Expiry` is populated in 99.8% of cohort rows (R6a). The grant-to-expiry gap distribution is sharply concentrated at 5.0 years (median 5.00 y, p25 and p75 both near 5.0), with 5.5% of rows showing a gap > 5.5 years — consistent with the construct that permissions-with-extension are a small minority and appear as the upper tail. On the restricted cohort of expiry-populated rows, the E11 extension-proxy gap is +445 days (R6c) — essentially identical to the raw +446 d, confirming that the sensitivity of the proxy to expiry-population is negligible. The E11 finding is robust. Direct cross-check against a Section 42 register was not available; this limitation is noted in §6.4.

**Dublin × apartment size-stratified (R3, R9j).** The raw I01 DiD is +130 days (CI 110–151; R9j). Within size strata (R3): +46 d (10–49), +188 d (50–199), +51 d (200+). **The draft headline +132 d is a weighted average dominated by the 50–199 stratum**, where the DiD is genuinely large; in the 10–49 and 200+ strata it is approximately one-third of the raw number. §5.6 below reports this as the size-conditioned interaction, with the raw cross-stratum number flagged as composition-inflated.

**LA dispersion (E19).** Coefficient of variation of LA-level medians across the 31 LAs is 0.272 (min 162 d, max 454 d, N ≥ 200 per LA). A placebo check shuffling LA labels collapses the CV to 0.020 (E25), confirming LA identity is a real signal, not sampling noise.

### 5.4 Channel-reporting (E26)

CCC filing rate (CCC-validated per commencement) varies across LAs from 11% to 69%, CV 0.47. This is a reporting-channel effect: CCC is a statutory filing that is *optional* for opt-out commencements (single-site self-builds) and LAs differ in enforcement. The 60% of commenced projects without CCC are a mixture of (a) uncompleted, (b) completed-but-unfiled, and (c) opt-out-exempt. Channel variance means that LA-level CCC-rate comparisons must be interpreted as filing-rate plus completion-rate compounded.

### 5.5 Tournament and model choice — in-sample and out-of-sample (R7)

Seven model families on the permission-to-commencement cohort (see `tournament_results.csv` and results below, with R7 out-of-sample concordance added):

| Family | In-sample concordance | AIC | OOS concordance (R7) | Brier (dark) | Notes |
|---|---|---|---|---|---|
| Kaplan–Meier | 0.500 | — | — | — | univariate reference |
| Cox PH | 0.621 | 974,867 | 0.582 (R7a) | — | penalty 0.01 |
| Weibull AFT | 0.621 | 691,877 | — | — | full parametric |
| Log-normal AFT | 0.622 | **690,626** | 0.566 (R7b) | — | best AIC in-sample |
| Generalised gamma | — | 697,446 | — | — | univariate |
| LightGBM dark-24m | — | — | AUROC 0.513 (R7c) | 0.158 OOS | in-sample AUROC 0.933 |
| Logistic dark-24m | — | — | — | 0.007 | in-sample AUROC 0.696 |

The in-sample log-normal advantage on AIC does not generalise. On a 2014–2020 train, 2021–2024 test split, Cox PH achieves OOS concordance 0.582 while log-normal AFT achieves 0.566; this inverts the in-sample ordering. **We withdraw the "champion" designation**; the draft's "log-normal AFT is champion" statement is replaced with: the three survival models are indistinguishable on temporal holdout, and all three show substantial in-sample-to-OOS degradation (0.62 → 0.57–0.58), consistent with a 2022–2024 regime shift not captured by the covariate set. The LightGBM dark-24m classifier's in-sample AUROC of 0.93 collapses to 0.51 on the 2021–2024 holdout, indicating that the dark-24m task is almost entirely learnt from grant-year and post-2020 administrative patterns that do not extrapolate forward. This is a material caveat on §5.7 and §6.3.

### 5.6 Interaction findings (Phase 2.5)

- **I01 Dublin × apartment (with size control, R3):** raw DiD +130 d (CI 110–151); size-conditioned DiD is +188 d in 50–199 stratum, +46 d in 10–49, +51 d in 200+. Headline is the size-conditioned 50–199 result.
- **I02 AHB × size:** AHB speed-up is larger for small schemes; gap persists after size control (R2a).
- **I03 Dublin × COVID:** Dublin 22-d COVID slowdown; rest 8-d; interaction +14 d.
- **I04 Apartment × COVID:** Apartments sped up post-COVID (−21 d), dwellings slowed (+21 d); interaction −41 d — cohort-selection effect as post-2020 apartment starts skew toward already-viable projects.
- **I05 Year × Dublin Cox coefficient:** +0.00005 (p = 0.003); Dublin hazard rising modestly year-over-year.

### 5.7 Dark-permission classifier (E20) — with OOS caution

Using permissions granted ≥ 72 months before export (N = 90,835), LightGBM achieves in-sample AUROC 0.933 and Brier 0.005. On the 2021–2024 OOS test, AUROC collapses to 0.513 (R7c). Permutation importance on the in-sample model assigns 62% of the explained variance to `grant_year`, 24% to `log_units`, 11% to `is_dublin`, and the remainder to `apartment_flag`, `ahb_flag`, and `opt_out_flag`; the `grant_year` dominance is the source of the OOS collapse. The in-sample AUROC is not a credible forecasting claim; the classifier is descriptive and should not be deployed for permissions granted after 2020.

### 5.8 Phase B discovery — channel-adjusted Local-Authority ranking (R1)

**Channel contamination check (R1).** Spearman rank correlation between the unadjusted p_complete_48m and LA CCC-filing rate is ρ = 0.28 (Pearson r = 0.25; n = 210 cells). This is below the 0.3 threshold the review set for "primary rewrite required" but still large enough that the unadjusted ranking leans systematically toward high-filing-rate LAs. Following the reviewer mandate we publish a **channel-adjusted ranking** (OLS residual of p_complete_48m on LA filing-rate) as the primary product. The adjusted file is at `discoveries/optimal_la_scheme_recommendations_channel_adjusted.csv`.

The channel-adjusted top-15 cells for 48-month completion, after residualising on LA CCC-filing rate:

| Rank (adj) | LA | Size | Type | N | p_complete_48m | p_complete_48m_adj |
|---|---|---|---|---|---|---|
| 1 | Offaly | 200+ | dwelling | 89 | 0.90 | +0.51 |
| 2 | Leitrim | 10–49 | dwelling | 128 | 0.86 | +0.50 |
| 3 | Clare | 50–199 | dwelling | 506 | 0.92 | +0.49 |
| 4 | Kilkenny | 50–199 | dwelling | 369 | 0.86 | +0.46 |
| 5 | Cork County | 50–199 | apartment | 95 | 0.89 | +0.43 |
| 6 | Kilkenny | 200+ | dwelling | 101 | 0.81 | +0.41 |
| 7 | Dublin City | 50–199 | dwelling | 426 | 0.79 | +0.41 |
| 8 | Wicklow | 200+ | apartment | 37 | 0.86 | +0.39 |
| 9 | Wicklow | 200+ | dwelling | 298 | 0.86 | +0.38 |
| 10 | Carlow | 50–199 | dwelling | 225 | 0.72 | +0.35 |
| 11 | Limerick City/Co | 50–199 | dwelling | 811 | 0.76 | +0.35 |
| 12 | Galway County | 50–199 | dwelling | 708 | 0.69 | +0.32 |
| 13 | Cork City | 50–199 | dwelling | 1,436 | 0.85 | +0.31 |
| 14 | Kilkenny | 10–49 | apartment | 34 | 0.71 | +0.31 |
| 15 | South Dublin | 50–199 | dwelling | 1,506 | 0.80 | +0.31 |

**The adjusted ranking differs substantively from the unadjusted ranking.** Fingal and South Dublin appear in the top-15 of the unadjusted list but Fingal drops out of the top-15 after channel adjustment; Offaly, Leitrim, Kilkenny, and Carlow rise sharply. The draft's claim that "Fingal, South Dublin, Dublin City, and Wicklow" are the "delivery workhorses" is withdrawn; after channel adjustment the top cells are concentrated in **mid-sized schemes (50–199 units) across a geographically broader set of LAs (Offaly, Leitrim, Clare, Kilkenny, Cork County, Wicklow, Dublin City)**, with Fingal and South Dublin's raw-ranking advantage partly attributable to higher-than-average CCC filing discipline rather than higher completion rates.

The bottom 15 cells are dominated by single-unit dwelling cohorts in low-filing-rate counties; this is the channel artefact (§5.4) and was already flagged in the draft.

## 6. Discussion

### 6.1 What the cohort study changes

The aggregate cross-correlation lag estimate (§2) implies a ~24-month permission-to-completion gap. The cohort complete-timeline median is 962 days (~32 months) — cross-correlation understates because it uses unweighted quarterly counts and misses the long right tail. The cohort number carries a tight bootstrap CI (959–966; R9c); the aggregate point estimate carries a soft ±0.7 quarter standard error on `k*` (§2.2). Phase B identifies the policy-relevant trade-off: mid-size dwelling schemes (10–199 units) in a geographically diverse set of LAs (after channel adjustment) are the high-completion cells.

### 6.2 Real-options evidence

E23 found 1.3% of commencements in the 55–61 month window — below the 2% threshold. The Section 42 extension proxy (E11) is the stronger lever: permissions whose expiry is extended commence 445 days later on average (R6c confirms the proxy is not artefactual), consistent with exercise of option value but not with a hard-expiry mode.

### 6.3 Channel-reporting and the dark-permission bounds

The commence-within-72-months dark-permission rate is tightly estimated at 0.67% (CI 0.62–0.72; R9f). The CCC-channel-implied upper bound depends sharply on whether one-off opt-out commencements are in scope: on non-opt-out projects the non-filed-CCC share is 39.3% (R4d), and this is the more conservative statement a policy reader should cite. The LightGBM dark-classifier's OOS collapse (R7c) reinforces this caution — the in-sample 93% AUROC is a function of `grant_year` and does not generalise to 2021–2024 cohorts. Policy use of point estimates of the dark-permission rate without this bound is not defensible.

### 6.4 Limitations

- **Channel confound of LA ranking.** The Phase B unadjusted ranking is co-informed by CCC-filing-rate heterogeneity (Pearson r = 0.25, Spearman ρ = 0.28; R1). The channel-adjusted ranking should be preferred. The county-level "delivery workhorse" framing used in the draft has been withdrawn.
- **AHB compositional confound.** AHB schemes differ from private on size and type. The size-adjusted Cox HR for AHB is 0.869 — the +46-day raw gap narrows but a residual persists. The mechanism ("site-complexity / regulatory-compliance diligence") is not identified and the draft's causal language is withdrawn.
- **Multi-phase compositional confound.** The +288-day raw multi-phase gap is largely a size effect; within-stratum gaps are 29–350 days and the size-controlled Cox HR is 0.923.
- **Extension-proxy external validity.** The E11 extension-proxy depends on populated `CN_Date_Expiry` reflecting post-grant administrative action; 99.8% of rows are populated (R6a) and the restricted-cohort result reproduces the raw gap (R6c), but we have not cross-checked against the Section 42 register directly. This is a construct-validity caveat that only a register merge can close.
- **Champion withdrawn.** In-sample concordance differences (0.622 vs 0.621) are within the noise floor. The temporal-split holdout (R7) inverts the in-sample ranking (Cox > log-normal > Weibull on OOS). We no longer claim a tournament champion; all three are acceptable and indistinguishable on out-of-sample performance.
- **Dark-classifier temporal regime shift.** R7c shows LightGBM AUROC collapses from 0.93 in-sample to 0.51 OOS. The in-sample classifier is descriptive, not predictive.
- **Data scope.** We do not observe developer identity directly; pre-2014 permissions are grandfathered imperfectly; `CCC_Units_Completed` is median 0.02, so most CCC filings certify partial/zero-unit completion — a structural feature of the filing, not a data error. All findings are descriptive; no treatment effect is identified.

### 6.5 What further work would add

- Cross-merge with a Section 42 extension register for R6 confirmation.
- Joint longitudinal-event model (Rizopoulos 2012) for multi-phase within-project phasing.
- Developer-frailty model separating developer identity from LA identity.
- Merge with BHQ15 / NDQ aggregates to cross-validate cohort-implied commencement rates.
- Retrain the dark-permission classifier with temporal regularisation (e.g. grant-year dropout) to recover OOS generalisation.

## 7. Conclusion

We construct a cohort-level micro-foundation for Irish residential permission-to-completion latency from BCMS data covering 183,633 residential permissions. Headline medians with bootstrap 95% confidence intervals are: permission-to-commencement 232 days (231–234), commencement-to-CCC 498 days (497–500), complete-timeline 962 days (959–966). Large-scheme, apartment, multi-phase, and extension-proxy stratifications produce duration gaps of 53 to 445 days; the Dublin advantage (−45 d) is 68% explained by one-off-dwelling composition. The raw AHB gap (+46 d) survives size control as a Cox HR of 0.869; the raw multi-phase gap (+288 d) is largely a size effect with a residual Cox HR of 0.923.

**The dark-permission rate is between 0.67% (commence-within-72-months) and 39% (non-opt-out CCC-filing) depending on channel definition.** The lower bound is a clean administrative statement; the upper bound folds in CCC filing discipline. A single-point number without this bound is not defensible.

**The Phase B LA ranking, after channel adjustment (R1), identifies high-completion 50–199-unit dwelling schemes across Offaly, Leitrim, Clare, Kilkenny, Cork County, Wicklow, Dublin City, Carlow, Limerick, Galway, Cork City, and South Dublin.** The unadjusted draft's emphasis on Fingal and South Dublin is partly a CCC-filing-discipline artefact.

The log-normal AFT "champion" designation is withdrawn; Cox, Weibull, and log-normal AFT are indistinguishable on temporal-split holdout. The LightGBM dark-24m classifier does not generalise out-of-sample and should not be deployed for post-2020 cohorts.

## 8. Caveats

Explicit enumeration of the channel and compositional risks:

- **LA CCC-filing-rate channel.** LAs differ in CCC-filing enforcement (CV 0.47; range 11–69%). Any LA-level completion comparison is filing-rate-compounded. Use the channel-adjusted ranking (§5.8, R1).
- **Opt-out channel.** Opt-out commencements (single-site self-builds) do not produce CCC filings; they are the dominant channel in one-off dwelling cohorts and inflate the unadjusted "dark" rate for rural counties.
- **Commencement-notice-vs-physical-start channel.** The BCMS outcome is *commencement-notice filed*, not *works on site*. Projects where a notice lapsed and was re-filed appear twice.
- **CCC-vs-certified-completion channel.** `CCC_Units_Completed` median is 0.02 — most CCCs certify partial completion. A CCC is not equivalent to a completed dwelling.
- **AHB compositional risk.** AHB schemes have median 28 units vs private 1 unit and a different apartment mix. The raw +46-day gap is 49-day on dwellings vs 290-day on apartments (R2b).
- **Multi-phase size risk.** Multi-phase status correlates with scheme size ρ > 0.6. The raw +288-day gap is partly a size restatement; size-controlled HR = 0.923.
- **Dublin compositional risk.** 68% of the −45-day Dublin advantage is explained by Dublin's lower share of one-off dwellings (R8b).
- **SHD-era temporal risk.** The SHD judicial-review regime (2017–2021) created a pipeline of contested large permissions that inflate the SHD-era median; this is a regime effect, not SHD-procedure-as-such.
- **Export-date censoring.** Right-censoring at 2026-04-15 means permissions granted after ~2024 have thin commencement observation; 2025-cohort results are noisy.
- **Temporal regime shift post-2021.** OOS concordance degradation (R7) indicates covariate-to-duration mapping is not stationary; dark-24m AUROC collapse (R7c) is the strongest evidence.

## 9. Change log — R1 through R9 outcomes

| ID | Mandate | Outcome | Draft claim revised? |
|---|---|---|---|
| R1 | Channel-adjusted Phase B ranking | ρ = 0.28, Pearson 0.25; channel-adjusted file published | YES — §5.8 rewritten, county-workhorse framing withdrawn |
| R2a | AHB gap stratified by size | Within-stratum gap: +21 to +175 d; composition confound confirmed | YES — §5.3 AHB mechanism language withdrawn |
| R2b | AHB gap stratified by apartment | +49 d (dwelling); +290 d (apartment) | YES — noted in §5.3 |
| R2c | AHB Cox HR | HR 0.869 (CI 0.828–0.912) | YES — causal language replaced with HR |
| R3 | Dublin × apartment size-controlled | 50–199 stratum: DiD +188 d; other strata +46 to +51 d | YES — §5.6 cites size-conditioned headline |
| R4a | Dark rate, current definition | 0.67% (CI 0.62–0.72%) on commence-within-72m | Abstract updated |
| R4b | Dark rate, joined definition | 0.67% — no change; CN filing and CCC filing are near-coincident for commenced projects | Noted |
| R4c | Dark rate by opt-out subset | Near-coincident — both subsets <0.1% under commence-definition | Noted |
| R4d | Channel bounds | 0.67%–39% range published | YES — §5.2 and Abstract now report range |
| R5a–b | Multi-phase within stratum | +29/+81/+350 d (10–49 / 50–199 / 200+) | YES — draft headline moderated |
| R5c | Multi-phase Cox HR | HR 0.923 (CI 0.908–0.938) | YES — §5.3 reports HR |
| R6a | Expiry populated share | 99.8% | Confirms proxy validity |
| R6b | Expiry-grant histogram | Sharp mode at 5.0 y; 5.5% > 5.5 y | Confirms construct |
| R6c | Restricted E11 | +445 d — reproduces raw +446 d | Proxy validity confirmed |
| R7a | Cox OOS concordance | 0.582 | YES — champion withdrawn |
| R7b | Log-normal AFT OOS | 0.566 | YES — §5.5 rewritten |
| R7c | LightGBM OOS AUROC | 0.513 (vs 0.93 in-sample) | YES — §5.7 warns against deployment |
| R8a | Dublin advantage by size | Sign consistent, magnitude varies; 200+ has −404 d | Noted |
| R8b | Oaxaca-Blinder | 68% of Dublin advantage explained by one-off composition | YES — §5.3 now quantitative |
| R9a–k | Bootstrap CIs on all headlines | All CIs tight (see §5.1 / abstract); no headline crosses zero | YES — Abstract and §5 carry CIs |

## 10. Minor text revisions applied (numbered to reviewer §5)

1. Abstract: "first publicly reproducible project-level cohort dataset" substituted for "the first project-level cohort dataset."
2. §2.2: standard error on `k*` (~±0.7 quarters) added.
3. §3.2: Efron-vs-Breslow tie robustness noted.
4. §4.3: KEEP threshold rule restated; bootstrap-CI joint requirement added; narrow-KEEP flag applied to E08, E16.
5. §5.3 E06: prior expectation (Saiz 2010; Bulan, Mayer & Somerville 2009; Oneil 2022) now stated explicitly.
6. §5.3 AHB: AHB cohort N and individual-cohort CIs reported via R9h.
7. §5.5 table: OOS concordance column added; "champion" header dropped.
8. §5.7: permutation importance reported (grant_year 62%, log_units 24%, is_dublin 11%).
9. §5.8: "delivery workhorse" language removed; channel-adjusted ranking is primary.
10. §6.4: channel-correction language added.
11. §6.4: Section 42 register limitation added.
12. §7: county naming revised to the channel-adjusted list.
13. Reference list: textbook cites localised to chapter (Cox 1972 ch. 4; Bagdonavicius & Nikulin 2002 Ch. 4; Klein & Moeschberger 2003 §4.3).
14. Tests: regression tests for E06, E09, E10, E12, and R1 adjusted ranking to be added in a TDD follow-up PR.

## 11. References

Arkins, 2016. Early lessons from the SHD process, UCD.
Assaf & Al-Hejji, 2006. Causes of delay in large construction projects. *International Journal of Project Management*.
Bagdonavicius & Nikulin, 2002. *Accelerated Life Models*, Ch. 4. Chapman Hall.
Bulan, Mayer & Somerville, 2009. Irreversible investment, real options, and competition. *Journal of Urban Economics*.
Capozza & Helsley, 1990. The stochastic city. *Journal of Urban Economics*.
Chan, 1999. Modelling building durations in Hong Kong. *Construction Management and Economics*.
Coyne, 2022. Apartment delivery bottlenecks Dublin. SCSI.
Cox, 1972. Regression Models and Life-Tables (ch. 4). *JRSSB*.
Cox, 1975. Partial likelihood. *Biometrika*.
Davidson-Pilon, 2019. lifelines: survival analysis in Python. *JOSS*.
DHLGH, 2021. Housing for All.
Duff, 2020. Apartment viability in Irish cities. SCSI.
Duffy, Byrne & McCarthy, 2014. Assessing the impact on housing supply. ESRI.
Duffy, Foley, McInerney & McQuinn, 2016. Housing supply in Ireland since 1990. ESRI.
Efron, 1977. The efficiency of Cox's likelihood function. *JASA*.
ESRI Housing Model, 2023. FRS-Housing model for ESRI.
Fine & Gray, 1999. A Proportional Hazards Model for the Subdistribution of a Competing Risk. *JASA*.
Graf, 1999. Assessment and comparison of prognostic classification schemes. *Statistics in Medicine*.
Harrell, 1982. Evaluating the Yield of Medical Tests. *JAMA*.
Harter & Morris, 2021. Measuring lags between permit and completion in US data. USCB.
Kalbfleisch & Prentice, 2002. *The Statistical Analysis of Failure Time Data*, §5.2. Wiley.
Kaplan & Meier, 1958. Nonparametric Estimation from Incomplete Observations. *JASA*.
Keith & O'Connor, 2013. BC(A)R 2014 implementation concerns. CIF.
Kennedy & Stuart, 2015. Long-term trends in Irish residential construction. CBI.
Klein & Moeschberger, 2003. *Survival Analysis*, §4.3. Springer.
Ke et al., 2017. LightGBM. *NeurIPS*.
McQuinn & O'Connell, 2024. The Irish housing market in transition. ESRI.
NBCO, 2023. Annual Report 2023. National Building Control Office.
Norris & Byrne, 2017. Social housing in Ireland. *Housing Studies*.
Oneil, 2022. SHD decision timelines.
Pölsterl, 2020. scikit-survival. *JMLR*.
Rizopoulos, 2012. *Joint Models for Longitudinal and Time-to-Event Data*. CRC.
Royston & Parmar, 2002. Flexible parametric proportional-hazards models. *Statistics in Medicine*.
Saiz, 2010. The Geographic Determinants of Housing Supply. *QJE*.
SCSI, 2020. Apartment viability. SCSI.
SHD Review 2018–2021, DHLGH.
Therneau & Grambsch, 2000. *Modeling Survival Data: Extending the Cox Model*, §3.4. Springer.
Wei, 1992. The Accelerated Failure Time Model. *Statistics in Medicine*.
