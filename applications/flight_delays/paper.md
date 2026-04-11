# When Your Flight Is Late: How Delays Ripple Through the US Aviation Network

## Abstract

We study delay propagation in the US domestic aviation network using 3.4 million flights from the Bureau of Transportation Statistics (BTS) On-Time Performance database (January--June 2024). We reconstruct aircraft rotation chains from tail-number identifiers, tracking how a delay on one flight cascades through subsequent flights on the same aircraft throughout the day. We find that aircraft rotation accounts for 41% of airline-reported delay minutes --- more than carrier operations (33%), air traffic control (20%), or weather (7%). An XGBoost classifier trained on rotation-chain features, airport congestion statistics, and temporal patterns achieves AUC 0.923 in temporal cross-validation (holdout AUC 0.920 on a single unseen month, April 2024) for predicting whether a flight will arrive more than 15 minutes late. The model is well calibrated (Brier score 0.074, expected calibration error 0.009) and temporally stable (AUC 0.919--0.921 across months 4--6). SHAP analysis reveals that airport congestion features (destination arrival delay, origin departure delay) and rotation-chain features (turnaround time, delay-buffer interaction) jointly dominate the model, with rotation features accounting for 28% of total SHAP importance. We identify super-spreader routes --- principally hub-to-hub corridors through Dallas/Fort Worth, Miami, and San Francisco --- where delays are most contagious, and show that delays accumulate monotonically through the day, from near-zero at 6 AM to a peak of +17 minutes at 7 PM, resetting overnight. Half of all initial delays are contained at the first affected flight, but 14% cascade through three or more subsequent flights, with a maximum observed propagation depth of 10 flights from a single root delay.

## 1. Introduction

Every air traveler has heard the announcement: "We apologize for the delay --- the incoming aircraft was late arriving from its previous city." This explanation, while frustrating, points to the central mechanism of delay propagation in aviation networks. When aircraft N12345 arrives 40 minutes late at Chicago O'Hare from its morning flight from Atlanta, its next scheduled departure to Denver cannot leave until the passengers deplane, the cabin is cleaned, new passengers board, and the aircraft is serviced. If the scheduled turnaround was 45 minutes, that 40-minute delay has consumed nearly all the buffer, and any additional friction (a gate conflict, a late bag) will push the Denver departure past its scheduled time. The Denver passengers will arrive late, and if N12345 has two more legs that evening --- Denver to Phoenix and Phoenix to San Diego --- the cascade may continue.

This mechanism, called *reactionary delay* or *knock-on delay* in the operations research literature, has been recognized since at least Beatty, Hsu, and Berry (1999) as a major contributor to system-wide delay. The Bureau of Transportation Statistics (BTS), which collects mandatory on-time performance reports from US carriers under 14 CFR Part 234, categorizes it as "late aircraft delay" --- one of five reported delay causes. Yet most machine learning models for flight delay prediction treat each flight independently, ignoring the aircraft's history earlier that day (Rebollo and Balakrishnan 2014; Choi et al. 2016; Gui et al. 2019). The BTS data include tail numbers, which uniquely identify individual aircraft, making it possible to reconstruct the rotation chain --- the sequence of flights a single aircraft flies in a day --- and use it as a first-class predictive feature.

In this paper, we ask: **when a flight is delayed, how far through the rotation chain does that delay ripple --- and what makes one delay contagious versus contained?** We use six months of real BTS data (3.4 million flights, January--June 2024) to answer this question through three complementary analyses:

1. **Prediction**: We build a classifier that predicts whether a flight will arrive more than 15 minutes late, using rotation-chain features, airport congestion, and temporal patterns, evaluated with strict temporal cross-validation and SHAP-based feature attribution.

2. **Decomposition**: We decompose total delay variance into rotation, carrier, weather, air traffic control (National Airspace System, or NAS), and security components using both BTS cause codes and model-based feature importance, noting important differences between these two decomposition approaches.

3. **Descriptive network characterization**: We characterize which routes, airports, and carriers are associated with the highest delay propagation, compute graph-theoretic centrality measures for the airport network, and measure how deeply delays cascade through rotation chains.

Our central finding is that airport congestion and rotation-chain dynamics jointly dominate delay prediction. SHAP analysis shows that destination airport arrival delay (20.4% of SHAP importance), origin departure delay (15.4%), turnaround time (10.6%), and the delay-buffer interaction (5.7%) are the top predictive features. The interaction between incoming delay and carrier schedule buffer, while not the single dominant feature by SHAP attribution, is the most important *rotation-specific* feature and confirms that airlines' buffer strategy is a key determinant of whether a delay propagates or is absorbed. This finding is consistent with simulation results by AhmadBeygi et al. (2008) and confirms at large scale what prior studies have shown on smaller samples (Beatty et al. 1999; Pyrgiotis et al. 2013).

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

