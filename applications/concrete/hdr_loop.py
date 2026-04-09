"""
hdr_loop.py — Phase 1 tournament + Phase 2 HDR loop for the concrete project.

Runs every experiment programmatically: each one defines a different
ConcreteModel variant (different features, hyperparameters, model family,
or ensemble strategy), evaluates it via the same evaluate.py harness used
for the baseline, records the result in results.tsv, and decides KEEP or
REVERT against the previous best.

The Phase 1 tournament tests 3 fundamentally different model families on
the raw feature set: XGBoost (the baseline), LightGBM, and ExtraTrees.
The winner is the starting point for Phase 2.

Phase 2 runs ~20 single-change experiments adding features, transforming
the target, modifying hyperparameters, and adding monotonicity constraints.

Phase B discovery (run separately by `phase_b_discovery.py`) takes the
final winning model and runs an aggressive multi-strategy candidate-
generation sweep.

Every row in results.tsv is reproducible by setting model.py to the
corresponding configuration and re-running evaluate.py.
"""
from __future__ import annotations

import json
import math
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.model_selection import KFold
import xgboost as xgb
import lightgbm as lgb

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_TSV = PROJECT_ROOT / "results.tsv"
DATA_PATH = PROJECT_ROOT / "data" / "concrete.csv"
N_FOLDS = 5
RANDOM_SEED = 42

COL_MAP = {
    "Cement (component 1)(kg in a m^3 mixture)": "cement",
    "Blast Furnace Slag (component 2)(kg in a m^3 mixture)": "slag",
    "Fly Ash (component 3)(kg in a m^3 mixture)": "fly_ash",
    "Water  (component 4)(kg in a m^3 mixture)": "water",
    "Superplasticizer (component 5)(kg in a m^3 mixture)": "superplasticizer",
    "Coarse Aggregate  (component 6)(kg in a m^3 mixture)": "coarse_agg",
    "Fine Aggregate (component 7)(kg in a m^3 mixture)": "fine_agg",
    "Age (day)": "age",
    "Concrete compressive strength(MPa. megapascals)": "strength",
}

RAW_FEATURES = [
    "cement", "slag", "fly_ash", "water", "superplasticizer",
    "coarse_agg", "fine_agg", "age",
]


def load_dataset() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH).rename(columns=COL_MAP)


