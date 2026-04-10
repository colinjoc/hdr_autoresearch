# Research Queue: Iberian Blackout Cascade Prediction

## Status Legend
- OPEN: not yet tested
- KEEP: tested, improved score, change retained
- REVERT: tested, did not improve, change reverted
- DEFER: blocked on data or dependency

## Feature Engineering Hypotheses

### H001: Add SNSP feature
- **Variable**: snsp = (wind + solar + import) / (total_gen + import)
- **Prior**: 65% — SNSP is the most-cited risk factor; should be a strong predictor
- **Mechanism**: Higher SNSP means less synchronous inertia, greater vulnerability to disturbances
- **Metric**: AUC improvement on frequency excursion classification
- **Status**: OPEN

### H002: Add inertia proxy
- **Variable**: inertia_proxy_mws = nuclear*6 + coal*5 + gas*4 + hydro*3.5
- **Prior**: 60% — direct physics relationship between inertia and frequency stability
- **Mechanism**: Lower inertia means faster frequency decline for same power imbalance
- **Status**: OPEN

### H003: Add generation diversity index
- **Variable**: gen_diversity_shannon
- **Prior**: 40% — intuitively sensible but may be redundant with individual fuel types
- **Mechanism**: Low diversity means correlated generation loss risk
- **Status**: OPEN

### H004: Add wind ramp rate (1h)
- **Variable**: wind_ramp_1h_mw
- **Prior**: 50% — rapid wind changes stress frequency response
- **Mechanism**: Large wind ramps require compensating generation; if insufficient, frequency excursion
- **Status**: OPEN

### H005: Add solar ramp rate (1h)
- **Variable**: solar_ramp_1h_mw
- **Prior**: 45% — solar ramps are more predictable (sunset) but cloud events cause fast ramps
- **Mechanism**: Similar to wind ramps
- **Status**: OPEN

### H006: Add total generation ramp rate
- **Variable**: total_ramp_1h_mw
- **Prior**: 55% — net ramp captures all sources of imbalance
- **Mechanism**: Total system ramp indicates dynamic stress regardless of source
- **Status**: OPEN

### H007: Add max 15-minute ramp
- **Variable**: max_ramp_15min_mw
- **Prior**: 50% — captures steepest recent change
- **Mechanism**: Short sharp ramps are the most dangerous for frequency
- **Status**: OPEN

### H008: Add SNSP 1-hour lag
- **Variable**: snsp_lag_1h
- **Prior**: 40% — persistence feature; may help if SNSP trends are informative
- **Mechanism**: SNSP trend indicates direction of system vulnerability evolution
- **Status**: OPEN

### H009: Add SNSP 6-hour lag
- **Variable**: snsp_lag_6h
- **Prior**: 35%
- **Status**: OPEN

### H010: Add SNSP 24-hour lag
- **Variable**: snsp_lag_24h
- **Prior**: 30% — daily cycle may already be captured by temporal features
- **Status**: OPEN

### H011: Add SNSP rate of change (1h delta)
- **Variable**: snsp_delta_1h = snsp(t) - snsp(t-1h)
- **Prior**: 50% — rate of change may matter more than level
- **Mechanism**: Rapidly increasing SNSP means inertia is declining fast
- **Status**: OPEN

### H012: Add SNSP rate of change (6h delta)
- **Variable**: snsp_delta_6h
- **Prior**: 35%
- **Status**: OPEN

### H013: Add inertia 1-hour lag
- **Variable**: inertia_lag_1h
- **Prior**: 35%
- **Status**: OPEN

### H014: Add inertia rate of change (1h delta)
- **Variable**: inertia_delta_1h
- **Prior**: 45% — declining inertia trend may precede excursions
- **Mechanism**: If inertia is dropping, system is becoming more vulnerable
- **Status**: OPEN

