# Knowledge Base: Phantom Traffic Jams and Mixed-Autonomy Suppression

## Established Results and Known Quantities

This document records proven facts, known benchmarks, validated techniques, and documented failures from the literature. HDR should treat these as constraints and baselines, not re-derive them. References are paper IDs from `papers.csv`.

---

## 1. Intelligent Driver Model (IDM) [17, 29, 120]

The IDM is the workhorse microscopic car-following model for the phantom-jam literature and the default human-driver model in Flow and SUMO.

### 1.1 Equations

```
v̇_i = a * [ 1 - (v_i / v0)^δ - ( s*(v_i, Δv_i) / s_i )^2 ]

s*(v, Δv) = s0 + max(0, v*T + v*Δv / (2*sqrt(a*b)))
```

Where:
- `v_i` = velocity of vehicle i
- `Δv_i = v_i - v_{i-1}` = closing speed (positive when approaching)
- `s_i` = bumper-to-bumper gap to the leader
- `v0` = desired free-flow speed
- `T` = safe/desired time headway
- `s0` = minimum standstill gap
- `a` = maximum acceleration
- `b` = comfortable deceleration
- `δ` = acceleration exponent (typically 4)

### 1.2 Standard highway parameters (Treiber-Kesting 2013 [29])

| Parameter | Symbol | Highway value | Units |
|---|---|---|---|
| Desired speed | v0 | 33.3 (= 120 km/h) | m/s |
| Safe time headway | T | 1.5 | s |
| Standstill gap | s0 | 2.0 | m |
| Max acceleration | a | 0.73 | m/s^2 |
| Comfort deceleration | b | 1.67 | m/s^2 |
| Exponent | δ | 4 | - |
| Vehicle length | l | 5 | m |

For ring-road experiments matching Sugiyama [1], smaller `v0` (~8 m/s) and smaller `s0` (1-2 m) are used. Higher `a` (~1.0-1.5 m/s^2) is used in some Flow benchmarks to make the instability more visible.

### 1.3 Equilibrium solution and fundamental diagram

Setting `v̇ = 0` and `Δv = 0`, the equilibrium gap is:

```
s_eq(v) = (s0 + v*T) / sqrt(1 - (v/v0)^δ)
```

The equilibrium density is `ρ(v) = 1 / (s_eq(v) + l)` and the equilibrium flow is `Q(v) = ρ(v) * v`. This gives a smooth unimodal fundamental diagram peaking at roughly 2000-2100 veh/h/lane with standard parameters.

### 1.4 String instability regime

The IDM becomes string-unstable in a density band around the capacity density. The exact range depends on `T`, `a`, `b` — higher `a`, higher `T`, and lower `b` tend to increase stability. Stability analysis is in Treiber-Kesting Chapter 15 [29] and Wilson-Ward [37]. For defaults, spontaneous jamitons form on a ring at ≈20-25 veh/km/lane.

---

## 2. Optimal Velocity Model (OVM) / Bando [18]

### 2.1 Equation

```
v̇_i = a * ( V(s_i) - v_i )
```

Pure OV: no relative-velocity feedback. Parameter `a` is the sensitivity (1/response time).

### 2.2 Standard V(s) function (Bando 1995)

```
V(s) = V_max / 2 * ( tanh((s - s_c)/w) + tanh(s_c / w) )
```

With standard parameters [18, 134]:
- `V_max` = 33.6 m/s
- `s_c` = 25 m (inflection / safe distance)
- `w` = characteristic width, ~13 m

The second `tanh` term is a normalisation ensuring V(0) = 0.

### 2.3 Stability criterion (linear, ring road)

The uniform state is linearly stable if and only if

```
V'(s*) < a / 2
```

where `s*` is the equilibrium gap. A smooth tanh V(s) with its peak derivative `V'_max = V_max / (2w)` fails this criterion whenever `V_max / (2w) > a/2`, i.e. `a < V_max / w`. For standard parameters (`V_max = 33.6, w = 13, a = 2.0 s^{-1}`) this is ≈2.58 > 2.0, so the pure OV model is unstable. This is by design: OV is the standard minimum model that exhibits spontaneous phantom jams.

### 2.4 Full Velocity Difference (FVD) extension [157]

```
v̇_i = a*(V(s_i) - v_i) + λ*Δv_i
```

with `Δv = v_leader - v_follower`. The relative-velocity feedback term `λ*Δv` stabilises the model considerably. With `λ ~ 0.3-0.5` and otherwise-OV-default parameters, the ring becomes stable at realistic densities.

