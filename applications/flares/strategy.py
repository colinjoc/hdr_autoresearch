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
