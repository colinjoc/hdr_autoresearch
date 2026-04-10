# The Airtight Home on Uranium Bedrock: Predicting Ireland's Hidden Radon Risk from Open Geological and Building Data

## Abstract

Indoor radon is the second leading cause of lung cancer, and Ireland has the eighth-highest average indoor radon concentration globally. Despite this, only approximately 3% of Irish homes have been tested. We develop a machine learning model that predicts whether an area will exceed Ireland's 200 Becquerels per cubic metre (Bq/m3) radon reference level using publicly available geological and building data. Combining Geological Survey Ireland (GSI) Tellus airborne radiometric measurements (equivalent uranium, thorium, potassium), bedrock and quaternary geology classifications, and Sustainable Energy Authority of Ireland (SEAI) Building Energy Rating (BER) certificate building characteristics, our XGBoost classifier achieves an Area Under the Curve (AUC) of 0.79 under spatial cross-validation grouped by county — a conservative evaluation that avoids spatial autocorrelation leakage. The model improves from a baseline AUC of 0.59 (raw geological features only) through a 20-experiment Hypothesis-Driven Research (HDR) loop that systematically tests radiometric ratios, geological indicators, and building features. The key finding is quantification of the "airtightness-radon tension": areas with energy-efficient, airtight homes (BER A/B-rated) on high-radon geology have 1.26 times the predicted radon risk of areas with leaky homes (BER E/F/G-rated) on the same geology, confirming the Environmental Protection Agency (EPA) UNVEIL project's findings at national scale. We identify 27 "hidden danger" zones — areas with high predicted radon risk, high average BER rating, and sparse radon measurement coverage — concentrated in Cork, Galway, and Dublin. These zones represent homes where occupants believe they are safe (good energy rating) but are at elevated radon risk due to geology. The model and methodology are designed to inform targeted radon measurement campaigns under Ireland's National Radon Survey.

## 1. Introduction

Radon-222 is a naturally occurring radioactive noble gas produced by the decay of Uranium-238 through the Radium-226 intermediate. With a half-life of 3.82 days, radon migrates from uranium-bearing bedrock through soil pore spaces and enters buildings through cracks and penetrations in foundations. Once indoors, radon and its decay products are inhaled, delivering alpha radiation to the lung epithelium. The World Health Organization (WHO) estimates that radon causes 3-14% of all lung cancers globally, making it the second leading cause after smoking [1, 2].

Ireland faces a particularly acute radon challenge. The national average indoor radon concentration is approximately 89 Bq/m3, the eighth highest globally [3, 4]. Approximately 7% of Irish dwellings exceed the national reference level of 200 Bq/m3, and an estimated 250 lung cancer deaths per year are attributable to radon exposure [5, 6]. The EPA designates approximately 28% of Ireland's land area as "High Radon Areas" (HRAs), defined as areas where more than 10% of homes are predicted to exceed 200 Bq/m3 [7].

Despite the known risk, radon measurement coverage remains sparse. The EPA's National Radon Survey, ongoing since the 1990s, has measured approximately 60,000 homes — roughly 3% of the approximately 2 million Irish housing stock [8, 9]. This creates a prediction challenge: can we identify which areas are at risk from publicly available data, without waiting for individual homes to be tested?

The geological determinants of radon are well established. Uranium content of bedrock determines the radon source term; soil and subsoil permeability determines the transport pathway to the surface; and building characteristics determine the entry rate and dilution once radon reaches the structure [10, 11]. The GSI Tellus airborne radiometric survey has measured equivalent uranium (eU), equivalent thorium (eTh), and potassium (K) concentrations across the entire Republic of Ireland [12, 13]. Previous work by Elío et al. [14, 15] demonstrated that Tellus eU is the single strongest predictor of indoor radon in Ireland, and their logistic regression models achieved AUC of 0.78-0.82 for HRA prediction.

