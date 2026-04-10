# Literature Review — Flight Delay Propagation Through US Airline Networks

## 1. Domain Fundamentals: Airline Operations and Scheduling

The US airline industry operates approximately 7 million domestic flights annually, connecting 500+ airports through a hub-and-spoke network structure [7, 11, 33]. The fundamental operational unit is the *aircraft rotation*: a single aircraft flies 3-6 legs per day, moving from airport to airport in a chain. Each leg has a scheduled departure time, arrival time, and a turnaround window at each intermediate airport during which the aircraft is unloaded, cleaned, refueled, and reloaded for the next leg [7, 9, 137].

The *turnaround time* is the minimum ground time required between consecutive legs. For narrow-body domestic aircraft, this is typically 35-55 minutes depending on carrier and aircraft type [128, 183]. The *schedule buffer* is the difference between the scheduled turnaround time and the operational minimum — it represents the airline's tolerance for absorbing delay from the inbound flight. Airlines face a fundamental trade-off: more buffer absorbs more delay but reduces aircraft utilization (fewer flights per aircraft per day, higher cost per available seat mile) [2, 64, 120].

Belobaba, Odoni, and Barnhart's textbook "The Global Airline Industry" [7] establishes the foundational framework: airline scheduling is a hierarchical process of fleet assignment (which aircraft type on which route), aircraft rotation (which specific tail number flies which sequence of legs), and crew pairing (which pilots and flight attendants work which sequence of flights). Disruptions at any level propagate to downstream levels through these assignment chains [9, 107, 174].

De Neufville and Odoni's "Airport Operations" [164] describes the airport side: runway capacity is the binding constraint at most major airports, with typical acceptance rates of 40-80 arrivals per hour depending on runway configuration and weather. When demand exceeds capacity, Air Traffic Control (ATC) imposes ground delay programs (GDPs) that hold flights at their origin airports, and airborne holding patterns that add fuel consumption and delay [171, 195].

## 2. Delay Propagation Mechanisms

### 2.1 Aircraft Rotation (Late Aircraft)

The dominant delay propagation mechanism is the aircraft rotation chain. When an aircraft arrives late from its previous flight, the next flight on that aircraft cannot depart until the turnaround is complete, regardless of whether the crew, passengers, and gate are ready [1, 2, 20, 21].

Pyrgiotis, Malone, and Odoni (2013) [1] developed the seminal airport-network queueing model for delay propagation, showing that aircraft rotation is responsible for the majority of "reactionary delay" (delay caused by a previous event, as opposed to "primary delay" caused by a new event). Their model treats each airport as a server in a queueing network, with aircraft moving between servers. Delays at one server propagate to downstream servers through the aircraft rotation chain.

AhmadBeygi, Cohn, Guan, and Belobaba (2008) [2] demonstrated the critical role of schedule buffers: the amount of delay that propagates from one leg to the next depends on the difference between the incoming delay and the available buffer. Their key insight is that propagation is *nonlinear* — small delays are fully absorbed by the buffer, while delays exceeding the buffer propagate almost completely to the next leg. This threshold effect means that the distribution of propagated delay is highly skewed: most legs absorb the incoming delay completely, but the minority that exceed the buffer propagate large amounts [28, 90].

Lan, Clarke, and Barnhart (2006) [13, 20] connected tail assignment optimization to delay propagation: by choosing which aircraft serves which rotation, airlines can mitigate propagation risk. Their robust scheduling approach explicitly minimizes the expected propagated delay by placing higher-buffer rotations on routes with higher delay variance. Rosenberger, Johnson, and Nemhauser (2003) [12] addressed the recovery problem: when a disruption occurs, how should the airline reassign aircraft to minimize total downstream propagation?

Eurocontrol's Performance Review Commission [24, 71, 102] tracks "reactionary delay" as a distinct category in European ATM statistics, finding that reactionary delay (equivalent to BTS "late aircraft" category) accounts for approximately 35-45% of total delay-minutes in Europe, with the fraction increasing during peak congestion periods.

### 2.2 Airport Congestion (NAS Delays)

