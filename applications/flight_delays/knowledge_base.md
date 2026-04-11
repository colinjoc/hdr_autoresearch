# Knowledge Base -- Flight Delay Propagation (Real BTS Data, Jan-Jun 2024)

## Established Facts

### Airport Congestion and Rotation Jointly Drive Delay Prediction
- **Finding (this study, real data)**: BTS delay cause decomposition shows 41.0% of all delay minutes attributed to late aircraft (rotation). SHAP analysis shows rotation features account for 28% of model importance, while airport congestion features (dest_arr_delay 20.4%, origin_dep_delay 15.4%, taxi-out 11.1%) account for ~47%. XGBoost gain importance (58% rotation) overstates rotation's role due to known gain-importance bias toward high-cardinality features.
- **Literature support**: Pyrgiotis-Malone-Odoni (2013) identified aircraft rotation as the primary delay vector. AhmadBeygi et al. (2008) showed cascades of 4-7 flights from single root delays. Fleurquin et al. (2013, Nature Scientific Reports) modeled network-level cascades.
- **Implication**: "Your flight was delayed because the plane was late from its previous flight" is the single largest BTS cause code, but the current state of airport congestion is equally or more important for prediction.

### Carrier Buffer Strategy is the Key Rotation-Specific Variable
- **Finding (this study, real data)**: The interaction feature `prev_delay_x_buffer` is the most important rotation-specific feature (5.7% SHAP importance, 27.4% XGBoost gain). Carriers with longer turnarounds (Delta: 152 min) are associated with lower propagation. American Airlines has the highest late-aircraft delay (14.8 min/flight).
- **SHAP vs Gain discrepancy**: XGBoost gain ranks prev_delay_x_buffer at 27.4% (#1), but SHAP ranks it at 5.7% (#6). The gain-importance bias inflated its apparent importance because the continuous interaction term appears in many tree splits with small individual contributions.
- **Literature**: AhmadBeygi et al. (2008) simulated this effect. AhmadBeygi et al. (2010) estimated 5 minutes extra buffer reduces propagation 15-20%.
- **Caution**: Carrier-level findings are observational correlations, not causal effects. Route mix, fleet age, and other confounds are not controlled.

### Delay Accumulation Through the Day
- **Finding (real data)**: Morning flights (06:00-09:00) arrive ~2 min early on average. Delays accumulate monotonically: +2.6 min at 9AM, +7.2 at noon, +12.3 at 3PM, +16.8 at 7PM. Peak at 19:00-20:00.
- **Literature**: Consistent with Simaiakis-Balakrishnan (2014) taxi-out delay dynamics. The overnight reset is a well-known phenomenon.
- **Practical**: First flight of the day has zero rotation-chain propagation. Every subsequent leg inherits risk.

### Hub Airports are Contagion Amplifiers
- **Finding (real data)**: DFW is the #1 super-spreader airport (propagation score 43.7), followed by MIA (41.6), FLL (39.8), MCO (37.0), SFO (36.6). DFW appears in 4 of top 10 super-spreader routes.
- **Literature**: Guimera et al. (2005, PNAS) showed hub-and-spoke topology concentrates traffic. Fleurquin et al. (2013) identified hubs as cascade amplifiers.

### Propagation Depth: Half Contained, Half Cascade
- **Finding (real data)**: 49.6% of initial delays are contained at first flight (depth=1). Mean depth 2.01, max 10. 14.4% cascade through 3+ flights.
- **Implication**: The tail is heavy -- the 5% of delays that cascade through 5+ flights are disproportionately expensive in total delay minutes.

### Tournament Results (Temporal CV, Jan-Mar 2024, Holdout Apr 2024)
| Model | CV AUC | Holdout AUC |
|-------|--------|-------------|
| Logistic regression | 0.863 | 0.863 |
| ExtraTrees | 0.890 | 0.888 |
| LightGBM | 0.919 | 0.918 |
| XGBoost (baseline 19 features) | 0.920 | 0.918 |
| **XGBoost (enhanced 29 features)** | **0.923** | **0.920** |

### The Signal is Substantially Linear
- **Finding**: Logistic regression (AUC 0.863) captures most of the signal that XGBoost (0.923) does. The 6-point AUC gap comes from interaction effects and thresholds.
- **Implication**: `P(delayed) ~ sigmoid(w1 * prev_delay * buffer + w2 * congestion + w3 * time_of_day)` captures the core mechanism.

### BTS Delay Cause Codes (Real Data, 749K Delayed Flights)
| Cause | Fraction |
|-------|----------|
| Late aircraft (rotation) | 41.0% |
| Carrier (ops/crew/maintenance) | 32.7% |
| NAS (ATC/congestion) | 19.6% |
| Weather | 6.5% |
| Security | 0.2% |

### Regression Performance
- **Holdout MAE**: 14.4 minutes (XGBoost regressor, enhanced features)

### Model Calibration (Added in Review Cycle)
- **Brier score**: 0.074 (baseline predicting marginal rate: 0.162)
- **Expected calibration error (ECE)**: 0.009
- **Implication**: Predicted probabilities can be interpreted directly (30% predicted = ~30% observed)

### Temporal Stability (Added in Review Cycle)
- AUC per month (trained on Jan-Mar): Apr 0.920, May 0.921, Jun 0.919
- Standard deviation: 0.0008
- **Implication**: No seasonal degradation across spring months. Summer not tested.

### First-Leg-of-Day Flights (Added in Review Cycle)
- First-leg AUC: 0.880 (24.4% of holdout flights)
- Non-first-leg AUC: 0.928
- First-leg delay rate: 12.6% vs 21.1% for subsequent legs
- **Implication**: Model degrades gracefully without rotation features; airport/temporal features provide a strong baseline

### Network Metrics (Added in Review Cycle)
- 343 airports, 6536 routes, density 0.056
- Top by degree centrality: DFW, DEN, ORD, ATL, CLT
- Top by betweenness: AGS, LGA, DAB, SDF, DFW
- Top by PageRank: DFW, PHX, DEN, LAX, LGA
- DFW ranks #1 on both degree centrality and propagation score

## What Does NOT Work
- Carrier one-hot encoding: redundant with carrier_buffer_factor
- Distance-squared: no nonlinear distance effect
- Holiday indicators: too sparse to learn from
- Architecture switches (LightGBM, ExtraTrees): marginal vs XGBoost
- Hyperparameter tweaks: learning_rate, max_depth, subsample changes negligible

## Open Questions
1. Does weather persistence (METAR-based) add signal beyond BTS cause codes?
2. Crew pairing proxy: same-carrier flights arriving within +/- 90 min?
3. Does cascade depth (how many legs back is root cause?) improve prediction?
4. Two-stage model (classify then regress) vs single-stage?
5. Flight cancellation effects on downstream propagation?