**Rotation chain features** (derived from tail-number reconstruction, following Beatty et al. 1999 and Pyrgiotis et al. 2013): prior flight arrival delay, prior flight departure delay, rotation position, cumulative delay, turnaround time, prior flight late-aircraft delay code, log-transformed prior delay (to capture diminishing marginal impact of extreme delays), and the carrier buffer interaction.

**Carrier buffer factor**: For each carrier, we compute the median turnaround time across all its flights and normalize relative to the global median. Carriers with shorter turnarounds receive higher buffer factors (indicating they propagate more delay). The interaction feature --- prior delay multiplied by carrier buffer factor --- captures the hypothesis that the same incoming delay propagates more at a tight-schedule carrier than at a padded-schedule carrier.

**Airport congestion features**: For each flight, we compute the mean departure delay and flight count at the origin airport in the same hour, the standard deviation of origin delays, and the mean arrival delay and flight count at the destination airport in the estimated arrival hour.

**Hub and route features**: Binary indicators for hub origin, hub destination, hub-to-hub route, and regional carrier. We define the top 30 US airports by passenger volume as hubs.

**Temporal features**: Hour-of-day (cyclic sine/cosine encoding), day-of-week (cyclic), month (cyclic), weekend indicator, morning flight (06:00--09:00), and evening flight (18:00+).

In total, we use 29 features in the enhanced model.

### 3.2 Target Variable

Our primary target is binary: whether the flight's arrival delay exceeds 15 minutes, consistent with the BTS/DOT definition of a "delayed" flight. The overall delay rate in our data is 20.3%.

### 3.3 Model Selection

We evaluate four model families in a tournament:

1. **Logistic regression** (Ridge-regularized, C=1.0, LBFGS solver): linear baseline with standardized features.
2. **XGBoost**: gradient boosted trees (n_estimators=300, max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, histogram method with GPU acceleration where available).
3. **LightGBM**: alternative gradient boosting (same hyperparameters as XGBoost for fair comparison).
4. **ExtraTrees**: random forest variant with fully random splits (n_estimators=200, max_depth=20).

All models are evaluated with 3-fold **temporal cross-validation** using expanding windows: the training data spans all dates up to a fold boundary, and the test data spans the subsequent fold-sized window. Concretely, with three months of data (January--March), fold 1 trains on approximately the first 23 days and tests on days 24--46, fold 2 trains on days 1--46 and tests on days 47--69, and fold 3 trains on days 1--69 and tests on days 70--91. Training data is always strictly temporally before test data, simulating real-world deployment. We also evaluate on a held-out single month (April 2024, trained on January--March). Missing feature values are filled with -999 for tree models (which handle this natively as a separate split direction).

### 3.4 Evaluation Metrics

We report AUC-ROC (area under the receiver operating characteristic curve) as the primary metric, since it is threshold-invariant and handles the 80/20 class imbalance. We also report F1 score at the default 0.5 threshold, Brier score for probability calibration, and for the regression variant, mean absolute error (MAE) in minutes.

### 3.5 Feature Attribution

We use two complementary approaches to feature attribution:

1. **XGBoost gain importance**: the total gain (reduction in loss) from all splits on a given feature, normalized to sum to 1. This is fast but known to be biased toward high-cardinality and continuous features (Strobl et al. 2007).

2. **SHAP (SHapley Additive exPlanations) values**: TreeExplainer computes exact Shapley values for tree ensembles (Lundberg and Lee, 2017). SHAP values provide unbiased, per-sample feature attributions grounded in cooperative game theory. We compute SHAP on a stratified subsample of 20,000 flights and report mean absolute SHAP values as our primary importance metric.

Where gain and SHAP importance disagree, we treat SHAP as the more reliable estimate.

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

We report feature importance from two complementary methods. XGBoost gain importance (Table 2) measures the total reduction in training loss from splits on each feature. SHAP values (Table 3) provide unbiased, game-theoretically grounded attributions.

**Table 2: Top 10 features by XGBoost gain importance**

| Rank | Feature | Gain | Category |
|------|---------|------|----------|
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

**Table 3: Top 10 features by mean |SHAP| value**

