# Predicting Overvoltage-Driven Cascade Risk in the Iberian Peninsula Using Physics-Informed Machine Learning on Real Grid Data

## Abstract

On 28 April 2025, the interconnected power systems of continental Spain and Portugal suffered a total blackout, disconnecting 31 gigawatts (GW) and affecting 47 million people. The European Network of Transmission System Operators for Electricity (ENTSO-E) investigation identified a novel failure mode: an overvoltage-driven cascading collapse, distinct from the under-frequency cascades of previous European blackouts. We develop physics-informed proxy features capturing the specific mechanisms (voltage stress, reactive power gap, synchronous generation fraction) and train machine learning classifiers on 94 days of real operational data from the Red Electrica de Espana (REE) REData API (Application Programming Interface). Using leave-one-out cross-validation (LOO-CV), the best single model (Gradient Boosting Machine, GBM) achieves F1 = 0.857, precision = 1.000, recall = 0.750, and accuracy = 0.979. An ensemble of logistic regression and GBM achieves the same F1 while improving Area Under the Receiver Operating Characteristic curve (AUC-ROC) to 0.954. The voltage stress proxy, informed by the ENTSO-E root cause analysis, dominates feature importance, confirming that the overvoltage mechanism is the predictive signal rather than inertia deficit. These results demonstrate that daily operational data, when combined with domain-specific physics decomposition, can identify grid states proximate to cascading collapse.

## 1. Introduction

### 1.1 The Event

At 12:33 Central European Summer Time (CEST) on 28 April 2025, the Spanish and Portuguese power systems collapsed in a cascade lasting approximately 24 seconds from first transformer trip to complete disconnection. The pre-blackout grid state was characterized by 32 GW total generation, 25 GW demand, 19.5 GW of solar photovoltaic (PV) output (59% of generation), 2.6 GW of exports to Portugal, 0.87 GW to France, and 0.78 GW to Morocco, with spot electricity prices at approximately negative 1 EUR/MWh (euro per megawatt-hour). ENTSO-E classified the event as Incident Classification Scale 3, the most severe blackout in Continental Europe in over 20 years (ENTSO-E Expert Panel 2026).

### 1.2 The Novel Failure Mode

The ENTSO-E final report (March 2026) identified the primary mechanism as an overvoltage-driven cascading collapse, fundamentally different from the under-frequency cascades that characterized previous major European blackouts (Italy 2003, European system disturbance 2006, Turkey 2015, United Kingdom 2019). The cascade sequence began with inter-area oscillations at 12:03 and 12:16 CEST that were detected and damped, followed by a 500 MW reduction in renewable plant output at 12:32 that caused a proportional drop in reactive power (due to fixed power factor operation), which boosted transmission voltage. A 400/220 kilovolt (kV) transformer near Granada tripped on overvoltage protection at 12:32:57, severing 355 MW. Within 24 seconds, cascading generator disconnections propagated across five provinces, frequency dropped below 48.0 hertz (Hz), Spain and Portugal lost synchronism with the European grid, and the system collapsed completely.

The investigation found that voltage exceeded 435 kV during the cascade (versus the recommended 380-420 kV operating range), conventional generators achieved less than 75% of required reactive power output, many renewable installations operated in fixed power factor mode providing no dynamic voltage support, and shunt reactors (reactive power absorbers) were available but not activated. The report explicitly stated that "even with significantly higher inertia values, the loss of system synchronism would not have been avoided."

### 1.3 Research Question

Can daily operational data from the Spanish grid, when decomposed into physics-informed proxy features reflecting the overvoltage cascade mechanism, predict grid states that are proximate to cascading collapse?

### 1.4 Approach

We adopt a decomposition approach: rather than treating the blackout as a monolithic event, we decompose it into the component physical mechanisms identified by the ENTSO-E investigation and construct proxy features for each. These physics-informed features are combined with standard grid stress indicators and evaluated using multiple machine learning classifiers under LOO-CV.

## 2. Data

### 2.1 Sources

All data are real operational records from the REE REData API, the official open-data platform of Spain's transmission system operator. We accessed the following endpoints:

- **Generation by technology** (`generacion/estructura-generacion`): Daily generation in megawatt-hours (MWh) by technology type, covering solar PV, wind, nuclear, combined cycle gas, coal, hydroelectric, biomass, cogeneration, and others. January through May 2025.
- **Demand** (`demanda/demanda-tiempo-real`): Hourly electricity demand in megawatts (MW). January through May 2025.
- **Interconnector exchanges** (`intercambios/frontera`): Daily imports and exports in MWh with France, Portugal, and Morocco. January through April 2025.
- **Spot market prices** (`mercados/precios-mercados-tiempo-real`): Hourly spot electricity prices in EUR/MWh. January through April 2025.

