# Research Queue: AARO Case Resolution Analysis

## Format: ID | Hypothesis | Prior | Mechanism | Design Variable | Metric | Baseline | Status | Impact

### Resolution-Rate Analysis
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H01 | Resolution rate declining over time as backlog grows | 0.7 | Intake outpaces resolution capacity | time_period | resolution_rate | 17.7% overall | OPEN | 8 |
| H02 | AARO resolution rate far below Blue Book's 94.4% | 0.9 | Different era, different data quality, different investigation depth | program | resolution_rate | Blue Book 94.4% | OPEN | 7 |
| H03 | Data insufficiency is primary driver of low resolution rate, not anomalous cases | 0.85 | 58.7% archived due to data gaps | data_sufficiency | archive_fraction | 58.7% | OPEN | 9 |
| H04 | Among cases with sufficient data, prosaic resolution approaches 100% | 0.9 | All 292 resolved cases are prosaic | data_quality | prosaic_pct | 100% resolved prosaic | OPEN | 9 |
| H05 | FY2024 formal resolution rate (49 cases/13 months) is capacity-limited | 0.8 | Bottleneck at director approval and peer review | processing_pipeline | cases_per_month | 3.8/month formal | OPEN | 7 |

### Backlog Growth Model
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H06 | Backlog is growing unsustainably (intake >> resolution) | 0.85 | 58.2/month intake vs 22.5/month resolution | intake_vs_resolution | ratio | 2.6x | OPEN | 8 |
| H07 | FAA channel opening explains majority of FY2024 volume increase | 0.7 | 392/757 reports from FAA = 51.8% | channel | faa_fraction | 51.8% | OPEN | 8 |
| H08 | Backlog will never clear at current rates | 0.75 | Net accumulation of ~35.7 cases/month | projection | months_to_clear | inf | OPEN | 7 |
| H09 | Prior-period catch-up (272 reports from 2021-2022) inflates apparent current intake | 0.7 | Backlogged reports from prior years | period | catch_up_fraction | 272/757 = 35.9% | OPEN | 7 |
| H10 | Actual current-period intake (485 cases/13 months = 37.3/month) is lower than headline suggests | 0.75 | Separating current from historical catch-up | period_filter | current_rate | 37.3/month | OPEN | 7 |

### Base-Rate Comparison
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H11 | Historical programs consistently find 88-95% prosaic when investigation is thorough | 0.9 | Blue Book 94.4%, Hendry 88.6%, GEIPAN 96.5% | program | prosaic_pct | varies | OPEN | 9 |
| H12 | AARO's residual unidentified fraction will converge toward 3-6% as investigation capacity grows | 0.6 | Convergence to GEIPAN/Blue Book base rate | projection | unid_pct | currently ~82% | OPEN | 7 |
| H13 | Expected number of daily identifiable aerial objects vastly exceeds UAP report rate | 0.95 | Millions of flights, billions of birds, thousands of balloons, 5000+ Starlink satellites | base_rate | objects_vs_reports | back-of-envelope | OPEN | 8 |
| H14 | Blue Book's 5.6% unidentified rate is an upper bound for the true anomaly rate | 0.5 | Some Blue Book unknowns were inadequately investigated (Hynek critique) | investigation_quality | adjusted_rate | 5.6% | OPEN | 6 |
| H15 | GEIPAN's 3.5% Type D rate is the best available estimate of true residual | 0.6 | Most thorough modern program with multi-step classification | program_quality | type_d_rate | 3.5% | OPEN | 7 |

### Bayesian Analysis
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H16 | Bayesian posterior on "anomalous" for unresolved AARO case is <10% | 0.7 | High P(unresolved|prosaic) due to data insufficiency | prior | posterior | 8.2% | OPEN | 8 |
| H17 | Likelihood ratio for unresolved status is modest (~1.7) | 0.7 | Unresolved is weak evidence because prosaic cases also go unresolved | bayesian | LR | 1.7 | OPEN | 7 |
| H18 | Varying the prior from 1% to 20% -- posterior remains dominated by data-insufficiency signal | 0.8 | Sensitivity analysis of Bayesian result | prior_range | posterior_range | 8.2% at 5% prior | OPEN | 7 |
| H19 | Using Hendry's 11.4% as prior instead of Blue Book's 5.6% changes posterior only modestly | 0.7 | Both give <15% posterior | prior_source | posterior | varies | OPEN | 6 |

