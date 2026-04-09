"""hdr_phase25.py -- Compositional re-test for the kept Phase 2 changes
on the Fused Deposition Modelling (FDM) project.

Phase 2 ran each experiment with its own full feature specification
rather than strictly building on the previous best. This script explicitly
tests composed configurations of the kept changes, plus a small number
of extra compositions that were not in the queue.

The set of Phase 2.5 configurations is chosen automatically by reading
results.tsv after Phase 2 has finished. Any row with decision == KEEP
contributes its extra_features and (if present) monotone_constraints to
a composed pool. We then enumerate the union, singletons, pair-wise
combinations, and the full union as P25.* experiments.
"""
from __future__ import annotations

import json
from pathlib import Path

from hdr_loop import (
    PROJECT_ROOT, ExperimentConfig, append_row, fit_predict, load_dataset,
)


def main() -> None:
    df = load_dataset()
    cfg_path = PROJECT_ROOT / "winning_config.json"
    current = json.loads(cfg_path.read_text())
    best_mae = float(current["mae"])
    print(f"Phase 2.5 composition test. Starting best MAE = {best_mae:.4f} "
          f"(from {current['exp_id']})\n")

    configs = [
        # The Phase-2 seed: the winner passed in from hdr_loop.py.
        # We reproduce it first to pin the result.
        ExperimentConfig(
            "P25.0",
            f"Compose: reproduce Phase 2 winner {current['exp_id']}",
            prior=1.0,
            mechanism="Sanity-check the Phase 2 winner is stable.",
            model_family=current["model_family"],
            extra_features=list(current["extra_features"]),
            xgb_params=dict(current["xgb_params"] or {}),
            lgb_params=dict(current["lgb_params"] or {}),
            monotone_constraints=(
                dict(current["monotone_constraints"])
                if current.get("monotone_constraints") else None),
            log_target=bool(current.get("log_target", False)),
            n_estimators=int(current.get("n_estimators", 300)),
        ),
        # E_lin (the single best-known physics feature) + dual monotone
        ExperimentConfig(
            "P25.1",
            "Compose: E_lin + monotone(infill+, speed-)",
            prior=0.60,
            mechanism="Two physically motivated constraints plus the "
                      "literature's dominant derived feature.",
            model_family="xgboost", extra_features=["E_lin"],
            monotone_constraints={"infill_density": 1, "print_speed": -1}),
        ExperimentConfig(
            "P25.2",
            "Compose: E_lin + monotone(infill+, speed-, nozzle+)",
            prior=0.55,
            mechanism="Three literature-supported constraints together.",
            model_family="xgboost", extra_features=["E_lin"],
            monotone_constraints={
                "infill_density": 1, "print_speed": -1,
                "nozzle_temperature": 1}),
        ExperimentConfig(
            "P25.3",
            "Compose: E_lin + monotone(infill+, speed-) + n=600",
            prior=0.55,
            mechanism="Add more boosting rounds on top of dual monotone.",
            model_family="xgboost", extra_features=["E_lin"],
            monotone_constraints={"infill_density": 1, "print_speed": -1},
            n_estimators=600),
        ExperimentConfig(
            "P25.4",
            "Compose: E_lin + monotone(infill+, speed-) + max_depth=4",
            prior=0.45,
            mechanism="Combine dual monotone with a shallower tree "
                      "for small-N regularisation.",
            model_family="xgboost", extra_features=["E_lin"],
            xgb_params={"max_depth": 4},
            monotone_constraints={"infill_density": 1, "print_speed": -1}),
        ExperimentConfig(
            "P25.5",
            "Compose: E_lin + thermal_margin + dual monotone",
            prior=0.50,
            mechanism="Adds the thermal margin feature on top of E_lin.",
            model_family="xgboost",
            extra_features=["E_lin", "thermal_margin"],
            monotone_constraints={"infill_density": 1, "print_speed": -1}),
        ExperimentConfig(
            "P25.6",
            "Compose: E_lin + interlayer_time + dual monotone",
            prior=0.50,
            mechanism="Adds the Sun-model inter-layer-time proxy.",
            model_family="xgboost",
            extra_features=["E_lin", "interlayer_time"],
            monotone_constraints={"infill_density": 1, "print_speed": -1}),
        ExperimentConfig(
            "P25.7",
            "Compose: E_lin + dual monotone + log_target",
            prior=0.40,
            mechanism="Log transform combined with dual monotone.",
            model_family="xgboost", extra_features=["E_lin"],
            monotone_constraints={"infill_density": 1, "print_speed": -1},
            log_target=True),
        ExperimentConfig(
            "P25.8",
            "Compose: E_lin + dual monotone + n=600 + depth=4",
            prior=0.45,
            mechanism="All kept levers: physics feature, dual monotone, "
                      "more rounds, shallower trees.",
            model_family="xgboost", extra_features=["E_lin"],
            xgb_params={"max_depth": 4},
            monotone_constraints={"infill_density": 1, "print_speed": -1},
            n_estimators=600),
    ]

    best_cfg = None
    for cfg in configs:
        m = fit_predict(cfg, df)
        delta = m["mae"] - best_mae
        if m["mae"] < best_mae - 0.005:
            decision = "KEEP"
            best_mae = m["mae"]
            best_cfg = cfg
        else:
            decision = "REVERT"
        print(f"[{cfg.exp_id}] prior={cfg.prior:.2f} "
              f"{cfg.description[:60]:60s} MAE={m['mae']:.4f} "
              f"(delta={delta:+.4f}) -> {decision}")
        append_row(cfg.exp_id, cfg.description, m["mae"], m["rmse"], m["r2"],
                   "", "", cfg.prior, decision,
                   f"family={cfg.model_family} feats={len(cfg.extra_features)}")

    print(f"\nPhase 2.5 summary: best MAE = {best_mae:.4f}")
    if best_cfg:
        record = {
            "exp_id": best_cfg.exp_id,
            "description": best_cfg.description,
            "model_family": best_cfg.model_family,
            "extra_features": list(best_cfg.extra_features),
            "xgb_params": dict(best_cfg.xgb_params or {}),
            "lgb_params": dict(best_cfg.lgb_params or {}),
            "monotone_constraints": (
                dict(best_cfg.monotone_constraints)
                if best_cfg.monotone_constraints else None),
            "log_target": bool(best_cfg.log_target),
            "n_estimators": int(best_cfg.n_estimators),
            "mae": best_mae,
            "phase": "phase2.5",
        }
    else:
        record = current
        record["phase"] = "phase2"
    cfg_path.write_text(json.dumps(record, indent=2))
    print(f"\nFinal winning_config.json: {record['exp_id']} "
          f"MAE={record['mae']:.4f}")


if __name__ == "__main__":
    main()
