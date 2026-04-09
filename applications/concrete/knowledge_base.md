# Knowledge Base: Concrete Mix Design Optimisation

## 1. UCI Dataset SOTA Benchmarks

### 1.1 Best Published Performance on UCI Concrete Dataset (1,030 samples, 8 features)

| Metric | Value | Model | Source |
|--------|-------|-------|--------|
| R2 (best single model) | 0.93-0.94 | CatBoost (tuned) | Nguyen et al. 2024; Gomaa et al. 2024 |
| R2 (best ensemble) | 0.95-0.96 | Stacked (XGB+CatBoost+LightGBM) | Multiple 2024-2025 |
| RMSE (best) | 2.0-2.7 MPa | CatBoost / Hybrid PCA-RFR-SVR-CNN | Multiple 2024-2025 |
| MAE (best) | 2.0-2.4 MPa | LightGBM / Ensemble | Multiple 2024-2025 |
| MAPE (best) | 5.5-8.3% | CatBoost / LightGBM | Multiple 2024-2025 |

### 1.2 Model Ranking (consensus from 2023-2025 literature)

1. CatBoost >= LightGBM (virtually tied for top)
2. XGBoost (close behind)
3. Random Forest
4. SVR (Support Vector Regression)
5. ANN (Artificial Neural Network)
6. Symbolic Regression (lower accuracy but interpretable)
7. KNN
8. Linear/Elastic Net Regression

### 1.3 Industry-Scale Performance

- 70,000 test records: embedding-based neural networks achieve mean 28-day error ~2.5% (Mohanty et al. 2025)
- GreenMix-Pareto (1,000 mixes, physics-constrained): R2 = 0.997, RMSE = 0.58 MPa (Tipu et al. 2026)

---

## 2. Feature Importance Rankings

### 2.1 SHAP Feature Importance (typical XGBoost on UCI)

| Rank | Feature | Mean |SHAP| | Direction |
|------|---------|----------------|-----------|
| 1 | Cement | 7.46 | Positive (more cement -> higher strength) |
| 2 | Age | 5.0-7.0 | Positive (older -> stronger) |
| 3 | Water | 4.0-5.0 | Negative (more water -> lower strength) |
| 4 | Superplasticizer | 1.0-2.0 | Positive (indirect: enables lower w/c) |
| 5 | Fly ash | 0.8-1.5 | Complex (reduces early, increases late strength) |
| 6 | Blast furnace slag | 0.5-1.2 | Complex (latent hydraulic contribution) |
| 7 | Coarse aggregate | 0.3-0.5 | Weak positive |
| 8 | Fine aggregate | 0.2-0.4 | Weak positive |

### 2.2 Derived Feature Importance

| Feature | Mean |SHAP| | Notes |
|---------|----------------|-------|
| Water-binder ratio (w/b) | 7.66 | Most important derived feature |
| Total binder | 3.0-5.0 | Strong positive |
| SCM replacement % | 1.5-3.0 | Non-linear effect |
| SP per binder | 0.8-1.5 | Positive |
| Sand ratio | 0.3-0.5 | Weak |

### 2.3 Key Interactions (from SHAP interaction analysis)

- **Cement x Water**: Strongest interaction. The effect of cement depends strongly on water content (i.e., w/c ratio matters, not cement alone).
- **Age x SCM content**: SCM-heavy mixes show different strength evolution than OPC-heavy mixes. Age has larger positive effect in SCM mixes at later ages.
- **Superplasticizer x Water**: SP enables water reduction; their joint effect on strength is synergistic.
- **Slag x Fly ash**: Ternary combinations show non-additive effects.

---

## 3. Abrams' Law and Its Limitations

### 3.1 The Law

fc = A / B^(w/c)

- A ~ 96 MPa for OPC at 28 days
- B ~ 8 for OPC at 28 days
- Valid for w/c ~ 0.3 to 0.8
- Discovered by Duff Abrams in 1918 via thousands of systematic experiments

### 3.2 Limitations

1. **Does not account for SCMs**: When slag or fly ash replace cement, the effective binder is larger than cement alone. The water-binder ratio (w/b) is more appropriate.
2. **Assumes full hydration**: At very low w/c (< 0.35), insufficient water for full hydration means actual strength can be lower than predicted.
3. **Ignores superplasticizer effect**: Modern superplasticizers allow very low w/c (0.20-0.30) with adequate workability, extending the relationship into regions Abrams did not test.
4. **Age-independent in basic form**: The constants A and B change with age, but the basic form does not capture the time evolution of strength.
5. **Aggregate effects neglected**: Aggregate quality, gradation, and type affect strength but are not captured.
6. **Temperature and curing effects**: Not accounted for in the basic empirical relationship.

### 3.3 Extensions

- **Water-cement-density ratio law** (Li et al. 2020): Adds relative apparent density as a second predictor.
- **Generalised Abrams' law** (multiple authors): Adds terms for cement content, paste content, consistency, squared terms.
- **Time-dependent generalisation** (Popovics 2006): fc(t) = fc28 * [A(t) / B(t)^(w/c)] with age-dependent constants.
- **Powers' gel-space ratio**: fc = A * X^n where X = gel-space ratio, n ~ 3. More fundamental but requires hydration degree measurement.