### NUFORC vs AARO Comparison (UFO-1)
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H20 | Resolution categories overlap: balloons and aircraft dominate both NUFORC and AARO | 0.85 | Same sky, same prosaic objects | comparison | category_overlap | qualitative | OPEN | 8 |
| H21 | NUFORC 0.54% explanation rate is not comparable to AARO's 17.7% resolution rate | 0.95 | Different investigation models; NUFORC has no systematic investigation | methodology | comparison_validity | rates differ | OPEN | 7 |
| H22 | Shape categories in AARO (orbs, lights dominant) match NUFORC temporal trend | 0.7 | NUFORC showed orb rising, disk declining; AARO morphology consistent | shape_evolution | orb_fraction | NUFORC 9.1% Orb by 2020s | OPEN | 7 |
| H23 | Starlink is emerging as a common resolution in both datasets | 0.8 | AARO explicitly notes Starlink; NUFORC had ITS-significant formation increase | starlink | presence | qualitative | OPEN | 7 |
| H24 | Geographic bias (military proximity) in AARO is analogous to population/infrastructure bias in NUFORC | 0.75 | Collection bias operates in both datasets | geography | bias_pattern | AARO military; NUFORC population | OPEN | 7 |

### Unresolved Cases Analysis
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H25 | Majority of unresolved cases are data-insufficient, not characteristically anomalous | 0.9 | 444/757 active archive; only 21 merit IC analysis | data_quality | archive_fraction | 58.7% | OPEN | 9 |
| H26 | The 21 IC-merit cases represent ~2.8% of intake, consistent with historical 3-6% residual | 0.6 | Convergence with GEIPAN Type D and Blue Book unknowns | historical_comparison | ic_merit_pct | 2.8% | OPEN | 8 |
| H27 | No SIGINT/GEOINT/MASINT detection suggests no technological signature detected | 0.7 | Truly advanced technology should have detectable EM signatures | sensor_coverage | national_platform_reports | 0 | OPEN | 7 |
| H28 | "Active Archive" label allows indefinite deferral -- cases may never be resolved | 0.6 | No mechanism forces re-investigation; data unlikely to improve retroactively | process | archive_resolution_rate | unknown | OPEN | 6 |
| H29 | The 21 cases likely include sensor artifacts not yet explained (similar to GoFast, Gimbal) | 0.6 | Historical pattern: high-profile unknowns later explained by parallax, rotation, etc. | precedent | explained_later | GoFast, Gimbal | OPEN | 7 |

### Congressional Claims vs AARO Findings
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H30 | Grusch's reverse-engineering claims are contradicted by AARO Historical Record Report | 0.9 | AARO found no evidence; circular reporting finding | evidence | contradiction | direct | OPEN | 8 |
| H31 | Fravor's Tic Tac kinematics cannot be verified from public AARO data | 0.8 | Case likely classified; kinematics depend on assumptions about distance | data_access | verifiability | limited | OPEN | 6 |
| H32 | Graves's description of regular encounters is consistent with AARO's collection-bias finding | 0.8 | Proximity to military operating areas = more reports | geography | encounter_rate | geographic pattern | OPEN | 7 |
| H33 | UAPDA's strongest provisions were stripped, limiting oversight | 0.9 | Review board with eminent domain removed in conference | legislation | provisions_enacted | partial | OPEN | 5 |

### Sensor and Domain Analysis
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H34 | Air domain dominates (93.5% of FY2024 reports = 708/757) | 0.95 | Airborne sensors most common; space reports from ground observers | domain | air_fraction | 93.5% | OPEN | 6 |
| H35 | Zero transmedium or maritime reports undermines transmedium UAP hypothesis | 0.7 | Definitional category exists but no reports fall in it | domain | transmedium_count | 0 | OPEN | 7 |
| H36 | FAA reporting channel is most productive single source at 51.8% | 0.8 | FAA logs all UAP since 2021; large commercial aviation volume | source | faa_share | 51.8% | OPEN | 6 |
| H37 | GREMLIN deployment will improve resolution rate if it addresses data-quality gap | 0.5 | Multi-sensor purpose-built system; first deployment Q1 FY2025 | sensor | resolution_improvement | projected | OPEN | 6 |

### Nuclear-Site Analysis
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H38 | All 18 nuclear-site reports are UAS, not exotic technology | 0.95 | NNSA/NRC categorized all as UAS | nuclear | uas_classification | 100% | OPEN | 7 |
| H39 | BWXT 6-night pattern suggests organized surveillance, not random | 0.7 | Consecutive nights at specific facility; deliberate pattern | nuclear | pattern | 6 consecutive nights | OPEN | 7 |
| H40 | D.C. Cook crash recovery could have provided forensic evidence | 0.6 | Physical UAS recovered; transferred to local law enforcement | nuclear | forensics | unknown disposition | OPEN | 5 |

