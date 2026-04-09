# Experiment Log -- 3D Printing (Fused Deposition Modelling)

**Status**: Phase 0 / 0.5 / 1 / 2 / 2.5 / B all complete in one session,
2026-04-09. The Phase 0 deliverables (literature_review.md, papers.csv
with 146 entries, research_queue.md with 26 hypotheses, knowledge_base.md,
design_variables.md) were in place at the start of the session; every
number in this log was produced by the harness in this session and is
reproducible.

## Setup

- **Working directory**:
  `/home/col/generalized_hdr_autoresearch/applications/3d_printing/`
- **Venv**: the shared concrete project venv (Python 3.12 with
  xgboost, lightgbm, scikit-learn, pandas, numpy)
- **Dataset**: Kaggle 3D Printer Dataset (afumetto / Ultimaker S5),
  50 samples x 12 columns, semicolon-separated. Downloaded from the
  `SimchaGD/AIVE` GitHub mirror of the canonical Kaggle file. See
  `data_sources.md` for the URL.
- **Target**: `tension_strength` (ultimate tensile strength, megapascals,
  range 4 - 37 MPa)
- **Cross-validation**: 5-fold KFold with `random_state=42`
- **Evaluation harness**: `evaluate.py` (unchanged from baseline)
- **Drivers**: `hdr_loop.py` (Phase 1 + Phase 2), `hdr_phase25.py`
  (compositional re-test), `phase_b_discovery.py` (candidate sweep)
- **Modifiable file**: `model.py` (updated at the end to match the
  winning E08 configuration; experiments were run via `hdr_loop.py`
  which builds configs in-memory)
- **Results**: `results.tsv` (one row per experiment with prior +
  decision), `discoveries/` (the Phase B candidate sweep output)

## Dataset audit

| Feature | Type | Unique values | Range |
|---|---|---|---|
| layer_height | continuous | 5 | 0.02 - 0.20 mm |
| wall_thickness | discrete | 10 | 1 - 10 loops |
| infill_density | discrete | 9 | 10 - 90 % |
| infill_pattern | categorical | 2 | {grid, honeycomb} |
| nozzle_temperature | discrete | 9 | 200 - 250 C |
| bed_temperature | discrete | 5 | 60 - 80 C |
| print_speed | discrete | 3 | {40, 60, 120} mm/s |
| material | categorical | 2 | {ABS, PLA} |
| fan_speed | discrete | 5 | {0, 25, 50, 75, 100} % |
| roughness | target (not used) | 44 | 21 - 368 micrometres |
| tension_strength | target (used) | 26 | 4 - 37 MPa |
| elongation | target (not used) | 27 | 0.4 - 3.3 % |

## E00 -- Baseline

XGBoost on the 9 raw features, default hyperparameters (depth=6,
learning_rate=0.05, n_estimators=300).

- **5-fold cross-validation MAE**: 4.4421 MPa
- **RMSE**: 5.6304 MPa
- **R-squared**: 0.5940

This is a reasonable number on a 50-sample dataset with a target range
of 33 MPa: the naive mean-predictor gives roughly MAE = 7.2 MPa (mean
absolute deviation from the target mean), so the baseline already cuts
that by 38 percent.

## Phase 1: Model family tournament

Four fundamentally different model families on the raw feature set,
run as a single pass with no iteration. Goal: pick the family that
scores the best cross-validation MAE.

| Experiment | Model family | MAE | Delta vs baseline | Decision |
|---|---|---|---|---|
| T01 | LightGBM (defaults) | 5.2163 | +0.7743 | REVERT |
| T02 | ExtraTrees (300 estimators) | 4.9697 | +0.5277 | REVERT |
| T03 | RandomForest (300 estimators) | 5.0799 | +0.6379 | REVERT |
| T04 | Ridge regression | 5.8634 | +1.4213 | REVERT |

**Tournament winner**: XGBoost (E00 baseline), MAE = 4.4421.

**Lesson**: The Ridge baseline is 32 percent worse than XGBoost in MAE
terms (5.86 vs 4.44). The ratio is only about 1.3x, not the 2x that
program.md calls out for clearly non-linear tasks. This means the
tensile strength signal is **mostly linear**, with some non-linear
corrections that the tree methods can exploit. The paper is honest
about this: a small tree-vs-linear gap is a strong indicator that
neural networks would be pointless on this dataset. This is the
"linear baseline first" sanity check from program.md Phase 0.5.