Airport congestion arises when the demand for runway, taxiway, or gate capacity exceeds supply. The FAA manages congestion through Traffic Flow Management (TFM) programs, including Ground Delay Programs (GDPs) that hold flights at their origin, miles-in-trail restrictions, and ground stops [66, 127, 171].

Peterson, Taga, and Abdul-Baki (1995) [91, 140] developed queueing models for runway operations, showing that delay increases superlinearly with demand-to-capacity ratio. When the ratio exceeds approximately 0.85, delays escalate rapidly due to queueing effects. Simaiakis, Khadilkar, Balakrishnan, Reynolds, and Hansman (2014) [27] demonstrated that controlling the pushback rate (the rate at which aircraft are released from gates onto taxiways) can reduce total system delay by preventing taxi congestion.

Ball, Hoffman, Odoni, and Rifkin (2003) [171] analyzed Ground Delay Programs, showing that centralizing the delay allocation decision (distributing delay across multiple origin airports rather than having all delay occur at the destination) reduces total system delay. This is because holding aircraft at gates is cheaper than holding them in the air.

Hub airports are particularly vulnerable to congestion because they concentrate traffic into narrow "banks" of arrivals and departures to facilitate passenger connections. Brueckner and Spiller (1994) [33] showed that hub-and-spoke structure increases efficiency through economies of density but concentrates delay risk. Guimera, Mossa, Turtschi, and Amaral (2005) [11] characterized the US air network as a scale-free small-world network where a few hub airports handle disproportionate traffic.

### 2.3 Weather

Weather is the root cause of a significant fraction of primary delay (delay not propagated from a previous event) but is a smaller fraction of total delay because weather delays do not propagate as directly as aircraft rotation delays [118, 144].

Klein, Kavoussi, and Lee (2009) [16] identified "weather-impacted traffic flow management" as the primary weather-delay mechanism: bad weather at a destination airport reduces its acceptance rate, causing ATC to impose GDPs or ground stops on inbound flights at their origins. Allan, Beesley, Evans, and Gaddy (2001) [118] at MIT Lincoln Laboratory established the foundational framework for weather-delay analysis, showing that convective weather (thunderstorms) has the largest impact per event but is confined to summer months, while low-ceiling/visibility events are more common in winter and cause sustained capacity reductions.

Ning, Strauss, and Bliss (2016) [108] quantified the impact of thunderstorms specifically on US airline schedule performance, finding that convective weather accounts for approximately 60% of weather-related delays in summer but only 15% in winter. Simaiakis and Balakrishnan (2009) [30] showed that wind direction and speed affect runway configuration and acceptance rates, with crosswind components above 15 knots forcing single-runway operations at many airports.

### 2.4 Crew and Ground Operations

Crew-related delays arise when flight crew (pilots and flight attendants) are not available at the departure gate on time, often because their inbound flight was delayed [14, 76, 87]. Unlike aircraft, crew cannot simply "connect" to the next flight by physical proximity — they must complete rest requirements, cross-check passengers, and comply with duty-time limits [67, 76].

Abdelghany, Abdelghany, and Ekollu (2008) [14] modeled crew recovery after disruptions, showing that crew constraints compound aircraft rotation delays. Yen and Birge (2006) [76] developed robust crew pairing methods that maintain buffer in crew assignments, analogous to schedule buffer in aircraft rotations. Maher, Desaulniers, Desrosiers, and Soumis (2014) [43] addressed the integrated crew-and-fleet rerouting problem, showing that joint optimization reduces total disruption cost by 15-20% compared to sequential recovery.

Gate conflicts — when two flights are scheduled at the same gate within a short time window — are a known delay source that is difficult to model from public data because gate assignments are not published in BTS data. Ding, Lim, Rodrigues, and Zhu (2005) [49] optimized gate assignment to minimize gate conflicts, finding that gate utilization above 80% leads to increasing conflict rates.

## 3. Candidate Features and Design Variables

The literature identifies several categories of predictive features for flight delay:

**Aircraft rotation features** are the strongest predictors. The previous flight's arrival delay is the single most informative feature [1, 2, 20, 85]. The rotation position (which leg in the day's chain), the accumulated delay over multiple legs, and the carrier's buffer strategy all contribute [13, 64, 120].

