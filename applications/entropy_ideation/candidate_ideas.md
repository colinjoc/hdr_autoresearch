# Candidate Research Ideas — Criticality in Trained Neural Networks

Twelve one-page proposals. Each declares observable, model, pre-registered kill condition, and novelty claim. Each is simulation-feasible on a single RTX 3060 12 GB. Cross-references into `literature_review.md` and `knowledge_base.md`.

Status tracking is in `promoted.md` after Phase −0.5 scope-checks.

---

## Candidate 1 — Activation-avalanche exponents in pretrained GPT-2

**Question.** Does a pretrained GPT-2 small / medium show power-law-distributed activation avalanches with α ≈ 3/2 on natural-text inputs?

**Observable.** Residual-stream activation avalanches across layers on Pile samples. Avalanche = contiguous supra-threshold activations traced across layers via causal paths (attention + MLP + residual). Measure P(s), P(T), shape-collapse, and scaling relation γ = (β − 1)/(α − 1).

**Why it's novel.** `lit_ml.md §Gap`: no published paper computes avalanche exponents on transformer activations. Closest adjacent work is on RNNs [3042: Torres 2023 VERIFY] and MLPs [3033: Testolin 2020] — neither transformers nor with the crackling-noise multi-exponent discipline.

**Method.** TransformerLens + powerlaw + mrestimator. Sweep activation thresholds θ ∈ {0, 0.1, 0.5, 95th percentile}. Sweep input distribution: Pile, code, math. At-init control: compare to randomly-initialised same-architecture model. Basis control: raw-neuron vs SAE feature (Gemma-Scope-style).

**Pre-registered kill.** If no basis-threshold combination yields ≥ 2 decades of power-law scaling with CSN p > 0.05 rejecting alternatives, report negative.

**Deliverable.** Single paper: first measurement of avalanche exponents on trained transformer language models. Either positive (α ≈ 3/2, consistent with mean-field criticality) or negative (off-critical) is publishable at NeurIPS / ICLR / ICML workshops or Entropy / Neural Computation.

**Cost.** ~2 weeks. No new training; all measurement on pretrained weights.

**Required controls.** At-init baseline; raw-neuron + SAE basis; threshold plateau; block-bootstrap; crackling-noise cross-check.

---

## Candidate 2 — Skip-connection topology sweep tunes distance-from-criticality

**Question.** As `n_skip_connections` varies across the existing nanoGPT sweep (0 → 1000), does the branching ratio σ and avalanche exponent α vary monotonically or non-monotonically? Is there a topology setting that places the network closest to σ = 1?

**Observable.** σ(n_skip) via MR estimator on layer-resolved activations. α(n_skip) via CSN on avalanche sizes. Task-performance (val loss) as a function of `|σ − 1|`.

**Why it's novel.** The sweep already exists on disk. No published paper uses continuous topology tuning to traverse a critical boundary in a trained transformer. The natural-experiment advantage: all other hyperparameters held fixed.

**Method.** Post-hoc analysis on existing `sweep_output/` and `sweep_output_threshold_0/` directories. Re-run any sweep runs where checkpoint is missing. Compute σ(n_skip), α(n_skip), val-loss(n_skip). Fit a U-shape or sigmoid for each observable; test whether val-loss correlates with |σ − 1|.

**Pre-registered kill.** If σ(n_skip) is flat (range < 0.1) OR val-loss is independent of `|σ − 1|` (correlation < 0.3 absolute), the skip-connection-tunes-criticality claim dies.

**Deliverable.** Paper companion to Candidate 1: first demonstration of continuous topology control over distance-from-criticality on a trained transformer, with a computation-capacity readout.

**Cost.** ~1 week post-processing + ~1 week for any missing reruns.

---

## Candidate 3 — Does training push transformers toward or away from edge-of-chaos init?

**Question.** Init edge of chaos is well-characterised [3002]. If a network is initialised on the critical line, does SGD move it toward stronger criticality, weaker criticality, or straight through?

**Observable.** σ(training step), α(training step), Jacobian spectral radius ρ(training step), on nanoGPT trained on TinyStories or Shakespeare-char, checkpointing every N steps.

**Why it's novel.** Mean-field theory is silent on trained dynamics. The only adjacent result is the at-init drift toward feature-learning [3010: Yang-Hu µP 2021]. No work has tracked a criticality observable through training on real language models.

**Method.** Train nanoGPT from critical init (tuned σ_w, σ_b per Schoenholz 2017). Save 20+ checkpoints log-spaced in training steps. On each checkpoint compute σ, α, ρ, val-loss. Plot trajectories. Compare: (a) init-near-critical; (b) init-deep-subcritical; (c) init-supercritical — do trajectories converge?

**Pre-registered kill.** If all three init regimes produce identical final criticality observables, the init-conditioning-of-trained-criticality claim dies.

**Deliverable.** Paper: first empirical map of how SGD deforms the mean-field criticality landscape. Strong Neural Computation / NeurIPS candidate.

**Cost.** ~1 week training + ~1 week analysis.

---

## Candidate 4 — Avalanches and grokking: do criticality observables predict the grokking phase transition?

**Question.** [3010: Power 2022] shows training dynamics with a delayed-generalisation phase transition. [3011: Nanda 2023] tracks "progress measures" through the transition. Do avalanche exponents or branching ratios shift at the grokking step, and do they predict it before the val-loss signal appears?

**Observable.** σ(step), α(step), Jacobian ρ(step) on the canonical modular-arithmetic grokking task. Cross-reference with Nanda progress measures (fourier-basis structure emergence).

**Why it's novel.** [3011] provides interpretability-side progress measures; [3010] provides the training-loss signal. No paper has tested whether criticality observables are early indicators of grokking. If yes, that is a new class of progress measure grounded in physics.

