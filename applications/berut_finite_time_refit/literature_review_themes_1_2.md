# Literature review — Themes 1 and 2

Scope: first of two Phase 0 lit-review deliverables for the Bérut finite-time
refit project. Theme 1 consolidates Landauer's principle and its finite-time
extensions. Theme 2 consolidates colloidal bit-erasure experiments and
optical-trap physics (apparatus, calibration, potential reconstruction). The
two themes together cover the theoretical prediction we aim to refit
(B = π²) and the experimental data (the Bérut 2012 ten-point curve) plus the
identifiability question for the well-depth asymmetry ratio *r*.

Throughout this document *Q*_diss denotes the average excess heat beyond the
quasistatic Landauer limit for erasing one symmetric bit at cycle time τ:
⟨*Q*_diss⟩(τ) = *k*_B *T* ln 2 + B *k*_B *T* / τ + O(1/τ²). The symmetric
prediction B = π² is Proesmans, Ehrich and Bechhoefer (2020). The asymmetric
generalisation under test is B(r) = π² (1 + r)² / (4 r), which reduces to π² at
r = 1 and inflates the coefficient for any r ≠ 1.

---

## Theme 1 — Landauer's principle and finite-time extensions

### 1.1 Quasistatic foundations: Landauer, Bennett, and the original claim

Landauer's 1961 IBM Journal paper frames the irreversibility of one-bit
erasure in thermodynamic terms: any logical operation that is not
injective reduces the phase-space volume accessible to the memory, and the
resulting entropy must be exported to the environment as heat. For a
symmetric two-well memory in contact with a reservoir at temperature *T*,
the minimum heat dissipated per reset is *k*_B *T* ln 2 per bit. The argument
is quasistatic: it assumes that the memory is manipulated infinitely slowly,
so that the work done exactly equals the free-energy change.

Bennett's 1982 *Int. J. Theor. Phys.* review placed the Landauer limit at
the heart of the Maxwell-demon resolution — the demon may appear to violate
the second law when it measures a system's microstate, but closing the loop
requires resetting the demon's memory, and the associated Landauer cost
exactly restores the second law. This reframing — that erasure, not
measurement, is where the entropy flows — became the textbook account.
Later discussion by Earman and Norton (1999), Bennett (2003), Norton (2013),
and Ladyman and Robertson (2013) established that, strictly as an *exact
equality*, Landauer's bound requires a long list of caveats: a symmetric
memory, an infinitely large reservoir, and a quasistatic protocol. Each of
those caveats is violated in the Bérut experiment, motivating the finite-size
and finite-time corrections reviewed below.

The first rigorous proof under modern stochastic-thermodynamic assumptions is
Reeb and Wolf (2014), who derive the principle as an equality that reduces to
the kT ln 2 inequality only in the infinite-reservoir limit. For finite
reservoirs, the heat of erasure exceeds kT ln 2 by a calculable
positive correction. In Bérut's colloidal apparatus the fluid bath is
effectively infinite on the time scale of the erasure protocol, so the
Reeb–Wolf correction is negligible; the residual excess heat observed at any
τ must be finite-*time* rather than finite-*size*.

A parallel stream of work extends Landauer beyond the symmetric case. Sagawa
and Ueda (2009) derive the minimum-energy cost for memory operations
including the asymmetric case, and show that the bound picks up a
distribution-dependent correction when the initial occupations of the two
wells are unequal. Maroney (2009) provides a general statement of
Landauer's principle for memories with arbitrary state-dependent entropy,
temperature, and mean energy. Kolchinsky and Wolpert (2017) catalogue the
dependence of dissipation on the initial distribution over states, making
explicit the claim that the excess over Landauer is bounded below by a KL
divergence between the actual initial distribution and the distribution that
would equilibrate under the final protocol.

### 1.2 Stochastic thermodynamics and the trajectory-level definition of heat

The Bérut measurement of ⟨*Q*_diss⟩ is a trajectory-averaged quantity
computed via Sekimoto's stochastic-energetics prescription: along each
trajectory the heat is *Q* = ∫ (γ ẋ − *F*_ext) ẋ d*t*, where *F*_ext is the
conservative force from the time-dependent trap and γ is the drag
coefficient. This definition, introduced by Sekimoto (1998) and lifted into
the modern stochastic-thermodynamics framework by Seifert (2005, 2012), is
the object whose ensemble mean the Proesmans formula predicts. Crooks (1999)
derives the detailed fluctuation theorem relating forward and reverse-path
probabilities in terms of entropy production; Jarzynski (1997) establishes the
corresponding integral theorem relating nonequilibrium-work averages to
free-energy differences. These three equalities — Sekimoto, Crooks,
Jarzynski — make trajectory-level dissipation a measurable,
unambiguous quantity, and they underpin the published Bérut bootstrap error
bars.

