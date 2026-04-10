"""Tests for data_loaders.py — verify synthetic radon data generation and feature engineering."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    generate_synthetic_radon_data,
    add_derived_features,
    get_cv_folds_spatial,
    get_train_test_split,
    COUNTIES,
    BEDROCK_CLASSES,
    QUATERNARY_CLASSES,
    BER_RATINGS,
)


@pytest.fixture
def small_df():
    """Generate a small synthetic dataset for testing."""
    df = generate_synthetic_radon_data(n_areas=300, seed=42)
    return add_derived_features(df)


@pytest.fixture
def medium_df():
    """Generate a medium synthetic dataset for testing."""
    df = generate_synthetic_radon_data(n_areas=2000, seed=42)
    return add_derived_features(df)


class TestSyntheticDataGeneration:
    def test_returns_dataframe(self, small_df):
        assert isinstance(small_df, pd.DataFrame)
        assert len(small_df) == 300

    def test_has_required_columns(self, small_df):
        required = [
            "area_id", "county", "latitude", "longitude", "elevation_mean",
            "eU_mean", "eTh_mean", "K_mean",
            "bedrock_code", "quat_code",
            "mean_ber_rating_ordinal", "mean_air_permeability",
            "pct_slab_on_ground", "pct_suspended_timber",
            "mean_year_built", "pct_detached",
            "pct_above_200", "is_hra",
            "n_measurements",
        ]
        for col in required:
            assert col in small_df.columns, f"Missing column: {col}"

    def test_eU_positive(self, small_df):
        assert (small_df["eU_mean"] > 0).all()

    def test_eTh_positive(self, small_df):
        assert (small_df["eTh_mean"] > 0).all()

    def test_K_positive(self, small_df):
        assert (small_df["K_mean"] > 0).all()

    def test_counties_valid(self, small_df):
        for c in small_df["county"].unique():
            assert c in COUNTIES, f"Invalid county: {c}"

    def test_bedrock_codes_valid(self, small_df):
        for code in small_df["bedrock_code"].unique():
            assert code in BEDROCK_CLASSES, f"Invalid bedrock code: {code}"

    def test_quaternary_codes_valid(self, small_df):
        for code in small_df["quat_code"].unique():
            assert code in QUATERNARY_CLASSES, f"Invalid quaternary code: {code}"

    def test_is_hra_binary(self, small_df):
        assert set(small_df["is_hra"].unique()).issubset({0, 1})

    def test_pct_above_200_range(self, small_df):
        assert (small_df["pct_above_200"] >= 0).all()
        assert (small_df["pct_above_200"] <= 100).all()

    def test_hra_consistent_with_pct(self, small_df):
        """HRA should be 1 when pct_above_200 > 10."""
        for _, row in small_df.iterrows():
            if row["pct_above_200"] > 10:
                assert row["is_hra"] == 1
            else:
                assert row["is_hra"] == 0

    def test_hra_prevalence_realistic(self, medium_df):
        """About 25-35% of areas should be HRA (Irish average ~28%)."""
        hra_pct = medium_df["is_hra"].mean() * 100
        assert 15 < hra_pct < 45, f"HRA prevalence {hra_pct:.1f}% outside expected range"

    def test_eU_range_realistic(self, medium_df):
        """eU should range from ~0.5 to ~15 ppm (typical Irish range)."""
        assert medium_df["eU_mean"].min() > 0
        assert medium_df["eU_mean"].max() < 30
        mean_eU = medium_df["eU_mean"].mean()
        assert 1 < mean_eU < 6, f"Mean eU {mean_eU:.1f} outside expected range"

    def test_deterministic_with_seed(self):
        df1 = generate_synthetic_radon_data(n_areas=100, seed=42)
        df2 = generate_synthetic_radon_data(n_areas=100, seed=42)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_different_data(self):
        df1 = generate_synthetic_radon_data(n_areas=100, seed=42)
        df2 = generate_synthetic_radon_data(n_areas=100, seed=99)
        assert not df1["eU_mean"].equals(df2["eU_mean"])

    def test_latitude_range(self, small_df):
        """Irish latitude: ~51.4 to ~55.4."""
        assert small_df["latitude"].min() > 51
        assert small_df["latitude"].max() < 56

    def test_longitude_range(self, small_df):
        """Irish longitude: ~-10.5 to ~-5.5."""
        assert small_df["longitude"].min() > -11
        assert small_df["longitude"].max() < -5

    def test_elevation_positive(self, small_df):
        assert (small_df["elevation_mean"] >= 0).all()

    def test_ber_rating_ordinal_range(self, small_df):
        assert (small_df["mean_ber_rating_ordinal"] >= 1).all()
        assert (small_df["mean_ber_rating_ordinal"] <= 15).all()

    def test_air_permeability_positive(self, small_df):
        assert (small_df["mean_air_permeability"] > 0).all()

    def test_pct_features_range(self, small_df):
        for col in ["pct_slab_on_ground", "pct_suspended_timber", "pct_detached"]:
            assert (small_df[col] >= 0).all(), f"{col} has negative values"
            assert (small_df[col] <= 100).all(), f"{col} exceeds 100"


class TestDerivedFeatures:
    def test_eU_eTh_ratio_positive(self, small_df):
        assert (small_df["eU_eTh_ratio"] > 0).all()

    def test_total_dose_rate_positive(self, small_df):
        assert (small_df["total_dose_rate"] > 0).all()

    def test_is_granite_binary(self, small_df):
        assert set(small_df["is_granite"].unique()).issubset({0, 1})

    def test_is_limestone_binary(self, small_df):
        assert set(small_df["is_limestone"].unique()).issubset({0, 1})

    def test_is_shale_binary(self, small_df):
        assert set(small_df["is_shale"].unique()).issubset({0, 1})

    def test_quat_permeability_ordinal(self, small_df):
        assert (small_df["quat_permeability"] >= 1).all()
        assert (small_df["quat_permeability"] <= 6).all()

    def test_is_rock_surface_binary(self, small_df):
        assert set(small_df["is_rock_surface"].unique()).issubset({0, 1})

    def test_is_peat_binary(self, small_df):
        assert set(small_df["is_peat"].unique()).issubset({0, 1})

    def test_derived_features_exist(self, small_df):
        expected = [
            "eU_eTh_ratio", "total_dose_rate",
            "is_granite", "is_limestone", "is_shale",
            "quat_permeability", "is_rock_surface", "is_peat",
            "log_eU",
        ]
        for col in expected:
            assert col in small_df.columns, f"Missing derived feature: {col}"


class TestSpatialCV:
    def test_correct_number_of_folds(self, small_df):
        folds = get_cv_folds_spatial(small_df, n_folds=5)
        assert len(folds) == 5

    def test_no_county_overlap(self, small_df):
        """Counties in train and val must not overlap (spatial CV)."""
        folds = get_cv_folds_spatial(small_df, n_folds=5)
        for train, val in folds:
            train_counties = set(train["county"])
            val_counties = set(val["county"])
            assert len(train_counties & val_counties) == 0, \
                f"County overlap: {train_counties & val_counties}"

    def test_all_data_used(self, small_df):
        folds = get_cv_folds_spatial(small_df, n_folds=5)
        all_val_ids = set()
        for _, val in folds:
            all_val_ids.update(val["area_id"])
        assert len(all_val_ids) == len(small_df)


class TestTrainTestSplit:
    def test_split_sizes(self, small_df):
        train, test = get_train_test_split(small_df, test_fraction=0.15)
        total = len(train) + len(test)
        assert total == len(small_df)
        assert abs(len(test) / total - 0.15) < 0.10

    def test_no_overlap(self, small_df):
        train, test = get_train_test_split(small_df)
        train_ids = set(train["area_id"])
        test_ids = set(test["area_id"])
        assert len(train_ids & test_ids) == 0

    def test_spatial_separation(self, small_df):
        """Train and test counties should not overlap."""
        train, test = get_train_test_split(small_df)
        train_counties = set(train["county"])
        test_counties = set(test["county"])
        assert len(train_counties & test_counties) == 0, \
            f"County overlap in train/test: {train_counties & test_counties}"
