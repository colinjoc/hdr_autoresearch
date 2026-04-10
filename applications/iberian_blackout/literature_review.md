# Literature Review: Predicting Cascading Failure in Inverter-Dominated Power Systems — The 28 April 2025 Iberian Blackout

## 1. Domain Fundamentals: Power System Stability Theory

Power system stability is "the ability of an electric power system, for a given initial operating condition, to regain a state of operating equilibrium after being subjected to a physical disturbance" (Kundur et al. 2004, P067). The IEEE/CIGRE Joint Task Force classifies stability into three categories: rotor angle stability (the ability of synchronous machines to remain in synchronism), frequency stability (the ability to maintain steady frequency following a severe system upset), and voltage stability (the ability to maintain steady acceptable voltages at all buses). Each category admits further subdivision into small-disturbance and large-disturbance phenomena, and into short-term (0-10 seconds) and long-term (10 seconds to minutes) time frames.

The foundational textbook treatment is Kundur (1994, P001), which develops the electromechanical dynamics of synchronous machines, excitation systems, governors, and their collective behavior during transients. Machowski et al. (2020, P002) update this treatment for modern systems with power electronics, emphasizing that the classical assumptions — large rotating masses providing inertia, predictable fault currents from synchronous generators, and voltage support from field-excited machines — no longer hold when inverter-based resources (IBR) dominate.

The swing equation governing synchronous machine rotor dynamics is:

    2H/omega_s * d^2(delta)/dt^2 = P_m - P_e - D * d(delta)/dt

where H is the inertia constant (typically 2-9 seconds for conventional generators), delta is the rotor angle, P_m is mechanical power, P_e is electrical power, D is the damping coefficient, and omega_s is synchronous speed. When a disturbance reduces electrical power (e.g., a line trip reducing transfer capacity), the machine accelerates; when generation is lost, the system decelerates. The Rate of Change of Frequency (RoCoF) immediately after a disturbance is inversely proportional to system inertia:

    RoCoF = -Delta_P / (2 * H_sys)

where H_sys is the system-wide inertia constant and Delta_P is the power imbalance. This relationship is central to the Iberian blackout analysis: as synchronous generation is displaced by inverter-based renewables that provide no inherent rotational inertia, the same power imbalance produces a larger RoCoF, leaving less time for primary frequency response to arrest the decline.

The frequency nadir — the minimum frequency reached after a disturbance — depends on both the inertia (which determines the initial RoCoF) and the primary frequency response (which determines how quickly generation ramps up to restore balance). Egido et al. (2009, P145) derive analytical approximations for the nadir as a function of system parameters. For the Continental European synchronous area, the ENTSO-E operational handbook (P104) specifies a maximum instantaneous frequency deviation of 800 mHz (i.e., nadir no lower than 49.2 Hz) before automatic under-frequency load shedding (UFLS) activates, and a design standard that the frequency should not fall below 49.0 Hz for any single credible contingency.

Voltage stability, the other critical axis, concerns the ability to maintain bus voltages within acceptable limits (typically 0.95-1.05 p.u.) under all operating conditions. Voltage collapse — an uncontrollable progressive decline in bus voltages leading to blackout — occurs when load demand exceeds the reactive power delivery capability of the network. Van Cutsem and Vournas (1998, P041) provide the canonical treatment, distinguishing between "long-term" voltage instability driven by on-load tap changers (OLTCs) restoring load beyond the network's capability, and "short-term" voltage instability driven by motor loads or HVDC converters. The ENTSO-E final report on the Iberian blackout (P025) identifies voltage instability in the southern Spanish grid as a key propagation mechanism after the initial frequency disturbance.

## 2. The 28 April 2025 Iberian Blackout: Event Sequence and Root Causes

On 28 April 2025 at approximately 12:33 Central European Time (CET), a cascading failure disconnected the Iberian Peninsula (Spain and Portugal) from the rest of the Continental European synchronous area, causing a near-total blackout affecting approximately 56 million people. The ENTSO-E Expert Panel Final Report (P025, March 2026) provides the canonical 440-page investigation.

The pre-event operating condition was characterized by high renewable penetration: approximately 70% of instantaneous generation in Spain was from wind and solar photovoltaic (PV) sources, with correspondingly low synchronous generation online. The Spain-France interconnection was exporting approximately 1.5 GW from France to Spain. Weather conditions were favorable for renewables — high wind speeds in northwestern Spain and strong solar irradiance across southern Spain.

The cascade sequence, as reconstructed by the Expert Panel, proceeded through several phases:

**Phase 1 (12:33:00-12:33:05 CET): Initiating event.** A loss of generation event in southwestern Spain (the specific trigger remains disputed in the report due to incomplete oscillographic data) created a sudden power deficit of approximately 1.2 GW.

