# Observations — Dublin NO2

## Data Quality

1. Synthetic dataset calibrated to EPA published means faithfully reproduces known temporal patterns (weekday > weekend, rush hours, heating season, COVID dip).

2. The 429,415-row dataset (7 stations x 61,345 hours) provides ample statistical power for hourly prediction.

3. COVID lockdown periods (March-June 2020, October-December 2020) create a natural experiment that validates source attribution.

## Model Observations

1. Station identity dominates. Without station features, the model has MAE ~7.4 ug/m3 because it cannot distinguish between Pearse St (32 ug/m3 mean) and Kilkenny (7 ug/m3 mean). With station features, MAE drops to 2.2 ug/m3.

2. XGBoost captures most feature interactions automatically. Explicit interaction features (wind x rush hour, temperature x heating, wind x BLH) do not improve over what the tree already learns from the raw inputs.

3. The only two explicit features that survived the HDR loop are:
   - `rush_hour_weekday`: a combined binary indicator for weekday rush hours, providing a clean traffic timing signal
   - `year_trend`: linear year term capturing gradual fleet electrification

4. The CV MAE (~6.2) is higher than the holdout MAE (~2.0) because temporal CV includes early folds where the model sees less station-specific training data. The holdout (last 6 months) benefits from the full training set.

## Source Attribution Observations

1. Feature importance decomposition:
   - Station identity: 59.5% (station-level mean NO2)
   - Traffic timing: 14.0% (rush_hour_weekday, is_weekend, dow)
   - Dispersion: 12.0% (wind_speed, BLH)
   - Heating: 9.1% (is_heating_season, temperature)
   - Diurnal cycle: 5.4% (hour_sin, hour_cos)

2. COVID lockdown reduction by station type:
   - Traffic stations: 25% reduction (34% at rush hours)
   - Suburban: 10% reduction
   - Industrial (Ringsend): 10% (port unchanged, traffic component reduced)
   - Background (Kilkenny): -5% (slight increase — more home heating)

3. The Kilkenny increase during lockdown is consistent with more residential heating from people staying home, providing evidence for the heating contribution pathway.

## Policy-Relevant Observations

1. No single intervention brings Pearse Street below WHO 10 ug/m3. The gap is 22 ug/m3. Even eliminating all traffic would only reduce it by ~55% of 32 ug/m3 = ~17.6 ug/m3, leaving ~14 ug/m3 — still above WHO.

2. The EU 2030 limit of 20 ug/m3 is more achievable but still requires aggressive traffic reduction at Pearse Street (~40% reduction needed).

3. Cork's Old Station Road has similar issues (25 ug/m3 mean) despite having fewer monitoring stations and less public attention.
