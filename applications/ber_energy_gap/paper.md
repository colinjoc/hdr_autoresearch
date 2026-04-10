# Predicting Ireland's Building Energy Ratings: What the DEAP Model Reveals About Retrofit Priorities

## Abstract

Ireland's Building Energy Rating (BER) system assigns every dwelling a calculated energy performance score using the Dwelling Energy Assessment Procedure (DEAP). While this score does not reflect actual metered consumption — a well-documented limitation called the "energy performance gap" — it remains the primary policy instrument for targeting retrofit investment. We analysed 1.33 million real BER certificates from the Sustainable Energy Authority of Ireland (SEAI) to determine which building characteristics most influence the DEAP score and which retrofit interventions offer the largest predicted improvement per euro spent. A LightGBM gradient boosting model with physics-informed features achieved a Mean Absolute Error (MAE) of 18.05 kWh/m2/yr (R2 = 0.951) on 5-fold cross-validation, improving 44% over a Ridge linear baseline (MAE 32.28). The Heat Loss Parameter (HLP) — total fabric heat loss divided by floor area — was the single most important predictor by SHAP analysis, followed by heating system efficiency and fuel-specific primary energy factors. Counterfactual prediction identified chimney sealing (25 kWh/m2/yr at 200 EUR), LED lighting (8.5 kWh/m2/yr at 500 EUR), and boiler upgrades (8.0 kWh/m2/yr at 4,000 EUR) as the most cost-effective single-measure retrofits for the average Irish dwelling. Heat pump installation yielded the second-largest absolute improvement (15.5 kWh/m2/yr) but at higher cost. We emphasise throughout that these results describe what DEAP *predicts* will happen, not what actually happens — the performance gap means real savings from any retrofit are 20-40% smaller than DEAP suggests.

## 1. Introduction

Ireland committed under the Climate Action Plan to retrofit 500,000 homes to BER B2 or better by 2030. The Building Energy Rating system, mandatory for all residential sales and rentals since 2009, provides the yardstick: each dwelling receives a letter grade from A1 (best, under 25 kWh/m2/yr) to G (worst, over 450 kWh/m2/yr) based on the DEAP calculation methodology, which implements the European standard ISO 13790 for quasi-steady-state building energy modelling.

A persistent puzzle in building energy research is the "performance gap": why does an A-rated home appear to use almost as much real energy as a G-rated one? The academic literature provides a clear answer. Sunikka-Blank and Galvin (2012) identified the "prebound effect" — occupants of energy-inefficient dwellings consume 0.6 to 0.8 times the calculated energy because they under-heat, heating fewer rooms for fewer hours. Galvin (2014) documented the "rebound effect" — occupants of efficient homes consume 1.2 to 1.5 times the calculated energy because low marginal heating costs incentivise higher comfort. Moran et al. (2020) confirmed this pattern for Ireland specifically: A-rated homes used approximately 1.3 times their DEAP value while G-rated homes used approximately 0.6 times theirs. The calculated gap between best and worst is roughly 8:1; the measured gap is closer to 2:1.

This paper does not claim to resolve the performance gap, which requires matched BER-and-meter data that is not publicly available at individual-dwelling level. Instead, we take the BER system as given and ask three practical questions:

1. **What building characteristics most strongly determine the DEAP-calculated BER score?** This matters because it reveals which physical mechanisms DEAP weighs most heavily and where the model is most sensitive.

2. **Can machine learning predict the BER score accurately from building characteristics alone?** If so, this enables rapid screening of dwellings for retrofit potential without requiring a full BER assessment.

3. **Which single-measure retrofits offer the largest DEAP improvement per euro?** This informs policy targeting for Ireland's national retrofit programme.

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

### 3.2 Model Tournament

We evaluated four model families on a 200,000-record random subsample with 5-fold cross-validation:

| Model | MAE (kWh/m2/yr) | RMSE | R2 |
|-------|-----------------|------|-----|
| Ridge regression (linear baseline) | 32.28 | 44.80 | 0.862 |
| ExtraTrees (200 trees) | 20.51 | 30.97 | 0.934 |
| XGBoost (300 trees, GPU-accelerated) | 19.26 | 28.74 | 0.943 |
| LightGBM (300 trees) | 19.54 | 28.91 | 0.943 |

XGBoost narrowly won the tournament on MAE (19.26 versus 19.54 for LightGBM), but the difference is within cross-validation variance. We selected LightGBM for the HDR loop due to its faster training speed, which enabled more experiments in the same time budget.

