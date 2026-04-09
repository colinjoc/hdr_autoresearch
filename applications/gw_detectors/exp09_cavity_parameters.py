"""
exp09_cavity_parameters.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.2, §3.3.

Goal: For the two essential arm cavities in type8/sol00 (identified in
exp08), measure how the choice of mirror reflectivities sets the cavity
finesse, and verify that the operating point sits at the impedance-
matching condition for critical coupling.

Expected:
    Arm cavity finesse ≈ 6100 (Voyager: ~3100)
    Mirror reflectivities matched to within 0.5% of the impedance-matched value.
"""

from evaluate import load_uifo_design
from utils import append_result, save_result_json


def main() -> None:
    d = load_uifo_design("type8", "sol00")
    print(f"type8/sol00 arm cavity finesse: {d.arm_cavity_finesse}")
    print(f"  (Voyager reference:           ~3100)")
    print(f"  (improvement factor:           {(d.arm_cavity_finesse or 0) / 3100:.2f}×)")

    # TODO: extract individual mirror reflectivities from raw_parameters
    # and compute the impedance-matching residual
    impedance_match_residual = None  # placeholder

    save_result_json("exp09_cavity_parameters", {
        "arm_cavity_finesse": d.arm_cavity_finesse,
        "voyager_finesse_ref": 3100,
        "finesse_ratio": (d.arm_cavity_finesse or 0) / 3100,
        "impedance_match_residual": impedance_match_residual,
    })
    append_result(
        exp_id="exp09",
        description="arm cavity parameter extraction",
        improvement=0.0,
        delta_vs_baseline=0.0,
        notes=f"finesse={d.arm_cavity_finesse}",
        status="ANALYSIS",
    )


if __name__ == "__main__":
    main()
