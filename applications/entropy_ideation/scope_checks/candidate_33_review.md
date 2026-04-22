# Phase -0.5 Scope-Check - Candidate 33

**Title.** Distillation preservation of σ - does knowledge distillation preserve the teacher's branching ratio in the student?
**Proposed observables.** σ(teacher) vs σ(student) for public distilled pairs: DistilBERT / BERT-base, DistilGPT-2 / GPT-2-small, TinyLLaMA / LLaMA-7B, Gemma-2-2B / Gemma-2 larger-teacher.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME, PROCEED as a ~10-day sub-study merged into Paper 3 (post-training axis, alongside C21 and C32), not a standalone short paper.** The observation gap is real - no 2024-2026 paper reports MR branching ratio or avalanche exponents on a distilled teacher-student pair - but the candidate's pair list is methodologically broken: TinyLLaMA is not distilled from LLaMA-7B (independently pretrained), Gemma-2-2B's teacher weights are not public, and DistilBERT/DistilGPT-2 carry confounds (layer-deletion init, cosine-embedding hidden-state alignment). The usable pair set reduces to DistilBERT/BERT-base and DistilGPT-2/GPT-2-small, optionally plus a self-run Pythia-410M -> Pythia-160M distillation as a third protocol-controlled pair.

## 2. Pair-matching audit: are the named pairs actually comparable?

The candidate's framing "every deployed distilled model is systematically sub-critical" requires pairs that share training data, objective and tokenizer up to the distillation signal. The four named pairs vary wildly.

| Pair | Same data? | Same tokenizer? | Distillation type | Usable? |
|---|---|---|---|---|
| DistilBERT / BERT-base | Yes (BookCorpus + Wikipedia) | Yes | KL(soft logits) + MLM + cosine-embedding(hidden states); student init'd by copying every-other BERT layer | Partial |
| DistilGPT-2 / GPT-2-small | Yes (OpenWebTextCorpus ≈ WebText) | Yes (GPT-2 BPE) | Same Sanh-2019 triple loss; halved depth | Partial |
| TinyLLaMA / LLaMA-7B | **No** - TinyLLaMA pretrained from scratch on 3T tokens of SlimPajama + StarCoder | Yes (Llama tokenizer) | **Not distilled.** Pretraining-from-scratch with Llama *architecture*; third-party BabyLlama-style distillations exist but are not the canonical checkpoint | **No - mis-labelled** |
| Gemma-2-2B / Gemma-2-"teacher" | Unknown; Gemma 2 tech report (arXiv:2408.00118) states 2B and 9B distilled from an undisclosed larger model; Gemma 3 tech report (arXiv:2503.19786) uses a Gemini-class teacher | Yes | KL over top-K=256 logits; on-policy for SFT | **No - teacher weights unavailable** |

**Consequence.** Two of the four named pairs are unusable. "TinyLLaMA / LLaMA-7B" must be struck - any positive result is explained by "different data", any negative result is uninformative.

**Sanh-2019 cosine-embedding confound.** DistilBERT and DistilGPT-2 are trained with an explicit cosine-distance loss aligning student and teacher hidden-state directions. That is exactly the distribution the σ pipeline probes. A positive "σ preserved" result is therefore partly tautological; the *informative* outcome is the negative one (direction-alignment insufficient to preserve critical dynamics). Pre-register this asymmetry.

**Layer-init confound.** DistilBERT's student is initialised by copying every-other BERT layer. σ preservation could therefore be weight-inheritance, not distillation signal. Control: measure σ on the layer-init-only checkpoint before distillation training (one extra inference run, no extra training).

## 3. Has 2024-2026 literature evaluated distillation via activation observables?

**Direct criticality observables on distilled pairs: no.** Neither arXiv searches for "distillation activation preservation" / "student teacher activation statistics" / "distillation branching ratio criticality" nor the 209-paper corpus (`papers.csv`, `papers_ml.csv`, `papers_round2.csv`) return any distillation/criticality paper.

**Adjacent work that must be cited.**

- arXiv:2510.16968 (Oct 2025) "Leave It to the Experts: Detecting Knowledge Distillation" - argues distillation transfers "structural habits" (internal computational patterns), not just input/output mapping. Closest 2025 work; observable is representational similarity, not avalanches. σ is complementary.
- ACL 2025 long paper "Beyond Logits: Aligning Feature Dynamics for Effective Distillation" - explicitly about dynamics preservation, though not criticality.
- arXiv:2502.08606 (Feb 2025) "Distillation Scaling Laws" - token-efficiency relationships; defines the published baseline for "matched-accuracy".
- OpenReview "Improving Language Model Distillation through Hidden State Matching" - CKA-based hidden-state alignment; characterises what standard distillation does *and* does not preserve in hidden-state geometry.
- Gemma 3 tech report (arXiv:2503.19786) - K=256 on-policy logit distillation; teacher weights not public.

The gap is real but narrow. Frame the contribution as: "distillation preserves representational geometry (2024-25 literature); we test whether it preserves *critical dynamics* (new physics observable)".

## 4. Falsifiability: is "distillation destroys criticality" well-posed?

The candidate's kill condition "σ(teacher) = σ(student) within CI" is under-specified on three axes.

1. **Matched-accuracy frontier.** Δσ must be reported at matched held-out perplexity, not nominal checkpoint. DistilBERT retains 97% of GLUE at 40% of parameters; DistilGPT-2 perplexity 21.1 vs GPT-2 16.3 on WikiText-103. The useful number is Δσ referenced against Paper 5's σ(params) scale-law curve at the student's parameter count - a *residual*, not a teacher-minus-student difference.
2. **Fraction of |σ-1| preserved.** Pre-register three levels: ≥90% preservation (σ-transparent), 50-90% (partial), <50% (criticality-destroying). Three-level kill, not binary.
3. **Direction.** σ(student) < σ(teacher) vs σ(student) > σ(teacher) are qualitatively different claims (sub- vs super-critical). The candidate assumes sub-critical without justification. Report signed Δσ.

