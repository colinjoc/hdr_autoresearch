# Literature Review: Welding Parameter Optimisation via Machine Learning and Multi-Objective Optimisation

## Phase 0 -- Deep Literature Review

**Date:** 2026-04-02
**Scope:** Welding metallurgy fundamentals, parameter-quality relationships, ML for weld quality prediction, multi-objective optimisation, defect prediction, process monitoring, physics-informed modelling, small-data inverse design

---

## 1. Welding Metallurgy Fundamentals

### 1.1 Heat Input and Thermal Cycles

The foundational physics of welding revolves around heat input, which governs the thermal cycle experienced by both the weld metal and the heat-affected zone (HAZ). The standard heat input formula is:

    HI (kJ/mm) = (60 * V * I * eta) / (1000 * travel_speed_mm_min)

where V is arc voltage (V), I is welding current (A), eta is thermal/arc efficiency (process-dependent: ~0.6 for GTAW, ~0.8 for GMAW, ~0.9 for SAW), and travel speed is in mm/min (Kou, 2003; Lancaster, 1999).

Heat input directly determines cooling rates, which in turn control microstructural evolution. The cooling time t8/5 -- the time for the weld to cool from 800 C to 500 C -- is the critical metric linking process parameters to metallurgical outcomes. Typical t8/5 values range from 5 to 30 seconds depending on steel grade, thickness, joint geometry, and preheat temperature (Lancaster, 1999; Easterling, 1992).

### 1.2 Solidification and Microstructural Evolution

During solidification, the ratio of temperature gradient (G) to solidification rate (R) controls the solidification mode: planar -> cellular -> columnar dendritic -> equiaxed dendritic, as G/R decreases (Kou, 2003). The product G*R determines the fineness of the solidification structure.

In ferritic and low-alloy steels, the austenite decomposition during cooling produces various transformation products depending on cooling rate:
- **Slow cooling** (high t8/5): Ferrite + pearlite (soft, ductile)
- **Moderate cooling**: Bainite (intermediate strength/toughness)
- **Fast cooling** (low t8/5): Martensite (hard, brittle, crack-susceptible)

Machine learning models have been developed to predict continuous cooling transformation (CCT) diagrams for weld HAZ. A hybrid model using MLP classifiers, k-Nearest Neighbours, and random forest predicted phase transformation temperatures and hardness from chemical composition and cooling rate, trained on 4,100 diagrams (Li et al., 2022). Random forest was found best for predicting pearlite and martensite transformation onset temperatures.

### 1.3 Carbon Equivalent and Weldability

The carbon equivalent (CE) quantifies a steel's susceptibility to hydrogen-induced cold cracking based on chemical composition. The IIW formula is:

    CE = C + Mn/6 + (Cr+Mo+V)/5 + (Ni+Cu)/15

CE serves as the basis for calculating minimum preheat temperatures and required cooling times t8/5 to prevent cold cracking. Steels with CE > 0.45 typically require preheat (Lancaster, 1999).

### 1.4 Heat-Affected Zone (HAZ) Metallurgy

The HAZ experiences thermal cycling without melting and is often the weakest link in welded joints due to:
- Grain coarsening in the coarse-grained HAZ (CGHAZ) adjacent to the fusion line
- Formation of hard, brittle phases (martensite) if cooling is too rapid
- Hydrogen trapping leading to delayed cold cracking
- Loss of precipitation hardening in age-hardened alloys (e.g., Al 6xxx, 7xxx series)

Preheat and interpass temperature control are critical: elevating base metal temperature slows HAZ cooling, shifting transformation products away from martensite toward tougher microstructures. However, excessive interpass temperatures cause grain growth that degrades impact toughness (Easterling, 1992).

### 1.5 Heat Source Modelling

The Goldak double-ellipsoidal heat source model is the de facto standard for welding FEA simulation (Goldak et al., 1984). The model uses two separate Gaussian distributions for the front and rear halves of the heat source, parameterised by semi-axes (a, b, c_f, c_r). Calibrating these parameters has been addressed using:
- ANN-based calibration from weld macrograph measurements (Rajeev et al., 2025)
- Systematic numerical approaches matching simulated and experimental weld pool dimensions
- Neural networks trained with Levenberg-Marquardt algorithms

