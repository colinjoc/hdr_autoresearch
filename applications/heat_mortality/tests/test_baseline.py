"""Tests for the Phase 0.5 baseline + Phase 1 tournament harness.

All tests run on a small in-memory synthetic panel (no network). They check
pipeline logic, target definitions, feature columns, and reproducibility.

Run from the application root:
    python -m pytest -x --tb=short tests/test_baseline.py
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
from evaluate import cross_validate  # noqa: E402
from model import (  # noqa: E402
    BASELINE_FEATURES,
    BASELINE_FEATURES_WITH_CITY,
    CITIES_FOR_BASELINE,
    add_features,
    build_clean_dataset,
    label_lethal_heatwave,
    make_baseline_xgb,
)


# ---------------------------------------------------------------- fixtures

def _synth_master(cities=("phoenix", "paris", "london", "new_york"),
                  start_year: int = 2015, end_year: int = 2023,
                  seed: int = 0) -> pd.DataFrame:
    """Synthetic (city × week) panel with a heat-driven excess signal.

    Layout matches what ``data_loaders.build_master_dataset`` emits:
    city, country, iso_week_start, iso_year_week, deaths_all_cause,
    age_group, expected_baseline, excess_deaths, p_score, tmax_c_mean,
    tmin_c_mean, tavg_c, tdew_c, tw_c_mean, tw_c_max, tw_night_c_mean,
    tw_night_c_max, tw_anomaly_c, consecutive_days_above_p95,
    heat_dome_flag, lat, lon.
    """
    rng = np.random.default_rng(seed)
    rows = []
    city_meta = {
        "phoenix": (33.45, -112.07, 1600, 20.0, 6.0),
        "paris": (48.86, 2.35, 900, 14.0, 5.0),
        "london": (51.51, -0.13, 1100, 12.0, 4.0),
        "new_york": (40.78, -73.97, 1800, 16.0, 5.0),
    }
    weeks_per_year = 52
    for city in cities:
        lat, lon, base_deaths, t_mean, t_ampl = city_meta[city]
        for year in range(start_year, end_year + 1):
            for w in range(1, weeks_per_year + 1):
                # Monday of ISO week `w`. Use %G-W%V-%u.
                try:
                    wk_start = pd.to_datetime(f"{year}-W{w:02d}-1",
                                              format="%G-W%V-%u")
                except ValueError:
                    continue

                # Seasonal temperature: peak mid-summer (week 28).
                season = np.cos(2 * np.pi * (w - 28) / 52.0)
                t = t_mean + t_ampl * season + rng.normal(0, 1.5)
                tmin = t - 6.0 + rng.normal(0, 0.8)
                tmax = t + 6.0 + rng.normal(0, 0.8)
                tdew = t - 3.0 + rng.normal(0, 0.8)
                tw = t - 2.0 + 0.3 * rng.normal()
                tw_night = t - 3.5 + 0.3 * rng.normal()

                # Deaths: base + heat excess above 25C + winter floor, noise.
                heat_excess = max(0.0, t - 25.0) * 15.0
                winter_excess = max(0.0, 8.0 - t) * 2.0
                noise = rng.normal(0, base_deaths * 0.035)
                deaths = base_deaths + heat_excess + winter_excess + noise

                consec = int(max(0, (t - 28.0) * 0.8 + rng.normal(0, 0.5)))
                rows.append({
                    "city": city,
                    "country": "US" if city in ("phoenix", "new_york") else "EU",
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
                    "lat": lat,
                    "lon": lon,
                })

    df = pd.DataFrame(rows)
    df = compute_expected_baseline(df, baseline_years=5,
                                   exclude_pandemic=True, group_cols=("city",))
    return df


@pytest.fixture(scope="module")
def synth_master() -> pd.DataFrame:
    return _synth_master()


@pytest.fixture(scope="module")
def synth_clean(synth_master) -> pd.DataFrame:
    return build_clean_dataset(synth_master)


# ---------------------------------------------------------------- tests

def test_master_dataset_shape(synth_master):
    """A small master dataset can be built and holds the target schema."""
    df = synth_master
    assert len(df) > 0
    for col in ("city", "iso_week_start", "deaths_all_cause",
                "expected_baseline", "excess_deaths", "p_score",
                "tmax_c_mean", "tw_c_mean", "lat"):
        assert col in df.columns, f"missing column: {col}"
    # Expected baseline computable for at least some rows (need 5y history).
    assert df["expected_baseline"].notna().sum() > 0
    # Every city in the synth list is present.
    assert df["city"].nunique() == 4


def test_add_features_shape(synth_clean):
    """add_features produces every BASELINE_FEATURES column on a cleaned panel."""
    df = synth_clean
    assert len(df) > 0, "cleaned dataset should not be empty"
    feat = add_features(df)
    for col in BASELINE_FEATURES:
        assert col in feat.columns, f"missing feature column: {col}"
    # Cyclic encodings live on the unit circle.
    r2 = feat["iso_month_sin"].values ** 2 + feat["iso_month_cos"].values ** 2
    assert np.allclose(r2, 1.0, atol=1e-9)
    # log_population finite.
    assert np.isfinite(feat["log_population"].values).all()
    # City one-hot sums to 1 for rows whose city is in the baseline list.
    present = feat["city"].isin(CITIES_FOR_BASELINE)
    assert present.all(), "synthetic panel should use baseline cities"
    city_cols = [f"city_{c}" for c in CITIES_FOR_BASELINE]
    sums = feat.loc[present, city_cols].sum(axis=1).values
    assert np.allclose(sums, 1.0)
    # No NaNs in the modelling matrix.
    X = feat[BASELINE_FEATURES_WITH_CITY].astype("float64").values
    assert np.isfinite(X).all(), "feature matrix has NaN/Inf"


def test_baseline_reproducibility(synth_clean):
    """Running the baseline twice with the same seed produces identical MAE."""
    m1 = cross_validate(synth_clean, make_baseline_xgb, n_splits=3,
                        seed=42, verbose=False)
    m2 = cross_validate(synth_clean, make_baseline_xgb, n_splits=3,
                        seed=42, verbose=False)
    assert m1["mae_deaths"] == pytest.approx(m2["mae_deaths"], rel=0, abs=1e-6), \
        f"reproducibility broken: {m1['mae_deaths']} vs {m2['mae_deaths']}"
    assert m1["r2"] == pytest.approx(m2["r2"], rel=0, abs=1e-6)


def test_target_definitions(synth_master):
    """excess_deaths = deaths - expected; p_score = excess / expected."""
    df = synth_master.dropna(subset=["expected_baseline", "excess_deaths",
                                     "p_score"]).copy()
    assert len(df) > 0
    # excess_deaths definition.
    expected_excess = df["deaths_all_cause"] - df["expected_baseline"]
    np.testing.assert_allclose(df["excess_deaths"].values,
                                expected_excess.values,
                                rtol=1e-10, atol=1e-10)
    # p_score definition.
    pos = df["expected_baseline"] > 0
    expected_p = df.loc[pos, "excess_deaths"] / df.loc[pos, "expected_baseline"]
    np.testing.assert_allclose(df.loc[pos, "p_score"].values,
                                expected_p.values,
                                rtol=1e-10, atol=1e-10)
    # The lethal-heatwave label uses p_score + streak — confirm it's a subset
    # of the p_score ≥ 0.10 rows.
    cleaned = build_clean_dataset(synth_master)
    if len(cleaned) > 0:
        feat = add_features(cleaned)
        lab = label_lethal_heatwave(feat)
        high_p = (feat["p_score"].values >= 0.10)
        assert (lab[~high_p] == 0).all(), \
            "lethal label fired on rows with p_score < 0.10"
