# Literature Review — Iberian Wildfire VLF Prediction

## 1. Domain Fundamentals: Fire Behavior Physics

Wildfire behavior is governed by the fire environment triangle: fuels, weather, and topography (Pyne 1996; Scott et al. 2005). The Rothermel (1972) fire spread model remains the physical foundation, expressing spread rate as a function of fuel bed properties, wind speed, and slope. Crown fire initiation follows Van Wagner's (1977) criteria, requiring sufficient surface fire intensity to ignite the canopy — a threshold transition that parallels our VLF question. The fire size distribution follows a power law (Malamud et al. 1998; Cumming 2001), with the tail containing very large fires (VLFs) that represent ~2-3% of events but ~80% of burned area (Tedim et al. 2018).

The Canadian Forest Fire Weather Index (FWI) system, codified by Van Wagner (1987), is the operational standard for fire danger rating across the European Union via EFFIS (European Forest Fire Information System). The system computes six components from noon temperature, relative humidity, wind speed, and 24-hour precipitation: the Fine Fuel Moisture Code (FFMC) for dead surface fuel moisture, the Duff Moisture Code (DMC) for loosely compacted organic layers, the Drought Code (DC) for deep organic layers, the Initial Spread Index (ISI) combining FFMC and wind, the Build-Up Index (BUI) combining DMC and DC, and the composite FWI. A critical limitation is that the FWI system was developed for Canadian boreal forests and does not include live fuel moisture content (LFMC), a quantity that is particularly important in Mediterranean evergreen vegetation where live fuels constitute a much larger fraction of the fire environment than in boreal deciduous-conifer systems.

Eruptive fire behavior — the sudden transition from a manageable fire to an uncontrollable conflagration — is a separate phenomenon documented by Viegas and Simeoni (2011). It occurs under specific topographic and meteorological conditions (canyon terrain, wind shifts, slope-wind alignment) and can produce fire intensity jumps of an order of magnitude within minutes. This stochastic nature means that even a perfect predictor of VLF transition would have an inherent uncertainty floor.

## 2. Phenomena of Interest: VLF Transition and Mediterranean Fire Ecology

The very large fire (VLF) transition — the shift from an ordinary wildfire to one exceeding 500 ha — is not simply a function of fire weather severity. Tedim et al. (2018) argued that VLFs emerge from the intersection of extreme weather, accumulated fuel, and suppression failure. Stephens et al. (2014) proposed a typology of extreme fire events distinguishing between weather-driven fires (wind storms), fuel-driven fires (drought-accumulated dead fuel), and plume-dominated fires (pyroconvection generating their own weather).

Mediterranean fire ecology has several distinctive features (Pausas 2004; Moreno and Oechel 2012). Fire-adapted vegetation (e.g., Cistus, Quercus suber) has evolved regeneration strategies, but non-native eucalyptus (Eucalyptus globulus) — introduced to Portugal at industrial scale — burns at approximately 2.5 times the rate of native broadleaf forest (Fernandes et al. 2016; Silva et al. 2019; Catarino et al. 2021). The 2017 Pedrogao Grande fire in central Portugal, which killed 66 people, occurred primarily in eucalyptus-pine mixed stands under extreme fire weather (Viegas et al. 2019; Guerreiro et al. 2018). The August 2025 NW Iberia cluster of 22 simultaneous VLFs further underscored the role of eucalyptus monoculture in fire regime intensification.

Fire regimes in the Iberian Peninsula have undergone significant change over the past century. Turco et al. (2016) documented a century-scale decline in fire frequency offset by an increase in fire severity and VLF occurrence. Land abandonment in southern Europe has allowed fuel accumulation in formerly managed landscapes (Koutsias et al. 2012; Moreira et al. 2011), while climate change is extending the fire season and increasing fire weather severity (Turco et al. 2018, 2023; Bedia et al. 2015).

## 3. Candidate Features: From Theory to Computable Proxies

The bridge from fire science theory to machine learning features requires mapping physical quantities to remotely sensed or reanalysis-derived proxies. The key candidate features fall into five categories:

**Fire weather** (from ERA5 reanalysis): temperature, humidity, wind speed, precipitation, and the Van Wagner FWI components. These capture instantaneous atmospheric conditions. Bedia et al. (2014) validated the FWI system for Mediterranean conditions, finding it useful but with calibration offsets relative to Canadian boreal conditions. Viegas et al. (2004) specifically evaluated FWI performance for Portugal, finding good correlations with fire occurrence but weaker performance for fire size prediction.

**Live fuel moisture** (from Sentinel-2 SWIR): LFMC is the water content of living vegetation, expressed as a percentage of dry weight. Yebra et al. (2013, 2019, 2024) developed and validated satellite-based LFMC estimation, showing that Sentinel-2 SWIR bands can estimate LFMC with R-squared values of 0.6-0.7. Jolly et al. (2015) demonstrated that fuel moisture influences fire weather globally more than temperature alone. Resco de Dios et al. (2015) showed that extreme fire events in Mediterranean ecosystems are consistently preceded by low LFMC. Dennison et al. (2008) identified critical LFMC thresholds: below 80% increases fire risk significantly, below 60% represents critical danger.

**Drought severity** (from SPEIbase): the Standardised Precipitation-Evapotranspiration Index (SPEI) at multiple timescales (Vicente-Serrano et al. 2010; Begueria et al. 2014) captures cumulative moisture deficit. Turco et al. (2017) showed that SPEI at the 6-month timescale is the most predictive drought indicator for fire in the Mediterranean, capturing the pre-fire-season preparation period when fuels accumulate.

