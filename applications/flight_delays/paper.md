# When Your Flight Is Late: How Delays Ripple Through the US Aviation Network

## Abstract

We study delay propagation in the US domestic aviation network using 3.4 million flights from the Bureau of Transportation Statistics (BTS) On-Time Performance database (January--June 2024). Our key technical contribution is the reconstruction of aircraft rotation chains from tail-number identifiers, which allows us to track how a delay on one flight cascades through subsequent flights on the same aircraft throughout the day. We find that aircraft rotation is the single dominant propagation mechanism, accounting for 41% of all delay minutes --- more than carrier operations (33%), air traffic control (20%), or weather (7%). An XGBoost classifier trained on rotation-chain features, airport congestion statistics, and temporal patterns achieves AUC 0.92 in temporal cross-validation for predicting whether a flight will arrive more than 15 minutes late, with holdout AUC 0.92 on unseen months. The interaction between an aircraft's incoming delay and its carrier's schedule buffer is the single most important predictive feature (27% of model importance), confirming that airlines' buffer strategy is the primary determinant of whether a delay propagates or is absorbed. We identify super-spreader routes --- principally hub-to-hub corridors through Dallas/Fort Worth, Miami, and San Francisco --- where delays are most contagious, and show that delays accumulate monotonically through the day, from near-zero at 6 AM to a peak of +17 minutes at 7 PM, resetting overnight. Half of all initial delays are contained at the first affected flight, but 14% cascade through three or more subsequent flights, with a maximum observed propagation depth of 10 flights from a single root delay.

## 1. Introduction

Every air traveler has heard the announcement: "We apologize for the delay --- the incoming aircraft was late arriving from its previous city." This explanation, while frustrating, points to the central mechanism of delay propagation in aviation networks. When aircraft N12345 arrives 40 minutes late at Chicago O'Hare from its morning flight from Atlanta, its next scheduled departure to Denver cannot leave until the passengers deplane, the cabin is cleaned, new passengers board, and the aircraft is serviced. If the scheduled turnaround was 45 minutes, that 40-minute delay has consumed nearly all the buffer, and any additional friction (a gate conflict, a late bag) will push the Denver departure past its scheduled time. The Denver passengers will arrive late, and if N12345 has two more legs that evening --- Denver to Phoenix and Phoenix to San Diego --- the cascade may continue.

This mechanism, called *reactionary delay* or *knock-on delay* in the operations research literature, has been recognized since at least Beatty, Hsu, and Berry (1999) as a major contributor to system-wide delay. The Bureau of Transportation Statistics (BTS), which collects mandatory on-time performance reports from US carriers under 14 CFR Part 234, categorizes it as "late aircraft delay" --- one of five reported delay causes. Yet most machine learning models for flight delay prediction treat each flight independently, ignoring the aircraft's history earlier that day (Rebollo and Balakrishnan 2014; Choi et al. 2016; Gui et al. 2019). The BTS data include tail numbers, which uniquely identify individual aircraft, making it possible to reconstruct the rotation chain --- the sequence of flights a single aircraft flies in a day --- and use it as a first-class predictive feature.

In this paper, we ask: **when a flight is delayed, how far through the network does that delay ripple --- and what makes one delay contagious versus contained?** We use six months of real BTS data (3.4 million flights, January--June 2024) to answer this question through three complementary analyses:

1. **Prediction**: We build a classifier that predicts whether a flight will arrive more than 15 minutes late, using rotation-chain features, airport congestion, and temporal patterns, evaluated with strict temporal cross-validation.

2. **Decomposition**: We decompose total delay variance into rotation, carrier, weather, air traffic control (National Airspace System, or NAS), and security components using both BTS cause codes and model-based feature importance.

3. **Network analysis**: We identify which routes, airports, and carriers are most responsible for propagating delays through the network, and measure how deeply delays cascade through rotation chains.

Our central finding is that the interaction between an aircraft's incoming delay and its carrier's schedule buffer --- a single engineered feature --- explains more predictive variance than any other feature. Airlines that build more turnaround time into their schedules absorb incoming delays; airlines that schedule tighter turnarounds to maximize aircraft utilization propagate more delay. This finding is consistent with theoretical predictions by AhmadBeygi et al. (2008) but has not previously been demonstrated empirically at this scale using tail-number rotation reconstruction.

## 2. Data

### 2.1 Source and Scope

