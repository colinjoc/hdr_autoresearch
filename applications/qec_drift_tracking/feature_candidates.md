# Feature Candidates — Drift-Aware Online Noise-Model Inference for QEC

Features / design variables grouped by role. Each is justified by its direct bearing on (a) the three-way SMC vs sliding-window MLE vs static Bayesian benchmark, (b) the phase-diagram success criterion, (c) the LCD-class adaptive-decoder comparison, (d) the Gidney-Ekerå-2025 FTQC sensitivity envelope (PER-2), or (e) PER-1 / PER-3. See `design_variables.md` for the decision-commitment table; this file is the brainstorm source.

## A. Filter-internal variables

### A1. Filter state dimension
Per-edge Pauli rates (X, Z separately) × number of edges in the Stim DEM + drift-kernel hyperparameters. At d=7: ~200–300 edges × 2 Pauli components = 400–600 stochastic dimensions before Rao-Blackwellisation, reducing to ~2 (kernel hyperparameters) with RBPF. **Justification:** controls the dim-curse risk; PRIMARY decision.

### A2. Drift-kernel parameterisation
Three candidate families:
- Ornstein-Uhlenbeck (1 timescale τ, 1 amplitude σ; Gaussian increments). Matches 2511.09491 assumptions.
- Piecewise-linear switching (TLS-motivated, heavy-tailed). Captures sub-second TLS switching.
- Piecewise-constant change-points with exponential waiting times. Matches bias-tee and cosmic-ray bursts.
**Justification:** mis-specified kernel = mis-specified filter; selecting the kernel is a key axis of the ablation study.

### A3. Proposal distribution
- Bootstrap (prior as proposal). Simple, vulnerable to dim-curse.
- Laplace-approximation around likelihood mode.
- Auxiliary particle filter (APF). Better when observation is informative.
- Block-diagonal Gaussian per-edge. Committed-to in proposal_v3 §3.
**Justification:** directly controls particle-degeneracy. PRIMARY design variable.

### A4. Rao-Blackwellisation structure
- Full RBPF: integrate per-edge rates analytically given kernel trajectory.
- Partial RBPF: integrate only "slow" edges, sample "fast" edges.
- No RBPF (reference for ablation).
**Justification:** effective-dimension reduction is the main trick enabling 10⁵ particles to work. PRIMARY.

### A5. Resampling schedule
- ESS-triggered at N/2 [Liu & Chen 1998].
- Fixed every-k-step.
- Adaptive based on weight-histogram bimodality.
**Justification:** balances weight-degeneracy vs sample-impoverishment.

### A6. Particle count N
Baselines N ∈ {10³, 10⁴, 10⁵, 10⁶}. Proposal_v3 commits to 10⁴ (d=5) / 10⁵ (d=7) with 10³ and 10⁶ as ablations.

### A7. Resampling algorithm
- Systematic (default, low variance).
- Residual.
- Stratified.
- Deterministic resampling [Li Bolic Djuric 2015].

### A8. Tempering schedule
- No tempering (standard).
- SMC-sampler-style bridging [Del Moral Doucet Jasra 2006] from prior to posterior per time-step.
- Annealed importance sampling warm-up.
**Justification:** mitigates high-dim degeneracy; defensive option for d=11+ future scaling.

### A9. Particle initialisation
- Uniform over prior support.
- Warm-start from sliding-window MLE estimate on first window.
- Warm-start from static Bayesian posterior mode.
**Justification:** initialisation can shave 10–100 updates off warm-up; worth testing.

### A10. Filter-update batch size
Number of QEC rounds consumed per filter update. Larger batches → more informative likelihoods, higher wall-clock, lower temporal resolution.

## B. Baseline variables (sliding-window MLE, static Bayesian, periodic DEM)

### B1. Sliding-window width (2511.09491 reproduction)
- Optimal window per 2511.09491 analytical formula.
- Fixed 1 min, 10 min, 1 hour (for ablation).
- Adaptive window based on empirical drift-rate estimate.

### B2. Sliding-window step
- 1 round stride (maximum overlap).
- 10-round stride.
- Full-window stride (no overlap).

### B3. Static Bayesian MCMC chain length (2406.08981 reproduction)
- Chain length N_chain ∈ {10³, 10⁴, 10⁵}; burn-in 25%.
- Proposal variance tuned by acceptance-rate target 25%.

### B4. Periodic-DEM refit cadence (proposal_v3 §4.2.a)
- Headline: 1 refit/hour (pinned).
- Control: 1 refit/min (upper-bound compute, not realistic).
- Never refit (static upper bound).

### B5. DEM estimation method (static baseline fourth-member)
- Per-edge MLE (arXiv:2504.14643).
- Differentiable MLE (arXiv:2602.19722).

## C. Decoder and LCD-baseline variables

### C1. Decoder backbone
- Reweighted PyMatching v2 (filter drives edge weights).
- Correlated matching [Fowler 2013].
- BP+OSD (for cross-check on qLDPC extensions).

