# Knowledge Base: Welding Parameter Optimisation HDR

## Phase 0 -- Established Domain Knowledge

**Date:** 2026-04-02
**Scope:** Parameter-quality relationships, defect mechanisms, process windows, and ML benchmarks drawn from `literature_review.md`. Serves as a reference for the HDR loop to avoid re-deriving known physics.

---

## 1. Established Parameter-Quality Relationships

### 1.1 Welding Current

- **Penetration:** ~2.5x more influential than any other parameter on penetration depth (Lincoln Electric; literature review Section 2.1).
- **Deposition rate:** Roughly linear with current in GMAW/FCAW; wire-feed-rate-current coupling ties WFR to current in CV power sources.
- **Heat input:** Enters linearly in HI = (60 V I eta)/(1000 v).
- **GMAW transfer mode transitions:** Short-circuit to globular at I ~180 A (Ar/CO2); globular to spray at I ~220-250 A (Ar-rich) for 1.2 mm wire.

### 1.2 Arc Voltage

- **Bead shape:** Higher V flattens the bead (higher width-to-depth ratio). No first-order effect on penetration in CV-GMAW.
- **Arc length:** V/I ratio is a proxy for arc length at a given current.
- **Spray transition:** Spray transfer requires voltage above a current-dependent threshold (e.g., >28 V at 250 A in Ar-rich blends).

### 1.3 Travel Speed

- **Heat input:** Inversely proportional; doubling v halves HI at fixed V, I.
- **Penetration saturation:** Penetration increases with reduced v up to a point, then saturates or inverts due to weld pool lift-off.
- **Humping:** Above a critical v (process-dependent), weld pool humping defect appears.

### 1.4 Wire Feed Rate

- **CV GMAW coupling:** WFR directly couples to current; maximum penetration at lowest travel speed and highest WFR (Sarikhani & Pouranvari, 2023).
- **CC processes:** WFR decouples from current and affects reinforcement height and dilution.

### 1.5 Shielding Gas

- **CO2 fraction effect:** Increasing CO2 deepens penetration but increases spatter; ductility improves while UTS/YS drop slightly.
- **He addition:** Hotter arc, broader penetration, enables faster travel speeds; useful for thick Al/Cu.
- **Ar/CO2/O2 ternary:** Best for galvanised steels -- reduces pitting, porosity, and spatter vs binary Ar/CO2.

### 1.6 Preheat and Interpass

- **Preheat lowers cooling rate:** Shifts HAZ transformation products from martensite toward bainite/ferrite.
- **Interpass trade-off:** Lower interpass -> higher strength but lower toughness below a critical threshold; above that threshold, the relationship reverses due to grain coarsening.

---

## 2. Heat Input Formula and Microstructural Effect

### 2.1 Formula

    HI [kJ/mm] = (60 * V * I * eta) / (1000 * v)

- V = arc voltage (V)
- I = welding current (A)
- v = travel speed (mm/min)
- eta = arc/thermal efficiency

Arc efficiency values (literature review Section 1.1):
- GTAW: ~0.6
- GMAW: ~0.8
- SAW: ~0.9
- SMAW: ~0.75
- Laser welding: ~0.7-0.9 (keyhole); ~0.2-0.5 (conduction mode)
- EBW: ~0.85-0.95

### 2.2 Cooling Time t8/5

The cooling time between 800 C and 500 C is the metallurgically critical metric for steel HAZ:

- Typical range: 5-30 seconds.
- Governs transformation products (martensite at low t8/5, ferrite/pearlite at high t8/5).
- Depends on heat input, preheat, plate thickness, joint geometry, and heat-flow regime (2D for thin plate, 3D for thick plate).

### 2.3 Microstructural Outcomes for Ferritic Steels

From Easterling (1992) and literature review Section 1.2:

| Cooling regime | t8/5 range | Products | Hardness | Toughness |
|---------------|------------|----------|----------|-----------|
| Slow | >25 s | Ferrite + pearlite | Low | Good |
| Moderate | 8-25 s | Bainite | Intermediate | Good |
| Fast | 3-8 s | Bainite + martensite | High | Reduced |
| Very fast | <3 s | Martensite | Very high | Poor, crack risk |

