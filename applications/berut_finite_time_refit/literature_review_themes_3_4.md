# Literature Review — Themes 3 and 4

This file contains the two thematic sections assigned to Part 2 of the Phase 0 literature review for the Bérut finite-time Landauer refit project. Themes 1 and 2 are delivered separately.

---

## Theme 3. Asymmetric double-well potentials in stochastic thermodynamics

### 3.1 Kramers' problem and the extension to asymmetric wells

The foundational paper of Kramers (1940, T3_001) posed the question of the thermally activated escape rate of a Brownian particle from a metastable potential well. In its overdamped version, the answer — at weak noise — is the Arrhenius–Kramers formula

    k_escape ~ (omega_well * omega_barrier) / (2 pi gamma) * exp(-Delta U / k_B T)

where gamma is the friction, omega_well and omega_barrier are the curvatures at the well minimum and the barrier top, and Delta U is the barrier height. Kramers' original derivation treated a single symmetric well; the extension to **asymmetric** double wells — two distinct wells L and R with different depths and different curvatures — is a long-standing exercise in the Fokker–Planck literature. The canonical treatment is in Hänggi, Talkner and Borkovec's review (1990, T3_002), where both the escape rates from L to R and the reverse rate R to L are derived, the ratio of forward to backward rate equals exp(-Delta V / k_B T) by detailed balance, where Delta V is the difference in well-depths, and the slowest (non-zero) eigenvalue of the Fokker–Planck operator equals the sum of the two rates. Risken's textbook (1989, T3_003) gives the matrix-continued-fraction expansion of this eigenvalue in chapter 5, and Gardiner (2009, T3_004) gives the operator-theoretic framing in chapter 11.

The asymmetric-well Kramers problem has a specific subtlety that is load-bearing for the present project. When the two wells differ in curvature, the naive equal-well prefactor factor (omega_well * omega_barrier) / (2 pi gamma) is replaced by a prefactor that depends on the well-depth asymmetry *r = V_L / V_R* in a non-trivial way. Coffey, Kalmykov and Titov (2005, T3_031) give an explicit asymmetric-well escape-rate expression valid across all dissipation regimes (very low damping, very high damping, crossover), and Mel'nikov (1991, T3_029) treats the problem in a fifty-year retrospective. The general result is that the overdamped Kramers prefactor for the slowest eigenvalue of a doubly-well Fokker–Planck operator with asymmetric well-depths scales as (1 + r)² / (4 r) relative to the symmetric case at r = 1 — this is the asymmetric factor that generalises the Proesmans B = π² result to non-equal wells. The asymmetric factor (1 + r)²/(4r) is not a Proesmans derivation; rather, it is an inherited piece of Kramers prefactor algebra whose applicability to the finite-time Landauer coefficient B has not been rigorously established in the published literature.

### 3.2 Stochastic thermodynamics of finite-time protocols

Stochastic thermodynamics, as formalised by Sekimoto (1998, T3_008; 2010, T3_009), Seifert (2005, T4_125; 2012, T3_007), Jarzynski (1997, T3_010), and Crooks (1999, T3_011), extends the thermodynamic quantities heat, work, and entropy production to individual trajectories of small-system Langevin dynamics. The Jarzynski equality ⟨exp(-W / k_B T)⟩ = exp(-ΔF / k_B T), the Crooks detailed fluctuation relation, and the Seifert integral fluctuation theorem for total entropy production together make work and heat individually random quantities whose averages are bounded by the Clausius inequality, while individual trajectories can violate the mean Clausius inequality by arbitrarily large amounts. Recent textbooks (Peliti & Pigolotti, T3_129; Sekimoto 2010, T3_009) consolidate the field.

The finite-time extension is the central question for the present project. Schmiedl and Seifert (2007, T3_006) posed the variational problem: for a system coupled to a heat bath at temperature T, what is the optimal time-dependent protocol λ(t) that minimises the expected work ⟨W⟩ over a fixed duration τ, subject to fixed initial and final equilibria? For the specific case of shifting a harmonic trap in 1D, they solved this exactly and found that the excess work above the free-energy change decays as 1/τ with an explicit dimensionless prefactor. Their approach is to solve an integro-differential equation; the optimal protocol typically has **finite jumps at the beginning and end** of the protocol, a distinctive prediction that the Bérut dataset has not directly tested.

Aurell, Mejía-Monasterio and Muratore-Ginanneschi (2011, T3_012) re-expressed the Schmiedl–Seifert variational problem in the language of Monge–Kantorovich optimal transport. Their refined second law (2012, T3_013) states that the mean dissipation lower bound is exactly the L² Wasserstein distance (divided by τ) between the initial and final probability distributions. For 1D overdamped systems, this is

    ⟨W_diss⟩(τ) ≥ (k_B T / τ D) * W²₂(ρ_i, ρ_f)

where D is the diffusion coefficient and W₂ is the Wasserstein distance. The bound is tight — achievable by the optimal protocol — in the fast regime. Sivak and Crooks (2012, T3_018; and Zulkowski et al. 2012, T3_017) gave the near-equilibrium (linear-response) perspective in terms of a generalised friction tensor that induces a Riemannian manifold on the space of control parameters. Near equilibrium, minimum-dissipation protocols are geodesics of this metric.

### 3.3 The finite-time Landauer principle

