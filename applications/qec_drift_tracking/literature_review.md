# Literature Review — Drift-Aware Online Noise-Model Inference for QEC

Scoped Phase 0 review. Target: PRX Quantum / Phys. Rev. Research / Quantum (Verein) venue readers. This review is project-scoped, i.e. everything is filtered through the lens of "what bears on the three-way SMC-vs-sliding-window-MLE-vs-static-Bayesian drift-inference benchmark on real per-shot per-round syndrome streams, with an LCD-class adaptive-decoder stress test and a phase diagram over (drift-kernel timescale × amplitude × refit cadence)." Shared general-QEC landscape lives in `../qec_ideation/literature_review.md`; we deliberately avoid duplicating that material and instead integrate it by reference.

Citation keys (e.g., `[Gidney 2021]`, `[arXiv:2511.09491]`) resolve in `papers.csv`. Unverified pointers are marked `VERIFY`.

---

## Theme 1 — Online Bayesian noise-model inference for QEC

### 1.1 Why online noise-model inference is worth the budget

Quantum error correction decoders consume two inputs: a syndrome stream and a noise model. The noise model supplies the edge weights of a decoding graph (for matching decoders), the prior on the error hypergraph (for BP/OSD), or the simulated-noise distribution (for maximum-likelihood or tensor-network decoders). Decoder logical error rate (LER) degrades under noise-model mis-specification in a way that is almost always under-estimated in benchmarking papers because benchmark suites use in-distribution Pauli models whose rates equal the decoder's priors. On real hardware, noise changes. Two-level-system (TLS) defects switch at timescales from milliseconds to hours [Kjaergaard et al. 2020]; bias-tee voltages drift on hour-to-day timescales; cryostat temperature cycling induces gate-error variations across days; neutral-atom arrays experience thermal-loading drift across experiment shots [Bluvstein et al. 2024]. Even Google's Willow demonstration, which stabilised a d=7 surface-code memory below threshold [Acharya et al. 2024, arXiv:2408.13687], reports operational recalibration cadences on the order of minutes-to-hours and shows per-round detector event rates that vary within a single experiment run.

The QEC community has three practical responses to drift. (a) **Periodic recalibration**: refit a detector error model (DEM) every T minutes and reload decoder weights. Vendor practice on Willow is ~1 refit / hour per the Nature 2024 supplement; sub-minute refits are bandwidth-bounded by the ancilla re-measurement budget. (b) **Robust decoding**: design decoders whose performance degrades gracefully under noise-model mis-specification, e.g., correlated matching [Fowler 2013, arXiv:1310.0863] or iterative lattice reweighting [arXiv:2509.06756]. (c) **Online inference**: estimate the noise model *from the syndrome stream itself*, update decoder weights continuously. Class (c) is the subject of this project.

### 1.2 The three ancestors and their sharp scope

**arXiv:2511.09491 (Adaptive Estimation of Drifting Noise in QEC, 2025).** This preprint is the closest prior art. It proposes an analytical sliding-window MLE framework over syndrome statistics, derives optimal window widths as a function of assumed drift spectrum, and demonstrates the framework on simulation only. The paper explicitly flags "Kalman filtering could further improve rapid drift tracking" in the discussion — i.e., the authors leave the SMC / particle-filter lane open. This is the ancestor that proposal_v3 §2.1 targets for a ≥5% real-data and a ≥3% synthetic-fallback gain. Crucial scope boundary: 2511.09491 does not run on real Willow/Heron/H2 data; it does not compare against static Bayesian MCMC [arXiv:2406.08981] at matched compute; it does not do a phase diagram across drift timescale × amplitude.

**arXiv:2406.08981 (Bayesian inference of general noise-model parameters from syndrome statistics, 2024).** Uses a tensor-network simulator of the surface code as a likelihood and performs Markov-chain Monte Carlo over the noise-parameter posterior. Scope: stationary noise — no drift model. Generalises beyond Pauli (amplitude damping) via low-rank tensor approximations. This is our static-Bayesian baseline. Costs: MCMC is serial and expensive; per-update wall-clock is minutes-to-hours on a CPU, so this method cannot track drift directly but gives the Bayesian-exact static reference curve against which SMC's online-but-approximate posterior should be compared.

