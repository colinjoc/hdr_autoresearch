# Observations: Iberian Blackout Cascade Prediction

## Phase 0.5 Observations
- Excursion events are extremely rare (~0.9% of hours) — extreme class imbalance
- With base features only, XGBoost AUC = 0.613 — barely above random
- F2 is stuck at 0.000 because the model predicts all zeros
- The holdout (April 28) has surprisingly high AUC (0.90) — different distribution
- GPU (CUDA) training works but data transfer overhead noted

## Phase 1 Observations
- Ridge (linear model) BEATS all tree models (AUC 0.645 vs 0.613 XGBoost)
- Tree-to-linear ratio = 0.950 — the signal is almost entirely linear
- Ridge detects the blackout day with holdout AUC = 1.0
- LightGBM fails on this system (no OpenCL) — CPU fallback needed
- ExtraTrees worst performer (0.600) — random splits don't help with so few positives

## Phase 2 Observations
- Of 38 experiments, only 3 features kept — most additions are noise at this sample size
- SNSP as a standalone feature does NOT help XGBoost — already captured by gen columns
- Inertia proxy similarly redundant — the individual fuel-type MW values carry the same info
- Total generation ramp, residual demand, and hour*SNSP interaction are the three keepers
- The hour*SNSP interaction is the largest single improvement (+0.014 AUC)
- Class weighting (scale_pos_weight=108) increases blackout-day max probability to 0.45 but doesn't help CV AUC
- Most lag features hurt — temporal autocorrelation introduces noise, not signal

## Phase 2.5 Observations
- Train AUC 0.999 vs holdout AUC 0.888 — significant overfitting (expected with 0.9% positive rate)
- Pre-cascade hours (10-12) rank in top 10% of historical risk — the model does see elevated risk
- Hour 13 (post-cascade) gets highest risk score of the day (P=0.101)
- But no hour exceeds P=0.5 — the model can rank but cannot alert

## Phase B Observations
- All top-20 dangerous hours are confirmed excursion events
- Risk surface confirms physics: highest risk at SNSP 0.55-0.60 with inertia 2.0-2.5s
- Pareto front shows risk increasing sharply above 32% RE, steepest at 57-62%
- Counterfactual (SNSP capped at 60%) shows no effect — because SNSP isn't a direct feature

## Key Insight
The honest conclusion is that publicly available ENTSO-E data provides a risk RANKING signal but is fundamentally insufficient for cascade PREDICTION. The gap is not resolution (15-min vs sub-second) — it is the TYPE of data. You need frequency, voltage, and protection relay state to predict cascades. Generation/load data can only tell you the system is in a riskier region.
