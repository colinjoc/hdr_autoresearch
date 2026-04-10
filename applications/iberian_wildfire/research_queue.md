# Research Queue — Iberian Wildfire VLF Prediction

## Status Legend
- OPEN: not yet tested
- KEPT: tested, improved performance, retained
- REVERTED: tested, did not improve, reverted
- TESTED: tested, results recorded but neutral impact

## Hypotheses (100+)

### FWI Component Analysis (E40-E50)
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 1 | Removing FWI hurts most of any single feature | 70% | TESTED | CV drops 0.018 — FWI is important |
| 2 | Removing ISI hurts less than removing FWI | 60% | TESTED | Confirmed, ISI less important alone |
| 3 | Removing DC is harmless (redundant with SPEI) | 50% | TESTED | Marginal impact, DC somewhat redundant |
| 4 | Removing NDVI hurts (vegetation greenness matters) | 55% | TESTED | CV drops 0.027 — NDVI matters |
| 5 | Removing elevation doesn't hurt (terrain effect is weak) | 40% | TESTED | Removing elevation slightly improves holdout |

### LFMC as Competing Predictor (E01, E56, E57, Phase 2.5)
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 6 | LFMC alone outpredicts FWI alone | 55% | **KEPT** | LFMC AUC 0.725 > FWI AUC 0.701 |
| 7 | Adding LFMC to FWI improves prediction | 60% | **KEPT** | FWI+LFMC AUC 0.793 vs FWI 0.701 |
| 8 | LFMC + FWI + SPEI-6 is best trio | 50% | **KEPT** | AUC 0.807 best single-predictor combo |
| 9 | LFMC below 80% is a critical threshold | 40% | TESTED | Binary threshold doesn't help (E24) |
| 10 | LFMC seasonal anomaly better than raw | 35% | REVERTED | Anomaly worse than raw (E66) |

### SPEI Multi-Timescale (E02-E04, E58-E61)
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 11 | Adding SPEI-1 improves over SPEI-6 alone | 40% | **KEPT** | Contributes to best config |
| 12 | Adding SPEI-3 captures seasonal drought | 45% | **KEPT** | Contributes to best config |
| 13 | Adding SPEI-12 captures annual water balance | 40% | **KEPT** | Contributes to best config |
| 14 | SPEI-6 is more important than SPEI-1 | 60% | TESTED | Removing SPEI-6 hurts more than removing SPEI-1 |
| 15 | All 4 SPEI timescales together is optimal | 45% | **KEPT** | CV 0.664 with all 4 SPEI |

### Wind and Temperature Effects
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 16 | FWI * wind interaction captures wind amplification | 50% | REVERTED | No CV improvement (E17) |
| 17 | temp * wind interaction captures hot wind | 45% | TESTED | Marginal (E19) |
| 18 | Wind > 30 km/h binary threshold | 40% | REVERTED | No improvement (E23) |
| 19 | Wind^2 captures nonlinear spread | 35% | REVERTED | No improvement (E21) |
| 20 | VPD outpredicts raw temp + RH | 45% | REVERTED | Redundant (E69) |

### Land Cover and Vegetation
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 21 | Eucalyptus fraction improves VLF prediction | 55% | TESTED | Improves with tuned model (E05, E62) |
| 22 | Land cover type categorical feature | 40% | OPEN | Not tested individually |
| 23 | Pre-fire NDVI anomaly | 35% | OPEN | Not tested |
| 24 | Eucalyptus * FWI interaction | 30% | OPEN | Not tested |
| 25 | Mixed forest vs monoculture | 30% | OPEN | Not tested |

### Terrain
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 26 | Slope improves prediction (uphill fire spread) | 50% | **KEPT** | In base features |
| 27 | Aspect captures south-facing drying | 30% | REVERTED | No signal (E13) |
| 28 | Elevation * temperature interaction | 25% | OPEN | Not tested |
| 29 | Slope > 20 deg threshold | 30% | OPEN | Not tested |
| 30 | Canyon terrain indicator | 25% | OPEN | Not tested |

### Temporal and Operational
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 31 | Detection hour (afternoon fires worse) | 40% | REVERTED | No CV gain (E07) |
| 32 | Concurrent fire count (suppression exhaustion) | 50% | TESTED | Helps with tuned model (E62) |
| 33 | Day of year (sub-monthly seasonality) | 30% | REVERTED | Redundant with month (E15) |
| 34 | Heatwave consecutive days > 35C | 45% | REVERTED | No CV gain (E08) |
| 35 | Night temperature (overnight drying) | 40% | REVERTED | No CV gain (E09) |
| 36 | Previous year precipitation (fuel load) | 35% | REVERTED | No signal (E10) |
| 37 | Weekend/holiday effect (ignition patterns) | 20% | OPEN | Not tested |
| 38 | Fire season week number | 25% | OPEN | Not tested |

