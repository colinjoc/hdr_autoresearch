# Knowledge Base: Traffic Signal Timing Optimisation

## Established Results and Known Quantities

This document records proven facts, known benchmarks, validated techniques, and documented failures from the literature. HDR should treat these as constraints and baselines, not re-derive them.

---

## 1. Classical Traffic Engineering Results

### 1.1 Webster's Optimal Cycle Length
- **Formula:** C_o = (1.5L + 5) / (1 - Y)
- **Status:** PROVEN for isolated intersections under uniform arrivals
- **Limitation:** Overestimates at V/C > 0.5; produces unrealistically long cycles under heavy saturation
- **Implication for HDR:** Any RL policy should beat Webster on variable/non-uniform demand. Webster is a strong baseline for uniform demand on isolated intersections.
- **Typical values:** 60-120s cycle lengths for urban intersections

### 1.2 Webster's Delay Formula
- **Formula:** d = C(1 - g/C)^2 / [2(1 - y)] + x^2 / [2q(1 - x)] - 0.65(C/q^2)^(1/3) * x^(2+5g/C)
- **Components:** Uniform delay + overflow delay + empirical correction
- **Status:** Still used in HCM worldwide (since 1958)
- **Accuracy:** Good for undersaturated conditions (V/C < 0.85), degrades for oversaturated

### 1.3 Saturation Flow Rate
- **Ideal value:** 1,800-1,900 pcu/hr/lane under ideal conditions
- **Adjustments:** Lane width, grade, heavy vehicles, turning movements, pedestrian conflicts
- **Start-up lost time:** ~2 seconds per phase
- **Clearance lost time:** ~1-2 seconds per phase (yellow + all-red minus used portion)

### 1.4 Fundamental Diagram Relationships
- **q = k * v** (flow = density * speed)
- **Free-flow speed:** Speed at near-zero density
- **Jam density:** Density at zero flow (bumper-to-bumper)
- **Capacity:** Maximum flow, at the inflection point of the fundamental diagram
- **Speed-density:** Linear with negative slope (Greenshields model)

### 1.5 Green Wave Parameters
- **Bandwidth:** Duration of the green window for progression
- **Offset:** Time difference between green starts at successive intersections
- **Design speed:** Vehicle speed for which the green wave is optimised
- **Bidirectional challenge:** Optimal offsets for one direction may conflict with the other
- **Common cycle length:** Required for coordination; all intersections must share the same cycle

---

## 2. SUMO-RL Benchmarks and Defaults

### 2.1 Default Environment Configuration
```python
# sumo-rl defaults
delta_time = 5          # seconds between RL decisions
min_green = 5           # minimum green time (seconds)
reward_fn = "diff-waiting-time"  # change in cumulative delay
single_agent = True     # single intersection mode
```

### 2.2 Default Observation Space
```
obs = [phase_one_hot, min_green_flag, lane_1_density, ..., lane_n_density, 
       lane_1_queue, ..., lane_n_queue]
```
- phase_one_hot: One-hot encoding of current green phase
- min_green_flag: Binary -- has minimum green been served?
- lane_density: Normalised vehicle count per lane (0-1)
- lane_queue: Normalised halting vehicle count per lane (0-1)

### 2.3 Built-in Reward Functions
| Reward | Formula | Best for |
|--------|---------|----------|
| `diff-waiting-time` | -(total_wait_t - total_wait_{t-1}) | Default, general use |
| `queue` | -sum(queue_lengths) | Single intersection optimisation |
| `pressure` | sum(incoming) - sum(outgoing) per movement | Multi-intersection coordination |
| `average-speed` | mean(vehicle_speeds) | Throughput focus |

### 2.4 Action Space
- Discrete: Each action selects the next green phase
- Actions evaluated every `delta_time` seconds
- Phase transitions include automatic yellow and all-red intervals

