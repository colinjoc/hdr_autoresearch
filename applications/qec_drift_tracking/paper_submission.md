# A Null-Hypothesis Test for Sequential Monte Carlo Noise-Model Inference on Quantum Error Correction Syndrome Streams

## Abstract

We propose a null-hypothesis test for online noise-model inference on quantum error correction (QEC) syndrome streams: initialise the estimator with a prior mean two orders of magnitude below the synthetic-drift generator's base rate and check whether the posterior moves toward truth or stays at the prior. A naive sequential Monte Carlo (SMC) particle filter with an independent-Bernoulli per-shot likelihood fails this test at per-edge rate $p \approx 10^{-3}$. A calibrated SMC — pair-correlation likelihood over 1000-shot windows with a Laplace-smoothed covariance shot-noise estimator, a log-normal prior of standard deviation 2.0 in log-rate space — passes it, closing approximately 14 percent of the prior-to-truth gap in 5,000 shots. On rate-estimation mean-squared error (MSE) across a 3-seed Monte Carlo of four drift-parameter cells at $T = 5000$, the calibrated SMC is second to a simple pseudo-inverse sliding-window MLE (MSE $9.10 \times 10^{-7}$ vs $6.05 \times 10^{-7}$), and both outperform a linearised pair-covariance least-squares MLE ($1.76 \times 10^{-6}$). We also identify a latent covariance-variance floor bug in pair-correlation likelihoods at low rates, and give the Laplace-smoothing fix that eliminates it. Per-shot informativeness comparisons between competing likelihoods turn out to be highly seed- and trajectory-length-sensitive; a single-fixture ratio can flip sign under changes to upstream random-number-generator (RNG) state, so no headline quantitative ratio is claimed. The contributions are the null-hypothesis test as a standard diagnostic for SMC-for-QEC, the Laplace covariance-variance calibration recipe, the seed-fragility observation for single-fixture likelihood comparisons, and an open-source reference implementation with a regression test suite protecting against re-introduction of the calibration bugs.

## 1 Introduction

Quantum error correction protects logical qubits by measuring a stream of *syndrome bits* on ancilla qubits many thousand times per second. A classical decoder reads each syndrome frame, infers the most likely physical-error configuration, and applies a correction [@dennis2002topological; @kitaev2003faulttolerant; @fowler2012surface]. Every practical decoder depends on a *noise model*: a list of per-edge error probabilities, or equivalently a detector error model (DEM), describing how often each individual physical error mechanism fires on the underlying superconducting, trapped-ion, or neutral-atom device. Real devices drift. Two-level-system (TLS) defects switch between states, bias-tee filters decay, dilution refrigerators cycle through thermal gradients, cosmic rays occasionally hit the chip [@klesse2005quantum; @mcewen2022cosmic; @klimov2018fluctuations; @burnett2019decoherence; @muller2019towards]. A DEM fit last week becomes wrong this week; a decoder that uses the stale DEM degrades the logical error rate.

The obvious fix is online re-estimation of the DEM from the live syndrome stream. Three recent proposals pursue this: a sliding-window maximum likelihood estimator that tracks per-edge rates over a rolling buffer [@panteleev2024sliding]; a static Bayesian tensor-network Markov chain Monte Carlo (MCMC) that treats the rate vector as a posterior to be sampled [@hillmann2024bayesian]; and a per-edge DEM estimator that maintains a running statistic per detector edge and updates online [@bausch2024detectorerror]. All three have been compared to themselves on synthetic data. None has been benchmarked against a production adaptive decoder [@barnes2025lcd], and none has been asked whether its reported "improvement" is actually filtering or merely an artefact of a well-chosen prior.

A natural extension is a sequential Monte Carlo (SMC) particle filter [@gordon1993novel; @liu1998sequential; @doucet2001smc; @chopin2020smc]. SMC supports non-Gaussian drift kernels, multimodal posteriors, and streaming operation, all desirable properties for a decoder that must run online. Raw-Blackwellised variants [@doucet2000rbpf] further exploit structure in the rate vector. A straightforward SMC implementation seems obvious. We built one.

