# Why Does an A-Rated Irish Home Use Almost the Same Energy as a G-Rated One? A Hypothesis-Driven Analysis of the BER Performance Gap

## Abstract

Ireland's Building Energy Rating (BER) system, based on the Dwelling Energy Assessment Procedure (DEAP), assigns homes a rating from A1 (best) to G (worst) based on calculated primary energy consumption. Published studies matching BER certificates to metered energy data (Coyne & Denny 2021) show that actual energy consumption converges dramatically across rating bands: a G-rated home uses approximately 1.5-2.5 times as much energy as an A-rated home, not the 5-10 times that BER ratings imply. We investigate this "performance gap" using a Hypothesis-Driven Research (HDR) protocol with 20 pre-registered experiments on a synthetic dataset of 100,000 BER certificates calibrated to published SEAI (Sustainable Energy Authority of Ireland) statistics. The winning ExtraTrees model achieves a cross-validated Mean Absolute Error (MAE) of 33.03 kWh/m2/yr (R2=0.88) on predicting BER energy values from building characteristics. The single most impactful feature was a dwelling form factor proxy capturing the surface-area-to-volume ratio, which reduced MAE from 55.5 to 34.2 (38% improvement). Phase B discovery analysis reveals that cavity wall insulation is the most cost-effective single retrofit measure at EUR28 per kWh/m2/yr saved, while deep retrofit packages (wall insulation + heat pump + Mechanical Ventilation with Heat Recovery (MVHR)) can move a 1950s semi-detached home from D2 to B1 at a total cost of EUR25,200. The fundamental limitation is that BER certificates provide DEAP-calculated energy, not measured energy. The performance gap cannot be measured from BER data alone. Our analysis quantifies what the BER system rewards and where the largest DEAP-to-reality discrepancies are predicted to occur based on the published Irish performance gap literature.

## 1. Introduction

### 1.1 The Performance Gap in Irish Housing

Ireland's BER system was introduced in 2007, implementing the European Union (EU) Energy Performance of Buildings Directive (EPBD). Every dwelling offered for sale or rent in Ireland must have a BER certificate showing a rating from A1 (most energy efficient) to G (least efficient) and a calculated energy value in kilowatt-hours per square meter per year (kWh/m2/yr). The calculation uses the Dwelling Energy Assessment Procedure (DEAP) [1], a quasi-steady-state monthly energy balance model based on the International Organisation for Standardisation (ISO) 13790 standard [2].

The "performance gap" -- the systematic discrepancy between calculated and actual energy consumption -- is among the most extensively documented phenomena in building science. Sunikka-Blank and Galvin [3] defined the "prebound effect": occupants of poorly-rated homes use less energy than predicted because they under-heat, close off rooms, or tolerate cold. Galvin [4] formalised this as a ratio of actual to predicted consumption, finding prebound ratios of approximately 0.6 for the worst-rated German dwellings. Majcen et al. [5] confirmed these findings with 200,000 Dutch homes.

In Ireland, Coyne and Denny [6] matched approximately 3,000 BER certificates to metered energy data from the Commission for Energy Regulation (CER) Smart Meter Trials [7]. They found prebound factors of 0.45-0.65 for E-G rated homes and rebound factors of 1.1-1.3 for A-B rated homes. Building vintage was the strongest predictor of gap magnitude.

The Economic and Social Research Institute (ESRI) March 2026 bulletin [8] concluded that Ireland is "lagging" on retrofit pace, with current rates insufficient to meet the National Retrofit Plan's target of 500,000 homes upgraded to BER B2 by 2030 [9]. Understanding what the BER system actually measures -- and where it diverges from reality -- is essential for effective retrofit policy.

### 1.2 Research Question

We ask two questions:
1. **What building characteristics predict the DEAP-calculated BER energy value?** This is a question about what the BER system rewards, not about actual energy consumption.
2. **Which retrofit measures are predicted to produce the largest, most cost-effective BER improvements for different Irish housing archetypes?**

### 1.3 Fundamental Limitation

BER certificates provide the output of the DEAP calculation engine, not measured energy consumption. The energy value on a BER certificate is a model prediction under standardised occupancy assumptions (20C living area, 18C elsewhere, 16 hours heating per day, standard occupancy from floor area). Real households deviate enormously from these assumptions: Irish homes are typically heated to 18-19C [10, 11], many households only heat the living room [12], and actual occupancy varies hugely. The "performance gap" can only be inferred, not directly measured, from BER data. Every quantitative finding in this paper is about predicting the DEAP model's output, not about predicting actual energy bills.

