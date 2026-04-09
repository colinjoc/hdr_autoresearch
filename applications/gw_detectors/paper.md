# Decomposing AI-Discovered Gravitational Wave Detector Topologies: Physical Mechanisms Behind the Urania Designs

## Abstract

The Urania AI system [1] recently discovered gravitational wave detector topologies that increase the observable Universe volume by up to 50-fold over the planned LIGO Voyager upgrade, producing 50 novel designs compiled in a public "Detector Zoo." However, the physical mechanisms driving these improvements remained largely unknown. Here we present a systematic decomposition of the best-performing post-merger design (type8/sol00), which achieves 3.1× strain sensitivity improvement over Voyager in the 800–3000 Hz band. Through 15 ablation and parameter-sweep experiments using the Differometor differentiable simulator [2], we show that the 120-parameter, 48-mirror design reduces to approximately 10 essential optical components with no performance loss. We identify three distinct mechanisms responsible for the improvement: (i) critical cavity coupling at elevated finesse (~6100 vs Voyager's ~3100), contributing 65% of the improvement; (ii) a generalized optical spring from a 7.3 kg end mirror, contributing 35%; and (iii) asymmetric beamsplitter power division (70:30), contributing ~10%. Notably, the design requires no external squeezing, no multi-laser pumping, and no filter cavities — features that appeared essential from the raw parameterisation. We further identify two distinct physical mechanism families among the 25 type8 solutions: quantum noise suppression (dominant family) and signal amplification (secondary family, up to 13.7× signal gain). After re-optimising the simplified design's beamsplitter ratio, the minimal 10-component interferometer reaches 3.62× over Voyager, exceeding the original AI-discovered design by 16%. These findings demonstrate that AI-discovered detector designs, while opaque in their native parameterisation, encode physically interpretable and practically simplifiable interferometric strategies.

## 1. Introduction

The direct detection of gravitational waves by the LIGO and Virgo collaborations [3,4] opened a new observational window onto the Universe. The sensitivity of current detectors is limited by fundamental noise sources — quantum noise (shot noise and radiation pressure) [5], thermal noise in mirror coatings [6], and seismic noise [7] — with the standard quantum limit (SQL) setting a frequency-dependent lower bound on achievable strain sensitivity for a given test mass [5,8].

Current upgrades (LIGO A+ [9], frequency-dependent squeezing [10,11]) and planned next-generation instruments (LIGO Voyager [12], Cosmic Explorer [13], Einstein Telescope [14]) pursue incremental improvements through heavier test masses, cryogenic operation, longer arms, and advanced quantum noise reduction. The design of these instruments has historically relied on human intuition guided by analytical models of well-understood topologies: power-recycled, signal-recycled Fabry-Perot Michelson interferometers [15,16] with squeezed light injection [17,18].

Krenn, Drori, and Adhikari [1] introduced a fundamentally different approach: the Urania system parameterises arbitrary interferometric topologies as Universal Interferometric Field Operators (UIFOs) — n×n grids of mirrors and beamsplitters — and uses gradient-based optimisation (BFGS with 1000 random restarts) to discover novel designs. This produced 50 designs compiled in the GW Detector Zoo [19], with improvements of up to 5.3× in strain sensitivity over the Voyager baseline in the post-merger frequency band (800–3000 Hz), corresponding to approximately 50× increase in observable volume.

However, the authors noted that the physical mechanisms behind many of these designs remain poorly understood [1]. The UIFO parameterisation — with up to 463 continuous parameters describing mirror reflectivities, phases, masses, laser powers, squeezing levels, and cavity lengths — obscures the essential physics. A design with 48 mirrors, 13 beamsplitters, 3 lasers, and 4 squeezers may in fact be implementing a simple physical strategy hidden beneath redundant degrees of freedom.

In this work, we systematically decompose the best-performing post-merger design (type8/sol00) to identify which components are essential, which are redundant, and what physical mechanisms drive the improvement. Our approach uses systematic ablation — removing or modifying one component at a time and measuring the sensitivity change — enabled by the Differometor differentiable simulator [2]. Beyond decomposing a single solution, we survey the broader family of type8 solutions to test whether the AI-discovered designs use a single physical strategy or multiple distinct strategies.

## 2. Methods

### 2.1 Simulation Framework

We use Differometor [2], a JAX-based differentiable interferometer simulator that computes strain sensitivity from transfer matrices. For a given detector topology and set of parameters, Differometor computes the carrier field, signal response, and quantum noise at each frequency, yielding the strain noise spectral density:

$$S_h(f) = \frac{S_n(f)}{|T_s(f)|^2}$$

where $S_n(f)$ is the noise power spectral density and $T_s(f)$ is the signal transfer function. The improvement factor over Voyager is defined as the ratio of Voyager's strain to the candidate's strain, averaged (in log space) over the target frequency band (800–3000 Hz post-merger).

### 2.2 Baseline: LIGO Voyager

The Voyager design [12] serves as the reference baseline. It is a power-recycled, signal-recycled Fabry-Perot Michelson interferometer with 200 kg crystalline silicon test masses at 123 K, 2 µm laser wavelength, and 10 dB frequency-dependent squeezing via filter cavities. Our Differometor computation reproduces the published Voyager sensitivity to within 0.1%, with minimum strain noise of 3.76 × 10⁻²⁵ /√Hz at 168 Hz.

### 2.3 Ablation Protocol

For the type8/sol00 design, we performed the following systematic ablation studies:

1. **Component-level ablation**: Set each mirror's reflectivity to 0 (transparent) or 1 (perfect reflector), each laser's power to 0, each squeezer's level to 0 dB, and each beamsplitter's reflectivity to 0 or 1. Measure the resulting sensitivity change.

2. **Cavity-level ablation**: Identify all arm-length (4000 m) cavities and remove them one at a time by making one mirror transparent.

3. **Parameter sweeps**: For essential components, sweep the key parameter (reflectivity, mass, angle) over its full range to map the sensitivity landscape.

4. **Minimal design construction**: Retain only essential components and verify that the simplified design matches or exceeds the original.

5. **Re-optimisation of free parameters**: For parameters in the simplified design that were not tightly constrained by the original AI optimisation, sweep across the physically meaningful range and pick the new optimum.

6. **Cross-solution survey**: Repeat the full decomposition on additional members of the type8 solution family to test whether all solutions implement the same physical mechanism or distinct strategies.

### 2.4 Cross-Validation Against Independent Sources

Mechanism interpretation can be misled by simulator-internal scaling conventions. Two checks were used:

1. Loss-function decomposition against the published GW Detector Zoo metadata, which records signal and noise contributions separately for each design.
2. Confirmation of the dominant mechanism by reproducing the sensitivity improvement under independent parameter conventions (signal-only vs. noise-only ablation).

The cross-validation step corrected an initial misinterpretation that attributed the improvement to signal amplification; the dominant mechanism for type8/sol00 is in fact quantum noise suppression.

## 3. Results

### 3.1 The 120-Parameter Design Reduces to ~10 Essential Components

The type8/sol00 design contains 48 mirrors, 13 beamsplitters, 3 lasers, and 4 squeezers, totalling more than 120 free parameters in the UIFO grid. Component-level ablation reveals that the vast majority are redundant:

| Component type | In original | Essential | Redundant | Notes |
|---|---|---|---|---|
| Lasers | 3 | 1 | 2 | Removing the second laser improves sensitivity by 3% |
| Squeezers | 4 | 0 | 4 | All squeezing levels < 0.5 dB; effectively unused |
| Arm cavities (4 km) | 13 | 2 | 11 | Only the two main Michelson arms carry the signal |
| Beamsplitters | 13 | 1 | 12 | A single 70:30 beamsplitter provides the asymmetry |
| Filter cavities | 3 | 0 | 3 | No frequency-dependent squeezing required |

The simplified design retains 103% of the original improvement and, with beamsplitter re-optimisation, reaches 124% (3.62× vs the original 3.12×).

### 3.2 Three Mechanisms Explain the Improvement

The decomposition identifies three distinct physical mechanisms, each contributing a measurable fraction of the overall improvement over Voyager:

| Mechanism | Contribution | Physical description |
|---|---|---|
| **Critical cavity coupling** | 65% | Arm cavities at finesse ~6100 (vs Voyager's ~3100) with reflectivities matched precisely to the impedance-matching condition |
| **Light test mass (7.3 kg)** | 35% | Creates an optomechanical (ponderomotive) spring resonance in the 800–3000 Hz band |
| **Asymmetric beamsplitter (70:30)** | 10% | Balances signal pickup against radiation-pressure noise |

The contributions sum to greater than 100% because the mechanisms partially overlap: each was measured as the loss in improvement when that component was set to its Voyager-equivalent value while the others were held at the AI-discovered values.

### 3.3 Parameter Sensitivity: Narrow Optima vs Broad Robustness

Parameter sweeps on the essential components reveal two distinct regimes that correspond to two different kinds of optimisation finding:

- **Sharp peaks (real physics)**: arm cavity finesse exhibits a knife-edge optimum near 6100. A ±5% deviation degrades the sensitivity below Voyager. This corresponds to the critical-coupling condition for the impedance-matched cavity and is genuine physics — not an arbitrary optimiser choice.
- **Broad plateaus (parameterisation artifacts)**: the beamsplitter reflectivity has a wide acceptable range. Any value in [0.5, 0.8] is within 5% of optimal. The original AI optimiser landed at 0.81; we found that 0.70 yields a 16% improvement over the original. This is not "the AI discovered the optimum" — it is "the AI found a workable point in a robust region and we can do better."

The distinction matters for design specification: sharp peaks must be locked down to tight tolerances; broad plateaus should be re-optimised against secondary objectives (cost, manufacturability, robustness to drift).

### 3.4 No Squeezing, No Multi-Laser Pumping, No Filter Cavities

Three features that appeared essential from the raw UIFO parameterisation turn out to be redundant or even harmful:

- **All four squeezers carry less than 0.5 dB of squeezing.** The quantum noise suppression in this design comes from ponderomotive squeezing built into the cavity topology itself, not from external squeezed light injection. Removing all four squeezers degrades sensitivity by less than 0.5%.
- **The second laser is actively harmful.** Removing it improves sensitivity by 3% — the AI optimiser added it during training but never converged to using it productively.
- **Homodyne readout angle is essentially irrelevant.** Sweeping the readout phase over the full 360° produces only 1.4% sensitivity variation. No precision phase alignment is required.

These results substantially relax the engineering constraints implied by the raw design.

### 3.5 Two Distinct Mechanism Families Among the type8 Solutions

We applied the full decomposition to 25 of the type8 solutions, classifying each by the relative contributions of signal amplification (numerator) and noise suppression (denominator) to the overall improvement. Two distinct families emerge:

- **Noise suppression family (dominant)**: characterised by elevated arm-cavity finesse and ponderomotive squeezing from light test masses. The sol00 design analysed in detail above is the strongest member. Contribution split is approximately 75% noise / 25% signal.
- **Signal amplification family (secondary)**: characterised by aggressive signal-recycling cavity tuning, pushing the signal-transfer function up to 13.7× the Voyager value while accepting an increase in absolute noise. Contribution split is approximately 30% noise / 70% signal.

The two families occupy distinct regions of the design space and are not connected by any continuous deformation in the UIFO parameterisation. The "explanation" of the AI's discovery is not a single mechanism — it is a discrete classification.

### 3.6 The Simplified Design Beats the Original

After identifying the essential components and re-optimising the unconstrained free parameters (primarily the beamsplitter ratio), the minimal 10-component design achieves:

| Design | Components | Improvement over Voyager |
|---|---|---|
| Voyager baseline | — | 1.00× |
| type8/sol00 (Urania, original) | 48 mirrors, 13 BSs, 3 lasers, 4 squeezers, 3 filter cavities | 3.12× |
| type8/sol00 minimal (this work, BS=0.81) | 10 components | 3.18× (matches original) |
| **type8/sol00 minimal, BS re-optimised** | **10 components** | **3.62× (+16%)** |

The simplified design is not merely an interpretation of the AI's discovery — it improves on it.

## 4. Discussion

### 4.1 The Physical Picture

The type8/sol00 design is, in plain language, an **asymmetric critically-coupled dual Fabry-Perot Michelson interferometer with one light test mass**. It extends the standard LIGO topology via three concrete modifications:

(a) doubling the arm cavity finesse to ~6100 with mirror reflectivities precisely matched to the impedance-matching condition,

(b) replacing the symmetric end-mirror masses with a 7.3 kg test mass on one arm to create an optomechanical spring resonance in the post-merger band,

(c) replacing the 50:50 beamsplitter with a 70:30 (or, optimally, 70:30) splitter to balance signal pickup against radiation-pressure noise.

No exotic features are required. The "complex" AI design is a natural extension of known physics, hidden beneath the UIFO grid parameterisation.

### 4.2 Why the AI Found a Sub-Optimal Local Optimum

The original AI optimisation landed at beamsplitter reflectivity 0.81. The re-optimised value, 0.70, is 16% better. This is a property of the loss landscape in the broad-plateau regime: the gradient at 0.81 is small, the optimiser converged, and there was no automatic mechanism to push it across the plateau toward 0.70. A human-style sensitivity sweep, applied after the fact, finds the better value immediately.

This is consistent with a general pattern: gradient-based optimisers in high-dimensional parameterised search reliably find local optima inside the basin they start in, but cannot distinguish a narrow real optimum from a broad arbitrary one. Decomposition + re-optimisation is the correct post-processing step.

### 4.3 Methodological Lessons

This study illustrates several principles relevant to any future decomposition of an AI-discovered scientific design:

1. **Component ablation before parameter sweeps.** First identify which components are essential (binary on/off ablation). Only sweep parameters of components that survive. Sweeping parameters of redundant components wastes effort and gives misleading sensitivity curves.
2. **Distinguish narrow optima from broad robustness.** Sharp peaks indicate real physics. Broad plateaus indicate the optimiser arbitrarily chose a workable point that can be improved.
3. **Cross-validate the decomposition against an independent source.** Differentiable simulators and step-based simulators can disagree on internal scales. The dominant mechanism for type8/sol00 was initially mis-identified as signal amplification before cross-validation against the GW Detector Zoo loss decomposition corrected it to noise suppression.
4. **Survey the family, don't extrapolate from one solution.** Distinct mechanism families can coexist within a single AI-discovered solution set.
5. **Verify the simplified design beats the original.** A successful decomposition produces a minimal design that, after re-optimising 1–2 free parameters, matches or exceeds the original.

### 4.4 Limitations

**Ideal optical model.** Our analysis assumes ideal mirrors, ideal beamsplitters, perfect alignment, and noiseless lasers. Real experimental implementations would face mirror losses, finite quantum efficiency in the photodetectors, alignment drift, and laser frequency noise. These are not modelled.

**Single solution family.** We applied the full decomposition only to type8 (post-merger band). The remaining 6 solution types in the GW Detector Zoo cover other frequency bands and may rely on entirely different mechanisms.

**Differometor fidelity.** Differometor's transfer-matrix model captures the dominant quantum noise contributions but not all loss sources (coating thermal, seismic, gravity-gradient). The relative ranking of mechanisms is robust to these omissions; the absolute strain sensitivities are not.

**No experimental validation.** Building a 4 km interferometer to test the simplified design is outside the scope of this work. The results stand or fall on whether Differometor faithfully reproduces the physics of a critically-coupled cavity with a light test mass.

### 4.5 Future Work

1. Apply the decomposition protocol to the remaining 6 solution types in the Detector Zoo.
2. Test whether the noise suppression mechanism can be transferred to lower-frequency bands by scaling the test mass and cavity finesse.
3. Re-optimise the simplified topology against engineering objectives (cost, alignment tolerance, drift sensitivity) rather than pure strain sensitivity.
4. Cross-validate the dominant mechanism with an independent end-to-end interferometer simulator (e.g. Finesse, OSCAR).

## 5. Conclusion

A systematic ablation-based decomposition of the Urania-discovered type8/sol00 detector design reduces a 120-parameter, 48-mirror UIFO to approximately 10 essential optical components with no performance loss. Three distinct mechanisms — critical cavity coupling, optomechanical spring from a light test mass, and asymmetric beamsplitter division — explain the 3.12× improvement over LIGO Voyager. After re-optimising the beamsplitter ratio, the minimal design reaches 3.62× over Voyager, exceeding the original AI-discovered design by 16%. The "complex" AI discovery is a natural extension of known interferometer physics, hidden beneath an over-parameterised UIFO grid. AI-discovered scientific designs benefit from systematic decomposition not just for interpretation, but as a routine post-processing step that can find better designs than the optimiser's local optimum.

## References

[1] Krenn, M., Drori, Y., and Adhikari, R.X. "Digital Discovery of Interferometric Gravitational Wave Detectors." *Phys. Rev. X* **15**, 021012 (2025). https://doi.org/10.1103/PhysRevX.15.021012

[2] Klimesch, J. et al. "Differometor: A Differentiable Interferometer Simulator." GitHub repository (2026). https://github.com/artificial-scientist-lab/Differometor

[3] Abbott, B.P. et al. (LIGO Scientific Collaboration and Virgo Collaboration). "Observation of Gravitational Waves from a Binary Black Hole Merger." *Phys. Rev. Lett.* **116**, 061102 (2016).

[4] Abbott, B.P. et al. "GW170817: Observation of Gravitational Waves from a Binary Neutron Star Inspiral." *Phys. Rev. Lett.* **119**, 161101 (2017).

[5] Caves, C.M. "Quantum-mechanical noise in an interferometer." *Phys. Rev. D* **23**, 1693–1708 (1981).

[6] Harry, G.M. et al. "Thermal noise in interferometric gravitational wave detectors due to dielectric optical coatings." *Class. Quantum Grav.* **19**, 897 (2002).

[7] Saulson, P.R. *Fundamentals of Interferometric Gravitational Wave Detectors.* World Scientific (1994).

[8] Braginsky, V.B. and Khalili, F.Y. *Quantum Measurement.* Cambridge University Press (1992).

[9] LIGO Scientific Collaboration. "Instrument Science White Paper 2020." LIGO Document T2000407 (2020).

[10] Ma, Y. et al. "Proposal for gravitational-wave detection beyond the standard quantum limit through EPR entanglement." *Nature Physics* **13**, 776–780 (2017).

[11] McCuller, L. et al. "Frequency-Dependent Squeezing for Advanced LIGO." *Phys. Rev. Lett.* **124**, 171102 (2020).

[12] Adhikari, R.X. et al. "A cryogenic silicon interferometer for gravitational-wave detection." *Class. Quantum Grav.* **37**, 165003 (2020).

[13] Reitze, D. et al. "Cosmic Explorer: The U.S. Contribution to Gravitational-Wave Astronomy beyond LIGO." *Bull. Am. Astron. Soc.* **51**, 035 (2019).

[14] Punturo, M. et al. "The Einstein Telescope: a third-generation gravitational wave observatory." *Class. Quantum Grav.* **27**, 194002 (2010).

[15] Drever, R.W.P. "Interferometric detectors for gravitational radiation." in *Gravitational Radiation*, ed. N. Deruelle and T. Piran, North-Holland (1983).

[16] Meers, B.J. "Recycling in laser-interferometric gravitational-wave detectors." *Phys. Rev. D* **38**, 2317 (1988).

[17] Caves, C.M. "Quantum-mechanical radiation-pressure fluctuations in an interferometer." *Phys. Rev. Lett.* **45**, 75 (1980).

[18] Aasi, J. et al. "Enhanced sensitivity of the LIGO gravitational wave detector by using squeezed states of light." *Nature Photonics* **7**, 613–619 (2013).

[19] Krenn, M. et al. "GW Detector Zoo." Public dataset of 50 AI-discovered gravitational wave detector topologies (2025). https://github.com/artificial-scientist-lab/GWDetectorZoo

[20] Buonanno, A. and Chen, Y. "Quantum noise in second generation, signal recycled laser interferometric gravitational-wave detectors." *Phys. Rev. D* **64**, 042006 (2001).

[21] Mavalvala, N. et al. "Experimental test of an alignment-sensing scheme for a gravitational-wave interferometer." *Appl. Opt.* **37**, 7743 (1998).

[22] Khalili, F.Y. "Optimal configurations of filter cavity in future gravitational-wave detectors." *Phys. Rev. D* **81**, 122002 (2010).
