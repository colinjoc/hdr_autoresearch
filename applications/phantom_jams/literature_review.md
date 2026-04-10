# Literature Review: Phantom Highway Traffic Jams and Their Suppression by a Small Fraction of Controlled Vehicles

## Phase 0 Deep Literature Review
**Date:** 2026-04-09
**Scope:** The self-sustained stop-and-go wave ("phantom jam" or "jamiton") on a homogeneous highway, and the question of whether a handful of longitudinally controlled vehicles — Automated Vehicles (AVs), Connected Automated Vehicles (CAVs), or Adaptive Cruise Control (ACC) units — can dissolve these waves in realistic traffic.

References below cite paper IDs from `papers.csv` in this directory.

---

## 1. The puzzle: why does flow break down without any obstacle

On a homogeneous, unobstructed highway at sufficient density, the uniform-flow equilibrium in which every car travels at the same speed with the same headway is dynamically unstable. Small perturbations — a driver hitting the brake slightly, a momentary loss of attention, a lane-change disturbance — amplify along the line of following vehicles until they grow into genuine stop-and-go waves. These waves then travel backward (relative to traffic) at a nearly universal velocity of roughly minus fifteen kilometres per hour and can persist for tens of minutes on a single lane [1, 26, 27, 160, 161]. The central puzzle is that the waves do *not* require any external trigger: no crash, no merge, no on-ramp, no obstacle, no lane closure. The mechanism is purely a driver-intrinsic instability of the following dynamics [1, 18, 50].

The earliest theoretical picture is Lighthill, Whitham and Richards [24, 25]: a first-order fluid conservation law `∂ρ/∂t + ∂Q(ρ)/∂x = 0`, with a concave flow-density relationship `Q(ρ)`. This LWR model predicts shocks and rarefactions but cannot produce spontaneous instability starting from a uniform state — a uniform profile remains uniform. The resolution came from second-order macroscopic models in the Aw-Rascle-Zhang (ARZ) family [22, 23, 175], which add a second equation for a "traffic pressure" that can destabilise uniform flow within a range of densities. Flynn, Kasimov, Nave, Rosales and Seibold [26] then showed that the same ARZ equations admit travelling-wave solutions — named *jamitons* — whose structure is mathematically analogous to detonation waves in reactive gas dynamics, complete with a sonic point, an attached relaxation zone, and a characteristic propagation speed. Jamitons are dynamically attracting: traffic that starts close to a uniform state but inside the unstable density band tends to a jamiton-populated configuration in finite time [26, 27, 141, 142, 189].

At the microscopic level, the instability lives in the car-following model (CFM). If every driver reacts to the car in front through an acceleration law `a_i = f(v_i, Δv_i, s_i)`, then the uniform solution `(v*, 0, s*)` is linearly stable against platoon perturbations only when a strict inequality between the partial derivatives of `f` holds. The condition is spelled out by Wilson and Ward [37] and, in book form, by Treiber and Kesting [29]. The two workhorse CFMs — the Optimal Velocity model of Bando, Hasebe, Nakayama, Shibata and Sugiyama [18] and the Intelligent Driver Model of Treiber, Hennecke and Helbing [17] — both violate this condition over a realistic range of densities when parameterised to match human data, so uniform flow spontaneously breaks down into jamitons in both simulation and experiment. Gipps [19], Wiedemann [20], Newell [21], and Jiang-Wu-Zhu's Full Velocity Difference Model [157] round out the list of standard CFMs, each with slightly different stability diagrams but the same qualitative behaviour.

Kerner's three-phase theory [34, 35, 146, 147, 149] is a distinct school: it splits congested traffic into a *synchronized* phase (dense but moving) and a *wide-moving-jam* phase (sharply bounded by backward-propagating wave fronts), and holds that breakdown is fundamentally the free-to-synchronized (F → S) transition, which is a different mechanism than the jamiton lens. The ARZ/jamiton and Kerner/three-phase accounts disagree on the identity of the instability but agree on its empirical consequences — the stop-and-go waves and backward-propagating fronts that HDR must ultimately suppress.

