"""Tests for data loading and baseline computations."""
import sys
sys.path.insert(0, "/home/col/generalized_hdr_autoresearch/applications/ie_zoned_land_conversion")

import pytest
import pandas as pd
import numpy as np
from load_data import (
    load_bhq01, load_rzlpa02, load_hpa09, load_planning_register,
    get_planning_by_la_year, GOODBODY, LA_REGION, DUBLIN_LAS,
    LA_POPULATION_2022
)


class TestDataLoading:
    def test_bhq01_loads(self):
        df = load_bhq01()
        assert len(df) > 0
        assert "value" in df.columns

    def test_rzlpa02_loads(self):
        df = load_rzlpa02()
        assert len(df) > 0
        assert "value" in df.columns

    def test_hpa09_loads(self):
        df = load_hpa09()
        assert len(df) > 0
        assert "value" in df.columns

    def test_planning_register_loads(self):
        df = load_planning_register()
        assert len(df) > 400000, "Expected ~491k rows"
        assert "ReceivedYear" in df.columns
        assert "is_residential" in df.columns
        assert "Region" in df.columns

    def test_planning_register_has_residential(self):
        df = load_planning_register()
        n_res = df["is_residential"].sum()
        assert n_res > 200000, f"Expected >200k residential, got {n_res}"

    def test_la_region_covers_all(self):
        df = load_planning_register()
        unmapped = df[df["Region"].isna()]["Planning Authority"].unique()
        # Allow some unmapped LAs (historic/merged)
        assert len(unmapped) < 5, f"Unmapped LAs: {unmapped}"

    def test_aggregation_shape(self):
        df = load_planning_register()
        agg = get_planning_by_la_year(df)
        assert len(agg) > 100
        assert "residential_permission_applications" in agg.columns
        assert "approval_rate" in agg.columns


class TestGoodbodyConstants:
    def test_total_zoned_ha(self):
        assert GOODBODY["total_zoned_ha"] == 7911

    def test_regional_sum(self):
        total = GOODBODY["east_midlands_ha"] + GOODBODY["southern_ha"] + GOODBODY["north_western_ha"]
        # Allow ~2% rounding tolerance
        assert abs(total - GOODBODY["total_zoned_ha"]) < 200

    def test_density(self):
        # 417k units / 7911 ha ~ 53
        computed = GOODBODY["potential_units"] / GOODBODY["total_zoned_ha"]
        assert abs(computed - GOODBODY["density_units_per_ha"]) < 1

    def test_zoned_decline(self):
        # 17434 -> 7911 is ~55% decline
        decline = 1 - GOODBODY["zoned_2024_ha"] / GOODBODY["zoned_2014_ha"]
        assert 0.5 < decline < 0.6


class TestBaselineMetric:
    """Test E00: national application intensity = residential apps per hectare of zoned land per year."""

    def test_e00_computable(self):
        df = load_planning_register()
        agg = get_planning_by_la_year(df, year_range=(2018, 2024))
        annual = agg.groupby("ReceivedYear")["residential_permission_applications"].sum()
        mean_annual = annual.mean()
        intensity = mean_annual / GOODBODY["total_zoned_ha"]
        # Should be roughly 2-5 applications per hectare per year (order of magnitude)
        assert 1 < intensity < 10, f"Intensity {intensity:.2f} outside expected range"

    def test_national_apps_per_year(self):
        df = load_planning_register()
        agg = get_planning_by_la_year(df, year_range=(2018, 2024))
        annual = agg.groupby("ReceivedYear")["residential_permission_applications"].sum()
        mean_annual = annual.mean()
        # ~20-40k per year based on data profile
        assert 10000 < mean_annual < 50000, f"Mean annual res perm apps: {mean_annual:.0f}"