### 2.5 Available Network Scenarios (RESCO)
| Scenario | Intersections | Type | Source |
|----------|--------------|------|--------|
| Single intersection | 1 | Synthetic | sumo-rl |
| 2x1 grid | 2 | Synthetic | sumo-rl |
| 2x2 grid | 4 | Synthetic | sumo-rl |
| 4x4 grid | 16 | Synthetic | sumo-rl |
| Ingolstadt (real) | 21 | Real-world | RESCO |
| Cologne (real) | 8 | Real-world | RESCO |

### 2.6 RESCO Baseline Results
- **Fixed Time:** Pre-computed signal plans based on demand estimates
- **MaxPressure:** Greedy phase selection based on pressure; near-optimal throughput under moderate demand
- **MaxWave:** Variant considering wave/platoon effects
- **Key finding:** Previous RL algorithms were NOT robust to varying sensing assumptions and non-stylised intersection layouts

---

## 3. RL Algorithm Performance (Established)

### 3.1 Algorithm Rankings (from comparative studies)
| Algorithm | Strengths | Weaknesses | Best for |
|-----------|-----------|------------|----------|
| DQN | Fast convergence, sample efficient | Overestimation bias, discrete actions only | Quick adaptation, small action spaces |
| DDQN | Reduces overestimation | Slightly slower | Improved stability over DQN |
| Dueling DQN | Better state value estimation | More parameters | Moderate improvement over DQN |
| PPO | Stable, handles multi-objective well | Slower, more exploratory | Complex scenarios, multi-objective |
| A2C | Fast training | Most variable, sensitive to dynamics | Simple scenarios, fast iteration |
| SAC | Entropy regularisation, continuous actions | Complex, computationally heavy | Continuous action spaces |

### 3.2 Validated Performance Numbers
- **PPO vs fixed-time:** Up to 21% fewer conflicts, 7% lower delays (high traffic)
- **DRL vs fixed-time:** 10-15% delay reduction, 2.2-6.4% emission reduction (real-world validation in Hangzhou, Cologne)
- **SAC large-scale:** ~1 minute reduction in average delay per vehicle, >50% CO2 reduction, 56% fuel reduction
- **Adaptive vs fixed-time:** 29.89% improvement in average waiting time
- **Actuated vs fixed-time:** 20.63% improvement in average waiting time
- **SOTL vs green wave:** 50% reduction in average trip waiting time
- **AttendLight vs baselines:** 46% over FixedTime, 39% over MaxPressure, 34% over SOTL, 9% over FRAP

### 3.3 Known Architecture Results
| Architecture | Key innovation | Reported improvement |
|-------------|----------------|---------------------|
| IntelliLight | Phase-gated DQN, image state | First major RL-TSC |
| PressLight | Pressure reward + arterial coordination | Effective multi-intersection |
| MPLight | Pressure in state + reward, FRAP architecture | Combined state+reward pressure |
| CoLight | Graph Attention Networks for cooperation | Neighbour-aware coordination |
| AttendLight | Universal attention, any geometry | 46% over FixedTime |
| FRAP | Phase competition principle | Phase-aware learning |
| DynamicLight | Two-stage cycle + phase | Structured timing |

---

## 4. Reward Function Results (Established)

### 4.1 Proven Equivalences
- **Queue length as reward (single intersection) is equivalent to optimising global travel time** (proven theoretically)
- **Pressure as reward (multi-intersection) is equivalent to optimising global travel time** (proven theoretically)
- These equivalences hold under standard assumptions (no spillback, moderate demand)

### 4.2 Known Failures
- **Throughput-only reward:** Encourages letting vehicles through regardless of delay to remaining vehicles; can cause starvation of minor approaches
- **Pure speed reward:** Agents learn to keep intersections empty (zero queue = high speed) rather than maximising throughput
- **Delay without differential:** Cumulative delay grows monotonically; agent cannot distinguish improving from deteriorating situations without the differential
- **Over-weighted emissions:** Adding emissions penalty >0.3 weight significantly degrades delay performance; marginal emission gains do not justify delay cost

### 4.3 Reward Weight Sensitivity
- Minor differences in multi-objective reward weights lead to dramatically different policies
- No universal weighting works across all scenarios
- This is explicitly an HDR-suitable problem: systematic exploration of weight space

