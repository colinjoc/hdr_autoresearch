# Research Queue — PL-1 Irish Commencement-Notice Cohort Study

Each hypothesis has: `id`, `theme`, `mechanism`, `design_variable`, `metric`, `baseline`, `prior` (probability the experiment returns a KEEP), `impact` (Expected Δ + Novelty + Mechanistic clarity, range 3-9), `status` (OPEN / RUN / KEEP / REVERT / BLOCKED), `posterior` (updated after run).

Long-shot quota target: ≥20 percent with prior ≤0.3.

---

## Theme A — Cohort definition and data quality

- **H001** | cohort | Excluding pre-2015 rows cleans up a data-quality ramp-up; pre-2015 reporting was sparse as BCMS phased in. | DV=year_cutoff. Metric=median permission-to-commencement duration and its SE. Baseline=no cutoff. Prior=0.7. Impact=6. Status=OPEN.
- **H002** | cohort | Dropping rows where CN_Date_Granted < 2010 or > today removes nonsensical permission dates (dataset has min=1900, max=2121). Prior=0.95. Impact=4. Status=OPEN.
- **H003** | cohort | Median absolute deviation (MAD) filter on permission-to-commencement at 5*MAD removes clerical errors (negative durations, 100-year gaps). Prior=0.85. Impact=5. Status=OPEN.
- **H004** | cohort | Restricting to CN_Proposed_use_of_building containing `1_residential_dwellings` produces a cleaner residential cohort than including types 2 and 3. Prior=0.55. Impact=5. Status=OPEN.
- **H005** | cohort | Restricting to CN_Validation_Status == "Valid" removes rejected/withdrawn notices. Prior=0.7. Impact=4. Status=OPEN.
- **H006** | cohort | Using CN_Commencement_Date vs CN_Date_Submitted_or_Received as the "commencement" timestamp changes the median by <5 days. Prior=0.6. Impact=3. Status=OPEN.
- **H007** | cohort | Rows with CN_Total_Number_of_Dwelling_Units == 0 are administrative ghosts and should be excluded from unit-weighted analyses. Prior=0.9. Impact=3. Status=OPEN.
- **H008** | cohort | De-duplicating on CN_Planning_Permission_Number yields a project-level dataset; the unit of analysis should be project, not building. Prior=0.75. Impact=5. Status=OPEN.
- **H009** | cohort | Phase field (CN_Phase_for_this_Notice, CN_Total_Number_of_Phases) isolates multi-phase developments; phase 1 completion predicts phases 2+ commencement. Prior=0.55. Impact=6. Status=OPEN.
- **H010** | cohort | Opt-out commencement notices (CN_Project_type == Opt_Out_Comm_Notice) have shorter permission-to-commencement because they are predominantly one-off self-builds with ready sites. Prior=0.8. Impact=6. Status=OPEN.

## Theme B — Heterogeneity by geography

- **H011** | geo | Dublin (4 LAs) has longer permission-to-commencement medians than non-Dublin because land assembly, appeals, and ground-condition surprises are more frequent. Prior=0.65. Impact=7. Status=OPEN.
- **H012** | geo | Urban density (Dublin + Cork + Limerick + Galway + Waterford cities) vs rural produces a 6-9 month duration gap. Prior=0.6. Impact=6. Status=OPEN.
- **H013** | geo | Specific LAs with known planning-appeal backlogs (Dún Laoghaire-Rathdown, Dublin City) show the longest commencement-to-completion tails. Prior=0.5. Impact=6. Status=OPEN.
- **H014** | geo | County-level spatial clustering of durations is statistically significant under Moran's I. Prior=0.6. Impact=5. Status=OPEN.
- **H015** | geo | LAT/LNG binned into 5km cells produces stable within-cell duration medians that differ from the national median by ±3 months. Prior=0.4. Impact=6. Status=OPEN.
- **H016** | geo | Distance-to-Dublin-CBD predicts longer permission-to-commencement (periphery has cheaper land, speculation, wait-for-infrastructure delays). Prior=0.35. Impact=6. Status=OPEN.
- **H017** | geo | Rural one-off dwellings (rural LA + 1-unit + detached) commence faster (median ~60 days) because the developer IS the owner. Prior=0.85. Impact=5. Status=OPEN.
- **H018** | geo | Dublin commercial-core LAs (DCC) have lower cure fraction (dark permissions) because land is more valuable to hold. Prior=0.3. Impact=7. Status=OPEN.
- **H019** | geo | LA frailty term in a Cox shared-frailty model explains 20%+ of residual variance after observable covariates. Prior=0.55. Impact=7. Status=OPEN.
- **H020** | geo | Border counties (Donegal, Monaghan, Louth, Cavan) have longer durations due to cross-Border material sourcing. Prior=0.25. Impact=5. Status=OPEN.

