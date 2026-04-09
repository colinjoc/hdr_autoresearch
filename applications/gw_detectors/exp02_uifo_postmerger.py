"""
exp02_uifo_postmerger.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §3.1 and the
website summary.

Goal: Compute the improvement factor of the type8/sol00 Urania design
over Voyager in the post-merger band (800-3000 Hz).

Expected output:
    Improvement factor: ~3.12×

Note: an earlier (and corrected) draft of this experiment misattributed
the dominant mechanism to signal amplification (claiming ~5449× signal
gain). The correction came in exp03 / exp04 — see paper §2.4.
"""

from evaluate import improvement_factor
from utils import append_result, save_result_json


def main() -> None:
    f = improvement_factor("type8", "sol00", band_hz=(800, 3000))
    print(f"type8/sol00 improvement over Voyager: {f:.3f}× (post-merger 800-3000 Hz)")

    save_result_json("exp02_uifo_postmerger", {
        "type": "type8",
        "sol": "sol00",
        "band_hz": (800, 3000),
        "improvement_factor": f,
    })
    append_result(
        exp_id="exp02",
        description="type8/sol00 post-merger improvement",
        improvement=f,
        delta_vs_baseline=f - 1.0,
        notes="Urania headline design",
        status="KEEP",
    )


if __name__ == "__main__":
    main()