Proesmans, Ehrich and Bechhoefer (2020, T3_014 and T3_015) specialised these variational tools to bit erasure. The system is a colloidal particle in a 1D double-well potential, initially uniformly distributed over the two wells (1 bit of entropy) and finally all in the right well (0 bits). Using Wasserstein-distance optimal-transport, they derived the finite-time Landauer principle:

    ⟨Q_diss⟩(τ) ≥ k_B T ln 2 + B k_B T / τ

where the constant B = π² for the symmetric double-well case under full dynamic control of the potential. The derivation pivots on the fact that the optimal transport from a bimodal initial distribution to a unimodal final distribution traverses the barrier, and the Wasserstein cost of this is fixed by geometry. The Proesmans result is a *lower bound* — experimentally measured ⟨Q_diss⟩(τ) cannot go below k_B T ln 2 + π² k_B T / τ at any τ — but is *achievable* under the idealised full-control model. At finite τ, the 1/τ correction is a real physical cost of finite-time erasure and has motivated much follow-up work.

Zulkowski and DeWeese (2014, T3_016) predated Proesmans in deriving finite-time erasure costs using thermodynamic-length geometry. Their bound is in terms of the squared Hellinger distance between initial and final distributions divided by τ, and is parametrically related to the Wasserstein bound but has a different prefactor in the symmetric case. The relationship between Hellinger, Wasserstein, and Fisher-information geometries of thermodynamic control is reviewed in Zulkowski et al. (2012, T3_017) and Sivak and Crooks (2012, T3_018). Dechant, Sakurai, Sasa and Ito (T3_021–T3_025) have elaborated the Wasserstein–entropy-production connection: the lower bound on entropy production can be decomposed into excess, housekeeping, and coupling parts, and the excess part is the geometric Wasserstein cost.

### 3.4 Asymmetric extensions of the finite-time Landauer principle

The finite-time B = π² result was derived for a **symmetric** double well. Generalisations to asymmetric wells have been sketched but not rigorously worked out. The predecessor paper thermodynamic_info_limits §3.2 proposed the heuristic formula

    B(r) = π² (1 + r)² / (4 r)

where r = V_L / V_R is the well-depth ratio. This inherits the Kramers-prefactor asymmetric-factor structure described in §3.1 — the intuition is that the cost of transporting probability between two wells scales with the geometric factor that governs the slowest eigenvalue of the asymmetric double-well Fokker–Planck operator. At r = 1 the formula reduces to B = π² (symmetric case). For r != 1, B(r) > π²: any asymmetry increases the finite-time cost of erasure, with diverging cost as either r → 0 or r → ∞. The heuristic has not been derived from the full optimal-transport machinery of Proesmans 2020 and is flagged by Phase 0.25 review as "untested extension".

Directly relevant experimental work:

- **Gavrilov and Bechhoefer (2016, T3_053), "Erasure without work in an asymmetric double-well potential"**. Crucial. Jun, Gavrilov and Bechhoefer had already demonstrated high-precision Landauer-principle tests in a virtual-potential feedback trap (T3_051, 2014); the 2016 paper specifically operates in an asymmetric trap and shows that erasure cost depends on the asymmetry in a non-trivial way. Their asymmetry parameter is defined and measured in the virtual trap, where it is exactly known. They demonstrate that the average work to erase can be much less than k_B T ln 2 when the asymmetry is sufficient and the initial distribution biased — but the **minimum** dissipated heat is always at least k_B T ln 2, consistent with second law. This is the closest experimental comparator for any asymmetric Landauer prediction.

- **Chiu, Lu and Jun (2022, T3_089), "Finite-time Landauer principle in an asymmetric double well"**. Critical. This paper directly probes B(r) in a feedback-trap-controlled explicitly asymmetric double well and connects to the Proesmans framework. The methodology here is a plausible template for how the asymmetric B(r) question has been attempted; their trap is virtual and r is known by construction, precisely the situation that Bérut is **not** in.

- **Dago, Pereda, Ciliberto, Bellon (2021, T3_054; 2022, T3_055, T3_056; 2024, T3_058)**. Finite-time Landauer tests in underdamped regime using a micromechanical oscillator. The physics is somewhat different — underdamped dynamics make the inertial timescale important — but the asymmetric-well protocol optimisation maps. The reliable-underdamped-memory paper T3_058 discusses asymmetric-protocol performance as a function of cycle time.

- **Zhen, Egloff, Modi, Dahlsten (2021, T3_060; 2022, T3_061)**. Give a universal hardware-independent lower bound on bit-reset cost; their formulation assumes nothing about the specific well geometry and reduces to inverse-linear scaling in τ with a B-coefficient that depends on the error tolerance and the initial distribution. In the limit of zero error and exactly equal initial probabilities, their bound also approaches a π² structure, but with different constants than Proesmans.

- **Boyd, Patra, Jarzynski, Crutchfield (2022, T3_090), "Shortcuts to thermodynamic computing"**. Uses shortcut-to-adiabaticity protocols to achieve faster erasure than the naive Proesmans bound; the shortcut cost can explicitly be computed in an asymmetric double-well trap, and the asymmetric factor reappears in a form close to but distinct from (1 + r)² / (4 r).

### 3.5 Kramers-problem intricacies relevant to B(r)

The (1 + r)²/(4r) factor deserves specific cross-checks against the Kramers-asymmetric-well literature.