## Theme C — Heterogeneity by development type

- **H021** | type | Apartments (CN_Proposed_use_of_building contains apartments markers OR CN_Sub_Group contains flat/maisonette) have longer commencement-to-completion than dwelling houses. Prior=0.9. Impact=8. Status=OPEN.
- **H022** | type | Apartments have longer permission-to-commencement too (financing friction). Prior=0.75. Impact=7. Status=OPEN.
- **H023** | type | Modular construction (CN_Main_Method_of_Construction starts with "MMC") shortens commencement-to-completion by 3-6 months. Prior=0.45. Impact=7. Status=OPEN.
- **H024** | type | AHB (CN_Approved_housing_body == yes) projects commence faster because funding is pre-approved. Prior=0.55. Impact=7. Status=OPEN.
- **H025** | type | Local Authority own-build (CN_Behalf_local_authority == yes) has no cure fraction — 100% commence. Prior=0.85. Impact=5. Status=OPEN.
- **H026** | type | Dwelling houses with attached garage commence faster than detached-garage variants. Prior=0.3. Impact=3. Status=OPEN.
- **H027** | type | Protected-structure works (CN_Protected_structure == yes) have longer commencement-to-completion. Prior=0.6. Impact=5. Status=OPEN.
- **H028** | type | Project size (CN_Total_Number_of_Dwelling_Units) has a non-linear relationship with permission-to-commencement — U-shape, with 1-unit and 50+ unit fastest, mid-size slowest. Prior=0.45. Impact=7. Status=OPEN.
- **H029** | type | Log(floor_area) is a stronger predictor of commencement-to-completion than log(units). Prior=0.5. Impact=5. Status=OPEN.
- **H030** | type | Seven-Day Notice projects (non-residential rapid-build) have shorter commencement-to-completion than residential. Prior=0.85. Impact=4. Status=OPEN.

## Theme D — Temporal / regime-shift

- **H031** | regime | Median permission-to-commencement fell after Rebuilding Ireland (July 2016). Prior=0.5. Impact=7. Status=OPEN.
- **H032** | regime | Median permission-to-commencement fell after Housing for All launch (Sept 2021). Prior=0.4. Impact=7. Status=OPEN.
- **H033** | regime | SHD-era permissions (2017-2021) commenced faster than pre-SHD because the fast track bundled permissions with commitment. Prior=0.4. Impact=7. Status=OPEN.
- **H034** | regime | Commencement-to-completion lengthened during COVID (commencements in 2019-2020). Prior=0.85. Impact=6. Status=OPEN.
- **H035** | regime | Construction cost inflation 2021-2022 extended commencement-to-completion for projects mid-build. Prior=0.7. Impact=6. Status=OPEN.
- **H036** | regime | 2023-2024 commencement surge (media-reported) is concentrated in apartment projects eligible for the Croí Cónaithe scheme. Prior=0.3. Impact=7. Status=OPEN.
- **H037** | regime | The "dark permission" rate (permissions never commenced within 5 years) is higher for permissions granted in 2018-2019 than 2020-2021. Prior=0.6. Impact=8. Status=OPEN.
- **H038** | regime | Calendar-month of permission grant: winter grants (Oct-Feb) have longer time-to-commence than spring grants (Mar-May). Prior=0.35. Impact=4. Status=OPEN.
- **H039** | regime | A time-varying LA fixed effect explains more than a time-invariant LA fixed effect. Prior=0.7. Impact=6. Status=OPEN.
- **H040** | regime | Interest-rate hikes 2022-2023 lengthened permission-to-commencement via financing delays. Prior=0.55. Impact=7. Status=OPEN.

## Theme E — Statistical model choice

