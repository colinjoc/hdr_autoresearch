# Lagged Fire Activity Outperforms Seasonal Climatology for Very Large Fire Week Classification on the Iberian Peninsula

## Abstract

We investigate which predictor family best classifies very large fire (VLF) weeks -- country-weeks with >5,000 hectares burned -- on the Iberian Peninsula. Using 14 years (2012-2025) of real weekly fire statistics from the European Forest Fire Information System (EFFIS), we compare three predictor families derived from fire activity data via strict temporal cross-validation: (1) seasonal fire climatology features (historical averages and maxima), (2) recent fire activity features (ratios to historical norms and lagged burned area), and (3) cumulative year-to-date fire features. Recent fire activity features achieve cross-validated area under the receiver operating characteristic curve (AUC) of 0.952 (95% bootstrap confidence interval (CI): 0.934-0.968), outperforming seasonal climatology (AUC 0.809, CI: 0.768-0.848). However, 47% of VLF weeks are persistence events (preceded by another VLF week), and a trivial persistence baseline (last week's burned area) achieves AUC 0.814. Restricting evaluation to VLF onset weeks (excluding persistence), the recent fire activity features still outperform seasonal climatology (AUC 0.921 vs. 0.799 with Ridge logistic regression), indicating the signal extends beyond simple fire persistence. A gradient-boosted tree model using all features achieves AUC 0.993 in temporal cross-validation. These results are consistent across VLF thresholds from 1,000 to 20,000 ha. Importantly, no actual fire weather data (temperature, humidity, wind, precipitation, or Fire Weather Index values) was used in this study: all predictor families are derived from satellite-detected fire activity. Whether recent fire activity features would outperform actual fire weather indices remains an open question requiring integration of gridded meteorological reanalysis data.

## 1. Introduction

The Iberian Peninsula experiences the most severe wildfire regime in Western Europe. Portugal and Spain account for approximately 60% of total European burned area in most years, with annual losses ranging from 50,000 to over 500,000 hectares per country depending on conditions (San-Miguel-Ayanz et al. 2024). The distribution of fire impacts is highly skewed: very large fires (VLFs) represent roughly 10-15% of fire events but account for 70-80% of total burned area and virtually all fire-related fatalities (Tedim et al. 2018).

The standard operational tool for fire danger assessment across the European Union is the Canadian Forest Fire Weather Index (FWI) system (Van Wagner 1987), deployed operationally through the European Forest Fire Information System (EFFIS). The FWI computes fire danger from temperature, humidity, wind speed, and precipitation. However, the FWI was developed for Canadian boreal forests and does not include live fuel moisture content (LFMC), a quantity that is particularly important in Mediterranean evergreen vegetation (Bedia et al. 2014; Viegas et al. 2004; Ruffault et al. 2018). Several studies have documented the limitations of FWI in the Mediterranean context: Bedia et al. (2018) found that FWI requires region-specific calibration, and Turco et al. (2018) showed that the relationship between FWI and burned area in Spain is nonlinear and mediated by fuel availability.

Fire activity itself is temporally autocorrelated. Large fires persist across weekly boundaries (a fire that burns 10,000 ha over 10 days will appear in two consecutive weekly observations), and the weather systems that drive extreme fire conditions typically persist for several days (Preisler et al. 2004; Taylor et al. 2013). This creates a natural autoregressive structure in fire activity time series. Turco et al. (2013) demonstrated strong temporal relationships between fire weather and fire activity in the Mediterranean, while Vitolo et al. (2020) assessed the operational performance of EFFIS fire danger forecasts.

Our research question: **Which predictor family derived from fire activity data -- seasonal climatology, recent dynamics, or cumulative stress -- best classifies the country-weeks that produce very large fires on the Iberian Peninsula?**

We emphasize that this study compares predictor families all derived from fire activity data, not from meteorological observations. The seasonal climatology features approximate what fire weather indices capture (the typical fire danger for each week of the year), but they are not actual fire weather measurements. The recent fire activity features are autoregressive -- they use recent fire observations to predict future fire activity. Testing whether actual meteorological fire weather indices are outperformed requires integration of gridded reanalysis data (e.g., ERA5), which we identify as essential future work.

## 2. Data

### 2.1 EFFIS Weekly Fire Statistics (Primary Dataset)

We obtained weekly fire statistics (number of detected fire events and total burned area in hectares) for Portugal and Spain from the EFFIS/GWIS statistics API (api2.effis.emergency.copernicus.eu), covering 2012-2025. Each observation is a (country, year, week) triplet. The EFFIS system detects fires from MODIS and VIIRS satellite imagery with a minimum detectable fire size of approximately 30 hectares.

The weekly data includes:
- **fires**: number of fire events detected that week
- **area_ha**: total burned area (hectares)
- **fires_avg / fires_max**: historical average and maximum fire count for that week
- **area_ha_avg / area_ha_max**: historical average and maximum burned area

This provides 1,456 country-week observations across 14 years and 2 countries. After filtering to fire-relevant weeks (15-48, approximately April-November), the modelling dataset contains 952 observations.

### 2.2 GWIS Regional Data (Supplementary)

We downloaded two supplementary datasets from the GWIS data archive (S3):
- **MCD64A1**: MODIS burned area by land cover type (forest, shrubland, cropland) at subnational level, 2002-2024
- **GlobFire**: Individual fire event counts and burned area at subnational level, 2002-2024

### 2.3 No External Meteorological Data

This study uses exclusively fire activity observations. No temperature, humidity, wind, precipitation, or computed fire weather index data was obtained. All predictor families are derived from satellite-detected fire counts and burned area. This is a limitation that we discuss in Section 5.3.

### 2.4 No Synthetic Data

All results use exclusively real satellite-derived fire observations.

## 3. Methods

### 3.1 VLF Definition

We define a "very large fire week" (VLF) as a country-week with total burned area exceeding 5,000 hectares. This threshold yields a 13.1% positive rate among fire-season country-weeks. We test sensitivity to this threshold (1,000, 2,500, 5,000, 10,000, 20,000 ha) in Section 4.6.

### 3.2 Predictor Families

We constructed three predictor families from the EFFIS weekly data:

**Seasonal Climatology (10 features)**: Historical fire activity patterns -- weekly average and maximum fire count and area, log-transformed averages, fire season indicator, fire season week number, and cyclical month encodings. These capture the expected level of fire activity for each week of the year, analogous to (but not equivalent to) fire weather indices.

**Recent Fire Activity (10 features)**: The ratio of current fire count and area to historical averages, and lagged values (1 week, 2 weeks, 2-week rolling sum), with cyclical month encodings. These are autoregressive features -- they use recent fire observations to predict near-future fire activity. The physical interpretation is that elevated recent burning indicates conditions (weather, fuel moisture, drought, landscape preconditioning) favorable for continued large fire activity.

**Cumulative Season Stress (7 features)**: Cumulative year-to-date fire counts and area, year trend, 4-week rolling sums, and cyclical month encodings. These capture the accumulation of fire activity over the season.

**Full Baseline (26 features)**: All of the above plus additional cyclical temporal encodings (week sine/cosine), country indicator, and longer lag features.

**Important clarification**: In the initial version of this paper, we labelled these families as "Fire Weather Proxy (FWI)," "Fuel Moisture Proxy (LFMC)," and "Drought Proxy (SPEI)." This labelling was misleading. None of these features are proxies for fire weather, fuel moisture, or drought in any physically meaningful sense. They are all derived from fire activity data. The seasonal climatology features capture *when* fires typically occur, and the recent fire activity features capture *what is currently happening*. We have corrected this throughout the revised paper.

### 3.3 Fire Persistence

Large fires on the Iberian Peninsula frequently persist across weekly boundaries. We define a VLF week as a "persistence" event if the immediately preceding week for the same country was also a VLF week, and as an "onset" event otherwise. This distinction is operationally important: predicting that a fire already burning will continue burning is less useful than predicting that a new VLF event will begin. We report results both on all VLF weeks and on onset-only VLF weeks.

### 3.4 Temporal Cross-Validation

We use strict temporal cross-validation: for each test year Y (2015 through 2025), we train on all data from years strictly before Y and evaluate on year Y. This ensures no future information leaks into training. The 2025 fire season serves as the final holdout test.

### 3.5 Model Tournament

We evaluated six model families:
1. Ridge logistic regression (L2-penalized, balanced class weights)
2. XGBoost (depth=4, scale_pos_weight=10)
3. XGBoost-deep (depth=6)
4. ExtraTrees (balanced class weights)
5. Random Forest (balanced class weights)
6. LightGBM (depth=4, scale_pos_weight=10)

### 3.6 Metrics

Primary: AUC (area under ROC curve) with 95% bootstrap confidence intervals (1,000 resamples). Secondary: F2-score (recall-weighted), Brier score, precision, and recall at optimal threshold.

## 4. Results

### 4.1 Fire Persistence Analysis

Of 125 total VLF weeks in the dataset, 66 (53%) are onset events and 59 (47%) are persistence events. The week-to-week autocorrelation of burned area is rho = 0.387 across the pooled dataset (rho = 0.285 for Portugal, rho = 0.456 for Spain).

A trivial persistence baseline -- predicting VLF from last week's burned area alone -- achieves AUC 0.814 on the full dataset. This sets a minimum bar: any useful VLF prediction model must substantially exceed this baseline.

### 4.2 Phase 1: Model Tournament

| Model | CV AUC | Holdout AUC | CV F2 |
|-------|--------|-------------|-------|
| XGBoost (depth=6) | 0.993 | 1.000 | 0.922 |
| XGBoost (depth=4) | 0.993 | 1.000 | 0.913 |
| LightGBM | 0.990 | 1.000 | 0.877 |
| Random Forest | 0.983 | 0.995 | 0.847 |
| ExtraTrees | 0.975 | 0.977 | 0.851 |
| Ridge | 0.926 | 0.913 | 0.736 |

The tree-based models substantially outperform the linear model, indicating nonlinear interactions among features. The holdout AUC of 1.000 for XGBoost means all 14 VLF weeks in 2025 are ranked above all 54 non-VLF weeks. However, this is a single year (68 observations), and 2025 was a severe fire year where VLF weeks were likely distinctly extreme. Per-year AUC analysis (Section 4.4) provides more robust estimates.

### 4.3 Predictor Family Comparison

We compare predictor families using both Ridge logistic regression and XGBoost, addressing the concern that the original comparison used only a linear model.

**Ridge logistic regression:**

| Predictor Family | N Features | CV AUC | 95% CI | Holdout AUC |
|-----------------|-----------|---------|--------|-------------|
| Seasonal climatology | 10 | 0.809 | [0.768, 0.848] | 0.922 |
| Cumulative stress | 7 | 0.808 | -- | 0.828 |
| **Recent fire activity** | **10** | **0.952** | **[0.934, 0.968]** | **0.971** |
| Full baseline | 26 | 0.926 | [0.902, 0.946] | 0.913 |

**XGBoost (depth=4):**

| Predictor Family | N Features | CV AUC | Holdout AUC |
|-----------------|-----------|---------|-------------|
| Seasonal climatology | 10 | 0.751 | 0.882 |
| Cumulative stress | 7 | 0.772 | 0.930 |
| **Recent fire activity** | **10** | **0.972** | **0.976** |
| Full baseline | 26 | 0.993 | 1.000 |

The recent fire activity features dominate in both Ridge and XGBoost. With XGBoost, seasonal climatology actually performs *worse* (AUC 0.751) than with Ridge (0.809), while recent fire activity features improve slightly (0.972 vs. 0.952). The 95% bootstrap confidence intervals for Ridge confirm the difference is statistically significant: the CI for recent fire activity [0.934, 0.968] does not overlap with the CI for seasonal climatology [0.768, 0.848].

The anomaly that combining all features hurts Ridge performance (AUC 0.920 < 0.952 for recent fire activity alone) likely reflects multicollinearity: the seasonal climatology features in the full baseline partially overlap with the month encodings already present in the recent fire activity set, and the increased dimensionality relative to the small training set (as few as 204 observations for the earliest folds) degrades Ridge regularization. With XGBoost, which handles multicollinearity through tree splitting, the full baseline achieves the best performance (AUC 0.993).

### 4.4 Per-Year AUC Analysis

| Year | XGBoost AUC | Ridge AUC | N VLF | N total |
|------|-------------|-----------|-------|---------|
| 2015 | 0.998 | 0.972 | 7 | 68 |
| 2016 | 0.983 | 0.903 | 14 | 68 |
| 2017 | 0.986 | 0.914 | 21 | 68 |
| 2018 | 0.977 | 0.977 | 2 | 68 |
| 2019 | 0.990 | 0.854 | 5 | 68 |
| 2020 | 1.000 | 0.946 | 6 | 68 |
| 2021 | 0.994 | 0.876 | 5 | 68 |
| 2022 | 0.995 | 0.975 | 17 | 68 |
| 2023 | 0.997 | 0.889 | 5 | 68 |
| 2024 | 1.000 | 0.974 | 3 | 68 |
| 2025 | 1.000 | 0.913 | 14 | 68 |

XGBoost achieves AUC > 0.977 in every year. Ridge is more variable, with worst performance in 2019 (AUC 0.854) and 2021 (AUC 0.876), both years with few VLF weeks. The high AUC is not driven by a few extreme years -- it is consistent across the full temporal range.

### 4.5 Onset-Only Evaluation

Restricting evaluation to VLF onset weeks (excluding persistence), using only non-VLF and onset-VLF weeks as the evaluation set:

| Model | Features | All VLF AUC | Onset-only AUC |
|-------|----------|-------------|----------------|
| Ridge | Full baseline | 0.926 | 0.897 |
| Ridge | Recent fire activity | 0.952 | 0.921 |
| Ridge | Seasonal climatology | 0.809 | 0.799 |
| XGBoost | Full baseline | 0.993 | 0.989 |

Performance drops modestly when restricting to onset (e.g., Ridge full baseline: 0.926 to 0.897), confirming that persistence events inflate the overall metric. However, the recent fire activity features still substantially outperform seasonal climatology in onset-only evaluation (Ridge: 0.921 vs. 0.799), indicating the signal extends beyond detecting ongoing fires. The recent fire activity features capture conditions favorable for *new* VLF onset, not just fire continuation.

### 4.6 Threshold Sensitivity

| Threshold (ha) | VLF rate | N pos | Seasonal clim. AUC | Recent activity AUC | Full AUC |
|----------------|----------|-------|---------------------|---------------------|----------|
| 1,000 | 42.4% | 404 | 0.813 | 0.913 | 0.892 |
| 2,500 | 24.1% | 229 | 0.825 | 0.924 | 0.906 |
| 5,000 | 13.1% | 125 | 0.809 | 0.952 | 0.926 |
| 10,000 | 7.4% | 70 | 0.794 | 0.969 | 0.948 |
| 20,000 | 3.5% | 33 | 0.738 | 0.985 | 0.945 |

The advantage of recent fire activity features over seasonal climatology is robust across all thresholds and increases for more extreme thresholds. At 20,000 ha (the most extreme 3.5% of weeks), the gap widens to 24.7 percentage points (0.985 vs. 0.738). This makes physical sense: the most extreme fire weeks are the ones most likely to follow other extreme weeks (compounding events).

### 4.7 Feature Importance

The top 5 features by standardized logistic regression coefficient are:
1. Historical average burned area for this week (seasonal climatology)
2. Area ratio: current area / historical average (anomaly signal)
3. Historical maximum burned area (seasonal climatology)
4. Log historical average area (seasonal climatology)
5. Historical average fire count (seasonal climatology)

The top-ranked features are seasonal climatology variables, but the highest-performing predictor *family* is recent fire activity. This apparent paradox reflects that individual seasonal features have high marginal importance, but the recent fire activity features are collectively more informative because they capture the current state of fire conditions. The anomaly signal (rank 2) -- how much more fire activity is occurring compared to expectations -- is the bridge between the two families.

### 4.8 Land Cover Features

Adding MCD64A1-derived land cover fractions (forest fraction, shrubland fraction) to the baseline did not improve performance: CV AUC = 0.909 (vs. 0.926 baseline). The land cover signal is implicitly captured by the country indicator.

## 5. Discussion

### 5.1 What Recent Fire Activity Features Actually Capture

The recent fire activity features are autoregressive: they use this week's and recent weeks' fire counts and burned area to predict next week's VLF status. Their strong performance has a clear interpretation: active large fires indicate that the combination of weather, fuel moisture, drought, and landscape conditions is favorable for extreme fire behavior. A fire week where burning significantly exceeds the historical average for that calendar week is a strong signal that conditions are extreme.

However, this interpretation must be qualified. The autoregressive signal has two components:

1. **Fire persistence**: Large fires frequently burn across weekly boundaries. When a 15,000 ha fire takes 10 days to contain, it appears as a VLF week followed by another VLF week. The lagged features detect this persistence -- but operationally, predicting that an ongoing fire will continue burning is not a useful early warning.

2. **Condition signaling**: Elevated fire activity also signals that atmospheric and fuel conditions are extreme, making *new* VLF onset more likely. Our onset-only analysis (Section 4.5) confirms this second component: recent fire activity features achieve AUC 0.921 even when persistence events are excluded.

The practical value lies primarily in the condition-signaling component. Fire managers already know about ongoing fires. What they need is warning that conditions are ripe for new fires to become VLFs.

### 5.2 What This Study Does Not Show

This study does **not** show that fire activity features outperform fire weather indices. The title of the initial version of this paper -- "Recent Fire Activity Dynamics Outpredict Fire Weather Indices" -- was unsupported and has been corrected. Specifically:

1. **No actual fire weather data was used.** The seasonal climatology features (historical averages and maxima of fire activity) are not fire weather measurements. The Fire Weather Index is computed from temperature, relative humidity, wind speed, and precipitation (Van Wagner 1987). We did not obtain or use any of these variables.

2. **The comparison is between autoregressive features and a seasonal baseline.** Finding that "what is currently burning" outpredicts "what usually burns this week" is expected because current conditions are more informative than long-term averages. This does not imply superiority over actual real-time weather data.

3. **Fire weather data is available but was not included.** ERA5 reanalysis provides gridded temperature, humidity, wind, and precipitation at hourly resolution. EFFIS computes country-level Daily Severity Rating (DSR) values from FWI. Integrating these data sources is a prerequisite for any claim about outperforming fire weather indices.

### 5.3 Limitations

1. **No meteorological covariates**: The most significant limitation is the absence of actual fire weather data. All predictor families are derived from fire activity observations, making this fundamentally a study of autoregressive prediction from fire activity data rather than a comparison with fire weather indices.

2. **Weekly temporal resolution**: VLF events develop over 1-3 days, not weeks. Weekly aggregation means the lagged features may capture fires that are still actively burning rather than providing advance warning. Sub-weekly data (daily EFFIS detections) would improve operational relevance.

3. **Country-level spatial resolution**: We aggregate to Portugal and Spain nationally. No fire management agency operates at this resolution. Subnational analysis (NUTS-2 or NUTS-3 regions) would be necessary for operational relevance but faces data sparsity issues.

4. **Fire persistence inflates metrics**: With 47% of VLF weeks being persistence events, models partially earn their AUC by detecting ongoing fires rather than predicting new VLF onset. Our onset-only analysis partially addresses this, but the operational distinction between detection and prediction remains.

5. **Small holdout test**: The 2025 holdout consists of 68 observations (14 VLF) from a single severe fire year. The holdout AUC of 1.000 reflects favorable test conditions and should not be interpreted as general performance.

6. **MODIS detection limits**: EFFIS detects fires > ~30 ha. Small fires that grow into VLFs within the same week may not be captured as separate events.

7. **VLF threshold not externally validated**: The 5,000 ha threshold was chosen to yield a ~13% positive rate. While results are robust across thresholds (Section 4.6), the threshold is not based on an established operational definition.

### 5.4 Relation to Prior Work

Rodrigues et al. (2019) studied spatial variation of human-caused wildfires in Spain using geographically weighted logistic regression. Our approach differs in focusing on temporal prediction of VLF weeks rather than spatial modeling of fire causes.

The finding that autoregressive features dominate is consistent with the broader time-series fire prediction literature. Preisler et al. (2004) showed that recent fire occurrence is a strong predictor of near-future fire occurrence. Taylor et al. (2013) demonstrated effective time-series forecasting of wildfire using lagged observations. Turco et al. (2013) found strong temporal coupling between fire weather and fire activity in the Mediterranean. Our contribution is quantifying the relative importance of autoregressive versus seasonal-climatological features specifically for VLF classification on the Iberian Peninsula.

The gap between tree models and Ridge logistic regression (AUC 0.993 vs. 0.926) is consistent with the fire risk literature finding that VLF transitions involve threshold behavior and compound conditions that linear models cannot capture (Fernandes et al. 2016).

### 5.5 Operational Implications

Despite the limitations, this study does have a practical suggestion for fire management, stated with appropriate caveats:

**For fire agencies already monitoring EFFIS weekly statistics**, tracking the ratio of current fire activity to the historical average for each calendar week provides a useful alert signal. When current-week burning exceeds, say, twice the historical average during fire season, the probability of VLF conditions continuing or new VLFs developing is elevated. This is complementary to (not a replacement for) weather-based fire danger forecasting.

However, this suggestion is modest compared to the original paper's claims. A country-level weekly indicator is not an operational alert system. Operational fire management requires spatial specificity (where will the next fire start?), temporal precision (when will conditions become critical?), and calibrated probabilities. This study provides none of these.

### 5.6 Future Work

1. **Integrate actual fire weather data.** Obtain ERA5 reanalysis (temperature, humidity, wind, precipitation) and compute actual FWI values for Portugal and Spain. Only then can the question "do fire activity features outperform fire weather?" be answered.

2. **Sub-weekly analysis.** Use daily EFFIS detection data to assess lead time: how many days before a VLF does the anomaly signal appear?

3. **Subnational analysis.** Use GWIS data at NUTS-2 or NUTS-3 level to test whether the approach provides spatial specificity.

4. **Calibration analysis.** Assess whether predicted VLF probabilities are well-calibrated (reliability diagram).

5. **SHAP analysis.** Use SHAP interaction values from XGBoost to identify which feature interactions drive the nonlinear performance gain.

## 6. Conclusion

Recent fire activity features outperform seasonal climatology features for classifying very large fire weeks on the Iberian Peninsula, achieving AUC 0.952 vs. 0.809 with Ridge logistic regression (a statistically significant difference based on non-overlapping 95% bootstrap confidence intervals). This finding is robust across VLF thresholds (1,000-20,000 ha), holds with both linear and tree-based models, and persists when evaluation is restricted to VLF onset events (excluding fire persistence).

However, approximately half of VLF weeks are persistence events, and a trivial persistence baseline achieves AUC 0.814. The autoregressive features earn part of their performance by detecting ongoing fires. Furthermore, no actual fire weather data was used in this study. Whether recent fire activity features outperform actual meteorological fire weather indices remains an open question that requires integration of gridded reanalysis data.

For practical fire management, the ratio of current fire activity to seasonal expectations provides a useful monitoring signal, but this study does not provide the spatial, temporal, or calibration precision needed for operational alert systems.

## References

Bedia J et al. (2014) Sensitivity of fire weather index to different reanalysis products in the Iberian Peninsula. *Natural Hazards and Earth System Sciences* 14:1699-1711.

Bedia J et al. (2018) Global patterns in the sensitivity of burned area to fire-weather: Implications for climate change. *Agricultural and Forest Meteorology* 214:369-379.

Fernandes PM et al. (2016) Characteristics and controls of extremely large wildfires in the western Mediterranean Basin. *Journal of Geophysical Research: Biogeosciences* 121:2141-2157.

Fernandes PM et al. (2019) Fire-smart management of forest landscapes in the Mediterranean basin under global change. *Landscape and Urban Planning* 189:1-10.

Preisler HK et al. (2004) Probability based models for estimation of wildfire risk. *International Journal of Wildland Fire* 13:133-142.

Rodrigues M et al. (2019) Modeling the spatial variation of the explanatory factors of human-caused wildfires in Spain using geographically weighted logistic regression. *Applied Geography* 48:52-63.

Ruffault J et al. (2018) Increased likelihood of heat-induced large wildfires in the Mediterranean Basin. *Scientific Reports* 8:14530.

San-Miguel-Ayanz J et al. (2024) Forest Fires in Europe, Middle East and North Africa 2023. JRC Technical Report.

Taylor SW et al. (2013) Wildfire prediction to inform fire management: Statistical science challenges. *Statistical Science* 28:586-615.

Tedim F et al. (2018) Defining extreme wildfire events: Difficulties, challenges, and impacts. *Fire* 1:9.

Turco M et al. (2013) Climate change impacts on wildfires in a Mediterranean environment. *Climatic Change* 125:369-380.

Turco M et al. (2016) Decreasing fires in Mediterranean Europe. *PLOS ONE* 11:e0150663.

Turco M et al. (2017) On the key role of droughts in the dynamics of summer fires in Mediterranean Europe. *Scientific Reports* 7:81.

Turco M et al. (2018) Exacerbated fires in Mediterranean Europe due to anthropogenic warming projected with non-stationary climate-fire models. *Nature Communications* 9:3821.

Van Wagner CE (1987) Development and structure of the Canadian Forest Fire Weather Index System. Canadian Forestry Service Technical Report 35.

Vicente-Serrano SM et al. (2010) A multiscalar drought index sensitive to global warming: The Standardized Precipitation Evapotranspiration Index. *Journal of Climate* 23:1696-1718.

Viegas DX et al. (2004) Comparative study of various methods of fire danger evaluation in Southern Europe. *International Journal of Wildland Fire* 8:235-246.

Vitolo C et al. (2020) ERA5-based global meteorological wildfire danger maps. *Scientific Data* 7:216.

Yebra M et al. (2019) A global review of remote sensing of live fuel moisture content for fire danger assessment. *Remote Sensing of Environment* 228:187-199.

Yebra M et al. (2024) Global estimation of live fuel moisture content. *Remote Sensing of Environment* 301:113893.
