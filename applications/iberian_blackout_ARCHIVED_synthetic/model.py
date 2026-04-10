"""
Model and feature engineering for Iberian blackout cascade prediction.

This is the file modified during HDR experiments.
Each experiment changes ONE thing here, evaluated by evaluate.py.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

# ============================================================================
# Feature configuration — modified during HDR loop
# ============================================================================

# Base features always included
BASE_FEATURES = [
    "gen_nuclear_mw", "gen_coal_mw", "gen_gas_ccgt_mw", "gen_gas_ocgt_mw",
    "gen_hydro_mw", "gen_wind_mw", "gen_solar_mw", "gen_other_re_mw",
    "gen_total_mw", "load_total_mw",
    "hour_sin", "hour_cos", "month_sin", "month_cos",
    "is_weekend", "year",
]

# Additional features added during HDR loop — start empty, add one at a time
EXTRA_FEATURES: list[str] = []


def get_feature_columns() -> list[str]:
    """Return the full list of feature columns for the model."""
    return BASE_FEATURES + EXTRA_FEATURES


# ============================================================================
# Model configuration — modified during HDR loop
# ============================================================================

MODEL_FAMILY = "xgboost"  # one of: xgboost, lightgbm, extratrees, ridge

XGBOOST_PARAMS = {
    "max_depth": 6,
    "learning_rate": 0.05,
    "min_child_weight": 3,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "n_estimators": 300,
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "tree_method": "hist",
    "device": "cuda",
    "random_state": 42,
    "scale_pos_weight": 1.0,  # adjusted for class imbalance
}

LIGHTGBM_PARAMS = {
    "max_depth": 6,
    "learning_rate": 0.05,
    "min_child_samples": 20,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "n_estimators": 300,
    "objective": "binary",
    "metric": "auc",
    "device": "cpu",
    "random_state": 42,
    "verbose": -1,
    "scale_pos_weight": 1.0,
}

EXTRATREES_PARAMS = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_leaf": 5,
    "random_state": 42,
    "n_jobs": -1,
}

RIDGE_PARAMS = {
    "alpha": 1.0,
}


def get_model_config() -> dict:
    """Return current model configuration."""
    return {
        "family": MODEL_FAMILY,
        "xgboost_params": XGBOOST_PARAMS.copy(),
        "lightgbm_params": LIGHTGBM_PARAMS.copy(),
        "extratrees_params": EXTRATREES_PARAMS.copy(),
        "ridge_params": RIDGE_PARAMS.copy(),
        "features": get_feature_columns(),
    }


def build_model(family: Optional[str] = None):
    """Build and return an unfitted model of the specified family."""
    fam = family or MODEL_FAMILY

    if fam == "xgboost":
        import xgboost as xgb
        params = XGBOOST_PARAMS.copy()
        n_est = params.pop("n_estimators")
        rs = params.pop("random_state")
        return xgb.XGBClassifier(n_estimators=n_est, random_state=rs, **params)

    elif fam == "lightgbm":
        import lightgbm as lgb
        params = LIGHTGBM_PARAMS.copy()
        return lgb.LGBMClassifier(**params)

    elif fam == "extratrees":
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(**EXTRATREES_PARAMS)

    elif fam == "ridge":
        from sklearn.linear_model import RidgeClassifier
        return RidgeClassifier(**RIDGE_PARAMS)

    else:
        raise ValueError(f"Unknown model family: {fam}")


def prepare_features(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Extract feature matrix X and label vector y from DataFrame.

    Returns (X, y) where X has shape (n_samples, n_features) and y has shape (n_samples,).
    """
    feature_cols = get_feature_columns()

    # Check all features exist
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")

    X = df[feature_cols].values.astype(np.float32)
    y = df["freq_excursion"].values.astype(np.int32)

    return X, y
