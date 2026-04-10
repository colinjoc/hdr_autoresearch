"""Tests for data_loaders.py — verify synthetic data generation and feature engineering."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    _generate_synthetic_data,
    add_derived_features,
    get_cv_folds,
    get_train_test_split,
    _interpolate_capacity,
    H_CONSTANTS,
)


@pytest.fixture
def small_df():
    """Generate a small synthetic dataset for testing."""
    df = _generate_synthetic_data(
        start="2024-01-01", end="2024-01-15", seed=42
    )
    return add_derived_features(df)


@pytest.fixture
def full_df():
    """Generate the full synthetic dataset (through end of April 28)."""
    df = _generate_synthetic_data(
        start="2023-01-01", end="2025-04-29", seed=42
    )
    return add_derived_features(df)


class TestSyntheticDataGeneration:
    def test_returns_dataframe(self, small_df):
        assert isinstance(small_df, pd.DataFrame)
        assert len(small_df) > 0

    def test_has_required_columns(self, small_df):
        required = [
            "gen_nuclear_mw", "gen_coal_mw", "gen_gas_ccgt_mw",
            "gen_gas_ocgt_mw", "gen_hydro_mw", "gen_wind_mw",
            "gen_solar_mw", "gen_other_re_mw", "gen_total_mw",
            "load_total_mw", "flow_es_fr_mw", "flow_es_pt_mw",
            "price_day_ahead_eur", "freq_excursion", "freq_dev_mhz",
        ]
        for col in required:
            assert col in small_df.columns, f"Missing column: {col}"

    def test_generation_values_non_negative(self, small_df):
        # Only check actual generation output columns, not derived imbalance/diversity
        gen_cols = [
            "gen_nuclear_mw", "gen_coal_mw", "gen_gas_ccgt_mw",
            "gen_gas_ocgt_mw", "gen_hydro_mw", "gen_wind_mw",
            "gen_solar_mw", "gen_other_re_mw", "gen_total_mw",
        ]
        for col in gen_cols:
            assert (small_df[col] >= 0).all(), f"{col} has negative values"

    def test_load_realistic_range(self, small_df):
        # Spanish demand should be 15-50 GW
        assert small_df["load_total_mw"].min() > 10000
        assert small_df["load_total_mw"].max() < 60000

    def test_flow_within_ntc(self, small_df):
        # Spain-France NTC ~ 2800 MW
        assert small_df["flow_es_fr_mw"].abs().max() <= 3000

    def test_freq_excursion_is_binary(self, small_df):
        assert set(small_df["freq_excursion"].unique()).issubset({0, 1})

    def test_excursion_rate_realistic(self, full_df):
        rate = full_df["freq_excursion"].mean()
        assert 0.005 < rate < 0.10, f"Excursion rate {rate:.4f} outside expected range"

    def test_solar_zero_at_night(self, small_df):
        idx = pd.to_datetime(small_df.index)
        night = small_df[(idx.hour < 6) | (idx.hour > 21)]
        if len(night) > 0:
            assert night["gen_solar_mw"].max() < 100, "Solar should be ~0 at night"

    def test_blackout_day_has_excursions(self, full_df):
        blackout = full_df[full_df.index.date == pd.Timestamp("2025-04-28").date()]
        if len(blackout) > 0:
            assert blackout["freq_excursion"].sum() > 0, \
                "Blackout day should have frequency excursions"

    def test_deterministic_with_seed(self):
        df1 = _generate_synthetic_data("2024-01-01", "2024-01-05", seed=42)
        df2 = _generate_synthetic_data("2024-01-01", "2024-01-05", seed=42)
        pd.testing.assert_frame_equal(df1, df2)


class TestDerivedFeatures:
    def test_snsp_range(self, small_df):
        assert (small_df["snsp"] >= 0).all()
        assert (small_df["snsp"] <= 1.0).all()

    def test_re_fraction_range(self, small_df):
        assert (small_df["re_fraction"] >= 0).all()
        assert (small_df["re_fraction"] <= 1.0).all()

    def test_inertia_proxy_positive(self, small_df):
        assert (small_df["inertia_proxy_mws"] > 0).all()

    def test_diversity_non_negative(self, small_df):
        assert (small_df["gen_diversity_shannon"] >= 0).all()

    def test_temporal_features_exist(self, small_df):
        for col in ["hour_sin", "hour_cos", "month_sin", "month_cos",
                     "is_weekend", "year"]:
            assert col in small_df.columns, f"Missing temporal feature: {col}"

    def test_lag_features_exist(self, small_df):
        for col in ["snsp_lag_1h", "snsp_lag_6h", "snsp_lag_24h",
                     "snsp_delta_1h", "inertia_delta_1h"]:
            assert col in small_df.columns, f"Missing lag feature: {col}"

    def test_ramp_features_exist(self, small_df):
        for col in ["wind_ramp_1h_mw", "solar_ramp_1h_mw", "total_ramp_1h_mw"]:
            assert col in small_df.columns, f"Missing ramp feature: {col}"


class TestCapacityInterpolation:
    def test_known_year(self):
        cap = _interpolate_capacity(2020)
        assert cap["nuclear"] == 7.1
        assert cap["coal"] == 5.0

    def test_interpolated_year(self):
        cap = _interpolate_capacity(2019)
        assert cap["nuclear"] == 7.1  # constant
        assert 5.0 < cap["coal"] < 8.0  # interpolated between 2018 and 2020

    def test_before_range(self):
        cap = _interpolate_capacity(2010)
        assert cap == _interpolate_capacity(2015)

    def test_after_range(self):
        cap = _interpolate_capacity(2030)
        assert cap == _interpolate_capacity(2025)


class TestTrainTestSplit:
    def test_split_date(self, full_df):
        train, test = get_train_test_split(full_df, "2025-04-28")
        assert len(train) > 0
        assert len(test) > 0
        assert train.index.max() < pd.Timestamp("2025-04-28")
        assert test.index.min() >= pd.Timestamp("2025-04-28")

    def test_no_overlap(self, full_df):
        train, test = get_train_test_split(full_df, "2025-04-28")
        assert len(set(train.index) & set(test.index)) == 0


class TestCVFolds:
    def test_correct_number_of_folds(self, full_df):
        folds = get_cv_folds(full_df, n_folds=5)
        assert len(folds) == 5

    def test_temporal_ordering(self, full_df):
        folds = get_cv_folds(full_df, n_folds=5)
        for train, val in folds:
            assert train.index.max() <= val.index.min(), \
                "Training data must come before validation data"

    def test_no_train_val_overlap(self, full_df):
        folds = get_cv_folds(full_df, n_folds=5)
        for train, val in folds:
            overlap = set(train.index) & set(val.index)
            assert len(overlap) == 0, "Train and val must not overlap"
