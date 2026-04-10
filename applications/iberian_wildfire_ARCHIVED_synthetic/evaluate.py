"""
Evaluation harness for Iberian wildfire VLF prediction.

Trains a model on fire-event features and evaluates VLF (>500 ha) prediction.
This file is NOT modified during HDR experiments -- only model.py changes.

Usage:
    python evaluate.py                  # Full 5-fold temporal CV + holdout
    python evaluate.py --baseline       # Phase 0.5 baseline only
    python evaluate.py --tournament     # Phase 1 model family tournament
    python evaluate.py --quick          # Single fold quick check
    python evaluate.py --exp-id E01 --description "Add LFMC feature"
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

from data_loaders import load_dataset, get_temporal_cv_folds, get_holdout_split
from model import (
    get_feature_columns, get_model_config, build_model, prepare_features,
    MODEL_FAMILY, SENTINEL2_FEATURES,
)

RESULTS_FILE = APP_DIR / "results.tsv"

TSV_HEADER = [
    "exp_id", "description", "model_family", "n_features",
    "cv_auc_mean", "cv_auc_std", "cv_f2_mean", "cv_f2_std",
    "holdout_auc", "holdout_f2",
    "holdout_precision", "holdout_recall",
    "aug2025_nw_auc", "notes",
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
    """Compute classification metrics for VLF prediction."""
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
        from sklearn.preprocessing import MinMaxScaler
        decision = model.decision_function(X)
        scaler = MinMaxScaler()
        return scaler.fit_transform(decision.reshape(-1, 1)).ravel()
    else:
        proba = model.predict_proba(X)
        if proba.ndim == 2:
            return proba[:, 1]
        return proba


def _prepare_Xy(
    df: pd.DataFrame,
    feature_cols: list[str],
    handle_sentinel2: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Prepare feature matrix X and target y from DataFrame.

    Handles missing LFMC for pre-2018 fires by filling with median.
    """
    X = df[feature_cols].copy()

    # Fill missing Sentinel-2 features (pre-2018) with training median
    for col in SENTINEL2_FEATURES:
        if col in X.columns:
            median_val = X[col].median()
            X[col] = X[col].fillna(median_val)

    # Fill any remaining NaN with 0
    X = X.fillna(0)

    return X.values.astype(np.float32), df["is_vlf"].values


def run_cv(
    df: pd.DataFrame, n_folds: int = 5, verbose: bool = True,
) -> dict:
    """Run temporal cross-validation and return aggregate metrics."""
    config = get_model_config()
    feature_cols = get_feature_columns()
    folds = get_temporal_cv_folds(df, n_folds)

    fold_metrics = []
    for i, (train_idx, val_idx) in enumerate(folds):
        train_df = df.loc[train_idx]
        val_df = df.loc[val_idx]

        X_train, y_train = _prepare_Xy(train_df, feature_cols)
        X_val, y_val = _prepare_Xy(val_df, feature_cols)

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
    df: pd.DataFrame, holdout_year: int = 2025, verbose: bool = True,
) -> tuple[dict, object]:
    """Train on all years before holdout, evaluate on holdout year."""
    config = get_model_config()
    feature_cols = get_feature_columns()
    train_df, test_df = get_holdout_split(df, holdout_year)

    X_train, y_train = _prepare_Xy(train_df, feature_cols)
    X_test, y_test = _prepare_Xy(test_df, feature_cols)

    if config["family"] == "ridge":
        scaler = RobustScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    model = build_model(config)
    model.fit(X_train, y_train)

    y_proba = _get_proba(model, X_test, config["family"])
    metrics = compute_metrics(y_test, y_proba)

    if verbose:
        print(f"\n  Holdout ({holdout_year}): AUC={metrics['auc']:.3f} "
              f"F2={metrics['f2']:.3f} Precision={metrics['precision']:.3f} "
              f"Recall={metrics['recall']:.3f}")
        print(f"  Holdout +/total: {metrics['n_positive']}/{metrics['n_total']}")

    # Evaluate specifically on August 2025 NW Iberia fires (the VLF cluster)
    aug2025_mask = (
        (test_df["month"] == 8) & (test_df["lat"] > 41.0)
    )
    if aug2025_mask.sum() > 0:
        aug_idx = test_df.index[aug2025_mask]
        aug_positions = [list(test_df.index).index(idx) for idx in aug_idx]
        aug_proba = y_proba[aug_positions]
        aug_true = y_test[aug_positions]
        if len(np.unique(aug_true)) > 1:
            aug_metrics = compute_metrics(aug_true, aug_proba)
            metrics["aug2025_nw_auc"] = aug_metrics["auc"]
            if verbose:
                print(f"  Aug 2025 NW Iberia: AUC={aug_metrics['auc']:.3f} "
                      f"(+: {aug_metrics['n_positive']}/{aug_metrics['n_total']})")
        else:
            metrics["aug2025_nw_auc"] = float("nan")
    else:
        metrics["aug2025_nw_auc"] = float("nan")

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
                "cv_auc_mean": f"{cv_result['cv_auc_mean']:.4f}",
                "cv_auc_std": f"{cv_result['cv_auc_std']:.4f}",
                "cv_f2_mean": f"{cv_result['cv_f2_mean']:.4f}",
                "cv_f2_std": f"{cv_result['cv_f2_std']:.4f}",
                "holdout_auc": f"{holdout_result['auc']:.4f}",
                "holdout_f2": f"{holdout_result['f2']:.4f}",
                "holdout_precision": f"{holdout_result['precision']:.4f}",
                "holdout_recall": f"{holdout_result['recall']:.4f}",
                "aug2025_nw_auc": f"{holdout_result.get('aug2025_nw_auc', float('nan')):.4f}",
                "notes": "Phase 1 tournament",
            }
            results.append(row)
            print(f"\n  {family}: CV AUC={cv_result['cv_auc_mean']:.3f} "
                  f"Holdout AUC={holdout_result['auc']:.3f}")

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


