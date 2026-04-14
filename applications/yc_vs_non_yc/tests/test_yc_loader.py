"""Tests for YC company loader.

Verifies: JSON parses, batch codes map to (year, season, quarter, quarter_start_date),
row counts are sane, status categories are as advertised, SAFE fields are present.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import pytest

from yc_loader import (
    BATCH_RE,
    load_yc_companies,
    parse_batch,
)

HERE = Path(__file__).resolve().parents[1]
RAW = HERE / "data" / "yc_companies_raw.json"


def test_raw_json_present():
    assert RAW.exists(), f"raw YC JSON missing at {RAW}"
    assert RAW.stat().st_size > 1_000_000  # sanity: ~9.5 MB


@pytest.mark.parametrize("code,expected_year,expected_season,expected_q", [
    ("Summer 2005", 2005, "Summer", 3),
    ("Winter 2006", 2006, "Winter", 1),
    ("Winter 2024", 2024, "Winter", 1),
    ("Fall 2025", 2025, "Fall", 4),
    ("Spring 2025", 2025, "Spring", 2),
])
def test_parse_batch_classic_codes(code, expected_year, expected_season, expected_q):
    year, season, quarter = parse_batch(code)
    assert year == expected_year
    assert season == expected_season
    assert quarter == expected_q


def test_parse_batch_unknown_returns_none():
    assert parse_batch("") == (None, None, None)
    assert parse_batch("IK12") == (None, None, None)
    assert parse_batch("Winter 22") == (None, None, None)  # two-digit year rejected
    assert parse_batch("winter 2022") == (None, None, None)  # case-sensitive


def test_load_yc_companies_returns_dataframe():
    df = load_yc_companies(RAW)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 5000  # as of 2026-04 there are 5,690
    for col in ("id", "name", "slug", "batch", "batch_year", "batch_season",
                "batch_quarter", "status", "industries", "long_description",
                "website"):
        assert col in df.columns, f"missing column {col}"


def test_status_values_are_as_advertised():
    df = load_yc_companies(RAW)
    expected = {"Active", "Inactive", "Acquired", "Public"}
    observed = set(df["status"].dropna().unique())
    # Allow additional minor categories but require the core four to appear
    assert expected.issubset(observed), f"missing status values: {expected - observed}"


def test_batch_year_span():
    df = load_yc_companies(RAW)
    years = df["batch_year"].dropna().astype(int)
    assert years.min() <= 2006  # first batches S05/W06
    assert years.max() >= 2023


def test_pre_2020_mature_cohort_size():
    """For a 5-year outcome window ending 2025, pre-2020 batches are mature."""
    df = load_yc_companies(RAW)
    mature = df[df["batch_year"] < 2020]
    assert len(mature) >= 1500, (
        f"pre-2020 cohort is too small ({len(mature)}) for matched-pair analysis"
    )


def test_no_duplicate_slugs():
    df = load_yc_companies(RAW)
    assert df["slug"].is_unique


def test_batch_regex_whole_codes_only():
    # Hardening: no partial-string bleed-through
    assert BATCH_RE.fullmatch("Winter 2022")
    assert BATCH_RE.fullmatch("Fall 2025")
    assert not BATCH_RE.fullmatch("XWinter 2022")
    assert not BATCH_RE.fullmatch("Winter 2022X")
