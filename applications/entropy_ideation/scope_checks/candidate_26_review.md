# Phase -0.5 Scope-Check - Candidate 26

**Candidate.** Prompt-type modulates σ at inference. Fixed GPT-2 / Gemma-2-2B weights; vary input class (ICL vs non-ICL, CoT vs direct, easy vs hard math, factual vs associative) and test whether σ depends on prompt class. Two-way ANOVA σ ~ prompt-class × layer.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME → PROCEED.** The question - is criticality runtime-elicited by specific inputs rather than a static property of the weights? - is genuinely novel for transformer LMs and has a *direct cited precedent in recurrent networks that the candidate does not engage with* (Magnasco, PNAS 2025 / arXiv:2405.15036). The σ-as-model-property framing in every other candidate (C1, C3, C7, C15, C21) is under-examined, and C26 is the right test. Two structural issues force a reframe: (a) the MR estimator does not converge on one batch of six prompts - per-class sample must be multiplied; (b) the observable must avoid the residual-stream tautology and prompt-length confounds already flagged in cross-review findings. The cleaned version (MR σ on MLP-output activity, per-class trial concatenation, length-matched, reported alongside mean-rate to separate "class moves σ" from "class moves baseline rate") is publishable standalone.

## 2. Prior art on input-conditional criticality (concern a)

**Direct precedent: arXiv:2405.15036 (Magnasco, PNAS 122:10, March 2025) "Input-driven circuit reconfiguration in critical recurrent neural networks."** Not currently in `papers.csv` - **must be added**. A single-layer recurrent net with unitary (critical) weights has its circuitry reshaped by input alone: low-frequency inputs landscape ongoing activity into regions that support or suppress traveling waves, so fixed weights implement different effective circuits for different inputs. That is exactly the claim C26 wants to make for transformers. Positioning: Magnasco 2025 established input-driven reconfiguration in a hand-designed critical RNN; C26 tests whether a trained-from-data transformer LM shows the same effective-dynamics modulation, measured as σ(prompt-class). Novel because (i) system differs (trained LM vs hand-designed RNN) and (ii) observable differs (σ vs wave propagation).

**Adjacent but non-scooping:**
- arXiv:2405.17391 (Katsnelson-Vanchurin 2024) "Dataset-learning duality and emergent criticality" - criticality from data distribution at *training* time; different observable.
- arXiv:3038 Deja Vu (Liu 2023), arXiv:3036 (Li 2023) lazy-neuron, and 2025 follow-ups (JENGA USENIX ATC 2025, Grasp DAC 2025, arXiv:2507.14179 activation-pattern clustering) show contextual sparsity *is* prompt-dependent. These establish that *something* in activity statistics is prompt-dependent, but σ has not been asked.
- arXiv:2501.00070 (Park et al., ICLR 2025) "In-context learning of representations" - sudden reorganisation of concept representations with context size; geometry change with prompt type is known.
- Olsson 2022 [3024] induction heads, Wang 2023 [3025] IOI, Todd 2024 / Hendel 2023 function vectors, Ren 2024 semantic induction heads - different prompt classes engage different sparse circuits. That is "which circuit fires", not "what is the branching ratio of whichever circuit fires"; C26 sits at a different abstraction level.
- Bellay-Plenz 2015 [1012], Hahn 2017 [1015] - state-conditioned avalanche analyses exist in cortex (up/down, awake vs anaesthesia). C26 is the LLM-side analogue.

**Conclusion.** Gap is real. No 2024-2026 paper measures σ(prompt-class) on a fixed-weights trained transformer LM. Magnasco sharpens rather than dissolves the claim - reposition C26 from "reframes the entire programme" to "empirically tests the Magnasco input-driven-reconfiguration principle in trained LLMs." Representation-geometry literature (Zavatone-Veth 2022 [3048], Olsson 2022 [3024], Wang 2023 [3025]) overlaps on *geometry changing with prompt type*; cite as "geometry known to change with prompt type, but branching ratio has not been measured."

