"""phase_b_discovery.py -- Phase B candidate generation and Pareto
screening for the Fused Deposition Modelling (FDM) parameter optimisation
project.

Loads the winning configuration written by hdr_loop.py / hdr_phase25.py,
retrains the model on the full Kaggle 3D Printer Dataset (no held-out
fold), then generates candidate parameter vectors across several
strategies (dense grid, physics-guided sweeps, and a Latin-hypercube-
style random sample) and scores each on three objectives:

  1. predicted tensile strength (megapascals)
  2. print time (hours) estimated from a simple kinematic proxy
  3. energy consumption (kilowatt-hours) estimated from the heater and
     motor power drawn over the estimated print time

Computes the strength-vs-time Pareto front and writes:
  discoveries/discovery_candidates.csv  -- all candidates with scores
  discoveries/discovery_pareto.csv      -- Pareto-optimal subset
  discoveries/discovery_summary.json    -- headline numbers
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import xgboost as xgb

from hdr_loop import (
    PROJECT_ROOT, RAW_FEATURES, XGB_DEFAULT,
    add_features, load_dataset,
)

DISC_DIR = PROJECT_ROOT / "discoveries"

# ----------------------------------------------------------------------------
# Physics-based proxies for print time and energy
# ----------------------------------------------------------------------------

# Reference specimen: ASTM D638 Type I tensile bar, approximately
# 165 mm x 19 mm x 3.2 mm, total volume roughly 10,032 cubic millimetres.
REFERENCE_VOLUME_MM3 = 165.0 * 19.0 * 3.2
LINE_WIDTH_MM = 0.48

# Approximate power draws for an Ultimaker-class FDM printer:
#   heater (nozzle + bed + electronics): 150 watts average during print
#   motors (X/Y/Z/E + fans):               50 watts average during print
# See Kellens (2011), Peng (2016), Tlegenov (2019).
HEATER_POWER_W = 150.0
MOTOR_POWER_W = 50.0


def print_time_proxy(mix: Dict[str, float]) -> float:
    """Estimate the print time in hours for the reference specimen.

    Uses the closed-form kinematic result

        time = volume / (layer_height * line_width * print_speed)

    multiplied by a scaling factor for travel moves and a factor that
    inflates the time for denser infills (dense infills have more toolpath
    per unit volume). Returns hours.
    """
    h = max(mix.get("layer_height", 0.0), 1e-3)
    v = max(mix.get("print_speed", 0.0), 1.0)
    density_frac = max(mix.get("infill_density", 20), 5) / 100.0
    # Solid fraction: the fraction of the specimen that is actually
    # extruded road. Walls dominate for low infill, infill for high.
    walls = max(mix.get("wall_thickness", 2), 1)
    solid_frac = min(
        0.25 + 0.01 * walls + 0.75 * density_frac, 1.0)
    extruded_vol_mm3 = REFERENCE_VOLUME_MM3 * solid_frac
    seconds = extruded_vol_mm3 / (h * LINE_WIDTH_MM * v) * 1.25  # travel
    return seconds / 3600.0


def energy_proxy(mix: Dict[str, float]) -> float:
    """Estimate energy consumption in kilowatt-hours for the reference
    specimen. Heater power is assumed constant during the print; motor
    power scales linearly with print time."""
    t_h = print_time_proxy(mix)
    # Add bed temperature heating energy (bed holds target temperature).
    bed = mix.get("bed_temperature", 60)
    heater_w = HEATER_POWER_W * (1.0 + 0.003 * (bed - 60))
    total_w = heater_w + MOTOR_POWER_W
    return total_w * t_h / 1000.0  # kWh


# ----------------------------------------------------------------------------
# Candidate generation
# ----------------------------------------------------------------------------

def generate_candidates() -> List[Dict[str, float]]:
    """Seven candidate-generation strategies for the 9-parameter FDM
    design space. Returns a list of dicts; each dict has the nine
    PrinterModel input fields plus a `source` tag.
    """
    cands: List[Dict[str, float]] = []

    # ---- Strategy 1: Dense grid over the dominant 4 parameters
    # (layer_height, print_speed, nozzle_temperature, infill_density)
    # at fixed wall / pattern / bed / fan / material.
    for layer_h in [0.06, 0.1, 0.15, 0.2]:
        for speed in [40, 60, 80, 100, 120]:
            for temp in [200, 210, 220, 230, 240]:
                for infill in [20, 40, 60, 80]:
                    for material in [0, 1]:
                        bed = 100 if material == 0 else 60
                        fan = 0 if material == 0 else 100
                        cands.append({
                            "layer_height": layer_h,
                            "wall_thickness": 3,
                            "infill_density": infill,
                            "infill_pattern": 0,
                            "nozzle_temperature": temp,
                            "bed_temperature": bed,
                            "print_speed": speed,
                            "material": material,
                            "fan_speed": fan,
                            "source": "grid_4d",
                        })

    # ---- Strategy 2: High-strength regime (low speed, low layer_height,
    # high temperature, high infill, many walls).
    for layer_h in [0.06, 0.1]:
        for speed in [40, 60]:
            for temp in [220, 230, 240, 250]:
                for infill in [70, 80, 90]:
                    for walls in [3, 5, 8]:
                        for material in [0, 1]:
                            bed = 100 if material == 0 else 60
                            fan = 0 if material == 0 else 100
                            cands.append({
                                "layer_height": layer_h,
                                "wall_thickness": walls,
                                "infill_density": infill,
                                "infill_pattern": 1,
                                "nozzle_temperature": temp,
                                "bed_temperature": bed,
                                "print_speed": speed,
                                "material": material,
                                "fan_speed": fan,
                                "source": "high_strength",
                            })

    # ---- Strategy 3: High-throughput regime (high speed, thick layers,
    # moderate temperature, low infill).
    for layer_h in [0.15, 0.2]:
        for speed in [80, 100, 120]:
            for temp in [210, 220, 230]:
                for infill in [20, 30, 40]:
                    for material in [0, 1]:
                        bed = 100 if material == 0 else 60
                        fan = 0 if material == 0 else 100
                        cands.append({
                            "layer_height": layer_h,
                            "wall_thickness": 2,
                            "infill_density": infill,
                            "infill_pattern": 0,
                            "nozzle_temperature": temp,
                            "bed_temperature": bed,
                            "print_speed": speed,
                            "material": material,
                            "fan_speed": fan,
                            "source": "high_throughput",
                        })

    # ---- Strategy 4: PLA-specific sweep (cold prints, fast speeds)
    for layer_h in [0.1, 0.15, 0.2]:
        for speed in [60, 80, 100, 120]:
            for temp in [200, 205, 210, 215, 220]:
                for infill in [30, 50, 70]:
                    for fan in [50, 75, 100]:
                        cands.append({
                            "layer_height": layer_h,
                            "wall_thickness": 3,
                            "infill_density": infill,
                            "infill_pattern": 1,
                            "nozzle_temperature": temp,
                            "bed_temperature": 60,
                            "print_speed": speed,
                            "material": 1,
                            "fan_speed": fan,
                            "source": "pla_sweep",
                        })

    # ---- Strategy 5: ABS-specific sweep (hot prints, low fan)
    for layer_h in [0.1, 0.15, 0.2]:
        for speed in [40, 60, 80]:
            for temp in [230, 240, 250]:
                for infill in [30, 50, 70]:
                    for fan in [0, 25]:
                        cands.append({
                            "layer_height": layer_h,
                            "wall_thickness": 3,
                            "infill_density": infill,
                            "infill_pattern": 1,
                            "nozzle_temperature": temp,
                            "bed_temperature": 100,
                            "print_speed": speed,
                            "material": 0,
                            "fan_speed": fan,
                            "source": "abs_sweep",
                        })

    # ---- Strategy 6: Latin-hypercube-style stratified random sample
    rng = np.random.default_rng(2026)
    for _ in range(400):
        material = int(rng.choice([0, 1]))
        cands.append({
            "layer_height": float(rng.choice([0.06, 0.1, 0.15, 0.2])),
            "wall_thickness": int(rng.integers(1, 9)),
            "infill_density": int(rng.choice([10, 20, 30, 40, 50, 60, 70, 80, 90])),
            "infill_pattern": int(rng.choice([0, 1])),
            "nozzle_temperature": int(rng.choice(
                [200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250])),
            "bed_temperature": int(rng.choice([60, 65, 70, 75, 80, 100])),
            "print_speed": int(rng.choice([40, 60, 80, 100, 120])),
            "material": material,
            "fan_speed": int(rng.choice([0, 25, 50, 75, 100])),
            "source": "latin_hypercube",
        })

    # ---- Strategy 7: Wall-thickness sweep (Phase B insight: wall loops
    # dominate tensile strength at low infill)
    for walls in [1, 2, 3, 4, 5, 6, 7, 8]:
        for layer_h in [0.1, 0.15, 0.2]:
            for infill in [20, 40]:
                for material in [0, 1]:
                    temp = 240 if material == 0 else 215
                    bed = 100 if material == 0 else 60
                    fan = 0 if material == 0 else 100
                    cands.append({
                        "layer_height": layer_h,
                        "wall_thickness": walls,
                        "infill_density": infill,
                        "infill_pattern": 0,
                        "nozzle_temperature": temp,
                        "bed_temperature": bed,
                        "print_speed": 60,
                        "material": material,
                        "fan_speed": fan,
                        "source": "wall_sweep",
                    })

    return cands


# ----------------------------------------------------------------------------
# Pareto front and main pipeline
# ----------------------------------------------------------------------------

def pareto_front_strength_time(df: pd.DataFrame) -> pd.DataFrame:
    """Strength-vs-time Pareto front: maximise predicted strength,
    minimise print time."""
    rows = df.sort_values("print_time_hours").reset_index(drop=True)
    front = []
    best_strength = -np.inf
    for _, row in rows.iterrows():
        if row["predicted_strength"] > best_strength:
            front.append(row)
            best_strength = row["predicted_strength"]
    return pd.DataFrame(front)


def train_winning_model(cfg: Dict, df: pd.DataFrame):
    """Train the Phase 2.5 winning model on the FULL dataset."""
    df_feat = add_features(df, cfg["extra_features"])
    feature_names = RAW_FEATURES + list(cfg["extra_features"])
    X = df_feat[feature_names].values.astype(np.float32)
    y = df_feat["tension_strength"].values.astype(np.float32)
    params = dict(XGB_DEFAULT)
    params.update(cfg.get("xgb_params") or {})
    if cfg.get("monotone_constraints"):
        vec = [cfg["monotone_constraints"].get(f, 0) for f in feature_names]
        params["monotone_constraints"] = (
            "(" + ",".join(str(v) for v in vec) + ")")
    dtr = xgb.DMatrix(X, label=y)
    booster = xgb.train(params, dtr, num_boost_round=cfg.get("n_estimators", 300))
    return booster, feature_names


def featurize_candidate(mix: Dict[str, float], extra_features: List[str],
                        feature_names: List[str]) -> np.ndarray:
    """Compute the feature row for a single candidate mix."""
    df_single = pd.DataFrame([mix])
    df_feat = add_features(df_single, extra_features)
    return df_feat[feature_names].values.astype(np.float32)[0]


def main() -> None:
    df = load_dataset()
    cfg = json.loads((PROJECT_ROOT / "winning_config.json").read_text())
    print(f"Loaded winning config: {cfg['exp_id']} MAE={cfg['mae']:.4f}")
    print(f"  features: {cfg['extra_features']}")
    print(f"  monotone_constraints: {cfg['monotone_constraints']}")
    print(f"  n_estimators: {cfg['n_estimators']}")

    booster, feature_names = train_winning_model(cfg, df)
    print(f"  retrained on full dataset ({len(df)} samples)")

    candidates = generate_candidates()
    print(f"\nGenerated {len(candidates)} candidate FDM print settings "
          f"across {len(set(c['source'] for c in candidates))} strategies")

    rows = []
    for cand in candidates:
        feat = featurize_candidate(cand, cfg["extra_features"], feature_names)
        try:
            strength = float(booster.predict(xgb.DMatrix(feat.reshape(1, -1)))[0])
        except Exception:
            continue
        t_h = print_time_proxy(cand)
        e_kwh = energy_proxy(cand)
        rows.append({
            **cand,
            "predicted_strength": strength,
            "print_time_hours": t_h,
            "energy_kwh": e_kwh,
            "strength_per_hour": strength / t_h if t_h > 0 else 0.0,
            "strength_per_kwh": strength / e_kwh if e_kwh > 0 else 0.0,
        })

    cand_df = pd.DataFrame(rows)
    cand_df = cand_df[cand_df["predicted_strength"] > 0].copy()
    DISC_DIR.mkdir(exist_ok=True)
    cand_df.to_csv(DISC_DIR / "discovery_candidates.csv", index=False)

    pareto = pareto_front_strength_time(cand_df)
    pareto.to_csv(DISC_DIR / "discovery_pareto.csv", index=False)

    print(f"\nDiscovery results:")
    print(f"  total candidates: {len(cand_df)}")
    print(f"  Pareto front (strength vs print time): {len(pareto)}")
    print(f"  max strength : {cand_df['predicted_strength'].max():.2f} MPa")
    print(f"  min time     : {cand_df['print_time_hours'].min():.2f} hours")
    print(f"  best strength/hour: {cand_df['strength_per_hour'].max():.2f}")
    print(f"  best strength/kWh : {cand_df['strength_per_kwh'].max():.2f}")

    # Headline thresholds
    above_25 = cand_df[cand_df["predicted_strength"] >= 25]
    above_30 = cand_df[cand_df["predicted_strength"] >= 30]
    print(f"\n  candidates >= 25 MPa: {len(above_25)}, "
          f"min time = {above_25['print_time_hours'].min():.2f} h"
          if len(above_25) > 0 else
          f"\n  candidates >= 25 MPa: 0")
    print(f"  candidates >= 30 MPa: {len(above_30)}, "
          f"min time = {above_30['print_time_hours'].min():.2f} h"
          if len(above_30) > 0 else
          f"  candidates >= 30 MPa: 0")

    best_25 = None
    if len(above_25) > 0:
        best_25 = above_25.sort_values("print_time_hours").iloc[0]
        print(f"\n  Best >=25 MPa setting (fastest):")
        print(f"    layer_h={best_25['layer_height']}  "
              f"speed={best_25['print_speed']}  "
              f"T_nozzle={best_25['nozzle_temperature']}  "
              f"infill={best_25['infill_density']}  "
              f"walls={best_25['wall_thickness']}  "
              f"material={best_25['material']}")



        print(f"    strength = {best_25['predicted_strength']:.2f} MPa  "
              f"time = {best_25['print_time_hours']:.2f} h  "
              f"energy = {best_25['energy_kwh']:.3f} kWh")

    top5 = cand_df.sort_values("strength_per_hour", ascending=False).head(5)
    print(f"\n  Top 5 by strength/hour efficiency:")
    for _, r in top5.iterrows():
        print(f"    {r['predicted_strength']:5.2f} MPa  "
              f"{r['print_time_hours']:5.2f} h  "
              f"eff={r['strength_per_hour']:.2f}  ({r['source']})")

    summary = {
        "total_candidates": int(len(cand_df)),
        "pareto_size": int(len(pareto)),
        "max_strength": float(cand_df["predicted_strength"].max()),
        "min_time": float(cand_df["print_time_hours"].min()),
        "best_strength_per_hour": float(cand_df["strength_per_hour"].max()),
        "best_strength_per_kwh": float(cand_df["strength_per_kwh"].max()),
        "n_above_25_MPa": int(len(above_25)),
        "n_above_30_MPa": int(len(above_30)),
        "best_fast_25_MPa_setting":
            {k: (float(v) if isinstance(v, (int, float, np.floating, np.integer))
                 else str(v)) for k, v in best_25.to_dict().items()}
            if best_25 is not None else None,
        "top5_efficiency": [
            {k: (float(v) if isinstance(v, (int, float, np.floating, np.integer))
                 else str(v)) for k, v in r.items()}
            for r in top5.to_dict("records")],
    }
    (DISC_DIR / "discovery_summary.json").write_text(
        json.dumps(summary, indent=2, default=str))
    print(f"\nWrote discovery_candidates.csv, discovery_pareto.csv, "
          f"discovery_summary.json")


if __name__ == "__main__":
    main()
