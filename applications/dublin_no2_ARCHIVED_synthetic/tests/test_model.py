"""
Tests for Dublin NO2 model and feature engineering.

Verifies that model.py produces correct features, builds models,
and generates predictions in the expected range.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import generate_synthetic_dataset
from model import (
    get_feature_columns,
    get_model_config,
    build_model,
    prepare_features,
    MODEL_FAMILY,
    BASE_FEATURES,
    EXTRA_FEATURES,
)


@pytest.fixture(scope="module")
def dataset():
    return generate_synthetic_dataset(seed=42)


@pytest.fixture(scope="module")
def prepared_dataset(dataset):
    return prepare_features(dataset)


class TestFeatureColumns:
    """Test feature column configuration."""

    def test_base_features_not_empty(self):
        assert len(BASE_FEATURES) > 0

    def test_all_features_are_strings(self):
        for f in get_feature_columns():
            assert isinstance(f, str)

    def test_no_duplicate_features(self):
        cols = get_feature_columns()
        assert len(cols) == len(set(cols))

    def test_no_target_in_features(self):
        cols = get_feature_columns()
        assert "no2_ugm3" not in cols


class TestPrepareFeatures:
    """Test feature engineering pipeline."""

    def test_returns_dataframe(self, prepared_dataset):
        assert isinstance(prepared_dataset, pd.DataFrame)

    def test_all_feature_columns_present(self, prepared_dataset):
        for col in get_feature_columns():
            assert col in prepared_dataset.columns, f"Missing: {col}"

    def test_no_inf_values(self, prepared_dataset):
        feature_cols = get_feature_columns()
        X = prepared_dataset[feature_cols]
        assert not np.isinf(X.values).any()

    def test_limited_nan_values(self, prepared_dataset):
        feature_cols = get_feature_columns()
        X = prepared_dataset[feature_cols]
        nan_frac = np.isnan(X.values).mean()
        assert nan_frac < 0.05, f"Too many NaNs: {nan_frac:.1%}"


class TestModelConfig:
    """Test model configuration."""

    def test_config_has_family(self):
        config = get_model_config()
        assert "family" in config

    def test_config_has_params(self):
        config = get_model_config()
        assert "params" in config

    def test_default_family_is_xgboost(self):
        assert MODEL_FAMILY == "xgboost"


class TestBuildModel:
    """Test model construction and basic fit/predict."""

    def test_build_xgboost(self):
        config = {"family": "xgboost", "params": {
            "max_depth": 3, "n_estimators": 10, "random_state": 42,
            "tree_method": "hist",
        }}
        model = build_model(config)
        assert model is not None

    def test_build_ridge(self):
        config = {"family": "ridge", "params": {"alpha": 1.0}}
        model = build_model(config)
        assert model is not None

    def test_model_can_fit_and_predict(self, prepared_dataset):
        """Smoke test: fit on 500 rows, predict on 100."""
        feature_cols = get_feature_columns()
        df = prepared_dataset.dropna(subset=feature_cols + ["no2_ugm3"]).head(600)
        X = df[feature_cols].values.astype(np.float32)
        y = df["no2_ugm3"].values

        config = {"family": "xgboost", "params": {
            "max_depth": 3, "n_estimators": 10, "random_state": 42,
            "tree_method": "hist",
        }}
        model = build_model(config)
        model.fit(X[:500], y[:500])

        preds = model.predict(X[500:600])
        assert len(preds) == 100
        assert np.isfinite(preds).all()
        # Predictions should be in a reasonable NO2 range
        assert preds.min() > -10  # slight negatives ok from regression
        assert preds.max() < 300


class TestExceedanceBinary:
    """Test the exceedance binary target derivation."""

    def test_exceedance_column_exists(self, prepared_dataset):
        assert "exceeds_who_24h" in prepared_dataset.columns

    def test_exceedance_is_binary(self, prepared_dataset):
        vals = prepared_dataset["exceeds_who_24h"].dropna().unique()
        assert set(vals).issubset({0, 1, 0.0, 1.0})
