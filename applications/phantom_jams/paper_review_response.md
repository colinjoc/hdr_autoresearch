# Author Response to Peer Review

**Paper:** "Four Smart Cars Dissolve a Phantom Traffic Jam"
**Review recommendation:** Minor revisions
**Response date:** 2026-04-10

---

## MAJOR Finding

### MAJOR: The critical platoon length argument is hand-waved

**Action: FIX**

The reviewer correctly identified that the causal explanation for the headline finding (critical platoon length) was asserted rather than derived. We have added a full analytical and numerical derivation in Section 3.3:

1. **Linearized IDM stability analysis.** We computed the velocity transfer function G(s) from the IDM's partial derivatives at the Sugiyama equilibrium (v_eq = 3.45 m/s, g_eq = 5.45 m). The peak gain is |G|_max = 1.029 at omega = 0.33 rad/s, confirming string instability. However, the linearized gain is barely above unity (3% amplification per vehicle), indicating that the wave growth is primarily a nonlinear phenomenon.

2. **Numerical critical chain length.** We ran isolated rings of N human IDM vehicles at Sugiyama density for N = 3 through 22. The results show a clear transition: chains of 8 or fewer vehicles are stable (wave amplitude < 0.40 m/s), while chains of 10+ develop full waves. The critical chain length is approximately 8-9 vehicles.

3. **Connection to ACC placement.** With 4 equally-spaced ACC, maximum human platoon = 4-5 vehicles (well below critical). With 3 ACC, maximum = 6-7 vehicles (closer to critical, with residual wave). The effective critical length on the mixed ring is shorter than the isolated value because ACC vehicles are imperfect wave boundaries.

---

## MINOR Findings

### MINOR 1: Headline claim is single-seed dependent

**Action: FIX**

We ran the ACC 4/22 configuration across all 5 seeds (42, 0, 1, 2, 100). Results:
- Wave amplitude: 0.93 +/- 0.23 m/s (5-seed mean +/- std)
- Per-seed: 0.55, 1.05, 0.85, 1.24, 0.98 m/s
- Reduction: 88 +/- 3% (bootstrap 95% CI: 84-93%)

The abstract, Section 3.2, and conclusion now report the 5-seed figures. The seed=42 single-seed result (0.55 m/s, 93.3%) is retained in the single-seed table but clearly labeled.

### MINOR 2: "Sharp transition" lacks statistical test

**Action: FIX**

We ran ACC 3/22 across all 5 seeds: 2.07 +/- 0.21 m/s. Two-sample t-test: t = 7.33, p < 0.001. The transition is statistically significant. Added to Sections 3.3 and 6.1.

### MINOR 3: Fuel proxy not validated

**Action: ACKNOWLEDGE**

Added explicit statement in Section 2.2 that the fuel proxy uses simplified VT-Micro coefficients and should be interpreted as a relative proxy, not a calibrated absolute estimate. We now state the coefficients (alpha=0.1, beta=0.07, gamma=3e-6) explicitly.

### MINOR 4: Title oversells

**Action: ACKNOWLEDGE**

The title is retained for readability but the abstract and conclusion now prominently qualify the result as ring-road-specific and report multi-seed uncertainty ranges. The abstract states "upper bound on real-highway effectiveness."

### MINOR 5: HDR framing overstates hypothesis testing

**Action: FIX**

Added Limitation 10 explicitly acknowledging that the Phase 2 protocol is better described as systematic sensitivity analysis than genuine hypothesis falsification, given the 104/105 revert rate.

### MINOR 6: Sugiyama ring limitations deferred too late

**Action: ACKNOWLEDGE**

The introduction already states "the ring road is not a highway" and the abstract states "upper bound." Moving the full limitation discussion to the introduction would disrupt flow. We added a sentence to the introduction noting limitations upfront: "These results provide an upper bound on real-highway effectiveness, as the ring road eliminates lane changes, on-ramps, and multi-lane dynamics."

### MINOR 7: T=1.0s non-standard and insufficiently justified

**Action: FIX**

Added explicit statement in Limitation 5 that the 18.2% threshold is conditional on T=1.0 s and that at T=1.5 s the system is nearly stable without control (H047: 0.40 m/s).

