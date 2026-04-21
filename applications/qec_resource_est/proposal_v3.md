# Proposal v3 — GPU-Decoder-Aware Resource Estimation for qLDPC vs Surface Code

Supersedes proposal_v2 (which cleared Phase 0.25 PROCEED tight) with factual corrections from Phase 0 smoke test (R-PER-1a, R-PER-1b) and the E00 baseline executed 2026-04-21.

## 1. Problem

FTQC resource estimators — Azure (Beverland 2022), Gidney-Ekerå (2021 arXiv:1905.09749, 2025 arXiv:2505.15917), Litinski 2019 (arXiv:1808.02892), Bravyi 2024 (Nature) for the `[[144,12,12]]` BB gross code — treat the classical decoder as constant-latency or free. At d=12 on a qLDPC, BP+OSD costs orders of magnitude more compute per shot than MWPM on the matched surface code. No paper folds **measured** GPU decoder cost into a resource-estimation-grade headline for a specific compiled algorithm. The "12× qubit advantage" of BB over surface (Bravyi 2024) is untested under this lens.

## 2. Claim (falsifiable)

**Headline (retitled — FPGA dropped, GPU locked in).** The **first GPU-decoder-aware resource estimate for RSA-2048**. Single pre-registered algorithm (Gidney 2025 RSA-2048 compiled circuit, arXiv:2505.15917), single pre-registered noise point (p = 10⁻³ circuit noise, SI1000), single composite metric (logical-qubit-seconds × measured GPU-decoder-Joules), single pre-registered decision threshold: **if the BB advantage shrinks by ≥2× once measured GPU-decoder cost is folded in, the qLDPC-overhead story has a hidden dominant cost**.

**Two factors reported separately** alongside the composite (per Phase 0.25 reviewer note): logical-qubit-seconds and decoder-Joules, so the composite cannot be gamed by offsetting swaps.

## 3. Method sketch (revised from v2)

### 3.1 Decoder pipeline — hybrid, not pure (R-PER-1a)

Phase 0 smoke established that **a pure MWPM-GPU does not exist publicly**: PyMatching v2 is CPU-only; a CUDA branch of PyMatching has not been released; Fowler sparse MWPM was never published. NVIDIA's "real-time MWPM" path in CUDA-Q QEC v0.6 is a **hybrid Ising-CNN pre-decoder (GPU) + PyMatching (CPU)** pipeline. Proposal v3 therefore commits to:

- **BB decoder (primary):** NVIDIA CUDA-Q QEC v0.6 `nv-qldpc-decoder` (BP + OSD-CS, GPU), pinned at a specific commit hash before Phase 1 kickoff.
- **Surface decoder (baseline):** CUDA-Q QEC v0.6 hybrid Ising-CNN-predecoder (GPU) + PyMatching v2 (CPU), same commit-hash lock.
- **Ablation baselines:** CPU `ldpc.BpOsdDecoder` v2.4 (pure CPU BP+OSD), CPU PyMatching v2 (pure CPU MWPM).
- **Methods disclosure:** paper will state the hybrid nature explicitly; no "pure GPU MWPM" claim anywhere.

### 3.2 Hardware — RTX 3060 floor + A100 headline (R-PER-1b)

Phase 0 confirmed the author's host: RTX 3060 12 GB (compute capability 8.6), CUDA 12.9. A100 access is pending:
- **NVIDIA Academic Grant** application submitted by 2026-04-27 (abstract in `nvidia_grant_abstract.md`).
- **Fallback:** $300 Lambda Labs / RunPod rental for the A100 headline run if the grant does not land by 2026-06.

**Paper will report both** RTX 3060 consumer-GPU numbers and A100 numbers side by side. The consumer-GPU floor is independently useful: academic readers rarely have A100 access, and the 3060 numbers document the regime where any GPU advantage vanishes.

### 3.3 Extended Azure Estimator plugin

Extend the Azure Resource Estimator with a decoder-compute axis. New input: `decoder_latency_model(code, d, iter, batch, hardware)` lookup table populated from measurements. Output: (logical-qubit-seconds, decoder-Joules, composite). Open-source as a pip-installable Python package before arXiv.

### 3.4 Benchmark matrix (pre-registered)

| Axis | Pre-registered values |
|---|---|
| Code | `[[144,12,12]]` BB (Bravyi 2024 A = x³+y+y², B = y³+x+x² on 12×6 torus) + matched-overhead surface code (d ∈ {15, 17, 19}) |
| Noise | SI1000 circuit noise, p = 10⁻³ |
| Decoder iteration count | {10, 30, 100} |
| Batch size | {1, 1024} |
| Hardware | {RTX 3060, A100 — pending grant} |
| Algorithm | RSA-2048, Gidney 2025 compiled circuit |
| Metric | (logical-qubit-seconds, decoder-Joules, composite = product) |
| Decision threshold | 2× shrinkage in BB-vs-surface ratio triggers "qLDPC overhead is hidden" paper claim |