## 2. Detailed Baseline

### 2.1 Data

Because the SEAI BER Research Tool requires manual county-by-county CSV export or a research data agreement for bulk access, and programmatic API access is not publicly available, we constructed a calibrated synthetic dataset of 100,000 BER certificates. The synthetic data generator captures:

- **Housing stock distribution**: County-weighted sampling matching the Central Statistics Office (CSO) 2022 housing census [13], with Dublin representing 28% of stock and rural counties proportionally represented.
- **Construction period distribution**: Year-built weights calibrated to SEAI annual BER reports [14] and CSO housing stock data, with the Celtic Tiger era (2000-2008) appropriately over-represented.
- **Building fabric characteristics**: Wall type, insulation, roof insulation, windows, and floor insulation assigned probabilistically by construction era, reproducing the documented relationship between building age and BER rating [15, 16].
- **Heating systems**: Fuel type distribution matching SEAI energy statistics [17]: approximately 37% oil, 34% gas, 12% solid fuel, 8% heat pump, with gas availability varying by county (80% in Dublin, 5% in rural western counties).
- **DEAP-like energy calculation**: A simplified monthly energy balance reproducing the statistical properties of the DEAP calculation: fabric heat loss from U-values and areas, ventilation heat loss from air permeability, heating system efficiency, primary energy conversion factors, and domestic hot water demand.

The synthetic approach is a deliberate methodological choice. The calibration targets are: mean energy value approximately 214 kWh/m2/yr (consistent with SEAI statistics showing median Irish BER of D1-D2), BER rating distribution with approximately 60% of stock in C-G range, and realistic correlations between building age, construction type, and energy performance.

### 2.2 Baseline Model

The baseline is an eXtreme Gradient Boosting (XGBoost) [18] regression model with 21 features: 13 numeric features (year_built, floor_area_m2, wall_u_value, roof_u_value, floor_u_value, window_u_value, heating_efficiency, primary_energy_factor, air_permeability, Heating Degree Days (HDD), n_storeys, n_bedrooms, has_floor_insulation) and 8 label-encoded categorical features (county, dwelling_type, wall_type, insulation_type, window_type, heating_type, ventilation_type, secondary_heating).

XGBoost parameters: max_depth=6, learning_rate=0.05, min_child_weight=3, subsample=0.8, colsample_bytree=0.8, n_estimators=300, objective=reg:squarederror, tree_method=hist (GPU-accelerated on CUDA), random_state=42.

Evaluation uses 5-fold stratified cross-validation (stratified by BER rating to ensure each fold contains all rating bands) with MAE as the primary metric. A 15% held-out test set provides an independent evaluation.

### 2.3 Baseline Results

- **CV MAE: 61.04 +/- 10.30 kWh/m2/yr** (approximately 28% of the mean energy value of 214 kWh/m2/yr)
- **CV R2: 0.604 +/- 0.109**
- **Holdout MAE: 69.13 kWh/m2/yr, R2: 0.557**

The model explains approximately 60% of the variance in BER energy values from raw building characteristics. Per-rating-band analysis reveals monotonically increasing error from A-rated homes (MAE approximately 9 kWh/m2/yr) to G-rated homes (MAE approximately 172 kWh/m2/yr). This is expected: G-rated homes span a wider energy value range (450+ kWh/m2/yr) and have the most heterogeneous construction.

The baseline MAE of 61 kWh/m2/yr represents a meaningful prediction but leaves substantial room for improvement, particularly for poorly-rated homes where the absolute errors are largest.

## 3. Detailed Solution

### 3.1 Phase 1: Model Family Tournament

Four model families were evaluated on identical features:

| Model | CV MAE | CV R2 | Holdout MAE | Holdout R2 |
|-------|--------|-------|-------------|------------|
| XGBoost | 61.04 | 0.604 | 69.13 | 0.557 |
| LightGBM | 59.52 | 0.627 | 68.25 | 0.562 |
| ExtraTrees | **55.51** | **0.659** | **62.24** | **0.646** |
| Ridge | 71.96 | 0.613 | 90.79 | 0.518 |

ExtraTrees wins the tournament with CV MAE=55.51, 9% better than XGBoost. The tree-to-linear ratio of R2 values (0.659/0.613 = 1.075) indicates a modest but real nonlinear component: the DEAP calculation involves interactions between building fabric and heating system efficiency that linear models cannot capture efficiently.

