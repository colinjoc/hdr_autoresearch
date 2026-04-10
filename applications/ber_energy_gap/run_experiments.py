"""Run full HDR experiment pipeline for BER Energy Gap analysis.

Phases:
    Phase 0.5: Baseline model (XGBoost on raw features, 5-fold CV)
    Phase 1:   Tournament (XGBoost, LightGBM, ExtraTrees, Ridge)
    Phase 2:   HDR loop — feature engineering experiments from research_queue.md
    Phase 2.5: Composition retest — combine all kept features
    Phase B:   Retrofit analysis — SHAP, partial dependence, cost-effectiveness
"""
import os
import sys
import time
import warnings
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from prepare import (
    load_raw, clean_and_feature_engineer, prepare_modelling_data,
    get_model_features, get_categorical_features,
)
from model import ridge_model, rf_model, et_model, xgb_model, lgbm_model
from evaluate import cross_validate, evaluate_by_band, record_result, feature_importance

warnings.filterwarnings("ignore", category=UserWarning)

PROJ_DIR = os.path.dirname(__file__)
RESULTS_PATH = os.path.join(PROJ_DIR, "results.tsv")
DISCOVERIES_DIR = os.path.join(PROJ_DIR, "discoveries")
os.makedirs(DISCOVERIES_DIR, exist_ok=True)

# Use a subsample for fast iteration during tournament/HDR;
# full data for composition retest and retrofit analysis.
TOURNAMENT_SUBSAMPLE = 200_000
HDR_SUBSAMPLE = 200_000


def load_data():
    """Load and prepare modelling data. Returns full dataset."""
    print("=" * 60)
    print("Loading real SEAI BER data...")
    raw = load_raw()
    print(f"Raw records: {len(raw):,}")

    clean = clean_and_feature_engineer(raw)
    print(f"Clean records: {len(clean):,}")

    X, y, df_model = prepare_modelling_data(clean)
    print(f"Model records: {len(X):,}")
    print(f"Features: {X.shape[1]}")
    print(f"Target: mean={y.mean():.1f}, std={y.std():.1f}, "
          f"min={y.min():.1f}, max={y.max():.1f}")

    return X, y, df_model, clean


def subsample(X, y, df_model, n, seed=42):
    """Subsample data for fast iteration."""
    if n is None or len(X) <= n:
        return X, y, df_model
    rng = np.random.RandomState(seed)
    idx = rng.choice(len(X), n, replace=False)
    return X.iloc[idx].reset_index(drop=True), y[idx], df_model.iloc[idx].reset_index(drop=True)


# ── Phase 1: Tournament ──────────────────────────────────────────────────────

def run_tournament(X, y):
    """Run model tournament: Ridge, ExtraTrees, XGBoost, LightGBM.

    Uses TOURNAMENT_SUBSAMPLE for speed.
    """
    print("\n" + "=" * 60)
    print("PHASE 1: MODEL TOURNAMENT")
    print(f"Using {TOURNAMENT_SUBSAMPLE:,} sample from {len(X):,} records")
    print("=" * 60)

    # Subsample for speed
    if TOURNAMENT_SUBSAMPLE and len(X) > TOURNAMENT_SUBSAMPLE:
        rng = np.random.RandomState(42)
        idx = rng.choice(len(X), TOURNAMENT_SUBSAMPLE, replace=False)
        Xs = X.iloc[idx].reset_index(drop=True)
        ys = y[idx]
    else:
        Xs, ys = X, y

    results = {}

    models = [
        ("T001_ridge", "Ridge (linear baseline)", ridge_model),
        ("T002_et", "ExtraTrees (200 trees)", et_model),
        ("T003_xgb", "XGBoost (300 trees, GPU)", xgb_model),
        ("T004_lgbm", "LightGBM (300 trees)", lgbm_model),
    ]

    for exp_id, desc, model_fn in models:
        print(f"\n--- {desc} ---", flush=True)
        metrics = cross_validate(model_fn, Xs, ys, n_splits=5)
        record_result(exp_id, desc, metrics, kept=True)
        results[exp_id] = metrics

    # Pick best model
    best_id = min(results, key=lambda k: results[k]["mae"])
    best_mae = results[best_id]["mae"]
    print(f"\n*** Tournament winner: {best_id} (MAE={best_mae:.2f}) ***")

    return results, best_id


