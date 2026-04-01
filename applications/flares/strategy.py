"""
Solar flare prediction strategy.

THIS IS THE ONLY FILE THE AUTORESEARCH AGENT MODIFIES.
"""

import numpy as np
import pandas as pd
import xgboost as xgb


def featurize(df):
    """Convert raw active region data to feature matrix.

    Args:
        df: DataFrame with columns from AR_flare_ml_23_24.csv

    Returns:
        np.ndarray of shape (n_samples, n_features)
    """
    features = pd.DataFrame(index=df.index)

    # Numerical features
    features["area"] = df["AREA"]
    features["longitude_extent"] = df["Longitude_extent"]
    features["n_sunspots"] = df["No_sunspots"]

    # Encode MAGTYPE as ordinal (complexity order)
    magtype_order = {
        "ALPHA": 0, "BETA": 1, "GAMMA": 2,
        "BETA-GAMMA": 3, "BETA-DELTA": 4,
        "GAMMA-DELTA": 5, "BETA-GAMMA-DELTA": 6,
    }
    features["magtype_ord"] = df["MAGTYPE"].map(magtype_order).fillna(0)
    features["area_x_magtype"] = df["AREA"] * features["magtype_ord"]

    # Position features
    features["abs_longitude"] = df["Longitude"].abs()

    # AR age (consecutive days observed)
    df_tmp0 = df.copy()
    df_tmp0["_date"] = pd.to_datetime(df_tmp0["AR issue_date"])
    df_tmp0 = df_tmp0.sort_values(["noaa_ar", "_date"])
    features["ar_age"] = df_tmp0.groupby("noaa_ar").cumcount().reindex(df.index)

    # AR area change rate (delta AREA from previous day for same AR)
    df_tmp = df.copy()
    df_tmp["_date"] = pd.to_datetime(df_tmp["AR issue_date"])
    df_tmp = df_tmp.sort_values(["noaa_ar", "_date"])
    df_tmp["area_change"] = df_tmp.groupby("noaa_ar")["AREA"].diff().fillna(0)
    features["area_change"] = df_tmp["area_change"].reindex(df.index)

    # Flare history: cumulative decayed flare count per AR at two timescales
    df_sorted = df.sort_values("date") if "date" in df.columns else df
    flare_hist_3 = []
    flare_hist_1 = []
    ar_history = {}
    for _, row in df_sorted.iterrows():
        ar = row["noaa_ar"]
        date = pd.Timestamp(row["AR issue_date"])
        c_plus = row["C+"]
        if ar in ar_history:
            decay_3 = sum(c * np.exp(-(date - d).days / 3.0) for d, c in ar_history[ar])
            decay_1 = sum(c * np.exp(-(date - d).days / 1.0) for d, c in ar_history[ar])
        else:
            decay_3 = 0.0
            decay_1 = 0.0
        flare_hist_3.append(decay_3)
        flare_hist_1.append(decay_1)
        if ar not in ar_history:
            ar_history[ar] = []
        if c_plus > 0:
            ar_history[ar].append((date, c_plus))
    features["flare_hist_decay3"] = pd.Series(flare_hist_3, index=df_sorted.index).reindex(df.index)
    features["flare_hist_decay1"] = pd.Series(flare_hist_1, index=df_sorted.index).reindex(df.index)

    # McIntosh sub-components
    mcintosh = df["McIntosh"].fillna("AXX")
    features["zurich"] = mcintosh.str[0].astype("category").cat.codes
    features["penumbral"] = mcintosh.str[1].astype("category").cat.codes
    features["compact"] = mcintosh.str[2].astype("category").cat.codes

    return features.values


def get_model():
    """Return a fresh model instance."""
    return xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.7,
        eval_metric="logloss",
        verbosity=0,
        random_state=42,
    )
