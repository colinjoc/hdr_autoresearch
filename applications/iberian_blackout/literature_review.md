# Literature Review: Cascade Risk Prediction for the Iberian Peninsula Blackout

## 1. Introduction

On 28 April 2025, at 12:33 Central European Summer Time (CEST), the interconnected power systems of continental Spain and Portugal experienced a total blackout, disconnecting approximately 31 gigawatts (GW) of generation and leaving 47 million people without electricity. The European Network of Transmission System Operators for Electricity (ENTSO-E) classified the event as Incident Classification Scale 3, making it the most severe blackout in Continental Europe in over two decades (ENTSO-E Expert Panel 2026). The final investigation revealed a novel failure mode: an overvoltage-driven cascading collapse, fundamentally distinct from the under-frequency cascades that characterized previous major European blackouts. This literature review surveys the theoretical and empirical foundations relevant to predicting such events, spanning power system stability theory, historical blackout analysis, renewable energy integration challenges, machine learning (ML) methods for grid anomaly detection, and the specific technical context of the Iberian grid.

## 2. Power System Stability Fundamentals

### 2.1 Stability Definitions and Classification

The foundational framework for power system stability was established by Kundur et al. (2004), who defined stability as "the ability of an electric power system, for a given initial operating condition, to regain a state of operating equilibrium after being subjected to a physical disturbance." The IEEE/CIGRE classification divides stability into three categories: rotor angle stability, frequency stability, and voltage stability. Kundur's textbook (1994, updated 2022 with Malik) remains the standard reference, providing comprehensive treatment of synchronous machine dynamics, excitation systems, and the physical mechanisms underlying each stability category.

Anderson and Fouad (2019, 3rd edition with Vittal and McCalley) provide complementary coverage of transient stability analysis and control system design. Von Meier (2006) offers an accessible conceptual introduction to power system operation, while Bergen and Vittal (2000) and Stevenson and Grainger (1994) provide the mathematical foundations of power flow analysis that underlie contingency assessment.

### 2.2 Voltage Stability and Collapse

Voltage stability, defined as the ability of a power system to maintain steady voltages at all buses after a disturbance, is the primary stability category relevant to the Iberian blackout. Van Cutsem and Vournas (1998) provide the definitive textbook treatment, covering both static and dynamic aspects of voltage instability. Taylor (1994) offers practical methods for voltage stability assessment. Venikov et al. (1989) laid early theoretical groundwork for understanding voltage collapse as a bifurcation phenomenon, while Lee et al. (1991) studied the mechanisms by which voltage collapse propagates through interconnected systems.

Critically, the classical literature focuses overwhelmingly on undervoltage collapse, where excessive reactive power demand relative to supply causes voltages to decline until protective equipment disconnects loads and generators. The IEEE Power System Relaying Committee (2014) documented mitigation strategies oriented toward this conventional mechanism. The Iberian blackout introduced a distinct failure mode -- overvoltage-driven cascading -- where lightly loaded transmission lines, high solar generation, and insufficient reactive power absorption caused voltages to rise above protection thresholds, triggering generator disconnections that further exacerbated the voltage excursion. This mechanism was documented for the first time in academic literature by a 2026 paper in Electric Power Systems Research, which presented a conceptual model of the overvoltage-driven cascade.

### 2.3 Frequency Stability and System Inertia

Frequency stability depends on the balance between generation and load, with system inertia determining the rate at which frequency deviates following a disturbance. Fernandez-Guillamon et al. (2019) provide a comprehensive review of inertia and frequency control strategies, documenting the trajectory from conventional synchronous-machine-dominated grids to systems where power-electronic-interfaced generation provides diminishing inertial response. Denholm et al. (2020) at the National Renewable Energy Laboratory (NREL) offer a practical guide to inertia concepts, distinguishing between physical inertia from rotating mass and synthetic (virtual) inertia emulated by inverter controls.

Smahi et al. (2025) and Alhejji et al. (2024) provide recent reviews of the challenges posed by renewable energy integration to grid inertia. Wang et al. (2024) review control strategies for low-inertia power systems. The ENTSO-E Project Inertia Phase II report (2023) analyzes frequency stability under long-term scenarios with increasing renewable penetration in the Continental Europe Synchronous Area, establishing that initial rate of change of frequency (RoCoF) values exceeding 1 Hz/s can compromise defence plan effectiveness.

A critical finding from the Iberian blackout investigation is that inadequate inertia, while a contributing factor, was not the primary cascade mechanism. The ENTSO-E final report (2026) explicitly states that "even with significantly higher inertia values, the loss of system synchronism would not have been avoided," redirecting analytical attention toward voltage and reactive power control.

## 3. Historical Blackout Analysis

### 3.1 The 2003 Northeast US-Canada Blackout

