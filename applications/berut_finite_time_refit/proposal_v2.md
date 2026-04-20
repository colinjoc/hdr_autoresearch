**Target**: publication — primary venue: Physical Review E, fallback venue: Journal of Statistical Mechanics: Theory and Experiment

# From optimal to realised: a first-principles prediction of the finite-time Landauer coefficient in the Bérut 2012 protocol

## 1. Question

The Schmiedl–Seifert / Proesmans finite-time Landauer formula ⟨*Q*_diss⟩(τ) = *k_B T* ln 2 + *B k_B T*/τ gives *B* = π² for the *optimal* overdamped symmetric protocol — a protocol that no experiment has ever implemented. Bérut et al. (2012) used a specific, non-optimal modulation of their optical double-well trap. What is the realised *B* for the Bérut protocol, predicted from first principles by direct Brownian-dynamics simulation of their actual experimental modulation? Does this first-principles prediction match the value fit empirically from their ten-point dissipation curve?

## 2. Proposed contribution

A first-principles comparison of predicted and measured *B* for a specific experimental protocol, closing a gap the field has acknowledged but never quantitatively tested:

**(a) Empirical *B* from the full Bérut curve.** Weighted nonlinear least-squares fit of ⟨*Q*_diss⟩(τ) = *k_B T* ln 2 + *B k_B T*/τ to the ten published Bérut points, with 95 % bootstrap confidence interval from the published Bérut ±0.15 *k_B T* per-point uncertainty. This has been cited but never performed in the literature; the Bérut paper itself fit only the quasistatic-limit point.

**(b) First-principles *B* from a Brownian-dynamics simulator.** Numerical integration of the overdamped Langevin equation in Bérut's reconstructed double-well potential *U*(*x*, *t*), with the specific time-dependent modulation used by Bérut (linear tilt ramp + barrier lowering, read off their Fig. 1c and SI). Ensemble-average ⟨*Q*_diss⟩(τ) computed stochastically over 10⁴ trajectories per cycle time, at the ten Bérut τ values. The resulting simulated *B*_Bérut is a pre-registered prediction: *either* it is consistent (to within both uncertainties) with the empirical fit from (a), *or* it is not.

**(c) Decomposition of the excess *B*_Bérut − π².** If (b) yields a simulated *B*_Bérut significantly above π², we decompose the excess into contributions from (i) protocol non-optimality (how far the Bérut modulation is from the Schmiedl–Seifert optimal protocol), (ii) detector bandwidth and photodiode nonlinearity, and (iii) any residual trap asymmetry. Each contribution is computed by turning that single factor off in the simulator and re-running.

**(d) The asymmetric extension is explicitly deferred.** The proposed asymmetric formula *B*(*r*) = π²(1+*r*)²/(4*r*) has vanishing derivative at *r* = 1, and the Bérut trap is near-symmetric. Any test of the asymmetric formula must use a dataset with genuinely asymmetric protocols — Gavrilov–Bechhoefer (2016, feedback-trap asymmetric potentials) or Chiu–Lu–Jun (2022, asymmetric optically-modulated traps) are the correct targets. We identify these datasets as the subject of a follow-up paper and explicitly state in this paper's §Methods that the Bérut dataset cannot resolve asymmetric *B*(*r*) by construction. The asymmetric formula remains listed as a prediction in §Discussion, not a tested claim.

## 3. Why now

Three specific developments:

- **The Bérut dataset has never been refit in the finite-time framework** — Proesmans, Ehrich & Bechhoefer (2020) derived the symmetric *B* = π² formula citing Bérut as motivation, but did not refit the ten-point curve. Eleven years of citations have passed.
- **Brownian-dynamics simulation of experimental protocols has become routine** — modern JAX/Numba stochastic integrators (e.g. `jax-sde`, `pychastic`) make first-principles prediction of ⟨*Q*_diss⟩(τ) for a specific experimental protocol a 100-line exercise, not a publication in its own right.
- **Phase 0 literature review of this project identified** that the gap between the optimal-protocol bound and any realised experimental value is *known* to the stochastic-thermodynamics community but has not been quantified for any specific experiment. Closing that gap for the Bérut landmark paper is a narrowly scoped, concretely publishable contribution.

## 4. Falsifiability

Three pre-registered, sharp, binary kill-outcomes — each a direct numerical comparison with a pre-specified tolerance:

- **Empirical fit validity.** The 95 % bootstrap CI on the fitted empirical *B* is either finite (the curve constrains *B*) or degenerate (it does not). Power analysis is reported before the fit.
- **Simulation–experiment consistency.** The simulated *B*_Bérut is either within 2 σ of the empirical CI or it is not. If not, we identify whether the discrepancy is explained by (i) protocol non-optimality, (ii) detector effects, or (iii) unaccounted physics (new result).
- **Relation to the optimal bound.** Simulated *B*_Bérut is either strictly ≥ π² (as required by the Proesmans bound being a *minimum*) or it violates the bound (which falsifies either the Proesmans derivation or our simulation).

## 5. Named comparators and differentiation

- **Proesmans, Ehrich & Bechhoefer (2020)** derived the optimal-protocol bound *B* = π². We do not extend that derivation. We test how far a realised experimental protocol sits above it.
- **Bérut et al. (2012)** — the source of the data and the protocol. They fit only the quasistatic limit.
- **Gavrilov–Bechhoefer (2016)** and **Chiu–Lu–Jun (2022)** are the correct datasets for testing asymmetric generalisations; we explicitly decline to treat them in this paper and flag them as the follow-up.
- **Dago–Ciliberto et al. (2021, 2022)** — recent logical-operation-based finite-time experiments. Complementary but different protocols; we use them as context, not substitutes.
- **Zhen–Chupeau et al. (2021)** — feedback-trap finite-time erasure with different optimisation target; also complementary.

This proposal's novelty claim is concrete: we are the first to (i) fit the full Bérut curve under the finite-time formula, (ii) predict *B*_Bérut from first-principles Brownian-dynamics simulation of the actual Bérut protocol, and (iii) attribute any excess over π² to specific protocol or detector effects.

## 6. Target venue

**Physical Review E** — publishes first-principles tests of stochastic-thermodynamics bounds against specific published experiments. The simulator + empirical-fit combination hits exactly PRE's "framework + data" category. Expected PRE objection: the Bérut supplementary's incomplete specification of the modulation shape (see the Phase 0 lit review's r-identifiability analysis) may require us to report bounds on the simulated *B* rather than a single number; we pre-commit to doing so.

**Fallback: J. Stat. Mech.** if the simulator turns out to be the main contribution and the refit ends up secondary.

## 7. Scope boundary — what this paper is NOT

- Not a new theorem. All the underlying bounds are pre-existing.
- Not a test of asymmetric-barrier extensions — those require Gavrilov–Bechhoefer 2016 / Chiu–Lu–Jun 2022 data, explicitly flagged as follow-up.
- Not a reinterpretation of Landauer. The quasistatic floor is unchallenged.
- Not a cross-substrate comparison — the killed `thermodynamic_cross_substrate` project tried that and failed scope check.
