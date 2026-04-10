"""
Model and feature engineering for DART cascading delay day prediction.

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
    "dow_sin", "dow_cos", "month_sin", "month_cos",
    "is_weekend", "is_monday", "is_friday",
    "wind_speed_kmh", "rainfall_mm", "temperature_c",
    "post_timetable_change", "year",
    "prev_day_punct", "prev_day_bad",
    "rolling_7d_punct", "rolling_7d_bad_count",
    "morning_punct",
]

# Additional features added during HDR loop — start empty, add one at a time
EXTRA_FEATURES: list[str] = [
    "wind_above_50",
    "rain_above_10",
    "morning_afternoon_gap",
    "rolling_7d_bad_rate",
    "post_change_x_wind",
    "is_school_term",
    "prev_day_bad_x_monday",
    "wind_dir_coastal_exposure",
    "rolling_3d_punct",
]


def get_feature_columns() -> list[str]:
    """Return the full list of feature columns for the model."""
    return BASE_FEATURES + EXTRA_FEATURES


# ============================================================================
# Model configuration — modified during HDR loop
# ============================================================================

MODEL_FAMILY = "xgboost"  # one of: xgboost, lightgbm, extratrees, ridge

XGBOOST_PARAMS = {
    "max_depth": 5,
    "learning_rate": 0.05,
    "min_child_weight": 5,
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
    "max_depth": 5,
    "learning_rate": 0.05,
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
    configs = {
        "xgboost": XGBOOST_PARAMS,
        "lightgbm": LIGHTGBM_PARAMS,
        "extratrees": EXTRATREES_PARAMS,
        "ridge": RIDGE_PARAMS,
    }
    return {
        "family": MODEL_FAMILY,
        "params": configs.get(MODEL_FAMILY, XGBOOST_PARAMS),
    }


def build_model(config: Optional[dict] = None):
    """Build and return the model object (unfitted)."""
    if config is None:
        config = get_model_config()

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
    """Prepare features for model training/prediction.

    Adds engineered features from the EXTRA_FEATURES list.
    This function is called by evaluate.py before splitting.
    """
    df = df.copy()

    # Wind threshold feature (Bray-Greystones exposure)
    if "wind_above_50" in EXTRA_FEATURES or "wind_above_50" in BASE_FEATURES:
        df["wind_above_50"] = (df["wind_speed_kmh"] > 50).astype(int)

    # Heavy rain threshold
    if "rain_above_10" in EXTRA_FEATURES or "rain_above_10" in BASE_FEATURES:
        df["rain_above_10"] = (df["rainfall_mm"] > 10).astype(int)

    # Morning-afternoon cascade gap
    if "morning_afternoon_gap" in EXTRA_FEATURES or "morning_afternoon_gap" in BASE_FEATURES:
        if "morning_punct" in df.columns and "afternoon_punctuality" in df.columns:
            df["morning_afternoon_gap"] = df["morning_punct"] - df["afternoon_punctuality"]
        else:
            df["morning_afternoon_gap"] = 0.0

    # 7-day bad day rate (rolling proportion)
    if "rolling_7d_bad_rate" in EXTRA_FEATURES or "rolling_7d_bad_rate" in BASE_FEATURES:
        df["rolling_7d_bad_rate"] = df["rolling_7d_bad_count"] / 7.0

    # Interaction: post-timetable-change X wind
    if "post_change_x_wind" in EXTRA_FEATURES or "post_change_x_wind" in BASE_FEATURES:
        df["post_change_x_wind"] = (
            df["post_timetable_change"] * df["wind_speed_kmh"]
        )

    # School term
    if "is_school_term" in EXTRA_FEATURES or "is_school_term" in BASE_FEATURES:
        # Already in data_loaders, but ensure column exists
        if "is_school_term" not in df.columns:
            df["is_school_term"] = 0

    # Previous bad day on Monday interaction
    if "prev_day_bad_x_monday" in EXTRA_FEATURES or "prev_day_bad_x_monday" in BASE_FEATURES:
        if "prev_day_bad" in df.columns and "is_monday" in df.columns:
            df["prev_day_bad_x_monday"] = df["prev_day_bad"] * df["is_monday"]
        else:
            df["prev_day_bad_x_monday"] = 0

    # Wind direction coastal exposure (Bray-Greystones faces east/SE)
    # Easterly winds (45-135 degrees) are worst for this section
    if "wind_dir_coastal_exposure" in EXTRA_FEATURES or "wind_dir_coastal_exposure" in BASE_FEATURES:
        if "wind_dir_deg" in df.columns:
            angle_from_east = np.abs(df["wind_dir_deg"] - 90)
            angle_from_east = np.minimum(angle_from_east, 360 - angle_from_east)
            df["wind_dir_coastal_exposure"] = np.cos(np.radians(angle_from_east))
        else:
            df["wind_dir_coastal_exposure"] = 0.0

    # Rolling 3-day punctuality
    if "rolling_3d_punct" in EXTRA_FEATURES or "rolling_3d_punct" in BASE_FEATURES:
        if "daily_punctuality" in df.columns:
            raw = df["daily_punctuality"].shift(1).rolling(3, min_periods=1).mean()
            df["rolling_3d_punct"] = raw.fillna(df["prev_day_punct"] if "prev_day_punct" in df.columns else 0.85)
        elif "prev_day_punct" in df.columns:
            df["rolling_3d_punct"] = (
                df["prev_day_punct"].rolling(3, min_periods=1).mean()
            )
        else:
            df["rolling_3d_punct"] = 0.0

    # Holiday flag (already in data)
    if "is_holiday" in EXTRA_FEATURES or "is_holiday" in BASE_FEATURES:
        if "is_holiday" not in df.columns:
            df["is_holiday"] = 0

    # Wind direction x speed interaction
    if "wind_dir_x_speed" in EXTRA_FEATURES or "wind_dir_x_speed" in BASE_FEATURES:
        if "wind_dir_coastal_exposure" in df.columns:
            df["wind_dir_x_speed"] = (
                df.get("wind_dir_coastal_exposure", 0) * df["wind_speed_kmh"]
            )
        else:
            df["wind_dir_x_speed"] = 0.0

    # Month x timetable interaction
    if "month_x_timetable" in EXTRA_FEATURES or "month_x_timetable" in BASE_FEATURES:
        df["month_x_timetable"] = df["month_sin"] * df["post_timetable_change"]

    # Ensure all requested features exist (fill missing with 0)
    for feat in get_feature_columns():
        if feat not in df.columns:
            df[feat] = 0.0

    return df