The August 14, 2003 blackout, which disconnected 55 GW affecting 55 million people across eight US states and the Canadian province of Ontario, was investigated by a joint US-Canada Power System Outage Task Force (2004). The root causes were identified as inadequate vegetation management (tree contact with transmission lines), failure of alarm systems at the responsible utility (FirstEnergy), and inadequate regional-scale situational awareness. Bialek et al. (2005) analyzed the causes of both the North American and Italian blackouts, finding common patterns of protection relay cascades amplifying initial disturbances. This event led directly to the creation of mandatory reliability standards enforced by the North American Electric Reliability Corporation (NERC).

### 3.2 The 2003 Italian Blackout

On September 28, 2003, a cascading failure disconnected 27 GW from the Italian grid, affecting 45 million people for up to 19 hours. Berizzi (2004), Corsi and Sabelli (2004), and Sforna and Delfanti (2006) provided detailed IEEE analyses. The cascade began with overloaded Swiss-Italian interconnectors tripping after tree flashover, followed by loss of synchronism between Italy and the Union for the Co-ordination of Transmission of Electricity (UCTE) network, and ultimately a system-wide under-frequency collapse when automatic load shedding proved insufficient. This event was a classic under-frequency cascade, fundamentally different from the Iberian overvoltage mechanism.

### 3.3 The 2006 European System Disturbance

The November 4, 2006 disturbance, documented in the UCTE final report (2007) and analyzed by Bialek (2007) and Vournas et al. (2008), split the Continental European synchronous area into three islands following the disconnection of a 380 kV line in northern Germany. Over 15 million people lost power, though full resynchronization was achieved within 38 minutes. Silvast and Kaplinsky (2010) analyzed the transnational vulnerability aspects. The relatively rapid recovery reflected the availability of synchronous generation to maintain frequency and voltage within each island.

### 3.4 The 2015 Turkey Blackout

On March 31, 2015, the Turkish power system experienced a nationwide blackout affecting 76 million people (ENTSO-E 2015; Gumus et al. 2023). The event began with inadequate N-1 contingency margins and the tripping of an east-west transmission corridor, splitting the system into two areas with diverging frequencies. The western area experienced under-frequency collapse when thermal generators could not maintain operation at reduced frequency. Zhang et al. (2016) drew lessons for the Chinese grid from this event.

### 3.5 The 2019 United Kingdom Power Disruption

The August 9, 2019 event, documented by the Energy Emergencies Executive Committee (E3C 2020) and Ofgem (2020), saw 1,691 megawatts (MW) of generation disconnect following a lightning strike, causing frequency to drop to 48.8 Hz. Strbac et al. (2020) analyzed implications for decarbonised power systems, noting that the Hornsea One offshore wind farm and Little Barford gas plant both disconnected unexpectedly. Wilson et al. (2021) and Dudgeon et al. (2021) provided detailed frequency analyses. This event presaged the Iberian blackout by demonstrating that inverter-based resources could disconnect during disturbances in ways not anticipated by the transmission system operator (TSO).

### 3.6 The 2021 Continental Europe System Separation

On January 8, 2021, the Continental Europe synchronous area split into two parts following a busbar coupler trip at the Ernestinovo substation in Croatia (ENTSO-E 2021). The northwest area experienced frequency drops to 49.74 Hz while the southeast area saw frequency rise to 50.6 Hz. This near-miss event, occurring just four years before the Iberian blackout, demonstrated the fragility of the European interconnected system under conditions of increasing power flow and decreasing inertia.

### 3.7 Common Patterns and the Iberian Novelty

Pourbeik, Kundur, and Taylor (2006) and the IEEE/CIGRE Joint Task Force (2007) documented common patterns across blackouts: inadequate N-1 security margins, protection relay cascades, insufficient operator situational awareness, and unexpected generation disconnections. Dobson et al. (2001, 2005) provided theoretical frameworks based on self-organized criticality and branching processes to explain the statistical properties of cascading failures. Hines et al. (2009) showed that blackout size distributions follow power-law-like patterns.

The Iberian blackout breaks from all previous Continental European events in its cascade mechanism. Where Italy (2003), Turkey (2015), and the UK (2019) experienced under-frequency cascades driven by generation deficit, the Iberian event was driven by overvoltage caused by generation surplus under specific conditions of high solar penetration, light loading, and inadequate reactive power absorption. This represents a genuinely novel failure mode in the power system stability literature.

## 4. Renewable Energy Integration and Grid Stability

### 4.1 The Spanish Solar Transition

