# Literature Review: 3D Printing Parameter Optimisation via Machine Learning

## Scope

This review covers the optimisation of Fused Deposition Modeling (FDM) / Fused Filament Fabrication (FFF) process parameters using machine learning and multi-objective optimisation methods. The goal is to maximise mechanical properties (tensile strength, surface finish, dimensional accuracy) while minimising print time and material usage, framed as a multi-objective inverse design problem from tabular data.

120 papers are catalogued in `papers.csv`. The review is organised into 7 themes.

---

## Theme 1: FDM Process Physics

### Extrusion and Deposition Mechanics

FDM works by melting thermoplastic filament (typically at 190-250C depending on material) through a heated nozzle and depositing it layer-by-layer onto a build platform. The molten polymer undergoes rapid cooling and solidification, creating bonds between adjacent rasters (roads) and between successive layers through inter-molecular diffusion of polymer chain segments across wetted interfaces [92]. This bonding process is thermally activated: the temperature of the newly deposited material must exceed the glass transition temperature (Tg) of the polymer to allow sufficient chain mobility for diffusion and neck growth [48, 51].

### Thermal Behaviour and Residual Stress

The dominant physics governing FDM part quality is thermal. During printing, each deposited road experiences:
1. **Rapid heating** from the nozzle (above melt temperature)
2. **Rapid cooling** toward ambient/bed temperature
3. **Partial reheating** when the next layer is deposited above it

This thermal cycling creates inhomogeneous temperature fields that produce residual stresses [55, 57, 58]. The temperature gradient between the newly deposited layer and previously cooled layers drives differential shrinkage, causing warping and potential delamination [55, 56]. Non-uniform cooling rates from higher layer heights result in increased temperature gradients, more residual stress, and greater warpage [58]. Semi-crystalline polymers (PLA, PEEK) exhibit additional complexity because crystallisation kinetics depend on cooling rate, affecting both mechanical properties and dimensional stability [45, 48, 56].

### Anisotropy

FDM parts are inherently anisotropic because material is deposited in-plane (XY) but layer bonding in Z depends solely on interlayer adhesion [49, 51, 53]. The raster angle determines in-plane anisotropy: 0-degree rasters (aligned with load direction) produce the highest tensile and flexural strength, while 90-degree rasters rely on weak inter-raster bonds, yielding roughly half the strength [49, 52, 54]. The +/-45-degree alternating pattern provides intermediate properties with both failure mechanisms active. Z-direction strength is always the weakest axis regardless of in-plane raster strategy, as no filament is deposited vertically [51, 53].

### Material-Specific Physics

Different materials have fundamentally different thermal windows:
- **PLA**: Low Tg (~60C), nozzle 190-220C, bed 50-60C, crystallises slowly, benefits from maximum cooling
- **ABS**: Higher Tg (~105C), nozzle 230-250C, bed 90-110C, requires minimal cooling to avoid warping
- **PETG**: Intermediate Tg (~80C), nozzle 220-250C, bed 70-80C, moderate cooling needed

ABS has superior impact and heat resistance but is harder to print; PLA is the most accessible; PETG offers the best balance of printability and mechanical performance [material comparison sources].

### Key Takeaways for HDR
- The parameter space is governed by coupled thermal-mechanical physics
- Material choice constrains feasible parameter ranges
- Anisotropy means mechanical properties are direction-dependent
- Residual stress and crystallisation add nonlinearity to parameter-property relationships

---

## Theme 2: Parameter Effects on Print Quality

### Primary Parameters and Their Effects

**Layer Height (0.05-0.4 mm)**
The single most influential parameter. Lower layer heights produce:
- Better surface finish (Ra decreases roughly linearly) [34, 46, 83, 84, 85]
- Stronger interlayer bonds (more contact area per unit height, better thermal fusion) [46, 49]
- Better dimensional accuracy [36, 79, 117]
- But significantly longer print times (roughly inversely proportional)

ANOVA studies consistently find layer height contributes the highest variance to both surface roughness and build time [34, 36, 47]. Taguchi-optimised parameters with low layer height reduced circularity error by 42% and Ra by 67% compared to defaults [36].

