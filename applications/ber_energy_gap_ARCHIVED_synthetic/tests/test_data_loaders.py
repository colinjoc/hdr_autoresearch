"""Tests for data_loaders.py — verify synthetic BER data generation and feature engineering."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    generate_synthetic_ber_data,
    add_derived_features,
    get_cv_folds,
    get_train_test_split,
    energy_value_to_ber_rating,
    _compute_wall_u_value,
    _get_wall_type_for_era,
    _get_heating_type,
    WALL_TYPES,
    INSULATION_TYPES,
    BER_BANDS,
    COUNTIES,
    COUNTY_HDD,
)


@pytest.fixture
def small_df():
    """Generate a small synthetic dataset for testing."""
    df = generate_synthetic_ber_data(n_records=500, seed=42)
    return add_derived_features(df)


@pytest.fixture
def medium_df():
    """Generate a medium synthetic dataset for testing."""
    df = generate_synthetic_ber_data(n_records=5000, seed=42)
    return add_derived_features(df)


class TestSyntheticDataGeneration:
    def test_returns_dataframe(self, small_df):
        assert isinstance(small_df, pd.DataFrame)
        assert len(small_df) == 500

    def test_has_required_columns(self, small_df):
        required = [
            "county", "year_built", "dwelling_type", "floor_area_m2",
            "wall_type", "insulation_type", "wall_u_value",
            "roof_insulation_mm", "roof_u_value",
            "window_type", "window_u_value",
            "heating_type", "heating_efficiency",
            "ventilation_type", "air_permeability",
            "energy_value_kwh_m2_yr", "ber_rating",
            "assessment_year", "assessor_id",
            "hdd", "co2_emissions_kg_m2_yr",
        ]
        for col in required:
            assert col in small_df.columns, f"Missing column: {col}"

    def test_energy_value_positive(self, small_df):
        assert (small_df["energy_value_kwh_m2_yr"] > 0).all()

    def test_floor_area_positive(self, small_df):
        assert (small_df["floor_area_m2"] > 0).all()

    def test_u_values_positive(self, small_df):
        for col in ["wall_u_value", "roof_u_value", "floor_u_value", "window_u_value"]:
            assert (small_df[col] > 0).all(), f"{col} has non-positive values"

    def test_heating_efficiency_positive(self, small_df):
        assert (small_df["heating_efficiency"] > 0).all()

    def test_counties_valid(self, small_df):
        for c in small_df["county"].unique():
            assert c in COUNTIES, f"Invalid county: {c}"

    def test_ber_ratings_valid(self, small_df):
        valid_ratings = set(BER_BANDS.keys())
        for r in small_df["ber_rating"].unique():
            assert r in valid_ratings, f"Invalid BER rating: {r}"

    def test_year_built_range(self, small_df):
        assert small_df["year_built"].min() >= 1900
        assert small_df["year_built"].max() <= 2029

    def test_assessment_year_after_year_built(self, small_df):
        assert (small_df["assessment_year"] >= small_df["year_built"]).all()

    def test_assessment_year_after_2006(self, small_df):
        assert (small_df["assessment_year"] >= 2007).all()

    def test_deterministic_with_seed(self):
        df1 = generate_synthetic_ber_data(n_records=100, seed=42)
        df2 = generate_synthetic_ber_data(n_records=100, seed=42)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_different_data(self):
        df1 = generate_synthetic_ber_data(n_records=100, seed=42)
        df2 = generate_synthetic_ber_data(n_records=100, seed=99)
        assert not df1["energy_value_kwh_m2_yr"].equals(df2["energy_value_kwh_m2_yr"])

    def test_ber_rating_distribution_realistic(self, medium_df):
        """Check BER distribution roughly matches SEAI published statistics."""
        counts = medium_df["ber_rating"].value_counts(normalize=True)
        # Most common should be C-D range
        cd_fraction = sum(counts.get(r, 0) for r in ["C1", "C2", "C3", "D1", "D2"])
        assert cd_fraction > 0.30, f"C-D fraction {cd_fraction:.2f} too low"
        # G should be uncommon
        g_fraction = counts.get("G", 0)
        assert g_fraction < 0.15, f"G fraction {g_fraction:.2f} too high"

    def test_energy_value_range_realistic(self, medium_df):
        """Energy values should span realistic range for Irish housing."""
        assert medium_df["energy_value_kwh_m2_yr"].min() > 0
        # 99th percentile should be below 800; extreme outliers can exceed
        p99 = medium_df["energy_value_kwh_m2_yr"].quantile(0.99)
        assert p99 < 800, f"99th percentile {p99:.0f} too high"
        mean_ev = medium_df["energy_value_kwh_m2_yr"].mean()
        assert 100 < mean_ev < 400, f"Mean energy value {mean_ev:.0f} outside expected range"


class TestWallUValue:
    def test_insulation_reduces_u_value(self):
        base_u = _compute_wall_u_value("cavity_block_unfilled", "none")
        insulated_u = _compute_wall_u_value("cavity_block_unfilled", "cavity_fill_bead")
        assert insulated_u < base_u

    def test_u_value_always_positive(self):
        for wt in WALL_TYPES:
            for ins in INSULATION_TYPES:
                u = _compute_wall_u_value(wt, ins)
                assert u > 0, f"U-value <= 0 for {wt} + {ins}"

    def test_better_insulation_lower_u(self):
        u_none = _compute_wall_u_value("solid_brick_225mm", "none")
        u_25mm = _compute_wall_u_value("solid_brick_225mm", "dry_lining_25mm")
        u_50mm = _compute_wall_u_value("solid_brick_225mm", "dry_lining_50mm")
        assert u_none > u_25mm > u_50mm


class TestBERRating:
    def test_low_energy_gets_a(self):
        assert energy_value_to_ber_rating(15) == "A1"
        assert energy_value_to_ber_rating(40) == "A2"

    def test_high_energy_gets_g(self):
        assert energy_value_to_ber_rating(500) == "G"
        assert energy_value_to_ber_rating(1000) == "G"

    def test_mid_range(self):
        assert energy_value_to_ber_rating(250) == "D1"


class TestDerivedFeatures:
    def test_regulation_era_range(self, small_df):
        assert small_df["regulation_era"].min() >= 0
        assert small_df["regulation_era"].max() <= 5

    def test_log_floor_area_positive(self, small_df):
        assert (small_df["log_floor_area"] > 0).all()

    def test_form_factor_proxy_range(self, small_df):
        assert small_df["form_factor_proxy"].min() >= 1.0
        assert small_df["form_factor_proxy"].max() <= 3.5

    def test_is_heat_pump_binary(self, small_df):
        assert set(small_df["is_heat_pump"].unique()).issubset({0, 1})

    def test_derived_features_exist(self, small_df):
        expected = [
            "regulation_era", "vintage_decade", "log_floor_area",
            "area_per_bedroom", "form_factor_proxy", "is_heat_pump",
            "is_condensing", "is_solid_fuel", "fuel_group",
            "wall_quality_ordinal", "window_quality_ordinal",
            "has_secondary_heating", "has_mvhr",
            "wall_u_x_eff_inv", "building_age_at_assessment", "is_nzeb",
        ]
        for col in expected:
            assert col in small_df.columns, f"Missing derived feature: {col}"


class TestTrainTestSplit:
    def test_split_sizes(self, small_df):
        train, test = get_train_test_split(small_df, test_fraction=0.15)
        total = len(train) + len(test)
        assert total == len(small_df)
        assert abs(len(test) / total - 0.15) < 0.05

    def test_no_overlap(self, small_df):
        train, test = get_train_test_split(small_df)
        train_ids = set(train["ber_number"])
        test_ids = set(test["ber_number"])
        assert len(train_ids & test_ids) == 0

    def test_stratified(self, medium_df):
        """Test that BER rating distribution is preserved in splits."""
        train, test = get_train_test_split(medium_df)
        train_dist = train["ber_rating"].value_counts(normalize=True)
        test_dist = test["ber_rating"].value_counts(normalize=True)
        for rating in train_dist.index:
            if rating in test_dist.index:
                diff = abs(train_dist[rating] - test_dist[rating])
                assert diff < 0.05, f"Rating {rating} distribution differs: {diff:.3f}"


class TestCVFolds:
    def test_correct_number_of_folds(self, small_df):
        folds = get_cv_folds(small_df, n_folds=5)
        assert len(folds) == 5

    def test_no_train_val_overlap(self, small_df):
        folds = get_cv_folds(small_df, n_folds=5)
        for train, val in folds:
            train_ids = set(train["ber_number"])
            val_ids = set(val["ber_number"])
            assert len(train_ids & val_ids) == 0, "Train and val must not overlap"

    def test_all_data_used(self, small_df):
        folds = get_cv_folds(small_df, n_folds=5)
        all_val_ids = set()
        for _, val in folds:
            all_val_ids.update(val["ber_number"])
        assert len(all_val_ids) == len(small_df)
