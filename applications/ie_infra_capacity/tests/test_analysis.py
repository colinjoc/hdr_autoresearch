"""Tests for the U-3 infrastructure capacity analysis pipeline."""
import os
import sys
import pytest
import pandas as pd
import numpy as np

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WW_PATH = os.path.join(PROJECT_DIR, "data", "raw", "wastewater_capacity.csv")
PLANNING_PATH = "/home/col/generalized_hdr_autoresearch/applications/ie_lapsed_permissions/data/raw/national_planning_points.csv"


class TestDataLoading:
    """Test that raw data loads correctly."""

    def test_wastewater_loads(self):
        ww = pd.read_csv(WW_PATH)
        assert len(ww) == 1063
        assert set(ww.columns) >= {"county", "settlement", "capacity", "project_planned"}

    def test_capacity_values_valid(self):
        ww = pd.read_csv(WW_PATH)
        assert set(ww["capacity"].unique()) == {"GREEN", "AMBER", "RED"}

    def test_all_29_counties_present(self):
        ww = pd.read_csv(WW_PATH)
        assert ww["county"].nunique() == 29

    def test_planning_data_loads(self):
        pp = pd.read_csv(PLANNING_PATH, encoding="utf-8-sig", low_memory=False, nrows=100)
        assert "Planning Authority" in pp.columns
        assert "NumResidentialUnits" in pp.columns


class TestCountyMapping:
    """Test county name mapping between wastewater and planning registers."""

    def test_county_mapping_covers_all_ww_counties(self):
        from analysis import COUNTY_MAP, load_wastewater
        ww = load_wastewater()
        for county in ww["county"].unique():
            assert county in COUNTY_MAP, f"Missing mapping for WW county: {county}"

    def test_county_mapping_covers_all_planning_authorities(self):
        from analysis import PA_TO_COUNTY
        pp = pd.read_csv(PLANNING_PATH, encoding="utf-8-sig", low_memory=False,
                         usecols=["Planning Authority"])
        real_pas = [p for p in pp["Planning Authority"].dropna().unique()
                    if "County Council" in p or "City Council" in p]
        for pa in real_pas:
            assert pa in PA_TO_COUNTY, f"Missing mapping for PA: {pa}"


class TestCountyAggregation:
    """Test county-level capacity aggregation."""

    def test_county_capacity_shares(self):
        from analysis import compute_county_capacity
        result = compute_county_capacity()
        assert "county" in result.columns
        assert "pct_red" in result.columns
        assert "pct_amber" in result.columns
        assert "pct_green" in result.columns
        # Shares should sum to ~100%
        total = result["pct_red"] + result["pct_amber"] + result["pct_green"]
        assert all(abs(total - 100.0) < 0.1)

    def test_national_capacity_shares(self):
        from analysis import load_wastewater
        ww = load_wastewater()
        n = len(ww)
        green_pct = (ww["capacity"] == "GREEN").sum() / n * 100
        assert abs(green_pct - 74.3) < 1.0  # ~74% GREEN nationally


class TestPlanningMerge:
    """Test linking planning applications to WWTP capacity status."""

    def test_merge_produces_results(self):
        from analysis import merge_planning_with_capacity
        merged = merge_planning_with_capacity()
        assert len(merged) > 0
        assert "capacity_status" in merged.columns or "county_pct_red" in merged.columns


class TestExperiments:
    """Test that experiments produce valid results."""

    def test_e00_baseline(self):
        from analysis import run_e00
        result = run_e00()
        assert "pct_red_or_amber" in result
        assert 0 < result["pct_red_or_amber"] < 100

    def test_e01_dublin(self):
        from analysis import run_e01_dublin
        result = run_e01_dublin()
        assert "dublin_settlements" in result
        assert result["dublin_settlements"] > 0

    def test_e09_hectares(self):
        from analysis import run_e09_hectares
        result = run_e09_hectares()
        assert "estimated_blocked_ha" in result
        assert result["estimated_blocked_ha"] > 0
