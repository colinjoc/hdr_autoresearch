"""
Evaluation harness for flight delay propagation prediction.

Trains a regression model on flight features and evaluates arrival delay
prediction. Also computes binary classification metrics for "significantly
delayed" (arrival delay > 30 min).

This file is NOT modified during HDR experiments — only model.py changes.

Usage:
    python evaluate.py                  # Full 5-fold temporal CV + holdout
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
    mean_absolute_error, mean_squared_error, r2_score,
    roc_auc_score, f1_score, precision_score, recall_score,
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
    "cv_mae_mean", "cv_mae_std", "cv_r2_mean", "cv_r2_std",
    "cv_auc30_mean", "cv_auc30_std",
    "holdout_mae", "holdout_rmse", "holdout_r2",
    "holdout_auc30", "holdout_f1_30",
    "holdout_precision_30", "holdout_recall_30",
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


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Compute regression + binary classification metrics."""
    metrics = {}

    # Regression metrics
    metrics["mae"] = mean_absolute_error(y_true, y_pred)
    metrics["rmse"] = np.sqrt(mean_squared_error(y_true, y_pred))
    metrics["r2"] = r2_score(y_true, y_pred)
    metrics["median_ae"] = float(np.median(np.abs(y_true - y_pred)))

    # Binary classification: delayed > 30 min
    y_binary = (y_true > 30).astype(int)
    y_pred_binary = (y_pred > 30).astype(int)

    try:
        metrics["auc_30"] = roc_auc_score(y_binary, y_pred)
    except ValueError:
        metrics["auc_30"] = float("nan")

    metrics["f1_30"] = f1_score(y_binary, y_pred_binary, zero_division=0)
    metrics["precision_30"] = precision_score(y_binary, y_pred_binary, zero_division=0)
    metrics["recall_30"] = recall_score(y_binary, y_pred_binary, zero_division=0)
    metrics["n_total"] = len(y_true)
    metrics["n_delayed_30"] = int(y_binary.sum())

    return metrics


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
        y_train = train_df["arr_delay"].values.astype(np.float32)
        X_val = val_df[feature_cols].values.astype(np.float32)
        y_val = val_df["arr_delay"].values.astype(np.float32)

        # Scale features for linear models
        if config["family"] == "ridge":
            scaler = RobustScaler()
            X_train = scaler.fit_transform(X_train)
            X_val = scaler.transform(X_val)

        model = build_model(config)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)

        metrics = compute_metrics(y_val, y_pred)

        if verbose:
            print(f"  Fold {i+1}/{n_folds}: MAE={metrics['mae']:.2f} "
                  f"R2={metrics['r2']:.4f} AUC30={metrics['auc_30']:.3f}")

        fold_metrics.append(metrics)

    # Aggregate
    result = {}
    for key in ["mae", "rmse", "r2", "auc_30", "f1_30"]:
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
    df: pd.DataFrame, verbose: bool = True,
) -> tuple[dict, object]:
    """Train on all data except last 15%, evaluate on holdout."""
    config = get_model_config()
    feature_cols = get_feature_columns()
    train_df, test_df = get_train_test_split(df)

    X_train = train_df[feature_cols].values.astype(np.float32)
    y_train = train_df["arr_delay"].values.astype(np.float32)
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df["arr_delay"].values.astype(np.float32)

    if config["family"] == "ridge":
        scaler = RobustScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    model = build_model(config)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    metrics = compute_metrics(y_test, y_pred)

    if verbose:
        print(f"\n  Holdout: MAE={metrics['mae']:.2f} RMSE={metrics['rmse']:.2f} "
              f"R2={metrics['r2']:.4f}")
        print(f"  AUC30={metrics['auc_30']:.3f} F1_30={metrics['f1_30']:.3f} "
              f"Prec={metrics['precision_30']:.3f} Rec={metrics['recall_30']:.3f}")
        print(f"  Flights: {metrics['n_total']}, delayed>30: {metrics['n_delayed_30']}")

    return metrics, model


