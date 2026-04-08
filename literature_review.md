# Literature Review -- Matbench Materials Property Prediction

*Comprehensive review organized by theme. Feeds into feature_candidates.md, research_queue.md, knowledge_base.md, and observations.md.*

## How to Use This Document

For each paper or book reviewed, create an entry with:

1. **Citation** (authors, year, title, venue)
2. **Key findings** relevant to your prediction task
3. **Features discussed** that map to your available signals
4. **Hypotheses generated** for research_queue.md (label as H1, H2, ...)
5. **Knowledge extracted** for knowledge_base.md

---

# PART 1: FOUNDATIONAL TEXTBOOKS

---

## Textbook 1: Introduction to Solid State Physics (Kittel)

**Full Citation**: Kittel, C. *Introduction to Solid State Physics*, 8th Edition. John Wiley & Sons, Hoboken, NJ, 2005. ISBN: 978-0-471-41526-8.

**Scope**: The standard undergraduate textbook for solid state physics worldwide. Covers crystal structure, lattice dynamics, electronic band theory, optical properties, and mechanical properties of solids. Universally required reading for all materials scientists and condensed matter physicists.

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 1: Crystal Structure | Bravais lattices, point groups, space groups, crystal systems | All structure tasks -- crystal symmetry is a fundamental descriptor |
| Ch. 2: Reciprocal Lattice | Brillouin zones, diffraction conditions | mp_gap, mp_is_metal (band structure lives in reciprocal space) |
| Ch. 3: Crystal Binding | Ionic, covalent, metallic, van der Waals, hydrogen bonds | mp_e_form, perovskites, jdft2d (exfoliation depends on interlayer binding) |
| Ch. 4: Phonons I -- Crystal Vibrations | Dispersion relations, acoustic/optical branches, density of states | phonons (directly predicts phonon DOS peak) |
| Ch. 5: Phonons II -- Thermal Properties | Debye model, specific heat, thermal conductivity | phonons, log_gvrh, log_kvrh (Debye temperature relates to elastic moduli) |
| Ch. 6: Free Electron Fermi Gas | Free electron model, Fermi energy, density of states | mp_gap, mp_is_metal, expt_gap, expt_is_metal |
| Ch. 7: Energy Bands | Bloch theorem, band gaps, metals vs insulators vs semiconductors | mp_gap, mp_is_metal, expt_gap, expt_is_metal (core theory) |
| Ch. 8: Semiconductor Crystals | Direct/indirect gaps, effective mass, intrinsic carriers | mp_gap, expt_gap, dielectric |
| Ch. 11: Optical Processes | Dielectric function, refractive index, Kramers-Kronig, absorption | dielectric (directly relevant to refractive index prediction) |
| Ch. 13: Dielectrics and Ferroelectrics | Clausius-Mossotti relation, polarizability, local fields | dielectric (key equations for refractive index) |

### Key Equations for Feature Engineering

1. **Clausius-Mossotti relation** (Ch. 13): (epsilon - 1)/(epsilon + 2) = (N * alpha) / (3 * epsilon_0), where alpha is atomic polarizability. This directly links dielectric constant to atomic-level quantities computable from composition.
2. **Debye temperature**: Theta_D = (hbar/k_B) * (6*pi^2*n)^(1/3) * v_s, where v_s is sound velocity. Links phonon peak frequency to elastic moduli.
3. **Free electron Fermi energy**: E_F = (hbar^2 / 2m) * (3*pi^2*n)^(2/3). Provides a baseline estimate for metallic systems.
4. **Band gap at zone boundary**: E_gap = 2|V_G| where V_G is the Fourier coefficient of the crystal potential. Links gap to electronegativity differences.

**Hypotheses generated**:
- H1: Clausius-Mossotti-derived polarizability features will improve dielectric constant prediction
- H2: Debye temperature computed from average atomic mass and bond strength will correlate with phonon DOS peak frequency
- H3: Electronegativity difference features (related to |V_G|) will be strong predictors of band gap

---

## Textbook 2: Solid State Physics (Ashcroft & Mermin)

**Full Citation**: Ashcroft, N. W. and Mermin, N. D. *Solid State Physics*. Harcourt College Publishers (Cengage Learning), 1976. ISBN: 978-0-03-083993-1.

**Scope**: The definitive graduate-level solid state physics textbook. More rigorous and comprehensive than Kittel. Treats band theory, lattice dynamics, transport, and mechanical properties with full mathematical detail. The standard reference for anyone doing computational materials science.

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 4-7: Crystal Lattices | Bravais lattices, reciprocal lattice, X-ray diffraction | All structure tasks |
| Ch. 8-10: Electron Levels in a Periodic Potential | Bloch's theorem, nearly free electron model, tight-binding model, band theory | mp_gap, mp_is_metal, expt_gap, expt_is_metal |
| Ch. 11: Other Methods for Band Structure | APW, OPW, pseudopotential methods | mp_gap, mp_is_metal (understanding DFT limitations) |
| Ch. 12: Semiclassical Model of Electron Dynamics | Effective mass, holes, electron/hole pockets | mp_gap, expt_gap |
| Ch. 22-23: Classical and Quantum Theory of the Harmonic Crystal | Phonon dispersion, density of states, Debye/Einstein models | phonons |
| Ch. 24: Measuring Phonon Dispersion | Neutron scattering, Raman/IR spectroscopy | phonons |
| Ch. 27: Dielectric Properties of Insulators | Macroscopic vs microscopic fields, Clausius-Mossotti, optical properties | dielectric |
| Ch. 28: Homogeneous Semiconductors | Intrinsic/extrinsic semiconductors, donor/acceptor levels | mp_gap, expt_gap, mp_is_metal, expt_is_metal |
| Ch. 29: Inhomogeneous Semiconductors | p-n junctions, carrier transport | expt_gap (practical gap measurements) |

### Key Equations for Feature Engineering

1. **Tight-binding band width** (Ch. 10): W ~ 2*z*t, where z is coordination number and t is the hopping integral. Band width relative to gap determines metallic character.
2. **Phonon density of states** (Ch. 23): g(omega) relates to the dynamical matrix eigenvalues. Peak frequency depends on force constants (bond stiffness) and atomic masses.
3. **Penn model for dielectric constant** (Ch. 27): epsilon ~ 1 + (hbar*omega_p / E_g)^2, linking dielectric constant to plasma frequency and band gap. This is a powerful feature: materials with small gaps have large dielectric constants.

**Hypotheses generated**:
- H4: Penn model feature (plasma_freq^2 / gap^2) will be a strong predictor for dielectric constant
- H5: Coordination number and bond-length-derived hopping parameters will correlate with band width and hence metallic character

---

## Textbook 3: Electronic Structure: Basic Theory and Practical Methods (Martin)

**Full Citation**: Martin, R. M. *Electronic Structure: Basic Theory and Practical Methods*, 2nd Edition. Cambridge University Press, Cambridge, UK, 2020. ISBN: 978-1-108-42947-2. (1st Edition: 2004, ISBN: 978-0-521-53440-6.)

**Scope**: The standard graduate textbook for density functional theory and electronic structure calculations. Essential for understanding the DFT calculations that generate the Materials Project data underlying 9 of the 13 Matbench tasks.

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 2: Overview of Electronic Structure Theory | Hartree-Fock, DFT overview, independent-particle approaches | All DFT-derived tasks |
| Ch. 6-7: Density Functional Theory | Hohenberg-Kohn theorems, Kohn-Sham equations, exchange-correlation | mp_e_form, mp_gap, mp_is_metal, perovskites (all DFT data) |
| Ch. 8: Functionals for Exchange and Correlation | LDA, GGA (PBE), meta-GGA, hybrid functionals | mp_gap (PBE gap underestimation is critical), mp_e_form |
| Ch. 9: Solving Kohn-Sham Equations | Plane waves, pseudopotentials, PAW | Understanding MP calculation methodology |
| Ch. 12: Plane Waves and Grids | Basis sets, cutoff energies | Understanding convergence of MP data |
| Ch. 14: Pseudopotentials | Norm-conserving, ultrasoft, PAW | MP uses PAW pseudopotentials |
| Ch. 19: Response Functions | Dielectric response, phonons from DFPT | dielectric, phonons |
| Ch. 20: Optical Properties | Dielectric function, refractive index from first principles | dielectric |
| Ch. 21: Lattice Dynamics | Force constants, dynamical matrix, phonon band structure | phonons |
| Ch. 22: Elastic Constants | Stress-strain, Voigt-Reuss-Hill averaging | log_gvrh, log_kvrh |

### Key Knowledge for Feature Engineering

1. **PBE band gap underestimation**: The PBE functional (used by Materials Project) systematically underestimates band gaps by 30-50%. This means the mp_gap task targets are NOT experimental gaps. Models should learn the PBE gap, not the true gap. The expt_gap task uses experimental values.
2. **Formation energy from DFT**: E_form = E_compound - sum(x_i * E_element_i). The elemental reference energies are DFT-calculated, so mp_e_form and perovskites targets are DFT formation energies.
3. **VRH averaging for elastic moduli**: The Voigt-Reuss-Hill average gives an effective isotropic modulus from the full elastic tensor. log_gvrh and log_kvrh use this averaging.
4. **Dielectric constant from DFPT**: The dielectric task values come from density-functional perturbation theory calculations.

**Hypotheses generated**:
- H6: Features derived from DFT-specific quantities (e.g., pseudopotential radius, number of valence electrons per DFT convention) may be more relevant than experimental atomic properties for DFT-data tasks
- H7: The systematic PBE gap error means composition-based "experimental gap" features should NOT be used directly for mp_gap prediction without correction

---

## Textbook 4: Materials Science and Engineering: An Introduction (Callister & Rethwisch)

**Full Citation**: Callister, W. D. Jr. and Rethwisch, D. G. *Materials Science and Engineering: An Introduction*, 10th Edition. John Wiley & Sons, Hoboken, NJ, 2018. ISBN: 978-1-119-40549-8.

**Scope**: The most widely used undergraduate textbook in materials science and engineering. Covers the full spectrum of materials science: structure, properties, processing, and performance. Provides an accessible introduction to mechanical, electronic, optical, and thermal properties.

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 2: Atomic Structure and Interatomic Bonding | Bonding types, bond energy vs. distance curves | mp_e_form, perovskites, jdft2d |
| Ch. 3: Structure of Crystalline Solids | Crystal systems, unit cells, APF, coordination number | All structure tasks |
| Ch. 6: Mechanical Properties | Stress-strain, elastic moduli, yield strength, hardness | steels, log_gvrh, log_kvrh |
| Ch. 7: Dislocations and Strengthening Mechanisms | Slip systems, solid solution strengthening, precipitation hardening, grain boundary strengthening | steels (core theory for yield strength) |
| Ch. 10: Phase Diagrams | Binary phase diagrams, lever rule, eutectic/eutectoid | steels (microstructure depends on phase equilibria) |
| Ch. 11: Phase Transformations | Nucleation, growth, TTT diagrams, martensite | steels, glass (glass formation = avoided crystallization) |
| Ch. 12: Electrical Properties | Band theory (simplified), conductors/semiconductors/insulators | mp_gap, mp_is_metal, expt_gap, expt_is_metal |
| Ch. 13: Optical Properties | Refractive index, absorption, transmission | dielectric |
| Ch. 15: Composites | Rule of mixtures | Mixing rule features for composition tasks |

### Key Equations for Feature Engineering

1. **Hall-Petch equation** (Ch. 7): sigma_y = sigma_0 + k_y / sqrt(d), where d is grain size. For steels, microstructural features dominate yield strength.
2. **Solid solution strengthening** (Ch. 7): Delta_sigma ~ c^(1/2) * |delta_r / r|^(4/3), where c is solute concentration and delta_r/r is atomic size misfit. Computable from composition.
3. **Rule of mixtures for moduli** (Ch. 15): K_mix = sum(x_i * K_i). A zeroth-order estimate for bulk/shear modulus from elemental values.
4. **Bond energy-interatomic distance relationship** (Ch. 2): E_bond ~ -A/r + B/r^n. Equilibrium bond length and bond energy set mechanical and thermal properties.

**Hypotheses generated**:
- H8: Atomic size mismatch features (Hume-Rothery rules) computed from composition will improve steels yield strength prediction
- H9: Weighted-average elemental elastic moduli will serve as strong baseline features for log_gvrh and log_kvrh
- H10: Electronegativity difference and atomic radius ratio will be strong predictors of formation energy

---

## Textbook 5: Physical Metallurgy (Haasen)

**Full Citation**: Haasen, P. *Physical Metallurgy*, 3rd Edition. Cambridge University Press, Cambridge, UK, 1996. ISBN: 978-0-521-55924-9.

**Scope**: A rigorous graduate-level treatment of the physics underlying metallic materials. Covers crystal defects, phase transformations, mechanical properties, and alloy design. Essential for understanding the steels and elastic moduli tasks.

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 1-3: Crystal Structure and Defects | Point defects, dislocations, stacking faults | steels, log_gvrh, log_kvrh |
| Ch. 7: Diffusion | Diffusion mechanisms, activation energy | steels (diffusion controls precipitation) |
| Ch. 8: Solidification | Nucleation theory, crystal growth, glass formation | glass |
| Ch. 9: Solid-Solid Phase Transformations | Precipitation, ordering, spinodal decomposition, martensitic transformation | steels |
| Ch. 10: Mechanical Properties | Elastic/plastic deformation, work hardening, fracture | steels, log_gvrh, log_kvrh |
| Ch. 11: Physical Properties of Alloys | Electronic structure, magnetic properties | expt_is_metal, mp_is_metal |

### Key Knowledge for Feature Engineering

1. **Peierls stress**: The intrinsic lattice friction for dislocation motion depends on crystal structure and bonding. FCC metals have low Peierls stress (ductile), BCC metals have high (strong but brittle at low T).
2. **Stacking fault energy**: Controls deformation mechanisms (twinning vs. slip). Low SFE promotes strain hardening. Related to composition via electronic structure (d-electron count).
3. **Precipitation strengthening**: Orowan mechanism -- strength increase proportional to precipitate spacing and size. For steels, the carbon content and alloying elements control precipitation.
4. **Elastic anisotropy**: The Zener ratio A = 2*C44/(C11-C12) measures elastic anisotropy. Important for understanding VRH averaging errors.

