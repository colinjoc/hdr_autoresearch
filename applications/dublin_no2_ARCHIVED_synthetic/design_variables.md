# Design Variables / Feature Candidates — Dublin NO2

## Meteorological Features

| Feature | Source | Physics Justification |
|---------|--------|----------------------|
| wind_speed_ms | Met Eireann | Higher wind = better dispersion, lower surface NO2 |
| wind_dir_deg | Met Eireann | Determines which sources are upwind of the station |
| temperature_c | Met Eireann | Affects photochemistry (NO2-O3), heating demand, BLH |
| rainfall_mm | Met Eireann | Rain washout removes NO2; wet deposition |
| blh_proxy_m | Met Eireann/derived | Boundary layer height controls mixing volume |
| wind_dir_traffic | Derived | Cosine of angle from traffic corridor direction |
| wind_dir_port | Derived | Cosine of angle from Dublin Port direction |
| calm_wind | Derived | Binary: wind < 1.5 m/s (poor dispersion) |
| wind_x_blh | Derived | Ventilation index: wind speed x BLH |
| inverse_ventilation | Derived | 1 / (wind x BLH) — poor dispersion indicator |
| temp_inversion_proxy | Derived | Night + cold + calm = temperature inversion trapping |
| rain_washout | Derived | Normalised rainfall effect (0-1) |

## Temporal Features

| Feature | Source | Physics Justification |
|---------|--------|----------------------|
| hour_sin, hour_cos | Clock | Diurnal cycle: rush hours, photochemistry, heating |
| dow_sin, dow_cos | Calendar | Weekday traffic pattern |
| month_sin, month_cos | Calendar | Seasonal cycle: heating, photochemistry, BLH |
| is_weekend | Calendar | Reduced traffic on weekends |
| is_heating_season | Calendar | Oct-Mar: residential combustion contributes NOx |
| rush_hour | Derived | Binary: 7-9am or 4-7pm |
| rush_hour_weekday | Derived | Rush hour on weekday only (strongest traffic signal) |
| weekend_early_morning | Derived | Weekend 2-5am as "background NO2" estimator |

## Source-Specific Features

| Feature | Source | Physics Justification |
|---------|--------|----------------------|
| traffic_volume | DCC counters | Direct hourly vehicle count at nearest counter |
| diesel_fraction | CSO fleet data | Fraction of vehicles that are diesel (proxy by year) |
| port_activity | AIS / Dublin Port | Ships at berth, auxiliary engine emissions |
| heating_proxy | SEAI / derived | Temperature-dependent heating demand estimate |
| cold_evening | Derived | Heating season + cold + evening = peak heating |
| temp_heating_interaction | Derived | Heating season x (12 - temp) / 20 |
| is_lockdown | Calendar | COVID lockdown as natural experiment |
| year_trend | Calendar | Fleet electrification trend (2019-2025) |

## Station Features

| Feature | Source | Physics Justification |
|---------|--------|----------------------|
| station_* (one-hot) | Station ID | Fixed effects for station-specific mean NO2 level |
| station_type | Station metadata | Traffic vs suburban vs background vs industrial |

## Kept Features (Final Model)

After 16 experiments in the HDR loop:

1. **station_* one-hot encoding** (E01, KEEP) — Largest improvement: MAE 7.36 → 2.20
2. **rush_hour_weekday** (E03, KEEP) — Traffic timing signal: MAE 2.20 → 2.14
3. **year_trend** (E13, KEEP) — Fleet composition trend: MAE 2.14 → 2.01

## Reverted Features

- rush_hour: Redundant with rush_hour_weekday
- wind_dir_traffic, wind_dir_port: XGBoost learns wind_dir_deg splits implicitly
- cold_evening, temp_heating_interaction: XGBoost learns from is_heating_season × temperature
- calm_wind, wind_x_blh, inverse_ventilation: Captured by wind_speed × blh_proxy
- rain_washout: Weak signal, XGBoost handles rainfall_mm
- is_lockdown: Too few data points for reliable learning
- weekend_early_morning: Sparse signal
- rush_wind_dir_traffic: Interaction already learned by tree
- temp_inversion_proxy: Marginal improvement below noise floor
