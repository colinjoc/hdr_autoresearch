# Literature Review: Paint/Coating Formulation Optimisation

## 1. Coating Science Fundamentals

### 1.1 Composition of Paints and Coatings

A paint or coating formulation consists of four to six primary components, each serving distinct functional roles [Dispersetech Guide; SubsTech]:

1. **Binder (Resin)**: The film-forming polymer that provides adhesion, durability, and mechanical integrity. Types include acrylics, alkyds, epoxies, polyurethanes, silicones, and vinyl esters. The binder determines most of the coating's fundamental properties -- adhesion, chemical resistance, flexibility, UV stability, and hardness.

2. **Pigment**: Solid particles dispersed in the binder to impart colour and opacity. Titanium dioxide (TiO2) is the dominant white pigment due to its extremely high refractive index (2.7 for rutile), providing hiding power through light scattering rather than absorption [SpecialChem; UL Prospector]. Optimal scattering occurs at particle sizes around 200-280 nm. Coloured pigments include iron oxides, phthalocyanines, and organic dyes.

3. **Extenders/Fillers**: Lower-cost mineral particles (calcium carbonate, kaolin, talc, mica, barytes, silica) that reduce cost and modify properties. Calcium carbonate is the most widely used extender, offering easy dispersibility and low oil absorption [PCI Mag; SpecialChem]. Talc provides sheen control and UV durability improvement (25% improvement at 20 wt%). Kaolin improves suspension, hiding power extension, and film hardness.

4. **Solvent/Carrier**: Water (in latex/waterborne systems) or organic solvents (in solventborne systems) that control viscosity for application. The solvent evaporates during film formation, leaving the solid coating. Hansen solubility parameters (HSP) with three components -- dispersion (dD), polarity (dP), and hydrogen bonding (dH) -- guide rational solvent selection and blend optimisation [Wikipedia HSP; SpecialChem; Springer 2025].

5. **Additives**: Small amounts of functional materials including:
   - Wetting/dispersing agents (surfactants, 0.1-2%) for pigment stabilisation
   - Rheology modifiers (HEUR, HASE thickeners, clay, fumed silica)
   - Defoamers, biocides, coalescing aids
   - UV stabilisers (HALS, UVA)
   - Adhesion promoters, flow agents, catalysts/driers

6. **Crosslinkers/Hardeners**: In two-component systems, separate curing agents (amine hardeners for epoxies, isocyanates for polyurethanes) that react with the binder to form crosslinked networks.

### 1.2 PVC and CPVC Theory

The **Pigment Volume Concentration (PVC)** is defined as the volume percentage of solid particles (pigment + extender) relative to the total dry film volume (solids only, after volatiles evaporate) [ScienceDirect; UL Prospector; DisperseTech]:

```
PVC = Volume(pigment + extender) / Volume(pigment + extender + binder) x 100%
```

The **Critical Pigment Volume Concentration (CPVC)** is the PVC at which there is exactly enough binder to fill the interstices between closely packed pigment particles. The CPVC typically falls in the 30-60% range depending on the pigment/extender system and can be calculated from oil absorption values.

**Below CPVC**: Excess binder fills all voids, producing a continuous film with maximum barrier properties, gloss, and mechanical strength.

**Above CPVC**: Insufficient binder to coat all pigment particles; air voids form in the film. While this can increase hiding power through air-void scattering, it causes severe deterioration in:
- Mechanical strength (cohesive failure risk)
- Barrier properties (moisture and gas permeation)
- Gloss (dramatic decrease)
- Stain resistance
- Weatherability

Most architectural paints are formulated near or slightly below CPVC for flat finishes (PVC ~55-65%) and well below CPVC for gloss finishes (PVC ~20-35%). The PVC/CPVC ratio is the single most important formulation parameter, governing the transition from binder-continuous to pigment-continuous films.

**TiO2 scattering efficiency** is particularly sensitive to PVC: between 15-30% PVC, scattering efficiency per particle decreases due to crowding effects. Above 30%, particle interference further reduces scattering power, making increased TiO2 loading counterproductive [UL Prospector; Chemours Ti-Pure].

### 1.3 Binder Chemistry

