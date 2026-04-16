# Research Queue — IE Housing Pipeline E2E

## Format: ID | Hypothesis | Prior | Impact | Mechanism | Design Variable | Metric | Baseline | Status

### Stage 1→2 (Lapse) Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H001 | NRU>0 filter gives cleanest lapse estimate | 0.80 | 8 | NRU populated only for genuine residential from 2017 | NRU filter | lapse_rate | E00 | TESTED-E24 |
| H002 | Fuzzy matching inflates apparent lapse by >10pp | 0.75 | 7 | String-matching failures create false non-matches | match_method | lapse_delta | PL-4 E01 | TESTED-PL4 |
| H003 | Dublin has higher lapse rate than national | 0.60 | 6 | Land banking in high-demand areas | is_dublin | lapse_rate | PL-4 E07 | TESTED-PL4 |
| H004 | Pre-2017 lapse rates are unreliable due to data quality | 0.85 | 5 | BCMS rollout incomplete before 2017 | grant_year | lapse_rate | PL-4 E08 | TESTED-PL4 |
| H005 | One-off houses have higher lapse than schemes | 0.55 | 5 | Self-builders face fewer finance constraints | one_off | lapse_rate | PL-4 E03 | TESTED-PL4 |
| H006 | Appealed permissions have higher lapse | 0.65 | 4 | Delay from appeal erodes project viability | appeal_status | lapse_rate | PL-4 E13 | TESTED-PL4 |
| H007 | Section 42 extensions proxy for near-lapse | 0.70 | 5 | Extended permissions were about to lapse | s42_flag | lapse_rate | PL-4 E11 | TESTED-PL4 |
| H008 | Lapse rate is declining over time (2014→2019) | 0.60 | 6 | Better data quality + tighter market | grant_year | lapse_trend | PL-4 E12 | TESTED-PL4 |
| H009 | Outline permissions lapse at higher rate | 0.70 | 4 | Outline = speculative; less committed | app_type | lapse_rate | PL-4 E04 | TESTED-PL4 |
| H010 | Large schemes (50+) have lower lapse than small | 0.65 | 6 | Finance commitment, public scrutiny | size_stratum | lapse_rate | PL-4 E09 | TESTED-PL4 |

### Stage 2→3 (CCC Filing) Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H011 | Opt-out status is the primary driver of low CCC rate | 0.90 | 9 | Regulatory exemption, not economic non-completion | opt_out | ccc_rate | E00 | TESTED-E15 |
| H012 | Scheme size predicts CCC rate monotonically | 0.80 | 8 | Larger schemes = professional developers = regulatory compliance | size_stratum | ccc_rate | E00 | TESTED-E01 |
| H013 | AHB projects have higher CCC rates | 0.75 | 6 | AHBs must certify for funding drawdown | ahb_flag | ccc_rate | E00 | TESTED-E08 |
| H014 | Multi-phase developments have higher CCC rates | 0.70 | 7 | Phase-level CCC required for next-phase CN | multi_phase | ccc_rate | E00 | TESTED-E25 |
| H015 | Dublin has higher CCC rate than national | 0.55 | 5 | More professional developers, higher scrutiny | is_dublin | ccc_rate | E00 | TESTED-E06 |
| H016 | COVID increased comm→CCC duration by 2-4 weeks | 0.70 | 5 | Construction shutdowns March-May 2020 | post_covid | median_gap | E00 | TESTED-E05 |
| H017 | Later grant years have higher CCC rates | 0.60 | 5 | Right-censoring less severe + market maturation | grant_year | ccc_rate | E00 | TESTED-E13 |
| H018 | Section 42 extended projects have higher CCC rate | 0.50 | 5 | Survived potential lapse, committed developer | s42_flag | ccc_rate | E00 | TESTED-E09 |
| H019 | SHD-era permissions have different CCC rates | 0.45 | 5 | Fast-track = larger schemes = more compliance | shd_era | ccc_rate | E00 | TESTED-E04 |
| H020 | Apartment projects have different CCC dynamics | 0.60 | 6 | Longer construction but higher completion rate | apartment_flag | ccc_rate | E00 | TESTED-E07 |

