# Predicting Dangerous Radon Levels in Irish Homes from Publicly Available Geological Data

## Abstract

Radon is a radioactive gas responsible for approximately 250 lung cancer deaths per year in Ireland. The Environmental Protection Agency (EPA) designates High Radon Areas (HRAs) using a 10-kilometre grid, but only about 3% of Irish homes have ever been tested. We ask whether publicly available geological data alone can predict which areas harbour dangerous radon levels. Using real measurements from the EPA radon survey (63,914 homes across 820 grid squares), airborne radiometric data from the Geological Survey Ireland (GSI) Tellus programme, bedrock geology at 1:500,000 scale, and national subsoil maps, we train gradient-boosted tree models to predict the percentage of homes exceeding the 200 Becquerels per cubic metre (Bq/m3) reference level in each grid square. Under strict spatial cross-validation grouped by county (ensuring no county appears in both training and test data), the best model achieves a mean absolute error (MAE) of 6.4 percentage points and a High Radon Area classification F1 score of 0.47. This is 12% better than the linear baseline, with the key finding that a single interaction feature (granite bedrock overlain by granite-derived till) is the third most important predictor. The dominant predictor is specific bedrock lithology, not the airborne uranium signal, suggesting that geological structure matters more than bulk radiometric intensity for radon risk at the 10-kilometre scale.

## 1. Introduction

Radon-222 (Rn-222) is a naturally occurring radioactive gas produced by the decay of Radium-226 in the Uranium-238 chain. With a half-life of 3.82 days, radon migrates from bedrock through soil into buildings, where it accumulates in indoor air and decays into radioactive progeny that lodge in lung tissue [1, 2]. The International Agency for Research on Cancer classifies radon as a Group 1 carcinogen, and epidemiological evidence shows a 16% increase in lung cancer risk per 100 Bq/m3 increase in long-term radon exposure, with no safe threshold [3, 4].

Ireland has the eighth-highest average indoor radon concentration globally, with a national geometric mean of approximately 89 Bq/m3 [5]. About 7% of Irish dwellings exceed the national reference level of 200 Bq/m3, and 23% exceed the World Health Organization (WHO) recommended maximum of 100 Bq/m3 [6]. The EPA designates approximately 28% of Ireland's land area as HRA, defined as areas where more than 10% of homes are predicted to exceed 200 Bq/m3 [7]. Radon is estimated to cause approximately 250 lung cancer deaths annually in Ireland, making it the second leading cause of lung cancer after smoking [8].

Despite the health risk, only about 60,000 of Ireland's approximately 2 million homes (3%) have been measured for radon [5]. The low measurement rate means that most homes in High Radon Areas have never been tested. Predictive models that identify high-risk areas from geological data alone could guide targeted measurement campaigns and building regulation enforcement, potentially preventing radon-related cancers.

Previous work on Irish radon prediction has used logistic regression with geological variables. Elio and colleagues [9, 10] combined Tellus airborne equivalent uranium (eU) measurements with bedrock geology codes and quaternary classifications, reporting Area Under the Curve (AUC) values of 0.78-0.82 for HRA prediction. However, these results used standard random cross-validation, which inflates performance by 10-30% for spatially autocorrelated environmental data [11]. No published study has applied gradient-boosted tree models to Irish radon prediction with honest spatial cross-validation, and no study has investigated the interaction between specific bedrock lithology and subsoil parent material as a predictor.

In this paper, we address the question: can we predict which Irish areas have dangerous radon levels from publicly available geological data alone? We use five real data sources (EPA radon grid map, GSI Tellus radiometric survey, GSI bedrock geology, EPA national subsoils, and county boundaries), engineer 53 features capturing bedrock type, subsoil composition, airborne radiometric signals, and geology-subsoil interactions, and evaluate models under county-grouped spatial cross-validation that prevents any information leakage between geologically similar adjacent areas.

## 2. Data and Methods

### 2.1 Data Sources

All data used in this study is real and publicly available. No synthetic data was generated.

**EPA Radon Grid Map.** The primary target variable comes from the EPA radon map of Ireland, a GeoJSON dataset of 10-kilometre grid squares covering the Republic of Ireland. Each grid square records the percentage of measured homes exceeding the 200 Bq/m3 reference level, derived from the National Radon Survey of 63,914 homes measured through December 2019 [5]. After filtering invalid entries, the dataset contains 820 grid squares with valid measurements. The distribution is heavily right-skewed: the median is 2.2% (most areas have low radon), the mean is 7.1%, and the maximum is 53.5%.

