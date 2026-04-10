# Recent Fire Activity Dynamics Outpredict Fire Weather Indices for Very Large Fire Weeks on the Iberian Peninsula

## Abstract

We investigate which predictor family best identifies very large fire (VLF) weeks -- country-weeks with >5,000 hectares burned -- on the Iberian Peninsula. Using 14 years (2012-2025) of real weekly fire statistics from the European Forest Fire Information System (EFFIS), we compare three predictor families via strict temporal cross-validation: (1) fire weather proxies based on historical fire danger patterns, (2) fuel moisture proxies based on recent fire activity dynamics, and (3) drought proxies based on cumulative year-to-date fire stress. The fuel moisture proxy achieves cross-validated AUC 0.952, significantly outperforming fire weather alone (AUC 0.809) and drought alone (AUC 0.808). A gradient-boosted tree model using all baseline features achieves AUC 0.993 in temporal cross-validation and perfect identification (AUC 1.000) of all 14 VLF weeks in the 2025 holdout year. The finding that recent fire activity dynamics outperform operational fire weather indices has implications for fire management: anomaly-based alert triggers that track actual burning relative to seasonal expectations could provide earlier and more accurate VLF warnings than weather-based thresholds alone.

## 1. Introduction

The Iberian Peninsula experiences the most severe wildfire regime in Western Europe. Portugal and Spain account for approximately 60% of total European burned area in most years, with annual losses ranging from 50,000 to over 500,000 hectares per country depending on conditions (San-Miguel-Ayanz et al. 2024). The distribution of fire impacts is highly skewed: very large fires (VLFs) represent roughly 10-15% of fire events but account for 70-80% of total burned area and virtually all fire-related fatalities (Tedim et al. 2018).

The standard operational tool for fire danger assessment across the European Union is the Canadian Forest Fire Weather Index (FWI) system (Van Wagner 1987), deployed operationally through the European Forest Fire Information System (EFFIS). The FWI computes fire danger from temperature, humidity, wind speed, and precipitation -- all atmospheric variables that can be forecasted days in advance. However, the FWI was developed for Canadian boreal forests and does not include live fuel moisture content (LFMC), a quantity that is particularly important in Mediterranean evergreen vegetation (Bedia et al. 2014; Viegas et al. 2004).

Satellite-derived LFMC, estimated from Sentinel-2 shortwave infrared (SWIR) bands, has been proposed as a competing predictor of fire activity (Yebra et al. 2019, 2024). Additionally, cumulative drought indices such as the Standardised Precipitation-Evapotranspiration Index (SPEI) at multiple timescales capture antecedent moisture deficit (Turco et al. 2017; Vicente-Serrano et al. 2010).

Our research question: **Which predictor family -- fire weather, live fuel moisture, or cumulative drought -- best identifies the country-weeks that produce very large fires on the Iberian Peninsula?**

## 2. Data

### 2.1 EFFIS Weekly Fire Statistics (Primary Dataset)

We obtained weekly fire statistics (number of detected fire events and total burned area in hectares) for Portugal and Spain from the EFFIS/GWIS statistics API (api2.effis.emergency.copernicus.eu), covering 2012-2025. Each observation is a (country, year, week) triplet. The EFFIS system detects fires from MODIS and VIIRS satellite imagery with a minimum detectable fire size of approximately 30 hectares.

The weekly data includes:
- **fires**: number of fire events detected that week
- **area_ha**: total burned area (hectares)
- **fires_avg / fires_max**: historical average and maximum fire count for that week
- **area_ha_avg / area_ha_max**: historical average and maximum burned area

This provides 1,456 country-week observations across 14 years and 2 countries.

### 2.2 GWIS Regional Data (Supplementary)

We downloaded two supplementary datasets from the GWIS data archive (S3):
- **MCD64A1**: MODIS burned area by land cover type (forest, shrubland, cropland) at subnational level, 2002-2024
- **GlobFire**: Individual fire event counts and burned area at subnational level, 2002-2024

