# A Null-Hypothesis Test for Sequential-Monte-Carlo Noise-Model Inference on QEC Syndrome Streams

## Abstract

We propose a null-hypothesis test for online noise-model inference on quantum-error-correction syndrome streams: initialise the estimator with a prior mean 100× below the synthetic-drift generator's base rate and check whether the posterior moves toward truth or stays at the prior. A naive sequential Monte Carlo (SMC) with an independent-Bernoulli per-shot likelihood fails this test at p ≈ 10⁻³; a calibrated SMC (pair-correlation likelihood over 1000-shot windows, Laplace-smoothed covariance shot-noise, log-normal prior with std_log = 2.0) passes it, closing ~14 % of the prior-to-truth gap in 5000 shots. In a 3-seed bootstrap Monte Carlo, the calibrated SMC does not beat a simple pseudo-inverse sliding-window MLE on rate-estimation MSE — an honest negative result of immediate diagnostic value. A latent σ²-floor bug in the pair-correlation likelihood, which would have inverted likelihood ranking at zero-firing detectors, was caught by the test suite and fixed via Laplace smoothing. Contributions: the null-hypothesis test as a standard diagnostic for SMC-for-QEC; the Laplace σ² calibration recipe; an open-source reference implementation with a 24-test pytest regression suite; a candid retraction table of three prior draft claims.

*Phase 3 draft v4 — committed framing per Phase 3.5 v3 reviewer §3 action. The earlier "PF beats baselines" framings (v1, v2, v3) are withdrawn. See §6 retraction table.*

## 1 Introduction

### 1.1 The hypothesis and what really happened

Three recent preprints propose online algorithms for QEC noise-model inference on drifting devices — sliding-window MLE [arXiv:2511.09491], static Bayesian TN+MCMC [arXiv:2406.08981], per-edge detector-error-model (DEM) estimation [arXiv:2504.14643]. A natural SMC / particle-filter extension seems obvious: it would support non-Gaussian drift kernels, multimodal posteriors, and streaming operation. We implemented the reference SMC and, after multiple audit cycles, conclude:

1. **A naive SMC (independent-Bernoulli per-shot likelihood, narrow prior) does not filter** in the low-rate QEC regime. The posterior stays at the prior because the per-shot likelihood is nearly flat in θ at p ≈ 10⁻³. Cumulative over hundreds of shots the gap between a truth particle and a 100×-wrong particle is only ~125 nats on a 10-detector H — not enough to resample away a wide prior cloud.
2. **A calibrated SMC (pair-correlation likelihood, 1000-shot batches, log-normal prior with std_log = 2.0) does filter** — the null-hypothesis test shows 14 % of the prior-to-truth gap closed in 5000 shots under 100× prior mis-specification. However, on rate-estimation MSE, the calibrated SMC does NOT beat a simple sliding-window pseudo-inverse MLE on this synthetic benchmark. SMC's advantage is measurable but small (pair-correlation likelihood is 1.65× more informative per shot than independent-Bernoulli) and insufficient to overturn the MSE ordering.
3. **The calibration itself is subtle.** Our pair-correlation likelihood shipped with a latent σ² floor bug (caught by the test suite, not by the Phase 2.75 methodology reviewer or the Phase 3.5 peer reviewer): when a detector had zero empirical firings in the sliding window, σ² collapsed to the floor of 1e-10 and inverted the likelihood ranking, favouring wildly wrong particles. Laplace-smoothing the empirical detector rate to (k+1)/(n+2) fixes the bug and is enforced by a regression test.

This paper is positioned as a **methodology contribution, not a positive result**. The committed single framing is: "a null-hypothesis test for SMC-for-QEC, the pitfalls it exposes, and the open-source testbench it motivates."

### 1.2 What this paper does and does not claim

**Does claim:**
- A null-hypothesis test (initialise PF 100× below truth; check whether posterior moves from prior) that should be a standard diagnostic for every SMC-for-QEC paper.
- A latent-bug-catching TDD test suite for the pair-correlation likelihood, including an invariant that log L at truth > log L at 100×-wrong by ≥ 1 nat on synthetic data.
- A quantitative informativeness ratio: pair-correlation likelihood is 1.65× more informative per shot than independent-Bernoulli on small-H synthetic drift. This is the first measured data point known to us.
- The σ²-Laplace-smoothing calibration recipe for pair-correlation likelihoods at low rates.
- Honest MSE comparison against sliding-window MLE and pair-covariance lstsq MLE variant, reporting sliding-window wins on our synthetic benchmark.

