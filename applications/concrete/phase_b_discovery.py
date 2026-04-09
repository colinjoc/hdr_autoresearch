"""
phase_b_discovery.py — Phase B: candidate generation + Pareto screening.

Loads the winning Phase 2.5 model from winning_config.json, retrains on
the FULL UCI Concrete dataset (not cross-validation), then generates
several thousand candidate mix designs across multiple strategies and
ranks them on three objectives:

  1. predicted compressive strength (megapascals)
  2. embodied carbon dioxide (kg CO₂ per cubic metre)
  3. cost (US dollars per cubic metre)

Computes the strength-vs-CO₂ Pareto front and writes:
  results/discovery_candidates.csv  — all generated candidates
  results/discovery_pareto.csv      — Pareto-optimal subset
  results/discovery_summary.json    — top-5 by efficiency, headline numbers
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import xgboost as xgb

from hdr_loop import (
    add_features, load_dataset, RAW_FEATURES, PROJECT_ROOT, XGB_DEFAULT,
)

DISC_DIR = PROJECT_ROOT / "discoveries"

# CO₂ emission factors (kg CO₂e per kg of ingredient) and cost ($/kg)
CO2_PER_KG = {
    "cement": 0.90, "slag": 0.07, "fly_ash": 0.01,
    "water": 0.001, "superplasticizer": 1.50,
    "coarse_agg": 0.005, "fine_agg": 0.005,
}
COST_PER_KG = {
    "cement": 0.15, "slag": 0.10, "fly_ash": 0.05,
    "water": 0.001, "superplasticizer": 3.00,
    "coarse_agg": 0.015, "fine_agg": 0.012,
}


def co2_per_m3(mix: Dict[str, float]) -> float:
    return sum(mix.get(k, 0) * v for k, v in CO2_PER_KG.items())


def cost_per_m3(mix: Dict[str, float]) -> float:
    return sum(mix.get(k, 0) * v for k, v in COST_PER_KG.items())


def train_winning_model(cfg: Dict, df: pd.DataFrame):
    """Train the Phase 2.5 winning XGBoost model on the FULL dataset."""
    df_feat = add_features(df, cfg["extra_features"])
    feature_names = RAW_FEATURES + list(cfg["extra_features"])
    X = df_feat[feature_names].values.astype(np.float32)
    y = df_feat["strength"].values.astype(np.float32)
    params = dict(XGB_DEFAULT)
    params.update(cfg.get("xgb_params") or {})
    if cfg.get("monotone_constraints"):
        vec = [cfg["monotone_constraints"].get(f, 0) for f in feature_names]
        params["monotone_constraints"] = "(" + ",".join(str(v) for v in vec) + ")"
    dtr = xgb.DMatrix(X, label=y)
    booster = xgb.train(params, dtr, num_boost_round=cfg.get("n_estimators", 300))
    return booster, feature_names


def featurize_candidate(mix: Dict[str, float], extra_features: List[str], feature_names: List[str]) -> np.ndarray:
    """Compute the full feature row for a single candidate mix."""
    binder = mix["cement"] + mix["slag"] + mix["fly_ash"]
    derived = {}
    if "log_age" in extra_features:
        derived["log_age"] = np.log1p(mix["age"])
    if "wb_ratio" in extra_features:
        derived["wb_ratio"] = mix["water"] / binder if binder > 0 else 0.0
    if "scm_pct" in extra_features:
        derived["scm_pct"] = (mix["slag"] + mix["fly_ash"]) / binder if binder > 0 else 0.0
    if "binder_total" in extra_features:
        derived["binder_total"] = binder
    if "agg_total" in extra_features:
        derived["agg_total"] = mix["coarse_agg"] + mix["fine_agg"]
    if "fine_frac" in extra_features:
        total = mix["coarse_agg"] + mix["fine_agg"]
        derived["fine_frac"] = mix["fine_agg"] / total if total > 0 else 0.0
    if "sp_per_binder" in extra_features:
        derived["sp_per_binder"] = mix["superplasticizer"] / binder if binder > 0 else 0.0
    if "cement_per_water" in extra_features:
        derived["cement_per_water"] = mix["cement"] / mix["water"] if mix["water"] > 0 else 0.0
    if "log_cement" in extra_features:
        derived["log_cement"] = np.log1p(mix["cement"])
    if "log_water" in extra_features:
        derived["log_water"] = np.log1p(mix["water"])
    if "slag_pct" in extra_features:
        derived["slag_pct"] = mix["slag"] / binder if binder > 0 else 0.0
    if "fa_pct" in extra_features:
        derived["fa_pct"] = mix["fly_ash"] / binder if binder > 0 else 0.0
    if "age_inv" in extra_features:
        derived["age_inv"] = 1.0 / (mix["age"] + 1.0)
    if "cement_x_age" in extra_features:
        derived["cement_x_age"] = mix["cement"] * np.log1p(mix["age"])
    if "wb_x_age" in extra_features:
        wb = mix["water"] / binder if binder > 0 else 0.0
        derived["wb_x_age"] = wb * np.log1p(mix["age"])

    full = {**mix, **derived}
    return np.array([full[f] for f in feature_names], dtype=np.float32)


# ---------------------------------------------------------------------------
# Candidate generation strategies
# ---------------------------------------------------------------------------

def generate_candidates() -> List[Dict[str, float]]:
    """Eleven candidate-generation strategies, ranging from systematic
    grids to physics-informed sampling. Returns a list of mix dicts.
    """
    candidates: List[Dict[str, float]] = []

    # Strategy 1: dense grid on the four primary variables (cement, slag, fly_ash, water)
    for c in [80, 100, 120, 150, 180, 200, 230, 260, 300, 350, 400, 450, 500]:
        for s in [0, 50, 100, 150, 180, 200, 250]:
            for fa in [0, 50, 100, 150, 200]:
                for w in [140, 160, 180, 200]:
                    candidates.append({
                        "cement": c, "slag": s, "fly_ash": fa, "water": w,
                        "superplasticizer": 8, "coarse_agg": 950, "fine_agg": 700,
                        "age": 28, "source": "grid_28d",
                    })

    # Strategy 2: same grid at 56-day curing (relaxed strength target)
    for c in [80, 100, 120, 150, 180, 200, 230, 260, 300, 400]:
        for s in [50, 100, 150, 180, 200]:
            for fa in [0, 50, 100, 150]:
                for w in [140, 160, 180]:
                    candidates.append({
                        "cement": c, "slag": s, "fly_ash": fa, "water": w,
                        "superplasticizer": 10, "coarse_agg": 950, "fine_agg": 700,
                        "age": 56, "source": "grid_56d",
                    })

    # Strategy 3: 90-day curing for ultra-high SCM mixes
    for c in [60, 80, 100, 120, 150, 180, 200]:
        for s in [100, 150, 200, 250, 300]:
            for fa in [0, 50, 100, 150]:
                candidates.append({
                    "cement": c, "slag": s, "fly_ash": fa, "water": 160,
                    "superplasticizer": 12, "coarse_agg": 950, "fine_agg": 700,
                    "age": 90, "source": "grid_90d",
                })

    # Strategy 4: pure-cement sweep (high strength, high CO₂)
    for c in [350, 380, 400, 420, 450, 480, 500, 540]:
        for w in [130, 140, 150, 160, 170]:
            for sp in [5, 10, 15, 20]:
                candidates.append({
                    "cement": c, "slag": 0, "fly_ash": 0, "water": w,
                    "superplasticizer": sp, "coarse_agg": 1000, "fine_agg": 750,
                    "age": 28, "source": "high_strength",
                })

    # Strategy 5: cement+slag binary sweep at multiple ages
    for c in [80, 100, 120, 150, 200, 250, 300]:
        for s in [50, 100, 150, 200, 250]:
            for age in [28, 56, 90]:
                candidates.append({
                    "cement": c, "slag": s, "fly_ash": 0, "water": 160,
                    "superplasticizer": 10, "coarse_agg": 950, "fine_agg": 700,
                    "age": age, "source": "cement_slag_binary",
                })

    # Strategy 6: cement+fly_ash binary sweep at multiple ages
    for c in [100, 120, 150, 180, 200, 250, 300]:
        for fa in [50, 100, 150, 200]:
            for age in [28, 56, 90]:
                candidates.append({
                    "cement": c, "slag": 0, "fly_ash": fa, "water": 160,
                    "superplasticizer": 10, "coarse_agg": 950, "fine_agg": 700,
                    "age": age, "source": "cement_fa_binary",
                })

    # Strategy 7: ternary blends (cement+slag+fly_ash)
    for c in [100, 150, 200, 250]:
        for s in [50, 100, 150]:
            for fa in [50, 100, 150]:
                for age in [28, 56]:
                    candidates.append({
                        "cement": c, "slag": s, "fly_ash": fa, "water": 160,
                        "superplasticizer": 10, "coarse_agg": 950, "fine_agg": 700,
                        "age": age, "source": "ternary",
                    })

    # Strategy 8: low-water (high-strength) variants
    for c in [200, 250, 300, 350]:
        for s in [50, 100, 150]:
            for w in [120, 130, 140, 150]:
                candidates.append({
                    "cement": c, "slag": s, "fly_ash": 0, "water": w,
                    "superplasticizer": 15, "coarse_agg": 1000, "fine_agg": 750,
                    "age": 28, "source": "low_water",
                })

    # Strategy 9: ultra-low-cement variants pushed to extreme
    for c in [40, 60, 80, 100]:
        for s in [150, 200, 250, 300, 350]:
            for fa in [0, 50, 100]:
                for age in [56, 90]:
                    candidates.append({
                        "cement": c, "slag": s, "fly_ash": fa, "water": 160,
                        "superplasticizer": 12, "coarse_agg": 950, "fine_agg": 700,
                        "age": age, "source": "ultra_low_cement",
                    })

    # Strategy 10: aggregate variants (test fine/coarse ratios)
    for c in [200, 300, 400]:
        for fine in [600, 700, 800, 900]:
            for coarse in [800, 950, 1100]:
                candidates.append({
                    "cement": c, "slag": 100, "fly_ash": 0, "water": 160,
                    "superplasticizer": 10, "coarse_agg": coarse, "fine_agg": fine,
                    "age": 28, "source": "agg_ratio",
                })

    # Strategy 11: Latin-hypercube-style stratified random
    rng = np.random.default_rng(2026)
    for _ in range(500):
        c = float(rng.uniform(80, 500))
        s = float(rng.uniform(0, 250))
        fa = float(rng.uniform(0, 200))
        w = float(rng.uniform(130, 200))
        sp = float(rng.uniform(0, 20))
        coarse = float(rng.uniform(800, 1100))
        fine = float(rng.uniform(600, 900))
        age = int(rng.choice([28, 56, 90]))
        candidates.append({
            "cement": c, "slag": s, "fly_ash": fa, "water": w,
            "superplasticizer": sp, "coarse_agg": coarse, "fine_agg": fine,
            "age": age, "source": "lhs_random",
        })

    return candidates


def pareto_front_strength_co2(df: pd.DataFrame) -> pd.DataFrame:
    """Strength-vs-CO₂ Pareto front (maximise strength, minimise CO₂)."""
    rows = df.sort_values("co2_kg_per_m3").reset_index(drop=True)
    front = []
    best_strength = -np.inf
    for _, row in rows.iterrows():
        if row["predicted_strength"] > best_strength:
            front.append(row)
            best_strength = row["predicted_strength"]
    return pd.DataFrame(front)


def main():
    df = load_dataset()
    cfg = json.loads((PROJECT_ROOT / "winning_config.json").read_text())
    print(f"Loaded winning config: {cfg['exp_id']} MAE={cfg['mae']:.4f}")
    print(f"  features: {cfg['extra_features']}")
    print(f"  monotone_constraints: {cfg['monotone_constraints']}")
    print(f"  n_estimators: {cfg['n_estimators']}")

    booster, feature_names = train_winning_model(cfg, df)
    print(f"  retrained on full dataset ({len(df)} samples)")

    candidates = generate_candidates()
    print(f"\nGenerated {len(candidates)} candidate mix designs across "
          f"{len(set(c['source'] for c in candidates))} strategies")

    rows = []
    for cand in candidates:
        feat = featurize_candidate(cand, cfg["extra_features"], feature_names)
        try:
            strength = float(booster.predict(xgb.DMatrix(feat.reshape(1, -1)))[0])
        except Exception:
            continue
        co2 = co2_per_m3(cand)
        cost = cost_per_m3(cand)
        rows.append({
            **cand,
            "predicted_strength": strength,
            "co2_kg_per_m3": co2,
            "cost_usd_per_m3": cost,
            "strength_per_co2": strength / co2 if co2 > 0 else 0,
        })

    cand_df = pd.DataFrame(rows)
    cand_df = cand_df[cand_df["predicted_strength"] > 0]
    DISC_DIR.mkdir(exist_ok=True)
    cand_df.to_csv(DISC_DIR / "discovery_candidates.csv", index=False)

    pareto = pareto_front_strength_co2(cand_df)
    pareto.to_csv(DISC_DIR / "discovery_pareto.csv", index=False)

    print(f"\nDiscovery results:")
    print(f"  total candidates: {len(cand_df)}")
    print(f"  pareto front: {len(pareto)}")
    print(f"  max strength: {cand_df['predicted_strength'].max():.1f} MPa")
    print(f"  min CO2: {cand_df['co2_kg_per_m3'].min():.1f} kg/m³")
    print(f"  best efficiency: {cand_df['strength_per_co2'].max():.3f} MPa per kg CO2")

    # Find specific reference points
    above_40 = cand_df[cand_df["predicted_strength"] >= 40]
    above_50 = cand_df[cand_df["predicted_strength"] >= 50]
    print(f"\n  candidates >=40 MPa: {len(above_40)}, min CO2 = {above_40['co2_kg_per_m3'].min():.1f}")
    print(f"  candidates >=50 MPa: {len(above_50)}, min CO2 = {above_50['co2_kg_per_m3'].min():.1f}")

    if len(above_50) > 0:
        best50 = above_50.sort_values("co2_kg_per_m3").iloc[0]
        print(f"\n  Best ≥50 MPa mix:")
        print(f"    cement={best50['cement']:.0f}, slag={best50['slag']:.0f}, "
              f"fly_ash={best50['fly_ash']:.0f}, water={best50['water']:.0f}, "
              f"age={best50['age']:.0f}d")
        print(f"    strength={best50['predicted_strength']:.1f} MPa  "
              f"CO2={best50['co2_kg_per_m3']:.1f} kg/m³  cost=${best50['cost_usd_per_m3']:.0f}/m³")

    # Top 5 by efficiency
    top5 = cand_df.sort_values("strength_per_co2", ascending=False).head(5)
    print(f"\n  Top 5 by strength/CO2 efficiency:")
    for _, r in top5.iterrows():
        print(f"    {r['predicted_strength']:5.1f} MPa  {r['co2_kg_per_m3']:5.1f} kg CO2  "
              f"eff={r['strength_per_co2']:.3f}  ({r['source']})")

    summary = {
        "total_candidates": int(len(cand_df)),
        "pareto_size": int(len(pareto)),
        "max_strength": float(cand_df["predicted_strength"].max()),
        "min_co2": float(cand_df["co2_kg_per_m3"].min()),
        "best_efficiency": float(cand_df["strength_per_co2"].max()),
        "n_above_50_MPa": int(len(above_50)),
        "min_co2_above_50_MPa": float(above_50["co2_kg_per_m3"].min()) if len(above_50) > 0 else None,
        "best_50_MPa_mix": best50.to_dict() if len(above_50) > 0 else None,
        "top5_efficiency": top5.to_dict("records"),
    }
    (DISC_DIR / "discovery_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote discovery_candidates.csv, discovery_pareto.csv, discovery_summary.json")


if __name__ == "__main__":
    main()
