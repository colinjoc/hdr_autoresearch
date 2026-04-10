"""
Model and feature engineering for Irish Radon Prediction.

Binary classification: predict whether an area exceeds the 200 Bq/m3
radon reference level (High Radon Area designation).

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
    "eU_mean",
    "eTh_mean",
    "K_mean",
    "elevation_mean",
    "latitude",
    "longitude",
]

# Categorical features (label-encoded)
CATEGORICAL_FEATURES = [
    "bedrock_code",
    "quat_code",
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
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_leaf": 5,
    "random_state": 42,
    "n_jobs": -1,
}

RIDGE_PARAMS = {
    "C": 1.0,
    "max_iter": 1000,
    "random_state": 42,
}


def get_model_config() -> dict:
    """Return current model configuration."""
    return {
        "family": MODEL_FAMILY,
        "features": get_feature_columns(),
        "xgboost_params": XGBOOST_PARAMS.copy(),
    }


def build_model(family: Optional[str] = None):
    """Build and return an unfitted classifier of the specified family."""
    fam = family or MODEL_FAMILY

    if fam == "xgboost":
        import xgboost as xgb
        params = XGBOOST_PARAMS.copy()
        n_est = params.pop("n_estimators")
        rs = params.pop("random_state")
        return xgb.XGBClassifier(
            n_estimators=n_est, random_state=rs, **params,
        )

    elif fam == "lightgbm":
        import lightgbm as lgb
        params = LIGHTGBM_PARAMS.copy()
        return lgb.LGBMClassifier(**params)

    elif fam == "extratrees":
        from sklearn.ensemble import ExtraTreesClassifier
        return ExtraTreesClassifier(**EXTRATREES_PARAMS)

    elif fam == "ridge":
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(
            l1_ratio=0,
            solver="lbfgs",
            **RIDGE_PARAMS,
        )

    else:
        raise ValueError(f"Unknown model family: {fam}")


def prepare_features(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Extract feature matrix X and label vector y from DataFrame.

    Handles label encoding of categorical features.
    Returns (X, y) where X has shape (n_samples, n_features) and y has shape (n_samples,).
    Target y is binary: 1 = HRA (>10% homes above 200 Bq/m3), 0 = non-HRA.
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
    y = df["is_hra"].values.astype(np.float32)

    return X, y