The contribution of this paper is not the filter. It is a diagnostic that showed us — across multiple independent iterations — that the obvious filter was silently broken in ways neither numerical sanity-checking nor domain reading caught. Specifically:

(i) A naive SMC with an independent-Bernoulli per-shot likelihood at per-edge rate $p \approx 10^{-3}$ does not actually filter; its posterior mean hovers near the prior regardless of the evidence, because the per-shot log-likelihood is approximately flat in the rate parameter at low rates. On matched-prior synthetic data this can be mistaken for a correct estimate.

(ii) A calibrated SMC, built on a pair-covariance likelihood aggregated over shot windows, does filter — but only after a Laplace-smoothing fix to the shot-noise variance estimator, which otherwise collapses to near-zero at detectors that happen not to fire in a given window and inverts the likelihood ranking.

(iii) On a 3-seed Monte Carlo benchmark the calibrated SMC places second to a simple pseudo-inverse sliding-window MLE on mean-squared error. We report this honestly and trace three plausible mechanisms for why the ordering could reverse under alternative conditions.

The unifying methodological recommendation: any future SMC or adaptive-decoder proposal for QEC noise inference should report the null-hypothesis test outcome described here before reporting improvement over a baseline. Improvements measured on matched-prior synthetic data are not necessarily evidence of filtering.

## 2 Methods

### 2.1 Null-hypothesis test

Let $p_0$ be the synthetic drift generator's base rate and $p_\pi$ the estimator's prior mean. The null-hypothesis test runs the estimator on a synthetic stream generated with base rate $p_0$ but initialised with prior $p_\pi = p_0 / 100$. Define the gap-closed fraction at shot $T$:
$$
\alpha(T) \;=\; \frac{\hat p(T) - p_\pi}{p_0 - p_\pi},
$$
where $\hat p(T)$ is the estimator's posterior mean at shot $T$ averaged over per-edge rates.

We define a pass threshold $\alpha_{\min} = 0.05$. The 5 percent threshold is grounded in two calibrations: (a) at prior-cloud width $\sigma_{\log} = 2.0$, running the SMC with prior equal to truth (no gap to close) gives posterior-mean drift equivalent to $\approx 3$ percent of the prior-to-truth gap purely from Ornstein-Uhlenbeck kernel noise plus resampling [@uhlenbeck1930theory; @pitt1999auxiliary; @kong1994sequential], and (b) below 5 percent movement could plausibly be attributed to particle-cloud shrinkage under the Laplace-smoothed likelihood's mild pull toward the prior mean rather than to evidence from the data. The 5 percent pass threshold is therefore approximately $1.7\times$ the no-filter noise floor.

### 2.2 Pair-correlation likelihood with Laplace-smoothed shot-noise variance

For each particle $p$ and each $W$-shot window of detector events $s_1, \dots, s_W \in \{0,1\}^D$, the empirical detector-pair covariance is
$$
C^{\text{emp}}_{ij} \;=\; \frac{1}{W}\sum_{t=1}^{W} s_{t,i} s_{t,j} \;-\; \hat p_i \hat p_j,
\qquad \hat p_i = \frac{1}{W}\sum_{t=1}^{W} s_{t,i}.
$$
The linearised low-rate prediction for a rate vector $\theta$ is $C^{\text{pred}}_{ij}(\theta) = \sum_e H_{i,e} H_{j,e}\, \theta_e$ where $H$ is the parity-check matrix. A Gaussian log-likelihood with per-entry shot-noise variance is
$$
\log L(\theta) \;=\; -\tfrac{1}{2} \sum_{i<j} \frac{\bigl(C^{\text{emp}}_{ij} - C^{\text{pred}}_{ij}(\theta)\bigr)^2}{\sigma^2_{ij}}.
$$

The critical calibration is $\sigma^2_{ij}$. A naive choice uses the empirical detector rates directly: $\sigma^2_{ij} = \hat p_i \hat p_j / W$. When any $\hat p_i = 0$ (a detector that simply did not fire in the window — common at $p \sim 10^{-3}$ with modest $W$), $\sigma^2_{ij}$ collapses. A floor such as $\sigma^2_{ij} = \max(\hat p_i \hat p_j / W,\, 10^{-10})$ produces catastrophic penalties: any non-trivial predicted covariance at a zero-fire detector is divided by $10^{-10}$, inverting the likelihood ranking so that wildly wrong $\theta$ values appear more likely than the truth.

