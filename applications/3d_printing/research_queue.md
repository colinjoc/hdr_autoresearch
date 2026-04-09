# Research Queue: 3D Printing Parameter Optimisation

This queue enumerates Hypothesis-Driven Research (HDR) hypotheses for the FDM/FFF parameter optimisation project. Each hypothesis is testable, quantitative, and grounded in the literature review. Phase A focuses on building the prediction infrastructure (which features matter, how they interact, which models work). Phase B focuses on discovery: finding parameter combinations that dominate conventional settings on multi-objective tradeoffs.

Priority: HIGH = critical path, MEDIUM = valuable secondary evidence, LOW = nice to have.

---

## Phase A: Prediction Infrastructure

### H1. Linear energy density is the dominant physics-informed feature for tensile strength
**Hypothesis**: Introducing `E_lin = T_nozzle * v_print / h_layer` (linear energy density proxy, units deg C * mm^-1 * s^-1 * mm^-1) as a derived feature to an XGBoost baseline will improve tensile-strength R2 by >= 0.03.
**Rationale**: The three parameters repeatedly flagged as most important for UTS are nozzle temperature, print speed, and layer height [73, 74, 112]. They couple through the thermal history: higher T and lower v give more time for chain interdiffusion, and lower h means thinner layers with faster reheating from above. `E_lin` combines them into a single dimensionally meaningful group analogous to the volumetric energy density used in laser powder bed fusion literature.
**Test**: Train XGBoost on the Kaggle 3D Printer dataset [102] with and without `E_lin`; compare R2 via 5-fold CV on tensile strength.
**Priority**: HIGH

### H2. A full physics-informed feature set beats raw parameters by >= 0.05 R2
**Hypothesis**: Adding the derived feature set {E_lin, volumetric_flow = v * w_line * h_layer, cooling_rate_proxy = (T_nozzle - T_amb) * F_cool / h_layer, interlayer_time = layer_area / (v * w_line), infill_contact_area = rho_infill * pattern_factor} simultaneously improves R2 by >= 0.05 vs raw parameters.
**Rationale**: Individual derived features encode distinct physical mechanisms (diffusion, rheology, cooling, bonding time, load-path area). Their joint effect should exceed any single one. The SHAP literature [73, 74] already identifies individual drivers but rarely tests them together.
**Test**: Sequential feature addition on Kaggle dataset [102] + APMonitor [104] combined. Measure R2 and RMSE at each step.
**Priority**: HIGH

### H3. log(print_time) target transformation improves tail accuracy
**Hypothesis**: Log-transforming the print-time target before training reduces MAE by >= 10% on the slowest 10% of samples, because print time is right-skewed.
**Rationale**: Print time follows v * h_layer in the denominator, yielding a 1/x shape that compresses at high values. A log transform linearises the relationship for tree-based models.
**Test**: Train XGBoost on raw vs log-transformed target. Compare MAE and MAPE on tail subsets.
**Priority**: LOW

### H4. Gaussian Process Regression matches XGBoost accuracy on small FDM datasets
**Hypothesis**: On datasets with N < 200 samples (typical FDM size), a tuned GPR with Matern 5/2 kernel achieves R2 within 0.01 of tuned XGBoost for tensile strength prediction, while providing calibrated uncertainty.
**Rationale**: Multiple studies use GPR as surrogate in BO workflows [38, 39, 41, 42] because it handles small data well and provides uncertainty estimates. XGBoost usually wins on larger tabular data but may lose its edge at small N.
**Test**: 5-fold CV comparison on APMonitor (N=116) [104] and Kaggle 3D Printer (N ~ 50) [102]. Measure R2, RMSE, and calibration of predictive intervals.
**Priority**: HIGH

### H5. Monotonicity constraints improve out-of-distribution generalisation
**Hypothesis**: Imposing monotone constraints (UTS increases monotonically with infill_density and T_nozzle; decreases monotonically with print_speed within the feasible window) reduces OOD RMSE by >= 15% while matching in-distribution R2.
**Rationale**: Literature consensus [73, 74, 112] supports these directional effects. Monotonicity acts as a physics-informed regulariser. Monotonic XGBoost has shown strong OOD gains in concrete and antenna domains (parallel HDR projects).
**Test**: Train XGBoost with and without `monotone_constraints`. Create an OOD split by holding out the top/bottom 10% of infill density.
**Priority**: HIGH

