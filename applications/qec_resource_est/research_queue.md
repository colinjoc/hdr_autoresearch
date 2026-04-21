# Research Queue — qec_resource_est

Status: **post-Phase-0 lit review**. This file now contains:
(a) the three verbatim `pre-empt-reviewer` items from Phase 0.25;
(b) Phase 0 smoke-test amendment items (R-PER-1a, R-PER-1b) from `data_sources.md`;
(c) ≥100 hypotheses populated from the seven-theme deep literature review.

Hypothesis IDs: `PER-N` = pre-empt-reviewer (Phase 0.25); `R-PER-Na` = Phase 0 amendment; `H-N` = Phase 0 hypothesis.

---

## Pre-empt-reviewer items (from Phase 0.25 publishability review) — PRESERVED VERBATIM

These are the top three killer objections raised by the Phase 0.25 reviewer at PRX Quantum. Every one must be addressed in the Phase 2 experiment plan, pro-actively.

### PER-1 [pre-empt-reviewer] MWPM-GPU codepath commit + A100 access evidence
- **Objection:** proposal_v2 names "Fowler sparse / PyMatching-CUDA" as the MWPM-GPU codepath with no commit. Whichever one is chosen colours the energy-per-shot number; the either/or is unacceptable for a pre-registered single-noise single-metric paper. Separately, A100 access is asserted but not evidenced in the proposal.
- **Required action (before Phase 0 toy run):** Lock the MWPM-GPU implementation choice (Fowler sparse vs PyMatching-CUDA) to a specific commit hash; measure both if feasible. Operationally attest A100 access in `data_sources.md` with the equivalent of a box label / cloud allocation ID.
- **Design variable:** MWPM-GPU implementation selection.
- **Metric:** wall-time + energy per shot at matched (p, d) between committed MWPM-GPU and BP+OSD-GPU.
- **Baseline:** PyMatching v2 CPU at matched parameters.
- **Prior:** 60% the two candidates disagree on energy-per-shot within 2×; 40% within 5×. Either way, committing is non-negotiable.

### PER-2 [pre-empt-reviewer] Sensitivity-grid specification before sweep
- **Objection:** The Phase 0 toy KILL gate is "<1.2× across the entire reasonable parameter range" but the parameter grid is not specified. Reviewers at PRX Quantum will demand a pre-registered grid with a specific ratio metric — otherwise "across the entire reasonable range" is a slider the authors can move post-hoc.
- **Required action (Phase 0):** Pre-register the parameter grid — BP+OSD iteration count × reaction-time multiplier × noise point. Specify the ratio metric (e.g. `total_cost_BB / total_cost_surface`). Also report the two factors (logical-qubit-seconds, decoder-Joules) *separately* at the decision moment so the 2× test cannot be gamed by offsetting swaps.
- **Design variable:** parameter-grid spec.
- **Metric:** min and max ratio across pre-registered grid cells.
- **Baseline:** Cohen 2024 analytic trade-off as the sanity-check envelope.
- **Prior:** 55% the ratio varies by <1.5× across the grid (robust result); 30% by 1.5–3× (still publishable, narrower claim); 15% by >3× (KILL triggers).

### PER-3 [pre-empt-reviewer] Scoop durability — 4-month timing
- **Objection:** Riverlane has commercial incentive (their hardware wins the accounting); NVIDIA's CUDA-Q QEC team has the infrastructure. 4-month timing to arXiv is aggressive-adequate but not comfortable.
- **Required action:** Ship fast (≤4 months to arXiv). Monitor arXiv + Riverlane / NVIDIA / IBM press monthly for a scooping decoder-compute-aware estimator. Pivot to reaction-time-sensitivity-only paper if scooped mid-flight (proposal_v2 §4.3 kill path).
- **Design variable:** paper-scope fallback plan.
- **Metric:** time-to-arXiv.
- **Baseline:** Bravyi 2024 gross-code Nature paper + CUDA-Q QEC 2024 release cadence.
- **Prior:** 60% arXiv lands before any competitor whitepaper; 40% scoop forces the fallback scope.