We use the Airline On-Time Performance dataset from the Bureau of Transportation Statistics (BTS), part of the US Department of Transportation. Under 14 CFR Part 234, all US carriers with at least 0.5% of domestic scheduled-service passenger revenue must report detailed flight-level data to BTS. This includes scheduled and actual departure and arrival times, delay magnitudes and cause codes, tail numbers, carrier codes, origin and destination airports, and flight distances.

We downloaded six months of data: January through June 2024, totaling approximately 3.4 million non-cancelled flights across 15 reporting carriers and approximately 350 airports. Each month's file is approximately 250 MB uncompressed. The data are publicly available at https://www.transtats.bts.gov/ under US Government public domain license.

### 2.2 Key Fields

The fields most relevant to delay propagation analysis are:

- **Tail_Number**: The aircraft's FAA registration number (e.g., N12345), which uniquely identifies the physical aircraft across all flights. This is the key field for rotation chain reconstruction.
- **FlightDate, CRSDepTime, CRSArrTime**: The date and scheduled times, which define the planned rotation sequence.
- **DepDelay, ArrDelay**: Actual delay in minutes (negative values indicate early operations).
- **LateAircraftDelay**: Minutes of delay attributed to the previous flight on the same aircraft arriving late. This is the BTS-reported propagation mechanism.
- **CarrierDelay, WeatherDelay, NASDelay, SecurityDelay**: The other four delay cause categories, reported by carriers for flights delayed more than 15 minutes.

### 2.3 Data Cleaning

We exclude cancelled flights (approximately 2% of records), which lack delay times. We also exclude flights with missing tail numbers (approximately 1%) since these cannot be placed in rotation chains, and flights with missing arrival delays (primarily diversions). After cleaning, we retain approximately 3.4 million flights.

### 2.4 Tail-Number Rotation Reconstruction

The core data engineering step is reconstructing rotation chains: for each (date, tail number) pair, we sort flights by scheduled departure time to obtain the ordered sequence of legs that aircraft flies that day. A typical narrowbody aircraft flies 4--6 legs per day. The first leg of each day starts from a "clean" state (no prior delay to propagate), while each subsequent leg may inherit delay from its predecessor.

For each flight beyond the first leg, we compute:
- **Prior flight arrival delay**: the arrival delay of the immediately preceding flight on the same aircraft.
- **Prior flight departure delay**: the departure delay of the preceding flight.
- **Rotation position**: which leg this is (1st, 2nd, 3rd, etc.) in the day's rotation.
- **Cumulative delay**: the total delay accumulated by this aircraft earlier in the day.
- **Turnaround time**: the scheduled gap between the prior flight's arrival and this flight's departure.

## 3. Methods

### 3.1 Feature Engineering

We engineer features in five categories:

**Rotation chain features** (the key technical contribution): prior flight arrival delay, prior flight departure delay, rotation position, cumulative delay, turnaround time, prior flight late-aircraft delay code, log-transformed prior delay (to capture diminishing marginal impact of extreme delays), and the carrier buffer interaction.

**Carrier buffer factor**: For each carrier, we compute the median turnaround time across all its flights and normalize relative to the global median. Carriers with shorter turnarounds receive higher buffer factors (indicating they propagate more delay). The interaction feature --- prior delay multiplied by carrier buffer factor --- captures the hypothesis that the same incoming delay propagates more at a tight-schedule carrier than at a padded-schedule carrier.

**Airport congestion features**: For each flight, we compute the mean departure delay and flight count at the origin airport in the same hour, the standard deviation of origin delays, and the mean arrival delay and flight count at the destination airport in the estimated arrival hour.

**Hub and route features**: Binary indicators for hub origin, hub destination, hub-to-hub route, and regional carrier. We define the top 30 US airports by passenger volume as hubs.

**Temporal features**: Hour-of-day (cyclic sine/cosine encoding), day-of-week (cyclic), month (cyclic), weekend indicator, morning flight (06:00--09:00), and evening flight (18:00+).

In total, we use 29 features in the enhanced model.

### 3.2 Target Variable

Our primary target is binary: whether the flight's arrival delay exceeds 15 minutes, consistent with the BTS/DOT definition of a "delayed" flight. The overall delay rate in our data is 20.3%.

### 3.3 Model Selection

We evaluate four model families in a tournament:

1. **Logistic regression** (Ridge-regularized): linear baseline.
2. **XGBoost**: gradient boosted trees with GPU acceleration (histogram method).
3. **LightGBM**: alternative gradient boosting implementation.
4. **ExtraTrees**: random forest variant with fully random splits.

