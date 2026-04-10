"""Tests for evaluate.py — verify evaluation harness correctness."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import generate_synthetic_ber_data, add_derived_features
from evaluate import compute_metrics, run_cv


@pytest.fixture
def small_df():
    df = generate_synthetic_ber_data(n_records=500, seed=42)
    return add_derived_features(df)


class TestComputeMetrics:
    def test_perfect_prediction(self):
        y_true = np.array([100.0, 200.0, 300.0])
        y_pred = np.array([100.0, 200.0, 300.0])
        metrics = compute_metrics(y_true, y_pred)
        assert metrics["mae"] == 0.0
        assert metrics["rmse"] == 0.0
        assert metrics["r2"] == 1.0

    def test_imperfect_prediction(self):
        y_true = np.array([100.0, 200.0, 300.0])
        y_pred = np.array([110.0, 190.0, 310.0])
        metrics = compute_metrics(y_true, y_pred)
        assert metrics["mae"] == pytest.approx(10.0)
        assert metrics["r2"] < 1.0
        assert metrics["r2"] > 0.0

    def test_metrics_have_expected_keys(self):
        y_true = np.array([100.0, 200.0])
        y_pred = np.array([110.0, 190.0])
        metrics = compute_metrics(y_true, y_pred)
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "r2" in metrics
        assert "median_ae" in metrics
        assert "n_samples" in metrics


class TestRunCV:
    def test_cv_returns_valid_metrics(self, small_df):
        results = run_cv(small_df, n_folds=3)
        assert "cv_mae_mean" in results
        assert "cv_r2_mean" in results
        assert results["cv_mae_mean"] > 0
        assert results["cv_r2_mean"] > 0  # Model should explain some variance
        assert results["cv_r2_mean"] < 1.0  # But not perfect

    def test_cv_mae_reasonable(self, small_df):
        results = run_cv(small_df, n_folds=3)
        # MAE should be much less than the standard deviation of energy values
        ev_std = small_df["energy_value_kwh_m2_yr"].std()
        assert results["cv_mae_mean"] < ev_std, \
            f"MAE {results['cv_mae_mean']:.1f} >= std {ev_std:.1f} — model not learning"
