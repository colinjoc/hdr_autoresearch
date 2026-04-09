"""
Fused Deposition Modelling (FDM) parameter-to-tensile-strength model.

THIS IS THE ONLY FILE THE AUTORESEARCH AGENT MODIFIES (per program.md).

Target task: predict ultimate tensile strength (UTS, megapascals) of an
American-Society-for-Testing-and-Materials (ASTM) D638 tensile bar
printed on an Ultimaker S5 FDM printer, given the printer's nine process
parameters.

Final winning configuration (Phase 2 experiment E08, Phase 2.5 sanity
check P25.0; see paper.md for derivation):

    - Features: raw 9 columns plus a five-feature physics-informed set:
         E_lin               linear energy density  T * v / h
         vol_flow            volumetric flow rate   v * h * w_line
         interlayer_time     time above glass transition (Sun model)
         infill_contact      load-bearing cross section proxy
         thermal_margin      T_nozzle - glass transition temperature

    - Model family: XGBoost (Extreme Gradient Boosting)
    - No monotonicity constraints (all four tried were reverted)
    - Default hyperparameters: depth=6, learning_rate=0.05,
      min_child_weight=3, subsample=0.8, colsample_bytree=0.8,
      n_estimators=300
    - 5-fold cross-validated mean absolute error (MAE) 4.292 MPa,
      R-squared 0.625 on the Kaggle 3D Printer Dataset (N=50).

The physics-informed five-feature set reduces MAE by roughly 0.15 MPa
(3.4 percent) over the nine-raw-feature XGBoost baseline. The
`cool_rate` feature was tried (as part of a six-feature set) and
reverted; its removal is the only reason the five-feature set beats the
full six-feature set.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import xgboost as xgb

RAW_FEATURES = [
    "layer_height",
    "wall_thickness",
    "infill_density",
    "infill_pattern",
    "nozzle_temperature",
    "bed_temperature",
    "print_speed",
    "material",
    "fan_speed",
]
DERIVED_FEATURES = [
    "E_lin",
    "vol_flow",
    "interlayer_time",
    "infill_contact",
    "thermal_margin",
]
FEATURE_NAMES = RAW_FEATURES + DERIVED_FEATURES

# Fixed Ultimaker S5 0.4 mm nozzle assumption: the Kaggle dataset does
# not include line width, so we use the slicer default of 0.48 mm
# (= 1.2 x 0.40). This constant is only used inside derived features.
LINE_WIDTH_MM = 0.48

# Glass transition temperatures (Tg, degrees Celsius) for the two
# materials in the dataset. Values from Sun et al. (2008) and the
# materials-science reviews cited in papers.csv.
TG_BY_MATERIAL = {
    0: 105.0,   # Acrylonitrile Butadiene Styrene (ABS)
    1: 60.0,    # Poly-Lactic Acid (PLA)
}

# Reference footprint for the interlayer-time proxy: a 50 mm x 50 mm
# layer (ASTM D638 tensile bar). The absolute value cancels out in any
# comparison between candidates.
REFERENCE_FOOTPRINT_MM2 = 50.0 * 50.0


def _add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the five physics-informed derived features.

    - E_lin (linear energy density, proxy for thermal input per unit
      road length) = nozzle_temperature * print_speed / layer_height.
      Borrowed from the Laser Powder Bed Fusion (LPBF) literature.
    - vol_flow (volumetric flow rate, cubic millimetres per second) =
      print_speed * layer_height * LINE_WIDTH_MM.
    - interlayer_time (seconds) = REFERENCE_FOOTPRINT_MM2 / (v * w_line).
      Proxy for how long the interface stays above the glass transition
      temperature, following Sun et al. (2008).
    - infill_contact (square millimetres) = (infill_density / 100) *
      REFERENCE_FOOTPRINT_MM2. Proxy for the load-bearing cross section.
    - thermal_margin (degrees Celsius) = nozzle_temperature - Tg.
      Measures how far the nozzle temperature sits above the polymer's
      glass transition temperature.
    """
    out = df.copy()
    layer_h = out["layer_height"].replace(0, np.nan)
    speed = out["print_speed"].replace(0, np.nan)

    out["E_lin"] = (out["nozzle_temperature"] * out["print_speed"] / layer_h).fillna(0.0)
    out["vol_flow"] = out["print_speed"] * out["layer_height"] * LINE_WIDTH_MM
    out["interlayer_time"] = (REFERENCE_FOOTPRINT_MM2 / (speed * LINE_WIDTH_MM)).fillna(0.0)
    out["infill_contact"] = out["infill_density"] / 100.0 * REFERENCE_FOOTPRINT_MM2
    tg = out["material"].map(TG_BY_MATERIAL).astype(float)
    out["thermal_margin"] = out["nozzle_temperature"].astype(float) - tg
    return out


class PrinterModel:
    """Mirrors the ConcreteModel interface from applications/concrete/."""

    def __init__(self) -> None:
        self.model: xgb.Booster | None = None
        self.feature_names = FEATURE_NAMES

    def featurize(self, df: pd.DataFrame):
        df = _add_features(df)
        X = df[FEATURE_NAMES].values.astype(np.float32)
        y = df["tension_strength"].values.astype(np.float32)
        return X, y

    def featurize_single(self, mix_dict: dict) -> np.ndarray:
        h = mix_dict.get("layer_height", 0.0) or 0.0
        v = mix_dict.get("print_speed", 0.0) or 0.0
        t = mix_dict.get("nozzle_temperature", 0.0)
        tg = TG_BY_MATERIAL.get(mix_dict.get("material", 1), 60.0)
        e_lin = t * v / h if h > 0 else 0.0
        vol_flow = v * h * LINE_WIDTH_MM
        interlayer_time = (REFERENCE_FOOTPRINT_MM2 / (v * LINE_WIDTH_MM)
                           if v > 0 else 0.0)
        infill_contact = mix_dict.get("infill_density", 0) / 100.0 * REFERENCE_FOOTPRINT_MM2
        thermal_margin = t - tg
        full = {
            **mix_dict,
            "E_lin": e_lin,
            "vol_flow": vol_flow,
            "interlayer_time": interlayer_time,
            "infill_contact": infill_contact,
            "thermal_margin": thermal_margin,
        }
        return np.array([full.get(f, 0) for f in FEATURE_NAMES], dtype=np.float32)

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        # The Phase 2 winner (E08) used the default XGBoost hyperparameters.
        # Monotonicity constraints were all reverted at Phase 2 and at
        # Phase 2.5 because they hurt the small-N cross-validation score.
        params = {
            "objective": "reg:squarederror",
            "max_depth": 6,
            "learning_rate": 0.05,
            "min_child_weight": 3,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "verbosity": 0,
        }
        dtrain = xgb.DMatrix(X, label=y)
        self.model = xgb.train(params, dtrain, num_boost_round=300)

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.model is not None, "Call train() before predict()."
        return self.model.predict(xgb.DMatrix(X))

    def generate_candidates(self):
        """Proxy to phase_b_discovery.generate_candidates(). See that
        module for the full multi-strategy candidate sweep."""
        from phase_b_discovery import generate_candidates
        return generate_candidates()
