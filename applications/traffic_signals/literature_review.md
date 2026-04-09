# Literature Review: Traffic Signal Timing Optimisation via HDR

## Phase 0 Deep Literature Review
**Date:** 2026-04-02
**Scope:** Traffic signal timing optimisation using SUMO simulator and hypothesis-driven research (HDR) with reinforcement learning

---

## Theme 1: Traffic Flow Fundamentals

### 1.1 Fundamental Diagram and Flow Theory

Traffic flow theory is grounded in three fundamental relationships: flow vs. density, speed vs. density, and speed vs. flow. The fundamental diagram of traffic flow relates road traffic flux (vehicles/hour) to traffic density (vehicles/km). At low density, vehicles travel near free-flow speed. As density increases, vehicle interactions intensify (reduced following distance, lane-change friction), and the system approaches maximum sustainable flow -- capacity. Beyond capacity, flow drops as the system enters congestion. The speed-density relationship is linear with negative slope: speed decreases as density rises, crossing the speed axis at free-flow speed and the density axis at jam density.

**Key variables:**
- **Flow (q):** vehicles per unit time (veh/hr)
- **Density (k):** vehicles per unit length (veh/km)
- **Speed (v):** space-mean speed (km/hr)
- **Relationship:** q = k * v

The intersection of free-flow and congested vectors defines the capacity of the roadway -- the maximum number of vehicles passing a point per unit time.

### 1.2 Webster's Optimal Cycle Time Formula

Webster's formula (1958) remains the foundation of traffic signal planning worldwide, used in the Highway Capacity Manual (HCM) and equivalent handbooks globally.

**Formula:** C_o = (1.5L + 5) / (1 - Y)

Where:
- C_o = optimal cycle length (seconds)
- L = total lost time per cycle (sum of start-up and clearance lost times across all phases)
- Y = sum of critical flow ratios (y_i = q_i / s_i, where q_i is demand flow and s_i is saturation flow for the critical lane group in phase i)

**Webster's delay formula:** d = C(1 - g/C)^2 / [2(1 - y)] + x^2 / [2q(1 - x)] - 0.65(C/q^2)^(1/3) * x^(2+5g/C)

**Limitations:**
- Overestimates optimal cycle length when volume-to-capacity ratio exceeds ~0.5
- Assumes uniform arrivals (no platoon effects)
- Designed for isolated intersections only -- does not account for coordination
- Produces unrealistically long cycles under heavy saturation

Modified Webster formulas have been developed to account for fuel consumption and emissions, extending the classical delay-only objective.

### 1.3 Green Wave and Offset Optimisation

A "green wave" is achieved when a vehicle travelling at a design speed along an arterial encounters successive green signals without stopping. Three parameters define signal coordination:

1. **Cycle length:** Must be common across coordinated intersections
2. **Splits:** Green time allocated to each phase within the cycle
3. **Offset:** Time difference between the start of green at successive intersections

The MAXBAND and MULTIBAND models are classical approaches:
- **MAXBAND:** Maximises the bandwidth (duration of green window) along an arterial for a given design speed
- **MULTIBAND:** Extends MAXBAND to allow different bandwidth weights per road section

Modern approaches use fuzzy neural networks to adjust cycle length based on saturation degree and calculate offsets from real-time average speeds. Bidirectional green wave coordination is particularly challenging because optimal offsets for one direction may conflict with the other.

### 1.4 Saturation Flow and Capacity

Saturation flow rate is the maximum rate of flow that can pass through an intersection approach under prevailing conditions, assuming the signal is always green. Typical values range from 1,800-1,900 passenger car units per hour per lane under ideal conditions, with adjustments for lane width, grade, heavy vehicles, turning movements, and pedestrian conflicts.

---

## Theme 2: SUMO Simulator

### 2.1 Overview

SUMO (Simulation of Urban MObility) is an open-source, highly portable, microscopic traffic simulation package. It simulates individual vehicles with car-following models (Krauss, IDM), lane-changing models, and junction logic. SUMO supports:

- Multimodal simulation (cars, trucks, buses, pedestrians, bicycles)
- Dynamic routing and trip assignment
- Traffic signal control with arbitrary phase definitions
- Detector emulation (induction loops, lane-area detectors)
- Emission models (HBEFA, PHEMlight) for CO2, NOx, PM, fuel consumption
- Network import from OpenStreetMap, VISUM, Vissim, and other formats

### 2.2 SUMO for RL Research

SUMO provides a TraCI (Traffic Control Interface) API for real-time interaction with running simulations. This enables:
- Reading vehicle positions, speeds, waiting times, queue lengths
- Setting traffic light phases and durations
- Subscribing to detector values
- Running simulation steps programmatically

**Performance:** SUMO runs in the order of seconds per evaluation for typical intersection scenarios, making it suitable for RL training loops that require millions of episodes.

### 2.3 SUMO-RL

SUMO-RL (by Lucas Alegre) wraps SUMO with Gymnasium and PettingZoo interfaces for RL research. Key features:

**Observation space (default):**
```
obs = [phase_one_hot, min_green, lane_1_density, ..., lane_n_density, lane_1_queue, ..., lane_n_queue]
```
- phase_one_hot: one-hot vector of current green phase
- min_green: binary flag indicating if minimum green time has been served
- lane_density: normalised number of vehicles per lane
- lane_queue: normalised number of halting vehicles per lane

**Action space:** Discrete -- each action selects the next green phase. Actions are evaluated every `delta_time` seconds (default 5s).

**Default reward:** `diff-waiting-time` -- the change in cumulative vehicle delay between consecutive time steps. Additional built-in rewards include queue length, pressure, and average speed.

**Built-in reward functions:**
- `diff-waiting-time`: change in total waiting time (default)
- `average-speed`: average speed of approaching vehicles
- `queue`: negative of total queue length
- `pressure`: difference between incoming and outgoing vehicle counts

**Customisation:** Users can define custom observation functions (inheriting from ObservationFunction) and reward functions.

**Network benchmarks:** The `nets/RESCO` folder contains networks from the RESCO benchmark (Reinforcement Learning Benchmarks for Traffic Signal Control), providing standardised evaluation scenarios.

### 2.4 RESCO Benchmark

RESCO provides:
- Real-world intersection layouts from Ingolstadt, Cologne, and other cities
- Both single-intersection and multi-intersection (grid, arterial) scenarios
- Baseline controllers: Fixed Time, MaxPressure, MaxWave
- Integration with PFRL library algorithms
- Standardised evaluation metrics: average waiting time, queue length, throughput

Key finding from RESCO: previous RL algorithms were not robust to varying sensing assumptions and non-stylised intersection layouts. A distributed deep-Q learning approach outperformed previously reported state-of-the-art in many cases when more realistic signal layouts and advanced sensing were assumed.

### 2.5 Other Simulators

- **CityFlow:** 20-25x faster than SUMO but less realistic (no lane-changing, pedestrians, or driver imperfection). Suitable for large-scale experiments where speed matters more than fidelity.
- **LibSignal:** Cross-simulator library supporting both SUMO and CityFlow with unified interfaces and fair benchmarking. First library to provide cross-simulator comparisons.
- **LightSim:** Pure-Python simulator running >20,000 steps/s with 19 built-in scenarios. Pip-installable with Gymnasium/PettingZoo interfaces.
- **PyTSC:** Unified platform for multi-agent RL in traffic signal control.

---

## Theme 3: Reinforcement Learning for Traffic Signals

### 3.1 Value-Based Methods (DQN and Variants)

DQN-based approaches dominate the traffic signal control literature:

- **IntelliLight (KDD 2018):** First major RL-based traffic signal controller. Used phase-gated DQN with rich state representation including vehicle positions as images.
- **IDQN (Independent DQN):** Each intersection runs an independent DQN agent. Simple but effective baseline -- often competitive with more complex methods.
- **Dueling DQN:** Separates state value and advantage estimation. Shown to improve stability in traffic signal applications.
- **Double DQN:** Addresses overestimation bias. Standard improvement used across traffic RL.