**Nozzle Temperature**
Must be within a material-specific window. Too low causes incomplete melting and intermittent extrusion; too high causes the molten filament to lose shape and increases dimensional error [45, 113]. SHAP analysis identifies printing temperature as the most influential parameter for tensile strength: higher temperatures improve layer bonding [73]. However, excessive temperature degrades surface quality and can cause thermal degradation in polymers like PLA [48].

**Print Speed (20-300+ mm/s)**
Higher speeds generally reduce tensile strength and surface quality due to:
- Less time for interlayer diffusion bonding
- Higher shear rates in the nozzle
- Less uniform cooling [111, 112]

However, modern high-speed PLA filaments maintain quality at 300+ mm/s with appropriate thermal management [111]. The optimal speed represents a complex tradeoff between throughput and quality.

**Bed Temperature**
Critical for first-layer adhesion and warping prevention. Must be within material-specific range (PLA: 50-60C, ABS: 90-110C, PETG: 70-80C). Uneven bed heating causes warping, especially on large flat parts.

**Infill Density (0-100%) and Pattern**
Infill density directly controls strength-to-weight ratio and material usage:
- 40-60% provides good strength for functional parts
- Gyroid infill offers the best isotropic strength-to-weight ratio [44]
- Honeycomb provides excellent compression resistance but uses ~25% more material
- Rectilinear is fastest to print with steady, predictable strength

**Retraction Settings**
Control stringing/oozing during travel moves. Key parameters are retraction distance (0.5-2mm direct drive, 4-7mm Bowden) and retraction speed. Interact with temperature and travel speed in complex ways.

**Cooling Fan Speed (0-100%)**
Material-dependent: PLA benefits from 100% fan speed for bridges/overhangs; ABS requires 0-20% to avoid warping; PETG needs 30-50% to balance overhang quality with layer adhesion.

**Flow Rate / Extrusion Multiplier (0.9-1.1)**
Fine-tunes volumetric extrusion. Under-extrusion creates gaps; over-extrusion causes scarring and dimensional error. Calibrated per-material using single-wall test cubes.

### Parameter Interactions

Parameters are not independent. Key interactions include:
- **Temperature x Speed**: Higher speeds require higher temperatures to maintain extrusion quality
- **Layer height x Speed**: Combined effect on cooling rate and interlayer bonding
- **Temperature x Cooling**: Competing effects on crystallisation and warping
- **Infill % x Pattern**: Pattern efficiency varies with density

RSM studies with central composite designs capture these second-order interactions as polynomial response surfaces [67, 68, 69]. SHAP interaction plots quantify mutual influence between parameters [72, 73, 74].

### Adhesion Aids

Brims (5-8mm), rafts, and skirts address first-layer adhesion. Brims are most common for warping-prone materials (ABS, Nylon). Raft parameters (layer thickness, air gap, margin, speed) constitute additional design variables.

---

## Theme 3: Machine Learning for Print Quality Prediction

### Supervised Learning Approaches

The dominant paradigm is supervised learning from tabular data: input features are print parameters, outputs are quality metrics.

**Neural Networks (ANN/MLP)**
The most widely applied method. ANNs predict tensile strength with MAPE of 2.54%, exceeding prior literature range of 2.56-3.34% [15]. Deep learning ANNs combined with definitive screening design achieve high accuracy for dimensional accuracy prediction [79]. LSTM networks predict stress-strain curves from parameter configurations [1].

**Tree-Based Ensembles (Random Forest, XGBoost, Gradient Boosting)**
Random Forest and J48 achieve the best Ra prediction for FDM [84]. XGBoost with recursive feature elimination and SHAP explainability achieves strong prediction of mechanical properties from 12 input features [16]. Tree ensembles handle nonlinear interactions naturally and provide built-in feature importance.

**Support Vector Regression (SVR)**
SVR with RBF kernel predicts UTS of PEEK parts with <5% deviation from experimental values [12]. SVR boosted with bagging/boosting slightly improves accuracy over standalone SVR.

**Gaussian Process Regression (GPR)**
Provides both predictions and uncertainty estimates, making it ideal for active learning and Bayesian optimisation frameworks. GPR used extensively as surrogate model in BO workflows [38, 39, 41, 42].

### Model Comparison Results

A six-model comparison study (NN, DT, SVR, RF, GPR, kNN) for dynamic tensile prediction found no single model universally superior [10]. Multiple studies report:
- 98% accuracy for surface roughness prediction [11]
- 96% accuracy for tensile strength prediction [11]
- 95% accuracy for elongation prediction [11]
- R-squared of 0.999 for dimensional change prediction with NN [80]