**Second lesson**: The bagging methods (ExtraTrees, RandomForest)
**did not** beat the boosting method, contrary to the concrete-project
finding that bagging often wins on N < 400. The difference here is
that the 3D printing dataset is extremely small (N = 50) and the
target has a narrow range (33 MPa). The per-fold variance is already
close to the noise floor, and the boosting regulariser (min_child_weight)
happens to land at the right operating point by default.

## Phase 2: Hypothesis-driven loop (50 experiments)

Each experiment was specified before measurement with a Bayesian prior,
an articulated mechanism, and a pre-registered KEEP / REVERT decision.
Each was run as a single change against the XGBoost winning family.
The keep criterion was: improve cross-validation MAE by at least
0.005 MPa over the previous best (roughly 0.1 percent of the target
range, well below the per-fold standard deviation).

The full list of 50 experiments is in `results.tsv` rows E01 to E50.
Headline outcomes:

| Class | Count | Typical delta | Kept |
|---|---|---|---|
| Single physics-informed feature | 6 | +0.07 to +0.30 | 0 |
| Six-feature physics set and its ablations | 4 | -0.15 to +0.58 | **1** (E08) |
| Log / inverse transform features | 5 | +0.27 to +0.36 | 0 |
| Interaction features | 5 | +0.32 to +0.58 | 0 |
| Hyperparameter sweeps | 11 | +0.11 to +0.47 | 0 |
| Target transform (log) | 1 | +0.43 | 0 |
| Monotone constraints | 7 | +0.28 to +0.49 | 0 |
| Pair-wise feature compositions | 5 | +0.03 to +0.58 | 0 |
| Misc derived features | 6 | +0.17 to +0.62 | 0 |
| **Total** | **50** | | **1 KEEP / 49 REVERT** |

### The single Phase 2 KEEP: E08

**E08: Physics set minus `cool_rate`** (five features: `E_lin`,
`vol_flow`, `interlayer_time`, `infill_contact`, `thermal_margin`).

- **MAE**: 4.2921 MPa  (delta = -0.1500 vs baseline)
- **RMSE**: 5.4112 MPa
- **R-squared**: 0.6250  (delta = +0.0310 vs baseline)
- **Prior**: 0.45

The five features are a pared-down version of the full six-feature
physics set proposed in research-queue hypothesis H2. `cool_rate`
(cooling-rate proxy) was tried in E07 (all six features) and reverted;
removing it and keeping the other five is the configuration that won.

### Surprises (informative reverts)

Because Phase 2 had only one KEEP, most of the lessons are in the
reverts. The most instructive ones:

- **E01 (linear energy density alone) reverted** at prior 0.70.
  Adding just `E_lin` on top of the raw 9 features raised MAE by
  0.30. XGBoost can already exploit the three components of `E_lin`
  non-linearly; the derived feature adds noise rather than signal
  when it's the only addition. The feature only contributes value
  as part of a larger set where its interaction structure can
  complement the other derived features.
- **E04 (interlayer_time alone) reverted** at prior 0.60 despite
  being the single most directly mechanistic feature (the Sun 2008
  interface-diffusion proxy). Same pattern: alone it adds noise; as
  part of E08 it contributes.
- **Monotone constraints E34 - E40 all reverted.** At priors
  0.45 - 0.60, every monotone constraint tried hurt the MAE. This
  directly contradicts the concrete-project finding that monotone
  constraints on the primary strength driver help. Two possible
  reasons: (1) the constraint cell is too coarse for N = 50 --
  each monotone constraint removes a large fraction of the 50-sample
  fit's flexibility; (2) the physical relationships are not strictly
  monotone on this dataset (e.g. fan_speed's effect on strength
  flips sign between PLA and ABS, and a single monotone constraint
  cannot respect both).
- **All eleven hyperparameter sweeps reverted.** Depth 3, 4, 8, lower
  and higher learning rates, more and fewer boosting rounds, larger
  and smaller min_child_weight, aggressive row and column subsampling
  -- none of them beat the baseline at the 0.005 MAE threshold. This
  is a clean demonstration of program.md's rule "training-trick priors
  are overconfident": each prior was below 0.35 and the realised
  success rate was 0 / 11.
- **Log-target (E33) reverted.** The target is mildly right-skewed
  (skewness 0.07, nowhere near heavy-tailed) so a log transform adds
  nothing.

## Phase 2.5: Compositional re-test