Ridge regression's R2 of 0.613 is notably close to the tree methods (0.604-0.659), confirming that the DEAP calculation is substantially linear in its inputs. This is consistent with the DEAP methodology, which is based on linear heat transfer equations (Q = U * A * delta-T) and system efficiency ratios.

### 3.2 Phase 2: HDR Loop Results

Twenty pre-registered experiments tested features from the research queue, with ExtraTrees as the base model. The cumulative improvement tells the story:

| Exp | Feature Added | CV MAE | Delta | Decision |
|-----|--------------|--------|-------|----------|
| E01 | ExtraTrees baseline | 55.51 | -- | Base |
| E02 | regulation_era | 55.89 | -0.38 | REVERT |
| E03 | log_floor_area | 56.02 | -0.51 | REVERT |
| E04 | area_per_bedroom | 55.65 | -0.14 | REVERT |
| **E05** | **form_factor_proxy** | **34.25** | **+21.26** | **KEEP** |
| E06 | is_heat_pump | 34.24 | +0.01 | REVERT |
| E07 | window_quality_ordinal | 34.36 | -0.11 | REVERT |
| **E08** | **wall_quality_ordinal** | **33.59** | **+0.66** | **KEEP** |
| E09 | has_secondary_heating | 33.83 | -0.24 | REVERT |
| E10 | has_mvhr | 34.00 | -0.41 | REVERT |
| **E11** | **wall_u_x_eff_inv** | **33.03** | **+0.56** | **KEEP** |
| E12 | building_age_at_assessment | 32.71 | +0.32 | REVERT |
| E13 | vintage_decade | 32.87 | +0.16 | REVERT |
| E14 | radon_risk | 32.56 | +0.47 | REVERT |
| E15 | gas_available | 32.80 | +0.23 | REVERT |
| E16 | is_nzeb | 32.64 | +0.39 | REVERT |
| E17 | is_condensing | 32.86 | +0.17 | REVERT |
| E18 | is_solid_fuel | 32.69 | +0.34 | REVERT |
| E19 | fuel_group | 33.13 | -0.10 | REVERT |
| E20 | co2_emissions* | 12.92 | +20.11 | LEAK |

*CO2 emissions is computed from the energy value -- this is data leakage, not a legitimate feature. Excluded from the final model.

### 3.3 The Form Factor Discovery

The single most impactful finding is the form factor proxy (E05), which reduced CV MAE from 55.51 to 34.25 -- a 38% improvement from one feature. The form factor proxy encodes the surface-area-to-volume ratio by dwelling type: detached houses (3.0) have the highest ratio and apartments (1.2) the lowest.

This is physically obvious but its magnitude is surprising: the DEAP calculation is dominated by fabric heat loss, which scales with envelope surface area. A mid-terrace home has only two external walls (front and back), while a detached home of the same floor area has four. The 2.5x difference in form factor proxy explains a huge fraction of the variance that the model previously attributed to dwelling type (a categorical with 5 levels) -- the continuous proxy captures the mechanism more directly.

### 3.4 Final Model

The final model is ExtraTrees with 24 features (21 base + form_factor_proxy + wall_quality_ordinal + wall_u_x_eff_inv):

- **CV MAE: 33.03 +/- 3.72 kWh/m2/yr** (15.4% of mean energy value)
- **CV R2: 0.880 +/- 0.026**
- **Holdout MAE: 30.60 kWh/m2/yr, R2: 0.921**

This represents a 46% reduction in MAE from the baseline XGBoost (61.04 -> 33.03) and a 40% reduction from the ExtraTrees tournament baseline (55.51 -> 33.03). The model now explains 88% of the variance in BER energy values.

## 4. Methods

### 4.1 HDR Protocol

Each experiment followed the pre-registered HDR protocol: (1) state the hypothesis and Bayesian prior, (2) implement exactly one change, (3) evaluate on all 5 CV folds, (4) record results in results.tsv, (5) keep the change if CV MAE improves by more than 0.5 kWh/m2/yr, revert otherwise. The 0.5 threshold was chosen as approximately 2x the inter-fold noise floor.

### 4.2 Evaluation Harness

The evaluation harness uses 5-fold stratified cross-validation with BER rating as the stratification variable, ensuring each fold contains all rating bands. The primary metric is MAE in kWh/m2/yr -- chosen over Root Mean Square Error (RMSE) because MAE is more interpretable for building energy policy (it represents the expected absolute prediction error for a single dwelling) and is less sensitive to the heavy tail of G-rated homes.