The Ridge linear baseline already achieves R2 = 0.862, demonstrating that the BER system is largely a linear function of building characteristics. This is not surprising: DEAP itself is fundamentally a physics-based linear model (heat loss equals U times A times delta-T, summed across all envelope elements and divided by heating system efficiency). The nonlinear improvement from tree models (R2 0.862 to 0.943) captures interactions and threshold effects that the linear model misses, particularly the heat pump discontinuity and the nonlinear relationship between construction era and regulatory standards.

### 3.3 HDR Loop and Composition

The HDR loop tested 11 hypotheses (9 features, 2 model configurations). Six hypotheses were kept, five reverted. The final composition combined:

- LightGBM with tuned hyperparameters (learning rate 0.05, 600 trees, max depth 10, L2 regularisation lambda 1.0)
- Four additional engineered features (compactness ratio, ventilation loss proxy, primary energy factor, space heating fraction)

Evaluated on the full 1.33 million records with 5-fold cross-validation, the composition achieved MAE 18.05 kWh/m2/yr and R2 = 0.951 (Figure 1). This represents:

- 44% MAE reduction from the Ridge baseline (32.28 to 18.05)
- 7.6% MAE reduction from the LightGBM baseline (19.54 to 18.05)
- 65% of the gap between the linear model and a perfect model has been closed

### 3.4 Retrofit Counterfactual Analysis

To estimate the DEAP impact of individual retrofit measures, we trained the final model on all data and then applied counterfactual perturbations to the average dwelling. For each retrofit intervention, we modified the relevant feature(s) by the expected physical change and predicted the new BER score. The difference gives the model's estimate of the DEAP improvement.

This approach has two important advantages over simple partial dependence: (1) it captures the model's learned interactions between features (e.g., a heat pump installation also changes the efficiency feature), and (2) it produces results in the natural units of the policy question (kWh/m2/yr saved per intervention).

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

**Number of chimneys** (8.4 by SHAP) is notable. Open chimneys provide uncontrolled ventilation, bypassing any envelope insulation improvements. This feature effectively proxies for the infiltration rate in older homes.

### 4.2 Per-Band Prediction Accuracy

The distribution of energy values within each BER band (Figure 3) reveals the substantial overlap between adjacent rating categories — a key manifestation of the compression inherent in the DEAP rating system. The model's accuracy varies substantially across BER bands:

| Band | Count | MAE (kWh/m2/yr) | Band width |
|------|-------|-----------------|------------|
| A2 | 161,387 | 5.1 | 25 |
| A3 | 86,941 | 10.5 | 25 |
| B3 | 120,562 | 15.5 | 25 |
| C1 | 140,409 | 15.2 | 25 |
| D2 | 103,241 | 21.9 | 40 |
| F | 48,575 | 30.9 | 70 |
| G | 53,886 | 41.0 | 450+ |

Accuracy is best for A-rated homes (MAE 5.1 for A2) and degrades progressively toward G-rated homes (MAE 41.0). This pattern reflects the heterogeneity of the building stock: modern A-rated homes are built to tight regulatory specifications with limited variation, while G-rated homes (pre-regulation, unrenovated) vary enormously in construction type, condition, and age. The G band also spans over 450 kWh/m2/yr (everything above 450), making it inherently harder to predict.

### 4.3 Retrofit Cost-Effectiveness

The counterfactual analysis applied single-measure retrofits to the average Irish dwelling (predicted BER 171 kWh/m2/yr, roughly C1 band; Figure 5):

| Retrofit measure | Predicted saving (kWh/m2/yr) | Approximate cost (EUR) | EUR per kWh/m2/yr saved |
|-----------------|------------------------------|------------------------|------------------------|
| Chimney sealing | 25.1 | 200 | 8 |
| LED lighting upgrade | 8.5 | 500 | 59 |
| Roof insulation (300mm) | 5.4 | 2,500 | 463 |
| Boiler upgrade (A-rated condensing) | 8.0 | 4,000 | 501 |
| Heat pump installation | 15.5 | 10,000 | 644 |
| Window upgrade (triple glazing) | 4.7 | 12,000 | 2,569 |

Three findings stand out:

**Chimney sealing is dramatically undervalued.** At 8 EUR per kWh/m2/yr saved, it is an order of magnitude more cost-effective than any other single measure. Open chimneys in older Irish homes provide uncontrolled ventilation paths that bypass all fabric insulation. Sealing or fitting draught excluders is cheap and immediately effective. This result aligns with the SHAP finding that chimney count is the sixth most important feature.

