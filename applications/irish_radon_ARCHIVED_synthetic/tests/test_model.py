"""Tests for model.py — verify feature preparation and model building for radon classification."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import generate_synthetic_radon_data, add_derived_features
from model import (
    get_feature_columns,
    get_model_config,
    build_model,
    prepare_features,
    BASE_FEATURES,
    CATEGORICAL_FEATURES,
    MODEL_FAMILY,
)


@pytest.fixture
def small_df():
    df = generate_synthetic_radon_data(n_areas=300, seed=42)
    return add_derived_features(df)


class TestFeatureColumns:
    def test_base_features_present(self):
        cols = get_feature_columns()
        for f in BASE_FEATURES:
            assert f in cols

    def test_categorical_features_present(self):
        cols = get_feature_columns()
        for f in CATEGORICAL_FEATURES:
            assert f in cols


class TestPrepareFeatures:
    def test_returns_correct_shapes(self, small_df):
        X, y = prepare_features(small_df)
        assert X.shape[0] == len(small_df)
        assert X.shape[1] == len(get_feature_columns())
        assert y.shape[0] == len(small_df)

    def test_X_is_float32(self, small_df):
        X, y = prepare_features(small_df)
        assert X.dtype == np.float32

    def test_y_is_binary(self, small_df):
        X, y = prepare_features(small_df)
        assert set(np.unique(y)).issubset({0, 1})

    def test_no_nan_in_X(self, small_df):
        X, y = prepare_features(small_df)
        assert not np.isnan(X).any(), "Feature matrix contains NaN"

    def test_no_nan_in_y(self, small_df):
        X, y = prepare_features(small_df)
        assert not np.isnan(y).any(), "Target vector contains NaN"


class TestBuildModel:
    def test_xgboost_builds(self):
        model = build_model("xgboost")
        assert model is not None

    def test_lightgbm_builds(self):
        model = build_model("lightgbm")
        assert model is not None

    def test_extratrees_builds(self):
        model = build_model("extratrees")
        assert model is not None

    def test_ridge_builds(self):
        model = build_model("ridge")
        assert model is not None

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            build_model("unknown_model")

    def test_xgboost_can_fit(self, small_df):
        X, y = prepare_features(small_df)
        model = build_model("xgboost")
        model.fit(X, y)
        probs = model.predict_proba(X[:10])
        assert probs.shape == (10, 2)
        assert all(np.isfinite(probs.ravel()))

    def test_ridge_can_fit(self, small_df):
        X, y = prepare_features(small_df)
        from sklearn.preprocessing import RobustScaler
        scaler = RobustScaler()
        X_s = scaler.fit_transform(X)
        model = build_model("ridge")
        model.fit(X_s, y)
        probs = model.predict_proba(X_s[:10])
        assert probs.shape == (10, 2)
        assert all(np.isfinite(probs.ravel()))

    def test_extratrees_can_fit(self, small_df):
        X, y = prepare_features(small_df)
        model = build_model("extratrees")
        model.fit(X, y)
        probs = model.predict_proba(X[:10])
        assert probs.shape == (10, 2)
        assert all(np.isfinite(probs.ravel()))


class TestModelConfig:
    def test_config_has_required_keys(self):
        config = get_model_config()
        assert "family" in config
        assert "features" in config
        assert config["family"] == MODEL_FAMILY
