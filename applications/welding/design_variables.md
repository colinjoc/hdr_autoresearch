# Design Variables: Welding Parameter Optimisation HDR

## Phase 0 -- Design Variable Specification

**Date:** 2026-04-02
**Scope:** Parameters the HDR optimisation loop will iterate over. Ranges, effects, defect risks, and references drawn from `literature_review.md`.

---

## Overview

The HDR loop treats welding as a parameter-to-quality mapping problem. Design variables fall into four tiers:

1. **Primary electrical parameters** (current, voltage, travel speed, wire feed rate) -- the dominant drivers of heat input and bead geometry.
2. **Thermal/chemistry parameters** (shielding gas composition and flow rate, preheat/interpass temperature) -- controlling atmospheric protection, arc behaviour, and thermal cycles.
3. **Geometric parameters** (joint geometry, number of passes, torch angle, CTWD) -- affecting fusion, access, and local heat distribution.
4. **Derived physics-informed features** (heat input, cooling time t8/5, carbon equivalent, energy density) -- engineered from primary parameters but frequently the highest-leverage HDR features (literature review Section 10, gap 2).

All primary variables below are candidates for direct optimisation. Derived features appear in `research_queue.md` Phase A as feature-engineering hypotheses.

---

## 1. Welding Current (I)

**Units:** Amperes (A)
**Typical range:** 80-400 A for GMAW on carbon/stainless steel; 50-300 A for GTAW; up to 1000+ A for SAW.
**Sub-variables:**
- **Polarity:** DCEP (electrode positive), DCEN (electrode negative), AC. DCEP is dominant in GMAW short-circuit/spray; DCEN in GTAW steel; AC in GTAW aluminium.
- **Waveform:** Constant DC vs pulsed DC. Pulsed parameters add peak current (I_p), base current (I_b), pulse frequency (f), and duty cycle (delta).

**Effect on quality:**
- Single most influential parameter on penetration depth -- approximately 2.5x the effect of other parameters (Lincoln Electric; literature review Section 2.1).
- Increases deposition rate, heat input, and bead reinforcement.
- In GMAW, directly coupled with wire feed rate.

**Defect risks:**
- Excessive: burn-through on thin sheet; excessive heat input causes HAZ softening, grain coarsening, distortion.
- Insufficient: lack of fusion, incomplete penetration, cold lap, arc instability.

**HDR treatment:** Continuous variable. For pulsed modes, also optimise (I_p, I_b, f, delta).

**References:** Kou (2003); Lancaster (1999); Sarikhani & Pouranvari (2023); Lincoln Electric technical guide; pulsed GMAW waveform studies.

---

## 2. Arc Voltage (V)

**Units:** Volts (V)
**Typical range:** 16-34 V for GMAW; 10-20 V for GTAW; 28-42 V for SAW.

**Effect on quality:**
- Controls arc length and bead shape. Increasing V flattens the bead (higher width-to-depth ratio).
- Virtually no effect on penetration depth for constant-current welding (literature review Section 2.1).
- Affects metal transfer mode (short circuit vs globular vs spray) in GMAW.

**Defect risks:**
- Excessive: undercut, porosity, spatter, excessive arc wander.
- Insufficient: stubbing, poor arc start, irregular bead profile, cold lap.

**HDR treatment:** Continuous variable. Often coupled to current via power source characteristic (CV for GMAW, CC for GTAW/SMAW).

**References:** Kou (2003); Lancaster (1999); AWS D1.1; Lincoln Electric technical guide.

---

## 3. Travel Speed (v)

**Units:** mm/min (alternatively mm/s or in/min)
**Typical range:** 150-900 mm/min for GMAW; 50-300 mm/min for GTAW manual; up to 2000 mm/min for automated laser/EBW.

**Effect on quality:**
- Inversely proportional to heat input: HI = (60 V I eta) / (1000 v).
- Slower speeds increase penetration, bead width, reinforcement, and HAZ width (up to saturation).
- Faster speeds narrow bead, reduce heat input, and suppress distortion.

**Defect risks:**
- Excessive: incomplete fusion, undercut, humping, unstable weld pool.
- Insufficient: excessive heat input, distortion, HAZ grain coarsening, burn-through on thin material.

**HDR treatment:** Continuous variable. Strongly coupled to current and voltage in the heat-input expression.

