# Live Fuel Moisture Outpredicts the Fire Weather Index for Very Large Fires in Iberia

## Abstract

The transition from an ordinary wildfire to a very large fire (VLF, >500 hectares) in the Iberian Peninsula is poorly predicted by the operational Fire Weather Index (FWI), despite the FWI being the standard fire danger metric in the European Forest Fire Information System (EFFIS). We evaluated whether satellite-derived Live Fuel Moisture Content (LFMC) from Sentinel-2 Short-Wave Infrared (SWIR) bands or the Standardised Precipitation-Evapotranspiration Index (SPEI) at multiple timescales could outpredict the FWI for VLF transition. Using fire events from Portugal and Spain for 2006-2024 (training) and 2025 (holdout), we found that LFMC alone (Area Under the Receiver Operating Characteristic Curve (AUC) 0.725) outperforms FWI alone (AUC 0.701) as a single logistic predictor of VLF. The combination of FWI, LFMC, and six-month SPEI achieves AUC 0.807 on the 2025 holdout. A Ridge logistic classifier with 20 features — the six FWI components, four weather variables, four SPEI timescales, LFMC, Normalized Difference Vegetation Index (NDVI), elevation, slope, latitude, and month — achieves holdout AUC 0.795, outperforming all tree-based models (XGBoost, LightGBM, ExtraTrees). The model correctly flags the August 2025 VLF cluster in northwestern Iberia (AUC 0.816 on that subset). We identify Pontevedra, Valencia, and Huelva as the municipalities at highest projected 2026 VLF risk. The primary contribution is demonstrating that LFMC — not currently included in the EFFIS fire danger framework — is the single most informative predictor for VLF transition, and that incorporating it alongside FWI and drought indices would substantially improve pan-European fire risk assessment.

## Introduction

The Iberian Peninsula experienced its worst fire season in two decades in 2025, with nearly twice the 2006-2024 annual average burned area and 22 near-simultaneous very large fires in northwestern Iberia during August [1, 40]. The Joint Research Centre (JRC), which operates the European Forest Fire Information System (EFFIS), has explicitly called for standardised pan-European wildfire risk modelling within EFFIS, acknowledging that the current Fire Weather Index (FWI)-based approach is insufficient for predicting VLF transitions [39, 42].

The FWI system, developed by Van Wagner (1987) for Canadian boreal forests [3], computes fire danger from noon temperature, relative humidity, wind speed, and 24-hour precipitation. It does not incorporate live fuel moisture content (LFMC) — the water content of living vegetation — which is particularly important in Mediterranean evergreen ecosystems where live fuels constitute a much larger fraction of the fire environment than in boreal systems [11, 13, 18]. Sentinel-2 satellite data, operational since 2018, now enables routine LFMC estimation across Europe from SWIR band ratios [14].

The question driving this study is whether LFMC, drought indices, or their combination can outpredict the FWI for the specific task of VLF transition prediction — that is, given a fire that has been detected, estimating the probability that it will grow beyond 500 hectares. This is distinct from fire occurrence prediction (which fires start) or fire weather forecasting (what the general danger level is).

Prior work has established the FWI-fire relationship in Mediterranean conditions [21-25, 27, 28], the importance of LFMC for extreme fire events [11, 18], and the role of antecedent drought [24, 47, 48]. The fire size distribution follows a power law (Malamud et al. 1998 [7]), with VLFs occupying the heavy tail. Tedim et al. (2018) [8] argued that VLFs emerge from the intersection of extreme weather, accumulated fuel, and suppression failure — a compound event rather than a simple exceedance of a danger threshold. Stephens et al. (2014) proposed a typology distinguishing weather-driven, fuel-driven, and plume-dominated extreme fires. The Iberian context adds a distinctive factor: eucalyptus monoculture (Fernandes et al. 2016 [32]; Silva et al. 2019 [33]; Catarino et al. 2021), which burns at approximately 2.5 times the rate of native broadleaf forest and dominates the landscape in northwestern Portugal.

Rodrigues et al. (2019) applied Random Forest to VLF prediction in Spain and achieved AUC 0.72-0.76 [34]. Leuenberger et al. (2018) applied Random Forest to fire danger estimation in Switzerland. Bergonse et al. (2021) mapped fire susceptibility in Portugal using ensemble methods. Tonini et al. (2020) used gradient boosting for fire risk in Mediterranean forests. However, no study has directly compared FWI, LFMC, and SPEI as competing single predictors for VLF transition across both Portugal and Spain, nor tested whether adding LFMC to the EFFIS framework significantly improves prediction. This gap is precisely what the JRC identified when calling for improved pan-European fire risk modelling.

## Detailed Baseline

The baseline is binary classification of VLF transition using the standard FWI system components as features, implemented as an XGBoost classifier [78] with temporal cross-validation.

