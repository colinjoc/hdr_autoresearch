"""
exp01_voyager_baseline.py — RECONSTRUCTED.

Original lost on 2026-04-09. Reconstructed from paper.md §2.2.

Goal: Establish the LIGO Voyager strain noise spectrum as the reference
baseline against which all candidate Urania designs are measured.

Expected output:
    Min strain noise: 3.76e-25 /√Hz
    At frequency:     168 Hz
    Within 0.1% of the published Voyager design.
"""

from evaluate import voyager_baseline_strain
from utils import append_result, save_result_json


def main() -> None:
    s = voyager_baseline_strain()
    print(f"Voyager baseline:")
    print(f"  min strain     = {s.min_strain:.3e} /√Hz")
    print(f"  at frequency   = {s.min_strain_freq_hz:.1f} Hz")

    save_result_json("exp01_voyager_baseline", {
        "min_strain": s.min_strain,
        "min_strain_freq_hz": s.min_strain_freq_hz,
    })
    append_result(
        exp_id="exp01",
        description="LIGO Voyager strain baseline",
        improvement=1.0,
        delta_vs_baseline=0.0,
        notes=f"min strain {s.min_strain:.3e} at {s.min_strain_freq_hz:.0f} Hz",
        status="BASELINE",
    )


if __name__ == "__main__":
    main()
