"""Tests for data_loaders.py — verify synthetic Xylella decline data generation."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    generate_synthetic_data,
    add_derived_features,
    get_cv_folds_spatial,
    get_train_test_split,
    load_dataset,
    ALL_PROVINCES,
    PUGLIA_PROVINCES,
    SPAIN_PROVINCES,
    FIRST_DETECTION_YEAR,
    _haversine_km,
)


@pytest.fixture
def small_df():
    """Generate a small synthetic dataset for testing."""
    df = generate_synthetic_data(n_municipalities=200, seed=42)
    return add_derived_features(df)


@pytest.fixture
def realistic_df():
    """Generate realistic-size dataset."""
    df = generate_synthetic_data(seed=42)
    return add_derived_features(df)


class TestHaversine:
    def test_same_point_zero(self):
        assert _haversine_km(40.0, 18.0, 40.0, 18.0) == 0.0

    def test_known_distance(self):
        # Lecce to Bari is roughly 150 km
        d = _haversine_km(40.20, 18.17, 41.12, 16.87)
        assert 100 < d < 200

    def test_positive(self):
        d = _haversine_km(38.0, -0.5, 40.0, 18.0)
        assert d > 0


class TestSyntheticDataGeneration:
    def test_returns_dataframe(self, small_df):
        assert isinstance(small_df, pd.DataFrame)
        assert len(small_df) >= 100  # At least some municipalities

    def test_has_required_columns(self, small_df):
        required = [
            "municipality_id", "province", "country",
            "latitude", "longitude", "elevation",
            "prediction_year",
            "jan_tmin_mean", "winter_tmin_abs",
            "annual_precip_mm", "summer_precip_mm",
            "precip_deficit_frac",
            "frost_days_below_minus6", "frost_days_below_minus12",
            "coldest_month_anomaly",
            "ndvi_mean", "ndvi_trend", "ndvi_anomaly", "ndvi_std",
            "evi_mean",
            "dist_epicentre_km", "dist_nearest_declining_km",
            "olive_area_fraction",
            "already_affected",
            "new_decline_12m",
        ]
        for col in required:
            assert col in small_df.columns, f"Missing column: {col}"

    def test_all_provinces_present(self, realistic_df):
        present = set(realistic_df["province"].unique())
        for p in ALL_PROVINCES:
            assert p in present, f"Missing province: {p}"

    def test_label_is_binary(self, small_df):
        assert set(small_df["new_decline_12m"].unique()).issubset({0, 1})

    def test_both_classes_present(self, small_df):
        """Both 0 and 1 labels should be present."""
        assert small_df["new_decline_12m"].nunique() == 2

    def test_ndvi_in_reasonable_range(self, small_df):
        assert (small_df["ndvi_mean"] > 0).all()
        assert (small_df["ndvi_mean"] < 0.8).all()

    def test_elevation_positive(self, small_df):
        assert (small_df["elevation"] > 0).all()

    def test_frost_days_non_negative(self, small_df):
        assert (small_df["frost_days_below_minus6"] >= 0).all()
        assert (small_df["frost_days_below_minus12"] >= 0).all()

    def test_distance_epicentre_non_negative(self, small_df):
        assert (small_df["dist_epicentre_km"] >= 0).all()

    def test_countries(self, small_df):
        countries = set(small_df["country"].unique())
        assert "Italy" in countries
        assert "Spain" in countries

    def test_municipality_ids_unique(self, small_df):
        assert small_df["municipality_id"].nunique() == len(small_df)


class TestDerivedFeatures:
    def test_derived_columns_present(self, small_df):
        derived = [
            "ndvi_x_jan_tmin", "log_dist_epicentre",
            "log_dist_nearest_declining", "frost_severity_index",
            "aridity_proxy", "ndvi_decline_rate",
            "lat_from_salento", "province_ordinal",
            "greenup_proxy", "soil_moisture_proxy",
        ]
        for col in derived:
            assert col in small_df.columns, f"Missing derived column: {col}"

    def test_no_nan_in_derived(self, small_df):
        derived = [
            "ndvi_x_jan_tmin", "log_dist_epicentre",
            "frost_severity_index", "aridity_proxy",
        ]
        for col in derived:
            assert not small_df[col].isna().any(), f"NaN in {col}"

    def test_log_dist_non_negative(self, small_df):
        assert (small_df["log_dist_epicentre"] >= 0).all()


class TestSpatialCV:
    def test_folds_cover_all_data(self, small_df):
        folds = get_cv_folds_spatial(small_df, n_folds=3)
        all_val_idx = np.concatenate([v for _, v in folds])
        assert len(all_val_idx) == len(small_df)

    def test_no_overlap_between_folds(self, small_df):
        folds = get_cv_folds_spatial(small_df, n_folds=3)
        for i in range(len(folds)):
            for j in range(i + 1, len(folds)):
                overlap = np.intersect1d(folds[i][1], folds[j][1])
                assert len(overlap) == 0

    def test_province_not_split(self, small_df):
        """Each province should be entirely in train or entirely in val."""
        folds = get_cv_folds_spatial(small_df, n_folds=3)
        for train_idx, val_idx in folds:
            train_provs = set(small_df.iloc[train_idx]["province"].unique())
            val_provs = set(small_df.iloc[val_idx]["province"].unique())
            assert len(train_provs & val_provs) == 0, \
                "Province appears in both train and val"


class TestTrainTestSplit:
    def test_returns_two_dataframes(self, small_df):
        train, test = get_train_test_split(small_df)
        assert isinstance(train, pd.DataFrame)
        assert isinstance(test, pd.DataFrame)

    def test_no_province_overlap(self, small_df):
        train, test = get_train_test_split(small_df)
        train_provs = set(train["province"].unique())
        test_provs = set(test["province"].unique())
        assert len(train_provs & test_provs) == 0

    def test_total_rows_preserved(self, small_df):
        train, test = get_train_test_split(small_df)
        assert len(train) + len(test) == len(small_df)


class TestLoadDataset:
    def test_returns_dataframe(self):
        df = load_dataset(n_municipalities=100, seed=42)
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 50

    def test_has_derived_features(self):
        df = load_dataset(n_municipalities=100, seed=42)
        assert "ndvi_x_jan_tmin" in df.columns
        assert "log_dist_epicentre" in df.columns
