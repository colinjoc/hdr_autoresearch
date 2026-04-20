# Knowledge Base — Bérut Finite-Time Refit

# Knowledge Base — Part 1 (Themes 1 & 2)

Stylised facts and known pitfalls for the Bérut 2012 finite-time Landauer
refit, drawn from Themes 1 (Landauer theory + finite-time extensions) and
2 (colloidal bit-erasure experiments + optical-trap physics).

---

## Stylised facts

1. **Quasistatic Landauer floor is kT ln 2 per bit erased.** Derived
   for an infinite reservoir and symmetric memory; Reeb & Wolf (2014)
   reformulate as equality with finite-reservoir corrections. Bérut's
   long-τ point saturates this to within published error bars.

2. **Finite-time excess heat is of the form B·kT/τ.** Proesmans, Ehrich
   and Bechhoefer (2020) derive B = π² for the optimal symmetric protocol.
   Three independent routes (optimal transport, thermodynamic length,
   Pontryagin) give the same π². A 1/τ² correction exists at sub-leading
   order (Miller et al. 2019, Bonanca & Deffner 2014).

3. **Bérut's protocol is not the Schmiedl-Seifert optimal one.** It is
   the cleanest implementable double-well erasure: barrier lowering →
   tilt → barrier raising. The B realised is not necessarily π²; it could
   be π² times an order-unity prefactor.

4. **The Bérut dataset has ten points in τ from ~5 s down to ~0.1 s.**
   Reported ⟨Q_diss⟩ values range from ~1.1 kT at τ = 5 s to ~6 kT at
   τ = 0.1 s. Error bars per point are ~10–20%.

5. **The Bérut apparatus is a silica bead in water held in a two-foci
   optical trap.** Bead diameter ~1 μm, trap stiffness ~1 pN/nm per well,
   inter-well separation ~0.8 μm, barrier height ~3–5 kT — within the
   overdamped, thermally-activated regime for which Proesmans' B = π²
   applies.

6. **γ is the Stokes drag on the bead corrected for wall proximity.**
   Faxen corrections from Berg-Sørensen & Flyvbjerg (2004) apply for
   beads within a few radii of the cover slip. Uncalibrated γ is the
   single largest source of systematic error in ⟨Q_diss⟩.

7. **Trap stiffness is calibrated by PSD fit to a Lorentzian.** The
   tweezercalib MATLAB package (Tolić-Nørrelykke, Berg-Sørensen and
   Flyvbjerg 2004) is the industry standard. Residual 5–10% systematic.

8. **Well-depth asymmetry r = V_left/V_right is extractable from
   Boltzmann histogram in bistable regime.** Requires long enough sampling
   to populate both wells; κ-curvature ratio alone does not fix r
   (Florin, Pralle, Stelzer and Hörber 1998; Bakhtiari, Esposito and
   Lindenberg 2015).

9. **Proesmans et al. (2020) cites Bérut as the experimental motivation**
   but does not re-fit the full ten-point curve. They compare only to the
   quasistatic point.

10. **Dago et al. (2021) reach the Landauer bound within 1%** in an
    underdamped micromechanical oscillator using virtual double-well
    feedback. Their apparatus is fundamentally different from Bérut's
    (underdamped, virtual potential) so it is a comparator not a
    substitute.

11. **Jun, Gavrilov and Bechhoefer (2014)** performed the first
    feedback-trap Landauer experiment. Approximately 4600 cycles total
    per condition; tighter error bars than Bérut but virtual potential.

12. **Hong, Lambson, Dhuey and Bokor (2016, Sci. Adv.)** measure
    nanomagnetic erasure at (1.0 ± 0.22) kT ln 2 — consistent with
    Landauer but insufficient resolution for finite-time refit.

13. **Single-electron Koski et al. (2014, 2015)** implement the Szilard
    and Landauer cycles in a single-electron box; cross-substrate
    comparison.

14. **Zulkowski and DeWeese (2014)** give a pre-Proesmans finite-time
    coefficient derived from Hellinger distance; their coefficient is
    close to but not identical to π² for the symmetric case.

15. **Asymmetric generalisation B(r) = π²(1+r)²/(4r)** is proposed in
    this project's predecessor paper as a heuristic; the literature has
    no direct experimental test of it.

16. **Sagawa and Ueda (2009)** derive distribution-dependent corrections
    to the Landauer bound when initial occupations are unequal; this is
    the principled way to frame the asymmetric-r extension.

