# Data Sources — Xylella Olive Decline Prediction

## 1. Copernicus Sentinel-2 NDVI
- **Name**: Sentinel-2 Level-2A surface reflectance (Band 4 Red, Band 8 NIR for NDVI)
- **URL**: https://dataspace.copernicus.eu/
- **Size**: ~500 MB per tile per date; project uses pre-computed NDVI statistics per municipality
- **License**: Copernicus Open Access (free for all uses)
- **Local path**: `data/sentinel2_ndvi/`
- **Download**: Via Copernicus Data Space API (requires free registration)
- **Notes**: 10 m resolution, 5-day revisit. Tiles T33TYF (Lecce), T33TXF (Brindisi/Taranto), T33TYE (Bari). Spanish tiles T30SYJ (Alicante).

## 2. E-OBS Gridded Climate Data
- **Name**: E-OBS v29.0e daily gridded temperature and precipitation
- **URL**: https://www.ecad.eu/download/ensembles/download.php
- **Size**: ~2 GB for 0.1-degree daily Tmin/Tmax/precip 2010-2025
- **License**: Non-commercial research use
- **Local path**: `data/eobs/`
- **Download**: `wget https://knmi-ecad-assets-prd.s3.amazonaws.com/download/ECA_blend_tg.zip`
- **Notes**: 0.1-degree (~11 km) daily resolution. Variables: TN (daily minimum), TX (daily maximum), RR (daily precipitation).

## 3. EFSA Demarcated Zones (Xylella fastidiosa)
- **Name**: European Food Safety Authority Xylella dashboard and demarcated zone maps
- **URL**: https://efsa.maps.arcgis.com/apps/dashboards/
- **Size**: ~50 MB (shapefiles)
- **License**: EFSA Open Data
- **Local path**: `data/efsa_zones/`
- **Download**: Not programmatically available; timeline reconstructed from EFSA scientific opinions and Italian/Spanish official gazette publications.
- **Notes**: Demarcated zones updated annually. Infected zone + buffer zone boundaries. We use the published timeline of province-level first detections.

## 4. ERA5-Land Reanalysis
- **Name**: ERA5-Land hourly/daily reanalysis
- **URL**: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land
- **Size**: ~1 GB for study area 2010-2025
- **License**: Copernicus Climate Data Store (free registration)
- **Local path**: `data/era5/`
- **Download**: Via CDS API (cdsapi Python package)
- **Notes**: 0.1-degree, hourly. Soil temperature, soil moisture, 2m temperature, 10m wind.

## 5. CORINE Land Cover 2018
- **Name**: Copernicus Land Monitoring Service CORINE Land Cover
- **URL**: https://land.copernicus.eu/pan-european/corine-land-cover/clc2018
- **Size**: ~300 MB (vector)
- **License**: Copernicus Open Access
- **Local path**: `data/corine/`
- **Download**: Direct download from CLMS portal
- **Notes**: Class 223 = Olive groves. Used to identify olive-growing municipalities.

## 6. Italian Municipality Boundaries (ISTAT)
- **Name**: ISTAT administrative boundaries
- **URL**: https://www.istat.it/it/archivio/222527
- **Size**: ~100 MB
- **License**: CC-BY 4.0
- **Local path**: `data/istat/`
- **Notes**: Municipality (comune) and province boundaries for Puglia region.

## 7. Spanish Municipality Boundaries (IGN)
- **Name**: Instituto Geografico Nacional LINEA administrative boundaries
- **URL**: https://centrodedescargas.cnig.es/
- **Size**: ~200 MB
- **License**: CC-BY 4.0
- **Local path**: `data/ign/`
- **Notes**: Municipality boundaries for Comunitat Valenciana.

## Ground Truth Construction

Ground truth is NOT from individual tree measurements. It is constructed from:
1. **EFSA official first-detection dates** at the province/municipality level
2. **Published expansion timeline**: Lecce province (2013), Brindisi (2016), Taranto (2018), Bari (partial by 2021), BAT (2023), Foggia (2025)
3. **Spanish timeline**: Alicante province first detection 2017, expansion through 2024
4. **Binary label**: municipality shows new olive decline (NDVI drop > threshold) within 12 months of prediction date

This is a limitation: the ground truth reflects the administrative detection timeline, not the precise biological onset. The lag between actual infection and administrative detection is estimated at 1-3 years.