**Phase 2 (12:33:05-12:33:15 CET): Frequency decline and oscillation onset.** The low system inertia (estimated at H_sys approximately 2.5 seconds, compared to a historical norm of 4-6 seconds) meant the RoCoF reached approximately -0.8 Hz/s, far exceeding the 0.5 Hz/s threshold at which many protection relays and IBR controllers are designed to operate. Simultaneously, inter-area oscillations between Spain and France amplified, reaching amplitudes that triggered line protection.

**Phase 3 (12:33:15-12:33:45 CET): Cascading line trips and system separation.** The Spain-France interconnectors tripped on distance-relay protection (impedance circles entered due to power swings), separating the Iberian system from Continental Europe. With the interconnection lost, the power deficit in Iberia increased to approximately 2.7 GW (the French import was lost).

**Phase 4 (12:33:45-12:34:30 CET): IBR disconnection and voltage collapse.** Grid-following inverters, which require a stable grid voltage and frequency to operate, began disconnecting as frequency fell below 47.5 Hz and voltage sagged below 0.85 p.u. at multiple buses. Each IBR disconnection increased the power deficit and further reduced voltage support, creating a positive feedback loop. The ENTSO-E report estimates that 15 GW of IBR generation disconnected within 60 seconds.

**Phase 5 (12:34:30-12:40:00 CET): Total system collapse.** Under-frequency load shedding activated but could not arrest the decline because the rate of generation loss (from IBR disconnection) exceeded the rate of load shedding. The system fragmented into multiple islands, most of which collapsed to blackout. Restoration took approximately 16 hours for full load recovery.

The ENTSO-E Expert Panel (P025) identified five systemic failures: (1) insufficient operational awareness of low-inertia conditions, (2) inadequate reactive power management during high-SNSP operation, (3) IBR fault-ride-through settings that were compliant with grid codes but collectively created a "cliff edge" where mass disconnection occurred near-simultaneously, (4) inter-area oscillation damping was insufficient, and (5) protection relay settings designed for synchronous-machine-dominated grids misoperated during the power swing. Critically, the report stated that "the investigation was hampered by incomplete data" from IBR sites, many of which did not have oscillographic recording or did not share their data.

Thlon and Brozek (2025, P024) provide the first independent academic analysis, focusing specifically on the frequency stability aspect and calculating that the System Non-Synchronous Penetration (SNSP) at the time of the event was approximately 78%, well above the 65% operational limit recommended by EirGrid/SONI for the Irish system (P027).

## 3. Candidate Features and Design Variables for Cascade Prediction

The core prediction task is: given a snapshot of grid-state features at time t, predict whether the grid is "one perturbation away from cascade" — operationally, whether the next hour will see a frequency excursion exceeding 200 mHz from nominal (50 Hz).

**System Non-Synchronous Penetration (SNSP).** Defined as (wind + solar + HVDC import) / (total generation + HVDC import) by EirGrid/SONI (P027). This is the single most frequently cited risk indicator in the literature. The Irish system operator has operationally demonstrated that SNSP above 75% creates unacceptable frequency stability risk unless mitigating measures (synchronous condensers, grid-forming inverters, fast frequency response from batteries) are in place. For Spain on 28 April 2025, SNSP was approximately 78%.

**System inertia proxy.** True system inertia requires knowledge of all online synchronous generators and their individual H constants. A proxy can be constructed from ENTSO-E generation data: inertia_proxy = sum over fuel types of (P_fuel * H_fuel), where H_fuel is a typical inertia constant for that fuel type (nuclear: 6s, coal: 5s, gas: 4s, hydro: 3.5s). This proxy was used by Ashton et al. (2015, P069) to estimate GB system inertia from generation mix data alone.

**Interconnector flow direction and magnitude.** The Spain-France interconnection has a Net Transfer Capacity (NTC) of approximately 2.8 GW France-to-Spain and 2.8 GW Spain-to-France (ENTSO-E TYNDP 2024, P138). The direction and magnitude of flow affect both the available inertia support from Continental Europe and the size of the power deficit if the interconnection trips.

**Generation ramp rates.** Large, rapid changes in renewable generation output (due to cloud cover changes or wind variability) stress the system's frequency response capability. Features: max 15-minute ramp in wind generation, max 15-minute ramp in solar generation, and total net ramp.

**Frequency statistics.** Mean frequency, standard deviation, RoCoF over the preceding hour. Elevated frequency variability is an early warning of reduced system strength (Schafer et al. 2018, P082).

**Reactive power balance.** The ratio of reactive power generation to reactive power demand, aggregated from ENTSO-E data where available. Low Q margins precede voltage instability (Modarresi et al. 2016, P012).

**Time-of-day and season interactions.** Solar generation creates a characteristic daily pattern; wind has seasonal and diurnal patterns. The "duck curve" (midday solar surplus followed by evening ramp) creates systematic stress patterns.

