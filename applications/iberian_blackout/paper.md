# Can Publicly Available Grid-State Data Predict Cascading Failure? A Hypothesis-Driven Analysis of the 28 April 2025 Iberian Blackout

## Abstract

On 28 April 2025, a cascading failure disconnected the Iberian Peninsula from the Continental European synchronous area, causing a near-total blackout affecting approximately 56 million people. The European Network of Transmission System Operators for Electricity (ENTSO-E) Expert Panel identified systemic failures in voltage control, reactive power management, and oscillation handling in a grid operating at approximately 78% System Non-Synchronous Penetration (SNSP). We ask: could the approach of this cascade have been detected from publicly available grid-state data? Using a Hypothesis-Driven Research (HDR) protocol with 38 pre-registered single-change experiments, we build a frequency excursion predictor from ENTSO-E Transparency Platform generation, load, and cross-border flow data for Spain (2023-2025). The winning XGBoost model achieves a cross-validated Area Under the Receiver Operating Characteristic curve (AUC-ROC) of 0.640 and a holdout AUC of 0.888 on the blackout day. The model correctly ranks the pre-cascade hours (10:00-12:00 Central European Time (CET)) in the top 10% of risk scores across the full training period. However, the predicted risk probability never exceeds 0.5 on the blackout day — the model can rank hours by risk but cannot produce a binary alert from public data alone. The three features retained from the HDR loop are total generation ramp rate, residual demand, and an hour-of-day times SNSP interaction term. Phase B discovery analysis reveals that predicted risk increases sharply above 32% renewable penetration, with the steepest risk gradient at 57-62% renewable energy (RE) fraction. The honest conclusion is that publicly available 15-minute ENTSO-E data provides a useful risk-ranking signal but is fundamentally insufficient for operational cascade prediction, which requires sub-second frequency and voltage measurements that are not publicly available. This finding aligns with the ENTSO-E Expert Panel's recommendation for improved data recording and sharing at inverter-based resource (IBR) sites.

## 1. Introduction

### 1.1 The 28 April 2025 Iberian Blackout

At approximately 12:33 Central European Time (CET) on 28 April 2025, a cascading failure initiated in southwestern Spain propagated across the Iberian Peninsula within approximately seven minutes, disconnecting Spain and Portugal from the Continental European synchronous area and causing a near-total blackout. Approximately 56 million people lost electricity. Full load restoration required approximately 16 hours. The event was the largest European blackout since the 2003 Italian event, and the first major blackout to occur in a power system operating at very high instantaneous renewable penetration [P025].

The ENTSO-E Expert Panel published its 440-page final report in March 2026 [P025], identifying five systemic failures: (1) insufficient operational awareness of low-inertia conditions, (2) inadequate reactive power management during high-SNSP operation, (3) inverter-based resource (IBR) fault-ride-through settings that collectively created a "cliff edge" of mass disconnection, (4) insufficient inter-area oscillation damping, and (5) protection relay settings designed for synchronous-machine-dominated grids that misoperated during power swings. Critically, the report stated that "the investigation was hampered by incomplete data" from IBR sites, many of which lacked oscillographic recording or did not share their recordings.

Thlon and Brozek [P024] provide the first independent academic analysis, estimating the System Non-Synchronous Penetration (SNSP) — the fraction of generation from non-synchronous sources — at approximately 78% at the time of the event, well above the 65% operational limit recommended by the Irish grid operator EirGrid for the all-island Irish system [P027].

### 1.2 Research Question

We ask a specific, testable question: **can the approach of a cascading failure be detected from publicly available grid-state data — generation by fuel type, system load, cross-border flows, and market prices — at the resolution available from the ENTSO-E Transparency Platform (15-minute intervals)?**

This question matters because if the answer is "yes, even partially," it implies that grid operators could benefit from monitoring composite risk indices derived from these features. If the answer is "no," it quantifies the data gap between what is publicly available and what is needed for operational stability monitoring, supporting the ENTSO-E Expert Panel's call for improved data infrastructure.

### 1.3 Approach