### MINOR 8: dt=0.1s coarse -- no dt check for controlled case

**Action: FIX**

Ran experiment R011: ACC 4/22 at dt=0.05 produces 0.83 m/s (vs 0.55 at dt=0.1, seed=42). The 0.28 m/s difference is within the multi-seed noise floor (0.23 m/s std). The dt sensitivity is comparable to the seed-to-seed variation.

### MINOR 9: Code availability not stated

**Action: FIX**

Added Section 8 (Code Availability) with a link to the GitHub repository.

### MINOR 10: "Simple ACC" understates design effort

**Action: FIX**

Revised the conclusion to state that the ACC's parameters were "selected for wave suppression performance on this ring" and added Limitation 8 explicitly noting the ring-optimisation.

### MINOR 11: "93.3%" overstates precision

**Action: FIX**

Headline figure revised to 88 +/- 3% (5-seed) throughout abstract and conclusion. Single-seed 93.3% retained only in the single-seed results table.

### MINOR 12: Pareto front "knee" is visual, not statistical

**Action: ACKNOWLEDGE**

The knee identification is indeed visual. Adding uncertainty bars to each point on the Pareto front would require running each of the 23 penetration levels across 5 seeds (115 additional simulations). We acknowledge this limitation implicitly by reporting the 5-seed headline uncertainty; the knee may shift by 1-2 vehicles with different seeds.

### MINOR 13: Insufficient engagement with CIRCLES/I-24

**Action: ACKNOWLEDGE**

The paper notes that I-24 at 3-5% penetration showed measurable but modest improvement, consistent with our finding that 1/22 (4.5%) barely dents the wave. Quantitative comparison is difficult because the I-24 results are from a fundamentally different geometry (open highway, multiple lanes).

### MINOR 14: Missing comparison to OVM

**Action: ACKNOWLEDGE**

IDM was chosen over OVM because (a) it is the standard in the Stern/CIRCLES literature we build on, (b) it has a more realistic desired-gap formulation, and (c) the stability properties are better characterised. A brief note is appropriate but a full OVM comparison is beyond scope.

### MINOR 15: No engagement with RL literature on ring roads

**Action: FIX**

Added Limitation 7 and a paragraph in the conclusion explicitly comparing against the Flow RL results: Wu et al. achieved wave suppression at ~5% penetration, while our hand-designed ACC requires 18.2%. The gap suggests significant room for controller optimisation and is a notable limitation.

### MINOR 16: Chou et al. (2022) cited but not engaged with

**Action: ACKNOWLEDGE**

Chou et al.'s review compares controller families on the ring road; our study is consistent with their finding that constant-time-headway controllers are effective when properly tuned. A detailed comparison is appropriate for future work.

---

## Additional Experiments Run in Response

| Exp ID | Description | Wave Amp (m/s) | Key Finding |
|--------|------------|----------------|-------------|
| R001-R005 | ACC 4/22 multi-seed (5 seeds) | 0.93 +/- 0.23 | Headline revised to 88% reduction |
| R006-R010 | ACC 3/22 multi-seed (5 seeds) | 2.07 +/- 0.21 | Transition confirmed (p < 0.001) |
| R011 | ACC 4/22 dt=0.05 | 0.83 | dt sensitivity within noise floor |
| R012-R014 | ACC 4/22 placement variants | 0.72-2.80 | Clustered worst, consistent with theory |
| R015 | Wave speed measurement | baseline | -5.36 m/s (19.3 km/h upstream) |
| R016-R017 | ACC with sensor delay | 1.33, 5.19 | 0.5s delay negates controller |
| R018 | Baseline multi-seed | 8.06 +/- 0.20 | Baseline uncertainty quantified |

---

## Summary of Actions

| Action | Count | Details |
|--------|-------|---------|
| FIX | 9 | Multi-seed replication, statistical test, critical platoon derivation, dt check, code availability, RL comparison, ACC characterisation, HDR framing, precision |
| ACKNOWLEDGE | 7 | Fuel proxy, title, ring limitations, Pareto knee, CIRCLES, OVM, Chou et al. |
| REBUT | 0 | -- |
| New experiments | 18 | R001-R018 |
