# Predicting Radon Risk in Irish Grid Squares from Publicly Available Geological Data

## Abstract

Radon is a radioactive gas responsible for approximately 250 lung cancer deaths per year in Ireland. The Environmental Protection Agency (EPA) designates High Radon Areas (HRAs) using a 10-kilometre grid, but only about 3% of Irish homes have ever been tested. We ask whether publicly available geological data alone can predict which grid squares harbour dangerous radon levels. Using real measurements from the EPA radon survey (63,914 homes across 820 grid squares), airborne radiometric data from the Geological Survey Ireland (GSI) Tellus programme, bedrock geology at 1:500,000 scale, and national subsoil maps, we train gradient-boosted tree models to predict the percentage of homes exceeding the 200 Becquerels per cubic metre (Bq/m3) reference level in each grid square. Under strict spatial cross-validation grouped by county (ensuring no county appears in both training and test data), the best model achieves a mean absolute error (MAE) of 6.4 percentage points (95% CI: 6.3-8.6) and a High Radon Area classification F1 score of 0.47 (precision 0.52, recall 0.43). The model systematically underpredicts high-radon areas: for grid squares where more than 30% of homes exceed the reference level, the mean prediction is only 13%. SHAP analysis reveals that geographic location, the uranium-to-thorium ratio, and specific bedrock lithology are the strongest predictors, while the airborne uranium signal (extracted from colour-rendered GeoTIFFs rather than raw radiometric data) contributes less than specific geological units. This last finding may partly reflect the degraded format of the available Tellus data rather than a genuine geological hierarchy. Under standard random cross-validation the model achieves AUC 0.83, comparable to Elio et al. (2022), but spatial cross-validation reduces this to 0.74, quantifying a 10% inflation from spatial autocorrelation. The results represent an exploratory analysis identifying promising geological predictors rather than an operationally reliable screening tool.

## 1. Introduction

Radon-222 (Rn-222) is a naturally occurring radioactive gas produced by the decay of Radium-226 in the Uranium-238 chain. With a half-life of 3.82 days, radon migrates from bedrock through soil into buildings, where it accumulates in indoor air and decays into radioactive progeny that lodge in lung tissue [1, 2]. The International Agency for Research on Cancer classifies radon as a Group 1 carcinogen, and epidemiological evidence shows a 16% increase in lung cancer risk per 100 Bq/m3 increase in long-term radon exposure, with no safe threshold [3, 4].

Ireland has the eighth-highest average indoor radon concentration globally, with a national geometric mean of approximately 89 Bq/m3 [5]. About 7% of Irish dwellings exceed the national reference level of 200 Bq/m3, and 23% exceed the World Health Organization (WHO) recommended maximum of 100 Bq/m3 [6]. The EPA designates approximately 28% of Ireland's land area as HRA, defined as areas where more than 10% of homes are predicted to exceed 200 Bq/m3 [7]. Radon is estimated to cause approximately 250 lung cancer deaths annually in Ireland, making it the second leading cause of lung cancer after smoking [8].

Despite the health risk, only about 60,000 of Ireland's approximately 2 million homes (3%) have been measured for radon [5]. The low measurement rate means that most homes in High Radon Areas have never been tested. Predictive models that identify high-risk areas from geological data alone could guide targeted measurement campaigns and building regulation enforcement.

Previous work on Irish radon prediction has used logistic regression with geological variables. Elio and colleagues [9, 10] combined Tellus airborne equivalent uranium (eU) measurements with bedrock geology codes and quaternary classifications, reporting Area Under the Curve (AUC) values of 0.78-0.82 for HRA prediction. However, these results used standard random cross-validation, which inflates performance by 10-30% for spatially autocorrelated environmental data [11]. The broader European radon mapping literature provides important context: Bossew et al. [27] review European radon mapping methodology, Cinelli et al. [28] present the European Atlas of Natural Radiation, Gruber et al. [29] predict radon from geology in Austria, Ielsch et al. [30] map radon in France, and Appleton and Miles [31] map radon from geology in the UK. These studies use similar approaches (geology plus radiometrics) and report similar challenges with spatial prediction at coarse resolution.

In this paper, we address the question: can we predict which Irish grid squares have dangerous radon levels from publicly available geological data alone? We use five real data sources (EPA radon grid map, GSI Tellus radiometric survey, GSI bedrock geology, EPA national subsoils, and county boundaries), engineer 53 features capturing bedrock type, subsoil composition, airborne radiometric signals, and geology-subsoil interactions, and evaluate models under county-grouped spatial cross-validation that prevents any information leakage between geologically similar adjacent areas.