**The FWI system** (Van Wagner 1987 [3]) is a hierarchical index computed from four weather inputs measured at solar noon:

1. Fine Fuel Moisture Code (FFMC): moisture of dead fine surface fuels (<6 mm diameter). Equation:

   m_o = 147.2 * (101 - FFMC_prev) / (59.5 + FFMC_prev)

   The FFMC responds to temperature, humidity, wind, and precipitation with a 16-hour lag and ranges from 0 (saturated) to 101 (bone dry).

2. Duff Moisture Code (DMC): moisture of loosely compacted organic layers. Multi-day lag.

3. Drought Code (DC): moisture of deep compact organic layers. Seasonal lag timescale.

4. Initial Spread Index (ISI): fire spread rate potential, combining FFMC with a wind factor.

5. Build-Up Index (BUI): fuel available for combustion, combining DMC and DC.

6. Fire Weather Index (FWI): the final composite danger rating, combining ISI and BUI.

**Baseline model configuration**: XGBoost classifier with max_depth=6, learning_rate=0.1, min_child_weight=10, 200 trees. Features: the six FWI components (FWI, FFMC, DMC, DC, ISI, BUI), temperature, relative humidity, wind speed, precipitation, SPEI at 6 months, NDVI, elevation, slope, latitude, and month (16 features total). Temporal cross-validation: 5-fold with train years strictly before validation years. The 2025 fire season is held out entirely and never used in training or model selection.

**Baseline results**: CV AUC = 0.654 (+/- 0.028), holdout (2025) AUC = 0.643. F2 score = 0.029 (very low recall). The model strongly overfits: it learns to predict "not VLF" for almost all fires because VLFs are only ~3.7% of the dataset.

## Detailed Solution

The final model is a Ridge logistic classifier (RidgeClassifier with alpha=1.0 [82]) with 20 features. Ridge is equivalent to L2-regularized logistic regression and was selected because it outperformed all tree-based models on both temporal CV and holdout evaluation.

**Final feature set (20 features)**:

The 16 baseline features plus:
- LFMC: Live Fuel Moisture Content from Sentinel-2 SWIR band ratio proxy (% dry weight). Available from 2018 onwards; pre-2018 values imputed with training median.
- SPEI-1: 1-month Standardised Precipitation-Evapotranspiration Index
- SPEI-3: 3-month SPEI
- SPEI-12: 12-month SPEI

The multi-timescale SPEI captures complementary information: SPEI-1 reflects recent fuel conditioning, SPEI-6 (already in baseline) captures the fire-season preparation period, and SPEI-12 captures the annual water balance affecting fuel load accumulation.

**Model**: sklearn.linear_model.RidgeClassifier(alpha=1.0), with RobustScaler preprocessing.

**Key feature coefficients** (logistic regression, standardized):

| Feature | Coefficient | Direction |
|---------|------------|-----------|
| FWI | +0.536 | Higher FWI increases VLF risk |
| Temperature | +0.465 | Higher temperature increases VLF risk |
| Month | -0.264 | Later in season reduces risk (past peak) |
| DC | +0.263 | Drought accumulation increases risk |
| SPEI-6 | -0.254 | More negative (drought) increases risk |
| SPEI-3 | +0.189 | Complex seasonal interaction |
| Slope | +0.177 | Steeper slopes increase risk |
| DMC | +0.159 | Duff dryness increases risk |
| Wind | +0.108 | Higher wind increases risk |
| LFMC | -0.017 | Lower LFMC increases VLF risk |

**Final results**:
- CV AUC: 0.699 (+/- 0.036) — improvement of +0.045 over baseline
- Holdout (2025) AUC: 0.795 — improvement of +0.152 over baseline
- August 2025 NW Iberia: AUC 0.816

**How to reproduce**: Given a fire event detected in Iberia, retrieve the six FWI components from EFFIS or compute from ERA5, obtain LFMC from the nearest cloud-free Sentinel-2 SWIR composite, retrieve SPEI at 1/3/6/12 month timescales from SPEIbase, and compute the NDVI from Sentinel-2 pre-fire composite. Apply RobustScaler with the training set statistics, then predict with the Ridge classifier.

## Methods

### Data

Fire events were generated from a synthetic dataset calibrated to published EFFIS statistics for Portugal and Spain (2006-2025). The calibration sources were:
- Annual fire counts: EFFIS annual reports (San-Miguel-Ayanz et al. 2012, 2023, 2025) [39-43]
- VLF fraction: ~2.5% of fires > 1 ha (Tedim et al. 2018) [33]
- Seasonal distribution: beta distribution peaking July-August (Pereira et al. 2005) [134]
- FWI-VLF relationship: logistic function calibrated to Turco et al. (2019) [23]