---

## 3. FollowerStopper controller [5, 12, 214, 217]

FollowerStopper is a safety-first velocity controller designed to dissipate stop-and-go waves. It commands a velocity `v_cmd` based on the leader distance `Δx` and closing speed `Δv`.

### 3.1 Inputs and parameters

- `U` = the driver's free-flow desired velocity (user parameter, e.g., 6-10 m/s on the ring, 25-30 m/s on a freeway)
- `Δx` = bumper-to-bumper gap to leader
- `Δv_plus = max(0, v_ego - v_leader)` = positive closing velocity
- Three threshold distances `Δx_1 < Δx_2 < Δx_3`
- Three parameters `r_1 < r_2 < r_3` (typically `r_1 = r_2/2, r_3 = 2r_2`)

### 3.2 The target gap curves

```
Δx_k = Δx_k_base + (1 / (2*r_k)) * Δv_plus^2    for k = 1, 2, 3
```

These are quadratic target-distance curves in the `(Δv, Δx)` plane. The controller then piecewise selects the command velocity:

```
v_cmd = 0                              if Δx <= Δx_1
v_cmd = v_target * (Δx - Δx_1)/(Δx_2 - Δx_1)
                                       if Δx_1 < Δx <= Δx_2
v_cmd = v_target + (U - v_target)*(Δx - Δx_2)/(Δx_3 - Δx_2)
                                       if Δx_2 < Δx <= Δx_3
v_cmd = U                              if Δx > Δx_3
```

where `v_target = min(max(v_leader, 0), U)`. The three regions correspond to "stop", "transitional", and "cruise at U".

### 3.3 Default tuning (Stern 2018 [4])

- `Δx_1_base = 4.5 m`, `Δx_2_base = 5.25 m`, `Δx_3_base = 6.0 m`
- `r_1 = 1.5 m/s`, `r_2 = 1.0 m/s`, `r_3 = 0.5 m/s` (or scaled variants)
- `U` = ~6 m/s for the ring; ~29 m/s for the I-24 setting

### 3.4 Key property

FollowerStopper is *not* a car-following model in the usual sense; it does not try to match a desired gap. Instead it guarantees that the AV never forces a hard brake: it always slows down smoothly enough, early enough, that even if the leader stops at worst-case deceleration the AV can reach zero velocity before collision. The wave-dissipation property is a *consequence*, not a direct objective: by refusing to catch the trailing edge of the wave, FollowerStopper effectively breaks the feedback loop that sustains it.

---

## 4. PI with Saturation (PISaturated, PIS) controller [5]

An alternative to FollowerStopper with an explicit "follow the mean flow" structure.

### 4.1 Core idea

Maintain a running estimate of the average leader velocity and track it with a saturation-limited PI controller, treating the estimate as the desired speed.

### 4.2 Equations (Cui et al. 2017 [5])

```
U = running average of v_leader over a window W (e.g., 30-60 s)
v_target = β * (U + v_catch) + (1 - β) * v_cmd_prev
v_cmd = clip(v_target, v_min, v_max)
```

where `v_catch` is a small correction term to bring the AV toward the leader if the gap has grown too large. The saturation limits `v_min, v_max` are chosen to respect physical constraints and desired cruising speeds.

### 4.3 Typical gains

- Window `W = 38 s`
- Mixing coefficient `β = 0.2 - 0.4`
- `v_catch ~ 1 m/s`
- `v_max ~ 40 m/s`

The key design philosophy is the same as FollowerStopper: do not chase the instantaneous leader; track its mean. Empirically the two controllers give similar performance on the ring [4, 5].

---

## 5. String stability

### 5.1 Definitions [36, 37, 124, 125, 212]

Let `V_i(s)` be the Laplace transform of the velocity perturbation of vehicle i and let `Γ(s) = V_i(s) / V_{i-1}(s)` be the transfer function from the predecessor to the follower under linearised dynamics.

- **L2 string stability**: `||V_i||_2 <= ||V_{i-1}||_2` for all i, all disturbance inputs
- **L∞ string stability**: `sup_t |V_i(t)| <= sup_t |V_{i-1}(t)|` for all i, all disturbance inputs

Equivalent frequency-domain criteria (for linear time-invariant systems):

- L2: `|Γ(jω)| <= 1` for all `ω >= 0`
- L∞: integral condition on the impulse response

L∞ is stricter than L2: L∞ string stability implies L2 string stability but not conversely.