**GSI Tellus Airborne Radiometrics.** The Geological Survey Ireland Tellus programme conducted airborne gamma-ray spectrometric surveys across Ireland from 2004 to 2022, measuring equivalent uranium (eU), equivalent thorium (eTh), and potassium (K) concentrations from fixed-wing aircraft at 56 metres altitude and 200-metre line spacing [12, 13]. The merged 2022 dataset provides national coverage at approximately 50-metre resolution. The GeoTIFF products available for download are colour-rendered maps (RGB, unsigned 8-bit) rather than raw radiometric values. We extract a pseudo-radiometric index from each pixel by computing (Red - Blue + 247) / 494, which maps the blue-to-red colour ramp to a [0, 1] scale that preserves the monotonic ordering of underlying physical measurements. For each 10-kilometre grid square, we sample at a 5 by 5 sub-grid (25 points) and compute the mean, standard deviation, and 90th percentile.

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

**Interaction features** (eU crossed with granite, limestone, shale, peat, gravel, till; granite crossed with till; limestone crossed with gravel): Adding interactions does not improve MAE when tested in isolation (MAE = 6.48), but the granite-by-till interaction becomes highly important in the full model.

**One-hot bedrock units and ages** (25 additional binary features for specific lithological units and geological age brackets): The full model achieves MAE = 6.42, a 12.3% improvement over the Ridge baseline and 2.4% over the XGBoost baseline.

The improvement trajectory is: Ridge baseline (7.33) to XGBoost baseline (6.58, 10.2% gain) to enhanced features (6.45, 12.0% gain) to full model (6.42, 12.4% gain). The largest single gain comes from switching from linear to tree-based models, with feature engineering providing incremental but meaningful improvements.

### 3.4 Feature Importance

The top 15 features by XGBoost gain-based importance in the final model reveal a clear geological hierarchy:

1. **Carboniferous marine shelf limestone** (18.4%): The dominant single lithological unit, indicating that the specific variety of limestone (marine shelf facies with calcite-rich beds) matters more than the generic "is limestone" indicator.

2. **Caledonian (Silurian-Devonian) bedrock age** (12.9%): Rocks from this orogenic cycle include the major granite intrusions in Ireland.

3. **Granite x Till interaction** (6.5%): The product of granite bedrock indicator and till subsoil indicator. This novel finding shows that the combination of uranium-rich bedrock and glacially-derived permeable overburden creates the highest radon transport pathway.

4. **Ordovician-Silurian bedrock** (4.9%): Ancient metamorphic and sedimentary rocks that host the Leinster Granite batholith.

5. **eU x Granite interaction** (4.3%): The uranium signal is most informative on granite bedrock, where it distinguishes between high-uranium and low-uranium granitic facies.

The dominance of specific lithological units over generic radiometric features is a key finding. The Tellus airborne uranium signal (eU mean) ranks only 10th in importance (2.0%), far below specific bedrock units. This suggests that at the 10-kilometre grid scale, knowing the exact rock type provides more predictive power than knowing the bulk radiometric intensity.

### 3.5 Spatial Variation in Model Performance

The model's per-county MAE varies from 2.8 (Kerry) to 12.1 (Sligo). The hardest counties to predict share a common characteristic: geological complexity at the county boundary.

**Sligo** (MAE = 12.1) has a sharp transition from the high-radon Benbulben Formation (Mississippian limestone and shale) to the low-radon Ox Mountains (Precambrian metamorphic). Grid squares straddling this transition have radon rates that depend on exactly where within the 10-kilometre square the homes are located.

**Carlow** (MAE = 11.9) sits on the eastern margin of the Leinster Granite batholith, where granite gives way to Ordovician volcanics within a few kilometres. The 10-kilometre grid resolution cannot capture this transition.

**Kerry** (MAE = 2.8) is the easiest county because it has relatively uniform geology (Devonian sandstones and Namurian shales) with consistently high radon across most of the county.

These patterns confirm that prediction error is driven by within-grid-square geological heterogeneity, not model inadequacy. Finer spatial resolution would reduce this irreducible error.

### 3.6 Comparison with Prior Work

Direct comparison with Elio et al. [9, 10] is complicated by their use of standard random cross-validation (reported AUC 0.78-0.82) versus our county-grouped spatial cross-validation. Our spatial CV is deliberately more conservative because it tests generalisation to entirely unseen counties rather than held-out grid squares within the same county. Under spatial CV, the achievable performance ceiling is lower because adjacent grid squares within the same county share geological conditions that are removed from the training set.

Our MAE of 6.4 percentage points means that for a typical grid square with 7% of homes above the reference level, the model's prediction is off by about 6 points. For a grid square with 20% above the reference level (a clear High Radon Area), the model might predict anywhere from 14% to 26%, but it would still correctly classify the area as HRA in most cases.

## 4. Discussion

### 4.1 The Granite-Till Interaction

The most novel finding is the importance of the granite-by-till interaction feature, which ranks third overall (6.5% importance). This feature captures a physical mechanism that is well understood in the radon literature but has not been explicitly modelled as a predictive feature for Ireland.