### Pipeline Yield Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H021 | Overall yield is between 30% and 50% | 0.80 | 9 | Product of three stage rates | yield_rate | yield | E00 | TESTED-E00 |
| H022 | Non-opt-out yield is >50% | 0.70 | 8 | Removing regulatory artefact | opt_out_filter | yield_nonopt | E00 | TESTED-KB28 |
| H023 | Permission volume is the binding constraint for HFA | 0.85 | 9 | Even at 100% yield, 38k < 50.5k | perm_volume | perms_needed | E00 | TESTED-E10 |
| H024 | Halving lapse rate adds <1000 completions/yr | 0.60 | 4 | Lapse is only 9.5%, small denominator effect | lapse_rate | extra_comps | E00 | TESTED-E11 |
| H025 | CCC rate improvement +10pp adds >3000 completions/yr | 0.55 | 7 | Large base of commenced projects | ccc_rate | extra_comps | E00 | TESTED-E31 |
| H026 | Increasing permission volume to 60k adds ~8k completions/yr | 0.65 | 8 | Linear in yield × volume | perm_volume | comps_at_60k | E00 | TESTED-E32 |
| H027 | LA-level yield heterogeneity is large (CV > 0.3) | 0.70 | 7 | Different LA cultures and markets | la | cv | E00 | TESTED-E02 |
| H028 | 2014-2017 mature cohort has higher yield than 2018-2019 | 0.40 | 5 | Less right-censoring | grant_year | yield_mature | E00 | TESTED-E23 |
| H029 | Right-censoring shifts yield by <2pp when censor -6mo | 0.75 | 4 | Most 2014-2019 completions already observed | censor_shift | yield_delta | E00 | TESTED-E22 |
| H030 | CSO 2-yr ratio tracks our cohort yield loosely | 0.50 | 5 | Different measurement but same population | cso_ratio | correlation | E00 | TESTED-E18 |

### Duration Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H031 | Perm→comm duration is log-normally distributed | 0.80 | 6 | Standard for administrative delays | distribution | fit | PL-1 | TESTED-T04 |
| H032 | Larger schemes take longer to commence | 0.85 | 7 | More complex financing and design | size_stratum | median_days | E00 | TESTED-E16 |
| H033 | Comm→CCC is shorter for larger schemes | 0.50 | 5 | Professional builders, economies of scale | size_stratum | median_days | E00 | TESTED-E17 |
| H034 | Total pipeline IQR spans >2 years | 0.75 | 6 | Fat right tail in construction durations | pipeline | IQR | E00 | TESTED-E14 |
| H035 | DES reproduces observed yield within 2pp | 0.70 | 6 | Calibrated to observed distributions | des | yield_match | E00 | TESTED-T04 |

### Sensitivity & Robustness Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H036 | Upper-bound lapse (27.4%) gives yield ~28% | 0.80 | 7 | Wide lapse uncertainty | lapse_upper | yield | E00 | TESTED-E26 |
| H037 | Placebo shuffling preserves overall rate | 0.99 | 3 | Sanity check | shuffled | rate | E00 | TESTED-E24 |
| H038 | KM-estimated CCC@6yr matches observed rate | 0.70 | 5 | Censoring adjustment | km | ccc_6yr | E00 | TESTED-E27 |
| H039 | Stage 3→4 = 1.0 changes yield by <2pp | 0.75 | 4 | 95% proxy is close to truth | s34 | yield_delta | E00 | TESTED-E29 |
| H040 | DES with upper lapse gives yield ~28% | 0.75 | 5 | Consistent with analytical bound | des_upper | yield | E00 | TESTED-E30 |

### Interaction Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H041 | Dublin × Apartment interaction exists | 0.40 | 5 | Apartment development concentrated in Dublin | is_dublin×apartment | ccc_rate | E00 | TESTED-I01 |
| H042 | Size × Dublin interaction: large Dublin schemes outperform | 0.50 | 6 | Urban + professional developer | size×dublin | ccc_rate | E00 | TESTED-I02 |
| H043 | Year × Type interaction: apartments improving faster | 0.35 | 5 | BCAR compliance improving differentially | year×apartment | ccc_rate | E00 | TESTED-I03 |

### Cross-Project Synthesis Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H044 | PL-0 aggregate ratio is consistent with our cohort yield | 0.50 | 7 | Different methods, same population | cso_aggregate | ratio_match | E00 | TESTED-E18 |
| H045 | PL-1 median latency consistent with PL-0 lag estimate of 8Q | 0.70 | 6 | 8Q ≈ 730d vs our 1096d | lag_comparison | days | E00 | TESTED-E14 |
| H046 | PL-3 LDA share is <5% of national completions | 0.90 | 4 | LDA is small delivery body | lda_share | pct | E00 | TESTED-E12 |
| H047 | LDA additionality is ~0 given 100% Tosaigh | 0.85 | 5 | Forward-purchase, already in denominator | lda_addition | count | E00 | TESTED-E12 |

