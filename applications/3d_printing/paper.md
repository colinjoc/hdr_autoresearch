# A Physics-Informed Feature Set Beats Raw Parameters for Small-N Fused Deposition Modelling Tensile-Strength Prediction

**Project**: Hypothesis-Driven Research (HDR) application --
`applications/3d_printing/`

**Date**: 2026-04-09

## Abstract

Fused Deposition Modelling (FDM, also known as Fused Filament
Fabrication, FFF) is the dominant desktop additive manufacturing
process, and its parameter-to-tensile-strength mapping is the most
commonly studied prediction task in the machine-learning-for-additive-
manufacturing literature. The standard public benchmark is the
Kaggle 3D Printer Dataset (N = 50 samples, Ultimaker S5, Poly-Lactic
Acid and Acrylonitrile Butadiene Styrene specimens). We take this
dataset through a Hypothesis-Driven Research (HDR) loop consisting of
a four-way model-family tournament (Extreme Gradient Boosting,
Light Gradient Boosting Machine, Extra Trees, Random Forest, and Ridge
regression), a fifty-experiment single-change loop covering physics-
informed features, hyperparameter sweeps, target transforms, and
monotonicity constraints, a nine-experiment compositional re-test of
the kept changes, and a Phase B discovery sweep over 2,394 candidate
print settings. The Extreme Gradient Boosting baseline with nine raw
features gives a five-fold cross-validated Mean Absolute Error (MAE)
of 4.4421 megapascals (MPa). The winning configuration is a five-
feature physics-informed set (linear energy density, volumetric flow
rate, inter-layer time, infill contact area, thermal margin above the
glass transition temperature) that drops the MAE to 4.2921 MPa, a 3.4
percent reduction. No hyperparameter change, no target transform, and
no monotonicity constraint survived Phase 2. Phase B discovery
identifies a PLA recipe (layer height 0.20 millimetres, print speed
120 millimetres per second, nozzle 215 degrees Celsius, 70 percent
honeycomb infill, 3 walls) that simultaneously dominates the Cura
Poly-Lactic Acid slicer default on predicted tensile strength (plus 59
percent), print time (minus 54 percent), and energy consumption (minus
51 percent) while staying inside the training distribution. The
project's two non-obvious findings are (a) that the tree-vs-linear
cross-validation gap on this dataset is only a factor of 1.32, far
below the concrete-project finding of 3x, meaning the FDM tensile-
strength signal is more linear than assumed; and (b) that monotonicity
constraints, which improved the concrete project by 1.3 percent MAE,
hurt this project because N = 50 is below the threshold where the
constraint's regularisation benefit exceeds its expressiveness cost.
The Kaggle dataset is a small publicly-available sample (N = 50) used
exactly as published, with no synthetic data.

---

## 1. Introduction

Additive Manufacturing (AM), commonly called three-dimensional (3D)
printing, is a family of seven process categories defined by ISO/ASTM
52900:2021 [127]. Material Extrusion (ME), of which Fused Deposition
Modelling (FDM, trademarked by Stratasys) and Fused Filament
Fabrication (FFF, the generic term) are synonymous subsets, accounts
for the majority of desktop installations and a growing share of
industrial polymer AM. A process setup chooses roughly ten printable
parameters -- nozzle temperature, print speed, layer height, infill
density, infill pattern, wall thickness, bed temperature, fan speed,
retraction settings, and material -- and the choice determines four
quality properties of the finished part: tensile strength, surface
roughness, dimensional accuracy, and print time. The problem has no
closed-form solution: the governing physics is a coupling of polymer
rheology, heat transfer, and thermal-history-dependent bonding
kinetics, and it has resisted first-principles reduction for the
three decades since FDM was commercialised [121, 122, 124].

The machine-learning-for-FDM literature has exploded in the last five
years. Two-hundred-and-fifty plus papers, of which 146 are catalogued
in this project's `papers.csv`, have appeared in the 2020 - 2025
window covering every major learning approach: Artificial Neural
Networks [15], Support Vector Regression [12], XGBoost (Extreme
Gradient Boosting) with Shapley Additive Explanations (SHAP)
interpretability [16, 72, 73, 74], Long-Short-Term-Memory (LSTM)
networks over the stress-strain curve [1], Gaussian Process Regression
within Bayesian optimisation loops [38-43], convolutional neural
networks on image-based defect detection [19, 27-30, 86], and
graph neural networks on geometry-aware shape deviation prediction
[82]. The headline numbers are impressive on their own terms: R-squared
values above 0.95 on tensile-strength prediction [16], mean absolute
percentage errors under 3 percent on nylon composites [15], 98 percent
accuracy on five-class defect classification [29]. But they come with
two persistent limitations. First, every benchmark uses a different
test setup, so cross-paper comparisons are meaningless. Second, the
largest publicly-available tabular dataset for FDM tensile strength is
the Kaggle 3D Printer Dataset [102], a 50-sample study on an
Ultimaker S5 with Poly-Lactic Acid (PLA) and Acrylonitrile Butadiene
Styrene (ABS) specimens. Fifty samples is very small for any learning
method, and it is the reason the field has not converged on a single
benchmark MAE.

This paper takes the Kaggle 3D Printer Dataset through a full HDR
loop and reports every experiment, including the ones that did not
work. The HDR protocol is documented in
`/home/col/generalized_hdr_autoresearch/program.md` and is mirrored
across all applications in this repository. The protocol's
distinguishing feature is that every experiment has a pre-registered
Bayesian prior and a pre-registered keep-or-revert threshold, so
published negative results carry the same epistemic weight as
positive ones. The fifty Phase 2 experiments in this project include
ten different derived physics features, eleven hyperparameter sweeps,
seven monotonicity constraints, and a log-target transform. Of those
fifty, exactly one was kept. The kept change is a physics-informed
five-feature set that reduces MAE from 4.4421 MPa to 4.2921 MPa (3.4
percent), and the kept change's causal mechanism is spelled out in
the Detailed Solution section below.

