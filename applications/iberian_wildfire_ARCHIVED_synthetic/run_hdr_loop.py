"""
Automated HDR loop for Iberian wildfire VLF prediction.

Runs 80-120 experiments systematically, modifying model.py between runs.
Each experiment tests one hypothesis at a time.
"""

from __future__ import annotations

import csv
import importlib
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

RESULTS_FILE = APP_DIR / "results.tsv"


# ============================================================================
# Experiment definitions
# ============================================================================

# Each experiment is (exp_id, description, extra_features, prepare_code, model_changes)
# extra_features: list of feature columns to add to EXTRA_FEATURES
# prepare_code: additional code for prepare_features
# model_changes: dict of model.py attributes to change

EXPERIMENTS = [
    # --- Phase 2: Feature engineering (one at a time) ---
    # E01-E10: Core feature additions
    ("E01", "Add LFMC (live fuel moisture)", ["lfmc"], None, None),
    ("E02", "Add SPEI-1 (1-month drought)", ["lfmc", "spei_1"], None, None),
    ("E03", "Add SPEI-3 (3-month drought)", ["lfmc", "spei_1", "spei_3"], None, None),
    ("E04", "Add SPEI-12 (12-month drought)", ["lfmc", "spei_1", "spei_3", "spei_12"], None, None),
    ("E05", "Add eucalyptus fraction", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac"], None, None),
    ("E06", "Add concurrent fires", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires"], None, None),
    ("E07", "Add detection hour", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires", "detection_hour"], None, None),
    ("E08", "Add heatwave days", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires", "detection_hour", "heatwave_days"], None, None),
    ("E09", "Add night temperature", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires", "detection_hour", "heatwave_days", "night_temp_c"], None, None),
    ("E10", "Add prev year precip", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires", "detection_hour", "heatwave_days", "night_temp_c", "prev_year_precip_mm"], None, None),

    # E11-E15: More features
    ("E11", "Add WUI distance", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires", "detection_hour", "heatwave_days", "night_temp_c", "prev_year_precip_mm", "wui_dist_km"], None, None),
    ("E12", "Add soil moisture", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires", "detection_hour", "heatwave_days", "night_temp_c", "prev_year_precip_mm", "wui_dist_km", "soil_moisture"], None, None),
    ("E13", "Add aspect", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires", "detection_hour", "heatwave_days", "night_temp_c", "prev_year_precip_mm", "wui_dist_km", "soil_moisture", "aspect_deg"], None, None),
    ("E14", "Add country indicator", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires", "detection_hour", "heatwave_days", "night_temp_c", "prev_year_precip_mm", "wui_dist_km", "soil_moisture", "aspect_deg", "is_portugal"], None, None),
    ("E15", "Add DOY (day of year)", ["lfmc", "spei_1", "spei_3", "spei_12", "eucalyptus_frac", "concurrent_fires", "detection_hour", "heatwave_days", "night_temp_c", "prev_year_precip_mm", "wui_dist_km", "soil_moisture", "aspect_deg", "is_portugal", "doy"], None, None),
]


def write_model_py(extra_features: list[str], prepare_code: str | None = None) -> None:
    """Write model.py with the given feature configuration."""
    extra_repr = repr(extra_features)

    prepare_body = ""
    if prepare_code:
        prepare_body = prepare_code
    else:
        # Always add is_portugal if in extra_features
        lines = []
        if "is_portugal" in extra_features:
            lines.append('    df["is_portugal"] = (df["country"] == "PT").astype(int)')
        prepare_body = "\n".join(lines) if lines else ""

    code = f'''"""
Model and feature engineering for Iberian wildfire VLF prediction.

This is the file modified during HDR experiments.
Each experiment changes ONE thing here, evaluated by evaluate.py.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


# ============================================================================
# Feature configuration — modified during HDR loop
# ============================================================================

BASE_FEATURES = [
    "fwi",
    "ffmc",
    "dmc",
    "dc",
    "isi",
    "bui",
    "temp_c",
    "rh_pct",
    "wind_kmh",
    "precip_mm",
    "spei_6",
    "ndvi",
    "elevation_m",
    "slope_deg",
    "lat",
    "month",
]

EXTRA_FEATURES: list[str] = {extra_repr}

SENTINEL2_FEATURES = ["lfmc"]


def get_feature_columns() -> list[str]:
    """Return the full list of feature columns for the model."""
    return BASE_FEATURES + EXTRA_FEATURES


# ============================================================================
# Model configuration
# ============================================================================

MODEL_FAMILY = "xgboost"

XGBOOST_PARAMS = {{
    "max_depth": 6,
    "learning_rate": 0.1,
    "min_child_weight": 10,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "n_estimators": 200,
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "tree_method": "hist",
    "device": "cuda",
    "random_state": 42,
    "scale_pos_weight": 1.0,
}}

LIGHTGBM_PARAMS = {{
    "max_depth": 6,
    "learning_rate": 0.1,
    "min_child_samples": 20,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "n_estimators": 200,
    "objective": "binary",
    "metric": "auc",
    "device": "cpu",
    "random_state": 42,
    "verbose": -1,
    "scale_pos_weight": 1.0,
}}

EXTRATREES_PARAMS = {{
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_leaf": 5,
    "random_state": 42,
    "n_jobs": -1,
}}

RIDGE_PARAMS = {{
    "alpha": 1.0,
    "random_state": 42,
}}


def get_model_config() -> dict:
    """Return the current model family and hyperparameters."""
    family = MODEL_FAMILY
    if family == "xgboost":
        params = XGBOOST_PARAMS.copy()
    elif family == "lightgbm":
        params = LIGHTGBM_PARAMS.copy()
    elif family == "extratrees":
        params = EXTRATREES_PARAMS.copy()
    elif family == "ridge":
        params = RIDGE_PARAMS.copy()
    else:
        raise ValueError(f"Unknown model family: {{family}}")
    return {{"family": family, "params": params}}


def build_model(config: dict):
    """Build a model instance from the config."""
    family = config["family"]
    params = config["params"]
    if family == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(**params)
    elif family == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(**params)
    elif family == "extratrees":
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(**params)
    elif family == "ridge":
        from sklearn.linear_model import RidgeClassifier
        return RidgeClassifier(**params)
    else:
        raise ValueError(f"Unknown model family: {{family}}")


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and engineer features from the raw fire event data."""
    df = df.copy()
{prepare_body}
    return df
'''

    with open(APP_DIR / "model.py", "w") as f:
        f.write(code)


def run_single_experiment(exp_id, description, extra_features, prepare_code=None, model_changes=None):
    """Run one experiment."""
    write_model_py(extra_features, prepare_code)

    # Reimport everything
    import model as model_module
    importlib.reload(model_module)

    from data_loaders import load_dataset
    from evaluate import run_cv, run_holdout, _write_results

    df = load_dataset()
    df = model_module.prepare_features(df)

    feature_cols = model_module.get_feature_columns()
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        print(f"  SKIP {exp_id}: Missing features {missing}")
        return None

    print(f"\n{'='*60}")
    print(f"  {exp_id}: {description}")
    print(f"  Features ({len(feature_cols)}): {feature_cols}")
    print(f"{'='*60}")

    cv_result = run_cv(df, n_folds=5, verbose=True)
    holdout_result, model = run_holdout(df, verbose=True)

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": model_module.MODEL_FAMILY,
        "n_features": cv_result["n_features"],
        "cv_auc_mean": f"{cv_result['cv_auc_mean']:.4f}",
        "cv_auc_std": f"{cv_result['cv_auc_std']:.4f}",
        "cv_f2_mean": f"{cv_result['cv_f2_mean']:.4f}",
        "cv_f2_std": f"{cv_result['cv_f2_std']:.4f}",
        "holdout_auc": f"{holdout_result['auc']:.4f}",
        "holdout_f2": f"{holdout_result['f2']:.4f}",
        "holdout_precision": f"{holdout_result['precision']:.4f}",
        "holdout_recall": f"{holdout_result['recall']:.4f}",
        "aug2025_nw_auc": f"{holdout_result.get('aug2025_nw_auc', float('nan')):.4f}",
        "notes": description,
    }
    _write_results([row], append=True)

    return {
        "cv_auc": cv_result["cv_auc_mean"],
        "holdout_auc": holdout_result["auc"],
    }


def main():
    print("=" * 60)
    print("  Iberian Wildfire VLF — HDR Phase 2 Loop")
    print("=" * 60)

    best_cv_auc = 0.654  # baseline
    best_holdout_auc = 0.643  # baseline
    best_config = []

    for exp_id, description, extra_features, prepare_code, model_changes in EXPERIMENTS:
        try:
            result = run_single_experiment(
                exp_id, description, extra_features, prepare_code, model_changes
            )
            if result and not result.get("error"):
                cv_auc = result["cv_auc"]
                holdout_auc = result["holdout_auc"]

                if cv_auc > best_cv_auc:
                    best_cv_auc = cv_auc
                    best_holdout_auc = holdout_auc
                    best_config = extra_features.copy()
                    print(f"\n  *** KEEP {exp_id}: CV AUC {cv_auc:.4f} > {best_cv_auc:.4f} ***")
                else:
                    print(f"\n  --- {exp_id}: CV AUC {cv_auc:.4f} (best: {best_cv_auc:.4f}) ---")

        except Exception as e:
            print(f"  FAILED {exp_id}: {e}")
            traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"  HDR Loop Complete")
    print(f"  Best CV AUC: {best_cv_auc:.4f}")
    print(f"  Best Holdout AUC: {best_holdout_auc:.4f}")
    print(f"  Best config: {best_config}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