The Rosenthal analytical solution, while simpler, provides useful first-order estimates for point/line heat sources and serves as physics-informed prior knowledge in hybrid models.

---

## 2. Welding Process Parameters and Their Effects

### 2.1 Primary Parameters

**Welding Current (Amperage):**
The single most influential parameter on weld penetration -- approximately 2.5x more effect than other parameters (Lincoln Electric). Increasing current increases penetration depth, deposition rate, and heat input. In GMAW, current is directly linked to wire feed speed.

**Arc Voltage:**
Controls arc length and bead shape. Increasing voltage flattens the bead (higher width-to-depth ratio) but has virtually no effect on penetration depth. Excessive voltage causes undercut and porosity; insufficient voltage causes stubbing and poor arc stability.

**Travel Speed:**
Inversely affects heat input and bead size. Slower speeds increase penetration (up to a point), bead width, and reinforcement height. Excessive speed causes incomplete fusion; too slow causes excessive heat input and distortion.

**Wire Feed Rate (WFR):**
In GMAW, WFR and current are directly coupled -- increasing WFR increases current and thus penetration. Maximum penetration is achieved at lowest welding speed and highest WFR (Sarikhani & Pouranvari, 2023).

**Contact Tip to Work Distance (CTWD):**
Affects resistive heating of the electrode extension. Increasing CTWD decreases effective amperage. Typical values: 3/8-1/2 inch for short circuit, 3/4 inch for spray transfer (Lincoln Electric).

### 2.2 Secondary Parameters

**Shielding Gas Composition:**
- Pure Ar: Stable arc, good appearance, narrower penetration profile
- Ar/CO2 blends (75/25 to 95/5): Balance of penetration, spatter, and bead quality
- Higher CO2: Deeper penetration but more spatter; improved ductility but lower tensile/yield strength
- He additions: Hotter arc, broader penetration, faster travel speeds
- Ar/CO2/O2 ternary blends: Best for galvanised steels (less pitting, porosity, spatter)

**Gas Flow Rate:**
Insufficient flow causes porosity from atmospheric contamination; excessive flow causes turbulent entrainment of air. Optimal ranges are process and nozzle-diameter dependent (typically 15-25 L/min for GMAW).

**Preheat Temperature:**
Slows cooling rate, reduces hydrogen cracking risk, lowers residual stress. Required when CE > 0.45 or thickness > ~25 mm for carbon steels. Typical range: 50-250 C depending on material and thickness.

**Interpass Temperature:**
Maximum interpass temperature controls grain growth and toughness degradation. Lower interpass gives higher strength but lower toughness; the relationship reverses above a critical threshold.

**Electrode/Torch Angle:**
Drag angle (pointed toward puddle) increases penetration; push angle (pointed away) decreases penetration. Most fillet welds target 45 degrees for even material distribution.

### 2.3 Process-Specific Parameters

**Friction Stir Welding (FSW):** Tool rotation speed (RPM), welding speed, axial force, pin geometry, tilt angle.

**Laser Welding:** Laser power, focal position, beam diameter, pulse frequency/duration (pulsed), oscillation amplitude/frequency.

**Electron Beam Welding (EBW):** Accelerating voltage, beam current, welding speed, focal position, beam oscillation pattern, vacuum level.

**Resistance Spot Welding (RSW):** Welding current, weld time, electrode force, hold time, squeeze time, electrode geometry.

**Wire Arc Additive Manufacturing (WAAM):** Same GMAW/GTAW parameters plus layer planning, interpass time/temperature, deposition strategy, path planning.

---

## 3. Machine Learning for Weld Quality Prediction

### 3.1 Regression Models for Bead Geometry

The prediction of weld bead geometry (width, height/reinforcement, penetration depth, dilution) from process parameters is the most extensively studied ML application in welding.

**ANN-based approaches** dominate the literature. Three-layer backpropagation networks predict bead width and reinforcement with average errors of 0.23 mm and 0.09 mm respectively for GMAW (Park et al., 2021). Neural networks consistently outperform second-order regression models due to their capacity for approximating nonlinear relationships.

