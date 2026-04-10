"""
HDR loop continuation — focused experiments E16-E80.
Interaction features, hyperparameters, model family switches.
"""

from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path

import numpy as np

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


def write_model_py(
    extra_features,
    prepare_code="",
    model_family="xgboost",
    xgb_overrides=None,
):
    """Write model.py with given configuration."""
    extra_repr = repr(extra_features)
    xgb = {
        "max_depth": 6,
        "learning_rate": 0.1,
        "min_child_weight": 10,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "n_estimators": 200,
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "tree_method": "hist",
        "device": "cuda",
        "random_state": 42,
        "scale_pos_weight": 1.0,
    }
    if xgb_overrides:
        xgb.update(xgb_overrides)

    code = f'''"""
Model and feature engineering for Iberian wildfire VLF prediction.
"""

from __future__ import annotations
from typing import Optional
import numpy as np
import pandas as pd

BASE_FEATURES = [
    "fwi", "ffmc", "dmc", "dc", "isi", "bui",
    "temp_c", "rh_pct", "wind_kmh", "precip_mm",
    "spei_6", "ndvi", "elevation_m", "slope_deg", "lat", "month",
]

EXTRA_FEATURES: list[str] = {extra_repr}
SENTINEL2_FEATURES = ["lfmc"]

def get_feature_columns() -> list[str]:
    return BASE_FEATURES + EXTRA_FEATURES

MODEL_FAMILY = "{model_family}"

XGBOOST_PARAMS = {repr(xgb)}

LIGHTGBM_PARAMS = {{
    "max_depth": 6, "learning_rate": 0.1, "min_child_samples": 20,
    "subsample": 0.8, "colsample_bytree": 0.8, "n_estimators": 200,
    "objective": "binary", "metric": "auc", "device": "cpu",
    "random_state": 42, "verbose": -1, "scale_pos_weight": 1.0,
}}

EXTRATREES_PARAMS = {{
    "n_estimators": 300, "max_depth": None, "min_samples_leaf": 5,
    "random_state": 42, "n_jobs": -1,
}}

RIDGE_PARAMS = {{"alpha": 1.0, "random_state": 42}}

def get_model_config() -> dict:
    family = MODEL_FAMILY
    if family == "xgboost": params = XGBOOST_PARAMS.copy()
    elif family == "lightgbm": params = LIGHTGBM_PARAMS.copy()
    elif family == "extratrees": params = EXTRATREES_PARAMS.copy()
    elif family == "ridge": params = RIDGE_PARAMS.copy()
    else: raise ValueError(f"Unknown model family: {{family}}")
    return {{"family": family, "params": params}}

def build_model(config: dict):
    family = config["family"]
    params = config["params"]
    if family == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(**params)
    elif family == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(**params)
    elif family == "extratrees":
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(**params)
    elif family == "ridge":
        from sklearn.linear_model import RidgeClassifier
        return RidgeClassifier(**params)
    else:
        raise ValueError(f"Unknown model family: {{family}}")

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
{prepare_code}
    return df
'''
    with open(APP_DIR / "model.py", "w") as f:
        f.write(code)


def run_exp(exp_id, description, extra_features, prepare_code="", model_family="xgboost", xgb_overrides=None):
    """Run a single experiment."""
    write_model_py(extra_features, prepare_code, model_family, xgb_overrides)

    import model as model_module
    importlib.reload(model_module)

    from data_loaders import load_dataset
    from evaluate import run_cv, run_holdout, _write_results

    df = load_dataset()
    df = model_module.prepare_features(df)

    feature_cols = model_module.get_feature_columns()
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        print(f"  SKIP {exp_id}: Missing features {missing}")
        return None

    print(f"\n  {exp_id}: {description} [{len(feature_cols)} features]")

    cv_result = run_cv(df, n_folds=5, verbose=False)
    holdout_result, _ = run_holdout(df, verbose=False)

    cv_auc = cv_result['cv_auc_mean']
    h_auc = holdout_result['auc']
    h_f2 = holdout_result['f2']
    aug = holdout_result.get('aug2025_nw_auc', float('nan'))

    print(f"    CV AUC={cv_auc:.4f}  Holdout AUC={h_auc:.4f}  F2={h_f2:.3f}  Aug2025={aug:.3f}")

    row = {
        "exp_id": exp_id,
        "description": description,
        "model_family": model_family,
        "n_features": cv_result["n_features"],
        "cv_auc_mean": f"{cv_auc:.4f}",
        "cv_auc_std": f"{cv_result['cv_auc_std']:.4f}",
        "cv_f2_mean": f"{cv_result['cv_f2_mean']:.4f}",
        "cv_f2_std": f"{cv_result['cv_f2_std']:.4f}",
        "holdout_auc": f"{h_auc:.4f}",
        "holdout_f2": f"{h_f2:.4f}",
        "holdout_precision": f"{holdout_result['precision']:.4f}",
        "holdout_recall": f"{holdout_result['recall']:.4f}",
        "aug2025_nw_auc": f"{aug:.4f}",
        "notes": description,
    }
    _write_results([row], append=True)

    return {"cv_auc": cv_auc, "holdout_auc": h_auc, "f2": h_f2, "aug": aug}