## 2. Data and Methods

### 2.1 Data Sources

All data used in this study is real and publicly available. No synthetic data was generated.

**EPA Radon Grid Map.** The primary target variable comes from the EPA radon map of Ireland, a GeoJSON dataset of 10-kilometre grid squares covering the Republic of Ireland. Each grid square records the percentage of measured homes exceeding the 200 Bq/m3 reference level, derived from the National Radon Survey of 63,914 homes measured through December 2019 [5]. After filtering invalid entries, the dataset contains 820 grid squares with valid measurements. The distribution is heavily right-skewed: the median is 2.2% (most areas have low radon), the mean is 7.1%, and the maximum is 53.5%.

**GSI Tellus Airborne Radiometrics.** The Geological Survey Ireland Tellus programme conducted airborne gamma-ray spectrometric surveys across Ireland from 2004 to 2022, measuring equivalent uranium (eU), equivalent thorium (eTh), and potassium (K) concentrations from fixed-wing aircraft at 56 metres altitude and 200-metre line spacing [12, 13]. The merged 2022 dataset provides national coverage at approximately 50-metre resolution.

**Critical data limitation:** The GeoTIFF products available for public download are colour-rendered maps (RGB, unsigned 8-bit) rather than raw radiometric values in physical units (ppm eU, ppm eTh, % K). We extract a pseudo-radiometric index from each pixel by computing (Red - Blue + 247) / 494, which maps the blue-to-red colour ramp to a [0, 1] scale. This transformation preserves the monotonic ordering of the underlying physical measurements but loses quantitative precision, particularly in the tails of the distribution. The formula depends on the specific colour palette chosen by GSI; if the rendering changes, the formula breaks. We have not validated this pseudo-index against raw eU values, so the radiometric features in this study are degraded proxies, not true radiometric measurements. This is a fundamental limitation that affects the interpretation of all comparisons between lithological and radiometric features (see Section 4.2).

For each 10-kilometre grid square, we sample at a 5 by 5 sub-grid (25 points) and compute the mean, standard deviation, and 90th percentile.

**GSI Bedrock Geology.** The all-island bedrock geology map at 1:500,000 scale [14] provides polygon geometries classified by lithological unit name and geological age bracket. We spatially join grid square centroids to the bedrock map, extracting the dominant unit and age, then derive binary indicator features for the major radon-relevant lithologies (granite, limestone, shale, sandstone) and geological ages (Carboniferous, Devonian, Ordovician-Silurian). Additionally, we one-hot encode the 15 most common lithological units and 10 most common age brackets.

**EPA National Subsoils.** The national subsoils (quaternary geology) dataset from the EPA [15] classifies subsoil deposits by category (till, peat, alluvium, sand and gravel, rock at surface, lacustrine), description (including parent material), and texture. We derive binary indicators for each major category and, critically, extract the parent material of till deposits (granite-derived, limestone-derived, shale-derived, sandstone-derived, metamorphic-derived). This is important because till inherits the geochemical signature of its parent bedrock: granite-derived till is enriched in uranium relative to limestone-derived till.

**County Boundaries.** EPA county boundary polygons assign each grid square to one of 27 spatial units (26 Republic of Ireland counties plus Northern Ireland border areas) for spatial cross-validation grouping.

### 2.2 Feature Engineering

We engineer 53 features across five categories:

1. **Tellus radiometric features** (8): eU mean, eTh mean, K mean, eU standard deviation, eU 90th percentile, eU/eTh ratio, total dose rate (0.0417K + 0.604eU + 0.310eTh, a standard composite index [16]), and log-transformed eU.

2. **Bedrock features** (32): Seven binary lithology indicators, 15 one-hot unit indicators, and 10 one-hot age indicators.

3. **Subsoil features** (9): Four category indicators (till, peat, alluvium, gravel) and five till parent material indicators.

4. **Geographic features** (2): Grid square centroid easting and northing in Irish National Grid coordinates.

5. **Interaction features** (8): Products of Tellus eU with each major bedrock type (granite, limestone, shale) and subsoil type (peat, gravel, till), plus granite-by-till and limestone-by-gravel interactions.

