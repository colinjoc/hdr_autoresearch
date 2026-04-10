# Literature Review — Predicting Cascading Delay Days on Dublin's DART Commuter Rail

## 1. Domain Fundamentals: Railway Operations and Timetabling

Railway operations are governed by the interaction of timetable design, infrastructure capacity, rolling stock availability, and external disruptions [P001, P070, P072]. The foundational textbook by Hansen and Pachl [P001] establishes the core concepts: headway (the minimum time separation between consecutive trains), dwell time (time spent at stations for passenger exchange), running time (time between stations including acceleration and braking), and buffer time (the difference between scheduled and minimum running time, providing recovery margin for small delays).

The Periodic Event Scheduling Problem (PESP), formalised by Serafini and Ukovich [P182], provides the mathematical framework for periodic timetables used by most European railway operators. Liebchen [P011, P127] extended this to synchronisation constraints at interchange stations, directly relevant to the Dublin Area Rapid Transit (DART) network where services from the Northern Line (Malahide/Howth) connect with the Southern Line (Bray/Greystones) through the Connolly-Tara Street-Pearse city centre section.

Capacity analysis follows the International Union of Railways (UIC) Leaflet 406 methodology [P067], measuring capacity consumption as the fraction of available time slots occupied by scheduled services. Landex [P065, P066] demonstrated that junction capacity is typically the binding constraint, not line capacity. This is particularly relevant to Connolly Station, where DART, InterCity, and Commuter services share a limited number of platform faces and signal routes through the 1970s-era interlocking.

Single-track sections impose additional capacity constraints. Harrod [P097] and Lai and Barkan [P098] showed that single-track capacity is approximately 60-70% of double-track capacity due to the requirement for trains to wait for opposing movements. The Bray-Greystones section of the DART line is single-track along the coast, and this section is the physical bottleneck for Southern Line frequency.

## 2. Delay Propagation and Knock-On Effects

Train delays rarely remain isolated. Yuan [P004, P005] developed the foundational stochastic model for delay propagation, showing that delays at one point in the network propagate to downstream services through shared infrastructure (junctions, platforms, single-track sections) and shared resources (rolling stock, crew). The propagation rate depends on the ratio of buffer time to initial delay — when buffer time is insufficient to absorb the initial delay, the knock-on effect grows.

Goverde [P002, P003, P112] introduced max-plus algebra as the mathematical framework for timetable stability analysis. A timetable is stable if any delay eventually dissipates to zero through the built-in recovery time. When the timetable becomes critical — meaning the minimum cycle time equals the scheduled cycle time — any delay becomes permanent and propagates indefinitely. This provides the theoretical explanation for the DART punctuality collapse: the September 2024 timetable change reduced buffer times to near-critical levels, transforming a stable timetable into one where delay propagation is effectively permanent.

Barta and Rizzoli [P006] developed scalable delay propagation algorithms for large networks. Meester and Muns [P051] provided analytical formulas for knock-on delays. Corman, D'Ariano, and Hansen [P034] specifically analysed cascading delay dynamics, showing that cascades follow a characteristic pattern: initial disruption, primary delay (direct effect), secondary delay (knock-on to dependent services), and in severe cases, tertiary delay (network-wide degradation). Janssen and Goverde [P181] quantified knock-on effects in the Dutch network, finding that a single delayed train at a major junction could affect 5-12 downstream services.

The DART network's vulnerability to cascading delay is extreme because of its linear topology. Unlike mesh networks where delays can be absorbed by rerouting, the DART line has essentially no alternative paths — a delay at Connolly propagates in both directions with no escape route [P036, P133].

## 3. Timetable Robustness and Buffer Time Design

The timetable robustness literature directly addresses the mechanism behind the DART punctuality collapse. Vromans, Dekker, and Kroon [P025] showed that timetable supplements (buffer times) serve three functions: (1) absorbing stochastic running time variation, (2) providing recovery time after small delays, and (3) maintaining connections at interchange stations. Removing buffer time below the stochastic variation threshold causes the timetable to become structurally unrecoverable.

Dewilde et al. [P026, P137, P126] developed stochastic robustness measures for Belgian railway timetables, demonstrating that a 1-minute reduction in buffer time at a critical junction can increase system-wide delay by 5-10 minutes per hour. Burggraeve et al. [P007, P183] extended this to robust timetabling under stochastic disruptions, showing that robustness is not proportional to total buffer — it depends critically on WHERE the buffer is placed. Buffer at junctions is 3-5 times more valuable than buffer on open line sections.

Caimi et al. [P010] applied these principles to complex stations (specifically Bern, Switzerland, which has similar junction complexity to Connolly). They found that the minimum feasible buffer at a complex junction is approximately 2 minutes for a 10-minute headway service — below this threshold, the junction becomes chronically congested. The DART post-September 2024 timetable reportedly reduced turnaround buffer at Connolly from approximately 4 minutes to approximately 2 minutes [P020, P200], placing it at or below this theoretical minimum.

Kroon, Maroti, and Nielsen [P037] used stochastic simulation to determine optimal buffer allocations for the Dutch railway network, finding that the optimal total buffer is 15-20% of running time for suburban services. Moltrecht [P138] analysed schedule padding for on-time performance, confirming that the relationship between buffer time and punctuality is highly nonlinear — small reductions in buffer below the threshold cause disproportionate punctuality losses.

## 4. Machine Learning for Train Delay Prediction

Machine learning (ML) approaches to train delay prediction have grown rapidly since 2015. Spanninger, Trivella, and Corman [P119] provide the most comprehensive survey, covering 150+ publications. They categorise approaches by prediction horizon (short-term: <30 minutes, medium-term: 30 min to 6 hours, long-term: next-day), input features (operational data, weather, infrastructure, historical patterns), and model families (tree-based, neural, Bayesian).

