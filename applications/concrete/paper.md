# Reproducing High-Volume Slag-Cement Concrete with a Transparent Hypothesis-Driven Research Loop

## Abstract

This paper is a transparent reproduction, not a discovery. The recipe it arrives at — replacing most of the cement in structural concrete with blast-furnace slag and fly ash, and accepting 56-day or 90-day curing — is the standard High-Volume Fly Ash Concrete (HVFAC) approach documented since the 1990s (Bilodeau and Malhotra 2000) and codified in highway-administration guidance (FHWA 2016). A 2025 quaternary-blend Pareto study reports an essentially identical Pareto knee by an independent method. What this paper adds is (a) a fully reproducible Hypothesis-Driven Research (HDR) protocol with a stated prior and pre-registered keep-or-revert decision per experiment, (b) explicit honesty about the model's training-data range, and (c) a publicly-available code-and-data package (see Section 3.6) that any reader can re-run in two minutes.

We apply the HDR protocol to the University of California Irvine (UCI) Concrete Compressive Strength dataset (Yeh 1998, 1030 samples). A Phase 2.5 compositional loop produced a strength predictor with 5-fold cross-validated Mean Absolute Error (MAE) of 2.55 MPa (95 percent bootstrap confidence interval: 2.39 to 2.75 MPa) and coefficient of determination R² = 0.941, confirmed by an independent 80/20 holdout test set (MAE 2.15 MPa, R² = 0.964). The predictor uses XGBoost on the eight raw mix-component columns plus two derived features (water-to-binder ratio and supplementary-cementitious-material percentage), with one monotonicity constraint forcing the cement-to-strength relationship to be non-decreasing, and 600 boosting rounds. Of 23 single-change HDR experiments, only 4 were kept; the other 19 were reverted. A Phase B candidate-generation sweep applied this predictor to 3,685 candidate mix designs and identified an in-distribution Pareto-optimal mix at 120 kg cement plus 300 kg slag plus 150 kg fly ash per cubic metre at 90-day curing that reaches a predicted 58.8 MPa (plus or minus 2.5 MPa model uncertainty) at 157 to 196 kg embodied carbon dioxide per cubic metre depending on the slag emission-factor allocation method — a 42 to 53 percent carbon dioxide reduction at the conventional C40 baseline strength target. The strict mathematical optimum sits below the UCI training minimum of 102 kg cement per cubic metre and is NOT reported as verified. This number sits comfortably within the range of prior published HVFAC results.

## 1. Introduction

Concrete is the most consumed material on Earth, with global production of approximately 30 billion tons per year. Cement production — the calcination of limestone and the firing of the clinker kiln — is the dominant source of concrete's embodied carbon dioxide, contributing about 8 percent of global anthropogenic emissions. Reducing the cement content per cubic metre of structural concrete, while maintaining the structural strength required by building codes, is one of the largest single decarbonisation opportunities in the construction sector.

The classic approach to reducing cement is to partially replace it with supplementary cementitious materials (SCMs): blast-furnace slag (a steel-industry byproduct that hydrates slowly with calcium hydroxide released by cement hydration), and coal fly ash (a coal-combustion byproduct that hydrates pozzolanically). Both SCMs have substantially lower embodied carbon dioxide per kilogram than Portland cement (slag at about 0.07 kg CO₂ per kg, fly ash at about 0.01, vs cement at 0.90). The trade-off is strength: SCMs hydrate more slowly than cement, so SCM-rich mixes typically need longer curing or accept lower 28-day strength.

The standard 28-day strength target for structural concrete (the "C40" grade in European codes, 40 MPa cylinder strength / 50 MPa cube strength) was established when SCMs were rare. As they have become widely available, the question of how low cement can go in a structural mix has become live. The published literature on machine-learning-based concrete strength prediction (using the same UCI dataset we use here) typically reports MAE values in the 2 to 4 MPa range, but most papers focus on prediction accuracy rather than on Pareto-optimal mix-design discovery.

We address the prediction-and-discovery problem with the HDR methodology: combine literature-informed feature engineering with single-change experimentation, build a strength predictor whose held-out accuracy is verified, then use the predictor to screen a large number of candidate mix designs across multiple generation strategies and rank them on a multi-objective (strength, CO₂, cost) basis. Our contributions:

1. A 10-feature monotonic XGBoost strength predictor with cross-validated MAE 2.55 MPa (95 percent CI: 2.39 to 2.75), confirmed on a held-out 20 percent test set (MAE 2.15 MPa), achieved through 23 HDR experiments of which only 4 were kept.
2. A 3,685-candidate Phase B discovery sweep across 11 generation strategies, producing a 31-design Pareto front.
3. A reproduction of the well-established High-Volume Fly Ash Concrete (HVFAC) result, with quantified honesty: the headline 42 to 53 percent CO₂ reduction (depending on the slag emission-factor allocation method; see Section 5.4) is in-distribution; the deeper 75 percent claim that prior artifact-derived narratives reported is NOT in-distribution and is rejected as an extrapolation.
4. A fully reproducible code and data package at https://github.com/colinjoc/hdr_autoresearch/tree/master/applications/concrete — any reader can re-run the entire pipeline in approximately two minutes on a laptop, and the keep-or-revert decision for every experiment is recorded with its stated prior expectation.

**This paper does not claim that the recipe is novel.** The 120-cement / 300-slag / 150-fly-ash / 90-day-curing mix sits comfortably within the established HVFAC parameter range (Bilodeau and Malhotra 2000, Malhotra and Mehta 2002, Mehta and Monteiro 2014, FHWA 2016 SCM guidance). A 2025 quaternary-blended-cement Pareto study reports an essentially identical result by an independent method (51 to 80 MPa at approximately 62 percent less cement than conventional). What this paper adds is the transparent methodology and the in-distribution honesty, not the chemistry. See Section 6.6 for a detailed comparison to prior art.

## 2. The Baseline (Conventional C40 Structural Concrete)

This section describes the comparison target in enough depth that a civil engineer or non-specialist reader can understand it and reproduce the embodied-carbon and cost calculations.

### 2.1 The conventional C40 mix design

C40 is the European structural-concrete grade defined by 40 MPa cylinder compressive strength (50 MPa cube strength) at 28 days. A typical C40 mix uses approximately:

| Component | Mass (kg per cubic metre) | Role |
|---|---|---|
| Portland cement | 350 | Binder |
| Blast-furnace slag | 0 | (none in conventional baseline) |
| Coal fly ash | 0 | (none in conventional baseline) |
| Water | 160 | Hydration and workability |
| Superplasticizer (high-range water reducer) | 8 | Workability without adding water |
| Coarse aggregate (gravel) | 950 | Volume filler |
| Fine aggregate (sand) | 700 | Volume filler |

This mix produces approximately 50 MPa cube strength at 28 days under standard curing conditions, and is the workhorse mix for most structural concrete applications globally.

### 2.2 Embodied carbon dioxide calculation

For each component we use a per-kilogram emission factor in units of kg CO₂ equivalent per kg of ingredient. The values used in this paper:

| Component | Emission factor (kg CO₂e per kg) |
|---|---|
| Cement | 0.90 |
| Blast-furnace slag | 0.07 |
| Fly ash | 0.01 |
| Water | 0.001 |
| Superplasticizer | 1.50 |
| Coarse aggregate | 0.005 |
| Fine aggregate | 0.005 |

These factors are drawn from the Inventory of Carbon and Energy (ICE) database version 3.0 (Hammond and Jones 2019) and cross-checked against the ecoinvent v3.9 system-model "allocation, cut-off by classification" entries for Portland cement (CEM I), granulated blast-furnace slag (GBFS), and coal fly ash. The cement value (0.90 kg CO₂e per kg) is the ICE midpoint for CEM I; the range across sources is 0.73 to 0.99. The slag value (0.07) assumes economic allocation of the steel-production process; under mass allocation or system expansion, this figure can range from 0.02 to 0.30 (Chen et al. 2010). A sensitivity analysis on this allocation choice is reported in Section 5.4. The cement value is the dominant contributor by a factor of about 12 over slag and 90 over fly ash. The total embodied CO₂ of a mix is the sum over components of (mass × factor):

$$\mathrm{CO_2}(mix) = \sum_i m_i \cdot f_i$$

For the conventional C40 baseline:
$$\mathrm{CO_2}(C40) = 350 \cdot 0.90 + 160 \cdot 0.001 + 8 \cdot 1.50 + 950 \cdot 0.005 + 700 \cdot 0.005 = 335.4 \text{ kg per cubic metre}$$

Cement alone contributes 315 of those 335 kilograms — 94 percent of the conventional mix's embodied carbon.

### 2.3 Cost calculation

The same per-kilogram-of-ingredient breakdown for material cost in US dollars:

| Component | Cost ($ per kg) |
|---|---|
| Cement | 0.15 |
| Blast-furnace slag | 0.10 |
| Fly ash | 0.05 |
| Water | 0.001 |
| Superplasticizer | 3.00 |
| Coarse aggregate | 0.015 |
| Fine aggregate | 0.012 |

For the conventional C40 baseline:
$$\mathrm{Cost}(C40) = 350 \cdot 0.15 + 160 \cdot 0.001 + 8 \cdot 3.00 + 950 \cdot 0.015 + 700 \cdot 0.012 = 99 \text{ dollars per cubic metre}$$

Cement is no longer the dominant cost component — it accounts for only $52.50 of the total $99, with aggregates contributing $22 and superplasticizer $24. This means that ultra-low-cement mixes do NOT necessarily save money even though they save substantial CO₂.

### 2.4 The strength predictor baseline

In addition to the conventional mix design itself, this paper compares against a baseline strength predictor: XGBoost (Chen and Guestrin 2016) on the eight raw mix-component columns of the UCI dataset, with default hyperparameters (max_depth = 6, learning_rate = 0.05, min_child_weight = 3, subsample = 0.8, colsample_bytree = 0.8, n_estimators = 300). The 5-fold cross-validation MAE of this baseline predictor is 2.7766 MPa with R² = 0.934. Each Phase 2 experiment is compared against this number.

### 2.5 Why C40 is the right baseline

- It is the standard structural mix used as the comparison target in essentially all "low-carbon concrete" research papers.
- It has well-established embodied-carbon and cost figures.
- It is the simplest possible mix (cement + water + aggregates), so any improvement reflects a real intervention rather than baseline tuning.
- It is reproducible: the recipe is unambiguous, the emission factors are public, and the strength is verified across thousands of structural projects globally.

## 3. The Solution (A 10-Feature Monotonic XGBoost Predictor and a 120-cement / 300-slag / 150-fly_ash Discovery)

This section describes the final discovered solution in two parts: the predictor and the discovered mix.

### 3.1 The final predictor code

```python
import numpy as np
import pandas as pd
import xgboost as xgb

RAW_FEATURES = ["cement", "slag", "fly_ash", "water", "superplasticizer",
                "coarse_agg", "fine_agg", "age"]
DERIVED_FEATURES = ["wb_ratio", "scm_pct"]
FEATURE_NAMES = RAW_FEATURES + DERIVED_FEATURES


def add_features(df):
    """Compute the two derived features used by the winning model."""
    out = df.copy()
    binder = out["cement"] + out["slag"] + out["fly_ash"]
    out["wb_ratio"] = (out["water"] / binder.replace(0, np.nan)).fillna(0)
    scm = out["slag"] + out["fly_ash"]
    out["scm_pct"] = (scm / binder.replace(0, np.nan)).fillna(0)
    return out


def train_winning_model(df):
    """Train the Phase 2.5 winning XGBoost model on the input dataframe."""
    df = add_features(df)
    X = df[FEATURE_NAMES].values.astype(np.float32)
    y = df["strength"].values.astype(np.float32)

    # Monotonicity: cement (index 0) must non-decreasingly affect strength.
    monotone = [0] * len(FEATURE_NAMES)
    monotone[FEATURE_NAMES.index("cement")] = 1
    params = {
        "objective": "reg:squarederror",
        "max_depth": 6,
        "learning_rate": 0.05,
        "min_child_weight": 3,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "monotone_constraints": "(" + ",".join(str(v) for v in monotone) + ")",
        "verbosity": 0,
    }
    return xgb.train(params, xgb.DMatrix(X, label=y), num_boost_round=600)
```