**DQN strengths for traffic:** Quick adaptation, time-efficient learning, well-suited to discrete action spaces (phase selection).

### 3.2 Policy Gradient Methods (PPO, A2C)

- **PPO:** Generally provides superior performance for multi-objective traffic control. Achieves up to 21% fewer conflicts and 7% lower delays in high-traffic scenarios compared to A2C and DQN. More stable training but longer episodes due to exploratory behaviour.
- **A2C:** Most variable learning curve, sensitive to environmental dynamics. Faster training than PPO but less stable.
- **SAC (Soft Actor-Critic):** Entropy-regularised policy. Shown to reduce average delay per vehicle by approximately one minute and CO2 emissions by more than double in large-scale networks.

### 3.3 Comparative Results

From a KDD 2024 comparative study (DQN vs PPO vs A2C):
- PPO outperformed A2C and DQN overall
- DQN was ideal for scenarios demanding quick adaptation
- PPO displayed reasonable stability with exploratory tendencies
- A2C showed highest variance, reflecting sensitivity to environmental dynamics
- Real-world validation in Hangzhou and Cologne confirmed 10-15% delay reductions and 2.2-6.4% lower emissions versus prior DRL models

### 3.4 Advanced Architectures

- **FRAP:** Phase competition principle -- when two signals conflict, priority goes to the one with larger traffic movement. Uses a network architecture that explicitly models phase competition.
- **PressLight (KDD 2019):** Minimises intersection pressure in reward, improving coordination with neighbours. Demonstrated effective arterial coordination.
- **MPLight:** Integrates pressure metrics into both state and reward. Uses FRAP-based training with phase competition.
- **CoLight:** Graph Attention Networks for junction-level cooperation via deep Q-learning. Can incorporate temporal and spatial influences of neighbouring intersections without explicit indexing.
- **AttendLight (NeurIPS 2020):** Universal attention-based model for any intersection geometry. Yields 46% improvement over FixedTime, 39% over MaxPressure, 34% over SOTL, 16% over DQTSC-M, 9% over FRAP.
- **DynamicLight:** Two-stage dynamic timing with cycle planning.
- **DuaLight:** Leverages both scenario-specific and scenario-shared knowledge.

---

## Theme 4: Reward Engineering

### 4.1 Common Reward Functions

The choice of reward function is critical and can dramatically change learned behaviour. A minor difference in reward weight setting can lead to dramatically different results.

**Single-metric rewards:**
1. **Queue length:** Number of halting vehicles. Simple and effective. Proven equivalent to optimising global travel time for single intersections.
2. **Waiting time:** Cumulative time vehicles spend stopped. Most common due to simplicity.
3. **Average speed:** Mean speed of approaching vehicles. Can encourage throughput.
4. **Pressure:** Difference between upstream and downstream vehicle counts. Proven equivalent to optimising global travel time in multi-intersection scenarios.
5. **Throughput:** Number of vehicles passing through the intersection per time step.

**Multi-metric (composite) rewards:**
- Weighted sum of queue length, waiting time, speed, pressure, etc.
- Challenge: weight tuning is highly sensitive; small changes produce dramatically different policies
- This is a prime target for HDR: systematic exploration of reward component weights

### 4.2 Pressure-Based Rewards

Traffic pressure = inflow - outflow for each lane/approach. Key results:
- Using queue length as reward for single intersections and pressure for multi-intersection scenarios are both equivalent to optimising global travel time
- MaxPressure algorithm greedily selects phases based on pressure difference, achieving near-optimal throughput under moderate demand
- PressLight and MPLight incorporate pressure into both state and reward

### 4.3 Emissions-Aware Rewards

