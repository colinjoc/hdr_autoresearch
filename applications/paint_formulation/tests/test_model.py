"""Tests for model.py — the PaintFormulationModel predictor."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from model import PaintFormulationModel, RAW_FEATURES, TARGET_COLS, featurize  # noqa: E402


@pytest.fixture
def df():
    return pd.read_csv(ROOT / "data" / "paint.csv")


def test_dataset_exists(df):
    assert len(df) >= 60, f"paint.csv should have >=60 rows, got {len(df)}"
    for col in RAW_FEATURES + TARGET_COLS + ["thickness_um"]:
        assert col in df.columns, f"missing column: {col}"


def test_featurize_returns_numpy(df):
    X, y = featurize(df, target="scratch_hardness_N", extra_features=())
    assert isinstance(X, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert X.dtype == np.float32
    assert y.dtype == np.float32
    assert X.shape[0] == len(df)
    assert y.shape[0] == len(df)
    # Default 4 composition features + thickness = 5 columns
    assert X.shape[1] == 5


def test_featurize_extra_features(df):
    X, _ = featurize(
        df,
        target="gloss_60",
        extra_features=("binder_pigment_ratio", "matting_agent_sq"),
    )
    assert X.shape[1] == 5 + 2


def test_model_train_predict(df):
    model = PaintFormulationModel(target="scratch_hardness_N")
    X, y = model.featurize(df)
    model.train(X, y)
    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    # On training data, a reasonable model should have MAE < 3 N
    mae = float(np.mean(np.abs(y_pred - y)))
    assert mae < 3.0, f"training MAE too high: {mae:.3f}"


def test_model_works_on_all_targets(df):
    for target in TARGET_COLS:
        model = PaintFormulationModel(target=target)
        X, y = model.featurize(df)
        model.train(X, y)
        y_pred = model.predict(X)
        assert y_pred.shape == y.shape, f"shape mismatch for {target}"
        assert np.isfinite(y_pred).all(), f"non-finite predictions for {target}"


def test_featurize_single(df):
    model = PaintFormulationModel(target="scratch_hardness_N")
    X_all, y = model.featurize(df)
    model.train(X_all, y)
    row = df.iloc[0].to_dict()
    feat = model.featurize_single(row)
    assert feat.shape == (X_all.shape[1],)
    pred = float(model.predict(feat.reshape(1, -1))[0])
    assert np.isfinite(pred)


def test_no_placeholder_features_on_synthetic(df):
    """Phase A -> Phase B bridge: generated candidates must get real features."""
    model = PaintFormulationModel(target="gloss_60")
    X, y = model.featurize(df)
    model.train(X, y)
    synthetic = {
        "crosslink": 0.5,
        "cyc_nco_frac": 0.5,
        "matting_agent": 0.2,
        "pigment_paste": 0.4,
        "thickness_um": 45.0,
    }
    feat = model.featurize_single(synthetic)
    assert np.isfinite(feat).all()
    pred = float(model.predict(feat.reshape(1, -1))[0])
    assert 0 < pred < 100, f"gloss out of range: {pred}"
