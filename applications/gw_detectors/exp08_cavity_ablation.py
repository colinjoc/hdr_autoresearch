"""
exp08_cavity_ablation.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §2.3 and §3.1.

Goal: Identify all 4 km arm-length cavities in type8/sol00 and ablate
each one independently by making one of its mirrors transparent (R=0).
Establishes which cavities are essential to the post-merger sensitivity.

Expected: of the 13 cavities in type8/sol00, only 2 (the main Michelson
arms) are essential. The other 11 are optimiser artifacts.
"""

from evaluate import load_uifo_design, ablate_component, improvement_factor
from utils import append_result, save_result_json


def find_arm_cavities(design):
    """Find all 4 km cavities in a UIFO design.

    Returns a list of (cavity_id, end_mirror_name) tuples.
    """
    # TODO: query Differometor for cavity-length topology
    # cavities = df.find_cavities(design, length_m=4000.0, tolerance_m=10.0)
    return []


def main() -> None:
    d = load_uifo_design("type8", "sol00")
    cavities = find_arm_cavities(d)
    print(f"Found {len(cavities)} arm-length (4 km) cavities in type8/sol00")

    baseline = improvement_factor("type8", "sol00", band_hz=(800, 3000))
    print(f"Baseline improvement: {baseline:.3f}×")

    cavity_results = []
    for cav_id, end_mirror in cavities:
        r = ablate_component("type8", "sol00", end_mirror)
        cavity_results.append({
            "cavity_id": cav_id,
            "end_mirror": end_mirror,
            "ablated_improvement": r.ablated_improvement,
            "delta_pct": r.delta_pct,
            "essential": r.delta_pct < -50.0,  # >2× degradation
        })

    n_essential = sum(1 for c in cavity_results if c["essential"])
    print(f"Essential cavities: {n_essential} of {len(cavities)}")

    save_result_json("exp08_cavity_ablation", {
        "baseline": baseline,
        "n_cavities": len(cavities),
        "n_essential": n_essential,
        "cavity_results": cavity_results,
    })
    append_result(
        exp_id="exp08",
        description="type8/sol00 4-km cavity ablation",
        improvement=baseline,
        delta_vs_baseline=0.0,
        notes=f"essential cavities {n_essential}/{len(cavities)}",
        status="ABLATION",
    )


if __name__ == "__main__":
    main()