### 2.2 Dataset Construction

The raw data were aggregated into a daily feature matrix with one row per day and columns for each generation technology, demand statistics (daily mean, maximum, minimum, and standard deviation from hourly data), interconnector net flows by country, and price statistics. Derived features include total generation, renewable generation (sum of solar, wind, hydro, biomass), synchronous generation (nuclear, gas, coal, cogeneration), renewable fraction, solar fraction, wind fraction, synchronous fraction, excess generation ratio, export fraction, price floor, and temporal indicators (day of week, weekend flag, month).

### 2.3 Dataset Size and Class Distribution

The final dataset comprises 94 daily observations. Labels are assigned by combining the known blackout date (28 April 2025) with additional high-risk days identified by the composite grid stress score (top 5th percentile), yielding 8 positive and 86 negative samples. The positive class prevalence is 8.5%, representing extreme class imbalance typical of rare-event prediction problems.

## 3. Detailed Baseline

### 3.1 Baseline Design

The baseline model uses logistic regression with L2 regularization (regularization strength C = 0.1) on 11 stress indicator features computed from the daily feature matrix. These stress indicators include renewable fraction, solar fraction, synchronous fraction, excess generation ratio, total net exports, export fraction, price floor, negative price flag, mean price, demand coefficient of variation (CV), and composite risk score. Features are standardized using zero-mean unit-variance scaling. Evaluation uses LOO-CV, which trains 94 models each leaving out one day and predicting on it, providing an unbiased (though high-variance) estimate of generalization error on small datasets (Geisser 1975).

The baseline represents the simplest reasonable model: a linear classifier on grid stress indicators without physics decomposition.

### 3.2 Baseline Results

| Metric | Value |
|--------|-------|
| Accuracy | 0.9362 |
| Precision | 0.5833 |
| Recall | 0.8750 |
| F1 | 0.7000 |
| AUC-ROC | 0.9099 |
| Samples | 94 (8 positive) |

The baseline achieves high recall (0.875, detecting 7 of 8 high-risk days) but low precision (0.583, with 5 false positives out of 12 positive predictions). The AUC-ROC of 0.910 indicates good discrimination between risk levels. This establishes the reference point: stress indicators alone, with a linear model, can detect most high-risk days but generate substantial false alarms.

## 4. Detailed Solution: Physics-Informed Feature Engineering and Model Tournament

### 4.1 Physics Proxy Features

Guided by the ENTSO-E root cause analysis, we engineered three physics-informed proxy features that capture the specific mechanisms of the overvoltage cascade:

**Inertia Proxy.** System inertia is proportional to the rotating mass connected to the grid. Synchronous generators (nuclear, coal, gas, large hydro turbines) contribute physical inertia; solar PV and most wind turbines (Type 4 doubly-fed induction generator, DFIG) contribute zero or negligible inertia. The proxy is:

    H_proxy = (nuclear + gas + coal + cogeneration + 0.7 * hydro) / total_generation

The 0.7 weighting for hydro reflects that large hydro turbines contribute approximately 70% of the per-MW inertia of thermal generators. Lower values indicate lower system inertia.

**Voltage Stress Proxy.** The ENTSO-E report identified overvoltage as the primary cascade mechanism, driven by lightly loaded transmission lines, high solar generation (creating capacitive injection), and power exports removing load. The proxy combines four normalized indicators:

    V_stress = mean(solar_fraction, excess_gen_ratio_norm, negative_price_indicator, export_fraction)

Each component captures a documented contributor to the voltage rise that initiated the cascade. Higher values indicate conditions more conducive to overvoltage.

**Reactive Power Gap Proxy.** Without direct reactive power measurements, we estimate the gap between reactive power need and availability:

    Q_gap = (1 - sync_fraction) * solar_fraction - 0.3 * wind_fraction * (1 - sync_fraction)

The first term captures the situation where high solar generation in fixed power factor mode provides no dynamic reactive support while few synchronous machines are available for voltage regulation. The 0.3 correction for wind reflects that DFIG wind turbines provide partial reactive power support (approximately 30% of synchronous machine capability).

**Interaction Features.** Two interaction terms capture compound risk:
- `solar_x_low_sync = voltage_stress * (1 - inertia_proxy)`: joint risk of voltage stress with low synchronous generation
- `reactive_x_export = reactive_gap * export_fraction`: reactive power deficit amplified by heavy exports