### Model Architecture
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 39 | XGBoost depth=4 beats depth=6 | 40% | **KEPT** | CV 0.668 vs 0.654 (E31) |
| 40 | scale_pos_weight=10 improves recall | 50% | TESTED | Improves F2 but hurts AUC |
| 41 | scale_pos_weight=25 too aggressive | 50% | TESTED | Confirmed (E35, E54) |
| 42 | LightGBM beats XGBoost | 30% | REVERTED | XGBoost better (E36 vs E04) |
| 43 | ExtraTrees beats XGBoost | 35% | TESTED | Yes, CV 0.685 (E37) |
| 44 | Ridge beats all trees | 30% | **KEPT** | Ridge CV 0.699 best overall |
| 45 | Lower learning rate + more trees | 40% | TESTED | Marginal (E33, E74) |
| 46 | Logistic regression with L2 | 40% | **KEPT** | Ridge is the winner |

### WUI and Interface
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 47 | WUI distance improves prediction | 35% | REVERTED | No signal (E11) |
| 48 | Soil moisture anomaly | 30% | REVERTED | No signal (E12) |
| 49 | Country indicator (PT vs ES) | 25% | REVERTED | No improvement (E14) |
| 50 | Portugal-specific eucalyptus model | 25% | OPEN | Not tested |

### Cross-Feature Interactions
| # | Hypothesis | Prior | Status | Result |
|---|-----------|-------|--------|--------|
| 51 | LFMC * FWI interaction | 35% | REVERTED | No improvement (E18) |
| 52 | SPEI-6 * LFMC interaction | 30% | REVERTED | No improvement (E22) |
| 53 | All three binary risk indicators | 30% | REVERTED | No improvement (E26) |
| 54 | Combined binary+interactions | 25% | REVERTED | E52 no improvement |
| 55 | KB drought proxy | 30% | REVERTED | No improvement (E70) |
| 56 | FWI percentile within month | 25% | REVERTED | No improvement (E68) |
| 57 | Temperature anomaly from monthly | 30% | REVERTED | No improvement (E67) |

### Additional Hypotheses (not yet tested)
| # | Hypothesis | Prior | Status |
|---|-----------|-------|--------|
| 58 | Fire weather type classification (synoptic patterns) | 35% | OPEN |
| 59 | NAO index as predictor | 30% | OPEN |
| 60 | Sea surface temperature anomaly | 25% | OPEN |
| 61 | Antecedent fire density in 30-day window | 40% | OPEN |
| 62 | Fuel break density in municipality | 25% | OPEN |
| 63 | Distance to nearest road (access for suppression) | 30% | OPEN |
| 64 | Population density at fire location | 25% | OPEN |
| 65 | Fire cause (arson vs natural vs accidental) | 35% | OPEN |
| 66 | Lightning activity in preceding 48h | 30% | OPEN |
| 67 | Relative greenness from NDVI anomaly | 30% | OPEN |
| 68 | Bioregion classification | 25% | OPEN |
| 69 | MODIS active fire count in surrounding area | 35% | OPEN |
| 70 | Fire radiative power at detection | 40% | OPEN |
| 71 | Atmospheric stability index | 30% | OPEN |
| 72 | Wind gust speed (not mean) | 40% | OPEN |
| 73 | Humidity recovery overnight | 35% | OPEN |
| 74 | Consecutive dry days count | 40% | OPEN |
| 75 | Fuel age since last fire | 35% | OPEN |
| 76 | Leaf area index from satellite | 30% | OPEN |
| 77 | Snow cover in preceding winter | 20% | OPEN |
| 78 | Spring precipitation anomaly | 35% | OPEN |
| 79 | Fire perimeter shape at 6 hours | 30% | OPEN |
| 80 | Elevation gradient in 5km radius | 25% | OPEN |
| 81 | River/water body proximity | 20% | OPEN |
| 82 | Fire size at 1 hour as early warning | 45% | OPEN |
| 83 | Diurnal temperature range | 30% | OPEN |
| 84 | Cloud cover at detection | 20% | OPEN |
| 85 | Multi-day FWI accumulation (3-day mean) | 35% | OPEN |
| 86 | FWI rate of change (day-over-day) | 30% | OPEN |
| 87 | Fraction of fires > 10 ha in past week | 35% | OPEN |
| 88 | Municipal fire history (fires per decade) | 30% | OPEN |
| 89 | Distance to water source for aerial suppression | 25% | OPEN |
| 90 | Vegetation continuity index | 30% | OPEN |
| 91 | Crown closure percentage | 25% | OPEN |
| 92 | Fuel model classification | 35% | OPEN |
| 93 | Thermal belt indicator (inversion layer) | 20% | OPEN |
| 94 | Dust/aerosol optical depth | 15% | OPEN |
| 95 | Upper-level jet stream position | 20% | OPEN |
| 96 | Geopotential height 500 hPa anomaly | 25% | OPEN |
| 97 | Atlantic blocking index | 25% | OPEN |
| 98 | Soil type (sandy vs clay) | 20% | OPEN |
| 99 | Canopy height from LiDAR | 25% | OPEN |
| 100 | Power line proximity (ignition source) | 20% | OPEN |
| 101 | Stacking ensemble (Ridge + XGBoost) | 35% | OPEN |
| 102 | Calibrated probability from Platt scaling | 30% | OPEN |
| 103 | Two-stage model: fire occurrence then VLF given fire | 40% | OPEN |
| 104 | Separate models for Portugal and Spain | 30% | OPEN |
| 105 | Seasonal model (separate summer/non-summer) | 30% | OPEN |
