# Design Variables — Bérut Finite-Time Refit

This project has no physical design-variable space in the usual HDR sense (no hyperparameter tuning, no architecture search). The free parameters of the analysis are:

## Fit parameters

- **B** — the finite-time Landauer coefficient. Free parameter in the primary fit to ⟨Q_diss⟩(τ) = k_B T ln 2 + B k_B T / τ on the ten Bérut 2012 points. Prior (uninformative): log-uniform over [1, 100]; posterior will be reported with 95% bootstrap CI.

## Derived / fixed quantities (not tuned)

- **r** — optical-trap well-depth asymmetry ratio. Reconstructed from the Bérut 2012 equilibrium histogram of particle position (published qualitatively as U(x) plots, not as polynomial coefficients). Reconstructed r carries a 95% CI of roughly 0.7–1.5 at the high barrier, 0.5–2.0 at the low barrier. Propagated, not fitted.
- **T** — 300 K, fixed.
- **cycle time τ** — ten published values from 5 ms to 40 s, fixed.
- **⟨Q_diss⟩ per cycle** — ten published values with Bérut-reported uncertainty ±0.15 k_B T. Used as observations, not fitted.

## Procedural choices (also free, must be committed in advance)

- **Fit method:** weighted nonlinear least squares with bootstrap CI, vs Bayesian nonlinear regression with flat log-prior. Default: weighted nonlinear least squares; Bayesian fit as robustness check.
- **Weighting:** published per-point uncertainty vs heteroscedastic inference from τ-dependent noise. Default: published per-point.
- **Extraction of r:** Boltzmann histogram inversion vs Kramers-rate asymmetry vs driven-response. Default: Boltzmann histogram inversion; other two as cross-checks.
- **Discrimination metric:** does the 95% CI on empirical B exclude B = π²? Does it exclude B(r)? Pre-registered before the fit is computed.

## Ansatz families considered

This project is Option A (dataset-based) not Option D (symbolic). The "model family" analogue for Phase 1 tournament purposes is the **functional form fitted**:

- F1: W(τ) = k_B T ln 2 + B k_B T / τ (Proesmans form, target of the analysis)
- F2: W(τ) = k_B T ln 2 + B k_B T / τ + C · (k_B T)² / τ² (next-order correction, Van Vu–Saito)
- F3: W(τ) = a + b / τ^α (power-law, α as a free parameter)
- F4: W(τ) = a + b · exp(-τ/τ₀) (activated-process form, as a sanity-check baseline)

The tournament asks which form best fits the data; F1 is expected to win, but F2 vs F1 is the non-trivial comparison. F4 is the linear-model-sanity-check equivalent.
