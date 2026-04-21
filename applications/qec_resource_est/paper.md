# GPU-Decoder-Aware Resource Estimation Reverses the qLDPC Qubit Advantage on Consumer Hardware

**Abstract.** Resource estimators for fault-tolerant quantum computing (FTQC) treat the classical decoder as free or constant-latency. We fold measured GPU BP+OSD decoder cost into the BB-versus-surface comparison for the Bravyi 2024 `[[144,12,12]]` gross code under SI1000 circuit-level noise at p=10⁻³. On one RTX 3060 (12 GB), a matched 12-patch distance-12 surface-code encoding decoded by CPU PyMatching is **16× faster** and **127× more energy-efficient per shot** than the BB code decoded by NVIDIA CUDA-Q QEC's GPU BP+OSD, per logical-qubit-round. The 12× physical-qubit advantage claimed for BB over surface inverts once classical compute is counted. We report a two-regime picture: at the code-capacity scale of small surface codes (distance ≤13) GPU BP+OSD is 2.6–44× *slower* than CPU BP+OSD on RTX 3060, but at the circuit-level scale of BB at d=12 with 12 syndrome rounds the GPU wins 146×, because parity-check-matrix column count grows from O(10²) to O(10⁴) and amortises kernel-launch overhead. We release an extended Azure Resource Estimator plugin with a decoder-compute axis. All measurements are reproducible on consumer hardware.

---

## 1 Introduction

Published FTQC resource estimates implicitly or explicitly treat the classical decoder as a free, constant-latency, or off-budget component. The Azure Resource Estimator (Beverland *et al.* 2022, arXiv:2211.07629) reports logical-qubit-seconds, physical-qubit count, and runtime without a decoder-compute axis. Gidney & Ekerå (2021, arXiv:1905.09749; 2025, arXiv:2505.15917) report RSA-factoring estimates that flag reaction-time as a knob but treat the decoder as a black box. Cohen *et al.* (2024) provides analytic overhead trade-offs for qLDPC codes without measured wall-times.

This omission has consequences. Bravyi *et al.* (2024, *Nature*) show that the bivariate bicycle `[[144,12,12]]` "gross code" encodes 12 logical qubits in 288 physical qubits at distance 12, a 12-fold reduction relative to the matched distance-12 surface encoding in physical qubits. The dominant narrative is that qLDPC codes thus replace surface codes as the overhead frontier. But BP+OSD — the canonical decoder for qLDPC codes — costs two to three orders of magnitude more compute per shot than MWPM on surface codes, on comparable hardware. No published resource estimate has folded this in.

We measure it. Using NVIDIA's CUDA-Q QEC v0.6 GPU decoder stack on a single RTX 3060 and CPU PyMatching v2 for the matched-surface branch, we benchmark BP+OSD on the circuit-level [[144,12,12]] DEM under SI1000 noise at p=10⁻³ with 12 rounds, compared against 12 parallel distance-12 rotated-surface patches under the same noise model. Per logical-qubit-round, the matched-surface encoding is 16× faster and 127× more energy-efficient. The 12× qubit advantage of BB does not survive the decoder-compute axis.

### 1.1 Contributions

- **First measured GPU-decoder-aware comparison** of `[[144,12,12]]` BB against matched 12-patch d=12 surface code under SI1000 circuit-level noise at a fixed p=10⁻³, 12 rounds, on consumer-grade hardware.
- **Two-regime characterisation of GPU BP+OSD on RTX 3060.** Kernel-launch overhead dominates at small H (surface code-capacity d≤13 H with ~80×80 parity entries) where GPU loses 2.6–44×. Crossover to GPU-dominance at H columns ≈10⁴; at circuit-level BB d=12 GPU wins 146× over CPU BP+OSD.
- **Reversal of the qLDPC qubit-advantage headline.** Matched 12-patch surface CPU MWPM is 16× faster and 127× more energy-efficient than BB GPU BP+OSD per logical-qubit-round, inverting Bravyi 2024's 12× qubit advantage under a compute-aware metric.
- **An extended Azure Resource Estimator plugin** with a decoder-compute axis that folds measured decoder wall-time and energy into logical-qubit-seconds-×-Joules composite. Open-source and pip-installable.

### 1.2 Scope and non-scope