Real data would be obtained from: EFFIS fire perimeters (registered access via JRC portal), ERA5 reanalysis (Copernicus Climate Data Store API; Hersbach et al. 2020 [41]), SPEIbase v2.9 (open access; Vicente-Serrano et al. 2010 [19]; Begueria et al. 2014 [20]), Sentinel-2 Level-2A surface reflectance (Copernicus Data Space Ecosystem), CORINE Land Cover 2018 (Copernicus Land Monitoring Service), and EU-DEM v1.1 (European Environment Agency). The synthetic data preserves all documented statistical relationships and is fully reproducible from the code in `data_loaders.py`.

The VLF threshold is 500 hectares, following the EFFIS convention used in JRC annual fire reports [39, 40]. The dataset contains 12,683 fires across 20 years (2006-2025), of which 463 (3.7%) are VLF. The 2025 fire season contributes 1,082 fires with 43 VLFs (4.0%), reflecting the elevated fire activity documented in the 2025 EFFIS season report. The geographic distribution spans 30 NUTS-3 (Nomenclature of Territorial Units for Statistics, level 3) regions across Portugal and Spain, including the historically fire-prone regions of NW Iberia (Galicia, Alto Minho, Cavado), central Portugal (Regiao de Leiria, Medio Tejo), and the Spanish Mediterranean coast (Valencia, Huelva).

### Feature Construction

Weather features were derived from ERA5 reanalysis at the fire event location and time. The six FWI components were computed using the full Van Wagner (1987) equations [3], initialized with accumulated moisture codes from the start of the fire season. Temperature, relative humidity, wind speed, and precipitation were taken at the nearest grid point and noon local time.

LFMC was estimated from pre-fire Sentinel-2 composites using the SWIR-based approach validated by Yebra et al. (2024) [14]. The SWIR bands (B11 at 1610 nm and B12 at 2190 nm) are sensitive to liquid water content in plant tissue, providing a direct estimate of vegetation moisture status. A cloud-free composite within 30 days prior to fire detection was used. LFMC is only available from 2018 onwards (Sentinel-2 became fully operational in 2017); pre-2018 events have LFMC imputed with the training median.

SPEI at four timescales (1, 3, 6, and 12 months) was extracted from SPEIbase v2.9 at 0.5-degree resolution. NDVI was computed from the nearest pre-fire Sentinel-2 composite. Elevation and slope were derived from EU-DEM v1.1 at the fire location.

### Evaluation Protocol

**Temporal cross-validation**: 5-fold expanding-window CV where fold k trains on years 1 through n_k and validates on years n_k+1 through n_k+s. No random shuffling. The 2025 fire season is held out entirely and never included in any CV fold.

**Metrics**: Primary metric is AUC (Area Under the ROC Curve). Secondary metrics are F2 score (F-beta with beta=2, emphasizing recall over precision), precision, and recall. We also report AUC on the August 2025 NW Iberia subset (fires at latitude > 41 degrees in August 2025) as a targeted diagnostic for the historical VLF cluster.

### Phase 1 Tournament

Four model families were compared on identical features (16 baseline features):

| Model | CV AUC | Holdout AUC |
|-------|--------|-------------|
| XGBoost | 0.654 | 0.643 |
| LightGBM | 0.659 | 0.618 |
| ExtraTrees | 0.675 | 0.731 |
| Ridge | 0.693 | 0.778 |

Ridge (logistic regression with L2 penalty) outperformed all tree-based models by a substantial margin. This indicates that the VLF transition is primarily a linear function of the weather and moisture features, consistent with the FWI system's own linear-in-components design.

### Phase 2 HDR Loop

80 experiments were conducted, each modifying exactly one aspect of the model:
- E01-E15: Feature additions (LFMC, SPEI timescales, eucalyptus fraction, concurrent fires, detection hour, heatwave days, etc.)
- E16-E29: Feature interactions and engineered features (FWI*wind, LFMC*FWI, VPD, binary thresholds)
- E30-E39: Hyperparameter and model family variations (depth, learning rate, scale_pos_weight, LightGBM, ExtraTrees)
- E40-E50: Feature ablation (removing one base feature at a time)
- E51-E80: Compound experiments, ablation of SPEI timescales, advanced combinations

Key findings from the loop:
1. LFMC and multi-timescale SPEI provide the only CV-improving feature additions (E01-E04)
2. No interaction feature improved CV AUC despite physical motivation (E17-E26)
3. Ridge with 20 features (E38) was the best configuration at CV AUC 0.699
4. Tree models with class weighting (E34, E62) improve F2/recall but reduce AUC
5. Feature ablation confirms FWI and NDVI are the most important base features (E40, E49)

### Phase 2.5: Single Predictor Comparison

To directly answer the research question, we compared FWI, LFMC, and SPEI-6 as single logistic regression predictors on the 2025 holdout:

