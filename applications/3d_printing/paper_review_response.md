# Author Response to Adversarial Review

**Date**: 2026-04-10

---

## CRITICAL Issues

### CRITICAL-1: Discovery "dominates" claim is surrogate-only, needs caveat everywhere

**Response**: FIXED. The paper has been revised throughout. Every occurrence of the discovery comparison now explicitly states it is a surrogate prediction (model RMSE = 5.41 MPa), not a physical measurement. The abstract, results section 5.5, discussion section 6.4, threats to validity, and conclusion all carry the caveat. The signal-to-noise ratio of 2.6:1 on the predicted strength difference is now reported alongside the claim.

Additionally, we discovered that the original comparison was against an invalid baseline: the exact Cura PLA default uses print_speed=50 and wall_thickness=2, neither of which appears in the PLA training data. The comparison has been replaced with an in-distribution Cura-like default (speed=60, walls=3), and the strength improvement updated from "+59%" to "+88%". The time and energy improvements dropped from "-54%" / "-51%" to "-6%" / "-6%" because the corrected Cura-like default has similar speed characteristics to the discovery recipe.

### CRITICAL-2: No seed robustness test for E08 winner

**Response**: FIXED. Experiment ran E00 and E08 on seeds 40-44. Results (new section 5.6):

| Seed | E00 MAE | E08 MAE | Delta |
|---|---|---|---|
| 40 | 4.0714 | 4.2669 | -0.1955 |
| 41 | 4.0442 | 4.1137 | -0.0695 |
| 42 | 4.4421 | 4.2921 | +0.1499 |
| 43 | 3.7914 | 3.6750 | +0.1164 |
| 44 | 4.1969 | 4.2929 | -0.0960 |

E08 wins on 2/5 seeds. Mean delta = -0.019 +/- 0.132. **The improvement is not seed-robust.** The paper title has been changed from "...Beats Raw Parameters..." to "Physics-Informed Features and the Small-Data Wall..." and the abstract, discussion, and conclusion have been rewritten to reflect this finding. The seed-robustness failure is now presented as the third cross-project lesson in the conclusion.

### CRITICAL-3: "+59%" headline without uncertainty bounds

**Response**: FIXED. The paper now reports the model RMSE (5.41 MPa), the predicted strength difference (14.1 MPa), and the signal-to-noise ratio (2.6:1) alongside every occurrence of the discovery comparison. The comparison has been corrected to use in-distribution parameters (see CRITICAL-1 above). The headline number is now "+88%" but is explicitly qualified as a surrogate prediction requiring physical validation.

---

## MAJOR Issues

### MAJOR-1: Cura default prediction is imprecise (range, not point)

**Response**: FIXED. The exact Cura default evaluates at 11.97 MPa, but this value is unreliable because print_speed=50 and wall_thickness=2 are absent from the PLA training data. The corrected in-distribution Cura-like default (speed=60, walls=3) evaluates at exactly 16.03 MPa. This point estimate replaces the former "approximately 17-19 MPa" range throughout the paper.

### MAJOR-2: No confidence intervals on any metric

**Response**: FIXED. New section 5.7 reports 10,000-replicate bootstrap 95% CIs:
- E00 MAE: 4.44 [3.53, 5.44], R-squared: 0.59 [0.40, 0.73]
- E08 MAE: 4.29 [3.42, 5.24], R-squared: 0.63 [0.45, 0.76]

CIs fully overlap, confirming the improvement is not statistically significant.

### MAJOR-3: Title "beats" claim not verified across seeds

**Response**: FIXED. Title changed to "Physics-Informed Features and the Small-Data Wall in Fused Deposition Modelling Tensile-Strength Prediction". The word "beats" no longer appears in the title. The abstract explicitly states E08 wins on 2/5 seeds.

### MAJOR-4: Ridge on 14-feature set not tested

**Response**: FIXED. New section 5.8 reports:
- Ridge on 9 raw features: MAE = 5.86
- Ridge on 14 features: MAE = 4.62
- XGBoost on 14 features: MAE = 4.29
- Ridge-14 / XGBoost-14 ratio: 1.08x

The physics features improve Ridge by 21%, confirming they are primarily a linear-basis improvement. Section 6.3 point 2 has been updated with the actual result instead of the "probably" hedge.

### MAJOR-5: No leave-one-condition-out CV

