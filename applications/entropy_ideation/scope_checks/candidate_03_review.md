# Phase −0.5 Scope Check — Candidate 3

**Target.** Does training push transformers toward or away from edge-of-chaos init? Track σ(step), α(step), Jacobian spectral radius ρ(step) on nanoGPT trained on TinyStories or Shakespeare-char, checkpointing every N steps. Compare init-near-critical vs init-deep-subcritical vs init-supercritical trajectories.

**Reviewer inputs.** `literature_review.md`, `knowledge_base.md`, `papers.csv`, `candidate_ideas.md`, `lit_ml.md` §§1, 3, 9, 10, `lit_complex.md` §6, and arXiv 2024–2026 scan.

**Verdict up front: REFRAME → PROCEED.** The core idea is sound and addresses a real gap in the literature, but three concrete design changes are needed before this is a clean Phase 0 target. The reframed version is a strong Neural Computation / NeurIPS-workshop candidate.

---

## 1. Novelty assessment

**Core claim.** Init-edge-of-chaos is well-characterised [3002, 3003, 3005]. Mean-field theory is silent on whether SGD preserves, augments, or destroys that structure. Tri-init trajectory tracking of (σ, α, ρ) through training on a real language-modelling task would be the first empirical map of SGD-induced deformation of the mean-field critical manifold.

**arXiv 2024–2026 scan.** The closest recent hits are:

- **[Mapping the Edge of Chaos, arXiv:2501.04286 (2025)].** Decoder-only transformers on Shakespeare-char; analyses the *hyperparameter-space* (learning-rate × attention-LR) boundary between convergent and divergent training and finds fractal structure with dimension ≈ 1.97. It does **not** track σ/α/ρ through training. Its "edge of chaos" is the trainability frontier in hyperparameter space, not the signal-propagation χ_1 = 1 manifold. Complementary, not redundant.
- **[Intelligence at the Edge of Chaos, ICLR 2025, arXiv:2410.02536].** Pretrains GPTs on ECA-generated data of varying Langton-λ complexity and finds a complexity sweet-spot for downstream reasoning. Tracks *task* performance against *input-data* complexity — orthogonal to our proposed tracking of *internal* criticality observables through training.
- **[Leveraging chaos in training, arXiv:2506.08523].** Characterises a chaotic-to-regular transition in *optimiser* dynamics as learning rate varies. Again, parameter-space rather than activation-space criticality.
- **[Phase Transitions in Small Transformers, arXiv:2511.12768, Nov 2025].** Tracks vocabulary-level order-parameters (Poisson/sub-Poisson statistics of word occurrences) through training on a small GPT on character-level text; identifies an abrupt transition. Does **not** compute σ, α, or Jacobian spectral radius. This is the closest live competitor; its existence raises the bar but leaves the signal-propagation observables untouched.
- **[Tuning Universality in Deep Neural Networks, arXiv:2512.00168, Dec 2025].** Stochastic theory (Brownian motion in a log trap vs absorbed BM) predicting that activation-function design selects avalanche universality classes in random DNNs. Theoretical; measurements at init only; no training trajectories.
- **[Algorithmic Phase Transitions, arXiv:2412.07386].** Tracks arithmetic-circuit emergence in Gemma-2-2B — mechanistic progress-measure style, no criticality observables.

The 2024–2026 literature has expanded the *language* of criticality-in-transformers but no paper tracks the Schoenholz-style χ_1 / branching-ratio / avalanche-exponent triple through training on a real LM with a tri-init design. The empirical niche stated in `literature_review.md` §"Open gap" is intact.

**Adjacency to grokking work.** Liu 2022 [3013] gives a phase diagram in (weight-decay × data-fraction) space but its order parameters are (accuracy, train-loss); no criticality observables. Nanda 2023 [3012] progress-measures are Fourier-basis-specific interpretability constructs. Power 2022 [3011] observes the loss-transition only. None of the three compute σ, α, or ρ. Candidate 4 — *not* Candidate 3 — is the one that specifically sits on the grokking progress-measure line. Candidate 3's domain is natural-language training, where no phase transition is expected a priori and the observable is the *drift* rather than the *jump*. This is a cleaner scientific question and does not collide with the Nanda/Power programme.

**Novelty verdict: HIGH.** No published or preprinted work does what the candidate proposes. The closest competitor [2511.12768] uses orthogonal vocabulary-level observables; the reframed version should cite it as related but distinct.

## 2. Falsifiability & the tri-init design

The candidate's pre-registered kill: "if all three init regimes produce identical final criticality observables, the claim dies." This is sharper than most candidate kills, but there are real concerns.

