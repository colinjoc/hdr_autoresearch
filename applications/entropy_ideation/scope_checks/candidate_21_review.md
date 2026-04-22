# Phase -0.5 Scope-Check - Candidate 21

**Title.** Pretrained vs instruction-tuned - does RLHF / SFT shift σ away from 1 toward sub-critical?
**Proposed observables.** σ(base) vs σ(SFT) vs σ(RLHF) for matched pairs: LLaMA-2-7B base/chat, Gemma-2-2B / 2-2B-it, Pythia-1.4B / Pythia-1.4B-instruct.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME, then MERGE as Paper 5 §N (post-training axis).** Stand-alone novelty is thin: Gemma Scope 2 (DeepMind, Dec 2025) already released base-vs-IT SAE comparisons, and Lin 2024 (arXiv:2312.01552) and Zhou 2023 LIMA already measure token-distribution shift. The useful residual claim is "first MR-branching-ratio + crackling-noise audit of base / SFT / RLHF pipeline on open-weight pairs" - a ~1-week delta on Paper 5 (scale atlas), not a separate paper. The σ-only observable is too narrow; the one-sided "-> sub-critical" framing is a guess not a prediction; and the Pythia-1.4B-instruct model named in the candidate does not exist.

## 2. Feasibility on a 12 GB RTX 3060

Weights + residual-stream activation cache (~10^5 tokens × L layers × d_model in bf16):

| Pair | fp16 weights | int8 | Cache peak | Verdict |
|---|---:|---:|---:|---|
| Pythia-1.4B / SFT variant | 2.8 GB | 1.4 | ~0.7 | fp16 comfortable |
| Gemma-2-2B / 2-2B-it | 5.0 | 2.5 | ~1.2 | fp16 comfortable |
| LLaMA-2-7B base / chat | 13.5 | 6.8 | ~2-3 | **int8 only**, tight |

**int8 as σ-confound.** Outlier-aware int8 (bitsandbytes LLM.int8(), SmoothQuant, GPTQ) preserves outlier channels in fp16 and rounds the bulk. Consequences for criticality:

- α is fit on the tail. int8 compresses the bulk while preserving the tail, *biasing α downward* (heavier apparent tail) by a scheme-dependent amount. Not cosmetic.
- σ via MR is sensitive to activation autocorrelation; cumulative int8 rounding over 32 layers perturbs autocorrelation at ≈10^-3 per op - probably below the 0.02 bar in `knowledge_base.md` §5.5 but worth reporting.
- Gemma Scope 2 reports elevated FVU on IT activations concentrated in stylistic-token directions. A quantiser that re-weights outlier channels vs bulk will shift stylistic-direction contributions asymmetrically between base and chat, producing *artefactual* Δσ.

**Rule:** run LLaMA-2-7B only if (a) base and chat use identical quantisation scheme, (b) the LLaMA row is labelled `int8-confounded`, (c) fp16 Gemma + Pythia pairs anchor the primary result. Recommended: demote LLaMA-2-7B to an appendix robustness row.

## 3. Matched base vs post-trained weights - what actually exists

The candidate's model list is partly wrong.

- **Gemma-2-2B** (`google/gemma-2-2b`) vs **Gemma-2-2B-it** (`google/gemma-2-2b-it`). SFT + RLHF; both covered by Gemma Scope. **Cleanest fp16 pair.**
- **LLaMA-2-7B** (`meta-llama/Llama-2-7b-hf`) vs **-chat-hf**. SFT + RLHF; gated but public. int8 only, with confound caveat.
- **Pythia-1.4B-instruct does not exist.** EleutherAI released no official instruct variant at 1.4B. Community options: `lambdalabs/pythia-1.4b-deduped-synthetic-instruct` (SFT on Dahoas/synthetic-instruct, matches `EleutherAI/pythia-1.4b-deduped`) - closest matched pair, but SFT-only, non-standard data. Pythia-Chat-Base-7B and OpenAssistant oasst-sft-*-pythia-12b are larger than card budget. `allenai/open-instruct-pythia-6.9b-tulu` is int8-only.