### 2.4 HAZ Size Scaling

HAZ width scales approximately with HI^0.5 for thick plate (3D heat flow) and HI for thin plate (2D heat flow), from the Rosenthal analytical solution (Rosenthal review, literature review Section 1.5).

### 2.5 Carbon Equivalent and Cold Cracking

IIW formula:

    CE = C + Mn/6 + (Cr + Mo + V)/5 + (Ni + Cu)/15

Thresholds (Lancaster 1999):
- CE < 0.35: no preheat required.
- 0.35 <= CE < 0.45: preheat recommended for thick sections.
- CE >= 0.45: preheat mandatory; magnitude depends on thickness and hydrogen level.

---

## 3. Common Defects and Their Parameter Causes

### 3.1 Porosity

**Appearance:** Round or elongated gas cavities in weld metal.

**Causes:**
- Insufficient shielding gas flow (atmospheric contamination).
- Excessive shielding gas flow (turbulence, air entrainment).
- Contaminated filler or base metal (oil, moisture, rust, mill scale).
- Wrong shielding gas for material (e.g., Ar on self-shielded FCAW; CO2 on Al).
- Excessive arc voltage (elongated arc draws in air).
- Too-long contact tip to work distance.
- Moisture in electrode/flux.

**References:** Kou (2003); Lancaster (1999); Al GMAW porosity studies (literature review Section 4.1).

### 3.2 Lack of Fusion / Lack of Penetration

**Appearance:** Unbonded interfaces between weld metal and base metal, or incomplete root fusion.

**Causes:**
- Insufficient current/heat input.
- Excessive travel speed.
- Wrong torch angle (push angle too steep).
- Poor joint preparation (narrow groove, wide root face).
- Excessive CTWD reducing effective amperage.
- Wrong electrode manipulation (weaving too fast).

**References:** Lancaster (1999); literature review Section 4.1.

### 3.3 Undercut

**Appearance:** Grooves at weld toe where base metal has melted away and not been filled.

**Causes:**
- Excessive arc voltage.
- Excessive travel speed.
- Wrong work angle (fillet welds).
- Excessive current with high travel speed.

**References:** Undercut formation studies (literature review Section 4.1); AWS D1.1.

### 3.4 Cracking

**Hot cracking (solidification):**
- Solidification cracking of the fusion zone.
- Causes: high sulphur/phosphorus, restraint, wide solidification range, high dilution.
- Susceptible materials: free-machining steels, some Ni alloys, Al 6xxx, austenitic stainless with low Cr/Ni ratio.

**Cold cracking (hydrogen-induced):**
- Delayed cracking in HAZ hours-to-days after welding.
- Causes: hydrogen (from moisture, contamination), susceptible microstructure (martensite), tensile stress.
- Requires all three: hydrogen + microstructure + stress.
- Mitigation: preheat, low-hydrogen consumables, drying of flux/filler, post-weld hydrogen bakeout.

**Lamellar tearing:**
- Through-thickness cracking in rolled steel plates under restraint.
- Caused by MnS inclusions aligned in rolling direction.

**References:** Lippold (2015); Easterling (1992); IIW cold-cracking literature.

### 3.5 Distortion

**Appearance:** Out-of-plane or in-plane geometric deviation after cooling.

**Causes:**
- Excessive heat input.
- Asymmetric welding sequence.
- Lack of fixturing/restraint (but restraint increases cracking risk).
- Single-pass welds with high heat input vs multi-pass balanced.

**References:** Easterling (1992); FEA distortion studies (literature review Section 4.4).

### 3.6 Spatter

**Appearance:** Molten metal droplets expelled from the arc.

**Causes:**
- Wrong voltage-current combination (outside optimal transfer mode).
- High CO2 fraction in shielding gas.
- Long arc length.
- Contaminated base metal.
- Incorrect inductance setting on power source.

