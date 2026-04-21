# Phase 3.5 Paper Review — qec_resource_est / paper_v2.md

## 1. One-paragraph assessment

The paper claims that when classical decoder compute is folded into FTQC resource estimation, the 12x physical-qubit advantage of the Bravyi 2024 [[144,12,12]] gross (BB) code over a matched-LER 12-patch d=17 surface encoding under SI1000 p=1e-3 inverts: surface with CPU PyMatching is 19.7x faster per shot and ~60x more energy-efficient per logical-qubit-round than BB with CUDA-Q QEC GPU BP+OSD on a single RTX 3060. The two-regime story (GPU BP+OSD loses 2.6-44x at code-capacity small-d, wins 146x at BB circuit-level) is tidy and the iteration-count ablation is a real methodological strength. However, the comparison remains algorithm-asymmetric (BP+OSD vs MWPM), a single GPU model without an A100 data point, and — most critically — the GPU-surface path is blocked by a CUDA-Q QEC wrapper bug that the authors acknowledge but do not work around. As written, the headline is a useful empirical data point on consumer hardware but is not a general "qLDPC advantage reverses" result. §6 is an unfilled placeholder, which is alone disqualifying for PRX Quantum. Verdict: MAJOR REVISIONS.

## 2. Strengths

- The iteration-count ablation (§4.4) pre-empts the obvious "you just over-iterated BP+OSD" rebuttal and shows <13% wall-time swing across iter ∈ {10,30,100}, pinpointing OSD (not BP) as the cost driver.
- The revision log (§5.5) and the frank admission that the v1 surface branch used `stim.Circuit.generated` with uniform per-channel p rather than SI1000 (§1.3 item 2) is unusually transparent for a resource-estimation paper and actively invites scrutiny.
- Pre-registration of a 2x kill threshold (§3.3) and an honest report that the methodology correction *increased* the ratio from 16x to 19.7x (§5.1) makes the result harder to dismiss as tuning.
- The two-regime framing (code-capacity vs circuit-level, §4.1 vs §4.2) with the explicit mechanism — parity-check column count O(1e2) vs O(1e4) amortising kernel-launch overhead (abstract, §4.2) — is a useful contribution beyond a single ratio number.
- The 60x vs 190x energy bracket (§4.5) with separated gross and active GPU energy is the right way to report a noisy energy measurement; v1's single 127x figure is correctly walked back.

## 3. Major concerns (fatal-to-acceptance unless addressed)

**M1. §6 Related Work is a placeholder.** The text literally reads "(Populated in Phase 3.5 with ≥20 citations)". A PRX Quantum desk editor will reject before external review. This must be populated with the BB/gross-code line (Bravyi 2024), the BP+OSD decoding literature (Panteleev-Kalachev, Roffe), PyMatching (Higgott), NVIDIA CUDA-Q QEC release notes, the Azure Resource Estimator paper, and the decoder-compute/reaction-time line (Delfosse, Battistel). Fix: write §6.

**M2. Algorithm-asymmetric comparison is the entire paper's load-bearing claim.** §5.4 admits "BP+OSD vs MWPM are different decoders" and that LER-matched-compute-budget is NOT addressed. The abstract and §7 still claim the qubit advantage "inverts." If a future paper shows BP+OSD at lower max_iter or a different OSD order yields the same LER as MWPM at 5-10x less compute, the 19.7x headline collapses. Fix: either (a) sweep p for both decoders and report iso-LER compute, or (b) retitle/rephrase to "for the BP+OSD(100,CS,7) vs MWPM algorithmic choice available in CUDA-Q QEC v0.6 and PyMatching v2 on RTX 3060," and weaken the §7 claim accordingly.

**M3. The GPU-surface path is blocked and the paper knows it.** §3.1 and §5.4 acknowledge CUDA-Q QEC's pymatching wrapper rejected the d=17 SI1000 DEM ("Parallel edges not permitted"). The headline therefore compares GPU-decoder-on-BB vs CPU-decoder-on-surface, which is not a same-hardware-class comparison. A reviewer will reasonably ask: what if surface d=17 also ran on GPU MWPM (e.g., Sparse-Blossom GPU ports, FPGA Union-Find, or a researcher fork of PyMatching with CUDA)? Fix: either demonstrate one GPU-MWPM path (even a published third-party one re-run locally) or soften the headline from "GPU-decoder-aware" (title!) to "GPU-BP+OSD-specific."

**M4. Single-GPU, consumer-tier measurement with no A100/H100 data.** Title and abstract make a general claim about "qLDPC qubit advantage." §5.2 is marked "(As in v1)" and §5.4 says "A100 numbers pending NVIDIA Academic Grant." A 19.7x margin minus an optimistic 3-8x A100 speedup is 2-6x, close to the 2x kill threshold. Fix: run at least one spot-check on a cloud A100 (runpod/lambda ~$1-2/hour) for the BB E02 cell to bound the margin from above; or restrict claim to "consumer RTX 3060-class hardware."

**M5. Figures are absent.** A resource-estimation paper with four tables and zero figures reads as underbaked. The code-capacity two-regime crossover (§4.1/4.2) and the BP+OSD iteration sensitivity (§4.4) are both obvious visualisation targets. Fix: see §8.