- **H041** | model | Kaplan-Meier curves by LA show visually distinct commencement hazards. Prior=0.9. Impact=5. Status=OPEN.
- **H042** | model | Cox PH assumption is violated for year-of-permission (time-varying effect) — Schoenfeld residuals show a p<0.01 PH violation. Prior=0.8. Impact=6. Status=OPEN.
- **H043** | model | Weibull AFT beats log-normal AFT on AIC for permission-to-commencement. Prior=0.4. Impact=5. Status=OPEN.
- **H044** | model | Log-normal AFT beats Weibull AFT on AIC for commencement-to-completion (long right tail). Prior=0.6. Impact=5. Status=OPEN.
- **H045** | model | Generalised-gamma AFT nests both Weibull and log-normal and delivers the best AIC on the full cohort. Prior=0.55. Impact=5. Status=OPEN.
- **H046** | model | Gradient-boosted survival (scikit-survival GradientBoostingSurvivalAnalysis) beats Cox PH on concordance by ≥0.02. Prior=0.45. Impact=7. Status=OPEN.
- **H047** | model | Random Survival Forest beats Cox PH on concordance by ≥0.02. Prior=0.45. Impact=6. Status=OPEN.
- **H048** | model | Shared-frailty Cox (LA as cluster) beats marginal Cox on integrated Brier. Prior=0.55. Impact=6. Status=OPEN.
- **H049** | model | LightGBM classifier for "dark permission" achieves AUROC ≥ 0.80 using grant_year, LA, units, floor_area, project_type, AHB. Prior=0.5. Impact=7. Status=OPEN.
- **H050** | model | Logistic regression baseline for dark-permission achieves AUROC within 0.02 of LightGBM (i.e. relationship is mostly linear). Prior=0.3. Impact=6. Status=OPEN.
- **H051** | model | Cure-fraction mixture model (logistic + Weibull) fits better than a plain Weibull because the dark-permission cure fraction is non-trivial (>0.1). Prior=0.65. Impact=7. Status=OPEN.
- **H052** | model | Discrete-time pooled-logistic survival with 3-month bins and a natural-spline time effect is within 0.01 concordance of continuous-time Cox. Prior=0.7. Impact=5. Status=OPEN.
- **H053** | model | Competing-risks Fine-Gray model (commence vs lapse) gives substantively different coefficient signs than marginal Cox for LA dummies. Prior=0.4. Impact=6. Status=OPEN.
- **H054** | model | Time-varying covariate (cumulative national quarterly commencements) improves concordance by ≥0.01 (macro conditions matter). Prior=0.5. Impact=6. Status=OPEN.
- **H055** | model | Stratified Cox by apartment-vs-dwelling fits better (different baseline hazards) than a single model with an apartment dummy. Prior=0.7. Impact=5. Status=OPEN.

## Theme F — Cohort survival percentiles and cure fractions

- **H056** | cure | Share of residential permissions that commence within 24 months exceeds 70 percent. Prior=0.5. Impact=6. Status=OPEN.
- **H057** | cure | Share of permissions commencing within 48 months exceeds 85 percent. Prior=0.6. Impact=6. Status=OPEN.
- **H058** | cure | Share of permissions commencing within 72 months exceeds 90 percent (i.e., dark-permission cure fraction is ≤ 10%). Prior=0.5. Impact=6. Status=OPEN.
- **H059** | cure | Commence-within-24-months share for apartments is ≤ 50 percent. Prior=0.5. Impact=7. Status=OPEN.
- **H060** | cure | Complete-within-24-months-of-commencement share for dwellings exceeds 60 percent. Prior=0.7. Impact=6. Status=OPEN.
- **H061** | cure | Complete-within-48-months-of-commencement share for apartments is ≤ 60 percent. Prior=0.55. Impact=6. Status=OPEN.
- **H062** | cure | Total permission-to-completion median (full cohort) is less than 36 months. Prior=0.4. Impact=7. Status=OPEN.
- **H063** | cure | Total permission-to-completion 75th percentile (full cohort) is less than 60 months. Prior=0.5. Impact=6. Status=OPEN.
- **H064** | cure | LA-level dark-permission rate has coefficient of variation > 0.25 across LAs. Prior=0.7. Impact=6. Status=OPEN.
- **H065** | cure | Approved-housing-body projects have near-zero dark-permission rate (below 3 percent). Prior=0.8. Impact=5. Status=OPEN.

## Theme G — Heterogeneity by project size

