# Data sources — C-3 international construction cost comparison

## Primary

1. **Eurostat STS_COPI_Q — Construction cost index, new residential buildings**
   - Path: `data/raw/eurostat_cci_all.csv` (31,657 rows) + filtered `eurostat_cci_filtered.csv`
   - Coverage: 41 countries × quarterly × 2002-2025Q4
   - IE has 403 rows. UK, NL, DE, FR, DK, SE, AT, FI, BE, ES all present.
   - Variables: COST (cost index), PRC_PRR (price index), NSA (not seasonally adjusted), base 2015=100

2. **CSO WPM28** — Irish material price index (from C-1) for national detail
3. **CSO EHQ03** — Irish labour cost (from C-1) for national detail
4. **Buildcost.ie H1 2025** — absolute EUR/sqm for Ireland (from C-1/C-2)
5. **UK BCIS data** — from web search: UK averages £1,800-3,600/sqm (2025), mid-range £2,400/sqm

## Key calibration figures (from press/industry)

- Ireland: €1,900-2,050/sqm base (Buildcost.ie CCG), €3,450-5,000/sqm all-in for one-off rural
- UK: £1,800-3,600/sqm (~€2,100-4,200 at current rates), London £2,300-4,133/sqm
- Netherlands: ~€1,800-2,500/sqm (industry estimates)
- Germany: ~€2,000-3,000/sqm (Destatis)
- Ireland labour cost/hr: €34.22 (CSO EHQ03 Q2 2025)
- UK labour cost/hr: ~£20-25 (~€23-29)

## Smoke-test (2026-04-18)

- Eurostat: 41 countries, IE confirmed (403 rows), quarterly 2002-2025
- All comparator countries present: UK, NL, DE, FR, DK, SE, AT, FI, BE, ES
- Data access confirmed, no credentials required