**Method.** Standard grokking task (modular arithmetic, weight decay). Track criticality observables per step. Test: does |σ − 1| decrease substantially at least N steps before val-loss drops?

**Pre-registered kill.** If criticality observables lag val-loss or are uncorrelated with the phase transition, the early-indicator claim dies. Negative result still publishable as evidence against criticality-based training-phase diagnostics.

**Deliverable.** Workshop paper at ICML MechInterp / NeurIPS ATTRIB. Natural follow-up to Nanda's progress-measure line.

**Cost.** ~2 weeks.

---

## Candidate 5 — SAE features vs raw neurons: does basis matter for criticality?

**Question.** Sparse autoencoder features are claimed to be the "true" basis of computation in transformers [3024: Bricken 2023, 3025: Templeton 2024]. Do SAE features produce different criticality observables than raw neurons on the same activations?

**Observable.** (α_raw, σ_raw) vs (α_SAE, σ_SAE) on Gemma-2-2B with Gemma Scope. Plus random-projection and PCA bases as additional controls.

**Why it's novel.** Basis-sensitivity of criticality is a known methodological concern but has not been studied in the SAE framework. If SAE features produce cleaner critical signatures, that is a new argument for SAEs. If they do not, that is a new constraint on SAE interpretability claims.

**Method.** Gemma-2-2B + Gemma Scope SAEs (public weights). Cache residual-stream activations on Pile. Compute criticality observables in each basis. Test null: all bases produce same exponents within CI.

**Pre-registered kill.** If exponents differ by less than 0.1 across all four bases, basis-invariance holds and the differential-criticality claim dies.

**Deliverable.** Workshop paper linking statistical-physics criticality to interpretability feature-discovery. Anthropic + DeepMind audience.

**Cost.** ~2 weeks. Gemma Scope weights public.

---

## Candidate 6 — Layer-depth gradient of branching ratio in pretrained transformers

**Question.** Does σ_ℓ vary systematically with layer depth? Hypothesis: early layers supercritical (amplification for feature construction), late layers subcritical (integration for decision).

**Observable.** σ_ℓ for each layer ℓ ∈ {0..N} in GPT-2 small / medium / large / XL. Plus cross-architecture: Pythia, LLaMA-open-reproductions, OLMo.

**Why it's novel.** Layer-resolved criticality is natural in physics but has not been computed for transformers. The hypothesis follows from MI circuit analyses [3024: Olsson induction heads, 3025: Wang IOI] where distinct layers play distinct roles.

**Method.** Extend Candidate 1 pipeline to per-layer decomposition. Fit a smooth function σ(ℓ / N); test monotonicity.

**Pre-registered kill.** If σ_ℓ is flat across depth within CI, the layer-gradient hypothesis dies.

**Deliverable.** Short paper on layer-resolved transformer criticality. Natural supplement to Candidate 1 but worth its own scope-check because it is architecturally informative on its own.

**Cost.** ~1 week as extension of Candidate 1.

---

## Candidate 7 — Criticality observables across model scale (Pythia suite)

**Question.** Pythia [3082: Biderman 2023] releases checkpointed runs at 7 scales from 70M to 12B. Do criticality observables (σ, α) scale systematically with model size? Approach a limit? Diverge?

**Observable.** σ, α, crackling-noise exponents for Pythia-70M through Pythia-12B, at fixed training checkpoint (final), on matched input distribution.

**Why it's novel.** Links criticality observables to the scaling-laws literature [3013: Kaplan 2020, 3014: Hoffmann 2022]. If criticality observables scale as a power of N, that is a new scaling law. If they asymptote, that is evidence large networks lock onto a universal critical manifold.

**Method.** Pythia HuggingFace weights. Sampling + avalanche analysis scripted across scales. Two decades of model size should be enough for power-law-vs-asymptote discrimination.

**Pre-registered kill.** If no systematic trend across 3+ scales, or if signal is buried in CI, report negative.

**Deliverable.** Paper: scaling-law for criticality, or negative result ruling it out.

**Cost.** ~3 weeks (largest models stress RTX 3060 VRAM — need to run inference at reduced batch size).

---

## Candidate 8 — Induction heads and critical dynamics: a case study

**Question.** [3024: Olsson 2022] identifies induction heads as a specific circuit that emerges during training. Does this specific circuit's activation pattern show avalanche statistics distinct from neighbouring (non-induction) heads?

**Observable.** Attention-pattern avalanches in induction heads vs matched-layer control heads, in pretrained GPT-2.

**Why it's novel.** Connects MI circuit discovery [3024, 3025] to criticality observables. If induction heads show stronger critical signatures than control, criticality is tied to specific computational mechanism, not an average property.

**Method.** Identify induction heads in GPT-2 (published in [3024] + TransformerLens replication). For each, compute avalanche statistics on attention patterns. Compare to matched non-induction heads.

**Pre-registered kill.** If induction-head and control-head exponents are within CI, the circuit-specific-criticality claim dies.

**Deliverable.** Short paper or workshop paper on circuit-specific criticality.

**Cost.** ~1 week.

---

## Candidate 9 — Dynamic range peaks at criticality: a capability-measurement test

**Question.** Kinouchi-Copelli [1022] predict that dynamic range (ratio of max to threshold response) is maximised at criticality. Translate to an LLM: prompt-difficulty sweep. Does perplexity / capability response vs prompt-difficulty peak in slope at a specific distance-from-criticality?

**Observable.** Capability metric vs input-difficulty curve, for networks at different tuned criticality (via skip-connection sweep, or across Pythia scales).

