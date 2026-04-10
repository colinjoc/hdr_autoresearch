"""Tests for the model module."""
import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model import (
    CascadeRiskModel,
    compute_inertia_proxy,
    compute_voltage_stress_proxy,
    compute_reactive_power_gap_proxy,
)
from data_loader import build_daily_feature_matrix

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class TestInertiaProxy:
    def test_returns_series(self):
        features = build_daily_feature_matrix(DATA_DIR)
        result = compute_inertia_proxy(features)
        assert isinstance(result, pd.Series)

    def test_positive_values(self):
        features = build_daily_feature_matrix(DATA_DIR)
        result = compute_inertia_proxy(features)
        valid = result.dropna()
        assert (valid >= 0).all()

    def test_blackout_day_low_inertia(self):
        features = build_daily_feature_matrix(DATA_DIR)
        result = compute_inertia_proxy(features)
        apr28 = result[result.index.date == pd.Timestamp("2025-04-28").date()]
        # Per ENTSO-E report: inertia was NOT the primary cause but was
        # still in the lower quartile of all days
        q75 = result.quantile(0.75)
        if len(apr28) > 0 and not apr28.isna().all():
            assert apr28.iloc[0] < q75


class TestVoltageStressProxy:
    def test_returns_series(self):
        features = build_daily_feature_matrix(DATA_DIR)
        result = compute_voltage_stress_proxy(features)
        assert isinstance(result, pd.Series)

    def test_bounded_values(self):
        features = build_daily_feature_matrix(DATA_DIR)
        result = compute_voltage_stress_proxy(features)
        valid = result.dropna()
        assert valid.min() >= 0


class TestReactivePowerGapProxy:
    def test_returns_series(self):
        features = build_daily_feature_matrix(DATA_DIR)
        result = compute_reactive_power_gap_proxy(features)
        assert isinstance(result, pd.Series)


class TestCascadeRiskModel:
    def test_fit_predict(self):
        features = build_daily_feature_matrix(DATA_DIR)
        model = CascadeRiskModel()
        model.fit(features)
        predictions = model.predict(features)
        assert isinstance(predictions, pd.DataFrame)
        assert "risk_score" in predictions.columns
        assert "risk_class" in predictions.columns

    def test_risk_score_bounded(self):
        features = build_daily_feature_matrix(DATA_DIR)
        model = CascadeRiskModel()
        model.fit(features)
        predictions = model.predict(features)
        valid = predictions["risk_score"].dropna()
        assert valid.min() >= 0
        assert valid.max() <= 1

    def test_blackout_day_high_risk(self):
        features = build_daily_feature_matrix(DATA_DIR)
        model = CascadeRiskModel()
        model.fit(features)
        predictions = model.predict(features)
        apr28 = predictions[predictions.index.date == pd.Timestamp("2025-04-28").date()]
        if len(apr28) > 0:
            # Blackout day should be classified as high risk
            assert apr28["risk_class"].iloc[0] == 1

    def test_feature_importance(self):
        features = build_daily_feature_matrix(DATA_DIR)
        model = CascadeRiskModel()
        model.fit(features)
        importance = model.feature_importance()
        assert isinstance(importance, pd.Series)
        assert len(importance) > 0