Ritort's reviews (2003, 2008) and Jarzynski's Annual Review article (2011)
provide the secondary-source account for non-specialists. Seifert's 2012
*Rep. Prog. Phys.* review is the canonical reference. Van den Broeck and
Esposito (2015) give a compact primer bridging the ensemble and trajectory
formulations of the second law, which is necessary for interpreting the
Bérut error bars — they are bootstrap confidence intervals on the
ensemble mean of Q, not on individual-trajectory work.

Important parallel streams include: Esposito and Van den Broeck's
decomposition of entropy production into adiabatic and non-adiabatic pieces
(2010, 2011), which identifies the Bérut excess heat cleanly as the
non-adiabatic piece; Kawai, Parrondo and Van den Broeck (2007) on the
phase-space Kullback–Leibler representation of dissipation; Still, Sivak,
Bell and Crooks (2012) on the link between dissipation and
non-predictive information. Together these provide multiple, equivalent
ways of writing the theoretical object we are fitting, each of which
produces the same π² coefficient when the protocol is optimal.

### 1.3 The finite-time coefficient B: three routes to π²

The finite-time excess heat B *k*_B *T* / τ appeared in several contexts
before Proesmans et al. consolidated the result. The three main
derivation routes are:

**Optimal-transport route** (Aurell, Mejía-Monasterio and
Muratore-Ginanneschi 2011; Aurell, Gawedzki, Mejía-Monasterio, Mohayaee and
Muratore-Ginanneschi 2012). For overdamped Langevin dynamics in 1D, the
minimum dissipation of a finite-time transition between two equilibrium
distributions p_0 and p_τ is given by the squared 2-Wasserstein distance
W_2²(p_0, p_τ) divided by τ. For the symmetric erasure (two equally
populated wells → one populated well) the computation gives exactly
W_2² = π² (*k*_B *T* / γ) × (well separation)² in the small-separation
limit, producing B = π² after restoring units. This route was sharpened by
Aurell (2023) and by Nakazato and Ito (2021) who reformulated entropy
production as a Wasserstein geometric object.

**Thermodynamic-length / friction-tensor route** (Sivak and Crooks 2012;
Zulkowski and DeWeese 2014). The friction tensor that controls the linear-
response dissipation induces a Riemannian metric on the space of
thermodynamic states. The minimum dissipation of a finite-time protocol
connecting two states is bounded below by the squared thermodynamic length
(geodesic distance) divided by τ. For symmetric-erasure in a double well
the geodesic-distance-squared gives exactly π² (*k*_B *T*)² up to the
Hellinger-distance correction derived by Zulkowski and DeWeese.

**Pontryagin / direct optimal-control route** (Schmiedl and Seifert 2007;
Muratore-Ginanneschi 2013; Muratore-Ginanneschi and Schwieger 2017). Apply
Pontryagin's maximum principle to the Langevin-Kramers equation with
boundary conditions p_0 and p_τ and a cost functional given by the
time-integrated dissipation. The resulting Euler-Lagrange equations yield
jump-discontinuous optimal protocols at τ = 0 and τ = τ_end, and
integrating the dissipation along the optimal trajectory recovers
B = π². This is the route Proesmans et al. (2020) use, and it has the
advantage that the protocol is constructible — it is the one any experiment
should implement to saturate the bound.

Each of these three derivations arrives at the same coefficient B = π². All
three assume a symmetric double well. Proesmans, Ehrich and Bechhoefer
(2020 PRL) explicitly frame their result for Bérut's apparatus:
"over-damped, symmetric, barrier-raised-then-tilted" — and discuss at
length the regime in which the Bérut experiment should saturate the
bound.

### 1.4 Competing and tighter finite-time bounds