The Laplace-smoothing fix is [@laplace1812theorie]
$$
\tilde p_i \;=\; \frac{k_i + 1}{W + 2}, \qquad k_i = \sum_t s_{t,i},
$$
giving $\sigma^2_{ij} = \tilde p_i \tilde p_j / W$, with a minimum value of $\bigl(1/(W+2)\bigr)^2/W$ rather than a hard floor. Zero-fire detectors contribute realistic variance $\approx 1/W^3$ that reflects sampling uncertainty rather than an ad-hoc floor.

This fix is enforced in the regression test suite (§2.5).

### 2.3 Baselines

Two baselines are reported at increasing fidelity to [@panteleev2024sliding]:

- **SlidingWindowMLE (pseudo-inverse attribution).** At each window refit, compute marginal per-detector probabilities $\hat p$ and solve $\hat\theta = H^{+} \hat p$ via least squares. This is a conservative estimator and is strictly weaker than a proper correlated-pair MLE.

- **CorrelatedPairMLE (pair-covariance lstsq attribution).** At each refit, compute the full detector-pair covariance matrix $C^{\text{emp}}$ and solve $C = M\theta$ via unweighted least squares, where the pair-edge incidence matrix is $M_{p,e} = 1$ iff pair $p$'s two detectors both connect to edge $e$. This is a linearised least-squares variant of the correlated-pair MLE — not a proper likelihood MLE — and agrees with [@panteleev2024sliding] in the low-rate limit. It provides a lower bound on what a proper weighted-likelihood MLE could achieve.

A static Bayesian Beta-conjugate baseline is retained in the reference implementation for completeness but is not a focus of the comparison here.

### 2.4 Synthetic drift benchmark

Each rate vector $\theta_t \in \mathbb R_+^E$ evolves under an Ornstein-Uhlenbeck process on $\log\theta$ with timescale $\tau$ and amplitude $\sigma_{\text{drift}}$. Base rate $p_0 = 10^{-3}$. Detector events are generated from the drifted rates by sampling Bernoulli edge firings and XOR-projecting through $H$. Four phase-diagram cells: $\tau \in \{1, 3600\}$~s $\times\ \sigma_{\text{drift}} \in \{0.05, 0.20\}$. Three independent seeds per cell. $T = 5000$ shots per (cell, seed) trajectory. Parity-check matrix $H$ of shape $20 \times 50$ with 15 percent density, resampled per seed.

### 2.5 Reproducibility and regression tests

The reference implementation is a standalone Python package depending only on NumPy, SciPy, Stim [@gidney2021stim], and PyMatching [@higgott2022pymatching]. A unit-test suite covers the drift generator, both likelihoods, the three rate estimators, the detector-error-model to parity-check-matrix converter, and the pair-edge incidence construction. Regression tests explicitly guard against recurrence of the likelihood-ranking inversion described in §2.2 and the self-consistency artefact described in §3.1. All tests are distributed with the reference implementation.

## 3 Results

### 3.1 Null-hypothesis test

The naive SMC fails the null-hypothesis test across all four synthetic cells: posterior mean remains within less than 1 percent of the 100$\times$-mis-specified prior over $T = 5000$ shots, with no detectable trend toward truth. The calibrated SMC passes: gap-closed fraction $\alpha(5000) = 0.14 \pm 0.01$ across three seeds (Figure 1).

![**Figure 1.** Calibrated particle-filter posterior-mean trajectory from a 100$\times$ mis-specified prior ($10^{-5}$, red dashed line) toward the truth ($10^{-3}$, green dashed line), three independent random seeds. Migration is approximately monotone up to $T \approx 3000$ and levels off thereafter. The gap-closed fraction at $T = 5000$ is approximately 14 percent across all seeds.](figures/fig1_prior_migration.png)

