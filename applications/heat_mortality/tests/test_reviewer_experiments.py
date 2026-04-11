"""Tests for reviewer-requested experiments (RX02, RX08).

Runs on the synthetic panel from test_baseline.py fixtures.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
APP = HERE.parent
sys.path.insert(0, str(APP))

from data_loaders import compute_expected_baseline  # noqa: E402
from model import (  # noqa: E402
    add_features,
    build_clean_dataset,
    label_lethal_heatwave,
)


# ---------------------------------------------------------------- fixtures

def _synth_master(cities=("phoenix", "paris", "london", "new_york"),
                  start_year: int = 2015, end_year: int = 2023,
                  seed: int = 0) -> pd.DataFrame:
    """Synthetic (city x week) panel with a heat-driven excess signal."""
    rng = np.random.default_rng(seed)
    rows = []
    city_meta = {
        "phoenix": (33.45, -112.07, 1600, 20.0, 6.0),
        "paris": (48.86, 2.35, 900, 14.0, 5.0),
        "london": (51.51, -0.13, 1100, 12.0, 4.0),
        "new_york": (40.78, -73.97, 1800, 16.0, 5.0),
    }
    for city in cities:
        lat, lon, base_deaths, t_mean, t_ampl = city_meta[city]
        for year in range(start_year, end_year + 1):
            for w in range(1, 53):
                try:
                    wk_start = pd.to_datetime(f"{year}-W{w:02d}-1",
                                              format="%G-W%V-%u")
                except ValueError:
                    continue
                season = np.cos(2 * np.pi * (w - 28) / 52.0)
                t = t_mean + t_ampl * season + rng.normal(0, 1.5)
                tmin = t - 6.0 + rng.normal(0, 0.8)
                tmax = t + 6.0 + rng.normal(0, 0.8)
                tdew = t - 3.0 + rng.normal(0, 0.8)
                tw = t - 2.0 + 0.3 * rng.normal()
                tw_night = t - 3.5 + 0.3 * rng.normal()
                heat_excess = max(0.0, t - 25.0) * 15.0
                winter_excess = max(0.0, 8.0 - t) * 2.0
                noise = rng.normal(0, base_deaths * 0.035)
                deaths = base_deaths + heat_excess + winter_excess + noise
                consec = int(max(0, (t - 28.0) * 0.8 + rng.normal(0, 0.5)))
                rows.append({
                    "city": city, "country": "US" if city in ("phoenix", "new_york") else "EU",
                    "iso_week_start": wk_start,
                    "iso_year_week": f"{year}-W{w:02d}",
                    "deaths_all_cause": float(deaths),
                    "age_group": "all",
                    "tmax_c_mean": float(tmax),
                    "tmin_c_mean": float(tmin),
                    "tavg_c": float(t),
                    "tdew_c": float(tdew),
                    "tw_c_mean": float(tw),
                    "tw_c_max": float(tw + 1.5),
                    "tw_night_c_mean": float(tw_night),
                    "tw_night_c_max": float(tw_night + 1.0),
                    "tw_anomaly_c": 0.0,
                    "consecutive_days_above_p95": consec,
                    "heat_dome_flag": consec >= 3,
                    "lat": lat, "lon": lon,
                })
    df = pd.DataFrame(rows)
    df = compute_expected_baseline(df, baseline_years=5,
                                   exclude_pandemic=True, group_cols=("city",))
    return df


@pytest.fixture(scope="module")
def synth_panel():
    """Cleaned + featured synthetic panel."""
    master = _synth_master()
    clean = build_clean_dataset(master)
    feat = add_features(clean)
    return feat.reset_index(drop=True)


# ---------------------------------------------------------------- tests

def test_case_crossover_matching(synth_panel):
    """Case-crossover matching produces valid matched sets."""
    panel = synth_panel
    y_bin = label_lethal_heatwave(panel)
    case_idx = np.where(y_bin == 1)[0]

    if len(case_idx) == 0:
        pytest.skip("No lethal weeks in synthetic panel")

    wk = pd.to_datetime(panel["iso_week_start"])
    panel_month = wk.dt.month.values
    panel_year = wk.dt.year.values
    panel_city = panel["city"].values

    rng = np.random.default_rng(42)
    matched_sets = []
    for ci in case_idx:
        city = panel_city[ci]
        month = panel_month[ci]
        year = panel_year[ci]
        control_mask = (
            (panel_city == city) &
            (panel_month == month) &
            (panel_year != year) &
            (y_bin == 0)
        )
        control_candidates = np.where(control_mask)[0]
        if len(control_candidates) >= 2:
            n_select = min(4, len(control_candidates))
            selected = rng.choice(control_candidates, size=n_select, replace=False)
            matched_sets.append({"case": ci, "controls": selected})

    # At least some matching should succeed
    assert len(matched_sets) > 0, "No matched sets created"

    # Verify matching constraints
    for ms in matched_sets:
        ci = ms["case"]
        for ctrl_i in ms["controls"]:
            # Same city
            assert panel_city[ci] == panel_city[ctrl_i], "Mismatched city"
            # Same month
            assert panel_month[ci] == panel_month[ctrl_i], "Mismatched month"
            # Different year
            assert panel_year[ci] != panel_year[ctrl_i], "Same year"
            # Control is not lethal
            assert y_bin[ctrl_i] == 0, "Control is lethal"


def test_permutation_changes_feature(synth_panel):
    """Within-city shuffle actually changes the feature column."""
    panel = synth_panel
    city_vals = panel["city"].values
    feat_vals = panel["tw_night_c_max"].astype("float64").values.copy()

    rng = np.random.default_rng(42)
    shuffled = feat_vals.copy()
    for city in np.unique(city_vals):
        idx = np.where(city_vals == city)[0]
        if len(idx) > 1:
            portion = shuffled[idx].copy()
            rng.shuffle(portion)
            shuffled[idx] = portion

    n_diff = (feat_vals != shuffled).sum()
    # Most values should be different after within-city shuffle
    assert n_diff > len(feat_vals) * 0.5, \
        f"Too few values changed: {n_diff}/{len(feat_vals)}"


def test_decoupled_label_more_positives(synth_panel):
    """Decoupled label (p_score >= 0.10 only) has more positives than coupled."""
    from model import BINARY_P_SCORE_THRESHOLD
    panel = synth_panel

    y_coupled = label_lethal_heatwave(panel)
    p = panel["p_score"].to_numpy(dtype="float64")
    y_decoupled = (np.where(np.isnan(p), 0.0, p) >= BINARY_P_SCORE_THRESHOLD).astype("int64")

    # Decoupled should have >= coupled positives (it relaxes a constraint)
    assert y_decoupled.sum() >= y_coupled.sum(), \
        f"Decoupled ({y_decoupled.sum()}) should have >= coupled ({y_coupled.sum()}) positives"
