# Knowledge Base — Flight Delay Propagation

## Established Facts

### Aircraft Rotation is the Dominant Propagation Mechanism
- **Finding (this study)**: Propagation features (previous leg delay, rotation position, log-transformed delay, buffer interaction) account for **91.5% of the model's explained variance (R2)**. Removing propagation features drops R2 from 0.327 to 0.028.
- **Literature support**: Pyrgiotis-Malone-Odoni (2013) identified aircraft rotation as the primary delay vector. AhmadBeygi et al. (2008) showed that schedule buffers in rotation chains determine how much delay propagates. Fleurquin et al. (2013, Nature Scientific Reports) modeled the network-level cascade.
- **Implication**: "Your flight was delayed because the plane was late from its previous flight" is not just a passenger excuse — it is the dominant mechanism in the data.

### Carrier Buffer Strategy is the Key Moderating Variable
- **Finding (this study)**: The interaction feature `prev_leg_delay_x_buffer` (previous delay times carrier buffer factor) is the **single most important feature** (35.7% importance in XGBoost). Carriers with tighter schedules (Spirit buffer factor 1.25, Frontier 1.20, JetBlue 1.15) propagate significantly more delay than padded carriers (Southwest 0.75, Hawaiian 0.80, Delta 0.85).
- **Literature**: AhmadBeygi et al. (2008) theoretically predicted this. Skaltsas-Barnhart-Jacquillat (2022, 2023) confirmed that schedule padding is a strategic carrier decision with propagation consequences.
- **Practical**: Spirit's mean delay (30.6 min) is nearly double Southwest's (16.6 min). The difference is largely explained by buffer strategy, not route characteristics.

### Delay Accumulation Through the Day
- **Finding**: Morning flights (06:00-09:00) have significantly lower propagated delay because they start from a "clean" overnight reset. Delays accumulate through the day, peaking at 17:00-19:00.
- **Literature**: Hourly delay factors range from 0.5 (06:00) to 1.3 (18:00), consistent with Simaiakis-Balakrishnan (2014) taxi-out delay dynamics.
- **Practical**: The first flight of the day is the only one with zero rotation-chain propagation. Every subsequent leg inherits risk.

### Hub Airports are Contagion Amplifiers
- **Finding**: Hub origin airports contribute a 15% congestion premium. Hub-to-hub routes (e.g., LAX-MIA, MIA-ATL, DFW-LAX) are the top delay contagion corridors.
- **Literature**: Guimera et al. (2005, PNAS) showed the hub-and-spoke topology concentrates traffic. Zanin-Lillo (2013) showed hubs amplify delay propagation through the network.

### BTS Delay Cause Codes are Noisy but Informative
- **Finding**: Delay cause decomposition shows 31.8% late aircraft, 57.0% carrier/crew/gate, 8.0% NAS, 3.2% weather. The high carrier fraction likely includes misattributed propagation.
- **Literature**: DOT Inspector General (2000) and BTS technical documentation (2023) document that airlines self-report delay causes and may systematically misattribute them. "Late aircraft" is the one cause that airlines cannot easily misattribute because it is mechanically verifiable from tail-number rotation.
- **Implication**: The model-based R2 decomposition (91.5% from propagation) is more reliable than the cause-code decomposition because it uses the actual arrival delay values, not self-reported attribution.

### The Signal is Substantially Linear
- **Finding**: Ridge regression (CV MAE 20.63) outperforms XGBoost (20.88) and LightGBM (20.83) in the tournament. This indicates that the relationship between previous-leg delay and current arrival delay is approximately additive.
- **Implication**: Tree models add modest value through interaction capture (buffer x delay, time-of-day effects) but the core signal is: current delay ≈ α * previous_leg_delay + β * independent_factors.

### Seasonal Patterns are Real but Secondary
- **Calendar**: December and January have the highest delay multipliers (1.15-1.20) due to winter weather. September has the lowest (0.85) after summer storms clear. Summer (June-August) shows 1.10-1.15 from convective weather.
- **Weekly**: Monday and Friday are slightly worse than midweek. Weekends have ~80% of weekday traffic, reducing congestion.
- **These factors are secondary to rotation chain propagation**, accounting for <5% of feature importance.

## What Does NOT Work
- Carrier one-hot encoding: redundant with carrier_buffer_factor
- Distance-squared: no nonlinear distance effect beyond linear
- Holiday indicators: too sparse to learn from
- Day-of-week interactions with delay: tree captures implicitly
- Architecture switches (LightGBM, ExtraTrees): marginal vs XGBoost
- Hyperparameter tweaks: learning_rate, max_depth, subsample changes have negligible effect

## Open Questions
1. Does the propagation fraction differ by time of year? (Summer convective delays may propagate differently from winter de-icing delays)
2. Gate conflict features: how many other flights are at the same gate within +/- 30 min? (Requires gate data not in BTS)
3. Crew pairing proxy: same-carrier flights arriving at origin within +/- 90 min? (Crew swap delays)
4. Does the propagation decay with cascade depth? (Is the 4th leg less affected than the 2nd?)
5. How do flight cancellations affect downstream propagation? (Cancelled flights free up gates/crew but strand passengers)