Recent work incorporates environmental objectives:
- CO2 emission reductions of 21-27% achieved through DRL-based signal control
- Composite rewards penalising CO2, queue growth, and delay while rewarding throughput
- SUMO's emission models (HBEFA, PHEMlight) enable computing per-vehicle emissions at each step

### 4.4 Effects Analysis

A systematic PLOS ONE study analysed reward function effects:
- AWT (average waiting time) and AQL (average queue length) metrics dominate reward design
- Constructing clear relationships between signal actions, state effects, and estimated rewards is key
- Queue-based PPO with autoencoder state representation significantly outperformed other formulations

---

## Theme 5: Multi-Intersection Coordination

### 5.1 Independent vs Coordinated Control

- **Independent:** Each intersection optimises locally. Simple but ignores spillback and green wave opportunities.
- **Coordinated:** Intersections communicate or share information. Can learn green waves, prevent spillback, and balance network flow.

### 5.2 Multi-Agent RL Approaches

MARL dominates the multi-intersection literature (>60% of studies from 2015-2025):

- **Independent learners (IL):** Each agent learns independently. Environments appear non-stationary from each agent's perspective.
- **Centralised training, decentralised execution (CTDE):** Agents share information during training but act independently at deployment. Most promising paradigm.
- **Fully centralised:** Single agent controls all intersections. Does not scale.
- **Federated learning:** FLDQN achieved >34.6% reduction in travel time compared to non-cooperative methods through cooperative multi-agent federated RL.

### 5.3 Communication and Coordination Mechanisms

- **Graph Attention Networks (GATs):** CoLight uses GATs for junction-level cooperation, modelling spatial dependencies without explicit indexing
- **LSTM/TCN for temporal:** DynSTGAT combines multi-head graph attention with temporal convolutional networks
- **Hierarchical RL:** Manager-worker framework where managers set regional goals and workers execute intersection-level control. HALO uses Transformer-LSTM encoders for global guidance.
- **Two-layer coordination:** Upper layer manages network-level coordination; lower layer handles intersection-level timing

### 5.4 Scalability Solutions

- **Parameter sharing:** Weight-tied policies that scale zero-shot to any road network (TransferLight)
- **Federated learning:** Distributed training without sharing raw data
- **Graph-based state representation:** GNNs enable flexible representation that generalises across intersection geometries
- **Region partitioning:** Divide large networks into manageable regions with inter-region coordination

---

## Theme 6: Adaptive vs Fixed-Time Control

### 6.1 Control Strategy Taxonomy

1. **Fixed-time (pre-timed):** Operates on fixed schedule. No detection required. Cheapest to deploy. Performance degrades under variable demand.
2. **Actuated:** Uses vehicle detection to extend/skip phases based on demand. Semi-responsive. Cost-effective for moderate traffic volumes.
3. **Adaptive (real-time):** Uses detection data and algorithms to adjust timing parameters continuously. Best performance under high and variable demand.
4. **RL-based:** Data-driven adaptive control that learns policies from interaction. Potential to outperform classical adaptive systems.

### 6.2 Real-World Adaptive Systems

- **SCOOT (Split Cycle Offset Optimisation Technique):** Developed in UK. Optimises split, cycle, and offset incrementally. Mixed reviews from agencies.
- **SCATS (Sydney Coordinated Adaptive Traffic System):** Deployed at 63,000+ intersections in 33 countries, 216+ cities. Heuristic feedback system (not optimisation-based). "Marriage and divorce" logic for automatic subsystem reconfiguration. Agencies generally satisfied.
- **InSync, SynchroGreen, OPAC, RHODES:** Other deployed adaptive systems with varying approaches.

### 6.3 Performance Comparisons

- Adaptive control: 29.89% improvement in average vehicle waiting time vs fixed-time
- Actuated control: 20.63% improvement vs fixed-time
- SCOOT and SCATS deliver similar delays despite different cycle lengths and methods
- RL-based approaches in simulation show 10-15% delay reductions and 2.2-6.4% emission reductions vs prior DRL models
- Adaptive systems excel under saturated and oversaturated conditions