### 5.2 Necessary conditions for ACC (Lp spacing policy) [88]

For predecessor-following ACC with constant time headway `h` and leader-acceleration feedback:

```
h > 2 * τ_delay
```

where `τ_delay` is the total actuator + sensor delay. For typical production values (`τ_delay ~ 0.3-0.5 s`), this gives `h > ~0.6-1.0 s` to be string stable. Stock commercial ACC frequently uses 0.8-1.4 s, which barely sits at the margin. Gunter et al. [16] showed empirically that real commercial systems are string-unstable in practice.

### 5.3 Mixed-autonomy string stability [38, 127]

For a mixed platoon of `N` human drivers and `M` AVs, the overall string stability depends on the transfer function of the *entire* chain, not the AV alone. A natural sufficient condition is that each AV's `|Γ_AV(jω)|` is small enough to compensate for the `|Γ_human(jω)| > 1` of the humans upstream. This leads to the intuition that AV spacing is tighter than AV count: distributing AVs through the platoon is more effective than clustering them. Chou 2022 [12] supports this on the ring.

---

## 6. Ring-road instability threshold

### 6.1 Sugiyama 2008 empirical [1]

- Track length: 230 m
- Target speed: 30 km/h (8.33 m/s)
- Critical density: 22 vehicles (threshold between stable and unstable)
- Below 22: stable uniform flow
- At/above 22: phantom jam forms within ~1-2 minutes

### 6.2 Tadaki 2013 follow-up [2]

- Larger tracks, more participants
- Confirms free-to-jammed transition has the character of a dynamical (second-order-like) phase transition
- Critical density (as vehicles per unit length) depends on track length as expected for a ring

### 6.3 Theoretical (OV model on a ring) [18, 37, 189]

For the OV model with `N` vehicles on a ring of length `L`, the uniform state at gap `s* = L/N` is stable iff `V'(s*) < a/2`. For standard Bando parameters the instability spans approximately `s* ∈ [4 m, 60 m]`, which covers the useful density range of a real highway. Ring size enters mainly through which modes of wavelength `L/k` are expressible.

### 6.4 Characteristic wavelength

The most unstable mode has wavelength of order the equilibrium gap times a factor set by the ratio `V'(s*) / a`. For Sugiyama-tuned parameters the characteristic spacing is ~3-5 car lengths, matching the observed jam cluster size.

---

## 7. Stop-and-go wave propagation speed

### 7.1 The classical number [29, 160, 161]

Wide moving jams propagate backward (relative to the road) at a nearly universal speed:

```
c_jam ≈ -15 km/h (≈ -4.2 m/s)
```

Typical measured range: -12 to -18 km/h.

### 7.2 Why it is universal (Daganzo triangular FD picture) [31, 67, 204]

For a triangular fundamental diagram with backward wave slope `w`, the propagation speed of the trailing edge of a jam equals `-w`. For passenger-car traffic, `w ≈ 15-20 km/h` is empirically consistent across sites and years, which is why the jam propagation speed is so stable. The value is set by the minimum time headway and average vehicle length:

```
w = 1 / (h_min * ρ_jam)
```

where `h_min ≈ 1.5 s` and `ρ_jam ≈ 150 veh/km`, giving `w ≈ 16 km/h`.

### 7.3 Implications for HDR wave detection

A stop-and-go wave is detectable in a Lagrangian trajectory by looking for a backward-propagating velocity dip that travels at ~-15 km/h in the road frame. This is a clean signature distinct from bottleneck-induced congestion (which has a stationary front).

---

## 8. Phase diagram of highway traffic

### 8.1 Kerner's three phases [34, 35, 146, 147, 148]

1. **Free flow (F)**: density below the critical value; all vehicles travel near desired speed with large fluctuations in spacing
2. **Synchronized flow (S)**: intermediate density; speeds are reduced and correlated across lanes but there is no sharp wave front; this is the dominant congested phase at bottlenecks
3. **Wide moving jam (J)**: sharp front propagating upstream at `c_jam ≈ -15 km/h`; the front velocity is invariant to traffic conditions outside the jam

### 8.2 Transitions

- F → S: usually an *induced* transition at a bottleneck; sometimes *spontaneous* at high demand
- F → J (direct): rarer; typical of very homogeneous high-demand conditions (the Sugiyama ring limit)
- S → J: synchronized flow can support pinch points that emit wide moving jams

### 8.3 Alternative ARZ / jamiton framing [22, 23, 26, 27]

