# Phase −0.5 Scope-Check — Candidate 8

**Candidate.** Induction heads and critical dynamics. Attention-pattern avalanches in induction heads vs matched-layer control heads in pretrained GPT-2 small. Test whether a specific identified circuit shows stronger critical signatures than neighbouring non-induction heads.

**Verdict: REFRAME.** The *object* being measured ("attention-pattern avalanche") is not well-defined; sample size for a per-head power-law fit is inadequate; and the core question collapses into a stronger, more tractable variant of Candidate 6 unless it is re-cast around a defensible observable. Proceed only after reframing as "per-head attention-entropy / attention-concentration dynamics on induction heads vs controls", dropping the CSN power-law avalanche claim for the attention-pattern observable.

---

## 1. Is an "attention-pattern avalanche" a well-defined object?

**No — not without a non-trivial definitional move that the candidate as written does not make.**

Attention patterns are probability distributions `A ∈ Δ^T` over context positions for each `(layer, head, query-token)` triple. `knowledge_base.md §2.1` requires an avalanche event to be a threshold-exceedance of a scalar quantity that is plausibly causally "on" or "off". Three candidate scalars exist for an attention pattern:

1. **Per-key mass `A_tk`** above threshold θ. Crossing θ defines which context positions a head "attends to". This is the most natural translation but is pathological: softmax normalisation forces `Σ_k A_tk = 1`, so a flat pattern has `A_tk = 1/T`, and a sharp induction-head pattern has `A_tk ≈ 1` on one key. The avalanche size (number of attended keys) distribution is mechanically bounded between 1 and T, with induction heads (by construction) occupying the sharp tail and non-induction heads occupying the diffuse tail. The resulting "avalanche distribution" is then a restatement of the known attention-entropy profile, not a dynamical critical observable. CSN bootstrap on such a bounded, categorically-different pair of distributions will always find "differences" that are definitional, not critical.

2. **Attention entropy `H(A)`**. Well-defined, unbounded on the tail side (can approach log T ≈ 6.7 for T = 1024), continuous. But it is a *per-token* scalar — not an avalanche size. Known literature on attention entropy is extensive (Zhai 2023 "Attention Entropy Collapse", Jha 2025, Gurnee 2025 attention sinks) and shows concentration behaviour that is the opposite of critical — entropy collapse is sharpening, entropy explosion is noise.

3. **Attention-pattern cascade across layers/tokens.** An event is an induction-head firing (QK matches the [A][B]...[A] pattern for that token); cascade size is the number of downstream components (MLP neurons, later attention heads, SAE features) whose activations change by > θ when the induction head is ablated. This is a causal-propagation construction in the `knowledge_base.md §3.3` spirit and is the only definition that is physically analogous to a neuronal avalanche. But note: this is no longer an "attention-pattern avalanche" — it is a **causal activation avalanche seeded by an attention-head intervention**, closer to Candidate 10 (ROME-style perturbations) than to the candidate as written.

Robustness to threshold choice: for option 1 the KS statistic on a threshold plateau in [1/(2T), 0.5] will move by orders of magnitude because a single token's attention mass shifts between concentrated and diffuse regimes. For option 3 the threshold plateau is inherited from Candidate 1's residual-stream avalanche framework and is tractable. The candidate as written does not specify which scalar is being measured, nor the threshold sweep — which is the first blocker under `knowledge_base.md §2.1`.

## 2. Sample-size adequacy for per-head power-law fits

**Marginal at best; fails the `≥ 2 decades, ≥ 50 events/decade` bar from `literature_review.md` pitfall 1 and `knowledge_base.md §2.1`.**

- GPT-2 small has 12 layers × 12 heads = 144 attention heads.
- Olsson et al. 2022 documents induction heads as layer-5-to-layer-6 phenomenon in GPT-2 small, with roughly 2–6 strong induction heads depending on detection threshold. Wang et al. 2023 confirmed 2 induction heads inside the IOI circuit. Gould et al. 2024 and subsequent cataloguing finds ~5–10 heads with measurable induction scores in GPT-2 small. Even at the loose end, `n_induction ≈ 10` candidates.
- A per-head power-law fit requires ≥ 500 avalanche events, per `candidate_ideas.md` Candidate 1 standard. On attention patterns, "one avalanche per token" gives 10⁵–10⁶ events per head from a modest corpus — that dimension is fine.
- The critical constraint is not event count but **dynamic range**. For option 1 above, avalanche size is bounded by T, and typical avalanches span 1–50 keys. Log₁₀(50) = 1.7 decades — borderline by Clauset 2009. For option 3 (causal cascade across layers and SAE features), cascade sizes span 1–10⁶, giving ≥ 4 decades and comfortably clearing the bar.
- **Between-head averaging is not a rescue.** Pooling 10 induction heads' avalanches into one distribution destroys the central claim ("this specific circuit shows stronger critical signatures than controls"). Per-head CSN fits are required, and per-head bootstrap CIs will be wide.