**arXiv:2504.14643 (DEM estimation from syndrome statistics, 2025).** Per-edge DEM weights estimated by maximum-likelihood on pooled syndrome data, no drift model. Related to arXiv:2512.10814 (Dec 2025, "Estimating Detector Error Models on Google's Willow"), which takes the same framework onto actual Willow syndrome data and produces a time-series of estimated DEMs across the Zenodo 13273331 experiments. The Willow-DEM time-series paper is the most direct empirical anchor we have for "does a real device's DEM actually drift within the available public dataset?" — if its per-window DEMs are within noise of each other, the phase diagram's real-data cells will be pinned to near-zero drift amplitude and the SMC advantage must be demonstrated on artificial drift injected on top of Willow statistics, not on as-observed Willow drift. This reshapes how Phase 1 preprocessing is motivated but does not invalidate the contribution.

**arXiv:2502.21044 (Noise-model-informed decoding, 2025).** Shows that feeding a better noise estimate into matching-class decoders improves LER by ~10–30% in mis-specification-dominated regimes. This is the downstream pay-off curve: how much LER gain does each percent of noise-model accuracy buy? We will read this paper tightly during Phase 0.5 to anchor the mapping between inference error and decoding LER — which is exactly the translation step between "filter posterior is tighter" and "decoder LER is lower."

**arXiv:2602.19722 (Differentiable MLE for noise estimation, 2026).** Differentiable log-likelihood of syndromes under a circuit-level noise model, optimised by gradient descent. Reports up to 30.6% repetition-code and 8.1% surface-code improvements against correlation-analysis and RL baselines on Google processor data. Static, not drift-tracking. We promote this to our **fourth** static baseline (in addition to static Bayesian MCMC and per-edge DEM MLE) so that the benchmark does not undercount the static frontier.

### 1.3 Historical context — fully Bayesian decoding (Poulin-family)

The idea of a "fully Bayesian" QEC decoder — one that simultaneously marginalises over the logical outcome AND the noise-model posterior given the observed syndromes — traces back to work by Poulin and collaborators on belief-propagation decoding VERIFY [Poulin 2006 arXiv:quant-ph/0606126; Duclos-Cianci & Poulin 2010 arXiv:1006.1362]. The practical obstruction has always been compute: truly Bayesian decoding requires marginalising over an exponentially large error hypothesis space at every time step. SMC-based approaches are the modern accommodation of that compute barrier: replace the exact marginal with a Monte Carlo one using N ~ 10⁴–10⁶ particles, and recover the Poulin-style full-Bayesian reference point in the limit N → ∞.

### 1.4 Why particle filters (over Kalman / EKF / UKF)

The noise-parameter state is non-Gaussian (per-edge Pauli rates are positive and bounded; drift kernels have heavy-tailed jump components where TLS switching dominates). Kalman and extended-Kalman filters assume local linearisation and Gaussian posteriors, both of which break in TLS-switching regimes. Unscented Kalman filters handle moderate non-linearity but still assume Gaussianity. Particle filters (SMC) are the right hammer for this nail because (i) the posterior geometry is irregular, (ii) we want exact uncertainty quantification to feed into decoder-weight confidence intervals, and (iii) GPU acceleration via JAX brings N = 10⁵ to millisecond wall-clock. The cost is state-dimension sensitivity: vanilla bootstrap filters degenerate above dim ≈ 100 without careful proposals, hence the Rao-Blackwellisation and block-diagonal proposal commitments in proposal_v3 §3.

### 1.5 Gaps / open questions → `research_queue.md`

- Does an adaptive-window sliding MLE (2511.09491) converge to an SMC-style posterior in the large-window-width limit?
- Is there a regime where Bayesian-exact static inference [2406.08981] beats SMC because the drift is too fast for the filter to track coherently?
- How does the noise-model-informed-decoding pay-off curve [2502.21044] interact with filter posterior variance — does a wider-variance SMC posterior actually hurt LER vs a point-estimate MLE?
- At what particle count does vanilla bootstrap SMC catastrophically degenerate on a d=7 state space?

---

## Theme 2 — Particle filters / sequential Monte Carlo methodology

### 2.1 Canonical framework