The interaction features are physically motivated: radon risk depends on both the uranium source (bedrock) and the transport pathway (subsoil permeability). A high uranium signal on granite bedrock overlain by permeable granitic till creates different radon dynamics than the same uranium signal on limestone bedrock overlain by peat.

### 2.3 Target Variable

The target is the continuous percentage of homes exceeding 200 Bq/m3 per grid square (range 0-54%). For classification evaluation, we threshold at 10% to define High Radon Areas, matching the EPA definition. The class balance is approximately 28% HRA, 72% non-HRA.

### 2.4 Models

We evaluate four model families:

1. **Ridge regression** (linear baseline): L2-regularised linear regression with alpha = 1.0.
2. **XGBoost** [17]: Gradient-boosted trees with 300-500 estimators, maximum depth 5-8, learning rate 0.03-0.05.
3. **LightGBM** [18]: Gradient-boosted trees with similar hyperparameters.
4. **Random Forest / ExtraTrees** [19]: Bagged ensemble trees with 300 estimators.

The final model is XGBoost with 500 estimators, maximum depth 6, learning rate 0.03, L1 regularisation (alpha = 0.1), and column subsampling ratio 0.7.

### 2.5 Evaluation: Spatial Cross-Validation

Standard random cross-validation is inappropriate for spatially autocorrelated environmental data because nearby observations share geological and meteorological conditions, leading to optimistic performance estimates [11, 20]. We use GroupKFold with county as the grouping variable, ensuring that no county appears in both training and test sets within any fold. With 27 county groups and 10 folds, each fold tests on 2-3 held-out counties.

This is a deliberately conservative evaluation. Counties share geological boundaries (the Leinster Granite spans Dublin, Wicklow, Wexford, Carlow, and Kilkenny), so holding out an entire county removes information about its geological context from training. The resulting metrics represent the model's ability to generalise to entirely unseen regions.

We report:
- Mean Absolute Error (MAE) on the continuous target (percentage points).
- F1 score for HRA classification (threshold at 10%).
- Per-county MAE for diagnostic inspection.

## 3. Results

### 3.1 Phase 0.5: Linear Baseline

Ridge regression on 21 baseline features (Tellus radiometric, bedrock indicators, subsoil indicators, geographic coordinates) achieves MAE = 7.33 +/- 1.49 and HRA F1 = 0.29 under spatial cross-validation. The model captures the broad geological pattern but cannot represent the nonlinear interactions between bedrock type and subsoil permeability.

### 3.2 Phase 1: Model Tournament

Table 1 shows the tournament results with baseline features.

| Model | MAE | MAE std | HRA F1 |
|---|---|---|---|
| Ridge | 7.33 | 1.49 | 0.29 |
| XGBoost | 6.58 | 1.31 | 0.47 |
| LightGBM | 6.53 | 1.53 | 0.47 |
| Random Forest | 6.64 | 1.44 | 0.43 |
| ExtraTrees | 6.94 | 1.42 | 0.46 |

All tree-based models substantially outperform Ridge, with XGBoost and LightGBM effectively tied. The jump from F1 = 0.29 (Ridge) to F1 = 0.47 (XGBoost) reflects the models' ability to learn threshold-like decision rules on geological features that linear models cannot represent.

### 3.3 Phase 2: Feature Engineering and HDR Loop

Starting from XGBoost on baseline features (MAE = 6.58), we incrementally test feature additions using the Hypothesis-Driven Research (HDR) methodology, keeping features that improve the held-out metric and reverting those that do not.

**Tellus-derived features** (eU standard deviation, 90th percentile, eU/eTh ratio, total dose rate, log eU): These reduce MAE from 6.58 to 6.45, a 2.0% improvement. The eU/eTh ratio is particularly informative because it indicates uranium enrichment relative to thorium, a signature of specific mineralisation processes that produce radon-generating minerals.

**Interaction features** (eU crossed with granite, limestone, shale, peat, gravel, till; granite crossed with till; limestone crossed with gravel): Adding interactions does not improve MAE when tested in isolation (MAE = 6.48). In ablation analysis, removing all interactions from the full model slightly improves MAE to 6.37, suggesting these features do not contribute to out-of-fold prediction despite appearing important in gain-based metrics (see Section 3.7).

**One-hot bedrock units and ages** (25 additional binary features for specific lithological units and geological age brackets): The full model achieves MAE = 6.42, a 12.3% improvement over the Ridge baseline and 2.4% over the XGBoost baseline.

