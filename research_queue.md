# Research Queue: Concrete Mix Design Optimisation

## Phase A: Prediction Infrastructure

### H1. Derived water-binder ratio improves prediction over raw features
**Hypothesis**: Adding w/b ratio = water / (cement + slag + fly_ash) as a derived feature to XGBoost will improve R2 by >= 0.02 over using only the 8 raw UCI features.
**Rationale**: SHAP analysis consistently shows w/b ratio has the highest SHAP value (~7.7) among all features. Abrams' law establishes the fundamental physics of the w/c relationship. Extending to w/b accounts for SCM contributions.
**Test**: Train XGBoost with raw features vs raw + w/b on UCI dataset, compare R2 via 5-fold CV.
**Priority**: HIGH

### H2. Full physics-informed feature set achieves SOTA
**Hypothesis**: Adding all physics-informed derived features (w/c, w/b, SCM%, sand_ratio, sp_per_binder, log_age, paste_fraction, total_binder) simultaneously will push R2 above 0.94.
**Rationale**: Individual derived features are known important from SHAP. Their combination should provide the model with all physically relevant ratios. Current SOTA on UCI is R2 ~0.93-0.94.
**Test**: Full feature ablation study. Start with raw 8 features, add derived features one at a time, measure R2 and RMSE at each step.
**Priority**: HIGH

### H3. Log-transforming age improves temporal modelling
**Hypothesis**: Replacing raw age (days) with log(age) will reduce RMSE by >= 5%, because strength gain follows a logarithmic curve (rapid early, diminishing later).
**Rationale**: Concrete strength development follows approximately fc(t) ~ fc28 * log(t)/log(28). The log transformation linearises this relationship for tree-based models.
**Test**: Compare models with age vs log(age) vs both age + log(age).
**Priority**: MEDIUM

### H4. CatBoost outperforms XGBoost on UCI with tuned hyperparameters
**Hypothesis**: CatBoost with Bayesian-optimised hyperparameters will achieve R2 >= 0.93 on UCI, matching or exceeding XGBoost.
**Rationale**: Recent literature (2024-2025) consistently ranks CatBoost >= XGBoost for concrete prediction. CatBoost handles ordered boosting which may capture age-dependent effects better.
**Test**: Bayesian hyperparameter search for both XGBoost and CatBoost, compare on identical CV splits.
**Priority**: MEDIUM

### H5. Monotonicity constraints improve generalisation without hurting accuracy
**Hypothesis**: Enforcing monotonicity constraints (strength decreases with w/b, increases with age, increases with cement) will improve out-of-distribution generalisation by >= 10% relative RMSE while maintaining or improving in-distribution R2.
**Rationale**: Physics-informed constraints prevent models from learning spurious patterns. GreenMix-Pareto achieved R2=0.997 with monotonicity constraints. This is increasingly recommended in the literature (Li et al., 2024).
**Test**: Train XGBoost with and without monotone_constraints parameter on UCI. Evaluate on both random test split and deliberately extrapolated test set.
**Priority**: HIGH

### H6. Feature interactions reveal non-obvious strength drivers
**Hypothesis**: SHAP interaction analysis on the best model will reveal at least 3 non-trivial feature interactions (beyond obvious ones like cement x water) that explain > 5% of variance.
**Rationale**: Literature reports cement x water and age x SCM interactions, but systematic exploration of all pairwise interactions may reveal under-appreciated effects (e.g., superplasticizer x slag, fly_ash x coarse_aggregate).
**Test**: Compute SHAP interaction values for best model. Rank all interactions by magnitude. Identify any surprises.
**Priority**: MEDIUM

### H7. Ensemble stacking of XGBoost, CatBoost, LightGBM exceeds any individual model
**Hypothesis**: A stacked ensemble (meta-learner: Ridge regression) of all three gradient-boosted tree models will achieve R2 >= 0.95 on UCI.
**Rationale**: Recent papers report ensemble models achieving R2 = 0.95-0.96 by combining complementary boosting algorithms. Each captures slightly different patterns.
**Test**: Train XGBoost, CatBoost, LightGBM individually, then stack with Ridge meta-learner. Compare R2/RMSE.
**Priority**: MEDIUM

