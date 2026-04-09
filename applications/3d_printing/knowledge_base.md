# Knowledge Base: 3D Printing (FDM/FFF) Parameter Optimisation

This document consolidates the established facts, empirical relationships, benchmarks, and datasets from the literature review. It serves as the authoritative "what we already know" reference for Phase 1+ work. Bracketed numbers [N] refer to `papers.csv`.

---

## 1. Process Physics: Established Relationships

### 1.1 No Single "Abrams' Law" Equivalent

Unlike concrete, which has Abrams' law (fc = A / B^(w/c)) as a universally accepted first-order model, FDM has no single dominant empirical law. The closest analogues are:

- **Thermal bonding time** (from Sun et al. [133]): Bond strength develops as the newly deposited road remains above the glass transition temperature Tg. The bond quality scales roughly as sqrt(t_contact) where t_contact is the time the interface spends above Tg - a reptation-like scaling.
- **Volumetric energy density** (borrowed from LPBF literature): E_vol = (T_nozzle - T_amb) / (v_print * h_layer * w_line) - proposed but not universally validated.
- **Anisotropy ratio**: UTS(90 deg raster) / UTS(0 deg raster) ~ 0.45-0.65 for ABS, 0.55-0.75 for PLA [132, 137].

### 1.2 Core Parameter-Property Relationships (Consensus from Literature)

| Parameter | Primary Property Effect | Secondary Effect | Source |
|-----------|------------------------|------------------|--------|
| Layer height (decrease) | Better surface finish (lower Ra) | Longer print time, better inter-layer bond | [34, 36, 47, 85] |
| Nozzle temperature (increase) | Stronger inter-layer bond, higher UTS | Worse dimensional accuracy, more stringing | [48, 73, 133] |
| Print speed (increase) | Faster print | Lower UTS, worse surface finish | [112, 133] |
| Infill density (increase) | Higher UTS, flexural strength | Proportional material use and print time | [44, 74] |
| Infill pattern (gyroid) | Isotropic strength, best strength/weight | Longer print time | [44] |
| Raster angle 0 deg | Maximum tensile strength (load-aligned) | Anisotropic (weak at 90 deg) | [132, 137] |
| Bed temperature (increase) | Better first-layer adhesion, less warping | Risk of elephant foot | [133] |
| Cooling fan (PLA: increase) | Better overhangs, detail | Weaker inter-layer bond | [48] |
| Cooling fan (ABS: decrease) | Reduced warping, better bonding | Worse overhangs | [48] |

### 1.3 Anisotropy (the "Sun Model")

Sun et al. [133] established that bond quality between adjacent roads depends on how long the interface remains above Tg. Faster printing and thinner layers give less time above Tg, weakening bonds. The resulting anisotropy:

- 0-degree raster UTS / 90-degree raster UTS ~ 1.5 to 2.2 for ABS
- Z-direction is always the weakest axis (~45-60% of XY strength)

---

## 2. Standard Test Specimens

### 2.1 Tensile Testing

- **ASTM D638-14 Type I**: 165 mm x 19 mm x 3.2 mm (gauge 50 mm x 13 mm) - most common for FDM tensile tests [128].
- **ASTM D638-14 Type IV**: smaller geometry for limited material or small printers.
- **ISO 527-2 Type 1A**: International equivalent, 170 mm x 20 mm x 4 mm [131].

Load rate: typically 5 mm/min for thermoplastics.

### 2.2 Flexural Testing

- **ASTM D790-17**: 3-point bending, span-to-thickness ratio 16:1, typical bar 127 mm x 12.7 mm x 3.2 mm [129].
- Support radius 5 mm, loading nose radius 5 mm, rate 2 mm/min.

### 2.3 Impact Testing

- **ASTM D256-10 (Izod)**: Notched bar 63.5 mm x 12.7 mm x 3.2 mm with V-notch [130].
- **ASTM D6110 (Charpy)**: Alternative configuration.

### 2.4 Surface Roughness (Ra)

- Stylus profilometer (contact) or confocal microscopy (non-contact).
- Typical evaluation length: 4 mm across the layer direction (captures layer lines).
- Reported as Ra (arithmetic mean) in micrometres.

### 2.5 Dimensional Accuracy

- Measured with calipers or CMM on standard cubes (20 mm or 50 mm edge) or NIST test artifact.
- Reported as absolute deviation (mm) or percentage error on X, Y, Z dimensions.

---

## 3. Typical Strength Values by Material (FDM Printed)

