# Research Queue: Traffic Signal Timing Optimisation

## Hypothesis-Driven Research Queue
Ordered by expected impact and dependency structure. Each hypothesis specifies the design variable being tested, the expected outcome, the evaluation metric, and the baseline.

---

## Phase 1: Reward Function Exploration (Single Intersection)

### H01: Pressure reward outperforms diff-waiting-time on single intersection under high demand
- **Design variable:** `reward_fn` = {diff-waiting-time, pressure}
- **Scenario:** Single 4-way intersection, high demand, uniform arrivals
- **Expected outcome:** Pressure reward produces 5-10% lower average waiting time under high demand because it directly captures inflow/outflow imbalance
- **Metric:** Average waiting time (AWT), average queue length (AQL), throughput
- **Baseline:** Fixed-time (Webster optimal), SOTL, diff-waiting-time DQN
- **Rationale:** Literature proves pressure is equivalent to optimising global travel time; test if this holds on single intersection too

### H02: Queue-based reward is more sample-efficient than pressure for single intersection
- **Design variable:** `reward_fn` = {queue, pressure}
- **Scenario:** Single intersection, medium demand
- **Expected outcome:** Queue reward converges 30-50% faster (fewer episodes to reach asymptotic performance) because queue provides more direct gradient signal
- **Metric:** Episodes to convergence, AWT at convergence
- **Baseline:** Convergence curves of both reward types
- **Rationale:** Queue is a simpler signal; simpler rewards should have sharper learning gradients

### H03: Composite reward (queue + pressure) outperforms either alone on time-varying demand
- **Design variable:** `w_queue`, `w_pressure` in composite reward
- **Scenario:** Single intersection, peak-hour demand pattern (low -> high -> low)
- **Expected outcome:** Equal weighting (0.5/0.5) captures both local queue clearance and flow balance, yielding 3-7% improvement
- **Metric:** AWT, AQL across full demand cycle
- **Baseline:** Best single-metric reward from H01/H02
- **Rationale:** Time-varying demand requires both immediate responsiveness (queue) and anticipatory balancing (pressure)

### H04: Adding emissions penalty to reward reduces CO2 by >15% with <5% delay increase
- **Design variable:** `w_emissions` = {0.0, 0.1, 0.2, 0.3}
- **Scenario:** Single intersection, medium demand, SUMO emission model enabled
- **Expected outcome:** w_emissions=0.1 reduces CO2 by 15-20% with marginal (<5%) delay increase; higher weights hurt delay too much
- **Metric:** CO2 emissions, fuel consumption, AWT
- **Baseline:** Best reward from H03 without emissions
- **Rationale:** Literature shows 21-27% CO2 reduction is achievable; HDR can find the Pareto-optimal weight

### H05: Reward clipping at [-5, 5] improves training stability without hurting final performance
- **Design variable:** `reward_clip` = {none, [-5,5], [-10,10], [-2,2]}
- **Scenario:** Single intersection, high demand (where rewards have high variance)
- **Expected outcome:** Moderate clipping stabilises learning (lower variance in returns) without degrading AWT
- **Metric:** Training curve variance, final AWT
- **Baseline:** No clipping
- **Rationale:** High-demand scenarios produce extreme reward values that destabilise Q-learning

---

## Phase 2: Observation Space Engineering

### H06: Adding average speed to observation improves performance under oversaturated conditions
- **Design variable:** `obs_avg_speed` = {true, false}
- **Scenario:** Single intersection, oversaturated demand (V/C > 1.0)
- **Expected outcome:** Speed provides early warning of congestion onset before queue lengths spike; 5-8% AWT improvement
- **Metric:** AWT, AQL under oversaturation
- **Baseline:** Default observation (density + queue + phase)
- **Rationale:** Queue saturates as detector range fills; speed degrades more gradually and provides richer signal

### H07: Elapsed phase time in observation enables better min-green compliance
- **Design variable:** `obs_elapsed_phase` = {true, false}
- **Scenario:** Single intersection, medium demand, min_green=7s
- **Expected outcome:** Agent learns to avoid premature phase switches; fewer min-green violations
- **Metric:** Min-green violation rate, AWT
- **Baseline:** Default observation with min_green_flag only
- **Rationale:** The binary min_green_flag only says "served or not"; continuous elapsed time gives the agent richer temporal context

### H08: Frame stacking (history_length=3) improves performance on time-varying demand
- **Design variable:** `obs_history_length` = {1, 3, 5}
- **Scenario:** Single intersection, sinusoidal demand pattern
- **Expected outcome:** 3-frame stacking captures demand trends; 5 adds noise; 1 is insufficient for pattern detection
- **Metric:** AWT across demand cycle, adaptation speed
- **Baseline:** history_length=1
- **Rationale:** Time-varying demand requires temporal context; too much history adds dimensionality without signal