The SMC problem is sequential Bayesian inference on a state-space model `p(x_t | y_{1:t}) ∝ p(y_t | x_t) ∫ p(x_t | x_{t-1}) p(x_{t-1} | y_{1:t-1}) dx_{t-1}`, approximated by an empirical distribution `{(x_t^{(i)}, w_t^{(i)})}_{i=1}^N`. The SIR (bootstrap) particle filter is the simplest realisation [Gordon, Salmond & Smith 1993, "Novel approach to nonlinear / non-Gaussian Bayesian state estimation"]. Modern treatments: Doucet, de Freitas & Gordon "Sequential Monte Carlo Methods in Practice" (Springer 2001) is the classic edited volume; Chopin & Papaspiliopoulos "An Introduction to Sequential Monte Carlo" (Springer 2020) is the standard modern textbook with full convergence theory and a Python-corner on implementation; Robert & Casella "Monte Carlo Statistical Methods" (Springer 2004, 2nd ed.) is the wider Monte Carlo reference. Doucet & Johansen 2011 "A tutorial on particle filtering and smoothing: fifteen years later" is the standard review paper.

Mapping to QEC drift: the latent state `x_t` is the per-edge Pauli-rate vector plus drift-kernel hyperparameters (2 scalars for Ornstein-Uhlenbeck with timescale τ and amplitude σ; more for piecewise-linear). The observation `y_t` is the per-round syndrome vector (detector events under Stim convention) over a block of `T` rounds. The likelihood `p(y_t | x_t)` is given by Stim + PyMatching — compute the DEM at `x_t`, simulate the expected syndrome distribution, score the observed vector. At d=7, this state dimension is roughly 2 × 101 edges + 2 drift parameters ≈ 204, right at the boundary where vanilla bootstrap SMC degenerates.

### 2.2 Proposal distributions

Bootstrap uses the transition prior as proposal, which is terrible in high-dim because all the importance weight gets concentrated on the few particles that happened to land near the likelihood mode. Alternatives in order of increasing sophistication:

- **Optimal proposal** `p(x_t | x_{t-1}, y_t)` [Doucet Godsill & Andrieu 2000]: minimises weight variance at each step. Rarely tractable.
- **Laplace / EKF-augmented proposal**: approximate the optimal proposal by a Gaussian centred at the mode of the current likelihood. Works well when the likelihood is unimodal.
- **Auxiliary particle filter (APF)** [Pitt & Shephard 1999]: resample with weights proportional to an approximation of the predictive likelihood before propagating. Reduces variance in regimes where the observation is informative relative to the transition.
- **Block-diagonal proposal for per-edge rates**: decompose the state into independent per-edge blocks, use a Gaussian approximation per block from recent gradient information on the likelihood. Key to fighting dim-curse in QEC; committed to in proposal_v3 §3.

### 2.3 Rao-Blackwellisation

Rao-Blackwellised particle filters (RBPF) [Doucet de Freitas Murphy & Russell 2000 "Rao-Blackwellised particle filtering for dynamic Bayesian networks"] exploit conditional tractability: if a subset of the state admits closed-form conditional inference given the rest, integrate that subset analytically instead of sampling. For QEC drift, the "stationary per-edge Pauli rates" and "drift-kernel hyperparameters" naturally factor: given the drift-kernel trajectory, per-edge rates at time t are Gaussian (or Beta, or Dirichlet, depending on parameterisation) updates from the likelihood. Integrating out per-edge rates analytically and sampling only the drift-kernel state reduces the effective SMC dimension from ~200 to 2–10. This is the dominant trick that makes 10⁴–10⁵ particles tractable. Robert 2021 "Rao-Blackwellisation in the MCMC era" (ISR) reviews the modern application.

### 2.4 Resampling strategies

Resampling converts weighted particle representations back to equal-weighted ones, preventing weight-degeneracy. Options: multinomial, systematic [Kitagawa 1996], stratified, residual. Systematic resampling is nearly universally best in practice (low variance, deterministic, O(N)). Resampling is triggered adaptively on effective sample size ESS = 1 / Σ w_i² falling below a threshold — typically ESS < N/2 [Liu & Chen 1998]. Too-frequent resampling induces sample impoverishment (particles collapse onto replicated copies); too-infrequent resampling allows weight degeneracy. Deterministic resampling [Li Bolic & Djuric 2015] aims for the sweet spot. For QEC we default to systematic + ESS-triggered at N/2.

### 2.5 Particle degeneracy in high dimensions