**Comparative ML studies** have evaluated multiple algorithms:
- Random Forest and XGBoost achieved >98% accuracy in FSW parameter regression for 2024-T3 aluminium (Matitopanum et al., 2024)
- XGBoost delivered R-squared up to 0.89 with lowest MAE/RMSE for joint load capacity (Mysliwiec et al., 2025)
- CatBoost and Gradient Boosting perform comparably to XGBoost across dissimilar material welding (Shinde et al., 2024)

**Modern ensemble methods** for bead geometry in GMAW compare linear regression, KNN, decision trees, random forests, and SVR for predicting bead width, penetration depth, reinforcement height, and dilution percentage.

### 3.2 Mechanical Property Prediction

**Tensile strength:** ML models using ANN, RF, XGBoost, and MLP predict UTS, YS, and elongation from FSW parameters. ANN models surpass SVM in optimising parameters for tensile strength and hardness (various studies, 2024-2025).

**Hardness:** CCT diagram prediction models link chemical composition and cooling rate to hardness through phase fraction prediction. The martensite fraction is particularly important for hardness prediction in high-strength steels.

**Fatigue life:** ML approaches use nominal stress, R-ratio, material properties, defect class, and stress concentration factor as inputs. Coupled approaches achieve predictions within a +/-1.2 error band on log(N). Transfer learning has been applied for data-driven fatigue assessment across different welded joint types (Braun et al., 2022).

### 3.3 Gaussian Process Regression for Small Data

GPR is particularly well-suited for welding quality prediction with limited experimental data because it:
- Provides both predictions and calibrated uncertainty estimates
- Works well with small training sets (tens to hundreds of samples)
- Enables principled active learning and Bayesian optimisation
- Produces "football-shaped" confidence intervals useful for design exploration

A Gaussian Process Regression Network (GPRN) has been applied to predict weld pool metrics (width, penetration depth) in laser welding of aluminium alloys, using FEA-DoE-GPRN hybrid frameworks (Duggirala et al., 2024).

### 3.4 Physics-Informed Machine Learning

The PHOENIX framework (Physics-informed Hybrid Optimisation for Efficient Neural Intelligence in Manufacturing) integrates physical knowledge into:
1. **Input features:** Physics-derived features (heat input, cooling rate estimates, carbon equivalent) augment raw sensor data
2. **Model architecture:** Physics-informed loss functions, conservation constraints
3. **Dynamic optimisation:** Real-time instability detection and parameter adjustment

A notable approach combines Rosenthal equation-based temperature field estimates with LSTM networks for real-time thermal prediction, using weld pool images to extract heat source parameters and correct the physics model (Li et al., 2025).

Physics-informed neural networks (PINNs) have been used for temperature field prediction in welding and additive manufacturing, integrating boundary conditions and physics-informed loss to reduce error accumulation beyond the active welding zone (Nature Communications, 2025).

### 3.5 Transfer Learning and Domain Adaptation

Transfer learning addresses the challenge of limited welding data by:
- Pre-training on one process/material and fine-tuning on another
- Using CNN features from laser metal deposition for weld defect detection in laser welding
- Federated learning for cross-facility model sharing without data centralisation
- Foundation model surrogates (e.g., TabPFN) providing meta-learned priors for in-context learning from small datasets

Explainable few-shot learning has been developed for online anomaly detection in ultrasonic metal welding with varying configurations (Chen et al., 2024).

---

## 4. Defect Prediction and Classification

### 4.1 Defect Types and Detection

Major weld defects addressed by ML include:
- **Porosity:** Gas entrapment during solidification; detectable via radiography, ultrasound, or real-time voltage signal analysis
- **Cracking:** Hot cracking (solidification), cold cracking (hydrogen-induced), lamellar tearing; AE sensors detect stress waves from crack initiation
- **Lack of fusion/penetration:** Insufficient bonding at interfaces; detectable via radiography or cross-section analysis
- **Distortion:** Residual stress-driven geometric deformation; predictable via FEA or ML surrogates
- **Undercut:** Material loss at weld toe; related to excessive voltage or travel speed
- **Spatter:** Molten metal expulsion; related to transfer mode and shielding gas composition

### 4.2 Image-Based Defect Classification