def run_tournament(df: pd.DataFrame) -> None:
    """Run Phase 1 model family tournament."""
    import model as model_module

    families = ["xgboost", "lightgbm", "extratrees", "ridge"]
    results = []

    for family in families:
        print(f"\n{'='*60}")
        print(f"  Tournament: {family}")
        print(f"{'='*60}")

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
                "cv_mae_mean": f"{cv_result['cv_mae_mean']:.2f}",
                "cv_mae_std": f"{cv_result['cv_mae_std']:.2f}",
                "cv_r2_mean": f"{cv_result['cv_r2_mean']:.4f}",
                "cv_r2_std": f"{cv_result['cv_r2_std']:.4f}",
                "cv_auc30_mean": f"{cv_result['cv_auc_30_mean']:.4f}",
                "cv_auc30_std": f"{cv_result['cv_auc_30_std']:.4f}",
                "holdout_mae": f"{holdout_result['mae']:.2f}",
                "holdout_rmse": f"{holdout_result['rmse']:.2f}",
                "holdout_r2": f"{holdout_result['r2']:.4f}",
                "holdout_auc30": f"{holdout_result['auc_30']:.4f}",
                "holdout_f1_30": f"{holdout_result['f1_30']:.4f}",
                "holdout_precision_30": f"{holdout_result['precision_30']:.4f}",
                "holdout_recall_30": f"{holdout_result['recall_30']:.4f}",
                "notes": "Phase 1 tournament",
            }
            results.append(row)
            print(f"\n  {family}: CV MAE={cv_result['cv_mae_mean']:.2f} "
                  f"Holdout MAE={holdout_result['mae']:.2f}")

        except Exception as e:
            print(f"  {family} FAILED: {e}")
            import traceback
            traceback.print_exc()
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
    parser = argparse.ArgumentParser(
        description="Flight delay propagation evaluation"
    )
    parser.add_argument("--baseline", action="store_true",
                        help="Phase 0.5 baseline only")
    parser.add_argument("--tournament", action="store_true",
                        help="Phase 1 tournament")
    parser.add_argument("--quick", action="store_true",
                        help="Single fold quick check")
    parser.add_argument("--exp-id", type=str, default=None,
                        help="Experiment ID")
    parser.add_argument("--description", type=str, default=None,
                        help="Experiment description")
    args = parser.parse_args()

    print("=" * 60)
    print("  Flight Delay Propagation Prediction")
    print("=" * 60)

    # Load data
    df = load_dataset()

    # Drop cancelled flights and NaN delays
    df = df[df["arr_delay"].notna()].copy()

    df = prepare_features(df)

    feature_cols = get_feature_columns()
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        print(f"  WARNING: Missing features: {missing}")
        return

    print(f"\n  Dataset: {len(df)} flights, {len(feature_cols)} features")
    print(f"  Mean arrival delay: {df['arr_delay'].mean():.1f} min")
    print(f"  Delayed >30 min: {(df['arr_delay'] > 30).mean():.1%}")
    print(f"  Model family: {MODEL_FAMILY}")

    if args.tournament:
        run_tournament(df)
        return

    # Run CV
    print(f"\n{'='*60}")
    print("  5-Fold Temporal Cross-Validation")
    print(f"{'='*60}")

    n_folds = 1 if args.quick else 5
    cv_result = run_cv(df, n_folds=n_folds, verbose=True)
    print(f"\n  CV MAE: {cv_result['cv_mae_mean']:.2f} +/- {cv_result['cv_mae_std']:.2f}")
    print(f"  CV R2:  {cv_result['cv_r2_mean']:.4f} +/- {cv_result['cv_r2_std']:.4f}")
    print(f"  CV AUC30: {cv_result['cv_auc_30_mean']:.4f} +/- {cv_result['cv_auc_30_std']:.4f}")

    # Run holdout
    print(f"\n{'='*60}")
    print("  Holdout Evaluation (last 15% of dates)")
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
        "cv_mae_mean": f"{cv_result['cv_mae_mean']:.2f}",
        "cv_mae_std": f"{cv_result['cv_mae_std']:.2f}",
        "cv_r2_mean": f"{cv_result['cv_r2_mean']:.4f}",
        "cv_r2_std": f"{cv_result['cv_r2_std']:.4f}",
        "cv_auc30_mean": f"{cv_result['cv_auc_30_mean']:.4f}",
        "cv_auc30_std": f"{cv_result['cv_auc_30_std']:.4f}",
        "holdout_mae": f"{holdout_result['mae']:.2f}",
        "holdout_rmse": f"{holdout_result['rmse']:.2f}",
        "holdout_r2": f"{holdout_result['r2']:.4f}",
        "holdout_auc30": f"{holdout_result['auc_30']:.4f}",
        "holdout_f1_30": f"{holdout_result['f1_30']:.4f}",
        "holdout_precision_30": f"{holdout_result['precision_30']:.4f}",
        "holdout_recall_30": f"{holdout_result['recall_30']:.4f}",
        "notes": description,
    }
    _write_results([row], append=True)
    print(f"\n  Results written to {RESULTS_FILE}")

    # Feature importance (for tree models)
    if MODEL_FAMILY in ("xgboost", "lightgbm", "extratrees"):
        try:
            importances = model.feature_importances_
            importance_pairs = sorted(
                zip(feature_cols, importances),
                key=lambda x: x[1], reverse=True,
            )
            print(f"\n  Top-15 Feature Importances:")
            for name, imp in importance_pairs[:15]:
                print(f"    {name:30s} {imp:.4f}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