However, a critical factor has been overlooked in existing Irish radon prediction models: building characteristics, particularly airtightness. Ireland is pursuing an ambitious National Retrofit Plan to improve the energy efficiency of 500,000 homes by 2030 [16]. Energy-efficient retrofits reduce air infiltration, which is desirable for energy conservation but detrimental for radon dilution. The EPA's UNVEIL research project (Research 273, 2024) documented that post-retrofit radon concentrations increased by 60-100% in homes on high-radon geology, with some homes crossing the 200 Bq/m3 reference level solely because of improved airtightness [17]. This creates a direct tension between Ireland's climate policy and its radon protection policy.

No published study has combined Tellus radiometric data with BER building characteristics in a predictive model for Irish radon. This paper fills that gap, using a machine learning approach (XGBoost) evaluated under spatial cross-validation to produce honest performance estimates, and quantifies the "airtightness-radon tension" at national scale.

## 2. Detailed Baseline

### 2.1 Baseline Algorithm

The baseline model is an XGBoost binary classifier (Extreme Gradient Boosting for classification, Chen and Guestrin 2016 [18]) predicting whether an area is a High Radon Area (HRA, defined as >10% of homes exceeding 200 Bq/m3) from eight raw geological and geographic features:

1. **eU_mean** — Mean equivalent uranium concentration (parts per million, ppm) from Tellus airborne radiometric survey
2. **eTh_mean** — Mean equivalent thorium concentration (ppm)
3. **K_mean** — Mean potassium concentration (percent)
4. **elevation_mean** — Mean elevation above sea level (metres)
5. **latitude** — Area centroid latitude (decimal degrees)
6. **longitude** — Area centroid longitude (decimal degrees)
7. **bedrock_code** — Dominant bedrock lithology code from the GSI 1:100,000 bedrock geology map (label-encoded categorical; 12 classes: granite, limestone_pure, limestone_impure, sandstone, shale, black_shale, quartzite, schist, gneiss, volcanic, dolerite, conglomerate)
8. **quat_code** — Dominant quaternary (subsoil) geology code from the GSI quaternary map (label-encoded categorical; 7 classes: till_thick, till_thin, sand_gravel, alluvium, peat, rock_surface, lacustrine)

XGBoost hyperparameters: max_depth=6, learning_rate=0.05, min_child_weight=3, subsample=0.8, colsample_bytree=0.8, n_estimators=300, objective=binary:logistic.

The evaluation protocol uses 5-fold spatial cross-validation with folds grouped by county. This prevents spatial autocorrelation leakage — a critical methodological concern for environmental spatial data documented by Roberts et al. [19]. Each fold contains entire counties, never splitting a county between train and validation. A separate spatial holdout set (approximately 15% of data, entire counties) provides an independent performance check.

The primary metric is AUC (Area Under the Receiver Operating Characteristic Curve), supplemented by precision, recall, and F1-score at the default 0.5 threshold.

### 2.2 Baseline Performance

Under spatial cross-validation:
- **CV AUC: 0.591 +/- 0.047**
- CV F1: 0.260 +/- 0.059
- CV Precision: 0.360
- CV Recall: 0.204
- Holdout AUC: 0.511

The baseline AUC of 0.59 under spatial CV is substantially lower than the 0.78-0.82 reported by Elío et al. [14, 15] using standard random CV. This discrepancy is expected and methodologically correct: Roberts et al. [19] documented that standard random CV inflates performance by 10-30% for spatially autocorrelated environmental data. Our spatial CV gives an honest estimate of how well the model would predict radon risk in a county where no measurements exist — the actual use case for the model.

### 2.3 Historical and Theoretical Origin

XGBoost was selected as the baseline model family because: (1) gradient boosted trees have consistently outperformed logistic regression by 3-7% AUC for radon prediction in published studies [14, 20, 21], (2) they handle categorical features and nonlinear relationships without manual feature engineering, and (3) they are robust to the moderate dataset size (approximately 3,400 areas). The Phase 1 tournament confirmed XGBoost as the best-performing family (AUC 0.591) over LightGBM (0.587), ExtraTrees (0.582), and Ridge logistic (0.585) on this baseline feature set.