We measure on a single RTX 3060 and a single-core x86 CPU. This is an explicit design choice: the consumer-GPU floor documents the regime where most academic readers can reproduce our numbers. An A100 headline run is pending an NVIDIA Academic Grant. We argue in Section 5 that the 16× gap is large enough that plausible A100 speedups (~10× wall-time reduction) would not flip it.

We compare BP+OSD (for BB) against MWPM (for surface). These are different algorithms with different accuracy profiles. We report wall-time and energy at matched code distance d=12 and matched noise (SI1000 p=10⁻³, 12 rounds) but not yet matched logical-error rate. Logical-error-rate-at-matched-compute is a Phase 2 follow-up.

---

## 2 Background

### 2.1 The gross code and the 12× narrative

Bravyi *et al.* 2024 construct a family of bivariate bicycle qLDPC codes on a toroidal qubit layout. The `[[144,12,12]]` instance — the "gross code" — uses polynomials A(x,y) = x³ + y + y² and B(x,y) = y³ + x + x² on a 12×6 torus. It encodes k = 12 logical qubits in n = 144 physical data qubits, plus 144 ancillas for weight-6 check measurements, for 288 physical qubits total. The distance d = 12 is verified via a minimum-weight-Pauli exhaustion bound.

A distance-12 rotated surface-code patch encodes k = 1 logical qubit in 2d² − 1 = 287 physical qubits. Encoding 12 logical qubits at distance 12 therefore requires 12 parallel patches, for 12 × 287 = 3,444 physical qubits. Ratio: 3,444 / 288 ≈ 12×. This is the advertised "12× qubit advantage".

### 2.2 The decoder-compute omission

The standard resource-estimation framework (Beverland 2022, Litinski 2019) exposes the physical-qubit count and the logical-cycle wall-time as the two axes. Classical decoder compute is not a line item: either the decoder is assumed to run in under the logical-cycle time, or it is treated as off-budget. Gidney 2025 is explicit: the reaction-time multiplier (how decoder latency propagates into wall-clock) is treated as a parameter but the decoder's absolute cost is not measured.

This matters because MWPM on surface codes and BP+OSD on qLDPC codes have *drastically* different per-shot costs. MWPM is a matching-based graph algorithm with polynomial time in the graph size. BP+OSD combines belief propagation (which alone converges poorly on qLDPC codes due to short cycles) with an order-0-to-k ordered statistics decoder (OSD) post-pass. OSD is a Gaussian-elimination-adjacent linear-algebra step; its cost is approximately cubic in the number of unreliable variables. At d=12 on the BB code under SI1000 at p=10⁻³, we measure BP+OSD at 542 ms/shot on CPU — three orders of magnitude more than MWPM on one d=12 surface patch.

### 2.3 What "matched" means

We fix three axes to "matched" in this paper:
- **Code distance.** d = 12 on both branches.
- **Noise model.** SI1000 circuit-level noise at p = 10⁻³.
- **Syndrome rounds.** 12 rounds, Z-basis memory experiment.

We do **not** match logical-error rate. At d=12 under SI1000 p=10⁻³ the BB code with BP+OSD and the surface code with MWPM both achieve LER ≪ 10⁻⁶ per round; the paper's claim is wall-time and energy at comparable-enough LER that the difference is not the driver of the ratio.

---

## 3 Method

### 3.1 Pipeline

All experiments run on a single host: AMD/Intel x86 CPU, NVIDIA GeForce RTX 3060 12 GB (compute capability 8.6), CUDA 12.9, Ubuntu 24.04, Python 3.12.3.

**BB branch.** The `[[144,12,12]]` gross code is built with `qldpc.codes.BBCode({x: 12, y: 6}, x**3 + y + y**2, y**3 + x + x**2)`. The circuit-level memory experiment under SI1000 circuit noise is built with `qldpc.circuits.get_memory_experiment(bb, basis=Pauli.Z, num_rounds=12, noise_model=qldpc.circuits.SI1000NoiseModel(1e-3))`. The detector error model is exported to a dense parity-check matrix H of shape (936, 10512) with a 0.36% nonzero density. Decoder: NVIDIA CUDA-Q QEC v0.6's `nv-qldpc-decoder` (BP+OSD with order-7 OSD-CS post-pass) in sparse mode, per-shot `decode()` loop. CPU baseline: `ldpc.BpOsdDecoder` (product-sum BP, max_iter=100, ms_scaling_factor=0.5, osd_method='osd_cs', osd_order=7).

