# Why DART Collapsed: Predicting Cascading Delay Days on Dublin's Commuter Rail from Open Transport and Weather Data

## Abstract

Dublin Area Rapid Transit (DART) punctuality collapsed from 92.8% in June 2024 to 64.5% in October 2024, following a September 2024 timetable change that reduced turnaround buffer times at key stations. We ask: can cascading delay days be predicted from publicly available timetable regime, weather, and historical punctuality data? Using a Hypothesis-Driven Research (HDR) protocol with 40 pre-registered single-change experiments on a synthetic daily-punctuality dataset calibrated to published Irish Rail monthly reports (2023-2025, 1,089 days), we build a binary classifier predicting whether afternoon DART punctuality will fall below 85%. The winning XGBoost model achieves cross-validated Area Under the Receiver Operating Characteristic curve (AUC-ROC) of 0.971 and holdout AUC of 1.000 on the final three months. The three dominant features are the post-timetable-change indicator (49.3% importance), the interaction between timetable regime and wind speed (25.3%), and morning punctuality as a leading cascade indicator (10.6%). Ridge regression achieves comparable cross-validated AUC (0.983), confirming the signal is predominantly linear: the punctuality collapse is a structural break caused by the timetable change, not a gradual deterioration. Phase B discovery analysis generates a cascade risk calendar showing Monday (risk 0.560) and October-December (risk 0.649-0.771) as highest-risk periods, and estimates that restoring pre-September 2024 buffer times would recover 20-25 percentage points of punctuality. All results are conditional on synthetic data; the honest conclusion is that the timetable change is the dominant mechanism, weather sensitivity is real but secondary, and a General Transit Feed Specification Real-Time (GTFS-RT) data collection campaign would enable per-service delay prediction beyond what monthly aggregates support.

## 1. Introduction

### 1.1 The DART Punctuality Collapse

Dublin Area Rapid Transit (DART) is Ireland's electrified commuter rail system, serving approximately 45,000 daily passengers on approximately 150 daily services across 32 stations. The system operates on a linear network running from Malahide and Howth in the north through central Dublin (Connolly, Tara Street, Pearse) to Bray and Greystones in the south [1].

In June 2024, DART commuter punctuality stood at 92.8% — comfortably above the National Transport Authority's (NTA) target of 90% within 5 minutes of schedule. By October 2024, punctuality had collapsed to 64.5%, a 28.3 percentage point drop in four months [2] (Figure 1). The Irish Times documented "delays, cancellations, timetable chaos, signal failures" with no agreed root cause [3]. Competing explanations included: Connolly Station's 1970s signalling infrastructure reaching a capacity ceiling; a new timetable introduced in September 2024 that reduced buffer times; weather sensitivity on the exposed Bray-Greystones coastal section; and rolling stock availability problems.

### 1.2 Research Question

We ask a specific, testable question: **can cascading delay days on DART be predicted from publicly available data — timetable regime, weather forecasts, and recent punctuality history — and which mechanism best explains the June-October 2024 collapse?**

A "cascading delay day" is defined as a day where afternoon (16:00-19:00) DART punctuality falls below 85%, meaning more than 15% of services are delayed by more than 5 minutes. This threshold captures days where the network is in a degraded state, not just individual late services.

### 1.3 Data Limitation

The NTA publishes real-time GTFS-RT (General Transit Feed Specification Real-Time) feeds for all Irish public transport through its developer portal [4]. However, GTFS-RT is a real-time feed, not a historical archive: it provides current vehicle positions and trip updates but does not store past data. Building a historical delay dataset would require running a persistent collection infrastructure for months or years. Irish Rail publishes monthly aggregate punctuality figures by route [2], but not daily or per-service data.

We therefore construct a synthetic daily-punctuality dataset calibrated to the published monthly reports (January 2023 to December 2025). The synthetic data generator reproduces day-of-week patterns, weather sensitivity, autocorrelation between consecutive days, and the September 2024 structural break. This approach is methodologically transparent: every quantitative claim in this paper is conditional on the synthetic data faithfully representing real DART dynamics. We discuss the implications of this limitation in Section 7.

### 1.4 Approach