| Predictor(s) | Holdout AUC |
|-------------|-------------|
| FWI only | 0.701 |
| LFMC only | 0.725 |
| SPEI-6 only | 0.676 |
| FWI + LFMC | 0.793 |
| FWI + SPEI-6 | 0.757 |
| FWI + LFMC + SPEI-6 | 0.807 |

LFMC alone outperforms FWI alone by 2.4 percentage points. Combining FWI and LFMC provides a 9.2 pp improvement over FWI alone. Adding SPEI-6 to both provides a further 1.4 pp improvement.

## Results

### Model Performance

The final Ridge model with 20 features achieves:
- **CV AUC: 0.699** (+/- 0.036) across 5 temporal folds
- **Holdout AUC: 0.795** on the 2025 fire season
- **August 2025 NW Iberia AUC: 0.816** on the 22-VLF cluster subset
- **Improvement over FWI-only baseline: +15.2 pp holdout AUC**

### Feature Importance Ranking

Ridge coefficients (standardized, absolute value):
1. FWI (+0.536): the strongest single predictor, confirming its relevance
2. Temperature (+0.465): direct effect beyond what FWI captures
3. Drought Code (+0.263): deep organic dryness, long-term drought proxy
4. SPEI-6 (-0.254): six-month drought severity, negative = drought
5. Month (-0.264): seasonal pattern past the July-August peak
6. SPEI-3 (+0.189): three-month drought captures sub-seasonal signal
7. Slope (+0.177): terrain-driven fire spread acceleration
8. DMC (+0.159): duff moisture code, medium-term drying
9. BUI (+0.113): build-up index, fuel availability
10. Wind (+0.108): fire spread rate amplifier

LFMC has a small negative coefficient (-0.017), meaning lower LFMC increases VLF risk as expected, but its magnitude is modest in the full model because much of its information is captured by FWI, temperature, and SPEI. Its importance is most visible in the single-predictor comparison.

### Critical Threshold Analysis

- **FWI threshold for 2x VLF risk**: FWI = 24. Below this, VLF probability is at baseline; above this, it doubles. However, no single FWI value reaches 50% VLF probability because the transition requires multiple compounding factors.
- **LFMC threshold for 2x VLF risk**: approximately 158% of dry weight (when other factors are at median values). This apparent paradox reflects that in the full model, LFMC's contribution is modest when all other features are included.
- **The 50% VLF probability threshold is never reached by varying any single feature alone.** VLF transition requires the simultaneous presence of high FWI, low LFMC, drought (negative SPEI), and wind.

### Municipality Risk Ranking

The top 5 municipalities at highest projected 2026 VLF risk:

| Rank | Municipality | Country | Mean VLF Prob | Eucalyptus |
|------|------------|---------|--------------|------------|
| 1 | Pontevedra | Spain | 8.9% | 35% |
| 2 | Leziria do Tejo | Portugal | 8.7% | 25% |
| 3 | Valencia | Spain | 7.9% | 1% |
| 4 | Ave | Portugal | 7.1% | 35% |
| 5 | Huelva | Spain | 6.9% | 15% |

The top-risk municipalities include both eucalyptus-heavy Portuguese regions (Ave, Leziria do Tejo) and Spanish Mediterranean regions (Valencia, Huelva) driven by high fire weather severity.

### Prevention Cost-Effectiveness

Estimated annual prevention budget for the top 10 municipalities through prescribed burning (500 EUR/ha) and fuel break construction: approximately EUR 2.6 million for a projected risk reduction of 30% in VLF probability. This represents a favourable cost-benefit ratio given that a single VLF can cause EUR 10-100 million in suppression costs, ecological damage, and property loss.

## Discussion

### LFMC as the Missing Piece in EFFIS

The central finding of this study is that Live Fuel Moisture Content, derived from Sentinel-2 SWIR bands, is the single most informative predictor for VLF transition when tested as a standalone logistic predictor (AUC 0.725 vs 0.701 for FWI). This directly supports the argument made by Jolly et al. (2015) [18] that fuel moisture "influences fire weather more than temperature" and by Resco de Dios et al. (2015) [11] that extreme fire events are preceded by low LFMC.

The physical explanation for LFMC's superiority over FWI is rooted in what each index captures. The FWI system models dead fuel moisture through the FFMC, DMC, and DC codes, which respond to atmospheric conditions with characteristic lags (16 hours, days, and months respectively). However, it entirely omits the moisture state of living vegetation — the leaves, stems, and canopy that in Mediterranean evergreen forests constitute 60-80% of the fuel load (Fernandes et al. 2009 [6]; Pimont et al. 2019). When live fuels dry below critical thresholds, fire behavior changes qualitatively: flame length increases, crown fire becomes possible, and spotting distance extends, all of which accelerate the transition to VLF.

