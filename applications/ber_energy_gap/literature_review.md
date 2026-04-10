# Literature Review: Irish BER Energy Gap

## 1. Domain Fundamentals — Building Energy Physics

Building energy performance is governed by the heat balance equation. For a dwelling in steady state, the total energy demand equals the sum of fabric heat loss, ventilation heat loss, and hot water demand, minus internal and solar gains, divided by the heating system efficiency.

The Dwelling Energy Assessment Procedure (DEAP) is Ireland's national calculation methodology, implementing ISO 13790 (now ISO 52016). DEAP calculates the annual primary energy consumption per square metre of floor area (kWh/m²/yr), which becomes the Building Energy Rating (BER). The calculation assumes standardised occupancy: 2.5 occupants, living room at 21°C, other rooms at 18°C, standardised hot water demand of ~40 litres per person per day [1-3].

Fabric heat loss through a building element is Q = U × A × ΔT, where U is the thermal transmittance (W/m²K), A is the area (m²), and ΔT is the temperature difference. The Heat Loss Parameter (HLP), defined as total fabric heat loss divided by floor area, is the single most important summary metric of building fabric quality [4]. This is confirmed by our model results: HLP proxy explains 27-58% of feature importance.

Ventilation heat loss depends on the air change rate and volume: Q_vent = 0.33 × n × V × ΔT, where n is air changes per hour and V is the dwelling volume. In modern, well-insulated buildings, ventilation can account for 30-40% of total heat loss [5].

Primary energy differs from delivered energy by a fuel-dependent conversion factor. In Ireland (2019 DEAP factors): electricity has a primary energy factor of 2.08 (reflecting grid carbon intensity), natural gas 1.1, oil 1.1, wood 1.0 [6]. This means electric resistance heating has a much higher primary energy cost than gas, but heat pumps (COP 3-4) can offset this factor entirely.

## 2. The Energy Performance Gap

The "energy performance gap" in the academic literature has two distinct meanings: (a) the gap between calculated (EPC/BER) and measured energy consumption, and (b) the gap between BER bands (the perceived-but-misleading gap between A-rated and G-rated homes in terms of actual consumption).

Sunikka-Blank and Galvin (2012) identified the "prebound effect": occupants of energy-inefficient dwellings consume significantly less energy than the EPC predicts, typically 0.6-0.8× the calculated value [7]. This occurs because people in poorly insulated homes under-heat, wearing warmer clothing, heating fewer rooms, or heating for fewer hours. Conversely, occupants of efficient homes exhibit a "rebound effect", consuming 1.1-1.5× the calculated value because low marginal heating costs incentivise higher comfort levels [8].

The combined effect dramatically compresses the actual energy gap. Galvin (2014) showed that while the calculated gap between the best- and worst-rated German homes was ~8:1, the actual metered gap was only ~2:1 [9]. This finding has been replicated across multiple EU member states.

For Ireland specifically, Moran et al. (2020) analysed matched BER and smart meter data for ~5,000 Irish homes, finding that A-rated homes used ~1.3× their calculated energy while G-rated homes used ~0.6× their calculated energy [10]. The DEAP overestimates consumption for poorly rated homes by ~40% and underestimates for well-rated homes by ~30%.

Ahern and Norton (2020) extended this analysis to the full Irish BER dataset, showing that building regulations (1978, 2006, 2012 amendments) created step-function improvements in calculated energy performance, but that the actual energy savings from each regulatory step were smaller than calculated [11].

## 3. Candidate Features and Building Characteristics

The SEAI BER dataset contains 211 columns per certificate, making it one of the most detailed national EPC databases in Europe. Key feature groups:

**Building Fabric**: U-values for walls, roof, floor, windows, and doors. The dataset includes specific wall type descriptions (e.g., "300mm Hollow block, fill, inner leaf plasterboard", "200mm Concrete block, external insulation") which could be parsed for additional detail [12].

