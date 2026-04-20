# Phase −0.5 Scope Check v3 (Round 3 of 3)

Reviewer: fresh sub-agent, no prior context. Inputs: `proposal_v3.md` and the Phase −0.5 section of `program.md`.

## 1. Novelty after pivot

The Crooks-ratio pivot plus n_eff gating plus pre-registered Gaussianity boundary is defensible but **narrow**. The pitch is no longer "we test the Langevin approximation" — it is "we measure, with pre-registered tolerances on an analytical testbed, the η at which the Jarque–Bera p-value crosses 0.01 and the η at which the Crooks work-distribution importance-sampler becomes uninformative." That is a *measurement paper*, not a theorem paper. Measurement papers have a legitimate home in JSTAT provided the testbed has an analytical reference — which Goldt–Seifert 2017 does supply.

Against the named comparators: Simsekli 2019 shows α-stability at large η but does not pre-register a p-value transition on a testbed with closed-form β; Panigrahi 2019 and Xie 2021 similarly do not commit to a specific η-grid and tolerance before measuring. The differentiation is real but thin — it lives almost entirely in the pre-registration and the analytical reference. Peng, Sun & Duraisamy 2024 is the bigger risk: if they already report Crooks-ratio linearity fits on an SGD testbed, v3 collapses to a replication. Phase 0 must verify.

**Verdict on novelty:** defensible as *measurement with pre-registered tolerances on an analytical testbed*, provided Peng et al. 2024 is not a near-duplicate. Not strong, but not synthesis-dressed-as-novelty.

## 2. Falsifiability

O1–O5 are binary and non-gamed. O1 has a clean "or unresolvable" clause which is honest rather than evasive. O3's 5 %-of-β tolerance is tight enough that passing it on noise is implausible at n_eff = 1000. O4 (intercept ≈ 0) is a genuine second constraint that a miscalibrated β cannot satisfy simultaneously with O3. O5 gives an external-transfer check.

The n_eff ≥ 1000 gate at n_traj = 10⁴ (10 % efficiency) is the key fix for F1. It directly prevents the heavy-tailed regime from passing the Crooks test on noise: when the importance weights collapse onto a few trajectories, the run is declared *uninformative*, not *passing*. This is the right mechanism. One residual concern: n_eff itself is stochastic and the 1000 threshold should carry a bootstrap tolerance (e.g. lower 95 % CI ≥ 1000), otherwise η values straddling the boundary will flip labels across seeds.

## 3. ΔF circularity

The Crooks ratio P_F(W)/P_R(−W) = exp(β W) contains no ΔF term — eliminated by construction. β enters as the slope of the log-ratio, so β = 1/T_SGD_GNS is tested rather than assumed. No circular reintroduction. M1 is resolved.

## 4. Venue fit

JSTAT primary is correct — exactly the class of controlled stochastic-thermodynamics validation they publish. PRE fallback is reasonable. The real risk is the opposite end: JSTAT may find a 50-dim quadratic plus one small MNIST too *thin*, not too broad. The "physics boundary measurement, not ML theorem" framing in §5 is the right defence.

## 5. Killer objections

- **(K1, major)** Peng, Sun & Duraisamy 2024 already did this. *Mitigation:* Phase 0 must locate and differentiate.
- **(K2, major)** n_eff threshold is itself seed-stochastic — pre-register bootstrap CI on n_eff, not the point estimate.
- **(K3, minor)** Scope thin for JSTAT — keep the physics-boundary framing.

VERDICT: PROCEED

