"""Tests for evaluate.py — focus on CI correctness."""
from __future__ import annotations

import numpy as np
import pytest

from evaluate import risk_diff_with_ci, classifier_metrics


def test_risk_diff_identical_groups_has_ci_spanning_zero():
    # Identical observed rates → bootstrap CI must span zero by construction.
    y_t = np.array([1] * 30 + [0] * 70)   # 30% rate
    y_c = np.array([1] * 300 + [0] * 700)  # 30% rate
    rd, lo, hi = risk_diff_with_ci(y_t, y_c, n_boot=1000, seed=1)
    assert abs(rd) < 1e-9
    assert lo < 0 < hi


def test_risk_diff_large_positive_effect():
    rng = np.random.default_rng(0)
    y_t = rng.binomial(1, 0.60, size=500)
    y_c = rng.binomial(1, 0.30, size=500)
    rd, lo, hi = risk_diff_with_ci(y_t, y_c, n_boot=500, seed=1)
    assert rd > 0.20
    assert lo > 0  # CI clearly above zero


def test_classifier_metrics_perfect_classifier():
    y_true = np.array([0, 0, 1, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.7, 0.8, 0.9])
    m = classifier_metrics(y_true, y_prob)
    assert m["roc_auc"] == 1.0
    assert m["brier"] < 0.1
