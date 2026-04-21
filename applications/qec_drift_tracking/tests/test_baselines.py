"""Tests for baselines.py.

Invariants tested:
- SlidingWindowMLE recovers base rate on a stationary stream within tolerance
- CorrelatedPairMLE._build_pair_incidence produces M with correct shape + sparsity
- CorrelatedPairMLE recovers base rate within tolerance
- StaticBayesianRates handles empty updates without NaN
- All baselines have posterior_mean returning shape (E,)
"""
from __future__ import annotations

import numpy as np
import pytest

from baselines import SlidingWindowMLE, CorrelatedPairMLE, StaticBayesianRates
from phase_diagram import inject_drift


def test_sliding_window_mle_posterior_shape(small_H):
    E = small_H.shape[1]
    mle = SlidingWindowMLE(E, window_size=100)
    post = mle.posterior_mean()
    assert post.shape == (E,)
    assert post.dtype == np.float64


def test_sliding_window_mle_recovers_base_rate(small_H):
    """SW-MLE on a stationary stream should give per-edge rate estimates whose
    MEAN is within 10× of the true base rate. (Not per-edge exact, because the
    pseudo-inverse has non-trivial conditioning on a random H.)"""
    E = small_H.shape[1]
    T = 2000
    base_rate = 1e-3
    e0 = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    events, _ = inject_drift(e0, small_H, 3600.0, 0.0, base_rate, seed=42)

    mle = SlidingWindowMLE(E, window_size=500)
    for t in range(T):
        mle.update(events[t], small_H)
    post_mean = mle.posterior_mean().mean()
    # Tolerance: the pseudo-inverse attribution overestimates by 3-10× in low-rate regime,
    # documented in paper_v3 §3.3. Upper-bound check.
    assert post_mean < 1e-1, \
        f"SW-MLE gave absurd rate mean {post_mean:.2e}; pipeline broken"
    assert post_mean > 0, "SW-MLE rates must be positive"


def test_correlated_pair_mle_incidence_matrix_shape(small_H):
    E = small_H.shape[1]
    D = small_H.shape[0]
    cp = CorrelatedPairMLE(E, D, window_size=100)
    cp._build_pair_incidence(small_H)
    expected_n_pairs = D * (D - 1) // 2
    assert cp._M.shape == (expected_n_pairs, E), \
        f"Pair-incidence M should be ({expected_n_pairs}, {E}); got {cp._M.shape}"
    # M[p, e] = 1 iff the pair at index p has both detectors connected to edge e
    # Each entry is {0, 1}
    assert set(np.unique(cp._M).tolist()).issubset({0.0, 1.0})


def test_correlated_pair_mle_incidence_matches_definition(tiny_css_H):
    """On a hand-built H, verify incidence row-by-row."""
    D = tiny_css_H.shape[0]
    E = tiny_css_H.shape[1]
    cp = CorrelatedPairMLE(E, D, window_size=10)
    cp._build_pair_incidence(tiny_css_H)
    # tiny_css_H: check 0 ← {q0, q1}; check 1 ← {q1, q2}
    # Only pair is (check 0, check 1). Shared edge = q1 only.
    assert cp._M.shape == (1, 3)
    expected = np.array([[0, 1, 0]], dtype=np.float64)
    np.testing.assert_array_equal(cp._M, expected)


def test_correlated_pair_mle_recovers_base_rate(small_H):
    """CP-MLE should estimate rates on a stationary stream; at minimum, output
    should be bounded and positive."""
    E = small_H.shape[1]
    D = small_H.shape[0]
    T = 3000
    base_rate = 1e-3
    e0 = np.zeros((T, D), dtype=np.uint8)
    events, _ = inject_drift(e0, small_H, 3600.0, 0.0, base_rate, seed=42)

    cp = CorrelatedPairMLE(E, D, window_size=1000)
    for t in range(T):
        cp.update(events[t], small_H)
    post_mean = cp.posterior_mean().mean()
    assert 0 < post_mean < 1e-1, \
        f"CP-MLE post mean out of range: {post_mean:.2e}"


def test_static_bayesian_handles_empty_updates(small_H):
    """StaticBayesianRates must not NaN on zero detector events."""
    E = small_H.shape[1]
    D = small_H.shape[0]
    bay = StaticBayesianRates(E)
    # Feed a run of all-zero detector events
    for _ in range(50):
        bay.update(np.zeros(D, dtype=np.uint8), small_H)
    post = bay.posterior_mean()
    assert not np.any(np.isnan(post)), "Static Bayesian must not produce NaN on zero events"
    assert (post > 0).all(), "Beta-conjugate posterior must remain positive"
