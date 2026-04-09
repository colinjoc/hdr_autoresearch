# Design Variables: FDM 3D Printing Parameter Optimisation

## Overview

This document catalogues all FDM/FFF design variables (input parameters), their feasible ranges, physical effects, and known interactions. Variables are grouped into categories: thermal, kinematic, structural, material, and auxiliary.

---

## 1. Thermal Parameters

### 1.1 Nozzle Temperature (T_nozzle)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | Celsius |
| Range (PLA) | 190 - 220 C |
| Range (ABS) | 230 - 250 C |
| Range (PETG) | 220 - 250 C |
| Range (TPU) | 210 - 230 C |
| Range (Nylon) | 240 - 270 C |
| Range (PEEK) | 360 - 420 C |
| Default (PLA) | 210 C |

**Effects:**
- Higher temperature improves interlayer bonding (better diffusion) and tensile strength [73]
- Too low: incomplete melting, intermittent extrusion, under-extrusion
- Too high: oozing, stringing, loss of dimensional accuracy, thermal degradation
- SHAP identifies nozzle temperature as the most influential parameter for tensile strength [73]

**Interactions:**
- Speed: higher speeds require higher temperatures for adequate melting
- Cooling: higher temps require more cooling to solidify bridges/overhangs
- Retraction: higher temps increase stringing, requiring more retraction

### 1.2 Bed Temperature (T_bed)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | Celsius |
| Range (PLA) | 50 - 60 C (or unheated) |
| Range (ABS) | 90 - 110 C |
| Range (PETG) | 70 - 80 C |
| Range (TPU) | 40 - 60 C |
| Default (PLA) | 60 C |

**Effects:**
- Ensures first-layer adhesion and prevents warping
- Too low: part detaches during print, corners lift
- Too high: elephant foot (first layer squished too wide), difficulty removing part
- Uneven bed heating is a primary warping cause for large flat parts

**Interactions:**
- Material: each material has a narrow optimal window
- Part geometry: large flat surfaces more sensitive
- Enclosure temperature: heated enclosures reduce bed temperature requirements for ABS

### 1.3 Cooling Fan Speed (F_cool)

| Property | Value |
|----------|-------|
| Type | Continuous (percentage) |
| Unit | % of max fan speed |
| Range | 0 - 100% |
| Default (PLA) | 100% |
| Default (ABS) | 0 - 20% |
| Default (PETG) | 30 - 50% |

**Effects:**
- Higher cooling improves bridge/overhang quality (faster solidification)
- Higher cooling reduces interlayer bonding (less time for diffusion)
- PLA: benefits from maximum cooling; critical for detail and overhangs
- ABS: minimal or no cooling to prevent warping and layer cracking
- PETG: moderate cooling balances overhang quality with layer adhesion

**Interactions:**
- Temperature: higher nozzle temps may tolerate more cooling
- Speed: slower speeds allow more natural cooling, reducing fan dependence
- Layer height: thinner layers cool faster naturally

### 1.4 Enclosure Temperature (T_enclosure)

| Property | Value |
|----------|-------|
| Type | Continuous (if available) |
| Unit | Celsius |
| Range | Ambient (22 C) - 70 C |
| Notes | Only on enclosed printers |

**Effects:**
- Reduces temperature gradient between deposited material and environment
- Critical for ABS, Nylon, and engineering plastics to prevent warping
- Too hot: PLA softens and deforms

---

## 2. Kinematic Parameters

### 2.1 Print Speed (v_print)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm/s |
| Range | 20 - 500 mm/s |
| Typical (standard) | 40 - 80 mm/s |
| Typical (high-speed) | 150 - 300 mm/s |
| Default (PLA) | 50 mm/s |

**Effects:**
- Higher speed reduces print time proportionally
- Higher speed generally reduces tensile strength and surface quality
- Optimal balance at ~300 mm/s for high-speed PLA filaments [111]
- Higher speed can improve bonding by reducing cooling time between layers at certain ranges [58]
- Very high speeds cause under-extrusion if volumetric flow limit is reached

**Interactions:**
- Temperature: faster speeds need higher temps
- Layer height: speed x layer_height x line_width = volumetric flow rate
- Cooling: faster moves reduce time for cooling fan to act

### 2.2 Travel Speed (v_travel)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm/s |
| Range | 100 - 500 mm/s |
| Default | 150 mm/s |

**Effects:**
- Speed during non-printing moves
- Higher travel speed reduces stringing (less time for oozing)
- Very high speeds can cause vibration artifacts (ringing/ghosting)

