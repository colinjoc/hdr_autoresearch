"""Tests for data loading and feature engineering pipeline.

The data pipeline must:
1. Load EPA radon grid map (868 10km grid squares with % homes > 200 Bq/m3)
2. Load GSI bedrock geology and spatially join to grid squares
3. Load EPA subsoils and spatially join to grid squares
4. Load EPA county boundaries and assign counties for spatial CV
5. Load county-level radon measurements for county features
6. Produce a clean DataFrame ready for modelling
"""
import os
import sys
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Skip all tests if data not downloaded
pytestmark = pytest.mark.skipif(
    not os.path.exists(os.path.join(DATA_DIR, "epa_radon", "radon_grid_map.geojson")),
    reason="Data not downloaded yet"
)


class TestRadonGridLoad:
    """Test loading the EPA 10km radon grid map."""

    def test_load_returns_geodataframe(self):
        from data_loaders import load_radon_grid
        gdf = load_radon_grid()
        assert hasattr(gdf, "geometry"), "Should return GeoDataFrame"

    def test_load_has_percent_column(self):
        from data_loaders import load_radon_grid
        gdf = load_radon_grid()
        assert "pct_above_rl" in gdf.columns, "Must have pct_above_rl (% homes > 200 Bq/m3)"

    def test_load_filters_invalid_percent(self):
        """The raw data has -999 for missing. These must be filtered."""
        from data_loaders import load_radon_grid
        gdf = load_radon_grid()
        assert (gdf["pct_above_rl"] >= 0).all(), "No negative percentages after cleaning"
        assert (gdf["pct_above_rl"] <= 100).all(), "No values > 100%"

    def test_load_has_centroid_coords(self):
        from data_loaders import load_radon_grid
        gdf = load_radon_grid()
        assert "centroid_x" in gdf.columns
        assert "centroid_y" in gdf.columns

    def test_grid_count_reasonable(self):
        """Should have ~800+ grid squares after filtering."""
        from data_loaders import load_radon_grid
        gdf = load_radon_grid()
        assert len(gdf) > 700, f"Too few grid squares: {len(gdf)}"
        assert len(gdf) < 1000, f"Too many grid squares: {len(gdf)}"


class TestBedrockJoin:
    """Test spatial join of bedrock geology to radon grid."""

    def test_bedrock_features_exist(self):
        from data_loaders import load_radon_grid, join_bedrock_features
        gdf = load_radon_grid()
        result = join_bedrock_features(gdf)
        # Should have columns for dominant bedrock type and age
        assert "bedrock_dominant_unit" in result.columns
        assert "bedrock_dominant_age" in result.columns

    def test_bedrock_coverage(self):
        """Most grid squares should have bedrock info."""
        from data_loaders import load_radon_grid, join_bedrock_features
        gdf = load_radon_grid()
        result = join_bedrock_features(gdf)
        coverage = result["bedrock_dominant_unit"].notna().mean()
        assert coverage > 0.8, f"Bedrock coverage too low: {coverage:.2%}"


class TestSubsoilJoin:
    """Test spatial join of subsoil/quaternary data to radon grid."""

    def test_subsoil_features_exist(self):
        from data_loaders import load_radon_grid, join_subsoil_features
        gdf = load_radon_grid()
        result = join_subsoil_features(gdf)
        assert "subsoil_dominant_category" in result.columns

    def test_subsoil_coverage(self):
        from data_loaders import load_radon_grid, join_subsoil_features
        gdf = load_radon_grid()
        result = join_subsoil_features(gdf)
        coverage = result["subsoil_dominant_category"].notna().mean()
        assert coverage > 0.5, f"Subsoil coverage too low: {coverage:.2%}"


class TestCountyAssignment:
    """Test assignment of counties for spatial CV."""

    def test_county_assigned(self):
        from data_loaders import load_radon_grid, assign_counties
        gdf = load_radon_grid()
        result = assign_counties(gdf)
        assert "county" in result.columns

    def test_county_coverage(self):
        from data_loaders import load_radon_grid, assign_counties
        gdf = load_radon_grid()
        result = assign_counties(gdf)
        coverage = result["county"].notna().mean()
        assert coverage > 0.8, f"County coverage too low: {coverage:.2%}"

    def test_multiple_counties(self):
        from data_loaders import load_radon_grid, assign_counties
        gdf = load_radon_grid()
        result = assign_counties(gdf)
        n_counties = result["county"].nunique()
        assert n_counties >= 20, f"Too few counties: {n_counties}"


class TestCountyRadonStats:
    """Test county-level radon measurement statistics."""

    def test_county_stats_loaded(self):
        from data_loaders import load_county_radon_stats
        df = load_county_radon_stats()
        assert "county" in df.columns
        assert "homes_measured" in df.columns
        assert "pct_above_rl" in df.columns

    def test_county_count(self):
        from data_loaders import load_county_radon_stats
        df = load_county_radon_stats()
        assert len(df) >= 26, f"Should have 26+ ROI counties, got {len(df)}"


class TestFullDataset:
    """Test the complete feature engineering pipeline."""

    def test_build_dataset_shape(self):
        from data_loaders import build_dataset
        X, y, groups = build_dataset()
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert len(X) == len(y)
        assert len(X) == len(groups)

    def test_no_target_leakage(self):
        """Target column must not appear in features."""
        from data_loaders import build_dataset
        X, y, groups = build_dataset()
        assert "pct_above_rl" not in X.columns
        assert "PERCENT_" not in X.columns

    def test_target_is_numeric(self):
        from data_loaders import build_dataset
        X, y, groups = build_dataset()
        assert y.dtype in [np.float64, np.float32, float]

    def test_groups_are_counties(self):
        from data_loaders import build_dataset
        X, y, groups = build_dataset()
        assert groups.nunique() >= 15, "Groups should be county-level"

    def test_no_all_nan_features(self):
        from data_loaders import build_dataset
        X, y, groups = build_dataset()
        all_nan = X.isna().all()
        assert not all_nan.any(), f"All-NaN features: {list(all_nan[all_nan].index)}"
