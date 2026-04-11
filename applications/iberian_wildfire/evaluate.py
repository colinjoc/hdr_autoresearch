"""Temporal CV harness for Iberian wildfire VLF prediction.

Uses strict temporal cross-validation: train on years < test_year,
test on test_year. This prevents any future information leakage.

Usage:
    python evaluate.py                     # run all phases
    python evaluate.py --only baseline     # just Phase 0.5
    python evaluate.py --only tournament   # just Phase 1
    python evaluate.py --only phase2       # Phase 2 feature experiments
    python evaluate.py --only comparison   # Phase 2.5 FWI vs LFMC vs SPEI
    python evaluate.py --only phase_b      # Phase B risk mapping

Metrics:
    - AUC (primary)
    - Brier score
    - F2 score (recall-weighted)
    - Precision / Recall at optimal threshold
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    brier_score_loss,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from data_loaders import (
    BASELINE_FEATURES,
    add_features,
    add_land_cover_features,
    build_modelling_dataset,
    label_vlf_week,
)
from model import (
    DROUGHT_PROXY_FEATURES,
    FWI_PROXY_FEATURES,
    LFMC_PROXY_FEATURES,
    TOURNAMENT,
    get_baseline_features,
    get_phase2_features,
    make_ridge,
    make_xgboost,
)
from data_loaders import load_effis_weekly, add_features

HERE = Path(__file__).resolve().parent
RESULTS_PATH = HERE / "results.tsv"
DISCOVERIES_DIR = HERE / "discoveries"


# ---------------------------------------------------------------- temporal CV

def temporal_cv(df: pd.DataFrame, model_factory, feature_cols: list,
                test_years: list | None = None, min_train_years: int = 3,
                verbose: bool = True) -> dict:
    """Temporal cross-validation: train on past, predict future.

    For each test_year, trains on all data from years strictly before
    test_year (requiring at least min_train_years of history).

    Returns dict with overall and per-fold metrics.
    """
    if test_years is None:
        all_years = sorted(df["year"].unique())
        test_years = [y for y in all_years if y >= all_years[0] + min_train_years]

    all_true = []
    all_proba = []
    fold_metrics = []

    for test_year in test_years:
        train = df[df["year"] < test_year].copy()
        test = df[df["year"] == test_year].copy()

        if len(train) == 0 or len(test) == 0:
            continue

        y_train = train["vlf"].values
        y_test = test["vlf"].values

        # Skip folds with no positive class in train
        if y_train.sum() == 0:
            continue

        # Ensure feature columns exist
        avail_cols = [c for c in feature_cols if c in train.columns]
        X_train = train[avail_cols].astype("float64").values
        X_test = test[avail_cols].astype("float64").values

        # Replace NaN/Inf with 0
        X_train = np.nan_to_num(X_train, nan=0.0, posinf=0.0, neginf=0.0)
        X_test = np.nan_to_num(X_test, nan=0.0, posinf=0.0, neginf=0.0)

        model = model_factory()
        model.fit(X_train, y_train)

        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X_test)[:, 1]
        else:
            proba = model.predict(X_test).astype(float)

        all_true.extend(y_test.tolist())
        all_proba.extend(proba.tolist())

        # Per-fold metrics
        fold_auc = float("nan")
        if y_test.sum() >= 1 and (len(y_test) - y_test.sum()) >= 1:
            try:
                fold_auc = float(roc_auc_score(y_test, proba))
            except ValueError:
                pass

        fold_metrics.append({
            "test_year": test_year,
            "n_train": len(train),
            "n_test": len(test),
            "n_pos_train": int(y_train.sum()),
            "n_pos_test": int(y_test.sum()),
            "auc": fold_auc,
        })

        if verbose:
            print(f"    {test_year}: n_train={len(train):4d} n_test={len(test):3d} "
                  f"pos_train={int(y_train.sum()):3d} pos_test={int(y_test.sum()):3d} "
                  f"AUC={fold_auc:.3f}")

    # Overall metrics
    y_true = np.array(all_true, dtype="int64")
    y_proba = np.array(all_proba, dtype="float64")

    metrics = compute_metrics(y_true, y_proba)
    metrics["fold_metrics"] = fold_metrics
    metrics["n_folds"] = len(fold_metrics)
    return metrics


def compute_metrics(y_true: np.ndarray, y_proba: np.ndarray) -> dict:
    """Compute all metrics from true labels and predicted probabilities."""
    y_true = np.asarray(y_true, dtype="int64")
    y_proba = np.asarray(y_proba, dtype="float64")

    n_pos = int(y_true.sum())
    n_neg = int(len(y_true) - n_pos)

    auc = float("nan")
    brier = float("nan")
    f2 = float("nan")
    precision = float("nan")
    recall = float("nan")

    if n_pos >= 1 and n_neg >= 1:
        try:
            auc = float(roc_auc_score(y_true, y_proba))
        except ValueError:
            pass
        try:
            brier = float(brier_score_loss(y_true, y_proba))
        except ValueError:
            pass

        # Optimize threshold for F2
        best_f2 = 0.0
        best_thresh = 0.5
        for thresh in np.arange(0.1, 0.9, 0.05):
            y_pred = (y_proba >= thresh).astype(int)
            try:
                f = float(fbeta_score(y_true, y_pred, beta=2))
                if f > best_f2:
                    best_f2 = f
                    best_thresh = thresh
            except ValueError:
                pass

        y_pred_best = (y_proba >= best_thresh).astype(int)
        f2 = best_f2
        try:
            precision = float(precision_score(y_true, y_pred_best, zero_division=0))
            recall = float(recall_score(y_true, y_pred_best, zero_division=0))
        except ValueError:
            pass

    return {
        "auc": auc,
        "brier": brier,
        "f2": f2,
        "precision": precision,
        "recall": recall,
        "n_pos": n_pos,
        "n_neg": n_neg,
        "n_total": n_pos + n_neg,
    }


# ---------------------------------------------------------------- holdout evaluation

def holdout_eval(df: pd.DataFrame, model_factory, feature_cols: list,
                 holdout_year: int = 2025, verbose: bool = True) -> dict:
    """Train on all years < holdout_year, test on holdout_year."""
    train = df[df["year"] < holdout_year].copy()
    test = df[df["year"] == holdout_year].copy()

    if len(test) == 0:
        return {"auc": float("nan"), "error": "no holdout data"}

    avail_cols = [c for c in feature_cols if c in train.columns]
    X_train = np.nan_to_num(train[avail_cols].astype("float64").values)
    X_test = np.nan_to_num(test[avail_cols].astype("float64").values)
    y_train = train["vlf"].values
    y_test = test["vlf"].values

    model = model_factory()
    model.fit(X_train, y_train)

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_test)[:, 1]
    else:
        proba = model.predict(X_test).astype(float)

    metrics = compute_metrics(y_test, proba)
    metrics["holdout_year"] = holdout_year

    if verbose:
        print(f"  Holdout {holdout_year}: AUC={metrics['auc']:.3f} "
              f"F2={metrics['f2']:.3f} "
              f"Prec={metrics['precision']:.3f} Rec={metrics['recall']:.3f} "
              f"pos={metrics['n_pos']} neg={metrics['n_neg']}")

    return metrics


# ---------------------------------------------------------------- results TSV

RESULTS_HEADER = (
    "exp_id\tdescription\tmodel\tfeatures\t"
    "cv_auc\tcv_brier\tcv_f2\tholdout_auc\tnotes"
)


def _init_results(path: Path) -> None:
    if not path.exists():
        path.write_text(RESULTS_HEADER + "\n")


def _append_result(path: Path, exp_id: str, description: str, model: str,
                   features: str, cv_metrics: dict, holdout_metrics: dict,
                   notes: str) -> None:
    _init_results(path)
    row = "\t".join([
        exp_id, description, model, features,
        f"{cv_metrics.get('auc', float('nan')):.4f}",
        f"{cv_metrics.get('brier', float('nan')):.4f}",
        f"{cv_metrics.get('f2', float('nan')):.4f}",
        f"{holdout_metrics.get('auc', float('nan')):.4f}",
        notes,
    ])
    with path.open("a") as f:
        f.write(row + "\n")


def _reset_results(path: Path) -> None:
    path.write_text(RESULTS_HEADER + "\n")


# ---------------------------------------------------------------- Phase 2.5 comparison

def run_predictor_comparison(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Phase 2.5: Compare FWI-proxy vs LFMC-proxy vs Drought-proxy.

    Tests each predictor family alone and in combinations to determine
    which predicts VLF weeks best.
    """
    configs = {
        "FWI_proxy": FWI_PROXY_FEATURES,
        "LFMC_proxy": LFMC_PROXY_FEATURES,
        "Drought_proxy": DROUGHT_PROXY_FEATURES,
        "FWI+LFMC": list(set(FWI_PROXY_FEATURES + LFMC_PROXY_FEATURES)),
        "FWI+Drought": list(set(FWI_PROXY_FEATURES + DROUGHT_PROXY_FEATURES)),
        "LFMC+Drought": list(set(LFMC_PROXY_FEATURES + DROUGHT_PROXY_FEATURES)),
        "All_three": list(set(FWI_PROXY_FEATURES + LFMC_PROXY_FEATURES
                              + DROUGHT_PROXY_FEATURES)),
        "Baseline_full": get_baseline_features(),
    }

    results = []
    for name, features in configs.items():
        if verbose:
            print(f"\n  === {name} ({len(features)} features) ===")
        cv = temporal_cv(df, make_ridge, features, verbose=verbose)
        ho = holdout_eval(df, make_ridge, features, verbose=verbose)
        results.append({
            "config": name,
            "n_features": len(features),
            "cv_auc": cv["auc"],
            "cv_f2": cv["f2"],
            "holdout_auc": ho["auc"],
        })
    return pd.DataFrame(results)