#### Acrylic Latex Systems
Acrylic and vinyl-acrylic emulsions dominate architectural waterborne coatings due to low cost, versatility, and tuneable properties. The glass transition temperature (Tg) is the critical parameter controlling film formation and service performance [MC Polymers; SpecialChem]:
- Tg must be below the minimum film formation temperature (MFFT) for particle coalescence
- Lower Tg: softer, more flexible films; better film formation but worse block resistance
- Higher Tg: harder, more durable films; but require coalescing aids for film formation
- Monomer selection (methyl methacrylate for high Tg; butyl acrylate for low Tg) tunes the Tg via the Fox equation
- Multistage polymer design creates core-shell particles with different Tg domains, optimising both film formation and hardness

#### Alkyd Resins
Alkyd resins are oil-modified polyesters classified by oil length [Sheboygan Paint; UL Prospector; Wikipedia]:
- **Short oil** (~30% oil): hard, rigid, fast-dry; used in industrial baking enamels
- **Medium oil** (~50% oil): balanced properties; brushability and durability
- **Long oil** (~60% oil): flexible, slow-dry, excellent brushability; architectural trim paints

Drying occurs by both solvent evaporation (physical drying) and autoxidative crosslinking of unsaturated fatty acid chains in the presence of atmospheric oxygen, catalysed by metal drier compounds (cobalt for surface dry, zirconium for through dry). Bio-based alkyds from soybean, linseed, castor, and tung oils are an active sustainability research area.

#### Epoxy Systems
Epoxy-amine coatings form crosslinked networks through the reaction of epoxide groups with amine hydrogens. The stoichiometric NCO/OH or amine-hydrogen/epoxide ratio critically determines final properties [PCI Mag; UL Prospector; ACS Appl. Polym. Mater.]:
- **1:1 stoichiometry**: maximum crosslink density, highest Tg, best chemical resistance
- **Excess amine**: reduced Tg, more flexibility, but potential amine blush
- **Excess epoxy**: hydrolysis risk, increased moisture sensitivity
- Practical coatings often use 5-10% excess isocyanate/hardener for compensation

#### Polyurethane Systems
Polyurethane coatings are formed by the reaction of isocyanate (NCO) groups with polyol (OH) groups. The NCO/OH ratio governs crosslink density and properties [Dongsen Chem; PMC; PCI Mag]:
- Higher NCO/OH: greater rigidity, higher Tg (50 to 84 degC), better chemical resistance
- Lower NCO/OH: greater flexibility, lower modulus
- High-build coatings: 3-6% excess NCO; thin coatings: 5-10% excess NCO

### 1.4 Film Formation and Drying

Film formation from waterborne latex coatings proceeds in four stages [ACS Appl. Mater. Interfaces 2024; Hoy 1996; Scott Bader]:

1. **Water evaporation**: Particles concentrate as water evaporates at constant rate
2. **Particle packing**: Close-packed array forms; transition from dilute to concentrated regime
3. **Particle deformation**: Capillary forces and surface tension deform soft particles; requires T > MFFT
4. **Coalescence/Interdiffusion**: Polymer chains diffuse across particle boundaries; continuous film forms

Coalescing aids (temporary plasticisers like Texanol) lower the effective Tg to enable film formation at ambient temperature and then slowly evaporate, restoring hardness. For solventborne systems, the drying model involves solvent evaporation at the surface (volatility-controlled) transitioning to diffusion-controlled transport as the film solidifies.

Crosslink density in thermoset coatings can be quantified via DMA (rubbery plateau modulus), solvent swelling (Flory-Rehner equation), or DSC (residual cure enthalpy) [PCI Mag 2018; TA Instruments].

---

## 2. Formulation Design and Optimisation Methods

### 2.1 Traditional Approaches

#### One-Factor-at-a-Time (OFAT)
The traditional coatings development approach varies one ingredient at a time while holding others constant. This is inefficient, cannot detect interactions between factors, and explores only a small fraction of the design space.

#### Design of Experiments (DOE)
DOE provides a structured, statistically rigorous approach that reveals effects and interactions of multiple variables simultaneously [Roessler 2008; PCI Mag 2012; Anderson 2025]:

- **Factorial designs**: Full or fractional factorials for screening process variables
- **Mixture designs**: Specialised for formulations where components must sum to 100%
  - Simplex lattice designs (Scheffe polynomials)
  - Simplex centroid designs
  - Extreme vertex designs for constrained regions
  - D-optimal designs for irregular design spaces