Fix candidate text: swap "Pythia-1.4B-instruct" -> `lambdalabs/pythia-1.4b-deduped-synthetic-instruct`, flag SFT-only. This splits the design cleanly:

- **Gemma pair** tests SFT+RLHF combined (the full pipeline).
- **Pythia-1.4B pair** tests SFT only.
- Together they isolate the marginal effect of RLHF on top of SFT - something the candidate as written cannot do because it conflates "instruction-tuned" with "RLHF-tuned".

## 4. Novelty vs 2024-2026 literature

Adjacent prior art not yet in `papers.csv`:

- **Lin et al. 2024 ICLR, arXiv:2312.01552 "The Unlocking Spell on Base LLMs"** (URIAL / AlignTDS). Base and aligned models share top-1 tokens on >90% of positions; shift is concentrated on stylistic tokens (discourse markers, safety disclaimers). If logits are near-identical on content tokens, upstream residual-stream statistics likely are too; any Δσ will localise on stylistic-token positions. A token-averaged σ dilutes the signal.
- **Zhou et al. 2023 LIMA (arXiv:2305.11206)** - superficial-alignment hypothesis. Predicts small Δσ if σ tracks capability (which LIMA says is ~unchanged).
- **Superficial Safety Alignment Hypothesis (arXiv:2410.10862)** - localised, not global, safety-alignment change.
- **Lieberum 2024 Gemma Scope (2408.05147)** + **Gemma Scope 2 technical paper (Dec 2025)**. Fig 17 / base-vs-IT FVU analysis is the nearest published comparison of base vs IT activation structure - SAE-reconstruction-faithfulness, not criticality, so genuine gap remains.
- **"The Price of Format: Diversity Collapse in LLMs" (arXiv:2505.18949)** and mode-collapse literature - RLHF < SFT < base in output diversity. Open question is whether this is late-layer / unembedding-only or reflects internal dynamics. Candidate 21 could address this if it reports *per-layer* σ_ℓ, not a scalar σ.
- **"Do Instruction-Tuned Models Always Perform Better?" (arXiv:2601.13244, Jan 2026)** - post-training capability shift is non-monotonic, sometimes negative. Makes a universal "post-training -> sub-critical" claim implausible.

No paper computes MR branching ratio or crackling-noise exponents on matched base-vs-post-trained pairs. The gap is real but narrow and inside a crowded region.

## 5. Is σ the right observable?

σ alone is too narrow. Broaden to four:

1. **Per-layer σ_ℓ profile** (not a scalar). Post-training concentrates in late layers (Nanda / Gemma Scope 2 / Lin 2024 stylistic-token localisation). Scalar-σ averaging will wash out the signal.
2. **Residual-stream spectral density** per layer - power-law spectral-decay exponent. Continuous analogue of σ, sidesteps MR subsampling bias. Jacobian spectral radius ρ (Paper 1 primary) reported alongside.
3. **SAE-feature χ² via Gemma Scope** - base-SAE reconstruction of IT activations, co-firing-cluster distribution comparison. Directly tests whether post-training changes critical-feature *identity* vs just re-weighting.
4. **Output-distribution Shannon entropy** per token. The observable the mode-collapse literature uses. Pairing with σ separates "internal-dynamics narrowing" (unknown) from "late-layer / unembedding narrowing" (known). If σ shifts but output-entropy doesn't -> internal change without output effect. If output-entropy shifts but σ doesn't -> unembedding-only effect.

Strongest Candidate 21: this four-observable panel × (base, SFT-only Pythia, SFT+RLHF Gemma) column.

## 6. Is the sub-critical direction theoretically motivated?

Only weakly. Three priors for "-> sub-critical":

- PPO-RLHF KL penalty caps policy divergence -> output entropy narrows -> *plausibly* σ narrows. But KL acts on output, not residual stream; link to σ not derived.
- Mode-collapse / diversity-loss literature (2505.18949) - output entropy drops. Assumes σ tracks output entropy, not established.
- Meisel 2013 sleep/wake biological prior - dampened dynamical range = sub-critical. Weak transfer.

Equally defensible priors for the opposite direction:

- Post-training sharpens circuits (Olsson, Wang IOI) -> stronger propagation -> σ *up*.
- Prakash-Martin 2025 HTSR (arXiv:2506.04434, on `promoted.md` missing-citations list) - RLHF models show *higher* Jacobian spectral radius, not lower. ρ up => σ up.
- Superficial-alignment hypothesis -> Δσ ≈ 0 on content tokens, sign indeterminate.

**Reframe as two-tailed.** Any of {no shift, sub-critical shift, super-critical shift} is publishable. One-tailed pre-registered kill in candidate_ideas.md is wrong for a sign-uncertain effect.

## 7. Pre-registered test (revised)

- **Primary (Gemma, fp16):** does σ_ℓ(base) differ from σ_ℓ(IT) at any layer beyond block-bootstrap 95% CI? Does Δσ_ℓ localise in late layers (L > 0.7·L_max)? Does it separate stylistic-token from content-token positions when stratified?
- **Narrative branches:**
  - No Δσ_ℓ at any layer + output-entropy(base) > output-entropy(IT): "post-training shifts output-distribution but not internal σ - evidence for late-layer / unembedding localisation" (confirms superficial-alignment at criticality level).
  - Uniform Δσ_ℓ across depth: "global σ shift" (contradicts superficial-alignment; sign and magnitude reported, not predicted).
  - Pythia-SFT and Gemma-IT (SFT+RLHF) same-sign Δσ, different magnitudes: RLHF amplifies SFT effect; opposite signs: RLHF partially reverses SFT.

All three are publishable; only the narrative changes.

## 8. Merge-vs-separate

**Merge as Paper 5 §N.** Paper 5 is a Pythia scale-ladder criticality atlas. Adding a training-regime axis (pretrain / SFT / RLHF) for available matched pairs fits the atlas narrative: criticality observables across (size, step, regime). Delta ~1 week on a ~4-week paper.

Standalone is a workshop paper at best, given Gemma Scope 2 / Lin 2024 / LIMA / diversity-collapse saturation of the adjacent space. Promote standalone only if the four-observable panel of §5 is adopted and Gemma is primary; otherwise merge.

## 9. Risks and mitigations

- int8 confound on LLaMA-2: demote to appendix; fp16 Gemma + Pythia are primary.
- Pythia-1.4B-instruct mis-identified: swap to `lambdalabs/...-synthetic-instruct`, label SFT-only.
- Single-scalar σ dilutes signal: per-layer profile + token-role stratification.
- Superficial-alignment predicts null: frame the null as a *positive* confirmation of Lin 2024 / Zhou 2023 at the activation-criticality level.
- Gemma Scope 2 scoop: position as complementary (criticality observables) to Gemma Scope 2's FVU comparison. Cite explicitly.

## 10. Summary

**Verdict.** REFRAME -> MERGE as §N of Paper 5 (post-training axis). Not standalone.
**Rubric.** D = 5 (public weights, modest compute); N = 2 standalone / 3 merged (first multi-observable criticality audit of pretrain/SFT/RLHF pipeline); F = 4 after four-observable two-tailed reframe, F = 2 as written; C = 5 (~1 week delta); P = 4 merged / 2 standalone.
**Actions.**
  1. Fix `candidate_ideas.md` C21: replace "Pythia-1.4B-instruct" with `lambdalabs/pythia-1.4b-deduped-synthetic-instruct`; flag SFT-only.
  2. Demote LLaMA-2-7B to appendix / int8-confound-labelled row.
  3. Broaden observable set to {σ_ℓ profile, residual-stream spectrum, SAE-feature χ² via Gemma Scope, output-distribution entropy}.
  4. Reframe hypothesis two-tailed: report direction and localisation.
  5. Fold into Paper 5 as training-regime §N; +1 week to Paper 5 budget.
  6. Append to `papers.csv`: Lin 2024 (2312.01552), Zhou 2023 LIMA (2305.11206), Gemma Scope 2 technical paper, "Price of Format" (2505.18949), "Do Instruction-Tuned..." (2601.13244), Superficial Safety Alignment (2410.10862).
  7. Update `promoted.md` C21 row: "REFRAME -> absorbed into Paper 5 §N (post-training axis)".
