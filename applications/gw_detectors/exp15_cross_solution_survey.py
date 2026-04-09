"""
exp15_cross_solution_survey.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.5.

Goal: Apply the decomposition protocol (exp06–exp14) to all 25 type8
solutions, not just sol00. Classify each by the relative contributions
of signal amplification vs noise suppression. Tests whether the AI's
type8 designs all use the same physical mechanism, or whether multiple
distinct mechanisms coexist within the family.

Expected: two distinct families.
    Noise-suppression family (dominant) — sol00 is the strongest member
    Signal-amplification family (secondary) — up to 13.7× signal gain

The "explanation" of the AI's discovery is plural, not singular.

Lesson (program.md): "Survey the family, don't extrapolate from one
solution. After decomposing the best solution, decompose 3-5 others
from the same family. They may use distinct mechanisms."
"""

from collections import Counter

from evaluate import classify_solution_family
from utils import append_result, save_result_json


def main() -> None:
    classifications = []
    for i in range(25):
        sol_id = f"sol{i:02d}"
        c = classify_solution_family("type8", sol_id)
        classifications.append({
            "sol_id": sol_id,
            "dominant_mechanism": c.dominant_mechanism,
            "noise_contribution": c.noise_contribution,
            "signal_contribution": c.signal_contribution,
            "signal_gain_factor": c.signal_gain_factor,
        })
        print(f"  {sol_id}: {c.dominant_mechanism:22s}  "
              f"signal_gain={c.signal_gain_factor:5.2f}×")

    family_counts = Counter(c["dominant_mechanism"] for c in classifications)
    max_signal_gain = max(c["signal_gain_factor"] for c in classifications)

    print(f"\nFamily counts:")
    for fam, n in family_counts.most_common():
        print(f"  {fam:22s} {n}")
    print(f"Max signal gain across family: {max_signal_gain:.1f}×")
    print(f"  (paper: 13.7×)")

    save_result_json("exp15_cross_solution_survey", {
        "classifications": classifications,
        "family_counts": dict(family_counts),
        "max_signal_gain": max_signal_gain,
    })
    append_result(
        exp_id="exp15",
        description="type8 family classification (25 solutions)",
        improvement=0.0,
        delta_vs_baseline=0.0,
        notes=f"families={dict(family_counts)}; max_gain={max_signal_gain:.1f}×",
        status="FAMILY_SURVEY",
    )


if __name__ == "__main__":
    main()
