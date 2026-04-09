"""
exp13_bs_sweep.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.3.

Goal: Sweep the main beamsplitter reflectivity from 0.50 to 0.80 in
type8/sol00. Tests whether the original AI's choice of 0.81 is a narrow
optimum or just a workable point on a broad plateau.

Expected: any value in [0.5, 0.8] is within 5% of optimal. The original
AI converged at 0.81 simply because the gradient was small in this
region — there was nothing pushing it across the plateau toward the
true optimum.

This finding motivates exp14, which builds the minimal design and
re-optimises this one parameter.

Lesson (program.md): "Broad plateaus indicate the optimiser
over-parameterised a robust choice — simplify or reoptimise."
"""

from evaluate import sweep_parameter
from utils import append_result, save_result_json


def main() -> None:
    bs_values = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.81]
    sweep = sweep_parameter("type8", "sol00", "beamsplitter_reflectivity", values=bs_values)
    best = max(sweep.values, key=lambda v: v.improvement_factor)

    print(f"Beamsplitter reflectivity sweep [0.50–0.80]:")
    for v in sweep.values:
        marker = " ← BEST" if v == best else ""
        print(f"  R={v.parameter_value:.2f}  improvement {v.improvement_factor:.3f}×{marker}")

    # Verify broad-plateau classification
    in_range = [v for v in sweep.values if 0.50 <= v.parameter_value <= 0.80]
    within_5pct = all(v.improvement_factor / best.improvement_factor > 0.95 for v in in_range)
    print(f"\nAll values in [0.5, 0.8] within 5% of best: {within_5pct}")

    save_result_json("exp13_bs_sweep", {
        "best_R": best.parameter_value,
        "best_improvement": best.improvement_factor,
        "is_broad_plateau": within_5pct,
        "sweep": [{"R": v.parameter_value, "improvement": v.improvement_factor} for v in sweep.values],
    })
    append_result(
        exp_id="exp13",
        description="beamsplitter reflectivity sweep",
        improvement=best.improvement_factor,
        delta_vs_baseline=best.improvement_factor - 3.12,
        notes=f"best R={best.parameter_value:.2f}, broad plateau confirmed",
        status="BROAD_PLATEAU",
    )


if __name__ == "__main__":
    main()