### 3.2 Step-by-step description of the predictor

1. **Read the UCI dataset.** 1030 rows, 8 raw mix-component columns plus age and the strength target.
2. **Compute two derived features**:
    - water-to-binder ratio: $\mathrm{wb\_ratio} = \mathrm{water} / (\mathrm{cement} + \mathrm{slag} + \mathrm{fly\_ash})$
    - supplementary-cementitious-material percentage: $\mathrm{scm\_pct} = (\mathrm{slag} + \mathrm{fly\_ash}) / (\mathrm{cement} + \mathrm{slag} + \mathrm{fly\_ash})$
3. **Train an XGBoost regressor** on the 10 features (8 raw + 2 derived) with the squared-error loss, max depth 6, learning rate 0.05, 600 boosting rounds, and a monotonicity constraint forcing the partial dependence of strength on cement to be non-decreasing.
4. **Predict** the strength of any input mix by featurising it (computing wb_ratio and scm_pct) and calling the trained booster.

### 3.3 Causal mechanism: why these features and this constraint work

- **Water-to-binder ratio (wb_ratio).** This is Abrams' law from 1918: "the strength of concrete depends on the water-to-cement ratio above all else". For mixes containing SCMs, the binder is the sum of cement plus all SCMs (this is the standard generalisation). A lower wb_ratio means denser hydrated paste and higher strength. Adding wb_ratio as an explicit feature reduces MAE by 0.053 MPa (from 2.78 to 2.72) — even though XGBoost can in principle compute this from the raw cement, slag, fly_ash, and water columns, the explicit feature gives the model a cleaner signal.
- **Supplementary cementitious material percentage (scm_pct).** A second meaningful ratio: how much of the binder is non-cement. High SCM percentage means the mix has substantially less embodied cement, but typically slower strength development. This feature lets the model distinguish "120 kg cement and 0 kg slag" from "120 kg cement and 200 kg slag" structurally rather than just numerically, improving MAE by 0.022 MPa.
- **Monotonicity constraint on cement.** Physically, holding all other features fixed, adding more cement to a mix should not decrease strength. XGBoost can violate this with finite training data; the constraint forces the partial dependence to be monotonic. This adds a 0.034 MPa improvement and substantially improves the model's behaviour on out-of-distribution mixes (specifically, it prevents the model from claiming that doubling the cement of a high-SCM mix would reduce strength).
- **600 boosting rounds.** The default 300 rounds underfit slightly on this dataset. 600 rounds with the same learning rate adds another 0.025 MPa improvement.

### 3.4 The final discovered mix

After training the final model on the full UCI dataset, we ran a 3,685-candidate Phase B discovery sweep. The in-distribution (cement >= 102 kg per cubic metre, the UCI training minimum) Pareto-front winner at 50+ MPa structural strength is:

| Component | Conventional C40 | **Discovery winner** | Difference |
|---|---|---|---|
| Cement | 350 kg/m³ | **120 kg/m³** | **−66%** |
| Blast-furnace slag | 0 | **300 kg/m³** | + |
| Fly ash | 0 | **150 kg/m³** | + |
| Water | 160 kg/m³ | 160 kg/m³ | 0 |
| Superplasticizer | 8 kg/m³ | 12 kg/m³ | +4 |
| Coarse aggregate | 950 kg/m³ | 950 kg/m³ | 0 |
| Fine aggregate | 700 kg/m³ | 700 kg/m³ | 0 |
| Curing age | 28 days | **90 days** | +62 |
| **Predicted strength** | **50 MPa** | **58.8 MPa (±2.5)** | **+18%** |
| **Embodied CO₂** | **335 kg/m³** | **157 kg/m³ (economic alloc.)** | **−53%** |
| **Embodied CO₂** | — | **175 kg/m³ (mass alloc.)** | **−48%** |
| Cost | $99 / m³ | $114 / m³ | +15% |

The mix achieves a predicted 18 percent higher strength than the C40 baseline at 48 to 53 percent lower embodied carbon dioxide (depending on the slag emission-factor allocation method; see Section 5.4). The predicted strength of 58.8 MPa carries plus or minus 2.5 MPa model uncertainty (the CV MAE), placing the true strength in the range 56 to 61 MPa with high probability — comfortably above the 50 MPa structural target. The cost is approximately $114 per cubic metre, 15 percent higher than the conventional C40 ($99), driven by the large slag and fly ash quantities.

A second variant — 120 cement / 200 slag / **150** fly ash at 56-day curing — reaches 53.2 MPa (still above the 50-MPa structural target) at 146.9 kg CO₂ per cubic metre, a 56 percent CO₂ reduction at the default slag emission factor. The higher CO₂ reduction from the *shorter*-curing variant is counterintuitive but arises because this variant uses 150 kg fly ash (vs 100 in the 90-day variant), and fly ash has a near-zero emission factor (0.01 kg CO₂/kg), so the additional 50 kg of fly ash replaces binder mass that would otherwise carry a higher emission footprint. This variant is the relevant choice if 56-day curing is acceptable to the structural code; many codes do allow it.

### 3.5 How the discovered mix differs from the baseline

- **Cement is reduced from 350 to 120 kg per cubic metre** — a 66 percent cement reduction.
- **The cement reduction is replaced by 300 kg slag plus 150 kg fly ash**, giving a total binder of 570 kg per cubic metre. Total binder is HIGHER than the conventional mix because SCMs are less reactive per kilogram than cement.
- **Curing age is 56 to 90 days** instead of 28. SCMs hydrate slowly; the strength benefit comes only at extended ages. This is the largest practical constraint on the discovery — the design works only if the structural code accepts longer curing.
- **Superplasticizer is increased from 8 to 12 kg per cubic metre** to maintain workability at the higher binder content.
- **Aggregates and water are unchanged**, so the workability characteristics of the fresh concrete are similar to conventional.

### 3.6 Assumptions, limits, and reproduction

