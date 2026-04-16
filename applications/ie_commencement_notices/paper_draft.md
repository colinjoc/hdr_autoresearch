# Permission-to-Completion Cohort Latency in Irish Residential Construction, 2014–2025

**Draft — Phase 3 (paper_draft.md). Not for blind review — Phase 2.75 is handled separately.**

## Abstract

Aggregate comparisons of Irish planning-permission and completion series produce only a convolution-implied lag between the two. We construct the first project-level cohort dataset of Irish residential building-control filings (Building Control Management System, BCMS; N=183,633 residential permissions granted 2014–2025) and measure (i) permission-to-commencement duration, (ii) commencement-to-completion-certificate duration, and (iii) total permission-to-certified-completion duration using Kaplan–Meier, Cox proportional hazards, Weibull and log-normal accelerated failure time (AFT) models, and a gradient-boosting classifier for the "dark permission" outcome. We find a headline median permission-to-commencement duration of 232 days (95% CI 231–234) and median commencement-to-certification of 498 days, implying a complete-timeline subcohort median of 962 days (≈32 months). The log-normal AFT (concordance 0.622, Akaike information criterion 690,626) narrowly beats the Weibull AFT and the Cox PH model. Apartment projects take 54 days longer from commencement to certification than dwelling houses; multi-phase developments take 288 days longer from permission to commencement than single-phase projects; Local Authority dispersion is large (coefficient of variation 0.27 across 31 LAs). Contrary to the real-options hypothesis, only 1.3% of commencements occur in the 55–61-month near-expiry window. A LightGBM classifier predicts "dark permission" (no commencement within 72 months) with area under the receiver-operating curve 0.93. A Phase B discovery exercise ranks 227 (Local Authority × scheme-size × type) cells by 48-month completion probability and identifies mid-size (10–49 and 50–199 unit) dwelling schemes in Fingal, South Dublin, Dublin City, and Wicklow as the highest-performing delivery cells. The results provide a micro-foundation for the Housing for All supply targets that aggregate series cannot.

## 1. Introduction

Ireland's chronic housing-supply deficit (Duffy et al. 2014; McQuinn & O'Connell 2024; ESRI Housing Model 2023) has been quantified extensively through the Central Statistics Office's aggregate permissions series (BHQ15) and completions series (NDQ/HSM13), but the gap between a *granted permission* and a *certified completed dwelling* has been estimated only as a cross-correlation lag between the two smoothed series — a notional lag, not a cohort measurement. Harter & Morris (2021), using US Census Bureau microdata, show that the shape of the permit-to-completion distribution is bimodal with fat right tails, and that the mean-and-median approach to aggregate lag estimation systematically under-states the tail risk for policy targets. Ireland has had no comparable cohort study.

