"""
hdr_phase25.py — Phase 2.5 extended HDR loop.

After the Phase 2 loop plateaued, this second round tests:
  - Multi-feature combinations (previously only singletons were explored
    for several targets because early KEEPs locked in a single feature)
  - Tighter hyperparameter grid around the winning models
  - Model family re-tournaments against the now-refined feature sets
  - Cross-target feature transfer: a feature that helped gloss may help
    scratch-hardness too

Every experiment is still a single change against the current winning
config for its target. Results append to results.tsv with exp_ids
prefixed "P25_".
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd

from hdr_loop import (
    ExperimentConfig, run_experiment, append_row, load_dataset,
    NOISE_FLOOR,
)
from model import TARGET_COLS

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "winning_config.json"


def load_winning() -> Dict:
    return json.loads(CONFIG_PATH.read_text())


def cfg_from_dict(target: str, desc: str, d: Dict, exp_id: str,
                  prior: float, mechanism: str, **overrides) -> ExperimentConfig:
    """Build an ExperimentConfig from a winning_config.json entry plus
    overrides. This is how we mutate the current best by exactly ONE change."""
    # Start from current best as the template
    template = dict(
        model_family=d["model_family"],
        extra_features=list(d["extra_features"]),
        xgb_params=dict(d.get("xgb_params") or {}),
        lgb_params=dict(d.get("lgb_params") or {}),
        sklearn_kwargs=dict(d.get("sklearn_kwargs") or {}),
        gp_kernel=d.get("gp_kernel", "matern"),
        monotone_constraints=d.get("monotone_constraints"),
        log_target=d.get("log_target", False),
        n_estimators=int(d.get("n_estimators", 300)),
    )
    # Apply overrides
    template.update(overrides)
    return ExperimentConfig(
        exp_id=exp_id,
        description=desc,
        target=target,
        prior=prior,
        mechanism=mechanism,
        **template,
    )


def build_phase25_experiments(winning: Dict) -> List[ExperimentConfig]:
    exps: List[ExperimentConfig] = []
    counter = 0
    def make_id():
        nonlocal counter
        counter += 1
        return f"P25_{counter:03d}"

    # --- Group A: multi-feature combinations for each target ---
    # Include the winning single feature plus 1 or 2 physics-informed siblings
    combos = {
        "scratch_hardness_N": [
            (["binder_pigment_ratio", "pvc_proxy"], 0.55,
             "add PVC proxy to best ridge feature"),
            (["binder_pigment_ratio", "matting_agent_sq"], 0.50,
             "matting agent saturation"),
            (["binder_pigment_ratio", "thickness_x_matting"], 0.50,
             "top interaction"),
            (["binder_pigment_ratio", "crosslink_sq"], 0.45,
             "nonlinear crosslink"),
            (["binder_pigment_ratio", "pvc_proxy", "matting_agent_sq"], 0.50,
             "three-feature PVC+matting"),
            (["binder_pigment_ratio", "log_thickness", "thickness_x_matting"], 0.50,
             "thickness suite added to ridge"),
            (["binder_pigment_ratio", "pigment_paste_sq", "matting_agent_sq"], 0.45,
             "quadratic saturation pair"),
            (["binder_pigment_ratio", "pvc_cpvc_dist"], 0.45,
             "CPVC distance"),
            (["binder_pigment_ratio", "crosslink_x_matting"], 0.40,
             "crosslink x matting interaction"),
        ],
        "gloss_60": [
            (["log_thickness", "thickness_x_matting", "pvc_proxy"], 0.55,
             "add PVC to gloss thickness suite"),
            (["log_thickness", "thickness_x_matting", "matting_pigment_ratio"], 0.50,
             "matting ratio feature"),
            (["log_thickness", "thickness_x_matting", "thickness_sq"], 0.40,
             "add thickness^2"),
            (["log_thickness", "thickness_x_matting", "pigment_paste_sq"], 0.35,
             "add pigment^2"),
            (["log_thickness", "thickness_x_matting", "matting_agent_sq"], 0.40,
             "add matting^2"),
            (["log_thickness", "thickness_x_matting", "binder_pigment_ratio"], 0.45,
             "add BPR"),
            (["log_thickness", "thickness_x_matting", "inv_thickness"], 0.30,
             "add 1/thickness"),
        ],
        "hiding_power_pct": [
            (["thickness_x_pigment", "pvc_proxy"], 0.55,
             "PVC affects hiding via void scattering"),
            (["thickness_x_pigment", "pigment_paste_sq"], 0.50,
             "quadratic pigment loading"),
            (["thickness_x_pigment", "log_thickness"], 0.50,
             "log thickness helper"),
            (["thickness_x_pigment", "matting_pigment_ratio"], 0.45,
             "matting/pigment competition"),
            (["thickness_x_pigment", "pigment_paste_sq", "matting_agent_sq"], 0.45,
             "saturation pair"),
        ],
        "cupping_mm": [
            (["cyc_x_matting", "log_thickness"], 0.55,
             "thickness drives cupping via flexural capacity"),
            (["cyc_x_matting", "thickness_sq"], 0.45,
             "quadratic thickness"),
            (["cyc_x_matting", "crosslink_x_cyc"], 0.45,
             "crosslink density determines flexibility"),
            (["cyc_x_matting", "pvc_proxy"], 0.40,
             "PVC affects rigidity"),
            (["cyc_x_matting", "log_thickness", "crosslink_x_cyc"], 0.50,
             "full cupping physics"),
        ],
    }
    for target, combos_list in combos.items():
        for feats, prior, mech in combos_list:
            exps.append(cfg_from_dict(
                target,
                f"{target}: combo feats={feats}",
                winning[target],
                make_id(), prior, mech,
                extra_features=feats,
            ))

    # --- Group B: cross-family tests against the refined feature set ---
    # For each target, try a different model family with the CURRENT winning
    # feature set. If a fresh family beats the winner it supersedes.
    other_families = ["xgboost", "lightgbm", "extratrees", "ridge"]
    for target in TARGET_COLS:
        current_family = winning[target]["model_family"]
        for fam in other_families:
            if fam == current_family:
                continue
            exps.append(cfg_from_dict(
                target,
                f"{target}: retry {fam} on current features",
                winning[target],
                make_id(),
                prior=0.35,
                mechanism=f"swap model family to {fam}",
                model_family=fam,
            ))

    # --- Group C: XGBoost depth sweep for gloss (current winner: d=7) ---
    for depth, prior in [(4, 0.30), (5, 0.35), (6, 0.35), (8, 0.25), (10, 0.20)]:
        exps.append(cfg_from_dict(
            "gloss_60",
            f"gloss_60: xgb depth sweep d={depth}",
            winning["gloss_60"],
            make_id(), prior,
            "refine depth near current winner",
            xgb_params={"learning_rate": 0.05, "max_depth": depth},
        ))

    # --- Group D: ExtraTrees max_features sweep ---
    for target in ["hiding_power_pct", "cupping_mm"]:
        for max_feats in ["sqrt", "log2", 0.5, 0.8, 1.0]:
            exps.append(cfg_from_dict(
                target,
                f"{target}: ExtraTrees max_features={max_feats}",
                winning[target],
                make_id(),
                prior=0.30,
                mechanism="control per-split feature subsample",
                model_family="extratrees",
                sklearn_kwargs={"max_features": max_feats},
            ))

    # --- Group E: Ridge alpha sweep for scratch hardness ---
    for alpha, prior in [(0.01, 0.30), (0.1, 0.40), (0.5, 0.45), (2.0, 0.35),
                          (5.0, 0.30), (10.0, 0.25)]:
        exps.append(cfg_from_dict(
            "scratch_hardness_N",
            f"scratch_hardness_N: Ridge alpha={alpha}",
            winning["scratch_hardness_N"],
            make_id(), prior,
            "vary regularisation strength",
            sklearn_kwargs={"alpha": alpha},
        ))

    # --- Group F: "kitchen sink" multi-feature sets (large feature adds) ---
    kitchen_sink = [
        "binder_pigment_ratio", "pvc_proxy", "log_thickness",
        "thickness_x_matting", "thickness_x_pigment",
        "matting_agent_sq", "pigment_paste_sq",
    ]
    for target in TARGET_COLS:
        exps.append(cfg_from_dict(
            target,
            f"{target}: kitchen sink 7 physics features",
            winning[target],
            make_id(),
            prior=0.30,
            mechanism="throw every physics-informed feature at the problem",
            extra_features=kitchen_sink,
        ))

    return exps


def main():
    df = load_dataset()
    winning = load_winning()
    print(f"Loaded Phase 2 winning config; MAEs:")
    for t in TARGET_COLS:
        print(f"  {t:20s} {winning[t]['cv_mae']:.4f}")

    experiments = build_phase25_experiments(winning)
    print(f"\nPhase 2.5: {len(experiments)} experiments")
    print("=" * 70)

    # Track per-target best
    best = {t: dict(winning[t]) for t in TARGET_COLS}
    keep_count = 0
    revert_count = 0
    per_target_counts = {t: [0, 0] for t in TARGET_COLS}

    for i, cfg in enumerate(experiments, 1):
        try:
            m = run_experiment(cfg, df)
        except Exception as e:
            print(f"[{cfg.exp_id}] ERROR {e}")
            append_row(cfg.exp_id, cfg.description, cfg.target,
                       9999.0, 9999.0, -9999.0, cfg.prior, "ERROR", str(e)[:150])
            continue
        current_mae = best[cfg.target]["cv_mae"]
        delta = m["mae"] - current_mae
        noise = NOISE_FLOOR.get(cfg.target, 0.01)
        if m["mae"] < current_mae - noise:
            decision = "KEEP"
            keep_count += 1
            per_target_counts[cfg.target][0] += 1
            best[cfg.target] = {
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
                "cv_mae": m["mae"],
                "cv_rmse": m["rmse"],
                "cv_r2": m["r2"],
            }
        else:
            decision = "REVERT"
            revert_count += 1
            per_target_counts[cfg.target][1] += 1
        print(f"[{cfg.exp_id}] ({i:3d}/{len(experiments)}) "
              f"{cfg.target[:10]:10s} MAE={m['mae']:.4f} "
              f"(Δ={delta:+.4f}) → {decision}  {cfg.description[:50]}")
        append_row(cfg.exp_id, cfg.description, cfg.target,
                   m["mae"], m["rmse"], m["r2"], cfg.prior, decision,
                   f"family={cfg.model_family} feats={len(cfg.extra_features)}")

    print("\n" + "-" * 70)
    print(f"Phase 2.5 summary: {keep_count} KEEP, {revert_count} REVERT "
          f"(total {len(experiments)})")
    for t in TARGET_COLS:
        k, r = per_target_counts[t]
        print(f"  {t:20s} keep={k:3d} revert={r:3d}  best MAE={best[t]['cv_mae']:.4f}")

    CONFIG_PATH.write_text(json.dumps(best, indent=2))
    print(f"\nWrote refreshed winning_config.json")


if __name__ == "__main__":
    main()
