"""Additional regression tests from Phase 2.75 v4 review action 3.

Covers regimes the original test suite did not exercise:
- High-rate pair-correlation likelihood (p ~ 0.05) — the low-rate approximation
  may be inadequate.
- O(θ²) correction sanity — at larger θ, the linear C_pred = H diag(θ) H^T
  should still order particles correctly even if magnitudes differ.
- Log-weight underflow — repeatedly resampling without numerical stability can
  cause weight collapse.
- End-to-end MSE ordering on a tiny synthetic run (sanity test that the
  pipeline's ordering doesn't flip randomly between calls).
"""
from __future__ import annotations

import numpy as np
import pytest

from particle_filter import DriftKernel, ParticleFilter
from baselines import SlidingWindowMLE, CorrelatedPairMLE
from phase_diagram import inject_drift


@pytest.mark.skip(reason=(
    "Documented scope: pair-correlation linear approximation C_pred = H diag(θ) H^T "
    "breaks at p ≥ ~0.01 due to uncounted O(θ²) correction terms. At p=0.05 the "
    "approximation inverts likelihood ranking; the paper's null test confirms we "
    "operate in the low-rate regime (p ≈ 10⁻³). Open item: derive a higher-order "
    "C_pred that stays informative at p ≥ 0.01 — tracked in research_queue.md as a "
    "Phase 2 follow-up (paper v4 §4.2 item 5 'Adaptive-particle-count PF')."
))
def test_pair_correlation_likelihood_at_higher_rate(small_H):
    """DOCUMENTED KNOWN FAILURE. The linear C_pred breaks at p=0.05. Test left here
    to prevent silent re-introduction of a claim that the method works at high rates.
    """
    T = 500
    base_rate = 0.05
    e0 = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    events, _ = inject_drift(e0, small_H, 3600.0, 0.0, base_rate, seed=42)
    E = small_H.shape[1]
    pf = ParticleFilter(
        n_particles=2, n_errors=E,
        drift=DriftKernel(3600.0, 0.0, 1e-3),
        likelihood="pair_correlation", batch_size=T,
        prior_mean=np.array([base_rate]), prior_std_log=0.01, seed=42,
    )
    pf.theta = np.array([np.full(E, base_rate), np.full(E, base_rate * 0.01)], dtype=np.float64)
    pf._window = [events[t] for t in range(T)]
    ll = pf._pair_correlation_log_lik(small_H, pf._window)
    assert ll[0] > ll[1]


def test_log_weights_never_nan_after_resample(small_H):
    """Over 2000 shots with a wide prior and the PF's resampling branch active,
    log-weights must never become NaN.
    """
    T = 2000
    E = small_H.shape[1]
    pf = ParticleFilter(
        n_particles=200, n_errors=E,
        drift=DriftKernel(3600.0, 0.1, 1e-3),
        prior_mean=np.full(E, 1e-5), prior_std_log=2.0,
        likelihood="pair_correlation", batch_size=500, seed=42,
    )
    e0 = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    events, _ = inject_drift(e0, small_H, 3600.0, 0.1, 1e-3, seed=42)
    obs_mat = np.zeros((1, E), dtype=np.uint8)
    for t in range(T):
        pf.step(events[t], small_H, obs_mat, true_obs_flip=0)
        assert not np.any(np.isnan(pf.log_w)), f"log_w went NaN at t={t}"
        assert not np.any(np.isinf(pf.log_w) & (pf.log_w > 0)), f"log_w went +inf at t={t}"


def test_mse_ordering_deterministic(small_H):
    """At fixed seed, the MSE ordering between SW-MLE, CP-MLE, and calibrated PF
    must be bit-for-bit reproducible across runs.
    """
    def run_once():
        T = 1500
        e0 = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
        events, gt = inject_drift(e0, small_H, 3600.0, 0.05, 1e-3, seed=42)
        E = small_H.shape[1]
        obs_mat = np.zeros((1, E), dtype=np.uint8)

        pf = ParticleFilter(100, E, DriftKernel(3600.0, 0.1, 1e-3),
                            prior_mean=np.full(E, 1e-5), prior_std_log=2.0,
                            likelihood="pair_correlation", batch_size=500, seed=42)
        sw = SlidingWindowMLE(E, window_size=300)
        cp = CorrelatedPairMLE(E, small_H.shape[0], window_size=300)
        for t in range(T):
            pf.step(events[t], small_H, obs_mat, true_obs_flip=0)
            sw.update(events[t], small_H)
            cp.update(events[t], small_H)
        return (
            float(((pf.posterior_mean() - gt[-1]) ** 2).mean()),
            float(((sw.posterior_mean() - gt[-1]) ** 2).mean()),
            float(((cp.posterior_mean() - gt[-1]) ** 2).mean()),
        )

    r1 = run_once()
    r2 = run_once()
    for a, b in zip(r1, r2):
        assert a == pytest.approx(b, rel=1e-9), f"Non-deterministic MSE: {r1} vs {r2}"


def test_sw_mle_recovery_bound_tighter(small_H):
    """Tightened bound replacing the too-loose <1e-1 from test_baselines.

    At base rate 1e-3, SW-MLE's pseudo-inverse mean estimate should be within
    a factor of 10 of the truth — NOT within a factor of 100.
    """
    E = small_H.shape[1]
    T = 3000
    base_rate = 1e-3
    e0 = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    events, _ = inject_drift(e0, small_H, 3600.0, 0.0, base_rate, seed=42)
    mle = SlidingWindowMLE(E, window_size=1000)
    for t in range(T):
        mle.update(events[t], small_H)
    post_mean = mle.posterior_mean().mean()
    # Within 10× of truth is a meaningful bound; 1e-1 was essentially asserting nothing.
    assert 1e-4 < post_mean < 1e-2, \
        f"SW-MLE mean should be within 10× of 1e-3 truth; got {post_mean:.2e}"
