**Target**: publication — primary venue: Physical Review E, fallback venue: Journal of Statistical Mechanics: Theory and Experiment

# A pre-registered Jarzynski-equality test of the Langevin approximation to SGD at controlled scale

## 1. Question

At which learning rates η does Langevin-approximated stochastic gradient descent (SGD) satisfy the Jarzynski equality with the Gradient-Noise-Scale-derived effective temperature, and — critically — what is the pre-registered, quantitatively-defined *validity boundary* of the Langevin approximation itself as measured by the Gaussianity of per-example gradient noise at each η?

The proposal v1 scope check correctly identified that (i) "validity regime" must be a measured quantity, not a knob; (ii) the Langevin-approximation check has to be first-class, not assumed; (iii) the pre-registered thresholds must be theory-derived; and (iv) the scope must honestly acknowledge perceptron / small-MNIST limits, or defend generalisation beyond them.

## 2. Proposed contribution

**(a) First-class Langevin-validity test.** For each learning rate η ∈ {10⁻⁵, 10⁻⁴, 10⁻³, 10⁻², 10⁻¹} on a controlled 50-dimensional quadratic landscape (the Goldt–Seifert 2017 testbed, which has a closed-form analytical entropy-production reference), measure the per-example-gradient distribution and report:
  - Jarque–Bera test statistic against a Gaussian null
  - Mardia skewness and kurtosis of the multivariate gradient noise
  - Largest and smallest eigenvalue of the empirical gradient covariance Σ_grad, and condition number

These quantities define the Langevin validity regime *empirically*, not by assumption. A pre-registered boundary: **η is inside the Langevin-valid regime if and only if the Jarque–Bera p-value on marginal gradients exceeds 0.01 AND the Mardia skewness p-value exceeds 0.01 AND Σ_grad condition number ≤ 100.**

**(b) Pre-registered Jarzynski test.** For each η, measure forward and time-reversed trajectory work distributions over a 10⁴-trajectory batch. Compute the Jarzynski ratio R(η) = ⟨exp(−β W)⟩ / exp(−β ΔF). Pre-register two fail-thresholds, derived from sample-size theory rather than chosen to taste:
  - *Tier-1 satisfied:* |log R(η)| / σ_log_R(η) ≤ 2.0 (the theoretical 2σ band at the declared 10⁴-trajectory sample size for a bona-fide Jarzynski-obeying process).
  - *Tier-2 satisfied:* |log R(η)| ≤ 0.1 (the "10 % multiplicative" engineering tolerance often used in experimental-stochastic-thermodynamics validations, e.g. Bérut 2012 quasistatic check).

Both thresholds stated before any data is seen.

**(c) GNS-derived T_SGD consistency.** Extract T_SGD_empirical from the measured Jarzynski work distribution via the fluctuation-theorem log-slope method (Collin et al. 2005). Extract T_SGD_GNS from Σ_grad and η via the Mandt et al. 2017 formula. Pre-register: the two are "consistent" iff their ratio lies in [0.9, 1.1] AND the corresponding pairs σ_W_measured vs σ_W_GNS-predicted lie within bootstrap 95 % CI of each other. No 30 % threshold; no "factor of 3".

**(d) ΔF for an SGD optimiser.** Use the a-priori loss-function-derived ΔF = L(θ_final) − L(θ_initial) where θ_final is sampled from the Gibbs distribution π_∞(θ) ∝ exp(−L(θ)/T_SGD_GNS) computed analytically on the quadratic landscape. This is a definition stated *before* running the test, not tuned to make Jarzynski hold.

**(e) Honest scope restriction.** This paper validates the GNS–Jarzynski–TUR framework at perceptron and N≤10 million parameter scale only. Claims at GPT-4 scale are NOT made. The paper's abstract states this limitation explicitly. A single larger-scale test is run (one forward pass of a ResNet-18 on CIFAR-10) to demonstrate Gaussianity breaks by N ~10⁵ — documenting the regime boundary, not claiming validity beyond it.

## 3. Why now

Three 2023-2026 developments make this tractable in a way it was not when Yaida 2018 or Chaudhari-Soatto 2018 were written:
  - Lotfi et al. 2022 (PAC-Bayes tight bounds) gives rigorous ΔF bounds for trained networks that can replace the Gibbs-distribution assumption if the quadratic-landscape restriction turns out to be too strict.
  - Peng, Sun, Duraisamy 2024 (*Entropy*) published a full stochastic-thermodynamics formulation of parametric probabilistic models, giving exact analytical forms against which to cross-check at perceptron scale.
  - Modern Jarque–Bera / Mardia test implementations (scipy.stats.jarque_bera, statsmodels) and eigendecomposition on 50-dim Σ_grad are computationally negligible — the proposed measurements take minutes per η on commodity hardware.

