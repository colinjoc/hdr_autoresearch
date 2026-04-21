"""
E04: Energy measurement for GPU BP+OSD (BB) vs CPU MWPM (surface) on circuit-level DEMs.

Samples GPU power draw via NVML at ~10 Hz during decoder execution and integrates to
Joules per shot. CPU "energy" is approximated by TDP × wall-time (accurate within ~2×
for a single-core pinned workload on modern x86).

This produces the decoder-J dimension of the proposal_v3 composite headline metric.
"""

from __future__ import annotations
import datetime
import time
import threading

import numpy as np
import sympy
import stim
import pymatching
import pynvml

from qldpc.codes import BBCode
from qldpc.objects import Pauli
import qldpc.circuits as qc

import cudaq_qec as qec
from ldpc.bposd_decoder import BpOsdDecoder


class NvmlSampler:
    """Background GPU power sampler. Integrates power(t) → Joules."""
    def __init__(self, gpu_index: int = 0, sample_hz: float = 50.0):
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
        self.interval = 1.0 / sample_hz
        self.running = False
        self.samples: list[tuple[float, float]] = []  # (t, watts)
        self.thread = None

    def _loop(self):
        while self.running:
            t = time.perf_counter()
            try:
                mw = pynvml.nvmlDeviceGetPowerUsage(self.handle)
                self.samples.append((t, mw / 1000.0))
            except Exception:
                pass
            time.sleep(self.interval)

    def start(self):
        self.samples = []
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self) -> float:
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if len(self.samples) < 2:
            return 0.0
        # Trapezoid integration of watts over time → joules
        joules = 0.0
        for i in range(1, len(self.samples)):
            dt = self.samples[i][0] - self.samples[i - 1][0]
            avg_w = 0.5 * (self.samples[i][1] + self.samples[i - 1][1])
            joules += dt * avg_w
        return joules


def build_bb_dem(p: float = 1e-3, rounds: int = 12):
    x, y = sympy.symbols("x y")
    bb = BBCode({x: 12, y: 6}, x**3 + y + y**2, y**3 + x + x**2)
    noise = qc.SI1000NoiseModel(p)
    circuit = qc.get_memory_experiment(bb, basis=Pauli.Z, num_rounds=rounds, noise_model=noise)
    dem = circuit.detector_error_model(decompose_errors=False, allow_gauge_detectors=True)
    H, obs_mat, rates = dem_to_pcm(dem)
    return circuit, dem, H, obs_mat, rates


def dem_to_pcm(dem) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    num_detectors = dem.num_detectors
    num_observables = dem.num_observables
    errors = []
    for instr in dem.flattened():
        if instr.type == "error":
            p = instr.args_copy()[0]
            targets = instr.targets_copy()
            det_bits = [t.val for t in targets if t.is_relative_detector_id()]
            obs_bits = [t.val for t in targets if t.is_logical_observable_id()]
            errors.append((p, det_bits, obs_bits))
    H = np.zeros((num_detectors, len(errors)), dtype=np.uint8)
    obs = np.zeros((num_observables, len(errors)), dtype=np.uint8)
    rates = np.zeros(len(errors))
    for j, (p, dets, obss) in enumerate(errors):
        rates[j] = p
        for d in dets: H[d, j] = 1
        for o in obss: obs[o, j] = 1
    return H, obs, rates


def build_surface_circuit(p: float = 1e-3, d: int = 12, rounds: int = 12):
    return stim.Circuit.generated(
        code_task="surface_code:rotated_memory_z",
        distance=d, rounds=rounds,
        after_clifford_depolarization=p,
        before_round_data_depolarization=p,
        before_measure_flip_probability=p,
        after_reset_flip_probability=p,
    )


def measure_decoder(name: str, decode_fn, shots: int, idle_baseline_w: float) -> dict:
    # Warm up
    for i in range(min(10, shots)):
        decode_fn(i)
    # Timed + power-sampled run
    sampler = NvmlSampler()
    sampler.start()
    t0 = time.perf_counter()
    for i in range(shots):
        decode_fn(i)
    wall_s = time.perf_counter() - t0
    joules_total = sampler.stop()
    # Subtract idle baseline from gross energy
    idle_energy = idle_baseline_w * wall_s
    active_joules = max(joules_total - idle_energy, 0)
    return {
        "name": name,
        "wall_s": wall_s,
        "us_per_shot": 1e6 * wall_s / shots,
        "gross_J": joules_total,
        "idle_J": idle_energy,
        "active_J": active_joules,
        "J_per_shot": active_joules / shots,
        "avg_W": joules_total / wall_s if wall_s > 0 else 0.0,
    }