**Hypotheses generated**:
- H11: d-electron count features will capture stacking fault energy effects relevant to mechanical properties
- H12: Features encoding crystal structure type (FCC/BCC/HCP) will be important for elastic moduli tasks

---

## Textbook 6: Phase Transformations in Metals and Alloys (Porter, Easterling & Sherif)

**Full Citation**: Porter, D. A., Easterling, K. E., and Sherif, M. Y. *Phase Transformations in Metals and Alloys*, 3rd Edition. CRC Press (Taylor & Francis), Boca Raton, FL, 2009. ISBN: 978-1-4200-6210-6.

**Scope**: The definitive graduate textbook on phase transformations. Critical for understanding glass-forming ability (which is fundamentally about suppressing crystallization) and steel microstructure (which determines yield strength).

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 1: Thermodynamics and Phase Diagrams | Free energy, chemical potential, phase stability | mp_e_form, perovskites, glass |
| Ch. 2: Diffusion | Atomic mechanisms, Arrhenius behavior | glass (glass formers have sluggish diffusion) |
| Ch. 3: Crystal Interfaces and Microstructure | Interfacial energy, nucleation barriers | glass |
| Ch. 4: Solidification | Nucleation kinetics, undercooling, critical cooling rate | glass (GFA directly relates to critical cooling rate) |
| Ch. 5: Diffusional Transformations in Solids | Precipitation, TTT/CCT diagrams | steels |
| Ch. 6: Diffusionless Transformations | Martensitic transformation | steels (martensite dominates high-strength steels) |

### Key Equations for Feature Engineering

1. **Gibbs free energy of mixing**: Delta_G_mix = Delta_H_mix - T * Delta_S_mix. Drives phase stability and formation energy.
2. **Ideal entropy of mixing**: Delta_S_mix = -R * sum(x_i * ln(x_i)). Higher mixing entropy stabilizes solid solutions (high-entropy alloy concept).
3. **Turnbull's reduced glass transition temperature**: T_rg = T_g / T_m. Higher T_rg indicates better glass-forming ability. T_rg > 2/3 is the Turnbull criterion for easy glass formation.
4. **Critical cooling rate for glass formation**: R_c ~ exp(-Delta_G* / kT) * exp(-Q_D / kT). Depends on nucleation barrier and diffusion activation energy.

**Hypotheses generated**:
- H13: Configurational entropy of mixing features will improve glass-forming ability prediction
- H14: Liquidus temperature estimates (from binary phase diagram data) combined with T_g proxies will be strong GFA predictors
- H15: Mixing enthalpy features (from Miedema model) will correlate with both formation energy and glass-forming ability

---

## Textbook 7: Introduction to Computational Materials Science (LeSar)

**Full Citation**: LeSar, R. *Introduction to Computational Materials Science: Fundamentals to Applications*. Cambridge University Press, Cambridge, UK, 2013. ISBN: 978-0-521-84587-8.

**Scope**: Bridges the gap between traditional materials science theory and computational methods. Covers DFT, molecular dynamics, Monte Carlo, and finite-element methods as applied to materials problems. Directly relevant to understanding how the Matbench data was generated.

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 3: Quantum Mechanics of Electrons | Schrodinger equation, variational principle | All DFT-derived tasks |
| Ch. 4: Density Functional Theory | Kohn-Sham equations, exchange-correlation, pseudopotentials | All DFT-derived tasks |
| Ch. 5: Applications of DFT | Total energy, forces, elastic constants, phonons | mp_e_form, log_gvrh, log_kvrh, phonons |
| Ch. 6: Atomic-Scale Simulations | Interatomic potentials, molecular dynamics | Understanding structure-property relationships |
| Ch. 8: Phase Diagrams | CALPHAD, first-principles thermodynamics | mp_e_form, perovskites |
| Ch. 10: Mechanical Properties | Elasticity, plastic deformation, fracture | log_gvrh, log_kvrh, steels |

### Key Knowledge for Feature Engineering

1. **Equation of state fitting**: E(V) curves fit to Birch-Murnaghan EOS yield bulk modulus K = V * d^2E/dV^2 at equilibrium. The curvature of the energy-volume relationship determines bulk modulus.
2. **Elastic constants from DFT**: Apply small strains, compute stress response. Voigt-Reuss-Hill average converts full Cij tensor to isotropic K and G.
3. **Phonons from DFPT**: Density-functional perturbation theory computes force constant matrices. Eigenvalues give phonon frequencies.
4. **Convergence requirements**: k-point mesh, energy cutoff, and structure relaxation all affect DFT accuracy. Materials Project uses standardized settings.

---

## Textbook 8: Introduction to Glass Science and Technology (Shelby)

**Full Citation**: Shelby, J. E. *Introduction to Glass Science and Technology*, 2nd Edition. Royal Society of Chemistry, Cambridge, UK, 2005. ISBN: 978-0-85404-639-3.

**Scope**: The standard textbook for glass science. Covers glass formation, structure, viscosity, and properties. Directly relevant to the glass-forming ability prediction task.

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 2: Fundamentals of the Glassy State | Definition of glass, glass transition, thermodynamics vs kinetics | glass |
| Ch. 3: Glass Formation | Kinetic theory, Turnbull criterion, structural criteria, Inoue rules | glass (core theory) |
| Ch. 4: Glass Composition | Oxide glasses, metallic glasses, network formers/modifiers | glass |
| Ch. 6: Viscosity of Glass-Forming Melts | VFT equation, fragility, Angell plot | glass |
| Ch. 9: Mechanical Properties | Elastic moduli of glasses | log_gvrh, log_kvrh (amorphous materials) |
| Ch. 11: Optical Properties | Refractive index of glasses | dielectric |

### Key Equations for Feature Engineering

1. **Inoue's three empirical rules for metallic glass formation**: (a) multicomponent system (3+ elements), (b) significant atomic size differences (>12%), (c) negative heats of mixing. All computable from composition.
2. **Zachariasen's rules for oxide glass formation**: (a) oxygen forms no more than 2 bonds with glass-forming cations, (b) coordination number of glass-forming cation is small (3 or 4), (c) oxygen polyhedra share corners, not edges or faces.
3. **VFT equation**: log(eta) = A + B / (T - T_0). Viscosity controls glass-forming ability. Materials with high fragility (large deviation from Arrhenius) are poor glass formers.

**Hypotheses generated**:
- H16: Inoue's three rules encoded as features (number of components, max atomic size ratio, mean mixing enthalpy) will be top predictors for glass-forming ability
- H17: Atomic size dispersion (std/mean of atomic radii) will be a strong GFA predictor

---

## Textbook 9: Introduction to Thermoelectrics (Goldsmid) / Thermodynamics in Materials Science (DeHoff)

### 9a: Thermodynamics in Materials Science (DeHoff)

**Full Citation**: DeHoff, R. T. *Thermodynamics in Materials Science*, 2nd Edition. CRC Press (Taylor & Francis), Boca Raton, FL, 2006. ISBN: 978-0-8493-4065-9.

**Scope**: A comprehensive treatment of thermodynamics as applied to materials science. Covers solution thermodynamics, phase equilibria, and reaction thermodynamics. Essential for understanding formation energy.

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 4: Thermodynamic Variables and Relations | Free energy, enthalpy, entropy | mp_e_form, perovskites |
| Ch. 8: Multicomponent Homogeneous Systems | Chemical potential, activity, solution models | mp_e_form, perovskites |
| Ch. 9: Multicomponent Heterogeneous Systems | Phase equilibria, phase diagrams, Gibbs phase rule | mp_e_form, glass |
| Ch. 10: Reaction Thermodynamics | Enthalpy of formation, Born-Haber cycle | mp_e_form, perovskites |

### Key Equations for Feature Engineering

1. **Born-Haber cycle**: Formation enthalpy of ionic compounds from ionization energies, electron affinities, and lattice energy. Provides physics-based estimate of formation energy from elemental properties.
2. **Miedema model**: Delta_H_mix = f(Delta_phi, Delta_n_ws, V^(2/3)), where phi is electronegativity, n_ws is electron density at Wigner-Seitz boundary. Empirical model for mixing enthalpy computable from composition.
3. **Regular solution model**: Delta_G_mix = Omega * x_A * x_B + RT * (x_A * ln(x_A) + x_B * ln(x_B)). Parameterizable from atomic properties.
4. **Hildebrand solubility parameter**: delta = sqrt(E_coh / V_m). Relates cohesive energy density to miscibility.

**Hypotheses generated**:
- H18: Miedema model mixing enthalpy, computable from composition alone, will be a strong predictor for formation energy
- H19: Born-Haber cycle components (ionization energy, electron affinity, lattice energy estimate) will improve mp_e_form prediction

---

## Textbook 10: Fundamentals of Semiconductors (Yu & Cardona)

**Full Citation**: Yu, P. Y. and Cardona, M. *Fundamentals of Semiconductors: Physics and Materials Properties*, 4th Edition. Springer-Verlag, Berlin, 2010. ISBN: 978-3-642-00709-5.

**Scope**: The definitive graduate textbook on semiconductor physics. Covers electronic band structure, optical properties, phonons, and transport in semiconductors. Essential for understanding band gap, dielectric constant, and phonon tasks.

### Relevant Chapters and Matbench Task Mapping

| Chapter | Topic | Relevant Matbench Tasks |
|---------|-------|------------------------|
| Ch. 2: Electronic Band Structures | Empirical pseudopotential, k.p theory, band structure of common semiconductors | mp_gap, expt_gap, mp_is_metal, expt_is_metal |
| Ch. 3: Vibrational Properties | Phonon dispersion, Raman/IR activity, LO-TO splitting | phonons |
| Ch. 4: Electronic Properties of Defects | Shallow and deep levels, vacancy formation energy | mp_e_form (defect contributions) |
| Ch. 6: Optical Properties I | Dielectric function, interband transitions, Penn model, oscillator strength | dielectric |
| Ch. 7: Optical Properties II | Excitons, polaritons, nonlinear optics | dielectric |

### Key Equations for Feature Engineering

1. **Penn model** (Ch. 6): epsilon_inf = 1 + (hbar * omega_p / E_g)^2, where omega_p is plasma frequency and E_g is band gap. Extremely powerful: links dielectric constant directly to gap and electron density.
2. **Moss relation**: E_g * n^4 = constant (~95 eV for many semiconductors). Empirical rule linking refractive index to band gap.
3. **Ravindra relation**: n = 4.16 - 0.85 * E_g. Linear approximation of refractive index vs. band gap.
4. **Phillips ionicity**: f_i = (C / E_g)^2, where C is the ionic contribution to the gap. Separates ionic from covalent character.
5. **Vegard's law**: a_alloy = x * a_A + (1-x) * a_B. Linear interpolation of lattice constant with composition for alloys. Deviations (bowing) relate to formation energy.

**Hypotheses generated**:
- H20: Penn model features (electron density / gap proxy) will be among the top 3 predictors for dielectric task
- H21: Moss/Ravindra relation features linking gap and refractive index suggest a joint model could help both dielectric and gap tasks
- H22: Phillips ionicity features will capture the ionic/covalent character relevant to band gap and formation energy

---

# PART 2: SEMINAL / FOUNDATIONAL PAPERS

---

## Theme A: Density Functional Theory Foundations

These papers underpin ALL DFT-derived Matbench tasks (mp_e_form, mp_gap, mp_is_metal, perovskites, log_gvrh, log_kvrh, phonons, dielectric, jdft2d).

---

### Seminal Paper 1: Hohenberg-Kohn Theorem

**Citation**: Hohenberg, P. and Kohn, W. "Inhomogeneous Electron Gas." *Physical Review* **136**(3B), B864-B871 (1964). DOI: 10.1103/PhysRev.136.B864

**Key contribution**: Proved that the ground-state electron density uniquely determines all ground-state properties of a many-electron system (the first Hohenberg-Kohn theorem), and that the ground-state density minimizes the total energy functional (the second HK theorem). This is the theoretical foundation of DFT.

**Relevance to Matbench**: Every DFT calculation in the Materials Project is based on this theorem. The total energy (used for formation energy), band structure (band gap), elastic constants, phonons, and dielectric response all derive from DFT.

**Key equation**: E[n] = F[n] + integral(v_ext(r) * n(r) dr), where F[n] is the universal functional.

---

### Seminal Paper 2: Kohn-Sham Equations

**Citation**: Kohn, W. and Sham, L. J. "Self-Consistent Equations Including Exchange and Correlation Effects." *Physical Review* **140**(4A), A1133-A1138 (1965). DOI: 10.1103/PhysRev.140.A1133

**Key contribution**: Introduced the Kohn-Sham scheme, mapping the interacting many-electron problem onto a set of non-interacting single-particle equations with an effective potential containing exchange and correlation effects. Made DFT computationally practical.

**Relevance to Matbench**: The Kohn-Sham equations are what the VASP code actually solves in every Materials Project calculation. The Kohn-Sham eigenvalues define the band structure (mp_gap), and the total energy from the KS functional gives formation energies (mp_e_form, perovskites).

**Key equation**: [-hbar^2/(2m) * nabla^2 + v_eff(r)] * psi_i(r) = epsilon_i * psi_i(r), where v_eff = v_ext + v_Hartree + v_xc.

---

### Seminal Paper 3: PBE Functional

**Citation**: Perdew, J. P., Burke, K., and Ernzerhof, M. "Generalized Gradient Approximation Made Simple." *Physical Review Letters* **77**(18), 3865-3868 (1996). DOI: 10.1103/PhysRevLett.77.3865

**Key contribution**: Introduced the PBE generalized gradient approximation (GGA) for the exchange-correlation functional. Became the most widely used functional in solid-state DFT due to its balance of accuracy and computational cost.

**Relevance to Matbench**: The Materials Project uses PBE for all calculations. This means: (1) formation energies (mp_e_form) are PBE formation energies; (2) band gaps (mp_gap) are PBE gaps, which systematically underestimate experimental gaps by 30-50%; (3) elastic constants, phonons, and dielectric properties are all PBE values. Understanding PBE's systematic errors is critical for feature engineering.

**Key knowledge**: PBE band gap underestimation is NOT random -- it's systematic. Larger-gap materials tend to have larger absolute errors but smaller relative errors. This suggests that features capturing the PBE error pattern could improve gap prediction.

---

### Seminal Paper 4: PAW Method

**Citation**: Blochl, P. E. "Projector augmented-wave method." *Physical Review B* **50**(24), 17953-17979 (1994). DOI: 10.1103/PhysRevB.50.17953