---

## Phase 0 smoke-test amendments (from data_sources.md)

### R-PER-1a MWPM-GPU codepath reframe
- **Finding:** pure MWPM-GPU does not exist publicly (neither Fowler sparse MWPM nor a CUDA branch of PyMatching). NVIDIA's "real-time MWPM" path is a hybrid Ising-CNN-predecoder on GPU + PyMatching on CPU.
- **Action:** lock PER-1 commitment to **NVIDIA CUDA-Q QEC v0.6 hybrid Ising-predecoder + PyMatching** pipeline pinned at a commit hash at Phase 1 kickoff. Ablation baselines: CPU PyMatching v2 alone, CPU `ldpc` v2 BP+OSD alone.
- **Disclosure:** paper methods must state the hybrid nature explicitly (not "pure MWPM-GPU").
- **Prior:** this is a non-negotiable factual correction to proposal_v2.

### R-PER-1b GPU class commitment
- **Finding:** author host is RTX 3060 (12 GB, compute-capability 8.6), not A100.
- **Action:** Phase 0 toy runs on 3060. Apply to NVIDIA Academic Grant Program by 2026-04-27. If not awarded by 2026-06, budget $300 rental on Lambda / RunPod for Phase 2 A100 headline run. Phase 0.25 reviewer's concern on "A100 access evidence" is satisfied by explicit rental-budget commitment.
- **Disclosure:** report RTX 3060 + A100 numbers side by side; consumer-GPU floor is independently useful.

---

## Phase 0 hypotheses — seven-theme lit-review follow-ups

### Theme 1: FTQC resource estimation frameworks (H-001 to H-014)

**H-001.** The Azure Resource Estimator's `logical_cycle_time` slot can be extended to incorporate a `decoder_latency_model(code, d, iter, batch, hardware)` lookup without modifying the core estimator — validated by Alice & Bob's cat extension precedent. *Metric:* plugin passes Azure conformance tests. *Prior:* 85%.

**H-002.** Gidney 2025's RSA compiled circuit (Zenodo DOI 10.5281/zenodo.15347487, `code.zip`) contains the Stim circuit fragments needed to drive our decoder-latency measurement pipeline directly (no re-compilation needed). *Prior:* 60% — needs Phase 1 day-1 download + inventory.

**H-003.** Litinski 2019 PBC compilation applied to BB codes (with lattice-surgery analogues substituted) yields a well-defined floor plan with T-factory count computable from Gidney 2025's T-count. *Prior:* 70%.

**H-004.** Cohen et al. 2024 analytic BB-vs-surface overhead is within 2× of our *measured* overhead including decoder cost, when interpreted at matched LER. *Prior:* 50%.

**H-005.** Beverland 2022's error-budget default (1/3:1/3:1/3) is robust to decoder-compute axis addition — i.e. moving budget across T-distillation vs rotation synthesis does not invalidate decoder-aware estimates. *Prior:* 80%.

**H-006.** Xu et al. 2024's end-to-end BB architecture can be ported to the Azure estimator input format with <1 week of engineering. *Prior:* 40% (untested).

**H-007.** The headline product metric (J × logical-qubit-s) decomposes cleanly into a geometric factor (qubit-s) × a compute factor (J) × an efficiency factor (ratio), with literature-cited analytic formulas for the first two and our measured data for the third. *Prior:* 75%.

**H-008.** At the Phase 2 headline point (d = 12 BB / d = 17 surface), the ratio of J-per-decode is dominated by the BP+OSD iteration count, not the GPU choice (3060 vs A100). *Prior:* 55%.

**H-009.** Applying Gottesman 2014 constant-overhead bounds to our BB+BP+OSD measurements yields an effective *non-constant* overhead term scaling as d⁴ in energy. *Prior:* 65%.

