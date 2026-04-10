"""5-fold CV harness for Phase 0.5 baseline + Phase 1 tournament.

Usage:
    python evaluate.py                   # run E00 + tournament, write results.tsv
    python evaluate.py --build-cache     # rebuild heat_mortality_master.parquet
    python evaluate.py --only baseline   # just E00
    python evaluate.py --reset-results   # overwrite results.tsv with the header

Metrics (all out-of-fold on 5 shuffled folds, seed=42):
    - MAE / RMSE / R²   on ``excess_deaths`` (the regression target)
    - AUC / Brier       on the binary ``label_lethal_heatwave`` target
    - MAE_p             MAE in P-score units (MAE_deaths / mean baseline)
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    brier_score_loss,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold

from model import (  # noqa: E402
    BASELINE_FEATURES,
    BASELINE_FEATURES_WITH_CITY,
    CITIES_FOR_BASELINE,
    TOURNAMENT,
    add_features,
    build_clean_dataset,
    label_lethal_heatwave,
    make_baseline_xgb,
    make_extratrees,
    make_lightgbm,
    make_randomforest,
    make_ridge,
)

HERE = Path(__file__).resolve().parent
CLEAN_PATH = HERE / "data" / "clean" / "heat_mortality_master.parquet"
RESULTS_PATH = HERE / "results.tsv"


# ----------------------------------------------------------------- dataset build

def build_clean_cache(start_year: int = 2013, end_year: int = 2024) -> pd.DataFrame:
    """Build the master (city × week) panel via data_loaders.build_master_dataset.

    Caches the raw (pre-clean) output to ``data/clean/heat_mortality_master.parquet``.
    """
    from data_loaders import build_master_dataset  # lazy — needs network on miss

    t0 = time.time()
    df = build_master_dataset(
        city_names=CITIES_FOR_BASELINE,
        start_year=start_year,
        end_year=end_year,
        use_era5=False,
        verbose=True,
    )
    print(f"  master rows={len(df)} cols={df.shape[1]} wall={time.time()-t0:.1f}s")
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CLEAN_PATH, index=False)
    print(f"  cached -> {CLEAN_PATH}")
    return df


def load_clean(build_if_missing: bool = True,
               start_year: int = 2013, end_year: int = 2024) -> pd.DataFrame:
    if CLEAN_PATH.exists():
        return pd.read_parquet(CLEAN_PATH)
    if not build_if_missing:
        raise FileNotFoundError(f"{CLEAN_PATH} missing; run with --build-cache")
    return build_clean_cache(start_year=start_year, end_year=end_year)


# ----------------------------------------------------------------- metrics

def compute_metrics(y_true_deaths: np.ndarray, y_pred_deaths: np.ndarray,
                    expected_baseline: np.ndarray,
                    y_true_binary: np.ndarray) -> dict:
    """All Phase 0.5 metrics on one OOF prediction set.

    Regression: MAE/RMSE/R² on ``excess_deaths``; MAE in P-score units.
    Binary: derive the predicted binary score by converting the regression
    output to a p_score proxy (``y_pred_deaths / expected_baseline``),
    clipping to [0,1] so AUC/Brier see a bounded score.
    """
    y_true_deaths = np.asarray(y_true_deaths, dtype="float64")
    y_pred_deaths = np.asarray(y_pred_deaths, dtype="float64")
    expected_baseline = np.asarray(expected_baseline, dtype="float64")
    y_true_binary = np.asarray(y_true_binary, dtype="int64")

    mae = float(mean_absolute_error(y_true_deaths, y_pred_deaths))
    rmse = float(np.sqrt(mean_squared_error(y_true_deaths, y_pred_deaths)))
    r2 = float(r2_score(y_true_deaths, y_pred_deaths))

    # P-score MAE = MAE(deaths) / mean(expected_baseline). A global rescaling
    # gives a dimensionless number we can compare against the +/-10% signal.
    mean_exp = float(np.nanmean(expected_baseline)) if len(expected_baseline) else 1.0
    mae_p = mae / mean_exp if mean_exp > 0 else float("nan")

    # Binary metrics — convert predicted excess -> predicted p-score proxy.
    safe_exp = np.where(expected_baseline > 0, expected_baseline, np.nan)
    p_pred = y_pred_deaths / safe_exp
    # Map the p-score proxy into a bounded pseudo-probability. A p-score of
    # +0.10 ≈ threshold -> ~0.5. Use a logistic with centre=0.10 and slope=10
    # so ±0.05 moves probability by ~12 points.
    scores = 1.0 / (1.0 + np.exp(-10.0 * (np.nan_to_num(p_pred, nan=0.0) - 0.10)))

    auc = float("nan")
    brier = float("nan")
    n_pos = int(y_true_binary.sum())
    n_neg = int(len(y_true_binary) - n_pos)
    if n_pos >= 1 and n_neg >= 1:
        try:
            auc = float(roc_auc_score(y_true_binary, scores))
        except ValueError:
            auc = float("nan")
        try:
            brier = float(brier_score_loss(y_true_binary, scores))
        except ValueError:
            brier = float("nan")

    return {
        "mae_deaths": mae,
        "rmse_deaths": rmse,
        "r2": r2,
        "mae_p": mae_p,
        "auc_lethal": auc,
        "brier_lethal": brier,
        "n_pos": n_pos,
        "n_neg": n_neg,
    }


# ----------------------------------------------------------------- CV harness

def cross_validate(df: pd.DataFrame, model_factory, n_splits: int = 5,
                   seed: int = 42, verbose: bool = True) -> dict:
    """5-fold KFold CV on the cleaned panel.

    Adds features once, then shuffled-KFold splits. Returns metrics dict.
    """
    df = df.reset_index(drop=True)
    df = add_features(df)

    feature_cols = BASELINE_FEATURES_WITH_CITY
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0.0

    X = df[feature_cols].astype("float32").values
    y = df["excess_deaths"].astype("float64").values
    exp_b = df["expected_baseline"].astype("float64").values
    y_bin = label_lethal_heatwave(df)

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof = np.zeros(len(df), dtype="float64")
    fold_mae = []
    fold_auc = []
    for fold_idx, (tr_idx, va_idx) in enumerate(kf.split(df)):
        X_tr, X_va = X[tr_idx], X[va_idx]
        y_tr = y[tr_idx]
        y_va = y[va_idx]
        m = model_factory()
        m.fit(X_tr, y_tr)
        pred = m.predict(X_va)
        oof[va_idx] = pred
        fold_mae.append(float(mean_absolute_error(y_va, pred)))
        # per-fold AUC if both classes present
        y_bin_va = y_bin[va_idx]
        exp_va = exp_b[va_idx]
        if y_bin_va.sum() >= 1 and (len(y_bin_va) - y_bin_va.sum()) >= 1:
            safe_exp = np.where(exp_va > 0, exp_va, np.nan)
            p_pred = pred / safe_exp
            s = 1.0 / (1.0 + np.exp(-10.0 * (np.nan_to_num(p_pred, nan=0.0) - 0.10)))
            try:
                fold_auc.append(float(roc_auc_score(y_bin_va, s)))
            except ValueError:
                fold_auc.append(float("nan"))
        else:
            fold_auc.append(float("nan"))
        if verbose:
            print(f"    fold {fold_idx}: MAE={fold_mae[-1]:8.2f} deaths  "
                  f"AUC={fold_auc[-1]:.3f}  "
                  f"n_train={len(tr_idx):5d}  n_valid={len(va_idx):5d}")

    metrics = compute_metrics(y, oof, exp_b, y_bin)
    metrics["fold_mae"] = fold_mae
    metrics["fold_auc"] = fold_auc
    return metrics


# ----------------------------------------------------------------- results TSV

RESULTS_HEADER = (
    "exp_id\tdescription\tmodel\textra_features\t"
    "cv_mae_deaths\tcv_rmse_deaths\tcv_r2\tcv_auc_lethal\tcv_brier_lethal\tnotes"
)


def _init_results(path: Path) -> None:
    if not path.exists():
        path.write_text(RESULTS_HEADER + "\n")


def _append_result(path: Path, exp_id: str, description: str, model: str,
                   extra_features: str, metrics: dict, notes: str) -> None:
    _init_results(path)
    row = "\t".join([
        exp_id, description, model, extra_features,
        f"{metrics['mae_deaths']:.3f}",
        f"{metrics['rmse_deaths']:.3f}",
        f"{metrics['r2']:.4f}",
        f"{metrics['auc_lethal']:.4f}" if not np.isnan(metrics['auc_lethal']) else "nan",
        f"{metrics['brier_lethal']:.4f}" if not np.isnan(metrics['brier_lethal']) else "nan",
        notes,
    ])
    with path.open("a") as f:
        f.write(row + "\n")


def _reset_results(path: Path) -> None:
    path.write_text(RESULTS_HEADER + "\n")


# ----------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-cache", action="store_true",
                    help="force rebuild of heat_mortality_master.parquet")
    ap.add_argument("--start-year", type=int, default=2013)
    ap.add_argument("--end-year", type=int, default=2024)
    ap.add_argument("--only", choices=["baseline", "tournament", "all"], default="all")
    ap.add_argument("--reset-results", action="store_true",
                    help="overwrite results.tsv with just the header")
    args = ap.parse_args()

    if args.build_cache or not CLEAN_PATH.exists():
        raw = build_clean_cache(start_year=args.start_year, end_year=args.end_year)
    else:
        raw = pd.read_parquet(CLEAN_PATH)
        print(f"loaded cached master: {len(raw)} rows from {CLEAN_PATH}")

    print("\nraw per-city counts:")
    print(raw["city"].value_counts().sort_index().to_string())

    clean = build_clean_dataset(raw)
    print(f"\nafter Phase 0.5 clean: {len(clean)} rows (dropped {len(raw)-len(clean)})")
    print("clean per-city counts:")
    print(clean["city"].value_counts().sort_index().to_string())

    if args.reset_results:
        _reset_results(RESULTS_PATH)
    else:
        _init_results(RESULTS_PATH)

    # Pre-compute label stats for transparency.
    feat = add_features(clean)
    y_bin = label_lethal_heatwave(feat)
    print(f"\nlethal-heatwave positives: {int(y_bin.sum())} / {len(y_bin)} "
          f"({y_bin.mean():.1%})")

    tag = f"5-fold CV, n={len(clean)}, cities={clean['city'].nunique()}"

    best_mae = None
    best_name = None

    if args.only in ("baseline", "all"):
        print("\n=== E00: baseline XGBoost (no night-time wet-bulb) ===")
        t0 = time.time()
        metrics = cross_validate(clean, make_baseline_xgb)
        dt = time.time() - t0
        print(f"  MAE={metrics['mae_deaths']:.2f} deaths  "
              f"RMSE={metrics['rmse_deaths']:.2f}  "
              f"R2={metrics['r2']:.4f}  "
              f"AUC={metrics['auc_lethal']:.3f}  "
              f"Brier={metrics['brier_lethal']:.4f}  "
              f"MAE_p={metrics['mae_p']:.3%}  "
              f"wall={dt:.1f}s")
        _append_result(RESULTS_PATH, "E00",
                       "Phase 0.5 atmospheric-only baseline",
                       "xgboost", "BASELINE", metrics,
                       f"{tag}, wall={dt:.1f}s")
        best_mae = metrics["mae_deaths"]
        best_name = "xgboost"

    ridge_mae = None

    if args.only in ("tournament", "all"):
        for exp_id_full, factory in TOURNAMENT.items():
            exp_id, family = exp_id_full.split("_", 1)
            print(f"\n=== {exp_id}: {family} ===")
            t0 = time.time()
            metrics = cross_validate(clean, factory)
            dt = time.time() - t0
            print(f"  MAE={metrics['mae_deaths']:.2f} deaths  "
                  f"RMSE={metrics['rmse_deaths']:.2f}  "
                  f"R2={metrics['r2']:.4f}  "
                  f"AUC={metrics['auc_lethal']:.3f}  "
                  f"Brier={metrics['brier_lethal']:.4f}  "
                  f"wall={dt:.1f}s")
            _append_result(RESULTS_PATH, exp_id, f"Tournament {family}",
                           family, "BASELINE", metrics,
                           f"{tag}, wall={dt:.1f}s")
            if best_mae is None or metrics["mae_deaths"] < best_mae:
                best_mae = metrics["mae_deaths"]
                best_name = family
            if family == "ridge":
                ridge_mae = metrics["mae_deaths"]

    # Tree-to-linear ratio — the smallest tree MAE divided by Ridge MAE.
    if ridge_mae is not None and best_mae is not None and ridge_mae > 0:
        # best_tree is the minimum of non-ridge MAEs; fall back to best_mae.
        best_tree = best_mae  # tournament orders ridge last
        ratio = best_tree / ridge_mae
        verdict = (
            "TREES DO NON-LINEAR WORK (ratio < 0.5)" if ratio < 0.5
            else "RELATIONSHIP MOSTLY LINEAR (ratio >= 0.5, flag)"
        )
        print(f"\ntree-to-linear ratio: best_tree_MAE / ridge_MAE = "
              f"{best_tree:.2f} / {ridge_mae:.2f} = {ratio:.3f} -- {verdict}")
    print(f"\nidentified winner: {best_name}  (MAE={best_mae:.2f} deaths)")
    print(f"\nresults written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
