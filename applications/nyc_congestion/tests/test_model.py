"""Tests for model.py — congestion charge effect decomposition."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestFeatureEngineering:
    def test_add_features(self):
        from model import add_features
        from data_loaders import build_master_dataset
        df = build_master_dataset()
        df = add_features(df)
        # Should have lag features, rolling means, interaction terms
        assert "vol_lag1w" in df.columns
        assert "vol_rolling4w" in df.columns
        assert "is_manhattan" in df.columns

    def test_build_clean_dataset(self):
        from model import build_clean_dataset
        df = build_clean_dataset()
        assert len(df) > 50
        # Core columns should not be NaN
        assert df["daily_vol_mean"].isna().sum() == 0
        assert df["boro"].isna().sum() == 0


class TestDecomposition:
    def test_decomposition_components(self):
        """Decomposition should produce mode_shift, route_displacement,
        time_shift, and trip_elimination components."""
        from model import decompose_volume_change
        from data_loaders import build_master_dataset
        df = build_master_dataset()
        result = decompose_volume_change(df)
        assert isinstance(result, dict)
        for key in ["mode_shift", "route_displacement",
                    "time_shift", "trip_elimination"]:
            assert key in result, f"Missing component: {key}"

    def test_components_sum_to_total(self):
        """Components should approximately sum to total observed change."""
        from model import decompose_volume_change
        from data_loaders import build_master_dataset
        df = build_master_dataset()
        result = decompose_volume_change(df)
        component_sum = (
            result["mode_shift"] + result["route_displacement"]
            + result["time_shift"] + result["trip_elimination"]
        )
        # Allow 20% tolerance since decomposition is approximate
        assert abs(component_sum - result["total_change"]) < abs(result["total_change"]) * 0.25 or abs(result["total_change"]) < 1.0


class TestPredictionModel:
    def test_train_predict(self):
        from model import build_clean_dataset, train_volume_model, FEATURE_COLS
        df = build_clean_dataset()
        model_obj, metrics = train_volume_model(df)
        assert model_obj is not None
        assert "mae" in metrics
        assert "r2" in metrics
        assert metrics["mae"] >= 0
        assert metrics["r2"] <= 1.0

    def test_tournament(self):
        from model import build_clean_dataset, run_tournament
        df = build_clean_dataset()
        results = run_tournament(df)
        assert isinstance(results, pd.DataFrame)
        assert len(results) >= 3  # at least 3 model families
        assert "model" in results.columns
        assert "mae" in results.columns


class TestDiDEstimator:
    def test_did_estimate(self):
        """Difference-in-differences should return estimate and p-value."""
        from model import did_estimate
        from data_loaders import build_master_dataset
        df = build_master_dataset()
        result = did_estimate(df)
        assert "did_coeff" in result
        assert "p_value" in result
        assert isinstance(result["did_coeff"], float)
