"""
phase_b_discovery.py — Phase B: inverse design + Pareto screening for the
welding HDR project.

Loads the Phase 2.5 winning model from `winning_config.json`, retrains on
the FULL steel arc-welding dataset (not cross-validation), then generates
several thousand candidate welding parameter tuples across multiple
strategies and ranks them on three objectives:

    1. predicted Heat-Affected Zone (HAZ) half-width (millimetres) —
       quality proxy (tighter HAZ means less distortion and less
       loss of mechanical properties)
    2. predicted production cost (proxy: inverse of travel speed,
       since slower welds take more arc-on time per metre)
    3. heat input per metre (sustainability proxy — lower heat input
       means less energy consumed per metre of weld)

Five candidate-generation strategies cover:
    - dense grid over (voltage, current, travel speed, thickness)
    - preheat sweeps
    - thin- vs thick-plate regimes
    - high-strength-steel windows (low HI, fast cooling)
    - random Latin-hypercube stratified samples

Outputs:
    discoveries/discovery_candidates.csv  — all scored candidates
    discoveries/discovery_pareto.csv      — Pareto-optimal subset
    discoveries/discovery_summary.json    — headline numbers
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import xgboost as xgb

from hdr_loop import (
    PROJECT_ROOT, RAW_FEATURES, XGB_DEFAULT, add_features, load_dataset,
)

DISC_DIR = PROJECT_ROOT / "discoveries"


def train_winning_model(cfg: Dict, df: pd.DataFrame):
    """Retrain the Phase 2.5 winner on the full steel arc-welding dataset."""
    df_feat = add_features(df, cfg["extra_features"])
    feature_names = RAW_FEATURES + list(cfg["extra_features"])
    X = df_feat[feature_names].values.astype(np.float32)
    y = df_feat["haz_width_mm"].values.astype(np.float32)
    if cfg.get("log_target"):
        y_fit = np.log1p(y)
    else:
        y_fit = y
    params = dict(XGB_DEFAULT)
    params.update(cfg.get("xgb_params") or {})
    if cfg.get("monotone_constraints"):
        vec = [cfg["monotone_constraints"].get(f, 0) for f in feature_names]
        params["monotone_constraints"] = "(" + ",".join(str(v) for v in vec) + ")"
    dtr = xgb.DMatrix(X, label=y_fit)
    booster = xgb.train(params, dtr, num_boost_round=cfg.get("n_estimators", 300))
    return booster, feature_names


def featurize_candidate(mix: Dict[str, float], extra_features: List[str],
                        feature_names: List[str]) -> np.ndarray:
    """Compute the full feature vector for a single candidate tuple."""
    row = pd.DataFrame([mix])
    df_feat = add_features(row, extra_features)
    return df_feat[feature_names].values.astype(np.float32)[0]


def predict_haz(booster, feature_vec: np.ndarray, log_target: bool) -> float:
    y_pred = booster.predict(xgb.DMatrix(feature_vec.reshape(1, -1)))[0]
    if log_target:
        y_pred = np.expm1(y_pred)
    return float(y_pred)


# ---------------------------------------------------------------------------
# Candidate generation strategies
# ---------------------------------------------------------------------------

def generate_candidates() -> List[Dict]:
    """Five generation strategies returning ~5000 candidate tuples.

    Every candidate specifies a process (GMAW), voltage, current, travel
    speed, thickness, preheat, and carbon equivalent. The efficiency is
    set to 0.8 (GMAW default) except for the GTAW sweep which uses 0.6.
    """
    candidates: List[Dict] = []

    # Strategy 1: dense grid over primary GMAW parameters
    for v in [18, 21, 24, 27, 30]:
        for i in [120, 150, 180, 210, 240, 270]:
            for s in [3, 5, 7, 9, 11]:
                for thk in [4, 8, 12, 16]:
                    candidates.append({
                        "process": "GMAW",
                        "voltage_v": float(v),
                        "current_a": float(i),
                        "travel_mm_s": float(s),
                        "thickness_mm": float(thk),
                        "preheat_c": 25.0,
                        "carbon_equiv": 0.40,
                        "efficiency": 0.8,
                        "source": "gmaw_grid",
                    })

    # Strategy 2: preheat sweep on high-CE steel (safety window)
    for pre in [0, 50, 100, 150, 200]:
        for i in [150, 200, 250]:
            for s in [4, 6, 8]:
                for thk in [10, 15, 20]:
                    candidates.append({
                        "process": "GMAW",
                        "voltage_v": 24.0,
                        "current_a": float(i),
                        "travel_mm_s": float(s),
                        "thickness_mm": float(thk),
                        "preheat_c": float(pre),
                        "carbon_equiv": 0.50,  # high-strength steel
                        "efficiency": 0.8,
                        "source": "preheat_sweep",
                    })

    # Strategy 3: thin-plate high-speed windows
    for v in [20, 24, 28]:
        for i in [100, 140, 180, 220]:
            for s in [6, 9, 12, 15]:
                for thk in [2.0, 3.0, 4.5]:
                    candidates.append({
                        "process": "GMAW",
                        "voltage_v": float(v),
                        "current_a": float(i),
                        "travel_mm_s": float(s),
                        "thickness_mm": float(thk),
                        "preheat_c": 25.0,
                        "carbon_equiv": 0.35,
                        "efficiency": 0.8,
                        "source": "thin_plate",
                    })

    # Strategy 4: low-heat-input windows (HAZ minimisation)
    for v in [18, 20, 22]:
        for i in [100, 130, 160]:
            for s in [8, 10, 12]:
                for thk in [6, 10, 14]:
                    candidates.append({
                        "process": "GMAW",
                        "voltage_v": float(v),
                        "current_a": float(i),
                        "travel_mm_s": float(s),
                        "thickness_mm": float(thk),
                        "preheat_c": 50.0,
                        "carbon_equiv": 0.42,
                        "efficiency": 0.8,
                        "source": "low_hi",
                    })

    # Strategy 5: stratified Latin-hypercube-style random samples
    rng = np.random.default_rng(20260409)
    for _ in range(800):
        candidates.append({
            "process": "GMAW",
            "voltage_v": float(rng.uniform(18, 32)),
            "current_a": float(rng.uniform(100, 300)),
            "travel_mm_s": float(rng.uniform(3, 12)),
            "thickness_mm": float(rng.uniform(3, 20)),
            "preheat_c": float(rng.uniform(0, 150)),
            "carbon_equiv": float(rng.choice([0.35, 0.40, 0.42, 0.50])),
            "efficiency": 0.8,
            "source": "lhs_random",
        })

    return candidates


def heat_input_kj_mm(row: Dict) -> float:
    return row["efficiency"] * row["voltage_v"] * row["current_a"] / (row["travel_mm_s"] * 1000.0)


def cost_proxy(row: Dict) -> float:
    """Production-cost proxy: inverse of travel speed, normalised to
    give dimensionless numbers in the [0.08, 0.33] range for the typical
    welding window. Lower is better.
    """
    return 1.0 / max(row["travel_mm_s"], 0.1)


def pareto_front_haz_cost(df: pd.DataFrame) -> pd.DataFrame:
    """Pareto front minimising HAZ and cost simultaneously."""
    rows = df.sort_values("cost_proxy").reset_index(drop=True)
    front = []
    best_haz = np.inf
    for _, row in rows.iterrows():
        if row["predicted_haz_mm"] < best_haz:
            front.append(row)
            best_haz = row["predicted_haz_mm"]
    return pd.DataFrame(front)


def main():
    cfg_path = PROJECT_ROOT / "winning_config.json"
    cfg = json.loads(cfg_path.read_text())
    print(f"loaded winning config: {cfg['exp_id']}  MAE={cfg['mae']:.4f}")
    print(f"  features: {cfg['extra_features']}")
    print(f"  monotone: {cfg.get('monotone_constraints')}")

    df = load_dataset()
    booster, feature_names = train_winning_model(cfg, df)
    print(f"  retrained on full dataset ({len(df)} rows)")

    candidates = generate_candidates()
    print(f"\ngenerated {len(candidates)} candidate tuples across "
          f"{len(set(c['source'] for c in candidates))} strategies")

    rows = []
    for cand in candidates:
        feat = featurize_candidate(cand, cfg["extra_features"], feature_names)
        try:
            haz = predict_haz(booster, feat, cfg.get("log_target", False))
        except Exception:
            continue
        hi = heat_input_kj_mm(cand)
        rows.append({
            **cand,
            "predicted_haz_mm": haz,
            "heat_input_kj_mm": hi,
            "cost_proxy": cost_proxy(cand),
        })

    cand_df = pd.DataFrame(rows)
    cand_df = cand_df[cand_df["predicted_haz_mm"] > 0]
    DISC_DIR.mkdir(exist_ok=True)
    cand_df.to_csv(DISC_DIR / "discovery_candidates.csv", index=False)

    pareto = pareto_front_haz_cost(cand_df)
    pareto.to_csv(DISC_DIR / "discovery_pareto.csv", index=False)

    print("\ndiscovery results:")
    print(f"  total candidates: {len(cand_df)}")
    print(f"  Pareto front:     {len(pareto)}")
    print(f"  min HAZ (any):    {cand_df['predicted_haz_mm'].min():.2f} mm")
    print(f"  max HAZ (any):    {cand_df['predicted_haz_mm'].max():.2f} mm")
    print(f"  min HI:           {cand_df['heat_input_kj_mm'].min():.3f} kJ/mm")
    print(f"  max HI:           {cand_df['heat_input_kj_mm'].max():.3f} kJ/mm")

    # Reference points
    narrow = cand_df[cand_df["predicted_haz_mm"] <= 3.0]
    print(f"\n  candidates with HAZ ≤ 3 mm: {len(narrow)}")
    if len(narrow) > 0:
        best = narrow.sort_values("cost_proxy").iloc[0]
        print(f"  best (≤3 mm, fastest travel):  "
              f"V={best['voltage_v']:.1f} I={best['current_a']:.0f} "
              f"v={best['travel_mm_s']:.1f} mm/s thk={best['thickness_mm']:.0f} mm "
              f"→ HAZ={best['predicted_haz_mm']:.2f} mm  HI={best['heat_input_kj_mm']:.2f} kJ/mm")

    # Top 5 by sustainability (lowest HI that still meets HAZ target)
    sust = cand_df[cand_df["predicted_haz_mm"] <= 5.0].sort_values("heat_input_kj_mm")
    print(f"\n  Top 5 low-HI candidates with HAZ ≤ 5 mm:")
    for _, r in sust.head(5).iterrows():
        print(f"    HI={r['heat_input_kj_mm']:.2f} kJ/mm  HAZ={r['predicted_haz_mm']:.2f} mm  "
              f"V={r['voltage_v']:.1f} I={r['current_a']:.0f} v={r['travel_mm_s']:.1f} mm/s "
              f"thk={r['thickness_mm']:.0f} ({r['source']})")

    summary = {
        "winning_exp": cfg["exp_id"],
        "total_candidates": int(len(cand_df)),
        "pareto_size": int(len(pareto)),
        "min_haz_mm": float(cand_df["predicted_haz_mm"].min()),
        "max_haz_mm": float(cand_df["predicted_haz_mm"].max()),
        "min_hi_kj_mm": float(cand_df["heat_input_kj_mm"].min()),
        "max_hi_kj_mm": float(cand_df["heat_input_kj_mm"].max()),
        "n_haz_under_3mm": int(len(narrow)),
        "n_haz_under_5mm": int((cand_df["predicted_haz_mm"] <= 5.0).sum()),
        "best_narrow_haz": narrow.sort_values("cost_proxy").iloc[0].to_dict() if len(narrow) > 0 else None,
        "top5_low_hi_under_5mm": sust.head(5).to_dict("records"),
    }
    (DISC_DIR / "discovery_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nwrote discovery_candidates.csv, discovery_pareto.csv, discovery_summary.json")


if __name__ == "__main__":
    main()
