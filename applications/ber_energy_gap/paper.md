# Predicting Ireland's DEAP-Calculated BER Scores: What Building Characteristics Drive the Rating and Where the Formula Is Most Sensitive

## Abstract

Ireland's Building Energy Rating (BER) system assigns every dwelling a calculated energy performance score using the Dwelling Energy Assessment Procedure (DEAP). The BER score is a deterministic output of a physics-based formula; it does not reflect actual metered consumption. We analysed 1.33 million real BER certificates from the Sustainable Energy Authority of Ireland (SEAI) to determine which building characteristics the DEAP formula weighs most heavily and how sensitive the formula is to individual feature perturbations. A LightGBM gradient boosting model with domain-knowledge features achieved a Mean Absolute Error (MAE) of 18.05 kWh/m2/yr on 5-fold cross-validation, improving 44% over a Ridge linear baseline (MAE 32.28). However, simply summing the DEAP primary energy components already present in the dataset achieves MAE 6.96 — the ML model is a lossy approximation to a known formula, not a discovery. Its value lies in SHAP-based attribution: the Heat Loss Parameter (HLP) dominates predictions at more than double the impact of any other feature, and per-dwelling counterfactual perturbations suggest that chimney sealing (mean saving 21.1 kWh/m2/yr for applicable dwellings, SD 10.5) is a high-impact measure warranting field validation. A temporal holdout (train pre-2020, test 2020+) shows substantial degradation (MAE 27.50), indicating the model does not generalise well across regulatory regime changes. All results describe DEAP-predicted energy, not real consumption — the well-documented performance gap means actual savings are 20-40% smaller.

## 1. Introduction

Ireland committed under the Climate Action Plan to retrofit 500,000 homes to BER B2 or better by 2030. The Building Energy Rating system, mandatory for all residential sales and rentals since 2009, provides the yardstick: each dwelling receives a letter grade from A1 (best, under 25 kWh/m2/yr) to G (worst, over 450 kWh/m2/yr) based on the DEAP calculation methodology, which implements the European standard ISO 13790 for quasi-steady-state building energy modelling.

The BER score is computed by DEAP, a quasi-steady-state energy balance model implementing ISO 13790. It is important to understand what this means: the BER rating is a deterministic function of building characteristics, heating system parameters, and standardised occupancy assumptions. It is not a measurement. The "performance gap" — the divergence between DEAP-calculated and actual metered consumption — is well-documented: Sunikka-Blank and Galvin (2012) identified the "prebound effect" (occupants of inefficient homes under-heat), Galvin (2014) documented the "rebound effect" (occupants of efficient homes increase comfort), and Moran et al. (2020) confirmed for Ireland that the actual consumption gap between best and worst homes is roughly 2:1, not the 8.5:1 that DEAP predicts. Majcen et al. (2013) found similar patterns in the Netherlands, and Galvin and Sunikka-Blank (2016) documented them for Germany.

This paper does not study the performance gap, which requires matched BER-and-meter data unavailable in the public SEAI dataset. Instead, we treat the DEAP formula as a black box and ask three questions:

1. **What building characteristics does the DEAP formula weigh most heavily?** This is a sensitivity analysis of a known model, not a discovery about building physics.

2. **Can machine learning approximate the BER score from building characteristics alone?** If so, this enables rapid screening without running the full DEAP calculation — useful for policy targeting at scale.

3. **How sensitive is the DEAP score to individual feature perturbations?** This is distinct from asking "what happens after a real retrofit" because model perturbation is not causal estimation (Fowlie et al. 2018; Allcott and Greenstone 2012).

We address these questions using the full SEAI BER public search dataset — 1.33 million real certificates covering approximately two-thirds of Ireland's dwelling stock — with gradient boosting models and SHAP-based feature attribution.

## 2. Data

### 2.1 Source and Scope

The Sustainable Energy Authority of Ireland (SEAI) publishes the National BER Research Tool, a tab-delimited file containing every domestic BER certificate issued. We downloaded the full dataset on 10 April 2026, obtaining 1,366,752 records with 211 columns per certificate. After removing records with missing or out-of-range target values (BER rating outside 0-1000 kWh/m2/yr) and trimming the 1st and 99th percentiles to exclude extreme outliers, 1,330,022 records remained for modelling. The data is released under a Creative Commons Attribution 4.0 licence.

Each record contains the complete DEAP input parameters: building envelope U-values (walls, roof, floor, windows, doors), envelope areas, heating system type and efficiency, ventilation method, lighting efficiency, thermal bridging factors, draught indicators, and the resulting energy breakdown by end-use (space heating, water heating, lighting, pumps and fans). The target variable is the BER rating in kWh/m2/yr of primary energy.

### 2.2 Key Characteristics of the Irish Housing Stock

