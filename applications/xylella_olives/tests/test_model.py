"""Tests for model.py — verify feature preparation and model building."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset
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
    return load_dataset(n_municipalities=200, seed=42)


class TestFeatureColumns:
    def test_base_features_present(self):
        cols = get_feature_columns()
        for f in BASE_FEATURES:
            assert f in cols

    def test_returns_list(self):
        cols = get_feature_columns()
        assert isinstance(cols, list)
        assert len(cols) >= len(BASE_FEATURES)


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


class TestModelConfig:
    def test_returns_dict(self):
        config = get_model_config()
        assert isinstance(config, dict)

    def test_model_family_valid(self):
        assert MODEL_FAMILY in ("xgboost", "lightgbm", "extratrees", "ridge")


class TestBuildModel:
    def test_xgboost(self):
        model = build_model(family="xgboost")
        assert hasattr(model, "fit")
        assert hasattr(model, "predict_proba")

    def test_lightgbm(self):
        model = build_model(family="lightgbm")
        assert hasattr(model, "fit")
        assert hasattr(model, "predict_proba")

    def test_extratrees(self):
        model = build_model(family="extratrees")
        assert hasattr(model, "fit")
        assert hasattr(model, "predict_proba")

    def test_ridge(self):
        model = build_model(family="ridge")
        assert hasattr(model, "fit")
        assert hasattr(model, "predict_proba")

    def test_invalid_family_raises(self):
        with pytest.raises(ValueError):
            build_model(family="nonexistent")

    def test_xgboost_can_fit(self, small_df):
        X, y = prepare_features(small_df)
        model = build_model(family="xgboost")
        model.fit(X, y)
        probs = model.predict_proba(X)
        assert probs.shape == (len(X), 2)
        assert (probs >= 0).all() and (probs <= 1).all()
