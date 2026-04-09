"""
exp04_uifo_broadband.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §2.1, §3.1.

Goal: Compute the type8/sol00 improvement factor in the full broadband
gravitational wave detection band, not just the post-merger window.
This characterises whether the design's win is band-localised or broad.

Expected: type8/sol00 is optimised for 800-3000 Hz post-merger; broadband
improvement is smaller and may even be < 1 in some sub-bands.
"""

from evaluate import improvement_factor
from utils import append_result, save_result_json


def main() -> None:
    bands = {
        "post_merger": (800, 3000),
        "inspiral":    (10, 100),
        "merger":      (100, 800),
        "broadband":   (10, 5000),
    }
    results = {}
    for name, band in bands.items():
        f = improvement_factor("type8", "sol00", band_hz=band)
        results[name] = f
        print(f"  {name:12s} {band[0]:>5.0f}-{band[1]:<5.0f} Hz   {f:.3f}×")

    save_result_json("exp04_uifo_broadband", results)
    append_result(
        exp_id="exp04",
        description="type8/sol00 broadband improvement",
        improvement=results["post_merger"],
        delta_vs_baseline=results["post_merger"] - 1.0,
        notes=f"broadband={results['broadband']:.2f}",
        status="CHARACTERISATION",
    )


if __name__ == "__main__":
    main()