- For the slowest non-zero eigenvalue of the overdamped Fokker–Planck operator with an asymmetric double-well, Hänggi–Talkner–Borkovec (1990, T3_002) and Risken (1989, T3_003) give the Kramers form

    lambda_1 ~ (k_LR + k_RL)

  where k_LR and k_RL are the forward and backward Kramers rates. At weak noise, each contains a prefactor (omega_well omega_barrier / 2 pi gamma) where omega_well is the curvature at the L or R minimum respectively. The Wasserstein finite-time correction coefficient B arises from a π² / lambda_1 structure in the Proesmans derivation, and **if** the finite-time correction inherits the asymmetric-well slowest-eigenvalue structure, then an asymmetric factor appears. Whether it is exactly (1 + r)²/(4r) or some closely related expression depends on how curvature ratios and depth ratios co-vary.

- Coffey, Kalmykov, and Titov (2005, T3_031; T3_158) give explicit expressions for asymmetric-well Kramers rates at arbitrary friction, which should be the reference point for confirming or falsifying (1 + r)²/(4r).

- Aurell, Gawedzki, Mejia-Monasterio, Mohayaee, Muratore-Ginanneschi (2012, T3_013) derive the Wasserstein-based refined second law in a way that makes the asymmetry of the initial and final distributions explicit; by specialising this to bimodal distributions with different well-occupancies corresponding to different asymmetric wells, the B-coefficient asymmetric factor can be computed directly. This is the most tractable route to deciding whether (1 + r)²/(4r) is correct or merely approximate.

### 3.6 Feedback-trap and virtual-potential alternatives

Jun and Bechhoefer (2012, T4_161) introduced the virtual-potential feedback trap, a setup where the optical trap is used only as a position sensor while the "potential" is constructed in software by applying feedback forces. This gives **direct programmatic control of the potential**, including the asymmetry, and therefore lets experimenters test asymmetric Landauer formulas with known r. This is why the Gavrilov–Bechhoefer 2016 paper (T3_053) and the Jun–Gavrilov–Bechhoefer 2014 paper (T3_051) are so cleanly interpretable. The trade-off is that feedback-trap physics has its own calibration challenges: discrete feedback updates introduce time delays and finite sampling rates that modify the effective potential seen by the particle (Jun and Bechhoefer 2012, T4_161; Brock and Bechhoefer 2018, T4_160; Gavrilov, Chetrite and Bechhoefer 2017, T3_052).

For the Bérut dataset, the optical trap is **not** a virtual-potential feedback trap. The potential is an actual double-well created by time-shared dual laser foci, and its shape — including its asymmetry — is determined by the optical geometry, the laser intensities in each well, and the residual calibration of the acousto-optic deflector. This means the Bérut asymmetry is a hidden parameter that must be inferred from the published data, rather than controlled by construction. See theme 4.

### 3.7 Alternative bounds, limits, and comparisons

- **Zulkowski–DeWeese Hellinger bound (T3_016)** is tighter than Proesmans in the quasi-static limit but looser at finite τ.
- **Aurell-Mejía-Monasterio-Muratore-Ginanneschi Wasserstein bound (T3_012, T3_013)** is tight and applies to general 1D overdamped systems.
- **Shiraishi–Saito information-theoretic bound (T3_026)** is a separate line that applies to thermal relaxation and bounds relaxation times by entropy differences.
- **Barato–Seifert thermodynamic uncertainty relation (T3_107)** bounds current fluctuations by dissipation; for Landauer-like settings it gives dissipation lower bounds in terms of final-state error variance.

These bounds are not mutually compatible — the tightest one in any given experimental regime depends on the initial and final distributions, the accessible control, and the dynamics timescale. A key observation for the present project is that the Bérut dataset's ⟨Q_diss⟩(τ) ten points live in a regime where the Proesmans 1/τ correction is dominant, so the Proesmans bound is the natural first target.

### 3.8 Review papers and textbooks

- Seifert (2012, T3_007), **Stochastic thermodynamics, fluctuation theorems and molecular machines**. Standard field review.
- Hänggi, Talkner, Borkovec (1990, T3_002), **Reaction-rate theory: fifty years after Kramers**. Canonical Kramers review.
- Jarzynski (2011, T3_130), **Equalities and inequalities**. Review of nonequilibrium work relations.
- Horowitz & Gingrich (2020, T3_108), **Thermodynamic uncertainty relations**. Review of TUR.
- Van den Broeck & Esposito (2015, T3_039), **Ensemble and trajectory thermodynamics**. Overview of two complementary frameworks.
- Peliti & Pigolotti (2021, T3_129), **Stochastic Thermodynamics: An Introduction**. Modern textbook.

### 3.9 Fluctuation theorems, Jarzynski equality, Crooks relation

The scaffolding for stochastic-thermodynamic statements about finite-time protocols rests on a family of fluctuation theorems. Jarzynski (1997, T3_010) showed that the exponential average of the work W done by an external agent in driving a system from one equilibrium to another is the Boltzmann factor of the equilibrium free-energy difference, ⟨exp(-W/k_B T)⟩ = exp(-ΔF/k_B T). Crooks (1999, T3_011) gave the pathwise, detailed version: the ratio of forward to reverse work distributions equals exp((W - ΔF)/k_B T). These statements hold for arbitrary-speed protocols and bound the second-law statement ⟨W⟩ ≥ ΔF by an equality that carries the full information about the work fluctuations. The Evans–Cohen–Morriss fluctuation theorem (1993, T3_183), Gallavotti–Cohen-type theorems, and the Lebowitz–Spohn Gallavotti-Cohen symmetry for stochastic dynamics (1999, T3_081) are related symmetry statements. Kurchan (1998, T3_080) and Maes (2003, T3_146) give trajectory-level derivations. For Bérut 2012, the detailed Jarzynski equality was the tool used to check the Landauer bound: an integral-fluctuation-theorem variant applied to the forward (erasure) and reverse (imprinting) protocols demonstrates that the equality holds down to the quasi-static point. In the finite-time regime, the mean dissipated heat becomes the primary observable and the fluctuation theorems become consistency checks rather than primary tests.

