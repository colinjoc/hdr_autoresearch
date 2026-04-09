# Design Variables: Concrete Mix Design Optimisation HDR

## Phase A: Prediction Infrastructure

### A1. Feature Engineering (what HDR iterates on)

**Raw features (from UCI dataset)**:
- cement (kg/m3)
- blast_furnace_slag (kg/m3)
- fly_ash (kg/m3)
- water (kg/m3)
- superplasticizer (kg/m3)
- coarse_aggregate (kg/m3)
- fine_aggregate (kg/m3)
- age (days)

**Derived features to explore** (each can be included/excluded by HDR):

| Feature | Formula | Physics rationale |
|---------|---------|-------------------|
| w_c_ratio | water / cement | Abrams' law: primary strength determinant |
| w_b_ratio | water / (cement + slag + fly_ash) | Extension to blended cements; SHAP ~7.7 |
| scm_replacement_pct | (slag + fly_ash) / (cement + slag + fly_ash) | Degree of cement replacement |
| agg_cement_ratio | (coarse_agg + fine_agg) / cement | Paste volume indicator |
| sand_ratio | fine_agg / (coarse_agg + fine_agg) | Aggregate gradation, workability |
| sp_per_binder | superplasticizer / (cement + slag + fly_ash) | Dosage normalised to binder content |
| total_binder | cement + slag + fly_ash | Total cementitious content |
| log_age | log(age) | Diminishing strength gain over time |
| paste_fraction | (cement/3.15 + slag/2.9 + fly_ash/2.2 + water + sp) / 1000 | Volume fraction of paste |
| slag_pct | slag / (cement + slag + fly_ash) | Slag replacement specifically |
| fa_pct | fly_ash / (cement + slag + fly_ash) | Fly ash replacement specifically |
| cement_sq | cement^2 | Non-linear cement effect |
| w_c_x_age | w_c_ratio * log_age | Interaction: hydration progress |
| binder_agg_ratio | total_binder / (coarse_agg + fine_agg) | Binder-to-aggregate ratio |

**HDR search space for feature set**:
- feature_include_wc: bool (include w/c ratio)
- feature_include_wb: bool (include w/b ratio)
- feature_include_scm_pct: bool
- feature_include_agg_cement: bool
- feature_include_sand_ratio: bool
- feature_include_sp_per_binder: bool
- feature_include_total_binder: bool
- feature_include_log_age: bool
- feature_include_paste_fraction: bool
- feature_include_individual_scm_pcts: bool
- feature_include_interactions: bool
- feature_include_squares: bool

### A2. Model Hyperparameters

**XGBoost** (primary model):
- n_estimators: int [100, 2000]
- max_depth: int [3, 15]
- learning_rate: float [0.01, 0.3]
- min_child_weight: int [1, 10]
- subsample: float [0.5, 1.0]
- colsample_bytree: float [0.3, 1.0]
- gamma: float [0, 5]
- reg_alpha: float [0, 10]
- reg_lambda: float [0, 10]

**CatBoost** (alternative):
- iterations: int [100, 2000]
- depth: int [4, 10]
- learning_rate: float [0.01, 0.3]
- l2_leaf_reg: float [1, 10]
- border_count: int [32, 255]

**LightGBM** (alternative):
- n_estimators: int [100, 2000]
- max_depth: int [3, 30]
- learning_rate: float [0.01, 0.3]
- num_leaves: int [20, 300]
- min_child_samples: int [5, 100]
- subsample: float [0.5, 1.0]
- colsample_bytree: float [0.3, 1.0]
- reg_alpha: float [0, 10]
- reg_lambda: float [0, 10]

### A3. Target Transform

- target_transform: categorical {none, log, sqrt, box_cox}
- The target (compressive strength in MPa) may benefit from transformation to reduce skewness

### A4. Cross-Validation Strategy

- cv_strategy: categorical {kfold_5, kfold_10, repeated_kfold_5x3, stratified_kfold}
- stratify_bins: int [3, 10] (number of strength bins for stratification)

### A5. Monotonicity Constraints

- enforce_monotonicity: bool
- monotone_wc: int {-1} (strength decreases with w/c)
- monotone_wb: int {-1} (strength decreases with w/b)
- monotone_age: int {1} (strength increases with age)
- monotone_cement: int {1} (strength increases with cement, all else equal)

---

## Phase B: Discovery / Multi-Objective Optimisation

### B1. Mix Design Space (continuous 8D)

