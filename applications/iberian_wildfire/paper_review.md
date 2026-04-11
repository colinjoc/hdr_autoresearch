# Adversarial Peer Review: "Recent Fire Activity Dynamics Outpredict Fire Weather Indices for Very Large Fire Weeks on the Iberian Peninsula"

**Reviewer recommendation: Major Revision**

---

## 1. Claims vs Evidence

### AUC 0.993 / 1.000 is almost certainly overfitting on a tiny dataset [CRITICAL]

The model achieves AUC 0.993 on temporal CV and AUC 1.000 on the 2025 holdout. These numbers are extraordinary for any ecological prediction task and should trigger immediate suspicion of data leakage or overfitting. The dataset has only 1,456 observations (14 years x 2 countries x 52 weeks), with a 13.1% positive rate (~191 VLF weeks total). The temporal CV trains on all years before the test year, meaning for the earliest test year (2015) the model sees only 3 years of training data. With XGBoost at depth=6, the model has enormous capacity relative to the data volume.

The holdout AUC = 1.000 means the model perfectly separates 14 VLF weeks from 54 non-VLF weeks in 2025 -- a single year that happened to be a severe fire year. On 68 observations, this could occur by chance with a reasonably separable distribution and does not warrant the strong claims made. The paper provides no confidence interval on the holdout AUC.

### The "fuel moisture proxy" is not a fuel moisture proxy [CRITICAL]

The paper names its predictor family "Fuel Moisture Proxy (LFMC)" but these features are ratios and lags of fire activity itself (area_ha / area_ha_avg, fires / fires_avg, lagged burned area). These are not proxies for live fuel moisture content. They are autoregressive features of the target variable: current fire activity predicting future fire activity. The paper even uses the LFMC abbreviation, borrowing credibility from the remote-sensing fuel moisture literature (Yebra et al. 2019, 2024), despite measuring nothing about fuel moisture.

This mislabeling is not cosmetic. The paper's headline claim is "fuel moisture outpredicts fire weather." A more accurate statement is "lagged fire activity outpredicts seasonal fire climatology" -- which is trivially expected because fire events are temporally autocorrelated. A big fire week is more likely to be followed by another big fire week because the same fire often burns across weekly boundaries and because the same weather system persists for days.

### The predictor comparison uses Ridge logistic regression, not the tournament-winning XGBoost [MAJOR]

Table in Section 4.3 (predictor family comparison) uses Ridge logistic regression. The tournament (Section 4.2) shows XGBoost with AUC 0.993, far above Ridge's 0.926. The predictor comparison therefore answers: "Which predictor family works best in a linear model?" -- not "Which predictor family is most informative in general." Tree models can extract nonlinear interactions from the fire weather features that Ridge cannot. The predictor comparison should be repeated with XGBoost, or the paper should explicitly state that the conclusion is conditional on a linear model.

### Combining predictors *hurts* performance in the linear model [MAJOR]

Table 4.3 shows that "All three combined" (AUC 0.920) scores lower than fuel moisture alone (0.952) and lower than the full baseline (0.926). This is paradoxical -- adding features to a regularized linear model should not systematically degrade performance unless there is severe multicollinearity or the model is overfitting on 952 observations. The paper does not investigate this anomaly. It could indicate that the LFMC proxy family's apparent superiority is fragile and driven by the specific regularization balance in Ridge, not a robust finding.

---

## 2. Scope vs Framing

### Title claims "outpredict" but comparison is not fair [CRITICAL]

The title states that "fire activity dynamics outpredict fire weather indices." But the fire weather proxy is not the FWI -- it is the seasonal climatology of fire activity (historical averages and maxima). The paper does not include any actual fire weather data (temperature, humidity, wind, FWI values). The comparison is between "how much is burning now vs. how much usually burns this week" versus "how much usually burns this week." The former obviously wins because it has access to the current observation; the latter is a naive seasonal baseline. Claiming this "outpredicts fire weather" is misleading because no fire weather data was tested.

### Country-week aggregation is too coarse for operational relevance [MAJOR]

