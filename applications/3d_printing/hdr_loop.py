"""hdr_loop.py -- Phase 1 tournament plus Phase 2 Hypothesis-Driven
Research (HDR) loop for the Fused Deposition Modelling (FDM) parameter
optimisation project.

Each experiment defines a different PrinterModel variant (different
features, hyperparameters, model family, or target transform), evaluates
it via a 5-fold cross-validation harness that is structurally identical
to evaluate.py, records the result in results.tsv, and decides KEEP or
REVERT against the previous best according to a pre-registered delta
threshold.

Phase 1 runs a model-family tournament with four fundamentally different
approaches (Extreme Gradient Boosting, Light Gradient Boosting Machine,
Extra Trees, and Ridge regression) on the raw feature set.

Phase 2 runs 50+ single-change experiments sourced from research_queue.md
and knowledge_base.md, covering derived physics features, hyperparameter
tuning, monotonicity constraints, and target transforms.

Phase 2.5 (hdr_phase25.py) explicitly composes the kept changes to
verify the union beats each kept change in isolation.

Phase B (phase_b_discovery.py) takes the final winning model and runs
a multi-strategy candidate generation sweep.

Every row in results.tsv is reproducible by instantiating the matching
ExperimentConfig and re-running fit_predict.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
import xgboost as xgb
import lightgbm as lgb

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_TSV = PROJECT_ROOT / "results.tsv"
DATA_PATH = PROJECT_ROOT / "data" / "3d_printing.csv"
N_FOLDS = 5
RANDOM_SEED = 42

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

# Fixed Ultimaker S5 0.4 mm nozzle assumption: the Kaggle dataset does
# not include line width, so we use the slicer default of 0.48 mm
# (= 1.2 x 0.40). This constant is only used inside derived features.
LINE_WIDTH_MM = 0.48

# Glass transition temperatures (Tg, degrees Celsius) for the two
# materials in the dataset. Used for derived features that need the
# thermal margin above Tg. Values from the FDM literature (Sun et al.
# 2008; Cantrell et al. 2017).
TG_BY_MATERIAL = {
    0: 105.0,   # Acrylonitrile Butadiene Styrene (ABS)
    1: 60.0,    # Poly-Lactic Acid (PLA)
}


def load_dataset() -> pd.DataFrame:
    """Load the Kaggle 3D Printer Dataset (semicolon-separated)."""
    return pd.read_csv(DATA_PATH, sep=";")


def add_features(df: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    """Compute derived features on a copy of df.

    `features` is a list of string keys. Each key maps to a derived
    column the cross-validation harness will use in addition to
    RAW_FEATURES. Grounded in the literature review (themes 3 and 5).
    """
    out = df.copy()
    layer_h = out["layer_height"].replace(0, np.nan)
    for f in features:
        if f == "E_lin":
            # Linear energy density (LPBF analogue): T_nozzle * v / h
            out["E_lin"] = out["nozzle_temperature"] * out["print_speed"] / layer_h
            out["E_lin"] = out["E_lin"].fillna(0.0)
        elif f == "vol_flow":
            # Volumetric flow rate = v * h * w_line (mm^3 per second)
            out["vol_flow"] = out["print_speed"] * out["layer_height"] * LINE_WIDTH_MM
        elif f == "cool_rate":
            # Cooling-rate proxy = (T_nozzle - T_amb) * fan% / h_layer
            out["cool_rate"] = ((out["nozzle_temperature"] - 25.0)
                                * out["fan_speed"] / layer_h)
            out["cool_rate"] = out["cool_rate"].fillna(0.0)
        elif f == "interlayer_time":
            # Time spent depositing one layer over a 50 mm x 50 mm
            # footprint. Proxy for how long the interface stays above
            # glass transition temperature.
            footprint = 50.0 * 50.0  # mm^2
            out["interlayer_time"] = footprint / (
                out["print_speed"].replace(0, np.nan) * LINE_WIDTH_MM)
            out["interlayer_time"] = out["interlayer_time"].fillna(0.0)
        elif f == "infill_contact":
            # Infill contact area, proxy = rho_infill x footprint.
            out["infill_contact"] = out["infill_density"] / 100.0 * 2500.0
        elif f == "thermal_margin":
            # (T_nozzle - T_g(material)) in degrees Celsius.
            tg = out["material"].map(TG_BY_MATERIAL)
            out["thermal_margin"] = out["nozzle_temperature"] - tg
        elif f == "log_layer":
            out["log_layer"] = np.log1p(out["layer_height"].astype(float))
        elif f == "log_speed":
            out["log_speed"] = np.log1p(out["print_speed"].astype(float))
        elif f == "inv_layer":
            out["inv_layer"] = 1.0 / (out["layer_height"].astype(float) + 1e-6)
        elif f == "inv_speed":
            out["inv_speed"] = 1.0 / (out["print_speed"].astype(float) + 1e-6)
        elif f == "temp_x_infill":
            out["temp_x_infill"] = out["nozzle_temperature"] * out["infill_density"]
        elif f == "speed_x_layer":
            out["speed_x_layer"] = out["print_speed"] * out["layer_height"]
        elif f == "temp_margin_x_wall":
            tg = out["material"].map(TG_BY_MATERIAL)
            out["temp_margin_x_wall"] = ((out["nozzle_temperature"] - tg)
                                         * out["wall_thickness"])
        elif f == "fan_over_temp_margin":
            tg = out["material"].map(TG_BY_MATERIAL)
            margin = (out["nozzle_temperature"] - tg).replace(0, np.nan)
            out["fan_over_temp_margin"] = out["fan_speed"] / margin
            out["fan_over_temp_margin"] = out["fan_over_temp_margin"].fillna(0.0)
        elif f == "bed_over_Tg":
            tg = out["material"].map(TG_BY_MATERIAL)
            out["bed_over_Tg"] = out["bed_temperature"] / tg
        elif f == "is_pla":
            out["is_pla"] = (out["material"] == 1).astype(float)
        elif f == "sqrt_infill":
            out["sqrt_infill"] = np.sqrt(out["infill_density"].astype(float))
        elif f == "road_aspect":
            # Aspect ratio of the deposited road: h / w_line.
            out["road_aspect"] = out["layer_height"].astype(float) / LINE_WIDTH_MM
        elif f == "Elin_per_vol":
            # Linear energy density normalised by volumetric flow.
            e_lin = out["nozzle_temperature"] * out["print_speed"] / layer_h
            vol_flow = out["print_speed"] * out["layer_height"] * LINE_WIDTH_MM
            out["Elin_per_vol"] = e_lin / vol_flow.replace(0, np.nan)
            out["Elin_per_vol"] = out["Elin_per_vol"].fillna(0.0)
        elif f == "walls_x_infill":
            out["walls_x_infill"] = out["wall_thickness"] * out["infill_density"]
        elif f == "layer_ratio":
            # layer_height / nozzle diameter (0.4 assumed)
            out["layer_ratio"] = out["layer_height"].astype(float) / 0.4
        elif f == "cool_per_fan":
            layer_h_local = out["layer_height"].astype(float)
            out["cool_per_fan"] = ((out["nozzle_temperature"] - 25.0)
                                   / (layer_h_local + 1e-6))
        else:
            raise ValueError(f"Unknown feature: {f}")
    return out


# ---------------------------------------------------------------------------
# Model configurations
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


XGB_DEFAULT = {
    "objective": "reg:squarederror",
    "max_depth": 6,
    "learning_rate": 0.05,
    "min_child_weight": 3,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "verbosity": 0,
}


def fit_predict(cfg: ExperimentConfig, df: pd.DataFrame) -> Dict[str, float]:
    """Run a 5-fold cross-validation for the given config. Returns a
    metric dict {mae, rmse, r2}."""
    df_feat = add_features(df, cfg.extra_features)
    feature_names = RAW_FEATURES + list(cfg.extra_features)
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    all_y_true, all_y_pred = [], []

    for train_idx, test_idx in kf.split(df_feat):
        train = df_feat.iloc[train_idx]
        test = df_feat.iloc[test_idx]
        X_tr = train[feature_names].values.astype(np.float32)
        X_te = test[feature_names].values.astype(np.float32)
        y_tr = train["tension_strength"].values.astype(np.float32)
        y_te = test["tension_strength"].values.astype(np.float32)
        y_tr_fit = np.log1p(y_tr) if cfg.log_target else y_tr

        if cfg.model_family == "xgboost":
            params = dict(XGB_DEFAULT)
            params.update(cfg.xgb_params)
            if cfg.monotone_constraints:
                vec = [cfg.monotone_constraints.get(f, 0) for f in feature_names]
                params["monotone_constraints"] = (
                    "(" + ",".join(str(v) for v in vec) + ")")
            dtr = xgb.DMatrix(X_tr, label=y_tr_fit)
            dte = xgb.DMatrix(X_te)
            booster = xgb.train(params, dtr, num_boost_round=cfg.n_estimators)
            y_pred = booster.predict(dte)

        elif cfg.model_family == "lightgbm":
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
            params.update(cfg.lgb_params)
            dtr = lgb.Dataset(X_tr, label=y_tr_fit)
            booster = lgb.train(params, dtr, num_boost_round=cfg.n_estimators)
            y_pred = booster.predict(X_te)

        elif cfg.model_family == "extratrees":
            kwargs = {
                "n_estimators": cfg.n_estimators,
                "random_state": RANDOM_SEED,
                "n_jobs": -1,
            }
            kwargs.update(cfg.sklearn_kwargs)
            mdl = ExtraTreesRegressor(**kwargs)
            mdl.fit(X_tr, y_tr_fit)
            y_pred = mdl.predict(X_te)

        elif cfg.model_family == "randomforest":
            kwargs = {
                "n_estimators": cfg.n_estimators,
                "random_state": RANDOM_SEED,
                "n_jobs": -1,
            }
            kwargs.update(cfg.sklearn_kwargs)
            mdl = RandomForestRegressor(**kwargs)
            mdl.fit(X_tr, y_tr_fit)
            y_pred = mdl.predict(X_te)

        elif cfg.model_family == "ridge":
            kwargs = {"alpha": 1.0}
            kwargs.update(cfg.sklearn_kwargs)
            mdl = Ridge(**kwargs)
            mdl.fit(X_tr, y_tr_fit)
            y_pred = mdl.predict(X_te)

        else:
            raise ValueError(f"Unknown model family: {cfg.model_family}")

        if cfg.log_target:
            y_pred = np.expm1(y_pred)
        all_y_true.extend(y_te.tolist())
        all_y_pred.extend(y_pred.tolist())

    y_true = np.array(all_y_true)
    y_pred = np.array(all_y_pred)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


# ---------------------------------------------------------------------------
# Phase 1 tournament + Phase 2 hypothesis-driven loop
# ---------------------------------------------------------------------------


def append_row(exp_id, description, mae, rmse, r2, n_pareto, best_eff,
               prior, decision, notes) -> None:
    """Append one row to results.tsv. Columns match concrete/results.tsv."""
    if not RESULTS_TSV.exists():
        header = ("exp_id\tdescription\tmae\trmse\tr2\tn_pareto\tbest_efficiency"
                  "\tprior\tdecision\tnotes\n")
        RESULTS_TSV.write_text(header)
    with RESULTS_TSV.open("a") as fh:
        fh.write(
            f"{exp_id}\t{description}\t{mae:.4f}\t{rmse:.4f}\t{r2:.4f}\t"
            f"{n_pareto}\t{best_eff}\t{prior:.2f}\t{decision}\t{notes}\n")


def run_tournament(df: pd.DataFrame, base: Dict[str, float]) -> tuple:
    """Phase 1: four-way model-family tournament on raw features."""
    tournament = [
        ExperimentConfig(
            "T01", "LightGBM on raw features",
            prior=0.45,
            mechanism="LightGBM sometimes beats XGBoost on small tabular",
            model_family="lightgbm"),
        ExperimentConfig(
            "T02", "ExtraTrees on raw features",
            prior=0.50,
            mechanism="Bagging often beats boosting for N<400 (concrete note)",
            model_family="extratrees"),
        ExperimentConfig(
            "T03", "RandomForest on raw features",
            prior=0.40,
            mechanism="Bagging variant; cross-check ExtraTrees result",
            model_family="randomforest"),
        ExperimentConfig(
            "T04", "Ridge regression on raw features (linear sanity check)",
            prior=0.10,
            mechanism="If trees are not >2x better than linear, skip neural nets",
            model_family="ridge"),
    ]
    print("=" * 60)
    print("PHASE 1: Model family tournament")
    print("=" * 60)
    results = {}
    for cfg in tournament:
        m = fit_predict(cfg, df)
        results[cfg.exp_id] = m
        delta = m["mae"] - base["mae"]
        decision = "KEEP" if m["mae"] < base["mae"] else "REVERT"
        print(f"[{cfg.exp_id}] {cfg.description[:55]:55s} "
              f"MAE={m['mae']:.4f} (delta={delta:+.4f}) -> {decision}")
        append_row(cfg.exp_id, cfg.description, m["mae"], m["rmse"], m["r2"],
                   "", "", cfg.prior, decision, f"family={cfg.model_family}")
    candidates = {**{"E00": base}, **results}
    winner_id = min(candidates, key=lambda k: candidates[k]["mae"])
    winner_mae = candidates[winner_id]["mae"]
    print(f"\nTournament winner: {winner_id} MAE={winner_mae:.4f}")
    family_map = {
        "E00": "xgboost", "T01": "lightgbm", "T02": "extratrees",
        "T03": "randomforest", "T04": "ridge",
    }
    return winner_id, family_map[winner_id], winner_mae


def build_phase2_experiments(winner_family: str) -> List[ExperimentConfig]:
    """Fifty Phase 2 single-change hypotheses sourced from research_queue.md.
    Each experiment is a full specification (not compositional)."""
    wf = winner_family
    exps: List[ExperimentConfig] = [
        # ---- Physics-informed derived features (H1, H2 from the queue)
        ExperimentConfig("E01", "Add linear energy density E_lin",
                         prior=0.70,
                         mechanism="LPBF-analogue thermal feature: "
                                   "T*v/h couples the three dominant drivers",
                         model_family=wf, extra_features=["E_lin"]),
        ExperimentConfig("E02", "Add volumetric flow rate",
                         prior=0.40,
                         mechanism="Volumetric flow = v*h*w caps under-extrusion",
                         model_family=wf, extra_features=["vol_flow"]),
        ExperimentConfig("E03", "Add cooling-rate proxy",
                         prior=0.55,
                         mechanism="Cooling reduces inter-layer diffusion time",
                         model_family=wf, extra_features=["cool_rate"]),
        ExperimentConfig("E04", "Add interlayer time (Sun-model proxy)",
                         prior=0.60,
                         mechanism="Time above Tg controls bond strength",
                         model_family=wf, extra_features=["interlayer_time"]),
        ExperimentConfig("E05", "Add infill contact area",
                         prior=0.50,
                         mechanism="Load-bearing cross section scales with infill",
                         model_family=wf, extra_features=["infill_contact"]),
        ExperimentConfig("E06", "Add thermal margin above Tg",
                         prior=0.50,
                         mechanism="T_nozzle - Tg measures how far above glass transition",
                         model_family=wf, extra_features=["thermal_margin"]),
        ExperimentConfig("E07", "Full physics feature set",
                         prior=0.55,
                         mechanism="Joint effect may exceed any single feature",
                         model_family=wf, extra_features=[
                             "E_lin", "vol_flow", "cool_rate",
                             "interlayer_time", "infill_contact",
                             "thermal_margin"]),
        ExperimentConfig("E08", "Physics set minus cool_rate",
                         prior=0.45,
                         mechanism="Cool rate may be redundant with fan_speed",
                         model_family=wf, extra_features=[
                             "E_lin", "vol_flow", "interlayer_time",
                             "infill_contact", "thermal_margin"]),
        ExperimentConfig("E09", "Physics set minus interlayer_time",
                         prior=0.45,
                         mechanism="Interlayer time uses an assumed 50mm footprint",
                         model_family=wf, extra_features=[
                             "E_lin", "vol_flow", "cool_rate",
                             "infill_contact", "thermal_margin"]),
        ExperimentConfig("E10", "Physics set minus thermal_margin",
                         prior=0.45,
                         mechanism="Thermal margin may be redundant with nozzle_temp",
                         model_family=wf, extra_features=[
                             "E_lin", "vol_flow", "cool_rate",
                             "interlayer_time", "infill_contact"]),

        # ---- Simpler log / inverse transforms
        ExperimentConfig("E11", "Add log(layer_height)",
                         prior=0.35,
                         mechanism="Layer height has multiplicative scaling",
                         model_family=wf, extra_features=["log_layer"]),
        ExperimentConfig("E12", "Add log(print_speed)",
                         prior=0.35,
                         mechanism="Print speed may have multiplicative impact",
                         model_family=wf, extra_features=["log_speed"]),
        ExperimentConfig("E13", "Add 1/layer_height",
                         prior=0.35,
                         mechanism="Strength scales inversely with layer height",
                         model_family=wf, extra_features=["inv_layer"]),
        ExperimentConfig("E14", "Add 1/print_speed",
                         prior=0.35,
                         mechanism="Lower speed -> more heating time",
                         model_family=wf, extra_features=["inv_speed"]),
        ExperimentConfig("E15", "Add road aspect ratio h/w",
                         prior=0.30,
                         mechanism="Road shape affects bonding interface",
                         model_family=wf, extra_features=["road_aspect"]),

        # ---- Interactions (H6: SHAP interaction findings)
        ExperimentConfig("E16", "Add nozzle_temp x infill_density interaction",
                         prior=0.45,
                         mechanism="Temperature and infill are top-2 drivers",
                         model_family=wf, extra_features=["temp_x_infill"]),
        ExperimentConfig("E17", "Add print_speed x layer_height interaction",
                         prior=0.40,
                         mechanism="Product is proportional to volumetric flow",
                         model_family=wf, extra_features=["speed_x_layer"]),
        ExperimentConfig("E18", "Add thermal_margin x wall_thickness",
                         prior=0.35,
                         mechanism="More walls amplify thermal-history effect",
                         model_family=wf, extra_features=["temp_margin_x_wall"]),
        ExperimentConfig("E19", "Add fan_speed / thermal_margin",
                         prior=0.30,
                         mechanism="Cooling efficiency relative to thermal margin",
                         model_family=wf, extra_features=["fan_over_temp_margin"]),
        ExperimentConfig("E20", "Add bed_temperature / Tg",
                         prior=0.35,
                         mechanism="Bed temperature normalised by glass transition",
                         model_family=wf, extra_features=["bed_over_Tg"]),

        # ---- Categorical / material features
        ExperimentConfig("E21", "Add is_pla binary flag",
                         prior=0.20,
                         mechanism="Material is already in raw feature set",
                         model_family=wf, extra_features=["is_pla"]),

        # ---- Hyperparameter sweeps (priors all <= 0.35 per program.md)
        ExperimentConfig("E22", "Lower learning rate 0.05 -> 0.02, n=600",
                         prior=0.30,
                         mechanism="Smaller LR with more rounds",
                         model_family=wf, extra_features=["E_lin"],
                         xgb_params={"learning_rate": 0.02},
                         lgb_params={"learning_rate": 0.02},
                         n_estimators=600),
        ExperimentConfig("E23", "Lower learning rate 0.05 -> 0.03, n=500",
                         prior=0.30,
                         mechanism="Moderate learning rate reduction",
                         model_family=wf, extra_features=["E_lin"],
                         xgb_params={"learning_rate": 0.03},
                         lgb_params={"learning_rate": 0.03},
                         n_estimators=500),
        ExperimentConfig("E24", "Increase max_depth to 8",
                         prior=0.25,
                         mechanism="Deeper trees for interactions",
                         model_family=wf, extra_features=["E_lin"],
                         xgb_params={"max_depth": 8},
                         lgb_params={"num_leaves": 63}),
        ExperimentConfig("E25", "Decrease max_depth to 4",
                         prior=0.30,
                         mechanism="Shallower trees for N=50",
                         model_family=wf, extra_features=["E_lin"],
                         xgb_params={"max_depth": 4},
                         lgb_params={"num_leaves": 15}),
        ExperimentConfig("E26", "Decrease max_depth to 3",
                         prior=0.30,
                         mechanism="Even shallower trees for small N",
                         model_family=wf, extra_features=["E_lin"],
                         xgb_params={"max_depth": 3},
                         lgb_params={"num_leaves": 7}),
        ExperimentConfig("E27", "Subsample 0.8 -> 0.6",
                         prior=0.25,
                         mechanism="More aggressive bagging",
                         model_family=wf, extra_features=["E_lin"],
                         xgb_params={"subsample": 0.6},
                         lgb_params={"bagging_fraction": 0.6}),
        ExperimentConfig("E28", "min_child_weight 3 -> 1",
                         prior=0.30,
                         mechanism="Finer leaves for small dataset",
                         model_family=wf, extra_features=["E_lin"],
                         xgb_params={"min_child_weight": 1},
                         lgb_params={"min_data_in_leaf": 1}),
        ExperimentConfig("E29", "min_child_weight 3 -> 5",
                         prior=0.25,
                         mechanism="Coarser leaves for overfit control",
                         model_family=wf, extra_features=["E_lin"],
                         xgb_params={"min_child_weight": 5},
                         lgb_params={"min_data_in_leaf": 5}),
        ExperimentConfig("E30", "n_estimators 300 -> 600",
                         prior=0.30,
                         mechanism="More rounds at baseline learning rate",
                         model_family=wf, extra_features=["E_lin"],
                         n_estimators=600),
        ExperimentConfig("E31", "n_estimators 300 -> 900",
                         prior=0.25,
                         mechanism="Even more rounds",
                         model_family=wf, extra_features=["E_lin"],
                         n_estimators=900),
        ExperimentConfig("E32", "colsample_bytree 0.8 -> 0.5",
                         prior=0.25,
                         mechanism="More column bagging for small N",
                         model_family=wf, extra_features=["E_lin"],
                         xgb_params={"colsample_bytree": 0.5},
                         lgb_params={"feature_fraction": 0.5}),

        # ---- Target transform (H3)
        ExperimentConfig("E33", "Train on log(tension_strength) target",
                         prior=0.35,
                         mechanism="Target is mildly right-skewed",
                         model_family=wf, extra_features=["E_lin"],
                         log_target=True),

        # ---- Monotonicity constraints (H5)
        ExperimentConfig("E34", "Monotone: infill_density -> strength (+1)",
                         prior=0.55,
                         mechanism="More infill -> more strength (Wang 2020 SHAP)",
                         model_family="xgboost", extra_features=["E_lin"],
                         monotone_constraints={"infill_density": 1}),
        ExperimentConfig("E35", "Monotone: nozzle_temperature -> strength (+1)",
                         prior=0.55,
                         mechanism="Higher T -> better inter-layer diffusion (Sun 2008)",
                         model_family="xgboost", extra_features=["E_lin"],
                         monotone_constraints={"nozzle_temperature": 1}),
        ExperimentConfig("E36", "Monotone: print_speed -> strength (-1)",
                         prior=0.55,
                         mechanism="Higher speed -> less time above Tg -> weaker",
                         model_family="xgboost", extra_features=["E_lin"],
                         monotone_constraints={"print_speed": -1}),
        ExperimentConfig("E37", "Monotone: layer_height -> strength (-1)",
                         prior=0.45,
                         mechanism="Thinner layers bond more (Wu 2015)",
                         model_family="xgboost", extra_features=["E_lin"],
                         monotone_constraints={"layer_height": -1}),
        ExperimentConfig("E38", "Monotone: infill+ and speed-",
                         prior=0.60,
                         mechanism="Two well-established physical priors together",
                         model_family="xgboost", extra_features=["E_lin"],
                         monotone_constraints={
                             "infill_density": 1, "print_speed": -1}),
        ExperimentConfig("E39", "Monotone: infill+, speed-, nozzle_temp+",
                         prior=0.50,
                         mechanism="All three top SHAP drivers",
                         model_family="xgboost", extra_features=["E_lin"],
                         monotone_constraints={
                             "infill_density": 1, "print_speed": -1,
                             "nozzle_temperature": 1}),
        ExperimentConfig("E40", "Monotone: infill+, speed-, layer-",
                         prior=0.50,
                         mechanism="Three geometric/kinematic constraints",
                         model_family="xgboost", extra_features=["E_lin"],
                         monotone_constraints={
                             "infill_density": 1, "print_speed": -1,
                             "layer_height": -1}),

        # ---- Feature subset studies
        ExperimentConfig("E41", "Add sqrt(infill_density)",
                         prior=0.30,
                         mechanism="Square-root compresses top end (saturation)",
                         model_family=wf, extra_features=["sqrt_infill"]),
        ExperimentConfig("E42", "Add walls_x_infill interaction",
                         prior=0.30,
                         mechanism="Shell and infill jointly carry load",
                         model_family=wf, extra_features=["walls_x_infill"]),
        ExperimentConfig("E43", "Add layer_ratio (h / d_nozzle)",
                         prior=0.25,
                         mechanism="Dimensionless layer-to-nozzle ratio",
                         model_family=wf, extra_features=["layer_ratio"]),
        ExperimentConfig("E44", "Add cool_per_fan (cool rate per fan slot)",
                         prior=0.25,
                         mechanism="Alternative cooling formulation",
                         model_family=wf, extra_features=["cool_per_fan"]),
        ExperimentConfig("E45", "Add Elin_per_vol",
                         prior=0.30,
                         mechanism="Energy per unit volume (not per length)",
                         model_family=wf, extra_features=["Elin_per_vol"]),

        # ---- Ensemble and averaging (priors modest per program.md)
        ExperimentConfig("E46", "E_lin + interlayer_time",
                         prior=0.40,
                         mechanism="Two complementary thermal features",
                         model_family=wf,
                         extra_features=["E_lin", "interlayer_time"]),
        ExperimentConfig("E47", "E_lin + cool_rate",
                         prior=0.40,
                         mechanism="Heat in plus heat out",
                         model_family=wf,
                         extra_features=["E_lin", "cool_rate"]),
        ExperimentConfig("E48", "E_lin + thermal_margin",
                         prior=0.40,
                         mechanism="Absolute and relative thermal drivers",
                         model_family=wf,
                         extra_features=["E_lin", "thermal_margin"]),
        ExperimentConfig("E49", "E_lin + infill_contact",
                         prior=0.40,
                         mechanism="Thermal plus mechanical drivers",
                         model_family=wf,
                         extra_features=["E_lin", "infill_contact"]),
        ExperimentConfig("E50", "E_lin + temp_x_infill",
                         prior=0.40,
                         mechanism="E_lin plus the top-2 driver interaction",
                         model_family=wf,
                         extra_features=["E_lin", "temp_x_infill"]),
    ]
    return exps


def run_phase2(df: pd.DataFrame, winner_family: str, winner_mae: float) -> tuple:
    """Phase 2 HDR loop: 50 single-change experiments."""
    print("=" * 60)
    print("PHASE 2: HDR loop (50 single-change experiments)")
    print("=" * 60)
    experiments = build_phase2_experiments(winner_family)
    best_mae = winner_mae
    best_cfg: Optional[ExperimentConfig] = None
    keep_count = 0
    revert_count = 0

    for cfg in experiments:
        m = fit_predict(cfg, df)
        delta = m["mae"] - best_mae
        if m["mae"] < best_mae - 0.005:
            decision = "KEEP"
            best_mae = m["mae"]
            best_cfg = cfg
            keep_count += 1
        else:
            decision = "REVERT"
            revert_count += 1
        print(f"[{cfg.exp_id}] prior={cfg.prior:.2f} "
              f"{cfg.description[:56]:56s} MAE={m['mae']:.4f} "
              f"(delta={delta:+.4f}) -> {decision}")
        append_row(cfg.exp_id, cfg.description, m["mae"], m["rmse"], m["r2"],
                   "", "", cfg.prior, decision,
                   f"family={cfg.model_family} feats={len(cfg.extra_features)}")

    print(f"\nPhase 2 summary: {keep_count} KEEP, {revert_count} REVERT")
    print(f"Final best MAE = {best_mae:.4f}")
    return best_cfg, best_mae, keep_count, revert_count


def save_winning_config(cfg: Optional[ExperimentConfig], winner_family: str,
                        best_mae: float, phase2_keeps: int) -> None:
    if cfg is not None:
        record = {
            "exp_id": cfg.exp_id,
            "description": cfg.description,
            "model_family": cfg.model_family,
            "extra_features": list(cfg.extra_features),
            "xgb_params": cfg.xgb_params,
            "lgb_params": cfg.lgb_params,
            "monotone_constraints": cfg.monotone_constraints,
            "log_target": cfg.log_target,
            "n_estimators": cfg.n_estimators,
            "mae": best_mae,
            "phase": "phase2",
        }
    else:
        record = {
            "exp_id": "E00",
            "description": f"tournament baseline ({winner_family}) on raw features",
            "model_family": winner_family,
            "extra_features": [],
            "xgb_params": {},
            "lgb_params": {},
            "monotone_constraints": None,
            "log_target": False,
            "n_estimators": 300,
            "mae": best_mae,
            "phase": "phase2",
        }
    record["phase2_keeps"] = phase2_keeps
    (PROJECT_ROOT / "winning_config.json").write_text(json.dumps(record, indent=2))
    print(f"\nWrote winning_config.json ({record['exp_id']}, MAE={best_mae:.4f})")


def main() -> None:
    df = load_dataset()
    print(f"Dataset: {len(df)} samples, tensile strength range "
          f"{df['tension_strength'].min():.1f} - "
          f"{df['tension_strength'].max():.1f} MPa\n")

    print("[E00] Baseline: XGBoost on raw features")
    base_cfg = ExperimentConfig(
        "E00", "Baseline XGBoost on raw features", prior=1.0,
        mechanism="established baseline", model_family="xgboost")
    t0 = time.time()
    base = fit_predict(base_cfg, df)
    print(f"  MAE = {base['mae']:.4f} MPa  R2 = {base['r2']:.4f}  "
          f"({time.time() - t0:.1f}s)")
    append_row("E00", base_cfg.description, base["mae"], base["rmse"],
               base["r2"], "", "", 1.0, "BASELINE",
               "depth=6 lr=0.05 n=300")

    winner_id, winner_family, winner_mae = run_tournament(df, base)
    print(f"  Phase 2 will use model family: {winner_family}\n")

    best_cfg, best_mae, keep, revert = run_phase2(
        df, winner_family, winner_mae)

    save_winning_config(best_cfg, winner_family, best_mae, keep)


if __name__ == "__main__":
    main()
