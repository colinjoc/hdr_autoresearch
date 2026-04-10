# Research Queue — DART Punctuality Cascade Prediction

## Status Legend
- **KEEP**: Tested, improved CV AUC above noise floor, retained in model
- **REVERT**: Tested, did not improve or regressed
- **OPEN**: Not yet tested
- **SKIP**: Skipped (data not available or redundant with tested hypothesis)

## Hypotheses

### Weather Features (H001-H010)
| ID | Hypothesis | Prior | Status | Delta |
|---|---|---|---|---|
| H001 | Wind >50 km/h binary threshold predicts bad days (Bray-Greystones speed restrictions) | 65% | **KEEP** | +0.008 |
| H002 | Rainfall >10mm binary threshold predicts bad days (adhesion, signal failures) | 50% | **KEEP** | +0.005 |
| H003 | Morning-afternoon punctuality gap captures cascade propagation | 70% | **KEEP** | +0.012 |
| H004 | Rolling 7-day bad day rate as system health proxy | 45% | **KEEP** | +0.004 |
| H005 | Post-timetable x wind interaction (reduced buffers amplify weather) | 60% | **KEEP** | +0.015 |
| H006 | School term indicator (passenger load proxy) | 40% | **KEEP** | +0.003 |
| H007 | Previous bad day x Monday interaction | 35% | **KEEP** | +0.002 |
| H008 | Wind direction coastal exposure (easterlies worst for Bray-Greystones) | 55% | **KEEP** | +0.006 |
| H009 | Rolling 3-day punctuality (shorter cascade memory) | 40% | **KEEP** | +0.004 |
| H010 | Holiday flag (bank holidays = different demand) | 30% | **REVERT** | -0.001 |

### Weather Interactions (H011-H016)
| ID | Hypothesis | Prior | Status | Delta |
|---|---|---|---|---|
| H011 | Wind direction x speed product | 45% | **REVERT** | +0.001 |
| H012 | Month x timetable interaction | 50% | **REVERT** | +0.000 |
| H013 | Reduce max_depth from 5 to 4 | 30% | **REVERT** | -0.003 |
| H014 | Increase n_estimators to 300 | 25% | **REVERT** | +0.000 |
| H015 | Previous week punctuality (weekly autocorrelation) | 45% | **REVERT** | +0.001 |
| H016 | Frost x wind interaction | 40% | **REVERT** | +0.002 |

### Training Improvements (H017-H026)
| ID | Hypothesis | Prior | Status | Delta |
|---|---|---|---|---|
| H017 | Exponentially weighted rolling mean | 35% | **REVERT** | -0.001 |
| H018 | Days since last bad day counter | 50% | **REVERT** | +0.001 |
| H019 | Scale_pos_weight for class imbalance | 35% | **REVERT** | +0.000 |
| H020 | Consecutive bad day counter | 50% | **REVERT** | +0.001 |
| H021 | Monday-after-weekend-bad interaction | 30% | **REVERT** | +0.000 |
| H022 | Rainfall x wind product | 40% | **REVERT** | +0.001 |
| H023 | Reduce learning rate to 0.02 | 25% | **REVERT** | -0.002 |
| H024 | Reduce colsample_bytree to 0.6 | 25% | **REVERT** | +0.000 |
| H025 | Year x timetable interaction | 30% | **REVERT** | +0.001 |
| H026 | Increase min_child_weight to 10 | 30% | **KEEP** | +0.003 |

### Diminishing Returns (H027-H040)
| ID | Hypothesis | Prior | Status | Delta |
|---|---|---|---|---|
| H027 | Day-of-week x timetable interaction | 25% | **REVERT** | +0.000 |
| H028 | Temperature x wind interaction | 35% | **REVERT** | +0.001 |
| H029 | Dark morning proxy | 30% | **REVERT** | +0.000 |
| H030 | 3-day cumulative rainfall | 40% | **REVERT** | +0.002 |
| H031 | Subsample to 0.7 | 20% | **REVERT** | -0.001 |
| H032 | Mean wind 3-day rolling | 30% | **REVERT** | +0.001 |
| H033 | Max depth to 6 | 25% | **REVERT** | +0.000 |
| H034 | Peak season (Oct-Jan) flag | 40% | **REVERT** | +0.001 |
| H035 | Morning punct x wind interaction | 50% | **REVERT** | +0.002 |
| H036 | Post-change x rain interaction | 45% | **REVERT** | +0.001 |
| H037 | Day-of-week x morning punct interaction | 35% | **REVERT** | +0.000 |
| H038 | Switch to LightGBM | 40% | **REVERT** | +0.002 |
| H039 | Rolling 14-day punctuality | 25% | **REVERT** | +0.000 |
| H040 | Rolling 7-day max wind | 30% | **REVERT** | +0.001 |

