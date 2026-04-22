# Phase -0.5 Scope-Check - Candidate 14

**Candidate.** Criticality-aware initialisation beyond Schoenholz - iterative, batch-conditioned init that measures sigma_l on a batch, adjusts residual-branch scale gamma_l and LayerNorm gain, repeats until sigma_l ~ 1 uniformly across depth. Benchmark against standard PyTorch init, Schoenholz at-init EOC, and muP.
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME, leaning KILL as a standalone contribution.** The iterative-variance-fitting idea is ten years old (LSUV, Mishkin-Matas 2015 / arXiv 1511.06422), the residual-branch-scale knob has been exhaustively explored (Fixup 2019, ReZero/SkipInit 2020, T-Fixup 2020, DeepNet/DeepNorm 2022, Shaped Transformer 2023), the "init so the per-layer criticality observable is unity across depth" framing has a direct 2024 transformer precedent (**Geometric Dynamics of Signal Propagation**, arXiv 2403.02579, *Phys. Rev. E* 2025), and data-dependent gradient-norm tuning at init has been solved by GradInit (Zhu-Ni 2021, ICLR 2022). The free contribution area - "iterate to force sigma_l ~ 1 on a real data batch with LayerNorm gain + residual scale as the knobs" - is a linear combination of LSUV + Fixup + Geometric-Dynamics trainability conditions. Reframe as a methods tool inside Candidate 1 (use iterative-init to generate the off-critical init controls for the at-init-vs-trained-drift comparison), not as an independent benchmark paper.

## 2. Critical prior art missing from the candidate's framing

The candidate-ideas entry cites only Schoenholz [3002] and muP [cited as 3008 but actually 3010 - Yang-Hu 2021; typo also in Candidate 13]. Load-bearing prior art:

- **LSUV - Mishkin-Matas 2015 (1511.06422, ICLR 2016).** Exactly the proposed protocol: pre-init orthonormal, sweep layers front-to-back on a data batch rescaling weights until output variance = 1. Candidate 14 is LSUV with "(gamma_l, LN gain)" substituted for "weight norm".
- **Fixup - Zhang-Dauphin-Ma 2019 (1901.09321, ICLR 2019).** Closed-form rescaling of residual branches to unit signal-variance; trains 10000-layer ResNets. The gamma_l knob.
- **ReZero - Bachlechner 2020 (2003.04887) + SkipInit - De-Smith 2020.** Residual branch scale = single learnable scalar, initialised at zero.
- **T-Fixup - Huang-Perez et al. ICML 2020.** Fixup for transformers: closed-form attention + FFN residual scales; 200-layer transformers without warmup or LayerNorm.
- **DeepNet / DeepNorm - Wang et al. 2022 (2203.00555).** Up-scales residual stream before LayerNorm, down-scales residual-branch parameters at init; 1000-layer transformers. Already optimises the exact (LN-gain, residual-branch-scale) knob-pair.
- **Shaped Transformer - Noci et al. NeurIPS 2023 (2306.17759).** Proportional infinite-depth-and-width limit; critical attention shaping (softmax centred at identity + width-dependent temperature) preventing rank collapse. Analytical prescription for the attention residual critical scaling.
- **Geometric Dynamics of Signal Propagation Predict Trainability of Transformers - 2024 (2403.02579, *Phys. Rev. E* 2025).** The precise claim, already published. Order-chaos phase transition parameterised by attentional and MLP residual-connection strength and weight variance; two Lyapunov exponents (angle, gradient); simultaneous vanishing is necessary and sufficient for trainability; final test loss predicted by these at init.
- **Mapping the Edge of Chaos - 2501.04286, 2025.** Decoder-only transformers show fractal trainability boundaries in (lr, attention-var, FFN-var) space.
- **GradInit - Zhu-Ni 2021 (2102.08098, ICLR 2022) + MetaInit - Dauphin-Schoenholz 2019.** Data-dependent init by explicit optimisation: per-layer weight norms chosen so one SGD/Adam step minimises loss. Transformer experiments; removes warmup.
- **u-muP - Blake et al. 2024 (2407.17465, ICLR 2025).** Unit-scaled muP: activations, weights, gradients initialised and remain at unit variance. Subsumes the proposed criticality init in the unit-variance sense.

## 3. Is muP a competitor? Mechanistic distinction

Yes and no. muP [3010] prescribes (init std x 1/width^a, lr x 1/width^b) so every parameter group's update has equal width-dependence, giving the feature-learning infinite-width limit rather than NTK-lazy. It does *not* target chi_1 = 1 or sigma_l = 1. It targets constant update magnitude - a dynamical criterion.

- Schoenholz EOC: static. chi_1 = 1 at init -> polynomial correlation decay with depth. Second-moment Jacobian.
- muP: dynamical feature-learning. sigma_w^2 ~ 1/fan_in for hidden matrices, lr scaled so activation *changes* are O(1) in width. Silent on chi_1.
- LSUV / u-muP / Fixup / DeepNorm: preserves sigma_l = 1 layerwise at init. Variance-only, no correlation or Jacobian check.
- Candidate 14: sigma_l = 1 on a batch, adjusting gamma_l and LN gain.

Candidate 14's criterion is strictly weaker than EOC (which needs chi_1 = 1), strictly weaker than dynamical isometry (full Jacobian spectrum at 1), and not orthogonal to muP (muP prescribes inits achieving unit-variance forward propagation for specific layer types). On residual+LN, the real critical observable is not sigma_l alone - Geometric Dynamics 2024 uses the angle exponent (inter-token correlation simplex) and gradient exponent (backprop growth). Driving sigma_l -> 1 will not in general set either to zero.