### H8. Target transformation (log or Box-Cox) of strength improves fit for extreme values
**Hypothesis**: Log-transforming the target (compressive strength) before training will reduce RMSE for very high (>60 MPa) and very low (<15 MPa) strength samples by >= 15%.
**Rationale**: Concrete strength distribution in UCI is right-skewed. Log transformation may improve prediction at the tails where most practical errors occur.
**Test**: Compare target-transformed vs raw models on tail subsets of the test data.
**Priority**: LOW

---

## Phase B: Multi-Objective Optimisation and Discovery

### H9. NSGA-II finds Pareto-optimal mixes dominating conventional designs
**Hypothesis**: NSGA-II optimisation using the trained prediction model as fitness function will identify at least 10 feasible mixes that dominate standard ACI 211 designs in all three objectives (strength, cost, CO2).
**Rationale**: Evolutionary multi-objective optimisation can explore the 8D design space far more thoroughly than traditional trial-and-error. Multiple papers report cement reductions of 25-62% while maintaining target strength.
**Test**: Define representative ACI 211 designs for C25, C30, C40, C50. Run NSGA-II. Count Pareto-dominant solutions.
**Priority**: HIGH

### H10. High SCM replacement (>50%) with superplasticizer can match C40 strength
**Hypothesis**: Mixes with >50% SCM replacement (combined slag + fly ash) can achieve 40 MPa at 28 days if superplasticizer dosage is optimised to maintain low w/b ratio.
**Rationale**: High SCM mixes drastically reduce CO2 and cost. The challenge is early strength. Superplasticizer allows water reduction (and hence lower w/b) without sacrificing workability, potentially compensating for slower SCM reaction.
**Test**: Generate mixes via NSGA-II with SCM% > 50% constrained. Check predicted 28-day strength and validate against known empirical bounds.
**Priority**: HIGH

### H11. Slag-dominant mixes are more cost-effective than fly-ash-dominant at high replacement levels
**Hypothesis**: For SCM replacement > 40%, slag-dominant mixes (slag/fly_ash ratio > 3) produce higher 28-day strength than fly-ash-dominant mixes at comparable cost and CO2.
**Rationale**: Slag has latent hydraulic properties (self-cementing), while fly ash is purely pozzolanic and slow. At high replacement, slag's hydraulic contribution becomes critical for 28-day strength. However, slag is more expensive and has higher CO2 than fly ash.
**Test**: Partition Pareto front by slag/fly_ash ratio. Compare strength contours at equal cost and CO2 levels.
**Priority**: MEDIUM

### H12. The Pareto frontier has a "knee" at approximately 30-35% SCM replacement
**Hypothesis**: The Pareto front of strength vs CO2 will show a pronounced knee (diminishing returns on CO2 reduction) at approximately 30-35% SCM replacement, corresponding to the point where further replacement significantly impacts 28-day strength.
**Rationale**: Fly ash replacement beyond 30% shows diminishing strength returns (optimum at 20-30%). The knee represents the most efficient tradeoff point for practitioners. GreenMix-Pareto's knee was at ~50 MPa / 220 kg CO2 per m3.
**Test**: Compute the Pareto front and identify the knee using the TOPSIS method. Characterise the mix composition at the knee.
**Priority**: HIGH

### H13. Superplasticizer interactions with SCMs are under-exploited
**Hypothesis**: The optimal superplasticizer dosage per binder varies significantly with SCM type and replacement level: slag-heavy mixes need less SP than fly-ash-heavy mixes for equivalent workability.
**Rationale**: Fly ash particles are spherical and improve workability naturally ("ball bearing effect"), while slag's angular particles may increase water demand. This interaction affects the cost-strength-CO2 tradeoff.
**Test**: Fix target strength at 40 MPa. Vary SCM type (slag-dominant vs fly-ash-dominant). Optimise SP dosage. Compare resulting cost and CO2.
**Priority**: MEDIUM

