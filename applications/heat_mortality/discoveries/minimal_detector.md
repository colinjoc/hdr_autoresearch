# Minimal Lethal-Heatwave Detector (Phase B task 1B)

Greedy forward selection on the Phase 2 best atmospheric-only feature set, scoring on 5-fold out-of-fold Area Under the Receiver Operating Characteristic curve (AUC-ROC) for the lethal-heatwave binary target (p-score >= 0.10 AND consecutive_days_above_p95_tmax >= 1). Model: ExtraTreesClassifier(n_estimators=150, class_weight='balanced'). Improvement floor: 0.001 AUC. Cap: 8 features. Structural one-hots (city_*, country_*) excluded from the candidate pool because they are not actionable for an early-warning system.

## Selected feature order

| Step | Feature | Cumulative AUC |
|------|---------|---------------:|
| 1 | `consecutive_days_above_p95_tmax` | 0.9486 |
| 2 | `iso_year` | 0.9696 |

**Final minimal detector AUC: 0.9696** (on 9,276 city-weeks, 5-fold cross-validation).

OOF classifier AUC (same features, verification): 0.9696  
OOF classifier Brier: 0.0759

## Minimal set evaluated as a regressor

- MAE: **81.433 deaths/week**  
- RMSE: 134.636  
- R^2: 0.1524  
- AUC (via p-pred proxy): 0.7209

The minimal detector **is** a useful binary classifier but does not carry most of the regression signal — the autocorrelation features (prior_week_pscore, prior_4w_mean_pscore) and country fixed effects that dominate the regression are **excluded** from the minimal set by design because they are not actionable atmospheric inputs for an early-warning system.

## Night-time wet-bulb in the minimal set?

**No** — no night-Tw feature survives greedy selection. The lethal-heatwave classifier achieves its full AUC without any reference to the night-time wet-bulb temperature. This is the Phase B confirmation of the Phase 2 / Phase 2.5 negative finding.