### H09: Removing lane density (keeping only queue) matches full observation performance
- **Design variable:** `obs_lane_density` = {true, false} (with queue always true)
- **Scenario:** Single intersection, medium demand
- **Expected outcome:** Queue alone captures 95%+ of the performance; density adds minimal signal when queue is present
- **Metric:** AWT, AQL, model size
- **Baseline:** Full default observation
- **Rationale:** "Expression is enough" -- literature suggests simple representations suffice

---

## Phase 3: Algorithm and Architecture

### H10: PPO outperforms DQN on multi-phase intersections (6+ phases)
- **Design variable:** `algorithm` = {DQN, PPO}
- **Scenario:** Single 4-way intersection with 6 phases (including left-turn phases)
- **Expected outcome:** PPO handles the larger action space better; 5-10% AWT improvement
- **Metric:** AWT, training stability, convergence speed
- **Baseline:** DQN baseline from Phase 1
- **Rationale:** Literature shows PPO superior for complex action spaces; 6-phase has more combinations

### H11: Dueling DQN outperforms vanilla DQN on single intersection
- **Design variable:** `algorithm` = {DQN, Dueling-DQN, DDQN}
- **Scenario:** Single intersection, medium demand
- **Expected outcome:** Dueling DQN provides 3-5% improvement through better state value estimation
- **Metric:** AWT, training stability
- **Baseline:** Vanilla DQN
- **Rationale:** Dueling architecture separates state value from action advantage; standard improvement

### H12: Smaller networks [64,32] match [256,128] for single intersection but fail for multi-intersection
- **Design variable:** `hidden_layers` = {[64,32], [128,64], [256,128]}
- **Scenario:** Both single intersection and 2x2 grid
- **Expected outcome:** Small network suffices for single; larger needed for multi-intersection coordination
- **Metric:** AWT, model size, inference time
- **Baseline:** [128,64] baseline
- **Rationale:** Single intersection has small state/action space; multi-intersection needs capacity for coordination patterns

---

## Phase 4: Phase Configuration and Timing

### H13: Allowing phase skipping reduces delay under asymmetric demand
- **Design variable:** `skip_phases` = {true, false}
- **Scenario:** Single intersection, heavy N-S demand, light E-W demand
- **Expected outcome:** Skipping low-demand E-W phases reduces AWT by 10-15%
- **Metric:** AWT per approach, overall AWT, throughput
- **Baseline:** Fixed phase sequence without skipping
- **Rationale:** Under asymmetric demand, serving empty phases wastes green time

### H14: delta_time=5s outperforms delta_time=10s and delta_time=3s
- **Design variable:** `delta_time` = {3, 5, 7, 10, 15}
- **Scenario:** Single intersection, medium demand
- **Expected outcome:** 5s balances responsiveness and stability; 3s causes oscillation; 10s is too sluggish
- **Metric:** AWT, phase oscillation rate, training stability
- **Baseline:** delta_time=5s (default)
- **Rationale:** Decision frequency interacts with traffic dynamics; too-frequent decisions chase noise

### H15: Enforcing realistic cycle length (60-120s) improves real-world deployability without hurting performance
- **Design variable:** `cycle_enforcement` = {none, soft, hard}, `target_cycle` = {60, 90, 120}
- **Scenario:** Single intersection, medium demand
- **Expected outcome:** Soft enforcement (penalty for deviation) maintains 95%+ of unconstrained performance while producing deployable timing plans
- **Metric:** AWT, cycle length distribution, deployability score
- **Baseline:** No cycle enforcement
- **Rationale:** Unconstrained RL may produce erratic cycle lengths that traffic engineers reject

---

## Phase 5: Multi-Intersection Coordination

### H16: CTDE with shared reward outperforms independent agents on 2x2 grid
- **Design variable:** `coordination` = {independent, CTDE}, `global_reward_weight` = {0.0, 0.3, 0.5}
- **Scenario:** 2x2 grid network, medium demand
- **Expected outcome:** CTDE with 0.3 global reward weight reduces network AWT by 8-12%
- **Metric:** Network AWT, per-intersection AWT, throughput
- **Baseline:** Independent DQN agents
- **Rationale:** Coordination prevents spillback and enables implicit green wave formation

### H17: Graph attention communication outperforms no-communication on arterial
- **Design variable:** `communication` = {none, graph-attention}
- **Scenario:** 5-intersection arterial network
- **Expected outcome:** Graph attention enables green wave learning; 10-15% AWT reduction
- **Metric:** AWT, green wave quality (bandwidth), throughput
- **Baseline:** Independent agents
- **Rationale:** CoLight demonstrated effective coordination through graph attention; arterials are ideal for green wave

