"""
Evaluation harness for Irish Radon Prediction.

Binary classification: predict High Radon Area (>10% homes above 200 Bq/m3).
Uses spatial cross-validation grouped by county to avoid spatial leakage.

This file is NOT modified during HDR experiments — only model.py changes.

Usage:
    python evaluate.py                  # Full spatial CV evaluation
    python evaluate.py --baseline       # Phase 0.5 baseline only
    python evaluate.py --tournament     # Phase 1 model family tournament
    python evaluate.py --quick          # Single fold quick check
    python evaluate.py --experiment E01 --description "Add eU/eTh ratio"
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
    precision_recall_curve, confusion_matrix,
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
    auc = roc_auc_score(y_true, y_prob)
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
        "n_predicted_positive": int(y_pred.sum()),
    }


def run_cv(df: pd.DataFrame, n_folds: int = 5,
           model_family: str = None) -> dict:
    """Run spatial cross-validation and return aggregated metrics.

    Folds are grouped by county to prevent spatial leakage.
    """
    folds = get_cv_folds_spatial(df, n_folds=n_folds)
    fam = model_family or MODEL_FAMILY

    fold_metrics = []

    for i, (train_df, val_df) in enumerate(folds):
        X_train, y_train = prepare_features(train_df)
        X_val, y_val = prepare_features(val_df)

        # Scale for Ridge; tree methods don't need it but it doesn't hurt
        scaler = RobustScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_val_s = scaler.transform(X_val)

        # Train
        clf = build_model(family=fam)

        if fam == "ridge":
            clf.fit(X_train_s, y_train)
            y_prob = clf.predict_proba(X_val_s)[:, 1]
        else:
            clf.fit(X_train, y_train)
            y_prob = clf.predict_proba(X_val)[:, 1]

        metrics = compute_metrics(y_val, y_prob)
        fold_metrics.append(metrics)

        val_counties = sorted(val_df["county"].unique())
        print(f"  Fold {i+1}/{n_folds}: AUC={metrics['auc']:.4f}, "
              f"F1={metrics['f1']:.4f}, P={metrics['precision']:.4f}, "
              f"R={metrics['recall']:.4f} "
              f"[{','.join(val_counties[:3])}{'...' if len(val_counties)>3 else ''}]")

    # Aggregate
    auc_vals = [m["auc"] for m in fold_metrics]
    f1_vals = [m["f1"] for m in fold_metrics]
    prec_vals = [m["precision"] for m in fold_metrics]
    rec_vals = [m["recall"] for m in fold_metrics]

    return {
        "cv_auc_mean": np.mean(auc_vals),
        "cv_auc_std": np.std(auc_vals),
        "cv_f1_mean": np.mean(f1_vals),
        "cv_f1_std": np.std(f1_vals),
        "cv_precision_mean": np.mean(prec_vals),
        "cv_recall_mean": np.mean(rec_vals),
        "n_folds": n_folds,
    }


def run_holdout(df: pd.DataFrame, model_family: str = None) -> dict:
    """Train on ~85%, test on held-out counties."""
    train_df, test_df = get_train_test_split(df)
    fam = model_family or MODEL_FAMILY

    X_train, y_train = prepare_features(train_df)
    X_test, y_test = prepare_features(test_df)

    scaler = RobustScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    clf = build_model(family=fam)

    if fam == "ridge":
        clf.fit(X_train_s, y_train)
        y_prob = clf.predict_proba(X_test_s)[:, 1]
    else:
        clf.fit(X_train, y_train)
        y_prob = clf.predict_proba(X_test)[:, 1]

    metrics = compute_metrics(y_test, y_prob)

    test_counties = sorted(test_df["county"].unique())
    print(f"\n  Holdout (counties: {', '.join(test_counties)}):")
    print(f"    AUC:       {metrics['auc']:.4f}")
    print(f"    F1:        {metrics['f1']:.4f}")
    print(f"    Precision: {metrics['precision']:.4f}")
    print(f"    Recall:    {metrics['recall']:.4f}")
    print(f"    n_test:    {metrics['n_samples']}")
    print(f"    n_positive:{metrics['n_positive']}")

    # Per-county analysis
    test_df = test_df.copy()
    test_df["y_prob"] = y_prob
    test_df["y_true"] = y_test

    print(f"\n  Per-county AUC:")
    for county in test_counties:
        mask = test_df["county"] == county
        if mask.sum() > 10:
            county_true = test_df.loc[mask, "y_true"].values
            county_prob = test_df.loc[mask, "y_prob"].values
            if len(np.unique(county_true)) > 1:
                county_auc = roc_auc_score(county_true, county_prob)
                print(f"    {county:>15}: AUC={county_auc:.4f} (n={mask.sum()})")

    return {
        "holdout_auc": metrics["auc"],
        "holdout_f1": metrics["f1"],
        "holdout_precision": metrics["precision"],
        "holdout_recall": metrics["recall"],
    }


def run_baseline(df: pd.DataFrame) -> dict:
    """Run Phase 0.5 baseline evaluation."""
    print("=" * 60)
    print("Phase 0.5: Baseline Evaluation")
    print(f"  Model family: {MODEL_FAMILY}")
    print(f"  Features: {len(get_feature_columns())}")
    print(f"  Feature list: {get_feature_columns()}")
    print(f"  Target: is_hra (>10% homes above 200 Bq/m3)")
    print(f"  Positive class prevalence: {df['is_hra'].mean()*100:.1f}%")
    print("=" * 60)

    t0 = time.time()

    print("\n5-fold spatial CV (grouped by county):")
    cv_results = run_cv(df, n_folds=5)
    print(f"\n  CV AUC:       {cv_results['cv_auc_mean']:.4f} +/- {cv_results['cv_auc_std']:.4f}")
    print(f"  CV F1:        {cv_results['cv_f1_mean']:.4f} +/- {cv_results['cv_f1_std']:.4f}")
    print(f"  CV Precision: {cv_results['cv_precision_mean']:.4f}")
    print(f"  CV Recall:    {cv_results['cv_recall_mean']:.4f}")

    print("\nHoldout evaluation:")
    holdout_results = run_holdout(df)

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")

    row = {
        "exp_id": "E00",
        "description": "Baseline: XGBoost on raw Tellus radiometric + geology + coords",
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
                "cv_f1_mean": float("nan"),
                "cv_f1_std": float("nan"),
                "cv_precision_mean": float("nan"),
                "cv_recall_mean": float("nan"),
                "holdout_auc": float("nan"),
                "holdout_f1": float("nan"),
                "holdout_precision": float("nan"),
                "holdout_recall": float("nan"),
                "notes": f"Phase 1 tournament - FAILED: {e}",
            }
            rows.append(row)

    # Print tournament summary
    print("\n" + "=" * 60)
    print("Tournament Summary")
    print("=" * 60)
    print(f"{'ID':<6} {'Family':<12} {'CV AUC':>10} {'CV F1':>10} "
          f"{'Holdout AUC':>12} {'Holdout F1':>12}")
    print("-" * 70)
    for r in rows:
        print(f"{r['exp_id']:<6} {r['model_family']:<12} "
              f"{r.get('cv_auc_mean', float('nan')):>10.4f} "
              f"{r.get('cv_f1_mean', float('nan')):>10.4f} "
              f"{r.get('holdout_auc', float('nan')):>12.4f} "
              f"{r.get('holdout_f1', float('nan')):>12.4f}")

    # Select winner (highest CV AUC)
    valid = [r for r in rows if not np.isnan(r.get("cv_auc_mean", float("nan")))]
    if valid:
        best = min(valid, key=lambda r: -r["cv_auc_mean"])
        print(f"\nTournament winner: {best['model_family']} "
              f"(CV AUC = {best['cv_auc_mean']:.4f})")

    return rows


def run_experiment(df: pd.DataFrame, exp_id: str, description: str,
                   notes: str = "") -> dict:
    """Run a single HDR experiment with current model.py configuration."""
    print(f"\n{'=' * 60}")
    print(f"Experiment: {exp_id} -- {description}")
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


def run_feature_importance(df: pd.DataFrame) -> dict:
    """Train on full data and report feature importances."""
    print("\n" + "=" * 60)
    print("Feature Importance Analysis")
    print("=" * 60)

    train_df, test_df = get_train_test_split(df)
    X_train, y_train = prepare_features(train_df)

    clf = build_model()
    clf.fit(X_train, y_train)

    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
        feature_cols = get_feature_columns()
        importance_pairs = sorted(zip(feature_cols, importances),
                                  key=lambda x: -x[1])
        print(f"\n  Feature importances (top 20):")
        for fname, imp in importance_pairs[:20]:
            bar = "#" * int(imp * 200)
            print(f"    {fname:>30}: {imp:.4f} {bar}")

        return {f"importance_{f}": float(v) for f, v in importance_pairs[:20]}

    return {}


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Irish Radon Evaluation Harness")
    parser.add_argument("--baseline", action="store_true", help="Run Phase 0.5 baseline")
    parser.add_argument("--tournament", action="store_true", help="Run Phase 1 tournament")
    parser.add_argument("--quick", action="store_true", help="Quick single-fold check")
    parser.add_argument("--importance", action="store_true", help="Feature importance analysis")
    parser.add_argument("--experiment", type=str, help="Run experiment with ID")
    parser.add_argument("--description", type=str, default="", help="Experiment description")
    parser.add_argument("--all", action="store_true", help="Run baseline + tournament")
    args = parser.parse_args()

    if not any([args.baseline, args.tournament, args.quick, args.importance,
                args.experiment, args.all]):
        args.all = True

    # Load data
    print("Loading dataset...")
    df = load_dataset()
    print(f"  {len(df)} areas, {df.columns.size} columns")
    print(f"  HRA prevalence: {df['is_hra'].mean()*100:.1f}%")

    all_rows = []

    if args.baseline or args.all:
        row = run_baseline(df)
        all_rows.append(row)

    if args.tournament or args.all:
        rows = run_tournament(df)
        all_rows.extend(rows)

    if args.quick:
        print("\nQuick single-fold check:")
        folds = get_cv_folds_spatial(df, n_folds=5)
        train_df, val_df = folds[0]
        X_train, y_train = prepare_features(train_df)
        X_val, y_val = prepare_features(val_df)
        clf = build_model()
        clf.fit(X_train, y_train)
        y_prob = clf.predict_proba(X_val)[:, 1]
        metrics = compute_metrics(y_val, y_prob)
        print(f"  AUC: {metrics['auc']:.4f}, F1: {metrics['f1']:.4f}")

    if args.importance or args.all:
        run_feature_importance(df)

    if args.experiment:
        row = run_experiment(df, exp_id=args.experiment,
                             description=args.description)
        all_rows.append(row)

    if all_rows:
        _write_results(all_rows, append=not (args.baseline and not args.tournament))
        print(f"\nResults written to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
