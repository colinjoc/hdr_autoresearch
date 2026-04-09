# Knowledge Base: Paint/Coating Formulation

Established facts, rules, and benchmarks extracted from `literature_review.md` and `papers.csv`. This file is the HDR loop's "prior knowledge" store: facts that should be enforced or respected by predictors and search algorithms, and benchmarks against which new models are compared.

Citations in square brackets: LR X.Y = `literature_review.md` Section X.Y; #N = `papers.csv` row N.

---

## 1. Established Results From the Literature

### 1.1 Composition and Component Roles
- A paint contains four to six component classes: binder, pigment, extender/filler, solvent/carrier, additives, and (in 2K thermosets) a separate crosslinker/hardener [LR 1.1].
- Binder (film-forming polymer) sets adhesion, chemical/UV resistance, flexibility, and hardness; it is the principal determinant of performance class [LR 1.1, 1.3].
- TiO2 (rutile) is the dominant white pigment with RI 2.7; optimal scattering particle size is 200-280 nm [LR 1.1].
- Calcium carbonate is the most common extender: cheap, easily dispersed, low oil absorption [LR 1.1].
- Talc at 20 wt% gives ~25% UV durability improvement [LR 1.1].

### 1.2 Film Formation
- Latex film formation proceeds in four stages: water evaporation, particle packing, particle deformation, coalescence/interdiffusion [LR 1.4; #12].
- Film formation requires ambient temperature above the Minimum Film Formation Temperature (MFFT). Coalescing aids (e.g. Texanol) lower the effective Tg below MFFT and then evaporate to restore hardness [LR 1.4].
- Solventborne film formation is evaporation-controlled at the surface, then diffusion-controlled as the film solidifies [LR 1.4].
- Crosslink density is measured by DMA (rubbery plateau modulus), solvent swelling (Flory-Rehner), or DSC (residual cure enthalpy) [LR 1.4].

### 1.3 Specific Reported Property Improvements
- Epoxy-polyurethane hybrids with 5-15% epoxy content: tensile strength 39.1 -> 86.3 MPa; adhesion 2.5 -> 8.3 MPa; thermal decomposition onset 320 -> 390 C [LR 6.2].
- Zinc-rich primers: 55-85 wt% Zn in dry film; cathodic + barrier protection; graphene/conductive additives can lower Zn loading while maintaining performance [LR 6.2].
- Graphene 0.5 vol% reduces OTR by ~90% [LR 6.3].
- Intumescent-coating expandable graphite loading optimum 5-22 wt% [LR 6.3].
- Antifouling marine coatings: 7-75 wt% Cu2O biocide; emerging biocide-free silicone foul-release alternatives [LR 6.3].
- PDMS brush grafting achieves superhydrophobic surfaces with contact angle hysteresis <1 deg [LR 6.3].

### 1.4 Commercial Tool Benchmarks
- Dow OpTiO2nizer reduces TiO2 usage in formulations (commercial evidence reduction is feasible) [LR 2.2].
- X-Rite Smart Formulation reduces effect paint iterations from 10+ to 2-4, with first-attempt accuracy dE 3.0-3.5 [LR 2.2; PCI Mag 2024].
- Durr spray-booth digital twin reduces test paint runs by >50% [LR 2.2].
- Axalta BioCore (2024): up to 70% bio-renewable content with comparable corrosion resistance [LR 5.2].

---

## 2. The PVC / CPVC Concept

The Pigment Volume Concentration (PVC) and Critical PVC (CPVC) framework is the single most important conceptual tool in formulation [LR 1.2].

### 2.1 Definitions
- **PVC** = V(pigment + extender) / V(pigment + extender + binder) x 100% in the dry film.
- **CPVC** = the PVC at which binder just fills the interstices between close-packed pigment particles. Depends on pigment packing and oil absorption.
- **CPVC range**: 30-60% for most pigment/extender systems.
- CPVC is calculable from oil-absorption values (OA = g oil per 100 g pigment) via standard formulas.

### 2.2 PVC/CPVC Ratio: Governing Rule
- **PVC/CPVC < 1** (binder continuous): void-free film; maximum gloss, barrier, mechanical strength, stain resistance.
- **PVC/CPVC = 1**: phase transition; sharp property changes.
- **PVC/CPVC > 1** (pigment continuous): air voids form; severe drops in gloss, barrier, mechanical strength, weatherability, stain resistance, but increased hiding from void scattering.

### 2.3 Typical PVC by Finish
| Finish | PVC (%) |
|---|---|
| High gloss | 15-25 |
| Semi-gloss | 25-35 |
| Eggshell / satin | 35-45 |
| Low sheen | 45-55 |
| Flat / matte | 55-65 |
| Primer | 45-75 |
| Ceiling paint | 60-75 |

### 2.4 TiO2 Crowding
- Below 15% PVC: TiO2 scattering is linear in concentration.
- 15-30% PVC: scattering efficiency per particle drops from crowding.
- Above 30% PVC: inter-particle interference further reduces scattering; additional TiO2 is counterproductive [LR 1.2; Chemours Ti-Pure].

---

## 3. Standard Formulation Rules

### 3.1 Binder / Pigment Ratio Rules
- For gloss finishes, keep PVC well below CPVC (PVC/CPVC <= 0.6).
- For flat finishes, operate near or slightly above CPVC (PVC/CPVC ~0.95-1.05).
- Maintain binder volume sufficient to fully wet all pigment surfaces; insufficient wetting leads to flocculation and poor rheology.

### 3.2 Binder Tg Rules
- Binder Tg must be below service temperature for flexibility but above 0 C for block resistance in architectural coatings.
- Latex Tg must be below MFFT for film formation. Typical compromise: Tg in 10-25 C range with coalescing aid.
- Fox equation predicts copolymer Tg: 1/Tg_blend = sum(w_i / Tg_i) [LR 1.3].

### 3.3 Stoichiometry Rules (2K Thermosets)
- Epoxy-amine: 1:1 amine-H/epoxide for maximum crosslink density, Tg, and chemical resistance.
- Polyurethane: NCO/OH 1.03-1.06 for high-build coatings; 1.05-1.10 for thin coatings; 5-10% NCO excess is common [LR 1.3].
- Off-stoichiometry: amine excess -> flexibility + blush; epoxy excess -> hydrolysis risk.

### 3.4 Alkyd Oil Length Rules
| Class | Oil content | Use |
|---|---|---|
| Short oil | ~30% | Industrial baking enamel |
| Medium oil | ~50% | Balanced architectural / brush |
| Long oil | ~60% | Flexible trim, slow-dry brushables |

### 3.5 Drier Package for Alkyds
- Cobalt drier: surface (top) dry.
- Zirconium drier: through dry.
- Manganese, calcium: auxiliary [LR 1.3].

### 3.6 Solvent Selection by Hansen Parameters
- Decompose solubility into (dD, dP, dH). Target solvent or blend inside the binder's solubility sphere.
- Blends of two or more solvents can hit targets unreachable by any single solvent [LR 1.1; #14, #15].

### 3.7 Mixture Constraint
- All composition variables must sum to 100%. HDR search must live on the simplex. Use Scheffe polynomial models, D-optimal designs, or log-ratio transforms [LR 2.1; #25, #26, #27, #28].

---

## 4. Additive Synergies and Antagonisms

### 4.1 Known Synergies
- **Talc + UV-stable binder**: 25% UV durability boost at 20 wt% talc [LR 1.1].
- **HALS + UVA**: radical-scavenging + UV-absorbing; complementary mechanisms give multiplicative weathering life extension [LR 1.1].
- **Cobalt + Zirconium drier (alkyd)**: top dry + through dry; always paired in practice [LR 1.3].
- **Kaolin + TiO2**: kaolin spaces TiO2 particles to maintain scattering efficiency at reduced TiO2 loading [LR 1.1; Dow OpTiO2nizer].
- **Epoxy + polyurethane blend**: 5-15% epoxy into PU gives 2.2x tensile and 3.3x adhesion improvement [LR 6.2].
- **Graphene + zinc-rich epoxy**: conductive additive extends percolation, allowing lower Zn loading [LR 6.2].

### 4.2 Known Antagonisms
- **Silicone defoamer + gloss**: overdose creates craters and fisheyes that destroy gloss [LR 1.1].
- **Anionic surfactant + HEUR thickener**: surfactant displaces HEUR hydrophobes, collapsing the thickener's association network [LR 1.1].
- **High PVC + gloss**: gloss decays sharply above 25% PVC and collapses near CPVC [LR 1.2].
- **Amine excess (epoxy)**: flexibility gained at cost of amine blush and water sensitivity [LR 1.3].
- **Excess coalescing aid**: lowers block resistance even after evaporation [LR 1.4].
- **TiO2 > 30% PVC**: interference scattering cancels gains; wasteful [LR 1.2].

---

## 5. Cost and VOC per Ingredient Class

Order-of-magnitude figures intended for relative cost/environmental comparisons in HDR optimisation. These are indicative and should be refined with current supplier data before downstream use.

### 5.1 Raw Material Cost (USD per kg, representative 2024 ranges)
| Class | Cost (USD/kg) | Notes |
|---|---|---|
| TiO2 rutile | 2.50-4.50 | Dominant cost driver in whites |
| Acrylic latex (solid) | 1.50-3.00 | Commodity architectural |
| Alkyd resin (solid) | 1.80-3.50 | Medium oil |
| Epoxy resin (DGEBA) | 3.00-6.00 | BPA-based |
| Aliphatic polyurethane | 6.00-12.00 | Premium, weather-stable |
| Polyester polyol | 2.50-5.00 | |
| CaCO3 extender | 0.10-0.30 | Cheapest filler |
| Kaolin clay | 0.20-0.50 | |
| Talc | 0.25-0.60 | |
| Water | ~0 | |
| Organic solvents (aliphatic) | 0.80-1.50 | |
| Organic solvents (aromatic/ester) | 1.20-2.50 | |
| Dispersants (specialty) | 4-12 | |
| Thickeners (HEUR/HASE) | 4-10 | |
| Defoamers (silicone) | 5-15 | |
| HALS/UVA stabilisers | 15-40 | Use in small quantities |
| Graphene nanoplatelets | 50-500 | Wide spread by quality |

### 5.2 VOC Contribution by Class
| Class | Typical VOC (g/L coating) | Notes |
|---|---|---|
| Waterborne latex | 10-50 | Low; coalescing aid dominates |
| High-solids solventborne alkyd | 250-420 | |
| Conventional solventborne | 400-600 | Being phased out |
| UV-curable | <20 | Near-zero solvent |
| Powder coatings | 0 | Solvent-free |
| 2K high-solids PU | 150-350 | |

EPA and EU regulations set category-specific g/L limits (EU Directive 2004/42/EC for decorative). LEED/WELL/BREEAM certifications impose tighter limits, driving growth of the <$50 g/L segment [LR 5.1].

### 5.3 Global Market Context
- Low-VOC paints and coatings market: USD 27.6 B in 2024, projected USD 40.1 B by 2035 [LR 5.1; MRFR].
- Waterborne basecoats now ~60% of automotive OEM share [LR 5.2].

---

## 6. ML Model Accuracy Benchmarks for Coating Property Prediction

Benchmarks from the literature for common coating property targets. These set the bar that any new HDR model should meet or exceed.

### 6.1 Thickness / Geometry
- **Random Forest, SVR, Extra Trees for LbL thickness** [#3, ACS Omega 2023]: competitive accuracy with 22-23 input features; Extra Trees generally leads.
- **Gradient Boosting / XGBoost for nano-film thickness** [Langmuir 2023]: 99.9% reported accuracy.
- **ANN for coating thickness, hardness, tribological, roughness** [#11]: state-of-the-art review confirms ANN generally competitive but benefits from large datasets.

### 6.2 Appearance
- **ANN for powder-coating gloss and roughness from PSD** [#8, Powder Technology 2025]: ANNs capture non-linear PSD effects.
- **X-Rite Smart Formulation for effect colour dE** [LR 2.2]: first-attempt dE 3.0-3.5; industrial deployment.

### 6.3 Formulation-Level Property Prediction
- **Gaussian Process + BO for lacquer gloss/hardness/flexibility** [#1, Prog. Org. Coat. 2025]: sequential design, explicit uncertainty estimates, interpretable.
- **ML for water-based architectural paint viscosity** [#2, J. Intelligent Mfg 2025]: supervised ML with maximum-dissimilarity sampling for process-quality prediction.
- **RF + gradient boosting for adhesion, corrosion rate, hardness** [#9, PMC 2025]: compositional descriptor inputs; strong baseline for structural coatings.
- **Corrosion coating formula discovery from historic data** [#4, npj Mater. Degrad. 2026]: ML identifies novel anticorrosion formulations from historical databases.
- **Two-stage ML for coating degradation** [#6, npj Mater. Degrad. 2025]: environmental factor + physical property -> corrosion failure prediction.
- **Generative AI for paint formula innovation** [#7, 2024]: historical-data-driven generative models produce new formula candidates.

### 6.4 Characterisation and Automation
- **Deep learning for crosshatch adhesion scoring via segmentation** [#10, JCTR 2021]: automates ASTM D3359 evaluation.
- **ML linking microscopy (SEM/TEM) to coating performance** [#5, MRS Comms 2025]: bridges micro-structure to macro-performance.

### 6.5 Transfer Learning and Generative Models
- **Shotgun transfer learning on materials datasets** [LR 3.4]: outperforms from-scratch models on ~69% of datasets.
- **VAE / GAN / diffusion for inverse design** [LR 3.4, 7.6]: proven in small-molecule and alloy design, open for paint formulation application.

### 6.6 Active Learning / BO
- **BO-based active learning vs grid search** [LR 3.5]: reduces required experiments by 5-10x in materials science.
- **CAMEO autonomous materials exploration at synchrotron** [LR 3.5; Nature Comms 2020]: provides a proven closed-loop template for coating formulation.
- **GP + BO for sol-gel coatings (EMMA)** [#16, Hyndman et al. 2005]: pioneering evolutionary model-based multiresponse approach.

### 6.7 Interpretability Standards
- **SHAP** for feature importance with directionality [LR 3.3].
- **Partial dependence plots** for marginal effects [LR 3.3].
- **Explainable ML** specifically applied to lacquer formulation [#1, Prog. Org. Coat. 2025].

### 6.8 Expected HDR Baselines
Baselines an HDR predictor should match or beat on held-out coating property data:

| Target | Baseline model | Expected metric |
|---|---|---|
| Viscosity | RF / XGBoost | R^2 > 0.85 on in-distribution |
| Gloss (60 deg) | GBR + PVC/CPVC feature | MAE < 5 GU |
| Hardness (Konig) | RF | MAE < 10 s |
| Adhesion (crosshatch class) | RF classifier | accuracy > 80% |
| Thickness | Extra Trees | R^2 > 0.9 |
| Weathering (gloss loss, 1000 h QUV) | GP + transfer learning | MAE < 10% gloss loss |
| Corrosion rate | GBR | R^2 > 0.7 |

---

## 7. Testing Standards Reference (for label generation)

| Property | Standard |
|---|---|
| Adhesion (crosshatch) | ASTM D3359 |
| Adhesion (pull-off) | ASTM D4541 |
| Pencil hardness | ASTM D3363 |
| Pendulum hardness | Konig / Persoz |
| Flexibility | ASTM D522 (mandrel) |
| Impact resistance | ASTM D2794 |
| Gloss | ASTM D523 (20/60/85 deg) |
| Accelerated weathering | ASTM G154 (QUV), G155 (Xenon) |
| Natural weathering | ASTM D1014 |
| Salt spray | ASTM B117 |
| EIS | ISO 16773 |

Accelerated weathering protocols correlate imperfectly with real-world performance; 10-year outdoor studies show variable correlation [LR 6.4; ACA 2020; AMPP 2023]. Any HDR loop predicting long-term durability must account for this uncertainty.

---

## 8. Known Gaps (Knowledge Boundary for HDR)

From LR 7, these are the limits of current formulation knowledge that HDR is expected to address:
1. No large-scale open formulation database exists [LR 7.1].
2. Composition data is compositionally constrained (simplex); standard ML ignores this [LR 7.1].
3. Dimensionality is 10-30 variables with strong interactions; curse of dimensionality bites DOE [LR 7.2].
4. No unified multi-scale model from molecular binder design to macro performance [LR 7.3].
5. Simultaneous performance/cost/environmental optimisation is rarely formalised [LR 7.4].
6. Accelerated -> real-world lifetime prediction is a century-old unsolved problem [LR 7.5].
7. Generative inverse design is proven elsewhere but unapplied to paint formulation [LR 7.6].
8. Physics-informed ML priors (PVC/CPVC, stoichiometry) are underused [LR 7.7].

The HDR loop should explicitly target gaps 2, 4, 5, 7, and 8 as scientific contributions.