### Morphology and Reporting Analysis
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H41 | 22.4% insufficient morphology reports indicate poor data quality more than exotic appearance | 0.8 | Same pattern as data-insufficient archive fraction | morphology | insufficient_pct | 22.4% | OPEN | 6 |
| H42 | "Unidentified lights" and "round/spherical/orb" dominant shapes consistent with NUFORC trend | 0.8 | Cross-dataset convergence on orb/light categories | shape | dominant_category | lights and orbs | OPEN | 7 |
| H43 | "Other" category descriptions (jellyfish, green fireball, silver rocket) suggest cultural influence | 0.5 | Unusual descriptions may reflect observer expectations or genuinely unusual objects | shape | other_descriptions | qualitative | OPEN | 5 |
| H44 | Clock-hour rounding bias (NUFORC finding: 38.7%) may be lower in military reports | 0.6 | Military uses precise time from sensors | reporting | rounding_bias | NUFORC 38.7% | OPEN | 5 |

### Robustness and Sensitivity
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H45 | Resolution rate is sensitive to how "pending closure" cases are counted | 0.8 | 118 formal vs 292 including pending changes rate from 7.1% to 17.7% | counting | resolution_rate | 7.1%-17.7% | OPEN | 7 |
| H46 | Excluding prior-period catch-up, FY2024 intake is 485 (lower than headline 757) | 0.9 | 272 reports from prior years counted in current period | period | adjusted_intake | 485 | OPEN | 7 |
| H47 | Bootstrap CI on resolution rate would be wide due to aggregate data | 0.7 | No case-level data; proportions from small resolved set | uncertainty | CI_width | point estimate only | OPEN | 6 |
| H48 | Trend in cumulative reports (144 -> 510 -> 801 -> 1652) is partly non-monotonic in intake rate | 0.5 | Channel openings cause step-function jumps, not organic growth | trend | intake_pattern | step vs linear | OPEN | 6 |

### Long-Shot Hypotheses (prior <= 0.3)
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H49 | Any of the 21 IC-merit cases will be publicly assessed as genuinely anomalous | 0.1 | Historical pattern: high-profile unknowns eventually explained | precedent | ic_outcome | under investigation | OPEN | 9 |
| H50 | Classified annex contains evidence contradicting public report's prosaic conclusions | 0.15 | Security classification covers sources and methods, not typically conclusions | classification | classified_divergence | unknown | OPEN | 8 |
| H51 | Grusch's claims will be substantiated by independent investigation | 0.1 | AARO found no evidence; IGDOD investigation ongoing | evidence | substantiation | no evidence to date | OPEN | 8 |
| H52 | Transmedium reports will emerge when maritime sensor networks are established | 0.3 | Current zero may reflect sensor gap, not absence of phenomenon | sensor | transmedium_reports | 0 | OPEN | 6 |
| H53 | UAS at nuclear sites represent foreign adversary surveillance | 0.25 | NNSA categorized all as UAS; adversary drones plausible | nuclear | adversary_attribution | under investigation | OPEN | 7 |
| H54 | AARO resolution taxonomy is incomplete -- missing a "sensor artifact" category | 0.3 | Sensor artifacts described in text but not broken out in resolution categories | taxonomy | missing_category | not reported | OPEN | 5 |
| H55 | Resolution rate will improve dramatically (>50%) with GREMLIN deployment | 0.2 | Single sensor system addressing one location; scaling unclear | sensor | rate_improvement | projected | OPEN | 6 |
| H56 | The post-2014 NUFORC decline and post-2022 AARO increase represent reporting shift military<->civilian | 0.25 | Military channels opened as civilian enthusiasm waned | reporting | channel_shift | qualitative | OPEN | 5 |
| H57 | Some Active Archive cases are actually adversary technology (non-ET but non-prosaic) | 0.2 | Data insufficient to determine; adversary tech possible | adversary | tech_fraction | unknown | OPEN | 7 |
| H58 | AARO's 100% prosaic resolution rate would drop below 95% with better sensor data | 0.15 | More data might reveal genuinely anomalous cases | sensor | prosaic_conditional | 100% with current data | OPEN | 7 |
| H59 | Congressional testimony claims will never be testable from public data | 0.3 | Classification barriers; AARO framing as circular reporting | access | testability | limited | OPEN | 5 |
| H60 | Public AARO data is sufficient to definitively answer "is there anything anomalous?" | 0.1 | Aggregate report-level data lacks case-level detail | data | definitiveness | insufficient for definitive answer | OPEN | 8 |