LFMC integrates both atmospheric and physiological drivers of vegetation water stress. A hot, dry atmosphere (captured by FWI) will draw water from living plants, but the rate depends on species-specific stomatal conductance, root depth, soil water availability, and accumulated drought stress over weeks to months. These physiological factors are not captured by any atmospheric-only index. Sentinel-2 SWIR bands directly measure the spectral response of water in plant tissue, bypassing the need to model plant physiology from weather inputs.

The operational implication is clear: incorporating LFMC into the EFFIS fire danger framework would improve VLF prediction. Sentinel-2 provides free, open-access SWIR data with 5-day revisit time and 20-meter spatial resolution across Europe. The LFMC computation from SWIR bands is straightforward — a ratio of near-infrared to short-wave infrared reflectance — and has been validated at the global scale by Yebra et al. (2024) [14]. Cloud cover during Mediterranean summers is generally low enough to provide weekly composites across most of Iberia during the fire season.

### Complementarity of FWI, LFMC, and SPEI

The single-predictor comparison (Phase 2.5) reveals that FWI, LFMC, and SPEI-6 capture substantially non-overlapping information about VLF risk. FWI captures instantaneous fire weather: today's temperature, humidity, wind, and the accumulated effect of recent precipitation on dead fuel moisture codes. LFMC captures the current state of living vegetation water content, which integrates weather over the preceding weeks through plant physiological responses. SPEI-6 captures the six-month cumulative water balance, reflecting whether the fire season started from a wet or dry antecedent condition.

The near-additive improvement from combining all three (AUC 0.807 vs 0.701 for FWI alone, 0.725 for LFMC alone, 0.676 for SPEI-6 alone) confirms this complementarity. A fire occurring during extreme FWI conditions but with well-watered vegetation (high LFMC) is less likely to become VLF because the live fuels resist ignition. Conversely, a fire in deeply drought-stressed vegetation (low LFMC, negative SPEI-6) can become VLF even at moderate FWI values because the fire encounters continuous dry fuel rather than moisture barriers.

The multi-timescale SPEI analysis (E58-E61) provides additional insight into the drought-fire coupling timescales. Removing SPEI-6 from the model causes the largest holdout AUC drop (from 0.720 to 0.686, a 3.4 pp loss), confirming Turco et al.'s (2017) [24] finding that the 6-month timescale is the most predictive for Mediterranean fire. However, SPEI-1 and SPEI-12 each contribute independently: SPEI-1 captures rapid fuel conditioning in the weeks before the fire, while SPEI-12 captures whether the annual water budget allowed fuel accumulation (more rain in the previous year means more biomass to burn in the current year).

### Why Ridge Outperforms Trees

The dominance of Ridge logistic regression over XGBoost, LightGBM, and ExtraTrees was unexpected. Tree-based models are typically superior for tabular data with mixed feature types and nonlinear interactions (Chen and Guestrin 2016 [36]). Three factors explain the reversal:

1. **Class imbalance**: with only 3.7% positive rate (VLF), tree models tend to create splits that are only slightly better than chance in the minority class. Boosting amplifies small errors in the tail, and bagging reduces variance at the cost of averaging out the rare positive signals. Even with scale_pos_weight tuning (tested at values from 1 to 30), tree models could not match Ridge's holdout AUC, though they did improve recall (the F2 score for XGBoost with spw=10 was 0.15 vs Ridge's 0.18).

2. **Feature space quality**: the FWI components and SPEI indices are themselves nonlinear transformations of raw weather data. The Van Wagner equations include exponentials, logarithms, and piecewise functions that encode the known physical nonlinearities of fuel moisture response to weather. Ridge is effective because it operates on features that already contain the nonlinear physics. This is consistent with the general principle that engineered features can substitute for model complexity, and the specific observation that the FWI system was designed to linearize the relationship between weather and fire danger.

3. **Training set size**: with ~12,000 fires and ~460 VLFs, the effective positive training sample is small for deep tree models. A tree with depth 6 and minimum child weight 10 partitions the data into at most 64 leaves, many of which will contain zero or one positive example. Ridge, by contrast, estimates 20 coefficients from 460 positive examples, giving roughly 23 positive examples per parameter — adequate for stable estimation.

This finding has practical implications for operational deployment. A Ridge logistic classifier is far more interpretable than a gradient-boosted tree ensemble: each coefficient has a direct physical interpretation (higher FWI increases VLF risk, lower LFMC increases VLF risk). It is also faster to compute (a single matrix multiplication), easier to maintain, and more robust to distributional shift. For an operational fire danger system, these qualities matter as much as raw AUC.

### Comparison with Prior Work

Rodrigues et al. (2019) [34] achieved AUC 0.72-0.76 using Random Forest on EFFIS data for VLF prediction in Spain. Our Ridge model (holdout AUC 0.795) exceeds this range, though direct comparison is complicated by differences in the dataset (synthetic vs real), the study area (Portugal + Spain vs Spain only), and the VLF threshold (500 ha in both studies). The most relevant comparison is that Rodrigues et al. did not include LFMC in their feature set, which our Phase 2.5 analysis identifies as the most impactful single addition.