After Proesmans et al., several papers have proposed tighter or
alternative bounds. Zhen, Egloff, Modi and Dahlsten (2021) derive a
universal bound that is tighter than B = π² in some regimes. Van Vu and
Saito (2022, *PRL* 129) use a geometric-speed-limit approach to produce a
*tight* finite-time Landauer bound that reduces to a protocol-dependent
coefficient. Van Vu and Saito (2022, *PRL* 128) extend to quantum
systems, with a classical limit that must reduce to the Proesmans
prediction. Lee, Park and Park (2022) derive speed limits for highly
irreversible processes. Machta (2015) gives a single-protocol bound that
sits between Schmiedl–Seifert and Proesmans.

The key point for the refit is that these competing bounds make *different
numerical* predictions in different regimes. The Bérut dataset sits in a
regime where Proesmans' π² is the leading prediction; the tighter bounds
typically match π² at the protocols used in Bérut, but they diverge at
short τ where Bérut's error bars are largest. A careful refit of the ten
points needs to acknowledge that the "prediction under test" is a family
of near-π² coefficients, not a single number — although all reduce to π²
in the regime where Bérut's experiment is cleanest.

### 1.5 Feedback, information, and the broader landscape

Sagawa and Ueda (2010, 2012) establish generalised Jarzynski equalities
that include feedback-acquired mutual information. Parrondo, Horowitz and
Sagawa (2015, *Nat. Phys.*) consolidate the field in a widely-cited
review; Wolpert (2019) extends the picture to circuit-level
computation. These papers are relevant for positioning the Bérut refit in
the broader information-thermodynamics programme, but they do not change
the prediction under test: the Bérut protocol is feed-*forward* (no
state-dependent control), so the feedback-corrected bounds reduce to
the Proesmans bound.

Modern re-derivations of Landauer and finite-time extensions include Faist
and Renner (2018), Faist et al. (2015), Riechers, Boyd, Wimsatt and
Crutchfield (2020), and Boyd, Mandal and Crutchfield (2018, *PRX*). These
produce single-shot, circuit-level and error-tradeoff bounds that are not
directly applicable to the Bérut average but which could motivate a
second-generation experiment.

The experimental landscape of Landauer-related tests has grown
substantially. Toyabe, Sagawa, Ueda, Muneyuki and Sano (2010) first
demonstrated information-to-energy conversion in an optical-trap apparatus;
Bérut et al. (2012) provided the first direct verification of the
Landauer *bound* on the erasure side; Jun, Gavrilov and Bechhoefer (2014)
provided the first feedback-trap Landauer verification with tighter error
bars; Hong, Lambson, Dhuey and Bokor (2016) did a nanomagnetic
implementation at ~1.0 *k*_B *T* ln 2; Gaudenzi et al. (2018) performed a
quantum implementation. Koski et al. (2014, 2015) did the single-electron
single-box analog, Yan et al. (2018, 2021) did a single-atom analog, and
Dago et al. (2021, 2022) brought the underdamped case within 1% of the
bound. The diversity of these experiments is itself evidence that Landauer
holds, but the only one of them that publishes a ten-point
τ-dependence of ⟨*Q*_diss⟩ at fixed apparatus is Bérut 2012.

### 1.6 Identifiability, uncertainty relations, and power analysis

Barato and Seifert's 2015 thermodynamic uncertainty relation (TUR)
constrains the variance-dissipation tradeoff for any stochastic process.
Horowitz and Gingrich's 2020 *Nat. Phys.* review consolidates the TUR
literature. For the Bérut refit the TUR provides an independent lower
bound on the Q-histogram width at each τ, against which the published
error bars can be compared; if Bérut's bars are tighter than the TUR
allows, they must be error-underestimates, and the refit CI needs
correspondingly inflated.

Shiraishi, Funo and Saito (2018) derived the speed-limit form of the
TUR; Lee, Park and Park (2019) developed the TUR–speed-limit unification.
Dechant and Sasa (2020) on fluctuation-response inequalities, and Landi
and Paternostro (2021, *Rev. Mod. Phys.*) in their review of irreversible
entropy production, provide further constraints that a careful refit
should respect.

### 1.7 Fluctuation theorems and their experimental verification