## 4. Kill-conditions (pre-registered, unchanged from v2)

### 4.1 Sensitivity kill

Phase 1 runs the sensitivity analysis on a **d=6 BB vs d=9 surface** toy (CUDA-Q QEC circuit-level DEM) at p=10⁻³. If the ratio `total_cost_BB / total_cost_surface` varies by less than **1.2×** across the pre-registered parameter grid, the paper collapses to a footnote. Downgrade or abandon.

### 4.2 Measurement kill

If CUDA-Q QEC `nv-qldpc-decoder` at d=12 BB cannot be wall-clock-measured on RTX 3060 within Phase 0.5 memory/latency budget, downgrade to smaller d and re-scope. **Phase 0 E00 already measured** GPU and CPU BP+OSD on surface code up to d=13 code-capacity — the crossover extrapolation predicts d=12 BB circuit-level is GPU-dominated (see `phase_0_5_findings.md` §2). This kill is lower-probability than v2 estimated.

### 4.3 Scoop kill

If Riverlane / NVIDIA / IBM publish a comparable decoder-compute-aware estimator during Phase 0.5–Phase 1, pivot to the reaction-time-sensitivity axis only (academic-differentiated) or abandon. Monthly arXiv + NVIDIA-blog scans from 2026-05-20. Phase 0 confirmed no 2026 preprint currently overlaps — niche still open.

## 5. Phase 0 amendments absorbed (new in v3)

| Amendment | Source | Effect |
|---|---|---|
| R-PER-1a hybrid MWPM pipeline | `data_sources.md` §3 — Phase 0 smoke test | §3.1 above; paper methods disclose hybrid nature |
| R-PER-1b RTX 3060 + grant fallback | `data_sources.md` §2 | §3.2 above; dual-hardware reporting |
| E00 surface-code baseline (d ∈ {3,5,7,9,11,13} code-capacity) | `results.tsv` + `phase_0_5_findings.md` | Confirms crossover trend; strengthens kill §4.2 |
| E00_azure RSA-2048 baseline (6 qubit presets) | `results.tsv` | Reference for proposal §3.4; confirms Gidney-Ekerå 2021 sanity |

## 6. Load-bearing parameters (revised table)

| Parameter | v3 commitment | Sensitivity plan |
|---|---|---|
| Target algorithm | RSA-2048, Gidney 2025 compiled circuit (arXiv:2505.15917) | Fixed |
| Noise point | p = 10⁻³ SI1000 circuit noise | Fixed |
| Composite metric | logical-qubit-seconds × decoder-Joules; reported alongside two factors separately | Fixed |
| Decision threshold | ≥2× BB-advantage shrinkage | Fixed |
| BP+OSD GPU runtime | MEASURED on author's RTX 3060 via CUDA-Q QEC; A100 pending grant | E00 complete for d ≤ 13 surface code-capacity; Phase 1 extends to d=12 BB circuit-level |
| Hybrid MWPM-GPU runtime | CUDA-Q QEC v0.6 Ising-CNN-predecoder + PyMatching; MEASURED | Phase 1 |
| Reaction-time multiplier | Full sweep {1, 3, 10} | Reported as sensitivity axis |
| BP+OSD iteration count | {10, 30, 100} | Ablation axis |
| Decoder energy per shot | MEASURED via NVML sampling in Phase 1 | Phase 1 |

## 7. Target venues (unchanged from v2)

**Primary: PRX Quantum.** Fit — resource-estimation papers. Anticipated objection "novelty beyond Cohen 2024 + Azure estimator" pre-empted by measured decoder numbers, reaction-time sensitivity axis, and the RTX 3060 consumer-GPU floor.

**Secondary: Quantum (Verein).** Fit — open-access, QEC-heavy, tolerant of tool papers.

## 8. Open-source commitment

Extended Azure-estimator plugin (pip-installable Python package); all measurement scripts + A100 + RTX 3060 benchmark data released on publication.

## 9. Timing

- **Phase 0.5 (completed 2026-04-21):** venv + CUDA-Q QEC 0.6 installed; E00 surface-code BP+OSD sweep (6 cells); E00_azure RSA-2048 sweep (6 qubit presets); this proposal_v3; NVIDIA grant abstract drafted.
- **Phase 1 (2026-04-22 → 2026-05-31):** BB d=12 circuit-level DEM + full benchmark matrix on RTX 3060; batched-decode investigation; iteration-count ablation; NVML energy sampling; extended Azure plugin v0.1.
- **Phase 1 A100 cells (pending grant award):** A100 headline numbers; full open-source estimator v1.0.
- **Phase 2 (June 2026):** interaction sweep + adversarial reviewer.
- **Phase 3 (July 2026):** paper draft.
- **Phase 3.5 (August 2026):** paper reviewer + revisions.
- **arXiv (September 2026).**

Scoop-risk timeline: 4–5 months to arXiv from v3 freeze. Pre-registered algorithm + metric + threshold + open-source tooling is the durable academic differentiator from any vendor whitepaper that may appear in the interim.