The dataset reveals several distinctive features of Ireland's residential buildings:

**Construction era distribution.** The mean BER by construction era ranges from 339 kWh/m2/yr (pre-1930, 114,506 certificates) through 271 (1930-1977), 199 (1978-2005), 146 (2006-2011), 54 (2012-2020) to 40 (2021+ near-zero energy buildings, 107,079 certificates). The step-function improvements align precisely with building regulation milestones: the 1978 Building Regulations first required insulation, the 2006 amendments raised standards substantially, and the 2012/2019 nearly-zero energy building (nZEB) regulations imposed modern performance targets.

**Geographic variation.** Mean BER ranges from 239 kWh/m2/yr in Leitrim to 160 in Kildare. Western and north-western counties (Leitrim, Roscommon, Mayo, Donegal) have worse average ratings, reflecting older rural housing stock rather than climate differences — the north-south degree-day variation across Ireland is only about 15%.

**Fuel mix.** Gas, oil, and electricity each serve roughly one-third of the stock. Heat pumps (identifiable by heating system efficiency exceeding 100%, indicating a coefficient of performance greater than 1) are present in only about 10% of 2012-2020 certificates but over 80% of 2021+ certificates, reflecting the nZEB regulation's effective requirement for renewable heating.

**Dwelling type.** Mid-floor apartments have the lowest mean BER (147 kWh/m2/yr) because they share walls, floor, and ceiling with adjacent units. Detached houses have the highest (209 kWh/m2/yr) because their entire envelope is exposed.

### 2.3 Fundamental Data Limitation

The BER dataset gives DEAP-calculated energy, not measured consumption. This is an asset rating: it describes the building's intrinsic performance under standardised occupancy assumptions (2.5 occupants, 21 degrees Celsius living room, 18 degrees Celsius elsewhere, standard hot water demand). Actual energy consumption depends on occupant behaviour, which varies hugely and creates the performance gap. All results in this paper describe DEAP-predicted energy performance, not real-world consumption.

## 3. Methods

### 3.1 Feature Engineering

We extracted 22 numeric features and 5 categorical features from the raw certificate data. The numeric features include the five envelope U-values (walls, roof, floor, windows, doors), six envelope areas, construction year, number of storeys, heating system efficiency, mechanical ventilation indicator, thermal bridging factor, low-energy lighting percentage, chimney and flue counts, draught indicators, and permeability test results.

Three derived features capture building physics more directly than raw variables:

- **Envelope average U-value**: area-weighted mean of all envelope element U-values, representing overall fabric thermal quality.
- **Heat Loss Parameter (HLP) proxy**: total area-weighted U-value sum divided by floor area, in W/m2K. This is the standard metric used in building physics to summarise a dwelling's fabric heat loss per unit floor area.
- **Window-to-wall ratio**: glazing area divided by opaque wall area, capturing the trade-off between daylight, solar gains, and thermal loss.

Categorical features (dwelling type, county, fuel group, structure type, age category) were one-hot encoded, producing 77 total features for the baseline model.

During the Hypothesis-Driven Research (HDR) loop, we tested nine additional engineered features individually. Four were retained based on improving cross-validation MAE by more than 0.01 kWh/m2/yr:

- **Compactness ratio** (total envelope area divided by floor area): captures the form factor that distinguishes apartments from detached houses.
- **Ventilation heat loss proxy** (chimney count plus 1.5 times open flue count plus 0.1 times permeability result): combines multiple infiltration indicators into a single feature.
- **Primary energy factor** (fuel-specific multiplier: gas and oil 1.1, electricity 2.08, solid fuel and wood 1.0): makes the DEAP primary energy conversion explicit.
- **Space heating fraction** (delivered space heating energy divided by total delivered energy): captures the relative importance of fabric versus hot water and lighting.

Space heating fraction was by far the most impactful individual feature, reducing LightGBM MAE from 19.54 to 18.47 kWh/m2/yr (a 5.5% improvement). This is physically intuitive: buildings where space heating dominates total energy use are those with the worst fabric, and knowing this fraction provides a strong signal about fabric quality that complements the HLP proxy.

Five features were tested and reverted because they did not improve MAE: wall insulation era interaction, heating-fabric interaction, roof-to-floor ratio, log-transformed floor area, and total wall heat loss.

### 3.2 Model Tournament and DEAP Baseline

Before evaluating ML models, we established a DEAP-reconstruction baseline. The dataset contains DEAP intermediate outputs: primary energy for space heating, water heating, lighting, pumps and fans, secondary space heating, and supplementary water heating. Simply summing these and dividing by floor area recovers the BER rating with MAE 6.96 kWh/m2/yr (RMSE 29.07, R2 0.942) on the full 1.33 million records after outlier trimming. This is the floor against which any ML model should be compared: since the BER rating is a deterministic function of these components, perfect reconstruction is theoretically possible (the residual reflects rounding, renewable energy credits, and minor formula details not captured by simple summation).