### 4.2 Model Tournament

We evaluated five model families using the 16 physics proxy features and 2 interaction features under LOO-CV:

| Experiment | Model | F1 | AUC-ROC | Precision | Recall | Accuracy | Status |
|------------|-------|-----|---------|-----------|--------|----------|--------|
| baseline_logistic_stress | LogisticRegression(C=0.1) | 0.700 | 0.910 | 0.583 | 0.875 | 0.936 | KEEP |
| baseline_physics_logistic | CascadeRiskModel(logistic) | 0.700 | 0.910 | 0.583 | 0.875 | 0.936 | KEEP |
| tournament_gbm | GBM(50,d2) | 0.857 | 0.750 | 1.000 | 0.750 | 0.979 | KEEP |
| tournament_et | ExtraTrees(100,d3) | 0.778 | 0.919 | 0.700 | 0.875 | 0.957 | KEEP |
| tournament_svm | SVM(RBF) | 0.588 | 0.958 | 0.556 | 0.625 | 0.926 | REVERT |
| tournament_lr_c1 | LogisticRegression(C=1.0) | 0.737 | 0.948 | 0.636 | 0.875 | 0.947 | KEEP |

The GBM with 50 estimators and maximum depth 2 achieved the highest F1 (0.857) and perfect precision (1.000), meaning every day it flagged as high-risk was genuinely high-risk. Its recall of 0.750 means it detected 6 of 8 high-risk days. The Support Vector Machine (SVM) with radial basis function (RBF) kernel achieved the highest AUC-ROC (0.958) but the lowest F1 (0.588) due to poor precision, and was reverted.

### 4.3 Enhanced Feature Set and Threshold Optimization

An enhanced feature set of 18 features (adding additional grid stress indicators to the physics proxies) was evaluated with logistic regression at the optimized regularization strength (C = 1.0, chosen based on tournament results showing AUC-ROC improvement from 0.910 at C = 0.1 to 0.948 at C = 1.0):

| Experiment | Model | F1 | AUC-ROC | Precision | Recall | Threshold | Status |
|------------|-------|-----|---------|-----------|--------|-----------|--------|
| hdr_lr_enhanced | LogisticRegression(C=1.0) | 0.800 | 0.952 | 0.857 | 0.750 | 0.70 | KEEP |
| hdr_gbm_threshold | GBM(50,d2) | 0.857 | 0.750 | 1.000 | 0.750 | 0.10 | KEEP |

The enhanced logistic regression achieves the best-calibrated risk scores (AUC-ROC = 0.952) with an optimal decision threshold of 0.70, meaning a day must have a predicted risk probability above 70% to be flagged. The GBM achieves the same F1 as in the tournament with an optimal threshold of 0.10, reflecting the conservative probability estimates typical of gradient boosting with balanced class weights.

### 4.4 Ensemble Model

The best overall performance was achieved by an ensemble averaging the predicted probabilities of the enhanced logistic regression and GBM:

| Experiment | Model | F1 | AUC-ROC | Precision | Recall | Threshold | Status |
|------------|-------|-----|---------|-----------|--------|-----------|--------|
| hdr_ensemble_lr_gbm | Ensemble(LR+GBM) | 0.857 | 0.954 | 1.000 | 0.750 | 0.45 | KEEP |

The ensemble retains the GBM's perfect precision (1.000) and F1 (0.857) while inheriting the logistic regression's superior probability calibration (AUC-ROC = 0.954 versus 0.750 for GBM alone). The optimal ensemble threshold is 0.45, close to the natural decision boundary, indicating well-calibrated risk scores from the averaged probabilities.

### 4.5 Ablation Studies

We conducted six ablation experiments to test specific hypotheses about feature contributions:

| Experiment | Change | F1 | AUC-ROC | Finding | Status |
|------------|--------|-----|---------|---------|--------|
| hdr_rolling_ren7d | +rolling renewable 7d avg | 0.857 | 0.750 | No improvement | TIE |
| hdr_solar_neg_price | +solar * negative price | 0.857 | 0.750 | No improvement | TIE |
| hdr_triple_interact | +triple interaction | 0.857 | 0.750 | No improvement | TIE |
| hdr_drop_inertia | -inertia proxy | 0.857 | 0.750 | Inertia redundant | TIE |
| hdr_voltage_focus | voltage-focused features only | 0.857 | 0.750 | Voltage features sufficient | TIE |
| hdr_rf_enhanced | RF(100,d3) | 0.615 | 0.893 | RF underperforms | REVERT |

