"""Tests for subspace.py and nulls.py."""

from __future__ import annotations

import numpy as np
import pytest


def test_participation_ratio_rank_4_plus_noise():
    from pipeline.subspace import participation_ratio
    rng = np.random.default_rng(0)
    d = 64
    T = 2000
    X = rng.normal(size=(T, 4)) @ rng.normal(size=(4, d)) + 0.1 * rng.normal(size=(T, d))
    pr = participation_ratio(X)
    assert 3.0 < pr < 10.0


def test_subspace_sigma_recovers_seeded_sigma_on_synthetic():
    """Synthetic BP: σ_K and σ_ambient both recover 0.95 on a uniform-σ
    vector process (true-null case, no subspace structure)."""
    from pipeline.subspace import subspace_sigma
    rng = np.random.default_rng(42)
    d = 16
    T = 30_000
    sigma_true = 0.95
    h = 5.0
    A = np.zeros((T, d), dtype=np.int64)
    A[0] = int(h / max(1 - sigma_true, 1e-3))
    for t in range(T - 1):
        A[t + 1] = rng.poisson(sigma_true * A[t] + h)
    r = subspace_sigma(A.astype(np.float64), K=4, method="participation_ratio")
    assert abs(r.sigma_K - sigma_true) < 0.08
    assert abs(r.sigma_ambient - sigma_true) < 0.08


def test_shuffle_null_runs_on_synthetic_burst_data():
    """Construct temporally-bursty activations where real structure
    exists but magnitudes are calibrated for avalanche detection.

    This is a minimal smoke test of the ``shuffle_null`` plumbing. Real
    empirical null-rejection quality is tested on actual LLM activations
    in Phase 2.
    """
    from pipeline.nulls import shuffle_null
    rng = np.random.default_rng(42)
    T, d = 5000, 32
    # Synthesize bursty activity: occasional ~1.0 spikes, otherwise ~0.1 noise
    A = 0.05 * rng.normal(size=(T, d))
    # Inject bursts at random times (~200 bursts covering ~1-3 tokens each)
    for start in rng.integers(10, T - 10, size=200):
        burst_len = rng.integers(1, 4)
        A[start : start + burst_len, : rng.integers(4, 16)] += 1.0
    result = shuffle_null(A, threshold=0.5, bin_size=1, rng_seed=0)
    # Minimum-viable assertion: result is well-formed.
    assert result.real_alpha == result.real_alpha  # i.e. not NaN
    # Shuffled data with same marginals often still produces a result;
    # the plumbing works.
    assert hasattr(result, "distinguishable")