## 3. Can σ be computed on a single batch of K prompts? (concern b)

**No, not with the naive recipe.** The MR estimator (Wilting-Priesemann 2018 [1019]; mrestimator Spitzner 2021 [1036]) fits A(k) ∝ m^k on autocorrelation over lags k = 1 ... k_max. Published cortical recipes use 10^4-10^6 time steps per session; the mrestimator documentation warns of substantial bias below ~10^3 correlated observations; Wilting-Priesemann's short-trial analysis gives an analytical bias already meaningful at ~500 steps with large CIs. One prompt yields ~10^2-10^3 tokens - inadequate. **Required: trial concatenation within class.** K prompts × T tokens treated as K trials (`coefficients=trialseparated`), effective sample K*T per class. Priesemann-quality σ CIs of ±0.02 need K*T on the order of 10^4-10^5 per class. For T ≈ 512 this is K ≈ 50-250 prompts per class. **The candidate's "K ≈ 6" is the *number of classes*, not per-class sample; phrasing is ambiguous - assume K_class ≥ 100.** 100 × 6 × 512 on GPT-2 small (768 resid / 3072 MLP × 12 layers) or Gemma-2-2B is a day or two of inference on an RTX 3060. Feasibility fine; spec must be tightened.

**Residual-stream caveat (cross-review finding 1).** σ on the raw residual-stream is trivially ≈ 1 because h_{ℓ+1} = h_ℓ + F_ℓ(h_ℓ); use F_ℓ (MLP or attention output). Because C26 rests on *inter-class differences*, the trivial-σ residual stream would make every class's σ look the same for the wrong reason. Pre-register MLP-output / attention-output streams; residual-stream only via causal path-patching σ per Elhage 2021 [3023].

## 4. Representation-geometry overlap (concern c)

**Overlap partial, non-fatal, engage explicitly.** Zavatone-Veth 2022 [3048] (analytical, Bayesian linear nets) sets the methodological bar: a σ(prompt-class) claim must clear a random-feature null with prompt-matched input statistics. Olsson 2022 [3024] implies σ_{ICL} may differ from σ_{non-ICL} simply because different heads engage; without a mechanistic decomposition, any σ gap is uninterpretable. Wang 2023 IOI [3025] (26 of 144 heads for one task) means factual/associative/IOI prompts engage different sparse subsets; per-head σ distribution (**C28**) is the within-circuit counterpart. **Bundle C26 with C28 in presentation**: C26 asks "does σ depend on prompt class at whole-layer level?"; C28 asks "is per-head σ distribution heterogeneous?"; together they localise the effect. **C27** (ICL emergence at σ=1 in training) is the training-time counterpart; co-promote.

No paper in the 209-citation set combines (σ) × (prompt-class conditioning) × (trained LLM). Gap is real; C26 occupies it.

## 5. Two-way ANOVA sample support (concern d)

**Adequate if sample-unit is defined correctly, marginal if treated naively.** Model σ ~ prompt-class × layer = J = 6 × L = 12 = 72 cells. Legitimate replicate unit is the bootstrap σ per cell (not per-token or per-prompt - those are autocorrelated within a trial). With 100 prompts × 512 tokens concatenated to one σ per (class, layer) with block-bootstrap CI, the right analysis is a weighted ANOVA / random-effects meta-analytic model using inverse-CI^2 weights. Priesemann MR bootstrap SDs for σ at ~10^4 observations are typically 0.005-0.02. Effect detectability is (inter-class SD in σ) / (within-cell bootstrap SD). If true inter-class SD < 0.01, the design detects nothing; if > 0.05, it detects at high power. **The load-bearing uncertainty is the effect size** - without a pilot the study risks a false-negative publication. **Mandatory Phase 0 pilot: 2 classes × 3 layers on GPT-2 small (~1 day), gate on inter-class SD > 3× bootstrap SE before running the full 6 × 2 × 12 grid.** The naive per-prompt-σ alternative (n = 100 per class) is inadequate: single-prompt short-trial σ has SE > 0.1, washing out realistic effects.

