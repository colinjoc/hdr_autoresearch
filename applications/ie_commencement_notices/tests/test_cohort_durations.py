"""TDD sanity tests for the cohort dataset.

Asserts duration invariants: permission_date <= commencement_date <= completion_date.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import analysis  # noqa: E402


@pytest.fixture(scope="module")
def df():
    return analysis.load_cohort()


def test_has_rows(df):
    assert len(df) > 100_000


def test_residential_filter(df):
    use = df["CN_Proposed_use_of_building"].astype(str)
    assert use.str.contains("residential").all()


def test_duration_nonneg_on_complete(df):
    complete = analysis.cohort_complete_timeline(df)
    d = complete["duration_perm_to_ccc_days"]
    assert (d > 0).all(), "duration permission-to-CCC must be positive on complete cohort"
    # not-trivially-tiny either
    assert d.median() > 30


def test_permission_le_commencement(df):
    sub = df.dropna(subset=["CN_Date_Granted", "CN_Commencement_Date"])
    # Allow small negatives from clerical errors but not structurally
    neg = (sub["CN_Commencement_Date"] - sub["CN_Date_Granted"]).dt.days < 0
    assert neg.mean() < 0.02, f"more than 2% of rows have commencement before grant: {neg.mean():.2%}"


def test_commencement_le_ccc(df):
    sub = df.dropna(subset=["CN_Commencement_Date", "CCC_Date_Validated"])
    neg = (sub["CCC_Date_Validated"] - sub["CN_Commencement_Date"]).dt.days < 0
    assert neg.mean() < 0.02, f"more than 2% of rows have CCC before commencement: {neg.mean():.2%}"


def test_cohort_sizes_reasonable(df):
    pc = analysis.cohort_for_perm_to_comm(df)
    cc = analysis.cohort_for_comm_to_ccc(df)
    assert len(pc) > 100_000
    assert len(cc) > 100_000


def test_apartment_flag_sanity(df):
    # Apartments are a non-trivial but minority class of BCMS residential rows
    # (one-off dwellings dominate by count; apartments dominate by unit-weight).
    assert 0.02 < df["apartment_flag"].mean() < 0.5
