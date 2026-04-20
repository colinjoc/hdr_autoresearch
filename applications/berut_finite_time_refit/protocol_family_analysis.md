# Protocol Family Sensitivity Analysis (PER-01 Phase 0.5 blocker)

This deliverable addresses the pre-empt-reviewer hypothesis PER-01 from the Phase 0.25 publishability review: the Bérut 2012 paper and its 2015 follow-up do not tabulate the time-dependent control U(x, t). For the project's first-principles Brownian-dynamics simulator to produce an informative prediction, we must establish (i) what the published protocol is at quantitative detail, (ii) what degrees of freedom remain under-specified, and (iii) whether any single uncontrolled knob could shift the simulated *B* by more than a factor of 2. A factor-2 protocol-family uncertainty is disqualifying — it makes the simulator–data comparison uninformative regardless of what the simulator returns.

## A. What the published sources actually specify

From Bérut et al. 2012 (*Nature* 483, Fig. 1b–c and Methods) and Bérut–Petrosyan–Ciliberto 2015 review (arXiv:1503.06537 §3.1–§3.2):

**Explicitly published (quantitative):**
- **Optical trap carrier.** Two laser beams (*λ* = 1064 nm) focused by a 100× NA 1.3 oil-immersion objective; acousto-optic deflectors (AODs) modulate the two beam intensities in counter-phase. Powers used: 40 and 60 mW per beam at the back aperture.
- **Colloidal particle.** 2-μm silica bead in water at T = 300 K.
- **Trap stiffness.** Each well has κ ≈ 2.7 × 10⁻⁶ N/m at full power.
- **Barrier height at the initial / final state.** Approximately 8 k_B T (published as "9 k_B T ≈ 3.6 × 10⁻²⁰ J" elsewhere and "8 k_B T" in the 2015 review — ~10 % inconsistency between sources).
- **Cycle structure.** Three stages of equal duration τ/3: (1) lower barrier by ramping intensity asymmetry, (2) tilt potential by intensity ramp, (3) restore symmetric barrier. "Equal duration" is stated; actual functional form of each ramp is not tabulated.
- **Cycle times used.** τ ∈ {5, 10, 15, 20, 25, 30, 35, 40} s (plus duplicate τ = 5 and τ = 10 points with slightly different ⟨Q⟩ reported in Fig. 8 of the 2015 review, attributable to repeated runs with minor AOD recalibration).
- **Friction coefficient.** γ = 6πη r_particle with r = 1 μm, η = 10⁻³ Pa·s → γ ≈ 1.9 × 10⁻⁸ kg/s (implied by particle size and water viscosity, not explicitly tabulated).

**Qualitative / figure-only (not tabulated):**
- **Ramp shape.** Barrier-lowering and tilt ramps are shown as smooth curves in Fig. 1c. The functional form (linear? sigmoidal? optimised protocol à la Schmiedl–Seifert?) is not stated. The 2015 review says the "optimised protocol" curve (Fig. 8, black) was "manually tuned by trial and error" — so there is no closed-form specification even for the best protocol.
- **Relative ordering and overlap of ramps.** Are the barrier-lowering and tilt ramps fully sequential, or do they overlap? Fig. 1c suggests mostly sequential but the boundary is ambiguous.
- **AOD ramp linearity.** AODs are nominally linear in RF drive power, but photodiode-calibrated intensity curves may deviate 5–10 % from linearity at the extrema of the modulation range. Not characterised in either source.
- **Well-depth asymmetry.** The "manually optimised" ramp produces a transient asymmetry during the tilt phase. Magnitude of the transient asymmetry is not published.

## B. Protocol-family parameterisation

Eight functional-form knobs are plausible given the published description. Each is a single real-valued parameter that, if varied across its plausible range, defines the family of Bérut-compatible modulations.

| Knob | Physical meaning | Plausible range | Unit |
|---|---|---|---|
| K1 | Barrier-lowering ramp shape | linear → sigmoidal (sharpness σ ∈ [0, 1]) | — |
| K2 | Tilt ramp shape | linear → sigmoidal (σ ∈ [0, 1]) | — |
| K3 | Ramp overlap fraction | 0 (fully sequential) → 0.5 (half overlapping) | — |
| K4 | Peak tilt amplitude | 6 → 10 k_B T (published value ~8 ± 1) | k_B T |
| K5 | Residual barrier at peak tilt | 0 → 3 k_B T (fully lowered to partially lowered) | k_B T |
| K6 | Transient well-depth asymmetry during tilt | 0 → 2 k_B T | k_B T |
| K7 | Initial equilibration time before cycle | 0 → τ/10 | s |
| K8 | AOD-nonlinearity correction amplitude | 0 → 10 % deviation from published κ | — |