In the ARZ picture, there is free flow below the critical density, and a jamiton-dominated attractor above. The jamiton is the continuum analog of the wide moving jam. The scatter in the fundamental diagram is the signature of jamiton presence.

---

## 9. Fundamental diagram estimation

### 9.1 Edie's generalized definitions [65, 117]

For a region A of space-time:

```
Density:   ρ = T / |A|    where T = total time spent in A by all vehicles
Flow:      q = X / |A|    where X = total distance travelled in A by all vehicles
Speed:     v = X / T       (space-mean speed)
```

This gives `q = ρ*v` as a definitional identity regardless of how A is chosen.

### 9.2 Greenshields (1935) [66]

Linear speed-density: `v = v_f * (1 - ρ/ρ_j)`, which gives a parabolic `q(ρ) = v_f*ρ - (v_f/ρ_j)*ρ^2`. Capacity at `ρ_j/2`, max flow `v_f*ρ_j/4`.

### 9.3 Daganzo triangular (CTM) [67, 68, 69, 204]

```
q(ρ) = v_f * ρ                 if ρ <= ρ_c
     = w * (ρ_j - ρ)            if ρ > ρ_c
```

with `v_f` free-flow speed, `w` backward wave speed, `ρ_c = w*ρ_j/(v_f + w)`. This is the minimal model that reproduces the -15 km/h wave.

### 9.4 Typical passenger-car highway values [62, 64, 160]

| Quantity | Value | Units |
|---|---|---|
| Free-flow speed | v_f = 25 - 33 | m/s |
| Jam density | ρ_j = 120 - 160 | veh/km/lane |
| Critical density | ρ_c = 20 - 30 | veh/km/lane |
| Backward wave speed | w = 15 - 20 | km/h |
| Max flow (capacity) | q_max = 1800 - 2200 | veh/h/lane |
| Capacity drop | Δq_max ≈ 5 - 15% | of q_max |

---

## 10. Glossary

- **AV**: Autonomous Vehicle (broadly; self-driving or longitudinally-controlled)
- **ACC**: Adaptive Cruise Control — front-sensor-only longitudinal controller
- **CACC**: Cooperative ACC — ACC augmented with V2V communication of leader intent/acceleration
- **CAV**: Connected and Automated Vehicle (umbrella term)
- **V2V**: Vehicle-to-Vehicle communication
- **V2I**: Vehicle-to-Infrastructure communication
- **Jamiton**: A self-sustained nonlinear travelling wave solution of a second-order macroscopic traffic model [26]. Analogous to a detonation wave.
- **Phantom jam / stop-and-go wave**: A density wave that emerges without any external trigger and propagates backward against traffic. The empirical signature of the string instability.
- **Wide moving jam**: A sharp-front jam of width > typical vehicle length, propagating upstream at ~-15 km/h, invariant to inflow conditions (Kerner) [34]
- **String stability**: Property of a vehicle chain that upstream perturbations do not amplify along the chain [36, 212]. L2 and L∞ variants exist.
- **CFM**: Car-Following Model — the acceleration law `a_i = f(v_i, Δv_i, s_i)` for a single follower reacting to one leader
- **Eulerian control**: Control that acts at fixed spatial points (VSL, ramp metering). "Field-based" analog.
- **Lagrangian control**: Control that moves with the traffic (AV insertion). "Particle-based" analog.
- **Mixed autonomy**: A traffic stream containing both human drivers and controlled (AV/CAV) vehicles
- **Penetration rate**: Fraction of total vehicles that are controlled. Typical HDR range: 1% - 20%.
- **Fundamental diagram**: Empirical relation `Q(ρ)` or `v(ρ)` linking flow (or speed) to density
- **Density (ρ)**: Vehicles per unit length (veh/km or veh/m)
- **Flux / flow (Q)**: Vehicles passing a cross-section per unit time (veh/h or veh/s)
- **Spacing (s)**: Bumper-to-bumper distance between follower and leader
- **Headway**: Either time headway (time between consecutive vehicles passing a point) or distance headway (space between consecutive vehicle positions)
- **Time headway**: `h = s / v` — the typical value for safe following is 1.5 s; safety regulations usually recommend 2.0 s
- **Greenshields**: The simplest linear speed-density model [66]
- **Daganzo triangular FD**: The piecewise-linear fundamental diagram used in the Cell Transmission Model [31, 67]
- **CTM**: Cell Transmission Model — discrete Godunov scheme for LWR [67]
- **IDM**: Intelligent Driver Model [17]
- **OVM / OV**: Optimal Velocity Model [18]
- **FVDM / FVD**: Full Velocity Difference Model [157]
- **FollowerStopper**: The Stern-Cui-Seibold velocity-controlling AV policy [5]
- **PIS / PI with saturation**: Alternative velocity controller in the Stern line [5]
- **Flow (framework)**: The Python/SUMO RL environment for mixed-autonomy traffic [6, 7, 11]
- **CIRCLES**: The Berkeley-Vanderbilt-Arizona consortium running the I-24 field experiments
- **MVT**: MegaVanderTest — the 100-AV I-24 field test of November 2022 [13]
- **I-24 MOTION**: The Nashville instrumented freeway dataset [14]
- **NGSIM**: Next Generation Simulation trajectory dataset (US-101 and I-80) [60, 203]
- **highD**: German drone-based highway trajectory dataset [59]
- **VSL**: Variable Speed Limit — eulerian freeway speed harmonisation [107, 108, 109, 205]
- **LWR**: Lighthill-Whitham-Richards first-order kinematic-wave model [24, 25]
- **ARZ**: Aw-Rascle-Zhang second-order macroscopic traffic model [22, 23]
- **Hopf bifurcation**: The bifurcation at which the uniform traffic state loses stability to periodic jamiton-like solutions (delay-DDE analysis of OV) [50, 51]
- **Cut-in**: A lane-change into the gap ahead of the ego vehicle; a dominant disturbance source in mixed-autonomy freeway settings [48, 156]

