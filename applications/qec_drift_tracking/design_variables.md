# Design Variables — Committed Axes for Phase 2

Pinned decisions for the Phase 2 experiment plan. Each row is a committed design variable; proposal_v3 commitments are repeated for traceability. Ablation variants live in `feature_candidates.md`.

| # | Variable | Committed value | Source | Rationale |
|---|---|---|---|---|
| 1 | Filter state dimension | per-edge Pauli + 2 drift-kernel hyperparameters, Rao-Blackwellised | proposal_v3 §3, §6 | Dim-curse risk addressed by RBPF. |
| 2 | Drift-kernel parameterisation | Primary: Ornstein-Uhlenbeck (τ, σ). Secondary: piecewise-linear switching. | Theme 2 / §1.3 lit review | Matches 2511.09491 assumption set for clean head-to-head; piecewise-linear added for TLS burst regimes. |
| 3 | Proposal distribution | Block-diagonal Gaussian per-edge + optimal proposal for kernel hyperparameters | proposal_v3 §3 | Fights dim-curse per Bengtsson-Bickel-Li 2008. |
| 4 | Rao-Blackwellisation | Full RBPF on per-edge rates given kernel trajectory | proposal_v3 §3 | Reduces stochastic dim from ~200 → ~2. |
| 5 | Particle count N | 10⁴ (d=5), 10⁵ (d=7). Ablation {10³, 10⁶}. | proposal_v3 §6 | Tractable on 24 GB GPU; degeneracy margin above expected var(log-lik). |
| 6 | Resampling schedule | Systematic, ESS < N/2 trigger | Liu-Chen 1998 | Canonical; deterministic option in ablation. |
| 7 | Headline refit cadence (periodic-DEM baseline) | 1 refit/hour | proposal_v3 §4.2.a | Anchored to Willow 2024 vendor practice. |
| 8 | Control refit cadence | 1 refit/min (upper-bound only) | proposal_v3 §4.2.a | Compute-infeasibility control. |
| 9 | Static Bayesian baseline | arXiv:2406.08981 TN+MCMC reimplementation | proposal_v3 §3 | Primary Bayesian baseline. |
| 10 | Sliding-window MLE baseline | arXiv:2511.09491 reimplementation at published optimal window | proposal_v3 §3 | Primary non-Bayesian drift baseline. |
| 11 | LCD-class adaptive decoder baseline | Published-LCD protocol reimplementation with version-controlled protocol | proposal_v3 §2.3 | Addresses reviewer revision #4; PER-1 conformance benchmark required. |
| 12 | Decoder backbone | Reweighted PyMatching v2 (filter edge-weight updates) | proposal_v3 §3 | Streaming-capable, standard toolchain. |
| 13 | Drift-kernel timescale axis | Sweep {10 ms, 1 s, 1 min, 10 min, 1 h, 6 h} | proposal_v3 §3, §6 | 6 cells × 4 amplitudes = 24-cell phase diagram. |
| 14 | Drift-kernel amplitude axis | Sweep {5%, 10%, 20%, 50%} of per-edge rate | proposal_v3 §3, §6 | Phase-diagram axis. |
| 15 | Statistical test | Per-cell paired t-test, Bonferroni over 24 cells, α = 0.05 | proposal_v3 §4.3, §6 | Pre-registered hypothesis test. |
| 16 | Strict-dominance margin | ≥1% relative mean LER at 95% CI lower bound | proposal_v3 §2.2 | Pre-registered effect-size. |
| 17 | Contiguous region success threshold | ≥10% of (timescale × amplitude) plane, rook-adjacency | proposal_v3 §2.2 | Phase-diagram success criterion. |
| 18 | §4.1.a synthetic-fallback dominance threshold | ≥3% relative mean-LER gain vs 2511.09491 averaged across 24 cells | proposal_v3 §4.1.a | Data-fallback gate. (NOT TRIGGERED: primary data path passes smoke test.) |
| 19 | Primary data source | Google Willow Zenodo 13273331 | data_sources.md | Smoke test 2026-04-20 passed. |
| 20 | Secondary (cross-vendor) data source | Rigetti Ankaa-2 Zenodo 13961130 | data_sources.md | Platform-general drift slice. |
| 21 | PER-2 FTQC sensitivity anchor | Gidney-Ekerå 2025 RSA-2048, Azure RE secondary | research_queue PER-2 | 5%-threshold envelope. |
| 22 | PER-2 LER sweep | {0.5, 0.9, 0.95, 1.0, 1.05, 1.1, 2×} of default | knowledge_base §PER-2 | Resource-estimation sensitivity grid. |
| 23 | PER-1 LCD conformance ratio threshold | report; flag caveat if >1.2×; abandon LCD baseline if >2× | research_queue PER-1 | Pre-registered conformance QC. |
| 24 | Evaluation LER protocol | Offline on pre-recorded syndrome streams; filter posterior → reweighted decoder | proposal_v3 §3 | Wall-clock comparisons use matched-compute budget. |
| 25 | Primary headline threshold | ≥5% relative mean LER reduction vs 1/hr DEM refit | proposal_v3 §2.1 | Operational headline. |
| 26 | Operational kill threshold | within 5% of 1/hr DEM refit at realistic filter-latency → downgrade | proposal_v3 §4.2 | Mirrors headline. |
| 27 | Venue primary | PRX Quantum | proposal_v3 §7 | Applied-Bayesian-on-hardware fit. |
| 28 | Venue secondary | Phys. Rev. Research | proposal_v3 §7 | Lower novelty-bar fallback. |
| 29 | Venue tertiary | Quantum (Verein) | proposal_v3 §7 | Gidney/Higgott reviewer pre-empt. |

Total: 29 committed design variables (≥15 requirement met).

## Phase-2 ablation matrix (planned)

- Particle count: {10³, 10⁴, 10⁵, 10⁶}.
- Proposal: {bootstrap, Laplace, APF, block-diagonal}.
- Drift-kernel: {OU, piecewise-linear, hybrid}.
- Refit cadence (for baseline sensitivity): {never, 1/hr, 1/min}.
- Data slice: {Willow d=5, Willow d=7, Rigetti, Willow rep-code d=29}.

## Open design decisions requiring Phase 0.5 resolution

- Whether to include the neutral-atom slice (no public per-shot per-round stream currently).
- Whether to include Quantinuum H2 slice at all (different drift regime may confound).
- Whether Willow within-run drift is detectable — if not, all primary-path cells are "real statistics + injected synthetic drift" hybrid.