- **Response Surface Methodology (RSM)**: Central composite or Box-Behnken designs for optimising continuous process variables
- **Combined mixture-process designs**: Simultaneously vary composition and process parameters

Scheffe polynomial models for mixtures include linear, quadratic, and special cubic terms that capture synergistic and antagonistic blending effects [SIAM; Penn State; Stat-Ease]. The quadratic Scheffe model is:

```
y = sum_i(b_i*x_i) + sum_{i<j}(b_ij*x_i*x_j)
```

where x_i are mixture component proportions and b_ij capture nonlinear blending.

### 2.2 Computational Design Tools

Several computational tools support coating formulation design:

- **DOW Paint Vision**: Digital platform with the industry's largest formulation database; includes Formulation Xpert for ingredient-application matching and OpTiO2nizer for reducing TiO2 usage [Dow Inc.]
- **Allchemist**: Digital formulation platform covering the entire development workflow [Allchemist]
- **X-Rite Smart Formulation**: Reduces effect paint iterations from 10+ to 2-4 with first-attempt accuracy of dE 3-3.5 [PCI Mag 2024]
- **Computer-Aided Product Design (CAPD)**: Combines databases and physicochemical property models for systematic formulation screening [ScienceDirect 2021]
- **Hansen Solubility Parameter tools**: Including a 2025 open-source Python tool for predicting optimal solvent blends [JCTR 2025]
- **Digital Twins**: Durr's spray booth digital twin reduces test paint runs by >50% [Durr]; BaseTwoAI provides digital twins for formulation optimisation [BaseTwoAI]

### 2.3 Evolutionary and Metaheuristic Optimisation

Evolutionary algorithms have been applied to coating formulation:

- **EMMA (Evolutionary Model-based Multiresponse Approach)**: Plans experiments and simultaneously models material properties for sol-gel coating optimisation, minimising experimental effort while optimising multiple responses [Hyndman et al.]
- **Genetic Algorithms**: Applied to thin film stack optimisation and optical coating design using real-coded representations
- **MOSPO (Multi-objective Stochastic Paint Optimizer)**: A novel metaheuristic inspired by colour theory for multi-objective optimisation [Neural Comput. Applic. 2022]
- **NSGA-II**: Applied to thermal barrier ceramic coatings for multi-criteria material selection [Shi et al. 2023]

---

## 3. Machine Learning for Coating Properties

### 3.1 Property Prediction Models

Machine learning has been applied to predict various coating properties from formulation inputs:

**Supervised regression models** are the dominant approach:
- **Random Forest / Extra Trees**: Effective for coating thickness prediction from 22-23 input features [ACS Omega 2023]
- **Gradient Boosting / XGBoost**: Achieves 99.9% accuracy for nano-film thickness prediction [Langmuir 2023]; strong for atmospheric corrosion rate prediction [Coatings MDPI 2025]
- **Neural Networks**: ANNs model particle size distribution effects on powder coating gloss and roughness [Powder Technology 2025]; wide applications including thickness, hardness, tribological properties [Materials Today Proceedings 2021]
- **Gaussian Process Regression**: Provides uncertainty estimates essential for active learning; used for lacquer formulation sequential design [Prog. Org. Coat. 2025]
- **Support Vector Regression**: Competitive for coating thickness and property prediction [ACS Omega 2023]

**Key target properties modelled**:
- Gloss, hiding power, colour
- Hardness (pencil, Konig, nanoindentation)
- Adhesion (pull-off, crosshatch)
- Flexibility (mandrel bend, impact resistance)
- Viscosity and rheological properties
- Corrosion protection (EIS impedance, salt spray hours)
- Weathering durability (gloss retention, colour change dE)

### 3.2 High-Throughput Experimentation (HTE)

Combinatorial and high-throughput methods accelerate coating data generation [ACS Comb. Sci. 2005, 2011, 2016]:

- Robotic automated synthesis with parallel processing and miniaturisation
- High-throughput testing of cure speed, hardness, scratch resistance, impact toughness
- Dow Chemical's industrial HTE platform for coatings research
- HTE for UV-cured automotive coating curing parameter optimisation [Anal. Chem. 2003]
- Automated weathering evaluation and combinatorial lead scale-up
- Typical throughput: 100-1000x faster than conventional testing

### 3.3 Interpretable and Explainable ML