### 3.2 Per-shot informativeness comparison is seed-fragile

We attempted to compare the per-shot informativeness of the pair-correlation likelihood against the independent-Bernoulli likelihood by computing $\log L$ at the truth rate $\theta = 10^{-3}$ versus at a 100$\times$-wrong rate $\theta = 10^{-5}$, for varying batch sizes on a fixed $10 \times 30$ fixture. Results show strong sensitivity to how much upstream RNG state has been consumed by the synthetic trajectory generator before the first shot of the batch arrives. On seed 42, a batch of 500 shots drawn from a $T = 1000$ trajectory gives a pair-correlation log-L gap of $+207$ nats (truth preferred over wrong). The same batch size and the same seed, but drawn from a $T = 2000$ trajectory, gives $-895$ nats (wrong preferred over truth). The difference is entirely in the number of `rng.normal` calls consumed before edge-firing starts (Figure 3).

![**Figure 3.** Log-likelihood gap between truth and 100$\times$-wrong particles versus batch size on a fixed $10 \times 30$ fixture. Pair-correlation likelihood (blue) is positive for small batches but crashes negative above batch $\approx 200$ on the specific upstream trajectory used. Independent-Bernoulli likelihood (orange) grows smoothly. Comparing ratios between these two curves on a single fixture produces numbers that are not robust under modest changes to upstream RNG consumption.](figures/fig3_log_L_gap_vs_batch.png)

This sign-flipping between nominally equivalent experimental configurations rules out any headline quantitative ratio. Multi-seed, multi-fixture sweeps are required for any per-shot informativeness claim. The null-hypothesis test pass at production scale ($T = 5000$, $W = 1000$, $H$ of shape $20 \times 50$) is robust to this fragility because the $W = 1000$ batching averages over sufficient RNG realisations that the posterior concentrates regardless of the per-shot gap noise.

### 3.3 Bootstrap MSE comparison on synthetic drift

MSE of the posterior mean against the ground-truth drift trajectory, with 1000-resample bootstrap intervals over $N = 3$ seeds. All four drift cells averaged (cells collapse to near-identical numbers at this $T$; see §3.4).

| Method | MSE at $T=1000$ | MSE at $T=2000$ | MSE at $T=5000$ |
|---|---:|---:|---:|
| Calibrated SMC (pair-correlation) | $8.83\times 10^{-7}$ [8.34, 9.25] | $8.85\times 10^{-7}$ [8.40, 9.25] | $9.10\times 10^{-7}$ [8.89, 9.25] |
| **Sliding-window MLE (pseudo-inverse)** | $\mathbf{7.18\times 10^{-7}}$ | $\mathbf{6.89\times 10^{-7}}$ | $\mathbf{6.05\times 10^{-7}}$ |
| Correlated-pair MLE (linearised lstsq) | $1.48\times 10^{-6}$ | $1.57\times 10^{-6}$ | $1.76\times 10^{-6}$ |

The bracketed range is the in-seed sampling distribution of the mean from the bootstrap [@efron1979bootstrap], not the between-seed spread. The between-seed spread is visualised as min-max envelopes in Figure 2. A tighter characterisation of between-seed uncertainty requires $N \gtrsim 10$ seeds, which is open work.

![**Figure 2.** Rate-estimation mean-squared error versus shots for three methods on the synthetic drift benchmark. Minimum-to-maximum spread across three independent seeds is shaded. Sliding-window MLE (orange) leads at every tested $T$ and in every seed. Calibrated SMC (blue) is second. Linearised correlated-pair lstsq (green) is third. The ordering is robust to between-seed variation even without tight confidence intervals.](figures/fig2_mse_vs_T.png)

The ordering (SW-MLE $<$ SMC $<$ CP-lstsq) is preserved at every $T$ and every seed (Figure 2). Three remarks qualify the SW-MLE lead:

- **Initial-condition asymmetry.** The SMC starts from a 100$\times$ mis-specified prior $10^{-5}$ and must migrate toward truth $10^{-3}$; SW-MLE starts with no prior and estimates directly from the first window. This is a deliberate construction of the null-hypothesis test and disadvantages the SMC on MSE. A matched-prior SMC (starting at truth) would likely reverse the ordering.
- **Least-squares vs likelihood in the pair-MLE baseline.** The CorrelatedPairMLE uses unweighted lstsq rather than a proper weighted likelihood, consistent with [@panteleev2024sliding]'s low-rate limit but not with its general form. Under a proper weighted MLE the pair-covariance baseline is expected to be competitive with or to surpass the calibrated SMC.
- **Metric choice.** Rate-estimation MSE against the ground-truth trajectory is one metric. The operationally relevant quantity is mean logical error rate under decoding with the inferred rates. A matched-prior experiment reporting that metric is the next study.

### 3.4 Cell indistinguishability at $T \le 5000$

All four phase-diagram cells ($\tau \in \{1, 3600\}$~s $\times\ \sigma_{\text{drift}} \in \{0.05, 0.20\}$) produce posterior means and MSEs identical to three significant figures. Two concurrent causes, neither a bug:

1. **Drift magnitude is dominated by noise at $T \le 5000$.** The root-mean-square drift-induced rate shift over 5000 shots at $\sigma_{\text{drift}} = 0.20$, $\tau = 1$~s is $\sim 1.6 \times 10^{-4}$ per edge, which is an order of magnitude below the filter's 100$\times$-mis-specified-prior migration distance of $\sim 9 \times 10^{-4}$. The filter's MSE is dominated by the prior-to-truth gap ($\sim 7 \times 10^{-7}$), not by drift-tracking error ($\sim 4 \times 10^{-8}$).
2. **Methodological consequence.** A drift-regime-dependent claim cannot be supported by this data at $T \le 5000$ with a prior of $\sigma_{\log} = 2.0$. Longer $T$ or a tighter prior would be required to make the cells distinguishable. This is listed as open work.

### 3.5 The covariance-variance floor bug

A latent bug in the pair-correlation shot-noise estimator (§2.2) produced inverted likelihood rankings on small-$H$ short-window fixtures before the Laplace-smoothing fix was applied. Specifically: at zero-fire detectors with an ad-hoc floor of $10^{-10}$, any non-trivial predicted covariance was penalised by a factor of $10^{-10}$ in the squared-error norm, giving wildly wrong $\theta$ values higher likelihood than the truth.

The bug is not detectable via standard numerical sanity checks — the code runs, the filter emits posterior samples, the MSE-on-MSE curves look smooth. It is exposed by the null-hypothesis test with two deliberately-placed particles (one at truth, one 100$\times$-wrong) on a deterministic fixture. The regression test asserts that the log-likelihood at truth exceeds the log-likelihood at 100$\times$-wrong by at least 1 nat on a small hand-built fixture, which catches the sign inversion immediately.

## 4 Discussion

The null-hypothesis test is a cheap, decisive diagnostic. It is one extra experimental run per estimator, costs nothing in wall-time beyond that, and distinguishes real filtering from prior-holding artefacts. We recommend it as a standard check for every published online noise-model estimator on QEC syndrome data. Reporting an estimator's gap-closed fraction under a 100$\times$-mis-specified prior is a strictly more informative summary than reporting its MSE on a matched-prior benchmark.

The Laplace-smoothing calibration for pair-covariance likelihoods generalises beyond QEC to any observation model with sparse-fire events and pair-correlation structure (network edge-prediction, event coincidence in particle physics, gene coexpression at low expression levels). The bug it fixes is easy to reintroduce, because the ad-hoc floor value of $10^{-10}$ is not obviously wrong on inspection; the fix is derived from an elementary prior-conjugate argument [@laplace1812theorie; @jeffreys1946invariant].

Sliding-window MLE with pseudo-inverse attribution is a surprisingly strong baseline. A linearised correlated-pair MLE underperforms it on our synthetic benchmark despite being more faithful to the published method of [@panteleev2024sliding]. Whether a proper weighted-likelihood correlated-pair MLE reverses the ordering, and whether any of these methods approach the adaptive-decoder performance of [@barnes2025lcd] on real syndrome data, are open questions.

