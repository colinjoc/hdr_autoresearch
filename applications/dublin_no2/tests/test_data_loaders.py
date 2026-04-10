"""
Tests for Dublin NO2 data loaders.

Verifies synthetic dataset generation, temporal CV folds, and feature
engineering for the Dublin/Cork NO2 source attribution project.
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

from data_loaders import (
    generate_synthetic_dataset,
    get_cv_folds,
    get_train_test_split,
    STATIONS,
    WHO_ANNUAL_GUIDELINE,
    WHO_24H_GUIDELINE,
    EU_ANNUAL_LIMIT,
)


@pytest.fixture(scope="module")
def dataset():
    """Generate synthetic dataset once for all tests."""
    return generate_synthetic_dataset(seed=42)


class TestDatasetShape:
    """Test that the dataset has the expected shape and columns."""

    def test_returns_dataframe(self, dataset):
        assert isinstance(dataset, pd.DataFrame)

    def test_has_datetime_index(self, dataset):
        assert isinstance(dataset.index, pd.DatetimeIndex)

    def test_minimum_rows(self, dataset):
        # 6 years of hourly data for 5+ stations => lots of rows
        # At minimum ~43800 rows per station × 5 stations = ~219000
        # But we may use long-form (station as column) or wide-form
        assert len(dataset) > 10000, f"Expected >10k rows, got {len(dataset)}"

    def test_has_no2_column(self, dataset):
        assert "no2_ugm3" in dataset.columns

    def test_has_station_column(self, dataset):
        assert "station" in dataset.columns

    def test_has_weather_columns(self, dataset):
        required = ["wind_speed_ms", "wind_dir_deg", "temperature_c", "rainfall_mm"]
        for col in required:
            assert col in dataset.columns, f"Missing weather column: {col}"

    def test_has_temporal_columns(self, dataset):
        required = ["hour", "dow", "month", "is_weekend"]
        for col in required:
            assert col in dataset.columns, f"Missing temporal column: {col}"


class TestNO2Values:
    """Test NO2 concentrations are physically realistic."""

    def test_no2_positive(self, dataset):
        assert (dataset["no2_ugm3"] >= 0).all()

    def test_no2_not_extreme(self, dataset):
        # Urban NO2 should rarely exceed 200 ug/m3 even in worst conditions
        assert dataset["no2_ugm3"].max() < 300

    def test_mean_no2_realistic_range(self, dataset):
        # Dublin annual mean NO2 is typically 15-40 ug/m3
        mean_no2 = dataset["no2_ugm3"].mean()
        assert 5 < mean_no2 < 60, f"Mean NO2 {mean_no2} outside realistic range"

    def test_who_exceedances_exist(self, dataset):
        # There should be some 24-hour exceedances of 25 ug/m3
        daily_means = dataset.groupby([dataset.index.date, "station"])["no2_ugm3"].mean()
        n_exceedances = (daily_means > WHO_24H_GUIDELINE).sum()
        assert n_exceedances > 0, "No WHO 24h exceedances — unrealistic"

    def test_station_differences(self, dataset):
        """Traffic stations should have higher NO2 than background."""
        station_means = dataset.groupby("station")["no2_ugm3"].mean()
        # Pearse St (traffic) should be higher than a background station
        if "pearse_street" in station_means.index and "rathmines" in station_means.index:
            assert station_means["pearse_street"] > station_means["rathmines"]


class TestWeatherValues:
    """Test weather data is physically realistic for Dublin."""

    def test_temperature_range(self, dataset):
        assert dataset["temperature_c"].min() > -15
        assert dataset["temperature_c"].max() < 35

    def test_wind_speed_positive(self, dataset):
        assert (dataset["wind_speed_ms"] >= 0).all()

    def test_rainfall_non_negative(self, dataset):
        assert (dataset["rainfall_mm"] >= 0).all()

    def test_wind_direction_range(self, dataset):
        assert (dataset["wind_dir_deg"] >= 0).all()
        assert (dataset["wind_dir_deg"] < 360).all()


class TestTemporalPatterns:
    """Test that temporal patterns match known Dublin NO2 behavior."""

    def test_weekday_higher_than_weekend(self, dataset):
        weekday = dataset[dataset["is_weekend"] == 0]["no2_ugm3"].mean()
        weekend = dataset[dataset["is_weekend"] == 1]["no2_ugm3"].mean()
        assert weekday > weekend, "Weekday NO2 should exceed weekend"

    def test_rush_hour_pattern(self, dataset):
        """NO2 should peak during rush hours (7-9, 16-19)."""
        hourly = dataset.groupby("hour")["no2_ugm3"].mean()
        # Morning rush (8am) should be higher than 3am
        assert hourly.loc[8] > hourly.loc[3]

    def test_heating_season_effect(self, dataset):
        """Winter NO2 should be higher than summer (heating + less dispersion)."""
        winter = dataset[dataset["month"].isin([11, 12, 1, 2])]["no2_ugm3"].mean()
        summer = dataset[dataset["month"].isin([5, 6, 7, 8])]["no2_ugm3"].mean()
        assert winter > summer


class TestCVFolds:
    """Test temporal cross-validation fold generation."""

    def test_returns_correct_number_of_folds(self, dataset):
        folds = get_cv_folds(dataset, n_folds=5)
        assert len(folds) == 5

    def test_no_temporal_leakage(self, dataset):
        """Validation data must always come AFTER training data."""
        folds = get_cv_folds(dataset, n_folds=5)
        for train_idx, val_idx in folds:
            assert train_idx.max() < val_idx.min()

    def test_folds_cover_all_data(self, dataset):
        folds = get_cv_folds(dataset, n_folds=5)
        all_val = np.concatenate([val for _, val in folds])
        # Not all data needs to be in validation, but should cover majority
        assert len(all_val) > len(dataset) * 0.5


class TestTrainTestSplit:
    """Test holdout split."""

    def test_temporal_ordering(self, dataset):
        train, test = get_train_test_split(dataset, test_months=6)
        assert train.index.max() < test.index.min()

    def test_test_size_reasonable(self, dataset):
        train, test = get_train_test_split(dataset, test_months=6)
        assert len(test) > 0
        assert len(train) > len(test)


class TestConstants:
    """Test that WHO/EU guideline constants are correct."""

    def test_who_annual(self):
        assert WHO_ANNUAL_GUIDELINE == 10  # ug/m3

    def test_who_24h(self):
        assert WHO_24H_GUIDELINE == 25  # ug/m3

    def test_eu_annual(self):
        assert EU_ANNUAL_LIMIT == 40  # ug/m3 (current, dropping to 20 by 2030)
