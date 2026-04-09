# Literature Review — gw_detectors

**Status**: Phase 0 in progress, started 2026-04-09. Target: 7 themes × 2000+ words each, traceable to ≥100 entries in `papers.csv`. Quality bar per `../../program.md` Phase 0.

This document is built theme-by-theme. Each theme begins as an outline (subsection headers + key questions) and gets filled in as the underlying papers are read. Do not skip subsections; do not handwave — every quantitative claim must cite a `papers.csv` entry by id.

---

## Theme 1: Domain fundamentals — interferometric gravitational-wave detection

### 1.1 Why interferometers detect strain
- Linearised general relativity: a passing gravitational wave produces a metric perturbation $h_{\mu\nu}(t)$ that changes proper distances between freely falling test masses
- Two polarisations $h_+$ and $h_\times$; differential length change in a Michelson is $\Delta L = h L / 2$
- Why arm length matters: signal-to-noise scales linearly with $L$ for shot-noise-limited detectors

### 1.2 The Michelson interferometer baseline
- Light split at a 50:50 beamsplitter, sent down two perpendicular arms, reflected, recombined
- Output power depends on the differential phase between the arms
- Key parameters: arm length, laser power, mirror reflectivity, photodetector efficiency

### 1.3 Power recycling and signal recycling
- Power recycling: a recycling mirror upstream of the beamsplitter forms a cavity that builds up circulating power, increasing shot-noise-limited sensitivity
- Signal recycling: a recycling mirror downstream creates a cavity for the signal sidebands, reshaping the frequency response (signal-recycling cavity, SRC)
- Combined power-recycled, signal-recycled, Fabry-Perot Michelson is the topology used by aLIGO, aVirgo, KAGRA

### 1.4 Fabry-Perot arm cavities
- Arm cavities increase the effective arm length by a factor of the cavity finesse
- Finesse $F = \pi\sqrt{R_{ITM} R_{ETM}} / (1 - R_{ITM} R_{ETM})$
- Tradeoff: higher finesse increases sensitivity but reduces bandwidth and increases coupling to noise sources

### 1.5 Quantum noise: shot noise and radiation pressure
- Shot noise: discrete arrival of photons at the photodetector. Spectral density $\propto 1/\sqrt{P_{\rm in}}$
- Radiation pressure noise: photon momentum transfer to mirrors. Spectral density $\propto \sqrt{P_{\rm in}} / (M f^2)$ for free-mass mirrors
- Standard quantum limit (SQL): the geometric mean of the two, set by $\hbar / (M (2\pi f)^2 L^2)$
- Caves 1981 first formalised the quantum noise budget for laser interferometers

### 1.6 Squeezed light injection
- Vacuum fluctuations entering the dark port set the shot noise floor
- Injecting a squeezed vacuum state reduces fluctuations in one quadrature at the cost of increasing them in the other
- Frequency-independent squeezing reduces shot noise but increases radiation-pressure noise
- Frequency-dependent squeezing (filter cavities) rotates the squeezing angle as a function of frequency, beating the SQL across the band

### 1.7 Other noise sources
- Coating thermal noise: dielectric coating dissipation drives mirror surface fluctuations. Dominant at mid-frequency in current detectors
- Suspension thermal noise: pendulum and violin modes
- Seismic noise: ground motion couples through the suspension chain
- Newtonian (gravity-gradient) noise: density fluctuations in the local environment couple directly to the test masses without going through the suspension
- Each noise source has its characteristic spectral shape and dominant frequency band

### 1.8 Detector generations: aLIGO → A+ → Voyager → Cosmic Explorer / Einstein Telescope
- aLIGO: first observation 2015 (GW150914)
- A+: incremental upgrade with frequency-dependent squeezing
- Voyager: cryogenic crystalline silicon test masses, 2 µm laser wavelength, 10 dB FDS — major upgrade target
- Cosmic Explorer (40 km arms) and Einstein Telescope (10 km triangular underground): third-generation, decade-out

### 1.9 Where the field stands today
- Current detectors are within ~2× of the SQL across the band
- Further improvements require either bigger detectors (Cosmic Explorer / ET), exotic noise reduction (frequency-dependent squeezing, optomechanical springs, white-light cavities), or fundamentally new topologies
- The Urania project (Krenn-Drori-Adhikari 2025) used gradient optimisation over Universal Interferometric Field Operators (UIFO grids) to discover novel topologies with up to 5.3× sensitivity improvement, but the physical mechanisms behind these designs are not understood

### Key references for this theme
*To be populated from `papers.csv` as the underlying papers are read.*

- Saulson, *Fundamentals of Interferometric Gravitational Wave Detectors* — textbook, the standard introduction
- Caves 1981 PRD — quantum noise in interferometers
- Aasi et al. 2013 (Nature Photonics) — squeezed light enhancement of LIGO
- Adhikari et al. 2020 (CQG) — Voyager design
- Krenn, Drori & Adhikari 2025 (PRX) — Urania, the seed paper for this project

---

## Theme 2: Phenomena of interest — noise sources, signal sources, frequency bands

