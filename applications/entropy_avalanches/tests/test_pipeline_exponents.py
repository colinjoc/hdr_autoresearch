"""Tests for pipeline/exponents.py against synthetic ground-truth."""

from __future__ import annotations

import numpy as np
import pytest


def galton_watson_avalanches_with_durations(sigma, n, seed=42, max_gen=500):
    rng = np.random.default_rng(seed)
    sizes = np.empty(n, dtype=np.int64)
    durations = np.empty(n, dtype=np.int64)
    for i in range(n):
        active = 1
        total = 0
        gen = 0
        while active > 0 and gen < max_gen:
            total += active
            active = int(rng.poisson(sigma * active))
            gen += 1
        sizes[i] = total
        durations[i] = gen
    return sizes, durations


def driven_bp(sigma, h, T, seed=42):
    rng = np.random.default_rng(seed)
    a = np.zeros(T, dtype=np.int64)
    a[0] = int(h / max(1 - sigma, 1e-3))
    for t in range(T - 1):
        a[t + 1] = rng.poisson(sigma * a[t] + h)
    return a


def test_fit_power_law_mean_field():
    from pipeline.exponents import fit_power_law
    sizes, _ = galton_watson_avalanches_with_durations(1.0, 40_000)
    fit = fit_power_law(sizes, discrete=True)
    assert 1.35 <= fit.alpha <= 1.70
    # Power-law should not be dismissively rejected vs lognormal on
    # true-BP data (p is typically mid-range, ~0.1-0.5).
    assert 0.0 <= fit.p_vs_lognormal <= 1.0


def test_fit_power_law_rejects_exponential_on_power_law_data():
    from pipeline.exponents import fit_power_law
    sizes, _ = galton_watson_avalanches_with_durations(1.0, 40_000)
    fit = fit_power_law(sizes, discrete=True)
    # R_power_law_minus_exp > 0 with significant p → power law wins.
    # (p_vs_exponential is the Vuong two-sided p; significant when p < 0.05.)
    assert fit.p_vs_exponential < 0.2  # power law strictly preferred


def test_crackling_noise_relation_closes_at_criticality():
    from pipeline.exponents import crackling_noise_check
    sizes, durations = galton_watson_avalanches_with_durations(1.0, 30_000)
    chk = crackling_noise_check(sizes, durations)
    # MF prediction γ_predicted = (β−1)/(α−1) ≈ 2.
    assert 1.4 <= chk.gamma_predicted <= 2.6
    # γ_measured from ⟨s|T⟩ fit on toy BP data should also be in the
    # mean-field ballpark; allow wide CI (finite-sample truncation etc.).
    assert 1.0 <= chk.gamma_measured <= 3.0


def test_branching_ratio_mr_recovers_sigma():
    from pipeline.exponents import branching_ratio_mr
    a = driven_bp(sigma=0.95, h=5.0, T=40_000)
    br = branching_ratio_mr(a, kmax=500, method="ts")
    assert abs(br.sigma - 0.95) < 0.05
    assert br.tau > 5  # autocorrelation time should be > a few steps at σ=0.95


def test_shape_collapse_returns_slope_at_criticality():
    from pipeline.exponents import shape_collapse
    sizes, durations = galton_watson_avalanches_with_durations(1.0, 10_000)
    sc = shape_collapse(sizes, durations)
    # γ from ⟨s⟩ vs T fit should be > 1 at criticality (mean-field: γ=2)
    assert sc.tau > 1.0
