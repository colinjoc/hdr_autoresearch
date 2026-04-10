"""
Phase 2 HDR loop runner for Iberian blackout cascade prediction.

Systematically tests hypotheses from research_queue.md.
Each experiment adds ONE feature or changes ONE configuration parameter,
evaluates, and decides KEEP or REVERT.

Usage:
    python run_phase2.py              # Run full Phase 2 loop
    python run_phase2.py --dry-run    # Show what would be tested without running
"""

from __future__ import annotations

import argparse
import csv
import copy
import sys
import time
from pathlib import Path

import numpy as np

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset
from evaluate import run_cv, run_holdout, TSV_HEADER, RESULTS_FILE

# Import model config as mutable module-level state
import model as M


def _write_result(row: dict) -> None:
    """Append a single result row to results.tsv."""
    file_exists = RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0
    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TSV_HEADER, delimiter="\t",
                                extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def run_experiment(df, exp_id: str, description: str, notes: str = "") -> dict:
    """Run one experiment and return results row."""
    config = M.get_model_config()
    t0 = time.time()

    cv = run_cv(df, n_folds=5)
    ho = run_holdout(df)

    elapsed = time.time() - t0

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": config["family"],
        "n_features": len(config["features"]),
        **cv,
        **ho,
        "notes": notes + f" ({elapsed:.1f}s)",
    }
    return row


def add_feature(feature_name: str) -> None:
    """Add a feature to the model's EXTRA_FEATURES list."""
    if feature_name not in M.EXTRA_FEATURES:
        M.EXTRA_FEATURES.append(feature_name)


def remove_feature(feature_name: str) -> None:
    """Remove a feature from the model's EXTRA_FEATURES list."""
    if feature_name in M.EXTRA_FEATURES:
        M.EXTRA_FEATURES.remove(feature_name)


def keep_or_revert(
    baseline_auc: float,
    new_auc: float,
    noise_floor: float = 0.005,
    exp_num: int = 0,
) -> str:
    """Decide KEEP or REVERT based on AUC improvement.

    Uses tightening thresholds per program.md:
    - Early (1-20): any positive delta above noise
    - Mid (20-50): delta > 2x noise
    - Late (50+): delta > 3x noise
    """
    delta = new_auc - baseline_auc

    if exp_num < 20:
        threshold = noise_floor
    elif exp_num < 50:
        threshold = 2 * noise_floor
    else:
        threshold = 3 * noise_floor

    if delta > threshold:
        return "KEEP"
    else:
        return "REVERT"