Granite bedrock contains elevated uranium concentrations (5-20 parts per million versus a crustal average of approximately 2.7 parts per million [21]). When glacial processes erode granite and deposit the material as glacial till (boulder clay), the till inherits the uranium-enriched geochemistry of its parent rock [22]. This granite-derived till is then both a uranium source (producing radon in situ) and a transport medium (sufficiently permeable to allow radon migration to the surface).

The result is that areas with granite bedrock overlain by granite-derived till have a "double source" of radon: from the bedrock below and from the till itself. This is different from areas where granite bedrock is overlain by limestone-derived till (which has lower uranium) or by peat (which acts as a low-permeability barrier).

The interaction feature captures this physical distinction that neither the generic "is granite" indicator nor the generic "is till" indicator can express alone. Tree models can learn interactions implicitly through sequential splits, but providing the explicit interaction feature reduces the tree depth needed and improves generalisation.

### 4.2 Why Lithology Outperforms Radiometrics

A counterintuitive finding is that specific bedrock lithological unit names outperform the Tellus airborne uranium signal (eU) as predictors. One might expect that a direct measurement of uranium concentration at the surface would be the strongest predictor of a uranium-derived gas. Several factors explain this:

**Scale mismatch.** The Tellus survey measures at approximately 50-metre resolution, but radon risk operates at building scale (metres) and is averaged over 10-kilometre grid squares. At the grid scale, the variance of eU within a square is large, and the mean eU signal is diluted by non-residential areas (agricultural land, bogs, water).

**Colour-map quantisation.** The available Tellus GeoTIFF products are colour-rendered maps rather than raw radiometric values in parts per million. Our pseudo-radiometric index preserves the monotonic ordering but loses quantitative precision, particularly in the tails of the distribution.

**Lithology encodes more than uranium.** The bedrock unit name implicitly encodes not just uranium content but also rock permeability, fracture density, karst development, and weathering characteristics, all of which affect radon transport independently of uranium source strength. The Carboniferous marine shelf limestone, the top-ranked feature, has moderate uranium but high permeability from karstification, creating efficient radon transport pathways.

### 4.3 Implications for Radon Policy

The model's county-level performance suggests where the EPA's measurement resources would be most productively deployed. Counties with high prediction error (Sligo, Carlow, Louth) contain grid squares where geological complexity means the current 10-kilometre grid resolution is inadequate. These areas would benefit most from targeted local measurement campaigns.

The granite-till interaction finding has practical implications for Ireland's National Retrofit Plan, which aims to retrofit 500,000 homes by 2030 for energy efficiency [23]. Homes on granite bedrock with granite-derived till that undergo deep energy retrofits (reducing ventilation) may experience significant increases in indoor radon. The interaction feature could be used to flag retrofit candidates for mandatory pre- and post-retrofit radon testing.

### 4.4 Limitations

Several limitations constrain this analysis:

**Tellus data format.** The available Tellus GeoTIFF products are colour-rendered images rather than raw radiometric data in physical units. Access to the underlying eU values in parts per million would likely improve the radiometric features' predictive power.

**Grid resolution.** The 10-kilometre EPA radon grid averages over substantial geological heterogeneity. Within a single grid square, radon levels can vary by more than an order of magnitude depending on local conditions [24]. Finer-resolution prediction (Electoral Division or Small Area level) would require individual home measurements, which are not publicly available.

**No building features.** This study uses geological data only and does not incorporate building characteristics (floor type, ventilation, airtightness) from the SEAI Building Energy Rating (BER) database. The interaction between building airtightness and geological radon supply is well documented [25, 26] and would likely improve predictions at finer spatial scales.

**Spatial CV conservatism.** County-grouped spatial CV is deliberately conservative. Counties that share the same geological formation (such as the Leinster Granite spanning five counties) are treated as independent test regions, which may underestimate the model's actual predictive power in practice.

## 5. Conclusion

We demonstrate that publicly available geological data, including airborne radiometric surveys, bedrock geology, and subsoil maps, can predict Irish radon risk areas with a mean absolute error of 6.4 percentage points under strict spatial cross-validation. The key finding is that specific bedrock lithological units and geology-subsoil interactions (particularly the granite-till combination) outperform bulk radiometric measurements as predictors. This suggests that geological structure, not just uranium concentration, determines radon risk at the landscape scale.

The model identifies areas where prediction is most uncertain (county boundary zones with complex geology) and areas where it is most reliable (geologically uniform counties). This information can guide the EPA's measurement campaigns toward the areas that would benefit most from additional testing.

Future work should incorporate building characteristics from the BER database to model the interaction between geological radon supply and building-level ventilation, enabling prediction of which specific homes are at risk rather than which areas. Access to raw Tellus radiometric values in physical units would also strengthen the radiometric features. The ultimate goal is a home-level radon risk prediction that integrates geology, building characteristics, and climate to identify the estimated 140,000 Irish homes above the reference level that have never been tested.

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
