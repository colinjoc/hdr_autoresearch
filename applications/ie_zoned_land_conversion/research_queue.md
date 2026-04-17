# Research Queue: IE Zoned Land Conversion

## Status key: OPEN | RUN | KEEP | REVERT | SKIP

| # | Hypothesis | Prior | Posterior | Design Variable | Metric | Status | Exp ID |
|---|-----------|-------|-----------|-----------------|--------|--------|--------|
| 1 | National application intensity is 2-5 apps/ha/yr | 0.7 | 0.85 | national aggregate | apps_per_ha_per_year | KEEP | E00 |
| 2 | East+Midlands has higher intensity than North+West | 0.7 | 0.85 | region | apps_per_ha_per_year | KEEP | E01 |
| 3 | Dublin has higher intensity than non-Dublin | 0.6 | 0.3 | dublin_flag | apps_per_ha_per_year | KEEP | E02 |
| 4 | RZLT announcement (2022) increased applications | 0.5 | 0.4 | pre_post_2022 | pct_change | KEEP | E03 |
| 5 | Higher land prices correlate with more applications | 0.6 | 0.5 | land_price_per_ha | pearson_r | KEEP | E04 |
| 6 | Sale price / construction cost ratio affects viability | 0.7 | 0.75 | viability_ratio | ratio | KEEP | E05 |
| 7 | One-off houses dominate residential applications | 0.6 | 0.7 | app_type | pct_oneoff | KEEP | E06 |
| 8 | Apartments are a small fraction of applications | 0.5 | 0.6 | app_type | pct_apartment | KEEP | E07 |
| 9 | COVID reduced application volumes in 2020-2021 | 0.7 | 0.3 | pre_post_covid | pct_change | KEEP | E08 |
| 10 | Applications show seasonal pattern | 0.6 | 0.7 | month | seasonality_ratio | KEEP | E09 |
| 11 | High-refusal LAs get fewer applications | 0.5 | 0.4 | approval_rate | pearson_r | KEEP | E10 |
| 12 | Zoned land declined 55% from 2014 to 2024 | 0.8 | 0.9 | time_period | consumed_ha | KEEP | E11 |
| 13 | Rural LAs have higher per-capita application rates | 0.5 | 0.6 | apps_per_1000 | ranking | KEEP | E12 |
| 14 | More zoned land → more applications | 0.7 | 0.2 | zoned_ha | pearson_r | KEEP | E13 |
| 15 | Fingal has disproportionately low intensity | 0.5 | 0.9 | fingal_flag | apps_per_ha | KEEP | E14 |
| 16 | Application trend is increasing over 2015-2025 | 0.6 | 0.65 | year | slope | KEEP | E15 |
| 17 | Longer decision lag deters applications | 0.4 | 0.35 | median_lag | pearson_r | KEEP | E16 |
| 18 | One-off rate proxies infrastructure availability | 0.5 | 0.45 | oneoff_pct | pearson_r | KEEP | E17 |
| 19 | Higher refusal rate deters applications | 0.5 | 0.5 | refusal_rate | pearson_r | KEEP | E18 |
| 20 | Land price × approval rate interaction matters | 0.4 | 0.35 | interaction_term | R_squared | KEEP | E19 |
| 21 | Ireland has higher intensity than UK per zoned ha | 0.5 | 0.5 | international | ratio | KEEP | E20 |
| 22 | E00 confidence interval excludes 0 | 0.8 | 0.85 | bootstrap | ci_lower | KEEP | E21 |
| 23 | Stock exhaustion in <20 years at current rate | 0.6 | 0.7 | stock_flow | years | KEEP | E22 |
| 24 | Cork County has highest intensity | 0.5 | 0.6 | la_ranking | max_intensity | KEEP | E23 |
| 25 | Mean units per application is <5 | 0.5 | 0.6 | units_per_app | mean | KEEP | E24 |
| 26 | Large schemes are increasing over time | 0.5 | 0.55 | large_scheme_count | slope | KEEP | E25 |
| 27 | Low quarterly volatility (<0.2 CV) | 0.5 | 0.55 | quarterly_cv | cv | KEEP | E26 |
| 28 | Annual capacity utilization is <15% | 0.5 | 0.6 | capacity_util | pct | KEEP | E27 |
| 29 | Applications modestly concentrated (HHI 0.03-0.1) | 0.5 | 0.5 | hhi | index | KEEP | E28 |
| 30 | Positive YoY growth trend | 0.5 | 0.5 | yoy_growth | mean_pct | KEEP | E29 |
| 31 | Filing concentrated on business days | 0.5 | 0.6 | weekday | concentration | KEEP | E30 |
| 32 | Dublin × RZLT differential effect exists | 0.4 | 0.45 | did_estimate | apps_per_yr | KEEP | INT01 |
| 33 | Large schemes cluster in East+Midlands | 0.5 | 0.5 | region × scheme_size | count | KEEP | INT02 |
| 34 | Approval × population interaction matters | 0.4 | 0.4 | interaction | pearson_r | KEEP | INT03 |
| 35 | Population is the strongest predictor in panel | 0.6 | 0.7 | panel_coefs | t_stat | KEEP | T02 |
| 36 | Logistic model achieves AUC > 0.8 | 0.5 | 0.8 | logistic | AUC | KEEP | T04 |
| 37 | Zoned land quantity is NOT the binding constraint | 0.3 | 0.8 | multiple | null_r | KEEP | E13 |
| 38 | Option value explains the gap better than regulation | 0.5 | 0.6 | viability | ratio | OPEN | - |
| 39 | RZLT will have larger effect after 2025 (delayed response) | 0.6 | - | time_lag | future | OPEN | - |
| 40 | Fingal land is held by a few large owners | 0.5 | - | ownership | concentration | OPEN | - |
| 41 | SHD process (2017-2022) created a structural break | 0.4 | - | policy_regime | app_count | OPEN | - |
| 42 | Apartment viability constraint is more binding than house | 0.6 | - | type_split | viability | OPEN | - |
| 43 | LDA land activation is negligible vs private | 0.7 | - | lda_share | pct | OPEN | - |
| 44 | Construction cost inflation exceeds sale price growth | 0.5 | - | cost_index | ratio | OPEN | - |
| 45 | Water infrastructure is the binding constraint in specific LAs | 0.5 | - | irish_water | capacity | OPEN | - |
| 46 | Permission-to-commencement lag is longer in low-intensity LAs | 0.4 | - | lag × intensity | pearson_r | OPEN | - |
| 47 | Landowners prefer to sell to developers rather than develop | 0.5 | - | transaction_data | volume | OPEN | - |
| 48 | Zoned land near existing development converts faster | 0.6 | - | spatial_proximity | hazard_ratio | OPEN | - |
| 49 | Smaller parcels convert faster than large ones | 0.5 | - | parcel_size | intensity | OPEN | - |
| 50 | Development plan cycle creates 6-year periodicity | 0.4 | - | dev_plan_year | app_count | OPEN | - |
| 51 | Pre-application consultation correlates with higher grant rate | 0.5 | - | pre_app | grant_rate | OPEN | - |
| 52 | Multi-unit applications have lower approval rate | 0.4 | - | app_type | grant_rate | OPEN | - |
| 53 | Cork County intensity driven by commuter belt | 0.6 | - | sub_county | intensity | OPEN | - |
| 54 | Meath intensity driven by Dublin spillover | 0.6 | - | commuter_flag | intensity | OPEN | - |
| 55 | Application intensity recovers faster post-GFC in urban LAs | 0.5 | - | urban_rural | recovery_speed | OPEN | - |
| 56 | Higher population growth LAs have higher intensity | 0.6 | - | pop_growth | pearson_r | OPEN | - |
| 57 | Institutional investors crowd out small developers | 0.3 | - | scheme_size_trend | distribution | OPEN | - |
| 58 | Part V (social housing) requirement deters applications | 0.3 | - | part_v | app_count | OPEN | - |
| 59 | Appeal rate is higher in high-intensity LAs | 0.4 | - | appeal_rate | pearson_r | OPEN | - |
| 60 | Environmental designations reduce usable zoned land | 0.5 | - | env_designation | effective_ha | OPEN | - |
| 61 | Landowners zone land to capture value without intending to develop | 0.6 | - | speculative_zoning | price_premium | OPEN | - |
| 62 | Cross-boundary commuting drives application patterns | 0.5 | - | commuter_flow | intensity | OPEN | - |
| 63 | Student accommodation distorts application counts | 0.3 | - | student_acc | filtering | OPEN | - |
| 64 | Vacant site levy had no measurable effect | 0.5 | - | vsl_era | app_count | OPEN | - |
| 65 | Planning conditions (conditions attached) vary by LA | 0.5 | - | condition_count | variation | OPEN | - |
| 66 | FI (further information) requests correlate with lag | 0.7 | - | fi_request | lag_days | OPEN | - |
| 67 | Commercial zoned land converts faster than residential | 0.4 | - | land_use_code | intensity | OPEN | - |
| 68 | Retained permissions (existing but unexercised) reduce effective demand | 0.5 | - | retention_count | intensity | OPEN | - |
| 69 | Post-2017 data quality improvement creates apparent increase | 0.4 | - | data_quality | break_test | OPEN | - |
| 70 | Weekend filing indicates online submission adoption | 0.5 | - | weekend_pct | trend | OPEN | - |
| 71 | Application intensity follows a saturation curve | 0.3 | - | nonlinear | R_squared | OPEN | - |
| 72 | Top-3 LAs account for >50% of national applications | 0.4 | - | concentration | lorenz_curve | OPEN | - |
| 73 | Grant rate is countercyclical (rises in downturns) | 0.4 | - | cycle | grant_rate | OPEN | - |
| 74 | Building energy rating requirements deter renovation applications | 0.3 | - | ber | app_count | OPEN | - |
| 75 | Design manual for urban roads delays large schemes | 0.3 | - | dmurs | lag_days | OPEN | - |
| 76 | Judicial review risk deters large applications | 0.5 | - | jr_risk | scheme_size | OPEN | - |
| 77 | Heritage/conservation areas reduce effective zoned stock | 0.4 | - | heritage | effective_ha | OPEN | - |
| 78 | Speculative applications (withdrawn before decision) inflate counts | 0.3 | - | withdrawal_rate | adjustment | OPEN | - |
| 79 | Multi-phase developments appear as multiple applications | 0.4 | - | phasing | double_count | OPEN | - |
| 80 | LA staffing levels correlate with processing speed | 0.5 | - | staff_per_app | lag_days | OPEN | - |
| 81 | e-Planning rollout improved data completeness | 0.5 | - | e_planning | completeness | OPEN | - |
| 82 | Agricultural land tax relief reduces development incentive | 0.4 | - | agri_tax | hold_out | OPEN | - |
| 83 | High site area applications (>1 ha) are a different market | 0.5 | - | site_area | segmentation | OPEN | - |
| 84 | Extension of duration applications proxy for stalled projects | 0.6 | - | eod_count | stalled_pct | OPEN | - |
| 85 | Retention applications indicate unpermitted development | 0.5 | - | retention | compliance | OPEN | - |
| 86 | SHD-eligible sites (>100 units) have different conversion | 0.4 | - | shd_eligible | intensity | OPEN | - |
| 87 | LPT (Local Property Tax) receipts correlate with intensity | 0.4 | - | lpt | pearson_r | OPEN | - |
| 88 | Net international migration correlates with application rate | 0.5 | - | migration | pearson_r | OPEN | - |
| 89 | Credit conditions (mortgage availability) drive applications | 0.5 | - | credit | pearson_r | OPEN | - |
| 90 | Interest rate changes affect application timing | 0.4 | - | ecb_rate | lag | OPEN | - |
| 91 | Brexit uncertainty affected 2019-2020 applications | 0.3 | - | brexit | event_study | OPEN | - |
| 92 | Help-to-Buy scheme (2017) stimulated one-off house applications | 0.5 | - | htb | one_off_count | OPEN | - |
| 93 | Developer confidence index correlates with application volume | 0.5 | - | confidence | pearson_r | OPEN | - |
| 94 | Material cost spikes cause application pauses | 0.4 | - | material_cost | timing | OPEN | - |
| 95 | Landowners wait for better zoning (higher density allowance) | 0.4 | - | density_zoning | hold_out | OPEN | - |
| 96 | Long-term vacancy in area deters new applications | 0.4 | - | vacancy_rate | intensity | OPEN | - |
| 97 | School and childcare capacity affects family housing demand | 0.3 | - | social_infra | intensity | OPEN | - |
| 98 | Flood risk designation removes effective zoned land | 0.5 | - | flood_zone | effective_ha | OPEN | - |
| 99 | Applications per zoned hectare is higher in city councils than county | 0.5 | - | city_vs_county | intensity | OPEN | - |
| 100 | Cross-LA heterogeneity exceeds within-LA temporal variation | 0.6 | - | variance_decomposition | ratio | OPEN | - |
| 101 | Converting Fingal to East+Midlands average would add ~1200 apps/yr | 0.5 | - | counterfactual | additional_apps | OPEN | - |
| 102 | National application rate is structurally capped by viability | 0.6 | - | viability_threshold | ceiling | OPEN | - |
| 103 | Planning register data break in 2017 explains apparent surge | 0.5 | - | structural_break | chow_test | OPEN | - |