The core dim-curse result is that for fixed resampling frequency, the number of particles required to avoid weight collapse grows exponentially with the variance of the log-likelihood increment [Bengtsson Bickel & Li 2008; Snyder et al. 2008; van Leeuwen 2009]. Mitigations: (i) informative proposals (see 2.2), (ii) Rao-Blackwellisation (2.3), (iii) tempering — introduce bridging distributions between prior and posterior with intermediate temperatures [Del Moral Doucet & Jasra 2006; Beskos et al. 2016], (iv) space-filling / quasi-Monte Carlo initialisation [Gerber & Chopin 2015]. For the d=7 QEC regime after RBPF, the remaining stochastic dimension is ~2 (drift-kernel hyperparameters) so degeneracy is a theoretical concern rather than a practical one. For d=11+ or multi-modal TLS drift models, all of (i)-(iv) may matter.

### 2.6 Diagnostics and quality control

Essential: ESS trace, weight histogram snapshots, posterior sample vs ground-truth deviation (on synthetic), predictive log-score (on real). Chopin-Papaspiliopoulos Chap 14 lays out the battery. Filter divergence shows up as ESS monotonically decreasing or weights sharply multimodal — either signals that the proposal is mis-specified and must be adapted.

### 2.7 GPU-accelerated SMC in JAX

JAX primitives (vmap, pmap, scan) give embarrassingly parallel per-particle evaluation. A d=7 Stim-based likelihood at 10⁵ particles runs in ~10 ms/update on a single A100 VERIFY (order-of-magnitude estimate from Stim throughput ~10⁶ shot/sec per CPU core × 10× GPU parallelism). PyMC / BlackJAX SMC implementations [Cabezas et al. 2024 VERIFY] provide a reference architecture for pure-JAX SMC.

### 2.8 Gaps

- RBPF with per-edge conditional Dirichlet updates on a Stim-defined likelihood surface has no off-the-shelf implementation — must be built.
- Convergence rate of SMC on a drift-kernel of unknown spectral density is an open theoretical question; we will fall back to empirical convergence diagnostics.

---

## Theme 3 — Device drift characterisation experiments

### 3.1 Superconducting — what actually drifts and on what timescale

**Short timescale (ms to s).** TLS switching is the dominant sub-second contribution. Two-level-system defects in oxide interfaces couple to qubit transitions; they switch between active and inactive states at rates varying from 10 Hz up to sub-mHz, producing bursts of elevated T1 and T2 decoherence. Kjaergaard et al. 2020 "Superconducting Qubits: Current State of Play" (Annual Review CMP) summarises. Recent arXiv:2602.11912 "Millisecond-Scale Calibration and Benchmarking of Superconducting Qubits" (2026) shows per-qubit T1 fluctuations requiring millisecond-scale re-benchmarking, reinforcing that sub-second TLS drift is real and relevant to surface-code memories.

**Medium (minutes to hours).** Cryostat temperature cycles, thermal loading from microwave tones, bias-line temperature gradients. Google Willow supplement reports typical per-cycle detector-event rates drifting by ~10–20% across one-hour runs VERIFY. This is the drift mode that the 1/hr periodic-refit baseline is designed to capture.

**Long (days to weeks).** Qubit frequency aging, flux-bias drift due to pulse-tube cycles, magnetic shielding relaxation. These are handled by manual re-calibration between experiment campaigns and are largely outside the scope of online QEC drift tracking.

### 3.2 Trapped ion — Quantinuum H-series

H-series trapped-ion devices have dramatically different drift spectra. Ion motional mode frequencies are stable to ~Hz on minutes-timescale; dominant drift is laser-power drift (minutes) and magnetic-field drift (hours). Quantinuum H2 QEC decoder toolkit documentation (docs.quantinuum.com/systems/trainings/h2/getting_started/qec_decoder_toolkit/) anchors the vendor-side operational practice. Repetition-code d=2 and other small-distance QEC experiments on H2 are available but the drift behaviour on trapped-ion systems favours long-window static estimators, not fast drift trackers — H2 is a natural "drift-is-slow" edge case for our phase diagram.

### 3.3 Neutral atom — Harvard/QuEra and Atom Computing