### Explainable AI (XAI) in Print Quality Prediction

SHAP analysis has become standard for interpreting ML predictions in AM [72, 73, 74, 107]:
- Printing temperature identified as most influential for tensile strength [73]
- Infill density most significant for UTS (SHAP +2.75) and flexural strength (SHAP +5.8) [74]
- LIME and partial dependence plots complement SHAP for local and global interpretability [74]

### Data Requirements and Challenges

Typical datasets are small (50-200 samples) because each data point requires physical printing and testing. This creates challenges for data-hungry deep learning methods and motivates:
- Design of experiments (DOE) for efficient data collection [7, 34, 36, 68]
- Transfer learning across materials/printers (limited research) 
- Physics-informed approaches to reduce data requirements [95, 96, 97, 98, 99]
- Active learning to select the most informative experiments [39, 116]

### Available Datasets

- ORNL Additive Manufacturing Dataset: publicly available, mechanical test data [17]
- Kaggle 3D Printer Dataset: 9 parameters, 3 quality metrics, Ultimaker S5 [102]
- Kaggle Full Extruded Dataset: extrusion-focused process data [103]
- APMonitor AM Dataset: 116 samples combining PLA and ABS [104]
- FDM-Bench: G-code dataset with systematic anomalies for LLM evaluation [18]

These datasets are relatively small by ML standards, reinforcing the need for sample-efficient methods.

---

## Theme 4: Multi-Objective Optimisation

### Problem Formulation

FDM parameter optimisation is inherently multi-objective. Typical competing objectives include:
- Maximise tensile strength vs. minimise print time
- Maximise surface quality vs. minimise material usage
- Maximise dimensional accuracy vs. maximise throughput
- Minimise warping vs. minimise support material

No single parameter set can simultaneously optimise all objectives, so the goal is to find the **Pareto front**: the set of solutions where no objective can be improved without worsening another.

### Evolutionary and Metaheuristic Algorithms

**NSGA-II** (Non-dominated Sorting Genetic Algorithm II) is the most widely used method [7, 24, 70, 71]. It provides a well-distributed Pareto front and is the de facto standard for FDM multi-objective optimisation. Recent work integrates NSGA-II with ML surrogates:
- ANN-NSGA-II hybrid optimises surface finish and VOC emissions simultaneously [70]
- RSM-NSGA-II combines response surface modeling with evolutionary search [7]
- Hypervolume indicators assess Pareto front quality, with optimal solutions from ~500 evaluations [7]

Six metaheuristic algorithms were compared for FDM optimisation: MOGWO, MOALO, MOMVO, MODA, PESA-II, SPEA-II [22], demonstrating the breadth of available optimisers.

### Bayesian Optimisation (BO)

BO is gaining traction because it is **sample-efficient**, requiring fewer physical experiments than evolutionary methods [38, 39, 40, 41, 42, 43]:
- GP-based BO for surface roughness minimisation [40]
- Deep Gaussian Process BO handles non-stationarity in AM parameter landscapes [41]
- AMBayes framework integrates physics with GP surrogate for rapid posterior updates [42]
- Autonomous BO for hydrogel printing achieves optimal parameters with minimal experiments [43]

BO is particularly suitable for HDR because it naturally balances exploration and exploitation.

### Response Surface Methodology (RSM)

RSM with Central Composite Design (CCD) or Box-Behnken design remains widely used as a classical DOE approach [67, 68, 69]:
- Creates second-order polynomial surrogate models
- Captures main effects and two-factor interactions
- Often combined with evolutionary algorithms (RSM+GA, RSM+PSO) [67, 69]
- Q-optimal designs reduce experimental requirements [68]

### Physics-Guided Multi-Task Approaches

Emerging work combines physics with multi-task learning for multi-objective optimisation [26]:
- Physics-Guided Multi-Task Attention Ensemble simultaneously predicts tri-domain properties
- Bayesian optimisation discovers Pareto-optimal configurations for nanocomposite polymers
- Physics constraints reduce the search space and improve sample efficiency

---

## Theme 5: Defect Prediction and Prevention

### Common FDM Defects

