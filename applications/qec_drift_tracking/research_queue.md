# Research Queue — qec_drift_tracking

Status: **Phase 0 completed 2026-04-20**. PER-1/2/3 from Phase 0.25 preserved verbatim. 100 additional Phase-0-literature-review hypotheses populated below. Data-access smoke test PASSED (see `data_sources.md`).

---

## Pre-empt-reviewer items (from Phase 0.25 publishability re-review v3)

These are the top three killer objections / soft spots identified by the Phase 0.25 reviewer at PRX Quantum on `proposal_v3.md`. Every one must be addressed in the Phase 2 experiment plan, pro-actively.

### PER-1 [pre-empt-reviewer] LCD-reimplementation quality-gap benchmark
- **Objection:** The §2.3 LCD-class baseline commitment says "closest open reimplementation; else published-algorithm reimplementation with version-controlled protocol". Riverlane production code may not be public, so a home reimplementation of the Local Clustering Decoder risks under-performing the production decoder, biasing the comparison AGAINST the LCD baseline — making the filter look better than it really is relative to production-quality adaptive decoders.
- **Required action (before filter-vs-LCD runs):** Benchmark the LCD reimplementation against published Riverlane benchmarks (Nat. Commun. 2025). Report a protocol-conformance gap numerically (e.g., LER ratio at matched (p, d) against Riverlane-published numbers). Phrase the filter-vs-LCD claim in the manuscript as **"vs published LCD protocol at matched reimplementation fidelity"**, not "vs Riverlane production LCD."
- **Design variable:** LCD reimplementation fidelity (protocol version, FPGA-vs-CPU equivalence).
- **Metric:** conformance ratio = (home LCD LER) / (published Riverlane LCD LER) at matched (p, d).
- **Baseline:** Riverlane 2025 Nat. Commun. published numbers.
- **Prior:** 50% the conformance gap is <1.2× (acceptable reimplementation); 30% 1.2–2× (must caveat); 20% >2× (reimplementation not fit for baseline — pivot to a different adaptive-decoder comparator).

### PER-2 [pre-empt-reviewer] 5%-threshold FTQC-sensitivity envelope
- **Objection:** The §2.1 "5% threshold justification" cites Fowler 2013 (~15%), Riverlane LCD (~2×), and Gidney–Ekerå 2025 reaction-time resource-estimation sensitivity — but no numerical sensitivity envelope is computed. A tough PRX Quantum reviewer will ask "quantify exactly how the Gidney–Ekerå 2025 reaction-time axis absorbs a 5% improvement" and the proposal currently answers qualitatively.
- **Required action (Phase 0 / early Phase 2):** Numerically compute the FTQC resource-estimation sensitivity envelope under a pre-registered algorithm (e.g., RSA-2048 factoring per arXiv:2505.15917). Show that a ≥5% mean-LER improvement shifts a resource-estimation-grade metric (logical-qubit-seconds or total magic-state cost) by a numerically meaningful amount (say, ≥1 σ of the published error bar), and that a <5% improvement does not.
- **Design variable:** sensitivity-envelope calculation protocol.
- **Metric:** |Δ(logical-qubit-seconds)| / σ(Gidney–Ekerå 2025) as a function of LER improvement.
- **Baseline:** Gidney–Ekerå 2025 arXiv:2505.15917 published envelope.
- **Prior:** 65% the envelope confirms 5% is the correct threshold; 25% it suggests a higher threshold (8–10%) is more defensible; 10% it suggests 5% is too tight and we should report a wider headline.