---

## 2. Empirical history: Sugiyama ring → I-24 MOTION → MegaVanderTest

For decades the phantom jam was a theoretical prediction supported by indirect loop-detector evidence: scatter in the fundamental diagram, capacity drops, empirical wide moving jams [62, 63, 64, 147, 148, 150, 160]. The decisive experimental confirmation came from Sugiyama, Fukui, Kikuchi and colleagues in 2008 [1]. They placed 22 drivers on a 230-metre circular track, asked them to maintain a target speed of 30 km/h with a safe distance, and watched the system break down from free flow to a stop-and-go wave entirely on its own. The critical density sat between 21 and 22 vehicles on the ring. The paper became the canonical existence proof: spontaneous stop-and-go waves are real, happen without any bottleneck, and can be reproduced on demand. Tadaki and co-authors' 2013 follow-up [2] extended this to larger rings and more participants, confirming that the free-to-jam transition has the character of a dynamical phase transition, and estimating the fundamental diagram across the transition. Nakayama et al. [3] and Jiang et al. [128] reproduced the effect in different contexts, the latter with 25 cars on a 3.2 km test track in China.

Almost a decade after the Sugiyama experiment, Stern, Cui, Delle Monache and collaborators [4] rebuilt the 22-vehicle ring with a crucial twist: one of the vehicles was now instrumented, computer-controlled, and running either a FollowerStopper or a PI-with-saturation controller designed and analysed in Cui, Seibold, Stern and Work [5]. When the human drivers were left to their own devices the wave was consistently recreated. When the controlled vehicle was activated, the wave was eliminated. Fuel consumption across the ring dropped by approximately forty per cent and effective throughput rose by about fifteen per cent [4, 103]. This is the most important empirical result in the field: a *single controlled vehicle among twenty humans*, a penetration of roughly five per cent, can dissipate an entire phantom jam.

The Stern experiment did not settle the operational question, though. A ring is not a highway. Its boundary is periodic, its density is conserved, and its single lane is not realistic. The Berkeley-Vanderbilt-Arizona CIRCLES consortium (Congestion Impacts Reduction via CAV-in-the-loop Lagrangian Energy Smoothing) was founded in 2019-2020 to move the result to an open highway. The CIRCLES effort required two new pieces of infrastructure. The first was I-24 MOTION [14, 15], a 4.2-mile segment of Interstate 24 in southeast Nashville instrumented with 276 pole-mounted high-resolution cameras providing continuous vehicle-level trajectories at ~10 Hz. This is the first highway test-bed in the world with *every* vehicle's Lagrangian trajectory recorded in a contiguous region large enough to cover multiple jamiton wavelengths. The second was the hardware and software stack for running a hundred production sedans (Nissan Rouge, Toyota RAV4, Cadillac XT5) simultaneously with a research controller overriding their cruise control [13].

The MegaVanderTest (MVT) was carried out between the 14th and 18th of November 2022 during the morning rush hour. A hundred AVs were driven into the normal flow of I-24 traffic, with the research controllers active for approximately five and a half hours per day over five days. Penetration rates varied throughout the experiment but stayed in the 3-5 per cent range by design. Lee, Wang, Jang, Lichtle and collaborators [13] describe the methodology, controller selection, and operational realities. The raw I-24 MOTION trajectory dataset is processed through a kernel-based wave identification pipeline in Zhao et al. [85], which provides the cleanest available ground truth on pre- and post-intervention wave statistics.

The MVT is the first mixed-autonomy field test on a real freeway. The headline numbers reported in media coverage and the associated technical papers [13, 103, 224] indicate measurable impact on surrounding traffic: one AV can influence the speed and headway of up to twenty trailing human drivers, and the overall fuel savings in affected bands of traffic are non-trivial. Formal peer-reviewed results are still being published as of 2026, and the field is actively processing the data with modern trajectory-level tools [85, 86, 210]. The critical thing for HDR is that the MVT provides the second piece of the minimum penetration rate picture: it demonstrates that the 5-per-cent Stern result at least *partially* survives the transition from a ring to a freeway.

