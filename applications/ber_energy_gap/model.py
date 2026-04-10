"""
Model and feature engineering for Irish BER vs Real Home Energy Gap analysis.

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
    "year_built",
    "floor_area_m2",
    "wall_u_value",
    "roof_u_value",
    "floor_u_value",
    "window_u_value",
    "heating_efficiency",
    "primary_energy_factor",
    "air_permeability",
    "hdd",
    "n_storeys",
    "n_bedrooms",
    "has_floor_insulation",
]

# Categorical features (label-encoded)
CATEGORICAL_FEATURES = [
    "county",
    "dwelling_type",
    "wall_type",
    "insulation_type",
    "window_type",
    "heating_type",
    "ventilation_type",
    "secondary_heating",
]

# Additional features added during HDR loop — start empty, add one at a time
EXTRA_FEATURES: list[str] = []

# Extra categorical features added during HDR loop
EXTRA_CATEGORICAL: list[str] = []


def get_feature_columns() -> list[str]:
    """Return the full list of feature columns for the model."""
    return BASE_FEATURES + CATEGORICAL_FEATURES + EXTRA_FEATURES + EXTRA_CATEGORICAL


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
    "objective": "reg:squarederror",
    "eval_metric": "mae",
    "tree_method": "hist",
    "device": "cuda",
    "random_state": 42,
}

LIGHTGBM_PARAMS = {
    "max_depth": 6,
    "learning_rate": 0.05,
    "min_child_samples": 20,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "n_estimators": 300,
    "objective": "regression",
    "metric": "mae",
    "device": "cpu",
    "random_state": 42,
    "verbose": -1,
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
        "features": get_feature_columns(),
        "xgboost_params": XGBOOST_PARAMS.copy(),
    }


def build_model(family: Optional[str] = None):
    """Build and return an unfitted model of the specified family."""
    fam = family or MODEL_FAMILY

    if fam == "xgboost":
        import xgboost as xgb
        params = XGBOOST_PARAMS.copy()
        n_est = params.pop("n_estimators")
        rs = params.pop("random_state")
        return xgb.XGBRegressor(n_estimators=n_est, random_state=rs, **params)

    elif fam == "lightgbm":
        import lightgbm as lgb
        params = LIGHTGBM_PARAMS.copy()
        return lgb.LGBMRegressor(**params)

    elif fam == "extratrees":
        from sklearn.ensemble import ExtraTreesRegressor
        return ExtraTreesRegressor(**EXTRATREES_PARAMS)

    elif fam == "ridge":
        from sklearn.linear_model import Ridge
        return Ridge(**RIDGE_PARAMS)

    else:
        raise ValueError(f"Unknown model family: {fam}")


def prepare_features(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Extract feature matrix X and label vector y from DataFrame.

    Handles label encoding of categorical features.
    Returns (X, y) where X has shape (n_samples, n_features) and y has shape (n_samples,).
    """
    feature_cols = get_feature_columns()
    all_categoricals = CATEGORICAL_FEATURES + EXTRA_CATEGORICAL

    # Build feature matrix
    frames = []
    for col in feature_cols:
        if col in all_categoricals:
            # Label encode
            codes, _ = pd.factorize(df[col])
            frames.append(pd.Series(codes, name=col))
        else:
            if col not in df.columns:
                raise ValueError(f"Missing feature column: {col}")
            frames.append(df[col].reset_index(drop=True))

    X_df = pd.concat(frames, axis=1)
    X = X_df.values.astype(np.float32)
    y = df["energy_value_kwh_m2_yr"].values.astype(np.float32)

    return X, y