Interpretability is critical for coating formulators to trust and act on ML recommendations:

- **SHAP (SHapley Additive exPlanations)**: Provides feature importance with directionality; mean absolute SHAP values identify which formulation variables most influence each property [Christoph Molnar; DataCamp]
- **Partial Dependence Plots**: Show marginal effect of individual variables
- **Interpretable models**: The 2025 lacquer formulation study specifically used "explainable machine learning" with interpretable models to enhance coating development [Prog. Org. Coat. 2025]
- Gradient boosting models with SHAP have been used to identify key environmental factors and physical properties affecting coating degradation [npj Mater. Degrad. 2025]

### 3.4 Advanced ML Approaches

**Transfer Learning**: Addresses the small-data problem prevalent in coating formulation [Nature Comms 2021; ACS Central Sci. 2020]:
- Cross-property transfer: models trained on abundant property data fine-tuned on scarce target properties
- Shotgun transfer learning outperforms from-scratch models for ~69% of materials datasets
- Applicable when coating property measurements are expensive (weathering, corrosion)

**Graph Neural Networks**: Emerging for polymer property prediction relevant to binder design [ACS Polymers Au 2022; npj Comput. Mater. 2023]:
- Predict Tg, Tm, density, elastic modulus from molecular graphs
- Handle polymer complexity (ensembles of similar molecules)
- End-to-end learning without hand-crafted descriptors

**Generative Models for Inverse Design** [arXiv 2024; NSR 2022]:
- VAE (Variational Autoencoder): learns continuous latent space for formulation generation
- GAN (Generative Adversarial Network): generates novel compositions conditioned on target properties
- Diffusion Models: emerging for high-quality materials generation
- Key challenge: navigating infinite composition space toward target regions

### 3.5 Bayesian Optimisation and Active Learning

Bayesian optimisation (BO) is particularly well-suited to coating formulation because it handles expensive evaluations, noisy observations, and high-dimensional spaces [npj Comput. Mater. 2021; Nature Comms 2020]:

- **Surrogate models**: Gaussian processes fit available data and predict outcomes with uncertainty
- **Acquisition functions**: Balance exploration (uncertain regions) and exploitation (promising regions)
- **Closed-loop systems**: CAMEO demonstrated autonomous materials exploration at synchrotron beamlines; directly applicable to automated coating formulation [Nature Comms 2020]
- **Batch active learning**: Selects multiple experiments per iteration using predictive covariance [arXiv 2024]
- **Multi-fidelity approaches**: Combine cheap screening experiments with expensive full testing

Active learning in materials science selects each subsequent experiment to maximise knowledge toward the user's goal, with BO-based strategies reducing required experiments by 5-10x compared to grid search [npj Comput. Mater. 2019; Acc. Chem. Res. 2021].

---

## 4. Multi-Objective Optimisation

Coating formulation inherently involves competing objectives:
- **Performance maximisation**: hardness, adhesion, gloss, weathering resistance, corrosion protection
- **Cost minimisation**: raw material costs, especially TiO2 and specialty additives
- **Environmental minimisation**: VOC emissions, carbon footprint, toxicity
- **Process constraints**: viscosity windows, pot life, cure conditions

### 4.1 Pareto Optimisation

Solutions are Pareto-optimal when no objective can be improved without degrading another. Key algorithms applied to materials [MGEA 2023; Nature Comms 2023]:

- **NSGA-II**: Most commonly used evolutionary multi-objective algorithm
- **MOPSO (Multi-Objective Particle Swarm)**: Applied to concrete mix optimisation (analogous problem)
- **Scalarisation**: Weighted-sum approach when preference structure is known
- **TOPSIS**: Multi-criteria decision making for coating material selection [Mater. Design 2013]
- **Ashby approach**: Material property charts for visual Pareto front identification

### 4.2 Concrete Mix Design Analogy

Concrete mix design optimisation shares the same mathematical structure as paint formulation [npj Comput. Mater. 2022; J. Building Eng. 2023; Sci. Reports 2025]:
- Multiple interacting mixture components (cement:binder, aggregate:pigment, water:solvent, admixtures:additives)
- Competing objectives (strength/hardness, cost, sustainability/cement reduction)
- Constraint satisfaction (workability/viscosity, setting time/pot life)
- ML surrogate models + multi-objective evolutionary optimisation
- DNN + MOPSO frameworks achieving simultaneous strength maximisation, cost minimisation, and environmental impact reduction