| Rank | Feature | Mean |SHAP| | Category |
|------|---------|-------------|----------|
| 1 | Dest. arrival delay (hourly) | 1.016 (20.4%) | Airport |
| 2 | Origin dep. delay (hourly) | 0.768 (15.4%) | Airport |
| 3 | Taxi-out time | 0.551 (11.1%) | Airport |
| 4 | Turnaround time | 0.529 (10.6%) | Rotation |
| 5 | Origin delay variability | 0.302 (6.1%) | Airport |
| 6 | Previous delay x buffer | 0.283 (5.7%) | Rotation |
| 7 | Buffer over minimum | 0.245 (4.9%) | Rotation |
| 8 | Dest. traffic volume | 0.241 (4.8%) | Airport |
| 9 | Regional carrier | 0.191 (3.8%) | Carrier |
| 10 | Carrier buffer factor | 0.134 (2.7%) | Rotation |

The two methods tell materially different stories. By XGBoost gain, rotation-chain features account for 58% of total importance, with the delay-buffer interaction alone at 27.4%. By SHAP, rotation features account for 28% of total importance, and airport congestion features dominate: destination arrival delay (20.4%) and origin departure delay (15.4%) are the top two features. This discrepancy is expected: gain importance is known to be inflated for high-cardinality continuous features that appear in many splits but contribute small marginal effects per split (Strobl et al. 2007). The SHAP analysis suggests a more balanced picture where both airport-level congestion and aircraft-level rotation dynamics contribute substantially to delay prediction.

The practical takeaway is that delay prediction depends on two complementary signals: (1) what is happening at the airports right now (congestion, taxi delays), and (2) what happened to this specific aircraft on its previous leg (incoming delay, available buffer). Neither alone is sufficient --- the model on first-leg-of-day flights (which lack rotation history) achieves AUC 0.880, compared to 0.928 on subsequent legs.

### 4.3 Delay Cause Decomposition

Using BTS delay cause codes for the 749,000 flights delayed more than 15 minutes:

| Cause | Fraction of Delay Minutes |
|-------|--------------------------|
| Late aircraft (rotation) | 41.0% |
| Carrier (ops/crew/maintenance) | 32.7% |
| NAS (ATC/congestion) | 19.6% |
| Weather | 6.5% |
| Security | 0.2% |

Aircraft rotation --- the mechanism we reconstruct from tail numbers --- accounts for the largest single share of delay minutes according to BTS cause codes. **Important caveat**: these cause codes are self-reported by airlines and represent categorical attributions for individual delayed flights. They measure a fundamentally different quantity than model-based feature importance, which measures how useful a feature is for prediction. The 41% BTS figure and the 28% SHAP figure (or 58% gain figure) for rotation features should not be compared directly: BTS codes decompose *realized delay minutes* by reported cause, while model importance decomposes *predictive variance* across all flights (including on-time ones). The "carrier" category (33%) likely includes some misattributed propagation, since airlines self-report and may classify rotation-caused delays as carrier delays in ambiguous cases, but quantifying this potential bias requires data beyond what BTS provides.

### 4.4 Propagation Depth

We traced 27,233 delay chains through January 2024 --- cases where the first flight of the day for a given aircraft was delayed more than 15 minutes. We restrict to a single month for computational tractability, as the analysis requires iterating over individual aircraft-day pairs; January was chosen as the first month in the dataset. Key findings:

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

We define a **propagation risk score** for each route as:

$$\text{propagation\_score}(r) = \text{delay\_rate}(r) \times \overline{\text{LateAircraftDelay}}(r) \times \log(1 + n_{\text{flights}}(r))$$

where delay_rate is the fraction of flights on route $r$ delayed 15+ minutes, $\overline{\text{LateAircraftDelay}}$ is the mean BTS late-aircraft delay in minutes across all flights on the route, and $n_{\text{flights}}$ is the total traffic volume. The log-traffic term ensures that high-volume routes are weighted more heavily, but sublinearly, so that a rare but severe route is not dominated by a high-volume, low-severity one. Routes with fewer than 100 flights in the analysis period are excluded. For airports, the same formula is applied using departure statistics aggregated across all routes from that airport (minimum 500 departures).

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

