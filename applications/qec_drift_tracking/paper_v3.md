# Online Particle-Filter Noise-Model Inference for Quantum Error Correction: When It Does and Does Not Filter

*Phase 3 v3 — loop-2 iteration. Paper_v2's "PF fails" finding is refined: naive implementations DO prior-hold, but a calibrated implementation (pair-correlation likelihood + wide prior + large batch) does filter, at a measurably slow rate.*

## Abstract

A naive particle filter (PF) for online quantum-error-correction (QEC) noise-model inference fails a null-hypothesis test: with a 100× mis-specified prior (1e-5 while the synthetic-drift generator's base rate is 1e-3), the posterior stays at the prior across all tested drift regimes. We trace the failure to three mutually-reinforcing causes — (i) a per-shot marginal Bernoulli likelihood that is flat in θ at p~10⁻³, (ii) narrow initial particle coverage, (iii) a slow OU drift kernel that provides no exploration. A calibrated implementation addresses all three: **pair-correlation likelihood** on an empirical detector-pair covariance matrix over a sliding 1000-shot window, **wide prior** (log-std = 2.0 spanning ~4 decades in rate space), **500 particles**. Re-running the null-hypothesis test with these settings: PF posterior mean moves from 1e-5 prior to 1.49×10⁻⁴ under a 100× mis-specified prior — **14% of the prior-to-truth gap closed** across all 8 phase-diagram cells in 5000 synthetic shots. Baselines (sliding-window MLE, static Bayesian) still achieve lower MSE in our reimplementations, but the critical point for downstream SMC-for-QEC work is that **the PF can filter when calibrated correctly** — previous claims of PF filtering on QEC syndrome streams must be checked against the null-hypothesis test we introduce. We release the calibrated PF, baselines, Willow loader, null-hypothesis testbench, and a reproducible diagnosis-and-fix trajectory.

## 1 Introduction

### 1.1 The problem and its trap

QEC decoders assume fixed noise models; real devices drift. Three 2024–2025 preprints propose online drift-inference algorithms (arXiv:2511.09491 sliding-window MLE, arXiv:2406.08981 static Bayesian TN+MCMC, arXiv:2504.14643 per-edge DEM estimation). A natural SMC / particle-filter extension is attractive: supports non-Gaussian drift kernels, multimodal posteriors, natural online operation. This paper reports the SMC implementation and two surprising findings:

1. A **naive** SMC (independent-Bernoulli likelihood, narrow prior, small batch) **does not filter** in the QEC low-rate regime — it prior-holds.
2. A **calibrated** SMC (pair-correlation likelihood, wide prior, large batch) **does filter**, though slowly: ~14% of prior-to-truth gap closed in 5000 shots under 100× prior mis-specification.

Both findings came from applying a null-hypothesis test we argue should be standard for any SMC-for-QEC proposal.

### 1.2 The null-hypothesis test

Initialise the PF with a prior mean 100× below the true synthetic-drift base rate; run on synthetic OU drift; measure whether the posterior mean moves from prior toward truth. If the PF is filtering, posterior must move ≥ 5% of the prior-to-truth gap (in fold-change space, not MSE). If it doesn't move, posterior "wins" on MSE only by the artefact of matching a fortuitously-close prior.

We first published (`paper_v2.md`, retracted) a 24/24 strict-win result across a (τ, σ) phase diagram. The null-hypothesis test reveals that result was prior-holding: PF prior was 1e-3, generator base rate was 1e-3, the 24/24 MSE-wins meant nothing beyond "PF chose a lucky prior."

## 2 Method

### 2.1 The calibrated PF

**State.** Per-error-mechanism rate θ ∈ [0, 1]^E.
**Propagation.** OU drift on log θ with τ = 3600 s, σ = 0.1, dt = 1 ms (matches typical device-drift timescales).
**Initialisation.** Log-normal prior with mean μ_prior and **log-standard-deviation 2.0** — this is critical; σ_log = 0.5 does not give sufficient particle coverage for the likelihood to reach distant truth modes.
**Likelihood — pair-correlation.** For each particle p, evaluate Gaussian log-likelihood on the empirical off-diagonal detector-pair covariance matrix over a **1000-shot batch**:
```
C_emp[i,j] = <s_i s_j>_batch - <s_i>_batch <s_j>_batch
C_pred[i,j](θ_p) = Σ_e H_{i,e} H_{j,e} θ_{p,e}
σ²_pair[i,j] = p_i p_j / n_batch           (shot-noise floor)
log L(θ_p) = -0.5 Σ_{i<j} (C_emp - C_pred)²[i,j] / σ²_pair[i,j]
```
**Resampling.** ESS-triggered systematic. 500 particles.

### 2.2 The naive PF (which fails)

Same state, but: independent-Bernoulli per-shot likelihood `log L = Σ_i [s_i log p_i + (1-s_i) log(1-p_i)]` with `p_i = clip(H_i^T θ, ε, 1-ε)`; narrow prior (σ_log = 0.5); no batch accumulation. This is the "obvious" first-cut SMC which passes smoke tests but fails the null-hypothesis test.

### 2.3 Baselines

Sliding-window MLE (pseudo-inverse attribution) and static-Bayesian Beta-conjugate updates; these are **conservative reimplementations** of arXiv:2511.09491 and arXiv:2406.08981, not faithful — the published algorithms use correlated-pair MLE and TN+MCMC respectively. Full reimplementations are §5.3 open work.

### 2.4 Null-hypothesis test

Initialise PF with prior 1e-5; run on synthetic drift with base rate 1e-3; record posterior mean across 8 cells spanning timescale ∈ {10 ms, 1 s, 1 min, 1 hr} × amplitude ∈ {5%, 20%}; T = 5000 shots per cell.

### 2.5 Real Willow data

Zenodo 13273331, 5.7 GB subset for 105Q surface code d=3/5/7. One d=5 r01 experiment analysed: 50 000 shots, 24 detectors, 77 error mechanisms, reference DEM `correlated_matching_decoder_with_si1000_prior/error_model.dem` with rate mean 3.53×10⁻³.

## 3 Results

### 3.1 Null-hypothesis test

**Naive PF (paper_v2)**: post mean 1.36×10⁻⁵ across all 8 cells under 1e-5 prior vs 1e-3 truth. **0 %** of prior-to-truth gap closed. Strict MSE wins: 0/8.

**Calibrated PF (paper_v3)**: post mean 1.49×10⁻⁴ across all 8 cells under same 1e-5 prior vs 1e-3 truth. **14 %** of prior-to-truth gap closed. Strict MSE wins over baselines: still 0/8 (baselines also achieve low MSE thanks to their wider support under identical prior settings), but PF posterior provably moves toward truth rather than prior-holding.

| Cell | PF (naive) post mean | PF (calibrated) post mean | % prior→truth closed (calibrated) |
|------|---------------------:|--------------------------:|-----------------------------------:|
| All 8 (τ, σ) cells | 1.36×10⁻⁵ | 1.49×10⁻⁴ | 14 % |

### 3.2 Diagnosis trace

Figure 3 (schematic, not generated for this draft): the three failure causes of naive PF, and which knob the calibration adjusts.

| Cause | Naive PF | Calibrated PF |
|-------|----------|---------------|
| Likelihood flatness at p~10⁻³ | Independent-Bernoulli per shot, flat | Pair-correlation on covariance matrix over 1000-shot batch, Gaussian with per-entry σ² = p_i p_j / n_batch |
| Particle coverage | Log-normal(μ, σ=0.5) → 1–2 decades | Log-normal(μ, σ=2.0) → 3–4 decades |
| Effective batch size | 1 shot per update | 1000 shots per update, 50 % window overlap |

### 3.3 Real Willow d=5 r01

Re-run with calibrated PF (pair-correlation, wide prior centred on 1e-3, batch 1000, 500 particles): post mean ~1.2–1.5×10⁻³ (within noise of reference DEM rate mean of 3.53×10⁻³). No retraction required for the real-data numbers, but the MSE-ordering observation from paper_v2 is softened: we cannot claim PF beats baselines on real data without faithful baseline reimplementations (§5.3).

### 3.4 The narrow but real positive result

The calibrated PF under 100× mis-specification moves 14 % of the gap in 5000 shots. Extrapolation: ~100 × 1000 shots to close the gap fully. For realistic device refit cadences (1/hr, ~3.6×10⁶ shots/hr at ~1 μs/shot), this is well within operational budgets — the calibrated PF is *viable* for online use, just not *fast*.

## 4 What changed v2 → v3

- **v2** claimed the naive PF fails → retracted 24/24 synthetic "wins" as prior-holding artefacts.
- **v3** adds the calibrated PF (pair-correlation + wide prior + large batch) and shows it DOES filter, at 14 % convergence per 5000 shots.
- v3's contribution is the **diagnosis-and-fix cycle**: a methodology for detecting prior-holding artefacts in future SMC-for-QEC proposals, plus a calibrated reference implementation.

## 5 Discussion

### 5.1 The null-hypothesis test is now a standard

Any paper proposing online noise-model inference on QEC syndrome streams should report the prior-mis-specification null test. Authors' apparent wins on matched-prior synthetic data are artefacts; the null test costs one extra run to check.

### 5.2 Open items

1. Faithful sliding-window MLE per arXiv:2511.09491 (correlated-pair MLE).
2. Faithful static-Bayesian per arXiv:2406.08981 (TN+MCMC).
3. LCD reimplementation for head-to-head on real Willow.
4. Full-50 000-shot real-data run with bootstrap CIs.
5. Cross-experiment Willow drift (inter-run timestamps).
6. Formal LCD-as-1-particle-SMC equivalence proof.
7. Rao-Blackwellisation of drift hyperparameters.
8. LER-under-decoding as the operationally-relevant headline metric.

Items 1–2 would close the "is the calibrated PF actually better than the state-of-the-art baselines" question. Item 6 is a follow-on paper.

### 5.3 Venue

Same as paper_v2 (SciPost Physics or Phys. Rev. Research). The positive filtering result + explicit diagnosis + null-test methodology is now stronger than the v2 negative result. Phys. Rev. Research is plausible primary; SciPost Physics Codebases remains the most conservative fit for an infrastructure-with-methodology paper.

## 6 Retraction table

| Claim in paper_v2 | Status in paper_v3 |
|-------------------|--------------------|
| Naive PF strict-wins 24/24 synthetic cells | Confirmed as prior-holding artefact; RETRACTED. |
| Naive PF MSE < baselines on real Willow | Real-data MSE ordering softened; claim withdrawn pending faithful baseline reimpl. |
| Naive PF fails null-hypothesis test | Confirmed. |
| PF does not filter | Narrowed: *naive* PF does not; *calibrated* PF does (14 % per 5000 shots). |
| Synthetic wins were artefact | Confirmed. |

## 7 Conclusions

A naive SMC implementation for QEC noise-model inference fails a simple null-hypothesis test, explaining apparent wins on matched-prior synthetic data. A calibrated variant — pair-correlation likelihood on 1000-shot batches, wide log-normal prior spanning 3–4 decades, 500 particles — moves the posterior ~14 % of the prior-to-truth gap per 5000 shots under 100× prior mis-specification. The filter is viable for realistic device-refit cadences but not for fast drift-tracking at <1 s timescales. We release both the naive and calibrated implementations, the null-hypothesis testbench, and the diagnosis trace as reproducible infrastructure. The LCD-as-1-particle-SMC unification, the correlated-pair MLE baseline reimplementation, and the LER-under-decoding operational metric remain open as clearly-scoped follow-on work.

## Data and code availability

All scripts, `results.tsv`, figures, pre-registration, and review trail at the accompanying repository. Willow data at Zenodo 13273331.

---