### 4.4 Emission Reduction Benchmarks
- DRL-based signal control achieves 21-27% CO2 reduction vs fixed-time
- Requires SUMO emission model (HBEFA or PHEMlight)
- Speed harmonisation + signal control combined can exceed 30% reduction

---

## 5. Multi-Intersection Coordination Results

### 5.1 MaxPressure Algorithm
- **How it works:** At each decision point, select the phase that maximises the pressure (difference between upstream and downstream queue counts)
- **Proven:** Achieves near-optimal throughput under moderate demand (theoretical guarantee from queueing theory)
- **Limitation:** Greedy; does not plan ahead; degrades under very high demand and spillback
- **Status:** Strong baseline that is difficult to significantly outperform on standard scenarios

### 5.2 MARL Dominance
- >60% of traffic signal control studies from 2015-2025 use MARL
- Independent DQN (IDQN) is surprisingly competitive and a strong baseline
- CTDE (centralised training, decentralised execution) is the most promising paradigm
- Fully centralised does not scale beyond ~4-5 intersections

### 5.3 Communication Overhead
- Graph attention (CoLight-style) adds moderate overhead but significant coordination benefit
- Message passing adds minimal overhead but limited coordination ability
- 1-hop neighbourhood information captures most of the coordination benefit
- Beyond 2 hops, diminishing returns dominate

### 5.4 Federated Learning for Traffic
- FLDQN: >34.6% travel time reduction vs non-cooperative methods
- Enables distributed training without sharing raw data
- Suitable for privacy-preserving multi-agency deployments

---

## 6. Real-World Deployment Constraints

