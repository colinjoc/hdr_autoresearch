# Design Variables for Paint/Coating Formulation HDR

This document enumerates all formulation variables that an HDR (Hypothesis-Driven Research) loop would iterate on for paint/coating optimisation. Variables are grouped by function. For each: typical range, effect on properties, physical mechanism, and references from `literature_review.md`.

Numbers in square brackets refer to the lit review sections (e.g. [LR 1.2] = Section 1.2 of `literature_review.md`) or to `papers.csv` entries (e.g. [papers #23]).

---

## 1. Binder (Resin) Variables

### 1.1 Binder type (categorical)
- **Options**: acrylic latex, vinyl-acrylic, alkyd (short/medium/long oil), epoxy, polyurethane (1K/2K), silicone, vinyl ester, UV-curable oligomer (epoxy acrylate, urethane acrylate, polyester acrylate).
- **Effect**: sets the ceiling on adhesion, chemical/UV resistance, flexibility, hardness, and cure mechanism. It is the single largest determinant of coating performance class.
- **Mechanism**: chemistry determines backbone energetics, crosslink topology, and polarity matching to substrate. Acrylics give UV stability; alkyds autoxidatively crosslink; epoxies form high-Tg thermosets; polyurethanes balance hardness and flexibility [LR 1.3].
- **References**: LR 1.1, 1.3; papers #1, #9, #23.

### 1.2 Binder content / solids fraction
- **Typical range**: 20-70 wt% in wet paint; 40-95 vol% in dry film depending on PVC.
- **Effect**: higher binder lowers PVC, improving gloss, barrier, mechanical strength; raises cost, VOC (for solvent-borne), viscosity.
- **Mechanism**: binder forms the continuous matrix phase; below CPVC the matrix is void-free (LR 1.2).
- **References**: LR 1.1, 1.2; papers #25, #28.

### 1.3 Glass transition temperature (Tg) of binder
- **Typical range**: -20 C to +80 C for architectural latex; up to 120 C for industrial thermosets.
- **Effect**: Tg must be below MFFT for film formation. Lower Tg -> softer film, better film formation, worse block resistance. Higher Tg -> harder, more durable, but needs coalescing aid.
- **Mechanism**: controlled via monomer selection (MMA for high Tg, BA/2-EHA for low Tg); Fox equation predicts blended Tg. Core-shell latex particles decouple film formation from service hardness.
- **References**: LR 1.3, 1.4; papers #1, #11.

### 1.4 NCO/OH or amine-H/epoxide stoichiometric ratio (thermoset binders)
- **Typical range**: 0.95-1.15 (2K systems); 1.05-1.10 most common; 1.03-1.06 high-build; 1.05-1.10 thin coatings.
- **Effect**: 1:1 gives peak crosslink density, highest Tg, best chemical resistance. Amine excess -> flexibility + blush risk. Epoxy excess -> hydrolysis susceptibility. NCO excess increases rigidity and chemical resistance.
- **Mechanism**: governs final crosslink density in step-growth networks; off-stoichiometry leaves dangling ends and unreacted reactive groups.
- **References**: LR 1.3; papers #9, #14.

### 1.5 Alkyd oil length
- **Options**: short (~30% oil), medium (~50%), long (~60%).
- **Effect**: short -> hard, fast-dry, industrial baking; medium -> balanced brush/durability; long -> flexible, slow-dry, architectural trim.
- **Mechanism**: longer unsaturated fatty-acid chains increase chain mobility and autoxidative crosslink spacing.
- **References**: LR 1.3.

### 1.6 Binder blend ratios (ternary or higher)
- **Typical range**: 0-100 wt% of each binder in the binder fraction, subject to sum = 1.
- **Effect**: can capture synergies (e.g. epoxy-polyurethane hybrids raise tensile strength from 39 to 86 MPa and adhesion from 2.5 to 8.3 MPa at 5-15% epoxy).
- **Mechanism**: compatible blends give interpenetrating networks; incompatible blends phase-separate into morphology that can toughen or weaken.
- **References**: LR 6.2; papers #4, #9.

---

## 2. Pigment and Extender Variables

### 2.1 Pigment Volume Concentration (PVC)
- **Typical range**: 15-80% depending on finish. Gloss paints: 20-35%. Semi-gloss: 35-45%. Eggshell/satin: 45-55%. Flat/matt: 55-70%. Primers: up to 75%.
- **Effect**: primary control of gloss, hiding power, mechanical strength, barrier, cost. Below CPVC -> continuous binder matrix, high gloss, high barrier. Above CPVC -> air voids, low gloss, low barrier, poorer weatherability.
- **Mechanism**: PVC determines whether binder fills interstices between packed pigment particles [LR 1.2].
- **References**: LR 1.2; papers #25.

### 2.2 CPVC (Critical PVC) and PVC/CPVC ratio
- **Typical range**: CPVC itself 30-60%; PVC/CPVC ratio the key dimensionless design parameter (0.3-1.2 typical).
- **Effect**: PVC/CPVC < 1 -> binder-continuous; PVC/CPVC > 1 -> pigment-continuous with air voids. Sharp property transitions near 1.0.
- **Mechanism**: CPVC is the packing density at which binder just fills pigment interstices. Computed from oil absorption values. This is the single most important formulation parameter.
- **References**: LR 1.2.

### 2.3 TiO2 loading
- **Typical range**: 0-30 wt% wet paint; 15-25 vol% dry film typical for white/tinted architectural.
- **Effect**: dominant contributor to hiding power and white colour. Above 15-30% PVC, scattering efficiency per particle drops due to crowding; above 30% PVC further interference makes added TiO2 counterproductive and expensive.
- **Mechanism**: TiO2 (rutile) has RI 2.7; optimal scattering at particle size 200-280 nm; closer than ~one-half-wavelength spacing gives destructive interference.
- **References**: LR 1.1, 1.2; Dow OpTiO2nizer [LR 2.2]; papers #25.

### 2.4 Extender type and loading
- **Options**: calcium carbonate (cheap, easy disperse, low oil absorption), kaolin (hiding extension, hardness, suspension), talc (sheen control, +25% UV durability at 20 wt%), mica (barrier, flake alignment), barytes (density, chemical inertness), silica (matting, scratch).
- **Typical range**: 0-40 wt%.
- **Effect**: reduce cost, tune gloss downward, extend TiO2 hiding, modify rheology, modify weathering.
- **Mechanism**: low-RI particles scatter less than TiO2 but fill volume; anisotropic platelets (talc, mica) align during film formation for barrier and matting.
- **References**: LR 1.1.

### 2.5 Coloured pigment type and concentration
- **Options**: iron oxides (red, yellow, black), phthalocyanines (blue, green), carbon black, organics (azo, quinacridone).
- **Typical range**: 0.1-15 wt%.
- **Effect**: colour, tinting strength, lightfastness.
- **Mechanism**: selective absorption in visible spectrum.
- **References**: LR 1.1.

### 2.6 Pigment particle size distribution
- **Typical range**: primary particle 50-1000 nm; dispersed agglomerates 200-1500 nm.
- **Effect**: controls gloss, hiding power, rheology, and in powder coatings the appearance.
- **Mechanism**: Mie scattering has maximum at ~half-wavelength; dispersion state controls rheology and hiding.
- **References**: LR 1.1; papers #8 (ANN model of PSD -> gloss/roughness).

---

## 3. Solvent / Carrier Variables

### 3.1 Carrier type
- **Options**: water (waterborne), aliphatic hydrocarbons (mineral spirits), aromatic (xylene, toluene), ketones (MEK, MIBK), esters (butyl acetate), alcohols (IPA, n-butanol), glycol ethers, 100% solids (no solvent).
- **Effect**: sets viscosity, drying profile, VOC, odour, substrate compatibility, and pot life for thermosets.
- **Mechanism**: evaporation profile and solvency (via HSP) determine film formation, popping, levelling, sagging.
- **References**: LR 1.1, 1.4, 5.2, 5.3; papers #14, #15.

### 3.2 Solvent / water content (wt%)
- **Typical range**: 0-60 wt% wet paint; low-VOC architectural < 5 wt% organic solvent.
- **Effect**: controls application viscosity, VOC, cost, film thickness per coat.
- **Mechanism**: evaporation raises solids fraction until close-packing then film coalescence.
- **References**: LR 1.4, 5.2.

### 3.3 Solvent blend composition (HSP targeting)
- **Variables**: fractional composition of multiple solvents, optimised to target (dD, dP, dH) matching binder solubility sphere.
- **Effect**: reduces hazardous solvent, controls levelling/evaporation, prevents popping.
- **Mechanism**: Hansen solubility parameters decompose solubility into dispersion, polarity, H-bonding contributions; blends can hit target sphere unreachable by any single solvent.
- **References**: LR 1.1, 5.3; papers #14, #15; open-source HSP Python tool [LR 2.2].

### 3.4 Coalescing aid type and loading
- **Options**: Texanol (2,2,4-trimethyl-1,3-pentanediol monoisobutyrate), dipropylene glycol n-butyl ether, other slow-evaporating ester alcohols.
- **Typical range**: 0-10 wt% of binder (waterborne).
- **Effect**: lowers effective Tg to enable ambient film formation; slowly evaporates to restore hardness.
- **Mechanism**: acts as temporary plasticiser, reduces Tg during particle deformation stage of latex film formation.
- **References**: LR 1.4.

---

## 4. Additives

### 4.1 Wetting / dispersing agents (surfactants)
- **Typical range**: 0.1-2.0 wt% on total formulation.
- **Effect**: stabilise pigment dispersion, prevent flocculation, enable milling efficiency.
- **Mechanism**: adsorb at pigment-liquid interface; provide electrostatic or steric stabilisation.
- **References**: LR 1.1; papers #1.

### 4.2 Rheology modifiers / thickeners
- **Options**: HEUR (hydrophobically modified ethoxylated urethane), HASE (hydrophobically modified alkali soluble emulsion), cellulosics (HEC), fumed silica, organoclay, attapulgite.
- **Typical range**: 0.1-3.0 wt%.
- **Effect**: set low-shear (sag resistance, pigment suspension) and high-shear (brush/spray) viscosity independently.
- **Mechanism**: associative thickeners (HEUR) form transient networks via hydrophobic association; non-associative modifiers raise bulk aqueous viscosity.
- **References**: LR 1.1; papers #2.

### 4.3 Defoamers
- **Options**: silicone, mineral oil, polymer.
- **Typical range**: 0.05-0.5 wt%.
- **Effect**: prevent foam during manufacture and application; side effects include craters, fisheyes if overdosed.
- **Mechanism**: destabilise air bubble films via low-surface-tension spreading droplets.
- **References**: LR 1.1.

### 4.4 UV stabilisers
- **Options**: HALS (hindered amine light stabiliser) and UVA (UV absorber; benzotriazoles, triazines).
- **Typical range**: 0.5-3 wt% of binder.
- **Effect**: prolong weathering life; preserve gloss and colour.
- **Mechanism**: UVA absorb UV before polymer damage; HALS scavenge free radicals formed by photo-oxidation.
- **References**: LR 1.1, 3.3; papers #6.

### 4.5 Biocides / preservatives
- **Typical range**: 0.05-0.5 wt% (in-can) plus optional dry-film biocides.
- **Effect**: prevent spoilage and mould growth.
- **References**: LR 1.1.

### 4.6 Driers / catalysts (alkyds, 2K)
- **Options**: cobalt (surface dry), zirconium (through dry), manganese, calcium driers; tin catalysts for PU.
- **Typical range**: 0.05-0.5 wt% metal on binder solids.
- **Mechanism**: transition metal complexes catalyse autoxidation of unsaturated fatty-acid chains.
- **References**: LR 1.3.

### 4.7 Adhesion promoters
- **Options**: silanes, titanates, phosphated acrylates.
- **Typical range**: 0.1-2 wt%.
- **Mechanism**: form covalent/polar bridges between polymer and substrate.
- **References**: LR 1.1.

### 4.8 Flow / levelling agents
- **Options**: polyacrylate modifiers, fluorosurfactants, silicones.
- **Typical range**: 0.05-1 wt%.
- **Effect**: promote uniform surface, eliminate orange peel. Critical in powder coatings.
- **References**: LR 1.1, 5.2.

### 4.9 Photoinitiators (UV-curable only)
- **Typical range**: 1-20 wt% of reactive fraction.
- **Effect**: controls cure speed, depth of cure, yellowing.
- **Mechanism**: generates radicals or cations on UV absorption to initiate polymerisation.
- **References**: LR 5.2.

---

## 5. Process and Application Variables

### 5.1 Film thickness (dry film thickness, DFT)
- **Typical range**: 15-50 um automotive; 25-100 um architectural; 200-500 um high-build protective.
- **Effect**: barrier performance scales with thickness; stress and cracking increase with thickness; cost and cure time scale linearly.
- **References**: LR 6.1, 6.2; papers #3, #11.

### 5.2 Cure / bake temperature
- **Typical range**: ambient 20-25 C (2K, latex); 60-100 C forced; 125-180 C powder; 140 C 1K automotive bake.
- **Effect**: determines final crosslink density, residual stress, and Tg.
- **References**: LR 5.2, 6.1; papers #11.

### 5.3 Cure time
- **Typical range**: seconds (UV) to 24 h (ambient 2K).
- **References**: LR 1.4.

### 5.4 Number of coats
- **Typical range**: 1-4.
- **Effect**: total DFT, inter-coat adhesion, defect coverage.
- **References**: LR 6.1.

### 5.5 Application method
- **Options**: brush, roller, airless spray, air spray, electrostatic, dip, curtain.
- **Effect**: determines optimal viscosity window and shear rate profile for rheology design.
- **References**: LR 2.2, 6.1.

### 5.6 Substrate temperature and humidity at application
- **Effect**: strongly influences film formation (MFFT constraint), crater/pop formation, and adhesion.
- **References**: LR 1.4.

---

## 6. HDR Variable Summary Table

| Class | Variable | Typical range | HDR treatment |
|---|---|---|---|
| Binder | type | 5-10 categoricals | one-hot / embedding |
| Binder | Tg | -20 to +120 C | continuous |
| Binder | stoichiometric ratio | 0.9-1.2 | continuous |
| Binder | blend fractions | 0-1 (simplex) | mixture |
| Pigment | PVC | 15-75% | continuous |
| Pigment | PVC/CPVC | 0.3-1.2 | derived |
| Pigment | TiO2 loading | 0-30 wt% | continuous |
| Extender | type + loading | 0-40 wt% | mixture |
| Solvent | type | categorical | one-hot / HSP encoding |
| Solvent | content | 0-60 wt% | continuous |
| Solvent | HSP (dD, dP, dH) | derived | 3 continuous |
| Additives | dispersant | 0.1-2 wt% | continuous |
| Additives | thickener | 0.1-3 wt% | continuous |
| Additives | defoamer | 0.05-0.5 wt% | continuous |
| Additives | UV stabiliser | 0.5-3 wt% | continuous |
| Additives | drier / catalyst | 0.05-0.5 wt% | continuous |
| Process | DFT | 15-500 um | continuous |
| Process | cure T | 20-180 C | continuous |
| Process | cure time | s-h | continuous |

Total dimensionality: roughly 15-30 active continuous variables plus 3-5 categorical choices, consistent with literature characterisation of coating formulation as a 10-30 dimensional problem [LR 7.2].

Compositional constraint: all wt% sum to 100, so the active formulation lives on a high-dimensional simplex; HDR search must respect mixture constraints [LR 2.1; papers #25, #26, #27, #28].
