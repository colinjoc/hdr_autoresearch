# Phase -0.5 Scope-Check — Candidate 11

**Candidate.** CNN criticality on Fashion-MNIST as a cross-architecture control. Extend ActivationAnalyzer -> avalanche pipeline to the existing `fashion_mnist_classifier.py`; compute sigma, alpha, crackling-noise exponents at multiple training stages.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Novelty vs papers.csv and 2025-2026 arXiv

The candidate's own novelty claim — "CNN criticality has been partially studied [3003: Xiao 2018 at-init] but not with post-training avalanche exponents" — is conservative and roughly correct but glosses over the strongest prior-art question.

**3003 Xiao et al. 2018** gives the full at-initialisation edge-of-chaos story for vanilla CNNs (sigma_w, sigma_b tuned to chi_1 = 1, Delta-Orthogonal init, 10 000-layer CNN trainability). It does *not* measure activation avalanches, does *not* compute alpha / beta / gamma with crackling-noise discipline, and does *not* track any observable through training. The gap the candidate names is real, but narrow: CNN-criticality-at-init is essentially a closed problem, so the standalone novelty reduces to "trained-CNN avalanches", an incremental observable-class extension.

**3033 Testolin et al. 2020** treats DBN weight-graphs as complex networks — weight-graph, not activation-avalanche, and not CNN. **3045 Torres et al. 2023** is RNN (VERIFY flag). Neither pre-empts.

**arXiv 2025-2026.** No hit on trained-CNN activation avalanches with CSN + crackling-noise on Fashion-MNIST / CIFAR. Adjacent CNN criticality work lives at-init (dynamical-isometry extensions) or on weight-graph topology. Kanders, Lorimer & Stoop (Chaos 2017) explicitly show that avalanche criticality and edge-of-chaos criticality do not necessarily co-occur — so "Xiao 2018 already did it at-init" is not a valid dismissal. They are distinct fingerprints.

**Novelty verdict.** Genuine gap, but smaller than for the transformer target (Candidate 1).

## 2. Sample support on Fashion-MNIST

The brief's central empirical concern. Existing `fashion_mnist_classifier.py` has per-image per-layer counts:

- Conv1 (26x26x32): 21632
- MaxPool1 (13x13x32): 5408
- Conv2 (11x11x64): 7744
- MaxPool2 (5x5x64): 1600
- Conv3 (3x3x64): 576
- Dense: 64
- Network total per image: ~37000.

Test set 10000 images. Two distinct observables:

**(a) Per-image total active-node counts** (what the existing callback computes). 10000 samples, range 0 to ~37000, but at trained-CNN sparsity (~30-50%) this sits as a sharply-peaked bulk near 10000-20000 — *not* heavy-tailed. This is an across-image activity histogram, not an avalanche distribution. The callback's log-log axes are cosmetic.

**(b) Spatially-contiguous supra-threshold avalanches** (what the candidate intends). Max support per image capped by largest single-layer neuron count. Post-pooling spatial maps are 13x13 and 5x5 — *small*. A 5x5 map caps a spatial avalanche at size 25, giving log10(25) = 1.4 decades. On 13x13: log10(169) = 2.2 decades *only if* the whole map is supra-threshold, which saturates and kills the power-law. Realistic per-image per-layer dynamic range: 0.5-1.5 decades.

Aggregating across 10000 images raises sample *count* at each size but not size *range*. CSN requires >= 2 decades above x_min for a credible fit. Fashion-MNIST with this architecture will struggle to clear that bar on any single layer.

**Mitigations.** (i) CIFAR-10 with the same pipeline: 32x32 inputs, deeper CNN gives log10 ~4-5 decades of headroom at essentially zero engineering cost. (ii) Cross-layer avalanches treated as depth-time series: support ~37000, realistic fitable ~2-3 decades. (iii) Scaling the CNN width/depth: erodes the "infrastructure already exists" advantage.

**Verdict.** Fashion-MNIST with the *current* architecture is marginal for the 2-decade bar. CIFAR-10 with the same pipeline fixes it cheaply. Dataset swap required before promotion.

## 3. CNN vs ViT vs BERT as cross-architecture control

The brief's sharpest concern — and the decisive one.

Candidate 1's transformer target has two orthogonal axes of specificity: **modality** (text, autoregressive, heavy-tailed token inputs) and **architecture** (residual + attention + LayerNorm + GELU, decoder-only). A CNN-on-Fashion-MNIST arm changes both simultaneously. If alpha_CNN differs from alpha_GPT2, we cannot tell whether modality or architecture drove it. That is a weak universality control.

Stronger controls, in decreasing cleanness:

- **ViT-Tiny on CIFAR-10 / ImageNet-100** (vision modality + transformer architecture) — isolates modality. Pretrained ViT-Tiny is 22M params, ~0.1 GB fp16, fits trivially on a 3060. Standard HuggingFace / timm loader.
- **BERT / RoBERTa** (text modality, encoder-only transformer) — isolates decoder-only direction.
- **Vision CNN** (vision modality + non-transformer) — changes both axes, weakest of the three, plus the sample-support problem from Section 2.

