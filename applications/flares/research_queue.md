# Research Queue

Prioritised hypotheses for HDR cycles. Format:
```
### Q[N] — [Title] [STATUS]
Impact: HIGH / MEDIUM / LOW
Hypothesis: ...
Mechanism: ...
```

Status: OPEN | RESOLVED | RETIRED

---

## Feature Engineering

### Q1 — Log-transform AREA and No_sunspots [OPEN]
Impact: HIGH
Hypothesis: Adding log(AREA) and log(No_sunspots+1) will improve TSS.
Mechanism: Area spans 0-2750 MSH (3 orders of magnitude). Log transform linearizes the relationship with flare flux and better separates flaring from non-flaring distributions (Hayes 2021, Fig 14). Trees handle this implicitly but providing it directly saves splits.

### Q2 — MAGTYPE one-hot encoding instead of ordinal [OPEN]
Impact: MEDIUM
Hypothesis: One-hot encoding MAGTYPE will improve over ordinal encoding.
Mechanism: The ordinal encoding assumes linear ordering of complexity, but GAMMA-DELTA vs BETA-GAMMA-DELTA may not be monotonically ordered in flare probability. One-hot lets the model learn non-monotonic relationships.

### Q3 — McIntosh full one-hot encoding [OPEN]
Impact: MEDIUM
Hypothesis: One-hot encoding the full 63-class McIntosh will improve TSS.
Mechanism: McIntosh classification is the foundation of Poisson-based forecasts (McStat). The 3-letter decomposition loses interaction information between Zurich class, penumbral type, and compactness. Full encoding preserves these interactions at the cost of higher dimensionality.

### Q4 — Absolute latitude feature [OPEN]
Impact: LOW
Hypothesis: Adding |Latitude| will improve TSS.
Mechanism: Active regions closer to the equator may behave differently from high-latitude ones. The butterfly diagram shows ARs migrate equatorward through the solar cycle. Latitude may proxy for solar cycle phase.

### Q5 — Central meridian distance [OPEN]
Impact: MEDIUM
Hypothesis: Adding |Longitude| as central meridian distance will improve TSS.
Mechanism: Flares near the limb are harder to detect/associate with ARs (71% association rate vs higher for disk-center ARs). Longitude also affects geoeffectiveness. The model may learn that limb ARs have different flare statistics.

### Q6 — Area × MAGTYPE interaction [OPEN]
Impact: HIGH
Hypothesis: Adding AREA * MAGTYPE_complexity interaction will improve TSS.
Mechanism: Large + magnetically complex = most dangerous. A 2000 MSH BETA-GAMMA-DELTA is far more likely to flare than a 2000 MSH ALPHA. This interaction is the key physical predictor but requires 2 tree splits to learn.

## Model Architecture

### Q7 — XGBoost instead of sklearn GradientBoosting [OPEN]
Impact: HIGH
Hypothesis: XGBoost will outperform sklearn's GradientBoostingClassifier.
Mechanism: XGBoost has better regularization (colsample, subsample), native handling of missing values, and is faster. Hayes 2021 k-fold showed similar performance but XGBoost wasn't fully tuned.

### Q8 — scale_pos_weight for class imbalance [OPEN]
Impact: HIGH
Hypothesis: Setting scale_pos_weight ≈ 4.3 (ratio of negatives to positives) will improve TSS.
Mechanism: The 81/19 class imbalance means the model sees 4.3x more negative examples. Upweighting positives forces the model to focus on correctly predicting flares. Critical lesson from the disruption project — scale_pos_weight tuning was the single biggest improvement.

### Q9 — Deeper trees (max_depth 5-6) [OPEN]
Impact: MEDIUM
Hypothesis: Increasing max_depth from 4 to 5-6 will improve TSS with 33k samples.
Mechanism: With 33,516 samples, deeper trees should generalize. Depth 4 may be too shallow to capture McIntosh × MAGTYPE × Area interactions.

## Advanced

### Q10 — Temporal features (solar cycle phase) [OPEN]
Impact: MEDIUM
Hypothesis: Adding year or solar cycle phase indicator will improve TSS.
Mechanism: Flare rates vary dramatically through the solar cycle (Fig 6, Hayes 2021). The model may benefit from knowing where in the cycle the observation falls. Can be encoded as continuous (year) or cyclical.

### Q11 — Previous day's flare history [OPEN]
Impact: HIGH
Hypothesis: If the AR_flare_ml_23_24_evol.csv dataset is used, including whether the AR flared yesterday will improve TSS.
Mechanism: Flare-productive ARs tend to produce multiple flares. "Did it flare yesterday?" is the simplest persistence forecast and a strong baseline predictor.
Note: May require switching to the _evol dataset.

### Q12 — Ensemble: Poisson + ML [OPEN]
Impact: MEDIUM
Hypothesis: Blending McStat Poisson probabilities with ML probabilities will improve BSS.
Mechanism: Poisson and ML models have different failure modes. Poisson is well-calibrated but low-resolution; ML has better discrimination but worse calibration. Blending combines strengths.

## Literature-Sourced Hypotheses

