# Literature Review: Flight Delay Propagation in Air Transport Networks

## Theme 1: Domain Fundamentals — Air Transport Network Operations

Air transport systems operate as highly coupled networks where aircraft, crews, gates, and passengers must be coordinated across hundreds of airports in real time. The fundamental unit of airline scheduling is the **rotation**: the sequence of flights (legs) that a single aircraft flies in a day. A typical narrowbody aircraft in the US domestic fleet flies 4-6 legs per day, with turnaround times of 30-60 minutes between legs. These rotations are planned months in advance and form the backbone of the airline's published schedule.

The Bureau of Transportation Statistics (BTS) within the US Department of Transportation (DOT) collects and publishes detailed on-time performance data for all US domestic flights under the Airline Service Quality Performance (ASQP) programme, established by 14 CFR Part 234. Reporting is mandatory for carriers with at least 0.5% of domestic scheduled-service passenger revenue. The data include scheduled and actual departure/arrival times, delay causes (when delay exceeds 15 minutes), tail numbers, carrier codes, and route information. This creates a uniquely rich dataset for studying delay propagation at the individual-flight level.

The FAA classifies delays into five cause categories, reported by carriers to BTS: (1) **Carrier delays** — maintenance, crew problems, aircraft cleaning, baggage handling, fueling; (2) **Weather delays** — significant meteorological events at origin, destination, or en route; (3) **NAS (National Airspace System) delays** — air traffic control, airport operations, heavy traffic volume, airspace restrictions; (4) **Security delays** — evacuation, re-boarding, long screening lines; (5) **Late aircraft delays** — the previous flight with the same aircraft arrived late, causing a downstream departure delay. This fifth category is the primary mechanism of delay propagation through aircraft rotation chains and is the central focus of this study.

**Key references**: Barnhart et al. (2014) provide a comprehensive survey of airline scheduling and operations research; Ball et al. (2010) review total delay impact in the National Airspace System; BTS Technical Documentation (2024) describes the ASQP reporting requirements and data dictionary.

## Theme 2: Delay Propagation Mechanisms

Delay propagation in air transport networks occurs through four primary channels:

**Aircraft rotation propagation** (also called "reactionary delays" or "knock-on effects") is the most direct mechanism. When flight F1 on aircraft N12345 arrives late at airport B, the next scheduled departure F2 of N12345 from B is delayed because the aircraft is not available at the gate. The BTS "LateAircraftDelay" field captures this mechanism. Empirical studies consistently find that aircraft rotation is the single largest propagation channel. Beatty et al. (1999) were among the first to quantify this, showing that 30-40% of all delay minutes in the US domestic system are attributable to late aircraft. AhmadBeygi et al. (2008) traced delay propagation trees through aircraft rotations and found that a single root delay at a hub airport could cascade through 4-7 subsequent flights.

**Crew propagation** occurs when pilots or flight attendants are delayed on an inbound flight and their next assignment departs from the same airport. FAA duty-time regulations (14 CFR Part 117) impose hard limits on crew rest, so a late arrival can trigger mandatory rest breaks that delay subsequent flights. Crew propagation is harder to study with public data because crew assignments are not in the BTS dataset, but Lan et al. (2006) and Dunbar et al. (2012) showed it accounts for 5-15% of propagated delays at major carriers.

**Airport congestion propagation** occurs through shared infrastructure: runways, taxiways, gates, and ground handling equipment. When arrival delays at a hub create a wave of late aircraft, ground resources become overloaded, and even flights with on-time aircraft may be delayed waiting for gates or ground crew. Pyrgiotis et al. (2013) developed a queuing network model showing that airport congestion amplifies delay propagation non-linearly — beyond a critical load threshold, delays grow faster than linearly with traffic volume.