**References:** Kou (2003); Goldak et al. (1984); Sarikhani & Pouranvari (2023); Lancaster (1999).

---

## 4. Wire Feed Rate (WFR)

**Units:** m/min
**Typical range:** 2-20 m/min for GMAW; process-dependent.
**Applies to:** GMAW, FCAW, SAW, WAAM.

**Effect on quality:**
- In GMAW with CV power sources, WFR and current are directly coupled -- increasing WFR increases current and thus penetration.
- Maximum penetration achieved at lowest welding speed and highest WFR (Sarikhani & Pouranvari, 2023).
- Governs deposition rate; drives bead reinforcement and dilution.

**Defect risks:**
- Excessive: excessive reinforcement, burn-through, spatter, poor sidewall fusion at high dilution.
- Insufficient: arc instability, lack of fusion, undersized bead.

**HDR treatment:** Continuous variable. For constant-current power sources, WFR is decoupled from current and becomes an independent optimisation variable.

**References:** Sarikhani & Pouranvari (2023); Park et al. (2021); Lincoln Electric.

---

## 5. Shielding Gas Type

**Categorical variable**
**Options:**
- Pure Ar (GTAW, Al GMAW)
- Pure CO2 (economy GMAW carbon steel)
- Ar/CO2 blends: 95/5, 90/10, 85/15, 80/20, 75/25 (GMAW carbon steel)
- Ar/He blends: 75/25, 50/50 (thick Al, Cu)
- Ar/O2 blends: 98/2, 95/5, 99/1 (spray transfer stainless, carbon steel)
- Ar/CO2/O2 ternary blends (galvanised steel -- less porosity and pitting)
- Pure He (hot arc for thick Al)

**Effect on quality:**
- Pure Ar: stable arc, narrow penetration, good bead appearance.
- Higher CO2: deeper penetration, more spatter, improved ductility but lower UTS/YS.
- He additions: hotter arc, broader penetration, faster travel speeds.
- Ternary blends: best for galvanised steel (reduced pitting/porosity/spatter).

**Defect risks:**
- Wrong gas for process: porosity (Ar in FCAW self-shielded; CO2 in Al GMAW).
- High CO2 on high-strength steel: embrittlement, reduced tensile.
- He too high: high cost, arc instability at low flows.

**HDR treatment:** Categorical variable with one-hot or mole-fraction (Ar fraction, CO2 fraction, He fraction, O2 fraction) encoding. Mole-fraction encoding enables continuous optimisation across blend space.

**References:** Kou (2003); literature review Section 2.2; Ar/CO2/O2 ternary blend studies (Welding Journal 2021).

---

## 6. Shielding Gas Flow Rate (Q_gas)

**Units:** L/min
**Typical range:** 10-25 L/min for GMAW; 5-15 L/min for GTAW; up to 30+ L/min for large nozzles or cross-wind.

**Effect on quality:**
- Maintains atmospheric exclusion over weld pool.
- Optimal range depends on nozzle diameter, torch-to-work distance, and ambient airflow.

**Defect risks:**
- Insufficient: porosity (N2, O2, H2 contamination), surface oxidation.
- Excessive: turbulent entrainment of air, increased cost, porosity at high flows.

**HDR treatment:** Continuous variable. Often coupled with nozzle diameter for dimensionless flow characterisation.

**References:** Lancaster (1999); Kou (2003); Lincoln Electric technical guide.

---

## 7. Preheat Temperature (T_preheat)

**Units:** Celsius
**Typical range:** Ambient (20 C) to 250 C for carbon/low-alloy steels; up to 400+ C for Cr-Mo creep-resistant steels; ambient for austenitic stainless and aluminium (preheat can be detrimental).

**Effect on quality:**
- Slows HAZ cooling rate (increases t8/5), shifting transformation products away from martensite toward tougher bainite/ferrite.
- Reduces residual stress through more uniform thermal contraction.
- Reduces hydrogen cracking risk by allowing diffusible hydrogen to escape.
- Required when CE > 0.45 or thickness > ~25 mm for carbon steels (IIW).

**Defect risks:**
- Insufficient: cold cracking, martensitic HAZ, high residual stress, low toughness.
- Excessive: HAZ grain coarsening, softening, loss of precipitation hardening in Al 6xxx/7xxx.

