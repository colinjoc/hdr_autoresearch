"""Reviewer-requested experiments for the adversarial paper review.

Runs the following experiments requested by the reviewer:
    RX01: Temporal CV (train 2013-2019, test 2023-2025, exclude pandemic)
    RX02: Bootstrap null distribution for the keep/revert threshold
    RX03: Decoupled label (p_score >= 0.10 only, no meteorological gate)
    RX04: Multi-seed sensitivity (seeds 0-4)
    RX05: Summer-only restriction (Jun-Sep for NH)
    RX06: Interaction terms (night-Tw x lat, night-Tw x log_population)
    RX07: Confidence intervals on all metrics via bootstrap

Results are appended to results.tsv with exp_id prefix RX##.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.metrics import (
    brier_score_loss,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold

from model import (
    BASELINE_FEATURES,
    BASELINE_FEATURES_WITH_CITY,
    BINARY_P_SCORE_THRESHOLD,
    add_features,
    add_phase2_features,
    build_clean_dataset,
    label_lethal_heatwave,
)
from evaluate import _append_result, _init_results

PHASE2_CACHE = HERE / "data" / "clean" / "heat_mortality_phase2.parquet"
RESULTS_PATH = HERE / "results.tsv"

# Phase 2 best accumulated features
PHASE2_BEST_ADDS: List[str] = (
    ["tw_night_c_max_roll4w", "tw_rolling_21d_mean",
     "prior_week_pscore", "prior_4w_mean_pscore"]
    + [f"country_{cn}" for cn in
       ("US", "FR", "GB", "ES", "IT", "DE", "GR", "PT", "RO",
        "AT", "PL", "SE", "DK", "IE", "NL")]
    + ["tmax_c_mean_lag1", "tmax_c_mean_lag2",
       "tmax_c_mean_lag3", "tmax_c_mean_lag4"]
    + ["week_of_year_sin", "week_of_year_cos"]
)
PHASE2_BEST_FEATURES = BASELINE_FEATURES_WITH_CITY + PHASE2_BEST_ADDS

# Flagship night-Tw columns (from phase25_robustness.py)
FLAGSHIP_NIGHT_TW_COLS: List[str] = [
    "tw_night_c_max", "tw_night_c_mean",
    "consecutive_nights_tw_above_24_count",
    "tw_day_night_spread_c",
    "tropical_night_count_week", "tropical_night_count_tw22",
    "tw_night_c_max_p95_anomaly", "tw_night_c_mean_p90_anomaly",
    "tw_night_c_max_zscore_city",
    "tw_night_c_max_nw22", "tw_night_c_mean_nw22",
    "tw_night_c_max_nw02", "tw_night_c_mean_nw02",
    "tw_night_c_min",
    "tw_night_max_roll3d",
    "compound_tw_days_count", "tw_compound_flag",
    "tw_degree_hours_above_26", "tw_degree_hours_above_24",
    "tw_night_c_max_roll4w",
]


def load_panel() -> pd.DataFrame:
    """Load and clean the Phase 2 cache, add all features."""
    raw = pd.read_parquet(PHASE2_CACHE)
    clean = build_clean_dataset(raw)
    feat = add_features(clean)
    feat = add_phase2_features(feat)
    return feat.reset_index(drop=True)


def _make_et():
    return ExtraTreesRegressor(
        n_estimators=300, max_depth=None, n_jobs=4, random_state=42,
    )


def _make_et_cls():
    return ExtraTreesClassifier(
        n_estimators=300, max_depth=None, n_jobs=4, random_state=42,
        class_weight="balanced",
    )


def _feature_cols(panel: pd.DataFrame, extra: List[str] = None) -> List[str]:
    """Return the feature column list, filtering to those present in panel."""
    base = PHASE2_BEST_FEATURES
    if extra:
        base = base + [c for c in extra if c not in base]
    return [c for c in base if c in panel.columns]


def _label_decoupled(df: pd.DataFrame) -> np.ndarray:
    """Binary label WITHOUT the meteorological gate: p_score >= 0.10 only."""
    p = df["p_score"].to_numpy(dtype="float64")
    p_ok = np.where(np.isnan(p), 0.0, p) >= BINARY_P_SCORE_THRESHOLD
    return p_ok.astype("int64")


# ===================================================================
# RX01: Temporal CV (train 2013-2019, test 2023-2025)
# ===================================================================

def run_temporal_cv(panel: pd.DataFrame) -> Dict:
    """Train on 2013-2019, test on 2023-2025 (exclude pandemic 2020-2022).

    This is the CRITICAL experiment the reviewer demanded. If temporal CV
    degrades the metrics substantially, the shuffled KFold numbers are inflated
    by temporal leakage.
    """
    print("\n=== RX01: Temporal CV (train 2013-2019, test 2023-2025) ===")
    t0 = time.time()

    wk = pd.to_datetime(panel["iso_week_start"])
    yr = wk.dt.year

    train_mask = yr <= 2019
    test_mask = yr >= 2023
    train_df = panel[train_mask].reset_index(drop=True)
    test_df = panel[test_mask].reset_index(drop=True)
    print(f"  train: {len(train_df)} rows (2013-2019), test: {len(test_df)} rows (2023-2025)")

    results = {}
    for label, extra_cols in [("baseline", []), ("tw_night_c_max", ["tw_night_c_max"]),
                               ("stacked_22", FLAGSHIP_NIGHT_TW_COLS)]:
        fcols = _feature_cols(panel, extra_cols)
        X_tr = train_df[fcols].astype("float64").fillna(0.0).values
        X_te = test_df[fcols].astype("float64").fillna(0.0).values
        y_tr = train_df["excess_deaths"].astype("float64").values
        y_te = test_df["excess_deaths"].astype("float64").values
        exp_te = test_df["expected_baseline"].astype("float64").values
        y_bin_te = label_lethal_heatwave(test_df)

        m = _make_et()
        m.fit(X_tr, y_tr)
        pred = m.predict(X_te)

        mae = float(mean_absolute_error(y_te, pred))
        rmse = float(np.sqrt(mean_squared_error(y_te, pred)))
        r2 = float(r2_score(y_te, pred))

        # AUC
        safe_exp = np.where(exp_te > 0, exp_te, np.nan)
        p_pred = pred / safe_exp
        scores = 1.0 / (1.0 + np.exp(-10.0 * (np.nan_to_num(p_pred, nan=0.0) - 0.10)))
        n_pos = int(y_bin_te.sum())
        n_neg = len(y_bin_te) - n_pos
        auc = float("nan")
        if n_pos >= 1 and n_neg >= 1:
            try:
                auc = float(roc_auc_score(y_bin_te, scores))
            except ValueError:
                pass

        results[label] = {"mae": mae, "rmse": rmse, "r2": r2, "auc": auc}
        print(f"  {label}: MAE={mae:.2f}  RMSE={rmse:.2f}  R2={r2:.4f}  AUC={auc:.4f}")

    dt = time.time() - t0
    print(f"  wall={dt:.1f}s")

    # Append to results.tsv
    for label, suffix in [("baseline", "E00"), ("tw_night_c_max", "tw_max"),
                           ("stacked_22", "stacked")]:
        r = results[label]
        _append_result(
            RESULTS_PATH, f"RX01.{suffix}",
            f"RX01 Temporal CV (train<=2019 test>=2023): {label}",
            "extratrees", label,
            {"mae_deaths": r["mae"], "rmse_deaths": r["rmse"],
             "r2": r["r2"], "auc_lethal": r["auc"], "brier_lethal": float("nan")},
            f"n_train={len(train_df)} n_test={len(test_df)} wall={dt:.1f}s",
        )
    return results


# ===================================================================
# RX01b: Temporal CV on baseline model (no autocorrelation features)
# ===================================================================

def run_temporal_cv_no_autocorr(panel: pd.DataFrame) -> Dict:
    """Temporal CV without prior_week_pscore and prior_4w_mean_pscore.

    This isolates the temporal leakage concern: if these autocorrelation features
    are the main source of inflation, dropping them should narrow the gap.
    """
    print("\n=== RX01b: Temporal CV, no autocorrelation features ===")
    t0 = time.time()

    wk = pd.to_datetime(panel["iso_week_start"])
    yr = wk.dt.year
    train_mask = yr <= 2019
    test_mask = yr >= 2023
    train_df = panel[train_mask].reset_index(drop=True)
    test_df = panel[test_mask].reset_index(drop=True)

    # Remove autocorrelation features
    fcols_no_ac = [c for c in _feature_cols(panel)
                   if c not in ("prior_week_pscore", "prior_4w_mean_pscore")]

    results = {}
    for label, extra_cols in [("baseline_no_ac", []),
                               ("tw_night_c_max_no_ac", ["tw_night_c_max"])]:
        fcols = [c for c in fcols_no_ac if c in panel.columns]
        if extra_cols:
            fcols = fcols + [c for c in extra_cols if c in panel.columns and c not in fcols]
        X_tr = train_df[fcols].astype("float64").fillna(0.0).values
        X_te = test_df[fcols].astype("float64").fillna(0.0).values
        y_tr = train_df["excess_deaths"].astype("float64").values
        y_te = test_df["excess_deaths"].astype("float64").values
        exp_te = test_df["expected_baseline"].astype("float64").values
        y_bin_te = label_lethal_heatwave(test_df)

        m = _make_et()
        m.fit(X_tr, y_tr)
        pred = m.predict(X_te)

        mae = float(mean_absolute_error(y_te, pred))
        rmse = float(np.sqrt(mean_squared_error(y_te, pred)))
        r2 = float(r2_score(y_te, pred))

        safe_exp = np.where(exp_te > 0, exp_te, np.nan)
        p_pred = pred / safe_exp
        scores = 1.0 / (1.0 + np.exp(-10.0 * (np.nan_to_num(p_pred, nan=0.0) - 0.10)))
        n_pos = int(y_bin_te.sum())
        n_neg = len(y_bin_te) - n_pos
        auc = float("nan")
        if n_pos >= 1 and n_neg >= 1:
            try:
                auc = float(roc_auc_score(y_bin_te, scores))
            except ValueError:
                pass

        results[label] = {"mae": mae, "rmse": rmse, "r2": r2, "auc": auc}
        print(f"  {label}: MAE={mae:.2f}  RMSE={rmse:.2f}  R2={r2:.4f}  AUC={auc:.4f}")

    dt = time.time() - t0
    print(f"  wall={dt:.1f}s")

    for label, suffix in [("baseline_no_ac", "E00"), ("tw_night_c_max_no_ac", "tw_max")]:
        r = results[label]
        _append_result(
            RESULTS_PATH, f"RX01b.{suffix}",
            f"RX01b Temporal CV no autocorr: {label}",
            "extratrees", label,
            {"mae_deaths": r["mae"], "rmse_deaths": r["rmse"],
             "r2": r["r2"], "auc_lethal": r["auc"], "brier_lethal": float("nan")},
            f"n_train={len(train_df)} n_test={len(test_df)} wall={dt:.1f}s",
        )
    return results


# ===================================================================
# RX02: Bootstrap null distribution for keep/revert threshold
# ===================================================================

def run_bootstrap_null(panel: pd.DataFrame, n_perms: int = 200) -> Dict:
    """Permutation null for the keep/revert threshold.

    For each of the top 5 flagship night-Tw features, shuffle the feature values
    within city-season strata and re-run 5-fold CV. Repeat n_perms times and
    compute the null distribution of MAE deltas. Report where the observed
    delta falls.

    Uses 200 permutations (not 1000) for computational budget.
    """
    print(f"\n=== RX02: Bootstrap null distribution ({n_perms} permutations) ===")
    t0 = time.time()

    fcols_base = _feature_cols(panel)
    X_base = panel[fcols_base].astype("float64").fillna(0.0).values
    y = panel["excess_deaths"].astype("float64").values

    # Get observed baseline MAE (5-fold CV)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof_base = np.zeros(len(panel))
    for tr, va in kf.split(panel):
        m = _make_et()
        m.fit(X_base[tr], y[tr])
        oof_base[va] = m.predict(X_base[va])
    baseline_mae = float(mean_absolute_error(y, oof_base))
    print(f"  Baseline MAE: {baseline_mae:.3f}")

    # Test 5 flagship features
    test_features = ["tw_night_c_max", "tw_night_c_mean",
                     "tw_night_c_max_p95_anomaly",
                     "tw_day_night_spread_c", "tw_night_c_max_roll4w"]
    test_features = [f for f in test_features if f in panel.columns]

    results = {}
    rng = np.random.default_rng(42)

    for feat_name in test_features:
        print(f"\n  Feature: {feat_name}")

        # Observed delta: add feature and measure MAE
        fcols_with = fcols_base + [feat_name] if feat_name not in fcols_base else fcols_base
        X_with = panel[fcols_with].astype("float64").fillna(0.0).values
        oof_with = np.zeros(len(panel))
        for tr, va in kf.split(panel):
            m = _make_et()
            m.fit(X_with[tr], y[tr])
            oof_with[va] = m.predict(X_with[va])
        observed_mae = float(mean_absolute_error(y, oof_with))
        observed_delta = observed_mae - baseline_mae
        print(f"    Observed MAE: {observed_mae:.3f}, delta: {observed_delta:+.3f}")

        # Permutation null: shuffle the feature within city-season strata
        city_vals = panel["city"].values
        month_vals = pd.to_datetime(panel["iso_week_start"]).dt.month.values
        # Create strata: city x season (Q1-Q4)
        season_vals = (month_vals - 1) // 3

        null_deltas = []
        feat_vals = panel[feat_name].astype("float64").values.copy()

        for perm_i in range(n_perms):
            shuffled = feat_vals.copy()
            # Shuffle within strata
            for city in np.unique(city_vals):
                for season in range(4):
                    mask = (city_vals == city) & (season_vals == season)
                    idx = np.where(mask)[0]
                    if len(idx) > 1:
                        rng.shuffle(shuffled[idx])

            # Build X with shuffled feature
            panel_copy = panel.copy()
            panel_copy[feat_name] = shuffled
            X_perm = panel_copy[fcols_with].astype("float64").fillna(0.0).values
            oof_perm = np.zeros(len(panel))
            for tr, va in kf.split(panel):
                m = _make_et()
                m.fit(X_perm[tr], y[tr])
                oof_perm[va] = m.predict(X_perm[va])
            perm_mae = float(mean_absolute_error(y, oof_perm))
            perm_delta = perm_mae - baseline_mae
            null_deltas.append(perm_delta)

            if (perm_i + 1) % 50 == 0:
                print(f"    permutation {perm_i + 1}/{n_perms} done")

        null_deltas = np.array(null_deltas)
        p_value = float(np.mean(null_deltas <= observed_delta))  # one-sided: is observed better than null?
        null_mean = float(null_deltas.mean())
        null_std = float(null_deltas.std())
        null_5, null_95 = float(np.percentile(null_deltas, 5)), float(np.percentile(null_deltas, 95))

        results[feat_name] = {
            "observed_delta": observed_delta,
            "null_mean": null_mean,
            "null_std": null_std,
            "null_ci_5": null_5,
            "null_ci_95": null_95,
            "p_value": p_value,
        }
        print(f"    Null: mean={null_mean:+.3f} sd={null_std:.3f} [5%={null_5:+.3f}, 95%={null_95:+.3f}]")
        print(f"    Observed delta={observed_delta:+.3f}, p={p_value:.3f}")

    dt = time.time() - t0
    print(f"\n  Total wall={dt:.1f}s")

    # Append summary to results.tsv
    for feat_name, r in results.items():
        _append_result(
            RESULTS_PATH, f"RX02.{feat_name}",
            f"RX02 Permutation null (n={n_perms}): {feat_name}",
            "extratrees", feat_name,
            {"mae_deaths": baseline_mae + r["observed_delta"],
             "rmse_deaths": float("nan"), "r2": float("nan"),
             "auc_lethal": float("nan"), "brier_lethal": float("nan")},
            f"delta={r['observed_delta']:+.3f} p={r['p_value']:.3f} "
            f"null_mean={r['null_mean']:+.3f} null_sd={r['null_std']:.3f} "
            f"null_ci=[{r['null_ci_5']:+.3f},{r['null_ci_95']:+.3f}]",
        )
    return results


# ===================================================================
# RX03: Decoupled label (remove label-feature coupling)
# ===================================================================

def run_decoupled_label(panel: pd.DataFrame) -> Dict:
    """Re-run the binary classifier with label = p_score >= 0.10 only.

    This eliminates the tautological AUC inflation from having
    consecutive_days_above_p95_tmax in both the label and the features.
    """
    print("\n=== RX03: Decoupled label (p_score >= 0.10 only, no meteorological gate) ===")
    t0 = time.time()

    y_bin_decoupled = _label_decoupled(panel)
    n_pos = int(y_bin_decoupled.sum())
    n_neg = len(y_bin_decoupled) - n_pos
    print(f"  Decoupled label positives: {n_pos}/{len(y_bin_decoupled)} ({n_pos/len(y_bin_decoupled):.1%})")
    print(f"  Original label positives: {int(label_lethal_heatwave(panel).sum())}")

    results = {}
    for label, extra_cols in [("baseline", []),
                               ("tw_night_c_max", ["tw_night_c_max"]),
                               ("stacked_22", FLAGSHIP_NIGHT_TW_COLS)]:
        fcols = _feature_cols(panel, extra_cols)
        X = panel[fcols].astype("float64").fillna(0.0).values

        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        oof_scores = np.zeros(len(panel))
        for tr, va in kf.split(panel):
            m = _make_et_cls()
            m.fit(X[tr], y_bin_decoupled[tr])
            proba = m.predict_proba(X[va])
            # Find the positive class column
            pos_idx = list(m.classes_).index(1)
            oof_scores[va] = proba[:, pos_idx]

        auc = float(roc_auc_score(y_bin_decoupled, oof_scores))
        brier = float(brier_score_loss(y_bin_decoupled, oof_scores))
        results[label] = {"auc": auc, "brier": brier}
        print(f"  {label}: AUC={auc:.4f}  Brier={brier:.4f}")

    dt = time.time() - t0
    print(f"  wall={dt:.1f}s")

    for label, suffix in [("baseline", "E00"), ("tw_night_c_max", "tw_max"),
                           ("stacked_22", "stacked")]:
        r = results[label]
        _append_result(
            RESULTS_PATH, f"RX03.{suffix}",
            f"RX03 Decoupled label (p>=0.10 only): {label}",
            "extratrees_cls", label,
            {"mae_deaths": float("nan"), "rmse_deaths": float("nan"),
             "r2": float("nan"), "auc_lethal": r["auc"], "brier_lethal": r["brier"]},
            f"label=p_score>=0.10_only n_pos={n_pos} n_neg={n_neg} wall={dt:.1f}s",
        )
    return results


# ===================================================================
# RX04: Multi-seed sensitivity
# ===================================================================

def run_multi_seed(panel: pd.DataFrame) -> Dict:
    """Re-run Phase 2 loop KEEP/REVERT decisions with 5 seeds.

    For each seed, re-evaluate the 22 flagship night-Tw features and record
    whether each one would KEEP or REVERT. If any flip, the deterministic
    conclusion is fragile.
    """
    print("\n=== RX04: Multi-seed sensitivity (seeds 0-4) ===")
    t0 = time.time()

    test_features = [
        ("tw_night_c_max", "H001"),
        ("tw_night_c_mean", "H002"),
        ("tw_day_night_spread_c", "H005"),
        ("tw_night_c_max_p95_anomaly", "H008"),
        ("tw_night_c_max_zscore_city", "H010"),
        ("tw_night_c_max_roll4w", "H022"),
    ]
    test_features = [(f, h) for f, h in test_features if f in panel.columns]

    y = panel["excess_deaths"].astype("float64").values
    seeds = [0, 1, 2, 3, 4]
    results = {}

    for feat_name, h_id in test_features:
        decisions = []
        maes_base = []
        maes_feat = []

        for seed in seeds:
            fcols_base = _feature_cols(panel)
            fcols_with = fcols_base + ([feat_name] if feat_name not in fcols_base else [])
            X_base = panel[fcols_base].astype("float64").fillna(0.0).values
            X_with = panel[fcols_with].astype("float64").fillna(0.0).values

            kf = KFold(n_splits=5, shuffle=True, random_state=seed)

            oof_base = np.zeros(len(panel))
            oof_with = np.zeros(len(panel))
            for tr, va in kf.split(panel):
                m = ExtraTreesRegressor(n_estimators=300, max_depth=None,
                                        n_jobs=4, random_state=seed)
                m.fit(X_base[tr], y[tr])
                oof_base[va] = m.predict(X_base[va])

                m2 = ExtraTreesRegressor(n_estimators=300, max_depth=None,
                                         n_jobs=4, random_state=seed)
                m2.fit(X_with[tr], y[tr])
                oof_with[va] = m2.predict(X_with[va])

            mae_base = float(mean_absolute_error(y, oof_base))
            mae_with = float(mean_absolute_error(y, oof_with))
            threshold = mae_base - max(0.5, 0.01 * mae_base)
            decision = "KEEP" if mae_with < threshold else "REVERT"
            decisions.append(decision)
            maes_base.append(mae_base)
            maes_feat.append(mae_with)

        n_keep = sum(1 for d in decisions if d == "KEEP")
        n_revert = sum(1 for d in decisions if d == "REVERT")
        fragile = n_keep > 0 and n_revert > 0

        results[feat_name] = {
            "decisions": decisions,
            "maes_base": maes_base,
            "maes_feat": maes_feat,
            "n_keep": n_keep,
            "n_revert": n_revert,
            "fragile": fragile,
        }
        print(f"  {h_id} ({feat_name}): decisions={decisions} "
              f"{'FRAGILE' if fragile else 'stable'}")

    dt = time.time() - t0
    print(f"  wall={dt:.1f}s")

    for feat_name, r in results.items():
        _append_result(
            RESULTS_PATH, f"RX04.{feat_name}",
            f"RX04 Multi-seed: {feat_name}",
            "extratrees", feat_name,
            {"mae_deaths": np.mean(r["maes_feat"]),
             "rmse_deaths": float("nan"), "r2": float("nan"),
             "auc_lethal": float("nan"), "brier_lethal": float("nan")},
            f"seeds=0-4 decisions={','.join(r['decisions'])} "
            f"n_keep={r['n_keep']} n_revert={r['n_revert']} "
            f"fragile={r['fragile']}",
        )
    return results


# ===================================================================
# RX05: Summer-only restriction (Jun-Sep)
# ===================================================================

def run_summer_only(panel: pd.DataFrame) -> Dict:
    """Restrict to June-September (NH summer) and re-test night-Tw.

    This gives the night-time hypothesis its best chance by removing
    cold-season dilution.
    """
    print("\n=== RX05: Summer-only restriction (Jun-Sep) ===")
    t0 = time.time()

    wk = pd.to_datetime(panel["iso_week_start"])
    summer_mask = wk.dt.month.isin([6, 7, 8, 9])
    summer = panel[summer_mask].reset_index(drop=True)
    print(f"  Summer panel: {len(summer)} rows (Jun-Sep)")

    y = summer["excess_deaths"].astype("float64").values
    y_bin = label_lethal_heatwave(summer)
    exp_b = summer["expected_baseline"].astype("float64").values
    print(f"  Lethal positives: {int(y_bin.sum())}/{len(y_bin)} ({y_bin.mean():.1%})")

    results = {}
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    for label, extra_cols in [("baseline", []),
                               ("tw_night_c_max", ["tw_night_c_max"]),
                               ("stacked_22", FLAGSHIP_NIGHT_TW_COLS)]:
        fcols = _feature_cols(summer, extra_cols)
        X = summer[fcols].astype("float64").fillna(0.0).values

        oof = np.zeros(len(summer))
        for tr, va in kf.split(summer):
            m = _make_et()
            m.fit(X[tr], y[tr])
            oof[va] = m.predict(X[va])

        mae = float(mean_absolute_error(y, oof))
        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        r2 = float(r2_score(y, oof))

        # AUC
        safe_exp = np.where(exp_b > 0, exp_b, np.nan)
        p_pred = oof / safe_exp
        scores = 1.0 / (1.0 + np.exp(-10.0 * (np.nan_to_num(p_pred, nan=0.0) - 0.10)))
        n_pos = int(y_bin.sum())
        n_neg = len(y_bin) - n_pos
        auc = float("nan")
        if n_pos >= 1 and n_neg >= 1:
            try:
                auc = float(roc_auc_score(y_bin, scores))
            except ValueError:
                pass

        results[label] = {"mae": mae, "rmse": rmse, "r2": r2, "auc": auc}
        print(f"  {label}: MAE={mae:.2f}  RMSE={rmse:.2f}  R2={r2:.4f}  AUC={auc:.4f}")

    dt = time.time() - t0
    print(f"  wall={dt:.1f}s")

    for label, suffix in [("baseline", "E00"), ("tw_night_c_max", "tw_max"),
                           ("stacked_22", "stacked")]:
        r = results[label]
        _append_result(
            RESULTS_PATH, f"RX05.{suffix}",
            f"RX05 Summer-only (Jun-Sep): {label}",
            "extratrees", label,
            {"mae_deaths": r["mae"], "rmse_deaths": r["rmse"],
             "r2": r["r2"], "auc_lethal": r["auc"], "brier_lethal": float("nan")},
            f"n={len(summer)} summer-only wall={dt:.1f}s",
        )
    return results


# ===================================================================
# RX06: Interaction terms
# ===================================================================

def run_interaction_terms(panel: pd.DataFrame) -> Dict:
    """Test night-Tw x vulnerability interactions.

    The reviewer noted that the literature frames night-time effects as
    interactions (night-Tw x age, night-Tw x acclimatization).
    We test the data-available proxies:
      - tw_night_c_max x lat
      - tw_night_c_max x log_population
      - tw_night_c_max x consecutive_days_above_p95_tmax (compound interaction)
    """
    print("\n=== RX06: Interaction terms ===")
    t0 = time.time()

    # Create interaction columns
    panel_int = panel.copy()
    interactions = []
    if "tw_night_c_max" in panel.columns:
        if "lat" in panel.columns:
            panel_int["tw_night_x_lat"] = (
                panel_int["tw_night_c_max"].astype("float64") *
                panel_int["lat"].astype("float64")
            )
            interactions.append("tw_night_x_lat")
        if "log_population" in panel.columns:
            panel_int["tw_night_x_logpop"] = (
                panel_int["tw_night_c_max"].astype("float64") *
                panel_int["log_population"].astype("float64")
            )
            interactions.append("tw_night_x_logpop")
        if "consecutive_days_above_p95_tmax" in panel.columns:
            panel_int["tw_night_x_p95streak"] = (
                panel_int["tw_night_c_max"].astype("float64") *
                panel_int["consecutive_days_above_p95_tmax"].astype("float64")
            )
            interactions.append("tw_night_x_p95streak")

    print(f"  Interactions created: {interactions}")

    y = panel_int["excess_deaths"].astype("float64").values
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    results = {}
    # Baseline
    fcols_base = _feature_cols(panel_int)
    X_base = panel_int[fcols_base].astype("float64").fillna(0.0).values
    oof_base = np.zeros(len(panel_int))
    for tr, va in kf.split(panel_int):
        m = _make_et()
        m.fit(X_base[tr], y[tr])
        oof_base[va] = m.predict(X_base[va])
    base_mae = float(mean_absolute_error(y, oof_base))
    results["baseline"] = {"mae": base_mae}
    print(f"  baseline: MAE={base_mae:.3f}")

    # Test each interaction
    for int_name in interactions:
        fcols = fcols_base + [int_name]
        X = panel_int[fcols].astype("float64").fillna(0.0).values
        oof = np.zeros(len(panel_int))
        for tr, va in kf.split(panel_int):
            m = _make_et()
            m.fit(X[tr], y[tr])
            oof[va] = m.predict(X[va])
        mae = float(mean_absolute_error(y, oof))
        delta = mae - base_mae
        threshold = base_mae - max(0.5, 0.01 * base_mae)
        decision = "KEEP" if mae < threshold else "REVERT"
        results[int_name] = {"mae": mae, "delta": delta, "decision": decision}
        print(f"  {int_name}: MAE={mae:.3f} delta={delta:+.3f} -> {decision}")

    # All interactions together
    all_int_cols = fcols_base + interactions
    X_all = panel_int[all_int_cols].astype("float64").fillna(0.0).values
    oof_all = np.zeros(len(panel_int))
    for tr, va in kf.split(panel_int):
        m = _make_et()
        m.fit(X_all[tr], y[tr])
        oof_all[va] = m.predict(X_all[va])
    mae_all = float(mean_absolute_error(y, oof_all))
    results["all_interactions"] = {"mae": mae_all, "delta": mae_all - base_mae}
    print(f"  all interactions: MAE={mae_all:.3f} delta={mae_all - base_mae:+.3f}")

    dt = time.time() - t0
    print(f"  wall={dt:.1f}s")

    for name, r in results.items():
        if name == "baseline":
            continue
        _append_result(
            RESULTS_PATH, f"RX06.{name}",
            f"RX06 Interaction: {name}",
            "extratrees", name,
            {"mae_deaths": r["mae"], "rmse_deaths": float("nan"),
             "r2": float("nan"), "auc_lethal": float("nan"),
             "brier_lethal": float("nan")},
            f"delta={r.get('delta', 0):+.3f} decision={r.get('decision', 'n/a')} wall={dt:.1f}s",
        )
    return results


# ===================================================================
# RX07: Bootstrap confidence intervals on key metrics
# ===================================================================

def run_bootstrap_ci(panel: pd.DataFrame, n_boot: int = 1000) -> Dict:
    """Bootstrap CIs for the Phase 2 best MAE, RMSE, R2, and AUC.

    Also computes per-fold metric distributions from the 5-fold CV.
    """
    print(f"\n=== RX07: Bootstrap confidence intervals ({n_boot} resamples) ===")
    t0 = time.time()

    fcols = _feature_cols(panel)
    X = panel[fcols].astype("float64").fillna(0.0).values
    y = panel["excess_deaths"].astype("float64").values
    exp_b = panel["expected_baseline"].astype("float64").values
    y_bin = label_lethal_heatwave(panel)

    # First get the OOF predictions
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(panel))
    fold_maes = []
    fold_aucs = []
    for tr, va in kf.split(panel):
        m = _make_et()
        m.fit(X[tr], y[tr])
        pred = m.predict(X[va])
        oof[va] = pred
        fold_maes.append(float(mean_absolute_error(y[va], pred)))

        # Per-fold AUC
        y_bin_va = y_bin[va]
        exp_va = exp_b[va]
        if y_bin_va.sum() >= 1 and (len(y_bin_va) - y_bin_va.sum()) >= 1:
            safe_exp = np.where(exp_va > 0, exp_va, np.nan)
            p_pred = pred / safe_exp
            s = 1.0 / (1.0 + np.exp(-10.0 * (np.nan_to_num(p_pred, nan=0.0) - 0.10)))
            try:
                fold_aucs.append(float(roc_auc_score(y_bin_va, s)))
            except ValueError:
                fold_aucs.append(float("nan"))

    # Report fold-level stats
    print(f"  Fold MAEs: {[f'{m:.2f}' for m in fold_maes]}")
    print(f"  Fold MAE mean={np.mean(fold_maes):.2f} std={np.std(fold_maes):.2f}")
    if fold_aucs:
        valid_aucs = [a for a in fold_aucs if not np.isnan(a)]
        if valid_aucs:
            print(f"  Fold AUCs: {[f'{a:.4f}' for a in fold_aucs]}")
            print(f"  Fold AUC mean={np.mean(valid_aucs):.4f} std={np.std(valid_aucs):.4f}")

    # Bootstrap on OOF predictions
    overall_mae = float(mean_absolute_error(y, oof))
    overall_rmse = float(np.sqrt(mean_squared_error(y, oof)))
    overall_r2 = float(r2_score(y, oof))

    rng = np.random.default_rng(42)
    boot_maes = []
    boot_rmses = []
    boot_r2s = []
    boot_aucs = []

    n = len(y)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        y_b = y[idx]
        oof_b = oof[idx]
        boot_maes.append(float(mean_absolute_error(y_b, oof_b)))
        boot_rmses.append(float(np.sqrt(mean_squared_error(y_b, oof_b))))
        boot_r2s.append(float(r2_score(y_b, oof_b)))

        y_bin_b = y_bin[idx]
        exp_b_b = exp_b[idx]
        if y_bin_b.sum() >= 1 and (len(y_bin_b) - y_bin_b.sum()) >= 1:
            safe_exp = np.where(exp_b_b > 0, exp_b_b, np.nan)
            p_pred = oof_b / safe_exp
            s = 1.0 / (1.0 + np.exp(-10.0 * (np.nan_to_num(p_pred, nan=0.0) - 0.10)))
            try:
                boot_aucs.append(float(roc_auc_score(y_bin_b, s)))
            except ValueError:
                pass

    results = {
        "mae": {"point": overall_mae,
                "ci_2.5": float(np.percentile(boot_maes, 2.5)),
                "ci_97.5": float(np.percentile(boot_maes, 97.5)),
                "std": float(np.std(boot_maes))},
        "rmse": {"point": overall_rmse,
                 "ci_2.5": float(np.percentile(boot_rmses, 2.5)),
                 "ci_97.5": float(np.percentile(boot_rmses, 97.5)),
                 "std": float(np.std(boot_rmses))},
        "r2": {"point": overall_r2,
               "ci_2.5": float(np.percentile(boot_r2s, 2.5)),
               "ci_97.5": float(np.percentile(boot_r2s, 97.5)),
               "std": float(np.std(boot_r2s))},
        "fold_mae_std": float(np.std(fold_maes)),
        "fold_mae_mean": float(np.mean(fold_maes)),
    }
    if boot_aucs:
        results["auc"] = {
            "point": float(roc_auc_score(y_bin, 1.0 / (1.0 + np.exp(-10.0 * (np.nan_to_num(oof / np.where(exp_b > 0, exp_b, np.nan), nan=0.0) - 0.10))))),
            "ci_2.5": float(np.percentile(boot_aucs, 2.5)),
            "ci_97.5": float(np.percentile(boot_aucs, 97.5)),
            "std": float(np.std(boot_aucs)),
        }

    print(f"\n  MAE: {results['mae']['point']:.2f} [{results['mae']['ci_2.5']:.2f}, {results['mae']['ci_97.5']:.2f}]")
    print(f"  RMSE: {results['rmse']['point']:.2f} [{results['rmse']['ci_2.5']:.2f}, {results['rmse']['ci_97.5']:.2f}]")
    print(f"  R2: {results['r2']['point']:.4f} [{results['r2']['ci_2.5']:.4f}, {results['r2']['ci_97.5']:.4f}]")
    if "auc" in results:
        print(f"  AUC: {results['auc']['point']:.4f} [{results['auc']['ci_2.5']:.4f}, {results['auc']['ci_97.5']:.4f}]")
    print(f"  Fold-level MAE std: {results['fold_mae_std']:.2f}")

    dt = time.time() - t0
    print(f"  wall={dt:.1f}s")

    # Append to results.tsv
    _append_result(
        RESULTS_PATH, "RX07",
        "RX07 Bootstrap CIs (1000 resamples) on Phase 2 best",
        "extratrees", "PHASE2_BEST",
        {"mae_deaths": results["mae"]["point"],
         "rmse_deaths": results["rmse"]["point"],
         "r2": results["r2"]["point"],
         "auc_lethal": results.get("auc", {}).get("point", float("nan")),
         "brier_lethal": float("nan")},
        f"MAE_95CI=[{results['mae']['ci_2.5']:.2f},{results['mae']['ci_97.5']:.2f}] "
        f"fold_mae_std={results['fold_mae_std']:.2f} "
        f"R2_95CI=[{results['r2']['ci_2.5']:.4f},{results['r2']['ci_97.5']:.4f}] "
        f"n_boot={n_boot} wall={dt:.1f}s",
    )
    return results


# ===================================================================
# Main
# ===================================================================

def main():
    print("=" * 72)
    print("REVIEWER-REQUESTED EXPERIMENTS")
    print("=" * 72)

    panel = load_panel()
    print(f"Panel loaded: {len(panel)} rows, {panel['city'].nunique()} cities")

    # RX01: Temporal CV (CRITICAL)
    rx01 = run_temporal_cv(panel)

    # RX01b: Temporal CV without autocorrelation
    rx01b = run_temporal_cv_no_autocorr(panel)

    # RX03: Decoupled label
    rx03 = run_decoupled_label(panel)

    # RX04: Multi-seed sensitivity
    rx04 = run_multi_seed(panel)

    # RX05: Summer-only
    rx05 = run_summer_only(panel)

    # RX06: Interaction terms
    rx06 = run_interaction_terms(panel)

    # RX07: Bootstrap CIs
    rx07 = run_bootstrap_ci(panel)

    # RX02: Permutation null (computationally expensive - run with fewer perms)
    rx02 = run_bootstrap_null(panel, n_perms=200)

    print("\n" + "=" * 72)
    print("ALL REVIEWER EXPERIMENTS COMPLETE")
    print("=" * 72)
    print(f"\nResults appended to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
