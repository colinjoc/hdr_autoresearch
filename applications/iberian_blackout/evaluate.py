"""
Evaluation harness for Iberian blackout cascade prediction.

Trains a model on grid-state features and evaluates frequency excursion prediction.
This file is NOT modified during HDR experiments — only model.py changes.

Usage:
    python evaluate.py                  # Full 5-fold CV + holdout evaluation
    python evaluate.py --baseline       # Phase 0.5 baseline only
    python evaluate.py --tournament     # Phase 1 model family tournament
    python evaluate.py --quick          # Single fold quick check
    python evaluate.py --blackout-day   # Evaluate model prediction on April 28, 2025
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
    accuracy_score, mean_absolute_error, fbeta_score,
    average_precision_score,
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
    "cv_mae_mhz_mean", "cv_mae_mhz_std",
    "holdout_auc", "holdout_f2", "holdout_mae_mhz",
    "blackout_day_predicted", "notes",
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


def compute_metrics(y_true: np.ndarray, y_proba: np.ndarray,
                    freq_dev_true: np.ndarray = None) -> dict:
    """Compute classification and regression metrics."""
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

    if freq_dev_true is not None:
        metrics["mae_mhz"] = mean_absolute_error(y_true * freq_dev_true,
                                                   y_pred * 200)  # crude

    return metrics


def run_cv(df: pd.DataFrame, n_folds: int = 5,
           model_family: str = None) -> dict:
    """Run temporal cross-validation and return aggregated metrics."""
    folds = get_cv_folds(df, n_folds=n_folds)
    feature_cols = get_feature_columns()
    fam = model_family or MODEL_FAMILY

    fold_metrics = []

    for i, (train_df, val_df) in enumerate(folds):
        X_train, y_train = prepare_features(train_df)
        X_val, y_val = prepare_features(val_df)

        # Scale
        scaler = RobustScaler()
        X_train = scaler.fit_transform(X_train)
        X_val = scaler.transform(X_val)

        # Train
        clf = build_model(family=fam)

        if fam == "ridge":
            # RidgeClassifier needs special handling for probability
            clf.fit(X_train, y_train)
            y_proba = clf.decision_function(X_val)
            # Normalize to [0, 1]
            y_proba = (y_proba - y_proba.min()) / (y_proba.max() - y_proba.min() + 1e-10)
        else:
            clf.fit(X_train, y_train)
            y_proba = clf.predict_proba(X_val)[:, 1]

        metrics = compute_metrics(y_val, y_proba)
        fold_metrics.append(metrics)
        print(f"  Fold {i+1}/{n_folds}: AUC={metrics['auc']:.4f}, "
              f"F2={metrics['f2']:.4f}, "
              f"pos={metrics['n_positive']}/{metrics['n_total']}")

    # Aggregate
    auc_vals = [m["auc"] for m in fold_metrics if not np.isnan(m["auc"])]
    f2_vals = [m["f2"] for m in fold_metrics]

    return {
        "cv_auc_mean": np.mean(auc_vals) if auc_vals else float("nan"),
        "cv_auc_std": np.std(auc_vals) if auc_vals else float("nan"),
        "cv_f2_mean": np.mean(f2_vals),
        "cv_f2_std": np.std(f2_vals),
        "cv_mae_mhz_mean": 0.0,  # placeholder
        "cv_mae_mhz_std": 0.0,
        "n_folds": n_folds,
    }


def run_holdout(df: pd.DataFrame, model_family: str = None) -> dict:
    """Train on all data before April 28, test on April 28."""
    train_df, test_df = get_train_test_split(df, test_date="2025-04-28")
    fam = model_family or MODEL_FAMILY

    if len(test_df) == 0:
        print("  WARNING: No test data for April 28, 2025")
        return {"holdout_auc": float("nan"), "holdout_f2": 0.0,
                "holdout_mae_mhz": float("nan"), "blackout_day_predicted": "N/A"}

    X_train, y_train = prepare_features(train_df)
    X_test, y_test = prepare_features(test_df)

    scaler = RobustScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    clf = build_model(family=fam)

    if fam == "ridge":
        clf.fit(X_train, y_train)
        y_proba = clf.decision_function(X_test)
        y_proba = (y_proba - y_proba.min()) / (y_proba.max() - y_proba.min() + 1e-10)
    else:
        clf.fit(X_train, y_train)
        y_proba = clf.predict_proba(X_test)[:, 1]

    metrics = compute_metrics(y_test, y_proba)

    # Check if the model flagged the blackout hours (10-14 CET)
    test_hours = test_df.index.hour if hasattr(test_df.index, 'hour') else pd.to_datetime(test_df.index).hour
    blackout_hours_mask = (test_hours >= 10) & (test_hours <= 14)
    if blackout_hours_mask.any():
        blackout_proba = y_proba[blackout_hours_mask]
        blackout_detected = (blackout_proba >= 0.5).any()
        max_proba = float(blackout_proba.max())
        blackout_str = f"YES (max_p={max_proba:.3f})" if blackout_detected else f"NO (max_p={max_proba:.3f})"
    else:
        blackout_str = "N/A"

    print(f"\n  Holdout (April 28, 2025):")
    print(f"    AUC: {metrics['auc']:.4f}")
    print(f"    F2:  {metrics['f2']:.4f}")
    print(f"    Recall: {metrics['recall']:.4f}")
    print(f"    Precision: {metrics['precision']:.4f}")
    print(f"    Positive/Total: {metrics['n_positive']}/{metrics['n_total']}")
    print(f"    Blackout detected: {blackout_str}")

    return {
        "holdout_auc": metrics["auc"],
        "holdout_f2": metrics["f2"],
        "holdout_mae_mhz": 0.0,
        "blackout_day_predicted": blackout_str,
    }


def run_baseline(df: pd.DataFrame) -> dict:
    """Run Phase 0.5 baseline evaluation."""
    print("=" * 60)
    print("Phase 0.5: Baseline Evaluation")
    print(f"  Model family: {MODEL_FAMILY}")
    print(f"  Features: {len(get_feature_columns())}")
    print(f"  Feature list: {get_feature_columns()}")
    print("=" * 60)

    t0 = time.time()

    # CV
    print("\n5-fold temporal CV:")
    cv_results = run_cv(df, n_folds=5)
    print(f"\n  CV AUC: {cv_results['cv_auc_mean']:.4f} +/- {cv_results['cv_auc_std']:.4f}")
    print(f"  CV F2:  {cv_results['cv_f2_mean']:.4f} +/- {cv_results['cv_f2_std']:.4f}")

    # Holdout
    print("\nHoldout evaluation:")
    holdout_results = run_holdout(df)

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")

    row = {
        "exp_id": "E00",
        "description": "Baseline: XGBoost on raw generation/load features",
        "model_family": MODEL_FAMILY,
        "n_features": len(get_feature_columns()),
        **cv_results,
        **holdout_results,
        "notes": "Phase 0.5 baseline",
    }

    return row


def run_tournament(df: pd.DataFrame) -> list[dict]:
    """Run Phase 1 model family tournament."""
    print("\n" + "=" * 60)
    print("Phase 1: Model Family Tournament")
    print("=" * 60)

    families = ["xgboost", "lightgbm", "extratrees", "ridge"]
    rows = []

    for i, fam in enumerate(families):
        exp_id = f"T{i+1:02d}"
        print(f"\n--- {exp_id}: {fam} ---")

        t0 = time.time()

        try:
            cv_results = run_cv(df, n_folds=5, model_family=fam)
            holdout_results = run_holdout(df, model_family=fam)
            elapsed = time.time() - t0

            row = {
                "exp_id": exp_id,
                "description": f"Tournament: {fam}",
                "model_family": fam,
                "n_features": len(get_feature_columns()),
                **cv_results,
                **holdout_results,
                "notes": f"Phase 1 tournament ({elapsed:.1f}s)",
            }
            rows.append(row)

            print(f"  CV AUC: {cv_results['cv_auc_mean']:.4f} +/- {cv_results['cv_auc_std']:.4f}")

        except Exception as e:
            print(f"  ERROR: {e}")
            row = {
                "exp_id": exp_id,
                "description": f"Tournament: {fam}",
                "model_family": fam,
                "n_features": len(get_feature_columns()),
                "cv_auc_mean": float("nan"),
                "cv_auc_std": float("nan"),
                "cv_f2_mean": 0.0,
                "cv_f2_std": 0.0,
                "holdout_auc": float("nan"),
                "holdout_f2": 0.0,
                "holdout_mae_mhz": float("nan"),
                "blackout_day_predicted": "ERROR",
                "notes": f"Phase 1 tournament - FAILED: {e}",
            }
            rows.append(row)

    # Print tournament summary
    print("\n" + "=" * 60)
    print("Tournament Summary")
    print("=" * 60)
    print(f"{'ID':<6} {'Family':<12} {'CV AUC':>10} {'CV F2':>10} {'Holdout AUC':>12} {'Blackout':>15}")
    print("-" * 70)
    for r in rows:
        print(f"{r['exp_id']:<6} {r['model_family']:<12} "
              f"{r.get('cv_auc_mean', float('nan')):>10.4f} "
              f"{r.get('cv_f2_mean', 0):>10.4f} "
              f"{r.get('holdout_auc', float('nan')):>12.4f} "
              f"{str(r.get('blackout_day_predicted', 'N/A')):>15}")

    # Select winner
    valid = [r for r in rows if not np.isnan(r.get("cv_auc_mean", float("nan")))]
    if valid:
        best = max(valid, key=lambda r: r["cv_auc_mean"])
        print(f"\nTournament winner: {best['model_family']} "
              f"(CV AUC = {best['cv_auc_mean']:.4f})")

    return rows


def run_experiment(df: pd.DataFrame, exp_id: str, description: str,
                   notes: str = "") -> dict:
    """Run a single HDR experiment with current model.py configuration."""
    print(f"\n{'=' * 60}")
    print(f"Experiment: {exp_id} — {description}")
    print(f"{'=' * 60}")

    config = get_model_config()
    print(f"  Model: {config['family']}")
    print(f"  Features ({len(config['features'])}): {config['features'][:10]}...")

    t0 = time.time()

    cv_results = run_cv(df, n_folds=5)
    holdout_results = run_holdout(df)

    elapsed = time.time() - t0

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": config["family"],
        "n_features": len(config["features"]),
        **cv_results,
        **holdout_results,
        "notes": notes + f" ({elapsed:.1f}s)",
    }

    return row


def run_blackout_day_analysis(df: pd.DataFrame) -> dict:
    """Detailed analysis of model predictions on April 28, 2025."""
    print("\n" + "=" * 60)
    print("Blackout Day Analysis: April 28, 2025")
    print("=" * 60)

    train_df, test_df = get_train_test_split(df, test_date="2025-04-28")

    if len(test_df) == 0:
        print("  No data for April 28, 2025")
        return {}

    X_train, y_train = prepare_features(train_df)
    X_test, y_test = prepare_features(test_df)

    scaler = RobustScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    clf = build_model()
    clf.fit(X_train, y_train)

    if MODEL_FAMILY == "ridge":
        y_proba = clf.decision_function(X_test)
        y_proba = (y_proba - y_proba.min()) / (y_proba.max() - y_proba.min() + 1e-10)
    else:
        y_proba = clf.predict_proba(X_test)[:, 1]

    # Hour-by-hour predictions
    print(f"\n  Hour-by-hour predictions:")
    print(f"  {'Hour':>6} {'True':>6} {'P(exc)':>8} {'Pred':>6} {'SNSP':>8} {'Inertia_s':>10}")
    print(f"  {'-'*50}")

    hours = test_df.index.hour if hasattr(test_df.index, 'hour') else pd.to_datetime(test_df.index).hour

    for idx_pos in range(len(test_df)):
        hour = hours[idx_pos]
        true_label = y_test[idx_pos]
        pred_proba = y_proba[idx_pos]
        pred_label = int(pred_proba >= 0.5)
        snsp = test_df.iloc[idx_pos]["snsp"]
        inertia_s = test_df.iloc[idx_pos]["inertia_proxy_s"]

        flag = " <<< BLACKOUT" if (hour == 12 and true_label == 1) else ""
        flag = " *** ALERT" if (pred_proba >= 0.5 and true_label == 0) else flag
        flag = " <<< BLACKOUT" if (hour == 12 and true_label == 1) else flag

        print(f"  {hour:>6} {true_label:>6} {pred_proba:>8.3f} {pred_label:>6} "
              f"{snsp:>8.3f} {inertia_s:>10.2f}{flag}")

    # Feature importance
    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
        feature_cols = get_feature_columns()
        importance_pairs = sorted(zip(feature_cols, importances),
                                  key=lambda x: -x[1])
        print(f"\n  Top 10 feature importances:")
        for fname, imp in importance_pairs[:10]:
            print(f"    {fname:>30}: {imp:.4f}")

    return {
        "blackout_hour_12_proba": float(y_proba[hours == 12].max()) if (hours == 12).any() else float("nan"),
        "max_proba_10_14": float(y_proba[(hours >= 10) & (hours <= 14)].max())
            if ((hours >= 10) & (hours <= 14)).any() else float("nan"),
        "n_hours_flagged": int((y_proba >= 0.5).sum()),
        "n_hours_total": len(y_proba),
    }


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Iberian Blackout Evaluation Harness")
    parser.add_argument("--baseline", action="store_true", help="Run Phase 0.5 baseline")
    parser.add_argument("--tournament", action="store_true", help="Run Phase 1 tournament")
    parser.add_argument("--quick", action="store_true", help="Quick single-fold check")
    parser.add_argument("--blackout-day", action="store_true", help="Blackout day analysis")
    parser.add_argument("--experiment", type=str, help="Run experiment with ID")
    parser.add_argument("--description", type=str, default="", help="Experiment description")
    parser.add_argument("--all", action="store_true", help="Run baseline + tournament")
    args = parser.parse_args()

    if not any([args.baseline, args.tournament, args.quick, args.blackout_day,
                args.experiment, args.all]):
        args.all = True

    # Load data
    print("Loading dataset...")
    df = load_dataset()
    print(f"  {len(df)} rows, {df.columns.size} columns")
    print(f"  Excursion rate: {df['freq_excursion'].mean():.4f}")

    all_rows = []

    if args.baseline or args.all:
        row = run_baseline(df)
        all_rows.append(row)

    if args.tournament or args.all:
        rows = run_tournament(df)
        all_rows.extend(rows)

    if args.quick:
        print("\nQuick single-fold check:")
        folds = get_cv_folds(df, n_folds=5)
        train_df, val_df = folds[0]
        X_train, y_train = prepare_features(train_df)
        X_val, y_val = prepare_features(val_df)
        scaler = RobustScaler()
        X_train = scaler.fit_transform(X_train)
        X_val = scaler.transform(X_val)
        clf = build_model()
        clf.fit(X_train, y_train)
        y_proba = clf.predict_proba(X_val)[:, 1]
        metrics = compute_metrics(y_val, y_proba)
        print(f"  AUC: {metrics['auc']:.4f}, F2: {metrics['f2']:.4f}")

    if args.blackout_day or args.all:
        run_blackout_day_analysis(df)

    if args.experiment:
        row = run_experiment(df, exp_id=args.experiment,
                             description=args.description)
        all_rows.append(row)

    if all_rows:
        _write_results(all_rows, append=not (args.baseline and not args.tournament))
        print(f"\nResults written to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