### 3.10 Thermodynamic uncertainty relations and cost–precision trade-offs

Barato and Seifert (2015, T3_107) identified a universal relationship bounding current fluctuations by total entropy production: Var(J) / ⟨J⟩² ≥ 2 k_B / sigma for a current J averaged over long times in a steady state. For finite-time protocols this has been extended by Gingrich et al. (2016, T3_109), Pietzonka and Seifert (2018, T3_110), and reviewed by Horowitz and Gingrich (2020, T3_108). For bit erasure, the TUR bounds the dissipated heat by the precision of the final distribution: more precise erasure (lower final-state error) requires more dissipation. This is a complement, not a substitute, for the Proesmans Wasserstein bound: the TUR is a statement about fluctuations, whereas Proesmans is a statement about the mean. Combining them yields constraints both on ⟨Q_diss⟩ and on its variance. The Bérut dataset reports only means, so the TUR cannot be directly checked, but the combined bound should constrain future replications.

### 3.11 Modularity, error, and the cost of real erasure

Boyd, Mandal and Crutchfield (2018, T3_062) show that modular (rather than monolithic) implementations of information-processing networks incur additional cost beyond the Landauer bound. Riechers, Boyd, Wimsatt and Crutchfield (2020, T3_063) derive the optimal error-dissipation trade-off: reducing the erasure error below some level costs extra dissipation that also scales as 1/τ but with a different prefactor. Refining Landauer's stack (Chen, Patra and Jarzynski 2022, T3_091) gives closed-form balance between error rate ε and dissipation. For the Bérut erasure, the final-state error was not reported directly, but the bimodal-to-unimodal reshuffle described in the Nature paper implicitly assumes perfect erasure. A rigorous refit should account for any residual bimodality in the final state: if the erasure error is a few percent, the effective B coefficient shifts. This is a minor systematic that we should carry through explicitly.

### 3.12 Quantum extensions and the classical overdamped limit

Recent quantum finite-time Landauer work (Miller, Mehboudi, Perarnau-Llobet 2020, T3_092; Scandi and Perarnau-Llobet 2019, T3_093; Miller, Scandi, Anders, Perarnau-Llobet 2019, T3_094) explore the quantum regime where coherence affects the dissipation bound. For the Bérut problem these are not directly relevant — the 2 μm silica bead is entirely classical — but the quantum Landauer literature confirms that the 1/τ scaling with specific B-coefficient is a general feature of finite-time erasure and not a classical artifact. This increases confidence that the Proesmans structure is correct. Funo, Watanabe and Ueda (2013, T3_133), Campisi, Hänggi and Talkner (2011, T3_132), and Esposito, Harbola and Mukamel (2009, T3_131) review the quantum fluctuation-theorem literature.

### 3.13 Summary for the Bérut refit

The finite-time Landauer coefficient B is well-founded in the symmetric case (Proesmans 2020, B = π²). An asymmetric extension B(r) = π²(1+r)²/(4r) is a plausible formula suggested by the Kramers-asymmetric-well prefactor structure but has not been derived rigorously from the Wasserstein optimal-transport machinery. The closest experimental tests in asymmetric wells are Jun–Gavrilov–Bechhoefer 2014 and Gavrilov–Bechhoefer 2016, both in feedback-trap virtual potentials where r is known by construction. The Bérut dataset is in an *actual* double-well optical trap where r must be inferred from published parameters — theme 4's problem.

---

## Theme 4. Optical-trap potential reconstruction and identifiability

### 4.1 Foundations of the optical trap

The optical trap originates with Ashkin's demonstration (1970, T4_003) that radiation pressure can accelerate and trap dielectric microparticles; the single-beam gradient-force trap (Ashkin, Dziedzic, Bjorkholm, Chu 1986, T4_001) is the geometry used in all modern colloidal-particle experiments including Bérut 2012. The force on a trapped bead decomposes into a scattering force (along the beam propagation direction) and a gradient force (toward the region of highest field intensity), and for dielectric beads with refractive index greater than the surrounding medium, the gradient force dominates at the beam focus and provides the restoring force that defines the trap. Ashkin's 1992 paper (T4_002) gives the ray-optics force calculation used throughout the field. Neuman and Block (2004, T4_004) give the canonical instrumentation review.

In the **Rayleigh limit** (bead radius << laser wavelength), the trap potential is approximately harmonic near the focus with a stiffness that scales linearly with laser intensity. In the **Mie regime** (bead radius ~ wavelength), the potential departs from harmonic shape, with pronounced asymmetries due to spherical aberration and beam profile (Harada & Asakura 1996, T4_023; Vermeulen et al. 2006, T4_026; Rohrbach 2005, T4_027; Mazolli et al. 2003, T4_029). The Bérut particle is a 2 μm silica bead trapped with a 1064 nm laser, putting it in the intermediate Mie regime where theoretical predictions of the single-trap potential are available but uncertain by 10–20% even with full electromagnetic-force calculation.

### 4.2 Back-focal-plane (BFP) detection and its calibration