### Not Tested — Data Unavailable (H041-H060)
| ID | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H041 | Connolly junction conflict count | 55% | SKIP | Requires signal box logs |
| H042 | Fleet availability (number of operational units) | 60% | SKIP | Not published |
| H043 | Passenger count at morning peak | 50% | SKIP | Requires smart card data |
| H044 | InterCity delay as DART delay predictor | 45% | SKIP | Requires separate GTFS-RT collection |
| H045 | Platform occupation time at Connolly | 55% | SKIP | Requires signal data |
| H046 | Crew roster pattern (driver shortages) | 50% | SKIP | Not published |
| H047 | Engineering works schedule | 45% | SKIP | Published ad hoc, not machine-readable |
| H048 | Level crossing activation frequency | 35% | SKIP | TII data not linked to rail delays |
| H049 | Luas-DART interchange delay | 30% | SKIP | Requires Luas GTFS-RT |
| H050 | Dublin Bus congestion as proxy for rail demand | 35% | SKIP | Requires bus GTFS-RT |
| H051 | Tidal height (sea wall overtopping at Bray Head) | 45% | SKIP | Available from Marine Institute, not collected |
| H052 | Air quality index (fog proxy) | 25% | SKIP | Weak signal expected |
| H053 | DART+ Phoenix Park tunnel traffic | 40% | SKIP | Service not yet operational in data period |
| H054 | Single-track section occupancy at Bray-Greystones | 55% | SKIP | Requires signal data |
| H055 | Dwell time at Tara Street (congestion proxy) | 50% | SKIP | Requires GTFS-RT |
| H056 | Short-formation running (fewer carriages) | 45% | SKIP | Requires fleet data |
| H057 | Planned vs actual headway variance | 50% | SKIP | Requires GTFS-RT + static |
| H058 | Speed restriction duration (wind warning periods) | 40% | SKIP | Requires Irish Rail internal data |
| H059 | Sunrise/sunset timing (darkness effect on operations) | 30% | SKIP | Testable but expected weak |
| H060 | Sports event calendar (GAA, rugby, concerts) | 40% | SKIP | Machine-readable calendar not built |

### Theoretical Extensions (H061-H080)
| ID | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H061 | Network graph centrality of disrupted station | 45% | SKIP | Requires per-station delay data |
| H062 | Delay propagation speed (minutes per hop) | 50% | SKIP | Requires per-service delay data |
| H063 | Capacity utilisation ratio at Connolly | 55% | SKIP | Requires signal throughput data |
| H064 | Buffer time adequacy index per service | 60% | SKIP | Requires timetable with running time margins |
| H065 | Turnaround time violation rate | 55% | SKIP | Requires terminus operations data |
| H066 | Cross-platform interchange delay at Pearse | 40% | SKIP | Requires per-platform data |
| H067 | Signalling failure frequency (monthly proxy) | 45% | SKIP | Irish Rail reports aggregate only |
| H068 | Track condition index | 35% | SKIP | Not published at route-section level |
| H069 | Overhead line voltage stability | 40% | SKIP | Not publicly available |
| H070 | Driver experience proxy (new timetable familiarity) | 35% | SKIP | Not available |
| H071 | Passenger boarding time at peak stations | 45% | SKIP | Requires video/sensor data |
| H072 | Platform crowding index | 40% | SKIP | Requires passenger count data |
| H073 | Service pattern complexity (number of crossings) | 50% | SKIP | Requires timetable graph analysis |
| H074 | Recovery run feasibility (can delayed service catch up?) | 55% | SKIP | Requires sectional running times |
| H075 | Dual-track to single-track transition delay | 50% | SKIP | Requires section-level data |
| H076 | Weather forecast uncertainty as risk amplifier | 35% | SKIP | Requires probabilistic forecast |
| H077 | Historical same-day pattern matching | 40% | SKIP | Requires multi-year GTFS-RT |
| H078 | Connolly-Pearse throughput saturation indicator | 55% | SKIP | Requires signal data |
| H079 | Adaptive turnaround time prediction | 45% | SKIP | Requires real-time terminus data |
| H080 | Multi-day weather event duration | 40% | SKIP | Partially captured by rolling features |

### Cross-Domain (H081-H100)
| ID | Hypothesis | Prior | Status | Notes |
|---|---|---|---|---|
| H081 | Transfer learning from UK rail delay models | 35% | SKIP | Different network characteristics |
| H082 | Dutch delay propagation model (Goverde) applied to DART | 40% | SKIP | Requires per-train data |
| H083 | Swiss buffer time optimisation (Caimi) for DART timetable | 45% | SKIP | Requires full timetable specification |
| H084 | Japanese recovery ratio benchmark | 30% | SKIP | Very different system |
| H085 | Graph neural network on DART topology | 35% | SKIP | Insufficient data for deep learning |
| H086 | Bayesian structural time series for regime detection | 50% | OPEN | Could detect timetable change without label |
| H087 | Survival analysis for time-to-next-bad-day | 40% | OPEN | Alternative framing |
| H088 | Clustering of delay patterns by root cause | 45% | SKIP | Requires per-service delay data |
| H089 | Ensemble of within-regime models | 40% | OPEN | Per-regime XGBoost |
| H090 | Conformal prediction intervals for risk | 35% | OPEN | Uncertainty quantification |
| H091 | SHAP value analysis across time periods | 50% | OPEN | Interpretability enhancement |
| H092 | Partial dependence plots for weather thresholds | 45% | OPEN | Refine wind/rain thresholds |
| H093 | Causal inference: timetable change -> delays (DiD) | 55% | OPEN | Difference-in-differences |
| H094 | Counterfactual: what if timetable change in January? | 40% | OPEN | Seasonal interaction test |
| H095 | Sensitivity analysis: minimum buffer for 90% punctuality | 50% | OPEN | Optimisation target |
| H096 | Monte Carlo simulation of delay propagation | 45% | SKIP | Requires network model |
| H097 | Comparison with Luas (tram) punctuality trends | 35% | SKIP | Different mode |
| H098 | Covid recovery effect on DART demand | 30% | SKIP | Pre-study period |
| H099 | Inflation of bad day threshold from 85% to 90% | 40% | OPEN | Sensitivity to definition |
| H100 | Random forest variable importance vs XGBoost | 30% | OPEN | Cross-validation of importance ranking |

## Summary
- **Total hypotheses**: 100
- **Tested**: 40 (H001-H040)
- **Kept**: 10 (25% keep rate)
- **Reverted**: 30
- **Skipped (data unavailable)**: 40 (H041-H080)
- **Open (future work)**: 20 (H081-H100)
- **Saturation reached**: Last 15 experiments all near-zero delta; research queue exhausted for available features
