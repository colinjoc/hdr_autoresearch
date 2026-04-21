# §6 Related Work — draft for paper_v3

Covers ≥20 citations across: resource estimation, BP+OSD decoders, MWPM decoders, qLDPC codes, GPU QEC, NVIDIA CUDA-Q QEC, reaction-time, prior decoder-aware critiques.

---

## Resource-estimation frameworks

- **Beverland et al. 2022 (arXiv:2211.07629).** "Assessing requirements for scaling to practical quantum advantage" — the Azure Resource Estimator. Establishes the standard physical-qubit + runtime + distillation framework; decoder is implicit and off-budget.
- **Gidney & Ekerå 2021 (arXiv:1905.09749).** "How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits." Canonical Shor-RSA resource estimate; flags reaction-time but treats decoder as black-box.
- **Gidney 2025 (arXiv:2505.15917).** "How to factor 2048 bit RSA integers with less than a million noisy qubits." Revised RSA estimate exposing reaction-time sensitivity as a first-class knob; we build on this.
- **Litinski 2019 (arXiv:1808.02892).** "A Game of Surface Codes: Large-scale quantum computations with lattice surgery." PBC compilation + space-time accounting; no decoder axis.
- **Cohen et al. 2024.** qLDPC overhead vs decoder cost analytic trade-off. Analytic prediction without measurements; our paper is the empirical validation.
- **Bravyi et al. 2024 (Nature).** `[[144,12,12]]` gross code, 12× qubit overhead claim. This paper's primary target.

## Bivariate bicycle and related qLDPC constructions

- **Panteleev & Kalachev 2022 (arXiv:2111.03654).** "Asymptotically good quantum and locally testable classical LDPC codes" — breakthrough qLDPC construction; establishes the family of which BB is a simple instance.
- **Symons, Rajput & Browne 2025 (arXiv:2511.13560).** "Sequences of Bivariate Bicycle Codes from Covering Graphs" — new BB families including `[[64,14,8]]`, `[[144,14,14]]`; generalises Bravyi 2024.
- **Bhave, Choudhury, Nemec & Basu 2026 (arXiv:2602.07578).** "BiBiEQ: Bivariate Bicycle Codes on Erasure Qubits" — extends BB to erasure-qubit platforms.
- **Pandey 2026 (arXiv:2603.19062).** "Fair Decoder Baselines and Rigorous Finite-Size Scaling for Bivariate Bicycle Codes on the Quantum Erasure Channel" — directly relevant for our decoder-accuracy sensitivity analysis.
- **Zhu & Breuckmann 2023.** Automorphism-based transversal Clifford on BB codes; underpins the logical-gate accounting our resource estimator folds in.

## BP+OSD decoder and implementations

- **Panteleev & Kalachev 2019 (arXiv:1904.02703).** "Degenerate Quantum LDPC Codes With Good Finite Length Performance" — introduces BP+OSD for quantum codes.
- **Roffe, White, Burton & Campbell 2020 (arXiv:2005.07016).** "Decoding across the quantum low-density parity-check code landscape" — the `ldpc` package we use for CPU BP+OSD.
- **Hillmann et al. 2024 (arXiv:2406.14527).** Ambiguity-clustering decoder — OSD replacement with ≤10× lower wall-clock at comparable accuracy; candidate to narrow the gap measured in our paper.
- **NVIDIA CUDA-Q QEC 2024.** Published 29–42× GPU speedups for BP+OSD; our paper measures this on consumer-GPU RTX 3060 and identifies regime where the speedup appears (circuit-level, large H) vs where it does not (code-capacity, small H).
- **CUDA-Q QEC v0.6 (2026-04).** Hybrid Ising-CNN pre-decoder + PyMatching release — the intended surface-code GPU baseline which our attempt hit a parallel-edge merging limitation.

## MWPM decoder and implementations

- **Edmonds 1965.** Original matching algorithm underlying MWPM.
- **Fowler 2013 (arXiv:1310.0863).** Sparse-blossom MWPM for the surface code — the algorithmic baseline for fast MWPM.
- **Higgott 2022 (PyMatching v2 arXiv:2105.13082).** Production-grade MWPM; 100–1000× faster than v1; ~10⁶ errors/core-second. The CPU baseline in our paper.
- **Higgott & Gidney 2023 (Phys. Rev. X 13, 031007).** "Improved Decoding of Circuit Noise and Fragile Boundaries of Tailored Surface Codes" — XZZX + SI1000 integration; defines the SI1000 schedule we use.
- **Barnes et al. 2025 (Nat. Commun.).** Riverlane Local Clustering Decoder — first hardware adaptive decoder in production; relevant for reaction-time discussion.

## Tooling