17. **Van Vu and Saito (2022, PRL 129)** derive a tighter
    geometric-speed-limit finite-time Landauer bound that coincides with
    π² for Bérut-style protocols but deviates at shorter τ.

18. **Zhen, Egloff, Modi and Dahlsten (2021)** derive an alternative
    universal bound on the energy cost of bit reset. Their coefficient
    is ≤ π² in the short-time regime.

19. **Bérut's ⟨Q_diss⟩ error bars are bootstrap-derived** from trajectory
    histograms. Scope check flags them as potentially optimistic; the
    TUR gives an independent floor that can be used to cross-check.

20. **Engineered swift equilibration** (Martinez et al. 2016; Chupeau et
    al. 2018; Proesmans and Bechhoefer 2019) is the protocol family
    that saturates the π² bound. A re-run Bérut-style experiment
    should use these protocols.

21. **Roldán, Martínez, Parrondo and Petrov (2014)** measured universal
    symmetry-breaking energetics in a Brownian two-trap — the closest
    existing analog to Bérut's cycle — and confirmed kT ln 2 cost at
    quasistatic limit.

22. **Kramers' rate determines the barrier-crossing time scale.** For
    Bérut's ~3-5 kT barrier the Kramers time is ~10-100 ms, comparable
    to the short-τ Bérut points — meaning the short-τ data include both
    finite-time protocol dissipation AND under-thermalised trajectory
    effects.

23. **Effective temperature from laser heating** is typically +1-2 °C
    above ambient for Bérut-scale laser power. Propagates into the
    translation between U(x) in units of kT and in units of joules.

24. **The Bérut experiment does NOT directly measure r.** It reports
    stiffnesses and separations. Extracting r requires re-analysis of
    the published histograms and propagating systematic bounds.

25. **Barato-Seifert TUR** gives a lower bound on the variance of the
    time-integrated heat, independent of the Proesmans coefficient.
    This is a second-order sanity check on published error bars.

26. **Esposito and Van den Broeck (2010, 2011)** decompose entropy
    production into adiabatic and non-adiabatic pieces. Bérut's excess
    heat is the non-adiabatic piece — this is what B·kT/τ measures.

27. **Aurell et al. (2011, 2012, 2023)** give the rigorous
    optimal-transport derivation of the finite-time Landauer bound. This
    is the mathematical gold standard and is the basis for Proesmans'
    derivation.

28. **Bérut's photodiode position detection** has sub-nanometer
    resolution over ~kHz bandwidth. Noise floor is set by shot noise
    on the back-focal-plane interference signal (Gittes and Schmidt
    1998; Florin et al. 1998).

29. **Schmiedl-Seifert (2007)** derived the earliest 1/τ excess-heat
    scaling for overdamped control. Their coefficient depends on the
    chosen control parameter; for the specific Bérut-style control it
    reduces to Proesmans' π².

30. **Optimal erasure protocols typically include discontinuous jumps**
    at τ = 0 and τ = τ_final (Schmiedl-Seifert 2007). The Bérut protocol
    is smooth, which is another reason the realised B may exceed π².

---

## Known pitfalls

**P1: Assuming Bérut's error bars are correct.** They are bootstrap
estimates from a finite sample. Compare against the TUR floor before
trusting them. If too tight, widen.

**P2: Confusing γ (drag) with κ (stiffness).** Both enter ⟨Q_diss⟩
via different pathways; mis-calibrating either biases the fit.

**P3: Fitting only the 1/τ term.** The 1/τ² correction can be
significant for short τ. Do a three-parameter fit (kT ln 2, B, C)
and report whether C is significant.

**P4: Extracting r from stiffness ratio alone.** Stiffness curvature
ratios κ_left/κ_right do not uniquely determine V_left/V_right depths;
the relationship involves the barrier height too. Must use Boltzmann
histogram or Kramers-rate asymmetry.

**P5: Neglecting laser-heating effective-temperature correction.**
Small (~1–2 °C) but propagates through U(x) in joules.

**P6: Assuming Markov dynamics for the bead.** Hydrodynamic memory
effects are non-Markovian (Wang-Uhlenbeck 1945; Goerlich et al. 2023).
For Bérut's τ range this is usually negligible but should be checked.

**P7: Interpreting Proesmans B = π² as the only prediction.** It is
one of a family (Proesmans, Van Vu-Saito, Zhen et al., Zulkowski-
DeWeese); they differ in regime and protocol. The refit should
enumerate which are in play.