## 6. Confounds to pre-register

1. **Prompt length.** Longer prompts reduce short-trial bias, shifting σ. Match median-token-length ± 10 %.
2. **Class baseline rate.** CoT elicits longer completions / lower per-token mean activation than direct answers; σ can track rate not branching. Report mean-activation-rate per class. If σ correlates with rate (r > 0.7), weaken claim to "activation statistics are input-conditional" (already established by Deja Vu).
3. **Class-identity permutation null.** Shuffle class labels across prompts, re-fit ANOVA. p must stay < 0.05.
4. **Inference mode.** Fix teacher-forcing on held-out corpus; do not mix with autoregressive generation.
5. **Residual-stream tautology** (§3). Pre-register MLP/attention output.
6. **Tokeniser confound.** Math vs factual prompts have different token distributions; rare tokens elevate MLP activity. Match vocab-frequency or report vocab-matched control.

## 7. Reframe

Refined: "σ(prompt-class) on fixed-weights GPT-2 small and Gemma-2-2B: empirical test of input-driven criticality in trained transformer LMs (arXiv:2405.15036 analogue)." Primary observable σ via mrestimator on MLP-output; secondary causal-σ via path-patching. K_class ≥ 100 prompts × T = 512 tokens, trials concatenated. Report σ_{class,layer} with block-bootstrap CIs plus mean-rate per class. Weighted two-way ANOVA + class-label permutation null. Pilot-gated. Length ± 10 %, MLP substrate, class-rate report pre-registered. Natural home: **new standalone paper - "Input-driven criticality in trained LLMs"** - presented alongside C27 (training-time) and C28 (per-head distribution). Could slot as §7 of Paper 1 if standalone framing underwhelms, but the claim deserves its own venue.

## 8. Rubric

D = 5 (pretrained weights + prompts free). N = 4 (Magnasco precedent in RNN; no LLM precedent; C27/C28 complements, not competitors). F = 3 (σ, mean-rate confound, permutation null, bootstrap, pilot). C = 4 (~3 weeks with pilot). P = 3 standalone (*ICML MechInterp*, *NeurIPS ATTRIB*, *TMLR*); P = 4 if co-submitted with C27 as joint "input-driven + training-time" paper to NeurIPS main.

**Composite: PROCEED as reframed standalone paper**, with Magnasco 2025 added to papers.csv, pilot mandatory, MLP substrate pre-registered, co-presentation with C27 + C28 planned.

## 9. Action items

1. Add **arXiv:2405.15036 (Magnasco, PNAS 122:10, 2025)** to `papers.csv` - framing precedent, currently missing.
2. Add **arXiv:2405.17391 (Katsnelson-Vanchurin 2024)**, **arXiv:2501.00070 (Park et al. 2025 ICLR)**, **arXiv:2507.14179 (activation-pattern clustering 2025)** as adjacent-but-non-scooping context.
3. Edit `candidate_ideas.md` C26: clarify K ≈ 6 is class count; add "K_class ≥ 100 prompts, trial-concatenated"; change observable to "mrestimator MR on concatenated MLP-output activity per class × layer, block-bootstrap CI"; add pilot clause (2 classes × 3 layers on GPT-2 small, gate on inter-class SD > 3× bootstrap SE); add §Confounds listing items 1-6 of §6.
4. Update `promoted.md` C26 row: natural home "**new paper - input-driven criticality**"; propose co-presentation with C27 and C28. Do not bundle into Paper 1.
5. Pre-register kill criterion in Phase 0: "permutation-null ANOVA p > 0.05 AND inter-class SD in σ < 0.02 AND class-σ tracks class-mean-rate (r > 0.7)". Negative result under this tighter test is itself publishable - it falsifies input-driven criticality for trained LLMs and strengthens the static-property framing assumed elsewhere in the programme.
