# Literature Review: Concrete Mix Design Optimisation via ML and HDR

## 1. Concrete Science Fundamentals

### 1.1 Portland Cement Chemistry and Hydration

Portland cement is composed of four principal clinker phases: tricalcium silicate (C3S, ~50-70%), dicalcium silicate (C2S, ~15-30%), tricalcium aluminate (C3A, ~5-10%), and tetracalcium aluminoferrite (C4AF, ~5-15%). Upon contact with water, these phases undergo hydration reactions that produce the binding phases responsible for concrete strength (Mehta & Monteiro, 2014; Neville, 2011).

The primary hydration reactions are:

- **C3S hydration**: 2C3S + 6H -> C3S2H3 (C-S-H) + 3CH. C3S hydrates rapidly and is responsible for early strength gain (1-28 days). It liberates more portlandite (CH) than C2S because it is richer in lime.
- **C2S hydration**: 2C2S + 4H -> C3S2H3 (C-S-H) + CH. C2S hydrates more slowly and contributes primarily to long-term strength (beyond 28 days).
- **C3A hydration**: C3A + 3CSH2 + 26H -> C6AS3H32 (ettringite). This reaction is rapid and exothermic; gypsum is added to control it.

The principal hydration products are: C-S-H (50-70% by volume, the primary strength-building phase), CH/portlandite (20-25%, no strength contribution, susceptible to chemical attack), and ettringite (10-15%) (Mindess, Young & Darwin, 2003). The C-S-H gel is the "glue" that binds concrete together, and its formation is the fundamental mechanism of strength development.

### 1.2 The Water-Cement Ratio: Abrams' Law

In 1918, Duff Abrams published the most important empirical relationship in concrete science: compressive strength is inversely proportional to the water-cement ratio (w/c) (Abrams, 1918). The mathematical expression is:

    fc = A / B^(w/c)

where A and B are empirical constants depending on cement type, age, and curing conditions. For OPC at 28 days, A ~ 96 MPa and B ~ 8. Between 1913 and 1918, Abrams conducted thousands of systematic experiments varying w/c, aggregate type, cement type, and curing conditions. This transformed concrete design from an art into a science.

Abrams' law holds well for conventional concrete with w/c ratios between 0.3 and 0.8. Its limitations include: (1) it does not account for the effect of supplementary cementitious materials (SCMs), (2) it assumes full hydration which may not occur at very low w/c ratios, (3) it does not capture the effect of superplasticizers that allow low w/c without compromising workability, and (4) it applies primarily to 28-day strength (Neville, 2011).

### 1.3 Gel-Space Ratio Theory

Powers and Brownyard (1946-1947) extended Abrams' work by developing the gel-space ratio theory, which relates strength to the ratio of hydrated cement gel volume to the total space available (gel + capillary pores). Powers (1958) found that this approach predicted strength independently of mix proportions and age, providing a more fundamental relationship. The two types of pores in hardened cement paste (capillary pores between cement gel masses, and gel pores within the gel itself) are critical determinants of strength, permeability, and durability (Powers, 1958; Mindess et al., 2003).

### 1.4 Pozzolanic Reactions and SCMs

Pozzolanic materials contain amorphous silica (and alumina) that reacts with the calcium hydroxide (CH) produced during cement hydration to form additional C-S-H gel. This reaction: (1) converts a non-strength-contributing phase (CH) into the primary binding phase (C-S-H), (2) refines the pore structure by filling capillary pores, (3) improves the interfacial transition zone (ITZ) between paste and aggregates, and (4) enhances long-term durability against chemical attack (Mehta & Monteiro, 2014).

Replacing 25% of cement with a pozzolan reduces CH formation by dilution, and the pozzolan reacts with remaining CH to form additional C-S-H binder, effectively converting waste into strength.

### 1.5 Strength Development Over Time

