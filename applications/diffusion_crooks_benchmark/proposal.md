**Target**: publication — primary venue: New Journal of Physics, fallback venue: Transactions on Machine Learning Research

# Diffusion models as a controlled testbed for the Crooks fluctuation theorem in machine learning

## 1. Question

Denoising-diffusion probabilistic models (DDPMs) are, by construction, a forward-reverse non-equilibrium process with an explicit ELBO decomposition: each sampling step is a thermodynamic transition between a data distribution and a noise distribution. Does the Crooks fluctuation theorem, applied to the forward / reverse trajectory work distributions in a small-scale DDPM trained on CIFAR-10, quantitatively match the ELBO decomposition — and does ⟨exp(−βW)⟩ recover exp(−βΔF) to within simulation precision?

## 2. Proposed contribution

**(a) Train a small-scale DDPM on CIFAR-10** (8-layer U-Net, T = 1000 diffusion steps). Log forward and reverse log-likelihoods per sampling trajectory.

**(b) Map diffusion-process quantities to stochastic-thermodynamics quantities.** Identify the "work" per diffusion step as −log p(x_{t-1} | x_t) + log q(x_t | x_{t-1}) (the ELBO score-per-step); identify ΔF per sampling trajectory with the trained model's log-evidence. Verify that this identification reduces to the Boyd-Crutchfield-Gu 2022 "maximum work = maximum likelihood" identity in the limit of optimal training.

**(c) Test the Crooks fluctuation theorem** on a batch of forward and reversed trajectories. Compute the ratio P_forward(W) / P_reverse(−W) and check it equals exp(β W − β ΔF).

**(d) Compare to the heuristic Crooks-for-SGD** used in `thermodynamic_ml_limits/paper.md`. DDPMs are rigorous; SGD is not. Quantify the gap in ⟨exp(−βW)⟩ between the two.

## 3. Why now

Sohl-Dickstein et al. 2015 and Ho et al. 2020 established the diffusion-ML framework with explicit thermodynamic mapping. Boyd, Crutchfield & Gu 2022 closed the conceptual loop between maximum-work and maximum-likelihood. No empirical Crooks-theorem test has been published for a trained ML system that admits one by construction. Small-scale DDPM training is now trivially reproducible on a single GPU in hours.

## 4. Falsifiability

Three binary kill-outcomes:

- **Jarzynski identity on DDPM.** ⟨exp(−βW)⟩ on the forward trajectories either equals exp(−βΔF) within 10 % or does not.
- **Crooks ratio linearity.** The log-ratio log[P_forward(W)/P_reverse(−W)] either is linear in W with slope β within 5 %, or it is not (the latter would indicate the identification of W is incorrect).
- **Map to ELBO decomposition.** The ΔF extracted from the Crooks fit either matches the trained model's log-evidence to within the training's Monte-Carlo error, or it does not.

## 5. Named comparators and differentiation

- Sohl-Dickstein et al. (2015), ICML — original diffusion-ML formulation.
- Ho, Jain, Abbeel (2020), NeurIPS — DDPM.
- Boyd, Crutchfield, Gu (2022), NJP / PRX Quantum — thermodynamic ML.
- Peng, Sun, Duraisamy (2024), Entropy — parametric probabilistic stochastic thermodynamics.

No prior work has empirically tested the Crooks fluctuation theorem on a trained DDPM. This is the first direct thermodynamic test of a widely-used ML training paradigm.

## 6. Target venue

**New Journal of Physics** — explicitly publishes interdisciplinary physics / ML work. **Fallback: TMLR** if the paper reads as more ML-methods than physics.