### Additional Robustness Hypotheses
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H61 | East Asian Seas resolution rate (40/100 = 40%) exceeds overall rate (17.7%) | 0.9 | Regional data quality varies; more sensor coverage in theater | geography | regional_rate | 40% | OPEN | 6 |
| H62 | Middle East resolution rate (13/57 = 22.8%) also exceeds overall | 0.85 | Same regional sensor coverage effect | geography | regional_rate | 22.8% | OPEN | 6 |
| H63 | Nuclear site reports have 100% UAS resolution -- highest certainty category | 0.95 | NNSA/NRC specialized in UAS identification | sector | nuclear_resolution | 100% UAS | OPEN | 6 |
| H64 | Flight safety concerns (2 reports + 3 trailed) represent <1% of total -- low safety risk | 0.85 | 5/757 = 0.66% | safety | safety_fraction | 0.66% | OPEN | 5 |
| H65 | FAA flight safety issues (1/392 = 0.26%) lower than military (5/365 = 1.37%) | 0.7 | Different reporting thresholds; military more attuned to threat | source | safety_rate | varies by source | OPEN | 5 |
| H66 | Space domain reports (49) are all ground-observer estimates, not space-sensor detections | 0.95 | Explicitly stated in report; no space-based sensor reports | domain | space_sensor | 0 | OPEN | 5 |
| H67 | Cumulative trend (144->510->801->1652) shows accelerating intake due to channel expansion | 0.7 | Each new channel (Navy, AARO, FAA) adds step function | trend | acceleration | accelerating | OPEN | 6 |
| H68 | Intake will decelerate as catch-up period ends and channels stabilize | 0.5 | 272 prior-period reports are a one-time catch-up | projection | deceleration | speculative | OPEN | 5 |
| H69 | AARO's "no evidence of ET" finding is conditional on public data completeness | 0.8 | Classified annex may contain additional context | conditionality | evidence_bound | public data only | OPEN | 6 |
| H70 | ORNL material analysis (terrestrial alloy) is replicable finding | 0.95 | Published methodology; standard materials science | materials | replicability | published | OPEN | 5 |
| H71 | Prosaic resolution fraction will remain at 100% for resolved cases | 0.85 | No mechanism suggests a non-prosaic case will be formally resolved | resolution | prosaic_permanence | 100% | OPEN | 6 |
| H72 | More experiments comparing AARO morphology distribution to NUFORC shape distribution | 0.7 | Cross-dataset shape comparison | comparison | morphology_match | qualitative | OPEN | 6 |
| H73 | Resolution taxonomy should include "atmospheric phenomena" category (missing from AARO) | 0.6 | ODNI 2021 listed it; AARO focuses on object categories | taxonomy | missing_category | not in FY2024 | OPEN | 5 |
| H74 | Time-to-resolution (not reported) is critical for understanding AARO efficiency | 0.8 | FY2024 reports 272 cases from 2021-2022 only now entering system | efficiency | time_to_resolution | not reported | OPEN | 6 |
| H75 | Comparison of AARO 2.8% IC-merit to GEIPAN 3.5% Type D is meaningful benchmark | 0.65 | Different methodologies but similar residual fractions | benchmark | residual_comparison | 2.8% vs 3.5% | OPEN | 7 |

### Interaction Hypotheses
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H76 | Channel x Geography interaction: FAA reports cluster differently than military reports | 0.6 | FAA covers commercial aviation routes; military covers operating areas | interaction | geographic_pattern | separate | OPEN | 5 |
| H77 | Data-quality x Domain interaction: space domain has worse data quality than air | 0.7 | Ground observers estimating altitude >100km | interaction | archive_rate_by_domain | unknown | OPEN | 5 |
| H78 | Time x Resolution interaction: resolution rate improving with AARO maturation | 0.5 | Institutional learning; better processes; pending closures accelerating | interaction | rate_trend | unclear | OPEN | 6 |
| H79 | Nuclear-site x Geographic interaction: nuclear reports concentrate in specific regions | 0.7 | BWXT Virginia, D.C. Cook Michigan identified specifically | interaction | nuclear_geography | specific sites | OPEN | 5 |
| H80 | Starlink x Shape interaction: Starlink cases predominantly "lights" or "formation" | 0.8 | Satellite trains appear as formations of lights | interaction | starlink_shape | formation/lights | OPEN | 5 |