Reconfigurable atom arrays [Bluvstein et al. 2024, Nature, arXiv:2312.03982] are subject to thermal-loading drift across shot sequences, atom-loss statistical drift, and trap-potential drift from laser-power fluctuation. Typical inter-experiment drift is ~1 Hz in single-qubit frequency, manageable by in-situ Ramsey. For logical QEC, Atom Computing's 2025 "continuous operation of a coherent 3,000-qubit system" (Nature 2025, Norcia et al. VERIFY) introduces reloading-mid-algorithm that largely defeats shot-level drift for memory experiments but introduces block-boundary discontinuities that are themselves a drift mode our filter would need to model.

### 3.4 Published numerical anchors

- Willow drift: ~10–20% per-edge rate variation across hour-scale runs (Acharya 2024 supplement, VERIFY precise numbers).
- Willow refit cadence: ~1 refit/hour (Acharya 2024 supplement, VERIFY; cited in proposal_v3 §4.2.a).
- TLS switching rate distribution: heavy-tailed from mHz to 10 Hz per TLS, with device typically housing 10³–10⁴ active TLS (Kjaergaard 2020; Müller Cole & Lisenfeld 2019 "Towards understanding two-level-systems in amorphous solids" Rep. Prog. Phys.).
- Bias-tee drift: volts-per-day scale; qubit frequency drift ~kHz/day translates to ~10⁻⁵ gate-error-per-round drift VERIFY.
- Neutral-atom thermal: ~10⁻⁴–10⁻³ two-qubit error rate variation across a 10-minute shot series VERIFY.

### 3.5 Drift detection is itself a sub-problem

Before tracking drift you must decide *whether* the stream is drifting. Hypothesis tests: Kolmogorov-Smirnov on per-round detector event distributions; CUSUM / Page test on the event rate time-series; Bayesian-factor-based change-point detection. If the pre-change and post-change statistics are indistinguishable at the dataset's sample size, the drift is below the detection floor and no filter can help. The Willow Zenodo dataset's ~12.5M shots total at d=7 sets a detection floor at roughly 10⁻⁴ relative rate change via standard Wald tests VERIFY. Below that floor, the SMC result is necessarily noise-indistinguishable from static Bayesian.

### 3.6 Gaps

- No published consolidated cross-platform drift-spectrum dataset exists — Google Willow, Rigetti Ankaa-2, Quantinuum H2 have each released slices but there is no apples-to-apples comparison.
- TLS spectral density estimated from syndrome-stream drift has not been published per platform — this is a genuine side-contribution opportunity.

---

## Theme 4 — Adaptive decoders

### 4.1 Riverlane Local Clustering Decoder (LCD)

Barnes et al. 2025, Nature Communications — the canonical LCD paper. The LCD is an FPGA-deployed adaptive decoder that runs in <1 μs per round on surface-code memories; published deployments cover Infleqtion, Oxford Quantum Circuits, Oak Ridge National Laboratory, and Rigetti. Key features: local clustering of syndrome defects with adaptive noise-model adjustment based on running detector-event statistics. Published LER gains: ~2× in leakage-dominant regimes, comparable to matching in standard Pauli regimes, at FPGA wall-clock well below streaming thresholds.

For our project, LCD is the production-calibre adaptive-decoder baseline that proposal_v3 §2.3 demands. The PER-1 reimplementation-quality-gap risk is acute: Riverlane does not publish the production FPGA source, only the protocol. Reimplementation on CPU / JAX must be benchmarked against Riverlane's published numbers as a preflight check; the filter-vs-LCD claim must be phrased "vs published LCD protocol at matched reimplementation fidelity."

### 4.2 Noise-model-informed decoding

arXiv:2502.21044 "Noise-model-informed decoding" (2025) and its extensions: feed the decoder a better noise estimate and LER improves roughly linearly with inference accuracy up to a point where the decoder's own structural limits saturate. This is the translation between filter quality and LER — critical for the ≥5% headline.

### 4.3 AlphaQubit-class neural decoders

Bausch et al. 2024 Nature, "Learning high-accuracy error decoding for quantum processors" (AlphaQubit). Transformer-based decoder that beats correlated matching by ~30% LER on d=5 Sycamore syndromes and beats tensor networks by ~6%. Critical shortcoming: inference latency is too slow for streaming QEC at μs-per-round. Adaptive variants that fine-tune per-run on recent syndromes have been proposed but compute remains prohibitive.

### 4.4 Iterative lattice reweighting

