"""Tests for model and feature engineering — Iberian wildfire VLF prediction."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import generate_synthetic_fires
from model import (
    get_feature_columns,
    get_model_config,
    build_model,
    prepare_features,
    BASE_FEATURES,
    MODEL_FAMILY,
)


class TestFeatureColumns:
    """Test feature column configuration."""

    def test_base_features_not_empty(self):
        assert len(BASE_FEATURES) > 0

    def test_get_feature_columns_returns_list(self):
        cols = get_feature_columns()
        assert isinstance(cols, list)

    def test_all_features_exist_in_data(self):
        """All features in the model must exist in the generated data."""
        df = generate_synthetic_fires(seed=42, years=(2020, 2020), n_scale=0.01)
        df = prepare_features(df)
        cols = get_feature_columns()
        missing = [c for c in cols if c not in df.columns]
        assert len(missing) == 0, f"Missing columns in data: {missing}"


class TestModelConfig:
    """Test model configuration."""

    def test_get_model_config_returns_dict(self):
        config = get_model_config()
        assert isinstance(config, dict)
        assert "family" in config
        assert "params" in config

    def test_build_model_xgboost(self):
        config = {"family": "xgboost", "params": {
            "max_depth": 3, "n_estimators": 10,
            "objective": "binary:logistic",
            "tree_method": "hist", "device": "cuda",
            "random_state": 42,
        }}
        model = build_model(config)
        assert hasattr(model, "fit")
        assert hasattr(model, "predict_proba")

    def test_build_model_lightgbm(self):
        config = {"family": "lightgbm", "params": {
            "max_depth": 3, "n_estimators": 10,
            "objective": "binary",
            "random_state": 42, "verbose": -1,
        }}
        model = build_model(config)
        assert hasattr(model, "fit")

    def test_build_model_extratrees(self):
        config = {"family": "extratrees", "params": {
            "n_estimators": 10, "random_state": 42,
        }}
        model = build_model(config)
        assert hasattr(model, "fit")

    def test_build_model_ridge(self):
        config = {"family": "ridge", "params": {
            "alpha": 1.0, "random_state": 42,
        }}
        model = build_model(config)
        assert hasattr(model, "fit")


class TestPrepareFeatures:
    """Test feature preparation pipeline."""

    def test_prepare_features_returns_dataframe(self):
        df = generate_synthetic_fires(seed=42, years=(2020, 2020), n_scale=0.01)
        result = prepare_features(df)
        assert isinstance(result, pd.DataFrame)

    def test_prepare_features_preserves_rows(self):
        df = generate_synthetic_fires(seed=42, years=(2020, 2020), n_scale=0.01)
        result = prepare_features(df)
        assert len(result) == len(df)


class TestEndToEnd:
    """End-to-end test: load data, prepare features, train, predict."""

    def test_model_trains_and_predicts(self):
        """Current model family can train on synthetic data and produce predictions."""
        from sklearn.preprocessing import RobustScaler, MinMaxScaler

        df = generate_synthetic_fires(seed=42, years=(2020, 2022), n_scale=0.01)
        df = prepare_features(df)
        cols = get_feature_columns()

        X = df[cols].fillna(0).values.astype(np.float32)
        y = df["is_vlf"].values

        # Split 80/20
        n_train = int(0.8 * len(df))
        X_train, X_test = X[:n_train], X[n_train:]
        y_train, y_test = y[:n_train], y[n_train:]

        config = get_model_config()
        model = build_model(config)

        # Ridge needs scaling
        if config["family"] == "ridge":
            scaler = RobustScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

        model.fit(X_train, y_train)

        if config["family"] == "ridge":
            # RidgeClassifier uses decision_function
            decision = model.decision_function(X_test)
            assert decision.shape[0] == len(X_test)
        else:
            proba = model.predict_proba(X_test)
            assert proba.shape[0] == len(X_test)
            assert proba.shape[1] == 2
            assert (proba >= 0).all()
            assert (proba <= 1).all()

    def test_predictions_are_nontrivial(self):
        """Model should not predict all zeros or all ones."""
        from sklearn.preprocessing import RobustScaler, MinMaxScaler

        df = generate_synthetic_fires(seed=42, years=(2015, 2024), n_scale=0.02)
        df = prepare_features(df)
        cols = get_feature_columns()

        X = df[cols].fillna(0).values.astype(np.float32)
        y = df["is_vlf"].values

        n_train = int(0.8 * len(df))
        X_train, X_test = X[:n_train], X[n_train:]
        y_train, y_test = y[:n_train], y[n_train:]

        config = get_model_config()
        model = build_model(config)

        if config["family"] == "ridge":
            scaler = RobustScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

        model.fit(X_train, y_train)

        if config["family"] == "ridge":
            decision = model.decision_function(X_test)
            assert decision.std() > 0.01, f"Decision std too low: {decision.std()}"
        else:
            proba = model.predict_proba(X_test)[:, 1]
            assert proba.std() > 0.01, f"Prediction std too low: {proba.std()}"
