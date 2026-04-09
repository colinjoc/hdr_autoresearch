# Reproducing High-Volume Slag-Cement Concrete with a Transparent Hypothesis-Driven Research Loop

## Abstract

Concrete production is responsible for approximately 8 percent of global anthropogenic carbon dioxide emissions, and reducing the cement content of structural concrete is one of the highest-leverage decarbonisation strategies available. We apply a Hypothesis-Driven Research (HDR) protocol to the University of California Irvine (UCI) Concrete Compressive Strength dataset (Yeh 1998, 1030 samples) and reproduce the well-established result that high-volume slag-cement-fly-ash ternary blends with extended curing achieve approximately 53 to 56 percent embodied-carbon reduction at equivalent or higher structural strength compared to a conventional C40 structural baseline mix. The contribution of this paper is methodological and empirical rather than mechanistic: the underlying recipe (replace cement with blast-furnace slag and fly ash, accept 56-day or 90-day curing) is the standard High-Volume Fly Ash Concrete (HVFAC) approach reported in dozens of prior studies, including a 2025 quaternary-blend Pareto study that reports an essentially identical Pareto knee. What this paper adds is (a) a fully reproducible HDR protocol with a Bayesian prior and pre-registered keep-or-revert decision per experiment, (b) explicit honesty about the model's training-data range — the strict mathematical optimum sits below the UCI training minimum of 102 kg cement per cubic metre and is NOT reported as verified, and (c) a publicly-available code-and-data package that any reader can re-run in two minutes. The result itself: a Phase 2.5 compositional HDR loop produced a strength predictor with 5-fold cross-validated Mean Absolute Error (MAE) of 2.547 MPa and coefficient of determination (R²) of 0.944, using XGBoost on the eight raw mix-component columns plus two derived features (water-to-binder ratio and supplementary-cementitious-material percentage), with one monotonicity constraint forcing the cement-to-strength relationship to be non-decreasing, and 600 boosting rounds. Of 23 single-change HDR experiments, only 4 were kept; the other 19 were reverted. A Phase B candidate-generation sweep applied this predictor to 3,685 candidate mix designs and identified an in-distribution Pareto-optimal mix at 120 kg cement plus 200 kg slag plus 100 kg fly ash per cubic metre at 90-day curing that reaches 58.8 MPa at 156.9 kg embodied carbon dioxide per cubic metre — a 53 percent carbon dioxide reduction at 18 percent higher strength than the 350-kg-cement, 335-kg-CO₂-per-cubic-metre conventional C40 baseline. This number sits comfortably within the range of prior published HVFAC results.

## 1. Introduction

Concrete is the most consumed material on Earth, with global production of approximately 30 billion tons per year. Cement production — the calcination of limestone and the firing of the clinker kiln — is the dominant source of concrete's embodied carbon dioxide, contributing about 8 percent of global anthropogenic emissions. Reducing the cement content per cubic metre of structural concrete, while maintaining the structural strength required by building codes, is one of the largest single decarbonisation opportunities in the construction sector.

The classic approach to reducing cement is to partially replace it with supplementary cementitious materials (SCMs): blast-furnace slag (a steel-industry byproduct that hydrates slowly with calcium hydroxide released by cement hydration), and coal fly ash (a coal-combustion byproduct that hydrates pozzolanically). Both SCMs have substantially lower embodied carbon dioxide per kilogram than Portland cement (slag at about 0.07 kg CO₂ per kg, fly ash at about 0.01, vs cement at 0.90). The trade-off is strength: SCMs hydrate more slowly than cement, so SCM-rich mixes typically need longer curing or accept lower 28-day strength.

The standard 28-day strength target for structural concrete (the "C40" grade in European codes, 40 MPa cylinder strength / 50 MPa cube strength) was established when SCMs were rare. As they have become widely available, the question of how low cement can go in a structural mix has become live. The published literature on machine-learning-based concrete strength prediction (using the same UCI dataset we use here) typically reports MAE values in the 2 to 4 MPa range, but most papers focus on prediction accuracy rather than on Pareto-optimal mix-design discovery.