---

## 3. Car-following models and string stability theory

A car-following model is the equation of motion `ẋ_i = v_i, v̇_i = f(v_i, Δv_i, s_i)` that governs one vehicle's response to the one directly in front. Different choices of `f` produce different stability diagrams, different fundamental diagrams, and different jamiton shapes. The four models HDR must be able to run are:

1. **Optimal Velocity (OV) model** [18]: `v̇_i = a (V(s_i) - v_i)` where `V(s)` is a monotone target-velocity function of the gap `s`. Stability requires `V'(s*) < a/2`, which is easy to violate on a ring with a smooth `V`.
2. **Intelligent Driver Model (IDM)** [17]: the acceleration is `a (1 - (v/v0)^δ - (s*(v, Δv)/s)^2)` with `s*(v, Δv) = s0 + v T + v Δv / (2 sqrt(a b))`. Six physically meaningful parameters (`v0, T, s0, a, b, δ`). Unstable in the density range where `Q(ρ)` is concave-down relative to its inflection.
3. **Gipps** [19]: a collision-avoidance safe-stopping speed chosen from maximum acceleration and desired braking, guaranteeing collision-freeness and producing slightly sharper queue profiles than IDM.
4. **Full Velocity Difference (FVD)** model [157]: OV + a relative-velocity term. More stable than pure OV on a ring.

In the Berkeley/CIRCLES line, IDM and OV are the default human-driver models, calibrated against NGSIM or ring-experiment data [17, 20, 21, 61, 121, 154, 140].

*String stability* is the property that a perturbation applied to the first vehicle in a chain does not amplify as it propagates down the chain [36, 37, 38, 39, 124, 125, 212, 222]. Swaroop and Hedrick [36] gave the original L∞ definition for linear unidirectional platoons. Wilson and Ward [37] and Feng et al. [212] provide modern unified statements and cover both L2 and L∞ variants. Ploeg, van de Wouw and Nijmeijer [124, 125] gave H-infinity synthesis conditions for CACC-type controllers with provable string stability.

The frequency-domain criterion is: writing `Γ(jω) = V_i(jω)/V_{i-1}(jω)` for the velocity transfer from leader to follower under linearised dynamics, L2 string stability requires `|Γ(jω)| ≤ 1` for all `ω ≥ 0`, and L∞ string stability is the sup-norm analog. For ACC with time-gap-based spacing policy and a leader-acceleration-only measurement, string stability can only be achieved with a time gap above a critical value (typically ~1.0-1.4 s depending on the specific dynamics) [88, 40, 42]. Below that gap, the ACC is string-unstable and amplifies disturbances — which is exactly what Gunter, Gloudemans, Stern, Work and collaborators [16] found in their 2018-19 experimental campaign: *every* commercial ACC system they tested was string-unstable. Their six-mph test disturbance grew to a twenty-five-mph disturbance along a seven-car platoon. This result is crucial context: *deploying more commercial ACC with stock settings would make phantom jams worse, not better*.

CACC — ACC augmented with V2V communication of leader acceleration — recovers string stability at smaller time gaps, and the PATH field experiments of Milanés and Shladover [40, 99] demonstrated this with production-quality hardware on a four-car platoon on a closed track. Cooperative vs non-cooperative ACC is the second axis HDR must consider.

An important subtlety exposed by Monteil, Bouroche and Leith [38], Monteil-Bhouri-Billot-El Faouzi [127], and Sau-Monteil-Billot-El Faouzi [126] is that in mixed heterogeneous traffic the question is *not* whether the AV itself is string-stable, but whether the *mixed* platoon containing the AV is string-stable as a whole. This is a non-trivial distinction: an AV can be individually string-unstable (and cope fine when following a smooth leader) while still stabilising a mixed chain, or vice versa. The HDR loop needs to evaluate the correct quantity: the mixed-system L2 and L∞ norms over disturbance bandwidths relevant to real stop-and-go waves (typically 0.05 - 0.5 Hz).