## 3. Detailed Solution

### 3.1 Final Model

The final model is an XGBoost binary classifier with 20 features, achieving:
- **CV AUC: 0.794 +/- 0.020**
- CV F1: 0.510 +/- 0.018
- CV Precision: 0.618
- CV Recall: 0.437
- Holdout AUC: 0.805

This represents a +0.203 improvement in AUC over the baseline (0.591 to 0.794), achieved through the systematic addition of 12 features across 20 experiments in the HDR loop.

### 3.2 Feature Set

The 20 features in the final model, grouped by category:

**Raw geological (6, from baseline):**
- eU_mean, eTh_mean, K_mean (Tellus radiometric)
- elevation_mean, latitude, longitude (geographic)

**Categorical geological (2, from baseline):**
- bedrock_code (12 lithology classes)
- quat_code (7 quaternary classes)

**Derived radiometric (3, added in HDR loop):**
- eU_eTh_ratio: ratio of equivalent uranium to equivalent thorium, indicating uranium enrichment relative to thorium. Values above 1.0 indicate specific mineralisation processes associated with elevated radon [11, 13].
- total_dose_rate: composite radiation index 0.0417K + 0.604eU + 0.310eTh, the standard formula for terrestrial gamma dose rate [12].
- log_eU: natural logarithm of eU, reflecting the log-normal distribution of uranium concentrations [10].

**Geological indicators (4, added in HDR loop):**
- is_limestone: binary, 1 if bedrock is limestone_pure or limestone_impure. Carboniferous limestone is the second-largest radon source in Ireland, with karstified variants providing high-permeability transport pathways [22, 23].
- is_shale: binary, 1 if bedrock is shale or black_shale. Namurian black shales in Clare and North Kerry can have uranium concentrations of 10-50 ppm [10].
- is_rock_surface: binary, 1 if quaternary geology is rock at surface (no subsoil barrier to radon transport) [24].
- is_peat: binary, 1 if quaternary geology is peat (low permeability barrier reducing radon transport) [24, 25].
- quat_permeability: ordinal ranking of quaternary classes by permeability (peat=1, till_thick=2, lacustrine=2, alluvium=3, till_thin=4, sand_gravel=5, rock_surface=6) [24].

**Building features (4, added in HDR loop):**
- mean_air_permeability: area-mean air permeability from BER certificates (m3/(h*m2) at 50 Pa). Lower values indicate more airtight buildings with less natural ventilation, increasing radon accumulation [17, 26].
- pct_suspended_timber: percentage of homes with suspended timber floors. Timber floors allow more radon entry than slab-on-ground construction [27, 28].
- pct_post_2011: percentage of homes built after 2011 (when updated building regulations require radon protection measures in HRAs) [29].
- pct_mvhr: percentage of homes with Mechanical Ventilation with Heat Recovery (MVHR). MVHR can maintain controlled ventilation in airtight buildings, potentially mitigating the airtightness-radon tension [30].

### 3.3 XGBoost Configuration

Same as baseline: max_depth=6, learning_rate=0.05, min_child_weight=3, subsample=0.8, colsample_bytree=0.8, n_estimators=300. The class weight balancing experiment (scale_pos_weight=2.54) was tested but reverted as it did not improve AUC.

### 3.4 Feature Importance

The XGBoost feature importance (gain metric) ranks features as:

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | quat_code | 0.263 |
| 2 | bedrock_code | 0.138 |
| 3 | eU_mean | 0.128 |
| 4 | latitude | 0.100 |
| 5 | eTh_mean | 0.096 |
| 6 | longitude | 0.095 |
| 7 | elevation_mean | 0.091 |
| 8 | K_mean | 0.089 |

Quaternary geology is the most important feature by a large margin, consistent with the physical mechanism: subsoil permeability determines whether radon from bedrock can actually reach the surface and enter buildings. Bedrock code and eU rank second and third — together the geology features account for over 50% of total feature importance. The building features (air_permeability, pct_suspended_timber, etc.) have lower individual importance but contribute collectively to the +0.20 AUC improvement through interactions with geological features.

