# h100_housekeeping_phi — PAUSED (external hardware blocker)

**Date:** 2026-04-20
**Follow-on priority in the thermodynamics portfolio:** #2 of 8.

## What this project would do

Measure the housekeeping fraction φ directly on H100 GPU kernels (attention, MLP, AllReduce) during a controlled transformer training microbenchmark. Use NVIDIA DCGM power counters + Nsight Compute to decompose total power into (a) arithmetic compute, (b) DRAM / HBM data movement, (c) NVLink inter-GPU traffic, (d) static leakage. Report φ = P_compute / P_total per kernel with propagated uncertainty.

φ is the single most load-bearing parameter in both predecessor thermodynamic papers (`thermodynamic_info_limits` and `thermodynamic_ml_limits`) and is currently assumed, not measured. A direct measurement would turn every numerical headline in those papers from "point inside an 8-OOM band" to "within a factor of 3".

## Why paused

Requires H100-class GPU hardware with DCGM power monitoring enabled, plus permission to run kernel microbenchmarks at the instrumentation level. Neither is available in the current research environment.

Per program.md external-blocker rule: the project is paused, not killed. Resumable when H100 access + DCGM permissions are available.

## Resumption checklist

1. Confirm H100 access with DCGM read permission.
2. Install Nsight Compute CLI for per-kernel DRAM / HBM traffic accounting.
3. Pick a small transformer (e.g. GPT-2 small, ~125M params) that fits in a single H100 80 GB.
4. Run the project's Phase −0.5 scope check (proposal will be drafted at resumption).
5. Continue through the full HDR sweep per program.md.

## Related open projects

- `yaida_gns_tur_jarzynski` (priority #3) — independent of hardware, proceed first.
- `diffusion_crooks_benchmark` (priority #5) — needs GPU but a single consumer GPU suffices (not H100-instrumented).
- `lan_chemotaxis_kur` (priority #6) — pure data re-analysis, no hardware.
- `non_markovian_tur_search` (priority #8) — pure data re-analysis, no hardware.
