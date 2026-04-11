# Author Response to Peer Review

We thank the reviewer for a thorough and exacting critique. The review identified fundamental problems with the paper's framing, a critical data confounding issue, missing experiments, and overclaiming. We agree with almost all of the criticism. The revision has substantially changed the paper's conclusions: what was framed as a promising predictive tool is now honestly described as an exploratory analysis with severe limitations. Below we address every point, grouped by severity.

---

## CRITICAL Issues

### C1. F1 = 0.47 is poor classification performance, but paper frames it positively

**Reviewer concern:** F1 = 0.47 means the model misclassifies the majority of HRAs. Precision and recall were not reported separately.

**Finding on investigation:** The reviewer was correct. The decomposition is damning:
- Precision: 0.52 -- of areas the model flags as HRA, 52% actually are.
- Recall: 0.43 -- the model identifies only 43% of actual HRAs.
- The model misses 132 out of 231 actual High Radon Areas. These missed areas have mean actual radon of 18.6% (up to 45%).

For health screening, recall is the critical metric. The model's recall of 0.43 means it misses 57% of dangerous areas -- areas where residents are not warned to test.

**Threshold sensitivity analysis:** To achieve recall >= 0.9, the threshold must be lowered to 3.5%, at which point the model flags approximately 60% of all grid squares. At that point it provides little screening value over universal testing. The F1-optimal threshold is 7.0% (precision 0.46, recall 0.72, F1 0.56), still missing 28% of dangerous areas.

**Paper change:** Added Section 3.5 (Precision, Recall, and the Cost of Missing Dangerous Areas) reporting the full decomposition and threshold sensitivity analysis. Reframed abstract and conclusion to describe the model as an exploratory analysis, not a screening tool.

### C2. Tellus data is degraded (RGB-rendered, not raw eU) -- confounds the lithology vs radiometrics finding

**Reviewer concern:** The paper's central claim that lithology outperforms radiometrics may be an artifact of using degraded radiometric data extracted from colour-rendered images.

**Finding on investigation:** The reviewer was entirely correct to flag this as critical. SHAP analysis reveals a more nuanced picture than gain importance:
- By SHAP, the eU/eTh ratio is the second most important feature globally (mean |SHAP| = 1.26), and radiometric features collectively contribute substantially.
- By gain importance, radiometric features appear weak because gain is biased toward binary features that appear in many tree splits.
- The discrepancy between gain and SHAP for radiometric features is consistent with the degradation hypothesis: even degraded radiometric data contributes meaningful signal by SHAP, suggesting raw data would contribute more.

We cannot validate the pseudo-radiometric index against raw eU values because the raw data was not available for this study (it requires a data download request to GSI). We have therefore rewritten Section 4.2 to present three possible explanations for the lithology-over-radiometrics ranking (data degradation, scale mismatch, transport mechanisms) and explicitly state that we cannot determine their relative contribution without raw data.

**Paper change:** Added critical data limitation paragraph to Section 2.1. Rewrote Section 4.2 as "Lithology vs Radiometrics: Confounded by Degraded Data." Removed all unqualified claims that lithology outperforms radiometrics. The abstract now states: "This last finding may partly reflect the degraded format of the available Tellus data rather than a genuine geological hierarchy."

### C3. Systematic underprediction of high-radon areas

**Reviewer concern:** The pred_vs_actual plot shows the model systematically underpredicts high-radon grid squares while overpredicting low-radon ones.

**Finding on investigation:** The underprediction is severe and systematic:

| Actual range | n | Mean predicted | Mean underprediction |
|---|---|---|---|
| 10-15% | 93 | 9.5% | 2.7 pp |
| 15-20% | 40 | 10.0% | 7.5 pp |
| 20-30% | 66 | 11.2% | 13.2 pp |
| 30-55% | 32 | 13.0% | 25.4 pp |

For the 32 most dangerous grid squares (>30% of homes above the reference level), the model predicts a mean of only 13.0%. Nearly half of these areas are classified as non-HRA by the model. This is classic regression to the mean in tree-based models trained on right-skewed targets.

**Paper change:** Added Section 3.6 (Systematic Underprediction of High-Radon Areas) with the full bias table. Updated pred_vs_actual.png to include precision/recall stats and a shaded false-negative quadrant. This section is now prominently placed before the feature importance discussion to frame all subsequent analysis in the context of the model's actual predictive limitations.

### C4. No SHAP analysis despite the BER paper using it

**Reviewer concern:** XGBoost gain-based importance is the only attribution method used. SHAP (TreeSHAP) would provide theoretically grounded attributions.

**New experiment:** Full TreeSHAP analysis on the training set. Key findings:

The SHAP ranking differs substantially from gain:
- Top by SHAP: centroid_x (1.83), eU_eTh_ratio (1.26), Carboniferous limestone (1.20), centroid_y (1.18), eU_std (0.85)
- Top by gain: Carboniferous limestone (9.2%), granite/granodiorite (7.4%), Ordovician-Silurian (4.2%)

SHAP reveals that geographic coordinates and radiometric features are globally more important than gain suggests, while binary geological features are locally important but overstated by gain.

The granite-till interaction has mean |SHAP| of only 0.034 globally but +0.815 for the 17 squares where it equals 1 -- a locally meaningful but globally minor effect on a tiny subset.

**Paper change:** Section 3.4 now presents both gain and SHAP rankings with discussion of their discrepancy. Added shap_importance.png and shap_beeswarm.png.

---

## MAJOR Issues

### M1. "12% better than linear baseline" is misleading framing

