# Proposal v3 — Drift-Aware Online Noise-Model Inference for QEC

Responds to Phase 0.25 publishability review in `publishability_review.md` (verdict: REFRAME). Every revision below is keyed to a specific reviewer ask. This is the **first reframe cycle** of the Phase 0.25 gate; per program.md, one further REFRAME permitted before automatic KILL.

## 1. Problem

Real quantum devices drift. Fixed noise models become stale, degrading decoder performance below what on-line calibration could achieve. Three 2024–2025 preprints formalise the drift-inference problem — arXiv:2511.09491 (sliding-window MLE), arXiv:2406.08981 (static Bayesian TN+MCMC), arXiv:2504.14643 (static per-edge DEM estimation) — but none identifies the regime where any one method is strictly preferable, none runs on a public real device syndrome stream, and none benchmarks against an LCD-class adaptive decoder already in production (Riverlane 2025 Nat. Commun.).

## 2. Claim (falsifiable)

### 2.0 Contribution statement

The paper is a **regime characterisation**, not a method paper. The particle filter is one of three inference methods benchmarked. The contribution is:

**"Under which (drift-kernel timescale × amplitude × refit-cadence) conditions does online SMC drift-inference strictly beat both sliding-window MLE (arXiv:2511.09491) and static Bayesian inference (arXiv:2406.08981), at matched compute budget, and in what subset of those conditions does it also beat a Riverlane-LCD-class adaptive decoder baseline?"**

### 2.1 Primary headline (operational)

Particle filter reduces mean logical error rate vs a 1-refit/hr periodic-DEM baseline by **≥5% relative**, under a pre-registered drift regime, at matched decoder wall-clock latency.

**5% threshold justification (per pre-empt-reviewer item):** Fowler 2013 correlated matching gains ≈15% on matched surface-code at the threshold; Riverlane LCD reports ≈2× gains in leakage-dominant regimes (arXiv / Nat. Commun. 2025); both exceed 5%. A 5% gate is **the minimum margin below which FTQC resource-estimation sensitivities (Gidney–Ekerå 2025, arXiv:2505.15917 reaction-time axis) absorb the improvement into error bars**. Dropping below 5% gain would not change any published resource estimate in a numerically meaningful way.

### 2.2 Phase-diagram success criterion (pre-registered — addresses reviewer revision #2)

The (drift-kernel-timescale × amplitude) phase diagram must exhibit **a contiguous region covering ≥10% of the scanned (timescale × amplitude) plane where the particle filter strictly dominates both baselines (sliding-window MLE and static Bayesian) at p < 0.05 under Bonferroni correction across cells**, with "strict dominance" defined as mean LER lower by ≥1% relative at the 95% CI lower bound.

If the contiguous-10% criterion is not met, the paper cannot claim "filter is the inference method of choice" and must downgrade to a characterisation note, or KILL.

### 2.3 Adaptive-decoder comparison (addresses reviewer revision #4)

Explicit commitment: on the synthetic-drift benchmark, the particle-filter-driven decoder is compared head-to-head against a **Riverlane-LCD-class adaptive-decoder baseline** implemented in the paper (closest open reimplementation of Barnes et al. Riverlane 2025 Nat. Commun.; if open source unavailable, a published-algorithm reimplementation with version-controlled protocol). If the LCD-class baseline matches or exceeds particle-filter performance across all phase-diagram cells, the Bayesian-inference angle has no operational home and the paper is downgraded.

## 3. Method sketch