**Passenger connection propagation** is the least operationally significant but most passenger-visible: when connecting passengers from a delayed inbound flight cause the outbound flight to hold at the gate. Airlines generally choose to depart on time rather than hold for connections, making this a minor propagation channel, though Wu (2005) documented cases where high-value connections (many passengers, last flight of the day) led to deliberate holds.

**Key references**: Beatty et al. (1999), AhmadBeygi et al. (2008), Pyrgiotis et al. (2013), Lan et al. (2006), Campanelli et al. (2016), Wu (2005).

## Theme 3: Candidate Features and Design Variables

The bridge from delay propagation theory to computable prediction features involves several categories:

**Rotation chain features** (directly computable from BTS tail numbers):
- Prior flight arrival delay (the most important single feature for predicting current departure delay)
- Rotation position (1st, 2nd, ... Nth leg of the day)
- Cumulative delay accumulated by the aircraft through the day
- Scheduled turnaround time (buffer between scheduled arrival and next departure)
- Actual turnaround time
- Origin and destination of prior flight (hub vs. non-hub)

**Airport state features** (computed from aggregate BTS data):
- Current departure delay rate at origin airport
- Current arrival delay rate at destination airport
- Airport traffic volume (flights per hour)
- Airport delay variance (high variance = unpredictable)
- Hub concentration index (fraction of traffic from a single carrier)

**Temporal features**:
- Hour of day (delays accumulate through the day; morning flights have lowest delay probability)
- Day of week (Monday and Friday highest; Saturday lowest)
- Month/season (summer thunderstorms, winter storms)
- Holiday indicators

**Network topology features**:
- Airport degree (number of routes served)
- Betweenness centrality (how many shortest paths pass through this airport)
- Carrier network density at this airport

**Weather features** (not in BTS data, but BTS reports weather delay as a cause code):
- BTS WeatherDelay gives indirect weather signal
- METAR/TAF data could provide direct weather features (future work)

**Key references**: Rebollo & Balakrishnan (2014) — random forest delay prediction with airport-level features achieving AUC ~0.85; Mueller & Chatterji (2002) — analysis of weather as delay cause; Xu et al. (2005) — network delay models.

## Theme 4: Machine Learning for Flight Delay Prediction

ML approaches to flight delay prediction fall into three categories:

**Classification** (delayed/on-time binary): Rebollo & Balakrishnan (2014) used random forests on airport-level aggregate data to predict whether delays at major airports would exceed thresholds, achieving AUC 0.80-0.85. Choi et al. (2016) applied gradient boosted trees to individual flight delay prediction using BTS data, finding AUC 0.75-0.82 depending on the prediction horizon. Belcastro et al. (2016) benchmarked multiple classifiers on BTS data and found that ensemble methods consistently outperformed single classifiers.

**Regression** (delay magnitude in minutes): Kim et al. (2016) used deep learning (LSTM networks) for departure delay prediction, achieving MAE of 12-15 minutes. Gui et al. (2019) applied XGBoost to BTS data with weather features, reducing MAE to ~10 minutes. The regression task is harder because the delay distribution is heavy-tailed — most flights are on time or slightly early, but some have extreme delays.

**Network/propagation models**: Fleurquin et al. (2013) modeled the US airport network as a complex system and found that delay propagation exhibits characteristics of epidemic spreading — a small number of "super-spreader" airports (major hubs) dominate network-wide delay dynamics. Baspinar & Koyuncu (2016) used Bayesian networks to model delay propagation, finding that aircraft rotation is the dominant transmission mechanism. Zanin et al. (2020) applied complex network analysis and found that delay propagation follows scale-free dynamics.

**Gap in the literature**: Most prediction models treat each flight independently, ignoring the aircraft rotation chain. The few that include rotation features (Rebollo & Balakrishnan 2014, AhmadBeygi et al. 2008) either use aggregate airport-level data or build separate propagation models rather than end-to-end prediction systems. Reconstructing rotation chains from BTS tail numbers and using them as first-class features in a prediction model is an underexplored approach.