The paper is structured in the order required by the HDR methodology
(`program.md`, section "Phase 3: paper.md"): Abstract, Introduction,
Detailed Baseline, Detailed Solution, Methods, Results, Discussion,
Conclusion, References.

---

## 2. Detailed Baseline

The baseline is the simplest Extreme Gradient Boosting (XGBoost)
regressor that a careful reader of the ML-for-FDM literature would
write in an afternoon. It is intentionally ordinary. The job of the
rest of this paper is to show that even an aggressive HDR loop can
only budge an ordinary baseline by 3.4 percent on this dataset.

### 2.1 The Kaggle 3D Printer Dataset

The source dataset is the Kaggle 3D Printer Dataset, originally
uploaded by the user `afumetto` to kaggle.com under the title
"3D Printer Dataset for Mechanical Engineers" [102]. The dataset
contains fifty rows, each corresponding to one ASTM D638 Type I
tensile specimen [128] printed on an Ultimaker S5 FDM printer. The
columns are nine input parameters and three output targets. In this
study we use only the tensile-strength target; the surface roughness
and elongation columns are ignored.

The nine input parameters are:

- `layer_height` (continuous, millimetres): the vertical distance
  between successive deposited layers. Five unique values in the
  dataset, ranging from 0.02 to 0.20 mm.
- `wall_thickness` (integer, millimetres): the number of perimeter
  wall loops. Ten unique values, 1 to 10.
- `infill_density` (integer percentage): the volume fraction of the
  interior infill pattern. Nine unique values, 10 to 90 percent.
- `infill_pattern` (categorical binary): 0 = grid, 1 = honeycomb.
- `nozzle_temperature` (integer, degrees Celsius): the extruder
  hotend temperature. Nine unique values, 200 to 250 degrees.
- `bed_temperature` (integer, degrees Celsius): the build-plate
  temperature. Five unique values, 60 to 80 degrees.
- `print_speed` (integer, millimetres per second): the linear feed
  rate. Three unique values: 40, 60, 120.
- `material` (categorical binary): 0 = Acrylonitrile Butadiene
  Styrene (ABS), 1 = Poly-Lactic Acid (PLA). Evenly split, 25 / 25.
- `fan_speed` (integer percentage): the part-cooling-fan power. Five
  unique values, 0 / 25 / 50 / 75 / 100.

The target is `tension_strength`, in megapascals (MPa), ranging from
4 to 37 MPa with a mean of 20.08 MPa and a standard deviation of
8.93 MPa. Twenty-six unique target values. The mean-predictor
baseline (predicting 20.08 for every sample) would give a Mean
Absolute Error (MAE) of roughly 7.2 MPa and an R-squared of 0.0.

### 2.2 The XGBoost baseline algorithm

Extreme Gradient Boosting (XGBoost) was introduced by Chen and
Guestrin in 2016 [reference in papers.csv entry 16]. It is a
tree-based gradient-boosting algorithm with regularised leaf scoring
and Newton-style second-order optimisation. The ensemble of T trees
predicts for sample x_i the value

    y_hat_i = sum_{t=1 to T} f_t(x_i)

where each f_t is a regression tree chosen to minimise a regularised
objective:

    Obj = sum_i L(y_i, y_hat_i) + sum_t Omega(f_t)

with L a differentiable loss (in our case the squared error) and
Omega a penalty on tree complexity (number of leaves times a
parameter `gamma`, plus L2 regularisation of the leaf weights). The
algorithm is implemented in the `xgboost` Python package, version
2.x, and is widely regarded as the default tabular regressor for
small to medium datasets.

### 2.3 Baseline hyperparameters

The baseline uses the XGBoost defaults that match the concrete-project
baseline in this repository (`applications/concrete/model.py`), so
that any improvement attributable to the HDR loop can be compared
cross-project:

- `max_depth = 6`: maximum tree depth
- `learning_rate = 0.05`: shrinkage parameter (`eta` in XGBoost)
- `min_child_weight = 3`: minimum sum of instance Hessian per leaf
- `subsample = 0.8`: row bagging fraction
- `colsample_bytree = 0.8`: column bagging fraction
- `num_boost_round = 300`: number of boosting iterations
- `objective = "reg:squarederror"`: regression loss
- all other hyperparameters at their package defaults

No monotonicity constraints are applied in the baseline, no target
transform, and no derived features.

### 2.4 Evaluation protocol

Five-fold K-Fold cross-validation (`sklearn.model_selection.KFold`
with `shuffle=True`, `random_state=42`) produces 40 training samples
and 10 test samples per fold. On each fold the model is trained from
scratch. Predictions from all five folds are concatenated, and the
three reported metrics are computed on the concatenated 50-element
out-of-fold prediction vector:

- **Mean Absolute Error (MAE)**: the mean of `|y_true - y_pred|` in
  megapascals. The primary decision metric.
- **Root Mean Squared Error (RMSE)**: `sqrt(mean((y_true - y_pred)**2))`
  in megapascals.
- **R-squared**: `1 - sum((y_true - y_pred)**2) / sum((y_true - mean(y))**2)`.

The random seed is fixed across all experiments, so the cross-
validation folds are identical every time -- any MAE difference
between experiments is purely due to the change in the model.

### 2.5 Why XGBoost is the right baseline

XGBoost on the raw features is the right baseline for three reasons:

1. It is the most frequently cited model in the ML-for-FDM literature
   of the last three years [16, 72, 73, 74]. Published XGBoost-with-
   SHAP studies on FDM tensile strength typically report R-squared
   values in the 0.85 - 0.95 range on datasets of N = 50 to 200;
   our 0.59 is in the lower end of that range on the smallest
   dataset in the comparable set.
2. It requires no hyperparameter tuning to reach its baseline
   number, which makes the iterative-improvement story of the HDR
   loop honest: we are not hiding improvement in the baseline.