**Concern 2a — seed variance.** nanoGPT-scale training on TinyStories or Shakespeare-char has non-trivial run-to-run variance in final val-loss (~5–15% at 10M params, per replication notes in `klyap/nanoGPT-TinyStories` and similar). Any claim that "final σ(critical-init) ≠ final σ(subcritical-init)" must clear a seed-variance baseline. Three seeds per regime is the Mathematical-Framework-style minimum; five is defensible. The cost is 5 seeds × 3 inits = 15 runs, not 3 runs — budget accordingly.

**Concern 2b — what "critical init" means for residuals + LayerNorm.** The Schoenholz χ_1 = 1 prescription assumes vanilla tanh/ReLU MLPs with i.i.d. weights. nanoGPT has residual streams, LayerNorm, and attention softmax. Per `lit_ml.md` §1 and §10, the vanilla mean-field prediction is *not* the relevant critical boundary for this architecture — residual-stream architectures sit near a trivial χ_1 = 1 fixed point at init by construction (Yang Tensor Programs, `lit_ml.md` §1). The "tri-init" design must therefore specify what knob is being varied. Candidate options:
- **(a)** σ_w on the attention Q/K/V weights (residual block Jacobian driver);
- **(b)** σ_w on MLP weights only;
- **(c)** an attention-free MLP-block analogue with the Schoenholz prescription applied cleanly;
- **(d)** residual branch scale γ (deep-narrow-residual formulation).

The proposal as written does not specify. **Required change.** Option (d) is the cleanest because γ has a known mean-field theory (Hayou et al., De & Smith [3030 VERIFY]) and directly sets a Lyapunov-like init.

**Concern 2c — degeneracy of observables.** σ (branching-ratio), α (avalanche-exponent), and ρ (Jacobian spectral radius) are three observables but only one independent critical parameter in mean field; they are linked by σ = ρ at the critical point of a mean-field branching process, and α = 3/2 is implied. Reporting three highly correlated observables as "tripled evidence" is a known Schaeffer-style methodological trap. The falsifier needs to state which observable is primary and which are cross-checks. **Suggested primary: ρ** (cheapest, cleanest link to theory, basis-independent); **secondary:** σ via MR estimator on layer-propagated events; **tertiary:** α for universality-class.

**Falsifiability verdict: STRONG once reframed.** With specified init knob + seed-replicated tri-init + observable-hierarchy, the kill condition is sharp.

## 3. Wall-cost audit

The reviewer asked specifically about ρ per checkpoint on a ~10M nanoGPT.

**Full Jacobian is intractable.** Residual-stream dim d = 384 (default nanoGPT small) × context length T = 256 gives per-layer residual state of dimension ~10^5. Full d·T × d·T Jacobian (~10^10 entries) won't fit.

**Power iteration is tractable.** The dominant eigenvalue of the layer-ℓ → layer-(ℓ+1) residual-update Jacobian can be obtained in ~20 JVPs via Lanczos / power iteration, each JVP costing one forward + one backward pass at the block level (≈ 2× a forward-pass of a single block). For a 6-layer nanoGPT on a single RTX 3060 at batch-size 32, a single forward is ~15 ms; per-layer power-iteration for ρ_ℓ is ~0.6 s; per-checkpoint × 6 layers × 32 probe tokens × 20 iterations ≈ 20–40 s. Over 20 checkpoints × 3 init regimes × 5 seeds = 300 checkpoints × 40 s ≈ **3.5 GPU-hours** for ρ alone. Feasible on a 3060.

**σ via MR estimator.** Cheaper than ρ — it fits a decay curve on cached layer-propagated activations. Sub-second per checkpoint given cached activations. Dominant cost is activation caching (~100 MB × 20 checkpoints × 15 runs ≈ 30 GB disk; manageable).

**α via Clauset-Shalizi-Newman.** Requires ~10^4–10^5 avalanche samples for 2 decades of scaling. Per-checkpoint activation sample needs ≈ 10^5 tokens — easily within nanoGPT context budget. Python `powerlaw` package CSN bootstrap is sub-minute per checkpoint.

**Training runs.** 15 nanoGPT-small runs × (a few hours each on a 3060 for TinyStories 1-epoch, or ~1 hour for Shakespeare-char). Total **~30–50 GPU-hours** including analysis. Within the candidate's stated "~1 week training + ~1 week analysis" budget.

**Cost verdict: feasible on declared hardware.** Candidate 3 stated "~1 week training + ~1 week analysis" — realistic if the tri-init scoping and seed count are as above. Not realistic if the candidate silently scales to GPT-2-small or adds more init regimes.

## 4. Venue fit