| Material | UTS (MPa) | Elongation (%) | Flexural (MPa) | Izod (J/m) | Density (g/cc) |
|----------|-----------|----------------|----------------|------------|----------------|
| PLA | 35-65 | 2-6 | 55-100 | 20-60 | 1.24 |
| PLA+ (toughened) | 40-55 | 8-15 | 60-90 | 60-130 | 1.24 |
| ABS | 25-45 | 3-8 | 40-75 | 200-400 | 1.04 |
| PETG | 30-55 | 4-12 | 50-85 | 60-150 | 1.27 |
| TPU 95A | 25-40 | 300-550 | 25-40 | n/a (flexible) | 1.21 |
| Nylon (PA12) | 40-65 | 20-50 | 45-80 | 100-250 | 1.03 |
| CF-PLA | 45-70 | 2-4 | 75-120 | 30-80 | 1.30 |
| CF-Nylon | 55-85 | 3-8 | 80-140 | 80-200 | 1.15 |
| PEEK | 80-110 | 4-10 | 130-180 | 60-180 | 1.32 |
| GF-PEEK | 100-140 | 2-5 | 150-220 | 80-200 | 1.48 |

All values are for 100% infill, 0-degree raster, optimised parameters. Real functional prints at 20-40% infill produce roughly 30-60% of these values. Compiled from [44, 45, 46, 132, 133, 145] and standard manufacturer datasheets.

---

## 4. Typical Parameter Windows

### 4.1 PLA (most common)

| Parameter | Min | Max | Default |
|-----------|-----|-----|---------|
| T_nozzle (C) | 190 | 220 | 210 |
| T_bed (C) | 0 | 60 | 60 |
| Print speed (mm/s) | 30 | 300 | 50 |
| Layer height (mm) | 0.08 | 0.32 | 0.20 |
| Infill density (%) | 0 | 100 | 20 |
| Cooling fan (%) | 80 | 100 | 100 |
| Retraction distance (mm, direct) | 0.5 | 2.0 | 1.0 |

### 4.2 ABS

| Parameter | Min | Max | Default |
|-----------|-----|-----|---------|
| T_nozzle (C) | 230 | 260 | 240 |
| T_bed (C) | 90 | 110 | 100 |
| Print speed (mm/s) | 30 | 80 | 50 |
| Layer height (mm) | 0.10 | 0.30 | 0.20 |
| Cooling fan (%) | 0 | 20 | 0 |
| Enclosure temp (C) | 30 | 60 | ambient |

### 4.3 PETG

| Parameter | Min | Max | Default |
|-----------|-----|-----|---------|
| T_nozzle (C) | 220 | 250 | 235 |
| T_bed (C) | 70 | 80 | 75 |
| Print speed (mm/s) | 30 | 80 | 50 |
| Layer height (mm) | 0.10 | 0.30 | 0.20 |
| Cooling fan (%) | 30 | 60 | 50 |
| Retraction distance (mm) | 1.0 | 3.0 | 2.0 |

---

## 5. ML Accuracy Benchmarks (from Literature)

### 5.1 Tensile Strength Prediction

| Model | Dataset | Metric | Value | Reference |
|-------|---------|--------|-------|-----------|
| ANN (pre-process) | FDM materials | MAPE | 2.54% | [15] |
| SVR | PEEK | Deviation | < 5% | [12] |
| XGBoost + SHAP | Nylon composites | R2 | > 0.95 | [16] |
| LSTM | MEX | Stress-strain curve match | high | [1] |
| SVR / RF | PLA | Accuracy | 96% | [11] |
| 6-model comparison (NN/DT/SVR/RF/GPR/kNN) | FDM dynamic | no single winner | - | [10] |

### 5.2 Surface Roughness Prediction

| Model | Accuracy / R2 | Reference |
|-------|---------------|-----------|
| Random Forest | 98% | [11] |
| J48 decision tree | best on Ra | [84] |
| ANN + Taguchi | 67% Ra reduction | [36] |

### 5.3 Dimensional Accuracy

| Model | R2 | Reference |
|-------|------|-----------|
| Deep ANN + Definitive Screening Design | 0.999 | [80] |
| Taguchi optimisation | 42% circularity error reduction | [36] |

### 5.4 Defect Detection (image-based)

| Model | Task | Accuracy | Reference |
|-------|------|----------|-----------|
| Improved YOLOv8 | FDM defects | 97.5% mAP50 | [27] |
| Enhanced YOLOv8 | AM defects | 91.7% mAP50 at 71.9 FPS | [28] |
| CNN | 5-class FDM defects | 98.6% | [29] |
| CNN | Stringing detection | 99.31% | [30] |
| VGGNet | Failure detection | 97% | [86] |
| Multi-head NN | Generalised defect | trained on 1.2M images | [19] |

