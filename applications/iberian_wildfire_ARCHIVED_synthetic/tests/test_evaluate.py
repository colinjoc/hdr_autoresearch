"""Tests for evaluation harness — Iberian wildfire VLF prediction."""

import sys
from pathlib import Path

import numpy as np
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from evaluate import compute_metrics


class TestComputeMetrics:
    """Test metric computation."""

    def test_perfect_predictions(self):
        y_true = np.array([0, 0, 1, 1])
        y_proba = np.array([0.1, 0.2, 0.8, 0.9])
        metrics = compute_metrics(y_true, y_proba)
        assert metrics["auc"] == 1.0
        assert metrics["recall"] == 1.0
        assert metrics["precision"] == 1.0

    def test_random_predictions(self):
        rng = np.random.RandomState(42)
        y_true = rng.randint(0, 2, 100)
        y_proba = rng.random(100)
        metrics = compute_metrics(y_true, y_proba)
        # AUC should be around 0.5 for random
        assert 0.3 < metrics["auc"] < 0.7

    def test_all_same_label(self):
        y_true = np.zeros(10)
        y_proba = np.random.random(10)
        metrics = compute_metrics(y_true, y_proba)
        # AUC should be NaN when only one class present
        assert np.isnan(metrics["auc"])

    def test_n_positive_correct(self):
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        metrics = compute_metrics(y_true, y_proba)
        assert metrics["n_positive"] == 3
        assert metrics["n_total"] == 5

    def test_metrics_keys(self):
        y_true = np.array([0, 1])
        y_proba = np.array([0.3, 0.7])
        metrics = compute_metrics(y_true, y_proba)
        expected_keys = {"auc", "pr_auc", "f2", "f1", "precision",
                         "recall", "accuracy", "n_positive", "n_total"}
        assert expected_keys.issubset(set(metrics.keys()))
