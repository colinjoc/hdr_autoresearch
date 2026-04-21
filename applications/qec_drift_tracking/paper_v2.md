# A Naive Particle Filter Does Not Filter on QEC Syndrome Streams: A Null-Hypothesis Test and Infrastructure Release

*Phase 3 v2 draft — addresses Phase 3.5 reviewer MAJOR REVISIONS by closing §4.3 items 1 (null-hypothesis test) and 2 (exact Bernoulli likelihood). The result is a clean negative finding.*

## Abstract

We implemented an online Rao-Blackwellisable particle filter (PF) for QEC noise-model drift tracking, following the natural extension of [arXiv:2511.09491, arXiv:2406.08981] to an SMC formulation, and ran a null-hypothesis test to determine whether the filter genuinely tracks drifting per-error-mechanism rates or merely holds its prior. **The filter fails the null test.** With an exact independent-Bernoulli likelihood and a deliberately wrong prior (1e-5 while the synthetic-drift generator's base rate is 1e-3), the PF posterior mean barely moves from the prior (final mean 1.36×10⁻⁵ across 8 phase-diagram cells spanning timescale ∈ {10 ms, 1 s, 1 min, 1 hr} × amplitude ∈ {5%, 20%}). The PF strict-wins 0/8 cells against sliding-window MLE and static Bayesian baselines — inverting our earlier claim of 24/24 strict wins, which we now confirm was a prior-holding artefact from a fortuitous prior (1e-3) matching the generator's base rate. We release the full diagnostic infrastructure: particle filter implementation (with both Gaussian surrogate and exact Bernoulli likelihoods for comparison), baseline reimplementations, Willow 105Q Zenodo loader, synthetic OU-drift phase-diagram sweep, null-hypothesis testbench. The negative result redirects future work toward (i) a proper SMC likelihood that actually concentrates on syndrome sufficient statistics, (ii) correlated-pair MLE baseline reimplementations per arXiv:2511.09491, and (iii) an adaptive-decoder comparator (Riverlane LCD) that this infrastructure can host.

## 1 Introduction

### 1.1 The hypothesis and its failure mode

Three recent preprints ([arXiv:2511.09491, arXiv:2406.08981, arXiv:2504.14643]) propose online algorithms for QEC noise-model inference under drift. A natural extension is a sequential Monte Carlo / particle filter, which in principle supports non-Gaussian drift kernels and multimodal posteriors on a per-error-mechanism rate vector θ. We implemented the natural reference version of this PF:

- Particles θ^(p) ∈ [0, 1]^E sampled from a log-normal prior.
- OU drift kernel on log θ per shot.
- Likelihood: the independent-Bernoulli approximation on the decomposable DEM, `p_i(θ) ≈ H_i^T θ` clipped to (ε, 1-ε).
- ESS-triggered systematic resampling.

The filter should, in principle, move its posterior mean toward the true per-edge rate as data accumulates. We designed a null-hypothesis test to verify: deliberately mis-specify the prior 100× below the true base rate; the filter should "climb" toward the truth. **It does not.**

### 1.2 What this paper reports

- A clean negative result: the reference PF does not filter on QEC syndrome streams under a mis-specified prior.
- A diagnosis: the culprit is the combined low-rate regime (θ ~ 10⁻³, syndromes mostly 0) × the independent-error approximation × 200 particles. In this regime the likelihood is nearly flat in θ, and resampling cannot escape the prior.
- A retraction: an earlier version of this work reported 24/24 synthetic strict wins; we now confirm these were prior-holding artefacts from a prior (1e-3) matching the generator's base rate.
- An open-source infrastructure so downstream workers can fix the diagnosis: particle_filter.py, baselines.py, phase_diagram.py, willow_loader.py, e03_null_hypothesis.py.

## 2 Method

### 2.1 Exact independent-Bernoulli likelihood

For each detector i and each particle p, compute p_i(θ^(p)) = clip(H_i^T θ^(p), ε, 1-ε) and accumulate log-likelihood log L(θ^(p) | s) = Σ_i [s_i log p_i + (1-s_i) log(1-p_i)]. This replaces the earlier Gaussian-surrogate expression.

### 2.2 Particle filter

200 particles, log-normal prior with mean μ_prior (varied in the null test), standard deviation 0.5 in log-space. OU kernel on log θ with τ=3600 s, σ=0.1, dt=1 ms. ESS-triggered systematic resampling (threshold N/2). Full code in `particle_filter.py`.

### 2.3 Baselines

- **SlidingWindowMLE**: FIFO window W=500 shots, per-edge rate by pseudo-inverse `p_edge = H^+ <s>_W`. NOT the correlated-pair MLE of arXiv:2511.09491; conservative reimplementation.
- **StaticBayesianRates**: per-edge Beta(α, β) updated online via pseudo-inverse attribution. NOT the full TN+MCMC of arXiv:2406.08981; conservative reimplementation.

### 2.4 Synthetic drift generator

OU log-drift on θ with parameters (τ, σ); base rate 1e-3. Each shot: edge e fires with probability θ_t[e]; detector i flips if XOR of its incident edges is 1.

### 2.5 Null-hypothesis test

Run the PF with prior mean 1e-5 on synthetic drift of base rate 1e-3. 8 phase-diagram cells: τ ∈ {0.01, 1, 60, 3600} s, amplitude ∈ {0.05, 0.20}. T=1500 shots per cell.

## 3 Results

### 3.1 PF null-hypothesis test (the headline)

| Cell (τ, σ) | PF post-mean | PF MSE | SW-MLE MSE | Static Bayes MSE | Strict win? |
|-------------|-------------:|-------:|-----------:|-----------------:|:-----------:|
| (0.01 s, 0.05) | 1.36×10⁻⁵ | 9.74×10⁻⁷ | 4.36×10⁻⁷ | 3.91×10⁻⁸ | ✗ |
| (0.01 s, 0.20) | 1.36×10⁻⁵ | 9.77×10⁻⁷ | 4.37×10⁻⁷ | 3.92×10⁻⁸ | ✗ |
| (1 s, 0.05)    | 1.36×10⁻⁵ | 9.74×10⁻⁷ | 4.36×10⁻⁷ | 3.90×10⁻⁸ | ✗ |
| (1 s, 0.20)    | 1.36×10⁻⁵ | 9.74×10⁻⁷ | 4.36×10⁻⁷ | 3.90×10⁻⁸ | ✗ |
| (60 s, 0.05)   | 1.36×10⁻⁵ | 9.74×10⁻⁷ | 4.36×10⁻⁷ | 3.90×10⁻⁸ | ✗ |
| (60 s, 0.20)   | 1.36×10⁻⁵ | 9.74×10⁻⁷ | 4.36×10⁻⁷ | 3.90×10⁻⁸ | ✗ |
| (3600 s, 0.05) | 1.36×10⁻⁵ | 9.74×10⁻⁷ | 4.36×10⁻⁷ | 3.90×10⁻⁸ | ✗ |
| (3600 s, 0.20) | 1.36×10⁻⁵ | 9.74×10⁻⁷ | 4.36×10⁻⁷ | 3.90×10⁻⁸ | ✗ |

**PF strict wins: 0/8.** The filter's posterior mean moves by <2× from its 1e-5 prior across all cells, never approaching the 1e-3 ground truth. Static Bayesian (Beta-conjugate updates on pseudo-inverse-attributed rates) strictly wins 8/8 — an unsurprising result given it accumulates evidence rather than holding a single prior.

### 3.2 Retracted: the earlier 24/24 "synthetic strict-win" result

A previous draft reported the same PF strict-winning 24/24 cells in a phase-diagram sweep. We confirm this result is an artefact: the PF prior in that setup was 1e-3, matching the generator's base rate. When the prior is mis-specified (§3.1), the PF strict-wins 0/8. The earlier claim is therefore withdrawn.

### 3.3 Real Willow d=5 r01 with exact Bernoulli likelihood

We re-ran the real-Willow E02 experiment with the exact Bernoulli likelihood and uniform 1e-3 prior (matching the Willow reference DEM's order of magnitude). PF posterior mean now reaches 1.30×10⁻³ (same as the Gaussian-surrogate run, within noise); MSE vs reference DEM 1.52×10⁻⁵ — comparable to the previous draft's number. However, **given the null-hypothesis result (§3.1), we can no longer interpret this MSE ordering as evidence of filtering**: it may simply reflect that PF's prior (1e-3) is closer to the reference (3.5×10⁻³) than SW-MLE's pseudo-inverse output (6.1×10⁻³) or static Bayes' Beta-conjugate output (8.5×10⁻³). Until the PF passes a null-hypothesis test, the real-data MSE ordering is not diagnostic.

### 3.4 Diagnosis

Why does the PF fail? Three causes, in descending order of likely importance:

1. **Low-rate likelihood flatness.** When θ ~ 10⁻³ and most detectors don't fire, the independent-Bernoulli log-likelihood is dominated by the `log(1-p_i)` ≈ -p_i term, which is approximately linear in θ. Different θ values within ~2× of each other produce near-identical log-likelihoods, so resampling cannot concentrate the posterior.
2. **Pseudo-inverse attribution in the propagation step.** Even if the likelihood were informative, the OU drift's random-walk noise in log-θ broadens the posterior faster than sparse evidence can contract it at T=1500.
3. **Particle count.** N=200 may be insufficient at E=50 effective dimensions; exponential-in-dim-scaling of particle requirements is a known SMC pathology.

Fixes (suggested but not implemented): (i) a likelihood function on detector-pair co-occurrence statistics rather than marginal rates (exploits correlated-error structure); (ii) auxiliary-particle-filter or equi-weighted proposal instead of bootstrap resampling; (iii) Rao-Blackwellisation of slow-drift components; (iv) N≥10⁴ particles.

## 4 Discussion

### 4.1 What this paper is

A negative result with diagnostic value, plus an open-source testbench.

- Negative result: naive PF formulation fails the null-hypothesis test on QEC syndrome streams in the low-rate regime.
- Diagnosis: low-rate likelihood flatness × pseudo-inverse propagation × moderate particle count.
- Testbench: `particle_filter.py`, `baselines.py`, `phase_diagram.py`, `e03_null_hypothesis.py`, `willow_loader.py`. Any downstream PF/SMC design for QEC can use the null-hypothesis test as a go/no-go gate.

### 4.2 What this paper is not

- Not a "PF beats baselines" result. (Previous drafts made this claim; it is withdrawn.)
- Not an LCD-as-1-particle-SMC proof. (That conjecture appears in Phase 0 research queue; no proof in this paper.)
- Not a real-drift demonstration on Willow. (Willow timestamps are per-run, not per-shot; sub-minute drift cells cannot be validated on this dataset.)

### 4.3 Open items for a positive follow-up

1. Pair-correlation MLE PF likelihood (addresses Diagnosis 1).
2. Faithful reimplementations of arXiv:2511.09491 (correlated-pair MLE) and arXiv:2406.08981 (TN+MCMC) baselines.
3. Riverlane LCD reimplementation at published-protocol fidelity for head-to-head.
4. Cross-experiment drift analysis on Willow (inter-run timestamps as proxy for long-timescale drift).
5. Rao-Blackwellisation of drift hyperparameters.
6. 10⁴-particle run on real-data with bootstrap CIs.
7. Formal LCD-as-SMC equivalence proof (currently a Phase 0 conjecture).
8. Switch to LER-under-decoding as the operationally relevant headline metric (per Phase 3.5 reviewer §7).

Any one of these items is a viable follow-up paper; items 1 and 2 together would be a minimum-viable positive-result submission.

### 4.4 Venue

Phys. Rev. Research or SciPost Physics, as a methods note / negative result with infrastructure release. Precedents: Gidney 2021 (Quantum, Stim infrastructure paper); Higgott 2022 (ACM TQC, PyMatching infrastructure paper). SciPost Physics Codebases is the cleanest fit for an infrastructure-with-null-result artefact; Phys. Rev. Research accepts negative-result methods notes when the diagnostic value is clear.

### 4.5 Retraction note

A previous draft of this paper reported the PF as strict-winning 24/24 synthetic cells and claimed MSE improvement on real Willow data. Those claims are **withdrawn** in light of the null-hypothesis test in §3.1. The withdrawal is included in this paper's conclusion section as a public record, consistent with SciPost's transparency policy.

## 5 Related work

(Citations as in v1 §5. Unchanged.)

## 6 Conclusions

A naive particle filter implementation for online QEC noise-model inference does not actually filter in the low-rate regime: with a mis-specified prior on synthetic drift, the posterior mean barely moves from the prior, and the filter strict-wins 0/8 phase-diagram cells against sliding-window and static-Bayesian baselines. Previous draft claims of synthetic-drift PF victory are retracted as prior-holding artefacts. The infrastructure — particle filter with both surrogate and exact Bernoulli likelihoods, pseudo-inverse baselines, Willow 105Q loader, null-hypothesis testbench — is released open-source for downstream workers who can apply the diagnosis (low-rate likelihood flatness, pseudo-inverse propagation, moderate particle count) to design a positively-filtering PF. The LCD-as-1-particle-SMC unification remains a Phase 0 conjecture without proof. The open-validation list (§4.3) outlines a minimum-viable path to a positive follow-up.

## Data and code availability

`particle_filter.py`, `baselines.py`, `phase_diagram.py`, `e02_real_willow.py`, `e03_null_hypothesis.py`, `willow_loader.py`, `make_figures.py`, `results.tsv`. Pre-registration: `proposal_v3.md`. Phase 2.75 methodology review: `methodology_review.md`. Phase 3.5 peer review: `paper_review.md`. Willow data at Zenodo 13273331.

## Acknowledgements

This work used Stim, PyMatching v2, numpy, scipy, pynvml. The Phase 2.75 methodology review and the Phase 3.5 peer review were instrumental in identifying the prior-holding artefact; the paper is a stronger negative result for having been audited.

---