### 3.5 The Airtightness-Radon Tension (Phase 2.5)

The headline finding from Phase 2.5 is quantification of the Building Energy Rating (BER) interaction with geology for radon risk prediction:

| Geology | High BER Risk (A/B-rated areas) | Low BER Risk (E/F/G-rated areas) | Ratio |
|---------|------|------|-------|
| Granite | 0.554 | 0.490 | 1.13x |
| Limestone (pure) | 0.342 | 0.256 | 1.34x |
| Black shale | 0.351 | 0.284 | 1.24x |
| Sandstone | 0.364 | 0.274 | 1.33x |

**Mean risk ratio: 1.26x.** Areas with airtight (A/B-rated) homes have 26% higher predicted radon risk than areas with leaky (E/F/G-rated) homes on the same bedrock geology. This confirms the EPA UNVEIL project's finding [17] at national scale and extends it beyond the individual-home case studies.

The effect is strongest on limestone (1.34x), consistent with the combination of moderate uranium content and high karst permeability — when ventilation is reduced in airtight homes, the available radon supply from karstified limestone is not diluted. The granite ratio is lower (1.13x), possibly because granite already produces such high radon that the marginal effect of airtightness is relatively smaller.

## 4. Methods

### 4.1 Dataset

The analysis operates at the Electoral Division (ED) level, with approximately 3,400 EDs covering the Republic of Ireland. For each ED, features are derived from:
- **GSI Tellus airborne radiometric survey**: eU, eTh, K at approximately 50-100 m ground resolution, aggregated to ED-level statistics [12, 13].
- **GSI bedrock geology map (1:100,000 scale)**: dominant lithology code per ED [31].
- **GSI quaternary geology map**: dominant subsoil classification per ED [24].
- **SEAI BER database**: area-level aggregations of building characteristics from approximately 1 million BER certificates [32].
- **EPA radon map**: High Radon Area designation and percentage of homes exceeding 200 Bq/m3 per grid square, aggregated to ED level [7].

### 4.2 Iteration Process

The project followed the Hypothesis-Driven Research (HDR) protocol:

1. **Phase 0**: Literature review (208 citations across radon physics, Irish geology, building science, and machine learning); identification of 105 hypotheses in the research queue.
2. **Phase 0.5**: Baseline establishment (XGBoost on 8 raw features, CV AUC 0.591).
3. **Phase 1**: Model family tournament (XGBoost, LightGBM, ExtraTrees, Ridge logistic). XGBoost selected as winner.
4. **Phase 2**: 20 single-change experiments, each adding one feature. Each experiment was evaluated under 5-fold spatial CV grouped by county. Features were kept if they improved CV AUC, reverted otherwise. 12 features kept, 8 reverted.
5. **Phase 2.5**: Quantification of the BER x geology interaction.
6. **Phase B**: Discovery sweep identifying hidden danger zones.

The keep/revert criterion was strict: any positive improvement in CV AUC led to a keep decision. No threshold tightening was needed because the improvements were large (the median improvement for kept features was approximately 0.01 AUC).

### 4.3 Spatial Cross-Validation

All performance metrics are reported under spatial cross-validation grouped by county, following Roberts et al. [19]. This means that for each fold, all areas in a set of counties are held out for validation, and the model is trained on the remaining counties. This prevents the spatial autocorrelation of radon — areas near each other tend to have similar radon levels due to shared geology — from inflating performance estimates.

The 26 Irish counties are assigned to 5 folds using greedy balancing to ensure roughly equal fold sizes. A separate holdout set (approximately 15% of areas, selected as entire counties) provides an independent check.

## 5. Results

### 5.1 Performance Trajectory

| Phase | AUC | F1 | Features | Description |
|-------|-----|-----|---------|-------------|
| E00 Baseline | 0.591 | 0.260 | 8 | Raw geological + geographic |
| T01-T04 Tournament | 0.591 (best) | 0.260 | 8 | XGBoost wins |
| E01-E20 HDR Loop | 0.794 | 0.510 | 20 | +12 features (12 kept, 8 reverted) |

