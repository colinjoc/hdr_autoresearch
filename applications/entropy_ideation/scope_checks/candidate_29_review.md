# Phase -0.5 Scope Check — Candidate 29

## Target

> **Effective dimension tracks σ.** On Pythia checkpoints, compute participation-ratio / effective dimension D_eff of residual-stream covariance; compare σ in the ambient basis vs σ in the top-K-PC subspace (K = D_eff). ML replication of Fontenele 2024 [4005] Sci. Adv. "low-dim critical subspace embedded in high-dim awake cortex."

## Verdict: **REFRAME → PROCEED**

Scientifically excellent, novel as a σ-based test, feasible on 12 GB. Three load-bearing fixes required: (a) port Fontenele's actual protocol, not a summary of it; (b) position against Liu-Paquette-Sous 2025 (NeurIPS OPT workshop), which publishes the covariance-spectrum-through-Pythia-training axis; (c) argue MR-estimator correctness on projected activations. With these, promote to Paper 4 §3 (MI bridge) or as a standalone Fontenele-in-LLMs short.

---

## 1. Fontenele 2024 [4005] — verified, and different from the proposal

Fetched Sci. Adv. eadj9303 / PMC11051676. Protocol on awake mouse motor-cortex spikes (N ≈ 200):

1. PCA on binned spike-count matrix (sklearn).
2. **Critical subspace K defined operationally**: largest k such that removing PC1..PCk collapses the avalanche power-law range below 1.5 decades. K is "rarely > 3, 13 at most" out of 200. **Not K = D_eff.**
3. Avalanche statistics computed on *population-summed activity reconstructed from the top-K-PC subspace*, not on individual PCs.
4. Maximum-likelihood power-law fit, custom F ≥ 0.8 goodness-of-fit. **They do not use the Wilting-Priesemann MR estimator**; their σ-equivalent is Sethna crackling-noise.
5. Criticality emerges only at Δ_T ≥ ≈ 10·⟨ISI⟩ — time-bin-dependent.

**Proposal mismatch.** K = D_eff is a convenience, not Fontenele's protocol. Fontenele projects *and sums back* to a scalar; he doesn't measure σ inside the K-dim subspace per-component. Time-bin dependence isn't mentioned in the proposal but maps directly onto the LLM token-vs-context-vs-batch aggregation axis.

**Fix.** Sweep K = 1..d_model; at each K compute σ on the reconstructed scalar population activity of the top-K-PC subspace AND of the complementary (d_model − K)-dim desynchronised subspace. Report K* = smallest K at which top-K is σ-critical-compatible (σ = 1 ± 0.02, MR 95% CI) AND complement has σ < 0.95. Sanity-check K* against D_eff = (Σλᵢ)²/Σλᵢ²: if K* ≈ D_eff, Fontenele transfers cleanly; if K* ≫ D_eff or K* ≪ D_eff, *that* is the ML-transfer result.

---

## 2. Prior art — the landscape has moved

**Liu, Paquette & Sous 2025 (NeurIPS OPT workshop, paper 43).** "Evolution of the Spectral Dimension of Transformer Activations." Fits covariance spectrum λᵢ ∝ i⁻ᵅ across OPT and Pythia 100 M – 70 B through fine-tuning; finds α < 1, rising with layer depth and training. **Implication:** the covariance-spectrum-through-training axis is *published*. C29's remaining unscooped claim is not "does dimensionality change during training" but "does σ *inside* the D_eff-dim subspace cross 1 at a training step that ambient σ does not flag." That is the σ-in-subspace claim; Liu-Paquette-Sous do not touch σ or branching ratios.

**Tulchinskii 2024 EACL "Shape of Learning."** Intrinsic dimension (TwoNN/MLE) of embeddings across training: expansion-then-compression. Related cousin, different estimator, no σ. Cite; not a scoop.

**Tulchinskii 2023 NeurIPS.** PHD-based AI-text detection. Different observable (embedding-set PHD), different question. Cite; not a scoop.

**Xu 2026 (arXiv 2602.10496) "Low-Dimensional Execution Manifolds."** Modular-arithmetic transformers collapse onto a 3–4-dim manifold in d=128, with > 92% of SGD non-commutativity orthogonal. Closest ML precedent for Fontenele's "critical subspace ⊥ desynchronised subspace" picture. **Must position against**: C29 is the pretrained-LLM analogue with σ (not execution) as the observable.

**Wang 2026 (arXiv 2604.16431, 2604.04655).** Dimensional criticality of *gradient-avalanche* process at grokking — different dynamical object (gradients, not activations). Cite in intro only.

**Net novelty after these.** Unscooped pair: (i) in trained transformers σ_topK ≠ σ_ambient, specifically critical-compatible-vs-desynchronised split à la Fontenele; (ii) this split emerges during training, with a σ_topK = 1 crossing that ambient σ hides. Both remain novel.

---

## 3. Is ambient-vs-subspace σ comparison well-posed? — yes, with caveats

**MR estimator on projections.** Wilting-Priesemann 2018 proves unbiasedness under subsampling; the proof relies on r_k = m^k holding for any *linear* observable of the branching process. PCA projection is a weighted linear sum — different from subsampling but covered by the same proof. **Applicable, but the candidate must argue this explicitly in methods**, not assume it. Cite Wilting-Priesemann 2018 §Methods and Spitzner 2021 Mr. Estimator §2.

**Complementary-subspace σ.** Fontenele's desynchronised (N − K)-dim subspace is the sharper asymmetry test. Compute σ_ambient, σ_topK, σ_complement; the Fontenele pattern is {intermediate, ≈1, < 0.95}.

**Random-subspace null (mandatory).** A Gaussian K-dim random projection should give σ indistinguishable from ambient. Without this the finding could be an artefact of "any K-dim projection pulls σ toward 1."

