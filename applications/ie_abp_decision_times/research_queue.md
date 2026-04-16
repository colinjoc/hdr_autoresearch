# Research queue — ABP decision times

## Ordering rule

3-axis impact score (Δ, Novelty, Mechanism) × proximity of prior to 0.5. See program.md §Phase 2 Prior Discipline. Long-shot quota (prior ≤ 0.3): ≥20 of the 100+.

## Phase 1 (tournament) hypotheses — families

| ID | Family | Prior | Mechanism |
|---|---|---|---|
| T01 | Year-over-year descriptive trend (linear OLS on year) | 0.60 | Time captures the composite of all drivers |
| T02 | Interrupted time series with multiple knots | 0.70 | Each knot (Plean-IT, COVID, board crisis, P&E List, ACP) is a structural break |
| T03 | Capacity-constrained queueing (Little's law fit) | 0.55 | W = L/λ holds in steady state |
| T04 | M/M/1 / M/G/1 heavy-traffic fit | 0.45 | Kingman's formula predicts convex delay growth |
| T05 | Case-type fixed-effects OLS on weeks-to-dispose (panel) | 0.75 | Case type is the dominant observable covariate |

## Phase 2 hypotheses (≥100)

### Core robustness (descriptive)
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H001 | Excluding 2020-2021 COVID years, the 2017-2024 trend is still monotonically increasing | 0.80 | 2 | 1 | 3 | robustness |
| H002 | Median weeks-to-dispose tracks mean to within ±10% in every year | 0.55 | 1 | 1 | 2 | robustness |
| H003 | Winsorising top 1% long cases reduces 2023 mean by >3 weeks | 0.60 | 2 | 1 | 3 | robustness |
| H004 | The 2023 compliance trough (28%) is tighter than the 95% CI around the 2018-2022 trend line | 0.80 | 3 | 1 | 3 | signal |
| H005 | Formal-disposal compliance trails all-disposal compliance by 10–15pp each year | 0.75 | 1 | 1 | 3 | descriptive |
| H006 | Appeals-only compliance has lower variance than overall compliance | 0.55 | 1 | 1 | 2 | robustness |
| H007 | SID-only compliance does not move with the overall crisis | 0.30 | 2 | 2 | 2 | heterogeneity |
| H008 | 2024 mix effect: removing SHD-only disposals leaves mean at ~30 weeks | 0.75 | 2 | 1 | 3 | mix |
| H009 | If 2024 compliance is re-computed excluding SHD, it is >40% | 0.70 | 2 | 1 | 3 | mix |
| H010 | Adding Q1-Q3 2025 interim data, compliance recovers to 55-65% | 0.80 | 2 | 1 | 3 | recovery |

### Capacity / queueing
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H011 | FTE count explains more variance in W than intake volume | 0.55 | 2 | 2 | 3 | capacity |
| H012 | Board-member count explains more variance in W than total FTE | 0.65 | 2 | 2 | 3 | capacity |
| H013 | ρ = intake/capacity exceeded 0.9 in 2022 (Kingman regime) | 0.70 | 3 | 2 | 3 | capacity |
| H014 | Backlog-at-start-of-year is the single strongest predictor of W | 0.60 | 3 | 2 | 3 | capacity |
| H015 | Inspector count interacts with intake (more inspectors = weaker intake effect) | 0.40 | 2 | 2 | 2 | capacity |
| H016 | FTE surge of 2023-2024 was undersized vs Indecon recommendation | 0.50 | 2 | 1 | 2 | capacity |
| H017 | If Indecon's full +60 FTE had been added in Q3 2022, 2023 compliance would be ≥45% | 0.30 | 3 | 3 | 2 | counterfactual |
| H018 | Return-to-60%-compliance timing projects to Q2 2026 under status quo | 0.60 | 3 | 2 | 3 | forecast |
| H019 | Return-to-60% projects to Q4 2025 under ACP's new 48-week SID / 18-week appeals timelines | 0.35 | 3 | 2 | 2 | forecast |
| H020 | ACP transition in Jun 2025 has no measurable effect in 2025 Q3 disposals | 0.70 | 2 | 1 | 3 | counterfactual |

### Legislative / case-law shocks
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H021 | Plean-IT transition explains 15-18pp of the 2017-2018 compliance drop | 0.60 | 2 | 1 | 2 | shock |
| H022 | SHD fast-track introduction (2017) raised mean weeks-to-dispose by >3 weeks | 0.50 | 2 | 2 | 3 | shock |
| H023 | LRD transition (2021) did not improve mean weeks-to-dispose in 2022 | 0.75 | 1 | 1 | 2 | shock |
| H024 | Heather Hill (Jul-2022) reduced JR lodgement; not observable at ABP-decision-time level | 0.55 | 1 | 1 | 2 | shock |
| H025 | P&E List (Nov-2022) had no measurable effect on ABP mean weeks in 2023-2024 | 0.70 | 2 | 2 | 3 | shock |
| H026 | Balz judgment (2019) is associated with step-up in inspector report length | 0.35 | 2 | 2 | 2 | shock |
| H027 | Connelly judgment (2018) is associated with step-up in decision-drafting time | 0.30 | 2 | 3 | 2 | shock |
| H028 | Board-crisis dummy (2022-2024) alone explains 25pp of compliance drop | 0.60 | 3 | 1 | 3 | shock |
| H029 | Farrell Report (Jul-2022) marks the true structural break rather than Hyde resignation | 0.50 | 2 | 2 | 2 | shock |
| H030 | Planning and Development Act 2024 statutory-timeline extensions (48w SID) are the primary 2026 compliance-recovery driver | 0.40 | 3 | 2 | 2 | shock |

### Case-type heterogeneity
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H031 | SHD cases are the slowest case type every year since 2018 | 0.85 | 2 | 1 | 3 | heterogeneity |
| H032 | SID cases have the highest variance in weeks-to-dispose | 0.60 | 2 | 2 | 3 | heterogeneity |
| H033 | Normal planning appeals track a stable 15-22-week cycle pre-2022 | 0.80 | 2 | 1 | 3 | heterogeneity |
| H034 | LRD cases since inception have cycled at 13-14 weeks (well inside 16-week SOP) | 0.90 | 2 | 1 | 3 | heterogeneity |
| H035 | LAOD cases deteriorated more than private appeals in 2022-2024 | 0.30 | 2 | 3 | 2 | heterogeneity |
| H036 | Referrals (section 5) are the fastest disposed category across all years | 0.65 | 1 | 1 | 2 | heterogeneity |
| H037 | Wind SID cases are slower than solar SID cases | 0.50 | 1 | 2 | 2 | heterogeneity |
| H038 | Infrastructure Local Authority cases are slower than Private SID | 0.40 | 1 | 2 | 2 | heterogeneity |
| H039 | Strategic Infrastructure Pre-App requests are disposed of in weeks, not months | 0.75 | 1 | 1 | 3 | heterogeneity |
| H040 | RZLT appeals (introduced 2023) are disposed within SOP 95%+ of the time | 0.90 | 1 | 1 | 3 | heterogeneity |

### JR feedback loop
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H041 | JR-lodgement-rate-year-t correlates positively with mean-W-year-t+1 in a panel | 0.40 | 3 | 3 | 3 | jr |
| H042 | SHD cases with prior JR history take longer than other SHD cases | 0.50 | 2 | 3 | 2 | jr |
| H043 | Inspector reports on cases with expected JR risk are >25% longer than non-JR-risk cases (proxied by applicant identity) | 0.30 | 2 | 3 | 2 | jr |
| H044 | The JR-lodgement channel accounts for <5pp of 2023 compliance drop | 0.50 | 2 | 2 | 2 | jr |
| H045 | P&E List's JR-disposal speed-up produces 2024 measurable ABP speed-up | 0.25 | 2 | 2 | 2 | jr |
| H046 | If JR lodgement rate stabilises, predicted 2026 compliance > 60% holds | 0.55 | 2 | 2 | 2 | jr |
| H047 | Peak JR lodgement 2021 (wave triggered by O'Broin v ABP) adds to 2022 backlog | 0.60 | 2 | 2 | 2 | jr |
| H048 | Courts-level remittals (ABP loses JR, case returns to Board) contribute 4–6 weeks extra per affected case | 0.70 | 2 | 2 | 3 | jr |
| H049 | "Inspector loop" delays (second inspector assigned post-JR) show up in the 2024 41-week NPA mean | 0.40 | 2 | 3 | 2 | jr |
| H050 | JR rate itself is predicted by ABP decision delay (reverse causation) | 0.30 | 3 | 3 | 2 | jr |

### Mix and outlier robustness
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H051 | Disposal-mix shift alone explains >50% of 2024-vs-2022 mean change | 0.65 | 3 | 2 | 3 | mix |
| H052 | 90th-percentile case time grew faster than median 2020-2024 | 0.80 | 2 | 1 | 3 | mix |
| H053 | The slowest 5% of SHD cases drive most of the 124-week SHD 2024 mean | 0.85 | 2 | 1 | 3 | mix |
| H054 | Pre-app cases (which are excluded from Table 1) have stable cycle times | 0.55 | 1 | 1 | 2 | mix |
| H055 | On-hands-at-year-end is more informative than mean-weeks-to-dispose | 0.35 | 2 | 2 | 2 | mix |
| H056 | Caseload peak (May 2023) precedes compliance trough by 6-9 months | 0.70 | 2 | 1 | 3 | mix |
| H057 | Caseload decline 2024 is compatible with flat compliance (mix effect) | 0.80 | 2 | 1 | 3 | mix |
| H058 | 2024 intake decline is from LA-refused cases (fewer appeals possible) | 0.40 | 1 | 2 | 2 | mix |
| H059 | 2024 RZLT wave of 648 cases is the majority of the 2023 backlog pulse | 0.60 | 3 | 2 | 3 | mix |
| H060 | Removing RZLT cases from 2024 leaves overall compliance ~35% | 0.50 | 2 | 2 | 2 | mix |

### Seasonality
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H061 | Q4 compliance is systematically higher than Q1 (push-to-year-end effect) | 0.55 | 1 | 2 | 2 | season |
| H062 | July-August disposal volumes are the lowest (holiday effect) | 0.70 | 1 | 1 | 3 | season |
| H063 | February is the single lowest-compliance month | 0.40 | 1 | 2 | 2 | season |
| H064 | Quarter-of-year effect is small vs year effect (< 3pp) | 0.65 | 1 | 1 | 2 | season |
| H065 | Seasonal effect weakened during board crisis (everything slowed) | 0.60 | 1 | 2 | 2 | season |

### Counter-factual / placebo
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H066 | Shuffling year labels produces mean |β_year| < 0.3 weeks/year (placebo test) | 0.85 | 2 | 1 | 3 | placebo |
| H067 | Placebo treatment in 2015 does NOT produce a significant break | 0.90 | 1 | 1 | 3 | placebo |
| H068 | Including only 2015-2019 years, trend is flat | 0.75 | 1 | 1 | 2 | placebo |
| H069 | If intake had been frozen at 2018 levels 2019-2024, predicted W stays <25 weeks | 0.55 | 3 | 2 | 2 | counterfactual |
| H070 | If FTE had grown linearly 2018-2024 (no lag), predicted W peaks at 30 weeks | 0.50 | 3 | 2 | 2 | counterfactual |

### Phase B scenarios
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H071 | Status-quo-FTE scenario projects 2028 compliance = 60-65% | 0.50 | 3 | 2 | 2 | forecast |
| H072 | +20% FTE scenario projects 2028 compliance = 70-80% | 0.55 | 3 | 2 | 2 | forecast |
| H073 | PDA-2024-48w-SID scenario projects SID-only compliance = 85%+ in 2027 | 0.45 | 3 | 2 | 2 | forecast |
| H074 | +20% intake shock in 2026 delays compliance recovery by >12 months | 0.60 | 3 | 2 | 3 | forecast |
| H075 | 2024-mix-frozen assumption understates 2026 compliance by ~5pp | 0.40 | 2 | 2 | 2 | forecast |
| H076 | ACP "parking" of pre-app consultations as a statistical category recovers ~3pp compliance | 0.35 | 1 | 2 | 2 | admin_trick |
| H077 | LRD cases continue at ~13 weeks indefinitely (steady-state assumption) | 0.75 | 2 | 1 | 3 | forecast |
| H078 | SHD backlog clears by end-2026 (all remaining cases disposed of) | 0.80 | 2 | 1 | 3 | forecast |
| H079 | Forecast without PDA-2024 and without FTE growth returns to 2023 crisis levels by 2027 | 0.30 | 3 | 3 | 3 | forecast |
| H080 | Return-to-80%-pre-2018-norm compliance does NOT happen before 2030 under any tested scenario | 0.80 | 3 | 2 | 3 | forecast |

### Model diagnostics
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H081 | OLS residuals are not white-noise-AR(1) after controlling for year and case-type | 0.40 | 1 | 1 | 2 | diagnostic |
| H082 | Poisson regression on on-hands-count fits better than OLS on mean-W | 0.35 | 2 | 2 | 2 | diagnostic |
| H083 | Log-transform of W improves R² by >5pp | 0.50 | 1 | 1 | 2 | diagnostic |
| H084 | Heteroskedasticity by case-type requires robust SEs | 0.75 | 1 | 1 | 3 | diagnostic |
| H085 | Year-and-case-type-fixed-effects model has within-R² > 0.6 | 0.70 | 2 | 1 | 3 | diagnostic |
| H086 | Dropping 2024 observation (outlier potential) does not change coefficient on board_crisis | 0.70 | 1 | 1 | 2 | diagnostic |
| H087 | 10-fold CV on year-level OLS gives stable coefficient within ±15% | 0.65 | 1 | 1 | 2 | diagnostic |
| H088 | ITS model with Nov-2022 knot has better AIC than with Jul-2022 knot | 0.55 | 2 | 2 | 2 | diagnostic |
| H089 | Model including FTE beats model with year trend alone on BIC | 0.60 | 2 | 1 | 2 | diagnostic |
| H090 | Inclusion of board-member count adds marginal information over FTE | 0.50 | 2 | 2 | 2 | diagnostic |

### Long-shot and novelty
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H091 | Mean-W is a leading indicator of housing completions 18 months later (upstream pipeline effect) | 0.25 | 3 | 3 | 2 | long_shot |
| H092 | SOP-compliance trajectory correlates r>0.5 with CSO housing permissions lagged 24 months | 0.20 | 2 | 3 | 2 | long_shot |
| H093 | Press-mention count of "ABP delays" Granger-causes intake growth the next year | 0.15 | 2 | 3 | 1 | long_shot |
| H094 | Inspector report page-counts (if extractable) correlate r>0.4 with weeks-per-case | 0.30 | 2 | 3 | 2 | long_shot |
| H095 | Same-inspector-repeat cases take ~15% less time than first-time cases | 0.25 | 1 | 3 | 2 | long_shot |
| H096 | Election-year effect: 2024 election visibly slowed ABP Board appointments | 0.20 | 2 | 3 | 2 | long_shot |
| H097 | 2025 ACP transition alone produces null improvement; gains come from FTE+2022 onward | 0.70 | 2 | 2 | 3 | structural |
| H098 | "Formal disposal" rate rises in anticipation of ACP audit scrutiny in 2025 | 0.25 | 2 | 3 | 2 | long_shot |
| H099 | Cases remitted from P&E List take 40%+ longer than non-remitted cases | 0.50 | 2 | 2 | 2 | long_shot |
| H100 | Irish Times "Ireland in delay" stories cluster within 60 days of major compliance drops (event study) | 0.25 | 2 | 3 | 1 | long_shot |

### Interaction candidates (for Phase 2.5)
| ID | Hypothesis | Prior | Δ | Novelty | Mech | Category |
|---|---|---|---|---|---|---|
| H101 | Intake × FTE ratio (ρ) > 0.85 is the single threshold indicator | 0.55 | 3 | 2 | 3 | interaction |
| H102 | Board-crisis × SHD-share interaction: SHD compliance hit hardest | 0.60 | 2 | 2 | 3 | interaction |
| H103 | FTE-surge × backlog: FTE gains only show up when backlog < 2,000 | 0.45 | 2 | 3 | 2 | interaction |
| H104 | Year × case-type FE: some case types recover faster than others | 0.65 | 2 | 1 | 3 | interaction |
| H105 | COVID × formal-disposal: formal disposals fell more than otherwise-disposals | 0.55 | 1 | 2 | 2 | interaction |

## Status tracking

Statuses: OPEN, DONE_KEEP, DONE_REVERT, DONE_MIXED, DEFERRED. All above start OPEN.
Long-shot count (prior ≤ 0.3): {H007, H017, H027, H035, H042, H043, H045, H050, H066 (placebo), H067 (placebo), H076, H079, H091, H092, H093, H094, H095, H096, H098, H100} = 20 / 105 = 19% — at quota floor.
