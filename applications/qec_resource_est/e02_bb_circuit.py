"""
E02: BB [[144,12,12]] gross code under CIRCUIT-LEVEL SI1000 noise.

This is the headline operating point for proposal_v3: d=12 BB + SI1000 at p=1e-3,
full circuit-level DEM including syndrome-extraction circuit noise.

Benchmarks BP+OSD GPU (nv-qldpc-decoder) vs CPU (ldpc.BpOsdDecoder) on the circuit-level
DEM. This is expected to be the regime where the GPU finally wins — much bigger H than
code-capacity, amortizes the GPU kernel-launch overhead.
"""

from __future__ import annotations
import datetime
import time

import numpy as np
import sympy
import stim

from qldpc.codes import BBCode
from qldpc.objects import Pauli
import qldpc.circuits as qc

import cudaq_qec as qec
from ldpc.bposd_decoder import BpOsdDecoder


def build_bb_circuit_dem(num_rounds: int = 12, p: float = 1e-3):
    """Build BB [[144,12,12]] memory experiment + circuit-level DEM under SI1000 noise."""
    x, y = sympy.symbols("x y")
    bb = BBCode({x: 12, y: 6}, x**3 + y + y**2, y**3 + x + x**2)
    noise = qc.SI1000NoiseModel(p)
    circuit = qc.get_memory_experiment(bb, basis=Pauli.Z, num_rounds=num_rounds, noise_model=noise)
    dem = circuit.detector_error_model(decompose_errors=False, allow_gauge_detectors=True)
    # Flatten detector-error-model to parity-check-matrix + error rates
    # Use stim's own DEM -> matrix helper if present, else hand-unpack
    return bb, circuit, dem


def dem_to_pcm(dem) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert a stim.DetectorErrorModel into (H, obs_mat, error_rates)."""
    num_detectors = dem.num_detectors
    num_observables = dem.num_observables

    errors = []
    for instr in dem.flattened():
        if instr.type == "error":
            p = instr.args_copy()[0]
            targets = instr.targets_copy()
            det_bits = []
            obs_bits = []
            for t in targets:
                if t.is_relative_detector_id():
                    det_bits.append(t.val)
                elif t.is_logical_observable_id():
                    obs_bits.append(t.val)
            errors.append((p, det_bits, obs_bits))
    num_errors = len(errors)
    H = np.zeros((num_detectors, num_errors), dtype=np.uint8)
    obs_mat = np.zeros((num_observables, num_errors), dtype=np.uint8)
    rates = np.zeros(num_errors, dtype=np.float64)
    for j, (p, det_bits, obs_bits) in enumerate(errors):
        rates[j] = p
        for d in det_bits:
            H[d, j] = 1
        for o in obs_bits:
            obs_mat[o, j] = 1
    return H, obs_mat, rates


def main():
    print("[E02] BB [[144,12,12]] circuit-level DEM benchmark on RTX 3060", flush=True)

    p = 1e-3
    num_rounds = 12
    print(f"[E02] building memory experiment: num_rounds={num_rounds}, SI1000 p={p}", flush=True)
    t0 = time.perf_counter()
    bb, circuit, dem = build_bb_circuit_dem(num_rounds=num_rounds, p=p)
    print(f"[E02] circuit built in {time.perf_counter()-t0:.2f}s", flush=True)
    print(f"[E02] circuit: {circuit.num_qubits} qubits, {circuit.num_detectors} detectors, {circuit.num_observables} observables", flush=True)

    t0 = time.perf_counter()
    H, obs_mat, rates = dem_to_pcm(dem)
    print(f"[E02] DEM->PCM in {time.perf_counter()-t0:.2f}s", flush=True)
    print(f"[E02] H shape: {H.shape}  rates shape: {rates.shape}", flush=True)
    print(f"[E02] fraction of nonzero H entries: {H.sum() / H.size:.6f}", flush=True)

    # Sample shots from the circuit to get real detector events
    shots = 300
    print(f"\n[E02] sampling {shots} shots via stim compiled sampler...", flush=True)
    t0 = time.perf_counter()
    sampler = circuit.compile_detector_sampler()
    detector_events, observable_flips = sampler.sample(shots=shots, separate_observables=True)
    sample_s = time.perf_counter() - t0
    print(f"[E02] sampled in {sample_s:.2f}s", flush=True)
    detector_events = detector_events.astype(np.uint8)

    # GPU decode loop
    print("\n[E02] GPU nv-qldpc-decoder (sparse mode) loop decode", flush=True)
    gpu = qec.get_decoder("nv-qldpc-decoder", H, use_sparsity=True)
    t0 = time.perf_counter()
    for i in range(shots):
        gpu.decode(detector_events[i].astype(float).tolist())
    gpu_s = time.perf_counter() - t0
    gpu_us = 1e6 * gpu_s / shots
    print(f"[E02] GPU sparse loop: {gpu_us:.1f} us/shot (total {gpu_s:.2f}s)", flush=True)

    # CPU decode loop
    print("\n[E02] CPU ldpc BP+OSD loop decode", flush=True)
    cpu = BpOsdDecoder(
        pcm=H,
        error_rate=float(rates.mean()),
        max_iter=100,
        bp_method="product_sum",
        ms_scaling_factor=0.5,
        osd_method="osd_cs",
        osd_order=7,
    )
    t0 = time.perf_counter()
    for i in range(shots):
        cpu.decode(detector_events[i].astype(np.uint8))
    cpu_s = time.perf_counter() - t0
    cpu_us = 1e6 * cpu_s / shots
    print(f"[E02] CPU loop: {cpu_us:.1f} us/shot (total {cpu_s:.2f}s)", flush=True)

    print(f"\n[E02] GPU/CPU ratio: {gpu_us/cpu_us:.3f}", flush=True)
    if cpu_us > gpu_us:
        print(f"[E02] GPU WINS by {cpu_us/gpu_us:.2f}x", flush=True)
    else:
        print(f"[E02] CPU still wins by {gpu_us/cpu_us:.2f}x", flush=True)

    # Append to results.tsv
    tsv_path = "/home/col/generalized_hdr_autoresearch/applications/qec_resource_est/results.tsv"
    ts = datetime.datetime.utcnow().isoformat()
    with open(tsv_path, "a") as f:
        line = (
            f"E02_BB_circuit_SI1000_p{p}\t{ts}\tBB_144_12_12\t12\t"
            f"SI1000_circuit\t{p}\t{shots}\t42\t"
            f"{H.shape[0]}\t{H.shape[1]}\t{cpu_us:.2f}\t{gpu_us:.2f}\t"
            f"{gpu_us/cpu_us:.3f}\tKEEP\t"
            f"Phase1_E02_BB_144_circuit_level_SI1000_rounds{num_rounds}\n"
        )
        f.write(line)
    print(f"[E02] wrote 1 row to {tsv_path}")


if __name__ == "__main__":
    main()