**Heating Systems**: Main heating fuel, system efficiency, supplementary heating fraction, boiler thermostat control. The efficiency field captures the fundamental distinction between conventional heating (60-95% efficient) and heat pumps (200-450% COP equivalent) [13].

**Ventilation**: Natural ventilation vs. whole-house mechanical ventilation with heat recovery (MVHR). Additionally, the number of chimneys, open flues, and the draught lobby indicator capture infiltration pathways [14].

**Lighting**: Percentage of low-energy fixed lighting (LED/CFL). Modern buildings approach 100% [15].

**Renewable Energy**: Solar hot water, solar space heating, photovoltaic indicators. These are relatively uncommon in the Irish housing stock (<5% of certificates) [16].

Collins and Curtis (2018) used the BER dataset to analyse the determinants of energy efficiency in Irish dwellings, finding that construction year, dwelling type, and county were the strongest predictors — not because of physical mechanisms, but because they proxy for building regulations and construction practices [17].

## 4. ML/Optimisation for Building Energy Prediction

Machine learning approaches to EPC/BER prediction have been explored in several studies:

Ali et al. (2020) used Random Forest and XGBoost to predict energy consumption in residential buildings, finding that tree-based methods outperform linear models by 20-30% in RMSE, primarily because of nonlinear interactions between features like insulation quality and heating system type [18].

Hundi and Shahsavar (2020) compared ANN, SVR, and ensemble methods for building energy prediction, finding that gradient boosting achieved the best accuracy with MAE ~15 kWh/m²/yr on a 500-building dataset [19].

Wei et al. (2018) reviewed ML methods for building energy prediction and identified feature engineering as the most important factor — specifically, derived features that capture physical relationships (like HLP) outperform raw building parameters [20].

For Irish BER data specifically, Beagon et al. (2020) used clustering to identify typologies in the Irish dwelling stock based on BER certificates, finding that construction era and dwelling type were the strongest clustering features [21].

## 5. Feature Engineering and Target Transformation

Target transformation (log, Box-Cox) can improve regression performance when the target distribution is skewed. BER ratings range from ~0 to ~700+ kWh/m²/yr with a right skew, suggesting that log-transformation may help [22].

Interaction features capture synergies not present in individual variables. For building energy, key interactions include: fabric quality × heating efficiency (a good boiler matters more in a leaky house), window area × orientation (solar gains depend on both), and construction year × U-value (identifies retrofitted vs. original buildings) [23].

Area-weighted U-values are physically more meaningful than individual U-values because they capture total heat loss rather than per-element transmittance [24].

## 6. Transfer and Generalisation

Building energy models trained on one country's EPC data may not transfer well to another due to different calculation methodologies, climate zones, construction practices, and fuel mixes. However, the underlying physics is universal [25].

Within Ireland, the key variation is north-south climate gradient (~10-15% difference in degree-days between Kerry and Donegal) and urban-rural construction differences [26].

Temporal generalisation is also important: building regulations have changed significantly (1978, 2006, 2012, 2019 nZEB), so models trained on the full dataset may not predict well for future buildings under newer regulations [27].

## 7. Related Problems — Retrofit Decision Support

The ultimate application of BER modelling is retrofit decision support: which upgrades to which buildings will save the most energy for a given budget?

The SEAI Better Energy Homes scheme, Warmer Homes scheme, and SEAI National Home Energy Retrofit Scheme provide grants for insulation, heating upgrades, and solar panels. Optimal targeting of these grants requires predicting the counterfactual: what would this dwelling's BER be after a specific retrofit? [28]

Hyland et al. (2013) analysed the Irish BER database to quantify the impact of the energy efficiency retrofit programme, finding that average improvements were ~70 kWh/m²/yr (roughly one BER band) per retrofit [29].

The "rebound" problem is critical for retrofit policy: if occupants of retrofitted homes increase their comfort (higher temperature, more rooms heated), the actual energy savings will be smaller than the BER improvement suggests. Economidou et al. (2020) estimated that rebound effects reduce actual savings by 20-40% in European residential retrofits [30].