Carriers differ substantially in their observed delay propagation profiles. Airlines with shorter mean turnaround times --- Spirit (NK), Frontier (F9), and JetBlue (B6) --- tend to have higher delay rates and more late-aircraft delay per flight. Southwest (WN), despite a low-cost model with high aircraft utilization, maintains relatively short turnarounds (86 minutes) but shows moderate propagation rates; its point-to-point network structure, smaller average aircraft, and different route mix may all contribute, though we cannot isolate these factors with observational data alone. Delta (DL) and Hawaiian (HA) show the lowest propagation rates; Delta's longer turnarounds (152 minutes) are correlated with lower propagation, though Delta's route mix (more long-haul flights with naturally longer gate times) and fleet composition may also contribute. American Airlines (AA) has the highest absolute late-aircraft delay per flight (14.8 minutes), associated with its hub-intensive operations at DFW, MIA, and CLT, though we note this is an observational correlation that does not control for route mix, fleet age, weather exposure, or passenger load.

### 4.8 Network Structure

We construct a directed weighted graph of the US domestic airport network, where nodes are airports, edges are routes, and edge weights are flight counts. The full six-month network comprises 343 airports and 6,536 directed routes with a density of 0.056.

**Degree centrality** (fraction of airports directly connected): DFW (0.58), DEN (0.54), ORD (0.51), ATL (0.51), CLT (0.45). These are the most connected airports, consistent with their roles as major airline hubs.

**Betweenness centrality** (fraction of shortest paths passing through the airport): The betweenness ranking differs from degree centrality. Several smaller airports (AGS/Augusta, DAB/Daytona Beach) rank high because they serve as sole connectors between small regional networks and the hub system. Among major airports, LGA (0.25), DFW (0.19), IAH (0.18), LAX (0.18), and PHX (0.15) have the highest betweenness, identifying them as critical bottleneck nodes whose disruption would most fragment the network.

**PageRank** (importance weighted by incoming connections from important nodes): DFW (0.046), PHX (0.023), DEN (0.022), LAX (0.022), LGA (0.018). PageRank favors airports that receive traffic from many other important airports, capturing the "cascading importance" of hub connectivity.

The network metrics complement the propagation risk scores in Section 4.6. DFW ranks #1 on both propagation risk and degree centrality --- it is both the most connected airport and the one where delays are most contagious, a combination that amplifies its system-wide impact.

### 4.9 Calibration and Temporal Robustness

**Calibration**: The model's predicted probabilities are well calibrated against observed delay rates. On the April 2024 holdout, the Brier score is 0.074 (lower is better; the baseline of predicting the marginal rate 20.3% for every flight gives Brier 0.162), and the expected calibration error (ECE) is 0.009. This means the model's probability outputs can be interpreted directly --- a predicted 30% probability corresponds closely to a 30% observed delay rate.

**Temporal stability**: We evaluate the model (trained on January--March) separately on each subsequent month. AUC is remarkably stable: April 0.920, May 0.921, June 0.919 (standard deviation 0.0008). The lack of seasonal degradation across spring months is encouraging, though we note that our data does not cover summer (July--September), when convective weather dominates and delay patterns may differ.

**First-leg-of-day flights**: First-leg flights (24.4% of holdout flights) have no rotation history and a lower base delay rate (12.6% vs. 21.1% for subsequent legs). The model achieves AUC 0.880 on first-leg flights, falling back to airport congestion and temporal features. This 0.048-point degradation relative to non-first-leg AUC (0.928) quantifies the contribution of rotation information.

## 5. Discussion

### 5.1 The Buffer-Delay Interaction

SHAP analysis reveals that the delay-buffer interaction is the most important rotation-specific feature (5.7% of total SHAP importance), though airport congestion features collectively contribute more to the model's predictions. The physical interpretation remains clear: a 30-minute incoming delay at an airline with 90-minute scheduled turnarounds leaves 60 minutes of buffer, easily absorbing the delay. The same 30-minute delay at an airline with 40-minute turnarounds leaves only 10 minutes, virtually guaranteeing propagation.

However, the SHAP results show that this mechanism operates in the context of broader airport conditions. The top two SHAP features --- destination arrival delay (20.4%) and origin departure delay (15.4%) --- capture the current state of the airport system. The buffer-delay interaction then modulates whether an aircraft-specific delay propagates within that system context. This is consistent with the finding that first-leg-of-day flights (which lack rotation history) still achieve AUC 0.880 using airport features alone.

This finding has direct operational implications. AhmadBeygi et al. (2010) simulated that adding 5 minutes to minimum turnaround times at the 10 busiest US airports would reduce propagated delay by 15--20%. Our data is consistent with this: carriers with turnarounds above 150 minutes show dramatically lower late-aircraft delay per flight.