### Q13 — Zurich class ordinal encoding (A=0..H=6) [OPEN]
Impact: MEDIUM
Hypothesis: Ordinal encoding the Zurich component of McIntosh by size/complexity will improve TSS.
Mechanism: McIntosh 1990 showed the modified Zurich class (A-H) tracks AR size and complexity monotonically. Currently encoded as arbitrary category codes. Ordinal encoding (A<B<C<D<E<F<H) encodes the domain-known ordering. H is a single spot with no penumbra (regressing), so H should rank between A and B.
Source: McIntosh 1990

### Q14 — Penumbral class ordinal encoding [OPEN]
Impact: MEDIUM
Hypothesis: Ordinal encoding penumbral type by penumbral area/complexity will improve TSS.
Mechanism: Penumbral type (X,R,S,A,H,K) encodes largest-spot penumbral structure. X=no penumbra < R=rudimentary < S=small symmetric < A=small asymmetric < H=large symmetric < K=large asymmetric. K penumbrae (largest, most asymmetric) are associated with highest flare rates.
Source: McIntosh 1990

### Q15 — Flare-history decay features (simulate from C+ column) [OPEN]
Impact: HIGH
Hypothesis: Engineering a time-decay feature from the AR's own C+ flare history will significantly improve TSS.
Mechanism: Jonas et al. 2018 showed flare-history decay features (Cdec = sum of exp(-dt/tau) for prior C-flares) are among the best predictors. Flare-productive ARs cluster in time. We can compute this from the C+ column by grouping by noaa_ar and computing cumulative decayed flare counts.
Source: Jonas et al. 2018

### Q16 — AR persistence feature (days since AR appeared) [OPEN]
Impact: MEDIUM
Hypothesis: Adding the number of consecutive days an AR has been observed will improve TSS.
Mechanism: ARs evolve through their disk passage (~14 days). Young ARs emerging from the east limb behave differently from mature ARs near the west limb. Falconer et al. 2011 found flare history over an AR's lifetime is predictive.
Source: Falconer et al. 2011

### Q17 — AR area change rate (delta AREA from previous observation) [OPEN]
Impact: HIGH
Hypothesis: Adding the rate of change of AR area will improve TSS.
Mechanism: McCloskey et al. 2018 showed that upward evolution in McIntosh components increases flaring rates. Growing ARs (increasing area) are more likely to flare. Requires computing per-AR daily differences. This is the continuous analog of McEvol.
Source: McCloskey et al. 2018

### Q18 — SMOTE or random oversampling [OPEN]
Impact: MEDIUM
Hypothesis: Oversampling the minority (flare) class will improve TSS over scale_pos_weight alone.
Mechanism: Ahmadzadeh et al. 2021 showed sampling strategy significantly affects performance. SMOTE generates synthetic minority samples. However, temporal coherence must be respected — only oversample within the training set.
Source: Ahmadzadeh et al. 2021

### Q19 — LightGBM instead of XGBoost [OPEN]
Impact: LOW
Hypothesis: LightGBM will match or exceed XGBoost with faster training.
Mechanism: LightGBM uses histogram-based splitting and leaf-wise growth, often faster than XGBoost on tabular data. Similar regularization options.
Source: General ML literature

### Q20 — Random Forest baseline [OPEN]
Impact: MEDIUM (tournament)
Hypothesis: RF will provide a competitive baseline for the model tournament.
Mechanism: Florios et al. 2018 found RF best on SHARP data. Hayes 2021 found RF worst. Discrepancy may be due to features — RF may benefit from our SRS feature set differently. Need to test for tournament.
Source: Florios et al. 2018, Hayes 2021

### Q21 — Logistic Regression baseline [OPEN]
Impact: MEDIUM (tournament)
Hypothesis: LR may match tree methods on this feature set.
Mechanism: Hayes 2021 showed LR TSS ~0.55, competitive with GB. LR produces naturally calibrated probabilities (good for BSS). Worth including in tournament.
Source: Hayes 2021

### Q22 — Hierarchical classification (C/M/X separately) [OPEN]
Impact: MEDIUM
Hypothesis: Training separate binary classifiers for C vs no-C, M vs no-M, then combining will improve TSS.
Mechanism: Zheng et al. 2019 found hierarchical decomposition outperforms flat multiclass. C and M+ flares may have different predictor profiles. Hierarchical approach avoids conflating them.
Source: Zheng et al. 2019

### Q23 — Compactness ordinal encoding [OPEN]
Impact: LOW
Hypothesis: Ordinal encoding compactness (X<O<I<C) will improve TSS.
Mechanism: Compactness of sunspot distribution (X=undefined, O=open, I=intermediate, C=compact). Compact groups have higher flare rates.
Source: McIntosh 1990

### Q24 — Remove Carrington longitude [OPEN]
Impact: LOW
Hypothesis: Removing Carrington_long will improve TSS by reducing noise.
Mechanism: Carrington longitude is an arbitrary coordinate that changes daily. It has no physical relationship to flare probability. Including it adds 360 values of noise the model may overfit to.

### Q25 — Sunspot count × MAGTYPE interaction [OPEN]
Impact: MEDIUM
Hypothesis: Adding No_sunspots * MAGTYPE_ord interaction will improve TSS.
Mechanism: Similar to Q6 (Area × MAGTYPE). More sunspots in a magnetically complex region = more free energy for reconnection. Distinct from area because many small spots behave differently from few large spots.
Source: Toriumi & Wang 2019
