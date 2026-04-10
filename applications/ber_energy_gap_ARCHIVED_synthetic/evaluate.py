"""
Evaluation harness for Irish BER vs Real Home Energy Gap analysis.

Trains a regression model on BER certificate features and evaluates
prediction of the DEAP Energy Value (kWh/m2/yr).

This file is NOT modified during HDR experiments -- only model.py changes.

Usage:
    python evaluate.py                  # Full 5-fold CV evaluation
    python evaluate.py --baseline       # Phase 0.5 baseline only
    python evaluate.py --tournament     # Phase 1 model family tournament
    python evaluate.py --quick          # Single fold quick check
    python evaluate.py --experiment E01 --description "Add regulation_era"
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
    median_absolute_error,
)
from sklearn.preprocessing import RobustScaler

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset, get_cv_folds, get_train_test_split
from model import (
    get_feature_columns, get_model_config, build_model, prepare_features,
    MODEL_FAMILY, CATEGORICAL_FEATURES, EXTRA_CATEGORICAL,
)

RESULTS_FILE = APP_DIR / "results.tsv"

TSV_HEADER = [
    "exp_id", "description", "model_family", "n_features",
    "cv_mae_mean", "cv_mae_std", "cv_rmse_mean", "cv_rmse_std",
    "cv_r2_mean", "cv_r2_std", "cv_median_ae_mean",
    "holdout_mae", "holdout_rmse", "holdout_r2", "holdout_median_ae",
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
    """Compute regression metrics."""
    return {
        "mae": mean_absolute_error(y_true, y_pred),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": r2_score(y_true, y_pred),
        "median_ae": median_absolute_error(y_true, y_pred),
        "n_samples": len(y_true),
    }


def run_cv(df: pd.DataFrame, n_folds: int = 5,
           model_family: str = None) -> dict:
    """Run stratified cross-validation and return aggregated metrics."""
    folds = get_cv_folds(df, n_folds=n_folds)
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
        reg = build_model(family=fam)

        if fam == "ridge":
            reg.fit(X_train_s, y_train)
            y_pred = reg.predict(X_val_s)
        else:
            reg.fit(X_train, y_train)
            y_pred = reg.predict(X_val)

        metrics = compute_metrics(y_val, y_pred)
        fold_metrics.append(metrics)
        print(f"  Fold {i+1}/{n_folds}: MAE={metrics['mae']:.2f}, "
              f"RMSE={metrics['rmse']:.2f}, R2={metrics['r2']:.4f}")

    # Aggregate
    mae_vals = [m["mae"] for m in fold_metrics]
    rmse_vals = [m["rmse"] for m in fold_metrics]
    r2_vals = [m["r2"] for m in fold_metrics]
    medae_vals = [m["median_ae"] for m in fold_metrics]

    return {
        "cv_mae_mean": np.mean(mae_vals),
        "cv_mae_std": np.std(mae_vals),
        "cv_rmse_mean": np.mean(rmse_vals),
        "cv_rmse_std": np.std(rmse_vals),
        "cv_r2_mean": np.mean(r2_vals),
        "cv_r2_std": np.std(r2_vals),
        "cv_median_ae_mean": np.mean(medae_vals),
        "n_folds": n_folds,
    }


def run_holdout(df: pd.DataFrame, model_family: str = None) -> dict:
    """Train on 85%, test on held-out 15%."""
    train_df, test_df = get_train_test_split(df)
    fam = model_family or MODEL_FAMILY

    X_train, y_train = prepare_features(train_df)
    X_test, y_test = prepare_features(test_df)

    scaler = RobustScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    reg = build_model(family=fam)

    if fam == "ridge":
        reg.fit(X_train_s, y_train)
        y_pred = reg.predict(X_test_s)
    else:
        reg.fit(X_train, y_train)
        y_pred = reg.predict(X_test)

    metrics = compute_metrics(y_test, y_pred)

    print(f"\n  Holdout (15%):")
    print(f"    MAE:       {metrics['mae']:.2f} kWh/m2/yr")
    print(f"    RMSE:      {metrics['rmse']:.2f} kWh/m2/yr")
    print(f"    R2:        {metrics['r2']:.4f}")
    print(f"    Median AE: {metrics['median_ae']:.2f} kWh/m2/yr")

    # Per-rating-band analysis
    test_df = test_df.copy()
    test_df["y_pred"] = y_pred
    test_df["y_true"] = y_test
    test_df["residual"] = y_pred - y_test

    print(f"\n  Per-BER-rating MAE:")
    for rating in sorted(test_df["ber_rating"].unique()):
        mask = test_df["ber_rating"] == rating
        if mask.sum() > 10:
            band_mae = mean_absolute_error(
                test_df.loc[mask, "y_true"],
                test_df.loc[mask, "y_pred"]
            )
            print(f"    {rating:>3}: MAE={band_mae:.1f} (n={mask.sum()})")

    return {
        "holdout_mae": metrics["mae"],
        "holdout_rmse": metrics["rmse"],
        "holdout_r2": metrics["r2"],
        "holdout_median_ae": metrics["median_ae"],
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

    print("\n5-fold stratified CV:")
    cv_results = run_cv(df, n_folds=5)
    print(f"\n  CV MAE:  {cv_results['cv_mae_mean']:.2f} +/- {cv_results['cv_mae_std']:.2f}")
    print(f"  CV RMSE: {cv_results['cv_rmse_mean']:.2f} +/- {cv_results['cv_rmse_std']:.2f}")
    print(f"  CV R2:   {cv_results['cv_r2_mean']:.4f} +/- {cv_results['cv_r2_std']:.4f}")

    print("\nHoldout evaluation:")
    holdout_results = run_holdout(df)

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")

    row = {
        "exp_id": "E00",
        "description": "Baseline: XGBoost on raw building characteristics",
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

            print(f"  CV MAE: {cv_results['cv_mae_mean']:.2f} +/- {cv_results['cv_mae_std']:.2f}")

        except Exception as e:
            print(f"  ERROR: {e}")
            row = {
                "exp_id": exp_id,
                "description": f"Tournament: {fam}",
                "model_family": fam,
                "n_features": len(get_feature_columns()),
                "cv_mae_mean": float("nan"),
                "cv_mae_std": float("nan"),
                "cv_rmse_mean": float("nan"),
                "cv_rmse_std": float("nan"),
                "cv_r2_mean": float("nan"),
                "cv_r2_std": float("nan"),
                "cv_median_ae_mean": float("nan"),
                "holdout_mae": float("nan"),
                "holdout_rmse": float("nan"),
                "holdout_r2": float("nan"),
                "holdout_median_ae": float("nan"),
                "notes": f"Phase 1 tournament - FAILED: {e}",
            }
            rows.append(row)

    # Print tournament summary
    print("\n" + "=" * 60)
    print("Tournament Summary")
    print("=" * 60)
    print(f"{'ID':<6} {'Family':<12} {'CV MAE':>10} {'CV R2':>10} {'Holdout MAE':>12} {'Holdout R2':>12}")
    print("-" * 70)
    for r in rows:
        print(f"{r['exp_id']:<6} {r['model_family']:<12} "
              f"{r.get('cv_mae_mean', float('nan')):>10.2f} "
              f"{r.get('cv_r2_mean', float('nan')):>10.4f} "
              f"{r.get('holdout_mae', float('nan')):>12.2f} "
              f"{r.get('holdout_r2', float('nan')):>12.4f}")

    # Select winner (lowest CV MAE)
    valid = [r for r in rows if not np.isnan(r.get("cv_mae_mean", float("nan")))]
    if valid:
        best = min(valid, key=lambda r: r["cv_mae_mean"])
        print(f"\nTournament winner: {best['model_family']} "
              f"(CV MAE = {best['cv_mae_mean']:.2f})")

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

    reg = build_model()
    reg.fit(X_train, y_train)

    if hasattr(reg, "feature_importances_"):
        importances = reg.feature_importances_
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
    parser = argparse.ArgumentParser(description="BER Energy Gap Evaluation Harness")
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
    print(f"  {len(df)} records, {df.columns.size} columns")
    print(f"  Mean energy value: {df['energy_value_kwh_m2_yr'].mean():.1f} kWh/m2/yr")

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
        reg = build_model()
        reg.fit(X_train, y_train)
        y_pred = reg.predict(X_val)
        metrics = compute_metrics(y_val, y_pred)
        print(f"  MAE: {metrics['mae']:.2f}, R2: {metrics['r2']:.4f}")

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
