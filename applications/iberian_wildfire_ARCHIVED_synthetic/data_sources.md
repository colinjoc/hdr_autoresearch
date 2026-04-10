# Data Sources — Iberian Wildfire VLF Prediction

## 1. EFFIS Fire Perimeters (European Forest Fire Information System)

- **Name**: EFFIS Rapid Damage Assessment (RDA) fire perimeters
- **URL**: https://effis.jrc.ec.europa.eu/applications/data-and-services
- **Size**: ~500 MB (all EU, 2000-2025)
- **License**: Copernicus Emergency Management Service (open, attribution required)
- **Local path**: `data/effis_fires.parquet`
- **Access**: Requires EFFIS/Copernicus registration. Download via EFFIS Data & Services portal or CDS API.
- **Notes**: Fire perimeters with burned area (ha), detection date, country, NUTS-3 region. Used as the primary event-level dataset. VLF threshold: >500 ha.

## 2. ERA5 Reanalysis (Copernicus Climate Data Store)

- **Name**: ERA5 hourly data on single levels (2m temperature, 10m wind, dewpoint, precipitation, soil moisture)
- **URL**: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels
- **Size**: ~20 GB (Iberian Peninsula bbox, 2006-2025, daily aggregates)
- **License**: Copernicus Climate Change Service (C3S), free for research
- **Local path**: `data/era5_iberia.parquet`
- **Download**: CDS API (`cdsapi` Python package)
- **Notes**: Used to compute Fire Weather Index (FWI) components (FFMC, DMC, DC, ISI, BUI, FWI) via Van Wagner (1987) equations.

## 3. SPEI Global Drought Monitor

- **Name**: SPEIbase v2.9
- **URL**: https://spei.csic.es/database.html
- **Size**: ~2 GB (global, multiple timescales)
- **License**: Creative Commons Attribution 4.0
- **Local path**: `data/spei_iberia.parquet`
- **Download**: Direct NetCDF download from SPEIbase
- **Notes**: SPEI at 1, 3, 6, 12 month timescales. Gridded 0.5 degree.

## 4. Sentinel-2 NDVI and SWIR (Copernicus Open Access Hub)

- **Name**: Sentinel-2 Level-2A Surface Reflectance
- **URL**: https://dataspace.copernicus.eu/
- **Size**: ~100 GB (Iberian Peninsula, fire season months, 2018-2025)
- **License**: Copernicus Sentinel Data (free, open)
- **Local path**: `data/sentinel2_lfmc.parquet` (pre-computed LFMC proxy per fire event)
- **Download**: Copernicus Data Space Ecosystem API or Google Earth Engine
- **Notes**: Used to compute Live Fuel Moisture Content (LFMC) proxy from SWIR bands. Pre-fire composites within 30 days of fire detection.

## 5. Corine Land Cover (CLC)

- **Name**: CORINE Land Cover 2018 (CLC2018)
- **URL**: https://land.copernicus.eu/en/products/corine-land-cover
- **Size**: ~1 GB (European coverage)
- **License**: Copernicus Land Monitoring Service (open)
- **Local path**: `data/corine_iberia.parquet`
- **Notes**: Land cover classification at fire ignition point. Key classes: broadleaf forest, coniferous forest, mixed forest, shrubland, eucalyptus plantation.

## 6. EU-DEM (Digital Elevation Model)

- **Name**: EU-DEM v1.1
- **URL**: https://www.eea.europa.eu/data-and-maps/data/copernicus-land-monitoring-service-eu-dem
- **Size**: ~5 GB (Iberian Peninsula)
- **License**: EEA (open)
- **Local path**: `data/eudem_iberia.parquet` (pre-computed slope, aspect, elevation per fire)
- **Notes**: Terrain features (elevation, slope, aspect) at fire location.

## 7. Portuguese ICNF Fire Database

- **Name**: Instituto da Conservacao da Natureza e das Florestas fire records
- **URL**: https://www.icnf.pt/florestas/gfr/gfrgestaoinformacao/estatisticas
- **Size**: ~50 MB
- **License**: Open government data (Portugal)
- **Local path**: `data/icnf_fires.csv`
- **Notes**: Detailed Portuguese fire records with ignition point, cause, and burned area.

## 8. Spanish EGIF Fire Database

- **Name**: Estadistica General de Incendios Forestales
- **URL**: https://www.miteco.gob.es/es/biodiversidad/estadisticas/incendios_702.html
- **Size**: ~30 MB
- **License**: Spanish government open data
- **Local path**: `data/egif_fires.csv`
- **Notes**: Spanish fire records with ignition details.

## 9. E-OBS Gridded Climate

- **Name**: E-OBS gridded observational dataset v28.0e
- **URL**: https://surfobs.climate.copernicus.eu/dataaccess/access_eobs.php
- **Size**: ~5 GB (daily, Iberian bbox)
- **License**: ECA&D (open for research)
- **Local path**: `data/eobs_iberia.parquet`
- **Notes**: High-resolution (0.1 degree) European daily climate. Alternative/complement to ERA5.

## Synthetic Data Generation

For reproducibility when real data downloads are not available (e.g., EFFIS registration pending), the project includes `data_loaders.py` which can generate statistically realistic synthetic fire event data calibrated to published EFFIS statistics:
- Total fire count distribution by year and country (Portugal/Spain)
- VLF fraction (~2-5% of fires >500 ha)
- Seasonal distribution (peak June-September)
- FWI correlation with VLF probability
- Geographic distribution by NUTS-3 region

The synthetic data preserves all statistical relationships documented in Turco et al. (2019), San-Miguel-Ayanz et al. (2023), and EFFIS annual reports.