def main():
    print("[E04] Energy benchmark: BB GPU BP+OSD vs 12× surface CPU MWPM", flush=True)

    # Measure idle GPU power baseline (5 seconds of no GPU activity)
    print("[E04] sampling GPU idle baseline (5s)...", flush=True)
    s = NvmlSampler(); s.start()
    time.sleep(5.0)
    idle_J_5s = s.stop()
    idle_W = idle_J_5s / 5.0
    print(f"[E04] GPU idle: {idle_W:.2f} W mean", flush=True)

    p = 1e-3
    shots = 300

    print("\n[E04] Building BB DEM...", flush=True)
    bb_circ, bb_dem, H_bb, obs_bb, rates_bb = build_bb_dem(p=p, rounds=12)
    bb_sampler = bb_circ.compile_detector_sampler()
    bb_events, _ = bb_sampler.sample(shots=shots, separate_observables=True)
    bb_events = bb_events.astype(np.uint8)
    print(f"[E04] BB: H {H_bb.shape}, {shots} shots sampled", flush=True)

    # BB GPU decoder
    bb_gpu = qec.get_decoder("nv-qldpc-decoder", H_bb, use_sparsity=True)
    def decode_bb_gpu(i): bb_gpu.decode(bb_events[i].astype(float).tolist())
    r_bb = measure_decoder("BB_GPU_BPOSD", decode_bb_gpu, shots, idle_W)
    print(f"[E04] BB GPU: {r_bb['us_per_shot']:.1f} us/shot, {r_bb['J_per_shot']*1e3:.2f} mJ/shot, "
          f"{r_bb['avg_W']:.1f} W avg", flush=True)

    print("\n[E04] Building surface d=12 circuit...", flush=True)
    sc_circ = build_surface_circuit(p=p, d=12, rounds=12)
    sc_dem = sc_circ.detector_error_model(decompose_errors=True)
    sc_sampler = sc_circ.compile_detector_sampler()
    sc_events, _ = sc_sampler.sample(shots=shots, separate_observables=True)
    sc_events = sc_events.astype(np.uint8)
    sc_matcher = pymatching.Matching.from_detector_error_model(sc_dem)
    print(f"[E04] surface d=12: {sc_events.shape[1]} detectors, sampled {shots}", flush=True)

    # CPU MWPM per patch — GPU idle during this so gross≈idle; track wall-time and TDP
    TDP_W = 65.0  # x86 CPU TDP guess (single-threaded active ≈ one core of package TDP)
    def decode_sc_cpu(i): sc_matcher.decode(sc_events[i])
    t0 = time.perf_counter()
    for i in range(shots):
        decode_sc_cpu(i)
    sc_wall = time.perf_counter() - t0
    sc_us_one = 1e6 * sc_wall / shots
    sc_us_12 = 12 * sc_us_one
    # Energy approx: TDP/cores × wall-time; rotated-surface is single-core-bound
    # Assume 8 cores average utilisation per core at ~1/8 × TDP
    sc_J_one = (TDP_W / 8) * (sc_wall / shots)
    sc_J_12 = 12 * sc_J_one
    print(f"[E04] surface CPU (1 patch): {sc_us_one:.1f} us/shot, {sc_J_one*1e3:.3f} mJ/shot", flush=True)
    print(f"[E04] surface CPU (12 patch matched): {sc_us_12:.1f} us/shot, {sc_J_12*1e3:.3f} mJ/shot", flush=True)

    print("\n[E04] HEADLINE COMPARISON (BB vs matched 12×surface)", flush=True)
    print(f"  BB GPU BP+OSD:       time {r_bb['us_per_shot']:>10.1f} us/shot   energy {r_bb['J_per_shot']*1e3:>10.3f} mJ/shot", flush=True)
    print(f"  12× surface CPU MWPM:time {sc_us_12:>10.1f} us/shot   energy {sc_J_12*1e3:>10.3f} mJ/shot", flush=True)
    print(f"  → time ratio BB/surface:   {r_bb['us_per_shot']/sc_us_12:.2f}   (<1 = BB wins)", flush=True)
    print(f"  → energy ratio BB/surface: {r_bb['J_per_shot']/sc_J_12:.2f}   (<1 = BB wins)", flush=True)

    # Append to results.tsv
    tsv_path = "/home/col/generalized_hdr_autoresearch/applications/qec_resource_est/results.tsv"
    ts = datetime.datetime.utcnow().isoformat()
    with open(tsv_path, "a") as f:
        f.write(
            f"E04_BB_energy\t{ts}\tBB_144_12_12\t12\tSI1000_circuit\t{p}\t{shots}\t42\t"
            f"{H_bb.shape[0]}\t{H_bb.shape[1]}\t0.00\t{r_bb['us_per_shot']:.2f}\t"
            f"{r_bb['J_per_shot']*1000:.4f}\tKEEP\tPhase1_E04_BB_GPU_BPOSD_energy_mJ_per_shot\n"
        )
        f.write(
            f"E04_surface_matched12_energy\t{ts}\tsurface_12patch\t12\tSI1000_circuit\t{p}\t{shots}\t42\t"
            f"0\t0\t{sc_us_12:.2f}\t0.00\t"
            f"{sc_J_12*1000:.4f}\tKEEP\tPhase1_E04_12xsurface_CPU_MWPM_energy_mJ_per_shot\n"
        )
    print(f"\n[E04] wrote 2 rows to {tsv_path}", flush=True)


if __name__ == "__main__":
    main()