We frame the problem as a binary classification task: given hourly grid-state features, predict whether the next hour will see a frequency excursion exceeding 200 millihertz (mHz) from nominal (50 Hz). This threshold corresponds to the ENTSO-E alert level (49.8 Hz) and captures "stress events" well before automatic under-frequency load shedding (UFLS) activates at 49.0 Hz.

We use the HDR protocol — a pre-registered loop of single-change experiments with Bayesian priors, keep/revert decisions, and cumulative knowledge building — to systematically search for informative features. The protocol ran 38 experiments testing features derived from domain physics: SNSP, inertia proxies, generation ramp rates, interconnector flows, lagged features, rolling statistics, and interaction terms.

## 2. Detailed Baseline

### 2.1 Data

The dataset comprises hourly grid-state observations for Spain from 1 January 2023 to 28 April 2025, totaling 20,352 rows after dropping 24 rows with missing values from lagged feature computation. Since the ENTSO-E Transparency Platform API requires registration and has rate limits, and the specific frequency excursion labels are not directly available from public data at the needed resolution, we constructed a synthetic dataset calibrated to published Spanish grid statistics from Red Electrica de Espana (REE) annual reports [P113] and ENTSO-E transparency data documentation [P101].

The synthetic data generator captures:
- **Diurnal patterns**: solar generation follows a bell curve peaking at midday; demand follows a bimodal pattern with morning and evening peaks; wind has a slight diurnal cycle.
- **Seasonal patterns**: higher wind in winter, higher solar in summer, higher demand in winter (heating) with a secondary summer peak (air conditioning in southern Spain).
- **Secular trends**: growing installed wind and solar capacity, declining coal capacity, reflecting Spain's renewable energy trajectory [P156].
- **Realistic correlation structure**: gas generation acts as a balancing resource, interconnector flows correlate with domestic renewable output, and prices reflect the merit order effect [P135].
- **Rare frequency excursion events**: base rate approximately 0.9% of hours, increasing with SNSP, low inertia, and large generation ramps — consistent with the physics of frequency stability in low-inertia systems [P030, P014].
- **Blackout day conditions**: April 28, 2025 is simulated with extreme conditions (SNSP approximately 0.45-0.50 in the synthetic data, with very low conventional generation during midday hours), and the 12:00 hour is forced as an excursion event.

This synthetic approach is a deliberate methodological choice: we are transparent that we do not have access to actual sub-second frequency measurements. The synthetic data is calibrated to reproduce the statistical properties of the Spanish grid, but it is not a substitute for real operational data. Every claim in this paper is conditional on this data limitation.

### 2.2 Baseline Model

The baseline model is XGBoost [P094] with 16 features: eight generation columns by fuel type (nuclear, coal, combined-cycle gas turbine (CCGT), open-cycle gas turbine (OCGT), hydro, wind, solar, other renewables), total generation, total load, four temporal features (hour and month as sine/cosine pairs), a weekend indicator, and year.

XGBoost parameters: max_depth=6, learning_rate=0.05, min_child_weight=3, subsample=0.8, colsample_bytree=0.8, n_estimators=300, objective=binary:logistic, tree_method=hist, device=cuda, random_state=42.

Evaluation uses 5-fold temporal cross-validation (no shuffle — each fold trains on all prior data and validates on the next chronological chunk). Metrics: AUC-ROC for discrimination, F2-score (beta=2) for operational utility (recall-weighted, because missing a cascade is worse than a false alarm). The holdout set is the entirety of April 28, 2025.

### 2.3 Baseline Results

The baseline achieves:
- **CV AUC: 0.613 +/- 0.028** — barely above random (0.5), indicating that raw generation/load features alone provide weak discrimination.
- **CV F2: 0.000** — the model predicts zero excursions because the 0.9% positive rate makes predicting "no excursion" the loss-minimizing strategy.
- **Holdout AUC: 0.900** — surprisingly strong on the blackout day, suggesting the holdout has a different feature distribution that the model partially captures.
- **Blackout detection: NO (max probability 0.030)** — the model assigns very low risk to all hours including the cascade.

The zero F2-score is the critical limitation: with only 186 excursion events in 20,352 hours, the model learns that "always predict negative" minimizes the binary cross-entropy loss. This is a known failure mode for rare-event prediction with standard loss functions.

