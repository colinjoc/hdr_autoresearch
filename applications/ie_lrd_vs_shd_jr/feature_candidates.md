# Feature candidates — LRD vs SHD JR

Features considered for the tournament models and the Phase 2 experiments.

## Case-level features (from OPR Appendix-2 + OPR bulletins + ABP decision references)

| # | Name | Source | Type | Notes |
|---|---|---|---|---|
| F1 | regime | derived from decision date | categorical {SHD, LRD} | Primary treatment indicator |
| F2 | decision_year | ABP decision date | integer | 2017-2024 |
| F3 | decision_month | ABP decision date | integer | Used for ITS |
| F4 | jr_lodgement_date | HC record | date | For survival analysis |
| F5 | time_to_jr_days | F4 - ABP decision date | integer | Censored at 56 days (8 weeks) |
| F6 | scheme_units | ABP decision text | integer | Scale proxy |
| F7 | scheme_type | ABP decision text | categorical {apartments, houses, student, BTR, mixed} | Typology |
| F8 | la_area | ABP decision text | categorical | Dublin vs rest; individual LA |
| F9 | dublin_flag | derived from F8 | bool | Dublin CCs = DCC, FCC, SDCC, DLRCC |
| F10 | scheme_size_band | derived F6 | ordinal {100-199, 200-499, 500+} | |
| F11 | applicant_type | OPR Appendix-2 applicant field | categorical {residents_assoc, env_ngo, individual, developer, la, other} | |
| F12 | multi_applicant_flag | OPR case name | bool | ">1" named applicant |
| F13 | grounds_procedural | OPR case summary | int 0/1 | Flag if procedural grounds pleaded |
| F14 | grounds_environmental | OPR case summary | int 0/1 | EIA/AA/SEA grounds |
| F15 | grounds_material_contravention | OPR case summary | int 0/1 | |
| F16 | grounds_height | OPR case summary | int 0/1 | SPPR 3 |
| F17 | grounds_density | OPR case summary | int 0/1 | |
| F18 | grounds_reasoning | OPR case summary | int 0/1 | Connelly/Balz line |
| F19 | outcome | OPR outcome column | categorical {won, lost, conceded, withdrawn, other} | Target for loss-rate |
| F20 | neutral_citation_year | OPR neutral citation | integer | For decision year |
| F21 | judge | IEHC citation | string | Planning and Environment List judges |
| F22 | oral_hearing_flag | ABP case file | bool | ABP 2022 reports 2 oral hearings that year |
| F23 | costs_order | OPR / HC judgment | categorical | Costs order result |
| F24 | conceded_before_hearing | OPR outcome | bool | |
| F25 | elapsed_days_to_judgment | judgment - lodgement | int | Pre-vs-post Planning List |

## Regime-level aggregate features (from ABP annual reports)

| # | Name | Source | Type | Notes |
|---|---|---|---|---|
| A1 | permissions_decided_year | ABP Annual Report | integer | Denominator for JR-rate |
| A2 | permissions_granted_year | ABP Annual Report | integer | Alt denominator |
| A3 | total_jrs_lodged_year | ABP Annual Report | integer | Numerator for intake-rate |
| A4 | total_jrs_served_year | ABP Annual Report | integer | |
| A5 | abp_legal_expenditure | ABP Annual Accounts | currency | Cost lever |
| A6 | abp_cost_recovery_rate | ABP Annual Accounts | ratio | Heather Hill impact |
| A7 | concession_rate_year | ABP Table 3 | ratio | Conceded / (won+lost+conceded) |
| A8 | withdrawal_rate_year | ABP Table 3 | ratio | |
| A9 | planning_list_operational | dummy | bool | 1 from Nov 2022 |
| A10 | covid_year | dummy | bool | 1 for 2020-2021 |
| A11 | housing_completions_year | CSO | integer | Macro context |
| A12 | housing_commencements_year | CSO | integer | Macro context |
| A13 | scheme_size_median_year | ABP decisions | integer | Typology shift |

## Derived statistical features (for models)

| # | Name | Derivation | Purpose |
|---|---|---|---|
| D1 | shd_indicator | F1 == SHD | Treatment indicator |
| D2 | lrd_indicator | F1 == LRD | Treatment indicator |
| D3 | post_dec2021 | decision_date >= 2021-12-17 | ITS knot dummy |
| D4 | months_since_knot | max(0, months - knot_month) | ITS slope |
| D5 | log_units | log(F6 + 1) | Handles skew |
| D6 | time_lag_dummy | permission_year >= 2022 AND decided_year - permission_year <= 2 | Censoring flag |
| D7 | carryover_shd | F1 == SHD AND decision_year >= 2022 | Exclusion flag for E01 |
| D8 | any_eu_ground | F14 OR grounds_habitats OR grounds_eia | EU law ground flag |
| D9 | ngo_x_ngo | F11 == env_ngo | Applicant indicator |
| D10 | dublin_x_regime | F9 * D1 | Interaction — E02 |
