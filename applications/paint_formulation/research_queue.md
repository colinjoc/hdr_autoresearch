# Research Queue: Paint/Coating Formulation HDR

HDR hypotheses for the paint formulation project. Phase A = predictor-model hypotheses (which features matter, how well we can predict). Phase B = discovery hypotheses (search for formulations that dominate the Pareto front of performance/cost/sustainability).

Format per item:
- **Impact**: expected scientific/practical value (low / medium / high)
- **Hypothesis**: falsifiable statement
- **Mechanism**: why we expect it
- **Reference**: pointer to `literature_review.md` section (LR X.Y) or `papers.csv` entry (#N)

Status tags: [OPEN] not started, [ACTIVE] in progress, [DONE] concluded, [DROP] falsified or retired.

---

## Phase A: Predictor Model Hypotheses

### H1 - PVC/CPVC dominates gloss prediction [OPEN]
- **Impact**: high
- **Hypothesis**: In a gradient-boosted regression model for 60-deg gloss trained on >500 waterborne latex formulations, the single feature `PVC/CPVC` will carry at least 40% of mean absolute SHAP value, exceeding the next-most-important feature by >2x.
- **Mechanism**: Below CPVC the matrix is continuous and gloss is near-constant; at PVC/CPVC = 1 there is a sharp drop as air voids form. PVC/CPVC captures this transition while absolute PVC does not.
- **Reference**: LR 1.2; papers #1, #9.

### H2 - Binder Tg is the top predictor of block resistance [OPEN]
- **Impact**: medium
- **Hypothesis**: Binder Tg (continuous) will be the top-ranked feature by permutation importance for block resistance in architectural waterborne paints, dominating coalescing aid loading and PVC.
- **Mechanism**: Block resistance is controlled by film hardness at service temperature; Fox equation ties binder composition to Tg directly.
- **Reference**: LR 1.3; papers #1, #11.

### H3 - Additive main effects explain <30% of variance vs interactions [OPEN]
- **Impact**: high
- **Hypothesis**: A model with only linear additive main effects will achieve <60% of the R^2 of a model that includes pairwise interactions (surfactant x thickener, dispersant x defoamer) on a held-out test set of viscosity/gloss data.
- **Mechanism**: Additives strongly interact (surfactant destabilises defoamer; dispersant competes with thickener for surface). Literature explicitly warns of interaction effects.
- **Reference**: LR 2.1 (DOE discussion of interactions); LR 7.2; papers #23, #24, #25.

### H4 - Hansen-parameter features outperform raw solvent one-hot for film-formation prediction [OPEN]
- **Impact**: medium
- **Hypothesis**: For a crater/popping incidence classifier on solvent-borne coatings, using (dD, dP, dH) plus evaporation rate will yield higher AUC than a one-hot solvent encoding of the same data.
- **Mechanism**: HSP coordinates linearly interpolate in solvent blends while one-hot encoding cannot generalise to unseen blends.
- **Reference**: LR 1.1, 5.3; papers #14, #15.

### H5 - Random forest beats DNN on small-data coating property prediction [OPEN]
- **Impact**: medium
- **Hypothesis**: On a dataset of <1000 formulations, random forest/ExtraTrees will match or exceed the RMSE of a tuned MLP for hardness, adhesion, and gloss, consistent with the ACS Omega benchmark.
- **Mechanism**: Tree ensembles are robust to small, noisy, tabular data. DNNs need more samples to outperform.
- **Reference**: papers #3, #9, #11.

### H6 - Gaussian Process uncertainty correlates with true prediction error [OPEN]
- **Impact**: high
- **Hypothesis**: On held-out formulations, GP posterior standard deviation will correlate (Spearman rho > 0.5) with absolute residual, validating its use as an acquisition signal for Bayesian optimisation.
- **Mechanism**: Well-calibrated GPs provide meaningful uncertainty; this is a prerequisite for active learning.
- **Reference**: LR 3.5; papers #1, #29.

### H7 - Transfer learning from abundant viscosity data boosts sparse weathering prediction [OPEN]
- **Impact**: high
- **Hypothesis**: Pretraining a feature encoder on a large viscosity dataset and fine-tuning on a 100-point weathering dataset will reduce test RMSE by at least 20% vs training from scratch on weathering alone.
- **Mechanism**: Viscosity is cheap and abundant; weathering is expensive and scarce. Shared features (binder chemistry, pigment loading) support transfer. Literature reports ~69% success rate of shotgun transfer.
- **Reference**: LR 3.4; papers #6.

### H8 - Graph neural network on monomer graph predicts binder Tg within 5 C [OPEN]
- **Impact**: medium
- **Hypothesis**: A message-passing GNN trained on (monomer, weight fraction) -> measured Tg will predict held-out copolymer Tg with MAE < 5 C, beating the Fox equation.
- **Mechanism**: Fox equation assumes additivity; GNN captures non-ideal copolymerisation and sequence effects.
- **Reference**: LR 3.4.

### H9 - Ternary mixture experiments along the Scheffe simplex are most information-efficient for blend optimisation [OPEN]
- **Impact**: medium
- **Hypothesis**: For a 3-binder blend system, a D-optimal Scheffe design of 10 points will yield a lower posterior mean squared error than 20 random mixtures when modelling the quadratic blend surface.
- **Mechanism**: D-optimal designs minimise the volume of the parameter covariance ellipsoid.
- **Reference**: LR 2.1; papers #25, #26, #27, #28.

### H10 - Physics-informed PVC/CPVC prior improves extrapolation to untested loadings [OPEN]
- **Impact**: high
- **Hypothesis**: A hybrid model with hard-coded PVC/CPVC sigmoid transition plus residual ML term will extrapolate to out-of-range PVC values with at least 30% lower RMSE than a pure ML model trained on the same data.
- **Mechanism**: Physics priors constrain ML where data is sparse. CPVC-based feature engineering encodes the known phase transition.
- **Reference**: LR 1.2, 7.7; papers #22.

### H11 - Active learning selects more informative experiments than Latin hypercube [OPEN]
- **Impact**: high
- **Hypothesis**: In a simulated coating formulation problem with 20 variables, Gaussian-process-based active learning will reach a target predictive RMSE using at least 5x fewer experiments than Latin hypercube sampling.
- **Mechanism**: BO's expected improvement targets informative regions; LHS covers space uniformly but wastes budget on low-value points. Literature reports 5-10x reductions.
- **Reference**: LR 3.5; papers #29.

---

## Phase B: Discovery Hypotheses

### H12 - Ternary acrylic / alkyd / polyurethane blends produce Pareto improvements [OPEN]
- **Impact**: high
- **Hypothesis**: Constrained Bayesian optimisation over ternary binder blends (acrylic, alkyd, PU) will discover formulations that dominate every single-binder baseline on the (gloss, adhesion, cost) Pareto front by at least 10% hypervolume.
- **Mechanism**: Epoxy-PU hybrids already show strong synergies (39 to 86 MPa tensile, 2.5 to 8.3 MPa adhesion). Acrylic/alkyd/PU is expected to span gloss, autoxidative cure, and mechanical domains.
- **Reference**: LR 6.2; papers #4, #9, #18.

### H13 - A low-VOC waterborne formulation can match solvent-borne benchmark within 5% on gloss, adhesion, hardness [OPEN]
- **Impact**: high
- **Hypothesis**: There exists an additive-optimised, coalescing-aid-tuned waterborne acrylic formulation with total VOC < 50 g/L that matches a representative solvent-borne alkyd benchmark on (60-deg gloss, crosshatch rating, pendulum hardness) to within 5%.
- **Mechanism**: Modern latex chemistry (core-shell, high-Tg, coalescing-aid reduction) has closed most of the gap; HDR search in the additive corner of the simplex may finish it.
- **Reference**: LR 5.1, 5.2; papers #13.

### H14 - TiO2 can be reduced by at least 15% without hiding loss via extender optimisation [OPEN]
- **Impact**: high
- **Hypothesis**: Reformulating a commercial white architectural paint with optimised extender type + PSD (kaolin + calcined clay + talc combination) will reduce TiO2 loading by >=15 wt% while maintaining contrast ratio >= 0.97 at 8 mil wet application.
- **Mechanism**: Above 15-30% PVC, extra TiO2 has diminishing returns. Light scattering can be extended by spacing pigment with void-creating extenders. Dow's OpTiO2nizer already proves commercial feasibility.
- **Reference**: LR 1.2, 2.2; papers #1.

### H15 - Multi-objective NSGA-II finds formulations dominating EMMA on the cost-gloss-hardness front [OPEN]
- **Impact**: medium
- **Hypothesis**: NSGA-II coupled with an ensemble surrogate will produce a Pareto set that strictly dominates the EMMA single-response optimiser on at least 70% of reference target profiles in a sol-gel coating benchmark.
- **Mechanism**: NSGA-II explores the full Pareto front; EMMA optimises scalarised objectives and may miss trade-off regions.
- **Reference**: LR 2.3, 4.1; papers #16, #17, #18.

### H16 - Bio-based alkyds at 50% oil can match petroleum alkyd gloss retention [OPEN]
- **Impact**: medium
- **Hypothesis**: A formulation search over soybean/linseed/tung oil fractions plus drier package can find a 50% oil-length bio-alkyd whose gloss retention after 1000 h QUV is within 10% of an iso-property petroleum reference.
- **Mechanism**: Degree of unsaturation (iodine value) and drier catalysis dictate film performance; these are tunable.
- **Reference**: LR 1.3, 5.2.

### H17 - 2K polyurethane stoichiometry has a secondary optimum above 1.10 NCO/OH [OPEN]
- **Impact**: medium
- **Hypothesis**: Scanning NCO/OH from 0.95 to 1.20 will reveal a second performance maximum in (chemical resistance, Tg) above 1.10, distinct from the primary 1.00 optimum, for high-build aliphatic PU.
- **Mechanism**: Excess NCO reacts with moisture to form allophanate/biuret, creating additional crosslinks that may outperform stoichiometric balance in humid cure.
- **Reference**: LR 1.3; papers #14.

### H18 - There exists a surfactant-thickener pair with anti-synergy that should be excluded from formulation space [OPEN]
- **Impact**: medium
- **Hypothesis**: HDR search will identify at least one (anionic surfactant x HEUR) combination whose measured Stormer viscosity drops >30% below the linear sum of single-additive effects, indicating specific exclusion rules.
- **Mechanism**: Anionic surfactants can displace HEUR hydrophobes from association junctions, destroying the rheological network.
- **Reference**: LR 1.1; papers #2.

### H19 - Cost-constrained BO finds formulations within 2% of unconstrained optimum at 60% of the ingredient cost [OPEN]
- **Impact**: high
- **Hypothesis**: Adding a raw-material cost constraint (<=0.6x of baseline) to multi-objective BO will yield formulations whose predicted gloss, hardness, and adhesion drop <2% vs the unconstrained optimum.
- **Mechanism**: Cheap extenders and lower-cost alkyd fractions can substitute for premium PU/acrylic at low performance penalty near the Pareto knee.
- **Reference**: LR 4.1; papers #20, #21, #22.

### H20 - Inverse-design VAE generates novel formulations matching target property vector within experimental noise [OPEN]
- **Impact**: high
- **Hypothesis**: A conditional VAE trained on a labelled formulation dataset will generate, for a held-out target property vector (gloss, hardness, adhesion, VOC), candidate formulations whose forward-predicted properties lie within 1-sigma measurement noise of the target, at a rate >30%.
- **Mechanism**: Continuous latent space interpolation enables efficient coverage of constrained composition space.
- **Reference**: LR 3.4, 7.6; papers #7.

### H21 - Graphene additive at 0.5 vol% halves moisture permeability without affecting gloss [OPEN]
- **Impact**: medium
- **Hypothesis**: Adding 0.5 vol% graphene nanoplatelets to a benchmark waterborne acrylic will reduce moisture vapour transmission rate by >=50% while changing 60-deg gloss by <5 units.
- **Mechanism**: Platelet barrier additives produce tortuous diffusion paths; literature reports ~90% OTR reduction at 0.5 vol%.
- **Reference**: LR 6.3.

### H22 - Zinc-rich primer performance can be maintained with 40% reduced zinc via conductive-additive replacement [OPEN]
- **Impact**: high
- **Hypothesis**: Replacing up to 40% of zinc in a 70 wt% zinc-rich epoxy primer with graphene or carbon black while maintaining an electrically percolating network will preserve salt-spray performance (>1000 h, ASTM B117) within 10% of the unmodified baseline.
- **Mechanism**: Conductive additives extend the percolation network so cathodic protection holds at lower Zn loading, while cost and weight drop.
- **Reference**: LR 6.2.

### H23 - Intumescent-coating formulation has a clear interior optimum in graphite loading [OPEN]
- **Impact**: medium
- **Hypothesis**: Multi-objective BO over (APP, pentaerythritol, melamine, expandable graphite) proportions will locate a graphite fraction in the 10-15% band where char expansion factor is maximised, resolving the 5-22% literature range.
- **Mechanism**: Too little graphite underexpands; too much disrupts the intumescent char structure.
- **Reference**: LR 6.3.

### H24 - Powder-coating cure temperature can drop from 160 to 130 C via photoinitiator-assisted hybrid system [OPEN]
- **Impact**: medium
- **Hypothesis**: Incorporating a dual-cure (thermal + UV) resin system in a powder formulation will enable full cure at 130 C (vs conventional 160 C) while maintaining pencil hardness >= 2H and crosshatch rating = 0.
- **Mechanism**: UV radicals initiate crosslinking before full melt flow, reducing the thermal activation needed.
- **Reference**: LR 5.2.

### H25 - Multi-fidelity BO with cheap rheology screening accelerates weathering-optimal discovery [OPEN]
- **Impact**: high
- **Hypothesis**: A multi-fidelity BO using viscosity and rub-off (cheap, same-day) to pre-screen candidates before sending to QUV will reach a specified weathering target in 40% fewer expensive weathering runs than single-fidelity BO.
- **Mechanism**: Cheap surrogates eliminate clearly bad formulations before the expensive step.
- **Reference**: LR 3.5; papers #29.

### H26 - Sustainability-weighted Pareto front reveals a "knee" with minimal performance loss at 50% bio-content [OPEN]
- **Impact**: medium
- **Hypothesis**: Scanning bio-renewable fraction from 0 to 100% while optimising all other variables, there exists a knee at 40-60% bio-content beyond which performance degrades sharply, matching the Axalta BioCore 70% figure.
- **Mechanism**: Low bio-content substitutes freely; high bio-content forces use of problematic monomers.
- **Reference**: LR 5.2.

---

## Prioritisation

Recommended Phase A order: **H1, H6, H11, H3, H10** (validate core predictor and active learning loop first).

Recommended Phase B order: **H14, H13, H19, H12, H20** (target highest-impact commercial discoveries once Phase A predictor and acquisition pipeline are validated).
