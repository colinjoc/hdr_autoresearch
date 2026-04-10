"""
Model and feature engineering for Xylella Olive Decline Prediction.

Binary classification: predict whether a municipality will show NEW olive
grove health decline (NDVI drop) within the next 12 months.

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

# Base features always included (Phase 0.5 baseline)
BASE_FEATURES = [
    "latitude",
    "longitude",
    "elevation",
    "jan_tmin_mean",
    "annual_precip_mm",
    "ndvi_mean",
    "dist_epicentre_km",
    "olive_area_fraction",
]

# Categorical features (label-encoded)
CATEGORICAL_FEATURES: list[str] = []

# Additional features added during HDR loop
EXTRA_FEATURES: list[str] = [
    "dist_nearest_declining_km",  # E01 KEEP: diffusion proxy
    "already_affected",            # E04 KEEP: binary flag
    "frost_severity_index",        # E09 KEEP: combined frost threshold
    "ndvi_trend",                  # E10 KEEP: temporal NDVI derivative
    "ndvi_anomaly",                # E11 KEEP: NDVI departure from mean
    "ndvi_std",                    # E12 KEEP: NDVI variability
    "summer_precip_mm",            # E15 KEEP: drought stress proxy
    "ndvi_x_jan_tmin",             # E17 KEEP: vegetation-frost interaction
]

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
    "objective": "binary:logistic",
    "eval_metric": "auc",
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
    "objective": "binary",
    "metric": "auc",
    "device": "cpu",
    "random_state": 42,
    "verbose": -1,
}

EXTRATREES_PARAMS = {
    "n_estimators": 500,
    "max_depth": None,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "max_features": "sqrt",
    "random_state": 42,
    "n_jobs": -1,
}

RIDGE_PARAMS = {
    "alpha": 1.0,
    "max_iter": 1000,
}


def get_model_config() -> dict:
    """Return the current model configuration dict."""
    configs = {
        "xgboost": XGBOOST_PARAMS,
        "lightgbm": LIGHTGBM_PARAMS,
        "extratrees": EXTRATREES_PARAMS,
        "ridge": RIDGE_PARAMS,
    }
    return configs[MODEL_FAMILY]


def build_model(family: Optional[str] = None, params: Optional[dict] = None):
    """Build and return a classifier instance.

    Args:
        family: Model family override. If None, uses MODEL_FAMILY.
        params: Parameter override. If None, uses get_model_config().

    Returns:
        Unfitted classifier with .fit() and .predict_proba() methods.
    """
    fam = family or MODEL_FAMILY
    p = params or get_model_config() if family is None else params

    if fam == "xgboost":
        import xgboost as xgb
        cfg = (p or XGBOOST_PARAMS).copy()
        rs = cfg.pop("random_state", 42)
        return xgb.XGBClassifier(**cfg, random_state=rs)

    elif fam == "lightgbm":
        import lightgbm as lgb
        cfg = (p or LIGHTGBM_PARAMS).copy()
        rs = cfg.pop("random_state", 42)
        return lgb.LGBMClassifier(**cfg, random_state=rs)

    elif fam == "extratrees":
        from sklearn.ensemble import ExtraTreesClassifier
        cfg = (p or EXTRATREES_PARAMS).copy()
        return ExtraTreesClassifier(**cfg)

    elif fam == "ridge":
        from sklearn.linear_model import LogisticRegression
        cfg = (p or RIDGE_PARAMS).copy()
        alpha = cfg.pop("alpha", 1.0)
        max_iter = cfg.pop("max_iter", 1000)
        return LogisticRegression(
            C=1.0 / alpha, penalty="l2", solver="lbfgs",
            max_iter=max_iter, random_state=42,
        )

    else:
        raise ValueError(f"Unknown model family: {fam}")


def prepare_features(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Prepare feature matrix X and label vector y from DataFrame.

    Args:
        df: DataFrame with all feature columns and 'new_decline_12m' label.

    Returns:
        (X, y) where X is float32 array and y is int array.
    """
    feature_cols = get_feature_columns()

    # Build feature matrix
    X = df[feature_cols].copy()

    # Encode categoricals
    for col in CATEGORICAL_FEATURES + EXTRA_CATEGORICAL:
        if col in X.columns:
            X[col] = X[col].astype("category").cat.codes

    # Fill NaN with 0 and convert to float32
    X = X.fillna(0).values.astype(np.float32)

    # Label
    y = df["new_decline_12m"].values.astype(int)

    return X, y
