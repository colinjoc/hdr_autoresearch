# Data sources — U-3 infrastructure capacity blocks

## Primary

1. **Uisce Éireann Wastewater Treatment Capacity Register (scraped)**
   - Path: `data/raw/wastewater_capacity.csv` (1,063 WWTP rows × 8 columns)
   - Scraped from per-county HTML pages at water.ie
   - Capacity status: GREEN (790, 74%), AMBER (109, 10%), RED (164, 15%)
   - 29 counties covered (DLR and South Dublin included under Dublin)
   - Fields: region, county, settlement, wwtp, reg_no, capacity (GREEN/AMBER/RED), project_planned

2. **National planning register** (reuse from PL-4)
   - Path: `/home/col/generalized_hdr_autoresearch/applications/ie_lapsed_permissions/data/raw/national_planning_points.csv`
   - 491,206 rows — join by settlement/county to link applications to WWTP capacity

3. **CSO NDQ04 — ESB Connections** (completion proxy)
   - Path: `data/raw/NDQ04.json` (already fetched in U-2)

4. **Zoned land estimates from U-1**
   - 7,911 ha nationally; Goodbody regional splits
   - Question: how much of this sits in RED/AMBER catchments?

5. **CSO BHQ01 — Permissions by LA** (from U-1)
   - Already at `/home/col/generalized_hdr_autoresearch/applications/ie_zoned_land_conversion/data/raw/BHQ01.json`

## Context

- Predecessor: U-1 zoned land conversion (4.8 apps/ha/yr ex-Fingal)
- Predecessor: U-2 viability frontier (83% of zoned land economically stranded)
- Predecessor: S-3 bottleneck ranking (permission volume is #1)

## Smoke-test verification (2026-04-17)

- 1,063 WWTP records parsed from 29 county pages (all HTTP 200 except DLR/South Dublin which are under Dublin)
- GREEN/AMBER/RED classification extracted from inline CSS color spans
- Cross-check: 74% GREEN nationally matches Uisce Éireann's public statement that "most treatment plants have capacity"

Data access confirmed. No credentials required.
