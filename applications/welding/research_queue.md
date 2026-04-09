# Research Queue: Welding Parameter Optimisation HDR

## Phase 0 -- Research Hypothesis Queue

**Date:** 2026-04-02
**Scope:** Hypotheses for the HDR autoresearch loop. Derived from gaps identified in `literature_review.md` Section 10 and design variables in `design_variables.md`.

Format:

    ### H[N] -- Title [STATUS]
    **Impact:** why it matters
    **Hypothesis:** testable claim
    **Mechanism:** physical/statistical basis

Statuses: `[OPEN]` (not started), `[RUNNING]` (under active test), `[DONE]` (accepted/rejected).

---

## Phase A -- Feature Engineering and Predictive Modelling

Phase A hypotheses test which input features most accurately predict weld quality. Outputs of this phase feed Phase B optimisation.

### H1 -- Heat input is the single best-scalar predictor of HAZ width [OPEN]
**Impact:** Establishes whether a physics-informed scalar derived from V, I, and travel speed outperforms the raw parameters individually. Unlocks dimensional reduction and transfer learning.
**Hypothesis:** A regression model using heat input HI = (60 V I eta)/(1000 v) as the sole feature will explain >=80% of the variance in HAZ width across a multi-process dataset (GMAW, GTAW, SAW).
**Mechanism:** HAZ width scales with the thermal field integrated over the cooling cycle, which is dominated by heat input per unit length. Section 1.1 of the literature review and Kou (2003) support this scaling.

### H2 -- Cooling time t8/5 outperforms heat input for hardness prediction [OPEN]
**Impact:** Identifies the most informative derived feature for mechanical-property prediction in ferritic steels, guiding feature selection in Phase B surrogates.
**Hypothesis:** Using t8/5 (estimated via the Rosenthal-derived closed form or from thermocouple data) as a feature yields lower RMSE than using heat input when predicting Vickers hardness in low-alloy steel HAZ.
**Mechanism:** Hardness is governed by the phase fractions formed during cooling, which depend on the time spent in the 800-500 C range (Easterling, 1992; Li et al. 2022 CCT diagram work).

### H3 -- Carbon equivalent improves cross-material generalisation [OPEN]
**Impact:** Enables ML models to transfer between carbon steel grades without per-grade retraining.
**Hypothesis:** Adding CE (IIW formula) as a feature reduces out-of-distribution RMSE by >=25% when predicting weld quality on held-out steel grades compared to a baseline model that sees only raw composition fractions.
**Mechanism:** CE collapses the effect of compositional variation on hardenability into a single scalar, which generalises across grades (Lancaster 1999; IIW Doc IX-535-67).

### H4 -- V/I ratio captures metal transfer mode in GMAW better than V and I individually [OPEN]
**Impact:** Simpler, physics-motivated features that correlate with spatter, porosity, and arc stability.
**Hypothesis:** A classifier using V/I as a single feature will distinguish short-circuit / globular / spray metal transfer modes in GMAW carbon steel with >=90% accuracy, exceeding the accuracy of a classifier using V and I as independent features in the same feature-count budget.
**Mechanism:** The V/I ratio is a proxy for effective arc length at a given current, and transfer mode transitions (globular to spray) occur at characteristic arc-length thresholds (Lincoln Electric; GMAW transfer mode literature).

### H5 -- Energy density per unit travel predicts laser keyhole stability [OPEN]
**Impact:** Transfers arc-welding feature engineering concepts to laser welding, enabling unified models across processes.
**Hypothesis:** Laser keyhole collapse events are predicted by rho_E = Power / (pi * (d/2)^2 * v) exceeding a threshold-specific material-dependent critical value with >=85% precision in coaxial high-speed data.
**Mechanism:** Keyhole stability is governed by the balance between vapour pressure (driven by energy density) and hydrostatic/surface-tension forces (Goldak 1984; laser keyhole monitoring studies).

### H6 -- Physics-informed feature augmentation reduces data requirements [OPEN]
**Impact:** Key enabler for small-data welding ML (literature review Section 10, gap 1).
**Hypothesis:** Models trained on raw parameters plus derived physics features (HI, t8/5, CE, V/I) reach the same RMSE on bead geometry prediction with half the training samples compared to models trained on raw parameters alone.
**Mechanism:** Derived features encode prior knowledge of the relevant physical scalings, reducing the function class the ML model must search (PHOENIX framework; Li et al. 2025 hybrid Rosenthal-LSTM).

### H7 -- Pulsed-GMAW waveform descriptors matter more than mean current [OPEN]
**Impact:** For pulsed modes, mean current is a lossy summary; full waveform matters.
**Hypothesis:** A tree-ensemble regressor with features (I_peak, I_base, f, duty_cycle) will predict weld pool area in pulsed GMAW with >=15% lower MAE than a model using only mean current.
**Mechanism:** Droplet detachment and peak thermal loading are driven by peak-current transients, which the mean averages out (pulsed GMAW literature; Neuro-NSGA-II for pulsed GMAW).