### 6.4 Self-Organising Traffic Lights (SOTL)

SOTL is a decentralised, detection-based heuristic:
- Traffic lights count (vehicles * time_steps) approaching red lights
- When count exceeds threshold, red switches to green
- Reduces average trip waiting times by 50% compared to green wave methods
- Robust to individual signal failure -- performance degrades gracefully
- No centralised control or communication required

---

## Theme 7: Open Challenges and Emerging Directions

### 7.1 Sim-to-Real Gap

The most critical barrier to deployment:
- RL policies trained in simulation suffer significant performance drops in real-world deployment
- Simulations allow flexible action definitions (e.g., phase changes at any time) that real traffic controllers do not support
- Real systems require safety constraints: minimum green times, all-red clearance intervals, pedestrian phases
- Approaches: domain randomisation, sim-to-real transfer learning, co-simulation frameworks with real camera data

### 7.2 Scalability

- Centralised learning faces communication and computing challenges
- Distributed learning struggles to adapt across heterogeneous intersections
- Current solutions: federated learning, hierarchical RL, parameter sharing, graph-based representations
- City-scale deployment (1000+ intersections) remains an open problem

### 7.3 Generalisation and Transfer

- Models trained on one intersection often fail on different geometries or traffic patterns
- **TransferLight:** Zero-shot transfer to any road network using decentralised, weight-tied policies
- **GeneraLight:** Meta-RL with Wasserstein GAN-based traffic flow generation for environment generalisation
- **ModelLight:** Model-based meta-RL for data-efficient adaptation
- **UniTSA:** Traffic state augmentation for handling unseen intersections
- **CROSS:** Mixture-of-experts framework with general feature extraction for cross-scenario generalisation

### 7.4 LLM-Based Traffic Control

Emerging direction (2024-2025):
- **LLMLight (KDD 2025):** Uses LLMs with Chain-of-Thought reasoning for traffic signal decisions. Fine-tuned GPT-4o-mini achieved 83% accuracy with high ROUGE-L scores.
- **Traffic-R1:** Lightweight reinforced LLM (Qwen2.5-3B) with two-stage agentic RL fine-tuning
- **CoLLMLight:** Cooperative LLM agents for network-wide control with asynchronous cooperative decision architecture
- LLMs bring reasoning, explainability, and natural language interaction but face latency and cost challenges

### 7.5 Multi-Modal and Mixed Traffic

- Current research focuses primarily on passenger vehicles
- Emerging challenges: shared mobility, micro-mobility (e-scooters, bikes), autonomous vehicles
- Transit signal priority (TSP) integration
- Pedestrian and cyclist safety considerations
- Mixed autonomy scenarios (human + autonomous vehicles)

### 7.6 Explainability and Safety

- RL policies are black boxes -- traffic engineers need to understand and trust decisions
- Safety guarantees (minimum green, pedestrian protection) must be hard constraints, not soft rewards
- Approaches: attention visualisation, policy distillation, constrained RL

### 7.7 Opportunities for HDR

The HDR framework is uniquely suited to several open problems:
1. **Reward function design:** Systematic exploration of reward component weights and combinations
2. **Observation space engineering:** Which features carry signal for which traffic patterns?
3. **Phase configuration:** How does the number and structure of phases affect performance?
4. **Coordination strategy:** When does coordination help vs hurt?
5. **Network architecture search:** What model capacity is needed for different intersection complexities?
6. **Cycle length vs delta_time:** How does the RL decision frequency interact with traffic dynamics?

---

## References Summary

This review synthesises findings from 100+ papers spanning traffic flow theory (Webster 1958, Greenshields, HCM), SUMO simulator documentation and API, RL architectures (IntelliLight, PressLight, MPLight, CoLight, AttendLight, FRAP), reward engineering studies, multi-agent coordination (federated, hierarchical, graph-based), real-world adaptive systems (SCATS, SCOOT), and emerging directions (LLMs, transfer learning, explainability). Full citation details are in `papers.csv`.