This structural analogy means methodologies validated in concrete science can be directly transferred to paint formulation.

---

## 5. Sustainability: Low-VOC and Waterborne Systems

### 5.1 Regulatory and Market Drivers

The low-VOC paints and coatings market was valued at $27.6 billion in 2024, projected to reach $40.1 billion by 2035 [MRFR]. Key drivers include:
- EPA VOC regulations with strict g/L limits by category
- LEED, WELL, and BREEAM certification requirements
- EU Directive 2004/42/EC on decorative coatings
- Consumer preference for low-odour, low-toxicity products

### 5.2 Technology Approaches

**Waterborne Systems**: Dominate the sustainability transition [RSC Sustainability 2024]:
- Acrylic latex: mature technology, excellent exterior durability
- Waterborne alkyds/alkyd emulsions: combine alkyd performance with low VOC
- Waterborne epoxies and polyurethanes: advancing for industrial/protective applications
- Waterborne basecoats now ~60% share in automotive OEM lines

**High-Solids Coatings**: Reduce VOC by minimising solvent fraction while maintaining application viscosity.

**Powder Coatings**: Zero-VOC technology; challenges in low-temperature cure optimisation [PCI Mag; SpecialChem]:
- Industrial standard shifting from 180 to 160 degC cure
- Advanced hybrid systems achieving 125-130 degC for MDF substrates
- Flow agents (polyacrylate on silica carriers) critical for levelling and degassing

**UV/EB Curable Coatings**: Near-zero VOC; rapid cure [Macromolecules 2022; MDPI 2024]:
- Formulation: oligomer + reactive monomer + photoinitiator (1-20%) + additives
- Monomer/oligomer ratio controls cure speed and final properties
- Photoinitiator selection must match UV lamp emission spectrum

**Bio-Based Materials** [PMC 2023; JRTE 2024; RSC Advances 2023]:
- Vegetable oil polyols (castor, soybean, linseed) for bio-based polyurethanes
- Bio-based alkyds from renewable triglycerides
- Axalta BioCore (2024): up to 70% bio-renewable content with comparable corrosion resistance
- Challenges: reproducibility, large-scale production, weathering susceptibility

### 5.3 Green Chemistry for Solvents

A 2024 solvent sustainability guide for the paints and coatings industry was published in Green Chemistry [RSC 2024], providing systematic evaluation criteria for solvent selection based on environmental, health, and safety metrics. Combined with HSP-based computational tools, this enables rational replacement of hazardous solvents with greener alternatives while maintaining formulation performance.

---

## 6. Specific Coating Systems and Applications

### 6.1 Automotive Coatings

Modern automotive OEM coating systems comprise four layers totalling ~100 microns [Wikipedia; ACA]:
1. **Electrocoat (E-coat)**: Cathodic epoxy primer; corrosion protection (15-25 um)
2. **Primer/surfacer**: Chip resistance, surface smoothing (25-35 um)
3. **Basecoat**: Colour and effect (metallic, pearlescent); predominantly waterborne acrylic-polyurethane (10-20 um)
4. **Clearcoat**: Gloss, UV protection, scratch resistance; 1K bake for metal bodies (140 degC), 2K for plastic parts (15-45 um)

### 6.2 Protective/Anticorrosion Coatings

- **Zinc-rich primers**: 55-85 wt% zinc in dry film; dual protection via cathodic protection (sacrificial anode) and barrier (corrosion product pore-sealing) [Prog. Org. Coat. 2021]. Graphene and conductive additives can reduce zinc loading while maintaining performance.
- **Epoxy-polyurethane hybrids**: 5-15% epoxy content increases tensile strength (39.1 to 86.3 MPa), adhesion (2.5 to 8.3 MPa), and thermal stability (320 to 390 degC decomposition) [Polymers MDPI 2025]
- **EIS characterisation**: Electrochemical impedance spectroscopy is the standard method for quantitative barrier performance assessment; |Z|0.01Hz values > 10^9 ohm.cm2 indicate excellent protection [PMC 2022; Mater. Corros. 2024]

### 6.3 Smart and Functional Coatings

