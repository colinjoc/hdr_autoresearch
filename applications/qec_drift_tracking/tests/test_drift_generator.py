"""Tests for inject_drift in phase_diagram.py.

Invariants tested:
- Output shape matches input (known-truth shape invariant).
- At zero amplitude + T=1, all rates equal base rate within floating-point tolerance.
- Ground-truth rate trajectory has correct dtype and range.
- Detector events are 0/1 valued.
- Determinism: same seed → identical output.
- Different seeds → different output.
"""
from __future__ import annotations

import numpy as np
import pytest

from phase_diagram import inject_drift


def test_inject_drift_shape(small_H):
    T = 100
    events_base = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    events, gt = inject_drift(events_base, small_H, drift_timescale_s=60.0,
                              drift_amplitude=0.1, shot_dt_s=1e-3, seed=42)
    assert events.shape == (T, small_H.shape[0])
    assert gt.shape == (T, small_H.shape[1])
    assert events.dtype == np.uint8


def test_inject_drift_zero_amplitude_constant(small_H):
    """At zero drift amplitude, all rates should equal base rate exactly."""
    T = 5
    events_base = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    _, gt = inject_drift(events_base, small_H, drift_timescale_s=1.0,
                         drift_amplitude=0.0, shot_dt_s=1e-3, seed=42)
    base_rate = 1e-3
    assert np.allclose(gt, base_rate, atol=1e-12), \
        f"gt should be constant at 1e-3 when amplitude=0; got range [{gt.min()}, {gt.max()}]"


def test_inject_drift_events_are_binary(small_H):
    T = 50
    events_base = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    events, _ = inject_drift(events_base, small_H, drift_timescale_s=60.0,
                             drift_amplitude=0.2, shot_dt_s=1e-3, seed=42)
    assert set(np.unique(events).tolist()).issubset({0, 1})


def test_inject_drift_deterministic_same_seed(small_H):
    T = 20
    e0 = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    events1, gt1 = inject_drift(e0, small_H, 60.0, 0.1, 1e-3, seed=42)
    events2, gt2 = inject_drift(e0, small_H, 60.0, 0.1, 1e-3, seed=42)
    np.testing.assert_array_equal(events1, events2)
    np.testing.assert_array_equal(gt1, gt2)


def test_inject_drift_different_seeds_differ(small_H):
    T = 20
    e0 = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    events1, _ = inject_drift(e0, small_H, 60.0, 0.2, 1e-3, seed=42)
    events2, _ = inject_drift(e0, small_H, 60.0, 0.2, 1e-3, seed=1337)
    assert not np.array_equal(events1, events2), "Different seeds should produce different outputs"


def test_inject_drift_rates_positive(small_H):
    """Rates should stay positive (clipped)."""
    T = 50
    e0 = np.zeros((T, small_H.shape[0]), dtype=np.uint8)
    _, gt = inject_drift(e0, small_H, 60.0, 2.0, 1e-3, seed=42)  # very large amplitude
    assert (gt > 0).all(), "Rates must stay positive under large drift"