def main():
    parser = argparse.ArgumentParser(description="Phase 2 HDR Loop")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=" * 70)
    print("Phase 2: HDR Loop — Iberian Blackout Cascade Prediction")
    print("=" * 70)

    # Load data
    df = load_dataset()
    print(f"Dataset: {len(df)} rows, excursion rate: {df['freq_excursion'].mean():.4f}")

    # Define experiments in order
    # Format: (exp_id, description, action_type, action_params)
    experiments = [
        # --- Feature additions (highest prior first) ---
        ("H001", "Add SNSP feature", "add_feature", "snsp"),
        ("H002", "Add inertia proxy (MW*s)", "add_feature", "inertia_proxy_mws"),
        ("H022", "Add ramp-to-inertia ratio", "add_feature", "ramp_to_inertia_ratio"),
        ("H006", "Add total generation ramp (1h)", "add_feature", "total_ramp_1h_mw"),
        ("H015", "Add Spain-France flow", "add_feature", "flow_es_fr_mw"),
        ("H021", "Add gen-load imbalance", "add_feature", "gen_load_imbalance_mw"),
        ("H004", "Add wind ramp rate (1h)", "add_feature", "wind_ramp_1h_mw"),
        ("H005", "Add solar ramp rate (1h)", "add_feature", "solar_ramp_1h_mw"),
        ("H011", "Add SNSP delta 1h", "add_feature", "snsp_delta_1h"),
        ("H014", "Add inertia delta 1h", "add_feature", "inertia_delta_1h"),
        ("H017", "Add net import", "add_feature", "net_import_mw"),
        ("H074", "Add residual demand", "add_feature", "residual_demand_mw"),
        ("H003", "Add generation diversity (Shannon)", "add_feature", "gen_diversity_shannon"),
        ("H023", "Add synchronous fraction", "add_feature", "synchronous_fraction"),
        ("H020", "Add day-ahead price", "add_feature", "price_day_ahead_eur"),
        ("H018", "Add flow magnitude ratio", "add_feature", "flow_magnitude_ratio"),
        ("H016", "Add Spain-Portugal flow", "add_feature", "flow_es_pt_mw"),
        ("H043", "Add year as integer (already in base)", "skip", None),
        ("H008", "Add SNSP 1h lag", "add_feature", "snsp_lag_1h"),
        ("H009", "Add SNSP 6h lag", "add_feature", "snsp_lag_6h"),
        ("H013", "Add inertia 1h lag", "add_feature", "inertia_lag_1h"),
        ("H012", "Add SNSP delta 6h", "add_feature", "snsp_delta_6h"),
        ("H047", "Add SNSP rolling 6h mean", "add_feature", "snsp_rolling_6h_mean"),
        ("H048", "Add SNSP rolling 6h std", "add_feature", "snsp_rolling_6h_std"),
        ("H053", "Add inertia rolling 6h min", "add_feature", "inertia_rolling_6h_min"),
        ("H010", "Add SNSP 24h lag", "add_feature", "snsp_lag_24h"),
        ("H075", "Add residual demand ramp", "add_feature_computed", "residual_demand_ramp_1h"),
        ("H069", "Normalize by installed capacity", "skip", None),  # would require new column
        # --- Class imbalance ---
        ("H037", "Add class weight for imbalance", "set_param", ("scale_pos_weight", "auto")),
        # --- Model configuration ---
        ("H035", "Reduce max_depth to 4", "set_param", ("max_depth", 4)),
        ("H034", "Increase n_estimators to 600", "set_param", ("n_estimators", 600)),
        # --- Inertia-derived features ---
        ("H084", "Add expected RoCoF for largest contingency", "add_feature_computed", "expected_rocof"),
        ("H085", "Add inertia floor distance", "add_feature_computed", "inertia_floor_dist"),
        # --- Threshold features ---
        ("H029", "Add SNSP > 0.65 threshold", "add_feature_computed", "snsp_above_65pct"),
        ("H030", "Add SNSP > 0.75 threshold", "add_feature_computed", "snsp_above_75pct"),
        # --- Interaction features ---
        ("H027", "Add SNSP * inertia interaction", "add_feature_computed", "snsp_times_inertia"),
        ("H026", "Add SNSP squared", "add_feature_computed", "snsp_squared"),
        ("H044", "Add hour * SNSP interaction", "add_feature_computed", "hour_snsp"),
    ]

    # Track best AUC
    best_auc = 0.0
    best_config = []
    results_log = []
    exp_count = 0

    # Run baseline to establish best_auc
    print("\n--- Establishing baseline ---")
    M.EXTRA_FEATURES.clear()
    baseline_row = run_experiment(df, "E00-phase2", "Phase 2 baseline (base features only)")
    best_auc = baseline_row["cv_auc_mean"]
    _write_result(baseline_row)
    print(f"Baseline CV AUC: {best_auc:.4f}")

    if args.dry_run:
        print("\n--- DRY RUN: experiments that would be run ---")
        for exp_id, desc, action, param in experiments:
            print(f"  {exp_id}: {desc} [{action}] -> {param}")
        return

    # Run experiments
    for exp_id, desc, action, param in experiments:
        exp_count += 1
        print(f"\n{'='*60}")
        print(f"Experiment {exp_count}: {exp_id} — {desc}")
        print(f"{'='*60}")

        if action == "skip":
            print(f"  SKIPPED: {desc}")
            continue

        # Save current state
        saved_extra = M.EXTRA_FEATURES.copy()
        saved_xgb = M.XGBOOST_PARAMS.copy()

        try:
            if action == "add_feature":
                if param not in df.columns:
                    print(f"  SKIP: Feature '{param}' not in dataset")
                    continue
                add_feature(param)
                print(f"  Added feature: {param}")
                print(f"  Feature count: {len(M.get_feature_columns())}")

            elif action == "add_feature_computed":
                # Compute and add a derived feature
                if param == "residual_demand_ramp_1h":
                    if "residual_demand_ramp_1h" not in df.columns:
                        df["residual_demand_ramp_1h"] = df["residual_demand_mw"].diff(1)
                        df["residual_demand_ramp_1h"] = df["residual_demand_ramp_1h"].fillna(0)
                    add_feature("residual_demand_ramp_1h")
                elif param == "expected_rocof":
                    if "expected_rocof" not in df.columns:
                        # Largest single generator ~ nuclear (~6000 MW)
                        df["expected_rocof"] = 6000 / (2 * df["inertia_proxy_mws"].clip(lower=1))
                    add_feature("expected_rocof")
                elif param == "inertia_floor_dist":
                    if "inertia_floor_dist" not in df.columns:
                        df["inertia_floor_dist"] = df["inertia_proxy_s"] - 3.0
                    add_feature("inertia_floor_dist")
                elif param == "snsp_above_65pct":
                    if "snsp_above_65pct" not in df.columns:
                        df["snsp_above_65pct"] = (df["snsp"] > 0.65).astype(float)
                    add_feature("snsp_above_65pct")
                elif param == "snsp_above_75pct":
                    if "snsp_above_75pct" not in df.columns:
                        df["snsp_above_75pct"] = (df["snsp"] > 0.75).astype(float)
                    add_feature("snsp_above_75pct")
                elif param == "snsp_times_inertia":
                    if "snsp_times_inertia" not in df.columns:
                        df["snsp_times_inertia"] = df["snsp"] * df["inertia_proxy_s"]
                    add_feature("snsp_times_inertia")
                elif param == "snsp_squared":
                    if "snsp_squared" not in df.columns:
                        df["snsp_squared"] = df["snsp"] ** 2
                    add_feature("snsp_squared")
                elif param == "hour_snsp":
                    if "hour_snsp" not in df.columns:
                        df["hour_snsp"] = df["hour_sin"] * df["snsp"]
                    add_feature("hour_snsp")
                print(f"  Computed and added feature: {param}")

            elif action == "set_param":
                pname, pvalue = param
                if pname == "scale_pos_weight" and pvalue == "auto":
                    # Compute from class frequencies
                    neg = (df["freq_excursion"] == 0).sum()
                    pos = (df["freq_excursion"] == 1).sum()
                    pvalue = neg / max(pos, 1)
                    print(f"  Auto scale_pos_weight: {pvalue:.1f}")
                M.XGBOOST_PARAMS[pname] = pvalue
                print(f"  Set {pname} = {pvalue}")

            # Run evaluation
            row = run_experiment(df, exp_id, desc)
            new_auc = row["cv_auc_mean"]

            if np.isnan(new_auc):
                print(f"  REVERT: AUC is NaN")
                decision = "REVERT"
            else:
                decision = keep_or_revert(best_auc, new_auc, exp_num=exp_count)
                delta = new_auc - best_auc
                print(f"\n  Current best AUC: {best_auc:.4f}")
                print(f"  New AUC: {new_auc:.4f}")
                print(f"  Delta: {delta:+.4f}")
                print(f"  Decision: {decision}")

            row["notes"] = f"{decision} delta={new_auc - best_auc:+.4f} " + row.get("notes", "")
            _write_result(row)

            if decision == "KEEP":
                best_auc = new_auc
                best_config = M.EXTRA_FEATURES.copy()
                print(f"  New best AUC: {best_auc:.4f}")
                print(f"  Active extra features: {M.EXTRA_FEATURES}")
            else:
                # Revert
                M.EXTRA_FEATURES.clear()
                M.EXTRA_FEATURES.extend(saved_extra)
                M.XGBOOST_PARAMS.update(saved_xgb)
                print(f"  Reverted to: {M.EXTRA_FEATURES}")

            results_log.append({
                "exp_id": exp_id,
                "desc": desc,
                "new_auc": new_auc,
                "delta": new_auc - best_auc if decision == "REVERT" else 0,
                "decision": decision,
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            M.EXTRA_FEATURES.clear()
            M.EXTRA_FEATURES.extend(saved_extra)
            M.XGBOOST_PARAMS.update(saved_xgb)
            continue

    # Final summary
    print("\n" + "=" * 70)
    print("Phase 2 Summary")
    print("=" * 70)
    print(f"Experiments run: {exp_count}")
    print(f"Final best CV AUC: {best_auc:.4f}")
    print(f"Final extra features: {best_config}")
    kept = [r for r in results_log if r["decision"] == "KEEP"]
    reverted = [r for r in results_log if r["decision"] == "REVERT"]
    print(f"Kept: {len(kept)}, Reverted: {len(reverted)}")

    if kept:
        print("\nKept experiments:")
        for r in kept:
            print(f"  {r['exp_id']}: {r['desc']} (AUC={r['new_auc']:.4f})")

    # Final holdout evaluation with best config
    print("\n--- Final holdout evaluation ---")
    M.EXTRA_FEATURES.clear()
    M.EXTRA_FEATURES.extend(best_config)
    final_ho = run_holdout(df)
    print(f"\nFinal configuration:")
    print(f"  Model: {M.MODEL_FAMILY}")
    print(f"  Features: {M.get_feature_columns()}")
    print(f"  CV AUC: {best_auc:.4f}")
    print(f"  Holdout AUC: {final_ho['holdout_auc']}")
    print(f"  Blackout detected: {final_ho['blackout_day_predicted']}")


if __name__ == "__main__":
    main()
