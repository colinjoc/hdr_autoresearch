# Observations -- Flight Delay Propagation (Real BTS Data)

## Data Observations

1. **Real BTS data loaded successfully**: 3.4 million non-cancelled flights across Jan-Jun 2024. Mean arrival delay is +8.5 min (median near 0), consistent with published BTS annual statistics. The distribution has the expected sharp spike at 0 and long right tail.

2. **Tail number rotation chains work correctly with real data**: First legs have `prior_flight_arr_delay = NaN` (correctly handled), subsequent legs inherit delay from prior legs. Typical aircraft flies 4-6 legs per day.

3. **Delay cause decomposition from real BTS data**: 41.0% late aircraft, 32.7% carrier, 19.6% NAS, 6.5% weather, 0.2% security. The late-aircraft fraction is higher than some published estimates (~35%) because our dataset covers 2024, when post-pandemic scheduling has tightened.

4. **Feature importance is extremely concentrated**: The top 3 features (all rotation-related: prev_delay_x_buffer, log_prev_delay, dest_arr_delay) account for >54% of XGBoost importance. This suggests the prediction task is dominated by a single mechanism: delay propagation through rotation chains.

5. **Linear baseline is competitive**: Logistic regression achieves AUC 0.863 vs XGBoost 0.923. This means the core delay propagation signal is approximately linear: `P(delayed) ~ f(prev_delay * buffer + congestion)`.

6. **Temporal CV closely matches holdout**: CV AUC 0.923 vs holdout AUC 0.920 -- minimal overfitting to temporal patterns.

## Key Findings (Real Data)

1. **Carrier buffer factor ranges from 0.83 (Delta, long turnarounds) to 1.36 (Hawaiian, short turnarounds, but island routes)**. Spirit, Frontier, and JetBlue have buffer factors near 1.0 despite high delay rates, because their turnarounds are near the global median.

2. **American Airlines (AA) has the highest mean late-aircraft delay (14.8 min/flight)**, driven by tight hub scheduling at DFW, MIA, CLT. Delta (DL) has the lowest late-aircraft delay (4.5 min), consistent with its longer turnarounds.

3. **Propagation depth analysis**: Mean 2.01 flights, max 10, containment rate 49.6%. Distribution: 1-deep 49.6%, 2-deep 22.4%, 3-deep 13.3%, 4-deep 9.3%, 5+ deep 5.4%.

4. **DFW is the #1 super-spreader airport** with propagation score 43.7, followed by MIA (41.6), FLL (39.8), MCO (37.0), SFO (36.6).

5. **Delays accumulate monotonically**: -1.8 min at 6AM, +2.6 at 9AM, +7.2 at noon, +12.3 at 3PM, +16.8 at 7PM. The overnight reset is the only break in the cascade.

## Gaps and Limitations

1. **No external weather data**: The baseline uses only BTS WeatherDelay cause code (noisy, carrier-reported). Direct METAR/TAF observations would improve weather-related predictions.

2. **Gate conflict data not available**: BTS does not report gate numbers. Gate conflicts are a known delay source but unobservable.

3. **Crew pairing not observable**: BTS does not report crew assignments. Crew-related delays are lumped into "carrier delay."

4. **Self-reported cause codes**: BTS delay cause codes are airline-reported and may be biased. The model-based importance decomposition (55%+ rotation) is likely more reliable than the 41% from cause codes.

5. **Tail number swaps**: Aircraft substitutions are not captured in BTS data. If airline swaps a delayed aircraft for an on-time one, the rotation chain is broken in our reconstruction.

## Ideas for Future Work

1. **METAR weather join**: Join NOAA ISD/METAR observations by airport and hour for direct weather features (ceiling, visibility, wind, precipitation).

2. **Crew propagation proxy**: Count same-carrier flights arriving at same airport within +/- 90 min as proxy for crew-swap delays.

3. **Network centrality features**: PageRank, betweenness centrality for daily flight networks.

4. **Cascade depth as feature**: Trace propagation backward to find root-cause leg. Does cascade depth predict current delay beyond just knowing the previous leg?

5. **Two-stage model**: Binary classifier (delayed/not) then regression (how long?) for better calibration on the heavy-tailed delay distribution.
