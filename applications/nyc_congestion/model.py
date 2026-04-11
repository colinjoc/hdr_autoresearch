"""NYC congestion charge effect decomposition — model and analysis.

The core question: did the NYC congestion charge (Jan 2025) actually reduce
traffic, or did it displace it? We decompose observed changes into:
  1. Genuine mode shift (switch to transit)
  2. Route displacement (to side streets / outer boroughs)
  3. Time-of-day shift (travel at off-peak to avoid charge)
  4. Trip elimination (trips that simply stopped happening)

Methods:
  - Difference-in-differences (Manhattan CBD vs outer boroughs)
  - Predictive model: predict weekly borough-level volume from pre-charge
    features, then measure counterfactual gap
  - Decomposition via TLC trip records + MTA ridership + CRZ entry data
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

try:
    import xgboost as xgb
    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False

from data_loaders import (
    CHARGE_START,
    build_master_dataset,
    load_mta_ridership,
    aggregate_mta_weekly,
    load_tlc_summary,
    load_traffic_counts,
    aggregate_daily_volume,
)

# ---------------------------------------------------------------- feature set
# For predicting weekly traffic volume.
# Target: daily_vol_sum (total weekly volume for a borough)
# We use pre-charge data only for training, then predict post-charge
# counterfactual to measure the actual effect.
FEATURE_COLS: List[str] = [
    "week_num", "month", "year", "n_days",
    "vol_lag1w", "vol_lag2w", "vol_rolling4w",
    "subway_ridership", "bus_ridership",
    "is_manhattan", "is_bronx", "is_brooklyn", "is_queens", "is_staten_island",
]

TARGET_COL = "daily_vol_mean"


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer features for the prediction model."""
    df = df.copy()

    # Borough dummies
    df["is_manhattan"] = (df["boro"] == "Manhattan").astype(int)
    df["is_bronx"] = (df["boro"] == "Bronx").astype(int)
    df["is_brooklyn"] = (df["boro"] == "Brooklyn").astype(int)
    df["is_queens"] = (df["boro"] == "Queens").astype(int)
    df["is_staten_island"] = (df["boro"] == "Staten Island").astype(int)

    # Lag features (within borough)
    df = df.sort_values(["boro", "week_start"]).reset_index(drop=True)
    for lag in [1, 2]:
        df[f"vol_lag{lag}w"] = df.groupby("boro")["daily_vol_mean"].shift(lag)

    # Rolling mean
    df["vol_rolling4w"] = (
        df.groupby("boro")["daily_vol_mean"]
        .transform(lambda x: x.rolling(4, min_periods=1).mean())
    )

    return df