Conclusion: under the attention-pattern-scalar definitions (options 1 and 2), the sample size is adequate but the dynamic range is not, so CSN will yield 1–2 decade fits that `literature_review.md` explicitly calls out as "cannot distinguish power-law from lognormal". Under the causal-cascade definition (option 3), both sample size and dynamic range are fine — but then this is Candidate 10 in disguise.

## 3. Has any 2024–2026 paper measured criticality observables on attention heads?

**Partially — the closest hits are from 2025–2026 and either subsume this candidate or undercut its novelty claim.**

From arXiv search (April 2026):

- **Zhai et al. 2023 "Stabilizing Transformer Training by Preventing Attention Entropy Collapse"** (ICML 2023) — measures per-head attention entropy dynamics, identifies an entropy-collapse instability with a tight lower bound decreasing exponentially in the spectral norm of attention logits. This is *the* closest pre-existing treatment of attention-distribution statistics with a phase-transition-like boundary. The candidate must cite and differentiate.
- **"Critical attention scaling in long-context transformers"** (arXiv 2510.05554, Oct 2025, OpenReview 7SLtElfqCW) — explicitly analyses attention as a phase transition governed by a scaling factor with "critical scaling proportional to log n". This is a direct theoretical treatment of attention-head criticality and must be engaged head-on. If this paper already contains the mechanistic reason induction heads are distinguished, Candidate 8 is a redundant empirical replication. I have not yet read the full text and flag as VERIFY before promotion.
- **"Dimensional Criticality at Grokking Across MLPs and Transformers"** (arXiv 2604.16431) — introduces TDU-OFC, an offline avalanche probe on gradient snapshots, extracts time-resolved cascade dimension across modular-addition transformers and XOR MLPs. This is the first paper to operationalise *avalanche statistics specifically on transformer activations* at the macroscale (gradient space, not attention). It narrows the `lit_ml.md §9 gap` meaningfully — the gap statement as of 2026-04 is no longer "no paper computes avalanche statistics on transformer activations". It is now "no paper computes avalanche statistics on *residual-stream* activations" or "… at *circuit granularity*" — which is the narrower version Candidate 8 would occupy. This materially reduces Candidate 8's novelty claim and must be acknowledged.
- **Gurnee et al. 2026 "Attention Sinks in GPT-2"** (arXiv 2604.14722) — mechanistic account of attention-mass concentration on the first position in GPT-2, tied to learned query biases and positional-encoding interaction. Provides a counter-hypothesis to any "induction heads are uniquely sharp" claim: attention sinks might dominate the tail of the attention-mass distribution for *every* head, not just induction heads, making differential-criticality per-head harder to detect.
- **"Beyond Induction Heads: In-Context Meta Learning Induces Multi-Phase Circuit Emergence"** (arXiv 2505.16694) and Musat 2025 (arXiv 2511.01033) document richer induction-head emergence dynamics. These extend rather than duplicate Candidate 8's scope but inform the "matched control" choice.

Net: as of 2026-04, attention-criticality is an active area with at least two directly competing 2025–2026 submissions. The candidate as written does not engage with this literature. Before promotion the proposer must (a) read Zhai 2023 and arXiv 2510.05554 in full, (b) restate the novelty claim in terms of what those papers did *not* measure (residual-stream avalanche propagation seeded by a specific head; cascade-depth distributions from causal patching; head-level differential-criticality under a ≥ 4-decade observable), and (c) remove the unqualified `lit_ml.md §9 gap` claim that no paper computes avalanche observables on transformers — that claim is obsolete as of arXiv 2604.16431.

## 4. Is Candidate 8 a stronger version of Candidate 6, or a fundamentally different question?

**It is a stricter/circuit-level variant of Candidate 6 on the attention-pattern observable, and a distinct project only if the observable shifts to causal cross-layer cascade.**

Candidate 6 proposes layer-resolved `σ_ℓ` across depth, with hypothesis early = supercritical, late = subcritical. Candidate 8 restricts the granularity from "layer" to "head within a layer" and compares induction heads (a specific functional subset) to matched-layer controls. As formulated:

- Under option 1 (per-key mass avalanche) the observable is a per-head attention-pattern statistic. This is simply Candidate 6 at head rather than layer granularity — a useful but not orthogonal follow-up. The natural paper is "Candidate 6 extended: layer + head-within-layer resolution, with induction heads as a case study". In that framing Candidate 8 is a subsection of Candidate 6, not a standalone paper.

- Under option 3 (causal cross-layer cascade seeded by head ablation) the observable is fundamentally different — it is a cross-layer residual-stream propagation measurement seeded by a specific functional component. This is methodologically novel (knowledge_base.md §2.2 layer-resolved causal σ, with a functionally-identified seed) and distinguishes Candidate 8 from both 6 and 10. ROME-perturbation Lyapunov (Candidate 10) perturbs along *directions*; the Candidate 8 reframe perturbs by *ablating an identified functional unit*. The deliverable is different — "circuit-anchored critical sensitivity" rather than "directional Lyapunov structure".