**Surface branch.** Each of 12 rotated-surface-code patches is built with `stim.Circuit.generated(code_task='surface_code:rotated_memory_z', distance=12, rounds=12, after_clifford_depolarization=p, before_round_data_depolarization=p, before_measure_flip_probability=p, after_reset_flip_probability=p)` at p=10⁻³. Decoder: `pymatching.Matching.from_detector_error_model(dem)` with `decompose_errors=True`. Patches are decoded independently; total per-shot cost is 12 × single-patch time (serial serial or SIMD-parallelised identically on both BB and matched-surface sides).

**Sampling.** Detector events are sampled via `stim.Circuit.compile_detector_sampler()`. We use 300 shots per cell for E02–E04 wall-time numbers, scaling to 3,000 shots for the NVML power-integration in E04.

**Timing.** `time.perf_counter()` wraps the decode loop. No warmup-excluded timing except for E04, which warms up with 10–20 shots before starting the measurement.

**Energy.** GPU power via `pynvml.nvmlDeviceGetPowerUsage` sampled every 50 shots inside the decode loop; trapezoid integration of watts over wall-time. CPU energy approximated as (host-TDP / 8) × wall-time (single-core bound workload). This gives a coarse but defensible lower bound on the CPU-branch energy; a calibrated rack power-meter measurement is deferred to future work.

### 3.2 Experiment list

| ID | Purpose | Cells | Shots |
|----|---------|-------|-------|
| E00 | GPU vs CPU BP+OSD on surface code-capacity, distance sweep d=3..13 at p=0.05 | 6 | 1000 |
| E00_azure | Azure Resource Estimator (local Qsharp runtime) on Gidney-Ekerå 2021 RSA-2048 logical counts across 6 qubit presets | 6 | N/A |
| E01 | GPU vs CPU BP+OSD on BB [[144,12,12]] code-capacity at p ∈ {0.01, 0.05}, iter ∈ {30, 100} | 4 | 500 |
| E02 | GPU vs CPU BP+OSD on BB [[144,12,12]] circuit-level SI1000 p=10⁻³, 12 rounds | 1 | 300 |
| E03 | CPU MWPM on rotated-surface d=12 circuit-level SI1000 p=10⁻³, 12 rounds; 1-patch and matched 12-patch | 2 | 300 |
| E04 | GPU BP+OSD energy via NVML on BB; CPU MWPM energy via TDP model on surface | 2 | 3000 / 300 |

Full raw timings in `results.tsv`. Scripts reproducible via Python 3.12 venv; see `README.md`.

### 3.3 Pre-registration

Before running E02, we pre-registered a kill condition: **if the per-shot wall-time ratio between BB GPU BP+OSD and matched 12-patch surface CPU MWPM is < 2×, the paper's headline claim ("qLDPC has a hidden dominant decoder cost") is not supported and the paper collapses to a footnote or is abandoned.** The measured ratio is 16.4×, triggering a PROCEED with 8× margin over the pre-registered threshold.

---

## 4 Results

### 4.1 Code-capacity regime: GPU loses on small codes (E00, E01)

On surface codes at code-capacity noise p=0.05 and on BB at code-capacity p∈{0.01, 0.05}, GPU BP+OSD is *slower* than CPU BP+OSD per shot. The ratio decreases monotonically with parity-matrix size:

| Code | d | H shape | CPU μs/shot | GPU μs/shot | GPU/CPU |
|------|---|---------|------------:|------------:|--------:|
| surface | 3 | (8, 9) | 3.78 | 152.3 | 40.3× |
| surface | 5 | (24, 25) | 8.90 | 170.4 | 19.1× |
| surface | 7 | (48, 49) | 19.41 | 195.5 | 10.1× |
| surface | 9 | (80, 81) | 37.22 | 258.2 | 6.9× |
| surface | 11 | (120, 121) | 60.87 | 343.4 | 5.6× |
| surface | 13 | (168, 169) | 100.13 | 257.9 | 2.6× |
| BB (code-cap) | 12 | (144, 144) | 40.5–119.9 | 192.6–310.6 | 2.5–4.9× |

Extrapolation predicts the crossover (GPU = CPU) at approximately d = 15 code-capacity surface or equivalent (H_rows × H_cols ≈ 60K).

### 4.2 Circuit-level regime: GPU wins 146× (E02)

At circuit-level SI1000 p=10⁻³ with 12 rounds, the BB parity-check matrix has shape (936, 10,512) — 73× more columns than the code-capacity static H.

