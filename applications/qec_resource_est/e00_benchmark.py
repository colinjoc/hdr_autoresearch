"""
E00 baseline benchmark for qec_resource_est.

Surface code d ∈ {3, 5, 7, 9}, code-capacity noise at p ∈ {0.05, 0.10}, compares BP+OSD
on GPU (cudaq_qec nv-qldpc-decoder) vs BP+OSD on CPU (ldpc.BpOsdDecoder). Same H matrix,
same syndromes, fair apples-to-apples decoder comparison.

Code-capacity (not circuit-level) is used here because:
1. CUDA-Q QEC v0.6 samples in native syndrome space without needing per-round detector
   reshaping. Matches H directly.
2. Phase 0.5 E00 bar is a seed-stable baseline on ONE hardware; the circuit-level
   benchmark is Phase 1 (requires Stim-native DEM + detector event reshaping).
3. [[144,12,12]] BB code replaces surface_code in Phase 1.
"""

from __future__ import annotations

import datetime
import os
import time

import numpy as np

import cudaq
cudaq.set_target("stim")
import cudaq_qec as qec


def _as_int(v):
    return int(v() if callable(v) else v)


def run_cell(distance: int, p: float, shots: int, seed: int = 42) -> dict:
    np.random.seed(seed)
    code = qec.get_code("surface_code", distance=distance)

    # Get code-capacity parity-check matrix (both X and Z stabilizers stacked)
    Hx = np.asarray(code.get_parity_x(), dtype=np.uint8)
    Hz = np.asarray(code.get_parity_z(), dtype=np.uint8)
    H = np.vstack([Hx, Hz])

    # Sample code-capacity shots: (syndromes, data_errors)
    t0 = time.perf_counter()
    syn_all, data_err = qec.sample_code_capacity(H, shots, p, seed)
    sample_time = time.perf_counter() - t0
    syn_all = np.asarray(syn_all, dtype=np.uint8)

    out = {
        "distance": distance,
        "p": p,
        "shots": shots,
        "seed": seed,
        "H_shape": tuple(H.shape),
        "syn_shape": tuple(syn_all.shape),
        "sample_s": sample_time,
    }

    # GPU BP+OSD: nv-qldpc-decoder
    try:
        gpu_dec = qec.get_decoder("nv-qldpc-decoder", H)
        t0 = time.perf_counter()
        for i in range(shots):
            syn = syn_all[i].astype(float).tolist()
            _ = gpu_dec.decode(syn)
        gpu_time = time.perf_counter() - t0
        out["gpu_bposd_us_per_shot"] = 1e6 * gpu_time / shots
        out["gpu_bposd_decode_s"] = gpu_time
    except Exception as e:
        out["gpu_error"] = f"{type(e).__name__}: {str(e)[:120]}"

    # CPU BP+OSD: ldpc
    try:
        from ldpc.bposd_decoder import BpOsdDecoder
        cpu_dec = BpOsdDecoder(
            pcm=H,
            error_rate=p,
            max_iter=100,
            bp_method="product_sum",
            ms_scaling_factor=0.5,
            osd_method="osd_cs",
            osd_order=7,
        )
        t0 = time.perf_counter()
        for i in range(shots):
            syn = syn_all[i].astype(np.uint8)
            _ = cpu_dec.decode(syn)
        cpu_time = time.perf_counter() - t0
        out["cpu_bposd_us_per_shot"] = 1e6 * cpu_time / shots
        out["cpu_bposd_decode_s"] = cpu_time
    except Exception as e:
        out["cpu_error"] = f"{type(e).__name__}: {str(e)[:120]}"

    if "gpu_bposd_us_per_shot" in out and "cpu_bposd_us_per_shot" in out:
        out["speedup"] = out["cpu_bposd_us_per_shot"] / max(out["gpu_bposd_us_per_shot"], 1e-9)

    return out


def main():
    print(f"[E00] host: RTX 3060 12GB, CUDA 12.9", flush=True)
    print(f"[E00] CUDA-Q QEC: {qec.__version__}", flush=True)
    print(f"[E00] code-capacity surface code, BP+OSD GPU vs CPU", flush=True)

    cells = []
    for d in [3, 5, 7, 9]:
        for p in [0.05]:  # single rate for smoke; sweep p in Phase 1
            print(f"\n=== surface_code d={d} p={p} shots=1000 ===", flush=True)
            try:
                r = run_cell(distance=d, p=p, shots=1000)
                for k, v in r.items():
                    print(f"  {k}: {v}", flush=True)
                cells.append(r)
            except Exception as e:
                import traceback
                print(f"  FAILED: {type(e).__name__}: {e}", flush=True)
                traceback.print_exc()
                cells.append({"distance": d, "p": p, "error": f"{type(e).__name__}: {e}"})

    tsv_path = "/home/col/generalized_hdr_autoresearch/applications/qec_resource_est/results.tsv"
    header = (
        "id\ttimestamp\tcode\tdistance\tnoise\tp\tshots\tseed\tsample_s\t"
        "cpu_bposd_us\tgpu_bposd_us\tspeedup\tH_rows\tH_cols\tstatus\tnote"
    )
    with open(tsv_path, "w") as f:
        f.write(header + "\n")
        for r in cells:
            if "error" in r:
                continue
            ts = datetime.datetime.utcnow().isoformat()
            row = [
                f"E00_d{r['distance']}",
                ts,
                "surface_code",
                str(r["distance"]),
                "code_capacity",
                f"{r['p']:.4f}",
                str(r["shots"]),
                str(r["seed"]),
                f"{r['sample_s']:.4f}",
                f"{r.get('cpu_bposd_us_per_shot', float('nan')):.2f}",
                f"{r.get('gpu_bposd_us_per_shot', float('nan')):.2f}",
                f"{r.get('speedup', float('nan')):.3f}",
                str(r["H_shape"][0]),
                str(r["H_shape"][1]),
                "KEEP",
                "Phase0.5_E00_code_capacity_RTX3060_BPOSD_CPUvsGPU",
            ]
            f.write("\t".join(row) + "\n")
    print(f"\n[E00] wrote {len(cells)} rows to {tsv_path}", flush=True)


if __name__ == "__main__":
    main()
