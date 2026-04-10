# Knowledge Base: Iberian Blackout Cascade Prediction

## Power System Stability Fundamentals

### Frequency Stability
- **Swing equation**: 2H/omega_s * d^2(delta)/dt^2 = P_m - P_e - D * d(delta)/dt
- **RoCoF**: Rate of Change of Frequency = -Delta_P / (2 * H_sys), where H_sys is system-wide inertia constant
- **Frequency nadir**: minimum frequency after disturbance; depends on inertia (sets initial slope) and primary response (sets arrest point)
- **Continental Europe nominal frequency**: 50.000 Hz
- **Normal operating band**: 50.000 +/- 0.050 Hz (standard frequency range)
- **Alert threshold**: 49.800 Hz (triggers manual intervention)
- **UFLS Stage 1**: typically 49.0 Hz (automatic load shedding begins)
- **UFLS Stage 2**: typically 48.5 Hz
- **UFLS Stage 3**: typically 48.0 Hz
- **Generator protection trip**: typically 47.5 Hz
- **Typical H constants by fuel**: nuclear 5-7s, coal 4-6s, CCGT 3-5s, OCGT 2-4s, hydro 2-4s

### Voltage Stability
- **P-V curve**: active power vs voltage at a bus; nose point is maximum loadability
- **Q-V curve**: reactive power vs voltage at a bus; minimum reactive power support needed
- **Voltage collapse**: occurs when load exceeds reactive power delivery capacity of network
- **Typical voltage limits**: 0.95-1.05 p.u. for normal operation; <0.85 p.u. triggers protection
- **OLTC mechanism**: on-load tap changers attempt to restore downstream voltage by adjusting transformer ratio; this increases upstream current, which can depress upstream voltage if near collapse margin

### System Strength
- **Short Circuit Ratio (SCR)**: ratio of short-circuit MVA at connection point to rated MVA of IBR plant
- **SCR < 3**: weak grid, challenging for grid-following inverters
- **SCR < 2**: very weak grid, stability not guaranteed without special measures
- **Effective SCR (ESCR)**: accounts for mutual interaction of multiple IBR plants at nearby buses

## Key Metrics

### System Non-Synchronous Penetration (SNSP)
- SNSP = (wind + solar + HVDC_import) / (total_generation + HVDC_import)
- EirGrid operational limit: 75% (being pushed to 80% with mitigations)
- Spanish SNSP on 28 April 2025: ~78%
- SNSP > 65% requires active management (synchronous condensers, grid-forming, FFR)

### Inertia Proxy
- H_sys_proxy = sum(P_fuel_type * H_typical_fuel_type) / sum(P_fuel_type)
- Where P_fuel_type is active generation from each fuel type
- This underestimates if some synchronous machines are constrained on but at minimum load

### Generation Diversity Index
- Shannon entropy: H_diversity = -sum(p_i * log(p_i)) over fuel types
- Where p_i = P_fuel_i / P_total
- Low diversity (H < 1.0) indicates vulnerability to correlated generation loss

## 28 April 2025 Event Parameters
- Time of initiation: ~12:33 CET
- Pre-event SNSP: ~78%
- Pre-event synchronous inertia: H_sys ~ 2.5s (estimated)
- Initial power deficit: ~1.2 GW
- Spain-France flow: ~1.5 GW import (France to Spain)
- Total IBR disconnected in cascade: ~15 GW within 60 seconds
- Time to system separation (Spain from CE): ~30 seconds
- Time to total collapse: ~7 minutes
- Restoration time: ~16 hours for full load recovery
- People affected: ~56 million

## Frequency Excursion Definition (Our Prediction Target)
- **Positive label**: max |f - 50.0| > 0.200 Hz in a 1-hour window
- This corresponds to frequency outside [49.8, 50.2] Hz
- 49.8 Hz is the ENTSO-E alert threshold
- 50.2 Hz is the symmetric high-frequency alert
- This is a conservative threshold — it captures "stress events" well before UFLS activation

## Data Availability Notes (from ENTSO-E Transparency Platform)
- Generation by fuel type: 15-min resolution, available from 2015
- Total load: 15-min resolution, available from 2015
- Cross-border physical flows: 60-min resolution, available from 2015
- Day-ahead prices: 60-min resolution
- Frequency data: NOT directly on transparency platform for most areas; must use alternative sources
- Installed capacity by fuel: annual resolution

## What Works in ML Power System Prediction
- Tree ensembles (XGBoost, LightGBM) dominate tabular grid-state prediction tasks
- Lagged features (1h, 6h, 24h) capture persistence and trends
- Time-of-day and day-of-week features capture systematic dispatch patterns
- SNSP and inertia proxies are strong features when available
- Frequency statistics (std, autocorrelation) capture pre-disturbance stress
- Linear models (Ridge) provide useful baselines — if trees don't beat linear by >2x, the relationship is mostly linear

## What Doesn't Work / Known Limitations
- Neural networks overfit on small tabular grid datasets (N < 50k rows)
- Frequency excursion events are rare (~1-3% of hours) — class imbalance must be handled
- ENTSO-E data has gaps, reporting delays, and inconsistencies between control areas
- Frequency data may not be publicly available at the needed resolution
- Cross-border flows can differ between scheduled and physical; physical is what matters
- Without bus-level data, voltage stability prediction is infeasible — we focus on frequency

## Observations
- The Iberian blackout shares the cascade mechanism of the 2016 South Australia event: IBR mass disconnection after initial disturbance in a low-inertia system
- Critical slowing down (increased variance, increased autocorrelation) may be detectable in publicly available frequency data before cascade events
- The "cliff edge" problem: grid-code-compliant IBR settings create discontinuous system behavior at specific SNSP thresholds
- ENTSO-E report acknowledges incomplete data as a limitation — our analysis is similarly limited
- The prediction task is inherently limited by data granularity: 15-minute ENTSO-E data cannot capture sub-second dynamics that determine cascade propagation