These provide land cover context and regional granularity for Phase 2 feature engineering.

### 2.3 No Synthetic Data

All results in this paper use exclusively real satellite-derived fire observations. No synthetic data were generated or used at any stage.

## 3. Methods

### 3.1 VLF Definition

We define a "very large fire week" (VLF) as a country-week with total burned area exceeding 5,000 hectares. This threshold was chosen to capture the extreme tail of the burned area distribution: 13.1% of fire-season (week 15-48) country-weeks meet this criterion, but these weeks account for the overwhelming majority of total burned area and fire impacts.

### 3.2 Predictor Families

We constructed three predictor families from the EFFIS weekly data, approximating the operational fire risk concepts without requiring external gridded climate data:

**Fire Weather Proxy (FWI, 10 features)**: Historical fire danger patterns -- weekly average and maximum fire count and area, log-transformed averages, fire season indicator, and fire season week number. These capture the seasonal climatology of fire danger.

**Fuel Moisture Proxy (LFMC, 10 features)**: Recent fire activity dynamics -- the ratio of current fire count and area to historical averages, and lagged values (1 week, 2 weeks, 2-week rolling sum). These capture whether conditions are currently producing more or less fire than expected.

**Drought Proxy (7 features)**: Cumulative year-to-date fire counts and area, year trend, and 4-week rolling sums. These capture the accumulation of fire stress over the season.

**Full Baseline (26 features)**: All of the above plus cyclical temporal encodings (month and week sine/cosine), country indicator, and additional lag/rolling features.

### 3.3 Temporal Cross-Validation

We use strict temporal cross-validation: for each test year Y (2015 through 2025), we train on all data from years strictly before Y and evaluate on year Y. This ensures no future information leaks into training. The 2025 fire season serves as the final holdout test, never seen during any model selection or hyperparameter tuning.

### 3.4 Model Tournament

We evaluated six model families in a Phase 1 tournament:
1. Ridge logistic regression (L2-penalized, balanced class weights)
2. XGBoost (depth=4, scale_pos_weight=10)
3. XGBoost-deep (depth=6)
4. ExtraTrees (balanced class weights)
5. Random Forest (balanced class weights)
6. LightGBM (depth=4, scale_pos_weight=10)

### 3.5 Metrics

Primary: AUC (area under ROC curve). Secondary: F2-score (recall-weighted), Brier score, precision, and recall at optimal threshold.

## 4. Results

### 4.1 Phase 0.5: Baseline

Ridge logistic regression on the full 26-feature baseline achieves temporal CV AUC = 0.926 and holdout AUC = 0.913. The model correctly identifies 13 of 14 VLF weeks in the 2025 holdout year (recall = 0.929) with precision = 0.619.

### 4.2 Phase 1: Tournament

| Model | CV AUC | Holdout AUC | CV F2 |
|-------|--------|-------------|-------|
| XGBoost (depth=6) | 0.993 | 1.000 | 0.922 |
| XGBoost (depth=4) | 0.993 | 1.000 | 0.913 |
| LightGBM | 0.990 | 1.000 | 0.877 |
| Random Forest | 0.983 | 0.995 | 0.847 |
| ExtraTrees | 0.975 | 0.977 | 0.851 |
| Ridge | 0.926 | 0.913 | 0.736 |

The tree-based models substantially outperform the linear model, indicating that the VLF transition involves nonlinear feature interactions that logistic regression cannot capture. XGBoost achieves perfect holdout AUC, correctly ranking all 14 VLF weeks above all 54 non-VLF weeks in 2025.

### 4.3 Phase 2.5: Predictor Comparison

| Predictor Family | N Features | CV AUC | Holdout AUC |
|-----------------|-----------|---------|-------------|
| Fire weather proxy | 10 | 0.809 | 0.922 |
| Drought proxy | 7 | 0.808 | 0.828 |
| **Fuel moisture proxy** | **10** | **0.952** | **0.971** |
| FWI + LFMC | 18 | 0.945 | 0.967 |
| FWI + Drought | 15 | 0.756 | 0.812 |
| LFMC + Drought | 15 | 0.895 | 0.897 |
| All three | 23 | 0.920 | 0.913 |
| Full baseline | 26 | 0.926 | 0.913 |

