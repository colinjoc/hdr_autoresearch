"""
Evaluation harness for Xylella Olive Decline Prediction.

Binary classification: predict which municipalities will show new olive
grove health decline (NDVI drop) within the next 12 months.
Uses spatial cross-validation grouped by province to avoid spatial leakage.

This file is NOT modified during HDR experiments — only model.py changes.

Usage:
    python evaluate.py                  # Full spatial CV evaluation
    python evaluate.py --baseline       # Phase 0.5 baseline only
    python evaluate.py --tournament     # Phase 1 model family tournament
    python evaluate.py --quick          # Single fold quick check
    python evaluate.py --experiment E01 --description "Add frost_days_below_minus6"
    python evaluate.py --mechanism      # Phase 2.5 mechanism comparison
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
    confusion_matrix,
)
from sklearn.preprocessing import RobustScaler

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset, get_cv_folds_spatial, get_train_test_split
from model import (
    get_feature_columns, get_model_config, build_model, prepare_features,
    MODEL_FAMILY, CATEGORICAL_FEATURES, EXTRA_CATEGORICAL,
)

RESULTS_FILE = APP_DIR / "results.tsv"

TSV_HEADER = [
    "exp_id", "description", "model_family", "n_features",
    "cv_auc_mean", "cv_auc_std", "cv_f1_mean", "cv_f1_std",
    "cv_precision_mean", "cv_recall_mean",
    "holdout_auc", "holdout_f1", "holdout_precision", "holdout_recall",
    "notes",
]


def _write_results(rows: list[dict], append: bool = True) -> None:
    """Write or append rows to results.tsv."""
    mode = "a" if append else "w"
    file_exists = RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0
    with open(RESULTS_FILE, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TSV_HEADER, delimiter="\t",
                                extrasaction="ignore")
        if not append or not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def compute_metrics(y_true: np.ndarray, y_prob: np.ndarray,
                    threshold: float = 0.5) -> dict:
    """Compute classification metrics.

    Args:
        y_true: Binary ground truth (0/1).
        y_prob: Predicted probability of positive class.
        threshold: Decision threshold for binary predictions.

    Returns:
        Dictionary with AUC, precision, recall, F1, and sample count.
    """
    y_pred = (y_prob >= threshold).astype(int)
    try:
        auc = roc_auc_score(y_true, y_prob)
    except ValueError:
        auc = 0.5  # Single class in fold

    n_pos = y_pred.sum()
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    return {
        "auc": auc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "n_samples": len(y_true),
        "n_positive": int(y_true.sum()),
    }


def run_cv(
    df: pd.DataFrame,
    n_folds: int = 5,
    family: str | None = None,
    params: dict | None = None,
    feature_cols: list[str] | None = None,
    verbose: bool = True,
) -> dict:
    """Run spatial cross-validation.

    Args:
        df: Full dataset with features and labels.
        n_folds: Number of CV folds.
        family: Model family override.
        params: Model params override.
        feature_cols: Feature column override.
        verbose: Print fold results.

    Returns:
        Dictionary with CV metrics (mean and std).
    """
    folds = get_cv_folds_spatial(df, n_folds=n_folds)
    fold_metrics = []

    for fold_idx, (train_idx, val_idx) in enumerate(folds):
        train_df = df.iloc[train_idx]
        val_df = df.iloc[val_idx]

        # Prepare features
        if feature_cols is not None:
            # Use custom feature list
            X_train = train_df[feature_cols].fillna(0).values.astype(np.float32)
            y_train = train_df["new_decline_12m"].values.astype(int)
            X_val = val_df[feature_cols].fillna(0).values.astype(np.float32)
            y_val = val_df["new_decline_12m"].values.astype(int)
        else:
            X_train, y_train = prepare_features(train_df)
            X_val, y_val = prepare_features(val_df)

        # Scale for ridge
        fam = family or MODEL_FAMILY
        if fam == "ridge":
            scaler = RobustScaler()
            X_train = scaler.fit_transform(X_train)
            X_val = scaler.transform(X_val)

        # Build and fit model
        model = build_model(family=fam, params=params)
        model.fit(X_train, y_train)

        # Predict
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_val)[:, 1]
        else:
            y_prob = model.decision_function(X_val)

        metrics = compute_metrics(y_val, y_prob)
        fold_metrics.append(metrics)

        if verbose:
            val_provs = val_df["province"].unique()
            print(f"  Fold {fold_idx + 1}: AUC={metrics['auc']:.4f} "
                  f"F1={metrics['f1']:.4f} "
                  f"(provinces: {', '.join(val_provs)})")

    # Aggregate
    aucs = [m["auc"] for m in fold_metrics]
    f1s = [m["f1"] for m in fold_metrics]
    precs = [m["precision"] for m in fold_metrics]
    recs = [m["recall"] for m in fold_metrics]

    return {
        "cv_auc_mean": np.mean(aucs),
        "cv_auc_std": np.std(aucs),
        "cv_f1_mean": np.mean(f1s),
        "cv_f1_std": np.std(f1s),
        "cv_precision_mean": np.mean(precs),
        "cv_recall_mean": np.mean(recs),
        "fold_metrics": fold_metrics,
    }


def run_holdout(
    df: pd.DataFrame,
    family: str | None = None,
    params: dict | None = None,
    feature_cols: list[str] | None = None,
) -> dict:
    """Run holdout evaluation.

    Args:
        df: Full dataset.
        family: Model family override.
        params: Model params override.
        feature_cols: Feature column override.

    Returns:
        Dictionary with holdout metrics.
    """
    train_df, test_df = get_train_test_split(df)

    if feature_cols is not None:
        X_train = train_df[feature_cols].fillna(0).values.astype(np.float32)
        y_train = train_df["new_decline_12m"].values.astype(int)
        X_test = test_df[feature_cols].fillna(0).values.astype(np.float32)
        y_test = test_df["new_decline_12m"].values.astype(int)
    else:
        X_train, y_train = prepare_features(train_df)
        X_test, y_test = prepare_features(test_df)

    fam = family or MODEL_FAMILY
    if fam == "ridge":
        scaler = RobustScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    model = build_model(family=fam, params=params)
    model.fit(X_train, y_train)

    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
    else:
        y_prob = model.decision_function(X_test)

    return compute_metrics(y_test, y_prob)


def run_full_evaluation(
    exp_id: str,
    description: str,
    family: str | None = None,
    params: dict | None = None,
    feature_cols: list[str] | None = None,
    notes: str = "",
    verbose: bool = True,
) -> dict:
    """Run full evaluation (CV + holdout) and record results.

    Args:
        exp_id: Experiment ID (e.g., "E00", "T01", "E01").
        description: Human-readable description.
        family: Model family override.
        params: Model params override.
        feature_cols: Feature column override.
        notes: Additional notes.
        verbose: Print progress.

    Returns:
        Dictionary with all metrics.
    """
    t0 = time.time()
    df = load_dataset()

    if verbose:
        n_features = (len(feature_cols) if feature_cols is not None
                      else len(get_feature_columns()))
        print(f"\n{'='*60}")
        print(f"Experiment {exp_id}: {description}")
        print(f"Model: {family or MODEL_FAMILY}, Features: {n_features}")
        print(f"{'='*60}")

    # CV
    cv_results = run_cv(df, family=family, params=params,
                        feature_cols=feature_cols, verbose=verbose)

    # Holdout
    holdout = run_holdout(df, family=family, params=params,
                          feature_cols=feature_cols)

    elapsed = time.time() - t0
    fam = family or MODEL_FAMILY
    n_feat = (len(feature_cols) if feature_cols is not None
              else len(get_feature_columns()))

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": fam,
        "n_features": n_feat,
        "cv_auc_mean": cv_results["cv_auc_mean"],
        "cv_auc_std": cv_results["cv_auc_std"],
        "cv_f1_mean": cv_results["cv_f1_mean"],
        "cv_f1_std": cv_results["cv_f1_std"],
        "cv_precision_mean": cv_results["cv_precision_mean"],
        "cv_recall_mean": cv_results["cv_recall_mean"],
        "holdout_auc": holdout["auc"],
        "holdout_f1": holdout["f1"],
        "holdout_precision": holdout["precision"],
        "holdout_recall": holdout["recall"],
        "notes": f"{notes} ({elapsed:.1f}s)",
    }

    _write_results([row])

    if verbose:
        print(f"\nResults:")
        print(f"  CV AUC:  {cv_results['cv_auc_mean']:.4f} "
              f"+/- {cv_results['cv_auc_std']:.4f}")
        print(f"  CV F1:   {cv_results['cv_f1_mean']:.4f} "
              f"+/- {cv_results['cv_f1_std']:.4f}")
        print(f"  Holdout AUC: {holdout['auc']:.4f}")
        print(f"  Holdout F1:  {holdout['f1']:.4f}")
        print(f"  Time: {elapsed:.1f}s")

    return row


def run_mechanism_comparison(verbose: bool = True) -> list[dict]:
    """Run Phase 2.5 mechanism comparison.

    Tests three competing hypotheses as separate predictive models:
    (a) Frost-kill model: only climate features
    (b) Diffusion model: only distance + time features
    (c) Combined model: climate + distance

    Returns:
        List of result dictionaries for each mechanism.
    """
    df = load_dataset()
    results = []

    # (a) Frost-kill model: climate features only
    frost_features = [
        "jan_tmin_mean", "winter_tmin_abs", "frost_days_below_minus6",
        "frost_days_below_minus12", "coldest_month_anomaly",
        "annual_precip_mm", "summer_precip_mm", "precip_deficit_frac",
    ]
    if verbose:
        print("\n--- Mechanism A: Frost-kill model (climate only) ---")
    cv_a = run_cv(df, feature_cols=frost_features, verbose=verbose)
    ho_a = run_holdout(df, feature_cols=frost_features)
    row_a = {
        "exp_id": "M_A", "description": "Mechanism A: Frost-kill (climate only)",
        "model_family": MODEL_FAMILY, "n_features": len(frost_features),
        "cv_auc_mean": cv_a["cv_auc_mean"], "cv_auc_std": cv_a["cv_auc_std"],
        "cv_f1_mean": cv_a["cv_f1_mean"], "cv_f1_std": cv_a["cv_f1_std"],
        "cv_precision_mean": cv_a["cv_precision_mean"],
        "cv_recall_mean": cv_a["cv_recall_mean"],
        "holdout_auc": ho_a["auc"], "holdout_f1": ho_a["f1"],
        "holdout_precision": ho_a["precision"],
        "holdout_recall": ho_a["recall"],
        "notes": "Phase 2.5 mechanism comparison",
    }
    _write_results([row_a])
    results.append(row_a)

    # (b) Diffusion model: distance + spatial features only
    diffusion_features = [
        "dist_epicentre_km", "dist_nearest_declining_km",
        "latitude", "longitude", "already_affected",
    ]
    if verbose:
        print("\n--- Mechanism B: Diffusion model (spatial only) ---")
    cv_b = run_cv(df, feature_cols=diffusion_features, verbose=verbose)
    ho_b = run_holdout(df, feature_cols=diffusion_features)
    row_b = {
        "exp_id": "M_B", "description": "Mechanism B: Diffusion (spatial only)",
        "model_family": MODEL_FAMILY, "n_features": len(diffusion_features),
        "cv_auc_mean": cv_b["cv_auc_mean"], "cv_auc_std": cv_b["cv_auc_std"],
        "cv_f1_mean": cv_b["cv_f1_mean"], "cv_f1_std": cv_b["cv_f1_std"],
        "cv_precision_mean": cv_b["cv_precision_mean"],
        "cv_recall_mean": cv_b["cv_recall_mean"],
        "holdout_auc": ho_b["auc"], "holdout_f1": ho_b["f1"],
        "holdout_precision": ho_b["precision"],
        "holdout_recall": ho_b["recall"],
        "notes": "Phase 2.5 mechanism comparison",
    }
    _write_results([row_b])
    results.append(row_b)

    # (c) Combined model: climate + distance
    combined_features = frost_features + diffusion_features
    # Remove duplicates
    combined_features = list(dict.fromkeys(combined_features))
    if verbose:
        print("\n--- Mechanism C: Combined (climate + spatial) ---")
    cv_c = run_cv(df, feature_cols=combined_features, verbose=verbose)
    ho_c = run_holdout(df, feature_cols=combined_features)
    row_c = {
        "exp_id": "M_C", "description": "Mechanism C: Combined (climate + spatial)",
        "model_family": MODEL_FAMILY, "n_features": len(combined_features),
        "cv_auc_mean": cv_c["cv_auc_mean"], "cv_auc_std": cv_c["cv_auc_std"],
        "cv_f1_mean": cv_c["cv_f1_mean"], "cv_f1_std": cv_c["cv_f1_std"],
        "cv_precision_mean": cv_c["cv_precision_mean"],
        "cv_recall_mean": cv_c["cv_recall_mean"],
        "holdout_auc": ho_c["auc"], "holdout_f1": ho_c["f1"],
        "holdout_precision": ho_c["precision"],
        "holdout_recall": ho_c["recall"],
        "notes": "Phase 2.5 mechanism comparison",
    }
    _write_results([row_c])
    results.append(row_c)

    if verbose:
        print("\n" + "="*60)
        print("MECHANISM COMPARISON SUMMARY")
        print("="*60)
        for r in results:
            print(f"  {r['exp_id']}: CV AUC={r['cv_auc_mean']:.4f} "
                  f"+/- {r['cv_auc_std']:.4f} | "
                  f"Holdout AUC={r['holdout_auc']:.4f} | "
                  f"{r['description']}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate Xylella olive decline prediction")
    parser.add_argument("--baseline", action="store_true",
                        help="Run Phase 0.5 baseline")
    parser.add_argument("--tournament", action="store_true",
                        help="Run Phase 1 tournament")
    parser.add_argument("--quick", action="store_true",
                        help="Single fold quick check")
    parser.add_argument("--mechanism", action="store_true",
                        help="Phase 2.5 mechanism comparison")
    parser.add_argument("--experiment", type=str, default=None,
                        help="Experiment ID (e.g., E01)")
    parser.add_argument("--description", type=str, default="",
                        help="Experiment description")
    args = parser.parse_args()

    if args.mechanism:
        run_mechanism_comparison()
    elif args.baseline:
        run_full_evaluation("E00",
                            "Baseline: XGBoost on core geographic + climate + NDVI features",
                            notes="Phase 0.5 baseline")
    elif args.tournament:
        families = ["xgboost", "lightgbm", "extratrees", "ridge"]
        for i, fam in enumerate(families, 1):
            params = {
                "xgboost": {"max_depth": 6, "learning_rate": 0.05,
                            "min_child_weight": 3, "subsample": 0.8,
                            "colsample_bytree": 0.8, "n_estimators": 300,
                            "objective": "binary:logistic", "eval_metric": "auc",
                            "tree_method": "hist", "device": "cuda",
                            "random_state": 42},
                "lightgbm": {"max_depth": 6, "learning_rate": 0.05,
                             "min_child_samples": 20, "subsample": 0.8,
                             "colsample_bytree": 0.8, "n_estimators": 300,
                             "objective": "binary", "metric": "auc",
                             "device": "cpu", "random_state": 42,
                             "verbose": -1},
                "extratrees": {"n_estimators": 500, "max_depth": None,
                               "min_samples_split": 5, "min_samples_leaf": 2,
                               "max_features": "sqrt", "random_state": 42,
                               "n_jobs": -1},
                "ridge": {"alpha": 1.0, "max_iter": 1000},
            }[fam]
            run_full_evaluation(f"T{i:02d}", f"Tournament: {fam}",
                                family=fam, params=params,
                                notes="Phase 1 tournament")
    elif args.experiment:
        run_full_evaluation(args.experiment, args.description,
                            notes="HDR experiment")
    else:
        # Default: run CV with current model.py config
        run_full_evaluation("E00",
                            "Baseline: XGBoost on core geographic + climate + NDVI features",
                            notes="Phase 0.5 baseline")