**Why it's novel.** Directly tests the functional claim of the criticality hypothesis on trained LLMs. Currently no published test of dynamic-range peak on a trained LLM.

**Method.** Benchmarks of graduated difficulty (e.g. arithmetic digit-count; multi-hop QA with variable hops). Measure response curve. Compute dynamic range. Correlate with |σ − 1|.

**Pre-registered kill.** If dynamic range is flat across criticality variation, or does not peak near σ = 1, the functional-criticality link dies.

**Deliverable.** Paper: direct test of the Kinouchi-Copelli prediction on trained LLMs. Strong ICML / ICLR candidate.

**Cost.** ~3 weeks.

---

## Candidate 10 — Semantically-conditioned Lyapunov: ROME-style perturbations

**Question.** Random-perturbation Lyapunov estimates may not capture the semantically-relevant sensitivity. Use ROME [3027: Meng 2022] perturbations (rank-one edits along known causally-important directions) to compute directional Lyapunov exponents. Do these track the raw-Lyapunov estimate, or show task-conditional structure?

**Observable.** Semantically-conditioned Lyapunov exponent along K known directions vs raw-random Lyapunov, on GPT-2 + GPT-J. Correlate with criticality observables.

**Why it's novel.** Semantically-conditioned Lyapunov is a bridge between MI primitives and criticality that has no precedent. Direct contribution from the lit_ml gap section.

**Method.** TransformerLens + ROME hooks + TransformerLens activation patching. Apply rank-one perturbations; measure response propagation.

**Pre-registered kill.** If directional Lyapunov is independent of direction (i.e. matches random-perturbation estimate), the semantic-structure claim dies.

**Deliverable.** Workshop paper at ATTRIB / MechInterp.

**Cost.** ~2 weeks.

---

## Candidate 11 — CNN criticality on Fashion-MNIST as a cross-architecture control

**Question.** The existing `fashion_mnist_project/` CNN is a smaller, more tractable testbed. Do the conclusions from transformer work (Candidates 1–3) transfer to CNNs?

**Observable.** σ, α, crackling-noise exponents on trained Fashion-MNIST CNN. Compare with init control and with the transformer results.

**Why it's novel.** Cross-architecture replication strengthens any universality claim. CNN criticality has been partially studied [3003: Xiao 2018 at-init] but not with post-training avalanche exponents.

**Method.** Extend ActivationAnalyzer → avalanche pipeline to the existing `fashion_mnist_classifier.py`. Compute observables at multiple training stages.

**Pre-registered kill.** Negative result is itself informative (architectural specificity of transformer criticality).

**Deliverable.** Replication / control for transformer papers; possibly a standalone workshop paper on CNN criticality.

**Cost.** ~1 week. Infrastructure already exists.

---

## Candidate 12 — Griffiths phase or true criticality? The neutral-model rejection test

**Question.** Martinello et al. [2037] show neutral null models and Griffiths phases reproduce α ≈ 3/2 without a phase transition. On the activation data from Candidate 1, can we distinguish "genuinely critical" from "Griffiths-phase-like"?

**Observable.** Scaling-relation residual `γ − (β − 1)/(α − 1)`; shape-collapse quality metric; parametric sensitivity of exponents across training runs with seed variation.

**Why it's novel.** The neutral-null-rejection step is methodologically mandatory for any criticality claim (per lit review) but has never been performed on an LLM.

**Method.** Use the observables already computed in Candidate 1. Add: seed-variation across 10+ training runs; fit the neutral-null Griffiths-phase prediction as a likelihood alternative.

**Pre-registered kill.** If neutral null fits at least as well as genuine criticality, the critical-brain-analogue-for-trained-LLM claim is narrowed or withdrawn.

**Deliverable.** Methodology paper: how to distinguish genuine from apparent criticality in deep networks. Necessary guard-rail for the broader program.

**Cost.** ~2 weeks, dependent on Candidate 1 completion.

---

## Candidate priorities (recommendation to scope-check agents)

- **Highest-novelty × lowest-cost**: Candidates 1, 2, 11. All use existing `~/entropy/` infrastructure directly; all target well-defined gaps in the lit review.
- **Highest-impact-if-positive**: Candidates 3, 4, 7. Trained-dynamics criticality, grokking-criticality link, scaling law for criticality.
- **Methodology-guardrail**: Candidate 12 is not optional — should run alongside Candidate 1 as a null-rejection check.
- **Highest-theoretical-depth**: Candidates 5, 10. Bridge criticality to mechanistic interpretability primitives.
- **Natural bundle**: 1 + 2 + 6 + 12 is a coherent first paper; 3 + 4 + 7 a second; 5 + 10 a third; 8 + 9 + 11 a fourth.

---

# Extension Round — Criticality-Driven Training and Brain-LLM Comparison

Candidates 13–22 proposed after the first round of scope-checks. These turn the programme from *"measure criticality in trained LLMs"* into *"use criticality to drive training"* and *"compare LLM criticality to biological brain criticality"*.

---

## Candidate 13 — Branching-ratio regularizer (criticality-penalised training)

**Question.** Does adding an explicit branching-ratio penalty `L_total = L_CE + λ · Σ_ℓ (σ_ℓ − 1)²` to the training loss produce better sample efficiency, generalisation gap, or grokking behaviour than standard training?

**Observable.** Val-loss trajectory, generalisation gap, grokking delay, and σ_ℓ(step) for `λ ∈ {0, 10⁻³, 10⁻², 10⁻¹, 1}` on nanoGPT + TinyStories and on modular-arithmetic grokking.

**Why it's novel.** Mean-field signal-propagation init [3002] ensures criticality at step 0. No published work penalises criticality *during* training as an auxiliary loss.