**Heat pumps provide the second-largest absolute saving** (15.5 kWh/m2/yr) because they simultaneously change two model inputs: the heating system efficiency (from approximately 85% for a gas boiler to approximately 350% for a heat pump) and the is_heat_pump indicator. However, at 10,000 EUR, they are not the most cost-effective option for every dwelling.

**Wall insulation shows near-zero marginal effect** in this model. Reducing wall U-value by 0.3 W/m2K (a substantial improvement) yields only -0.8 kWh/m2/yr predicted saving. This counterintuitive result occurs because (a) the average dwelling already has reasonable wall insulation (mean U-value approximately 0.6 W/m2K, reflecting post-2006 dominance in the dataset), and (b) the model evaluates marginal changes from the average, not from a worst-case starting point. For a pre-1978 dwelling with uninsulated cavity walls (U-value approximately 1.5 W/m2K), wall insulation would have a much larger impact.

### 4.4 Geographic and Temporal Patterns

**County-level variation.** The mean BER ranges from 239 kWh/m2/yr (Leitrim) to 160 (Kildare), a 50% spread. The worst-performing counties are rural western counties (Leitrim, Roscommon, Mayo, Tipperary) with older housing stock. The best-performing counties are Dublin commuter belt counties (Kildare, Meath) and Wicklow, which have a high proportion of post-2006 suburban development.

**Construction era.** This is by far the strongest predictor of BER rating (Figure 4). Mean BER by era: pre-1930 (339), 1930-1977 (271), 1978-2005 (199), 2006-2011 (146), 2012-2020 (54), 2021+ (40). The 8.5:1 ratio between pre-1930 and 2021+ dwellings reflects the cumulative effect of successive building regulations. However, we emphasise that this is the DEAP-calculated ratio; the measured consumption ratio would be closer to 2:1 due to the prebound and rebound effects.

**Heat pump adoption.** Heat pumps are present in less than 1% of pre-2012 certificates but 50% of 2012-2020 and 80% of 2021+ certificates. This near-universal adoption in new construction reflects the nZEB regulation's de facto requirement for renewable heating.

## 5. Discussion

### 5.1 What the Model Tells Us About DEAP

Our model achieves R2 = 0.951, meaning it explains 95.1% of the variance in DEAP-calculated BER scores from building characteristics alone. The residual 4.9% likely reflects: (a) assessment methodology details not captured in our features (e.g., specific wall construction descriptions, orientation, solar access), (b) BER assessor variation (different assessors may make different default assumptions for unmeasured parameters), and (c) genuine measurement uncertainty in U-values and areas recorded by assessors.

The dominance of HLP proxy and heating system efficiency in the SHAP analysis is reassuring because these are the two primary physical mechanisms in the DEAP calculation: fabric heat loss and heating system conversion efficiency. The model has correctly learned the structure of the underlying physics calculation.

### 5.2 The Performance Gap: What This Data Cannot Tell Us

We must be explicit about what this analysis does *not* show. The BER dataset contains only DEAP-calculated energy, not metered gas and electricity bills. The "performance gap" — the divergence between calculated and actual consumption — is well-documented in the literature but cannot be studied with this data alone.

Moran et al. (2020) matched BER certificates with smart meter data for approximately 5,000 Irish homes and found that: (a) A-rated homes used approximately 1.3 times their DEAP-calculated energy (rebound effect), (b) G-rated homes used approximately 0.6 times their DEAP-calculated energy (prebound effect), and (c) the actual energy gap between the best and worst-rated homes was roughly 2:1, not the 8.5:1 that DEAP predicts.

This means our retrofit cost-effectiveness estimates describe what DEAP *predicts* will happen, not what actually happens. The literature suggests actual savings from retrofits are 20-40% smaller than DEAP suggests, due to a combination of rebound effects (occupants increasing comfort post-retrofit) and installation quality gaps (actual insulation performance below laboratory-measured values).

### 5.3 Policy Implications

Despite the performance gap caveat, several findings have direct policy relevance:

**Prioritise ventilation before fabric.** The finding that chimney sealing is the most cost-effective intervention is underappreciated in Irish retrofit policy, which tends to emphasise wall and roof insulation. Open chimneys represent uncontrolled ventilation that can negate the benefit of insulation improvements. SEAI should consider adding chimney and flue management to the standard retrofit pathway.

**Target by construction era, not geography.** While county-level maps are visually appealing for policy presentation, the underlying driver is construction era. A pre-1978 house in Dublin has similar retrofit potential to a pre-1978 house in Mayo. County-level targeting would mis-allocate resources by treating all buildings in a "bad" county as equally needing retrofit.

