# Phase -0.5 Scope-Check - Candidate 23

**Candidate.** DFA of LLM residual-stream activation time series. Test alpha_DFA ~ 1 (1/f / long-range temporal correlation, LRTC) per layer on GPT-2, Pythia-1.4B, Gemma-2-2B with at-init control. Anchors: [1023: Linkenkaer-Hansen 2001], [1032: Meisel 2017].
**Reviewer.** Phase -0.5 sub-agent, 2026-04-21.

---

## 1. Verdict

**REFRAME, leaning PROCEED-as-bundled.** C23 is low-cost, well-motivated, with a real 2024-2026 novelty window, but standalone it is a single-exponent paper that violates the knowledge-base rule against single-exponent criticality claims (kb §4, lit-review Pitfall 2). Promote **as the temporal-observable arm of a bundled C23+C24 short paper** (DFA + 1/f spectrum on the same activation cache). Standalone it is workshop-tier and invites "why not also the spectrum?" reviewer questions; bundled, it is a legitimate two-axis cross-check of the same LRTC hypothesis.

## 2. Novelty (2024-2026 gap)

arXiv + web searches ("detrended fluctuation transformer", "DFA neural network activations", "long-range temporal correlation LLM", "Hurst exponent transformer residual stream") return **zero published papers computing DFA on trained transformer activations**. Nearest adjacencies:

- **arXiv:2512.00168 "Tuning Universality in Deep Neural Networks"** (Ghavasieh 2025). Avalanche universality classes on random deep MLPs from activation-function Taylor coefficients; cross-sectional, not DFA/LRTC, not trained transformers. Broader criticality-in-DNNs cell is live; DFA cell is empty.
- **MDPI Fractal Fract. 10:224 (2025)** "DFA complements spectral features in characterizing functional brain aging" - EEG; directly supports §7 complementarity argument.
- **arXiv:2604.09716 (Apr 2026)** "Training Deep Visual Networks through Dynamical Systems" - uses integration / metastability / stability scores on CNNs + ViT on CIFAR; direct inspection confirms no DFA. No collision.
- None of 209 entries in `papers.csv` claim a trained-transformer DFA.

Gap is real but narrow. A competent group with a cached Pythia activation dump could publish this in ~4 weeks; prioritise bundle-with-C24 + fast preprint.

## 3. Falsifiability

Pre-registered kill ("alpha_DFA within 0.05 of 0.5 or 1.5 across all layers and bases") is correctly oriented but weaker than the kb bar. Tighten:

1. Positive: alpha_DFA in [0.7, 1.3] on >=2 bases (raw + SAE) on >=2 models, bootstrap CI excluding 0.5, shuffled-token surrogate in [0.45, 0.55].
2. Negative: alpha_DFA CI overlaps 0.5 across bases / layers / models.
3. Basis-sensitive (raw shows LRTC, SAE does not, or vice versa) is a distinct, publishable outcome per kb §3.1 - anticipate it explicitly.
4. **Alpha-beta internal consistency gate** (links C23 to C24): for stationary signals, beta_1/f = 2 alpha_DFA - 1. A failed relation flags non-stationarity and demands multi-fractal follow-up. As written, the kill is passable by a weakly auto-correlated signal (alpha = 0.6) that does not support the LRTC claim.

## 4. Venue fit

- Workshop (MechInterp / SciForDL / Re-Align): clears easily.
- *Entropy* / *Neural Computation* / *PRX Life* short paper: clears only bundled with C24 and ideally with the existing `~/entropy/` branching-ratio pipeline. Standalone invites "why only time domain?".
- NeurIPS / ICLR main track: does not clear alone - no interpretability / capability hook.

Candidate's stated target (*Entropy* / workshop) is honest; do not promote to a main-conference target.

## 5. Controls

Candidate's listed controls (at-init, shuffled-token, block-bootstrap, threshold independence) are correct but incomplete. Required additions:

| Gap | Required addition |
|---|---|
| At-init only | Also report at 1%, 10%, 100% Pythia checkpoints to show trajectory |
| Shuffled-token | Plus phase-randomised surrogate (Theiler 1992) to separate linear from non-linear structure |
| Block length | Must be >= decorrelation time - measure first |
| Threshold independence | Irrelevant to DFA (threshold-free on continuous signals); replace with **basis independence** (raw vs SAE vs PCA vs random projection) |
| Window range | Pre-register n in [16, N/4]; Hardstone 2012 methods-paper bar |
| Detrending order | Run DFA-1, DFA-2, DFA-3; if alpha drops > 0.1 between orders, signal has a polynomial trend, not genuine LRTC |
| Crossover | LRTC requires alpha stable across >= 1.5 decades; if alpha is large at small n then drops at large n, we measured short-range AR, not LRTC |
| Model-size control | Three-model ladder (124M, 1.4B, 2B) is reasonable, but Gemma-2 RMS-norm / rotary-embed differences from Pythia's learned-absolute-pos make cross-architecture claims non-trivial - tie primary claim to within-architecture replication |

Missing controls are not optional - Hardstone et al. 2012 (Front. Physiol. 3:450) lists them as the DFA-methods bar. Omission is a desk-reject risk at *Entropy*.

## 6. DFA on autoregressive token sequences vs cortical spike-rate time series

Partially well-defined; three latent confounds:

1. **Sampling regime.** Cortical DFA works on amplitude envelopes of narrow-band oscillations (alpha 8-13 Hz), quasi-stationary filtered signals from a homogeneous population. Transformer activations on AR generation are **closed-loop** (each token's activation partly reflects prior tokens' embeddings), not passive recording. The "time" axis is a generation axis, not physical time.
2. **Non-stationarity.** Natural text activations are non-stationary across topic shifts / sentence / document boundaries. DFA-2 or DFA-3 needed; DFA-1 conflates slow topic drift with genuine LRTC and over-estimates alpha.
3. **Bounded amplitude.** Post-LayerNorm residual-stream is L2-normalised per token - bounded, unlike cortical data. Pre-LN is unbounded but grows super-linearly with depth. Pre-register basis; report both if feasible.

**Recommendation:** primary claim restricted to residual-stream activations on **Pile natural (non-generated) text** as model input. AR-generation DFA is secondary only, confounded by closed-loop dynamics.

## 7. Relation to C24 (1/f spectrum)

Complementary in principle, partially redundant in yield. For a stationary signal with S(f) ~ 1/f^beta:

    beta = 2 alpha_DFA - 1

So alpha=1 <-> beta=1 (pink); alpha=0.5 <-> beta=0 (white); alpha=1.5 <-> beta=2 (Brownian). On perfectly stationary signals they are one degree of freedom and one is redundant.

They diverge when: (a) signal is non-stationary - DFA is robust to polynomial trends, periodograms inherit leakage; alpha - 0.5 and beta/2 disagree and the gap is diagnostic. (b) crossovers exist - DFA exposes them via log-log slope; spectrum folds regimes into one fit unless bandpass-decomposed. (c) signal is bounded / normalised - post-LN residual stream violates spectral-fit stationarity differently from DFA detrending.

The 2025 MDPI paper reports alpha-beta disagreements > 0.2 on cortical data - complementarity is real in our exact regime.

**Conclusion:** execute C23 and C24 on the **identical activation cache and co-report** as a single bundled paper. Separate runs yielding alpha=0.95 and beta=1.5 would force a third reconciliation run; joint execution answers this in the first pass. Treat (alpha, beta) as the observable, not alpha alone.

## 8. Statistical power

Adequate but non-trivial; pre-flight pilot required.

1. **DFA bias at short N** (Weron 2002): alpha bias ~0.05 at N=2^10, ~0.01 at N=2^15 for fGn ground truth. 1e5 tokens ~= 2^17, safely low-bias *per time series*.
2. **Per-layer d = 768-2560 neurons** inflates multiple-comparison risk - report per-layer alpha *distribution*, not per-neuron p-values.
3. **Decorrelation time.** Attention induces correlations over 1-2k tokens. If decorrelation ~200 tokens, effective N on a single 1e5-token stream is ~500 and DFA bias becomes non-negligible. Measure autocorrelation decay first.
4. **SAE inflates d 8-32x** - Gemma-Scope SAE DFA is ~10x raw-neuron compute.
5. **Block-bootstrap CI** (block ~= decorrelation time, 1000 replicates): typical alpha CI +/- 0.03-0.05 - discriminates alpha=1 from alpha=0.5, not alpha=1.0 from alpha=1.1.

**Pre-flight:** pilot on GPT-2 124M with N in {1e4, 3e4, 1e5, 3e5}; confirm alpha_DFA stabilises. Pre-register pilot + scale-up rule.

## 9. Dependence

- Depends on: caching pipeline from Paper 1 (assumed live); public pretrained weights (HuggingFace); Gemma-Scope / SAE-Lens SAE bases (public). No custom training.
- Does not depend on: avalanche / branching-ratio pipeline (useful companion, not prerequisite).
- Couplings: **strong with C24** (bundle required); moderate with C25 (alpha feeds the TRG flow); weak with C18 (one cell of the universality-class table).

## 10. Rubric

- D (data): 5 - inference only on public weights + Pile + public SAEs.
- N (novelty): 3 - real gap, narrow window, adjacent 2512.00168 covers broader space.
- F (falsifiability): 3 as written / 4 with §3 and §5 tightening.
- C (cost): 5 bundled / 4 standalone - ~3 weeks inference-only for the bundle.
- P (publishability): 2 standalone / 4 bundled - *Entropy* or a co-branded Paper 1 section as the (alpha, beta) pair with at-init + training-step controls.

**Composite: PROCEED as temporal-observables arm of bundled (C23 + C24) short paper.** Budget 3 weeks for bundled execution + missing controls + stationarity / closed-loop sanity checks.

## 11. Action items

1. Merge C23 + C24 in `candidate_ideas.md` as "Temporal correlation signatures of trained transformers: DFA + 1/f spectrum". Keep both sub-observables explicit.
2. Add six controls from §5: window-range pre-registration, DFA-1/2/3 order comparison, crossover analysis, phase-randomised surrogate, pre-LN vs post-LN basis, checkpoint trajectory.
3. Tighten kill axes per §3: raise CI bounds to +/- 0.1, require multi-basis replication, add alpha-beta internal-consistency gate.
4. Pre-register power pilot per §8.
5. Restrict primary claim to Pile natural-text activations (§6); AR-generation DFA secondary only.
6. Cite **arXiv:2512.00168 (Ghavasieh 2025)** as adjacent-distinct baseline and **Hardstone et al. 2012** (Front. Physiol. 3:450) as the DFA-methods anchor alongside [1023, 1032].
7. Move C23 from standalone to "Paper 1 temporal-observables section" or to a bundled C23+C24 short-paper slot in `promoted.md`.