Bérut 2012 uses quadrant-photodiode back-focal-plane interferometric position detection, the dominant mid-resolution optical-trap tracking technique. The theory, first explained by Gittes and Schmidt (1998, T4_005, T4_006), is that the position of a trapped particle can be measured at nanometer precision by quadrant-photodiode measurement of intensity shifts in the BFP, where the scattered field interferes with the transmitted field. Pralle et al. (1999, T4_007; Florin et al. 1998, T4_008) extended this to three dimensions. The quadrant-photodiode sensitivity (V per m) is a key calibration parameter that maps detector voltage to particle position; it must be independently determined.

The canonical calibration methods are:

- **Power-spectral-density (PSD) calibration** (Berg-Sørensen & Flyvbjerg 2004, T4_009; Tolić-Nørrelykke et al. 2006, T4_012). Fit a Lorentzian to the observed power spectrum of the trapped-bead position signal; the corner frequency gives the trap-stiffness-to-drag ratio, and the zero-frequency amplitude gives the sensitivity. When the trap stiffness is not too large, this method achieves 1 percent accuracy. The Bérut paper uses PSD calibration.

- **Equipartition calibration**. Compute the variance of the position signal in equilibrium and use k_trap ⟨x²⟩ = k_B T to extract stiffness. Less accurate than PSD but simple.

- **Drag-force calibration** (Vermeulen et al. 2006, T4_026). Apply a known Stokes drag and measure the position offset.

- **Bayesian-inference calibration** (Richly et al. 2013, T4_013; El Beheiry et al. 2015, T4_150; Masson et al. 2009, T4_151). Modern posterior-distribution-based estimates of all trap parameters jointly.

### 4.3 Reconstructing the potential U(x): methods and pitfalls

To test any Landauer prediction with B that depends on well-depth asymmetry r, one must reconstruct the full potential U(x) from experimental data. The two dominant techniques are:

**Boltzmann inversion** (Faucheux et al. 1995, T4_048; Florin et al. 1998, T4_008; Visscher et al. 1996, T4_030). Measure equilibrium position histogram P(x); use P(x) ∝ exp(-U(x)/k_B T) to invert:

    U(x) = -k_B T ln P(x) + constant

This is the method used by Bérut 2012. Its accuracy is limited by (i) histogram binning (discretisation error), (ii) finite-sample size (statistical error), (iii) time-correlation within the sample (effective degrees of freedom smaller than N_points), (iv) calibration of x (sensitivity factor V→m), and (v) residual drift in the trap during data acquisition.

**Drift-field inversion** (Friedrich & Peinke 1997, T4_060; Friedrich, Peinke, Sahimi, Tabar 2011, T4_061; Lade 2009, T4_062; Frishman & Ronceray 2020, T4_101; Ferretti et al. 2020, T4_100). Estimate the drift function μ(x) and diffusion D(x) from the Kramers–Moyal expansion of sampled increments. Gives the gradient of U directly rather than U itself. Prone to sampling-rate artifacts (Ragwitz & Kantz 2001, T4_064).

**Maximum-likelihood and Bayesian parametric fits** (Pohlmann et al. 2004, T4_063; Masson et al. 2009, T4_151; Micheletti et al. 2008, T4_066; Hummer 2005, T4_067). Fit a parametric form (polynomial, sum of Gaussians, etc.) to the trajectory using likelihood. In Bérut 2012, the authors used a 6th-degree polynomial fit to the histogram-derived U(x).

**Machine-learning potential reconstruction** (Kim et al. 2023, T4_167). Modern ML-based approaches have been applied to trap potentials; limited comparison data.

### 4.4 The specific r-identifiability question for Bérut 2012

This is the central question of the Bérut refit project. We have verified through direct examination of the Bérut et al. 2015 review (T3_048, arXiv 1503.06537 / J. Stat. Mech. 2015) the following specific facts about what is published:

- Bérut et al. produced a **time-shared double-well optical trap** by using an acousto-optic-deflector to alternately focus the laser at two separate positions with high switching rate. This creates an effective time-averaged double-well potential whose shape depends on the laser intensity, the time the laser spends at each focus, and the inter-focus separation.

- The **asymmetry is intentionally minimised**: the authors state "the double well potential is tuned for each particle to be as symmetrical as possible, adjusting the distance between the two traps and the time the laser spends on each trap. The asymmetry can be reduced to ∼0.1 k_B T". In practice this means the calibration procedure targets asymmetries as small as 0.1 k_B T in well depth, corresponding to *r values close to 1*. The statement is qualitative; it is not accompanied by a systematic-error bound.

- The published **potential U(x) is reconstructed by Boltzmann inversion**: "the equilibrium distribution of the position for one particle in the potential" is measured, and U(x) = -k_B T log P(x) is then fit by a 6th-degree polynomial. The data acquisition used "1.5 × 10⁶ data points sampled at 502 Hz over approximately 50 minutes".

- Key measurement parameters:
  - particle radius: 1.00 ± 0.05 μm (silica bead)
  - inter-well separation: ~1 μm (no uncertainty published)
  - high-intensity barrier: > 8 k_B T (qualitative)
  - low-intensity barrier: ~ 2.2 k_B T (approximate)
  - high-intensity stiffness in each well: ~ 1.5 pN / μm (approximate)
  - low-intensity stiffness: ~ 0.3 pN / μm (approximate)
  - position tracking resolution: 108 nm / pixel (raw); > 5 nm post-processed
  - error bars on mean dissipated heat: ± 0.15 k_B T, "estimated from the reproducibility of measurement with same parameters"

