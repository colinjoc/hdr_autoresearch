# Phase -0.5 Scope-Check - Candidate 32

**Candidate.** Quantization damage detectable via σ-shift.
**Question.** Does int8 / int4 quantisation measurably shift σ relative to fp16? Can Δσ distinguish AWQ / GPTQ / SmoothQuant recipes for LLaMA-2-7B, Mistral-7B, Gemma-2-2B?
**Observable (as written).** Δσ = σ(fp16) − σ(int8) − σ(int4) via MR-estimator on matched prompt set.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME — downgrade to a 1-week Paper-5 appendix / robustness row, not a standalone deployment-short.**
The core quantity *is* measurable on a 3060 (for the 2B fp16 anchor at least), but (i) the adjacent 2024-2026 quantisation literature already characterises what Δσ will pick up via outlier / massive-activation statistics; (ii) the 3060 memory budget forbids fp16 on any 7B model, which breaks the headline fp16-anchor design; (iii) the quantisation recipes are *explicitly* distribution-reshaping, so Δσ is algebraically confounded with the recipe's by-design intervention on the tail; and (iv) the practical impact pitch is weaker than the candidate claims — quantisation practitioners already monitor outlier-channel kurtosis and perplexity-vs-bitwidth curves. Standalone P ≈ 2 (workshop toy). Reframed as a Paper-5 robustness row it is P ≈ 4 and earns its keep as a *confound-quantification* companion to any int4-labelled exponent in the scale atlas.

## 2. Prior art on activation-statistics observables under quantisation

The candidate's novelty claim ("no work evaluates quantisation via activation-criticality drift") is narrow-true but broad-false.

- **LLM.int8() Dettmers 2208.07339** and **SmoothQuant Xiao 2211.10438** center on activation *outlier* channels — magnitudes 20-100× bulk — precisely the tail that powers σ on thresholded events.
- **GPTQ 2210.17323** and **AWQ 2306.00978** each motivate from activation-magnitude / salience statistics. AWQ's "activation-aware" name *is* the observable.
- **Massive Activations Sun 2402.17762** characterises 10³-10⁴× residual-stream peaks critical for attention sinks. **Hidden Dynamics 2508.03616** traces their emergence through training.
- **QuaRot 2404.00456 / SpinQuant 2405.16406** rotate the residual stream to flatten outliers *before* quantisation — the same heavy-tailed distribution σ would measure.
- **Evaluating Quantized LLMs 2402.18158** benchmarks W4A16 / W8A8 / smooth variants on 5 capability axes beyond perplexity.
- **BERT Busters 2105.06990** and **Outlier-Weighed Sparsity 2310.05175** — outlier magnitudes drive pruning and quantisation sensitivity.

**Net.** Δσ is a specific statistic in a dense landscape. Outlier-kurtosis, massive-activation magnitude ratios, and SmoothQuant's migration-strength α are adjacent summaries of the same tail. Novelty survives only if (a) Δσ adds information beyond those metrics, (b) Δσ correlates with downstream quality when kurtosis / perplexity-delta do not, or (c) MR-σ resolves a recipe-ordering outlier-counts cannot. Absent one of those, this is a restatement in criticality vocabulary.

## 3. Feasibility on 12 GB RTX 3060

| Model | fp16 | int8 (bnb LLM.int8) | int4 (AWQ/GPTQ) | Cache | Verdict |
|---|---:|---:|---:|---:|---|
| Gemma-2-2B | ~5.0 GB | ~2.5 | ~1.4 | ~1.2 | **fp16 primary**, all three recipes fit |
| LLaMA-2-7B | ~13.5 | ~6.8 | ~3.8 | ~2-3 | **int8 / int4 only**; fp16 does not fit |
| Mistral-7B-v0.1 | ~14 | ~7 | ~4 | ~2-3 | **int8 / int4 only**; fp16 does not fit |

