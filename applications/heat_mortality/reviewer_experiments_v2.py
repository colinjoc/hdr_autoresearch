"""Second round of reviewer-requested experiments.

Runs experiments that were missing or pending from the first round:
    RX02: Permutation null distribution for the keep/revert threshold
    RX08: Matched case-crossover design (reviewer experiment #6)

Results are appended to results.tsv with exp_id prefix RX##.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import (
    mean_absolute_error,
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


def _feature_cols(panel: pd.DataFrame, extra: List[str] = None) -> List[str]:
    """Return the feature column list, filtering to those present in panel."""
    base = PHASE2_BEST_FEATURES
    if extra:
        base = base + [c for c in extra if c not in base]
    return [c for c in base if c in panel.columns]


# ===================================================================
# RX02: Permutation null distribution for the keep/revert threshold
# ===================================================================

def run_permutation_null(panel: pd.DataFrame, n_perms: int = 200) -> Dict:
    """Permutation null for the keep/revert threshold.

    For each of the top 5 flagship night-Tw features, shuffle the feature values
    within city-season strata and re-run 5-fold CV. Repeat n_perms times and
    compute the null distribution of MAE deltas. Report where the observed
    delta falls.
    """
    print(f"\n=== RX02: Permutation null distribution ({n_perms} permutations) ===")
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

    city_vals = panel["city"].values
    month_vals = pd.to_datetime(panel["iso_week_start"]).dt.month.values
    season_vals = (month_vals - 1) // 3

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

        feat_vals = panel[feat_name].astype("float64").values.copy()

        null_deltas = []
        for perm_i in range(n_perms):
            shuffled = feat_vals.copy()
            for city in np.unique(city_vals):
                for season in range(4):
                    mask = (city_vals == city) & (season_vals == season)
                    idx = np.where(mask)[0]
                    if len(idx) > 1:
                        rng.shuffle(shuffled[idx])

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

            if (perm_i + 1) % 25 == 0:
                print(f"    permutation {perm_i + 1}/{n_perms} done")

        null_deltas = np.array(null_deltas)
        p_value = float(np.mean(null_deltas <= observed_delta))
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
# RX08: Matched case-crossover design
# ===================================================================

def run_case_crossover(panel: pd.DataFrame) -> Dict:
    """Matched case-crossover analysis for the night-time Tw effect.

    For each lethal heat-wave week (case), match to 3-4 control weeks in the
    same city and same ISO month of a different year. Test whether night-Tw
    differs between cases and controls after conditioning on daytime Tmax.

    This follows the epidemiological standard (Achebak et al. 2022) more
    closely than a regression approach.

    We use conditional logistic regression via stratified analysis:
    within each matched set (case + controls), compute the odds ratio
    for night-Tw being elevated in the case week vs control weeks,
    adjusting for Tmax.

    Since we cannot install statsmodels' conditional logistic regression
    in this environment without new dependencies, we implement this as:
    1. Match cases to controls
    2. Compute within-stratum differences (case - mean(controls))
    3. Run a paired t-test / Wilcoxon signed-rank test on the night-Tw
       residuals after regressing out Tmax
    """
    print("\n=== RX08: Matched case-crossover design ===")
    t0 = time.time()

    # Identify case weeks
    y_bin = label_lethal_heatwave(panel)
    case_idx = np.where(y_bin == 1)[0]
    print(f"  Cases (lethal heat-wave weeks): {len(case_idx)}")

    wk = pd.to_datetime(panel["iso_week_start"])
    panel_month = wk.dt.month.values
    panel_year = wk.dt.year.values
    panel_city = panel["city"].values

    # For each case, find 3-4 control weeks: same city, same month, different year
    rng = np.random.default_rng(42)
    matched_sets = []
    n_controls_target = 4

    for ci in case_idx:
        city = panel_city[ci]
        month = panel_month[ci]
        year = panel_year[ci]

        # Find controls: same city, same month, different year, NOT lethal
        control_mask = (
            (panel_city == city) &
            (panel_month == month) &
            (panel_year != year) &
            (y_bin == 0)
        )
        control_candidates = np.where(control_mask)[0]

        if len(control_candidates) < 2:
            continue

        n_select = min(n_controls_target, len(control_candidates))
        selected = rng.choice(control_candidates, size=n_select, replace=False)
        matched_sets.append({
            "case_idx": ci,
            "control_idx": selected.tolist(),
            "city": city,
            "month": month,
        })

    print(f"  Matched sets created: {len(matched_sets)} (with >= 2 controls each)")

    if len(matched_sets) < 10:
        print("  WARNING: Too few matched sets for meaningful analysis")
        return {"n_sets": len(matched_sets), "status": "insufficient_data"}

    # Extract variables for analysis
    tw_night = panel["tw_night_c_max"].astype("float64").values
    tmax = panel["tmax_c_mean"].astype("float64").values
    tmin = panel["tmin_c_mean"].astype("float64").values
    tw_day = panel["tw_c_max"].astype("float64").values

    # Within each matched set, compute:
    # 1. Raw tw_night difference (case - mean controls)
    # 2. Tmax-residualized tw_night difference
    raw_diffs_tw_night = []
    raw_diffs_tmax = []
    raw_diffs_tmin = []
    raw_diffs_tw_day = []
    residual_diffs = []

    for ms in matched_sets:
        ci = ms["case_idx"]
        ctrls = ms["control_idx"]

        # Case values
        tw_night_case = tw_night[ci]
        tmax_case = tmax[ci]
        tmin_case = tmin[ci]
        tw_day_case = tw_day[ci]

        # Control means
        tw_night_ctrl_mean = np.mean(tw_night[ctrls])
        tmax_ctrl_mean = np.mean(tmax[ctrls])
        tmin_ctrl_mean = np.mean(tmin[ctrls])
        tw_day_ctrl_mean = np.mean(tw_day[ctrls])

        raw_diffs_tw_night.append(tw_night_case - tw_night_ctrl_mean)
        raw_diffs_tmax.append(tmax_case - tmax_ctrl_mean)
        raw_diffs_tmin.append(tmin_case - tmin_ctrl_mean)
        raw_diffs_tw_day.append(tw_day_case - tw_day_ctrl_mean)

        # Residualize: regress tw_night on tmax within the set
        # Since we have few points per set, use the global relationship
        # and compute residual = tw_night - E[tw_night | tmax]
        # For now: simple difference after matching on Tmax level
        # residual = (tw_night_case - tw_night_ctrl_mean) - beta * (tmax_case - tmax_ctrl_mean)
        # We compute beta from the whole panel later

    raw_diffs_tw_night = np.array(raw_diffs_tw_night)
    raw_diffs_tmax = np.array(raw_diffs_tmax)
    raw_diffs_tmin = np.array(raw_diffs_tmin)
    raw_diffs_tw_day = np.array(raw_diffs_tw_day)

    # Global beta: regress tw_night on tmax across the whole panel
    valid = np.isfinite(tw_night) & np.isfinite(tmax)
    tw_night_v = tw_night[valid]
    tmax_v = tmax[valid]
    beta = np.cov(tw_night_v, tmax_v)[0, 1] / np.var(tmax_v)
    residual_diffs = raw_diffs_tw_night - beta * raw_diffs_tmax

    # Statistical tests
    from scipy import stats

    # 1. Raw night-Tw difference: one-sample t-test (H0: mean diff = 0)
    t_raw, p_raw = stats.ttest_1samp(raw_diffs_tw_night, 0)
    # 2. Tmax-residualized night-Tw difference
    t_resid, p_resid = stats.ttest_1samp(residual_diffs, 0)
    # 3. Wilcoxon signed-rank (non-parametric)
    try:
        stat_wilcox, p_wilcox = stats.wilcoxon(residual_diffs)
    except ValueError:
        stat_wilcox, p_wilcox = float("nan"), float("nan")

    # 4. Comparison: raw Tmax difference
    t_tmax, p_tmax = stats.ttest_1samp(raw_diffs_tmax, 0)
    # 5. Raw Tmin difference
    t_tmin, p_tmin = stats.ttest_1samp(raw_diffs_tmin, 0)
    # 6. Daytime Tw difference
    t_tw_day, p_tw_day = stats.ttest_1samp(raw_diffs_tw_day, 0)

    print(f"\n  Results ({len(matched_sets)} matched sets):")
    print(f"  Raw night-Tw diff: mean={raw_diffs_tw_night.mean():+.3f} C, "
          f"t={t_raw:.2f}, p={p_raw:.4f}")
    print(f"  Raw Tmax diff:     mean={raw_diffs_tmax.mean():+.3f} C, "
          f"t={t_tmax:.2f}, p={p_tmax:.4f}")
    print(f"  Raw Tmin diff:     mean={raw_diffs_tmin.mean():+.3f} C, "
          f"t={t_tmin:.2f}, p={p_tmin:.4f}")
    print(f"  Raw Tw-day diff:   mean={raw_diffs_tw_day.mean():+.3f} C, "
          f"t={t_tw_day:.2f}, p={p_tw_day:.4f}")
    print(f"  Residualized night-Tw diff (after Tmax): mean={residual_diffs.mean():+.3f} C, "
          f"t={t_resid:.2f}, p={p_resid:.4f}")
    print(f"  Wilcoxon signed-rank on residuals: stat={stat_wilcox:.1f}, p={p_wilcox:.4f}")
    print(f"  Global beta (tw_night ~ tmax): {beta:.4f}")

    # Interpretation
    if p_resid < 0.05:
        interp = "SIGNIFICANT: night-Tw differs between case and control weeks after conditioning on Tmax"
    else:
        interp = "NOT SIGNIFICANT: night-Tw does not differ after conditioning on Tmax (consistent with null finding)"

    print(f"\n  Interpretation: {interp}")

    dt = time.time() - t0
    print(f"  wall={dt:.1f}s")

    results = {
        "n_sets": len(matched_sets),
        "n_controls_per_set": n_controls_target,
        "raw_tw_night_diff_mean": float(raw_diffs_tw_night.mean()),
        "raw_tw_night_diff_t": float(t_raw),
        "raw_tw_night_diff_p": float(p_raw),
        "raw_tmax_diff_mean": float(raw_diffs_tmax.mean()),
        "raw_tmax_diff_t": float(t_tmax),
        "raw_tmax_diff_p": float(p_tmax),
        "raw_tmin_diff_mean": float(raw_diffs_tmin.mean()),
        "raw_tmin_diff_p": float(p_tmin),
        "raw_tw_day_diff_mean": float(raw_diffs_tw_day.mean()),
        "raw_tw_day_diff_p": float(p_tw_day),
        "residual_diff_mean": float(residual_diffs.mean()),
        "residual_diff_t": float(t_resid),
        "residual_diff_p": float(p_resid),
        "wilcoxon_p": float(p_wilcox),
        "beta_tw_on_tmax": float(beta),
        "interpretation": interp,
    }

    # Append to results.tsv
    _append_result(
        RESULTS_PATH, "RX08.raw",
        f"RX08 Case-crossover raw night-Tw (n={len(matched_sets)} sets)",
        "case_crossover", "tw_night_c_max",
        {"mae_deaths": float("nan"), "rmse_deaths": float("nan"),
         "r2": float("nan"), "auc_lethal": float("nan"),
         "brier_lethal": float("nan")},
        f"mean_diff={raw_diffs_tw_night.mean():+.3f}C t={t_raw:.2f} p={p_raw:.4f} "
        f"n_sets={len(matched_sets)} controls_per_set={n_controls_target}",
    )
    _append_result(
        RESULTS_PATH, "RX08.residual",
        f"RX08 Case-crossover Tmax-residualized night-Tw (n={len(matched_sets)} sets)",
        "case_crossover", "tw_night_c_max|tmax",
        {"mae_deaths": float("nan"), "rmse_deaths": float("nan"),
         "r2": float("nan"), "auc_lethal": float("nan"),
         "brier_lethal": float("nan")},
        f"mean_resid_diff={residual_diffs.mean():+.3f}C t={t_resid:.2f} p={p_resid:.4f} "
        f"wilcoxon_p={p_wilcox:.4f} beta={beta:.4f} n_sets={len(matched_sets)}",
    )
    _append_result(
        RESULTS_PATH, "RX08.tmax_comparison",
        f"RX08 Case-crossover Tmax comparison (n={len(matched_sets)} sets)",
        "case_crossover", "tmax_c_mean",
        {"mae_deaths": float("nan"), "rmse_deaths": float("nan"),
         "r2": float("nan"), "auc_lethal": float("nan"),
         "brier_lethal": float("nan")},
        f"mean_diff={raw_diffs_tmax.mean():+.3f}C t={t_tmax:.2f} p={p_tmax:.4f} "
        f"tmin_diff={raw_diffs_tmin.mean():+.3f}C tmin_p={p_tmin:.4f} "
        f"tw_day_diff={raw_diffs_tw_day.mean():+.3f}C tw_day_p={p_tw_day:.4f}",
    )

    return results


# ===================================================================
# Main
# ===================================================================

def main():
    print("=" * 72)
    print("REVIEWER-REQUESTED EXPERIMENTS - ROUND 2")
    print("=" * 72)

    panel = load_panel()
    print(f"Panel loaded: {len(panel)} rows, {panel['city'].nunique()} cities")

    # RX08: Case-crossover (fast, run first)
    rx08 = run_case_crossover(panel)

    # RX02: Permutation null (computationally expensive)
    rx02 = run_permutation_null(panel, n_perms=200)

    print("\n" + "=" * 72)
    print("ALL ROUND 2 REVIEWER EXPERIMENTS COMPLETE")
    print("=" * 72)
    print(f"\nResults appended to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