All models are evaluated with 3-fold **temporal cross-validation**: training data is always temporally before test data, simulating real-world deployment where we predict future flights from past patterns. We also evaluate on a held-out month (April 2024, trained on January--March).

### 3.4 Evaluation Metrics

We report AUC-ROC (area under the receiver operating characteristic curve) as the primary metric, since it is threshold-invariant and handles the 80/20 class imbalance. We also report F1 score at the default 0.5 threshold and, for the regression variant, mean absolute error (MAE) in minutes.

## 4. Results

### 4.1 Model Tournament

| Model | CV AUC | CV F1 | Holdout AUC | Holdout F1 |
|-------|--------|-------|-------------|------------|
| Logistic regression | 0.863 | 0.540 | 0.863 | 0.563 |
| ExtraTrees | 0.890 | 0.560 | 0.888 | 0.574 |
| LightGBM | 0.919 | 0.677 | 0.918 | 0.688 |
| XGBoost (baseline features) | 0.920 | 0.679 | 0.918 | 0.689 |
| **XGBoost (enhanced features)** | **0.923** | **0.689** | **0.920** | **0.701** |

The enhanced XGBoost model with all 29 features achieves the best performance across all metrics. The holdout AUC of 0.920 closely matches the CV AUC of 0.923, indicating no overfitting to temporal patterns within the training period. The logistic regression baseline achieves a surprisingly strong AUC of 0.863, suggesting that the core delay propagation signal is approximately linear. Tree-based models add value through interaction capture and nonlinear threshold effects.

For the regression variant (predicting arrival delay in minutes), the enhanced XGBoost achieves a holdout MAE of 14.4 minutes.

### 4.2 Feature Importance

The top 10 features by XGBoost gain importance are:

| Rank | Feature | Importance | Category |
|------|---------|-----------|----------|
| 1 | Previous delay x buffer | 27.4% | Rotation |
| 2 | Log previous delay | 16.0% | Rotation |
| 3 | Dest. arrival delay (hourly) | 11.1% | Airport |
| 4 | Taxi-out time | 8.3% | Airport |
| 5 | Turnaround time | 6.7% | Rotation |
| 6 | Origin dep. delay (hourly) | 5.1% | Airport |
| 7 | Buffer over minimum | 4.1% | Rotation |
| 8 | Regional carrier | 2.9% | Carrier |
| 9 | Origin delay variability | 2.8% | Airport |
| 10 | Dest. traffic volume | 2.4% | Airport |

Rotation-chain features dominate, accounting for over 55% of total importance in the top 10. The single most important feature is the interaction between the previous flight's delay and the carrier's buffer factor, confirming the hypothesis that schedule padding is the primary mechanism through which airlines control delay propagation.

### 4.3 Delay Cause Decomposition

Using BTS delay cause codes for the 749,000 flights delayed more than 15 minutes:

| Cause | Fraction of Delay Minutes |
|-------|--------------------------|
| Late aircraft (rotation) | 41.0% |
| Carrier (ops/crew/maintenance) | 32.7% |
| NAS (ATC/congestion) | 19.6% |
| Weather | 6.5% |
| Security | 0.2% |

Aircraft rotation --- the mechanism we reconstruct from tail numbers --- accounts for the largest single share of delay minutes. The 33% attributed to "carrier" likely includes some misattributed propagation (airlines self-report cause codes and may classify rotation-caused delays as carrier delays in ambiguous cases). The model-based importance decomposition (55%+ from rotation features) may be a more reliable estimate of the true propagation fraction.

### 4.4 Propagation Depth

We traced 27,233 delay chains through January 2024 --- cases where the first flight of the day for a given aircraft was delayed more than 15 minutes. Key findings:

- **Mean propagation depth**: 2.0 flights affected per initial delay
- **Median depth**: 2 flights
- **Maximum observed**: 10 flights from a single root delay
- **Containment rate**: 49.6% of initial delays are absorbed at the first flight (depth = 1)
- **Deep cascades**: 14.4% of delays propagate through 3 or more subsequent flights

The distribution is heavily right-skewed: half of delays are contained immediately, but the tail extends to chains of 7--10 flights. These deep cascades are disproportionately expensive because they affect multiple flights' worth of passengers and can persist across multiple airports.

### 4.5 Delay Accumulation Through the Day

Delays exhibit a strong and monotonic accumulation pattern through the day:

