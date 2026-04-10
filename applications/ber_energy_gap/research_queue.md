# Research Queue: Irish BER Energy Gap

## Experiment Format
Each hypothesis: ID | Status | Prior | Feature/Change | Expected Outcome | Metric | Baseline

## Active Queue

### Feature Engineering
| ID | Status | Prior | Change | Expected | Metric | Result |
|----|--------|-------|--------|----------|--------|--------|
| H001 | KEPT | 70% | Add compactness ratio (envelope_area / floor_area) | Better separation of detached vs apartment | MAE -0.5 | MAE 19.52 (-0.02) |
| H002 | REVERTED | 65% | Add wall insulation era interaction (year_built x UValueWall) | Capture retrofit vs original fabric | MAE -0.3 | MAE 19.54 (+0.00) |
| H003 | REVERTED | 60% | Add heating-fabric interaction (hs_efficiency x envelope_u_avg) | Capture synergy of good heating + good fabric | MAE -0.3 | MAE 19.56 (+0.02) |
| H004 | KEPT | 55% | Add ventilation heat loss estimate from chimney/flue count | Better predict old homes with open fires | MAE -0.2 | MAE 19.52 (-0.02) |
| H005 | KEPT | 60% | Add primary energy factor by fuel type | Explicit fuel conversion rather than one-hot | MAE -0.5 | MAE 19.52 (-0.02) |
| H006 | REVERTED | 50% | Add roof-to-floor area ratio | Proxy for bungalow vs multi-storey | MAE -0.2 | MAE 19.54 (0.00) |
| H007 | REVERTED | 45% | Add log-transform of ground_floor_area | Non-linear area effect | MAE -0.1 | MAE 19.54 (0.00) |
| H009 | KEPT | 55% | Add space_heating_fraction as feature | Captures relative importance of heating vs DHW | MAE -0.2 | MAE 18.47 (-1.07) |
| H010 | REVERTED | 50% | Add wall_area x UValueWall (total wall heat loss) | Raw heat loss better than U-value alone | MAE -0.3 | MAE 19.54 (0.00) |

### Model Improvements
| ID | Status | Prior | Change | Expected | Metric | Result |
|----|--------|-------|--------|----------|--------|--------|
| H013 | KEPT | 20% | Lower learning_rate to 0.05, increase n_estimators to 600 | More careful boosting | MAE -0.2 | MAE 19.44 (-0.10) |
| H014 | REVERTED | 35% | Use log-transform of target (predict log(kWh/m2)) | Better handling of skewed distribution | MAE -0.5 | MAE 19.67 (+0.13) |

### Composition Retest
| ID | Status | Change | Result |
|----|--------|--------|--------|
| COMP_01 | KEPT | LightGBM tuned + 4 HDR features (compactness, vent_loss, PE factor, sh_fraction) | MAE 18.05 R2=0.9508 |

## Summary

- **Tournament winner**: XGBoost (MAE=19.26, R2=0.943) but LightGBM (MAE=19.54) used for HDR loop due to faster iteration
- **Best single feature**: Space heating fraction (H009) — MAE -1.07, the only feature with substantial individual impact
- **Composition improvement**: Baseline LightGBM MAE 19.54 → Composed MAE 18.05 (7.6% improvement)
- **Overall improvement from Ridge baseline**: MAE 32.28 → 18.05 (44% reduction)