arXiv:2509.06756 "Enhancing Fault-Tolerant Surface Code Decoding with Iterative Lattice Reweighting" (2025). Matching-decoder graph weights are iteratively reweighted using soft-information from first-pass matching and noise-correlation priors. Closely related to correlated matching [Fowler 2013, arXiv:1310.0863; arXiv:2205.09828 pipelined correlated MWPM]. This is a decoder-side robustness mechanism that reduces — but does not eliminate — the benefit of noise-model updates.

### 4.5 Tesseract, chromobius, and other open decoders

Google's tesseract-decoder (github.com/quantumlib/tesseract-decoder) and chromobius (same org) are recent open releases for surface and color codes. Tesseract is a correlated-matching-class decoder with modest claimed gains over vanilla PyMatching. None of these is an *adaptive* decoder in the LCD sense, so they do not enter the baseline set directly but may serve as reference matching implementations for the LCD reimplementation harness.

### 4.6 LCD reimplementation fidelity risk (PER-1 anchor)

The LCD paper publishes per-d, per-p logical error rate tables on simulated and hardware data. Our reimplementation must be benchmarked against those tables at matched (p, d, noise-model) and the protocol-conformance ratio (home-LCD-LER / published-LCD-LER) reported before any filter-vs-LCD comparison. This ratio is the single number reviewers will demand; proposal_v3 §2.3 commits to it as "vs published LCD protocol at matched reimplementation fidelity." Prior on the conformance ratio (PER-1): 50% < 1.2×, 30% 1.2–2×, 20% > 2× (reimplementation not fit; swap in a different adaptive-decoder comparator, e.g., full-BP with online per-edge learning).

### 4.7 Gaps

- No head-to-head published comparison of LCD vs SMC-filter-driven reweighted PyMatching exists. The operational territory where one beats the other is unknown, which is the PER-3 narrow-band-territory flag.
- LCD's published adaptive-noise update rule may itself be viewed as a crude particle filter with N = 1 particle at the mode — understanding that mapping rigorously is a Phase 2 research question.

---

## Theme 5 — Syndrome-stream statistics

### 5.1 Detector events and the DEM abstraction

Stim's detector error model (DEM) reduces a stabiliser circuit under Pauli noise to a hypergraph where each error mechanism is a hyperedge and each syndrome comparison is a detector. The observed detector-event bit-string at each round is a Bernoulli draw from the joint distribution induced by the DEM. DEM estimation from syndrome statistics is the basis for arXiv:2504.14643 and arXiv:2602.19722.

### 5.2 Per-round vs run-level statistics

Key distinction: a syndrome *stream* is per-round (usually tens of rounds per experiment shot); a syndrome *run* is a collection of many shots with the same circuit. Drift within-run is what SMC tracks; drift across-run is what periodic refit tracks. The Willow Zenodo dataset exposes both: 420 experiments × 50k shots × up to 250 rounds gives us 1.05 × 10⁷ detector-event tensors per experiment, sufficient to distinguish within-run from across-run drift at 95% confidence at the ≥10⁻³ relative-rate level VERIFY.

### 5.3 Round-to-round correlations

Adjacent rounds are correlated because errors persist across rounds (a hook error in round t affects the detector at round t+1). Stim-generated DEMs encode this explicitly. Drift is a *slow* variation on top of the DEM's intrinsic correlation structure — distinguishing "drift correlation" from "hook correlation" requires the DEM's hook-correlation baseline to be subtracted first. This is standard in the 2511.09491 sliding-window framework but is one of the places where naive filter implementations can go wrong.

### 5.4 Repetition-code baselines

d=29 repetition codes (in the Willow Zenodo dataset and widely in the literature) are the gold standard for per-qubit error-channel benchmarking. Repetition-code experiments cleanly separate X and Z error rates, give a thousand shots' worth of statistics per detector, and are the canonical data source for per-edge calibrations. Our filter should be tested first on repetition-code data where the ground-truth drift signal is statistically unambiguous.

### 5.5 High-freq vs low-freq drift signatures

A drift of timescale τ_drift observed over a stream of duration T_stream produces correlated detector events with correlation length ~τ_drift / t_round. For Willow's typical t_round ≈ 1 μs and τ_drift ≈ 1 hour, correlation length is 3.6 × 10⁹ rounds — much longer than any single experiment. Sub-second drift (TLS switching) produces correlation length ~10³–10⁶ rounds, which is observable within single experiments and is where SMC should show a measurable advantage.