# ── Phase 2: HDR Loop ────────────────────────────────────────────────────────

def add_engineered_features(X, df_model):
    """Add HDR-loop engineered features to X."""
    X = X.copy()

    # H001: Compactness ratio (total_envelope_area / ground_floor_area)
    total_env = (
        X["wall_area"].fillna(0) + X["roof_area"].fillna(0) +
        X["floor_area"].fillna(0) + X["window_area"].fillna(0) +
        X["door_area"].fillna(0)
    )
    X["compactness_ratio"] = np.where(
        X["ground_floor_area"] > 0,
        total_env / X["ground_floor_area"],
        np.nan
    )
    X["compactness_ratio"] = X["compactness_ratio"].fillna(X["compactness_ratio"].median())

    # H002: Wall insulation era interaction (year_built * UValueWall)
    X["wall_era_interaction"] = X["year_built"] * X["uvaluewall"]
    X["wall_era_interaction"] = X["wall_era_interaction"].fillna(
        X["wall_era_interaction"].median()
    )

    # H003: Heating-fabric interaction (efficiency * envelope_u_avg)
    X["heating_fabric_interaction"] = X["hs_efficiency"] * X["envelope_u_avg"]
    X["heating_fabric_interaction"] = X["heating_fabric_interaction"].fillna(
        X["heating_fabric_interaction"].median()
    )

    # H004: Ventilation heat loss proxy (chimney + flue count)
    X["vent_loss_proxy"] = X["no_chimneys"].fillna(0) + X["no_open_flues"].fillna(0) * 1.5
    # Add permeability contribution
    X["vent_loss_proxy"] = X["vent_loss_proxy"] + X["permeability_result"].fillna(0) * 0.1

    # H005: Primary energy factor by fuel group
    # PE factors from SEAI (2019): gas=1.1, oil=1.1, elec=2.08, solid=1.0, wood=1.0, lpg=1.1
    fuel_pe = {
        "gas": 1.1, "oil": 1.1, "electricity": 2.08,
        "solid": 1.0, "wood": 1.0, "lpg": 1.1, "other": 1.2
    }
    if "fuel_group" in df_model.columns:
        X["primary_energy_factor"] = df_model["fuel_group"].map(fuel_pe).fillna(1.2).values
    elif any("fuel_group" in c for c in X.columns):
        # Reconstruct from one-hot columns
        pe_val = np.ones(len(X)) * 1.2  # default
        for fuel, factor in fuel_pe.items():
            col = f"fuel_group_{fuel}"
            if col in X.columns:
                pe_val = np.where(X[col] == 1, factor, pe_val)
        X["primary_energy_factor"] = pe_val

    # H006: Roof-to-floor area ratio
    X["roof_floor_ratio"] = np.where(
        X["ground_floor_area"] > 0,
        X["roof_area"].fillna(0) / X["ground_floor_area"],
        np.nan
    )
    X["roof_floor_ratio"] = X["roof_floor_ratio"].fillna(X["roof_floor_ratio"].median())

    # H007: Log-transform of ground floor area
    X["log_floor_area"] = np.log1p(X["ground_floor_area"].clip(lower=1))

    # H009: Space heating fraction
    if "sh_fraction" in df_model.columns:
        X["sh_fraction"] = df_model["sh_fraction"].fillna(
            df_model["sh_fraction"].median()
        ).values

    # H010: Wall heat loss (wall_area * UValueWall)
    X["wall_heat_loss"] = X["wall_area"].fillna(0) * X["uvaluewall"].fillna(0)

    # H014: Log-transform target (handled in the experiment itself)

    # Fill any NaN
    for col in X.columns:
        if X[col].isna().any():
            X[col] = X[col].fillna(X[col].median())

    return X