### 6.1 Safety Requirements (Non-Negotiable)
- Minimum green time: 5-15 seconds depending on jurisdiction
- Yellow interval: 3-5 seconds (ITE formula based on speed)
- All-red clearance: 1-3 seconds based on intersection width and speed
- Pedestrian phase: 7-30 seconds (MUTCD walk + flashing don't walk)
- Maximum cycle length: Typically 150-180 seconds (driver expectation)

### 6.2 Sim-to-Real Gap Issues
- Simulation allows phase changes at any time; real controllers have fixed minimum intervals
- SUMO uses idealised car-following; real drivers have higher variance
- Detector noise, communication latency, and failure modes absent from simulation
- RL policies trained in simulation suffer "significant performance drops" in real deployment

### 6.3 Deployed System Performance
- **SCATS:** 63,000+ intersections, 33 countries. Heuristic feedback (not optimisation). Generally well-regarded.
- **SCOOT:** UK-developed. Split/cycle/offset optimisation. Mixed reviews; some agencies removed it.
- **Both deliver similar delays** despite fundamentally different approaches
- Agencies with SCATS would use it again; SCOOT received mixed reviews

### 6.4 Deployment Readiness Checklist
1. Minimum green, yellow, all-red intervals enforced as hard constraints
2. Cycle length within agency-acceptable range (60-150s typically)
3. Phase sequence compatible with NEMA standards
4. Graceful degradation to fixed-time plan on failure
5. Latency < 100ms for decision computation
6. Interpretable decisions (attention maps, phase justification)

---

## 7. Open Questions (Not Yet Resolved)

### 7.1 Reward Design
- No universal reward weighting across scenarios
- Optimal reward changes with demand level, network topology, and objective priorities
- HDR is well-suited to systematically explore this space

### 7.2 Generalisation
- Policies trained on one intersection typically fail on different geometries
- TransferLight, GeneraLight, UniTSA show promise but not yet validated at scale
- Zero-shot transfer remains unreliable for heterogeneous networks

### 7.3 Scalability
- City-scale (1000+ intersections) RL control is unsolved
- Hierarchical approaches (HALO, federated hierarchical) are most promising
- Computational cost of training scales poorly with network size

### 7.4 Mixed Traffic
- Autonomous vehicles, e-scooters, bicycles, transit priority
- Most studies consider only passenger vehicles
- Multi-modal coordination is largely unexplored

### 7.5 LLM Integration
- LLMLight, Traffic-R1, CoLLMLight show reasoning capability
- Latency and cost make real-time deployment challenging
- Potential for explainability and human-in-the-loop operation
- Very early stage; unclear if reasoning adds value over well-tuned RL

---

## 8. Recommended Baselines for HDR Evaluation

Every HDR experiment should compare against these baselines:

| Baseline | Type | What it tests |
|----------|------|---------------|
| Webster optimal timing | Classical | Can RL beat the 1958 gold standard? |
| Fixed-time (uniform split) | Classical | Can RL beat naive timing? |
| MaxPressure | Heuristic | Can RL beat the theoretically-grounded greedy? |
| SOTL | Self-organising | Can RL beat adaptive heuristic? |
| Random | Lower bound | Sanity check |
| IDQN (diff-waiting-time) | RL baseline | Standard RL comparison point |
| Actuated control | Semi-adaptive | Practical deployment comparison |

**Important:** MaxPressure is a surprisingly strong baseline that is difficult to significantly outperform. Any claimed RL improvement should be validated against MaxPressure, not just fixed-time.

---

## 9. Tool and Library Versions

| Tool | Version | Notes |
|------|---------|-------|
| SUMO | 1.18+ | Use latest stable release |
| sumo-rl | 1.4.5 | PyPI package |
| Gymnasium | 0.29+ | Environment API |
| PettingZoo | 1.24+ | Multi-agent API |
| Stable-Baselines3 | 2.0+ | DQN, PPO, A2C, SAC |
| RLlib | 2.7+ | Scalable MARL |
| PyTorch | 2.0+ | Neural network backend |

---

## 10. Key Metrics and Their Definitions

| Metric | Definition | Units | Computed from |
|--------|------------|-------|---------------|
| AWT | Average waiting time across all vehicles | seconds | SUMO vehicle waiting time |
| AQL | Average queue length across all approaches | vehicles | SUMO lane queue count |
| Throughput | Vehicles completing trip per hour | veh/hr | SUMO trip completions |
| CO2 | Total CO2 emissions | g | SUMO emission model |
| Fuel | Total fuel consumption | mL | SUMO emission model |
| Pressure | Sum of |incoming - outgoing| per phase | vehicles | SUMO lane vehicle counts |
| Travel time | Average trip duration | seconds | SUMO trip statistics |
| Stops | Average number of stops per vehicle | count | SUMO vehicle stops |
| Green wave bandwidth | Duration of uninterrupted green progression | seconds | Time-space diagram analysis |

---

## 11. HDR Discoveries (Single Intersection, Phase 1 – SUMO validation)

These findings are from the HDR loop documented in `experiment_log.md`
(20 experiments on the lightweight toy simulator, then 18 redo experiments
on SUMO + sumo-rl). The lightweight toy sim encoded Webster's analytical
model (Poisson + saturation flow), so beating Webster on it was largely
tautological. The SUMO redo is the honest validation.
Primary metric: mean AWT delta vs Webster across 7 SUMO scenarios × 2 seeds.

### 11.1 SOTL beats Webster by 42.67% without any RL training
- **Final controller:** 2 parameters (CLEAR_THRESHOLD=0, WAITING_THRESHOLD=2)
- **Rule:** Yield current green when `green_phase_queue == 0 AND red_phase_queue >= 2`
- **Per-scenario delta:**
  - uniform_low -33.82%, uniform_med -42.02%, uniform_high -32.25%
  - asymmetric -41.32%, peak_hour -63.93%
- **Variance reduction:** Robustness std 2.41 → 0.62 (4× reduction)
- **Lesson:** Deterministic self-organising rules reach adaptive-control
  benchmark literature range (29-46%) with < 20 lines of Python.

### 11.2 Drain-first-then-yield dominates partial-drain strategies
- CLEAR_THRESHOLD=0 (full drain) beats CLEAR_THRESHOLD=1 by ~7 pp mean delta.
- A single residual vehicle on a yielded approach costs the full cycle of wait.

### 11.3 Occam's razor applies to signal control rules
Every added complexity lost to the 2-parameter rule:
- Cumulative-wait override (E07): no benefit
- Anticipatory rate branch (E08, E17): worse at low demand
- Transition-aware prediction (E16): hurts high demand
- Demand-scaled thresholds (E20): constant wait=2 wins
- Asymmetric major/minor thresholds (E19): symmetric rule handles imbalance
- Starvation guards (E09): premature switches hurt high-demand
- Soft max-green caps (E10): hurts productive greens
- Min-burst rules (E18): breaks low-demand efficiency

### 11.4 Reactive controllers require phase commitment
- Pure queue-greedy (E01) is **4.86× worse** than Webster because it flips
  at every equal-queue tie, wasting ~33% of clock time on transitions.
- Phase commitment primitive options (ranked):
  1. Drain-based: yield only when green queue == 0 (**BEST** — self-scaling)
  2. Hysteresis (fixed margin): works at low demand, fails at high (E02)
  3. Max-green cap: hurts productive greens (E10)

### 11.5 Peak-hour scenarios reward adaptive control the most
- Webster fixed-time achieves 43.81s AWT on sinusoidal demand.
- SOTL achieves 15.80s (-63.93%). Webster is tuned at t=0 and cannot adapt
  as demand rises past its design point.

### 11.6 Asymmetric demand is solved "for free" by drain-first SOTL
- Hand-designed asymmetric thresholds (E19) performed WORSE than the symmetric
  SOTL rule (-42.23% vs -42.67% mean).
- Mechanism: under asymmetry, the minor phase drains faster (it has a shorter
  queue), so the drain-first rule naturally yields it sooner.

### 11.7 The 1-Hz decision loop requires explicit phase commitment
- E01 demonstrates that returning the greedy best phase every step, with
  min-green enforcement, is NOT sufficient for stability.
- The controller must either (a) maintain an internal phase commitment, or
  (b) use a selection rule that produces stable choices.
- SOTL's drain-rule does (b): as long as the green phase has queue, the
  controller returns the current phase, even if the red competitor is
  growing — this gives the green "control inertia" without an explicit timer.

### 11.8 Simple simulator validation
- A 100-line Poisson+saturation-flow simulator was sufficient to reach the
  literature-reported adaptive-vs-fixed-time gain range. This confirms
  Webster's formula + queue dynamics (knowledge base §1) are enough for
  rapid HDR iteration on single-intersection hypotheses.
- Simulator speed: ~0.3s per episode → 5 scenarios × 3 seeds + 10 robustness
  seeds runs in < 1.5s.
- **CAVEAT:** the lightweight simulator IS Webster's analytical model.
  Beating Webster on it therefore has near-zero information content.
  The SUMO validation below is the meaningful result.

---

## 12. SUMO validation of the lightweight findings (April 2026)

The HDR loop was re-run from scratch on SUMO 1.18 + sumo-rl 1.4.5 using the
standard 2way-single-intersection network. **The top-level finding transfers
with the same magnitude, but parameter tuning and several dynamics differ.**

### 12.1 Headline result
- **Plain SOTL port** (E12 rule: `clear=0, wait=2`) beats SUMO Webster by
  `-46.05 %` mean across 7 scenarios (toy sim: `-42.67 %`). The drain-first
  SOTL rule IS robust across simulators.
- **Tuned final rule** (S16 `clear=0, wait=1, preempt_ratio=2, floor=4`)
  beats SUMO Webster by `-49.10 %` mean (3 seeds). Robustness on
  uniform_med: `-55.42 %` with 5 seeds.

### 12.2 What DOES NOT transfer from toy sim to SUMO
- **Optimal `WAITING_THRESHOLD` differs**: toy sim wanted `2`, SUMO wants `1`.
  Toy sim `wait=3` was "slightly worse"; SUMO `wait=3` is CATASTROPHIC on
  uniform_low (+219 %). The toy sim's long yellow (4 s vs SUMO's 2 s) made
  eager switching more expensive in the toy model.