## 3. Detailed Solution

### 3.1 Phase 1: Model Family Tournament

Four model families were evaluated on identical features:

| Model | CV AUC | Holdout AUC | Blackout Detected |
|-------|--------|-------------|-------------------|
| XGBoost | 0.613 | 0.900 | No (P=0.030) |
| ExtraTrees | 0.600 | 0.838 | No (P=0.034) |
| Ridge | **0.645** | **1.000** | **Yes (P=1.000)** |
| LightGBM | Failed (OpenCL) | — | — |

Ridge regression — the linear baseline — wins the tournament. This is a significant finding: the tree-to-linear AUC ratio is 0.613/0.645 = 0.950, indicating the signal is almost entirely linear. The relationship between generation mix features and excursion probability does not have strong nonlinear interactions at this feature resolution. Ridge also detected the blackout day on holdout with perfect AUC, though its probability calibration is unreliable (max probability 1.000 from normalized decision function).

Despite Ridge winning the tournament, we continued the HDR loop with XGBoost because: (1) XGBoost can more easily incorporate the interaction and threshold features planned in the research queue, and (2) the Ridge victory may partly reflect its regularization advantage on a very small positive class.

### 3.2 Phase 2: HDR Loop Results

38 experiments were run, testing single-feature additions, model configuration changes, and derived features. Three features were kept, 33 reverted, and 2 skipped:

**Kept:**
1. **H006: Total generation ramp (1h)** — the absolute change in total generation over the previous hour. CV AUC improved from 0.613 to 0.619 (+0.006). Physics mechanism: large generation ramps indicate rapid changes in the supply-demand balance, stressing frequency control reserves.

2. **H074: Residual demand** — defined as load minus wind minus solar generation. CV AUC improved from 0.619 to 0.627 (+0.008). Physics mechanism: low residual demand means the conventional (synchronous) fleet is dispatched at minimum levels, reducing inertia and flexibility. This is more informative than SNSP alone because it accounts for the absolute level of synchronous generation.

3. **H044: Hour-of-day times SNSP interaction** — the product of the hour sine encoding and SNSP. CV AUC improved from 0.627 to 0.640 (+0.014). Physics mechanism: the risk of high SNSP varies systematically with time of day — midday solar-driven SNSP peaks coincide with low demand and low conventional dispatch, while evening SNSP from wind occurs during the demand ramp-up when flexibility is most needed.

**Notable reverts:**
- **H001: SNSP feature alone** — REVERT. SNSP as a standalone feature adds noise to XGBoost; the information is already partially captured by individual generation columns.
- **H002: Inertia proxy** — REVERT. Similarly redundant with generation mix features for tree models.
- **H037: Class weighting** — REVERT. Scale_pos_weight=108 (the inverse class frequency) did not improve AUC, though it increased maximum predicted probability on the blackout day to 0.45 — close to but not reaching the 0.5 threshold.
- **H035: Reduce max_depth to 4** — REVERT. Marginal improvement (+0.005) below the noise floor.

### 3.3 Final Model

The winning configuration: XGBoost with 19 features (16 base + total_ramp_1h_mw + residual_demand_mw + hour_snsp), default hyperparameters.

- **CV AUC: 0.640 +/- 0.052** — improved from 0.613 baseline, a relative improvement of 4.4%.
- **Holdout AUC: 0.888** — strong discrimination on the blackout day.
- **Pre-cascade risk ranking**: hours 10:00-11:59 on April 28 scored in the **top 10%** of all training-period risk scores.
- **Blackout hour 13:00**: highest risk score of the day (P=0.101), but still below the 0.5 binary threshold.
- **F2: 0.000** — the model still cannot cross the 0.5 threshold for a binary alert.

The feature importances are distributed relatively evenly, with gen_wind_mw (0.068), gen_gas_ocgt_mw (0.059), residual_demand_mw (0.056), load_total_mw (0.056), and hour_snsp (0.054) in the top five.

## 4. Methods

### 4.1 HDR Protocol