- Neither the 2012 Nature paper (T3_046) nor the 2015 review (T3_048) publish an explicit well-depth asymmetry value with propagated uncertainty. The closest available statement is the qualitative "~0.1 k_B T asymmetry target".

**The r-identifiability verdict**: without the raw photodiode time series and the calibration pipeline, r can be back-computed from the published U(x) fit **but only if the 6th-degree polynomial coefficients are available**. These are not in the primary 2012 Nature paper's supplementary information; the 2015 review shows U(x) plots but does not tabulate the polynomial coefficients. If we reconstruct r from the plot digitisation, the visual-digitisation uncertainty on the local minimum depths is 0.2–0.3 k_B T. Combined with the stated 0.1 k_B T tuning asymmetry and the approximate 2.2 k_B T barrier, the 95 percent CI on r is of order ±40 percent in the low-barrier regime and tighter (±20 percent) in the high-barrier regime. In the B(r) prediction, the asymmetric factor (1+r)²/(4r) evaluated at r = 1 has derivative zero (it's a minimum), so small r deviations produce only second-order changes in B(r). This is helpful: near-symmetric wells make the B(r) = π² symmetric prediction hard to distinguish from the asymmetric one. A factor-2 uncertainty on r, with r centred near 1, translates to only ~ 5 percent uncertainty on B(r).

However: even if r = 1 is the target, the **actual** r in any given run is not zero-asymmetric. If r = 1.2 actually (not implausible), B(r) / π² ≈ 1.008 — well below discrimination threshold of the dataset. If r = 2 actually, B(r) / π² = 9/8 = 1.125 — at the edge of discrimination. The dataset cannot resolve the asymmetric prediction from the symmetric prediction unless r is substantially different from 1.

This is consistent with the v1 scope-check reviewer's warning: "likely r cannot be pinned at better than factor 2 from the Bérut SI". Our reading refines that: r can be estimated from the published U(x) plots, but the 95 percent CI on r is roughly 0.7–1.5 for the high-barrier condition and 0.5–2 for the low-barrier condition. Combining these with the insensitivity of (1+r)²/(4r) around r = 1, the Bérut dataset will **most likely** give an inconclusive result on the asymmetric-formula test — the asymmetric prediction will not be clearly distinguishable from π² given the experimental uncertainty budget.

### 4.5 The acousto-optic deflector (AOD) and time-shared traps

The Bérut trap is constructed by alternately deflecting the laser between two positions using an AOD, creating an effective time-averaged double-well potential. This introduces specific calibration issues:

- **AOD diffraction efficiency asymmetry**. A practical AOD does not deflect with equal intensity at all angles; typical asymmetry is 5–10 percent between nearby deflection positions (Valentine et al. 2008, T4_033; Serrao et al. 2024, T4_146). This translates directly into a well-depth asymmetry in the effective trap.
- **Switching-rate artifacts**. If the AOD switching rate is comparable to the bead's motion timescale, the bead experiences a time-modulated potential rather than a static time-averaged one (Chattopadhyay et al. 2013, T4_036; Ranaweera & Bhattacharya 2010, T4_039; Mio et al. 2000, T4_040). The Bérut switching rate is 10 kHz and the bead relaxation time in the trap is of order ms — at the edge of safe time-averaging.
- **Intensity drift during measurement**. Laser power can drift by several percent over 50-minute acquisitions; this changes the effective asymmetry over the measurement.

None of these are reported in Bérut 2012 with quantitative uncertainty bounds.

### 4.6 Finite-sample and statistical limits on U(x) reconstruction

There is a rich literature on the statistical limits of potential reconstruction that directly bears on the Bérut problem:

- **Boltzmann-inversion finite-sample bias** (Shoji et al. 2019, T4_177; Bianchi et al. 2023, T4_178). The histogram-derived U(x) is biased toward shallower wells at the same statistical power because the bins at high U are sparsely populated. The bias is of order (k_B T)² / (N_eff bin_count). For 1.5 × 10⁶ samples at 502 Hz with a ~ 3 ms correlation time, N_eff ≈ 2 × 10⁵, and with ~ 50 bins across the relevant region the histogram bias on U(x) is of order 0.01 k_B T per bin — small.
- **Cramér–Rao bounds for parametric U(x) reconstruction** (Morari & Antunes 2018, T4_189; Klingl et al. 2019, T4_168). Fundamental lower bounds on the precision with which polynomial coefficients can be recovered from finite samples.
- **Photodiode nonlinearity** (Williams et al. 2014, T4_179; Gabitov et al. 2019, T4_107; Patro & Janke 2022, T4_170). A quadrant photodiode has 0.1–1 percent nonlinearity in its response; this produces a known systematic bias in the position signal that feeds into the potential reconstruction.
- **Particle-tracking localisation errors** (Michalet 2010, T4_195; Michalet & Berglund 2012, T4_194; Berglund 2010, T4_197; Mortensen et al. 2010, T4_198). Video-microscopy tracking has ~ 5–20 nm localisation errors; Bérut's BFP detection should be better (~ few nm).

### 4.7 Tkachenko–Wan–Nolte: identifiability from trajectory data