**Demand level.** Absolute demand and demand as fraction of installed capacity. Higher demand reduces the margin for generation loss.

**Cross-border flow reversal indicators.** A binary feature indicating whether the Spain-France flow direction has reversed within the past 6 hours, which indicates market-driven dispatch changes that may not be optimized for reliability.

**Lagged features.** The grid state 1, 6, and 24 hours ago. Persistence and trend features capture whether the system is moving toward or away from stress.

**Generation diversity index.** Shannon entropy over generation fuel types. Low diversity (dominated by one or two fuel types, typically wind and solar) indicates vulnerability to correlated weather events.

## 4. Machine Learning for Power System Stability Assessment

Zhang et al. (2021, P046) provide a comprehensive review of ML methods applied to power system stability, covering both static security assessment (is the current state N-1 secure?) and dynamic security assessment (will the system survive a given contingency?). The review identifies a gap: most ML approaches use detailed simulation data (power flows, bus voltages, generator states) rather than the coarser publicly available data from transparency platforms.

Kruse et al. (2021, P048) demonstrate that power system frequency can be predicted from publicly available generation and load data using gradient-boosted trees. Their approach uses 15-minute ENTSO-E data for Germany and achieves useful prediction skill out to 1 hour ahead. This is the closest methodological precedent to our approach, though they predict continuous frequency rather than a binary excursion indicator.

Podolsky et al. (2021, P050) demonstrate that critical slowing down — a universal early warning signal from complex systems theory (Scheffer et al. 2009, P093; 2012, P092) — can detect approaching instability in power grids from frequency time series alone. They find that increased autocorrelation and variance in frequency measurements precede major disturbances by minutes to hours. This motivates our inclusion of lagged frequency statistics as features.

Duchesne et al. (2020, P049) apply deep learning to dynamic security assessment using post-contingency trajectories from time-domain simulations, achieving high accuracy. However, their approach requires detailed network models and dynamic simulations, which are not available for our publicly-data-only approach. Bhatt et al. (2021, P163) apply ML specifically to cascade prediction, using graph neural networks on the network topology. Again, the data requirements exceed what is publicly available.

The methodological gap our work addresses: can publicly available 15-minute ENTSO-E data — generation by fuel type, load, cross-border flows, and day-ahead prices — provide sufficient signal to predict frequency excursion events, without access to detailed network models, bus-level measurements, or proprietary operator data?

## 5. Cascading Failure Theory and Mechanisms

Cascading failures in power systems are fundamentally different from cascading failures in other networked systems because of the physics: power flow obeys Kirchhoff's laws, so removing a line does not simply disconnect part of the network — it redistributes flow to all remaining lines, potentially overloading them and triggering further trips. Buldyrev et al. (2010, P010) develop the interdependent network theory in general; Vaiman et al. (2012, P013) survey the power-system-specific mechanisms.

The cascade amplification mechanisms identified in the literature are:

1. **Thermal overload cascade**: A line trips (due to fault, protection, or thermal overload), redistributing its power to parallel paths, which may then exceed their thermal limits and trip. This is the classic "hidden failure" mechanism (Chen et al. 2005, P054).

2. **Voltage cascade**: Reactive power support is lost (generator trip, IBR disconnection), causing voltage depression at nearby buses, which increases current draw from remaining sources, which depresses voltage further (Van Cutsem and Vournas 1998, P041).

3. **Frequency cascade**: Generation loss exceeds primary response capability, frequency falls, UFLS activates, but the declining frequency causes more IBR to disconnect (due to frequency protection settings), amplifying the deficit. This is the mechanism dominant in the Iberian blackout (P025).

4. **Protection cascade**: Power swings during electromechanical transients cause distance relays to perceive a fault where none exists and trip healthy lines. This was the mechanism that separated Spain from France (P025).

5. **Oscillation cascade**: Poorly damped inter-area oscillations grow in amplitude, triggering protection trips. The role of IBR in either damping or amplifying oscillations depends on controller tuning (Hatziargyriou et al. 2020, P149).

Dobson et al. (2005, P055) model cascading blackouts as branching processes and find that large blackouts follow a power-law distribution — consistent with self-organized criticality (Carreras et al. 2002, P153). This means that the system naturally evolves toward a state where small perturbations can trigger arbitrarily large cascades, and attempts to prevent small outages by operating closer to limits paradoxically increase the probability of large blackouts. This theoretical insight explains why the Iberian blackout was simultaneously unpredicted and, in hindsight, foreseeable: the system was operating in a regime where self-organized criticality made large cascades possible.

## 6. Historical Blackout Case Studies and Cross-Domain Insights

