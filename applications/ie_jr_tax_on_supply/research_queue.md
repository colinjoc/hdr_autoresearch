# Research Queue — JR Tax on Housing Supply

100+ hypotheses for the synthesis project.

| # | Hypothesis | Prior | Mechanism | Design Variable | Metric | Baseline | Status |
|---|-----------|-------|-----------|----------------|--------|----------|--------|
| H01 | Direct JR delay > 50,000 unit-months | 0.80 | 22 cases x ~250 units x ~18 months | units, delay_months | direct_unit_months | 0 | TESTED:KEEP (E01) |
| H02 | Indirect delay central > 2,000 unit-months | 0.70 | ABP slowdown x JR share x cases | jr_share, housing_cases | indirect_unit_months | 0 | TESTED:KEEP (E03) |
| H03 | Counterfactual gap > 10,000 units over 2018-2024 | 0.60 | Excess weeks push completions forward | excess_weeks, housing_share | total_gap | 0 | TESTED:KEEP (E04) |
| H04 | Dublin concentration > 70% of JR'd units | 0.75 | SHD concentrated in Dublin | location | dublin_share | 0 | TESTED:KEEP (E05) |
| H05 | Quashed cases dominate delay (>80% of direct) | 0.70 | More numerous and larger schemes | outcome | quashed_share | 0 | TESTED:KEEP (E06) |
| H06 | Pre-HH cases > 60% of total | 0.80 | Most JRs decided before July 2022 | decision_year | pre_hh_share | 0 | TESTED:KEEP (E07) |
| H07 | Holding cost > EUR 50M | 0.65 | 100k unit-months x EUR 500 | holding_cost | total_eur | 0 | TESTED:KEEP (E08) |
| H08 | Construction inflation adds > EUR 100M | 0.50 | 7% p.a. on 350k units | inflation_rate | inflation_cost | 0 | TESTED:KEEP (E09) |
| H09 | Sensitivity to imputation > 20% range | 0.70 | Many cases imputed | imputed_units | range | 0 | TESTED:KEEP (E11) |
| H10 | Conceded cases resolve faster than quashed | 0.60 | Concession avoids full hearing | outcome | avg_delay | 0 | TESTED:KEEP (E12) |
| H11 | JR component of rho > 0.10 | 0.55 | JR defense work is resource-intensive | jr_multiplier | rho_jr | 0 | TESTED:KEEP (E13) |
| H12 | 2020 is peak direct-delay year | 0.75 | Most SHD JRs decided in 2020 | year | annual_peak | 0 | TESTED:KEEP (E14) |
| H13 | Large schemes (>300u) account for >50% of unit-months | 0.70 | Power-law: few large schemes dominate | units | size_concentration | 0 | TESTED:KEEP (E16) |
| H14 | Total JR tax with central indirect > 100k unit-months | 0.60 | Direct + 25% indirect | all | total | 0 | TESTED:KEEP (E17) |
| H15 | Dublin x quashed interaction dominates | 0.75 | Most JR'd schemes are Dublin + quashed | location, outcome | interaction | 0 | TESTED:KEEP (P01) |
| H16 | Large x quashed has outsized impact | 0.70 | Concentration of delay in large quashed | units, outcome | interaction | 0 | TESTED:KEEP (P02) |
| H17 | 2020 x large is peak interaction | 0.65 | 2020 was peak JR year + large schemes | year, units | interaction | 0 | TESTED:KEEP (P03) |
| H18 | DiD housing vs commercial > 15 excess weeks | 0.65 | Housing delayed more than commercial | case_type | did_weeks | 0 | TESTED:KEEP (T04) |
| H19 | RD proxy > 50 weeks JR premium | 0.55 | SHD cases dramatically slower | case_type | rd_weeks | 0 | TESTED:KEEP (T02) |
| H20 | Counterfactual is best champion model | 0.50 | Most policy-relevant | all | champion | 0 | TESTED:KEEP (TC) |
| H21 | Direct delay is > 80k unit-months even with min imputation | 0.60 | Even at 100 units imputed, many cases | imputed_units | direct_low | 0 | OPEN |
| H22 | Indirect channel upper bound > 8000 unit-months | 0.55 | At 50% JR attribution | jr_share | indirect_upper | 0 | OPEN |
| H23 | Adding remittal time (24mo for quashed) increases direct by >30% | 0.65 | Remittal adds 12-24 months | remittal_months | direct_expanded | 0 | OPEN |
| H24 | Opportunity cost (rent) triples the holding cost estimate | 0.70 | Dublin rents EUR 1500/unit/month | holding_cost | total_cost | 0 | OPEN |
| H25 | Bootstrap CI on direct delay spans < 30% of point estimate | 0.45 | Imputation uncertainty is moderate | bootstrap | ci_width | 0 | OPEN |
| H26 | Non-Dublin cases have lower avg units per scheme | 0.55 | Galway/Meath schemes smaller | location | avg_units | 0 | OPEN |
| H27 | 2023-2024 counterfactual gap > 2022 gap | 0.80 | ABP at 42wk vs 26wk | year | annual_gap | 0 | OPEN |
| H28 | SHD carryover (2022-2024 SHD decisions at ABP) adds to the tax | 0.60 | SHD tail clearing extends the crisis | shd_carryover | additional_delay | 0 | OPEN |
| H29 | Per-unit holding cost in Dublin > EUR 2000/month (incl opportunity) | 0.50 | High Dublin rents | holding_cost | per_unit | 0 | OPEN |
| H30 | JR-lodgement year is better delay start than decision year | 0.55 | Delay begins at lodgement, not decision | delay_measure | comparison | 0 | OPEN |
| H31 | Material contravention is the top quashing reason | 0.70 | From PL-1 paper | quashing_reason | frequency | 0 | OPEN |
| H32 | Environmental grounds (AA/EIA) are second most common | 0.55 | Habitats Directive cases prominent | quashing_reason | frequency | 0 | OPEN |
| H33 | ABP legal cost per JR case > EUR 150k | 0.60 | EUR 8.2M / ~50 JRs | legal_cost | per_case | 0 | OPEN |
| H34 | Total economic cost (direct + indirect + holding + inflation) > EUR 500M | 0.40 | Speculative; high-end | all_costs | total_eur | 0 | OPEN |
| H35 | Meath cases (Protect East Meath, Highland) account for >15% of unit-months | 0.55 | Two large Meath schemes | location | meath_share | 0 | OPEN |
| H36 | BTR (build-to-rent) apartments dominate the unit count | 0.50 | Dublin Cycling = 741 BTR, others | scheme_type | btr_share | 0 | OPEN |
| H37 | Clonres (cases 63 + 115) alone = >20% of direct delay | 0.65 | Two large Clonres cases (536 + 657) | case_name | concentration | 0 | OPEN |
| H38 | Cases with first-party (developer) challengers have shorter delay | 0.45 | Developers have incentive to resolve quickly | challenger_type | avg_delay | 0 | OPEN |
| H39 | Residents' association cases have longer delay | 0.55 | Less incentive to settle | challenger_type | avg_delay | 0 | OPEN |
| H40 | ABP FTE growth (202 to 290) reduced the JR backlog | 0.60 | More staff = faster processing | fte | rho_impact | 0 | OPEN |
| H41 | 2025 compliance recovery (37% to 77%) is consistent with queueing drain | 0.75 | PL-3 rho = 0.74 in 2024 | rho | recovery | 0 | OPEN |
| H42 | Planning and Environment List reduced JR resolution time | 0.60 | Dedicated list from Nov 2022 | p_e_list | jr_resolution | 0 | OPEN |
| H43 | P&E List did NOT reduce ABP decision time | 0.70 | PL-3 E09: mean-W unchanged | p_e_list | abp_effect | 0 | OPEN |
| H44 | Heather Hill extended Aarhus cost protection increased JR intake | 0.60 | PL-2 system-wide 58% growth | heather_hill | jr_intake | 0 | OPEN |
| H45 | 2024 concession spike (53/68 losses) reflects defensive posture | 0.75 | ABP conceding to avoid full loss | concession | rate | 0 | OPEN |
| H46 | SHD scheme size correlates with JR probability | 0.45 | Larger = more visible = more objectors | units | jr_rate | 0 | OPEN |
| H47 | Apartment schemes have higher JR rate than houses | 0.50 | Height/density controversies | scheme_type | jr_rate | 0 | OPEN |
| H48 | Connelly/Balz reason-giving expansion added 5-10 weeks per case | 0.55 | PL-3 beta2 = +5 weeks at 2018 | reason_giving | time_added | 0 | OPEN |
| H49 | Board-member crisis (2022) added 15+ weeks per case | 0.70 | PL-3 beta4 = +15 weeks at 2023 | board_crisis | time_added | 0 | OPEN |
| H50 | Plean-IT transition (2018) added 5 weeks per case | 0.60 | PL-3 beta2 = +5 weeks | it_transition | time_added | 0 | OPEN |
| H51 | Direct delay per case averages > 3,000 unit-months | 0.50 | 100k / ~30 weighted cases | per_case | avg_unit_months | 0 | OPEN |
| H52 | Sensitivity to outcome weights > sensitivity to imputed units | 0.55 | Weights affect all 22 cases; imputation affects 14 | sensitivity | comparison | 0 | OPEN |
| H53 | Monthly counterfactual gap > 500 units in 2023-2024 | 0.70 | Peak excess weeks | counterfactual | monthly | 0 | OPEN |
| H54 | ABP throughput under 18wk SOP would be same as actual (demand-driven) | 0.45 | Processing time doesn't affect demand | counterfactual | throughput | 0 | OPEN |
| H55 | SHD carryover tail-clearing means 2022-2024 direct delay is underestimated | 0.50 | Cases decided post-2022 but not in OPR Appendix-2 | carryover | additional | 0 | OPEN |
| H56 | Total housing units affected by SHD JR > 8,000 including 2022 partial | 0.55 | 22 cases, avg ~360 units | total | units | 0 | OPEN |
| H57 | ABP defence of JR consumes 15-20% of inspector capacity | 0.50 | 50 JRs x 7x multiplier / 2115 disposed | capacity | jr_share | 0 | OPEN |
| H58 | The counterfactual is sensitive to housing_share parameter | 0.65 | 0.30 vs 0.50 makes large difference | housing_share | sensitivity | 0 | OPEN |
| H59 | Non-SHD JRs (SID, NPA) also contribute to ABP slowdown | 0.60 | JR pressure is system-wide | case_type | broad_effect | 0 | OPEN |
| H60 | The direct tax is invariant to reasonable discount-rate assumptions | 0.55 | Unit-months don't discount | discount | invariance | 0 | OPEN |
| H61 | Monte Carlo over design variables gives 95% CI on total tax | 0.45 | Many uncertain parameters | monte_carlo | ci | 0 | OPEN |
| H62 | The indirect tax central estimate is < 10% of direct | 0.50 | Direct dominates | comparison | ratio | 0 | OPEN |
| H63 | Developer-challenger cases had different outcome distribution | 0.40 | First-party vs third-party | challenger | outcome | 0 | OPEN |
| H64 | Average SHD scheme permitted ~185 units (from ABP 2020) | 0.75 | 25,403 / 137 decisions | avg_units | per_scheme | 0 | OPEN |
| H65 | The 2020 spike (10 JRs decided) was the crisis year for SHD | 0.80 | Most JRs converged in 2020 | year | peak | 0 | OPEN |
| H66 | ABP won only 2 of 16 SHD JRs in 2018-2021 | 0.90 | PL-1 established | state_wins | count | 0 | OPEN |
| H67 | Each quashed SHD adds 2-3 years to the scheme timeline | 0.65 | JR + remittal + re-decision | delay | per_quash | 0 | OPEN |
| H68 | Some quashed schemes were never rebuilt | 0.50 | Scheme becomes unviable after delay | viability | non_rebuilt | 0 | OPEN |
| H69 | The EUR 8.2M ABP legal cost in 2020 is < 5% of total JR tax | 0.70 | Holding cost >> legal cost | cost_comparison | ratio | 0 | OPEN |
| H70 | System-wide JR growth (58% in 2024) exceeds LRD-specific growth | 0.75 | PL-2 confirmed | system_vs_regime | comparison | 0 | OPEN |
| H71 | ABP throughput-per-FTE was ~12.8 in 2024, below pre-crisis levels | 0.60 | PL-3 calibration | productivity | per_fte | 0 | OPEN |
| H72 | The indirect channel is the dominant policy lever | 0.50 | Systemic reforms > case-level | policy | leverage | 0 | OPEN |
| H73 | LRD-era JR tax will be estimable by 2027 | 0.55 | PL-2 monitoring framework | projection | timeline | 0 | OPEN |
| H74 | Quarterly ABP data would improve counterfactual precision | 0.65 | Monthly rather than annual resolution | data_granularity | improvement | 0 | OPEN |
| H75 | The top 5 cases by unit count account for > 50% of direct delay | 0.70 | Power-law distribution | concentration | top5_share | 0 | OPEN |
| H76 | Including student accommodation would add to the unit count | 0.50 | Some SHD included student beds | scheme_type | additional_units | 0 | OPEN |
| H77 | The JR tax is regressive (delays housing for those most in need) | 0.60 | Large urban schemes = affordable supply | equity | regressivity | 0 | OPEN |
| H78 | ABP decision quality improved post-crisis (fewer JR losses) | 0.40 | More time per case = better reasoning | quality | loss_rate | 0 | OPEN |
| H79 | The costs rule is the single biggest driver of JR filing rates | 0.55 | Near-zero cost to file | costs_rule | jr_rate | 0 | OPEN |
| H80 | Reforms to the costs rule would reduce JR tax more than any other single policy | 0.50 | Remove the asymmetry | policy | impact | 0 | OPEN |
| H81 | PDA 2024 will reduce JR filing rates by restricting grounds | 0.40 | New Act narrows JR scope | pda_2024 | jr_reduction | 0 | OPEN |
| H82 | The direct JR delay is a lower bound on total housing impact | 0.85 | Indirect + cost + viability not counted | bounding | direction | 0 | OPEN |
| H83 | Per-year direct delay correlates with JR cases decided that year | 0.80 | More cases = more delay | correlation | r_squared | 0 | OPEN |
| H84 | The counterfactual assumes ABP intake is exogenous to processing time | 0.60 | Demand-driven intake | assumption | validity | 0 | OPEN |
| H85 | Ireland's JR rate is 5-10x higher than UK NSIP JR rate | 0.65 | PL-2 E20: IE 8.6% vs UK 3-5% | international | comparison | 0 | OPEN |
| H86 | The housing share of ABP cases is stable over time | 0.50 | Mix may shift with SHD->LRD | housing_share | stability | 0 | OPEN |
| H87 | ABP backlog-at-start is the best single predictor of mean weeks | 0.70 | PL-3 E12: +13.7wk per 1000 cases | predictor | importance | 0 | OPEN |
| H88 | The JR tax is larger in unit-months than the board-crisis tax | 0.35 | Board crisis was the dominant shock | comparison | relative_size | 0 | OPEN |
| H89 | Adding commercial-type delays to the counterfactual is inappropriate | 0.70 | Commercial not affected by housing JR | scope | validity | 0 | OPEN |
| H90 | The 18-week baseline is the right counterfactual (not 22 or 23 weeks) | 0.60 | Pre-2018 was 17-18 weeks | baseline | choice | 0 | OPEN |
| H91 | A 22-week baseline reduces the counterfactual gap by ~30% | 0.55 | Less excess per year | sensitivity | gap_reduction | 0 | OPEN |
| H92 | The direct delay is robust to removing any single case | 0.60 | No single case dominates > 20% | robustness | leave_one_out | 0 | OPEN |
| H93 | The total JR tax (direct + indirect) is equivalent to ~1 year of Dublin completions | 0.50 | ~110k unit-months / 12 ~= 9k units | scale | comparison | 0 | OPEN |
| H94 | Environmental grounds produce longer delays than procedural grounds | 0.45 | AA/EIA cases are more complex | quashing_reason | delay | 0 | OPEN |
| H95 | The 2020 peak in JR decisions was driven by the courts clearing a backlog | 0.60 | Courts Service capacity | court_capacity | effect | 0 | OPEN |
| H96 | Pre-application consultation did not reduce JR risk for SHD | 0.55 | SHD had mandatory pre-app but high JR | pre_app | effectiveness | 0 | OPEN |
| H97 | The unit count sensitivity range is [80k, 140k] unit-months | 0.60 | From min to max imputation | sensitivity | range | 0 | OPEN |
| H98 | ABP legal costs per JR are lower than developer holding costs per JR | 0.75 | Legal ~EUR 150k vs holding ~EUR 1.8M | cost_comparison | ratio | 0 | OPEN |
| H99 | The counterfactual gap accelerates nonlinearly with excess weeks | 0.60 | Completions x (excess/52) is linear; but excess itself grows nonlinearly | nonlinearity | acceleration | 0 | OPEN |
| H100 | A structural queueing model would give tighter indirect bounds | 0.45 | More mechanistic than channel bounds | model | precision | 0 | OPEN |
| H101 | The JR tax per unit is > 10 months of delay for quashed schemes | 0.60 | Direct: 18mo typical for quashed | per_unit | delay | 0 | OPEN |
| H102 | Including commencement-notice lag data from PL-1 would improve the counterfactual | 0.50 | Permission-to-commencement is another delay | data | improvement | 0 | OPEN |