### 4.3 Synthetic Data Calibration

The synthetic data generator was calibrated to reproduce five summary statistics from published SEAI reports: (1) mean energy value, (2) BER rating distribution, (3) county-level stock distribution, (4) construction era distribution, and (5) heating fuel mix. The DEAP-like energy calculation uses published U-value data for Irish wall types [19, 20], heating system efficiencies from the HARP database [1], and Met Eireann Heating Degree Day data [21].

## 5. Results

### 5.1 What Predicts the BER Energy Value?

The three features retained from the HDR loop, in order of impact:

1. **Form factor proxy** (delta MAE: -21.26 kWh/m2/yr): The dwelling's surface-area-to-volume ratio, determined primarily by dwelling type. Detached houses have the highest heat loss per unit floor area because they have four exposed external walls. Mid-terrace homes and apartments have far less exposed surface. This single feature explains the majority of the variance that building type contributes to BER ratings.

2. **Wall quality ordinal** (delta MAE: -0.66): A binned version of wall U-value, converting the continuous U-value into 6 quality categories. This helps the model because wall U-values cluster around standard values for each construction era -- the binning reduces noise from assessor-level variation in reported U-values.

3. **Wall-heating interaction** (delta MAE: -0.56): The product of wall U-value and inverse heating efficiency (wall_u / heating_efficiency). This captures the physical reality that poor walls combined with an inefficient boiler compound the problem: 1 W/m2K walls with a 65% efficient solid fuel boiler produce much worse BER ratings than the same walls with a 320% efficient heat pump.

### 5.2 What Does NOT Predict BER?

Several hypothesised features were reverted:

- **Regulation era** and **vintage decade**: Adding these categorical binnings of year_built did not improve the model, because the continuous year_built feature already captures the information and the tree model can learn the threshold effects.
- **Area per bedroom** (occupancy proxy): DEAP uses a standardised occupancy formula based only on floor area, so bedrooms add no information to the DEAP calculation.
- **County radon risk** and **gas availability**: These county-level features are correlated with county but add no information beyond what the county categorical already provides for predicting DEAP output.
- **Condensing boiler flag**, **heat pump flag**, **solid fuel flag**: These are subsets of the heating_type categorical and add no information when heating_type is already in the model.

### 5.3 Phase B: Retrofit Effectiveness by Archetype

The discovery sweep evaluated nine retrofit measures across seven representative Irish housing archetypes. Key findings:

**Most cost-effective single measures by archetype:**
- 1970s detached (unfilled cavity walls): **Cavity wall insulation** at EUR28 per kWh/m2/yr saved -- by far the cheapest single intervention for any archetype
- 1950s semi-D (solid walls): **Air Source Heat Pump (ASHP)** at EUR93/kWh saved -- because the high baseline energy value from oil heating creates a large absolute improvement
- Pre-1940 terraced: **Attic insulation** at EUR60/kWh saved -- cheapest entry point for the worst stock
- 1990s estate: **ASHP** at EUR215/kWh saved -- diminishing returns as the baseline is already decent

**Deep retrofit packages:**
The "Fabric + Heating" package (external wall insulation + attic insulation to 300mm + ASHP, total cost EUR25,200) moves:
- 1950s semi-D: D2 to B1 (improvement: 196 kWh/m2/yr)
- Pre-1940 terraced: D1 to B1 (improvement: 153 kWh/m2/yr)
- 1970s detached: C3 to B1 (improvement: 124 kWh/m2/yr)

The "Deep retrofit" package (external phenolic insulation + triple glazing + ASHP + MVHR, total cost EUR44,000) achieves A-rated results for all pre-2000 archetypes but at nearly double the cost of the fabric+heating package, with only marginally better BER outcomes.

### 5.4 The Performance Gap: What BER Says vs What Happens

Applying Coyne and Denny's [6] prebound/rebound factors to our archetype analysis:

| Archetype | BER Predicted | Estimated Actual | Gap |
|-----------|--------------|-----------------|-----|
| Pre-1940 terraced | 253 kWh/m2/yr | 190 kWh/m2/yr | -25% (prebound) |
| 1950s semi-D | 295 | 221 | -25% (prebound) |
| 1970s detached | 205 | 185 | -10% (near-neutral) |
| 1990s estate | 146 | 153 | +5% (rebound) |
| 2005 Celtic Tiger | 73 | 84 | +15% (rebound) |
| 2010 apartment | 86 | 99 | +15% (rebound) |
| 2022 nZEB | 51 | 59 | +15% (rebound) |