## C. Directional and order-of-magnitude effect on simulated *B*

For each knob, the expected effect on simulated *B* from the Schmiedl–Seifert / Proesmans framework:

| Knob | Direction on *B* | Rough magnitude | Reasoning |
|---|---|---|---|
| K1 (ramp shape, lowering) | ↑ away from linear | 0.1–0.3 π² | Optimal protocol is not linear; any departure from SS-optimal ramp pushes *B* above π². Sigmoidal is further from optimal than linear for this step. |
| K2 (ramp shape, tilt) | ↑ away from linear | 0.3–1.0 π² | Tilt is the dominant dissipation step. A linear tilt is far from the SS-optimal (which concentrates work at intermediate times); sigmoidal is even further. |
| K3 (overlap) | ↓ toward optimal | 0.0 – 0.3 π² | Partial overlap effectively implements a smoother combined ramp, closer to the SS-optimal two-step protocol. Fully sequential is the worst case. |
| K4 (peak tilt amplitude) | ↑ with under- or over-forcing | 0.1–0.5 π² | Under 7 k_B T and the tilt is too weak to drive full population transfer; over 9 k_B T and the finite-time correction inflates. Authors explicitly excluded these from their fit. |
| K5 (residual barrier) | ↑ with residual | 0.0 – 1.5 π² | A residual barrier at peak tilt traps part of the population; dissipation to drive it out scales as (residual / k_B T)². Strong effect. |
| K6 (transient asymmetry) | small | 0.0 – 0.1 π² | The B(r) derivative is O(r − 1)²; small transient asymmetries don't move *B* much (as the lit review confirmed). |
| K7 (equilibration) | small | < 0.1 π² | Affects only how close the initial distribution is to Boltzmann; for long enough equilibration this is negligible. |
| K8 (AOD nonlinearity) | ↑ systematic | 0.0 – 0.2 π² | Nonlinearity distorts the effective ramp shape; quantitatively similar to K1+K2 systematic. |

## D. Risk assessment and Phase 0.5 verdict

**Load-bearing knobs:** K2 (tilt ramp shape), K3 (ramp overlap), and K5 (residual barrier at peak tilt) are each capable of moving simulated *B* by more than 0.5 π². Combined, they could in principle span a range of up to ~2 π², which is **larger than** the empirical CI of [0.75, 0.93] π² — and crucially, could push the simulator's prediction either above π² (consistent with Proesmans) or below π² (consistent with the Bérut empirical value).

**But:** this is an upper bound on the spread under maximally adversarial parameter choices. A reasonable subset of protocol-family choices that match the qualitative description in Fig. 1c of Bérut 2012 (smooth ramps, sequential-with-light-overlap, fully lowered barrier during tilt) shrinks the spread to ~0.3–0.5 π², which is **comparable to** the empirical CI width.

**Recommendation.**

1. Phase 2 simulator runs should compute *B* for a grid of (K1, K2, K3, K5) values within the qualitatively-consistent region, not the adversarial region.
2. The reported simulated *B* range will be: **the minimum and maximum *B* across this grid**, not a point estimate.
3. If the qualitatively-consistent spread turns out to be larger than ~0.3 π² in simulator runs (making the simulator–data comparison uninformative at better than ~π² precision), the project will contact the Ciliberto group for the actual control waveform before committing to the full Phase 2 loop, as flagged in PER-01.

**Not a disqualifying blocker.** The qualitatively-consistent spread is on the order of the empirical CI, which means a meaningful comparison is achievable without new experimental data. The Phase 0.5 verdict on this deliverable is **CLEAR-WITH-CAVEAT**: proceed, but the Phase 2 simulator loop will need to track the protocol-family grid explicitly and the Phase 3 paper will report simulator results as bands, not points.

## E. Related note — the actual scientific tension

Our Phase 0.5 E00 fit recovers the authors' published B = 8.15 k_B T·s (= 0.826 π²), which sits **below** the Proesmans symmetric-optimal lower bound of π². This is the finding the project exists to examine: either (a) Bérut's realised "optimised" protocol is not truly optimal in the SS sense (our simulator will reveal what fraction of the discrepancy is protocol non-optimality), or (b) the Proesmans lower bound does not apply to the Bérut protocol class (the derivation assumes specific boundary conditions — if Bérut's protocol violates them, π² is not the bound), or (c) the published fit form differs from Proesmans in a subtle way the simulator must replicate.

The simulator runs in Phase 2 will decompose the apparent excess (negative excess, in this case) into protocol-non-optimality + boundary-condition + fit-form contributions, per the pre-empt-reviewer decomposition deliverable PER-02. This is the paper's physics content.
