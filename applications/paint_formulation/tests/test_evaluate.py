"""Tests for evaluate.py — cross-validation harness."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import evaluate  # noqa: E402
from model import PaintFormulationModel, TARGET_COLS  # noqa: E402


@pytest.fixture
def df():
    return pd.read_csv(ROOT / "data" / "paint.csv")


def test_load_dataset():
    df = evaluate.load_dataset()
    assert len(df) >= 60
    for t in TARGET_COLS:
        assert t in df.columns


def test_cross_validate_returns_metrics(df):
    result = evaluate.cross_validate(
        lambda: PaintFormulationModel(target="scratch_hardness_N"),
        df, target="scratch_hardness_N",
    )
    assert "mae" in result
    assert "rmse" in result
    assert "r2" in result
    assert result["mae"] > 0
    assert result["mae"] < 10.0  # sanity: should not be insane


def test_cross_validate_all_targets(df):
    for target in TARGET_COLS:
        result = evaluate.cross_validate(
            lambda t=target: PaintFormulationModel(target=t),
            df, target=target,
        )
        assert result["mae"] > 0
        assert np.isfinite(result["mae"])
        assert np.isfinite(result["rmse"])
