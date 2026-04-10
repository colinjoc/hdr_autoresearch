"""Tests for model.py — verify feature engineering and model building."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from model import (
    get_feature_columns, get_model_config, build_model, prepare_features,
    BASE_FEATURES, EXTRA_FEATURES, MODEL_FAMILY,
)
from data_loaders import generate_synthetic_dataset


class TestFeatureColumns:
    def test_base_features_nonempty(self):
        assert len(BASE_FEATURES) > 5

    def test_all_features_returned(self):
        cols = get_feature_columns()
        for f in BASE_FEATURES:
            assert f in cols
        for f in EXTRA_FEATURES:
            assert f in cols

    def test_prev_leg_arr_delay_in_base(self):
        """The key propagation feature must be in base features."""
        assert "prev_leg_arr_delay" in BASE_FEATURES


class TestModelConfig:
    def test_config_has_family(self):
        config = get_model_config()
        assert "family" in config
        assert "params" in config

    def test_default_family(self):
        assert MODEL_FAMILY in ("xgboost", "lightgbm", "extratrees", "ridge")


class TestBuildModel:
    def test_xgboost(self):
        config = {"family": "xgboost", "params": {
            "n_estimators": 10, "max_depth": 3, "random_state": 42,
        }}
        model = build_model(config)
        assert model is not None

    def test_lightgbm(self):
        config = {"family": "lightgbm", "params": {
            "n_estimators": 10, "max_depth": 3, "random_state": 42, "verbose": -1,
        }}
        model = build_model(config)
        assert model is not None

    def test_ridge(self):
        config = {"family": "ridge", "params": {"alpha": 1.0}}
        model = build_model(config)
        assert model is not None

    def test_extratrees(self):
        config = {"family": "extratrees", "params": {
            "n_estimators": 10, "random_state": 42,
        }}
        model = build_model(config)
        assert model is not None

    def test_unknown_family_raises(self):
        with pytest.raises(ValueError):
            build_model({"family": "unknown", "params": {}})


class TestPrepareFeatures:
    @pytest.fixture(scope="class")
    def dataset(self):
        df = generate_synthetic_dataset(n_target_flights=5_000, seed=42)
        return df[df["arr_delay"].notna()].copy()

    def test_all_feature_columns_present(self, dataset):
        df = prepare_features(dataset)
        feature_cols = get_feature_columns()
        for col in feature_cols:
            assert col in df.columns, f"Missing feature column: {col}"

    def test_no_nans_in_features(self, dataset):
        df = prepare_features(dataset)
        feature_cols = get_feature_columns()
        for col in feature_cols:
            nan_count = df[col].isna().sum()
            assert nan_count == 0, f"NaN in feature {col}: {nan_count}"

    def test_prev_leg_delay_x_buffer(self, dataset):
        """Interaction feature should be product of prev delay and buffer."""
        df = prepare_features(dataset)
        if "prev_leg_delay_x_buffer" in df.columns:
            expected = df["prev_leg_arr_delay"] * df["carrier_buffer_factor"]
            np.testing.assert_allclose(
                df["prev_leg_delay_x_buffer"].values,
                expected.values,
                rtol=1e-5,
            )

    def test_hub_to_hub(self, dataset):
        """Hub-to-hub should be 1 only when both origin and dest are hubs."""
        df = prepare_features(dataset)
        if "is_hub_to_hub" in df.columns:
            expected = (df["origin_is_hub"] & df["dest_is_hub"]).astype(int)
            np.testing.assert_array_equal(
                df["is_hub_to_hub"].values,
                expected.values,
            )

    def test_model_can_fit_on_prepared_data(self, dataset):
        """Smoke test: model should be able to fit on prepared features."""
        df = prepare_features(dataset)
        feature_cols = get_feature_columns()
        X = df[feature_cols].values[:500].astype(np.float32)
        y = df["arr_delay"].values[:500].astype(np.float32)

        config = {"family": "ridge", "params": {"alpha": 1.0}}
        model = build_model(config)
        model.fit(X, y)
        preds = model.predict(X)
        assert len(preds) == 500
        assert not np.isnan(preds).any()