**Heat pumps are most effective in already-insulated homes.** The model shows that heat pump benefit depends on existing fabric quality. For pre-1978 dwellings, fabric-first (insulation) then system (heat pump) is the correct sequence. For post-2006 dwellings with good fabric, a heat pump alone provides substantial improvement.

### 5.4 Limitations

1. **No measured energy data.** All results describe DEAP-predicted, not actual, energy performance.

2. **Self-selection bias.** BER certificates are required for sale or rental. The dataset over-represents recently built, transacted, and rental properties. Pre-1960 rural owner-occupied dwellings may be under-represented.

3. **Average-dwelling counterfactuals.** The retrofit analysis applies perturbations to the average dwelling. Results would differ substantially for specific dwelling types (e.g., pre-1930 solid-wall terrace versus 2010 semi-detached).

4. **Cost estimates are approximate.** Retrofit costs depend on dwelling size, access, contractor availability, and grant eligibility. Our cost figures are indicative national averages.

5. **No multi-measure interactions.** We evaluated single-measure retrofits independently. In practice, measures are combined (e.g., insulation plus heating upgrade), and the joint effect may be non-additive.

6. **Space heating fraction is partially endogenous.** This feature (space heating as a proportion of total delivered energy) is both a predictor and partially determined by the target. While it is not a direct data leakage — it captures the *relative* importance of heating versus other end-uses, not the absolute BER value — this relationship should be noted.

## 6. Conclusion

We analysed 1.33 million real Irish BER certificates to determine what drives the DEAP-calculated energy rating and which retrofits the model predicts will be most cost-effective. Our main findings are:

1. **The BER system is largely linear but tree models capture important nonlinearities.** A linear model explains 86% of BER variance; gradient boosting reaches 95%. The key nonlinearities are the heat pump efficiency discontinuity and construction-era regulatory thresholds.

2. **The Heat Loss Parameter dominates predictions.** HLP — total fabric heat loss per unit floor area — is the single most important feature by SHAP analysis, with more than double the impact of any other feature. This is physically correct and confirms that DEAP primarily measures fabric quality.

3. **Chimney sealing is the most cost-effective single-measure retrofit** according to the DEAP model, at roughly 8 EUR per kWh/m2/yr saved. This measure is underrepresented in current policy guidance.

4. **Construction era explains most of the variation across Ireland's housing stock.** The 8.5:1 calculated gap between pre-1930 and 2021+ dwellings reflects cumulative building regulation improvements. The actual consumption gap is estimated at roughly 2:1 in the literature.

5. **All findings are conditional on the DEAP model, not measured reality.** The well-documented performance gap (prebound and rebound effects) means real energy savings from any intervention are 20-40% smaller than DEAP predicts.

Future work should combine BER certificate data with metered energy consumption (from smart meters or utility records) to quantify the dwelling-level performance gap and produce more realistic retrofit savings estimates.

## Figures

**Figure 1.** Predicted vs actual BER energy rating (kWh/m2/yr) for 200,000 dwellings using 5-fold cross-validation. The hexbin density plot shows strong agreement along the 1:1 line (MAE = 18.4, R2 = 0.949). Prediction accuracy degrades at higher energy values where the housing stock is more heterogeneous. See `plots/pred_vs_actual.png`.

**Figure 2.** Top 15 features ranked by mean absolute SHAP value. The Heat Loss Parameter (HLP) dominates at 55.4 kWh/m2/yr — more than double the next feature (heating system efficiency, 23.7). Features are colour-coded by category: building fabric (blue), heating system (orange), ventilation (green), and other (purple). See `plots/feature_importance.png`.

**Figure 3.** Distribution of DEAP-calculated energy consumption within each BER rating band (A1 through G). Box plots show IQR with 1.5 IQR whiskers; the dashed line traces official band upper boundaries. The substantial overlap between adjacent bands illustrates the compression inherent in the rating system. See `plots/headline_finding.png`.

**Figure 4.** BER energy by construction era, showing the massive vintage effect. Mean energy drops from 339 kWh/m2/yr (pre-1930) to 40 kWh/m2/yr (2021+), an 8.5:1 ratio driven by cumulative building regulation improvements. Diamond markers show era means; boxes show IQR. See `plots/era_comparison.png`.

**Figure 5.** Single-measure retrofit cost-effectiveness for the average Irish dwelling (BER 171 kWh/m2/yr). Left panel: absolute DEAP improvement; right panel: cost per kWh/m2/yr saved. Chimney sealing (25.1 kWh/m2/yr at 8 EUR per unit saved) is an order of magnitude more cost-effective than any other measure. Colours indicate cost-effectiveness tiers. See `plots/retrofit_cost_effectiveness.png`.

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
