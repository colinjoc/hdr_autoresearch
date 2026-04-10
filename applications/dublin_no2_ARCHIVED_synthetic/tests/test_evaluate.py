"""
Tests for the evaluation harness.

Verifies that CV, holdout, and metric computation work correctly
for the Dublin NO2 source attribution project.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from evaluate import compute_metrics


class TestComputeMetrics:
    """Test metric computation for regression and classification."""

    def test_perfect_regression(self):
        y_true = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        y_pred = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        metrics = compute_metrics(y_true, y_pred)
        assert metrics["mae"] == 0.0
        assert metrics["r2"] == 1.0

    def test_constant_prediction_r2(self):
        y_true = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        y_pred = np.full(5, 30.0)
        metrics = compute_metrics(y_true, y_pred)
        assert metrics["r2"] == 0.0

    def test_mae_positive(self):
        y_true = np.array([10.0, 20.0, 30.0])
        y_pred = np.array([12.0, 18.0, 33.0])
        metrics = compute_metrics(y_true, y_pred)
        assert metrics["mae"] > 0

    def test_exceedance_auc_perfect(self):
        y_true_cont = np.array([10.0, 15.0, 30.0, 35.0])
        y_pred_cont = np.array([10.0, 15.0, 30.0, 35.0])  # > 25 = exceedance
        metrics = compute_metrics(
            y_true=y_true_cont,
            y_pred=y_pred_cont,
            exceedance_threshold=25.0,
        )
        assert metrics["exceedance_auc"] > 0.9

    def test_metrics_dict_has_required_keys(self):
        y_true = np.random.RandomState(0).normal(20, 5, 100)
        y_pred = y_true + np.random.RandomState(1).normal(0, 2, 100)
        metrics = compute_metrics(y_true, y_pred)
        required = ["mae", "rmse", "r2", "mbe"]
        for key in required:
            assert key in metrics, f"Missing metric: {key}"