The improvement trajectory is: Ridge baseline (7.33) to XGBoost baseline (6.58, 10.2% gain) to enhanced features (6.45, 12.0% gain) to full model (6.42, 12.4% gain). The largest single gain comes from switching from linear to tree-based models, with feature engineering providing incremental but meaningful improvements.

### 3.4 Feature Importance

We report feature importance using both XGBoost gain and SHAP values (TreeSHAP [32]). These methods tell different stories, and the discrepancy is informative.

**XGBoost gain-based importance** ranks specific bedrock lithological units highest: Carboniferous marine shelf limestone (9.2%), granite/granodiorite (7.4%), Ordovician-Silurian bedrock (4.2%), and the eU x granite interaction (3.9%). The granite-by-till interaction ranks modestly (1.8%) in the full training fit, lower than the 6.5% observed in earlier cross-validation folds. Gain-based importance is known to be biased toward features used in many splits, including low-cardinality binary features that appear early in trees [32].

**SHAP values** (mean absolute SHAP, computed on the full training set) provide a theoretically grounded attribution that accounts for feature interactions. The SHAP ranking is substantially different:

1. **Geographic easting** (centroid_x): 1.83 -- location alone is the strongest single predictor, likely because it captures unmeasured east-west geological trends.
2. **Uranium/thorium ratio** (eU_eTh_ratio): 1.26 -- this ratio indicates uranium enrichment relative to thorium, a signature of specific mineralisation processes.
3. **Carboniferous marine shelf limestone**: 1.20 -- consistent with gain importance.
4. **Geographic northing** (centroid_y): 1.18 -- latitude captures the north-south geological gradient.
5. **Uranium variability** (eU_std): 0.85 -- within-grid-square variability of the pseudo-radiometric signal.
6. **eU 90th percentile**: 0.56
7. **eU mean**: 0.51
8. **Potassium** (K_mean): 0.48

By SHAP, radiometric features collectively contribute more than by gain importance, and geographic coordinates are the strongest predictors. The granite-by-till interaction has mean |SHAP| of only 0.034 overall, but for the 17 grid squares where it equals 1, the mean SHAP value is +0.815 -- a locally large effect on a very small subset (see Section 3.7).

The discrepancy between gain and SHAP rankings is important. Gain importance overstates the global contribution of binary geological indicators (which appear in many tree splits but have small marginal effects) and understates the contribution of continuous features like the eU/eTh ratio and geographic coordinates. The SHAP ranking suggests that radiometric features are more important globally than gain importance indicates, though the caveat about degraded Tellus data (Section 2.1) means we cannot determine whether raw radiometric values would be even stronger.

### 3.5 Precision, Recall, and the Cost of Missing Dangerous Areas

For a health-screening application, the decomposition of F1 into precision and recall is critical because the cost of false negatives (missing a dangerous area) far exceeds the cost of false positives (flagging a safe area for testing).

At the EPA's HRA threshold of 10%, the model achieves:
- **Precision: 0.52** -- of areas the model flags as HRA, 52% actually are.
- **Recall: 0.43** -- of areas that are actually HRA, the model identifies only 43%.
- **F1: 0.47**

The model misses 132 out of 231 actual High Radon Areas. These missed areas have a mean actual radon percentage of 18.6% (range 10-45%), meaning they are genuinely dangerous areas where the model incorrectly predicts safety.

Lowering the classification threshold improves recall at the cost of precision:
- At threshold 7.0%: precision 0.46, recall 0.72, F1 0.56 (optimal F1)
- At threshold 3.5%: precision 0.35, recall 0.90, F1 0.50

To achieve recall of 0.9 (missing only 10% of dangerous areas), the threshold must be lowered to 3.5%, which means the model would flag 60% of all grid squares as potentially dangerous -- at that point, the model provides little screening value over universal testing.

### 3.6 Systematic Underprediction of High-Radon Areas

The model exhibits severe regression to the mean, systematically underpredicting the most dangerous areas:

| Actual radon range | n | Mean actual | Mean predicted | Mean bias | HRA miss rate |
|---|---|---|---|---|---|
| 0-5% | 491 | 0.9% | 5.4% | +4.4 | N/A |
| 5-10% | 98 | 7.3% | 7.9% | +0.6 | N/A |
| 10-15% | 93 | 12.2% | 9.5% | -2.7 | 67% |
| 15-20% | 40 | 17.5% | 10.0% | -7.5 | 60% |
| 20-30% | 66 | 24.5% | 11.2% | -13.2 | 47% |
| 30-55% | 32 | 38.4% | 13.0% | -25.4 | 47% |

