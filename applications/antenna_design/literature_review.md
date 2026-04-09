# Literature Review: Antenna Design Optimisation via GPU-Accelerated Simulation and Machine Learning

## 1. Antenna Theory Fundamentals

### 1.1 Core Antenna Parameters

An antenna is a transducer that converts guided electromagnetic waves into free-space radiation (and vice versa). The key performance metrics that any optimisation framework must target are:

- **Gain (G)**: The ratio of radiation intensity in a given direction to the average radiation intensity over all directions, measured in dBi. Gain equals directivity multiplied by radiation efficiency. Typical values range from 2.15 dBi (half-wave dipole) to 30+ dBi (horn/array antennas).
- **Bandwidth (BW)**: The frequency range over which the antenna meets specified performance criteria (typically VSWR < 2:1 or S11 < -10 dB). Expressed as a percentage of centre frequency or as a ratio.
- **Radiation Efficiency (eta_rad)**: The ratio of radiated power to accepted power, accounting for ohmic and dielectric losses. Typically 80--98% for well-designed patch antennas, lower at mmWave frequencies.
- **Return Loss / S11**: Measures impedance match quality. S11 < -10 dB corresponds to < 10% reflected power.
- **Directivity (D)**: Maximum radiation intensity normalised to the isotropic level, related to gain by G = eta_rad * D.
- **Radiation Pattern**: Spatial distribution of radiated power characterised by half-power beamwidth (HPBW), sidelobe level (SLL), front-to-back ratio, and cross-polarisation level.
- **Polarisation**: Linear, circular, or elliptical. Axial ratio (AR) < 3 dB defines circular polarisation bandwidth.
- **Input Impedance**: Must be matched to the feed line (typically 50 ohm or 75 ohm) for efficient power transfer.

### 1.2 Antenna Types Relevant to Optimisation

**Microstrip Patch Antennas** are the most widely studied in ML-driven optimisation owing to their planar geometry, ease of fabrication, and parametric simplicity. A rectangular patch operating in fundamental TM10 mode has length L ~ lambda_d/2 (where lambda_d = lambda_0 / sqrt(epsilon_reff)), and the resonant frequency is primarily determined by patch length, substrate permittivity, and substrate height [Balanis 2016]. The transmission line model represents the patch as two radiating slots separated by a low-impedance transmission line; the cavity model treats the patch region as an electromagnetic cavity bounded by electric walls (ground and patch) and magnetic walls (edges) [Pozar 1992]. Typical performance: 2--8 dBi gain, 1--5% bandwidth (broadened to 10--25% with stacking, slots, or thick substrates), 80--95% efficiency.

**Slot Antennas** achieve wider bandwidth through slot geometry (rectangular, annular, fractal). A fractal slot-loaded super-wideband antenna has demonstrated 3--40 GHz bandwidth (13:1 ratio) with 9.7 dBi peak gain and 94% average radiation efficiency [Electronics 2024].

**Dielectric Resonator Antennas (DRAs)** offer higher radiation efficiency (no conductor loss) and wider bandwidth than patches. They are increasingly used at mmWave frequencies with machine learning optimisation for 5G NR applications, achieving tuning ranges exceeding 80% [Rai et al. 2024].

**Horn Antennas** provide 10--25 dBi gain with usable bandwidth ratios up to 20:1 and aperture efficiency of 40--80%. Horn arrays have demonstrated 27 dBi gain with >70% aperture efficiency [Anjomshoa et al. 2024].

**MIMO Array Antennas** for 5G/6G require high isolation (>25 dB), compact form factor, and optimised beamforming. Element spacing of >= 0.5 lambda effectively reduces mutual coupling. Recent 8-element mmWave designs achieve isolation exceeding 25 dB with peak gain of 7.5 dBi at 39 GHz.