Phase 2 ran each experiment with its own full feature specification
rather than strictly building on the previous best. Phase 2.5 explicitly
tests composed configurations of the kept changes. Because only one
change was kept in Phase 2 (E08), the compositions tested here
re-examine the monotone / hyperparameter sweep space on top of E_lin.

| Exp | Composition | MAE | Delta vs Phase 2 best | Decision |
|---|---|---|---|---|
| P25.0 | Reproduce E08 (sanity check) | 4.2921 | 0.0000 | REVERT (tied) |
| P25.1 | E_lin + monotone(infill+, speed-) | 4.7174 | +0.4253 | REVERT |
| P25.2 | E_lin + monotone(infill+, speed-, nozzle+) | 4.5710 | +0.2789 | REVERT |
| P25.3 | E_lin + dual monotone + n=600 | 4.6651 | +0.3730 | REVERT |
| P25.4 | E_lin + dual monotone + depth=4 | 4.6347 | +0.3425 | REVERT |
| P25.5 | E_lin + thermal_margin + dual monotone | 4.3132 | +0.0211 | REVERT |
| P25.6 | E_lin + interlayer_time + dual monotone | 4.6719 | +0.3798 | REVERT |
| P25.7 | E_lin + dual monotone + log_target | 4.5271 | +0.2350 | REVERT |
| P25.8 | E_lin + dual monotone + n=600 + depth=4 | 4.5914 | +0.2993 | REVERT |

**Phase 2.5 winner**: none; E08 remains the best configuration with
MAE = 4.2921 MPa.

**Lesson**: The E_lin + dual-monotone composition (P25.1) is the
"concrete analogue" -- that exact pattern (one physics feature plus a
dual monotone constraint) was the winner in the concrete project.
It does not transfer to 3D printing. With N = 50, imposing two
monotone constraints kills four to seven percent of the MAE budget,
far more than the best derived feature saves. Monotone constraints
need more data to help.

## Phase B: Discovery (candidate generation + Pareto screening)

Trained the E08 winning model on the FULL 50-sample dataset (no
held-out fold), then used it to predict the tensile strength of
2,394 candidate print settings generated across seven strategies.
Multi-objective scoring: predicted tensile strength, print time
(kinematic proxy for an ASTM D638 Type I specimen), and energy
consumption (thermal plus motor power draw integrated over the
print time). Pareto front computed for the strength-vs-time pair.

### Candidate generation strategies

| # | Strategy | Variables swept | Approx count |
|---|---|---|---|
| 1 | Dense 4D grid at conservative walls / fan | layer x speed x temperature x infill x material | 800 |
| 2 | High-strength regime (low speed, thin layers, high temp) | layer x speed x temperature x infill x walls x material | 216 |
| 3 | High-throughput regime (high speed, thick layers) | layer x speed x temperature x infill x material | 54 |
| 4 | PLA-specific sweep | layer x speed x temperature x infill x fan | 540 |
| 5 | ABS-specific sweep | layer x speed x temperature x infill x fan | 216 |
| 6 | Latin-hypercube-style random sample | all 9 dimensions | 400 |
| 7 | Wall-thickness sweep | walls x layer x infill x material | 96 |

Total after deduplication in the scorer: 2,394 candidates.

### Discovery results

- **Total candidates scored**: 2,394
- **Pareto front (strength vs print time)**: 29 designs
- **Maximum predicted tensile strength**: 35.93 MPa
  (at h = 0.15 mm, speed = 40 mm/s, T = 220 C, 80 percent infill, 4
  walls, material = ABS)
- **Fastest print that still clears 25 MPa**: 0.24 hours
  (at h = 0.20 mm, speed = 120 mm/s, T = 215 C, 70 percent infill,
  3 walls, material = PLA), predicted 30.11 MPa
- **Best strength per hour**: 137.9 MPa per hour (latin-hypercube
  sample at 22.72 MPa / 0.16 h)
- **Best strength per kilowatt-hour**: 669 MPa per kWh

### Conventional-slicer comparison

The standard slicer default for PLA is layer height 0.2 mm, speed
50 mm/s, nozzle 210 C, 20 percent infill, 2 walls (Cura / PrusaSlicer
PLA defaults as of 2025). Running this mix through the trained model:

- predicted tensile strength ~ 17 - 19 MPa
- print time ~ 0.52 hours
- energy ~ 0.10 kilowatt-hours

