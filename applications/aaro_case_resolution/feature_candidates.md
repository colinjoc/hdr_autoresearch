# Feature Candidates: AARO Case Resolution Analysis

## Quantitative Figures Extractable from Reports

| Feature | Source | Type | Justification |
|---|---|---|---|
| cumulative_total | All reports | count | Total UAP reports over time; baseline volume metric |
| new_reports_period | All reports | count | Intake rate; channel effect measurement |
| cases_resolved | FY2024 | count | Resolution capacity metric |
| cases_pending_closure | FY2024 | count | Processing pipeline bottleneck indicator |
| cases_active_archive | FY2024 | count | Data-insufficiency rate |
| cases_merit_ic | FY2024 | count | Potentially anomalous fraction |
| resolution_rate | Computed | ratio | Primary outcome: resolved/total |
| archive_fraction | Computed | ratio | Data quality proxy: archived/intake |
| ic_merit_fraction | Computed | ratio | Anomaly candidate rate: ic_merit/intake |
| air_domain_fraction | FY2024 | ratio | Domain distribution |
| faa_fraction | FY2024 | ratio | Channel contribution |
| nuclear_reports | FY2024 | count | Nuclear security dimension |
| morphology_insufficient_pct | FY2024 | pct | Data quality proxy for observation detail |
| flight_safety_count | FY2024 | count | Safety dimension |
| intake_rate_per_month | Computed | rate | Temporal intake pattern |
| resolution_rate_per_month | Computed | rate | Temporal resolution capacity |
| intake_to_resolution_ratio | Computed | ratio | Backlog growth indicator |

## Derived Analytical Features

| Feature | Formula | Justification |
|---|---|---|
| prosaic_conditional_rate | resolved_prosaic / resolved_total | P(prosaic | resolved) -- currently 100% |
| data_sufficiency_rate | 1 - archive_fraction | Fraction with enough data for analysis |
| bayesian_posterior | Bayes theorem with base-rate prior | P(anomalous | unresolved, prior) |
| base_rate_comparison | Program resolution rates | Cross-program calibration |
| backlog_months | cumulative_open / net_resolution_rate | Time to clear at current pace |
| channel_effect | reports_by_source / total | Source contribution decomposition |
| regional_resolution_rate | regional_resolved / regional_total | Geographic resolution variation |

## Qualitative/Categorical Features

| Feature | Values | Source |
|---|---|---|
| resolution_category | balloons, birds, UAS, satellites, aircraft, clutter | FY2024, ODNI 2022 |
| domain | air, space, maritime, transmedium | All reports |
| morphology | lights, orb/sphere, disk, triangle, other, insufficient | FY2024 Fig 3 |
| data_status | resolved, pending, active_archive, ic_merit | FY2024 |
| geographic_cluster | East Asian Seas, Middle East, US military areas, CONUS | FY2024 |
