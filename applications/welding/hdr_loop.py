"""
hdr_loop.py — Phase 0.5 baseline + Phase 1 tournament + Phase 2 HDR loop
for the welding parameter-quality HDR project.

Runs every experiment programmatically: each one defines a different
WeldingModel variant (different features, hyperparameters, model family,
or constraint strategy), evaluates it via a 5-fold cross-validation
harness identical to `evaluate.py`, records the result in `results.tsv`,
and decides KEEP or REVERT against the previous best.

Phase 0.5 establishes the raw-features-only baseline (E00).

Phase 1 runs a 4-way tournament between fundamentally different model
families: XGBoost (the default), LightGBM, ExtraTrees, and Ridge linear
regression. The linear baseline matters because the textbook scaling laws
(heat input, Rosenthal t_{8/5}) are essentially log-linear in the primary
parameters.

Phase 2 runs ~55 single-change Hypothesis-Driven Research (HDR) experiments,
each grounded in domain physics. Feature hypotheses come from
`research_queue.md`:
    H1: heat input → HAZ width
    H2: cooling time t_{8/5} → hardness (and through hardness → HAZ)
    H3: carbon equivalent → generalisation
    H4: voltage/current ratio → transfer mode proxy
    H6: physics-informed feature augmentation
    H9: Gaussian process uncertainty
    H20: cross-process transfer (GMAW → GTAW)

Every row in `results.tsv` is reproducible by rebuilding the corresponding
ExperimentConfig and calling `fit_predict`.
"""
from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_TSV = PROJECT_ROOT / "results.tsv"
DATA_PATH = PROJECT_ROOT / "data" / "welding.csv"
N_FOLDS = 5
RANDOM_SEED = 42

# Thermal constants for Rosenthal-derived features
K_STEEL = 45.0
RHO_STEEL = 7850.0
CP_STEEL = 490.0
T_AMB = 25.0

RAW_FEATURES = [
    "voltage_v", "current_a", "travel_mm_s",
    "thickness_mm", "preheat_c", "carbon_equiv",
]
STEEL_PROCESSES = ("GMAW", "GTAW")


# ---------------------------------------------------------------------------
# Feature engineering — vectorised Rosenthal-based derived columns
# ---------------------------------------------------------------------------

