"""Tests for the evaluation harness."""
import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evaluate import (
    label_blackout_risk,
    evaluate_model,
    run_full_evaluation,
)
from data_loader import build_daily_feature_matrix, compute_grid_stress_indicators

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class TestLabelBlackoutRisk:
    def test_returns_series(self):
        features = build_daily_feature_matrix(DATA_DIR)
        labels = label_blackout_risk(features)
        assert isinstance(labels, pd.Series)

    def test_binary_labels(self):
        features = build_daily_feature_matrix(DATA_DIR)
        labels = label_blackout_risk(features)
        assert set(labels.dropna().unique()).issubset({0, 1})

    def test_apr28_is_positive(self):
        features = build_daily_feature_matrix(DATA_DIR)
        labels = label_blackout_risk(features)
        # April 28, 2025 must be labeled as high-risk
        apr28_labels = labels[labels.index.date == pd.Timestamp("2025-04-28").date()]
        assert len(apr28_labels) > 0
        assert apr28_labels.iloc[0] == 1

    def test_most_days_are_negative(self):
        features = build_daily_feature_matrix(DATA_DIR)
        labels = label_blackout_risk(features)
        # Only a few days should be high-risk
        assert labels.sum() < len(labels) * 0.2


class TestEvaluateModel:
    def test_returns_metrics_dict(self):
        features = build_daily_feature_matrix(DATA_DIR)
        stress = compute_grid_stress_indicators(features)
        labels = label_blackout_risk(features)
        metrics = evaluate_model(stress, labels)
        assert isinstance(metrics, dict)
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert "auc_roc" in metrics

    def test_metrics_bounded(self):
        features = build_daily_feature_matrix(DATA_DIR)
        stress = compute_grid_stress_indicators(features)
        labels = label_blackout_risk(features)
        metrics = evaluate_model(stress, labels)
        for k, v in metrics.items():
            if v is not None:
                assert 0 <= v <= 1, f"{k}={v} out of bounds"


class TestRunFullEvaluation:
    def test_returns_results(self):
        results = run_full_evaluation(DATA_DIR)
        assert isinstance(results, dict)
        assert "metrics" in results
        assert "predictions" in results
        assert "features_used" in results