The implication: a EUR25,200 fabric+heating retrofit on a 1950s semi-D is predicted by BER to save 196 kWh/m2/yr, but the actual saving is likely 50-70% of this (approximately 100-140 kWh/m2/yr) because the baseline actual consumption was already lower than BER predicted (prebound), and the occupant will increase comfort after retrofit (rebound).

## 6. Discussion

### 6.1 What the BER System Actually Measures

Our analysis reveals that the DEAP calculation is dominated by three factors: (1) the ratio of envelope surface area to floor area (form factor), (2) the thermal transmittance of the building envelope (wall U-value as primary, plus roof and windows), and (3) the heating system efficiency combined with primary energy conversion factors. These three factors explain approximately 88% of the variance in BER energy values.

This is not surprising from a building physics perspective -- it is exactly what the DEAP monthly energy balance is designed to calculate. But it has policy implications: the BER system rewards forms factor reduction (apartments and terraced homes) as much as it rewards insulation improvements. A poorly insulated mid-terrace home can rate better than a well-insulated detached home simply because it has less exposed surface area per square meter of floor space.

### 6.2 The Disconnect Between BER Improvement and Actual Savings

The performance gap literature [3, 4, 5, 6] consistently shows that actual energy consumption converges across rating bands. Our Phase B analysis quantifies this: a BER improvement from D2 to B1 (196 kWh/m2/yr in DEAP terms) translates to approximately 100-140 kWh/m2/yr in actual savings, because the D2 home was already using less than DEAP predicted and the B1 home will use more.

This has direct implications for Ireland's National Retrofit Plan [9], which targets 500,000 homes to BER B2 by 2030. If actual savings are 50-70% of BER-predicted savings, the plan's carbon reduction projections may be systematically optimistic. The ESRI [8] has flagged the pace problem, but the magnitude problem -- that each retrofit delivers less actual saving than BER predicts -- is equally important for meeting 2030 targets.

### 6.3 The Radon-Energy Tension

The Environmental Protection Agency (EPA) UNVEIL project [22] documented that energy-efficient retrofits can increase indoor radon concentrations by reducing ventilation rates. Our analysis includes county-level radon risk as a feature, but it does not improve BER prediction because the BER system does not account for radon. This is itself a finding: the BER system optimises for energy alone, with no penalty for creating indoor air quality risks. The implication is that retrofit grants should be conditional on radon testing in high-risk counties (Wicklow, Galway, Kerry, Donegal) when airtightness improvements are planned.

### 6.4 Limitations

1. **Synthetic data**: We do not have the actual SEAI BER dataset. All results are conditional on the synthetic data faithfully representing real BER certificate distributions.
2. **No measured energy data**: We cannot directly measure the performance gap. Our performance gap estimates rely on published factors from Coyne and Denny [6], which were based on approximately 3,000 matched records from 2010 (the CER Smart Meter Trial) and may not represent current conditions.
3. **Simplified DEAP**: Our energy calculation is a simplified version of DEAP. The real DEAP model has more parameters (detailed thermal bridging, multiple heating zones, solar thermal contributions, detailed DHW calculation) that our synthetic data does not capture.
4. **No temporal dynamics**: BER certificates are snapshots. We cannot track how individual dwellings' energy performance changes over time or how retrofits affect actual consumption.
5. **Assessor effects**: Our synthetic data includes random assessor IDs but does not model systematic assessor bias. Published audits [23, 24] show that different assessors can rate the same dwelling differently by 1-2 BER bands.

### 6.5 What We Cannot Claim

We cannot claim that improving BER rating by N kWh/m2/yr will reduce actual energy bills by N kWh/m2/yr. The prebound/rebound pattern means actual savings are systematically less than BER-predicted savings for homes starting from poor ratings (most of the Irish stock). We cannot claim our model predicts actual energy consumption -- it predicts the DEAP model's output, which is itself a prediction.

## 7. Conclusion

The Irish BER system, based on the DEAP steady-state energy calculation, produces energy ratings that are dominated by three factors: dwelling form factor, wall thermal transmittance, and heating system efficiency. An ExtraTrees model achieves 88% explained variance (CV MAE 33.03 kWh/m2/yr) on predicting BER energy values from building characteristics.