Four open directions follow from this work. (a) A production-fidelity local clustering decoder [@barnes2025lcd] reimplemented as a comparator. (b) A head-to-head evaluation of the calibrated SMC against [@barnes2025lcd], [@panteleev2024sliding], and [@hillmann2024bayesian] on real device syndrome streams [@acharya2024willow; @zenodo13273331]. (c) A formal relationship between local clustering decoder updates and 1-particle SMC with a crude proposal distribution, which we conjecture exists. (d) Mean logical error rate under decoding as the operationally relevant metric, in place of rate-estimation MSE. Each of these is substantial follow-up work.

## 5 Conclusion

A null-hypothesis test applied to a naive sequential Monte Carlo noise-model estimator on QEC syndrome streams shows that the estimator does not filter at per-edge rate $p \approx 10^{-3}$; its posterior holds the prior regardless of the evidence. A calibrated SMC, built on a pair-covariance likelihood with a Laplace-smoothed shot-noise variance estimator, passes the test by closing 14 percent of a 100$\times$-mis-specified prior-to-truth gap in 5000 shots. The calibrated SMC does not beat a simple pseudo-inverse sliding-window MLE on rate-estimation mean-squared error on our synthetic benchmark, for three identifiable reasons any of which could be addressed in follow-up work. Per-shot informativeness comparisons between competing likelihoods are seed-fragile and require multi-fixture analysis. The null-hypothesis test, the Laplace-smoothing covariance-variance calibration, the seed-fragility observation, and the reference implementation with regression test suite are the contributions.

## 6 Data and code availability

The reference implementation, regression-test suite, raw numerical result tables, and figure-generation code are archived at the accompanying repository and at a Zenodo snapshot (DOI to be minted at submission). The Willow syndrome dataset used in exploratory analysis is publicly available at [@zenodo13273331].

## 7 Acknowledgements

We thank the open-source maintainers of Stim [@gidney2021stim; @stim_github] and PyMatching [@higgott2022pymatching; @pymatching2github] for the simulator and decoder infrastructure on which this work depends.

## References

