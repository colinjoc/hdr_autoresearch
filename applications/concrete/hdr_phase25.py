"""
hdr_phase25.py — composition test for the kept Phase 2 changes.

Phase 2 ran each experiment with its own extra_features spec rather than
strictly building on the previous best. This script explicitly tests the
composed configurations to verify the actual best.

Configs tested:
  P25.1  baseline + wb_ratio
  P25.2  baseline + wb_ratio + scm_pct
  P25.3  baseline + wb_ratio + scm_pct + monotone(cement)
  P25.4  baseline + wb_ratio + scm_pct + n_estimators=600
  P25.5  baseline + wb_ratio + scm_pct + monotone(cement) + n=600
  P25.6  baseline + log_age + wb_ratio + scm_pct + monotone(cement) + n=600
  P25.7  the full E20 feature set + monotone(cement) + n=600
  P25.8  the full E20 feature set + monotone(cement) + n=900
"""
from hdr_loop import ExperimentConfig, fit_predict, load_dataset, append_row
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

def main():
    df = load_dataset()

    configs = [
        ExperimentConfig("P25.1", "Compose: baseline + wb_ratio",
                         prior=0.85, mechanism="Verify wb_ratio in isolation",
                         model_family="xgboost", extra_features=["wb_ratio"]),
        ExperimentConfig("P25.2", "Compose: baseline + wb_ratio + scm_pct",
                         prior=0.70, mechanism="Verify both kept features together",
                         model_family="xgboost", extra_features=["wb_ratio", "scm_pct"]),
        ExperimentConfig("P25.3", "Compose: baseline + wb+scm + monotone(cement)",
                         prior=0.70, mechanism="Add the monotone constraint to the wb+scm pair",
                         model_family="xgboost", extra_features=["wb_ratio", "scm_pct"],
                         monotone_constraints={"cement": 1}),
        ExperimentConfig("P25.4", "Compose: baseline + wb+scm + n=600",
                         prior=0.65, mechanism="Test more rounds with the kept feature pair",
                         model_family="xgboost", extra_features=["wb_ratio", "scm_pct"],
                         n_estimators=600),
        ExperimentConfig("P25.5", "Compose: baseline + wb+scm + monotone + n=600",
                         prior=0.70, mechanism="All four kept changes combined",
                         model_family="xgboost", extra_features=["wb_ratio", "scm_pct"],
                         monotone_constraints={"cement": 1}, n_estimators=600),
        ExperimentConfig("P25.6", "Compose: + log_age + wb+scm + monotone + n=600",
                         prior=0.50, mechanism="Add log_age to the full combination (log_age was reverted alone)",
                         model_family="xgboost",
                         extra_features=["log_age", "wb_ratio", "scm_pct"],
                         monotone_constraints={"cement": 1}, n_estimators=600),
        ExperimentConfig("P25.7", "Compose: E20 features + monotone(cement) + n=600",
                         prior=0.55, mechanism="Add monotone to the E20 winner",
                         model_family="xgboost",
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         monotone_constraints={"cement": 1}, n_estimators=600),
        ExperimentConfig("P25.8", "Compose: E20 features + monotone(cement) + n=900",
                         prior=0.40, mechanism="Even more rounds",
                         model_family="xgboost",
                         extra_features=["log_age", "wb_ratio", "scm_pct", "binder_total", "sp_per_binder"],
                         monotone_constraints={"cement": 1}, n_estimators=900),
    ]

    best_mae = 2.6419  # from Phase 2 winner E20
    best_cfg = None
    print(f"Starting from Phase 2 best: MAE = {best_mae:.4f}\n")

    for cfg in configs:
        m = fit_predict(cfg, df)
        delta = m["mae"] - best_mae
        if m["mae"] < best_mae - 0.005:
            decision = "KEEP"
            best_mae = m["mae"]
            best_cfg = cfg
        else:
            decision = "REVERT"
        print(f"[{cfg.exp_id}] prior={cfg.prior:.2f} {cfg.description[:60]:60s} "
              f"MAE={m['mae']:.4f} (Δ={delta:+.4f}) → {decision}")
        append_row(cfg.exp_id, cfg.description, m["mae"], m["rmse"], m["r2"],
                   "", "", cfg.prior, decision,
                   f"family={cfg.model_family} feats={len(cfg.extra_features)}")

    print(f"\nPhase 2.5 summary: best MAE = {best_mae:.4f}")
    if best_cfg:
        winner = {
            "exp_id": best_cfg.exp_id,
            "description": best_cfg.description,
            "model_family": best_cfg.model_family,
            "extra_features": list(best_cfg.extra_features),
            "xgb_params": best_cfg.xgb_params,
            "lgb_params": best_cfg.lgb_params,
            "monotone_constraints": best_cfg.monotone_constraints,
            "log_target": best_cfg.log_target,
            "n_estimators": best_cfg.n_estimators,
            "mae": best_mae,
        }
    else:
        # Phase 2.5 didn't beat Phase 2; load Phase 2 winner
        winner = json.loads((PROJECT_ROOT / "winning_config.json").read_text())
    (PROJECT_ROOT / "winning_config.json").write_text(json.dumps(winner, indent=2))
    print(f"\nFinal winning_config.json updated: {winner['exp_id']} MAE={winner['mae']:.4f}")


if __name__ == "__main__":
    main()