These changes convert what was previously an open methodological question (how do you pre-register a Langevin-validity boundary?) into a concrete engineering protocol.

## 4. Falsifiability

Four binary kill-outcomes, each with pre-registered tolerances tied to either sample-size theory or published engineering practice:

- **Gaussianity boundary measured.** There exists some η* in the tested grid such that (Jarque-Bera p-value > 0.01 at η < η*) AND (≤ 0.01 at η > η*), OR the transition is undetectable at the tested sample size. Either result is publishable.
- **Jarzynski Tier-1 held at least once.** At least one η satisfies |log R(η)| / σ_log_R(η) ≤ 2.0, or none does. If none does at any η, the Langevin-SGD-thermodynamics framing is empirically unfalsified (null result).
- **T_SGD consistency at least once.** At least one η satisfies both the ratio ∈ [0.9, 1.1] AND the σ_W bootstrap agreement, or none does. This is a tighter threshold than v1's "30 %" and removes the tolerance-gaming risk.
- **Regime-boundary transfer.** The η* at which Gaussianity or Jarzynski fails on the quadratic landscape either predicts the same η* on small MNIST to within one order of magnitude, or it does not. "Substrate-independence" of the boundary is a binary claim at a well-defined precision.

## 5. Named comparators and differentiation

- **Yaida (2018)** — stationary-FDR tests only. Our Jarzynski test is non-stationary. Differentiation: Yaida tests relations that hold *in* the stationary distribution; we test relations that govern the *approach* to it.
- **Goldt & Seifert (2017)** — closed-form analytical perceptron stochastic thermodynamics. Our contribution is *measurement* of what Goldt-Seifert derived analytically, plus the Gaussianity boundary they did not characterise.
- **Chaudhari & Soatto (2018)** — SGD as variational inference. They bound the posterior's KL divergence from the loss landscape's Gibbs measure; we test the work-distribution identity that, together with that bound, defines the Langevin approximation's validity. Orthogonal.
- **Peng, Sun & Duraisamy (2024, *Entropy*)** — stochastic thermodynamics of parametric probabilistic models. Our perceptron result is a direct numerical check of their framework at a specific testbed; no claim to extend.
- **Kunin, Sagastuy-Breña, Gillespie et al. (2021)** — "Rethinking SGD as a Langevin process" — implicit Langevin-breakdown analysis. They give a qualitative critique; we give a quantitative pre-registered boundary.

The Phase 0 literature review will actively search 2022–2026 PRE, JSTAT, NJP, and arXiv abs/cond-mat.stat-mech for any paper whose headline combines "SGD + Jarzynski" or "SGD + work distribution + measurement" to close remaining novelty gaps before Phase 0.25.

## 6. Target venue

**Physical Review E** — publishes controlled empirical tests of stochastic-thermodynamics frameworks at small scale, with rigorous pre-registered thresholds. Expected PRE objection: "your result is only at perceptron scale." Mitigation: we state the scope limitation in the title and abstract, and we produce the Gaussianity-breakdown measurement at N~10⁵ as evidence of *where* the validity boundary sits rather than a claim of validity beyond it. Fallback: **J. Stat. Mech.** if the scope-restriction framing is judged too narrow for PRE.

## 7. Scope boundaries — what this paper is NOT

- NOT a test of the GNS-TUR bound at GPT-4 scale. The predecessor paper `thermodynamic_ml_limits` still needs independent validation there; this project cannot supply it.
- NOT a new theorem or a modification of the Jarzynski, Crooks, or TUR relations.
- NOT a cross-substrate comparison. The `thermodynamic_cross_substrate` project was killed; its scope is not revived.
- NOT a definition of SGD's "free energy" that avoids the circularity objection — we *adopt* the Gibbs-distribution analytical form on the quadratic landscape and report its domain of applicability as one of our measurements.

## 8. Addressing the real-data rule from CLAUDE.md

The user's global CLAUDE.md requires real data over synthetic. This project uses a synthetic quadratic landscape AS THE PRIMARY TESTBED. Justification: stochastic thermodynamics tests require a system with a *known analytical reference* for ΔF, for σ_phys, and for the Jarzynski partition function. Real ML tasks (MNIST, CIFAR, etc.) do not have closed-form ΔF; a Jarzynski test on them cannot separate "Jarzynski fails" from "ΔF is mis-estimated". The synthetic quadratic landscape is therefore not a shortcut but the mandatory reference point.

A complementary MNIST test is included (as a secondary measurement) to verify the validity-boundary transfer claim. This is real data, but its role is confined to regime-boundary measurement, not ΔF determination.
