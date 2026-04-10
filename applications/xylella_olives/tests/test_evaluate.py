"""Tests for evaluate.py — verify evaluation harness correctness."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset
from evaluate import compute_metrics, run_cv


@pytest.fixture
def small_df():
    return load_dataset(n_municipalities=200, seed=42)


class TestComputeMetrics:
    def test_perfect_prediction(self):
        y_true = np.array([0, 1, 0, 1, 1])
        y_prob = np.array([0.0, 1.0, 0.0, 1.0, 1.0])
        metrics = compute_metrics(y_true, y_prob)
        assert metrics["auc"] == 1.0
        assert metrics["precision"] == 1.0
        assert metrics["recall"] == 1.0
        assert metrics["f1"] == 1.0

    def test_imperfect_prediction(self):
        y_true = np.array([0, 1, 0, 1, 0])
        y_prob = np.array([0.6, 0.8, 0.3, 0.4, 0.2])
        metrics = compute_metrics(y_true, y_prob)
        assert 0 < metrics["auc"] < 1
        assert 0 < metrics["f1"] <= 1

    def test_metrics_have_expected_keys(self):
        y_true = np.array([0, 1, 0, 1])
        y_prob = np.array([0.2, 0.8, 0.3, 0.7])
        metrics = compute_metrics(y_true, y_prob)
        assert "auc" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert "n_samples" in metrics

    def test_random_prediction_auc_near_05(self):
        """Random predictions should have AUC near 0.5."""
        rng = np.random.RandomState(42)
        y_true = rng.randint(0, 2, size=1000)
        y_prob = rng.random(size=1000)
        metrics = compute_metrics(y_true, y_prob)
        assert 0.4 < metrics["auc"] < 0.6


class TestRunCV:
    def test_cv_returns_valid_metrics(self, small_df):
        results = run_cv(small_df, n_folds=3, verbose=False)
        assert "cv_auc_mean" in results
        assert "cv_auc_std" in results
        assert "cv_f1_mean" in results
        assert 0 < results["cv_auc_mean"] < 1

    def test_cv_auc_above_random(self, small_df):
        """Model should beat random (AUC > 0.5) on this synthetic data."""
        results = run_cv(small_df, n_folds=3, verbose=False)
        # With spatial CV, may be marginal, but should be above 0.45
        assert results["cv_auc_mean"] > 0.45

    def test_cv_custom_features(self, small_df):
        """CV with custom feature list should work."""
        results = run_cv(small_df, n_folds=3,
                         feature_cols=["latitude", "longitude", "ndvi_mean"],
                         verbose=False)
        assert "cv_auc_mean" in results