def build_clean_dataset() -> pd.DataFrame:
    """Build and clean the master dataset with features."""
    df = build_master_dataset()
    df = add_features(df)
    # Drop rows with NaN in key feature columns (from lags)
    df = df.dropna(subset=["vol_lag1w", "vol_lag2w"]).reset_index(drop=True)
    # Fill remaining NaN in transit columns with median
    for col in ["subway_ridership", "bus_ridership"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    return df


def _get_Xy(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Extract feature matrix and target from clean dataset."""
    feats = [c for c in FEATURE_COLS if c in df.columns]
    X = df[feats].copy()
    y = df[TARGET_COL].copy()
    return X, y


def train_volume_model(
    df: pd.DataFrame,
    model_factory=None,
    n_splits: int = 5,
    seed: int = 42,
) -> Tuple[object, Dict[str, float]]:
    """Train and cross-validate a volume prediction model.

    Uses 5-fold CV on pre-charge data to evaluate generalisation,
    then fits on all pre-charge data for counterfactual prediction.

    Returns (fitted_model, metrics_dict).
    """
    if model_factory is None:
        model_factory = lambda: ExtraTreesRegressor(
            n_estimators=200, max_depth=12, random_state=seed, n_jobs=-1
        )

    X, y = _get_Xy(df)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)

    oof_preds = np.full(len(y), np.nan)
    for train_idx, val_idx in kf.split(X):
        m = model_factory()
        m.fit(X.iloc[train_idx], y.iloc[train_idx])
        oof_preds[val_idx] = m.predict(X.iloc[val_idx])

    mask = ~np.isnan(oof_preds)
    mae = mean_absolute_error(y[mask], oof_preds[mask])
    rmse = np.sqrt(mean_squared_error(y[mask], oof_preds[mask]))
    r2 = r2_score(y[mask], oof_preds[mask])

    # Fit final model on all data
    final_model = model_factory()
    final_model.fit(X, y)

    metrics = {"mae": mae, "rmse": rmse, "r2": r2}
    return final_model, metrics


def run_tournament(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Run a model family tournament. Returns DataFrame of results."""
    factories = {
        "ExtraTrees": lambda: ExtraTreesRegressor(
            n_estimators=200, max_depth=12, random_state=seed, n_jobs=-1
        ),
        "RandomForest": lambda: RandomForestRegressor(
            n_estimators=200, max_depth=12, random_state=seed, n_jobs=-1
        ),
        "GBR": lambda: GradientBoostingRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.05, random_state=seed
        ),
        "Ridge": lambda: Ridge(alpha=1.0),
    }
    if _HAS_XGB:
        factories["XGBoost"] = lambda: xgb.XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.05,
            random_state=seed, verbosity=0,
        )

    results = []
    for name, factory in factories.items():
        _, metrics = train_volume_model(df, model_factory=factory, seed=seed)
        results.append({"model": name, **metrics})

    return pd.DataFrame(results).sort_values("mae")


def decompose_volume_change(df: pd.DataFrame) -> Dict[str, float]:
    """Decompose the post-charge traffic volume change into components.

    Components:
      - mode_shift: estimated from transit ridership increase
      - route_displacement: Manhattan decrease offset by outer borough increase
      - time_shift: change in peak-hour share
      - trip_elimination: residual after accounting for other components

    Returns dict with component values as percentage change in CBD volume.
    """
    # Split pre/post
    pre = df[df["post_charge"] == 0]
    post = df[df["post_charge"] == 1]

    # --- Total observed change in Manhattan volume ---
    man_pre = pre[pre["boro"] == "Manhattan"]["daily_vol_mean"].mean()
    man_post = post[post["boro"] == "Manhattan"]["daily_vol_mean"].mean()
    total_change_pct = ((man_post - man_pre) / man_pre * 100) if man_pre > 0 else 0.0

    # --- Mode shift: proxy via transit ridership increase ---
    transit_cols = ["subway_ridership", "bus_ridership"]
    available_transit = [c for c in transit_cols if c in df.columns and df[c].notna().any()]
    if available_transit:
        transit_pre = pre[available_transit].mean().sum()
        transit_post = post[available_transit].mean().sum()
        transit_change_pct = ((transit_post - transit_pre) / transit_pre * 100) if transit_pre > 0 else 0.0
        # Scale: each transit rider gained = fraction of car trips removed
        # Upper bound: 30% of transit increase was mode-shifted drivers
        mode_shift = min(transit_change_pct * 0.3, abs(total_change_pct) * 0.5)
        if total_change_pct < 0:
            mode_shift = -abs(mode_shift)
        else:
            mode_shift = abs(mode_shift)
    else:
        mode_shift = 0.0

    # --- Route displacement: outer borough volume change ---
    outer_boros = ["Bronx", "Brooklyn", "Queens", "Staten Island"]
    outer_pre = pre[pre["boro"].isin(outer_boros)]["daily_vol_mean"].mean()
    outer_post = post[post["boro"].isin(outer_boros)]["daily_vol_mean"].mean()
    if outer_pre > 0:
        outer_change_pct = (outer_post - outer_pre) / outer_pre * 100
        route_displacement = outer_change_pct * 0.5
    else:
        route_displacement = 0.0
        outer_change_pct = 0.0

    # --- Time-of-day shift ---
    traffic = load_traffic_counts()
    traffic["post_charge"] = (traffic["date"] >= CHARGE_START).astype(int)
    man_traffic = traffic[traffic["boro"] == "Manhattan"]
    if len(man_traffic) > 0 and "hour" in man_traffic.columns:
        peak_hours = [7, 8, 9, 16, 17, 18]
        pre_traffic = man_traffic[man_traffic["post_charge"] == 0]
        post_traffic = man_traffic[man_traffic["post_charge"] == 1]
        if len(pre_traffic) > 0 and len(post_traffic) > 0:
            pre_peak_share = pre_traffic[pre_traffic["hour"].isin(peak_hours)]["vol"].sum() / max(pre_traffic["vol"].sum(), 1)
            post_peak_share = post_traffic[post_traffic["hour"].isin(peak_hours)]["vol"].sum() / max(post_traffic["vol"].sum(), 1)
            time_shift = (post_peak_share - pre_peak_share) / max(pre_peak_share, 0.01) * 100
        else:
            time_shift = 0.0
    else:
        time_shift = 0.0

    # --- Trip elimination: residual ---
    trip_elimination = total_change_pct - mode_shift - route_displacement - time_shift

    return {
        "total_change": total_change_pct,
        "mode_shift": mode_shift,
        "route_displacement": route_displacement,
        "time_shift": time_shift,
        "trip_elimination": trip_elimination,
        "manhattan_pre_vol": man_pre,
        "manhattan_post_vol": man_post,
        "outer_boro_change_pct": outer_change_pct,
    }