### H015: Add Spain-France flow
- **Variable**: flow_es_fr_mw
- **Prior**: 55% — flow level affects loss-of-import risk
- **Mechanism**: Large import means large potential deficit if interconnector trips
- **Status**: OPEN

### H016: Add Spain-Portugal flow
- **Variable**: flow_es_pt_mw
- **Prior**: 40% — less critical interconnection for cascade risk
- **Status**: OPEN

### H017: Add net import to Iberian peninsula
- **Variable**: net_import_mw
- **Prior**: 50% — total exposure to interconnection loss
- **Status**: OPEN

### H018: Add flow-to-NTC ratio (Spain-France)
- **Variable**: flow_magnitude_ratio = |flow_es_fr| / NTC
- **Prior**: 45% — operating near transfer limit increases separation risk
- **Mechanism**: High utilization of interconnector means less margin for power swings
- **Status**: OPEN

### H019: Add flow reversal indicator (6h)
- **Variable**: flow_es_fr_reversed_6h
- **Prior**: 30% — speculative; may indicate dispatch instability
- **Status**: OPEN

### H020: Add day-ahead price
- **Variable**: price_day_ahead_eur
- **Prior**: 40% — low/negative prices indicate high RE, potential stress
- **Mechanism**: Negative prices indicate excess generation, possible curtailment, stressed dispatch
- **Status**: OPEN

### H021: Add generation-load imbalance
- **Variable**: gen_load_imbalance_mw
- **Prior**: 55% — direct power balance indicator
- **Mechanism**: Large imbalance means the system is already stressed
- **Status**: OPEN

### H022: Add ramp-to-inertia ratio
- **Variable**: ramp_to_inertia_ratio = max_ramp / inertia_proxy
- **Prior**: 60% — combines ramp stress with inertia availability
- **Mechanism**: Same ramp is more dangerous in a low-inertia system
- **Status**: OPEN

### H023: Add synchronous generation fraction
- **Variable**: synchronous_fraction = (nuclear + coal + gas + hydro) / total_gen
- **Prior**: 45% — may be redundant with SNSP but captures inertia providers directly
- **Status**: OPEN

### H024: Add Herfindahl-Hirschman Index
- **Variable**: gen_hhi = sum(p_i^2)
- **Prior**: 30% — likely redundant with Shannon diversity
- **Status**: OPEN

### H025: Add kinetic energy estimate
- **Variable**: kinetic_energy_gwh = inertia_proxy_mws / 3600
- **Prior**: 25% — may be redundant with inertia_proxy_s, just scaled differently
- **Status**: OPEN

### H026: SNSP squared (nonlinear)
- **Variable**: snsp_squared = snsp^2
- **Prior**: 35% — if there's a threshold effect, polynomial may help
- **Mechanism**: Risk may increase nonlinearly above a SNSP threshold (~65%)
- **Status**: OPEN

### H027: SNSP * inertia interaction
- **Variable**: snsp_times_inertia = snsp * inertia_proxy_s
- **Prior**: 40% — interaction captures the joint effect
- **Mechanism**: High SNSP combined with low inertia is worse than either alone
- **Status**: OPEN

### H028: SNSP * flow interaction
- **Variable**: snsp_times_flow = snsp * |flow_es_fr|
- **Prior**: 35% — high SNSP plus high import = double vulnerability
- **Status**: OPEN

### H029: SNSP > 0.65 binary threshold
- **Variable**: snsp_above_65pct = (snsp > 0.65)
- **Prior**: 45% — EirGrid's operational threshold; may help as explicit feature
- **Mechanism**: Known operational boundary for frequency stability risk
- **Status**: OPEN

### H030: SNSP > 0.75 binary threshold
- **Variable**: snsp_above_75pct = (snsp > 0.75)
- **Prior**: 40% — more extreme threshold; April 28 was at 78%
- **Status**: OPEN

## Model Configuration Hypotheses

### H031: Switch to LightGBM
- **Prior**: 45% — often competitive with XGBoost, sometimes faster
- **Status**: OPEN

