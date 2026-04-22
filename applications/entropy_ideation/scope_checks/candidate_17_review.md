# Scope check — Candidate 17: Controllable grokking via σ-steering

**Date:** 2026-04-21
**Reviewer:** Phase -0.5 scope-check agent
**Target:** Candidate 17 (`candidate_ideas.md §Candidate 17`). Actively steer the branching ratio σ → 1 during training on modular arithmetic; test whether σ-control accelerates, eliminates, or destabilises grokking. Pitched as the causal complement to Wang 2026 and as "the causal grokking result the field is missing".

**Verdict: REFRAME (leaning KILL of the headline).** The intervention-on-grokking slot is heavily occupied by 2024-2026 work; the specific Jacobian-spectral-radius knob is already implemented as a grokking accelerator by GrokAlign (arXiv:2506.12284). A σ-steering study can still publish, but only as a head-to-head intervention benchmark, not a first-causal-test.

---

## 1. Novelty

### 1.1 The "missing causal test" claim collapses

Between May 2024 and Feb 2026 at least eight papers have intervened on grokking and reported acceleration, elimination, or anti-grokking:

- **Grokfast** (arXiv:2405.20233, NeurIPS 2024) — amplify slow gradient components; >50× speedup on mod-add.
- **NeuralGrok** (arXiv:2504.17243, Apr 2025) — bilevel neural-amplifier; accelerates grokking on mod-arith.
- **GrokTransfer** (arXiv:2504.13292, Apr 2025) — embedding transfer *eliminates* the grokking phase transition.
- **Muon accelerates grokking** (arXiv:2504.16041, Apr 2025) — optimiser swap cuts mean grokking epoch 153→103.
- **⊥Grad / StableMax** (arXiv:2501.04697, Jan 2025) — prevents softmax-collapse; induces grokking without weight decay.
- **GrokAlign** (arXiv:2506.12284, Jun 2025) — **direct scoop.** Jacobian-regularisation on modular arithmetic; 7.56× fewer steps, 6.31× faster than weight decay. Necessary-and-sufficient causal framing under low-rank Jacobian.
- **Geometric Inductive Bias of Grokking** (arXiv:2603.05228, Feb 2026) — architectural ablations (spherical residual stream, uniform-attention) *bypass* grokking; orthogonal-gradient-flow ablation *prevents* it. Explicit causal language.
- **Low-Dimensional Curvature Dynamics** (arXiv:2602.16746, Feb 2026) — orthogonal flow necessary, curvature boosting insufficient, non-commutativity amplification gives ~50 % acceleration.

These collectively cover the three arms:

| Candidate 17 arm | Prior art |
| --- | --- |
| Accelerate grokking | Grokfast, NeuralGrok, Muon, GrokAlign, ⊥Grad |
| Eliminate grokking | GrokTransfer, ⊥Grad, StableMax, spherical residual stream |
| Anti-steer / prevent | Orthogonal-flow suppression (2602.16746), uniform-attention ablation (2603.05228), class-removal (2502.01774) |

### 1.2 The σ-specific framing is a relabel of GrokAlign

Candidate 13 penalises `(σ_ℓ − 1)²` via power-iterated Jacobian spectral radius, i.e. the top singular value of the layer Jacobian. GrokAlign regularises the full Jacobian (centroid alignment). σ-regularisation is a rank-1 projection of GrokAlign's knob. A paper that re-does this with one singular value under statistical-physics branding is a minor scoop-verification, not a field-missing causal test.

The only surviving conceptual move: operationalise σ as the **activation-avalanche branching ratio** via the Wilting-Priesemann MR estimator (Candidate 1 pipeline) rather than Jacobian spectral radius. That is a genuinely different quantity — collective activation-space vs linearised Jacobian sensitivity — and no published work steers activation-level σ during training. But the dependency chain changes: Candidate 17 no longer depends on Candidate 13's JVP-σ; it needs a new differentiable MR-estimator, which is non-trivial (MR estimator is a regression on conditional activation counts; back-prop through it is possible but unproven).

### 1.3 The "causal complement to Wang 2026" framing is occupied