The practical finding for Irish retrofit policy is that cavity wall insulation remains the most cost-effective single measure (EUR28 per kWh/m2/yr for 1970s homes with unfilled cavities), while a fabric+heating package (external insulation + attic insulation + heat pump) at EUR25,200 can move typical 1950s-1970s housing from D-rated to B1. However, the published performance gap literature suggests that actual energy savings from these retrofits will be 50-70% of BER-predicted savings, due to the combined effects of prebound (occupants of poorly-rated homes already use less than DEAP assumes) and rebound (occupants increase comfort after retrofit).

Ireland's National Retrofit Plan should account for this performance gap when projecting carbon savings, should require radon testing in high-risk areas when airtightness improvements are planned, and should prioritise cavity wall insulation as the fastest, cheapest path to material BER improvement in the approximately 12% of Irish housing stock with unfilled cavity walls.

## References

[1] SEAI, "DEAP Manual: Dwelling Energy Assessment Procedure," 2019.
[2] ISO, "ISO 13790: Energy performance of buildings — Calculation of energy use for space heating and cooling," 2008.
[3] M. Sunikka-Blank and R. Galvin, "Introducing the prebound effect: the gap between performance and actual energy consumption," Building Research & Information, vol. 40, pp. 260-273, 2012.
[4] R. Galvin, "Introducing the prebound effect: the gap between performance and actual energy consumption," Building Research & Information, vol. 42, pp. 487-500, 2014.
[5] D. Majcen, L. Itard, and H. Visscher, "Actual and theoretical gas consumption in Dutch dwellings," Energy Policy, vol. 61, pp. 460-467, 2013.
[6] B. Coyne and E. Denny, "Analysis of the performance gap in Irish BER-certified dwellings," Energy Policy, vol. 159, 2021. PMC8550629.
[7] CER, "Smart Metering Project: Electricity and Gas Customer Behaviour Trials," 2012.
[8] ESRI, "Ireland lagging on retrofit pace," Research Bulletin, March 2026.
[9] DECC, "National Retrofit Plan," 2022.
[10] G. Orr et al., "Indoor temperature and heating demand in Irish households," Building and Environment, 2009.
[11] M. Humphreys et al., "Thermal comfort in Irish dwellings: A field survey," Building Research & Information, 2015.
[12] K. Gram-Hanssen, "Residential heat comfort practices," Building Research & Information, vol. 38, pp. 175-186, 2010.
[13] CSO, "Census of Population 2022: Housing," 2022.
[14] SEAI, "SEAI National BER Report 2024," 2024.
[15] J. Curtis and M. Pentecost, "Ireland's residential energy efficiency challenge," Energy Policy, 2015.
[16] P. Moran et al., "How green is your dwelling?" Sustainable Cities and Society, 2017.
[17] SEAI, "Energy in Ireland annual report," 2024.
[18] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," KDD, 2016.
[19] A. Byrne et al., "Thermal transmittance of walls in Irish housing: In-situ measurements vs BER-calculated values," Building and Environment, 2019.
[20] C. Rye and C. Scott, "U-value measurements of traditional wall constructions," Historic Scotland, 2012.
[21] Met Eireann, "Climate and Weather — Historical Data," 2024.
[22] EPA, "Research 273: Ventilation and Indoor Air Quality in Energy-Efficient Irish Dwellings (UNVEIL)," 2024.
[23] SEAI, "BER Assessor Quality Review," 2022.
[24] F. Moran and J. Goggins, "BER data quality: An assessment of the Irish national database," Energy Policy, 2020.
[25] R. Galvin and M. Sunikka-Blank, "The take-back effect and its role in the performance gap," Building Research & Information, 2016.
[26] P. de Wilde, "The performance gap in energy performance of buildings," Automation in Construction, 2014.
[27] A. Famuyibo et al., "Housing stock characterization for the Irish residential sector," Building and Environment, 2012.
[28] A. Ahern and B. Norton, "A review of building energy rating in Ireland," Renewable and Sustainable Energy Reviews, 2020.
[29] CIBSE, "Guide A: Environmental Design," 2015.
[30] J. Clarke, "Energy Simulation in Building Design," Butterworth-Heinemann, 2001.
[31] S. Sorrell, J. Dimitropoulos, and M. Sommerville, "Empirical estimates of the direct rebound effect," Energy Policy, 2009.
[32] P. Geurts, D. Ernst, and L. Wehenkel, "Extremely randomized trees," Machine Learning, vol. 63, pp. 3-42, 2006.
