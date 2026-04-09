"""
exp06_ablation_postmerger.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.1, §3.4.

Goal: Component-level ablation study. For each mirror, beamsplitter,
laser, and squeezer in type8/sol00, set its key parameter to a "removed"
value (R=0 transparent, P=0 dark, sq=0 dB) and measure the change in
post-merger improvement factor.

This is the ablation that produces the §3.1 Table:
    Lasers       3 → essential 1 (removing 2nd improves +3%)
    Squeezers    4 → essential 0 (all carry <0.5 dB)
    Arm cavities 13 → essential 2
    Beamsplitters 13 → essential 1 (the 70:30 splitter)
    Filter cavities 3 → essential 0

Lesson (program.md): component ablation BEFORE parameter sweeps.
"""

from evaluate import load_uifo_design, ablate_component, improvement_factor
from utils import append_result, save_result_json


def main() -> None:
    d = load_uifo_design("type8", "sol00")
    baseline = improvement_factor("type8", "sol00", band_hz=(800, 3000))
    print(f"Baseline improvement: {baseline:.3f}×")

    ablations = []
    component_names = (
        [f"mirror_{i}" for i in range(d.n_mirrors)]
        + [f"bs_{i}" for i in range(d.n_beamsplitters)]
        + [f"laser_{i}" for i in range(d.n_lasers)]
        + [f"squeezer_{i}" for i in range(d.n_squeezers)]
    )

    for name in component_names:
        r = ablate_component("type8", "sol00", name)
        # Classify: <1.2× degradation → redundant; 1.2-2× → important; >2× → essential
        ratio = baseline / max(r.ablated_improvement, 1e-9)
        if ratio < 1.2:
            classification = "redundant"
        elif ratio < 2.0:
            classification = "important"
        else:
            classification = "essential"
        ablations.append({
            "component": name,
            "ablated_improvement": r.ablated_improvement,
            "delta_pct": r.delta_pct,
            "classification": classification,
        })

    n_essential = sum(1 for a in ablations if a["classification"] == "essential")
    n_important = sum(1 for a in ablations if a["classification"] == "important")
    n_redundant = sum(1 for a in ablations if a["classification"] == "redundant")
    print(f"  essential   = {n_essential}")
    print(f"  important   = {n_important}")
    print(f"  redundant   = {n_redundant}")

    save_result_json("exp06_ablation_postmerger", {
        "baseline": baseline,
        "ablations": ablations,
        "n_essential": n_essential,
        "n_important": n_important,
        "n_redundant": n_redundant,
    })
    append_result(
        exp_id="exp06",
        description="type8/sol00 component-level ablation",
        improvement=baseline,
        delta_vs_baseline=0.0,
        notes=f"essential={n_essential}, important={n_important}, redundant={n_redundant}",
        status="ABLATION",
    )


if __name__ == "__main__":
    main()
