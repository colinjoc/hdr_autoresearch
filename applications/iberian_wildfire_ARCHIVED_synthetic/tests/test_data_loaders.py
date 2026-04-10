"""Tests for data loaders — Iberian wildfire VLF prediction."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add application directory to path
APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    generate_synthetic_fires,
    load_dataset,
    get_temporal_cv_folds,
    get_holdout_split,
    _compute_fwi_from_weather,
    NUTS3_REGIONS,
    VLF_FRACTION,
)


class TestFWIComputation:
    """Test the Van Wagner FWI calculation."""

    def test_fwi_returns_all_components(self):
        result = _compute_fwi_from_weather(25.0, 30.0, 15.0, 0.0)
        expected_keys = {"ffmc", "dmc", "dc", "isi", "bui", "fwi"}
        assert set(result.keys()) == expected_keys

    def test_fwi_values_are_finite(self):
        result = _compute_fwi_from_weather(25.0, 30.0, 15.0, 0.0)
        for key, val in result.items():
            assert np.isfinite(val), f"{key} is not finite: {val}"

    def test_fwi_increases_with_temperature(self):
        cool = _compute_fwi_from_weather(15.0, 40.0, 10.0, 0.0)
        hot = _compute_fwi_from_weather(35.0, 40.0, 10.0, 0.0)
        # Higher temperature should generally increase FWI
        assert hot["fwi"] > cool["fwi"]

    def test_fwi_decreases_with_rain(self):
        dry = _compute_fwi_from_weather(25.0, 30.0, 10.0, 0.0)
        wet = _compute_fwi_from_weather(25.0, 30.0, 10.0, 20.0)
        # Precipitation should reduce FFMC
        assert wet["ffmc"] < dry["ffmc"]

    def test_ffmc_in_valid_range(self):
        result = _compute_fwi_from_weather(25.0, 30.0, 15.0, 0.0)
        assert 0 <= result["ffmc"] <= 101

    def test_fwi_nonnegative(self):
        result = _compute_fwi_from_weather(25.0, 30.0, 15.0, 0.0)
        for key, val in result.items():
            assert val >= 0, f"{key} is negative: {val}"


class TestSyntheticFireGeneration:
    """Test synthetic fire data generation."""

    @pytest.fixture
    def small_df(self):
        return generate_synthetic_fires(seed=42, years=(2020, 2022), n_scale=0.01)

    def test_returns_dataframe(self, small_df):
        assert isinstance(small_df, pd.DataFrame)

    def test_has_required_columns(self, small_df):
        required = [
            "fire_id", "year", "month", "country", "nuts3",
            "burned_area_ha", "is_vlf", "land_cover",
            "temp_c", "rh_pct", "wind_kmh", "precip_mm",
            "fwi", "ffmc", "dmc", "dc", "isi", "bui",
            "spei_1", "spei_3", "spei_6", "spei_12",
            "lfmc", "ndvi", "lat", "lon",
            "elevation_m", "slope_deg", "detection_hour",
        ]
        for col in required:
            assert col in small_df.columns, f"Missing column: {col}"

    def test_vlf_consistency(self, small_df):
        """VLF fires must have burned_area >= 500 ha."""
        vlf = small_df[small_df["is_vlf"] == 1]
        assert (vlf["burned_area_ha"] >= 500).all()

    def test_non_vlf_below_threshold(self, small_df):
        """Non-VLF fires must have burned_area < 500 ha."""
        non_vlf = small_df[small_df["is_vlf"] == 0]
        assert (non_vlf["burned_area_ha"] < 500).all()

    def test_countries_are_pt_es(self, small_df):
        assert set(small_df["country"].unique()) == {"PT", "ES"}

    def test_months_valid(self, small_df):
        assert small_df["month"].min() >= 1
        assert small_df["month"].max() <= 12

    def test_vlf_fraction_reasonable(self, small_df):
        """VLF fraction should be roughly 1-10%."""
        vlf_frac = small_df["is_vlf"].mean()
        assert 0.005 < vlf_frac < 0.15, f"VLF fraction: {vlf_frac:.3f}"

    def test_reproducible_with_same_seed(self):
        df1 = generate_synthetic_fires(seed=123, years=(2020, 2020), n_scale=0.01)
        df2 = generate_synthetic_fires(seed=123, years=(2020, 2020), n_scale=0.01)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_give_different_data(self):
        df1 = generate_synthetic_fires(seed=1, years=(2020, 2020), n_scale=0.01)
        df2 = generate_synthetic_fires(seed=2, years=(2020, 2020), n_scale=0.01)
        # They should have similar sizes but different values
        assert not df1["burned_area_ha"].equals(df2["burned_area_ha"])

    def test_lfmc_nan_before_2018(self, small_df):
        """LFMC should be NaN for fires before Sentinel-2 era."""
        # All fires in small_df are 2020-2022, so LFMC should be present
        assert small_df["lfmc"].notna().any()

    def test_lfmc_nan_before_sentinel2(self):
        """LFMC should be NaN before 2018."""
        df = generate_synthetic_fires(seed=42, years=(2015, 2017), n_scale=0.01)
        assert df["lfmc"].isna().all()

    def test_2025_has_more_fires(self):
        """2025 should have elevated fire count (1.8x multiplier)."""
        df = generate_synthetic_fires(seed=42, years=(2023, 2025), n_scale=0.01)
        n_2024 = len(df[df["year"] == 2024])
        n_2025 = len(df[df["year"] == 2025])
        # 2025 should have roughly 1.8x fires, allow some tolerance
        assert n_2025 > n_2024 * 1.3, f"2025: {n_2025}, 2024: {n_2024}"


class TestTemporalCV:
    """Test temporal cross-validation splitting."""

    @pytest.fixture
    def df(self):
        return generate_synthetic_fires(seed=42, years=(2010, 2024), n_scale=0.01)

    def test_folds_are_temporal(self, df):
        """Train years must always be before validation years."""
        folds = get_temporal_cv_folds(df, n_folds=5)
        for train_idx, val_idx in folds:
            train_years = df.loc[train_idx, "year"].max()
            val_years = df.loc[val_idx, "year"].min()
            assert train_years < val_years, (
                f"Train max year {train_years} >= Val min year {val_years}"
            )

    def test_no_holdout_leakage(self, df):
        """2025 data should never appear in CV folds."""
        # Add some 2025 data
        df_full = pd.concat([df, generate_synthetic_fires(
            seed=42, years=(2025, 2025), n_scale=0.01
        )], ignore_index=True)
        folds = get_temporal_cv_folds(df_full, n_folds=5, holdout_year=2025)
        for train_idx, val_idx in folds:
            assert 2025 not in df_full.loc[train_idx, "year"].values
            assert 2025 not in df_full.loc[val_idx, "year"].values

    def test_returns_correct_number_of_folds(self, df):
        folds = get_temporal_cv_folds(df, n_folds=5)
        assert len(folds) >= 3  # at least 3 folds with 15 years of data

    def test_no_index_overlap_between_folds(self, df):
        folds = get_temporal_cv_folds(df, n_folds=5)
        for train_idx, val_idx in folds:
            assert len(set(train_idx) & set(val_idx)) == 0


class TestHoldoutSplit:
    """Test holdout split."""

    @pytest.fixture
    def df(self):
        return generate_synthetic_fires(seed=42, years=(2020, 2025), n_scale=0.01)

    def test_holdout_contains_only_holdout_year(self, df):
        _, holdout = get_holdout_split(df, 2025)
        assert (holdout["year"] == 2025).all()

    def test_train_does_not_contain_holdout_year(self, df):
        train, _ = get_holdout_split(df, 2025)
        assert 2025 not in train["year"].values

    def test_no_data_loss(self, df):
        train, holdout = get_holdout_split(df, 2025)
        assert len(train) + len(holdout) == len(df)