### H032: Switch to ExtraTrees
- **Prior**: 40% — may be better for small N or noisy features
- **Status**: OPEN

### H033: Switch to Ridge regression
- **Prior**: 20% — linear baseline sanity check
- **Status**: OPEN

### H034: Increase n_estimators from 300 to 600
- **Prior**: 30% — diminishing returns likely
- **Status**: OPEN

### H035: Reduce max_depth from 6 to 4
- **Prior**: 35% — prevent overfitting on small excursion event count
- **Status**: OPEN

### H036: Increase max_depth to 8
- **Prior**: 25% — risk of overfitting
- **Status**: OPEN

### H037: Add class weight for imbalanced excursion events
- **Prior**: 55% — excursion events are ~1-3% of hours; class weighting should help AUC
- **Mechanism**: Without weighting, model may learn to predict "no excursion" always
- **Status**: OPEN

### H038: Use SMOTE oversampling for excursion events
- **Prior**: 30% — often worse than class weighting for tree models
- **Status**: OPEN

### H039: Use focal loss equivalent (weighted by prediction confidence)
- **Prior**: 25% — speculative for tree models
- **Status**: OPEN

### H040: Optimize learning rate (try 0.01)
- **Prior**: 30%
- **Status**: OPEN

## Temporal Feature Hypotheses

### H041: Add hour-of-day as linear feature
- **Prior**: 40% — already have sin/cos encoding; explicit may help
- **Status**: OPEN

### H042: Add month as integer
- **Prior**: 30% — seasonal pattern may be captured better
- **Status**: OPEN

### H043: Add year as integer
- **Prior**: 45% — secular trend in RE penetration over years
- **Mechanism**: SNSP has trended upward from 2015 to 2025; year captures this
- **Status**: OPEN

### H044: Hour * SNSP interaction
- **Variable**: hour_snsp = hour_sin * snsp
- **Prior**: 40% — midday solar peak creates specific SNSP pattern
- **Mechanism**: Solar-driven SNSP peak at midday; interaction captures this
- **Status**: OPEN

### H045: Weekend * SNSP interaction
- **Variable**: weekend_snsp = is_weekend * snsp
- **Prior**: 30% — lower weekend demand may mean higher SNSP
- **Status**: OPEN

### H046: Season * SNSP interaction
- **Variable**: month_snsp = month_sin * snsp
- **Prior**: 35% — summer vs winter SNSP patterns differ
- **Status**: OPEN

## Rolling Window Features

### H047: 6-hour rolling mean of SNSP
- **Variable**: snsp_rolling_6h_mean
- **Prior**: 40% — smoothed SNSP may be more informative than instantaneous
- **Status**: OPEN

### H048: 6-hour rolling std of SNSP
- **Variable**: snsp_rolling_6h_std
- **Prior**: 45% — high variability in SNSP indicates rapidly changing conditions
- **Mechanism**: Analogy to critical slowing down: increased variance precedes transitions
- **Status**: OPEN

### H049: 24-hour rolling mean of SNSP
- **Variable**: snsp_rolling_24h_mean
- **Prior**: 35%
- **Status**: OPEN

### H050: 6-hour rolling std of total generation
- **Variable**: gen_total_rolling_6h_std
- **Prior**: 40% — generation variability as stress indicator
- **Status**: OPEN

### H051: 6-hour rolling max of wind ramp
- **Variable**: wind_ramp_rolling_6h_max
- **Prior**: 35% — captures worst recent ramp event
- **Status**: OPEN

### H052: 24-hour rolling mean of inertia proxy
- **Variable**: inertia_rolling_24h_mean
- **Prior**: 30% — smoothed inertia trend
- **Status**: OPEN

### H053: 6-hour rolling min of inertia proxy
- **Variable**: inertia_rolling_6h_min
- **Prior**: 45% — worst-case recent inertia level
- **Mechanism**: Minimum inertia in recent hours captures transient vulnerability windows
- **Status**: OPEN