Crooks' 1999 fluctuation theorem is the backbone of how we measure heat and
work at the trajectory level. For an overdamped particle driven by a
time-dependent conservative force, the ratio of forward and backward
trajectory probabilities equals exp(−W/kT) where W is the work done.
Collin, Ritort, Jarzynski, Smith, Tinoco and Bustamante (2005, *Nature*)
provided the first direct verification in a molecular-biology context
using optical tweezers on an RNA hairpin; Liphardt et al. (2002, *Science*)
did the Jarzynski-equality verification on the same apparatus family.
Carberry, Reid, Wang, Sevick, Searles and Evans (2004, *PRL*) provided the
transient fluctuation theorem verification in an optical trap. These
experiments are the immediate precursors to Bérut's apparatus and
methodology, and they establish that the trajectory-level stochastic
energetics is both theoretically sound and experimentally realisable.

Extensions of the Crooks framework to account for feedback-controlled
processes appear in Sagawa and Ueda (2010, 2012) and Horowitz and Parrondo
(2011). Van Zon and Cohen (2003) extended the fluctuation theorem to
systems where the work distribution has extended tails. Kwon, Noh and Park
(2011) treat the work/heat distribution in linearly driven overdamped
systems, which is precisely the baseline regime the Bérut cycle sits in
during the hold and ramp segments.

Campisi, Hänggi and Talkner (2011, *Rev. Mod. Phys.*) provide the quantum
FT review; Esposito, Harbola and Mukamel (2009, *Rev. Mod. Phys.*) on
nonequilibrium fluctuations in quantum systems is the quantum-counting
companion. Harris and Schütz (2007) provide the stochastic-dynamics FT
review. Manzano, Fazio and Roldán (2019, *PRL*) give a martingale-theoretic
view of entropy production, providing tail-bound tools applicable to
Bérut's heat histogram.

### 1.8 Power analysis and falsifiability

The scope check flags that ten data points cannot distinguish π² from
π²(1+r)²/(4r) at realistic *r* unless *r* is far from 1 and σ_B is small.
The literature provides two tools for this power analysis:

**TUR-inspired lower bounds on σ_B.** The Barato–Seifert TUR (2015) bounds
the variance of the time-integrated current (here, the heat) by 2/(<Q>·ΔS).
For the Bérut cycle this produces a floor on the minimum achievable σ_B at
each τ; if the published Bérut error bars are tighter than this floor, they
are error underestimates and the refit CI must be inflated.

**Identifiability under the asymmetric model.** For a two-parameter fit
(B, r) against ten data points, standard Fisher-information analysis
(Machta, Chachra, Transtrum and Sethna 2013) gives conditions under which
*r* and *B* become collinear — i.e., the fit cannot distinguish a
symmetric prediction with slightly offset B from an asymmetric prediction
with B = π². The Machta et al. 2013 parameter-space compression framework
is the principled way to ask "how identifiable is r from ten points?".

**Reviewer-friendly robustness checks.** Miller, Scandi, Anders and
Perarnau-Llobet (2019) give the slow-process limit of work fluctuations;
Scandi and Perarnau-Llobet (2019) extend thermodynamic length to open
quantum systems. These provide alternative functional forms for the
⟨Q_diss⟩(τ) curve that can be fit alongside the leading 1/τ term, checking
whether a small second-order 1/τ² correction is present in the Bérut data
and whether ignoring it biases B.

### 1.9 Textbooks and pedagogical references for Theme 1

Peliti and Pigolotti (2021, Princeton) is the modern stochastic-thermo
textbook. Sekimoto (2010) is the canonical stochastic-energetics
treatment. Van Kampen (2007), Risken (1989), and Gardiner (2009) are the
standard Fokker-Planck and stochastic-process references that underpin
the theory. For the information-theoretic side, Cover and Thomas' textbook
(not cited here but standard) and Parrondo, Horowitz and Sagawa's 2015
*Nat. Phys.* review are the canonical resources. Wolpert (2019, *J.
Phys. A*) is the modern review of stochastic thermodynamics of
computation, extending beyond Bérut to full circuits. Landi and
Paternostro (2021, *Rev. Mod. Phys.*) on irreversible entropy production
provides the broad context.

### 1.10 What the literature does not settle

Three important questions remain unsettled in the literature and are
live for the Bérut refit:

1. **Does Bérut's experiment meet the optimal-protocol assumption that
   B = π² requires?** Proesmans' derivation assumes the protocol saturates
   the bound. Bérut's protocol is not the Schmiedl–Seifert optimal
   one; it is the cleanest implementable double-well erasure. No published
   calculation shows what *B* the Bérut protocol actually realises. A
   plausible hypothesis is that the Bérut protocol realises a B larger
   than π² by a constant prefactor of order unity.
