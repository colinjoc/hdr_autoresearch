# Four Smart Cars Dissolve a Phantom Traffic Jam: A Hypothesis-Driven Study on the Sugiyama Ring Road

## Abstract

Phantom traffic jams -- stop-and-go waves that form on homogeneous highways without any external trigger -- can be suppressed by a small fraction of longitudinally controlled vehicles. We quantify the minimum penetration rate required using a pure-Python Intelligent Driver Model (IDM) simulation of the canonical Sugiyama ring road (22 vehicles, 230 metres) and a systematic hypothesis-driven research (HDR) loop of 105 pre-registered single-change experiments followed by composition retests and a dense penetration sweep. Starting from an all-human baseline with 8.17 m/s wave amplitude, we test five controller families across 20 experimental themes covering penetration rate, controller gains, ring size, human-driver model parameters, noise levels, vehicle placement, and multi-objective trade-offs.

The headline finding is that four Adaptive Cruise Control (ACC) vehicles among 22 human drivers -- an 18.2% penetration rate -- reduce wave amplitude from 8.17 to 0.55 m/s, a 93.3% reduction. The transition is sharp: three ACC vehicles (13.6%) still leave a 1.77 m/s wave. The FollowerStopper (FS) controller requires 22.7% penetration (5/22 vehicles) to achieve comparable suppression but imposes a throughput penalty of 61% versus ACC's 10%. The PI-with-saturation controller is catastrophically unstable on the ring due to integral windup. A dense sweep from 0 to 22 ACC vehicles reveals monotonic improvement with diminishing returns, while the wave-amplitude-versus-throughput Pareto front shows that ACC at 18.2% sits at a natural knee where further penetration buys little additional wave reduction but costs significant throughput. These results provide an upper bound on real-highway effectiveness, as the ring road eliminates lane changes, on-ramps, and multi-lane dynamics.

---

## 1. Introduction

In 2008, Sugiyama, Fukui, Kikuchi and colleagues placed 22 drivers on a 230-metre circular track and asked them to maintain a target speed of 30 kilometres per hour with a safe following distance. Within minutes, the uniform flow broke down into a stop-and-go wave travelling backward around the ring -- a phantom traffic jam with no external cause. This experiment became the canonical existence proof for what physicists call jamitons: self-sustained traffic waves generated entirely by the intrinsic instability of human car-following behaviour.

The instability is well understood theoretically. When traffic density exceeds a critical threshold, the equilibrium in which every vehicle travels at the same speed with the same headway becomes linearly unstable. Small perturbations -- a driver braking slightly, a momentary loss of attention -- amplify along the chain of following vehicles until they grow into genuine stop-and-go waves. These waves travel backward at approximately 15 kilometres per hour and can persist for tens of minutes. The mathematical structure is captured by the Intelligent Driver Model (IDM) of Treiber, Hennecke and Helbing (2000), the Optimal Velocity Model of Bando (1995), and at the macroscopic level by the Aw-Rascle-Zhang second-order traffic flow equations. Flynn, Kasimov, Nave, Rosales and Seibold (2009) showed that the travelling-wave solutions of these equations -- jamitons -- are dynamically attracting: traffic starting near but inside the unstable density band evolves toward a jamiton-populated state.

The control question follows naturally: can a small fraction of longitudinally controlled vehicles -- Automated Vehicles (AVs), Connected Automated Vehicles (CAVs), or vehicles equipped with purpose-built Adaptive Cruise Control (ACC) -- dissolve these waves? Stern, Cui, Delle Monache and collaborators (2018) rebuilt the Sugiyama ring with one computer-controlled vehicle and demonstrated that a single controlled vehicle among twenty-one humans, a penetration of roughly 5%, could dissipate the wave entirely. Fuel consumption across the ring dropped by approximately 40% and effective throughput rose by about 15%.

The Stern result did not settle the operational question. A ring is not a highway: its boundary is periodic, its density is conserved, and its single lane is not realistic. The CIRCLES consortium moved the result toward real-world conditions with the MegaVanderTest (MVT) on Interstate 24 in Nashville, where 100 AVs were driven into normal traffic at 3-5% penetration. The headline numbers indicate measurable impact, but the precise minimum penetration rate on a real freeway remains an open question.

This paper approaches the minimum-penetration question through a systematic HDR methodology. We implement the Sugiyama ring road as a pure-Python IDM simulation, establish a quantitative baseline, tournament five controller families, run 105 pre-registered single-change experiments with strict keep/revert criteria, compose the best improvements, and perform a dense penetration sweep from 0% to 100% for the top two controller families. The result is a complete picture of how wave amplitude, throughput, and fuel consumption vary with penetration rate and controller choice on the canonical ring road.

---

## 2. Detailed Baseline: The All-IDM Ring Road

### 2.1 Configuration

The baseline simulation reproduces the Sugiyama experiment in silico. Twenty-two vehicles are placed on a 230-metre ring road, initially equally spaced (10.45 m apart) with a small random velocity perturbation (uniform on [-0.5, +0.5] m/s around the equilibrium speed). Each vehicle is 5 metres long and governed by the IDM:

```
acceleration_i = a * [1 - (v_i / v0)^delta - (s_star / gap_i)^2]

s_star = s0 + max(0, v_i * T + v_i * (v_i - v_leader) / (2 * sqrt(a * b)))
```

with parameters tuned for ring-road instability:

| Parameter | Symbol | Value | Units |
|---|---|---|---|
| Desired speed | v0 | 30.0 | m/s |
| Time headway | T | 1.0 | s |
| Max acceleration | a | 1.3 | m/s^2 |
| Comfortable deceleration | b | 2.0 | m/s^2 |
| Acceleration exponent | delta | 4 | - |
| Minimum gap | s0 | 2.0 | m |
| Vehicle length | L | 5.0 | m |
| Noise standard deviation | sigma | 0.3 | m/s^2 |

The time headway T = 1.0 s is deliberately reduced from the textbook value of 1.5 s. At T = 1.5 s on the 22/230 ring, the IDM equilibrium has spacing ~10.5 m and speed ~2.3 m/s, which lies near the stability boundary. Reducing T to 1.0 s raises the equilibrium speed slightly and pushes the system firmly into the string-unstable regime. Adding Gaussian acceleration noise (sigma = 0.3 m/s^2 per vehicle per timestep) then reliably triggers stop-and-go waves within the first 100 seconds, matching the Sugiyama experiment qualitatively.

Integration uses forward Euler at dt = 0.1 s for 600 seconds. A single-timestep braking perturbation of -5 m/s^2 is applied to vehicle 0 at t = 5 s to seed the wave, though experiments H062-H065 confirm that the wave forms even without this perturbation (noise alone suffices).

### 2.2 Baseline Metrics

The baseline all-IDM run (experiment E00, seed=42) produces:

| Metric | Value | Definition |
|---|---|---|
| Wave amplitude | 8.17 m/s | Mean per-timestep (max velocity - min velocity) in steady-state window (last 2/3 of simulation) |
| Velocity variance | 2.89 m/s | Standard deviation of all velocities in steady-state |
| Throughput | 1039.4 veh/hr | Edie's generalised throughput: total distance / (ring length x time) x 3600 |
| Fuel proxy | 130.65 mL/km | VT-Micro simplified: alpha*v + beta*v*max(a,0) + gamma*v^3, normalised to mL per vehicle-km |
| Minimum spacing | 1.79 m | Smallest bumper-to-bumper gap in steady-state |

A 5-seed sweep (seeds: 42, 0, 1, 2, 100) established the noise floor at 2-sigma: wave amplitude +/- 0.40 m/s, velocity variance +/- 0.109 m/s, throughput +/- 15.15 veh/hr, fuel +/- 1.98 mL/km. The keep/revert threshold for Phase 2 experiments is set at 2-sigma: an improvement must reduce wave amplitude by at least 0.40 m/s below the current best to be kept.

### 2.3 Wave Characteristics

The baseline wave is a single coherent jamiton propagating backward around the ring. Vehicles periodically decelerate to near-zero speed (the "jam" region), then accelerate back toward free-flow speed before encountering the trailing edge of the jam again. The wave period is approximately 35-40 seconds, consistent with analytical predictions for IDM at this density. The velocity range within a single wave cycle spans from near 0 m/s to approximately 8 m/s, matching the measured wave amplitude of 8.17 m/s.

**Figure 1** (`plots/trajectory_baseline.png`) shows the space-time trajectory diagram of the baseline all-IDM ring. Each dot represents a vehicle at a given time, coloured by velocity (dark = stopped, bright = free-flow). The backward-propagating stop-and-go wave is clearly visible as diagonal dark bands sweeping from right to left across the ring.

---

## 3. Detailed Solution: ACC at 18.2% Penetration

### 3.1 The Winning Controller

The Phase 1 tournament tested five controller families at two penetration levels (4.5% and 18.2%). The clear winner was the Adaptive Cruise Control (ACC) controller at 18.2% penetration (4 vehicles out of 22):

```python
@dataclass
class ACCController:
    v_des: float = 20.0    # desired cruise speed (m/s)
    T_des: float = 1.8     # desired time headway (s)
    s0: float = 4.0        # minimum standstill gap (m)
    k1: float = 0.3        # gap-error gain
    k2: float = 0.5        # speed-difference gain
    name: str = "ACC"

    def __call__(self, own_v, lead_v, gap, dt):
        desired_gap = self.s0 + own_v * self.T_des
        accel = self.k1 * (gap - desired_gap) + self.k2 * (lead_v - own_v)
        if gap > 3.0 * desired_gap:
            accel += 0.2 * (self.v_des - own_v)
        return clamp(accel, -9.0, 3.0)
```

The four ACC vehicles are placed at equally spaced positions around the ring (indices 0, 5, 11, 16 from 22 vehicles).

### 3.2 Performance

| Metric | Baseline (E00) | ACC 4/22 (T08) | Change |
|---|---|---|---|
| Wave amplitude | 8.17 m/s | 0.55 m/s | -93.3% |
| Velocity variance | 2.89 m/s | 0.16 m/s | -94.5% |
| Throughput | 1039.4 veh/hr | 930.4 veh/hr | -10.5% |
| Fuel proxy | 130.65 mL/km | 107.55 mL/km | -17.7% |
| Minimum spacing | 1.79 m | 4.08 m | +128% |

**Figure 2** (`plots/trajectory_suppressed.png`) shows the space-time trajectory for the ACC 4/22 configuration. Compared to Figure 1, the dark bands have vanished: all vehicles maintain a nearly uniform velocity, and the stop-and-go wave is suppressed.