### H054: 6-hour rolling std of interconnector flow
- **Variable**: flow_es_fr_rolling_6h_std
- **Prior**: 35% — flow variability indicates stressed interconnection
- **Status**: OPEN

### H055: 12-hour rolling mean of load
- **Variable**: load_rolling_12h_mean
- **Prior**: 25% — smoothed demand trend
- **Status**: OPEN

## Cross-Country Features (Spain + Portugal combined)

### H056: Add Portugal generation data alongside Spain
- **Prior**: 50% — Iberian system is coupled; Portugal data adds information
- **Mechanism**: Spain-Portugal flows depend on relative generation-load balance
- **Status**: OPEN

### H057: Portugal SNSP
- **Variable**: snsp_portugal
- **Prior**: 40% — Portuguese renewable penetration affects Iberian stability
- **Status**: OPEN

### H058: Combined Iberian SNSP
- **Variable**: snsp_iberian = (wind_ES + solar_ES + wind_PT + solar_PT) / (total_ES + total_PT)
- **Prior**: 50% — whole-peninsula metric may be more relevant for cascade risk
- **Status**: OPEN

### H059: Spain-Portugal flow balance indicator
- **Variable**: iberian_flow_balance = flow_es_pt / (gen_total_es - load_es)
- **Prior**: 30%
- **Status**: OPEN

## Target Engineering Hypotheses

### H060: Use 100 mHz excursion threshold instead of 200 mHz
- **Prior**: 35% — lower threshold captures more events but noisier
- **Status**: OPEN

### H061: Use 300 mHz excursion threshold instead of 200 mHz
- **Prior**: 30% — higher threshold, fewer positive events, may be too rare
- **Status**: OPEN

### H062: Use continuous target (max frequency deviation in mHz) with MAE metric
- **Prior**: 45% — regression may capture gradations that binary misses
- **Status**: OPEN

### H063: Use RoCoF > 0.5 Hz/s as excursion label
- **Prior**: 35% — RoCoF-based label captures inertia-related events specifically
- **Status**: OPEN

### H064: Multi-class target (normal/alert/critical)
- **Prior**: 25% — three classes may improve discrimination but harder to train
- **Status**: OPEN

## Data Processing Hypotheses

### H065: Use 1-hour aggregation instead of 15-minute
- **Prior**: 35% — smoother, fewer noisy features, but loses short-term dynamics
- **Status**: OPEN

### H066: Use 4-hour aggregation
- **Prior**: 20% — probably too coarse for cascade prediction
- **Status**: OPEN

### H067: Drop hours 0-5 (overnight, low solar, low risk)
- **Prior**: 30% — overnight hours may add noise without excursion events
- **Status**: OPEN

### H068: Only use daytime hours (6-22)
- **Prior**: 30% — solar-driven risk is daytime; but overnight events exist
- **Status**: OPEN

### H069: Normalize all features by installed capacity (not raw MW)
- **Prior**: 45% — accounts for capacity growth over the 2015-2025 period
- **Mechanism**: Raw MW values conflate system growth with operating state
- **Status**: OPEN

### H070: Log-transform generation values
- **Prior**: 25% — may help with skewed distributions
- **Status**: OPEN

## Advanced Feature Hypotheses

### H071: SNSP percentile within day (how extreme is current SNSP relative to today's range)
- **Prior**: 35%
- **Status**: OPEN

### H072: SNSP percentile within season (how extreme relative to seasonal norm)
- **Prior**: 40% — captures whether current SNSP is unusually high for the time of year
- **Status**: OPEN

### H073: "Solar duck curve" feature: rate of solar decline in late afternoon
- **Prior**: 45% — evening solar ramp-down is a known stress period
- **Mechanism**: Rapid solar decline requires fast-ramping replacement generation
- **Status**: OPEN