def run_hdr_loop(X, y, df_model, baseline_mae):
    """Run HDR loop experiments incrementally.

    Uses HDR_SUBSAMPLE for speed.
    """
    print("\n" + "=" * 60)
    print("PHASE 2: HDR LOOP — Feature Engineering")
    print(f"Using {HDR_SUBSAMPLE:,} sample from {len(X):,} records")
    print("=" * 60)

    # Subsample for speed
    if HDR_SUBSAMPLE and len(X) > HDR_SUBSAMPLE:
        rng = np.random.RandomState(42)
        idx = rng.choice(len(X), HDR_SUBSAMPLE, replace=False)
        X = X.iloc[idx].reset_index(drop=True)
        y = y[idx]
        df_model = df_model.iloc[idx].reset_index(drop=True)

    # Re-compute baseline on subsample
    print("Re-computing LightGBM baseline on subsample...")
    baseline_metrics = cross_validate(lgbm_model, X, y, n_splits=5)
    baseline_mae = baseline_metrics["mae"]
    print(f"Subsample baseline MAE: {baseline_mae:.2f}")

    best_mae = baseline_mae
    kept_features = []
    results = {}

    # Test each feature individually first
    experiments = [
        ("H001", "compactness_ratio", "Compactness ratio (envelope/floor area)"),
        ("H002", "wall_era_interaction", "Wall insulation era interaction"),
        ("H003", "heating_fabric_interaction", "Heating-fabric interaction"),
        ("H004", "vent_loss_proxy", "Ventilation heat loss proxy"),
        ("H005", "primary_energy_factor", "Primary energy factor by fuel"),
        ("H006", "roof_floor_ratio", "Roof-to-floor area ratio"),
        ("H007", "log_floor_area", "Log-transform floor area"),
        ("H009", "sh_fraction", "Space heating fraction"),
        ("H010", "wall_heat_loss", "Wall heat loss (area * U-value)"),
    ]

    X_enhanced = add_engineered_features(X, df_model)

    for exp_id, feat_name, desc in experiments:
        if feat_name not in X_enhanced.columns:
            print(f"\n--- {exp_id}: {desc} — SKIPPED (feature not available) ---")
            continue

        print(f"\n--- {exp_id}: {desc} ---")
        X_test = X.copy()
        X_test[feat_name] = X_enhanced[feat_name]
        # Fill NaN
        X_test[feat_name] = X_test[feat_name].fillna(X_test[feat_name].median())

        metrics = cross_validate(lgbm_model, X_test, y, n_splits=5)

        improvement = baseline_mae - metrics["mae"]
        kept = improvement > 0.01  # Keep if improves by >0.01 kWh/m2/yr

        record_result(exp_id, desc, metrics, kept=kept)
        results[exp_id] = {**metrics, "kept": kept, "feature": feat_name}

        if kept:
            kept_features.append(feat_name)
            print(f"    → KEPT: MAE improved by {improvement:.3f}")
        else:
            print(f"    → REVERTED: MAE change {-improvement:.3f} (worse or negligible)")

    # H014: Log-transform target
    print("\n--- H014: Log-transform target ---")
    y_log = np.log1p(y)
    metrics_log = cross_validate(lgbm_model, X, y_log, n_splits=5)
    # Convert back to original scale for comparison
    preds_log = np.expm1(metrics_log["predictions"])
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    mae_orig = mean_absolute_error(y, preds_log)
    rmse_orig = np.sqrt(mean_squared_error(y, preds_log))
    r2_orig = r2_score(y, preds_log)
    metrics_log_adj = {
        "mae": mae_orig, "rmse": rmse_orig, "r2": r2_orig,
        "mae_std": metrics_log["mae_std"], "rmse_std": metrics_log["rmse_std"],
        "r2_std": metrics_log["r2_std"], "elapsed_s": metrics_log["elapsed_s"],
        "predictions": preds_log,
    }
    improvement = baseline_mae - mae_orig
    kept = improvement > 0.01
    record_result("H014", "Log-transform target (predict log(kWh/m2))", metrics_log_adj, kept=kept)
    results["H014"] = {**metrics_log_adj, "kept": kept, "feature": "log_target"}
    if kept:
        kept_features.append("log_target")
        print(f"    → KEPT: MAE improved by {improvement:.3f}")
    else:
        print(f"    → REVERTED: MAE change {-improvement:.3f}")

    # Model tuning experiments
    print("\n--- H013: Lower learning rate (0.05) + more trees (600) ---")
    from lightgbm import LGBMRegressor
    def lgbm_tuned():
        return LGBMRegressor(
            n_estimators=600, max_depth=10, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
            device="cpu", random_state=42, n_jobs=-1, verbose=-1,
        )
    metrics_tuned = cross_validate(lgbm_tuned, X, y, n_splits=5)
    improvement = baseline_mae - metrics_tuned["mae"]
    kept = improvement > 0.01
    record_result("H013", "LightGBM tuned (lr=0.05, n=600, depth=10, reg_lambda=1)", metrics_tuned, kept=kept)
    results["H013"] = {**metrics_tuned, "kept": kept, "feature": "model_tuning"}
    if kept:
        kept_features.append("model_tuning")
        print(f"    → KEPT: MAE improved by {improvement:.3f}")
    else:
        print(f"    → REVERTED: MAE change {-improvement:.3f}")

    return results, kept_features


