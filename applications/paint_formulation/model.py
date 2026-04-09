"""
Paint formulation: prediction + discovery.

THIS IS THE ONLY FILE THE AUTORESEARCH AGENT MODIFIES DURING THE HDR LOOP.

Dataset (real, not synthetic): Borgert et al., "High-Throughput and Explainable
Machine Learning for Lacquer Formulations", Zenodo DOI 10.5281/zenodo.13742098.
65 two-component polyurethane (2K PU) lacquer samples, four composition
variables plus film thickness, four performance targets.

Composition variables (all on normalised [0, 1] scale):
  crosslink       — relative crosslinker (OH/NCO) content
  cyc_nco_frac    — cycloaliphatic isocyanate (IPDI) fraction of total NCO
  matting_agent   — matting agent (silica) mass fraction
  pigment_paste   — pigment paste mass fraction
  thickness_um    — dry film thickness (microns; not composition but process)

Targets:
  scratch_hardness_N  — scratch hardness in newtons (higher = better)
  gloss_60            — 60 degree gloss in gloss units (higher = glossier)
  hiding_power_pct    — contrast ratio percent (higher = better hiding)
  cupping_mm          — Erichsen cupping depth in millimetres (higher = more
                        flexible before cracking)

The model is a per-target XGBoost regressor. The HDR loop writes the winning
configuration here after Phase 2.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
import xgboost as xgb

# ---------------------------------------------------------------------------
# Column definitions
# ---------------------------------------------------------------------------

# Four composition variables + film thickness. The original paper uses all
# five as inputs. Film thickness is treated as a process parameter the user
# can independently specify during application.
RAW_FEATURES: List[str] = [
    "crosslink",
    "cyc_nco_frac",
    "matting_agent",
    "pigment_paste",
    "thickness_um",
]

TARGET_COLS: List[str] = [
    "scratch_hardness_N",
    "gloss_60",
    "hiding_power_pct",
    "cupping_mm",
]


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def _safe_div(a, b):
    return a / b.replace(0, np.nan)


def add_features(df: pd.DataFrame, features: Sequence[str]) -> pd.DataFrame:
    """Compute the named derived features on a copy of df.

    All derived features used anywhere in the HDR loop live here so that both
    the training harness and `featurize_single` (used during Phase B discovery)
    produce identical columns from identical inputs.
    """
    out = df.copy()
    # --- composition-level features
    if "binder_frac" in features:
        # binder_frac = 1 - (matting_agent + pigment_paste); crosslink is
        # expressed relative to binder so it does not enter the mass balance
        # on the normalised scale.
        out["binder_frac"] = 1.0 - out["matting_agent"] - out["pigment_paste"]
    if "pvc_proxy" in features:
        # Pigment Volume Concentration proxy (dimensionless). The normalised
        # Pigmentpaste column is proportional to pigment volume; the matting
        # agent (silica) also behaves as an extender. The remaining space is
        # binder. This is only a proxy because the Zenodo dataset does not
        # expose absolute volumes.
        solids = out["pigment_paste"] + out["matting_agent"]
        binder = 1.0 - solids
        denom = (solids + binder).replace(0, np.nan)
        out["pvc_proxy"] = (solids / denom).fillna(0.0)
    if "pvc_cpvc_dist" in features:
        # Distance from assumed Critical Pigment Volume Concentration 0.45
        # (midpoint of the typical 30-60% CPVC range for silica-filled
        # polyurethane lacquers).
        solids = out["pigment_paste"] + out["matting_agent"]
        denom = (solids + (1.0 - solids)).replace(0, np.nan)
        out["pvc_cpvc_dist"] = ((solids / denom).fillna(0.0) - 0.45)
    if "binder_pigment_ratio" in features:
        binder = 1.0 - out["matting_agent"] - out["pigment_paste"]
        solids = (out["pigment_paste"] + out["matting_agent"]).replace(0, np.nan)
        out["binder_pigment_ratio"] = (binder / solids).fillna(10.0)
    if "matting_pigment_ratio" in features:
        p = out["pigment_paste"].replace(0, np.nan)
        out["matting_pigment_ratio"] = (out["matting_agent"] / p).fillna(0.0)
    # --- isocyanate chemistry features
    if "hdi_frac" in features:
        # HDI fraction of total isocyanate (1 - cyc_nco_frac).
        out["hdi_frac"] = 1.0 - out["cyc_nco_frac"]
    if "crosslink_x_cyc" in features:
        out["crosslink_x_cyc"] = out["crosslink"] * out["cyc_nco_frac"]
    if "crosslink_sq" in features:
        out["crosslink_sq"] = out["crosslink"] ** 2
    if "matting_agent_sq" in features:
        out["matting_agent_sq"] = out["matting_agent"] ** 2
    if "pigment_paste_sq" in features:
        out["pigment_paste_sq"] = out["pigment_paste"] ** 2
    # --- thickness features
    if "log_thickness" in features:
        out["log_thickness"] = np.log1p(out["thickness_um"])
    if "inv_thickness" in features:
        out["inv_thickness"] = 1.0 / (out["thickness_um"] + 1.0)
    if "thickness_sq" in features:
        out["thickness_sq"] = out["thickness_um"] ** 2
    if "thickness_x_matting" in features:
        out["thickness_x_matting"] = out["thickness_um"] * out["matting_agent"]
    if "thickness_x_pigment" in features:
        out["thickness_x_pigment"] = out["thickness_um"] * out["pigment_paste"]
    # --- Aitchison log-ratio (compositional) features
    # Build three log-ratios from the four composition columns with binder as
    # reference. This is the standard simplex-aware featurisation. We clip
    # each composition column to >=eps before logging so a slightly negative
    # entry from experimental rounding does not produce NaN.
    eps = 1e-3
    if "lr_crosslink" in features:
        binder = (1.0 - out["matting_agent"] - out["pigment_paste"]).clip(lower=eps)
        out["lr_crosslink"] = np.log(out["crosslink"].clip(lower=eps) / binder)
    if "lr_cyc" in features:
        binder = (1.0 - out["matting_agent"] - out["pigment_paste"]).clip(lower=eps)
        out["lr_cyc"] = np.log(out["cyc_nco_frac"].clip(lower=eps) / binder)
    if "lr_matting" in features:
        binder = (1.0 - out["matting_agent"] - out["pigment_paste"]).clip(lower=eps)
        out["lr_matting"] = np.log(out["matting_agent"].clip(lower=eps) / binder)
    if "lr_pigment" in features:
        binder = (1.0 - out["matting_agent"] - out["pigment_paste"]).clip(lower=eps)
        out["lr_pigment"] = np.log(out["pigment_paste"].clip(lower=eps) / binder)
    # --- interaction / cross features
    if "crosslink_x_matting" in features:
        out["crosslink_x_matting"] = out["crosslink"] * out["matting_agent"]
    if "cyc_x_matting" in features:
        out["cyc_x_matting"] = out["cyc_nco_frac"] * out["matting_agent"]
    if "pigment_x_matting" in features:
        out["pigment_x_matting"] = out["pigment_paste"] * out["matting_agent"]
    return out


def featurize(
    df: pd.DataFrame,
    target: str,
    extra_features: Sequence[str] = (),
) -> Tuple[np.ndarray, np.ndarray]:
    """Return (X, y) for the specified target with the given extra features."""
    df_f = add_features(df, extra_features)
    feature_names = list(RAW_FEATURES) + list(extra_features)
    X = df_f[feature_names].values.astype(np.float32)
    y = df_f[target].values.astype(np.float32)
    return X, y


# ---------------------------------------------------------------------------
# Model class (modified by the HDR loop during Phase 2)
# ---------------------------------------------------------------------------

# Final winning configuration after Phase 2 + Phase 2.5 HDR loop.
# Per-target dispatch: Ridge for scratch hardness, XGBoost depth-7 for gloss,
# ExtraTrees for hiding power and cupping test. See paper.md Section 3
# "Detailed Solution" for the physical motivation for each choice.
WINNING_EXTRA_FEATURES_PER_TARGET: Dict[str, List[str]] = {
    "scratch_hardness_N": ["binder_pigment_ratio"],
    "gloss_60":           ["log_thickness", "thickness_x_matting"],
    "hiding_power_pct":   ["thickness_x_pigment"],
    "cupping_mm":         ["cyc_x_matting", "pvc_proxy"],
}

# Legacy alias for any downstream code expecting a single list
WINNING_EXTRA_FEATURES: List[str] = []

WINNING_MODEL_PARAMS: Dict[str, Dict] = {
    # scratch hardness: Ridge regression wins the Phase 1 tournament on
    # this small-N target (65 samples). Linear baseline is competitive
    # because matting agent + crosslink + pigment_paste contribute
    # approximately linearly to scratch hardness on this dataset.
    "scratch_hardness_N": {
        "model_family": "ridge",
        "sklearn_kwargs": {"alpha": 1.0},
        "n_estimators": 300,  # unused by ridge but kept for config uniformity
    },
    # gloss: XGBoost with deeper trees (depth 7) plus two physics-informed
    # thickness features. Log thickness captures the negative-power-law
    # dependence of specular reflectance on surface roughness; the
    # thickness-x-matting interaction captures the protrusion of matting
    # silica particles at thick films.
    "gloss_60": {
        "model_family": "xgboost",
        "xgb_params": {
            "objective": "reg:squarederror",
            "max_depth": 7,
            "learning_rate": 0.05,
            "min_child_weight": 2,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "verbosity": 0,
        },
        "n_estimators": 300,
    },
    # hiding power: ExtraTrees with max_features=0.5 plus the Kubelka-Munk-
    # inspired thickness x pigment_paste product term.
    "hiding_power_pct": {
        "model_family": "extratrees",
        "sklearn_kwargs": {"max_features": 0.5},
        "n_estimators": 300,
    },
    # cupping: ExtraTrees with cyc_x_matting (IPDI stiffness contribution)
    # and the PVC proxy.
    "cupping_mm": {
        "model_family": "extratrees",
        "n_estimators": 300,
    },
}


class PaintFormulationModel:
    """Single-target predictor.

    The class wraps an XGBoost, LightGBM, ExtraTrees, or Ridge model chosen
    by the HDR loop and exposes `featurize`, `train`, `predict`,
    `featurize_single`, and `generate_candidates` — the same surface used
    by the concrete application so evaluate.py can treat them the same way.
    """

    def __init__(
        self,
        target: str = "scratch_hardness_N",
        extra_features: Sequence[str] = None,
        config: Dict = None,
    ):
        if target not in TARGET_COLS:
            raise ValueError(f"unknown target: {target}")
        self.target = target
        if extra_features is not None:
            self.extra_features = list(extra_features)
        else:
            self.extra_features = list(WINNING_EXTRA_FEATURES_PER_TARGET.get(target, []))
        self.config = config if config is not None else dict(WINNING_MODEL_PARAMS[target])
        self.feature_names = list(RAW_FEATURES) + list(self.extra_features)
        self.model = None
        self._log_target = self.config.get("log_target", False)
        self._monotone = self.config.get("monotone_constraints")

    # -- feature interface used by evaluate.py -------------------------------

    def featurize(self, df: pd.DataFrame):
        return featurize(df, self.target, self.extra_features)

    def featurize_single(self, mix_dict: Dict) -> np.ndarray:
        row_df = pd.DataFrame([mix_dict])
        for col in RAW_FEATURES:
            if col not in row_df.columns:
                row_df[col] = 0.0
        df_f = add_features(row_df, self.extra_features)
        return df_f[self.feature_names].values.astype(np.float32)[0]

    # -- training / prediction ----------------------------------------------

    def train(self, X: np.ndarray, y: np.ndarray):
        y_fit = np.log1p(y) if self._log_target else y
        family = self.config.get("model_family", "xgboost")
        n_estimators = int(self.config.get("n_estimators", 300))
        if family == "xgboost":
            params = dict(self.config.get("xgb_params", {}))
            params.setdefault("objective", "reg:squarederror")
            params.setdefault("verbosity", 0)
            if self._monotone:
                vec = [self._monotone.get(f, 0) for f in self.feature_names]
                params["monotone_constraints"] = "(" + ",".join(str(v) for v in vec) + ")"
            dtrain = xgb.DMatrix(X, label=y_fit)
            self.model = xgb.train(params, dtrain, num_boost_round=n_estimators)
        elif family == "lightgbm":
            import lightgbm as lgb
            params = {
                "objective": "regression",
                "metric": "mae",
                "num_leaves": 31,
                "learning_rate": 0.05,
                "feature_fraction": 0.8,
                "bagging_fraction": 0.8,
                "bagging_freq": 5,
                "min_data_in_leaf": 3,
                "verbosity": -1,
            }
            params.update(self.config.get("lgb_params", {}))
            dtrain = lgb.Dataset(X, label=y_fit)
            self.model = lgb.train(params, dtrain, num_boost_round=n_estimators)
        elif family == "extratrees":
            from sklearn.ensemble import ExtraTreesRegressor
            kwargs = {"n_estimators": n_estimators, "random_state": 42, "n_jobs": -1}
            kwargs.update(self.config.get("sklearn_kwargs", {}))
            self.model = ExtraTreesRegressor(**kwargs)
            self.model.fit(X, y_fit)
        elif family == "randomforest":
            from sklearn.ensemble import RandomForestRegressor
            kwargs = {"n_estimators": n_estimators, "random_state": 42, "n_jobs": -1}
            kwargs.update(self.config.get("sklearn_kwargs", {}))
            self.model = RandomForestRegressor(**kwargs)
            self.model.fit(X, y_fit)
        elif family == "ridge":
            from sklearn.linear_model import Ridge
            from sklearn.preprocessing import StandardScaler
            from sklearn.pipeline import Pipeline
            kwargs = {"alpha": 1.0}
            kwargs.update(self.config.get("sklearn_kwargs", {}))
            self.model = Pipeline([
                ("scaler", StandardScaler()),
                ("ridge", Ridge(**kwargs)),
            ])
            self.model.fit(X, y_fit)
        elif family == "gp":
            from sklearn.gaussian_process import GaussianProcessRegressor
            from sklearn.gaussian_process.kernels import RBF, WhiteKernel, DotProduct, Matern
            from sklearn.preprocessing import StandardScaler
            from sklearn.pipeline import Pipeline
            kernel_name = self.config.get("gp_kernel", "matern")
            if kernel_name == "rbf":
                kernel = RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e3)) + WhiteKernel(1e-3)
            elif kernel_name == "matern":
                kernel = Matern(length_scale=1.0, length_scale_bounds=(1e-2, 1e3), nu=1.5) + WhiteKernel(1e-3)
            elif kernel_name == "rbf_dot":
                kernel = RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e3)) + DotProduct() + WhiteKernel(1e-3)
            else:
                kernel = RBF(length_scale=1.0)
            self.model = Pipeline([
                ("scaler", StandardScaler()),
                ("gp", GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3, normalize_y=True, random_state=42)),
            ])
            self.model.fit(X, y_fit)
        else:
            raise ValueError(f"unknown model family: {family}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("model not trained")
        family = self.config.get("model_family", "xgboost")
        if family == "xgboost":
            y_pred = self.model.predict(xgb.DMatrix(X))
        elif family == "lightgbm":
            y_pred = self.model.predict(X)
        else:
            y_pred = self.model.predict(X)
        if self._log_target:
            y_pred = np.expm1(y_pred)
        return np.asarray(y_pred, dtype=np.float32)

    # -- discovery interface used by phase_b_discovery.py --------------------

    def generate_candidates(self):
        from phase_b_discovery import generate_candidates
        return generate_candidates()
