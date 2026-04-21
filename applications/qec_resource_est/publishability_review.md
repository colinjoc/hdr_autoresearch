# Phase 0.25 Publishability Review: GPU-Decoder-Aware Resource Estimation for qLDPC vs Surface Code

Reviewer: PRX Quantum (grouchy). Inputs: `proposal_v2.md`, `scope_checks/candidate_07_review.md`, `literature_review.md`, `knowledge_base.md`, Phase 0.25 section of `program.md`. No prior conversation.

## 1. Novelty taxonomy

**Category: Synthesis** (unchanged from the prior scope check; v2 does not claim otherwise and that is correct).

Specific prior work this extends / synthesises:

- Beverland et al. 2022, arXiv:2211.07629 — Azure Resource Estimator. Treats decoder as free / constant-latency. v2 adds a "decoder compute" axis.
- Gidney 2025, arXiv:2505.15917 (RSA-2048) + Gidney & Ekerå 2021 — supplies the pre-registered compiled algorithm.
- Gidney, Shutty & Jones 2024 arXiv:2409.17595 — cultivation; enters only via Gidney 2025 compiled circuit.
- Bravyi et al. 2024 (Nature gross code) + Xu et al. 2024 arXiv:2308.08648 + Cohen, Kim, Bartlett & Brown 2024 — the qLDPC-overhead claim being stress-tested.
- NVIDIA CUDA-Q QEC 2024 (29–42× BP+OSD GPU speedups) + Roffe `ldpc`/`bposd` + PyMatching v2 (Higgott & Gidney 2023) — measurement tooling.
- Litinski 2019 (PBC) — compilation framework assumed by Gidney 2025.

Does v2 genuinely differentiate or is the reframe cosmetic? Partly real. The three differentiators are: (i) direct A100 measurement rather than cited vendor speedups, (ii) single pre-registered algorithm + metric + threshold, (iii) reaction-time sensitivity axis. None of (i)–(iii) individually is novel, but together they cover a hole the lit review itself flags as unfilled (literature_review.md lines 371–372, 389, 405, 410–411). The question "does the BB code still win once you pay for BP+OSD?" is, as the scope check noted, obvious to anyone who read Bravyi 2024 alongside CUDA-Q QEC. Novelty is genuine but incremental. The synthesis label is honest.

## 2. Falsifiability

The kill-outcome is now sharp: "BB advantage shrinks by ≥2× once GPU-decoder cost is folded in → qLDPC-overhead story has a hidden dominant cost; if <2× → robust." Single algorithm (RSA-2048 per Gidney 2025), single noise point (p = 10⁻³, SI1000), single metric (logical-qubit-seconds × measured GPU-decoder-Joules), single threshold (2×). This is a clean improvement over the v1 2–5× band and does satisfy the scope check's pre-registration ask.

Residual wobble: the metric is a *product* of two quantities with very different units (logical-qubit-seconds, Joules). Reviewers will ask whether the 2× threshold has physical meaning across both axes or is just a convenient line. A defensible answer would be to also report the two factors separately at the decision moment, not only the product, so the kill-test cannot be gamed by an offsetting swap between the two. v2 does not state this explicitly. Minor, fixable.

Reaction-time sweep ∈ {1, 3, 10} is a *sensitivity axis*, not a kill knob — good, because otherwise the paper would have a second threshold and the single-threshold discipline would collapse. v2 is disciplined here.

Overall: the headline is genuinely falsifiable and single-threshold. Not unfalsifiable-in-disguise.

## 3. Load-bearing parameters