# ── Phase 2.5: Composition Retest ────────────────────────────────────────────

def run_composition_retest(X, y, df_model, kept_features, hdr_results):
    """Combine all kept features and retest."""
    print("\n" + "=" * 60)
    print("PHASE 2.5: COMPOSITION RETEST")
    print("=" * 60)

    X_enhanced = add_engineered_features(X, df_model)

    # Add only kept feature columns
    X_composed = X.copy()
    feat_cols_kept = [f for f in kept_features if f not in ("log_target", "model_tuning")]
    for feat in feat_cols_kept:
        if feat in X_enhanced.columns:
            X_composed[feat] = X_enhanced[feat]

    print(f"Composed feature set: {X_composed.shape[1]} features "
          f"({len(feat_cols_kept)} new from HDR loop)")

    # Determine best model config
    use_tuned = "model_tuning" in kept_features
    use_log_target = "log_target" in kept_features

    from lightgbm import LGBMRegressor
    if use_tuned:
        def model_fn():
            return LGBMRegressor(
                n_estimators=600, max_depth=10, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
                device="cpu", random_state=42, n_jobs=-1, verbose=-1,
            )
        model_desc = "LightGBM tuned"
    else:
        model_fn = lgbm_model
        model_desc = "LightGBM default"

    if use_log_target:
        y_input = np.log1p(y)
        target_desc = "log(target)"
    else:
        y_input = y
        target_desc = "raw target"

    print(f"Model: {model_desc}, Target: {target_desc}")

    metrics = cross_validate(model_fn, X_composed, y_input, n_splits=5)

    # If log target, convert metrics back
    if use_log_target:
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        preds_orig = np.expm1(metrics["predictions"])
        mae_orig = mean_absolute_error(y, preds_orig)
        rmse_orig = np.sqrt(mean_squared_error(y, preds_orig))
        r2_orig = r2_score(y, preds_orig)
        metrics = {
            **metrics,
            "mae": mae_orig, "rmse": rmse_orig, "r2": r2_orig,
            "predictions": preds_orig,
        }

    record_result(
        "COMP_01",
        f"Composition: {model_desc} + {len(feat_cols_kept)} HDR features + {target_desc}",
        metrics, kept=True
    )

    print(f"\nComposition result: MAE={metrics['mae']:.2f}, "
          f"R²={metrics['r2']:.4f}")

    return metrics, X_composed, model_fn


# ── Phase B: Retrofit Analysis ────────────────────────────────────────────────