### H6. SHAP interaction analysis reveals at least 3 non-obvious interactions
**Hypothesis**: SHAP interaction values on the best model will identify at least 3 parameter interactions beyond the well-known temperature-speed coupling, each accounting for > 3% of variance.
**Rationale**: Most parameter studies analyse main effects only. RSM literature [67, 68, 69] captures second-order terms but rarely reports them. SHAP interaction values give a principled map of joint effects.
**Test**: Compute SHAP interaction matrix for best model. Rank interactions by mean |value|. Report the top 5.
**Priority**: MEDIUM

### H7. CatBoost outperforms XGBoost when infill_pattern (categorical) is included
**Hypothesis**: When the categorical infill pattern is encoded as a native categorical feature, CatBoost beats XGBoost (with one-hot) by >= 0.02 R2 on combined tensile-strength prediction.
**Rationale**: CatBoost handles categoricals natively using ordered target statistics. Infill pattern is a high-cardinality categorical (8+ options) whose one-hot representation dilutes XGBoost splits.
**Test**: Train both with Bayesian-tuned hyperparameters on combined dataset with infill_pattern present. Compare 5-fold CV R2.
**Priority**: MEDIUM

### H8. Transfer learning from PLA to PETG improves small-data PETG models
**Hypothesis**: Pre-training on a larger PLA dataset and fine-tuning on a small PETG dataset reduces PETG tensile RMSE by >= 20% compared to training on PETG alone.
**Rationale**: PLA and PETG share the same extrusion physics but differ in thermal windows. Transfer learning has strong theoretical basis and is under-explored in FDM [open challenge from Theme 7].
**Test**: Train MLP on PLA subset, fine-tune on PETG subset. Compare with PETG-only baseline at matched capacity.
**Priority**: MEDIUM

### H9. Symbolic regression discovers a compact empirical law for print time
**Hypothesis**: Symbolic regression (PySR) discovers an equation with <= 5 terms that predicts print time with R2 >= 0.95, and matches the known kinematic form `t ~ V / (v * w_line * h_layer)`.
**Rationale**: Print time is nearly deterministic from geometry and kinematics. This is a sanity check that SR can recover known physics - a prerequisite for trusting it on strength prediction.
**Test**: Run PySR on the print-time target from the Kaggle dataset. Check if the recovered expression matches the analytic form.
**Priority**: MEDIUM

### H10. Ensemble stacking of XGBoost + GPR + MLP beats any individual model on multi-target tasks
**Hypothesis**: A stacked ensemble predicting [UTS, surface_Ra, dimensional_err, print_time] simultaneously achieves mean R2 >= 0.90 across targets, exceeding the best single model by >= 0.02.
**Rationale**: Different models capture different structure: XGBoost excels at interactions, GPR at smooth surfaces, MLP at cross-target correlations.
**Test**: Multi-output stacking with Ridge meta-learner. Compare with each base model.
**Priority**: MEDIUM

### H11. A physics-informed cooling-rate proxy predicts warping risk
**Hypothesis**: The derived feature `cool_rate = (T_nozzle - T_bed) * F_cool / (h_layer * sqrt(w_line))` correlates with warping-defect incidence (binary label) with AUC >= 0.80.
**Rationale**: Warping is driven by thermal gradients and differential shrinkage [55-58]. This proxy captures the dominant drivers in closed form.
**Test**: Label samples with documented warping events. Train logistic regression on `cool_rate` alone vs raw parameters.
**Priority**: MEDIUM

### H12. Material-conditioned models outperform material-one-hot models
**Hypothesis**: A multi-task model with a material embedding layer (trained jointly on PLA+PETG+ABS) beats a model with material one-hot encoding by >= 0.03 mean R2 across target properties.
**Rationale**: Material-specific thermal windows are nonlinear. An embedding can learn a continuous material representation that generalises better than discrete codes.
**Test**: Train MLP with embedding vs one-hot on multi-material dataset (APMonitor PLA+ABS [104] plus PETG papers).
**Priority**: LOW

---

## Phase B: Discovery and Multi-Objective Optimisation

