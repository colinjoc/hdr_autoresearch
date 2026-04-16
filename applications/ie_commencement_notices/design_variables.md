# Design variables — PL-1 cohort study

This is a descriptive+predictive project; design variables are the levers we sweep in Phase 2 (cohort definitions, stratifications, filter cutoffs) and the Phase B discovery variables (LA choice and scheme-size choice).

## Phase 2 experimental design variables (cohort filters / stratifications)

| variable | values | used in |
|---|---|---|
| year_cutoff | 2014, 2015, 2016 | E01 |
| use_class_filter | residential-only vs residential-multi-only | E02 |
| la_fixed_effects | included / excluded | E03 |
| size_stratum | 1, 2-9, 10-49, 50-199, 200+ units | E04, E15 |
| winsorise_percentile | 0, 1, 5 | E05 |
| dublin_subset | dublin-only / non-dublin / both | E06 |
| shd_era_split | pre-2017 / 2017-2021 / post-2021 | E07 |
| covid_split | pre-COVID / post-COVID | E08 |
| dwelling_type_split | apartment / dwelling | E09 |
| ahb_split | AHB-yes / AHB-no | E10 |
| near_expiry_subset | within-6m-of-expiry / not | E11 |
| multi_phase_subset | phase-1 / phase-2+ | E12 |
| completion_metric | CCC_Units_Completed / CN_Total_Number_of_Dwelling_Units | E13 |
| censoring_date | dataset_end / dataset_end - 6m | E14 |
| rural_urban_split | rural (small LA) / urban (Dublin+Cork+Galway+Limerick+Waterford) | E16 |
| cohort_horizon | 24 / 48 / 72 months | E17 |
| cohort_year | 2014, 2015, ..., 2020 | E18 |
| la_cluster | county-level clustering for GEE | E19 |
| darkperm_model | logistic vs LightGBM vs RandomForest | E20 |

## Phase B discovery design variables

| variable | values | role |
|---|---|---|
| LA | 31 Local Authorities | discovery input |
| scheme_size_stratum | 1, 2-9, 10-49, 50-199, 200+ units | discovery input |
| dwelling_type | apartment / dwelling | discovery input |
| era | pre-2020 / post-2020 | stratifier |
| target | P(complete within 48 months of permission) | discovery objective |

The Phase B script scores every (LA × size × type × era) cell and ranks the top-K cells by predicted completion probability, conditional on at least 30 historical cohort members in the cell.