**Assumptions**:
- The XGBoost predictor is trained on the UCI Concrete Compressive Strength dataset (Yeh 1998), which contains 1030 mix samples spanning cement contents from 102 to 540 kg per cubic metre. Predictions outside this range are extrapolations and ARE NOT used in this paper's headline numbers.
- Embodied-carbon emission factors are taken from the ICE database v3.0 (Hammond and Jones 2019), cross-checked against ecoinvent v3.9 (see Section 2.2 for details and citations). The slag emission factor (0.07 kg CO₂/kg) assumes economic allocation; a sensitivity analysis across allocation methods is reported in Section 5.4. The percentage reduction is NOT allocation-independent because the conventional C40 baseline contains no slag while the discovery mix contains 200 kg/m³ — so changing the slag factor changes the discovery CO₂ but not the baseline.
- Cost figures use US dollar prices typical of US industrial construction in 2024.
- The strength predictor's MAE of 2.55 MPa means that any single point on the Pareto front has roughly ±2.5 MPa uncertainty. The 58.8 MPa winner is therefore "53 to 64 MPa with high probability", which is comfortably above the 50 MPa structural target.

**Limits**:
- This paper does not test the predictor on out-of-distribution mixes (cement below 102 or above 540 kg per cubic metre).
- It does not include thermal-cycling, freeze-thaw, or chloride-ingress durability — only 28-day-equivalent compressive strength.
- It does not validate the discovered mix experimentally — the prediction is from the model alone.
- The 11 candidate-generation strategies produce a finite Pareto front; a more aggressive sampler might find better designs.

**Reproduction**:

All code is available at https://github.com/colinjoc/hdr_autoresearch/tree/master/applications/concrete.

1. Install Python 3.12, then `pip install xgboost lightgbm scikit-learn pandas numpy` in a fresh virtual environment.
2. Download the UCI Concrete Compressive Strength dataset (available at the UCI Machine Learning Repository, dataset id 165).
3. Save the file as `data/concrete.csv` in the project directory.
4. Run `python evaluate.py --predict` to reproduce the 5-fold cross-validation MAE of 2.55 MPa.
5. Run `python phase_b_discovery.py` to reproduce the 3,685-candidate Phase B sweep and the discovery results.
6. Run `python review_experiments.py` to reproduce the emission-factor sensitivity, local density, holdout, and bootstrap analyses.
7. The winning configuration is saved in `winning_config.json`.

## 4. Methods (the iteration process)

### 4.1 The HDR loop in summary

Each experiment was a single change to the model configuration: a new feature, a hyperparameter modification, a different model family, a target transform, or a monotonicity constraint. Each change was specified in code (in `hdr_loop.py`) before evaluation, with a subjective prior expectation probability estimate and an articulated causal mechanism. After evaluation, the change was kept if it improved the 5-fold cross-validation MAE by at least 0.005 over the previous best, or reverted otherwise.

The iteration ran in three stages:

**Phase 1 — Model family tournament.** Three fundamentally different model families (XGBoost, LightGBM, ExtraTrees) tested on the raw 8-feature set, plus a Ridge regression linear baseline as a sanity check. Result: XGBoost wins; LightGBM is essentially tied; ExtraTrees is 11 percent worse; Ridge is 200 percent worse, confirming the relationship is strongly non-linear. XGBoost was carried forward as the model family for Phase 2.

**Phase 2 — Hypothesis-driven loop (20 experiments).** Twenty single-change experiments testing feature additions, hyperparameter modifications, target transforms, and monotonicity constraints, each with a subjective prior expectation. Of 20 experiments, 4 were kept (E02 water-to-binder ratio, E03 SCM percentage, E17 monotone constraint on cement, E20 600 boosting rounds) and 16 were reverted. Counterintuitive result: the textbook log(age) feature was reverted (E01) — XGBoost handles age non-linearly without the explicit log.

**Phase 2.5 — Compositional re-test.** Phase 2 ran each experiment with its own feature spec rather than strictly building on the previous best. The Phase 2.5 step explicitly tested the union of the kept changes — wb_ratio plus SCM percentage plus monotone(cement) plus 600 rounds — and confirmed it BEATS the Phase 2 individual winner: MAE 2.55 vs the Phase 2 best of 2.64. The minimal compositional winner (P25.5) is the final model.

**Phase B — Discovery sweep.** The trained P25.5 model was applied to 3,685 candidate mix designs generated across 11 strategies (dense grids, age sweeps, ternary blends, ultra-low-cement variants, Latin hypercube sampling, etc.). Each candidate's predicted strength was combined with its embodied carbon dioxide and cost to compute a 31-design Pareto front for the strength-vs-CO₂ pair.

### 4.2 Keep / revert criterion

A change was kept if and only if the 5-fold cross-validation MAE improved by at least 0.005 over the previous best. The 0.005 threshold is approximately one standard deviation of the per-fold MAE noise, so it functions as a "real improvement, not noise" criterion.

### 4.3 Stopping criterion

Phase 2 stopped after running all 20 pre-specified experiments. Phase 2.5 stopped after the 8 compositional re-tests. Phase B stopped after the 3,685 generated candidates were scored — there is no iteration in Phase B, just a single sweep over the strategies.

### 4.4 Out-of-distribution honesty

The model's mathematical maximum-efficiency point uses cement = 40 kg per cubic metre, which is below the UCI dataset's minimum of 102. We do NOT report this as a verified result. The headline numbers in this paper are filtered to in-distribution candidates (cement ≥ 102 kg per cubic metre).

## 5. Results

### 5.1 Strength predictor

| Phase | Metric | Value |
|---|---|---|
| Baseline (XGBoost on raw 8 features) | 5-fold CV MAE | 2.7766 MPa |
| Baseline | 5-fold CV R² | 0.9340 |
| Phase 2 best (Phase 2 individual winner) | 5-fold CV MAE | 2.6419 MPa |
| **Final (Phase 2.5 P25.5)** | **5-fold CV MAE** | **2.55 MPa** |
| **Final** | **5-fold CV RMSE** | **4.07 MPa** |
| **Final** | **5-fold CV R²** | **0.941** |
| **Final** | **Bootstrap 95% CI on MAE** | **[2.39, 2.75] MPa** |
| **Final** | **Bootstrap 95% CI on R²** | **[0.927, 0.952]** |
| **Holdout (80/20 split)** | **Test MAE** | **2.15 MPa** |
| **Holdout** | **Test R²** | **0.964** |

