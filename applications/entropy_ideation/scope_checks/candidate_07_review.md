# Phase −0.5 Scope-Check — Candidate 7

**Title.** Criticality observables across model scale (Pythia suite).
**Proposed observables.** σ, α, crackling-noise exponents for Pythia-70M → Pythia-12B at final checkpoint, matched input distribution.
**Reviewer.** Phase −0.5 sub-agent, 2026-04-21.

**Verdict. REFRAME — PROCEED** on a `70M → 2.8B` scale ladder × Pythia's intermediate-checkpoint axis; drop 6.9B and 12B as full-precision targets on a 12 GB RTX 3060; reposition as a *training-step × model-size* criticality atlas, not a seven-point single-checkpoint scaling fit.

One-line justification: the as-proposed seven-point fit is both noise-limited (one estimate per scale, per-estimate σ_α ≈ 0.05) and infeasible at the top end on 12 GB, but trading 6.9B/12B for Pythia's 154 intermediate checkpoints on the smaller five scales produces a two-axis atlas with ≈ 20× more data points, no hardware risk, and no competing published work.

---

## 1. Feasibility on a 12 GB RTX 3060

EleutherAI's Hugging Face "AUTOMATED Model Memory Requirements" tool reports Pythia-12B at ≈ 21.6 GB fp16 weights (close to the reviewer's 24 GB estimate). Using `2·N` fp16 / `1·N` int8 / `0.5·N` int4 bytes per parameter:

| Scale | fp16 | int8 | int4 | Activations @ ctx 2048 | 12 GB verdict |
|---|---:|---:|---:|---:|---|
| 70M | 0.14 GB | 0.07 | 0.04 | <0.1 | trivial |
| 160M | 0.32 | 0.16 | 0.08 | <0.2 | trivial |
| 410M | 0.82 | 0.41 | 0.21 | ~0.3 | trivial |
| 1B | 2.0 | 1.0 | 0.5 | ~0.5 | comfortable |
| 1.4B | 2.8 | 1.4 | 0.7 | ~0.7 | comfortable |
| 2.8B | 5.6 | 2.8 | 1.4 | ~1.5 | **fp16 comfortable** |
| 6.9B | 13.8 | 6.9 | 3.5 | ~2–4 | int8 possible, tight |
| 12B | 24 (official 21.6) | 12 | 6 | ~3–6 | **int8 does not fit headroom**; int4 see below |

The reviewer's concern is correct: Pythia-12B int8 occupies essentially the whole card, and the criticality pipeline requires caching ≥10⁵ tokens × per-layer residual-stream activations, which runs into multi-GB peaks even at batch 1. int4 quantisation (bitsandbytes nf4 / GPTQ / AWQ) is not part of the Pythia release; running criticality analysis on int4-quantised weights and calling the result "Pythia-12B" is scientifically indefensible because any exponent drift could be due to quantisation, not scale. CPU-offload via `device_map="auto"` is order-of-magnitude too slow (≈ 1 tok/s → ~30 h per pass × threshold × basis × bootstrap grid) — blows the four-week cap.

**Practical upper bound: Pythia-2.8B at fp16.** Pythia-6.9B at int8 is includable as a single-point extrapolation with an explicit int8-confound caveat; Pythia-12B is out.

## 2. Is "seven scales, one checkpoint each" statistically strong?

Per-scale CSN-fit shot noise on α from 10⁵-token caches is typically ± 0.05 (1σ) [Clauset 2009]. To detect a trend `α(N) = α_0 · N^ζ` with |ζ| ~ 0.02 on seven log-spaced points with σ_α = 0.05 requires |Δα| ≥ 0.15 across the full range at 2σ. There is no theoretical prediction that Δα is that large — the null expectation is α ≈ 3/2 (mean-field / DP universality class) at every scale. The proposed "power-law-vs-asymptote discrimination" therefore fails unless the true effect is unusually large.

## 3. Intermediate checkpoints materially improve the design

Pythia ships 154 checkpoints per scale: `step0`, ten log-spaced `step{1,2,4,…,512}`, and 143 evenly-spaced from `step1000` to `step143000`. Using a subset of ~20 log-spaced checkpoints per scale delivers three benefits:

1. **Power.** One point per scale becomes ~20; a (N, t) surface fit averages scale-agnostic noise.
2. **Bundled novelty.** Exercises Candidate 3's "training pushes toward / away from edge-of-chaos init" question *at scale*, bundling two of the three "highest-impact-if-positive" candidates per `candidate_ideas.md §Candidate priorities`.
3. **Natural at-init control.** `step0` is the mandatory at-init control from `knowledge_base.md §5` item 7, available for free.

Cost: 20 ckpts × 5 scales = 100 shards, ~200 GB SSD (fine). Forward-pass on ~10⁵ tokens on RTX 3060 fp16 is minutes-to-tens-of-minutes for 70M–2.8B. Primary sweep ≈ 25 GPU-hours; plus threshold × basis × bootstrap overhead ≈ 3 weeks wall-clock — matches the reviewer's original budget for a far weaker single-checkpoint design.

## 4. Prior-art check — 2024 – 2026