**P8: Confusing 'Landauer verified at long τ' with 'finite-time formula
verified'.** Bérut verified kT ln 2 at the single quasistatic point.
The finite-time formula has never been re-fit against the full curve.

**P9: Over-trusting a single experimental dataset.** Dago's apparatus
and Jun's feedback trap produce comparable data with different
systematics. A refit that cites both as consistency checks is
stronger than a Bérut-only refit.

**P10: Conflating symmetric and asymmetric predictions.** B(r) reduces
to π² at r = 1; the asymmetric test requires r to be far from 1, and
scope check (i) warns this may not be the case in Bérut.

**P11: Ignoring non-conservative optical forces.** Pesce et al. (2009)
show ~5–10% non-conservative component in tight traps. These violate
the equilibrium Boltzmann histogram, biasing r extraction.

**P12: Bootstrap of error bars not error bars on bootstrap.** Bérut
reports σ on each point from individual-trajectory histograms. A
refit should bootstrap at the trajectory level, not the
already-aggregated-point level.

**P13: Treating the Bérut cycle as time-reversal symmetric.** It is
not — erasure is intrinsically irreversible. Forward- and backward-
protocol work distributions are not mirror images.

**P14: Ignoring the 'no-erasure' control.** Bérut's control experiment
(barrier lowering only, no tilt) should show zero excess heat.
Re-checking this is a consistency step.

**P15: Reporting a fitted B without specifying the protocol family.**
Different protocols give different B. A refit must either restrict to
Bérut's realised protocol (producing a protocol-specific B) or assert
that the realised protocol saturates the Proesmans bound (requiring
justification).

---

# Knowledge base — Part 2 (Themes 3 and 4)

Stylised facts distilled from the literature review.

## F3.1 The overdamped Fokker–Planck slowest eigenvalue for a symmetric double well

At weak noise (Delta U >> k_B T), the slowest non-zero eigenvalue lambda_1 ~ 2 k_Kramers, where k_Kramers = (omega_well omega_barrier) / (2 pi gamma) exp(-Delta U / k_B T). This eigenvalue sets the inverse relaxation time for the bimodal-to-unimodal transition that Landauer erasure is. Source: Risken 1989 (T3_003), Hänggi-Talkner-Borkovec 1990 (T3_002).

## F3.2 The asymmetric Kramers prefactor

For asymmetric wells with depth ratio r, the forward and backward rates are not equal and the slowest eigenvalue picks up a geometric factor. For equal curvatures but unequal depths, the prefactor geometric factor is (1+r)²/(4r), with minimum 1 at r = 1. Source: Coffey-Kalmykov-Titov 2005 (T3_031), Hänggi-Talkner-Borkovec 1990 (T3_002).

## F3.3 The Schmiedl–Seifert variational optimal protocol for harmonic-trap shift

For shifting a 1D harmonic trap from x_0 to x_f in time tau, the minimum-work protocol has finite jumps at t = 0 and t = tau and excess-work W_diss - ΔF ≈ (gamma (x_f - x_0)² / tau) — scales as 1/tau. Source: Schmiedl-Seifert 2007 (T3_006).

## F3.4 The Wasserstein refined second law (Aurell 2011–2012)

For overdamped 1D Langevin dynamics, the mean dissipated work over a finite-time protocol of duration tau satisfies:

    ⟨W_diss⟩(tau) >= (k_B T / (tau D)) W²_2(rho_initial, rho_final)

where W_2 is the L² Wasserstein distance. This bound is tight in the fast-time limit. Source: Aurell-Mejía-Monasterio-Muratore-Ginanneschi 2011/2012 (T3_012, T3_013).

## F3.5 The Proesmans finite-time Landauer coefficient B = pi²

For a symmetric double-well with full dynamic control and perfect initial equilibrium, the mean dissipated heat in finite-time bit erasure is

    ⟨Q_diss⟩(tau) >= k_B T ln 2 + (pi² k_B T)/tau

valid in the regime where tau is long enough to allow thermalisation but short enough that the 1/tau correction is not negligible compared to ln 2. Source: Proesmans-Ehrich-Bechhoefer 2020 (T3_014, T3_015).

## F3.6 B = pi² is a lower bound, not a prediction

The bound is achievable only under idealised full-control of the potential (unrestricted U(x,t) landscape, no physical barrier to what the experimenter can command). Real experimental protocols typically dissipate more than the bound. The Bérut 2012 protocol is a specific, not-necessarily-optimal, protocol, so the empirical B will be >= π² by construction; a discrimination test asks whether it is **near** π² or whether it is substantially larger.