| Parameter | Committed value | Lit range | Headline scaling | Stable? |
|---|---|---|---|---|
| Algorithm | RSA-2048, Gidney 2025 | fixed | n/a (fixed) | Yes |
| Noise model / point | p = 10⁻³ circuit, SI1000 | 10⁻⁴–10⁻² discussed across platforms | Moderate — BB distance needed, surface matched | Moderate; single point is pre-registered so acceptable |
| BP+OSD GPU wall-clock at d=12 BB | MEASURED on A100 | ~100 μs – ms from CUDA-Q QEC numbers | Near-linear in headline | Resolved by measurement — **IF A100 access is real** |
| MWPM-GPU wall-clock on matched surface distance | MEASURED on A100 | PyMatching v2 ~10⁶ err/core-s on CPU; GPU variant less standardised | Near-linear | Contingent on measurement; PyMatching-CUDA / Fowler sparse is the hinge — **which one?** v2 says "Fowler sparse / PyMatching-CUDA" as an either/or. That is a genuine open choice and affects the MWPM baseline by >2× |
| Decoder Joules per shot | derived from measured power × wall-clock | essentially unpublished | Linear in energy axis of headline | Resolved by measurement if A100 wattmeter access is real; NVML power draw is standard, should be fine |
| Reaction-time multiplier | sweep {1, 3, 10} | Gidney 2025 flags 1–10 range | Can dominate headline | Treated as sensitivity, not a load-bearing single number — acceptable |
| BP+OSD iteration count | ablation {10, 30, 100} | 10–100 typical | Linear in decoder time | Acceptable |
| BB logical error rate at p=10⁻³, d=12 | ~10⁻⁹ (Bravyi 2024) | well-cited | Determines matched surface d ≈ 15–19 | Stable |

Flags:
- **MWPM-GPU choice** (Fowler sparse vs PyMatching-CUDA) — v2 is under-committed. Pre-register ONE before the Phase 0 toy sweep.
- **A100 access and thermal throttling** — "the author's A100" appears twice. If the author does not in fact have dedicated A100 access (not a shared Colab instance, not a rental that throttles), the whole headline falls through. v2 does not contain a one-line "A100 is available at <provider> with <job-hours budget>" commitment. This is the single biggest load-bearing operational parameter, and it is under-specified.
- **SI1000 single noise point**: defensible *because* pre-registered, but reviewers will ask for at least one off-point check. v2 has no plan. Minor.

## 4. Venue fit

- **PRX Quantum (primary).** Fit: publishes resource estimation and QEC architecture papers in the Beverland / Litinski / Cohen tradition. Typical objection: "novelty beyond Cohen 2024 + Azure Resource Estimator + CUDA-Q QEC is thin" and "decoder-hardware modelling is speculative." v2 pre-empts the second via direct A100 measurement and dropping FPGA MWPM from the headline; it pre-empts the first only partially — the reaction-time sensitivity axis and the pre-registered algorithm/metric/threshold are the differentiators, but a referee can reasonably argue this is an engineering study not a PRX-Quantum-level contribution. Moderate fit.
- **Quantum (Verein, secondary).** Fit: open-access, QEC-heavy, methodology-tolerant. Typical objection: "how much of this is already in CUDA-Q QEC docs or IBM's own accounting?" v2 pre-empts by open-sourcing extended Azure estimator plugin + benchmark data. Good fit.
- **(not claimed but worth mentioning)** npj Quantum Information would be a valid third option if PRX Quantum bounces. v2 does not list it; fine.

## 5. Top three killer objections

1. **(Major — borderline fatal) "Decoder-hardware numbers are still contingent on your one A100 and your choice of MWPM-GPU implementation; the 2× threshold therefore rests on benchmark-engineering choices reviewers cannot audit."** v2 mitigates by committing to measurement + open-sourcing data + sensitivity sweeps. Unaddressed residue: the MWPM-GPU implementation is under-committed ("Fowler sparse / PyMatching-CUDA"), and A100 availability is asserted not evidenced. Mitigation: pre-register the specific MWPM-GPU codepath (commit hash) before Phase 0; include a single-line operational attestation that A100 access is real and owned (not a rental subject to throttling). Solvable by the proposal author in one paragraph. Not fatal if addressed.