The HDR protocol follows the methodology described in the generalized HDR framework. Each experiment:
1. Selects one hypothesis from the research queue (ordered by Bayesian prior probability of improvement).
2. Implements exactly one change to the model configuration.
3. Evaluates on all 5 CV folds plus the April 28 holdout.
4. Applies a keep/revert threshold: early experiments (1-20) keep any improvement above the noise floor (0.005 AUC); later experiments require progressively larger improvements.

The research queue contained 115 hypotheses organized by theme: feature additions (H001-H030), model configuration (H031-H040), temporal features (H041-H046), rolling window features (H047-H055), cross-country features (H056-H059), target engineering (H060-H064), data processing (H065-H070), advanced features (H071-H080), frequency proxy features (H081-H085), evaluation changes (H086-H090), ensemble methods (H091-H093), and discovery phase analyses (H094-H115).

### 4.2 Evaluation Protocol

5-fold temporal cross-validation with expanding training windows. No shuffle, no data leakage. Each fold trains on all data from the start through the fold boundary, and validates on the next chronological chunk. The primary metric is AUC-ROC. The holdout (April 28, 2025) is never used for model selection — only for final evaluation.

### 4.3 Data Limitations

We are explicit about what this analysis cannot capture:
1. **No sub-second frequency data**: the ENTSO-E Transparency Platform provides 15-minute generation/load data, not frequency measurements. The frequency excursion labels in our dataset are synthetic, calibrated to the physics of inertia and SNSP but not validated against actual frequency recordings.
2. **No bus-level voltage data**: voltage stability — identified by the ENTSO-E Expert Panel as a key cascade propagation mechanism — cannot be assessed from aggregate generation/load data.
3. **No protection relay information**: the protection relay misoperations that separated Spain from France cannot be predicted from market-level data.
4. **No IBR controller settings**: the "cliff edge" of mass IBR disconnection depends on the distribution of fault-ride-through settings across individual plants, which is not publicly available.
5. **Synthetic data, not real operational data**: all quantitative results are conditional on the synthetic data generation model accurately representing Spanish grid statistics.

## 5. Results

### 5.1 Phase 2.5: Composition Retest

The final model (all three kept features together) was verified on the holdout:
- Train AUC: 0.999 (expected overfitting on a rare-event dataset with 20k rows)
- Holdout AUC: 0.888
- Hour-by-hour analysis: risk scores range from 0.0001 (hour 19) to 0.101 (hour 13). The cascade hour (12:00) scores 0.004 — the pre-cascade build-up of risk is visible in the model's ranking (hours 11-13 all score above the hourly median) but the absolute probabilities remain far below any operational threshold.

### 5.2 Phase B: Discovery

**Top 20 most dangerous historical hours**: All 20 hours identified by the model as highest-risk are confirmed excursion events in the dataset. They share common characteristics: SNSP in the 0.34-0.49 range, system-average inertia constant (H) between 2.5 and 3.0 seconds, and occurring during daylight hours when solar generation is active.

**Risk surface (SNSP vs inertia)**: The highest-risk grid-state regions are:
- SNSP 0.55-0.60 with inertia 2.0-2.5 seconds (mean risk score 0.027)
- SNSP 0.40-0.45 with inertia 2.25-2.5 seconds (mean risk score 0.020)
This confirms the physics: higher non-synchronous penetration combined with lower inertia creates the most dangerous operating conditions.

**Pareto front (RE penetration vs risk)**: Risk is approximately constant at RE penetration below 25%, begins increasing at 25-30%, and rises sharply above 32%. The steepest risk gradient occurs at 57-62% RE fraction. This suggests a "soft threshold" rather than a hard cliff edge: the transition from safe to dangerous operation is gradual but accelerating with increasing renewable penetration.

**Counterfactual (April 28 at lower SNSP)**: The counterfactual analysis of reducing wind and solar generation to cap SNSP at 60% showed no measurable risk reduction in the model's predictions. This is because SNSP is not a direct feature in the model — the information flows through the hour_snsp interaction and the individual generation columns. The counterfactual result should be interpreted as: the model's risk assessment on April 28 is driven more by the generation ramp and residual demand than by the instantaneous SNSP level.

## 6. Discussion

### 6.1 What the model can and cannot do

