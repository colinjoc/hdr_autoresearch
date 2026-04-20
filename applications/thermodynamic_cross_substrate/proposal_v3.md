**Target**: publication — primary venue: Physical Review E, fallback venue: Journal of Statistical Mechanics

# Finite-time Landauer bounds from colloidal bit erasure to GPU training: empirical verification and cross-substrate extension

## 1. Question

Does the finite-time Landauer coefficient *B*, measured directly from the Bérut et al. (2012) colloidal bit-erasure dataset, match the symmetric Schmiedl–Seifert (2007) prediction *B* = π², match the asymmetric proposal *B*(*r*) = π²(1+*r*)²/(4*r*) from our prior work (at the known asymmetry of the Bérut optical trap), or neither? And if *B* is empirically known, does the same finite-time framework predict the excess dissipation per bit in published GPU-training energy data, or is the prediction off by more than a specified tolerance?

## 2. Proposed contribution

The scope-check has correctly rejected both a "universal saturation ratio" framing (too loose, collides with Kempes 2017) and a "Harada–Sasa extension to SGD" framing (collides with Yaida 2018 and Goldt–Seifert 2017). This v3 drops both and replaces them with a **purely empirical test** of an existing theoretical framework across two substrates it has never been jointly applied to:

**(a) Empirical extraction of *B* from Bérut 2012.** The Bérut dataset contains ten cycle times τ ranging from 5 ms to ~40 s at fixed *T* = 300 K. Fitting ⟨*Q*_diss⟩(τ) = *k_BT* ln 2 + *Bk_BT*/τ to the full curve yields an empirical *B* with error bars. We then compare to (i) *B* = π² (Schmiedl–Seifert symmetric prediction), (ii) *B*(*r*) = π²(1 + *r*)²/(4*r*) evaluated at the optical-trap asymmetry *r* that can be read off the Bérut et al. supplementary, and (iii) *B* fitted as a free parameter. Binary outcome: either the asymmetric formula matches the empirical *B* within stated error bars, or it does not.

**(b) Cross-substrate extrapolation.** The finite-time Landauer formula with the empirically extracted *B* is then applied to GPT-4-scale GPU training (τ_clock ≈ 1 ns, *T* = 350 K). The prediction is: per-FLOP dissipation in a modern transformer kernel should exceed the quasistatic floor by a factor of approximately *B*·τ_Landauer/τ_clock, where τ_Landauer = ℏ/(*k_BT* ln 2). Using Horowitz 2014 and Patterson et al. 2021 published energy data we compute the observed excess and compare. Binary outcome: either the finite-time prediction matches published CMOS data within one order of magnitude (the known CMOS-vs-Landauer gap), or it is off by more — in which case we report *which* correction factor (leakage, data movement, or the finite-time coefficient itself) is responsible.

**(c) The combined paper.** If (a) and (b) both succeed, the thermodynamic_info_limits and thermodynamic_ml_limits papers are merged around the finite-time framework as the shared methodology. If (a) or (b) fails, the individual papers remain separately submittable and the merge is abandoned. This decision is pre-committed, not contingent on which result is more flattering.

## 3. Why now

Three specific developments:

- **Bérut 2012 has never been refit in the finite-time-with-asymmetry framework.** The original paper fit the quasistatic limit only; Proesmans et al. 2020 derived the symmetric finite-time formula post hoc but did not refit the data. No one has tested the asymmetric generalisation against real colloidal data.
- **Patterson et al. 2021 (Green AI) and NVIDIA H100 specification** together provide enough published CMOS energy numbers at the kernel level to compute the finite-time prediction without new measurements.
- **The two existing thermodynamic-bounds papers (thermodynamic_info_limits, thermodynamic_ml_limits) have been reframed as syntheses-with-one-novel-piece.** A sharp, binary, empirical result closes the remaining gap for either a merge or for each paper separately.

## 4. Falsifiability

Three binary kill-outcomes, each a numerical comparison with a published dataset at a pre-specified tolerance:

- **Bérut *B* fit.** If the empirical *B* (from the full ten-point curve) is not consistent with *B*(*r*)·[1 ± 0.2] at the optical-trap asymmetry, the asymmetric formula is falsified and §3.2 of the info_limits paper must retract the formula. Tolerance is set by the published Bérut measurement uncertainty.
- **Symmetric vs asymmetric discrimination.** If the 95% confidence interval on the empirical *B* includes both *B* = π² and *B*(*r*), the data cannot discriminate between the two predictions and the paper reports that null result instead.
- **CMOS excess dissipation.** If the finite-time prediction for GPT-4-scale per-bit dissipation is off from the Patterson-reported value by more than one order of magnitude, the naive finite-time extrapolation fails and we identify the dominant missing physics (leakage, data movement, or the finite-time coefficient itself).

None of these uses hand-picked tolerances; all three are numerical comparisons to published data at pre-specified precision.

## 5. Named comparators and differentiation

- **Proesmans, Ehrich & Bechhoefer (2020)** derived the symmetric *B* = π² finite-time Landauer formula. We test their formula on the Bérut data that it was designed to explain, but that it was never empirically refit against. Our asymmetric *B*(*r*) is a proposed extension.
- **Bérut et al. (2012)** is the dataset; the original paper used only the quasistatic-limit point for Landauer verification. The full τ-dependent curve has been cited but never refit in the finite-time framework.
- **Yaida (2018)** and **Goldt–Seifert (2017)** are the FDR/SGD literature. This proposal does NOT claim to extend their framework. It uses the finite-time Landauer bound, which is substrate-independent by construction, and tests whether it extrapolates from colloidal to CMOS.
- **Kempes et al. (2017)** did cross-substrate dissipation-per-bit. We do cross-substrate finite-time-Landauer prediction — a narrower, sharper test with binary outcomes.

## 6. Target venue

**Physical Review E** — publishes empirical tests of stochastic-thermodynamics bounds with quantitative tolerances. The test we propose is exactly the kind of work PRE accepts: refit a published dataset under a previously untested theoretical prediction, report the binary outcome. Expected PRE objection: they will want explicit statistical treatment of the Bérut error bars and a stated prior on *r* from the optical-trap paper, both tractable.

**Fallback: J. Stat. Mech.** — more tolerant of synthesis framing if only (a) succeeds and (b) partially fails.
