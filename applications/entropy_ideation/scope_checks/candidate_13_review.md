# Phase -0.5 Scope-Check — Candidate 13

**Candidate.** Branching-ratio regulariser. Add `L_total = L_CE + lambda * sum_l (sigma_l - 1)^2` during training. Test sample efficiency, generalisation gap, and grokking vs lambda = 0 on nanoGPT + TinyStories and on modular-arithmetic grokking. Compute differentiable sigma_l via Jacobian-spectral-radius power iteration per batch.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Novelty vs papers.csv and 2024-2026 arXiv

The candidate claims mean-field init [3002 Schoenholz 2017] fixes criticality only at step 0, and that no prior work penalises criticality *during* training as an auxiliary loss. That framing is pre-empted in at least three lines of 2018-2025 work.

**Direct pre-emption — Falanti et al., *Lyapunov Learning at the Onset of Chaos* (arXiv 2506.12810, June 2025).** Adds exactly `L_total = L_MSE + alpha * |lambda_max|` where `lambda_max` is the largest Lyapunov exponent, computed differentiably via QR decomposition of the unrolled Jacobian, backpropagated per step. Applied to feedforward nets on Lorenz regime-shift tasks; the authors explicitly flag "future work: transformers and SSMs". Candidate 13 *is* that future work, one architecture step removed. The regulariser form, the differentiable-Jacobian machinery, and the "push training to the edge" framing are identical at the loss-function level. Residual uncovered axes: (i) transformer architecture, (ii) per-layer vs global, (iii) target `sigma_l = 1` rather than `lambda_max = 0` (reparameterisation), (iv) grokking as test bed.

**Secondary pre-emption — Lewandowski et al., *Learning Continually by Spectral Regularization* (arXiv 2406.06811, 2024).** Per-layer penalty `sum_l (sigma_1(W_l) - 1)^2` kept near one during training via power iteration; ~1 extra JVP per layer per step. Structurally identical to Candidate 13 if "sigma_l" is read as the weight-matrix spectral norm (the dominant contribution to the Jacobian spectral radius in ReLU MLPs). Empirical claim — keeping singular values near one improves continual trainability — overlaps directly with what Candidate 13 proposes.

**Foundational — Miyato et al. 2018 SN-GAN; Yoshida & Miyato 2017 Spectral Norm Regularisation.** Exactly the power-iteration-per-step machinery Candidate 13 proposes, same overhead, deployed at transformer scale in BigGAN/StyleGAN/SAGAN for seven years. Spectral *normalisation* is a hard cap `sigma_1 <= 1`; Candidate 13 relaxes to a soft penalty centred at 1. The soft-vs-hard distinction is real but the implementation overhead and "regulates Lipschitz/spectral radius per layer during training" claim are not new. Also adjacent: Arjovsky 2016 unitary RNNs (parametrisation-based), Spectral Norm Variance Regularisation (OpenReview 2024).

**What is genuinely novel after this pre-emption:** (a) activation-space sigma_l (causal MR-estimator definition, §2.2 of knowledge_base) rather than weight-matrix spectral norm — if Candidate 13 commits to this distinction; (b) grokking transitions on modular arithmetic as test bed, untouched by Falanti/Lewandowski/Miyato; (c) soft-penalty framing on transformer scale.

**Novelty verdict.** Mechanism not novel. Observable (if committed to activation-space sigma) and test bed (grokking) are genuinely new. The candidate_ideas sentence "no published work penalises criticality during training" is factually wrong and must be rewritten.

## 2. The sigma_l identifiability problem

Load-bearing scope issue, unaddressed in the candidate.

`knowledge_base.md §2.2` defines sigma_l as a *causal* observable recoverable via the MR estimator [1015 Wilting-Priesemann] on subsampled activation streams. Candidate 13's proposed method — Jacobian-spectral-radius power iteration — is not the MR estimator. It is the spectral radius of post- wrt pre-activation Jacobian. These agree only in the mean-field limit (Poole 2016, Schoenholz 2017), which is known to break in trained transformers with residual streams, attention, and extreme activation sparsity.

Penalising the Jacobian spectral radius is well-defined and tractable — it is what Lewandowski, Miyato, and Falanti do. But then Candidate 13 no longer measures what Candidates 1/2/3 measure, and the cross-candidate "sigma_l controls training" narrative breaks. The candidate must either (a) rename the target and accept full overlap with Lewandowski 2024, or (b) design a differentiable relaxation of the MR causal estimator — itself a research problem, unmentioned in the brief.

**Verdict.** Disambiguate target before implementation. Conflating Jacobian-spectral-radius with MR branching-ratio is a category error peer reviewers will catch.

## 3. Compute feasibility (brief's headline concern)

Empirical anchors: Miyato 2018 spectral normalisation via power iteration adds ~5-10 % per step on DCGAN with warm-start; Lewandowski 2024 adds <20 % on supervised benchmarks; Falanti 2025 QR-based Lyapunov regulariser on 4-layer MLP adds ~2x per step.

Candidate 13's "~20 JVPs per layer per step" is a 5-10x overestimate. One power iteration (1 JVP + 1 VJP per layer per step) suffices when the previous step's top eigenvector is reused as warm start (standard since Miyato). Realistic overhead on 12-layer nanoGPT: 20-40 %, not 2x.

nanoGPT-small on TinyStories on RTX 3060 12 GB: ~8-12 GPU-hours per full run at ~300k steps. With 40 % overhead: 12-17 hours. lambda-sweep of 5 values x 3 seeds = 15 runs = 180-250 GPU-hours = 8-11 wall-days. Modular-arithmetic grokking is much cheaper (~30 min each, 30 seeds x 3 conditions = 1-2 days). Plus debug cycles. Realistically 2.5-3 weeks if nothing breaks; 4+ weeks if the MR-vs-Jacobian disambiguation forces a second regulariser implementation.