2. **Is the well-depth asymmetry small enough that the symmetric prediction
   applies?** Bérut reports stiffness parameters but not a clean V_left /
   V_right ratio; the asymmetric prediction B(r) = π²(1+r)²/(4r) is the
   candidate generalisation. If *r* is extractable, we can test either
   prediction; if not, the asymmetric test is inconclusive.
3. **Do the published Bérut error bars adequately propagate the
   measurement uncertainty?** Scope check (ii) flags this: the error bars
   are known to be optimistic. Any refit has to either widen the CI or
   make an explicit case for trusting them. Tools: TUR floors on σ_Q,
   parametric-vs-nonparametric bootstrap comparison.

---

## Theme 2 — Colloidal bit-erasure experiments and optical-trap physics

### 2.1 Optical trapping: apparatus foundations

The Bérut apparatus is a single-beam gradient optical trap operating on a
silica bead in water. The apparatus derives from Ashkin's 1970 PRL
demonstration of radiation-pressure trapping and the 1986 Ashkin, Dziedzic,
Bjorkholm and Chu *Opt. Lett.* paper establishing the single-beam gradient
configuration. Ashkin's 1997 PNAS review and his 2000 IEEE history
paper consolidate the physics. Neuman and Block's 2004 *Rev. Sci.
Instrum.* review is the canonical apparatus reference; Gieseler et al.
(2021, *Adv. Opt. Photonics*) is the modern tutorial, including
calibration and potential-reconstruction recipes that are directly
relevant to extracting *r* from Bérut's data.

The Bérut double-well configuration is a two-beam construction in which two
foci are placed at an adjustable separation, producing a bistable
potential for the trapped bead. This apparatus family is described in
Visscher, Gross and Block (1996), Bustamante, Chemla and Moffitt (2008),
Moffitt, Chemla, Smith and Bustamante (2008), and Greenleaf, Woodside and
Block (2007). The Grier 2003 *Nature* review and Jones, Maragò and Volpe
(2015 textbook) are the standard apparatus references.

### 2.2 Calibration and potential reconstruction

Three methods are used to extract trap stiffness and potential shape:

**Power-spectrum (PSD) analysis.** Berg-Sørensen and Flyvbjerg (2004)
established the gold-standard method of fitting a Lorentzian to the power
spectrum of the bead's Brownian motion. For a harmonic trap the Lorentzian
cutoff frequency gives the stiffness κ directly. The method was implemented
in the *tweezercalib* MATLAB package (Tolić-Nørrelykke, Berg-Sørensen and
Flyvbjerg 2004; Hansen, Tolić-Nørrelykke, Flyvbjerg and Berg-Sørensen 2006),
which is the software Bérut et al. use. The systematic corrections are
large and well-documented: frequency-dependent drag (Wang and Uhlenbeck 1945;
Berg-Sørensen and Flyvbjerg 2004), photodiode aliasing, and hydrodynamic
coupling to the cover slip.

**Boltzmann-histogram (thermal-noise) method.** Florin, Pralle, Stelzer and
Hörber (1998) introduced the method of reconstructing *U*(*x*) from the
Boltzmann-weighted histogram of the bead's equilibrium positions:
*U*(*x*) = −*k*_B *T* ln *P*_eq(*x*) + const. This method gives the *full
potential shape* without assuming harmonicity, and is the natural method for
extracting the well-depth asymmetry ratio *r* from a double-well trap. A
variant (Selmke, Khadem and Cichos 2018) handles non-harmonic potentials.
Gieseler et al. (2021) describe the Bayesian refinements; Banerjee et al.
(2022) give the Bayesian calibration for optical traps. Richly, Zindrou
and Moerner (2022) is the most recent methodological paper on reconstructing
asymmetric potentials from driven noise.

**Driven-response (Stokes-drag) calibration.** Pesce, Volpe, De Luca,
Rusciano and Volpe (2009) measure the trap's response to a known
fluid-flow force. This is the most robust method because it is
calibration-free (the viscosity of water is known), but it requires a
flow stage and is used less commonly. Rohrbach (2005) provides the EM-theory
comparison.

Bérut et al. use a combination of PSD and Boltzmann-histogram methods. The
well-depth asymmetry *r* = V_left / V_right is in principle extractable from
the Boltzmann histogram in the bistable regime, but the 2012 supplement
reports only stiffness and well-separation values, not a fitted asymmetric
double-well form. Our r-identifiability leg needs to back-reconstruct
*r* from the stiffness, separation, and any published histograms.