We then evaluated four ML model families on a 200,000-record random subsample with 5-fold cross-validation, using only building characteristics (not DEAP intermediate outputs) as features:

| Model | MAE (kWh/m2/yr) | RMSE | R2 |
|-------|-----------------|------|-----|
| DEAP reconstruction (sum PE/area) | 6.96 | 29.07 | 0.942 |
| Ridge regression (linear baseline) | 32.28 | 44.80 | 0.862 |
| ExtraTrees (200 trees) | 20.51 | 30.97 | 0.934 |
| XGBoost (300 trees, GPU-accelerated) | 19.26 | 28.74 | 0.943 |
| LightGBM (300 trees) | 19.54 | 28.91 | 0.943 |

The DEAP reconstruction has lower MAE (6.96 vs 18.05 for the final ML model) but comparable R2 (0.942 vs 0.951). The ML model's marginally higher R2 reflects fewer extreme outliers (the DEAP reconstruction has large errors for the 23% of records with renewable energy credits that require additional formula terms). On MAE — the more interpretable metric — the ML model is 2.6 times worse than the DEAP formula itself.

This establishes a crucial context: the ML model is a lossy approximation to a known formula, not a scientific advance. Its value is not in accuracy but in (a) SHAP-based attribution that decomposes the DEAP output into per-feature contributions, (b) rapid screening from building characteristics without running the full DEAP calculation, and (c) revealing which feature interactions the nonlinear model exploits.

XGBoost narrowly won the tournament on MAE (19.26 versus 19.54 for LightGBM), but the difference is within cross-validation variance. We selected LightGBM for the HDR loop due to its faster training speed.

The Ridge linear baseline already achieves R2 = 0.862, confirming that the BER system is largely a linear function of building characteristics. The nonlinear improvement from tree models (R2 0.862 to 0.943) captures interactions and threshold effects — particularly the heat pump efficiency discontinuity and construction-era regulatory thresholds.

### 3.3 HDR Loop and Composition

The HDR loop tested 11 hypotheses (9 features, 2 model configurations) using 5-fold CV on a 200,000-record subsample. Hyperparameters were tuned by testing learning rate (0.05 vs 0.1), tree count (300 vs 600), and max depth (8 vs 10), selecting by CV MAE. Six hypotheses were kept, five reverted. The final composition combined:

- LightGBM with tuned hyperparameters (learning rate 0.05, 600 trees, max depth 10, L2 regularisation lambda 1.0)
- Four additional domain-knowledge features (compactness ratio, ventilation loss proxy, primary energy factor, space heating fraction)

Evaluated on the full 1.33 million records with 5-fold cross-validation, the composition achieved MAE 18.05 kWh/m2/yr (bootstrap 95% CI: [18.17, 18.33] on 200k subsamples). This represents:

- 44% MAE reduction from the Ridge baseline (32.28 to 18.05)
- 7.6% MAE reduction from the LightGBM baseline (19.54 to 18.05)

**Ablation study.** Space heating fraction (sh_fraction) contributed the bulk of the HDR improvement. This feature — delivered space heating energy divided by total delivered energy — is partially endogenous because it is derived from DEAP intermediate outputs, not directly measured building characteristics:

| Configuration | MAE | R2 |
|--------------|-----|-----|
| Full model (all HDR features) | 18.36 | 0.949 |
| Without sh_fraction | 19.44 | 0.943 |
| Without sh_fraction and PE factor | 19.42 | 0.943 |
| Original features only (no HDR) | 19.44 | 0.943 |

Removing sh_fraction accounts for 1.08 of the 1.09 MAE improvement from the HDR loop. The other three HDR features (compactness ratio, ventilation loss proxy, primary energy factor) contribute negligibly when sh_fraction is absent. The honest model without any DEAP-derived features achieves MAE 19.44 — the version we recommend for applications where DEAP intermediate outputs are unavailable.

### 3.4 Feature Perturbation Analysis

To estimate DEAP sensitivity to individual building characteristics, we trained the final model on all data and applied per-dwelling perturbations. For each intervention, we modified the relevant feature(s) for every applicable dwelling (e.g., chimney sealing only for dwellings that have chimneys) and predicted the new BER score. The difference gives the model's estimate of the DEAP sensitivity.

An earlier version of this analysis used the "average dwelling" — taking the mean of all features and perturbing one. This approach is flawed when the mean is unphysical. For example, the mean chimney count is 0.52 (because 58% of dwellings have zero chimneys); subtracting 1 yields -0.48, a negative chimney count that forces the model to extrapolate out of distribution. The per-dwelling approach avoids this problem by only modifying dwellings where the intervention is physically meaningful.