def add_features(df: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    """Return a copy of `df` with each feature in `features` added."""
    out = df.copy()
    eta = out["efficiency"].astype(float)
    v = out["voltage_v"].astype(float)
    i = out["current_a"].astype(float)
    s = out["travel_mm_s"].astype(float)
    thk = out["thickness_mm"].astype(float)
    pre = out["preheat_c"].astype(float)
    ce = out["carbon_equiv"].astype(float)
    q_watts = eta * v * i
    q_per_mm = q_watts / s              # J/mm = kW·s/mm; note 1 kJ/mm = 1000 J/mm
    q_per_m = q_per_mm * 1000.0
    hi_kj_mm = q_per_mm / 1000.0        # HI in kJ/mm (the textbook definition)
    t0 = pre + T_AMB

    for f in features:
        if f == "heat_input_kj_mm":
            out["heat_input_kj_mm"] = hi_kj_mm
        elif f == "log_heat_input":
            out["log_heat_input"] = np.log1p(hi_kj_mm)
        elif f == "heat_input_sq":
            out["heat_input_sq"] = hi_kj_mm ** 2
        elif f == "cooling_t85_s_est":
            a1 = 1.0 / np.maximum(500.0 - t0, 10.0)
            a2 = 1.0 / np.maximum(800.0 - t0, 10.0)
            thk_m = thk / 1000.0
            t85_thick = (q_per_m / (2.0 * math.pi * K_STEEL)) * (a1 - a2)
            safe_thk2 = np.maximum(thk_m ** 2, 1e-10)
            t85_thin = (q_per_m ** 2) / (4.0 * math.pi * K_STEEL * RHO_STEEL * CP_STEEL * safe_thk2) * (a1 ** 2 - a2 ** 2)
            out["cooling_t85_s_est"] = np.where(thk >= 8.0, t85_thick, t85_thin)
        elif f == "log_t85":
            a1 = 1.0 / np.maximum(500.0 - t0, 10.0)
            a2 = 1.0 / np.maximum(800.0 - t0, 10.0)
            thk_m = thk / 1000.0
            t85_thick = (q_per_m / (2.0 * math.pi * K_STEEL)) * (a1 - a2)
            safe_thk2 = np.maximum(thk_m ** 2, 1e-10)
            t85_thin = (q_per_m ** 2) / (4.0 * math.pi * K_STEEL * RHO_STEEL * CP_STEEL * safe_thk2) * (a1 ** 2 - a2 ** 2)
            t85 = np.where(thk >= 8.0, t85_thick, t85_thin)
            out["log_t85"] = np.log1p(np.maximum(t85, 0.01))
        elif f == "delta_t":
            out["delta_t"] = np.maximum(800.0 - t0, 10.0)
        elif f == "power_w":
            out["power_w"] = q_watts
        elif f == "v_over_i":
            out["v_over_i"] = v / np.maximum(i, 1.0)
        elif f == "i_over_v":
            out["i_over_v"] = i / np.maximum(v, 1.0)
        elif f == "heat_flux_w_mm2":
            out["heat_flux_w_mm2"] = q_watts / np.maximum(thk ** 2, 1.0)
        elif f == "arc_length_proxy":
            out["arc_length_proxy"] = (v - 14.0) / np.maximum(i * 0.04, 1.0)
        elif f == "linear_energy":
            out["linear_energy"] = q_per_m
        elif f == "log_travel":
            out["log_travel"] = np.log1p(s)
        elif f == "log_current":
            out["log_current"] = np.log1p(i)
        elif f == "log_voltage":
            out["log_voltage"] = np.log1p(v)
        elif f == "inv_travel":
            out["inv_travel"] = 1.0 / np.maximum(s, 0.01)
        elif f == "inv_thickness":
            out["inv_thickness"] = 1.0 / np.maximum(thk, 0.5)
        elif f == "hi_over_thk":
            out["hi_over_thk"] = hi_kj_mm / np.maximum(thk, 0.5)
        elif f == "hi_over_sqrt_thk":
            out["hi_over_sqrt_thk"] = hi_kj_mm / np.sqrt(np.maximum(thk, 0.5))
        elif f == "ce_ratio":
            out["ce_ratio"] = ce
        elif f == "ce_times_hi":
            out["ce_times_hi"] = ce * hi_kj_mm
        elif f == "preheat_bonus":
            out["preheat_bonus"] = pre
        elif f == "hi_preheat_interaction":
            out["hi_preheat_interaction"] = hi_kj_mm * (pre / 100.0 + 1.0)
        elif f == "effective_heat_density":
            # HI × k thermal conductivity (constant) collapses to HI*45, a
            # scaling that is supposed to be universal across materials if
            # textbook scalings hold.
            out["effective_heat_density"] = hi_kj_mm * K_STEEL
        elif f == "sqrt_hi":
            out["sqrt_hi"] = np.sqrt(np.maximum(hi_kj_mm, 1e-6))
        elif f == "thickness_sq":
            out["thickness_sq"] = thk ** 2
        elif f == "current_sq":
            out["current_sq"] = i ** 2
        elif f == "cube_root_hi":
            out["cube_root_hi"] = np.cbrt(np.maximum(hi_kj_mm, 1e-6))
        else:
            raise ValueError(f"unknown feature key: {f}")
    return out


# ---------------------------------------------------------------------------
# Experiment configuration
# ---------------------------------------------------------------------------

@dataclass
class ExperimentConfig:
    exp_id: str
    description: str
    prior: float
    mechanism: str
    model_family: str = "xgboost"
    extra_features: List[str] = field(default_factory=list)
    xgb_params: Dict[str, Any] = field(default_factory=dict)
    lgb_params: Dict[str, Any] = field(default_factory=dict)
    sklearn_kwargs: Dict[str, Any] = field(default_factory=dict)
    monotone_constraints: Optional[Dict[str, int]] = None
    log_target: bool = False
    n_estimators: int = 300
    target: str = "haz_width_mm"
    standardise: bool = False   # affects Ridge only


XGB_DEFAULT = {
    "objective": "reg:squarederror",
    "max_depth": 6,
    "learning_rate": 0.05,
    "min_child_weight": 3,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "verbosity": 0,
    "nthread": 1,
}

LGB_DEFAULT = {
    "objective": "regression",
    "metric": "mae",
    "num_leaves": 31,
    "learning_rate": 0.05,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "min_data_in_leaf": 5,
    "verbosity": -1,
    "num_threads": 1,
}


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    return df[df["process"].isin(STEEL_PROCESSES)].reset_index(drop=True)


def fit_predict(cfg: ExperimentConfig, df: pd.DataFrame) -> Dict[str, float]:
    """5-fold cross-validation with the given configuration."""
    df_feat = add_features(df, cfg.extra_features)
    feature_names = RAW_FEATURES + list(cfg.extra_features)
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    all_y_true, all_y_pred = [], []

    for train_idx, test_idx in kf.split(df_feat):
        train = df_feat.iloc[train_idx]
        test = df_feat.iloc[test_idx]
        X_tr = train[feature_names].values.astype(np.float32)
        X_te = test[feature_names].values.astype(np.float32)
        y_tr = train[cfg.target].values.astype(np.float32)
        y_te = test[cfg.target].values.astype(np.float32)
        y_tr_fit = np.log1p(y_tr) if cfg.log_target else y_tr

        if cfg.standardise and cfg.model_family == "ridge":
            scaler = StandardScaler()
            X_tr = scaler.fit_transform(X_tr)
            X_te = scaler.transform(X_te)

        if cfg.model_family == "xgboost":
            params = dict(XGB_DEFAULT)
            params.update(cfg.xgb_params)
            if cfg.monotone_constraints:
                vec = [cfg.monotone_constraints.get(f, 0) for f in feature_names]
                params["monotone_constraints"] = "(" + ",".join(str(v) for v in vec) + ")"
            dtr = xgb.DMatrix(X_tr, label=y_tr_fit)
            dte = xgb.DMatrix(X_te)
            booster = xgb.train(params, dtr, num_boost_round=cfg.n_estimators)
            y_pred = booster.predict(dte)
        elif cfg.model_family == "lightgbm":
            params = dict(LGB_DEFAULT)
            params.update(cfg.lgb_params)
            dtr = lgb.Dataset(X_tr, label=y_tr_fit)
            booster = lgb.train(params, dtr, num_boost_round=cfg.n_estimators)
            y_pred = booster.predict(X_te)
        elif cfg.model_family == "extratrees":
            kwargs = {"n_estimators": cfg.n_estimators, "random_state": RANDOM_SEED, "n_jobs": 1}
            kwargs.update(cfg.sklearn_kwargs)
            mdl = ExtraTreesRegressor(**kwargs)
            mdl.fit(X_tr, y_tr_fit)
            y_pred = mdl.predict(X_te)
        elif cfg.model_family == "ridge":
            kwargs = {"alpha": 1.0}
            kwargs.update(cfg.sklearn_kwargs)
            mdl = Ridge(**kwargs)
            mdl.fit(X_tr, y_tr_fit)
            y_pred = mdl.predict(X_te)
        else:
            raise ValueError(f"unknown family: {cfg.model_family}")

        if cfg.log_target:
            y_pred = np.expm1(y_pred)
        all_y_true.extend(y_te.tolist())
        all_y_pred.extend(y_pred.tolist())

    y_true = np.array(all_y_true)
    y_pred = np.array(all_y_pred)
    return {
        "mae":  float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2":   float(r2_score(y_true, y_pred)),
    }


# ---------------------------------------------------------------------------
# Phase 1 tournament and Phase 2 HDR loop
# ---------------------------------------------------------------------------

def append_row(exp_id, description, mae, rmse, r2, n_pareto, best_eff, prior, decision, notes):
    with RESULTS_TSV.open("a") as fh:
        fh.write(
            f"{exp_id}\t{description}\t{mae:.4f}\t{rmse:.4f}\t{r2:.4f}\t"
            f"{n_pareto}\t{best_eff}\t{prior:.2f}\t{decision}\t{notes}\n"
        )


def phase_2_experiments(winner_family: str) -> List[ExperimentConfig]:
    """Ordered Phase 2 experiment queue. Each hypothesis changes exactly one
    thing relative to E00. Grouped by class:
      1. single-feature physics additions (H1, H2)
      2. compound physics feature sets
      3. ratios, logs, interactions
      4. process-level transforms (log target, monotonicity)
      5. hyperparameter tightening
      6. cross-process transfer hypotheses (GMAW→GTAW, see hdr_phase25.py)
    """
    xs: List[ExperimentConfig] = []
    f = winner_family

    # 1. Single physics features
    xs += [
        ExperimentConfig("E01", "Add heat input (HI) as single derived feature",
                         prior=0.85, mechanism="H1: Rosenthal scaling says HAZ ∝ HI",
                         model_family=f, extra_features=["heat_input_kj_mm"]),
        ExperimentConfig("E02", "Add log(heat input)",
                         prior=0.55, mechanism="Thin-plate regime has HAZ ∝ log(HI)",
                         model_family=f, extra_features=["log_heat_input"]),
        ExperimentConfig("E03", "Add heat_input^2 (quadratic regime)",
                         prior=0.30, mechanism="Thick-plate HAZ width² ∝ HI",
                         model_family=f, extra_features=["heat_input_sq"]),
        ExperimentConfig("E04", "Add sqrt(heat input)",
                         prior=0.45, mechanism="3D Rosenthal gives HAZ ∝ sqrt(HI)",
                         model_family=f, extra_features=["sqrt_hi"]),
        ExperimentConfig("E05", "Add cube-root heat input",
                         prior=0.20, mechanism="Bulk scaling of a 3D point source",
                         model_family=f, extra_features=["cube_root_hi"]),
    ]
    # 2. Rosenthal cooling time features
    xs += [
        ExperimentConfig("E06", "Add Rosenthal cooling time t_{8/5}",
                         prior=0.55, mechanism="H2: t_{8/5} drives transformation phases",
                         model_family=f, extra_features=["cooling_t85_s_est"]),
        ExperimentConfig("E07", "Add log(t_{8/5}) — wide dynamic range",
                         prior=0.50, mechanism="t_{8/5} spans 3 orders of magnitude",
                         model_family=f, extra_features=["log_t85"]),
        ExperimentConfig("E08", "Add both HI and t_{8/5}",
                         prior=0.75, mechanism="Two distinct physics regimes",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"]),
        ExperimentConfig("E09", "Add HI + t_{8/5} + log variants",
                         prior=0.60, mechanism="Log features linearise the power law",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "log_heat_input", "log_t85"]),
    ]
    # 3. Raw power and flux features
    xs += [
        ExperimentConfig("E10", "Add raw arc power (eta*V*I)",
                         prior=0.40, mechanism="Power is the numerator of HI",
                         model_family=f, extra_features=["power_w"]),
        ExperimentConfig("E11", "Add V/I ratio (arc length proxy)",
                         prior=0.40, mechanism="H4: V/I → transfer mode",
                         model_family=f, extra_features=["v_over_i"]),
        ExperimentConfig("E12", "Add I/V ratio",
                         prior=0.25, mechanism="Reciprocal of E11",
                         model_family=f, extra_features=["i_over_v"]),
        ExperimentConfig("E13", "Add heat flux per unit area (W/mm²)",
                         prior=0.30, mechanism="Surface heat flux bounds weld pool",
                         model_family=f, extra_features=["heat_flux_w_mm2"]),
        ExperimentConfig("E14", "Add linear energy (J/m)",
                         prior=0.30, mechanism="Linear energy in SI units",
                         model_family=f, extra_features=["linear_energy"]),
    ]
    # 4. Log transforms of raw inputs
    xs += [
        ExperimentConfig("E15", "Add log(travel_mm_s)",
                         prior=0.30, mechanism="Travel speed is the denominator of HI",
                         model_family=f, extra_features=["log_travel"]),
        ExperimentConfig("E16", "Add log(current)",
                         prior=0.30, mechanism="Current dominates by ~2.5×",
                         model_family=f, extra_features=["log_current"]),
        ExperimentConfig("E17", "Add log(voltage)",
                         prior=0.25, mechanism="V has weaker effect than I",
                         model_family=f, extra_features=["log_voltage"]),
        ExperimentConfig("E18", "Add 1/travel speed",
                         prior=0.30, mechanism="Inverse makes HI linear in it",
                         model_family=f, extra_features=["inv_travel"]),
        ExperimentConfig("E19", "Add 1/thickness",
                         prior=0.25, mechanism="Thin plate: cooling ∝ 1/thk²",
                         model_family=f, extra_features=["inv_thickness"]),
    ]
    # 5. Physics-informed composite / interaction features
    xs += [
        ExperimentConfig("E20", "Add HI / thickness",
                         prior=0.55, mechanism="Energy per unit thickness",
                         model_family=f, extra_features=["hi_over_thk"]),
        ExperimentConfig("E21", "Add HI / sqrt(thickness)",
                         prior=0.50, mechanism="2D/3D regime boundary scaling",
                         model_family=f, extra_features=["hi_over_sqrt_thk"]),
        ExperimentConfig("E22", "Add CE × HI interaction",
                         prior=0.30, mechanism="H3: CE modulates the HI effect",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "ce_times_hi"]),
        ExperimentConfig("E23", "Add effective heat density (HI × k_steel)",
                         prior=0.25, mechanism="Textbook universal scaling",
                         model_family=f, extra_features=["effective_heat_density"]),
        ExperimentConfig("E24", "Add HI × preheat interaction",
                         prior=0.30, mechanism="Preheat widens HAZ at same HI",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "hi_preheat_interaction"]),
        ExperimentConfig("E25", "Add Δ_T=800-T0 (cooling driver)",
                         prior=0.30, mechanism="Preheat raises T0 → shallower gradient",
                         model_family=f, extra_features=["delta_t"]),
    ]
    # 6. Model hyperparameters
    xs += [
        ExperimentConfig("E26", "Lower learning rate to 0.03, n=500",
                         prior=0.30, mechanism="Fine-grained boosting",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         xgb_params={"learning_rate": 0.03}, n_estimators=500),
        ExperimentConfig("E27", "Increase max_depth to 8",
                         prior=0.25, mechanism="Deeper trees, interaction capture",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         xgb_params={"max_depth": 8}),
        ExperimentConfig("E28", "Decrease max_depth to 4 (regularise)",
                         prior=0.30, mechanism="Shallower for N~560",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         xgb_params={"max_depth": 4}),
        ExperimentConfig("E29", "Train on log(HAZ width)",
                         prior=0.50, mechanism="Stabilise variance on skewed target",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         log_target=True),
        ExperimentConfig("E30", "Subsample 0.6 (heavier bagging)",
                         prior=0.25, mechanism="Reduce overfit on 560 samples",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         xgb_params={"subsample": 0.6}),
        ExperimentConfig("E31", "min_child_weight = 5 (stricter leaves)",
                         prior=0.25, mechanism="Prevent single-sample leaves",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         xgb_params={"min_child_weight": 5}),
        ExperimentConfig("E32", "n_estimators 300 → 600",
                         prior=0.40, mechanism="Match concrete project gain",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         n_estimators=600),
    ]
    # 7. Monotonicity constraints (physics priors hard-wired)
    xs += [
        ExperimentConfig("E33", "Monotone: HI↑ → HAZ↑",
                         prior=0.55, mechanism="Rosenthal says HAZ↑ with HI",
                         model_family="xgboost",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         monotone_constraints={"heat_input_kj_mm": 1}),
        ExperimentConfig("E34", "Monotone: HI↑, t85↑ → HAZ↑",
                         prior=0.55, mechanism="Both HI and cooling time widen HAZ",
                         model_family="xgboost",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         monotone_constraints={"heat_input_kj_mm": 1, "cooling_t85_s_est": 1}),
        ExperimentConfig("E35", "Monotone: current↑ → HAZ↑, travel↑ → HAZ↓",
                         prior=0.50, mechanism="Heat-input signs without computing HI",
                         model_family="xgboost",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         monotone_constraints={"current_a": 1, "travel_mm_s": -1}),
        ExperimentConfig("E36", "Monotone: I↑ → HAZ↑, v↑ → HAZ↓, thk↑ → HAZ↓",
                         prior=0.45, mechanism="Three physics priors at once",
                         model_family="xgboost",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         monotone_constraints={"current_a": 1, "travel_mm_s": -1, "thickness_mm": -1}),
    ]
    # 8. Full physics feature bundles
    xs += [
        ExperimentConfig("E37", "Full physics bundle (HI, t85, hi_over_thk, ce_times_hi)",
                         prior=0.55, mechanism="Combine all physically motivated features",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "hi_over_thk", "ce_times_hi"]),
        ExperimentConfig("E38", "Full bundle + log_travel + v_over_i",
                         prior=0.45, mechanism="Add transfer-mode proxy",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "hi_over_thk", "ce_times_hi",
                                          "log_travel", "v_over_i"]),
        ExperimentConfig("E39", "Physics bundle + all log variants",
                         prior=0.35, mechanism="Log-linearise everything",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "log_heat_input", "log_t85", "log_travel",
                                          "log_current", "log_voltage"]),
        ExperimentConfig("E40", "Physics bundle + sqrt/cube-root HI",
                         prior=0.25, mechanism="Try both Rosenthal regimes",
                         model_family=f,
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "sqrt_hi", "cube_root_hi"]),
    ]
    # 9. Regularised linear attempts (does linear physics do better w/ features?)
    xs += [
        ExperimentConfig("E41", "Ridge on physics bundle (linear HDR baseline)",
                         prior=0.35, mechanism="Textbook scalings are log-linear",
                         model_family="ridge",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "log_heat_input", "log_t85"],
                         standardise=True),
        ExperimentConfig("E42", "Ridge on log features only",
                         prior=0.30, mechanism="Pure log-linear model",
                         model_family="ridge",
                         extra_features=["log_heat_input", "log_t85", "log_travel"],
                         standardise=True, sklearn_kwargs={"alpha": 0.1}),
        ExperimentConfig("E43", "Ridge alpha sweep 10.0",
                         prior=0.15, mechanism="Heavier regularisation",
                         model_family="ridge",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "log_heat_input", "log_t85"],
                         standardise=True, sklearn_kwargs={"alpha": 10.0}),
    ]
    # 10. Winner family alternates + repeats for robustness
    xs += [
        ExperimentConfig("E44", "LightGBM + physics bundle",
                         prior=0.40, mechanism="LGBM often ties/exceeds XGB",
                         model_family="lightgbm",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"]),
        ExperimentConfig("E45", "LightGBM + full bundle",
                         prior=0.35, mechanism="All physics features",
                         model_family="lightgbm",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "hi_over_thk", "ce_times_hi"]),
        ExperimentConfig("E46", "ExtraTrees + physics bundle",
                         prior=0.30, mechanism="Bagging vs boosting test",
                         model_family="extratrees",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         sklearn_kwargs={"min_samples_leaf": 2}),
        ExperimentConfig("E47", "ExtraTrees deeper (unlimited depth)",
                         prior=0.25, mechanism="Full-depth bagging",
                         model_family="extratrees",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"]),
    ]
    # 11. Combinations of the best bets
    xs += [
        ExperimentConfig("E48", "XGB + HI + t85 + n=600 + monotone(HI)",
                         prior=0.60, mechanism="Compose the strongest single changes",
                         model_family="xgboost",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
                         n_estimators=600,
                         monotone_constraints={"heat_input_kj_mm": 1}),
        ExperimentConfig("E49", "XGB + full bundle + log target",
                         prior=0.45, mechanism="Log stabilise + physics features",
                         model_family="xgboost",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "hi_over_thk", "ce_times_hi"],
                         log_target=True),
        ExperimentConfig("E50", "XGB + full bundle + monotone(HI, t85)",
                         prior=0.55, mechanism="Compose physics features + constraints",
                         model_family="xgboost",
                         extra_features=["heat_input_kj_mm", "cooling_t85_s_est",
                                          "hi_over_thk", "ce_times_hi"],
                         monotone_constraints={"heat_input_kj_mm": 1, "cooling_t85_s_est": 1}),
    ]
    return xs


