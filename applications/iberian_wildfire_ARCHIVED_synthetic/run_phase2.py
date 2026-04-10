"""
Phase 2 HDR loop runner for Iberian wildfire VLF prediction.

Automates the experiment loop: modify model.py, evaluate, record, keep/revert.
"""

from __future__ import annotations

import csv
import importlib
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


def run_experiment(exp_id: str, description: str) -> dict:
    """Run a single HDR experiment and return metrics."""
    # Reimport model to pick up changes
    import model as model_module
    importlib.reload(model_module)

    from data_loaders import load_dataset, get_temporal_cv_folds, get_holdout_split
    from evaluate import (
        compute_metrics, _get_proba, _prepare_Xy, _write_results,
        run_cv, run_holdout,
    )

    df = load_dataset()
    df = model_module.prepare_features(df)

    feature_cols = model_module.get_feature_columns()
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        return {"error": f"Missing features: {missing}"}

    print(f"\n{'='*60}")
    print(f"  Experiment: {exp_id} — {description}")
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
        "holdout_f2": holdout_result["f2"],
        "aug2025_nw_auc": holdout_result.get("aug2025_nw_auc", float("nan")),
        "n_features": len(feature_cols),
    }


if __name__ == "__main__":
    result = run_experiment("E_test", "test run")
    print(f"\nResult: {result}")