**Important caveat:** These perturbations measure model sensitivity, not causal retrofit effects. A real chimney seal changes air flow patterns that may affect other features (moisture, indoor temperature, heating demand); a real heat pump installation changes multiple building parameters simultaneously. The perturbation analysis holds all other features fixed, which is a counterfactual assumption, not a physical reality. The distinction between predictive perturbation and causal estimation is fundamental (Fowlie et al. 2018).

### 3.5 SHAP Feature Attribution

We computed SHAP (SHapley Additive exPlanations) values on a random subsample of 5,000 records using the TreeExplainer algorithm. SHAP values decompose each prediction into per-feature contributions, enabling both global feature importance ranking and individual-dwelling attribution.

## 4. Results

### 4.1 Feature Importance

Two complementary importance measures — built-in LightGBM split-based importance and SHAP mean absolute values — agree on the top features but with instructive differences (Figure 2):

| Rank | Feature | SHAP (mean |SHAP|) | Built-in importance (%) |
|------|---------|---------------------|-------------------------|
| 1 | HLP proxy | 55.4 | 8.6 |
| 2 | Heating system efficiency | 23.7 | 11.8 |
| 3 | Primary energy factor | 14.5 | 3.8 |
| 4 | Window area | 9.9 | 4.7 |
| 5 | Window U-value | 9.4 | 4.9 |
| 6 | Number of chimneys | 8.4 | 2.7 |
| 7 | Space heating fraction | 7.7 | 8.2 |
| 8 | Year built | 7.0 | 5.9 |
| 9 | Low-energy lighting (%) | 5.7 | 3.7 |
| 10 | Ground floor area | 4.9 | 5.1 |

**HLP proxy dominates** by SHAP with a mean absolute value of 55.4 kWh/m2/yr — more than double the next feature. This is physically correct: the Heat Loss Parameter is the standard summary metric for building fabric thermal quality. A dwelling's HLP encapsulates the combined effect of wall, roof, floor, window, and door U-values weighted by their areas, normalised by floor area. The built-in importance ranks heating system efficiency first because that feature is used in many tree splits (high cardinality), but SHAP correctly identifies HLP as having the largest *magnitude* of impact on predictions.

**Heating system efficiency** is second by SHAP (23.7). This feature captures the fundamental distinction between conventional heating (60-95% efficiency for gas and oil boilers) and heat pumps (200-450% coefficient of performance). The bimodal distribution creates a natural split point that tree models exploit effectively.

**Primary energy factor** (14.5 by SHAP) was one of our HDR-loop additions. It makes explicit the fuel-specific conversion from delivered to primary energy that is central to the DEAP calculation. In Ireland, electricity has a primary energy factor of 2.08 (reflecting grid carbon intensity), while gas and oil have factors of 1.1. This means the same delivered energy maps to very different BER scores depending on fuel type.

**Windows** rank highly on both measures (area and U-value). Windows typically have U-values of 1.5-5.0 W/m2K compared to 0.2-1.5 for walls, making them disproportionate contributors to heat loss despite their smaller area.

**Number of chimneys** (8.4 by SHAP) is notable. Open chimneys provide uncontrolled ventilation, bypassing any envelope insulation improvements. This feature effectively proxies for the infiltration rate in older homes. The mean SHAP value of 8.4 should be compared to the per-dwelling perturbation estimate of 21.1 for dwellings that actually have chimneys (Section 4.3) — the difference reflects that SHAP averages over all dwellings including the 58% with zero chimneys, while the perturbation analysis conditions on having a chimney to seal.

### 4.2 Per-Band Prediction Accuracy

The distribution of energy values within each BER band (Figure 3) reveals the substantial overlap between adjacent rating categories. The model's accuracy varies substantially across all 15 BER bands:

| Band | Count | MAE (kWh/m2/yr) | Band width |
|------|-------|-----------------|------------|
| A1 | 1,538 | 19.9 | 25 |
| A2 | 161,387 | 5.1 | 25 |
| A3 | 86,941 | 10.5 | 25 |
| B1 | 42,246 | 23.6 | 25 |
| B2 | 67,679 | 18.3 | 25 |
| B3 | 120,562 | 15.5 | 25 |
| C1 | 140,409 | 15.2 | 25 |
| C2 | 144,329 | 16.3 | 25 |
| C3 | 130,751 | 17.8 | 25 |
| D1 | 121,633 | 19.2 | 35 |
| D2 | 103,241 | 21.9 | 40 |
| E1 | 59,837 | 24.8 | 40 |
| E2 | 47,008 | 27.5 | 40 |
| F | 48,575 | 30.9 | 70 |
| G | 53,886 | 41.0 | 450+ |

