---
title: "Classical decoder cost narrows the qLDPC qubit advantage on consumer GPUs"
date: 2026-04-20
domain: "Quantum Computing"
blurb: "A widely-cited quantum-error-correction code saves 12× physical qubits over the surface-code alternative. On a consumer GPU, once you count the classical decoder's wall-clock and energy, the 12× qubit win becomes a 20× compute loss."
weight: 39
tags: ["quantum-error-correction", "qldpc", "decoder", "benchmark", "negative-result"]
---

*A plain-language summary. The [full technical paper](https://github.com/colinjoc/hdr_autoresearch/blob/master/applications/qec_resource_est/paper_submission.md) has the complete methods and results. See [About HDR](/hdr/) for how this work was produced.*

**Bottom line.** Published resource estimates for future quantum computers treat the classical decoder — the algorithm that reads error-syndrome bits and decides what to fix — as free. Bravyi *et al.* 2024's bivariate bicycle "gross code" is the poster child of a new code family that uses 12× fewer physical qubits than the surface code at matched distance. We measured both codes end-to-end on one consumer GPU and folded in the decoder's wall-time and energy. The 12× qubit advantage becomes a 20× wall-clock deficit and a 60×–190× energy deficit once decoder compute is counted. The contribution is the measurement, the pre-registered threshold test, and an open-source extended Azure Resource Estimator plugin with a decoder-compute axis.

## The question

Fault-tolerant quantum computers correct errors by running a small classical algorithm, thousands of times a second, that translates measured syndromes into corrections. Two decoders currently dominate: minimum-weight perfect matching (MWPM, on surface codes) and belief-propagation plus ordered statistics decoding (BP+OSD, on qLDPC codes such as the gross code). MWPM is cheap; BP+OSD is orders of magnitude more expensive on matched hardware.

A 2024 result from IBM [Bravyi *et al.* 2024] showed that the [[144,12,12]] "gross code" encodes 12 logical qubits in 288 physical qubits versus 3,444 for a matched-distance surface-code equivalent. That 12× qubit advantage is the dominant headline motivating qLDPC research. But the standard resource estimators — Azure, Litinski, Gidney-Ekerå — do not charge anything for the decoder. If the BP+OSD decoder is 20× slower than MWPM in wall-time, and 100× more energy-hungry, does the 12× qubit win survive?

## What we found

![Figure 1. Two-regime GPU vs CPU BP+OSD crossover. Log-scale per-shot wall-time versus parity-check-matrix size: GPU loses by up to 40× on small code-capacity surfaces, crosses over near 60K entries, and wins by 146× at BB circuit-level.](plots/fig1_codecap_crossover.png)

**GPU BP+OSD is not a free lunch.** On an RTX 3060, NVIDIA's CUDA-Q QEC v0.6 GPU BP+OSD decoder loses to CPU BP+OSD by factors of 2.6 to 44 on small surface codes at code-capacity noise. Only once the parity-check matrix grows above about 60,000 entries does the GPU start to win. At BB circuit-level noise with 12 syndrome rounds, the parity-check matrix has 9.8M entries and the GPU wins by 146× over CPU BP+OSD — a genuine speedup. This two-regime picture is the first contribution: it tells you when GPU decoding pays off and when it does not.

![Figure 2. BB vs matched-LER 12 × d=17 surface. Left panel: per-shot μs on log scale. Right panel: per-logical-qubit-round μs. BB GPU BP+OSD is 20× slower than matched-logical-error-rate surface CPU MWPM.](plots/fig2_bb_vs_surface.png)

**The BB qubit advantage inverts on compute.** Running the gross code at distance 12 with SI1000 circuit-level noise at error rate 10⁻³, we compared against a 12-patch distance-17 rotated surface-code encoding that reaches the same logical error rate. Both branches used the identical SI1000 per-channel noise schedule. BB on GPU BP+OSD takes 3,695 microseconds per shot. Twelve d=17 surface patches on CPU PyMatching MWPM take 188 microseconds per shot. The BB code is 19.7× slower per shot, which equates to 19.7× slower per logical-qubit-round since both branches encode the same 12 logical qubits. The physical-qubit advantage remains real — BB uses 288 physical qubits versus 6,924 for matched-LER surface, a 24× ratio — but that 24× qubit win does not translate into a wall-clock or energy win under the decoder pair available on consumer hardware in April 2026.

![Figure 3. BP+OSD iteration-count ablation. The 19.7× ratio is robust to max_iter choice: iter=10, 30, and 100 differ by less than 13% in wall-time because the post-BP OSD-CS pass dominates at all settings.](plots/fig3_iter_ablation.png)

**The result is robust to obvious knobs.** We swept BP+OSD iteration count across {10, 30, 100} and found the CPU wall-time shifts by less than 13%: BP converges well before iteration 10 and the OSD-CS-7 pass dominates. A pre-registered kill threshold of 2× shrinkage was set before data collection; the measured ratio exceeded it by ~10× on wall-time and ~30–95× on the energy bracket.

![Figure 4. GPU vs CPU BP+OSD regime map. A log-log scatter of the GPU/CPU ratio against parity-check-matrix entry count shows the crossover at ~60K entries.](plots/fig4_regime_map.png)

**Energy is between 60× and 190×.** The NVML-integrated gross GPU energy of 233 mJ per shot on BB, measured across 3,000 shots, compared against a TDP-model CPU energy upper bound for the surface branch, brackets the BB/matched-surface energy ratio between 60× (active-GPU vs CPU-TDP) and 190× (gross-GPU vs CPU-TDP). A rack-level CPU power meter would narrow this bracket and is a follow-up.

## Why that matters

Resource estimators drive architectural decisions that shape billion-dollar hardware roadmaps. The choice between a qLDPC-first surface-free architecture and a conventional surface-code architecture turns on the total cost of classical decoding at scale. If public estimates omit decoder compute — and they do — then architectural decisions are being made on a number that is off by 20× on wall-clock and 100× on energy for the currently-best qLDPC decoder on consumer hardware. Our extended Azure Resource Estimator plugin makes the decoder axis explicit.

The two-regime picture is also useful on its own. GPU acceleration of BP+OSD does not help on small surface codes and does not help on code-capacity sampling at any practical scale; it helps only when the parity-check matrix grows large enough to amortise GPU kernel-launch overhead. This is a concrete rule of thumb for anyone choosing a decoder for a specific code and hardware pair.

## What it means in practice

**For groups reporting qLDPC resource estimates.** Publish wall-clock and energy per logical-qubit-round with the decoder and hardware you actually used, not only qubit counts at the matched-distance headline. The matched-logical-error-rate comparison, not matched-distance, is the operationally relevant one.

**For hardware architects considering qLDPC-first designs.** The qubit advantage is real; the compute advantage is not, on today's decoder and consumer hardware. Expect the gap to narrow with better BP+OSD variants (ambiguity clustering, evolutionary BP+OSD, RelayBP) and purpose-built GPU kernels, but plan for a factor-of-several compute deficit relative to surface-code MWPM baselines until measured otherwise.

**For anyone running BP+OSD on a GPU.** If your parity-check matrix has fewer than about 60,000 nonzero entries, stay on CPU. GPU kernel-launch overhead will dominate until H grows past that size.

## How we did it

All measurements are from a single-host pipeline: x86-64 CPU, NVIDIA GeForce RTX 3060 12 GB, CUDA 12.9, Ubuntu 24.04, Python 3.12.3. The BB code is built from the Bravyi-compliant bivariate bicycle constructor; both code branches share the exact same SI1000 per-channel noise schedule generated by a single shared helper. Per-shot decode calls are wrapped in `time.perf_counter` with warmup excluded. GPU power is sampled inside the decode loop via NVML and trapezoid-integrated against wall-time. A pre-registered proposal document set the 2× shrinkage threshold before data collection.

The reference implementation, raw measurement tables, figure-generation artefacts, and the extended Azure Resource Estimator plugin are in the [project repository](https://github.com/colinjoc/hdr_autoresearch/tree/master/applications/qec_resource_est). The paper is prepared for submission to PRX Quantum; an NVIDIA Academic Grant application is pending for A100 follow-up runs.

## What's next

Three follow-up experiments would directly tighten the headline. First, an A100 data point — optimistic extrapolation places the BB/matched-surface ratio at ~2.1× on A100, still above the pre-registered threshold but close enough to be worth measuring. Second, a same-hardware-class GPU-vs-GPU surface baseline, contingent on CUDA-Q QEC's `pymatching` plugin supporting the parallel-edges merge strategy that SI1000 DEMs require. Third, a LER-matched-compute-budget sweep rather than a LER-matched-distance sweep, which would replace the matched-distance axis with the operationally relevant "matched classical compute" axis.