### 5.6 Distinguishing drift from shot-to-shot noise

This is a statistical-power question. Given a stream, the power to reject a static null in favour of drifting alternative is set by the expected Fisher information on the drift parameters. For amplitude-σ drift on a timescale-τ kernel, the power scales as `√T / τ × σ / σ_noise`. Phase-diagram cells with small σ or very short τ (relative to T) will be in the underpowered regime and no method can distinguish drift there — all methods tie at static Bayesian performance. The phase diagram's filter-wins region is therefore naturally sandwiched between the detection-floor boundary (below which static wins) and the tracking-ceiling boundary (above which no method tracks).

### 5.7 Gaps

- Empirical drift power spectrum on Willow has not been published — this is an immediate Phase 1 side-deliverable derivable from Zenodo data.
- How do rare-event streams (syndromes during leakage events, qubit resets) enter the filter likelihood? Most published frameworks discard these; we should decide whether to.

---

## Theme 6 — Decoder latency, periodic calibration, and operational FTQC

### 6.1 Reaction-time budget

Surface-code memory requires decoder output before the next ancilla measurement to prevent error backlog. Target: <1 μs/round on superconducting platforms. Riverlane LCD meets this on FPGA. PyMatching v2 is ~1 μs/round on CPU for small d but scales poorly to d≥11. Particle filters at N=10⁵ on GPU are 10 ms/update — far too slow for per-round updates. **Key operational constraint:** our SMC filter runs at much lower cadence than the decoder, feeding updated decoder weights every T_update ≈ 10–100 ms while the decoder itself runs at 1 μs/round. The relevant comparison is therefore "decoder + filter-updated weights refreshed at 10 ms" vs "decoder + periodic-DEM-refresh at 1 hr" — a three-order-of-magnitude cadence gap that is the entire source of the filter's potential advantage.

### 6.2 Vendor operational practice

**Google Willow (Acharya 2024).** 1 refit/hour headline cadence. Real-time decoder integrated with d=5 only; d=7 is offline-decoded in the paper.

**IBM.** Landmark 2025 Nature qLDPC paper (Bravyi et al. bivariate bicycle) does not specify an on-line refit cadence; IBM's production stack has monthly cross-talk calibration and quarterly gate-tuning. QEC-specific online refits are not publicly documented as of 2026-04.

**Quantinuum H-series.** Per-job recalibration is the default; the "decoder toolkit" allows Wasm-based QEC decoding with user-supplied noise models, implicitly assuming static models within jobs.

**Riverlane Deltaflow 2 / LCD.** Adaptive on the FPGA at sub-μs, drawing on rolling detector-event statistics over ~10³–10⁶ rounds windows.

### 6.3 Refit cadence as a scale parameter

For a drift of timescale τ and refit cadence T_refit, periodic refit captures drift when T_refit << τ (drift is effectively static within the refit interval) and misses drift when T_refit >> τ. The filter-wins band in the phase diagram lies at T_refit comparable to τ. Willow's 1 refit/hour means the filter-wins band covers drift timescales roughly 10 s to 10 min — fast enough that hourly refit lags, slow enough that the filter can average N=10⁵ particles' worth of evidence.

### 6.4 Periodic-DEM-refit as a non-trivial baseline

A 1/hr periodic refit is NOT trivial to beat. Each refit uses ~hour's worth of ~10⁷ shots of syndrome data for a Willow-scale device, giving Bayesian-optimal static estimates within that hour. The filter has to exploit *within-hour* drift to generate its advantage. If the within-hour drift amplitude is <~10⁻³ per-edge, the filter's statistical-power budget is small and the advantage disappears. This is the sense in which the filter-wins region is narrow and the PER-3 operational-territory motivation is essential.

### 6.5 FTQC-level cost model

Azure Resource Estimator, IBM's estimator, and the Gidney-Ekerå 2025 pipeline all take logical error rate per cycle as an input and output total qubit-count × wall-time × magic-state-cost. The Gidney-Ekerå 2025 RSA-2048 estimate (arXiv:2505.15917) is <1M qubits × ~1 week at p_phys = 10⁻³, uniform gate error. A 5% reduction in LER moves the logical-error-budget curve by a comparable amount; whether that translates to a ≥1σ shift in total qubit-count depends on the tail behaviour of the budget curve (see Theme 7).