**Fractal Antennas** use self-similar geometries (Sierpinski, Koch, Minkowski) for multiband operation and size reduction. Parametric studies show slot width has greater influence than slot length on band-notch characteristics.

**Conformal Antennas** fabricated via additive manufacturing on curved surfaces are emerging as a critical application domain, with 3D printing achieving line widths of 8 um and height differences up to 50 mm for conformal metallisation.

### 1.3 Characteristic Mode Analysis (CMA)

CMA decomposes a structure's current distribution into a set of orthogonal characteristic modes, each with a known resonant frequency and radiation pattern. CMA provides physical insight for systematic antenna design: identifying which modes contribute to desired radiation, guiding feed placement, and informing topology decisions. Recent work applies CMA with genetic algorithms for reconfigurable holographic surface antennas and for achieving wideband circular polarisation through orthogonal mode excitation [2024].

### 1.4 Substrate Materials and Their Impact

Substrate selection critically affects antenna performance:

| Material | epsilon_r | tan(delta) | Cost | Use Case |
|----------|-----------|------------|------|----------|
| FR4 | 4.2--4.7 | 0.02 | Low | Prototyping, sub-GHz |
| Rogers RT/duroid 5880 | 2.2 | 0.0009 | High | mmWave, low-loss |
| Rogers RO4003C | 3.38 | 0.0027 | Medium | General microwave |
| Rogers RO3010 | 10.2 | 0.0023 | High | Miniaturisation |
| Alumina (Al2O3) | 9.8 | 0.0001 | High | mmWave, DRA |

Higher permittivity reduces antenna size but degrades bandwidth and efficiency. Loss tangent directly impacts radiation efficiency; FR4 losses become significant above 1 GHz.

---

## 2. Electromagnetic Simulation Methods

### 2.1 Finite-Difference Time-Domain (FDTD)

FDTD discretises Maxwell's curl equations on a Yee grid in both space and time, solving for E and H fields alternately at half-time-step offsets. Key properties:

- **Broadband**: A single time-domain simulation yields the full frequency response via FFT, making FDTD ideal for wideband/UWB antenna analysis.
- **GPU Parallelism**: The structured grid and local stencil operations map naturally to GPU architectures. CUDA implementations achieve up to 17x throughput improvement over CPU, with multi-GPU configurations delivering up to 80x speedup [ICCS 2024, Keysight 2024].
- **Numerical Dispersion**: The structured grid introduces frequency-dependent phase velocity errors that must be controlled via mesh refinement (Courant stability condition: delta_t <= delta_x / (c * sqrt(3)) in 3D).
- **Open-Source Implementations**: gprMax (Edinburgh, 3D FDTD with GPU support via OpenCL), openEMS (FDTD with Matlab/Octave scripting), Meep (MIT, Python/C++ with MPI parallelisation, primarily photonics).
- **Limitations**: Conformally meshing curved geometries requires staircasing approximation; absorbing boundary conditions (PML) add computational overhead.

### 2.2 Finite Element Method (FEM)

FEM uses unstructured tetrahedral meshes to discretise the variational form of Maxwell's equations in the frequency domain:

- **Geometry Conformity**: Triangular/tetrahedral elements accurately represent curved boundaries and fine geometric features without staircasing.
- **Frequency Domain**: No numerical dispersion, but each frequency point requires a separate solution.
- **Adaptive Meshing**: Commercial solvers (HFSS) automatically refine meshes in regions of high field gradient.
- **Computational Cost**: Mesh generation is complex and time-consuming; volumetric meshing yields large systems of equations.
- **Commercial Implementations**: ANSYS HFSS (industry standard for high-frequency design), integrated with PyAEDT for Python automation.

### 2.3 Method of Moments (MoM)

MoM solves integral equations (EFIE/MFIE) on conductor/dielectric surfaces only:

- **Surface-Only Discretisation**: No volumetric meshing of free space required, giving MoM a significant computational advantage for radiating structures surrounded by large empty regions.
- **No Numerical Dispersion**: Frequency-domain formulation.
- **Limitations**: Best suited for piecewise-homogeneous media; large dense matrix fills require O(N^2) storage and O(N^3) solution. MLFMA accelerations reduce this to O(N log N). Harder to parallelise on GPUs than FDTD.
- **Implementations**: NEC2/nec2c (open-source, MoM for wire antennas), FEKO (commercial, MoM + MLFMA + hybrid), ADS Momentum (planar MoM).

### 2.4 Comparative Assessment for Antenna Optimisation

| Criterion | FDTD | FEM | MoM |
|-----------|------|-----|-----|
| Broadband capability | Excellent (single run) | Poor (per-frequency) | Poor (per-frequency) |
| GPU acceleration | Excellent | Moderate | Difficult |
| Complex geometry | Staircasing issues | Excellent | Surface only |
| Open-source maturity | Good (gprMax, Meep, openEMS) | Limited | Good (NEC2) |
| Dataset generation speed | Fast (broadband + GPU) | Slow | Moderate |
| Memory scaling | O(N) | O(N) | O(N^2) |

**Recommendation for HDR**: GPU-accelerated FDTD is the optimal backbone for generating large training datasets for ML surrogates, with FEM used selectively for validation of geometrically complex designs.

### 2.5 Commercial Solver Landscape

- **CST Studio Suite** (Dassault Systemes): FIT/FDTD time-domain solver, highly visual CAD-integrated interface, GPU acceleration support.
- **ANSYS HFSS** (Synopsys): FEM frequency-domain, industry standard for precision. PyAEDT provides full Python automation.
- **FEKO** (Altair): MoM + MLFMA + hybrid methods, specialised for antenna placement and RCS.
- **Keysight ADS Momentum**: Planar MoM, integrated circuit co-simulation, excellent for microstrip and RFIC.

---

## 3. Machine Learning Surrogate Models for Antenna Design

### 3.1 The Surrogate Modelling Paradigm

Direct optimisation using full-wave EM simulation is computationally prohibitive: each function evaluation requires minutes to hours, and evolutionary algorithms may require thousands of evaluations. Surrogate models (metamodels) replace the expensive simulator with a fast approximation trained on a limited set of simulation data.

The surrogate-assisted optimisation loop:
1. Generate initial design of experiments (DoE) via Latin hypercube sampling
2. Evaluate DoE points using full-wave EM simulation
3. Train surrogate model on (parameters, performance) pairs
4. Use surrogate to identify promising candidates (exploit) and uncertain regions (explore)
5. Evaluate selected candidates with full-wave simulation
6. Update surrogate and repeat until convergence

### 3.2 Gaussian Process Regression (Kriging)

GP/Kriging models are the workhorse of surrogate-assisted antenna optimisation, providing both predictions and uncertainty estimates that enable efficient global optimisation (EGO) via expected improvement acquisition functions. Key advantages:

- Analytical uncertainty quantification
- Data-efficient (works well with 50--200 training samples)
- Smooth interpolation of antenna response surfaces

Limitations: Training cost scales as O(N^3) for N data points; performance degrades in high-dimensional spaces (>15--20 parameters) without dimensionality reduction [Koziel et al. 2024].

### 3.3 Deep Neural Networks (DNNs)

DNNs scale better than GPs to high-dimensional parameter spaces and large datasets:

- **Feedforward Networks (MLPs)**: Map design parameters to performance metrics. Widely used for S-parameter prediction with architectures of 3--5 hidden layers [multiple 2024 studies].
- **Convolutional Neural Networks (CNNs)**: Process pixelated antenna geometry representations (e.g., 10x10 binary matrices) to predict S-parameters. A CNN trained on 150,000 simulated datasets achieves accurate S-parameter prediction as a surrogate for full-wave simulation [MDPI Electronics 2025].
- **Recurrent Neural Networks (RNNs/LSTMs)**: Capture sequential frequency-dependent behaviour. BNN-LSTM surrogate models leverage LSTM's strength with sequence data for antenna modelling across frequency [Wiley 2024].
- **Bayesian Neural Networks (BNNs)**: Replace GPs for uncertainty-aware surrogate modelling with better scalability. The SB-SADEA method introduces BNN-based surrogate modelling into antenna optimisation, providing uncertainty estimates without the cubic scaling cost of GPs [IEEE TAP 2022, Liu PhD thesis 2024].

### 3.4 Convolutional Neural Networks for Geometry Representation

A critical innovation is representing antenna topology as a binary image:

- Metalised pixels = 1, substrate pixels = 0, excitation port = 0.5
- Additional channels encode spatial coordinates for position-sensitive features
- Enables CNN-based forward and inverse models that generalise across topologies
- Training datasets of 10,000--150,000 samples generated via parameterised EM simulation

Branched-output CNN architectures predict multiple electromagnetic parameters (gain, bandwidth, S11) simultaneously over an operating frequency range [2024].

### 3.5 Reduced-Dimensionality Surrogates

High-dimensional antenna design spaces (10--30+ parameters) challenge surrogate accuracy. Key dimensionality reduction techniques:

- **Principal Component Analysis (PCA)**: Kriging surrogates built over PCA-reduced affine subspaces yield accurate models with fewer training samples. Eigenvalues from spectral analysis of antenna response Jacobians identify maximum-variability directions [Koziel et al. 2024].
- **Global Sensitivity Analysis (GSA)**: Identifies which parameters most influence antenna response, enabling selective optimisation of the most impactful variables while fixing insensitive ones [Scientific Reports 2024].
- **Autoencoders**: Learned nonlinear dimensionality reduction for antenna geometry representation, enabling compact latent spaces for generative design.

### 3.6 Physics-Informed Neural Networks (PINNs)

PINNs embed Maxwell's equations into the neural network loss function, constraining predictions to be physically consistent:

- Time-domain 3D EM field estimation for microstrip circuits and inverted-F antennas, achieving 200x speedup over FDTD [DATE 2025].
- Domain-adaptive PINNs for inverse problems in heterogeneous media [arXiv 2024].
- Quantum-enhanced PINNs (QPINNs) achieve up to 19% accuracy improvement over classical PINNs on 2D Maxwell benchmarks [2025].
- PINNs for high-fidelity EM field approximation in VLSI and RF EDA applications.

**Open challenge**: PINNs struggle with high-frequency, multi-scale EM problems and require careful loss balancing between data fidelity and physics terms.

### 3.7 Neural Operators

Neural operators learn mappings between function spaces (e.g., permittivity distribution to E-field), offering mesh-independent generalisation:

- **Fourier Neural Operator (FNO)**: Operates in Fourier domain for spectral efficiency; demonstrated on electromagnetic problems including Maxwell's equations for metasurface wavefront shaping via adjoint-method integration [Cell Press 2024].
- **LOGLO-FNO**: Efficient local-global feature learning accepted at ICLR 2025.
- Optical neural engines combining diffractive optical networks with crossbar structures solve time-dependent and time-independent PDEs including Maxwell's equations [Nature Comms 2025].

### 3.8 Transfer Learning and Few-Shot Learning

Transfer learning reduces training data requirements by adapting pre-trained models to new antenna configurations:

- Autoencoder-based transfer learning for MIMO system adaptation across diverse scenarios [Tandfonline 2025].
- Data-free solutions of electromagnetic PDEs using neural networks with extensions to transfer learning [IEEE TAP Special Issue 2024].
- Few-shot learning addresses the common scenario where only a small number of expensive EM simulations are available for a new antenna type.

---

## 4. Optimisation Methods for Antenna Design

### 4.1 Evolutionary and Nature-Inspired Algorithms

