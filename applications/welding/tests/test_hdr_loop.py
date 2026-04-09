"""Tests for hdr_loop.py, hdr_phase25.py, and phase_b_discovery.py.

Exercises the Hypothesis-Driven Research (HDR) components to make sure
they are importable and that a single experiment config can be fit
without error. Integration-level smoke tests only — the full loops are
run separately from the command line.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

import hdr_loop


def test_hdr_loop_importable():
    assert hasattr(hdr_loop, "ExperimentConfig")
    assert hasattr(hdr_loop, "fit_predict")
    assert hasattr(hdr_loop, "add_features")


def test_add_features_produces_expected_columns():
    df = hdr_loop.load_dataset().head(20)
    out = hdr_loop.add_features(df, ["heat_input_kj_mm", "cooling_t85_s_est"])
    assert "heat_input_kj_mm" in out.columns
    assert "cooling_t85_s_est" in out.columns
    # Heat input must match the textbook HI = eta*V*I/(v*1000) in kJ/mm
    expected = (out["efficiency"] * out["voltage_v"] * out["current_a"]
                / (out["travel_mm_s"] * 1000.0))
    np.testing.assert_allclose(out["heat_input_kj_mm"].values, expected.values, rtol=1e-6)


def test_fit_predict_runs_single_experiment():
    df = hdr_loop.load_dataset()
    cfg = hdr_loop.ExperimentConfig(
        "TEST01", "smoke test", prior=0.5, mechanism="unit test",
        model_family="xgboost",
        extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
        n_estimators=50)
    m = hdr_loop.fit_predict(cfg, df)
    assert "mae" in m
    assert m["mae"] > 0
    assert m["r2"] > 0.5  # even a weak model should beat the mean


def test_winning_config_json_readable_and_valid():
    cfg_path = PROJECT / "winning_config.json"
    assert cfg_path.exists(), "run hdr_loop.py first"
    cfg = json.loads(cfg_path.read_text())
    for required in ("exp_id", "model_family", "extra_features", "mae"):
        assert required in cfg
    assert cfg["mae"] > 0


def test_results_tsv_contains_baseline_row():
    tsv = PROJECT / "results.tsv"
    assert tsv.exists()
    df = pd.read_csv(tsv, sep="\t")
    assert "E00" in df["exp_id"].values
    baseline_row = df[df["exp_id"] == "E00"].iloc[0]
    assert baseline_row["decision"] == "BASELINE"
    assert baseline_row["mae"] > 0


def test_phase_b_discovery_importable():
    import phase_b_discovery
    assert hasattr(phase_b_discovery, "generate_candidates")
    cands = phase_b_discovery.generate_candidates()
    assert len(cands) > 100
    # Every candidate carries the 8 process + efficiency parameters
    required = {"voltage_v", "current_a", "travel_mm_s",
                "thickness_mm", "preheat_c", "carbon_equiv", "efficiency"}
    for cand in cands[:5]:
        assert required <= set(cand.keys())


def test_hdr_phase25_importable():
    import hdr_phase25
    assert hasattr(hdr_phase25, "cross_process_transfer")
    assert hasattr(hdr_phase25, "h1_explicit_test")