Oneto et al. [P029] used deep learning for Italian train delay prediction, achieving mean absolute error (MAE) of approximately 3 minutes on a per-train basis. However, they noted that aggregate daily predictions are more useful for operational planning than per-train predictions. Marquez, Nozick, and Turnquist [P027] compared ML methods for passenger train delay prediction, finding that gradient boosted trees outperformed neural networks on tabular railway data — consistent with the broader finding that tree methods dominate on structured tabular data [P021, P155].

Kecman and Goverde [P030] used kernel methods for delay prediction on the Dutch network, achieving strong per-station predictions. Li and Kecman [P042] specifically addressed weather-related delays using random forests, finding that wind speed and temperature were the most important weather features for Dutch railway delays.

For daily-level prediction (the timescale of our DART model), the literature is sparser. Tsapakis, Schneider, and Bolbol [P061] analysed daily delay patterns in relation to weather for US commuter rail. Chapman et al. [P104] built weather-based delay prediction models for British railways, finding that wind speed explained 15-25% of daily delay variance and temperature extremes explained an additional 5-10%.

Graph-based approaches [P032, P088, P173] have shown promise for capturing network structure effects but require per-train, per-station data that is unavailable for DART without a GTFS-RT collection campaign.

## 5. Weather Effects on Railway Operations

The weather-railway interaction literature is substantial. Xia and Van Arem [P012, P062] provide the comprehensive review, categorising weather effects by mechanism: wind (speed restrictions, infrastructure damage, overhead line issues), rainfall (adhesion, flooding, signal failures), temperature (rail buckling in heat, frozen points in cold), snow/ice (point failures, visibility), and fog (reduced visibility for level crossings).

Dobney et al. [P013, P043] quantified UK-specific weather-rail interactions, finding that wind speeds above approximately 45 mph (72 km/h) trigger speed restrictions on most UK routes, while temperatures below -5 degrees Celsius cause a significant increase in point failures. Baker [P014] and Dorigatti et al. [P047] analysed aerodynamic effects on trains, showing that coastal routes are particularly vulnerable to cross-winds — directly relevant to the Bray-Greystones section which runs along exposed sea cliffs.

For Ireland specifically, Hickey [P148] documented extreme wind events and their transport impacts, noting that the prevailing south-westerly winds are less damaging to east-facing coastal infrastructure than easterly storms. Nogal and O'Connor [P090] provided an Irish-specific analysis of extreme weather effects on railway operations. The Environmental Protection Agency (EPA) Ireland [P152] assessed climate change impacts on Irish railway infrastructure, noting that the Bray-Greystones coastal section is among the most climate-vulnerable rail infrastructure in the country due to sea-level rise, coastal erosion, and increased storm frequency.

Olofsson and Lewis [P044] reviewed autumn adhesion problems (leaf fall on rails), which is a significant factor in the October-November peak of DART delays. Kellermann et al. [P045] analysed flooding impacts on railway operations, relevant to the low-lying sections of the DART line near Dublin Bay.

## 6. GTFS and Open Transit Data Analysis

The General Transit Feed Specification for Real-Time updates (GTFS-RT) provides a standardised format for publishing real-time transit information [P015, P016]. The National Transport Authority (NTA) Ireland publishes GTFS-RT feeds for all Irish public transport services through its developer portal [P093]. However, as Zervaas [P015] notes, GTFS-RT is a feed, not an archive — it provides current positions and trip updates but does not store historical data. Building a historical dataset requires a persistent collection infrastructure running 24/7.

Kujala et al. [P016] demonstrated that GTFS data (both static and real-time) can be used for transit network analysis, demand estimation, and service quality evaluation. Transitland [P017] provides an open aggregation platform, but its historical coverage of Irish rail services is incomplete.

The lack of a publicly available historical GTFS-RT archive for Irish Rail is the single biggest data limitation for this project. The published Irish Rail punctuality reports [P019] provide monthly aggregates but not daily or per-service data. This necessitates the synthetic data approach used in this project — generating daily punctuality figures calibrated to the published monthly means.

## 7. Irish Rail Context and Cross-Domain Insights

The Irish rail system operates under specific constraints not found in larger European networks [P091, P092, P142]. DART serves approximately 45,000 daily passengers on approximately 150 daily services across approximately 32 stations. The network is small enough that a single disruption at the central hub (Connolly) affects the entire system — there are no parallel routes or diversionary options [P198].

The DART+ programme [P096, P146] plans to extend electrification and increase capacity, but the core bottleneck at Connolly Station requires signalling upgrade rather than electrification extension. The NBRU (National Bus and Rail Union) has publicly stated that the September 2024 timetable changes were introduced without adequate buffer time, and that the resulting operational difficulties were foreseeable [P200].

The Greater Dublin Area Transport Strategy [P143, P145] acknowledges the capacity constraint at Connolly and plans for station redevelopment, but this is a multi-decade project. In the interim, the NTA annual report [P018] shows that DART punctuality targets (90% within 5 minutes) were consistently met before the September 2024 timetable change and consistently missed after it.

Cross-domain insights come from the Dutch, Swiss, and Scandinavian railway literature, where dense suburban operations face similar challenges. The Dutch experience [P048, P053] shows that delay propagation on dense urban networks follows predictable patterns amenable to statistical modelling. The Swiss experience [P099, P010] demonstrates that buffer time at junction stations is the most cost-effective intervention for punctuality improvement. The Nordic benchmarking [P205, P128] provides context for European railway performance standards.

The transfer learning literature [P089, P168] suggests that models trained on one railway network can partially transfer to another, but network-specific features (topology, signalling, weather exposure) dominate the prediction. This supports our approach of building a DART-specific model rather than adapting a generic railway delay predictor.
