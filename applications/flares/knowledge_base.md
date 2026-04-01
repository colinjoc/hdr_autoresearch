# Knowledge Base

Cumulative findings from experiments. Consult before proposing any hypothesis.

## Published Baselines (from Hayes 2021)

| Method | TSS | BSS | AUC | Notes |
|--------|-----|-----|-----|-------|
| McStat (Poisson) | 0.50 | - | 0.82 | Based on McIntosh classification flaring rates |
| McEvol (Poisson) | 0.49 | - | 0.78 | Uses McIntosh classification evolution |
| Gradient Boost | 0.57 | 0.59 | 0.87 | sklearn GradientBoostingClassifier |
| Logistic Regression | ~0.55 | ~0.63 | - | k-fold CV, Hayes 2021 |
| LDA | ~0.55 | ~0.62 | - | k-fold CV |
| Random Forest | ~0.43 | ~0.50 | - | k-fold CV, worst performer |
| XGBoost | ~0.52 | ~0.59 | - | k-fold CV |

## Current Best Scores

(To be populated after baseline run)

## What Works

(To be populated during HDR loop)

## What Doesn't Work

(To be populated during HDR loop)

## Key Domain Facts

- Class imbalance: 81.2% negative, 18.8% positive for C+ flares
- MAGTYPE is the strongest single predictor — BETA-GAMMA-DELTA ARs produce the most large flares
- McIntosh classification encodes 3 independent physical properties (Zurich size, penumbral type, compactness)
- Flare rates follow a power law — C flares are ~5x more common than M, which are ~9x more common than X
- AR area correlates with flare peak intensity (Fig 10, Hayes 2021)
- Flaring ARs have distinctly different distributions in area, longitudinal extent, and sunspot count vs non-flaring ARs (Figs 13-14)
- Log transforms of area and sunspot count better separate flaring from non-flaring distributions (Fig 14)
