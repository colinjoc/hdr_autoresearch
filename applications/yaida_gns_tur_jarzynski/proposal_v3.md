**Target**: publication — primary venue: Journal of Statistical Mechanics: Theory and Experiment, fallback venue: Physical Review E

# A pre-registered Crooks-ratio test of the Langevin approximation to SGD, with effective-sample-size gating and an independent Gaussianity boundary

## 1. Question

At which learning rates η does time-reversed Langevin-approximated stochastic gradient descent (SGD) satisfy the Crooks fluctuation theorem with the Gradient-Noise-Scale-derived effective temperature — and what is the pre-registered, quantitatively-defined Gaussianity boundary beyond which the Langevin framing becomes formally inapplicable?

v2 of this proposal (scope_check_v2.md) reached REFRAME over three issues, each concrete and individually addressable: (F1) the Jarzynski Tier-1 threshold |log R|/σ_log_R ≤ 2 self-widens in the heavy-tailed regime the test is meant to detect, passing on noise alone; (M1) the Gaussianity-measurement novelty is oversold against Simsekli 2019, Panigrahi 2019 and Xie 2021; (M2) the ΔF definition in v2 is circular — it uses T_SGD_GNS, which is what the Jarzynski test is meant to validate. v3 addresses all three, below.

## 2. Proposed contribution

**(a) Pivot from Jarzynski to Crooks ratio.** The Crooks fluctuation theorem states

    P_F(W) / P_R(−W) = exp(β W)

where P_F(W) and P_R(W) are the work distributions in a forward and a time-reversed protocol on the *same* Hamiltonian. Measuring this *linear-in-W* relationship requires no free-energy estimate. ΔF is eliminated by construction. v3 tests the Crooks ratio directly: log[P_F(W)/P_R(−W)] is either linear in W with slope β = 1/T_SGD_GNS, or it is not.

**(b) First-class Gaussianity test differentiated from prior work.** For each η ∈ {10⁻⁵, 10⁻⁴, 10⁻³, 10⁻², 10⁻¹} on the Goldt–Seifert 2017 50-dimensional quadratic testbed, compute the Jarque–Bera, Mardia skewness / kurtosis, and Σ_grad condition-number diagnostics of the per-example gradient noise. Differentiation from prior work:
  - **Simsekli, Sagun & Gurbuzbalaban 2019** established that SGD gradient noise is *heavy-tailed* (α-stable, not Gaussian) at the large-learning-rate regime of practical interest. We do not dispute this; we pre-register the boundary where it begins by directly measuring the Jarque–Bera p-value transition.
  - **Panigrahi, Misra, Kunnumkal 2019** studied non-Gaussianity on image tasks without pre-registered tolerances.
  - **Xie, Sato & Sugiyama 2021** proposed a "diffusion theory of SGD" acknowledging the Gaussian assumption can fail. They do not quantify the η-boundary.

Our contribution is the *pre-registered quantitative Gaussianity boundary on a testbed with an analytical reference*, which none of the three did.

**(c) Effective-sample-size gating — the fatal-objection fix.** Before reporting any Crooks-ratio result at a given η, we pre-register the requirement

    n_eff(η) ≥ 1000