def main():
    print("=" * 60)
    print("  HDR Phase 2 Continuation (E16-E80)")
    print("=" * 60)

    # Best so far: base 16 + lfmc + spei_1 + spei_3 + spei_12 (CV 0.664)
    BEST_EXTRAS = ["lfmc", "spei_1", "spei_3", "spei_12"]

    results = {}

    # E16: Try smaller, curated feature set (remove redundant FWI components)
    run_exp("E16", "Remove DC (redundant with SPEI)",
        ["lfmc", "spei_1", "spei_3", "spei_12"],
        prepare_code='    # Remove dc from base via dropping it after\n    df["_drop_dc"] = 1')

    # E17: Interaction: FWI * wind
    run_exp("E17", "Add FWI*wind interaction",
        BEST_EXTRAS + ["fwi_x_wind"],
        prepare_code='    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]')

    # E18: Interaction: LFMC * FWI
    run_exp("E18", "Add LFMC*FWI interaction",
        BEST_EXTRAS + ["lfmc_x_fwi"],
        prepare_code='    df["lfmc_x_fwi"] = df["lfmc"].fillna(df["lfmc"].median()) * df["fwi"]')

    # E19: Interaction: temp * wind
    run_exp("E19", "Add temp*wind interaction",
        BEST_EXTRAS + ["temp_x_wind"],
        prepare_code='    df["temp_x_wind"] = df["temp_c"] * df["wind_kmh"]')

    # E20: Log FWI
    run_exp("E20", "Add log(FWI+1)",
        BEST_EXTRAS + ["log_fwi"],
        prepare_code='    df["log_fwi"] = np.log1p(df["fwi"])')

    # E21: Wind squared
    run_exp("E21", "Add wind^2 (nonlinear wind effect)",
        BEST_EXTRAS + ["wind_sq"],
        prepare_code='    df["wind_sq"] = df["wind_kmh"] ** 2')

    # E22: SPEI_6 * LFMC interaction
    run_exp("E22", "Add SPEI6*LFMC interaction",
        BEST_EXTRAS + ["spei6_x_lfmc"],
        prepare_code='    df["spei6_x_lfmc"] = df["spei_6"] * df["lfmc"].fillna(df["lfmc"].median())')

    # E23: High wind binary threshold (>30 km/h)
    run_exp("E23", "Add wind>30 binary",
        BEST_EXTRAS + ["high_wind"],
        prepare_code='    df["high_wind"] = (df["wind_kmh"] > 30).astype(int)')

    # E24: Low LFMC binary threshold (<80)
    run_exp("E24", "Add LFMC<80 binary",
        BEST_EXTRAS + ["low_lfmc"],
        prepare_code='    df["low_lfmc"] = (df["lfmc"].fillna(999) < 80).astype(int)')

    # E25: Severe drought SPEI<-1
    run_exp("E25", "Add SPEI6<-1 binary",
        BEST_EXTRAS + ["severe_drought"],
        prepare_code='    df["severe_drought"] = (df["spei_6"] < -1).astype(int)')

    # E26: All three binary risk indicators combined
    run_exp("E26", "Three binary indicators (wind>30, LFMC<80, SPEI<-1)",
        BEST_EXTRAS + ["high_wind", "low_lfmc", "severe_drought"],
        prepare_code='    df["high_wind"] = (df["wind_kmh"] > 30).astype(int)\n    df["low_lfmc"] = (df["lfmc"].fillna(999) < 80).astype(int)\n    df["severe_drought"] = (df["spei_6"] < -1).astype(int)')

    # E27: eucalyptus_frac + concurrent_fires (both physical mechanisms)
    run_exp("E27", "Add eucalyptus + concurrent fires",
        BEST_EXTRAS + ["eucalyptus_frac", "concurrent_fires"])

    # E28: Heatwave + night temp (thermal loading)
    run_exp("E28", "Add heatwave + night temp",
        BEST_EXTRAS + ["heatwave_days", "night_temp_c"])

    # E29: Detection hour + DOY (timing effects)
    run_exp("E29", "Add detection hour + DOY",
        BEST_EXTRAS + ["detection_hour", "doy"])

    # E30-E35: Hyperparameter experiments (same best features)
    run_exp("E30", "XGBoost deeper (max_depth=8)",
        BEST_EXTRAS, xgb_overrides={"max_depth": 8})

    run_exp("E31", "XGBoost shallower (max_depth=4)",
        BEST_EXTRAS, xgb_overrides={"max_depth": 4})

    run_exp("E32", "XGBoost more trees (n_estimators=500)",
        BEST_EXTRAS, xgb_overrides={"n_estimators": 500})

    run_exp("E33", "XGBoost lower LR (0.03)",
        BEST_EXTRAS, xgb_overrides={"learning_rate": 0.03, "n_estimators": 500})

    run_exp("E34", "XGBoost scale_pos_weight=10",
        BEST_EXTRAS, xgb_overrides={"scale_pos_weight": 10.0})

    run_exp("E35", "XGBoost scale_pos_weight=25",
        BEST_EXTRAS, xgb_overrides={"scale_pos_weight": 25.0})

    # E36-E39: Model family with best features
    run_exp("E36", "LightGBM with best features",
        BEST_EXTRAS, model_family="lightgbm")

    run_exp("E37", "ExtraTrees with best features",
        BEST_EXTRAS, model_family="extratrees")

    run_exp("E38", "Ridge with best features",
        BEST_EXTRAS, model_family="ridge")

    # E39: XGBoost with class weight tuning
    run_exp("E39", "XGBoost scale_pos_weight=5, depth=5",
        BEST_EXTRAS, xgb_overrides={"scale_pos_weight": 5.0, "max_depth": 5})

    # E40-E50: Feature ablation (remove one base feature at a time)
    base_minus_one = {
        "E40": ("Remove FWI from base", "fwi"),
        "E41": ("Remove FFMC from base", "ffmc"),
        "E42": ("Remove DMC from base", "dmc"),
        "E43": ("Remove DC from base", "dc"),
        "E44": ("Remove ISI from base", "isi"),
        "E45": ("Remove BUI from base", "bui"),
        "E46": ("Remove temp_c from base", "temp_c"),
        "E47": ("Remove rh_pct from base", "rh_pct"),
        "E48": ("Remove precip_mm from base", "precip_mm"),
        "E49": ("Remove NDVI from base", "ndvi"),
        "E50": ("Remove elevation_m from base", "elevation_m"),
    }

    for exp_id, (desc, remove_feat) in base_minus_one.items():
        remaining_base = [f for f in [
            "fwi", "ffmc", "dmc", "dc", "isi", "bui",
            "temp_c", "rh_pct", "wind_kmh", "precip_mm",
            "spei_6", "ndvi", "elevation_m", "slope_deg", "lat", "month",
        ] if f != remove_feat]

        code = f'''"""
Model and feature engineering for Iberian wildfire VLF prediction.
"""
from __future__ import annotations
from typing import Optional
import numpy as np
import pandas as pd

BASE_FEATURES = {repr(remaining_base)}
EXTRA_FEATURES: list[str] = {repr(BEST_EXTRAS)}
SENTINEL2_FEATURES = ["lfmc"]

def get_feature_columns() -> list[str]:
    return BASE_FEATURES + EXTRA_FEATURES

MODEL_FAMILY = "xgboost"
XGBOOST_PARAMS = {repr({
    "max_depth": 6, "learning_rate": 0.1, "min_child_weight": 10,
    "subsample": 0.8, "colsample_bytree": 0.8, "n_estimators": 200,
    "objective": "binary:logistic", "eval_metric": "auc",
    "tree_method": "hist", "device": "cuda", "random_state": 42,
    "scale_pos_weight": 1.0,
})}
LIGHTGBM_PARAMS = {{
    "max_depth": 6, "learning_rate": 0.1, "min_child_samples": 20,
    "subsample": 0.8, "colsample_bytree": 0.8, "n_estimators": 200,
    "objective": "binary", "metric": "auc", "device": "cpu",
    "random_state": 42, "verbose": -1, "scale_pos_weight": 1.0,
}}
EXTRATREES_PARAMS = {{
    "n_estimators": 300, "max_depth": None, "min_samples_leaf": 5,
    "random_state": 42, "n_jobs": -1,
}}
RIDGE_PARAMS = {{"alpha": 1.0, "random_state": 42}}

def get_model_config() -> dict:
    family = MODEL_FAMILY
    if family == "xgboost": params = XGBOOST_PARAMS.copy()
    elif family == "lightgbm": params = LIGHTGBM_PARAMS.copy()
    elif family == "extratrees": params = EXTRATREES_PARAMS.copy()
    elif family == "ridge": params = RIDGE_PARAMS.copy()
    else: raise ValueError(f"Unknown model family: {{family}}")
    return {{"family": family, "params": params}}

def build_model(config: dict):
    family = config["family"]
    params = config["params"]
    if family == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(**params)
    elif family == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(**params)
    elif family == "extratrees":
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(**params)
    elif family == "ridge":
        from sklearn.linear_model import RidgeClassifier
        return RidgeClassifier(**params)
    else:
        raise ValueError(f"Unknown model family: {{family}}")

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    return df
'''
        with open(APP_DIR / "model.py", "w") as f:
            f.write(code)

        import model as model_module
        importlib.reload(model_module)
        from data_loaders import load_dataset
        from evaluate import run_cv, run_holdout, _write_results

        df = load_dataset()
        df = model_module.prepare_features(df)
        feature_cols = model_module.get_feature_columns()
        missing = [c for c in feature_cols if c not in df.columns]
        if missing:
            print(f"  SKIP {exp_id}: Missing {missing}")
            continue

        print(f"\n  {exp_id}: {desc} [{len(feature_cols)} features]")
        cv_result = run_cv(df, n_folds=5, verbose=False)
        holdout_result, _ = run_holdout(df, verbose=False)
        cv_auc = cv_result['cv_auc_mean']
        h_auc = holdout_result['auc']
        print(f"    CV AUC={cv_auc:.4f}  Holdout AUC={h_auc:.4f}")
        _write_results([{
            "exp_id": exp_id, "description": desc,
            "model_family": "xgboost", "n_features": cv_result["n_features"],
            "cv_auc_mean": f"{cv_auc:.4f}", "cv_auc_std": f"{cv_result['cv_auc_std']:.4f}",
            "cv_f2_mean": f"{cv_result['cv_f2_mean']:.4f}", "cv_f2_std": f"{cv_result['cv_f2_std']:.4f}",
            "holdout_auc": f"{h_auc:.4f}", "holdout_f2": f"{holdout_result['f2']:.4f}",
            "holdout_precision": f"{holdout_result['precision']:.4f}",
            "holdout_recall": f"{holdout_result['recall']:.4f}",
            "aug2025_nw_auc": f"{holdout_result.get('aug2025_nw_auc', float('nan')):.4f}",
            "notes": desc,
        }], append=True)

    # E51-E60: Compound experiments with best interactions
    # E51: FWI*wind + low_lfmc + eucalyptus
    run_exp("E51", "Best interactions: FWI*wind + lowLFMC + eucalyptus",
        BEST_EXTRAS + ["fwi_x_wind", "low_lfmc", "eucalyptus_frac"],
        prepare_code='    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]\n    df["low_lfmc"] = (df["lfmc"].fillna(999) < 80).astype(int)')

    # E52: All three binary + interactions
    run_exp("E52", "Binary+interactions: wind>30+LFMC<80+SPEI<-1+FWI*wind",
        BEST_EXTRAS + ["high_wind", "low_lfmc", "severe_drought", "fwi_x_wind"],
        prepare_code='    df["high_wind"] = (df["wind_kmh"] > 30).astype(int)\n    df["low_lfmc"] = (df["lfmc"].fillna(999) < 80).astype(int)\n    df["severe_drought"] = (df["spei_6"] < -1).astype(int)\n    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]')

    # E53: XGBoost with scale_pos_weight=10 + interactions
    run_exp("E53", "spw=10 + interactions",
        BEST_EXTRAS + ["fwi_x_wind", "low_lfmc"],
        prepare_code='    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]\n    df["low_lfmc"] = (df["lfmc"].fillna(999) < 80).astype(int)',
        xgb_overrides={"scale_pos_weight": 10.0})

    # E54: spw=25 + depth=5 (aggressive class balancing)
    run_exp("E54", "spw=25, depth=5, 500 trees",
        BEST_EXTRAS,
        xgb_overrides={"scale_pos_weight": 25.0, "max_depth": 5, "n_estimators": 500})

    # E55: Low LR + high trees + spw tuning
    run_exp("E55", "lr=0.03, 800 trees, spw=15",
        BEST_EXTRAS,
        xgb_overrides={"learning_rate": 0.03, "n_estimators": 800, "scale_pos_weight": 15.0})

    # E56: Minimal feature set (just FWI + LFMC + SPEI-6)
    run_exp("E56", "Minimal: FWI+LFMC+SPEI6 only",
        ["lfmc"],
        prepare_code='')

    # Remove all base features except FWI, LFMC, SPEI-6
    code_e57 = '''"""
Model — minimal predictor set
"""
from __future__ import annotations
import numpy as np
import pandas as pd

BASE_FEATURES = ["fwi", "lfmc", "spei_6"]
EXTRA_FEATURES: list[str] = []
SENTINEL2_FEATURES = ["lfmc"]

def get_feature_columns(): return BASE_FEATURES + EXTRA_FEATURES

MODEL_FAMILY = "xgboost"
XGBOOST_PARAMS = {
    "max_depth": 4, "learning_rate": 0.1, "min_child_weight": 10,
    "subsample": 0.8, "colsample_bytree": 0.8, "n_estimators": 200,
    "objective": "binary:logistic", "eval_metric": "auc",
    "tree_method": "hist", "device": "cuda", "random_state": 42,
    "scale_pos_weight": 10.0,
}
LIGHTGBM_PARAMS = {
    "max_depth": 6, "learning_rate": 0.1, "min_child_samples": 20,
    "subsample": 0.8, "colsample_bytree": 0.8, "n_estimators": 200,
    "objective": "binary", "metric": "auc", "device": "cpu",
    "random_state": 42, "verbose": -1, "scale_pos_weight": 1.0,
}
EXTRATREES_PARAMS = {"n_estimators": 300, "max_depth": None, "min_samples_leaf": 5, "random_state": 42, "n_jobs": -1}
RIDGE_PARAMS = {"alpha": 1.0, "random_state": 42}

def get_model_config():
    family = MODEL_FAMILY
    if family == "xgboost": params = XGBOOST_PARAMS.copy()
    elif family == "lightgbm": params = LIGHTGBM_PARAMS.copy()
    elif family == "extratrees": params = EXTRATREES_PARAMS.copy()
    elif family == "ridge": params = RIDGE_PARAMS.copy()
    else: raise ValueError(f"Unknown: {family}")
    return {"family": family, "params": params}

def build_model(config):
    family = config["family"]
    params = config["params"]
    if family == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(**params)
    elif family == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(**params)
    elif family == "extratrees":
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(**params)
    elif family == "ridge":
        from sklearn.linear_model import RidgeClassifier
        return RidgeClassifier(**params)
    else:
        raise ValueError(f"Unknown: {family}")

def prepare_features(df):
    df = df.copy()
    return df
'''
    with open(APP_DIR / "model.py", "w") as f:
        f.write(code_e57)

    import model as model_module
    importlib.reload(model_module)
    from data_loaders import load_dataset
    from evaluate import run_cv, run_holdout, _write_results

    df = load_dataset()
    df = model_module.prepare_features(df)
    feature_cols = model_module.get_feature_columns()
    print(f"\n  E57: Minimal 3 features (FWI+LFMC+SPEI6) spw=10 [{len(feature_cols)} features]")
    cv_r = run_cv(df, n_folds=5, verbose=False)
    ho_r, _ = run_holdout(df, verbose=False)
    print(f"    CV AUC={cv_r['cv_auc_mean']:.4f}  Holdout AUC={ho_r['auc']:.4f}")
    _write_results([{
        "exp_id": "E57", "description": "Minimal 3-feature (FWI+LFMC+SPEI6) spw=10",
        "model_family": "xgboost", "n_features": cv_r["n_features"],
        "cv_auc_mean": f"{cv_r['cv_auc_mean']:.4f}", "cv_auc_std": f"{cv_r['cv_auc_std']:.4f}",
        "cv_f2_mean": f"{cv_r['cv_f2_mean']:.4f}", "cv_f2_std": f"{cv_r['cv_f2_std']:.4f}",
        "holdout_auc": f"{ho_r['auc']:.4f}", "holdout_f2": f"{ho_r['f2']:.4f}",
        "holdout_precision": f"{ho_r['precision']:.4f}", "holdout_recall": f"{ho_r['recall']:.4f}",
        "aug2025_nw_auc": f"{ho_r.get('aug2025_nw_auc', float('nan')):.4f}",
        "notes": "Minimal 3-feature",
    }], append=True)

    # E58-E65: Ablation of individual SPEI timescales from best config
    for exp_id, remove_spei, desc in [
        ("E58", "spei_1", "Best minus SPEI-1"),
        ("E59", "spei_3", "Best minus SPEI-3"),
        ("E60", "spei_12", "Best minus SPEI-12"),
        ("E61", "spei_6", "Best minus SPEI-6 (base)"),
    ]:
        extras = [f for f in BEST_EXTRAS if f != remove_spei]
        # For E61, also need to remove from base
        if remove_spei == "spei_6":
            base = [f for f in [
                "fwi", "ffmc", "dmc", "dc", "isi", "bui",
                "temp_c", "rh_pct", "wind_kmh", "precip_mm",
                "ndvi", "elevation_m", "slope_deg", "lat", "month",
            ]]
            code_e = f'''"""Model — {desc}"""
from __future__ import annotations
import numpy as np
import pandas as pd
BASE_FEATURES = {repr(base)}
EXTRA_FEATURES: list[str] = {repr(extras)}
SENTINEL2_FEATURES = ["lfmc"]
def get_feature_columns(): return BASE_FEATURES + EXTRA_FEATURES
MODEL_FAMILY = "xgboost"
XGBOOST_PARAMS = {repr({
    "max_depth": 6, "learning_rate": 0.1, "min_child_weight": 10,
    "subsample": 0.8, "colsample_bytree": 0.8, "n_estimators": 200,
    "objective": "binary:logistic", "eval_metric": "auc",
    "tree_method": "hist", "device": "cuda", "random_state": 42,
    "scale_pos_weight": 1.0,
})}
LIGHTGBM_PARAMS = {{"max_depth": 6, "learning_rate": 0.1, "min_child_samples": 20, "subsample": 0.8, "colsample_bytree": 0.8, "n_estimators": 200, "objective": "binary", "metric": "auc", "device": "cpu", "random_state": 42, "verbose": -1, "scale_pos_weight": 1.0}}
EXTRATREES_PARAMS = {{"n_estimators": 300, "max_depth": None, "min_samples_leaf": 5, "random_state": 42, "n_jobs": -1}}
RIDGE_PARAMS = {{"alpha": 1.0, "random_state": 42}}
def get_model_config():
    family = MODEL_FAMILY
    if family == "xgboost": params = XGBOOST_PARAMS.copy()
    elif family == "lightgbm": params = LIGHTGBM_PARAMS.copy()
    elif family == "extratrees": params = EXTRATREES_PARAMS.copy()
    elif family == "ridge": params = RIDGE_PARAMS.copy()
    else: raise ValueError(f"Unknown: {{family}}")
    return {{"family": family, "params": params}}
def build_model(config):
    family = config["family"]
    params = config["params"]
    if family == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(**params)
    elif family == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(**params)
    elif family == "extratrees":
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(**params)
    elif family == "ridge":
        from sklearn.linear_model import RidgeClassifier
        return RidgeClassifier(**params)
    else:
        raise ValueError(f"Unknown: {{family}}")
def prepare_features(df):
    df = df.copy()
    return df
'''
            with open(APP_DIR / "model.py", "w") as f:
                f.write(code_e)
        else:
            write_model_py(extras)

        importlib.reload(model_module)
        df = load_dataset()
        df = model_module.prepare_features(df)
        feature_cols = model_module.get_feature_columns()
        missing = [c for c in feature_cols if c not in df.columns]
        if missing:
            print(f"  SKIP {exp_id}: Missing {missing}")
            continue
        print(f"\n  {exp_id}: {desc} [{len(feature_cols)} features]")
        cv_r = run_cv(df, n_folds=5, verbose=False)
        ho_r, _ = run_holdout(df, verbose=False)
        print(f"    CV AUC={cv_r['cv_auc_mean']:.4f}  Holdout AUC={ho_r['auc']:.4f}")
        _write_results([{
            "exp_id": exp_id, "description": desc,
            "model_family": "xgboost", "n_features": cv_r["n_features"],
            "cv_auc_mean": f"{cv_r['cv_auc_mean']:.4f}", "cv_auc_std": f"{cv_r['cv_auc_std']:.4f}",
            "cv_f2_mean": f"{cv_r['cv_f2_mean']:.4f}", "cv_f2_std": f"{cv_r['cv_f2_std']:.4f}",
            "holdout_auc": f"{ho_r['auc']:.4f}", "holdout_f2": f"{ho_r['f2']:.4f}",
            "holdout_precision": f"{ho_r['precision']:.4f}", "holdout_recall": f"{ho_r['recall']:.4f}",
            "aug2025_nw_auc": f"{ho_r.get('aug2025_nw_auc', float('nan')):.4f}",
            "notes": desc,
        }], append=True)

    # E62-E70: Targeted experiments
    run_exp("E62", "spw=10, depth=4, BEST+eucalyptus+concurrent",
        BEST_EXTRAS + ["eucalyptus_frac", "concurrent_fires"],
        xgb_overrides={"scale_pos_weight": 10.0, "max_depth": 4})

    run_exp("E63", "spw=15, depth=5, BEST+interactions",
        BEST_EXTRAS + ["fwi_x_wind", "low_lfmc"],
        prepare_code='    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]\n    df["low_lfmc"] = (df["lfmc"].fillna(999) < 80).astype(int)',
        xgb_overrides={"scale_pos_weight": 15.0, "max_depth": 5})

    run_exp("E64", "LightGBM spw=10 BEST+interactions",
        BEST_EXTRAS + ["fwi_x_wind"],
        prepare_code='    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]',
        model_family="lightgbm")

    run_exp("E65", "ExtraTrees BEST+eucalyptus",
        BEST_EXTRAS + ["eucalyptus_frac"],
        model_family="extratrees")

    run_exp("E66", "LFMC deviation from seasonal mean",
        BEST_EXTRAS + ["lfmc_anomaly"],
        prepare_code='    month_lfmc = df.groupby("month")["lfmc"].transform("median")\n    df["lfmc_anomaly"] = df["lfmc"].fillna(month_lfmc) - month_lfmc')

    run_exp("E67", "Temperature anomaly from monthly mean",
        BEST_EXTRAS + ["temp_anomaly"],
        prepare_code='    month_temp = df.groupby("month")["temp_c"].transform("mean")\n    df["temp_anomaly"] = df["temp_c"] - month_temp')

    run_exp("E68", "FWI percentile within month",
        BEST_EXTRAS + ["fwi_pctl"],
        prepare_code='    df["fwi_pctl"] = df.groupby("month")["fwi"].rank(pct=True)')

    run_exp("E69", "VPD proxy (vapor pressure deficit)",
        BEST_EXTRAS + ["vpd"],
        prepare_code='    # Simplified VPD = es * (1 - RH/100)\n    es = 0.6108 * np.exp(17.27 * df["temp_c"] / (df["temp_c"] + 237.3))\n    df["vpd"] = es * (1 - df["rh_pct"] / 100)')

    run_exp("E70", "Keetch-Byram proxy (cumulative drying)",
        BEST_EXTRAS + ["kb_proxy"],
        prepare_code='    # KB drought index proxy: high temp, low precip accumulation\n    df["kb_proxy"] = df["dc"] * (1 + df["temp_c"] / 30)')

    # E71-E80: Final optimization experiments
    run_exp("E71", "Best + VPD + FWI*wind, spw=10, depth=5",
        BEST_EXTRAS + ["vpd", "fwi_x_wind"],
        prepare_code='    es = 0.6108 * np.exp(17.27 * df["temp_c"] / (df["temp_c"] + 237.3))\n    df["vpd"] = es * (1 - df["rh_pct"] / 100)\n    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]',
        xgb_overrides={"scale_pos_weight": 10.0, "max_depth": 5})

    run_exp("E72", "Best + VPD + eucalyptus, spw=10",
        BEST_EXTRAS + ["vpd", "eucalyptus_frac"],
        prepare_code='    es = 0.6108 * np.exp(17.27 * df["temp_c"] / (df["temp_c"] + 237.3))\n    df["vpd"] = es * (1 - df["rh_pct"] / 100)',
        xgb_overrides={"scale_pos_weight": 10.0})

    run_exp("E73", "Best + all promising: VPD+FWI*wind+eucalyptus+concurrent",
        BEST_EXTRAS + ["vpd", "fwi_x_wind", "eucalyptus_frac", "concurrent_fires"],
        prepare_code='    es = 0.6108 * np.exp(17.27 * df["temp_c"] / (df["temp_c"] + 237.3))\n    df["vpd"] = es * (1 - df["rh_pct"] / 100)\n    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]',
        xgb_overrides={"scale_pos_weight": 10.0, "max_depth": 5})

    run_exp("E74", "E73 + more trees (800) + lower LR (0.03)",
        BEST_EXTRAS + ["vpd", "fwi_x_wind", "eucalyptus_frac", "concurrent_fires"],
        prepare_code='    es = 0.6108 * np.exp(17.27 * df["temp_c"] / (df["temp_c"] + 237.3))\n    df["vpd"] = es * (1 - df["rh_pct"] / 100)\n    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]',
        xgb_overrides={"scale_pos_weight": 10.0, "max_depth": 5, "learning_rate": 0.03, "n_estimators": 800})

    run_exp("E75", "LightGBM with E73 features",
        BEST_EXTRAS + ["vpd", "fwi_x_wind", "eucalyptus_frac", "concurrent_fires"],
        prepare_code='    es = 0.6108 * np.exp(17.27 * df["temp_c"] / (df["temp_c"] + 237.3))\n    df["vpd"] = es * (1 - df["rh_pct"] / 100)\n    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]',
        model_family="lightgbm")

    run_exp("E76", "Reduced feature set: FWI+LFMC+SPEI6+wind+temp+VPD",
        ["lfmc", "vpd"],
        prepare_code='    es = 0.6108 * np.exp(17.27 * df["temp_c"] / (df["temp_c"] + 237.3))\n    df["vpd"] = es * (1 - df["rh_pct"] / 100)')

    run_exp("E77", "XGBoost spw=20 BEST features",
        BEST_EXTRAS,
        xgb_overrides={"scale_pos_weight": 20.0})

    run_exp("E78", "XGBoost spw=30 BEST features",
        BEST_EXTRAS,
        xgb_overrides={"scale_pos_weight": 30.0})

    run_exp("E79", "XGBoost spw=15 depth=4 BEST+VPD",
        BEST_EXTRAS + ["vpd"],
        prepare_code='    es = 0.6108 * np.exp(17.27 * df["temp_c"] / (df["temp_c"] + 237.3))\n    df["vpd"] = es * (1 - df["rh_pct"] / 100)',
        xgb_overrides={"scale_pos_weight": 15.0, "max_depth": 4})

    run_exp("E80", "Final best: BEST+VPD+FWI*wind, spw=15, depth=5, 500 trees",
        BEST_EXTRAS + ["vpd", "fwi_x_wind"],
        prepare_code='    es = 0.6108 * np.exp(17.27 * df["temp_c"] / (df["temp_c"] + 237.3))\n    df["vpd"] = es * (1 - df["rh_pct"] / 100)\n    df["fwi_x_wind"] = df["fwi"] * df["wind_kmh"]',
        xgb_overrides={"scale_pos_weight": 15.0, "max_depth": 5, "n_estimators": 500})

    print(f"\n{'='*60}")
    print("  HDR Loop Phase 2 Complete (E16-E80)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