2. **(Major) "Scoop from Riverlane / NVIDIA / IBM."** Scope check flagged Medium-to-High. Lit review lists Riverlane, NVIDIA, IBM, Microsoft, Photonic Inc. as active in resource estimation (lines 360–368). The lit review, as read, does not cite a 2025–2026 preprint that already couples measured GPU decoder compute to a specific compiled algorithm for BB vs matched surface; the closest adjacent works are CUDA-Q QEC 2024 (speedups, no resource estimate), Cohen 2024 (analytic trade-off), Bravyi 2024 (code only). So the niche is still open as of the lit-review cutoff — but a vendor whitepaper could close this in weeks, and the author's 4-month arXiv timing is aggressive-adequate rather than safe. v2 mitigates via pre-registration + reaction-time sensitivity + open-source tooling, which is a genuine academic differentiator from a vendor whitepaper (vendors typically report headline numbers on their own hardware without pre-registered thresholds). Mitigation is adequate; residual risk is timing. Addressable only by shipping.

3. **(Major) "The 2× threshold is a prediction, not a result, until Phase 0's toy sweep clears."** v2's kill-condition §4.1 is explicit: d=6 BB vs d=9 surface, p=10⁻³, KILL if effect <1.2× across parameter range. This is the right gate. Unaddressed residue: "across the entire reasonable parameter range" is vague. Which parameters? BP+OSD iter count, reaction-time multiplier, noise — all three? And what counts as "the effect"? Presumably BB/(surface) product ratio, but v2 does not pin it. Mitigation: §4.1 should commit to the specific ratio metric and the parameter ranges (e.g. iter ∈ {10, 30, 100}, reaction ∈ {1, 3, 10}, p fixed at 10⁻³) and state that ANY combination where ratio ≥1.2× is sufficient to proceed. Tight, cheap to add. Solvable.

No objection is fatal *given* the fixes above are added.

Additional reviewer-grade concern not in the top three but worth pre-empting in Phase 2: (a) NVML power read is coarse and includes host overhead — reviewers will ask for a proper isolated-GPU power methodology (e.g. `nvidia-smi` sampling rate, idle subtraction, thermal steady-state). (b) "Matched-overhead surface code" must be defined: matched to BB at the same logical-error-rate target (10⁻⁹), not at the same physical qubit count. v2 implies the former but does not state it.

## VERDICT: PROCEED

Tight PROCEED. No unaddressed fatal; at least one plausible venue fit (PRX Quantum, with Quantum as viable fallback); novelty is genuine-but-incremental synthesis and the proposal is honest about that; the headline is cleanly falsifiable with a single algorithm, single noise point, single metric, single threshold, and a real Phase 0 toy-gate. The scope-check's three objections are substantively addressed, not cosmetically: FPGA MWPM is genuinely dropped from the headline (appendix-only, with *no* numerical claim — so it does not sneak back in), the BP+OSD-GPU and MWPM-GPU numbers are to be measured directly, and the 2× threshold has a hard <1.2× KILL gate at Phase 0.

Append to `research_queue.md` with flag `pre-empt-reviewer`:

1. Lock MWPM-GPU implementation choice (Fowler sparse vs PyMatching-CUDA) by commit hash before Phase 0 toy run; measure both if feasible. Operationally attest A100 access in `data_sources.md` equivalent.
2. Ship fast (≤4 months to arXiv). Monitor arXiv + Riverlane/NVIDIA/IBM press for a scooping decoder-compute-aware estimator; pivot to reaction-time-sensitivity-only paper if scooped mid-flight per §4.3.
3. Tighten Phase 0 toy gate: pre-register the exact ratio metric (BB/surface on logical-qubit-s × J product), the exact parameter grid (iter ∈ {10, 30, 100}, reaction ∈ {1, 3, 10}, p = 10⁻³), and the rule that ≥1.2× in any cell is sufficient to proceed. Also report the two metric factors separately at decision time so the 2× test cannot be gamed by offsetting swaps.

(Words: ~1,340.)