For the 32 grid squares where more than 30% of homes exceed the reference level (the most dangerous areas in Ireland), the model predicts a mean of only 13.0% -- a 25.4 percentage point underprediction. Nearly half of these extremely dangerous areas are classified as non-HRA by the model. This is the most important finding in the analysis: the model fails most severely exactly where accurate prediction matters most for public health.

### 3.7 The Granite-Till Interaction: A Real but Unstable Signal

The granite-by-till interaction was originally reported as the third most important feature by XGBoost gain (6.5%). Additional analysis reveals important caveats:

- Only 17 out of 820 grid squares (2.1%) have both granite bedrock and till subsoil.
- These 17 squares have mean radon of 14.0% versus the overall mean of 7.1% -- a genuine elevation.
- SHAP analysis confirms a locally meaningful effect: mean SHAP = +0.815 for these 17 squares, but mean |SHAP| = 0.034 globally (ranking well below radiometric and geographic features).
- Bootstrap confidence intervals on the granite-till gain importance: 0.018 (95% CI: 0.000-0.048). The importance is not stable across resamples.
- Feature ablation shows that removing the granite-till interaction barely changes performance (MAE 6.46 vs 6.43), and removing all eight interaction features actually *improves* MAE slightly to 6.37.

The granite-till combination is genuinely associated with elevated radon in the data, consistent with the physical mechanism (double uranium source plus permeable transport pathway). However, its importance in the predictive model is overstated by gain-based metrics, it is supported by too few observations (17) to be robust, and its removal does not degrade model performance. The interaction is a valid geological observation but not a reliable predictive feature at this sample size.

### 3.8 Random Cross-Validation Comparison

To enable comparison with Elio et al. [9, 10], we evaluated the same model under both spatial (county-grouped) and standard random 10-fold cross-validation:

| Metric | Spatial CV | Random CV | Inflation |
|---|---|---|---|
| MAE | 6.43 | 5.54 | 16% |
| HRA F1 | 0.47 | 0.60 | 28% |
| Correlation | 0.43 | 0.60 | 40% |
| AUC | 0.74 | 0.83 | 11% |

Random CV inflates all metrics substantially. Our random CV AUC of 0.83 is comparable to Elio et al.'s reported AUC of 0.78-0.82, suggesting that the difference between their results and our spatial CV results is primarily due to evaluation methodology, not modelling improvements. The 10-11% AUC inflation from random CV is consistent with the literature on spatial autocorrelation bias [11].

### 3.9 Bootstrap Confidence Intervals

County-level bootstrap (50 iterations, resampling counties with replacement) provides uncertainty estimates:

- MAE: 7.13 (95% CI: 6.29-8.56)
- F1: 0.42 (95% CI: 0.25-0.59)
- Precision: 0.44 (95% CI: 0.28-0.59)
- Recall: 0.41 (95% CI: 0.20-0.61)

The wide confidence intervals, particularly for F1 (0.25-0.59) and recall (0.20-0.61), indicate that model performance is highly sensitive to which counties are included. A bad draw of held-out counties can reduce F1 to 0.25 -- barely better than random for HRA classification.

### 3.10 Spatial Variation in Model Performance

The model's per-county MAE varies from 2.8 (Kerry) to 12.1 (Sligo). The hardest counties to predict share a common characteristic: geological complexity at the county boundary.

**Sligo** (MAE = 12.1) has a sharp transition from the high-radon Benbulben Formation (Mississippian limestone and shale) to the low-radon Ox Mountains (Precambrian metamorphic). Grid squares straddling this transition have radon rates that depend on exactly where within the 10-kilometre square the homes are located.

**Carlow** (MAE = 11.9) sits on the eastern margin of the Leinster Granite batholith, where granite gives way to Ordovician volcanics within a few kilometres. The 10-kilometre grid resolution cannot capture this transition.

**Kerry** (MAE = 2.8) is the easiest county because it has relatively uniform geology (Devonian sandstones and Namurian shales) with consistently high radon across most of the county.

These patterns confirm that prediction error is driven by within-grid-square geological heterogeneity, not model inadequacy. Finer spatial resolution would reduce this irreducible error.