### H13. NSGA-II finds Pareto-optimal settings dominating slicer defaults across strength, time, and material use
**Hypothesis**: NSGA-II over the trained surrogate will find >= 20 parameter sets that dominate Cura/PrusaSlicer PLA defaults in all three objectives: UTS higher by >= 5%, print time lower by >= 5%, material usage lower by >= 5%.
**Rationale**: Slicer defaults are conservative compromise values. Multi-objective search of the surrogate can find regions where all three objectives improve simultaneously. This is the headline discovery claim.
**Test**: Define Cura default as reference. Run NSGA-II (pop 200, 100 generations). Count dominating solutions.
**Priority**: HIGH

### H14. The Pareto frontier has a pronounced knee near 40-50% infill
**Hypothesis**: The strength-vs-material-use Pareto front shows a diminishing-returns knee at 40-50% infill for most patterns, beyond which strength gains drop below 0.1 MPa per percentage point.
**Rationale**: Infill density has a roughly saturating effect on UTS [74]. The knee represents the most efficient operating point for functional parts. Gyroid in particular is expected to saturate earlier than rectilinear.
**Test**: Compute Pareto fronts separately per infill pattern. Apply TOPSIS to locate the knee.
**Priority**: HIGH

### H15. Gyroid infill is Pareto-dominant over rectilinear for strength-per-time
**Hypothesis**: For equivalent infill density >= 30%, gyroid produces parts with higher strength-per-print-time ratio than rectilinear across all tested materials.
**Rationale**: Gyroid has the best isotropic strength-to-weight ratio [44] but is slower to print. The question is whether its higher strength compensates for the time penalty in a strength-per-time metric.
**Test**: Grid search over (density, pattern) with density in {20, 40, 60, 80}%, pattern in {gyroid, rectilinear, cubic, honeycomb}. Compute strength/time ratio.
**Priority**: HIGH

### H16. Bayesian optimisation matches NSGA-II hypervolume with 5x fewer evaluations
**Hypothesis**: BO with Expected Hypervolume Improvement reaches the same hypervolume as NSGA-II in 5x fewer surrogate evaluations.
**Rationale**: BO is sample-efficient [38-43]. In the HDR context, the surrogate is cheap but BO's uncertainty-awareness may still reveal better frontiers when the surrogate has local uncertainty.
**Test**: Run both NSGA-II and BO-EHVI. Track hypervolume vs evaluation count.
**Priority**: MEDIUM

### H17. Optimal nozzle temperature for strength is at the upper end of the safe window
**Hypothesis**: For each material, the strength-maximising T_nozzle (holding other parameters at Pareto-optimal values) sits within 5 C of the upper limit of the manufacturer window.
**Rationale**: Higher T improves chain interdiffusion and bond quality [48, 73]. The tradeoff (thermal degradation, dimensional error) only matters above the upper safe limit.
**Test**: Optimise UTS for each material subject to parameter bounds. Report T_nozzle at optimum.
**Priority**: MEDIUM

### H18. Strength-optimal settings differ substantially from surface-quality-optimal settings
**Hypothesis**: The parameter vector that maximises UTS differs from the one that minimises Ra by > 20% relative change in at least 3 of {T_nozzle, v_print, h_layer, F_cool}.
**Rationale**: Higher T and thinner layers both favour strength; thinner layers but lower speed favour surface. Cooling has opposite effects on the two objectives. The optima may be physically separated.
**Test**: Solve single-objective maxima for UTS and Ra separately. Compute element-wise difference.
**Priority**: HIGH

### H19. Inverse design via gradient descent through a differentiable surrogate recovers feasible optima
**Hypothesis**: Gradient-based inverse design (backprop through a neural network surrogate) finds >= 10 parameter vectors meeting hard targets (UTS >= 45 MPa for PLA, print time <= 2 h for a 50 mm test cube) that are not on the NSGA-II Pareto front.
**Rationale**: Gradient methods navigate smooth loss landscapes efficiently and can find solutions in narrow basins that population-based methods miss.
**Test**: Train differentiable MLP surrogate. Perform constrained gradient descent from random starting points. Verify feasibility with the XGBoost surrogate.
**Priority**: MEDIUM

### H20. Cooling fan speed interacts strongly with material in a direction opposite to naive intuition for ABS
**Hypothesis**: For ABS, the strength-optimal fan speed is 0-20%, but a thin intermediate band (20-40%) causes a local strength minimum that is worse than either extreme by > 10%.
**Rationale**: ABS cooling trades warping against interlayer bonding [38]. A non-monotonic relationship would be a non-obvious HDR finding with direct practical consequences.
**Test**: Hold other ABS parameters at typical values. Sweep F_cool in steps of 10%. Inspect the response.
**Priority**: MEDIUM

