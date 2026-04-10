"""Tests for evaluate.py — verify evaluation harness."""

import sys
from pathlib import Path

import numpy as np
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from evaluate import compute_metrics


class TestComputeMetrics:
    def test_perfect_predictions(self):
        """Perfect predictions should give MAE=0, R2=1."""
        y_true = np.array([10, 20, 30, 40, 50], dtype=float)
        y_pred = np.array([10, 20, 30, 40, 50], dtype=float)
        metrics = compute_metrics(y_true, y_pred)
        assert metrics["mae"] == 0.0
        assert metrics["r2"] == 1.0

    def test_constant_prediction(self):
        """Predicting the mean should give R2=0."""
        y_true = np.array([0, 10, 20, 30, 40], dtype=float)
        y_pred = np.full(5, 20.0)
        metrics = compute_metrics(y_true, y_pred)
        assert abs(metrics["r2"]) < 0.01

    def test_binary_classification_metrics(self):
        """Binary classification for delay>30 should work."""
        y_true = np.array([10, 20, 35, 45, 50], dtype=float)
        y_pred = np.array([15, 25, 40, 50, 55], dtype=float)
        metrics = compute_metrics(y_true, y_pred)

        # 3 flights truly delayed >30, predictions should match
        assert metrics["n_delayed_30"] == 3
        assert metrics["recall_30"] == 1.0  # all truly delayed predicted as delayed

    def test_all_metrics_present(self):
        y_true = np.random.RandomState(42).uniform(-5, 60, 100)
        y_pred = y_true + np.random.RandomState(43).normal(0, 10, 100)
        metrics = compute_metrics(y_true, y_pred)

        expected_keys = [
            "mae", "rmse", "r2", "median_ae",
            "auc_30", "f1_30", "precision_30", "recall_30",
            "n_total", "n_delayed_30",
        ]
        for key in expected_keys:
            assert key in metrics, f"Missing metric: {key}"

    def test_mae_positive(self):
        y_true = np.array([10, 20, 30], dtype=float)
        y_pred = np.array([15, 18, 35], dtype=float)
        metrics = compute_metrics(y_true, y_pred)
        assert metrics["mae"] > 0