- **Peak-hour gain is overstated by the toy sim**: toy peak_hour `-63.93 %`
  vs SUMO vhvh `-47.57 %`. The toy used a smooth sinusoid that Webster
  (tuned at t=0) could not track; SUMO's vhvh uses step-function intervals
  that the Webster plan handles better.
- **Uniform-low gain is overstated by the toy sim**: toy `-33.82 %` vs
  SUMO `-18.10 %`. On realistic microscopic dynamics with start-up lost
  time and 4-phase protected-left logic, Webster is closer to optimal at
  low demand than the toy sim suggested.

### 12.3 NEW findings unique to SUMO
- **Preemption is a meaningful control primitive.** When a single phase is
  heavily loaded, the plain drain-first rule can under-serve other phases.
  A rule that switches early when `best_other_q >= 2 * current_q AND
  best_other_q >= 4` adds `+3 pp` of mean gain (S16 vs S03), almost entirely
  from the sumo-rl horizontal/vertical/vhvh scenarios. This was never
  visible on the toy sim because the toy-sim 2-phase structure decorrelated
  the phases.
- **Pressure ≡ Queue on an isolated intersection (empirical).** Implementing
  the standard MaxPressure rule on the 2way-single-intersection net reproduces
  the plain queue-based rule EXACTLY (same AWT to the 4th decimal). This is
  because the net's outbound edges are dead-end sinks with zero downstream
  queue, so pressure = in_queue - 0 = queue. The equivalence theorem from
  literature (§4.1) held empirically.