Concrete reaches approximately 30-40% of 28-day strength by day 3, 65-75% by day 7, and 85-90% by day 14. The 28-day strength is the standard benchmark because 95-99% of ultimate strength is achieved by this point under standard curing. Beyond 28 days, strength continues to gain at 1-2% per week under ideal conditions.

Mixes containing SCMs (fly ash, slag) develop strength more slowly in the first 1-2 weeks but continue gaining strength meaningfully past 28 days, which is why engineers sometimes specify 56-day or 90-day strength instead. Air-drying concrete can reduce compressive strength by 28-40% compared to continuously moist-cured concrete (Neville, 2011).

---

## 2. Mix Design Methods

### 2.1 ACI 211 Method

The ACI 211.1 "Standard Practice for Selecting Proportions for Normal, Heavyweight, and Mass Concrete" is the most widely used mix design method, particularly in North America. The method is based on estimating the weight of concrete per unit volume while considering consistency/workability (slump), strength, durability, and economy.

The procedure involves: (1) selecting the target slump based on application, (2) selecting maximum aggregate size, (3) estimating water content and air content, (4) determining w/c ratio from target strength, (5) calculating cement content, (6) estimating coarse aggregate content based on fineness modulus, (7) estimating fine aggregate content by difference. The method relies on standard tables derived from extensive empirical research (ACI Committee 211, 2022).

### 2.2 British DOE Method

The British Department of Environment method, now part of BRE (Building Research Establishment), takes a similar approach but with different empirical relationships calibrated to UK materials and conditions. It requires: target mean strength, free w/c ratio, water content estimation, cement content calculation, and aggregate proportioning. The DOE method is considered more cumbersome to apply than ACI 211 but produces similar results (Neville, 2011).

### 2.3 Dreux-Gorisse Method

The Dreux-Gorisse method, originating from France, combines graphical and analytical approaches with correction tables. It optimises the aggregate grading curve using a "reference curve" approach, which can produce better-packed aggregates than the ACI method. The method considers: target strength, aggregate characteristics, cement type, workability, and exposure conditions (Dreux & Festa, 1998).

### 2.4 Limitations of Traditional Methods

All traditional methods share common limitations: (1) they are based on empirical relationships from specific materials and conditions that may not generalise, (2) they are primarily designed for OPC concrete and do not handle complex binder systems well, (3) they typically optimise for one property (usually strength) at a time, (4) they do not directly consider CO2 emissions or cost optimisation, and (5) they require iterative trial batching to refine proportions (Mehta & Monteiro, 2014). These limitations motivate the use of ML-based approaches for modern concrete design.

---

## 3. ML for Concrete Strength Prediction

### 3.1 The UCI Concrete Dataset

The foundational dataset for ML concrete research was created by I-Cheng Yeh in 1998 and published alongside his seminal paper "Modeling of strength of high performance concrete using artificial neural networks" (Cement and Concrete Research, Vol. 28, No. 12, pp. 1797-1808). The dataset contains 1,030 samples with 8 input features (cement, blast furnace slag, fly ash, water, superplasticizer, coarse aggregate, fine aggregate, age in days) and one output (compressive strength in MPa). All component features are in kg/m3 except age (days 1-365) and strength (MPa). The dataset is available from the UCI Machine Learning Repository (DOI: 10.24432/C5PK67) under CC BY 4.0 licence (Yeh, 1998).

### 3.2 Model Performance Benchmarks

Performance on the UCI dataset has evolved significantly:

| Model | R2 | RMSE (MPa) | MAE (MPa) | Source |
|-------|-----|-----------|-----------|--------|
| ANN (Yeh, 1998) | ~0.80 | ~6.5 | - | Yeh (1998) |
| SVR | ~0.85 | ~5.5 | - | Various |
| Random Forest | ~0.88 | ~4.8 | - | Various |
| XGBoost | ~0.91-0.92 | ~4.0-4.4 | ~2.8 | Multiple (2020-2024) |
| CatBoost | ~0.92-0.94 | ~2.7-3.5 | - | Multiple (2023-2025) |
| LightGBM | ~0.93-0.96 | ~2.4-3.3 | ~2.4 | Multiple (2023-2025) |
| Hybrid PCA-RFR-SVR-CNN | ~0.95-0.96 | ~2.0-3.5 | - | 2024-2025 |
| Ensemble (stacking) | ~0.95-0.96 | ~2.0-3.0 | - | 2024-2025 |
| Transformer-based | ~0.95+ | - | ~2.5% error | 2025-2026 |

