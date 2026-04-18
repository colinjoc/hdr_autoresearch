# Data sources — UFO-2 AARO case resolution analysis

## Primary

1. **AARO FY2024 Consolidated Annual Report on UAP**
   - Path: `data/raw/aaro_fy2024_dni.txt` (649 lines, extracted from PDF)
   - Source: DNI via defense.gov (November 2024)
   - Coverage: May 2023 - June 2024 + all prior unreported cases
   - Key figures: 757 new cases received, 118 resolved (all prosaic), 21 merit IC analysis, 1,600+ cumulative

2. **ODNI 2022 Annual Report on UAP**
   - Path: `data/raw/odni_2022.txt` (400 lines)
   - Coverage: FY2022
   - Earlier baseline for trend comparison

3. **AARO Historical Record Report Volume 1** (March 2024)
   - NOT successfully fetched (defense.gov 403/404)
   - Key claim from press: "no evidence of extraterrestrial activity" across historical review
   - Will use press-reported figures from web search

## Extractable data from FY2024 report

- Total cases received: 757
- Cases resolved during period: 49 (all prosaic)
- Total resolved to date: 118
- Resolution categories: balloons, birds, UAS, satellites, aircraft
- Cases meriting IC/S&T analysis: 21
- Reporting sources: 392 from USSPACECOM; remainder DoD/IC
- Morphologies reported (in report figures)
- UAS near nuclear sites (flagged as emerging concern)
- No cases substantiate advanced adversarial capabilities or extraterrestrial origin

## Supplementary (from web search / press)

- 1,600+ cumulative reports to AARO
- Pentagon: "discovered no evidence of extraterrestrial beings, activity or technology"
- New AARO chief (2024) committed to transparency
- Congressional hearings 2023-2024 testimony (Grusch, Graves, Fravor)

## Smoke-test (2026-04-18)

- AARO FY2024: 649 lines extracted, key numbers grep-verified
- ODNI 2022: 400 lines extracted
- Historical V1: access blocked, will use secondary sources
- Data sufficient for a structured analysis of resolution patterns, though limited to aggregate report-level data (no individual case records publicly available)
