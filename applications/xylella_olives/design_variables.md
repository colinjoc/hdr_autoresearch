# Design Variables — Xylella Olive Decline Prediction

## Feature → Computable Proxy Mapping

| # | Domain Variable | Computable Proxy | Source | Units | Physics Justification |
|---|---|---|---|---|---|
| 1 | Olive grove health | ndvi_mean | Sentinel-2 B4/B8 | dimensionless 0-1 | Chlorophyll absorption in red, leaf reflectance in NIR; healthy canopy = high NDVI |
| 2 | Health trajectory | ndvi_trend | Linear fit to NDVI time series | NDVI/year | Declining NDVI indicates progressive xylem blockage and canopy desiccation |
| 3 | Health anomaly | ndvi_anomaly | Departure from multi-year mean | NDVI units | Identifies abnormal years controlling for seasonal cycle |
| 4 | Canopy heterogeneity | ndvi_std | Std dev of pixel-level NDVI | NDVI units | Patchy decline = high std; uniform canopy = low std |
| 5 | Vegetation robustness | evi_mean | Enhanced Vegetation Index | dimensionless | Less atmospheric sensitivity than NDVI; captures canopy structure |
| 6 | Relative decline rate | ndvi_decline_rate | ndvi_trend / ndvi_mean | per year | Normalizes decline by baseline health |
| 7 | Winter cold stress | jan_tmin_mean | E-OBS TN January mean | degrees C | Bacterial and vector survival threshold |
| 8 | Absolute cold extreme | winter_tmin_abs | Coldest recorded temperature | degrees C | Acute frost kill of bacteria or vectors |
| 9 | Vector frost risk | frost_days_below_minus6 | Count(Tmin < -6C) | days/winter | P. spumarius mortality threshold (~-6C) |
| 10 | Bacterial cold-curing | frost_days_below_minus12 | Count(Tmin < -12C) | days/winter | Xf in-planta death threshold (~-12C) |
| 11 | Combined frost severity | frost_severity_index | frost_days_-6 + 3*frost_days_-12 | composite | Weights severe frost (bacterial kill) higher than moderate frost (vector stress) |
| 12 | Coldest month departure | coldest_month_anomaly | Departure from 1991-2020 mean | degrees C | Identifies unusually cold or warm winters |
| 13 | Annual moisture | annual_precip_mm | E-OBS RR annual sum | mm | Drought stress weakens tree defenses |
| 14 | Summer drought | summer_precip_mm | E-OBS RR Jun-Aug sum | mm | Summer drought = maximum water stress + peak vector activity |
| 15 | Moisture deficit | precip_deficit_frac | Fraction below normal | dimensionless | Identifies drought years |
| 16 | Aridity | aridity_proxy | Precip / simplified PET | dimensionless | Integrates temperature and precipitation |
| 17 | Spatial proximity | dist_epicentre_km | Haversine to Lecce/Alicante | km | Diffusion model: distance from origin of epidemic |
| 18 | Frontier proximity | dist_nearest_declining_km | Nearest affected municipality | km | Diffusion model: proximity to active decline front |
| 19 | Already affected | already_affected | Binary: province detected | 0/1 | Whether the pathogen is administratively confirmed present |
| 20 | Olive density | olive_area_fraction | CORINE class 223 area | fraction | Host density affects transmission probability |
| 21 | Topography | elevation | DEM mean | metres | Colder at altitude; different microclimate |
| 22 | Position | latitude, longitude | Centroid | degrees | Geographic gradients; proxy for many unmeasured variables |
| 23 | Vegetation-frost interaction | ndvi_x_jan_tmin | NDVI * January Tmin | composite | Tests whether cold effects are amplified in already-stressed groves |
| 24 | Phenological timing | greenup_proxy | Estimated green-up DOY | day of year | Earlier green-up = longer vector exposure window |
| 25 | Latitude proxy | lat_from_salento | Latitude - 40.0 | degrees | Distance north from Salento epicentre |
| 26 | Soil moisture | soil_moisture_proxy | Annual precip - 3*summer precip | mm | Approximates water balance |

## Final Model Feature Set (16 features)

After the HDR loop, 8 base + 8 added features are retained:

**Base (8):** latitude, longitude, elevation, jan_tmin_mean, annual_precip_mm, ndvi_mean, dist_epicentre_km, olive_area_fraction

**Added (8):** dist_nearest_declining_km, already_affected, frost_severity_index, ndvi_trend, ndvi_anomaly, ndvi_std, summer_precip_mm, ndvi_x_jan_tmin

**Reverted (15):** log_dist_nearest_declining, log_dist_epicentre, frost_days_below_minus6, frost_days_below_minus12, winter_tmin_abs, coldest_month_anomaly, evi_mean, ndvi_decline_rate, precip_deficit_frac, aridity_proxy, lat_from_salento, greenup_proxy, soil_moisture_proxy, province_ordinal, country