**Airport congestion features** capture the demand-capacity balance: the number of flights scheduled in the same hour, the runway acceptance rate (which depends on weather and configuration), and historical delay rates at the airport [27, 91, 140]. Gopalakrishnan and Balakrishnan (2017) [85] showed that network-level congestion features (delay at connected airports, not just the origin) improve prediction.

**Weather features** from METAR observations — ceiling height, visibility, wind speed and direction, precipitation, and present weather codes (thunderstorm, freezing rain, fog) — are available in real time from NOAA's Integrated Surface Database [16, 30, 75, 108, 160]. Rebollo and Balakrishnan (2014) [10] found that weather features add 3-5 percentage points of accuracy to departure delay prediction models.

**Temporal features** — hour of day, day of week, month, holiday indicators — capture systematic patterns in delay accumulation and seasonal weather [48, 83, 197, 205].

## 4. Machine Learning for Flight Delay Prediction

### 4.1 Classical ML Approaches

Rebollo and Balakrishnan (2014) [10] applied Random Forests to departure delay prediction at individual airports, achieving Area Under the Receiver Operating Characteristic Curve (AUC-ROC) of 0.70-0.80 for binary delay prediction. Their key contribution was demonstrating that weather features and historical delay features are complementary: weather captures root-cause events, while historical delay captures persistent congestion.

Belcastro, Marozzo, Talia, and Trunfio (2016) [99] compared Random Forests, Support Vector Machines (SVMs), and Naive Bayes on BTS data, finding Random Forests consistently best for the tabular feature structure. Khaksar and Sheikholeslami (2019) [145] systematically ranked features for delay prediction, finding departure time, carrier, origin airport, and weather as the top four categories.

### 4.2 Gradient Boosting Approaches

XGBoost (Chen and Guestrin, 2016) [45] and LightGBM (Ke et al., 2017) [46] have become the dominant approaches for tabular flight delay prediction due to their ability to capture nonlinear feature interactions without explicit feature engineering. Ding (2017) [119] showed XGBoost outperforming Random Forests on BTS delay data by 5-8% in AUC. Sternberg, Soares, Carvalho, and Ogasawara (2017) [193] achieved similar results with gradient boosting on Brazilian flight data.

### 4.3 Deep Learning Approaches

Chakrabarty (2019) [17] applied Long Short-Term Memory (LSTM) networks to departure delay prediction, treating delay as a time series across the day. Gui, Liu, Zhang, Shen, De Almeida Lobo, Hou, Deek, and Pei (2020) [18] used Convolutional Neural Networks (CNNs) on historical delay patterns, achieving modest improvements over gradient boosting. Kim, Choi, Jun, and Chang (2016) [63] introduced deep learning for airport-level delay prediction.

Yu, Wang, Liao, Jin, Cai, and Zhang (2019) [121] applied deep learning to airport delay prediction, finding that the improvement over gradient boosting is typically 1-3% in MAE — a finding consistent with the observation that the delay signal is largely linear [80, 202].

### 4.4 Graph Neural Networks

Pang, Xu, and Liu (2021) [100] applied Graph Neural Networks (GNNs) to air traffic flow management, treating the airport network as a graph where airports are nodes and flights are edges. Cai, Vandebona, and Zhong (2022) [203] used Graph Convolutional Networks (GCNs) for delay propagation prediction, finding that network topology features (airport centrality, connectivity) add modest predictive value beyond local features.

### 4.5 Reviews

Zoutendijk and Mitici (2021) [19] published a comprehensive review of ML for flight delay prediction in Computers & Operations Research, cataloging 50+ studies and finding that: (a) gradient boosting consistently outperforms deep learning on tabular flight features, (b) the choice of features matters more than the choice of model, and (c) previous-flight delay and weather are the two most impactful feature categories. Oza, Sharma, Pipralia, and Kumar (2023) [56] and Henrique, Andrade, and Wittevrongel (2021) [55] reach similar conclusions.

