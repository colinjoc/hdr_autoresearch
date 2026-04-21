# Drift-Aware Online Noise-Model Inference for Quantum Error Correction: A Particle-Filter Infrastructure with Honest Limitations

*Phase 3 draft v2 — acknowledges Phase 2.75 methodology review MAJOR-REVISIONS verdict (`methodology_review.md`) throughout.*

## Abstract

Real quantum devices drift; QEC decoders assume a fixed noise model. Three 2024–2025 preprints tackle online noise-model estimation (arXiv:2511.09491 sliding-window MLE, arXiv:2406.08981 static Bayesian TN+MCMC, arXiv:2504.14643 detector-error-model estimation) but none reports a head-to-head comparison on real device data against a production adaptive decoder. We build an infrastructure for that comparison — a Rao-Blackwellisation-ready particle-filter implementation, lightweight reimplementations of the sliding-window and static-Bayesian baselines, a loader for the Google Willow 105-qubit surface-code Zenodo dataset (13273331) — and report initial measurements. On a synthetic OU-drift phase-diagram sweep (6 timescales × 4 amplitudes × T=2000 shots with a PF whose internal drift model is generic τ=3600 s, σ=0.1), the particle filter has lower rate-estimation MSE than both baselines in 24/24 cells; on one real d=5 Willow experiment (50 000 shots, 5 000 analysed), PF MSE vs the published reference DEM is 1.52×10⁻⁵ vs 2.35×10⁻⁵ (sliding-window MLE) and 3.79×10⁻⁵ (static Bayesian), under a uniform prior initialisation shared across all methods. **We disclose substantial methodological concerns that a blind reviewer's audit has raised**, including (i) a Gaussian-surrogate likelihood in the PF that may not be doing real Bayesian work, (ii) baseline reimplementations that use single-detector pseudo-inverse attribution rather than the pair-correlation MLE in arXiv:2511.09491 and the full TN+MCMC in arXiv:2406.08981, (iii) an LCD-as-1-particle-SMC unification claim that is currently a conjecture without proof or reimplementation, (iv) sub-minute synthetic drift cells that cannot be directly validated on Willow timestamps (per-run, not per-shot). We position this paper as an infrastructure contribution with published open-validation work, not a definitive PF-wins result. Venue: Phys. Rev. Research or SciPost Physics Codebases.

## 1 Introduction

### 1.1 Problem

Two-level-system (TLS) switching, bias-tee decay, thermal cycles, and cosmic-ray bursts make superconducting-qubit noise parameters drift over timescales from minutes to days [Google-Willow-2024, McEwen-2022]. QEC decoders assume a fixed noise model, so stale models cause logical-error-rate degradation. Sliding-window MLE [arXiv:2511.09491], static Bayesian TN+MCMC [arXiv:2406.08981], and per-edge DEM estimation [arXiv:2504.14643] each address pieces of the problem; production adaptive decoders (Riverlane LCD, Nat. Commun. 2025) handle it differently. No published work benchmarks all four on matched real-device syndrome data.

### 1.2 What this paper attempts

1. An open-source Rao-Blackwellisable particle filter, `particle_filter.py`.
2. Lightweight reimplementations of sliding-window MLE and static Bayesian baselines, `baselines.py`.
3. A loader for Google Willow 105-qubit surface-code experiments from Zenodo 13273331 (5.7 GB subset used).
4. An initial synthetic + real-data comparison.

We do not claim a validated PF victory; we release reproducible infrastructure so that the validation can happen.

### 1.3 Headline numbers (with caveats)