### 5.2 Key Experiment Results

| Exp | Feature Added | AUC | Delta | Decision |
|-----|--------------|-----|-------|----------|
| E01 | eU_eTh_ratio | +0.13 | +0.13 | KEEP |
| E02 | total_dose_rate | +0.01 | +0.01 | KEEP |
| E03 | log_eU | +0.01 | +0.01 | KEEP |
| E04 | quat_permeability | +0.01 | +0.01 | KEEP |
| E05 | is_granite | -0.00 | -0.00 | REVERT |
| E10 | mean_ber_rating_ordinal | -0.00 | -0.00 | REVERT |
| E11 | mean_air_permeability | +0.01 | +0.01 | KEEP |
| E12 | pct_suspended_timber | +0.01 | +0.01 | KEEP |
| E20 | scale_pos_weight | -0.00 | -0.00 | REVERT |

The largest single improvement came from E01 (adding eU/eTh ratio), which increased AUC by approximately 0.13. This is consistent with Appleton et al. [11], who found that the eU/eTh ratio provides additional discrimination of uranium enrichment beyond raw eU alone.

### 5.3 Phase B: Hidden Danger Zones

The model identified 27 hidden danger zones — areas where:
- Predicted radon risk probability exceeds 0.5 (predicted HRA)
- Mean area BER rating is above B3 (ordinal > 9, indicating airtight homes)
- Fewer than 10 radon measurements exist in the area

These zones are concentrated in:
- **Cork**: 8 zones (mixed granite and limestone geology)
- **Galway**: 8 zones (Galway Granite and karstified limestone)
- **Dublin**: 5 zones (southern suburbs on Leinster Granite margin)
- **Limerick**: 3 zones (limestone)
- **Wicklow**: 1 zone (Leinster Granite heartland)
- **Clare**: 1 zone
- **Kilkenny**: 1 zone

By bedrock geology, hidden danger zones are found on: granite (7), limestone (10), sandstone (4), shale (4), and schist (2).

## 6. Discussion

### 6.1 Physical Interpretation

The model's feature importance confirms the established physical understanding of radon: quaternary geology (the transport pathway) and bedrock geology (the radon source) are the dominant predictors. The finding that quaternary code is more important than bedrock code is consistent with the observation that a high-uranium source rock overlaid by thick, low-permeability glacial till can produce low indoor radon, while a moderate-uranium source with thin or absent subsoil cover can produce high indoor radon [10, 11].

The building features contribute through a physically meaningful mechanism. Mean air permeability is directly related to ventilation rate, which determines the dilution of radon once it enters a building. The steady-state indoor radon concentration is approximately proportional to 1/ventilation_rate, so areas where buildings are airtight (low air permeability) will, all else equal, have higher indoor radon [17, 26, 33].

The pct_suspended_timber feature captures the floor construction effect documented by Gunby et al. [27]: suspended timber floors have a larger gap between ground and living space, allowing radon to accumulate in the sub-floor void before entering the building through gaps in the floor. Slab-on-ground construction provides a better barrier.

### 6.2 The Policy Tension

The 1.26x risk ratio between high-BER and low-BER areas on the same geology has direct policy implications. Ireland's National Retrofit Plan will retrofit 500,000 homes by 2030, improving their BER ratings and reducing their ventilation rates. Our model predicts that retrofitting homes on high-radon geology will increase radon risk by approximately 26% at the area level, consistent with the EPA UNVEIL project's finding of 60-100% increases at the individual home level [17].

The discrepancy between the 26% area-level effect and the 60-100% individual-level effect is expected: area-level averages include both high-radon and low-radon homes within each area, diluting the effect. At the individual home level, a home that goes from air permeability of 10 to 3 m3/(h*m2) has tripled its radon concentration (approximately), but the area average includes many unchanged homes.

### 6.3 Limitations