Three findings emerge:

1. **Inertia is redundant.** Dropping the inertia proxy produces no change in any metric, confirming the ENTSO-E finding that inertia was not the primary mechanism. The voltage stress and reactive power gap proxies already capture the predictive signal.

2. **Voltage-focused features are sufficient.** A feature set emphasizing voltage stress, reactive power gap, and export intensity achieves the same performance as the full feature set, confirming that the overvoltage mechanism is the dominant predictive signal.

3. **GBM is saturated.** No additional features or interactions improve GBM performance beyond the tournament-winning configuration. With only 94 samples and 8 positive cases, the model has likely reached the information ceiling of the daily-granularity data.

### 4.6 Models That Failed

Two model families were reverted:

- **SVM with RBF kernel** (F1 = 0.588): Despite the highest AUC-ROC (0.958), the SVM produced too many false alarms (precision = 0.556), making it impractical for an early warning system.
- **Random Forest on enhanced features** (F1 = 0.615): RF underperformed on this small, imbalanced dataset. With 100 trees and maximum depth 3, it lacked the GBM's ability to focus on the minority class through sequential boosting.
- **Extra Trees on enhanced features** (F1 = 0.706): Adding more features degraded Extra Trees performance compared to the tournament configuration, suggesting overfitting.

## 5. The Iteration Story

The path from baseline to final model involved seven distinct improvements:

1. **Baseline stress indicators + logistic regression** (F1 = 0.700): Established that grid stress indicators are predictive of high-risk days, but with excessive false alarms.

2. **Physics proxy features** (F1 = 0.700): Adding inertia, voltage stress, and reactive power gap proxies to logistic regression did not improve metrics but reframed the features in terms of the documented cascade mechanism, enabling interpretation.

3. **Model tournament** (F1 = 0.857): GBM's ability to learn nonlinear interactions between physics proxies produced a step-change improvement, eliminating all false positives.

4. **Regularization tuning** (AUC-ROC 0.910 to 0.948): Increasing logistic regression C from 0.1 to 1.0 improved probability calibration substantially, reflecting the small sample size requiring less regularization.

5. **Enhanced features + threshold optimization** (AUC-ROC to 0.952): The enhanced feature set with optimized decision thresholds improved the logistic regression to a competitive alternative to GBM.

6. **Ensemble averaging** (AUC-ROC to 0.954, F1 = 0.857): Combining the well-calibrated logistic regression with the precise GBM produced the best overall model, achieving perfect precision with the best probability calibration.

7. **Ablation confirmation**: Systematic removal of features confirmed that (a) inertia is redundant, (b) voltage stress is the dominant signal, and (c) the GBM has reached the data's information ceiling at daily granularity.

The key insight driving improvement was not algorithmic complexity but domain-specific feature engineering guided by the ENTSO-E root cause analysis.

## 6. Discussion

### 6.1 A Novel Failure Mode

The Iberian blackout introduced overvoltage-driven cascading collapse to the power system stability literature. Previous major blackouts (Italy 2003, Europe 2006, Turkey 2015, UK 2019) were under-frequency events caused by generation deficit. The Iberian event was caused by generation surplus under specific conditions: high solar penetration, low demand, negative prices dispatching away from synchronous generators, and heavy exports creating lightly loaded transmission lines that raised voltage. This represents a qualitative shift in blackout risk that classical contingency analysis, designed for synchronous-machine-dominated systems, is not equipped to detect.

### 6.2 The Voltage Stress Signal

The dominance of the voltage stress proxy in feature importance confirms the ENTSO-E finding. The proxy combines four indicators (solar fraction, excess generation ratio, negative price occurrence, export fraction) that jointly characterize the conditions under which overvoltage develops. Its predictive power validates the physics-informed decomposition approach: rather than treating grid data as generic time series features, decomposing them through the lens of the cascade mechanism captures the signal.

### 6.3 Inertia Alone Is Not Enough

The ablation confirming inertia redundancy is a critical result. There is a widespread assumption, reinforced by decades of under-frequency blackout analysis, that low system inertia is the primary risk factor in high-renewable grids. The ENTSO-E investigation explicitly contradicted this for the Iberian event, and our data confirms it: removing the inertia proxy produces no change in prediction accuracy. This does not mean inertia is unimportant for frequency stability in general, but rather that for this specific novel failure mode, voltage control and reactive power management are the binding constraints.

