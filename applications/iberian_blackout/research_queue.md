# Research Queue: Iberian Blackout Cascade Prediction

## Format: ID | Hypothesis | Design Variable | Expected Outcome | Metric | Prior | Status

### Model Architecture
| H001 | Random Forest outperforms logistic regression on small imbalanced data | model_type=rf | Higher F1 | F1 | 40% | OPEN |
| H002 | Gradient Boosting with shallow trees handles interactions better | model_type=gbm | Higher AUC | AUC-ROC | 35% | OPEN |
| H003 | ExtraTrees (bagging) beats boosting for N<200 | model_type=et | Higher F1 | F1 | 45% | OPEN |
| H004 | SVM with RBF kernel captures nonlinear boundaries | model_type=svm | Higher AUC | AUC-ROC | 30% | OPEN |
| H005 | Linear baseline (Ridge) is competitive with tree methods | model_type=ridge | Comparable F1 | F1 | 50% | OPEN |

### Feature Engineering
| H010 | Adding 7-day rolling renewable fraction improves prediction | rolling_renewable_7d | Higher AUC | AUC-ROC | 55% | OPEN |
| H011 | Rate of change of solar fraction captures fast ramp-ups | solar_roc_1d | Higher recall | Recall | 45% | OPEN |
| H012 | Price volatility (7-day rolling std) indicates unstable dispatch | price_vol_7d | Higher AUC | AUC-ROC | 40% | OPEN |
| H013 | Demand volatility from hourly data captures intra-day stress | demand_hourly_std | Higher precision | Precision | 50% | OPEN |
| H014 | Interaction solar_frac * negative_price is strongest single predictor | solar_x_neg_price | Higher AUC | AUC-ROC | 60% | OPEN |
| H015 | Weekend indicator captures lower demand / higher solar penetration | is_weekend | Marginal improvement | F1 | 25% | OPEN |
| H016 | Three-way interaction: solar * low_sync * export captures full mechanism | triple_interaction | Higher AUC | AUC-ROC | 55% | OPEN |
| H017 | Log-transform of generation ratios handles skew | log_ratios | Higher F1 | F1 | 30% | OPEN |
| H018 | Adding month-over-month generation change captures seasonal transitions | gen_mom_change | Higher AUC | AUC-ROC | 35% | OPEN |
| H019 | Nuclear fraction as independent feature (constant baseload indicator) | nuclear_fraction | Higher precision | Precision | 40% | OPEN |
| H020 | Export direction (sign) matters more than magnitude | export_direction | Higher recall | Recall | 35% | OPEN |

### Labeling Strategy
| H030 | Using 90th percentile stress threshold instead of 95th produces better labels | label_threshold=0.90 | Higher F1 | F1 | 45% | OPEN |
| H031 | Labeling days before blackout as high-risk (lead time) improves recall | label_lead_days=2 | Higher recall | Recall | 50% | OPEN |
| H032 | Using k-means clustering to identify risk clusters instead of percentile | label_method=kmeans | Higher AUC | AUC-ROC | 35% | OPEN |
| H033 | Multi-level risk labels (low/medium/high) with ordinal regression | ordinal_labels | Higher rank correlation | Spearman | 40% | OPEN |

### Physics-Informed Decomposition
| H040 | Voltage stress proxy should have highest feature importance | voltage_stress_weight | Confirmed importance | Importance rank | 65% | OPEN |
| H041 | Reactive gap proxy adds predictive power beyond voltage stress alone | reactive_gap_incremental | Higher AUC vs voltage-only | AUC-ROC delta | 50% | OPEN |
| H042 | Inertia proxy is redundant given voltage stress (per ENTSO-E) | drop_inertia | No AUC change | AUC-ROC | 55% | OPEN |
| H043 | Weighted inertia proxy (hydro=0.7, nuclear=1.0, gas=0.8) is more accurate | weighted_inertia | Higher correlation with known risk | Correlation | 40% | OPEN |
| H044 | Including hydro pump-storage as load-side demand improves excess-gen calc | hydro_pump_adjustment | Higher AUC | AUC-ROC | 45% | OPEN |
| H045 | Decomposing solar into utility-scale vs rooftop matters for voltage | solar_decomposition | Higher precision | Precision | 30% | OPEN |