def run_single_predictor_comparison(df: pd.DataFrame) -> dict:
    """Phase 2.5: Compare FWI vs LFMC vs SPEI-6 as single predictors.

    Tests each as a single-feature logistic regression and compares AUC.
    Then tests whether adding LFMC to FWI improves prediction.
    """
    from sklearn.linear_model import LogisticRegression

    train_df, test_df = get_holdout_split(df, 2025)
    results = {}

    # Only use data with LFMC available (2018+) for fair comparison
    train_s2 = train_df[train_df["lfmc"].notna()].copy()

    single_predictors = {
        "fwi_only": ["fwi"],
        "lfmc_only": ["lfmc"],
        "spei6_only": ["spei_6"],
        "fwi_plus_lfmc": ["fwi", "lfmc"],
        "fwi_plus_spei6": ["fwi", "spei_6"],
        "all_three": ["fwi", "lfmc", "spei_6"],
    }

    print(f"\n{'='*60}")
    print("  Phase 2.5: Single Predictor Comparison")
    print(f"{'='*60}")

    for name, cols in single_predictors.items():
        X_train = train_s2[cols].fillna(0).values.astype(np.float32)
        y_train = train_s2["is_vlf"].values

        # Test data: use 2025 with LFMC where available
        test_s2 = test_df[test_df["lfmc"].notna()].copy()
        if len(test_s2) == 0:
            test_s2 = test_df.copy()
            for c in cols:
                if c == "lfmc":
                    test_s2["lfmc"] = test_s2["lfmc"].fillna(train_s2["lfmc"].median())

        X_test = test_s2[cols].fillna(0).values.astype(np.float32)
        y_test = test_s2["is_vlf"].values

        scaler = RobustScaler()
        X_train_sc = scaler.fit_transform(X_train)
        X_test_sc = scaler.transform(X_test)

        lr = LogisticRegression(max_iter=1000, random_state=42)
        lr.fit(X_train_sc, y_train)
        y_proba = lr.predict_proba(X_test_sc)[:, 1]

        try:
            auc = roc_auc_score(y_test, y_proba)
        except ValueError:
            auc = float("nan")

        results[name] = {"auc": auc, "features": cols, "n_test": len(y_test)}
        print(f"  {name:25s}: AUC={auc:.4f} (n={len(y_test)})")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Iberian wildfire VLF prediction evaluation"
    )
    parser.add_argument("--baseline", action="store_true",
                        help="Phase 0.5 baseline only")
    parser.add_argument("--tournament", action="store_true",
                        help="Phase 1 tournament")
    parser.add_argument("--quick", action="store_true",
                        help="Single fold quick check")
    parser.add_argument("--single-predictor", action="store_true",
                        help="Phase 2.5 single predictor comparison")
    parser.add_argument("--exp-id", type=str, default=None,
                        help="Experiment ID")
    parser.add_argument("--description", type=str, default=None,
                        help="Experiment description")
    args = parser.parse_args()

    print("=" * 60)
    print("  Iberian Wildfire VLF (>500 ha) Prediction")
    print("=" * 60)

    # Load data
    df = load_dataset()
    df = prepare_features(df)

    feature_cols = get_feature_columns()
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        print(f"  WARNING: Missing features: {missing}")
        return

    print(f"\n  Dataset: {len(df)} fires, {len(feature_cols)} features")
    print(f"  VLF fires: {df['is_vlf'].sum()} ({df['is_vlf'].mean():.1%})")
    print(f"  Years: {df['year'].min()}-{df['year'].max()}")
    print(f"  Countries: {df['country'].unique()}")
    print(f"  Model family: {MODEL_FAMILY}")
    print(f"  Features: {feature_cols}")

    if args.single_predictor:
        run_single_predictor_comparison(df)
        return

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
    print("  Holdout Evaluation (2025)")
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
        "aug2025_nw_auc": f"{holdout_result.get('aug2025_nw_auc', float('nan')):.4f}",
        "notes": description,
    }
    _write_results([row], append=True)
    print(f"\n  Results written to {RESULTS_FILE}")

    # Feature importance
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