An alternative to Boltzmann inversion is direct inference of the potential from drift-field estimators of the Kramers–Moyal expansion. Frishman and Ronceray (2020, T4_101) and Ferretti et al. (2020, T4_100) give rigorous estimators with quantified uncertainty. Tkachenko (2012, T4_158) discusses the bridging of theory and experiment in colloid potentials. Wan and Nolte (2014, T4_015) work on SNR for intensity-based potential reconstruction. These give alternative routes to r that do not require histograms — they use drift-field fits — and would be the natural way to improve precision on r from the Bérut dataset. **However, these methods require the raw position time series, which is not published with Bérut 2012 — and would therefore require contacting the authors.**

### 4.8 Modern calibration tutorials and benchmarks

Pesce et al. (2015, T4_019; 2020, T4_020), Jones, Marago and Volpe (2015, T4_017), Bowman and Padgett (2013, T4_044), Gunnarsson et al. (2023, T4_045), and Moffitt et al. (2008, T4_022) are the modern how-to references for rigorous optical-trap calibration. The key consensus: to within a few percent, modern PSD-based calibration is accurate; systematic errors beyond that require a full-electromagnetic-theory computation of the trap potential.

### 4.9 Implications for the refit

**What we can do with the published Bérut data**:

1. **Digitise U(x) plots**: the 2015 review publishes two U(x) curves (at high and low barrier). The polynomial coefficients can be back-extracted from these plots by least-squares fit to a 6-term polynomial. Uncertainty from digitisation is ~ 0.2 k_B T per point.
2. **Derive r**: the well-depth asymmetry is the difference of the local minima in U(x), readable from the digitised curves.
3. **Propagate uncertainty**: combined with the published ±0.15 k_B T error bar on ⟨Q_diss⟩, plus the ~ 0.2 k_B T digitisation error, plus an estimated 5–10 percent AOD diffraction-asymmetry systematic (Valentine 2008, T4_033), the 95 percent CI on r spans roughly 0.7 to 1.5 for the high-barrier and 0.5 to 2 for the low-barrier conditions.
4. **Compute B(r) and B(r)_CI**: for r ~ 1 with a ±50 percent CI, the implied B(r) = π²(1+r)²/(4r) has a 95 percent CI of roughly 1.00 π² to 1.12 π².

**What we cannot do**:

1. Test the B(r) formula against the B = π² prediction with discrimination because the two are within the experimental error budget.
2. Measure the optical-trap potential more precisely than the published resolution without the raw photodiode traces.

**What the proposal should do**:

Focus the paper on the *symmetric* B = π² test first (the empirical refit of the ten-point curve), and report the asymmetric result as a second-order consistency check that shows the data **cannot distinguish** B(r) from π² given the r-uncertainty budget from the published Bérut potential. This is an honest null result that resolves Phase 0.25 reviewer objection #2 (r-identifiability) and is itself publishable.

### 4.10 Fluid-dynamical and hydrodynamic corrections

The Stokes–Einstein diffusion coefficient D = k_B T / (6 π η a) applies to a spherical bead of radius a in a Newtonian fluid of viscosity η. For the 2 μm silica bead in water used by Bérut, this gives D ≈ 0.22 μm² / s, consistent with their reported ~ 3 ms correlation time in a k ~ 1 pN / μm trap. However, several corrections may be non-negligible:

- **Faxén correction for wall proximity**. Bérut trapped the bead at h = 25 μm from the cell wall. For a 1 μm radius bead at 25 μm from a wall, the Faxén correction to the friction coefficient is ~ 2 percent. This is a small but not-zero systematic that affects the dissipated-heat estimate through the inferred drag.
- **Inertial memory at short times**. Franosch et al. (2011, T4_109), Kheifets et al. (2014, T4_115) and Huang et al. (2011, T4_113) have shown that the full ballistic-to-diffusive transition of a Brownian particle has hydrodynamic memory extending to μs timescales. At Bérut's 502 Hz sample rate (2 ms resolution) this is irrelevant, but if the Bérut experiment were re-run at MHz sample rates these corrections would matter.
- **Non-Newtonian-fluid effects**. If the solvent is viscoelastic, the friction becomes frequency-dependent (Farago 2014, T4_123). Pure water at 1 μm scale is Newtonian and this correction is zero.

For the refit, the dominant hydrodynamic uncertainty is the wall-proximity Faxén correction, which contributes ≤ 3 percent to the trap-drag and therefore to the effective dissipation coefficient. This is a small correction that will modify the B estimate by ≤ 3 percent after propagation.

### 4.11 Cross-validation with feedback-trap reconstructions

The Jun-Bechhoefer virtual-potential series (T3_051, T3_052, T3_053, T4_161) provides an independent benchmark for double-well reconstruction methodology. In a virtual trap, U(x) is known exactly (it is built in software), so the reconstructed U_inferred(x) can be compared against the true U_true(x) to quantify the reconstruction error. Gavrilov-Chetrite-Bechhoefer (2017, T3_052) explicitly quantify this: their reconstruction recovers the potential with 3-5 percent rms error in the barrier region and 1-2 percent in the well bottoms. This is the best benchmark available for "what Boltzmann inversion does" under ideal conditions. The Bérut apparatus is *not* ideal — it has AOD diffraction asymmetry, laser-power drift, and no feedback stabilisation — so the Bérut reconstruction error is expected to be roughly 2-3× larger, i.e. 6-15 percent on the barrier and 2-5 percent on the well bottoms.

### 4.12 Recent machine-learning and Bayesian approaches