**Method.** Compute differentiable σ_ℓ via Jacobian-spectral-radius power iteration per batch (~20 JVPs per layer per step). Back-prop through σ. Sweep λ; compare matched-compute trajectories.

**Pre-registered kill.** If no λ beats λ = 0 on val-loss at matched compute, or if σ_ℓ is uncontrollable (training diverges), the regulariser-helps claim dies.

**Deliverable.** First training-time criticality-regularised LLM. If positive, a new knob alongside weight decay and dropout.

**Cost.** ~3 weeks. Training cost dominated by σ_ℓ gradient (~2× vanilla).

**Required controls.** L_CE-only baseline at matched λ-compute; dropout-matched baseline; weight-decay-matched baseline; 5 seeds per λ.

---

## Candidate 14 — Criticality-aware initialisation beyond Schoenholz

**Question.** Schoenholz 2017 [3002] tunes σ_w², σ_b² to χ_1 = 1 at init. For residual-LayerNorm architectures (modern LLMs), the critical knob is the residual branch scale γ and the LayerNorm gain. Can an iterative init — sample a batch, measure σ_ℓ, adjust γ_ℓ, repeat — reach σ_ℓ ≈ 1 uniformly across depth before training starts?

**Observable.** Pre-training σ_ℓ profile for (a) standard init, (b) Schoenholz at-init EOC, (c) iterative criticality init. Post-training val-loss vs compute.

**Why it's novel.** Schoenholz covers non-residual only. µP [3010] tunes for feature-learning scale but not σ = 1. Iterative batch-conditioned init for criticality is unexplored.

**Method.** Implement `fit_init_to_criticality(model, data_batch, target_σ=1.0)` as pre-training step. Benchmark against standard PyTorch init and Schoenholz init.

**Pre-registered kill.** If iterative init takes >1 % of training compute to converge, or if post-training val-loss is equal to standard init, the pre-tuning-helps claim dies.

**Deliverable.** A drop-in init function; benchmark paper. TMLR / JMLR.

**Cost.** ~2 weeks including benchmark.

---

## Candidate 15 — Criticality early-stopping signal

**Question.** Does `|σ_ℓ − 1|` (or D(t) from Wang 2604.16431) rise *before* val-loss degrades on an overfitting run? Can we early-stop purely on the criticality signal?

**Observable.** σ_ℓ(step), D(step), val-loss(step) on deliberately-overfitting runs (small data, long training). Time-lag cross-correlation of criticality-deviation onset with val-loss inflection.

**Why it's novel.** Val-loss early-stopping is standard. No published work uses a criticality observable as an independent early-stop signal. If criticality leads val-loss by even ~5 %, that's a new training-practice contribution.

**Method.** Overfit nanoGPT on 10 K-token Shakespeare subset (known to overfit by step ~5 K). Track criticality observables densely. Test lead-lag.

**Pre-registered kill.** If criticality lags val-loss, or leads by < 2 % of training budget, the early-stop claim dies.

**Deliverable.** Workshop paper on practical training diagnostics.

**Cost.** ~1 week.

---

## Candidate 16 — Criticality curriculum: anneal λ during training

**Question.** Biological cortex is more critical during development and less critical in mature state [1020: Tetzlaff 2010, 1033: Gireesh-Plenz 2008]. Does an annealed criticality regulariser — strong at start, weak at end — produce better-trained LLMs than constant λ?

**Observable.** Final val-loss and capability metrics for `λ(t) = λ_0 · decay(t)` schedules vs constant λ and λ = 0.

**Why it's novel.** Curriculum-learning literature covers data-difficulty schedules; no work schedules the criticality-regulariser coefficient. The biological cortical-development analogue is a direct motivation.

**Method.** Build on Candidate 13's training pipeline. Compare linear / cosine / exponential λ-schedules. Train nanoGPT + Pythia-70M from scratch.

**Pre-registered kill.** If no schedule beats best-constant-λ within seed noise, curriculum dies.

**Deliverable.** Training-regime paper. Strong ICLR / NeurIPS candidate if positive.

**Cost.** ~3 weeks (requires Candidate 13 training infrastructure).

**Dependence.** Requires Candidate 13.

---

## Candidate 17 — Controllable grokking via σ-steering

**Question.** If σ tracks the grokking transition (Candidate 4, Wang 2604.16431), can we *induce* grokking by actively steering σ → 1 during training on modular arithmetic? Does σ-control accelerate, eliminate, or destabilise grokking?