- **Self-healing coatings**: Microcapsule-based systems with encapsulated healing agents; double-walled capsules improve stability and efficiency; pH/wettability-responsive release [Adv. Sci. 2025; MDPI 2024]
- **Intumescent fire-protective coatings**: Formulated with ammonium polyphosphate (acid source), pentaerythritol (carbon source), melamine (blowing agent), and expandable graphite; optimal graphite loading typically 5-22% [Fire MDPI 2025; PMC 2022]
- **Superhydrophobic coatings**: Silicone-based with micro/nano textured surfaces; PDMS brush grafting achieves contact angle hysteresis <1 deg [PMC 2023]
- **Nanocomposite barrier coatings**: Graphene (0.5 vol%) reduces OTR by ~90%; clay and GO multilayers effective at high humidity [ACS Omega 2023; Prog. Org. Coat. 2025]
- **Antifouling marine coatings**: Cu2O biocide-based (7-75 wt% Cu) with controlled release profiles; emerging biocide-free foul-release silicone systems [Biofouling 2023]

### 6.4 Coating Testing and Characterisation

Standard test methods relevant to formulation optimisation:
- **Adhesion**: ASTM D3359 (crosshatch tape), ASTM D4541 (pull-off dolly)
- **Hardness**: Pencil hardness (ASTM D3363), Konig/Persoz pendulum, nanoindentation
- **Flexibility**: Mandrel bend (ASTM D522), impact resistance (ASTM D2794)
- **Gloss**: 20/60/85 degree gloss meter (ASTM D523)
- **Weathering**: Accelerated (QUV, Xenon arc per ASTM G154/G155); natural (ASTM D1014)
- **Corrosion**: Salt spray (ASTM B117), cyclic corrosion, EIS (ISO 16773)
- **Viscosity/Rheology**: Stormer viscometer, rotational viscometry at multiple shear rates

Accelerated weathering remains an imperfect predictor of real-world performance because protocols distort degradation chemistry and physical failure modes [ACA 2020; AMPP 2023]. Ten-year outdoor studies show variable correlation with accelerated devices [Prog. Org. Coat. 2013].

---

## 7. Open Challenges and Research Gaps

### 7.1 Data Scarcity and Quality
- No large-scale open paint formulation database exists; data is fragmented across proprietary company databases, patents, and literature
- Formulation data is inherently compositional (constrained to sum to 100%), requiring specialised ML approaches
- Measurement noise in coating properties (especially weathering, corrosion) adds uncertainty
- Transfer learning and data augmentation methods are underexplored for coatings

### 7.2 High-Dimensional Composition Space
- A typical coating formulation has 10-30 adjustable ingredients with continuous composition ranges
- Interaction effects between components are prevalent and poorly understood
- The curse of dimensionality limits DOE approaches; active learning and BO offer relief but are underutilised in industry

### 7.3 Multi-Scale, Multi-Physics Modelling
- Film formation involves coupled heat/mass transfer, polymer physics, and surface chemistry
- No unified model connects molecular-level binder design to macro-scale coating performance
- Digital twins exist for spray application but not for composition-property relationships

### 7.4 Sustainability Constraints
- Simultaneous optimisation of performance, cost, and environmental impact is rarely addressed formally
- Life-cycle assessment integration with formulation optimisation is nascent
- Bio-based feedstock variability introduces batch-to-batch inconsistency

### 7.5 Accelerated Testing to Lifetime Prediction
- The coating industry's century-old challenge: reliably predicting 10-20 year outdoor performance from short-term tests [AMPP 2023]
- ML-based degradation prediction from accelerated data is emerging but not validated at scale
- Computer vision for automated test evaluation (crosscut, blister rating) shows promise but needs standardisation

### 7.6 Inverse Formulation Design
- Given target property specifications, algorithmically generating optimal formulations remains unsolved
- Generative models (VAE, GAN) are proven in small-molecule and alloy design but unapplied to paint formulation
- Constraint satisfaction (cost, regulatory, supply chain) adds complexity beyond pure property matching

### 7.7 Integration of Domain Knowledge
- Embedding established formulation rules (PVC/CPVC theory, stoichiometry constraints) into ML models as physics-informed priors
- Hybrid models combining mechanistic understanding with data-driven flexibility
- Encoding formulator expertise and heuristics into algorithmic frameworks

---

## References

See papers.csv for the complete bibliography of 115 entries covering coating science fundamentals, ML for coatings, optimisation methods, DOE, sustainability, and specific coating systems.