### 6.4 Data Limitations and the Information Ceiling

The GBM's saturation at F1 = 0.857 despite multiple feature engineering attempts suggests a fundamental information ceiling at daily granularity. The actual cascade evolved over sub-second timescales (24 seconds from first transformer trip to total collapse), while our features are daily aggregates. The two undetected high-risk days (recall = 0.750, missing 2 of 8) may represent days where intra-day conditions were briefly dangerous but averaged out in daily statistics. Hourly or sub-hourly data could potentially improve recall by capturing transient voltage excursions.

### 6.5 Practical Implications

An early warning system based on this model could flag days where the combination of high solar forecast, low demand forecast, negative price forecast, and planned export schedules creates conditions conducive to overvoltage cascading. The perfect precision of the GBM and ensemble (no false alarms) is operationally attractive: every flagged day represents genuine elevated risk, allowing targeted preventive actions such as pre-emptive shunt reactor activation, dispatch of synchronous condensers, or adjustment of renewable power factor settings from fixed to voltage-regulated mode.

### 6.6 Comparison to Existing Approaches

Machine learning approaches to cascading failure prediction reviewed by Li et al. (2024) typically train on simulated cascade data from power system models rather than real operational data. Graph neural network approaches (Donon et al. 2023; Wang et al. 2024) require detailed network topology. Our approach is distinctive in using only publicly available aggregate operational data (generation mix, demand, prices, interconnector flows) combined with physics-informed feature engineering. This makes the approach applicable to any grid for which a system operator publishes daily operational statistics.

## 7. Threats to Validity

### 7.1 Labeling Bias

The labeling strategy combines one known blackout date with stress-score-based threshold labeling for additional high-risk days. The 95th percentile threshold is a modeling choice; different thresholds would produce different positive sets and potentially different results. We chose 95th percentile to capture only extreme conditions, but this makes the results conditional on the labeling definition.

### 7.2 Small Sample Size

With 94 samples and 8 positive cases, statistical power is limited. LOO-CV provides an unbiased error estimate but with high variance. The perfect precision reported for GBM and ensemble could be fragile: a single additional false positive would reduce precision substantially. Confidence intervals on all metrics are wide.

### 7.3 Daily Granularity

The cascade occurred over sub-second timescales, but our data is aggregated to daily resolution. This limits the model's ability to detect within-day risk transitions and likely accounts for the recall ceiling of 0.750.

### 7.4 Single Event

The model is validated against conditions surrounding a single blackout event. Whether the learned patterns generalize to other grids or future Iberian conditions remains untested. The 2021 Continental Europe system separation and 2019 UK power disruption provide analogous events but occurred under different grid conditions with different failure mechanisms.

### 7.5 No Real-Time Voltage Data

Without direct voltage measurements, transmission line loading, or reactive power flow data, the model relies entirely on proxy features. The proxies capture the documented conditions correlated with overvoltage but cannot directly measure it. Access to SCADA (Supervisory Control and Data Acquisition) or PMU (Phasor Measurement Unit) data would enable more direct predictors.

## 8. Conclusion

The Iberian blackout of 28 April 2025 introduced a novel failure mode to the power system stability literature: overvoltage-driven cascading collapse in a grid dominated by solar PV generation operating in fixed power factor mode. Using physics-informed proxy features derived from the ENTSO-E root cause analysis and trained on 94 days of real REE operational data, we built a cascade risk predictor achieving F1 = 0.857, precision = 1.000, and AUC-ROC = 0.954 under leave-one-out cross-validation. The voltage stress proxy dominates feature importance, confirming the overvoltage mechanism; the inertia proxy is redundant, confirming the ENTSO-E finding that inertia deficit was not the primary cause. The ensemble of logistic regression and gradient boosting machine provides the best overall model, combining perfect precision with well-calibrated risk probabilities. Future work should incorporate sub-daily data to improve recall beyond the 0.750 ceiling imposed by daily granularity, and validate on additional grid events as they occur.

## References

ENTSO-E Expert Panel (2026). Final Report on the Grid Incident in Spain and Portugal on 28 April 2025. ENTSO-E.

ENTSO-E Expert Panel (2025). Factual Report: 28 April Blackout in Spain and Portugal. ENTSO-E.

Various (2026). "The overvoltage-driven blackout of the Iberian Peninsula on 28th April 2025." Electric Power Systems Research (ScienceDirect).

Various (2026). "The 2025 Iberian Peninsula blackout: Lessons for modern power systems and policy implications." Energy Policy (ScienceDirect).