**Key contribution**: Introduced the projector augmented-wave (PAW) method, which combines the computational efficiency of pseudopotentials with the accuracy of all-electron methods. The PAW method is the basis for accurate treatment of core electrons in VASP.

**Relevance to Matbench**: All Materials Project calculations use VASP with PAW pseudopotentials. The PAW method determines which electrons are treated explicitly (valence) versus frozen (core), affecting the accuracy of computed properties.

---

### Seminal Paper 5: VASP

**Citation**: Kresse, G. and Furthmuller, J. "Efficient iterative schemes for ab initio total-energy calculations using a plane-wave basis set." *Physical Review B* **54**(16), 11169-11186 (1996). DOI: 10.1103/PhysRevB.54.11169

**Key contribution**: Described the implementation of DFT in the VASP code with efficient algorithms for self-consistent iteration, including the residual minimization method and the blocked Davidson scheme. VASP became the most widely used DFT code for solids.

**Relevance to Matbench**: VASP is the code used by the Materials Project for all calculations. Understanding VASP's computational parameters (ENCUT, KPOINTS, EDIFF, etc.) helps understand the precision of Matbench data. VASP's default convergence criteria set the noise floor of the training data.

---

## Theme B: Band Theory and Electronic Structure

Relevant to: mp_gap, mp_is_metal, expt_gap, expt_is_metal, dielectric

---

### Seminal Paper 6: Bloch's Theorem (original)

**Citation**: Bloch, F. "Uber die Quantenmechanik der Elektronen in Kristallgittern." *Zeitschrift fur Physik* **52**(7-8), 555-600 (1929). DOI: 10.1007/BF01339455

**Key contribution**: Proved that electron wavefunctions in a periodic potential must have the form psi_k(r) = u_k(r) * exp(i*k.r), where u_k has the periodicity of the lattice. This is the foundation of band theory.

**Relevance to Matbench**: Bloch's theorem is why band structure exists. The concept of band gaps, metals vs. insulators, and effective masses all follow from the periodicity of the crystal potential. Band gap prediction (mp_gap, expt_gap) and metallic classification (mp_is_metal, expt_is_metal) are direct consequences of band theory.

---

### Seminal Paper 7: Penn Model for Dielectric Constant

**Citation**: Penn, D. R. "Wave-Number-Dependent Dielectric Function of Semiconductors." *Physical Review* **128**(5), 2093-2097 (1962). DOI: 10.1103/PhysRev.128.2093

**Key contribution**: Derived a simple expression for the static dielectric constant of semiconductors based on a two-band model: epsilon = 1 + (hbar * omega_p / E_g)^2, where omega_p is the plasma frequency. Showed that dielectric constant is primarily determined by electron density and band gap.

**Relevance to Matbench**: Directly relevant to the dielectric task. The Penn model suggests that features encoding electron density (from composition) and band gap proxy will be the most important predictors of dielectric constant/refractive index.

**Key equation**: epsilon_infinity ~ 1 + (hbar * omega_p)^2 / E_g^2

---

### Seminal Paper 8: Harrison's Tight-Binding Theory

**Citation**: Harrison, W. A. "Electronic Structure and the Properties of Solids: The Physics of the Chemical Bond." W. H. Freeman and Company, San Francisco, 1980 (reprinted by Dover, 1989). ISBN: 978-0-486-66021-9.

Note: This is technically a monograph, but it functions as the seminal reference for tight-binding parameterization. The key papers are:
- Harrison, W. A. "Bond-orbital model and the properties of tetrahedrally coordinated solids." *Physical Review B* **8**(10), 4487-4498 (1973). DOI: 10.1103/PhysRevB.8.4487

**Key contribution**: Developed a universal tight-binding model parameterized by interatomic distance d: V_ll'm = eta_ll'm * hbar^2 / (m * d^2). The parameters eta are universal constants for each orbital interaction type (ss_sigma, sp_sigma, pp_sigma, pp_pi, etc.). This allows prediction of band gaps, dielectric constants, elastic constants, and cohesive energies from structure alone.

**Relevance to Matbench**: Harrison's model provides physics-motivated features: the tight-binding hopping integrals scale as 1/d^2, so bond-length-based features should capture electronic structure trends. The bond-orbital model predicts band gaps from electronegativity differences and bond lengths, directly useful for mp_gap and expt_gap.

**Key equation**: E_gap ~ 2 * sqrt(V2^2 + V3^2), where V2 is the covalent energy (~1/d^2) and V3 is the ionic energy (~electronegativity difference).

---

## Theme C: Elastic Properties

Relevant to: log_gvrh, log_kvrh, steels

---

### Seminal Paper 9: Voigt-Reuss-Hill Averaging

**Citation**: Hill, R. "The Elastic Behaviour of a Crystalline Aggregate." *Proceedings of the Physical Society, Section A* **65**(5), 349-354 (1952). DOI: 10.1088/0370-1298/65/5/307

Also foundational:
- Voigt, W. *Lehrbuch der Kristallphysik*. Teubner, Leipzig, 1928.
- Reuss, A. "Berechnung der Fliessgrenze von Mischkristallen auf Grund der Plastizitatsbedingung fur Einkristalle." *Zeitschrift fur Angewandte Mathematik und Mechanik* **9**(1), 49-58 (1929).

**Key contribution**: Hill proved that the Voigt average (uniform strain assumption) provides an upper bound and the Reuss average (uniform stress assumption) provides a lower bound for the effective elastic moduli of a polycrystalline aggregate. The arithmetic mean of Voigt and Reuss (the VRH average) gives the best single estimate.

**Relevance to Matbench**: The log_gvrh and log_kvrh tasks predict exactly the VRH-averaged shear and bulk moduli. Understanding that these are averages of the single-crystal elastic tensor Cij helps explain why certain structural features (anisotropy, crystal system) matter.

**Key equations**:
- K_Voigt = (1/9) * (C11 + C22 + C33 + 2*(C12 + C13 + C23))
- K_Reuss = 1 / (S11 + S22 + S33 + 2*(S12 + S13 + S23))
- K_VRH = (K_Voigt + K_Reuss) / 2

---

### Seminal Paper 10: Elastic Constants and Bonding

**Citation**: Gilman, J. J. "Electronic Basis of the Strength of Materials." Cambridge University Press, 2003. ISBN: 978-0-521-62005-5.

And the earlier seminal paper:
- Cohen, M. L. "Calculation of bulk moduli of diamond and zinc-blende solids." *Physical Review B* **32**(12), 7988-7991 (1985). DOI: 10.1103/PhysRevB.32.7988

**Key contribution**: Cohen showed that the bulk modulus of covalent solids scales as K ~ (1971 - 220*lambda) / d^3.5, where d is the nearest-neighbor distance and lambda is an ionicity parameter (0 for Group IV, 1 for III-V, 2 for II-VI). This is a remarkably simple predictive formula.

**Relevance to Matbench**: Cohen's formula suggests that bond length and ionicity are the dominant predictors of bulk modulus. For the log_kvrh task, features based on average bond length and electronegativity difference should be highly predictive.

**Key equation**: B_0 = (1971 - 220*lambda) / d^3.5 GPa (for tetrahedral semiconductors)

**Hypotheses generated**:
- H23: Cohen's d^(-3.5) scaling for bulk modulus, computable from structure, will be a top feature for log_kvrh
- H24: Ionicity-corrected bond-length features will outperform uncorrected bond-length features for elastic moduli

---

### Seminal Paper 11: Hall-Petch Relation

**Citation**: Hall, E. O. "The Deformation and Ageing of Mild Steel: III Discussion of Results." *Proceedings of the Physical Society, Section B* **64**(9), 747-753 (1951). DOI: 10.1088/0370-1301/64/9/303

And independently:
- Petch, N. J. "The Cleavage Strength of Polycrystals." *Journal of the Iron and Steel Institute* **174**, 25-28 (1953).

**Key contribution**: Discovered that the yield strength of polycrystalline metals varies inversely with the square root of the grain size: sigma_y = sigma_0 + k_y / sqrt(d). This established that microstructure, not just composition, determines mechanical strength.

**Relevance to Matbench**: For matbench_steels, the Hall-Petch effect means that yield strength depends on processing history (which determines grain size), not just composition. Since Matbench provides only composition, the steels task is intrinsically limited -- composition alone cannot capture grain size effects. This sets a floor on achievable MAE.

**Key knowledge**: The matbench_steels dataset likely includes steels with similar compositions but different processing, leading to different yield strengths. This is an irreducible source of noise for composition-only prediction.

---

### Seminal Paper 12: Solid Solution Strengthening

**Citation**: Fleischer, R. L. "Substitutional solution hardening." *Acta Metallurgica* **11**(3), 203-209 (1963). DOI: 10.1016/0001-6160(63)90213-X

Also foundational:
- Labusch, R. "A Statistical Theory of Solid Solution Hardening." *Physica Status Solidi B* **41**(2), 659-669 (1970). DOI: 10.1002/pssb.19700410221

**Key contribution**: Fleischer developed the theory of solid solution strengthening, showing that the yield strength increase from solute atoms scales with the square root of solute concentration and depends on atomic size misfit and modulus misfit: Delta_sigma ~ c^(1/2) * (|delta_G/G|^2 + alpha^2 * |delta_r/r|^2)^(1/2).

**Relevance to Matbench**: For matbench_steels, solid solution strengthening from alloying elements (C, Mn, Si, Cr, Mo, Ni, V, etc.) is a major contribution to yield strength. The Fleischer/Labusch model suggests that size misfit (|delta_r/r|) and modulus misfit (|delta_G/G|) computed from composition are key features.

**Hypotheses generated**:
- H25: Fleischer-Labusch model features (size misfit, modulus misfit per element, weighted by concentration) will improve steels prediction
- H26: Square root of total alloying content may be a useful simple feature for steels yield strength

---

## Theme D: Glass-Forming Ability

Relevant to: glass

---

### Seminal Paper 13: Turnbull's Criterion for Glass Formation

**Citation**: Turnbull, D. "Under what conditions can a glass be formed?" *Contemporary Physics* **10**(5), 473-488 (1969). DOI: 10.1080/00107516908204405

**Key contribution**: Established the reduced glass transition temperature T_rg = T_g / T_m as the key parameter for glass-forming ability. Materials with T_rg > 2/3 are excellent glass formers because the ratio of glass transition temperature to melting/liquidus temperature controls the time window for crystallization. Also discussed the kinetic theory of nucleation as applied to glass formation.

**Relevance to Matbench**: For the glass task, Turnbull's criterion suggests that features approximating T_g / T_m from composition will be powerful predictors. Elemental melting points (weighted average) provide a T_m proxy; T_g can be estimated from empirical correlations.

---

### Seminal Paper 14: Inoue's Three Rules for Bulk Metallic Glass Formation

**Citation**: Inoue, A. "Stabilization of metallic supercooled liquid and bulk amorphous alloys." *Acta Materialia* **48**(1), 279-306 (2000). DOI: 10.1016/S1359-6454(99)00300-6

Earlier foundational work:
- Inoue, A., Zhang, T., and Masumoto, T. "Al-La-Ni amorphous alloys with a wide supercooled liquid region." *Materials Transactions, JIM* **30**(12), 965-972 (1989).

**Key contribution**: Formulated the three empirical rules for forming bulk metallic glasses: (1) multicomponent systems with 3 or more elements; (2) significant difference in atomic size ratios (above ~12% mismatch among the main constituent elements); (3) negative heats of mixing among the main constituent elements. Also identified the supercooled liquid region Delta_T_x = T_x - T_g as a measure of thermal stability.

**Relevance to Matbench**: All three of Inoue's rules can be computed from composition: (1) number of distinct elements, (2) atomic size mismatch parameter delta = sqrt(sum(c_i*(1-r_i/r_bar)^2)), (3) mixing enthalpy from Miedema or similar models. These should be top features for the glass task.

**Key equations**:
- delta = sqrt(sum_i c_i * (1 - r_i / r_mean)^2) (atomic size mismatch parameter)
- Delta_H_mix = sum_{i!=j} 4 * Omega_ij * c_i * c_j (mixing enthalpy from regular solution)

---

### Seminal Paper 15: Senkov/Miracle Topological Model

**Citation**: Miracle, D. B. "A structural model for metallic glasses." *Nature Materials* **3**, 697-702 (2004). DOI: 10.1038/nmat1219

**Key contribution**: Proposed a structural model for metallic glasses based on efficient packing of atoms with different sizes around solute-centered clusters. The model explains why certain atomic size ratios favor glass formation and predicts the composition ranges where metallic glasses form.

**Relevance to Matbench**: Reinforces that atomic size ratios and packing efficiency are key descriptors for glass-forming ability.

---

## Theme E: Perovskite Structure and Stability

Relevant to: perovskites

---

### Seminal Paper 16: Goldschmidt Tolerance Factor

**Citation**: Goldschmidt, V. M. "Die Gesetze der Krystallochemie." *Die Naturwissenschaften* **14**(21), 477-485 (1926). DOI: 10.1007/BF01507527

**Key contribution**: Introduced the tolerance factor t = (r_A + r_O) / (sqrt(2) * (r_B + r_O)) for ABX3 perovskites, where r_A, r_B, and r_O are the ionic radii of the A-site cation, B-site cation, and anion respectively. Perovskites form when 0.8 < t < 1.0. This is one of the most successful simple predictive rules in materials science.

**Relevance to Matbench**: For the perovskites task (predicting formation energy of ABX3 perovskites), the Goldschmidt tolerance factor is likely the single most important feature. Deviation from t = 1 indicates structural distortion and higher formation energy.

**Key equation**: t = (r_A + r_X) / (sqrt(2) * (r_B + r_X))

**Hypotheses generated**:
- H27: Goldschmidt tolerance factor will be among the top 3 features for perovskite formation energy
- H28: Octahedral factor mu = r_B / r_X is a complementary predictor to the tolerance factor

---

### Seminal Paper 17: Bartel's New Tolerance Factor

**Citation**: Bartel, C. J., Sutton, C., Goldsmith, B. R., Ouyang, R., Musgrave, C. B., Ghiringhelli, L. M., and Scheffler, M. "New tolerance factor to predict the stability of perovskite oxides and halides." *Science Advances* **5**(2), eaav0693 (2019). DOI: 10.1126/sciadv.aav0693

