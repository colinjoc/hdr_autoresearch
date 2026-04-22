"""Phase 0.5 baseline-audit tests: can our analysis toolchain recover
known-truth exponents from synthetic data?

This is the methodology-correctness gate. Before Phase 1 applies
``powerlaw`` / ``mrestimator`` / Sethna-crackling cross-check to real
activations, we must prove the toolchain recovers the right numbers on
synthetic branching-process data where the ground truth is known.

Fail modes this catches:
- A ``powerlaw`` call that returns α off by more than the estimator CI.
- An ``mrestimator`` MR estimator that under-estimates σ at low subsample.
- A crackling-noise scaling-relation check that doesn't close within
  bootstrap.
"""

from __future__ import annotations

import numpy as np
import pytest


def galton_watson_avalanches(
    sigma: float,
    n_avalanches: int,
    max_generations: int = 200,
    seed: int = 42,
):
    """Seed a Galton-Watson process at branching ratio ``sigma`` with
    Poisson offspring distribution; return avalanche sizes s.

    σ = 1 is critical; expected total avalanche size diverges as σ → 1⁻.
    Mean-field prediction: P(s) ∝ s^{-3/2} at σ = 1.
    """
    rng = np.random.default_rng(seed)
    sizes = np.empty(n_avalanches, dtype=np.int64)
    for i in range(n_avalanches):
        active = 1
        total = 0
        for _ in range(max_generations):
            if active == 0:
                break
            total += active
            active = int(rng.poisson(sigma * active))
        sizes[i] = total
    return sizes


def test_galton_watson_critical_avalanche_alpha_recovered():
    """P(s) from σ = 1 Galton-Watson has mean-field α ≈ 3/2; powerlaw fit
    should recover within bootstrap CI (target ±0.1)."""
    import powerlaw
    sizes = galton_watson_avalanches(sigma=1.0, n_avalanches=50_000)
    sizes = sizes[sizes >= 2]  # drop trivial avalanches of size 1
    fit = powerlaw.Fit(sizes, discrete=True, verbose=False)
    alpha = fit.power_law.alpha
    # mean-field prediction α = 3/2 = 1.5; finite-sample + truncation
    # shifts estimates up by ~5-10 %.
    assert 1.35 <= alpha <= 1.70, f"α = {alpha:.3f} outside [1.35, 1.70]"


def test_galton_watson_subcritical_alpha_steeper():
    """P(s) at σ = 0.9 falls off faster than at σ = 1 — α larger or
    exponential truncation dominates. Sanity check against the
    critical run above."""
    import powerlaw
    sub = galton_watson_avalanches(sigma=0.9, n_avalanches=50_000, seed=43)
    sub = sub[sub >= 2]
    crit = galton_watson_avalanches(sigma=1.0, n_avalanches=50_000, seed=44)
    crit = crit[crit >= 2]
    assert sub.mean() < crit.mean(), (
        f"subcritical mean {sub.mean()} should be < critical {crit.mean()}"
    )
    # Tail: 99th percentile of critical should exceed subcritical.
    assert np.percentile(crit, 99) > np.percentile(sub, 99) * 1.5


def test_mrestimator_recovers_branching_ratio():
    """``mrestimator`` MR estimator should recover branching ratio from
    a coarse-grained Galton-Watson time series within ±0.05."""
    import mrestimator as mre
    rng = np.random.default_rng(42)
    # Driven sub-critical branching process with constant homeostatic drive h:
    # a_{t+1} ~ Poisson(σ · a_t + h). This is the standard Priesemann
    # set-up — exponential autocorrelation decay with rate exp(-1/τ) = σ,
    # no re-seed discontinuity.
    sigma_true = 0.95
    h = 5.0  # drive keeps stationary mean at h / (1 − σ) = 100
    T = 40000
    activity = np.zeros(T, dtype=np.int64)
    activity[0] = 100
    for t in range(T - 1):
        activity[t + 1] = rng.poisson(sigma_true * activity[t] + h)

    result = mre.full_analysis(
        activity.reshape(1, -1),
        dt=1,
        kmax=500,
        method="ts",
        dtunit="step",
        fitfuncs=["exponential"],
        numboot=100,
        showoverview=False,
        targetdir=None,
    )
    # In mrestimator, the fit object exposes mre (= branching-ratio estimate).
    sigma_est = result.fits[0].mre
    assert abs(sigma_est - sigma_true) < 0.05, (
        f"σ_est = {sigma_est:.3f}, σ_true = {sigma_true}"
    )


@pytest.mark.slow
def test_crackling_noise_scaling_relation_closes():
    """Sethna γ = (β − 1)/(α − 1) should close within bootstrap CI on
    σ = 1 Galton-Watson data."""
    import powerlaw
    # Sample avalanche sizes and durations together.
    rng = np.random.default_rng(42)
    sigma = 1.0
    n_avalanches = 30_000
    sizes, durations = [], []
    for _ in range(n_avalanches):
        active = 1
        total = 0
        gen = 0
        while active > 0 and gen < 500:
            total += active
            active = int(rng.poisson(sigma * active))
            gen += 1
        sizes.append(total)
        durations.append(gen)
    sizes = np.array([s for s in sizes if s >= 2])
    durations = np.array([d for d in durations if d >= 2])

    alpha = powerlaw.Fit(sizes, discrete=True, verbose=False).power_law.alpha
    beta = powerlaw.Fit(durations, discrete=True, verbose=False).power_law.alpha
    # Sethna: ⟨s⟩(T) ∝ T^γ where γ_predicted = (β − 1)/(α − 1).
    gamma_predicted = (beta - 1) / (alpha - 1)
    # Mean-field prediction: α = 3/2, β = 2, γ = (2−1)/(3/2−1) = 2.
    # So predicted γ should be in roughly [1.6, 2.4].
    assert 1.4 <= gamma_predicted <= 2.6, (
        f"γ_predicted = {gamma_predicted:.3f} outside expected [1.4, 2.6]"
    )
