"""Fast RX02: Permutation null with corrected shuffle.

Uses 100 permutations per feature. Shuffles within city (not city-season)
to ensure the permutation actually disrupts the feature-target association.
Results appended to results.tsv.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold

from model import (
    BASELINE_FEATURES_WITH_CITY,
    add_features,
    add_phase2_features,
    build_clean_dataset,
)
from evaluate import _append_result

PHASE2_CACHE = HERE / "data" / "clean" / "heat_mortality_phase2.parquet"
RESULTS_PATH = HERE / "results.tsv"

PHASE2_BEST_ADDS = (
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


def load_panel():
    raw = pd.read_parquet(PHASE2_CACHE)
    clean = build_clean_dataset(raw)
    feat = add_features(clean)
    feat = add_phase2_features(feat)
    return feat.reset_index(drop=True)


def _make_et_fast():
    """Faster ExtraTrees for permutation test."""
    return ExtraTreesRegressor(
        n_estimators=100, max_depth=20, n_jobs=4, random_state=42,
    )


def _feature_cols(panel, extra=None):
    base = PHASE2_BEST_FEATURES
    if extra:
        base = base + [c for c in extra if c not in base]
    return [c for c in base if c in panel.columns]


def main():
    n_perms = 100
    print(f"=== RX02: Permutation null ({n_perms} perms, within-city shuffle) ===")
    t0_all = time.time()

    panel = load_panel()
    print(f"Panel: {len(panel)} rows")

    fcols_base = _feature_cols(panel)
    X_base = panel[fcols_base].astype("float64").fillna(0.0).values
    y = panel["excess_deaths"].astype("float64").values

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    # Baseline MAE
    oof_base = np.zeros(len(panel))
    for tr, va in kf.split(panel):
        m = _make_et_fast()
        m.fit(X_base[tr], y[tr])
        oof_base[va] = m.predict(X_base[va])
    baseline_mae = float(mean_absolute_error(y, oof_base))
    print(f"Baseline MAE (fast): {baseline_mae:.3f}")

    test_features = ["tw_night_c_max", "tw_night_c_mean",
                     "tw_night_c_max_p95_anomaly",
                     "tw_day_night_spread_c", "tw_night_c_max_roll4w"]
    test_features = [f for f in test_features if f in panel.columns]

    city_vals = panel["city"].values
    rng = np.random.default_rng(42)

    for feat_name in test_features:
        t0 = time.time()
        print(f"\nFeature: {feat_name}")

        # For features already in the base, we need to compare:
        # (a) baseline MAE WITH the real feature
        # (b) baseline MAE WITH the shuffled feature
        # The "observed delta" is: MAE(base+real) - MAE(base+shuffled_mean)
        in_base = feat_name in fcols_base
        if in_base:
            # Feature is in base. We shuffle it in-place and compare to unshuffled.
            fcols_with = fcols_base
        else:
            fcols_with = fcols_base + [feat_name]

        # Observed MAE with the real feature
        X_real = panel[fcols_with].astype("float64").fillna(0.0).values
        oof_real = np.zeros(len(panel))
        for tr, va in kf.split(panel):
            m = _make_et_fast()
            m.fit(X_real[tr], y[tr])
            oof_real[va] = m.predict(X_real[va])
        observed_mae = float(mean_absolute_error(y, oof_real))
        print(f"  Observed MAE (with feature): {observed_mae:.3f}")

        # Permutation null: shuffle feature within city and re-run CV
        feat_vals = panel[feat_name].astype("float64").values.copy()
        null_maes = []

        for perm_i in range(n_perms):
            shuffled = feat_vals.copy()
            # Shuffle within each city (preserving city-level distribution
            # but breaking temporal association).
            # NOTE: rng.shuffle on a fancy-indexed array shuffles a copy,
            # so we must extract, shuffle, and write back.
            for city in np.unique(city_vals):
                idx = np.where(city_vals == city)[0]
                if len(idx) > 1:
                    portion = shuffled[idx].copy()
                    rng.shuffle(portion)
                    shuffled[idx] = portion

            panel_copy = panel.copy()
            panel_copy[feat_name] = shuffled
            X_perm = panel_copy[fcols_with].astype("float64").fillna(0.0).values

            oof_perm = np.zeros(len(panel))
            for tr, va in kf.split(panel):
                m = _make_et_fast()
                m.fit(X_perm[tr], y[tr])
                oof_perm[va] = m.predict(X_perm[va])
            null_maes.append(float(mean_absolute_error(y, oof_perm)))

            if (perm_i + 1) % 20 == 0:
                print(f"  perm {perm_i + 1}/{n_perms}")

        null_maes = np.array(null_maes)
        null_mean = float(null_maes.mean())
        null_std = float(null_maes.std())
        null_5 = float(np.percentile(null_maes, 5))
        null_95 = float(np.percentile(null_maes, 95))

        # The observed MAE should be LOWER than null MAEs if the feature helps.
        # p-value: fraction of null MAEs <= observed (lower = feature helps)
        p_value = float(np.mean(null_maes <= observed_mae))

        # Delta: how much better is observed vs null mean?
        observed_delta = observed_mae - null_mean

        dt = time.time() - t0
        print(f"  Observed MAE: {observed_mae:.3f}")
        print(f"  Null MAEs: mean={null_mean:.3f} sd={null_std:.3f} "
              f"[5%={null_5:.3f}, 95%={null_95:.3f}]")
        print(f"  Delta (observed - null_mean): {observed_delta:+.3f}")
        print(f"  p (frac null <= observed): {p_value:.3f}")
        print(f"  Interpretation: {'SIGNIFICANT (p<0.05)' if p_value < 0.05 else 'NOT SIGNIFICANT'}")
        print(f"  wall={dt:.1f}s")

        _append_result(
            RESULTS_PATH, f"RX02.{feat_name}",
            f"RX02 Permutation null (n={n_perms}): {feat_name}",
            "extratrees", feat_name,
            {"mae_deaths": observed_mae,
             "rmse_deaths": float("nan"), "r2": float("nan"),
             "auc_lethal": float("nan"), "brier_lethal": float("nan")},
            f"delta_vs_null={observed_delta:+.3f} p={p_value:.3f} "
            f"null_mean={null_mean:.3f} null_sd={null_std:.3f} "
            f"null_ci=[{null_5:.3f},{null_95:.3f}]",
        )

    print(f"\nTotal wall: {time.time() - t0_all:.1f}s")
    print("Done.")


if __name__ == "__main__":
    main()