**Genetic Algorithm (GA)**: Encodes antenna parameters as chromosomes; applies selection, crossover, and mutation operators. Standard for antenna array synthesis, geometry optimisation, and impedance matching. Typically requires 1000--10,000 function evaluations.

**Particle Swarm Optimisation (PSO)**: Swarm-intelligence approach where candidate solutions adjust positions based on personal and global best experiences. Outperforms GA for many antenna problems; improves SLL by 4.0 dB over GA for circular arrays [Panduro et al.].

**Differential Evolution (DE)**: Vector-difference mutation operator provides efficient exploration. DE outperforms GA by 4.6 dB in SLL reduction for antenna array synthesis [IEEE TAP 2014]. DE is the most commonly used optimiser in surrogate-assisted antenna design.

**Hybrid Algorithms**: Recent work combines multiple metaheuristics (e.g., Salp Swarm + Seagull Optimisation + Naked Mole-Rat Algorithm) for improved exploration-exploitation balance, validated on CEC 2019 benchmarks [Scientific Reports 2025].

### 4.2 Multi-Objective Optimisation

Antenna design inherently involves conflicting objectives (gain vs. size, bandwidth vs. efficiency, directivity vs. cross-polarisation). Multi-objective evolutionary algorithms (MOEAs) find Pareto-optimal trade-off solutions:

- **NSGA-II**: The dominant algorithm for antenna multi-objective optimisation. Recent improvements add adaptive crossover/mutation rates for better convergence on irregular polygon patch antennas [Micromachines 2025]. Performance-constrained variants eliminate solutions failing return-loss requirements during non-dominated sorting [Scientific Reports 2024].
- **NSGA-III**: Reference-point-based approach for many-objective problems (>3 objectives). Integrated with surrogate models for fast processing [ScienceDirect 2024].
- **MOEA/D**: Decomposition-based approach that converts multi-objective problems into scalar subproblems. Competitive with NSGA-III for antenna geometry optimisation [Radio Science 2025].
- **SPEA2**: Strength Pareto approach, compared with MOEA/D and NSGA-III for antenna parameter optimisation.

### 4.3 Bayesian Optimisation

Bayesian optimisation (BO) is the natural framework for simulation-driven antenna design, combining GP surrogates with acquisition functions:

- Expected Improvement (EI) balances exploitation and exploration
- Multi-objective BO (e.g., TSEMO) extends to Pareto front discovery
- Sample-efficient: converges in 50--200 evaluations vs. 1000+ for evolutionary methods
- Scalability limited by GP training cost; addressed by BNN surrogates

### 4.4 Surrogate-Assisted Optimisation

The dominant paradigm combines evolutionary algorithms with surrogate models:

- GA-based optimisation using trained ML models has reduced computational time by 90% compared to conventional optimisation [Springer 2025].
- Variable-fidelity approaches use coarse-mesh simulations for global search and fine-mesh for local refinement, achieving 70% speedup [Scientific Reports 2024].
- Co-kriging multi-fidelity surrogates require approximately 90 high-fidelity EM analyses for convergence [Scientific Reports 2024].
- Active learning strategies with computational budgets of 200--1000 evaluations achieve near-optimal designs with ~85% cost savings [ScienceDirect 2024].

### 4.5 Gradient-Based and Adjoint Methods

For high-dimensional topology optimisation, gradient-based methods scale better than evolutionary approaches:

- **Adjoint Method**: Computes gradients of all N design variables with respect to an objective using only 2 EM simulations (forward + adjoint), regardless of N. Critical for pixel-level topology optimisation with thousands of design variables.
- **Differentiable Simulation**: Time-reversal differentiation of FDTD reduces memory by 98% compared to automatic differentiation while maintaining adjoint-level computational cost [ACS Photonics 2024].
- **Precomputed Numerical Green Function**: Enables ultrafast inverse design by pre-computing static components, dramatically reducing per-iteration cost [Nature Communications 2026].
- **Neural Electromagnetic Topology Optimisation (NETO)**: Incorporates differentiable Maxwell operators into a neural optimisation cycle, reducing design time by 40x compared to iterative FEM [Antenna Journal 2024].

