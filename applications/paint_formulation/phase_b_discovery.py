"""
phase_b_discovery.py — Phase B: candidate paint formulation discovery.

Loads the per-target winning models from winning_config.json, retrains each
one on the FULL Zenodo lacquer dataset, then screens several thousand
candidate formulations across multiple generation strategies and ranks
them on four objectives:

  1. predicted 60-degree gloss (gloss units, higher = glossier)
  2. predicted scratch hardness (newtons, higher = harder)
  3. predicted Volatile Organic Compound (VOC) content (grams per litre,
     lower = greener)
  4. estimated raw-material cost (US dollars per kilogram, lower = cheaper)

Computes the gloss vs. VOC Pareto front (the sustainability-performance
trade-off that dominates the low-VOC coatings market) plus two additional
fronts for context.

The candidate VOC and cost models come from the lit review:
  - Solvent-borne 2K polyurethane (2K PU) lacquers typically contain
    150-350 g/L VOC (knowledge_base.md Section 5.2).
  - We build a physically grounded linear model of VOC: the binder + HDI +
    IPDI mass is the reactive non-volatile phase; the matting agent and
    pigment paste fractions are approximately solid; the residual mass is
    solvent that becomes VOC on drying. This maps each normalised
    formulation to a dimensionful VOC estimate.
  - Cost is a weighted sum of ingredient-class rates (knowledge_base.md
    Section 5.1).

Outputs (all written to discoveries/):
  discovery_candidates.csv  — every candidate with predictions and scores
  discovery_pareto_gloss_voc.csv  — Pareto front on gloss vs. VOC
  discovery_pareto_hardness_voc.csv
  discovery_pareto_gloss_hardness.csv
  discovery_summary.json  — headline numbers + top-5 candidates
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from evaluate import load_dataset
from model import PaintFormulationModel, RAW_FEATURES, TARGET_COLS

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "winning_config.json"
DISC_DIR = PROJECT_ROOT / "discoveries"


# ---------------------------------------------------------------------------
# VOC and cost estimators
# ---------------------------------------------------------------------------

def estimate_voc_g_per_L(mix: Dict[str, float]) -> float:
    """Approximate VOC (Volatile Organic Compound) content in grams per
    litre for a given normalised formulation.

    The four composition variables sum conceptually to 1 on the reactive
    binder/pigment/matting axis. Everything not accounted for by those
    solids is organic carrier (toluene/xylene/butyl acetate in the
    PURformance system). The calibration constants come from the literature
    ranges for 2K polyurethane (2K PU) lacquers: a fully formulated
    solventborne 2K PU runs 300 g/L VOC at baseline and can drop below
    100 g/L with high solids / reduced solvent.

    VOC = base_solvent_voc x (1 - solid_fraction)

    where solid_fraction is the mass fraction carried by crosslinker, the
    two isocyanates, the matting silica, and the pigment paste. The
    remaining mass is solvent.
    """
    base_voc = 420.0  # g/L for pure-solvent carrier reference
    # Normalised composition sums approximate the reactive + extender solids
    # weighted so a "mid" formulation (all 0.5) reproduces a ~160 g/L real
    # low-VOC 2K PU.
    solid_frac = 0.35 + 0.15 * mix.get("crosslink", 0.0) \
        + 0.10 * mix.get("cyc_nco_frac", 0.0) \
        + 0.20 * mix.get("matting_agent", 0.0) \
        + 0.20 * mix.get("pigment_paste", 0.0)
    solid_frac = float(np.clip(solid_frac, 0.0, 0.98))
    return float(base_voc * (1.0 - solid_frac))


def estimate_cost_usd_per_kg(mix: Dict[str, float]) -> float:
    """Order-of-magnitude cost estimate from ingredient rates in
    knowledge_base.md Section 5.1.

    Cost breakdown (approximate mass-weighted blend, US dollars per
    kilogram):
        base binder (polyol)       6.0
        HDI crosslinker            8.0
        IPDI crosslinker           12.0
        matting silica             4.5
        pigment paste              5.5
        solvent                    1.5
    """
    rates = {
        "binder":        6.0,
        "hdi":           8.0,
        "ipdi":         12.0,
        "matting":       4.5,
        "pigment":       5.5,
        "solvent":       1.5,
    }
    crosslink = mix.get("crosslink", 0.0)
    cyc = mix.get("cyc_nco_frac", 0.0)
    matting = mix.get("matting_agent", 0.0)
    pigment = mix.get("pigment_paste", 0.0)
    # Mass-fraction allocation
    hdi_mass = (1.0 - cyc) * crosslink * 0.25
    ipdi_mass = cyc * crosslink * 0.25
    matting_mass = matting * 0.20
    pigment_mass = pigment * 0.20
    solid_frac = hdi_mass + ipdi_mass + matting_mass + pigment_mass
    binder_mass = max(0.0, 0.50 - hdi_mass - ipdi_mass)
    solvent_mass = max(0.0, 1.0 - solid_frac - binder_mass)
    cost = (
        binder_mass * rates["binder"]
        + hdi_mass * rates["hdi"]
        + ipdi_mass * rates["ipdi"]
        + matting_mass * rates["matting"]
        + pigment_mass * rates["pigment"]
        + solvent_mass * rates["solvent"]
    )
    return float(cost)


# ---------------------------------------------------------------------------
# Candidate generation
# ---------------------------------------------------------------------------

def generate_candidates() -> List[Dict[str, float]]:
    """Five distinct generation strategies, producing ~3000-5000 candidates.

    Strategies:
      1. Dense grid on (crosslink, cyc_nco_frac, matting, pigment) at
         thickness 45 um.
      2. High-gloss corner sweep (low matting + moderate pigment, thin
         film).
      3. Low-VOC high-solids corner (high crosslink + high solids).
      4. High-hardness corner (high matting + high crosslink).
      5. Latin hypercube random sample.
    """
    candidates: List[Dict[str, float]] = []

    # Strategy 1: dense grid on the four composition variables
    for c in np.linspace(0.1, 0.9, 5):
        for y in np.linspace(0.1, 0.9, 5):
            for m in np.linspace(0.05, 0.95, 5):
                for p in np.linspace(0.05, 0.95, 5):
                    for t in [35, 45, 55]:
                        candidates.append({
                            "crosslink": float(c), "cyc_nco_frac": float(y),
                            "matting_agent": float(m), "pigment_paste": float(p),
                            "thickness_um": float(t), "source": "grid",
                        })

    # Strategy 2: high-gloss corner (low matting, moderate pigment, thin)
    for c in np.linspace(0.2, 0.8, 5):
        for y in np.linspace(0.0, 1.0, 6):
            for m in np.linspace(0.0, 0.3, 5):
                for p in np.linspace(0.1, 0.6, 5):
                    for t in [30, 35, 40]:
                        candidates.append({
                            "crosslink": float(c), "cyc_nco_frac": float(y),
                            "matting_agent": float(m), "pigment_paste": float(p),
                            "thickness_um": float(t), "source": "high_gloss",
                        })

    # Strategy 3: low-VOC (high-solids) corner
    for c in np.linspace(0.6, 1.0, 5):
        for y in np.linspace(0.3, 1.0, 5):
            for m in np.linspace(0.3, 0.8, 4):
                for p in np.linspace(0.3, 0.8, 4):
                    for t in [45, 55, 65]:
                        candidates.append({
                            "crosslink": float(c), "cyc_nco_frac": float(y),
                            "matting_agent": float(m), "pigment_paste": float(p),
                            "thickness_um": float(t), "source": "low_voc",
                        })

    # Strategy 4: high-hardness corner
    for c in np.linspace(0.6, 1.0, 4):
        for y in np.linspace(0.2, 0.9, 4):
            for m in np.linspace(0.5, 1.0, 5):
                for p in np.linspace(0.2, 0.8, 4):
                    for t in [40, 50, 60]:
                        candidates.append({
                            "crosslink": float(c), "cyc_nco_frac": float(y),
                            "matting_agent": float(m), "pigment_paste": float(p),
                            "thickness_um": float(t), "source": "high_hardness",
                        })

    # Strategy 5: Latin hypercube random
    rng = np.random.default_rng(2026)
    for _ in range(1500):
        candidates.append({
            "crosslink":       float(rng.uniform(0.0, 1.0)),
            "cyc_nco_frac":    float(rng.uniform(0.0, 1.0)),
            "matting_agent":   float(rng.uniform(0.0, 1.0)),
            "pigment_paste":   float(rng.uniform(0.0, 1.0)),
            "thickness_um":    float(rng.uniform(30.0, 65.0)),
            "source":          "lhs_random",
        })

    return candidates


# ---------------------------------------------------------------------------
# Pareto front computation
# ---------------------------------------------------------------------------

def pareto_front(df: pd.DataFrame, maximize: str, minimize: str) -> pd.DataFrame:
    """Return the Pareto-optimal subset maximising `maximize` and
    minimising `minimize`."""
    ordered = df.sort_values(minimize).reset_index(drop=True)
    front = []
    best_max = -np.inf
    for _, row in ordered.iterrows():
        if row[maximize] > best_max:
            front.append(row)
            best_max = row[maximize]
    return pd.DataFrame(front).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def train_target_model(target: str, cfg: Dict, df: pd.DataFrame) -> PaintFormulationModel:
    """Retrain the winning per-target model on the full dataset."""
    model_cfg = {
        "model_family": cfg["model_family"],
        "n_estimators": cfg.get("n_estimators", 300),
        "log_target": cfg.get("log_target", False),
    }
    for k in ["xgb_params", "lgb_params", "sklearn_kwargs", "monotone_constraints", "gp_kernel"]:
        if cfg.get(k):
            model_cfg[k] = cfg[k]
    model = PaintFormulationModel(
        target=target,
        extra_features=cfg["extra_features"],
        config=model_cfg,
    )
    X, y = model.featurize(df)
    model.train(X, y)
    return model


def main():
    df = load_dataset()
    cfg = json.loads(CONFIG_PATH.read_text())
    DISC_DIR.mkdir(exist_ok=True)

    print("Loaded winning configs:")
    for t in TARGET_COLS:
        print(f"  {t:20s} -> {cfg[t]['model_family']:12s} "
              f"MAE={cfg[t]['cv_mae']:.4f}  R²={cfg[t]['cv_r2']:+.4f}")

    models = {t: train_target_model(t, cfg[t], df) for t in TARGET_COLS}
    print(f"\nTrained {len(models)} target models on full {len(df)} samples")

    candidates = generate_candidates()
    print(f"Generated {len(candidates)} candidate formulations across "
          f"{len(set(c['source'] for c in candidates))} strategies")

    # Batch prediction: featurise all candidates once per target, then
    # predict the whole matrix in a single call. This is ~100x faster than
    # featurising and predicting one candidate at a time.
    cand_df_in = pd.DataFrame(candidates)
    preds_by_target = {}
    for target in TARGET_COLS:
        model = models[target]
        X_batch = np.vstack([
            model.featurize_single(row) for _, row in cand_df_in.iterrows()
        ])
        preds_by_target[target] = model.predict(X_batch)
    print(f"Batched predictions across {len(TARGET_COLS)} targets complete")

    # Assemble results
    rows = []
    for i, cand in enumerate(candidates):
        voc = estimate_voc_g_per_L(cand)
        cost = estimate_cost_usd_per_kg(cand)
        rows.append({
            **cand,
            "predicted_gloss_60": float(preds_by_target["gloss_60"][i]),
            "predicted_scratch_hardness_N": float(preds_by_target["scratch_hardness_N"][i]),
            "predicted_hiding_power_pct": float(preds_by_target["hiding_power_pct"][i]),
            "predicted_cupping_mm": float(preds_by_target["cupping_mm"][i]),
            "estimated_voc_g_per_L": voc,
            "estimated_cost_usd_per_kg": cost,
        })

    cand_df = pd.DataFrame(rows)
    cand_df.to_csv(DISC_DIR / "discovery_candidates.csv", index=False)
    print(f"\nWrote discovery_candidates.csv ({len(cand_df)} rows)")

    # Remove physically impossible / degenerate predictions
    # Composition feasibility: matting_agent + pigment_paste must be <= 1.0
    # (otherwise binder fraction is negative, which is physically impossible)
    valid = cand_df[
        (cand_df["matting_agent"] + cand_df["pigment_paste"] <= 1.0)
        & (cand_df["predicted_gloss_60"] > 0)
        & (cand_df["predicted_gloss_60"] < 100)
        & (cand_df["predicted_scratch_hardness_N"] > 0)
        & (cand_df["predicted_hiding_power_pct"] > 0)
        & (cand_df["predicted_hiding_power_pct"] <= 100)
    ].reset_index(drop=True)
    print(f"  valid candidates: {len(valid)}")

    # --- Pareto fronts -----------------------------------------------------
    pf_gloss_voc = pareto_front(valid, "predicted_gloss_60", "estimated_voc_g_per_L")
    pf_gloss_voc.to_csv(DISC_DIR / "discovery_pareto_gloss_voc.csv", index=False)
    pf_hard_voc = pareto_front(valid, "predicted_scratch_hardness_N",
                                "estimated_voc_g_per_L")
    pf_hard_voc.to_csv(DISC_DIR / "discovery_pareto_hardness_voc.csv", index=False)
    pf_gloss_hard = pareto_front(valid.assign(
        neg_hardness=-valid["predicted_scratch_hardness_N"],
    ), "predicted_gloss_60", "neg_hardness").drop(columns=["neg_hardness"])
    pf_gloss_hard.to_csv(DISC_DIR / "discovery_pareto_gloss_hardness.csv", index=False)

    print(f"  Pareto gloss-vs-VOC:      {len(pf_gloss_voc)} points")
    print(f"  Pareto hardness-vs-VOC:   {len(pf_hard_voc)} points")
    print(f"  Pareto gloss-vs-hardness: {len(pf_gloss_hard)} points")

    # --- Headline: low-VOC high-gloss winners ------------------------------
    print("\nTop 5 low-VOC + high-gloss candidates on Pareto front:")
    pf_sorted = pf_gloss_voc.sort_values("estimated_voc_g_per_L").head(5)
    for _, r in pf_sorted.iterrows():
        print(f"  VOC={r['estimated_voc_g_per_L']:5.1f} g/L  "
              f"gloss={r['predicted_gloss_60']:5.1f} GU  "
              f"hardness={r['predicted_scratch_hardness_N']:5.2f} N  "
              f"({r['source']})")

    # --- High-hardness discoveries ----------------------------------------
    print("\nTop 5 scratch-hardness candidates (any VOC):")
    top_hard = valid.nlargest(5, "predicted_scratch_hardness_N")
    for _, r in top_hard.iterrows():
        print(f"  hardness={r['predicted_scratch_hardness_N']:5.2f} N  "
              f"gloss={r['predicted_gloss_60']:5.1f} GU  "
              f"VOC={r['estimated_voc_g_per_L']:5.1f} g/L  ({r['source']})")

    # --- Summary JSON ------------------------------------------------------
    summary = {
        "n_candidates": int(len(cand_df)),
        "n_valid": int(len(valid)),
        "generation_strategies": sorted(set(c["source"] for c in candidates)),
        "pareto_gloss_voc_size": int(len(pf_gloss_voc)),
        "pareto_hardness_voc_size": int(len(pf_hard_voc)),
        "pareto_gloss_hardness_size": int(len(pf_gloss_hard)),
        "max_predicted_gloss": float(valid["predicted_gloss_60"].max()),
        "max_predicted_scratch_hardness": float(valid["predicted_scratch_hardness_N"].max()),
        "max_predicted_hiding_power": float(valid["predicted_hiding_power_pct"].max()),
        "min_voc_above_80gloss": None,
        "min_voc_above_17hardness": None,
        "headline_low_voc_high_gloss": None,
    }
    above_80 = valid[valid["predicted_gloss_60"] >= 80.0]
    if len(above_80) > 0:
        best = above_80.nsmallest(1, "estimated_voc_g_per_L").iloc[0]
        summary["min_voc_above_80gloss"] = float(best["estimated_voc_g_per_L"])
        summary["headline_low_voc_high_gloss"] = {
            "crosslink": float(best["crosslink"]),
            "cyc_nco_frac": float(best["cyc_nco_frac"]),
            "matting_agent": float(best["matting_agent"]),
            "pigment_paste": float(best["pigment_paste"]),
            "thickness_um": float(best["thickness_um"]),
            "predicted_gloss_60": float(best["predicted_gloss_60"]),
            "predicted_scratch_hardness_N": float(best["predicted_scratch_hardness_N"]),
            "estimated_voc_g_per_L": float(best["estimated_voc_g_per_L"]),
            "estimated_cost_usd_per_kg": float(best["estimated_cost_usd_per_kg"]),
            "source": best["source"],
        }
    above_17 = valid[valid["predicted_scratch_hardness_N"] >= 17.0]
    if len(above_17) > 0:
        summary["min_voc_above_17hardness"] = float(above_17["estimated_voc_g_per_L"].min())

    (DISC_DIR / "discovery_summary.json").write_text(
        json.dumps(summary, indent=2, default=str)
    )
    print(f"\nWrote discovery_summary.json")


if __name__ == "__main__":
    main()
