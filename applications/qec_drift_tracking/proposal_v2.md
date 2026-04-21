# Proposal v2 — Drift-Aware Online Noise-Model Inference for QEC

Responds to scope check in `../qec_ideation/scope_checks/candidate_02_review.md` (verdict: REFRAME).

## 1. Problem

Real quantum devices drift. Fixed noise models become stale, degrading decoder performance below what on-line calibration could achieve. Two recent simulation-only preprints formalise the drift-inference problem ([arXiv:2511.09491, 2025] sliding-window MLE; [arXiv:2406.08981, 2024] static Bayesian) but neither identifies the regime where any one method is strictly preferable, and neither has been run on real device syndrome streams.

## 2. Claim (falsifiable)

**Headline (reframed):** We will demonstrate that a drift-aware particle-filter noise-model estimator **reduces the mean logical error rate relative to a periodic-DEM-refit baseline by ≥5%**, under a single pre-registered drift regime on either real public syndrome data (if available) or pre-registered synthetic drift with ground-truth parameters — and we will produce a phase diagram naming the (kernel timescale × amplitude) regions in which the filter strictly beats both sliding-window MLE ([arXiv:2511.09491]) and static Bayesian inference ([arXiv:2406.08981]).

**Demoted from headline (still measured, secondary):** LER-variance reduction. Variance is cosmetic; mean-LER-at-matched-latency is the reviewer-defensible operational metric.

## 3. Method sketch

- Particle filter over a per-edge Pauli-rate state × a drift-kernel parameterisation (OU or piecewise-linear), GPU-accelerated via JAX.
- Reweighted PyMatching v2 (existing API) for online LER evaluation.
- Stim for ground-truth synthetic drift.
- Phase diagram: sweep kernel timescale ∈ {10 ms, 1 s, 1 min, 1 h} × kernel amplitude, compare filter vs sliding-window MLE vs static MCMC at matched compute budgets.

## 4. Kill-conditions (pre-registered)

1. **Data-access kill:** if 15-min smoke test fails (no raw per-shot per-round syndrome stream from any public vendor — Google Willow, IBM Heron, Quantinuum H2), KILL the real-data headline and either (i) reshape to fully-synthetic with explicit scoping, or (ii) abandon if the fully-synthetic version is dominated by arXiv:2511.09491.
2. **Operational kill:** if mean LER under particle-filter-driven reweighting is within 5% of periodic-DEM-refit at realistic refit cadences, the paper has no operational story — downgrade to note or abandon.
3. **Regime kill:** if the phase diagram shows no (kernel, amplitude) cell where the filter strictly beats both sliding-window and static baselines, the filter is a method swap without a regime — downgrade to method note.

## 5. Reframe responses to scope-check objections

- **Objection A (fatal — Willow data access):** addressed by gating the entire project on a data-access smoke test per `feedback_verify_data_access_before_phase_0`. Fallback targets IBM Heron or Quantinuum H2 public streams; if none exist, KILL.
- **Objection B (particle filter is a method choice, not a contribution):** addressed by the phase-diagram experiment. The *contribution* is the regime characterisation, not the filter itself.
- **Objection C (30% variance reduction is cosmetic):** addressed by promoting mean-LER-vs-periodic-refit to the headline and demoting variance to secondary.

## 6. Load-bearing parameters (pre-registered)

| Parameter | Committed value | Sensitivity plan |
|---|---|---|
| Primary data source | TBD after smoke test | Gated — see §4 |
| Drift-kernel timescale | Full sweep {10 ms … 1 h} | Phase-diagram axis |
| Particle count N | 10⁴ (d=5), 10⁵ (d=7) | Ablation at 10³, 10⁶ |
| Filter state dim | per-edge Pauli rates + 2 drift-kernel params | Fixed pre-registration |
| Refit-baseline cadence | {never, 1/hr, 1/min} | All three as comparators |

## 7. Target venue

**Primary: PRX Quantum.** Fit — applied-Bayesian-on-hardware niche. Anticipated objection pre-empted by phase-diagram contribution (quantifies operational benefit over periodic recalibration).

**Secondary: Phys. Rev. Research.** Fit — empirical methods, lower novelty bar.

## 8. Open-source commitment

All code, drift-kernel configs, and pre-registration document to arXiv companion with reproducibility requirements per Quantum-journal norms.

## 9. Timing

Aim: arXiv within 4–5 months if smoke test passes. Scoop-risk mitigation — first public real-data particle-filter QEC characterisation is the differentiator.
