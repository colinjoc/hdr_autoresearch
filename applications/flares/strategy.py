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

    # AR area change rate (delta AREA from previous day for same AR)
    df_tmp = df.copy()
    df_tmp["_date"] = pd.to_datetime(df_tmp["AR issue_date"])
    df_tmp = df_tmp.sort_values(["noaa_ar", "_date"])
    df_tmp["area_change"] = df_tmp.groupby("noaa_ar")["AREA"].diff().fillna(0)
    features["area_change"] = df_tmp["area_change"].reindex(df.index)

    # Flare history: cumulative decayed flare count per AR
    # Cdec = sum of exp(-dt/tau) for prior C+ flares from this AR
    df_sorted = df.sort_values("date") if "date" in df.columns else df
    tau = 3.0  # decay constant in days
    flare_hist = []
    ar_history = {}  # noaa_ar -> list of (date, flare_count)
    for _, row in df_sorted.iterrows():
        ar = row["noaa_ar"]
        date = pd.Timestamp(row["AR issue_date"])
        c_plus = row["C+"]
        # Compute decayed sum from prior observations of this AR
        if ar in ar_history:
            decay_sum = sum(
                count * np.exp(-(date - prev_date).days / tau)
                for prev_date, count in ar_history[ar]
            )
        else:
            decay_sum = 0.0
        flare_hist.append(decay_sum)
        # Update history
        if ar not in ar_history:
            ar_history[ar] = []
        if c_plus > 0:
            ar_history[ar].append((date, c_plus))
    # Reindex to match original df
    features["flare_hist_decay"] = pd.Series(flare_hist, index=df_sorted.index).reindex(df.index)

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
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.7,
        eval_metric="logloss",
        verbosity=0,
        random_state=42,
    )