Two patterns are notable. First, accuracy is best for A2 (MAE 5.1) where the model benefits from a large sample of relatively homogeneous modern homes, and degrades progressively toward G (MAE 41.0) where the pre-regulation stock varies enormously. Second, A1 has anomalously high MAE (19.9) despite being the best band, because it contains only 1,538 records (0.1% of data) — the model struggles with this sparse, extreme category. Similarly, B1 (MAE 23.6) is worse than adjacent B2 and B3, likely reflecting its position at the transition between old and new building stock.

### 4.3 Feature Perturbation Results

The per-dwelling perturbation analysis (Section 3.4) applied single-feature changes to all applicable dwellings and reports the distribution of predicted savings (Figure 5):

| Intervention | Applicable dwellings | Mean saving (kWh/m2/yr) | Median | SD | Cost (EUR) | EUR/unit |
|-------------|---------------------|------------------------|--------|-----|------------|---------|
| Chimney sealing | 563,145 | 21.1 | 19.2 | 10.5 | 200 | 9 |
| LED lighting | 1,057,002 | 4.8 | 4.9 | 2.1 | 500 | 104 |
| Roof insulation | 427,143 | 3.2 | 2.8 | 2.4 | 2,500 | 775 |
| Boiler upgrade | 563,331 | 54.4 | 40.6 | 37.2 | 4,000 | 74 |
| Heat pump | 1,142,838 | 86.7 | 75.5 | 52.4 | 10,000 | 115 |
| Triple glazing | 1,051,628 | 6.0 | 4.8 | 5.4 | 12,000 | 1,986 |

Three findings stand out, with important caveats:

**The model predicts large chimney-related savings.** For the 42% of dwellings with open chimneys, setting the chimney count to zero predicts a mean saving of 21.1 kWh/m2/yr (SD 10.5). This is a model prediction, not a measured effect. The prediction is plausible — open chimneys create uncontrolled ventilation paths — but the magnitude warrants validation through field trials before informing policy. Archetype-specific results range from 26.3 for pre-1930 detached homes to 14.9 for post-2006 homes.

**Heat pump and boiler savings are large but highly variable.** The per-dwelling analysis produces much larger estimates than the mean-dwelling approach (86.7 vs 15.5 for heat pumps) because many dwellings start from very poor heating systems. The high standard deviation (52.4) reflects enormous heterogeneity: a heat pump in a well-insulated 2006 home saves far less than in a poorly-insulated 1960 home. Real-world heat pump performance depends on outdoor temperature, radiator sizing, and hot water demand in ways the model cannot capture.

**Wall insulation sensitivity varies by construction era** but is modest even for the worst stock. Reducing wall U-value by up to 0.3 W/m2K (to a minimum of 0.21) predicts savings of 2.1 for pre-1930 homes (mean wall U 1.34), 1.3 for 1930-1977 (mean U 1.04), and near zero for post-2006 homes. The model has learned that chimney/ventilation losses dominate in older homes, and wall insulation alone does not address the primary heat loss pathway. This does not mean wall insulation is unimportant — it means the model treats it as secondary to ventilation management for the worst-performing stock.

### 4.4 Temporal Holdout

Training on pre-2020 certificates (657,882 records) and testing on 2020-2026 (672,138 records) reveals substantial degradation:

| Split | MAE | RMSE | R2 |
|-------|-----|------|-----|
| Cross-validation (random) | 18.05 | 26.77 | 0.951 |
| Temporal holdout (2020+) | 27.50 | 39.49 | 0.884 |

The model loses 52% of its MAE advantage over the Ridge baseline when evaluated on temporally out-of-sample data. This likely reflects the rapid shift to heat pumps and nZEB standards post-2019: the training data contains few examples of the building types dominating post-2020 construction. This result cautions against using the model for forward-looking policy analysis without periodic retraining.

### 4.5 Geographic and Construction Era Patterns

**County-level variation.** The mean BER ranges from 239 kWh/m2/yr (Leitrim) to 160 (Kildare), a 50% spread. The worst-performing counties are rural western counties (Leitrim, Roscommon, Mayo, Tipperary) with older housing stock. The best-performing counties are Dublin commuter belt counties (Kildare, Meath) and Wicklow, which have a high proportion of post-2006 suburban development.

**Construction era.** This is by far the strongest predictor of BER rating (Figure 4). Mean BER by era: pre-1930 (339), 1930-1977 (271), 1978-2005 (199), 2006-2011 (146), 2012-2020 (54), 2021+ (40). The 8.5:1 ratio between pre-1930 and 2021+ dwellings reflects the cumulative effect of successive building regulations. However, we emphasise that this is the DEAP-calculated ratio; the measured consumption ratio would be closer to 2:1 due to the prebound and rebound effects.

