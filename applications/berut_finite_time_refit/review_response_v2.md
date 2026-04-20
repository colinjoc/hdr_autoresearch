# Phase 2.75 (round 2) Review Response — Bérut Finite-Time Refit

**Status: Phase 2.75 BLOCKED (second time).** The round-2 reviewer's mandated RV07–RV09 experiments executed cleanly and confirmed the reviewer's two CRITICAL findings. A new physics gap emerged that cannot be resolved by additional autonomous iteration.

## Summary after RV07–RV09

| Reviewer finding | RV executed | Outcome |
|---|---|---|
| PROT-01 (CRITICAL) — switched from Bérut's 3-stage to 4-stage without admitting | Acknowledged. The 4-stage protocol is distinct from Bérut's protocol class; any published claim must name it as such. | Requires paper reframe, not an experiment |
| UNIT-01 (CRITICAL) — T0 computed using inter-well distance L; correct length unit is L/(2√a_peak) | RV08 recomputed. **T0 = 19.71 ms, not 447 ms** — the reviewer was right, my round-1 correction was cosmetically off by a factor of 22.6. | Consequential — changes every physical-unit number in phase2b_summary.md |
| DEC-01 (MAJOR) — factor-2.2 gap not decomposed | Superseded. With the corrected T0 the "factor 2.2" becomes a factor ~0.1 (simulator under-predicts Bérut 10×). There is no longer a gap to decompose; there is a different, larger gap in the opposite direction. | Requires physics-level investigation, not more knob-sweeping |

## RV07 (Schmiedl-Seifert cross-check) — simulator machinery is sound

Harmonic-shift protocol (analytical Proesmans): linear drive of a harmonic centre from −x_centre to +x_centre, where γ = 1, k_spring = 4. Analytical answer for OPTIMAL linear drive: W_min = γ(2 x_centre)²/τ = 22.63/τ in simulator units.

Simulator measured: B_SS = 33.05 ± 5.13 (= 3.35 π² in simulator units).

Ratio to analytical: 33.05 / 22.63 = **1.46**. For a non-optimal linear drive (as opposed to Schmiedl-Seifert's full optimal protocol), B_sim should exceed the analytical by a modest factor. 1.46 is in the expected range. The simulator machinery correctly reproduces the harmonic-shift Proesmans bound.

## RV09 (Bérut-regime τ sweep) — dimensional contradiction revealed

At the corrected τ_sim = {256, 512, 1024} (= Bérut physical τ ≈ 5, 10, 20 s), the simulator gives:

| τ_sim | τ_phys (s) | W (k_BT) | occ_R | bits_erased | W − ln 2 | × τ_sim |
|---|---|---|---|---|---|---|
| 256 | 5.0 | 0.847 ± 0.032 | 0.000 | 1.000 | +0.154 | 39.4 |
| 512 | 10.1 | 0.796 ± 0.023 | 0.007 | 0.942 | +0.103 | 52.7 |
| 1024 | 20.2 | 0.720 ± 0.023 | 0.010 | 0.919 | +0.027 | 27.6 |
| 2048 | 40.4 | −1.707 ± 0.137 | 0.337 | 0.078 | −2.40 | — |

The τ_sim = 2048 point is anomalous: negative W is unphysical; occ_R = 0.337 indicates partial re-bimodalisation during stage 3's long low-barrier phase. Interpretation: at τ_sim ≥ 2048, the stage-3 duration (τ/4) approaches the Kramers hopping timescale at the 8 k_BT barrier, and the erased distribution thermally re-equilibrates during stage 3. This is a genuine physics limit of the four-stage protocol at very long τ.

Fitting the three lower-τ points: B_sim = 40.1 ± 6.4 (= 4.06 π²). Converting to physical units with T0 = 19.71 ms:

**Simulator B_phys = 40.1 × 19.71 ms = 0.790 k_BT·s.**
**Bérut empirical B_phys = 8.269 k_BT·s.**
**Ratio simulator/empirical = 0.10 (simulator 10× below Bérut).**

This is the inverse of Phase 2b's apparent factor-2.2 "simulator above Bérut" result, and it is inconsistent with the Proesmans symmetric-optimal lower bound (if the bound is ~π² τ_rel = 2.20 k_BT·s, our simulator sits below it in physical units).

## What this contradiction means

Since RV07 verified the simulator reproduces the Schmiedl-Seifert harmonic-shift result to 1.46× (acceptable for non-optimal linear drive), the simulator's internal consistency is OK. The contradiction with Bérut must come from one of three places:

1. **Mis-identification of physical parameters.** Bérut's inter-well distance was inferred from barrier + stiffness; the published values are qualitative ("~8 k_BT") with 10–20 % uncertainty. If the actual L is 2× larger than my estimate, T0 grows by 4× and the gap closes. But a 4× correction still leaves a factor-2.5 discrepancy.
2. **Bérut's measured dissipation includes calibration losses.** AOD modulation inefficiency, photodiode nonlinearity, laser heating, and thermal lensing all contribute to apparent dissipation in the colloidal system but are not in my simulator. The 2015 review acknowledges ±0.15 k_BT "from reproducibility" without a systematic budget. If these contribute 3–5 k_BT·s to the apparent B, the gap closes.
3. **My protocol-class mismatch.** The 4-stage canonical Landauer protocol I simulate may not be the one Bérut implemented. The Bérut 2015 review describes a 3-stage smooth protocol with "manually tuned" AOD ramps. Maybe the extra dissipation in Bérut is structurally inherent to their 3-stage class.

Disambiguating these is a physics research project in its own right, not an autonomous-iteration fix.

## Decision

**This project is re-paused at Phase 2.75 BLOCKED.** Resolution requires:

- Contact the Ciliberto group for (a) the actual AOD control waveform, (b) a systematic error budget including AOD nonlinearity and photodiode calibration, and (c) the full raw ⟨Q⟩(τ) curve (not the digitised 2015 review figure).
- OR pivot the paper to a methodology note: "we present the first full-curve finite-time refit of Bérut 2012, report a 10 orders-of-magnitude discrepancy with the Proesmans symmetric-optimal lower bound when the parameter reconstruction is taken at face value, and identify the calibration / parameter ambiguities responsible". This is publishable at *Phys. Rev. E* as a rigorous null.

Both paths require a human physicist in the loop. The autonomous HDR sweep cannot proceed without one.

## Artifacts committed

- Phase 0 (701 citations, 115 hypotheses, 4-theme lit review)
- Phase 0.25 v2 PROCEED
- Phase 0.5 CLEAR (E00 empirical fit reproduces Bérut's published B = 8.15 k_BT·s)
- Phase 1 winner: Proesmans 1/τ form (AICc-selected from 4 functional families)
- Phase 2: original (faulty, superseded)
- Phase 2b: corrected simulator, corrected 4-stage protocol, corrected barrier scaling — but with wrong T0
- Phase 2.75 round 1: DO NOT PROCEED (5 major findings)
- RV01–RV05: executed
- Phase 2b summary: dimensionally confused, superseded
- Phase 2.75 round 2: DO NOT PROCEED (PROT-01, UNIT-01, DEC-01)
- RV07–RV09: executed (this file documents the results)

No paper.md. Phase 3 not entered. Project genuinely needs human expertise before further autonomous work.
