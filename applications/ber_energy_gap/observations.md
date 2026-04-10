# Observations: Irish BER vs Real Home Energy Gap

## Phase 0.5 Baseline
- Baseline XGBoost: CV MAE=61.04, R2=0.60, Holdout MAE=69.13
- Mean energy value: 214.4 kWh/m2/yr, so MAE represents ~28% of mean
- Model struggles most with G-rated homes (MAE=172) and improves for better ratings (A2: MAE=9)
- This is expected: G-rated homes have the most heterogeneous construction and the largest absolute energy values

## Phase 1 Tournament
- ExtraTrees wins: CV MAE=55.51, R2=0.66 — 9% better than XGBoost
- LightGBM: CV MAE=59.52, close to XGBoost
- Ridge: CV MAE=71.96 — worst, BUT Ridge R2 (0.61) is not drastically worse than tree methods (0.60-0.66)
- This means the relationship is substantially linear — tree models add ~10% improvement from nonlinear interactions
- Per-rating: Ridge's errors are most uniform across ratings (77-142), while tree models have monotonically increasing errors from A to G
- ExtraTrees has notably better G-rated performance (MAE=149 vs 172 for XGBoost)

## Key Signals
- Wall U-value and heating system are clearly the most important features (from physics)
- The model explains ~60-65% of variance — the remaining 35-40% is likely from:
  1. Interaction effects not captured by default features
  2. Missing features (detailed geometry, thermal bridges, exact insulation thickness)
  3. Noise from assessor variability and standardised assumptions
  4. Non-physical features of the DEAP model (e.g., primary energy factors for electricity)

## Data Quality Notes
- Synthetic data calibrated to SEAI statistics — but synthetic data may understate real assessor variability
- Energy values capped at 700 kWh/m2/yr (a few records hit the cap)
- The synthetic DEAP calculation is simplified — real DEAP has more parameters
