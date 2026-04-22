# Phase -0.5 Scope-Check - Candidate 35

**Candidate.** ViT vs language-transformer σ - same-architecture-class, different-modality criticality comparison. Targets: ViT-B/16 (ImageNet), DINOv2 ViT-B, CLIP-vision-B/16 vs GPT-2 small, Pythia-160M. Matched parameter count where possible.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME.** The cross-modal σ-comparison is a genuinely open question in 2026 and the observable is tractable on a single 3060, but three disqualifying issues as written: (i) "same architecture class" compresses seven microscopic differences into one label, so split σ cannot be attributed to modality without holding the other six fixed; (ii) the input-distribution confound is the dominant physical difference between vision and language, and pixel-patch vs BPE-token cannot be matched, only controlled; (iii) Candidate 11's Phase -0.5 verdict already absorbed the ViT arm into Candidate 1, so C35 stands alone only after arguing why it is more than a scale-up of that cell. Reframe the headline to "training-objective effect on σ within the ViT family" (supervised vs DINO-SSL vs CLIP-contrastive), make vision-vs-language a secondary figure reading off Paper 1's GPT-2 number, add the within-modality input-distribution ablation the candidate's required-controls list elides.

## 2. Prior work 2024-2026

**Direct hits: zero.** No 2024-2026 paper reports avalanche exponents (α, β, γ, shape collapse) or MR-estimated σ on a ViT, DINOv2, or CLIP-vision checkpoint. No paper compares any activation-criticality observable between vision and language transformers. The gap is real.

**Adjacent, must be engaged:**

- **Gauthaman, Ménard, Bonner 2024** [arXiv:2409.06843, PLOS Comp Bio]: fMRI covariance-spectrum is a power law over ~4 decades, consistent across cortical regions and subjects. This is *covariance-spectrum* scale-freeness, not avalanche criticality, but it is the closest vision-side prior. ViT activations should be tested against this exponent as a secondary observable - potentially a stronger publishable comparison than branching ratio alone.
- **[arXiv:2410.06672] "Towards Universality: Mechanistic Similarity Across LM Architectures"** - Transformer vs Mamba feature-similarity via SAEs. Same logical shape as C35; defines the genre. Flagged as closest adjacent in the C20 review.
- **Huh et al. 2024 Platonic Representation Hypothesis**; 2026 Aristotelian critique [arXiv:2602.14486]. As models scale, representations converge across modalities. Matched σ across ViT-B and GPT-2 small supports Platonic; split is evidence against. The 2026 critique argues convergence is partly width/depth confound after calibration - directly relevant to matched-parameter control. **Missing from the candidate.**

