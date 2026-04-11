# Review Signoff: Irish Radon Paper

**Reviewer recommendation after revision: Accept with Minor Revisions**

---

## Assessment of Revisions

### CRITICAL issues: All addressed substantively

1. **F1 = 0.47 framed positively (C1):** The full precision/recall decomposition is now in the paper: precision 0.52, recall 0.43. The paper honestly documents that the model misses 132 of 231 actual HRAs and provides the threshold sensitivity analysis showing that recall >= 0.9 requires lowering the threshold to 3.5% (at which point the model flags 60% of grid squares). The abstract and conclusion have been reframed from "promising tool" to "exploratory analysis." **Resolved.**

2. **Tellus data degradation confounds lithology finding (C2):** This is the most important correction. The paper now has an explicit critical data limitation paragraph in Section 2.1, a completely rewritten Section 4.2 ("Confounded by Degraded Data"), and the abstract states the finding "may partly reflect the degraded format." The SHAP analysis also shows that radiometric features are more important by SHAP than by gain, consistent with the degradation hypothesis suppressing but not eliminating the radiometric signal. The paper cannot resolve this confound without raw data, and it says so honestly. **Resolved to the extent possible without raw data.**

3. **Systematic underprediction of high-radon areas (C3):** New Section 3.6 provides a quantified bias table. The most damning finding: grid squares with >30% actual radon get predicted at 13.0% (25.4 pp underprediction). This is now the most prominently placed empirical finding in the results section. **Resolved.**

4. **No SHAP analysis (C4):** Full TreeSHAP analysis added, revealing a substantially different importance ranking from gain. The discrepancy itself is informative and well-discussed. Two new plots (shap_importance.png, shap_beeswarm.png) are clear and well-designed. **Resolved.**

### MAJOR issues: All addressed

- M1 (misleading framing): Absolute and relative improvements now both reported.
- M2 (granite-till weakly validated): Ablation shows no MAE improvement; bootstrap CI includes zero; n=17. All documented in new Section 3.7. The interaction is downgraded from "key finding" to "valid geology, weak signal."
- M3 (pred_vs_actual bias): Covered under C3.
- M4 (title): Changed to "Predicting Radon Risk in Irish Grid Squares."
- M5 (Elio comparison not apples-to-apples): Random CV experiment added. Random AUC 0.83 matches Elio et al.'s 0.78-0.82, demonstrating the difference is evaluation methodology.
- M6 (SHAP): Covered under C4.
- M7 (random CV): Covered under M5.
- M8 (precision-recall): Covered under C1.
- M9 (bootstrap CIs): 50-iteration county bootstrap. Wide CIs (F1: 0.25-0.59) honestly reported.
- M10 (raw Tellus validation): Not feasible; correctly noted as most important future work.
- M11 (calibration plot): Added. Shows moderate undercalibration at high predictions.
- M12 (European literature): Five new references added.

### MINOR issues: Mostly addressed

- m1 (novelty claim): Removed. Acceptable.
- m2 (cancer prevention claim): Removed. Acceptable.
- m3 (target aggregation): Noted as limitation. Acceptable.
- m4 (feature-to-observation ratio): Noted as limitation. Acceptable.
- m5 (subsoil permeability): Not implemented; future work. Acceptable.
- m6 (floor type interaction): Not implemented; future work. Acceptable.
- m7 (residual spatial analysis): County-level calibration provided; formal Moran's I deferred. Acceptable.
- m8 (alternative spatial CV): Not implemented. County-grouped CV remains the sole spatial evaluation, which is a minor gap. Acceptable.
- m9 (soil gas literature): Neznal et al. added.

### New findings from the revision

The revision surfaced several important results not in the original:

1. **The SHAP vs gain discrepancy** reveals that gain importance systematically overstates binary geological features and understates continuous radiometric features. This is a methodological finding relevant beyond this paper.

2. **The random CV experiment** confirms that spatial autocorrelation inflates AUC by approximately 10% and that our model performs comparably to Elio et al. under the same evaluation methodology.

3. **The ablation study** shows that removing all interaction features *improves* MAE slightly (6.37 vs 6.43), meaning the paper's original emphasis on interactions was misguided.

4. **The bootstrap CIs** show that F1 can range from 0.25 to 0.59 depending on which counties are held out, indicating that the single-point F1 = 0.47 gives a misleadingly precise impression of model reliability.

### Remaining concerns (minor)

1. **Geographic features dominate SHAP but are not discussed as proxy variables.** Centroid_x (easting) being the top SHAP feature suggests the model is learning a spatial field -- essentially interpolating radon risk from geographic location rather than from geology. This raises the question of whether the geological features are providing genuine mechanistic insight or merely co-varying with location. The paper could add a brief note distinguishing the geographic features' contribution from genuine geological prediction.

2. **The SHAP analysis is on the full training set, not on out-of-fold predictions.** This means the SHAP values reflect the model's in-sample attributions, which may differ from the features' contribution to held-out prediction. Cross-validated SHAP would be more rigorous but is computationally expensive.

3. **The paper still does not discuss the number of homes per grid square.** Even as a rough histogram from the county-level data (total county measurements divided by county grid squares), this would provide a useful estimate of target variable noise.

These are minor points that do not prevent acceptance. The paper has been transformed from one that overclaimed on F1 = 0.47, presented a confounded comparison as a geological finding, and ignored its model's most dangerous failure mode, to one that honestly characterizes a modest exploratory analysis with clear limitations and productive future directions.

---

**Signed off:** 2026-04-10
**Verdict:** The revisions are thorough and honest. The paper now accurately represents an exploratory analysis of geological predictors for Irish radon risk, with appropriate caveats about the degraded radiometric data, the model's systematic underprediction of dangerous areas, and the instability of the granite-till finding. Accept with the minor suggestions above.