CNN-based models dominate image-based weld defect classification:
- **ResNet50** achieved 98.75% accuracy on the RIAWELC radiographic dataset for crack, pore, non-penetration, and no-defect classes
- **DenseNet121** achieved 98.88% accuracy with Grad-CAM interpretability
- **ConvNeXt** combining CNN and Vision Transformer achieved 99.52% classification accuracy
- **VGG-inspired models** (WeldVGG) with Grad-CAM++ for visual validation of predictions

Feature extraction approaches include FFT, GLCM, GLDM, texture analysis, and DWT, often used in ensemble architectures.

### 4.3 Real-Time Defect Prediction from Process Signals

For GMAW, CNN-based models using welding voltage signals predict penetration state and surface pores with >97% accuracy and 0.38s inference time (Nature Scientific Reports, 2023).

Statistical parameters from welding current and voltage signals achieve 95-100% diagnosis rates for abnormal/normal classification.

XGBoost combined with Particle Swarm Optimisation achieves high accuracy in weld quality monitoring from process signals.

### 4.4 Residual Stress and Distortion Prediction

ML surrogates for residual stress prediction include:
- Deep neural networks mapping welding parameters directly to stress fields
- Attention-based multi-fidelity networks combining refined and coarse FEM data
- SVR for small-sample, high-dimensional residual stress prediction
- Deep learning frameworks as alternatives to computationally expensive FEA

### 4.5 Synthetic Data Generation for Data-Scarce Scenarios

Generative models address welding data scarcity:
- **GANs** for defect image synthesis, seam tracking, weld-pool generation (Welding in the World, 2025)
- **Improved DCGAN** for GMAW weld defect dataset augmentation addressing class imbalance
- **beta-TC VAE** for modelling weld pool features
- **VAE-GAN hybrids** combining latent space learning with high-quality image generation

The INWELD dataset provides multi-category weld annotations under real-world production conditions for benchmarking.

---

## 5. Multi-Objective Optimisation

### 5.1 Classical Approaches: Taguchi and RSM

**Taguchi method** uses orthogonal arrays (L9, L16, L27) for efficient experimental design, with signal-to-noise ratios for quality characteristic optimisation. ANOVA identifies statistically significant parameters and their relative contributions.

**Response Surface Methodology (RSM)** uses central composite design (CCD) or Box-Behnken design to develop second-order polynomial models capturing parameter interactions. RSM contour and surface plots visualise the effect of parameter combinations on quality responses.

Integration of Taguchi with Grey Relational Analysis (GRA) enables multi-response optimisation by converting multiple quality characteristics into a single Grey Relational Grade.

### 5.2 Evolutionary Multi-Objective Optimisation

**NSGA-II** is the most widely used algorithm for welding parameter optimisation:
- T-shaped bilateral laser welding: NSGA-II and MOPSO optimised ANN outputs for minimising residual stress and deformation (Li et al., 2024)
- RFSSW for AA2024-T3: XGBoost + NSGA-II generated Pareto frontiers balancing multiple quality objectives (Mysliwiec et al., 2025)
- Pulsed GMAW: Neuro-NSGA-II for multi-objective process parameter optimisation
- FSW: NSGA-II for friction stir welding of dissimilar alloys

**MOPSO (Multi-Objective Particle Swarm Optimisation)** provides competitive performance, particularly for T-shaped welding joints.

### 5.3 Bayesian Optimisation

Bayesian optimisation (BO) is increasingly applied to welding for:
- Sample-efficient exploration with GPR surrogates
- Expected Improvement (EI) and Upper Confidence Bound (UCB) acquisition functions
- Adaptive surrogate model selection for automated experimental design
- Target-oriented BO where the number of iterations must be minimised

GPR models with physics-informed kernels (PIK) incorporating FEM simulation prior knowledge have shown particular promise for parameter space exploration with limited experiments (Bayesian optimization with adaptive surrogate models, npj Computational Materials, 2021).

### 5.4 Reinforcement Learning

Deep reinforcement learning (DRL) frameworks for welding optimisation include:
- Deep Q-learning for welding path optimisation to minimise distortion
- Actor-critic methods for real-time laser welding power control
- Deep Predictive Reward Reinforcement Learning (DPRRL-net) for laser oscillation welding optimising porosity and penetration
- Closed-loop adaptive control learning policies without prior knowledge of process dynamics