Suggested pre-registered kill: **|σ(teacher) - σ(student)| / |σ(teacher) - 1| < 0.2 across ≥2 usable pairs at matched perplexity** -> σ-transparent; **signed |ratio| > 0.5 in a consistent direction across ≥2 pairs** -> distillation-shifts-σ with direction as headline; otherwise pair-dependent.

## 5. Practical venue

Standalone MLSys / ENLSP workshop paper (the candidate's own suggestion) is weak - single observable, single axis, partly tautological for the Sanh pairs. Stronger options, in order:

- **Bundled into Paper 3 (post-training axis)** with C21 (base vs SFT/RLHF), C32 (quantisation), and optionally C30 (pruning): "Post-training modifications shift σ: a criticality audit". TMLR-length, unified observable, five axes. Recommended.
- **Appendix of Paper 5 (scale atlas)**: distilled pairs as data points on or off the σ(params) scale-law curve. Cheaper alternative if Paper 3 is not pursued.
- **Standalone workshop spin-off** - only if Paper 3 already exists. Otherwise the bundled version strictly dominates.

Not a main-conference paper alone: that would require σ *and* a downstream capability consequence (e.g. σ-preserving distilled models transfer better), which is a larger study.

## 6. Cost feasibility on 12 GB RTX 3060

**Simultaneous LLaMA-7B teacher + TinyLLaMA student: no.** LLaMA-7B fp16 is ~13.5 GB, exceeding the 12 GB frame buffer before any activation cache. Options if LLaMA-class pairs were retained:

- **Sequential loading** - teacher σ pipeline runs first, residual-stream activations cached to disk (~2 GB/checkpoint for 10^5 tokens × 32 layers × 4096 dim bf16), teacher unloaded, student loaded, student σ pipeline runs, comparison offline. This is the required mode regardless.
- **int8 weights, fp16 activations** - LLaMA-7B in bitsandbytes int8 is ~6.8 GB, leaves ~4-5 GB for activations. Inherits the int8-confound documented in the Candidate 21 review §2 (outlier-aware rounding biases tail exponent α and perturbs the autocorrelation the MR σ estimator consumes). If used, label the row "int8-confounded".

**With TinyLLaMA struck (§2) the question is moot.** The retained pairs fit comfortably in fp16 on 12 GB: BERT-base (440 MB), DistilBERT (265 MB), GPT-2-small (500 MB), DistilGPT-2 (330 MB), plus Pythia-410M/160M (~1 GB total) as a control pair.

**Budget:** activation extraction (2-3 pairs × 10^5 tokens × ~6 h) + MR σ fits + avalanche exponents + at-init + layer-init-only controls + two-basis reporting: ~8-10 GPU-days = ~1.5 weeks. If the Pythia distillation is self-run, add ~3 days training the 160M student on a 10B-token subset.

## 7. Pre-registered kill and controls

Across the usable pairs (DistilBERT/BERT, DistilGPT-2/GPT-2, optional Pythia-410M-distilled/160M):

- |Δσ_residual| < 0.03 at matched perplexity with α, β overlapping within CI -> **σ-transparent distillation**. Null result; workshop-publishable, framed as constraint on "distillation destroys criticality" hypothesis.
- Δσ > 0.05 signed-consistent across ≥2 pairs and larger than Paper 5 scale-law residual -> **distillation shifts σ**. Direction + magnitude become headline.
- Pair-dependent -> **architecture-/corpus-dependent effect**; report as such, no universal claim.

Required controls beyond the candidate's list:

1. **Layer-init-only control** for DistilBERT (σ on the every-other-BERT-layer checkpoint before distillation training).
2. **Sanh-2019 cosine-embedding asymmetry** explicitly labelled - positive result partly tautological.
3. **Scale-law anchor**: Δσ referenced to Paper 5's σ(params) curve at student parameter count, not to teacher.
4. **At-init σ** for every student architecture (per `knowledge_base.md` §5.7).
5. **Two-basis requirement** (raw-neuron + SAE-feature where available, per `knowledge_base.md` §3.3).
6. **Pre-Phase-0 reachability check** on all HF checkpoints (per `feedback_verify_data_access_before_phase_0` memory).

## 8. Action items

1. **Strike "TinyLLaMA / LLaMA-7B" from `candidate_ideas.md` line 658**; it is not a distilled pair.
2. **Strike or caveat "Gemma-2-2B / Gemma-2-teacher"**; teacher weights unavailable. If retained, note only the student can be measured (no pair comparison).
3. Optionally add **Pythia-410M -> Pythia-160M** as a third, protocol-controlled distillation pair (~3 days extra training).
4. Reframe kill from binary to three-level (≥90% / 50-90% / <50% preservation of |σ-1|) with signed Δσ against the Paper 5 scale-law residual.
5. **Merge into Paper 3 (post-training axis)** alongside C21 and C32. Do not promote as standalone.
6. Verify HF availability of all retained checkpoints before Phase 0.

**Rubric.** D = 4 (HF public weights for retained pairs). N = 2 standalone / N = 4 as Paper-3 arm. F = 3 (three-level kill + at-init + layer-init-only + scale-law anchor). C = 3 standalone after corrected pair list / C = 4 as Paper-3 arm (pipeline reuse). P = 1 standalone workshop / P = 3-4 as Paper-3 arm (TMLR).

**Composite:** **REFRAME-and-MERGE** into Paper 3 post-training axis. Standalone promotion not recommended.
