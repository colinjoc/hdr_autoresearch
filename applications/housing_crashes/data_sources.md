# Data Sources — Housing Market Crash Prediction

All sources public, no credentials required. Smoke-tested 2026-04-14.

## 1. Zillow Home Value Index (primary price series)

- **URL**: `https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfr_tier_0.33_0.67_sm_sa_month.csv` (4.4 MB)
- **Coverage**: ~900 US metros, monthly, 2000-01 → present
- **Methodology**: Zillow's ZHVI, smoothed, seasonally-adjusted, single-family tier 0.33–0.67 (i.e. the middle third of market — excludes ultra-luxury/cheap)
- **Role**: primary outcome (crash event) + most of the features (momentum, acceleration, level)

## 2. FRED Case-Shiller and supplementary indices

- **Case-Shiller National**: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=CSUSHPISA` (monthly)
- **20-city composite**: `CSUSHPINSA` (not seasonally adjusted)
- **Per-metro**: `ATNHPIUS12420Q` style series IDs per MSA
- **30-year fixed mortgage rate**: `MORTGAGE30US` (weekly)
- **Role**: cross-validation of the ZHVI outcome; mortgage rate as macro covariate

## 3. Realtor.com monthly inventory

- **URL**: `https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Metro_History.csv`
- **Coverage**: ~500 metros, monthly, 2016-07 → present
- **Fields**: active listing count, median days on market, new listings, price reductions, median listing price
- **Role**: lead indicators — inventory build-up and median-days-on-market historically precede price declines by 3-9 months

## 4. Census ACS median household income

- **API**: `https://api.census.gov/data/2022/acs/acs5?get=NAME,B19013_001E&for=metropolitan%20statistical%20area/micropolitan%20statistical%20area:*`
- **Coverage**: annual, 5-year rolling MSAs, ~930 MSAs, 2009 → present
- **Role**: denominator for price-to-income ratio (the canonical Shiller-Case bubble signal)

## 5. Census Building Permits Survey (to be URL-refreshed)

- **Landing**: `https://www.census.gov/econ/bps/`
- **Coverage**: monthly metro-level new housing units authorised; 1988 → present
- **Role**: supply elasticity proxy — Glaeser-Gyourko (2005) argues supply-constrained metros crash deeper

## 6. FHFA HPI (to be URL-refreshed)

- **Landing**: `https://www.fhfa.gov/DataTools/Downloads/Pages/House-Price-Index.aspx`
- **Role**: independent cross-check of Case-Shiller / ZHVI; covers more metros and all counties

## 7. Smoke-test results (2026-04-14)

```
FRED Case-Shiller national          → 200 OK, CSV
Zillow ZHVI metro (4.4 MB)          → 200 OK, CSV
Realtor.com inventory metro         → 200 OK, CSV (S3)
Census ACS median income API        → 200 OK, JSON
FHFA HPI                            → 404 (URL refresh needed in Phase 0)
Census Building Permits Survey      → 404 (URL refresh needed in Phase 0)
```

All primary sources are public and working. FHFA + BPS are secondary —
defer URL refresh to Phase 0.5 data pull.

## 8. Crash definition (to be finalised in Phase 0)

Candidate definitions for the treatment variable `y_metro_t = 1 iff "metro m crashes in window [t, t+h]"`:

- **Classical**: peak-to-trough ≥20% decline in Case-Shiller (Shiller 2005)
- **Rolling**: 12-month trailing ZHVI return ≤ −10%
- **Rapid**: 6-month trailing ZHVI return ≤ −7% (captures fast 2022-era crashes)
- **Deep**: eventual 24-month peak-to-trough ≥ 15%

Pre-registered primary: **12-month trailing ZHVI return ≤ −10%** (binary per metro-month). Robustness variants tested in Phase 2.

## 9. Minimal viable first pull

- **Scope**: all ~500 Realtor.com metros (inventory-complete), 2016-07 → 2024-12
- **Volume**: ~42k metro-months after join, ~30 MB cached parquet
- **Wall-clock**: ~5 min if all four sources are cached
