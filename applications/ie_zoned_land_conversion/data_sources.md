# Data sources — U-1 zoned land to application conversion

## Primary

1. **National planning register** (reuse from PL-4)
   - Path: `/home/col/generalized_hdr_autoresearch/applications/ie_lapsed_permissions/data/raw/national_planning_points.csv`
   - 491,206 rows, all applications since 2012, per LA, with ReceivedDate, Decision, GrantDate
   - Gives: applications filed per LA per year, approval rates

2. **CSO BHQ01 — Planning Permissions Granted for New Houses and Apartments**
   - Path: `data/raw/BHQ01.json` (JSON-stat 2.0)
   - 89 LAs × 53 quarters × 4 housing types × 4 statistics
   - Gives: permissions granted per LA per quarter (2001-2014)

3. **CSO RZLPA02 — Residentially Zoned Land Prices 2024**
   - Path: `data/raw/RZLPA02.json`
   - 35 regions × 8 statistics (transactions, volume, value, median/mean price per hectare)
   - Gives: zoned land transaction activity and prices by county

4. **Goodbody September 2024 report** — "Residential Land Availability"
   - 7,911 hectares of residentially zoned, serviced land with no active planning nationally
   - Regional split: East+Midlands 33% (~2,611 ha), Southern 26% (~2,057 ha), Northern+Western 40% (~3,164 ha)
   - 417,000 potential units estimated
   - Only 1/6 of zoned land activated during a 6-year Development Plan cycle
   - Fingal specific: 3,519 hectares in-scope (from Fingal RZLT map)

5. **2014 Residential Land Availability Survey**
   - Department of Environment: 17,434 hectares nationally of undeveloped residential zoned land
   - Comparison: 17,434 ha (2014) → 7,911 ha (2024) — land consumed or rezoned

## Cross-validation
- CSO BHQ15 (permissions aggregate) from predecessor projects
- BCMS commencement data from PL-1

## Smoke-test verification (2026-04-17)
- BHQ01: 89 LAs × 53 quarters — confirmed loadable
- RZLPA02: 35 regions × 8 stats × 1 year — confirmed loadable
- National register: 491k rows — confirmed (from PL-4)
- Goodbody report accessible at goodbody.ie (not downloadable as CSV; figures manually extracted from press coverage)

Data access confirmed. No credentials required.