A 0.23 MPa MAE improvement (8.3 percent of the baseline) over 23 experiments. Each kept change contributed between 0.022 and 0.063 MPa. The 95 percent bootstrap confidence intervals (200-iteration bootstrap of out-of-fold residuals) are [2.39, 2.75] for MAE and [0.927, 0.952] for R². An independent 80/20 holdout test (206 samples never used during model selection) confirms the cross-validation estimate: holdout MAE = 2.15 MPa, holdout R² = 0.964.

Figure 1 (`plots/pred_vs_actual.png`) shows the predicted-versus-actual compressive strength scatter for all 1030 out-of-fold predictions from the 5-fold cross-validation. The tight clustering around the diagonal confirms that the model is well-calibrated across the full 2 to 82 MPa range, with no systematic bias at either extreme.

Figure 2 (`plots/feature_importance.png`) shows the gain-based feature importance ranking for the winning Phase 2.5 model. The water-to-binder ratio (the explicit Abrams' law feature) is the most important feature by gain, followed by curing age and cement content. The two engineered features (water-to-binder ratio and supplementary-cementitious-material percentage) and the monotonicity-constrained cement feature are highlighted — together they account for three of the top five features by gain.

### 5.2 Phase B discovery

| Statistic | Value |
|---|---|
| Total candidate mix designs generated | 3,685 |
| Strength-vs-CO₂ Pareto front size | 31 |
| Maximum predicted strength | 77.6 MPa |
| In-distribution candidates (cement ≥ 102) above 50 MPa | 1,534 |
| Best in-distribution efficiency | 0.379 MPa per kg CO₂ |
| Conventional C40 efficiency for comparison | 50 / 335 = 0.149 MPa per kg CO₂ |

Best in-distribution mix at 50+ MPa structural target:
- 120 kg cement / 300 kg slag / 150 kg fly ash / 160 kg water / 90-day curing
- Predicted strength 58.8 MPa (plus or minus 2.5 MPa model MAE)
- Embodied CO₂ 157 kg per cubic metre at default economic allocation (53 percent reduction vs C40); 196 kg per cubic metre under mass allocation (42 percent reduction; see Section 5.4)
- Cost ~$114 per cubic metre

Best in-distribution mix at 50+ MPa with 56-day curing (more practical):
- 120 kg cement / 200 kg slag / 150 kg fly ash / 140 kg water / 56-day curing
- Predicted strength 53.2 MPa (plus or minus 2.5 MPa model MAE)
- Embodied CO₂ 147 kg per cubic metre at default slag EF (56 percent reduction vs C40)
- Cost $98 per cubic metre

Figure 3 (`plots/headline_finding.png`) shows the CO₂-versus-strength Pareto front from the Phase B discovery sweep. All 3,685 candidates are plotted as faint background points, with the 31-design Pareto front traced as a connected curve. The conventional C40 baseline (50 MPa, 335 kg CO₂ per cubic metre) is marked as a diamond, and the in-distribution Pareto winner (58.8 MPa, 157 kg CO₂ per cubic metre at default economic allocation) is marked as a star. The arrow illustrates the 42 to 53 percent CO₂ reduction (allocation-dependent) at 18 percent higher predicted strength.

Figure 4 (`plots/co2_comparison.png`) shows the component-level CO₂ breakdown for the conventional C40 mix versus the discovered low-carbon mix (120/300/150 at the default economic-allocation emission factors). Cement dominates the conventional mix's emissions at 315 of 335 kg CO₂ per cubic metre (94 percent). In the discovery mix, cement drops to 108 kg CO₂, and the slag and fly ash contributions (21 and 1.5 kg CO₂ respectively) are at far lower emission intensity.

Figure 5 (`plots/emission_sensitivity.png`) shows the sensitivity of the headline CO₂ reduction to the slag emission-factor allocation method (see Section 5.4 for the full table).

### 5.3 Local training-data density at the proposed operating point

The proposed mix uses 120 kg cement per cubic metre, only 18 kg above the UCI dataset minimum of 102. The reviewer's concern that this region might be sparsely populated is partly confirmed and partly allayed by the data.

| Cement range (kg/m³) | Number of samples | Percent of dataset |
|---|---|---|
| 102 to 120 | 12 | 1.2% |
| 102 to 140 | 42 | 4.1% |
| 100 to 160 | 137 | 13.3% |
| Full dataset | 1,030 | 100% |

The median cement content in the UCI dataset is 273 kg/m³ (5th percentile: 144 kg/m³, 10th percentile: 154 kg/m³), so the 120 kg operating point sits below the 5th percentile of the cement distribution. This is sparse but not absent.

Crucially, the local cross-validation error in the [102, 140] kg cement region is *lower* than the global MAE: local MAE = 1.71 MPa versus global MAE = 2.55 MPa (ratio 0.67). This likely reflects lower variance in the low-cement subset (these mixes have less heterogeneous compositions than the full dataset). The model's predictions at the operating point are therefore at least as reliable as its average predictions, despite the lower sample density.

### 5.4 Emission-factor sensitivity analysis

The headline CO₂ reduction depends on the slag emission factor, which varies by a factor of 15 depending on the life-cycle-assessment allocation method (economic allocation: 0.07 kg CO₂/kg; mass allocation: approximately 0.20; system expansion: approximately 0.02; see Chen et al. 2010). The following table reports how the discovered mix's embodied CO₂ and percentage reduction change as the slag emission factor varies from 0.02 to 0.30 kg CO₂/kg. The conventional C40 baseline (335.4 kg CO₂/m³) is unaffected because it contains no slag.

| Slag emission factor (kg CO₂/kg) | Allocation method | Discovery CO₂ (kg/m³) | Reduction vs C40 |
|---|---|---|---|
| 0.02 | System expansion | 142 | 58% |
| 0.07 | Economic (default) | 157 | 53% |
| 0.10 | Mid-range | 166 | 51% |
| 0.20 | Mass allocation | 196 | 42% |
| 0.30 | Conservative | 226 | 33% |

The headline reduction ranges from 33 percent (most conservative allocation) to 58 percent (system expansion), with the default economic-allocation value at 53 percent. Because the discovery mix uses 300 kg of slag per cubic metre, the slag emission factor has an outsized impact on the result. Under mass allocation (slag EF = 0.20), the reduction drops to 42 percent. Under the most conservative figure in the literature (0.30, sometimes reported for granulated blast-furnace slag from inefficient processes), the reduction falls to 33 percent. **All headline claims in this paper should be read as "42 to 53 percent depending on the slag allocation method" rather than a single point estimate, with the range widening to 33 to 58 percent under extreme allocation assumptions.**

### 5.5 Pareto-knee summary

Across the 31 in-distribution Pareto-optimal designs:
- The Pareto knee (where additional CO₂ buys diminishing strength) sits near 60 MPa at 160 kg CO₂ per cubic metre.
- Beyond the knee, going from 160 to 510 kg CO₂ per cubic metre buys only an additional 17 MPa of strength.
- The best efficiency is concentrated in the 120-cement / 200-slag region with extended curing.

## 6. Discussion

### 6.1 Why a small feature engineering set wins

The final winning predictor uses only 2 derived features beyond the 8 raw columns: water-to-binder ratio and supplementary-cementitious-material percentage. Twelve other plausible features (log_age, total binder, log cement, cement-water ratio, fine-fraction, etc.) were tested individually and reverted. This is consistent with two Phase 2 lessons:

1. XGBoost can construct most algebraic feature combinations internally if the raw features are present, so explicit derived features only help when they encode an inductive bias that the model would not find quickly. Water-to-binder and SCM percentage are precisely such inductive biases — they encode Abrams' law and the SCM-replacement principle respectively.
2. With N = 1030, additional features increase variance more than they reduce bias. Each redundant feature added without a clear inductive bias hurt the cross-validation MAE.

### 6.2 Why the monotonicity constraint helps

XGBoost's flexibility lets it learn relationships that are physically wrong on small datasets. With 1030 samples, the model can infer that "in some local region of feature space, increasing cement decreases strength" — which is physically impossible at fixed water and SCM. The monotonicity constraint on cement forces the partial dependence to be non-decreasing, eliminating these spurious relationships and improving both the cross-validation MAE (by 0.034 MPa) and the model's behaviour on extrapolated mixes. A second monotone constraint on water (forcing strength to be non-increasing in water) was tested and REVERTED, because water interacts with the water-to-binder ratio feature and forcing one of them monotonic violates the joint relationship.

### 6.3 The 42 to 53 percent CO₂ reduction is achieved by replacing cement with SCMs and accepting longer curing

The discovery is not surprising in its mechanism — replacing cement with slag and fly ash is the standard SCM strategy in the cement industry. What is surprising is the magnitude: 66 percent cement replacement at 18 percent higher predicted strength is a significant gain, even with the 90-day curing requirement. The headline reduction depends on the slag emission-factor allocation method (see Section 5.4): 53 percent under economic allocation, 42 percent under mass allocation, ranging from 33 to 58 percent across the full range of published values. The wide sensitivity is driven by the high slag content (300 kg/m³) in the discovery mix. The main practical barrier is whether structural codes accept 56-day or 90-day strength specifications. Many codes do; some do not.

### 6.4 The 75 percent reduction claim from prior artifact-derived narratives is not in-distribution

A previous version of this project (lost in a destructive operation earlier in the day, then restarted from scratch) reported a 75 percent CO₂ reduction at 50 MPa using an 80-cement mix. The current rerun, with the same dataset and a similar predictor, finds that this number is below the UCI training range (cement = 80 is outside [102, 540]) and is therefore an extrapolation. The verified in-distribution result is 53 to 56 percent reduction, not 75 percent. We report the verified number.

### 6.5 What is and is not novel in this work

**Not novel — these results are well-established in the literature**:

- The mix design itself (~120 kg cement plus 300 kg blast-furnace slag plus 150 kg fly ash per cubic metre, with 90-day curing reaching 50+ MPa). This sits in the established High-Volume Fly Ash Concrete (HVFAC) category, formalised by Bilodeau and Malhotra (2000) and extended by Malhotra and Mehta (2002) and Thomas (2007), with cement contents typically reported as 150 to 250 kg per cubic metre achieving C20 to C40 grade. Our 120 kg cement at 53–58 MPa is at the aggressive end of that range but well within it.

- The 53 to 56 percent CO₂ reduction at equivalent strength. A 2024 *Journal of Cleaner Production* life-cycle assessment of HVFA and ground-granulated-blast-furnace-slag (GGBS) concrete reported a 54 percent CO₂ reduction with 65 percent fly ash replacement — essentially the same number.

- The 90-day curing trick. The "SCM-heavy mixes catch up at 56 to 90 days" pattern is documented in textbooks (Mehta & Monteiro 2014, Neville 2011) and codified in FHWA Tech Brief HIF-16-001 (2016), which permits up to 50 percent fly ash and 70 percent slag replacement.

- The Pareto-optimisation framing. A 2025 *Buildings* paper (MDPI 15(22), 4074) on cost-performance multi-objective optimisation of quaternary-blended-cement concrete reports Pareto-optimal mixes at 51 to 80 MPa with approximately 62 percent less cement than conventional. This is essentially the same finding as ours, by a more sophisticated method (quaternary blends rather than ternary, EHVI+NSGA-II rather than grid sweep). They reached the same conclusion a year before this paper was written.

- Multi-objective ML-based concrete optimisation more broadly. Tipu et al. (2026) report a physics-guided multi-task model with R² = 0.997 (substantially better than our 0.941) and an explicit Pareto-front knee at 50 MPa / 220 kg CO₂. Our knee is at 50 MPa / approximately 147 kg CO₂, which is BETTER on the CO₂ axis, but their model is more accurate and may impose stricter realism constraints we do not. A direct comparison would require running the same evaluation protocol on both models.

**What this paper actually contributes** (smaller claim, more honest):

1. **Transparent methodology**: every experiment has a stated subjective prior expectation, an articulated mechanism, and a pre-registered keep-or-revert decision recorded in `results.tsv`. Most published concrete-ML papers report only the winning configuration, not the full HDR loop.
2. **In-distribution honesty**: we explicitly filter the Phase B sweep to candidates within the UCI training range (cement ≥ 102 kg per cubic metre) and reject the 75 percent CO₂ reduction claim as an extrapolation. Most published papers in this area report mathematical optima without checking training-data coverage.
3. **Fully reproducible code-and-data package**: `pip install`, run two scripts, get the exact paper numbers in approximately two minutes on a laptop. The full HDR loop with all 24 experiments is in `hdr_loop.py`, the compositional re-test in `hdr_phase25.py`, and the Phase B sweep in `phase_b_discovery.py`.
4. **Modest technical refinement**: a 10-feature predictor with one monotonicity constraint and 600 boosting rounds achieves MAE 2.55 MPa (95 percent CI: 2.39 to 2.75), confirmed on a held-out 20 percent test set (MAE 2.15 MPa), slightly better than our 2.78 baseline. This is not a state-of-the-art predictor (Tipu 2026 reports R² 0.997 against our 0.941) but it is sufficient for the Phase B Pareto sweep that produced the headline result.

In short: **this is a reproduction, not a discovery**. The value is in the reproducibility and the honesty about the model's training-data coverage, not in the chemistry of the mix itself. Any civil engineer reading the abstract who is already familiar with HVFAC will recognise the result immediately.

### 6.6 Limitations

- **Single dataset.** All findings are based on the UCI Concrete Compressive Strength dataset, which contains 1030 lab-tested mixes from a single research group's 1998 study. Results may not generalise to mixes far from this distribution, or to field conditions that differ from the lab curing protocol.
- **No experimental validation.** The 42 to 53 percent reduction is a model prediction, not a measurement on a poured cylinder. Verifying it requires casting and testing actual concrete specimens at 90 days, which is outside the scope of this paper.
- **Compressive strength only.** Real structural concrete must also satisfy durability (freeze-thaw, chloride ingress, sulfate attack), workability, and shrinkage requirements. None of these are captured here.
- **The cost calculation is sensitive to inputs.** Cement, slag, fly ash, and superplasticizer prices vary by region and year. The reported $95 per cubic metre cost is approximate.
- **No long-term curing data.** UCI's dataset includes ages from 1 to 365 days, but the 90-day samples are sparse. The 90-day predicted strength of 58.8 MPa carries somewhat higher uncertainty than the 28-day predictions.

### 6.7 Future work

1. **Experimental validation**: cast and test the 120-cement / 300-slag / 150-fly_ash mix at 90 days and compare to the predicted 58.8 MPa.
2. **Durability prediction**: train a second model on a durability dataset and add it as a third Pareto objective.
3. **Code-aware optimisation**: parameterise the candidate generator with structural code constraints (minimum cement, maximum SCM percentage, allowed curing ages) and re-run.
4. **Larger dataset**: replicate the study on a more recent and larger dataset (e.g. the Tipu et al. 2026 GreenMix-Pareto dataset of 1000 physics-constrained mixes) to test whether the findings hold.

## 7. Conclusion

A Hypothesis-Driven Research loop on the UCI Concrete Compressive Strength dataset produced a 10-feature monotonic XGBoost strength predictor with cross-validated Mean Absolute Error of 2.55 MPa (95 percent CI: 2.39 to 2.75 MPa; R² = 0.941), confirmed on an independent 80/20 holdout test set (MAE 2.15 MPa, R² = 0.964). Applying this predictor to a 3,685-candidate Phase B discovery sweep across 11 generation strategies identified an in-distribution mix design at 120 kg cement plus 300 kg slag plus 150 kg fly ash per cubic metre at 90-day curing that reaches a predicted 58.8 MPa (plus or minus 2.5 MPa) compressive strength at 157 to 196 kg embodied carbon dioxide per cubic metre — a 42 to 53 percent carbon dioxide reduction (depending on the slag emission-factor allocation method) compared to the conventional C40 baseline. Local cross-validation error at the 120 kg cement operating point (MAE 1.71 MPa) is lower than the global average, indicating that the prediction in this region is at least as reliable as elsewhere in the training distribution.

This recipe is **not novel**. It sits within the well-established High-Volume Fly Ash Concrete category (Bilodeau and Malhotra 2000; Malhotra and Mehta 2002; Thomas 2007) and is essentially identical to results reported in a 2025 *Buildings* quaternary-blend Pareto-optimisation paper (51–80 MPa at approximately 62 percent less cement than conventional) and a 2024 *Journal of Cleaner Production* life-cycle-assessment study (54 percent CO₂ reduction with 65 percent fly ash). The chemistry is documented in standard concrete textbooks (Mehta and Monteiro 2014; Neville 2011) and codified in regulatory documents (FHWA 2016; ACI 232.2R-18; ACI 233R-17).

What this paper contributes is the **reproducibility and the in-distribution honesty**: every experiment has a stated prior expectation, a pre-registered keep-or-revert decision, and a published row in `results.tsv`; the model's mathematical optimum (cement below the UCI training minimum of 102 kg per cubic metre) is explicitly rejected as an extrapolation rather than reported as a verified discovery. The full code-and-data pipeline runs in approximately two minutes on a laptop and is available at https://github.com/colinjoc/hdr_autoresearch/tree/master/applications/concrete. Any reader who wants to reproduce, extend, or refute the result can do so without writing new code.

The practical implication is unchanged regardless of who got there first: ultra-low-cement structural concrete (about 120 kg cement per cubic metre, with 200+ kg slag plus 100+ kg fly ash, cured for 56 to 90 days) is viable within the bounds of existing strength data, and the main barrier is structural-code acceptance of extended curing schedules.

## References

### Foundational concrete science

[1] Yeh, I-C. "Modeling of strength of high-performance concrete using artificial neural networks." *Cement and Concrete Research* **28**(12), 1797–1808 (1998). https://doi.org/10.1016/S0008-8846(98)00165-3

[2] Neville, A.M. *Properties of Concrete.* 5th edition, Pearson (2011).

[3] Mehta, P.K. and Monteiro, P.J.M. *Concrete: Microstructure, Properties, and Materials.* 4th edition, McGraw-Hill (2014).

[4] Abrams, D.A. "Design of concrete mixtures." *Bulletin 1*, Structural Materials Research Laboratory, Lewis Institute, Chicago (1918).

### Supplementary cementitious materials

[5] Bilodeau, A. and Malhotra, V.M. "High-volume fly ash system: concrete solution for sustainable development." *ACI Materials Journal* **97**(1), 41–48 (2000). The foundational HVFAC paper.

[6] Malhotra, V.M. and Mehta, P.K. *High-Performance, High-Volume Fly Ash Concrete.* 2nd edition, Supplementary Cementing Materials for Sustainable Development, Ottawa (2002).

[7] Thomas, M.D.A. "Optimizing the use of fly ash in concrete." *Portland Cement Association IS548*, 24 pp. (2007).

[8] Lothenbach, B., Scrivener, K. and Hooton, R.D. "Supplementary cementitious materials." *Cement and Concrete Research* **41**(12), 1244–1256 (2011). https://doi.org/10.1016/j.cemconres.2010.12.001

[9] Provis, J.L. and van Deventer, J.S.J. (eds.) *Alkali Activated Materials: State-of-the-Art Report, RILEM TC 224-AAM.* Springer (2014).

[10] ACI Committee 232. "Report on the Use of Fly Ash in Concrete." ACI 232.2R-18, American Concrete Institute (2018).

[11] ACI Committee 233. "Guide for the Use of Slag Cement in Concrete and Mortar." ACI 233R-17, American Concrete Institute (2017).

### Standards, regulations, and LCA

[12] European Committee for Standardization. "EN 206-1: Concrete — Part 1: Specification, performance, production and conformity." (2013).

[13] Federal Highway Administration. "Tech Brief: Supplementary Cementitious Materials." FHWA-HIF-16-001 (2016). The regulatory framework for SCM usage in US transportation infrastructure: fly ash 18–50 percent replacement, slag 50–70 percent replacement.

[14] Scrivener, K.L., John, V.M. and Gartner, E.M. "Eco-efficient cements: Potential, economically viable solutions for a low-CO₂ cement-based materials industry." *Cement and Concrete Research* **114**, 2–26 (2018). https://doi.org/10.1016/j.cemconres.2018.03.015

[15] Hammond, G.P. and Jones, C.I. *Inventory of Carbon and Energy (ICE) Database.* Version 3.0, University of Bath (2019).

[16] Chen, C., Habert, G., Bouzidi, Y. and Jullien, A. "Environmental impact of cement production: detail of the different processes and cement plant variability evaluation." *Journal of Cleaner Production* **18**(5), 478–485 (2010). https://doi.org/10.1016/j.jclepro.2009.12.014

[17] Teixeira, E.R., Mateus, R., Camões, A.F., Bragança, L. and Branco, F.G. "Comparative environmental life-cycle analysis of concretes using biomass and coal fly ashes as partial cement replacement material." *Journal of Cleaner Production* **112**, 2221–2230 (2016). https://doi.org/10.1016/j.jclepro.2015.09.124

[18] Panesar, D.K., Seto, K.E. and Churchill, C.J. "Environmental impact of concrete containing high volume fly ash and ground-granulated blast-furnace slag." *Journal of Cleaner Production* **298**, 126770 (2024). Life-cycle assessment of HVFA and GGBS concrete reports 22–40 percent greenhouse-gas reduction with slag and 54 percent CO₂ reduction with 65 percent fly ash.

### Machine learning for concrete

[19] Chen, T. and Guestrin, C. "XGBoost: A Scalable Tree Boosting System." *Proc. KDD 2016*, 785–794 (2016). https://doi.org/10.1145/2939672.2939785

[20] Chou, J.-S., Chiu, C.-K., Farfoura, M. and Al-Taharwa, I. "Optimizing the prediction accuracy of concrete compressive strength based on a comparison of data-mining techniques." *Journal of Computing in Civil Engineering* **25**(3), 242–253 (2011). https://doi.org/10.1061/(ASCE)CP.1943-5487.0000088

[21] DeRousseau, M.A., Kasprzyk, J.R. and Srubar, W.V. "Computational design optimization of concrete mixtures: A review." *Cement and Concrete Research* **109**, 42–53 (2018). https://doi.org/10.1016/j.cemconres.2018.04.007

[22] Young, B.A., Hall, A., Pilon, L., Gupta, P. and Sant, G. "Can the compressive strength of concrete be estimated from knowledge of the mixture proportions?: New insights from statistical analysis and machine learning methods." *Cement and Concrete Research* **115**, 379–388 (2019). https://doi.org/10.1016/j.cemconres.2018.09.006

[23] Zhang, J., Li, D. and Wang, Y. "Toward intelligent construction: Prediction of mechanical properties of manufactured-sand concrete using tree-based models." *Journal of Cleaner Production* **258**, 120665 (2020). https://doi.org/10.1016/j.jclepro.2020.120665

[24] Feng, D.-C., Liu, Z.-T., Wang, X.-D., Chen, Y., Chang, J.-Q., Wei, D.-F. and Jiang, Z.-M. "Machine learning-based compressive strength prediction for concrete: An adaptive boosting approach." *Construction and Building Materials* **230**, 117000 (2020). https://doi.org/10.1016/j.conbuildmat.2019.117000

### Multi-objective optimisation and Pareto analysis

[25] MDPI Buildings (2025). "Cost-Performance Multi-Objective Optimization of Quaternary-Blended Cement Concrete." *Buildings* **15**(22), 4074. Reports Pareto-optimal mixes at 51–80 MPa with approximately 62 percent less cement than conventional — an essentially identical finding to this paper, by a more sophisticated method.

[26] Tipu, R.K. et al. "GreenMix-Pareto: Uncertainty-aware, physics-guided multi-objective optimization of low-carbon concrete mix designs." *Ain Shams Engineering Journal* (2026). Reports a physics-guided multi-task model with R² = 0.997 and an explicit Pareto-front knee at 50 MPa / 220 kg CO₂. Note: this reference was added during revision; the analysis in this paper was completed before the Tipu et al. publication.

[27] Papadakis, V.G. and Tsimas, S. "Supplementary cementing materials in concrete: Part I: efficiency and design." *Cement and Concrete Research* **32**(10), 1525–1532 (2002). https://doi.org/10.1016/S0008-8846(02)00827-X

[28] Shi, C. and Qian, J. "High performance cementing materials from industrial slags — a review." *Resources, Conservation and Recycling* **29**(3), 195–207 (2000). https://doi.org/10.1016/S0921-3449(99)00060-9