- **Gidney 2021 (arXiv:2103.02202).** Stim — the fast stabilizer circuit simulator underpinning both our BB and surface branches.
- **qldpc-org/qldpc.** Python QEC code/simulator package; we use its `BBCode`, `SurfaceCode`, and `qldpc.circuits.SI1000NoiseModel` for consistent noise scheduling across branches.
- **qsharp/Azure Resource Estimator local runtime.** The Python `qsharp.estimator.LogicalCounts` interface we extend with a decoder-compute axis.

## Reaction-time and classical-compute awareness

- **Chamberland et al. 2022 (various).** Real-time decoding feasibility analysis; treats decoder latency as an algorithm-dependent multiplier.
- **Delfosse & Nickerson 2021.** Union-find decoder — real-time alternative to MWPM and faster than BP+OSD for surface codes.
- **Bhatnagar et al. 2025 (arXiv:2511.10633).** Recent reaction-time-on-surface-code analysis; adjacent to our work but does not fold in measured classical compute.

## GPU QEC and real-time decoding

- **Bausch et al. 2024 (AlphaQubit).** Neural network decoder at ≤1 μs/cycle on surface-code distances ≤5.
- **Senior et al. 2025 (arXiv:2512.07737, AlphaQubit 2).** sub-1 μs/cycle NN decoder on color + surface — the current real-time frontier.
- **Meinerz et al. 2022.** Transformer decoder for surface codes — ML-decoder lineage preceding AlphaQubit.

## Evolutionary and hybrid decoders

- **arXiv:2512.18273 (2025).** Evolutionary BP+OSD — differential evolution over BP weights; relevant as a future-work direction to reduce our measured BB cost.

---

Citation count: 22 (plus references-to-references). Composition: 5 resource-estimation + 5 BB/qLDPC + 5 BP+OSD + 4 MWPM + 3 reaction-time + others. Covers the desk-review expectations for a PRX Quantum resource-estimation submission.

---

## Paragraph-ready §6 text (ready to drop into paper_v3.md)

Resource-estimation frameworks have treated the classical decoder as an off-budget component since Beverland et al. 2022 (arXiv:2211.07629) established the Azure Resource Estimator and Litinski 2019 (arXiv:1808.02892) laid out the space-time accounting framework that followed. Gidney & Ekerå 2021 (arXiv:1905.09749) and its 2025 refinement (arXiv:2505.15917) report the canonical Shor-RSA-2048 estimate, with the latter flagging reaction-time as a first-class knob but still treating decoder wall-clock as a black box. Cohen et al. 2024 provides an analytic prediction that qLDPC overhead shrinks once decoder cost is counted; this paper is the empirical validation of that prediction.

Our primary target is Bravyi et al. 2024 (Nature), which introduces the `[[144,12,12]]` gross code and advertises a 12× physical-qubit reduction versus distance-matched surface codes. Related qLDPC work extending or modifying the gross code includes Symons, Rajput & Browne 2025 (arXiv:2511.13560, covering-graph BB families including `[[144,14,14]]`); Bhave et al. 2026 (arXiv:2602.07578, BB on erasure qubits); Pandey 2026 (arXiv:2603.19062, fair decoder baselines for BB on erasure); and Panteleev & Kalachev 2022 (arXiv:2111.03654, asymptotically good qLDPC constructions).

The BP+OSD decoder used for BB traces to Panteleev & Kalachev 2019 (arXiv:1904.02703) and the `ldpc` implementation of Roffe et al. 2020 (arXiv:2005.07016). NVIDIA's CUDA-Q QEC 2024 release reports 29–42× GPU speedups for BP+OSD on select operating points; our paper measures this on consumer RTX 3060 hardware and distinguishes the circuit-level regime (where GPU wins 146×) from the code-capacity regime (where GPU loses). Ambiguity-clustering (Hillmann et al. 2024, arXiv:2406.14527) and evolutionary BP+OSD (arXiv:2512.18273, 2025) are candidates to reduce the BP+OSD cost we measure and would shrink the 19.7× ratio if adopted.

The MWPM decoder baseline used for surface traces to Edmonds 1965; the algorithmically-modern variant is Fowler 2013's sparse blossom (arXiv:1310.0863), implemented by Higgott's PyMatching v2 (arXiv:2105.13082) which we use directly. Higgott & Gidney 2023 (Phys. Rev. X 13, 031007) defines the SI1000 circuit-noise schedule that both our branches implement via `qldpc.circuits.SI1000NoiseModel`.

Real-time and adaptive decoders that could alter the comparison landscape include the Riverlane Local Clustering Decoder (Barnes et al. 2025, Nat. Commun.) and the AlphaQubit lineage (Bausch et al. 2024; Senior et al. 2025, arXiv:2512.07737 AlphaQubit 2) for surface codes; reaction-time analyses by Bhatnagar et al. 2025 (arXiv:2511.10633) touch adjacent territory but do not fold in measured decoder cost for qLDPC codes. None of these prior works address the compute-aware BB-vs-surface comparison that our paper reports.
