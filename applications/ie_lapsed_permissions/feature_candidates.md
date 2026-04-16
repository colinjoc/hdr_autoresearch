# Feature candidates — lapsed permissions

All features are derivable from the National Planning Application register (`national_planning_points.csv`) plus join to BCMS (`bcms_notices.csv`).

| # | feature | type | derivation | rationale | expected sign (on lapse) |
|---|---------|------|-----------|-----------|--------------------------|
| 1 | grant_year | int | year(GrantDate) | cohort cycle | complex (year F.E.) |
| 2 | planning_authority | cat(31) | PlanningAuthority | LA heterogeneity | F.E. |
| 3 | app_type | cat(3) | ApplicationType ∈ {PERMISSION, OUTLINE, RETENTION} | regime | OUTLINE, RETENTION → higher |
| 4 | decision | cat(3) | Decision | filter: keep CONDITIONAL + GRANT PERMISSION | — |
| 5 | num_residential_units | int | NumResidentialUnits | scheme size | non-linear |
| 6 | size_band | cat(4) | {1, 2-4, 5-49, 50+} | interpretable bins | U-shaped |
| 7 | one_off | bool | `One-Off House == "Yes"` | personal vs corporate | lower |
| 8 | floor_area | float | FloorArea | secondary size | — |
| 9 | area_of_site | float | AreaofSite (hectares) | infrastructure prereq | positive |
| 10 | appeal_status | cat | AppealStatus | ABP processing | selection |
| 11 | appealed_flag | bool | AppealReferenceNumber populated | committed applicants | lower |
| 12 | has_forename | bool | ApplicantForename non-empty | individual vs corporate | complex |
| 13 | dublin_flag | bool | PA ∈ {DCC, FCC, SDCC, DLR} | market tier | lower |
| 14 | gda_flag | bool | Greater Dublin Area (incl. Meath, Kildare, Wicklow) | market tier | lower |
| 15 | shd_era | bool | 2017 ≤ grant_year ≤ 2021 | regime | neutral |
| 16 | pre_shd | bool | grant_year ≤ 2016 | post-crash recovery | higher |
| 17 | covid_granted | bool | grant_year ≥ 2020 | supply-chain shock | higher (short-term) |
| 18 | decision_lag_days | int | DecisionDate − ReceivedDate | contested sites | positive |
| 19 | fi_requested | bool | FIRequestDate populated | iterative resolution | positive |
| 20 | expiry_horizon_days | int | ExpiryDate − ETL_DATE | remaining window (if positive) | derived |
| 21 | expiry_passed | bool | ExpiryDate < ETL_DATE | resolved cohort | T → unambiguous |
| 22 | land_use_code | cat | LandUseCode | non-residential filter | — |
| 23 | itm_geocoded | bool | ITMEasting populated | data quality | data-quality control |
| 24 | applicant_surname | cat(top-N + other) | ApplicantSurname | repeat-developer | repeat → lower |
| 25 | description_len | int | len(DevelopmentDescription) | scheme complexity | positive |

Derived feature families:
- Time-to-event target (for Cox/AFT): `days_to_commence = CN_Commencement_Date − GrantDate`; censored = `expiry_passed and no BCMS match` OR `ETL_DATE − GrantDate` for live cases.
- Binary lapse target (for logit/GBM/RF): `lapse = (no BCMS match) AND (expiry_passed OR grant_year ≤ 2019)`.
- Interaction features explored in Phase 2.5: `size_band × dublin_flag`, `size_band × app_type`, `grant_year × dublin_flag`, `grant_year × size_band`.

Phase B design variables (prospective-developer-facing): `planning_authority × size_band × app_type × dublin_flag` → grid of predicted commencement probability.
