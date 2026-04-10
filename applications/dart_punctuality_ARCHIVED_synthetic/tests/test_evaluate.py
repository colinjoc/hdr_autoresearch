"""Tests for evaluate.py — verify evaluation metrics and pipeline."""

import sys
from pathlib import Path

import numpy as np
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from evaluate import compute_metrics


class TestComputeMetrics:
    def test_perfect_predictions(self):
        y_true = np.array([0, 0, 1, 1, 1])
        y_proba = np.array([0.1, 0.2, 0.8, 0.9, 0.95])
        metrics = compute_metrics(y_true, y_proba)
        assert metrics["auc"] == 1.0
        assert metrics["recall"] == 1.0
        assert metrics["precision"] == 1.0

    def test_all_zeros(self):
        y_true = np.array([0, 0, 0, 0])
        y_proba = np.array([0.1, 0.2, 0.3, 0.4])
        metrics = compute_metrics(y_true, y_proba)
        # AUC is undefined with single class — should handle gracefully
        assert "auc" in metrics

    def test_random_predictions(self):
        rng = np.random.default_rng(42)
        y_true = rng.integers(0, 2, size=1000)
        y_proba = rng.random(1000)
        metrics = compute_metrics(y_true, y_proba)
        # AUC should be near 0.5 for random
        assert 0.3 < metrics["auc"] < 0.7

    def test_all_required_metrics(self):
        y_true = np.array([0, 1, 0, 1])
        y_proba = np.array([0.2, 0.8, 0.3, 0.7])
        metrics = compute_metrics(y_true, y_proba)
        required = ["auc", "f2", "f1", "precision", "recall", "accuracy",
                     "n_positive", "n_total"]
        for key in required:
            assert key in metrics, f"Missing metric: {key}"

    def test_n_positive_correct(self):
        y_true = np.array([0, 1, 0, 1, 1])
        y_proba = np.array([0.1, 0.9, 0.2, 0.8, 0.7])
        metrics = compute_metrics(y_true, y_proba)
        assert metrics["n_positive"] == 3
        assert metrics["n_total"] == 5

    def test_f2_favours_recall(self):
        """F2 should weight recall > precision."""
        y_true = np.array([1, 1, 1, 0, 0])
        # High recall, low precision
        y_proba_recall = np.array([0.9, 0.8, 0.7, 0.6, 0.4])
        m_recall = compute_metrics(y_true, y_proba_recall)
        # Low recall, high precision
        y_proba_prec = np.array([0.9, 0.3, 0.3, 0.1, 0.1])
        m_prec = compute_metrics(y_true, y_proba_prec)
        assert m_recall["f2"] >= m_prec["f2"]