- Arola-Fernández, "Intuition emerges in Maximum Caliber models at criticality" (arXiv 2508.06477, 2025). Toy maze-walker Maximum-Caliber models, not pretrained LLMs — conceptual adjacency only.
- "Allometric scaling of brain activity explained by avalanche criticality" (arXiv 2512.10834, 2025). Brain data; provides a directly testable prediction — critical-avalanche systems exhibit *sublinear* activity-size scaling — that could be imported into the LLM setting.
- "A universal route from avalanches in mean-field models … to stochastic Poisson branching events" (arXiv 2502.08526, 2025). Theory; null-model machinery.
- "Pretraining scaling laws for …" (arXiv 2509.24012, ICLR 2026). Pythia scaling laws, *not* criticality observables.
- EleutherAI + FaithfulSAE (arXiv 2506.17673, 2025) — SAE faithfulness on Pythia-1.4B vs 2.8B. No σ, α, or scaling-relation measurements.
- `lit_ml.md §9` gap statement remains open as of this review.

**No paper 2024 – 2026 computes σ, α, or the Sethna scaling relation on the Pythia suite across scale.** Novelty bar is clean.

## 5. Minimum-evidence-bar audit (`knowledge_base.md §5`)

Candidate 7 as-written covers items 1, 2 (per-scale), 5 (partial). **Missing and must be added:** (3) independent β, γ + scaling relation; (4) shape collapse; (6) threshold plateau θ ∈ {0, 0.1, 0.5, p95}; (7) at-init control — mandatory and only available once intermediate checkpoints are in scope; (8) neutral-null rejection — requires bundling Candidate 12's Martinello-2017 Griffiths-phase null.

## 6. Required controls

- Step-0 at-init control per scale (free with the intermediate-checkpoint axis).
- Raw-neuron + SAE basis (EleutherAI pretrained-SAEs exist for mid scales; fall back to training small SAEs otherwise).
- Block-bootstrap over token-context blocks for autocorrelation.
- Threshold plateau sweep.
- MR branching-ratio estimator on layer (primary) and batch (cross-check) axes.
- Neutral-null rejection (from Candidate 12).
- Deduplicated vs non-deduplicated Pythia variants as a data-side robustness check.

## 7. Rewritten pre-registered kill

Kill if *all three*: (a) σ(N, t_final) flat within ± 0.02 across the five primary scales; (b) α(N, t_final) drifts less than σ_α ≈ 0.05 across scales; (c) the (N, t) trajectory surface shows no training step at which σ crosses 1 at any scale. If all three obtain, the scaling-law-for-criticality claim dies; the (N, t) trajectory atlas itself is still a publishable negative result because trajectories-are-flat across scale is a non-trivial finding.

## 8. Venue fit

Primary: NeurIPS 2026 main track or ICLR 2027 (bridges scaling-laws and interpretability). Secondary: ICML MechInterp workshop. Tertiary: Entropy (MDPI) for the statistical-physics angle. Author-demographic match: EleutherAI (Biderman, Cunningham) engages with criticality-adjacent work on Pythia; Anthropic / DeepMind SAE community (Templeton, Lieberum) if SAE basis is included; Priesemann / Plenz neuroscience-criticality community if MR estimator and Sethna relation are applied correctly.

## 9. Dependence structure

Reframed Candidate 7 *absorbs* Candidate 3 (training-drift-of-EOC) into its (N, t) grid and *requires* Candidate 12 (neutral-null rejection) as mandatory methodology. This matches `candidate_ideas.md §Candidate priorities`' suggested `3 + 4 + 7` bundle, making 3+7 explicit. Candidate 4 (grokking) stays orthogonal (modular-arithmetic, not Pythia-pretrained).

## 10. Citation bug

The candidate cites "[3017: Biderman 2023]" for Pythia, but `papers.csv` ID 3017 is Frankle & Carbin (lottery-ticket). The Biderman Pythia paper is arXiv 2304.01373, ICML 2023. `papers.csv` must be updated with a fresh ID before the submission paper cites it. Two-minute fix, flagged so it does not propagate into the promoted project.

## 11. Summary

| Item | As-proposed | Reframed |
|---|---|---|
| Scales | 70M–12B (seven) | 70M–2.8B (five) + 6.9B int8 single-point |
| Checkpoints | Final only | ≥ 20 log-spaced per scale |
| Grid | 7 cells | 100 primary cells + controls |
| Hardware | Infeasible at top | Comfortable on 12 GB fp16 |
| Observables | σ, α, "crackling-noise" (vague) | σ (MR, two axes), α, β, γ, scaling-relation residual, shape collapse |
| Wall-clock | Claimed 3 weeks; realistically 6–8 | 3 weeks realistic |
| Statistical power | Under-powered | Well-powered surface fit |
| Novelty | Clean | Same, strictly stronger evidence |
| §5 controls | Partial (items 3, 4, 6, 7, 8 missing) | All eight addressable |

**Verdict. REFRAME — PROCEED.** Promote to `applications/entropy_pythia_atlas/` with the five-scale × twenty-checkpoint grid; drop Pythia-12B, de-prioritise Pythia-6.9B to a single int8 extrapolation point with explicit quantisation caveat; bundle Candidate 3's training-drift question; require Candidate 12's neutral-null methodology; fix the `papers.csv` 3017 citation.
