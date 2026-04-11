# Review Response: Iberian Wildfire VLF Prediction

## Summary of Changes

The review identified 7 CRITICAL, 11 MAJOR, and 5 MINOR issues. We agree with all of them. The paper has been substantially revised with a new title, new framing, and six new experiments. The core finding survives the revision: recent fire activity features outperform seasonal climatology for VLF classification. But the original headline claim -- "fuel moisture outpredicts fire weather" -- has been retracted because it was unsupported.

---

## CRITICAL Issues

### 1. "Fuel moisture proxy" is NOT fuel moisture [CRITICAL]

**Reviewer**: The features labelled "LFMC proxy" are ratios and lags of fire activity, not proxies for fuel moisture. The LFMC abbreviation borrows credibility from the remote-sensing fuel moisture literature.

**Response**: Fully agreed. The feature families have been renamed throughout:
- "Fire Weather Proxy (FWI)" -> "Seasonal Climatology" (historical averages/maxima)
- "Fuel Moisture Proxy (LFMC)" -> "Recent Fire Activity" (ratios and lags)
- "Drought Proxy (SPEI)" -> "Cumulative Season Stress" (year-to-date accumulations)

The paper now explicitly states: "None of these features are proxies for fire weather, fuel moisture, or drought in any physically meaningful sense. They are all derived from fire activity data."

### 2. AUC 1.000 on 68 holdout observations from a single extreme year [CRITICAL]

**Reviewer**: Perfect AUC on 68 observations from a single extreme year is not meaningful validation.

**Response**: Agreed. The paper now:
- Presents holdout AUC 1.000 as "a single favorable test case" rather than a general result
- Adds per-year AUC analysis (Section 4.4): XGBoost achieves AUC > 0.977 in every test year (2015-2025), showing consistent performance not driven by a few extreme years
- Adds 95% bootstrap confidence intervals on the predictor comparison
- Notes the small sample size explicitly in the limitations

### 3. Predictor comparison uses Ridge, not tournament-winning XGBoost [CRITICAL]

**Reviewer**: The predictor comparison should use XGBoost, not Ridge.

**Response**: We now report the predictor comparison with both Ridge and XGBoost (Section 4.3, Table). The finding is robust:
- Ridge: Recent fire activity AUC 0.952, seasonal climatology AUC 0.809
- XGBoost: Recent fire activity AUC 0.972, seasonal climatology AUC 0.751

With XGBoost, the seasonal climatology features actually perform *worse* (0.751) than with Ridge (0.809), while recent fire activity features improve (0.972 vs. 0.952). The advantage is model-independent.

### 4. Multi-week fire persistence likely explains lagged features [CRITICAL]

**Reviewer**: The lagged features may simply detect ongoing fires. What fraction of VLF weeks are followed by another VLF week?

**Response**: New Section 4.1 (Fire Persistence Analysis) reports:
- 59 of 125 VLF weeks (47%) are persistence events (preceded by another VLF week)
- Week-to-week burned area autocorrelation: rho = 0.387 (pooled), 0.285 (Portugal), 0.456 (Spain)
- Trivial persistence baseline (area_lag1 alone): AUC 0.814

New Section 4.5 (Onset-Only Evaluation) addresses this directly by removing persistence VLF weeks:
- Ridge recent fire activity on onset-only: AUC 0.921 (vs. 0.952 on all VLF)
- Ridge seasonal climatology on onset-only: AUC 0.799 (vs. 0.809 on all VLF)
- The recent fire activity advantage persists: 0.921 vs. 0.799 for onset-only

Conclusion: Persistence inflates the overall metric by about 3 percentage points for Ridge, but the signal extends well beyond simple fire persistence.

### 5. No actual fire weather data used [CRITICAL]

**Reviewer**: Despite claiming to outpredict fire weather, no temperature, humidity, wind, or FWI data was used.

**Response**: Fully agreed. The paper has been fundamentally reframed:
- New title: "Lagged Fire Activity Outperforms Seasonal Climatology for VLF Week Classification"
- New Section 5.2: "What This Study Does Not Show" -- explicitly states no fire weather data was used
- Limitation 1 elevated to most prominent position
- Abstract now states: "no actual fire weather data was used in this study"
- Future work item 1: "Integrate actual fire weather data"

We attempted to obtain FWI data from EFFIS but the Daily Severity Rating endpoint returned 404 errors, and the FWI data available through EFFIS is gridded (8 km ECMWF resolution) requiring country-level spatial aggregation from ERA5. This is identified as essential future work.

### 6. Combining all features HURTS Ridge [CRITICAL]

**Reviewer**: Adding features to a regularized linear model should not degrade performance. This anomaly is unexplained.

