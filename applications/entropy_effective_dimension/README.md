**Target type**: publication-target

# entropy_effective_dimension — Subspace Criticality in Trained Transformers

## Target paper

Direct empirical test of Fontenele et al. 2024 (Sci. Adv.) in new substrate: criticality on trained transformer activations is confined to a low-dimensional subspace, with subspace-σ = 1 at training steps where ambient-σ is far from 1. The "ambient-basis negative for criticality is not informative" claim the Paper 1 Anchor scope-check flagged is here elevated to a standalone publishable test.

## Candidate (from ideation workspace)

From `applications/entropy_ideation/candidate_ideas.md §Candidate 29` and scope-check `candidate_29_review.md`:
- **C29** — effective dimension D_eff vs σ (Paper 1 Anchor candidate for the strongest novelty-per-cost of the 35-candidate portfolio per the scope-check).

## Critical methodology corrections (from scope-check)

1. **Fontenele's method is not "K = D_eff" PCA projection.** It uses PCA with an *operational* K = largest k such that removing PC1..PCk collapses the power-law range below 1.5 decades (typically K < 3 / 200 dims). Avalanche statistics computed on a reconstructed scalar population-summed activity from the top-K subspace, not per-PC. ML-power-law fits (not MR estimator). Time-bin-dependent (Δ_T ≥ 10·⟨ISI⟩).
2. **Related but non-overlapping prior:** Liu-Paquette-Sous NeurIPS OPT 2025 workshop 43 (covariance spectrum α across Pythia through training); Razzhigaev et al. 2311.05928 EACL 2024 "Shape of Learning" (intrinsic dimension trajectory); Xu 2602.10496 (low-dim execution manifolds in modular-arithmetic transformers); Wang 2604.16431 (dimensional criticality at grokking — but on gradients, different axis).
3. **Net surviving novel claim:** subspace σ differs from ambient σ; subspace σ = 1 crossing exists that ambient σ hides. Falsifiable against random-subspace null.

## Scope and constraints

- **Single RTX 3060 12 GB.** Pythia 70M – 2.8B fp16 across 20-checkpoint × 5-scale grid (~100 cells, ~170 GPU-hours within 3-week budget).
- **Streaming covariance accumulation** — not full-activation-cache (that would need 1.6 TB). Covariance matrix is trivial (d_model² = 26 MB for Pythia-1.4B).
- **Random-subspace null** mandatory (rule out "any K-dim projection pulls σ toward 1").
- **MR estimator well-posed on linear projections** (r_k = m^k holds for any linear observable per Wilting-Priesemann) but must be argued explicitly.
- **Faithful Fontenele replication vs K-tuning.** Pre-register both (Fontenele's collapse-criterion K + direct participation-ratio K) and compare; either outcome is publishable.

## Prior-art engagement (mandatory citations)

- Fontenele et al. 2024 Sci. Adv. (papers.csv 4005) — the paper being replicated.
- Liu-Paquette-Sous NeurIPS OPT 2025 workshop paper 43 — covariance spectrum on Pythia.
- Razzhigaev et al. 2024 EACL (arXiv:2311.05928) — intrinsic dimension trajectory.
- Xu 2026 (arXiv:2602.10496) — low-dim execution manifolds.
- Wang 2604.16431 — dimensional criticality on gradients at grokking (different axis, must differentiate).
- Wilting & Priesemann 2018 (papers.csv 1019) — MR estimator linearity.
- Spitzner 2021 — mrestimator toolbox.

## Phase sequence

- **Phase 0 — deep lit review** (in progress; target 200+ citations across Fontenele-lineage low-dim-criticality, intrinsic-dimension papers, participation-ratio literature, SSM / LLM covariance spectrum work, Pythia-specific studies).
- **Phase 0.25 — publishability review.**
- **Phase 0.5 — verify Pythia checkpoint access (HuggingFace mirror of 154 per scale); verify mrestimator works on linear projections via synthetic ground truth.**
- **Phase 1 Day 1 — dynamic-range pilot.** *Before* committing to Fontenele's operational K-selection rule, measure P(s) dynamic range on Σ_K for GPT-2-small + Pythia-160M at one checkpoint. If avalanche span is < 2.5 decades, Fontenele's 1.5-decade-collapse rule is degenerate on this substrate and the paper's K-selection methodology must be re-derived. Kill gate before burning the 100-cell sweep.
- **Phase 1 — pipeline build**: streaming covariance accumulator (PyTorch hooks), two K-selection rules (Fontenele operational + direct participation-ratio), MR-σ on reconstructed scalars, random-subspace null, participation-ratio computation, **synthetic continuous-activation K-validator** (render known-σ branching process as continuous activation matrix; pipeline must recover σ + K within CI), **Halloran-Roysdon Jacobian-Lyapunov companion observable** (~3 GPU-days, narrative insurance against a flat-σ null in Phase 2).
- **Phase 2 — experiments** across 100-cell grid.
- **Phase 2.75 / 3 / 3.5 / 4** per program.md.

## Venue target

**Post-Phase-0.25 reframe.** Liu-Paquette-Sous 2025 is a NeurIPS OPT workshop paper, not main-track — this is the informative prior that a one-predicate extension of Fontenele does not clear NeurIPS/ICLR main. Honest ranking conditional on clean dynamic-range-pilot + synthetic-validator + positive subspace-σ-vs-ambient-σ result:

- **Primary: *Neural Computation*** (~60%).
- **Parallel submission: TMLR (~65%) + NeurIPS UniReps workshop** (well-matched audience).
- **NeurIPS/ICLR main: ~15-25% conditional on the Halloran-Lyapunov companion observable confirming the σ result** (two orthogonal observables agreeing substantially strengthens the main-track case; σ alone is too thin).

## Phase 0.25 reframes applied (2026-04-21)

Full review at `publishability_review.md`. Seven load-bearing reframes:
1. **Shape-collapse (evidence-bar item 4)** explicitly named in the pipeline — was missing.
2. **At-init baseline = fresh-weight-matched Pythia init** (not just "step 0" which already has training data leakage on some initialisations).
3. **Crackling-γ on the reconstructed scalar Σ_K** must be paper-level (not appendix) — it's load-bearing for the universality-class claim on the LLM subspace.
4. **Griffiths-phase neutral-null rejection explicitly out-of-scope** in this paper (matches entropy_brain_homology precedent); reference Paper 1 (entropy_avalanches §7) for that arm.
5. **Dynamic-range pilot as Phase 1 Day 1 kill gate** — Fontenele's 1.5-decade-collapse K-selection rule is degenerate if LLM P(s) span < 2.5 decades.
6. **Halloran-Roysdon Lyapunov companion observable** added as ~3 GPU-day narrative insurance; single-candidate paper with no fallback observable is structurally fragile.
7. **Venue realignment.** Drop NeurIPS/ICLR main primary; primary = *Neural Computation*; parallel = TMLR + NeurIPS UniReps workshop.

## Parent ideation

See `../entropy_ideation/` for the full 35-candidate portfolio.