def run_retrofit_analysis(X_composed, y, df_model, model_fn, clean_df):
    """Retrofit effectiveness analysis using SHAP and counterfactual prediction."""
    print("\n" + "=" * 60)
    print("PHASE B: RETROFIT ANALYSIS")
    print("=" * 60)

    # Train a single model on all data for SHAP analysis
    X_arr = X_composed.values if hasattr(X_composed, "values") else np.asarray(X_composed)
    model = model_fn()
    model.fit(X_arr, y)

    # Feature importance (built-in)
    imp = feature_importance(model, list(X_composed.columns))
    imp_path = os.path.join(DISCOVERIES_DIR, "feature_importance.csv")
    imp.to_csv(imp_path, index=False)
    print(f"\nTop 10 features by importance:")
    print(imp.head(10).to_string(index=False))

    # SHAP analysis (on a subsample for speed)
    print("\nComputing SHAP values (subsample of 5000)...")
    rng = np.random.RandomState(42)
    shap_idx = rng.choice(len(X_arr), min(5000, len(X_arr)), replace=False)
    X_shap = X_arr[shap_idx]

    import shap
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_shap)

    # Mean absolute SHAP values per feature
    shap_importance = pd.DataFrame({
        "feature": list(X_composed.columns),
        "mean_abs_shap": np.mean(np.abs(shap_values), axis=0),
    }).sort_values("mean_abs_shap", ascending=False)
    shap_path = os.path.join(DISCOVERIES_DIR, "shap_importance.csv")
    shap_importance.to_csv(shap_path, index=False)
    print(f"\nTop 10 features by SHAP importance:")
    print(shap_importance.head(10).to_string(index=False))

    # Per-band analysis
    print("\nPer-band prediction accuracy:")
    preds = model.predict(X_arr)
    band_results = evaluate_by_band(y, preds, df_model["energy_rating"])
    band_path = os.path.join(DISCOVERIES_DIR, "per_band_accuracy.csv")
    band_results.to_csv(band_path, index=False)
    print(band_results.to_string(index=False))

    # Retrofit counterfactual: what happens if we improve each feature by one "step"?
    print("\n--- Retrofit Counterfactual Analysis ---")
    retrofit_results = []

    # Define retrofit interventions (feature, improvement, description, approx cost EUR)
    interventions = [
        ("uvaluewall", -0.3, "Wall insulation (cavity/external)", 8000),
        ("uvalueroof", -0.2, "Roof/attic insulation (300mm)", 2500),
        ("uvaluewindow", -1.0, "Window upgrade (double to triple)", 12000),
        ("uvaluefloor", -0.2, "Floor insulation", 5000),
        ("hs_efficiency", 30, "Boiler upgrade (old to A-rated condensing)", 4000),
        ("is_heat_pump", 1, "Heat pump installation (from gas boiler)", 10000),
        ("thermal_bridging", -0.05, "Thermal bridge remediation", 3000),
        ("low_energy_lighting_pct", 50, "LED lighting upgrade", 500),
        ("no_chimneys", -1, "Chimney sealing/draught excluder", 200),
        ("pct_draught_stripped", 50, "Draught proofing", 800),
    ]

    X_baseline_mean = X_arr.mean(axis=0)
    pred_baseline = model.predict(X_baseline_mean.reshape(1, -1))[0]

    feature_names = list(X_composed.columns)

    for feat, delta, desc, cost in interventions:
        if feat not in feature_names:
            continue
        feat_idx = feature_names.index(feat)

        # Apply improvement
        X_modified = X_baseline_mean.copy()
        if feat == "is_heat_pump":
            X_modified[feat_idx] = 1  # switch to heat pump
            # Also adjust efficiency
            eff_idx = feature_names.index("hs_efficiency")
            X_modified[eff_idx] = 350  # heat pump COP ~3.5
        else:
            X_modified[feat_idx] = X_baseline_mean[feat_idx] + delta

        pred_after = model.predict(X_modified.reshape(1, -1))[0]
        saving = pred_baseline - pred_after

        retrofit_results.append({
            "intervention": desc,
            "feature": feat,
            "delta": delta,
            "predicted_ber_before": round(pred_baseline, 1),
            "predicted_ber_after": round(pred_after, 1),
            "saving_kwh_m2_yr": round(saving, 1),
            "approx_cost_eur": cost,
            "cost_per_kwh_m2_saved": round(cost / max(saving, 0.1), 0),
        })

    retrofit_df = pd.DataFrame(retrofit_results)
    retrofit_df = retrofit_df.sort_values("saving_kwh_m2_yr", ascending=False)
    retrofit_path = os.path.join(DISCOVERIES_DIR, "retrofit_effectiveness.csv")
    retrofit_df.to_csv(retrofit_path, index=False)
    print("\nRetrofit effectiveness (average dwelling):")
    print(retrofit_df.to_string(index=False))

    # County-level analysis
    print("\n--- County-Level Analysis ---")
    county_stats = df_model.groupby("county").agg(
        mean_ber=("ber_kwh_m2", "mean"),
        median_ber=("ber_kwh_m2", "median"),
        std_ber=("ber_kwh_m2", "std"),
        count=("ber_kwh_m2", "count"),
        pct_heat_pump=("is_heat_pump", "mean"),
    ).round(1)
    county_stats = county_stats.sort_values("mean_ber", ascending=False)
    county_path = os.path.join(DISCOVERIES_DIR, "county_analysis.csv")
    county_stats.to_csv(county_path)
    print(f"County analysis saved to {county_path}")
    print(county_stats.head(10).to_string())

    # Construction era analysis
    print("\n--- Construction Era Analysis ---")
    era_stats = df_model.groupby("age_category").agg(
        mean_ber=("ber_kwh_m2", "mean"),
        median_ber=("ber_kwh_m2", "median"),
        count=("ber_kwh_m2", "count"),
        pct_heat_pump=("is_heat_pump", "mean"),
    ).round(1)
    era_path = os.path.join(DISCOVERIES_DIR, "era_analysis.csv")
    era_stats.to_csv(era_path)
    print(era_stats.to_string())

    # Dwelling type analysis
    print("\n--- Dwelling Type Analysis ---")
    dtype_stats = df_model.groupby("dwelling_type").agg(
        mean_ber=("ber_kwh_m2", "mean"),
        median_ber=("ber_kwh_m2", "median"),
        count=("ber_kwh_m2", "count"),
    ).round(1)
    dtype_stats = dtype_stats.sort_values("mean_ber", ascending=False)
    dtype_path = os.path.join(DISCOVERIES_DIR, "dwelling_type_analysis.csv")
    dtype_stats.to_csv(dtype_path)
    print(dtype_stats.to_string())

    return {
        "feature_importance": imp,
        "shap_importance": shap_importance,
        "band_results": band_results,
        "retrofit_df": retrofit_df,
        "county_stats": county_stats,
        "era_stats": era_stats,
        "dtype_stats": dtype_stats,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    # Unbuffered output
    sys.stdout.reconfigure(line_buffering=True)

    t_start = time.time()

    # Reset results file for clean run
    if os.path.exists(RESULTS_PATH):
        os.remove(RESULTS_PATH)

    # Load data
    X, y, df_model, clean = load_data()

    # Phase 1: Tournament (on subsample)
    tournament_results, best_model_id = run_tournament(X, y)

    # Baseline MAE from LightGBM (or best model)
    baseline_mae = tournament_results.get("T004_lgbm", tournament_results[best_model_id])["mae"]
    print(f"\nBaseline MAE for HDR loop: {baseline_mae:.2f}", flush=True)

    # Phase 2: HDR loop (on subsample)
    hdr_results, kept_features = run_hdr_loop(X, y, df_model, baseline_mae)

    # Phase 2.5: Composition retest (on FULL data)
    print(f"\nUsing FULL dataset ({len(X):,} records) for composition retest...", flush=True)
    comp_metrics, X_composed, final_model_fn = run_composition_retest(
        X, y, df_model, kept_features, hdr_results
    )

    # Phase B: Retrofit analysis (on full data)
    retrofit_results = run_retrofit_analysis(
        X_composed, y, df_model, final_model_fn, clean
    )

    elapsed = time.time() - t_start
    print(f"\n{'=' * 60}")
    print(f"COMPLETE in {elapsed/60:.1f} minutes")
    print(f"Final composition MAE: {comp_metrics['mae']:.2f}")
    print(f"Final composition R²: {comp_metrics['r2']:.4f}")
    print(f"{'=' * 60}")
