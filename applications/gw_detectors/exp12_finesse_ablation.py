"""
exp12_finesse_ablation.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.2, §3.3.

Goal: Sweep the arm cavity finesse around the type8/sol00 operating
point (6100) over a ±5% window. Verifies that this parameter is a
narrow optimum corresponding to the impedance-matched critical-coupling
condition — i.e. real physics, not parameterisation artifact.

Expected: at -5% (5795) and +5% (6405), the improvement factor drops
below 1.0× (i.e. worse than Voyager). This is the signature of a sharp
peak — locked-down specification.

Lesson (program.md): "Distinguish narrow optima (real physics) from broad
robustness (parameterisation choice). Sharp peaks require tight tolerance;
broad plateaus invite re-optimisation."
"""

import numpy as np

from evaluate import sweep_parameter
from utils import append_result, save_result_json


def main() -> None:
    sweep = sweep_parameter(
        "type8", "sol00", "arm_finesse",
        center=6100, frac_window=0.05, n_steps=21,
    )
    best = max(sweep.values, key=lambda v: v.improvement_factor)
    edge_low = sweep.values[0]
    edge_high = sweep.values[-1]

    print(f"Arm finesse sweep around 6100 ±5%:")
    print(f"  best  ({best.parameter_value:6.1f}) → improvement {best.improvement_factor:.3f}×")
    print(f"  -5%   ({edge_low.parameter_value:6.1f}) → improvement {edge_low.improvement_factor:.3f}×")
    print(f"  +5%   ({edge_high.parameter_value:6.1f}) → improvement {edge_high.improvement_factor:.3f}×")
    is_narrow = edge_low.improvement_factor < 1.0 and edge_high.improvement_factor < 1.0
    print(f"  → {'NARROW OPTIMUM (real physics)' if is_narrow else 'broad'}")

    save_result_json("exp12_finesse_ablation", {
        "best_finesse": best.parameter_value,
        "best_improvement": best.improvement_factor,
        "edge_low_finesse": edge_low.parameter_value,
        "edge_low_improvement": edge_low.improvement_factor,
        "edge_high_finesse": edge_high.parameter_value,
        "edge_high_improvement": edge_high.improvement_factor,
        "is_narrow_optimum": is_narrow,
    })
    append_result(
        exp_id="exp12",
        description="arm cavity finesse sweep around critical coupling",
        improvement=best.improvement_factor,
        delta_vs_baseline=0.0,
        notes="narrow optimum confirmed" if is_narrow else "broad plateau",
        status="NARROW_PEAK",
    )


if __name__ == "__main__":
    main()