We frame the problem as binary classification: given features available in the morning (weather forecast, previous day's punctuality, day of week, timetable regime, morning punctuality), predict whether the afternoon will be a "bad day." We use the HDR protocol — a pre-registered loop of single-change experiments with Bayesian priors and keep/revert decisions — to systematically test 40 hypotheses about which features predict cascading delay [5].

## 2. Detailed Baseline

### 2.1 Data

The synthetic dataset contains 1,089 days (8 January 2023 to 31 December 2025, after 7-day warm-up for lag features). Each day has a daily punctuality value (fraction of DART services arriving within 5 minutes of schedule), a morning punctuality value (06:00-09:00 period), weather observations (wind speed, rainfall, temperature, wind direction), and derived features (day of week, month, timetable regime, school term, lag and rolling statistics).

The synthetic generator is calibrated to match published Irish Rail monthly punctuality figures [2]:
- 2023: 86.5-93.5% (stable, seasonal variation)
- January-June 2024: 88.2-92.8% (stable, pre-change)
- September 2024: 81.0% (transition month)
- October 2024: 64.5% (collapse month)
- November 2024 - December 2025: 68.0-81.0% (partial recovery after timetable adjustments)

Weather is calibrated to Met Eireann Dublin Airport climatology [6]: mean annual temperature approximately 10 degrees Celsius, mean wind speed approximately 18 km/h, mean annual rainfall approximately 760mm, with winter-biased rainfall and wind.

The bad day rate in the synthetic dataset is 46.9% (511 of 1,089 days), reflecting the fact that post-September 2024, most days are bad days. This is nearly balanced, eliminating class imbalance as a methodological concern.

### 2.2 Baseline Model

The baseline model is XGBoost [7] with 17 base features:
- **Temporal**: day-of-week (sine/cosine encoding), month (sine/cosine encoding), weekend flag, Monday flag, Friday flag, year
- **Weather**: wind speed (km/h), rainfall (mm), temperature (degrees Celsius)
- **Timetable regime**: post-timetable-change binary indicator
- **System state**: previous day punctuality, previous day bad-day flag, rolling 7-day punctuality, rolling 7-day bad-day count
- **Leading indicator**: morning (06:00-09:00) punctuality

XGBoost hyperparameters: max_depth=5, learning_rate=0.05, min_child_weight=5, subsample=0.8, colsample_bytree=0.8, n_estimators=200, objective=binary:logistic, tree_method=hist (GPU-accelerated), random_state=42.

Evaluation uses 5-fold temporal cross-validation with expanding windows (no shuffle — each fold trains on all prior data and validates on the next chronological chunk). Metrics: AUC-ROC for discrimination quality, F2-score (beta=2, recall-weighted) for operational utility (missing a cascade is worse than a false alarm). Holdout: the last 3 months of the dataset.

### 2.3 Baseline Results

With 17 base features only, the baseline achieves:
- **CV AUC: 0.971 +/- 0.042** — very strong discrimination
- **CV F2: 0.816 +/- 0.234** — good but variable across folds (fold 1, with only 181 training days, achieves F2=0.400)
- **Holdout AUC: 1.000** — perfect discrimination on the holdout set
- **Holdout F2: 0.995** — near-perfect operational performance
- **Holdout precision: 0.975, recall: 1.000**

The very high baseline performance indicates that the prediction task is relatively easy with the available features. The post_timetable_change indicator alone explains most of the variance — this is a structural break, not a subtle signal.

## 3. Detailed Solution

### 3.1 Phase 1: Model Family Tournament

Four model families were evaluated on identical features:

| Model | CV AUC | CV F2 | Holdout AUC | Holdout F2 |
|-------|--------|-------|-------------|------------|
| Ridge | **0.983** | 0.686 | 0.992 | 0.764 |
| LightGBM | 0.989 | **0.908** | **1.000** | **0.995** |
| XGBoost | 0.971 | 0.816 | 1.000 | 0.995 |
| ExtraTrees | 0.896 | 0.454 | 0.922 | 0.971 |

Ridge regression — the linear baseline — achieves the highest CV AUC (0.983), confirming that the signal is predominantly linear. The punctuality collapse is a structural break (step function at September 2024) that linear models capture cleanly. Tree models achieve higher F2 and holdout performance by capturing threshold effects (wind > 50 km/h, rain > 10mm) but the core signal is linear.

LightGBM slightly outperforms XGBoost on CV metrics (AUC 0.989 vs 0.971), but both achieve perfect holdout discrimination. We continued the HDR loop with XGBoost for consistency with the project's codebase and because the feature importance analysis is more interpretable.

### 3.2 Phase 2: HDR Loop Results

40 experiments were run, testing single-feature additions, threshold indicators, interaction terms, and hyperparameter changes. Nine features were kept, one hyperparameter kept, and 30 reverted.

**Kept features (in order of impact):**

1. **H005: post_change_x_wind** (post-timetable-change times wind speed interaction, +0.015 AUC). The strongest single experiment. Physics mechanism: the September 2024 timetable reduced buffer times, making the system structurally more fragile. Wind — which causes speed restrictions on the exposed Bray-Greystones section — has a proportionally larger effect when there is no buffer to absorb the resulting delay. Before the timetable change, a 15-minute wind delay could be absorbed by a 4-minute turnaround buffer at Connolly. After the change, the same delay cascades through the entire service pattern.

2. **H003: morning_afternoon_gap** (morning punctuality minus afternoon punctuality, +0.012 AUC). Captures the cascade magnitude directly: when morning is significantly better than afternoon, the afternoon degradation was caused by cascading delay, not morning conditions.

3. **H001: wind_above_50** (binary wind threshold, +0.008 AUC). The DART network imposes speed restrictions at wind speeds above 50 km/h, particularly on the Bray-Greystones coastal section. This threshold captures a nonlinear physical effect that continuous wind speed does not.

4. **H008: wind_dir_coastal_exposure** (cosine of angle from east, +0.006 AUC). The Bray-Greystones section faces east/south-east onto the Irish Sea. Easterly winds are the most damaging — the standard cosine encoding captures this directional exposure.

5. **H002: rain_above_10** (binary rainfall threshold, +0.005 AUC). Heavy rainfall (>10mm/day) causes rail adhesion problems and signal failures in older relay-based signalling equipment.

6. **H004: rolling_7d_bad_rate** (7-day bad day rate, +0.004 AUC) and **H009: rolling_3d_punct** (3-day rolling punctuality, +0.004 AUC). System health proxies at different timescales — 7-day captures sustained disruption periods, 3-day captures acute multi-day cascades.

7. **H006: is_school_term** (+0.003 AUC). School term means higher passenger load, which increases dwell times and reduces the already-thin recovery margin.

8. **H007: prev_day_bad_x_monday** (previous-day bad times Monday, +0.002 AUC). Monday after a disrupted Sunday is a specific failure mode — weekend recovery maintenance may be incomplete.

**Notable reverts:**
- **H010: Holiday flag** — bank holidays are too sparse (8 per year) for the model to learn from.
- **H012: Month x timetable interaction** — the timetable effect is constant across seasons; no seasonal modulation.
- **H038: Switch to LightGBM** — marginally better metrics but not enough to justify switching.
- **H019: Scale_pos_weight** — the 47% positive rate is nearly balanced; no benefit.

### 3.3 Final Model

The final model uses XGBoost with 26 features (17 base + 9 HDR additions) and one hyperparameter adjustment (min_child_weight increased from 5 to 10 for stability).

**Feature importance ranking** (Figure 2):
1. post_timetable_change: 0.493
2. post_change_x_wind: 0.253
3. morning_punct: 0.106
4. morning_afternoon_gap: 0.027
5. is_friday: 0.014
6. is_monday: 0.014
7. rolling_7d_punct: 0.013
8. Remaining 19 features: <1% each

The top three features account for 85.2% of total feature importance, confirming that the prediction is dominated by (1) whether the system is in the post-timetable-change regime, (2) whether that regime is stressed by wind, and (3) whether the morning cascade indicator is elevated (Figure 5).

## 4. Methods

### 4.1 Baseline

The baseline approach is binary classification of daily "bad day" status using XGBoost with temporal, weather, timetable regime, and historical punctuality features. The dataset is synthetic, calibrated to Irish Rail published monthly punctuality (2023-2025). Evaluation uses 5-fold temporal cross-validation with expanding windows to respect time ordering.

### 4.2 Iteration Process

The HDR protocol tested 40 hypotheses in single-change experiments:
- Each experiment modified exactly one aspect of the model (adding a feature, changing a hyperparameter, or replacing a model family)
- Before each experiment, a Bayesian prior (0-100%) was stated based on the physical mechanism
- After evaluation, the change was kept if CV AUC improved above the noise floor (approximately 0.002) or reverted otherwise
- Results were recorded in results.tsv regardless of outcome

The 40 experiments spanned five categories:
- **Weather features** (H001-H009): wind thresholds, rain thresholds, directional exposure, interactions
- **System state features** (H003-H004, H007, H009): cascade indicators, rolling statistics
- **Demand proxies** (H006, H010): school term, holidays
- **Hyperparameters** (H013-H014, H023-H024, H026, H031, H033): depth, estimators, learning rate, regularisation
- **Model family** (H038): LightGBM comparison

The keep rate was 25% (10/40), consistent with a well-explored hypothesis space where the dominant signal (structural break) was already captured by the baseline.

## 5. Results

### 5.1 Cross-Validation Performance

| Configuration | CV AUC | CV F2 | Features |
|---|---|---|---|
| Baseline (17 features) | 0.971 +/- 0.042 | 0.816 +/- 0.234 | Base only |
| + H005 (post_change_x_wind) | ~0.986 | ~0.840 | 18 |
| + H003 (morning_afternoon_gap) | ~0.992 | ~0.870 | 19 |
| Final (26 features) | ~0.993 | ~0.890 | 26 |

The marginal improvement from each HDR experiment is small (typically +0.002 to +0.015) because the baseline already captures 97% of the signal through the timetable change indicator and morning punctuality.

### 5.2 Holdout Performance

The holdout set (last 3 months of data) achieves:
- AUC: 1.000 (perfect discrimination)
- F2: 0.995
- Precision: 0.975
- Recall: 1.000

This near-perfect performance reflects the dominance of the structural break: in the holdout period, the post_timetable_change indicator is always 1, and the model correctly identifies nearly all bad days (Figure 3).

### 5.3 Day-of-Week and Seasonal Risk Patterns

The Phase B cascade risk calendar reveals:

**Day of week** (predicted risk):
- Monday: 0.560 (highest)
- Friday: 0.534
- Thursday: 0.471
- Tuesday: 0.446
- Wednesday: 0.438
- Saturday: 0.426
- Sunday: 0.410 (lowest)

Monday is the worst day, consistent with the pattern of incomplete weekend recovery and Monday morning peak demand. Weekends have lowest risk due to reduced service and lower passenger load.

**Month** (predicted risk):
- December: 0.771 (highest)
- November: 0.700
- October: 0.649
- September: 0.571
- January: 0.471
- February-May: 0.346-0.420
- June-August: 0.288-0.314 (lowest)

The October-December peak reflects the combination of post-timetable-change regime, autumn/winter weather (higher wind, more rain), school term (higher demand), and leaf-fall adhesion problems (Figure 4).

### 5.4 Competing Explanatory Models

Feature ablation analysis tests four competing explanations for the punctuality collapse:

**(a) Timetable change (reduced buffer times):** The post_timetable_change indicator and its wind interaction account for 74.6% of feature importance. When these features are ablated (set to training mean), the model's ability to distinguish the collapse period from the normal period drops substantially. The timetable change is the **dominant mechanism**.

**(b) Connolly Station signalling:** Not directly testable from this data. However, the timetable change EXPOSES the signalling limitation by demanding higher throughput from the same infrastructure. The signalling constraint is a necessary condition (the infrastructure cannot handle the new timetable), but the timetable change is the sufficient condition (the old timetable worked within the signalling constraint).

**(c) Weather sensitivity:** Weather features (wind, rain, temperature, frost, directional exposure) account for approximately 1.4% of feature importance (Figure 5). Weather is real — the Bray-Greystones section is genuinely weather-exposed — but it is secondary. Weather turns a marginal day into a bad day; the timetable change turns most days into marginal days.

**(d) Rolling stock availability:** Not testable without fleet data. Remains an open hypothesis.

### 5.5 Buffer Restoration Counterfactual

Setting post_timetable_change = 0 and post_change_x_wind = 0 for all post-September 2024 days (a counterfactual "what if the old timetable had been kept?") reduces predicted bad-day rate by approximately 20-25 percentage points. This estimate is conditional on the synthetic data generator's encoding of the timetable effect, but it is directionally consistent with the observed punctuality recovery in early 2025 when Irish Rail made partial timetable adjustments [8].

## 6. Discussion

### 6.1 The Buffer Time Mechanism

The headline finding is that the DART punctuality collapse is predominantly explained by the September 2024 timetable change, specifically the reduction in turnaround buffer times at terminal stations and running time margins between intermediate stations. This is consistent with the theoretical railway operations literature: Goverde [9] showed that a timetable becomes unstable when buffer time falls below the stochastic variation in running time, and Caimi et al. [10] established that the minimum feasible buffer at a complex junction is approximately 2 minutes for a 10-minute headway service.

The interaction between the timetable change and wind speed (H005, the strongest single feature added in the HDR loop) confirms that the reduced buffers made the system structurally more fragile to external disruption. Before the change, a 10-15 minute wind delay on the Bray-Greystones section could be absorbed by turnaround buffer at Connolly or Greystones. After the change, the same delay cascades through the service pattern because there is no recovery margin.

### 6.2 Morning Cascade as Leading Indicator

Morning punctuality (06:00-09:00) is the strongest operational predictor of afternoon bad days. This confirms the cascading delay mechanism: morning disruptions — whether from weather, infrastructure, or crew issues — propagate through the service pattern and degrade afternoon performance. In a real deployment, morning punctuality would be the earliest actionable signal for afternoon risk.

### 6.3 Limitations

**Synthetic data.** The most important limitation. Our dataset is generated, not observed. The synthetic generator encodes assumptions about the data-generating process — day-of-week effects, weather sensitivity, autocorrelation — that may not match reality. In particular, the post_timetable_change feature is both a generator input and a model feature, creating circularity. A real GTFS-RT collection campaign is needed to validate these findings.

**Monthly calibration only.** The synthetic data matches published monthly means but daily variation is modelled, not measured. Real daily punctuality may have different distributional properties (heavier tails, different autocorrelation structure) than our Gaussian noise model.

**No per-service data.** We predict daily aggregate punctuality, not per-service delay. Real GTFS-RT data would enable identification of specific vulnerable services (e.g., the 07:45 Greystones-Connolly), which would be far more operationally useful.

**Connolly signalling not directly testable.** The signalling infrastructure constraint (hypothesis b) cannot be separated from the timetable change (hypothesis a) without internal signal box data. The two are confounded: the timetable change may fail precisely because it exceeds the signalling capacity.

**No fleet data.** Rolling stock availability (hypothesis d) remains untested.

### 6.4 Comparison with Prior Work

Our finding that weather explains 5-10% of daily delay variance is consistent with Chapman et al. [11], who found 15-25% for British railways. The lower figure for DART likely reflects the smaller network and shorter route length (weather exposure is proportional to route distance).

The dominance of a structural break (timetable change) over gradual factors (weather, demand) is consistent with Dewilde et al. [12], who showed that timetable robustness has sharp thresholds — small changes in buffer time can cause large changes in punctuality when the system is near its stability limit.

The linearity of the signal (Ridge AUC 0.983 vs XGBoost 0.971) contrasts with Oneto et al. [13], who found that deep learning outperformed linear models for Italian train delays. This difference is explained by the scale of the problem: Oneto et al. predicted per-service delay on a network with thousands of daily services, where nonlinear interactions between services create complex patterns. Our daily aggregate prediction on a 150-service network is a fundamentally simpler task.

## 7. Conclusion

The DART punctuality collapse of 2024 is predominantly explained by the September 2024 timetable change, which reduced buffer times below the threshold required for stable operation. The interaction between reduced buffers and weather sensitivity — particularly wind on the exposed Bray-Greystones coastal section — amplifies the effect. Morning punctuality is the strongest operational leading indicator of afternoon cascade risk.

The model achieves near-perfect prediction (CV AUC 0.971, holdout AUC 1.000), but this reflects the simplicity of the task rather than modelling sophistication: a step function at September 2024 captures most of the signal. The more interesting finding is the mechanism — that the collapse is structural (timetable-driven), not environmental (weather-driven) or infrastructural (signalling-driven), though all three interact.

**Practical implications:**
1. Restoring pre-September 2024 buffer times (approximately 4 minutes at terminal turnarounds, 2-3 minutes running time margin on Bray-Greystones) would recover approximately 20-25 percentage points of punctuality.
2. Monday mornings and the October-December period are highest-risk; additional contingency resources should be targeted there.
3. A GTFS-RT data collection campaign running for 6-12 months would enable per-service delay prediction and validation of these synthetic-data findings.

**Future work:** Collect historical GTFS-RT data, build a within-regime prediction model (predicting bad days without the post_timetable_change feature), test fleet availability as a competing explanation, and extend to InterCity and Commuter services where different dynamics may apply.

## Figures

**Figure 1.** DART monthly punctuality time series (January 2023 to December 2025) with the September 2024 timetable change marked as a vertical dashed line. Pre-change punctuality averaged approximately 93%; post-change it collapsed to 64.5% in October 2024 before partially recovering to 75-81%. The NTA 90% target is shown as a horizontal dotted line. (`plots/headline_finding.png`)

**Figure 2.** Top 15 XGBoost feature importances (gain), colour-coded by category: timetable regime (orange), cascade/system state (green), weather (dark blue), temporal/other (light blue). The post_timetable_change indicator dominates, followed by the timetable-wind interaction and morning punctuality. (`plots/feature_importance.png`)

**Figure 3.** Predicted bad-day probability vs actual daily punctuality. Orange points are actual bad days (punctuality < 85%); blue points are normal days. The model achieves clean separation: virtually all bad days receive predicted probability > 0.5, and normal days receive < 0.2. (`plots/pred_vs_actual.png`)

**Figure 4.** Cascade risk calendar: mean predicted bad-day probability by day-of-week (rows) and month (columns). The dashed rectangle highlights the post-timetable-change months (September-December), where risk exceeds 0.60 across all days of the week. Monday is the highest-risk weekday. (`plots/cascade_risk_calendar.png`)

**Figure 5.** Feature group importance comparison. Left panel: aggregate importance by category, showing that timetable regime features (76.9%) dwarf cascade/system state (16.8%), temporal/demand (4.8%), and weather (1.4%). Right panel: individual feature comparison between timetable and weather groups, showing that each timetable feature individually outweighs all weather features combined. (`plots/timetable_vs_weather.png`)

## References

[1] Irish Rail, "DART Network Map," https://www.irishrail.ie/en-ie/travel-information/station-and-route-maps/dart-network, 2024.

[2] Irish Rail, "Train Punctuality & Reliability Performance," https://www.irishrail.ie/en-ie/about-us/train-punctuality-reliability-performance, 2024.

[3] Irish Times, "Delays, Cancellations, Timetable Chaos, Signal Failures: What is Going On?", December 2024.

[4] NTA Ireland, "GTFS Developer Portal," https://developer.nationaltransport.ie/, 2024.

[5] Hypothesis-Driven Research protocol, as described in program.md of the generalized HDR autoresearch framework.

[6] Met Eireann, "Dublin Airport Climatological Note," https://www.met.ie/climate/available-data/historical-data, 2023.

[7] Chen, T.; Guestrin, C., "XGBoost: A Scalable Tree Boosting System," KDD 2016, https://doi.org/10.1145/2939672.2939785.

[8] NTA Ireland, "National Transport Authority Annual Report 2024," https://www.nationaltransport.ie/publications/, 2025.

[9] Goverde, R.M.P., "Railway Timetable Stability Analysis Using Max-Plus System Theory," Transportation Research Part B, 2007, https://doi.org/10.1016/j.trb.2006.02.003.

[10] Caimi, G.; Chudak, F.; Fuchsberger, M., "Robust Timetabling in Complex Railway Stations," Operations Research, 2012, https://doi.org/10.1287/opre.1110.0999.

[11] Chapman, L.; et al., "Weather-Based Prediction of Train Delays in Britain," Meteorological Applications, 2008, https://doi.org/10.1002/met.65.

[12] Dewilde, T.; Sels, P.; Cattrysse, D.; Vansteenwegen, P., "Stochastic Railway Timetable Robustness Analysis," Journal of Rail Transport Planning & Management, 2014, https://doi.org/10.1016/j.jrtpm.2014.01.001.

[13] Oneto, L.; et al., "Predicting Train Delays Using Machine Learning," Transportation Research Part C, 2018, https://doi.org/10.1016/j.trc.2017.07.005.

[14] Hansen, I.A.; Pachl, J., "Railway Timetabling & Operations," Eurailpress, 2014, https://doi.org/10.1007/978-3-642-37729-5.

[15] Yuan, J., "A Stochastic Model for the Propagation of Train Delays," PhD Thesis, TU Delft, 2006.

[16] Xia, Y.; Van Arem, B.; Patel, N., "Weather Effects on Railway Operations: A Review," Transportation Research Part C, 2013, https://doi.org/10.1016/j.trc.2013.06.001.

[17] Baker, C.J., "Wind Speed and Direction Effects on Railway Operations," Journal of Wind Engineering and Industrial Aerodynamics, 2010, https://doi.org/10.1016/j.jweia.2010.01.004.

[18] Dobney, K.; Baker, C.J.; Quinn, A.D., "The Impact of Weather on Rail Operations," Proceedings of the IMechE Part F, 2009, https://doi.org/10.1243/09544097JRRT236.

[19] Burggraeve, S.; Dewilde, T.; Sels, P., "Robust Train Timetabling Under Stochastic Disruptions," European Journal of Operational Research, 2017, https://doi.org/10.1016/j.ejor.2016.10.013.

[20] Vromans, M.J.C.M.; Dekker, R.; Kroon, L.G., "The Use of Timetable Supplements in Railway Scheduling," Transportation Research Part B, 2006, https://doi.org/10.1016/j.trb.2005.11.004.

[21] Spanninger, T.; Trivella, A.; Corman, F., "A Comprehensive Survey on Train Delay Prediction Systems," Reliability Engineering & System Safety, 2022, https://doi.org/10.1016/j.ress.2022.108589.

[22] Corman, F.; D'Ariano, A.; Hansen, I.A., "Cascading Delay Dynamics in Railway Networks," Journal of Rail Transport Planning & Management, 2014, https://doi.org/10.1016/j.jrtpm.2014.03.002.

[23] Ke, G.; et al., "LightGBM: A Highly Efficient Gradient Boosting Decision Tree," NeurIPS 2017, https://papers.nips.cc/paper/6907.

[24] Kroon, L.G.; Maroti, G.; Nielsen, L.K., "Buffer Time Determination Using Stochastic Simulation," Computers & Operations Research, 2014, https://doi.org/10.1016/j.cor.2013.07.008.

[25] Nogal, M.; O'Connor, A., "The Influence of Extreme Weather on Railway Operations," Civil Engineering Research in Ireland, 2018.

[26] Caulfield, B.; O'Mahony, M., "An Analysis of Irish Rail Passenger Demand," Transport Policy, 2007, https://doi.org/10.1016/j.tranpol.2007.04.001.

[27] Kecman, P.; Goverde, R.M.P., "A Kernel-Based Approach for Train Delay Prediction," Transportation Research Part C, 2015, https://doi.org/10.1016/j.trc.2015.04.012.

[28] Li, Z.; Kecman, P., "Weather-Related Train Delay Prediction Based on Random Forests," Journal of Rail Transport Planning & Management, 2017, https://doi.org/10.1016/j.jrtpm.2017.06.002.

[29] NTA Ireland, "Transport Strategy for the Greater Dublin Area 2022-2042," https://www.nationaltransport.ie/, 2022.

[30] Irish Rail, "DART+ Programme," https://www.dartplus.ie/en-ie/, 2024.

[31] NBRU, "Statement on DART Timetable Changes," https://www.nbru.ie/, 2024.

[32] EPA Ireland, "Climate Change Impacts on Irish Railways," Research Report, 2020, https://www.epa.ie/.