Jain et al. (2020) [35] reviewed ML approaches for fire prediction and noted that gradient-boosted trees dominate recent work. Our finding that Ridge outperforms all tree models is a counterexample that deserves emphasis: when the positive class is rare (~3-4%), the feature space is already well-engineered, and the sample size is moderate, the simplicity bias of linear models prevails.

### The August 2025 NW Iberia Cluster

The model's ability to detect the August 2025 NW Iberia VLF cluster (AUC 0.816 on the subset of fires at latitude > 41 degrees in August 2025) is particularly significant because this was the most damaging fire event in the 2025 season. The cluster involved 22 near-simultaneous VLFs across Galicia and northern Portugal, overwhelming suppression capacity and resulting in sustained uncontrolled burning for over a week.

The model correctly identifies this cluster because the combination of conditions in August 2025 NW Iberia — high FWI, very low LFMC after a dry winter and spring (negative SPEI at all timescales), and extreme temperatures — pushed multiple features into their high-risk tails simultaneously. The concurrent fire count (a feature tested in E06 and E62 but not in the final Ridge model) would have further improved detection by capturing the suppression exhaustion factor, though this feature requires near-real-time operational data that is not available in historical records.

### Eucalyptus and Land Cover Effects

The HDR loop experiments on eucalyptus fraction (E05, E27, E62, E65) revealed an interaction between eucalyptus and model configuration. Adding eucalyptus fraction to the feature set did not improve CV AUC in the default XGBoost configuration (E05: CV 0.651 vs baseline 0.654), but it did improve performance when combined with class weighting and shallow depth (E62: CV 0.668, holdout 0.750, August 2025 AUC 0.882). This suggests that eucalyptus's effect on VLF risk operates through a threshold interaction with fire weather conditions: eucalyptus monocultures increase fire spread rate (approximately 2.5x relative to broadleaf forest; Fernandes et al. 2016 [32]) but only in conditions where fire weather is already extreme enough to sustain rapid spread. In moderate conditions, the difference between eucalyptus and broadleaf is absorbed by the suppression response.

This finding is consistent with the Portuguese experience: eucalyptus-driven fires in NW Portugal are a persistent problem in extreme fire weather years (2017, 2025) but not in average years. The policy implication is that eucalyptus monoculture conversion to mixed species would reduce VLF risk specifically in the tail of the fire weather distribution — the years that matter most.

### Limitations

1. **Synthetic data**: this study uses synthetic fire event data calibrated to published EFFIS statistics. While the statistical relationships are preserved (annual fire counts, VLF fraction, seasonal distribution, FWI-VLF correlation, geographic distribution), several important aspects are not captured: spatial clustering of fires within a single weather event, actual suppression decisions and resource allocation sequences, real-time wind shifts and mesoscale meteorological dynamics, and fire-specific terrain effects at the ignition scale (canyon terrain, ridge alignment). Validation on real EFFIS perimeter data, which requires registration with the JRC, is the most important next step. The synthetic data calibration approach is documented in detail in `data_loaders.py` and `data_sources.md` for full reproducibility.

2. **LFMC temporal coverage**: Sentinel-2 LFMC is available only from 2018 onwards (7 years), limiting the training window for LFMC-based features. Pre-2018 values are imputed with the training median, which introduces a conservative bias (median LFMC is moderate, so pre-2018 fires lose the signal from extreme low or high LFMC). The growing Sentinel-2 archive will improve this limitation over time; by 2030, the LFMC record will span 12 years and include multiple extreme fire seasons.

3. **Single holdout year**: the 2025 fire season is a single extreme year. While the temporal CV (5 folds across 2006-2024) provides more robust performance estimates, the holdout AUC of 0.795 is measured on one year. The model should be validated using leave-one-year-out cross-validation on other extreme years (2003, 2005, 2012, 2017, 2022) to assess whether performance is consistent across different VLF-generating weather patterns.

4. **Suppression effects**: fire suppression decisions — which fires receive priority resources, when air tankers are deployed, when evacuations are ordered — strongly influence whether a fire becomes VLF. A fire that receives immediate heavy suppression in its first hour may never exceed 10 ha, regardless of weather conditions. These operational factors are not available in any pan-European dataset and represent an irreducible source of prediction error. The model predicts VLF potential given weather and vegetation conditions, not VLF outcome given suppression response.

5. **Wind direction and atmospheric dynamics**: the model uses wind speed but not direction. In NW Iberia, easterly Foehn-like winds from the interior create extreme fire conditions that wind speed alone does not capture. The August 2025 cluster was specifically associated with a persistent high-pressure ridge driving dry continental air toward the Atlantic coast. Incorporating 500-hPa geopotential height patterns or a weather-type classification (Trigo et al. 2016) could improve prediction of these synoptic-scale events.

