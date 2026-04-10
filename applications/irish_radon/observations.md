# Observations: Irish Radon Prediction

## Data Summary
- **820** 10km grid squares from EPA radon map (real measurements from ~63,914 homes)
- **692** grid squares with Tellus radiometric coverage (pseudo-values from RGB-encoded GeoTIFFs)
- **27** counties for spatial CV grouping
- **53** features after engineering (radiometric, bedrock, subsoil, geographic, interactions)
- Target: % homes above 200 Bq/m3 per grid square (continuous, 0-54%)
- HRA threshold: >=10% defines a High Radon Area

## Data Sources (ALL REAL)
1. EPA Radon Grid Map: radon_grid_map.geojson (16 MB, 10km grid squares with % homes > 200 Bq/m3)
2. GSI Bedrock Geology 500K: shapefiles (ITM, ~500 lithology units)
3. EPA National Subsoils: subsoils.geojson (151 MB, quaternary sediment types)
4. GSI Tellus Airborne Radiometrics: 5 GeoTIFFs (eU, eTh, K, TC, Ternary) at 50m resolution
5. EPA County Boundaries: counties.geojson (for spatial CV grouping)
6. EPA County Radon Statistics: hard-coded from EPA website (63,914 homes measured)

## Tellus Radiometric Processing
The Tellus GeoTIFFs (RAD_MERGE_2022) are RGB-encoded color maps (uint8 x 3 bands), not raw radiometric data in ppm. The color ramp maps from blue (R=0, B=247, low value) to red (R=247, B=0, high value). We extract a pseudo-radiometric index as (R - B + 247) / 494, giving a [0, 1] range that preserves the monotonic ordering of the underlying physical measurements. This is sampled at 5x5 sub-grid points within each 10km grid square.

## Phase 0.5 Baseline
- Ridge regression on 21 features (Tellus + geology + subsoil + geographic)
- Spatial CV (grouped by county, 10 folds): MAE = 7.33 +/- 1.49, HRA F1 = 0.29
- This is a reasonable linear baseline that already captures the geology-radon relationship

## Phase 1 Tournament
| Model | MAE | MAE std | HRA F1 |
|---|---|---|---|
| Ridge | 7.33 | 1.49 | 0.29 |
| XGBoost | 6.58 | 1.31 | 0.47 |
| LightGBM | 6.53 | 1.53 | 0.47 |
| ExtraTrees | 6.94 | 1.42 | 0.46 |
| Random Forest | 6.64 | 1.44 | 0.43 |

- LightGBM and XGBoost are nearly tied; XGBoost selected for consistency
- All tree models substantially outperform Ridge baseline
- HRA F1 ~0.47 on spatial CV is the honest baseline (no county leakage)

## Phase 2 HDR Loop
| Experiment | Description | MAE | HRA F1 | Kept |
|---|---|---|---|---|
| E05 | XGBoost + Tellus derived features | 6.45 | 0.49 | Yes |
| E07 | LightGBM + enhanced features | 6.49 | 0.49 | No |
| E08 | XGBoost tuned (500 trees, lr=0.03) | 6.44 | 0.48 | Yes |
| E09 | XGBoost + interaction features | 6.48 | 0.48 | Yes |
| E10 | XGBoost full (interactions + one-hot bedrock) | 6.42 | 0.47 | Yes (BEST) |

Best model: XGBoost with 53 features (MAE=6.42, HRA F1=0.47)

## Key Findings

### 1. Geology is the dominant predictor
The top features are all geological:
- Carboniferous limestone shelf facies: 18.4% importance
- Bedrock age (Caledonian): 12.9%
- Granite x Till interaction: 6.5%
- Ordovician/Silurian bedrock: 4.9%
- eU x Granite interaction: 4.3%

### 2. Tellus radiometric data adds value
Adding eU-derived features improved MAE from 6.58 to 6.45 (2.0% reduction).
The eU/eTh ratio and uranium variability (eU_std) are the most informative derived features.

### 3. Interaction features reveal hidden structure
The `granite_x_till` interaction (granite bedrock overlain by granitic till) has 6.5% importance - the third most important feature. This captures the physical reality that granitic till is derived from uranium-rich parent rock and provides permeable transport pathways.

### 4. Spatial CV is essential
Our spatial CV (county-grouped) gives MAE ~6.4 and HRA F1 ~0.47, which is substantially lower than what random CV would give. This is the honest performance estimate, avoiding the inflated metrics (AUC 0.78-0.82) reported in prior work that used standard CV.

### 5. County-level variation is large
Hardest counties to predict:
- Sligo (MAE=12.1): Complex geology with high variability
- Carlow (MAE=11.9): Leinster Granite edge effects
- Louth (MAE=10.6): Transition zone

Easiest counties:
- Kerry (MAE=2.8): Uniform high-radon from Namurian shales
- Kildare (MAE=3.6): Uniform low-radon from limestone

## Feature Importance (Final Model, Top 15)
1. Carboniferous limestone facies: 0.184
2. Caledonian bedrock age: 0.129
3. Granite x Till interaction: 0.065
4. Ordovician/Silurian bedrock: 0.049
5. eU x Granite interaction: 0.043
6. Granite bedrock unit: 0.040
7. Mullaghmore/Downpatrick facies: 0.030
8. Carboniferous Mississippian age: 0.027
9. Southern Highland pelites: 0.025
10. Log uranium (eU): 0.020
11. Shale-derived till: 0.018
12. eU/eTh ratio: 0.019
13. Cork Group marine: 0.018
14. Longitude (easting): 0.023
15. Uranium variability (eU_std): 0.017

## Summary
- 12.3% improvement from Ridge baseline (MAE 7.33) to best model (MAE 6.42)
- The honest spatial CV metric is ~6.4 MAE points (% homes above reference level)
- Geology (bedrock type + age + subsoil interactions) dominates prediction
- Tellus radiometric features add measurable but secondary improvement
- The granite-till interaction is a novel finding: areas where uranium-rich granite has deposited granitic till create highest radon risk