### 2.3 Stochastic thermodynamics in optical traps

The use of optical traps to test fluctuation theorems is a mature
subfield. Wang, Sevick, Mittag, Searles and Evans (2002, *PRL*) did the
first demonstration of FT violations in an optical trap; Carberry, Reid,
Wang, Sevick, Searles and Evans (2004, *PRL*) did the TFT; Liphardt,
Dumont, Smith, Tinoco and Bustamante (2002, *Science*) did the first
Jarzynski test with an optical tweezer on a biomolecule. The Ciliberto
group's contributions — Douarche, Ciliberto, Petrosyan and Rabbiosi
(2005); Douarche, Joubaud, Garnier, Petrosyan and Ciliberto (2006); Joubaud,
Garnier and Ciliberto (2007) — developed the apparatus that Bérut
inherited.

Optical-trap heat engines and information engines constitute a related
experimental stream. Blickle and Bechinger (2012) built a micrometre Stirling
engine; Martinez, Roldán, Dinis, Petrov, Parrondo and Rica (2016) built an
optical-trap Carnot engine. Roldán, Martinez, Parrondo and Petrov (2014,
*Nat. Phys.*) showed universal features in symmetry-breaking energetics —
the closest existing analog to Bérut's double-well cycle. Paneru, Lee,
Tlusty and Pak (2018, *PRL*) demonstrated a lossless Brownian information
engine. Saha, Lucero, Ehrich, Sivak and Bechhoefer (2021, *PNAS*) maximised
power of an information engine. Ribezzi-Crivellari and Ritort (2019, *Nat.
Phys.*) built a continuous Maxwell demon reaching the Landauer bound.

Engineered swift equilibration is a protocol-level methodological advance
directly relevant to re-running Bérut. Martinez, Petrosyan, Guery-Odelin,
Trizac and Ciliberto (2016) introduced ESE in a Brownian particle, reducing
relaxation times by a factor of 100. Chupeau, Besga, Guery-Odelin, Trizac,
Petrosyan and Ciliberto (2018) developed thermal-bath engineering for ESE.
Proesmans and Bechhoefer (2019) derived optimal ESE protocols — this is
the protocol family that saturates the Schmiedl-Seifert / Proesmans bound
and hence the one that a re-run Bérut experiment would use.

### 2.4 The Bérut apparatus family: Ciliberto-group publications

The Bérut 2012 Nature paper is supplemented by several longer Ciliberto-group
papers: Bérut, Petrosyan and Ciliberto (2013, 2015) on the Jarzynski
equality applied to the erasure cycle; Bérut, Imparato, Petrosyan and
Ciliberto (2014, 2015) on multi-particle heat flux; Bérut, Petrosyan and
Ciliberto (2015, *J. Stat. Mech.*) as the long-form expansion of the Nature
paper. The apparatus publications include Petrov, Tarkanyi, Banyasz and
Ciliberto (2006) on single-beam optical traps and later papers on dual-beam
constructions.

Dago's follow-up programme (Dago, Pereda, Barros, Ciliberto and Bellon 2021;
Dago, Pereda, Ciliberto and Bellon 2022; Dago, Ciliberto and Bellon 2022) is
the closest modern comparator: a virtual double-well potential for an
underdamped micromechanical oscillator, used to test Landauer at fast
protocols (100 ms) with 1% precision. Dago's apparatus is different from
Bérut's — underdamped vs overdamped, feedback-virtual well vs physical
two-foci, silicon cantilever vs silica bead in water — so it is a
comparator but not a substitute.

Goerlich, Rosales-Cabara, Zindrou, Richly, Genet and Moerner (2023, *Nat.
Commun.*) is a very recent non-Markovian erasure paper. Goerlich,
Rosales-Cabara and Ciliberto (2022, *Phys. Rev. Res.*) test Landauer's
principle for stochastic memories with non-equilibrium initial conditions —
directly relevant for discussing whether Bérut's initial-state preparation
is truly equilibrium.

### 2.5 Potential reconstruction for the asymmetric case