Spain's solar photovoltaic (PV) capacity grew dramatically, with solar becoming the country's top power source in 2024 at 32,043 MW installed capacity (REE 2025). In April 2025, just days before the blackout, Spain achieved its first weekday of 100% renewable generation on the national grid (pv magazine 2025). The pace of deployment outstripped Red Electrica de Espana's (REE's) infrastructure planning, creating grid sections unable to absorb the generation levels being connected (RatedPower 2025). Negative electricity prices, already a growing European phenomenon (pv magazine 2024; Fortune 2026), occurred with increasing frequency in Spain, with over 500 negative-price hours in 2025 alone, reflecting structural oversupply during high-solar periods.

### 4.2 Grid-Forming versus Grid-Following Inverters

Most existing solar PV and wind installations use grid-following inverter controls that track the voltage and frequency established by synchronous machines. Khan et al. (2024) review grid-forming control for inverter-based resources (IBRs), documenting how grid-forming inverters can actively establish voltage and frequency rather than passively following them. Lin et al. (2024) at NREL provide an accessible introduction. Mehedi et al. (2024) and Rosso et al. (2023) compare the performance of grid-forming and grid-following controls, finding that grid-forming inverters improve frequency response by 69% compared to only 3% for grid-following designs. The ENTSO-E investigation found that renewable installations in the Iberian peninsula were operating predominantly in fixed power factor mode (grid-following), providing no dynamic voltage support during the cascade.

### 4.3 Synthetic and Virtual Inertia

Virtual inertia techniques, reviewed by Tamrakar et al. (2020) and Kerdphol et al. (2019), use inverter control algorithms to emulate the inertial response of synchronous generators. Gonzalez-Longatt et al. (2024) assessed synthetic inertia from an actual solar PV plant, finding that PV can provide frequency support comparable to synchronous machines. Coordination between wind turbine synthetic inertia and battery energy storage systems was explored by Gonzalez-Longatt et al. (2024). However, a 2025 review in Cleaner Energy Systems cautioned that virtual inertia strategies face trade-offs between energy reserves and response speed that limit their practical contribution.

### 4.4 System Strength and Short Circuit Ratio

System strength, quantified by the short circuit ratio (SCR), determines grid sensitivity to disturbances. Wu et al. (2018) proposed site-dependent SCR metrics for assessing renewable integration impact, while NERC (2017) provided guidance on integrating IBRs into weak (low SCR) systems. Zhang et al. (2021) evaluated system strength in grids with high renewable penetration. The replacement of synchronous generation with IBRs reduces short circuit levels, since inverters deliver overcurrent of less than 2 per unit (p.u.) compared to 2-5 p.u. from synchronous machines (NERC 2018). This reduction directly affects the grid's ability to regulate voltage during disturbances.

### 4.5 Reactive Power Control

Kumar et al. (2023) review reactive power control in renewable-rich power grids, documenting the shift from synchronous machine-based voltage regulation to inverter-based reactive power provision. The IEA Photovoltaic Power Systems Programme (2024) addresses reactive power management with distributed energy resources (DERs). Ahmed et al. (2025) evaluate control strategies for grid-connected PV systems under varying solar conditions. The ENTSO-E investigation found that conventional generators in the Iberian system achieved less than 75% of required reactive power output during the cascade, while many renewable installations operated in fixed power factor mode that eliminated their reactive power contribution during the voltage excursion.

## 5. Protection System Challenges

The integration of renewables fundamentally changes protection system behavior. Mishra et al. (2024) review adaptive protection schemes for future grids, while the International Electrotechnical Commission (IEC 2025) addresses relay protection for power-electronics-dominated systems. Andreev et al. (2024) propose novel relay protection methods for systems with renewable sources and energy storage. The IEEE Guide C37.246-2017 covers protection systems for transmission-to-generation interconnections. Blackburn and Domin (2014) and Horowitz and Phadke (2014) provide the standard textbook references for protective relaying.

The ENTSO-E investigation of the Iberian blackout found that some renewable installations had overvoltage protection thresholds set below regulatory limits, causing premature disconnection. Additionally, shunt reactors (reactive power absorbers) were available but not activated during the voltage rise, partly due to manual rather than automatic connection procedures. These protection configuration deficiencies amplified the cascade.

## 6. Contingency Analysis and Security Assessment

The N-1 contingency criterion, requiring that the system remain stable following the loss of any single element, is the backbone of power system security assessment. Gholami et al. (2020) review static security assessment methods. Abul'Wafa and El'Garably (2023) extend to N-1-1 conditions. Yang et al. (2023) address computational challenges of contingency analysis for large systems using high-performance computing. Wang et al. (2017) propose security level classification methods under N-1 contingency.

The Iberian blackout revealed that traditional N-1 analysis, designed for systems dominated by synchronous generators, may be inadequate for grids where inverter-based resources constitute the majority of generation. The speed of the cascade (complete collapse within 24 seconds of the first transformer trip) exceeded the timescales assumed by conventional contingency analysis, pointing to a need for dynamic rather than static security assessment.

