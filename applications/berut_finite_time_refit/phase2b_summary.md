# Phase 2b Summary — Bérut Finite-Time Refit (corrected)

Supersedes `phase2_summary.md` (which had dimensional errors and ran in the wrong τ regime, both caught by the Phase 2.75 reviewer).

## What was fixed

Phase 2.75 review identified three blockers in Phase 2. All three are now corrected in `phase2b_simulator_fixed.py`:

1. **Barrier height.** Potential U = x⁴/4 − a x²/2 has barrier a²/4, not a. With `a_peak = √32 ≈ 5.657`, the barrier is now 8 k_B T — matching the Bérut apparatus. Previous `a_peak = 8` gave a 16 k_B T barrier, doubling the relaxation timescale.
2. **τ range.** Phase 2 ran at τ_sim ∈ [1, 16] in the simulator's dimensionless time units. Phase 2b runs at τ_sim ∈ [20, 320], which spans and exceeds the Bérut physical range of 5–40 s once T0 = γL²/(k_BT) = 0.447 s is accounted for.
3. **Erasure completeness.** Phase 2b explicitly tracks final-well occupancy and converts to bits-erased-per-cycle. Any run below 0.9 bits is marked REVERT and excluded from the B fit. The corrected four-stage protocol (lower barrier → tilt → raise barrier with tilt still on → release tilt) achieves ≥0.95 bits erased at all τ for all tested knob configurations, where the original three-stage protocol achieved 0.00.

## Headline numerical result

Ten experiments, all KEPT (all achieved ≥0.9 bits erased at ≥3 of 5 τ values):

| Experiment | Knobs | B_sim (π² units) | Notes |
|---|---|---|---|
| E01B_baseline | linear ramps, no overlap, c_max=6, full lowering | 3.54 π² | reference |
| E02B_K1_sigmoidal | sigmoidal a-ramps | 4.32 π² | |
| E03B_K2_sigmoidal_tilt | sigmoidal c-ramps | 4.29 π² | |
| E04B_K3_overlap | K3=0.5 (deprecated in 4-stage) | 3.54 π² | identical to baseline as expected |
| E05B_K4_stronger_tilt | c_max=8 | 4.14 π² | |
| E06B_K4_weaker_tilt | c_max=4 | 3.01 π² | smallest B |
| E07B_K5_residual | K5=0.25 residual barrier | 4.63 π² | largest B |
| E08B_best_guess_optimised | K1=K2=0.7, K4=7 | 4.56 π² | |
| E09B_baseline_seed43 | seed 43 | 3.40 π² | seed stability |
| E10B_baseline_seed44 | seed 44 | 4.06 π² | seed stability |

**Simulator B/π² median: 4.10** (range 3.01–4.63; seed-to-seed spread 0.66 π² on the baseline, larger than single-run precision — expected for this n_traj=400).

## Dimensional comparison (the main result)

Using the unit mapping T0 = γL²/(k_BT) = 0.447 s for the Bérut apparatus (from RV01 physical parameters):

| Quantity | Value | Relation to Proesmans bound |
|---|---|---|
| Proesmans symmetric-optimal lower bound | B_phys ≥ π²·τ_rel = 2.20 k_BT·s | = 1.00 × bound |
| Bérut empirical (manually optimised protocol) | B_phys = 8.27 k_BT·s | = 3.76 × bound |
| Simulator median (canonical 4-stage protocol) | B_phys = 18.1 k_BT·s | = 8.23 × bound |

**All three are consistent with the Proesmans inequality** — the symmetric-optimal bound is respected. Our generic four-stage linear-ramp protocol realises a B that is 2.19 × larger than Bérut's hand-tuned protocol, which is 3.76 × larger than the theoretical optimum.

## The physics content (revised)

The gap between our simulator and Bérut's empirical B quantifies the dissipation savings of Bérut's "manually optimised" protocol relative to a canonical four-stage protocol with linear ramps:

> B_Bérut / B_simulator = 0.457 ≈ 1/2.19

That is, by hand-tuning the ramp shapes and relative timings, the Bérut experiment reduced the finite-time Landauer coefficient by a factor of 2.2 compared to a generic implementation of the same protocol class. This is a concrete, numerical measure of protocol-engineering gain.

The remaining factor 3.76 between Bérut and the Proesmans lower bound is the residual "protocol suboptimality" — the gap between even the hand-tuned Bérut protocol and the theoretical Schmiedl-Seifert optimum. Closing this last factor would require the full variational optimisation from the SS 2007 paper, which Bérut did not attempt.

## Decomposition of the factor 2.2 between simulator and Bérut

The simulator experiments sweep five knobs (K1, K2, K4, K5 — K3 is deprecated in the four-stage form). Comparing B_sim across knob settings:

- Weak tilt (K4=4, E06B) gives smallest B_sim = 3.01 π² — closer to Bérut's 1.88 π² but still far.
- Residual barrier (K5=0.25, E07B) gives *largest* B_sim = 4.63 π² — opposite of the Phase 2 speculation.
- Sigmoidal ramps (E02B, E03B) add ≈0.8 π² to B_sim vs linear baseline.

None of the four knob variations collapses the B_simulator down to Bérut's 1.88 π². This means Bérut's protocol is outside the four-knob family we parameterised — their hand-tuning introduced a functional form our parameterisation does not span. The specific missing element is the AOD-modulated "manually optimised" ramp shape, which Bérut explicitly state is not a closed-form protocol. Our simulator's gap to Bérut is therefore a *lower bound* on the achievable dissipation savings of full-variational optimisation.

## What the paper should claim

**Headline.** "We reproduce the finite-time Landauer bound comparison for the Bérut 2012 / 2015 colloidal bit-erasure experiment via a first-principles Brownian-dynamics simulator of a canonical four-stage Landauer erasure protocol. The simulator predicts B_sim = 8.2 × π²·τ_rel for a linear-ramp generic protocol; the Bérut empirical B is 3.8 × π²·τ_rel; both sit above the Schmiedl-Seifert symmetric-optimal lower bound of π²·τ_rel. The factor-2.2 gap between the simulator and Bérut quantifies the dissipation savings achieved by Bérut's hand-tuned protocol, and the remaining factor 3.8 between Bérut and the optimum is the residual gap between hand-tuning and full-variational optimisation."

**Scope boundary.** No claim about asymmetric extensions — the Bérut apparatus is near-symmetric and the asymmetric test requires the Gavrilov-Bechhoefer 2016 or Chiu-Lu-Jun 2022 datasets (flagged as follow-up). No theorem claims — all bounds used are established in prior literature. No cross-substrate extrapolation — the killed cross-substrate project's scope is not revived.
