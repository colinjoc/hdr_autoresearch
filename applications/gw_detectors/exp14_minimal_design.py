"""
exp14_minimal_design.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.6.

Goal: Build the minimal essential design from the components identified
as essential by exp06 (component ablation) and exp08 (cavity ablation).
Then re-optimise the one parameter exp13 showed was on a broad plateau
(beamsplitter reflectivity).

Headline result of the entire project:
    Original Urania type8/sol00:    3.12× over Voyager
    Minimal design (10 components): 3.18× (matches original at BS=0.81)
    Minimal + re-optimised BS=0.70: 3.62× (+16% over the original)

The simplified design BEATS the original AI-discovered design.

Lesson (program.md): "Verify the simplified design reaches or beats the
original. If it doesn't, you removed something essential. If it does,
you've found a better design hiding inside the AI's local optimum."
"""

from evaluate import minimal_design, minimal_design_strain, improvement_factor
from utils import append_result, save_result_json


def main() -> None:
    original = improvement_factor("type8", "sol00", band_hz=(800, 3000))
    print(f"Original Urania type8/sol00:           {original:.3f}×")

    # Build minimal design (using AI's BS reflectivity 0.81)
    minimal_no_reopt = minimal_design_strain("type8", "sol00", reoptimise=False)
    print(f"Minimal design (BS=0.81, AI's value):  {minimal_no_reopt.improvement_factor:.3f}×")
    print(f"  components: {minimal_no_reopt.total_components}")
    print(f"  retention:  {minimal_no_reopt.improvement_factor / original:.1%}")

    # Re-optimise the broad-plateau parameter
    minimal_reopt = minimal_design_strain("type8", "sol00", reoptimise=True)
    print(f"Minimal design (BS re-optimised):      {minimal_reopt.improvement_factor:.3f}×")
    print(f"  re-optimised BS reflectivity: {minimal_reopt.beamsplitter_reflectivity:.2f}")
    print(f"  improvement over original:    {(minimal_reopt.improvement_factor / original - 1):+.1%}")

    save_result_json("exp14_minimal_design", {
        "original_improvement": original,
        "minimal_no_reopt_improvement": minimal_no_reopt.improvement_factor,
        "minimal_reopt_improvement": minimal_reopt.improvement_factor,
        "minimal_total_components": minimal_no_reopt.total_components,
        "reoptimised_bs": minimal_reopt.beamsplitter_reflectivity,
    })
    append_result(
        exp_id="exp14",
        description="minimal design + BS reoptimisation",
        improvement=minimal_reopt.improvement_factor,
        delta_vs_baseline=minimal_reopt.improvement_factor - original,
        notes=f"+{(minimal_reopt.improvement_factor / original - 1):.0%} over original; "
              f"BS={minimal_reopt.beamsplitter_reflectivity:.2f}",
        status="HEADLINE_RESULT",
    )


if __name__ == "__main__":
    main()
