"""
Phase 2 HDR Loop Runner for Irish Radon Prediction.

Runs a series of pre-registered single-change experiments, each modifying
model.py's feature set or model configuration and evaluating with spatial CV.

Usage:
    python run_phase2.py
"""

from __future__ import annotations

import csv
import importlib
import sys
import time
from pathlib import Path

import numpy as np

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset
from evaluate import run_cv, run_holdout, _write_results, compute_metrics

RESULTS_FILE = APP_DIR / "results.tsv"


def reload_model():
    """Reload model module to pick up changes."""
    import model
    importlib.reload(model)
    return model


def run_experiment(df, exp_id, description, model_mod, notes=""):
    """Run a single experiment and return results row."""
    print(f"\n{'='*60}")
    print(f"Experiment {exp_id}: {description}")
    print(f"{'='*60}")

    features = model_mod.get_feature_columns()
    print(f"  Model: {model_mod.MODEL_FAMILY}")
    print(f"  Features ({len(features)}): {features}")

    t0 = time.time()

    cv_results = run_cv(df, n_folds=5, model_family=model_mod.MODEL_FAMILY)
    holdout_results = run_holdout(df, model_family=model_mod.MODEL_FAMILY)

    elapsed = time.time() - t0

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": model_mod.MODEL_FAMILY,
        "n_features": len(features),
        **cv_results,
        **holdout_results,
        "notes": notes + f" ({elapsed:.1f}s)",
    }

    print(f"\n  >>> CV AUC: {cv_results['cv_auc_mean']:.4f} +/- {cv_results['cv_auc_std']:.4f}")
    print(f"  >>> CV F1:  {cv_results['cv_f1_mean']:.4f}")

    return row


