# Thermodynamics Portfolio — State Snapshot

**Snapshot date:** 2026-04-20
**Session:** autonomous HDR sweep of thermodynamic follow-ons from the Phase 0.25 portfolio analysis of April 2026.
**Purpose:** resume state for a future session.

---

## Quick status table

| # | Project directory | Phase | Verdict | Next action |
|---|---|---|---|---|
| 4 | `thermodynamic_cross_substrate/` | −0.5 (×3) | KILLED | None — do not resume as publication-target |
| 1 | `berut_finite_time_refit/` | 2.75 (×2) | ARCHIVED | Needs human physicist input before resumption |
| 3 | `yaida_gns_tur_jarzynski/` | −0.5 r3 PROCEED | Phase 0 ready | Start 200+ citation lit review |
| 5 | `diffusion_crooks_benchmark/` | −0.5 r2 PROCEED | Phase 0 ready | Start 200+ citation lit review |
| 6 | `lan_chemotaxis_kur/` | −0.5 r2 PROCEED | Phase 0 ready | Start 200+ citation lit review + smoke-test Lan 2012 data |
| 8 | `non_markovian_tur_search/` | −0.5 r3 PROCEED | Phase 0 ready | Start 200+ citation lit review + tier A/B/C data smoke-test |
| 2 | `h100_housekeeping_phi_hw_blocked/` | pre-phase | HW-BLOCKED | Resume when H100 + DCGM access available |
| 7 | `revnet_landauer_imagenet_hw_blocked/` | pre-phase | HW-BLOCKED | Resume when multi-GPU cluster access available |

All commits pushed to `origin/master` on `hdr_autoresearch`.

---

## Per-project detail

### Project #4 — thermodynamic_cross_substrate — KILLED

**What it was.** Cross-substrate directional saturation ratio S = τ_observed/τ_min compared across biology (ribosome, CRISPR, E. coli evolution) and ML (GPT-4-class training).

**Why killed.** Three rounds of Phase −0.5 scope checks returned REFRAME. v1 collided with Kempes 2017 + Wolpert 2019. v2 collided with Yaida 2018 + Goldt-Seifert 2017. v3 (narrowed to a Bérut-refit + CMOS extrapolation) was judged apples-to-oranges on the CMOS leg. Per program.md the third non-PROCEED is auto-kill.

**Consequence for paper merge.** The idea of combining the two predecessor papers (`thermodynamic_info_limits`, `thermodynamic_ml_limits`) around a new cross-substrate result is abandoned. Each predecessor paper remains separately submittable under its REFRAME framings already on disk.

**Files preserved:** `proposal.md`, `proposal_v2.md`, `proposal_v3.md`, three `scope_check*.md` files, `PROJECT_KILLED.md`.

**Do not resume** as publication-target. May be revived as website-target if desired.

### Project #1 — berut_finite_time_refit — ARCHIVED (paused indefinitely)

**What it was.** Empirical refit of the Bérut 2012 ten-point finite-time colloidal bit-erasure dataset to the Proesmans B = π² lower bound, with a Brownian-dynamics simulator of the actual Bérut protocol as a first-principles cross-check.

**Why archived.** Two rounds of Phase 2.75 produced DO-NOT-PROCEED verdicts. All mandated RV01–RV09 experiments were executed honestly and each round of fixes introduced new critical issues:
- Round 1 caught unit inconsistency + incomplete-erasure decomposition.
- Round 2 caught silent protocol-class swap (3-stage Bérut → 4-stage canonical) and a factor-22.6 error in the T0 dimensional conversion.

After the round-2 corrections, the simulator gave B_phys = 0.79 k_BT·s while Bérut measured 8.27 k_BT·s — a factor-10 discrepancy that sits BELOW the Proesmans symmetric-optimal lower bound in physical units. The RV07 Schmiedl-Seifert harmonic-shift cross-check confirmed the simulator itself is sound (ratio 1.46 to analytical, acceptable for non-optimal linear drive). The factor-10 gap therefore lives in either (a) the Bérut L reconstruction from published barrier + stiffness (10–20 % uncertainty), or (b) calibration-loss physics in the Bérut apparatus that the simulator does not model.