User's scoping is correct: **fp16 unavailable for the 7B models on a 3060.** Consequences:

- Δσ = σ(fp16) − σ(int8) − σ(int4) is undefined for LLaMA-2-7B and Mistral-7B; design reduces to σ(int8) vs σ(int4) only.
- Gemma-2-2B is the only model that supports the three-way fp16 / int8 / int4 comparison. A single-model, single-family result is a case study, not an evaluation of "recipes".
- CPU-offload fp16 at 7B (~30h/pass per promoted.md §139) breaks the ≥10⁵-token MR-estimator throughput budget.

**Rescue.** Promote Gemma-2-2B to primary fp16 anchor and add sub-2B families (Pythia-1.4B at 2.8 GB, Qwen2.5-1.5B, TinyLlama-1.1B, SmolLM2-1.7B — all have community AWQ / GPTQ quants) for matched 3×3 cells. Retain LLaMA-2-7B and Mistral-7B only as int8/int4-only appendix rows, fp16 column explicitly `unavailable`.

## 4. Central confound: recipes reshape the distribution by design

This is the candidate's fatal-as-written weakness and must become the paper's core methodological contribution.

- **SmoothQuant** migrates activation magnitudes into weights via per-channel `s_j = max(|X_j|)^α / max(|W_j|)^(1-α)`; *purpose* is to flatten the activation tail. σ on smoothed activations reads the intended intervention, not a side effect.
- **AWQ** preserves top-1% salient channels in fp16, quantises the rest. Outlier-driven events above threshold are protected; bulk events perturbed. Δσ(AWQ vs fp16) will be small at outlier thresholds, larger at bulk — a predictable threshold-dependent signature, not a quality signal.
- **GPTQ** is weight-only (W4A16). The activation distribution is closer to fp16 than any W+A method. σ(GPTQ) should track σ(fp16) tightly. The candidate's design does not separate W-only vs W+A recipes.
- **QuaRot / SpinQuant** rotate the residual stream — a unitary reparameterisation of the basis σ is computed on. knowledge_base.md §3.1 mandates dual-basis reporting for exactly this case.

**Consequence.** Δσ has three components: (i) genuine dynamical change from precision loss, (ii) intended reshaping (SmoothQuant migration, AWQ protection, QuaRot rotation), (iii) basis-dependence of the threshold event. Candidate assumes only (i); (ii)+(iii) dominate at int8. Without percentile-thresholds co-computed per recipe, or a rotation-equivariant observable (spectral radius), the result is a recipe fingerprint not a damage measurement.

**Required controls.** (1) Percentile thresholds per activation tensor so event-counts are equated across recipes. (2) Dual basis — raw-neuron + rotation-invariant (Jacobian spectral radius, or Gemma-Scope SAE features for the 2B anchor). (3) W-only vs W+A axis (GPTQ vs SmoothQuant), not pooled "int8". (4) **Perplexity-matched pairing**: match WikiText-103 perplexity ±0.1 nats, then ask whether σ separates recipes perplexity cannot. Control (4) is where the deployment-diagnostic claim lives or dies.

## 5. Falsifiability revised

Candidate kill (|Δσ| < 0.05) is too loose vs knowledge_base §5 noise (σ = 1 ± 0.02). It passes trivially for AWQ (outlier-preserving) and fails trivially for SmoothQuant (bulk-reshaping) — pre-ordained by recipe design.

**Revised pre-registered tests.**

