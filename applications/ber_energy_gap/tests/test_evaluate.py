"""Tests for evaluation harness."""
import os
import sys
import tempfile
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import Ridge

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from evaluate import cross_validate, evaluate_by_band, record_result, feature_importance


class TestCrossValidate:
    def test_returns_expected_keys(self):
        """CV results contain all expected metric keys."""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = X @ np.array([1, 2, 3, 4, 5]) + np.random.randn(100) * 0.1

        result = cross_validate(Ridge, X, y, n_splits=3)

        for key in ["mae", "rmse", "r2", "mae_std", "rmse_std", "r2_std",
                     "fold_maes", "fold_rmses", "fold_r2s", "predictions", "elapsed_s"]:
            assert key in result, f"Missing key: {key}"

    def test_perfect_prediction(self):
        """Linear model on purely linear data should get R2 > 0.99."""
        np.random.seed(42)
        X = np.random.randn(200, 3)
        y = X @ np.array([1, 2, 3])

        result = cross_validate(Ridge, X, y, n_splits=5)
        assert result["r2"] > 0.99

    def test_predictions_length(self):
        """Out-of-fold predictions should cover all samples."""
        np.random.seed(42)
        X = np.random.randn(50, 2)
        y = X @ np.array([1, 2])

        result = cross_validate(Ridge, X, y, n_splits=5)
        assert len(result["predictions"]) == 50

    def test_fold_count(self):
        np.random.seed(42)
        X = np.random.randn(60, 2)
        y = X[:, 0] + X[:, 1]

        result = cross_validate(Ridge, X, y, n_splits=3)
        assert len(result["fold_maes"]) == 3


class TestEvaluateByBand:
    def test_per_band_metrics(self):
        y_true = np.array([40, 45, 160, 170, 320, 330])
        y_pred = np.array([42, 43, 162, 168, 325, 328])
        ratings = pd.Series(["A2", "A2", "C1", "C1", "E1", "E1"])

        result = evaluate_by_band(y_true, y_pred, ratings)
        assert len(result) == 3
        assert set(result["band"]) == {"A2", "C1", "E1"}
        assert all(result["mae"] < 5)


class TestRecordResult:
    def test_writes_tsv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "results.tsv")
            # Monkey-patch the path
            import evaluate
            orig = evaluate.RESULTS_PATH
            evaluate.RESULTS_PATH = path

            try:
                metrics = {
                    "mae": 25.0, "rmse": 35.0, "r2": 0.85,
                    "mae_std": 1.0, "rmse_std": 1.5, "r2_std": 0.01,
                    "elapsed_s": 10.0,
                }
                record_result("exp001", "test experiment", metrics, kept=True)

                assert os.path.exists(path)
                df = pd.read_csv(path, sep="\t")
                assert len(df) == 1
                assert df.iloc[0]["experiment_id"] == "exp001"
                assert df.iloc[0]["kept"] == "YES"
            finally:
                evaluate.RESULTS_PATH = orig


class TestFeatureImportance:
    def test_with_ridge(self):
        X = np.random.randn(50, 3)
        y = X @ np.array([10, 1, 0.1])
        model = Ridge()
        model.fit(X, y)

        result = feature_importance(model, ["a", "b", "c"])
        assert result is not None
        assert result.iloc[0]["feature"] == "a"  # largest coef