The current SOTA on UCI-like datasets clusters around R2 = 0.93-0.96, RMSE = 2.0-3.5 MPa. Gradient-boosted decision tree models (CatBoost, XGBoost, LightGBM) consistently outperform traditional ML and basic neural networks. The model ranking order is approximately: CatBoost >= LightGBM > XGBoost > RF > SVR > ANN > KNN > linear models (Nguyen et al., 2024; Abuodeh et al., 2020; Gomaa et al., 2024).

### 3.3 Larger Datasets

Beyond UCI:
- **ConcreteXAI** (Guzman-Torres et al., 2024): 18,480 data points from a 10-year laboratory investigation, covering 12 distinct concrete formulations including compressive (4,420 samples), tensile (3,460), and flexural (1,760) strength plus non-destructive test measurements. Available on GitHub.
- **FHWA LTPP ARMAD**: The Long-Term Pavement Performance database contains concrete strength, modulus, and durability data from thousands of pavement sections across the US. The Analysis-Ready Materials Dataset (ARMAD) was released in SDR 36 (2022).
- **Industry-scale datasets**: A 2025 study leveraged approximately 70,000 compressive strength test records, demonstrating that embedding-based neural networks achieve a mean 28-day prediction error of approximately 2.5% at industry scale (Mohanty et al., 2025).

### 3.4 Deep Learning and Transformer Approaches

Recent advances include:
- **CNN-LSTM with attention mechanisms**: Combining CNNs for local feature extraction with LSTMs for temporal strength evolution during curing, improved by 15% over baselines (2025).
- **Swin Transformer**: Achieved >95% accuracy in compressive strength prediction by capturing long-range dependencies in mix design data (2025).
- **Hybrid CNN-Transformer**: Combining convolutional layers for local features with self-attention mechanisms for global dependencies (2025).
- **Large Language Models**: Recent work (2026) explores using optimised deep learning and LLMs for concrete strength prediction.
- **Embedding-based neural networks**: At industry scale (~70k samples), consistently outperform traditional ML and transformer approaches (Mohanty et al., 2025).

### 3.5 Explainable AI (XAI) for Concrete

SHAP (SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic Explanations) have been widely applied to interpret concrete prediction models:
- **SHAP feature importance ranking** (typical): cement > age > water > superplasticizer > fly ash > slag > coarse aggregate > fine aggregate (multiple studies, 2023-2025).
- Cement exhibits the highest mean SHAP value (~7.5), confirming its dominant influence.
- Water-to-binder ratio (W/B) shows a SHAP value of ~7.7, emphasising its pivotal role.
- Superplasticizer has a positive SHAP value (~1.1), reflecting its constructive influence through water reduction.
- SHAP interaction plots reveal non-trivial interactions, particularly between cement content and water, and between age and SCM content (Aldoseri et al., 2023; Gomaa et al., 2024).

### 3.6 Symbolic Regression

Symbolic regression discovers explicit mathematical equations from data, offering interpretability advantages over black-box ML models. Applied to concrete, SR models achieve R2 ~ 0.86-0.91 with transparent equations that align with known physics (e.g., strength decreasing with w/c ratio). While accuracy slightly lags behind gradient-boosted trees, the interpretability is crucial for engineering adoption and scientific discovery (2024-2025).

---

## 4. Feature Engineering for Concrete

### 4.1 Raw Features (UCI Dataset)

