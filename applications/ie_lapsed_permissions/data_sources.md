# Data sources — PL-4 lapsed / unbuilt permissions study

## Primary

1. **National Planning Application register** (row-level, every Irish planning application since ~2012)
   - URL: `https://data-housinggovie.opendata.arcgis.com/api/download/v1/items/8f69dffe26324ba3acc653cf6cb5cf8b/csv?layers=0`
   - Publisher: Dept of Housing, Local Government and Heritage
   - Local path: `data/raw/national_planning_points.csv` (290 MB, 491,206 rows, 39 cols)
   - Coverage: 2012-2026 (ETL_DATE 2026-04-14)
   - Key fields for lapse analysis:
     - `Application Number` — matches BCMS `CN_Planning_Permission_Number`
     - `Planning Authority` — 31 LAs
     - `Application Type` — PERMISSION / RETENTION / OUTLINE PERMISSION
     - `Decision` — CONDITIONAL / GRANT PERMISSION / REFUSED
     - `GrantDate` — date permission was granted (317,041 populated)
     - `ExpiryDate` — 5-year default expiry (168,191 populated)
     - `NumResidentialUnits` — scheme size
     - `One-Off House` — flag
   - Smoke-test summary:
     - Total rows: 491,206
     - Rows with GrantDate: 317,041
     - Rows with ExpiryDate: 168,191
     - Top app types: PERMISSION (286k), RETENTION (46k), OUTLINE (10k)
     - Top decisions: CONDITIONAL (232k), GRANT PERMISSION (58k), REFUSED (32k)

2. **BCMS row-level dataset** (for matching permissions against commencement)
   - Reuse from PL-1: `/home/col/generalized_hdr_autoresearch/applications/ie_commencement_notices/data/raw/bcms_notices.csv`
   - `CN_Planning_Permission_Number` is the matching key.
   - 231,623 rows, 183,633 residential with GrantDate populated.

3. **CSO BHQ15 permissions aggregated** (cross-validation)
   - Reuse from PL-1/housing pipeline: `/home/col/generalized_hdr_autoresearch/applications/ie_housing_pipeline/data/raw/BHQ15.json`

## Context / secondary

- **Planning and Development Act 2000 Sections 42 & 43** — Section 42 = extension-of-duration, valid 5 years default, extendable up to 5 years.
- **Planning and Development (Amendment) Act 2025 Section 28** — inserts new provisions allowing un-commenced extensions of up to 3 additional years for one-or-more houses.
- **Section 42 extension data** — no national aggregated dataset; must either (a) use BCMS non-appearance as proxy for "did not commence", which conflates truly-lapsed with extended-but-not-yet-commenced; or (b) scrape individual LA registers. We will use (a) with explicit caveat.

## Smoke-test verification (2026-04-15)

- National register: 491,206 rows fetched (HTTP 200, 290 MB); GrantDate and ExpiryDate fields confirmed; matching key `Application Number` confirmed.
- BCMS: previously verified; 183,633 residential rows with CN_Planning_Permission_Number.
- Match test: joining `Application Number` ↔ `CN_Planning_Permission_Number` produces non-empty intersection (exact match-rate will be an E01 experiment).

Data access confirmed. No credentials required.