### 5.2 The Linear Core

The surprisingly strong performance of logistic regression (AUC 0.863 vs. XGBoost 0.923) reveals that the delay propagation signal is largely linear: current delay is approximately proportional to previous delay, modulated by buffer and congestion. Tree models add 6 points of AUC primarily through interaction effects (buffer x delay, time-of-day x congestion) and threshold effects (delays below ~10 minutes rarely propagate, above ~30 minutes almost always do).

### 5.3 Limitations

**Data limitations**: BTS delay cause codes are self-reported by airlines, introducing potential bias. We cannot observe crew assignments, gate numbers, or passenger connection decisions, all of which affect delay propagation. Weather data is only indirectly available through BTS cause codes; direct METAR observations would improve weather-related predictions. We report flight-level delay counts but do not estimate passenger-hours of delay, which would require load factor data not available in BTS.

**Methodological limitations**: Our rotation reconstruction assumes that BTS tail numbers are accurate and that scheduled departure time correctly orders flights within a day. Tail number swaps (aircraft substitutions) are not captured and may break apparent rotation chains; we have not quantified the frequency of such swaps. A sensitivity analysis randomly breaking some fraction of chains would bound this concern. We do not model flight cancellations, which break propagation chains but have their own downstream effects.

**Temporal scope**: Six months (January--June 2024) covers winter and spring but not summer, when thunderstorm-driven delays dominate historically. Model performance on July--September data may differ. Models should be retrained periodically to capture evolving airline scheduling practices.

**Causal inference**: All carrier-level and route-level findings in this paper are observational correlations. We do not control for fleet composition, route mix, passenger demographics, or operational strategy. Claims about the effect of buffer strategy on delay propagation should be interpreted as associations, not causal effects.

## 6. Conclusion

Delay propagation in the US domestic aviation network is driven by the interaction of two factors: airport-level congestion and aircraft-specific rotation dynamics. An XGBoost classifier trained on 29 features achieves AUC 0.923 (CV) and 0.920 (holdout), with good calibration (Brier 0.074, ECE 0.009) and temporal stability across months. SHAP analysis reveals that airport congestion features (destination and origin delay levels) and rotation-chain features (turnaround time, delay-buffer interaction) jointly dominate the model, with neither category alone sufficient.

Aircraft rotation accounts for 41% of airline-reported delay minutes (BTS cause codes) and 28% of SHAP-based model importance. The interaction between incoming delay magnitude and carrier schedule buffer is the strongest rotation-specific predictor: carriers with longer turnarounds are associated with lower propagation rates, though this observational finding does not control for fleet mix, route structure, or other operational differences.

Half of all initial delays are contained at the first affected flight, but the remaining half propagate through an average of 2 additional flights, with extreme cases cascading through up to 10 flights. Delays accumulate monotonically through the day, from near-zero at 6 AM to +17 minutes at 7 PM, resetting overnight. Super-spreader routes cluster around major hub airports --- particularly Dallas/Fort Worth (highest degree centrality and propagation score), Miami, and San Francisco --- where high traffic volume meets tight scheduling.

For passengers, the practical advice is straightforward and consistent with prior knowledge: book the first flight of the day (which has no rotation history to inherit and shows AUC 0.880 vs. 0.928 for later flights) and avoid late-afternoon connections through busy hubs. For airlines, the analysis is consistent with AhmadBeygi et al.'s (2010) finding that schedule padding is an effective lever for controlling delay propagation.

## Code and Data Availability

All code for data loading, feature engineering, model training, SHAP analysis, and plot generation is available at https://github.com/colinjoc/hdr_autoresearch/tree/master/applications/flight_delays. The raw BTS On-Time Performance data are publicly available at https://www.transtats.bts.gov/ under US Government public domain license. The analysis requires the following monthly CSV files for 2024 months 1--6. Feature engineering, model training, and evaluation can be reproduced by running `evaluate.py` (model tournament), `review_experiments.py` (SHAP, calibration, temporal robustness), and `generate_plots.py` (all figures).

## References

AhmadBeygi, S., Cohn, A., Guan, Y., & Belobaba, P. (2008). Analysis of the potential for delay propagation in passenger airline networks. *Journal of Air Transport Management*, 14(5), 221--236.

AhmadBeygi, S., Cohn, A., & Lapp, M. (2010). Decreasing airline delay propagation by re-allocating scheduled slack. *IIE Transactions*, 42(7), 478--489.

