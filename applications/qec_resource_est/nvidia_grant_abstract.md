# NVIDIA Academic Grant Program — Research Abstract (DRAFT)

**Deadline to submit: 2026-04-27.** Portal: https://www.nvidia.com/en-us/industries/higher-education-research/academic-grant-program/

---

## Project title

GPU-Decoder-Aware Resource Estimation for Quantum Fault-Tolerance: Bivariate-Bicycle vs Surface Code with Measured Classical Compute

## Principal investigator

Colin [surname] — HDR autoresearch program, 2026

## One-sentence statement

We will produce the first resource-estimation-grade comparison of IBM's `[[144,12,12]]` bivariate-bicycle (BB) gross code against the matched-overhead surface code for RSA-2048 factoring, with every classical-decoder cost (wall-clock, energy, reaction-time compounding) **measured on GPU** using NVIDIA CUDA-Q QEC v0.6, rather than assumed.

## Problem

All published fault-tolerant quantum-computing (FTQC) resource estimates — Azure Quantum Resource Estimator (Beverland 2022), Gidney–Ekerå 2025 RSA-factoring estimate (arXiv:2505.15917), the 12× qubit-overhead claim for IBM's gross code (Bravyi 2024 Nature) — treat the classical decoder as a constant-latency black box. But at d=12 on a qLDPC like the BB code, BP+OSD decoding costs orders of magnitude more compute per shot than MWPM on the surface code. No paper has folded measured GPU decoder cost into a resource-estimation-grade headline for a specific compiled algorithm. The "12× advantage" claim for qLDPC is vapour to this degree.

## What we will do

1. **Extend Azure Resource Estimator** with a decoder-compute axis (FLOPs / DRAM-bandwidth / wall-time / joules) keyed to a `decoder_latency_model(code, d, iter, batch, hardware)` lookup. Open-source as a pip-installable Python package.
2. **Measure BP+OSD wall-time + energy directly on GPU** using NVIDIA CUDA-Q QEC v0.6 at d=12 on the `[[144,12,12]]` BB code under SI1000 circuit noise at p=10⁻³. Match against the hybrid Ising-CNN-predecoder + PyMatching pipeline on the matched-overhead surface code.
3. **Apply to RSA-2048 per Gidney 2025**, reporting the composite headline (logical-qubit-seconds × measured-GPU-decoder-Joules) for both code families, with a single pre-registered decision threshold (≥2× BB-advantage shrinkage when decoder cost is folded in → "qLDPC-overhead story has a hidden dominant cost").
4. **Quantify the reaction-time sensitivity** axis Gidney 2025 flagged but did not quantify; this is the dimension industrial whitepapers typically omit and our academic-differentiation lever.

## Why NVIDIA compute is essential

The headline requires BP+OSD measurements at d=12 BB with ~100 belief-propagation iterations per shot, at millions of shots per noise point across three decoder iteration counts, two code families, and a sensitivity-grid sweep — on the order of 10⁵ A100-hours for the full paper. Our host is an RTX 3060 12GB (compute capability 8.6), which cannot hold d≥20 extrapolations or large batch sizes. The A100 headline numbers are the difference between a consumer-GPU methodology note and a PRX Quantum resource-estimation-grade result.

## Deliverables

- Open-source extended Azure Estimator plugin (pip-installable).
- Full measured benchmarking dataset: BP+OSD and hybrid MWPM wall-time + energy, at d ∈ {8, 10, 12} BB and matched surface distances {13, 15, 17}, under SI1000 noise at p ∈ {10⁻³, 3×10⁻³, 10⁻²}.
- Publication submission to PRX Quantum within 4–5 months; Quantum (Verein) as secondary venue.
- Citation of NVIDIA's CUDA-Q QEC as the enabling toolchain.

## Tooling

- **CUDA-Q QEC v0.6** (hybrid Ising-CNN-predecoder + PyMatching pipeline, BP+OSD GPU implementation) — primary.
- cuQuantum / cuTensorNet — for secondary verification against exact-ML decoders.
- Stim (sampling + detector error models), PyMatching v2 (CPU MWPM baseline), `ldpc` (CPU BP+OSD baseline), Azure Resource Estimator (baseline framework we extend).

## Requested allocation

- Approximately 2,000 A100-GPU-hours over 4 months, or equivalent credits on NVIDIA DGX Cloud / Lambda / RunPod.
- Breakdown: 500 hours smoke + baseline; 1,000 hours headline sweep; 500 hours sensitivity analysis + reviewer follow-ups.

## Timeline

- Month 1: RTX 3060 Phase 0.5 smoke runs + proposal_v3 + plugin scaffold.
- Month 2: A100 headline sweep (requires this grant).
- Month 3: Reaction-time sensitivity + plugin release + draft.
- Month 4: Revisions + arXiv submission.

---

## Notes for the user before submitting

- Replace "[surname]" with your actual surname.
- Confirm the one-paragraph project title + PI lines match NVIDIA's grant form field requirements.
- Attach a link to the arxiv pre-registration doc once Phase 0.5 Step 5 (proposal_v3) is complete — this strengthens the application.
- If the portal asks for a CV or publications list, include your other HDR / autoresearch work and the `qec_ideation` artifact as evidence of a structured research pipeline.
