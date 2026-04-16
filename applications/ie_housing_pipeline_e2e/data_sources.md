# Data Sources — IE Housing Pipeline E2E

## Primary Data Sources

### 1. BCMS Commencement Notices (PL-1)
- **Source**: Building Control Management System (BCMS), National Building Control Office (NBCO)
- **URL**: https://www.localgov.ie/en/link-type/bcms (public download via localgov.ie)
- **File**: `ie_commencement_notices/data/raw/bcms_notices.csv`
- **Coverage**: All building-control filings from 1 March 2014 (BCAR 2014 commencement) to April 2026
- **Schema**: 97 columns including planning permission number, grant date, commencement date, CCC validation date, local authority, dwelling units, building type, project type (opt-out vs standard), AHB flag
- **Rows**: 285,140 total; 184,133 residential after filtering
- **Smoke test**: PASS — 85,565 residential rows for 2014-2019 cohort

### 2. National Planning Register (PL-4)
- **Source**: MyPlan.ie / Local Government Open Data, operated by each Planning Authority
- **URL**: https://data.gov.ie/dataset/national-planning-applications (Ordnance Survey Ireland / data.gov.ie)
- **File**: `ie_lapsed_permissions/data/raw/national_planning_points.csv`
- **Coverage**: All planning applications across 31 Local Authorities, 1998-2026
- **Schema**: 39 columns including planning authority, application number, decision, grant date, expiry date, NumResidentialUnits, application type
- **Rows**: 536,141 total; 66,163 granted residential PERMISSION applications for 2014-2019
- **Smoke test**: PASS — NRU>0 2017-2019 subset yields 19,593 rows matching PL-4 E15

### 3. CSO BHQ15 — Planning Permissions Granted (PL-0)
- **Source**: Central Statistics Office PxStat
- **URL**: https://data.cso.ie/table/BHQ15
- **File**: `ie_housing_pipeline/data/raw/BHQ15.json`
- **Coverage**: Quarterly planning permissions 2019-2025, with SHD/non-SHD split
- **Format**: JSON-stat 2.0
- **Smoke test**: PASS — 2019 total matches known 38,461

### 4. CSO NDA12 — New Dwelling Completions (PL-0)
- **Source**: Central Statistics Office PxStat
- **URL**: https://data.cso.ie/table/NDA12
- **File**: `ie_housing_pipeline/data/raw/NDA12.json`
- **Coverage**: Annual new dwelling completions by urban area 2012-2025
- **Format**: JSON-stat 2.0
- **Smoke test**: PASS — 2023 towns total matches 24,316

### 5. LDA Delivery Data (PL-3)
- **Source**: LDA 2023 Annual Report; Irish Times September 2025 reporting
- **URL**: https://lda.ie/publications/annual-reports/
- **File**: `ie_lda_delivery/results.tsv`
- **Coverage**: 2023 audited (ca. 850 homes), cumulative through end-2024 (~2,054)
- **Smoke test**: PASS — matches LDA 2023 report verbatim

## Data Reuse Note

All datasets are reused from predecessor projects. No new downloads required.
The synthesis joins PL-4 (all permissions) with PL-1 (commenced permissions) conceptually
via the stage-by-stage attrition model rather than a row-level record linkage,
because the predecessor PL-4 project demonstrated that fuzzy matching between
the planning register and BCMS introduces substantial confounding (27.4% vs 9.5% lapse rate
depending on match method).