### 3.11 Comparison with Prior Work

The random CV experiment (Section 3.8) enables direct comparison with Elio et al. [9, 10]. Under random CV, our model achieves AUC 0.83, comparable to their reported 0.78-0.82. Under spatial CV, our AUC drops to 0.74. This demonstrates that the difference between studies is primarily due to evaluation methodology: spatial CV reveals the true difficulty of predicting radon in unseen regions.

Our MAE of 6.4 percentage points means that for a typical grid square with 7% of homes above the reference level, the model's prediction is off by about 6 points. For a grid square with 20% above the reference level (a clear High Radon Area), the model typically predicts only 10-12% -- often misclassifying the area as safe (Section 3.6).

## 4. Discussion

### 4.1 The Granite-Till Interaction: Valid Geology, Weak Signal

The granite-by-till interaction captures a well-established physical mechanism [21, 22, 33]. Granite bedrock contains elevated uranium concentrations (5-20 parts per million versus a crustal average of approximately 2.7 parts per million). When glacial processes erode granite and deposit the material as till, the till inherits the uranium-enriched geochemistry of its parent rock. Areas with granite bedrock overlain by granite-derived till have a "double source" of radon.

However, the predictive importance of this interaction is much weaker than originally framed. Only 17 grid squares in the dataset exhibit this combination, and while their mean radon (14.0%) is elevated above the dataset mean (7.1%), the signal is not robust: bootstrap confidence intervals on the gain importance include zero, and ablation shows no MAE improvement from including the interaction. The physical mechanism is valid, but at the 10-kilometre grid scale with 820 observations, the dataset is too small to exploit it reliably.

### 4.2 Lithology vs Radiometrics: Confounded by Degraded Data

By XGBoost gain importance, specific bedrock lithological units rank above the Tellus airborne uranium signal. However, SHAP analysis tells a more nuanced story: the uranium-to-thorium ratio (eU_eTh_ratio) is the second most important feature globally, and radiometric features collectively contribute substantially. The apparent dominance of lithology over radiometrics in gain importance may be partly an artifact of the degraded Tellus data format.

**The data confounding problem.** The available Tellus GeoTIFF products are colour-rendered RGB images, not raw radiometric values in physical units. Our pseudo-radiometric index preserves the monotonic ordering but loses quantitative precision, particularly in the distribution tails where the colour ramp saturates. This means the radiometric features are degraded proxies competing against categorical geological features that suffer no such degradation. Finding that the degraded proxy underperforms categorical features could simply mean that colour-map extraction destroyed the quantitative information in the uranium signal. We cannot determine from this analysis whether raw eU values (in ppm) would outperform lithological features.

**Three factors contribute to the observed ranking, but their relative weight is unknown:**

1. **Data degradation.** The colour-map extraction artificially weakens radiometric features. This is an artifact, not a geological finding.

2. **Scale mismatch.** The Tellus survey measures at approximately 50-metre resolution, but the target is averaged over 10-kilometre grid squares. At the grid scale, the variance of eU within a square is large, and the mean signal is diluted by non-residential areas.

3. **Lithology encodes transport, not just source.** The bedrock unit name implicitly encodes permeability, fracture density, karst development, and weathering characteristics, all of which affect radon transport independently of uranium source strength. The Carboniferous marine shelf limestone, the top-ranked feature, has moderate uranium but high permeability from karstification.

The third factor is a genuine geological insight, but we cannot cleanly separate it from the first two without access to raw radiometric data. Any claim that "geological structure matters more than bulk radiometric intensity" requires validation against raw Tellus data, which was not available for this study.

### 4.3 Operational Assessment

With F1 = 0.47, precision 0.52, and recall 0.43, the model is not accurate enough to guide public health decisions. Specifically:
- It misses 57% of actual High Radon Areas -- a false-negative rate that is unacceptable for health screening.
- It systematically underpredicts the most dangerous areas by 13-25 percentage points.
- Its confidence intervals are wide (F1: 0.25-0.59), meaning performance is unstable across regions.

The model is best understood as an exploratory analysis that identifies geological features correlated with radon risk, not as an operational screening tool. The county-level calibration analysis reveals systematic biases: Dublin is overpredicted (mean bias +8.2), while Sligo and Carlow are severely underpredicted (bias -7.5 and -9.2 respectively).

### 4.4 Implications for Future Work