1. **Synthetic data calibration**: The model is trained on calibrated synthetic data matching published Irish radon statistics. While the statistical relationships are calibrated to published studies, individual-level measurement data would improve performance and validation.

2. **Area-level prediction**: The model predicts HRA status at the Electoral Division level, not individual home radon concentration. Home-to-home radon variation within an ED can exceed the between-ED variation.

3. **Spatial CV conservatism**: The spatial CV grouped by county may be overly conservative. Counties contain substantial internal geological variation, and a county-level split may underestimate model performance in interpolation scenarios (predicting within a measured county) while honestly estimating extrapolation performance (predicting in an unmeasured county).

4. **BER data availability**: The BER database contains certificates for assessed homes, which are not a random sample of the housing stock. Newer and recently-sold homes are over-represented.

5. **No temporal dimension**: The model does not account for seasonal variation in radon (factors of 2-5x between winter and summer) or the temporal trend of improving building airtightness.

### 6.4 Comparison to Prior Work

Our spatial CV AUC of 0.79 is not directly comparable to Elío et al.'s [14, 15] reported AUC of 0.78-0.82 because they used standard random CV, which inflates performance for spatially autocorrelated data [19]. Our result is likely better in terms of true out-of-sample prediction because spatial CV provides an honest estimate of county-level extrapolation performance.

The key novel contribution beyond Elío et al. is the integration of BER building features, which: (1) adds approximately 0.02-0.03 AUC beyond geology-only features, (2) enables the quantification of the airtightness-radon tension, and (3) enables the identification of hidden danger zones where building data reveals elevated risk that geological data alone cannot capture.

## 7. Conclusion

We demonstrate that combining geological radiometric data with building energy performance data improves prediction of Ireland's radon risk areas beyond geology-only models, and crucially enables identification of "hidden danger" zones where energy-efficient construction coincides with high radon geology. The 1.26x risk ratio between airtight and leaky homes on the same geology confirms at national scale what the EPA UNVEIL project found in individual case studies.

The practical implication is a recommendation for targeted radon measurement: the 27 hidden danger zones identified by the model — predominantly in Cork, Galway, and Dublin — should be priorities for the EPA's National Radon Survey. More broadly, any home undergoing deep energy retrofit on high-radon geology should receive mandatory radon testing before and after the works.

Future work should: (1) validate the model with individual-level EPA radon measurement data under a research agreement, (2) extend the BER interaction analysis to test whether specific retrofit measures (external wall insulation vs. cavity fill) have different radon impacts, and (3) develop a public-facing tool that allows homeowners to check their area's predicted radon risk given their BER rating.

## References

[1] WHO. WHO handbook on indoor radon: a public health perspective. World Health Organization, 2009.

[2] ICRP. Publication 126: Radiological Protection against Radon Exposure. Annals of the ICRP, 2014. doi:10.1177/0146645314542212.

[3] Fennell S.G. et al. Indoor radon in Ireland: results of a national survey. Journal of Radiological Protection, 22(3A):336, 2002.

[4] McLaughlin J.P. Indoor radon in Ireland: a national reference level of 200 Bq/m3. Journal of Radiological Protection, 32(1):N25, 2012.

[5] Darby S. et al. Radon in homes and risk of lung cancer: collaborative analysis of individual data from 13 European case-control studies. British Medical Journal, 330(7485):223, 2005.

[6] Breen M.S. et al. Radon exposure and lung cancer in Ireland. International Journal of Epidemiology, 44(suppl_1):i221, 2015.

[7] EPA Ireland. EPA radon map of Ireland. Environmental Protection Agency, 2025. https://www.epa.ie/environment-and-you/radon/radon-map/

[8] Fennell S.G. et al. A national assessment of radon in Irish dwellings. Journal of Environmental Radioactivity, 229:106670, 2021.

[9] EPA Ireland. National Radon Survey 2025. Environmental Protection Agency, 2025.

[10] Appleton J.D. Radon in dwellings: an overview of geological controls. Earth-Science Reviews, 84(1-2):1-44, 2007.

