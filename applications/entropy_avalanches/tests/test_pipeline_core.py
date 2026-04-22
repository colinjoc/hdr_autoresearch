"""Unit tests for pipeline/activation_cache.py and pipeline/avalanche_detection.py.

TDD discipline: every pipeline module gets a test file; tests written
alongside code, both green before experiments run.
"""

from __future__ import annotations

import numpy as np
import pytest


# ---------- avalanche_detection tests ----------


def test_binarise_threshold_zero():
    from pipeline.avalanche_detection import binarise_activations
    acts = np.array([[-0.5, 0.0, 0.1], [0.0, 0.0, 0.0]])
    b = binarise_activations(acts, threshold=0.0)
    assert b[0, 0] == True  # |-0.5| > 0
    assert b[0, 1] == False
    assert b[0, 2] == True
    assert not b[1].any()


def test_detect_avalanches_simple_run():
    """A binary matrix with one clear avalanche returns size=3, duration=2."""
    from pipeline.avalanche_detection import detect_avalanches
    # Shape (T=5, d=2). Two active tokens in a row, then quiescence.
    binary = np.array(
        [[0, 0], [1, 0], [1, 1], [0, 0], [0, 0]], dtype=bool
    )
    sizes, durations = detect_avalanches(binary)
    assert sizes.tolist() == [3]  # 1 + 2 = 3 events
    assert durations.tolist() == [2]  # bins 1-2


def test_detect_avalanches_multiple():
    from pipeline.avalanche_detection import detect_avalanches
    binary = np.array(
        [[1], [1], [0], [0], [1], [0], [1], [1], [1]], dtype=bool
    )
    sizes, durations = detect_avalanches(binary)
    assert sizes.tolist() == [2, 1, 3]
    assert durations.tolist() == [2, 1, 3]


def test_detect_avalanches_all_quiescent():
    from pipeline.avalanche_detection import detect_avalanches
    binary = np.zeros((10, 4), dtype=bool)
    sizes, durations = detect_avalanches(binary)
    assert len(sizes) == 0
    assert len(durations) == 0


def test_detect_avalanches_binning():
    """bin_size > 1 should coarsen the time axis."""
    from pipeline.avalanche_detection import detect_avalanches
    binary = np.array(
        [[1], [0], [1], [0], [1], [0], [0], [0]], dtype=bool
    )
    # bin_size=2 -> [1, 1, 1, 0] (four 2-bins); detect finds one avalanche
    # of duration 3 (size 3).
    sizes, durations = detect_avalanches(binary, bin_size=2)
    assert len(sizes) == 1
    assert sizes[0] == 3
    assert durations[0] == 3


def test_threshold_plateau_returns_all_thresholds():
    from pipeline.avalanche_detection import threshold_plateau
    acts = np.random.RandomState(0).randn(100, 16).astype(np.float32)
    result = threshold_plateau(acts, thresholds=[0.0, 0.5, 1.0, 2.0])
    assert set(result.keys()) == {0.0, 0.5, 1.0, 2.0}
    # Higher thresholds should produce fewer total events.
    sizes_low = result[0.0][0].sum()
    sizes_high = result[2.0][0].sum()
    assert sizes_low >= sizes_high


# ---------- activation_cache tests ----------


@pytest.mark.network
@pytest.mark.slow
def test_cache_gpt2_small_shapes():
    """GPT-2-small cache produces 12 layers × (≤ N_tokens, 768)."""
    from pipeline.activation_cache import cache_activations
    cache = cache_activations(
        "gpt2",
        texts=["The quick brown fox jumps over the lazy dog."],
        max_length=16,
        batch_size=1,
    )
    assert cache.d_model == 768
    assert set(cache.layer_activations.keys()) == set(range(12))
    assert cache.layer_activations[0].shape[0] == cache.n_tokens


@pytest.mark.network
@pytest.mark.slow
def test_random_init_gives_different_activations():
    """at-init control: random weights should produce activations with
    statistics distinct from trained weights on the same input."""
    from pipeline.activation_cache import cache_activations
    texts = ["Once upon a time, in a far away land, "]
    trained = cache_activations("gpt2", texts, max_length=16, random_init=False)
    init = cache_activations("gpt2", texts, max_length=16, random_init=True)
    # On any layer, std at init will differ markedly from trained.
    trained_std = np.std(trained.layer_activations[5])
    init_std = np.std(init.layer_activations[5])
    assert abs(trained_std - init_std) > 0.1, (
        f"trained σ {trained_std:.3f} too close to init σ {init_std:.3f}"
    )
