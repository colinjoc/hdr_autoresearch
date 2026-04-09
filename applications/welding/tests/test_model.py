"""Tests for the WeldingModel class (`model.py`).

Every test hits a single property. Run `pytest tests/test_model.py -v`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from model import WeldingModel, FEATURE_NAMES, _add_features
from evaluate import load_dataset


@pytest.fixture(scope="module")
def df():
    return load_dataset()


@pytest.fixture(scope="module")
def fitted():
    df = load_dataset()
    m = WeldingModel()
    X, y = m.featurize(df)
    m.train(X, y)
    return m, X, y


def test_featurize_returns_expected_shapes(df):
    m = WeldingModel()
    X, y = m.featurize(df)
    assert X.ndim == 2
    assert X.shape[0] == len(df)
    assert X.shape[1] == len(FEATURE_NAMES)
    assert y.shape[0] == len(df)


def test_derived_feature_names_present():
    assert "heat_input_kj_mm" in FEATURE_NAMES
    assert "cooling_t85_s_est" in FEATURE_NAMES


def test_heat_input_formula_matches_expected(df):
    feat = _add_features(df.iloc[:5].copy())
    expected = feat["efficiency"] * feat["voltage_v"] * feat["current_a"] / (feat["travel_mm_s"] * 1000.0)
    np.testing.assert_allclose(feat["heat_input_kj_mm"].values, expected.values, rtol=1e-6)


def test_featurize_single_gives_same_vector_as_batch():
    df = load_dataset()
    m = WeldingModel()
    X_batch, _ = m.featurize(df.head(3))
    for idx, row in df.head(3).iterrows():
        vec = m.featurize_single(row.to_dict())
        np.testing.assert_allclose(vec, X_batch[idx], rtol=1e-5)


def test_train_predict_produces_finite_output(fitted):
    m, X, _ = fitted
    y_pred = m.predict(X)
    assert np.isfinite(y_pred).all()
    assert (y_pred > 0).all()


def test_model_can_predict_novel_candidate():
    df = load_dataset()
    m = WeldingModel()
    X, y = m.featurize(df)
    m.train(X, y)
    candidate = {
        "process": "GMAW", "voltage_v": 25.0, "current_a": 200.0,
        "travel_mm_s": 6.0, "efficiency": 0.80, "thickness_mm": 10.0,
        "preheat_c": 50.0, "carbon_equiv": 0.40,
    }
    vec = m.featurize_single(candidate)
    pred = m.predict(vec.reshape(1, -1))[0]
    # The predicted HAZ half-width must be inside the training range.
    assert df["haz_width_mm"].min() * 0.3 < pred < df["haz_width_mm"].max() * 1.5
