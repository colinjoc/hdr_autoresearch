# Phase -0.5 Scope Check — Candidate 5

## Target

> **Candidate 5 — SAE features vs raw neurons: does basis matter for criticality?**
> Compute (alpha_raw, sigma_raw) vs (alpha_SAE, sigma_SAE) on Gemma-2-2B with Gemma Scope SAEs. Include random-projection and PCA bases as controls.

## Verdict: **REFRAME → PROCEED**

Scientifically strong and fills a genuine gap, but the null as written ("bases produce same exponents within CI") is mis-specified and makes the experiment uninformative in its most likely outcome branch. Reframe around *which* basis tracks the theoretical critical manifold, add missing controls, and expand the budget from 2 weeks to 3.

---

## 1. Feasibility on 12 GB VRAM — fits

**Gemma-2-2B:** d_model = 2304, 26 layers, 2.6 B params. bf16 inference: ~5.2 GB weights + KV cache + activations ≈ **5.7 GB resident**.

**Gemma Scope JumpReLU SAEs (residual-stream suite):**
- width 16k: ~76 M params ≈ **152 MB in bf16** per layer
- width 131k: ~600 M params ≈ **1.2 GB** per layer
- width 262k (Gemma Scope 2): ~1.2 B params ≈ **2.4 GB** per layer
- width 1M (select layers): **~9 GB** — does NOT fit alongside base model; skip

Analyse one layer at a time, streaming SAEs. Base model (~5.7 GB) + one width-131k SAE (~1.2 GB) + activation buffers (~0.5 GB) ≈ 7.5 GB. Comfortable on RTX 3060 12 GB. Your back-of-envelope estimate is correct.

Weights are public (`google/gemma-2-2b`, `google/gemma-scope-2b-pt-res`). No institutional-access barrier. SAELens handles loading. **[Lieberum 2024, arXiv 2408.05147 — VERIFIED, not just VERIFY.]**

Practical: cache activations to disk once per layer (~20 GB for 1M tokens × 2304 dim bf16) and run all bases on the same tensor.

---

## 2. Prior art

arXiv + Scholar searches for "SAE basis invariance", "SAE activation statistics", "SAE power law", "SAE criticality" + papers_ml.csv:

1. **Heimersheim & Turner 2025 (arXiv 2501.17727), "SAEs Can Interpret Randomly Initialized Transformers."** SAEs trained on random-init transformers recover auto-interp scores and reconstruction metrics comparable to SAEs on trained models. **Direct implication for Candidate 5:** SAE dictionaries absorb input statistics as much as learned structure. This is a sharper null than random-projection / PCA and must be included as a 5th basis (SAE trained on random-init Gemma-2-2B, or with re-initialised SAE weights).
2. **Gao et al. 2024 (OpenAI scaling SAEs).** MSE–L0 *training-curve* scaling laws, not activation-statistics power laws. The SAE literature uses power-law fits casually without Clauset-Shalizi-Newman discipline — meaning a CSN-disciplined SAE analysis would be the first of its kind. Methodological contribution in itself.
3. **Martin-Mahoney line, "Heavy-Tailed Mechanistic Universality" (arXiv 2506.03470).** Heavy-tailed *weight/Jacobian/Hessian* spectra with specific exponents. Parallel programme on a different observable. Cite as related but distinct.
4. **"Lazy Neuron" [3036] + Deja Vu [3038]:** raw-neuron activations already heavy-tailed. Raw basis is *not* a trivial null — the right null is iid-matched-sparsity shuffling.
5. **"Sparse but not Simpler" (vision transformers, 2025):** sparse activations are not always more monosemantic than learned SAEs. Sparsity ≠ privileged basis.
6. **MDL-SAEs (Ayonrinde et al. 2024, arXiv 2410.11179).** Principled alternative framing for "which basis has least redundant structure". Tangential.

**No paper computes CSN-disciplined avalanche or branching exponents in the SAE basis.** Confirmed gap.

---

## 3. The null is mis-specified — the load-bearing issue

The proposal states: *"Test null: all bases produce same exponents within CI. If exponents differ by less than 0.1 across all four bases, basis-invariance holds and the differential-criticality claim dies."*

This is backwards.

**(a)** Basis-invariance is the *unexpected* outcome. Raw neurons (d=2304, dense) and SAE features (d=16384–262144, L0≈100) have different dimensionality, different sparsity, and different correlation structure. Under any generative model where exponents depend on sparsity or dimension, they *must* differ. The strong null for criticality is iid sparsity-matched shuffling, not basis-transform invariance.

**(b)** The interesting scientific question is *which* basis tracks the theoretical critical manifold (mean-field DP prediction alpha ≈ 3/2). If only one basis produces clean CSN-valid power laws at the theoretical exponent, that basis is privileged. If multiple bases produce power laws but at different exponents, we have a *universality-class-by-basis* result — also novel and publishable. If no basis produces clean power laws, this kills Candidate 1's Gemma-variant criticality claim on its own.

**Reframed pre-registered kill:**