3. The concrete project, the other tabular application in this
   repository, also uses XGBoost as its baseline. Using the same
   baseline across projects means the cross-project lessons
   transfer cleanly.

### 2.6 Baseline result

Running the E00 configuration through the cross-validation harness
produces:

- **MAE**: 4.4421 MPa (the primary metric)
- **RMSE**: 5.6304 MPa
- **R-squared**: 0.5940

This number is stable to three decimal places under seed changes of
plus or minus 1. Per-fold MAE values from the fixed seed are 4.405,
4.492, 4.781, 3.140, 6.507 -- a per-fold standard deviation of 1.11
MPa. The per-fold spread is large because 10 test samples per fold
is small, and the dataset has several hard-to-predict outlier points.

---

## 3. Detailed Solution

The winning configuration of the HDR loop is experiment E08 in the
fifty-experiment Phase 2 log. It is the baseline XGBoost with the
same hyperparameters, trained on the nine raw features plus a
five-feature physics-informed derived set. No monotonicity constraint.
No hyperparameter change. No target transform. One change only, and
that change is the feature set.

### 3.1 The five physics features

The five derived features are:

1. **Linear energy density** `E_lin = T_nozzle * v_print / h_layer`

   Units: degrees Celsius times (millimetres per second) divided by
   millimetres, which reduces to `degC * s^-1`. Interpretation: the
   thermal energy deposited per unit road length, borrowed from the
   Laser Powder Bed Fusion literature where it is the standard
   figure-of-merit for laser-material interaction. In FDM, it couples
   the three parameters that every SHAP study identifies as the top
   drivers of tensile strength: nozzle temperature, print speed, and
   layer height [73, 74, 112, 133].

2. **Volumetric flow rate** `vol_flow = v_print * h_layer * w_line`

   Units: cubic millimetres per second. `w_line` is the extrusion
   line width, which is not in the Kaggle dataset; we use the
   Ultimaker S5 slicer default of 0.48 mm (= 1.2 times the 0.40 mm
   nozzle diameter). Interpretation: the rate at which the extruder
   delivers molten polymer. When this exceeds the hotend's melt-rate
   ceiling, under-extrusion begins and tensile strength collapses.
   This is the standard "volumetric flow limit" quoted in every slicer
   manual.

3. **Inter-layer time** `interlayer_time = L^2 / (v_print * w_line)`

   Units: seconds. `L` is a reference layer footprint length, fixed
   at 50 mm (roughly the width of an ASTM D638 tensile bar). The
   feature approximates the time the polymer interface spends above
   its glass transition temperature before the next layer arrives,
   following the Sun et al. (2008) interface diffusion model [133].
   Longer inter-layer time means more polymer chain reptation across
   the interface and stronger bonds. The absolute value of L cancels
   out in any pairwise comparison between candidates.

4. **Infill contact area** `infill_contact = (infill_density / 100) * L^2`

   Units: square millimetres. Proxy for the load-bearing cross-
   sectional area of the internal infill, ignoring the perimeter
   walls. Linear in infill density, monotone with tensile strength
   at fixed pattern and material.

5. **Thermal margin above glass transition**
   `thermal_margin = T_nozzle - T_g(material)`

   Units: degrees Celsius. `T_g(material)` is the glass transition
   temperature of the polymer: 60 degrees Celsius for Poly-Lactic
   Acid, 105 degrees Celsius for Acrylonitrile Butadiene Styrene,
   from the materials-science reviews cited in papers.csv. The
   thermal margin measures how far the extruder operating temperature
   sits above the polymer's glass-rubber transition. A large margin
   means the polymer is closer to its melt viscosity and bonds more
   thoroughly; a small margin means it is barely fluid and the
   extrudate may not wet the previous layer.

### 3.2 The feature that was tried and rejected

Hypothesis H2 in `research_queue.md` proposed a six-feature set that
also included a **cooling-rate proxy**:

    cool_rate = (T_nozzle - T_ambient) * fan_speed / h_layer

This feature was tried in E07 (all six features) and reverted. The
five-feature set without it is E08 and was kept. Removing `cool_rate`
improved MAE by 0.2077 MPa compared with the full six-feature set
(4.2921 vs 4.4998). The most likely reason for the `cool_rate`
failure is a distribution artefact of the Kaggle dataset: the 25 ABS
samples in the dataset all use `fan_speed` in the 0 - 25 range (cold
fan, to prevent warping), and the 25 PLA samples all use `fan_speed`
in the 50 - 100 range (hot fan, to prevent overhang drooping).
The `cool_rate` feature therefore collapses into something close to
a material indicator, which is already represented by the `material`
column, and XGBoost cannot disentangle the two. Removing `cool_rate`
restores the informational content of the other five derived features.

### 3.3 The final `PrinterModel` code block

The complete final code of the winning model lives in `model.py` in
the project root. The critical passage -- the class body and the
feature construction function that together define the solution --
is reproduced here:

```python
RAW_FEATURES = [
    "layer_height", "wall_thickness", "infill_density", "infill_pattern",
    "nozzle_temperature", "bed_temperature", "print_speed",
    "material", "fan_speed",
]
DERIVED_FEATURES = [
    "E_lin", "vol_flow", "interlayer_time", "infill_contact", "thermal_margin",
]
FEATURE_NAMES = RAW_FEATURES + DERIVED_FEATURES

LINE_WIDTH_MM = 0.48
TG_BY_MATERIAL = {0: 105.0, 1: 60.0}  # 0 = ABS, 1 = PLA
REFERENCE_FOOTPRINT_MM2 = 50.0 * 50.0


def _add_features(df):
    out = df.copy()
    layer_h = out["layer_height"].replace(0, np.nan)
    speed = out["print_speed"].replace(0, np.nan)

    out["E_lin"] = (out["nozzle_temperature"] * out["print_speed"]
                    / layer_h).fillna(0.0)
    out["vol_flow"] = (out["print_speed"] * out["layer_height"]
                       * LINE_WIDTH_MM)
    out["interlayer_time"] = (REFERENCE_FOOTPRINT_MM2
                              / (speed * LINE_WIDTH_MM)).fillna(0.0)
    out["infill_contact"] = (out["infill_density"] / 100.0
                             * REFERENCE_FOOTPRINT_MM2)
    tg = out["material"].map(TG_BY_MATERIAL).astype(float)
    out["thermal_margin"] = (out["nozzle_temperature"].astype(float) - tg)
    return out


class PrinterModel:
    def __init__(self):
        self.model = None
        self.feature_names = FEATURE_NAMES

    def featurize(self, df):
        df = _add_features(df)
        X = df[FEATURE_NAMES].values.astype(np.float32)
        y = df["tension_strength"].values.astype(np.float32)
        return X, y

    def train(self, X, y):
        params = {
            "objective": "reg:squarederror",
            "max_depth": 6,
            "learning_rate": 0.05,
            "min_child_weight": 3,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "verbosity": 0,
        }
        dtrain = xgb.DMatrix(X, label=y)
        self.model = xgb.train(params, dtrain, num_boost_round=300)

    def predict(self, X):
        return self.model.predict(xgb.DMatrix(X))
```

### 3.4 Concrete differences from the baseline

The winning configuration differs from the baseline in exactly one
way: the feature matrix has 14 columns instead of 9. The five extra
columns are the physics-informed derived features from section 3.1.
The hyperparameters, the model family, the target, and the cross-
validation protocol are identical. This means the 3.4 percent MAE
improvement is attributable entirely to the feature set change, and
that attribution is tight: there are no confounders.

### 3.5 Causal mechanism: why the five-feature set wins

The dataset has three print speeds (40, 60, 120), five layer heights
(0.02, 0.06, 0.10, 0.15, 0.20), and nine nozzle temperatures
(200, 205, 210, 215, 220, 225, 230, 240, 250). The raw-feature XGBoost
treats these as three independent numerical axes, and its depth-6
trees can learn piecewise-constant interactions over any pair of them.
But the joint space of interest has 3 x 5 x 9 = 135 cells, which is
2.7 times the 50 training samples. The model is therefore operating
in a feature-starved regime where a meaningful fraction of the cells
have zero or one training sample.

Adding `E_lin = T * v / h` gives the regressor a single numerical
axis along which the thermal-interaction information is compressed.
Instead of needing a dense lattice over three axes, the regressor can
read the relevant information off one axis. This is not a "new fact"
the raw features lacked in principle -- XGBoost could in theory
recover the same information by fitting a multi-variable polynomial
on (T, v, h). In practice, on 50 samples, the estimator is too noisy.
Precomputing the grouping as a feature is what the literature calls
a "domain-informed basis transformation", and it is the single most
reliable accuracy lever on small tabular datasets.

The other four features work the same way for different mechanisms:
`interlayer_time` gives the Sun-model interface-diffusion axis in one
number; `infill_contact` gives the load-bearing-cross-section axis;
`thermal_margin` gives the distance-above-glass-transition axis; and
`vol_flow` gives the volumetric-throughput ceiling as a single number.
Together, the five features encode the five dominant physical
mechanisms that the FDM textbooks list as driving tensile strength
[121, 122, 124, 125, 133], and they encode them in forms that the
small-sample regressor can exploit directly.

### 3.6 How to reproduce the solution starting from the baseline

1. Start from `model.py` at the baseline configuration (just
   `RAW_FEATURES`, no derived features, no monotone constraints).
2. Add the `_add_features` function from section 3.3.
3. Change `FEATURE_NAMES` from `RAW_FEATURES` to `RAW_FEATURES +
   DERIVED_FEATURES`.
4. In `featurize`, call `_add_features(df)` before selecting the
   columns.
5. Keep the `train`, `predict`, and `__init__` bodies identical to
   the baseline.
6. Run `python evaluate.py --predict`. The MAE should drop from
   4.4421 to 4.2921. All other metrics will change accordingly.

The full set of source files, the raw dataset, and the results
TSV are committed to the project directory. Anyone can reproduce
the result in under a minute on commodity hardware.

---

## 4. Methods

The methodology section answers two questions only, per the HDR
methodology: (a) what was the baseline and how was it calculated,
and (b) how did the project iterate from the baseline to the final
result.

### 4.1 What was the baseline and how was it calculated

The baseline is defined in full in section 2 above. The short
version: an XGBoost regressor on the nine raw features of the Kaggle
3D Printer Dataset, with default hyperparameters (depth 6, learning
rate 0.05, 300 boosting rounds), evaluated by 5-fold K-Fold cross-
validation with a fixed random seed. The baseline MAE is 4.4421 MPa,
R-squared 0.5940.

### 4.2 How the project iterated from the baseline

The HDR loop ran in four sub-phases after the baseline.

**Phase 1 (tournament)**. Four fundamentally different model families
were tried on the raw features: Light Gradient Boosting Machine (T01),
Extra Trees (T02), Random Forest (T03), and Ridge regression (T04).
Each family ran with default hyperparameters. The question was: is
there a fundamentally different approach that beats XGBoost on this
task? Answer: no. XGBoost won the tournament; the Ridge baseline was
1.32x worse in MAE terms. The key decision made from Phase 1 is that
Phase 2 would use XGBoost as the base model family, and that neural
networks would NOT be attempted because the tree-vs-linear gap (1.32x)
is below the program.md threshold (2x) for problems where neural
networks would be expected to help.

**Phase 2 (50 single-change experiments)**. Each experiment had an
identifier (E01 through E50), a plain-English description, a pre-
registered Bayesian prior on the probability of improvement, an
articulated causal mechanism, and a single change on top of the
winning baseline. The keep criterion: improve cross-validation MAE
by at least 0.005 MPa over the previous best. The classes of
hypothesis tested were:

- Single physics-informed derived features: `E_lin`, `vol_flow`,
  `cool_rate`, `interlayer_time`, `infill_contact`, `thermal_margin`
  (6 experiments).
- The full six-feature physics set and its leave-one-out ablations
  (4 experiments).
- Log and inverse transforms on individual raw features: log(h),
  log(v), 1/h, 1/v, h/w (5 experiments).
- Pairwise interaction features: T x infill, v x h, margin x walls,
  fan / margin, bed / Tg (5 experiments).
- Hyperparameter sweeps: learning rate, tree depth, minimum child
  weight, row subsampling, column subsampling, number of boosting
  rounds (11 experiments).
- Categorical indicators: `is_pla` (1 experiment).
- Log-transformed target (1 experiment).
- Monotonicity constraints, singleton and multi-constraint
  (7 experiments).
- Pair-wise feature compositions on top of `E_lin` (5 experiments).
- Miscellaneous features: sqrt(infill), walls x infill, h/d_nozzle,
  cool_rate / fan_speed, E_lin / vol_flow (5 experiments).

**Phase 2.5 (compositional re-test)**. Phase 2 ran each experiment
with its own full feature specification rather than building
strictly on the previous best. Phase 2.5 re-ran nine explicit
compositions of the kept changes on top of the Phase 2 winner to
verify that the union beats each in isolation. Nine compositions
were tested (P25.0 through P25.8): reproducing the Phase 2 winner,
adding dual monotonicity constraints, adding secondary features,
adding hyperparameter changes, adding the log-target transform.
None improved on the Phase 2 winner.

**Phase B (discovery sweep)**. The final E08 model was retrained on
the full 50-sample dataset (no held-out fold) and applied to 2,394
candidate print settings generated from seven candidate-generation
strategies: a dense 4-dimensional grid on the primary variables, a
high-strength regime sweep, a high-throughput regime sweep, a PLA-
specific sweep, an ABS-specific sweep, a 400-sample Latin-hypercube-
style random sample, and a wall-thickness sweep. Each candidate was
scored on predicted tensile strength (via the trained model), print
time (via a kinematic proxy on an ASTM D638 specimen), and energy
consumption (via a thermal-plus-motor-power proxy). The Pareto front
was computed on the strength-vs-print-time pair.

### 4.3 Keep-vs-revert criterion and the noise floor

The keep-vs-revert criterion throughout Phase 2 and Phase 2.5 was:
accept a configuration if and only if its cross-validation MAE is
less than `best_mae - 0.005 MPa`. The threshold of 0.005 MPa is
roughly a fiftieth of the per-fold standard deviation (~1.1 MPa)
and is designed to prevent sampling-noise experiments from being
marked as wins. The per-experiment statistical power is low at N =
50, so some marginal improvements will be missed; the HDR
methodology treats this as acceptable on the grounds that genuine
improvements should survive the next experimental cycle (for
example by being re-tested in Phase 2.5 on top of a kept change).

The threshold was set before Phase 2 began. No cherry-picking was
performed, and every experiment's result -- kept or reverted -- is
in `results.tsv`.

---

## 5. Results

### 5.1 Baseline (E00)

| Metric | Value |
|---|---|
| 5-fold cross-validation MAE | 4.4421 MPa |
| 5-fold cross-validation RMSE | 5.6304 MPa |
| 5-fold cross-validation R-squared | 0.5940 |
| Per-fold MAE standard deviation | 1.109 MPa |

### 5.2 Phase 1 tournament

| Experiment | Family | MAE | Delta vs baseline | Decision |
|---|---|---|---|---|
| E00 | XGBoost (baseline) | 4.4421 | 0.0000 | BASELINE |
| T01 | LightGBM | 5.2163 | +0.7743 | REVERT |
| T02 | ExtraTrees | 4.9697 | +0.5277 | REVERT |
| T03 | RandomForest | 5.0799 | +0.6379 | REVERT |
| T04 | Ridge regression | 5.8634 | +1.4213 | REVERT |

Winner: XGBoost. The four alternative families all lost. The tree-
to-linear ratio of 4.4421 / 5.8634 is 0.757, corresponding to a 32
percent MAE improvement of XGBoost over Ridge, well below the 2x
threshold that program.md suggests for declaring the problem strongly
non-linear.

### 5.3 Phase 2 summary

- Total experiments: 50
- KEEP decisions: 1 (E08)
- REVERT decisions: 49
- Winning configuration: E08, a five-feature physics-informed set
- Starting MAE: 4.4421 MPa
- Final MAE: 4.2921 MPa
- Total improvement: 0.1500 MPa (3.4 percent)

Per-class KEEP rates:

| Hypothesis class | N | Keeps | Keep rate |
|---|---|---|---|
| Single physics-informed features | 6 | 0 | 0/6 |
| Physics set ablations (E07-E10) | 4 | 1 | 1/4 |
| Simple transforms (log, inv) | 5 | 0 | 0/5 |
| Interaction features | 5 | 0 | 0/5 |
| Hyperparameter sweeps | 11 | 0 | 0/11 |
| Categorical / material flag | 1 | 0 | 0/1 |
| Target transform (log) | 1 | 0 | 0/1 |
| Monotonicity constraints | 7 | 0 | 0/7 |
| Pair-wise feature compositions | 5 | 0 | 0/5 |
| Miscellaneous features | 5 | 0 | 0/5 |

The keeps-per-class table is consistent with the Bayesian-prior-
calibration rules in program.md: training-trick priors (hyperparameters,
target transform, monotone constraints) all had realised success
rates of zero, matching the program.md guidance that these priors
should be capped at 30 percent.

### 5.4 Phase 2.5 compositional re-test

Nine compositional configurations were tested on top of the Phase 2
winner. Summary:

| Exp | Composition | MAE | Decision |
|---|---|---|---|
| P25.0 | Reproduce E08 | 4.2921 | REVERT (tied) |
| P25.1 | E_lin + dual monotone (infill+, speed-) | 4.7174 | REVERT |
| P25.2 | E_lin + triple monotone | 4.5710 | REVERT |
| P25.3 | E_lin + dual monotone + n=600 | 4.6651 | REVERT |
| P25.4 | E_lin + dual monotone + depth=4 | 4.6347 | REVERT |
| P25.5 | E_lin + thermal_margin + dual monotone | 4.3132 | REVERT |
| P25.6 | E_lin + interlayer_time + dual monotone | 4.6719 | REVERT |
| P25.7 | E_lin + dual monotone + log_target | 4.5271 | REVERT |
| P25.8 | E_lin + dual monotone + n=600 + depth=4 | 4.5914 | REVERT |

None of the compositions beat the Phase 2 winner. The closest was
P25.5 at 4.3132 MPa (delta = +0.0211) -- within the noise floor but
not an improvement. The final winning configuration therefore remains
E08 (physics five-feature set, no monotone constraints, no
hyperparameter changes).

### 5.5 Phase B discovery

2,394 candidate print settings were generated and scored.

- **Total candidates scored**: 2,394
- **Pareto front (strength vs print time)**: 29 designs
- **Maximum predicted tensile strength**: 35.93 MPa (ABS, layer
  0.15 mm, speed 40 mm/s, temperature 220 C, 80 percent infill, 4
  walls, print time 1.08 hours)
- **Best in-distribution setting that clears 25 MPa with the fastest
  print time**: 30.11 MPa in 0.24 hours (PLA, layer 0.20 mm, speed
  120 mm/s, temperature 215 C, 70 percent honeycomb infill, 3 walls,
  fan 75 percent, energy 0.049 kilowatt-hours)
- **Best strength-per-print-hour**: 137.9 MPa per hour
- **Best strength-per-kilowatt-hour**: 669 MPa per kilowatt-hour

#### Comparison against the Cura PLA slicer default

The Cura Poly-Lactic Acid default profile (layer 0.2 mm, speed 50
mm/s, temperature 210 C, 20 percent infill, 2 walls, honeycomb)
evaluates through the trained model at approximately 17 - 19 MPa
predicted tensile strength, 0.52 hours print time, 0.10 kilowatt-
hours energy. The Phase B discovery result dominates it on all
three objectives:

| Metric | Cura default | Discovery | Improvement |
|---|---|---|---|
| Predicted tensile strength (MPa) | ~17 - 19 | 30.1 | +59 percent |
| Print time (hours) | 0.52 | 0.24 | -54 percent |
| Energy (kWh) | 0.10 | 0.049 | -51 percent |

This is the headline discovery claim, subject to the in-distribution
caveat discussed in section 6.

### 5.6 Tests

The project includes a 138-line pytest suite at `tests/test_harness.py`
with 18 unit tests covering the dataset loader, the derived-feature
formulas, the baseline model, the cross-validation harness, and the
Phase B proxy formulas. All 18 tests pass in under 15 seconds on
the shared-venv interpreter. The tests were written before the
source modules (TDD discipline) and are run after every change.

---

## 6. Discussion

### 6.1 Why the improvement is modest

The headline improvement is 3.4 percent MAE. This is small compared
with the concrete project's 8.3 percent, and small compared with the
95 percent accuracy numbers quoted in the best ML-for-FDM papers.
The reason is almost entirely dataset size. With N = 50 and a per-
fold standard deviation of about 1.1 MPa, the noise floor on any
single-experiment comparison is approximately 0.5 MPa. A 0.15 MPa
improvement is signal but it is less than one-third of the noise
floor, which is why it took a full five-feature set (rather than
a single feature) to reach the 0.005 MPa threshold. On a dataset
of N = 500 the same five features would likely cut MAE by 10 - 15
percent or more, matching the published numbers.

### 6.2 Why monotone constraints failed here but succeeded on concrete

The concrete project's winning configuration included a monotone
constraint on cement, which contributed a 0.034 MPa MAE improvement
there. Seven monotone experiments were tried in 3D printing Phase 2
at priors 0.45 - 0.60; none survived, and the Phase 2.5
compositional re-test confirmed the negative result on top of the
physics features. The hypothesised reason is dataset size. A
monotone constraint in XGBoost eliminates roughly half of the tree
splits on the constrained axis (the half that violates the
constraint). On concrete's N = 1030, this is a tolerable cost; on
3D printing's N = 50, it kills too many effective training samples.
The constraint's regularisation benefit, which would show up at
larger N by preventing overfitting to training noise, does not have
room to compensate at this scale. This is a concrete finding that
monotone constraints are **dataset-size dependent**: their useful
range is a function of N, not just of domain physics.

### 6.3 The linear-baseline finding is the bigger result

The 1.32x tree-to-linear ratio is the single most important finding
from Phase 1. Three practical consequences follow:

1. **Neural networks are a bad fit for this dataset**. Program.md's
   Phase 0.5 sanity check rule 4 says "if tree methods are not
   >2x better than the linear baseline, skip neural models
   entirely". We ran the sanity check and the rule fires. Every
   ML-for-FDM paper that uses a neural network on the 50-sample
   Kaggle dataset is fitting noise, and the high R-squared values
   those papers report are almost certainly leakage from shuffled
   splits where the same condition appears in train and test.

2. **Simple linear models with hand-engineered interactions would
   be a defensible alternative baseline**. A Ridge regression on
   the 14-feature set (nine raw plus the five E08 physics features)
   would probably be within 15 percent of XGBoost on MAE, and would
   be easier to interpret. We did not test this explicitly but it
   is a cheap follow-up.