### 5.5 Closed-Loop Control

- RL-based control: 35-55% quality improvement, 18-28% efficiency gains [76].
- BO outperforms standard ML with as few as 5 experiments [116].

---

## 6. Public Datasets

### 6.1 Kaggle 3D Printer Dataset [102]

- **Source**: Kaggle (afumetto/3dprinter)
- **Size**: 50 samples
- **Parameters (9)**: layer_height, wall_thickness, infill_density, infill_pattern, nozzle_temperature, bed_temperature, print_speed, material, fan_speed
- **Targets (3)**: roughness, tension_strength, elongation
- **Machine**: Ultimaker S5
- **Materials**: PLA, ABS
- **Licence**: Open (Kaggle)
- **Notes**: The most cited benchmark in the ML-for-FDM literature. Small but clean.

### 6.2 APMonitor Additive Manufacturing Dataset [104]

- **Source**: apmonitor.com/pds
- **Size**: 116 samples (PLA + ABS combined)
- **Targets**: Tensile strength
- **Notes**: Frequently used in pedagogical ML examples. Larger than Kaggle but still small.

### 6.3 ORNL Additive Manufacturing Dataset [17]

- **Source**: Oak Ridge National Laboratory
- **Size**: Thousands of mechanical tests
- **Notes**: Focused on metal AM but includes polymer data. Reported 61% reduction in UTS prediction error using this data. Quality of annotations is high.

### 6.4 Kaggle Full Extruded Dataset [103]

- **Source**: Kaggle (marcelobatalhah/full-extruded-dataset)
- **Focus**: Extrusion-process data
- **Notes**: More process-oriented than quality-oriented.

### 6.5 FDM-Bench [18]

- **Source**: arXiv 2412.09819
- **Focus**: G-code level dataset with systematic anomalies, designed for LLM evaluation
- **Notes**: Useful for defect-classification tasks, less so for parameter optimisation.

### 6.6 Nature Communications 1.2M Image Dataset [19]

- **Size**: 1.2 million images from 192 parts
- **Focus**: Defect detection, not parameter optimisation
- **Notes**: Gold standard for image-based defect ML.

### 6.7 GitHub Open-Source Framework (Concrete Printing) [20]

- **Notes**: Not FDM but concrete 3D printing. Referenced for infrastructure patterns.

---

## 7. Defect Taxonomy and Prevention

| Defect | Cause | Primary Parameter Fix |
|--------|-------|------------------------|
| Warping | Thermal gradient, differential shrinkage | Higher bed temp; enclosure; lower print speed; brim |
| Stringing | Oozing during travel | Increase retraction distance/speed; lower nozzle temp |
| Delamination | Insufficient inter-layer bonding | Higher nozzle temp; reduce cooling; slower speed |
| Under-extrusion | Insufficient material flow | Calibrate flow rate; higher temp; check filament diameter |
| Over-extrusion | Excess material | Reduce flow rate; check calibration |
| Elephant foot | First layer squished | Reduce bed temp; increase first-layer Z offset |
| Spaghetti | Loss of adhesion mid-print | Improve first-layer adhesion; reduce speed on small features |
| Layer shifting | Mechanical missteps | Reduce acceleration; check belts |
| Bridging failure | Unsupported spans sagging | Higher fan; slower bridging speed; add supports |
| Ringing/ghosting | Vibration artifacts | Lower acceleration; input shaper |

---

## 8. Multi-Objective Optimisation Standard Practices

### 8.1 Common Objective Combinations

1. **Strength vs time**: classical tradeoff; UTS in MPa vs hours/part.
2. **Strength vs material**: UTS vs grams/part; proxy for cost and sustainability.
3. **Surface quality vs time**: Ra (um) vs print time.
4. **Dimensional accuracy vs throughput**: |delta| (mm) vs parts per hour.
5. **Strength vs VOC emissions**: reported in [70].

### 8.2 Standard Algorithms

| Algorithm | Typical Use | Sample Efficiency | Reference |
|-----------|-------------|-------------------|-----------|
| NSGA-II | Default multi-objective workhorse | Low (needs 1000s of evaluations) | [7, 22, 24] |
| Bayesian Optimisation (EHVI) | Expensive evaluations | High (< 100 evaluations) | [38-43] |
| RSM-CCD / Box-Behnken | Classical DOE with quadratic model | Very high (~20-50 runs) | [67, 68, 69] |
| Taguchi (orthogonal arrays) | Screening, limited interactions | Very high (~9-27 runs) | [34, 36, 37] |
| MOGWO / MOALO / MOMVO / PESA-II / SPEA-II | Metaheuristic alternatives | Low | [22] |