### H18: Pressure reward is superior to queue reward for multi-intersection coordination
- **Design variable:** `reward_fn` = {queue, pressure} crossed with `coordination` = {independent, CTDE}
- **Scenario:** 2x2 grid network, medium-high demand
- **Expected outcome:** Pressure with CTDE achieves lowest network AWT; queue with independent may be competitive for per-intersection
- **Metric:** Network AWT, per-intersection AWT, spillback events
- **Baseline:** Independent + diff-waiting-time
- **Rationale:** Literature proves pressure is equivalent to optimising global travel time in multi-intersection settings

### H19: Neighbour queue observation (1-hop) provides most of the coordination benefit
- **Design variable:** `obs_neighbour_hops` = {0, 1, 2, 3}
- **Scenario:** 4x4 grid network
- **Expected outcome:** 1-hop captures 80%+ of the benefit; 2+ hops add diminishing returns
- **Metric:** Network AWT, communication overhead
- **Baseline:** 0-hop (no neighbour info)
- **Rationale:** Traffic effects are primarily local; distant intersections contribute noise

### H20: Hierarchical RL outperforms flat MARL on large networks (4x4 grid)
- **Design variable:** `coordination` = {CTDE, hierarchical}
- **Scenario:** 4x4 grid network, time-varying demand
- **Expected outcome:** Hierarchical (manager sets regional goals, workers execute) achieves 5-10% better AWT on large network
- **Metric:** Network AWT, regional balance, scalability (time per episode)
- **Baseline:** Flat CTDE from H16 scaled up
- **Rationale:** HALO and other hierarchical methods show benefits at scale; flat MARL struggles with large state spaces

---

## Phase 6: Robustness and Transfer

### H21: Policy trained on medium demand transfers to high demand with <10% performance loss
- **Design variable:** `demand_level` at training vs evaluation
- **Scenario:** Single intersection, train on medium, evaluate on {low, medium, high, oversaturated}
- **Expected outcome:** <10% degradation on high; >20% degradation on oversaturated
- **Metric:** AWT relative to demand-specific optimal
- **Baseline:** Demand-specific trained policies
- **Rationale:** Real-world demand varies; robust policies must handle range without retraining

### H22: Domain randomisation over demand levels improves out-of-distribution robustness
- **Design variable:** Training with randomised vs fixed demand
- **Scenario:** Single intersection, random demand sampling during training
- **Expected outcome:** Randomised training produces a policy that is within 5% of demand-specific optimal across all levels
- **Metric:** AWT across demand levels, worst-case AWT
- **Baseline:** Fixed-demand training from H21
- **Rationale:** Standard domain randomisation technique; should generalise to traffic demand

### H23: Parameter-shared policy transfers zero-shot across RESCO benchmark scenarios
- **Design variable:** `parameter_sharing` = full, trained on subset of RESCO scenarios
- **Scenario:** RESCO Ingolstadt and Cologne benchmarks
- **Expected outcome:** Zero-shot transfer achieves 70%+ of fine-tuned performance
- **Metric:** AWT relative to scenario-specific optimal
- **Baseline:** Scenario-specific trained policies
- **Rationale:** TransferLight demonstrated zero-shot transfer; validate with HDR-tuned policies

### H24: Stochastic demand during training produces more robust policies than deterministic demand
- **Design variable:** `demand_pattern` = {deterministic, stochastic-10%, stochastic-30%}
- **Scenario:** Single intersection, medium demand with noise
- **Expected outcome:** 10% stochastic noise improves robustness with negligible performance loss; 30% may hurt
- **Metric:** AWT mean and variance across 100 evaluation runs
- **Baseline:** Deterministic demand training
- **Rationale:** Real traffic is inherently stochastic; training should reflect this

---

## Bonus Hypotheses (stretch goals)

### H25: Combining RL timing with speed advisory reduces emissions by >30%
- **Design variable:** Joint signal timing + upstream speed guidance
- **Scenario:** Arterial with connected vehicle data
- **Expected outcome:** Combined approach exceeds signal-only emission reduction
- **Metric:** CO2, fuel consumption, AWT
- **Baseline:** Signal-only RL

### H26: Attention-based observation aggregation matches CoLight performance with simpler architecture
- **Design variable:** Attention vs GAT for neighbour aggregation
- **Scenario:** 2x2 grid
- **Expected outcome:** Simple attention matches GAT with fewer parameters
- **Metric:** AWT, model size, inference time
- **Baseline:** CoLight-style GAT

---

## Dependency Graph

```
H01 -> H02 -> H03 -> H04 -> H05  (reward function chain)
H06 -> H07 -> H08 -> H09          (observation space chain)
H10 -> H11 -> H12                  (algorithm/architecture chain)
H13 -> H14 -> H15                  (phase/timing chain)

[H03, H09, H12] -> H16 -> H17 -> H18 -> H19 -> H20  (multi-intersection chain)
[H05, H15] -> H21 -> H22 -> H23 -> H24               (robustness chain)
```

Phase 1-4 hypotheses are independent and can be run in parallel.
Phase 5-6 depend on results from earlier phases.
