"""Phase 0.5 baseline-audit tests for entropy_effective_dimension.

The paper claims that on a *linearly-projected* residual stream (the top-K
PC subspace per Fontenele 2024), the MR-estimator branching ratio σ crosses
1 at training checkpoints where the ambient σ is off-critical. For that
claim to be interpretable, the MR estimator must be correct on linear
projections of branching-process time-series — a fact that Wilting-
Priesemann 2018 proves at the theory level but we must verify numerically
on synthetic data before trusting it on real activations.

Also: the Phase 0.25 publishability review's Phase 1 Day 1 kill gate is a
"dynamic-range pilot" — P(s) on Σ_K must span ≥ 2.5 decades or Fontenele's
1.5-decade-collapse K-selection rule is degenerate. Here we confirm that
synthetic critical avalanches with enough sample support do span that
range; Phase 1 replaces synthetic with real Pythia residual-stream data.
"""

from __future__ import annotations

import numpy as np
import pytest


def driven_branching_process_vector(
    d: int, sigma: float, h: float, T: int, seed: int = 42
):
    """Vector-valued driven branching process: d independent streams, each
    at branching ratio sigma. Returns (T, d) int array."""
    rng = np.random.default_rng(seed)
    activity = np.zeros((T, d), dtype=np.int64)
    activity[0] = int(h / max(1 - sigma, 1e-3))
    for t in range(T - 1):
        activity[t + 1] = rng.poisson(sigma * activity[t] + h)
    return activity


def test_mr_estimator_on_linear_projection():
    """Key claim underlying the paper: MR σ on a linear projection of a
    vector-valued branching process equals MR σ on the raw stream.

    This is the Wilting-Priesemann 2018 r_k = m^k linearity property at
    the practical level: project (T, d) onto a random unit vector w, run
    MR on the scalar time-series, recover the seeded σ.
    """
    import mrestimator as mre
    sigma_true = 0.95
    d = 32
    activity = driven_branching_process_vector(d=d, sigma=sigma_true, h=5.0, T=40_000)
    # Project onto a random unit vector (standard Gaussian, normalised).
    rng = np.random.default_rng(0)
    w = rng.normal(size=d)
    w /= np.linalg.norm(w)
    projected = activity.astype(np.float64) @ w

    result = mre.full_analysis(
        projected.reshape(1, -1),
        dt=1, kmax=500, method="ts",
        dtunit="step", fitfuncs=["exponential"],
        numboot=100, showoverview=False, targetdir=None,
    )
    sigma_est = result.fits[0].mre
    assert abs(sigma_est - sigma_true) < 0.05, (
        f"σ_est on projection = {sigma_est:.3f}, true = {sigma_true}"
    )


def test_mr_estimator_on_top_K_PC_reconstruction():
    """Fontenele 2024 uses reconstructed-scalar = sum of top-K PC projections
    of the population activity vector. Test that MR σ on that reconstructed
    scalar equals σ on the raw activity (all PCs have the same σ here
    because we seeded identical processes — the right null)."""
    import mrestimator as mre
    sigma_true = 0.95
    d = 32
    activity = driven_branching_process_vector(
        d=d, sigma=sigma_true, h=5.0, T=40_000, seed=123
    )
    # Centre + PCA
    X = activity.astype(np.float64)
    X -= X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    # Reconstruct scalar from top-K PCs: sum of projections onto first K PCs.
    K = 4
    top_K = (U[:, :K] * S[:K]) @ Vt[:K, :]  # (T, d)
    scalar = top_K.sum(axis=1)

    result = mre.full_analysis(
        scalar.reshape(1, -1),
        dt=1, kmax=500, method="ts",
        dtunit="step", fitfuncs=["exponential"],
        numboot=100, showoverview=False, targetdir=None,
    )
    sigma_est = result.fits[0].mre
    assert abs(sigma_est - sigma_true) < 0.05, (
        f"σ_est on top-{K}-PC reconstruction = {sigma_est:.3f}, "
        f"true = {sigma_true}"
    )


def test_critical_P_of_s_spans_2_decades():
    """Phase 0.25 Day-1 kill gate: P(s) must span ≥ 2.5 decades for
    Fontenele's 1.5-decade-collapse K-selection to work. On synthetic
    σ = 1 Galton-Watson, 50K avalanches easily give ≥ 3 decades."""
    rng = np.random.default_rng(42)
    sigma = 1.0
    n = 50_000
    sizes = np.empty(n, dtype=np.int64)
    for i in range(n):
        active = 1
        total = 0
        gen = 0
        while active > 0 and gen < 500:
            total += active
            active = int(rng.poisson(sigma * active))
            gen += 1
        sizes[i] = total
    sizes = sizes[sizes >= 2]
    min_size = float(sizes.min())
    max_size = float(np.percentile(sizes, 99.9))
    decades = np.log10(max_size / min_size)
    assert decades >= 2.5, (
        f"P(s) spans {decades:.2f} decades, need ≥ 2.5 for Fontenele K-selection"
    )


def test_participation_ratio_sane():
    """Participation ratio PR = (Σ λ)² / Σ λ² of the covariance spectrum.
    For isotropic noise (identity covariance) PR = d; for low-rank data
    PR → rank. Used as D_eff in the subspace-criticality pipeline."""
    rng = np.random.default_rng(0)
    d = 64
    T = 2000
    # Rank-4 data + noise.
    low_rank = rng.normal(size=(T, 4)) @ rng.normal(size=(4, d))
    noise = 0.1 * rng.normal(size=(T, d))
    X = low_rank + noise
    cov = np.cov(X, rowvar=False)
    lam = np.linalg.eigvalsh(cov)
    lam = lam[lam > 1e-10]
    pr = (lam.sum() ** 2) / (lam ** 2).sum()
    # True PR for rank-4+noise at this SNR should be close to 4-6
    assert 3.0 < pr < 10.0, f"PR = {pr:.2f} outside expected [3, 10]"
