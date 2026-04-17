# Data sources — U-2 development viability frontier

## Primary

1. **CSO HPM09 — Residential Property Price Index (monthly, by region)**
   - Path: `data/raw/HPM09.json` — 20 regions × 254 months × 4 statistics
   - Gives: sale price trends by region (Dublin, outside Dublin, by property type)

2. **CSO HPA06 — Residential Property Price Index (annual, by region)**
   - Path: `data/raw/HPA06.json` — 20 regions × 21 years × 2 statistics
   - Cross-validates HPM09 at annual granularity

3. **CSO BEA04 — Building & Construction Production Index**
   - Path: `data/raw/BEA04.json` — 5 sectors × 25 years × 4 statistics (value/volume, raw/SA)
   - Includes "Residential building" as a separate sector
   - INDEX not absolute EUR — use buildcost.ie for calibration

4. **Buildcost.ie Construction Cost Guide H1 2025**
   - Path: `data/raw/buildcost_2025h1.pdf` + `.txt` (1.9 MB)
   - Absolute EUR/sqm for different build types — the calibration anchor for BEA04 index

5. **CSO RZLPA02 — Residentially Zoned Land Prices 2024**
   - Path: `data/raw/RZLPA02.json` — 35 counties × 8 statistics
   - Gives: median/mean land price per hectare by county — the land-cost component

6. **CSO NDQ04 — ESB Connections**
   - Path: `data/raw/NDQ04.json` — quarterly, 2011-present
   - Completion proxy (new dwelling connections)

## Secondary / context

- **Central Bank of Ireland** — "Rising construction costs and the residential real estate market in Ireland" (PDF available)
- **SCSI Tender Price Index** — 1.5% H1 2025, 3.0% YoY
- **S-1 predecessor** — build-yield 59.6%, permissions needed 85k/yr

## Viability equation

Sale Price > Land Cost/unit + Construction Cost/sqm × avg sqm + Finance Cost + Dev Contributions + Profit Margin (~15-20%)

If this inequality fails for a given county, development is unviable there.

## Smoke-test verification (2026-04-17)
- HPM09: 20 regions × 254 months — confirmed
- HPA06: 20 regions × 21 years — confirmed
- BEA04: 5 sectors × 25 years — confirmed
- RZLPA02: 35 counties × 8 stats — confirmed
- Buildcost PDF: 1.9 MB — confirmed

Data access confirmed. No credentials required.