Despite its limitations for direct screening, the analysis points toward productive directions:

1. **Target measurement campaigns.** Counties where the model is most uncertain (Sligo, Carlow, Louth) contain grid squares where geological complexity means the 10-kilometre grid resolution is inadequate. These are the areas where additional measurement would be most informative.

2. **Retrofit screening.** Ireland's National Retrofit Plan aims to retrofit 500,000 homes for energy efficiency by 2030 [23]. Homes on granite bedrock that undergo deep energy retrofits (reducing ventilation) may experience increased indoor radon [25, 26]. The geological features identified here could contribute to a retrofit risk-screening tool, but only as one input among many, not as a standalone predictor.

3. **Raw Tellus data.** The most important next step is to validate results against raw radiometric data from GSI, which would resolve the confounding between data degradation and genuine geological hierarchy.

### 4.5 Limitations

Several limitations constrain this analysis:

**Tellus data format (critical).** The available Tellus GeoTIFF products are colour-rendered images rather than raw radiometric data in physical units. This is not a minor processing detail -- it is the foundation of 8 of 53 features and directly confounds the comparison between lithological and radiometric predictors. Access to raw eU values in ppm is necessary to determine whether the apparent lithology-over-radiometrics hierarchy is genuine or an artifact.

**Systematic underprediction (critical).** The model underpredicts by 13-25 percentage points in the most dangerous areas. For a health-screening application, this failure mode is the most consequential: the areas where accurate prediction matters most are exactly where the model performs worst. This is an inherent limitation of regression-to-the-mean in tree-based models trained on right-skewed targets.

**Target variable quality.** The EPA radon grid records the percentage of measured homes exceeding 200 Bq/m3, but the number of homes measured per grid square is not reported. Grid squares with few measurements have high sampling variance in the target, adding noise that the model cannot distinguish from geological signal.

**Grid resolution.** The 10-kilometre EPA radon grid averages over substantial geological heterogeneity. Within a single grid square, radon levels can vary by more than an order of magnitude [24]. Finer-resolution prediction would require individual home measurements.

**No building features.** This study uses geological data only. Building characteristics (floor type, ventilation, airtightness) from the SEAI Building Energy Rating (BER) database [25, 26] would likely improve predictions at finer spatial scales.

**Small sample size for interactions.** With 820 observations and 53 features, the features-to-observations ratio is approximately 1:15. Interaction features involving rare geological combinations (e.g., granite-till, n=17) are supported by too few observations for robust estimation.

## 5. Conclusion

We evaluate whether publicly available geological data can predict Irish radon risk areas, using gradient-boosted tree models under strict county-grouped spatial cross-validation. The model achieves MAE 6.4 percentage points and HRA F1 0.47 (precision 0.52, recall 0.43), a modest improvement over linear baselines but not operationally reliable for health screening. The model systematically underpredicts the most dangerous areas by 13-25 percentage points and misses 57% of actual High Radon Areas.

SHAP analysis reveals that geographic location, the uranium-to-thorium ratio, and specific bedrock lithologies are the strongest predictors. The originally reported finding that lithology outperforms radiometrics is confounded by the degraded format of the available Tellus data (colour-rendered GeoTIFFs rather than raw values); without validation against raw radiometric data, we cannot determine whether this reflects genuine geological mechanisms or data processing artifacts. The granite-till interaction is associated with elevated radon in 17 grid squares, consistent with known geochemistry, but is too sparsely supported to be a robust predictive feature.

Under random cross-validation, the model achieves AUC 0.83, comparable to Elio et al. (0.78-0.82), demonstrating that the difference between studies is due to evaluation methodology. The 10% AUC inflation from random CV confirms the importance of spatial cross-validation for environmental prediction.

Future work should prioritize obtaining raw Tellus radiometric data in physical units, incorporating building characteristics from the BER database, and validating the pseudo-radiometric index against known ground-truth uranium measurements. The current results represent an exploratory analysis that identifies promising geological correlates of radon risk, not a predictive tool ready for public health deployment.

## References

[1] Nazaroff, W.W. and Nero, A.V. (1988). Radon and its Decay Products in Indoor Air. Wiley.

[2] Tanner, A.B. (1964). Radon migration in the ground: A supplementary review. In: The Natural Radiation Environment III, pp. 5-56.

[3] Darby, S. et al. (2005). Radon in homes and risk of lung cancer: collaborative analysis of individual data from 13 European case-control studies. BMJ, 330(7485), 223.

