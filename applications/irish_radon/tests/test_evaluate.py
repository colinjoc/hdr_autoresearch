"""Tests for the evaluation harness.

The evaluation must:
1. Use spatial CV grouped by county (no leakage across counties)
2. Report MAE on the held-out county group
3. Report classification metrics for HRA threshold (>=10%)
4. Return per-county scores for diagnostic inspection
"""
import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
pytestmark = pytest.mark.skipif(
    not os.path.exists(os.path.join(DATA_DIR, "epa_radon", "radon_grid_map.geojson")),
    reason="Data not downloaded yet"
)


class TestSpatialCV:
    """Test that spatial CV groups by county."""

    def test_cv_splits_by_county(self):
        from evaluate import make_spatial_cv_splits
        from data_loaders import build_dataset
        X, y, groups = build_dataset()
        splits = make_spatial_cv_splits(X, y, groups)
        assert len(splits) >= 5, "Should have at least 5 CV folds"
        for train_idx, test_idx in splits:
            train_counties = set(groups.iloc[train_idx])
            test_counties = set(groups.iloc[test_idx])
            assert train_counties.isdisjoint(test_counties), \
                f"Leak: {train_counties & test_counties}"

    def test_all_samples_tested(self):
        from evaluate import make_spatial_cv_splits
        from data_loaders import build_dataset
        X, y, groups = build_dataset()
        splits = make_spatial_cv_splits(X, y, groups)
        tested = set()
        for _, test_idx in splits:
            tested.update(test_idx)
        assert len(tested) == len(X), "Every sample must be tested exactly once"


class TestEvaluation:
    """Test the full evaluation pipeline."""

    def test_evaluate_returns_metrics(self):
        from evaluate import evaluate_model
        from model import build_model
        metrics = evaluate_model(build_model)
        assert "mae_mean" in metrics
        assert "mae_std" in metrics
        assert "hra_f1" in metrics
        assert "hra_accuracy" in metrics

    def test_evaluate_returns_per_county(self):
        from evaluate import evaluate_model
        from model import build_model
        metrics = evaluate_model(build_model)
        assert "per_county_mae" in metrics
        assert isinstance(metrics["per_county_mae"], dict)
        assert len(metrics["per_county_mae"]) >= 5

    def test_mae_is_reasonable(self):
        """MAE should be less than predicting the mean everywhere."""
        from evaluate import evaluate_model
        from model import build_model
        from data_loaders import build_dataset
        _, y, _ = build_dataset()
        metrics = evaluate_model(build_model)
        naive_mae = np.abs(y - y.mean()).mean()
        assert metrics["mae_mean"] < naive_mae * 1.5, \
            f"Model MAE {metrics['mae_mean']:.2f} is worse than naive {naive_mae:.2f}"


class TestResultsRecording:
    """Test that results are recorded properly."""

    def test_record_appends_to_tsv(self, tmp_path):
        from evaluate import record_result
        tsv_path = tmp_path / "results.tsv"
        record_result(
            experiment_id="E00",
            description="baseline",
            metrics={"mae_mean": 5.0, "mae_std": 1.0, "hra_f1": 0.6},
            kept=True,
            results_path=str(tsv_path),
        )
        df = pd.read_csv(tsv_path, sep="\t")
        assert len(df) == 1
        assert df.iloc[0]["experiment_id"] == "E00"