### 8.3 Pareto Front Quality Metrics

- **Hypervolume indicator**: volume of objective space dominated by the front relative to a reference point.
- **Spacing**: uniformity of solutions along the front.
- **Spread**: distribution range.
- **Epsilon indicator**: distance to a reference front.

---

## 9. Feature Engineering Conventions

Based on the literature review, the following derived features are proposed and likely informative:

| Feature | Formula | Rationale |
|---------|---------|-----------|
| Linear energy density | T_nozzle * v_print / h_layer | Borrowed from LPBF literature; couples thermal and kinematic |
| Volumetric flow rate | v_print * w_line * h_layer | Direct mass-flow indicator; hits hardware limits |
| Cooling rate proxy | (T_nozzle - T_amb) * F_cool / h_layer | Proxy for inter-layer cooling gradient |
| Inter-layer dwell time | layer_area / (v_print * w_line) | Time interface spends above Tg (Sun model) |
| Infill contact area | rho_infill * pattern_factor * layer_area | Load-bearing cross section |
| Total heating energy | T_nozzle * print_time | Aggregate thermal input |
| Aspect ratio | h_layer / w_line | Road cross-section shape; affects bonding |
| Material thermal margin | T_nozzle - Tg(material) | How far above Tg the polymer flows |

These derived features will be tested in Phase A (H1, H2).

---

## 10. Open Challenges (Summary from Theme 7)

1. **Small datasets** (50-200 samples typical) limit deep learning applicability.
2. **No universal benchmark** analogous to UCI Concrete for FDM.
3. **Geometry dependence** mostly ignored; studies use simple specimens.
4. **Multi-material** optimisation largely unexplored.
5. **Real-time adaptive control** is research-stage only.
6. **Physics-ML integration** (PINNs) is underutilised for polymer extrusion specifically.
7. **Slicer integration** of ML recommendations remains a practical gap.
8. **Sustainability objectives** (energy, VOC, waste) rarely considered.
9. **True inverse design** via generative models largely unexplored.
10. **Transfer learning** across printers/materials is severely under-studied.

---

## 11. Key Textbook References

- **Gibson, Rosen, Stucker, Khademhosseini (2021)** - "Additive Manufacturing Technologies" 3rd ed. The definitive AM textbook [121].
- **Chua, Leong, Lim (2010, 2017)** - Rapid prototyping textbooks covering FDM physics [122, 124].
- **Gebhardt (2011)** - "Understanding Additive Manufacturing" [123].
- **Baird, Collias (2014)** - "Polymer Processing: Principles and Design" - for underlying extrusion physics [125].

## 12. Key Standards

- **ISO/ASTM 52900:2021** - AM terminology (material extrusion = ME = FDM = FFF) [127].
- **ASTM F2792-12a** - Original AM standard terminology [126].
- **ASTM D638-14 / ISO 527-2** - Tensile testing of plastics [128, 131].
- **ASTM D790-17** - Flexural testing [129].
- **ASTM D256-10** - Izod impact [130].

---

## 13. Glossary

- **FDM** (Fused Deposition Modeling) - Trademarked term by Stratasys for material extrusion.
- **FFF** (Fused Filament Fabrication) - Generic term; functionally equivalent to FDM.
- **ME** (Material Extrusion) - ISO/ASTM 52900 category name.
- **MEX** - Alternative acronym for material extrusion.
- **Raster** - Single line of deposited material within a layer.
- **Infill** - Interior pattern of a 3D printed part (non-solid).
- **Perimeter / Wall** - Outer shell lines of a layer.
- **Retraction** - Filament pullback during travel moves to prevent oozing.
- **Ra** - Arithmetic mean surface roughness (um).
- **UTS** - Ultimate Tensile Strength (MPa).
- **Tg** - Glass transition temperature (C).
- **LPBF** - Laser Powder Bed Fusion (metal AM, referenced for parallels).
- **PLA / ABS / PETG / TPU** - Common thermoplastic feedstocks.
- **Gyroid** - Triply periodic minimal surface infill pattern with isotropic mechanical properties.

---

## 14. Phase 2 HDR findings (added 2026-04-09)

The following facts were added to the knowledge base by the HDR loop run
in this session. The source for every number is `results.tsv` in this
directory.

### 14.1 Model family ranking on the Kaggle 3D Printer Dataset (N = 50)