# ---------------------------------------------------------------- Phase B: risk mapping

def run_phase_b(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Phase B: Identify highest-risk weeks and country patterns.

    Train on all years except the last two, predict on all data,
    and rank by predicted VLF probability.
    """
    features = get_baseline_features()
    avail = [c for c in features if c in df.columns]

    # Train on 2012-2023, predict all
    train = df[df["year"] <= 2023].copy()
    X_train = np.nan_to_num(train[avail].astype("float64").values)
    y_train = train["vlf"].values

    model = make_ridge()
    model.fit(X_train, y_train)

    X_all = np.nan_to_num(df[avail].astype("float64").values)
    df = df.copy()
    df["vlf_prob"] = model.predict_proba(X_all)[:, 1]

    # Rank highest-risk weeks
    risk = df.sort_values("vlf_prob", ascending=False).head(30)

    if verbose:
        print("\nTop 30 highest VLF risk weeks:")
        print(risk[["country", "year", "week", "fires", "area_ha",
                     "vlf", "vlf_prob"]].to_string())

    # Country-level risk summary
    country_risk = df.groupby("country").agg(
        mean_vlf_prob=("vlf_prob", "mean"),
        total_vlf_weeks=("vlf", "sum"),
        total_weeks=("vlf", "count"),
    ).reset_index()
    country_risk["vlf_rate"] = country_risk["total_vlf_weeks"] / country_risk["total_weeks"]

    if verbose:
        print("\nCountry risk summary:")
        print(country_risk.to_string())

    # Seasonal risk profile
    seasonal = df.groupby("week").agg(
        mean_vlf_prob=("vlf_prob", "mean"),
        vlf_rate=("vlf", "mean"),
    ).reset_index()

    return df


# ---------------------------------------------------------------- feature importance

def compute_feature_importance(df: pd.DataFrame) -> pd.DataFrame:
    """Compute feature importance via permutation on Ridge coefficients."""
    features = get_baseline_features()
    avail = [c for c in features if c in df.columns]

    X = np.nan_to_num(df[avail].astype("float64").values)
    y = df["vlf"].values

    model = make_ridge()
    model.fit(X, y)

    # Coefficient-based importance for logistic regression
    coefs = np.abs(model.coef_[0])
    # Scale features to get standardized coefficients
    X_std = np.std(X, axis=0)
    X_std[X_std == 0] = 1.0
    std_coefs = coefs * X_std

    imp = pd.DataFrame({
        "feature": avail,
        "coefficient": model.coef_[0],
        "abs_coefficient": coefs,
        "standardized_importance": std_coefs,
    }).sort_values("standardized_importance", ascending=False)

    return imp


# ---------------------------------------------------------------- review-driven experiments


def fire_persistence_analysis(df: pd.DataFrame) -> dict:
    """Analyse how many VLF weeks are onset (new) vs persistence (continuing).

    A VLF week is 'persistence' if the immediately preceding week for the
    same country was also VLF. Otherwise it is 'onset'.

    Returns dict with onset_count, persist_count, persist_fraction,
    autocorrelation (week-to-week burned area correlation).
    """
    df2 = df.sort_values(["country", "year", "week"]).reset_index(drop=True)
    df2["vlf_prev"] = df2.groupby("country")["vlf"].shift(1).fillna(0)
    # Onset: VLF this week, not VLF last week (or first week of year)
    onset = ((df2["vlf"] == 1) & (df2["vlf_prev"] == 0)).sum()
    persist = ((df2["vlf"] == 1) & (df2["vlf_prev"] == 1)).sum()
    total_vlf = int(df2["vlf"].sum())
    persist_frac = persist / total_vlf if total_vlf > 0 else 0.0

    # Week-to-week autocorrelation of burned area
    area = df2["area_ha"].values
    area_lag = df2["area_lag1"].values
    mask = np.isfinite(area) & np.isfinite(area_lag)
    if mask.sum() > 2:
        autocorr = float(np.corrcoef(area[mask], area_lag[mask])[0, 1])
    else:
        autocorr = float("nan")

    return {
        "onset_count": int(onset),
        "persist_count": int(persist),
        "persist_fraction": float(persist_frac),
        "autocorrelation": autocorr,
        "total_vlf": total_vlf,
    }


def onset_only_eval(df: pd.DataFrame, model_factory, feature_cols: list,
                    verbose: bool = False) -> dict:
    """Evaluate on onset-only VLF weeks (excluding persistence).

    Removes VLF weeks that are preceded by another VLF week, then
    runs temporal CV on the remaining data with vlf_onset as target.
    """
    df2 = df.sort_values(["country", "year", "week"]).reset_index(drop=True)
    df2["vlf_prev"] = df2.groupby("country")["vlf"].shift(1).fillna(0)
    df2["vlf_onset"] = ((df2["vlf"] == 1) & (df2["vlf_prev"] == 0)).astype(int)
    df2["vlf_persist"] = ((df2["vlf"] == 1) & (df2["vlf_prev"] == 1)).astype(int)

    # Remove persistence weeks entirely, relabel target
    df_onset = df2[df2["vlf_persist"] == 0].copy()
    df_onset["vlf"] = df_onset["vlf_onset"]
    n_onset = int(df_onset["vlf"].sum())

    cv = temporal_cv(df_onset, model_factory, feature_cols, verbose=verbose)
    return {
        "auc": cv["auc"],
        "f2": cv["f2"],
        "n_onset": n_onset,
        "n_total": len(df_onset),
        "fold_metrics": cv.get("fold_metrics", []),
    }


def persistence_baseline_auc(df: pd.DataFrame) -> dict:
    """Compute AUC for a trivial persistence baseline: predict VLF from area_lag1."""
    y_true = df["vlf"].values
    y_pred = df["area_lag1"].values
    auc = float("nan")
    if y_true.sum() >= 1 and (len(y_true) - y_true.sum()) >= 1:
        try:
            auc = float(roc_auc_score(y_true, y_pred))
        except ValueError:
            pass
    return {"auc": auc, "n_pos": int(y_true.sum()), "n_total": len(y_true)}


def threshold_sensitivity(df_raw: pd.DataFrame,
                          thresholds: list | None = None) -> list[dict]:
    """Run predictor comparison at multiple VLF thresholds.

    df_raw should have features added but NO vlf column (or it will be overwritten).
    """
    if thresholds is None:
        thresholds = [1000, 2500, 5000, 10000, 20000]

    results = []
    for thresh in thresholds:
        df = df_raw.copy()
        df["vlf"] = ((df["area_ha"] > thresh) & (df["fires"] >= 1)).astype(int)
        n_pos = int(df["vlf"].sum())
        if n_pos < 5:
            results.append({
                "threshold": thresh, "n_pos": n_pos, "vlf_rate": df["vlf"].mean(),
                "fwi_auc": float("nan"), "lfmc_auc": float("nan"),
                "full_auc": float("nan"),
            })
            continue

        cv_fwi = temporal_cv(df, make_ridge, FWI_PROXY_FEATURES, verbose=False)
        cv_lfmc = temporal_cv(df, make_ridge, LFMC_PROXY_FEATURES, verbose=False)
        cv_full = temporal_cv(df, make_ridge, get_baseline_features(), verbose=False)
        results.append({
            "threshold": thresh,
            "n_pos": n_pos,
            "vlf_rate": float(df["vlf"].mean()),
            "fwi_auc": cv_fwi["auc"],
            "lfmc_auc": cv_lfmc["auc"],
            "full_auc": cv_full["auc"],
        })
    return results


def run_predictor_comparison_xgb(df: pd.DataFrame,
                                  verbose: bool = True) -> pd.DataFrame:
    """Phase 2.5b: Predictor comparison using XGBoost instead of Ridge."""
    configs = {
        "FWI_proxy": FWI_PROXY_FEATURES,
        "LFMC_proxy": LFMC_PROXY_FEATURES,
        "Drought_proxy": DROUGHT_PROXY_FEATURES,
        "Baseline_full": get_baseline_features(),
    }
    results = []
    for name, features in configs.items():
        if verbose:
            print(f"\n  === {name} (XGBoost, {len(features)} features) ===")
        cv = temporal_cv(df, make_xgboost, features, verbose=verbose)
        ho = holdout_eval(df, make_xgboost, features, verbose=verbose)
        results.append({
            "config": name,
            "n_features": len(features),
            "cv_auc": cv["auc"],
            "cv_f2": cv["f2"],
            "holdout_auc": ho["auc"],
        })
    return pd.DataFrame(results)


def per_year_auc(df: pd.DataFrame, model_factory, feature_cols: list,
                 test_years: list | None = None) -> list[dict]:
    """Return per-year AUC from temporal CV."""
    cv = temporal_cv(df, model_factory, feature_cols,
                     test_years=test_years, verbose=False)
    return cv.get("fold_metrics", [])


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["baseline", "tournament", "phase2",
                                       "comparison", "phase_b", "all"],
                    default="all")
    ap.add_argument("--reset-results", action="store_true")
    args = ap.parse_args()

    print("Loading data...")
    df = build_modelling_dataset()
    print(f"Dataset: {len(df)} rows, {df['year'].nunique()} years, "
          f"VLF rate: {df['vlf'].mean():.1%} ({df['vlf'].sum()} positive)")

    if args.reset_results:
        _reset_results(RESULTS_PATH)
    else:
        _init_results(RESULTS_PATH)

    features = get_baseline_features()

    if args.only in ("baseline", "all"):
        print("\n=== Phase 0.5: Baseline Ridge ===")
        t0 = time.time()
        cv = temporal_cv(df, make_ridge, features)
        ho = holdout_eval(df, make_ridge, features)
        dt = time.time() - t0
        print(f"  CV AUC={cv['auc']:.3f} F2={cv['f2']:.3f} | "
              f"Holdout AUC={ho['auc']:.3f} | wall={dt:.1f}s")
        _append_result(RESULTS_PATH, "E00", "Phase 0.5 baseline",
                       "ridge", "BASELINE", cv, ho,
                       f"temporal CV, n={len(df)}")

    if args.only in ("tournament", "all"):
        best_auc = 0
        best_name = ""
        for exp_name, factory in TOURNAMENT.items():
            exp_id, family = exp_name.split("_", 1)
            print(f"\n=== {exp_id}: {family} ===")
            t0 = time.time()
            cv = temporal_cv(df, factory, features)
            ho = holdout_eval(df, factory, features)
            dt = time.time() - t0
            print(f"  CV AUC={cv['auc']:.3f} F2={cv['f2']:.3f} | "
                  f"Holdout AUC={ho['auc']:.3f} | wall={dt:.1f}s")
            _append_result(RESULTS_PATH, exp_id, f"Tournament {family}",
                           family, "BASELINE", cv, ho,
                           f"temporal CV, wall={dt:.1f}s")
            if cv["auc"] > best_auc:
                best_auc = cv["auc"]
                best_name = family
        print(f"\nTournament winner: {best_name} (CV AUC={best_auc:.3f})")

    if args.only in ("comparison", "all"):
        print("\n=== Phase 2.5: Predictor Comparison ===")
        comp_df = run_predictor_comparison(df)
        print("\nComparison results:")
        print(comp_df.to_string(index=False))

        # Save comparison
        DISCOVERIES_DIR.mkdir(exist_ok=True)
        comp_df.to_csv(DISCOVERIES_DIR / "predictor_comparison.csv", index=False)

    if args.only in ("phase2", "all"):
        print("\n=== Phase 2: Land Cover Features ===")
        df_lc = add_land_cover_features(df)
        phase2_feats = get_phase2_features()
        avail_feats = [f for f in phase2_feats if f in df_lc.columns]
        cv_lc = temporal_cv(df_lc, make_ridge, avail_feats)
        ho_lc = holdout_eval(df_lc, make_ridge, avail_feats)
        print(f"  With land cover: CV AUC={cv_lc['auc']:.3f} "
              f"Holdout AUC={ho_lc['auc']:.3f}")
        _append_result(RESULTS_PATH, "E50",
                       "Phase 2: + land cover fractions",
                       "ridge", "BASELINE+LANDCOVER", cv_lc, ho_lc,
                       "added forest_frac, shrub_frac")

    if args.only in ("phase_b", "all"):
        print("\n=== Phase B: Risk Mapping ===")
        df_risk = run_phase_b(df)
        DISCOVERIES_DIR.mkdir(exist_ok=True)
        df_risk[["country", "year", "week", "fires", "area_ha", "vlf",
                 "vlf_prob"]].to_csv(
            DISCOVERIES_DIR / "vlf_risk_scores.csv", index=False)

    if args.only in ("all",):
        print("\n=== Feature Importance ===")
        fi = compute_feature_importance(df)
        DISCOVERIES_DIR.mkdir(exist_ok=True)
        fi.to_csv(DISCOVERIES_DIR / "feature_importance.csv", index=False)
        print(fi.head(15).to_string(index=False))

    print(f"\nResults written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