**How to resume.** Not autonomously. Either:
- Contact Ciliberto group (Skinner-Dunkel has similar open-access flagellar datasets as a separate substrate if Bérut raw data can't be acquired).
- Pivot to a methodology note at PRE documenting the 10× simulator-vs-measurement discrepancy as a rigorous null result with specific calibration hypotheses.

Both paths require a physicist in the loop.

**Files preserved** (full audit trail): `proposal.md`, `proposal_v2.md`, `scope_check.md`, `literature_review.md` (701 citations), `papers.csv`, `knowledge_base.md`, `research_queue.md`, `publishability_review.md`, `publishability_review_v2.md`, `data_sources.md`, `data/raw/berut_2012_qdiss_vs_tau.csv`, `protocol_family_analysis.md`, `sanity_checks.md`, `design_variables.md`, `feature_candidates.md`, `results.tsv`, `tournament_results.csv`, `e00_baseline_fit.py`, `phase1_tournament.py`, `phase2_simulator.py`, `phase2b_simulator_fixed.py`, `phase275_rv_experiments.py`, `phase275b_rv_units.py`, `phase2_summary.md`, `phase2b_summary.md`, `paper_review.md`, `paper_review_v2.md`, `review_response.md`, `review_response_v2.md`, `PROJECT_ARCHIVED.md`.

### Project #3 — yaida_gns_tur_jarzynski — Phase 0 ready

**What it is.** A pre-registered Crooks-ratio test of the Langevin approximation to SGD, with effective-sample-size gating and an independent Gaussianity boundary.

**Key pivot (v3).** Crooks ratio instead of Jarzynski ⟨exp(−βW)⟩ — the Crooks slope is linear in W and ΔF-free by construction, eliminating the circularity the v2 reviewer caught. n_eff ≥ 1000 gating prevents the heavy-tail leak where Jarzynski tests pass on noise alone.

**Venue.** JSTAT primary, PRE fallback.

**Phase 0 follow-ups flagged by the scope-check reviewer:**
- Check whether Peng, Sun & Duraisamy 2024 (*Entropy*) is a near-duplicate; differentiate explicitly.
- Use bootstrap lower CI on n_eff, not point estimate.
- Strengthen the scope defence against "toy-scale" critique (possibly by adding a larger controlled testbed).

**To start Phase 0:**
- Run two parallel Phase 0 lit-review sub-agents (as was done for project #1) targeting 200+ citations across 4 themes: (1) Jarzynski + SGD, (2) Langevin-SGD validity / Gaussianity, (3) GNS + TUR + Mandt lineage, (4) Peng-Sun-Duraisamy lineage.

**Files present:** `proposal.md`, `proposal_v2.md`, `proposal_v3.md`, `scope_check.md`, `scope_check_v2.md`, `scope_check_v3.md`.

### Project #5 — diffusion_crooks_benchmark — Phase 0 ready

**What it is.** Measure the Crooks-ratio slope β̂(k) as training progresses on a 1-D analytical DDPM testbed, characterising the convergence rate κ of β̂(k) → β_true.

**Key pivot (v2).** From static-validation (tautological — a trained DDPM satisfies ELBO identity by construction) to training-dynamics measurement (non-tautological by design — β̂(0) at random init ≠ β).

**Venue.** TMLR primary, Entropy fallback.

**Phase 0 follow-ups flagged by the scope-check reviewer:**
- Pre-register a decorrelation threshold (new O6) demonstrating β̂(k) carries information beyond the ELBO loss curve.
- Add a real-data extension (MNIST-2 or similar) beyond the 1-D/2-D analytical testbeds.
- Expand lit search terms to "detailed-balance residual", "reverse-process consistency", "trajectory-asymmetry loss" — ~25% risk of undiscovered overlap in 2023-2025 generative-modelling literature.
- Demote O1 (β̂(0) ≠ β) from kill-outcome to calibration check.

**Files present:** `proposal.md`, `proposal_v2.md`, `scope_check.md`, `scope_check_v2.md`.

### Project #6 — lan_chemotaxis_kur — Phase 0 ready

**What it is.** A bound-tightness comparison (TUR vs KUR vs Landauer-Bennett) on the Lan, Sartori, Neumann, Sourjik & Tu 2012 *E. coli* chemotaxis dataset, gated on a Phase 0.5 analytical KUR-tightness check.

**Key pivot (v2).** From "KUR saturation test" (vulnerable to the TUR ≡ KUR pre-objection that would eliminate physics content) to a three-way bound comparison gated on an analytical tightness check.

**Venue.** Biophysical Journal primary, PRE fallback (per v1 reviewer).

**Phase 0 follow-ups flagged by the scope-check reviewer:**
- Read Lan & Tu 2016 review in full to pre-commit to the specific remaining gap.
- Run a pixel-level smoke test on Lan 2012 Fig. 3 to verify error bars are extractable at point-level precision — this is a Phase 0.5 prerequisite per CLAUDE.md "verify data access before Phase 0".
- Strengthen the KUR-fail fallback (currently a thin "TUR + housekeeping with φ uncertainty propagation" that sits too close to Sartori 2014 on its own).

**Files present:** `proposal.md`, `proposal_v2.md`, `scope_check.md`, `scope_check_v2.md`.

### Project #8 — non_markovian_tur_search — Phase 0 ready

**What it is.** KUR-vs-TUR tightness comparison on Skinner-Dunkel 2021 single-molecule traces + Pekola single-electron-box + Bustamante DNA-unzipping (three-tier data cascade for robustness).

**Key pivots (v2 → v3).** v2 pivoted from broad TUR-violation hunt (redundant with Skinner-Dunkel) to targeted KUR-vs-TUR comparison. v3 added the three-tier data cascade (v2 had a polite-way-to-die single-source dependency) and reworked O2 from "theorem violation" framing (tautological) to "ratio measurement with diagnostic protocol".

**Venue.** PRE primary, JSTAT fallback.

**Phase 0 follow-ups flagged by the scope-check reviewer:**
- Drop Tier C (Bustamante DNA-unzipping) — non-stationary pulling data without clean counted currents; cosmetic substitute.
- Operationalise the three diagnostic protocol checks (stationarity, Markov-order, observable-validity) with concrete thresholds.
- Pekola dataset run-length power analysis before committing to tier B alone.

**Files present:** `proposal.md`, `proposal_v2.md`, `proposal_v3.md`, `scope_check.md`, `scope_check_v2.md`, `scope_check_v3.md`.

### Projects #2 + #7 — HW-BLOCKED

**h100_housekeeping_phi_hw_blocked/** and **revnet_landauer_imagenet_hw_blocked/**. Both have `PROJECT_PAUSED.md` files with resumption checklists. Paused until the stated hardware is available.

---

## What the Phase −0.5 gate proved across the portfolio

Every single publishable project in the April 2026 follow-on portfolio **needed at least one round of reframe** before passing scope check. Every project had close comparators the initial brainstorm hadn't surfaced. Every project had at least one kill-outcome that was tautological, arbitrarily-thresholded, or gate-rather-than-falsifiability.

The gate forced all four projects through 2–3 REFRAME rounds that produced genuinely narrower, more defensible, less-tautological scopes with named differentiation against specific prior work and pre-registered tolerances tied to statistics rather than taste.

This is exactly what the gate was designed for. Had these projects been pursued directly from their v1 proposals, each would have consumed a full literature review + several weeks of experiments before producing a paper that Phase 2.75 or Phase 3.5 would have rejected on the same grounds the scope check caught in minutes.

## Predecessor paper status (for context)

`thermodynamic_info_limits/` — paper.md exists; REFRAME edits (ESSENTIAL + STRONGLY RECOMMENDED) applied April 2026. Target: J. Stat. Mech. or NJP. Not merged.

`thermodynamic_ml_limits/` — paper.md exists; REFRAME edits applied April 2026. Target: Entropy or TMLR. Not merged.

Neither paper depends on the follow-on portfolio. Each is independently submittable today.

---

## Resumption playbook for a future session

To pick up where the autonomous sweep stopped:

1. Pick a single Phase 0-ready project (#3, #5, #6, or #8) OR resume a hardware-blocked one if access is now available.
2. Read its v2/v3 proposal and the scope-check follow-ups listed above.
3. Run Phase 0 (200+ citations, 4 themes, 100+ hypotheses) — expect ~one hour of parallel sub-agent work per project.
4. Run Phase 0.25 publishability review incorporating the flagged follow-ups.
5. Proceed through 0.5 → 1 → 2 → 2.5 → 2.75 → 3 → 3.5 → B → publish per program.md.

The predecessor-paper REFRAMEs can also be re-submitted to their chosen venues today without needing any follow-on work.
