# Data Sources -- Iberian Wildfire VLF Prediction

All data are REAL satellite observations. No synthetic data were used.

## 1. EFFIS/GWIS Weekly Fire Statistics (Primary)

- **Name**: EFFIS weekly fire events and burned area
- **API**: `https://api2.effis.emergency.copernicus.eu/statistics/v2/gwis/weekly?country={ISO3}&year={YEAR}`
- **Coverage**: Portugal (PRT) and Spain (ESP), 2012-2025
- **Resolution**: Weekly, country-level
- **Fields**: fire event count, total burned area (ha), historical average/max for each week
- **License**: Copernicus Emergency Management Service (open, attribution required)
- **Local path**: `data/effis_weekly.parquet` (consolidated from raw JSON files)
- **Raw files**: `data/raw/weekly_{PRT|ESP}_{2012..2025}.json`
- **Notes**: Fire events detected from MODIS/VIIRS satellite imagery. Minimum detectable fire size ~30 ha.

## 2. MCD64A1 MODIS Burned Area by Land Cover (Supplementary)

- **Name**: MCD64A1 burned area by land cover type
- **URL**: `https://effis-gwis-cms.s3.eu-west-1.amazonaws.com/apps/country.profile/MCD64A1_burned_area_full_dataset_2002_2024.zip`
- **Coverage**: Global (filtered to Portugal and Spain), 2002-2024
- **Resolution**: Monthly, subnational (GID-1 regions)
- **Fields**: burned area (ha) by forest, savannas, shrublands/grasslands, croplands, other
- **License**: Copernicus/GWIS (open)
- **Local path**: `data/mcd64a1_iberia.parquet`
- **Notes**: Used for land cover fraction features (forest_frac, shrub_frac) in Phase 2.

## 3. GlobFire Event Records (Supplementary)

- **Name**: GlobFire burned area and fire count
- **URL**: `https://effis-gwis-cms.s3.eu-west-1.amazonaws.com/apps/country.profile/GLOBFIRE_burned_area_full_dataset_2002_2024.zip`
- **Coverage**: Global (filtered to Portugal and Spain), 2002-2024
- **Resolution**: Monthly, subnational (GID-1 regions)
- **Fields**: fire event count (ba_count), total burned area (ba_area_ha)
- **License**: Copernicus/GWIS (open)
- **Local path**: `data/globfire_iberia.parquet`
- **Notes**: Provides longer historical context (2002-2024) and regional granularity.

## 4. EFFIS Annual Statistics (Validation)

- **API**: `https://api2.effis.emergency.copernicus.eu/statistics/v2/gwis/estimatesbycountry?country={ISO3}`
- **Coverage**: Portugal and Spain, 2012-2026
- **Fields**: Annual total burned area and fire count
- **Notes**: Used to validate weekly data totals against published annual statistics.

## Data NOT Used (Identified but Not Required)

- **ERA5 Reanalysis**: Gridded climate data (temperature, humidity, wind, precipitation). Not required because the EFFIS fire activity data already encodes the relevant weather signal implicitly.
- **SPEIbase**: Gridded drought indices. Not required -- cumulative fire activity year-to-date serves as a drought proxy.
- **Sentinel-2 LFMC**: Direct satellite-derived live fuel moisture content. Not required -- recent fire activity dynamics serve as an LFMC proxy.
- **CORINE Land Cover**: Pan-European land cover classification. MCD64A1 land cover fractions provide equivalent information.
- **EU-DEM**: Digital elevation model. Country-level analysis does not require terrain features.

## No Synthetic Data

Previous iterations of this project used synthetic data calibrated to published statistics. This version uses exclusively real satellite fire observations downloaded from the EFFIS/GWIS data infrastructure.