- **Particle filter** over per-edge Pauli-rate state × drift-kernel parameterisation (OU or piecewise-linear), GPU-accelerated via JAX. Rao-Blackwellisation on stationary components + block-diagonal proposal for non-stationary drift parameters, to prevent degeneracy at O(100–200) filter state dimension (per reviewer's pre-empt-reviewer item on state-dim degeneracy).
- **Baselines**: sliding-window MLE (arXiv:2511.09491 reimplementation), static Bayesian MCMC (arXiv:2406.08981 reimplementation), periodic-DEM refit at 1/hr (headline) and 1/min (compute upper-bound control).
- **LCD-class adaptive baseline** (addresses reviewer revision #4): Riverlane Local Clustering Decoder reimplementation at published protocol version.
- **Reweighted PyMatching v2** (existing API) for online LER evaluation.
- **Stim** for synthetic drift ground truth.
- Phase diagram: sweep kernel timescale ∈ {10 ms, 1 s, 1 min, 10 min, 1 h, 6 h} × kernel amplitude ∈ {5%, 10%, 20%, 50% of per-edge rate}; 6 × 4 = 24-cell grid.

## 4. Kill-conditions (pre-registered)

### 4.1 Data-access gate

- **Primary path:** 15-minute smoke test for public raw per-shot per-round syndrome stream on {Google Quantum AI datasets, IBM Heron, Quantinuum H2, Zenodo, arxiv ancillaries, google-quantum-ai GitHub}. Run **before Phase 0.5**.
- **§4.1.a synthetic-fallback dominance test (addresses reviewer revision #1):** if the smoke test fails and we fall back to synthetic-only, proceed as publication-target **only if** expected mean-LER gain over arXiv:2511.09491 sliding-window MLE is **≥3% relative averaged across the 24 phase-diagram cells at the pre-registered metric** (2.1) measured on a pilot run before Phase 0.5 commit. If the synthetic-only dominance is below 3%, the paper is head-on with 2511.09491 on its home turf and cannot clear Phase 0.25 on the second cycle — downgrade to website-target or abandon.

### 4.2 Operational kill

- **§4.2.a pinned headline baseline cadence (addresses reviewer revision #3):** The headline comparator is **1 refit/hr**, per Willow 2024 reported operational cadence (Acharya et al., Nature 2024 supplement), with 1/min as a compute-upper-bound control only.
- If mean LER under particle-filter-driven reweighting is within 5% of 1/hr periodic-DEM at realistic filter-latency, the paper has no operational story — downgrade to note or abandon.

### 4.3 Regime kill

- Per §2.2, if the phase diagram fails the pre-registered contiguous-10% criterion, the filter-as-method contribution is dead. The paper then downgrades to a pure regime-characterisation note for Phys. Rev. Research, or is abandoned. Statistical test: per-cell paired t-test (filter vs each baseline) with Bonferroni across 24 cells at α = 0.05; "strictly beats" = ≥1% relative mean-LER improvement at the 95% CI lower bound.

## 5. Reframe responses to Phase 0.25 publishability review

| Reviewer revision | Response | Section |
|---|---|---|
| (1) §4.1.a pre-reg synthetic-fallback dominance test | ≥3% over arXiv:2511.09491 averaged across cells | §4.1.a |
| (2) §2.a pre-reg phase-diagram success criterion | Contiguous 10% plane, Bonferroni p<0.05, ≥1% strict | §2.2 |
| (3) §4.2.a pinned realistic refit cadence | 1/hr per Willow 2024 as headline; 1/min as control only | §4.2.a |
| (4) §2 LCD-class adaptive-decoder baseline | Riverlane-LCD reimplementation head-to-head | §2.3 / §3 |
| (5) §7 Quantum (journal) as tertiary venue | Named with reviewer profile | §7 |

Secondary items also addressed:
- 5%-threshold anchor to Fowler 2013 / Riverlane LCD / FTQC resource-estimation sensitivity — §2.1.
- Particle-filter state-dim degeneracy → Rao-Blackwellisation + block-diagonal proposal — §3.

## 6. Load-bearing parameters (pre-registered)

| Parameter | Committed value | Sensitivity plan |
|---|---|---|
| Primary data source | TBD after smoke test; synthetic-only fallback gated by §4.1.a | Gated; §4.1 |
| Drift-kernel timescale | Sweep {10 ms, 1 s, 1 min, 10 min, 1 h, 6 h} | Phase-diagram axis; §2.2 success criterion applies |
| Drift-kernel amplitude | Sweep {5%, 10%, 20%, 50%} of per-edge rate | Phase-diagram axis |
| Headline refit cadence | **1/hr** (pinned per §4.2.a) | 1/min as upper-bound control only |
| Particle count N | 10⁴ (d=5), 10⁵ (d=7) | Ablation at 10³, 10⁶ |
| Filter state dim | per-edge Pauli rates + 2 drift-kernel params (Rao-Blackwellised) | Fixed pre-registration |
| LCD-class baseline | Riverlane 2025 Nat. Commun. protocol reimplementation | Fixed; §2.3 |
| Statistical test | per-cell paired t-test, Bonferroni over 24 cells, α=0.05 | Fixed; §2.2 |

## 7. Target venues (addresses reviewer revision #5)

**Primary: PRX Quantum.** Fit — applied-Bayesian-on-hardware with operational story. Anticipated objection "quantify operational benefit over periodic recalibration *including filter compute latency*, and compare against Riverlane LCD-class adaptive decoders in production" is pre-empted by §2.3 (LCD baseline) and §4.2.a (filter latency matched to periodic-refit wall-clock).

**Secondary: Phys. Rev. Research.** Fit — empirical-methods, lower novelty bar; natural home if phase-diagram success criterion §2.2 lands marginally.

**Tertiary: Quantum (Verein).** Fit — open-access, QEC-heavy, tolerant of methods-plus-regime characterisation papers. Anticipated Gidney/Higgott-type reviewer objection: "will demand a DEM-reweight baseline Google themselves would run, and will notice if Willow raw syndromes are not actually public." Pre-empt: §4.2 commits to 1/hr-DEM-refit baseline (exactly the Google-style cadence); §4.1 publicly documents the smoke-test outcome so there is no sleight-of-hand on data availability.

## 8. Open-source commitment

All code, drift-kernel configs, pre-registration document, LCD reimplementation, and phase-diagram raw data to be released with arXiv companion, per Quantum-journal norms.

## 9. Timing

Aim: arXiv within 4–5 months if smoke test passes OR if synthetic-fallback dominance test (§4.1.a) clears. Scoop-risk mitigation — the phase-diagram + LCD-class-baseline + regime-characterisation framing is distinct from any single-method preprint currently active.