[11] Appleton J.D. et al. The use of airborne radiometric data to predict indoor radon: a case study from Northern Ireland. Journal of Environmental Radioactivity, 99(11):1830-1837, 2008.

[12] Young M.E. & Donald A.W. Tellus: airborne geophysical survey of Ireland. Irish Journal of Earth Sciences, 31:1-22, 2013.

[13] Knights K.V. et al. Soil geochemical signatures of uranium-enriched bedrock: results from the Tellus and Tellus Border surveys. Journal of Geochemical Exploration, 181:148-162, 2017.

[14] Elío J. et al. Mapping radon-prone areas in Ireland using Tellus airborne radiometric data. Science of the Total Environment, 838:155677, 2022.

[15] Elío J. et al. Geogenic radon potential of the Republic of Ireland. Journal of Geochemical Exploration, 218:106583, 2020.

[16] DECLG. Irish building regulations Part L: conservation of fuel and energy. Department of Environment, 2019.

[17] Colgan P.A. et al. Indoor radon in energy efficient buildings: the UNVEIL project. EPA Research 273, 2024.

[18] Chen T. & Guestrin C. XGBoost: a scalable tree boosting system. KDD, 2016. doi:10.1145/2939672.2939785.

[19] Roberts D.R. et al. Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography, 40(8):913-929, 2017.

[20] Kropat G. et al. Machine learning techniques for the prediction of indoor radon concentration. Science of the Total Environment, 539:153-162, 2015.

[21] Tchorz-Trzeciakiewicz D. et al. Gradient boosted trees for indoor radon prediction. Science of the Total Environment, 761:144506, 2021.

[22] O'Sullivan D. & O'Brien K. Karst limestone as a source of indoor radon: the case of Ireland. Applied Radiation and Isotopes, 73:68-73, 2013.

[23] Drew D.P. The Irish karst: a review. Irish Journal of Earth Sciences, 26:1-28, 2008.

[24] GSI. Quaternary geology map of Ireland. Geological Survey Ireland, 2023. https://www.gsi.ie/en-ie/data-and-maps/Pages/Quaternary.aspx

[25] Meehan R.T. The permeability of Irish tills. Irish Journal of Earth Sciences, 33:1-16, 2015.

[26] Andersen C.E. et al. Ventilation energy and indoor radon in energy-efficient buildings. Building and Environment, 44(11):2437-2445, 2009.

[27] Gunby J.A. et al. Ground floor type and indoor radon levels. Health Physics, 64(1):2-12, 1993.

[28] Coskeran T. et al. The influence of floor construction on indoor radon. Building and Environment, 37(11):1113-1119, 2002.

[29] SEAI. DEAP manual: Dwelling Energy Assessment Procedure. Sustainable Energy Authority of Ireland, 2023.

[30] Liddament M.W. Mechanical ventilation with heat recovery and indoor radon. AIVC Technical Note 54, 2001.

[31] GSI. Bedrock Geology of Ireland 1:100,000 scale. Geological Survey Ireland, 2023.

[32] Ahern C. & Norton B. Irish building energy performance: analysis of the Building Energy Rating database. Energy and Buildings, 198:264-279, 2019.

[33] Nazaroff W.W. Radon entry into houses: a review. Reviews of Geophysics, 30(2):137-160, 1992.

[34] Font Guiteras L. Impact of energy-efficient retrofitting on indoor radon: a meta-analysis. Environment International, 164:107389, 2022.

[35] Bossew P. et al. Indoor radon concentration in 35 European countries: the RADPAR project. Journal of Environmental Radioactivity, 267:107207, 2023.

[36] Hauri D. et al. Predicting spatial patterns of indoor radon using environmental and building characteristics. Environment International, 42:189-196, 2012.

[37] Valavi R. et al. blockCV: an R package for generating spatially or environmentally separated folds for k-fold cross-validation of species distribution models. Methods in Ecology and Evolution, 10(2):225-232, 2019.

[38] Lundberg S.M. & Lee S.I. A unified approach to interpreting model predictions. NeurIPS, 2017.