### H074: Residual demand = load - wind - solar
- **Variable**: residual_demand_mw
- **Prior**: 50% — standard grid planning metric; low residual demand means stressed conventional fleet
- **Status**: OPEN

### H075: Residual demand rate of change
- **Variable**: residual_demand_ramp_1h
- **Prior**: 45% — rate of change of residual demand = flexibility requirement
- **Status**: OPEN

### H076: Import dependency ratio = import / load
- **Prior**: 40% — high import dependency means vulnerability to interconnection loss
- **Status**: OPEN

### H077: Minimum synchronous generation in past 6 hours
- **Variable**: sync_gen_min_6h
- **Prior**: 40% — captures transient low-inertia windows
- **Status**: OPEN

### H078: Wind capacity factor
- **Variable**: wind_cf = gen_wind / installed_wind_capacity
- **Prior**: 35% — high wind CF with high SNSP may indicate specific risk
- **Status**: OPEN

### H079: Solar capacity factor
- **Variable**: solar_cf = gen_solar / installed_solar_capacity
- **Prior**: 30%
- **Status**: OPEN

### H080: Combined RE capacity factor
- **Variable**: re_cf = (gen_wind + gen_solar) / (installed_wind + installed_solar)
- **Prior**: 30%
- **Status**: OPEN

## Frequency Proxy Features (if actual frequency data unavailable)

### H081: Power balance error proxy
- **Variable**: pbe = (gen_total - load - exports) / gen_total
- **Prior**: 45% — approximates frequency deviation direction
- **Status**: OPEN

### H082: Power balance error variance (6h rolling)
- **Variable**: pbe_var_6h
- **Prior**: 50% — increased variance = critical slowing down signal
- **Mechanism**: Scheffer et al. (2009): rising variance precedes tipping points
- **Status**: OPEN

### H083: Power balance autocorrelation (6h rolling)
- **Variable**: pbe_autocorr_6h
- **Prior**: 45% — increased autocorrelation = critical slowing down
- **Mechanism**: Podolsky et al. (2021): autocorrelation rises before grid instability
- **Status**: OPEN

### H084: Expected RoCoF for largest credible contingency
- **Variable**: expected_rocof = largest_generator_mw / (2 * inertia_proxy_mws)
- **Prior**: 55% — direct physics-based vulnerability metric
- **Mechanism**: Predicts how severe a frequency decline would be for loss of largest online unit
- **Status**: OPEN

### H085: Inertia floor distance
- **Variable**: inertia_floor_dist = inertia_proxy_s - 3.0
- **Prior**: 40% — distance below safe operating inertia level
- **Mechanism**: H_sys < 3s is generally considered dangerous for CE synchronous area
- **Status**: OPEN

## Cross-Validation and Evaluation Hypotheses

### H086: Use 10-fold time-series CV instead of 5-fold
- **Prior**: 25% — more folds may give better CV estimate but each fold smaller
- **Status**: OPEN

### H087: Use expanding window CV instead of fixed-fold
- **Prior**: 35% — more realistic for deployment; always train on all past data
- **Status**: OPEN

### H088: Add F2-score as secondary metric (emphasize recall over precision)
- **Prior**: 40% — for a safety system, missing an event is worse than false alarm
- **Status**: OPEN

### H089: Use precision-recall AUC instead of ROC AUC
- **Prior**: 30% — PR-AUC better for imbalanced classes
- **Status**: OPEN

### H090: Weight CV by year (more weight to recent years)
- **Prior**: 25% — recent data may be more relevant due to changing generation mix
- **Status**: OPEN

## Ensemble and Stacking Hypotheses

### H091: Stack XGBoost + LightGBM predictions
- **Prior**: 30% — stacking often helps but may overfit on small event count
- **Status**: OPEN

### H092: Stack XGBoost + Ridge predictions
- **Prior**: 25% — tree + linear often complementary
- **Status**: OPEN