Recommendation on the dependency: if the project proceeds only under option 3, it is genuinely distinct from Candidate 6 and complementary to Candidate 10. If it proceeds on any attention-pattern scalar (options 1–2), it should be merged into Candidate 6 as a subsection and not run as a standalone project.

## 5. Pre-registered kill condition — adequacy check

Candidate as written: *"If induction-head and control-head exponents are within CI, the circuit-specific-criticality claim dies."*

Inadequate for two reasons.

1. **"Within CI" is under-specified.** `knowledge_base.md §5` requires (a) α within 0.1 of a target for a positive claim, (b) bootstrap CI width reported, (c) threshold plateau demonstrated across ≥ 1 decade of θ. Kill must be operationalised at that level.

2. **Null model is missing.** The proper null for "induction heads are critical" is not "induction heads equal control heads" but "induction heads produce avalanche exponents distinguishable from a sparsity-matched, first-moment-matched Bernoulli null" — see `lit_ml.md §7` on the Deja Vu / context-sparse null. Induction heads have dramatically sharper attention patterns than controls *for definitional reasons* (they implement the [A][B]...[A] → [B] rule); any difference between induction and control avalanche statistics is overwhelmingly likely to be a restatement of this sharpness rather than evidence of distinct criticality. The null must control for attention-pattern sharpness (e.g. compare induction heads against matched-entropy non-induction heads, not layer-matched arbitrary heads).

## 6. Methodological constraints specific to attention-pattern avalanches

Additional constraints from `knowledge_base.md §3.3` and the MI literature that Candidate 8 as written does not address:

- **Causal vs correlational.** The proposal implies attention-pattern cascades are "caused by" upstream activations but does not specify a causal-intervention protocol. For any σ claim on attention, activation patching or path patching (Goldowsky-Dill 2023 / 3031) is the gold standard, and the MI community will not accept a correlational-only result at this scale of claim.
- **Basis choice.** Attention patterns are in the key-token basis (discrete, T-dimensional per head). There is no natural SAE analogue; the basis-invariance cross-check required by `knowledge_base.md §3.1` is not applicable. This must be declared as a known limitation.
- **Block-bootstrap on autocorrelated tokens.** Attention on text is strongly autocorrelated across adjacent tokens. i.i.d. bootstrap on attention patterns will over-narrow CIs. Block-bootstrap over sequences of ≥ 512 tokens is required.
- **Head enumeration.** The candidate does not specify how induction heads are identified. The standard TransformerLens approach (prefix-matching score on random repeated tokens) produces a continuous induction score per head, not a binary classification. The choice of "induction vs control" threshold is a hyperparameter and must be swept.

## 7. Feasibility and cost

Cost estimate (1 week) is plausible *for the attention-pattern observable on GPT-2 small*. Under the causal-cascade reframe, cost realistically 2–3 weeks because activation patching across 144 heads × ≥ 10⁴ tokens × residual-stream + MLP + attention observables is substantially heavier than attention-pattern caching. Either estimate is achievable on a single RTX 3060 12 GB for GPT-2 small — VRAM is not the bottleneck; disk for cached activations is (~5–20 GB depending on observable).

## 8. Citation drift (minor)

`candidate_ideas.md` cites `[3018: Olsson 2022]` and `[3025: Wang IOI]`. In `papers.csv` the actual row 3018 is Kaplan scaling laws; Olsson is row 3024; Wang IOI is row 3025 (the Wang cite is correct). The Olsson citation ID should be `3024`. Small fix for the promotion document.

## 9. Recommendation

**REFRAME and conditionally proceed.** Required reframe:

1. Declare the observable unambiguously. Prefer the *causal cross-layer cascade* definition (option 3) over any attention-pattern scalar. Under option 3 this becomes "circuit-seeded residual-stream avalanche statistics", and Candidate 8 is genuinely distinct from Candidate 6 and Candidate 10.
2. If the proposer insists on attention-pattern scalars, fold this into Candidate 6 as a head-resolved extension and do not run it as a standalone project.
3. Engage arXiv 2510.05554 and arXiv 2604.16431 explicitly in the related-work section; update the `lit_ml.md §9 gap` statement to reflect that avalanche observables on transformers are now partially documented, and narrow the novelty to circuit-granularity residual-stream propagation.
4. Replace the layer-matched control with an attention-entropy-matched or induction-score-matched control, and add a sparsity-matched Bernoulli null (per `lit_ml.md §7`).
5. Tighten the pre-registered kill to: "induction-head causal-cascade exponents within 0.1 of the sparsity-matched null exponent, with threshold plateau across [θ/2, 2θ], kills the circuit-specific-criticality claim". 
6. Fix the Olsson citation ID to 3024.

Promote only after the proposer returns a revised one-pager reflecting (1)–(6). Otherwise, KILL as a standalone project and merge into Candidate 6.

---

*Word count: ~1 470.*