- **`CLEAR_THRESHOLD = 1` is tied with `CLEAR_THRESHOLD = 0`** on SUMO
  (-46.78 % vs -46.72 %, within noise). On the toy sim `CLEAR=0`
  strictly dominated by 7 pp. Reason: the toy sim's discrete queue made
  "residual 1 vehicle" a large fraction of typical queue; SUMO's multi-lane
  layout dilutes the effect because only one of several lanes might have
  that residual vehicle.

### 12.4 The final SUMO controller (S16)

```python
class Controller:
    name = "S16_preempt2x"
    CLEAR_THRESHOLD = 0
    WAITING_THRESHOLD = 1
    PREEMPT_RATIO = 2.0
    PREEMPT_FLOOR = 4

    def act(self, obs):
        cur = obs["current_phase"]
        phase_queue = obs["phase_lane_mask"] @ obs["lane_queue_count"]
        green_q = phase_queue[cur]
        others = [(p, phase_queue[p]) for p in range(obs["num_green_phases"]) if p != cur]
        best_p, best_q = max(others, key=lambda t: t[1])
        if best_q >= self.PREEMPT_RATIO * max(green_q, 1) and best_q >= self.PREEMPT_FLOOR:
            return best_p
        if green_q <= self.CLEAR_THRESHOLD and best_q >= self.WAITING_THRESHOLD:
            return best_p
        return cur
```

Four hyper-parameters, all motivated by experiments:
1. `CLEAR_THRESHOLD = 0`: drain before yielding. (Confirmed from toy sim.)
2. `WAITING_THRESHOLD = 1`: switch as soon as any other phase has demand.
   (TUNED ON SUMO; toy sim wanted 2.)
3. `PREEMPT_RATIO = 2.0`: preempt when heavily outnumbered. (NEW on SUMO.)
4. `PREEMPT_FLOOR = 4`: do not preempt for trivial queues. (NEW on SUMO.)

### 12.5 Lesson for HDR methodology
- Always redo the HDR loop on the standard published simulator (SUMO for
  traffic). Toy simulators written as "fast proxies" can encode assumptions
  that make the experimental question degenerate.
- The top-level discoveries were robust; the hyper-parameter tuning was
  NOT robust and needed to be re-done on the real simulator.
- SUMO ran at ~10 s per episode (vs toy sim 0.3 s), adding ~5 min per
  full benchmark. This is still fast enough for an HDR loop of ~20
  experiments in a half-hour session — SUMO is workable, no toy sim needed.