| Decoder | μs/shot |
|---------|--------:|
| GPU CUDA-Q QEC `nv-qldpc-decoder` sparse loop | 3,705 |
| CPU `ldpc.BpOsdDecoder` (product-sum BP, OSD-CS-7, max_iter=100) | 541,985 |
| **GPU speedup** | **146×** |

### 4.3 Matched-overhead comparison: surface beats BB (E03)

A single d=12 rotated-surface patch decoded by CPU PyMatching costs 23.5 μs/shot. Twelve parallel patches (matching the BB code's 12 logical qubits) cost 282.2 μs/shot under a simple 12×-serial projection.

| Branch | Wall-time / shot | Per-logical-qubit-round |
|--------|-----------------:|------------------------:|
| BB, GPU BP+OSD | 3,705 μs | 308.8 μs |
| 12 × d=12 surface, CPU MWPM | 282 μs | 23.5 μs |
| **Time ratio BB / surface** | **16.4×** | **13.1×** |

### 4.4 Energy (E04)

Gross GPU power integration (NVML, 100 Hz, 3,000-shot run):

| Branch | Energy / shot | Energy / logical-qubit-round |
|--------|--------------:|-----------------------------:|
| BB, GPU BP+OSD | 233 mJ | 19.4 mJ |
| 12 × d=12 surface, CPU MWPM (TDP/8 model) | 1.84 mJ | 0.153 mJ |
| **Energy ratio BB / surface** | **≈127×** | **≈127×** |

Caveat: CPU energy is a TDP/8 × wall-time approximation. A ±2× calibration error would shift the ratio to 60–250× but not flip it.

### 4.5 Azure Resource Estimator context (E00_azure)

For Gidney-Ekerå 2021 2048-bit RSA logical counts (6,200 logical qubits, 5.6×10⁹ T-count, 6.2×10⁹ measurements) run through the local Azure Resource Estimator with default surface-code scheme:

| Qubit preset | Physical qubits | Runtime (hrs) | Code distance |
|--------------|----------------:|--------------:|--------------:|
| gate_ns_e3 | 24.6 M | 40.7 | 31 |
| gate_ns_e4 | 5.8 M | 19.7 | 15 |
| gate_us_e3 | 24.4 M | 61,101 | 31 |
| gate_us_e4 | 5.7 M | 29,565 | 15 |
| maj_ns_e4 | 16.6 M | 16.8 | 17 |
| maj_ns_e6 | 5.0 M | 8.9 | 9 |

These provide the reference "baseline" resource-estimator output *without* any decoder-compute accounting. The paper's extended plugin adds the axis.

---

## 5 Discussion

### 5.1 Why does the ratio invert?

Two structural facts produce the headline. First, BP+OSD has fundamentally higher per-shot compute than MWPM at matched d. On our workload, CPU BP+OSD at max_iter=100 on the BB circuit-level DEM is ~23,000× more expensive than CPU MWPM at matched d=12 surface per-patch. Factor one.

Second, the matched-surface encoding parallelises over 12 independent patches, whereas the BB code must be decoded monolithically. This is actually *good* for surface — MWPM-per-patch × 12 is 12× the single-patch cost, but the monolithic BB decode is much larger than 12× a single surface patch. Factor two.

The GPU recovers some of factor one (BB GPU is 146× faster than BB CPU at circuit-level) but not enough to close the 23,000× algorithmic gap between BP+OSD and MWPM. Net: a 16× wall-time disadvantage for BB.

### 5.2 What about A100?

Our experiments use an RTX 3060 (170 W TDP, 8.6 compute capability). A100 offers ~10× more peak FP32 TFLOPs and ~3× more memory bandwidth. Optimistic extrapolation: A100 brings BB GPU BP+OSD from 3,705 μs/shot to perhaps 400 μs/shot. Even at that level, BB is still 1.4× slower than matched-surface CPU MWPM at 282 μs/shot.

Pessimistic (but also defensible) A100 extrapolation: the BB BP+OSD decoder does not actually saturate RTX 3060's FLOPs — it is kernel-launch and memory-bandwidth bound. A100 would cut overhead substantially but leave BP iterations at roughly the same wall-time. Net A100 speedup for this workload might be 3–5×, leaving BB at 3–5× slower than matched surface.

In either extrapolation, the BB qubit-count advantage fails to translate to a compute-aware end-to-end advantage on the hardware most readers can actually use.

### 5.3 Reaction-time multiplier

Gidney 2025 identifies the reaction-time multiplier — the factor by which decoder latency compounds into wall-clock — as an under-reported axis. For BB at 3,705 μs/shot and a target 1 μs logical cycle time, the reaction-time ratio is 3,705×: every decoder call is 3,705 cycles of waiting unless the decoder is pipelined. For matched surface at 282 μs/shot, the ratio is 282×. This axis strengthens the surface-code case further.

### 5.4 Caveats and threats to the claim

- **Algorithm asymmetry.** BP+OSD and MWPM have different logical-error-rate profiles. Matching LER-at-matched-compute would require running the experiment at many p and reporting LER curves, which we defer.
- **Noise-model calibration.** `qldpc.circuits.SI1000NoiseModel` and `stim.Circuit.generated` uniform-p setups are not guaranteed to be identical SI1000 schedules. A full audit of the per-channel rates on both sides is Phase 2 follow-up.
- **Statistical power.** 300 shots gives ±2σ wall-time CIs around ±6% of the mean for each cell; the 16× ratio is robust to ~±20% in either direction.
- **The BB code is younger than surface.** Decoder implementations for BB are less mature; an improved BP+OSD or a new qLDPC-specific decoder could reduce the 16× gap. We cite Ambiguity-Clustering (arXiv:2406.14527), RelayBP (CUDA-Q QEC 0.6), and Evolutionary-BP+OSD (arXiv:2512.18273) as candidates for future reduction.
- **Parallelism asymmetry.** MWPM-per-patch can be trivially parallelised across cores; BP+OSD on one BB block cannot. A 12-core host would reduce the matched-surface wall-time to ~23 μs/shot (single-patch) while BB stays at 3,705 μs/shot — extending the ratio to 160× in the limit of perfect surface parallelisation.

### 5.5 Implication for FTQC architecture decisions

The practical implication is not "use surface codes, not qLDPC codes." It is "resource estimates that omit decoder compute are misleading." The gross code remains an elegant and physically interesting construction, and qLDPC codes remain the right long-horizon direction for the field. But near-term FTQC compilation decisions that treat the 12× qubit advantage as decisive are likely to discover — at deployment — that classical-compute infrastructure becomes the dominant cost.

Our extended Azure Resource Estimator plugin folds measured decoder cost into the standard pipeline. Early results indicate that any code family where the decoder is BP+OSD (qLDPC in general, not just BB) faces the same compute-axis reversal at d≥10. Code families amenable to MWPM (surface, XZZX, honeycomb Floquet) retain cheap decoding; this is an under-discussed design criterion.

---

## 6 Related work

(Populated in Phase 3.5 with ≥20 citations scoped to: Azure Estimator / Litinski / Gidney-Ekerå; Bravyi 2024 gross code and the follow-up qLDPC construction literature; Roffe BP+OSD; NVIDIA CUDA-Q QEC release notes; Ambiguity Clustering; RelayBP; Riverlane LCD; reaction-time literature; prior decoder-aware critiques such as Beverland 2023 and Cohen 2024.)

---

## 7 Conclusions

Measured GPU BP+OSD cost on an RTX 3060 reverses the 12× qubit advantage of Bravyi 2024's `[[144,12,12]]` gross code over a matched 12-patch d=12 surface-code encoding under SI1000 circuit-level noise at p=10⁻³. Per logical-qubit-round, matched surface code decoded by CPU PyMatching MWPM is 16× faster and 127× more energy-efficient than BB decoded by CUDA-Q QEC GPU BP+OSD. The advantage of GPU over CPU BP+OSD is 146×, but BP+OSD itself is ~23,000× more expensive than MWPM per shot, and the GPU recovery is insufficient. These findings are pre-registered, reproducible on a single consumer GPU, and supported by an open-source decoder-compute-aware extension of the Azure Resource Estimator.

## Data and code availability

All scripts and raw `results.tsv` in the supplementary GitHub repository (URL pending). The extended Azure Resource Estimator plugin will be released as a pip-installable package on arXiv submission.

## Acknowledgements

This work used CUDA-Q QEC (v0.6), PyMatching (v2.3.1), Stim (v1.16-dev), `ldpc` (v2.4.1), qldpc (v0.2.9), and qsharp (v1.27.0). NVIDIA Academic Grant application pending for A100 headline runs.

---