A DRL framework for induction welding demonstrated superior spatiotemporal thermal characteristics compared to state-of-the-art approaches (ScienceDirect, 2024).

---

## 6. Process Monitoring and Sensing

### 6.1 Sensor Modalities

**Infrared thermography:** Converts IR radiation to temperature maps; monitors weld pool temperature correlated with penetration depth. Tracks thermal patterns to detect porosity, lack of fusion, asymmetric heat distribution.

**Acoustic emission (AE):** Captures high-frequency stress waves from crack initiation and propagation. Real-time crack detection during welding. Combined with air-coupled ultrasonics for comprehensive monitoring.

**Vision systems:** High-speed cameras for weld pool imaging; structured light for bead profile measurement; laser line scanners for geometric inspection.

**Electrical signals:** Current and voltage waveforms encode information about arc stability, metal transfer mode, and defect formation.

### 6.2 Multi-Sensor Fusion

Sensor fusion combining thermal, vision, and acoustic data enables defect detection rates unachievable by any single modality. AI inference engines process fused data streams in real time for zero-defect manufacturing targets.

Real-time GTAW defect detection systems integrate IR cameras, laser line scanners, and acoustic sensors, with extracted thermal, geometrical, and acoustic features fed to ensemble ML models (multi-sensor studies, 2024).

### 6.3 Digital Twin and Industry 4.0

Welding digital twins integrate:
- Real-time sensor data from IoT devices (temperature, pressure, current, voltage)
- FEA-based process simulation
- ML-based quality prediction
- Adaptive feedback for real-time parameter adjustment

Deployment results show 75% reduction in process failures (from 20/month to 5/month) through root cause analysis of thermographic and sensor data. Systems achieve 94.8% defect detection accuracy with low latency (various studies, 2024).

### 6.4 Weld Pool Monitoring

MobileNetV2-based transfer learning pretrained on ImageNet recognises GTAW weld penetration states with 99.88% validation accuracy and 65ms per-image inference time.

Conditional Variational Autoencoders (CVAE) generate realistic 2D weld pool and keyhole geometries from welding parameters (Journal of Laser Applications, 2025).

YOLOv4 object detection automatically measures keyhole apertures in coaxial high-speed observation systems for laser welding.

---

## 7. Small-Data and Inverse Design Strategies

### 7.1 Active Learning

Active learning iteratively selects the most informative experiments for labelling, efficiently navigating the parameter space to identify promising candidates. The approach combines:
- GPR surrogate model predictions
- Uncertainty quantification for exploration
- Utility/acquisition functions for exploitation-exploration trade-off

Active learning with deep Gaussian process surrogates has been demonstrated for materials design applications similar to welding parameter optimisation (Sauer et al., 2022).

### 7.2 Foundation Model Surrogates

Recent advances in foundation model-based surrogates (e.g., TabPFN) use meta-learned priors from millions of synthetic regression tasks to:
- Perform probabilistic inference in single forward passes
- Eliminate dataset-specific retraining
- Provide calibrated uncertainty in small-data settings (tens to hundreds of labelled examples)
- Accelerate active learning loops

### 7.3 Multi-Fidelity Modelling

Combining low-fidelity (coarse FEM, analytical models) with high-fidelity (refined FEM, experimental) data through:
- Multi-fidelity Gaussian processes
- Attention-based multi-fidelity neural networks
- Transfer learning from simulation to experiment

### 7.4 Data Augmentation

For small welding datasets:
- Improved DCGAN for generating synthetic defect images
- Physics-based simulation (FEA) for generating virtual experiment data
- Mixup and SMOTE for tabular parameter-quality data
- Domain randomisation for robust generalisation

---

## 8. Specialised Welding Domains

### 8.1 Underwater Wet Welding

Unique challenges include:
- Extremely high cooling rates from water contact
- Hydrostatic pressure effects on arc behaviour (increased arc voltage, decreased arc length)
- Hydrogen embrittlement from water decomposition
- Limited depth capability (~400m for dry hyperbaric, ~2500m with special techniques)