def did_estimate(df: pd.DataFrame) -> Dict[str, float]:
    """Difference-in-differences estimate of congestion charge effect.

    Treatment: Manhattan. Control: outer boroughs.
    Pre: before Jan 5 2025. Post: after.
    """
    master = df if "post_charge" in df.columns else build_master_dataset()
    master = add_features(master) if "is_manhattan" not in master.columns else master

    master["treated"] = (master["boro"] == "Manhattan").astype(int)
    master["post"] = master["post_charge"]
    master["did"] = master["treated"] * master["post"]

    try:
        import statsmodels.api as sm
        X = master[["treated", "post", "did"]].astype(float)
        X = sm.add_constant(X)
        y = master["daily_vol_mean"].astype(float)
        mask = y.notna() & X.notna().all(axis=1)
        result = sm.OLS(y[mask], X[mask]).fit()
        did_coeff = float(result.params["did"])
        p_val = float(result.pvalues["did"])
    except Exception:
        pre_treat = master[(master["treated"] == 1) & (master["post"] == 0)]["daily_vol_mean"].mean()
        post_treat = master[(master["treated"] == 1) & (master["post"] == 1)]["daily_vol_mean"].mean()
        pre_ctrl = master[(master["treated"] == 0) & (master["post"] == 0)]["daily_vol_mean"].mean()
        post_ctrl = master[(master["treated"] == 0) & (master["post"] == 1)]["daily_vol_mean"].mean()
        did_coeff = (post_treat - pre_treat) - (post_ctrl - pre_ctrl)
        p_val = np.nan

    return {"did_coeff": did_coeff, "p_value": p_val}


def compute_counterfactual(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Train on pre-charge data, predict counterfactual for post-charge period.

    Returns DataFrame with actual vs predicted (counterfactual) volume.
    """
    pre = df[df["post_charge"] == 0].copy()
    post = df[df["post_charge"] == 1].copy()

    feats = [c for c in FEATURE_COLS if c in df.columns]

    model = ExtraTreesRegressor(n_estimators=200, max_depth=12,
                                 random_state=seed, n_jobs=-1)
    X_pre = pre[feats]
    y_pre = pre[TARGET_COL]
    model.fit(X_pre, y_pre)

    # Predict counterfactual for post period
    X_post = post[feats]
    post["predicted_counterfactual"] = model.predict(X_post)
    post["actual"] = post[TARGET_COL]
    post["effect"] = post["actual"] - post["predicted_counterfactual"]
    post["effect_pct"] = post["effect"] / post["predicted_counterfactual"] * 100

    return post[["boro", "week_start", "actual", "predicted_counterfactual",
                  "effect", "effect_pct"]].copy()
