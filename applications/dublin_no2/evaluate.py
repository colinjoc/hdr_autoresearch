"""
Evaluation harness for Dublin NO2 source attribution.

Trains a model on hourly NO2 features and evaluates prediction quality.
This file is NOT modified during HDR experiments — only model.py changes.

Usage:
    python evaluate.py                  # Full 5-fold CV + holdout evaluation
    python evaluate.py --baseline       # Phase 0.5 baseline only
    python evaluate.py --tournament     # Phase 1 model family tournament
    python evaluate.py --quick          # Single fold quick check
    python evaluate.py --station pearse_street  # Single station evaluation
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
    roc_auc_score,
)
from sklearn.preprocessing import RobustScaler

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import (
    load_dataset, get_cv_folds, get_train_test_split,
    STATIONS, WHO_24H_GUIDELINE, WHO_ANNUAL_GUIDELINE,
)
from model import (
    get_feature_columns, get_model_config, build_model, prepare_features,
    MODEL_FAMILY,
)

RESULTS_FILE = APP_DIR / "results.tsv"

TSV_HEADER = [
    "exp_id", "description", "model_family", "n_features",
    "cv_mae_mean", "cv_mae_std", "cv_r2_mean", "cv_r2_std",
    "cv_exceedance_auc_mean", "cv_exceedance_auc_std",
    "holdout_mae", "holdout_r2", "holdout_exceedance_auc",
    "holdout_mbe",
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


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_true_continuous: np.ndarray = None,
    y_pred_continuous: np.ndarray = None,
    exceedance_threshold: float = WHO_24H_GUIDELINE,
) -> dict:
    """Compute regression metrics for NO2 prediction.

    Also computes exceedance classification AUC if threshold provided.
    """
    metrics = {}
    metrics["mae"] = float(mean_absolute_error(y_true, y_pred))
    metrics["rmse"] = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    metrics["r2"] = float(r2_score(y_true, y_pred))
    metrics["mbe"] = float(np.mean(y_pred - y_true))  # mean bias error
    metrics["n_samples"] = len(y_true)

    # Exceedance AUC
    # Use provided continuous arrays or fall back to y_true/y_pred
    yt = y_true_continuous if y_true_continuous is not None else y_true
    yp = y_pred_continuous if y_pred_continuous is not None else y_pred

    exceedance_true = (yt > exceedance_threshold).astype(int)
    if exceedance_true.sum() > 0 and exceedance_true.sum() < len(exceedance_true):
        try:
            metrics["exceedance_auc"] = float(roc_auc_score(exceedance_true, yp))
        except ValueError:
            metrics["exceedance_auc"] = float("nan")
    else:
        metrics["exceedance_auc"] = float("nan")

    return metrics


def run_cv(
    df: pd.DataFrame, n_folds: int = 5, target_col: str = "no2_ugm3",
    verbose: bool = True,
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
        y_train = train_df[target_col].values
        X_val = val_df[feature_cols].values.astype(np.float32)
        y_val = val_df[target_col].values

        # Scale for linear models
        if config["family"] == "ridge":
            scaler = RobustScaler()
            X_train = scaler.fit_transform(X_train)
            X_val = scaler.transform(X_val)

        # Handle NaN
        nan_mask_train = np.isnan(X_train).any(axis=1) | np.isnan(y_train)
        nan_mask_val = np.isnan(X_val).any(axis=1) | np.isnan(y_val)
        X_train = X_train[~nan_mask_train]
        y_train = y_train[~nan_mask_train]
        X_val = X_val[~nan_mask_val]
        y_val = y_val[~nan_mask_val]

        if len(X_train) == 0 or len(X_val) == 0:
            continue

        model = build_model(config)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)

        metrics = compute_metrics(y_val, y_pred)

        if verbose:
            print(f"  Fold {i+1}/{n_folds}: MAE={metrics['mae']:.2f} "
                  f"R²={metrics['r2']:.3f} "
                  f"ExcAUC={metrics['exceedance_auc']:.3f}")

        fold_metrics.append(metrics)

    # Aggregate
    result = {}
    for key in ["mae", "rmse", "r2", "mbe", "exceedance_auc"]:
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
    df: pd.DataFrame, target_col: str = "no2_ugm3",
    test_months: int = 6, verbose: bool = True,
) -> tuple[dict, object]:
    """Train on all data except last N months, evaluate on holdout."""
    config = get_model_config()
    feature_cols = get_feature_columns()
    train_df, test_df = get_train_test_split(df, test_months)

    X_train = train_df[feature_cols].values.astype(np.float32)
    y_train = train_df[target_col].values
    X_test = test_df[feature_cols].values.astype(np.float32)
    y_test = test_df[target_col].values

    if config["family"] == "ridge":
        scaler = RobustScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    # Handle NaN
    nan_mask = np.isnan(X_train).any(axis=1) | np.isnan(y_train)
    X_train, y_train = X_train[~nan_mask], y_train[~nan_mask]
    nan_mask = np.isnan(X_test).any(axis=1) | np.isnan(y_test)
    X_test, y_test = X_test[~nan_mask], y_test[~nan_mask]

    model = build_model(config)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    metrics = compute_metrics(y_test, y_pred)

    if verbose:
        print(f"\n  Holdout ({test_months} months): MAE={metrics['mae']:.2f} "
              f"R²={metrics['r2']:.3f} MBE={metrics['mbe']:.2f}")
        print(f"  Exceedance AUC: {metrics['exceedance_auc']:.3f}")
        print(f"  N samples: {metrics['n_samples']}")

    # COVID period analysis
    lockdown_mask = test_df.iloc[~np.isnan(X_test).any(axis=1)]["is_lockdown"] == 1 if "is_lockdown" in test_df.columns else None

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
                "cv_mae_mean": f"{cv_result['cv_mae_mean']:.4f}",
                "cv_mae_std": f"{cv_result['cv_mae_std']:.4f}",
                "cv_r2_mean": f"{cv_result['cv_r2_mean']:.4f}",
                "cv_r2_std": f"{cv_result['cv_r2_std']:.4f}",
                "cv_exceedance_auc_mean": f"{cv_result.get('cv_exceedance_auc_mean', float('nan')):.4f}",
                "cv_exceedance_auc_std": f"{cv_result.get('cv_exceedance_auc_std', float('nan')):.4f}",
                "holdout_mae": f"{holdout_result['mae']:.4f}",
                "holdout_r2": f"{holdout_result['r2']:.4f}",
                "holdout_exceedance_auc": f"{holdout_result.get('exceedance_auc', float('nan')):.4f}",
                "holdout_mbe": f"{holdout_result['mbe']:.4f}",
                "notes": "Phase 1 tournament",
            }
            results.append(row)
            print(f"\n  {family}: CV MAE={cv_result['cv_mae_mean']:.2f} "
                  f"R²={cv_result['cv_r2_mean']:.3f} "
                  f"Holdout MAE={holdout_result['mae']:.2f}")

        except Exception as e:
            print(f"  {family} FAILED: {e}")
            import traceback; traceback.print_exc()
            results.append({
                "exp_id": f"T_{family}",
                "description": f"Tournament: {family} (FAILED)",
                "model_family": family,
                "notes": f"Failed: {str(e)[:100]}",
            })

        model_module.MODEL_FAMILY = original_family

    _write_results(results, append=True)
    print("\n  Tournament results written to results.tsv")


def run_source_attribution(df: pd.DataFrame, model=None) -> dict:
    """Phase 2.5: Source attribution from feature importance.

    Decomposes NO2 into source fractions using trained model's
    feature importance pattern:
    - Traffic features → traffic share
    - Heating features → heating share
    - Port/wind features → port share
    - Remainder → background/regional
    """
    if model is None:
        # Train a model on all data
        config = get_model_config()
        feature_cols = get_feature_columns()
        X = df[feature_cols].values.astype(np.float32)
        y = df["no2_ugm3"].values
        nan_mask = np.isnan(X).any(axis=1) | np.isnan(y)
        model = build_model(config)
        model.fit(X[~nan_mask], y[~nan_mask])

    feature_cols = get_feature_columns()

    # Get feature importance
    try:
        importances = model.feature_importances_
    except AttributeError:
        # Ridge: use coefficient magnitudes
        importances = np.abs(model.coef_)

    imp_dict = dict(zip(feature_cols, importances))
    total_imp = sum(importances)

    # Categorize features into source groups
    traffic_features = [
        "rush_hour", "rush_hour_weekday", "rush_wind_dir_traffic",
        "wind_dir_traffic", "is_weekend", "dow_sin", "dow_cos",
    ]
    heating_features = [
        "is_heating_season", "cold_evening", "temp_heating_interaction",
        "temperature_c", "month_sin", "month_cos",
    ]
    port_features = [
        "wind_dir_port", "port_activity",
    ]
    dispersion_features = [
        "wind_speed_ms", "blh_proxy_m", "wind_x_blh",
        "inverse_ventilation", "calm_wind", "rain_washout", "rainfall_mm",
    ]
    temporal_features = [
        "hour_sin", "hour_cos",
    ]

    def _group_importance(group_feats):
        return sum(imp_dict.get(f, 0) for f in group_feats)

    traffic_imp = _group_importance(traffic_features)
    heating_imp = _group_importance(heating_features)
    port_imp = _group_importance(port_features)
    dispersion_imp = _group_importance(dispersion_features)
    temporal_imp = _group_importance(temporal_features)
    other_imp = total_imp - traffic_imp - heating_imp - port_imp - dispersion_imp - temporal_imp

    attribution = {
        "traffic_share": traffic_imp / total_imp if total_imp > 0 else 0,
        "heating_share": heating_imp / total_imp if total_imp > 0 else 0,
        "port_share": port_imp / total_imp if total_imp > 0 else 0,
        "dispersion_share": dispersion_imp / total_imp if total_imp > 0 else 0,
        "temporal_share": temporal_imp / total_imp if total_imp > 0 else 0,
        "other_share": other_imp / total_imp if total_imp > 0 else 0,
        "feature_importances": imp_dict,
    }

    return attribution


def main():
    parser = argparse.ArgumentParser(description="Dublin NO2 evaluation")
    parser.add_argument("--baseline", action="store_true", help="Phase 0.5 baseline")
    parser.add_argument("--tournament", action="store_true", help="Phase 1 tournament")
    parser.add_argument("--quick", action="store_true", help="Single fold quick check")
    parser.add_argument("--station", type=str, default=None, help="Single station")
    parser.add_argument("--attribution", action="store_true", help="Source attribution")
    parser.add_argument("--exp-id", type=str, default=None)
    parser.add_argument("--description", type=str, default=None)
    args = parser.parse_args()

    print("=" * 60)
    print("  Dublin/Cork NO2 Source Attribution")
    print("=" * 60)

    # Load data
    df = load_dataset()
    df = prepare_features(df)

    # Filter to single station if requested
    if args.station:
        df = df[df["station"] == args.station]
        print(f"\n  Filtered to station: {args.station}")

    feature_cols = get_feature_columns()
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        print(f"  WARNING: Missing features: {missing}")
        return

    # Drop NaN target rows
    df = df.dropna(subset=["no2_ugm3"])

    print(f"\n  Dataset: {len(df)} rows, {len(feature_cols)} features")
    print(f"  Stations: {sorted(df['station'].unique())}")
    print(f"  Mean NO2: {df['no2_ugm3'].mean():.1f} ug/m3")
    print(f"  WHO 24h exceedances: {df['exceeds_who_24h'].sum()}")
    print(f"  Model family: {MODEL_FAMILY}")

    if args.tournament:
        run_tournament(df)
        return

    if args.attribution:
        print(f"\n{'='*60}")
        print("  Source Attribution (Phase 2.5)")
        print(f"{'='*60}")
        attr = run_source_attribution(df)
        print(f"\n  Traffic share:    {attr['traffic_share']:.1%}")
        print(f"  Heating share:    {attr['heating_share']:.1%}")
        print(f"  Port share:       {attr['port_share']:.1%}")
        print(f"  Dispersion share: {attr['dispersion_share']:.1%}")
        print(f"  Temporal share:   {attr['temporal_share']:.1%}")
        print(f"  Other share:      {attr['other_share']:.1%}")
        return

    # Run CV
    print(f"\n{'='*60}")
    print("  5-Fold Temporal Cross-Validation")
    print(f"{'='*60}")

    n_folds = 1 if args.quick else 5
    t0 = time.time()
    cv_result = run_cv(df, n_folds=n_folds, verbose=True)
    cv_time = time.time() - t0
    print(f"\n  CV MAE: {cv_result['cv_mae_mean']:.2f} +/- {cv_result['cv_mae_std']:.2f}")
    print(f"  CV R²:  {cv_result['cv_r2_mean']:.3f} +/- {cv_result['cv_r2_std']:.3f}")
    print(f"  CV Exceedance AUC: {cv_result.get('cv_exceedance_auc_mean', float('nan')):.3f}")
    print(f"  Time: {cv_time:.1f}s")

    # Run holdout
    print(f"\n{'='*60}")
    print("  Holdout Evaluation (last 6 months)")
    print(f"{'='*60}")
    holdout_result, model = run_holdout(df, verbose=True)

    # Record results
    exp_id = args.exp_id or ("E00" if args.baseline else "E_latest")
    description = args.description or ("Baseline: met+temporal features" if args.baseline else "Latest run")

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": MODEL_FAMILY,
        "n_features": cv_result["n_features"],
        "cv_mae_mean": f"{cv_result['cv_mae_mean']:.4f}",
        "cv_mae_std": f"{cv_result['cv_mae_std']:.4f}",
        "cv_r2_mean": f"{cv_result['cv_r2_mean']:.4f}",
        "cv_r2_std": f"{cv_result['cv_r2_std']:.4f}",
        "cv_exceedance_auc_mean": f"{cv_result.get('cv_exceedance_auc_mean', float('nan')):.4f}",
        "cv_exceedance_auc_std": f"{cv_result.get('cv_exceedance_auc_std', float('nan')):.4f}",
        "holdout_mae": f"{holdout_result['mae']:.4f}",
        "holdout_r2": f"{holdout_result['r2']:.4f}",
        "holdout_exceedance_auc": f"{holdout_result.get('exceedance_auc', float('nan')):.4f}",
        "holdout_mbe": f"{holdout_result['mbe']:.4f}",
        "notes": description,
    }
    _write_results([row], append=True)
    print(f"\n  Results written to {RESULTS_FILE}")

    # Feature importance
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        importance_pairs = sorted(
            zip(feature_cols, importances),
            key=lambda x: x[1], reverse=True,
        )
        print(f"\n  Top-10 Feature Importances:")
        for name, imp in importance_pairs[:10]:
            print(f"    {name:35s} {imp:.4f}")


if __name__ == "__main__":
    main()