> For each basis, fit power law with CSN bootstrap; report (alpha, p, x_min, log-likelihood ratios vs lognormal / truncated exponential). A basis is "critical-compatible" if (i) p > 0.05 for power-law, (ii) alpha in [1.3, 1.7], (iii) ≥ 2 decades of scaling. Primary result: whether SAE basis is critical-compatible, whether raw is, and whether they agree on alpha. Interpretable in all branches:
> - **Divergent (expected):** some bases critical-compatible, others not → basis matters, SAE or raw is privileged.
> - **Convergent (surprising):** all four bases agree within CSN CI → basis-invariance, unexpectedly strong universality claim.
> - **All fail:** Gemma-2-2B off-critical — negative result feeding Candidate 1.

---

## 4. Missing controls / confounds

1. **Sparsity confound.** Raw (~dense), SAE (~0.6% active), random-projection (dense), PCA (dense) differ by orders of magnitude in per-unit firing rate. Required: iid-shuffled-sparsity per-basis null (destroys co-firing, preserves marginal rate) + Deja Vu-style context-sparsity null + at least one comparison at matched effective-L0 (threshold raw at 99.4-th percentile).
2. **Dimensionality confound.** 2304 vs 16384 is a 7x difference. Cluster-size support scales with dimension. Report alpha at matched dimensionality (top-2304 PCA; random 2304-subset of SAE) alongside native-dimension comparison. If exponents match under dimension-matched but not native comparison, story is "dimensionality matters", shrinking the contribution.
3. **Threshold plateau** [knowledge_base §3.1, §5 item 6]. Exponents stable across theta in [theta/2, 2 theta], for every basis.
4. **Crackling-noise scaling relation** gamma = (beta - 1)/(alpha - 1) [knowledge_base §2.3, §5 item 3]. Multi-exponent check rules out Griffiths-phase false-positives. Candidate 5 does not mention this; it is mandatory.
5. **MR estimator for sigma** [knowledge_base §2.2]. Naive branching-ratio estimator is biased under subsampling; SAE basis is severely subsampled. Use `mrestimator`.
6. **SAE width robustness.** Primary at width 16k (closest to raw d=2304); replicate at 131k and 262k. If alpha drifts with SAE width, "the SAE exponent" is not well-defined.
7. **Layer choice:** report at ≥ 3 layers (early/mid/late, e.g. 6, 13, 20 of 26). Coordinate with Candidate 6 (layer-depth gradient) to share cache.
8. **Random-init SAE** (the 5th basis, per §2 item 1). SAE trained on frozen-at-init Gemma-2-2B activations, or re-init SAE weights. Decisive null — if trained-SAE and random-init-SAE exponents match, "SAE basis is privileged" fails directly.

---

## 5. Cost

Stated 2 weeks is too tight. Realistic:

- Infrastructure (SAELens + TransformerLens + Gemma-2-2B + activation cache): 2–3 days.
- Activation caching (1M–5M Pile tokens × 3 layers, bf16 to disk): 1 day compute, 60–100 GB disk.
- Six bases × CSN + MR + threshold sweep × 3 layers: ~1 week.
- Crackling-noise check + null models + shape collapse: 3–4 days.
- Writing + plots: 3–4 days.

**Revised: 3 weeks.** Storage (100 GB scratch) is the real bottleneck, not VRAM.

---

## 6. Positioning

Interpretable in all outcomes:

- **Divergent:** workshop paper at ICML Mech-Interp / NeurIPS ATTRIB. Natural co-submission with Candidate 1.
- **Convergent:** stronger claim, "criticality observables are basis-invariant in trained transformers" — main-track ICLR / NeurIPS candidate.
- **All-fail:** merges into Candidate 1 negative result on Gemma-2-2B.

Audience: Anthropic/DeepMind interpretability + statistical-physics criticality. Both will scrutinise power-law fits; CSN discipline is not optional.

---

## 7. Dependencies

- **Prerequisite:** Candidate 1 pipeline validated on GPT-2 first. Candidate 5 re-uses it.
- **Coordinate with:** Candidate 6 (layer-depth gradient on Gemma) — share the activation cache.
- **Tooling:** `powerlaw`, `mrestimator`, TransformerLens, SAELens, Gemma Scope public weights. All available.

## 8. Final verdict

**REFRAME → PROCEED**, conditional on:

1. Rewrite the null per §3 (basis-divergence is expected; the informative question is *which* basis is critical-compatible).
2. Add sparsity- and dimensionality-matched controls (§4 items 1, 2).
3. Add random-init SAE as 5th basis (§4 item 8).
4. Require crackling-noise cross-check, threshold plateau, MR sigma estimator (§4 items 3, 4, 5).
5. Budget 3 weeks.
6. Sequence after Candidate 1 pipeline validation.

With these, Candidate 5 plugs a real gap (first CSN-disciplined criticality measurement across SAE vs non-SAE bases) and is informative in every outcome branch. Without them, the stated kill condition kills the wrong branch and the paper is either unsurprising-by-construction or unfalsifiable.