**Key contribution**: Proposed an improved tolerance factor tau = r_X / r_B - n_A * (n_A - r_A/r_B) / ln(r_A/r_B), where n_A is the oxidation state of the A-site cation. This outperforms the Goldschmidt tolerance factor for predicting perovskite stability, especially for halide perovskites.

**Relevance to Matbench**: The Bartel tolerance factor is a more modern and accurate predictor for perovskite stability. Should be implemented as a feature for the perovskites task.

**Hypotheses generated**:
- H29: Bartel tolerance factor tau will outperform Goldschmidt tolerance factor t for perovskite formation energy prediction

---

## Theme F: Formation Energy and Thermodynamic Stability

Relevant to: mp_e_form, perovskites

---

### Seminal Paper 18: Miedema's Model for Alloy Formation Enthalpy

**Citation**: Miedema, A. R., de Chatel, P. F., and de Boer, F. R. "Cohesion in alloys -- fundamentals of a semi-empirical model." *Physica B+C* **100**(1), 1-28 (1980). DOI: 10.1016/0378-4363(80)90054-6

Earlier work:
- Miedema, A. R. "A simple model for alloys." *Phillips Technical Review* **33**, 149-160 (1973).

**Key contribution**: Developed a semi-empirical model for the enthalpy of formation of binary alloys based on two parameters: the electronegativity difference (Delta_phi*) and the electron density mismatch at the Wigner-Seitz cell boundary (Delta_n_ws^(1/3)). The model: Delta_H = f(c) * [-P*(Delta_phi*)^2 + Q*(Delta_n_ws^(1/3))^2 - R], where f(c) accounts for composition and surface area.

**Relevance to Matbench**: Miedema's model provides a physics-based estimate of mixing enthalpy that is computable from composition alone. For mp_e_form and perovskites tasks, Miedema-derived features could capture the chemical driving force for compound formation. The matminer library includes a Miedema featurizer.

**Key knowledge**: Miedema parameters (phi*, n_ws) are tabulated for all metallic elements. The model works well for metallic alloys but is less accurate for ionic/covalent compounds.

---

### Seminal Paper 19: Materials Project

**Citation**: Jain, A., Ong, S. P., Hautier, G., Chen, W., Richards, W. D., Dacek, S., Cholia, S., Gunter, D., Skinner, D., Ceder, G., and Persson, K. A. "Commentary: The Materials Project: A materials genome approach to accelerating materials innovation." *APL Materials* **1**(1), 011002 (2013). DOI: 10.1063/1.4812323

**Key contribution**: Established the Materials Project, a comprehensive open-access database of computed materials properties using high-throughput DFT. As of 2024, contains data for >150,000 inorganic compounds including formation energies, band gaps, elastic constants, dielectric properties, and more.

**Relevance to Matbench**: The Materials Project is the primary data source for 7 of the 13 Matbench tasks (mp_e_form, mp_gap, mp_is_metal, log_gvrh, log_kvrh, dielectric, phonons). Understanding the MP computation workflow (VASP with PBE, PAW pseudopotentials, standardized convergence criteria via pymatgen) is essential for understanding the data.

**Key knowledge**:
- All MP calculations use VASP with PBE functional
- PAW pseudopotentials with standard VASP POTCAR files
- Automatic structure relaxation to equilibrium geometry
- Elastic constants computed via finite-difference or DFPT
- Band gaps from standard PBE (known to underestimate)
- Formation energies referenced to elemental ground states (with MP corrections for certain elements)

---

## Theme G: Phonons and Lattice Dynamics

Relevant to: phonons

---

### Seminal Paper 20: Born-von Karman Lattice Dynamics

**Citation**: Born, M. and von Karman, T. "Uber Schwingungen in Raumgittern." *Physikalische Zeitschrift* **13**, 297-309 (1912).

And the comprehensive treatment:
- Born, M. and Huang, K. *Dynamical Theory of Crystal Lattices*. Oxford University Press, Oxford, 1954. ISBN: 978-0-19-850369-9.

**Key contribution**: Developed the theory of lattice dynamics based on the harmonic approximation. The vibrational frequencies of a crystal lattice are determined by the eigenvalues of the dynamical matrix, which depends on the force constants between atoms. This provides the theoretical basis for phonon dispersion relations and the phonon density of states.

**Relevance to Matbench**: The phonons task predicts the last (highest-frequency) peak in the phonon density of states. The Born-von Karman theory tells us this peak frequency depends on (1) force constants (bond stiffness, related to elastic moduli) and (2) atomic masses. The highest-frequency phonon mode is typically associated with the lightest atom vibrating against its nearest neighbors.

**Key equation**: omega_max ~ sqrt(k / m_reduced), where k is the interatomic force constant and m_reduced is the reduced mass of the vibrating atoms. For a simple diatomic crystal, omega_optical = sqrt(2*k*(1/m1 + 1/m2)).

**Hypotheses generated**:
- H30: The inverse square root of the lightest atomic mass in the structure will be strongly correlated with phonon peak frequency
- H31: Bond stiffness features (from elastic moduli or bond-valence parameters) divided by reduced mass will predict phonon peak frequency

---

### Seminal Paper 21: DFPT for Phonons

**Citation**: Baroni, S., de Gironcoli, S., Dal Corso, A., and Giannozzi, P. "Phonons and related crystal properties from density-functional perturbation theory." *Reviews of Modern Physics* **73**(2), 515-562 (2001). DOI: 10.1103/RevModPhys.73.515

**Key contribution**: Comprehensive review of density-functional perturbation theory (DFPT) for computing phonon dispersion relations, elastic constants, dielectric properties, and Born effective charges from first principles. DFPT is the method used to compute the phonon and dielectric data in the Materials Project.

**Relevance to Matbench**: The phonons and dielectric tasks use DFPT-calculated data. Understanding DFPT helps explain the accuracy and limitations of the training data.

---

## Theme H: Dielectric Properties and Optical Response

Relevant to: dielectric

---

### Seminal Paper 22: Clausius-Mossotti Relation

**Citation**: The Clausius-Mossotti relation was derived independently by:
- Mossotti, O. F. "Discussione analitica sull'influenza che l'azione di un mezzo dielettrico ha sulla distribuzione dell'elettricita alla superficie di piu corpi elettrici disseminati in esso." *Memorie di Matematica e di Fisica della Societa Italiana delle Scienze* **24**(2), 49-74 (1850).
- Clausius, R. *Die mechanische Warmetheorie, Vol. 2*. Vieweg, Braunschweig, 1879, pp. 62-97.

Modern treatment in Kittel (Ch. 13) and Ashcroft & Mermin (Ch. 27).

**Key contribution**: Related the macroscopic dielectric constant to the microscopic atomic polarizabilities: (epsilon - 1)/(epsilon + 2) = (N * alpha) / (3 * epsilon_0). This is the fundamental bridge between atomic-level properties and the dielectric response.

**Relevance to Matbench**: For the dielectric task, the Clausius-Mossotti relation suggests that atomic polarizability (tabulated for each element) weighted by stoichiometry and divided by unit cell volume should predict dielectric constant. This is one of the most direct composition-to-property links in the entire benchmark.

**Key equation**: (epsilon_r - 1)/(epsilon_r + 2) = (rho * N_A * alpha) / (3 * M * epsilon_0)

**Hypotheses generated**:
- H32: Sum of atomic polarizabilities divided by unit cell volume (Clausius-Mossotti-inspired) will be a top-3 feature for the dielectric task
- H33: The Clausius-Mossotti function (epsilon-1)/(epsilon+2) may be a better target transformation than raw epsilon for the dielectric task

---

### Seminal Paper 23: Lorentz-Lorenz and Refractive Index

**Citation**: The refractive index connection to polarizability:
- Lorenz, L. "Ueber die Refractionsconstante." *Annalen der Physik* **247**(9), 70-103 (1880).
- Lorentz, H. A. "Ueber die Beziehung zwischen der Fortpflanzungsgeschwindigkeit des Lichtes und der Korperdichte." *Annalen der Physik* **245**(4), 641-665 (1880).

**Key contribution**: The Lorentz-Lorenz equation relates refractive index to polarizability: (n^2 - 1)/(n^2 + 2) = (N * alpha) / (3 * epsilon_0). Since the Matbench dielectric task predicts refractive index n (not dielectric constant epsilon), and n^2 = epsilon for non-magnetic non-absorbing materials, the Lorentz-Lorenz equation is the directly relevant form.

**Relevance to Matbench**: The dielectric task target is the refractive index (the square root of the electronic dielectric constant). Features should be designed for n, not epsilon. The Lorentz-Lorenz relation suggests that polarizability per unit volume is the key descriptor.

---

## Theme I: 2D Materials and Exfoliation

Relevant to: jdft2d

---

### Seminal Paper 24: Graphene Isolation

**Citation**: Novoselov, K. S., Geim, A. K., Morozov, S. V., Jiang, D., Zhang, Y., Dubonos, S. V., Grigorieva, I. V., and Firsov, A. A. "Electric Field Effect in Atomically Thin Carbon Films." *Science* **306**(5696), 666-669 (2004). DOI: 10.1126/science.1102896

**Key contribution**: First experimental isolation and electronic characterization of graphene, a single layer of graphite. Demonstrated that 2D crystals are stable and exhibit remarkable electronic properties (high mobility, anomalous quantum Hall effect). Opened the field of 2D materials research. (Nobel Prize in Physics, 2010.)

**Relevance to Matbench**: The jdft2d task predicts exfoliation energy of 2D materials. Graphene's exfoliation energy (~20 meV/atom for graphite) is the reference point. The exfoliation energy measures the energy cost to separate a single layer from its bulk parent, which depends on the interlayer bonding (van der Waals for most 2D materials).

---

### Seminal Paper 25: Exfoliation Energy Calculations (JARVIS-DFT)

**Citation**: Choudhary, K., Kalish, I., Beams, R., and Tavazza, F. "High-throughput Identification and Characterization of Two-dimensional Materials using Density functional theory." *Scientific Reports* **7**, 5179 (2017). DOI: 10.1038/s41598-017-05402-0

**Key contribution**: Performed high-throughput DFT calculations of exfoliation energies for layered materials using the vdW-DF-optB88 functional (which captures van der Waals interactions that standard PBE misses). Identified hundreds of potentially exfoliable 2D materials.

**Relevance to Matbench**: This is the source of the jdft2d dataset. The data uses JARVIS-DFT calculations with a vdW-corrected functional. Understanding the calculation methodology explains the data distribution and potential feature relevance.

**Key knowledge**: Exfoliation energy depends on: (1) interlayer distance, (2) area of the unit cell in the layer plane, (3) strength of interlayer interactions (van der Waals, ionic, or mixed). Materials with purely vdW interlayer bonding (like graphite, MoS2) have low exfoliation energies (~10-30 meV/atom), while those with stronger interlayer interactions have higher values.

**Hypotheses generated**:
- H34: Interlayer distance extracted from structure will be the dominant feature for jdft2d
- H35: Features encoding the strength of van der Waals interactions (e.g., atomic polarizability of interlayer species) will improve jdft2d prediction

---

## Theme J: Yield Strength of Steels

Relevant to: steels

---

### Seminal Paper 26: Precipitation Hardening Theory

**Citation**: Orowan, E. "Discussion on Internal Stresses." In: *Symposium on Internal Stresses in Metals and Alloys*, Institute of Metals, London, pp. 451-453 (1948).

And the comprehensive treatment:
- Ardell, A. J. "Precipitation hardening." *Metallurgical Transactions A* **16**(12), 2131-2165 (1985). DOI: 10.1007/BF02670416

**Key contribution**: Orowan showed that the strength increase from hard precipitates scales as Delta_sigma = M * G * b / L, where G is shear modulus, b is Burgers vector, and L is the inter-precipitate spacing. This is the dominant strengthening mechanism in high-strength steels (maraging steels, precipitation-hardened stainless steels).

**Relevance to Matbench**: For matbench_steels, the Orowan mechanism means that the types and amounts of carbide/nitride/intermetallic forming elements (V, Nb, Ti, Mo, W) in the composition determine precipitate strengthening potential. Features encoding the total "precipitate-former content" should be predictive.

**Hypotheses generated**:
- H36: Sum of strong carbide/nitride former concentrations (V + Nb + Ti) will correlate with yield strength in the steels task
- H37: Carbon content and its interaction with carbide formers (e.g., C * (V + Nb)) may capture precipitation strengthening effects

---

### Seminal Paper 27: Strengthening Mechanisms in Steels -- Review

**Citation**: Bhadeshia, H. K. D. H. and Honeycombe, R. W. K. *Steels: Microstructure and Properties*, 4th Edition. Butterworth-Heinemann (Elsevier), Oxford, 2017. ISBN: 978-0-08-100270-4.

**Scope**: While technically a textbook, this is the definitive reference for understanding the relationship between steel composition, processing, microstructure, and properties. Covers all strengthening mechanisms: solid solution, precipitation, grain refinement, work hardening, and transformation strengthening (martensite, bainite).

### Relevant Chapters for matbench_steels

| Chapter | Topic | Feature Engineering Implication |
|---------|-------|---------------------------------|
| Ch. 2: Iron-Carbon Phase Diagram | Phase equilibria, carbon solubility | Carbon content as key feature |
| Ch. 5: Formation of Martensite | M_s temperature, martensite strength | M_s ~ 539 - 423*C - 30.4*Mn - 17.7*Ni - 12.1*Cr - 7.5*Si (Andrews formula) |
| Ch. 7: Precipitation Hardening | Carbide types (MC, M2C, M23C6, M7C3), strengthening | Type and amount of carbide formers |
| Ch. 10: Stainless Steels | Austenitic, ferritic, martensitic, duplex | Cr, Ni content determines steel class |
| Ch. 11: Maraging Steels | Ultra-high strength through intermetallic precipitation | Ni, Co, Mo, Ti content |
| Ch. 12: HSLA Steels | Microalloying with V, Nb, Ti | Microalloying element concentrations |

**Key equations for feature engineering**:
1. **Andrews' martensite start temperature**: M_s (C) = 539 - 423*C - 30.4*Mn - 17.7*Ni - 12.1*Cr - 7.5*Si (a linear model of composition!)
2. **Carbon equivalent**: CE = C + Mn/6 + (Cr+Mo+V)/5 + (Ni+Cu)/15. Summarizes weldability and hardenability.
3. **Cr equivalent / Ni equivalent**: For predicting phase stability (austenite vs ferrite vs martensite).

