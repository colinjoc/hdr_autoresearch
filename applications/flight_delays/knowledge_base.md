# Knowledge Base -- Flight Delay Propagation (Real BTS Data, Jan-Jun 2024)

## Established Facts

### Aircraft Rotation is the Dominant Propagation Mechanism
- **Finding (this study, real data)**: BTS delay cause decomposition shows 41.0% of all delay minutes attributed to late aircraft (rotation). Model-based feature importance: rotation-chain features account for >55% of XGBoost gain importance.
- **Literature support**: Pyrgiotis-Malone-Odoni (2013) identified aircraft rotation as the primary delay vector. AhmadBeygi et al. (2008) showed cascades of 4-7 flights from single root delays. Fleurquin et al. (2013, Nature Scientific Reports) modeled network-level cascades.
- **Implication**: "Your flight was delayed because the plane was late from its previous flight" is the dominant mechanism in real BTS data -- not an excuse.

### Carrier Buffer Strategy is the Key Moderating Variable
- **Finding (this study, real data)**: The interaction feature `prev_delay_x_buffer` (previous delay times carrier buffer factor) is the **single most important feature** (27.4% importance in XGBoost). Carriers with longer turnarounds (Delta: 152 min, Hawaiian: 84 min) propagate less delay than tight-schedule carriers (Southwest: 86 min, Spirit: 140 min, American: 145 min).
- **Literature**: AhmadBeygi et al. (2008) theoretically predicted this. AhmadBeygi et al. (2010) estimated 5 minutes extra buffer reduces propagation 15-20%.
- **Practical**: American Airlines' mean late-aircraft delay (14.8 min/flight) is over 3x Delta's (4.5 min/flight). The difference is largely explained by hub scheduling intensity.

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
