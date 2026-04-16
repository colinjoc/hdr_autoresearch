# Data sources — PL-1 commencement-notice cohort study

## Primary

1. **BCMS row-level dataset** (row-level, per-building)
   - URL: https://data.nbco.gov.ie/dataset/2704a333-874d-46f5-b3bc-3673766bf816/resource/0774e781-7af8-46da-b623-872e74cf541e/download/buildingscnscccs.csv
   - Publisher: National Building Control Office
   - Local path: `data/raw/bcms_notices.csv` (258 MB, 231,623 rows, 99 cols)
   - Coverage: 2014-present, all 31 Building Control Authorities
   - Cohort-relevant fields:
     - `CN_Planning_Permission_Number` — links to LA planning register
     - `CN_Date_Granted` — date planning permission granted (98.8% populated)
     - `CN_Date_Submitted_or_Received` — date commencement notice filed
     - `CN_Commencement_Date` — actual commencement (100% populated)
     - `CN_Proposed_end_date` — self-declared expected completion
     - `CCC_Date_Validated` — completion-certificate validation date (39.2%)
     - `CCC_Units_Completed` — dwelling units certified in CCC
     - `CN_Total_Number_of_Dwelling_Units` — units declared at commencement
     - `CN_County`, `CN_LAT`, `CN_LNG` — geo
     - `CN_Proposed_use_of_building` — use class (residential_dwelling vs apartments vs non-res)

   Full-cohort residential subset (granted+commence+ccc all populated): 73,829 rows, 138,818 dwelling units.

2. **HSM13 aggregated** (cross-validation)
   - URL: https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/HSM13/JSON-stat/2.0/en
   - Publisher: Dept of Housing / CSO PxStat
   - Local path: `data/raw/HSM13_v2.json`
   - Coverage: 2014 March - present, 32 geographies, monthly
   - Variables: notices for residential development, residential units, one-off residential units

## Secondary / cross-check

3. `ie_housing_pipeline/data/raw/BHQ15.json` (CSO permissions) — to cross-reference permission dates in BCMS against the aggregate permission series.
4. `ie_housing_pipeline/data/raw/BHQ16.json` / `NDA12.json` (CSO completions) — to cross-reference CCC dates against aggregate completion totals.

## Smoke-test verification (2026-04-15)

- HSM13 JSON-STAT v2.0: 144 months × 32 LAs × 3 variables — confirmed loadable.
- BCMS CSV: 258 MB, 231,623 rows, 99 columns — confirmed loadable.
- Residential rows: 190,157. Rows with full granted+commence+ccc timeline: 73,829.

Data access verified before Phase 0 lit review begins. No credentials required.