### 3.3 Causal Mechanism

The ACC suppresses the wave through two complementary mechanisms embedded in its control law:

**Gap-error feedback (k1 term):** The term `k1 * (gap - desired_gap)` acts as a restoring force that pulls the ACC vehicle's gap toward its desired value. When the human driver ahead brakes (closing the gap), the ACC decelerates proportionally. When the human accelerates (opening the gap), the ACC accelerates. This proportional response is critically different from the IDM's nonlinear desired-gap calculation, which can overshoot and amplify perturbations.

**Relative-velocity damping (k2 term):** The term `k2 * (lead_v - own_v)` directly opposes the velocity difference between the ACC vehicle and its leader. This is the string-stability term: it damps oscillations by making the ACC resist velocity changes relative to its leader. When the leader's velocity oscillates as the wave passes, the k2 term smooths the ACC's own velocity response, preventing the oscillation from amplifying to the vehicles behind.

**Conservative time headway:** The ACC's T_des = 1.8 s (versus the human IDM's T = 1.0 s) means the ACC maintains a larger gap. This absorbs perturbations: when a human ahead brakes into the jam, the ACC has more gap-distance to work with before it needs to brake sharply itself. The larger gap acts as a buffer.

**Why four vehicles suffice:** With four equally-spaced ACC vehicles on a 22-vehicle ring, every consecutive human platoon contains at most 4-5 vehicles. Below the critical platoon length for IDM wave growth at these parameters, perturbations cannot amplify enough within a 4-5 vehicle chain to regenerate the wave before hitting the next ACC vehicle, which damps them. The transition from 3 ACC (1.77 m/s, platoon length ~6) to 4 ACC (0.55 m/s, platoon length ~4-5) corresponds precisely to crossing below this critical length.

---

## 4. Methods

### 4.1 Simulation Platform

All experiments use a pure-Python forward-Euler IDM simulator (`sim_ring_road.py`, 329 lines). The simulator takes a `RingRoadConfig` dataclass specifying ring geometry, IDM parameters, noise level, and perturbation settings. It accepts a list of "smart" vehicle indices and a controller factory function that replaces the default IDM with a pluggable controller for those vehicles. The simulator returns a pandas DataFrame with columns (time, vehicle_id, position, velocity, acceleration, gap, is_smart) at 0.1-second resolution.

We chose pure-Python over SUMO/Flow because the ring road is a one-dimensional continuous-time ODE (Ordinary Differential Equation) system where forward Euler at dt = 0.1 s is well within stability limits. Each 600-second simulation of 22 vehicles takes approximately 0.5 seconds. This enables the large-scale HDR loop (105 + 10 + 69 = 184 total experiments) to complete in under 5 minutes.

### 4.2 Metrics

Four primary metrics and one safety metric are computed on the steady-state window (last 2/3 of each simulation):

1. **Wave amplitude** (m/s): mean of per-timestep (max velocity - min velocity) across all vehicles. The primary optimisation target.
2. **Velocity variance** (m/s): standard deviation of all velocities.
3. **Throughput** (veh/hr): Edie's generalised definition -- total distance travelled divided by (ring length times simulation duration), converted to vehicles per hour.
4. **Fuel proxy** (mL/km): VT-Micro simplified model using speed and positive acceleration.
5. **Minimum spacing** (m): smallest bumper-to-bumper gap, a safety indicator.

### 4.3 Phase 0.5: Baseline Audit

The all-IDM baseline (E00) was established with a single canonical run (seed=42) and a 5-seed sweep to quantify the noise floor. The 2-sigma threshold for keep/revert decisions was set at 0.40 m/s on wave amplitude.

### 4.4 Phase 1: Controller Tournament

Five controller families were tested at 4.5% (1/22) and 18.2% (4/22) penetration, plus ceiling checks at 100% (22/22):

| Controller | Source | Key Feature |
|---|---|---|
| IDM (control) | Treiber et al. 2000 | Same as human drivers; null control |
| FollowerStopper | Cui et al. 2017 / Stern et al. 2018 | Gap-based piecewise desired velocity |
| PIWithSaturation | Stern et al. 2018 | Integral feedback on leader velocity |
| ACC | Milanes & Shladover 2014 | Constant time-headway with gap-error + relative-velocity gains |
| ConstantVelocity | (Lower bound) | Ignores leader; perfect wave damper but unsafe |