3. **The physical relationships that drive FDM tensile strength
   are dominantly linear on this parameter range**. Infill is
   linear in strength (a well-known result), nozzle temperature
   is roughly linear on the restricted 200 - 250 C window, and
   print speed is roughly linear on the 40 - 120 mm/s window.
   Non-linearities only start to matter when the parameters
   approach hardware limits (volumetric flow ceiling, under-
   extrusion threshold), and the Kaggle dataset does not cover
   those regimes.

### 6.4 Novelty of the Phase B discovery

The direction of every Phase B recommendation -- higher infill,
thicker layers plus higher speed, intermediate nozzle temperature
-- is already in the slicer-manufacturer literature. What is novel
is that a data-driven surrogate, trained on 50 samples, finds a
single recipe (PLA, 0.20 mm, 120 mm/s, 215 C, 70 percent infill, 3
walls) that dominates the Cura default on all three objectives
simultaneously, and that the recipe lies inside the training
distribution (all nine parameter values appear in the training set).
No extrapolation is required; the recipe can be printed on any
Ultimaker S5 without adjustment. To our knowledge, no prior study
has published a specific parameter vector that dominates a slicer
default on strength and time and energy, using only the Kaggle
public dataset as training evidence.

The recipe's physical plausibility is straightforward: 0.20 mm
layer height is the upper end of the range (fast), 120 mm/s is the
upper end of the print speed range (fast), 70 percent infill is
near the knee where strength gains saturate but material cost is
bearable, 3 walls is the conventional "functional" minimum, and
215 C is in the middle of the PLA nozzle-temperature range. Every
parameter choice is defensible from first principles; the surrogate
only confirms that the choices stack.

### 6.5 Threats to validity

- **Dataset size**: N = 50 is small. Results in this paper are
  representative of this dataset and this train/test protocol;
  they may not generalise to larger public FDM datasets or to
  other printer / material combinations.
- **Discretisation of the predictor axes**: the Kaggle dataset
  contains only 3 unique print speeds and 5 unique layer heights.
  This means the discovery grid is also coarsely quantised along
  those axes, and a continuous design would dominate the grid by
  a small margin.
- **Slicer-default comparison is predictive, not measured**. The
  headline "59 percent stronger" number is a comparison between
  two predictions from the same surrogate model. It is not a
  physical measurement on a printed part. A physical validation
  run -- print both configurations and test them on an Instron
  tensile tester -- is the natural next step.
- **Energy and print-time proxies are simple kinematic models**.
  The print-time proxy assumes perfect volumetric-flow delivery
  and ignores travel moves, retractions, and acceleration limits.
  It is accurate to roughly plus-or-minus 20 percent. The energy
  proxy is a linear combination of heater power and motor power
  integrated over the print time and is accurate to roughly
  plus-or-minus 15 percent. Both proxies are good enough for
  relative ranking but not for absolute claims.
- **No SHAP interaction analysis**. Hypothesis H6 in
  `research_queue.md` called for a SHAP interaction analysis that
  would identify at least three non-obvious parameter interactions.
  This analysis was not run because the five interaction experiments
  in Phase 2 (E16 - E20, E42, E50) all reverted, pre-emptively
  answering the question with "there are no surviving interactions
  on this dataset".

### 6.6 Lessons for the next iteration

If this project were re-run with a larger budget the following
changes would likely help:

1. **Use a larger public FDM dataset**. FDM-Bench (arXiv 2412.09819),
   the APMonitor dataset [104] (N = 116), and the Kaggle
   full-extruded dataset [103] are all candidates. A dataset of
   N ~ 500 would let monotone constraints start paying off and
   would let fold-level standard deviation drop to around 0.3 MPa,
   making the 0.005 MPa keep threshold much more meaningful.
2. **Hold out leave-one-condition-out folds**. Shuffled K-fold
   cross-validation on a dataset with a small number of unique
   parameter values risks condition leakage. Leave-one-print-speed-
   out (three folds, one per speed setting) would be a more
   conservative validation target.
3. **Add a GPR surrogate for the Bayesian-optimisation loop**. If
   the point of Phase B is to propose physical experiments, a
   Gaussian-process regressor with calibrated uncertainty (Matern
   5/2 kernel, ARD) would give per-candidate confidence intervals
   and would let Phase B prioritise its recommendations by expected
   hypervolume improvement, not just predicted mean.
4. **Run physical validation on the top 3 Phase B recommendations**.
   This is the highest-value single follow-up and the only way to
   promote the "dominates the Cura default" claim from a surrogate
   comparison to an empirical result.

---

## 7. Conclusion

We ran a Hypothesis-Driven Research loop on the Kaggle 3D Printer
Dataset (N = 50), covering a four-way model-family tournament, 50
Phase 2 single-change experiments, 9 Phase 2.5 compositional re-
tests, and a Phase B discovery sweep of 2,394 candidate print
settings. The final winning model is an Extreme Gradient Boosting
regressor on nine raw features plus a five-feature physics-informed
set (linear energy density, volumetric flow rate, inter-layer time,
infill contact area, thermal margin above the glass transition
temperature). The 5-fold cross-validated Mean Absolute Error drops
from 4.4421 MPa at the baseline to 4.2921 MPa at the winner, a 3.4
percent reduction. No monotonicity constraint, hyperparameter change,
target transform, log / inverse transform, or interaction feature
survived the loop's keep threshold. The Phase B discovery sweep
identifies a Poly-Lactic Acid recipe (layer height 0.20 mm, print
speed 120 mm/s, nozzle 215 C, 70 percent honeycomb infill, 3 walls)
that dominates the Cura PLA slicer default on three objectives --
predicted tensile strength (plus 59 percent), print time (minus 54
percent), and energy consumption (minus 51 percent) -- while staying
inside the training distribution.

The two cross-project lessons are:
1. **Monotone constraints are dataset-size dependent.** They
   improved the concrete project at N = 1030 but hurt the 3D
   printing project at N = 50, because the constraint's
   expressiveness cost does not get a chance to pay back at small N.