For the symmetric Bérut case *r* = 1, the potential is a symmetric quartic
with equal well depths. The asymmetric extension is *V*(*x*) = *a*x^4 −
*b*x² + *c*x, where the linear tilt produces *r* = V_left / V_right. Given
measured stiffnesses at the minima κ_left, κ_right and a measured
inter-well separation Δ, the curvature ratio κ_left / κ_right and the
depth ratio *r* are related — but not identical. Without a histogram in
the bistable regime long enough to sample both wells, *r* is only
*indirectly* constrained. Bakhtiari, Esposito and Lindenberg (2015) work
out the Kramers escape rate in asymmetric double wells, giving an
independent handle: if two Kramers rates can be measured, the depth
asymmetry follows.

Relevant methodology papers for this identifiability step: Raju and
Bechhoefer (2021) on Bayesian inference of optical-trap stiffness and
diffusion; Frishman and Ronceray (2020) on learning force fields from
trajectories; Ronceray, Broedersz and Lenz (2022) on learning stochastic
dynamics from data. Wu, Zhang and Wu (2022) is the most recent
methodological paper on dynamically controlled double-well optical
potentials, and is the single closest reference to Bérut's apparatus in the
last five years.

### 2.6 Cross-substrate comparisons

Bérut's result is one of five experimental implementations of Landauer's
bound, each with different sources of systematic error:

- **Colloid in a double-well optical trap** (Bérut 2012; Dago 2021/2022).
  Systematics: drag calibration, photodiode linearity, well-depth
  asymmetry.
- **Feedback-trap colloidal** (Jun, Gavrilov, Bechhoefer 2014; Gavrilov and
  Bechhoefer 2016; Saha et al. 2021). Systematics: feedback loop delay,
  virtual-potential fidelity. Zhou and Bechhoefer 2020 on feedback-loop
  artefact analysis.
- **Nanomagnetic** (Hong, Lambson, Dhuey and Bokor 2016). Systematics:
  magnetic-field calibration, switching-energy inference.
- **Single-electron** (Koski et al. 2014, 2015; Pekola 2015). Systematics:
  gate-voltage drift, thermometry.
- **Single-atom** (Yan et al. 2018, 2021). Systematics: quantum-state
  preparation fidelity.

The Bérut dataset is the one with the cleanest τ-dependence published, so it
remains the natural target for a refit of the Proesmans formula.

### 2.7 Textbooks and pedagogical references

The canonical stochastic-thermodynamics textbooks are Peliti and Pigolotti
(2021), Sekimoto (2010), Van Kampen (2007), Risken (1989), Gardiner (2009),
and Coffey and Kalmykov (2017). For optical tweezers, Jones, Maragò and
Volpe (2015) is the modern textbook; Neuman and Block (2004) and Gieseler
et al. (2021) are the comprehensive reviews. Bechhoefer (2005 *Rev. Mod.
Phys.*) on feedback for physicists is the standard apparatus-control
reference. Efron and Tibshirani (1994) is the canonical bootstrap
reference needed for the refit's CI construction; Novak (2012) covers
extreme-value methods needed if the published Bérut error bars prove
under-propagated.

### 2.8 Hydrodynamic and thermal systematics

For a colloidal bead in water, the drag coefficient γ appearing in the
Langevin equation is not the Stokes drag 6πηa alone; hydrodynamic
coupling to the cover-slip wall raises γ by a distance-dependent factor
(Florin, Pralle, Stelzer and Hörber 1998). Berg-Sørensen and Flyvbjerg
(2004, RSI) catalogue these corrections for the PSD calibration;
Ermak and McCammon (1978) established the hydrodynamic-interaction
Brownian-dynamics scheme. Iniguez and Pleimling (2022) give a recent
treatment of hydrodynamic interactions in driven colloidal systems.

Beyond drag, the bath temperature is effectively set by the laser
heating as well as the ambient temperature. Rings, Selmke, Cichos and
Kroy (2011) and Falasco, Gnann, Rings and Kroy (2014) provide the
"hot-Brownian-motion" framework for distinguishing true bath
temperature from effective temperature felt by the bead. For Bérut's
apparatus the effective-T correction is typically small, but it
propagates into the translation between *U*(x) (measured in units of
*k*_B *T*) and V_depth (measured in joules) and so into *r*.

### 2.9 Numerical simulation of the Bérut apparatus