### 4.6 Topology Optimisation

Topology optimisation determines the optimal material distribution within a design domain, enabling discovery of non-intuitive antenna geometries:

- **Density-Based (SIMP)**: Continuous relaxation of binary material assignment; requires gradient computation.
- **Level-Set Methods**: Represent boundaries as zero contour of a level-set function; produces smooth boundaries.
- **Pixel-Based Methods**: Discretise design domain into binary pixels; combinatorial space explored by GA, PSO, or RL.
- **Deep RL for Topology Optimisation**: PPO-based agents learn optimal material layouts with physics-informed rewards from FEA, achieving up to 40% weight reduction while maintaining compliance [MethodsX 2025].

---

## 5. Generative and Inverse Design

### 5.1 Generative Adversarial Networks (GANs)

GANs generate novel antenna geometries by learning the distribution of high-performance designs:

- **ACWGAN**: Auxiliary Classifier Wasserstein GAN generates synthetic electromagnetic field distributions and antenna characteristics across frequencies for multiband IoT antenna design [Wiley 2025].
- **RGAN**: Raw network GAN framework for metasurface inverse design; generates novel designs completely distinct from training data, maximising exploration of the parameter space.
- GANs create more unique and diverse shapes than VAEs, which rely on interpolating training sample features.

### 5.2 Variational Autoencoders (VAEs)

VAEs learn a continuous latent space of antenna geometries, enabling smooth interpolation between designs and gradient-based optimisation in latent space. Used primarily for mechanical metamaterial geometry generation, with growing application to antenna design.

### 5.3 CNN-Based Inverse Design

The forward-inverse paradigm:
1. **Forward model**: CNN maps geometry (binary pixel matrix) to performance (S-parameters, gain)
2. **Inverse model**: Maps desired performance to geometry via:
   - Tandem networks (inverse + forward verifier)
   - Optimisation in CNN latent space
   - BPSO over binary pixel matrices using CNN as surrogate

A 10x10 pixelated microstrip antenna inverse design framework with CNN surrogate trained on 150,000 datasets demonstrates automated structure generation from performance targets [MDPI 2025].

### 5.4 Reinforcement Learning for Antenna Design

Deep Q-Networks (DQNs) model antenna design as a sequential decision-making task where an agent iteratively modifies geometry parameters based on performance feedback. The agent learns design strategies transferable across related antenna classes.

---

## 6. GPU-Accelerated Simulation for ML-Driven Design

### 6.1 GPU-FDTD for Dataset Generation

The ML surrogate paradigm requires large training datasets (1,000--150,000 simulations). GPU-accelerated FDTD is the enabling technology:

- gprMax GPU framework for antenna simulation generates datasets for ML applications, with CUDA implementations achieving 17x single-GPU throughput improvement [arXiv 2025].
- Multi-GPU configurations deliver up to 80x performance increase [Keysight 2024].
- Fine FDTD cell sizes for mmWave antennas (28 GHz, 60 GHz) especially benefit from GPU acceleration.
- Open-source gprMax with OpenCL GPU support enables reproducible research without commercial software licenses.

### 6.2 Integration with ML Pipelines

End-to-end GPU-accelerated workflows:
1. GPU-FDTD generates simulation data
2. GPU-trained neural networks learn surrogates
3. GPU-accelerated optimisation (evolutionary or gradient-based) searches surrogate
4. Candidate designs validated by GPU-FDTD
5. Surrogate updated and refined iteratively

### 6.3 Differentiable GPU Simulators

Emerging differentiable EM simulators (e.g., Meent for optics/metasurfaces) provide analytical gradients via the adjoint method, enabling end-to-end training where EM simulation provides the forward model and gradient information for backpropagation-based optimisation.

