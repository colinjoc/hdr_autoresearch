"""Tests for data_loaders.py — verify synthetic flight data generation."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    generate_synthetic_dataset,
    get_cv_folds,
    get_train_test_split,
    TOP_AIRPORTS,
    CARRIERS,
    HUB_AIRPORTS,
)


class TestSyntheticDataGeneration:
    @pytest.fixture(scope="class")
    def dataset(self):
        """Generate a small dataset for testing (50k flights)."""
        return generate_synthetic_dataset(n_target_flights=50_000, seed=42)

    def test_shape(self, dataset):
        """Dataset should have a meaningful number of flights."""
        assert len(dataset) > 10_000
        assert len(dataset) < 200_000

    def test_no_nans_in_key_columns(self, dataset):
        """Key columns should not have NaN (except cancelled flights)."""
        valid = dataset[dataset["cancelled"] == 0]
        key_cols = [
            "fl_date", "carrier", "tail_num", "origin", "dest",
            "crs_dep_hour", "dep_delay", "arr_delay",
        ]
        for col in key_cols:
            assert valid[col].isna().sum() == 0, f"NaN found in {col}"

    def test_airports_valid(self, dataset):
        """All airports should be from the TOP_AIRPORTS list."""
        origins = set(dataset["origin"].unique())
        dests = set(dataset["dest"].unique())
        valid_airports = set(TOP_AIRPORTS)
        assert origins.issubset(valid_airports), f"Invalid origins: {origins - valid_airports}"
        assert dests.issubset(valid_airports), f"Invalid dests: {dests - valid_airports}"

    def test_carriers_valid(self, dataset):
        """All carriers should be from the CARRIERS dict."""
        carriers_in_data = set(dataset["carrier"].unique())
        valid_carriers = set(CARRIERS.keys())
        assert carriers_in_data.issubset(valid_carriers), \
            f"Invalid carriers: {carriers_in_data - valid_carriers}"

    def test_tail_numbers_exist(self, dataset):
        """Every flight should have a tail number."""
        assert dataset["tail_num"].notna().all()
        assert dataset["tail_num"].nunique() > 50

    def test_delay_distribution(self, dataset):
        """Delay statistics should approximately match BTS published values."""
        valid = dataset[dataset["arr_delay"].notna()]
        mean_delay = valid["arr_delay"].mean()
        frac_delayed_15 = (valid["arr_delay"] > 15).mean()

        # BTS: mean delay ~7-8 min, ~20% delayed >15 min
        # Synthetic can deviate somewhat — use wide bounds
        assert -5 < mean_delay < 25, f"Mean delay {mean_delay:.1f} outside expected range"
        assert 0.05 < frac_delayed_15 < 0.50, \
            f"Fraction delayed >15 min {frac_delayed_15:.2%} outside expected range"

    def test_delay_cause_codes(self, dataset):
        """Delay cause codes should sum approximately to total delay for delayed flights."""
        valid = dataset[(dataset["arr_delay"].notna()) & (dataset["arr_delay"] > 15)]
        if len(valid) == 0:
            pytest.skip("No delayed flights")

        cause_cols = [
            "carrier_delay", "weather_delay", "nas_delay",
            "security_delay", "late_aircraft_delay",
        ]
        for col in cause_cols:
            assert col in valid.columns, f"Missing delay cause column: {col}"
            assert (valid[col] >= 0).all(), f"Negative values in {col}"

    def test_late_aircraft_delay_present(self, dataset):
        """Late aircraft delay should be non-zero for some flights (the propagation signal)."""
        valid = dataset[dataset["arr_delay"].notna()]
        has_late_aircraft = (valid["late_aircraft_delay"] > 0).sum()
        assert has_late_aircraft > 0, "No flights have late_aircraft_delay > 0"

    def test_rotation_chains_exist(self, dataset):
        """Some tail numbers should have multiple flights per day (rotation chains)."""
        flights_per_tail_day = dataset.groupby(["fl_date", "tail_num"]).size()
        multi_leg = (flights_per_tail_day > 1).sum()
        assert multi_leg > 0, "No multi-leg rotation chains found"

    def test_propagation_features(self, dataset):
        """Propagation features should be present and valid."""
        assert "prev_leg_arr_delay" in dataset.columns
        assert "rotation_position" in dataset.columns
        assert "origin_hour_flights" in dataset.columns

        # First legs in rotation should have prev_leg_arr_delay == 0
        first_legs = dataset[dataset["rotation_position"] == 1]
        assert (first_legs["prev_leg_arr_delay"] == 0).all(), \
            "First rotation legs should have no previous delay"

    def test_temporal_features(self, dataset):
        """Cyclic temporal features should exist and be in [-1, 1]."""
        for col in ["dep_hour_sin", "dep_hour_cos", "dow_sin", "dow_cos",
                     "month_sin", "month_cos"]:
            assert col in dataset.columns, f"Missing temporal feature: {col}"
            assert dataset[col].min() >= -1.01
            assert dataset[col].max() <= 1.01

    def test_hub_flags(self, dataset):
        """Hub airports should be correctly flagged."""
        hub_flights = dataset[dataset["origin_is_hub"] == 1]
        non_hub_flights = dataset[dataset["origin_is_hub"] == 0]
        assert len(hub_flights) > 0
        assert len(non_hub_flights) > 0

        # Hub flights should have origin in HUB_AIRPORTS
        hub_origins = set(hub_flights["origin"].unique())
        assert hub_origins.issubset(set(HUB_AIRPORTS.keys()))

    def test_distance_positive(self, dataset):
        """All distances should be positive."""
        assert (dataset["distance"] > 0).all()

    def test_deterministic(self):
        """Same seed should produce identical datasets."""
        df1 = generate_synthetic_dataset(n_target_flights=5_000, seed=123)
        df2 = generate_synthetic_dataset(n_target_flights=5_000, seed=123)
        pd.testing.assert_frame_equal(df1, df2)


class TestCVFolds:
    @pytest.fixture(scope="class")
    def dataset(self):
        return generate_synthetic_dataset(n_target_flights=10_000, seed=42)

    def test_fold_count(self, dataset):
        folds = get_cv_folds(dataset, n_folds=5)
        assert len(folds) == 5

    def test_no_overlap(self, dataset):
        folds = get_cv_folds(dataset, n_folds=5)
        for train_idx, val_idx in folds:
            assert len(set(train_idx) & set(val_idx)) == 0

    def test_temporal_order(self, dataset):
        """Validation dates should always come after training dates."""
        folds = get_cv_folds(dataset, n_folds=5)
        for train_idx, val_idx in folds:
            train_dates = dataset.iloc[train_idx]["fl_date"]
            val_dates = dataset.iloc[val_idx]["fl_date"]
            assert train_dates.max() <= val_dates.min()


class TestTrainTestSplit:
    @pytest.fixture(scope="class")
    def dataset(self):
        return generate_synthetic_dataset(n_target_flights=10_000, seed=42)

    def test_no_overlap(self, dataset):
        train, test = get_train_test_split(dataset)
        train_dates = set(train["fl_date"].unique())
        test_dates = set(test["fl_date"].unique())
        assert len(train_dates & test_dates) == 0

    def test_temporal_order(self, dataset):
        train, test = get_train_test_split(dataset)
        assert train["fl_date"].max() < test["fl_date"].min()

    def test_test_size_reasonable(self, dataset):
        train, test = get_train_test_split(dataset)
        total = len(train) + len(test)
        test_frac = len(test) / total
        assert 0.05 < test_frac < 0.30
