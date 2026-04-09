"""
Welding parameter-to-quality prediction: model definition.

THIS IS THE ONLY FILE THE AUTORESEARCH AGENT MODIFIES DURING THE HDR LOOP.

Final winning configuration after Phase 0.5 baseline, Phase 1 tournament,
Phase 2 Hypothesis-Driven Research (HDR) loop, and Phase 2.5 composition
re-test (experiment P25.3; see `experiment_log.md` for the full trajectory):

  - Target: Heat-Affected Zone (HAZ) half-width in millimetres,
      trained on log(1 + HAZ) to stabilise variance on a skewed target
  - Raw features (6): voltage_v, current_a, travel_mm_s, thickness_mm,
      preheat_c, carbon_equiv
  - Physics-informed features (2): heat input HI = eta*V*I/v (kJ/mm);
      cooling time t_{8/5} from the Rosenthal closed-form solution
      (Easterling 1992 eqs. 3.4 / 3.7 for 3D thick-plate and 2D thin-plate)
  - XGBoost regressor, depth 6, learning rate 0.05, 300 boosting rounds,
      monotonicity constraints: HI → HAZ must be non-decreasing AND
      cooling time t_{8/5} → HAZ must be non-decreasing (both signs
      consistent with Rosenthal physics)
  - 5-fold cross-validated Mean Absolute Error (MAE) 1.19 mm,
      coefficient of determination R² 0.967 — recorded in `results.tsv`
      as row P25.3.
"""

from __future__ import annotations

import math
from typing import Dict, List

import numpy as np
import pandas as pd
import xgboost as xgb

RAW_FEATURES = [
    "voltage_v", "current_a", "travel_mm_s",
    "thickness_mm", "preheat_c", "carbon_equiv",
]
DERIVED_FEATURES = ["heat_input_kj_mm", "cooling_t85_s_est"]
FEATURE_NAMES = RAW_FEATURES + DERIVED_FEATURES

# Thermal properties used in the Rosenthal-derived features
K_STEEL = 45.0       # W/(m·K)
RHO_STEEL = 7850.0   # kg/m^3
CP_STEEL = 490.0     # J/(kg·K)
T_AMB = 25.0         # °C


def _add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the two physics-informed features added to the raw process
    parameters. Both rely only on columns the raw feature vector already
    contains, so they can be recomputed on novel candidates at discovery time.
    Vectorised over the whole DataFrame.
    """
    out = df.copy()
    if "efficiency" in out.columns:
        eta = out["efficiency"].astype(float)
    else:
        eta = pd.Series(0.8, index=out.index)

    # Heat input in kJ/mm: eta * V * I / (v * 1000) with v in mm/s.
    hi = eta * out["voltage_v"] * out["current_a"] / (out["travel_mm_s"] * 1000.0)
    out["heat_input_kj_mm"] = hi.values

    # Approximate cooling time t_{8/5}:
    #   thick plate (>=8 mm): t85 = q_per_m / (2*pi*k) * [1/(500-T0) - 1/(800-T0)]
    #   thin plate  (< 8 mm): t85 = q_per_m^2 / (4*pi*k*rho*cp*thk^2) *
    #                                 [1/(500-T0)^2 - 1/(800-T0)^2]
    q_per_mm = eta * out["voltage_v"].astype(float) * out["current_a"].astype(float) / out["travel_mm_s"].astype(float)
    q_per_m = (q_per_mm * 1000.0).values
    t0 = out["preheat_c"].astype(float).values + T_AMB
    a1 = 1.0 / np.maximum(500.0 - t0, 10.0)
    a2 = 1.0 / np.maximum(800.0 - t0, 10.0)
    thk = out["thickness_mm"].astype(float).values
    thk_m = thk / 1000.0

    t85_thick = (q_per_m / (2.0 * math.pi * K_STEEL)) * (a1 - a2)
    # Prevent divide-by-zero for degenerate cases
    safe_thk2 = np.maximum(thk_m ** 2, 1e-10)
    t85_thin = (q_per_m ** 2) / (4.0 * math.pi * K_STEEL * RHO_STEEL * CP_STEEL * safe_thk2) * (a1 ** 2 - a2 ** 2)
    t85 = np.where(thk >= 8.0, t85_thick, t85_thin)
    out["cooling_t85_s_est"] = t85
    return out


class WeldingModel:
    """XGBoost regressor predicting HAZ half-width (millimetres) from raw
    and Rosenthal-derived welding parameters.
    """

    def __init__(self):
        self.model = None
        self.feature_names = FEATURE_NAMES

    def featurize(self, df: pd.DataFrame):
        df_feat = _add_features(df)
        X = df_feat[FEATURE_NAMES].values.astype(np.float32)
        # Training target is HAZ half-width in mm, returned un-transformed.
        # The log1p transform is applied inside `train()` so that the
        # stored `y` matches the evaluate.py convention used for metrics.
        y = df_feat["haz_width_mm"].values.astype(np.float32)
        return X, y

    def featurize_single(self, params: Dict) -> np.ndarray:
        row = pd.DataFrame([params])
        if "efficiency" not in row.columns:
            row["efficiency"] = 0.8  # default to GMAW
        df_feat = _add_features(row)
        return df_feat[FEATURE_NAMES].values.astype(np.float32)[0]

    def train(self, X: np.ndarray, y: np.ndarray):
        monotone = [0] * len(FEATURE_NAMES)
        # Both heat input AND cooling time t_{8/5} should monotonically
        # increase HAZ width (Rosenthal physics).
        monotone[FEATURE_NAMES.index("heat_input_kj_mm")] = 1
        monotone[FEATURE_NAMES.index("cooling_t85_s_est")] = 1
        params = {
            "objective": "reg:squarederror",
            "max_depth": 6,
            "learning_rate": 0.05,
            "min_child_weight": 3,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "monotone_constraints": "(" + ",".join(str(v) for v in monotone) + ")",
            "verbosity": 0,
            "nthread": 1,
        }
        # Train on log(1 + HAZ) to stabilise variance.
        y_fit = np.log1p(y.astype(np.float32))
        dtrain = xgb.DMatrix(X, label=y_fit)
        self.model = xgb.train(params, dtrain, num_boost_round=300)

    def predict(self, X: np.ndarray) -> np.ndarray:
        log_pred = self.model.predict(xgb.DMatrix(X))
        return np.expm1(log_pred)

    def generate_candidates(self):
        """Thin wrapper so the legacy evaluate.py interface still works.
        The canonical Phase B run is via `phase_b_discovery.py`.
        """
        from phase_b_discovery import generate_candidates
        return generate_candidates()