**Hypotheses generated**:
- H38: Andrews' M_s temperature formula applied to composition will be a strong predictor of yield strength (martensite is the strongest phase)
- H39: Carbon equivalent (CE) will capture overall strengthening potential
- H40: Separate features for austenite stabilizers (C, N, Mn, Ni) vs ferrite stabilizers (Cr, Mo, Si, V, Nb) will help distinguish steel classes

---

## Theme K: Band Gap Prediction and Metal/Non-Metal Classification

Relevant to: mp_gap, mp_is_metal, expt_gap, expt_is_metal

---

### Seminal Paper 28: Electronegativity and Band Gap

**Citation**: Phillips, J. C. "Ionicity of the Chemical Bond in Crystals." *Reviews of Modern Physics* **42**(3), 317-356 (1970). DOI: 10.1103/RevModPhys.42.317

**Key contribution**: Developed a dielectric theory of chemical bonding in crystals that separates the band gap into covalent (E_h, homopolar) and ionic (C, charge transfer) contributions: E_g^2 = E_h^2 + C^2. Defined the Phillips ionicity f_i = C^2 / E_g^2. This provides a physical basis for predicting band gaps from atomic properties.

**Relevance to Matbench**: The Phillips ionicity framework suggests that band gap depends on electronegativity difference (ionic component) and bond length (covalent component). Features encoding both will be important for mp_gap, expt_gap, and metallic classification.

**Key equation**: E_g = sqrt(E_h^2 + C^2), where E_h ~ d^(-2.5) and C ~ electronegativity difference.

---

### Seminal Paper 29: Zunger's Structural Map

**Citation**: Zunger, A. "Systematization of the stable crystal structure of all AB-type binary compounds: A pseudopotential orbital-radii approach." *Physical Review B* **22**(12), 5839-5872 (1980). DOI: 10.1103/PhysRevB.22.5839

**Key contribution**: Showed that crystal structure types can be separated in a 2D map using orbital radii (r_s, r_p) as coordinates. Different structure types (rock salt, zinc blende, wurtzite, etc.) occupy distinct regions. This demonstrates that atomic properties alone can predict crystal structure.

**Relevance to Matbench**: Zunger's orbital radii capture the essential chemistry. The concept generalizes: orbital radii differences between constituent atoms predict structure type, which in turn affects band gap, elastic properties, and formation energy. Orbital radii are among the most powerful elemental descriptors for ML.

**Hypotheses generated**:
- H41: Zunger's orbital radii (r_s, r_p, r_d) or their differences between elements will be strong composition-based features for structure prediction and property prediction
- H42: Features encoding the expected crystal structure type (from orbital radii maps) may help all structure-dependent tasks

---

### Seminal Paper 30: Empirical Rules for Band Gap

**Citation**: Duffy, J. A. "Ultraviolet transparency of glass: A chemical approach in terms of band theory, polarisability and electronegativity." *Physics and Chemistry of Glasses* **42**(3), 151-157 (2001).

And the comprehensive empirical study:
- Zhuo, Y., Mansouri Tehrani, A., and Brgoch, J. "Predicting the Band Gaps of Inorganic Solids by Machine Learning." *The Journal of Physical Chemistry Letters* **9**(7), 1668-1673 (2018). DOI: 10.1021/acs.jpclett.8b00124

**Key contribution**: Zhuo et al. showed that machine learning with composition-based features (Magpie-type: elemental properties statistics) can predict experimental band gaps with MAE ~ 0.45 eV. Key features included average electronegativity, average atomic number, and the range of first ionization energy across constituent elements.

**Relevance to Matbench**: This paper directly addresses the expt_gap task methodology. Their best features serve as a starting point for feature engineering. Their MAE of 0.45 eV is close to the current expt_gap leaderboard, suggesting that composition-based features capture most of the predictable variance.

**Key features identified**: Average electronegativity, range of electronegativity, average/range of ionic radius, mean first ionization energy, mean atomic number, average covalent radius, fraction of d-block elements.

---

# SUMMARY OF HYPOTHESES GENERATED

| ID | Hypothesis | Source | Relevant Task(s) |
|----|-----------|--------|-------------------|
| H1 | Clausius-Mossotti polarizability features improve dielectric prediction | Kittel Ch. 13 | dielectric |
| H2 | Debye temperature from mass/bond-strength correlates with phonon peak | Kittel Ch. 5 | phonons |
| H3 | Electronegativity difference features predict band gap | Kittel Ch. 7 | mp_gap, expt_gap |
| H4 | Penn model (plasma_freq^2/gap^2) predicts dielectric constant | Ashcroft Ch. 27 | dielectric |
| H5 | Coordination number + bond length hopping → metallic character | Ashcroft Ch. 10 | mp_is_metal, expt_is_metal |
| H6 | DFT-convention valence electron counts may differ from standard | Martin Ch. 14 | All DFT tasks |
| H7 | Experimental gap features should NOT be used directly for PBE gap | Martin Ch. 8 | mp_gap |
| H8 | Atomic size mismatch features improve steels prediction | Callister Ch. 7 | steels |
| H9 | Weighted-average elemental moduli as baseline for log_gvrh/kvrh | Callister Ch. 15 | log_gvrh, log_kvrh |
| H10 | Electronegativity diff. + radius ratio predict formation energy | Callister Ch. 2 | mp_e_form, perovskites |
| H11 | d-electron count captures stacking fault energy effects | Haasen Ch. 10 | steels, log_gvrh, log_kvrh |
| H12 | Crystal structure type features important for elastic moduli | Haasen Ch. 1-3 | log_gvrh, log_kvrh |
| H13 | Configurational entropy improves GFA prediction | Porter Ch. 1 | glass |
| H14 | Liquidus temperature + Tg proxy → strong GFA features | Porter Ch. 4 | glass |
| H15 | Miedema mixing enthalpy correlates with formation energy and GFA | Porter Ch. 1 | mp_e_form, glass |
| H16 | Inoue's 3 rules encoded as features → top GFA predictors | Shelby Ch. 3 | glass |
| H17 | Atomic size dispersion (std/mean of radii) → strong GFA predictor | Shelby Ch. 3 | glass |
| H18 | Miedema model enthalpy predicts formation energy | DeHoff Ch. 10 | mp_e_form, perovskites |
| H19 | Born-Haber cycle components improve mp_e_form | DeHoff Ch. 10 | mp_e_form |
| H20 | Penn model features among top 3 for dielectric task | Yu Ch. 6 | dielectric |
| H21 | Moss/Ravindra relation links gap and n → joint modeling | Yu Ch. 6 | dielectric, mp_gap |
| H22 | Phillips ionicity captures ionic/covalent character | Yu Ch. 2 | mp_gap, mp_e_form |
| H23 | Cohen's d^(-3.5) scaling → top feature for log_kvrh | Cohen 1985 | log_kvrh |
| H24 | Ionicity-corrected bond length outperforms raw bond length | Cohen 1985 | log_gvrh, log_kvrh |
| H25 | Fleischer-Labusch misfit features improve steels | Fleischer 1963 | steels |
| H26 | sqrt(total alloy content) useful for steels | Fleischer 1963 | steels |
| H27 | Goldschmidt tolerance factor → top 3 for perovskites | Goldschmidt 1926 | perovskites |
| H28 | Octahedral factor mu = r_B/r_X complementary to tolerance factor | Goldschmidt 1926 | perovskites |
| H29 | Bartel tolerance factor outperforms Goldschmidt | Bartel 2019 | perovskites |
| H30 | Inverse sqrt of lightest mass correlates with phonon peak | Born 1912 | phonons |
| H31 | Bond stiffness / reduced mass predicts phonon peak | Born 1912 | phonons |
| H32 | Polarizability / volume → top 3 for dielectric | Clausius-Mossotti | dielectric |
| H33 | (epsilon-1)/(epsilon+2) better target transform than raw epsilon | Clausius-Mossotti | dielectric |
| H34 | Interlayer distance dominant for jdft2d | Novoselov 2004 | jdft2d |
| H35 | Atomic polarizability of interlayer species → jdft2d | Choudhary 2017 | jdft2d |
| H36 | Sum of carbide formers (V+Nb+Ti) → steels yield strength | Orowan 1948 | steels |
| H37 | C * (V+Nb) interaction → precipitation strengthening | Orowan 1948 | steels |
| H38 | Andrews M_s formula → strong yield strength predictor | Bhadeshia 2017 | steels |
| H39 | Carbon equivalent → overall strengthening potential | Bhadeshia 2017 | steels |
| H40 | Austenite vs ferrite stabilizer features | Bhadeshia 2017 | steels |
| H41 | Zunger orbital radii as composition features | Zunger 1980 | All tasks |
| H42 | Expected crystal structure type from orbital radii | Zunger 1980 | All structure tasks |

---
---

# PART 2: ML METHODS, REVIEWS, FEATURES, AND TASK-SPECIFIC PAPERS

*106 papers covering review articles, ML model papers, feature engineering papers, and task-specific property prediction papers. Full detailed entries in `literature/matbench_lit_review_part2.md`.*

---

## Theme 5: Review Papers on ML for Materials Science (15 papers)

### Review 1: Schmidt et al. (2019) -- "Recent advances and applications of machine learning in solid-state materials science"
**Citation**: Schmidt, J., Marques, M.R.G., Botti, S., & Marques, M.A.L. npj Computational Materials, 5, 83 (2019). DOI: 10.1038/s41524-019-0221-0
**Key findings**: Surveys ~200 papers. Identifies representation/descriptors as most critical step. Kernel methods and neural networks dominate for property prediction. Lack of standardized benchmarks hampers fair comparison.
**Features discussed**: Coulomb matrix, SOAP, hand-crafted composition features
**Knowledge extracted**: K43: Descriptor choice matters more than model choice for small-medium datasets

### Review 2: Chen et al. (2020) -- "A Critical Review of Machine Learning of Energy Materials"
**Citation**: Chen, C., Zuo, Y., Ye, W., Li, X., Deng, Z., & Ong, S.P. Advanced Energy Materials, 10(8), 1903242 (2020). DOI: 10.1002/aenm.201903242
**Key findings**: Reviews >300 papers. Identifies three generations of descriptors: hand-crafted, learned, universal. GNNs emerging as dominant paradigm for structure-property prediction.
**Knowledge extracted**: K44: GNNs represent the "third generation" of materials ML representations

### Review 3: Choudhary et al. (2022) -- "Recent advances and applications of deep learning methods in materials science"
**Citation**: Choudhary, K. et al. npj Computational Materials, 8, 59 (2022). DOI: 10.1038/s41524-022-00734-6
**Key findings**: Comprehensive review covering GNNs (CGCNN, MEGNet, SchNet, ALIGNN), generative models, NLP approaches. Message-passing GNNs achieve SOTA on structure tasks.
**Knowledge extracted**: K45: Angular information (bond angles) provides ~10-20% improvement over distance-only GNNs

### Review 4: Reiser et al. (2022) -- "Graph neural networks for materials science and chemistry"
**Citation**: Reiser, P. et al. Communications Materials, 3, 93 (2022). DOI: 10.1038/s43246-022-00315-6
**Key findings**: Categorizes GNNs by symmetry: invariant (SchNet, CGCNN), equivariant (NequIP, MACE), higher-order (DimeNet, GemNet). Including 3-body interactions significantly improves accuracy.
**Knowledge extracted**: K46: Equivariant GNNs preserve physical symmetries -- important for vector/tensor properties

### Review 5: Fung et al. (2021) -- "Benchmarking graph neural networks for materials chemistry"
**Citation**: Fung, V. et al. npj Computational Materials, 7, 84 (2021). DOI: 10.1038/s41524-021-00554-0
**Key findings**: Systematically benchmarks CGCNN, MEGNet, SchNet, MPNN on MP data. SchNet generally outperforms on energy tasks. Model performance varies significantly across property types.
**Knowledge extracted**: K47: No single GNN dominates across all property types -- task-specific tuning matters

### Review 6: Murdock et al. (2020) -- "Is domain knowledge necessary for ML in materials science?"
**Citation**: Murdock, R.J. et al. IMMI, 9, 221-227 (2020). DOI: 10.1007/s40192-020-00179-z
**Key findings**: Domain-informed features (Magpie) consistently outperform raw element fractions on composition-only tasks. Domain knowledge important for small-medium datasets; less critical for very large datasets where deep learning can learn representations.
**Knowledge extracted**: K48: For composition tasks with <10k samples, Magpie features > raw element fractions

### Review 7: Butler et al. (2018) -- "Machine learning for molecular and materials science" (Nature)
**Citation**: Butler, K.T. et al. Nature, 559, 547-555 (2018). DOI: 10.1038/s41586-018-0337-2
**Key findings**: High-impact review emphasizing representation as key bottleneck. Argues for uncertainty quantification. Ensemble methods and Gaussian processes provide natural uncertainty estimates.
**Knowledge extracted**: K49: Uncertainty quantification is critical for materials discovery but often neglected

### Review 8: Himanen et al. (2019) -- "Data-driven materials science: status, challenges, perspectives"
**Citation**: Himanen, L. et al. Advanced Science, 6(21), 1900808 (2019). DOI: 10.1002/advs.201900808
**Key findings**: Identifies 4 descriptor families: global (Coulomb matrix), local (SOAP, ACSF), graph-based (CGCNN), composition-based (Magpie). No single family dominates across all tasks.
**Knowledge extracted**: K50: Combining descriptors from different families can improve performance

### Review 9: Morgan & Jacobs (2020) -- "Opportunities and challenges for ML in materials science"
**Citation**: Morgan, D. & Jacobs, R. Annu. Rev. Mater. Res., 50, 71-103 (2020). DOI: 10.1146/annurev-matsci-070218-010015
**Key findings**: Domain knowledge should be embedded in features rather than learned from data for small datasets (<10k). Provides guidelines for when different model types are appropriate.
**Knowledge extracted**: K51: For datasets <1k samples, simple models (Ridge, RF) often match or beat deep learning

### Review 10: Bartel (2022) -- "Review of computational approaches to predict thermodynamic stability"
**Citation**: Bartel, C.J. J. Mater. Sci., 57, 10475-10498 (2022). DOI: 10.1007/s10853-022-06915-4
**Key findings**: Compares composition-only models (Roost, CrabNet) with structure-based models (CGCNN, MEGNet). Structure information provides 2-5x improvement for formation energy prediction.
**Knowledge extracted**: K52: Structure features provide 2-5x improvement over composition-only for formation energy