### C2. LCD reimplementation fidelity parameters (PER-1)
- Cluster-size threshold.
- Adaptive-noise update rule (linear, exponential moving average).
- Boundary-handling protocol.
- FPGA-emulation vs CPU-only.
**Justification:** PER-1 reimplementation conformance is a publication-load-bearing number.

### C3. LCD adaptive-update cadence
- Per-round (production).
- Per-block (slower, simpler).
- Per-refit-cycle (slowest, compatible with our periodic-DEM framework).

### C4. Evaluation LER protocol
- Offline on pre-recorded syndrome streams (synthetic + Willow).
- Online simulation with filter-updated weights in the loop.

## D. Drift-kernel / phase-diagram variables

### D1. Timescale axis
Proposal_v3 commits {10 ms, 1 s, 1 min, 10 min, 1 h, 6 h}. Could extend to 10 h for super-slow bias-tee mode.

### D2. Amplitude axis
Proposal_v3 commits {5%, 10%, 20%, 50%} of per-edge rate.

### D3. Drift distribution shape
- OU stationary (Gaussian).
- Heavy-tailed TLS-switch (Poisson jump process).
- Hybrid OU + burst.
**Justification:** mis-specified drift family is a sensitivity axis.

### D4. Drift injection location
- Synthetic: inject OU drift onto Stim-generated syndromes.
- Real + injection: add synthetic drift onto Willow base statistics.
- Real only (if Willow's own within-run drift is detectable).

## E. Data-pipeline variables

### E1. Dataset slice
- Willow Zenodo 13273331 (primary).
- Rigetti Ankaa-2 Zenodo 13961130 (cross-vendor).
- Google 2022 Sycamore Zenodo 6804040 (cross-generation).

### E2. Experiment selection within Willow
- All 420 experiments (full).
- d=5 only (most statistics per edge).
- d=7 only (below-threshold data).
- Repetition-code d=29 (cleanest edge-level statistics).

### E3. Round-window pre-processing
- Raw per-round detector events.
- Hook-error-subtracted (remove intrinsic DEM correlations before drift estimation).
- Soft-information-weighted (if available in dataset).

### E4. Cross-shot aggregation
- Per-shot filter update.
- Per-block-of-K-shots aggregate.
- Per-experiment summary.

## F. Statistical-test / evaluation variables

### F1. Per-cell statistical test
- Paired t-test (proposal_v3 commitment).
- Bootstrap CI on LER difference.
- Bayes-factor per cell.

### F2. Multiple-comparisons correction
- Bonferroni across 24 cells (proposal_v3 commitment).
- Holm-Bonferroni.
- False-discovery-rate (Benjamini-Hochberg).

### F3. Effect-size definition
- Relative mean LER reduction (proposal_v3 commitment: ≥1%).
- Absolute LER reduction.
- Log-odds shift.

### F4. "Strict dominance" operationalisation
- ≥1% relative at 95% CI lower bound (proposal_v3 commitment).
- Cohen's d > 0.2.
- Stochastic dominance (first-order).

### F5. "Contiguous region" definition
- Rook-adjacency on the 6×4 grid.
- King-adjacency (includes diagonals).
- Requires connected-component area ≥10% of plane.

## G. FTQC-sensitivity variables (PER-2)

### G1. Resource-estimation algorithm
- Gidney-Ekerå 2025 RSA-2048 (proposal_v3 commitment).
- Azure Resource Estimator default workloads.
- Quantum-chemistry algorithm (benchmark-chem).

### G2. Per-cycle LER sweep range
- {0.5, 0.9, 0.95, 1.0, 1.05, 1.1, 2×} of default.
- Fine-grained {0.9, 0.92, 0.95, 0.97, 1.0, 1.03, 1.05, 1.08, 1.10}.

### G3. Resource metric
- Logical-qubit-seconds.
- Total magic-state count.
- Wall-clock runtime at fixed qubit count.

### G4. Sensitivity-envelope reporting
- σ-expressed ratio (Δresource / published-error-bar).
- Relative envelope (%-Δresource per %-ΔLER).
- Absolute (Δqubits / ΔLER at fixed target).

## H. Operational-territory variables (PER-3)

### H1. Fleet-scale parameter
- Production fleet size (devices in parallel production QEC).
- Drift-window-sensitivity fraction.
- Time-to-recalibration window.

### H2. Deployment-cost parameter
- Filter compute cost per update × updates/second.
- Periodic refit compute cost × refits/hour.
- Ratio (filter-total / refit-total) for operational cost comparison.

## Total variable count

- A: 10
- B: 5
- C: 4
- D: 4
- E: 4
- F: 5
- G: 4
- H: 2
- **Total: 38 variables (exceeds 15-variable minimum).**

Variables intended as Phase 2 committed-design axes (not ablations) are subset: {A1, A2, A3, A4, A6, B4, C2, D1, D2, F1, F2, F4, G1, G2, H1} — 15 committed, in line with proposal_v3.
