"""
exp05_topology_analysis.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.1.

Goal: Enumerate every component in the type8/sol00 UIFO and classify it
by type. Establishes the starting point for subsequent ablation work.

Expected:
    48 mirrors
    13 beamsplitters
    3 lasers
    4 squeezers
    3 filter cavities
    > 120 free parameters
"""

from evaluate import load_uifo_design
from utils import append_result, save_result_json


def main() -> None:
    d = load_uifo_design("type8", "sol00")
    print(f"type8/sol00 component inventory:")
    print(f"  mirrors           = {d.n_mirrors}")
    print(f"  beamsplitters     = {d.n_beamsplitters}")
    print(f"  lasers            = {d.n_lasers}")
    print(f"  squeezers         = {d.n_squeezers}")
    print(f"  filter cavities   = {d.n_filter_cavities}")
    print(f"  arm finesse       = {d.arm_cavity_finesse}")
    print(f"  test mass         = {d.test_mass_kg} kg")
    print(f"  bs reflectivity   = {d.beamsplitter_reflectivity}")
    print(f"  squeezer levels   = {[s.level_db for s in d.squeezers]}")

    save_result_json("exp05_topology_analysis", {
        "type": "type8",
        "sol": "sol00",
        "n_mirrors": d.n_mirrors,
        "n_beamsplitters": d.n_beamsplitters,
        "n_lasers": d.n_lasers,
        "n_squeezers": d.n_squeezers,
        "n_filter_cavities": d.n_filter_cavities,
        "squeezer_levels_db": [s.level_db for s in d.squeezers],
    })
    append_result(
        exp_id="exp05",
        description="type8/sol00 topology inventory",
        improvement=0.0,
        delta_vs_baseline=0.0,
        notes=f"{d.n_mirrors}M+{d.n_beamsplitters}BS+{d.n_lasers}L+{d.n_squeezers}Sq",
        status="TOPOLOGY",
    )


if __name__ == "__main__":
    main()