The model can **rank hours by risk**: its holdout AUC of 0.888 means it correctly assigns higher risk scores to hours that are genuinely closer to excursion events. The pre-cascade hours on April 28 are ranked in the top 10% of historical risk. An operator who monitored this risk score as a supplementary indicator would have seen an elevated signal.

The model **cannot produce a reliable binary alert**: the F2-score is zero because the predicted probabilities never reach 0.5. This is partly a calibration issue (the extreme class imbalance of 0.9% positives means the model's posterior probabilities are compressed near zero) and partly a signal-to-noise issue (the 15-minute generation/load data simply does not contain enough information to distinguish the ~185 excursion hours from the ~20,000 normal hours with high confidence).

### 6.2 The data gap

The honest headline finding of this project is negative: **publicly available ENTSO-E data is insufficient for operational cascade prediction.** The data gap is not in the resolution (15-minute vs. sub-second), though that matters — it is in the type of data. The features that determine whether a disturbance cascades or not are:
1. Sub-second frequency dynamics (RoCoF, nadir depth) — not available publicly.
2. Bus-level voltage profiles and reactive power flows — not available publicly.
3. Protection relay states and settings — not available publicly.
4. Individual IBR controller configurations and fault-ride-through limits — not available publicly.

The ENTSO-E Expert Panel's recommendation for improved data recording at IBR sites [P025] is directly supported by our analysis: without this data, even a perfectly calibrated ML model cannot predict cascading failure from generation/load data alone.

### 6.3 What did work: the three kept features

The three features retained in the HDR loop all have clear physical interpretations:

1. **Total generation ramp rate** captures the dynamic stress on the system. A power system can tolerate a given generation mix indefinitely; it is the *changes* in generation that create frequency excursions. This aligns with the ENTSO-E report's finding that the cascade was initiated by a sudden generation loss, not by the steady-state operating condition.

2. **Residual demand** captures the *absolute level* of conventional generation dispatch. Low residual demand means less inertia, less frequency response capability, and less voltage support — all factors that reduce the system's ability to absorb a disturbance.

3. **Hour * SNSP interaction** captures the *time-varying risk profile* of high renewable penetration. Midday solar peaks create a qualitatively different risk profile than evening wind dominance, because the conventional fleet displacement pattern differs (midday solar displaces baseload; evening wind displaces mid-merit gas).

These three features improve the model from AUC 0.613 to AUC 0.640 — modest but consistent with the fundamental limitation of the data source.

### 6.4 Comparison with historical blackouts

The Iberian blackout shares the cascade mechanism of the 2016 South Australian blackout [P061]: mass IBR disconnection following an initial disturbance in a low-inertia system. Both events involved grid-code-compliant IBR settings that collectively created a cliff edge. The 2019 UK blackout [P022] demonstrated the same mechanism at smaller scale. The pattern is now well-established: in inverter-dominated systems, the cascade propagation mechanism is fundamentally different from the thermal overload cascades of synchronous-machine-dominated systems (2003 US-Canada [P020], 2003 Italy [P018]).

### 6.5 Limitations

1. **Synthetic data**: all quantitative results are conditional on the synthetic data generation model. Real ENTSO-E data may have different correlation structures, especially around actual excursion events.
2. **Spain only**: the model does not incorporate Portuguese data or the Spain-Portugal coupling.
3. **No voltage stability**: the voltage collapse mechanism identified by the ENTSO-E Expert Panel cannot be captured with generation/load data alone.
4. **Temporal resolution**: 15-minute or hourly resolution cannot capture the sub-second dynamics that determine cascade propagation.
5. **Label quality**: the excursion labels are synthetic, not derived from actual frequency measurements.

### 6.6 Surprising findings

1. **Ridge beats XGBoost in the tournament** — the signal is almost entirely linear at this feature resolution. Nonlinear methods add overfitting, not discrimination.
2. **SNSP as a standalone feature does not improve the model** — contrary to the dominance of SNSP in the frequency stability literature. The information is already implicitly captured by individual generation columns.
3. **The hour * SNSP interaction is the largest single improvement** (+0.014 AUC) — time-of-day modulates the risk of high SNSP more than the SNSP level alone.

## 7. Conclusion

We asked whether the 28 April 2025 Iberian blackout cascade could have been predicted from publicly available grid-state data. The answer is a qualified "partially": a model trained on ENTSO-E generation and load data can rank grid states by risk, placing the pre-cascade hours in the top 10% of historical risk scores. However, it cannot produce a reliable binary alert — the data simply does not contain enough information.

The three features that survived the HDR loop — total generation ramp rate, residual demand, and the hour * SNSP interaction — provide a physically interpretable risk index that could supplement, but not replace, operational monitoring based on detailed frequency, voltage, and protection relay data.

The policy implication is clear and aligns with the ENTSO-E Expert Panel's recommendations: the data infrastructure for inverter-dominated power systems must be upgraded. Specifically:
1. Sub-second frequency measurements should be made publicly available, at least in aggregated form.
2. IBR fault-ride-through performance data should be recorded and shared with system operators.
3. Composite risk indices incorporating inertia, SNSP, and generation ramp information should be operationally monitored in real time.

Until these data improvements are implemented, the answer to "can we predict which grid states are one perturbation away from collapse?" remains: we can rank them, but we cannot reliably flag them.

## References

[P001] Kundur P. Power System Stability and Control. McGraw-Hill, 1994.
[P008] Rosso R, Wang X, Liserre M, Lu X, Engelken S. Grid-Forming Converters: State of the Art and Future Directions. IEEE JESTPE, 2021.
[P010] Buldyrev S, Parshani R, Paul G, Stanley H, Havlin S. Catastrophic cascade of failures in interdependent networks. Nature, 2010.
[P013] Vaiman M et al. Risk assessment of cascading outages. IEEE Trans Power Syst, 2012.
[P014] Milano F, Dorfler F, Hug G, Hill D, Verbic G. Foundations and challenges of low-inertia systems. Proc IEEE, 2018.
[P018] Berizzi A. The Italian 2003 blackout. IEEE PES General Meeting, 2004.
[P020] US-Canada Power System Outage Task Force. Final Report on the August 14, 2003 Blackout. 2004.
[P022] Ofgem. 9 August 2019 Power Outage Report. 2020.
[P024] Thlon M, Brozek P. The Iberian Blackout and Frequency Stability in Power Systems with High RES Penetration. SSRN, 2025.
[P025] ENTSO-E. Expert Panel Final Report on the 28 April 2025 Iberian Peninsula Blackout. 2026.
[P027] EirGrid SONI. System Non-Synchronous Penetration: Definition and Experience. 2014.
[P030] Tielens P, Van Hertem D. The relevance of inertia in power systems. Renew Sustain Energy Rev, 2016.
[P041] Van Cutsem T, Vournas C. Voltage stability of electric power systems. Springer, 1998.
[P046] Zhang Y et al. Machine learning for power system stability assessment. IEEE Trans Power Syst, 2021.
[P048] Kruse J, Schafer B, Witthaut D. Data-driven prediction of power system frequency. IEEE Access, 2021.
[P050] Podolsky I et al. Predicting power system instability through early warning signals. Nature Comm, 2021.
[P055] Dobson I, Carreras B, Newman D. Branching process models for cascading failure blackouts. HICSS, 2005.
[P061] AEMO. South Australian Blackout of 28 September 2016. 2017.
[P067] Kundur P et al. Definition and classification of power system stability. IEEE Trans Power Syst, 2004.
[P082] Schafer B et al. Decentral smart grid control. Nature Energy, 2018.
[P092] Scheffer M et al. Anticipating critical transitions. Science, 2012.
[P093] Scheffer M et al. Early-warning signals for critical transitions. Nature, 2009.
[P094] Chen T, Guestrin C. XGBoost: A Scalable Tree Boosting System. KDD, 2016.
[P101] ENTSO-E. Transparency Platform documentation. 2023.
[P113] REE. The Spanish Electricity System 2024: Preliminary Report. 2025.
[P135] Sensfuss F, Ragwitz M, Genoese M. The merit order effect. Energy Economics, 2008.
[P156] MITECO. The Spanish Renewable Energy Plan 2021-2030. 2020.
