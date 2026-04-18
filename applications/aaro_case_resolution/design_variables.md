# Design Variables: AARO Case Resolution Analysis

This project is a descriptive/decomposition analysis (Option C) rather than a predictive model. The "design variables" are the analytical choices that affect conclusions.

## Primary Analysis Variables

| Variable | Range | Effect on Analysis |
|---|---|---|
| resolution_counting | {formal_only, include_pending} | Changes rate from 7.1% to 17.7% |
| period_filtering | {all_reports, current_period_only} | Intake 757 vs 485 if excluding prior-period catch-up |
| base_rate_prior | [0.01, 0.20] | Bayesian posterior sensitivity |
| comparison_program | {Blue Book, Hendry, GEIPAN, NUFORC} | Different base rates for calibration |
| archive_treatment | {count_as_unresolved, exclude_from_denominator} | Changes effective resolution rate |
| ic_merit_interpretation | {anomalous_candidate, further_investigation_needed} | Framing of 21 cases |

## Sensitivity Dimensions

| Dimension | Values Tested | Impact |
|---|---|---|
| Time period | pre-2021, 2022, 2023, 2024 | Trend analysis |
| Data source | FY2024, ODNI 2022, Blue Book, Hendry, NUFORC | Cross-program comparison |
| Resolution definition | formal closure, pending closure, initial characterization | Rate calculation |
| Geographic scope | global, East Asian Seas, Middle East, CONUS | Regional variation |
| Report source | military, FAA, combined | Channel effects |