---

## 7. Multi-Fidelity and Active Learning Approaches

### 7.1 Variable-Fidelity Simulation

Multi-fidelity frameworks exploit cheap low-fidelity models (coarse mesh, simplified physics) to guide expensive high-fidelity evaluations:

- Co-kriging models fuse low- and high-fidelity simulation data, requiring ~90 high-fidelity evaluations for convergence vs. 200+ for single-fidelity approaches [Scientific Reports 2024].
- Reduction of mesh fidelity is the most universal approach for antenna applications.
- Variable-resolution approaches achieve up to 70% speedup with negligible accuracy loss.

### 7.2 Active Learning and Sample Efficiency

Active learning strategies select the most informative simulation points to minimise total computational budget:

- Model management strategies allocate simulation budgets of 500--1000 evaluations effectively [ScienceDirect 2024].
- Uncertainty-guided sampling concentrates evaluations in regions where the surrogate is most uncertain.
- Combining active learning with variable fidelity yields ~85% cost savings compared to high-fidelity-only approaches.

---

## 8. Manufacturing-Aware Design

### 8.1 Tolerance Analysis and Robust Optimisation

Fabrication inaccuracies affect fundamental antenna parameters (centre frequency, bandwidth, impedance match):

- Conventional design procedures routinely neglect fabrication tolerances, leading to designs that fail in practice.
- Yield-driven design evaluates performance across parameter distributions representing manufacturing uncertainty.
- Response-variability essential directions identify which parameter deviations most affect performance [Scientific Reports 2022].
- Machine learning-assisted robust design uses ML surrogates to efficiently evaluate statistical performance over tolerance ranges.

### 8.2 Additive Manufacturing

3D printing enables conformal antennas on curved surfaces:

- Fused filament fabrication (FFF) for dielectric substrates
- Aerosol jet and inkjet printing for conformal metallisation (line width down to 8 um)
- Electric-field-driven jet printing achieves high-resolution conformal circuits on 3D surfaces
- Optimisation must account for manufacturing-specific constraints (minimum feature size, layer adhesion, surface roughness)

---

## 9. Application Domains

### 9.1 5G/6G Communications

- mmWave antenna arrays at 28 GHz, 39 GHz, 60 GHz
- Massive MIMO beamforming optimisation
- Mutual coupling reduction in compact arrays (target: >25 dB isolation)
- ML-assisted gain prediction for dual-band MIMO designs [Scientific Reports 2025]

### 9.2 Internet of Things (IoT)

- Multiband compact antennas for diverse IoT protocols
- Machine learning-driven design for 5G/6G IoT systems [Springer 2025]
- Size-constrained optimisation for wearable and embedded devices

### 9.3 Reconfigurable Intelligent Surfaces (RIS)

- Phase-programmable metasurface antenna optimisation
- Tandem neural networks for dynamic reconfigurable surface design at microwave frequencies [2023--2024]
- Deep learning for multifunctional vortex beam generation

### 9.4 Satellite and Aerospace

- Phased array antennas for satellite communications
- Conformal antennas for aircraft and UAV platforms
- Antenna placement optimisation on complex platforms (NSGA-II Pareto solutions) [ResearchGate 2024]

---

## 10. Benchmark Datasets and Reproducibility

### 10.1 Publicly Available Datasets

- **Mendeley Antenna Parameters Dataset** (2024): Varied substrate width, patch width, patch length, feedline width, and slot dimensions with gain, directivity, S11, radiated efficiency extracted from simulation.
- **URSI 2024 Microstrip Dataset**: 27,026 simulation entries across three target frequencies (1.5 GHz, 2.4 GHz, 5.8 GHz) via HFSS [GitHub: LC-Linkous/2024-URSI-NRSM-1265].
- **CST 2.4 GHz Patch with Slot Dataset** (2024): Parametric simulation dataset generated over one month using CST parameter sweeps, designed for ML benchmarking [ScienceDirect 2025].
- **PathWave ADS Dataset** (2024): 1,000 antennas simulated from 0.5--10.5 GHz in 0.1 GHz steps across various substrate materials.