where n_eff is the effective sample size of the importance-sampling weights in the Crooks estimator (Kish's effective sample size: n_eff = (Σ wᵢ)² / Σ wᵢ² with wᵢ = exp(−β Wᵢ) / Z). At n_traj = 10⁴, n_eff ≥ 1000 is a 10 %-efficiency gate; below that, the distribution is too heavy-tailed for a 2σ Crooks-ratio test to distinguish satisfied from violated at any reasonable wall-clock.

When n_eff < 1000 at a given η, the η is declared **Crooks-uninformative**, and the paper reports this outcome explicitly rather than claiming failure. This separates "SGD violates Crooks" (a genuine negative result) from "heavy-tailed noise makes the test uninformative" (a statistical artefact). The v2 reviewer explicitly named this as the single most-important recommendation.

**(d) Five binary kill-outcomes with pre-registered tolerances.**

- **(O1) Gaussianity boundary measured.** There exists some η* in the tested grid such that the Jarque–Bera p-value transitions from > 0.01 to ≤ 0.01 across it, OR the transition is not resolvable at n = 10⁴. Either result is publishable.
- **(O2) Effective sample size gate.** For each η, either n_eff(η) ≥ 1000 (run informative) or < 1000 (run declared Crooks-uninformative). Reported as a per-η binary flag in the results table.
- **(O3) Crooks ratio linearity in the informative regime.** On the set of η for which n_eff ≥ 1000, a least-squares fit of log[P_F(W)/P_R(−W)] vs W yields a slope either consistent with β = 1/T_SGD_GNS to within 5 % (well inside the bootstrap 95 % CI at n_eff = 1000), or not.
- **(O4) Intercept check.** The fit intercept is either consistent with 0 to within bootstrap 95 % CI, or not. A nonzero intercept would indicate a bias inconsistent with the Crooks identity.
- **(O5) Regime-boundary transfer to small real data.** The η* from (O1) and the Crooks-informative regime from (O2)–(O3) either predict the same η* on a small MNIST network (784 → 10, ~8000 parameters) to within one order of magnitude, or not. The real-data test is the single MNIST run; the quadratic landscape remains primary because it supplies the analytical β reference.

## 3. Why now

Three specific 2021–2024 developments make this tractable:
  - **Simsekli et al. 2019–2021** established the α-stable nature of SGD noise and gave sharp quantitative bounds on the failure of Gaussianity. We now know *what* to measure and at *what scale of η* to expect the transition.
  - **Peng, Sun & Duraisamy 2024 (*Entropy*)** published a rigorous stochastic-thermodynamics formulation of learning with ΔF-free Crooks-ratio observables, giving our v3 pivot its theoretical anchor.
  - **Mandt et al. 2017 and Mandt follow-ups through 2023** refined the T_SGD_GNS expression. We adopt the Mandt-2023 form, not the original 2017 form.

## 4. Named comparators and differentiation (expanded to address v2 scope-check)

- **Yaida 2018** — stationary fluctuation-dissipation only; no non-stationary Crooks or Jarzynski. Our non-stationary Crooks test fills this gap.
- **Goldt & Seifert 2017** — closed-form perceptron stochastic thermodynamics; analytical reference point, not a measurement protocol.
- **Chaudhari & Soatto 2018** — variational inference framing; bounds on posterior KL, not the work-distribution identity.
- **Simsekli, Sagun & Gurbuzbalaban 2019** — non-Gaussianity of SGD noise in practice. Cited; our contribution is the pre-registered quantitative η-boundary.
- **Panigrahi, Misra & Kunnumkal 2019** — non-Gaussianity evidence on images; no pre-registered tolerances.
- **Xie, Sato & Sugiyama 2021** — diffusion theory of SGD; Gaussian assumption acknowledged as limiting, not quantitatively tested.
- **Kunin, Sagastuy-Breña, Gillespie et al. 2021** — qualitative Langevin critique; no quantitative boundary.
- **Peng, Sun & Duraisamy 2024** — stochastic-thermodynamic formulation of learning with Crooks-ratio observables. Direct anchor for our ΔF-free formulation.
- **Mandt et al. 2017 / Mandt follow-ups 2023** — T_SGD_GNS definitional lineage.

The Phase 0 literature review will actively search JSTAT, PRE, NJP, Physical Review Research, and arXiv abs/cond-mat.stat-mech 2022–2026 for any paper combining ("SGD OR neural network training") + ("Crooks" OR "Jarzynski" OR "fluctuation theorem") + "work distribution" — and differentiate against each hit.

## 5. Target venue — swap to JSTAT primary (per v2 scope-check recommendation)

**Journal of Statistical Mechanics: Theory and Experiment** — publishes controlled stochastic-thermodynamics validations with explicit scope restrictions and pre-registered thresholds. The scope-restriction-to-perceptron-and-small-MNIST framing v3 commits to fits JSTAT's remit. Expected JSTAT objection: perceptron scale is too narrow to interest the ML community. Mitigation: we state the scope as a *physics* result (validity boundary measurement) not an *ML* result (SGD theorem).

**Fallback: PRE** — if the scope restriction is judged too narrow for JSTAT and a broader ML framing is desired, PRE is an alternative with a higher novelty bar.

**Not attempted:** PRL (too narrow-scope), Nature Physics (too narrow-scope), ML venues like NeurIPS (our result is a physics boundary, not an ML methodology).

## 6. Scope boundaries — what this paper is NOT

- NOT a test at GPT-4 scale; the predecessor paper `thermodynamic_ml_limits`' GNS-TUR bound is not validated here.
- NOT a new theorem. The Crooks, Jarzynski, and TUR identities are used unchanged.
- NOT a cross-substrate comparison.
- NOT a disproof of the α-stable-noise literature (Simsekli 2019); we confirm it and report the η-boundary.
- NOT a claim that the Crooks test passes or fails at any specific η — the paper's contribution is the *measurement*, not a predetermined conclusion.

## 7. Address for the real-data rule from CLAUDE.md

The synthetic 50-dimensional quadratic landscape is not a shortcut — it is the *mandatory* analytical reference point for a stochastic-thermodynamics validation. Real ML tasks do not have closed-form β, ΔF, or Σ_grad structure. Our MNIST run is included as regime-boundary transfer, not as the primary validation. This addresses the CLAUDE.md rule's "synthetic data requires real-data lineage" clause by adopting the Goldt–Seifert 2017 already-published testbed with known analytical answers.