---

## 4. Controller families: FollowerStopper, PI-with-saturation, ACC/CACC, RL-trained

The Stern-Cui-Seibold line of work produced the first controllers designed specifically for phantom-jam suppression. FollowerStopper, introduced in Cui et al. [5] and refined in Bhadani et al. [217], is a model-free controller that specifies a desired velocity as a piecewise function of the leader distance and relative velocity: the AV targets a soft *command* velocity, equal to the driver's desired free-flow speed `U`, unless the measured gap to the leader falls into one of three thresholded regions, in which case the command is reduced. The controller is designed so that the AV never catches the wave at its trailing edge, but also never lets the gap grow without bound; the intuition is "drive smoothly at `U` unless the traffic ahead is getting dangerously close, in which case slow down *before* you have to brake hard". The second family, PI-with-saturation (PIS), uses integral feedback on a running average of the front car's velocity with saturation limits, producing a controller that tracks the mean flow even when the instantaneous leader is oscillating [5]. Both FollowerStopper and PIS are simple enough to be implemented on production hardware and were the controllers used in the Stern 2018 ring experiment.

The controllers evaluated on real I-24 traffic during the MegaVanderTest are documented in Lee et al. [13]. They include variants of the FollowerStopper family with adaptive desired velocity, micro-level safety wrappers [218], and reinforcement-learning-trained policies from the Flow/RL line.

RL-based controllers enter via the Flow framework [6, 7, 8, 9, 10, 11, 12, 114, 115, 179, 198, 199, 211]. Wu, Kreidieh, Parvate, Vinitsky and Bayen developed Flow as a SUMO-based modular RL environment where the action is the acceleration of the controlled vehicle(s), the observation is some subset of the local traffic state, and the reward is typically a combination of mean velocity and instantaneous flow with negative penalties on headway violations. On the Sugiyama-style ring, a single RL-trained AV at 5 per cent penetration matches or exceeds FollowerStopper performance and additionally learns emergent behaviours such as exploiting a smaller-than-human safe gap to push the equilibrium velocity above its theoretical bound [10]. On open straight highways with 10 per cent penetration, Kreidieh, Wu and Bayen [9] reported near-complete wave dissipation; even at 2.5 per cent they found measurable reduction in wave frequency.

Chou, Bagabaldo and Bayen [12] ("The Lord of the Ring Road") is the most systematic controller comparison available: they benchmark ten published AV control policies (FollowerStopper, PI-saturated, LQR variants, MPC variants, and RL variants) on a single ring under matched conditions. Their headline finding is that *distribution* of AVs around the ring matters less than expected, *penetration* matters more, and *the RL controller is the most consistently effective across regimes*.

MPC-based controllers are a distinct family, represented by Wang, Daamen, Hoogendoorn and van Arem [89, 90], Dunbar and Caveney [93], and others [91, 92, 208]. They cast the vehicle-level control problem as a receding-horizon optimal control and handle input/state constraints naturally. The cost of MPC is computational; the benefit is explicit safety constraints and easy adaptation to changing leader dynamics.

Finally there is a theoretical line based directly on the PDE model: Delle Monache and Goatin [77], Garavello, Goatin, Liard and Piccoli [76], Delle Monache, Liard, Piccoli, Stern and Work [78], and Chiarello, Piccoli and Tosin [79] treat the AV as a moving constraint on the flux of the underlying LWR or ARZ system, and derive existence and stabilisation results analytically. Hayat, Piccoli and Truong [80] push this further with Lyapunov-based controller synthesis with provable closed-loop stability for ARZ. These results provide *analytical* lower bounds on the AV penetration required for macroscopic stabilisation [81, 213, 220, 221], which complement the numerical bounds coming out of the Flow/RL experiments.