The design space is the 8-dimensional space of mix proportions:

| Variable | Unit | Typical range | Hard constraints |
|----------|------|---------------|------------------|
| cement | kg/m3 | [100, 600] | > 0 |
| slag | kg/m3 | [0, 400] | >= 0 |
| fly_ash | kg/m3 | [0, 300] | >= 0 |
| water | kg/m3 | [100, 250] | > 0 |
| superplasticizer | kg/m3 | [0, 35] | >= 0 |
| coarse_aggregate | kg/m3 | [700, 1200] | > 0 |
| fine_aggregate | kg/m3 | [500, 1000] | > 0 |
| age | days | [1, 365] | fixed at 28 for design |

**Physical constraints**:
- Total volume approximately 1 m3: sum of (component / density) + air ~ 1.0 m3
- w/c ratio: [0.25, 0.80] for normal concrete
- w/b ratio: [0.20, 0.65] for HPC
- SCM replacement: [0%, 70%] total
- Fly ash: <= 50% of binder
- Slag: <= 70% of binder
- Air content: [1%, 8%] (implicit)

### B2. Objective Functions

**Strength** (maximise or satisfy constraint):
- predicted_strength = model.predict(mix)
- Constraint form: strength >= target_class (e.g., 30, 40, 50 MPa)

**Cost** (minimise):
- cost = sum(ingredient_i * price_per_kg_i)
- Prices (USD/kg, configurable):
  - cement: 0.12-0.18
  - slag: 0.08-0.15
  - fly_ash: 0.03-0.13
  - water: 0.0005
  - superplasticizer: 1.5-4.0
  - coarse_aggregate: 0.01-0.03
  - fine_aggregate: 0.01-0.025

**CO2** (minimise):
- co2 = sum(ingredient_i * co2_per_kg_i)
- CO2 factors (kg CO2e/kg):
  - cement: 0.90
  - slag: 0.07
  - fly_ash: 0.01
  - water: 0.001
  - superplasticizer: 0.50
  - coarse_aggregate: 0.01
  - fine_aggregate: 0.01

### B3. Optimisation Strategy (HDR variable)

- strategy: categorical {nsga2, mopso, bayesian_mobo, grid_then_refine, random_pareto}
- population_size: int [50, 500] (for evolutionary algorithms)
- n_generations: int [100, 1000]
- crossover_prob: float [0.5, 0.95]
- mutation_prob: float [0.01, 0.3]
- n_initial_samples: int [50, 500] (for Bayesian)
- acquisition_function: categorical {ehvi, ucb, ei} (for Bayesian)

### B4. Constraint Handling

- min_strength_class: float [20, 80] MPa
- max_wc_ratio: float [0.35, 0.65]
- max_wb_ratio: float [0.25, 0.55]
- max_scm_replacement: float [0.30, 0.70]
- workability_proxy: categorical {none, min_sp_per_binder, min_paste_fraction}

### B5. Pareto Analysis Variables

- n_pareto_points: int [50, 500]
- reference_point: [strength_min, cost_max, co2_max]
- hypervolume_indicator: bool (compute HV for solution quality)
- knee_point_selection: categorical {topsis, min_distance, manual}

### B6. Discovery-Specific Exploration

- explore_unusual_regions: bool (intentionally sample from under-represented mix regions)
- constraint_relaxation: float [0, 0.2] (allow slight constraint violations for exploration)
- interaction_focus: list of feature pairs to specifically investigate
  - [cement, slag]
  - [fly_ash, superplasticizer]
  - [water, slag]
  - [age, fly_ash]
  - [superplasticizer, water]

---

## HDR Iteration Summary

### Phase A iteration targets (prediction quality)
- Primary metric: R2 on held-out test set
- Secondary metrics: RMSE (MPa), MAE (MPa), MAPE (%)
- Baseline to beat: R2 = 0.91 (XGBoost with raw features, Yeh-style)
- Target: R2 >= 0.94 with interpretable feature importance

### Phase B iteration targets (discovery quality)
- Primary metric: Pareto hypervolume indicator (strength x cost x CO2)
- Secondary metrics: number of feasible Pareto-optimal solutions, spread of Pareto front
- Discovery target: identify non-obvious mixes that are simultaneously stronger, cheaper, and lower-carbon than conventional designs
- Novelty target: mixes with unusual SCM combinations, unexpected superplasticizer interactions, or counter-intuitive aggregate ratios