### Review 11: Jain et al. (2016) -- "Computational predictions of energy materials using DFT"
**Citation**: Jain, A. et al. Nature Reviews Materials, 1, 15004 (2016). DOI: 10.1038/natrevmats.2015.4
**Key findings**: DFT accuracy benchmarks: formation energies ~0.1 eV/atom, band gaps underestimated by ~40%, elastic constants ~10% error. Critical for understanding Matbench target noise.
**Knowledge extracted**: K53: DFT noise floor: ~0.02 eV/atom (formation energy), ~0.3 eV (band gap), ~5 GPa (elastic moduli)

### Review 12: Schleder et al. (2019) -- "From DFT to machine learning: recent approaches to materials science"
**Citation**: Schleder, G.R. et al. J. Phys.: Mater., 2(3), 032001 (2019). DOI: 10.1088/2515-7639/ab084b
**Key findings**: Reviews pipeline from DFT to ML. DFT data quality affects ML model ceilings. Proper cross-validation critical; data leakage common in materials science.

### Review 13: Liu et al. (2017) -- "Materials discovery and design using machine learning"
**Citation**: Liu, Y. et al. J. Materiomics, 3(3), 159-177 (2017). DOI: 10.1016/j.jmat.2017.08.002
**Key findings**: Early comprehensive review. Covers one-hot encoding, physicochemical descriptors, orbital-based features. RF and SVM most commonly used at the time.

### Review 14: Merchant et al. (2023) -- "Scaling deep learning for materials discovery" (Nature/GNoME)
**Citation**: Merchant, A. et al. Nature, 624, 80-85 (2023). DOI: 10.1038/s41586-023-06735-9
**Key findings**: Google DeepMind GNoME: GNNs predict stability of 2.2M new materials. Scaling training data and model size dramatically improves predictions.
**Knowledge extracted**: K54: Scaling laws exist for materials GNNs -- more data consistently improves performance

### Review 15: Xie et al. (2023) -- "Ultra-fast interpretable machine-learning potentials"
**Citation**: Xie, S.R. et al. npj Computational Materials, 9, 162 (2023). DOI: 10.1038/s41524-023-01092-7
**Key findings**: Interpretable features (SOAP) provide insight that black-box GNNs cannot. Interpretability matters for scientific discovery.

---

## Theme 6: ML Model Papers -- Graph Neural Networks (16 papers)

### Model 1: coGN -- Connectivity Optimized Graph Network (Rank #1 on Matbench)
**Citation**: Ruff, R., Reiser, P., Stuhmer, J., & Friederich, P. Digital Discovery, 3, 862-872 (2024). DOI: 10.1039/D3DD00194F
**Key findings**: Nested graph representations separating atom, bond, and angle interactions. Voronoi-based edge sets instead of distance cutoffs. 0.0170 eV/atom MAE on mp_e_form. #1 on all structure tasks.
**Features discussed**: Voronoi connectivity, distance bins (32), atomic mass/radius embeddings
**Matbench tasks**: All 9 structure tasks

### Model 2: ALIGNN -- Atomistic Line Graph Neural Network
**Citation**: Choudhary, K. & DeCost, B. npj Computational Materials, 7, 185 (2021). DOI: 10.1038/s41524-021-00650-1
**Key findings**: Line graph (bond-to-bond adjacency) encodes bond angles. Alternating message passing on atom graph and line graph. 0.022 eV/atom on formation energy. Explicit angle encoding outperforms distance-only GNNs.
**Features discussed**: CGCNN atom features, line graph for angular encoding, 8.0A cutoff
**Matbench tasks**: All 9 structure tasks

### Model 3: SchNet -- Continuous-Filter Convolutions
**Citation**: Schutt, K.T. et al. NeurIPS 30, 991-1001 (2017); J. Chem. Phys. 148, 241722 (2018). DOI: 10.1063/1.5019779
**Key findings**: Continuous-filter convolutions using radial basis functions as distance-dependent filter weights. Naturally handles varying coordination environments. Extended to periodic crystals.
**Features discussed**: Gaussian distance expansions, radial basis functions
**Matbench tasks**: All structure tasks (via kgcnn)

### Model 4: DimeNet / DimeNet++ -- Directional Message Passing
**Citation**: Gasteiger, J. et al. ICLR 2020; arXiv:2011.14115 (2020)
**Key findings**: Directional message passing incorporating bond angles. DimeNet++ reduces cost by ~8x while maintaining accuracy. 2D spherical Bessel basis for distance and angle embeddings.
**Features discussed**: Bond angles, spherical Bessel basis, directional messages
**Matbench tasks**: Structure tasks (via kgcnn)

### Model 5: MEGNet -- Graph Networks for Molecules and Crystals
**Citation**: Chen, C. et al. Chemistry of Materials, 31(9), 3564-3572 (2019). DOI: 10.1021/acs.chemmater.9b01294
**Key findings**: Extends DeepMind's graph network framework to periodic crystals. Uses node (atom), edge (bond), and global state vectors. Pre-trained on ~60k MP structures. 0.028 eV/atom formation energy, 0.33 eV band gap.
**Features discussed**: Gaussian distance expansion, element embeddings, global state vector
**Matbench tasks**: All structure tasks (Matbench baseline model)

### Model 6: CGCNN -- Crystal Graph Convolutional Neural Network
**Citation**: Xie, T. & Grossman, J.C. Physical Review Letters, 120, 145301 (2018). DOI: 10.1103/PhysRevLett.120.145301
**Key findings**: First GNN for crystal property prediction. Graph from crystal structure using distance cutoff. One-hot element embeddings + Gaussian distances. Interpretable via attention weights.
**Features discussed**: One-hot element features (92-dim), Gaussian-expanded distances, 8A cutoff
**Matbench tasks**: All structure tasks (Matbench baseline model)

### Model 7: DeeperGATGNN -- Scalable Deeper Graph Neural Networks
**Citation**: Omee, S.S. et al. Patterns, 3(5), 100491 (2022). DOI: 10.1016/j.patter.2022.100491
**Key findings**: Differentiable group normalization + skip connections enable 30+ layer GNNs. Competitive with ALIGNN on Matbench, 0.169 eV MAE on mp_gap.
**Matbench tasks**: All 9 structure tasks

### Model 8: iCGCNN -- Improved CGCNN
**Citation**: Park, C.W. & Wolverton, C. Physical Review Materials, 4, 063801 (2020). DOI: 10.1103/PhysRevMaterials.4.063801
**Key findings**: Adds Voronoi-based neighbor identification and global state features. ~30% improvement over original CGCNN on formation energy.
**Matbench tasks**: mp_e_form, mp_gap, log_gvrh, log_kvrh

### Model 9: GATGNN -- Graph Attention Networks for Materials
**Citation**: Louis, S.Y. et al. PCCP, 22, 18141-18148 (2020). DOI: 10.1039/D0CP01474E
**Key findings**: Multi-headed attention + global attention pooling for crystal GNNs. Attention learns neighbor importance per property. Improved over CGCNN on band gap.
**Matbench tasks**: mp_gap, mp_e_form, dielectric

### Model 10: M3GNet -- Universal Interatomic Potential
**Citation**: Chen, C. & Ong, S.P. Nature Computational Science, 2, 718-728 (2022). DOI: 10.1038/s43588-022-00349-3
**Key findings**: Universal graph deep learning interatomic potential for entire periodic table. Trained on MP energies, forces, stresses. Can predict formation energy, relax structures, run MD.
**Matbench tasks**: mp_e_form (indirectly), structure relaxation for all structure tasks

### Model 11: MACE -- Higher Order Equivariant Message Passing
**Citation**: Batatia, I. et al. NeurIPS 35, 11423-11436 (2022)
**Key findings**: Higher-order equivariant message passing with ACE basis. Foundation model MACE-MP-0 trained on MP achieves broad applicability. Preserves physical symmetries.
**Matbench tasks**: Structure tasks via universal potential approach

### Model 12: CHGNet -- Charge-Informed Neural Network Potential
**Citation**: Deng, B. et al. Nature Machine Intelligence, 5, 1031-1041 (2023). DOI: 10.1038/s42256-023-00716-3
**Key findings**: Explicitly models magnetic moments and charge states. Pretrained on MP trajectories. Charge decoration improves transition metal oxide handling.
**Matbench tasks**: mp_e_form, mp_is_metal, perovskites

### Model 13: GNoME (revisited as model)
**Citation**: Merchant, A. et al. Nature, 624, 80-85 (2023). DOI: 10.1038/s41586-023-06735-9
**Key findings**: Graph network predicting stability of 2.2M new materials. Demonstrates scaling laws for materials GNNs.

### Model 14: Data Augmentation for GNNs
**Citation**: Gibson, J. et al. npj Computational Materials, 8, 211 (2022). DOI: 10.1038/s41524-022-00891-8
**Key findings**: Augmentation by perturbing atomic positions improves GNN robustness for imperfect input structures.

### Model 15: ALIGNN-FF -- Universal Force Field
**Citation**: Choudhary, K. et al. Digital Discovery, 2, 346-355 (2022). DOI: 10.1039/D2DD00096B
**Key findings**: Extends ALIGNN to universal force-field. Pre-trained ALIGNN-FF achieves competitive property prediction through fine-tuning on small datasets.
**Matbench tasks**: All structure tasks via pre-training

### Model 16: AtomSets -- Hierarchical Transfer Learning
**Citation**: Chen, C. & Ong, S.P. npj Computational Materials, 7, 173 (2021). DOI: 10.1038/s41524-021-00639-w
**Key findings**: DeepSets architecture with attention. Hierarchical transfer: pre-train on large dataset, fine-tune on small. Significant improvements on small Matbench tasks (steels, jdft2d).
**Matbench tasks**: All tasks, especially small-data tasks

---

## Theme 7: ML Model Papers -- Composition-Based and Feature-Based (10 papers)

### Model 17: MODNet -- Materials Optimal Descriptor Network
**Citation**: De Breuck, P.P. et al. npj Computational Materials, 7, 83 (2021). DOI: 10.1038/s41524-021-00552-2
**Key findings**: NMI-based feature selection from matminer descriptors. Selects ~100-300 optimal features from thousands. Joint learning (multi-target) improves small dataset performance. Only top-tier model completing all 13 Matbench tasks.
**Features discussed**: All matminer features, NMI relevance-redundancy selection, joint learning targets
**Hypotheses generated**: H43: NMI feature selection will identify a sparse, high-quality feature subset for each task

### Model 18: MODNet extended analysis
**Citation**: De Breuck, P.P. et al. J. Phys.: Condens. Matter, 33(40), 404002 (2021). DOI: 10.1088/1361-648X/ac1f8a
**Key findings**: NMI selection identifies physically meaningful features. Handles data imbalance through proper weighting. Detailed analysis of all 13 Matbench tasks.

### Model 19: CrabNet -- Compositionally Restricted Attention-Based Network
**Citation**: Wang, A.Y. et al. npj Computational Materials, 7, 77 (2021). DOI: 10.1038/s41524-021-00545-1
**Key findings**: Self-attention (transformer) on elemental compositions. Elements embedded and weighted by stoichiometric fraction. Multi-headed attention learns element-element interactions. With Ax/SAASBO optimization, 0.331 eV on expt_gap.
**Features discussed**: Learned element embeddings, stoichiometric fractional weighting, attention weights
**Matbench tasks**: Composition tasks

### Model 20: Roost -- Representation Learning from Stoichiometry
**Citation**: Goodall, R.E.A. & Lee, A.A. Nature Communications, 11, 6280 (2020). DOI: 10.1038/s41467-020-19964-7
**Key findings**: Graph from composition where nodes are elements, edges connect all pairs. Message passing learns composition representations. Composition-only model achieves ~0.1 eV/atom on formation energy (surprisingly good without structure).
**Features discussed**: Learned element embeddings, composition graph, message passing on element pairs
**Matbench tasks**: Composition tasks, mp_e_form (composition baseline)

### Model 21: ElemNet -- Deep Learning from Elemental Composition
**Citation**: Jha, D. et al. Scientific Reports, 8, 17593 (2018). DOI: 10.1038/s41598-018-35934-y
**Key findings**: 17-layer deep NN taking raw element fractions as input. Discovers composition-property relationships without domain-specific features. Typically underperforms feature-engineered approaches on small datasets.
**Features discussed**: Raw element fractions (86-dim), no hand-crafted features
**Matbench tasks**: Composition tasks

### Model 22: IRNet -- Deep Residual Regression
**Citation**: Jha, D. et al. KDD 2019, 2385-2393. DOI: 10.1145/3292500.3330691
**Key findings**: Extends ElemNet with residual connections. Residual networks learn more transferable features.
**Matbench tasks**: Composition tasks

### Model 23: mat2vec -- Word Embeddings from Materials Literature
**Citation**: Tshitoyan, V. et al. Nature, 571, 95-98 (2019). DOI: 10.1038/s41586-019-1335-8
**Key findings**: Word2Vec-style embeddings from 3.3M materials science abstracts. Element embeddings capture chemical similarity. Can predict thermoelectric materials before experimental discovery. Available as "matscholar_el" preset in matminer.
**Features discussed**: 200-dim element embeddings, composition-weighted mean/std
**Matbench tasks**: Composition tasks (via matscholar_el preset)

### Model 24: SkipAtom -- Structure-Derived Element Embeddings
**Citation**: Antunes, L.M. et al. npj Computational Materials, 8, 44 (2022). DOI: 10.1038/s41524-022-00729-3
**Key findings**: Skip-gram on crystal structure "sentences" (random walks on crystal graphs). Element embeddings encode structural chemistry. Competitive with Magpie on property prediction.
**Features discussed**: Skip-gram element embeddings (100-dim), composition statistics
**Matbench tasks**: Composition tasks

### Model 25: Automatminer / AMMExpress (Matbench Reference)
**Citation**: Dunn, A. et al. npj Computational Materials, 6, 138 (2020). DOI: 10.1038/s41524-020-00406-3
**Key findings**: THE Matbench paper. AutoML pipeline: matminer featurization -> feature reduction -> TPOT. Best on 8/13 tasks when published. Tree-based AutoML competitive with GNNs on small/medium tasks.
**Features discussed**: All matminer features, correlation-based reduction, TPOT-evolved pipeline
**Matbench tasks**: All 13 tasks