**H-010.** The cultivation magic-state protocol of Gidney-Shutty-Jones 2024 is more reaction-time-sensitive than 15-to-1 block distillation (higher %-conditional operations). *Prior:* 60%.

**H-011.** Extending the Azure estimator with a decoder-cost axis changes the *optimal* code-distance choice at fixed LER target by at most 1 unit of distance. *Prior:* 55%.

**H-012.** At large enough code distance (d ≥ 20), decoder compute becomes the dominant Azure-estimator cost term on both BB and surface branches. *Prior:* 65%.

**H-013.** The plug-in extended Azure estimator can be open-sourced as a pip-installable Python package (≤1 week engineering). *Prior:* 90%.

**H-014.** Reporting the joule-logical-qubit-second product alongside the two factors separately preempts the "gameable single-metric" reviewer concern (PER-2). *Prior:* 90%.

### Theme 2: BP+OSD decoder (H-015 to H-034)

**H-015.** BP+OSD on RTX 3060 achieves 10–15× speedup over CPU `ldpc` v2 at d = 12 BB, iter = 100. *Prior:* 65%. *Metric:* μs per shot. *Baseline:* CPU measurement on same host.

**H-016.** BP+OSD on A100 achieves 29–35× speedup over CPU at d = 12 BB, iter = 100 (matches NVIDIA CUDA-Q QEC v0.4 published numbers). *Prior:* 70%.

**H-017.** CUDA-Q QEC v0.6 RelayBP on A100 achieves >19× speedup over v0.5 at d = 12 BB (matches NVIDIA blog headline). *Prior:* 70%.

**H-018.** BP+OSD iteration count ∈ {10, 30, 100} translates to roughly linear wall-clock ratio (10:1, 30:3, 100:10). *Prior:* 80%.

**H-019.** OSD invocation rate at p = 10⁻³ with iter = 100 is <10% on d = 12 BB. *Prior:* 70%. *Source:* Roffe 2020 benchmarks.

**H-020.** OSD invocation rate at iter = 10 is >40% at p = 10⁻³, making iter = 10 a poor operating point for LER-sensitive workloads. *Prior:* 70%.

**H-021.** BP+OSD wall-clock scales as O(d⁴) at fixed iteration count. *Prior:* 55%.

**H-022.** GPU memory footprint at d = 12 BB with batch 1000 is <2 GB, fits RTX 3060 12 GB with headroom. *Prior:* 85%.

**H-023.** GPU memory footprint at d = 24 BB (extrapolated) with batch 1000 is <8 GB, still fits RTX 3060 with narrow headroom. *Prior:* 65%.

**H-024.** RelayBP accuracy (LER) is within 1.2× of BP+OSD on d = 12 BB at matched iteration count. *Prior:* 70%.

**H-025.** Ambiguity clustering (2406.14527) as OSD alternative gives within 5% accuracy match to OSD-0 on BB at 10× lower wall-clock. *Prior:* 45%.

**H-026.** BP+LSD parallel variant (ldpc_v2) on 16-core CPU achieves 5–10× over single-core BP+OSD. *Prior:* 70%.

**H-027.** GPU BP+OSD is wall-clock-linear in batch size for batch ∈ {1, 100, 1000}. *Prior:* 70%.

**H-028.** GPU BP+OSD energy-per-shot (μJ) is roughly *constant* across batch sizes (power scales with batch but throughput scales linearly). *Prior:* 75%.

**H-029.** NVML `power.draw` 1 Hz sampling with 10-s windows gives ±5% accuracy on BP+OSD mean power. *Prior:* 85%.

**H-030.** Thermal throttling does not occur on RTX 3060 in BP+OSD runs of <10 min duration at 20°C ambient. *Prior:* 75%.

**H-031.** BP+OSD with noise-aware weights (2502.21044) improves accuracy 1.3–1.5× at same iter count, at 1.1–1.3× wall-clock. *Prior:* 50%.