### PER-3 [pre-empt-reviewer] Narrow-band operational territory motivation
- **Objection:** The §2.2 phase-diagram success criterion (contiguous 10% of plane) is tight, but reviewers at PRX Quantum will ask "why is 10% of a (timescale × amplitude) plane the operationally relevant territory, not a boutique sliver?" without a deployment-value argument.
- **Required action (paper draft §Discussion):** Motivate the contiguous-10% criterion in terms of operational deployment value — product of (time-to-recalibration-window in drift-fleet operations) × (fleet scale of devices drifting across the relevant band). Frame the filter-wins region as publishable territory, not a narrow band between refit cadence and slowest drift mode.
- **Design variable:** operational-relevance argument structure.
- **Metric:** qualitative — do Gidney/Higgott/Riverlane-style reviewers read the 10% region as "a meaningful operating regime" or "a boutique sliver"?
- **Baseline:** Willow 2024 operational cadence (1/hr refit) as the reference regime.
- **Prior:** 70% the argument lands on first try; 30% requires a second iteration to land convincingly.

---

## Phase 0 deep-literature-review hypotheses

Populated 2026-04-20 after Phase 0 deep scoped lit review. 97+ additional items below; PER-1/PER-2/PER-3 are preserved verbatim above.

### Filter methodology

- H1. RBPF reduces effective stochastic dimension from ~200 to ~2 under OU drift kernel; verify numerically that ESS traces track Chopin-Papaspiliopoulos Chap. 10 predictions.
- H2. Block-diagonal Gaussian proposal outperforms bootstrap at N=10⁴ in every phase-diagram cell, measured by ESS stability and posterior-MSE on synthetic truth.
- H3. APF (auxiliary particle filter) is an ablation with second-order wall-clock cost; test whether it closes the gap to the Laplace-optimal proposal on TLS-switch regimes.
- H4. Tempering [Del Moral Doucet Jasra 2006] is unnecessary at d=5/7 but becomes load-bearing at d=11 — predict dim-curse transition empirically.
- H5. ESS-triggered systematic resampling is uniformly best across cells; residual resampling is a near-identical second; stratified is worse by ~5% posterior MSE.
- H6. Warm-starting from sliding-window MLE output on the first window reduces filter warm-up from 100 to ~20 updates — measure.
- H7. Filter posterior variance correlates monotonically with decoder LER — verify that wider posteriors hurt downstream LER and tighten the PER-1 translation curve.
- H8. Optimal filter-update batch size is 10–50 rounds, not 1 — larger batches trade temporal resolution for likelihood informativeness.
- H9. Particle count scaling: N = c × exp(var(log-lik)) with c ~ 10³; for 2-dim RB state and 10⁻² per-edge rate, var(log-lik) ≈ 3, so N ~ 10⁴ suffices.
- H10. Rao-Blackwellising only the slowest-drifting edges (partial RBPF) recovers 80% of the computational saving at 95% of the accuracy — test tradeoff.

### Drift-kernel specification

- H11. OU-parameterised drift matches Willow per-run drift to within χ² goodness-of-fit at the data detection floor.
- H12. Piecewise-linear-with-jumps drift matches TLS-switching regimes better than OU — verify on synthetic TLS-mode data.
- H13. Hybrid OU + Poisson-jump drift kernel is the dominant real-world model; test on Willow's repetition-code d=29 detector event time series.
- H14. Mis-specifying drift kernel (OU ↔ piecewise) costs ≤5% LER in the filter-wins region — acceptable robustness.
- H15. Drift-kernel hyperparameters (τ, σ) converge to posterior mode within 1 hour of live data.
- H16. Cosmic-ray burst events [McEwen 2022] introduce drift modes outside any single-family kernel; may require an explicit burst-detection preprocessor.
- H17. Heavy-tailed TLS-switching produces non-Gaussian posterior on drift amplitude — Laplace proposal under-covers; SMC fixes it.
- H18. Drift-kernel hyperparameters are identifiable from 10³ rounds of syndrome data at d=5 per power-analysis calculation.
- H19. Prior mis-specification (Beta(2,2000) too narrow vs too broad) costs ≤2% LER if posterior converges within 100 updates.
- H20. Temperature-dependent drift-kernel amplitude (cryostat thermal cycle) is a separable covariate; factor out before filter.