### Model 26: TPOT -- Tree-based Pipeline Optimization
**Citation**: Olson, R.S. et al. GECCO 2016, 485-492. DOI: 10.1145/2908812.2908918
**Key findings**: Genetic programming evolves sklearn pipelines. Typically evolves gradient boosting or random forest as final estimator.
**Matbench tasks**: All tasks (via Automatminer)

---

## Theme 8: Feature Engineering and Descriptor Papers (25 papers)

### Feature 1: Magpie Features -- THE Standard Composition Descriptor
**Citation**: Ward, L. et al. npj Computational Materials, 2, 16028 (2016). DOI: 10.1038/npjcompumats.2016.28
**Key findings**: 132 features from composition: statistics (mean, std, min, max, range, mode) of 22 elemental properties. RF+Magpie achieves strong baselines across diverse tasks. Most widely used feature set in materials ML.
**Features discussed**: Magpie statistics of electronegativity, atomic radius, melting point, molar volume, thermal conductivity, etc. (22 properties x 6 statistics)
**Knowledge extracted**: K55: Magpie features are the composition-feature gold standard -- always include as baseline

### Feature 2: matminer -- Materials Data Mining Toolkit
**Citation**: Ward, L. et al. Computational Materials Science, 152, 60-69 (2018). DOI: 10.1016/j.commatsci.2018.05.018
**Key findings**: 44 featurizer classes generating thousands of descriptors. Organized by input type. Integrates with Materials Project API.
**Features discussed**: ElementProperty, Stoichiometry, BandCenter, SineCoulombMatrix, OFM, DensityFeatures, GlobalSymmetryFeatures, VoronoiFingerprint, etc.
**Knowledge extracted**: K56: matminer is the canonical featurization library for Matbench

### Feature 3: Coulomb Matrix
**Citation**: Rupp, M. et al. Physical Review Letters, 108, 058301 (2012). DOI: 10.1103/PhysRevLett.108.058301
**Key findings**: C_ij = Z_i*Z_j/|R_i-R_j| for i!=j; C_ii = 0.5*Z_i^2.4. Sorted eigenvalue representation ensures permutation invariance. Foundation for structural descriptors.
**Features discussed**: Coulomb matrix elements, sorted eigenvalues
**Matbench tasks**: Structure tasks

### Feature 4: SOAP -- Smooth Overlap of Atomic Positions
**Citation**: Bartok, A.P. et al. Physical Review B, 87, 184115 (2013). DOI: 10.1103/PhysRevB.87.184115
**Key findings**: Encodes local atomic environments using radial basis + spherical harmonics. Provably complete for distinguishing different local environments. Best hand-crafted descriptor per Lam et al. (2023) benchmarks.
**Features discussed**: SOAP power spectrum, radial cutoff, angular channels, species channels
**Knowledge extracted**: K57: SOAP descriptors outperform other hand-crafted structure descriptors for tabular ML

### Feature 5: Atom-Centered Symmetry Functions (ACSF)
**Citation**: Behler, J. J. Chem. Phys., 134, 074106 (2011). DOI: 10.1063/1.3553717
**Key findings**: G2 radial (neighbor distance) and G4/G5 angular (triplet angle) symmetry functions. Foundation for Behler-Parrinello neural network potentials.
**Features discussed**: G2 parameters (eta, Rs), G4/G5 parameters (eta, lambda, zeta)
**Matbench tasks**: Structure tasks

### Feature 6: Sine Coulomb Matrix (for periodic crystals)
**Citation**: Faber, F.A. et al. Physical Review Letters, 117, 135502 (2016). DOI: 10.1103/PhysRevLett.117.135502
**Key findings**: Adapts Coulomb matrix for periodic boundary conditions using sine function. Part of the RF-SCM/Magpie baseline in Matbench.
**Features discussed**: Sine Coulomb Matrix: sin(pi*r_ij/L) for periodicity
**Matbench tasks**: All structure tasks (in RF-SCM/Magpie baseline)

### Feature 7: Orbital Field Matrix (OFM)
**Citation**: Pham, T.L. et al. Sci. Technol. Adv. Mater., 18(1), 756-765 (2017). DOI: 10.1080/14686996.2017.1378060
**Key findings**: Encodes orbital-orbital interactions between neighboring atoms. Captures bonding character (ionic vs. covalent) missed by simpler descriptors.
**Features discussed**: OFM: s-s, s-p, s-d, p-p, p-d, d-d interaction statistics

### Feature 8: Voronoi Tessellation Features
**Citation**: Ward, L. et al. Physical Review B, 96, 024104 (2017). DOI: 10.1103/PhysRevB.96.024104
**Key findings**: Statistics of Voronoi cell properties: face areas, bond distances, coordination numbers, local ordering. Adding to Magpie features improves formation energy from 0.12 to 0.08 eV/atom (33% improvement).
**Features discussed**: Mean/std of coordination number, bond length, face area, volume; chemical ordering
**Knowledge extracted**: K58: Voronoi features provide ~33% improvement on formation energy over composition-only

### Feature 9: Oliynyk Elemental Properties
**Citation**: Oliynyk, A.O. et al. Chemistry of Materials, 28(20), 7324-7331 (2016). DOI: 10.1021/acs.chemmater.6b02724
**Key findings**: 44 elemental properties optimized for intermetallic compounds. Emphasis on metallic bonding descriptors. Distinct from Magpie.
**Features discussed**: Mendeleev number, orbital radii, metallic electronegativity, heat of fusion
**Knowledge extracted**: K59: Oliynyk features better than Magpie for metallic systems (steels, glass)

### Feature 10: Yang Omega and Delta Parameters
**Citation**: Yang, X. & Zhang, Y. Mater. Chem. Phys., 132, 233-238 (2012). DOI: 10.1016/j.matchemphys.2011.11.021
**Key findings**: Omega = Tm_mix*dSmix/|dHmix| (thermodynamic parameter). Delta = sqrt(sum(ci*(1-ri/ravg)^2)) (atomic size mismatch). Key features for solid solution and glass stability prediction.
**Features discussed**: Omega, delta, lambda (atomic packing mismatch)
**Knowledge extracted**: K60: Yang delta parameter is the single best predictor for glass-forming ability

### Feature 11: Meredig Feature Set
**Citation**: Meredig, B. et al. Physical Review B, 89, 094104 (2014). DOI: 10.1103/PhysRevB.89.094104
**Key findings**: Composition-weighted averages of elemental properties + Boolean element indicators. 22 weighted features + element fractions. Enables rapid screening of millions of compositions.
**Features discussed**: Weighted averages of electronegativity, radius, etc.

### Feature 12: DEML Feature Set
**Citation**: Deml, A.M. et al. Physical Review B, 93, 085142 (2016). DOI: 10.1103/PhysRevB.93.085142
**Key findings**: Thermochemical feature set using DFT elemental energies, ionization energies, electron affinities, Miedema parameters. Particularly good for formation energy prediction.
**Features discussed**: Thermochemical properties, Miedema parameters, DFT elemental energies
**Knowledge extracted**: K61: DEML features particularly strong for formation energy (thermochemically motivated)

### Feature 13: Miedema Model Parameters
**Citation**: Miedema, A.R. et al. Physica B+C, 100(1), 1-28 (1980). DOI: 10.1016/0378-4363(80)90054-6
**Key findings**: Semi-empirical alloy formation enthalpy model using electron density mismatch (Delta_n_WS) and electronegativity difference (Delta_phi).
**Features discussed**: n_WS (Wigner-Seitz electron density), phi (work function)
**Knowledge extracted**: K62: Miedema enthalpy can be directly computed from composition as a feature

### Feature 14: Goldschmidt Tolerance Factor
**Citation**: Goldschmidt, V.M. Die Naturwissenschaften, 14, 477-485 (1926). DOI: 10.1007/BF01507527
**Key findings**: t = (rA + rO) / (sqrt(2)*(rB + rO)) for perovskites. 0.8 < t < 1.0 indicates stability. Single best predictor for perovskite stability.

### Feature 15: Bartel Tolerance Factor (improved)
**Citation**: Bartel, C.J. et al. Science Advances, 5(2), eaav0693 (2019). DOI: 10.1126/sciadv.aav0693
**Key findings**: Improved tolerance factor tau outperforms Goldschmidt (92% vs 74% accuracy for perovskite classification). Derived using SISSO.
**Knowledge extracted**: K63: Bartel tau factor should replace Goldschmidt t for perovskite tasks

### Feature 16: Local Structure Order Parameters
**Citation**: Zimmermann, N.E.R. et al. Frontiers in Materials, 4, 34 (2017). DOI: 10.3389/fmats.2017.00034
**Key findings**: Order parameters classify local environments (octahedral, tetrahedral, cubic). Site-level features aggregated for crystal-level prediction. Available in matminer.

### Feature 17: Universal Fragment Descriptors (PLMF)
**Citation**: Isayev, O. et al. Nature Communications, 8, 15679 (2017). DOI: 10.1038/ncomms15679
**Key findings**: Crystal decomposition into Voronoi fragments labeled with elemental properties. Competitive results on formation energy and band gap.

### Feature 18: SISSO for Optimal Descriptors
**Citation**: Ghiringhelli, L.M. et al. Physical Review Letters, 114, 105503 (2015). DOI: 10.1103/PhysRevLett.114.105503
**Key findings**: Sure Independence Screening and Sparsifying Operator finds optimal compound descriptors from massive feature spaces. Physical descriptors from combinations of primary features outperform individual features.
**Knowledge extracted**: K64: Compound features (ratios, products of elemental properties) can outperform individual features

### Feature 19: Atom2Vec -- Learned Element Embeddings
**Citation**: Zhou, Q. et al. PNAS, 115(28), E6411-E6417 (2018). DOI: 10.1073/pnas.1801181115
**Key findings**: Learns 200-dim element embeddings from crystal structures. Captures periodic table relationships and chemical similarity.

### Feature 20: DScribe Descriptor Library
**Citation**: Himanen, L. et al. Computer Physics Communications, 247, 106949 (2020). DOI: 10.1016/j.cpc.2019.106949
**Key findings**: Python library for SOAP, ACSF, MBTR, Coulomb matrix, Ewald sum matrix, sine matrix. Efficient implementations with consistent API.

### Feature 21: MBTR -- Many-Body Tensor Representation
**Citation**: Huo, H. & Rupp, M. Machine Learning: Sci. Technol., 3(4), 045017 (2022). DOI: 10.1088/2632-2153/aca005
**Key findings**: k=1 (atomic numbers), k=2 (distances), k=3 (angles) distributions as continuous functions. Unified framework for periodic and non-periodic systems.

### Feature 22: Electronic Structure Descriptors for Band Gap
**Citation**: Zhuo, Y. et al. J. Phys. Chem. Lett., 9(7), 1668-1673 (2018). DOI: 10.1021/acs.jpclett.8b00124
**Key findings**: Electronegativity difference and d-orbital character most predictive for band gap. Electronic structure features outperform generic composition features for gap prediction.
**Knowledge extracted**: K65: d-electron count and electronegativity difference are top-2 features for band gap

### Feature 23: Thermoelectric Property Features
**Citation**: Chen, W. et al. J. Mater. Chem. C, 4, 4414-4426 (2016). DOI: 10.1039/C5TC04339E
**Key findings**: Effective mass, band degeneracy, deformation potential are critical electronic descriptors. PBE band gaps need corrections.

### Feature 24: Feature Selection for Half-Heuslers
**Citation**: Legrain, F. et al. J. Phys. Chem. B, 122(2), 625-632 (2017). DOI: 10.1021/acs.jpcb.7b05296
**Key findings**: Small set of physically motivated features (electronegativity difference, size mismatch, VEC) achieves near-optimal performance. Diminishing returns from adding more features.
**Knowledge extracted**: K66: ~10-20 well-chosen features can match hundreds of auto-generated ones

### Feature 25: Benchmarking Structure Descriptors on Matbench
**Citation**: Lam, T.H.T. et al. Machine Learning: Sci. Technol., 4(4), 045046 (2023). DOI: 10.1088/2632-2153/ad0f4b
**Key findings**: Systematically benchmarks SOAP, ACSF, MBTR, Coulomb matrix, SCM, OFM on Matbench tasks. SOAP generally outperforms for tabular ML. Graph-based learned representations still beat hand-crafted descriptors.
**Knowledge extracted**: K67: SOAP > MBTR > ACSF > OFM > Sine Coulomb Matrix for tabular ML on Matbench structure tasks

---

## Theme 9: Task-Specific Property Prediction Papers (23 papers)

### Task Paper 1: Steel Yield Strength -- Xiong et al. (2020)
**Citation**: Xiong, J. et al. Sci. China Technol. Sci., 63, 1247-1255 (2020). DOI: 10.1007/s11431-020-1599-5
**Key findings**: RF, GBM, NN for yield strength prediction. Carbon content, tempering temperature, alloying elements most important. MAE ~80 MPa on similar datasets.
**Matbench tasks**: matbench_steels

### Task Paper 2: Steel Properties -- Agrawal et al. (2014)
**Citation**: Agrawal, A. et al. IMMI, 3, 90-108 (2014). DOI: 10.1186/2193-9772-3-8
**Key findings**: RF and NN with elemental composition for steel fatigue/yield strength. C, Mn, Si, Cr are top features.
**Matbench tasks**: matbench_steels

### Task Paper 3: Computational Materials Design for Steels
**Citation**: Olson, G.B. Science, 277(5330), 1237-1242 (1997). DOI: 10.1126/science.277.5330.1237
**Key findings**: ICME approach: composition -> processing -> structure -> properties. Composition alone insufficient for steel properties -- microstructure and processing critical. Explains fundamental limitation of composition-only prediction.
**Matbench tasks**: matbench_steels -- explains why MAE floor is high

### Task Paper 4: Band Gap from ML -- Two-Stage Approach
**Citation**: Zhuo, Y. et al. Nature Communications, 9, 4377 (2018). DOI: 10.1038/s41467-018-06625-z
**Key findings**: Two-stage prediction (classify metal/non-metal, then regress gap) improves accuracy. Magpie features best for composition-only gap prediction.
**Matbench tasks**: expt_gap, expt_is_metal, mp_gap -- two-stage approach
**Hypotheses generated**: H44: Two-stage (classifier + regressor) will beat single-model gap prediction

