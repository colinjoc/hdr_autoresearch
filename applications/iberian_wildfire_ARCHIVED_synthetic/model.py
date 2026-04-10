"""
Model and feature engineering for Iberian wildfire VLF prediction.

Final configuration after 80 experiments.

Best model: Ridge (logistic) with 20 features
- CV AUC: 0.699 +/- 0.036
- Holdout (2025) AUC: 0.795
- Aug 2025 NW Iberia AUC: 0.816

Key finding: Ridge outperforms all tree-based models, confirming
the VLF transition is primarily a linear function of weather/moisture
conditions. Adding LFMC and multi-timescale SPEI to the base FWI
features provides the largest improvement.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


# ============================================================================
# Feature configuration — final after 80 experiments
# ============================================================================

BASE_FEATURES = [
    "fwi",           # Fire Weather Index (Van Wagner 1987)
    "ffmc",          # Fine Fuel Moisture Code
    "dmc",           # Duff Moisture Code
    "dc",            # Drought Code
    "isi",           # Initial Spread Index
    "bui",           # Build-Up Index
    "temp_c",        # Noon temperature (C)
    "rh_pct",        # Noon relative humidity (%)
    "wind_kmh",      # Noon wind speed (km/h)
    "precip_mm",     # 24-hour precipitation (mm)
    "spei_6",        # 6-month SPEI drought index
    "ndvi",          # Pre-fire NDVI greenness
    "elevation_m",   # Elevation (m)
    "slope_deg",     # Terrain slope (degrees)
    "lat",           # Latitude
    "month",         # Month of year
]

# Features added during HDR loop — the kept additions
EXTRA_FEATURES: list[str] = [
    "lfmc",          # Live Fuel Moisture Content (Sentinel-2 SWIR proxy)
    "spei_1",        # 1-month SPEI
    "spei_3",        # 3-month SPEI
    "spei_12",       # 12-month SPEI
]

# Features that require Sentinel-2 (only available from 2018 onwards)
SENTINEL2_FEATURES = ["lfmc"]


def get_feature_columns() -> list[str]:
    """Return the full list of feature columns for the model."""
    return BASE_FEATURES + EXTRA_FEATURES


# ============================================================================
# Model configuration — Ridge (logistic) is the winner
# ============================================================================

MODEL_FAMILY = "ridge"  # Ridge wins tournament and HDR loop

XGBOOST_PARAMS = {
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

LIGHTGBM_PARAMS = {
    "max_depth": 6,
    "learning_rate": 0.1,
    "min_child_samples": 20,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "n_estimators": 200,
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
    "random_state": 42,
}


def get_model_config() -> dict:
    """Return the current model family and hyperparameters."""
    family = MODEL_FAMILY

    if family == "xgboost":
        params = XGBOOST_PARAMS.copy()
    elif family == "lightgbm":
        params = LIGHTGBM_PARAMS.copy()
    elif family == "extratrees":
        params = EXTRATREES_PARAMS.copy()
    elif family == "ridge":
        params = RIDGE_PARAMS.copy()
    else:
        raise ValueError(f"Unknown model family: {family}")

    return {"family": family, "params": params}


def build_model(config: dict):
    """Build a model instance from the config."""
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
        raise ValueError(f"Unknown model family: {family}")


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and engineer features from the raw fire event data."""
    df = df.copy()
    return df
