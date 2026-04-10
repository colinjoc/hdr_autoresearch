# Data Sources: Iberian Blackout Cascade Prediction

## Primary Data Sources

### 1. ENTSO-E Transparency Platform
- **Name**: ENTSO-E Transparency Platform
- **URL**: https://transparency.entsoe.eu
- **API Documentation**: https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html
- **Size**: ~500 MB for Spain+Portugal 2015-2025 generation+load+flow data
- **License**: Open data (free registration required for API access)
- **Local path**: `data/entsoe_raw/`
- **Download**: Requires API security token (free registration at https://transparency.entsoe.eu)
- **Resolution**: 15-minute for generation/load; 60-minute for cross-border flows
- **Key endpoints**:
  - Actual Generation per Type (A75): generation by fuel type
  - Actual Total Load (A65): system demand
  - Physical Cross-Border Flows (A11): interconnector flows
  - Day-Ahead Prices (A44): market prices
  - Installed Capacity per Type (A68): annual installed capacity
- **Country codes**: Spain = 10YES-REE------0, Portugal = 10YPT-REN------W
- **Note**: API requires registration and has rate limits (400 requests/minute). Bulk download via SFTP available for registered users.

### 2. REE ESIOS API (Red Electrica de Espana)
- **Name**: REE System Operator Information System (ESIOS)
- **URL**: https://www.esios.ree.es/en
- **API Documentation**: https://api.esios.ree.es/
- **Size**: ~200 MB for relevant time series 2015-2025
- **License**: Open data (API token required, free)
- **Local path**: `data/ree_raw/`
- **Download**: `curl -H "Authorization: Token token=YOUR_TOKEN" https://api.esios.ree.es/indicators/INDICATOR_ID`
- **Key indicators**:
  - Indicator 1293: Real-time demand
  - Indicator 1294: Programmed demand
  - Indicator 10035-10050: Generation by type
  - Indicator 600: System frequency (may be limited availability)
- **Note**: Some indicators may have restricted access or limited historical depth.

### 3. ENTSO-E Blackout Report Data Annex
- **Name**: ENTSO-E Expert Panel Final Report on 28 April 2025 Iberian Blackout
- **URL**: https://www.entsoe.eu/publications/blackout/28-april-2025-iberian-blackout/
- **Size**: ~50 MB (report + annexes)
- **License**: Public ENTSO-E publication
- **Local path**: `data/entsoe_report/`
- **Contents**: Event timeline, generation dispatch at time of event, protection relay sequences, frequency recordings during cascade, recommendations
- **Note**: The report explicitly states data was incomplete. Not all oscillographic records were available.

### 4. Open Power System Data
- **Name**: Open Power System Data platform
- **URL**: https://open-power-system-data.org
- **Size**: ~100 MB for time series + power plant datasets
- **License**: Various open licenses (see individual datasets)
- **Local path**: `data/opsd/`
- **Key datasets**:
  - Time series: hourly generation/load for European countries
  - Conventional power plants: plant-level data including capacity and fuel type
  - Renewable power plants: plant-level data for wind and solar
- **Download**: Direct CSV/XLSX download from website
- **Note**: Data may lag behind ENTSO-E by several months. Coverage through 2023 confirmed; 2024-2025 may be incomplete.

### 5. ERA5 Reanalysis
- **Name**: ERA5 hourly data on single levels from 1940 to present
- **URL**: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels
- **Size**: ~1 GB for Iberian Peninsula April 2025 wind/solar variables
- **License**: Copernicus License (free registration required)
- **Local path**: `data/era5/`
- **Variables**: 10m/100m wind speed, surface solar radiation, 2m temperature
- **Resolution**: 0.25 degree, hourly
- **Download**: CDS API (cdsapi Python package)
- **Note**: Used for wind/solar resource reconstruction on blackout day and surroundings. Registration at Copernicus CDS required.

### 6. Thlon & Brozek SSRN 2025
- **Name**: "The Iberian Blackout and Frequency Stability in Power Systems with High RES Penetration"
- **URL**: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5285068
- **Size**: ~5 MB (PDF)
- **License**: Academic publication
- **Local path**: Do not store — reference by URL only
- **Note**: Early academic analysis with independent frequency data analysis.

## Data Availability Summary

| Data Type | Source | Resolution | Coverage | Status |
|-----------|--------|------------|----------|--------|
| Generation by type | ENTSO-E | 15 min | 2015-2025 | Requires API token |
| Total load | ENTSO-E | 15 min | 2015-2025 | Requires API token |
| Cross-border flows | ENTSO-E | 60 min | 2015-2025 | Requires API token |
| Day-ahead prices | ENTSO-E | 60 min | 2015-2025 | Requires API token |
| System frequency | REE ESIOS | varies | varies | May be limited |
| Blackout timeline | ENTSO-E report | event-level | 28 Apr 2025 | Public |
| Wind/solar resource | ERA5 | hourly | 1940-present | Requires CDS account |
| Power plant data | OPSD | annual | through ~2023 | Public download |

## Fallback Strategy

If ENTSO-E API registration is not available or rate limits prevent bulk download:
1. Use Open Power System Data time series as primary source (hourly resolution, coverage through 2023)
2. Supplement with ENTSO-E Transparency Platform web interface manual downloads for 2024-2025
3. Construct synthetic frequency excursion labels from generation ramp rates and SNSP thresholds
4. Document all data gaps explicitly in the paper

## Frequency Data Challenge

True grid frequency data at sub-second resolution is typically not publicly available. Our approach:
1. **Primary**: Attempt to access REE ESIOS frequency indicator
2. **Secondary**: Use 15-minute generation/load data to construct a "frequency stress proxy" based on generation-load imbalance, SNSP, and inertia proxy
3. **Label construction**: Define "frequency excursion > 200 mHz" label from either (a) actual frequency data if available, or (b) historical frequency event reports cross-referenced with generation/load data patterns