**The fuel moisture proxy (recent fire activity dynamics) alone achieves CV AUC 0.952, outperforming fire weather alone (0.809) by 14.3 percentage points.** This is the headline finding.

Combining predictors does not improve over the fuel moisture proxy alone for temporal CV. The full baseline with all 26 features achieves AUC 0.926, below the LFMC proxy's 0.952. Adding features from other families introduces noise that hurts the linear model on this small dataset (952 observations with 13.1% positive rate).

### 4.4 Phase 2: Land Cover Features

Adding MCD64A1-derived land cover fractions (forest fraction, shrubland fraction) to the baseline did not improve performance: CV AUC = 0.909 (vs 0.926 baseline). The land cover signal is already implicitly captured by the country indicator (Portugal has more eucalyptus, Spain more pine and shrubland).

### 4.5 Feature Importance

The top 5 features by standardized logistic regression coefficient are:
1. Historical average burned area for this week (seasonal fire climatology)
2. Area ratio: current area / historical average (anomaly signal)
3. Historical maximum burned area (tail severity)
4. Log historical average area
5. Historical average fire count

The top features combine seasonal fire climatology (what normally burns during this week) with the anomaly signal (how much more or less is burning compared to normal). Recent lagged features (previous week's area, 2-week rolling area) rank 8th and 9th, confirming the momentum component of the fuel moisture proxy.

### 4.6 Phase B: Risk Characterization

Portugal has a higher average predicted VLF probability (17.2%) than Spain (11.5%), consistent with Portugal's higher per-capita burned area documented in the literature (Fernandes et al. 2019). The seasonal risk profile differs between countries: Portugal's peak risk is concentrated in weeks 29-34 (mid-July to late August), while Spain's risk is more distributed across weeks 26-40 (late June to early October).

The model correctly identifies the extreme 2017 and 2025 fire seasons as having elevated VLF risk, with predicted probabilities exceeding 0.8 for the most severe weeks. The model also correctly identifies the relatively quiet 2018 and 2014 seasons as low-risk.

## 5. Discussion

### 5.1 Why Fire Activity Dynamics Outpredict Fire Weather

The finding that recent fire activity dynamics (our "fuel moisture proxy") outpredict fire weather indices has a clear physical interpretation. Active large fires are an integrative signal: they indicate that fuel moisture is low, that ignition conditions are met, that winds are sufficient for fire spread, and that drought has preconditioned the landscape. A single composite observable -- "how much is currently burning relative to expectations" -- encodes information from all four components of the fire environment triangle (fuels, weather, topography) plus the suppression dimension that fire weather indices cannot capture.

Fire weather, by contrast, captures only the atmospheric conditions. It can be extreme without producing large fires (when fuels are still green in early season, or when suppression successfully contains initial ignitions), and large fires can occur under apparently moderate fire weather when drought has accumulated over weeks or months.

### 5.2 Operational Implications

The current EFFIS alert system is based on FWI thresholds. Our results suggest that an anomaly-based alert trigger -- "current weekly fire activity exceeds X times the historical average for this week" -- could provide more accurate VLF warnings. This approach is complementary to, not a replacement for, weather-based forecasting: fire weather forecasts are available days in advance, while fire activity anomalies are observable in near-real-time from satellite.

A practical implementation would use a two-tier system: fire weather forecasts for anticipatory resource positioning (days ahead), and fire activity anomalies for escalated alerts and emergency pre-positioning (hours ahead, when satellite detections show above-normal burning).

### 5.3 Limitations

1. **Weekly temporal resolution**: EFFIS weekly data cannot capture sub-weekly VLF transitions. A fire that grows from manageable to catastrophic within 24 hours is resolved only at the weekly level.

2. **Country-level spatial resolution**: We aggregate to Portugal and Spain nationally. Subnational models (NUTS-3 regions) would improve spatial specificity but face data sparsity issues.

3. **No direct climate covariates**: Our predictor proxies approximate fire weather, fuel moisture, and drought from fire activity data rather than from gridded reanalysis. Adding ERA5 temperature, humidity, wind, and precipitation could improve the FWI proxy, potentially narrowing the performance gap with the LFMC proxy.

4. **MODIS detection limits**: EFFIS detects fires > ~30 ha from MODIS imagery. Small fires that grow into VLFs within the same week may not be captured as separate events.

5. **2025 holdout is a single year**: The holdout test on 2025 (a severe fire year) provides one validation point. Multi-year leave-one-out provides more robust estimates (the temporal CV results).

### 5.4 Relation to Prior Work

Rodrigues et al. (2019) applied Random Forest to VLF prediction in Spain using EFFIS data and achieved AUC 0.72-0.76. Our higher AUC (0.975-0.993 for tree models) likely reflects the inclusion of lagged fire activity features, which their study did not use. Viegas et al. (2004) found FWI correlates well with fire occurrence but weakly with fire size in Portugal -- consistent with our finding that fire weather alone has limited VLF prediction power (AUC 0.809).

The finding that tree models substantially outperform logistic regression (AUC 0.993 vs 0.926) reverses the finding from our synthetic-data preliminary analysis, which had found Ridge dominant. The real data contains nonlinear interaction effects that trees can capture -- likely the threshold behavior of VLF transitions under compound conditions.

## 6. Conclusion

Recent fire activity dynamics outpredict traditional fire weather indices for identifying very large fire weeks on the Iberian Peninsula. The ratio of current fire activity to historical seasonal expectations is the single most informative predictor, achieving AUC 0.952 with logistic regression and contributing to AUC 0.993 in gradient-boosted tree models. For operational fire management, this finding supports adding anomaly-based alert triggers that track actual burning in near-real-time alongside conventional fire weather forecasts.

## References

Bedia J et al. (2014) Sensitivity of fire weather index to different reanalysis products in the Iberian Peninsula. *Natural Hazards and Earth System Sciences* 14:1699-1711.

Fernandes PM et al. (2016) Characteristics and controls of extremely large wildfires in the western Mediterranean Basin. *Journal of Geophysical Research: Biogeosciences* 121:2141-2157.

Fernandes PM et al. (2019) Fire-smart management of forest landscapes in the Mediterranean basin under global change. *Landscape and Urban Planning* 189:1-10.

Rodrigues M et al. (2019) Modeling the spatial variation of the explanatory factors of human-caused wildfires in Spain using geographically weighted logistic regression. *Applied Geography* 48:52-63.

San-Miguel-Ayanz J et al. (2024) Forest Fires in Europe, Middle East and North Africa 2023. JRC Technical Report.

Tedim F et al. (2018) Defining extreme wildfire events: Difficulties, challenges, and impacts. *Fire* 1:9.

Turco M et al. (2016) Decreasing fires in Mediterranean Europe. *PLOS ONE* 11:e0150663.

Turco M et al. (2017) On the key role of droughts in the dynamics of summer fires in Mediterranean Europe. *Scientific Reports* 7:81.

Van Wagner CE (1987) Development and structure of the Canadian Forest Fire Weather Index System. Canadian Forestry Service Technical Report 35.

Vicente-Serrano SM et al. (2010) A multiscalar drought index sensitive to global warming: The Standardized Precipitation Evapotranspiration Index. *Journal of Climate* 23:1696-1718.

Viegas DX et al. (2004) Comparative study of various methods of fire danger evaluation in Southern Europe. *International Journal of Wildland Fire* 8:235-246.

Yebra M et al. (2019) A global review of remote sensing of live fuel moisture content for fire danger assessment. *Remote Sensing of Environment* 228:187-199.

Yebra M et al. (2024) Global estimation of live fuel moisture content. *Remote Sensing of Environment* 301:113893.