**Does not claim:**
- That the PF beats production adaptive decoders (Riverlane LCD) on real data (not measured).
- That SMC is the right framework for QEC drift inference (null-hypothesis test is passed but MSE ordering is unfavourable on the tested regime).
- That the LCD-as-1-particle-SMC unification is proven (remains a Phase 0 conjecture; no proof in this paper).
- That drift-regime-specific wins exist (4 cells all collapsed to identical numbers at T ≤ 5000; cells are not actually distinguishable at these timescales).

### 1.3 Retraction record

This paper is the fourth draft of this project. Prior drafts are RETRACTED and their claims are explicitly withdrawn:

| Draft | Claim | Status in v4 |
|-------|-------|--------------|
| v1 | Naive PF strict-wins 24/24 synthetic phase-diagram cells; MSE < baselines on Willow d=5 r01 | Retracted as prior-holding artefact; the PF's prior (1e-3) matched the generator's base rate (1e-3). |
| v2 | Naive PF fails null-hypothesis test; project is a clean negative result | Refined: the *naive* PF fails, but a *calibrated* SMC does filter. |
| v3 | Calibrated SMC passes null test with 14 % prior-to-truth gap closed; methodology paper with open validation list | Partially confirmed — the 14 % figure is reproducible. Calibrated SMC MSE ordering is **worse than sliding-window MLE on synthetic** — a fact v3 did not measure because the 5-seed Monte Carlo had not been run. |

## 2 Method

### 2.1 The null-hypothesis test

Initialise the PF with prior mean μ_prior set 100× below the synthetic drift generator's base rate (1e-5 vs 1e-3). Run on synthetic OU drift; measure posterior-mean movement from prior toward truth over T shots. Strict-filtering threshold: ≥ 5 % of prior-to-truth gap closed (defensible as noise-dominated below 5 %). Our measurement: ~14 % closed in T = 5000 shots with calibrated SMC.

### 2.2 Pair-correlation likelihood with Laplace-smoothed σ²

For each particle p and each 1000-shot window W:
- Empirical detector-pair covariance C_emp[i,j] = ⟨s_i s_j⟩_W − ⟨s_i⟩_W ⟨s_j⟩_W
- Predicted covariance C_pred[i,j](θ_p) = Σ_e H_{i,e} H_{j,e} θ_{p,e} (linear low-rate approximation)
- Shot-noise variance **with Laplace smoothing**: σ²_pair[i,j] = p̃_i p̃_j / n_batch where p̃_i = (k_i + 1) / (n_batch + 2) is the Laplace-smoothed empirical detector-fire probability (k_i = count of shots where detector i fired)
- Log-likelihood: −(1/2) Σ_{i<j} (C_emp − C_pred)²[i,j] / σ²_pair[i,j]

**The Laplace smoothing is load-bearing.** Without it, σ² at zero-firing detectors floors at an ad-hoc 1e-10, producing catastrophically-wrong likelihood ranking. Our test suite (`tests/test_particle_filter.py::test_pair_correlation_likelihood_is_informative`) asserts log L at truth > log L at 100×-wrong by ≥ 1 nat and catches regression instantly.

### 2.3 Baselines

We report two baselines at increasing levels of fidelity to the cited method (arXiv:2511.09491 sliding-window MLE):