**H-032.** Evolutionary BP weight-optimisation (2512.18273) gives ≤5% BP+OSD accuracy improvement on BB. *Prior:* 40%.

**H-033.** Co-designed BB + BP (2401.06874, short-4-cycle elimination) achieves 2× faster BP convergence at matched LER. *Prior:* 55%.

**H-034.** Our CPU-GPU BP+OSD measurement pipeline detects thermal throttling if present (ramp-up protocol + temperature monitoring). *Prior:* 85%.

### Theme 3: MWPM decoder (H-035 to H-051)

**H-035.** PyMatching v2 CPU on d = 17 surface code achieves ~1 μs per single-shot decode on modern i9 / equivalent. *Prior:* 80%.

**H-036.** NVIDIA CUDA-Q QEC v0.6 hybrid Ising-predecoder + PyMatching achieves 2–5× speedup over CPU PyMatching alone on d = 17 surface. *Prior:* 65%.

**H-037.** The Ising CNN predecoder reduces syndrome density by 60–80% before PyMatching invocation. *Prior:* 55%.

**H-038.** Hybrid pipeline energy is dominated by GPU predecoder at d = 17 surface (CPU PyMatching is energy-cheap). *Prior:* 60%.

**H-039.** Correlated matching (Fowler 2013) as CUDA-Q QEC variant, if available, improves LER by 15% at matched wall-clock. *Prior:* 50%.

**H-040.** Fusion-blossom CPU parallel variant scales super-linearly up to 16 cores. *Prior:* 55%.

**H-041.** Union-find decoder on surface code has 10% higher LER than MWPM at matched distance but 3× faster throughput on CPU. *Prior:* 70%.

**H-042.** Riverlane LCD FPGA energy (estimated from public lit) is 3–5× lower than our hybrid GPU+CPU pipeline per decode. *Prior:* 50%. *Note:* appendix-only, no headline claim.

**H-043.** AlphaQubit 2 (2512.07737) on surface code is within 1.5× of MWPM LER at sub-1-μs latency. *Prior:* 60%.

**H-044.** Neural-decoder energy per decode is 2–5× higher than MWPM on matched code distances. *Prior:* 50%.

**H-045.** Skoric 2022 streaming MWPM window decoder runs at 1 μs/cycle at d = 13 on modern CPU. *Prior:* 65%.

**H-046.** Predictive window decoding (2412.05115) reduces stall rate by 2× in reaction-time-limited operation. *Prior:* 55%.

**H-047.** Elastic QEC decoders (2406.17995) save 20% of wall-clock on our compiled RSA circuit. *Prior:* 45%.

**H-048.** PyMatching v2 scales O(d² log d) in wall-clock at fixed noise rate. *Prior:* 70%.

**H-049.** PyMatching v2 energy-per-decode scales as O(d² log d) as well (wall-clock × TDP). *Prior:* 70%.

**H-050.** On d = 17 surface, hybrid-pipeline energy is competitive with BP+OSD GPU energy on d = 12 BB (within 2×). *Prior:* 50%. *Critical for headline.*

**H-051.** Running CPU PyMatching + CPU BP+OSD CPU-only baseline (no GPU) produces a useful "CPU-only" variant of the headline comparison at ~10× slower but ≈ matched energy. *Prior:* 65%.

### Theme 4: Reaction time (H-052 to H-063)

**H-052.** At μ_react = 1, BB + BP+OSD total wall-clock is dominated by decoder (>50%) at d = 12, iter = 100. *Prior:* 70%.

**H-053.** At μ_react = 10, BB's total wall-clock is ~10× that of surface, erasing BB's qubit-count advantage on joule-logical-qubit-s metric. *Prior:* 65%.

**H-054.** At μ_react = 1, surface code's wall-clock is dominated by T_cyc,base not decoder. *Prior:* 75%.

**H-055.** Reaction-time sensitivity slope on headline metric is ~0.5 decades per μ_react decade (BB is more sensitive than surface). *Prior:* 55%.