**Key references**: Rebollo & Balakrishnan (2014), Fleurquin et al. (2013), Kim et al. (2016), Choi et al. (2016), Gui et al. (2019), Zanin et al. (2020).

## Theme 5: Delay Propagation Containment and Buffer Strategies

Airlines and airports use several strategies to contain delay propagation:

**Schedule padding**: Airlines build buffer time into published schedules to absorb expected delays. The difference between "block time" (scheduled gate-to-gate) and "flight time" (actual air time) has increased by ~8 minutes on average since 2000, partly to improve on-time statistics. Forbes et al. (2019) found that schedule padding is concentrated at congested airports and peak times, suggesting airlines strategically pad where propagation risk is highest.

**Aircraft swaps**: When a delayed aircraft would cascade delays through multiple subsequent flights, dispatchers may swap it with a less-utilized aircraft. This breaks the propagation chain but is operationally expensive and only feasible at hub airports. Bratu & Barnhart (2006) found that optimal swap strategies could reduce passenger delay by 20-30%.

**Turnaround time buffers**: The minimum turnaround time (time between arrival and next departure at a gate) is a critical parameter. Shorter turnarounds increase aircraft utilization but also increase propagation risk. Ahmadbeygi et al. (2010) showed that adding 5 minutes to minimum turnaround times at the 10 busiest US airports would reduce total propagated delay by 15-20%.

**Hub de-peaking**: After 9/11, several US airlines "de-peaked" their hub operations — spreading arrival/departure banks more evenly through the day rather than concentrating them in tight connection banks. This reduced congestion-driven propagation but increased passenger connection times. Campbell et al. (2005) documented the trade-offs.

## Theme 6: Transfer and Generalization Across Conditions

**Temporal generalization**: Flight delay patterns are strongly non-stationary. Summer thunderstorms, winter snowstorms, holiday travel, and airline schedule changes create distributional shifts. Models trained on summer data perform poorly on winter data and vice versa. Temporal cross-validation (train on past months, test on future months) is essential and reveals significant performance drops vs. random CV. Rebollo & Balakrishnan (2014) showed 5-10% AUC degradation with temporal vs. random splits.

**Airport generalization**: Delay dynamics differ fundamentally between hub and non-hub airports. Hub airports have high propagation potential (many connecting flights, tight turnarounds) while point-to-point airports have lower coupling. Models trained on hub airports may not transfer to regional airports.

**Carrier generalization**: Different carriers have different operational strategies (turnaround times, maintenance scheduling, crew utilization) that affect propagation patterns. A model that captures carrier-specific propagation patterns may outperform a generic model.

**Scale effects**: The US domestic system has ~600k flights/month from ~15 reporting carriers at ~350 airports. This scale permits fine-grained analysis of propagation at the individual tail-number level, which is not possible with smaller datasets.

## Theme 7: Related Problems and Cross-Domain Insights

**Railway delay propagation**: Train delays propagate through similar mechanisms (shared infrastructure, rolling stock rotation), but with the added constraint of fixed track topology. Goverde (2010) developed max-plus algebra models for train delay propagation that could inspire analytical approaches for aircraft.

**Power grid cascading failures**: Electrical grid cascades share structural similarities with delay propagation — a local failure (generator trip) cascades through the network via shared infrastructure (transmission lines). The network science tools used to study grid cascades (percolation theory, epidemic spreading) have been applied to air transport by Fleurquin et al. (2013).

**Epidemic spreading**: Delay propagation through airport networks has been modeled using SIR-type (Susceptible-Infected-Recovered) epidemic models, where "infected" airports spread delay to "susceptible" airports through connecting flights. This framework naturally captures the concepts of "super-spreader" airports and "herd immunity" (schedule buffers).

**Supply chain disruption propagation**: Supply chain research on disruption propagation (Craighead et al. 2007) identifies node criticality and path redundancy as key factors — the same concepts that determine whether an airport delay propagates or is absorbed.