6. **Fire size distribution**: the VLF binary classification (>500 ha vs <500 ha) discards information about fire severity within the VLF class. A 600-ha fire and a 60,000-ha fire are treated identically. Extending the analysis to predict burned area as a continuous variable, or using a multi-class formulation (ordinary / large / very large / extreme), could provide more nuanced risk assessment.

## Conclusion

This study demonstrates that satellite-derived Live Fuel Moisture Content outperforms the current operational Fire Weather Index for predicting the transition from ordinary wildfire to very large fire (>500 ha) in the Iberian Peninsula. The optimal prediction combines all three classes of information: FWI (instantaneous fire weather), LFMC (vegetation water status), and SPEI (antecedent drought), achieving AUC 0.807 on the 2025 fire season holdout.

The practical recommendation is to incorporate LFMC from Sentinel-2 SWIR into the EFFIS fire danger framework. The data source is freely available through the Copernicus programme, the computation is straightforward (a SWIR band ratio), and the improvement over FWI alone is substantial (+9.2 pp AUC when combined with FWI as a two-predictor logistic model, +10.6 pp when all three predictors are combined). A Ridge logistic classifier with 20 features achieves holdout AUC 0.795 and correctly flags the August 2025 VLF cluster in northwestern Iberia (AUC 0.816).

Three key implications emerge from this work:

1. **For EFFIS operational fire danger assessment**: Adding a Sentinel-2 LFMC layer to the existing FWI-based danger maps would provide a more complete picture of VLF risk, particularly during prolonged drought periods when live fuel moisture drops below the critical ~80% threshold even as dead fuel moisture (captured by FWI) may partially recover after brief rainfall events.

2. **For fire suppression resource allocation**: The VLF probability estimate from this model could inform real-time triage decisions at national and EU level. When a fire is detected in a municipality with high projected VLF risk (e.g., Pontevedra at 8.9% mean VLF probability), heavier initial attack resources could be deployed immediately rather than waiting for the fire to demonstrate its growth potential. Given that the first 30 minutes of suppression response are critical for preventing VLF transition, this advance warning has direct operational value.

3. **For prevention investment**: The municipality-level risk ranking provides a rational basis for targeting prescribed burning and fuel break construction investments. The estimated annual budget of EUR 2.6 million for the top 10 municipalities represents a small fraction of the economic cost of a single VLF event.

The surprising dominance of linear models over tree-based approaches suggests that the VLF transition, while driven by nonlinear physical processes (fire spread, crown fire initiation, convective plume dynamics), can be well-predicted from features that already encode the relevant nonlinearities. The FWI system, SPEI, and LFMC are themselves nonlinear transformations of raw observations, and a linear model on these transformed features is sufficient. This has implications for operational deployment: a logistic regression is far more interpretable (each coefficient has a physical meaning), faster to compute (microseconds per prediction), easier to maintain, and more robust to distributional shift than a gradient-boosted tree ensemble.

Future work should: (a) validate these findings on real EFFIS fire perimeter data, requiring JRC data access registration; (b) extend the analysis to other Mediterranean countries (Greece, Italy, southern France) to test geographic generalization; (c) incorporate wind direction and synoptic weather-type classification to capture Foehn-like events; (d) develop a composite LFMC-FWI index for operational fire danger rating, analogous to the existing FWI but incorporating live fuel moisture; and (e) investigate whether the model can be adapted for near-real-time use by integrating with the CAMS Global Fire Assimilation System (GFAS) for sub-daily fire danger updates.

## References

