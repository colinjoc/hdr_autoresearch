# Knowledge Base — qec_drift_tracking (project-scoped)

Stylised facts and numerical anchors specific to the drift-tracking project. General QEC facts live in `../qec_ideation/knowledge_base.md` and are integrated by reference. Numbers flagged VERIFY need primary-source re-check during Phase 0.5 or Phase 1. All timescales and rates are approximate.

## Drift timescales by platform

### Superconducting (Willow, Sycamore, Heron, Rigetti Ankaa-2, OQC)

- **Sub-second TLS switching.** Active TLS defects switch at 10⁻³–10¹ Hz per defect; device typically houses 10³–10⁴ active TLS. Observed T1 fluctuations on ms timescale per [arXiv:2602.11912]. Burnett et al. 2019 (npj QI) report 10%–30% T1 variation over minutes.
- **Minutes.** Thermal loading, bias-tee relaxation, microwave-cable drift. Gate-error variation ~1–5% per hour during active use.
- **Hours.** Cryostat temperature cycles, pulse-tube compressor cycles, shielding relaxation. Willow 2024 reports recalibration at ~1/hour. Per-edge DEM rates drift ~10–20% across hour-scale runs (Acharya 2024 supplement, VERIFY).
- **Days.** Qubit frequency aging; dilution-fridge dewar warming cycles. Manual recalibration territory.
- **Cosmic-ray burst events.** Rare (hours-to-days), correlated across multiple qubits, order-of-ms duration; [Martinis 2021, McEwen 2022].

### Trapped ion (Quantinuum H2, IonQ)

- **Seconds.** Laser-power drift (~10⁻³ per minute), dominated by servo-loop performance.
- **Minutes.** Magnetic-field drift (milligauss scale) → Zeeman shift → rotation-gate miscalibration.
- **Hours.** Trap-potential drift due to electrode charging. Re-calibrated between jobs.
- **Net:** dominant drift mode is 10–100 s; long integration windows work well; static and slow-drift methods dominate.

### Neutral atom (Harvard/QuEra, Atom Computing)

- **Shot-to-shot.** Atom-loading statistical variation; trap-depth drift due to laser power fluctuation.
- **Minutes.** Thermal loading from high-intensity beams; dipole-trap drift.
- **Hours.** Vacuum-chamber outgassing cycles; magnetic-coil thermal drift.
- **Block boundaries.** Reloading events (Atom Computing 2025) introduce step discontinuities in noise parameters.

## Published refit cadences (vendor operational practice)

- **Google Willow 2024:** ~1 refit/hour (headline); real-time decoder at d=5 refreshed per-experiment-block, d=7 offline-decoded. [Acharya 2024 supplement, VERIFY precise cadence.]
- **IBM Quantum:** per-job DEM fit; cross-talk calibration monthly; gate-tuning quarterly. No published per-round DEM refit cadence.
- **Quantinuum H-series:** per-job recalibration; QEC decoder toolkit assumes static noise within jobs.
- **Riverlane Deltaflow 2 / LCD:** sub-μs FPGA adaptive; noise-model adjustment from rolling 10³–10⁶ round windows.
- **Atom Computing:** per-block recalibration after atom reload.

## Filter convergence heuristics (from SMC literature)

- **Effective sample size threshold**: resample when ESS < N/2 [Liu & Chen 1998]. Resampling too often induces sample impoverishment; too rarely induces weight degeneracy.
- **Particle count scaling under dim-curse**: N ~ exp(var(log-likelihood)) [Bengtsson Bickel Li 2008]. For our RBPF with 2-dim remaining drift state, N = 10⁴–10⁵ gives ESS > 10³ after 100 updates on expected-drift regimes.
- **Warm-up**: ~100 × τ_update steps from a diffuse prior to converged posterior. For 10 ms filter updates, allow ~1 s of live data before decoder-reweighting is trusted.
- **Degeneracy catastrophes**: if ESS drops to ~1 and never recovers, the filter has lost contact with truth — force global resample from diffuse prior or trigger a re-initialisation from a recent sliding-window MLE estimate.

## LCD numerical benchmarks (PER-1 anchors)

From Riverlane LCD Nature Comm. 2025:
- Sub-1 μs per round on FPGA, surface code d≤7 VERIFY.
- ~2× LER reduction vs matching in leakage-dominant regimes VERIFY.
- ~match with vanilla MWPM in Pauli-dominated regimes.
- Published benchmarks: expect tables at (p=10⁻³, d=5) and (p=10⁻³, d=7) with logical error per round VERIFY.

**Reimplementation risk**: Production FPGA code not public. Protocol published. Expected conformance ratio (home/production): 50% < 1.2×, 30% 1.2–2×, 20% > 2× (per PER-1 prior).

## Fowler 2013 anchor (PER-2 / 5%-threshold justification)