## F3.7 The Wasserstein distance for a bit erasure

For a system uniformly distributed over two wells of depth V_L and V_R (bit 0 and bit 1) and finally all in one well, the Wasserstein-2 distance depends on the inter-well separation L and the asymmetry. For equal-depth wells, W²_2 = L²/4. For asymmetric wells with initial occupancy proportional to exp(-V/kT), W²_2 has a geometric correction that generalises to give the predicted B(r) asymmetric factor (heuristic connection, not rigorously derived).

## F3.8 Kramers timescale vs Langevin relaxation timescale

The shortest relevant timescale in bit erasure is the Langevin relaxation within one well: t_relax ~ gamma / omega_well². The longest is the Kramers escape time: t_Kramers = 1 / (2 k_Kramers). For B k_B T / tau to dominate over ln 2 k_B T, we need B/tau > ln 2 ≈ 0.69, so tau < 14 seconds for B = π². The Bérut data go out to tau = 40 seconds, so the dataset spans both the dominant-1/τ and the dominant-ln 2 regimes. Source: Bérut 2012 (T3_046).

## F3.9 Boltzmann inversion bias at finite sample

For histogram-based Boltzmann inversion of the potential, the statistical bias at each bin scales as (k_B T)² / (N_effective bin_count). For N_eff ~ 10⁵ and bin_count ~ 50, the bias is ~ 0.01 k_B T per bin — small, but not zero. Source: Shoji et al. 2019 (T4_177), Bianchi et al. 2023 (T4_178).

## F3.10 Optimal protocol finite jumps

The Schmiedl-Seifert and Proesmans optimal protocols prescribe jumps in the control parameter at t = 0 and t = tau. In Bérut 2012 the protocol is a smooth lowering of the barrier; this is **not** the optimal protocol. Consequently the empirical B from the Bérut protocol should be larger than π².

## F3.11 The virtual-potential (feedback-trap) advantage

In a feedback trap the "potential" is constructed by software-applied feedback forces and is **known by construction**. This gives direct programmatic control over the asymmetry — r is not inferred, it is set. Source: Jun-Bechhoefer 2012 (T4_161), Bechhoefer feedback-trap series.

## F3.12 Bérut is NOT a virtual-potential trap

Bérut 2012 uses a time-shared actual double-well optical trap, not a virtual feedback trap. The trap potential U(x) is determined by (laser intensity × time at each focus) and must be inferred from the equilibrium position histogram — it is not set a priori. Source: Bérut 2012 Nature (T3_046), Bérut-Petrosyan-Ciliberto 2015 review (T3_048).

## F3.13 The Bérut published r

The Bérut authors do not publish r explicitly. They state the asymmetry is "reduced to ~0.1 k_B T" by tuning, which implies r values within ~ 0.8 to 1.2 of symmetric. The published U(x) polynomial is 6th-degree but the coefficients are not tabulated in the primary Nature paper or in the 2015 review. Source: Bérut-Petrosyan-Ciliberto 2015 (T3_048).

## F3.14 Bérut error bars

Dissipated heat has published error bar ± 0.15 k_B T, attributed to "reproducibility of measurement with same parameters" — this is a statistical estimate, not a fully propagated systematic uncertainty. Source: Bérut 2015 (T3_048).

## F3.15 The Bérut sample rate and N_effective

Data acquired at 502 Hz for ~ 50 minutes = 1.5 × 10⁶ points. Autocorrelation time of position in the trap ~ 3 ms, so N_effective ≈ 10⁵. Source: Bérut 2015 (T3_048).

## F3.16 The Gavrilov–Bechhoefer 2016 asymmetric-well result

In a virtual-potential feedback trap with *known* asymmetry, Gavrilov & Bechhoefer 2016 demonstrated that the **mean work** to erase can be less than k_B T ln 2 when the initial distribution is biased and the asymmetry is large. This is not a violation of Landauer — the dissipated heat (not mean work) is always bounded below by k_B T ln 2. But it means the mean work depends on the asymmetry in ways the Landauer bound does not constrain. Source: T3_053.

## F3.17 The Chiu–Lu–Jun 2022 asymmetric finite-time Landauer

In a feedback-trap-controlled asymmetric double well, Chiu-Lu-Jun 2022 directly tested the finite-time Landauer coefficient B at explicitly known r. Their result is the closest precedent for the asymmetric B(r) test but uses a different protocol class. Source: T3_089.

