"""
Model and feature engineering for Dublin NO2 source attribution.

This is the file modified during HDR experiments.
Each experiment changes ONE thing here, evaluated by evaluate.py.

Target: hourly NO2 concentration (ug/m3) at Dublin monitoring stations.
Task: regression (predict NO2) + binary classification (predict WHO exceedance).
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

# ============================================================================
# Feature configuration — modified during HDR loop
# ============================================================================

# Base features: meteorological + temporal (Phase 0.5 baseline)
BASE_FEATURES = [
    "wind_speed_ms", "wind_dir_deg", "temperature_c", "rainfall_mm",
    "blh_proxy_m",
    "hour_sin", "hour_cos",
    "dow_sin", "dow_cos",
    "month_sin", "month_cos",
    "is_weekend",
    "is_heating_season",
]

# Additional features added during HDR loop
EXTRA_FEATURES: list[str] = [
    "rush_hour_weekday",
    "year_trend",
]

# Station encoding (one-hot for station fixed effects)
STATION_FEATURES: list[str] = [
    "station_pearse_street",
    "station_winetavern_street",
    "station_rathmines",
    "station_dun_laoghaire",
    "station_ringsend",
    "station_kilkenny",
    "station_cork_old_station_road",
]


def get_feature_columns() -> list[str]:
    """Return the full list of feature columns for the model."""
    return BASE_FEATURES + EXTRA_FEATURES + STATION_FEATURES


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
    "min_samples_leaf": 10,
    "random_state": 42,
    "n_jobs": -1,
}

RIDGE_PARAMS = {
    "alpha": 1.0,
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

    Adds engineered features. Called by evaluate.py before splitting.
    """
    df = df.copy()

    # Cyclic encoding of hour, day of week, month
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"] = np.sin(2 * np.pi * df["dow"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["dow"] / 7)
    df["month_sin"] = np.sin(2 * np.pi * (df["month"] - 1) / 12)
    df["month_cos"] = np.cos(2 * np.pi * (df["month"] - 1) / 12)

    # --- EXTRA FEATURES (added during HDR loop) ---

    # Wind direction sectors (for source attribution)
    if "wind_dir_traffic" in EXTRA_FEATURES:
        # Wind from traffic corridors (S-SW, 180-250 degrees)
        angle_from_traffic = np.abs(df["wind_dir_deg"] - 215) % 360
        angle_from_traffic = np.minimum(angle_from_traffic, 360 - angle_from_traffic)
        df["wind_dir_traffic"] = np.cos(np.radians(angle_from_traffic))

    if "wind_dir_port" in EXTRA_FEATURES:
        # Wind from Dublin Port direction (E-NE, 45-90 degrees)
        angle_from_port = np.abs(df["wind_dir_deg"] - 70) % 360
        angle_from_port = np.minimum(angle_from_port, 360 - angle_from_port)
        df["wind_dir_port"] = np.cos(np.radians(angle_from_port))

    # Traffic proxy features
    if "rush_hour" in EXTRA_FEATURES:
        df["rush_hour"] = (
            ((df["hour"] >= 7) & (df["hour"] <= 9)) |
            ((df["hour"] >= 16) & (df["hour"] <= 19))
        ).astype(int)

    if "rush_hour_weekday" in EXTRA_FEATURES:
        df["rush_hour_weekday"] = (
            (df["is_weekend"] == 0) &
            (((df["hour"] >= 7) & (df["hour"] <= 9)) |
             ((df["hour"] >= 16) & (df["hour"] <= 19)))
        ).astype(int)

    # Heating features
    if "cold_evening" in EXTRA_FEATURES:
        df["cold_evening"] = (
            (df["is_heating_season"] == 1) &
            (df["hour"] >= 17) & (df["hour"] <= 22) &
            (df["temperature_c"] < 8)
        ).astype(int)

    if "temp_heating_interaction" in EXTRA_FEATURES:
        df["temp_heating_interaction"] = (
            df["is_heating_season"] * np.clip(12.0 - df["temperature_c"], 0, 20) / 20.0
        )

    # Wind dispersion features
    if "calm_wind" in EXTRA_FEATURES:
        df["calm_wind"] = (df["wind_speed_ms"] < 1.5).astype(int)

    if "wind_x_blh" in EXTRA_FEATURES:
        df["wind_x_blh"] = df["wind_speed_ms"] * df["blh_proxy_m"] / 1000.0

    if "inverse_ventilation" in EXTRA_FEATURES:
        # Ventilation coefficient = wind × BLH; inverse = poor dispersion
        vent = df["wind_speed_ms"] * df["blh_proxy_m"]
        df["inverse_ventilation"] = 1.0 / np.clip(vent, 100, None)

    # Rain interaction
    if "rain_washout" in EXTRA_FEATURES:
        df["rain_washout"] = np.clip(df["rainfall_mm"] / 5.0, 0, 1)

    # COVID lockdown
    if "is_lockdown" in EXTRA_FEATURES:
        pass  # Already in data

    # Year trend
    if "year_trend" in EXTRA_FEATURES:
        df["year_trend"] = df["year"] - 2019

    # Station fixed effects (one-hot)
    if STATION_FEATURES:
        for feat in STATION_FEATURES:
            sname = feat.replace("station_", "")
            df[feat] = (df["station"] == sname).astype(int)

    # Weekend morning as background estimator
    if "weekend_early_morning" in EXTRA_FEATURES:
        df["weekend_early_morning"] = (
            (df["is_weekend"] == 1) & (df["hour"] >= 2) & (df["hour"] <= 5)
        ).astype(int)

    # Wind direction × rush hour interaction
    if "rush_wind_dir_traffic" in EXTRA_FEATURES:
        if "rush_hour" not in df.columns:
            df["rush_hour"] = (
                ((df["hour"] >= 7) & (df["hour"] <= 9)) |
                ((df["hour"] >= 16) & (df["hour"] <= 19))
            ).astype(int)
        if "wind_dir_traffic" not in df.columns:
            angle = np.abs(df["wind_dir_deg"] - 215) % 360
            angle = np.minimum(angle, 360 - angle)
            df["wind_dir_traffic"] = np.cos(np.radians(angle))
        df["rush_wind_dir_traffic"] = df["rush_hour"] * df["wind_dir_traffic"]

    # Temperature inversion proxy (cold surface + warm aloft = trapping)
    if "temp_inversion_proxy" in EXTRA_FEATURES:
        # Night-time cold surface in winter with low wind = likely inversion
        df["temp_inversion_proxy"] = (
            (df["temperature_c"] < 5) &
            (df["wind_speed_ms"] < 2) &
            ((df["hour"] >= 20) | (df["hour"] <= 7))
        ).astype(float)

    # Exceedance binary target (for classification metrics)
    if "no2_24h_mean" not in df.columns and "no2_ugm3" in df.columns:
        # Group by station to compute per-station 24h mean
        df["no2_24h_mean"] = df.groupby("station")["no2_ugm3"].transform(
            lambda x: x.rolling(24, min_periods=12).mean()
        )
    if "no2_24h_mean" in df.columns:
        df["exceeds_who_24h"] = (df["no2_24h_mean"] > 25).astype(int)

    # Ensure all requested features exist (fill missing with 0)
    for feat in get_feature_columns():
        if feat not in df.columns:
            df[feat] = 0.0

    return df
