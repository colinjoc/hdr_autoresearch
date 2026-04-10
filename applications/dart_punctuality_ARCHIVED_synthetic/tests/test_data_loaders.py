"""Tests for data_loaders.py — verify synthetic data generation."""

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
    MONTHLY_PUNCTUALITY,
    TIMETABLE_CHANGE_DATE,
)


class TestSyntheticDataGeneration:
    @pytest.fixture
    def dataset(self):
        return generate_synthetic_dataset(seed=42)

    def test_shape(self, dataset):
        # ~3 years of data minus first 7 days for lag features
        assert len(dataset) > 1050
        assert len(dataset) < 1100

    def test_no_nans(self, dataset):
        assert dataset.isna().sum().sum() == 0

    def test_date_range(self, dataset):
        assert dataset.index.min() >= pd.Timestamp("2023-01-01")
        assert dataset.index.max() <= pd.Timestamp("2025-12-31")

    def test_target_column_exists(self, dataset):
        assert "bad_day" in dataset.columns
        assert "daily_punctuality" in dataset.columns

    def test_bad_day_binary(self, dataset):
        assert set(dataset["bad_day"].unique()).issubset({0, 1})

    def test_bad_day_definition(self, dataset):
        """Bad day = punctuality < 0.85 (>15% delayed)."""
        expected = (dataset["daily_punctuality"] < 0.85).astype(int)
        np.testing.assert_array_equal(dataset["bad_day"].values, expected.values)

    def test_bad_day_prevalence(self, dataset):
        """Bad days should be a meaningful minority, not trivially rare or common."""
        rate = dataset["bad_day"].mean()
        assert 0.05 < rate < 0.60, f"Bad day rate {rate:.2%} outside expected range"

    def test_monthly_calibration(self, dataset):
        """Monthly means should approximately match published punctuality."""
        for (year, month), target in MONTHLY_PUNCTUALITY.items():
            mask = (dataset.index.year == year) & (dataset.index.month == month)
            if mask.sum() == 0:
                continue
            monthly_mean = dataset.loc[mask, "daily_punctuality"].mean()
            assert abs(monthly_mean - target) < 0.05, (
                f"{year}-{month:02d}: mean={monthly_mean:.3f}, target={target:.3f}"
            )

    def test_june_2024_high(self, dataset):
        """June 2024 should be ~92.8% on-time."""
        mask = (dataset.index.year == 2024) & (dataset.index.month == 6)
        mean = dataset.loc[mask, "daily_punctuality"].mean()
        assert mean > 0.88, f"June 2024 too low: {mean:.3f}"

    def test_october_2024_low(self, dataset):
        """October 2024 should be ~64.5% on-time."""
        mask = (dataset.index.year == 2024) & (dataset.index.month == 10)
        mean = dataset.loc[mask, "daily_punctuality"].mean()
        assert mean < 0.72, f"October 2024 too high: {mean:.3f}"

    def test_collapse_visible(self, dataset):
        """The June->October 2024 collapse should be clear."""
        june_mask = (dataset.index.year == 2024) & (dataset.index.month == 6)
        oct_mask = (dataset.index.year == 2024) & (dataset.index.month == 10)
        june_mean = dataset.loc[june_mask, "daily_punctuality"].mean()
        oct_mean = dataset.loc[oct_mask, "daily_punctuality"].mean()
        drop = june_mean - oct_mean
        assert drop > 0.20, f"Collapse too small: {drop:.3f}"

    def test_weather_columns(self, dataset):
        required = ["wind_speed_kmh", "rainfall_mm", "temperature_c"]
        for col in required:
            assert col in dataset.columns, f"Missing weather column: {col}"

    def test_wind_speed_range(self, dataset):
        assert dataset["wind_speed_kmh"].min() >= 0
        assert dataset["wind_speed_kmh"].max() < 130

    def test_temperature_range(self, dataset):
        assert dataset["temperature_c"].min() > -15
        assert dataset["temperature_c"].max() < 40

    def test_feature_columns(self, dataset):
        required = [
            "dow_sin", "dow_cos", "month_sin", "month_cos",
            "is_weekend", "post_timetable_change",
            "prev_day_punct", "rolling_7d_punct", "morning_punct",
        ]
        for col in required:
            assert col in dataset.columns, f"Missing feature: {col}"

    def test_post_timetable_change(self, dataset):
        """Post-timetable-change flag should be 0 before Sep 2024, 1 after."""
        pre = dataset[dataset.index < "2024-09-01"]["post_timetable_change"]
        post = dataset[dataset.index >= "2024-09-01"]["post_timetable_change"]
        assert (pre == 0).all()
        assert (post == 1).all()

    def test_deterministic(self):
        """Same seed should produce identical datasets."""
        df1 = generate_synthetic_dataset(seed=123)
        df2 = generate_synthetic_dataset(seed=123)
        pd.testing.assert_frame_equal(df1, df2)


class TestCVFolds:
    def test_fold_count(self):
        df = generate_synthetic_dataset(seed=42)
        folds = get_cv_folds(df, n_folds=5)
        assert len(folds) == 5

    def test_no_overlap(self):
        df = generate_synthetic_dataset(seed=42)
        folds = get_cv_folds(df, n_folds=5)
        for train_idx, val_idx in folds:
            assert len(set(train_idx) & set(val_idx)) == 0

    def test_temporal_order(self):
        """Validation indices should always come after training indices."""
        df = generate_synthetic_dataset(seed=42)
        folds = get_cv_folds(df, n_folds=5)
        for train_idx, val_idx in folds:
            assert train_idx.max() < val_idx.min()


class TestTrainTestSplit:
    def test_no_overlap(self):
        df = generate_synthetic_dataset(seed=42)
        train, test = get_train_test_split(df, test_months=3)
        assert train.index.max() < test.index.min()

    def test_test_size(self):
        df = generate_synthetic_dataset(seed=42)
        train, test = get_train_test_split(df, test_months=3)
        assert len(test) > 60  # ~3 months
        assert len(test) < 120