### H14. Bayesian optimisation finds better Pareto fronts than NSGA-II in fewer evaluations
**Hypothesis**: Bayesian multi-objective optimisation (EHVI acquisition) will achieve equivalent or better Pareto hypervolume as NSGA-II with 3-5x fewer model evaluations.
**Rationale**: BOxCrete (Meta) demonstrated successful BO for concrete. BO is sample-efficient and uncertainty-aware, making it ideal when each evaluation (lab test) is expensive. For our setting with a fast surrogate model, BO's sample efficiency matters less, but its uncertainty awareness may still help find better frontiers.
**Test**: Run both NSGA-II and BO-EHVI to equivalent computation budgets. Compare hypervolume indicator.
**Priority**: MEDIUM

### H15. Inverse design via gradient descent through differentiable model discovers novel mixes
**Hypothesis**: Gradient-based inverse design (backpropagation through a neural network surrogate) will discover at least 5 feasible mixes not present in the Pareto front from evolutionary optimisation.
**Rationale**: Gradient methods can navigate smooth loss landscapes efficiently. A differentiable neural network surrogate enables direct gradient computation. This may find solutions in narrow regions that evolutionary algorithms miss.
**Test**: Train a differentiable neural network on UCI. Backpropagate from target properties to mix inputs. Compare discovered mixes with NSGA-II Pareto front.
**Priority**: MEDIUM

### H16. Age-28 optimised mixes differ significantly from age-56 optimised mixes for SCM-heavy concrete
**Hypothesis**: When optimising for 56-day strength instead of 28-day, the optimal SCM replacement increases by >= 15 percentage points, because SCMs gain more strength after 28 days.
**Rationale**: SCMs (especially fly ash and slag) have slower pozzolanic/hydraulic reactions. Specifying 56-day strength is increasingly adopted (per Concrete Centre guidance) and would dramatically change the Pareto frontier.
**Test**: Run NSGA-II twice: once with age=28 fixed, once with age=56 fixed. Compare optimal SCM replacement levels.
**Priority**: HIGH

### H17. Ternary blends (cement + slag + fly_ash) outperform binary blends on the Pareto front
**Hypothesis**: Ternary blends using both slag and fly ash simultaneously will produce Pareto-dominant solutions over binary blends (cement + one SCM) in at least 20% of cases.
**Rationale**: Literature on quaternary blends (2025) shows synergistic effects: fly ash provides long-term strength and cost/CO2 benefits, while slag provides intermediate-term hydraulic strength. Combined, they can cover each other's weaknesses.
**Test**: Run separate NSGA-II optimisations: binary (slag only), binary (fly ash only), ternary (both). Compare Pareto hypervolumes.
**Priority**: HIGH

### H18. Aggregate ratio has minimal effect on strength but significant effect on cost
**Hypothesis**: Varying the coarse/fine aggregate ratio within physical limits (sand ratio 0.35-0.50) changes predicted cost by >= 5% but predicted strength by < 2%.
**Rationale**: SHAP consistently ranks aggregates lowest in feature importance for strength. But aggregate costs vary regionally, and the ratio affects workability and total material volume.
**Test**: Fix binder and water content at C40 levels. Vary sand ratio from 0.35 to 0.50. Measure predicted strength change and cost change.
**Priority**: LOW

### H19. Physics-constrained synthetic data augmentation improves inverse design quality
**Hypothesis**: Augmenting the UCI dataset with physics-constrained synthetic samples (via PI-CTGAN) will improve the quality of inverse-designed mixes, as measured by predicted-vs-actual strength deviation on validation mixes.
**Rationale**: The UCI dataset has 1,030 samples with limited coverage of the 8D design space. Data augmentation with physics constraints can fill gaps. PI-CTGAN enforces mass conservation and w/c bounds.
**Test**: Train PI-CTGAN, generate 5,000 synthetic samples. Retrain prediction model on combined data. Compare inverse design quality.
**Priority**: MEDIUM