### H8 -- TabPFN foundation-model surrogate matches hand-tuned XGBoost on small welding datasets [OPEN]
**Impact:** Removes per-dataset retraining overhead for HDR iteration speed.
**Hypothesis:** TabPFN in zero-shot mode matches or exceeds tuned XGBoost RMSE on weld quality regression datasets with <=300 samples, across >=5 benchmark datasets.
**Mechanism:** TabPFN's meta-learned prior covers the low-dimensional tabular regimes typical of welding experiments (Hollmann et al. 2023; literature review Section 7.2).

### H9 -- Gaussian process surrogates provide calibrated uncertainty critical for HDR exploration [OPEN]
**Impact:** Uncertainty quality governs acquisition-function effectiveness in Phase B.
**Hypothesis:** GPR with a Matern-5/2 kernel yields coverage probabilities within +/-5% of nominal for 95% credible intervals on held-out welding bead geometry data, where XGBoost quantile regression fails to achieve this calibration.
**Mechanism:** GPs provide analytically calibrated posteriors under correctly-specified priors; tree-ensemble quantile methods typically require conformal post-processing (Duggirala et al. 2024; literature review Section 3.3).

### H10 -- Multi-fidelity GP combining Rosenthal and FEA reduces experimental budget [OPEN]
**Impact:** Addresses literature review gap 4 (multi-fidelity integration).
**Hypothesis:** A bi-fidelity GP (cheap Rosenthal analytical + expensive refined FEA) reaches target RMSE on weld pool temperature prediction with 40% fewer high-fidelity samples than a single-fidelity baseline.
**Mechanism:** Co-kriging leverages the correlated bias structure between low- and high-fidelity physics models (Kennedy & O'Hagan 2000; attention-based multi-fidelity networks 2024).

---

## Phase B -- Parameter Window and Multi-Objective Optimisation

Phase B hypotheses drive the optimisation loop: finding parameter windows that maximise quality targets subject to defect and distortion constraints.

### H11 -- A process window exists that maximises UTS while bounding HAZ width below 3 mm [OPEN]
**Impact:** Directly actionable for structural-steel fabrication shops.
**Hypothesis:** For S355 carbon steel GMAW butt welds (thickness 10 mm), there exists a connected parameter window in (I, V, v) where UTS >= 500 MPa AND HAZ half-width <= 3 mm AND porosity < 1% by area.
**Mechanism:** Higher heat input increases UTS of the weld metal via reduced cooling-rate embrittlement, but beyond a threshold produces HAZ grain coarsening that increases HAZ width and degrades toughness (Easterling 1992; literature review Section 1.4).

### H12 -- NSGA-II finds a Pareto frontier dominating Taguchi-optimal points [OPEN]
**Impact:** Quantifies the gain from modern MOO vs classical DoE for welding.
**Hypothesis:** On a 3-objective GMAW optimisation (UTS, HAZ width, deposition rate), NSGA-II with an XGBoost surrogate produces a Pareto set that strictly dominates the Taguchi L27 optimum in at least 2 of 3 objectives simultaneously.
**Mechanism:** Taguchi's additive signal-to-noise analysis ignores interaction effects; NSGA-II searches the full interaction space (literature review Section 5.1 and 5.2; Mysliwiec et al. 2025).

### H13 -- Bayesian optimisation with PIK outperforms random search for sample-efficient exploration [OPEN]
**Impact:** Core HDR efficiency claim.
**Hypothesis:** Bayesian optimisation with a physics-informed kernel (Rosenthal-prior mean, Matern covariance) reaches the optimal UTS-HAZ trade-off with >=50% fewer experiments than random search and >=30% fewer than BO with a plain Matern kernel.
**Mechanism:** PIK embeds the known heat-input scaling in the prior mean, focusing acquisition away from physically unreasonable regions (npj Computational Materials 2021; literature review Section 5.3).

### H14 -- Optimal pulsed GMAW parameters exist at frequency-duty-cycle combinations absent from classical L16 designs [OPEN]
**Impact:** Identifies blind spots of orthogonal-array DoE.
**Hypothesis:** Continuous optimisation over (I_peak, I_base, f, delta) finds settings that improve the objective (UTS + alpha*penetration - beta*spatter) by >=10% over the best point in a matched L16 Taguchi grid on the same response surface.
**Mechanism:** Optimum interactions between frequency and duty cycle lie on continuous manifolds that discrete grids miss (pulsed GMAW literature).

### H15 -- Preheat can be halved without increasing cold-cracking risk for high-CE steels if travel speed is co-optimised [OPEN]
**Impact:** Productivity gain for thick-section welding without safety compromise.
**Hypothesis:** For a CE=0.5 steel, there exists a (T_preheat, v) combination where T_preheat <= 75 C AND t8/5 >= 10 s AND predicted cold-cracking probability (from trained classifier) <= 1%, whereas code-based preheat tables specify T_preheat >= 150 C.
**Mechanism:** Slowing travel speed increases heat input, compensating for lower preheat in the t8/5 cooling-time budget (Lancaster 1999; IIW cold-cracking literature).

### H16 -- Low-distortion parameter windows trade travel speed for multiple small passes [OPEN]
**Impact:** Enables distortion-controlled fabrication for large thin-wall structures.
**Hypothesis:** Multi-pass sequences with N_pass >= 4 and heat input per pass <= 0.6 kJ/mm reduce out-of-plane distortion by >=30% vs a single-pass weld of equivalent total heat input on the same joint geometry.
**Mechanism:** Distributed heat input across time and passes allows partial thermal relaxation and lower peak through-thickness gradients (literature review Section 4.4; FEA distortion studies).

### H17 -- Ternary Ar/CO2/O2 blend outperforms binary Ar/CO2 on galvanised steel quality objectives [OPEN]
**Impact:** Validates gas blend selection in HDR optimisation across shielding-gas categorical.
**Hypothesis:** For galvanised carbon steel GMAW, a ternary blend (e.g., 93 Ar / 5 CO2 / 2 O2) produces lower porosity AND lower spatter AND lower pitting count than any point in the binary Ar/CO2 space sampled at 5% resolution.
**Mechanism:** O2 stabilises the cathode spot on the zinc-coated surface, reducing porosity and pitting (literature review Section 2.2; ternary blend studies).

### H18 -- Inverse design of parameters from target bead geometry is tractable with conditional generative models [OPEN]
**Impact:** Addresses literature review gap 6 (inverse design underexplored).
**Hypothesis:** A conditional VAE trained on (parameters, bead geometry) pairs produces parameter suggestions that, when executed in the forward surrogate, hit the target bead width and penetration within +/-10% in >=80% of test targets.
**Mechanism:** CVAE latent space enables sampling-based inverse mapping that accommodates the one-to-many nature of inverse design (Journal of Laser Applications 2025 CVAE work; literature review Section 6.4 and 7).

### H19 -- Active learning with GPR surrogate halves the experiments needed to map a process window [OPEN]
**Impact:** Central HDR efficiency claim for small-sample welding optimisation.
**Hypothesis:** Active learning with uncertainty-based acquisition (BALD or maximum variance) on a GPR surrogate reaches >=95% classification accuracy on "in/out of process window" after <=50 experiments, vs 100+ experiments required by space-filling designs.
**Mechanism:** Uncertainty-guided sampling concentrates experiments along the decision boundary of the process window (Sauer et al. 2022; literature review Section 7.1).

### H20 -- Transfer learning from GMAW to GTAW cuts target data requirements by 60% [OPEN]
**Impact:** Addresses literature review gap 3 (cross-process transfer).
**Hypothesis:** A model pre-trained on GMAW bead geometry data and fine-tuned on GTAW (same steel grade) requires <=40% of the GTAW data to match the RMSE of a GTAW-only baseline.
**Mechanism:** Shared underlying thermal physics (heat input, cooling) creates transferable feature representations; process-specific offsets are small relative to the function class (literature review Section 3.5; CNN transfer work).

### H21 -- Multi-objective BO over (UTS, HAZ width, distortion, deposition rate) finds a knee point unreachable by sequential single-objective optimisation [OPEN]
**Impact:** Validates multi-objective BO as an HDR primitive.
**Hypothesis:** Multi-objective Bayesian optimisation (e.g., ParEGO or qNEHVI) identifies a knee-point solution on the 4D Pareto frontier with hypervolume >=20% larger than weighted-sum sequential optimisation under the same experimental budget.
**Mechanism:** Sequential weighted-sum optimisation misses concave regions of the Pareto front; multi-objective acquisition functions directly target hypervolume expansion (literature review Section 5.3 and Section 10 gap 10).

### H22 -- Explainable models (SHAP on XGBoost) recover physics-accepted parameter importance ranking [OPEN]
**Impact:** Trust and auditability for industrial HDR adoption.
**Hypothesis:** SHAP feature importance rankings from an XGBoost model trained on GMAW bead geometry agree with expert rankings (current > travel speed > voltage > WFR) in the top-4 features with >=75% rank correlation.
**Mechanism:** Correctly specified models should recover the 2.5x current-dominance empirically observed in welding literature (Lincoln Electric; literature review Section 9).

---

## Phase Roadmap

Phase A hypotheses (H1-H10) run first to establish feature representations and surrogate quality. Phase B hypotheses (H11-H22) then execute against the best Phase A pipeline. Each hypothesis produces a decision record; rejected hypotheses inform queue revision.

---

## References

See `papers.csv` for the full bibliography. Hypotheses reference: Kou (2003) [id=1], Lancaster (1999) [id=2], Easterling (1992) [id=3], Goldak et al. (1984) [id=4], Li et al. (2022) [id=11], Sarikhani & Pouranvari (2023) [id=14], Mysliwiec et al. (2025) [id=16], Hollmann et al. (2023) [id=46], Kennedy & O'Hagan (2000) [id=47], Sauer et al. (2022) [id=45], Duggirala et al. (2024) [id=19], Bayesian optimisation with PIK (npj 2021) [id=33, 98].