### 2.3 First Layer Speed (v_first)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm/s |
| Range | 10 - 40 mm/s |
| Default | 20 mm/s |

**Effects:**
- Slower first layer improves bed adhesion
- Critical for preventing first-layer failures

### 2.4 Acceleration (a_print)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm/s^2 |
| Range | 500 - 20000 mm/s^2 |
| Default | 1000 - 3000 mm/s^2 |

**Effects:**
- Higher acceleration reduces print time on short segments
- Too high causes ringing/ghosting artifacts
- Input shaper algorithms can compensate for resonance

---

## 3. Geometric / Structural Parameters

### 3.1 Layer Height (h_layer)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm |
| Range | 0.05 - 0.4 mm |
| Typical | 0.12 - 0.28 mm |
| Default | 0.2 mm |
| Constraint | Should be < 80% of nozzle diameter |

**Effects:**
- **Most influential parameter overall** per ANOVA studies [34, 36, 47]
- Lower layer height: better surface finish (Ra), stronger interlayer bonds, better accuracy
- Higher layer height: faster print, but worse surface quality and potentially weaker bonding
- Contributes highest variance to both build time and surface roughness

**Interactions:**
- Nozzle diameter: layer height must be less than nozzle diameter
- Speed: thinner layers allow higher linear speeds while maintaining volumetric flow
- Cooling: thinner layers cool faster

### 3.2 Line Width / Extrusion Width (w_line)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm |
| Range | 0.3 - 0.8 mm |
| Default | ~1.0 to 1.2x nozzle diameter |
| Constraint | Typically 100-120% of nozzle diameter |

**Effects:**
- Wider lines improve layer adhesion (more contact area)
- Narrower lines improve detail resolution
- Affects volumetric flow requirement

### 3.3 Infill Density (rho_infill)

| Property | Value |
|----------|-------|
| Type | Continuous (percentage) |
| Unit | % |
| Range | 0 - 100% |
| Typical functional | 20 - 60% |
| Default | 20% |

**Effects:**
- SHAP identifies infill density as most significant for UTS (+2.75) and flexural strength (+5.8) [74]
- Linear relationship with weight and material cost
- Diminishing strength returns above ~60%
- 100% = solid part (maximum strength, maximum time/material)

### 3.4 Infill Pattern (P_infill)

| Property | Value |
|----------|-------|
| Type | Categorical |
| Options | Grid, Lines, Rectilinear, Triangles, Cubic, Gyroid, Honeycomb, Lightning, Concentric |

**Effects by pattern:**
- **Gyroid**: Best isotropic strength-to-weight ratio, highest mean tensile fracture force [44]
- **Honeycomb**: Excellent compression resistance, ~25% more material, 2x print time
- **Rectilinear/Grid**: Fast, predictable, steady strength
- **Cubic**: Good all-around with consistent 3D strength
- **Lightning**: Minimal material for top-surface-only support (not structural)
- **Concentric**: Good for cylindrical parts

### 3.5 Number of Perimeters / Wall Loops (N_walls)

| Property | Value |
|----------|-------|
| Type | Discrete integer |
| Unit | count |
| Range | 1 - 10 |
| Default | 2 - 3 |

**Effects:**
- More walls increase strength (especially in bending and impact)
- More walls improve surface quality
- Each wall adds ~2x line width to part shell thickness

### 3.6 Top/Bottom Solid Layers (N_top, N_bottom)

| Property | Value |
|----------|-------|
| Type | Discrete integer |
| Unit | count |
| Range | 2 - 10 |
| Default | 3 - 5 |

**Effects:**
- Enough layers prevent infill showing through top surface
- More layers improve strength of horizontal surfaces

### 3.7 Build Orientation

| Property | Value |
|----------|-------|
| Type | Categorical (or angular) |
| Options | Flat (XY), On-edge (XZ), Upright (Z) |

**Effects:**
- Determines anisotropy direction relative to load
- Flat orientation maximises XY strength
- Upright orientation weakest in Z (interlayer failure)
- On-edge can increase interface toughness by 389% in multi-material prints [93]

### 3.8 Raster Angle (theta_raster)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | Degrees |
| Range | 0 - 90 degrees (or alternating +/-45) |
| Default | +/-45 degrees |

**Effects:**
- 0 degrees (aligned with load): maximum tensile and flexural strength [49, 52, 54]
- 90 degrees (perpendicular to load): minimum strength (~50% of 0-degree) 
- +/-45 degrees: balanced, intermediate properties
- Failure mode changes: 0 degree = raster failure, 90 degree = inter-raster bond failure

