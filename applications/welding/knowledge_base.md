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

---

## 11. Phase 2 Findings (added 2026-04-09)

These entries record what the Hypothesis-Driven Research (HDR) loop
**learned** on top of the Phase 0 literature review. They are kept as a
separate section so the Phase 0 content above remains a pure lit-review
record.

### 11.1 Heat input (HI) is necessary but not sufficient for Heat-Affected Zone (HAZ) prediction

On a 560-row synthetic arc-welding dataset generated from the Rosenthal
closed-form heat-flow solution, a linear regression using only
HI = (eta * V * I) / (v * 1000) as a feature achieves cross-validated
R^2 = 0.485 — well below the hypothesised 0.80 target in H1. Adding
HI to a boosted-tree model (LightGBM) drops the 5-fold Mean Absolute
Error (MAE) from 1.63 mm to 1.57 mm (3.4 percent) -- a real but modest
gain. The dominant residual variance comes from the thin-/thick-plate
regime switch at ~6 mm thickness, which a single HI scalar cannot
represent.

**Lesson:** Heat input alone is a necessary feature but thickness must
enter the feature set explicitly or the model cannot separate the 2D
and 3D heat-flow regimes.

### 11.2 Cooling time t_{8/5} adds more than HI

Adding the Rosenthal-derived cooling time t_{8/5} on top of the raw
parameters dropped MAE from 1.63 to 1.32 mm — a 19 percent improvement,
five times larger than HI alone. t_{8/5} is a scalar of the same
physics as HI but has different thickness dependence (quadratic for
thin plate, linear for thick plate) which the single HI scalar does
not encode.

**Lesson:** When two physics scalars express the same underlying heat
flow in different ways, include both. Tree models will learn which to
use in which regime.

### 11.3 Monotonicity constraints beat hyperparameter tuning

On this dataset, XGBoost with the constraint that `HI -> HAZ` and
`t_{8/5} -> HAZ` must be non-decreasing gave MAE 1.28 mm — better than
any combination of learning rate, depth, subsample, or estimator count
we tested. Hyperparameter tuning alone never beat the default setting
by more than 1 percent.

**Lesson:** Physics-informed hard constraints are a higher-ROI lever
than hyperparameter search on small (N~500) physics datasets. This
is consistent with the concrete HDR project's P25.5 finding (monotone
cement -> strength was the final winning change).

### 11.4 Log-target transform is a composition-only win

Training on log(1 + HAZ) with the raw feature set reverted (E29,
delta = +0.02 mm over the running best). Training on log(1 + HAZ)
*composed* with the HI + t_{8/5} + monotonicity bundle gave the final
winning MAE of 1.19 mm -- a 8 percent drop from the non-log variant
and a 30 percent drop from the E00 baseline.

**Lesson:** Variance-stabilising target transforms should be re-tested
in composition with feature-engineering changes, not only in isolation.
The methodology's Phase 2.5 compositional retest exists exactly for
this case.

### 11.5 Cross-process transfer (GMAW -> GTAW) refuted

H20 from `research_queue.md` claimed a model trained on Gas Metal Arc
Welding (GMAW) would transfer to Gas Tungsten Arc Welding (GTAW) with
small loss because of shared physics. On this dataset the GMAW -> GTAW
transfer MAE was 3.95 mm against a 0.71 mm within-family CV baseline
(+455 percent gap). The reverse direction (GTAW -> GMAW) was worse
(MAE 9.76 mm, R^2 = -0.75 — worse than predicting the mean).

**Lesson:** Arc efficiency and typical working windows differ enough
between GMAW (eta 0.8, thick plate 3-20 mm) and GTAW (eta 0.6, thin
plate 1.5-10 mm) that a single model does not generalise. Textbook
claims of "heat input is universal" refer to physical principles, not
to the calibration of ML regressors.

### 11.6 Inverse design recovered the thin-plate low-heat-input window

Phase B screened 1760 candidate tuples across five strategies. The
top-5 candidates satisfying HAZ <= 5 mm were all at the low-voltage
(18-24 V), low-current (100 A), high-travel-speed (10-15 mm/s),
thin-plate (4-6 mm) corner of the parameter space. This is exactly
the prescription Kou (2003) ch. 2 gives for narrow-HAZ welds. The
model independently rediscovered it.

### 11.7 Dataset gap (re-affirmed)

A genuine open tabular welding parameter-quality dataset with bead
geometry or HAZ measurements remains **unavailable** as of 2026-04.
Every public release we could find in this session was either
time-series process signals (not tabular), radiographic image data
(different task), or too large to fetch in-session (Zenodo 12.7 GB).
The Mendeley simulated-robotic-welding dataset
(`data.mendeley.com/datasets/ndcns86bzt/1`) is binary classification.
The Matitopanum et al. 2024 FSW tabular data is 45 rows -- too small
for regression. Future welding HDR projects should budget time for
curating data from supplementary materials.