## 7. Machine Learning for Cascading Failure Prediction

### 7.1 Classification Approaches

Machine learning has been increasingly applied to cascading failure prediction. Li et al. (2024) provide a comprehensive review of ML applications in cascade analysis. Nakarmi et al. (2025) demonstrate that random forests and gradient boosting classifiers can predict cascade outcomes from grid operating parameters including loading levels, load shedding, and topological metrics. Althelaya et al. (2022) revisited gradient boosting approaches for imbalanced power grid anomaly detection, finding that CatBoost outperformed competitors. Wang et al. (2022) applied transformer models to cascade prediction, while Donon et al. (2023) used geometric deep learning for online prediction.

### 7.2 Class Imbalance and Small-Sample Challenges

Blackout events are inherently rare, creating severe class imbalance in training data. He and Garcia (2009) review learning from imbalanced datasets, while Chawla et al. (2002) introduced the Synthetic Minority Over-sampling Technique (SMOTE). Galar et al. (2020) review boosting methods for imbalanced classification. Gunnarsson et al. (2024) find that gradient boosting methods maintain robustness over time in imbalanced risk assessment.

For small-sample problems, leave-one-out cross-validation (LOO-CV) provides the least biased estimate of generalization error (Geisser 1975; Arlot and Celisse 2010), though it exhibits high variance and may be problematic with severe class imbalance. Logistic regression in rare events data is addressed by King and Zeng (2001) and Albert and Anderson (1984). The present study uses LOO-CV on 94 daily samples with 8 positive cases, making variance reduction through ensemble methods and threshold optimization essential.

### 7.3 Model Frameworks

Gradient boosting (Friedman 2001), implemented via scikit-learn (Pedregosa et al. 2011), provides the modeling backbone, supplemented by logistic regression (Friedman et al. 2010), random forests (Breiman 2001), extremely randomized trees (Geurts et al. 2006), and support vector machines (Hsu and Lin 2002). Chen and Guestrin (2016) introduced XGBoost as a scalable tree boosting system. Niculescu-Mizil and Caruana (2005) address probability calibration, which is important when using risk scores for decision-making. Ensemble methods including bagging, boosting, and stacking (Opitz and Maclin 1999; Wolpert 1992) improve robustness on small datasets.

## 8. Power System Resilience and Climate

Perera et al. (2024) in Nature Energy analyze how renewable energy resources affect weather vulnerability of power systems, finding that high renewable penetration can mitigate blackout intensity despite introducing weather-dependent variability. Joskow et al. (2023) in Nature Reviews Electrical Engineering review climate risk resilience for renewable power systems. The IEA (2023) addresses climate resilience in the context of power system transitions. Uddin et al. (2023) comprehensively review extreme weather impacts on energy systems, while Wang et al. (2025) in Nature Communications develop coupled climate-energy models for cascading outages.

These studies contextualize the Iberian blackout within the broader challenge of operating power systems under conditions that are simultaneously more renewable-dependent and more climate-exposed. The event occurred not during extreme weather but during routine sunny midday conditions, suggesting that the risk frontier has expanded from weather extremes to include normal operating states in which the generation mix creates novel vulnerability.

## 9. Real-Time Monitoring and Situational Awareness

Wide-area monitoring systems (WAMS) based on phasor measurement units (PMUs) offer the potential for real-time stability assessment. Kamwa et al. (2011) review WAMS applications, while Zhang et al. (2020) demonstrate PMU-based real-time stability monitoring. Nezam Sarmadi et al. (2016) address oscillation source location using data-driven approaches. The US Department of Energy (2019) documents synchrophasor technology deployment.

The ENTSO-E investigation found that rooftop solar PV (installations below 1 MW) represented a significant blind spot for the Spanish TSO, with incomplete production data preventing accurate real-time assessment of system conditions. This monitoring gap contributed to the failure to detect the developing voltage instability.

## 10. Synthesis and Research Gap

The literature reveals a clear research gap at the intersection of overvoltage cascade mechanisms, machine learning prediction, and high-renewable-penetration grid operations. Classical voltage stability theory focuses on undervoltage; classical blackout analysis focuses on under-frequency; and classical contingency analysis assumes synchronous-machine-dominated systems. The Iberian blackout exposed a failure mode that sits outside all three classical frameworks.

This project addresses the gap by constructing physics-informed proxy features, derived from the overvoltage cascade mechanism documented in the ENTSO-E investigation, and combining them with machine learning classifiers trained on real operational data from the REE API. The approach captures the specific conditions (high solar penetration, low synchronous generation, negative prices, high exports, light loading) that the investigation identified as contributing factors, and evaluates whether daily operational data can predict proximity to the cascade boundary.
