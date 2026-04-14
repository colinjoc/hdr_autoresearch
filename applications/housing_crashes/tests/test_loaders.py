"""Tests for housing-crash project data loaders."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from loaders import (
    crosswalk_zillow_to_cbsa,
    load_mortgage_30yr_monthly,
    load_realtor,
    load_zhvi_long,
    normalize_metro_name,
)


HERE = Path(__file__).resolve().parents[1]


def test_raw_zhvi_exists_and_nonempty():
    p = HERE / "data" / "zillow_zhvi_metro.csv"
    assert p.exists() and p.stat().st_size > 1_000_000


def test_raw_realtor_exists_and_nonempty():
    p = HERE / "data" / "realtor_inventory_metro.csv"
    assert p.exists() and p.stat().st_size > 10_000_000


def test_zhvi_long_structure():
    df = load_zhvi_long()
    for c in ("zillow_region_id", "metro_name", "state", "month", "zhvi"):
        assert c in df.columns
    assert len(df) > 200_000  # 895 metros × 300+ months ≈ 270k rows
    assert df["zhvi"].notna().all()
    assert df["month"].dtype.kind == "M"
    # No US aggregate row
    assert (df["metro_name"] != "United States").all()


def test_zhvi_month_range():
    df = load_zhvi_long()
    assert df["month"].min() <= pd.Timestamp("2000-01-01")
    assert df["month"].max() >= pd.Timestamp("2024-12-01")


def test_realtor_structure():
    df = load_realtor()
    for c in ("month", "cbsa_code", "cbsa_title",
              "median_listing_price", "active_listing_count",
              "median_days_on_market"):
        assert c in df.columns
    assert len(df) > 100_000
    assert df["month"].min() <= pd.Timestamp("2016-08-01")
    assert df["cbsa_code"].dtype == object  # str for join safety


def test_mortgage_monthly_structure():
    df = load_mortgage_30yr_monthly()
    assert list(df.columns) == ["month", "mortgage_30yr"]
    assert len(df) >= 300  # 25+ years of monthly
    assert df["mortgage_30yr"].between(1, 20).all()


@pytest.mark.parametrize("raw,expected", [
    ("New York, NY", "new york"),
    ("Los Angeles, CA", "los angeles"),
    ("Dallas-Fort Worth-Arlington, TX", "dallas fort worth arlington"),
    ("Raleigh, NC", "raleigh"),
    ("Kansas City, MO-KS", "kansas city"),
    ("  Boston  ", "boston"),
])
def test_normalize_metro_name(raw, expected):
    assert normalize_metro_name(raw) == expected


def test_crosswalk_coverage_meaningful():
    zhvi = load_zhvi_long()
    realtor = load_realtor()
    xw = crosswalk_zillow_to_cbsa(zhvi, realtor)
    # 100+ metro matches is the minimum viable overlap
    assert len(xw) >= 100
    # Check uniqueness: each zillow ID maps to exactly one CBSA and vice versa
    assert xw["zillow_region_id"].is_unique
    assert xw["cbsa_code"].is_unique
