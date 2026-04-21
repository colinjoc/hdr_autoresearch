"""
E01: BB [[144,12,12]] gross code under code-capacity noise.

BP+OSD GPU (nv-qldpc-decoder) vs CPU (ldpc.BpOsdDecoder) on the [[144,12,12]] Bravyi 2024
gross code. This is the Phase 1 first run — real benchmark at the paper's headline code.

Code-capacity is the Phase 1 baseline; circuit-level DEM is E02 (requires building the
Stim memory circuit manually because CUDA-Q QEC does not ship BB as a built-in code).
"""

from __future__ import annotations
import datetime
import time

import numpy as np
import sympy
from qldpc.codes import BBCode

import cudaq
cudaq.set_target("stim")
import cudaq_qec as qec
from ldpc.bposd_decoder import BpOsdDecoder


def build_bb_gross() -> tuple[np.ndarray, dict]:
    x, y = sympy.symbols("x y")
    poly_a = x**3 + y + y**2
    poly_b = y**3 + x + x**2
    bb = BBCode({x: 12, y: 6}, poly_a, poly_b)
    # Extract parity-check matrices. CSSCode stores X-check and Z-check matrices.
    Hx = np.asarray(bb.matrix_x, dtype=np.uint8)
    Hz = np.asarray(bb.matrix_z, dtype=np.uint8)
    H = np.vstack([Hx, Hz])
    info = {
        "n": bb.num_qubits,
        "k": bb.dimension,
        "H_shape": H.shape,
        "Hx_shape": Hx.shape,
        "Hz_shape": Hz.shape,
    }
    return H, info


def run_iter_count(H: np.ndarray, shots: int, p: float, max_iter: int, seed: int = 42) -> dict:
    np.random.seed(seed)
    syn_all, _ = qec.sample_code_capacity(H, shots, p, seed)
    syn_all = np.asarray(syn_all, dtype=np.uint8)

    # GPU nv-qldpc-decoder (BP+OSD)
    gpu = qec.get_decoder("nv-qldpc-decoder", H)
    t0 = time.perf_counter()
    for i in range(shots):
        gpu.decode(syn_all[i].astype(float).tolist())
    gpu_s = time.perf_counter() - t0

    # CPU ldpc BP+OSD
    cpu = BpOsdDecoder(
        pcm=H,
        error_rate=p,
        max_iter=max_iter,
        bp_method="product_sum",
        ms_scaling_factor=0.5,
        osd_method="osd_cs",
        osd_order=7,
    )
    t0 = time.perf_counter()
    for i in range(shots):
        cpu.decode(syn_all[i].astype(np.uint8))
    cpu_s = time.perf_counter() - t0

    return {
        "shots": shots,
        "p": p,
        "max_iter": max_iter,
        "gpu_us_per_shot": 1e6 * gpu_s / shots,
        "cpu_us_per_shot": 1e6 * cpu_s / shots,
        "gpu_over_cpu": gpu_s / cpu_s,
    }


def main():
    print("[E01] [[144,12,12]] BB gross code code-capacity on RTX 3060", flush=True)
    H, info = build_bb_gross()
    print(f"[E01] BB code info: {info}", flush=True)

    cells = []
    shots = 500  # BB is heavier per shot; start modest
    for p in [0.01, 0.05]:
        for max_iter in [30, 100]:
            print(f"\n=== BB p={p} iter={max_iter} shots={shots} ===", flush=True)
            try:
                r = run_iter_count(H, shots, p, max_iter)
                for k, v in r.items():
                    print(f"  {k}: {v}", flush=True)
                cells.append(r)
            except Exception as e:
                import traceback
                print(f"  FAILED: {type(e).__name__}: {e}", flush=True)
                traceback.print_exc()

    # Append to results.tsv
    tsv_path = "/home/col/generalized_hdr_autoresearch/applications/qec_resource_est/results.tsv"
    with open(tsv_path, "a") as f:
        for r in cells:
            ts = datetime.datetime.utcnow().isoformat()
            line = (
                f"E01_BB_iter{r['max_iter']}_p{r['p']}\t{ts}\tBB_144_12_12\t12\t"
                f"code_capacity\t{r['p']}\t{r['shots']}\t42\t"
                f"{H.shape[0]}\t{H.shape[1]}\t"
                f"{r['cpu_us_per_shot']:.2f}\t{r['gpu_us_per_shot']:.2f}\t"
                f"{r['gpu_over_cpu']:.3f}\tKEEP\t"
                f"Phase1_E01_BB_144_code_capacity_RTX3060_BPOSD_iter{r['max_iter']}\n"
            )
            f.write(line)
    print(f"\n[E01] appended {len(cells)} rows to {tsv_path}")


if __name__ == "__main__":
    main()