**References:** Literature review Section 2.2; AWS WJ gas studies.

---

## 4. Process Windows for Common Materials

### 4.1 Carbon Steel (Mild / HSLA / S355)

**Typical GMAW parameters (1.2 mm wire, Ar/CO2 80/20):**
- Current: 150-280 A
- Voltage: 20-30 V
- Travel speed: 250-500 mm/min
- WFR: 6-12 m/min
- CTWD: 12-19 mm
- Preheat: 0-100 C (depends on CE and thickness)
- Heat input range: 0.5-2.5 kJ/mm
- Gas flow: 15-20 L/min

**Quality targets (AWS D1.1):**
- Max heat input: 2.5 kJ/mm for Q&T steels to limit HAZ softening.
- UTS (weld metal): 480-550 MPa for E71T-1 wires.
- CVN impact: >=27 J at -20 C.

**References:** AWS D1.1:2020; EN 1011-2:2009; Lancaster (1999); Cary & Helzer (2004).

### 4.2 Austenitic Stainless Steel (304, 316)

**Typical GTAW parameters (DCEN):**
- Current: 80-200 A
- Voltage: 10-15 V
- Travel speed: 100-300 mm/min
- Gas flow: 8-12 L/min pure Ar
- No preheat (preheat can increase sensitisation risk).
- Heat input: 0.4-1.5 kJ/mm.

**Quality targets:**
- Maintain ferrite number 3-10 in fusion zone to suppress hot cracking.
- Avoid sensitisation (Cr-carbide precipitation at 500-800 C): minimise time at temperature.
- Interpass temperature <=150 C typical.

**References:** Kou (2003); Lippold (2015); austenitic solidification cracking studies (literature review Section 4.1).

### 4.3 Aluminium (6061, 5083)

**Typical GMAW parameters (1.2 mm wire, pure Ar):**
- Current: 120-250 A (spray transfer DCEP)
- Voltage: 22-28 V
- Travel speed: 400-800 mm/min
- WFR: 8-14 m/min
- Gas flow: 18-24 L/min pure Ar
- Preheat: ambient to 150 C (for thick 6xxx to reduce porosity from trapped moisture).

**Quality targets:**
- Porosity <1% by volume (key challenge due to H solubility step at solidification).
- Avoid over-aging in 6xxx HAZ (loss of precipitation strengthening).
- Surface preparation critical: mechanical brushing + chemical cleaning.

**References:** Kou (2003); Al GMAW porosity studies (literature review Section 4.1); Cary & Helzer (2004).

### 4.4 High-Strength Steels (Q&T, e.g., HY-80, S690)

**GMAW/SMAW with strict controls:**
- Heat input typically capped at 1.5-2.0 kJ/mm to preserve HAZ properties.
- Preheat: 100-200 C depending on CE and thickness.
- Interpass: 150-200 C max.
- Low-hydrogen consumables mandatory (diffusible H < 5 ml/100 g).

**References:** EN 1011-2:2009; high strength steel welding studies (literature review references id=110).

### 4.5 WAAM (Wire Arc Additive Manufacturing)

**Typical parameters for carbon/low-alloy steel:**
- Current: 120-220 A
- Voltage: 18-25 V
- Travel speed: 300-600 mm/min
- Interpass temperature: 100-200 C (lower than conventional welding for shape retention).
- Dwell time between layers: 30-120 s.

**References:** WAAM literature review Section 8.2; ANN and NSGA-II WAAM studies.

---

## 5. ML Model Accuracy Benchmarks for Weld Quality Prediction

Drawn from literature review Sections 3 and 4. Numerical values are representative (not conservative lower bounds).

### 5.1 Bead Geometry Regression (GMAW, GTAW, FSW)