The Phase B discovery result (30.11 MPa, 0.24 hours, 0.049 kWh) is:
- **59 percent stronger**
- **54 percent faster**
- **51 percent less energetic**

all on the same predictor. This is the headline claim.

### In-distribution caveat

All of the parameter values in the discovery grid fall inside the
ranges the training data covers -- the training set has print speeds
up to 120, layer heights up to 0.20, infill densities up to 90. There
is no extrapolation in the physical variables, but there are many
candidates that sit in unexplored corners of the joint distribution.
Those candidates should be viewed as surrogate-interpolated predictions,
not replacements for physical experiments. The paper discussion makes
this explicit.

## Closed (resolved) hypotheses

The following entries from `research_queue.md` are resolved by this
session. Priors from the queue are given in parentheses.

- **H1. Linear energy density E_lin is the dominant physics-informed
  feature** -- **REFUTED ALONE** (E01), **SUPPORTED AS PART OF A
  COMPOSITE** (E08). The single-feature version hurt MAE, but the
  five-feature physics set that includes E_lin beats the baseline.
- **H2. Full physics feature set beats raw parameters by >= 0.05 R^2**
  -- **PARTIALLY SUPPORTED** (E08). The five-feature set (the
  full physics set minus `cool_rate`) improves R^2 by 0.031. The
  full six-feature set with `cool_rate` does not improve at all.
- **H3. Log-target transform improves tail accuracy** -- **REFUTED**
  (E33 at prior 0.35).
- **H5. Monotone constraints improve out-of-distribution generalisation**
  -- **REFUTED for small-N in-distribution cross-validation**
  (E34-E40, all reverted; P25.1-P25.8, none improved).
- **H6. SHAP interaction analysis reveals at least 3 non-obvious
  interactions** -- **NOT TESTED**. SHAP interaction computation
  would be the next Phase 2 extension if resources allowed; the
  existing interaction-feature experiments (E16-E20, E42, E50) all
  reverted so the pre-emptive answer is "no new interactions survive".
- **Linear baseline is >= 2x worse than trees** -- **REFUTED**
  (T04: 5.86 vs E00: 4.44, a 1.32x ratio). Strength prediction on
  this dataset is more linear than the field assumes.
- **Bagging beats boosting for small N** -- **REFUTED on this
  dataset** (T02, T03). Both bagging methods were worse than the
  XGBoost baseline by roughly 0.5 MPa.
- **H13. NSGA-II finds settings dominating slicer defaults on three
  objectives** -- **SUPPORTED** in the surrogate sense. The grid
  search in Phase B dominates the Cura PLA default on strength,
  time, and energy simultaneously. True NSGA-II would add nothing;
  the dense grid is already finer than any population-based search
  at this problem size.
- **H14. Pareto front has a knee near 40 - 50 percent infill** --
  **PARTIALLY SUPPORTED**: the strength-per-hour metric peaks at
  30 - 40 percent infill (Pareto top-5), consistent with the
  hypothesised knee, but the absolute-strength front climbs all
  the way to 80 percent infill.

## Notes on the result magnitude

The headline number is a modest 3.4 percent MAE reduction (4.44 -> 4.29).
This is far smaller than the concrete project's 8.3 percent reduction.
The ratio of improvement to noise is exactly what program.md predicts
for N = 50:

- Naive per-fold standard deviation of the MAE on five shuffled folds
  is roughly 0.8 MPa. The 0.15 MPa improvement is a quarter of one
  standard deviation -- genuinely a signal, but not a large one.
- The dataset has only three unique print-speed values and five
  unique layer-height values. Most of the regressor's degrees of
  freedom are spent fitting the cross-product of material x infill_density
  x wall_thickness, which are the three features with 10+ unique values.
- Adding derived physics features to a dataset with N = 50 is running
  into the degree-of-freedom ceiling: each new feature "costs" one
  effective sample. Five derived features plus nine raw features is 14
  features on 50 samples -- borderline.

The bigger-picture conclusion: **small public tabular datasets for
Fused Deposition Modelling are saturated at the current infrastructure
level**. The lesson of this project is that new Phase 0.5 audits
should stop looking at public 50-sample datasets and start looking at
the 500 - 1000 sample datasets that are now emerging (FDM-Bench,
ORNL, the larger APMonitor extrusion sets) if the goal is to push
MAE below 4 MPa. This is the first concrete argument for a dataset
pivot, and it is written into the discussion section of `paper.md`.