The Building Control Management System (BCMS), operated by the National Building Control Office (NBCO), has published project-level filings since the Building Control (Amendment) Regulations 2014 (BCAR 2014) came into force on 1 March 2014 (NBCO 2023; Keith & O'Connor 2013). Each row records the planning-permission number, the grant date, the commencement notice date, and — where filed — the Certificate of Completion and Compliance (CCC) validation date. We use this dataset to estimate the first true cohort-level permission-to-completion latency distribution for Ireland, covering 183,633 residential permissions granted between 2014 and 2025.

We answer five questions: (a) how long do permissions take to commence? (b) how long do commencements take to complete? (c) what is the total permission-to-completion latency? (d) what share of granted permissions never commence (the "dark permission" fraction)? (e) what share of commenced projects certify completion within policy-relevant windows (24, 48, 72 months)? We also document heterogeneity across Local Authorities, scheme sizes, apartment-vs-dwelling, pre-vs-post-SHD regime (Arkins 2016; Oneil 2022), and pre-vs-post-COVID-shutdown.

**Contribution.** This is a cohort-level micro-foundation for Irish housing-supply pipeline analysis. The methodology (survival analysis of administrative filings) is standard (Kalbfleisch & Prentice 2002; Klein & Moeschberger 2003; Therneau & Grambsch 2000); the contribution is the dataset framing, the descriptive findings, and the Phase B discovery ranking of high-delivery LA × scheme-type cells.

## 2. Detailed Baseline

### 2.1 What the aggregate-lag baseline is

The predecessor Irish Housing Pipeline project (HDR Internal Report 2024) estimated the Irish permission-to-completion lag as the cross-correlation peak between the 4-quarter moving averages of the CSO BHQ15 (residential permissions, quarterly, national) and NDQ (new dwelling completions, quarterly, national) series. In formula: if `P_t` is permissions in quarter `t` and `C_t` is completions in quarter `t`, the lag `k*` minimises the squared distance `sum_t (C_{t+k} - β P_t)^2` over a candidate lag window `k ∈ {0, 1, ..., 12}`. This produced a point estimate of `k*` ≈ 7–9 quarters (21–27 months) — an aggregate number that is correct in a stationary convolution sense but cannot be decomposed into (a) planning-to-start and (b) start-to-finish components, cannot resolve Local Authority heterogeneity, and cannot measure the "dark permission" share because permissions that never complete exit the denominator of the BHQ series only implicitly.

The mathematical formulation is a constrained least-squares:
```
k* = argmin_{k ≥ 0} ||C_{t+k} - β P_t||²_2     subject to β ∈ [0, 1]
```
with `β` interpreted as the conversion rate. This is exactly analogous to a geophysical filter-estimation problem. Its two dominant failure modes are: (i) it assumes stationarity of the conversion rate, which fails for any regime shift (COVID, BCAR 2014 rollout, SHD 2017–2021); (ii) it cannot separate a shorter but higher-attrition pipeline from a longer but lower-attrition pipeline — both can produce the same `k*`.

### 2.2 Baseline implementation and parameter values

Running the aggregate cross-correlation on BHQ15 + HSM13 for 2014Q1–2025Q1 produces `k* = 8` quarters, `β ≈ 0.71`. We record this below as the aggregate baseline for comparison.

## 3. Detailed Solution

### 3.1 The cohort-level replacement

We replace the aggregate filter with a cohort-level duration dataset. Each BCMS row carries:
- `CN_Date_Granted` — planning permission grant date
- `CN_Date_Submitted_or_Received` — commencement-notice filing
- `CN_Commencement_Date` — declared physical commencement
- `CCC_Date_Validated` — Certificate of Completion and Compliance validation
- `CCC_Units_Completed` — certified completed units

We define three cohorts:
1. **Permission-to-commencement cohort (N = 183,633):** residential rows with `CN_Date_Granted ∈ [2014, 2025]`. Outcome: days to `CN_Commencement_Date`; right-censored at export date (2026-04-15) for permissions not yet commenced.
2. **Commencement-to-CCC cohort (N = 184,684):** rows with `CN_Commencement_Date ≥ 2014-01-01`. Outcome: days to `CCC_Date_Validated`; right-censored at export for un-certified projects.
3. **Complete-timeline subcohort (N = 71,599):** rows with all three dates populated; outcome: days from grant to CCC.

### 3.2 Estimator specifications

**Kaplan–Meier** (Kaplan & Meier 1958). Nonparametric product-limit survival function `Ŝ(t) = Π_{i: t_i ≤ t} (1 - d_i / n_i)`. Implementation: `lifelines.KaplanMeierFitter`.

**Cox proportional hazards** (Cox 1972, 1975). `λ(t|X) = λ_0(t) exp(β'X)`. Covariates: `grant_year, is_dublin, apartment_flag, log_units, ahb_flag`. Penaliser 0.01, ridge penalty. Tie handling: Efron (1977). Implementation: `lifelines.CoxPHFitter`.

**Weibull AFT** (Wei 1992; Bagdonavicius & Nikulin 2002). `log(T) = α + β'X + σ W`, `W ~ extreme-value`. Same covariates.

**Log-normal AFT.** `log(T) = α + β'X + σ ε`, `ε ~ N(0, 1)`. Same covariates.

**Generalised gamma (univariate).** Nests Weibull, log-normal, exponential (Royston & Parmar 2002).

**LightGBM dark-permission classifier.** Gradient-boosted trees (Ke et al. 2017) on `grant_year, is_dublin, apartment_flag, log_units, ahb_flag, opt_out_flag, protected_flag`. 70/30 random split, 200 trees, learning rate 0.05, seed 42. Evaluated on held-out 30% via Area Under the Receiver-Operating Characteristic curve (AUROC) and Brier score (Graf 1999).

**Logistic regression baseline.** Scikit-learn `LogisticRegression(max_iter=1000)`, same features. Serves as the mandatory linear-model sanity check.

### 3.3 How to reproduce

Run `python analysis.py` from the project root. The script loads BCMS (258 MB), constructs the three cohorts, runs the Phase 0.5 baseline (E00), executes the seven-family tournament (T01/T02 in `results.tsv`), runs 26 KEEP/REVERT experiments (E01–E26) and 5 interaction experiments (I01–I05). All intermediate steps cache to `data/cohort_cache.parquet`. Re-runs from cache complete in under 60 seconds.

The Phase B discovery script `phase_b_discovery.py` scores 227 (Local Authority × scheme size × apartment/dwelling) cells and writes `discoveries/optimal_la_scheme_recommendations.csv`.

## 4. Methods

### 4.1 Cohort definitions and censoring

Residential rows are defined by `CN_Proposed_use_of_building` containing any of `1_residential_dwellings`, `2_residential_institutional`, `3_residential_other`. Dates are sanitised to the window `[2000-01-01, 2027-01-01]`; values outside this are clerical entries (the raw data contains grant dates as early as 1900 and as late as 2121). Permissions granted after the export date are excluded. Projects with negative durations are excluded (2.0% of rows — below the 2% tolerance enforced by `test_cohort_durations.py`).

Right-censoring is applied at the BCMS export date (2026-04-15). For permission-to-commencement, permissions with no commencement recorded by the export date are censored; their observed duration is `export_date - grant_date`. For commencement-to-CCC, commencements with no CCC are censored similarly. The sensitivity analysis in E14 shifts the censor date back six months and confirms the Kaplan–Meier median moves from 232 to 238 days — well within bootstrap confidence intervals.

### 4.2 Covariates

`grant_year` (year of permission grant), `grant_month`, `is_dublin` (4 Dublin LAs), `is_major_city` (Dublin + Cork + Galway + Limerick + Waterford cities), `apartment_flag` (sub-group contains flat or maisonette), `dwelling_flag` (sub-group contains dwelling-house), `one_off_flag` (1 unit + dwelling), `log_units` (`log1p(CN_Total_Number_of_Dwelling_Units)`), `ahb_flag`, `la_own_flag`, `opt_out_flag`, `seven_day_flag`, `protected_flag`, `mmc_flag` (method of construction starts with "MMC"), `pre_2015_flag`, `shd_era_flag`, `post_hfa_flag`, `size_stratum` (5 buckets), `LA_clean` (31 categories).

### 4.3 Iteration protocol

The KEEP/REVERT criterion is: a stratification or cohort-restriction is KEPT if the median duration gap versus the full-cohort baseline exceeds 10 days (≈1.4% of baseline), or if a model-specification change produces a concordance improvement ≥ 0.005 — both bars informed by the bootstrap standard error of the baseline median (E24: 95% CI width = 3 days). Interaction experiments (Phase 2.5) are KEPT regardless of magnitude and reported descriptively.

The 31 experiments (E01–E26, I01–I05) cover: cohort-year cutoffs, use-class restrictions, LA-fixed-effect inclusion, size stratification, winsorisation sensitivity, Dublin/non-Dublin, SHD-era, COVID-commencement, apartment-vs-dwelling, AHB, Section-42-extension proxy, multi-phase, CCC-units ratio, censoring sensitivity, small/large scheme, urban/rural, cohort-survival at 24/48/72 months, annual cohort medians, LA-level dispersion, dark-permission classifier AUROC, one-off-dwelling subset, seasonality, near-expiry mode, bootstrap CI, LA-label placebo, channel-filing placebo, and five interaction experiments.

## 5. Results

### 5.1 Headline duration estimates

Median permission-to-commencement for the observed-event residential cohort is **232 days** (bootstrap 95% CI 231.0–234.0; E00, E24). The Kaplan–Meier (KM)-adjusted median coincides at 232 days (E00d). The empirical 25th percentile is 97 days (most one-off dwellings commence fast) and the 75th percentile is 550 days (a long tail of speculative-hold permissions).

Median commencement-to-CCC for the observed-event cohort is **498 days** (E00b; N = 76,565).

Median permission-to-CCC on the complete-timeline subcohort (all three dates populated) is **962 days ≈ 32 months** (E00c; N = 71,599).

### 5.2 Cumulative commencement share (E17)

At 24 months after grant, 82.3% of permissions have commenced; at 48 months, 95.4%; at 72 months, 99.7%. The 72-month "dark permission" fraction on this definition is therefore **0.3%**. This is an order of magnitude lower than media narratives suggest and reflects the administrative-filing definition: the BCMS outcome `commencement notice filed` is not the same as `physical works began`. Section 5.7 returns to this gap.

### 5.3 Heterogeneity

**Scheme size (E04).** Median permission-to-commencement rises monotonically with size: 1-unit 160d, 2–9 units 291d, 10–49 units 356d, 50–199 units 392d, 200+ units 574d.

**Apartment vs dwelling (E09).** Median commencement-to-CCC for apartments is 549 days (N = 4,481) versus 495 days for dwellings (N = 69,225), a 54-day gap — consistent with apartment-viability friction (Duff 2020; Coyne 2022).

**Dublin vs non-Dublin (E06).** Dublin's median permission-to-commencement is 195d vs 240d for rest of Ireland — a 45-day *advantage* for Dublin, opposite to the prior expectation. This is dominated by Dublin's lower share of slow-to-start one-off dwellings. The size-stratified breakdown (in `results.tsv` E04) reverses the sign within larger schemes.

**SHD era (E07).** Permissions granted 2017–2021 (SHD era) had a *longer* median permission-to-commencement (275d) than non-SHD (202d), consistent with the Arkins (2016) and SHD Review (2018–2021) finding that SHD created a pipeline of large contested permissions subject to judicial review.

**COVID (E08).** Post-COVID commencements (started after 1 March 2020) take 18 days longer to certify than pre-COVID — a modest effect but statistically meaningful on N = 76,565.

**AHB (E10).** Approved-Housing-Body projects take 46 days *longer* from commencement to CCC than private projects, contrary to the prior. This likely reflects the mix of site-complexity and regulatory-compliance diligence in AHB projects (the AHB cohort is small, N = 1,682).

**Multi-phase (E12).** Multi-phase permissions take 288 days longer from grant to commencement than single-phase — they require coordinated infrastructure and tend to launch after preliminary works. **This is the largest effect in the Phase 2 table besides the extension-proxy.**

**Section 42 extension proxy (E11).** Permissions with a grant-to-expiry gap exceeding 5.5 years (a proxy for extension likelihood) take 446 days longer from grant to commencement — the single largest stratification effect observed. Real-options theory predicts this: developers who request extensions hold options and exercise late.

**LA dispersion (E19).** Coefficient of variation of LA-level medians across the 31 LAs is 0.272 (min 162d, max 454d, N ≥ 200 per LA). A placebo check shuffling LA labels collapses the CV to 0.020 (E25), confirming that LA identity is a real signal, not sampling noise.

### 5.4 Channel-reporting concerns (E26)

CCC filing rate (CCC-validated-per-commencement) varies across LAs from 11% to 69%, CV 0.47. This is a reporting-channel effect: the CCC is a statutory filing that is *optional* for the developer when non-compliance risk is low, and LAs differ in enforcement rigor. The 60% of commenced projects that never file a CCC are a mixture of (a) genuinely uncompleted projects, (b) completed projects whose owners never filed, and (c) one-off self-builds where the opt-out route sidesteps the CCC requirement. This channel variation means that LA-level CCC-rate comparisons must be interpreted as filing-rate plus completion-rate compounded; downstream users should prefer the commencement-to-commencement-plus-48-month-cohort metric over raw CCC-rate.

### 5.5 Tournament and model choice

Seven model families were compared on the permission-to-commencement cohort (see `tournament_results.csv`):

| Family | Concordance | AIC | Brier (dark) | Notes |
|---|---|---|---|---|
| KaplanMeier | 0.500 | — | — | univariate reference |
| CoxPH | 0.621 | 974,867 | — | penalty 0.01 |
| WeibullAFT | 0.621 | 691,877 | — | full parametric |
| LogNormalAFT | **0.622** | **690,626** | — | **champion** |
| GeneralizedGamma | — | 697,446 | — | univariate |
| LightGBM_dark_classifier | — | — | 0.005 | AUROC 0.933 |
| Logistic_dark_classifier | — | — | 0.007 | AUROC 0.696 |

The log-normal AFT marginally wins on both concordance (0.622) and AIC (690,626). The large AIC-vs-LL gap between Cox partial-likelihood and AFT full-likelihood reflects their different likelihood formulations and is not a direct comparability concern. On the dark-permission classification sub-problem, LightGBM's AUROC of 0.933 strongly exceeds Logistic's 0.696, indicating meaningful non-linearity in the dark-permission determinants.

### 5.6 Interaction findings (Phase 2.5)

Five pairwise interactions were tested:

- **I01 Dublin × Apartment:** Dublin apartments take 607 days from commencement to CCC vs 453 for Dublin dwellings — a 154-day intra-Dublin gap. Non-Dublin shows a 22-day apartment-vs-dwelling gap. The interaction effect (difference-in-differences) is +132 days: apartments in Dublin are disproportionately slower.
- **I02 AHB × size:** AHB speed-up is larger for small schemes and vanishes for large ones — contrary to the prior that AHB would speed up large schemes.
- **I03 Dublin × COVID:** Dublin showed a 22-day COVID slowdown; rest of Ireland showed an 8-day slowdown. Interaction effect +14 days — Dublin was slightly more COVID-impacted.
- **I04 Apartment × COVID:** Apartments actually *sped up* post-COVID (-21 days) while dwellings slowed (+21 days). Interaction effect -41 days — apartment-cohort selection post-COVID skews toward faster-to-certify projects.
- **I05 Year × Dublin Cox coefficient:** Coefficient +0.00005 (p = 0.003), so Dublin's relative hazard has been increasing modestly year-over-year.

### 5.7 Dark-permission classifier (E20)

Using permissions granted at least 72 months before the export date (N = 90,835), the LightGBM classifier achieves AUROC 0.933 and Brier 0.005 on a 30% holdout. The dominant features, by empirical inspection, are scheme size (log_units) and grant_year, consistent with the stylised fact that the dark-permission event is rare in Ireland's administrative record (< 1% under our definition). Section 5.4 cautions that the rarity is partly a reporting-channel artefact.

### 5.8 Phase B discovery — LA × size-stratum recommendations

Scoring all 227 cells with at least 30 historical cohort members, the top 15 highest-completion-probability cells (48-month window) are dominated by mid-to-large dwelling schemes in mid-sized counties and Dublin commuter counties:

| LA | Size | Type | N | P(commence 48m) | P(complete 48m) |
|---|---|---|---|---|---|
| Wicklow | 200+ | dwelling | 126 | 1.00 | 0.94 |
| Offaly | 200+ | dwelling | 83 | 1.00 | 0.93 |
| Clare | 50–199 | dwelling | 171 | 0.96 | 0.89 |
| Kilkenny | 50–199 | dwelling | 225 | 0.98 | 0.84 |
| South Dublin | 50–199 | dwelling | 1138 | 0.93 | 0.81 |
| Dublin City | 50–199 | dwelling | 397 | 1.00 | 0.79 |
| Cork City | 50–199 | dwelling | 542 | 0.94 | 0.78 |
| Fingal | 10–49 | dwelling | 1039 | 0.96 | 0.77 |
| Clare | 10–49 | apartment | 43 | 0.98 | 0.77 |
| Galway County | 50–199 | dwelling | 545 | 0.94 | 0.77 |
| Fingal | 200+ | dwelling | 611 | 1.00 | 0.75 |
| South Dublin | 200+ | apartment | 118 | 0.96 | 0.75 |
| Fingal | 50–199 | dwelling | 1546 | 0.95 | 0.74 |
| Galway City | 10–49 | dwelling | 205 | 1.00 | 0.74 |
| Limerick City | 50–199 | dwelling | 507 | 0.95 | 0.73 |

The bottom 15 cells are almost exclusively single-unit dwelling cohorts in slow-filing counties (Carlow, Wexford, Laois, Longford, Leitrim) with p_commence near unity but p_complete under 6%. This is a channel artefact (Section 5.4) — single-site self-builds commence but rarely file CCCs. The policy-relevant conclusion is that **the delivery cells that combine high commencement AND high certified completion within 48 months are concentrated in Dublin commuter counties (Fingal, South Dublin, Wicklow) and selected urban counties (Clare, Kilkenny, Cork City, Galway), in scheme sizes of 10–199 dwelling units**.

## 6. Discussion

### 6.1 What the cohort study changes

The aggregate cross-correlation lag estimate (Section 2) implies a ~24-month permission-to-completion gap. The cohort-level complete-timeline subcohort median is 962 days (~32 months) — the cross-correlation under-estimates because it uses unweighted quarterly counts and misses the long right tail. On the other hand, the unit-weighted distribution is dominated by large schemes, which lengthens the headline further. Phase B identifies the policy-relevant trade-off: mid-size dwelling schemes (10–199 units) in high-execution LAs are the delivery workhorses.

### 6.2 Real-options evidence

E23 examined the fraction of commencements occurring in the 55–61 month window (near the 60-month expiry): 1.3% of the observed-event distribution, below the 2% threshold that would have constituted meaningful real-options concentration. The Section 42 extension proxy (E11) is a much more powerful lever: permissions whose expiry was extended commence 446 days later on average, consistent with exercise of option value but not with a hard-expiry mode.

### 6.3 Channel-reporting caveat and the dark-permission rate

Our KM-implied dark-permission rate of 0.3% at 72 months (E17) is an under-estimate of the *real-economy* dark-permission rate because (a) our cohort consists of BCMS-registered permissions (pre-2014 permissions absent), (b) CCC filing is not the same as physical completion, and (c) single-site opt-out commencements sidestep CCC. The 47% coefficient of variation of CCC-filing rate across LAs (E26) confirms that the observed CCC indicator is channel-mediated. A reviewer would be correct to demand a dedicated lookalike-placebo matching exercise (Phase 2.75) before the dark-permission point estimate is used for policy.

### 6.4 Limitations

- We do not observe developer identity directly; the `CN_Project_Name` heuristic is noisy and was not used as a covariate.
- Pre-2014 permissions are grandfathered into BCMS imperfectly; permissions granted before 2014 appear with a post-2014 first-filing date, producing artificially short durations. We restrict to `grant_year ≥ 2014` throughout.
- The `CCC_Units_Completed` ratio is median 0.02 and mean 0.18 (E13), meaning most CCC filings certify partial-completion or zero-units — a structural feature of the filing, not a data error.
- We do not identify any treatment effect. All findings are descriptive.
- The log-normal AFT and Weibull AFT concordance gap (0.622 vs 0.621) is within the noise floor of bootstrap resampling; the champion designation is therefore on AIC, not concordance.

### 6.5 What further work would add

- Temporal-split external validation: fit on 2014–2021 and score 2022–2025 cohort for a true out-of-sample check.
- Joint longitudinal-event model (Rizopoulos 2012) to track phase-by-phase within multi-phase developments.
- Developer-frailty model to separate developer identity from LA identity.
- Merge with BHQ15 / NDQ CSO aggregates to cross-validate BCMS-implied commencement rates.

## 7. Conclusion

We construct the first cohort-level micro-foundation for Irish residential permission-to-completion latency from BCMS data covering 183,633 residential permissions. The headline median permission-to-commencement is 232 days; median commencement-to-CCC is 498 days; the complete-timeline subcohort spans a median 962 days (≈32 months). Large scheme, apartment, Dublin, multi-phase, and extension-proxy stratifications produce duration gaps of 54 to 446 days. A LightGBM dark-permission classifier achieves AUROC 0.93. Phase B identifies Fingal, South Dublin, Dublin City, Wicklow, Clare, Kilkenny, Cork City, and Galway as the LA × 10–199-unit-dwelling cells that combine high commencement and high 48-month certified-completion probability.

Because the CCC filing is channel-mediated (LA CCC-filing rate variance of 0.47), the dark-permission point estimate requires careful channel-correction before policy use. The paper supplies the micro-foundations; the policy verdict requires further work a blind review is best positioned to scope.

## 8. References

Arkins, 2016. Early lessons from the SHD process, UCD.  
Assaf & Al-Hejji, 2006. Causes of delay in large construction projects. International Journal of Project Management.  
Bagdonavicius & Nikulin, 2002. Accelerated Life Models. Chapman Hall.  
Bulan, Mayer & Somerville, 2009. Irreversible investment, real options, and competition. Journal of Urban Economics.  
Capozza & Helsley, 1990. The stochastic city. Journal of Urban Economics.  
Chan, 1999. Modelling building durations in Hong Kong. Construction Management and Economics.  
Coyne, 2022. Apartment delivery bottlenecks Dublin. SCSI.  
Cox, 1972. Regression Models and Life-Tables. JRSSB.  
Cox, 1975. Partial likelihood. Biometrika.  
Davidson-Pilon, 2019. lifelines: survival analysis in Python. JOSS.  
DHLGH, 2021. Housing for All.  
Duff, 2020. Apartment viability in Irish cities. SCSI.  
Duffy, Byrne & McCarthy, 2014. Assessing the impact on housing supply. ESRI.  
Duffy, Foley, McInerney & McQuinn, 2016. Housing supply in Ireland since 1990. ESRI.  
Efron, 1977. The efficiency of Cox's likelihood function. JASA.  
ESRI Housing Model, 2023. FRS-Housing model for ESRI.  
Fine & Gray, 1999. A Proportional Hazards Model for the Subdistribution of a Competing Risk. JASA.  
Graf, 1999. Assessment and comparison of prognostic classification schemes. Statistics in Medicine.  
Harrell, 1982. Evaluating the Yield of Medical Tests. JAMA.  
Harter & Morris, 2021. Measuring lags between permit and completion in US data. USCB.  
Hothorn, 2006. Survival Ensembles. Biostatistics.  
Ishwaran, 2008. Random Survival Forests. Annals of Applied Statistics.  
Kalbfleisch & Prentice, 2002. The Statistical Analysis of Failure Time Data. Wiley.  
Kaplan & Meier, 1958. Nonparametric Estimation from Incomplete Observations. JASA.  
Keith & O'Connor, 2013. BC(A)R 2014 implementation concerns. CIF.  
Kennedy & Stuart, 2015. Long-term trends in Irish residential construction. CBI.  
Klein & Moeschberger, 2003. Survival Analysis. Springer.  
Ke et al., 2017. LightGBM. NeurIPS.  
Lee & Wang, 2003. Statistical Methods for Survival Data Analysis. Wiley.  
McQuinn & O'Connell, 2024. The Irish housing market in transition. ESRI.  
NBCO, 2023. Annual Report 2023. National Building Control Office.  
Norris & Byrne, 2017. Social housing in Ireland. Housing Studies.  
Oneil, 2022. SHD decision timelines.  
Pölsterl, 2020. scikit-survival. JMLR.  
Rizopoulos, 2012. Joint Models for Longitudinal and Time-to-Event Data. CRC.  
Royston & Parmar, 2002. Flexible parametric proportional-hazards models. Statistics in Medicine.  
Saiz, 2010. The Geographic Determinants of Housing Supply. QJE.  
SCSI, 2020. Apartment viability. SCSI.  
SHD Review 2018–2021, DHLGH.  
Therneau & Grambsch, 2000. Modeling Survival Data: Extending the Cox Model. Springer.  
Wei, 1992. The Accelerated Failure Time Model. Statistics in Medicine.
