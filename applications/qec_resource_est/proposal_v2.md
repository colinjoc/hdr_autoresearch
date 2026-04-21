# Proposal v2 — GPU-Decoder-Aware Resource Estimation for qLDPC vs Surface Code

Responds to scope check in `../qec_ideation/scope_checks/candidate_07_review.md` (verdict: REFRAME).

## 1. Problem

Existing resource estimators (Beverland et al. 2022 Azure; Gidney & Ekerå 2021/2025 RSA; Litinski 2019) treat the classical decoder as free or constant-latency. The [[144,12,12]] BB code (Bravyi 2024) claims ~12× qubit-overhead reduction vs surface codes, but the comparison omits BP+OSD's heavier classical compute. CUDA-Q QEC 2024 published 29–42× GPU speedups for BP+OSD, making a measured apples-to-apples accounting possible — but no published paper does it.

## 2. Claim (falsifiable)

**Headline (reframed — retitled, FPGA MWPM dropped):** We will deliver the **first GPU-decoder-aware resource estimate** for a single pre-registered algorithm (RSA-2048 factoring, per Gidney 2025 arXiv:2505.15917), at a single pre-registered noise point (p = 10⁻³ circuit noise, SI1000), reporting total (logical-qubit-seconds × measured GPU-decoder-Joules) for `[[144,12,12]]` BB + BP+OSD-on-GPU vs matched-overhead surface code + MWPM-on-GPU. Pre-registered decision threshold: **if the BB advantage shrinks by ≥2× once measured GPU-decoder cost is folded in, the qLDPC-overhead story has a hidden dominant cost**. If the shrinkage is <2×, the BB advantage is robust.

FPGA MWPM cost estimates are **dropped from the headline**. They appear only as an appendix sensitivity discussion, using a literature-cited analytic model, with no numerical claim.

## 3. Method sketch

- CUDA-Q QEC BP+OSD wall-clock + energy measurements at d = 12 BB on one A100 (measured, not cited).
- MWPM-GPU (Fowler sparse / PyMatching-CUDA) wall-clock + energy measurements at matched-overhead surface code.
- Extend Azure Resource Estimator with a "decoder compute" axis and a reaction-time-compounding multiplier.
- Apply to RSA-2048 via Gidney 2025's compiled circuit; report logical-qubit-seconds × decoder-Joules.
- Sensitivity: sweep reaction-time multiplier ∈ {1, 3, 10} and BP+OSD iteration count.

## 4. Kill-conditions (pre-registered)

1. **Sensitivity kill:** Phase 0 runs the sensitivity analysis on a two-decoder two-code toy (d = 6 BB vs d = 9 surface, p = 10⁻³). If the effect is <1.2× across the entire reasonable parameter range, the paper collapses to a footnote. Downgrade or abandon.
2. **Measurement kill:** if CUDA-Q QEC BP+OSD at d = 12 BB cannot be wall-clock-measured on one A100 within the Phase 0 window (memory or latency blockers), downgrade to smaller d and re-scope.
3. **Scoop kill:** if Riverlane, NVIDIA, or IBM publish a comparable paper during Phase 0, pivot to the reaction-time-sensitivity axis only (academic-differentiated) or abandon.

## 5. Reframe responses to scope-check objections

- **Objection 1 (fatal — decoder-hardware numbers are vapour):** addressed by (i) measuring BP+OSD-GPU and MWPM-GPU directly on the author's A100, not citing vendor blurbs, and (ii) dropping FPGA MWPM from the headline entirely. Retitle reflects this.
- **Objection 2 (scoop from industrial groups):** addressed by pre-registering the specific algorithm, metric, and threshold (industrial whitepapers tend to use synthetic / un-pre-registered metrics), open-sourcing the extended estimator, and exposing the reaction-time sensitivity industrial whitepapers typically omit.
- **Objection 3 (2–5× band is a prediction):** addressed by the Phase 0 sensitivity-on-a-toy gate (§4.1). If the effect is not robust on a toy, it is not robust on the full estimate — no sunk cost.

## 6. Load-bearing parameters (pre-registered)

| Parameter | Committed value | Sensitivity plan |
|---|---|---|
| Algorithm | RSA-2048 factoring per Gidney 2025 (arXiv:2505.15917) | Fixed |
| Noise point | p = 10⁻³ circuit noise, SI1000 | Fixed |
| Metric | logical-qubit-seconds × measured GPU-decoder-Joules | Fixed |
| Decision threshold | 2× shrinkage of BB advantage | Fixed |
| BP+OSD GPU runtime | MEASURED on author's A100 via CUDA-Q QEC | — |
| MWPM GPU runtime | MEASURED on author's A100 | — |
| Reaction-time multiplier | Full sweep {1, 3, 10} | Reported as sensitivity axis |
| BP+OSD iteration count | {10, 30, 100} | Ablation |

## 7. Target venue

**Primary: PRX Quantum.** Fit — resource-estimation papers. Anticipated objection "novelty beyond Cohen 2024 + Azure estimator" pre-empted by measured decoder numbers and the reaction-time sensitivity axis (neither is in prior art).

**Secondary: Quantum (Verein).** Fit — open-access, QEC-heavy, tolerant of tool papers.

## 8. Open-source commitment

Extended Azure-estimator plugin as a pip-installable Python package; all measurement scripts + A100 benchmark data released on publication.

## 9. Timing

Aim: arXiv within 4 months. Scoop risk is Medium-to-High; the pre-registered algorithm + metric + threshold is the durable academic differentiator from any vendor whitepaper that may appear in the interim.