**Heat pump adoption.** Heat pumps are present in less than 1% of pre-2012 certificates but 50% of 2012-2020 and 80% of 2021+ certificates. This near-universal adoption in new construction reflects the nZEB regulation's de facto requirement for renewable heating.

## 5. Discussion

### 5.1 What the Model Tells Us About DEAP

The DEAP intermediate outputs in the dataset reconstruct the BER rating with MAE 6.96 kWh/m2/yr. Our ML model, using only building characteristics, achieves MAE 18.05 — 2.6 times worse. This establishes that the model is a lossy approximation to a known formula. The residual beyond the DEAP reconstruction (4.9% of variance unexplained) likely reflects: (a) renewable energy credit calculations not fully captured by our features, (b) BER assessor variation, and (c) measurement uncertainty in U-values and areas.

The dominance of HLP proxy and heating system efficiency in the SHAP analysis is expected because these are the two primary physical mechanisms in the DEAP calculation. The model has correctly learned the structure of the formula — but this is function approximation, not scientific discovery. The European EPC prediction literature has reached similar conclusions: Pasichnyi et al. (2019) for Sweden, Hong et al. (2020) for England, and Cozza et al. (2020) for Switzerland all find that gradient boosting can approximate national energy rating formulae from building characteristics, with fabric quality and heating system type as dominant predictors.

### 5.2 The Performance Gap: What This Data Cannot Tell Us

We must be explicit about what this analysis does *not* show. The BER dataset contains only DEAP-calculated energy, not metered gas and electricity bills. The "performance gap" — the divergence between calculated and actual consumption — is well-documented in the literature but cannot be studied with this data alone.

Moran et al. (2020) matched BER certificates with smart meter data for approximately 5,000 Irish homes and found that: (a) A-rated homes used approximately 1.3 times their DEAP-calculated energy (rebound effect), (b) G-rated homes used approximately 0.6 times their DEAP-calculated energy (prebound effect), and (c) the actual energy gap between the best and worst-rated homes was roughly 2:1, not the 8.5:1 that DEAP predicts.

This means our retrofit cost-effectiveness estimates describe what DEAP *predicts* will happen, not what actually happens. The literature suggests actual savings from retrofits are 20-40% smaller than DEAP suggests, due to a combination of rebound effects (occupants increasing comfort post-retrofit) and installation quality gaps (actual insulation performance below laboratory-measured values).

### 5.3 Policy Implications

These are model-derived hypotheses, not causal estimates. They warrant investigation through field trials, not direct implementation.

**Chimney ventilation deserves field investigation.** The model predicts large DEAP sensitivity to chimney count, suggesting that uncontrolled ventilation through open chimneys may be a substantial heat loss pathway in older Irish homes. This is physically plausible and consistent with the building science literature on infiltration losses (Jones et al. 2016). However, the magnitude (21 kWh/m2/yr average for homes with chimneys) has not been validated by before-and-after measurement. SEAI should commission field trials measuring actual energy consumption before and after chimney sealing to validate or reject this prediction.

**Target by construction era, not geography.** County-level BER variation (239 in Leitrim to 160 in Kildare) is almost entirely explained by construction era. A pre-1978 house in Dublin has similar DEAP characteristics to a pre-1978 house in Mayo.

**Heat pumps interact with fabric quality.** The model predicts that heat pump benefit depends on existing insulation quality. For pre-1978 dwellings, fabric improvement before heat pump installation may be the correct sequence. For post-2006 dwellings, the model predicts large benefit from heat pump alone. These are DEAP predictions subject to the same performance gap caveats as all other findings.

### 5.4 Limitations

1. **No measured energy data.** All results describe DEAP-predicted, not actual, energy performance. The well-documented performance gap means real savings are 20-40% smaller than DEAP predicts.

2. **The ML model does not outperform DEAP.** The DEAP reconstruction from intermediate outputs achieves MAE 6.96 vs the ML model's 18.05. The model's contribution is SHAP attribution and rapid screening, not accuracy.

3. **Perturbations are not causal estimates.** Changing one feature while holding all others fixed does not correspond to a real retrofit, which changes multiple correlated properties simultaneously. The perturbation results are model sensitivity analyses, not policy recommendations.

4. **Space heating fraction is partially endogenous.** This feature is derived from DEAP intermediate outputs and contributes the majority of the HDR improvement (1.08 of 1.09 MAE points). The model without this feature achieves MAE 19.44.

5. **Temporal generalisation is poor.** The temporal holdout shows MAE degradation from 18.05 to 27.50 on post-2020 data, indicating the model does not generalise across regulatory regime changes.

6. **Self-selection bias.** BER certificates are required for sale or rental. Pre-1960 rural owner-occupied dwellings may be under-represented.

7. **No before-and-after validation.** The public SEAI dataset is anonymised (no dwelling identifiers), so we cannot match repeat certificates for the same dwelling to validate perturbation predictions against observed changes. This would be possible with the non-public version of the dataset.