**H-056.** Aligned-window scheduling (Bhatnagar 2025) reduces reaction-time penalty by 50% on surface; comparable reduction achievable on BB. *Prior:* 50%.

**H-057.** Cultivation pipeline depth 10 → 30 halves reaction-time penalty on RSA. *Prior:* 50%.

**H-058.** Predictive window decoding on BB with BP+OSD has not been demonstrated; our project *should not* claim it (out of scope). *Prior:* 95% (procedural).

**H-059.** At utility-scale (10⁶ logical qubits), reaction-time compounding scales non-linearly due to classical-I/O bandwidth saturation at Tb/s. *Prior:* 40%. *Note:* out of scope for RSA-2048 scale (10³ qubits) but relevant for appendix forward-looking discussion.

**H-060.** Elastic scheduling of BP+OSD iterations (stop early on easy cases) can recover 15–25% of reaction-time penalty. *Prior:* 50%.

**H-061.** Measuring reaction time on real hardware is not feasible in this project; we use a simulation-based model per Bhatnagar 2025. *Prior:* 95% (procedural).

**H-062.** Gidney 2025's reaction-time coefficient ~1 μs is a best case for modern SC platforms; actual deployed systems likely 3–5 μs. *Prior:* 65%.

**H-063.** Our reaction-time-only fallback paper (per proposal_v2 §4.3) is viable as a Quantum-journal submission if scooped on headline. *Prior:* 70%.

### Theme 5: qLDPC vs surface overhead (H-064 to H-083)

**H-064.** At matched LER 10⁻⁹, BB [[144,12,12]] qubit overhead is 13.5× lower than surface d = 17 (raw). *Prior:* 85%.

**H-065.** With connectivity-cost multiplier 1.3×, BB advantage becomes 10.4× (raw qubit). *Prior:* 80%.

**H-066.** Adding measured decoder-compute cost on headline metric compresses BB advantage to 5–8× (stylised prediction from knowledge_base.md). *Prior:* 55%.

**H-067.** If the BB advantage compression is ≥2× (from 13.5× to <6.75×), proposal_v2 kill threshold fires. *Prior:* 40%.

**H-068.** At d = 14 BB (vs d = 19 surface), the compression factor is *larger* (decoder cost scales faster on BB). *Prior:* 50%.

**H-069.** At d = 10 BB (vs d = 15 surface), the compression factor is *smaller* (less relative decoder burden). *Prior:* 55%.

**H-070.** In-situ qLDPC magic-state injection (2604.05126) further reduces BB footprint by ~20–40% if integrated. *Prior:* 45%. *Scope:* Phase 4+ extension only.

**H-071.** Alternative BB codes (Symons 2025 [[64,14,8]] or [[144,14,14]]) have different compression behaviour; not swept in headline. *Prior:* 60%.

**H-072.** Hypergraph product codes at matched parameters have decoder cost similar to BB. *Prior:* 55%.

**H-073.** Quantum Tanner codes at matched parameters have single-shot decoding advantage offsetting decoder cost. *Prior:* 45%.

**H-074.** Automorphism-based logical gates (Zhu et al. 2023) add <10% overhead to BB memory. *Prior:* 55%.

**H-075.** BB threshold is degraded by 10–20% under geometry-induced correlated noise (2604.01040). *Prior:* 55%.

**H-076.** Hyperbolic Floquet codes (Fahimniya 2023) have qubit overhead competitive with BB but higher decoder cost. *Prior:* 45%. *Scope:* out of headline.

**H-077.** BB code on neutral-atom platform (Xu 2024) has identical decoder cost to SC platform (decoder is the same). *Prior:* 85%.

**H-078.** Riverlane commercial whitepaper does not contain a pre-registered Gidney-2025 BB-vs-surface cost coupling. *Prior:* 75%. *Action:* verify Phase 1 day 1 by direct whitepaper retrieval.

**H-079.** Our headline result is robust to substituting [[144,14,14]] for [[144,12,12]] (qualitative conclusion unchanged). *Prior:* 70%.