---

## 11. MegaVanderTest summary

[From Lee et al. 2024 [13], Gloudemans 2023 [14], and associated CIRCLES reports]

- **Date**: November 14-18, 2022 (Mon-Fri)
- **Location**: Interstate 24, southeast Nashville, TN
- **Test section**: ~4 miles of I-24, 4-5 lanes per direction
- **Time of day**: ~5:00 - 10:30 AM (morning rush)
- **Vehicle count**: 100 controlled vehicles (AVs)
- **AV makes/models**: Nissan Rogue, Toyota RAV4, Cadillac XT5 (all ~2020-2022 production)
- **Control method**: Research controller overrides cruise control; longitudinal only (no lane change decisions)
- **Controllers deployed**: FollowerStopper-family and RL-trained policies from Flow [5, 10, 13]
- **Background traffic**: normal morning commuter traffic (on the order of ~4000-6000 veh/h total across lanes)
- **Penetration rate achieved**: ~3-5% at any given time (100 AVs / ~2000-3000 concurrent vehicles in the test zone)
- **Instrumentation**: I-24 MOTION provides per-vehicle trajectories of *all* vehicles at ~10 Hz [14]
- **Metrics**: aggregate fuel consumption of AVs and surrounding vehicles, mean velocity, wave amplitude and frequency, throughput, headway distribution

### Reported results (preliminary / under publication)

- **Qualitative**: One AI-equipped vehicle can influence the speed and driving behaviour of up to ~20 surrounding cars [13, 224]
- **Fuel savings**: not yet finalised in peer review; order-of-magnitude: ~4-10% on affected traffic bands, considerably less than the 40% seen on the controlled ring
- **Wave statistics**: Zhao et al. [85] provides the kernel-based wave identification pipeline; preliminary results show measurable reduction in wave frequency during controller-active periods
- **Operational findings**: Lane changes by non-AV vehicles routinely reduced the effective headway the AV could maintain; the longitudinal-only intervention is challenged by the multilane lane-change dynamics

### Known limitations

- Penetration rate was set by the logistics of running 100 research vehicles, not by the theoretically minimum effective value
- The test section is long enough to observe waves but short enough that upstream waves can enter the section from outside
- Controller hardware was the production vehicle's cruise control stack, which has inherent actuator limits
- Single-lane ring-road results do not translate directly; the multilane freeway is fundamentally a different regime

---

## 12. I-24 MOTION dataset summary

[Gloudemans et al. 2023 [14], Gloudemans 2023 virtual trajectories [15], Zhao et al. 2023 [85]]

### Physical infrastructure

