"""TDD unit tests for the Fused Deposition Modelling (FDM) parameter
optimisation harness.

These tests exercise the dataset loader, the derived feature computations,
the baseline model, the cross-validation harness, and the Phase B
candidate-generation helpers in isolation. Every test is small enough to
run in under a second on the 50-row Kaggle 3D Printer Dataset.

Run from the project root:
    pytest tests/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hdr_loop import (  # noqa: E402
    RAW_FEATURES,
    add_features,
    fit_predict,
    load_dataset,
    ExperimentConfig,
)
import evaluate  # noqa: E402
from model import PrinterModel  # noqa: E402


# ---------------------------------------------------------------------------
# Dataset loader
# ---------------------------------------------------------------------------


def test_dataset_file_exists():
    assert (ROOT / "data" / "3d_printing.csv").exists(), (
        "data/3d_printing.csv missing. Fetch via data_sources.md."
    )


def test_load_dataset_shape_and_columns():
    df = load_dataset()
    # The canonical Kaggle 3D Printer Dataset has 50 rows.
    assert len(df) == 50
    expected = {
        "layer_height", "wall_thickness", "infill_density", "infill_pattern",
        "nozzle_temperature", "bed_temperature", "print_speed", "material",
        "fan_speed", "roughness", "tension_strength", "elongation",
    }
    assert expected.issubset(set(df.columns))


def test_target_is_in_physical_range():
    df = load_dataset()
    y = df["tension_strength"]
    # Tensile strength for PLA and ABS tensile bars typically falls in
    # the 4 - 70 megapascal range. This is a sanity check on the units.
    assert y.min() >= 1
    assert y.max() <= 100


# ---------------------------------------------------------------------------
# Derived features
# ---------------------------------------------------------------------------


def test_add_features_preserves_rows():
    df = load_dataset()
    out = add_features(df, ["E_lin"])
    assert len(out) == len(df)


def test_linear_energy_density_formula():
    df = load_dataset()
    out = add_features(df, ["E_lin"])
    # E_lin = nozzle_temperature * print_speed / layer_height (lit H1).
    expected = df["nozzle_temperature"] * df["print_speed"] / df["layer_height"]
    np.testing.assert_allclose(out["E_lin"].values, expected.values, rtol=1e-10)


def test_volumetric_flow_formula():
    df = load_dataset()
    out = add_features(df, ["vol_flow"])
    # vol_flow = print_speed * layer_height * assumed_line_width.
    # Line width is fixed at 1.2 * (assumed nozzle diameter 0.4) = 0.48 mm
    # for the Kaggle dataset (Ultimaker S5 default). See hdr_loop.add_features.
    expected = df["print_speed"] * df["layer_height"] * 0.48
    np.testing.assert_allclose(out["vol_flow"].values, expected.values, rtol=1e-10)


def test_cooling_rate_formula():
    df = load_dataset()
    out = add_features(df, ["cool_rate"])
    # cool_rate = (T_nozzle - T_amb) * fan_speed / h_layer  with T_amb = 25
    expected = (df["nozzle_temperature"] - 25.0) * df["fan_speed"] / df["layer_height"]
    np.testing.assert_allclose(out["cool_rate"].values, expected.values, rtol=1e-10)


def test_unknown_feature_name_raises():
    df = load_dataset()
    with pytest.raises(ValueError):
        add_features(df, ["a_feature_that_does_not_exist"])


# ---------------------------------------------------------------------------
# Baseline model sanity
# ---------------------------------------------------------------------------


def test_fit_predict_baseline_runs_and_returns_metrics():
    df = load_dataset()
    cfg = ExperimentConfig(
        "test_baseline", "smoke-test baseline", prior=1.0,
        mechanism="sanity", model_family="xgboost",
    )
    m = fit_predict(cfg, df)
    assert {"mae", "rmse", "r2"} <= set(m.keys())
    # On a tensile-strength range of roughly 33 MPa, the MAE should be
    # less than the naive-mean MAE (roughly 7.2 MPa) by any sensible model.
    assert m["mae"] < 7.2
    assert m["mae"] > 0


def test_fit_predict_ridge_is_linear_sanity_check():
    df = load_dataset()
    cfg = ExperimentConfig(
        "test_ridge", "linear sanity", prior=0.05,
        mechanism="linear", model_family="ridge",
    )
    m = fit_predict(cfg, df)
    assert m["mae"] > 0
    assert np.isfinite(m["r2"])


# ---------------------------------------------------------------------------
# PrinterModel class (mirrors concrete.ConcreteModel interface)
# ---------------------------------------------------------------------------


def test_printer_model_interface():
    df = load_dataset()
    model = PrinterModel()
    X, y = model.featurize(df)
    assert X.shape[0] == len(df)
    assert y.shape[0] == len(df)
    model.train(X, y)
    preds = model.predict(X)
    assert preds.shape == y.shape
    # Training-set fit MAE must be small (<5 megapascals) for an XGBoost.
    mae = float(np.mean(np.abs(preds - y)))
    assert mae < 5.0


def test_printer_model_featurize_single():
    model = PrinterModel()
    mix = {
        "layer_height": 0.1, "wall_thickness": 5, "infill_density": 50,
        "infill_pattern": 1, "nozzle_temperature": 220, "bed_temperature": 70,
        "print_speed": 60, "material": 1, "fan_speed": 50,
    }
    feat = model.featurize_single(mix)
    assert feat.ndim == 1
    assert feat.shape[0] == len(model.feature_names)
    assert np.all(np.isfinite(feat))


# ---------------------------------------------------------------------------
# Evaluate harness (cross-validation wrapper)
# ---------------------------------------------------------------------------


def test_cross_validate_runs_on_printer_model():
    df = load_dataset()
    out = evaluate.cross_validate(PrinterModel, df)
    assert {"mae", "rmse", "r2", "n"} <= set(out.keys())
    assert out["n"] == len(df)
    # Sanity: MAE must be better than mean-predictor (~7.2 MPa) and
    # must be positive.
    assert 0 < out["mae"] < 7.2


# ---------------------------------------------------------------------------
# Phase B physics helpers
# ---------------------------------------------------------------------------


def test_print_time_proxy_is_positive():
    import phase_b_discovery as pb
    mix = {
        "layer_height": 0.1, "wall_thickness": 2, "infill_density": 20,
        "infill_pattern": 0, "nozzle_temperature": 210, "bed_temperature": 60,
        "print_speed": 60, "material": 1, "fan_speed": 100,
    }
    t = pb.print_time_proxy(mix)
    assert t > 0


def test_energy_cost_proxy_scales_with_time():
    import phase_b_discovery as pb
    mix_fast = {
        "layer_height": 0.20, "wall_thickness": 2, "infill_density": 20,
        "infill_pattern": 0, "nozzle_temperature": 210, "bed_temperature": 60,
        "print_speed": 120, "material": 1, "fan_speed": 100,
    }
    mix_slow = dict(mix_fast, layer_height=0.06, print_speed=40)
    t_fast = pb.print_time_proxy(mix_fast)
    t_slow = pb.print_time_proxy(mix_slow)
    assert t_slow > t_fast
    e_fast = pb.energy_proxy(mix_fast)
    e_slow = pb.energy_proxy(mix_slow)
    assert e_slow > e_fast


def test_pareto_front_nontrivial():
    import phase_b_discovery as pb
    # Handcrafted set: three dominated candidates and one strictly better.
    data = pd.DataFrame([
        {"predicted_strength": 30, "print_time_hours": 2.0},
        {"predicted_strength": 20, "print_time_hours": 2.0},   # dominated
        {"predicted_strength": 20, "print_time_hours": 3.0},   # dominated
        {"predicted_strength": 35, "print_time_hours": 1.0},   # dominates all
    ])
    front = pb.pareto_front_strength_time(data)
    assert len(front) == 1
    assert front.iloc[0]["predicted_strength"] == 35


def test_generate_candidates_count_and_variety():
    import phase_b_discovery as pb
    cands = pb.generate_candidates()
    assert len(cands) > 500, "Phase B should generate at least 500 candidates"
    materials = set(c["material"] for c in cands)
    assert materials == {0, 1}, "Candidates must span both PLA and ABS"
    sources = set(c["source"] for c in cands)
    assert len(sources) >= 4, "At least 4 generation strategies expected"


def test_winning_config_round_trip(tmp_path):
    # Minimal round-trip serialization: write the structure we persist.
    cfg = {
        "exp_id": "test", "description": "d", "model_family": "xgboost",
        "extra_features": ["E_lin"], "xgb_params": {}, "lgb_params": {},
        "monotone_constraints": None, "log_target": False,
        "n_estimators": 300, "mae": 5.0,
    }
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(cfg))
    loaded = json.loads(p.read_text())
    assert loaded == cfg