| Target | Model | Metric | Reference |
|--------|-------|--------|-----------|
| Bead width (GMAW) | 3-layer ANN (BP) | 0.23 mm mean error | Park et al. 2021 |
| Reinforcement (GMAW) | 3-layer ANN (BP) | 0.09 mm mean error | Park et al. 2021 |
| FSW params -> UTS (2024-T3 Al) | Random Forest, XGBoost | >98% accuracy (R^2 proxy) | Matitopanum et al. 2024 |
| Joint load capacity (RFSSW) | XGBoost | R^2 up to 0.89 | Mysliwiec et al. 2025 |
| Cross dissimilar materials | CatBoost, GB, XGBoost | Comparable (RMSE ~5-10% of mean) | Shinde et al. 2024 |

### 5.2 Mechanical Property Prediction

| Target | Model | Metric | Reference |
|--------|-------|--------|-----------|
| UTS / YS / elongation (FSW) | ANN, RF, XGBoost, MLP | R^2 ~0.85-0.95 | 2024-2025 FSW studies |
| Hardness (HAZ, ferritic) | RF on CCT features | Classification accuracy >90% for phase | Li et al. 2022 |
| Fatigue life | Coupled ML + physics | +/-1.2 log10(N) error band | Braun et al. 2022 |

### 5.3 Defect Classification (Radiographic / Vision)

| Target | Model | Accuracy | Reference |
|--------|-------|----------|-----------|
| RIAWELC (4-class) | ResNet50 | 98.75% | literature review Section 4.2 |
| 4-class weld defects | DenseNet121 + Grad-CAM | 98.88% | literature review Section 4.2 |
| Weld defect multi-class | ConvNeXt | 99.52% | literature review Section 4.2 |
| GTAW penetration state | MobileNetV2 | 99.88%, 65ms inference | literature review Section 6.4 |

### 5.4 Real-Time Process Signal Analysis

| Target | Model | Metric | Reference |
|--------|-------|--------|-----------|
| GMAW penetration from voltage | CNN | >97% accuracy, 0.38 s | Nature Sci Reports 2023 |
| Weld quality from I/V statistics | Classical ML (RF, SVM) | 95-100% abnormal/normal | literature review Section 4.3 |
| Weld quality monitoring | XGBoost + PSO | High (dataset-specific) | literature review Section 4.3 |

### 5.5 Small-Data Regression

| Method | Claim | Sample size |
|--------|-------|-------------|
| GPR with Matern kernel | Calibrated UQ | 20-200 |
| GPRN (FEA-DoE-GPRN hybrid) | Laser Al bead metrics | Small (tens) |
| Active learning (DGP) | Sample efficient | 20-100 |
| TabPFN foundation surrogate | Zero-shot regression | <=1000 |

### 5.6 Physics-Informed Gains

From literature review Section 3.4:
- PINN temperature field prediction: reduced error accumulation beyond active welding zone vs unconstrained NN.
- PHOENIX framework: real-time instability detection and parameter adjustment.
- Rosenthal + LSTM hybrid: improved extrapolation vs pure data-driven LSTM (Li et al. 2025).

---

## 6. Open Datasets for Welding ML

Not extensive compared to image classification benchmarks (literature review Section 10 gap 8). Known resources:

### 6.1 Radiographic Defect Datasets

- **RIAWELC:** Radiographic Images for Automatic Weld Defect Classification. 4 classes (crack, pore, non-penetration, no defect). Used for ResNet50, DenseNet121 benchmarking.
- **GDXRay:** Grima database of X-ray images including welds. Freely available.
- **INWELD:** Multi-category weld annotations under real production conditions (literature review Section 4.5).

### 6.2 Process Signal Datasets

- Most I/V signal datasets are proprietary to individual labs/OEMs; limited public release.
- Some GitHub/Mendeley repositories associated with published papers.

### 6.3 FSW/WAAM Parameter-Quality Datasets

- Small tabular datasets attached to individual papers (Matitopanum 2024 for Al 2024-T3 FSW; WAAM Inconel 625 studies).
- Typically 30-300 rows with inputs (params) and outputs (UTS, bead geometry).

### 6.4 UCI/Kaggle

