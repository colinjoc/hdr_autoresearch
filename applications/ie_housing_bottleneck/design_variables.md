# Design Variables

## Pipeline Stage Parameters (directly from predecessor studies)

| Variable | Current Value | Source | Unit |
|----------|--------------|--------|------|
| permission_volume | 38,000 | BHQ15 median 2019-2025 | units/yr |
| lapse_rate | 0.095 | PL-4 NRU>0 2017-2019 | fraction |
| lapse_rate_ci_lo | 0.044 | PL-4 cluster-bootstrap | fraction |
| lapse_rate_ci_hi | 0.156 | PL-4 cluster-bootstrap | fraction |
| perm_to_comm_days | 232 | PL-1 median | days |
| comm_to_ccc_days | 498 | PL-1 median | days |
| total_pipeline_days | 962 | PL-1 complete timeline | days |
| ccc_filing_rate | 0.409 | S-1 (all commenced) | fraction |
| ccc_filing_rate_nonoptout | 0.598 | S-1 (non-opt-out) | fraction |
| opt_out_share | 0.316 | S-1 | fraction |
| ccc_to_occupied | 0.95 | S-1 (estimated) | fraction |
| abp_weeks_2017 | 18 | PL-3 baseline | weeks |
| abp_weeks_2024 | 42 | PL-3 | weeks |
| abp_rho_2022 | 1.45 | PL-3 | ratio |
| jr_direct_unit_months | 105504 | S-2 central | unit-months |
| jr_direct_range_lo | 85404 | S-2 floor | unit-months |
| jr_direct_range_hi | 150204 | S-2 high | unit-months |
| counterfactual_gap_uncapped | 16638 | S-2 | units over 2018-2024 |
| counterfactual_gap_35k_cap | 7421 | S-2 | units over 2018-2024 |
| lda_delivery_2023 | 850 | PL-3 LDA | units/yr |
| completions_2024 | 34177 | NDA12 | units |
| hfa_target | 50500 | Housing for All | units/yr |
| construction_capacity | 35000 | Observed 2024 ceiling | units/yr |

## Scenario Parameters (for sensitivity analysis)

| Variable | Range | Purpose |
|----------|-------|---------|
| permission_volume_scenario | [38000, 48000, 58000, 68000] | E02 permission volume sensitivity |
| abp_weeks_scenario | [18, 30, 42] | E03 ABP speed sensitivity |
| lapse_rate_scenario | [0.0475, 0.095, 0.156] | E05 lapse sensitivity |
| construction_duration_factor | [0.5, 0.75, 1.0] | E06 construction speed |
| capacity_ceiling | [35000, 40000, 50000, None] | E07 capacity scenarios |
| opt_out_build_rate | [0.5, 0.75, 0.9, 1.0] | E01 opt-out adjustment |
