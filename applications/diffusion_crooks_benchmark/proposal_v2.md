**Target**: publication — primary venue: Transactions on Machine Learning Research (TMLR), fallback venue: Entropy

# The training dynamics of the Crooks-ratio slope: empirically tracking a diffusion model's approach to the fluctuation-theorem limit

## 1. Question

For a denoising diffusion probabilistic model (DDPM), the Crooks fluctuation theorem predicts

    log[P_F(W) / P_R(−W)] = β W

where P_F and P_R are forward- and reverse-trajectory work distributions and β = 1/T is set by the SDE schedule. The equality is *guaranteed* at the exact reverse process, and it becomes *tight* only when the learned model matches the true reverse dynamics — i.e. only at training convergence. At random initialisation the slope ≠ β; at convergence the slope → β. **How fast does the empirical Crooks-ratio slope β̂(t_train) converge to the theoretical β as training progresses, and does the convergence rate depend on model size, schedule, or noise level in a way standard ELBO-gap measurements cannot see?**

The v1 scope check correctly flagged that tests of Crooks / Jarzynski on a *trained* DDPM are mathematically equivalent to the ELBO being tight, which a well-trained model satisfies by construction. v2 pivots the question from static-validation (tautological) to training-dynamics measurement (non-tautological by design).

## 2. Proposed contribution

**(a) A 1-D analytical-reference DDPM.** Use a one-dimensional Gaussian target distribution with a closed-form score function s(x, t) = ∂_x log p_t(x). Train a small MLP (∼100 parameters) as the learned score. At every training step, analytical β, analytical ΔF, and the exact P_F and P_R are known. This is the diffusion analogue of the Goldt–Seifert 2017 perceptron testbed: an analytically tractable reference where the measurement can be cross-checked.

**(b) Training-dynamics measurement of β̂.** At training iterations k ∈ {0, 10, 100, 1000, 10000}, evaluate the empirical Crooks-ratio slope β̂(k) from 10⁴ forward- and reverse-trajectory pairs. Plot β̂(k)/β_true vs k. Report:
  - The rate constant κ in an exponential-fit |β̂(k) − β|/β ~ exp(−κ k)
  - The asymptote β̂(∞) and whether |β̂(∞) − β| is statistically consistent with zero at n = 10⁴
  - Whether the convergence rate κ correlates with the training-loss convergence rate (classical ELBO-based measurement)

**(c) The independent control — schedule perturbation.** Train two additional DDPMs at the same model size but with (i) a modified noise schedule (cosine vs linear β_t), and (ii) additional score-matching targets at intermediate t. Compare the β̂(k) curves. If the Crooks-ratio-slope convergence is substrate-independent of schedule, it is a measurement of training progress alone; if not, it is also a schedule-diagnostic.

**(d) One real-data sanity check at 2-D.** Repeat the same β̂(k) measurement on a 2-D mixture-of-Gaussians task where analytical β is still computable. Verify the 1-D result transfers. No CIFAR-10 — CIFAR-10 has no analytical reference and would re-introduce the tautology.

**(e) The honest non-claim.** This paper does not claim to resolve whether a *trained* DDPM satisfies Crooks — the v1 reviewer is right that this is tautological. What the paper claims is that β̂(k) measured during training is a **previously-untracked ML training diagnostic** that can be computed at negligible cost and provides information not captured by the ELBO loss alone.

## 3. Why now — and the comparator differentiation that v1 missed

Three 2015–2024 papers define the prior art, all cited in the v1 reviewer's scope check and addressed here:

- **Sohl-Dickstein et al. 2015** — wrote the ELBO of a diffusion model as a Jarzynski-style trajectory average. Static formulation; no training-dynamics measurement. Our β̂(k) is the *time-series* of what Sohl-Dickstein wrote as a single equation.
- **Neal 2001 / Grosse et al. 2013 (Annealed Importance Sampling) / Masrani, Wu & Wood 2019 (Thermodynamic Variational Objective)** — all test ⟨exp(−βW)⟩ = exp(−βΔF) on trained latent-variable models. Static checks. None of the three measures the trajectory of the slope during training.
- **Boyd, Crutchfield & Gu 2022** — max-work = max-likelihood theorem. Proves the identity in the limit. Our measurement characterises the *approach to* the limit.