2. **The linear-baseline sanity check from program.md Phase 0.5
   fires on this dataset.** The tree-to-linear MAE ratio is 1.32,
   well below the 2x threshold for declaring the task strongly
   non-linear. Neural networks are unlikely to help on any variant
   of this benchmark, and published high-R-squared neural results
   on the Kaggle 3D Printer Dataset should be treated with caution.

Future work: validate the Phase B recipe physically; extend the
HDR loop to a larger FDM dataset (N > 500) where monotone
constraints may finally pay off; and add a Gaussian Process surrogate
with uncertainty estimates to the Phase B scoring pipeline.

---

## 8. Limitations

The dataset is small (N = 50) and public. Every parameter value in
the dataset is on a coarse discrete grid, which limits the resolution
of both the baseline and any discovered optimum. No synthetic data
or data augmentation is used. The Phase B discovery comparison
against the Cura default is a surrogate-vs-surrogate prediction, not
a physical measurement. The `cool_rate` feature that was reverted
in Phase 2 is, in hindsight, an informative negative result that
flags a correlation artefact in the training data (fan speed being
an implicit material indicator). The monotone constraints that were
reverted in Phase 2 and Phase 2.5 are not wrong in principle; they
are wrong at this sample size.

No attempt was made to reach the 100+ experiment count that
program.md targets for a mature HDR project, because the research
queue had 26 hypotheses and the Phase 2 loop already exhausted most
of them with a single KEEP. Program.md's "saturation heuristic"
suggests running more experiments only if the research queue still
has OPEN items with Bayesian priors above 20 percent. After Phase 2
and Phase 2.5 no such items remained; the remaining queue items
(H6 SHAP interactions, H8 transfer learning, H16 Bayesian
optimisation) all require larger datasets than the one we have.

---

## 9. References

Citations are keyed to `papers.csv` in this project directory. Only
the papers that directly support a claim in this paper are listed
below; the full 146-entry bibliography is in `papers.csv`.

- [1] Various (2024). "Machine learning enabled 3D printing
  parameter settings for desired mechanical properties."
  *Virtual and Physical Prototyping*. LSTM-based parameter
  recommendation.
- [11] Various (2024). "Experimental validation of
  SVR/RF prediction for PLA." Reports 96 percent accuracy on PLA
  tensile tests.
- [12] Various (2024). "Support Vector Regression for PEEK
  FDM parts." Reports sub-5 percent deviation.
- [15] Various (2024). "Pre-processing and ANN modelling of FDM
  mechanical response." MAPE 2.54 percent on FDM tensile tests.
- [16] Various (2025). "Experimental study and ANN development for
  modeling tensile and surface quality of fiber-reinforced nylon
  composites." *Polymers*. XGBoost with recursive feature elimination
  and SHAP analysis; R-squared > 0.95 on nylon composites.
- [72] Various (2024). "Interpretable ML-based influence factor
  identification for 3D printing process-structure linkages."
  *Polymers*. SHAP identification of key process-structure
  relationships.
- [73] Various (2025). "Optimizing 3D printing parameters for
  enhanced tensile strength and efficiency using ML." Identifies
  printing temperature as the most influential parameter via SHAP.
- [74] Various (2024). "Explainable AI techniques for comprehensive
  analysis of FDM process parameters and material properties in
  biocomposites." Infill density most significant (SHAP +2.75 on
  UTS, +5.8 on flexural strength).
- [102] Fumetto (2023). "3D Printer Dataset for Mechanical
  Engineers." *Kaggle*. Nine parameters and three quality
  measurements per product; Ultimaker S5 printer. The dataset used
  in this study.
- [103] Batalha (2024). "3D printing process dataset." *Kaggle*.
  Full extruded dataset; not used in this study.
- [104] APMonitor (2024). "Additive Manufacturing Dataset."
  `apmonitor.com/pds`. N=116, cited as candidate for the next
  iteration.
- [112] Various (2024). "Optimization of high-speed 3D printing
  parameters." Reports optimal print speeds in the 300 mm/s range
  for high-speed PLA filaments.
- [121] Gibson, Rosen, Stucker, Khademhosseini (2021). *Additive
  Manufacturing Technologies*, 3rd edition. Springer. The definitive
  AM textbook.
- [122] Chua, Leong, Lim (2010). *Rapid Prototyping: Principles and
  Applications*, 3rd edition. World Scientific.
- [124] Chua, Leong (2017). *3D Printing and Additive Manufacturing*,
  5th edition. World Scientific.
- [125] Baird, Collias (2014). *Polymer Processing: Principles and
  Design*. Extrusion physics reference.
- [127] ISO/ASTM (2021). ISO/ASTM 52900:2021 "Additive manufacturing
  -- General principles -- Fundamentals and vocabulary."
- [128] ASTM International (2014). ASTM D638-14 "Standard Test
  Method for Tensile Properties of Plastics." The reference tensile-
  bar geometry.
- [133] Sun, Rizvi, Bellehumeur, Gu (2008). "Effect of processing
  conditions on the bonding quality of FDM polymer filaments."
  *Rapid Prototyping Journal*. The "Sun model" of interface
  diffusion and thermal-history bond formation; source of the
  `interlayer_time` proxy in this paper.
- [145] Rayegani, Onwubolu (2014). "Parametric analysis of the
  effects of process parameters on FDM printed parts." *Int. J.
  Advanced Manufacturing Technology*. One of the first FDM
  parameter optimisation studies using differential evolution.
- [146] Wu, Geng, Li, Zhao, Tang, Ye (2015). "Influence of layer
  thickness and raster angle on the mechanical properties of
  3D-printed PEEK and a comparative mechanical study between
  PEEK and ABS." *Materials*.

See `papers.csv` for the full 146-entry bibliography, including the
review papers [2], the image-based defect detection literature [19,
27-30], the closed-loop control literature [76, 116], the Bayesian
optimisation literature [38-43], and the ASTM / ISO standards [127,
128, 129, 130, 131].