1. **Stringing/Oozing**: Thin threads between separate features caused by molten filament leaking during travel moves
2. **Warping**: Upward curling of corners/edges due to thermal stress and differential cooling
3. **Delamination**: Layer separation caused by insufficient interlayer bonding (temperature below Tg)
4. **Under-extrusion**: Gaps between roads due to insufficient material flow
5. **Over-extrusion**: Excess material causing surface bumps and dimensional error
6. **Spaghetti**: Complete print failure where filament stops adhering to previous layers
7. **Layer shifting**: Misalignment between layers due to mechanical issues
8. **Bridging failure**: Sagging of unsupported horizontal spans

### Image-Based Defect Detection

Deep learning for visual defect detection has achieved remarkable accuracy:
- Improved YOLOv8: 97.5% mAP50 for real-time FDM defect detection [27]
- Enhanced YOLOv8: 91.7% mAP50 at 71.9 FPS [28]
- CNN classification of 5 common defects: 98.6% accuracy on 1,912 images [29]
- Modified VGGNet: 97% accuracy for ME failure detection from webcam images [86]
- CNN stringing detection: 99.31% accuracy [30]
- Multi-head neural network: trained on 1.2M images from 192 parts [19]

YOLOv4/v8 variants dominate real-time detection due to speed-accuracy tradeoff. AlexNet-SVM has been deployed on Raspberry Pi for edge inference [87].

### Predictive Defect Models (Pre-Process)

Rather than detecting defects during printing, predictive models estimate defect risk from parameters before printing:
- Warping prediction via thermal-structural FEA [55, 56, 58, 59]
- Shrinkage prediction and compensation using neural networks [78, 79, 80, 81]
- Shape deviation prediction using graph neural networks (GraphCompNet) [82]
- Dimensional accuracy prediction with deep learning ANN achieving R-squared 0.999 [80]

### Variational Autoencoder for Anomaly Detection

VAE-based approaches enable unsupervised defect detection by learning the distribution of normal prints and flagging deviations [114]. This is valuable when labelled defect data is scarce.

### Prevention via Parameter Optimisation

The most impactful approach is **preventing defects through optimal parameter selection**:
- Warping: adequate bed temperature, low layer height, heated enclosure for ABS
- Stringing: optimised retraction distance/speed, lower nozzle temperature
- Delamination: ensure interlayer temperature above Tg, appropriate cooling
- Under/over-extrusion: calibrated flow rate and extrusion multiplier

---

## Theme 6: Process Monitoring and Closed-Loop Control

### Sensor Modalities

Multiple sensor types enable real-time FDM monitoring [31, 89, 90, 91]:

**Visual (Cameras)**
- High-resolution cameras capture each layer for computer vision analysis
- Webcam-based systems achieve 97%+ accuracy at low cost [86]
- Multi-view fusion provides more complete spatial information [32]
- Open-source layer-wise analysis tools available [118]

**Acoustic Emission (AE)**
- AE sensors detect filament breakage and nozzle clogging [89]
- A single AE sensor can identify part quality issues, material defects, phase transformations, and clogging [89]
- Non-invasive and inexpensive

**Vibration**
- Vibration sensors near the nozzle detect clogging via nonlinear amplitude increase [90, 91]
- Physics-based dynamic models relate vibration signatures to nozzle condition

**Current Monitoring**
- Extruder motor current changes when nozzle clogs reduce effective diameter [90]
- Low-cost and easily integrated into existing hardware

**Thermal (IR)**
- Infrared thermometers/cameras monitor temperature fields
- Critical for validating thermal models and detecting anomalies

### Digital Twins

Digital twins integrate simulation, sensor data, and AI for comprehensive process management [60, 61, 62, 63, 64, 65]:
- Real-time digital counterpart captures data from embedded sensors
- AI/ML models predict outcomes and detect anomalies
- Enable "what-if" simulation before production
- HP/NVIDIA have open-sourced physics-informed ML surrogates for AM digital twins [66]
- Time-series DNNs with model predictive control enable real-time decision-making [62]

### Closed-Loop Control

The frontier of AM monitoring is closing the loop between sensing and actuation:
- RL-based closed-loop control achieves 35-55% quality improvements and 18-28% efficiency gains [76]
- Uncertainty-aware RL integrates vision-based uncertainty quantification with control [75]
- Tilted elliptical reward functions capture coupling between flow rate and temperature [76]
- Model reference adaptive control for direct ink writing achieves real-time regulation [76]