8. **No multi-measure interactions.** Single-feature perturbations cannot capture interaction effects (e.g., insulation plus heat pump). In practice, measures are combined.

9. **Cost estimates are approximate.** Retrofit costs depend on dwelling size, access, contractor availability, and grant eligibility.

10. **No assessor effects.** Assessor identity is not included in the public dataset. Assessor variation may explain some of the residual error.

## 6. Conclusion

We analysed 1.33 million real Irish BER certificates to understand what the DEAP formula weighs most heavily and where it is most sensitive. We are explicit about what this exercise is and is not.

**What it is:** A sensitivity analysis of a known physics formula using gradient boosting and SHAP attribution, applied at national scale.

**What it is not:** A discovery about building physics, a causal evaluation of retrofit effectiveness, or a study of the performance gap.

Our main findings are:

1. **The ML model approximates DEAP but does not outperform it.** The DEAP intermediate outputs in the dataset achieve MAE 6.96; the ML model achieves 18.05. The model's value is in SHAP attribution and rapid screening, not accuracy.

2. **The Heat Loss Parameter dominates DEAP sensitivity.** HLP — total fabric heat loss per unit floor area — has more than double the SHAP impact of any other feature. This confirms that DEAP primarily measures fabric quality, which is expected from the formula's structure.

3. **The model predicts high DEAP sensitivity to chimney count,** with mean savings of 21.1 kWh/m2/yr for dwellings with open chimneys. This prediction is physically plausible but unvalidated by field measurement and should be treated as a hypothesis for testing, not a policy recommendation.

4. **Temporal generalisation is poor.** The model trained on pre-2020 data degrades substantially on post-2020 certificates (MAE 27.50 vs 18.05), indicating it does not generalise across regulatory regime changes.

5. **All findings describe DEAP-calculated energy, not real consumption.** The performance gap means actual savings from any intervention are 20-40% smaller than DEAP predicts.

Future work should: (a) validate chimney-sealing predictions through field trials with measured energy consumption, (b) use the non-public SEAI dataset (with dwelling identifiers) to match before-and-after certificates for the same property, and (c) combine BER certificates with smart meter data to quantify the dwelling-level performance gap.

## Figures

**Figure 1.** Predicted vs actual BER energy rating (kWh/m2/yr) for 200,000 dwellings using 5-fold cross-validation. The hexbin density plot shows agreement along the 1:1 line (MAE = 18.4, R2 = 0.949). Note that R2 = 0.949 is expected given that the target is a deterministic function of building characteristics; the DEAP formula itself achieves MAE 6.96. See `plots/pred_vs_actual.png`.

**Figure 2.** Top 15 features ranked by mean absolute SHAP value. The Heat Loss Parameter (HLP) dominates at 55.4 kWh/m2/yr — more than double the next feature (heating system efficiency, 23.7). Features are colour-coded by category: building fabric (blue), heating system (orange), ventilation (green), and other (purple). See `plots/feature_importance.png`.

**Figure 3.** Distribution of DEAP-calculated energy consumption within each BER rating band (A1 through G). Box plots show IQR with 1.5 IQR whiskers; the dashed line traces official band upper boundaries. The substantial overlap between adjacent bands illustrates the compression inherent in the rating system. See `plots/headline_finding.png`.

**Figure 4.** BER energy by construction era, showing the massive vintage effect. Mean energy drops from 339 kWh/m2/yr (pre-1930) to 40 kWh/m2/yr (2021+), an 8.5:1 ratio driven by cumulative building regulation improvements. Diamond markers show era means; boxes show IQR. See `plots/era_comparison.png`.

**Figure 5.** Per-dwelling feature perturbation results for applicable dwellings. Left panel: mean predicted DEAP improvement; right panel: approximate cost per kWh/m2/yr saved. Chimney sealing shows the highest predicted sensitivity per euro, but this is a model prediction requiring field validation. Colours indicate cost-effectiveness tiers. See `plots/retrofit_cost_effectiveness.png`.

## References