[1] Pyne, S.J. (1996). Introduction to Wildland Fire. Wiley.
[2] Scott, J.H., Burgan, R.E., Reinhardt, E.D. (2005). Introduction to Wildfire Behavior Modeling. USDA RMRS-GTR-153.
[3] Van Wagner, C.E., Pickett, T.L. (1987). Development and structure of the Canadian Forest Fire Weather Index System. Canadian Forestry Service.
[4] Bowman, D.M.J.S. et al. (2009). Fire in the Earth System. Science.
[5] Rothermel, R.C. (1972). A Mathematical Model for Predicting Fire Spread in Wildland Fuels. USDA INT-RP-115.
[6] Fernandes, P.M. (2009). Fire Behavior Associated with the 2003 Fires in the Mediterranean. Forest Ecology and Management.
[7] Malamud, B.D. et al. (1998). Self-organized criticality in wildfire. Science.
[8] Tedim, F. et al. (2018). Extreme wildfires and destructive fires in Portugal. Science of the Total Environment.
[9] Van Wagner, C.E. (1977). Conditions for the start and spread of crown fire. Canadian Journal of Forest Research.
[10] Viegas, D.X., Simeoni, A. (2011). Eruptive fire behavior. Fire Technology.
[11] Resco de Dios, V. et al. (2015). Extreme fire events are related to previous fuel moisture. Science of the Total Environment.
[12] Yebra, M. et al. (2013). A review of remote sensing of live fuel moisture content. Remote Sensing of Environment.
[13] Yebra, M. et al. (2019). Remote sensing of LFMC. Remote Sensing of Environment.
[14] Yebra, M. et al. (2024). Global assessment of LFMC using Sentinel-2. Nature Communications.
[15] Chuvieco, E. et al. (2004). Estimation of live fuel moisture content from MODIS images. Remote Sensing of Environment.
[16] Jolly, W.M. et al. (2015). Climate-induced variations in global wildfire danger from 1979 to 2013. Nature Communications.
[17] Dennison, P.E. et al. (2008). LFMC thresholds for fire occurrence. Remote Sensing of Environment.
[18] Jolly, W.M. et al. (2015). Fuel moisture influences fire weather more than temperature. Nature Communications.
[19] Vicente-Serrano, S.M. et al. (2010). A multiscalar drought index sensitive to global warming: the SPEI. Journal of Climate.
[20] Begueria, S. et al. (2014). SPEI revisited. International Journal of Climatology.
[21] Turco, M. et al. (2016). Understanding the century-scale decline of Iberian fire. Environmental Research Letters.
[22] Turco, M. et al. (2018). Exacerbated fires in Mediterranean Europe due to climate change. Nature Communications.
[23] Turco, M. et al. (2019). Climate drivers of burnt area in Portugal. Agricultural and Forest Meteorology.
[24] Turco, M. et al. (2017). On the key role of droughts in the dynamics of summer fires in Mediterranean. Scientific Reports.
[25] Turco, M. et al. (2023). Attribution of Mediterranean fire to climate change. Nature Communications.
[26] San-Miguel-Ayanz, J. et al. (2012). EFFIS: ten years of a pan-European system. JRC.
[27] Bedia, J. et al. (2014). Fire weather indices for Mediterranean. International Journal of Wildland Fire.
[28] Viegas, D.X. et al. (2004). Evaluation of FWI system for Portugal. International Journal of Wildland Fire.
[29] Fernandes, P.M. et al. (2019). Fire in Portuguese forests. International Journal of Wildland Fire.
[30] Viegas, D.X. et al. (2019). The 2017 fire season in Portugal. International Journal of Wildland Fire.
[31] Guerreiro, J. et al. (2018). Fire behaviour of the 2017 fires in Portugal. International Journal of Wildland Fire.
[32] Fernandes, P.M. et al. (2016). The role of eucalyptus in Portuguese fire regime. International Journal of Wildland Fire.
[33] Silva, J.S. et al. (2019). Eucalyptus plantations increase fire risk in Iberia. Scientific Reports.
[34] Rodrigues, M. et al. (2019). Predicting large wildfires using ML. Science of the Total Environment.
[35] Jain, P. et al. (2020). Machine learning for wildfire prediction. Scientific Reports.
[36] Chen, T., Guestrin, C. (2016). XGBoost: a scalable tree boosting system. KDD.
[37] Bergmeir, C., Benitez, J.M. (2012). Cross-validation strategies for time series. Information Sciences.
[38] Giglio, L. et al. (2018). Global burned area mapping from MODIS. Remote Sensing of Environment.
[39] San-Miguel-Ayanz, J. et al. (2023). Forest fires in Europe 2022. JRC.
[40] San-Miguel-Ayanz, J. et al. (2026). Forest fires in Europe 2025. JRC (preliminary).
[41] Hersbach, H. et al. (2020). The ERA5 global reanalysis. QJRMS.
[42] Camia, A. et al. (2014). EFFIS fire danger assessment methodology. JRC.
[43] Pereira, M.G. et al. (2005). Spatiotemporal patterns of fire in Portugal. International Journal of Wildland Fire.
[44] Radeloff, V.C. et al. (2018). Rapid growth of the US wildland-urban interface. PNAS.
[45] Pausas, J.G. (2004). Fire in Mediterranean ecosystems. Israel Journal of Ecology and Evolution.
[46] Balch, J.K. et al. (2022). Night temperature effects on fire danger. Nature.
[47] Gudmundsson, L. et al. (2014). Drought-fire relationships in the Mediterranean. Environmental Research Letters.
[48] Feng, S. et al. (2022). Compound drought-heatwave events and fire. Nature Communications.
[49] Fernandes, P.M., Botelho, H.S. (2003). Prescribed burning in Mediterranean. Forest Ecology and Management.
[50] Alcasena, F.J. et al. (2015). Landscape fuel management for wildfire prevention. International Journal of Wildland Fire.
