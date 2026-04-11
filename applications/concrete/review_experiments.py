"""
review_experiments.py -- Run the four experiments demanded by the adversarial
review and save results for paper revision.

Experiments:
  1. Emission factor sensitivity: vary slag EF from 0.02 to 0.30 and report
     how the headline CO2 reduction changes.
  2. Local density analysis: count training samples near 120 kg cement and
     compute local CV error in that region.
  3. Holdout test set: 80/20 stratified split, train on 80%, evaluate on 20%
     never used for any model selection.
  4. Bootstrap confidence intervals: 200-iteration bootstrap on 5-fold CV
     to provide CIs on MAE and R2.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.model_selection import KFold, train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "concrete.csv"

COL_MAP = {
    "Cement (component 1)(kg in a m^3 mixture)": "cement",
    "Blast Furnace Slag (component 2)(kg in a m^3 mixture)": "slag",
    "Fly Ash (component 3)(kg in a m^3 mixture)": "fly_ash",
    "Water  (component 4)(kg in a m^3 mixture)": "water",
    "Superplasticizer (component 5)(kg in a m^3 mixture)": "superplasticizer",
    "Coarse Aggregate  (component 6)(kg in a m^3 mixture)": "coarse_agg",
    "Fine Aggregate (component 7)(kg in a m^3 mixture)": "fine_agg",
    "Age (day)": "age",
    "Concrete compressive strength(MPa. megapascals)": "strength",
}

RAW_FEATURES = ["cement", "slag", "fly_ash", "water", "superplasticizer",
                "coarse_agg", "fine_agg", "age"]
FEATURE_NAMES = RAW_FEATURES + ["wb_ratio", "scm_pct"]

# Baseline CO2 factors
CO2_PER_KG_BASE = {
    "cement": 0.90, "slag": 0.07, "fly_ash": 0.01,
    "water": 0.001, "superplasticizer": 1.50,
    "coarse_agg": 0.005, "fine_agg": 0.005,
}

# The discovered mix (Pareto winner from discovery_pareto.csv)
DISCOVERY_MIX = {
    "cement": 120, "slag": 300, "fly_ash": 150, "water": 160,
    "superplasticizer": 12, "coarse_agg": 950, "fine_agg": 700,
}

# Conventional C40
C40_CO2 = 335.4  # kg CO2/m3


def load_dataset() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH).rename(columns=COL_MAP)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    binder = out["cement"] + out["slag"] + out["fly_ash"]
    out["wb_ratio"] = (out["water"] / binder.replace(0, np.nan)).fillna(0)
    scm = out["slag"] + out["fly_ash"]
    out["scm_pct"] = (scm / binder.replace(0, np.nan)).fillna(0)
    return out


def get_xgb_params() -> dict:
    monotone = [0] * len(FEATURE_NAMES)
    monotone[FEATURE_NAMES.index("cement")] = 1
    return {
        "objective": "reg:squarederror",
        "max_depth": 6,
        "learning_rate": 0.05,
        "min_child_weight": 3,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "monotone_constraints": "(" + ",".join(str(v) for v in monotone) + ")",
        "verbosity": 0,
    }


def compute_co2(mix: dict, co2_factors: dict) -> float:
    return sum(mix.get(k, 0) * co2_factors.get(k, 0) for k in co2_factors)


# ── Experiment 1: Emission factor sensitivity ──

def emission_sensitivity() -> list[dict]:
    """Vary the slag emission factor and report the headline CO2 reduction."""
    slag_efs = [0.02, 0.04, 0.07, 0.10, 0.15, 0.20, 0.25, 0.30]
    results = []
    for slag_ef in slag_efs:
        factors = dict(CO2_PER_KG_BASE)
        factors["slag"] = slag_ef
        disc_co2 = compute_co2(DISCOVERY_MIX, factors)
        # C40 has no slag, so its CO2 is unchanged
        pct_reduction = (1 - disc_co2 / C40_CO2) * 100
        results.append({
            "slag_ef": slag_ef,
            "co2_kg_per_m3": round(disc_co2, 2),
            "pct_reduction": round(pct_reduction, 2),
        })
    return results


# ── Experiment 2: Local density analysis ──

def local_density_analysis(df: pd.DataFrame) -> dict:
    """Analyse training data density near the 120 kg cement operating point
    and compute local cross-validation error in the low-cement region."""
    # Sample counts in various cement bands
    n_102_140 = int(((df["cement"] >= 102) & (df["cement"] <= 140)).sum())
    n_100_160 = int(((df["cement"] >= 100) & (df["cement"] <= 160)).sum())
    n_102_120 = int(((df["cement"] >= 102) & (df["cement"] <= 120)).sum())

    # Cement distribution statistics
    cement_vals = df["cement"].values
    percentiles = {
        f"p{p}": float(np.percentile(cement_vals, p))
        for p in [5, 10, 25, 50, 75, 90, 95]
    }

    # Local cross-validation error: run 5-fold CV and compute MAE
    # only on test-fold samples with cement in [102, 140]
    df_feat = add_features(df)
    X = df_feat[FEATURE_NAMES].values.astype(np.float32)
    y = df_feat["strength"].values.astype(np.float32)
    cement = df_feat["cement"].values
    params = get_xgb_params()
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    local_true, local_pred = [], []
    global_true, global_pred = [], []
    for train_idx, test_idx in kf.split(X):
        dtrain = xgb.DMatrix(X[train_idx], label=y[train_idx])
        dtest = xgb.DMatrix(X[test_idx])
        booster = xgb.train(params, dtrain, num_boost_round=600)
        preds = booster.predict(dtest)
        global_true.extend(y[test_idx].tolist())
        global_pred.extend(preds.tolist())
        # Filter to local region
        mask = (cement[test_idx] >= 102) & (cement[test_idx] <= 140)
        local_true.extend(y[test_idx][mask].tolist())
        local_pred.extend(preds[mask].tolist())

    local_mae = float(mean_absolute_error(local_true, local_pred)) if local_true else float("nan")
    global_mae = float(mean_absolute_error(global_true, global_pred))

    return {
        "total_samples": int(len(df)),
        "n_samples_102_140": n_102_140,
        "n_samples_100_160": n_100_160,
        "n_samples_102_120": n_102_120,
        "cement_percentiles": percentiles,
        "local_mae_102_140": round(local_mae, 4),
        "local_n_test_samples": len(local_true),
        "global_mae": round(global_mae, 4),
        "local_vs_global_ratio": round(local_mae / global_mae, 3) if global_mae > 0 else None,
    }


# ── Experiment 3: Holdout test set ──

def holdout_evaluation(df: pd.DataFrame) -> dict:
    """80/20 train/test split. Train on 80%, evaluate on 20% never seen
    during any model selection. Uses stratified split on binned strength."""
    df_feat = add_features(df)
    X = df_feat[FEATURE_NAMES].values.astype(np.float32)
    y = df_feat["strength"].values.astype(np.float32)

    # Stratify on binned strength to ensure representativeness
    y_bins = pd.qcut(y, q=5, labels=False, duplicates="drop")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y_bins
    )

    params = get_xgb_params()
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test)
    booster = xgb.train(params, dtrain, num_boost_round=600)
    y_pred = booster.predict(dtest)

    return {
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "test_mae": round(float(mean_absolute_error(y_test, y_pred)), 4),
        "test_rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
        "test_r2": round(float(r2_score(y_test, y_pred)), 4),
    }


# ── Experiment 4: Bootstrap confidence intervals ──

def bootstrap_confidence_intervals(df: pd.DataFrame, n_bootstrap: int = 200) -> dict:
    """Bootstrap the out-of-fold residuals from 5-fold CV to estimate CIs.

    Approach: run 5-fold CV once to get (y_true, y_pred) for all 1030 samples,
    then bootstrap-resample these paired residuals 200 times to get the
    distribution of MAE and R2. This avoids the data-leakage problem of
    resampling-then-CV.
    """
    df_feat = add_features(df)
    X = df_feat[FEATURE_NAMES].values.astype(np.float32)
    y = df_feat["strength"].values.astype(np.float32)
    params = get_xgb_params()

    # Step 1: get all out-of-fold predictions
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof_true = np.zeros(len(y))
    oof_pred = np.zeros(len(y))
    for train_idx, test_idx in kf.split(X):
        dtrain = xgb.DMatrix(X[train_idx], label=y[train_idx])
        dtest = xgb.DMatrix(X[test_idx])
        booster = xgb.train(params, dtrain, num_boost_round=600)
        oof_pred[test_idx] = booster.predict(dtest)
        oof_true[test_idx] = y[test_idx]

    # Step 2: bootstrap the paired (true, pred) vectors
    rng = np.random.default_rng(42)
    n = len(oof_true)
    mae_list = []
    r2_list = []

    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        bt = oof_true[idx]
        bp = oof_pred[idx]
        mae_list.append(float(mean_absolute_error(bt, bp)))
        r2_list.append(float(r2_score(bt, bp)))

    mae_arr = np.array(mae_list)
    r2_arr = np.array(r2_list)

    return {
        "n_bootstrap": n_bootstrap,
        "mae_mean": round(float(mae_arr.mean()), 4),
        "mae_std": round(float(mae_arr.std()), 4),
        "mae_ci_lower": round(float(np.percentile(mae_arr, 2.5)), 4),
        "mae_ci_upper": round(float(np.percentile(mae_arr, 97.5)), 4),
        "r2_mean": round(float(r2_arr.mean()), 4),
        "r2_std": round(float(r2_arr.std()), 4),
        "r2_ci_lower": round(float(np.percentile(r2_arr, 2.5)), 4),
        "r2_ci_upper": round(float(np.percentile(r2_arr, 97.5)), 4),
    }


# ── Run all ──

def run_all_experiments() -> dict:
    """Execute all four review experiments and save results."""
    df = load_dataset()
    print("Running review experiments...")

    print("  1/4: Emission factor sensitivity...")
    sens = emission_sensitivity()
    print(f"       {len(sens)} scenarios computed")

    print("  2/4: Local density analysis...")
    ld = local_density_analysis(df)
    print(f"       {ld['n_samples_102_140']} samples in [102, 140] kg cement")
    print(f"       Local MAE = {ld['local_mae_102_140']:.4f} vs global {ld['global_mae']:.4f}")

    print("  3/4: Holdout test set evaluation...")
    ho = holdout_evaluation(df)
    print(f"       Holdout MAE = {ho['test_mae']:.4f}, R2 = {ho['test_r2']:.4f}")

    print("  4/4: Bootstrap confidence intervals (200 iterations)...")
    bs = bootstrap_confidence_intervals(df, n_bootstrap=200)
    print(f"       MAE = {bs['mae_mean']:.4f} [{bs['mae_ci_lower']:.4f}, {bs['mae_ci_upper']:.4f}]")
    print(f"       R2  = {bs['r2_mean']:.4f} [{bs['r2_ci_lower']:.4f}, {bs['r2_ci_upper']:.4f}]")

    results = {
        "emission_sensitivity": sens,
        "local_density": ld,
        "holdout": ho,
        "bootstrap_ci": bs,
    }

    outpath = PROJECT_ROOT / "review_experiment_results.json"
    outpath.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {outpath}")
    return results


if __name__ == "__main__":
    run_all_experiments()