---

## 4. CO2 and Cost per Ingredient

### 4.1 Embodied CO2

| Ingredient | kg CO2e / kg | kg CO2e / m3 (typical) | % of total |
|------------|-------------|----------------------|------------|
| Portland cement (OPC) | 0.82 - 1.00 | 280 - 400 | 75-90% |
| GGBS | 0.05 - 0.15 | 5 - 15 | 1-5% |
| Fly ash (Class F/C) | 0.00 - 0.03 | 0 - 3 | <1% |
| Silica fume | 0.01 - 0.03 | 0.5 - 1.5 | <1% |
| Coarse aggregate | 0.005 - 0.02 | 5 - 20 | 2-5% |
| Fine aggregate | 0.005 - 0.02 | 3 - 15 | 1-4% |
| Water | ~0.001 | ~0.2 | <0.1% |
| Superplasticizer | 0.20 - 0.70 | 1 - 7 | <2% |

**Total typical concrete**: 300-450 kg CO2e/m3 for conventional; 150-250 kg CO2e/m3 for optimised low-carbon.

### 4.2 Cost Estimates

| Ingredient | USD / ton (2024) | USD / m3 (typical) |
|------------|-----------------|-------------------|
| Portland cement | 120 - 180 | 40 - 70 |
| GGBS | 80 - 150 | 8 - 30 |
| Fly ash | 30 - 130 | 2 - 20 |
| Silica fume | 300 - 700 | 10 - 30 |
| Coarse aggregate | 10 - 30 | 10 - 30 |
| Fine aggregate | 10 - 25 | 5 - 20 |
| Water | ~0.50 | ~0.10 |
| Superplasticizer | 1,500 - 4,000 | 5 - 40 |

**Total typical concrete**: 70-120 USD/m3 for conventional; 50-100 USD/m3 for optimised.

### 4.3 Key Insight for Optimisation

Cement is simultaneously the most expensive bulk ingredient AND the highest CO2 contributor. Every kg of cement replaced by an SCM reduces both cost and CO2 (with fly ash being the best on both dimensions). The constraint is maintaining adequate strength, especially at 28 days. This makes the strength-cost-CO2 optimisation problem highly tractable: the question is how much cement can be safely removed.

---

## 5. Typical Strength Ranges by Mix Type

| Concrete type | Strength class | Typical 28d fc (MPa) | Typical w/b | Typical cement (kg/m3) |
|---------------|----------------|----------------------|-------------|----------------------|
| Normal strength concrete | C20-C40 | 20-50 | 0.45-0.65 | 250-400 |
| High performance concrete | C50-C80 | 50-80 | 0.30-0.40 | 400-550 |
| Ultra-high performance (UHPC) | C100+ | 100-200 | 0.15-0.25 | 800-1000+ |
| Self-compacting concrete (SCC) | C30-C60 | 30-60 | 0.30-0.45 | 350-500 |
| High-volume fly ash concrete | C20-C40 | 20-40 | 0.35-0.50 | 150-250 |
| LC3 concrete | C30-C50 | 30-50 | 0.40-0.50 | 250-350 |
| Mass concrete | C15-C25 | 15-25 | 0.50-0.65 | 200-300 |

---

## 6. Strength Development Milestones

| Age (days) | % of 28-day strength (OPC) | % of 28-day strength (30% FA) | % of 28-day strength (50% slag) |
|------------|---------------------------|------------------------------|-------------------------------|
| 1 | 15-25% | 10-15% | 10-20% |
| 3 | 30-40% | 20-30% | 25-35% |
| 7 | 65-75% | 45-60% | 55-65% |
| 14 | 85-90% | 70-80% | 75-85% |
| 28 | 100% (reference) | 90-100% | 95-100% |
| 56 | 105-110% | 105-120% | 105-115% |
| 90 | 108-115% | 115-130% | 110-120% |

Key insight: SCM-heavy mixes catch up and often exceed OPC mixes by 56-90 days. Specifying 56-day rather than 28-day strength enables significantly higher SCM replacement.

---

## 7. UCI Dataset Statistics

### 7.1 Feature Distributions (from Yeh 1998, 1,030 samples)

| Feature | Min | Max | Mean | Std | Unit |
|---------|-----|-----|------|-----|------|
| Cement | 102.0 | 540.0 | 281.2 | 104.5 | kg/m3 |
| Blast furnace slag | 0.0 | 359.4 | 73.9 | 86.3 | kg/m3 |
| Fly ash | 0.0 | 200.1 | 54.2 | 64.0 | kg/m3 |
| Water | 121.8 | 247.0 | 181.6 | 21.4 | kg/m3 |
| Superplasticizer | 0.0 | 32.2 | 6.2 | 5.97 | kg/m3 |
| Coarse aggregate | 801.0 | 1145.0 | 972.9 | 77.8 | kg/m3 |
| Fine aggregate | 594.0 | 992.6 | 773.6 | 80.2 | kg/m3 |
| Age | 1 | 365 | 45.7 | 63.2 | days |
| Comp. strength | 2.33 | 82.60 | 35.82 | 16.71 | MPa |

