# Research Queue — Xylella Olive Decline Prediction

## Status Legend
- OPEN: not yet tested
- KEEP: tested, kept (improved score)
- REVERT: tested, reverted (no improvement)
- DONE: completed, results recorded

## Tested Hypotheses

| # | Hypothesis | Prior | Status | Result | Exp |
|---|---|---|---|---|---|
| 1 | dist_nearest_declining_km improves prediction (diffusion proxy) | 70% | KEEP | +0.013 AUC | E01 |
| 2 | log(dist_nearest_declining) captures nonlinear distance decay | 40% | REVERT | -0.001 AUC | E02 |
| 3 | log(dist_epicentre) adds to raw distance | 35% | REVERT | -0.004 AUC | E03 |
| 4 | already_affected flag adds signal beyond distance | 50% | KEEP | +0.004 AUC | E04 |
| 5 | frost_days_below_minus6 (vector kill threshold) | 45% | REVERT | -0.005 AUC | E05 |
| 6 | frost_days_below_minus12 (bacterial kill threshold) | 40% | REVERT | -0.001 AUC | E06 |
| 7 | winter_tmin_abs (absolute cold extreme) | 35% | REVERT | -0.013 AUC | E07 |
| 8 | coldest_month_anomaly (unusual cold) | 30% | REVERT | -0.004 AUC | E08 |
| 9 | frost_severity_index (combined frost measure) | 50% | KEEP | +0.0001 AUC | E09 |
| 10 | ndvi_trend (temporal NDVI derivative) | 75% | KEEP | +0.053 AUC | E10 |
| 11 | ndvi_anomaly (departure from mean) | 55% | KEEP | +0.001 AUC | E11 |
| 12 | ndvi_std (canopy heterogeneity) | 45% | KEEP | +0.006 AUC | E12 |
| 13 | evi_mean (alternative vegetation index) | 30% | REVERT | -0.002 AUC | E13 |
| 14 | ndvi_decline_rate (relative decline) | 40% | REVERT | -0.001 AUC | E14 |
| 15 | summer_precip_mm (drought stress) | 50% | KEEP | +0.003 AUC | E15 |
| 16 | precip_deficit_frac (moisture deficit) | 35% | REVERT | -0.019 AUC | E16 |
| 17 | ndvi_x_jan_tmin interaction | 45% | KEEP | +0.002 AUC | E17 |
| 18 | aridity_proxy (precip/PET ratio) | 30% | REVERT | -0.007 AUC | E18 |
| 19 | lat_from_salento (latitude proxy) | 25% | REVERT | -0.0003 AUC | E19 |
| 20 | greenup_proxy (phenological timing) | 35% | REVERT | -0.007 AUC | E20 |
| 21 | soil_moisture_proxy | 30% | REVERT | -0.0001 AUC | E21 |
| 22 | province_ordinal (south-to-north encoding) | 20% | REVERT | -0.009 AUC | E22 |
| 23 | country indicator | 25% | REVERT | -0.007 AUC | E23 |

## Remaining OPEN Hypotheses

### Climate Features
| # | Hypothesis | Prior | Notes |
|---|---|---|---|
| 24 | Winter Tmin range (max-min across Dec-Feb) | 25% | Captures variability, not just mean |
| 25 | Growing degree days above 12C (Xf growth threshold) | 35% | Integrates warmth over season |
| 26 | Consecutive frost-free days | 30% | Vector activity window length |
| 27 | Spring Tmin (March-April mean) | 25% | Vector emergence timing |
| 28 | Wind speed (ERA5-Land) | 15% | Vector dispersal aid |
| 29 | Humidity (ERA5-Land specific humidity) | 20% | Vector survival in humid conditions |
| 30 | Soil temperature (ERA5-Land) at 0-7cm | 30% | Root zone temperature; dormancy |

### NDVI / Remote Sensing
| 31 | NDVI percentile 10th (worst condition) | 35% | Captures drought/disease floor |
| 32 | NDVI seasonal amplitude | 30% | Phenological disruption signal |
| 33 | NDVI trend acceleration (2nd derivative) | 25% | Accelerating decline |
| 34 | Red Edge NDVI (Sentinel-2 Band 5) | 30% | More sensitive to chlorophyll changes |
| 35 | NDWI (Normalized Difference Water Index) | 25% | Water stress proxy |
| 36 | LAI (Leaf Area Index from Sentinel-2) | 30% | Canopy density change |
| 37 | NDVI difference (current year - 2 years ago) | 40% | Short-term change |
| 38 | Max NDVI date shift | 25% | Phenological shift indicator |

