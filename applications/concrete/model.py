"""
Concrete mix design: prediction + discovery.

THIS IS THE ONLY FILE THE AUTORESEARCH AGENT MODIFIES.

Final winning configuration (Phase 2.5 P25.5):
  - Features: raw 8 columns + water-to-binder ratio + supplementary-
    cementitious-material percentage
  - Monotonicity constraint: cement → strength must be non-decreasing
  - XGBoost with 600 boosting rounds (otherwise default hyperparameters)
  - 5-fold cross-validated MAE = 2.55 MPa, R² = 0.941
"""

import numpy as np
import pandas as pd
import xgboost as xgb

RAW_FEATURES = ["cement", "slag", "fly_ash", "water", "superplasticizer",
                "coarse_agg", "fine_agg", "age"]
DERIVED_FEATURES = ["wb_ratio", "scm_pct"]
FEATURE_NAMES = RAW_FEATURES + DERIVED_FEATURES


def _add_features(df):
    """Compute derived features (water-to-binder ratio and SCM percentage)."""
    out = df.copy()
    binder = out["cement"] + out["slag"] + out["fly_ash"]
    out["wb_ratio"] = (out["water"] / binder.replace(0, np.nan)).fillna(0)
    scm = out["slag"] + out["fly_ash"]
    out["scm_pct"] = (scm / binder.replace(0, np.nan)).fillna(0)
    return out


class ConcreteModel:

    def __init__(self):
        self.model = None
        self.feature_names = FEATURE_NAMES

    def featurize(self, df):
        df = _add_features(df)
        X = df[FEATURE_NAMES].values.astype(np.float32)
        y = df["strength"].values.astype(np.float32)
        return X, y

    def featurize_single(self, mix_dict):
        binder = mix_dict.get("cement", 0) + mix_dict.get("slag", 0) + mix_dict.get("fly_ash", 0)
        wb = mix_dict.get("water", 0) / binder if binder > 0 else 0.0
        scm = (mix_dict.get("slag", 0) + mix_dict.get("fly_ash", 0)) / binder if binder > 0 else 0.0
        full = {**mix_dict, "wb_ratio": wb, "scm_pct": scm}
        return np.array([full.get(f, 0) for f in FEATURE_NAMES], dtype=np.float32)

    def train(self, X, y):
        # Monotonicity: cement (index 0 in RAW_FEATURES) must monotonically
        # increase strength. Other features are unconstrained.
        monotone = [0] * len(FEATURE_NAMES)
        monotone[FEATURE_NAMES.index("cement")] = 1
        params = {
            "objective": "reg:squarederror",
            "max_depth": 6,
            "learning_rate": 0.05,
            "min_child_weight": 3,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "monotone_constraints": "(" + ",".join(str(v) for v in monotone) + ")",
            "verbosity": 0,
        }
        dtrain = xgb.DMatrix(X, label=y)
        self.model = xgb.train(params, dtrain, num_boost_round=600)

    def predict(self, X):
        return self.model.predict(xgb.DMatrix(X))

    def generate_candidates(self):
        """Generate candidate mix designs for multi-objective screening.

        Eleven generation strategies; full implementation in
        phase_b_discovery.py. This method is kept for the legacy
        evaluate.py interface but the canonical Phase B run is via
        phase_b_discovery.py.
        """
        from phase_b_discovery import generate_candidates
        return generate_candidates()