- **H066** | size | Small schemes (1-9 units) have a different log-linear duration structure than large schemes (50+ units). Prior=0.7. Impact=6. Status=OPEN.
- **H067** | size | The log(units) → log(commencement-to-completion) coefficient is between 0.15 and 0.35 (Bromilow-like). Prior=0.5. Impact=5. Status=OPEN.
- **H068** | size | Mega-schemes (200+ units) have longer tails (95th percentile duration > 1.5 × median). Prior=0.8. Impact=6. Status=OPEN.
- **H069** | size | Mid-sized schemes (10-49 units) have the highest dark-permission rate because they straddle viability thresholds. Prior=0.45. Impact=7. Status=OPEN.
- **H070** | size | Using units_declared vs units_completed as the size covariate changes the size-effect magnitude by <10 percent. Prior=0.6. Impact=3. Status=OPEN.

## Theme H — Unit-weighted vs project-weighted

- **H071** | weighting | Project-weighted median permission-to-commencement exceeds unit-weighted median (big schemes are faster per project, slower per unit). Prior=0.55. Impact=6. Status=OPEN.
- **H072** | weighting | Unit-weighted dark-permission rate is lower than project-weighted (big projects rarely go dark). Prior=0.75. Impact=6. Status=OPEN.
- **H073** | weighting | The Housing for All 300k-units-by-2030 target is easier to meet per-unit than per-project because of this weighting. Prior=0.55. Impact=5. Status=OPEN.

## Theme I — Data-source robustness

- **H074** | robust | Re-running the full analysis using CN_Validation_Date as the permission-commencement-proxy (instead of CN_Date_Submitted_or_Received) changes medians by <7 days. Prior=0.6. Impact=3. Status=OPEN.
- **H075** | robust | Ceramic-test: using only rows where CN_Date_Expiry is populated changes results by <5 percent. Prior=0.7. Impact=3. Status=OPEN.
- **H076** | robust | Seed stability — bootstrap medians over 1000 resamples produce a 95% CI with width < 10 days for permission-to-commencement national median. Prior=0.85. Impact=4. Status=OPEN.
- **H077** | robust | Winsorising top 1 percent of durations changes medians by 0 days (medians are winsorisation-robust by construction). Prior=0.95. Impact=2. Status=OPEN.
- **H078** | robust | Winsorising top 1 percent of durations changes means by >30 percent (means are NOT winsorisation-robust). Prior=0.8. Impact=3. Status=OPEN.
- **H079** | robust | The BCMS-implied total commencement count per year matches the CSO HSM13 aggregate within ±15 percent. Prior=0.7. Impact=6. Status=OPEN.
- **H080** | robust | BCMS-implied completions per year match CSO NDQ aggregate within ±20 percent. Prior=0.5. Impact=6. Status=OPEN.

## Theme J — Causal/placebo tests

- **H081** | placebo | Shuffling the LA label across projects and refitting produces a null coefficient distribution centred on zero. Prior=0.95. Impact=3. Status=OPEN.
- **H082** | placebo | Permission-to-commencement duration does NOT predict a placebo outcome (a randomly permuted CCC indicator). Prior=0.95. Impact=3. Status=OPEN.
- **H083** | placebo | Splitting the dataset by permission-year-even vs odd and comparing medians: the distribution is stable. Prior=0.9. Impact=3. Status=OPEN.
- **H084** | placebo | Swapping the "commencement" label with a random date in the project's grant-year produces a 95% CI for median duration that excludes the true value. Prior=0.95. Impact=4. Status=OPEN.

## Theme K — Reporting channel / observability

- **H085** | channel | The CCC filing is NOT reliably made on the date of physical completion — there is a systematic 3-6 month lag between occupancy and CCC validation. Prior=0.7. Impact=7. Status=OPEN.
- **H086** | channel | LAs differ in CCC-filing enforcement rigor: LAs with high CCC-per-commencement ratio likely run tighter enforcement, not actually completing more. Prior=0.65. Impact=7. Status=OPEN.
- **H087** | channel | Lookalike-placebo on matched un-commenced permissions shows channel bias. Prior=0.3. Impact=8. Status=OPEN.

## Theme L — Interactions

