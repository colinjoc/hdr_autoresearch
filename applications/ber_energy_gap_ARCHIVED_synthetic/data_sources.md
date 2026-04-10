# Data Sources: Irish BER vs Real Home Energy Gap

## Primary Dataset: SEAI BER Public Search

- **Name**: SEAI National BER Research Tool (public register of ~1M Building Energy Rating certificates)
- **URL**: https://ndber.seai.ie/BERResearchTool/Register/Register.aspx
- **Size**: ~1M records, ~200 MB as CSV
- **Checksum**: N/A (dynamic database, not a static file)
- **License**: Open Data, SEAI terms of use (non-commercial research permitted)
- **Local path**: `data/ber_certificates.parquet`
- **Download method**: The SEAI BER Research Tool provides a web interface with postback-based pagination (ASP.NET WebForms). No public REST API. Options:
  1. **Manual export**: The tool allows searching by county/year and exporting CSV batches. Rate-limited; full export requires ~26 county queries.
  2. **data.gov.ie**: Partial BER data published at https://data.gov.ie/dataset/ber-public-search — check for bulk download.
  3. **SEAI research access**: Researchers can request the full anonymized dataset via email to ber@seai.ie.
  4. **Synthetic fallback**: If programmatic access is unavailable, generate calibrated synthetic data matching published SEAI summary statistics (BER rating distribution by county, year built, heating type).
- **Schema** (key fields): BER Number, County, Year Built, Floor Area (m2), Wall Type, Wall Insulation, Roof Insulation, Window Type, Heating System, Ventilation Type, BER Rating (A1-G), Energy Value (kWh/m2/yr), CO2 Emissions (kgCO2/m2/yr), Date of Assessment, Assessor ID

## Secondary Dataset: SEAI National Retrofit Reports

- **Name**: SEAI grant scheme data — before/after BER ratings for retrofit projects
- **URL**: https://www.seai.ie/data-and-insights/seai-statistics/
- **Size**: ~50,000-100,000 retrofit records (estimated)
- **License**: Published statistics; individual records may require research agreement
- **Local path**: `data/retrofit_records.parquet`
- **Download method**: Published aggregate statistics available; individual retrofit records may require SEAI research data request

## CSO Ireland Household Energy Data

- **Name**: CSO Household Budget Survey, Census housing data
- **URL**: https://data.cso.ie/
- **Size**: Aggregate statistics by region/year
- **License**: Open Data (CSO Open Data Policy)
- **Local path**: `data/cso_energy.csv`
- **Download method**: CSO PxStat API or bulk CSV download

## Met Eireann Climate Data

- **Name**: Heating Degree Days and climate observations
- **URL**: https://www.met.ie/climate/available-data/historical-data
- **Size**: ~50 MB for station data covering 1961-present
- **License**: Creative Commons Attribution 4.0
- **Local path**: `data/met_eireann_hdd.csv`
- **Download method**: wget from Met Eireann historical data portal

## EPA Ireland Radon Data

- **Name**: EPA radon risk maps and survey results
- **URL**: https://www.epa.ie/environment-and-you/radon/radon-map/
- **Size**: County-level risk estimates
- **License**: Open Data (EPA Ireland)
- **Local path**: `data/epa_radon_risk.csv`
- **Download method**: Manual extraction from EPA radon map viewer

## GSI Tellus Geochemistry

- **Name**: GSI Tellus programme — bedrock geology and geochemistry surveys
- **URL**: https://www.gsi.ie/en-ie/programmes-and-projects/tellus/
- **Size**: Varies by layer
- **License**: Creative Commons Attribution 4.0 (GSI)
- **Local path**: `data/gsi_geology.csv`
- **Download method**: GSI data viewer download

## Data Availability Honest Assessment

The fundamental challenge for this project is that the SEAI BER dataset provides **calculated** (modeled) energy use, not **measured** energy use. The BER Energy Value (kWh/m2/yr) is the output of the DEAP (Dwelling Energy Assessment Procedure) model, which is a standardized calculation based on building characteristics under standard occupancy assumptions. It is NOT a measurement of actual energy bills.

The "performance gap" — the discrepancy between BER-predicted and actual energy use — cannot be directly measured from the BER dataset alone. It requires linking BER certificates to actual metered energy consumption data, which is:
1. Not publicly available at individual dwelling level
2. Held by energy suppliers (ESB Networks, Gas Networks Ireland) under GDPR
3. Available only to approved researchers through the CER Smart Meter Trials (2009-2010, ~5,000 homes) or the SEAI/CSO Household Energy Survey

Our approach: use the BER dataset to understand what predicts the BER Energy Value, identify which building characteristics the DEAP model is most sensitive to, and cross-reference with published performance gap studies (Coyne & Denny 2021) that DID have matched BER + metered data.