def main():
    print("Loading dataset...")
    df = load_dataset()
    print(f"  {len(df)} areas, HRA prevalence: {df['is_hra'].mean()*100:.1f}%")

    all_rows = []
    best_auc = 0.5909  # E00 baseline

    # ====================================================================
    # Experiment E01: Add eU/eTh ratio
    # Prior: 65% (strong literature support)
    # ====================================================================
    import model
    model.EXTRA_FEATURES.clear()
    model.EXTRA_CATEGORICAL.clear()
    model.EXTRA_FEATURES.append("eU_eTh_ratio")
    row = run_experiment(df, "E01", "Add eU/eTh ratio (uranium enrichment indicator)", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("eU_eTh_ratio")
    all_rows.append(row)

    # ====================================================================
    # Experiment E02: Add total_dose_rate
    # Prior: 30%
    # ====================================================================
    model.EXTRA_FEATURES.append("total_dose_rate")
    row = run_experiment(df, "E02", "Add total dose rate (composite radiometric)", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("total_dose_rate")
    all_rows.append(row)

    # ====================================================================
    # Experiment E03: Add log_eU
    # Prior: 50%
    # ====================================================================
    model.EXTRA_FEATURES.append("log_eU")
    row = run_experiment(df, "E03", "Add log(eU) transform", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("log_eU")
    all_rows.append(row)

    # ====================================================================
    # Experiment E04: Add quat_permeability ordinal
    # Prior: 55%
    # ====================================================================
    model.EXTRA_FEATURES.append("quat_permeability")
    row = run_experiment(df, "E04", "Add quaternary permeability ordinal", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("quat_permeability")
    all_rows.append(row)

    # ====================================================================
    # Experiment E05: Add is_granite indicator
    # Prior: 45%
    # ====================================================================
    model.EXTRA_FEATURES.append("is_granite")
    row = run_experiment(df, "E05", "Add is_granite binary indicator", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("is_granite")
    all_rows.append(row)

    # ====================================================================
    # Experiment E06: Add is_limestone indicator
    # Prior: 45%
    # ====================================================================
    model.EXTRA_FEATURES.append("is_limestone")
    row = run_experiment(df, "E06", "Add is_limestone binary indicator", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("is_limestone")
    all_rows.append(row)

    # ====================================================================
    # Experiment E07: Add is_shale indicator
    # Prior: 40%
    # ====================================================================
    model.EXTRA_FEATURES.append("is_shale")
    row = run_experiment(df, "E07", "Add is_shale binary indicator", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("is_shale")
    all_rows.append(row)

    # ====================================================================
    # Experiment E08: Add is_rock_surface indicator
    # Prior: 50%
    # ====================================================================
    model.EXTRA_FEATURES.append("is_rock_surface")
    row = run_experiment(df, "E08", "Add is_rock_surface binary indicator", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("is_rock_surface")
    all_rows.append(row)

    # ====================================================================
    # Experiment E09: Add is_peat indicator
    # Prior: 50%
    # ====================================================================
    model.EXTRA_FEATURES.append("is_peat")
    row = run_experiment(df, "E09", "Add is_peat binary indicator", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("is_peat")
    all_rows.append(row)

    # ====================================================================
    # Experiment E10: Add BER rating ordinal (BUILDING FEATURE)
    # Prior: 50%
    # ====================================================================
    model.EXTRA_FEATURES.append("mean_ber_rating_ordinal")
    row = run_experiment(df, "E10", "Add area-mean BER rating ordinal", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("mean_ber_rating_ordinal")
    all_rows.append(row)

    # ====================================================================
    # Experiment E11: Add air permeability
    # Prior: 55%
    # ====================================================================
    model.EXTRA_FEATURES.append("mean_air_permeability")
    row = run_experiment(df, "E11", "Add area-mean air permeability", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("mean_air_permeability")
    all_rows.append(row)

    # ====================================================================
    # Experiment E12: Add pct_suspended_timber
    # Prior: 45%
    # ====================================================================
    model.EXTRA_FEATURES.append("pct_suspended_timber")
    row = run_experiment(df, "E12", "Add pct suspended timber floor", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("pct_suspended_timber")
    all_rows.append(row)

    # ====================================================================
    # Experiment E13: Add pct_slab_on_ground
    # Prior: 40%
    # ====================================================================
    model.EXTRA_FEATURES.append("pct_slab_on_ground")
    row = run_experiment(df, "E13", "Add pct slab-on-ground floor", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("pct_slab_on_ground")
    all_rows.append(row)

    # ====================================================================
    # Experiment E14: Add mean_year_built
    # Prior: 45%
    # ====================================================================
    model.EXTRA_FEATURES.append("mean_year_built")
    row = run_experiment(df, "E14", "Add mean year built", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("mean_year_built")
    all_rows.append(row)

    # ====================================================================
    # Experiment E15: Add pct_detached
    # Prior: 40%
    # ====================================================================
    model.EXTRA_FEATURES.append("pct_detached")
    row = run_experiment(df, "E15", "Add pct detached homes", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("pct_detached")
    all_rows.append(row)

    # ====================================================================
    # Experiment E16: Add pct_post_2011 (modern building regs)
    # Prior: 40%
    # ====================================================================
    model.EXTRA_FEATURES.append("pct_post_2011")
    row = run_experiment(df, "E16", "Add pct homes built post-2011 (modern regs)", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("pct_post_2011")
    all_rows.append(row)

    # ====================================================================
    # Experiment E17: Add pct_pre_1970 (old construction)
    # Prior: 35%
    # ====================================================================
    model.EXTRA_FEATURES.append("pct_pre_1970")
    row = run_experiment(df, "E17", "Add pct homes built pre-1970", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("pct_pre_1970")
    all_rows.append(row)

    # ====================================================================
    # Experiment E18: Add mean_floor_area
    # Prior: 30%
    # ====================================================================
    model.EXTRA_FEATURES.append("mean_floor_area")
    row = run_experiment(df, "E18", "Add mean floor area", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("mean_floor_area")
    all_rows.append(row)

    # ====================================================================
    # Experiment E19: Add pct_mvhr (mechanical ventilation)
    # Prior: 30%
    # ====================================================================
    model.EXTRA_FEATURES.append("pct_mvhr")
    row = run_experiment(df, "E19", "Add pct MVHR ventilation", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.EXTRA_FEATURES.remove("pct_mvhr")
    all_rows.append(row)

    # ====================================================================
    # Experiment E20: Class weight balancing (scale_pos_weight)
    # Prior: 50%
    # ====================================================================
    pos_rate = df["is_hra"].mean()
    old_params = model.XGBOOST_PARAMS.copy()
    model.XGBOOST_PARAMS["scale_pos_weight"] = (1 - pos_rate) / pos_rate
    row = run_experiment(df, "E20", f"Class weight balancing (scale_pos_weight={model.XGBOOST_PARAMS['scale_pos_weight']:.2f})", model)
    if row["cv_auc_mean"] > best_auc:
        best_auc = row["cv_auc_mean"]
        print(f"  >>> KEEP (new best: {best_auc:.4f})")
        row["notes"] += " KEEP"
    else:
        print(f"  >>> REVERT (no improvement over {best_auc:.4f})")
        row["notes"] += " REVERT"
        model.XGBOOST_PARAMS.clear()
        model.XGBOOST_PARAMS.update(old_params)
    all_rows.append(row)

    # ====================================================================
    # Write all results
    # ====================================================================
    _write_results(all_rows, append=True)

    print(f"\n{'='*60}")
    print(f"Phase 2 Summary")
    print(f"{'='*60}")
    print(f"Best CV AUC: {best_auc:.4f}")
    print(f"Current features: {model.get_feature_columns()}")
    print(f"Experiments run: {len(all_rows)}")
    kept = sum(1 for r in all_rows if "KEEP" in r.get("notes", ""))
    print(f"Kept: {kept}, Reverted: {len(all_rows) - kept}")


if __name__ == "__main__":
    main()