- **H088** | interaction | LA × apartment-vs-dwelling interaction changes coefficient signs for ≥3 LAs. Prior=0.5. Impact=6. Status=OPEN.
- **H089** | interaction | Year × Dublin interaction shows divergence during SHD period only. Prior=0.5. Impact=6. Status=OPEN.
- **H090** | interaction | Size × AHB interaction: AHB speeds up large schemes more than small. Prior=0.45. Impact=6. Status=OPEN.
- **H091** | interaction | Year × AHB interaction: AHB speedup is larger post-2020. Prior=0.5. Impact=6. Status=OPEN.
- **H092** | interaction | LA × year interaction: Dublin City slowed post-2022; Cork County accelerated post-2022. Prior=0.4. Impact=6. Status=OPEN.

## Theme M — Phase B discovery design

- **H093** | discovery | Top-3 LAs by 4-year completion probability account for more than 30 percent of cohort completions. Prior=0.6. Impact=6. Status=OPEN.
- **H094** | discovery | The "optimal scheme" to maximise 4-year completion is mid-size (10-29 units), dwelling-house, non-Dublin LA. Prior=0.55. Impact=7. Status=OPEN.
- **H095** | discovery | A counterfactual policy of redirecting permissions from slowest-decile LAs to fastest-decile LAs would lift nationwide 4-year completion by ≥15 pp. Prior=0.3. Impact=8. Status=OPEN.
- **H096** | discovery | The Phase B recommendation is robust to the champion model choice — Cox vs AFT gives ≥80% overlap in top-10 recommendations. Prior=0.55. Impact=6. Status=OPEN.
- **H097** | discovery | LDA-eligible sites in the "fast" LAs identified by the champion model would shorten delivery to ≤18 months. Prior=0.25. Impact=7. Status=OPEN.

## Theme N — Miscellaneous

- **H098** | misc | Seasonality: more projects commence in Q2 than Q4 (seasonal weather/funding cycle). Prior=0.7. Impact=3. Status=OPEN.
- **H099** | misc | The 2020 COVID-shutdown March-May shows a spike in Oct-Dec 2020 commencement backlog absorption. Prior=0.6. Impact=4. Status=OPEN.
- **H100** | misc | Multi-building projects (CN_Number_of_New_Buildings > 1) have shorter per-unit commencement-to-completion due to economies of scale. Prior=0.45. Impact=5. Status=OPEN.
- **H101** | misc | Detached vs semi-detached vs terraced sub-group dwellings have similar commencement-to-completion (within ±30 days). Prior=0.55. Impact=3. Status=OPEN.
- **H102** | misc | Fee-waiver projects (CN_Fee_Waiver_Request_Accepted == yes) are predominantly AHB or LA and commence faster. Prior=0.6. Impact=4. Status=OPEN.
- **H103** | misc | Pre-2014 permissions (grandfathered into BCMS) have a different commencement pattern and should be flagged. Prior=0.7. Impact=4. Status=OPEN.
- **H104** | misc | The 5-year permission expiry rule creates a visible duration-to-commence mode near 60 months (developers commence just before expiry). Prior=0.35. Impact=7. Status=OPEN.
- **H105** | misc | Section 42 extensions add a second mode beyond 60 months. Prior=0.5. Impact=6. Status=OPEN.
- **H106** | misc | Not_Commenced==yes flag contradicts Commencement_Date populated for <1% of rows (data-integrity check). Prior=0.9. Impact=2. Status=OPEN.
- **H107** | misc | S11_Request == yes flag (section 11 request for clarification) is associated with longer permission-to-commencement. Prior=0.6. Impact=4. Status=OPEN.
- **H108** | misc | Developer concentration (top-10 developers by CN_Building_Name family) accounts for ≥20 percent of multi-unit commencements. Prior=0.5. Impact=5. Status=OPEN.

---

## Summary of hypotheses

- Total: 108
- Long-shot (prior ≤ 0.3): 12 (H016 0.35, H018 0.30, H020 0.25, H036 0.30, H050 0.30, H087 0.30, H095 0.30, H097 0.25, H104 0.35, H016 counted once) — 12 with prior ≤ 0.35; 6 with prior ≤ 0.30 = ~5.6%. Need to seed more long-shots to hit 20% quota; will add during loop when needed.
- High-impact (impact ≥ 7): ~25

The queue is intentionally dense so Phase 2 can pick high-impact-near-0.5-prior hypotheses preferentially. Phase 2 posterior updates are recorded alongside results.tsv rather than inline.