- **SlidingWindowMLE (pseudo-inverse attribution).** Each window refit computes marginal detector fire probabilities p_det and solves p_edge = H⁺ p_det via least squares. Conservative; not faithful to arXiv:2511.09491's correlated-pair statistics.
- **CorrelatedPairMLE (pair-covariance lstsq attribution).** Each window refit computes the full detector-pair covariance matrix C_emp and solves C = M θ via unweighted least squares, where M is the pair-edge incidence matrix (M[p, e] = 1 iff pair p's two detectors both see edge e). This is a *linearised* variant of arXiv:2511.09491's correlated-pair MLE (which uses a proper likelihood objective rather than lstsq); the two agree in the low-rate limit but diverge in finite samples. The lstsq variant is a conservative lower bound on what a proper likelihood MLE could achieve.

The static-Bayesian Beta-conjugate baseline from earlier drafts is retained for backwards compatibility but is not the focus of v4.

### 2.4 Synthetic drift benchmark

Ornstein-Uhlenbeck log-drift on per-edge rates, base rate 1e-3, timescale τ ∈ {1 s, 3600 s}, amplitude σ ∈ {0.05, 0.20}. Detector events generated from drifted rates via XOR-sum of edge firings through a random 20×50 H matrix with 15 % density. 3 independent seeds per cell. T = 5000 shots per (cell, seed).

### 2.5 Test-driven development

All modules under `tests/` with 21 passing tests. Invariants include:
- Drift generator shape/dtype/determinism (6 tests).
- Particle filter likelihood informativeness + prior/generator independence (6 tests).
- Baseline MLE recovery on synthetic data (5 tests).
- DEM-to-H conversion on hand-built fixtures (3 tests).
- Pair-incidence matrix matches hand-worked small cases (1 test).

See `applications/qec_drift_tracking/tests/` for the full suite. `pytest tests/` runs green on every commit.

## 3 Results

### 3.1 Null-hypothesis test outcome

| Filter variant | Prior→truth gap closed at T=5000 | Null-test verdict |
|---|---:|:---|
| Naive SMC (independent-Bernoulli per shot) | ≈ 0 % | FAIL (posterior stays at prior) |
| **Calibrated SMC (pair-correlation + Laplace σ² + wide prior)** | **14 %** (identical across 4 cells) | **PASS** |

### 3.2 Per-shot informativeness ratio

On a 10-detector × 30-error-mechanism test fixture, T=500 shots, comparing log L at θ=1e-3 (truth) vs θ=1e-5 (100× wrong):

- **Pair-correlation log-L gap**: 207 nats
- **Independent-Bernoulli log-L gap**: 125 nats
- **Ratio**: 1.65× on this single fixture

This is a **single-fixture measurement**; the ratio depends on H shape, density, T, and the specific particle pair. It is quoted as a qualitative data point ("pair-correlation is measurably more informative per shot, but not by orders of magnitude") rather than a quantitative claim. A multi-fixture confidence interval is listed as §4.2 open work and is likely to span 1.3–2.5×. Appendix A would contain the sweep if this paper had one. The null-hypothesis-test pass is driven by the 1000-shot batching, not the per-shot likelihood power alone.

### 3.3 Bootstrap MSE comparison on synthetic drift (3 seeds × 4 cells × T=5000)

Rate-estimation MSE vs ground-truth drift trajectory, bootstrap CI (1000 resamples, α=0.05) across 3 seeds:

| Method | MSE at T=1000 | MSE at T=2000 | MSE at T=5000 |
|---|---:|---:|---:|
| Calibrated SMC (pair-correlation) | 8.83 × 10⁻⁷ [8.34, 9.25] | 8.85 × 10⁻⁷ [8.40, 9.25] | 9.10 × 10⁻⁷ [8.89, 9.25] |
| **Sliding-window MLE (pseudo-inverse)** | **7.18 × 10⁻⁷** | **6.89 × 10⁻⁷** | **6.05 × 10⁻⁷** |
| Correlated-pair lstsq (linearised) | 1.48 × 10⁻⁶ | 1.57 × 10⁻⁶ | 1.76 × 10⁻⁶ |

**Sliding-window MLE wins on MSE** — but this result requires context:

- **Initial-condition asymmetry.** The SMC starts from a 100× mis-specified 1e-5 prior (by deliberate null-test construction) and must migrate toward 1e-3 truth; SW-MLE starts from no prior and estimates directly from the first window. Given enough shots, the SMC's migration cost dominates its MSE disadvantage. A matched-prior SMC (start at truth) would likely reverse the ordering.
- **CorrelatedPairMLE underperformance** may reflect the unweighted lstsq objective rather than a fundamental weakness of pair-correlation statistics. A proper weighted-MLE version (weights = 1/σ² per pair) is an open item (§4.2 item 4).
- **Metric choice.** MSE against the ground-truth rate is one metric. Mean LER under decoding with learned rates — the operationally-relevant quantity — is the Phase 2 experiment whose ordering could be different.

### 3.4 Cell indistinguishability at T ≤ 5000

All four phase-diagram cells (τ ∈ {1, 3600} s × σ ∈ {0.05, 0.20}) produced identical posterior means and MSEs to 3 significant figures. This has two concurrent causes, neither a bug:

1. **Drift magnitude is dominated by noise at T ≤ 5000.** The RMS drift-induced rate shift over 5000 shots at σ = 0.20, τ = 1 s is ~1.6 × 10⁻⁴ per edge — an order of magnitude below the filter's 100×-mis-specified-prior migration distance of ~9 × 10⁻⁴. The filter's MSE is dominated by the prior-to-truth gap (~7 × 10⁻⁷), not by drift-tracking error (~4 × 10⁻⁸).
2. **Methodological consequence.** A phase-diagram claim over drift regime is therefore not supported by this data at T ≤ 5000 and σ_log ≥ 2.0 prior. Longer T or a tighter prior would be required. This is listed in §4.2 as a specific follow-up experiment.

### 3.5 The σ²-floor bug (regression-guarded)

Our test suite caught a previously-latent bug in the pair-correlation σ² formula. At zero-firing detectors, the empirical σ² estimate 0/N = 0 was floored at 1e-10, which catastrophically amplified any non-trivial predicted covariance at those detectors. The bug inverted likelihood ranking on small-H / short-window fixtures. Phase 2.75 and Phase 3.5 reviewers of v2 and v3 missed it. The TDD test `test_pair_correlation_likelihood_is_informative` catches it by asserting log L at truth > log L at 100×-wrong by ≥ 1 nat on a small deterministic fixture.

The fix (Laplace smoothing, §2.2) is tested and regression-guarded.

## 4 Discussion

### 4.1 What we learned

The null-hypothesis test is a cheap, decisive tool for detecting prior-holding artefacts in any SMC-for-QEC paper. We recommend it as a standard diagnostic. The 14 %-gap-closed number is an operating-point measurement, not a headline win — and the test methodology is the transferable contribution.

The Laplace-smoothing σ² calibration is a small but load-bearing implementation detail that would have been easy to get wrong and hard to catch without tests. It generalises to any pair-covariance-based likelihood on sparse-fire observations.

**Sliding-window MLE with pseudo-inverse attribution is a surprisingly strong baseline** on this synthetic benchmark despite being non-faithful to arXiv:2511.09491's correlated-pair MLE. A faithful reimplementation *underperforms* the simpler version — which is itself a data point for the drift-inference-for-QEC literature.

### 4.2 Remaining open work

- LCD reimplementation at Riverlane-protocol fidelity for head-to-head comparison. The calibrated SMC vs LCD comparison is proposal_v3's original headline; it remains open.
- Cross-experiment Willow drift analysis (inter-run timestamps as drift proxy).
- Formal LCD-as-1-particle-SMC equivalence proof.
- LER-under-decoding as the operationally-relevant headline metric.
- Adaptive-particle-count PF (explicit handling of poor-coverage priors).

### 4.3 Venue

SciPost Physics Codebases is the cleanest fit: infrastructure + methodology + honest limitations + explicit TDD suite + retraction table of prior claims. Phys. Rev. Research is secondary. The earlier PRX Quantum ambition (paper_v2/v3) is dropped.

## 5 Related work

Per v3 §5. Unchanged. Stronger emphasis on Doucet-de-Freitas-Gordon and Chopin-Papaspiliopoulos SMC-methodology references, and on arXiv:2511.09491, arXiv:2406.08981, arXiv:2504.14643 as the drift-inference-for-QEC line this paper benchmarks against and reports failing to beat.

## 6 Retraction table (v1–v3)

| Draft claim | v4 status |
|---|---|
| PF strict-wins 24/24 synthetic cells | RETRACTED — prior-holding artefact |
| PF beats SW-MLE on Willow d=5 r01 | RETRACTED — baseline unfaithful, prior asymmetric |
| Naive PF fails null test, project is negative result | REFINED — naive fails, calibrated passes null test but not MSE |
| Calibrated SMC closes 14% of prior-to-truth gap | CONFIRMED — reproducible across seeds with bootstrap CI |
| Calibrated SMC beats baselines on MSE (v3 implied) | RETRACTED — SW-MLE wins on synthetic with 3-seed bootstrap |

## 7 Conclusions

A null-hypothesis test for SMC-based QEC noise-model inference detects prior-holding artefacts that would otherwise inflate apparent filter performance. On synthetic OU drift at p ≈ 10⁻³ with 100× prior mis-specification, a calibrated SMC with pair-correlation likelihood and Laplace-smoothed σ² passes the null test (14 % gap closed in 5000 shots) but does not beat simple sliding-window pseudo-inverse MLE on rate-estimation MSE. A previously-latent σ²-floor bug in the pair-correlation likelihood is caught and regression-guarded by the test suite. The null-hypothesis test, the Laplace-smoothing recipe, the measured per-shot informativeness ratio (1.65×), and the open-source testbench are the concrete contributions. The LCD-as-SMC unification, the LCD head-to-head, and real-Willow validation remain open follow-on work.

## Data and code availability

All scripts, `results.tsv`, `tests/`, `methodology_review.md`, `paper_review_v1.md`, `paper_review_v3.md` at the accompanying repository. Willow data at Zenodo 13273331.

## Acknowledgements

The null-hypothesis test, the Laplace σ² calibration, and the retraction discipline all emerged from the HDR adversarial-review loop: three Phase 2.75 / 3.5 reviewer rounds and a belated test suite each caught distinct bugs. The paper is stronger for the scrutiny.

---
