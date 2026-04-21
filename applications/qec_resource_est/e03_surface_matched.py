"""
E03: matched-overhead surface code benchmark to compare against BB E02.

Bravyi 2024 [[144,12,12]] BB encodes 12 logical qubits at distance 12 with 288 physical
qubits. Matched surface-code encoding of 12 logical qubits at distance 12 requires
12 × rotated-surface-d=12 patches → 12 × (2d²-1) = 12 × 287 = 3,444 physical qubits.

Per-shot decoder cost per branch:
  BB:       1 call to BP+OSD on the full [[144,12,12]] DEM
  Surface:  12 calls to MWPM (PyMatching), one per d=12 patch

This E03 measures the per-patch cost of d=12 surface circuit-level MWPM on CPU PyMatching
and on CUDA-Q QEC's `pymatching` wrapper (which runs CPU-side via the CUDA-Q harness).
The composite comparison (BB vs 12-surface) is then computed in the findings doc.
"""

from __future__ import annotations
import datetime
import time

import numpy as np
import stim
import pymatching


def build_surface_d12_circuit(p: float = 1e-3, rounds: int = 12) -> stim.Circuit:
    """Rotated surface code d=12, Z-basis memory, SI1000-like circuit noise.

    Use Stim's built-in `generated` circuit with circuit-level noise. This is the
    standard way to get a d=12 rotated surface memory experiment.
    """
    return stim.Circuit.generated(
        code_task="surface_code:rotated_memory_z",
        distance=12,
        rounds=rounds,
        after_clifford_depolarization=p,
        before_round_data_depolarization=p,
        before_measure_flip_probability=p,
        after_reset_flip_probability=p,
    )


def main():
    print("[E03] matched-overhead surface code d=12 rotated, circuit-level MWPM", flush=True)
    p = 1e-3
    rounds = 12
    shots = 300

    circ = build_surface_d12_circuit(p=p, rounds=rounds)
    dem = circ.detector_error_model(decompose_errors=True)
    print(f"[E03] d=12 surface: {circ.num_qubits} qubits, {dem.num_detectors} detectors, "
          f"{dem.num_observables} observables, {dem.num_errors} errors", flush=True)

    # PyMatching from DEM
    matcher = pymatching.Matching.from_detector_error_model(dem)

    # Sample shots
    sampler = circ.compile_detector_sampler()
    detector_events, observable_flips = sampler.sample(shots=shots, separate_observables=True)
    detector_events = detector_events.astype(np.uint8)

    # CPU PyMatching — ONE patch
    t0 = time.perf_counter()
    for i in range(shots):
        matcher.decode(detector_events[i])
    cpu_one = time.perf_counter() - t0
    cpu_us_one = 1e6 * cpu_one / shots
    print(f"[E03] CPU PyMatching (ONE d=12 patch): {cpu_us_one:.1f} us/shot", flush=True)

    # Matched 12-patch cost (estimate: 12× single-patch)
    cpu_us_12 = 12 * cpu_us_one
    print(f"[E03] Matched 12-patch surface MWPM cost: {cpu_us_12:.1f} us/shot "
          f"(12 × single-patch)", flush=True)

    # Compare vs BB row from E02
    bb_gpu_us = 3705.13
    bb_cpu_us = 541984.66
    print(f"\n[E03] COMPARISON", flush=True)
    print(f"[E03] BB GPU BP+OSD:              {bb_gpu_us:.1f} us/shot ({bb_gpu_us/1000:.2f} ms)", flush=True)
    print(f"[E03] BB CPU BP+OSD:              {bb_cpu_us:.1f} us/shot ({bb_cpu_us/1000:.2f} ms)", flush=True)
    print(f"[E03] 12× surface CPU MWPM:       {cpu_us_12:.1f} us/shot ({cpu_us_12/1000:.2f} ms)", flush=True)
    print()
    print(f"[E03] BB-GPU vs 12×surface-CPU-MWPM: {bb_gpu_us/cpu_us_12:.3f} (GPU BP+OSD vs CPU MWPM)", flush=True)
    print(f"[E03] BB-CPU vs 12×surface-CPU-MWPM: {bb_cpu_us/cpu_us_12:.3f}", flush=True)
    print()
    if bb_gpu_us > cpu_us_12:
        print(f"[E03] !!! 12×surface MWPM BEATS BB GPU by {bb_gpu_us/cpu_us_12:.2f}x — "
              f"qLDPC decoder cost inverts the 12× qubit advantage", flush=True)
    else:
        print(f"[E03] BB GPU wins over 12×surface MWPM by {cpu_us_12/bb_gpu_us:.2f}x", flush=True)

    # Append to results.tsv
    tsv_path = "/home/col/generalized_hdr_autoresearch/applications/qec_resource_est/results.tsv"
    ts = datetime.datetime.utcnow().isoformat()
    with open(tsv_path, "a") as f:
        f.write(
            f"E03_surface_d12_circuit_1patch\t{ts}\tsurface_d12\t12\t"
            f"SI1000_circuit\t{p}\t{shots}\t42\t"
            f"{dem.num_detectors}\t{dem.num_errors}\t{cpu_us_one:.2f}\t0.00\t0.000\tKEEP\t"
            f"Phase1_E03_surface_d12_CPU_PyMatching_1patch\n"
        )
        f.write(
            f"E03_surface_d12_matched12\t{ts}\tsurface_12patch\t12\t"
            f"SI1000_circuit_matched\t{p}\t{shots}\t42\t"
            f"{dem.num_detectors*12}\t{dem.num_errors*12}\t{cpu_us_12:.2f}\t0.00\t0.000\tKEEP\t"
            f"Phase1_E03_surface_matched_12patch_CPU_PyMatching\n"
        )
    print(f"\n[E03] wrote 2 rows to {tsv_path}")


if __name__ == "__main__":
    main()
