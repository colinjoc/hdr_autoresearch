"""
Model and feature engineering for flight delay propagation prediction.

This is the file modified during HDR experiments.
Each experiment changes ONE thing here, evaluated by evaluate.py.

Prediction task: given a flight's scheduled characteristics and the current
state of the network at departure time, predict arrival delay in minutes.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

# ============================================================================
# Feature configuration — modified during HDR loop
# ============================================================================

# Base features always included (raw scheduled + system state)
BASE_FEATURES = [
    # Temporal
    "dep_hour_sin", "dep_hour_cos",
    "dow_sin", "dow_cos",
    "month_sin", "month_cos",
    "is_weekend", "is_monday", "is_friday",
    # Route
    "distance",
    "sched_elapsed_min",
    # Congestion
    "origin_hour_flights",
    # Hub
    "origin_is_hub",
    # Carrier buffer
    "carrier_buffer_factor",
    # THE key propagation feature: previous leg delay on same tail
    "prev_leg_arr_delay",
]

# Additional features added during HDR loop — start empty, add one at a time
EXTRA_FEATURES: list[str] = [
    "rotation_position",
    "prev_leg_late_aircraft",
    "dest_hour_flights",
    "dest_is_hub",
    "schedule_buffer_min",
    "prev_leg_delay_x_buffer",
    "is_hub_to_hub",
    "morning_flight",
    "evening_flight",
    "log_prev_delay",
    "congestion_ratio",
    "is_regional_carrier",
]


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
    "min_child_weight": 10,
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
        from xgboost import XGBRegressor
        return XGBRegressor(**params)

    elif family == "lightgbm":
        from lightgbm import LGBMRegressor
        return LGBMRegressor(**params)

    elif family == "extratrees":
        from sklearn.ensemble import ExtraTreesRegressor
        return ExtraTreesRegressor(**params)

    elif family == "ridge":
        from sklearn.linear_model import Ridge
        return Ridge(**params)

    else:
        raise ValueError(f"Unknown model family: {family}")


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare features for model training/prediction.

    Adds engineered features from the EXTRA_FEATURES list.
    This function is called by evaluate.py before splitting.
    """
    df = df.copy()

    # Rotation position (already in data, but ensure present)
    if "rotation_position" not in df.columns:
        df["rotation_position"] = 1

    # Previous leg late aircraft delay (already in data)
    if "prev_leg_late_aircraft" not in df.columns:
        df["prev_leg_late_aircraft"] = 0.0

    # Destination congestion (already in data)
    if "dest_hour_flights" not in df.columns:
        df["dest_hour_flights"] = 0

    # Destination hub (already in data)
    if "dest_is_hub" not in df.columns:
        df["dest_is_hub"] = 0

    # Schedule buffer (already in data)
    if "schedule_buffer_min" not in df.columns:
        df["schedule_buffer_min"] = 0.0

    # INTERACTION: prev leg delay x carrier buffer factor
    # Core hypothesis: tight-buffer carriers propagate more delay
    if "prev_leg_delay_x_buffer" in EXTRA_FEATURES or "prev_leg_delay_x_buffer" in BASE_FEATURES:
        df["prev_leg_delay_x_buffer"] = (
            df["prev_leg_arr_delay"] * df["carrier_buffer_factor"]
        )

    # Hub-to-hub flights (highest propagation risk)
    if "is_hub_to_hub" in EXTRA_FEATURES or "is_hub_to_hub" in BASE_FEATURES:
        df["is_hub_to_hub"] = (df["origin_is_hub"] & df["dest_is_hub"]).astype(int)

    # Morning flight (06:00-09:00) — morning flights start the day's cascade
    if "morning_flight" in EXTRA_FEATURES or "morning_flight" in BASE_FEATURES:
        df["morning_flight"] = (
            (df["crs_dep_hour"] >= 6) & (df["crs_dep_hour"] <= 9)
        ).astype(int)

    # Evening flight (18:00-22:00) — evening delays die at overnight
    if "evening_flight" in EXTRA_FEATURES or "evening_flight" in BASE_FEATURES:
        df["evening_flight"] = (
            (df["crs_dep_hour"] >= 18) & (df["crs_dep_hour"] <= 22)
        ).astype(int)

    # Log transform of previous delay (compresses large delays)
    if "log_prev_delay" in EXTRA_FEATURES or "log_prev_delay" in BASE_FEATURES:
        df["log_prev_delay"] = np.log1p(np.clip(df["prev_leg_arr_delay"], 0, None))

    # Congestion ratio: origin flights / typical for this hour
    if "congestion_ratio" in EXTRA_FEATURES or "congestion_ratio" in BASE_FEATURES:
        median_flights = df.groupby("crs_dep_hour")["origin_hour_flights"].transform("median")
        df["congestion_ratio"] = df["origin_hour_flights"] / median_flights.clip(lower=1)

    # Regional carrier flag (MQ, OO, YX — tighter operations)
    if "is_regional_carrier" in EXTRA_FEATURES or "is_regional_carrier" in BASE_FEATURES:
        regional = {"MQ", "OO", "YX"}
        df["is_regional_carrier"] = df["carrier"].isin(regional).astype(int)

    # Ensure all requested features exist (fill missing with 0)
    for feat in get_feature_columns():
        if feat not in df.columns:
            df[feat] = 0.0

    return df