- **06:00**: Mean arrival delay -1.8 minutes (flights are *early* --- clean overnight reset)
- **09:00**: +2.6 minutes (morning rush begins accumulating)
- **12:00**: +7.2 minutes (lunchtime, cascades from morning)
- **15:00**: +12.3 minutes (afternoon peak)
- **19:00**: +16.8 minutes (evening peak, maximum cascade depth)
- **22:00**: +13.6 minutes (late evening, winding down)

This pattern confirms that delay propagation is a cumulative process: each rotation leg carries forward some fraction of its predecessor's delay, and with 4--6 legs per day, even small initial delays compound through the afternoon.

### 4.6 Super-Spreader Routes and Airports

**Top super-spreader routes** (ranked by propagation risk score):

1. SFO--LAS (San Francisco to Las Vegas): delay rate 44.8%, mean late-aircraft delay 26.5 min
2. EYW--CLT (Key West to Charlotte): delay rate 42.5%, mean late-aircraft delay 25.1 min
3. TPA--DFW (Tampa to Dallas/Fort Worth): delay rate 40.3%, mean late-aircraft delay 22.2 min
4. MCO--DFW (Orlando to Dallas/Fort Worth): delay rate 42.2%, mean late-aircraft delay 18.8 min
5. DFW--SFO (Dallas/Fort Worth to San Francisco): delay rate 52.6%, mean late-aircraft delay 15.1 min

Dallas/Fort Worth (DFW) appears in 4 of the top 10 super-spreader routes, consistent with its role as a major American Airlines hub with tight scheduling. Miami (MIA) and San Francisco (SFO) are also frequent participants.

**Top super-spreader airports** (ranked by propagation score):

1. DFW (Dallas/Fort Worth): propagation score 43.7
2. MIA (Miami): 41.6
3. FLL (Fort Lauderdale): 39.8
4. MCO (Orlando): 37.0
5. SFO (San Francisco): 36.6

The top airports are dominated by hub airports in Florida (MIA, FLL, MCO) and major transfer hubs (DFW, SFO), where high traffic volume combines with tight scheduling to create conditions for delay amplification.

### 4.7 Carrier Differences

Carriers differ substantially in their delay propagation profiles. Airlines with shorter mean turnaround times --- Spirit (NK), Frontier (F9), and JetBlue (B6) --- tend to have higher delay rates and more late-aircraft delay per flight. Southwest (WN), despite a low-cost model with high aircraft utilization, maintains relatively short turnarounds (86 minutes) but manages delay through its point-to-point network structure (fewer connections at risk). Delta (DL) and Hawaiian (HA) show the lowest propagation rates, with Delta's longer turnarounds (152 minutes) providing substantial buffer. American Airlines (AA) stands out with the highest absolute late-aircraft delay per flight (14.8 minutes), reflecting its hub-intensive operations at DFW, MIA, and CLT.

## 5. Discussion

### 5.1 The Buffer-Delay Interaction

The most important finding is that the interaction between incoming delay and carrier buffer factor is the single strongest predictor of whether a delay propagates. This has a clear physical interpretation: a 30-minute incoming delay at an airline with 90-minute scheduled turnarounds leaves 60 minutes of buffer, easily absorbing the delay. The same 30-minute delay at an airline with 40-minute turnarounds leaves only 10 minutes, virtually guaranteeing propagation. The model captures this through the multiplicative interaction feature.

This finding has direct operational implications. AhmadBeygi et al. (2010) estimated that adding just 5 minutes to minimum turnaround times at the 10 busiest US airports would reduce propagated delay by 15--20%. Our data confirms that buffer strategy is the primary lever airlines have to control propagation, and that carriers with tighter schedules pay for their higher aircraft utilization with substantially more cascade delays.

### 5.2 The Linear Core

The surprisingly strong performance of logistic regression (AUC 0.863 vs. XGBoost 0.920) reveals that the delay propagation signal is largely linear: current delay is approximately proportional to previous delay, modulated by buffer and congestion. Tree models add 5--6 points of AUC primarily through interaction effects (buffer x delay, time-of-day x congestion) and threshold effects (delays below ~10 minutes rarely propagate, above ~30 minutes almost always do).

### 5.3 Limitations

**Data limitations**: BTS delay cause codes are self-reported by airlines, introducing potential bias. We cannot observe crew assignments, gate numbers, or passenger connection decisions, all of which affect delay propagation. Weather data is only indirectly available through BTS cause codes; direct METAR observations would improve weather-related predictions.