- Correlated matching [arXiv:1310.0863]: ~15% effective-threshold improvement vs vanilla MWPM.
- Sub-threshold distance scaling: correlated matching "nearly doubles" the LER-reduction benefit of incrementing distance.
- Interpretation for PER-2: 15% is an upper bound on the kind of decoder-margin gain QEC literature treats as unambiguously material. A 5% gain is roughly one-third of that — it should be similarly detectable if FTQC estimation was linear in LER, but is in the grey zone where resource-estimation modelling error begins to compete with the signal.

## Gidney-Ekerå 2025 anchor (PER-2 envelope target)

From [arXiv:2505.15917]:
- Resource estimate: <1M noisy qubits × ~1 week runtime for RSA-2048.
- Assumptions: p_phys = 10⁻³ uniform, 1 μs surface-code cycle time, 10 μs control-system reaction time.
- 20× collapse vs 2019 [arXiv:1905.09749] estimate — driven by cultivation + yoked codes + residue arithmetic, NOT decoder-margin improvement.
- Implication: structural innovations dominate; decoder-margin effects at the 5–10% LER level are sub-structural-innovation in magnitude.

## Stim / PyMatching toolchain benchmarks

- Stim ~1 kHz shot rate at d=100 on single CPU core.
- PyMatching v2 ~10⁶ errors/core-sec [Higgott Gidney 2023].
- Sinter: Monte Carlo driver providing ~10⁵ shots/sec/core aggregated.
- GPU BP+OSD (CUDA-Q QEC 2024): 29–42× CPU speedup.

## Expected filter-update wall-clock (on A100/H100)

- Stim-based likelihood evaluation at d=7, 10⁵ particles: target ~10 ms/update via vmap.
- JAX JIT compilation amortisation: first call ~seconds, steady state ~ms.
- Total update budget: 10 ms / 1 hr = 3.6 × 10⁵ updates/hour = comfortably above the drift-time-resolution requirement.

## Scoop-scan numerical summary (as of 2026-04-20)

- Closest adjacent 2026 preprints (ReloQate, Ch-DQN, dMLE, DEM-on-Willow, QuBA, QuFid) all score orthogonal-or-subset on the three-way SMC + sliding-window + static-Bayesian comparison at matched compute on real raw syndromes + LCD head-to-head.
- No 2026 paper carves out the (drift-timescale × drift-amplitude × refit-cadence) phase diagram.
- Closest methodological adjacent: arXiv:2512.10814 "Estimating DEMs on Willow" — uses the same Zenodo dataset we target; uses window-based DEM estimation (sliding-window family). Good candidate for direct baseline reproduction.

## Willow Zenodo 13273331 structure (from smoke-test)

- 420 experiments: d = 3, 5, 7 surface-code memory + d = 29 repetition code.
- 50 000 shots per experiment.
- Up to 250 QEC rounds per shot.
- 112.5 GB total, CC-BY 4.0.
- README per archive describes detector-event structure, Stim-circuit anchor, qubit mapping.

## Detection-floor statistical power

- Willow dataset: 420 × 50 000 × ~100 rounds ≈ 2.1 × 10⁹ detector-round samples.
- Wald-test detection floor on relative rate change: ~10⁻⁴ at 95% CI VERIFY (from √(1/N) back-of-envelope).
- Phase-diagram cells below this drift amplitude: all methods statistically indistinguishable; plan to exclude from the filter-wins region.

## Phase-diagram grid (proposal_v3 §3)

- 24 cells: 6 timescales × 4 amplitudes.
- Timescales: {10 ms, 1 s, 1 min, 10 min, 1 h, 6 h}.
- Amplitudes: {5%, 10%, 20%, 50%} of per-edge rate.
- Statistical test: per-cell paired t-test, Bonferroni across 24 cells at α = 0.05.
- Success criterion: contiguous region ≥10% of plane (~2.4 cells) where filter beats both baselines by ≥1% LER at 95% CI lower bound.

## Per-edge Pauli rate priors (d=7)

- 101 data qubits, 72 ancilla qubits, ~200–300 edges in the Stim DEM.
- Typical per-edge rate p ~ 10⁻³, range 10⁻⁴–10⁻². Prior Beta(α=2, β=2000) approximately matches.
- Drift-kernel: OU parameterisation (τ, σ) with τ ∈ [ms, hr], σ ∈ [10⁻⁴, 10⁻²] per-edge. Piecewise-linear secondary with jump rate λ and jump-magnitude σ_jump — captures TLS-switch mode.

## Open operational-territory numbers (PER-3)

- 1 refit/hour × 10⁴-device fleet × 10-minute drift-sensitive window = 10⁴ × 6 sensitive windows × 10 min = 10⁶ device-minutes/day of filter-relevant operating time.
- Willow-class production deployments projected for 2027–2028 (Google roadmap).
- Compared to the filter-irrelevant region (drift much faster than refit, or drift much slower than operational campaign), the filter-wins band of 10s–10min drift × 5–20% amplitude covers roughly 20–30% of realistic production-drift spectra VERIFY.
