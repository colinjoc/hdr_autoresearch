# Phase -0.5 Scope-Check - Candidate 20

**Candidate.** Architecture-class criticality: dense vs SSM vs MoE.
**Question.** Do dense transformers (GPT-2, Pythia), selective state-space models (Mamba, Mamba-2), and mixture-of-experts (DeepSeek-V2-Lite, Mixtral) land on the same criticality manifold, or cluster into distinct universality sub-classes?
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME.** Keep the dense-vs-SSM axis; drop MoE from the 3060 scope. Narrow the claim from "universality class" to a matched-parameter, matched-data, matched-observable crackling-noise comparison on Pile-300B-trained 1.3-1.4B models. Address event-definition portability upfront or the paper is dead on arrival.

## 2. Observable portability: does the avalanche event definition survive the architecture jump?

Candidate 1's avalanche is layer-axis: residual stream, thresholded activations, contiguous supra-threshold cascade across `attn + MLP + residual` layers. Three reasons this does not transfer cleanly to Mamba:

1. **Mamba has no attention.** Token mixing is a selective SSM, `h_t = A(x_t) h_{t-1} + B(x_t) x_t`. Information flows along the *token axis via the hidden state*, not the *layer axis via QK-OV*. Residual + norm still exist, so a layer-axis avalanche is well-defined - but it is measuring a very different mechanism.
2. **The native avalanche axis in Mamba is token-time.** The SSM is recurrent along tokens; perturb `h_t`, propagate through the recurrence, count downstream hidden dims that cross threshold. Time-axis and layer-axis exponents need not lie in the same universality class even for a critical network.
3. **Lyapunov-stability preempts.** Halloran et al. (2406.00209, TMLR 2025) prove Mamba-1 / Mamba-2 SSM layers have bounded Lyapunov exponents and are empirically stable under perturbations where Transformers diverge. If the *trained-weights* exponent is strictly negative, the SSM time channel is sub-critical *by construction*, and any layer-axis power law reduces to "Mamba layers behave like attention-free transformer layers" - a much narrower result.

**Mitigation.** Report both layer- and token-axis avalanche statistics on every architecture; use the Gu-Dao 2405.21060 structured-semiseparable duality as the formal bridge; pre-register which axis carries the universality claim.

## 3. MoE VRAM and quantisation confound

DeepSeek-V2-Lite: 15.7B total / 2.4B active, BF16 ~40 GB. Mixtral-8x7B: 46.7B total / 12.9B active, BF16 ~90 GB. RTX 3060 12 GB hosts neither. Int4 gets DeepSeek-V2-Lite to ~8 GB (tight w/ kv-cache) and Mixtral to ~23 GB (still does not fit).

Int4 quantisation is *distribution-reshaping*: SmoothQuant / AWQ / QuIP / SpinQuant explicitly flatten heavy-tailed activations to fit the 4-bit grid. These transforms change the threshold landscape the avalanche definition depends on (knowledge_base.md §3.1, §4 "threshold sensitivity"). A measured exponent shift between BF16-GPT-2, BF16-Mamba, and int4-DeepSeek cannot be attributed to architecture without an int4 dense-side control - itself a separate study.

MoE routing is a hard sparsity gate: 6 of 64 (DeepSeek-V2-Lite) or 2 of 8 (Mixtral) experts fire per token. This moves the effective active-unit denominator and will shift `alpha` even for identical dynamics. Also: Pile-trained MoE open-weights of matched 1-2B size do not exist on 2026-04-21 surface, so the matched-data constraint breaks.

**Drop MoE for this paper.** MoE criticality deserves its own candidate on >=24 GB hardware.

## 4. Prior work 2024-2026

- **Gu, Dao 2312.00752 (Mamba)** and **2405.21060 "Transformers are SSMs"** - architecture + SSM-attention duality (the formal bridge).
- **Halloran 2406.00209 (TMLR 2025)** - Mamba / Mamba-2 Lyapunov bounds. Direct prior on "distance from edge of chaos" for SSMs; any criticality paper on Mamba must engage it.
- **"Towards Universality: Mechanistic Similarity Across LM Architectures" (2410.06672)** - Transformer vs Mamba feature similarity via SAEs, *not* criticality exponents. Closest adjacent work; defines the exact gap for Candidate 20.
- **"Sparsity and Superposition in MoE" (2510.23671, Oct 2025)** - MoEs show *continuous* rather than sharp phase transitions, and greater monosemanticity. Suggests the architectural-class distinction may already be established at the superposition level.
- **Ghavasieh 2026 (2512.00168)** (from Candidate 12 review) - activation-function Taylor coefficients tune the universality class. Mamba uses SiLU, GPT-2 GELU, MoE SiLU+softmax gating - even activation-function differences can shift the class.
- **No 2024-2026 paper measures avalanche or crackling-noise exponents on Mamba or on MoE LMs.** Gap is real on the SSM side; real but infeasible on MoE.

Relative to papers.csv: 3039 (Zhang 2022 MoEfication) shows dense FFNs are implicitly expert-structured; 3036/3037/3038 (Li 2023, Mirzadeh 2024, Liu 2023) show dense FFNs are already 75-95 percent inactive per token. The dense-vs-MoE boundary is fuzzier than the brief treats it.

## 5. Falsifiability: pre-registered numerical thresholds

"Same manifold OR distinct sub-classes" is not falsifiable - every outcome is nameable. Fix by pre-registering *quantitative* bounds:

- **Universal (strong)**: `|alpha_dense - alpha_SSM| < 0.05`; crackling relation `gamma = (beta-1)/(alpha-1)` within CI on both; shape-collapse `F(t/T)` matches across classes, chi-squared/dof < 2.
- **Same class, different prefactors (weak universal)**: exponents match within 2 sigma, shape-collapse amplitudes differ. Publishable as "universal exponents, non-universal amplitudes".
- **Distinct sub-classes (positive architectural effect)**: `|alpha_dense - alpha_SSM| > 0.15` (3x seed-variance CI per Candidate 12 §5.3); crackling holds per-class but with distinct `(alpha, beta, gamma)` tuples; cross-class shape collapse fails.
- **One class off-critical**: scaling relation fails in one architecture. Headline: "one architecture is not critical".
- **Kill**: neither passes Candidate 1 / knowledge_base.md §5 minimum bar. No universality claim.

With these numerical thresholds the hypothesis is falsifiable; without them, decorative.

## 6. Matched-parameter, matched-data feasibility

| Family | Sizes | Corpus | VRAM FP16 batch 1 |
|---|---|---|---|
| GPT-2 (OpenAI) | 124M - 1.5B | WebText | fits to 1.5B |
| Pythia | 70M - 12B | Pile, 300B tok | <=1.4B fits |
| Mamba-1 | 130M - 2.8B | Pile, 300B tok | all fit |
| Mamba-2 | 130M - 2.7B | Pile, 300B tok | all fit |

The only clean matched cell is **Pythia-1.4B vs Mamba-1-1.4B vs Mamba-2-1.3B on Pile-300B**. That is the primary comparison. GPT-2 is WebText not Pile - keep only as a secondary "different-data" check. Extending to MoE breaks matched-data (no Pile-trained open-weights MoE at this scale).

## 7. Compute

Inference-only, batch 1, 2-4k tokens, activation caching. Per-architecture on RTX 3060: ~1.0-1.5 GPU-days inference each (selective-scan kernel is compiled for sm_86; Mamba-2 SSD algorithm is Triton, faster than Mamba-1). Three architectures x 1.5 days = ~4-5 GPU-days inference. CSN + bootstrap + crackling + shape-collapse + MR branching + at-init controls = ~1 GPU-week. Token-axis pipeline on Mamba (causal patching on `h_t`) is a new pipeline, ~1 week.

**Realistic total: 3-4 weeks** (matches candidate's 4 weeks) *with MoE excluded*.

## 8. Risks and mitigations

- **Lyapunov theorem preempts a Mamba-subcritical finding.** Halloran 2406.00209 bounds the SSM Lyapunov exponent; measuring it on trained weights is the actual contribution, not the bound itself. *Mitigation*: frame trained-weights Lyapunov measurement on Mamba as the primary token-axis observable.
- **Layer-axis Mamba avalanches may be trivially transformer-like.** Mamba's layer structure is residual + norm + block, i.e. a transformer minus attention. *Mitigation*: acknowledge that the narrower question "does removing attention change `alpha`?" is itself publishable.
- **At-init control for Mamba is non-trivial.** Mamba init is HiPPO-structured, not Gaussian - not a "random network" in the Sompolinsky sense. *Mitigation*: use the published Mamba init as the at-init baseline and document the non-Gaussianity.
- **Activation-function confound (SiLU vs GELU).** Per Ghavasieh 2026 this alone can shift the universality class. *Mitigation*: run a dense SiLU-transformer control (SwiGLU-nanoGPT or a public LLaMA-style small checkpoint). If SiLU-dense is closer to Mamba than GELU-dense, the "architecture" effect is really an activation-function effect.
- **Seed variance.** Pile-trained Mamba-1 and Mamba-2 at 1.3-1.4B have one public seed each; Pythia-1.4B has one. Seed-variance bounds from Candidate 12 §5.3 are not available cross-architecture. *Mitigation*: report point estimates with block-bootstrap CIs on activation samples; explicitly note that *weight-seed* variance is unaccounted for and widen the "distinct sub-class" threshold accordingly (already done: 0.15, 3x typical seed sigma).

## 9. Summary

**Verdict.** REFRAME. Drop MoE. Reframe as "dense vs selective-state-space: cross-architecture crackling-noise comparison on matched Pile-300B-trained 1.3-1.4B models, pre-registered numerical universality thresholds, both layer- and token-axis avalanche observables."

**Rubric.** D = 5 (Pythia + Mamba-1 + Mamba-2 open on Pile, no data problem); N = 4 (first measurement of crackling-noise exponents on an SSM LM; modest if layer-axis only, strong if token-axis included); F = 4 once §5 thresholds are adopted; C = 3 (3-4 weeks, dominated by token-axis pipeline); P = 4 as reframed, 2 as originally stated.

**Action items.**
  (i) Strike MoE / DeepSeek / Mixtral from the primary comparison. Spin out a separate MoE-criticality candidate for >=24 GB hardware.
  (ii) Add the pre-registered quantitative universality thresholds (§5) before Phase 0.
  (iii) Add a SiLU-dense control to separate architecture effects from activation-function effects (Ghavasieh 2026).
  (iv) Commit to both layer-axis and token-axis avalanche observables; cite Gu-Dao 2405.21060 duality as the bridge.
  (v) Engage Halloran 2406.00209 directly; frame trained-weights Lyapunov measurement on Mamba as a primary observable, not a secondary check.
  (vi) Depend on Candidate 1 for the layer-axis pipeline; build the token-axis SSM-state patching pipeline de novo (+1 week; total 3-4 weeks).