def main():
    RESULTS_TSV.write_text("exp_id\tdescription\tmae\trmse\tr2\tn_pareto\tbest_efficiency\tprior\tdecision\tnotes\n")
    df = load_dataset()
    print(f"dataset: {len(df)} arc-welding rows (GMAW+GTAW)")
    print(f"target range: {df['haz_width_mm'].min():.2f}–{df['haz_width_mm'].max():.2f} mm\n")

    # -------- Phase 0.5 baseline: XGBoost on raw features only
    print("=" * 66)
    print("PHASE 0.5: raw-feature baseline (E00)")
    print("=" * 66)
    base_cfg = ExperimentConfig("E00", "XGBoost on raw process features",
                                1.0, "no physics-informed features",
                                model_family="xgboost")
    base = fit_predict(base_cfg, df)
    print(f"  MAE={base['mae']:.4f}  R²={base['r2']:.4f}")
    append_row(base_cfg.exp_id, base_cfg.description, base["mae"], base["rmse"],
               base["r2"], "", "", base_cfg.prior, "BASELINE", "raw features")
    best_mae = base["mae"]
    best_cfg: Optional[ExperimentConfig] = base_cfg

    # -------- Phase 1 tournament: 4 fundamentally different model families
    print("\n" + "=" * 66)
    print("PHASE 1: four-way model-family tournament")
    print("=" * 66)
    tournament = [
        ExperimentConfig("T01", "LightGBM on raw features",
                         prior=0.55, mechanism="Tabular parity with XGBoost",
                         model_family="lightgbm"),
        ExperimentConfig("T02", "ExtraTrees on raw features",
                         prior=0.45, mechanism="Bagging may help small-N",
                         model_family="extratrees"),
        ExperimentConfig("T03", "Ridge regression on raw features (linear baseline)",
                         prior=0.10, mechanism="Textbook scalings are linear/log-linear",
                         model_family="ridge", standardise=True),
    ]
    tournament_results: Dict[str, Dict[str, float]] = {}
    for cfg in tournament:
        m = fit_predict(cfg, df)
        tournament_results[cfg.exp_id] = m
        delta = m["mae"] - base["mae"]
        decision = "KEEP" if m["mae"] < base["mae"] else "REVERT"
        print(f"  [{cfg.exp_id}] {cfg.description[:52]:52s} MAE={m['mae']:.4f}  Δ={delta:+.4f}  → {decision}")
        append_row(cfg.exp_id, cfg.description, m["mae"], m["rmse"], m["r2"],
                   "", "", cfg.prior, decision, f"family={cfg.model_family}")

    # pick winner — include E00 in the candidate set
    all_candidates = {"E00": base, **tournament_results}
    winner_id = min(all_candidates, key=lambda k: all_candidates[k]["mae"])
    winner_mae = all_candidates[winner_id]["mae"]
    family_map = {"E00": "xgboost", "T01": "lightgbm", "T02": "extratrees", "T03": "ridge"}
    winner_family = family_map[winner_id]
    print(f"\ntournament winner: {winner_id} — MAE={winner_mae:.4f}  family={winner_family}")
    best_mae = winner_mae

    # -------- Phase 2 HDR loop
    print("\n" + "=" * 66)
    print("PHASE 2: HDR loop (50 single-change experiments)")
    print("=" * 66)
    keep = 0
    revert = 0
    best_phase2_cfg: Optional[ExperimentConfig] = None
    for cfg in phase_2_experiments(winner_family):
        t0 = time.time()
        m = fit_predict(cfg, df)
        dt = time.time() - t0
        delta = m["mae"] - best_mae
        # Require a strict improvement above noise floor (1% of best_mae)
        threshold = max(0.005, 0.01 * best_mae)
        if m["mae"] < best_mae - threshold:
            decision = "KEEP"
            best_mae = m["mae"]
            best_phase2_cfg = cfg
            keep += 1
        else:
            decision = "REVERT"
            revert += 1
        print(f"  [{cfg.exp_id}] p={cfg.prior:.2f}  {cfg.description[:50]:50s} "
              f"MAE={m['mae']:.4f}  Δ={delta:+.4f}  ({dt:.1f}s)  → {decision}")
        append_row(cfg.exp_id, cfg.description, m["mae"], m["rmse"], m["r2"],
                   "", "", cfg.prior, decision,
                   f"family={cfg.model_family} feats={len(cfg.extra_features)}")

    print(f"\nphase 2: {keep} KEEP, {revert} REVERT  → best MAE={best_mae:.4f}")

    # Save winning config to JSON for phase_b_discovery.py
    final = best_phase2_cfg or base_cfg
    winning = {
        "exp_id": final.exp_id,
        "description": final.description,
        "model_family": final.model_family,
        "extra_features": list(final.extra_features),
        "xgb_params": final.xgb_params,
        "lgb_params": final.lgb_params,
        "sklearn_kwargs": final.sklearn_kwargs,
        "monotone_constraints": final.monotone_constraints,
        "log_target": final.log_target,
        "n_estimators": final.n_estimators,
        "target": final.target,
        "mae": best_mae,
    }
    (PROJECT_ROOT / "winning_config.json").write_text(json.dumps(winning, indent=2))
    print(f"\nwrote winning_config.json  (exp_id={final.exp_id})")


if __name__ == "__main__":
    main()
