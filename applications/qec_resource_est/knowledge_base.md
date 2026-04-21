# knowledge_base.md — qec_resource_est

Project-scoped stylised facts distilled from the Phase 0 literature review. Each entry includes a source and an approximate value. Values marked `VERIFY` require download/measurement in Phase 1.

---

## Azure Resource Estimator defaults

- **Default physical error rate**: 10⁻³ circuit-level (SI1000 equivalent) for "qubit_gate_us_e3" — matches our pre-registered noise point.
- **Default logical-cycle time formula**: `logical_cycle_time_us = 4 * d * one_qubit_gate_time_us` for surface-code with 4-cycle syndrome schedule.
- **Default qubit-per-logical**: `2 * d² + d + 1` (rotated surface) or `2 * d² + 2d + 1` (unrotated); Azure default uses `2 * d²`.
- **Default distillation unit**: 15-to-1, 5-level nested; output infidelity ≈ 35 p_in³.
- **Default error-budget allocation**: 1/3 logical qubits, 1/3 T-distillation, 1/3 rotation synthesis.
- **Extensibility API**: `QecScheme` object is the extension point; Alice & Bob's cat extension is the reference pattern.
- **Decoder compute**: **not modelled** — this is the gap we close.

Source: Beverland et al. 2022 arXiv:2211.07629; Microsoft Learn docs 2024-07-01 (updated 2026-01-29).

## Gidney 2025 RSA-2048 reference numbers

- **Physical qubits**: <1,000,000 (target ~750k).
- **Wall-clock**: <1 week (target ~5 days).
- **Logical qubits at peak**: ~1500.
- **T-count**: ~10⁹ (cultivation-priced; equivalent pre-cultivation T-count was ~10¹⁰).
- **Noise point**: p = 10⁻³ circuit-level on SI1000-like superconducting model.
- **Cycle time assumed**: T_cyc,base = 1 μs.
- **Code**: surface code d = 27 (conservative data), d = 31 (T-factory).
- **Reaction time coefficient**: ~1 μs baseline; sweeps within paper at 0.5–5 μs.
- **Zenodo assets**: DOI 10.5281/zenodo.15347487; `code.zip` 6.2 MB CC-BY-4.0.

Source: Gidney 2025 arXiv:2505.15917.

## Bravyi 2024 BB gross code [[144,12,12]]

- **Parameters**: n = 144 physical qubits, k = 12 logical qubits, d = 12 distance.
- **Threshold**: ~0.8% circuit noise.
- **LER at p = 10⁻³**: ~10⁻⁹ at d = 12 (Bravyi et al. Nature data).
- **Decoder**: BP+OSD with 100 iterations, OSD-0 post-processor.
- **Required connectivity**: nearest-neighbour + 6 long-range couplers per qubit, 2 layers.
- **Qubit overhead vs rotated surface code at matched LER**: ~12–24× fewer physical qubits per logical.
- **Matched surface-code distance**: d ≈ 17–19 at p = 10⁻³ for 10⁻⁹ LER target (from $p_L \sim A(p/p_c)^{(d+1)/2}$).

Source: Bravyi et al. 2024 Nature (arXiv:2308.07915).

## Matched surface-code sizing

