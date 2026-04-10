"""
Phase 2: HDR Loop for Irish BER vs Real Home Energy Gap.

Runs pre-registered single-change experiments, testing hypotheses from
research_queue.md one at a time.
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from data_loaders import load_dataset, get_cv_folds, get_train_test_split
from evaluate import compute_metrics, TSV_HEADER, RESULTS_FILE


def _write_result(row: dict) -> None:
    """Append one result row to results.tsv."""
    file_exists = RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0
    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TSV_HEADER, delimiter="\t",
                                extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def run_experiment(
    df: pd.DataFrame,
    exp_id: str,
    description: str,
    feature_cols: list[str],
    categorical_cols: list[str],
    model_family: str = "extratrees",
    n_folds: int = 5,
) -> dict:
    """Run a single experiment with specified features and model."""
    from sklearn.preprocessing import RobustScaler
    from sklearn.ensemble import ExtraTreesRegressor
    from sklearn.linear_model import Ridge
    import xgboost as xgb
    import lightgbm as lgb

    print(f"\n{'='*60}")
    print(f"Experiment {exp_id}: {description}")
    print(f"  Model: {model_family}, Features: {len(feature_cols)}")
    print(f"{'='*60}")

    t0 = time.time()

    def prepare(sub_df):
        frames = []
        for col in feature_cols:
            if col in categorical_cols:
                codes, _ = pd.factorize(sub_df[col])
                frames.append(pd.Series(codes, name=col))
            else:
                frames.append(sub_df[col].reset_index(drop=True))
        X = pd.concat(frames, axis=1).values.astype(np.float32)
        y = sub_df["energy_value_kwh_m2_yr"].values.astype(np.float32)
        return X, y

    def build_model():
        if model_family == "extratrees":
            return ExtraTreesRegressor(n_estimators=300, min_samples_leaf=5,
                                        random_state=42, n_jobs=-1)
        elif model_family == "xgboost":
            return xgb.XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05,
                                     subsample=0.8, colsample_bytree=0.8,
                                     tree_method="hist", device="cuda", random_state=42)
        elif model_family == "lightgbm":
            return lgb.LGBMRegressor(n_estimators=300, max_depth=6, learning_rate=0.05,
                                      subsample=0.8, colsample_bytree=0.8,
                                      random_state=42, verbose=-1)
        elif model_family == "ridge":
            return Ridge(alpha=1.0)

    folds = get_cv_folds(df, n_folds=n_folds)
    fold_metrics = []

    for i, (train_df, val_df) in enumerate(folds):
        X_train, y_train = prepare(train_df)
        X_val, y_val = prepare(val_df)

        if model_family == "ridge":
            scaler = RobustScaler()
            X_train = scaler.fit_transform(X_train)
            X_val = scaler.transform(X_val)

        reg = build_model()
        reg.fit(X_train, y_train)
        y_pred = reg.predict(X_val)

        metrics = compute_metrics(y_val, y_pred)
        fold_metrics.append(metrics)
        print(f"  Fold {i+1}: MAE={metrics['mae']:.2f}, R2={metrics['r2']:.4f}")

    # Holdout
    train_df, test_df = get_train_test_split(df)
    X_train, y_train = prepare(train_df)
    X_test, y_test = prepare(test_df)
    if model_family == "ridge":
        scaler = RobustScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
    reg = build_model()
    reg.fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    holdout = compute_metrics(y_test, y_pred)

    elapsed = time.time() - t0

    cv_mae = np.mean([m["mae"] for m in fold_metrics])
    cv_r2 = np.mean([m["r2"] for m in fold_metrics])

    print(f"\n  CV MAE: {cv_mae:.2f}, CV R2: {cv_r2:.4f}")
    print(f"  Holdout MAE: {holdout['mae']:.2f}, R2: {holdout['r2']:.4f}")
    print(f"  Time: {elapsed:.1f}s")

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": model_family,
        "n_features": len(feature_cols),
        "cv_mae_mean": cv_mae,
        "cv_mae_std": np.std([m["mae"] for m in fold_metrics]),
        "cv_rmse_mean": np.mean([m["rmse"] for m in fold_metrics]),
        "cv_rmse_std": np.std([m["rmse"] for m in fold_metrics]),
        "cv_r2_mean": cv_r2,
        "cv_r2_std": np.std([m["r2"] for m in fold_metrics]),
        "cv_median_ae_mean": np.mean([m["median_ae"] for m in fold_metrics]),
        "holdout_mae": holdout["mae"],
        "holdout_rmse": holdout["rmse"],
        "holdout_r2": holdout["r2"],
        "holdout_median_ae": holdout["median_ae"],
        "notes": f"Phase 2 ({elapsed:.1f}s)",
    }

    return row


def main():
    print("Loading dataset...")
    df = load_dataset()
    print(f"  {len(df)} records")

    # Base features (from Phase 0.5)
    base_num = [
        "year_built", "floor_area_m2", "wall_u_value", "roof_u_value",
        "floor_u_value", "window_u_value", "heating_efficiency",
        "primary_energy_factor", "air_permeability", "hdd",
        "n_storeys", "n_bedrooms", "has_floor_insulation",
    ]
    base_cat = [
        "county", "dwelling_type", "wall_type", "insulation_type",
        "window_type", "heating_type", "ventilation_type", "secondary_heating",
    ]

    # Track best result
    best_mae = 55.51  # ExtraTrees tournament baseline
    kept_extra = []  # extra features that improved the model
    results = []

    # ---------------------------------------------------------------
    # E01: Switch to ExtraTrees (tournament winner)
    # ---------------------------------------------------------------
    row = run_experiment(df, "E01",
        "ExtraTrees baseline (tournament winner)",
        base_num + base_cat, base_cat,
        model_family="extratrees")
    _write_result(row)
    best_mae = row["cv_mae_mean"]
    results.append(row)

    # ---------------------------------------------------------------
    # Experiment helper
    # ---------------------------------------------------------------
    def try_feature(exp_id, desc, extra_num=None, extra_cat=None, prior=50):
        nonlocal best_mae, kept_extra
        feat_num = base_num + [f for f in kept_extra if f not in base_cat]
        feat_cat = base_cat + [f for f in kept_extra if f in base_cat]
        if extra_num:
            feat_num = feat_num + extra_num
        if extra_cat:
            feat_cat = feat_cat + extra_cat
        all_feat = feat_num + feat_cat
        row = run_experiment(df, exp_id, desc, all_feat, feat_cat)
        _write_result(row)
        results.append(row)

        delta = best_mae - row["cv_mae_mean"]
        if delta > 0.5:  # Improvement threshold
            print(f"  >>> KEEP: delta={delta:.2f}")
            best_mae = row["cv_mae_mean"]
            if extra_num:
                kept_extra.extend(extra_num)
            if extra_cat:
                kept_extra.extend(extra_cat)
            return "KEEP"
        else:
            print(f"  >>> REVERT: delta={delta:.2f}")
            return "REVERT"

    # ---------------------------------------------------------------
    # H026: Add regulation_era
    # ---------------------------------------------------------------
    try_feature("E02", "H026: Add regulation_era", extra_num=["regulation_era"], prior=55)

    # ---------------------------------------------------------------
    # H035: Log floor area
    # ---------------------------------------------------------------
    try_feature("E03", "H035: Add log_floor_area", extra_num=["log_floor_area"], prior=50)

    # ---------------------------------------------------------------
    # H032: Area per bedroom (occupancy proxy)
    # ---------------------------------------------------------------
    try_feature("E04", "H032: Add area_per_bedroom", extra_num=["area_per_bedroom"], prior=45)

    # ---------------------------------------------------------------
    # H002: Form factor proxy
    # ---------------------------------------------------------------
    try_feature("E05", "H002: Add form_factor_proxy", extra_num=["form_factor_proxy"], prior=55)

    # ---------------------------------------------------------------
    # H018: Is heat pump flag
    # ---------------------------------------------------------------
    try_feature("E06", "H018: Add is_heat_pump", extra_num=["is_heat_pump"], prior=50)

    # ---------------------------------------------------------------
    # H050: Window quality ordinal
    # ---------------------------------------------------------------
    try_feature("E07", "H050: Add window_quality_ordinal", extra_num=["window_quality_ordinal"], prior=60)

    # ---------------------------------------------------------------
    # H011: Wall quality ordinal
    # ---------------------------------------------------------------
    try_feature("E08", "H011: Add wall_quality_ordinal", extra_num=["wall_quality_ordinal"], prior=65)

    # ---------------------------------------------------------------
    # H015: Has secondary heating
    # ---------------------------------------------------------------
    try_feature("E09", "H015: Add has_secondary_heating", extra_num=["has_secondary_heating"], prior=40)

    # ---------------------------------------------------------------
    # H093: Has MVHR
    # ---------------------------------------------------------------
    try_feature("E10", "H093: Add has_mvhr", extra_num=["has_mvhr"], prior=50)

    # ---------------------------------------------------------------
    # H031: Wall x heating efficiency interaction
    # ---------------------------------------------------------------
    try_feature("E11", "H031: Add wall_u_x_eff_inv interaction", extra_num=["wall_u_x_eff_inv"], prior=50)

    # ---------------------------------------------------------------
    # H039: Building age at assessment
    # ---------------------------------------------------------------
    try_feature("E12", "H039: Add building_age_at_assessment", extra_num=["building_age_at_assessment"], prior=35)

    # ---------------------------------------------------------------
    # H026b: Vintage decade
    # ---------------------------------------------------------------
    try_feature("E13", "H027: Add vintage_decade", extra_num=["vintage_decade"], prior=50)

    # ---------------------------------------------------------------
    # H040: County radon risk
    # ---------------------------------------------------------------
    try_feature("E14", "H040: Add radon_risk", extra_num=["radon_risk"], prior=25)

    # ---------------------------------------------------------------
    # H023: Gas availability
    # ---------------------------------------------------------------
    try_feature("E15", "H023: Add gas_available", extra_num=["gas_available"], prior=45)

    # ---------------------------------------------------------------
    # H030: nZEB flag
    # ---------------------------------------------------------------
    try_feature("E16", "H100: Add is_nzeb", extra_num=["is_nzeb"], prior=40)

    # ---------------------------------------------------------------
    # H011: Is condensing boiler
    # ---------------------------------------------------------------
    try_feature("E17", "H011b: Add is_condensing", extra_num=["is_condensing"], prior=50)

    # ---------------------------------------------------------------
    # H013: Is solid fuel
    # ---------------------------------------------------------------
    try_feature("E18", "H013: Add is_solid_fuel", extra_num=["is_solid_fuel"], prior=50)

    # ---------------------------------------------------------------
    # H048: Fuel group categorical
    # ---------------------------------------------------------------
    try_feature("E19", "H048: Add fuel_group", extra_cat=["fuel_group"], prior=55)

    # ---------------------------------------------------------------
    # H043: CO2 emissions as auxiliary feature
    # ---------------------------------------------------------------
    try_feature("E20", "H043: Add co2_emissions_kg_m2_yr", extra_num=["co2_emissions_kg_m2_yr"], prior=40)

    # Print summary
    print("\n" + "="*60)
    print("Phase 2 Summary")
    print("="*60)
    print(f"  Best CV MAE: {best_mae:.2f}")
    print(f"  Kept features: {kept_extra}")
    print(f"\n  All experiments:")
    for r in results:
        status = "KEEP" if r["cv_mae_mean"] <= best_mae + 0.5 else "REVERT"
        print(f"    {r['exp_id']:>4}: MAE={r['cv_mae_mean']:.2f} R2={r['cv_r2_mean']:.4f} [{r['description'][:50]}] {status}")


if __name__ == "__main__":
    main()