---

## 5. The minimum penetration rate question

The central quantitative question HDR is positioned to answer is: *what is the smallest fraction of controlled vehicles that can dissipate phantom jams on a realistic highway, and how does that fraction depend on density, demand, controller family, noise in human driving, and lane-change coupling?*

The existing empirical numbers, compiled from the papers above:

| Source | Setting | Reported minimum penetration | Notes |
|---|---|---|---|
| Stern 2018 [4] | 22-car ring | 5% (1/22) | FollowerStopper / PI-saturated; complete dissipation |
| Kreidieh 2018 [9] | Closed + open straight Flow environments | 2.5% - 10% | 10% for near-complete dissipation; 2.5% detectable |
| Chou 2022 [12] | Ring road benchmark | 5-10% for RL; higher for classical | Distribution largely irrelevant |
| Schakel 2010 [43] | Macroscopic sim | ~50% | CACC, no dedicated controller |
| Shladover 2012 [41] | Microscopic sim | 40%+ | CACC capacity gain becomes material |
| Wu 2017 [213] | Theoretical | Depends on human CFM parameters | Analytical lower bound |

The two clusters are striking. Classical ACC/CACC requires 40-50 per cent penetration before it materially changes traffic flow [41, 43, 44]. Purpose-built phantom-jam controllers work at roughly a tenth of that — 2.5-10 per cent [4, 9, 12]. The difference lies entirely in the controller objective: ACC is designed to follow the car in front, CACC to follow the car in front with V2V communication, and *neither* has a mandate to suppress upstream oscillations. A FollowerStopper or RL-trained controller has that mandate built in: it actively chooses to smooth its own velocity profile even at the cost of occasionally running a large gap [5, 10, 12]. This distinction is a key HDR observation: the *design objective* of the longitudinal controller, not the AV fraction per se, is what determines the minimum penetration.

Several open questions remain. First, all the minimum-penetration results above are for single-lane or minimally-multilane scenarios. On a real freeway with frequent lane changes [48, 164, 165, 196, 209], disturbances can be seeded by lane-change maneuvers that the longitudinal controller does not see coming. The 2504.11372 review [83] explicitly compares the Lagrangian and Eulerian (VSL) suppression paradigms and argues that lane-change seeding may make pure longitudinal AV control insufficient. Second, the minimum rate depends on the human driving model. With an IDM-like model at realistic noise [140], the wave growth rate is slower than with a pure OV model, and the required AV fraction is correspondingly lower. Third, the penetration question interacts with spatial distribution of AVs. Chou et al. [12] report that distribution matters less than expected on a ring, but this may not hold on a freeway with heterogeneous lane loadings. Fourth, controller robustness under communication dropout, sensor delay, and noise [52, 53, 137, 187] degrades the achievable penetration floor.

---

## 6. Simulation frameworks: SUMO, Flow, ring-road testbeds

The default simulation environment for phantom-jam research is now Flow [6, 7, 8, 11, 211], built on top of SUMO [56, 57, 58]. Flow is a Python wrapper that exposes SUMO as a Gymnasium environment: at each step the agent observes a user-configured slice of vehicle state (typically velocities and headways of the ego vehicle and its neighbours), outputs accelerations, and receives a reward. The benchmarks published with Flow [8] include four canonical scenarios — single-lane ring, figure-8 intersection, on-ramp merge, and a closed-loop bottleneck — with baselines for PPO, TRPO, DDPG, TD3 and SAC from the standard RL literature [70, 71, 72, 73, 74]. The ring road in Flow is the single most important benchmark for phantom-jam suppression because it maps cleanly onto the Sugiyama experiment and admits analytical stability checks.