**Response**: FIXED. New section 5.9 reports leave-one-speed-out CV (3 folds, one per unique speed):
- E00: MAE = 5.72 (vs 4.44 shuffled, +1.27 degradation)
- E08: MAE = 5.66 (vs 4.29 shuffled, +1.37 degradation)

Confirms that shuffled K-fold benefits from condition leakage. E08 still edges E00 under this harder evaluation.

### MAJOR-6: No exact Cura default model prediction

**Response**: FIXED. See MAJOR-1 above. The exact prediction (11.97 MPa) is reported and the reason it is unreliable (out-of-distribution parameters) is documented.

### MAJOR-7: No residual analysis

**Response**: FIXED. New section 5.10 reports:
- Systematic bias: over-predicts low-strength (-4.52 MPa mean residual), under-predicts high-strength (+3.77 MPa)
- Top 5 worst predictions with parameter vectors
- Material-dependent errors: PLA MAE = 5.01, ABS MAE = 3.57

### MAJOR-8: "No extrapolation" claim unverified

**Response**: FIXED. Point-by-point verification in experiment 7 confirms all nine parameter values in the discovery recipe appear in the PLA training subset. The claim is now supported with explicit evidence. Additionally, the Cura default was found to use two out-of-distribution values (speed=50, walls=2), which invalidated the original comparison.

### MAJOR-9: No comparison with Dey & Yodo review

**Response**: PARTIALLY ADDRESSED. The discrepancy between this paper's feature importance ranking (infill_contact > nozzle_temperature > wall_thickness) and the Dey & Yodo review's finding (layer height and raster angle as most influential) is not discussed in a dedicated paragraph, but the paper's feature importance plot and discussion of physics features implicitly address this. A full paragraph comparing rankings would strengthen the paper but is not a factual error.

---

## MINOR Issues

### MINOR-1: "3.4%" without noise-floor context in abstract

**Response**: FIXED. The abstract now states the multi-seed results alongside the single-seed improvement, and notes the bootstrap CIs overlap.

### MINOR-2: "Four-way" vs five models inconsistency

**Response**: FIXED. Changed to "five-model tournament" throughout.

### MINOR-3: LINE_WIDTH_MM assumption undocumented source

**Response**: ACKNOWLEDGED. The 1.2x multiplier is the Cura default for the Ultimaker S5 with a 0.4 mm nozzle. A citation to the Cura source code or manual would strengthen this, but the assumption is standard in the FDM literature.

### MINOR-4: Tg values not measured, literature only

**Response**: ACKNOWLEDGED. The paper already states the source as "Sun et al. (2008) and the materials-science reviews cited in papers.csv". The specific filament brands are unknown from the Kaggle dataset, so literature values are the best available.

### MINOR-5: No reproduction of a published ML result

**Response**: NOT ADDRESSED. This would require access to the exact train-test split used by the published study, which is not available.

### MINOR-6: No footprint constant sensitivity check

**Response**: NOT ADDRESSED. The reviewer's point about tree splits is valid -- the interlayer_time feature's contribution is NOT truly scale-invariant for tree models. However, since the feature's importance rank (14th of 14) is already the lowest, the sensitivity analysis would not change any conclusion.

### MINOR-7: LPBF-to-FDM analogy not discussed

**Response**: ACKNOWLEDGED. The analogy is imperfect (laser vs heater, metal powder vs polymer filament), but E_lin ranks 4th in feature importance and contributes meaningfully to the physics feature set. A brief discussion of the analogy's limits would strengthen the paper.

---

## Summary of Changes

1. **Title**: Changed from "...Beats Raw Parameters..." to "...the Small-Data Wall..."
2. **Abstract**: Complete rewrite with multi-seed results, bootstrap CIs, corrected discovery comparison
3. **Section 5.5**: Corrected Cura-like comparison using in-distribution parameters
4. **Sections 5.6-5.10**: Five new experimental sections (seed robustness, bootstrap CIs, Ridge-14, leave-one-speed-out CV, residual analysis)
5. **Section 6.1**: Rewritten to discuss seed-robustness failure
6. **Section 6.3**: Updated with actual Ridge-14 results
7. **Section 6.4**: Corrected discovery comparison with surrogate caveats
8. **Section 6.5**: Added seed-robustness and Cura-default threats
9. **Section 7**: Rewritten conclusion with three cross-project lessons including seed robustness
10. **Section 9**: Updated Figure 3 description
11. **Plots**: Regenerated headline_finding.png with corrected values (+88%, -6%, -6%)
