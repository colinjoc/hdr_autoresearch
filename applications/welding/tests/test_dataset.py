"""Tests for the welding dataset builder and loader.

Every test aims at a single invariant of the dataset. Run with
`pytest tests/test_dataset.py -v`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

DATA = PROJECT / "data" / "welding.csv"

EXPECTED_COLUMNS = {
    "process", "voltage_v", "current_a", "travel_mm_s", "efficiency",
    "thickness_mm", "preheat_c", "carbon_equiv", "base_material",
    "haz_width_mm", "hardness_hv", "cooling_t85_s", "uts_mpa",
}


@pytest.fixture(scope="module")
def welding_df() -> pd.DataFrame:
    assert DATA.exists(), f"run build_dataset.py first; missing {DATA}"
    return pd.read_csv(DATA)


def test_dataset_file_exists():
    assert DATA.exists()


def test_required_columns_present(welding_df):
    missing = EXPECTED_COLUMNS - set(welding_df.columns)
    assert not missing, f"missing columns: {missing}"


def test_nonzero_row_count(welding_df):
    assert len(welding_df) > 500, "dataset too small for 5-fold CV"


def test_all_three_process_families(welding_df):
    processes = set(welding_df["process"].unique())
    assert {"GMAW", "GTAW", "FSW"} <= processes


def test_no_missing_values(welding_df):
    assert welding_df.isna().sum().sum() == 0


def test_parameter_ranges_physical(welding_df):
    steel = welding_df[welding_df["process"].isin(["GMAW", "GTAW"])]
    assert steel["voltage_v"].between(8, 40).all()
    assert steel["current_a"].between(30, 350).all()
    assert steel["travel_mm_s"].between(0.5, 20).all()


def test_haz_width_positive(welding_df):
    assert (welding_df["haz_width_mm"] > 0).all()


def test_hardness_in_reasonable_hv_band(welding_df):
    assert (welding_df["hardness_hv"] > 50).all()
    assert (welding_df["hardness_hv"] < 600).all()


def test_heat_input_correlates_with_haz(welding_df):
    """Sanity check: Rosenthal physics implies HI↑ → HAZ width↑.

    Corr on the arc-welding subset must exceed 0.5 — a loose bound that
    still rules out random / shuffled targets.
    """
    steel = welding_df[welding_df["process"].isin(["GMAW", "GTAW"])].copy()
    steel["hi"] = (steel["efficiency"] * steel["voltage_v"]
                   * steel["current_a"] / (steel["travel_mm_s"] * 1000.0))
    corr = steel[["hi", "haz_width_mm"]].corr().iloc[0, 1]
    assert corr > 0.5, f"HI/HAZ correlation {corr:.3f} unexpectedly low"
