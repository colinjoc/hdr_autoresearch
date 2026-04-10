"""
Phase 2 HDR loop runner for Dublin NO2 source attribution.

Runs experiments programmatically by modifying model.py features,
evaluating, and recording results. Each experiment adds ONE feature.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

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
    mode = "a" if append else "w"
    file_exists = RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0
    with open(RESULTS_FILE, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TSV_HEADER, delimiter="\t",
                                extrasaction="ignore")
        if not append or not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_single_experiment(
    exp_id: str,
    description: str,
    extra_features: list[str],
    station_features: list[str] = None,
    model_family: str = "xgboost",
    df=None,
) -> dict:
    """Run one experiment with given features."""
    import model as model_module
    import evaluate as eval_module

    # Set features directly on the module (no reload — reload resets them)
    model_module.EXTRA_FEATURES = list(extra_features)
    model_module.STATION_FEATURES = list(station_features or [])
    model_module.MODEL_FAMILY = model_family

    from data_loaders import load_dataset
    from model import prepare_features

    if df is None:
        df = load_dataset()

    df_prep = prepare_features(df)
    feature_cols = model_module.get_feature_columns()

    # Quick check: all features present
    missing = [c for c in feature_cols if c not in df_prep.columns]
    if missing:
        print(f"  SKIP {exp_id}: missing features {missing}")
        return None

    df_prep = df_prep.dropna(subset=["no2_ugm3"])

    # Run CV
    t0 = time.time()
    cv_result = eval_module.run_cv(df_prep, n_folds=5, verbose=False)
    holdout_result, trained_model = eval_module.run_holdout(df_prep, verbose=False)
    elapsed = time.time() - t0

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": model_family,
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

    _write_results([row])

    cv_mae = float(cv_result['cv_mae_mean'])
    h_mae = float(holdout_result['mae'])
    h_r2 = float(holdout_result['r2'])
    exc_auc = float(holdout_result.get('exceedance_auc', float('nan')))

    print(f"  {exp_id:6s} | CV MAE={cv_mae:.2f} | H-MAE={h_mae:.2f} | "
          f"H-R²={h_r2:.3f} | ExcAUC={exc_auc:.3f} | "
          f"{len(feature_cols)} feats | {elapsed:.1f}s | {description}")

    return {
        "cv_mae": cv_mae,
        "holdout_mae": h_mae,
        "holdout_r2": h_r2,
        "exceedance_auc": exc_auc,
        "model": trained_model,
    }


def main():
    from data_loaders import load_dataset

    print("=" * 80)
    print("  Dublin NO2 — Phase 2 HDR Loop")
    print("=" * 80)

    df = load_dataset()

    # Track best results
    best_mae = 999.0
    best_features = []
    best_station_features = []

    # Cumulative feature lists
    kept_features = []
    kept_station_features = []

    # ================================================================
    # Experiment definitions: (exp_id, description, new_feature, type)
    # type = "extra" or "station"
    # ================================================================
    experiments = [
        # Station fixed effects — the biggest missing signal
        ("E01", "Add station fixed effects (all stations)",
         None, "station_all"),

        # Traffic-related features
        ("E02", "Add rush_hour indicator",
         "rush_hour", "extra"),
        ("E03", "Add rush_hour_weekday interaction",
         "rush_hour_weekday", "extra"),

        # Wind direction source features
        ("E04", "Add wind_dir_traffic (wind from traffic corridors)",
         "wind_dir_traffic", "extra"),
        ("E05", "Add wind_dir_port (wind from Dublin Port)",
         "wind_dir_port", "extra"),

        # Heating features
        ("E06", "Add cold_evening (heating season + cold + evening)",
         "cold_evening", "extra"),
        ("E07", "Add temp_heating_interaction",
         "temp_heating_interaction", "extra"),

        # Dispersion features
        ("E08", "Add calm_wind indicator (< 1.5 m/s)",
         "calm_wind", "extra"),
        ("E09", "Add wind_x_blh ventilation index",
         "wind_x_blh", "extra"),
        ("E10", "Add inverse_ventilation coefficient",
         "inverse_ventilation", "extra"),

        # Rain and lockdown
        ("E11", "Add rain_washout effect",
         "rain_washout", "extra"),
        ("E12", "Add is_lockdown (COVID natural experiment)",
         "is_lockdown", "extra"),

        # Trend
        ("E13", "Add year_trend (fleet electrification proxy)",
         "year_trend", "extra"),

        # Background estimator
        ("E14", "Add weekend_early_morning (background NO2 proxy)",
         "weekend_early_morning", "extra"),

        # Interactions
        ("E15", "Add rush_wind_dir_traffic interaction",
         "rush_wind_dir_traffic", "extra"),
        ("E16", "Add temp_inversion_proxy (night cold calm = trapping)",
         "temp_inversion_proxy", "extra"),
    ]

    for exp_id, desc, feature, ftype in experiments:
        # Build candidate feature list
        test_extras = list(kept_features)
        test_stations = list(kept_station_features)

        if ftype == "station_all":
            station_names = [
                "station_pearse_street", "station_winetavern_street",
                "station_rathmines", "station_dun_laoghaire",
                "station_ringsend", "station_kilkenny",
                "station_cork_old_station_road",
            ]
            test_stations = station_names
        elif ftype == "extra" and feature:
            test_extras.append(feature)

        result = run_single_experiment(
            exp_id=exp_id,
            description=desc,
            extra_features=test_extras,
            station_features=test_stations,
            df=df,
        )

        if result is None:
            continue

        # KEEP/REVERT decision
        improved = result["holdout_mae"] < best_mae - 0.05  # noise floor ~0.05

        if improved:
            decision = "KEEP"
            best_mae = result["holdout_mae"]
            if ftype == "station_all":
                kept_station_features = test_stations
            elif ftype == "extra" and feature:
                kept_features.append(feature)
            best_features = list(kept_features)
            best_station_features = list(kept_station_features)
        else:
            decision = "REVERT"

        print(f"         → {decision} (best MAE so far: {best_mae:.2f})")
        print()

    # ================================================================
    # Second pass: combinations and refinements
    # ================================================================
    print("\n" + "=" * 80)
    print("  Phase 2 — Second pass: refinements")
    print("=" * 80)

    # Try removing each kept feature to check necessity
    for i, feat in enumerate(list(best_features)):
        test_features = [f for j, f in enumerate(best_features) if j != i]
        result = run_single_experiment(
            exp_id=f"E{17+i:02d}",
            description=f"Ablation: remove {feat}",
            extra_features=test_features,
            station_features=best_station_features,
            df=df,
        )
        if result and result["holdout_mae"] < best_mae - 0.05:
            print(f"         → {feat} is harmful, removing")
            best_features.remove(feat)
            best_mae = result["holdout_mae"]
        else:
            print(f"         → {feat} is useful, keeping")
        print()

    print("\n" + "=" * 80)
    print("  Phase 2 COMPLETE")
    print("=" * 80)
    print(f"\n  Best holdout MAE: {best_mae:.2f} ug/m3")
    print(f"  Final features: {best_features}")
    print(f"  Station features: {best_station_features}")

    # Final run with best features
    print("\n  Running final evaluation with best feature set...")
    final = run_single_experiment(
        exp_id="E_final",
        description="Final: best feature combination",
        extra_features=best_features,
        station_features=best_station_features,
        df=df,
    )
    print(f"\n  FINAL: MAE={final['holdout_mae']:.2f}, R²={final['holdout_r2']:.3f}, "
          f"ExcAUC={final['exceedance_auc']:.3f}")

    # Source attribution
    print("\n" + "=" * 80)
    print("  Phase 2.5 — Source Attribution")
    print("=" * 80)

    import model as model_module
    model_module.EXTRA_FEATURES = best_features
    model_module.STATION_FEATURES = best_station_features

    from model import prepare_features
    from evaluate import run_source_attribution

    df_prep = prepare_features(df)
    attr = run_source_attribution(df_prep, model=final["model"])

    print(f"\n  Source attribution (feature importance decomposition):")
    print(f"    Traffic share:    {attr['traffic_share']:.1%}")
    print(f"    Heating share:    {attr['heating_share']:.1%}")
    print(f"    Port share:       {attr['port_share']:.1%}")
    print(f"    Dispersion share: {attr['dispersion_share']:.1%}")
    print(f"    Temporal share:   {attr['temporal_share']:.1%}")
    print(f"    Other share:      {attr['other_share']:.1%}")

    # Top features
    imp = attr["feature_importances"]
    top = sorted(imp.items(), key=lambda x: x[1], reverse=True)[:15]
    print(f"\n  Top-15 feature importances:")
    for name, val in top:
        print(f"    {name:35s} {val:.4f}")


if __name__ == "__main__":
    main()