### H21. Active learning reduces required experiments by 50% for Pareto exploration
**Hypothesis**: Starting from 30 random samples and acquiring 50 additional samples via EHVI, active learning reaches hypervolume that matches 160 random samples.
**Rationale**: Active learning has demonstrated 50-75% sample reductions in materials discovery [116]. FDM is an ideal setting because each physical experiment is expensive.
**Test**: Simulate loop on held-out surrogate "ground truth." Compare acquired-sample hypervolume to random-sampling hypervolume curves.
**Priority**: MEDIUM

### H22. Retraction settings are near-irrelevant to mechanical properties but strongly affect dimensional error
**Hypothesis**: Retraction distance and speed have SHAP importance < 1% for UTS but > 10% for dimensional error.
**Rationale**: Retraction mainly controls stringing and oozing, which manifest as surface defects and dimensional inaccuracies rather than bulk strength. This would let us drop retraction parameters from the strength optimisation, reducing the search space.
**Test**: Compute SHAP for both targets on combined dataset with retraction features present.
**Priority**: LOW

### H23. A single pareto-dominant "universal" PLA recipe exists across geometries
**Hypothesis**: There exists a single parameter vector that dominates slicer defaults on UTS, print time, and material use for at least 80% of test geometries (dog bone, cube, bridge, overhang set).
**Rationale**: If true, it would provide a practical default. If false, it confirms that geometry-aware optimisation is required - a strong negative result also publishable.
**Test**: Find Pareto-optimal recipe on dog-bone data. Evaluate predicted performance on the other geometries using geometry-aware surrogate (if available) or report as open question.
**Priority**: MEDIUM

### H24. Tradeoff between strength and print time follows a power law with exponent near -0.5
**Hypothesis**: Along the strength-vs-time Pareto front, log(UTS) vs log(time) fits a power law with exponent in the range [-0.6, -0.4] with R2 >= 0.95.
**Rationale**: Power laws are common in materials tradeoffs (Ashby maps). The exponent ~ -0.5 would reflect the square-root dependence of interdiffusion bond strength on time.
**Test**: Fit log-log regression on Pareto-front points. Test exponent confidence interval.
**Priority**: LOW

### H25. A derived "print quality index" Q = UTS^alpha / (time^beta * material^gamma) has a clean physical optimum
**Hypothesis**: For alpha = 1, beta = 0.5, gamma = 0.3 (sensible defaults from cost-benefit analysis), the single-objective optimum of Q lies in a basin within 5% of the maximum across a 10% perturbation of the exponents.
**Rationale**: Scalarising multi-objective problems with weighted products provides a single target amenable to gradient methods. Robustness to exponent choice validates the scalarisation.
**Test**: Maximise Q for each exponent triple within +/- 10% of defaults. Check if optima cluster.
**Priority**: LOW

### H26. Uncertainty quantification flags the "high-speed high-temp" corner as under-explored
**Hypothesis**: Conformal prediction intervals on the surrogate identify the top 10% highest-uncertainty region as being the `v_print > 200 mm/s AND T_nozzle > 230 C` corner, which is under-represented in public datasets.
**Rationale**: Most datasets use conservative speeds (50-100 mm/s). High-speed filaments are a recent development, so the training data is skewed. Flagging this gap motivates targeted future experiments.
**Test**: Train conformal predictor. Map interval width across the 2D (v, T) slice. Identify widest region.
**Priority**: MEDIUM

---

## Success Metrics for Phase 0 -> Phase 1 Transition

Before moving to implementation the project must demonstrate:

1. A working baseline (XGBoost raw features) with R2 >= 0.75 on the Kaggle 3D Printer dataset [102] (documented in `experiment_log.md`).
2. Derived-feature ablation showing at least one physics-informed feature improves baseline by >= 0.02 R2 (validates H1 or H2).
3. First NSGA-II Pareto front plotted on the surrogate (validates H13 infrastructure).
4. Confirmed availability of >= 2 public datasets loaded and parsed (validates data access).

---

## Notes

- Hypotheses H1-H12 (Phase A) should be executed before Phase B.
- H13-H15 are the headline discovery claims and define success.
- Each hypothesis logs results in `experiment_log.md` with references back to this queue.
- Bracketed numbers [N] refer to `papers.csv` entries.