- **Location**: Interstate 24, southeast Nashville, TN, USA
- **Length**: ~4.2 miles (6.5 km) of mainline freeway
- **Lanes**: 4-5 per direction (variable)
- **Camera count**: 276 pole-mounted high-resolution cameras
- **Coverage**: seamless (overlapping fields of view ensure no gaps in trajectory continuity)
- **Sample rate**: ~10 Hz (10 frames per second), though exact frame rate varies with camera and lighting
- **Total traffic volume covered**: >3.29 million vehicle trajectories over 40 hours of processed data in the canonical 2024 release
- **Vehicle types**: cars, trucks, buses, motorcycles, all commingled traffic

### Data products

- **Raw trajectory dataset** (INCEPTION v1.0.0): per-vehicle 10 Hz position over the full 4.2-mile section
- **Virtual trajectory dataset** [15]: a derived product giving trajectories on a virtual straight segment, useful for Lagrangian analysis
- **Wave-labelled subsets** [85]: stop-and-go wave regions identified by kernel-based clustering
- **Noise-aware generative simulator** [210]: calibrated to match the empirical trajectory noise of I-24 MOTION

### Known quirks

- **Occlusions**: despite the overlap, certain weather conditions (heavy rain, fog) and certain traffic configurations (tight platoons of trucks) can cause short track breaks that are re-stitched by the processing pipeline
- **Lane assignment**: lane identity is inferred from position; at off-ramp gores and lane lines the assignment can be ambiguous for a short time
- **Coordinate system**: the freeway has curvature, so a "virtual straight" projection is typically used for Lagrangian analysis [15]
- **Edge effects**: vehicles entering and leaving the monitored region create incomplete trajectories at the boundaries
- **Sampling rate consistency**: actual frame rate can drift slightly from 10 Hz; interpolation to a uniform 10 Hz grid is common practice before analysis
- **Calibration dates**: the camera calibrations are periodically updated, and trajectories near a recalibration may have slight offsets

### For HDR

- The dataset provides the ground-truth distribution of `(ρ, v, q)` on a real freeway, including the wave statistics. This is the target distribution for any HDR-trained policy.
- The dataset provides the noise and heterogeneity profile needed to build realistic synthetic scenarios in Flow/SUMO.
- The dataset is the empirical reference point for the minimum-penetration-rate question: any HDR claim about minimum penetration must either be demonstrated on an I-24-MOTION-calibrated simulator or evaluated against the MegaVanderTest data.

---

## 13. Baseline numbers HDR should not redundantly rediscover

- **Ring-road instability threshold (Sugiyama 230 m, 30 km/h target)**: 22 vehicles [1]
- **Minimum penetration for wave dissipation on a ring (single AV, FollowerStopper)**: ~5% [4, 5]
- **Minimum penetration for wave dissipation on an open straight network (RL, Flow)**: ~10% full, ~2.5% partial [9]
- **Stop-and-go wave propagation speed**: -15 km/h backward [29, 160, 161]
- **IDM standard parameters for highway**: v0=33 m/s, T=1.5 s, s0=2 m, a=0.73 m/s², b=1.67 m/s², δ=4 [29]
- **Commercial ACC systems are string-unstable**: empirically demonstrated across 7 models, 2018 [16]
- **Fuel savings from wave dissipation**: ~40% on the ring; ~5-10% on real freeway (less because the uncontrolled baseline has less wave content to remove) [4, 13, 103]
- **ACC/CACC penetration required to affect capacity**: 40%+ [41, 42, 43]
- **Purpose-built suppression controller penetration required**: 2.5-10% [4, 9, 12]
- **Minimum time gap for string-stable ACC with delay 0.4 s**: h > 0.8 s [88]
- **Capacity drop at bottleneck breakdown**: 5-15% of peak flow [62, 144]
- **Typical backward wave slope for passenger cars**: w ≈ 15-20 km/h [31, 67, 160]

---

## 14. Documented failure modes

- **Stock ACC worsens phantom jams in dense traffic** because all seven tested commercial systems are string-unstable [16]
- **FollowerStopper on a multilane freeway is vulnerable to cut-ins**: a longer-gap AV invites lane changes from adjacent lanes which seed fresh disturbances [48, 83]
- **RL policies overfit to training density**: a policy trained at one density may not suppress waves at another [114, 115]
- **High-penetration CACC does not help proportionally**: beyond ~50% penetration the returns diminish because the remaining human drivers set the worst-case disturbance [41, 43]
- **Pure longitudinal control cannot address lane-change-seeded oscillations**: documented in Laval-Leclercq [48] and reviewed in He et al. 2025 [83]
- **Reaction-time delay reduces the stability margin**: as shown analytically by Jin-Orosz [52, 53] and Molnar et al. [137]

---

*End of knowledge base.*
