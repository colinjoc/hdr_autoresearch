# design_variables.md — qec_resource_est

Pre-registered design variables and feature candidates for the measured-decoder-aware BB-vs-surface resource estimate. 20+ variables, each justified.

The variables partition into four layers: (A) **physical / noise**, (B) **code / QEC scheme**, (C) **decoder / compute**, (D) **algorithm / compilation**. The pre-registered kill-gate in proposal_v2 §4.1 uses a subset (marked PRIMARY); the rest are sensitivity / ablation axes (SECONDARY). Variables marked FIXED are pre-registered at a single value.

---

## Layer A — Physical / noise parameters

### A1. Physical error rate p **[FIXED]**
- **Committed value**: p = 10⁻³ circuit-level, SI1000 equivalent.
- **Justification**: Bravyi 2024, Gidney 2025, and Beverland 2022 all use this as a canonical noise point. Pre-registered to avoid post-hoc sliding.
- **Sensitivity**: off-point check at p = 5 × 10⁻⁴ and p = 2 × 10⁻³ in appendix (requested by Phase 0.25 reviewer, minor).

### A2. Noise model **[FIXED]**
- **Committed value**: SI1000 (Stim superconducting-inspired 1000 circuit-noise, single-qubit + two-qubit + measurement + idle).
- **Justification**: most-cited circuit-level noise baseline; enables direct comparison with Bravyi 2024 and Gidney 2025.
- **Sensitivity**: none at headline level; Phase 3 appendix may include biased-noise variant.

### A3. Syndrome-extraction cycle time T_cyc,base **[FIXED]**
- **Committed value**: 1 μs (matches Gidney 2025 superconducting assumption).
- **Justification**: enables direct comparison with published RSA estimates.
- **Sensitivity**: robustness check in appendix at 500 ns and 2 μs.

---

## Layer B — Code / QEC scheme parameters

### B1. Code family **[FIXED / bifurcated]**
- **BB branch**: [[144,12,12]] bivariate bicycle (Bravyi 2024 gross code).
- **Surface branch**: rotated surface code at matched d (see B2).
- **Justification**: Bravyi 2024 is the canonical published BB code; rotated surface is the canonical baseline.

### B2. Code distance d **[PRIMARY]**
- **BB committed**: d = 12 for Phase 2 headline; d = 6, 8, 10, 14 as ablation.
- **Surface committed**: d = 17 for Phase 2 headline (matched LER target); d = 9, 13, 15, 19 as ablation.
- **Phase 0 toy gate**: BB d = 6 vs surface d = 9.
- **Justification**: d = 12 BB is the Nature-published code; d = 17 surface is the matched-LER distance at p = 10⁻³.
- **Sensitivity**: d swept over full ablation range to produce the cost vs d scaling curves.

### B3. Matched-LER target **[FIXED]**
- **Committed value**: 10⁻⁹ per logical-qubit-round.
- **Justification**: utility-scale FTQC target; matches Gidney 2025's effective target.
- **Sensitivity**: 10⁻⁸ and 10⁻¹⁰ as appendix sensitivities.

### B4. Surface-code variant **[FIXED]**
- **Committed value**: rotated surface code (Bombin-MartinDelgado 2007).
- **Justification**: canonical low-qubit-count surface-code layout; matched to Gidney 2025's implicit choice.

### B5. BB code variant **[FIXED]**
- **Committed value**: [[144,12,12]] gross code (Bravyi 2024).
- **Justification**: reference Nature paper. Alternative [[144,14,14]] (Symons et al. 2025 arXiv:2511.13560) is future work.

### B6. Connectivity cost adjustment factor **[PRIMARY]**
- **Committed value**: swept over {1.0, 1.2, 1.5} as a modelling choice for BB long-range overhead.
- **Justification**: different platforms (SC vs NA vs photonic) price long-range differently; our metric should expose sensitivity to the choice.

---

## Layer C — Decoder / compute parameters

### C1. BB decoder **[FIXED]**
- **Committed value**: BP+OSD from CUDA-Q QEC v0.6 pinned at commit hash at Phase 1 kickoff.
- **Ablation baselines**: (i) CPU `ldpc` v2 BP+OSD; (ii) CUDA-Q QEC RelayBP (GPU) at single configuration.
- **Justification**: matches Bravyi 2024's decoder choice; CUDA-Q QEC is the standard GPU implementation.

### C2. Surface decoder **[FIXED]**
- **Committed value**: hybrid pipeline — NVIDIA Ising CNN predecoder on GPU (TensorRT FP16) + PyMatching v2 on CPU (CUDA-Q QEC v0.6 integration).
- **Ablation baselines**: (i) PyMatching v2 CPU alone; (ii) correlated-matching variant if available in CUDA-Q QEC.
- **Justification**: **This is the reframe from proposal_v2 (R-PER-1a in data_sources.md §3.3).** Pure MWPM-GPU does not exist publicly. The hybrid pipeline is the best available "GPU-accelerated MWPM" path.

### C3. BP+OSD iteration count **[PRIMARY]**
- **Committed sweep**: {10, 30, 100}.
- **Justification**: brackets the operating space per Panteleev-Kalachev / Roffe / Bravyi defaults. Headline uses 100; 10 and 30 are ablation.