1. SEAI. Dwelling Energy Assessment Procedure (DEAP) Manual, Version 4.2.2. Sustainable Energy Authority of Ireland, 2019.
2. ISO 13790:2008. Energy performance of buildings — Calculation of energy use for space heating and cooling.
3. EU Directive 2010/31/EU. Energy Performance of Buildings Directive (recast).
4. Anderson, B. Conventions for U-value calculations. BRE Report BR 443, 2006.
5. Jokisalo, J., et al. Building leakage, infiltration, and energy performance analyses for Finnish detached houses. Building and Environment, 44(2), 2009.
6. SEAI. Primary Energy Conversion Factors for the Irish Context. Technical Report, 2019.
7. Sunikka-Blank, M. & Galvin, R. Introducing the prebound effect: the gap between performance and actual energy consumption. Building Research & Information, 40(3), 2012.
8. Galvin, R. Making the 'rebound effect' more useful for performance evaluation of thermal retrofits. Building and Environment, 71, 2014.
9. Galvin, R. & Sunikka-Blank, M. Quantifying the 'performance gap' — Are the EPCs really performance certificates? Energy and Buildings, 73, 2014.
10. Moran, P., et al. Measured vs calculated energy performance in Irish residential buildings. Energy and Buildings, 226, 2020.
11. Ahern, C. & Norton, B. Energy Performance Certification: Misassessment due to assuming default data. Energy and Buildings, 224, 2020.
12. Famuyibo, A., et al. Developing archetypes for domestic dwellings — An Irish case study. Energy and Buildings, 50, 2012.
13. Stafford, A. & Lilley, D. Predicting in situ heat pump performance: An investigation into a single ground-source heat pump system in the context of 10 similar systems. Energy and Buildings, 45(2), 2012.
14. Jones, B., et al. Assessing uncertainty in housing stock infiltration rates and associated heat loss. Building and Environment, 108, 2016.
15. IEA. Energy Efficiency 2019 — Lighting. International Energy Agency, 2019.
16. SEAI. Energy in Ireland 2023 Report. Sustainable Energy Authority of Ireland, 2023.
17. Collins, M. & Curtis, J. Identification of the information gap in residential energy efficiency: How home-owners and landlords differ. Energy Efficiency, 11, 2018.
18. Ali, U., et al. A data-driven approach for multi-scale building archetypes development. Energy and Buildings, 202, 2019.
19. Hundi, P. & Shahsavar, R. Comparative study of machine learning methods for building energy use prediction. Energy and Buildings, 208, 2020.
20. Wei, Y., et al. A review of data-driven approaches for prediction and classification of building energy consumption. Renewable and Sustainable Energy Reviews, 82, 2018.
21. Beagon, P., et al. Closing the gap between design and as-built performance of nearly zero energy housing. Energy and Buildings, 211, 2020.
22. Box, G.E.P. & Cox, D.R. An analysis of transformations. Journal of the Royal Statistical Society, Series B, 26(2), 1964.
23. Amasyali, K. & El-Gohary, N. A review of data-driven building energy consumption prediction studies. Renewable and Sustainable Energy Reviews, 81, 2018.
24. CIBSE. Guide A: Environmental Design, 8th edition. Chartered Institution of Building Services Engineers, 2015.
25. Dall'O', G., et al. A methodology for evaluating the performance of residential buildings. Energy and Buildings, 60, 2013.
26. Walsh, S. A summary of climate averages for Ireland, 1981-2010. Climatological Note No. 14, Met Eireann, 2012.
27. S.I. No. 259/2019. European Union (Energy Performance of Buildings) Regulations 2019.
28. SEAI. Better Energy Homes Scheme — Grant Eligibility. Sustainable Energy Authority of Ireland, 2023.
29. Hyland, M., et al. The value of domestic building energy efficiency: evidence from Ireland. Energy Economics, 40, 2013.
30. Economidou, M., et al. Review of 50 years of EU energy efficiency policies for buildings. Energy and Buildings, 225, 2020.
31. Lundberg, S. & Lee, S. A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems, 30, 2017.
32. Ke, G., et al. LightGBM: A highly efficient gradient boosting decision tree. Advances in Neural Information Processing Systems, 30, 2017.
33. Chen, T. & Guestrin, C. XGBoost: A scalable tree boosting system. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2016.
34. Pasichnyi, O., et al. Data-driven building energy labeling for Stockholm. Energy and Buildings, 184, 2019.
35. Hong, T., et al. Data-driven predictive model of the English EPC. Applied Energy, 278, 2020.
36. Cozza, S., et al. Measuring the thermal energy performance gap in Swiss buildings. Energy and Buildings, 224, 2020.
37. Majcen, D., et al. Theoretical vs. actual energy consumption of labelled dwellings in the Netherlands. Energy Policy, 54, 2013.
38. Galvin, R. & Sunikka-Blank, M. Quantification of the performance gap in German residential buildings. Energy and Buildings, 73, 2016.
39. Fowlie, M., et al. Do energy efficiency investments deliver? Evidence from the Weatherization Assistance Program. Quarterly Journal of Economics, 133(3), 2018.
40. Allcott, H. & Greenstone, M. Is there an energy efficiency gap? Journal of Economic Perspectives, 26(1), 2012.
41. Arcipowska, A., et al. Energy performance certificates across the EU: A mapping of national approaches. BPIE, 2014.
42. Fabbri, K., et al. Heritage buildings and energy performance legislation. Energy and Buildings, 72, 2014.