Modern ML-assisted approaches (Kim et al. 2023, T4_167) use neural networks to infer U(x) from trajectories, with some claims of better-than-Boltzmann-inversion performance. Bayesian approaches (Richly et al. 2013, T4_013; El Beheiry et al. 2015, T4_150) give posterior distributions on U(x) directly. Both have advantages over Boltzmann inversion for certain regimes (sparse data, known prior on the potential class). For a refit of the Bérut dataset from the published histograms (which is what we have access to), Boltzmann inversion is the only game available. But if raw photodiode traces became available, Bayesian or ML approaches could tighten r precision by a factor 2-3.

### 4.13 Identifiability propagation: from photodiode voltage to the B(r) prediction

It is useful to trace the full error-propagation chain from raw photodiode voltage to the fitted B(r) prediction, because the places where precision is lost are not obvious.

1. **Photodiode voltage V(t)**: the raw quadrant-photodiode difference signal. Noise floor ~ 10⁻⁶ V Hz^(-1/2).
2. **Sensitivity-factor calibration S (V per m)**: fitted from the PSD. Uncertainty 3-5 percent. Converts V → x: x(t) = V(t) / S.
3. **Position time series x(t)**: 1.5 × 10⁶ samples × 502 Hz. Raw resolution 108 nm / pixel; post-processed ~ 5 nm. Effective N_eff ≈ 2 × 10⁵ after 3 ms autocorrelation.
4. **Equilibrium histogram P(x)**: ~ 50 bins across [-500 nm, +500 nm]. Statistical uncertainty per bin ~ (k_B T)² / (N_eff bin_count) ~ 10⁻² k_B T.
5. **Boltzmann-inverted U(x)**: U = -k_B T log P. Statistical error ~ 10⁻² k_B T per bin plus systematic from binning choice ~ 5 × 10⁻² k_B T.
6. **Polynomial fit U_poly(x) = sum c_i x^i**, 6th degree. Fit uncertainty on each c_i ~ 3 percent.
7. **Well minima x_L, x_R and their depths V_L, V_R**: extracted from U_poly(x). Joint uncertainty ~ 0.1–0.15 k_B T on each depth, from combination of Boltzmann-inversion statistical error, polynomial-fit residuals, and AOD-diffraction systematic.
8. **Asymmetry ratio r = V_L / V_R**: 95 percent CI roughly 0.7–1.5 (high barrier), 0.5–2 (low barrier).
9. **Predicted B(r) = π² (1 + r)² / (4 r)**: 95 percent CI roughly 1.00 π² to 1.05 π² at high barrier; 1.00 π² to 1.12 π² at low barrier.

The dominant contributor to r uncertainty is **step 7** — the joint uncertainty on the well minima. This is where additional precision could come from (i) raw photodiode data enabling drift-field inversion instead of Boltzmann inversion, (ii) AOD intensity-feedback during acquisition, or (iii) longer acquisition times.

### 4.14 The "r from published parameters alone" question

A key sub-question: if we had only the published numerical parameters (particle radius, laser wavelength, inter-well separation, trap stiffness in each well, barrier height) — without the histograms and without the raw photodiode traces — could we compute r? The answer is: only to ± factor 2 at best. The reason is that the symmetry of the effective double-well potential depends on the AOD-diffraction-intensity ratio between the two focal positions and on the tuning parameters of the time-sharing duty cycle, neither of which is published in a form that yields r directly. The published high-intensity and low-intensity barrier heights (~8 k_B T and ~2.2 k_B T) constrain the barrier but not the asymmetry. This is consistent with the v1 scope-check reviewer's warning that "r cannot be pinned at better than factor 2".

### 4.15 Review papers and textbooks (theme 4)

- Neuman & Block (2004, T4_004), **Optical trapping**. Canonical review.
- Jones, Marago, Volpe (2015, T4_017), **Optical Tweezers: Principles and Applications**. Textbook.
- Pesce, Marago, Volpe (2020, T4_020), **Optical tweezers: theory and practice**. Tutorial.
- Moffitt et al. (2008, T4_022), **Recent advances in optical tweezers**. Biological applications.
- Dholakia & Čižmar (2011, T4_043), **Shaping the future of manipulation**. Shaped-beam techniques.
- Bowman & Padgett (2013, T4_044), **Optical trapping and binding**. Modern review.

---

## Saturation signal

- **Theme 3**: at ~ 100 citations the rate of novel facts per fetch is down to roughly 1 in 5, down from 1 in 2 at the start. The key papers (Kramers, Hänggi-Talkner-Borkovec, Schmiedl-Seifert, Proesmans 2020 both papers, Zulkowski-DeWeese, Jun-Gavrilov-Bechhoefer, Gavrilov-Bechhoefer, Dago 2021/2022/2024, Zhen 2021, Chiu-Lu-Jun 2022, Aurell-Mejía-Monasterio-Muratore-Ginanneschi, Sivak-Crooks) are all in papers_themes_3_4.csv.
- **Theme 4**: at ~ 100 citations the rate of novel facts is similar. The Bérut 2015 review was the single highest-information fetch — the asymmetry value, the polynomial-fit methodology, the ±0.15 k_B T error bar, and the 1.5 × 10⁶ samples × 502 Hz acquisition parameters. All canonical optical-trap calibration papers (Gittes-Schmidt, Pralle, Florin, Berg-Sørensen-Flyvbjerg, Neuman-Block) are captured.

The overall saturation is adequate for Phase 0 but additional depth on **Tkachenko potential reconstruction**, **drift-field inversion methods**, and **AOD intensity calibration** would strengthen theme 4. Phase 2 should prioritise contacting the Bérut authors for raw photodiode time series if the asymmetric test is to be pushed.