- **Primary.** On Gemma-2-2B fp16 anchor + 3-recipe × 2-bitwidth quantised set: is there a (r₁, r₂) pair with identical WikiText-103 perplexity (±0.1 nats) where MR-σ differs by > 3× within-recipe bootstrap SD? If yes, σ carries orthogonal information; if no, σ restates perplexity.
- **Secondary.** Does Δσ rank-correlate with downstream drop on a 5-task panel (MMLU, ARC-c, HellaSwag, TruthfulQA-MC, GSM8K) *after controlling for perplexity*? Spearman |ρ| > 0.3, p < 0.05 is publishable.
- **Basis check.** Does Δσ flip sign between raw-neuron and SAE-feature basis (Gemma Scope)? If yes, basis-dependence is the headline and the ranking claim dies.
- **Recipe family.** Does σ separate W-only (GPTQ) from W+A (SmoothQuant, bnb-LLM.int8) at matched bitwidth? If yes, σ specifically tracks the activation-intervention axis — a useful narrower claim.

## 6. Practical impact + merge recommendation

As written: **workshop toy**. Deployment community already has perplexity-vs-bitwidth curves, outlier-kurtosis monitors, capability panels. A single scalar σ does not beat those.

Reframed (§5 tests pass): **TMLR / MLSys workshop** — a criticality-flavoured deployment diagnostic. Not an MLSys short-paper main track. Value: one cheap activation-statistic pass for recipe ordering at matched perplexity.

**Fold into Paper 5 (scale atlas) as int-precision robustness §N.** Paper 5 must already caveat int8-forced rows (LLaMA-2-7B, Pythia-6.9B+) with a quantisation-confound label (promoted.md §139). C32's contribution — *how much does the caveat shift σ?* — is exactly the quantification that caveat needs. +1 week to Paper 5; removes the "int8 confound is qualitative" weakness. Promote standalone only if §5 primary + secondary both land on the 2B anchor plus ≥2 sub-2B families.

## 7. Action items

1. Fix candidate_ideas.md C32 observable: percentile-threshold Δσ + Jacobian spectral radius + perplexity-matched pairing; state fp16 unavailable on 7B for 12 GB cards.
2. Swap model list: Gemma-2-2B primary; add Pythia-1.4B + TinyLlama-1.1B + Qwen2.5-1.5B sub-2B anchors; LLaMA-2-7B / Mistral-7B as int8/int4-only appendix.
3. Separate W-only (GPTQ, AWQ) from W+A (SmoothQuant, bnb-LLM.int8) recipes; four distinct interventions, not pooled "int8".
4. Add to papers.csv: Dettmers 2208.07339, Xiao SmoothQuant 2211.10438, Frantar GPTQ 2210.17323, Lin AWQ 2306.00978, Sun Massive-Activations 2402.17762, Li Eval-Quant-LLM 2402.18158, QuaRot 2404.00456, SpinQuant 2405.16406, BERT-Busters 2105.06990, Outlier-Weighed-Sparsity 2310.05175, Hidden-Dynamics 2508.03616.
5. Move C32 in promoted.md from "Deployment-short" to "Paper 5 §N (int-precision robustness)"; +1 week to Paper 5. Promote standalone only if §5 (a)-(c) land on the 2B anchor.

## 8. Rubric

- **D (data availability)** = 5 (all checkpoints public: Gemma-2-2B + AWQ/GPTQ/SmoothQuant community quants; WikiText-103 / Pile for prompts).
- **N (novelty)** = 2 standalone after prior-art audit / 3 as Paper-5 section (first activation-criticality quantification of the int4/int8 confound in a scale atlas).
- **F (falsifiability)** = 2 as written (one-scalar, confounded) / 4 after §5 revision (perplexity-matched pairing + basis check + W-only vs W+A axis).
- **C (cost)** = 5 as Paper-5 arm (~1 week) / 3 standalone (~3 weeks once sub-2B families added).
- **P (practical impact)** = 2 as written / 4 reframed — and only if §5 (a)-(c) land.

**Composite.** PROCEED as Paper-5 §N. Do not promote standalone until the §5 tests pass on the 2B anchor. Kill-as-standalone on any of: (i) Δσ fully explained by perplexity-delta, (ii) sign reverses between raw-neuron and SAE basis, (iii) Δσ(GPTQ vs SmoothQuant) is within-seed noise.