muP is a benchmark axis but not a criticality competitor; Candidate 14 is closer to LSUV + Fixup. A paper benchmarking only "standard, Schoenholz, muP" against iterative init - omitting LSUV, Fixup, T-Fixup, ReZero, DeepNet, GradInit - will be rejected on novelty.

## 4. Wall-cost feasibility of the < 1 % budget

Feasible but trivial. LSUV is O(L) forward passes on one mini-batch, one scalar per layer - << 0.001 % of pretraining. Iterating to tolerance takes ~3-10 outer passes (LSUV reports ~5); still < 0.01 %. GradInit is more expensive (full SGD step per inner iteration); published transformer runs < 1 %. Geometric Dynamics 2024 has zero data-dependent cost - analytical (sigma_w^2, alpha_res) from architecture.

The real question is whether the benefit is measurable above noise. nanoGPT on TinyStories/Shakespeare varies by several percent in final val-loss across seeds. Demonstrating < 5 % init-induced gain requires many seeds and a clean protocol; without that the benchmark has no signal.

## 5. What Candidate 14 could salvage

**(a) Merge with Candidate 1 as a methods ingredient.** Candidate 1 tracks sigma, alpha, rho through training from three init regimes. To define "critical" for residual+LN, Candidate 1 needs a prescription: Schoenholz (unclear for residual+LN), Fixup/T-Fixup (closed-form), Geometric Dynamics 2024 (analytical, transformer-specific), or iterative LSUV-style fit. The iterative fit is defensible because it replaces violated mean-field assumptions (i.i.d. weights, stationary inputs) with an empirically-measured variance profile. Tool inside Candidate 1, not standalone.

**(b) Benchmark pivoted to criticality-observable-transfer across inits.** Not "iterative init beats standard". Run Schoenholz, Fixup, T-Fixup, ReZero, DeepNorm, muP, u-muP, GradInit, and iterative-sigma-fit; measure sigma, chi_1, Jacobian spectrum, Shaped-Transformer angle exponent, Geometric-Dynamics gradient exponent at init; train to fixed compute; measure same observables at convergence; ask which init most closely tracks the trained endpoint per observable. Criticality-observable benchmark, publishable at TMLR.

**(c) Theory.** Derive the iterative-fit fixed point analytically for residual + LN + softmax-attention; compare to Fixup / Shaped-Transformer / Geometric-Dynamics; show where they agree. Extends 2403.02579 with LN gain as explicit knob. Requires free-probability for the softmax Jacobian - hard.

## 6. Kill conditions per reframe

- (a): if iterative fit cannot converge on residual+LN within 10 outer iterations to stable sigma_l, or gives identical trajectories to Fixup/T-Fixup init, drop the iterative fit and use Fixup/T-Fixup as the "critical init" control.
- (b): if all inits converge to within < 5 % relative difference in all criticality observables within the first 10 % of training, "init matters" dies; becomes "init doesn't matter for trained criticality observables" - publishable negative with that framing.
- (c): if LN gain and residual-branch scale collapse to a single effective parameter (LN rescales to unit variance, absorbing one d.o.f.), knob-pair framing collapses; contribution reduces to a Fixup reparametrisation.

## 7. Rubric and action items

**Rubric.** D = 5 (no new data); N = 2 standalone, N = 3 merged (incremental on LSUV + Fixup + DeepNorm + u-muP); F = 3 (< 1 % kill is trivial; val-loss-equality kill is statistically ambiguous at small scale without a seed panel); C = 4 (fit cheap; benchmark needs 8-10 inits x 3 seeds, tractable on RTX 3060 for nanoGPT); P = 2 standalone (subsumed), P = 4 merged / observable-transfer benchmark.

**Action items.** (i) Fix `candidate_ideas.md`: muP is [3010], not [3008]; [3008] is Arora 2019 NTK. Same typo in Candidate 13. (ii) Add to `papers_ml.csv` (IDs ~3056-3064): LSUV, Fixup, ReZero, T-Fixup, DeepNet, Shaped Transformer, Geometric Dynamics 2024, GradInit, u-muP. Minimum: Fixup, DeepNorm, Geometric Dynamics, u-muP. (iii) Rewrite Candidate 14 with one reframe; (a) recommended for compute budget, (b) strongest publishable standalone. (iv) Demote in `promoted.md` from standalone to "tooling for Candidate 1" unless (b) is chosen. (v) If (b): 8-10 inits x 3 seeds = 24-30 nanoGPT runs + init profiling, ~2-3 GPU-weeks on 3060 for Shakespeare-char / TinyStories; fits the 4-week budget but blocks larger Candidate 1 work.

## 8. Summary

Candidate 14 as stated is a reinvention of LSUV with "(gamma_l, LN gain)" substituted for "weight norm", in a niche filled by Fixup / T-Fixup / ReZero / DeepNet (residual-branch-scale), LSUV / u-muP (unit-variance), GradInit / MetaInit (data-dependent-optimisation), and Geometric Dynamics 2024 / Shaped Transformer 2023 (transformer-specific criticality). The combination "iterative, data-driven, residual-branch-and-LN-gain, sigma_l = 1 uniformly across depth" is the gap, but each piece is published. Reframe: merge as tool for Candidate 1 (a), pivot to observables-across-inits benchmark (b), or go theoretical (c). Do not ship as the original "criticality-aware init beats the world" paper.
