"""
exp10_mass_sweep.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.2.

Goal: Sweep the end-mirror mass on the asymmetric arm of type8/sol00
across 0.1 kg to 200 kg and characterise the optomechanical spring
resonance. Identifies the mass that produces the spring resonance in
the 800-3000 Hz post-merger band.

Expected: optimum near 7.3 kg, with the spring resonance at ~1500 Hz.
The Voyager-equivalent 200 kg test mass produces no useful spring
resonance in the post-merger band.
"""

import numpy as np

from evaluate import sweep_parameter
from utils import append_result, save_result_json


def main() -> None:
    masses_kg = list(np.geomspace(0.1, 200.0, num=30))
    sweep = sweep_parameter("type8", "sol00", "test_mass_kg", values=masses_kg)

    best = max(sweep.values, key=lambda v: v.improvement_factor)
    print(f"Best test mass: {best.parameter_value:.2f} kg → improvement {best.improvement_factor:.3f}×")
    print(f"  (paper expectation: 7.3 kg)")

    save_result_json("exp10_mass_sweep", {
        "sweep": [
            {
                "test_mass_kg": v.parameter_value,
                "improvement": v.improvement_factor,
                "min_strain": v.min_strain,
            }
            for v in sweep.values
        ],
        "best_mass_kg": best.parameter_value,
        "best_improvement": best.improvement_factor,
    })
    append_result(
        exp_id="exp10",
        description="end-mirror mass sweep",
        improvement=best.improvement_factor,
        delta_vs_baseline=best.improvement_factor - 3.12,
        notes=f"best mass {best.parameter_value:.1f} kg",
        status="SWEEP",
    )


if __name__ == "__main__":
    main()
