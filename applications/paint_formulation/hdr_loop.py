"""
hdr_loop.py — Phase 1 tournament + Phase 2 HDR loop for paint formulation.

Phase 1 runs a 4-way tournament across fundamentally different model families
(XGBoost, LightGBM, ExtraTrees, Ridge regression) on the raw 5-feature set,
for each of the four prediction targets.

Phase 2 runs a long series of single-change experiments that add physics-
informed features, log-ratio composition features, monotonicity constraints,
and hyperparameter adjustments. Each experiment is one change against the
current best on a specific target.

Outputs:
  - Appends every experiment result to results.tsv
  - Writes winning_config.json with per-target winning configurations

Usage:
    python hdr_loop.py
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

from model import (
    PaintFormulationModel, RAW_FEATURES, TARGET_COLS, add_features, featurize,
)

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_TSV = PROJECT_ROOT / "results.tsv"
DATA_PATH = PROJECT_ROOT / "data" / "paint.csv"
N_FOLDS = 5
RANDOM_SEED = 42

# Noise floors (empirical) — experiments must improve by at least this much
# to count as a KEEP. Calibrated from baseline noise estimates.
NOISE_FLOOR = {
    "scratch_hardness_N": 0.02,
    "gloss_60":           0.20,
    "hiding_power_pct":   0.05,
    "cupping_mm":         0.03,
}


def load_dataset() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


# ---------------------------------------------------------------------------
# Experiment configuration
# ---------------------------------------------------------------------------

@dataclass
class ExperimentConfig:
    exp_id: str
    description: str
    target: str
    prior: float
    mechanism: str
    model_family: str = "xgboost"   # xgboost / lightgbm / extratrees / ridge / gp
    extra_features: List[str] = field(default_factory=list)
    xgb_params: Dict[str, Any] = field(default_factory=dict)
    lgb_params: Dict[str, Any] = field(default_factory=dict)
    sklearn_kwargs: Dict[str, Any] = field(default_factory=dict)
    gp_kernel: str = "matern"
    monotone_constraints: Optional[Dict[str, int]] = None
    log_target: bool = False
    n_estimators: int = 300

    def to_model_config(self) -> Dict[str, Any]:
        cfg: Dict[str, Any] = {
            "model_family": self.model_family,
            "n_estimators": self.n_estimators,
            "log_target": self.log_target,
        }
        if self.model_family == "xgboost":
            xgb_params = {
                "objective": "reg:squarederror",
                "max_depth": 5,
                "learning_rate": 0.05,
                "min_child_weight": 2,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "verbosity": 0,
            }
            xgb_params.update(self.xgb_params)
            cfg["xgb_params"] = xgb_params
        elif self.model_family == "lightgbm":
            cfg["lgb_params"] = dict(self.lgb_params)
        elif self.model_family in ("extratrees", "randomforest"):
            cfg["sklearn_kwargs"] = dict(self.sklearn_kwargs)
        elif self.model_family == "ridge":
            cfg["sklearn_kwargs"] = dict(self.sklearn_kwargs)
        elif self.model_family == "gp":
            cfg["gp_kernel"] = self.gp_kernel
        if self.monotone_constraints:
            cfg["monotone_constraints"] = dict(self.monotone_constraints)
        return cfg


def run_experiment(cfg: ExperimentConfig, df: pd.DataFrame) -> Dict[str, float]:
    """5-fold cross-validation of a single experiment."""
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    y_true_all, y_pred_all = [], []
    for train_idx, test_idx in kf.split(df):
        model = PaintFormulationModel(
            target=cfg.target,
            extra_features=cfg.extra_features,
            config=cfg.to_model_config(),
        )
        X_tr, y_tr = model.featurize(df.iloc[train_idx])
        X_te, y_te = model.featurize(df.iloc[test_idx])
        model.train(X_tr, y_tr)
        y_pred = model.predict(X_te)
        y_true_all.extend(y_te.tolist())
        y_pred_all.extend(y_pred.tolist())
    y_true = np.array(y_true_all)
    y_pred = np.array(y_pred_all)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def append_row(exp_id: str, description: str, target: str,
               mae: float, rmse: float, r2: float,
               prior: float, decision: str, notes: str) -> None:
    with RESULTS_TSV.open("a") as fh:
        fh.write(
            f"{exp_id}\t{description}\t{target}\t{mae:.4f}\t{rmse:.4f}\t"
            f"{r2:.4f}\t{prior:.2f}\t{decision}\t{notes}\n"
        )


# ---------------------------------------------------------------------------
# Phase 1 tournament
# ---------------------------------------------------------------------------

def phase1_tournament(df: pd.DataFrame) -> Dict[str, str]:
    """Tournament of 4 fundamentally different model families for each target.

    Returns {target -> winning model family}.
    """
    winners: Dict[str, str] = {}
    print("=" * 70)
    print("PHASE 1: Model family tournament (4 families x 4 targets)")
    print("=" * 70)
    for target in TARGET_COLS:
        print(f"\n-- target: {target} --")
        candidates = [
            ExperimentConfig(
                exp_id=f"T01_{target}",
                description="XGBoost on raw features",
                target=target,
                prior=0.50,
                mechanism="established gradient-boosted baseline",
                model_family="xgboost",
            ),
            ExperimentConfig(
                exp_id=f"T02_{target}",
                description="LightGBM on raw features",
                target=target,
                prior=0.50,
                mechanism="LightGBM often beats XGBoost on small tabular data",
                model_family="lightgbm",
                n_estimators=300,
                lgb_params={"learning_rate": 0.05, "num_leaves": 15, "min_data_in_leaf": 3},
            ),
            ExperimentConfig(
                exp_id=f"T03_{target}",
                description="ExtraTrees on raw features",
                target=target,
                prior=0.60,
                mechanism="bagging beats boosting for small N (<100 samples)",
                model_family="extratrees",
                n_estimators=400,
            ),
            ExperimentConfig(
                exp_id=f"T04_{target}",
                description="Ridge regression on raw features (linear baseline)",
                target=target,
                prior=0.20,
                mechanism="if Ridge wins, relationship is mostly linear - publish this",
                model_family="ridge",
                sklearn_kwargs={"alpha": 1.0},
            ),
        ]
        scores: Dict[str, float] = {}
        for c in candidates:
            m = run_experiment(c, df)
            scores[c.model_family] = m["mae"]
            print(f"  [{c.exp_id}] {c.model_family:12s} "
                  f"MAE={m['mae']:.4f}  R²={m['r2']:+.3f}  {c.description}")
            append_row(c.exp_id, c.description, target, m["mae"], m["rmse"], m["r2"],
                       c.prior, "TOURNAMENT", f"family={c.model_family}")
        winner = min(scores, key=lambda k: scores[k])
        winners[target] = winner
        print(f"  winner: {winner}  (MAE={scores[winner]:.4f})")
    return winners


# ---------------------------------------------------------------------------
# Phase 2 HDR loop
# ---------------------------------------------------------------------------

# The canonical physics-informed feature set. Each entry is a candidate
# feature to add.
CANDIDATE_FEATURES = [
    "binder_frac",
    "pvc_proxy",
    "pvc_cpvc_dist",
    "binder_pigment_ratio",
    "matting_pigment_ratio",
    "hdi_frac",
    "crosslink_x_cyc",
    "crosslink_sq",
    "matting_agent_sq",
    "pigment_paste_sq",
    "log_thickness",
    "inv_thickness",
    "thickness_sq",
    "thickness_x_matting",
    "thickness_x_pigment",
    "lr_crosslink",
    "lr_cyc",
    "lr_matting",
    "lr_pigment",
    "crosslink_x_matting",
    "cyc_x_matting",
    "pigment_x_matting",
]


def build_phase2_experiments(winners: Dict[str, str]) -> List[ExperimentConfig]:
    """Build the Phase 2 experiment list. Each experiment tests ONE change
    against the baseline for a given target. The HDR driver evaluates each
    one and keeps only if it improves on the running best for that target.
    """
    exps: List[ExperimentConfig] = []
    counter = 0
    def make_id():
        nonlocal counter
        counter += 1
        return f"E{counter:03d}"

    # --- Group A: single physics-informed feature for each target ---
    single_feature_priors = {
        "pvc_proxy":              (0.70, "PVC dominates gloss via void formation"),
        "pvc_cpvc_dist":          (0.65, "distance from CPVC drives gloss phase change"),
        "binder_frac":            (0.50, "binder fraction is the complement of pigment"),
        "binder_pigment_ratio":   (0.50, "literature rule for gloss/hardness balance"),
        "matting_pigment_ratio":  (0.40, "matting agents dominate gloss Sobol"),
        "hdi_frac":               (0.35, "HDI fraction complements IPDI (redundant)"),
        "crosslink_x_cyc":        (0.45, "crosslink interacts with isocyanate type"),
        "crosslink_sq":           (0.30, "quadratic crosslink response plausible"),
        "matting_agent_sq":       (0.40, "matting effect saturates (nonlinear)"),
        "pigment_paste_sq":       (0.40, "pigment loading saturates"),
        "log_thickness":          (0.45, "gloss depends on log thickness (scaling)"),
        "inv_thickness":          (0.30, "thickness inverse may help hiding power"),
        "thickness_sq":           (0.30, "quadratic thickness for cupping test"),
        "thickness_x_matting":    (0.45, "thickness*matting is the top 2 gloss Sobol pair"),
        "thickness_x_pigment":    (0.40, "thickness*pigment important for hiding"),
        "lr_crosslink":           (0.40, "Aitchison log-ratio - simplex aware"),
        "lr_cyc":                 (0.40, "Aitchison log-ratio for cyc isocyanate"),
        "lr_matting":              (0.50, "Aitchison log-ratio for matting agent"),
        "lr_pigment":              (0.45, "Aitchison log-ratio for pigment"),
        "crosslink_x_matting":    (0.35, "interaction: matting-agent cure interference"),
        "cyc_x_matting":          (0.30, "interaction: IPDI + silica bulk effect"),
        "pigment_x_matting":      (0.40, "interaction: pigment+matting both occupy solids"),
    }

    for target in TARGET_COLS:
        family = winners[target]
        for feat_name, (prior, mech) in single_feature_priors.items():
            exps.append(ExperimentConfig(
                exp_id=make_id(),
                description=f"{target}: add {feat_name}",
                target=target,
                prior=prior,
                mechanism=mech,
                model_family=family,
                extra_features=[feat_name],
            ))

    # --- Group B: physics-informed multi-feature sets per target ---
    for target in TARGET_COLS:
        family = winners[target]
        exps.append(ExperimentConfig(
            exp_id=make_id(),
            description=f"{target}: PVC suite (pvc_proxy + pvc_cpvc_dist + binder_frac)",
            target=target,
            prior=0.60,
            mechanism="full PVC/CPVC feature suite",
            model_family=family,
            extra_features=["pvc_proxy", "pvc_cpvc_dist", "binder_frac"],
        ))
        exps.append(ExperimentConfig(
            exp_id=make_id(),
            description=f"{target}: Aitchison log-ratio suite",
            target=target,
            prior=0.55,
            mechanism="simplex-aware compositional featurisation",
            model_family=family,
            extra_features=["lr_crosslink", "lr_cyc", "lr_matting", "lr_pigment"],
        ))
        exps.append(ExperimentConfig(
            exp_id=make_id(),
            description=f"{target}: thickness interactions (log+x_matting+x_pigment)",
            target=target,
            prior=0.55,
            mechanism="thickness dominates gloss/cupping Sobol",
            model_family=family,
            extra_features=["log_thickness", "thickness_x_matting", "thickness_x_pigment"],
        ))
        exps.append(ExperimentConfig(
            exp_id=make_id(),
            description=f"{target}: quadratic + interaction suite",
            target=target,
            prior=0.45,
            mechanism="polynomial terms capture local curvature",
            model_family=family,
            extra_features=["crosslink_sq", "matting_agent_sq", "pigment_paste_sq",
                             "crosslink_x_matting", "pigment_x_matting"],
        ))

    # --- Group C: hyperparameter experiments on the best XGBoost setting ---
    # Use gloss as the representative target because XGBoost is strong there
    hp_target = "gloss_60"
    hp_feats = ["log_thickness", "thickness_x_matting"]
    for lr, n_est, depth, prior, mech in [
        (0.03, 500, 5, 0.35, "lower LR + more rounds often helps small N"),
        (0.10, 300, 4, 0.30, "higher LR + shallower trees regularise"),
        (0.05, 600, 4, 0.30, "more rounds + shallower trees"),
        (0.05, 300, 3, 0.35, "very shallow trees for small N"),
        (0.05, 300, 7, 0.20, "deeper trees capture interactions but overfit risk"),
    ]:
        exps.append(ExperimentConfig(
            exp_id=make_id(),
            description=f"gloss_60: xgb lr={lr} n={n_est} d={depth}",
            target=hp_target,
            prior=prior,
            mechanism=mech,
            model_family="xgboost",
            extra_features=hp_feats,
            xgb_params={"learning_rate": lr, "max_depth": depth},
            n_estimators=n_est,
        ))

    # --- Group D: monotonicity constraints for XGBoost ---
    for target, mono, mech in [
        ("gloss_60", {"matting_agent": -1, "pigment_paste": -1},
         "gloss monotonically decreases with pigment and matting agent"),
        ("scratch_hardness_N", {"matting_agent": 1, "crosslink": 1},
         "scratch hardness increases with matting agent and crosslink density"),
        ("hiding_power_pct", {"pigment_paste": 1},
         "hiding power increases with pigment loading"),
        ("cupping_mm", {"thickness_um": 1},
         "cupping depth increases with thicker films (more material to deform)"),
    ]:
        exps.append(ExperimentConfig(
            exp_id=make_id(),
            description=f"{target}: monotone constraints {mono}",
            target=target,
            prior=0.55,
            mechanism=mech,
            model_family="xgboost",
            extra_features=["pvc_proxy", "log_thickness", "thickness_x_matting"],
            monotone_constraints=mono,
        ))

    # --- Group E: log target transform ---
    for target, prior in [
        ("scratch_hardness_N", 0.30),
        ("gloss_60",           0.30),
        ("hiding_power_pct",   0.25),
        ("cupping_mm",         0.35),
    ]:
        exps.append(ExperimentConfig(
            exp_id=make_id(),
            description=f"{target}: log target transform",
            target=target,
            prior=prior,
            mechanism="log target stabilises variance on skewed distributions",
            model_family=winners[target],
            extra_features=["log_thickness"],
            log_target=True,
        ))

    # --- Group F: tree count sweep for ExtraTrees (winner for small N) ---
    for target in TARGET_COLS:
        if winners[target] != "extratrees":
            continue
        for n, prior in [(100, 0.25), (200, 0.30), (600, 0.35), (1000, 0.30)]:
            exps.append(ExperimentConfig(
                exp_id=make_id(),
                description=f"{target}: ExtraTrees n={n}",
                target=target,
                prior=prior,
                mechanism=f"vary ExtraTrees n_estimators={n}",
                model_family="extratrees",
                n_estimators=n,
            ))

    # --- Group G: GP (Gaussian Process) experiments - published baseline ---
    # The published Zenodo paper uses a GP. We replicate it as a control so
    # our final comparison is honest.
    for target in TARGET_COLS:
        for kern, prior in [("matern", 0.45), ("rbf", 0.40), ("rbf_dot", 0.35)]:
            exps.append(ExperimentConfig(
                exp_id=make_id(),
                description=f"{target}: GP({kern}) - published baseline family",
                target=target,
                prior=prior,
                mechanism="Zenodo paper uses GP with Matern/RBF+DotProduct kernels",
                model_family="gp",
                gp_kernel=kern,
            ))

    return exps


# ---------------------------------------------------------------------------
# Phase 2 driver
# ---------------------------------------------------------------------------

def phase2_loop(df: pd.DataFrame, baseline: Dict[str, Dict[str, float]],
                winners: Dict[str, str]) -> Dict[str, Dict]:
    """Run every experiment in build_phase2_experiments, keeping per-target
    winners based on >noise_floor improvement on MAE."""
    experiments = build_phase2_experiments(winners)
    # Per-target best record
    best: Dict[str, Dict] = {}
    for t in TARGET_COLS:
        best[t] = {
            "mae": baseline[t]["mae"],
            "rmse": baseline[t]["rmse"],
            "r2": baseline[t]["r2"],
            "config": ExperimentConfig(
                exp_id="E00",
                description="Phase 0.5 baseline XGBoost",
                target=t,
                prior=1.0,
                mechanism="baseline",
                model_family="xgboost",
            ),
        }
    # Also consider tournament winners as starting point
    # (re-run each tournament winner one time to record in consistent format)
    keep_count = 0
    revert_count = 0
    per_target_counts = {t: [0, 0] for t in TARGET_COLS}  # [keep, revert]
    print("\n" + "=" * 70)
    print(f"PHASE 2: HDR loop ({len(experiments)} single-change experiments)")
    print("=" * 70)
    for i, cfg in enumerate(experiments, 1):
        t0 = time.time()
        try:
            m = run_experiment(cfg, df)
        except Exception as e:
            print(f"[{cfg.exp_id}] {cfg.target}: ERROR {e}")
            append_row(cfg.exp_id, cfg.description, cfg.target,
                       9999.0, 9999.0, -9999.0, cfg.prior, "ERROR", str(e)[:200])
            continue
        current_best_mae = best[cfg.target]["mae"]
        delta = m["mae"] - current_best_mae
        noise = NOISE_FLOOR.get(cfg.target, 0.01)
        if m["mae"] < current_best_mae - noise:
            decision = "KEEP"
            best[cfg.target] = {
                "mae": m["mae"],
                "rmse": m["rmse"],
                "r2": m["r2"],
                "config": cfg,
            }
            keep_count += 1
            per_target_counts[cfg.target][0] += 1
        else:
            decision = "REVERT"
            revert_count += 1
            per_target_counts[cfg.target][1] += 1
        elapsed = time.time() - t0
        print(f"[{cfg.exp_id}] ({i:3d}/{len(experiments)}) "
              f"{cfg.target[:10]:10s} MAE={m['mae']:.4f} "
              f"(Δ={delta:+.4f}) → {decision}  {elapsed:.1f}s  {cfg.description[:45]}")
        append_row(cfg.exp_id, cfg.description, cfg.target,
                   m["mae"], m["rmse"], m["r2"], cfg.prior, decision,
                   f"family={cfg.model_family} feats={len(cfg.extra_features)}")

    print("\n" + "-" * 70)
    print(f"Phase 2 summary: {keep_count} KEEP, {revert_count} REVERT "
          f"(total {len(experiments)} experiments)")
    for t, (k, r) in per_target_counts.items():
        print(f"  {t:20s} keep={k:3d} revert={r:3d}  best MAE={best[t]['mae']:.4f}")
    return best


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    df = load_dataset()
    print(f"Dataset: {len(df)} samples, targets: {TARGET_COLS}")

    # --- Establish baseline for each target ---
    baseline: Dict[str, Dict[str, float]] = {}
    print("\n" + "=" * 70)
    print("PHASE 0.5: Baseline audit")
    print("=" * 70)
    for target in TARGET_COLS:
        cfg = ExperimentConfig(
            exp_id="E00",
            description="Baseline XGBoost on raw 5 features",
            target=target,
            prior=1.0,
            mechanism="established baseline",
            model_family="xgboost",
        )
        m = run_experiment(cfg, df)
        baseline[target] = m
        print(f"  [{target:20s}] MAE={m['mae']:.4f}  RMSE={m['rmse']:.4f}  R²={m['r2']:+.4f}")

    # --- Phase 1 tournament ---
    winners = phase1_tournament(df)
    print(f"\nPhase 1 winners: {winners}")

    # --- Phase 2 HDR loop ---
    best = phase2_loop(df, baseline, winners)

    # --- Persist winning config per target ---
    out = {}
    for t in TARGET_COLS:
        cfg = best[t]["config"]
        out[t] = {
            "exp_id": cfg.exp_id,
            "description": cfg.description,
            "model_family": cfg.model_family,
            "extra_features": list(cfg.extra_features),
            "xgb_params": dict(cfg.xgb_params),
            "lgb_params": dict(cfg.lgb_params),
            "sklearn_kwargs": dict(cfg.sklearn_kwargs),
            "gp_kernel": cfg.gp_kernel,
            "monotone_constraints": cfg.monotone_constraints,
            "log_target": cfg.log_target,
            "n_estimators": cfg.n_estimators,
            "cv_mae": best[t]["mae"],
            "cv_rmse": best[t]["rmse"],
            "cv_r2": best[t]["r2"],
        }
    (PROJECT_ROOT / "winning_config.json").write_text(json.dumps(out, indent=2))
    print(f"\nWrote winning_config.json:")
    for t in TARGET_COLS:
        print(f"  {t:20s} -> {out[t]['model_family']:12s} "
              f"+ {len(out[t]['extra_features'])} feats  "
              f"MAE={out[t]['cv_mae']:.4f}  R²={out[t]['cv_r2']:+.4f}")


if __name__ == "__main__":
    main()