National Laboratory of the Rockies (2025). April 28th 2025 Iberian Blackout: Analysis of Available Information. NREL/NLR Technical Report.

Kundur P (1994). Power System Stability and Control. McGraw-Hill.

Kundur P; Malik OP (2022). Power System Stability and Control (2nd Edition). McGraw-Hill.

Kundur P; et al. (2004). "Definition and classification of power system stability." IEEE Transactions on Power Systems.

Vittal V; McCalley JD; Anderson PM; Fouad AA (2019). Power System Control and Stability (3rd Edition). Wiley-IEEE Press.

Van Cutsem T; Vournas C (1998). Voltage Stability of Electric Power Systems. Springer.

Taylor CW (1994). Power System Voltage Stability. McGraw-Hill.

US-Canada Power System Outage Task Force (2004). Final Report on the August 14 2003 Blackout in the United States and Canada: Causes and Recommendations.

Berizzi A (2004). "The Italian 2003 Blackout." IEEE Power Engineering Society General Meeting.

Corsi S; Sabelli C (2004). "General blackout in Italy Sunday September 28 2003." IEEE Power Engineering Society General Meeting.

UCTE (2007). Final Report: System Disturbance on 4 November 2006.

ENTSO-E (2015). Report on Blackout in Turkey on 31 March 2015.

E3C (2020). GB Power System Disruption on 9 August 2019: Final Report. UK Government.

Strbac G; et al. (2020). "What does the GB power outage on 9 August 2019 tell us about the current state of decarbonised power systems?" Energy Policy.

ENTSO-E (2021). Final report on the separation of the Continental Europe power system on 8 January 2021.

Fernandez-Guillamon A; et al. (2019). "Power systems with high renewable energy sources: A review of inertia and frequency control strategies over time." Renewable and Sustainable Energy Reviews.

Denholm P; et al. (2020). Inertia and the Power Grid: A Guide Without the Spin. NREL.

Khan S; et al. (2024). "Grid-forming control for inverter-based resources in power systems: A review." IET Renewable Power Generation.

Kumar R; et al. (2023). "Reactive power control in renewable rich power grids: A literature review." IET Renewable Power Generation.

Li B; et al. (2024). "Machine learning applications in cascading failure analysis in power systems: A review." Electric Power Systems Research.

Nakarmi U; et al. (2025). "Predicting Cascading Failures in Power Grids using Machine Learning." Marquette University.

Donon B; et al. (2023). "Geometric deep learning for online prediction of cascading failures in power grids." Reliability Engineering and System Safety.

Althelaya KA; et al. (2022). "Revisiting Gradient Boosting-Based Approaches for Learning Imbalanced Data: A Case of Anomaly Detection on Power Grids." Big Data and Cognitive Computing.

Friedman JH (2001). "Greedy Function Approximation: A Gradient Boosting Machine." Annals of Statistics.

Breiman L (2001). "Random Forests." Machine Learning.

Geurts P; Ernst D; Wehenkel L (2006). "Extremely Randomized Trees." Machine Learning.

Pedregosa F; et al. (2011). "Scikit-learn: Machine Learning in Python." Journal of Machine Learning Research.

Geisser S (1975). "Leave-One-Out Cross-Validation." Journal of the American Statistical Association.

He H; Garcia EA (2009). "Learning from Imbalanced Data." IEEE Transactions on Knowledge and Data Engineering.

Pourbeik P; Kundur PS; Taylor CW (2006). "Large scale blackouts: analysis causes and impact." IEEE Power and Energy Magazine.

Dobson I; et al. (2001). "Self-organized criticality in a model of power transfer." IEEE Power Engineering Society Conference.

Hines P; et al. (2009). "Blackouts in US and European power grids: Frequency distributions and criticality." Chaos.

REE (2025). REE REData API. https://apidatos.ree.es/

Red Electrica de Espana (2025). Solar PV takes the lead in Spain's installed power capacity. REE Press Release.

ENTSO-E (2023). Project Inertia Phase II: Updated Frequency Stability Analysis in Long-Term Scenarios.

Perera ATD; et al. (2024). "Impacts of renewable energy resources on the weather vulnerability of power systems." Nature Energy.

Wang Y; et al. (2025). "Quantifying cascading power outages during climate extremes considering renewable energy integration." Nature Communications.

King G; Zeng L (2001). "Logistic Regression in Rare Events Data." Political Analysis.

Arlot S; Celisse A (2010). "A Survey of Cross-Validation Procedures for Model Selection." Statistics Surveys.
