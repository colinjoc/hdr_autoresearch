# Phase -0.5 Scope-Check - Candidate 28

**Candidate.** Per-attention-head branching ratio `σ_{layer,head}` across all heads of GPT-2 small (144) / medium (288). Report the histogram; test unimodal vs bimodal (Hartigan's dip) vs power-law (CSN). Distributional, not circuit-specific.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME, leaning ABSORB.** The distributional framing is cleaner than Candidate 8's circuit-vs-control comparison and removes the definitional quicksand of "attention-pattern avalanche" — the observable here is the per-head causal branching ratio, which is well-defined once the causal protocol is fixed. But as written, Candidate 28 is (a) under-powered as a standalone distributional-shape paper (144 / 288 samples for a bimodality test with induction heads at ~5-10 of 144 is near the statistical floor); (b) dependent on unspecified causal machinery whose cost dominates the 2-week estimate; (c) substantially overlapping with the reframed Candidate 8 (causal-cascade definition). Recommended reframe: merge C28 and the causal-cascade version of C8 into a single Paper-1 section on "head-resolved causal σ, with distribution shape and induction-head sub-analysis as joint deliverables". Promote to standalone only if the model panel is widened to five+ models so the distributional claim has cross-architecture support.

## 2. Is per-head σ meaningful given the common residual stream? (Concern a)

**Yes, but only under a causal definition. Correlational per-head σ is trivially confounded.**

The residual-stream confound is the same one flagged for Candidate 6 (§2 of `candidate_06_review.md`): `h_{l+1} = h_l + F_l(h_l)` means any correlational "how much does activity at this head at layer l predict activity at layer l+1?" reads back σ ≈ 1 tautologically, because the head's output is a rank-`d_head` write into the residual stream and the residual stream is algebraically preserved. For attention heads specifically, the write is `sum_j softmax(QK^T/sqrt(d_k))_ij V_j W_O^h`, and the naive per-head σ conflates (i) the norm of that write, (ii) how much of the write is aligned with the residual stream's principal components, (iii) whether downstream heads / MLPs actually route on it.

Only definition that survives: **per-head causal σ via ablation + patching** — patch head `h` at layer `l` with its mean-over-prompts output (or zero-ablate), count how many units at layer `l+1, l+2, ..., L` change by > θ, and average over prompts. This is exactly the protocol the candidate states ("Per-head causal branching via attention-head ablation + patching"), and it is the correct choice. But the candidate does not say whether the cascade is counted at (i) layer `l+1` only (one-step branching, consistent with σ), (ii) across all downstream layers (cascade-size, consistent with α), or (iii) until cascade death (cascade-length, consistent with β). Pre-registration of (i) is the tightest match to σ; (ii) and (iii) bleed into Candidate 1's avalanche observables and create a naming collision. Fix: call the observable `σ_{l,h}^causal` and define it as the one-step next-layer branching.

**Side concern — attention sinks.** Gurnee 2026 (arXiv 2604.14722, cited in `candidate_08_review.md`) shows attention sinks concentrate mass on position 0 for nearly every head in GPT-2. If head ablation is done on the `A_{ij}` weights, sink ablation may dominate causal effect regardless of head identity, compressing the σ distribution. The protocol must ablate at the head-output level (`head_output = A V W_O^h`), not at the attention-weight level.

## 3. How does C28 differ from C8? (Concern b)

**Under the causal-cascade reframe of C8, the two are near-duplicates with different primary plots.**

C8 (post-reframe per `candidate_08_review.md` §9): pre-register an induction-score threshold, split heads into `induction` vs `matched-entropy-control`, compute causal-cascade exponents on each, test whether induction-head exponents are outside the sparsity-matched null CI.

C28: compute the *same* causal-cascade or branching observable on *all* 144 / 288 heads and report the histogram. The induction-head subset is then implicit — their σ values are dots in the histogram.

C28 is the strictly more informative protocol for two reasons: (i) it avoids pre-committing to a binary induction / control split that is well-known to be continuous (TransformerLens induction score is a real-valued quantity, not a label); (ii) a distributional view tests "is the σ heterogeneity concentrated in a known circuit, or is it distributed across the whole head inventory?" — the latter is the null for C8 and C28 makes it the subject.

The pair is therefore not two papers. Recommended arrangement: **C28 is the figure, C8 is the sub-analysis**. The histogram answers "what is the shape of σ across heads?"; the induction-head labelling on that histogram answers "do induction heads occupy a specific region of the distribution?". Both fit in a single Paper-1 section, ~2-3 figures, matching `promoted.md` line 16 ("C8 - §X of Paper 1, or kill") and line 149 ("C8 §X circuit-specific, if causal-cascade reframe holds"). Running them as two separate projects double-books the infrastructure (activation cache, patching harness, threshold sweep, bootstrap) for a marginal differentiation.

## 4. Is 144 heads enough sample? Or need multiple models? (Concern c)

**144 is marginal for bimodality, inadequate for power-law, and inadequate for cross-model claims. 288 (GPT-2 medium) helps modestly. Cross-architecture is required.**

Hartigan's dip test with n = 144 has ~80 % power to detect two modes separated by ~1 inter-mode-SD (Hartigan & Hartigan 1985 Table 1); for induction heads at ~5 / 144 of the sample, the second mode is under-populated and dip-test power collapses — the test is designed for roughly balanced mixtures. Mixture-model likelihood (2-component Gaussian fit, BIC vs 1-component) is a better choice and is reliable at n ≈ 100-200 for moderate separation. Report both. The candidate specifies only Hartigan's dip test; this is a methodology weakness.

Power-law fit on 144 points fails the `>= 2 decade, >= 50 events/decade` bar (`knowledge_base.md §2.1`, `literature_review.md` pitfall 1) outright. If σ is bounded in [0, 3] (plausible empirical range) the dynamic range is less than one decade. A power-law-in-σ-values claim is unviable at this sample size. If the candidate means power-law in a *derived* quantity (e.g. head activation norm, head ablation-effect magnitude) the right section is Candidate 1's avalanche-size distribution, not C28. Strike the power-law hypothesis from C28; keep bimodality-vs-unimodality.

**Cross-model requirement.** A distributional claim on one model (GPT-2 small, 144 heads) is descriptive at best. The publishable version asks: is the distribution shape *universal* across GPT-2 small (144) + medium (288) + GPT-2-XL (300) + Pythia-1.4B (256) + OLMo-1B (256) + TinyLLaMA-1.1B (352) → ~1500 heads total with per-model histograms. This also directly tests whether the induction-head mode is at a consistent σ value across models, which bears on the Gurnee 2024 universality claim (§5 below). Scoping to GPT-2 S + M only is the weakest viable panel and should be escalated.

## 5. Relation to universal-neurons literature (Concern d)

**Strongly related. C28 is the per-head analogue of Gurnee et al. 2024 on neurons, and must engage that paper explicitly.**

Gurnee, Horsley, Guo et al. 2024 ("Universal neurons in GPT-2", paper 3034) finds ~1-5 % of GPT-2 MLP neurons are *universal* across random seeds — same functional role in replicate training runs. The immediate question C28 must answer: is the σ-distribution across heads reproducible across seeds? If the bimodality (or its absence) is seed-dependent, the claim is fragile. Gurnee's methodology — train 5 GPT-2-small replicates with different seeds, compare neuron-wise features — is the natural design pattern. Pythia releases 9 seeds of Pythia-160M; that is the right model for the seed-robustness test because GPT-2 has only one public seed.

The deeper relation: if a small fraction of *heads* is distinguished on σ (paralleling universal neurons), and the distinguished heads coincide with induction / previous-token / name-mover heads from Wang 2023 IOI (paper 3025), C28 provides a dynamical-observable grounding for the universal-circuit hypothesis. This is a substantially stronger framing than "is the histogram bimodal?" and should be the headline in the reframed version.

Also relevant, not yet in `papers.csv`: Chughtai, Chan, Nanda 2023 "A toy model of universality" — toy-model replication of Gurnee; Lieberum et al. 2024 Gemma-Scope across-seed stability for SAE features. Neither provides per-head σ, but both constrain what "universality" should mean methodologically.

## 6. What is the right null? (Concern e)

**Not iid Bernoulli. The null hierarchy is: (i) per-head-activation-sparsity-matched shuffle, (ii) layer-matched-shuffle, (iii) attention-entropy-matched shuffle, (iv) random-read/write-direction head with matched OV and QK spectral norms.**

Per `candidate_05_review.md` §4 and `candidate_08_review.md` §5, an iid Bernoulli null destroys co-firing structure and is trivially rejected — it matches *marginal* firing rate but not the anisotropy that drives branching. For C28 specifically, the hierarchy is:

1. **Sparsity-matched per-head null.** For each head, shuffle its attention patterns across tokens (preserve per-head marginal sparsity, destroy per-token coherence). Recompute causal σ. Distribution of nulled σ gives the "what would σ look like if this head had no coherent function?" baseline. Expected result: narrow unimodal distribution centred near 0 (ablation cascades are short when pattern is scrambled).

2. **Layer-matched null.** Compare head `h` at layer `l` against other heads at layer `l` only. Controls for the confound that early layers have mechanically higher σ (more downstream layers over which to cascade). This is the right control for the within-layer heterogeneity claim.

3. **Attention-entropy-matched null** (Zhai 2023 / Gurnee 2026 considerations). Attention sinks and entropy-collapsed heads have distinctive σ for sharpness reasons, not functional reasons. Match on attention entropy before making functional claims.

4. **Random-OV null.** Replace the trained `W_O W_V` product with a random matrix of matched Frobenius norm. Preserves head capacity, destroys learned function. This is the "does the σ heterogeneity come from training or architecture?" null and plays the role of Candidate 1's at-init control.

The pre-registered kill (`σ-range < 0.05 with uniform distribution`) is too weak. Tighten to: **(a) KS distance between trained and random-OV-null σ distributions is < 0.1**, OR **(b) at least 3 / 4 of the above nulls fail to reject unimodality when the trained-network distribution passes dip-test rejection**. Either condition kills the "heads are functionally heterogeneous on σ" claim.

## 7. Cost and feasibility

Per-head causal patching: for GPT-2 small, one patching run = 1 prompt × 12 layers × 12 heads × 1 ablated head × forward pass. At ~1 k prompts × 144 heads × single forward = 144 k forward passes. GPT-2 small inference is ~50 ms/prompt on RTX 3060; wall-clock ~2 hours. Activation caching for cascade measurement doubles to ~4 hours. GPT-2 medium: 2 x layers, 2 x heads, ~16 hours. Threshold sweep (5 values) × model (2) × null (4) × seed (1 for GPT-2, 9 for Pythia replication) brings the total to ~1-2 GPU-weeks including pipeline debugging — not 2 weeks as estimated, but close, and fits Paper 1's extension slot.

If the cross-model panel (§4) is adopted, add ~5 GPU-days for the four extra models. Total ~3 weeks; tight but achievable on one RTX 3060.

## 8. Methodological fixes required before promotion

1. Specify the causal protocol: head-output ablation (not attention-weight ablation); one-step branching (not cascade size); pre-registered threshold sweep [theta/2, 2*theta].
2. Drop the power-law hypothesis from C28 — unviable at n = 144. Retain bimodality-vs-unimodality only.
3. Replace Hartigan's dip test with 2-component GMM vs 1-component BIC comparison as primary; Hartigan as secondary. Report both.
4. Widen model panel to GPT-2 S + M + XL at minimum; add Pythia-160M x 9 seeds for the seed-stability test that makes the distributional claim cross-seed-robust.
5. Replace the existing null with the four-level hierarchy in §6. Pre-register which nulls must fail for each verdict.
6. Explicitly engage Gurnee 2024 (paper 3034) as methodological precedent and reframe the headline around "are some heads dynamically distinguished in a seed-robust way?" rather than "is the histogram bimodal?".
7. Reconcile with the reframed C8. Recommended: absorb C8 as the induction-head labelling of the C28 histogram, run both as one Paper-1 section.

## 9. Final disposition

**REFRAME → ABSORB** into Paper 1 as the head-resolved-σ section, co-scoped with the reframed C8. Standalone only if the six-model cross-architecture panel is committed and the Pythia seed-replication is run. Otherwise promote as §X of Paper 1, parallel to `promoted.md` lines 14 and 16 (C6 and C8 already absorbed as §4 and §X of Paper 1).

*Word count: ~1490.*