**Observable.** Grokking step (val-loss-inflection step) for (a) standard training, (b) σ-steered training (Candidate 13's regulariser targeted at σ = 1), (c) σ-anti-steered (target σ = 0.7 or 1.3). 30 seeds per condition.

**Why it's novel.** Passive grokking observation is documented [3010: Power 2022, 3011: Nanda 2023]. Active σ-steering as a grokking intervention is new. If positive, it is direct causal evidence that criticality drives grokking.

**Method.** Build on Candidates 13 + 4. Modular-arithmetic + weight-decay setup from Power 2022; add σ-steering; n = 30 seeds per condition to beat seed variance (per scope-check of Candidate 4).

**Pre-registered kill.** If σ-steered condition shows grokking-step within CI of standard (Mann-Whitney U > 0.05), active-steering-causes-grokking claim dies.

**Deliverable.** Strong NeurIPS / ICML submission; the causal grokking result the field is missing.

**Cost.** ~3 weeks.

**Dependence.** Requires Candidate 13 pipeline; benefits from Candidate 4 reframed analysis.

---

## Candidate 18 — Cross-universality-class comparison: LLM activations vs cortical avalanches

**Question.** Do pretrained-LLM avalanche exponents (α, β, γ) match the mean-field-DP universality class of cortical avalanches [1001: Beggs-Plenz 2003, 1005: Shriki 2013, 1004: Ma 2019] *quantitatively* within bootstrap CI, not just qualitatively as "near 3/2"?

**Observable.** α_LLM vs α_cortex for matched event-definition protocols. Public cortical-avalanche datasets (Beggs-Plenz archive, Shriki MEG data) vs GPT-2 / Pythia residual-stream activations on matched-time-length sequences.

**Why it's novel.** The "LLMs are like brains" claim is routinely made qualitatively. No paper has tested universality-class membership between cortex and trained LLM activations using the same exponent-extraction protocol on both.

**Method.** Identical CSN-fitting + crackling-noise-cross-check + shape-collapse pipeline applied to both data sources. Joint bootstrap test for exponent-equality.

**Pre-registered kill.** If exponent-CIs do not overlap, the universality-class claim dies. Still publishable as "LLMs and cortex are in *different* universality classes", which itself is informative.

**Deliverable.** Nature Machine Intelligence / PNAS / Neural Computation cross-field paper.

**Cost.** ~3 weeks. Data loading for cortical datasets is the wall cost.

**Dependence.** Requires Candidate 1 pipeline.

---

## Candidate 19 — Sleep / wake analogue: training-mode vs inference-mode criticality

**Question.** Cortical avalanche statistics differ between awake (active processing, near σ = 1) and slow-wave sleep (memory consolidation, σ ≠ 1) [1031: Meisel 2013, 1032: Meisel 2017]. Do transformer activation statistics differ between training-mode (backprop active, weights updating) and inference-mode (forward-only)? Which is the "awake" analogue?

**Observable.** σ, α, crackling-noise exponents computed (a) during training, on activations from training steps; (b) post-training, on the same model frozen, same inputs. Compare.

**Why it's novel.** No work has compared criticality observables between training and inference modes of the same network. The sleep/wake analogue is a testable-but-untested biological mapping.

**Method.** Capture activations on a held-out batch mid-training (model weights frozen on that batch); compare to same model fully trained on same batch. Repeat across training steps.

**Pre-registered kill.** If no statistically-detectable difference, the mode-asymmetry claim dies.

**Deliverable.** Workshop or short paper. Neural Computation.

**Cost.** ~2 weeks.

**Dependence.** Candidate 1 pipeline + Candidate 3 mid-training checkpoints.

---

## Candidate 20 — Architecture-class criticality: dense vs SSM vs MoE

**Question.** Do modern architectures with fundamentally different inductive biases — dense transformer, Mamba state-space model, mixture-of-experts — land on the same criticality manifold, or do they cluster into distinct universality sub-classes?

**Observable.** σ, α, crackling-noise exponents for: GPT-2 small/medium, Pythia-1.4B (dense), Mamba-1.4B / Mamba-2.8B (SSM), DeepSeek-V2-Lite or Mixtral-8x7B-int4 (MoE if it fits). Matched input distribution.

**Why it's novel.** All adjacent prior work is on dense transformers or RNNs. SSMs have different recurrence structure (selective state-space) and MoEs have sparse-activation-by-design. The architectural-class hypothesis is fresh.

**Method.** HuggingFace weights for all; matched-pipeline exponent extraction. Cross-class universality test. Controls: matched parameter count where possible; matched training data where possible.

**Pre-registered kill.** Negative result (same exponents across classes) is publishable as "criticality is architecture-independent"; positive result as "architectural class determines criticality universality class". Kill: neither direction is distinguishable from seed noise.

**Deliverable.** Strong ICML / ICLR main paper.

**Cost.** ~4 weeks. Mamba is tricky (few public checkpoints); MoE is VRAM-constrained.

**Dependence.** Candidate 1 pipeline.

---

## Candidate 21 — Pretrained vs instruction-tuned: does RLHF shift σ?

**Question.** Post-training (SFT + RLHF) narrows a model's output distribution substantially [cite Anthropic/DeepMind]. Does it also narrow its activation statistics, and specifically does it move σ away from 1 toward a sub-critical (damped) regime?

**Observable.** σ(base) vs σ(instruction-tuned) vs σ(RLHF-tuned) for matched model families: LLaMA-2-7B base vs chat, Gemma-2-2B vs 2-2B-it, Pythia-1.4B vs Pythia-1.4B-instruct (where available).

**Why it's novel.** No paper compares criticality observables between base and post-trained models. The "RLHF tames capability" claim has no physics-observable test.

**Method.** Matched activation-extraction pipeline; CSN fits on both; bootstrap difference test.

**Pre-registered kill.** If σ_base ≈ σ_RLHF within CI, the RLHF-shifts-criticality claim dies.

**Deliverable.** Short paper; ICLR / ICML workshop.

**Cost.** ~2 weeks.

**Dependence.** Candidate 1 pipeline.

---

## Candidate 22 — Spiking-transformer direct biological comparison

**Question.** Convert a small transformer to spiking-neural-network form via surrogate-gradient training [Eshraghian 2021 snntorch, Zhou et al. 2024 spiking transformer]. Its spike rasters can be analysed with the identical cortical-avalanche detection pipeline used on rodent recordings. Do spiking-transformer avalanches quantitatively match cortical avalanches?

**Observable.** Spike-raster avalanche exponents (α, β, γ) on a trained spiking transformer vs the same exponents on published cortical spike data.

**Why it's novel.** Makes the brain-LLM comparison literal: spike-level observation on both sides. No prior work does this.

**Method.** Train a small SpikFormer / Spiking-GPT on TinyStories (public codebase exists). Apply Beggs-Plenz avalanche detection to spike raster. Compare to [1001: Beggs-Plenz 2003] and related cortical data.

**Pre-registered kill.** If spiking-transformer avalanches show exponents outside published cortical CI, the literal-brain-analogue claim dies.

**Deliverable.** Bridge paper; Nature Machine Intelligence / Neural Computation. Potentially the most theoretically significant of the set if positive.

**Cost.** ~4 weeks including spiking-transformer training.

**Dependence.** Independent of main pipeline; needs spiking-transformer training from scratch.

---

## Extension-round priorities (recommendation to scope-check agents)

- **Highest-novelty × moderate-cost**: Candidates 17, 18, 20, 22. Controllable grokking, brain-LLM universality class test, architecture-class criticality, spiking-transformer bridge.
- **Most practical / training-regime**: Candidates 13, 14, 15, 16. Regulariser, init, early-stop, curriculum.
- **Comparative / descriptive**: Candidates 19, 21. Training-vs-inference, base-vs-RLHF.
- **Natural bundles**: 13 + 14 + 17 (criticality-as-training-tool); 18 + 20 + 22 (brain-homology across architectures); 15 + 16 (training-regime interventions); 19 + 21 fold into existing Papers 3 and 5.

---

# Synthesis Round — Candidates Drawn from the 209-Paper Database

Candidates 23–35 proposed after merging the Agent-A arXiv fill-in (38 entries) and Agent-B non-arXiv sweep (31 entries) that raised the citation count to 209. Each draws on at least one specific paper the first two rounds did not explicitly use.

---

## Candidate 23 — Detrended Fluctuation Analysis (DFA) of LLM activations

**Question.** Do residual-stream activation time series show long-range temporal correlations with a DFA exponent α_DFA ≈ 1, the signature of 1/f fluctuations associated with critical brain dynamics [1023: Linkenkaer-Hansen 2001, 1032: Meisel 2017]?

**Observable.** DFA scaling exponent α_DFA per layer on token-wise residual-stream activations for GPT-2, Pythia-1.4B, Gemma-2-2B. Compare to at-init control.

**Why it's novel.** Avalanche-size `P(s)` is a cross-sectional observable; DFA is a complementary long-range-temporal-correlation probe. No published work computes DFA on trained transformer activations. The neuroscience use is mature (DFA exponent shifts away from 1 under sleep deprivation).

**Method.** Cache token-wise activations on Pile sample. For each neuron / SAE feature, compute integrated fluctuation F(n) vs window size n; fit slope in log-log. Report α_DFA distributions per layer + per basis (raw vs SAE).

**Pre-registered kill.** If α_DFA is within 0.05 of 0.5 (uncorrelated) or 1.5 (non-stationary) across all layers and bases, the LRTC-criticality claim dies.

**Deliverable.** Short paper or section of Paper 1 Anchor. Entropy journal / workshop.

**Cost.** ~2 weeks. Inference-only on pretrained models.

**Required controls.** At-init baseline; shuffled-token surrogate; block-bootstrap for CIs; threshold independence.

---

## Candidate 24 — 1/f power spectrum of residual-stream activations

**Question.** Does the power spectral density of residual-stream activations show 1/f^β scaling with β ≈ 1, the canonical SOC signature [2001: Bak, Tang, Wiesenfeld 1987]?

**Observable.** Power spectral density S(f) of per-neuron activation time series on auto-regressive generation. Fit β in S(f) ∝ 1/f^β across decades.

**Why it's novel.** 1/f spectrum is the founding SOC observable; no ML paper has measured it on trained transformer activations. Complementary to both avalanche size (cross-sectional) and DFA (time-integrated).

**Method.** Welch / multi-taper spectrum on per-neuron time series from 100K-token generation. Fit β via CSN-style goodness-of-fit for power-law spectra.

**Pre-registered kill.** If β is consistently outside [0.8, 1.2] across layers / bases, the 1/f-SOC-signature claim dies.

**Deliverable.** Methodology paper / section of Paper 1.

**Cost.** ~1 week. Inference-only.

**Required controls.** At-init baseline; surrogate time series; block-bootstrap.

---

## Candidate 25 — Temporal renormalization group on LLM token sequences

**Question.** Sooter 2025 [4007] applies temporal renormalization group (TRG) to neural activity, revealing universality at critical points. Does TRG on transformer token activations reveal a non-trivial fixed point, and does the fixed-point exponent match a known universality class (DP / mean-field / edge-of-synchronization)?

**Observable.** TRG flow of activation covariance spectrum under coarse-graining.

**Why it's novel.** TRG is a canonical physics tool newly adapted to neural data. No ML work uses it. If LLM activations flow to a DP fixed point, that is a strong universality-class assignment.

**Method.** Implement Sooter's TRG pipeline; apply to GPT-2 residual-stream activations. Report fixed-point exponent with uncertainty.

**Pre-registered kill.** If flow is trivial (no fixed point) or fixed-point exponent is well outside all known universality classes, the universality-class assignment dies.

**Deliverable.** Strong Neural Computation / PNAS candidate if positive (bridge paper between statistical physics and ML).

**Cost.** ~4 weeks including TRG infrastructure.

**Required controls.** At-init baseline; CNN baseline (to check Yoneda 2025 PRR [4021] CNN-DP assignment recoverable); Mamba baseline.

---

## Candidate 26 — Prompt-type modulates σ at inference

**Question.** Static weights; runtime-variable input. Does branching ratio σ depend on the prompt class — ICL vs non-ICL, chain-of-thought vs direct answer, easy vs hard math, factual vs associative?

**Observable.** σ(prompt-class) for each of N prompt classes on fixed GPT-2 / Gemma-2-2B weights.

**Why it's novel.** All existing candidates treat σ as a property of the model. If σ varies per-input class, criticality is a *computational state* elicited by specific inputs, not a fixed property. This reframes the entire programme and aligns with input-driven absorbing-state dynamics in physics [2015: Jensen 1998, 2016: Hinrichsen 2000].

**Method.** Curate K balanced prompt sets (K ≈ 6). Compute σ via MR estimator per prompt-class batch. Two-way ANOVA: σ ~ prompt-class × layer.

**Pre-registered kill.** If σ is within CI across all prompt classes, the input-modulation claim dies.

**Deliverable.** ICML / NeurIPS main if positive — a new meta-observable.

**Cost.** ~3 weeks.

**Required controls.** Prompt-length matching; per-class sample size; random-class permutation null.

---

## Candidate 27 — In-context-learning emergence at σ = 1

**Question.** Olsson 2022 [3024] shows induction-head / ICL emerges at a specific training step via a phase transition. Does σ cross 1 at the same step? If yes, ICL emergence is a direct consequence of criticality crossing.

**Observable.** σ(step), ICL-benchmark(step), induction-head-score(step) on checkpoint-trained nanoGPT or Pythia-70M. Cross-correlation at the emergence step.

**Why it's novel.** Olsson's phase transition is MI-framed; Nanda 2023 [3012] progress measures are MI-framed. No-one has correlated with σ. Strong Paper 3 companion.

**Method.** Pythia checkpoints (154 per scale) + Nanda-style ICL score + σ pipeline. Compute cross-correlation at fine step resolution around the induction-head emergence.

**Pre-registered kill.** If σ step and ICL-emergence step differ by > 10 % of training, the coincidence claim dies.

**Deliverable.** ICML MechInterp / ATTRIB workshop; natural companion to Paper 3.

**Cost.** ~2 weeks as extension of Paper 3.

**Required controls.** Matched-compute baseline; non-ICL-prone architecture control.

---

## Candidate 28 — Per-attention-head σ distribution

**Question.** Is the per-head branching ratio distribution across GPT-2's 144 heads bimodal (induction vs non-induction), unimodal, or power-law? What does the distribution shape reveal about criticality-circuit structure?

**Observable.** σ_{layer, head} for every attention head in GPT-2 small / medium. Distributional analysis.

**Why it's novel.** Candidate 8 is circuit-specific (induction-head vs control). C28 is distributional — reveals whether criticality is concentrated in specific heads or spread across all. Different, finer-grained question.

**Method.** Per-head causal branching via attention-head ablation + patching. Report histogram of σ values; test bimodality (Hartigan's dip test).

**Pre-registered kill.** If the distribution is uniform and σ-range < 0.05, the head-heterogeneity claim dies.

**Deliverable.** Short paper / section of Paper 1.

**Cost.** ~2 weeks.

**Required controls.** Causal ablation vs correlational co-firing.

---

## Candidate 29 — Effective dimension tracks σ

**Question.** Fontenele 2024 [4005] shows cortical criticality is confined to a low-dimensional subspace. In trained transformers, does participation ratio / effective dimension of residual-stream activations track σ(t) through training? Is ambient σ ≠ low-dim-subspace σ?

**Observable.** Effective dimension D_eff (participation ratio) vs σ_ambient vs σ_top-K-PC for matched checkpoints.

**Why it's novel.** Fontenele's finding is the most important non-arXiv 2024 result in the entire lit review and directly motivates a reframe of Candidate 5's basis-invariance null. No ML paper has replicated Fontenele in trained networks.

**Method.** On Pythia checkpoints, compute D_eff via covariance-eigenvalue participation ratio. Measure σ in (a) ambient basis, (b) top-K-PC subspace with K = D_eff. Test whether subspace σ is criticality-consistent while ambient is not.

**Pre-registered kill.** If ambient and subspace σ agree within CI at all checkpoints, the low-dim-subspace reframe of criticality dies.

**Deliverable.** ICML / NeurIPS main if positive. Direct empirical replication of a Sci. Adv. result in ML.

**Cost.** ~3 weeks.

**Required controls.** At-init baseline; random-projection subspace control; sparsity-matched null.

---

## Candidate 30 — Hallucination rate and σ

**Question.** Hypothesis: hallucinations occur more frequently when the model is locally super-critical. Testable: controlled hallucination benchmark (TruthfulQA, HalluQA, FEVER-contradicting) response accuracy vs per-prompt σ on a fixed model.

**Observable.** Hallucination-benchmark score as function of binned per-prompt σ, for Gemma-2-2B and Pythia-1.4B.

**Why it's novel.** Connects criticality to a practical model-behavior pathology. No work relates statistical-physics observables to hallucination rate. Potentially opens an interpretable "hallucination diagnostic" axis.

**Method.** On each benchmark prompt, compute σ at runtime + hallucination label. Regression: accuracy ∝ f(|σ − 1|).

**Pre-registered kill.** If hallucination rate is independent of |σ − 1| (correlation < 0.15 absolute), the criticality-hallucination link dies.

**Deliverable.** NeurIPS / ICLR main if positive; potential applied-safety impact.

**Cost.** ~3 weeks.

**Required controls.** Per-prompt difficulty confound; length confound; base vs instruction-tuned confound.

---

## Candidate 31 — Adversarial robustness as sub-criticality

**Question.** At criticality, sensitivity to small perturbations diverges. Adversarially-robust models should be sub-critical. Test: measure σ for matched pairs of vanilla vs adversarially-trained vision transformers (ViT-B/16 on ImageNet — public adversarial checkpoints exist).

**Observable.** σ(vanilla) vs σ(adv-trained) for matched-architecture ViT pairs. Also: robust-accuracy vs |σ − 1| scaling.

**Why it's novel.** No work relates adversarial robustness to a statistical-physics observable. If positive, σ becomes a robustness proxy that can be read out without running expensive adversarial attack.

**Method.** Public Madry-style adversarial-trained ViT-B/16 (or robust ResNet as baseline). Compute σ pipeline. Compare to non-robust counterparts.

**Pre-registered kill.** If σ(vanilla) and σ(robust) overlap within CI, the sub-critical-robustness claim dies.

**Deliverable.** NeurIPS / ICLR main.

**Cost.** ~2 weeks.

**Required controls.** Matched-accuracy control; matched-architecture control.

---

## Candidate 32 — Quantization damage detectable via σ-shift

**Question.** Does int8 / int4 quantisation measurably shift σ relative to fp16? If yes, σ-shift is a new diagnostic for "quantisation damage" independent of perplexity.

**Observable.** Δσ = σ(fp16) − σ(int8) − σ(int4) for LLaMA-2-7B, Mistral-7B, Gemma-2-2B matched weights at multiple quantisation recipes (AWQ, GPTQ, SmoothQuant).

**Why it's novel.** Quantisation is evaluated by perplexity + downstream accuracy; no work evaluates it via activation-criticality drift. A criticality-based quantisation diagnostic has practical value for edge deployment.

**Method.** HuggingFace public quantised checkpoints; matched prompt set; σ measurement via MR estimator.

**Pre-registered kill.** If |Δσ| < 0.05 across all quantisation recipes, the quantisation-damage-via-σ claim dies.

**Deliverable.** Short paper; TMLR / MLSys workshop; practical impact.

**Cost.** ~2 weeks.

**Required controls.** Perplexity-matched baseline; calibration-data confound.

---

## Candidate 33 — Distillation preservation of σ

**Question.** Does knowledge distillation preserve or destroy σ from teacher to student? If distillation destroys criticality, every deployed distilled model is systematically sub-critical — a fundamental observation for deployment science.

**Observable.** σ(teacher) vs σ(student) for public distilled pairs: DistilBERT / BERT, DistilGPT-2 / GPT-2, TinyLLaMA / LLaMA-7B, smaller-student-vs-teacher via Gemma-2-2B → Gemma-2-nano.

**Why it's novel.** Distillation literature evaluates via downstream task score; no work evaluates criticality preservation.

**Method.** Matched input distribution; σ pipeline on both models; statistical test on Δσ.

**Pre-registered kill.** If σ(teacher) = σ(student) within CI across all pairs, the distillation-destruction claim dies.

**Deliverable.** Short paper; workshop.

**Cost.** ~2 weeks.

**Required controls.** Matched-accuracy control; matched-data-distribution control.

---

## Candidate 34 — Emergent capability = σ phase transition

**Question.** Wei 2022 [3015] claims genuine phase transitions in emergent capabilities; Schaeffer 2023 [3016] claims metric-artifact. Compute σ(scale) across Pythia 70M–2.8B (and Pythia 12B int8 if feasible). Do capability-discontinuities correspond to σ-crossings?

**Observable.** Capability score (e.g. TriviaQA accuracy, BIG-Bench subsets) vs scale; σ vs scale. Test whether their inflection points align.

**Why it's novel.** Directly resolves a named open field debate. A σ-crossing at the same scale as the emergence step is strong evidence for a real phase transition (Wei side); no σ-crossing supports Schaeffer. First empirical test with a physics observable.

**Method.** Pythia suite + capability benchmarks at matched scale; σ pipeline. Bayesian changepoint detection on both curves.

**Pre-registered kill.** If σ(scale) is monotone and featureless across scales where capabilities discontinuously emerge, Schaeffer-side verdict.

**Deliverable.** NeurIPS / ICLR main — high-impact debate resolution.

**Cost.** ~4 weeks as companion to Paper 5.

**Required controls.** Matched-data-distribution; matched-training-compute; metric-artifact test via continuous proxy.

---

## Candidate 35 — ViT vs language-transformer σ

**Question.** Same architecture class (attention-based transformer); different input modality (pixels vs tokens). Does σ match between vision and language transformers, pointing to architecture-dependent criticality, or differ, pointing to input-distribution-dependent criticality?

**Observable.** σ for ViT-B/16 (ImageNet), DinoV2 ViT-B, CLIP-vision-B/16 vs GPT-2 small, Pythia-160M. Matched parameter count where possible.

**Why it's novel.** No cross-modal criticality comparison exists. A matched-σ result would support architecture-dependent universality; a split would support input-distribution-dependent criticality. Either outcome is informative.

**Method.** HuggingFace weights; matched activation-pipeline; cross-modal σ comparison.

**Pre-registered kill.** Genuine null: if σ values overlap within CI, criticality is architecture-determined (publishable positive). If σ values differ by > 0.15, criticality is input-dependent (publishable differently).

**Deliverable.** ICML / NeurIPS main or Paper 7 arm.

**Cost.** ~2 weeks.

**Required controls.** Matched-parameter; matched-training-data-scale; matched-pretraining-objective.

---

## Synthesis-round priorities

- **Highest novelty-cost ratio**: C29 (effective dim vs σ — Fontenele hook), C34 (Wei vs Schaeffer resolution), C23/C24 (new orthogonal observables), C26 (input-modulation paradigm shift).
- **Practical impact if positive**: C30 (hallucination), C31 (adversarial robustness), C32 (quantisation), C33 (distillation).
- **Natural bundles**: 23 + 24 + 28 as "observable-battery" extension of Paper 1; 29 + 34 as Paper 5 scaling-atlas enrichment; 30 + 31 as a new applied-criticality paper; 32 + 33 as a deployment-criticality short; 26 + 27 + 35 as an input-and-modality set.