The 8 raw features in the UCI dataset are: cement (kg/m3), blast furnace slag (kg/m3), fly ash (kg/m3), water (kg/m3), superplasticizer (kg/m3), coarse aggregate (kg/m3), fine aggregate (kg/m3), and age (days).

### 4.2 Physics-Informed Derived Features

Extensive research and domain knowledge suggest the following derived features substantially improve prediction:

1. **Water-cement ratio (w/c)**: water / cement. The fundamental Abrams' law parameter. Monotonically inversely related to strength.
2. **Water-binder ratio (w/b)**: water / (cement + slag + fly_ash). More appropriate when SCMs are present. SHAP value ~7.7, among the most important features.
3. **SCM replacement percentage**: (slag + fly_ash) / (cement + slag + fly_ash) * 100. Captures the degree of cement replacement.
4. **Aggregate-cement ratio**: (coarse_agg + fine_agg) / cement. Relates to paste volume fraction.
5. **Fine-to-total aggregate ratio (sand ratio)**: fine_agg / (coarse_agg + fine_agg). Affects workability and packing density.
6. **Superplasticizer per binder**: superplasticizer / (cement + slag + fly_ash). Dosage relative to total binder.
7. **Paste volume fraction**: (cement/3.15 + slag/2.9 + fly_ash/2.2 + water + superplasticizer) / total_volume.
8. **Total binder content**: cement + slag + fly_ash.
9. **Log(age)**: Captures the diminishing returns of strength gain with time.

### 4.3 Feature Importance and Interactions

From SHAP analysis across multiple studies (2023-2025):
- Cement-to-water ratio (C/W) and water-to-binder ratio (W/B) are consistently the most important features for strength prediction.
- Age is the second or third most important feature, with log-transformation improving model fit.
- Superplasticizer dosage has a positive but non-linear effect on strength (indirect through reduced w/c).
- Feature interactions are critical: cement x water, age x SCM content, superplasticizer x water all show significant SHAP interaction effects.
- Monotonicity constraints (strength non-increasing with w/b, non-decreasing with age) from physics improve model robustness and generalisation (Li et al., 2024).

### 4.4 Physics-Informed Feature Constraints

Recent work on physics-informed ML for concrete (2024-2025) incorporates:
- **Monotonicity constraints**: Strength should decrease with increasing w/c or w/b ratio (for fixed binder), and increase with age. These can be enforced as soft penalties in loss functions or hard constraints in gradient-boosted trees.
- **Mass conservation**: Total volume of all components should sum to approximately 1 m3 (with air content).
- **Domain knowledge regularisation**: Using output or intermediate variables from empirical/physical models as constraints, reducing data requirements and improving out-of-distribution generalisation.
- **Physics-informed GANs**: Physics-Informed Conditional Tabular GANs (PI-CTGANs) incorporate domain constraints directly into the generator's loss function to produce physically plausible synthetic mixtures.

---

## 5. Multi-Objective Optimisation of Concrete

### 5.1 The Three-Objective Problem