### H20. Transfer learning from ConcreteXAI improves prediction on UCI
**Hypothesis**: Pre-training on ConcreteXAI (18,480 samples) and fine-tuning on UCI will improve R2 by >= 0.01 over training on UCI alone.
**Rationale**: ConcreteXAI covers 12 formulations over 10 years. Transfer learning from a richer source dataset improves target performance (literature shows R2 improvement of ~16%).
**Test**: Pre-train on overlapping features of ConcreteXAI. Fine-tune on UCI. Compare with UCI-only model.
**Priority**: MEDIUM

### H21. The strongest low-CO2 mixes use unexpected ingredient ratios
**Hypothesis**: Among mixes with CO2 < 150 kg CO2e/m3 and strength > 40 MPa, the optimal designs will feature ingredient ratios that differ from standard practice by > 2 standard deviations in at least one dimension.
**Rationale**: This is the core discovery hypothesis. HDR exploration of the design space should uncover non-obvious combinations that are simultaneously strong, cheap, and low-carbon. Literature reports cement reductions of 62% in optimised quaternary blends.
**Test**: Generate full Pareto front. Filter to CO2 < 150 and strength > 40 MPa. Compute z-scores of all ingredient ratios relative to UCI dataset statistics. Report any |z| > 2.
**Priority**: HIGH

### H22. Cost-optimised mixes are not the same as CO2-optimised mixes
**Hypothesis**: The mix that minimises cost (subject to strength >= 40 MPa) is substantively different from the mix that minimises CO2 (subject to same strength), differing in at least 2 ingredient quantities by > 20%.
**Rationale**: Although cement is both the costliest and highest-CO2 ingredient, the cost-optimal and CO2-optimal substitutes differ: fly ash is cheap and zero-CO2 but slow; slag is moderate cost and low CO2 but has some embodied carbon; silica fume is expensive but effective. This tension creates different optima.
**Test**: Run single-objective optimisation for cost-only and CO2-only (both subject to strength constraint). Compare resulting mixes.
**Priority**: HIGH

### H23. Symbolic regression discovers a compact strength equation competitive with XGBoost
**Hypothesis**: Symbolic regression (e.g., PySR/gplearn) on UCI with physics-informed feature space will discover an equation with <= 10 terms that achieves R2 >= 0.88.
**Rationale**: Symbolic regression has achieved R2 ~0.86-0.91 on related structural concrete problems. A compact equation would be far more deployable in engineering practice than a black-box model.
**Test**: Run PySR on UCI with derived features. Evaluate complexity-accuracy tradeoff. Compare with Abrams' law baseline.
**Priority**: MEDIUM

### H24. Active learning sample selection outperforms random sampling for Pareto exploration
**Hypothesis**: An active learning strategy (acquire next mix design using Expected Hypervolume Improvement) will achieve equivalent Pareto front quality as random sampling with 50% fewer samples.
**Rationale**: Meta's BOxCrete demonstrated 10x faster design cycle with active learning. Even with a surrogate model (rather than real experiments), active learning should be more efficient at exploring the Pareto front.
**Test**: Simulate active learning loop: start with 100 random mixes, iteratively add 10 mixes via EHVI vs 10 random. Compare hypervolume after 500 total evaluations.
**Priority**: MEDIUM

### H25. Uncertainty quantification reveals where the model is most uncertain about strength
**Hypothesis**: The regions of highest model uncertainty in the mix design space (as estimated by ensemble variance or conformal prediction intervals) will correspond to high-SCM, high-SP, low-water mixes that are under-represented in the UCI dataset.
**Rationale**: The UCI dataset is biased toward conventional mixes. Extreme mixes (very high SCM replacement, very low w/b with high SP) are rare in the data. These are precisely the mixes most interesting for sustainable concrete discovery.
**Test**: Train ensemble of 10 XGBoost models with different seeds. Map uncertainty (std of predictions) across the design space. Identify regions of highest uncertainty. Compare with UCI data density.
**Priority**: HIGH
