"""Tests for model.py — verify feature extraction and model building."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import _generate_synthetic_data, add_derived_features
from model import (
    get_feature_columns, build_model, prepare_features,
    BASE_FEATURES, EXTRA_FEATURES, MODEL_FAMILY,
)


@pytest.fixture
def small_df():
    """Generate a small synthetic dataset for testing."""
    df = _generate_synthetic_data(
        start="2024-01-01", end="2024-02-01", seed=42
    )
    df = add_derived_features(df)
    return df.dropna()


class TestFeatureColumns:
    def test_base_features_not_empty(self):
        assert len(BASE_FEATURES) > 0

    def test_get_feature_columns_returns_list(self):
        cols = get_feature_columns()
        assert isinstance(cols, list)
        assert all(isinstance(c, str) for c in cols)

    def test_base_features_in_output(self):
        cols = get_feature_columns()
        for f in BASE_FEATURES:
            assert f in cols


class TestPrepareFeatures:
    def test_returns_arrays(self, small_df):
        X, y = prepare_features(small_df)
        assert isinstance(X, np.ndarray)
        assert isinstance(y, np.ndarray)

    def test_correct_shape(self, small_df):
        X, y = prepare_features(small_df)
        assert X.shape[0] == len(small_df)
        assert X.shape[1] == len(get_feature_columns())
        assert y.shape[0] == len(small_df)

    def test_no_nans_in_features(self, small_df):
        X, y = prepare_features(small_df)
        assert not np.isnan(X).any(), "Features contain NaN"

    def test_labels_are_binary(self, small_df):
        X, y = prepare_features(small_df)
        assert set(np.unique(y)).issubset({0, 1})

    def test_missing_column_raises(self, small_df):
        # Drop a required column
        df_bad = small_df.drop(columns=["gen_nuclear_mw"])
        with pytest.raises(ValueError, match="Missing feature columns"):
            prepare_features(df_bad)


class TestBuildModel:
    def test_xgboost_model(self):
        model = build_model("xgboost")
        assert hasattr(model, "fit")
        assert hasattr(model, "predict_proba")

    def test_lightgbm_model(self):
        model = build_model("lightgbm")
        assert hasattr(model, "fit")
        assert hasattr(model, "predict_proba")

    def test_extratrees_model(self):
        model = build_model("extratrees")
        assert hasattr(model, "fit")
        assert hasattr(model, "predict_proba")

    def test_ridge_model(self):
        model = build_model("ridge")
        assert hasattr(model, "fit")
        assert hasattr(model, "decision_function")

    def test_unknown_family_raises(self):
        with pytest.raises(ValueError, match="Unknown model family"):
            build_model("neural_net")


class TestModelTraining:
    def test_xgboost_fits_and_predicts(self, small_df):
        X, y = prepare_features(small_df)
        model = build_model("xgboost")
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (len(X), 2)
        assert (proba >= 0).all() and (proba <= 1).all()

    def test_extratrees_fits_and_predicts(self, small_df):
        X, y = prepare_features(small_df)
        model = build_model("extratrees")
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (len(X), 2)

    def test_ridge_fits_and_scores(self, small_df):
        X, y = prepare_features(small_df)
        model = build_model("ridge")
        model.fit(X, y)
        scores = model.decision_function(X)
        assert scores.shape == (len(X),)