**Terrain** (from EU-DEM): elevation, slope, and aspect affect fire spread through uphill acceleration, solar exposure, and wind channeling (Viegas 2004; Dillon et al. 2011). Slope is the most important terrain variable: fire spread rate approximately doubles per 10 degrees of slope increase.

**Vegetation and land cover** (from CORINE/Sentinel-2): fuel type determines fire behavior. Pre-fire NDVI (Normalized Difference Vegetation Index) captures vegetation greenness and biomass availability (Chuvieco et al. 2014).

## 4. Machine Learning for Wildfire Prediction

Machine learning has been applied to wildfire prediction at multiple scales. Jain et al. (2020) reviewed ML approaches for fire prediction, noting that gradient-boosted trees (XGBoost, LightGBM) dominate recent work due to their ability to handle mixed feature types and class imbalance. Rodrigues et al. (2019) specifically applied ML to VLF prediction in Spain, using Random Forest on EFFIS data and achieving AUC 0.72-0.76. Leuenberger et al. (2018) applied Random Forest to fire danger estimation in Switzerland. Bergonse et al. (2021) mapped fire susceptibility in Portugal using ensemble methods.

A critical methodological concern is class imbalance: VLFs represent only 2-3% of all fires. Standard approaches include class weighting (scale_pos_weight in XGBoost), SMOTE oversampling (Chawla et al. 2002), and threshold optimization. He and Ma (2013) showed that gradient boosting is generally robust to moderate imbalance but can still overfit in the tail.

Temporal cross-validation is essential for fire prediction (Bergmeir and Benitez 2012). Random shuffled CV would allow information leakage from future fire seasons into training, inflating AUC estimates. Our protocol trains on all years before the validation year, testing on the next year(s), with 2025 as the final holdout.

The finding that Ridge (logistic regression) outperforms tree-based models in our study (CV AUC 0.699 vs XGBoost 0.654) is consistent with Podschwit and Cullen (2020) and with the general principle that linear models can outperform complex models when (a) the feature space is already informative, (b) the sample size is moderate, and (c) the positive class is rare.

## 5. Feature Engineering for Fire Risk

Feature engineering in fire science draws on two traditions: the fire weather index tradition (Van Wagner 1987; Dowdy et al. 2018) and the remote sensing tradition (Chuvieco et al. 2004; Giglio et al. 2018). The fire weather approach computes indices from meteorological data, while the remote sensing approach directly measures fuel state from satellite imagery.

The vapor pressure deficit (VPD) has emerged as a competitive fire predictor (Seager et al. 2015; Williams et al. 2013), defined as the difference between the saturation vapor pressure at the current temperature and the actual vapor pressure. VPD captures the atmospheric drying demand on vegetation and has been shown to outperform temperature alone for fire prediction in some systems. However, our experiments found that VPD adds no information beyond raw temperature and relative humidity, suggesting that the tree-based models implicitly capture the VPD relationship from its constituent variables.

Night-time temperature has recently been identified as important for fire activity (Balch et al. 2022), as warm nights prevent overnight humidity recovery and keep fuel moisture low. Compound drought-heatwave events produce disproportionately more fire than either drought or heatwave alone (Feng et al. 2022; Ruffault et al. 2020).

## 6. Transfer and Generalization

Fire models developed in one region may not transfer to another due to differences in fuel type, climate, suppression capacity, and ignition patterns. Bedia et al. (2015, 2018) projected fire weather changes across Europe under climate scenarios, showing that Mediterranean fire risk is expected to increase while Northern European risk may increase or decrease depending on the moisture balance.

The Iberian Peninsula is often treated as a single fire regime but contains significant internal diversity: the Atlantic northwest (high rainfall, eucalyptus plantations), the Mediterranean east (dry summers, pine forests), the continental interior (cold winters, oak woodlands), and the semi-arid south (Algarve, Andalusia). Country-level differences between Portugal and Spain reflect both ecological and institutional factors: Portugal has higher per-capita burned area due to eucalyptus expansion, smaller landholdings, and different suppression philosophies (Fernandes et al. 2019).

California fire prediction (Kolden and Abatzoglou 2018) and Australian fire weather (Dowdy 2018; Clarke and Evans 2019) provide cross-domain validation: the same physical drivers (fuel dryness, wind, drought) operate in all Mediterranean-climate fire systems, but the relative importance varies with vegetation type and fire regime.

## 7. Related Problems: Operational Fire Management

Fire suppression resource allocation (Gebert et al. 2007; Donovan and Rideout 2003; Thompson et al. 2011) connects VLF prediction to decision-making. If a model can predict VLF probability at the time of fire detection, it can inform triage decisions: allocate heavy resources early to fires with high VLF probability rather than waiting for fires to prove they are growing. Thompson et al. (2017) documented that multiple simultaneous fires overwhelm suppression capacity, creating a cascading failure mode that is distinct from the weather-driven VLF transition.

Prescribed burning (Fernandes and Botelho 2003; Fernandes et al. 2013) and fuel break construction (Agee et al. 2000; Alcasena et al. 2015) are the primary prevention tools. Their cost-effectiveness depends on targeting: treating the highest-risk municipalities identified by VLF prediction models could achieve more risk reduction per euro than untargeted landscape-scale treatment. The Pareto analysis in Phase B of this study estimates the cost-risk tradeoff for the top 10 municipalities at highest VLF risk.