### Cross-Border Flow Analysis
| H050 | France interconnector flow is more predictive than Portugal flow | france_flow_weight | Higher importance | Feature importance | 45% | OPEN |
| H051 | Total export as fraction of generation captures system stress better than absolute | export_fraction_vs_abs | Higher AUC | AUC-ROC | 55% | OPEN |
| H052 | Direction of Morocco flow matters (Spain was exporting) | morocco_direction | Marginal improvement | F1 | 25% | OPEN |
| H053 | Interconnector flow imbalance (asymmetry) captures vulnerability | flow_asymmetry | Higher AUC | AUC-ROC | 35% | OPEN |

### Price Signal Analysis
| H060 | Negative price hours per day better than daily min price | neg_price_hours | Higher AUC | AUC-ROC | 50% | OPEN |
| H061 | Price spread (max-min) captures dispatch volatility | price_spread | Higher precision | Precision | 40% | OPEN |
| H062 | Price relative to 30-day moving average captures anomalous dispatch | price_deviation | Higher AUC | AUC-ROC | 45% | OPEN |
| H063 | Zero-crossing frequency (pos/neg price transitions) indicates dispatch stress | price_zero_crossings | Higher recall | Recall | 30% | OPEN |

### Demand Pattern Analysis
| H070 | Demand ramp rate (morning rise) captures inertia requirement | demand_ramp_rate | Higher AUC | AUC-ROC | 40% | OPEN |
| H071 | Demand-forecast error captures unexpected conditions | demand_forecast_error | Higher precision | Precision | 45% | OPEN |
| H072 | Min/max demand ratio captures daily variability | demand_min_max_ratio | Higher AUC | AUC-ROC | 35% | OPEN |
| H073 | Midday demand (11:00-14:00) specifically relevant (peak solar hours) | midday_demand | Higher recall | Recall | 50% | OPEN |

### Ensemble and Composition
| H080 | Stacking logistic + RF improves over either alone | stacking_lr_rf | Higher AUC | AUC-ROC | 40% | OPEN |
| H081 | Voting ensemble (logistic + RF + GBM) more robust | voting_ensemble | Higher F1 | F1 | 45% | OPEN |
| H082 | Two-stage model: cluster grid states first, then classify within clusters | two_stage | Higher precision | Precision | 35% | OPEN |

### Regularization and Training
| H090 | Lower C (stronger regularization) prevents overfitting on 94 samples | C=0.01 | Higher LOO AUC | AUC-ROC | 45% | OPEN |
| H091 | SMOTE oversampling of positive class improves recall | smote | Higher recall | Recall | 35% | OPEN |
| H092 | Cost-sensitive learning with 10:1 weight ratio | class_weight_10 | Higher recall | Recall | 40% | OPEN |
| H093 | Feature selection via mutual information before model | mi_selection | Higher AUC | AUC-ROC | 35% | OPEN |

### Validation Strategy
| H100 | Temporal split (train pre-April, test April) is more honest than LOO | temporal_split | Comparable AUC | AUC-ROC | 50% | OPEN |
| H101 | Stratified 5-fold CV is more efficient than LOO | stratified_5fold | Comparable AUC | AUC-ROC | 50% | OPEN |

### Historical Comparison
| H110 | April 2024 data has lower risk scores than April 2025 (validation of trend) | 2024_comparison | Lower mean risk | Risk score | 70% | OPEN |
| H111 | Similar grid states in March 2025 had elevated risk but didn't cascade | march_near_misses | Identified near-misses | Count | 60% | OPEN |