### 2.1 Quantum noise budget in detail
- Subsections to come: shot noise spectral density, radiation pressure noise spectral density, ponderomotive squeezing, optomechanical effects, role of test mass mass and mechanical Q

### 2.2 Coating thermal noise
- Dielectric coating dissipation, fluctuation-dissipation theorem
- Why this is the dominant noise floor in the 50–500 Hz band for current detectors
- Mitigation strategies: crystalline coatings, larger beam spots, beam shape engineering

### 2.3 Suspension thermal noise and seismic noise
### 2.4 Newtonian (gravity-gradient) noise
### 2.5 Astrophysical signal sources by frequency band
- Inspiral: 10–100 Hz (BBH, BNS, NSBH)
- Merger: 100–800 Hz
- Post-merger / ringdown: 800–3000 Hz (target band for type8 of the GWDetectorZoo)
- Neutron-star f-mode oscillations
- Why post-merger detection is hard and what we'd learn

### 2.6 The post-merger band specifically
- Why 800–3000 Hz — neutron star equation of state, post-merger dynamics
- Existing sensitivity in this band
- The Urania type8 family targets this band

### Key references for this theme
*To be populated.*

---

## Theme 3: Candidate features / design variables — the UIFO parameter space

### 3.1 What the UIFO parameterises
- An $n \times n$ grid of optical elements connected by ports
- Mirrors, beamsplitters (regular and directional), lasers, squeezers, photodetectors, free masses, signal sinks
- Each element has its own physical parameters (reflectivity, mass, temperature, power, squeezing level, phase)

### 3.2 Per-element parameters and physical ranges
- Mirror: reflectivity (0..1), loss, tuning (phase), mass (0.1–200 kg), temperature (4–300 K)
- Beamsplitter: reflectivity (typically 0.5 for symmetric, but UIFO allows arbitrary)
- Laser: input power (0–1000 W), wavelength (typically 1064 nm for current detectors, 2 µm for Voyager)
- Squeezer: squeezing level (dB), squeezing angle (degrees)
- Cavity: length (10 m – 4 km)
- Photodetector: homodyne angle (0–360°)

### 3.3 Derived quantities
- Arm cavity finesse, optical spring constants, signal transfer functions, noise spectra

### 3.4 The number of parameters in a typical UIFO design
- Krenn et al. report up to 463 continuous parameters for some designs
- type8/sol00 specifically: paper-derived counts to be confirmed in Phase 0.5

### 3.5 Which parameters are typically critically tuned vs. arbitrarily filled
- Hypothesis (to be tested in Phase 1): impedance-matching conditions for cavity coupling are sharply peaked; beamsplitter ratios and homodyne angles are broad plateaus

### Key references for this theme
*To be populated.*

---

## Theme 4: ML / optimisation for interferometer design

### 4.1 Gradient-based optimisation in interferometer design
### 4.2 Differometor and JAX
### 4.3 Urania: BFGS over UIFO grids
### 4.4 Evolutionary and reinforcement-learning approaches
### 4.5 Surrogate models, Bayesian optimisation
### 4.6 Comparison: what each method has produced

### Key references for this theme
*To be populated.*

---

## Theme 5: Objective function design

### 5.1 Strain sensitivity as a frequency-domain quantity
### 5.2 Log-space averaging across frequency bands
### 5.3 Multi-objective tradeoffs (sensitivity vs cost vs alignment tolerance)
### 5.4 Decomposing strain into signal vs noise contributions

### Key references for this theme
*To be populated.*

---

## Theme 6: Transfer / generalisation across conditions

### 6.1 Frequency-band transfer (post-merger → broadband)
### 6.2 Detector-type transfer (Voyager → CE/ET)
### 6.3 Mechanism transfer across the GWDetectorZoo type families

### Key references for this theme
*To be populated.*

---

## Theme 7: Related problems — AI-discovered scientific designs in other domains

### 7.1 AlphaFold and protein structure prediction
### 7.2 Neural architecture search
### 7.3 Symbolic regression for physical laws
### 7.4 Reverse-engineering AI-discovered solutions: existing methodology
### 7.5 What's transferable to GW detector decomposition

### Key references for this theme
*To be populated.*

---

## Phase 0 progress

| Theme | Status | Word count | Key references read |
|---|---|---|---|
| 1. Domain fundamentals | outline + initial fill | ~700 / 2000 target | 0 / 15 |
| 2. Phenomena of interest | outline only | ~250 / 2000 target | 0 / 15 |
| 3. Candidate features | outline + initial fill | ~400 / 2000 target | 0 / 15 |
| 4. ML / optimisation | outline only | ~50 / 2000 target | 0 / 15 |
| 5. Objective function design | outline only | ~30 / 2000 target | 0 / 10 |
| 6. Transfer / generalisation | outline only | ~30 / 2000 target | 0 / 10 |
| 7. Related problems | outline only | ~50 / 2000 target | 0 / 10 |

**Next session**: read Krenn-Drori-Adhikari 2025 (Urania PRX) and Adhikari et al. 2020 (Voyager CQG) in full, populate Theme 1 to 2000+ words against actual citations, fill Theme 2's quantum-noise subsections from Caves 1981 and Buonanno-Chen 2001.