Universality-class language in statistical mechanics specifically turns on changing one microscopic detail while fixing others. The CNN arm as proposed fails this discipline.

**Verdict.** ViT-Tiny is the strictly-better control. Swap strongly recommended. Engineering cost relative to the existing CNN is ~1 day.

## 4. Bundle with Candidate 1 or stand alone?

The brief's fourth concern.

Candidate 1 already lists "at-init baseline" as required control and uses the same pipeline. A cross-architecture arm is naturally a *section of Candidate 1*, not an independent deliverable.

As a standalone paper Candidate 11 is thin: a single-architecture replication without the transformer target is not a research contribution but a methods-transfer. Its value is *conditional on Candidate 1 existing* — the pair is a universality statement; Candidate 11 alone reduces to "CNN on Fashion-MNIST has / does not have avalanche criticality", workshop material at best, crowded out by the already-settled Xiao 2018 at-init story.

**Verdict.** Absorb into Candidate 1 as a cross-architecture-control section, or structure Candidate 1 + Candidate 11 as a two-paper programme whose second paper headlines *universality across transformer + ViT + CNN exponents* rather than Fashion-MNIST specifically.

## 5. Required controls vs the 8-item knowledge-base bar

Against `knowledge_base.md §5`:

| # | Item | Handled? |
|---|---|---|
| 1 | P(s) via `powerlaw` + KS + p + LLR | Implicit — not committed |
| 2 | alpha ~ 3/2 with 95% CI | Yes |
| 3 | beta, gamma, scaling relation | Yes (crackling-noise exponents) |
| 4 | Shape collapse | **Missing** |
| 5 | sigma ~ 1 via MR estimator on >= 2 axes | Partial |
| 6 | Threshold plateau | **Missing** |
| 7 | At-init control | Yes |
| 8 | Neutral-null rejection (Martinello) | **Missing** |

Three hard, one partial, three missing, one implicit — worse than Candidate 1's 6/8. A promotion-grade rewrite must commit to shape collapse, threshold plateau, CSN statistical-test language, and parallel Candidate 12 null-rejection.

## 6. Falsifiability and compute

**Kill condition as written**: "Negative result is itself informative." Too permissive — "informative" is not a binary. A proper pre-registered kill: "if neither Fashion-MNIST CNN nor the at-init control yields >= 2 decades with CSN p > 0.05, drop the CNN arm from any universality claim." Sharpen before promotion.

**Compute.** Fashion-MNIST CNN trains in ~10 minutes on a 3060. Activation caching + CSN + MR-estimator + crackling-noise is <1 day. 1-week estimate is correct if Fashion-MNIST is kept, 1.5 weeks if swapped to ViT-Tiny on CIFAR-10.

## 7. Venue fit

As standalone: workshop-only. NeurIPS SciForDL or ICLR Tiny Papers. Not journal-grade.

As cross-architecture section of bundled Candidate 1 + 11: upgrades the combined paper from "first avalanche measurement on GPT-2" to "first cross-architecture avalanche universality test", which is a stronger journal pitch (Entropy, Neural Computation, PRX Life).

## 8. Verdict and one-line justification

Three substantive problems. (i) Fashion-MNIST with the existing 28x28 CNN gives marginal (~1.5 decades) dynamic range on single-layer spatial avalanches, below the 2-decade CSN bar; CIFAR-10 fixes this cheaply. (ii) A CNN is the weakest of three plausible cross-architecture controls — it changes modality and architecture simultaneously, violating universality-class discipline; ViT-Tiny on CIFAR-10 is strictly better at the same compute cost. (iii) Four of eight knowledge-base evidence-bar items are uncommitted — shape collapse, threshold plateau, CSN test language, Martinello null.

**Verdict — REFRAME.** Absorb into Candidate 1 as a cross-architecture-universality arm, swap Fashion-MNIST CNN for ViT-Tiny on CIFAR-10 (retain a CIFAR-10 CNN arm only if 2+-decade support is demonstrated upfront), and upgrade the required-controls list to match Candidate 1's 8-item bar. No independent workshop paper.

---

**External sources consulted** beyond `papers.csv` / `literature_review.md`:

- Clauset, Shalizi, Newman 2009 "Power-law distributions in empirical data", *SIAM Review* 51:661 — CSN methodology and 2-decade minimum guidance. [arXiv:0706.1062](https://arxiv.org/abs/0706.1062)
- Kanders, Lorimer, Stoop 2017 "Avalanche and edge-of-chaos criticality do not necessarily co-occur", *Chaos* 27:047408 — establishes distinctness of at-init edge-of-chaos (Xiao 2018) and activation-avalanche fingerprints. [pubs.aip.org](https://pubs.aip.org/aip/cha/article/27/4/047408/322534/)
- Xiao et al. 2018 (paper 3003) — at-init CNN mean-field theory, reviewed against the trained-avalanche gap.
- `/home/col/entropy/fashion_mnist_project/fashion_mnist_classifier.py` — inspected for per-layer support sizes.