### Extended Hypotheses (Long-shots, prior ≤ 0.3)

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H048 | Construction material (MMC) predicts faster completion | 0.25 | 6 | Modern methods of construction | mmc_flag | days_delta | E00 | OPEN |
| H049 | Protected structures have lower yield | 0.30 | 3 | Heritage constraints delay construction | protected | yield | E00 | OPEN |
| H050 | Seasonal grant timing affects yield | 0.20 | 3 | Q4 grants may face winter delays | grant_quarter | yield | E00 | OPEN |
| H051 | County-level housing demand predicts yield | 0.30 | 5 | High-demand areas may have faster completion | demand_proxy | yield_corr | E00 | OPEN |
| H052 | EIR code availability predicts completion | 0.25 | 4 | Address completeness as quality proxy | eircode | ccc_rate | E00 | OPEN |
| H053 | Fire safety certificate (FSC) timing predicts CCC | 0.30 | 4 | FSC is prerequisite for CCC | fsc_lag | ccc_prediction | E00 | OPEN |
| H054 | DAC (Disability Access Certificate) delays CCC | 0.25 | 3 | Accessibility compliance bottleneck | dac_lag | days_delta | E00 | OPEN |
| H055 | Building height predicts completion rate | 0.20 | 4 | Taller = more complex = lower rate | height | ccc_rate | E00 | OPEN |
| H056 | Consequence class predicts CCC timing | 0.30 | 4 | Higher consequence = more inspection | consequence_class | days_delta | E00 | OPEN |
| H057 | Cladding system type affects CCC timing | 0.20 | 3 | Post-Grenfell scrutiny | cladding | days_delta | E00 | OPEN |
| H058 | Number of bedrooms predicts CCC rate | 0.25 | 3 | Proxy for unit complexity | bedrooms | ccc_rate | E00 | OPEN |
| H059 | Floor area correlates with CCC duration | 0.30 | 4 | Larger = longer construction | floor_area | days | E00 | OPEN |
| H060 | Engineered foundation predicts faster completion | 0.25 | 3 | Better-planned projects | eng_found | days_delta | E00 | OPEN |
| H061 | Multiple building types within a notice predict delay | 0.30 | 4 | Complex mixed-use | multi_bldg | days_delta | E00 | OPEN |
| H062 | S11 request flag predicts inspection delay | 0.25 | 3 | Section 11 = compliance issue | s11 | days_delta | E00 | OPEN |
| H063 | Fee waiver requests correlate with social housing yield | 0.20 | 3 | Fee waiver = LA/social project | fee_waiver | ccc_rate | E00 | OPEN |
| H064 | Balcony flag predicts apartment complexity | 0.20 | 3 | Balconies add construction time | balcony | days_delta | E00 | OPEN |
| H065 | Heat supply type predicts completion speed | 0.15 | 2 | District heating vs individual | heat_supply | days_delta | E00 | OPEN |
| H066 | Pre-notification flag predicts faster CCC | 0.30 | 3 | Projects that pre-notify complete sooner | pre_notif | days_delta | E00 | OPEN |
| H067 | Seven-day notices have different yield than standard CN | 0.35 | 4 | Different regulatory pathway | seven_day | ccc_rate | E00 | OPEN |
| H068 | Number of storeys predicts completion time | 0.30 | 4 | More floors = longer construction | storeys | days | E00 | OPEN |
| H069 | Grant-to-submission lag predicts abandonment | 0.25 | 5 | Long gap = lukewarm commitment | submission_lag | ccc_rate | E00 | OPEN |
| H070 | Part A/B/C compliance flags predict CCC | 0.20 | 3 | More compliance = more likely to complete | part_flags | ccc_rate | E00 | OPEN |

### Policy & Scenario Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H071 | Mandatory CCC for opt-out would add 8k reported completions/yr | 0.40 | 7 | Opt-out homes exist but aren't counted | mandatory_ccc | counted_comps | E00 | OPEN |
| H072 | Reducing planning decision time by 30d adds <500 completions/yr | 0.60 | 4 | Decision time is small fraction of pipeline | decision_time | extra_comps | E00 | OPEN |
| H073 | A "use it or lose it" 3-year permission would halve lapse | 0.30 | 5 | Shorter window forces commitment | permission_duration | lapse_rate | E00 | OPEN |
| H074 | LA-level yield could be improved by sharing best practice | 0.35 | 5 | Heterogeneity implies room for convergence | la_best_practice | yield_uplift | E00 | OPEN |
| H075 | If all LAs matched top-5 CCC rate, yield would increase by 8pp | 0.30 | 7 | Removing bottom of distribution | la_convergence | yield_delta | E00 | OPEN |
| H076 | A national building completion register would improve measurement | 0.80 | 3 | Better data, not more houses | data_quality | measurement | E00 | OPEN |
| H077 | Standardising BCMS identifier format to planning register would improve linkage | 0.85 | 4 | Reduce join failure rate | identifier_standard | match_rate | E00 | OPEN |