- **Neural Computation** — primary target; edge-of-chaos + trained-network drift is a clean NC story.
- **NeurIPS / ICLR main track** — possible if results are strong (e.g. clear convergent trajectory independent of init across 5 seeds). Needs a tighter theoretical framing to compete.
- **NeurIPS MechInterp / ATTRIB / SciForDL workshops** — natural fit, lower bar.
- **Entropy (MDPI)** — fallback; compatible with the statistical-physics framing.

Reviewer risk: **Schaeffer-style push-back** that all three observables are noisy proxies of the same underlying quantity and that "drift" is simply an optimisation artefact. Mitigation: (i) report at-init and well-trained endpoints with 95% CIs; (ii) cross-reference at least one observable with a task-relevant metric (val-loss) to demonstrate it is not a nuisance parameter.

## 5. Required controls

Derived from `knowledge_base.md` §§4–5 and `literature_review.md` "pitfalls":

1. **At-init control at matching step 0.** Baseline for each of the three init regimes.
2. **Seed replication.** Minimum 3, preferred 5.
3. **Threshold plateau** for α (not for ρ). Sweep θ across at least 0.5× to 2× the nominal.
4. **Block-bootstrap CIs.** LLM activations are autocorrelated across tokens — naive bootstrap under-estimates error.
5. **MR estimator for σ** (Priesemann); naive branching-ratio is biased under subsampling.
6. **CSN fit for α** with lognormal / truncated-exponential log-likelihood rejection.
7. **NTK-regime probe.** Empirical NTK flow across checkpoints (trivial cost — Frobenius distance on gradient-kernel at fixed probe batch). This is the `lit_ml.md` §2 cheap check; it tells the reader whether the network is NTK-lazy (in which case criticality claims are trivial) or feature-learning (where they have teeth).
8. **Scaling-relation cross-check.** β, γ measured; test γ = (β − 1)/(α − 1) within bootstrap error. This is the `knowledge_base.md` §2.3 mandatory multi-exponent check.
9. **Architectural control.** ReLU nanoGPT variant (per [Mirzadeh 2024]) as sparsity-decoupling check.

Not all nine are mandatory for a first submission; items 1, 2, 4, 5, 6, 7 are the hard minimum.

## 6. Dependence structure

- **Independent of Candidate 1** (pretrained GPT-2 avalanches) — the pipelines share tooling (`powerlaw`, `mrestimator`) but operate on disjoint models and data.
- **Sibling to Candidate 4** (grokking-phase-transition observables) — Candidate 3 = smooth training on natural language; Candidate 4 = algorithmic task with a known phase transition. Combining these as companion papers is natural but not required.
- **Prerequisite-sharing with Candidate 12** (neutral-null rejection) — if α is the primary observable, the Griffiths / neutral null must be rejected per Candidate 12 methodology. If ρ is primary (recommended), Candidate 12 dependence drops.
- **Feeds into Candidate 2** — if Candidate 3 establishes that σ drifts predictably in training, Candidate 2's σ(n_skip) × training time interaction becomes a natural follow-up.

No hard blocker from other candidates; stand-alone feasible.

## 7. Suggested reframe (required before promote)

1. Specify the init-regime knob explicitly. Recommendation: residual branch scale γ ∈ {γ_crit, 0.5 γ_crit, 2.0 γ_crit}, derived per Hayou-style deep-narrow-residual mean-field.
2. Promote ρ (per-layer Jacobian spectral radius via power iteration) to the primary observable; σ and α as secondary/tertiary cross-checks. State in the pre-registration.
3. Bump seed count to n ≥ 3 per init. Report CIs.
4. Add empirical-NTK-flow as a low-cost "regime" control (feature-learning vs lazy).
5. Name the competitor [arXiv:2511.12768] explicitly in the lit-review section; differentiate on the observable (signal-propagation vs vocabulary-statistics).
6. State choice of dataset: TinyStories is better than Shakespeare-char for this (more diverse, tests generalisation not memorisation), but ~5× the training cost. Accept Shakespeare-char for the scoping run; TinyStories for the confirmation run.

## 8. Verdict

**REFRAME → PROCEED.** The experimental design needs the six points above. With those changes the candidate addresses an open, well-defined gap; the observables are computable on the declared hardware at the declared cost; the falsifier is sharp; the venue fit is clear; and no 2024–2026 preprint scoops the specific question. Promote to Phase 0 after reframe.

**If reframe is not done:** KILL — unfalsifiable in its current loose form because the "critical init" regime is under-specified for a residual-LayerNorm architecture.

---

*Wordcount: ~1420.*

Sources consulted (2024–2026, beyond `papers.csv`): arXiv:2501.04286, 2410.02536, 2506.08523, 2511.12768, 2512.00168, 2412.07386, 2506.05447.