### H093: Separate models for high-SNSP and low-SNSP regimes
- **Prior**: 40% — regime-specific models may capture different physics
- **Mechanism**: The risk factors at SNSP < 50% vs SNSP > 65% are qualitatively different
- **Status**: OPEN

## Discovery Phase Hypotheses

### H094: Identify SNSP threshold above which predicted excursion risk exceeds X%
- **Prior**: N/A (discovery, not improvement)
- **Status**: OPEN

### H095: Map 2D risk surface: SNSP vs inertia proxy
- **Prior**: N/A (discovery)
- **Status**: OPEN

### H096: Reconstruct April 28 2025 grid state and check model prediction
- **Prior**: N/A (critical validation)
- **Status**: OPEN

### H097: Generate counterfactual: what if SNSP had been 60% on April 28?
- **Prior**: N/A (discovery)
- **Status**: OPEN

### H098: Generate Pareto front: RE penetration vs predicted stability margin
- **Prior**: N/A (discovery)
- **Status**: OPEN

### H099: Identify top-10 most dangerous historical hours (by model prediction) and check against known events
- **Prior**: N/A (validation)
- **Status**: OPEN

### H100: Feature importance permutation analysis for winning model
- **Prior**: N/A (interpretation)
- **Status**: OPEN

### H101: Partial dependence plots for SNSP, inertia, and flow features
- **Prior**: N/A (interpretation)
- **Status**: OPEN

### H102: SHAP analysis for April 28 prediction
- **Prior**: N/A (interpretation)
- **Status**: OPEN

### H103: Add Spanish-specific grid events as binary features (known maintenance, reported incidents)
- **Prior**: 25% — data may not be systematically available
- **Status**: DEFER

### H104: Add ERA5 weather features (wind speed, solar irradiance, temperature)
- **Prior**: 45% — weather drives RE output and demand; may add signal beyond generation data
- **Status**: OPEN

### H105: Add weather forecast error proxy (actual - day-ahead scheduled generation)
- **Prior**: 50% — forecast errors cause unplanned imbalances
- **Status**: OPEN

### H106: Cross-border scheduled vs actual flow difference
- **Prior**: 35% — unplanned flow deviations indicate stress
- **Status**: OPEN

### H107: Rolling max of SNSP in past 24h
- **Variable**: snsp_max_24h
- **Prior**: 35%
- **Status**: OPEN

### H108: Time since last SNSP > 65% event
- **Variable**: hours_since_high_snsp
- **Prior**: 30% — persistence of high-SNSP conditions
- **Status**: OPEN

### H109: Cumulative hours of SNSP > 65% in past 7 days
- **Variable**: cum_high_snsp_7d
- **Prior**: 35% — sustained high-SNSP operation may fatigue conventional fleet
- **Status**: OPEN

### H110: ENTSO-E frequency quality indicator (if available)
- **Prior**: 50% — direct signal if accessible
- **Status**: DEFER

### H111: Nuclear generation status change (plant trip indicator)
- **Variable**: nuclear_dropped_500mw_1h = nuclear decreased > 500 MW in 1 hour
- **Prior**: 45% — nuclear trip is a large single-unit loss event
- **Status**: OPEN

### H112: Large conventional plant trip indicator
- **Variable**: any_fuel_dropped_500mw_15min
- **Prior**: 50% — large rapid generation drops are cascade triggers
- **Status**: OPEN

### H113: Minimum residual demand in day so far
- **Variable**: min_residual_demand_today
- **Prior**: 30%
- **Status**: OPEN

### H114: Load forecast error proxy (load deviation from 7-day same-hour mean)
- **Variable**: load_deviation_from_weekly_mean
- **Prior**: 35% — unusual load may stress dispatch
- **Status**: OPEN

### H115: Iberian peninsula as isolated system indicator (France flow near zero)
- **Variable**: near_isolated = |flow_es_fr| < 100 MW
- **Prior**: 35% — near-zero France flow means Iberia is nearly islanded already
- **Status**: OPEN