[4] Darby, S. et al. (2006). Residential radon and lung cancer: detailed results of a collaborative analysis of individual data on 7148 persons with lung cancer and 14208 persons without lung cancer in 13 European countries. Scandinavian Journal of Work, Environment and Health, 32(Suppl 1), 1-84.

[5] Fennell, S.G. et al. (2002). Radon in dwellings: The Irish National Radon Survey. Radiological Protection Institute of Ireland.

[6] McLaughlin, J.P. (2012). An overview of the radon situation in Ireland. Radiation Protection Dosimetry, 152(1-3), 13-18.

[7] EPA Ireland (2025). Radon Map. Available at: https://www.epa.ie/environment-and-you/radon/radon-map/

[8] Breen, M.S. et al. (2015). Assessment of exposure to radon in Irish dwellings. Irish Medical Journal, 108(1), 12-15.

[9] Elio, J. et al. (2020). Logistic regression model for detecting radon-prone areas in Ireland. Science of The Total Environment, 714, 136765.

[10] Elio, J. et al. (2022). Estimation of residential radon in Ireland using geology, TELLUS radiometric data and indoor radon measurements. Journal of Environmental Radioactivity, 249, 106903.

[11] Roberts, D.R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography, 40(8), 913-929.

[12] Young, M.E. and Donald, A.W. (2013). A Guide to the Tellus Data. Geological Survey of Northern Ireland.

[13] Hodgson, J.A. and Young, M.E. (2016). The Tellus Airborne Geophysical Survey of Ireland. In: Geophysics for the Mineral Exploration Geoscientist, Cambridge University Press.

[14] GSI (2023). Bedrock Geology of Ireland, 1:500,000 scale. Geological Survey Ireland.

[15] EPA Ireland (2023). National Subsoils Map. Environmental Protection Agency.

[16] IAEA (2003). Guidelines for radioelement mapping using gamma ray spectrometry data. IAEA-TECDOC-1363.

[17] Chen, T. and Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. In: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, pp. 785-794.

[18] Ke, G. et al. (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree. In: Advances in Neural Information Processing Systems 30, pp. 3146-3154.

[19] Geurts, P. et al. (2006). Extremely Randomized Trees. Machine Learning, 63(1), 3-42.

[20] Valavi, R. et al. (2019). blockCV: An R package for generating spatially or environmentally separated folds for k-fold cross-validation of species distribution models. Methods in Ecology and Evolution, 10(2), 225-232.

[21] O'Connor, P.J. et al. (1993). Airborne gamma-ray survey results for the Leinster Granite Batholith. GSI Technical Report.

[22] Meehan, R. (2015). Subsoils of Ireland: Quaternary Geology Map Guide. GSI.

[23] DEHLG (2022). National Retrofit Plan. Department of the Environment, Heritage and Local Government.

[24] Murray, M. et al. (2009). Methodology for designation of radon-prone areas. RPII Technical Report.

[25] Font Guiteras, L. (2022). Impact of energy efficiency measures on indoor radon: A meta-analysis. Building and Environment, 208, 108550.

[26] Colgan, S. et al. (2024). UNVEIL: Understanding the Impact of Energy Efficiency Retrofits on Indoor Radon in Ireland. EPA Research Report 273.

[27] Bossew, P. et al. (2020). Development of a geogenic radon hazard index -- concept, history, experiences. International Journal of Environmental Research and Public Health, 17(11), 4134.

[28] Cinelli, G. et al. (2019). European Atlas of Natural Radiation. European Commission, Joint Research Centre.

[29] Gruber, V. et al. (2013). The Austrian radon project. Radiation Protection Dosimetry, 157(1-3), 9-12.

[30] Ielsch, G. et al. (2010). Radon potential mapping in France. Journal of Environmental Radioactivity, 101(8), 633-641.

[31] Appleton, J.D. and Miles, J.C.H. (2010). A statistical evaluation of the geogenic controls on indoor radon concentrations and radon risk. Journal of Environmental Radioactivity, 101(10), 799-803.

[32] Lundberg, S.M. and Lee, S.I. (2017). A Unified Approach to Interpreting Model Predictions. In: Advances in Neural Information Processing Systems 30, pp. 4765-4774.

[33] Neznal, M. et al. (2004). The new method for assessing the radon risk of building sites. Czech Geological Survey Special Papers 16.