### Baselines

- H21. Sliding-window MLE [2511.09491] with optimal window width matches static Bayesian within 1% LER in stationary cells.
- H22. Static Bayesian [2406.08981] is Bayes-optimal on stationary cells and provides a Pareto-frontier reference.
- H23. Differentiable MLE [2602.19722] is within 2% of static Bayesian MCMC at 10× lower wall-clock — use as static-baseline proxy where MCMC is infeasible.
- H24. Per-edge DEM MLE [2504.14643] underperforms static Bayesian by ≥5% in amplitude-damping regimes — document where each is appropriate.
- H25. LCD adaptive-update rule [Riverlane 2025] is effectively a 1-particle SMC with a crude proposal — formalise the mapping.
- H26. 1/hr periodic DEM refit captures ≥90% of drift-driven LER at drift timescale >1 hr; filter-wins band is narrower than 1 hr timescale.
- H27. The 1/min cadence control baseline is compute-infeasible on current vendor hardware but is a clean upper bound on what periodic refit could achieve.
- H28. Never-refit baseline (pure static) loses ≥15% LER relative to 1/hr in hour-drift regimes — confirm on synthetic.
- H29. The four static baselines (static Bayesian MCMC, per-edge MLE, dMLE, periodic-DEM 1/hr) cluster within 3% LER on stationary cells.
- H30. Correlated-matching [Fowler 2013] itself provides robustness to drift at 5-10% mis-specification — quantify and subtract before claiming filter advantage.

### Phase-diagram and statistical power

- H31. Willow within-run drift is below the Wald detection floor of ~10⁻⁴ relative rate change at 95% CI → real-data phase diagram uses injected-synthetic drift on Willow base statistics.
- H32. Filter-wins band lies at drift timescale τ ∈ [10 s, 10 min] × amplitude ≥ 10% — roughly 6 of 24 cells, meeting contiguous-10% criterion.
- H33. Bonferroni correction across 24 cells makes per-cell α = 0.002, requiring ~10⁶ shots per cell to detect 1% LER difference at 80% power.
- H34. Rook-adjacency contiguous region is achievable if filter wins in adjacent (τ, amp) cells; king-adjacency is easier but harder to motivate.
- H35. The detection-floor boundary and tracking-ceiling boundary together sandwich a filter-wins ridge running diagonally on the phase diagram.
- H36. Cells with drift timescale τ < 10 × filter update period are all filter-dominated (filter can track); τ > refit_cadence are all refit-dominated.
- H37. Amplitude ≥50% cells are extreme and likely operationally unrealistic — include for completeness but flag as outside PER-3 territory.
- H38. Phase-diagram shape is approximately independent of code distance d=5 vs d=7 — verify as a robustness claim.
- H39. Cross-vendor phase-diagram comparison (Willow vs Rigetti Ankaa-2) reveals platform-specific filter-wins regions.
- H40. Bootstrap CIs on per-cell LER differences stabilise at ~10⁴ bootstrap draws; use this as the reporting protocol.

### LCD baseline and PER-1