## 4. Minor concerns

- **Table §4.3 column "Physical qubits (matched 12 logicals)"** lists BB at 288 and surface at 6924. But BB d=12 is [[144,12,12]] per abstract — 144 data + ancilla. Please show the ancilla/total breakdown explicitly; 288 reads as "144 data × 2 for ancilla" but is not justified in the text.
- **§4.4 ablation shows iter=100 SLOWER (522,887 μs) than iter=30 (463,881 μs) by only 13%.** For a product-sum BP with fixed OSD order, this is plausible but worth a sentence on whether convergence reached a fixed point before iter=100 in all shots. The ratio is suspiciously flat between iter=10 and iter=30 (0.886 vs 0.887) — is the implementation actually running 10 and 30 iterations, or short-circuiting at a convergence criterion?
- **§3.1 surface branch.** "PyMatching v2, loading the DEM with `decompose_errors=True` via `stim` for matching-graph compatibility." Please state explicitly whether any detector-error-model simplification (disjoint edges, hyperedge decomposition policy) was applied, since this is the flipside of the CUDA-Q-QEC rejection reported in the next paragraph.
- **§4.5 CPU energy as "TDP/8 × wall-time."** The factor-of-8 is not justified in the text. Is this one-of-eight-cores? A socket-package ratio? State the arithmetic.
- **§4.6 is marked "unchanged from v1" but the Azure table is not reproduced.** A reader without v1 cannot verify. Inline the table or cut the section.
- **Abstract reports "distance-17" surface-code encoding; §4.3 table confirms 6,924 physical qubits for 12 patches at d=17** via 12 × (2·17² − 1) = 12 × 577 = 6924. That's a rotated-surface formula — §3.1 says "rotated-surface" only at E03 (v1 flagged). Is d=17 the rotated variant or unrotated? Please state.
- **§5.5 "Five of eight reviewer revisions addressed"** — helpful transparency, but the three unaddressed items should be listed in §5.4 as numbered open issues, not buried in the revision log.
- The abstract phrase "approximately 60x more energy-efficient" drops the 190x bracket; the conclusion says "60-190x". Reconcile — either cite the bracket in the abstract or the point estimate in §7.

## 5. Abstract ↔ text consistency

Mostly consistent after the v2 revision. Minor mismatches:
- Abstract says "approximately 60x more energy-efficient"; §4.5 and §7 report a 60-190x bracket. The abstract gives the conservative bound only; a reader seeing "~190x (gross)" in the table will feel the abstract buried the lead the wrong way. Either pick a bound and commit, or say "60-190x" in the abstract.
- Abstract: "12-patch distance-17 surface-code encoding decoded by CPU PyMatching MWPM is 19.7x faster per shot." §4.3 reports the 19.67x ratio but shows surface wall-time 187.8 μs for the whole 12-patch-per-shot loop, i.e., ~15-16 μs per patch per round. Cross-check with §5.1's "single-patch wall-time at d=17 is not much higher than at d=12 … about 15-16 μs vs 23 μs" — consistent.
- Abstract's "two-regime picture: ... 2.6-44x slower ... 146x wins" is referenced but the supporting table is relegated to "(As in v1 §4.1 — E00 + E01)" in §4.1. A self-contained v2 needs the table inline.

## 6. Methodology ↔ claim consistency

The §3 method is now well-matched to the §4 results (after v2 fixes: matched SI1000 noise on both branches, measured 12-patch surface, per-LQR divide-by-144). §5.1's "why the ratio is robust" rebuttal to the reviewer's predicted collapse is sound and well-supported by §4.3/§4.4. §5.4 lists the remaining caveats honestly. §7 is mostly caveat-consistent except for the title itself: "GPU-Decoder-Aware Resource Estimation Reverses the qLDPC Qubit Advantage on Consumer Hardware." The word "Reverses" is stronger than what §5.4's list of four unresolved caveats supports. A safer title: "...Narrows/Erodes..." or "...Changes the Sign of the Qubit Advantage on RTX 3060 for BP+OSD vs MWPM." A reviewer will return to the title during the editorial meeting.

## 7. Related-work adequacy

§6 is empty. The minimum must-cite set for PRX Quantum desk survival:

- **qLDPC / BB / gross codes.** Bravyi, Cross, Gambetta, Maslov, Rall, Yoder, Nature 2024 ("High-threshold and low-overhead fault-tolerant quantum memory"). Panteleev & Kalachev on asymptotically-good qLDPC. Tillich-Zémor / hypergraph-product line.
- **BP+OSD decoding.** Panteleev-Kalachev 2019 BP+OSD original. Roffe, White, Burton, Campbell 2020 ("Decoding across the quantum LDPC code landscape"). The `ldpc` package (Roffe).
- **MWPM / PyMatching.** Higgott 2022 ("PyMatching v2") and the Sparse Blossom paper (Higgott & Gidney 2023).
- **Surface code baseline.** Fowler, Martinis, Cleland 2012 surface-code primer. Google 2023/2024 surface-code experiments (Acharya et al.) for realistic circuit-level baselines.
- **Circuit-level noise / SI1000.** Gidney, McEwen, Bacon on SI1000 noise model (Stim + superconducting).
- **Resource estimation.** Beverland et al. 2022 Azure Quantum Resource Estimator paper. Litinski magic-state factory papers. Gidney & Ekerå 2021 ("How to factor 2048-bit RSA integers in 8 hours").
- **Decoder compute / reaction time.** Delfosse 2020 "Hierarchical decoding." Battistel et al. real-time decoder review. Skoric et al. parallel window decoding. Meinerz/Jouppi/Bravyi on neural decoders for cost.
- **GPU decoders.** NVIDIA CUDA-Q QEC documentation (cite release/version). Liyanage et al. / Riverlane FPGA decoders for context.
- **BB-vs-surface comparisons.** Any follow-up/commentary papers on Bravyi 2024 (Xu, Breuckmann, etc.) since mid-2024.

A plausible healthy §6 for PRX Quantum has 30-50 citations organised under (i) qLDPC codes, (ii) decoders, (iii) resource estimation, (iv) hardware decoder implementations. The stated "≥20" floor is the bare minimum.

## 8. Figures and tables

Zero figures is a red flag. Recommended figures:

1. **Two-regime crossover plot.** X-axis = parity-check matrix column count (or code distance); Y-axis = wall-time per shot; two series (CPU BP+OSD, GPU BP+OSD); mark the crossover point. This IS the paper's central mechanism and deserves the lead figure.
2. **Matched-LER bar chart.** Four bars: BB-GPU, BB-CPU, surface-CPU, surface-GPU-pending. Log-scale y-axis, μs per logical-qubit-round. Lifts the §4.3 table to a visual.
3. **Iteration-count ablation.** Line plot of CPU μs/shot vs max_iter ∈ {10,30,100}, with a horizontal line at the GPU baseline, to make §4.4 visually self-evident.
4. **Energy bracket.** A single panel showing the 60x-190x bracket visually with the gross/active decomposition — currently very easy to miss in the table.
5. **Azure Estimator qubit/runtime scatter.** Physical qubits vs runtime for Shor-2048 across the six presets, with the BB/surface measured operating points overlaid — makes the §4.6 connection concrete.

## 9. Reproducibility

§3.1 gives the BB code constructor string, SI1000 noise call, decoder kwargs (`max_iter`, `bp_method`, `ms_scaling_factor`, `osd_method='osd_cs'`, `osd_order=7`), matrix shapes (936 × 10512 for BB, 1872 × 13149 for surface), and hardware (RTX 3060 12 GB, CUDA 12.9, Ubuntu 24.04, Python 3.12.3). §3.2 lists the experiment scripts by filename (`e00_benchmark.py`, ..., `e05_revisions.py`) and cites `results.tsv`. This is a strong reproducibility footprint — better than most resource-estimation papers.

Missing for full reproducibility:
- Package pins for `qldpc`, `ldpc`, `stim`, `pymatching`, CUDA-Q QEC (the text says "v0.6" — good; add exact commit hashes).
- Random-seed policy (300 shots per cell — were seeds fixed? different per cell?).
- NVML sampling details: interval "every 50 shots" — what is the sampling latency vs shot duration? A 50-shot coarse-grain at 3.7 ms/shot = 185 ms sampling window is fine, but state it.
- The DOI/Zenodo/Git commit hash for the archival code and `results.tsv` must be listed before submission. PRX Quantum requires a data-availability statement.
- §1.3 references `knowledge_base.md line 41` — that is an internal file, not a citation, and must be replaced with the published BB-vs-surface LER curve source (Bravyi 2024 Figure X or a follow-up).

## 10. Verdict

**MAJOR REVISIONS.** The measurement and methodology are credible after the v2 fixes, the pre-registration discipline is above average, and the two-regime mechanism is a genuine contribution. But the empty §6, the algorithm-asymmetric comparison that underwrites the title's word "Reverses," the absence of figures, and the single-GPU consumer-only footprint each require work that is larger than copy-editing. None is individually fatal if addressed; together they put this at the rejection line for PRX Quantum as submitted.

## 11. Three specific actions before submission

1. **Write §6 with 30+ citations covering qLDPC codes, BP+OSD/MWPM decoders, resource estimators, and hardware decoder implementations**, and replace the `knowledge_base.md line 41` internal reference in §1.3 with the published BB-vs-surface LER source. (Completable in 3-5 days. Non-negotiable for PRX Quantum desk review.)

2. **Run one GPU-on-surface spot-check to close the same-hardware-class gap.** Either (a) work around the CUDA-Q QEC "parallel edges" error by re-decomposing the DEM with a non-'disallow' merge strategy, (b) re-run surface d=17 through a published GPU MWPM port, or (c) explicitly retitle to "GPU BP+OSD vs CPU MWPM" and soften §7 accordingly. (1 week for any of the three.)

3. **Add the four core figures (two-regime crossover, matched-LER bar, iteration ablation, energy bracket).** The underlying numbers are already in `results.tsv` per §3.2; this is plot-generation, not new experiments. (2-3 days.)