1. P. Panteleev and G. Kalachev, *Adaptive Estimation of Drifting Noise in Quantum Error Correction*, arXiv:2511.09491 (2025).
2. T. Hillmann, T. Kapourniotis, and J. Roffe, *Bayesian Inference of Drifting Noise Model Parameters from Quantum Error-Correction Syndromes*, arXiv:2406.08981 (2024).
3. J. Bausch, A. W. Senior, F. J. H. Heras, and T. Edlich, *Per-Edge Detector Error Model Estimation from Streaming Syndromes*, arXiv:2504.14643 (2025).
4. O. Higgott and C. Gidney, *Sparse Blossom: Correcting a Million Errors per Core Second with Minimum-Weight Matching*, arXiv:2303.15933 (2023).
5. J. Barnes, C. Greganti, C. Chamberland, E. T. Campbell, et al. (Riverlane), *A Local Clustering Decoder for Real-Time Quantum Error Correction*, Nat. Commun. **16**, 2415 (2025).
6. R. Acharya, L. Aghababaie-Beni, I. Aleiner, et al. (Google Quantum AI), *Quantum Error Correction Below the Surface Code Threshold*, arXiv:2408.13687 (2024).
7. M. McEwen, L. Faoro, K. Arya, et al., *Resolving Catastrophic Error Bursts from Cosmic Rays in Large Arrays of Superconducting Qubits*, arXiv:2104.05219 (2022).
8. Google Quantum AI, *Suppressing Quantum Errors by Scaling a Surface Code Logical Qubit*, Nature **614**, 676–681 (2023).
9. A. G. Fowler, M. Mariantoni, J. M. Martinis, and A. N. Cleland, *Surface Codes: Towards Practical Large-Scale Quantum Computation*, Phys. Rev. A **86**, 032324 (2012).
10. P. W. Shor, *Scheme for Reducing Decoherence in Quantum Computer Memory*, Phys. Rev. A **52**, R2493–R2496 (1995).
11. A. Doucet, N. de Freitas, and N. Gordon (eds.), *Sequential Monte Carlo Methods in Practice*, Springer, 2001.
12. N. Chopin and O. Papaspiliopoulos, *An Introduction to Sequential Monte Carlo*, Springer Series in Statistics, 2020.
13. N. J. Gordon, D. J. Salmond, and A. F. M. Smith, *Novel Approach to Nonlinear/Non-Gaussian Bayesian State Estimation*, IEE Proc. F **140**, 107–113 (1993).
14. J. S. Liu and R. Chen, *Sequential Monte Carlo Methods for Dynamic Systems*, J. Amer. Statist. Assoc. **93**, 1032–1044 (1998).
15. A. Doucet, N. de Freitas, K. P. Murphy, and S. Russell, *Rao-Blackwellised Particle Filtering for Dynamic Bayesian Networks*, Proc. UAI, 176–183 (2000).
16. M. K. Pitt and N. Shephard, *Filtering via Simulation: Auxiliary Particle Filters*, J. Amer. Statist. Assoc. **94**, 590–599 (1999).
17. G. E. Uhlenbeck and L. S. Ornstein, *On the Theory of the Brownian Motion*, Phys. Rev. **36**, 823–841 (1930).
18. P.-S. Laplace, *Théorie analytique des probabilités*, Courcier, Paris, 1812.
19. H. Jeffreys, *An Invariant Form for the Prior Probability in Estimation Problems*, Proc. Roy. Soc. A **186**, 453–461 (1946).
20. C. Gidney, *Stim: A Fast Stabilizer Circuit Simulator*, arXiv:2103.02202 (2021).
21. O. Higgott, *PyMatching: A Python Package for Decoding Quantum Codes with Minimum-Weight Perfect Matching*, ACM Trans. Quantum Comput. **3**, 1–16 (2022), arXiv:2105.13082.
22. E. Dennis, A. Kitaev, A. Landahl, and J. Preskill, *Topological Quantum Memory*, J. Math. Phys. **43**, 4452–4505 (2002).
23. A. Yu. Kitaev, *Fault-Tolerant Quantum Computation by Anyons*, Ann. Phys. **303**, 2–30 (2003).
24. S. Bravyi, A. W. Cross, J. M. Gambetta, D. Maslov, P. Rall, and T. J. Yoder, *High-Threshold and Low-Overhead Fault-Tolerant Quantum Memory*, Nature **627**, 778–782 (2024).
25. R. Klesse and S. Frank, *Quantum Error Correction in Spatially Correlated Quantum Noise*, Phys. Rev. Lett. **95**, 230503 (2005).
26. P. V. Klimov, J. Kelly, Z. Chen, et al., *Fluctuations of Energy-Relaxation Times in Superconducting Qubits*, Phys. Rev. Lett. **121**, 090502 (2018).
27. J. J. Burnett, A. Bengtsson, M. Scigliuzzo, et al., *Decoherence Benchmarking of Superconducting Qubits*, npj Quantum Inf. **5**, 54 (2019).
28. C. Müller, J. H. Cole, and J. Lisenfeld, *Towards Understanding Two-Level-Systems in Amorphous Solids*, Rep. Prog. Phys. **82**, 124501 (2019).
29. B. Efron, *Bootstrap Methods: Another Look at the Jackknife*, Ann. Statist. **7**, 1–26 (1979).
30. A. Kong, J. S. Liu, and W. H. Wong, *Sequential Imputations and Bayesian Missing Data Problems*, J. Amer. Statist. Assoc. **89**, 278–288 (1994).
31. L. Skoric, D. E. Browne, K. M. Barnes, N. I. Gillespie, and E. T. Campbell, *Parallel Window Decoding Enables Scalable Fault-Tolerant Quantum Computation*, arXiv:2209.08552 (2022).
32. H. Bombín, D. Litinski, N. Nickerson, F. Pastawski, and N. Shutty, *Unifying Flavors of Fault Tolerance with the ZX Calculus*, arXiv:2303.08829 (2023).
33. Google Quantum AI, *Willow 105-Qubit Surface Code Syndrome Data (d=3/5/7)*, Zenodo doi:10.5281/zenodo.13273331 (2024).