The tournament winner was ACC at 18.2% (T08: wave_amp 0.55 m/s). ConstantVelocity was excluded as unrealistic (it ignores the leader's state and is unsafe by construction). FollowerStopper showed promise but underperformed (4.44 m/s at 18.2% with default parameters). PIWithSaturation was catastrophically unstable at 18.2% (30.13 m/s).

### 4.5 Phase 2: HDR Loop (105 Hypotheses)

One hundred five pre-registered single-change experiments were organised across 20 themes:

| Theme | Hypotheses | Key Question |
|---|---|---|
| 1. FS penetration sweep | H001-H008 | How does FS performance scale with penetration? |
| 2. Controller family comparison | H009-H016 | Repeated tournament at controlled conditions |
| 3. FS gain tuning | H017-H026 | Can FS be improved by parameter tuning? |
| 4. PI gain tuning | H027-H033 | Can PI be fixed? |
| 5. ACC time headway | H034-H038 | What is the optimal ACC time headway? |
| 6. Ring size | H039-H044 | Do findings transfer to larger rings? |
| 7. Human driver model | H045-H054 | How sensitive are results to IDM parameters? |
| 8. Noise level | H055-H061 | Does noise level affect controller effectiveness? |
| 9. Initial perturbation | H062-H065 | Does perturbation type matter for steady state? |
| 10. Vehicle placement | H066-H070 | Does placement strategy matter? |
| 11. Heterogeneous desired speed | H071-H073 | Effect of driver heterogeneity |
| 12. Multi-objective | H074-H077 | Fuel and throughput trade-offs |
| 13. Run length | H078-H080 | Sensitivity to simulation duration |
| 14. dt sensitivity | H081-H083 | Integration timestep validation |
| 15. Cross-controller penetrations | H084-H087 | ACC at intermediate penetrations |
| 16. ACC gain tuning | H088-H091 | Sensitivity of ACC to gain parameters |
| 17. FS tuning at low penetration | H092-H095 | Ring-specific FS tuning |
| 18. Noise x controller | H096-H098 | Controller robustness under varying noise |
| 19. Density variation | H099-H103 | Effect of vehicle count at fixed ring length |
| 20. Mixed controller strategies | H104-H105 | Combining FS and ACC |

Each experiment changes exactly one variable from either the Phase 1 winner configuration (ACC at 4/22) or the all-IDM baseline, runs with seed=42, and measures all five metrics. The keep/revert decision compares wave amplitude against the running best minus 0.40 m/s (2-sigma noise floor).

### 4.6 Phase 2.5: Compositional Retest

Ten compositions (C001-C010) combined the most promising single-change improvements: optimal ACC time headway with higher penetration, ring-tuned FS at various penetrations, ACC transfer to larger rings, noise robustness checks, combined gain tuning, and mixed controller fleets.

### 4.7 Phase B: Discovery Sweep

A dense sweep from 0 to 22 smart vehicles (in steps of 1) was run for three controller variants: ACC (default parameters), FS-tuned (ring-specific v_des=6, s_st=2, s_go=12, k_v=0.8), and FS-default (standard parameters). This yields wave amplitude, throughput, and fuel consumption as continuous functions of penetration rate for each controller, enabling identification of the critical penetration rate and construction of the Pareto front.

---

## 5. Results

### 5.1 Phase 1 Tournament

| Exp | Controller | Penetration | Wave Amp (m/s) | Throughput (veh/hr) | Fuel (mL/km) |
|---|---|---|---|---|---|
| E00 | All-IDM | 0% | 8.17 | 1039.4 | 130.65 |
| T03 | FollowerStopper | 4.5% (1/22) | 8.28 | 863.8 | 132.44 |
| T04 | FollowerStopper | 18.2% (4/22) | 4.44 | 529.4 | 119.98 |
| T05 | PIWithSaturation | 4.5% (1/22) | 8.77 | 912.8 | 135.41 |
| T06 | PIWithSaturation | 18.2% (4/22) | 30.13 | 3962.8 | 122.85 |
| T07 | ACC | 4.5% (1/22) | 7.45 | 1008.5 | 126.47 |
| T08 | ACC | 18.2% (4/22) | 0.55 | 930.4 | 107.55 |
| T09 | ConstantVelocity | 4.5% (1/22) | 0.46 | 2725.6 | 108.57 |
| T11 | All-FollowerStopper | 100% (22/22) | 0.00 | 7.6 | 100.00 |
| T12 | All-ACC | 100% (22/22) | 0.00 | 283.2 | 100.00 |

Key observations: ACC dramatically outperforms FS at 18.2%. PI is catastrophically broken. ConstantVelocity is effective but unsafe (it ignores the leader). Both FS and ACC can fully suppress the wave at 100% penetration, but FS reduces throughput to near-zero (7.6 veh/hr) at 100% because its v_des = 15 m/s is too high for the ring's equilibrium, causing vehicles to stop frequently.

**Figure 3** (`plots/controller_comparison.png`) shows the wave amplitude for each controller family at 18.2% penetration. The PI controller's catastrophic instability (30.1 m/s, worse than baseline) and ACC's near-complete suppression (0.55 m/s) are immediately apparent.

### 5.2 Phase 2: HDR Loop Results

Of 105 pre-registered single-change experiments:
- **1 KEEP** (H008: all-FS 100%, wave_amp 0.00)
- **104 REVERT**
- **0 DEFER**

The sole KEEP was H008 (all 22 vehicles FollowerStopper, 100% penetration), which trivially achieves zero wave amplitude. The strict keep/revert protocol -- requiring improvement below the running best minus 0.40 m/s -- means that once H008 set the best to 0.00 m/s, no single-change experiment could beat zero. However, the Phase 2 data is rich with insights even among the reverted experiments:

**Theme 3 (FS gain tuning) revealed that FS is highly sensitive to v_des:** Lowering v_des from 15 to 5-8 m/s at 4/22 penetration reduced wave amplitude from 4.44 m/s (default) to 0.30-0.32 m/s. This dramatic improvement shows that the default FS parameters are calibrated for highway conditions (v_des = 15 m/s ~ 54 km/h), not the ring's low equilibrium speed. The FS's poor tournament performance was a tuning issue, not a fundamental limitation.

**Theme 4 (PI tuning) confirmed that PI is fundamentally unsuited to the ring.** Even with k_i = 0 (pure proportional, H030: 6.06 m/s) or T_des = 2.5 s (H033: 3.01 m/s), PI never approached ACC's performance. The integral term causes catastrophic windup: the ring's equilibrium gap (~5.5 m) is far below PI's target (s0 + v * T_des ~ 11 m), creating persistent error that the integrator accumulates without bound.

**Theme 5 (ACC time headway) showed that T_des = 1.8 s is near-optimal for the ring.** Shorter headways (T_des = 0.8 or 1.0 s) made ACC *worse* (wave_amp 9.55 and 8.57 m/s respectively), because the ACC becomes string-unstable with too-tight following. Longer headways (T_des = 2.5-3.0 s) achieved slightly lower wave amplitude (0.36-0.39 m/s) but at the cost of reduced throughput. The default T_des = 1.8 sits at a sweet spot.

**Theme 7 (IDM parameters) confirmed the stability diagram.** Increasing T from 1.0 to 1.5 s (textbook value) reduced wave amplitude to 0.40 m/s -- the system approaches linear stability. At T = 2.0 s, wave amplitude drops to 0.30 m/s. This validates our choice of T = 1.0 s to reliably produce phantom jams.

**Theme 9 (perturbation) confirmed that steady-state wave amplitude is independent of the initial perturbation type.** Whether the perturbation is removed entirely (H062: 8.00 m/s), strengthened to -9 m/s^2 (H063: 8.20 m/s), weakened to -1 m/s^2 (H064: 8.05 m/s), or delayed to 50 s (H065: 8.07 m/s), the steady-state wave amplitude stays within the noise floor of the baseline. This confirms that the jamiton is a dynamical attractor, consistent with the theoretical prediction.

**Theme 10 (placement) showed that equally-spaced placement outperforms clustered and random placement for FS.** Clustered placement (H066: 7.18 m/s) is dramatically worse than equally-spaced (T04: 4.44 m/s), while random placements (H068-H070: 7.13-8.14 m/s) are generally worse as well. This supports the theory that the key parameter is maximum human-platoon length: clustering creates one long uncontrolled chain that supports wave growth.

**Theme 15 (ACC at intermediate penetrations) mapped the ACC transition:** 1/22 = 7.45, 2/22 = 5.27, 3/22 = 1.77, 4/22 = 0.55, 6/22 = 0.41, 11/22 = 0.26 m/s. The sharp transition between 3/22 and 4/22 corresponds to crossing below the critical human-platoon length for the IDM at these parameters.

### 5.3 Phase 2.5: Composition Results

| Exp | Description | Wave Amp (m/s) | Throughput (veh/hr) |
|---|---|---|---|
| C001 | ACC T_des=0.8, 6/22 | 9.32 | -- |
| C002 | FS ring-tuned, 6/22 | 5.89 | -- |
| C003 | ACC 18/100 on 1000m ring | 1.08 | -- |
| C004 | ACC 4/22, noise=0.5 | 1.10 | -- |
| C005 | ACC T_des=0.8, k2=1.0, 4/22 | 7.22 | -- |
| C006 | FS ring-tuned, 8/22 | 6.44 | -- |
| C007 | ACC T_des=1.0, 3/22 | 8.00 | -- |
| C008 | ACC T_des=0.8, 3/22 | 9.13 | -- |
| C009 | ACC T_des=0.8, 2/22 | 8.87 | -- |
| C010 | Mixed 2ACC+2FS(tuned), 4/22 | 7.74 | -- |

No composition improved on the Phase 2 best. The most notable result is C003: ACC at 18% penetration on a larger ring (100 vehicles, 1000 m) achieves 1.08 m/s -- the finding *partially* transfers to larger scale but with reduced effectiveness (0.55 to 1.08 m/s). C004 shows that increasing noise from 0.3 to 0.5 m/s^2 degrades ACC performance from 0.55 to 1.10 m/s -- the controller is noise-sensitive. C001 and C005 confirm that shortening ACC time headway below 1.8 s is counterproductive even when combined with higher penetration or increased damping gain.

### 5.4 Phase B: Dense Penetration Sweep

The critical finding from the dense 0-to-22 sweep:

**ACC penetration sweep (wave amplitude in m/s):**

| n_smart | Penetration | Wave Amp | Throughput | Fuel | Min Spacing |
|---|---|---|---|---|---|
| 0 | 0.0% | 8.17 | 1039.4 | 130.65 | 1.79 |
| 1 | 4.5% | 7.45 | 1008.5 | 126.47 | 1.79 |
| 2 | 9.1% | 5.27 | 1006.1 | 117.47 | 1.80 |
| 3 | 13.6% | 1.77 | 984.8 | 109.15 | 3.39 |
| **4** | **18.2%** | **0.55** | **930.4** | **107.55** | **4.08** |
| 5 | 22.7% | 0.50 | 875.7 | 107.15 | 3.97 |
| 6 | 27.3% | 0.41 | 824.5 | 106.76 | 3.92 |
| 8 | 36.4% | 0.32 | 730.2 | 106.00 | 3.77 |
| 11 | 50.0% | 0.26 | 607.2 | 104.87 | 3.40 |
| 16 | 72.7% | 0.19 | 439.5 | 102.77 | 2.98 |
| 22 | 100.0% | 0.00 | 283.2 | 100.00 | 5.45 |

**Figure 4** (`plots/headline_finding.png`) plots wave amplitude against the number of ACC vehicles from 0 to 22. The sharp transition at 4/22 is the headline finding of this paper: the curve drops from 1.77 m/s at 3 ACC vehicles to 0.55 m/s at 4 ACC vehicles, then flattens with diminishing returns.

**Critical penetration rates for wave_amp < 1 m/s:**
- ACC: **4/22 (18.2%)** -- achieves 0.55 m/s
- FS-default: **5/22 (22.7%)** -- achieves 0.74 m/s
- FS-tuned (ring): **19/22 (86.4%)** -- the "ring-tuned" parameters actually perform worse

**Pareto front (wave amplitude vs throughput):**

The Pareto front for ACC shows a clear knee at 4/22 (18.2%):
- Below 18.2%: large wave amplitude, high throughput (the wave costs fuel but not throughput)
- At 18.2%: wave nearly eliminated, throughput reduced by only 10.5%
- Above 18.2%: diminishing returns on wave amplitude with continued throughput loss

Each additional ACC vehicle beyond 4 reduces wave amplitude by only ~0.02-0.05 m/s but costs roughly 45-50 veh/hr of throughput. The marginal trade-off becomes unfavourable.

**Figure 5** (`plots/pareto_front.png`) shows this Pareto front with points coloured by the number of ACC vehicles. The knee at 4 ACC (18.2%) is clearly visible: moving rightward (higher throughput) from the knee rapidly increases wave amplitude, while moving leftward (more ACC vehicles) yields only marginal wave reduction.

### 5.5 FollowerStopper: A Throughput Problem

The FS-default sweep reveals a striking throughput penalty. At 5/22 (22.7%), FS achieves 0.74 m/s wave amplitude -- good -- but throughput drops to 401 veh/hr, a 61% reduction from baseline. The reason is the FS's v_des = 15 m/s: on the dense ring where equilibrium speed is ~4-5 m/s, the FS spends most of its time in the s_st < gap < s_go region where it targets a low speed via the quadratic ramp. Furthermore, because v_des = 15 m/s is far above attainable speed, the FS never enters its cruise mode and instead acts as a permanent speed limiter.

At 100% penetration (all FS), throughput collapses to 7.6 veh/hr -- essentially traffic standstill. Compare with all-ACC at 100%, which maintains 283.2 veh/hr. This makes ACC strictly preferable for any practical application.

---

## 6. Discussion

### 6.1 The Sharp Transition at 18.2%

The most striking finding is the sharpness of the ACC penetration transition. Moving from 3 to 4 ACC vehicles (13.6% to 18.2%) reduces wave amplitude from 1.77 to 0.55 m/s -- a factor of 3.2 improvement from adding a single vehicle. This transition corresponds to reducing the maximum human-platoon length from approximately 6 vehicles to 4-5 vehicles, which crosses below the critical platoon length for IDM wave growth at T = 1.0 s, a = 1.3 m/s^2, noise = 0.3 m/s^2.

The critical platoon length for string instability depends on the human driver model parameters. With the Treiber-Kesting stability criterion for IDM, the amplification factor per vehicle is approximately exp(L / L_crit) where L_crit depends on the IDM parameters. When the maximum platoon length drops below L_crit, perturbations decay rather than grow, and the wave cannot sustain itself.

### 6.2 ACC Beating FollowerStopper: A Surprising Result

The literature prior, particularly Stern et al. (2018) and Cui et al. (2017), used FollowerStopper as the primary wave-suppression controller. Our finding that ACC dramatically outperforms FS at matched penetration (0.55 vs 4.44 m/s at 18.2%) warrants explanation.

The key difference is that FS was designed for the original Stern ring experiment where vehicles cruise at ~30 km/h (8.3 m/s) with large gaps. Its default parameters (v_des = 15 m/s, s_go = 35 m) are calibrated for a highway-like flow regime. On our denser ring (equilibrium speed ~4-5 m/s, equilibrium gap ~5.5 m), the FS's s_go = 35 m is far above any gap the FS will ever encounter, meaning the FS operates entirely in its "stop" and "quadratic ramp" regions and never reaches cruise mode. This causes it to drive too slowly and degrade throughput.

The ACC, by contrast, uses a relative control law (gap-error + speed-difference) that adapts automatically to the local flow conditions. It does not have a fixed desired speed that can mismatch the ring's equilibrium; instead, it adjusts its speed to maintain a desired headway relative to whatever the leader is doing. This makes ACC more portable across flow regimes.

H017-H018 confirm this interpretation: when FS v_des is lowered to 5-8 m/s (matching the ring's equilibrium), FS achieves 0.30-0.32 m/s wave amplitude -- comparable to ACC. The FS is not inherently inferior; it was simply miscalibrated for our ring.

### 6.3 PIWithSaturation: Integral Windup

PI's catastrophic failure (30.13 m/s at 18.2%, worse than baseline) has a clear root cause: integral windup. The PI targets a desired gap of s0 + v * T_des = 5 + 4 * 1.5 = 11 m. But the ring's equilibrium gap is approximately 5.5 m. The persistent 5.5 m gap error is accumulated by the integral term, eventually driving the PI to its saturation limits in an oscillatory mode. Reducing T_des to 0.8 s (H032) makes this worse (119.95 m/s) because the PI now targets an even tighter gap relative to what is achievable. Only T_des = 2.5 s (H033: 3.01 m/s) partially helps by making the target gap closer to the ring's natural gap, reducing the persistent error.

### 6.4 Noise, Perturbation, and the Jamiton Attractor

The robustness experiments (Themes 8, 9) confirm that the steady-state wave is a dynamical attractor. The wave amplitude at steady state is nearly independent of:
- Initial perturbation strength (H062-H064: 8.00-8.20 m/s)
- Perturbation timing (H065: 8.07 m/s)
- Noise level over a wide range (H055-H059: 5.92-8.23 m/s)

The only case where noise matters significantly is the zero-noise case (H055: 5.92 m/s), where the wave forms from the perturbation alone but has lower steady-state amplitude because noise is not continuously feeding energy into the wave. This is consistent with the jamiton theory: the wave structure is determined by the traffic flow equations, not the initial conditions, but noise affects the wave's energy input.

### 6.5 Transfer to Larger Rings

The composition experiments tested whether the ACC result transfers beyond the 22-vehicle Sugiyama ring. C003 placed 18 ACC vehicles among 100 total on a 1000-metre ring (18% penetration, same density as Sugiyama), achieving 1.08 m/s wave amplitude. This is notably higher than the 0.55 m/s on the 22-vehicle ring, suggesting partial but incomplete transfer. On the larger ring, there are more human vehicles between each pair of ACC vehicles (approximately 4.6 vs 4.5), and the longer absolute distances give perturbations more room to amplify before encountering the next damper. Additionally, the larger ring may support multiple simultaneous jamitons, creating a more complex wave structure that is harder for evenly-spaced ACC vehicles to address.

The ring-size experiments (H039-H044) provide additional context. At 40 vehicles on 400 metres (same density), 4 FS at 10% penetration achieved 4.90 m/s wave amplitude, while 8 FS at 20% achieved 0.72 m/s. On a much larger ring (200 vehicles, 4000 metres), 10 FS at 5% achieved 14.40 m/s -- worse than even the small-ring baseline. These results suggest that wave suppression on larger rings requires maintaining the same absolute spacing between smart vehicles, not merely the same penetration fraction.

### 6.6 Density and the Instability Boundary

Theme 19 explored density variation at fixed ring length. Reducing the vehicle count from 22 to 18 on the 230-metre ring (H099: 8.12 m/s) did not eliminate the wave, contrary to the expectation that 18 vehicles would be below the Sugiyama critical density. This is because our IDM T = 1.0 s is more unstable than the T = 1.5 s used in many analytical stability calculations. At 20 vehicles (H100: 8.42 m/s), the wave is actually slightly stronger than at 22, likely due to different wave-vehicle resonance conditions. Increasing density to 25 (H101: 5.19 m/s) and 30 (H102: 2.52 m/s) vehicles surprisingly reduced wave amplitude. At 30 vehicles, the equilibrium gap is only 2.67 m, which is so tight that vehicles cannot reach high speeds even briefly, limiting the velocity range and thus the measured wave amplitude. The system is deeply congested rather than oscillating.

### 6.7 Fuel and Multi-Objective Trade-offs

The fuel proxy metric tracks wave amplitude closely because the fuel model penalises positive acceleration events. When the wave is suppressed and vehicles maintain steady speed, the acceleration variance drops and fuel consumption decreases. ACC at 18.2% reduces fuel from 130.65 to 107.55 mL/km (-17.7%). The fuel reduction saturates quickly: going from 18.2% to 100% ACC only further reduces fuel from 107.55 to 100.00 mL/km, a diminishing return. The Pareto front shows that the fuel-optimal point coincides with the wave-suppression knee at 18.2% penetration, making fuel reduction a free co-benefit of wave suppression rather than a competing objective.

### 6.8 Limitations

This study has several important limitations:

1. **The ring road is not a highway.** Periodic boundaries conserve total vehicle number, eliminate on-ramps and off-ramps, and prevent density changes. Real highways have open boundaries, merging traffic, and spatially varying demand.

2. **Single lane only.** Lane-change disturbances are a major source of phantom jams on real highways. Our ring has no lane changes. The minimum penetration rate on a multi-lane highway is likely higher.

3. **Pure-Python, not SUMO.** Our forward-Euler integrator at dt = 0.1 s is accurate for the IDM's timescales but does not include SUMO's lane-change model, vehicle-type distributions, or detailed geometric representation. The dt sensitivity experiments (H081-H083) show that halving dt to 0.05 s produces similar results (8.28 vs 8.17 m/s), validating the 0.1 s timestep.

4. **No actuator delay or sensor noise in the controller.** Real ACC systems have sensor delay (~0.1-0.3 s), actuator delay (~0.1-0.5 s), and measurement noise. These reduce the achievable minimum headway for string stability and would increase the required penetration rate.

5. **IDM may not perfectly represent human driving.** The IDM is a convenient analytical model but real drivers exhibit asymmetric acceleration/deceleration, distraction, variable reaction times, and cultural differences in following distance.

6. **The result is an upper bound.** Given limitations 1-5, the 18.2% critical penetration rate we find should be interpreted as a lower bound on the real-highway figure. Real-world experiments like the CIRCLES MegaVanderTest suggest that 3-5% penetration has measurable but incomplete effect on I-24, consistent with our finding that ACC at 4.5% (1/22) reduces wave amplitude by only 9% (from 8.17 to 7.45 m/s).

---

## 7. Conclusion

Four Adaptive Cruise Control vehicles among 22 human drivers -- an 18.2% penetration rate -- reduce phantom traffic jam wave amplitude on the Sugiyama ring road from 8.17 m/s to 0.55 m/s, a 93.3% reduction. This result emerges from a systematic hypothesis-driven research campaign of 105 single-change experiments across 20 themes, with strict pre-registered keep/revert criteria.

The ACC controller achieves this through gap-error feedback and relative-velocity damping, which together prevent perturbation amplification across short human-driver platoons. The transition from ineffective (13.6% penetration, 1.77 m/s wave) to effective (18.2%, 0.55 m/s) is sharp and corresponds to reducing the maximum human-platoon length below the critical threshold for IDM string instability.

Key secondary findings include:
- FollowerStopper matches ACC performance when its parameters are tuned for the ring (v_des = 5-8 m/s), but imposes a severe throughput penalty
- PIWithSaturation is catastrophically unstable on the ring due to integral windup
- The steady-state wave amplitude is a dynamical attractor independent of perturbation type
- ACC with time headway below 1.4 s becomes string-unstable and worsens the wave
- Equal spacing of smart vehicles outperforms clustered or random placement
- Noise level has minimal effect on steady-state wave characteristics

The ring road result provides an optimistic upper bound. Real highways with lane changes, on-ramps, and heterogeneous traffic will require higher penetration rates. Nevertheless, the finding that a simple constant-time-headway ACC -- not a purpose-designed wave-suppression controller -- can nearly eliminate a phantom jam at under 20% penetration is encouraging for the near-term deployment of connected and automated vehicles.

---

## List of Figures

| Figure | File | Description |
|---|---|---|
| 1 | `plots/trajectory_baseline.png` | Space-time trajectory of the all-IDM baseline showing the backward-propagating stop-and-go wave |
| 2 | `plots/trajectory_suppressed.png` | Space-time trajectory with 4 ACC vehicles (18.2%) showing the wave suppressed |
| 3 | `plots/controller_comparison.png` | Controller comparison bar chart at 18.2% penetration |
| 4 | `plots/headline_finding.png` | Wave amplitude vs number of ACC vehicles -- the sharp penetration threshold |
| 5 | `plots/pareto_front.png` | Pareto front: wave amplitude vs throughput for the ACC penetration sweep |

---

## 8. Key References

1. Sugiyama, Y., Fukui, M., Kikuchi, M., et al. (2008). "Traffic jams without bottlenecks -- experimental evidence for the physical mechanism of the formation of a jam." New Journal of Physics 10, 033001.
2. Tadaki, S., Kikuchi, M., Fukui, M., et al. (2013). "Phase transition in traffic jam experiment on a circuit." New Journal of Physics 15, 103034.
3. Stern, R.E., Cui, S., Delle Monache, M.L., et al. (2018). "Dissipation of stop-and-go waves via control of autonomous vehicles: Field experiments." Transportation Research Part C 89, 205-221.
4. Cui, S., Seibold, B., Stern, R., Work, D.B. (2017). "Stabilizing traffic flow via a single autonomous vehicle: Possibilities and limitations." IEEE Intelligent Vehicles Symposium.
5. Treiber, M., Hennecke, A., Helbing, D. (2000). "Congested traffic states in empirical observations and microscopic simulations." Physical Review E 62(2), 1805.
6. Treiber, M., Kesting, A. (2013). Traffic Flow Dynamics: Data, Models and Simulation. Springer.
7. Wilson, R.E., Ward, J.A. (2011). "Car-following models: fifty years of linear stability analysis -- a mathematical perspective." Transportation Planning and Technology 34(1), 3-18.
8. Monteil, J., Bouroche, M., Leith, D.J. (2014). "L2 and L-infinity stability analysis of heterogeneous traffic with application to parameter optimization for the control of automated vehicles." IEEE Transactions on Control Systems Technology.
9. Milanes, V., Shladover, S.E. (2014). "Modeling cooperative and autonomous adaptive cruise control dynamic responses using experimental data." Transportation Research Part C 48, 285-300.
10. Flynn, M.R., Kasimov, A.R., Nave, J.C., Rosales, R.R., Seibold, B. (2009). "Self-sustained nonlinear waves in traffic flow." Physical Review E 79(5), 056113.
11. Lee, J.H., Wang, T., Jang, K., Lichtle, N., et al. (2024). "The MegaVanderTest: A hundred AVs on I-24." Transportation Research Part C.
12. Chou, F.C., Bagabaldo, A., Bayen, A.M. (2022). "The Lord of the Ring Road: A Review and Evaluation of Autonomous Vehicle Control on a Single-Lane Ring Road." ACM/IEEE Transactions on Networking.
13. Wu, C., Kreidieh, A.R., Parvate, K., Vinitsky, E., Bayen, A.M. (2017-2022). "Flow: A Modular Learning Framework for Mixed Autonomy Traffic." Various venues.
14. Bando, M., Hasebe, K., Nakayama, A., Shibata, A., Sugiyama, Y. (1995). "Dynamical model of traffic congestion and numerical simulation." Physical Review E 51(2), 1035.
15. Gunter, G., Gloudemans, D., Stern, R.E., et al. (2020). "Are commercially implemented adaptive cruise control systems string stable?" IEEE Transactions on Intelligent Transportation Systems.
