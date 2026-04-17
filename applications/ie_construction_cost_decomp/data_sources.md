# Data sources — C-1 construction cost decomposition

## Primary

1. **CSO WPM28 — Wholesale Price Index for Building & Construction Materials**
   - Path: `data/raw/WPM28.json` (JSON-stat 2.0)
   - 40 material categories × 117 months (Jan 2015 - Sep 2025) × 3 statistics (index, MoM%, YoY%)
   - Categories include: concrete/cement, structural steel, timber, insulation, electrical, plumbing, HVAC, glass, paints

2. **CSO EHQ03 — Average Earnings, Hours Worked, Employment and Labour Costs**
   - Path: `data/raw/EHQ03.json`
   - Construction sector (NACE F) separately identifiable
   - Quarterly, ~2007-2025
   - Gives: hourly labour cost, hours worked, employment count for construction

3. **Buildcost.ie Construction Cost Guides**
   - `data/raw/buildcost_2025h1.pdf` + `.txt` — H1 2025, absolute EUR/sqm by trade
   - `data/raw/buildcost_2024h2.pdf` + `.txt` — H2 2024, for comparison
   - Breakdown by: substructure, frame, upper floors, roof, stairs, external walls, windows, internal walls, finishes, fittings, services (mechanical, electrical, lift), site works, preliminaries

4. **CSO BEA04 — Building & Construction Production Index**
   - Path: `data/raw/BEA04.json`
   - Residential building as separate sector, 2000-2024, value and volume indices

## Key calibration figures (from SCSI / press)

- Hard costs = 53% of total nationally; 49% in Dublin (soft costs = 47% / 51%)
- Labour cost per hour construction: €34.22 Q2 2025 (up from €30.85 Q2 2024 = +10.9% YoY)
- WPM28 All Materials Index: +0.9% YoY annual average 2025
- Building & Construction Index (materials + wages): +2.0% YoY 2025
- Concrete/cement: +3-5%/yr; Timber: -7%/yr; Steel: -8%/yr
- SCSI Tender Price Index: +3.0% YoY (H1 2025)

## Cross-reference

- U-2 viability frontier: construction cost 10x more sensitive than land cost
- S-3 bottleneck: permission volume #1; construction capacity #2

## Smoke-test verification (2026-04-18)

- WPM28: 40 categories × 117 months confirmed
- EHQ03: construction sector identifiable, quarterly data confirmed
- Buildcost PDFs: both extracted to text
- Data access confirmed, no credentials required