### Additional Long-Shots
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H81 | AARO will publish individual case-level data in future | 0.2 | Transparency commitment; but classification barriers | data_access | case_level | aggregate only | OPEN | 6 |
| H82 | Some "birds" resolutions are incorrect -- edge cases of bird vs drone discrimination | 0.15 | Sensor artifacts make birds look anomalous; reverse could occur | resolution | misclassification | unknown | OPEN | 4 |
| H83 | AARO's 21 IC-merit cases include Nimitz/Gimbal type encounters | 0.3 | High-profile cases from FY2024 period | cases | notable_inclusion | not specified | OPEN | 5 |
| H84 | MIT Lincoln Lab radar filter research will reveal previously missed UAP data | 0.25 | Filtered radar returns may contain UAP signals | sensor | filtered_data | unknown | OPEN | 6 |
| H85 | International partner sharing will reveal convergent global patterns | 0.4 | Five Eyes and other partners sharing data | international | convergence | limited data | OPEN | 5 |

### Process and Methodology
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H86 | AARO's director-approval bottleneck is the binding constraint on resolution rate | 0.6 | 174 cases pending approval; only 49 formally closed during period | process | bottleneck | 49 formal / 243 pending | OPEN | 6 |
| H87 | "Pending closure" should be counted as resolved for analytical purposes | 0.7 | All assessed as prosaic; only awaiting administrative sign-off | counting | definition | 118 vs 292 | OPEN | 6 |
| H88 | AARO's analytic methodology (multi-agency, whole-of-government) is more rigorous than Blue Book | 0.7 | 30 coordinating agencies; IC integration; modern sensors | methodology | rigor_comparison | qualitative | OPEN | 5 |
| H89 | Data quality will improve with GENADMIN directive (96-hour reporting requirement) | 0.5 | Timelier reporting preserves more data; but witnesses still limited | process | data_quality_trend | improving | OPEN | 5 |
| H90 | Web-based reporting (aaro.mil) will change the nature of reports received | 0.6 | Different population (former USG employees); historical claims dating to 1945 | process | report_type | operational vs historical | OPEN | 5 |

### Additional Hypotheses for Completeness
| ID | Hypothesis | Prior | Mechanism | DV | Metric | Baseline | Status | Impact |
|---|---|---|---|---|---|---|---|---|
| H91 | 22.4% morphology-insufficient rate correlates with data-insufficient archive rate (58.7%) | 0.6 | Both driven by poor sensor data | correlation | insufficient_rates | possible | OPEN | 5 |
| H92 | Weekend vs weekday reporting difference (NUFORC: 1.20x) may not apply to military reports | 0.6 | Military operates 24/7; reporting not leisure-dependent | comparison | temporal_pattern | different | OPEN | 5 |
| H93 | Summer peak (NUFORC: 1.6x) may be weaker in AARO due to military operations tempo | 0.5 | Military operations year-round; but sky visibility still varies | comparison | seasonal_pattern | unknown | OPEN | 5 |
| H94 | The KONA BLUE debunking demonstrates AARO's willingness to investigate and publish | 0.9 | Proactive publication of classified program documents | transparency | debunking_pattern | KONA BLUE | OPEN | 5 |
| H95 | Next AARO report will show resolution rate increase from pending-closure clearance | 0.7 | 174+243 pending cases moving to resolved | projection | rate_improvement | pending batch | OPEN | 6 |
| H96 | Cumulative trend line fits exponential better than linear | 0.5 | 144->510->801->1652 is accelerating | trend_model | fit_quality | R-squared | OPEN | 5 |
| H97 | AARO's "no evidence" finding applies only to investigated cases, not uninvestigated archive | 0.8 | Finding conditional on cases actually analyzed | scope | evidence_scope | conditional | OPEN | 6 |
| H98 | Bayesian analysis is more informative than frequentist resolution rate for policy | 0.6 | Incorporates prior knowledge; updates with data | methodology | analytical_value | qualitative | OPEN | 5 |
| H99 | If AARO achieved Blue Book's investigation depth, ~95% of current unknowns would resolve prosaic | 0.7 | Historical convergence across programs | projection | projected_rate | ~95% | OPEN | 7 |
| H100 | The honest answer to "is there anything anomalous?" is "the data cannot tell us" | 0.8 | Aggregate data insufficient; 58.7% lack data; 100% resolved are prosaic | epistemology | answerable | insufficient for definitive answer | OPEN | 9 |
