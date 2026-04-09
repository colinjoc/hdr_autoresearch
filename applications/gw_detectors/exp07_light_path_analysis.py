"""
exp07_light_path_analysis.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.1.

Goal: Trace the actual carrier light path through the type8/sol00 UIFO
to identify which optical elements actually carry power. UIFO grids can
contain "ghost" mirrors and beamsplitters that the optimiser left in
place but that no light ever touches.

Output: a graph (or simple adjacency list) of the active light path,
distinguishing components carrying > 1% of input power from those
carrying < 0.001%.

This is the data that allows exp06's ablation interpretation: a
component carrying < 0.001% of power is by definition redundant
without needing to ablate it.
"""

from evaluate import load_uifo_design
from utils import append_result, save_result_json


def main() -> None:
    d = load_uifo_design("type8", "sol00")

    # TODO: hook into Differometor's field-tracing API to get carrier amplitudes
    # at each port. The original code probably did something like:
    #     fields = df.compute_carrier_fields(design)
    #     active = [k for k, v in fields.items() if abs(v)**2 > 0.001]
    active_mirrors = []     # placeholder
    active_bs = []          # placeholder
    active_lasers = []      # placeholder
    active_squeezers = []   # placeholder

    print(f"Active light path:")
    print(f"  mirrors carrying >0.1% power     = {len(active_mirrors)} of {d.n_mirrors}")
    print(f"  beamsplitters carrying >0.1%      = {len(active_bs)} of {d.n_beamsplitters}")
    print(f"  lasers contributing >0.1% input   = {len(active_lasers)} of {d.n_lasers}")
    print(f"  squeezers carrying >0.1 dB        = {len(active_squeezers)} of {d.n_squeezers}")

    save_result_json("exp07_light_path_analysis", {
        "active_mirrors": active_mirrors,
        "active_beamsplitters": active_bs,
        "active_lasers": active_lasers,
        "active_squeezers": active_squeezers,
    })
    append_result(
        exp_id="exp07",
        description="type8/sol00 light-path active component count",
        improvement=0.0,
        delta_vs_baseline=0.0,
        notes=f"{len(active_mirrors)}M+{len(active_bs)}BS+{len(active_lasers)}L active",
        status="ANALYSIS",
    )


if __name__ == "__main__":
    main()