Ball, M. O., Barnhart, C., Dresner, M., Hansen, M., Neels, K., Odoni, A., Peterson, E., Sherry, L., Trani, A., & Zou, B. (2010). Total delay impact study. *NEXTOR Research Report*.

Barnhart, C., Fearing, D., Odoni, A., & Vaze, V. (2014). Demand and capacity management in air transportation. *EURO Journal on Transportation and Logistics*, 3(3--4), 135--155.

Baspinar, B., & Koyuncu, E. (2016). A data-driven air transportation delay propagation model using epidemic process models. *International Journal of Aerospace Engineering*, 2016, 4836260.

Beatty, R., Hsu, R., Berry, L., & Rome, J. (1999). Preliminary evaluation of flight delay propagation through an airline schedule. *Air Traffic Control Quarterly*, 7(4), 259--270.

Belcastro, L., Marozzo, F., Talia, D., & Trunfio, P. (2016). Using scalable data mining for predicting flight delays. *ACM Transactions on Intelligent Systems and Technology*, 8(1), 1--20.

Bratu, S., & Barnhart, C. (2006). Flight operations recovery: New approaches considering passenger recovery. *Journal of Scheduling*, 9(3), 279--298.

Campanelli, B., Fleurquin, P., Arranz, A., Etxebarria, I., Ciruelos, C., Eguiluz, V. M., & Ramasco, J. J. (2016). Comparing the modelling of delay propagation in the US and European air traffic networks. *Journal of Air Transport Management*, 56, 12--18.

Choi, S., Kim, Y. J., Briceno, S., & Mavris, D. (2016). Prediction of weather-induced airline delays based on machine learning algorithms. *AIAA DASC*.

Dunbar, M., Froyland, G., & Wu, C. (2012). Robust airline schedule planning: Minimizing propagated delay in an integrated routing and crewing framework. *Transportation Science*, 46(2), 204--216.

EUROCONTROL (2023). *CODA Digest: All-Causes Delay and Cancellations to Air Transport in Europe --- Annual 2022*. Brussels: EUROCONTROL.

Fleurquin, P., Ramasco, J. J., & Eguiluz, V. M. (2013). Systemic delay propagation in the US airport network. *Scientific Reports*, 3, 1159.

Fleurquin, P., Ramasco, J. J., & Eguiluz, V. M. (2014). Characterization of delay propagation in the US air-transportation network. *Transportation Journal*, 53(3), 330--344.

Forbes, S. J., Lederman, M., & Tombe, T. (2019). Quality disclosure and the timing of airline delays. *Review of Economics and Statistics*, 101(5), 843--856.

Gui, G., Liu, F., Sun, J., Yang, J., Zhou, Z., & Zhao, D. (2019). Flight delay prediction based on aviation big data and machine learning. *IEEE Transactions on Vehicular Technology*, 69(1), 140--150.

Guimera, R., Mossa, S., Turtschi, A., & Amaral, L. A. N. (2005). The worldwide air transportation network: Anomalous centrality, community structure, and cities' global roles. *Proceedings of the National Academy of Sciences*, 102(22), 7794--7799.

Henricksen, D., & Olaya, C. (2020). Flight delay prediction using machine learning: A comparative study. *Computers & Industrial Engineering*, 148, 106717.

Kim, Y. J., Choi, S., Briceno, S., & Mavris, D. (2016). A deep learning approach to flight delay prediction. *IEEE/AIAA Digital Avionics Systems Conference*.

Lan, S., Clarke, J. P., & Barnhart, C. (2006). Planning for robust airline operations: Optimizing aircraft routings and flight departure times to minimize passenger disruptions. *Transportation Science*, 40(1), 15--28.

Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30, 4765--4774.

Pyrgiotis, N., Malone, K. M., & Odoni, A. (2013). Modelling delay propagation within an airport network. *Transportation Research Part C*, 27, 60--75.

Rebollo, J. J., & Balakrishnan, H. (2014). Characterization and prediction of air traffic delays. *Transportation Research Part C*, 44, 231--241.

Strobl, C., Boulesteix, A. L., Zeileis, A., & Hothorn, T. (2007). Bias in random forest variable importance measures: Illustrations, sources and a solution. *BMC Bioinformatics*, 8, 25.

Wu, C. (2005). Inherent delays and operational reliability of airline schedules. *Journal of Air Transport Management*, 11(4), 273--282.

Zanin, M., & Lillo, F. (2013). Modelling the air transport with complex networks: A short review. *European Physical Journal Special Topics*, 215(1), 5--21.