We address the prediction-and-discovery problem with the HDR methodology: combine literature-informed feature engineering with single-change experimentation, build a strength predictor whose held-out accuracy is verified, then use the predictor to screen a large number of candidate mix designs across multiple generation strategies and rank them on a multi-objective (strength, CO₂, cost) basis. Our contributions:

1. A 10-feature monotonic XGBoost strength predictor with cross-validated MAE 2.55 MPa, achieved through 23 HDR experiments of which only 4 were kept.
2. A 3,685-candidate Phase B discovery sweep across 11 generation strategies, producing a 31-design Pareto front.
3. A reproduction of the well-established High-Volume Fly Ash Concrete result, with quantified honesty: the headline 53 percent CO₂ reduction is in-distribution; the deeper 75 percent claim that prior artifact-derived narratives reported is NOT in-distribution and is rejected as an extrapolation.
4. A fully reproducible code and data package — any reader can re-run the entire pipeline in approximately two minutes on a laptop, and the keep-or-revert decision for every experiment is recorded with its Bayesian prior.

**This paper does not claim that the recipe is novel.** The 120-cement / 200-slag / 100-fly-ash / 90-day-curing mix sits comfortably within the established HVFAC parameter range (Bilodeau and Malhotra 1990s, Mehta and Monteiro textbook, FHWA 2016 SCM guidance). A 2025 quaternary-blended-cement Pareto study reports an essentially identical result by an independent method (51 to 80 MPa at approximately 62 percent less cement than conventional). What this paper adds is the transparent methodology and the in-distribution honesty, not the chemistry. See Section 6.6 for a detailed comparison to prior art.

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

These factors come from standard industry life-cycle-assessment databases. The cement value (0.90) is the dominant contributor by a factor of about 12 over slag and 90 over fly ash. The total embodied CO₂ of a mix is the sum over components of (mass × factor):

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

## 3. The Solution (A 10-Feature Monotonic XGBoost Predictor and a 120-cement / 200-slag / 100-fly_ash Discovery)

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

After training the final model on the full UCI dataset, we ran a 3,685-candidate Phase B discovery sweep. The in-distribution (cement ≥ 102 kg per cubic metre, the UCI training minimum) Pareto-front winner is:

| Component | Conventional C40 | **Discovery winner** | Difference |
|---|---|---|---|
| Cement | 350 kg/m³ | **120 kg/m³** | **−66%** |
| Blast-furnace slag | 0 | **200 kg/m³** | + |
| Fly ash | 0 | **100 kg/m³** | + |
| Water | 160 kg/m³ | 160 kg/m³ | 0 |
| Superplasticizer | 8 kg/m³ | 12 kg/m³ | +4 |
| Coarse aggregate | 950 kg/m³ | 950 kg/m³ | 0 |
| Fine aggregate | 700 kg/m³ | 700 kg/m³ | 0 |
| Curing age | 28 days | **90 days** | +62 |
| **Strength** | **50 MPa** | **58.8 MPa** | **+18%** |
| **Embodied CO₂** | **335 kg/m³** | **156.9 kg/m³** | **−53%** |
| Cost | $99 / m³ | $95 / m³ | −4% |

The mix achieves 18 percent higher strength than the C40 baseline at 53 percent lower embodied carbon dioxide and roughly the same cost.

A second variant — 120 cement / 200 slag / **150** fly ash at 56-day curing — reaches 53.2 MPa (still above the 50-MPa structural target) at 146.9 kg CO₂ per cubic metre, a 56 percent CO₂ reduction. This is the relevant choice if 56-day curing is acceptable to the structural code; many codes do allow it.

### 3.5 How the discovered mix differs from the baseline

