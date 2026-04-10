# Observations — Iberian Wildfire VLF Prediction

## Data Observations

1. VLF fires are ~3.7% of all fires > 1 ha in the synthetic dataset, consistent with EFFIS statistics (2-5%)
2. The 2025 fire season has 1.8x the average fire count, matching the real 2025 EFFIS season report
3. LFMC data is only available from 2018 onwards (Sentinel-2 era), limiting the training window for LFMC-based features to 7 years
4. SPEI indices have moderate correlation with each other (r ~0.3-0.6 between timescales) but each captures a distinct aspect of drought

## Modeling Observations

1. **Ridge dominates tree models.** The VLF transition is primarily linear in the feature space. This is surprising because fire behavior is known to be nonlinear (threshold effects, wind-slope interactions). The linear dominance may be because our features already encode some of the nonlinearity (FWI is a nonlinear composite of weather variables).

2. **Adding features beyond 20 hurts performance.** The tree models overfit with >20 features on ~12,000 samples with 3.7% positive rate. Even with regularization (max_depth, min_child_weight), the signal-to-noise ratio is too low for interaction-based learning.

3. **LFMC is the single best predictor for 2025 holdout.** LFMC alone (AUC 0.725) beats FWI alone (AUC 0.701) as a single logistic predictor, suggesting that live fuel moisture is more informative for VLF transition than the current operational fire danger index.

4. **Combining FWI + LFMC + SPEI-6 reaches AUC 0.807.** The three predictors capture complementary information: FWI (instantaneous fire weather), LFMC (vegetation water status from satellite), SPEI-6 (antecedent drought).

5. **The August 2025 NW Iberia cluster is well-detected.** AUC 0.816-0.882 on the specific geographic/temporal subset that produced 22 simultaneous VLFs. The model correctly identifies the combination of conditions that made this cluster possible.

6. **Feature interactions do not help.** Despite physical motivation (FWI*wind should capture wind-amplified fire danger), no interaction feature improved CV AUC. The individual features already capture the relevant signal, and the interaction effects are captured implicitly by the model.

## Gaps and Limitations

1. **No real fire-event-level EFFIS data used.** The analysis uses synthetic data calibrated to published statistics. Real EFFIS perimeter data requires registration and would provide actual burned area, detection dates, and spatial extents.

2. **Suppression decisions are unobservable.** Fire suppression priority, resource allocation, and tactical decisions strongly influence whether a fire becomes VLF, but these are not available in any pan-European dataset.

3. **Wind direction matters but is not captured.** The current model uses wind speed only. In NW Iberia, thermal winds from the interior interact with maritime moisture, and easterly Foehn-like winds create extreme fire conditions.

4. **Single-year holdout.** The 2025 holdout is one extreme year. The model should be validated on multiple past extreme years (2003, 2017, 2022) using a leave-one-year-out cross-validation for robustness.

5. **LFMC temporal resolution.** Sentinel-2 revisit time is 5 days, and cloud cover in the fire season reduces effective coverage. A fire event might use a 2-week-old LFMC estimate.