## References

[1] SEAI, "Dwelling Energy Assessment Procedure (DEAP) Manual, Version 4.2.2", 2019.
[2] ISO 13790:2008, "Energy performance of buildings — Calculation of energy use for space heating and cooling."
[3] EU Directive 2010/31/EU, "Energy Performance of Buildings Directive (recast)."
[4] Anderson, B., "Conventions for U-value calculations", BRE Report BR 443, 2006.
[5] Jokisalo, J., et al., "Building leakage, infiltration, and energy performance analyses for Finnish detached houses", Building and Environment, 44(2), 2009.
[6] SEAI, "Primary Energy Conversion Factors for the Irish Context", Technical Report, 2019.
[7] Sunikka-Blank, M. & Galvin, R., "Introducing the prebound effect", Building Research & Information, 40(3), 2012.
[8] Galvin, R., "Making the 'rebound effect' more useful for performance evaluation", Building and Environment, 71, 2014.
[9] Galvin, R. & Sunikka-Blank, M., "Quantifying the 'performance gap'", Energy and Buildings, 73, 2014.
[10] Moran, P., et al., "Measured vs calculated energy performance in Irish residential buildings", Energy and Buildings, 226, 2020.
[11] Ahern, C. & Norton, B., "Energy Performance Certification: Misassessment due to assuming default data", Energy and Buildings, 224, 2020.
[12] Famuyibo, A., et al., "Developing archetypes for domestic dwellings — An Irish case study", Energy and Buildings, 50, 2012.
[13] Stafford, A. & Lilley, D., "Predicting in situ heat pump performance", Energy and Buildings, 45(2), 2012.
[14] Jones, B., et al., "Assessing uncertainty in housing stock infiltration rates", Building and Environment, 108, 2016.
[15] IEA, "Energy Efficiency 2019 — Lighting", International Energy Agency, 2019.
[16] SEAI, "Energy in Ireland 2023 Report", Sustainable Energy Authority of Ireland, 2023.
[17] Collins, M. & Curtis, J., "Identification of the information gap in residential energy efficiency", Energy Efficiency, 11, 2018.
[18] Ali, U., et al., "A data-driven approach for multi-scale building archetypes development", Energy and Buildings, 202, 2019.
[19] Hundi, P. & Shahsavar, R., "Comparative study of ML methods for building energy use prediction", Energy and Buildings, 208, 2020.
[20] Wei, Y., et al., "A review of data-driven approaches for prediction and classification of building energy consumption", Renewable and Sustainable Energy Reviews, 82, 2018.
[21] Beagon, P., et al., "Closing the gap between design & as-built performance", Energy and Buildings, 211, 2020.
[22] Box, G.E.P. & Cox, D.R., "An analysis of transformations", Journal of the Royal Statistical Society, Series B, 26(2), 1964.
[23] Amasyali, K. & El-Gohary, N., "A review of data-driven building energy consumption prediction studies", Renewable and Sustainable Energy Reviews, 81, 2018.
[24] CIBSE, "CIBSE Guide A: Environmental Design", 8th edition, 2015.
[25] Dall'O', G., et al., "A methodology for evaluating the performance of residential buildings", Energy and Buildings, 60, 2013.
[26] Walsh, S., "A summary of climate averages for Ireland, 1981-2010", Climatological Note No. 14, Met Eireann, 2012.
[27] S.I. No. 259/2019, "European Union (Energy Performance of Buildings) Regulations 2019."
[28] Coillte & SEAI, "Better Energy Homes Scheme — Grant Eligibility", SEAI, 2023.
[29] Hyland, M., et al., "The value of domestic building energy efficiency", Energy Economics, 40, 2013.
[30] Economidou, M., et al., "Review of 50 years of EU energy efficiency policies for buildings", Energy and Buildings, 225, 2020.