### Spatial / Diffusion
| 39 | Expansion rate (km/year local estimate) | 40% | Local front velocity |
| 40 | Olive grove connectivity (nearest neighbor count) | 35% | Stepping-stone density |
| 41 | Road distance to nearest affected area | 25% | Human-mediated transport |
| 42 | Coastal vs interior indicator | 20% | Adriatic coast expansion is faster |
| 43 | Buffer zone status (EFSA) | 30% | Regulatory containment indicator |
| 44 | Spatial lag of NDVI decline (neighbors' trend) | 45% | Contagion signal |
| 45 | Directional distance (south-to-north only) | 30% | Expansion is directional |

### Landscape
| 46 | DEM aspect (N/S facing slope) | 20% | Microclimate effect on frost |
| 47 | DEM slope | 15% | Drainage, vector habitat |
| 48 | Forest cover fraction | 20% | Alternative host reservoir |
| 49 | Urbanization fraction | 15% | Fragmentation effect |
| 50 | Irrigated fraction | 25% | Irrigated groves may resist drought stress |

### Temporal
| 51 | Years since first detection in province | 40% | Time-since-infection proxy |
| 52 | Rate of province-level expansion | 35% | Regional velocity |
| 53 | Seasonal NDVI phase (harmonic fit) | 25% | Phenological disruption |
| 54 | Inter-annual NDVI variance | 30% | Instability indicator |

### Model Configuration
| 55 | LightGBM instead of XGBoost | 30% | Marginal in tournament |
| 56 | ExtraTrees (bagging approach for small N) | 20% | High variance in tournament |
| 57 | Increase n_estimators to 500 | 25% | More trees, possible overfit |
| 58 | Decrease max_depth to 4 | 25% | Regularization |
| 59 | Increase min_child_weight to 5 | 25% | Regularization |
| 60 | Lower learning_rate to 0.01, more estimators | 20% | Slower but potentially better |

### Interaction Features
| 61 | dist_nearest_declining * ndvi_trend | 40% | Proximity + decline interaction |
| 62 | frost_severity * dist_epicentre | 30% | Climate barrier at distance |
| 63 | elevation * jan_tmin | 25% | Altitude-temperature coupling |
| 64 | olive_area_fraction * dist_nearest_declining | 35% | Host density at frontier |
| 65 | summer_precip * ndvi_mean | 25% | Drought-health coupling |
| 66 | ndvi_trend * ndvi_std | 30% | Decline rate * heterogeneity |

### Target Engineering
| 67 | Multi-year target (2-year decline window) | 30% | Broader prediction horizon |
| 68 | Severity target (continuous NDVI drop) | 25% | Regression instead of classification |
| 69 | Calibrated probability output | 35% | Isotonic regression calibration |

### Cross-Country Transfer
| 70 | Train only on Italian data, test on Spanish | 40% | Transfer learning test |
| 71 | Country-specific models | 30% | Separate Italian/Spanish models |
| 72 | Add domain adaptation features | 20% | Explicitly bridge country differences |

### Ensemble
| 73 | XGBoost + LightGBM blend | 35% | Ensemble of top-2 |
| 74 | Stacking with logistic meta-learner | 25% | More complex ensemble |
| 75 | Temporal ensemble (models from different prediction years) | 20% | Multi-temporal prediction |

### Additional Climate
| 76 | Palmer Drought Severity Index | 25% | Standard drought index |
| 77 | De Martonne aridity index | 20% | Classic aridity measure |
| 78 | Heating degree days (below 12C) | 25% | Bacterial dormancy proxy |
| 79 | Chilling hours (0-7C) | 25% | Olive phenology trigger |
| 80 | Maximum temperature (heatwave risk) | 20% | Heat stress on vector/host |

### Mechanistic
| 81 | Estimated time to front arrival (distance/20 km/yr) | 45% | Simple diffusion prediction |
| 82 | Climate suitability score (from EFSA envelope) | 35% | Literature-derived suitability |
| 83 | Vector abundance proxy (GDD for P. spumarius) | 30% | Insect phenology model |
| 84 | Xylem flow rate proxy (Tmax * precip) | 15% | Bacterial transport |
| 85 | Tree age proxy | 10% | Older trees more susceptible? |

### Validation
| 86 | Leave-one-province-out CV | 35% | Alternative spatial CV scheme |
| 87 | Temporal split (train on 2013-2020, test 2021-2024) | 40% | Time-forward validation |
| 88 | Permutation feature importance | 30% | Model interpretation |
| 89 | SHAP value analysis | 35% | Feature interaction analysis |
| 90 | Confidence interval estimation | 25% | Uncertainty quantification |

### Data Augmentation
| 91 | Add Sardinia as negative control (olive groves, no Xf) | 30% | Expand negative class |
| 92 | Add Corsica (detected 2015) | 25% | Additional diffusion data |
| 93 | Add Mallorca (detected 2016) | 30% | Island dynamics |
| 94 | Historical NDVI from Landsat (pre-2015) | 20% | Longer time series |
| 95 | MODIS LST for frost proxy | 25% | Higher temporal resolution |

### Advanced
| 96 | Spatial autocorrelation feature (Moran's I of NDVI) | 25% | Spatial clustering signal |
| 97 | Graph neural network on municipality adjacency | 10% | Spatial deep learning |
| 98 | Survival analysis formulation | 20% | Time-to-event instead of binary |
| 99 | Bayesian spatial model (INLA) | 15% | Principled spatial inference |
| 100 | Convolutional features from NDVI raster | 15% | Spatial texture features |

### Prediction Horizon
| 101 | 6-month prediction window | 25% | Shorter horizon, tighter signal |
| 102 | 24-month prediction window | 25% | Longer horizon, more uncertainty |
| 103 | Rolling 3-year average features | 30% | Smoothed temporal features |
| 104 | Seasonal prediction (spring vs autumn risk) | 20% | Temporal risk profile |
| 105 | Multi-step prediction (chain 1-year models) | 20% | Iterative forecasting |
