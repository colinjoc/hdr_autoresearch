# Design Variables — IE Housing Pipeline E2E

## Pipeline Stage Transition Rates (Primary Design Variables)

| Variable | Definition | Source | Range |
|---|---|---|---|
| `lapse_rate` | Share of granted permissions that never file a commencement notice | PL-4 planning register | 0.0949 (NRU>0 2017-2019) to 0.274 (all-cohort fuzzy) |
| `ccc_rate` | Share of commenced projects that file a Certificate of Completion and Compliance | PL-1 BCMS | 0.409 (all) to 0.598 (non-opt-out) |
| `ccc_to_occupied` | Share of CCC-certified homes that become occupied | CSO completions proxy | ~0.95 (estimated) |
| `yield_rate` | End-to-end: completions / permissions | Derived: (1-lapse) × ccc × occ | 0.28 to 0.37 |

## Pipeline Duration Variables

| Variable | Definition | Source | Median (days) |
|---|---|---|---|
| `days_perm_to_comm` | Permission grant to commencement notice | PL-1 BCMS | 234 [231, 236] |
| `days_comm_to_ccc` | Commencement to CCC validation | PL-1 BCMS | 496 [492, 498] |
| `days_perm_to_ccc` | Total pipeline latency | PL-1 BCMS | 1,096 [1,084, 1,105] |

## Stratification Variables (Covariates)

| Variable | Levels | Expected effect on yield |
|---|---|---|
| `size_stratum` | 1, 2-9, 10-49, 50-199, 200+ | Larger schemes have higher CCC rates |
| `is_dublin` | True/False | Dublin has higher CCC rates (+8pp) |
| `apartment_flag` | True/False | Apartment blocks have different completion dynamics |
| `one_off_flag` | True/False | One-off houses have very low CCC rate (opt-out) |
| `ahb_flag` | True/False | AHB projects have higher CCC rate (~72%) |
| `opt_out` | True/False | Opt-out projects never file CCC (0% by design) |
| `grant_year` | 2014-2019 | Later years have higher CCC rates |
| `shd_era` | True/False | SHD-era permissions (2017-2021) |
| `post_covid` | True/False | COVID-19 increased latency by ~28d |
| `la_clean` | 31 Local Authorities | Large heterogeneity (CV=0.48) |

## Sensitivity Variables

| Variable | Scenario | Impact |
|---|---|---|
| `halved_lapse` | Lapse rate from 9.5% to 4.75% | +700 completions/yr |
| `ccc_plus_10pp` | CCC rate +10pp | +3,267 completions/yr |
| `perms_60k` | Permission volume to 60k/yr | 21,081 completions/yr |
| `s34_1.0` | CCC→occupied = 100% | Yield +1.9pp |