---

## 4. Extrusion Control Parameters

### 4.1 Flow Rate / Extrusion Multiplier (M_flow)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | Dimensionless ratio (or %) |
| Range | 0.85 - 1.15 |
| Default | 1.0 (100%) |

**Effects:**
- Under-extrusion (< 1.0): gaps between roads, weak parts
- Over-extrusion (> 1.0): surface scarring, dimensional error
- Calibrated per material using single-wall test cube

### 4.2 Retraction Distance (d_retract)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm |
| Range (Direct Drive) | 0.5 - 2.0 mm |
| Range (Bowden) | 4.0 - 7.0 mm |
| Default (Direct Drive) | 1.0 mm |

**Effects:**
- Controls stringing during travel moves
- Too much: filament grinding, jams, under-extrusion after travel
- Too little: stringing, oozing, blobs

### 4.3 Retraction Speed (v_retract)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm/s |
| Range | 20 - 70 mm/s |
| Default | 40 mm/s |

**Effects:**
- Faster retraction reduces oozing more effectively
- Too fast can cause filament grinding or jams

### 4.4 Z-Hop Height (h_zhop)

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm |
| Range | 0 - 2.0 mm |
| Default | 0 (disabled) or 0.2 mm |

**Effects:**
- Lifts nozzle during travel to avoid hitting printed features
- Can increase stringing slightly
- Useful for tall, thin features

---

## 5. Material Parameters

### 5.1 Material Type

| Property | Value |
|----------|-------|
| Type | Categorical |
| Options | PLA, ABS, PETG, TPU, Nylon, PEEK, PLA+, CF-PLA, CF-Nylon, etc. |

**Effects:**
- Determines all thermal parameter ranges
- Determines mechanical property ceilings
- ANOVA shows material type is among the most significant factors for accuracy and roughness [36]

### 5.2 Filament Diameter

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | mm |
| Values | 1.75 mm or 2.85 mm |
| Tolerance | +/- 0.02 mm |

**Effects:**
- Diameter inconsistency causes extrusion variation
- 1.75mm is the modern standard

### 5.3 Nozzle Diameter (d_nozzle)

| Property | Value |
|----------|-------|
| Type | Categorical/discrete |
| Unit | mm |
| Options | 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0 mm |
| Default | 0.4 mm |

**Effects:**
- Constrains minimum layer height and line width
- Larger nozzles: faster printing, rougher surface
- Smaller nozzles: finer detail, slower printing
- 0.8mm nozzle with low layer height can yield favorable mechanical properties [47]

---

## 6. Adhesion and Support Parameters

### 6.1 Brim Width / Line Count

| Property | Value |
|----------|-------|
| Type | Continuous / Discrete |
| Unit | mm or count |
| Range | 0 - 20 mm (or 0 - 15 lines) |
| Default | 5-6 lines for warping-prone materials |

### 6.2 Raft Parameters

- Raft layers: 2-4
- Raft air gap: 0.1 - 0.3 mm
- Raft margin: 3 - 10 mm

### 6.3 Support Density

| Property | Value |
|----------|-------|
| Type | Continuous |
| Unit | % |
| Range | 5 - 30% |

---

## Summary: Parameter Importance Rankings

Based on ANOVA and SHAP analyses across multiple studies:

### For Surface Roughness (Ra):
1. Layer height (highest contribution) [34, 36, 85]
2. Print speed [85]
3. Infill percentage [85]
4. Nozzle temperature [46]

### For Tensile Strength:
1. Nozzle temperature [73]
2. Infill density [74]
3. Layer height [46, 49]
4. Raster angle [52, 54]
5. Print speed [112]

### For Dimensional Accuracy:
1. Layer height [36, 117]
2. Material type [36]
3. Print speed [111]
4. Nozzle temperature [79]

### For Print Time:
1. Layer height (inversely proportional)
2. Print speed (inversely proportional)
3. Infill density (proportional)
4. Infill pattern (Gyroid slowest, Rectilinear fastest)

---

## Total Design Variable Count

| Category | Count | Type |
|----------|-------|------|
| Thermal | 4 | Continuous |
| Kinematic | 4 | Continuous |
| Geometric/Structural | 8 | Mixed |
| Extrusion Control | 4 | Continuous |
| Material | 3 | Mixed |
| Adhesion/Support | 3 | Mixed |
| **Total** | **26** | |

For the HDR tabular optimisation task, a practical subset of 8-12 most influential continuous parameters is recommended, with material type as a categorical conditioning variable.