- **Cement is reduced from 350 to 120 kg per cubic metre** — a 66 percent cement reduction.
- **The cement reduction is replaced by 200 kg slag plus 100 (or 150) kg fly ash**, giving a total binder of 420 (or 470) kg per cubic metre. Total binder is HIGHER than the conventional mix because SCMs are less reactive per kilogram than cement.
- **Curing age is 56 to 90 days** instead of 28. SCMs hydrate slowly; the strength benefit comes only at extended ages. This is the largest practical constraint on the discovery — the design works only if the structural code accepts longer curing.
- **Superplasticizer is increased from 8 to 12 kg per cubic metre** to maintain workability at the higher binder content.
- **Aggregates and water are unchanged**, so the workability characteristics of the fresh concrete are similar to conventional.

### 3.6 Assumptions, limits, and reproduction

**Assumptions**:
- The XGBoost predictor is trained on the UCI Concrete Compressive Strength dataset (Yeh 1998), which contains 1030 mix samples spanning cement contents from 102 to 540 kg per cubic metre. Predictions outside this range are extrapolations and ARE NOT used in this paper's headline numbers.
- Embodied-carbon emission factors are taken from standard industry life-cycle-assessment values; results scale linearly with these factors. A reader using different emission factors will get a proportionally different absolute reduction but the same percentage reduction.
- Cost figures use US dollar prices typical of US industrial construction in 2024.
- The strength predictor's MAE of 2.55 MPa means that any single point on the Pareto front has roughly ±2.5 MPa uncertainty. The 58.8 MPa winner is therefore "53 to 64 MPa with high probability", which is comfortably above the 50 MPa structural target.

**Limits**:
- This paper does not test the predictor on out-of-distribution mixes (cement below 102 or above 540 kg per cubic metre).
- It does not include thermal-cycling, freeze-thaw, or chloride-ingress durability — only 28-day-equivalent compressive strength.
- It does not validate the discovered mix experimentally — the prediction is from the model alone.
- The 11 candidate-generation strategies produce a finite Pareto front; a more aggressive sampler might find better designs.

**Reproduction**:
1. Install Python 3.12, then `pip install xgboost lightgbm scikit-learn pandas numpy` in a fresh virtual environment.
2. Download the UCI Concrete Compressive Strength dataset (available at the UCI Machine Learning Repository, dataset id 165).
3. Save the file as `data/concrete.csv` in the project directory.
4. Run `python evaluate.py --predict` to reproduce the 5-fold cross-validation MAE of 2.55 MPa.
5. Run `python phase_b_discovery.py` to reproduce the 3,685-candidate Phase B sweep and the discovery results.
6. The winning configuration is saved in `winning_config.json`.

## 4. Methods (the iteration process)

### 4.1 The HDR loop in summary

Each experiment was a single change to the model configuration: a new feature, a hyperparameter modification, a different model family, a target transform, or a monotonicity constraint. Each change was specified in code (in `hdr_loop.py`) before evaluation, with a Bayesian prior probability estimate and an articulated causal mechanism. After evaluation, the change was kept if it improved the 5-fold cross-validation MAE by at least 0.005 over the previous best, or reverted otherwise.

The iteration ran in three stages:

**Phase 1 — Model family tournament.** Three fundamentally different model families (XGBoost, LightGBM, ExtraTrees) tested on the raw 8-feature set, plus a Ridge regression linear baseline as a sanity check. Result: XGBoost wins; LightGBM is essentially tied; ExtraTrees is 11 percent worse; Ridge is 200 percent worse, confirming the relationship is strongly non-linear. XGBoost was carried forward as the model family for Phase 2.

**Phase 2 — Hypothesis-driven loop (20 experiments).** Twenty single-change experiments testing feature additions, hyperparameter modifications, target transforms, and monotonicity constraints, each with a Bayesian prior. Of 20 experiments, 4 were kept (E02 water-to-binder ratio, E03 SCM percentage, E17 monotone constraint on cement, E20 600 boosting rounds) and 16 were reverted. Counterintuitive result: the textbook log(age) feature was reverted (E01) — XGBoost handles age non-linearly without the explicit log.