Practical concrete design involves at least three competing objectives:
1. **Maximise compressive strength** (or meet a minimum strength class, e.g., C30 = 30 MPa)
2. **Minimise cost** (cement is the most expensive ingredient by far)
3. **Minimise CO2 emissions** (cement accounts for 75-90% of concrete's embodied carbon)

Additional objectives sometimes considered: durability (chloride resistance, carbonation resistance), workability (slump), shrinkage, heat of hydration.

### 5.2 CO2 Emissions by Ingredient

| Ingredient | CO2 (kg CO2e/kg) | Typical range |
|------------|-------------------|---------------|
| Portland cement (OPC) | 0.82 - 1.00 | ~0.90 |
| Ground granulated blast furnace slag (GGBS) | 0.05 - 0.15 | ~0.07 |
| Fly ash (Class F/C) | 0.00 - 0.03 | ~0.01 |
| Silica fume | 0.01 - 0.03 | ~0.02 |
| Coarse aggregate | 0.005 - 0.02 | ~0.01 |
| Fine aggregate (sand) | 0.005 - 0.02 | ~0.01 |
| Water | ~0.001 | negligible |
| Superplasticizer | 0.2 - 0.7 | ~0.5 |

Cement dominates: it makes up ~10% of concrete by volume but accounts for 75-90% of embodied carbon. Replacing cement with SCMs is therefore the single most impactful lever for reducing concrete's carbon footprint.

### 5.3 Cost by Ingredient

Approximate costs (USD/ton, 2024 values, region-dependent):

| Ingredient | USD/ton (approx.) |
|------------|--------------------|
| Portland cement | 120 - 180 |
| GGBS | 80 - 150 |
| Fly ash | 30 - 130 |
| Silica fume | 300 - 700 |
| Coarse aggregate | 10 - 30 |
| Fine aggregate | 10 - 25 |
| Water | ~0.5 |
| Superplasticizer | 1,500 - 4,000 |

Cement is the costliest ingredient per ton among the bulk materials. Fly ash and slag are generally cheaper than cement, providing both cost and CO2 advantages. Silica fume and superplasticizer are expensive per kg but used in small quantities.

### 5.4 Optimisation Methods

**NSGA-II (Non-dominated Sorting Genetic Algorithm II)**: The most widely used algorithm for multi-objective concrete optimisation. Known for good convergence, global optimisation ability, short computation time, and strong scalability. Applied in concrete mix design with 2-4 objectives (strength, cost, CO2, durability). Representative results include optimal C50 mixes with cement reduced to 331 kg/m3 by incorporating fly ash, achieving strength requirements while minimising CO2 (multiple studies, 2024-2025).

**MOPSO (Multi-Objective Particle Swarm Optimisation)**: Found multiple optimal solutions simultaneously optimising strength maximisation, cost minimisation, and cement reduction. Optimised mixes surpassed 50 MPa with cement reduction up to 25%, leading to 15% total cost reduction.

**Bayesian Optimisation**: BOxCrete (Meta/Facebook Research, 2025-2026) uses Gaussian Process regression for probabilistic strength prediction coupled with BoTorch for multi-objective Bayesian optimisation. Achieved R2 = 0.94 on 500+ strength measurements. Open-source under MIT licence.

**TOPSIS**: Used for decision-making among Pareto-optimal solutions, selecting the solution closest to the ideal point and farthest from the anti-ideal point.

### 5.5 Pareto Frontiers

GreenMix-Pareto (2026) represents the state-of-the-art, combining physics-guided multi-task learning with monotonicity constraints, conformal calibration for uncertainty quantification, feasibility screening, and hybrid EHVI + NSGA-II optimisation. On the UCI-like 1000-mix dataset, it achieved:
- Strength prediction: RMSE = 0.58 MPa, R2 = 0.997
- Representative knee solution: ~50 MPa strength with ~220 kg CO2 and ~1159 MJ per m3

Quaternary-blended systems have produced Pareto-optimal mixes achieving 51-80 MPa with approximately 62% less cement than conventional designs (2025).

---

## 6. Inverse Design and Generative Approaches

### 6.1 The Inverse Design Problem

Traditional ML predicts strength from mix proportions (forward model). Inverse design asks: given a target strength (and cost/CO2 constraints), what are the optimal mix proportions? This is inherently more challenging because: (1) the mapping is one-to-many (multiple mixes can achieve the same strength), (2) the design space is high-dimensional (8+ continuous variables), (3) constraints must be satisfied (physical feasibility, workability, durability).

### 6.2 Evolutionary/Optimisation-Based Approaches

The most common approach trains a forward prediction model (e.g., XGBoost) then uses it as a fitness function within an evolutionary algorithm (NSGA-II, GA, PSO) to search the mix design space. This approach is well-established but suffers from: slow convergence in high dimensions, no guarantee of global optimality, and difficulty handling complex constraints.

### 6.3 Bayesian Optimisation

BOxCrete (Meta, 2025-2026) and related frameworks use Gaussian Process surrogates for uncertainty-aware inverse design. Key advantages: (1) uncertainty quantification enables confidence-aware recommendations, (2) acquisition functions (Expected Hypervolume Improvement) balance exploration and exploitation, (3) natural integration with active learning loops where AI suggests mixes and labs test them. Meta demonstrated 50% OPC reduction while maintaining target strength >= 40 MPa, with 10x faster design optimisation cycle.

### 6.4 Generative Models

**VAE-based generation**: A Variational Autoencoder transforms the high-dimensional mix design space into a 2D latent space, where sampling and optimisation are simpler. VAE-generated synthetic datasets (10,000 samples) outperformed GAN-generated data in quality metrics (entropy, KL divergence, FID) (2024-2025).

**Physics-Informed CTGAN**: PI-CTGANs incorporate domain constraints (mass conservation, w/c bounds, mix feasibility) directly into the generator's loss function, producing physically plausible synthetic mixtures for data augmentation.

**Cooperative Neural Networks (CoNN)**: A framework for partial inverse design that reformulates the problem as constraint-aware imputation. An imputation model is coupled with a fixed surrogate strength predictor through cooperative training. Achieves R2 = 0.87-0.92 and reduces MSE by 50-70% compared to baselines (Yao et al., 2025).

### 6.5 Tandem Neural Networks

A novel tandem neural network (TNN) framework based on autoencoders enables end-to-end inverse design. A performance inference model is trained first, then a mix proportion generation model is connected upstream and trained for the "performance-to-mix" pathway. The generator enables real-time mix design with millisecond-level speed, outperforming traditional surrogate + optimisation approaches in both accuracy and speed (Li et al., 2025).

### 6.6 Gradient-Based Inverse Design

Differentiable forward models enable gradient-based optimisation of mix proportions. By backpropagating through a trained neural network, gradients of predicted strength with respect to input features can be computed and used for gradient descent in the design space. This is faster than evolutionary approaches but requires differentiable models and may get stuck in local optima (Chen et al., 2020; general materials science literature 2024-2025).

### 6.7 Active Learning

Active learning creates a closed loop between ML prediction and experimental validation: (1) train a model on existing data, (2) use acquisition functions to identify the most informative experiments, (3) conduct those experiments, (4) update the model. Meta's collaboration with University of Illinois demonstrated this approach with concrete, iteratively discovering high-performance, low-carbon mixes (2025-2026). Transfer learning can further accelerate the process by pre-training on simulation data before fine-tuning on experimental results (R2 = 0.95 with 15.9% improvement over traditional methods).

---

## 7. Supplementary Cementitious Materials (SCMs)

### 7.1 Fly Ash

Fly ash is a byproduct of coal combustion, classified as Class F (low calcium, <15% CaO, primarily pozzolanic) or Class C (high calcium, >15% CaO, both pozzolanic and cementitious).

**Strength effects**: No increase in compressive strength vs control at early ages (3-28 days), but up to 4% increase at 56 days for 20% replacement. The pozzolanic reaction is slow, consuming CH to form additional C-S-H over weeks to months. Optimal replacement level: 20-30% for strength, up to 50-65% for sustainability applications with acceptable long-term strength.

**CO2 and cost**: Fly ash CO2 ~ 0.01 kg CO2e/kg (essentially zero as a waste product). Cost: $30-130/ton depending on region (significantly less than OPC). A 30% fly ash replacement reduces concrete CO2 by approximately 29% (from 410 to 290 kg CO2/m3 for structural concrete).

**Dosage in standards**: FDOT allows 18-50% replacement; typical UK practice is 25% by mass of total cementitious content, reducing embodied carbon by >20%.

### 7.2 Ground Granulated Blast Furnace Slag (GGBS)

GGBS is a byproduct of iron production with both pozzolanic and latent hydraulic properties.

**Strength effects**: Slower early strength development but equal or higher long-term strength. 50% GGBS replacement is common in UK practice, reducing embodied carbon by >30%. Higher replacement (70%) is feasible but significantly delays early strength gain.

**CO2 and cost**: GGBS CO2 ~ 0.05-0.15 kg CO2e/kg. Cost similar to or slightly less than OPC. Reduces greenhouse gas emissions by 22-40% depending on replacement percentage.

### 7.3 Silica Fume

Silica fume is an ultrafine byproduct of silicon/ferrosilicon alloy production (particle size ~0.1 um, ~100x finer than cement).

**Strength effects**: Significant strength increase even at early ages: 15% improvement at 3 days for 5% replacement. Strongest effect of all SCMs on mechanical properties across all ages due to both pozzolanic reactivity and micro-filler effect. Optimal replacement: 5-10%, rarely exceeds 15% due to increased water demand.

**CO2 and cost**: CO2 ~ 0.02 kg CO2e/kg. Cost: $300-700/ton (expensive but used in small quantities). Required for ultra-high-performance concrete (UHPC).

### 7.4 Metakaolin

Metakaolin is produced by calcining kaolin clay at 600-800 degrees C. It is a manufactured pozzolan (unlike fly ash and slag which are industrial byproducts).

**Strength effects**: 10-15% replacement is optimal. At 20% replacement, compressive strength increased 33.4% at 90 days vs control. Early strength (1-7 days) is 5-23% higher; long-term strength (up to 120 days) is 10-30% higher. Flexural strength improvement peaks at 10% replacement (+10.2%). Refines microstructure, decreases pore size, and improves ITZ quality.

### 7.5 Natural Pozzolans

Natural pozzolans (volcanic ash, pumicite, diatomaceous earth) can replace up to 75% of fly ash in UHPC with acceptable strengths (>120 MPa). Interest is growing as coal plant closures reduce fly ash availability.

### 7.6 Limestone Calcined Clay Cement (LC3)

LC3 is a next-generation low-carbon cement composed of ~50% clinker, ~30% calcined clay, ~15% limestone, and ~5% gypsum. It reduces CO2 emissions by 30-40% vs OPC while achieving comparable or better 28-day compressive strength. LC3 shows excellent chloride penetration resistance, sulfate attack resistance, and alkali-silica reaction resistance. ML prediction models for LC3 achieve R2 = 0.927-0.928 using XGBoost and polynomial regression. SHAP analysis identifies water-to-cement/binder ratio and kaolinite content as key factors (2024-2025).

### 7.7 Ternary and Quaternary Blends

Ternary blends (e.g., 30% fly ash + 5-10% silica fume) exploit synergistic effects: fly ash provides long-term strength and CO2 reduction while silica fume provides early strength and pore refinement. Quaternary-blended systems (OPC + GGBS + fly ash + silica fume/limestone) have produced Pareto-optimal mixes achieving 51-80 MPa with ~62% less cement than conventional designs (2025).

---

## 8. Durability Prediction and Life Cycle Assessment

### 8.1 Chloride Penetration

The chloride migration coefficient (CMC) is crucial for evaluating concrete durability in marine/coastal environments. ML models predict CMC from mix design parameters, with ensemble models outperforming single models. The most important features are water-to-cement ratio (C/W) followed by silica fume-to-binder ratio (SF/B) and water-to-binder ratio (W/B). Five ML algorithms have been adopted for chloride resistance level prediction (2023-2024).

### 8.2 Carbonation

Carbonation causes CO2 penetration into concrete, lowering pH and increasing corrosion risk for steel reinforcement. Hybrid AI approaches for carbonation depth prediction have achieved good accuracy using mix design parameters and exposure conditions.

### 8.3 Integration with Strength Prediction

Modern multi-objective frameworks increasingly consider durability as a fourth objective alongside strength, cost, and CO2. GreenMix-Pareto's multi-task learning approach predicts strength, embodied CO2, energy, and resource use simultaneously, enabling holistic concrete design.

---

## 9. Transfer Learning and Data Scarcity

### 9.1 The Data Scarcity Challenge

Most concrete research is constrained to small datasets (UCI: 1,030 samples). Data scarcity is a well-recognised challenge in concrete informatics, with most labs having access to only hundreds to low thousands of mix records.

### 9.2 Transfer Learning Approaches

- **Simulation-based transfer learning**: Pre-train on physics-based simulation results, fine-tune on experimental data. Most effective when source dataset is more complex than target.
- **Dynamic weighted transfer learning**: Transfers knowledge from conventional concrete to novel formulations (e.g., phosphogypsum concrete), achieving R2 = 0.95 (15.9% improvement).
- **Few-shot meta-learning (MAML)**: Enables rapid adaptation to new concrete types using minimal samples.

### 9.3 Data Augmentation

- **SMOTE**: Applied to generate ~1,000 new synthetic concrete mixes for dataset enrichment.
- **VAE/GAN**: Physics-Informed CTGANs generate physically plausible synthetic mixtures with domain constraints.
- **Bootstrap resampling**: Combined with feature normalisation for cross-domain transfer.
- **Physics constraints**: Critical to prevent generation of infeasible mixes (mass conservation, w/c bounds, rheological constraints).

---

## 10. Key Gaps and Opportunities for HDR

1. **Derived feature engineering**: Most studies use raw UCI features. Systematic HDR exploration of physics-informed derived features (w/c, w/b, SCM%, paste fraction) could improve SOTA.
2. **Multi-objective inverse design**: Few studies combine prediction accuracy, Pareto optimisation, AND uncertainty quantification in one framework. GreenMix-Pareto and BOxCrete are notable exceptions.
3. **Non-obvious interactions**: HDR can systematically explore feature interactions (e.g., superplasticizer x slag, age x fly ash) that may reveal non-obvious strength-CO2-cost tradeoffs.
4. **Physics-informed constraints in ML**: Monotonicity constraints (strength vs w/b, strength vs age) improve robustness but are not yet standard practice.
5. **Generalisability**: Most models are trained and tested on a single dataset. Transfer learning across concrete types is under-explored.
6. **Practical deployment**: The gap between academic benchmarks and industry adoption remains large. Interpretable models (symbolic regression, SHAP-based explanations) are crucial for engineer trust.

---

## References

### Textbooks
- Neville, A.M. (2011). Properties of Concrete, 5th Edition. Pearson Education.
- Mehta, P.K. & Monteiro, P.J.M. (2014). Concrete: Microstructure, Properties, and Materials, 4th Edition. McGraw-Hill.
- Mindess, S., Young, J.F. & Darwin, D. (2003). Concrete, 2nd Edition. Prentice Hall.
- Kosmatka, S.H. & Wilson, M.L. (2016). Design and Control of Concrete Mixtures, 16th Edition. Portland Cement Association.

### Foundational Papers
- Abrams, D.A. (1918). Design of Concrete Mixtures. Bulletin 1, Structural Materials Research Laboratory, Lewis Institute, Chicago.
- Powers, T.C. & Brownyard, T.L. (1946-1947). Studies of Physical Properties of Hardened Portland Cement Paste. Bulletin No. 22, Portland Cement Association.
- Powers, T.C. (1958). Structure and Physical Properties of Hardened Portland Cement Paste. Journal of the American Ceramic Society, 41(1), 1-6.
- Yeh, I-C. (1998). Modeling of strength of high performance concrete using artificial neural networks. Cement and Concrete Research, 28(12), 1797-1808.

### Standards
- ACI Committee 211 (2022). ACI 211.1-22: Standard Practice for Selecting Proportions for Normal, Heavyweight, and Mass Concrete.
- BRE (1997). Design of Normal Concrete Mixes, 2nd Edition. Building Research Establishment.

(Full bibliography in papers.csv)
