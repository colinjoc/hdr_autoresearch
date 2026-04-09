"""
exp11_homodyne_sweep.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.4.

Goal: Sweep the homodyne readout phase across the full 360° range and
characterise the sensitivity variation. Tests whether the original UIFO's
homodyne angle is critically tuned (real physics) or arbitrary
(parameterisation artifact).

Expected: only 1.4% sensitivity variation across the full 360° sweep.
The homodyne angle is essentially irrelevant. No precision phase
alignment is required for the simplified design.
"""

import numpy as np

from evaluate import sweep_parameter
from utils import append_result, save_result_json


def main() -> None:
    angles_deg = list(np.linspace(0.0, 360.0, 36))
    sweep = sweep_parameter(
        "type8", "sol00", "homodyne_angle_deg",
        values=angles_deg, n_steps=36, span=360.0,
    )
    best = max(sweep.values, key=lambda v: v.improvement_factor)
    worst = min(sweep.values, key=lambda v: v.improvement_factor)
    rel_var = (best.improvement_factor - worst.improvement_factor) / best.improvement_factor

    print(f"Homodyne angle sweep:")
    print(f"  best  ({best.parameter_value:6.1f}°) → improvement {best.improvement_factor:.3f}×")
    print(f"  worst ({worst.parameter_value:6.1f}°) → improvement {worst.improvement_factor:.3f}×")
    print(f"  relative variation                      = {rel_var:.1%}")
    print(f"  paper expectation: ~1.4%")

    save_result_json("exp11_homodyne_sweep", {
        "best_angle_deg": best.parameter_value,
        "worst_angle_deg": worst.parameter_value,
        "best_improvement": best.improvement_factor,
        "worst_improvement": worst.improvement_factor,
        "relative_variation": rel_var,
    })
    append_result(
        exp_id="exp11",
        description="homodyne readout angle sweep",
        improvement=best.improvement_factor,
        delta_vs_baseline=0.0,
        notes=f"variation {rel_var:.1%} (paper: 1.4%)",
        status="SWEEP",
    )


if __name__ == "__main__":
    main()
