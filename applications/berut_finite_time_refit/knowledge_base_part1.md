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