**Verdict.** Feasible at 3 weeks *if* warm-started power iteration is used (not brute 20-JVP) and *if* target is Jacobian spectral radius. Tight but not infeasible. Correct the 20-JVP estimate in the brief.

## 4. Falsifiability and missing controls

Given kill line: "If no lambda beats lambda = 0 on val-loss at matched compute, or if sigma_l is uncontrollable, the claim dies." Too permissive.

**Required additional controls:**

1. **Weight-decay ablation.** Zhang 2107.09437 and edge-of-chaos lit show weight decay already pushes toward the ordered phase, i.e. reduces effective sigma_l. Without a parallel weight-decay sweep, a positive result is indistinguishable from "reparameterised weight decay". Single most important control, currently absent.
2. **Dropout ablation.** Stochastically prunes activation paths; directly alters empirical branching. Hold fixed or sweep.
3. **Spectral-norm-regularisation baseline.** Lewandowski 2024 on weights must run alongside Candidate 13 on activations, else the paper cannot claim a distinct axis.
4. **Matched-compute definition.** Same wall-clock, same optimiser steps, same FLOPs? Each gives a different conclusion when lambda > 0 adds overhead. Pre-register.
5. **At-init sigma_l.** Schoenholz critical init already starts with sigma_l = 1. Without reporting at-init value, cannot distinguish "regulariser held it at 1" from "training did it anyway".
6. **Mechanism-discrimination probe.** If lambda > 0 helps, is it via Lipschitz bounding (Miyato), criticality (Schoenholz), or implicit weight-norm regularisation (weight decay)? Compare lambda applied only at early steps vs throughout to distinguish.

With (1)-(6) the study becomes mechanistically interpretable; without them neither positive nor negative results are informative.

## 5. Venue fit and dependence

- Positive + full controls: NeurIPS / ICLR / ICML main track.
- Positive without weight-decay control: workshop only; reviewers reject on "is this just weight decay?".
- Negative: Entropy / Neural Computation / NeurIPS workshop; still valuable.
- Methodology-only (differentiable MR estimator engineering): TMLR / ICML workshop.

**Dependence.** Candidates 16 (criticality curriculum) and 17 (sigma-steered grokking) both require 13's pipeline. A kill on 13 kills them. Standalone-13 against the Lewandowski/Falanti backdrop is thin; 17 is the novel causal result the field is missing. Recommend bundling: 13 as infrastructure + nanoGPT lambda sweep; 17 as headline (active sigma-steering of grokking). 16 is weaker — annealed-lambda replicates curriculum-on-regularisation intuitions without a new observable.

## 6. Recommended reframing before PROCEED

1. Rewrite novelty claim in `candidate_ideas.md` to acknowledge Falanti 2025, Lewandowski 2024, Miyato 2018. State residual novelty (activation-space sigma, grokking, transformer scale, soft-penalty).
2. Commit to Jacobian-spectral-radius as target; drop MR-estimator language that implies a causal observable is being penalised. Flag the caveat explicitly.
3. Add weight-decay, dropout, spectral-norm-reg baselines to required controls.
4. Correct ~20-JVP estimate to 1-2 JVPs per layer per step with warm-started power iteration.
5. Reframe deliverable from "first criticality-regularised LLM" to "activation-space analogue of Miyato 2018 SN, tested on grokking and TinyStories".
6. Bundle with Candidate 17 as high-novelty companion.

## 7. Summary

**Verdict.** REFRAME. Mechanism is pre-empted by Falanti 2025, Lewandowski 2024, and Miyato 2018; residual novelty (activation-space branching, grokking, soft-penalty) is real but requires tighter scoping, the weight-decay control, and a corrected compute estimate to survive review.

**Rubric.** D = 5 (nanoGPT training data is appropriate; claim is about training dynamics, no real-data-first violation); N = 2 standalone / N = 3 bundled with 17; F = 3 (kill line exists but controls missing); C = 4 (3 weeks feasible with corrected compute estimate and target disambiguated; slips >4 weeks otherwise); P = 3 standalone / P = 4 bundled with 17. Composite supports REFRAME, not KILL.

**Action items.** (i) Rewrite novelty paragraph acknowledging Falanti, Lewandowski, Miyato. (ii) Commit to Jacobian-spectral-radius target; drop MR-causal language. (iii) Add weight-decay + dropout + spectral-norm-reg controls. (iv) Correct compute to 1-2 JVPs per layer per step with warm start. (v) Reframe as infrastructure-for-17, not standalone-headline. (vi) Defer promotion to `promoted.md` until (i)-(v) are reflected in `candidate_ideas.md`.

Sources:
- [Falanti et al., Lyapunov Learning at the Onset of Chaos (arXiv 2506.12810)](https://arxiv.org/abs/2506.12810)
- [Lewandowski et al., Learning Continually by Spectral Regularization (arXiv 2406.06811)](https://arxiv.org/abs/2406.06811)
- [Miyato et al., Spectral Normalization for GANs (arXiv 1802.05957)](https://arxiv.org/abs/1802.05957)
- [Yoshida & Miyato, Spectral Norm Regularization (arXiv 1705.10941)](https://arxiv.org/abs/1705.10941)
- [Zhang & Feng, Edge of chaos as a guiding principle for modern neural network training (arXiv 2107.09437)](https://arxiv.org/abs/2107.09437)
- [Arjovsky et al., Unitary Evolution RNNs (arXiv 1511.06464)](https://arxiv.org/abs/1511.06464)