SUMO itself uses IDM or Krauss as default CFMs [56, 130, 131]. IDM's stability diagram matches human ring-experiment data reasonably well but the behaviour is sensitive to the choice of the desired time gap `T` and maximum acceleration `a` [61, 121, 140]. Flow provides parameter overrides for these so that phantom jams form reliably in the ring environment at densities around 20-22 vehicles per kilometer. The noise-aware extension of SUMO used in the I-24 MOTION project [210] adds stochastic perturbations calibrated to match the observed trajectory statistics on I-24.

Alternatives to SUMO/Flow include CityFlow (faster but less realistic), PyTSC, the LightSim cell-transmission-model simulator, and the Flynn-Seibold jamiton simulators for ARZ-level questions [26, 27]. Since HDR wants a microscopic picture with AV insertion and a realistic lane-change model, Flow on SUMO is the appropriate environment.

Two important *testbeds*, as opposed to simulators, complete the picture. The University of Delaware scaled city is a 1:25 scale physical miniature highway with real autonomous robots driving under an RL policy; Jang et al. [102] used it to demonstrate zero-shot sim-to-real transfer of a Flow-trained policy. The I-24 MOTION instrument [14, 15, 85, 86, 210] is the other end of the spectrum: a full-scale uninstrumented (from the driver side) freeway where CAVs can be inserted into normal traffic. For HDR the simulator is where the policy is trained, the scaled city is where it can be tested cheaply, and I-24 MOTION is where the evaluation trajectories come from.

---

## 7. Energy and safety trade-offs of wave suppression

Suppressing stop-and-go waves is attractive for two reasons beyond driver comfort. The first is energy. Kesting and Treiber [45, 46, 155] derived and simulated the energy cost of stop-and-go patterns using vehicle dynamics models; Stern et al. [4, 103] measured it directly on the ring (40 per cent fuel reduction and significant NOx reduction on gasoline engines when the wave is removed). Lee et al. [13] report similar order-of-magnitude numbers for the MegaVanderTest. The energy benefit comes from two channels: the elimination of the deep minimum speed (and therefore the high-acceleration phase that follows it) and the smoothing of the acceleration profile over time, which pushes the engine operating point into a more efficient region. The latter dominates at normal highway speeds.

The safety question is more subtle. On one hand, suppressing waves reduces the number of sharp braking events, which reduces the probability of a rear-end collision — the single most common crash type on congested freeways. On the other hand, every AV controller that achieves wave suppression must at some point run with a *longer* than-equilibrium gap, because that is how it absorbs the upstream disturbance. A larger gap invites cut-ins from the adjacent lane, and a cut-in is itself a disturbance; Laval and Leclercq [48] and Zheng et al. [49] documented this effect empirically. A pure longitudinal-only controller can therefore be out-manoeuvered by the lane-change dynamics it does not control. The HDR loop must track this: the headway distribution and the time-to-collision distribution of the AV and its neighbours are as important as the aggregate wave statistic.

Safety wrappers are beginning to appear around learning-based AV controllers [218]. They typically enforce a minimum time-to-collision, a maximum deceleration, and sometimes a check on relative velocity before releasing the controller's nominal action. The headline evidence [95, 96, 181, 182] is that human reaction times have a heavy tail and the safety wrapper should be designed against the tail, not the mean.

---

## 8. Open questions (2024-2026)

Much of the post-MegaVanderTest literature is devoted to picking apart what worked, what did not, and what the minimum penetration number actually is in the field. A non-exhaustive list of what remains unsettled as of early 2026:

1. **What is the minimum penetration rate on a real freeway, accounting for lane changes?** The ring gives 5%. Flow in closed-loop gives 2.5-10%. The MegaVanderTest operated at 3-5% and observed *partial* suppression. The gap between theoretical rings and real freeways is not fully closed [83, 224].

2. **Is the VSL vs Lagrangian choice a dichotomy or a complementarity?** He et al. [83] argue they are competing paradigms. Čičić and Johansson [220, 221] argue the AV moving-bottleneck picture is a bridge between them. The HDR project has the opportunity to test both in the same simulator, which no published work has done at a single fair comparison.