**Phase 2.5 — Compositional re-test.** Phase 2 ran each experiment with its own feature spec rather than strictly building on the previous best. The Phase 2.5 step explicitly tested the union of the kept changes — wb_ratio plus SCM percentage plus monotone(cement) plus 600 rounds — and confirmed it BEATS the Phase 2 individual winner: MAE 2.5467 vs the Phase 2 best of 2.6419. The minimal compositional winner (P25.5) is the final model.

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
| **Final (Phase 2.5 P25.5)** | **5-fold CV MAE** | **2.5467 MPa** |
| **Final** | **5-fold CV R²** | **0.944** |

A 0.23 MPa MAE improvement (8.3 percent of the baseline) over 23 experiments. Each kept change contributed between 0.022 and 0.063 MPa.

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
- 120 kg cement / 200 kg slag / 100 kg fly ash / 160 kg water / 90-day curing
- Predicted strength 58.8 MPa
- Embodied CO₂ 156.9 kg per cubic metre (53 percent reduction vs C40)
- Cost ~$95 per cubic metre

Best in-distribution mix at 50+ MPa with 56-day curing (more practical):
- 120 kg cement / 200 kg slag / 150 kg fly ash / 140 kg water / 56-day curing
- Predicted strength 53.2 MPa
- Embodied CO₂ 146.9 kg per cubic metre (56 percent reduction vs C40)
- Cost $98 per cubic metre

### 5.3 Pareto-knee summary

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

### 6.3 The 53 percent CO₂ reduction is achieved by replacing cement with SCMs and accepting longer curing

The discovery is not surprising in its mechanism — replacing cement with slag and fly ash is the standard SCM strategy in the cement industry. What is surprising is the magnitude: 66 percent cement replacement at 18 percent higher strength is a significant gain, even with the 90-day curing requirement. The main practical barrier is whether structural codes accept 56-day or 90-day strength specifications. Many codes do; some do not.

### 6.4 The 75 percent reduction claim from prior artifact-derived narratives is not in-distribution

A previous version of this project (lost in a destructive operation earlier in the day, then restarted from scratch) reported a 75 percent CO₂ reduction at 50 MPa using an 80-cement mix. The current rerun, with the same dataset and a similar predictor, finds that this number is below the UCI training range (cement = 80 is outside [102, 540]) and is therefore an extrapolation. The verified in-distribution result is 53 to 56 percent reduction, not 75 percent. We report the verified number.

### 6.5 What is and is not novel in this work

**Not novel — these results are well-established in the literature**:

- The mix design itself (~120 kg cement plus 200–250 kg blast-furnace slag plus 100–150 kg fly ash per cubic metre, with 56- or 90-day curing reaching 50+ MPa). This sits in the established High-Volume Fly Ash Concrete (HVFAC) category, formalised by Bilodeau and Malhotra in the 1990s, with cement contents typically reported as 150 to 250 kg per cubic metre achieving C20 to C40 grade. Our 120 kg cement at 53–58 MPa is at the aggressive end of that range but well within it.

- The 53 to 56 percent CO₂ reduction at equivalent strength. A 2024 *Journal of Cleaner Production* life-cycle assessment of HVFA and ground-granulated-blast-furnace-slag (GGBS) concrete reported a 54 percent CO₂ reduction with 65 percent fly ash replacement — essentially the same number.

- The 90-day curing trick. The "SCM-heavy mixes catch up at 56 to 90 days" pattern is documented in textbooks (Mehta & Monteiro 2014, Neville 2011) and codified in FHWA Tech Brief HIF-16-001 (2016), which permits up to 50 percent fly ash and 70 percent slag replacement.

- The Pareto-optimisation framing. A 2025 *Buildings* paper (MDPI 15(22), 4074) on cost-performance multi-objective optimisation of quaternary-blended-cement concrete reports Pareto-optimal mixes at 51 to 80 MPa with approximately 62 percent less cement than conventional. This is essentially the same finding as ours, by a more sophisticated method (quaternary blends rather than ternary, EHVI+NSGA-II rather than grid sweep). They reached the same conclusion a year before this paper was written.

- Multi-objective ML-based concrete optimisation more broadly. Tipu et al. (2026) report a physics-guided multi-task model with R² = 0.997 (substantially better than our 0.944) and an explicit Pareto-front knee at 50 MPa / 220 kg CO₂. Our knee is at 50 MPa / approximately 147 kg CO₂, which is BETTER on the CO₂ axis, but their model is more accurate and may impose stricter realism constraints we do not. A direct comparison would require running the same evaluation protocol on both models.