**Agreement:** The 12.3% relative improvement obscures the tiny absolute gain (0.91 MAE pp). The paper now reports both relative and absolute improvements and notes that the largest gain comes from switching to tree models, not from feature engineering.

### M2. Granite-till interaction weakly validated

**New experiment:** Ablation and bootstrap analysis.
- Only 17 out of 820 grid squares (2.1%) have both granite and till.
- Removing granite_x_till: MAE changes from 6.43 to 6.46 (negligible).
- Removing ALL interactions: MAE improves to 6.37 -- interactions hurt.
- Bootstrap 95% CI for granite-till gain importance: [0.000, 0.048] -- includes zero.

**Paper change:** Added Section 3.7 documenting the granite-till interaction as a valid geological observation but an unreliable predictive feature. Removed all framing of this as a "key finding" or "novel finding."

### M3. pred_vs_actual shows substantial bias (covered under C3)

Addressed in new Section 3.6.

### M4. Title implies home-level prediction but model operates at 10km grid scale

**Paper change:** Title changed from "Predicting Dangerous Radon Levels in Irish Homes" to "Predicting Radon Risk in Irish Grid Squares from Publicly Available Geological Data."

### M5. Comparison with Elio et al. is not apples-to-apples

**New experiment:** Random CV comparison.
- Our random CV AUC: 0.83 (matches Elio et al.'s 0.78-0.82)
- Our spatial CV AUC: 0.74
- Inflation from random CV: 11%

This demonstrates the difference is evaluation methodology, not modelling. Added Section 3.8.

### M6. SHAP analysis missing (covered under C4)

Full SHAP analysis added.

### M7. Random CV comparison missing (covered under M5)

Added Section 3.8 with dual evaluation.

### M8. Precision-recall decomposition missing (covered under C1)

Added Section 3.5 and threshold sensitivity plot.

### M9. Bootstrap confidence intervals missing

**New experiment:** 50 county-level bootstrap iterations.
- MAE: 7.13 (95% CI: 6.29-8.56)
- F1: 0.42 (95% CI: 0.25-0.59)
- Recall: 0.41 (95% CI: 0.20-0.61)

The wide CI for F1 (0.25-0.59) shows the model is highly sensitive to which counties are held out. Added Section 3.9.

### M10. Validation against raw Tellus data

Not feasible in this revision. Raw Tellus radiometric data requires a download request to GSI. Noted as the most important direction for future work.

### M11. Calibration plot missing

**New experiment:** Reliability diagram showing predicted-vs-actual by prediction bin. Key finding: for grid squares predicted to be 20-30%, the actual mean is 17.7% -- moderate undercalibration. For predictions above 30%, actual mean is 26.0%. Added calibration.png.

### M12. Missing comparison with European radon mapping literature

**Paper change:** Added references to Bossew et al. (2020), Cinelli et al. (2019), Gruber et al. (2013), Ielsch et al. (2010), and Appleton & Miles (2010) in the introduction.

---

## MINOR Issues

### m1. "No published study" novelty claim is trivially true

**Paper change:** Removed the novelty claim. The combination of standard methods does not constitute a novel contribution.

### m2. "Could prevent radon-related cancers" is speculative

**Paper change:** Removed the causal leap from the introduction. The model can guide measurement campaigns; the causal chain from model to cancer prevention has many links.

### m3. Target variable aggregation is unclear

**Paper change:** Added to limitations section: the number of homes measured per grid square is not reported, and grid squares with few measurements have high sampling variance.

### m4. Feature engineering decisions not fully justified

**Paper change:** Added to limitations: the 53:820 feature-to-observation ratio is in the danger zone, particularly for interaction features involving rare combinations.

### m5. Subsoil permeability as explicit feature

Not implemented in this revision. The binary subsoil type indicators are a crude proxy. Noted as future work.

### m6. Floor type interaction

Not implemented. Building characteristics from the BER database remain a promising direction but were not integrated.

### m7. Residual spatial analysis / Moran's I

Not implemented formally. County-level calibration analysis (Section 3.10, county_calibration.png) reveals spatially structured errors: Dublin is systematically overpredicted (+8.2), Sligo and Carlow severely underpredicted (-7.5 and -9.2). Formal Moran's I test noted as future work.

### m8. Alternative spatial CV schemes

Not implemented. County-grouped CV remains the only spatial evaluation. Block CV with spatial buffering noted as future work.

### m9. Missing soil gas radon literature

**Paper change:** Added Neznal et al. (2004) reference.

---

## Summary of Changes

1. **Title changed** to reflect grid-square prediction, not home-level
2. **Abstract rewritten** to be honest about F1 = 0.47, systematic underprediction, and the degraded data confound
3. **SHAP analysis added** (Section 3.4) showing different ranking from gain importance
4. **Precision/recall decomposition** (Section 3.5) with threshold sensitivity plot
5. **Systematic underprediction documented** (Section 3.6) with quantified bias table
6. **Granite-till interaction downgraded** (Section 3.7) from "key finding" to "valid geology, weak signal"
7. **Random CV comparison** (Section 3.8) matching Elio et al. and quantifying spatial inflation
8. **Bootstrap CIs** (Section 3.9) showing wide uncertainty
9. **Lithology vs radiometrics reframed** (Section 4.2) as confounded by degraded data
10. **Operational assessment added** (Section 4.3) honestly stating the model is not ready for health screening
11. **Five new references** added for European radon mapping and SHAP
12. **Six new plots**: shap_importance.png, shap_beeswarm.png, threshold_sensitivity.png, calibration.png, county_calibration.png, updated pred_vs_actual.png
13. **Conclusion rewritten** to frame results as exploratory analysis with severe limitations
