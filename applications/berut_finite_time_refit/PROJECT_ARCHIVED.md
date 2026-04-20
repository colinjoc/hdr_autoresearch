# berut_finite_time_refit — ARCHIVED (paused indefinitely)

**Status at archive:** Phase 2.75 BLOCKED (round 2).
**Archive date:** 2026-04-20.
**Archived by:** autonomous HDR loop, at user instruction.

## Why archived

Two consecutive Phase 2.75 rounds produced DO-NOT-PROCEED verdicts:
  - Round 1 (paper_review.md): caught unit inconsistency + incomplete-erasure decomposition.
  - Round 2 (paper_review_v2.md): caught silent protocol-class swap (3-stage → 4-stage) and a factor-22.6 error in the T0 dimensional conversion.

After the round-2 mandated RV07-RV09 experiments:
  - RV07 verified the simulator machinery against the Schmiedl-Seifert analytical result (ratio 1.46, acceptable for non-optimal linear drive).
  - RV09 at corrected τ_sim values matching the Bérut regime gave B_phys = 0.79 k_BT·s, **10× below Bérut's empirical 8.27 k_BT·s**.
  - The simulator now sits below the Proesmans symmetric-optimal lower bound in physical units — impossible if both simulator and parameter reconstruction are correct.

The simulator is self-consistent (RV07 passes). The Bérut parameter reconstruction is approximate (L inferred from published κ + barrier, with ±10–20 % uncertainty). Calibration-loss physics in the Bérut apparatus (AOD nonlinearity, photodiode, laser heating) is not modelled. Disambiguating these is a physics-research task requiring a human stochastic-thermodynamics specialist.

## What is preserved

The project directory contains:
  - Complete Phase 0 lit review (701 citations, 115 hypotheses, 4 themes)
  - Phase 0.25 v2 PROCEED verdict
  - Phase 0.5 CLEAR verdict with E00 that reproduces Bérut's published fit to 1 part in 200
  - Phase 1 tournament winner (F1 Proesmans 1/τ form, AICc-selected)
  - Phase 2 (original, superseded) and Phase 2b (corrected, superseded) simulator scripts
  - Phase 2.75 round 1 + round 2 reviewer verdicts with mandated RV experiments executed
  - review_response.md and review_response_v2.md documenting all findings

A future session can resume this project by:
  1. Contacting the Ciliberto group for the raw AOD control waveform + systematic error budget OR for a digitally-reproducible reconstructed U(x, t).
  2. OR pivoting the paper to a methodology note at PRE reporting the 10× simulation-vs-measurement discrepancy as a rigorous null.

Either path requires external input that the autonomous loop cannot supply.

## DO NOT resume this project autonomously

The two Phase 2.75 rounds both caught critical errors that cosmetic autonomous fixes introduced. A third round without external input is unlikely to produce a publishable result; the honest call is to stop until a physicist is in the loop.