**2003 Italy blackout (P018, P019, P162)**: On 28 September 2003, a tree flashover in Switzerland triggered a cascade that disconnected Italy from the European grid, causing a nationwide blackout affecting 56 million people. The key mechanism was thermal overload cascade amplified by a 30-minute delay in re-dispatching after the initial line trip. The parallel to 2025 Iberia: both events involved the loss of a critical interconnection followed by system-internal collapse, but the 2003 event occurred in a synchronous-machine-dominated system where inertia was not the limiting factor.

**2003 US-Canada blackout (P020, P130)**: The largest blackout in North American history (55 million people). Root cause: software bugs in the energy management system plus inadequate vegetation management. The cascade propagated through thermal overload. The parallel: inadequate situational awareness, a theme echoed in the ENTSO-E Iberian report's finding of "insufficient operational awareness of low-inertia conditions."

**2006 European frequency split (P021, P060, P085)**: A planned switching operation on the Ems crossing split the Continental European system into three islands. Frequency rose to 51.4 Hz in the western island and fell to 49.0 Hz in the eastern. The event demonstrated that the Continental European system was vulnerable to unplanned separations, and that island frequency depends on the generation-load balance at the moment of separation.

**2016 South Australia blackout (P061)**: The most relevant precedent for the Iberian event. On 28 September 2016, a severe storm caused multiple transmission line faults in a system with approximately 50% wind penetration. Wind turbines disconnected due to a previously unidentified fault-ride-through limitation in their control software (a maximum number of voltage dip ride-through events within a time window). The cascade of wind turbine disconnections caused the interconnector to South Australia to overload and trip, islanding the state. The islanded system then collapsed due to insufficient remaining generation. The AEMO investigation (P061) identified IBR settings — compliant with grid codes but collectively dangerous — as the root cause. This is the direct precursor to the Iberian event, where IBR grid-code compliance similarly created a "cliff edge."

**2019 UK blackout (P022)**: On 9 August 2019, near-simultaneous trips of a gas turbine (Hornsea 1 offshore wind farm) and a steam turbine caused a 1 GW deficit. Frequency fell to 48.8 Hz, triggering UFLS and disconnecting approximately 1 million customers. The Ofgem investigation found that the frequency decline was amplified by distributed solar PV disconnecting due to rate-of-change-of-frequency (RoCoF) protection. This event, though smaller than the Iberian blackout, demonstrated the same mechanism: IBR disconnection amplifying an initial disturbance.

**Critical slowing down as a cross-domain early warning (P091, P092, P093)**: Scheffer et al. (2009) demonstrate that systems approaching a tipping point exhibit increased autocorrelation, increased variance, and slower recovery from perturbations — "critical slowing down." This has been validated in ecosystems, climate, finance, and epileptic seizure prediction. Podolsky et al. (2021, P050) apply it to power grids. Our prediction task is essentially: detect the approach to a tipping point in the Iberian power system from publicly available coarse-grained observables.

## 7. Renewable Integration Challenges and Future Grid Architecture

The fundamental challenge is that the physics of power system stability was developed for, and tested on, systems dominated by synchronous machines. The rotating mass of turbine-generator sets provides inertial response (immediate, physics-based resistance to frequency change), primary frequency response (governor-mediated generation increase within seconds), and voltage support (field-excited synchronous machines provide and absorb reactive power naturally). Inverter-based resources provide none of these inherently — they must be specifically designed and programmed to do so.

Denholm et al. (2021, P033) identify the key operational challenges at 50-100% renewable penetration: declining system strength (measured by short-circuit ratio, SCR), declining inertia, reduced controllability of active and reactive power independently, and increased variability on all time scales from seconds to seasons. The Spanish system in April 2025 was at approximately 70% instantaneous renewable penetration — squarely in the challenging regime they identify.

Grid-forming inverters (Rosso et al. 2021, P008) offer a potential solution: instead of following the grid voltage and frequency (grid-following mode), these inverters establish their own voltage and frequency reference, providing voltage source behavior similar to synchronous machines. Grid-forming inverters can provide synthetic inertia, fault current contribution, and inherent oscillation damping. However, as of April 2025, the vast majority of deployed IBR in Spain were grid-following, and grid codes had not yet mandated grid-forming capability for new installations.

The ENTSO-E Expert Panel report (P025) concludes with recommendations that amount to a fundamental rethinking of grid operation at high SNSP: mandatory grid-forming capability for new IBR, real-time inertia monitoring, dynamic SNSP limits, enhanced protection coordination for low-fault-current conditions, and improved oscillographic data recording at IBR sites. These recommendations implicitly acknowledge that the grid code framework that was in place on 28 April 2025 was insufficient for the penetration level achieved.

Our prediction task sits in this context: can the approach of a critical operating condition — where the system is "one perturbation from cascade" — be detected from publicly available data, providing an early warning that complements the operational measures ENTSO-E recommends?