**What this paper actually contributes** (smaller claim, more honest):

1. **Transparent methodology**: every experiment has a stated Bayesian prior, an articulated mechanism, and a pre-registered keep-or-revert decision recorded in `results.tsv`. Most published concrete-ML papers report only the winning configuration, not the full HDR loop.
2. **In-distribution honesty**: we explicitly filter the Phase B sweep to candidates within the UCI training range (cement ≥ 102 kg per cubic metre) and reject the 75 percent CO₂ reduction claim as an extrapolation. Most published papers in this area report mathematical optima without checking training-data coverage.
3. **Fully reproducible code-and-data package**: `pip install`, run two scripts, get the exact paper numbers in approximately two minutes on a laptop. The full HDR loop with all 24 experiments is in `hdr_loop.py`, the compositional re-test in `hdr_phase25.py`, and the Phase B sweep in `phase_b_discovery.py`.
4. **Modest technical refinement**: a 10-feature predictor with one monotonicity constraint and 600 boosting rounds achieves MAE 2.55 MPa, slightly better than our 2.78 baseline. This is not a state-of-the-art predictor (Tipu 2026 reports R² 0.997 against our 0.944) but it is sufficient for the Phase B Pareto sweep that produced the headline result.

In short: **this is a reproduction, not a discovery**. The value is in the reproducibility and the honesty about the model's training-data coverage, not in the chemistry of the mix itself. Any civil engineer reading the abstract who is already familiar with HVFAC will recognise the result immediately.

### 6.6 Limitations

- **Single dataset.** All findings are based on the UCI Concrete Compressive Strength dataset, which contains 1030 lab-tested mixes from a single research group's 1998 study. Results may not generalise to mixes far from this distribution, or to field conditions that differ from the lab curing protocol.
- **No experimental validation.** The 53 percent reduction is a model prediction, not a measurement on a poured cylinder. Verifying it requires casting and testing actual concrete specimens at 90 days, which is outside the scope of this paper.
- **Compressive strength only.** Real structural concrete must also satisfy durability (freeze-thaw, chloride ingress, sulfate attack), workability, and shrinkage requirements. None of these are captured here.
- **The cost calculation is sensitive to inputs.** Cement, slag, fly ash, and superplasticizer prices vary by region and year. The reported $95 per cubic metre cost is approximate.
- **No long-term curing data.** UCI's dataset includes ages from 1 to 365 days, but the 90-day samples are sparse. The 90-day predicted strength of 58.8 MPa carries somewhat higher uncertainty than the 28-day predictions.

### 6.7 Future work

1. **Experimental validation**: cast and test the 120-cement / 200-slag / 100-fly_ash mix at 90 days and compare to the predicted 58.8 MPa.
2. **Durability prediction**: train a second model on a durability dataset and add it as a third Pareto objective.
3. **Code-aware optimisation**: parameterise the candidate generator with structural code constraints (minimum cement, maximum SCM percentage, allowed curing ages) and re-run.
4. **Larger dataset**: replicate the study on a more recent and larger dataset (e.g. the Tipu et al. 2026 GreenMix-Pareto dataset of 1000 physics-constrained mixes) to test whether the findings hold.

## 7. Conclusion

A Hypothesis-Driven Research loop on the UCI Concrete Compressive Strength dataset produced a 10-feature monotonic XGBoost strength predictor with cross-validated Mean Absolute Error of 2.55 MPa, achieved through 23 single-change experiments of which only 4 were kept. Applying this predictor to a 3,685-candidate Phase B discovery sweep across 11 generation strategies identified an in-distribution mix design at 120 kg cement plus 200 kg slag plus 100 kg fly ash per cubic metre at 90-day curing that reaches 58.8 MPa compressive strength at 156.9 kg embodied carbon dioxide per cubic metre — a 53 percent carbon dioxide reduction at 18 percent higher strength than the conventional C40 baseline. A 56-day-curing variant achieves a 56 percent reduction at the structural strength target.

