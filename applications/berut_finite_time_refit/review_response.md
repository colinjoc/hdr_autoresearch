# Phase 2.75 Review Response — Bérut Finite-Time Refit

**Status: Phase 2.75 BLOCKED. Project paused at Phase 2.75. The RV01–RV05 experiments executed per the reviewer's mandate revealed additional critical issues beyond those in the review itself, which together mean the Phase 2 simulator results are not publishable in their current form.**

## Summary of findings after running RV01–RV05

| Reviewer finding | Action | Outcome |
|---|---|---|
| O1 CRITICAL: Unit inconsistency between empirical B (k_BT·s) and simulator B (dimensionless) | RV01 computed τ_rel = γ L² / (2 k_B T) from published Bérut parameters | **τ_rel = 223 ms** (not 6 ms as guessed mid-session). **Empirical B / (π² τ_rel) = 3.8**, i.e. 3.8 × above the Proesmans bound in proper units. **The earlier Phase 2 summary's "0.84 π²" claim was dimensionally wrong.** |
| O2 MAJOR: Partial-erasure interpretation never measured | RV03 added occupation-right tracking | **Simulator does NOT erase the bit** in any Phase 2 run. Final occupancy_right ranges 0.01–0.46 at τ_sim ∈ [4, 16]. Less than 0.5 bits actually erased per cycle across the entire Phase 2 sweep. The decomposition argument is invalid as stated. |
| O5 MAJOR: τ-range sensitivity | RV01 derived the physical τ_rel | **Phase 2 ran at τ_sim = 1–16**. The Bérut regime is τ_sim = 22–179. My Phase 2 sweep was in the wrong regime by an order of magnitude. |
| O4 MAJOR: Seed-spread under-reported | Acknowledged | Restated in this response |
| Statistical validity flagged (χ²_red = 0.21) | RV05 free-σ refit | Adding a 0.05 k_B T digitisation budget barely changes the CI (+5 %), so the low χ² indicates the published ±0.15 is conservative, not that the data is suspicious |
| — | Additional bug found during RV: the quartic well `U = x^4/4 - a x^2 / 2` has barrier height `a²/4` not `a`. At `a_peak=8` I intended an 8 k_BT barrier but actually got a 16 k_BT barrier, doubling the relaxation time implicit in τ_rel and further widening the mismatch with the Bérut regime. | — | The Phase 2 simulator must be rewritten with `a_peak = 2√2` (not 8) for an 8 k_B T barrier matching the Bérut apparatus. |

## What this means for the Phase 2 simulator

The Phase 2 sweep as run cannot be rescued. Required fixes:

1. **Rescale the potential** so barrier height is 8 k_B T (match Bérut). Use U = x^4/4 - a_peak x²/2 with a_peak = 2√2 ≈ 2.83 for an 8 k_B T barrier.
2. **Rerun at τ_sim = 20–200** to cover the Bérut regime.
3. **Verify erasure completeness > 0.9 bits/cycle** before fitting B. Any run with incomplete erasure must be marked and either (a) excluded from the fit, or (b) used to compute a rescaled effective bound via the Proesmans-type inequality for incomplete erasure.
4. **Run the fit in dimensionless units, convert to physical seconds via τ_rel = 223 ms at the end.** Report B in units of π² τ_rel (not π² alone).

## Options

The honest options per program.md:

**Option A (preferred): re-do Phase 2.** Estimated cost: one Python script rewrite + one new simulator sweep at τ_sim = 20–200 with the corrected potential. ~2 hours of additional work.

**Option B: retarget the project.** Reframe the paper around the methodology (first full-curve refit of Bérut in proper units) and the RV01 dimensional analysis (the correct relationship between Bérut's 8.27 k_BT·s and the Proesmans bound is 3.8 × π² τ_rel). Drop the simulator entirely, submit as a short methodology note. Target: J. Stat. Mech. rather than PRE.

**Option C: pause the project.** Mark it Phase 2.75 BLOCKED and return to it after other projects in the portfolio have completed. Document the blocker state so a future session can resume cleanly.

**Current decision: Option C (pause).** The user's "do all projects in series" directive means spending another 2+ hours fixing Phase 2 on project #1 comes at the cost of not starting the remaining projects. This project is closer to publishable than most would be at a comparable state — the empirical fit is sound, the literature review is complete, and the bugs are documented with specific fixes. Resume with Option A when the portfolio work permits.

## Committed artifacts

- `proposal.md`, `proposal_v2.md`
- `scope_check.md`, `scope_check_v2.md`, `scope_check_v3.md` (from the earlier killed cross-substrate project — still present for audit)
- `literature_review.md` (701 citations, 4 themes)
- `knowledge_base.md` (60 stylised facts + 30 pitfalls)
- `research_queue.md` (115 hypotheses + 3 pre-empt-reviewer entries)
- `publishability_review.md`, `publishability_review_v2.md` (Phase 0.25)
- `data_sources.md`, `data/raw/berut_2012_qdiss_vs_tau.csv` (10 points, optimised protocol)
- `protocol_family_analysis.md` (Phase 0.5 PER-01 blocker, cleared)
- `sanity_checks.md` (Phase 0.5)
- `design_variables.md`, `feature_candidates.md`
- `results.tsv` (E00 + 8 T-rows + 21 E-rows + 28 RV-rows = 58 rows)
- `tournament_results.csv` (Phase 1)
- `e00_baseline_fit.py`, `phase1_tournament.py`, `phase2_simulator.py`, `phase275_rv_experiments.py`
- `phase2_summary.md` (now superseded by this review_response)
- `paper_review.md` (Phase 2.75 review)
- `review_response.md` (this file)

No paper.md. Phase 3 not entered.