Wang 2026a/b is the passive side. But 2603.05228 and 2602.16746 (Feb 2026) explicitly frame themselves as causal grokking interventions. The "causal result the field is missing" framing was already obsolete at time of writing.

## 2. Specific concerns

### 2.1 Does active steering go meaningfully beyond Wang 2026?

Only if σ is operationalised as activation-avalanche branching ratio, not Jacobian spectral radius. Under Jacobian-σ, GrokAlign already did it. Under activation-σ, a narrow causal slot survives — but see §1.2 for the build cost.

### 2.2 Intervention-on-grokking 2024-2026?

Yes, at least eight papers (§1.1). "Inducing grokking" and "grokking intervention" arXiv searches return all of GrokAlign, NeuralGrok, Grokfast, Muon, ⊥Grad, GrokTransfer, geometric-inductive-bias, curvature-dynamics. The novelty claim cannot survive a Phase-0 lit review.

### 2.3 Is ~3 weeks feasible at n ≥ 30?

Arithmetic: 3 conditions × 30 seeds = 90 runs. Mod-add (p = 97, WD = 1, train-fraction 0.3) groks in ~10⁵ steps, ~10 min per run on RTX 3060. Candidate 13's σ-regulariser is ~2× vanilla (JVP power iteration): so 30 × 20 + 30 × 20 + 30 × 10 ≈ 25 GPU-hours training, plus analysis/pre-reg work. **Feasible at n = 30 on option-C GPU** *conditional on Candidate 13 being stable*. If Candidate 13 needs debugging (and divergence risk under anti-steer is real, §2.4), realistic is 4-5 weeks.

### 2.4 Is the σ-anti-steered (0.7 / 1.3) arm clean?

**No, not as specified.** At σ = 0.7, layer gain <1 across depth — signal dies; on a 2-layer transformer this collapses to under-parameterisation failure, indistinguishable from "too small to learn". At σ = 1.3, activation norms grow exponentially layer-to-layer and *compete directly with LayerNorm*. Two failure modes:

1. Regulariser pushes pre-LN σ to 1.3, LayerNorm erases it — no effective perturbation.
2. Regulariser pushes post-LN σ to 1.3, LayerNorm gain destabilises — training diverges before any grokking window.

Required mitigations (pre-register all):

- **Gentler anti-steer targets**: σ ∈ {0.85, 1.15} on a LayerNorm transformer. σ = 0.7 is unrecoverable.
- **Apply target in pre-LN signal** and report post-LN effective σ.
- **Adaptive λ with divergence-detector**: halt-and-record threshold.
- **Pre-registered outcome classes**: "anti-steered, stable, did not grok" vs "anti-steered, diverged" must be reported separately — not folded into "no grokking".
- **Matched-perturbation baseline** (dropout-matched or WD-matched to match training-loss curvature): separates "training was different" from "σ was different". Without this control, causal inference dies.

### 2.5 Dependence on Candidate 13; viability if it fails?

Candidate 13's kill clauses:

- **"σ_ℓ uncontrollable / training diverges"** — hard kill of Candidate 17. No σ-steering possible.
- **"No λ beats λ = 0 on val-loss at matched compute"** — Candidate 17 can still proceed; σ-steering's effect on *grokking* is separable from its effect on general pre-training val-loss.

Required milestone before committing Candidate 17's 3-week budget: Candidate 13 demonstrates differentiable σ-control on the target 2-layer mod-arith transformer with `|σ_measured − σ_target| < 0.1` for σ_target ∈ [0.85, 1.15] across ≥ 3 seeds. If milestone fails, Candidate 17 cancels.

**Backup plan if Candidate 13 fails outright:** switch σ operationalisation to activation-avalanche MR-estimator (§2.1) and use GrokAlign's published Jacobian-reg library as the intervention knob. Paper becomes "compare Jacobian-reg to activation-avalanche-σ-reg on grokking" — a head-to-head intervention benchmark, not a causality claim.

## 3. Falsifiability

The stated kill ("Mann-Whitney U > 0.05 vs standard") is well-posed only for the steered = target-σ-1 arm. For anti-steer arms it is undefined: is divergence "different grokking step (=∞)" or a separate outcome class? Import Candidate 4's operationalisation discipline wholesale:

