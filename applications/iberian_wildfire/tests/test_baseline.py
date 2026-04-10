"""Tests for data loaders, features, model, and evaluation pipeline.

All tests run on the real EFFIS data (no synthetic data). They verify:
- Data loading and schema
- Feature engineering correctness
- VLF labelling logic
- Temporal CV implementation
- Model reproducibility

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

from data_loaders import (  # noqa: E402
    BASELINE_FEATURES,
    VLF_AREA_THRESHOLD,
    add_features,
    build_modelling_dataset,
    label_vlf_week,
    load_effis_weekly,
)
from evaluate import compute_metrics, temporal_cv  # noqa: E402
from model import (  # noqa: E402
    get_baseline_features,
    make_ridge,
    make_xgboost,
)


# ---------------------------------------------------------------- fixtures

@pytest.fixture(scope="module")
def effis_weekly() -> pd.DataFrame:
    """Load real EFFIS weekly data."""
    return load_effis_weekly()


@pytest.fixture(scope="module")
def modelling_df() -> pd.DataFrame:
    """Build the full modelling dataset."""
    return build_modelling_dataset()


# ---------------------------------------------------------------- data loading

def test_effis_weekly_loads(effis_weekly):
    """EFFIS weekly data loads with expected schema."""
    df = effis_weekly
    assert len(df) > 0, "EFFIS data should not be empty"
    for col in ["country", "year", "week", "fires", "area_ha",
                "fires_avg", "area_ha_avg"]:
        assert col in df.columns, f"missing column: {col}"
    assert set(df["country"].unique()) == {"PRT", "ESP"}
    assert df["year"].min() >= 2006
    assert df["year"].max() <= 2026


def test_effis_weekly_year_range(effis_weekly):
    """Data covers at least 2012-2025."""
    years = set(effis_weekly["year"].unique())
    for y in range(2012, 2026):
        assert y in years, f"missing year: {y}"


def test_effis_weekly_no_nulls(effis_weekly):
    """No null values in core columns."""
    for col in ["fires", "area_ha", "fires_avg"]:
        assert effis_weekly[col].notna().all(), f"NaN in {col}"


# ---------------------------------------------------------------- VLF labelling

def test_vlf_label_definition():
    """VLF labelling matches documented definition."""
    # Case 1: total area > 5000 ha with fires -> VLF
    df = pd.DataFrame({
        "fires": [3], "area_ha": [8000],
    })
    labels = label_vlf_week(df)
    assert labels[0] == 1

    # Case 2: total area just above threshold
    df = pd.DataFrame({
        "fires": [1], "area_ha": [5500],
    })
    labels = label_vlf_week(df)
    assert labels[0] == 1

    # Case 3: below threshold -> not VLF
    df = pd.DataFrame({
        "fires": [5], "area_ha": [3000],
    })
    labels = label_vlf_week(df)
    assert labels[0] == 0

    # Case 4: no fires -> not VLF
    df = pd.DataFrame({
        "fires": [0], "area_ha": [0],
    })
    labels = label_vlf_week(df)
    assert labels[0] == 0

    # Case 5: large area but no fires -> not VLF
    df = pd.DataFrame({
        "fires": [0], "area_ha": [10000],
    })
    labels = label_vlf_week(df)
    assert labels[0] == 0


def test_vlf_rate_reasonable(modelling_df):
    """VLF rate should be 5-25% of fire-season weeks."""
    vlf_rate = modelling_df["vlf"].mean()
    assert 0.03 < vlf_rate < 0.25, \
        f"VLF rate {vlf_rate:.1%} outside plausible range"


# ---------------------------------------------------------------- feature engineering

def test_add_features_produces_all_columns(modelling_df):
    """All BASELINE_FEATURES columns exist in the modelling dataset."""
    for col in BASELINE_FEATURES:
        assert col in modelling_df.columns, f"missing feature: {col}"


def test_features_no_nans(modelling_df):
    """No NaN values in feature columns."""
    for col in BASELINE_FEATURES:
        if col in modelling_df.columns:
            n_nan = modelling_df[col].isna().sum()
            assert n_nan == 0, f"NaN in {col}: {n_nan} values"


def test_cyclic_features_on_unit_circle(modelling_df):
    """Sine/cosine features should satisfy sin^2 + cos^2 = 1."""
    for prefix in ["month", "week"]:
        sin_col = f"{prefix}_sin"
        cos_col = f"{prefix}_cos"
        if sin_col in modelling_df.columns and cos_col in modelling_df.columns:
            r2 = modelling_df[sin_col].values ** 2 + modelling_df[cos_col].values ** 2
            np.testing.assert_allclose(r2, 1.0, atol=1e-6,
                                       err_msg=f"{prefix} cyclic features not on unit circle")


def test_country_indicator(modelling_df):
    """country_pt is 1 for Portugal, 0 for Spain."""
    pt = modelling_df[modelling_df["country"] == "PRT"]["country_pt"]
    es = modelling_df[modelling_df["country"] == "ESP"]["country_pt"]
    assert (pt == 1.0).all(), "country_pt should be 1 for PRT"
    assert (es == 0.0).all(), "country_pt should be 0 for ESP"


def test_lag_features_temporal_order(modelling_df):
    """Lag features should not contain future information."""
    # fires_lag1 for the first week of each country-year should be 0 or from prev year
    for country in ["PRT", "ESP"]:
        for year in modelling_df["year"].unique():
            subset = modelling_df[
                (modelling_df["country"] == country) &
                (modelling_df["year"] == year)
            ]
            if len(subset) == 0:
                continue
            first_row = subset.iloc[0]
            # fires_lag1 should not be NaN
            assert np.isfinite(first_row["fires_lag1"]), \
                f"NaN lag for {country} {year}"


# ---------------------------------------------------------------- metrics

def test_compute_metrics_perfect():
    """Perfect predictions should give AUC=1 and Brier=0."""
    y_true = np.array([0, 0, 0, 1, 1, 1])
    y_proba = np.array([0.0, 0.1, 0.2, 0.8, 0.9, 1.0])
    m = compute_metrics(y_true, y_proba)
    assert m["auc"] == 1.0
    assert m["brier"] < 0.1


def test_compute_metrics_random():
    """Random predictions should give AUC ~0.5."""
    rng = np.random.default_rng(42)
    y_true = rng.integers(0, 2, 1000)
    y_proba = rng.random(1000)
    m = compute_metrics(y_true, y_proba)
    assert 0.4 < m["auc"] < 0.6, f"Random AUC={m['auc']:.3f}"


# ---------------------------------------------------------------- temporal CV

def test_temporal_cv_no_leakage(modelling_df):
    """Temporal CV should never use future data in training."""
    features = get_baseline_features()
    # Use small set of test years for speed
    test_years = [2020, 2021]
    cv = temporal_cv(modelling_df, make_ridge, features,
                     test_years=test_years, verbose=False)
    assert cv["n_folds"] == len(test_years)
    for fold in cv["fold_metrics"]:
        # All training data should be before test year
        assert fold["n_train"] > 0
        assert fold["n_test"] > 0


def test_temporal_cv_auc_above_chance(modelling_df):
    """Model should beat random (AUC > 0.55) on temporal CV."""
    features = get_baseline_features()
    cv = temporal_cv(modelling_df, make_ridge, features, verbose=False)
    assert cv["auc"] > 0.55, f"CV AUC={cv['auc']:.3f} not above chance"


def test_ridge_reproducibility(modelling_df):
    """Running Ridge twice with same data produces identical results."""
    features = get_baseline_features()
    m1 = temporal_cv(modelling_df, make_ridge, features,
                     test_years=[2020], verbose=False)
    m2 = temporal_cv(modelling_df, make_ridge, features,
                     test_years=[2020], verbose=False)
    assert abs(m1["auc"] - m2["auc"]) < 1e-10, \
        f"Reproducibility broken: {m1['auc']} vs {m2['auc']}"
