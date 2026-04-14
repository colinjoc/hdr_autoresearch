# Data Sources — YC vs Non-YC Outperformance

All sources are public, no credentials required. Smoke-tested 2026-04-14.

## 1. YC company directory (treated cohort)

- **Mirror**: https://yc-oss.github.io/api/companies/all.json (yc-oss/api, daily-refreshed mirror of ycombinator.com/companies)
- **Rows**: 5,690 companies
- **Fields**: `id, name, slug, batch, status (Active/Inactive/Acquired/Public), stage, team_size, industries[], regions[], launched_at, long_description, website, all_locations`
- **Coverage**: S05 (first batch, 2005) through current year.
- **Role**: treated cohort; `batch` encodes funding quarter (S = Summer/Q3, W = Winter/Q1).

## 2. SEC EDGAR Form D filings (control cohort + raise amounts)

- **Full-text search API**: https://efts.sec.gov/LATEST/search-index?forms=D&dateRange=custom&startdt=...&enddt=...
- **Quarterly full index**: https://www.sec.gov/Archives/edgar/full-index/{YYYY}/QTR{1-4}/form.idx (~46 MB)
- **Headers required**: `User-Agent: <name> <email>` (SEC rule, or 403).
- **Key fields in primary_doc.xml**: `totalOfferingAmount, minimumInvestmentAccepted, typeOfFiler, issuer.name, industryGroup`
- **Role**: universe of private-market seed/Series-A raises; control pool + raise-size covariate for treated companies.

## 3. SEC EDGAR outcome filings

- Subsequent Form D (same CIK, later date) → follow-on raise
- 8-K (item 2.01) → acquisition / merger
- S-1 or 8-A12B → IPO registration
- All via `https://data.sec.gov/submissions/CIK{10-digit}.json`

## 4. Smoke-test results

```
yc-oss all.json                 → 200, 9.5 MB, 5690 rows
SEC full-index 2019 Q1          → 200, 46 MB
SEC full-text search            → 200, JSON, working
SEC CIK submissions (no UA)     → 403 (expected)
SEC CIK submissions (with UA)   → [not yet tested, pending]
```

## 5. Matched-pair design

- **Treated**: YC batch ∈ {S05..W24}; ~5,690 treated companies
- **Control**: Form D filings same quarter, `totalOfferingAmount` within ±50 % of YC average for batch, `typeOfFiler` / `industryGroup` consistent
- **Match ratio**: 1 YC : 5 non-YC (nearest-neighbour on propensity score)
- **Covariates**: quarter, industry, raise amount band, location metro (from issuer address)
- **Outcomes (T+5 y)**: {survived, raised_again, acquired, IPO, defunct}
- **Exposure**: binary (YC batch attended) — propensity-score-matched

## 6. Known confounds

- YC self-selection: smartest/scrappiest founders apply → baseline selection effect
- Geographic: YC concentrates in SF Bay Area; control pool is national
- Sector: YC historically over-indexes SaaS vs broader Form D universe
- Time trend: late-stage private capital environment shifted markedly 2021→2023