---

## 4. Relation to C5 (SAE basis) — subspace σ is a *stronger* claim

C5 is a *basis change* on the full activation space (all info preserved, sparsity/dimensionality re-parameterised). C29 is a *lossy projection* (discards d_model − K dimensions claimed desynchronised).

**Implication.** If C29 is positive, C5's basis-invariance negative becomes uninformative: criticality could be a subspace-localised property that gets averaged out in any *full-rank* basis. C29 therefore *reframes* C5 — already flagged in promoted.md §4005 but now concrete.

**Sequence + bundle.** Run C29 before or in parallel with C5. Add an explicit bridge experiment: cosine-overlap between top-K-PC directions and top-activating SAE features. If the critical subspace aligns with the learned SAE dictionary, "interpretable critical subspace" becomes a tight joint claim for Paper 4.

---

## 5. Pythia × RTX 3060 feasibility — comfortable on C7's five-scale × 20-ckpt grid

Grid: 70 M / 160 M / 410 M / 1.4 B / 2.8 B × 20 log-spaced checkpoints = 100 cells.

**Memory.** Covariance d_model × d_model, worst case Pythia-2.8B d_model = 2560 → 2560² × 4 B fp32 = **26 MB**. `torch.linalg.eigh` on 2560² is seconds. No VRAM issue beyond the forward pass itself (already budgeted in C7).

**Compute per cell.** (i) stream ~10⁵ tokens into a covariance accumulator (1–10 min); (ii) eigendecomp (seconds); (iii) project → scalar population activity → `mrestimator` (minutes); (iv) K-sweep at ~15 log-spaced K.

**Totals.** Primary sweep ~17 GPU-h. K-sweep × threshold × block-bootstrap (200 resamples) overhead ≈ 10× → **~170 GPU-h ≈ 7–10 days wall-clock on RTX 3060 fp16**, inside the proposal's 3-week budget.

**Disk.** *Stream* the covariance accumulator — don't cache per-token activations. Caching would need 1.6 TB across 100 cells; streaming needs < 10 GB scratch. The candidate should commit to streaming.

---

## 6. Missing controls (non-negotiable + recommended)

Non-negotiable:

1. **step0 at-init control** per scale — free with C7's checkpoint axis, mandatory per knowledge_base §5 item 7.
2. **Random-subspace null** (§3).
3. **Threshold plateau** θ ∈ {0, 0.1, p95} on the reconstructed scalar.
4. **Crackling-noise scaling relation** γ = (β−1)/(α−1) on the critical-subspace avalanche distribution — rejects Griffiths-like σ ≈ 1 artefacts in projected traces.
5. **Block-bootstrap** over token-context blocks for σ-CI.

Strongly recommended:

6. **Sparsity-matched null:** random-K-PC projection (not top) with matched variance captured. If both give σ ≈ 1, the story is "low-dim in general," not "top-PC-aligned."
7. **Fontenele time-bin-dependence analogue:** sweep (a) per-token, (b) per-sequence, (c) per-batch aggregation. Fontenele's "criticality only at Δ_T > 10·⟨ISI⟩" is the direct null — if σ_topK → 1 only at one aggregation level, replicate; at all levels, stronger claim; at none, negative result.

---

## 7. Rewritten kill

Kill if, across 5 scales × 20 checkpoints × 3 thresholds × 3 aggregation levels, *all three* hold:

- σ_topK* − σ_ambient < 0.03 at every cell;
- σ_complement > 0.95 at every cell;
- no pair (N, t) at which σ_topK crosses 1 while σ_ambient does not.

If all three, the Fontenele-in-LLM claim dies; the data is still publishable as an explicit non-transfer result with direct Paper 7 (brain-homology) relevance.

---

## 8. Positioning

- **Positive (Fontenele pattern replicates):** ICML / NeurIPS main — first direct ML replication of a Sci. Adv. 2024 neuroscience result. Paper 4 §3 or standalone short.
- **Partial (subspace asymmetry without a clean σ=1 crossing):** ICML MechInterp workshop + Entropy long.
- **Negative:** NeurIPS position paper "Fontenele does not transfer," pairs naturally with Paper 7 negative arms.

---

## 9. Dependencies

- **Prerequisite:** Paper 1 pipeline (CSN + MR + threshold sweep + block-bootstrap) validated.
- **Shares:** C7 scale-atlas checkpoint cache.
- **Bundles:** C5 basis sweep via §4 cosine-overlap bridge.
- **Co-reports:** Liu-Paquette-Sous 2025 covariance-spectrum α alongside D_eff — same spectrum, both cheap, complementary descriptors.

---

## 10. Action items before promotion

1. Port Fontenele's protocol faithfully (§1) — operational K, reconstructed scalar, complement σ, aggregation sweep.
2. Cite and position against Liu-Paquette-Sous 2025 (NeurIPS OPT workshop paper 43), Tulchinskii 2024 EACL, Xu 2026 (arXiv 2602.10496).
3. Methods section must argue MR-estimator applicability on PCA projections (§3).
4. Add §6 non-negotiable controls 1–5; recommend 6–7.
5. Rewrite kill per §7.
6. Commit to streaming covariance accumulation; drop the 1.6 TB per-token cache.
7. Bundle with C5 via SAE-topK-PC cosine-overlap experiment.
8. Budget 3 weeks post-Paper-1.

## Final verdict

**REFRAME → PROCEED.** One of the programme's highest novelty-per-cost items: a direct ML replication of the single most important non-arXiv 2024 neuroscience result in the lit review, with a pre-registered kill and three orthogonal controls. Promote to Paper 4 §3 (MI bridge) or as a standalone Fontenele-in-LLMs short; sequence in parallel with C5 once Paper 1 infrastructure lands.
