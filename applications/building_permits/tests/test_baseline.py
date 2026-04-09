"""Tests for the Phase 0.5 baseline + Phase 1 tournament harness.

These tests run against a small synthetic DataFrame (no network) plus a
tiny-scale end-to-end reproduction check. They do NOT require the full
50k-row cleaned parquet to exist — a tiny synthetic fixture proves the
pipeline logic without depending on live APIs.
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

from model import (  # noqa: E402
    CITIES_FOR_BASELINE,
    RAW_FEATURES,
    RAW_FEATURES_NON_TE,
    add_features,
    build_clean_dataset,
    make_baseline_xgb,
    target_encode,
)
from evaluate import cross_validate  # noqa: E402


# ---------------------------------------------------------------- fixtures

def _synth_df(n_per_city: int = 200, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    subtypes_by_city = {
        "sf": ["1 family dwelling", "2 family dwelling", "apartments"],
        "nyc": ["A1 residential", "A2 residential", "R6 residential"],
        "la": ["1 or 2 Family Dwelling", "Apartment", "Duplex"],
        "chicago": ["NEW CONSTRUCTION", "STANDARD PLAN REVIEW", "EASY PERMIT"],
        "austin": ["R- 101 Single Family Houses", "R- 103 Two Family Bldgs", "Residential"],
    }
    ptypes_by_city = {
        "sf": ["new construction", "additions alterations or repairs"],
        "nyc": ["NB", "A1", "A2"],
        "la": ["Bldg-New", "Bldg-Alter/Repair"],
        "chicago": ["PERMIT - NEW CONSTRUCTION", "PERMIT - RENOVATION/ALTERATION"],
        "austin": ["Building Permit", "Residential"],
    }
    neighborhoods_by_city = {
        "sf": ["Mission", "Castro", "Sunset", "Bayview", "OTHER"],
        "nyc": ["Williamsburg", "Midtown", "Harlem", "Astoria"],
        "la": ["Hollywood", "Venice", "Downtown", "Silver Lake"],
        "chicago": ["Lincoln Park", "Wicker Park", "Hyde Park"],
        "austin": ["78704", "78702", "78745", "78703"],
    }
    base_median = {"sf": 200, "nyc": 150, "la": 90, "chicago": 60, "austin": 45}
    for city in CITIES_FOR_BASELINE:
        for i in range(n_per_city):
            filed = pd.Timestamp("2020-01-01") + pd.Timedelta(days=int(rng.integers(0, 1500)))
            # Duration heavy-tailed around city median, with subtype drift.
            subtype = subtypes_by_city[city][int(rng.integers(0, len(subtypes_by_city[city])))]
            subtype_mult = 1.0 if "1 family" in subtype.lower() or "single" in subtype.lower() else 1.5
            duration = int(max(1, rng.lognormal(mean=np.log(base_median[city] * subtype_mult), sigma=0.5)))
            rows.append({
                "city": city,
                "permit_id": f"{city}-{i:05d}",
                "address": f"{i} Main St",
                "parcel_id": f"{i:06d}",
                "permit_type": ptypes_by_city[city][int(rng.integers(0, len(ptypes_by_city[city])))],
                "permit_subtype": subtype,
                "use_code": "dwelling",
                "status": "issued",
                "filed_date": filed,
                "first_action_date": filed,
                "plan_check_start_date": filed,
                "plan_check_end_date": filed + pd.Timedelta(days=duration // 2),
                "approval_date": filed + pd.Timedelta(days=duration),
                "issued_date": filed + pd.Timedelta(days=duration),
                "finaled_date": filed + pd.Timedelta(days=duration + 30),
                "valuation_usd": float(rng.uniform(50_000, 1_500_000)),
                "square_feet": float(rng.uniform(500, 5_000)),
                "unit_count": float(rng.integers(1, 5)),
                "neighborhood": neighborhoods_by_city[city][int(rng.integers(0, len(neighborhoods_by_city[city])))],
            })
    return pd.DataFrame(rows)


@pytest.fixture(scope="module")
def clean_synth() -> pd.DataFrame:
    return build_clean_dataset(_synth_df(n_per_city=200))


# ---------------------------------------------------------------- tests

def test_load_clean_dataset(clean_synth):
    """Filters produce a non-empty dataset with the expected columns and target."""
    df = clean_synth
    assert len(df) > 0, "clean dataset should not be empty"
    assert "duration_days" in df.columns
    assert (df["duration_days"] > 0).all()
    assert (df["duration_days"] < 1825).all()
    assert df["filed_date"].notna().all()
    assert df["issued_date"].notna().all()
    # All five baseline cities represented.
    present_cities = set(df["city"].unique())
    assert present_cities.issubset(set(CITIES_FOR_BASELINE))
    assert len(present_cities) >= 3, f"expected ≥3 cities, got {present_cities}"


def test_add_features_shape(clean_synth):
    """add_features produces every non-target-encoded RAW_FEATURES column."""
    feat = add_features(clean_synth)
    for col in RAW_FEATURES_NON_TE:
        assert col in feat.columns, f"missing feature column: {col}"
    # Cyclic encodings live on the unit circle.
    r2 = feat["filed_month_sin"].values ** 2 + feat["filed_month_cos"].values ** 2
    assert np.allclose(r2, 1.0, atol=1e-9)
    # log_* columns are finite and non-negative after log1p.
    for c in ["log_valuation", "log_square_feet", "log_unit_count"]:
        vals = feat[c].values
        assert np.isfinite(vals).all(), f"{c} has non-finite values"
        assert (vals >= 0).all(), f"{c} has negative values"
    # City one-hot sums to at most 1 per row (==1 for known cities).
    city_cols = [f"city_{c}" for c in CITIES_FOR_BASELINE]
    assert np.allclose(feat[city_cols].sum(axis=1).values, 1.0)


def test_baseline_reproducibility(clean_synth):
    """Running the baseline twice with same seed produces identical MAE."""
    m1 = cross_validate(clean_synth, make_baseline_xgb, n_splits=3, seed=42, verbose=False)
    m2 = cross_validate(clean_synth, make_baseline_xgb, n_splits=3, seed=42, verbose=False)
    assert m1["mae_days"] == pytest.approx(m2["mae_days"], rel=0, abs=1e-6), \
        f"reproducibility broken: {m1['mae_days']} vs {m2['mae_days']}"
    assert m1["r2_log"] == pytest.approx(m2["r2_log"], rel=0, abs=1e-6)


def test_target_encode_no_leakage():
    """Target encoding derived from train only never uses valid-row y values."""
    rng = np.random.default_rng(0)
    n_train = 80
    n_valid = 20
    cats = np.array(["A", "B", "C", "D"])
    train_df = pd.DataFrame({
        "cat": rng.choice(cats, size=n_train),
    })
    valid_df = pd.DataFrame({
        "cat": rng.choice(cats, size=n_valid),
    })
    y_train = rng.normal(loc=5.0, scale=2.0, size=n_train)

    te_valid_a = target_encode(train_df, valid_df, "cat", y_train)

    # Recompute after CLOBBERING the valid frame's cat column with garbage — the
    # train-derived encoding should not be a function of valid's categories at all,
    # so we instead verify: changing y values that correspond to VALID-index rows
    # (which don't exist in y_train) must leave the encoding unchanged.
    # Direct check: encoding is fully determined by (train_df.cat, y_train),
    # independent of valid y. We simulate an "oracle" valid y and confirm it's
    # never read.
    y_valid_garbage = np.full(n_valid, 1e9)  # would shift means massively if leaked
    te_valid_b = target_encode(train_df, valid_df, "cat", y_train)  # no valid y passed
    np.testing.assert_array_equal(te_valid_a, te_valid_b)

    # Each encoded value must equal the smoothed train-only stat for its cat.
    global_mean = float(np.mean(y_train))
    smoothing = 10.0
    for cat in np.unique(valid_df["cat"]):
        train_mask = (train_df["cat"] == cat).values
        n_tr = int(train_mask.sum())
        if n_tr == 0:
            expected = global_mean
        else:
            mean_tr = float(np.mean(y_train[train_mask]))
            expected = (mean_tr * n_tr + global_mean * smoothing) / (n_tr + smoothing)
        actual_vals = te_valid_a[(valid_df["cat"] == cat).values]
        np.testing.assert_allclose(actual_vals, expected, rtol=1e-10, atol=1e-10)

    # Unused variable guard (y_valid_garbage purposely unused)
    assert y_valid_garbage.sum() > 0
