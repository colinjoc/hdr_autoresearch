"""
hdr_phase25.py — Phase 2.5 composition retest + cross-process transfer
experiments for the welding HDR project.

Three independent follow-up investigations after the main Phase 2 loop:

1. **Compositional retest.** Phase 2 evaluated single-change experiments
   against the running best; it is possible that two changes that both
   individually revert nonetheless combine into a KEEP. Phase 2.5 retries
   the most promising combinations using the winning feature set.

2. **Cross-process transfer (H20 from research_queue.md).** Train the
   winning model on the Gas Metal Arc Welding (GMAW) subset only, then
   test on the Gas Tungsten Arc Welding (GTAW) subset. Compare against
   training on the combined arc-welding data. If the physics-informed
   heat-input feature is universal, the transfer gap should be small.

3. **H1 explicit test.** A direct test of the research-queue claim that
   heat input HI = (60·η·V·I)/(1000·v) alone explains ≥80% of HAZ-width
   variance. Uses linear regression on HI as the sole feature, with
   5-fold cross-validation on the arc-welding subset.

Output:
    results.tsv  — three P25.* rows appended
    Printed summary of transfer MAE on each test condition
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

from hdr_loop import (
    PROJECT_ROOT, RESULTS_TSV, ExperimentConfig, add_features,
    fit_predict, load_dataset, append_row, RAW_FEATURES,
    XGB_DEFAULT,
)
import xgboost as xgb

STEEL_PROCESSES = ("GMAW", "GTAW")


# ---------------------------------------------------------------------------
# 1. Compositional retest
# ---------------------------------------------------------------------------

def compositional_retest(df: pd.DataFrame, best_cfg: ExperimentConfig,
                         best_mae: float):
    """Retry combinations that individually reverted but might compose well."""
    print("\n" + "=" * 60)
    print("PHASE 2.5a: Compositional retest")
    print("=" * 60)
    retests = [
        ExperimentConfig(
            "P25.1", "Compose: HI + t85 + monotone + n=600",
            prior=0.70, mechanism="Stack the best single changes",
            model_family="xgboost",
            extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
            monotone_constraints={"heat_input_kj_mm": 1, "cooling_t85_s_est": 1},
            n_estimators=600),
        ExperimentConfig(
            "P25.2", "Compose: HI + t85 + hi_over_thk + monotone",
            prior=0.65, mechanism="Add physics-derived ratio",
            model_family="xgboost",
            extra_features=["heat_input_kj_mm", "cooling_t85_s_est", "hi_over_thk"],
            monotone_constraints={"heat_input_kj_mm": 1, "cooling_t85_s_est": 1}),
        ExperimentConfig(
            "P25.3", "Compose: HI + t85 + log_target + monotone",
            prior=0.50, mechanism="Stabilise variance + physics",
            model_family="xgboost",
            extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
            monotone_constraints={"heat_input_kj_mm": 1, "cooling_t85_s_est": 1},
            log_target=True),
        ExperimentConfig(
            "P25.4", "Compose: HI + t85 + depth=4 + monotone",
            prior=0.40, mechanism="Regularise + physics",
            model_family="xgboost",
            extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
            monotone_constraints={"heat_input_kj_mm": 1, "cooling_t85_s_est": 1},
            xgb_params={"max_depth": 4}),
        ExperimentConfig(
            "P25.5", "Compose: HI + t85 + depth=4 + n=600 + monotone",
            prior=0.45, mechanism="Both hyperparam tweaks + physics",
            model_family="xgboost",
            extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
            monotone_constraints={"heat_input_kj_mm": 1, "cooling_t85_s_est": 1},
            xgb_params={"max_depth": 4}, n_estimators=600),
        ExperimentConfig(
            "P25.6", "Compose: HI + t85 + lr=0.03 + n=800 + monotone",
            prior=0.40, mechanism="Slow boost + more rounds + physics",
            model_family="xgboost",
            extra_features=["heat_input_kj_mm", "cooling_t85_s_est"],
            monotone_constraints={"heat_input_kj_mm": 1, "cooling_t85_s_est": 1},
            xgb_params={"learning_rate": 0.03}, n_estimators=800),
    ]
    keep = 0
    revert = 0
    winner_cfg = best_cfg
    winner_mae = best_mae
    for cfg in retests:
        m = fit_predict(cfg, df)
        delta = m["mae"] - winner_mae
        threshold = max(0.005, 0.01 * winner_mae)
        if m["mae"] < winner_mae - threshold:
            decision = "KEEP"
            keep += 1
            winner_mae = m["mae"]
            winner_cfg = cfg
        else:
            decision = "REVERT"
            revert += 1
        print(f"  [{cfg.exp_id}] p={cfg.prior:.2f} {cfg.description[:48]:48s} "
              f"MAE={m['mae']:.4f} Δ={delta:+.4f} → {decision}")
        append_row(cfg.exp_id, cfg.description, m["mae"], m["rmse"], m["r2"],
                   "", "", cfg.prior, decision,
                   f"family={cfg.model_family} feats={len(cfg.extra_features)}")
    print(f"\nP25 composition: {keep} KEEP, {revert} REVERT → best MAE={winner_mae:.4f}")
    return winner_cfg, winner_mae


# ---------------------------------------------------------------------------
# 2. Cross-process transfer — GMAW → GTAW
# ---------------------------------------------------------------------------

def cross_process_transfer(df: pd.DataFrame, winning_cfg: ExperimentConfig):
    """Train on GMAW, test on GTAW; compare to full combined training.

    This is H20 from research_queue.md: if heat input is the universal
    feature the textbook scaling predicts, a model fit on GMAW should
    generalise to GTAW within the noise floor.
    """
    print("\n" + "=" * 60)
    print("PHASE 2.5b: Cross-process transfer (H20)")
    print("=" * 60)
    gmaw = df[df["process"] == "GMAW"].reset_index(drop=True)
    gtaw = df[df["process"] == "GTAW"].reset_index(drop=True)
    print(f"  GMAW rows: {len(gmaw)}; GTAW rows: {len(gtaw)}")

    def train_one(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict:
        train_feat = add_features(train_df, winning_cfg.extra_features)
        test_feat = add_features(test_df, winning_cfg.extra_features)
        feature_names = RAW_FEATURES + list(winning_cfg.extra_features)
        X_tr = train_feat[feature_names].values.astype(np.float32)
        X_te = test_feat[feature_names].values.astype(np.float32)
        y_tr = train_feat["haz_width_mm"].values.astype(np.float32)
        y_te = test_feat["haz_width_mm"].values.astype(np.float32)
        params = dict(XGB_DEFAULT)
        params.update(winning_cfg.xgb_params)
        if winning_cfg.monotone_constraints:
            vec = [winning_cfg.monotone_constraints.get(f, 0) for f in feature_names]
            params["monotone_constraints"] = "(" + ",".join(str(v) for v in vec) + ")"
        dtr = xgb.DMatrix(X_tr, label=y_tr)
        dte = xgb.DMatrix(X_te)
        booster = xgb.train(params, dtr, num_boost_round=winning_cfg.n_estimators)
        y_pred = booster.predict(dte)
        return {
            "mae": float(mean_absolute_error(y_te, y_pred)),
            "r2": float(r2_score(y_te, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_te, y_pred))),
        }

    res_g2t = train_one(gmaw, gtaw)
    res_t2g = train_one(gtaw, gmaw)
    # Within-family baseline: 5-fold CV on GTAW alone
    from sklearn.model_selection import KFold
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    gtaw_feat = add_features(gtaw, winning_cfg.extra_features)
    fn = RAW_FEATURES + list(winning_cfg.extra_features)
    X_g = gtaw_feat[fn].values.astype(np.float32)
    y_g = gtaw_feat["haz_width_mm"].values.astype(np.float32)
    all_t, all_p = [], []
    for tr, te in kf.split(X_g):
        params = dict(XGB_DEFAULT)
        params.update(winning_cfg.xgb_params)
        if winning_cfg.monotone_constraints:
            vec = [winning_cfg.monotone_constraints.get(f, 0) for f in fn]
            params["monotone_constraints"] = "(" + ",".join(str(v) for v in vec) + ")"
        dtr = xgb.DMatrix(X_g[tr], label=y_g[tr])
        dte = xgb.DMatrix(X_g[te])
        b = xgb.train(params, dtr, num_boost_round=winning_cfg.n_estimators)
        y_pred = b.predict(dte)
        all_t.extend(y_g[te].tolist())
        all_p.extend(y_pred.tolist())
    in_family = {
        "mae": float(mean_absolute_error(all_t, all_p)),
        "r2": float(r2_score(all_t, all_p)),
        "rmse": float(np.sqrt(mean_squared_error(all_t, all_p))),
    }

    print(f"  train GMAW, test GTAW:   MAE={res_g2t['mae']:.4f}  R²={res_g2t['r2']:.4f}")
    print(f"  train GTAW, test GMAW:   MAE={res_t2g['mae']:.4f}  R²={res_t2g['r2']:.4f}")
    print(f"  GTAW-only 5-fold CV:     MAE={in_family['mae']:.4f}  R²={in_family['r2']:.4f}")
    transfer_gap = res_g2t["mae"] - in_family["mae"]
    rel_gap = transfer_gap / max(in_family["mae"], 1e-6) * 100.0
    verdict = ("CONFIRMED (heat input is universal)"
               if rel_gap < 15.0
               else f"REFUTED (gap = {rel_gap:.1f}% > 15%)")
    print(f"\n  transfer gap (GMAW→GTAW − GTAW own): "
          f"Δ={transfer_gap:+.4f} mm  ({rel_gap:+.1f}%)")
    print(f"  H20 verdict: {verdict}")
    append_row("P25.T1", "Transfer: train GMAW, test GTAW",
               res_g2t["mae"], res_g2t["rmse"], res_g2t["r2"],
               "", "", 0.60, "TRANSFER", "H20 cross-process test")
    append_row("P25.T2", "Transfer: train GTAW, test GMAW",
               res_t2g["mae"], res_t2g["rmse"], res_t2g["r2"],
               "", "", 0.60, "TRANSFER", "H20 reverse-direction")
    append_row("P25.T3", "GTAW-only 5-fold CV (baseline for transfer)",
               in_family["mae"], in_family["rmse"], in_family["r2"],
               "", "", 1.00, "BASELINE", "within-family reference")
    return {
        "gmaw_to_gtaw": res_g2t,
        "gtaw_to_gmaw": res_t2g,
        "gtaw_in_family": in_family,
        "transfer_gap_mm": transfer_gap,
        "relative_gap_pct": rel_gap,
    }


# ---------------------------------------------------------------------------
# 3. H1 explicit test: HI alone predicts HAZ width
# ---------------------------------------------------------------------------

def h1_explicit_test(df: pd.DataFrame):
    """Fit a linear regression using heat input as the sole feature.

    H1 from research_queue.md claims this model should reach R² ≥ 0.80.
    """
    print("\n" + "=" * 60)
    print("PHASE 2.5c: H1 — heat input as single HAZ predictor")
    print("=" * 60)
    steel = df[df["process"].isin(STEEL_PROCESSES)].reset_index(drop=True)
    hi = (steel["efficiency"] * steel["voltage_v"] * steel["current_a"]
          / (steel["travel_mm_s"] * 1000.0)).values.reshape(-1, 1)
    y = steel["haz_width_mm"].values
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    all_t, all_p = [], []
    for tr, te in kf.split(hi):
        m = LinearRegression().fit(hi[tr], y[tr])
        p = m.predict(hi[te])
        all_t.extend(y[te].tolist())
        all_p.extend(p.tolist())
    r2 = r2_score(all_t, all_p)
    mae = mean_absolute_error(all_t, all_p)
    rmse = float(np.sqrt(mean_squared_error(all_t, all_p)))
    verdict = "CONFIRMED" if r2 >= 0.80 else "REFUTED"
    print(f"  linear HI → HAZ  MAE={mae:.3f}  R²={r2:.4f}  → {verdict}")
    append_row("P25.H1", "H1 linear HI-only → HAZ width",
               mae, rmse, r2, "", "", 0.80, verdict,
               "research_queue H1 explicit test")
    return {"mae": mae, "r2": r2, "verdict": verdict}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Load winning config from hdr_loop.py output
    cfg_path = PROJECT_ROOT / "winning_config.json"
    cfg_json = json.loads(cfg_path.read_text())
    # Convert JSON back to ExperimentConfig
    winning_cfg = ExperimentConfig(
        exp_id=cfg_json["exp_id"],
        description=cfg_json["description"],
        prior=0.60, mechanism="phase 2 winner",
        model_family=cfg_json["model_family"],
        extra_features=list(cfg_json["extra_features"]),
        xgb_params=cfg_json.get("xgb_params") or {},
        lgb_params=cfg_json.get("lgb_params") or {},
        sklearn_kwargs=cfg_json.get("sklearn_kwargs") or {},
        monotone_constraints=cfg_json.get("monotone_constraints"),
        log_target=bool(cfg_json.get("log_target", False)),
        n_estimators=int(cfg_json.get("n_estimators", 300)),
    )
    best_mae = float(cfg_json["mae"])
    print(f"loaded winning config: {winning_cfg.exp_id} MAE={best_mae:.4f}")

    df = load_dataset()
    # 1. Composition retest
    new_cfg, new_mae = compositional_retest(df, winning_cfg, best_mae)
    # If composition found a better model, persist it
    if new_mae < best_mae:
        updated = dict(cfg_json)
        updated.update({
            "exp_id": new_cfg.exp_id,
            "description": new_cfg.description,
            "extra_features": list(new_cfg.extra_features),
            "xgb_params": new_cfg.xgb_params,
            "monotone_constraints": new_cfg.monotone_constraints,
            "log_target": new_cfg.log_target,
            "n_estimators": new_cfg.n_estimators,
            "mae": new_mae,
        })
        cfg_path.write_text(json.dumps(updated, indent=2))
        print(f"  updated winning_config.json → {new_cfg.exp_id} MAE={new_mae:.4f}")
        winning_cfg = new_cfg
    else:
        print("  composition did not improve; keeping previous winner")

    # 2. Cross-process transfer
    transfer = cross_process_transfer(df, winning_cfg)

    # 3. Explicit H1 linear test
    h1 = h1_explicit_test(df)

    # Persist the transfer + H1 results next to winning_config.json
    summary = {
        "winning_exp": winning_cfg.exp_id,
        "winning_mae": float(best_mae) if new_mae >= best_mae else float(new_mae),
        "transfer": transfer,
        "h1_test": h1,
    }
    (PROJECT_ROOT / "phase25_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nwrote phase25_summary.json")


if __name__ == "__main__":
    main()
