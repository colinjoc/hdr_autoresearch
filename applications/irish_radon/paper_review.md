# Adversarial Peer Review: "Predicting Dangerous Radon Levels in Irish Homes from Publicly Available Geological Data"

**Reviewer recommendation: Major Revision**

---

## 1. Claims vs Evidence

### F1 = 0.47 is poor classification performance, but paper frames it positively [CRITICAL]

The abstract reports HRA F1 = 0.47 as if it is a meaningful result. An F1 of 0.47 means the model misclassifies the majority of High Radon Areas -- it is getting the binary decision wrong more often than right (precision and recall are both well below 0.7). The pred_vs_actual.png plot confirms this: there is massive scatter, the correlation is only r = 0.43, and the model systematically underpredicts high-radon grid squares while overpredicting low-radon ones. The paper does not report precision and recall separately, making it impossible to assess whether the model is failing by missing dangerous areas (low recall -- a public health disaster) or by false-alarming on safe areas (low precision -- a resource waste). For a health-critical application, recall must be explicitly reported and discussed.

### "12% better than linear baseline" is a misleading framing of a tiny gain [MAJOR]

The improvement from Ridge (MAE 7.33) to the final model (MAE 6.42) is 0.91 percentage points on a target that ranges from 0 to 54%. The paper frames this as "12.3% improvement" (relative), which sounds substantial but is a marginal absolute gain. On the F1 metric, Ridge achieves 0.29 and the final model achieves 0.47 -- a larger jump, but from an unusable baseline to a barely usable one. The framing consistently emphasizes relative improvements while downplaying the absolute performance level, which is poor for a health-screening application.

### Granite-till interaction claim is interesting but weakly validated [MAJOR]

The paper's "key finding" is that a granite-by-till interaction feature ranks third in XGBoost gain importance at 6.5%. However: (a) gain-based importance in XGBoost is known to be biased toward high-cardinality and correlated features; (b) no SHAP analysis is presented to confirm the finding with a theoretically grounded attribution method; (c) the paper does not report how much MAE actually improved when this interaction was added vs. removed; (d) with 820 observations, the number of grid squares that are both granite AND till is likely very small (possibly < 50), making importance estimates unstable. The paper needs a proper ablation and a count of the relevant interaction subset.

### pred_vs_actual plot shows the model is substantially biased [MAJOR]

The scatter plot reveals systematic underprediction for grid squares above ~15% and overprediction for squares near 0%. The model is regressing toward the mean. For grid squares with >30% homes exceeding the reference level (the most dangerous areas), the model predicts 10-25% -- grossly underestimating the risk. This bias pattern is not discussed in the paper and is arguably the most important finding in the plot.

---

## 2. Scope vs Framing

### Title implies home-level prediction but model operates at 10km grid scale [MAJOR]

The title says "Predicting Dangerous Radon Levels in Irish Homes" but the model predicts the percentage of homes exceeding a threshold within 10-kilometre grid squares. The unit of prediction is a geographic area, not a home. Within a single grid square, radon can vary by orders of magnitude. The title should read "...in Irish Grid Squares" or "...in Irish Areas." The current title could mislead a homeowner into thinking the model provides dwelling-level risk assessment.

### The paper positions itself as an advance over Elio et al. but comparison is not apples-to-apples [MAJOR]

Section 3.6 acknowledges that Elio et al. used random CV (AUC 0.78-0.82) while this paper uses spatial CV. The paper cannot then claim to be "better" or "more honest" without running the same model under random CV for a fair comparison. Without this dual evaluation, the reader cannot determine whether the difference is due to better modeling or more conservative evaluation. Both numbers are needed.

---

## 3. Reproducibility

### Tellus data extraction is a critical weakness [CRITICAL]

The paper acknowledges that the Tellus GeoTIFF products are colour-rendered maps (RGB, 8-bit) rather than raw radiometric values. The pseudo-radiometric index formula "(Red - Blue + 247) / 494" is an ad hoc transformation of a color ramp that depends on the specific rendering palette chosen by GSI. If GSI changes the color map, updates the rendering, or uses a different stretch, this formula breaks entirely. The paper does not validate this pseudo-index against any known ground-truth uranium measurements. This is not a minor data processing choice -- it is the foundation of 8 of 53 features and the paper's claim about lithology outperforming radiometrics may be an artifact of using degraded radiometric data.

### Target variable aggregation is unclear [MINOR]

The EPA radon grid map records "the percentage of measured homes exceeding 200 Bq/m3." How many homes are measured per grid square? If some squares have only 5 measurements, the percentage estimate has enormous sampling variance. The paper does not report the distribution of measurement counts per grid square or weight observations by sample size.

### Feature engineering decisions not fully justified [MINOR]

53 features from 820 observations gives a features-to-observations ratio of ~1:15, which is in the danger zone for tree models prone to overfitting on sparse interactions. The paper does not discuss this ratio or apply any dimensionality reduction or feature selection beyond the HDR loop.

---

## 4. Missing Experiments

1. **SHAP analysis.** The paper uses XGBoost gain-based importance exclusively. SHAP values (TreeSHAP is available for XGBoost) would provide theoretically grounded, consistent feature attributions and enable investigation of interaction effects. The BER paper uses SHAP; this paper does not. This is a significant methodological gap. [MAJOR]