The 2025 reviews in the Wiley Journal of Advanced Transportation [125] and Springer [126] both identify airline-specific versus airport-specific propagation mechanisms as poorly modeled — the gap this project addresses.

## 5. Delay Variance Decomposition and Cause Attribution

### 5.1 BTS Delay Cause Codes

Since 2003, BTS has required airlines to report delay causes for flights delayed 15+ minutes, decomposed into five categories: carrier, weather, National Aviation System (NAS), security, and late aircraft [61, 201]. The "late aircraft" category directly measures aircraft rotation propagation: it records the minutes of delay attributable to the late arrival of the aircraft from its previous flight.

Tu, Ball, and Jank (2008) [35] developed a Bayesian decomposition of delay causes, finding that the BTS categories are noisy but informative at the aggregate level. The DOT Inspector General (2000) [113] documented that airlines self-report delay causes and may systematically misattribute them — for example, reporting a crew delay as "NAS" or "weather" to minimize the carrier's accountability.

### 5.2 Model-Based Decomposition

An alternative to cause-code decomposition is model-based decomposition: measure how much of the model's predictive power comes from different feature groups. This approach avoids the self-reporting bias in BTS cause codes. Gopalakrishnan and Balakrishnan (2017) [85] used this approach to show that network-level features (delay at connected airports) explain approximately 15-20% of the variance not captured by local features alone.

## 6. Schedule Padding and Buffer Optimization

Airlines strategically pad their schedules — adding extra time beyond the minimum required — to improve on-time statistics. Skaltsas, Barnhart, and Jacquillat (2022, 2023) [64, 120] analyzed schedule padding as a strategic interaction: when one airline pads more, it absorbs more delay from the shared airport infrastructure, creating a positive externality for other airlines. But padding is costly (reduced aircraft utilization), so airlines underinvest in padding from a system perspective.

The implication for delay propagation is direct: carriers with less padding (budget carriers like Spirit, Frontier) propagate more delay through their rotation chains, while carriers with more padding (Southwest, Delta) absorb more. This carrier-specific propagation rate is a key feature candidate for prediction models.

Wu and Caves (2004) [183] analyzed turnaround time variability, showing that turnaround buffer is the single most effective tool for breaking propagation chains. Cook and Tanner (2015) [128] estimated the cost of delay at European airports, finding that one minute of delay costs airlines 50-100 euros depending on aircraft type and phase of flight, with ground delay cheaper than airborne delay. Pyrgiotis and Odoni (2016) [204] analyzed the interaction between airport capacity constraints and airline schedule padding.

## 7. Related Problems: Network Propagation and Complex Systems

Flight delay propagation is an instance of a broader class of problems in network science: how do disturbances propagate through interconnected systems? Barabasi and Albert (1999) [133] showed that scale-free networks (like the US air network) are robust to random failures but vulnerable to targeted attacks on high-degree nodes (hub airports). Watts and Strogatz (1998) [134] showed that small-world properties (short average path lengths) facilitate rapid propagation of disturbances.

Fleurquin, Ramasco, and Eguiluz (2013) [3] published the landmark study in Nature Scientific Reports applying epidemiological models to flight delay contagion, showing that delays spread through the network in a manner analogous to disease propagation. They found a critical threshold: when the initial delay fraction exceeds approximately 10%, the system transitions from local containment to network-wide cascade. Lacasa, Cea, and Zanin (2009) [142] found evidence of self-organized criticality in delay propagation, suggesting the system naturally operates near a critical point.

Mazzarisi, Zaoli, and Lillo (2020) [141] developed methods for identifying and quantifying delay propagation chains in airline networks, tracing cascades through multiple legs and airports. Their "propagation tree" methodology allows measurement of cascade depth (how many legs a delay ripples through) and breadth (how many aircraft are affected).

The cross-domain connection to public transit delay propagation (Schobel, 2001 [78]) provides a useful contrast: in rail systems, the "wait or depart" decision at each station determines whether delay propagates along the line. In aviation, the analogous decision is whether to hold a departing aircraft for connecting passengers — but this is rarely done for domestic flights, so propagation is primarily through the aircraft and crew chains rather than through passenger connections.