**H-080.** The cultivation factory footprint is code-independent — same footprint on BB and surface branches. *Prior:* 60%.

**H-081.** Lattice-surgery-analog joint measurements on BB cost ~1.5× more than lattice surgery on surface in logical-qubit-seconds. *Prior:* 50%.

**H-082.** Matched-LER distance choice does not interact with reaction-time multiplier (axes are independent in Azure estimator). *Prior:* 75%.

**H-083.** Photonic-platform BB (SHYPS / Photonic Inc.) has favourable connectivity cost (native long-range) making BB still 10× advantageous. *Prior:* 45%. *Scope:* out of headline.

### Theme 6: Energy and power (H-084 to H-092)

**H-084.** NVML `power.draw` measurements on RTX 3060 during BP+OSD achieve ±5% reproducibility at 10⁴-shot window. *Prior:* 85%.

**H-085.** Wall-plug GPU energy is 20–40% higher than GPU-rail-only (PSU + CPU + RAM overhead). *Prior:* 80%.

**H-086.** Idle-subtracted GPU energy per decode at d = 12 BB, iter = 100 is 25–50 μJ on RTX 3060. *Prior:* 65%.

**H-087.** Idle-subtracted GPU energy per decode on A100 (if measured) is 20–30 μJ — *lower* than 3060 despite higher TDP, due to better perf/W. *Prior:* 60%.

**H-088.** CPU PyMatching v2 energy per decode at d = 17 surface is ~12 μJ on i9-class CPU. *Prior:* 65%.

**H-089.** FPGA LCD energy per decode (literature-cited) is ~10 μJ at d = 17 surface. *Prior:* 50%. *Scope:* appendix.

**H-090.** Cryogenic-CMOS decoder energy at d = 7 surface (Overwater scaled) is ~1 μJ per decode. *Prior:* 50%. *Scope:* appendix.

**H-091.** Headline joule-logical-qubit-s metric is dominated by decoder-J term (not logical-qubit-s term) at d ≥ 14 BB. *Prior:* 55%.

**H-092.** Total decoder-energy bill for RSA-2048 factoring run (Gidney 2025 scale) is ~1–10 kWh — negligible vs dilution-fridge (~MWh/run). *Prior:* 80%.

### Theme 7: Target algorithm RSA-2048 (H-093 to H-102)

**H-093.** Gidney 2025 Zenodo `code.zip` contains directly-usable Stim circuit fragments + T-count tallies. *Prior:* 60%. *Action:* download + inventory Phase 1 day 1.

**H-094.** Our extended Azure estimator reproduces Gidney 2025's 750k-qubit / ~5-day headline within 10% at their assumed decoder-cost = 0. *Prior:* 75%. *Sanity check.*

**H-095.** At measured decoder cost, BB + BP+OSD yields <500k physical qubits for RSA-2048 — *better than Gidney 2025's surface-code number* on the qubit axis. *Prior:* 65%.

**H-096.** At measured decoder cost, BB + BP+OSD yields similar or slightly longer wall-clock than surface (decoder latency offsets factory pipelining gains). *Prior:* 55%.

**H-097.** RSA-2048 T-count in Gidney 2025 is ~10⁹; cultivation makes T-gates cheap so T-count sensitivity to decoder cost is minor. *Prior:* 80%.

**H-098.** Windowed-arithmetic window size Gidney-default (4) is close to optimum for our decoder-cost-aware estimator (variation ≤ 5% headline). *Prior:* 70%.

**H-099.** Applying our decoder-cost extension to a second algorithm (quantum chemistry nitrogenase) gives qualitatively similar BB-vs-surface conclusion. *Prior:* 60%. *Scope:* Phase 4+ future work.

**H-100.** Cryptographic-policy implication of our measured BB-favourable result: tightens Q-Day timeline by ≤1 year beyond Gidney 2025. *Prior:* 40%. *Scope:* discussion section only.