**Vision-side SAE availability** (brief's (e)): ViT SAEs exist in 2026-04. `saev` (OSU-NLP), PatchSAE for CLIP-vision, [arXiv:2504.08729] (CLIP-ViT steering SAEs), [arXiv:2502.06755] (interpretable/testable vision SAE features), CVPR 2025 MIV workshop toolkit. No Gemma-Scope-class publicly-shipped multi-width suite yet, but at least one pretrained SAE per vision backbone. **Basis-invariance is testable on the vision side**; the asymmetry worry was real in 2023, not 2026-04. Caveat: one-SAE-per-checkpoint, not matched across the three vision targets - cross-target basis-invariance needs matched-SAE training (~1 GPU-week with `saev`).

## 3. "Same architecture class" - is it true?

Axes on which ViT-B/16 and GPT-2 small differ at a microscopic-dynamics level:

1. **Token-mixing direction.** Bidirectional (ViT) vs causal-masked (GPT-2). Causal masking is an asymmetric token-axis structure.
2. **Positional encoding.** Learned 1D vs learned/sinusoidal 2D patch-position.
3. **CLS token and readout.** ViT reads from prepended CLS; GPT-2 from last-token residual. Different aggregation dynamic.
4. **Activation function.** Mostly matched (GELU; CLIP-ViT uses QuickGELU).
5. **Normalisation.** Pre-LN both. Matched.
6. **Objective.** Cross-entropy over 50k vocab vs classification (ViT) vs contrastive (CLIP) vs self-distillation/EMA (DINOv2). Four different loss shapes on the vision side alone.
7. **Input pre-embedding.** Patch-linear projection of RGB pixels vs token-embedding lookup. Pixels live on a continuous low-dim manifold; tokens on a discrete high-dim vocabulary.

Seven axes; "same architecture class" compresses to one. Per Ghavasieh 2026 (papers.csv 2046), activation function alone tunes the universality class; the other six axes have no such bound. **Split σ cannot be attributed to modality without holding six other axes fixed, and those cannot be fixed with public checkpoints.**

**Matched axis that transfers.** Candidate 1's layer-axis residual-stream avalanche at percentile θ is well-defined on both: 768-dim residual, 12 blocks, same LN position. **Layer-axis transfers; token-axis does not** - causal masking gives GPT-2 a temporal direction, ViT has none. C20's layer-vs-token dichotomy is inherited.

**Action.** Replace "same architecture class" with "matched residual-stream layer-axis observable across two input modalities and four training objectives; architectural differences enumerated and ablated where possible".

## 4. Input-distribution confound - does σ standardise over it?

**No.** Every criticality observable is a functional of the activation distribution, which is a functional of input × weights.

- **Input-independent at init.** σ is computable from weights + activation alone (Schoenholz 2017). Trained-net σ inherits input-freeness only if activations stay Gaussian-like. LLMs demonstrably don't: outlier features and superposition produce input-dependent heavy tails.
- **Candidate 26** ("prompt-type modulates σ") explicitly posits input-dependence. If C26 is right, C35 is confounded: σ_ViT on ImageNet and σ_GPT2 on WebText are two input distributions, not two architectures.

**Pre-registered outcomes as written:** σ_ViT ≈ σ_GPT2 is consistent with either architecture-determined criticality *or* self-organisation regardless of input - different claims. σ_ViT ≠ σ_GPT2 is consistent with input-dependence, *or* any of six architectural axes (§3), *or* any of four training-objective axes. Neither maps 1-1 to a causal claim; the "Δσ > 0.15 = input-dependent" kill is **underspecified**.

**Fix.** Add a **within-modality input-distribution ablation** as prerequisite: σ_ViT on ImageNet vs iNaturalist vs random crops; σ_GPT2 on WebText vs Pile-code vs random tokens. If within-modality σ already varies by >0.15, cross-modal Δσ is uninformative. Only after this fixes the within-modality variance scale can cross-modal Δσ be interpreted.

## 5. Overlap with Candidate 11 / Candidate 1 - standalone?

C11's scope-check recommends **ViT-Tiny on CIFAR-10 / ImageNet-100** as the strictly-better cross-architecture control for C1, absorbed as a cross-architecture-universality section of Paper 1. If that REFRAME is adopted, Paper 1 already contains a ViT arm.

- **C35 is not novel against reframed C11.** ViT-B/16 becomes a scale-up (Tiny → Base) of that section. Novelty beyond C11: (i) DINOv2 SSL, (ii) CLIP contrastive, (iii) cross-*modal* universality as headline rather than cross-*architecture*.
- **The headline C35 could own.** "Does training objective (supervised vs DINO-SSL vs CLIP-contrastive) shift σ within a fixed ViT architecture?" C1 doesn't touch this; C11 doesn't touch this; it is the vision analogue of C21 (base vs RLHF). This axis is natively falsifiable (three public ViT-B/16 checkpoints, identical architecture, different objective only) and avoids both §3 and §4 confounds.

**Action.** Reframe C35 around training objective; cross-modal becomes a secondary figure reading Paper 1's GPT-2 number for context.

## 6. Minimum-evidence-bar audit

Against knowledge_base.md §5:

| # | Item | Handled as written? |
|---|---|---|
| 1 | P(s) via powerlaw + KS + LLR | Not committed |
| 2 | α ≈ 3/2 with 95% CI | Not committed (σ only) |
| 3 | β, γ, scaling relation | Not committed |
| 4 | Shape collapse | **Missing** |
| 5 | σ via MR estimator on ≥ 2 axes | Partial (σ only) |
| 6 | Threshold plateau | **Missing** |
| 7 | At-init control | **Missing** (matched-pretraining only) |
| 8 | Neutral-null rejection | **Missing** |

One partial, seven absent or uncommitted. Worse than Candidate 11's 3/8. A promotion-grade rewrite must commit to the full battery (layer-axis α, β, γ, σ, shape collapse, threshold plateau, at-init matched-architecture control, parallel Candidate-12 null rejection).

## 7. Feasibility and compute

Inference-only, HuggingFace weights, batch 1. Five targets × ~1 GPU-day = ~5 GPU-days; CSN + crackling + shape-collapse + MR + at-init = ~1 GPU-week; within-modality ablation (+2 days); matched-SAE training for basis-invariance (+1 GPU-week). **Realistic 3-4 weeks**, not the stated 2.

## 8. Rubric

As originally written: D=4 (public weights, no data issue), N=3 (real gap but confounded per §3-§4), F=2 (kill threshold does not map to causal claim), C=3 (2 weeks understated), P=2.

As reframed per §5 ("training-objective effect on σ within vision-transformer family, cross-modal secondary"): D=5, N=4, F=4, C=3-4, P=4.

## 9. Action items before Phase 0 promotion

(i) Retarget headline to "training objective vs σ within the ViT family" (§5); cross-modal secondary.
(ii) Add within-modality input-distribution ablation as prerequisite control (§4).
(iii) Enumerate the seven architectural axes; commit to residual-stream layer-axis; acknowledge token-axis does not transfer (§3).
(iv) Engage Gauthaman 2024, Huh 2024 Platonic, arXiv:2410.06672 as prior universality benchmarks (§2).
(v) Coordinate with reframed C11 - absorb into Paper 1 or bundle into Paper 7 alongside C18/C20/C22.
(vi) Commit to the 8-item knowledge_base.md §5 bar - currently one partial, seven missing (§6).
(vii) Tighten kill to "Δσ > 3 × within-modality σ-variance, direction assigned by within-modality ablation" (§4).

---

**External sources consulted** beyond `papers.csv` / `literature_review.md` / `knowledge_base.md`:

- Gauthaman, Ménard, Bonner 2024, *PLOS Comp Bio* - [arXiv:2409.06843](https://arxiv.org/abs/2409.06843). Covariance-spectrum scale-freeness in human visual cortex.
- Huh et al. 2024 "Platonic Representation Hypothesis"; 2026 Aristotelian critique [arXiv:2602.14486](https://arxiv.org/abs/2602.14486).
- "Towards Universality: Mechanistic Similarity Across LM Architectures" [arXiv:2410.06672](https://arxiv.org/abs/2410.06672).
- `saev` (OSU-NLP Group); PatchSAE; [arXiv:2504.08729](https://arxiv.org/abs/2504.08729) (CLIP-ViT steering SAEs); [arXiv:2502.06755](https://arxiv.org/abs/2502.06755) (interpretable/testable vision SAE features).
- `candidate_11_review.md`, `candidate_20_review.md`, `candidate_22_review.md` - prior scope-checks with overlapping cross-architecture / cross-modal scope.