| Rank | Family | 5-fold MAE (MPa) | Relative to XGBoost |
|---|---|---|---|
| 1 | XGBoost (depth 6, lr 0.05, n=300) | 4.44 | 1.00x |
| 2 | ExtraTrees (300 est.) | 4.97 | 1.12x worse |
| 3 | RandomForest (300 est.) | 5.08 | 1.14x worse |
| 4 | LightGBM (defaults) | 5.22 | 1.18x worse |
| 5 | Ridge regression | 5.86 | 1.32x worse |

**Key observation**: The tree-vs-linear gap is only 1.3x on this dataset.
This is below program.md's 2x threshold for declaring the problem
"strongly non-linear", which means the tensile-strength signal is
roughly two-thirds linear and only one-third structured non-linear
interactions. The implication for downstream work: neural networks
are unlikely to help; linear models with hand-engineered interactions
would be a defensible simpler baseline.

### 14.2 The physics-informed feature set that wins

**E08 winning feature set** (five derived features):

- `E_lin = T_nozzle * v_print / h_layer` -- linear energy density
- `vol_flow = v_print * h_layer * w_line` -- volumetric flow rate
- `interlayer_time = 2500 / (v_print * w_line)` -- proxy for time above Tg
- `infill_contact = (infill_density / 100) * 2500` -- load-bearing area proxy
- `thermal_margin = T_nozzle - Tg(material)` -- temperature above glass transition

**Rejected because hurt MAE**: `cool_rate = (T_nozzle - T_amb) * fan_speed / h_layer`

The cooling-rate proxy was part of the pre-registered "full six-feature
set" from hypothesis H2 but consistently made things worse. The most
likely reason: the fan-speed coefficient in the formula gives the
feature a bimodal distribution (ABS samples in the dataset have
fan_speed 0 - 25, PLA samples have fan_speed 50 - 100), which XGBoost
interprets as an implicit material indicator rather than a genuine
thermal signal.

### 14.3 Monotone constraints do not transfer from concrete to FDM

Seven monotone-constraint experiments (E34 - E40) were run at priors
0.45 - 0.60, all based on directional relationships that are well
established in the FDM literature (infill+, print_speed-,
nozzle_temperature+, layer_height-). All seven reverted. Phase 2.5
re-tested the two most promising monotone compositions (P25.1 and
P25.5) on top of the winning physics features. Both reverted.

**Hypothesised reason**: N = 50 is too small for the constraint to
help. Each monotone constraint eliminates tree splits that would
otherwise fit the training fold, and the cross-validation fold's
variance is too high for the regularisation benefit to show up.
Concrete's N = 1030 is twenty times larger, and the monotone
constraint on cement improved MAE there (E17: -0.034 MPa).

### 14.4 Log-target transform does not help

E33 (`log(tension_strength)` as the training target) reverted with
delta = +0.43 MPa. The target is only mildly right-skewed (skewness
0.07) and the dataset is too small to benefit from variance-stabilising
transforms.

### 14.5 Most hyperparameter sweeps are noise

Eleven hyperparameter sweeps in Phase 2 (E22 - E32), all at priors
0.25 - 0.30, all reverted. The deltas ranged from +0.11 to +0.47,
all consistent with per-fold sampling noise. **On N = 50, the
default XGBoost hyperparameters are already at or beyond the point
of diminishing returns** -- spending optimisation budget on depth,
learning rate, or row subsampling returns nothing.

### 14.6 Phase B discovery result (in-distribution)

The trained E08 model, when swept over 2,394 candidate print
settings, identifies a configuration that simultaneously beats the
Cura PLA slicer default on tensile strength, print time, and
energy consumption:

| Metric | Cura default | Discovery | Improvement |
|---|---|---|---|
| Predicted tensile strength | ~17 - 19 MPa | 30.1 MPa | +59 percent |
| Print time | 0.52 h | 0.24 h | -54 percent |
| Energy | 0.10 kWh | 0.049 kWh | -51 percent |

The discovered recipe: PLA, layer height 0.20 mm, print speed 120
mm/s, nozzle 215 C, infill 70 percent (honeycomb), 3 walls, fan
75 percent, bed 60 C.

**Novelty caveat**: The direction of each change is already in the
literature (higher infill = stronger; thicker layers plus higher
speed = faster; 70 percent infill is the classical "functional"
setpoint). The novelty is that a data-driven surrogate, trained on
50 samples, finds a single set of values that hit all three targets
simultaneously, and that the set falls inside the training
distribution so it can be printed immediately without extrapolation.