**Response**: Section 4.3 now explains this: "The anomaly that combining all features hurts Ridge performance (AUC 0.920 < 0.952) likely reflects multicollinearity: the seasonal climatology features in the full baseline partially overlap with the month encodings already present in the recent fire activity set, and the increased dimensionality relative to the small training set (as few as 204 observations for the earliest folds) degrades Ridge regularization. With XGBoost, which handles multicollinearity through tree splitting, the full baseline achieves the best performance (AUC 0.993)."

### 7. "LFMC outpredicts FWI" claim unsupported [CRITICAL]

**Reviewer**: Neither actual LFMC nor actual FWI was computed.

**Response**: The claim has been fully retracted. The new title, abstract, and all sections use honest terminology. The paper now explicitly acknowledges this was the most serious conceptual error in the original version.

---

## MAJOR Issues

### 8. Country-week aggregation too coarse for operational relevance [MAJOR]

**Response**: Section 5.5 now states: "A country-level weekly indicator is not an operational alert system. Operational fire management requires spatial specificity, temporal precision, and calibrated probabilities. This study provides none of these." Subnational analysis identified as future work.

### 9. Weekly temporal resolution misses the phenomenon [MAJOR]

**Response**: Acknowledged in Limitation 2. Sub-weekly analysis with daily EFFIS detections identified as future work item 2.

### 10. VLF threshold of 5,000 ha not justified [MAJOR]

**Response**: New Section 4.6 (Threshold Sensitivity) tests 1,000, 2,500, 5,000, 10,000, and 20,000 ha thresholds. The recent fire activity advantage is robust across all thresholds and increases for more extreme thresholds (AUC gap widens from 10 to 25 percentage points). Limitation 7 acknowledges the threshold is not based on an established operational definition.

### 11. Combining predictors hurts performance -- unexplained [MAJOR]

**Response**: See response to CRITICAL 6 above.

### 12. "Significantly outperforming" without significance test [MAJOR]

**Response**: 95% bootstrap confidence intervals now provided. The CIs for recent fire activity [0.934, 0.968] and seasonal climatology [0.768, 0.848] do not overlap, confirming the difference is statistically significant. The word "significantly" in the abstract has been replaced with the specific CI values.

### 13. Abstract: "fire weather proxies" misnomer [MAJOR]

**Response**: All proxy terminology has been replaced with honest descriptors throughout.

### 14. Operational implications overclaimed [MAJOR]

**Response**: Section 5.5 now uses appropriate caveats: "this suggestion is modest" and "this study provides none of" the operational requirements.

### 15-17. Missing experiments (confidence intervals, XGBoost comparison, threshold sensitivity, per-year AUC) [MAJOR x4]

**Response**: All four experiments have been run and reported:
- 95% bootstrap CIs (Section 4.3)
- XGBoost predictor comparison (Section 4.3)
- Threshold sensitivity (Section 4.6)
- Per-year AUC (Section 4.4)

### 18. Missing autoregressive fire modeling literature [MAJOR]

**Response**: Added citations to Preisler et al. (2004), Taylor et al. (2013), and Turco et al. (2013). Section 5.4 now discusses autoregressive fire modeling context.

---

## MINOR Issues

### 19. Feature construction details insufficient [MINOR]

**Response**: Fire season defined as weeks 22-42 (Section 3.2, data_loaders.py line 210-211). Feature definitions clarified in methods.

### 20. Rodrigues et al. (2019) citation misattributed [MINOR]

**Response**: Description corrected in Section 5.4 to reflect the actual paper content (geographically weighted logistic regression of fire causes, not RF VLF prediction).

### 21-23. Subnational analysis, calibration, SHAP interaction values [MINOR]

**Response**: All three identified as future work items in Section 5.6.

---

## Missing Experiments from Review (Checklist)

| Experiment | Status | Section |
|-----------|--------|---------|
| Include actual fire weather data | Not possible via API (404); identified as future work | 5.2, 5.6 |
| Threshold sensitivity | Done: 1K-20K ha, 5 thresholds | 4.6 |
| XGBoost predictor comparison | Done: all 4 families | 4.3 |
| Confidence intervals | Done: 95% bootstrap CIs | 4.3 |
| Autocorrelation analysis | Done: rho=0.387, persistence baseline AUC=0.814 | 4.1 |
| Per-year AUC | Done: all 11 test years | 4.4 |
| Subnational analysis | Identified as future work | 5.6 |
| Calibration analysis | Identified as future work | 5.6 |
| SHAP interaction values | Identified as future work | 5.6 |
| Multi-week persistence analysis | Done: 47% persistence, onset-only eval | 4.1, 4.5 |