### 10.2 Open-Source Software Ecosystem

- **gprMax**: 3D FDTD, GPU-accelerated (OpenCL), Python API [gprmax.com]
- **openEMS**: FDTD, Matlab/Octave scripting, GPL v3 [openems.de]
- **Meep**: FDTD, Python/Scheme, MPI-parallel, primarily photonics [meep.readthedocs.io]
- **NEC2/nec2c**: MoM for wire antennas, multiple free GUIs (4nec2)
- **OpenParEM**: Open-source parallel EM simulators [openparem.org]
- **Meent**: Differentiable EM simulator for ML [GitHub]
- **AntennaCAT**: ML-assisted antenna optimisation toolkit [GitHub: LC-Linkous]

---

## 11. Open Challenges and Research Gaps

1. **Scalability of Inverse Design**: Current pixel-based methods are limited to ~10x10 grids; scaling to realistic resolutions (100x100+) remains computationally challenging.
2. **Generalisation Across Antenna Types**: Most ML surrogates are trained for a single antenna class; transfer learning across fundamentally different antenna types is underexplored.
3. **3D Topology Optimisation**: Nearly all work focuses on 2D planar topologies; extending to full 3D volumetric optimisation (e.g., 3D-printed DRAs, conformal arrays) is an open problem.
4. **Multi-Physics Co-Design**: Thermal, structural, and electromagnetic objectives must be jointly optimised for practical deployments but are rarely addressed together.
5. **Manufacturing Fidelity Gap**: Designs optimised in simulation often underperform when fabricated due to unmodelled manufacturing effects; closing this gap requires manufacturing-aware surrogate models.
6. **Foundation Models for EM**: No equivalent of LLMs exists for electromagnetic simulation; pre-trained foundation models that generalise across EM problems could dramatically reduce per-problem training costs.
7. **Real-Time Adaptive Design**: Reconfigurable antennas require real-time optimisation (millisecond-scale) that current surrogate-based methods cannot yet achieve for complex geometries.
8. **Uncertainty Quantification at Scale**: While BNNs and GPs provide uncertainty estimates, integrating rigorous UQ into high-dimensional, multi-objective antenna optimisation pipelines remains immature.
9. **Differentiable Simulation Maturity**: Differentiable FDTD/FEM tools are emerging but not yet mature enough for production-scale antenna design.
10. **Standardised Benchmarks**: The field lacks standardised benchmark problems (geometry, objectives, constraints) for comparing ML-driven antenna optimisation methods.

---

## 12. Key Textbooks and Foundational References

- Balanis, C.A. "Antenna Theory: Analysis and Design", 4th Ed., Wiley, 2016
- Stutzman, W.L. and Thiele, G.A. "Antenna Theory and Design", 3rd Ed., Wiley, 2012
- Pozar, D.M. "Microwave Engineering", 4th Ed., Wiley, 2011
- Haupt, R.L. "Antenna Arrays: A Computational Approach", Wiley, 2010
- Taflove, A. and Hagness, S.C. "Computational Electrodynamics: The FDTD Method", 3rd Ed., Artech House, 2005
- Jin, J.M. "The Finite Element Method in Electromagnetics", 3rd Ed., Wiley, 2014
- Koziel, S. and Bandler, J.W. "Antenna Design by Simulation-Driven Optimization", Springer, 2014
- Rahmat-Samii, Y. and Michielssen, E. "Electromagnetic Optimization by Genetic Algorithms", Wiley, 1999
- Volakis, J.L. "Antenna Engineering Handbook", 4th Ed., McGraw-Hill, 2007