3. **How robust is the minimum penetration to the human driving model?** Almost all minimum-penetration numbers are computed with IDM or OV. Kerner-Klenov three-phase CFMs [149] give qualitatively different predictions. This uncertainty should be explicit in the HDR output.

4. **Do learned policies transfer across density regimes?** RL-trained policies can overfit to the specific density at which they were trained [114, 115]. Jang et al. [102] showed zero-shot transfer from simulation to a scaled city, but the density band was narrow.

5. **Can a small fraction of AVs also stabilise the *fundamental diagram* — i.e. recover the theoretical flow without scatter?** The set-valued fundamental diagram [27] is a direct empirical signature of jamiton presence. If HDR can produce a scatter-free fundamental diagram at a measured penetration, that is a new-to-literature result.

6. **What is the minimum-penetration-rate vs. sensor-information trade-off?** An AV with only its front-gap sensor can in principle implement FollowerStopper. With V2V it can implement CACC. With V2I and downstream density information it can implement VSL-like smoothing. The penetration rate likely scales inversely with information available [52, 53, 106, 215]. The HDR loop can make this trade-off curve quantitative.

7. **What is the effect of driver heterogeneity on the controller performance?** Monteil et al. [38, 127], Sau et al. [126] give partial theoretical answers. Empirical validation on I-24 MOTION or highD is missing.

8. **How much do RL-trained policies exploit the simulator's specific noise model?** Noise-aware generative simulation from I-24 MOTION data [210] is the relevant baseline; there is no published HDR-style test of this.

---

## 9. Implications for HDR

The existing literature gives HDR a clear foundation and a clear set of unanswered questions. The foundation is strong:

- The existence and qualitative structure of phantom jams are proven experimentally on a ring [1, 2, 128], theoretically via ARZ/jamiton analysis [26, 27, 189], and empirically on real freeways [147, 160, 161].
- The feasibility of suppression by a small AV fraction is proven on a ring [4, 5] and numerically in Flow [6, 9, 10, 12].
- Standard controllers (FollowerStopper, PI-saturated, LQR, MPC, RL) are documented and implementable [5, 12, 93, 214, 217].
- Two high-quality test-beds exist: the Flow ring environment on SUMO [6, 8, 11] and the I-24 MOTION dataset [14, 15].

The HDR loop can add value in several distinct directions:

- **Exhaustive exploration of the penetration-density phase diagram**. No single published work has mapped out the minimum penetration rate as a function of density, demand, CFM choice, noise level, and lane-change frequency. A HDR loop running PPO/SAC with systematically varied design variables is well-suited to producing this phase diagram.
- **Cross-CFM robustness testing**. The same controller trained on IDM human drivers, evaluated on OV/FVD/Kerner-Klenov drivers, with the full cross product of CFM pairs. Publishable result class.
- **Comparison of FollowerStopper-family, RL-family, and MPC-family at matched conditions**. Chou 2022 [12] did this on a ring; HDR can extend it to multilane open freeway scenarios that the literature has not covered at the same level of rigor.
- **Sensor/information ablation**. What is the minimum penetration when the AV has only front gap sensing vs. front + rear vs. full local state vs. V2V communication? This maps directly onto deployment cost.
- **Sim-to-I-24-MOTION transfer**. The noise-aware I-24 MOTION simulator [210] provides the target distribution; training a policy in Flow and evaluating it against the I-24 trajectory bank is a sim-to-real analogue without field access.
- **Lane-change-seeded disturbance suppression**. Most of the existing literature is on closed single-lane rings. HDR can explicitly target the multilane problem where the dominant disturbance source is no longer the OV instability but the lane-change manoeuvre [48, 164, 165, 196].

The minimum-penetration question is the "leading edge" HDR result: what is the smallest controlled fraction that suppresses phantom jams under realistic assumptions, and how does it scale with the design variables? The simulator and data infrastructure to answer this now exist. The remaining work is systematic exploration of the design space, which is exactly what HDR is designed for.

---

*End of literature review.*