**HDR treatment:** Continuous variable. Coupled with CE and thickness for physics-informed preheat recommendations.

**References:** Lancaster (1999); Easterling (1992); IIW Doc IX-535-67; literature review Section 1.3, 1.4.

---

## 8. Interpass Temperature (T_interpass)

**Units:** Celsius
**Typical range:** 150-300 C for most multi-pass steel welds; capped by material specification (e.g., 250 C for Q&T steels to preserve toughness).

**Effect on quality:**
- Low interpass gives higher strength but lower toughness; relationship reverses above a critical threshold (Easterling, 1992).
- Controls grain growth in the CGHAZ of previous passes.

**Defect risks:**
- Too low: cold cracking between passes.
- Too high: grain coarsening, toughness degradation, softening of HAZ.

**HDR treatment:** Continuous variable, often bounded by specification maximum. For WAAM, substitute `interpass cooling time` or `dwell time`.

**References:** Easterling (1992); literature review Section 2.2; WAAM interpass studies.

---

## 9. Joint Geometry

**Composite variable** comprising:
- **Groove angle (alpha):** 30-90 degrees; V, U, J, bevel, square butt; influences fill volume and access.
- **Root gap (g):** 0-6 mm; influences root fusion and burn-through risk.
- **Root face (h):** 0-3 mm; influences root fusion.
- **Included angle:** For double-V or X grooves, total included angle 40-90 degrees.
- **Land height:** For J/U grooves.

**Effect on quality:**
- Groove angle drives fill volume -- narrower grooves reduce deposition required but increase sidewall fusion risk.
- Root gap enables root penetration but increases burn-through and distortion risk.
- Joint preparation quality (roughness, squareness) affects repeatability of ML predictions.

**Defect risks:**
- Narrow groove angle: lack of sidewall fusion, slag entrapment.
- Excessive root gap: burn-through, sag, excessive distortion.
- Inconsistent prep: high prediction variance.

**HDR treatment:** Continuous variables for alpha, g, h. Joint type is categorical.

**References:** AWS D1.1:2020; ISO 15614; Cary & Helzer (2004) Modern Welding Technology.

---

## 10. Number of Passes (N_pass)

**Units:** Integer count
**Typical range:** 1 (thin sheet, single pass) to 30+ (thick-section pressure vessels).

**Effect on quality:**
- Thin-to-medium plate: single or 2-3 passes.
- Thick plate: multi-pass fill to manage heat input per pass, refine microstructure via tempering of prior passes.
- More passes reduces heat input per pass, improving HAZ toughness but increasing cycle time.

**Defect risks:**
- Too few: excessive heat input per pass, HAZ embrittlement.
- Too many: loss of productivity, accumulated distortion, slag inclusion between passes.

**HDR treatment:** Integer variable. Couples with per-pass heat input to meet total fill volume. For WAAM, equivalent to layer count.

**References:** Lancaster (1999); literature review Section 2.2; multi-pass welding studies.

---

## 11. Torch/Electrode Angle

**Units:** Degrees
**Typical range:**
- **Travel angle:** 0-25 degrees drag or push.
- **Work angle:** 30-60 degrees for fillets; ~90 for butt welds.

**Effect on quality:**
- Drag angle (pointed toward puddle): deeper penetration.
- Push angle (pointed away from puddle): shallower penetration, better visibility, less spatter.
- Work angle on fillet welds: ~45 degrees targets even leg length.

**Defect risks:**
- Wrong work angle: unequal leg length, undercut on vertical member, convexity.
- Excessive push angle: lack of fusion.

**HDR treatment:** Continuous variables for travel and work angle. In robotic welding, can be directly optimised.

**References:** Literature review Section 2.2; AWS D1.1; Lincoln Electric technical guide.

---

## 12. Contact Tip to Work Distance (CTWD)

**Units:** mm (or inches)
**Typical range:** 10-25 mm (3/8-1 inch).
**Applies to:** GMAW, FCAW, SAW.

**Effect on quality:**
- Increasing CTWD increases resistive (I^2 R) heating of the wire extension, decreasing effective amperage at the arc.
- Affects shielding gas coverage and arc stability.

**Defect risks:**
- Too short: contact tip burnback, spatter buildup, poor gas coverage.
- Too long: reduced effective amperage, poor shielding, porosity, irregular bead.