Validating the refit against simulated data is an essential TDD step.
Volpe and Volpe (2013, *Am. J. Phys.*) give the canonical
Brownian-dynamics simulation recipe for a particle in an optical trap.
Ermak and McCammon (1978) established the simulation algorithm.
Gieseler et al. (2021) include simulation code in their tutorial.
With a simulator in hand we can (i) generate synthetic Bérut-like data
at known ground truth *B* and *r*, (ii) run the refit on it, (iii)
confirm that the refit recovers ground truth, and (iv) estimate the
power of the test under realistic noise. This is the methodology that
turns the proposal's ten-point fit into a credible publication-grade
analysis.

### 2.10 Modern benchmarks: Dago, Proesmans-Bechhoefer, Ciliberto

Dago, Pereda, Barros, Ciliberto and Bellon (2021, *PRL*) achieved the
Landauer bound at 1% precision in an underdamped micromechanical
oscillator; Dago, Pereda, Ciliberto and Bellon (2022, *PRL*) extended
the analysis to fast processes and quantified the separation of
dissipation into overdamped and underdamped contributions. Dago,
Ciliberto and Bellon (2022, *J. Stat. Mech.*) is the methodology paper
for the virtual-double-well apparatus. These papers are the modern
gold-standard experiments to which Bérut 2012 is compared.

Proesmans and Bechhoefer (2019, *PRE*) derived the optimal ESE
protocols that saturate the π² bound. Wadhia, Proesmans and Bechhoefer
(2024, *PRE*) derive universally optimal cooling protocols, extending
the framework. Blaber and Sivak (2020, 2023) extend to skewed
geometries and beyond linear response. Kumar and Bechhoefer (2020,
*Nature*) demonstrate exponentially faster cooling; Bechhoefer's
feedback-control textbook chapter (2005, *RMP*) is the apparatus-
level foundation.

### 2.11 What the optical-trap literature does not settle

Two issues remain active:

1. **Absolute calibration.** Even with modern PSD methods the trap
   stiffness has a residual 5–10% systematic uncertainty due to drag
   calibration, bead-size polydispersity, and beam-aberration. The Bérut
   stiffness value therefore carries an error bar that propagates into
   the κ-derived *r*. Banerjee et al. (2022) and Raju and Bechhoefer
   (2021) describe Bayesian calibration methods that reduce this to 1–2%
   but require re-running the experiment.
2. **Well-depth asymmetry in published datasets.** Most published double-
   well optical-trap experiments report stiffness at each well separately
   but rarely report a clean fitted *V*(*x*) with asymmetric depths. The
   Bérut supplement is typical in this respect, and the project's
   r-identifiability task is not solved in the literature — it must be
   done *ab initio*. The techniques we will draw on: Boltzmann-histogram
   reconstruction in the bistable regime (Florin, Pralle, Stelzer and Hörber
   1998), driven-noise asymmetric-potential fitting (Richly, Zindrou and
   Moerner 2022), and Kramers escape-rate asymmetry (Bakhtiari, Esposito
   and Lindenberg 2015).

---

## Synthesis

The two themes together tell a coherent story for the Bérut refit:

- **Theme 1** gives us the prediction B = π² under three independent
  derivation routes (optimal transport, thermodynamic length, Pontryagin
  optimal control), plus a family of tighter alternative bounds in Van Vu &
  Saito and Zhen et al., and the asymmetric generalisation B(r) = π²(1+r)²/(4r)
  that is the genuinely new piece of our refit.
- **Theme 2** gives us the apparatus (colloid in a double-well optical
  trap), the calibration methodology (PSD plus Boltzmann histogram), and
  the cross-substrate context (four other experimental implementations that
  do not publish τ-dependence).

The refit is a well-posed problem: given the Bérut ten points, we fit
*k*_B *T* ln 2 + B *k*_B *T* / τ; the CI on B is computable by bootstrap; the
symmetric test is whether π² is in that CI; the asymmetric test is whether
B(r) for Bérut-extracted *r* is in the CI. The weak joint, as flagged by the
scope check, is whether *r* is extractable at useful precision from the
published supplement — and the literature reviewed here (Florin et al.
1998; Gieseler et al. 2021; Banerjee et al. 2022; Raju and Bechhoefer 2021;
Bakhtiari, Esposito and Lindenberg 2015) makes clear that the answer depends
on whether the published histograms sample both wells sufficiently. If they
do, *r* can be extracted to ~10%; if they do not, the asymmetric test is
inconclusive and the project's honest pre-registration is that we report the
null.
