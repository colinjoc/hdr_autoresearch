"""Tests for model.py — verify feature engineering and model construction."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from model import (
    get_feature_columns, get_model_config, build_model, prepare_features,
    BASE_FEATURES, EXTRA_FEATURES,
)
from data_loaders import generate_synthetic_dataset


class TestFeatureColumns:
    def test_base_features_present(self):
        cols = get_feature_columns()
        for feat in BASE_FEATURES:
            assert feat in cols

    def test_extra_features_present(self):
        cols = get_feature_columns()
        for feat in EXTRA_FEATURES:
            assert feat in cols

    def test_no_duplicates(self):
        cols = get_feature_columns()
        assert len(cols) == len(set(cols))


class TestModelConfig:
    def test_returns_dict(self):
        config = get_model_config()
        assert isinstance(config, dict)
        assert "family" in config
        assert "params" in config

    def test_valid_family(self):
        config = get_model_config()
        assert config["family"] in ["xgboost", "lightgbm", "extratrees", "ridge"]


class TestBuildModel:
    def test_xgboost(self):
        model = build_model({"family": "xgboost", "params": {
            "n_estimators": 10, "max_depth": 3, "random_state": 42,
            "tree_method": "hist", "device": "cuda",
        }})
        assert model is not None

    def test_extratrees(self):
        model = build_model({"family": "extratrees", "params": {
            "n_estimators": 10, "random_state": 42,
        }})
        assert model is not None

    def test_ridge(self):
        model = build_model({"family": "ridge", "params": {
            "alpha": 1.0,
        }})
        assert model is not None

    def test_unknown_family_raises(self):
        with pytest.raises(ValueError):
            build_model({"family": "unknown_model", "params": {}})


class TestPrepareFeatures:
    @pytest.fixture
    def dataset(self):
        return generate_synthetic_dataset(seed=42)

    def test_output_has_all_features(self, dataset):
        df = prepare_features(dataset)
        for col in get_feature_columns():
            assert col in df.columns, f"Missing feature after prepare: {col}"

    def test_no_nans_in_features(self, dataset):
        df = prepare_features(dataset)
        feature_cols = get_feature_columns()
        nans = df[feature_cols].isna().sum()
        bad = nans[nans > 0]
        assert len(bad) == 0, f"NaN in features: {dict(bad)}"

    def test_wind_above_50_binary(self, dataset):
        df = prepare_features(dataset)
        if "wind_above_50" in df.columns:
            assert set(df["wind_above_50"].unique()).issubset({0, 1})

    def test_rain_above_10_binary(self, dataset):
        df = prepare_features(dataset)
        if "rain_above_10" in df.columns:
            assert set(df["rain_above_10"].unique()).issubset({0, 1})

    def test_rolling_7d_bad_rate_bounded(self, dataset):
        df = prepare_features(dataset)
        if "rolling_7d_bad_rate" in df.columns:
            assert df["rolling_7d_bad_rate"].min() >= 0
            assert df["rolling_7d_bad_rate"].max() <= 1.0

    def test_model_can_fit_on_prepared(self, dataset):
        """Smoke test: model can fit on prepared features."""
        df = prepare_features(dataset)
        feature_cols = get_feature_columns()
        X = df[feature_cols].values[:100].astype(np.float32)
        y = df["bad_day"].values[:100]
        model = build_model({
            "family": "xgboost",
            "params": {
                "n_estimators": 5, "max_depth": 2, "random_state": 42,
                "tree_method": "hist", "device": "cuda",
            },
        })
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape[0] == 100
