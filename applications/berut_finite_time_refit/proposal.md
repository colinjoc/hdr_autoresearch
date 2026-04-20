**Target**: publication — primary venue: Physical Review E, fallback venue: Journal of Statistical Mechanics: Theory and Experiment

# Empirical refit of the finite-time Landauer coefficient from the Bérut 2012 colloidal bit-erasure dataset

## 1. Question

Does the finite-time Landauer coefficient *B* in the Schmiedl–Seifert / Proesmans formula ⟨*Q*_diss⟩(τ) = *k_BT* ln 2 + *Bk_BT*/τ, fit to the full ten-point Bérut et al. (2012) cycle-time-dependent dissipation curve, agree with the symmetric prediction *B* = π², with a proposed asymmetric generalisation *B*(*r*) = π²(1 + *r*)²/(4*r*) at the optical-trap asymmetry *r* extracted from the Bérut supplementary information, or with neither?

## 2. Proposed contribution

A single, narrowly scoped empirical test of a prediction that has not been verified against the data it was designed to explain. Three deliverables:

**(a) Empirical *B* fit.** The Bérut 2012 supplementary publishes ten (τ, ⟨*Q*_diss⟩) points. Fitting *k_BT* ln 2 + *Bk_BT*/τ to the full curve yields an empirical *B* with 95 % confidence bounds from bootstrap resampling of the published error bars. This fit has been cited but not performed in the published literature to our knowledge.

**(b) Identifiability of the optical-trap asymmetry *r*.** Before testing the asymmetric formula, we must establish that the Bérut trap *r* is extractable at useful precision from the published optical-trap parameters (well depths, trap stiffnesses, photodiode-measured barrier shape). Section §2 of the paper will be devoted entirely to this question: we will reconstruct the potential *U*(*x*) from the Bérut parameters, measure the well-depth asymmetry ratio *r* = *V*_left/*V*_right, and report *r* ± its propagated uncertainty. If *r* cannot be pinned down at better than factor-2 precision, the asymmetric test is inconclusive and we report that null result.

**(c) Discrimination test.** With empirical *B* ± σ_B and reconstructed *r* ± σ_r, we ask: does the 95 % confidence interval on *B* exclude *B* = π² (symmetric)? Does it exclude *B*(*r*)? If it excludes one but not the other, the data discriminates between the two predictions and we report which. If it excludes both, the finite-time Landauer framework is falsified in its current form, and we report that falsification. If it excludes neither, the data is insufficient to discriminate and we state so.

A paper produced under this scope is **submit-and-revise at PRE** regardless of the outcome — the empirical refit itself is the contribution, the discrimination result is a bonus.

## 3. Why now

The finite-time Landauer formula is eleven years old and has been cited hundreds of times. It has never been refit against the full Bérut curve — the Bérut paper used only the quasistatic-limit point to verify Landauer, and Proesmans et al. 2020 cited Bérut as motivation without refitting. Dago et al. (2021, 2022) have recent follow-up experiments but with different protocols; they are natural comparators but not substitutes. The asymmetric extension *B*(*r*) was proposed in our prior work (thermodynamic_info_limits, §3.2) as a heuristic and flagged by Phase 0.25 review as untested; closing that gap is the single highest-value edit to the predecessor paper.

## 4. Falsifiability

Three pre-specified binary kill-outcomes:

- **Empirical *B* fit.** The 95 % CI on the fitted *B* is either finite (a proper fit exists) or it is degenerate (the ten-point curve does not constrain *B*). The latter outcome falsifies the assumption that the Bérut curve carries enough information to test the formula, which is itself publishable.
- **Asymmetric-formula test.** With *r* pinned from the optical-trap reconstruction, *B*(*r*) is a specific numerical prediction. Either the empirical *B* CI contains this prediction or it does not.
- **Symmetric-formula test.** Either the empirical *B* CI contains *B* = π² or it does not.

The four possible joint outcomes of the last two — (excludes symmetric, excludes asymmetric), (includes symmetric, excludes asymmetric), (excludes symmetric, includes asymmetric), (includes both) — are all scientifically meaningful and all publishable. There is no parameter-tuning degree of freedom: *r* is fixed by the optical trap, *B* is fixed by the fit.

## 5. Named comparators and differentiation

- **Proesmans, Ehrich & Bechhoefer (2020)** — derived the symmetric *B* = π² formula. We test their formula on the data that motivated it but was never refit under it.
- **Bérut et al. (2012)** — the dataset. They fit only the quasistatic-limit point; we fit the full curve.
- **Dago, Ciliberto et al. (2021, 2022)** — newer finite-time Landauer experiments with different protocols (logical operations, modulated traps). We use their work as context but our test is specifically against Bérut 2012 because that is the dataset the theoretical *B* = π² was proposed for.
- **Zhen, Chupeau et al. (2021)** — feedback-trap finite-time erasure; relevant but uses a different optimisation target.

This proposal's novelty claim is narrow and concrete: we are the first to refit the original Bérut dataset against the Proesmans formula and the first to test the asymmetric generalisation *B*(*r*) against any experimental data.

## 6. Target venue

**Physical Review E** — publishes empirical tests of stochastic-thermodynamics bounds at this exact scale and scope. The test is binary, the dataset is public, the prediction has a pre-registered form. Expected PRE objection: a rigorous propagation of the Bérut measurement uncertainty through to the *B* fit (not a heuristic 20 % handwave). Tractable.

**Fallback: J. Stat. Mech.** if the fit is inconclusive and the paper becomes a methodology-and-null-result synthesis rather than a discrimination.

## 7. Relation to the broader research programme

This project is a narrowly scoped empirical closure of the one genuinely falsifiable claim in the predecessor paper `thermodynamic_info_limits/paper.md` §3.2. A PROCEED outcome here turns that paper's REFRAME verdict at PRE into a candidate submit-and-revise, and renders the asymmetric-barrier claim either validated or retracted. It does NOT depend on the now-killed cross-substrate project (thermodynamic_cross_substrate), nor on the thermodynamic_ml_limits paper.