### International Comparison Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H078 | UK permit-to-completion yield is >50% (higher than Ireland) | 0.55 | 5 | More mature market, better tracking | UK_yield | yield | E00 | OPEN |
| H079 | NZ consent-to-completion yield is ~80% | 0.50 | 5 | Different regulatory system | NZ_yield | yield | E00 | OPEN |
| H080 | Netherlands has >90% yield (tight coupling) | 0.60 | 5 | Centralized planning system | NL_yield | yield | E00 | OPEN |
| H081 | Australian approval-to-completion has similar fat tail | 0.45 | 4 | Similar common-law planning system | AU_pipeline | duration_shape | E00 | OPEN |
| H082 | US permit-to-completion lag (Harter & Morris 2021) is shorter than Ireland's | 0.55 | 5 | Larger, more liquid market | US_lag | days | E00 | OPEN |

### Real-Options & Queueing Theory Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H083 | Near-expiry commencement mode exists (real-options) | 0.50 | 5 | Developers hold option value until forced | expiry_proximity | comm_hazard | PL-1 E23 | TESTED-PL1 |
| H084 | Pipeline duration follows M/G/1 queue with heavy-tailed service | 0.45 | 6 | Construction service time is heavy-tailed | queue_model | fit | E00 | OPEN |
| H085 | Erlang-based capacity model predicts annual throughput | 0.35 | 5 | Pipeline capacity is a function of service rate × servers | erlang | throughput | E00 | OPEN |
| H086 | Price index correlates with commencement lag | 0.40 | 5 | Higher prices = faster commencement | house_price | lag_corr | E00 | OPEN |
| H087 | Interest rate shocks affect lapse rate with 12-18mo lag | 0.35 | 5 | Rate hikes kill project viability | interest_rate | lapse_lag | E00 | OPEN |

### Additional Robustness Hypotheses

| ID | Hypothesis | Prior | Impact | Mechanism | DV | Metric | Baseline | Status |
|---|---|---|---|---|---|---|---|---|
| H088 | Bootstrap yields tight CI (<3pp width) | 0.85 | 4 | Large sample, well-behaved distribution | bootstrap | ci_width | E00 | TESTED-E19/E21 |
| H089 | Temporal split (train on 2014-2017, test on 2018-2019) maintains yield | 0.70 | 6 | No regime shift | temporal | yield_stability | E00 | OPEN |
| H090 | Removing top/bottom 1% of durations doesn't change median | 0.90 | 3 | Median is robust to outliers | winsorise | median_delta | PL-1 E05 | TESTED-PL1 |
| H091 | County-level random effects explain >20% of CCC variance | 0.45 | 5 | Institutional heterogeneity | la_random | var_explained | E00 | OPEN |
| H092 | Weibull AFT fits better than Cox for comm→CCC | 0.40 | 4 | Parametric vs semi-parametric | model | AIC | PL-1 T01 | TESTED-PL1 |
| H093 | Log-normal AFT fits best on AIC | 0.45 | 4 | Heavy right tail | model | AIC | PL-1 T01 | TESTED-PL1 |
| H094 | LightGBM classifier predicts dark-permission at AUC>0.9 | 0.60 | 5 | Nonlinear interactions in covariates | lgbm | AUC | PL-1 E20 | TESTED-PL1 |
| H095 | Concordance difference between Cox and LR is <0.05 | 0.65 | 4 | Mostly linear relationships | model_gap | concordance | T03/T05 | TESTED |
| H096 | Multi-state competing-risks model outperforms simple binomial | 0.30 | 5 | Competing risks may matter | competing_risks | yield_accuracy | T01/T03 | TESTED |
| H097 | Scheme-size is confounded with opt-out status | 0.80 | 6 | Size=1 ≈ one-off ≈ opt-out | confound | partial_r | E01/E15 | OPEN |
| H098 | Non-opt-out yield is more policy-relevant than all-in yield | 0.75 | 7 | Opt-out is regulatory artefact | policy | yield_choice | E00 | TESTED-KB |
| H099 | Inverse yield at non-opt-out rate requires ~98k perms/yr for HFA | 0.70 | 8 | Still far above current 38k | inverse | perms_needed | E10 | TESTED-KB29 |
| H100 | The 3 top levers rank: volume > CCC rate > lapse rate | 0.75 | 8 | Volume has largest marginal effect | sensitivity | ranking | E10/E11/E31 | TESTED |
| H101 | LA clustering reveals 3-4 distinct pipeline archetypes | 0.35 | 5 | Urban/suburban/rural LA types | clustering | n_clusters | E02 | OPEN |
| H102 | Yield is highest for 50-199 unit schemes | 0.50 | 5 | Sweet spot: professional but not mega | size | yield_peak | E01 | TESTED |
| H103 | 2014-2015 cohort may have data-quality issues inflating apparent non-completion | 0.60 | 5 | Early BCAR adoption incomplete | data_quality | rate_diff | E13 | TESTED |