### 7.2 Derived Feature Statistics (computed)

| Feature | Approximate range | Typical value |
|---------|-------------------|---------------|
| w/c ratio | 0.23 - 2.42 | ~0.65 |
| w/b ratio | 0.23 - 0.97 | ~0.45 |
| SCM replacement % | 0% - 77% | ~30% |
| Sand ratio | 0.35 - 0.55 | ~0.44 |
| Total binder | 102 - 540 | ~409 |

### 7.3 Data Characteristics

- **Missing values**: None (complete dataset)
- **Duplicates**: Some near-duplicates exist (same mix, different ages)
- **Licence**: CC BY 4.0
- **Key limitation**: Only 8 features, no durability data, no workability data, no curing conditions, no aggregate properties

---

## 8. Available Datasets and Tools

| Dataset / Tool | Size | Description | Access |
|----------------|------|-------------|--------|
| UCI Concrete | 1,030 | 8 features + strength | archive.ics.uci.edu |
| ConcreteXAI | 18,480 | 12 formulations, mechanical + NDT | GitHub (JaGuzmanT/ConcreteXAI) |
| FHWA LTPP ARMAD | Thousands | Pavement concrete properties | LTPP InfoPave |
| Meta SustainableConcrete | 500+ | Mortar and concrete strength at 5 ages | GitHub (facebookresearch/SustainableConcrete) |
| BOxCrete | Open source | GP + BoTorch for concrete optimisation | GitHub (MIT licence) |
| Kaggle datasets | Various | UCI mirrors + community notebooks | kaggle.com |

---

## 9. Key Physical Constraints for Mix Design

### 9.1 Volume Constraint
Sum of (component_i / density_i) + air_content = 1.0 m3

Approximate densities (kg/m3):
- Cement: 3,150
- Slag: 2,900
- Fly ash: 2,200 (Class F), 2,600 (Class C)
- Silica fume: 2,200
- Water: 1,000
- Superplasticizer: 1,100
- Coarse aggregate: 2,600-2,800
- Fine aggregate: 2,600-2,700
- Air: 0 (but occupies 1-8% of volume)

### 9.2 Standard Limits

| Parameter | Typical limit | Standard |
|-----------|--------------|----------|
| Max w/c ratio (durability) | 0.40-0.65 | EN 206, ACI 318 |
| Min cement content | 260-360 kg/m3 | EN 206 (exposure-dependent) |
| Max cement content | 500-550 kg/m3 | Thermal cracking risk |
| Fly ash replacement | <= 50% | EN 197, ACI |
| Slag replacement | <= 70% | EN 197, ACI |
| Silica fume replacement | <= 15% | EN 197, ACI |
| Total SCM | <= 70% | Various |
| Min total binder | 280-400 kg/m3 | EN 206 |

---

## 10. Established Concrete Strength Equations

### 10.1 Abrams' Law (1918)
fc = A / B^(w/c)
- OPC 28d: A ~ 96 MPa, B ~ 8
- Accuracy: R2 ~ 0.65-0.75 on diverse datasets

### 10.2 Powers' Gel-Space Ratio (1958)
fc = A * X^n
- X = gel-space ratio = volume of gel / (volume of gel + capillary pores)
- A ~ 234 MPa, n ~ 2.6-3.0
- More fundamental than Abrams but requires hydration degree measurement

### 10.3 Bolomey Formula
fc = A * (c/w - 0.5)
- A = cement-dependent constant
- Linear approximation of Abrams for practical w/c range

### 10.4 ACI 209 Strength-Time Relationship
fc(t) = [t / (a + b*t)] * fc28
- a = 4.0, b = 0.85 for OPC Type I, moist cured
- a = 2.3, b = 0.92 for OPC Type III
- Does not account for SCMs well

### 10.5 CEB-FIP Model Code
fc(t) = fc28 * exp[s * (1 - sqrt(28/t))]
- s = 0.20 (rapid hardening), 0.25 (normal), 0.38 (slow)
- Better handles different cement types

---

## 11. Open Research Questions

1. Can physics-informed ML (with monotonicity constraints, domain features) consistently exceed R2 = 0.95 on UCI-scale datasets?
2. What is the minimum dataset size needed for reliable multi-objective concrete optimisation?
3. How well do models trained on one dataset transfer to different cement sources and aggregate types?
4. Can inverse design frameworks reliably generate mixes that validate experimentally (not just in silico)?
5. What is the practical limit of SCM replacement while maintaining C40+ strength at 28 days?
6. How should uncertainty be quantified and communicated in AI-suggested concrete mixes for engineering adoption?
7. Can symbolic regression discover new empirical laws that extend Abrams' law to blended cements?
