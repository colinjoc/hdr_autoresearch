# Observations — Flight Delay Propagation

## Data Observations

1. **The synthetic dataset produces reasonable delay distributions** but the mean delay (23.1 min) is higher than typical BTS annual mean (~7-8 min). This is because the synthetic generator does not model the "on-time" peak (most flights are 0-5 min early) as sharply as real BTS data. Real BTS data has a sharp spike at 0 and a long right tail; the synthetic data is smoother.

2. **Tail number rotation chains work correctly**: first legs have `prev_leg_arr_delay = 0`, subsequent legs inherit delay from prior legs with partial absorption. The absorption depends on carrier buffer factor.

3. **The delay cause code decomposition differs from BTS published proportions**: our synthetic data shows 31.8% late aircraft vs BTS published ~35%. This is close but could be improved. The carrier fraction (57%) is higher than BTS (~30%) because our "carrier" bin includes everything not attributed to the other causes.

4. **Feature importance is extremely concentrated**: the top 3 features (all propagation-related) account for >80% of XGBoost importance. This suggests the prediction task is dominated by a single mechanism.

5. **The tournament revealed that Ridge (linear regression) is competitive**, with CV MAE 20.63 vs XGBoost 20.88. This is remarkable because it means the entire delay propagation signal is approximately linear: `arr_delay ≈ w1 * prev_delay + w2 * buffer + w3 * congestion + ...`

## Gaps and Limitations

1. **Synthetic data limitation**: All quantitative claims are conditional on the synthetic data generator faithfully representing real BTS dynamics. The generator captures first-order effects (propagation through rotation chains, time-of-day accumulation, hub congestion) but may miss second-order effects (weather correlation across airports, crew fatigue patterns, gate conflict cascades).

2. **No weather data**: The baseline does not incorporate actual METAR weather observations. The BTS `WEATHER_DELAY` cause code is a noisy proxy. Phase 2 hypothesis: join NOAA ISD data by airport and date/hour for direct weather features.

3. **Gate conflict data not available**: BTS does not report gate numbers. Gate conflicts (two flights scheduled at the same gate within close time windows) are a known delay source but cannot be modeled from BTS data alone.

4. **Crew pairing not observable**: BTS does not report crew assignments. Crew-related delays are lumped into "carrier delay." A proxy (same-carrier flights arriving at same airport within +/- 90 min) could capture some crew-swap delay.

5. **Self-reported delay causes**: BTS delay cause codes are airline-reported and known to be biased. Airlines may systematically underreport "carrier delay" by reclassifying as "NAS delay" or "weather delay." The model-based R2 decomposition is more objective but has its own limitations (correlation vs causation).

## Ideas for Future Work

1. **Real BTS data validation**: Download 3 months of actual BTS data and compare synthetic vs real delay distributions, feature importances, and model performance. This would validate or invalidate the synthetic approach.

2. **Crew propagation proxy**: Engineer a feature counting same-carrier flights arriving at the same airport within +/- 90 minutes of the current flight's departure. If crew are swapping between flights, this proxy may capture the delay.

3. **Network centrality features**: Compute PageRank, betweenness centrality, and degree centrality for each airport in the daily flight network. Highly central airports may propagate delay more effectively.

4. **Weather persistence feature**: For airports with METAR data, compute whether bad weather at departure time is still present 2 hours later. Persistent weather events cause sustained cascades; passing storms allow recovery.

5. **Cascade depth**: Trace delay propagation backwards through the rotation chain to find the root-cause leg. Does knowing the cascade depth (this is the 4th leg affected) improve prediction beyond just knowing the previous leg's delay?