### Task Paper 5: Band Gap Prediction -- Composition Features
**Citation**: Zhuo, Y. et al. J. Phys. Chem. Lett., 9(7), 1668-1673 (2018). DOI: 10.1021/acs.jpclett.8b00124
**Key findings**: SVR and RF achieve 0.45 eV MAE on experimental band gaps with composition features. s-p orbital overlap and electronegativity difference most predictive.
**Matbench tasks**: expt_gap, mp_gap

### Task Paper 6: Band Gap -- DFT + ML
**Citation**: Lee, J. et al. Physical Review B, 93, 115104 (2016). DOI: 10.1103/PhysRevB.93.115104
**Key findings**: 200+ features for band gap. Structure features (space group, bond lengths) improve MAE from 0.51 to 0.37 eV.
**Matbench tasks**: mp_gap

### Task Paper 7: Glass-Forming Ability -- Sun et al. (2017)
**Citation**: Sun, Y. et al. J. Phys. Chem. Lett., 8(14), 3434-3439 (2017). DOI: 10.1021/acs.jpclett.7b01046
**Key findings**: SVM, RF, NN for GFA prediction. Atomic size mismatch (lambda) and mixing entropy most important features. ROC-AUC > 0.9.
**Matbench tasks**: matbench_glass
**Hypotheses generated**: H45: Lambda (atomic packing efficiency) should be a top-3 feature for glass task

### Task Paper 8: Metallic Glass Alloy Design
**Citation**: Ward, L. et al. Acta Materialia, 159, 102-111 (2018). DOI: 10.1016/j.actamat.2018.08.002
**Key findings**: Magpie features + thermodynamic descriptors for GFA. Mixing entropy, atomic size variance, Miedema enthalpy are key. 87% accuracy. Notes class imbalance issues.
**Matbench tasks**: matbench_glass

### Task Paper 9: Active Learning for Metallic Glasses
**Citation**: Ren, F. et al. Science Advances, 4(4), eaaq1566 (2018). DOI: 10.1126/sciadv.aaq1566
**Key findings**: RF + Magpie for GFA with active learning loop. ML-guided exploration discovers new glass compositions 3x faster than traditional approaches.
**Matbench tasks**: matbench_glass

### Task Paper 10: Elastic Properties Dataset (data source)
**Citation**: de Jong, M. et al. Scientific Data, 2, 150009 (2015). DOI: 10.1038/sdata.2015.9
**Key findings**: DFT elastic tensors for ~11k compounds (expanded to 10,987 for Matbench). VRH averaging. ~10-15% error vs experiment. Data source for log_gvrh and log_kvrh.
**Matbench tasks**: matbench_log_gvrh, matbench_log_kvrh

### Task Paper 11: Elastic Modulus Prediction
**Citation**: Mansouri Tehrani, A. et al. JACS, 140(31), 9844-9853 (2018). DOI: 10.1021/jacs.8b02717
**Key findings**: VEC, bond valence, atomic density are key features for elastic property prediction. R^2 > 0.9 for bulk and shear moduli.
**Matbench tasks**: matbench_log_gvrh, matbench_log_kvrh
**Hypotheses generated**: H46: VEC should be top-5 feature for both elastic modulus tasks

### Task Paper 12: Dielectric Properties Dataset (data source)
**Citation**: Petousis, I. et al. Scientific Data, 4, 160134 (2017). DOI: 10.1038/sdata.2016.134
**Key findings**: DFT dielectric constants and refractive indices for ~4.8k compounds. Band gap and ionic character are key predictors.
**Matbench tasks**: matbench_dielectric

### Task Paper 13: Dielectric Properties -- Physics
**Citation**: Naccarato, F. et al. Phys. Rev. Materials, 3, 044602 (2019). DOI: 10.1103/PhysRevMaterials.3.044602
**Key findings**: Inverse correlation between band gap and refractive index. Transition metal d-electrons enhance dielectric response.
**Matbench tasks**: matbench_dielectric
**Hypotheses generated**: H47: 1/band_gap should be a strong feature for dielectric prediction

### Task Paper 14: DFT Dielectric Benchmarking
**Citation**: Petousis, I. et al. Phys. Rev. B, 93, 115151 (2016). DOI: 10.1103/PhysRevB.93.115151
**Key findings**: PBE underestimates gaps leading to overestimated dielectric constants. Ionic contribution varies strongly across structure types.
**Matbench tasks**: matbench_dielectric

### Task Paper 15: Perovskite Screening (data source)
**Citation**: Castelli, I.E. et al. Energy Environ. Sci., 5, 5814-5819 (2012). DOI: 10.1039/C1EE02717D
**Key findings**: ~19k perovskite formation energies. GLLB-SC functional. High-throughput screening for solar absorbers. Data source for matbench_perovskites.
**Matbench tasks**: matbench_perovskites

### Task Paper 16: Perovskite Water Splitting (data source extension)
**Citation**: Castelli, I.E. et al. Energy Environ. Sci., 5, 9034-9043 (2012). DOI: 10.1039/C2EE22341D
**Key findings**: Tolerance factor, electronegativity difference, ionic radius ratio are key perovskite stability predictors.
**Matbench tasks**: matbench_perovskites

### Task Paper 17: Perovskite ML Prediction
**Citation**: Pilania, G. et al. Frontiers in Materials, 3, 19 (2016). DOI: 10.3389/fmats.2016.00019
**Key findings**: SVM, KRR, RF for perovskite stability and band gap. Tolerance factor, octahedral factor, electronegativity difference are top-3 features.
**Matbench tasks**: matbench_perovskites

### Task Paper 18: Perovskite Thermodynamic Stability
**Citation**: Li, W. et al. Comp. Mater. Sci., 150, 454-463 (2018). DOI: 10.1016/j.commatsci.2018.04.033
**Key findings**: GBM with 145 composition features for perovskite formation energy. 0.05 eV/atom MAE. Ionic radius ratio, electronegativity difference, d-electron count are top features. >5k samples needed for convergence.
**Matbench tasks**: matbench_perovskites

### Task Paper 19: 2D Materials Exfoliation
**Citation**: Mounet, N. et al. Nature Nanotechnology, 13, 246-252 (2018). DOI: 10.1038/s41565-017-0035-5
**Key findings**: Computational exfoliation of layered materials. Weak interlayer binding (van der Waals), layered structure, anisotropic bonding predict exfoliation energy. Physics underlying the jdft2d task.
**Matbench tasks**: matbench_jdft2d

### Task Paper 20: Phonon Dataset (data source)
**Citation**: Petretto, G. et al. Scientific Data, 5, 180065 (2018). DOI: 10.1038/sdata.2018.65
**Key findings**: DFT phonon DOS for ~1.5k compounds. "Last phonon DOS peak" correlates with highest-frequency optical mode. Heavier atoms and weaker bonds -> lower frequencies.
**Matbench tasks**: matbench_phonons

### Task Paper 21: Phonon Prediction Comparison
**Citation**: Wines, D. et al. Mach. Learn.: Sci. Technol., 4(1), 015005 (2023). DOI: 10.1088/2632-2153/aca9a2
**Key findings**: Systematic comparison of ML for phonon properties. ALIGNN best. Structural features (bond lengths, angles) critical for phonon properties.
**Matbench tasks**: matbench_phonons

### Task Paper 22: Matbench Discovery
**Citation**: Riebesell, J. et al. Nature Machine Intelligence (2025); arXiv:2308.14920
**Key findings**: Stability prediction benchmark complementary to Matbench v0.1. Universal interatomic potentials (MACE, CHGNet, M3GNet) outperform energy-only models. Tests predict stability on WBM dataset.
**Matbench tasks**: Related to mp_e_form

### Task Paper 23: Formation Energy Stability Prediction
**Citation**: Bartel, C.J. et al. npj Computational Materials, 6, 97 (2020). DOI: 10.1038/s41524-020-00362-y
**Key findings**: Composition-only models insufficient for convex hull predictions. ~0.03 eV/atom MAE needed for reliable stability prediction.
**Matbench tasks**: mp_e_form

---

## Theme 10: Additional Method and Framework Papers (8 papers)

### Additional 1: Materials Project Database
**Citation**: Jain, A. et al. APL Materials, 1, 011002 (2013). DOI: 10.1063/1.4812323
**Key findings**: Database providing data for 7/13 Matbench tasks. >150k materials with consistent DFT settings.
**Matbench tasks**: mp_e_form, mp_gap, mp_is_metal, log_gvrh, log_kvrh, dielectric, phonons

### Additional 2: JARVIS Database
**Citation**: Choudhary, K. et al. npj Computational Materials, 6, 173 (2020). DOI: 10.1038/s41524-020-00440-1
**Key findings**: JARVIS-DFT with OptB88vdW functional. Provides jdft2d data. >40k materials.
**Matbench tasks**: matbench_jdft2d

### Additional 3: pymatgen
**Citation**: Ong, S.P. et al. Comp. Mater. Sci., 68, 314-319 (2013). DOI: 10.1016/j.commatsci.2012.10.028
**Key findings**: Core library for Structure/Composition handling. Foundation for all Matbench data.
**Matbench tasks**: All 13 tasks

### Additional 4: DOS Prediction via Contrastive Learning
**Citation**: Kong, S. et al. Nature Communications, 13, 949 (2022). DOI: 10.1038/s41467-022-28543-x
**Key findings**: Predicts full DOS from crystal structure. Deriving band gap from predicted DOS can be more accurate than direct prediction.
**Matbench tasks**: mp_gap, mp_is_metal

### Additional 5: Deep Transfer Learning for Materials
**Citation**: Jha, D. et al. Nature Communications, 10, 5316 (2019). DOI: 10.1038/s41467-019-13297-w
**Key findings**: Pre-train on DFT data (mp_e_form), fine-tune on experimental data (expt_gap). 10-30% improvement via transfer.
**Matbench tasks**: expt_gap, expt_is_metal

### Additional 6: Cross-Property Transfer for Small Data
**Citation**: Gupta, V. et al. Nature Communications, 12, 6595 (2021). DOI: 10.1038/s41467-021-26921-5
**Key findings**: Pre-train ALIGNN on formation energy then fine-tune on smaller property datasets. Significant improvement for small Matbench tasks.
**Matbench tasks**: steels, jdft2d, phonons, dielectric

### Additional 7: LLMs as Materials Science Assistants
**Citation**: Choudhary, K. & Garrity, K. arXiv:2306.07197 (2023)
**Key findings**: GPT-4 and other LLMs for materials property prediction from text. Reasonable for well-known materials, struggles with novel compositions.
**Matbench tasks**: expt_gap, expt_is_metal

### Additional 8: ML Best Practices Guide
**Citation**: Wang, A.Y. et al. Chemistry of Materials, 32(12), 4954-4965 (2020). DOI: 10.1021/acs.chemmater.0c01907
**Key findings**: Practical guide: feature selection (filter/wrapper/embedded), CV strategies, common pitfalls (leakage, class imbalance). Start with simple baselines.
**Matbench tasks**: All tasks -- methodology

---

## Comprehensive Hypothesis Summary (from Part 2)

| ID | Hypothesis | Source | Relevant Tasks |
|----|-----------|--------|----------------|
| H43 | NMI feature selection will identify sparse, high-quality feature subset per task | MODNet (De Breuck 2021) | All tasks |
| H44 | Two-stage (classifier + regressor) will beat single-model gap prediction | Zhuo et al. 2018 | expt_gap, mp_gap |
| H45 | Lambda (atomic packing efficiency) should be top-3 feature for glass | Sun et al. 2017 | glass |
| H46 | VEC should be top-5 feature for elastic modulus tasks | Mansouri Tehrani 2018 | log_gvrh, log_kvrh |
| H47 | 1/band_gap should be strong feature for dielectric prediction | Naccarato 2019 | dielectric |

## Knowledge Extracted Summary (from Part 2)

| ID | Knowledge | Source |
|----|-----------|--------|
| K43 | Descriptor choice matters more than model choice for small-medium datasets | Schmidt et al. 2019 |
| K44 | GNNs represent "third generation" materials ML representations | Chen et al. 2020 |
| K45 | Angular info (bond angles) gives ~10-20% improvement over distance-only GNNs | Choudhary et al. 2022 |
| K46 | Equivariant GNNs preserve physical symmetries for vector/tensor properties | Reiser et al. 2022 |
| K47 | No single GNN dominates across all property types | Fung et al. 2021 |
| K48 | For composition tasks <10k samples, Magpie > raw element fractions | Murdock et al. 2020 |
| K49 | Uncertainty quantification critical but often neglected | Butler et al. 2018 |
| K50 | Combining descriptors from different families can improve performance | Himanen et al. 2019 |
| K51 | For datasets <1k, simple models (Ridge, RF) often match deep learning | Morgan & Jacobs 2020 |
| K52 | Structure features provide 2-5x improvement over composition-only for formation energy | Bartel 2022 |
| K53 | DFT noise floor: ~0.02 eV/atom (formation energy), ~0.3 eV (band gap) | Jain et al. 2016 |
| K54 | Scaling laws exist for materials GNNs -- more data improves performance | Merchant et al. 2023 |
| K55 | Magpie features are composition gold standard -- always include as baseline | Ward et al. 2016 |
| K56 | matminer is canonical featurization library for Matbench | Ward et al. 2018 |
| K57 | SOAP outperforms other hand-crafted structure descriptors for tabular ML | Bartok et al. 2013 |
| K58 | Voronoi features give ~33% improvement on formation energy vs composition-only | Ward et al. 2017 |
| K59 | Oliynyk features better than Magpie for metallic systems | Oliynyk et al. 2016 |
| K60 | Yang delta parameter is single best predictor for glass-forming ability | Yang & Zhang 2012 |
| K61 | DEML features particularly strong for formation energy | Deml et al. 2016 |
| K62 | Miedema enthalpy computable from composition as a feature | Miedema et al. 1980 |
| K63 | Bartel tau factor should replace Goldschmidt t for perovskite tasks | Bartel et al. 2019 |
| K64 | Compound features (ratios, products) can outperform individual features | Ghiringhelli et al. 2015 |
| K65 | d-electron count and electronegativity difference are top-2 for band gap | Zhuo et al. 2018 |
| K66 | ~10-20 well-chosen features can match hundreds of auto-generated ones | Legrain et al. 2017 |
| K67 | Descriptor ranking for tabular ML: SOAP > MBTR > ACSF > OFM > SCM | Lam et al. 2023 |