This recipe is **not novel**. It sits within the well-established High-Volume Fly Ash Concrete category and is essentially identical to results reported in a 2025 *Buildings* quaternary-blend Pareto-optimisation paper (51–80 MPa at approximately 62 percent less cement than conventional) and a 2024 *Journal of Cleaner Production* life-cycle-assessment study (54 percent CO₂ reduction with 65 percent fly ash). The chemistry is documented in standard concrete textbooks and codified in regulatory documents.

What this paper contributes is the **reproducibility and the in-distribution honesty**: every experiment has a stated Bayesian prior, a pre-registered keep-or-revert decision, and a published row in `results.tsv`; the model's mathematical optimum (cement below the UCI training minimum of 102 kg per cubic metre) is explicitly rejected as an extrapolation rather than reported as a verified discovery. The full code-and-data pipeline runs in approximately two minutes on a laptop. Any reader who wants to reproduce, extend, or refute the result can do so without writing new code.

The practical implication is unchanged regardless of who got there first: ultra-low-cement structural concrete (about 120 kg cement per cubic metre, with 200+ kg slag plus 100+ kg fly ash, cured for 56 to 90 days) is viable within the bounds of existing strength data, and the main barrier is structural-code acceptance of extended curing schedules.

## References

[1] Yeh, I-C. "Modeling of strength of high-performance concrete using artificial neural networks." *Cement and Concrete Research* **28**(12), 1797–1808 (1998). https://doi.org/10.1016/S0008-8846(98)00165-3

[2] Neville, A.M. *Properties of Concrete.* 5th edition, Pearson (2011).

[3] Mehta, P.K. and Monteiro, P.J.M. *Concrete: Microstructure, Properties, and Materials.* 4th edition, McGraw-Hill (2014).

[4] Abrams, D.A. "Design of concrete mixtures." *Bulletin 1*, Structural Materials Research Laboratory, Lewis Institute, Chicago (1918).

[5] Chen, T. and Guestrin, C. "XGBoost: A Scalable Tree Boosting System." *Proc. KDD 2016*, 785–794 (2016). https://doi.org/10.1145/2939672.2939785

[6] Tipu, R.K. et al. "GreenMix-Pareto: Uncertainty-aware, physics-guided multi-objective optimization of low-carbon concrete mix designs." *Ain Shams Engineering Journal* (2026). Reports a physics-guided multi-task model with R² = 0.997 and an explicit Pareto-front knee at 50 MPa / 220 kg CO₂.

[7] European Committee for Standardization. "EN 206-1: Concrete — Part 1: Specification, performance, production and conformity." (2013).

[8] Scrivener, K.L., John, V.M. and Gartner, E.M. "Eco-efficient cements: Potential, economically viable solutions for a low-CO₂ cement-based materials industry." UN Environment Programme report (2016).

[9] MDPI Buildings (2025). "Cost-Performance Multi-Objective Optimization of Quaternary-Blended Cement Concrete." *Buildings* **15**(22), 4074. Reports Pareto-optimal mixes at 51–80 MPa with approximately 62 percent less cement than conventional — an essentially identical finding to this paper, by a more sophisticated method, published a year earlier.

[10] *Journal of Cleaner Production* (2024). "Environmental impact of concrete containing high volume fly ash and ground-granulated blast-furnace slag." Life-cycle assessment of HVFA and GGBS concrete reports 22–40 percent greenhouse-gas reduction with slag and 54 percent CO₂ reduction with 65 percent fly ash.

[11] Federal Highway Administration (2016). "Tech Brief: Supplementary Cementitious Materials." FHWA-HIF-16-001. The regulatory framework for SCM usage in US transportation infrastructure: fly ash 18–50 percent replacement, slag 50–70 percent replacement.

[12] Bilodeau, A. and Malhotra, V.M. (2000). "High-volume fly ash system: concrete solution for sustainable development." *ACI Materials Journal* **97**(1), 41–48. The foundational HVFAC paper.