## F3.18 AOD diffraction asymmetry

A practical acousto-optic deflector does not deflect identically at different angles; typical asymmetry between nearby deflection positions is 5-10 percent in intensity. When deflector positions are used to time-share between two traps, this translates directly to a well-depth asymmetry in the effective potential. The Bérut 2012 trap uses AOD switching and does not report the measured diffraction-asymmetry. Source: Valentine et al. 2008 (T4_033), Serrao et al. 2024 (T4_146).

## F3.19 Time-sharing frequency limits on time-averaging

For time-shared dual traps, the switching rate must be >> the bead's inverse relaxation time for the bead to see an effective time-averaged potential. Bérut uses 10 kHz switching and bead relaxation ~ ms — this is on the edge of safety. Source: Chattopadhyay et al. 2013 (T4_036), Ranaweera & Bhattacharya 2010 (T4_039).

## F3.20 The Bérut potential height calibration

High-intensity barrier ~ 8 k_B T, low-intensity barrier ~ 2.2 k_B T. No explicit uncertainty. Polynomial fit is 6th degree. Source: T3_048.

## F3.21 Zulkowski-DeWeese Hellinger bound

Zulkowski-DeWeese 2014 gave an earlier finite-time erasure bound in terms of the squared Hellinger distance between initial and final distributions divided by tau. Tighter in the quasi-static limit, looser at finite tau than Proesmans. Source: T3_016.

## F3.22 Shortcut-to-adiabaticity

Using shortcut-to-adiabaticity protocols (Boyd-Patra-Jarzynski-Crutchfield 2022, T3_090), erasure can be accelerated below the naive Proesmans bound at extra dissipation cost. The asymmetric extension appears in the shortcut cost structure. Source: T3_090.

## F3.23 The Zhen et al. 2021 universal bit-reset bound

Zhen-Egloff-Modi-Dahlsten 2021 give a universal hardware-independent lower bound. In the zero-error, equal-initial-probability limit, the scaling is also B/tau, with a B-coefficient that matches Proesmans. Source: T3_060.

## F3.24 Thermodynamic uncertainty relation (TUR)

The TUR (Barato-Seifert 2015, T3_107) bounds current fluctuations by dissipation. For bit erasure, it gives a complementary bound to Proesmans in terms of final-state-error variance.

## F3.25 Identifiability of r from published Bérut

Without raw photodiode time series, r is estimable only from digitised U(x) plots. 95 percent CI on r is roughly 0.7–1.5 (high barrier) and 0.5–2 (low barrier).

## F3.26 Sensitivity of B(r) = π²(1+r)²/(4r) near r = 1

(1+r)²/(4r) evaluated at r = 1 has derivative 0 (it's a minimum). A ±50 percent CI on r near r = 1 maps to only ~ 5 percent uncertainty on B(r). Consequence: the Bérut dataset cannot discriminate B(r) from B = π² for realistic r values.

## F3.27 Bérut protocol is NOT the optimal Schmiedl-Seifert protocol

Bérut's erasure protocol is a smooth linear lowering of the barrier. The optimal protocol has finite jumps at t=0 and tau. So empirical B > π² is expected simply from protocol-suboptimality.

## F3.28 No rigorous derivation of B(r) = π²(1+r)²/(4r)

The formula B(r) = π²(1+r)²/(4r) is a heuristic that inherits the asymmetric Kramers-prefactor structure. It has not been rigorously derived from the Aurell-Proesmans Wasserstein optimal-transport framework. This is flagged by Phase 0.25.

## F3.29 Dago 2024 reliability-operation-cost curves

Dago-Ciliberto-Bellon 2024 (T3_058) give measured erasure-cost curves in cyclic underdamped erasure as a function of asymmetry. These are the closest experimental comparator for B(r) in a physical (non-virtual) double well.

## F3.30 Calibration uncertainty budget

For a Bérut-style reconstruction using PSD + Boltzmann inversion, the dominant uncertainty contributions are: (i) PSD sensitivity factor ± 3 percent; (ii) Boltzmann-inversion statistical ± 0.02 k_B T per bin; (iii) AOD diffraction asymmetry ± 5-10 percent; (iv) laser-power drift over 50 min acquisition ± 3-5 percent. Total uncertainty on well-depth asymmetry ± 10-15 percent. This is the irreducible uncertainty floor on r for the Bérut published data.