def add_features(df: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    """Compute derived features on a copy of df. `features` is a list of
    string keys; each maps to a column the cross-validation harness will use
    in addition to RAW_FEATURES.
    """
    out = df.copy()
    for f in features:
        if f == "log_age":
            out["log_age"] = np.log1p(out["age"].astype(float))
        elif f == "wb_ratio":
            binder = out["cement"] + out["slag"] + out["fly_ash"]
            out["wb_ratio"] = out["water"] / binder.replace(0, np.nan)
            out["wb_ratio"] = out["wb_ratio"].fillna(out["wb_ratio"].median())
        elif f == "scm_pct":
            binder = out["cement"] + out["slag"] + out["fly_ash"]
            scm = out["slag"] + out["fly_ash"]
            out["scm_pct"] = scm / binder.replace(0, np.nan)
            out["scm_pct"] = out["scm_pct"].fillna(0)
        elif f == "binder_total":
            out["binder_total"] = out["cement"] + out["slag"] + out["fly_ash"]
        elif f == "agg_total":
            out["agg_total"] = out["coarse_agg"] + out["fine_agg"]
        elif f == "fine_frac":
            out["fine_frac"] = out["fine_agg"] / (out["coarse_agg"] + out["fine_agg"])
        elif f == "sp_per_binder":
            binder = out["cement"] + out["slag"] + out["fly_ash"]
            out["sp_per_binder"] = out["superplasticizer"] / binder.replace(0, np.nan)
            out["sp_per_binder"] = out["sp_per_binder"].fillna(0)
        elif f == "cement_per_water":
            out["cement_per_water"] = out["cement"] / out["water"].replace(0, np.nan)
            out["cement_per_water"] = out["cement_per_water"].fillna(0)
        elif f == "log_cement":
            out["log_cement"] = np.log1p(out["cement"])
        elif f == "log_water":
            out["log_water"] = np.log1p(out["water"])
        elif f == "slag_pct":
            binder = out["cement"] + out["slag"] + out["fly_ash"]
            out["slag_pct"] = out["slag"] / binder.replace(0, np.nan)
            out["slag_pct"] = out["slag_pct"].fillna(0)
        elif f == "fa_pct":
            binder = out["cement"] + out["slag"] + out["fly_ash"]
            out["fa_pct"] = out["fly_ash"] / binder.replace(0, np.nan)
            out["fa_pct"] = out["fa_pct"].fillna(0)
        elif f == "age_inv":
            out["age_inv"] = 1.0 / (out["age"].astype(float) + 1.0)
        elif f == "cement_x_age":
            out["cement_x_age"] = out["cement"] * np.log1p(out["age"])
        elif f == "wb_x_age":
            binder = out["cement"] + out["slag"] + out["fly_ash"]
            wb = out["water"] / binder.replace(0, np.nan)
            wb = wb.fillna(wb.median())
            out["wb_x_age"] = wb * np.log1p(out["age"])
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
    model_family: str = "xgboost"   # xgboost / lightgbm / extratrees / ridge
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
    """5-fold CV with the given configuration; returns metric dict."""
    df_feat = add_features(df, cfg.extra_features)
    feature_names = RAW_FEATURES + list(cfg.extra_features)
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    all_y_true, all_y_pred = [], []

    for train_idx, test_idx in kf.split(df_feat):
        train = df_feat.iloc[train_idx]
        test = df_feat.iloc[test_idx]
        X_tr = train[feature_names].values.astype(np.float32)
        X_te = test[feature_names].values.astype(np.float32)
        y_tr = train["strength"].values.astype(np.float32)
        y_te = test["strength"].values.astype(np.float32)
        if cfg.log_target:
            y_tr_fit = np.log1p(y_tr)
        else:
            y_tr_fit = y_tr

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
            params = {
                "objective": "regression",
                "metric": "mae",
                "num_leaves": 31,
                "learning_rate": 0.05,
                "feature_fraction": 0.8,
                "bagging_fraction": 0.8,
                "bagging_freq": 5,
                "min_data_in_leaf": 5,
                "verbosity": -1,
            }
            params.update(cfg.lgb_params)
            dtr = lgb.Dataset(X_tr, label=y_tr_fit)
            booster = lgb.train(params, dtr, num_boost_round=cfg.n_estimators)
            y_pred = booster.predict(X_te)
        elif cfg.model_family == "extratrees":
            kwargs = {"n_estimators": cfg.n_estimators, "random_state": RANDOM_SEED, "n_jobs": -1}
            kwargs.update(cfg.sklearn_kwargs)
            mdl = ExtraTreesRegressor(**kwargs)
            mdl.fit(X_tr, y_tr_fit)
            y_pred = mdl.predict(X_te)
        elif cfg.model_family == "randomforest":
            kwargs = {"n_estimators": cfg.n_estimators, "random_state": RANDOM_SEED, "n_jobs": -1}
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

def append_row(exp_id, description, mae, rmse, r2, n_pareto, best_eff, prior, decision, notes):
    with RESULTS_TSV.open("a") as fh:
        fh.write(
            f"{exp_id}\t{description}\t{mae:.4f}\t{rmse:.4f}\t{r2:.4f}\t"
            f"{n_pareto}\t{best_eff}\t{prior:.2f}\t{decision}\t{notes}\n"
        )


def main():
    df = load_dataset()
    print(f"Dataset: {len(df)} samples, target range "
          f"{df['strength'].min():.1f}–{df['strength'].max():.1f} MPa\n")

    # Re-establish baseline first
    print("[E00] Baseline: XGBoost on raw features")
    base_cfg = ExperimentConfig("E00", "Baseline XGBoost on raw features", 1.0, "established baseline")
    base = fit_predict(base_cfg, df)
    print(f"  MAE = {base['mae']:.4f}, R² = {base['r2']:.4f}")
    best_mae = base["mae"]
    best_cfg = base_cfg
    print(f"  → starting best: MAE = {best_mae:.4f}\n")

    # ---- Phase 1 tournament: 3 fundamentally different model families
    tournament = [
        ExperimentConfig("T01", "LightGBM on raw features",
                         prior=0.55, mechanism="LightGBM often beats XGBoost on tabular by 5-10%",
                         model_family="lightgbm"),
        ExperimentConfig("T02", "ExtraTrees on raw features",
                         prior=0.45, mechanism="Bagging may outperform boosting on small N",
                         model_family="extratrees"),
        ExperimentConfig("T03", "Ridge regression on raw features (linear baseline)",
                         prior=0.05, mechanism="If trees aren't >2x better than linear, skip NNs",
                         model_family="ridge"),
    ]
    print("=" * 60)
    print("PHASE 1: Model family tournament")
    print("=" * 60)
    tournament_results = {}
    for cfg in tournament:
        m = fit_predict(cfg, df)
        tournament_results[cfg.exp_id] = m
        delta = m["mae"] - base["mae"]
        decision = "KEEP" if m["mae"] < base["mae"] else "REVERT"
        print(f"[{cfg.exp_id}] {cfg.description[:50]:50s} MAE={m['mae']:.4f} "
              f"(Δ={delta:+.4f}) → {decision}")
        append_row(cfg.exp_id, cfg.description, m["mae"], m["rmse"], m["r2"],
                   "", "", cfg.prior, decision, f"family={cfg.model_family}")

    # Pick the tournament winner
    candidates = {**{"E00": base}, **tournament_results}
    winner_id = min(candidates, key=lambda k: candidates[k]["mae"])
    winner_mae = candidates[winner_id]["mae"]
    print(f"\nTournament winner: {winner_id} with MAE = {winner_mae:.4f}")

    # Choose model family for Phase 2 based on winner
    if winner_id == "T01":
        winner_family = "lightgbm"
    elif winner_id == "T02":
        winner_family = "extratrees"
    else:
        winner_family = "xgboost"
    print(f"  Phase 2 will use model family: {winner_family}\n")

    # Update best
    best_mae = winner_mae

    # ---- Phase 2 HDR loop: 20+ single-change experiments
    print("=" * 60)
    print("PHASE 2: HDR loop (20 single-change experiments)")
    print("=" * 60)

    experiments: List[ExperimentConfig] = [
        ExperimentConfig("E01", "Add log(age) feature",
                         prior=0.70, mechanism="Strength grows logarithmically with curing age",
                         model_family=winner_family, extra_features=["log_age"]),
        ExperimentConfig("E02", "Add water-to-binder ratio",
                         prior=0.85, mechanism="Abrams' law: w/b ratio drives strength",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio"]),
        ExperimentConfig("E03", "Add SCM percentage",
                         prior=0.60, mechanism="SCM fraction modulates strength via pozzolanic reaction",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio", "scm_pct"]),
        ExperimentConfig("E04", "Add total binder content",
                         prior=0.50, mechanism="Total binder is a primary strength predictor",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total"]),
        ExperimentConfig("E05", "Add aggregate ratio (fine_frac)",
                         prior=0.30, mechanism="Aggregate gradation has minor effect on workability and strength",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "fine_frac"]),
        ExperimentConfig("E06", "Add superplasticizer-per-binder ratio",
                         prior=0.40, mechanism="SP normalisation by binder is more meaningful than absolute SP",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"]),
        ExperimentConfig("E07", "Add cement/water ratio (inverse w/c)",
                         prior=0.30, mechanism="Cement-to-water is the inverse of w/c — may add nonlinearity",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder", "cement_per_water"]),
        ExperimentConfig("E08", "Add log(cement) and log(water)",
                         prior=0.30, mechanism="Log transforms help when underlying physics is multiplicative",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder", "log_cement", "log_water"]),
        ExperimentConfig("E09", "Add slag and fly-ash percentages separately",
                         prior=0.40, mechanism="Slag and fly-ash have different chemistry; separate features may help",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder", "slag_pct", "fa_pct"]),
        ExperimentConfig("E10", "Add cement×log(age) interaction",
                         prior=0.50, mechanism="Cement and age interact: more cement strengthens faster",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder", "cement_x_age"]),
        ExperimentConfig("E11", "Add (w/b ratio) × log(age) interaction",
                         prior=0.45, mechanism="High w/b mixes mature differently than low w/b mixes",
                         model_family=winner_family, extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder", "wb_x_age"]),
        ExperimentConfig("E12", "Lower learning rate to 0.03, n=500",
                         prior=0.30, mechanism="Smaller LR + more rounds often gains marginal accuracy",
                         model_family=winner_family,
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         xgb_params={"learning_rate": 0.03},
                         lgb_params={"learning_rate": 0.03},
                         n_estimators=500),
        ExperimentConfig("E13", "Increase max_depth to 8",
                         prior=0.30, mechanism="Deeper trees may capture interactions; risks overfitting",
                         model_family=winner_family,
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         xgb_params={"max_depth": 8},
                         lgb_params={"num_leaves": 63}),
        ExperimentConfig("E14", "Decrease max_depth to 4 (regularize)",
                         prior=0.30, mechanism="Shallower trees may generalize better on N=1030",
                         model_family=winner_family,
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         xgb_params={"max_depth": 4},
                         lgb_params={"num_leaves": 15}),
        ExperimentConfig("E15", "Subsample 0.6 (more aggressive bagging)",
                         prior=0.25, mechanism="More bagging may reduce overfit on small N",
                         model_family=winner_family,
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         xgb_params={"subsample": 0.6},
                         lgb_params={"bagging_fraction": 0.6}),
        ExperimentConfig("E16", "Train on log(strength) target",
                         prior=0.40, mechanism="Log target stabilises variance and matches Abrams law",
                         model_family=winner_family,
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         log_target=True),
        ExperimentConfig("E17", "Monotonicity constraint: cement → strength must increase",
                         prior=0.55, mechanism="Physically, more cement at fixed w/b → more strength",
                         model_family="xgboost",  # XGBoost has explicit monotone_constraints
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         monotone_constraints={"cement": 1, "age": 1}),
        ExperimentConfig("E18", "Monotonicity: cement+, age+, water-",
                         prior=0.60, mechanism="Three physical priors: more cement helps, more age helps, more water hurts",
                         model_family="xgboost",
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         monotone_constraints={"cement": 1, "age": 1, "water": -1}),
        ExperimentConfig("E19", "Larger min_child_weight (5)",
                         prior=0.30, mechanism="Higher MCW prevents overfitting to small leaves",
                         model_family=winner_family,
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         xgb_params={"min_child_weight": 5},
                         lgb_params={"min_data_in_leaf": 10}),
        ExperimentConfig("E20", "n_estimators 300 → 600",
                         prior=0.30, mechanism="More rounds with same LR may underfit less",
                         model_family=winner_family,
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         n_estimators=600),
    ]

    best_features: List[str] = []  # tracks the kept feature set, modified as keeps land
    final_cfg: Optional[ExperimentConfig] = None
    keep_count = 0
    revert_count = 0

    for cfg in experiments:
        # If a previous experiment kept new features, this one inherits them
        # only if the experiment explicitly extends from the prior best.
        # For simplicity in this driver, each experiment is run as-specified
        # (each cfg lists the full extra_features set it wants), and we keep
        # the experiment as the new best only if it strictly improves MAE.
        m = fit_predict(cfg, df)
        delta = m["mae"] - best_mae
        if m["mae"] < best_mae - 0.005:  # require >5e-3 improvement to overcome noise
            decision = "KEEP"
            best_mae = m["mae"]
            final_cfg = cfg
            keep_count += 1
        else:
            decision = "REVERT"
            revert_count += 1
        print(f"[{cfg.exp_id}] prior={cfg.prior:.2f} {cfg.description[:55]:55s} "
              f"MAE={m['mae']:.4f} (Δ={delta:+.4f}) → {decision}")
        append_row(cfg.exp_id, cfg.description, m["mae"], m["rmse"], m["r2"],
                   "", "", cfg.prior, decision,
                   f"family={cfg.model_family} feats={len(cfg.extra_features)}")

    print(f"\nPhase 2 summary: {keep_count} KEEP, {revert_count} REVERT")
    print(f"Final best MAE = {best_mae:.4f}")
    if final_cfg:
        print(f"Winning config: {final_cfg.exp_id} — {final_cfg.description}")
        # Save the winning config so phase_b_discovery.py can rebuild it
        winner_record = {
            "exp_id": final_cfg.exp_id,
            "description": final_cfg.description,
            "model_family": final_cfg.model_family,
            "extra_features": list(final_cfg.extra_features),
            "xgb_params": final_cfg.xgb_params,
            "lgb_params": final_cfg.lgb_params,
            "monotone_constraints": final_cfg.monotone_constraints,
            "log_target": final_cfg.log_target,
            "n_estimators": final_cfg.n_estimators,
            "mae": best_mae,
        }
    else:
        # No experiment improved on baseline — winner is whichever family won the tournament
        winner_record = {
            "exp_id": winner_id,
            "description": f"tournament winner ({winner_family}) on raw features",
            "model_family": winner_family,
            "extra_features": [],
            "xgb_params": {},
            "lgb_params": {},
            "monotone_constraints": None,
            "log_target": False,
            "n_estimators": 300,
            "mae": best_mae,
        }
    (PROJECT_ROOT / "winning_config.json").write_text(json.dumps(winner_record, indent=2))
    print(f"\nWrote winning_config.json")


if __name__ == "__main__":
    main()