- No widely adopted welding parameter-quality dataset on UCI at time of literature review.
- Occasional Kaggle competitions on weld defect imaging but not parameter optimisation.

### 6.5 HDR Dataset Strategy

Given the sparse benchmark landscape, the HDR project will:
1. Curate tabular datasets from published supplementary materials (Park et al., Matitopanum, Mysliwiec).
2. Augment with FEA-generated synthetic data (Goldak heat source + Rosenthal validation).
3. Use multi-fidelity and transfer learning (H10, H20) to stretch limited experimental data.

**References:** Literature review Sections 4 and 7; INWELD dataset; Matitopanum 2024; Mysliwiec 2025.

---

## 7. Physical Constants and Typical Values

For HDR code and quick sanity checks:

| Quantity | Symbol | Typical value | Notes |
|----------|--------|---------------|-------|
| Arc efficiency GMAW | eta_GMAW | 0.8 | Literature review Section 1.1 |
| Arc efficiency GTAW | eta_GTAW | 0.6 | Literature review Section 1.1 |
| Arc efficiency SAW | eta_SAW | 0.9 | Literature review Section 1.1 |
| Thermal conductivity carbon steel | k_steel | 45 W/m.K | At room temp |
| Density carbon steel | rho | 7850 kg/m^3 | |
| Specific heat carbon steel | c_p | 490 J/kg.K | |
| Melting point mild steel | T_m | 1510 C | |
| Austenite start Ac3 | Ac3 | ~800-900 C | Composition dependent |
| Martensite start Ms | Ms | 200-400 C | Composition dependent |
| IIW CE preheat threshold | CE_threshold | 0.45 | Above this, preheat mandatory |
| t8/5 typical range | | 5-30 s | Process and geometry dependent |

---

## 8. Standards and Codes Referenced

- **AWS D1.1/D1.1M:2020** Structural Welding Code -- Steel
- **AWS D1.2** Structural Welding Code -- Aluminum
- **ISO 15614-1:2017** Specification and qualification of welding procedures
- **EN 1011-2:2009** Welding recommendations for welding of metallic materials -- Part 2: Arc welding of ferritic steels
- **ASME BPVC Section IX** Welding, Brazing, and Fusing Qualifications
- **IIW Doc IX-535-67** Carbon equivalent formula
- **API 1104** Welding of Pipelines and Related Facilities

---

## 9. Cross-References

- **Design variables:** see `design_variables.md` for parameter ranges and definitions.
- **Research hypotheses:** see `research_queue.md` for Phase A/B tests.
- **Literature:** see `literature_review.md` for the full Phase 0 review and `papers.csv` for the bibliography.

---

## 10. Key Literature Citations

Drawn from `papers.csv`:

- Kou (2003) *Welding Metallurgy* [id=1] -- foundational metallurgy reference.
- Lancaster (1999) *Metallurgy of Welding* [id=2] -- heat input, CE, preheat.
- Easterling (1992) *Physical Metallurgy of Welding* [id=3] -- thermal cycles, HAZ.
- Goldak et al. (1984) [id=4] -- double-ellipsoidal heat source.
- Cary & Helzer (2004) *Modern Welding Technology* [id=8] -- process parameters.
- ASM Handbook Vol 6 [id=9] -- comprehensive process reference.
- AWS D1.1 [id=76], ISO 15614 [id=77], EN 1011-2 [id=78] -- standards.
- Park et al. (2021) [id=13] -- GMAW bead ANN benchmarks.
- Matitopanum et al. (2024) [id=15] -- FSW RF/XGBoost benchmarks.
- Mysliwiec et al. (2025) [id=16] -- XGBoost + NSGA-II.
- Li et al. (2022) [id=11] -- CCT diagram ML.
- Sarikhani & Pouranvari (2023) [id=14] -- WFR and penetration.
- Duggirala et al. (2024) [id=19] -- GPRN for laser Al.
- Li et al. (2025) [id=21] -- Rosenthal + LSTM.
- Braun et al. (2022) [id=18] -- transfer learning for fatigue.