2. **Random CV comparison.** As noted above, running the same model under both random and spatial CV would quantify the spatial autocorrelation inflation and enable comparison with Elio et al. [MAJOR]

3. **Precision-recall decomposition.** For a health-screening application, the cost of false negatives (missing a dangerous area) vastly exceeds the cost of false positives. Precision and recall should be reported separately, and a threshold analysis optimizing for recall >= 0.9 should be presented. [CRITICAL]

4. **Bootstrap confidence intervals.** With 820 observations and county-grouped CV, fold-level variance is high. Bootstrap CIs on MAE, F1, and feature importance would indicate whether the granite-till finding is robust or an artifact of particular fold compositions. [MAJOR]

5. **Validation against raw Tellus data.** GSI provides raw Tellus point data through data download requests. Even a small validation comparing the pseudo-radiometric index to actual eU values in ppm for a subset of points would establish whether the color-map extraction preserves useful quantitative information. [MAJOR]

6. **Subsoil permeability as an explicit feature.** The paper hypothesizes that subsoil permeability matters for radon transport but only includes binary subsoil type indicators. A continuous permeability proxy (e.g., from the GSI subsoil texture classification: well-drained vs. poorly-drained) could test this hypothesis directly. [MINOR]

7. **Floor type interaction.** The paper mentions (Section 4.4) that building characteristics are not included. However, if the goal is practical risk prediction, combining geology with even crude building-era information (from the BER dataset) at the grid level would test whether dwelling susceptibility adds predictive power. [MINOR]

8. **Residual spatial analysis.** Mapping the prediction residuals would reveal whether errors are spatially structured (indicating missing spatial features) or random (indicating irreducible noise from within-grid-square heterogeneity). A Moran's I test on residuals would formalize this. [MINOR]

9. **Alternative spatial CV schemes.** County-grouped CV is one choice. Block CV with spatial buffering (Roberts et al. 2017, already cited) or leave-one-geological-unit-out CV would provide complementary perspectives on spatial generalization. [MINOR]

10. **Calibration plot.** For grid squares predicted to be HRA (>10%), what fraction actually are? A reliability diagram would show whether the model's continuous predictions are well-calibrated or systematically biased. [MAJOR]

---

## 5. Overclaiming

### "The dominant predictor is specific bedrock lithology, not the airborne uranium signal" [CRITICAL]

This is the paper's central claim. However, the airborne uranium signal was extracted from a color-rendered RGB image using an ad hoc formula, not from raw radiometric data. The finding that this degraded proxy underperforms categorical geological features could simply mean that color-map extraction destroyed the quantitative information in the uranium signal. The paper presents this as a geological insight ("geological structure matters more than bulk radiometric intensity") when it may be a data processing artifact. This distinction is fundamental and the paper must either validate the pseudo-index or heavily caveat this claim.

### "No published study has applied gradient-boosted tree models to Irish radon prediction with honest spatial cross-validation" [MINOR]

This novelty claim is narrow to the point of being trivially true. The individual components (gradient boosting, spatial CV, Irish radon) are all well-established. The combination being novel does not make the contribution significant unless the results are meaningfully better, which at F1 = 0.47 they arguably are not.

### "Could prevent radon-related cancers" (Introduction) [MINOR]

This is a speculative leap from a moderate-accuracy area-level prediction model to cancer prevention. The causal chain (model prediction leads to testing leads to mitigation leads to reduced exposure leads to fewer cancers) has many links, each with substantial friction. The claim should be hedged.

---

## 6. Literature Positioning

### Missing comparison with European radon mapping literature [MAJOR]

The paper cites Elio et al. (2020, 2022) as the only prior Irish radon prediction work. The broader European radon mapping literature is extensive and relevant:
- Bossew et al. (2020) on European radon mapping methodology
- Cinelli et al. (2019) on the European Atlas of Natural Radiation
- Gruber et al. (2013) on Austrian radon prediction from geology
- Ielsch et al. (2010) on French radon mapping
- Appleton & Miles (2010) on UK radon mapping from geology

These studies use similar approaches (geology + radiometrics) and would provide crucial context for evaluating whether F1 = 0.47 is typical or poor by international standards.

### Missing soil gas radon literature [MINOR]

The paper discusses radon transport through subsoil but does not cite the soil gas radon measurement literature (Neznal et al. 2004; Kemski et al. 2009) that directly validates the physical mechanisms invoked (permeability, uranium concentration in overburden).

### Statistical learning references are adequate [POSITIVE]

The XGBoost, LightGBM, spatial CV, and Roberts et al. references are appropriate and correctly cited.

---

## Severity Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 4 |
| MAJOR    | 10 |
| MINOR    | 8 |

The paper addresses a genuinely important public health question and uses appropriate spatial cross-validation methodology. However, the core results are weak (F1 = 0.47, r = 0.43), the central claim about lithology vs. radiometrics is confounded by the degraded Tellus data format, and the paper does not adequately characterize the failure modes of the model for the health-screening context where they matter most. The pred_vs_actual plot tells a more honest story than the text: this model is not yet accurate enough to guide public health decisions, and the paper should frame it as an exploratory analysis identifying promising geological predictors rather than a predictive tool. Major revision required, with particular attention to validating the Tellus data extraction, providing SHAP analysis, and honestly assessing whether F1 = 0.47 is operationally useful.