Parameter optimisation focuses on electrode type, current, and diameter using statistical DoE methods.

### 8.2 Wire Arc Additive Manufacturing (WAAM)

Extends traditional welding to layer-by-layer deposition:
- GPR models optimise wire feed rate, travel speed, and interpass time
- ANN models predict bead width and height from wire feed speed, travel speed, and interpass temperature
- NSGA-II for multi-objective optimisation of Inconel 625 bead characteristics
- Layer geometry variability requires adaptive control strategies

### 8.3 Dissimilar Material Welding

Joining different metals (e.g., steel-aluminium, copper-aluminium) introduces:
- Intermetallic compound formation
- Coefficient of thermal expansion mismatch
- Galvanic corrosion concerns
- Complex metallurgical interactions requiring ML to navigate

### 8.4 Laser Keyhole Welding

Keyhole instability in deep-penetration welding requires:
- Real-time keyhole monitoring via coaxial high-speed cameras
- Deep learning (YOLO, CNN) for keyhole aperture measurement
- Reinforcement learning for adaptive power control
- CVAE-based weld pool/keyhole geometry prediction

---

## 9. Explainability and Interpretability

### 9.1 XAI Methods for Welding

- **SHAP:** Global and local feature importance based on Shapley values from game theory; applicable to any model type
- **LIME:** Local interpretable model-agnostic explanations using local surrogate models
- **Grad-CAM/Grad-CAM++:** Class-discriminative saliency maps for CNN-based defect classification
- **Feature importance ranking:** Tree-based methods (RF, XGBoost) provide built-in feature importance

### 9.2 Industrial Trust and Adoption

Explainability is critical for industrial adoption because:
- Welding codes and standards require documented rationale
- Safety-critical applications demand transparent decision-making
- Domain experts need to validate model recommendations against metallurgical knowledge
- Regulatory compliance (e.g., ASME, AWS, EN/ISO standards) requires auditable processes

---

## 10. Research Gaps and Opportunities

1. **Small-data regime:** Most ML studies use relatively small datasets (10s-100s of experiments) but do not systematically address sample efficiency or active learning strategies for welding
2. **Physics-informed features:** Derived quantities (heat input, cooling rate, carbon equivalent) are underutilised as features; most studies use raw parameters
3. **Cross-process transfer:** Limited work on transferring learned models between welding processes (e.g., GMAW to GTAW) or materials
4. **Multi-fidelity integration:** Combining analytical solutions (Rosenthal), FEA, and experimental data in a principled multi-fidelity framework
5. **Uncertainty quantification:** Most studies report point predictions without calibrated uncertainty estimates critical for safety-critical applications
6. **Inverse design:** Forward prediction (parameters -> quality) is well-studied; inverse design (quality -> parameters) receives less attention
7. **Temporal dynamics:** Most models are static; incorporating time-series process signals for real-time adaptive optimisation is emerging
8. **Benchmark datasets:** No widely adopted benchmark dataset exists for welding parameter-quality prediction (unlike image classification)
9. **Interpretability:** SHAP/LIME are applied post-hoc; building inherently interpretable models for welding is largely unexplored
10. **Multi-objective Bayesian optimisation:** Combining BO with Pareto-optimal search for simultaneously optimising conflicting welding objectives

---

## References (Selected)

See `papers.csv` for the full bibliography of 100+ entries. Key foundational references:

- Kou, S. (2003). *Welding Metallurgy*, 2nd ed. Wiley.
- Lancaster, J.F. (1999). *Metallurgy of Welding*, 6th ed. Abington Publishing.
- Easterling, K.E. (1992). *Introduction to the Physical Metallurgy of Welding*, 2nd ed. Butterworth-Heinemann.
- Goldak, J., Chakravarti, A., Bibby, M. (1984). A new finite element model for welding heat sources. *Metallurgical Transactions B*, 15(2), 299-305.
- Messler, R.W. (1999). *Principles of Welding: Processes, Physics, Chemistry, and Metallurgy*. Wiley.
- Lippold, J.C. (2015). *Welding Metallurgy and Weldability*. Wiley.
- AWS WM1.4:1994. *Fundamentals of Welding Metallurgy*, Vol. 1.