- Pre-register t_grokking (logistic-midpoint of val-loss, causal changepoint detection).
- Survival analysis, not Mann-Whitney-on-infinities, for runs that never grok.
- Divergent runs reported as a separate outcome class.
- n = 30 seeds per condition on option-C GPU.

## 4. Venue fit

NeurIPS / ICML main-track was premised on the "causal result the field is missing" framing, which is dead. Realistic under reframe:

- **NeurIPS ATTRIB / ICML MechInterp workshop** — head-to-head benchmark across Grokfast, GrokAlign, Muon, σ-steering on matched seeds. Publishable even if σ-steering merely replicates GrokAlign.
- **TMLR** — "Jacobian spectral radius is a sufficient rank-1 projection of Jacobian alignment for grokking" within GrokAlign framework.
- **Entropy criticality-in-learning special issue** — if activation-avalanche-σ operationalisation is adopted.

Not viable for NeurIPS/ICML main-track as currently specified.

## 5. Required controls

On top of §3 operationalisation pre-registration:

- **GrokAlign-reproduction arm** at matched λ, matched seeds — Candidate 17 must be distinguishable from GrokAlign, else it is scoop-verification.
- **Weight-decay-matched arm** (Power 2022 setup).
- **Dropout-matched arm** — separates "any perturbation shifts grokking" from "σ specifically does".
- **Anti-steer divergence-detector** (§2.4).
- **n ≥ 30 seeds** per condition per Candidate 4 variance floor.

## 6. Recommended reframe

**Kill:** "σ-steering is the missing causal test of criticality-drives-grokking." Scooped by GrokAlign, ⊥Grad, and Feb-2026 orthogonal-flow ablations.

**Reframe as:** *Head-to-head intervention benchmark — Jacobian-spectral-radius σ-regulariser vs GrokAlign Jacobian-alignment vs Grokfast vs Muon vs ⊥SGD vs standard WD — on identical mod-arith seeds with uniform t_grokking operationalisation, n = 30 per arm.*

Primary question: are these interventions empirically redundant or genuinely separable? Secondary question (the surviving causal claim): does the σ-regulariser's effect predict monotonically from `|σ_target − 1|` in a dose-response, as the criticality hypothesis requires?

Deliverable: workshop paper (ATTRIB or MechInterp). Cost ≤ 3 weeks on option-C GPU, conditional on Candidate 13 σ-control milestone being green. If Candidate 13 fails hard, cancel.

Priority: **demote below Candidates 1, 12, 13, 14**; keep above Candidate 19.

---

**Sources consulted:**

- [GrokAlign (arXiv:2506.12284)](https://arxiv.org/abs/2506.12284)
- [Jacobian Alignment Explains Grokking (OpenReview 1l6I2s79iX)](https://openreview.net/pdf?id=1l6I2s79iX)
- [Grokfast (arXiv:2405.20233)](https://arxiv.org/abs/2405.20233)
- [NeuralGrok (arXiv:2504.17243)](https://arxiv.org/abs/2504.17243)
- [GrokTransfer (arXiv:2504.13292)](https://arxiv.org/abs/2504.13292)
- [Muon Accelerates Grokking (arXiv:2504.16041)](https://arxiv.org/abs/2504.16041)
- [Grokking at the Edge of Numerical Stability / ⊥Grad (arXiv:2501.04697)](https://arxiv.org/abs/2501.04697)
- [Geometric Inductive Bias of Grokking (arXiv:2603.05228)](https://arxiv.org/abs/2603.05228)
- [Low-Dimensional Curvature Dynamics in Grokking (arXiv:2602.16746)](https://arxiv.org/abs/2602.16746)
- [Grokking Explained: A Statistical Phenomenon (arXiv:2502.01774)](https://arxiv.org/abs/2502.01774)
- [Wang 2026a (arXiv:2604.16431)](https://arxiv.org/abs/2604.16431); [Wang 2026b (arXiv:2604.04655)](https://arxiv.org/abs/2604.04655)
- Internal: `scope_checks/candidate_04_review.md`; `candidate_ideas.md §Candidate 13`; `knowledge_base.md §2.5`; `lit_ml.md §3`.