Our contribution is orthogonal to all three: the time-series of β̂(k) during training is a quantity none of these works reports. A focused Phase 0 literature review will search 2023–2026 ML theory venues (ICLR, NeurIPS, ICML, TMLR) for "diffusion model + ELBO-gap" or "diffusion model + training-dynamics + fluctuation" before any Phase 0.25 claim of novelty.

## 4. Pre-registered binary kill-outcomes

- **(O1) β̂(0) ≠ β.** At training iteration 0 (random-initialised score), the empirical Crooks slope is either inconsistent with β to > 5σ (non-tautological), or it is consistent with β by accident (confirming the task is too trivial to be informative).
- **(O2) β̂(k) → β.** The empirical slope either converges to β as training progresses (|β̂(k) − β| / β < 0.1 at k = 10⁴) or it does not. Non-convergence would indicate the learned model fails to saturate the Crooks identity — a publishable negative result.
- **(O3) Exponential-fit quality.** The |β̂(k) − β|/β trajectory either admits an exponential fit with R² > 0.8 or it does not. A power-law or plateau fit is a different finding and is reported as such.
- **(O4) Schedule transfer.** The rate constant κ either changes by less than a factor 2 across the two schedules tested, or it does not. Schedule-dependence would be a new finding about diffusion training.
- **(O5) Dimensionality transfer.** The 2-D result either reproduces the 1-D κ to within a factor 2 or it does not. This is the scope-restriction check for real-data transfer.

## 5. Named comparators and differentiation (full list)

| Comparator | What they did | What we do differently |
|---|---|---|
| Sohl-Dickstein et al. 2015 (ICML) | Identified diffusion ELBO as Jarzynski trajectory sum (static) | Measure the slope's training-time trajectory |
| Ho, Jain & Abbeel 2020 (NeurIPS) | Trained DDPM on CIFAR-10 | Use 1-D/2-D analytical reference; no CIFAR |
| Neal 2001 (Stat. Comput.) | AIS for partition-function estimation | Use Crooks ratio, not AIS estimator |
| Grosse et al. 2013 (NeurIPS) | AIS on trained latent-variable models | Measure during training, not post-hoc |
| Masrani, Wu & Wood 2019 (NeurIPS) | Thermodynamic Variational Objective | Same underlying identity, different observable (β̂ not bound gap) |
| Boyd, Crutchfield & Gu 2022 (PRX Quantum) | Max-work = max-likelihood theorem | We measure the approach to the limit |
| Peng, Sun & Duraisamy 2024 (Entropy) | Stochastic-thermodynamic formulation of learning | We test a specific observable they introduce |

## 6. Target venue — TMLR primary per v1 reviewer recommendation

**TMLR** — publishes ML-methods papers with rigorous empirical analyses and pre-registered tolerances; welcomes training-dynamics measurements that produce new diagnostics for existing models. The TMLR framing is correct for this pivot: the paper is an ML-training-diagnostic result, not a physics-theorem result.

**Fallback: Entropy (MDPI)** — welcomes synthesis and measurement papers in stochastic thermodynamics applied to ML. Open-access, broader audience, lower novelty bar. JSTAT is a further fallback if the measurement framing dominates.

**NOT attempted:** NJP (the v1 stretch — not a physics-theorem result), PRL (too narrow-scope).

## 7. Scope boundaries — what this paper is NOT

- NOT a test that "diffusion models satisfy the Crooks theorem." We agree with the v1 reviewer that this is tautological for a trained model.
- NOT a proof of a new theorem.
- NOT a CIFAR-10 or text-to-image result; we stop at 2-D because 2-D has analytical β and higher dimensions do not.
- NOT a claim to predict ML training loss from β̂(k); we measure the two trajectories and report whether they correlate, not whether one predicts the other.
- NOT a validation of the predecessor paper `thermodynamic_ml_limits`' GNS-TUR bound; the observables here are different.

## 8. Real-data rule (CLAUDE.md)

The 1-D Gaussian and 2-D mixture-of-Gaussians testbeds are synthetic, justified by the stochastic-thermodynamics requirement that β be analytically known for Crooks-identity validation. Real image data (CIFAR, MNIST) has no analytical β and cannot supply the reference this measurement requires. The scope boundary in §7 states this directly.
