---
title: "Activation avalanches in a trained transformer: a negative result on mean-field criticality"
date: 2026-04-22
domain: "Machine Learning"
blurb: "Neuroscience says biological cortex sits at a critical point where neural activity avalanches have a specific mathematical signature. We tested whether a trained GPT-2 does the same on natural text. It doesn't. But training leaves two other structural fingerprints that random-init weights don't."
weight: 38
tags: ["deep-learning", "criticality", "self-organized-criticality", "transformer", "negative-result", "methodology"]
---

*A plain-language summary. The [full technical paper](https://github.com/colinjoc/hdr_autoresearch/blob/master/applications/entropy_avalanches/paper_submission.md) has the complete methods and results. See [About HDR](/hdr/) for how this work was produced.*

**Bottom line.** The critical-brain hypothesis says biological cortex self-organises at a phase transition where neural activity propagates in power-law-distributed "avalanches" with a signature exponent α ≈ 3/2. Similar claims have been made, increasingly, for trained neural networks. We applied the full six-element statistical-physics battery that neuroscientists use on cortex to the activations of pretrained GPT-2-small on natural text, with a matched random-weight control. Every criticality predicate fails: α is nowhere near 3/2, the Sethna crackling-noise scaling relation does not close, threshold plateau fails, and lognormal is strongly preferred over power-law at every layer. Training does, however, produce two depth-graded structural signatures — a layer-dependent branching ratio and a layer-dependent participation ratio — that sharply distinguish trained from random-weight networks and align with a layer-specialisation picture rather than a universal criticality picture.

## The question

Biological cortex has a robust signature in its electrical activity: neurons fire in cascades whose size distribution follows a power law P(s) ∝ s^{-α} with α ≈ 3/2, and durations follow P(T) ∝ T^{-β} with β ≈ 2. When you measure both exponents independently and plug them into the Sethna scaling relation γ = (β − 1)/(α − 1), you get γ ≈ 2 — and when you measure γ directly, it agrees. The branching ratio σ (the average number of spikes one spike triggers) sits at σ ≈ 1 in cortex slice or slightly below it (σ ≈ 0.98) in awake animals. This combination is what makes neuroscientists say "cortex is critical". Whether trained deep neural networks satisfy the same combination has been conjectured in recent literature. We wanted to know if a pretrained transformer language model on natural text does.

## What we found

![Figure 1. MR branching ratio σ by layer for trained GPT-2-small (blue) vs a matched-init random-weight control (red) at z-score threshold θ = 2.5 on the ambient residual-stream basis. Reference lines: σ = 1 is the critical branching ratio; σ = 0.98 is the "reverberating regime" found in awake-mouse cortex by Ma et al. 2019.](plots/fig1_sigma_vs_layer.png)

**Criticality predicates all fail on trained GPT-2.** Across 12 layers × 3 z-score thresholds × 3 bases × 2 conditions (216 cells total), the avalanche-size exponent α ranges 2.02 to 3.00 — nowhere near the mean-field 3/2 prediction. There is exactly one near-miss in the entire grid: layer 11 at threshold θ = 3.0 returns α = 1.69, but that same layer at θ = 2.5 jumps to α = 2.89 — a 1.2-unit drift across a 0.5-σ threshold change, failing the threshold-plateau criterion that any real critical exponent is supposed to satisfy. The Sethna γ scaling relation is nowhere close: predicted γ ranges 0.79 to 1.12 across layers where the mean-field prediction is γ = 2. And the Vuong likelihood-ratio test strongly prefers lognormal over power-law at every single layer (p < 0.01 all 12). None of our supporting evidence bars clears either: the temporal-shuffle null-rejection test does not cleanly reject the null on most layers (shuffled α is within 0.35 of real α where both can be fit), basis-invariance fails at our pre-registered ±0.3 tolerance (realised ±0.5). The picture is not "transformer activations are at criticality with caveats" — it is that they are not critical on this model and corpus.

![Figure 2. Avalanche-size exponent α at layer 6 versus z-score threshold θ for trained vs random-init. The α values drift by about 0.9 units across the tested threshold range on trained GPT-2 — the threshold plateau that any genuine critical exponent should satisfy is not satisfied.](plots/fig2_alpha_vs_threshold.png)

**But training leaves a sharp, distinctive fingerprint.** Figure 1 shows the MR branching ratio σ by layer for trained GPT-2 vs a matched-init random-weight control. The random-init control is almost flat at σ ≈ 0.94–0.96 across all 12 layers — precisely what you'd expect for an isotropic random network. The trained network, by contrast, shows a striking layer-depth gradient: early layers 0–2 sit at σ ≈ 1.08 (slightly super-critical), layer 5 collapses to σ = 0.30, middle-late layers 6–9 drift around σ ≈ 0.66–0.80, and the final layers recover to σ ≈ 0.92–0.95. Training *introduces* this structure; it is not present at initialisation.

![Figure 3. Scatter of subspace σ (top-K PCA reconstructed scalar, following Fontenele 2024) vs ambient σ per layer for trained and random-init GPT-2.](plots/fig3_subspace_vs_ambient.png)

**A second, complementary fingerprint.** Participation ratio — a measure of how many effective dimensions the activations span, out of the 768-dimensional residual-stream space — tells the same story in different terms. Trained layers 1–5 operate in a PR ≈ 1–8 subspace, essentially collapsed to one or a handful of shared directions. Middle layers 6–9 expand back to near-isotropic (PR ≈ 46–140). Final layers re-compress. The random-init control is uniformly PR ≈ 80 across all 12 layers. Training creates representational bottlenecks at early layers and recovers high-dimensional variance at middle layers, while random initialisation leaves the whole residual stream isotropic.

## Why that matters

The "deep networks are at criticality" idea is appealing — it would link machine learning to statistical physics in a tidy way. But when you apply the actual statistical-physics tests that physicists have developed for exactly this question, they don't support the idea on at least this canonical trained language model. Single-number reports of α ≈ 3/2 in the neural-network literature should be read with caution: the Vuong likelihood-ratio test against lognormal, and the threshold-plateau test, routinely kill apparent power-laws that would look convincing on a single log-log plot.

The positive findings — the depth-graded σ and PR — are arguably more interesting anyway. They're a quantitative summary of what deep-learning practitioners have long suspected: early layers of trained transformers compute shared positional and lexical features that collapse many neurons onto one effective axis; middle layers expand back to high-dimensional conceptual representations; final layers re-compress to read out predictions. These structures are created by training, not present at initialisation, and they appear in a matched random-weight control with striking clarity.

## What it means in practice

**For researchers claiming deep networks are "at the edge of chaos".** Our threshold-plateau test fails by a wide margin. Any criticality claim on trained-network activations that reports α at a single z-score threshold should be read as weak evidence. A reasonable minimum methodological bar is to report α over at least a 1-σ range of thresholds plus the Vuong lognormal-rejection p-value.

**For mechanistic interpretability.** The layer-graded σ and PR gradients are candidate diagnostics for layer specialisation. A sharp σ or PR transition between layers is a bulk-statistical marker of a representational change and could complement circuit-level analyses.

**For the broader critical-brain-hypothesis programme.** Cortex may or may not be critical; that's a separate empirical question. What our work shows is that the analogy between cortex and trained LLMs is narrower than it might sound — at least for the multi-predicate statistical-physics signature that cortex papers use.

## How we did it

We loaded pretrained GPT-2-small (124M parameters) and a matched-init random-weight control (constructed via `AutoModelForCausalLM.from_config` to preserve LayerNorm initialisation). We streamed 1 000 documents from the C4 English corpus, truncated to 64 tokens each, and cached the output of each block's MLP sub-module (not the residual stream, which would create a tautology). We z-scored each neuron's activations across valid tokens, thresholded at θ ∈ {2.0, 2.5, 3.0} σ-units, detected avalanches as contiguous supra-threshold runs, and applied the Clauset-Shalizi-Newman power-law fit, the MR-estimator branching ratio, the Sethna γ scaling-relation cross-check, a temporal-shuffle null, and a PCA-based subspace σ. SVD is accelerated on CUDA; everything else runs on CPU with the standard `powerlaw` and `mrestimator` Python packages.

The reference implementation, 216-row result table, and three figures are in the [project repository](https://github.com/colinjoc/hdr_autoresearch/tree/master/applications/entropy_avalanches). The paper is prepared for submission to *Entropy* / NeurIPS MechInterp workshop / TMLR.

## What's next

The obvious follow-ups are to scale the test to larger models (Pythia 70M through 2.8B, Gemma-2-2B), to add the sparse-autoencoder-basis invariance check (using an open-source GPT-2 SAE release such as `gpt2-small-res-jb`), and to run the full Griffiths-phase null-rejection battery beyond the simple temporal-shuffle null we used. Whether the depth-graded σ and PR gradients are a universal feature of trained LLMs or specific to GPT-2-small is the most interesting of these open questions.