- H41. Home-LCD protocol-conformance ratio at (p=10⁻³, d=5) matches Riverlane published number within 1.2× (50% prior per PER-1).
- H42. LCD FPGA-vs-CPU equivalence is within 2× in LER; CPU reimplementation suffices for publication.
- H43. LCD adaptive-update cadence matters — per-round LCD dominates per-block LCD by 10% LER.
- H44. Filter-driven matching vs LCD at matched wall-clock: filter wins in slow-drift regimes, LCD wins in leakage-dominated regimes.
- H45. Combining filter + LCD (filter feeds noise-estimate to LCD's adaptive branch) is strictly better than either alone — test as a bonus result.
- H46. LCD's own adaptive-noise update is a 1-particle SMC whose formal upgrade to N=10⁵ SMC recovers the filter — clean theoretical bridge.
- H47. If LCD reimplementation conformance >2×, swap in a BP-with-online-per-edge-learning baseline as a published-algorithm alternative.
- H48. LCD and filter complement rather than compete at fleet-scale: filter feeds LCD clusters, LCD does latency-critical decoding — operationalise this in PER-3 narrative.

### FTQC sensitivity and PER-2

- H49. The Gidney-Ekerå 2025 qubit-count × wall-time envelope is approximately log-linear in per-cycle LER over the range 0.9×–1.1× default.
- H50. A 5% LER improvement shifts total logical-qubit-seconds by ≥1σ of published uncertainty → PER-2 threshold is defensible.
- H51. A 2.5% improvement is <1σ → below-5% margins are absorbed → 5% floor is correct.
- H52. Azure RE gives the same envelope qualitatively — cross-validates Gidney-Ekerå.
- H53. Chemistry benchmark (FeMoCo or similar) gives a more sensitive envelope than factoring — report both.
- H54. Magic-state cost dominates wall-time; LER improvement at idling logical qubits buys less than at computing ones.
- H55. Distance-boundary step in resource-envelope at d=21 (e.g.) is an artifact that can obscure or inflate LER sensitivity — handle carefully.
- H56. Reaction-time axis (1 μs, 10 μs, 100 μs) sweeps show filter-latency-dependent envelope: 100 μs filter update is OK, 1 ms is NOT.

### Operational territory and PER-3

- H57. Time-to-recalibration window × fleet scale gives 10⁶ device-minutes/day in filter-relevant drift regime — operationally meaningful.
- H58. Narrow-band (10 s – 10 min drift × 5–20% amplitude) covers 20–30% of realistic production-drift spectra — fleet-level publishable.
- H59. Filter deployment cost: 1 GPU per device at 10 ms update cadence → $10³ classical-compute per quantum device at 2026 prices — affordable.
- H60. Periodic refit cost: ancilla qubits consumed for DEM refit scale with distance-squared — refit-every-minute is prohibitive at d=11+.
- H61. Fleet-scale scaling: 10⁴ devices × 1 GPU each is plausible by 2028; filter-level classical budget is not the limiter.
- H62. LCD + filter hybrid is the production-stack logical endpoint — PER-3 argument aligns the paper with Riverlane-Deltaflow-2 trajectory.

### Data access, preprocessing, and smoke-test follow-ups

- H63. Willow Zenodo 13273331 timestamps have per-run resolution, not per-shot → hour-scale drift is observable, sub-hour is not without run-aggregation assumptions.
- H64. Rigetti Ankaa-2 dataset has finer per-shot timestamps than Willow → different drift-resolution tradeoff.
- H65. Willow rep-code d=29 stream gives cleanest per-edge statistics for kernel-parameter identification — preprocess this first.
- H66. Hook-error subtraction from DEM before drift estimation is essential; verify that un-subtracted streams produce spurious drift signals.
- H67. Leakage-event filtering: whether to include or exclude leakage-marked syndromes in the filter likelihood — test both.
- H68. Classical memory footprint: 112.5 GB Willow data → local SSD staging plan; streaming I/O to avoid full load.
- H69. Stim-circuit compatibility across Zenodo archives: check all README's for circuit-format version consistency.
- H70. CC-BY 4.0 licence enables our open-source companion repo; confirm Rigetti licence during Phase 0.5 ingest.
- H71. Willow DEM time-series from arXiv:2512.10814 is a direct baseline to reproduce — invite authors or reimplement.

### Cross-method theory and formal

- H72. SMC posterior converges to static Bayesian in limit of zero drift — verify analytically.
- H73. Sliding-window MLE converges to SMC posterior in limit of wide window on stationary data — verify.
- H74. Particle filter is Bayes-optimal among causal methods at matched state space — cite Bain-Crisan stochastic filtering theory.
- H75. Bayes-factor comparison between drift-on vs drift-off models gives a drift-detection test complementary to CUSUM.
- H76. Filter posterior on drift hyperparameters (τ, σ) provides a natural drift-characterisation by-product — document as a side-deliverable.
- H77. Mutual information between drift-kernel trajectory and syndrome stream upper-bounds filter performance — compute as a theoretical benchmark.

### Platform-specific predictions

- H78. Willow superconducting: filter-wins band at τ ∈ [10 s, 10 min], amp ≥10%.
- H79. Rigetti Ankaa-2: similar band but shifted to longer τ due to different TLS density.
- H80. Quantinuum H2 trapped-ion: filter-wins region is very narrow; trapped-ion drift is dominated by minute-scale laser servo loops.
- H81. Atom Computing neutral-atom: reload-block boundaries introduce non-stationarities that need separate handling.
- H82. Cross-platform generalisation: filter trained on Willow transfers to Rigetti with minimal kernel-parameter retuning if drift family is OU.

### Decoder integration

- H83. Reweighted PyMatching v2 is the right default; no extra decoder innovation needed for the headline.
- H84. AlphaQubit-class decoders [Bausch 2024] fine-tuned to filter posterior is a future direction — out of Phase 2 scope.
- H85. Tesseract decoder [quantumlib] at correlated-matching weights gives a modest robustness floor — include as an ablation baseline.
- H86. BP+OSD for qLDPC drift-tracking is a future extension — surface-code first.
- H87. Union-find decoder gives near-identical result to MWPM for d=5/7 at streaming budget — use for FPGA-emulation proxy.

### Risk and robustness

- H88. Filter failure mode: weight collapse under observation shock (sudden large-amplitude drift) — design fallback to MLE warm-start.
- H89. Filter mis-specification risk: wrong drift-kernel family → quantify sensitivity analysis per H14.
- H90. Likelihood mis-specification risk: Stim-generated likelihood assumes Pauli noise; real Willow has leakage → robustness analysis with leakage-contaminated likelihood.
- H91. Compute budget failure: if GPU SMC is slower than estimated, re-scope to 10⁴ particles and accept wider posteriors.
- H92. Statistical-power failure: if per-cell sample size is insufficient after Bonferroni, reduce phase-diagram grid to 4×3 = 12 cells.

### Open side-deliverables (potential Phys. Rev. Research notes)

- H93. Willow drift power-spectrum: empirical PSD of per-edge rates from arXiv:2512.10814 + our re-analysis — standalone note.
- H94. Cross-platform drift taxonomy: first consolidated table of drift timescales × amplitudes by platform.
- H95. LCD ↔ SMC formal equivalence: N=1 particle mapping and what it tells us about production-FPGA adaptive design.
- H96. RBPF implementation note: open-source JAX RBPF for QEC drift, documented architecture.
- H97. PER-2 FTQC envelope: standalone resource-estimation sensitivity table under Gidney-Ekerå 2025.

### Meta / programme

- H98. Replication test: re-run our filter on arXiv:2512.10814's published DEM time-series to verify that their DEMs match our posterior modes.
- H99. Peer-review pre-empt: commit to a pre-registered phase-diagram result before any real-data filter runs; publish pre-registration as a Zenodo DOI.
- H100. Open-source companion: release all code, drift-kernel configs, LCD reimplementation, phase-diagram raw data on GitHub under MIT, per proposal_v3 §8.

---

**Hypothesis count: 100 (plus 3 PER items = 103 total).**
**Coverage: filter methodology (H1-H10), kernel specification (H11-H20), baselines (H21-H30), phase diagram (H31-H40), LCD (H41-H48), FTQC (H49-H56), operational territory (H57-H62), data (H63-H71), theory (H72-H77), platform (H78-H82), decoder integration (H83-H87), risk (H88-H92), side-deliverables (H93-H97), meta (H98-H100).**