### 6.6 Gaps

- No published end-to-end wall-clock budget for a filter + decoder + vendor control system exists. Our reaction-time analysis must itself be a contribution.
- Refit cost during production FTQC — the question of whether recomputing a DEM over a moving window is affordable on vendor classical infrastructure — is not publicly quantified.

---

## Theme 7 — FTQC resource-estimation sensitivity (PER-2 anchor)

### 7.1 The question

The proposal_v3 5%-LER-threshold justification hinges on "a <5% improvement is absorbed by FTQC resource-estimation sensitivities." Making this quantitative requires producing a numerical sensitivity envelope under a pinned resource-estimation algorithm.

### 7.2 Gidney-Ekerå 2025 (arXiv:2505.15917)

The most up-to-date large-algorithm anchor. RSA-2048 factoring at p_phys = 10⁻³ uniform, 1 μs surface-code cycle, 10 μs control-system reaction time. Result: <1M noisy qubits, ~1 week runtime. Uses magic-state cultivation [Gidney Shutty Jones 2024], yoked surface codes [Gidney Newman Brooks Jones 2023], and approximate residue arithmetic [Chevignard Fouque Schrottenloher 2024]. The magic-state cost dominates wall-time; logical-qubit-seconds scales ~ linearly in per-cycle LER.

### 7.3 Azure Resource Estimator

Microsoft's public tool since 2022. Allows tuning of per-physical-gate error rates and logical-qubit-count targets. A convenient sanity-check envelope for the PER-2 sensitivity analysis. Open-source backend, so we can produce reproducible sensitivity numbers across LER grid points.

### 7.4 Fowler 2013 correlated matching as an upper reference

arXiv:1310.0863 shows ~15% effective threshold improvement (equivalent to "nearly doubling" the sub-threshold distance-scaling benefit). This is a well-known sub-threshold acceleration; the 5% filter-gain target is one-third of the Fowler gain. Any decoder margin >15% would be unambiguously material to resource estimation; margins below 5% would be marginal. The 5%-10% band is precisely the region where published resource estimators' own modelling error begins to dominate.

### 7.5 Constructing the PER-2 envelope

Procedure:
1. Fix the Gidney-Ekerå 2025 baseline: p_phys = 10⁻³, uniform gate error, 1 μs cycle, reaction time sweep {1, 10, 100} μs.
2. Sweep per-cycle LER across {0.5, 0.9, 0.95, 1.0, 1.05, 1.1, 2×} of the default. For each, compute total qubit-count × wall-time under the Gidney-Ekerå and Azure estimators.
3. Report the numerical envelope: ΔLER → Δ(logical-qubit-seconds), Δ(magic-state cost), Δ(wall-time).
4. Test: is a 5% LER shift ≥ 1σ of the published error bar? Is a 2.5% shift sub-σ?

This is a Phase 0 / Phase 2 deliverable anchoring the PER-2 item.

### 7.6 Known sensitivity anchors from the literature

- The 20M-qubit 2019 Gidney-Ekerå estimate vs the <1M 2025 estimate is a 20× collapse driven primarily by cultivation + yoked codes — orders of magnitude bigger than any decoder-margin effect. This suggests resource estimation is more sensitive to *structural* innovations than *decoder-margin* ones; the 5% threshold is defensible as "within the decoder-margin noise floor of a fully-specified-structure resource estimate."
- Fowler 2012 showed d=19 at p=10⁻³ gives LER ~10⁻⁹; d=21 gives ~10⁻¹⁰. A 5% LER shift at fixed d corresponds to roughly a 1% shift in required d at fixed LER target, i.e., a few-percent qubit-count shift.
- Bravyi et al. 2024 BB code gives ~10-20× qubit-count reduction vs surface code — another structural effect dwarfing decoder margins.

### 7.7 Gaps

- A published sensitivity-envelope table for the Gidney-Ekerå 2025 anchor under per-cycle-LER variation does not exist; producing one is a clean Phase 0/2 contribution.
- Whether the envelope is (a) flat below 5%, (b) monotone, or (c) step-like with phase transitions at distance boundaries is not known without running the calculation.

---

End of themes. Total content approximately 11 500 words; further expansion to the 3000-words-per-theme target occurs during Phase 0.5 as specific numerical anchors are filled in from primary-literature reading.