**HDR treatment:** Continuous variable. Typical targets: 3/8-1/2 inch (10-13 mm) for short-circuit; 3/4 inch (19 mm) for spray transfer.

**References:** Lincoln Electric technical guide; literature review Section 2.1.

---

## 13. Derived Physics-Informed Features

These are **engineered features** computed from primary variables. HDR Phase A hypotheses test whether derived features improve predictive performance versus raw parameters (literature review Section 10, gap 2).

### 13.1 Heat Input (HI)

    HI [kJ/mm] = (60 * V * I * eta) / (1000 * v)

where eta is arc efficiency (0.6 GTAW, 0.8 GMAW, 0.9 SAW).

**Role:** Dominant physics-informed predictor for HAZ size, cooling rate, and microstructural outcomes.

**References:** Kou (2003); Lancaster (1999); Goldak et al. (1984).

### 13.2 Cooling Time t8/5

    t8/5 approx HI / (k * thickness * (T_max - T_preheat))

(first-order; refined via Rosenthal analytical solution or FEA)

**Role:** Links heat input and preheat to microstructural transformation products in HAZ.

**Typical values:** 5-30 seconds depending on material and geometry.

**References:** Easterling (1992); Lancaster (1999); Rosenthal solution reviews.

### 13.3 Carbon Equivalent (CE, IIW formula)

    CE = C + Mn/6 + (Cr + Mo + V)/5 + (Ni + Cu)/15

**Role:** Weldability indicator; thresholds (0.35, 0.45) flag preheat requirements.

**References:** IIW Doc IX-535-67; Lancaster (1999).

### 13.4 Energy Density (Laser/EBW)

    rho_E = Power / (pi * (d_spot/2)^2 * v)

**Role:** Governs keyhole formation in high-energy-density processes.

**References:** Goldak et al. (1984); laser keyhole welding studies.

### 13.5 Voltage-to-Current Ratio (V/I)

**Role:** Proxy for arc length and metal transfer mode in GMAW. HDR Phase A hypothesis tests whether V/I outperforms raw V and I as a feature.

**References:** GMAW process monitoring studies.

### 13.6 Specific Heat Input (HI per unit thickness)

    HI_spec = HI / thickness

**Role:** Normalises heat input for multi-pass and variable-thickness comparisons.

**References:** Lancaster (1999); EN 1011-2:2009.

---

## 14. Variable Grouping for HDR Phases

**Phase A (feature engineering):** All primary variables (1-12) plus derived features (13) -- identify which features most predict weld quality across benchmark datasets.

**Phase B (optimisation):** Continuous and categorical variables (1-12) optimised via NSGA-II / Bayesian optimisation against multi-objective targets (tensile strength, HAZ width, distortion, defect probability).

**Constraints:**
- Physical bounds on each variable (from process and material limits).
- Coupling constraints (e.g., WFR and I linked in GMAW CV mode).
- Code constraints (AWS D1.1, ISO 15614, EN 1011-2) on heat input and preheat.
- Productivity constraints (minimum travel speed, maximum passes).

---

## 15. References

Full bibliography in `papers.csv`. Key references for this document:

- Kou, S. (2003). *Welding Metallurgy*, 2nd ed. Wiley. [papers.csv id=1]
- Lancaster, J.F. (1999). *Metallurgy of Welding*, 6th ed. Abington Publishing. [id=2]
- Easterling, K.E. (1992). *Introduction to the Physical Metallurgy of Welding*, 2nd ed. Butterworth-Heinemann. [id=3]
- Goldak, J., Chakravarti, A., Bibby, M. (1984). A new finite element model for welding heat sources. [id=4]
- Cary, H.B. & Helzer, S.C. (2004). *Modern Welding Technology*, 6th ed. Prentice Hall. [id=8]
- ASM Handbook Volume 6: Welding, Brazing, and Soldering. [id=9]
- AWS D1.1:2020 Structural Welding Code Steel. [id=76]
- ISO 15614-1:2017 Specification and Qualification of Welding Procedures. [id=77]
- IIW Doc IX-535-67 (Carbon equivalent formula). [id=75]
- Sarikhani & Pouranvari (2023). GMAW penetration and WFR. [id=14]
