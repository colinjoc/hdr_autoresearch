"""
Evaluation harness for DART cascading delay day prediction.

Trains a model on daily DART features and evaluates bad-day prediction.
This file is NOT modified during HDR experiments — only model.py changes.

Usage:
    python evaluate.py                  # Full 5-fold CV + holdout evaluation
    python evaluate.py --baseline       # Phase 0.5 baseline only
    python evaluate.py --tournament     # Phase 1 model family tournament
    python evaluate.py --quick          # Single fold quick check
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
    roc_auc_score, f1_score, precision_score, recall_score,
    accuracy_score, fbeta_score, average_precision_score,
)
from sklearn.preprocessing import RobustScaler

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset, get_cv_folds, get_train_test_split
from model import (
    get_feature_columns, get_model_config, build_model, prepare_features,
    MODEL_FAMILY,
)

RESULTS_FILE = APP_DIR / "results.tsv"

TSV_HEADER = [
    "exp_id", "description", "model_family", "n_features",
    "cv_auc_mean", "cv_auc_std", "cv_f2_mean", "cv_f2_std",
    "holdout_auc", "holdout_f2",
    "holdout_precision", "holdout_recall",
    "collapse_period_auc", "notes",
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


def compute_metrics(y_true: np.ndarray, y_proba: np.ndarray) -> dict:
    """Compute classification metrics for bad-day prediction."""
    y_pred = (y_proba >= 0.5).astype(int)

    metrics = {}
    try:
        metrics["auc"] = roc_auc_score(y_true, y_proba)
    except ValueError:
        metrics["auc"] = float("nan")

    try:
        metrics["pr_auc"] = average_precision_score(y_true, y_proba)
    except ValueError:
        metrics["pr_auc"] = float("nan")

    metrics["f2"] = fbeta_score(y_true, y_pred, beta=2, zero_division=0)
    metrics["f1"] = f1_score(y_true, y_pred, zero_division=0)
    metrics["precision"] = precision_score(y_true, y_pred, zero_division=0)
    metrics["recall"] = recall_score(y_true, y_pred, zero_division=0)
    metrics["accuracy"] = accuracy_score(y_true, y_pred)
    metrics["n_positive"] = int(y_true.sum())
    metrics["n_total"] = len(y_true)

    return metrics


def _get_proba(model, X: np.ndarray, family: str) -> np.ndarray:
    """Get predicted probabilities from model, handling different APIs."""
    if family == "ridge":
        # RidgeClassifier uses decision_function, not predict_proba
        from sklearn.preprocessing import MinMaxScaler
        decision = model.decision_function(X)
        # Normalize to [0, 1]
        scaler = MinMaxScaler()
        return scaler.fit_transform(decision.reshape(-1, 1)).ravel()
    else:
        proba = model.predict_proba(X)
        if proba.ndim == 2:
            return proba[:, 1]
        return proba


def run_cv(
    df: pd.DataFrame, n_folds: int = 5, verbose: bool = True,
) -> dict:
    """Run temporal cross-validation and return aggregate metrics."""
    config = get_model_config()
    feature_cols = get_feature_columns()
    folds = get_cv_folds(df, n_folds)

    fold_metrics = []
    for i, (train_idx, val_idx) in enumerate(folds):
        train_df = df.iloc[train_idx]
        val_df = df.iloc[val_idx]

        X_train = train_df[feature_cols].values.astype(np.float32)
        y_train = train_df["bad_day"].values
        X_val = val_df[feature_cols].values.astype(np.float32)
        y_val = val_df["bad_day"].values

        # Scale features for linear models
        if config["family"] == "ridge":
            scaler = RobustScaler()
            X_train = scaler.fit_transform(X_train)
            X_val = scaler.transform(X_val)

        model = build_model(config)
        model.fit(X_train, y_train)

        y_proba = _get_proba(model, X_val, config["family"])
        metrics = compute_metrics(y_val, y_proba)

        if verbose:
            print(f"  Fold {i+1}/{n_folds}: AUC={metrics['auc']:.3f} "
                  f"F2={metrics['f2']:.3f} "
                  f"(+: {metrics['n_positive']}/{metrics['n_total']})")

        fold_metrics.append(metrics)

    # Aggregate
    result = {}
    for key in ["auc", "f2", "f1", "precision", "recall"]:
        values = [m[key] for m in fold_metrics if not np.isnan(m[key])]
        if values:
            result[f"cv_{key}_mean"] = np.mean(values)
            result[f"cv_{key}_std"] = np.std(values)
        else:
            result[f"cv_{key}_mean"] = float("nan")
            result[f"cv_{key}_std"] = float("nan")

    result["n_folds"] = len(fold_metrics)
    result["config"] = config
    result["n_features"] = len(feature_cols)

    return result


def run_holdout(
    df: pd.DataFrame, test_months: int = 3, verbose: bool = True,
) -> dict:
    """Train on all data except last N months, evaluate on holdout."""
    config = get_model_config()
    feature_cols = get_feature_columns()
    train_df, test_df = get_train_test_split(df, test_months)

    X_train = train_df[feature_cols].values.astype(np.float32)
    y_train = train_df["bad_day"].values
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df["bad_day"].values

    if config["family"] == "ridge":
        scaler = RobustScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    model = build_model(config)
    model.fit(X_train, y_train)

    y_proba = _get_proba(model, X_test, config["family"])
    metrics = compute_metrics(y_test, y_proba)

    if verbose:
        print(f"\n  Holdout ({test_months} months): AUC={metrics['auc']:.3f} "
              f"F2={metrics['f2']:.3f} Precision={metrics['precision']:.3f} "
              f"Recall={metrics['recall']:.3f}")
        print(f"  Holdout +/total: {metrics['n_positive']}/{metrics['n_total']}")

    # Evaluate specifically on Oct-Dec 2024 (the collapse period)
    collapse_mask = (
        (test_df.index >= "2024-10-01") & (test_df.index <= "2024-12-31")
    )
    if collapse_mask.sum() > 0:
        collapse_metrics = compute_metrics(
            y_test[collapse_mask], y_proba[collapse_mask]
        )
        metrics["collapse_auc"] = collapse_metrics["auc"]
        if verbose:
            print(f"  Collapse period (Oct-Dec 2024): AUC={collapse_metrics['auc']:.3f}")

    return metrics, model


def run_tournament(df: pd.DataFrame) -> None:
    """Run Phase 1 model family tournament."""
    import model as model_module

    families = ["xgboost", "extratrees", "ridge", "lightgbm"]
    results = []

    for family in families:
        print(f"\n{'='*60}")
        print(f"  Tournament: {family}")
        print(f"{'='*60}")

        # Temporarily change model family
        original_family = model_module.MODEL_FAMILY
        model_module.MODEL_FAMILY = family

        try:
            cv_result = run_cv(df, n_folds=5, verbose=True)
            holdout_result, _ = run_holdout(df, verbose=True)

            row = {
                "exp_id": f"T_{family}",
                "description": f"Tournament: {family}",
                "model_family": family,
                "n_features": cv_result["n_features"],
                "cv_auc_mean": f"{cv_result['cv_auc_mean']:.4f}",
                "cv_auc_std": f"{cv_result['cv_auc_std']:.4f}",
                "cv_f2_mean": f"{cv_result['cv_f2_mean']:.4f}",
                "cv_f2_std": f"{cv_result['cv_f2_std']:.4f}",
                "holdout_auc": f"{holdout_result['auc']:.4f}",
                "holdout_f2": f"{holdout_result['f2']:.4f}",
                "holdout_precision": f"{holdout_result['precision']:.4f}",
                "holdout_recall": f"{holdout_result['recall']:.4f}",
                "collapse_period_auc": f"{holdout_result.get('collapse_auc', float('nan')):.4f}",
                "notes": "Phase 1 tournament",
            }
            results.append(row)
            print(f"\n  {family}: CV AUC={cv_result['cv_auc_mean']:.3f} "
                  f"Holdout AUC={holdout_result['auc']:.3f}")

        except Exception as e:
            print(f"  {family} FAILED: {e}")
            results.append({
                "exp_id": f"T_{family}",
                "description": f"Tournament: {family} (FAILED)",
                "model_family": family,
                "notes": f"Failed: {str(e)[:100]}",
            })

        model_module.MODEL_FAMILY = original_family

    _write_results(results, append=True)
    print("\n  Tournament results written to results.tsv")


def main():
    parser = argparse.ArgumentParser(description="DART delay prediction evaluation")
    parser.add_argument("--baseline", action="store_true", help="Phase 0.5 baseline only")
    parser.add_argument("--tournament", action="store_true", help="Phase 1 tournament")
    parser.add_argument("--quick", action="store_true", help="Single fold quick check")
    parser.add_argument("--exp-id", type=str, default=None, help="Experiment ID")
    parser.add_argument("--description", type=str, default=None, help="Experiment description")
    args = parser.parse_args()

    print("=" * 60)
    print("  DART Cascading Delay Day Prediction")
    print("=" * 60)

    # Load data
    df = load_dataset()
    df = prepare_features(df)

    feature_cols = get_feature_columns()
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        print(f"  WARNING: Missing features: {missing}")
        return

    print(f"\n  Dataset: {len(df)} days, {len(feature_cols)} features")
    print(f"  Bad days: {df['bad_day'].sum()} ({df['bad_day'].mean():.1%})")
    print(f"  Model family: {MODEL_FAMILY}")
    print(f"  Features: {feature_cols}")

    if args.tournament:
        run_tournament(df)
        return

    # Run CV
    print(f"\n{'='*60}")
    print("  5-Fold Temporal Cross-Validation")
    print(f"{'='*60}")

    n_folds = 1 if args.quick else 5
    cv_result = run_cv(df, n_folds=n_folds, verbose=True)
    print(f"\n  CV AUC: {cv_result['cv_auc_mean']:.4f} +/- {cv_result['cv_auc_std']:.4f}")
    print(f"  CV F2:  {cv_result['cv_f2_mean']:.4f} +/- {cv_result['cv_f2_std']:.4f}")

    # Run holdout
    print(f"\n{'='*60}")
    print("  Holdout Evaluation (last 3 months)")
    print(f"{'='*60}")
    holdout_result, model = run_holdout(df, verbose=True)

    # Record results
    exp_id = args.exp_id or ("E00" if args.baseline else "E_latest")
    description = args.description or ("Baseline" if args.baseline else "Latest run")

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": MODEL_FAMILY,
        "n_features": cv_result["n_features"],
        "cv_auc_mean": f"{cv_result['cv_auc_mean']:.4f}",
        "cv_auc_std": f"{cv_result['cv_auc_std']:.4f}",
        "cv_f2_mean": f"{cv_result['cv_f2_mean']:.4f}",
        "cv_f2_std": f"{cv_result['cv_f2_std']:.4f}",
        "holdout_auc": f"{holdout_result['auc']:.4f}",
        "holdout_f2": f"{holdout_result['f2']:.4f}",
        "holdout_precision": f"{holdout_result['precision']:.4f}",
        "holdout_recall": f"{holdout_result['recall']:.4f}",
        "collapse_period_auc": f"{holdout_result.get('collapse_auc', float('nan')):.4f}",
        "notes": description,
    }
    _write_results([row], append=True)
    print(f"\n  Results written to {RESULTS_FILE}")

    # Feature importance (for XGBoost)
    if MODEL_FAMILY == "xgboost":
        try:
            importances = model.feature_importances_
            importance_pairs = sorted(
                zip(feature_cols, importances),
                key=lambda x: x[1], reverse=True,
            )
            print(f"\n  Top-10 Feature Importances:")
            for name, imp in importance_pairs[:10]:
                print(f"    {name:35s} {imp:.4f}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