Aggregating to entire countries eliminates the spatial information that fire managers need. Portugal and Spain are large, heterogeneous countries. A VLF in the Algarve and a VLF in Galicia have different causes, fuels, and management contexts. The paper acknowledges this (Limitation 2) but still frames the results as having "implications for fire management" and proposes "anomaly-based alert triggers." No fire agency would implement a country-level weekly alert system.

### Weekly temporal resolution misses the phenomenon of interest [MAJOR]

VLF events typically develop over 1-3 days, not weeks. Aggregating to weekly data means a week with 6 days of zero fire and one day of 6,000 ha is treated identically to a week with steady 800 ha/day burning. The lagged features (previous week's area) may simply capture multi-week fires rather than providing early warning. The paper acknowledges this (Limitation 1) but does not discuss the implications for the operational "earlier and more accurate VLF warnings" claim in the abstract.

---

## 3. Reproducibility

### EFFIS API access and data format are well-specified [POSITIVE]

The data source, API endpoint, time range, and variables are clearly described. The GWIS S3 archive is also specified. This is a strength.

### The VLF threshold of 5,000 ha is not justified [MAJOR]

The choice of 5,000 ha as the VLF threshold is presented without justification beyond "13.1% of fire-season country-weeks." Different thresholds (1,000, 10,000, 20,000 ha) would change the positive rate, class balance, and likely the ranking of predictor families. No sensitivity analysis to threshold choice is provided.

### Feature construction details are insufficient for some features [MINOR]

"Fire season indicator" and "fire season week number" are not precisely defined. What weeks constitute "fire season"? The paper mentions weeks 15-48 for some analyses but it is unclear whether the indicator is 1 for weeks 15-48 and 0 otherwise, or uses a different definition.

---

## 4. Missing Experiments

1. **Include actual fire weather data.** The paper claims fire activity outpredicts fire weather but never uses fire weather data. ERA5 reanalysis provides temperature, humidity, wind, and precipitation for the study period. At minimum, country-averaged weekly FWI (available from EFFIS) should be included to test the titular claim. Without this, the central claim is unsupported. [CRITICAL]

2. **Threshold sensitivity analysis.** Repeat the predictor comparison at 1,000, 2,500, 5,000, 10,000, and 20,000 ha thresholds to determine whether the finding is robust to definition choices. [MAJOR]

3. **XGBoost predictor comparison.** Repeat the predictor family comparison (Table 4.3) with XGBoost instead of Ridge to determine whether the LFMC proxy superiority holds for nonlinear models. [MAJOR]

4. **Confidence intervals on all metrics.** With 11 temporal CV folds, bootstrap confidence intervals on AUC, F2, and the predictor comparison are essential. The difference between AUC 0.952 and 0.809 may or may not be significant given the small number of positive cases per fold. [MAJOR]

5. **Autocorrelation analysis.** The lagged features create temporal autocorrelation by design. What is the week-to-week autocorrelation of burned area? If rho > 0.5, the "fuel moisture proxy" is largely a persistence forecast, and the paper should benchmark against a simple autoregressive model (predict this week's area = last week's area). [CRITICAL]

6. **Leave-one-year-out analysis with per-year metrics.** The temporal CV averages across all test years. Reporting per-year AUC would reveal whether the model performs well consistently or if a few extreme years (2017, 2025) dominate the average. [MAJOR]

7. **Subnational analysis.** NUTS-2 or NUTS-3 level data is available from GWIS. Even a feasibility analysis showing whether the approach works at regional scale would strengthen the operational claims. [MINOR]

8. **Calibration analysis.** Are the predicted VLF probabilities well-calibrated? A reliability diagram would show whether "P(VLF) = 0.3" actually corresponds to 30% of such weeks being VLF. [MINOR]

9. **Feature interaction analysis.** The paper claims "nonlinear feature interactions" explain the Ridge-to-XGBoost gap. SHAP interaction values from the XGBoost model would identify which specific interactions matter. [MINOR]

10. **Multi-week fire persistence analysis.** How many VLF weeks are followed by another VLF week? If the answer is "most of them," then the lagged features are simply detecting ongoing fires, not predicting new VLF onset. This distinction is operationally crucial: predicting that a fire that is already burning will continue burning is not useful warning. [CRITICAL]

---

## 5. Overclaiming

### "Perfect identification (AUC 1.000) of all 14 VLF weeks in the 2025 holdout year" [CRITICAL]

Calling AUC 1.000 on 68 observations "perfect identification" implies the model has solved the VLF prediction problem. This is a single year, and 2025 was an extreme fire year where VLF weeks were likely very obviously extreme. The paper should present this as a single favorable test case, not a general result.

### "Implications for fire management: anomaly-based alert triggers" [MAJOR]

The paper proposes a practical alert system based on country-level weekly fire activity ratios. No fire management agency operates at this resolution. The gap between "country-week AUC is high" and "this could provide earlier and more accurate VLF warnings" is enormous and unbridged. The paper does not discuss lead time (how many days before a VLF does the anomaly signal appear?), spatial specificity, or operational false alarm tolerance.

### "Significantly outperforming fire weather alone" [MAJOR]

The word "significantly" implies a statistical test. No significance test is presented. The comparison is between AUC 0.952 and 0.809 from a single Ridge logistic regression with no confidence intervals.

### Abstract: "fire weather proxies based on historical fire danger patterns" [MAJOR]

The fire weather proxy features are not fire weather data. They are historical fire activity statistics (average burned area for this week, maximum fire count). Calling these "fire weather proxies" conflates cause (weather) with effect (fire activity). Weather-driven fire danger indices (FWI, Keetch-Byram, etc.) are fundamentally different from historical fire occurrence statistics.

---

## 6. Literature Positioning

### Missing the operational fire danger literature [CRITICAL]

The paper's central claim is about outperforming fire weather indices, but the literature review barely engages with the operational fire danger research community:
- Vitolo et al. (2020) on EFFIS operational performance
- Bedia et al. (2018) on FWI calibration for Mediterranean
- Turco et al. (2018) on the relationship between FWI and burned area in Spain
- De Groot et al. (2015) on extending FWI to global applications
- Ruffault et al. (2018) on FWI limitations in Mediterranean

Without engaging this literature, the paper cannot credibly claim its approach outperforms fire weather indices.

### Rodrigues et al. (2019) citation appears to be misattributed [MINOR]

The paper states Rodrigues et al. (2019) applied Random Forest to VLF prediction in Spain with AUC 0.72-0.76. The reference list describes this paper as "Modeling the spatial variation of the explanatory factors of human-caused wildfires in Spain using geographically weighted logistic regression." If this is the correct paper, it uses logistic regression, not Random Forest, and studies spatial variation of fire causes, not VLF prediction. The citation or the description in the text may be incorrect.

### Missing autoregressive fire modeling literature [MAJOR]

The paper's best predictor family is essentially an autoregressive model of fire activity. The literature on autoregressive and time-series approaches to fire prediction is substantial:
- Preisler et al. (2004) on probability-based fire occurrence models
- Taylor et al. (2013) on time-series forecasting of wildfire
- Turco et al. (2013) on fire weather and fire activity relationships in Mediterranean

These would provide essential context for the finding that lagged fire activity is predictive.

---

## Severity Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 7 |
| MAJOR    | 11 |
| MINOR    | 5 |

This paper has serious conceptual problems that go beyond typical revision issues. The central claim -- that fuel moisture outpredicts fire weather -- is not supported because (a) no fire weather data was actually used, (b) the "fuel moisture proxy" measures fire activity, not fuel moisture, and (c) the predictor comparison uses a linear model while the tournament shows nonlinear models dominate. The AUC 1.000 holdout result on 68 observations from a single extreme year is presented as if it validates the approach when it primarily reflects the small sample and the extremity of 2025. The paper has genuine potential: the question of what signals best predict VLF weeks is operationally important, and the temporal CV methodology is sound. But the framing needs a fundamental overhaul. The paper should be recast as: "Lagged fire activity features outperform seasonal climatology baselines for VLF classification at the country-week level" -- a defensible but much less exciting finding. Including actual FWI data is a prerequisite for the current title. Major revision required, with the expectation that the central claims may need to be substantially revised.