**H-101.** The cultivation pipeline depth on BB is the same as on surface (no code-specific dependency). *Prior:* 60%.

**H-102.** Our measured-decoder result reproduces within 20% when a second GPU class (A100 vs 3060) is substituted, confirming the conclusion is GPU-class-robust. *Prior:* 50%. *Critical robustness check for reviewer Obj 1.*

### Additional cross-cutting hypotheses (H-103 to H-110)

**H-103.** The Azure-estimator plugin open-source release is accepted by the Microsoft `qsharp` repo as a recommended third-party extension (listed in docs). *Prior:* 35%. *Scope:* post-publication.

**H-104.** Our pre-registered 2× kill threshold matches industry heuristics for "material" cost shifts. *Prior:* 70%.

**H-105.** arXiv-first publication (before any commercial whitepaper from Riverlane/NVIDIA/IBM) is achievable within 4 months. *Prior:* 55%.

**H-106.** The joule-logical-qubit-second metric is adopted by follow-on papers within 12 months. *Prior:* 30%. *Speculative.*

**H-107.** The Phase 0 toy gate (d = 6 BB vs d = 9 surface, p = 10⁻³) clears with effect ≥1.2× in at least one cell of {iter × μ_react} grid. *Prior:* 70%. *Kill gate.*

**H-108.** Independent replication by another lab within 6 months confirms our measured decoder costs within 30%. *Prior:* 50%. *Long-term.*

**H-109.** The paper is cited by the next RSA-factoring resource-estimate paper (natural follow-up to Gidney 2025). *Prior:* 60%.

**H-110.** The reaction-time-sensitivity fallback (proposal_v2 §4.3) is a publishable paper in Quantum even without the measured-GPU-decoder headline. *Prior:* 65%. *Fallback viability.*

---

## Hypothesis inventory summary

- Preserved verbatim pre-empt-reviewer: **3** (PER-1, PER-2, PER-3).
- Phase 0 smoke-test amendments: **2** (R-PER-1a, R-PER-1b).
- Theme-1 (frameworks): 14 (H-001 — H-014).
- Theme-2 (BP+OSD): 20 (H-015 — H-034).
- Theme-3 (MWPM): 17 (H-035 — H-051).
- Theme-4 (reaction time): 12 (H-052 — H-063).
- Theme-5 (qLDPC vs surface): 20 (H-064 — H-083).
- Theme-6 (energy): 9 (H-084 — H-092).
- Theme-7 (RSA target): 10 (H-093 — H-102).
- Cross-cutting: 8 (H-103 — H-110).

**Total: 3 + 2 + 110 = 115 entries.** Exceeds the ≥100 bar with 15 margin.

Prior distribution (on the 110 Phase 0 H-entries): mean prior ~61%, spans 30% (speculative) to 95% (procedural). Distribution skew reflects scientific uncertainty: most measurement predictions sit 50–70%, most procedural / tooling predictions sit 75–90%, and a handful of stretch predictions sit 30–45%.

---

## Phase 1 day-1 triage

From the above, the Phase 1 kickoff tasks (in priority order):

1. **R-PER-1b** — submit NVIDIA Academic Grant application (writeable by author in <4 hours).
2. **H-093** — download Gidney 2025 Zenodo `code.zip`; inventory contents; verify Stim circuits present.
3. **R-PER-1a** — pin CUDA-Q QEC v0.6 commit hash; install on local host; run smoke example.
4. **H-015, H-016** — CPU-baseline BP+OSD benchmark on d = 12 BB with `ldpc` v2.
5. **H-094** — reproduce Gidney 2025 Azure-estimator numbers with decoder-cost=0.
6. **H-107** — run Phase 0 toy gate (d = 6 BB vs d = 9 surface) on RTX 3060.

If H-107 fails the 1.2× kill gate in *every* cell: invoke proposal_v2 §4.1 kill path and stop. Else: proceed to Phase 2.
