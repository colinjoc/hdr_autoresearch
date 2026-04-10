# Data Sources: Irish Radon Prediction

## 1. EPA Ireland Radon Map — High Radon Area Designations

- **Name**: EPA Radon Map of Ireland
- **URL**: https://www.epa.ie/environment-and-you/radon/radon-map/
- **Size**: ~5 MB (shapefile/CSV of grid squares with HRA classification)
- **Format**: GeoJSON/Shapefile with 10km grid squares; each square has: % predicted >200 Bq/m3, HRA designation (yes/no), number of measurements, mean radon
- **License**: Open Government License — Ireland
- **Local path**: `data/epa_radon_map.geojson`
- **Download**: Manual export from EPA interactive map, or via EPA open data portal
- **Notes**: This is our primary target variable source. Individual home measurements are restricted (privacy), but area-level statistics are public. The 10km grid is the coarsest resolution; some data may be available at Electoral Division level from published papers.

## 2. GSI Tellus Airborne Radiometric Data

- **Name**: Tellus Airborne Radiometric Survey
- **URL**: https://www.gsi.ie/en-ie/programmes-and-projects/tellus/Pages/Data-Downloads.aspx
- **Size**: ~500 MB - 2 GB (GeoTIFF grids or point data)
- **Format**: GeoTIFF raster grids at ~50-100m resolution. Bands: equivalent Uranium (eU, ppm), equivalent Thorium (eTh, ppm), Potassium (K, %). Also available as point data (CSV/shapefile) at ~200m line spacing.
- **License**: Creative Commons Attribution 4.0 (CC-BY-4.0)
- **Local path**: `data/tellus_radiometric/` (eU.tif, eTh.tif, K.tif)
- **Download**: `wget https://gsi.geodata.gov.ie/downloads/Tellus/Radiometrics/` (check exact URL on GSI data downloads page)
- **Notes**: This is the key geological predictor dataset. eU is the single strongest predictor of indoor radon. Coverage: entire Republic of Ireland. Coordinate system: Irish Transverse Mercator (ITM, EPSG:2157).

## 3. GSI Bedrock Geology 1:100,000

- **Name**: Bedrock Geology of Ireland
- **URL**: https://www.gsi.ie/en-ie/data-and-maps/Pages/Bedrock.aspx
- **Size**: ~100 MB (shapefile)
- **Format**: Shapefile with polygon geometries. Key fields: LEX_CODE (lithology code), ROCK_CLASS (igneous/sedimentary/metamorphic), ROCK_DESC (description), AGE, FORMATION
- **License**: CC-BY-4.0
- **Local path**: `data/bedrock_geology.shp`
- **Download**: Via GSI open data portal or WMS/WFS service
- **Notes**: ~500 distinct lithology codes. Need to aggregate into radon-relevant classes (granite, limestone, shale, sandstone, etc.).

## 4. GSI Quaternary (Subsoil) Geology

- **Name**: Quaternary Geology Map of Ireland
- **URL**: https://www.gsi.ie/en-ie/data-and-maps/Pages/Quaternary.aspx
- **Size**: ~80 MB (shapefile)
- **Format**: Shapefile with polygon geometries. Key fields: QUAT_CODE (quaternary classification), DESCRIPTION
- **License**: CC-BY-4.0
- **Local path**: `data/quaternary_geology.shp`
- **Download**: Via GSI open data portal
- **Notes**: Key classes: Till (thick), Till (thin), Sand and Gravel, Alluvium, Peat, Rock at surface, Lacustrine. Acts as permeability modifier on bedrock radon signal.

## 5. SEAI BER Public Search Database

- **Name**: National BER Database (public subset)
- **URL**: https://ndber.seai.ie/BERResearchTool/Register/Register.aspx
- **Size**: ~1 GB (CSV/Excel, ~1 million records)
- **Format**: CSV with ~50+ columns per certificate including: county, dwelling type, year built, floor area, wall type, insulation type, U-values, heating type, ventilation type, air permeability, BER rating, energy value (kWh/m2/yr), CO2 emissions
- **License**: Research use via SEAI agreement; public summary statistics available
- **Local path**: `data/ber_certificates.parquet`
- **Download**: Via SEAI BER Research Tool (requires registration) or public API
- **Notes**: Critical for building feature extraction. Key fields: air_permeability (airtightness proxy), floor_type (suspended timber vs slab), ventilation_type, ber_rating (A1-G), year_built. County-level aggregation needed to match radon data.

## 6. CSO Small Area Population Statistics

- **Name**: Census 2022 Small Area Population Statistics
- **URL**: https://www.cso.ie/en/census/census2022/
- **Size**: ~50 MB
- **Format**: CSV with Small Area boundaries (shapefile), population counts, housing characteristics
- **License**: Open Government License — Ireland
- **Local path**: `data/cso_small_areas/`
- **Notes**: Provides the spatial unit for risk mapping. ~18,000 Small Areas in Ireland. Population weighting for risk prioritization.

## 7. Met Éireann Climate Data

- **Name**: Historical climate data
- **URL**: https://www.met.ie/climate/available-data/historical-data
- **Size**: ~200 MB
- **Format**: CSV with station-level daily/monthly data: temperature, rainfall, wind speed, sunshine hours
- **License**: Open Government License — Ireland
- **Local path**: `data/met_eireann/`
- **Notes**: For climate features (wind speed affects ventilation, rainfall affects soil moisture and radon transport). Need spatial interpolation to grid/Small Area level.

## 8. OSi Building Footprints and Elevation

- **Name**: Ordnance Survey Ireland Open Data
- **URL**: https://data-osi.opendata.arcgis.com/
- **Size**: ~1 GB
- **Format**: GeoJSON/Shapefile
- **License**: CC-BY-4.0
- **Local path**: `data/osi/`
- **Notes**: Building footprints for spatial matching. Digital elevation model for slope/aspect features.

## Data Integration Strategy

The analysis operates at two spatial resolutions:
1. **Electoral Division (ED) level** (~3,400 EDs): Where EPA radon data is most reliably aggregated. Each ED gets: mean Tellus radiometric values, predominant bedrock code, predominant quaternary code, mean BER characteristics, climate normals, elevation stats.
2. **Small Area (SA) level** (~18,000 SAs): For fine-grained risk mapping in Phase B. SAs are nested within EDs.

All spatial data is reprojected to Irish Transverse Mercator (ITM, EPSG:2157) for analysis.

## Synthetic Data Strategy

Since individual-level EPA radon measurements are restricted and the Tellus GeoTIFF downloads require manual acquisition, this project generates calibrated synthetic data that reproduces the published statistical relationships. The synthetic data is calibrated to:
- Fennell et al. (2002, 2021) national radon statistics
- Elío et al. (2020, 2022) geology-radon correlations
- SEAI (2023) BER database summary statistics
- GSI bedrock and quaternary classification schemes

The synthetic data generator is designed to be replaceable: when real data becomes available, the `load_dataset()` function switches from synthetic to real data with no changes to the model or evaluation code.