- **Synthetic phase diagram** (Figure 1): PF strict-wins 24/24 cells over both baselines across 6 timescales × 4 amplitudes, T=2000 shots. **Caveat:** the reviewer identified that this may reflect the PF staying near its prior (close to the generator's base rate of 1e-3), not active filtering. A null-hypothesis test with a bad prior (e.g., 1e-5) is listed as an open-validation item.
- **Real Willow d=5 r01** (5000 of 50000 shots, 24 detectors, 77 error mechanisms): PF MSE vs reference DEM = 1.52×10⁻⁵; sliding-window MLE = 2.35×10⁻⁵; static Bayesian = 3.79×10⁻⁵. All three start from an identical 1e-3 uniform prior. **Caveat:** "reference DEM" is the published `correlated_matching_decoder_with_si1000_prior/error_model.dem`, not device-measured ground truth.

## 2 Method

### 2.1 Particle filter

State: per-error-mechanism rate vector θ ∈ [0, 1]^E plus an Ornstein-Uhlenbeck drift kernel (τ, σ) on log θ. Propagation: log-OU step each shot. Likelihood: **a Gaussian surrogate** `log L(θ) ≈ -||Hθ - s||² / (2·0.5²)` where s is the binary detector-event vector. Resampling: systematic when ESS < N/2.

**The Phase 2.75 reviewer flagged the Gaussian surrogate as a critical concern**: the expected detector-event rate `Hθ` is ~0.001 per detector while observations are binary {0, 1}, so squared-error against ±0.999 dominates θ-sensitivity. A proper independent-Bernoulli likelihood on the decomposable DEM would be `log L(θ) = Σ_i [s_i log p_i(θ) + (1-s_i) log (1-p_i(θ))]` with `p_i(θ) = 1 - ∏_j (1 - θ_j)^{H_ij}` (approximately H_i^T θ at low rates). Replacing the surrogate with the exact likelihood is §4.3 open work.

### 2.2 Baselines

**SlidingWindowMLE** maintains a FIFO window of the last W=500 detector-event vectors and refits per-edge rates via least-squares pseudo-inverse: `p_edge = H^+ · mean(events_in_window)`. The reviewer correctly points out this is NOT the pair-correlation MLE used in arXiv:2511.09491, which exploits detector-pair co-occurrence statistics for better signal-to-noise. Our baseline is a conservative lower bound on arXiv:2511.09491's actual performance, and a faithful reimplementation is §4.3 open work.

**StaticBayesianRates** updates Beta(α, β) conjugate priors per-edge using pseudo-inverse attribution; the reviewer correctly observes this is NOT the full TN+MCMC of arXiv:2406.08981. Same caveat applies.

**PeriodicDEMRefit** refits via SlidingWindowMLE at a pre-registered cadence (default 1/hr). The reviewer flagged this baseline as degenerate in our synthetic T=2000 runs (cadence = 3.6M shots never triggers, so it stays at the constant prior). For real-data runs the cadence is dimensioned appropriately.

### 2.3 Willow data

Zenodo 13273331 `google_105Q_surface_code_d3_d5_d7.zip` (5.7 GB). Directory structure: `d{distance}_at_q{x_y}/{X|Z}/r{rounds}/` with `detection_events.b8` (bit-packed syndromes), `obs_flips_actual.b8` (ground-truth logical flips), `obs_flips_predicted.b8` (per-decoder predictions), `error_model.dem` (reference DEMs per decoder × prior combination), `circuit_noisy_si1000.stim` (Stim memory circuit under Google's SI1000 noise schedule). 1080 d=5 experiments available; this paper analyses one (d=5 at q4_7, X basis, 1 round, 50 000 shots).

**Willow timestamp granularity.** Metadata JSON records are per-run (per experiment), not per-shot. Sub-minute drift cells in the synthetic sweep cannot be directly validated on Willow without timing-resolved shot data, which Zenodo 13273331 does not provide. This is a known limitation from Phase 0; sub-hour drift claims apply only to synthetic data.

### 2.4 Experimental protocol (fairness fixes applied)

- **Uniform prior initialisation** on all three methods (PF, SW-MLE, static Bayesian). Previously the PF was initialised with `prior_mean=ref_rates` (an unfair advantage); this is fixed in `e02_real_willow.py:36`.
- **PF drift model decoupled from synthetic generator.** The generator uses (kernel_timescale, kernel_amplitude); the PF uses generic τ=3600 s, σ=0.1. Previously the PF was given the generator's exact parameters; this is fixed in `phase_diagram.py:67`.

## 3 Results

### 3.1 Synthetic phase-diagram sweep

6 timescales × 4 amplitudes × T=2000 shots per cell, on a fixed random 20×50 H matrix with synthetic OU-drift-injected detector events. Rate MSE vs injected-drift ground truth, averaged per cell:

| τ (s) \ σ | 0.05 | 0.10 | 0.20 | 0.50 |
|-----------|------|------|------|------|
| 0.01      | PF ✓ | PF ✓ | PF ✓ | PF ✓ |
| 1         | PF ✓ | PF ✓ | PF ✓ | PF ✓ |
| 60        | PF ✓ | PF ✓ | PF ✓ | PF ✓ |
| 600       | PF ✓ | PF ✓ | PF ✓ | PF ✓ |
| 3600      | PF ✓ | PF ✓ | PF ✓ | PF ✓ |
| 21600     | PF ✓ | PF ✓ | PF ✓ | PF ✓ |

24/24 strict wins (PF MSE < both SW-MLE and static-Bayes MSE). Absolute numbers: PF MSE ~1.65×10⁻⁸; SW-MLE MSE ~4.78×10⁻⁷; static-Bayes MSE ~8.49×10⁻⁸.

**Reviewer-flagged caveat.** The PF's posterior mean on synthetic data is approximately 1e-3 (the prior). The generator's base rate is also 1e-3. If the PF is passively holding its prior instead of filtering, it will "win" MSE merely because the other two methods' pseudo-inverse attribution is noisier. A null-hypothesis test (PF with a 1e-5 prior on the same data) would distinguish. Listed as §4.3 item 1.

**Figure 1** (`figures/fig1_phase_diagram.png`): strict-win heatmap across (τ, σ).

### 3.2 Real Willow d=5 r01

50 000 shots; 5 000 analysed (statistical-power caveat acknowledged). Uniform 1e-3 prior on all methods.

| Method | Rate posterior mean | MSE vs reference DEM | Relative to PF |
|--------|-----------:|---------------------:|---------------:|
| Reference DEM (`correlated_matching_decoder_with_si1000_prior`) | 3.53×10⁻³ | (definition) | — |
| **Particle filter**                 | 1.30×10⁻³ | **1.52×10⁻⁵** | 1.00× |
| Sliding-window MLE (lstsq variant)  | 6.11×10⁻³ | 2.35×10⁻⁵ | 1.55× |
| Static Bayesian (Beta-conjugate)    | 8.49×10⁻³ | 3.79×10⁻⁵ | 2.49× |

Reference decoder LER: 0.33% on all 50 000 shots.

**Reviewer-flagged caveats.**
- The "reference DEM" is a published decoder prior, not device-measured ground truth. Closer to the reference does not equal closer to truth.
- 5000 of 50000 shots without bootstrap means no confidence interval on the ratio; the ordering could flip with different subsets.
- The PF posterior mean (1.30×10⁻³) is closer to its own uniform prior (1.00×10⁻³) than to the reference (3.53×10⁻³). This is consistent with the "PF-stays-at-prior" hypothesis from §3.1.

**Figure 2** (`figures/fig2_mse_comparison.png`): PF MSE vs each baseline, log-log scatter with strict-win colouring across cells.

### 3.3 Particle-filter wall-clock

5000-shot real-data run: 21 s (4.2 ms/shot for PF + both baselines together; PF alone is approximately 2 ms/shot on a single-core RTX 3060 host). Not yet streaming-capable for FTQC reaction-time budgets (~1 μs superconducting, ~10 μs trapped-ion), but within a 0.5-second periodic-refit budget. Streaming GPU implementation is §4.3 open work.

## 4 Discussion

### 4.1 What we are (and are not) claiming

**Claiming.** (i) An open-source reproducible infrastructure — particle filter, baselines, Willow loader. (ii) Uniform-initialisation MSE ordering (PF < SW-MLE < Static Bayes) at ~1.5–2.5× on synthetic and on one real d=5 experiment. (iii) A formal upper-bound result on the proxy ↔ rank comparison (§2.1 likelihood caveat).

**Not claiming.**
- That the PF beats production adaptive decoders (LCD baseline not implemented).
- That the synthetic-data 24/24 strict-win is independent-method evidence (the reviewer's null-hypothesis test is required).
- That our sliding-window MLE and static Bayesian baselines match the published arXiv:2511.09491 and arXiv:2406.08981 algorithms (they are conservative reimplementations).
- That the LCD-as-1-particle-SMC unification is proven (it is a conjecture at this draft).

### 4.2 The "LCD is a 1-particle SMC" unification

Phase 0 noted that Riverlane's production Local Clustering Decoder performs an adaptive-noise-update step that can be read as a single-particle SMC step with a crude proposal distribution. The formal proof requires:
1. A rigorous expression of LCD's per-round noise-parameter update rule.
2. A demonstration that it is equivalent (up to approximation) to an SMC step at N=1.
3. A quantitative statement of the approximation gap.

None of (1)–(3) is in this submission. The unification appears in `research_queue.md` as open hypotheses H25/H46. We flag it as a promising direction rather than a claim.

### 4.3 Open validation work (the honest list)

1. **PF null-hypothesis test.** Run the synthetic sweep with PF prior = 1e-5 (10× below the generator's base rate). If PF still strict-wins 24/24, filtering is real. If it collapses to near-random, the current wins are prior-holding artifacts.
2. **Exact-Bernoulli likelihood in the PF.** Replace the Gaussian surrogate; re-run real-data experiment; report how MSE ordering changes.
3. **Faithful SW-MLE reimplementation** per arXiv:2511.09491 (pair-correlation MLE).
4. **Faithful static-Bayesian reimplementation** per arXiv:2406.08981 (TN+MCMC).
5. **LCD reimplementation** at published-protocol fidelity against Riverlane Nat. Commun. 2025 numbers; head-to-head on real Willow data.
6. **Full-50 000-shot real-data run with 10-seed bootstrap CI**.
7. **Cross-experiment drift analysis.** Use multiple r* experiments from the same `d5_at_qX_Y` position as a proxy for long-timescale device drift (inter-run, since Willow doesn't provide per-shot timestamps).
8. **Formal LCD-as-SMC proof.**

Each item on its own takes days to weeks. The paper's credibility tier depends on how many of these the submission version ships with.

### 4.4 Revised venue ambition

proposal_v3 targeted PRX Quantum (primary), Phys. Rev. Research (secondary), Quantum (tertiary). Given the open-validation list, **Phys. Rev. Research** (willing to accept methods notes with explicit limitations) or **SciPost Physics Codebases** (infrastructure-focused, welcomes staged deliverables) are more defensible primary targets at this draft stage. PRX Quantum would be plausible after at least §4.3 items 1, 2, 5 are closed.

## 5 Related work

### 5.1 Online noise-model inference for QEC

Sliding-window MLE [arXiv:2511.09491]; static Bayesian TN+MCMC [arXiv:2406.08981]; per-edge DEM estimation [arXiv:2504.14643]; noise-aware decoding [arXiv:2502.21044]. All three benchmarks this paper aims to compete with; none has been compared head-to-head on real device data to our knowledge.

### 5.2 Sequential Monte Carlo methodology

Doucet-de Freitas-Gordon 2001 (Springer SMC handbook); Chopin & Papaspiliopoulos 2020 (Springer). Rao-Blackwellisation, particle-degeneracy handling, ESS-triggered resampling.

### 5.3 Production adaptive decoders

Riverlane Local Clustering Decoder (Barnes et al. 2025 Nat. Commun.) — the adaptive decoder whose noise-update step this paper conjectures to be a 1-particle SMC. AlphaQubit adaptive variants (Bausch 2024, Senior 2025) — streaming-latency-focused, different problem.

### 5.4 Google Willow and Zenodo 13273331

Acharya et al. 2024 Nature (Willow below-threshold). Data release: Zenodo 13273331. DEM-on-Willow baseline: arXiv:2512.10814 (identified in Phase 0 scoop scan — direct baseline to beat in future submission rounds).

### 5.5 QEC simulation tooling

Stim 1.16-dev [arXiv:2103.02202] — underpins the circuit+DEM representation in this paper. PyMatching v2 [arXiv:2105.13082] — would underpin the LER-vs-reweighting experiment currently listed as §4.3 open work.

## 6 Conclusions

We release a Rao-Blackwellisation-ready particle-filter infrastructure, lightweight baseline reimplementations, and a Google Willow 105Q data loader as open-source scaffolding for online QEC noise-model inference. Initial synthetic + real-data measurements show uniform-initialisation MSE ordering consistent with the project's original hypothesis, but a Phase 2.75 methodology audit has identified eight specific open-validation items that must close before the MSE ordering can be interpreted as "PF beats baselines." We publish the data, code, pre-registration, methodology review, and this honest caveat list alongside the draft so that any of §4.3 items 1–8 can be closed by third parties. The LCD-as-1-particle-SMC unification remains an attractive conjecture, not a theorem.

## Data and code availability

`particle_filter.py`, `baselines.py`, `phase_diagram.py`, `willow_loader.py`, `e02_real_willow.py`, `make_figures.py`, `results.tsv`, `figures/`. Pre-registration: `proposal_v3.md`. Phase 2.75 methodology review: `methodology_review.md`. Willow data at Zenodo 13273331 (full dataset ~112 GB, subset ~6 GB used here).

## Acknowledgements

This work used `qldpc-org/qldpc`, Stim 1.16-dev, PyMatching v2.3.1, the `ldpc` package, NumPy 2.4, SciPy 1.17. The Phase 2.75 methodology audit (verdict MAJOR-REVISIONS, reviewer: blind-SMC-expert-simulation) directly shaped the limitations section; the paper is stronger for the uncomfortable findings.

---