- **Rotated surface at d = 17**: 162 physical qubits per logical.
- **For 12 logical qubits** (BB block match): 12 × 162 = **1944 physical qubits** via surface vs **144 physical qubits** via BB.
- **Raw qubit ratio**: 13.5× in BB's favour. Close to Bravyi's 10–12× claim.
- **With 1.3× connectivity-cost adjustment for long-range couplers**: ratio ~10×.
- **With additional factor-2× for decoder compute (our project's expected result)**: net ratio ~5× — **still BB-favourable but materially compressed**.

## BP+OSD decoder benchmarks

- **CPU single-core** (`ldpc` v2 on Intel i9): ~3–5 ms per shot at d = 12 BB, 100 iterations.
- **CPU parallel** (`ldpc` v2 OpenMP, 16 cores): ~0.2–0.5 ms per shot.
- **GPU A100** (CUDA-Q QEC v0.4 baseline from NVIDIA blog): ~100–300 μs per shot at d = 12 BB (29–35× speedup single-shot).
- **GPU A100** (CUDA-Q QEC v0.6 with RelayBP + 19× improvement): ~20–50 μs per shot.
- **GPU RTX 3060** (our host, estimated 10–15× CPU, 2–3× slower than A100): ~200–500 μs per shot.
- **Iteration-count effect**: roughly linear — 10 iters ≈ 3× faster than 100 iters on same hardware.
- **OSD invocation rate** at p = 10⁻³: ~5–15% of decodes (well-converged BP regime).

Source: CUDA-Q QEC 0.6 release notes (2026-04-14); NVIDIA Technical Blog 2024; `ldpc` v2 README; estimated scaling for RTX 3060.

## MWPM decoder benchmarks

- **PyMatching v2 CPU single-core**: ~10⁶ errors/core-second on d = 13 surface code.
- **PyMatching v2 CPU multi-core** (8-core workstation): ~8 × 10⁶ errors/s = ~125 ns/error.
- **PyMatching v2 CPU d = 17**: ~1 μs/single-shot decode.
- **Fusion-blossom CPU parallel**: comparable per-core, better parallel scaling ~1.5× at 16 cores.
- **Micro-blossom FPGA** (Zynq, d = 17): ~10 μs per round (pipelined).
- **Riverlane LCD FPGA**: <1 μs per round at d = 17 (Nature Comm. 2025).
- **NVIDIA Ising predecoder + PyMatching hybrid** (CUDA-Q QEC v0.6 on B300 + Grace Neoverse-V2): ~2 μs per QEC round.
- **Pure MWPM-GPU**: **does not exist publicly**; Fowler's 2013 sparse MWPM was unreleased.

Source: Higgott & Gidney 2023 arXiv:2303.15933; NVIDIA CUDA-Q QEC 0.6 release notes 2026-04-14; Riverlane Nature Comm. 2025.

## Gidney 2025 reaction-time coefficients

- **Baseline T_reaction**: ~1 μs assumed (SC platform with tunable couplers).
- **Practical upper bound**: ~10 μs (slow decoder) — factors of 10 over baseline.
- **Multiplier $\mu_{react}$ for RSA**: ~1 (T-gate density low enough that reaction-time is not load-bearing).
- **Multiplier for T-heavy chemistry**: ~3–10.
- **Cultivation pipeline depth assumed**: ~10–30 in-flight magic states.
- **Reaction-time → LER coupling**: for Shor with cultivation, 10× reaction-time degradation corresponds to ~1.1× total wall-clock inflation (reported in Gidney 2025 §8).

Source: Gidney 2025 arXiv:2505.15917 §8; Bhatnagar et al. 2025 arXiv:2511.10633 analog for surface-code-only.

## Gross-code LER at p = 10⁻³

- **d = 12 BB**: ~10⁻⁹ LER per logical-qubit-round (Bravyi 2024 data).
- **d = 10 BB**: ~10⁻⁷ LER.
- **d = 14 BB**: ~10⁻¹¹ LER.
- **BP+OSD accuracy vs optimal decoder gap**: ~1.5–2× LER (Roffe 2020 benchmarks).

## GPU power specifications

- **RTX 3060** (our host): 170 W TDP, 11 W idle (measured 2026-04-20), 12 GB GDDR6, compute capability 8.6.
- **A100 SXM4**: 400 W TDP, 50 W idle, 40/80 GB HBM2e, compute capability 8.0.
- **H100 SXM**: 700 W TDP, 50 W idle, 80 GB HBM3, compute capability 9.0.
- **B200/B300**: 1000 W TDP class, 180 GB HBM3e, compute capability 10.0.
- **NVML sampling rate**: 1 Hz for `power.draw`.

Source: NVIDIA datasheets; local `nvidia-smi` output 2026-04-20.

## Per-decode energy estimates (stylised)

- **BB + BP+OSD GPU A100 (100 iters d=12)**: 250 W × 100 μs ≈ **25 μJ/decode**.
- **BB + BP+OSD GPU RTX 3060 (100 iters d=12 estimated)**: 120 W × 300 μs ≈ **36 μJ/decode**.
- **Surface + MWPM CPU (d=17, PyMatching v2)**: 12 W × 1 μs ≈ **12 μJ/decode**.
- **Surface + hybrid Ising-GPU + PyMatching CPU**: ~30 W × 2 μs ≈ **60 μJ/decode** (GPU + CPU combined).
- **FPGA LCD (Riverlane, d=17)**: ~10 W × 1 μs ≈ **10 μJ/decode**.
- **Cryogenic CMOS** (Overwater 2022 scaled): ~100 mW × 10 μs ≈ **1 μJ/decode** (but small d only).

All numbers `VERIFY` in Phase 1 toy.

## Logical-qubit-second × decoder-Joules benchmark

- **BB + BP+OSD A100** at 10³ decodes/logical-qubit-second: 25 μJ × 10³ = ~25 mJ/logical-qubit-s.
- **Surface + hybrid MWPM** at 10³ decodes/logical-qubit-second: 60 μJ × 10³ = ~60 mJ/logical-qubit-s.
- **Ratio (BB/surface on decoder J axis)**: ~0.42 at matched decode rate.
- **Qubit ratio (BB/surface)**: ~0.074 (1/13.5).
- **Combined product ratio**: 0.42 × 0.074 × (surface-wall-clock / BB-wall-clock).
- **If wall-clock is matched**: combined BB advantage is 0.42 × 0.074 = **~0.031**, i.e. BB ~32× better than surface on the joule-logical-qubit-second metric.

These are *stylised* numbers; measurement may change the 0.42 factor by ±2× (which is exactly the project's measurement goal). If decoder J shifts the ratio to ≥0.84 (i.e. 2× compression of BB advantage on decoder axis), proposal_v2 kill threshold fires.

## Tooling stack (pinned)

- Python 3.12.3 on WSL2 Ubuntu 24.04.
- CUDA 12.9 (nvcc V12.9.86, driver 576.88).
- PyTorch 2.6.0+cu124 (installed).
- CuPy 14.0.1 cu12x (installed).
- Stim (to install: `pip install stim` at pinned version 1.15.0).
- PyMatching v2 (to install: `pip install pymatching` ≥ 2.1).
- `ldpc` v2 (to install: `pip install ldpc` C++ rewrite).
- `qLDPC` (to install: `pip install qldpc` unified API).
- CUDA-Q QEC (to install from github.com/NVIDIA/cudaqx at v0.6 tag).
- Microsoft qsharp / qdk for RE (to install: `pip install qsharp`).

## Scoop-scan monitoring schedule

- **Next scan**: 2026-05-20.
- **Trigger query set**: five queries from `data_sources.md` §4.
- **Abort rule**: if a 2026+ preprint couples measured GPU decoder cost to a pre-registered compiled algorithm for BB vs matched surface, trigger proposal_v2 §4.3 pivot.