### C4. Decoder batch size **[SECONDARY]**
- **Committed values**: batch ∈ {1, 100, 1000} for throughput-mode benchmarks.
- **Justification**: batched decoding better utilises GPU; single-shot is more realistic for reaction-time-critical operations. Both are reportable.

### C5. GPU hardware **[FIXED; documented gap]**
- **Phase 0 toy**: RTX 3060 12 GB (local).
- **Phase 2 headline**: A100 or H100 (NVIDIA Academic Grant Program if awarded, or rental $300 fallback).
- **Justification**: documented in `data_sources.md` R-PER-1b.

### C6. Power-measurement methodology **[FIXED]**
- **Committed value**: NVML `power.draw` 1 Hz sampling, idle-subtracted, thermal-steady-state (5 min pre-run), aggregated 1 s windows, wall-plug + GPU-rail both reported.
- **Justification**: MLPerf GPU power methodology; pre-empts Phase 0.25 reviewer concern 4a.

### C7. Reaction-time multiplier $\mu_{react}$ **[PRIMARY]**
- **Committed sweep**: {1, 3, 10}.
- **Justification**: Gidney 2025 range; {1,3,10} covers baseline / moderate / worst-case SC platforms.

### C8. Decoder convergence criterion **[SECONDARY]**
- **Committed value**: max-iter fixed (not convergence-based); default OSD-0 invocation on non-convergence.
- **Ablation**: OSD-10 variant in Phase 3 appendix.
- **Justification**: deterministic iteration count is reproducible; convergence-based stops complicate power accounting.

---

## Layer D — Algorithm / compilation parameters

### D1. Target algorithm **[FIXED]**
- **Committed value**: Shor factoring of RSA-2048 compiled per Gidney 2025 arXiv:2505.15917.
- **Justification**: pre-registered single-algorithm headline; matches Phase 0.25 reviewer Obj 1.

### D2. Logical-qubit count at peak **[derived]**
- **Committed value**: ~1500 (Gidney 2025 default).
- **Justification**: derived from Gidney 2025 compiled circuit; not swept.

### D3. T-count **[derived]**
- **Committed value**: ~10⁹ (cultivation-priced).
- **Justification**: derived; sensitivity to T-count uncertainty is minor once cultivation throughput is fixed.

### D4. Magic-state factory protocol **[FIXED]**
- **Committed value**: magic-state cultivation (Gidney-Shutty-Jones 2024) on both BB and surface branches.
- **Justification**: cultivation is the current state-of-the-art and is Gidney 2025's default.
- **Future work**: in-situ qLDPC injection (arXiv:2604.05126, April 2026) as a Phase 4+ extension.

### D5. Cultivation pipeline depth **[SECONDARY sensitivity]**
- **Committed values**: {10, 20, 30}.
- **Justification**: pipeline depth affects reaction-time-coupled throughput; sensitivity to this axis is a natural companion to $\mu_{react}$.

### D6. Windowed arithmetic window size **[FIXED]**
- **Committed value**: Gidney 2025 default (n_window = 4 for RSA-2048).
- **Justification**: not under investigation in this paper.

### D7. Compiled-circuit source **[FIXED]**
- **Committed value**: Gidney 2025 Zenodo DOI 10.5281/zenodo.15347487.
- **Justification**: reproducibility.

### D8. Error-budget allocation **[FIXED]**
- **Committed value**: Azure default (1/3 logical / 1/3 distillation / 1/3 rotation).
- **Justification**: standard; not under investigation.

---

## Cross-cutting metrics (what we report)

### M1. **Headline metric** — logical-qubit-seconds × measured GPU-decoder-Joules.
### M2. **Factor metrics** — logical-qubit-seconds *and* decoder-Joules reported separately (per R-PER-2 in research_queue.md).
### M3. **BB/surface ratio** — of the headline metric, min and max across the pre-registered grid.
### M4. **Phase 0 kill ratio** — `total_cost_BB / total_cost_surface` at toy d = 6 BB vs d = 9 surface, p = 10⁻³. KILL if ≥1.2× in **no** cell of the grid.
### M5. **LER match quality** — ratio of achieved BB LER to achieved surface LER at matched distance choice; should be within 0.5–2× for the comparison to be valid.
### M6. **Connectivity-adjusted BB qubit count** — raw BB qubit count × B6 connectivity factor.
### M7. **Wall-plug vs GPU-rail energy** — both reported (transparency on measurement methodology).
### M8. **Iteration-count ablation curves** — headline metric vs BP+OSD iterations for both codes.

---

## Summary — 22 design variables

A-layer: A1, A2, A3 (3).
B-layer: B1, B2, B3, B4, B5, B6 (6).
C-layer: C1, C2, C3, C4, C5, C6, C7, C8 (8).
D-layer: D1, D2, D3, D4, D5, D6, D7, D8 (8) — but D2, D3 are derived so the independent count is 6.

**Total independent design variables: 3 + 6 + 8 + 6 = 23.**
**Total sweep variables at headline (PRIMARY): B2, B6, C3, C7, D5 = 5 axes.**
**Total fixed pre-registered: 14.**
**Total ablation / secondary: 4.**

Meets the ≥15 variable bar with margin.
