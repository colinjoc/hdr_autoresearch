"""Tests for hdr_loop.py — experiment dispatch."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import hdr_loop  # noqa: E402


@pytest.fixture
def df():
    return pd.read_csv(ROOT / "data" / "paint.csv")


def test_run_experiment_xgboost(df):
    cfg = hdr_loop.ExperimentConfig(
        exp_id="T_test_xgb",
        description="XGBoost test",
        target="gloss_60",
        prior=0.5,
        mechanism="test",
        model_family="xgboost",
    )
    m = hdr_loop.run_experiment(cfg, df)
    assert m["mae"] > 0
    assert m["mae"] < 50


def test_run_experiment_lightgbm(df):
    cfg = hdr_loop.ExperimentConfig(
        exp_id="T_test_lgb",
        description="LightGBM test",
        target="gloss_60",
        prior=0.5,
        mechanism="test",
        model_family="lightgbm",
    )
    m = hdr_loop.run_experiment(cfg, df)
    assert m["mae"] > 0


def test_run_experiment_extratrees(df):
    cfg = hdr_loop.ExperimentConfig(
        exp_id="T_test_et",
        description="ExtraTrees test",
        target="scratch_hardness_N",
        prior=0.5,
        mechanism="test",
        model_family="extratrees",
        n_estimators=50,
    )
    m = hdr_loop.run_experiment(cfg, df)
    assert m["mae"] > 0


def test_run_experiment_ridge(df):
    cfg = hdr_loop.ExperimentConfig(
        exp_id="T_test_ridge",
        description="Ridge test",
        target="cupping_mm",
        prior=0.5,
        mechanism="test",
        model_family="ridge",
    )
    m = hdr_loop.run_experiment(cfg, df)
    assert m["mae"] > 0


def test_run_experiment_gp(df):
    cfg = hdr_loop.ExperimentConfig(
        exp_id="T_test_gp",
        description="GP test",
        target="hiding_power_pct",
        prior=0.5,
        mechanism="test",
        model_family="gp",
    )
    m = hdr_loop.run_experiment(cfg, df)
    assert m["mae"] > 0


def test_run_experiment_with_extra_features(df):
    cfg = hdr_loop.ExperimentConfig(
        exp_id="T_test_feat",
        description="XGB + PVC",
        target="gloss_60",
        prior=0.5,
        mechanism="test",
        model_family="xgboost",
        extra_features=["pvc_proxy", "log_thickness"],
    )
    m = hdr_loop.run_experiment(cfg, df)
    assert m["mae"] > 0


def test_experiment_count():
    winners = {"scratch_hardness_N": "xgboost", "gloss_60": "xgboost",
               "hiding_power_pct": "xgboost", "cupping_mm": "xgboost"}
    exps = hdr_loop.build_phase2_experiments(winners)
    # Require at least 50 total experiments
    assert len(exps) >= 50, f"only {len(exps)} experiments"