### Practical Monitoring Systems

Commercial systems (Obico, 3DPrinterOS) use CNN-based spaghetti detection to auto-pause failed prints. These demonstrate industrial viability of ML monitoring, though most focus on catastrophic failure detection rather than continuous quality optimisation.

---

## Theme 7: Open Challenges and Research Gaps

### Data Scarcity and Generalisability

The most persistent challenge is **small dataset size**. Physical printing experiments are time-consuming and expensive, typically yielding 50-200 samples per study. This limits:
- Deep learning applicability (though transfer learning shows promise)
- Model generalisability across printers, materials, and geometries
- Statistical power for detecting subtle parameter interactions

**Transfer learning across printers and materials** is severely under-explored. A domain adaptation architecture achieved 27.3% reduction in false negative rates and 94.8% precision across 5 material combinations, demonstrating feasibility but highlighting the gap.

### Missing Standard Benchmarks

There is no universally accepted benchmark dataset for FDM parameter optimisation analogous to UCI/ImageNet for general ML. Existing datasets are small, printer-specific, and use inconsistent measurement protocols. FDM-Bench [18] addresses LLM evaluation but not tabular ML. The ORNL dataset [17] is the closest to a community standard but focuses on metal AM.

### Parameter-Geometry Interaction

Most studies optimise parameters for **simple test specimens** (tensile bars, cubes). Real parts have varying geometry: thin walls, overhangs, bridges, infill transitions. Geometry-aware optimisation using GNNs and point clouds [82] is nascent but critical for practical applications.

### Multi-Material Optimisation

Multi-material FDM introduces additional variables (material sequence, interface parameters, overlap distance) with poorly understood interactions. Interface bonding can vary by 389% based on print orientation alone [93]. This is largely unexplored with ML methods.

### Real-Time Adaptive Control

While RL-based control shows promise [75, 76, 77], integrating real-time parameter adjustment with existing printer firmware is a practical barrier. Most work assumes simplified action spaces. The gap between research demonstrations and industrial deployment remains large.

### Physics-ML Integration

Physics-informed neural networks show promise for thermal modeling [95-99] but are underutilised for FDM specifically. Most PINN work targets metal AM (laser powder bed fusion). Adapting PINNs to the polymer extrusion context -- with its crystallisation kinetics, viscoelastic flow, and complex cooling -- is an open opportunity.

### Slicer Integration

Current ML models operate independently of slicing software. Embedding predictive models directly into slicers (Cura, PrusaSlicer, OrcaSlicer) to provide real-time parameter recommendations is a practical gap. LLM-based approaches [100, 101] are exploring this direction but lack the precision of purpose-built ML models.

### Sustainability and Multi-Objective Scope

Most studies optimise for mechanical properties alone. Broader objectives -- energy consumption, VOC emissions [70], filament waste, recyclability -- are underrepresented. The environmental impact of parameter choices is an emerging concern.

### AutoML and Model Selection

Automated model selection and hyperparameter tuning (AutoML) has not been systematically applied to FDM optimisation. Most studies manually select and tune models, potentially missing better alternatives.

### Inverse Design

The ultimate goal -- "given desired properties, find optimal parameters" -- is framed as forward prediction in most work. True inverse design using generative models (GANs, VAEs, diffusion models) or invertible neural networks is largely unexplored for FDM parameter selection, though established in molecular/materials design.

---

## Summary of Key Quantitative Results

| Method | Target | Best Accuracy | Reference |
|--------|--------|---------------|-----------|
| ANN | Tensile strength | MAPE 2.54% | [15] |
| SVR/RF | Surface roughness | R^2 0.98 | [11] |
| SVR | PEEK UTS | <5% deviation | [12] |
| NN | Dimensional change | R^2 0.999 | [80] |
| YOLOv8 | Defect detection | 97.5% mAP50 | [27] |
| CNN | 5-class defects | 98.6% accuracy | [29] |
| VGGNet | Failure detection | 97% accuracy | [86] |
| Taguchi | Surface roughness | 67% Ra reduction | [36] |
| RL control | Quality improvement | 35-55% gain | [76] |
| BO (5 expts) | Parameter calibration | Outperforms ML | [116] |

---

## References

Numbers in brackets [N] refer to paper IDs in `papers.csv`.