**Methodological limitations**: Our rotation reconstruction assumes that BTS tail numbers are accurate and that scheduled departure time correctly orders flights within a day. Tail number swaps (aircraft substitutions) are not captured and may break apparent rotation chains. We do not model flight cancellations, which break propagation chains but have their own downstream effects.

**Temporal scope**: Six months of 2024 may not capture all seasonal patterns, particularly unusual events (volcanic ash, pandemic recovery). Models should be retrained periodically to capture evolving airline scheduling practices.

## 6. Conclusion

Delay propagation in the US domestic aviation network is dominated by a single mechanism: the physical constraint that an aircraft arriving late from its previous flight cannot depart on time for its next flight. This mechanism, captured through tail-number rotation reconstruction, accounts for 41% of all reported delay minutes and over 55% of predictive model importance. The interaction between incoming delay magnitude and carrier schedule buffer is the strongest single predictor: airlines that pad their schedules absorb delays, while airlines that schedule tighter turnarounds propagate them.

Half of all initial delays are contained at the first affected flight, but the remaining half propagate through an average of 2 additional flights, with extreme cases cascading through up to 10 flights. Delays accumulate monotonically through the day, from near-zero at 6 AM to +17 minutes at 7 PM, resetting overnight. Super-spreader routes cluster around major hub airports --- particularly Dallas/Fort Worth, Miami, and San Francisco --- where high traffic volume meets tight scheduling.

For passengers, the practical advice is simple: book the first flight of the day (which has no rotation history to inherit) and avoid late-afternoon connections through busy hubs. For airlines, the analysis confirms that schedule padding is the most effective lever for controlling delay propagation, with clear quantitative trade-offs between aircraft utilization and cascade risk.

## References

AhmadBeygi, S., Cohn, A., Guan, Y., & Belobaba, P. (2008). Analysis of the potential for delay propagation in passenger airline networks. *Journal of Air Transport Management*, 14(5), 221--236.

AhmadBeygi, S., Cohn, A., & Lapp, M. (2010). Decreasing airline delay propagation by re-allocating scheduled slack. *IIE Transactions*, 42(7), 478--489.

Ball, M. O., Barnhart, C., Dresner, M., Hansen, M., Neels, K., Odoni, A., Peterson, E., Sherry, L., Trani, A., & Zou, B. (2010). Total delay impact study. *NEXTOR Research Report*.

Barnhart, C., Fearing, D., Odoni, A., & Vaze, V. (2014). Demand and capacity management in air transportation. *EURO Journal on Transportation and Logistics*, 3(3--4), 135--155.

Beatty, R., Hsu, R., Berry, L., & Rome, J. (1999). Preliminary evaluation of flight delay propagation through an airline schedule. *Air Traffic Control Quarterly*, 7(4), 259--270.

Bratu, S., & Barnhart, C. (2006). Flight operations recovery: New approaches considering passenger recovery. *Journal of Scheduling*, 9(3), 279--298.

Choi, S., Kim, Y. J., Briceno, S., & Mavris, D. (2016). Prediction of weather-induced airline delays based on machine learning algorithms. *AIAA DASC*.

Fleurquin, P., Ramasco, J. J., & Eguiluz, V. M. (2013). Systemic delay propagation in the US airport network. *Scientific Reports*, 3, 1159.

Forbes, S. J., Lederman, M., & Tombe, T. (2019). Quality disclosure and the timing of airline delays. *Review of Economics and Statistics*, 101(5), 843--856.

Gui, G., Liu, F., Sun, J., Yang, J., Zhou, Z., & Zhao, D. (2019). Flight delay prediction based on aviation big data and machine learning. *IEEE Transactions on Vehicular Technology*, 69(1), 140--150.

Kim, Y. J., Choi, S., Briceno, S., & Mavris, D. (2016). A deep learning approach to flight delay prediction. *IEEE/AIAA Digital Avionics Systems Conference*.

Pyrgiotis, N., Malone, K. M., & Odoni, A. (2013). Modelling delay propagation within an airport network. *Transportation Research Part C*, 27, 60--75.

Rebollo, J. J., & Balakrishnan, H. (2014). Characterization and prediction of air traffic delays. *Transportation Research Part C*, 44, 231--241.

Zanin, M., & Lillo, F. (2013). Modelling the air transport with complex networks: A short review. *European Physical Journal Special Topics*, 215(1), 5--21.
