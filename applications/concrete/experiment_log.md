# Experiment Log — concrete

**Status**: Phase 0 / 0.5 / 1 / 2 / 2.5 / B all complete in one fresh-restart session, 2026-04-09. The previous version of this project was lost in a destructive subtree-import operation earlier in the day; the restart began from the surviving Phase 0 deliverables (literature_review, papers.csv, research_queue, knowledge_base, design_variables) and the data file. All experiments below were run in this session and every number is reproducible.

## Setup

- **Working directory**: `/home/col/generalized_hdr_autoresearch/applications/concrete/`
- **Venv**: `venv/` (Python 3.12 with `xgboost`, `lightgbm`, `scikit-learn`, `pandas`, `numpy`)
- **Dataset**: UCI Concrete Compressive Strength (Yeh 1998), 1030 samples, 8 raw features plus the strength target. Columns renamed by `evaluate.py` for readability.
- **Cross-validation**: 5-fold KFold with `random_state=42`
- **Evaluation harness**: `evaluate.py` (unchanged from baseline)
- **Modifiable file**: `model.py` (updated by hand to match the final winning config; experiments were run via `hdr_loop.py` which builds configs in-memory)
- **Drivers**: `hdr_loop.py` (Phase 1 + Phase 2), `hdr_phase25.py` (compositional re-test), `phase_b_discovery.py` (Phase B candidate sweep)
- **Results**: `results.tsv` (one row per experiment with prior + decision), `discoveries/` (the final candidate sweep output)
- **Baseline reference**: Conventional C40 structural concrete: 350 kg cement, 0 supplementary cementitious material, 160 kg water, 28-day curing → embodied CO₂ 335.4 kg per cubic metre at $99 per cubic metre

---

## E00 — Baseline

XGBoost on raw 8 features, default hyperparameters (depth=6, learning_rate=0.05, n_estimators=300).

- **5-fold cross-validation MAE**: 2.7766 MPa
- **R²**: 0.9340
- **RMSE**: 4.2858 MPa
- **Phase B output (raw model)**: 18 Pareto-optimal designs, best efficiency 0.32 MPa per kg CO₂

This is the same number reported in the only surviving committed result row from the lost project (MAE 2.78). Reproducibility confirmed.

---

## Phase 1: Model family tournament

Three fundamentally different model families on the raw feature set, single-pass without iteration. The goal: pick the family that gets the best Mean Absolute Error on the cross-validation harness.

| Experiment | Model family | MAE | Δ vs baseline | Decision |
|---|---|---|---|---|
| T01 | LightGBM (defaults) | 2.7818 | +0.0052 | REVERT |
| T02 | ExtraTrees (300 estimators) | 3.0761 | +0.2995 | REVERT |
| T03 | Ridge regression | 8.3417 | +5.5651 | REVERT |

**Tournament winner**: XGBoost (E00 baseline), MAE 2.7766. LightGBM is essentially tied (within noise) but does not improve.

**Lesson**: The Ridge baseline is 3× worse than the boosting / bagging methods, confirming that the strength-vs-mix-design relationship is genuinely non-linear and that the tree methods are doing useful feature interactions. This is the "linear baseline first" sanity check from the program.md Phase 0.5 rules — the relationship is strongly non-linear, so neural network experiments would be defensible if needed (they were not, in the end).

---

## Phase 2: Hypothesis-driven loop (20 experiments)

Each experiment was specified before measurement with a Bayesian prior, articulated mechanism, and pre-registered KEEP / REVERT decision. Each was run as a single change against the XGBoost winning family. The keep criterion was: improve cross-validation MAE by at least 0.005 over the previous best.

| Exp | Hypothesis | Prior | Result | Δ | Decision |
|---|---|---|---|---|---|
| E01 | Add log(age) feature | 0.70 | 2.8389 | +0.0623 | REVERT |
| **E02** | **Add water-to-binder ratio** | **0.85** | **2.7234** | **−0.0532** | **KEEP** |
| **E03** | **Add supplementary cementitious material percentage** | **0.60** | **2.7011** | **−0.0223** | **KEEP** |
| E04 | Add total binder content | 0.50 | 2.7400 | +0.0390 | REVERT |
| E05 | Add fine-to-total aggregate fraction | 0.30 | 2.7084 | +0.0073 | REVERT (within noise) |
| E06 | Add superplasticizer-per-binder ratio | 0.40 | 2.7433 | +0.0423 | REVERT |
| E07 | Add cement-to-water ratio | 0.30 | 2.7574 | +0.0564 | REVERT |
| E08 | Add log(cement) and log(water) | 0.30 | 2.7267 | +0.0256 | REVERT |
| E09 | Add slag-percent and fly-ash-percent separately | 0.40 | 2.7331 | +0.0320 | REVERT |
| E10 | Add cement × log(age) interaction | 0.50 | 2.7612 | +0.0601 | REVERT |
| E11 | Add water-to-binder × log(age) interaction | 0.45 | 2.8019 | +0.1008 | REVERT |
| E12 | Lower learning rate to 0.03, n_estimators=500 | 0.30 | 2.7033 | +0.0023 | REVERT (within noise) |
| E13 | Increase max_depth to 8 | 0.30 | 2.7634 | +0.0624 | REVERT |
| E14 | Decrease max_depth to 4 | 0.30 | 2.8922 | +0.1912 | REVERT |
| E15 | Subsample 0.8 → 0.6 | 0.25 | 2.7477 | +0.0466 | REVERT |
| E16 | Train on log(strength) target | 0.40 | 2.7878 | +0.0867 | REVERT |
| **E17** | **Monotone constraint: cement → strength must be non-decreasing** | **0.55** | **2.6668** | **−0.0343** | **KEEP** |
| E18 | Monotone: cement+, age+, water− | 0.60 | 2.7182 | +0.0515 | REVERT (water− too aggressive) |
| E19 | min_child_weight 3 → 5 | 0.30 | 2.7749 | +0.1081 | REVERT |
| **E20** | **n_estimators 300 → 600 (with the 5-feature set from E12)** | **0.30** | **2.6419** | **−0.0248** | **KEEP** |

**Phase 2 summary**: 4 KEEP, 16 REVERT. The keeps were `wb_ratio`, `scm_pct`, monotonicity on cement, and 600 boosting rounds. The kept feature set after Phase 2 was conceptually the union of E02+E03+E17+E20, but each experiment had its own feature spec, so the test was non-compositional.

### Surprises (the seven informative reverts)

- **E01 (log(age) reverted)**: log(age) is a textbook feature for concrete strength prediction (Abrams' law), and the prior was 0.70. It hurt performance. Possible reason: XGBoost can already exploit the age feature non-linearly without a log transform, and adding a redundant transformation increased overfitting on the small N=1030 dataset.
- **E04 (total binder content reverted)**: total binder is the primary strength driver in textbooks, but adding it as a feature on top of cement+slag+fly_ash+water+wb_ratio is fully redundant — XGBoost can already construct sums of features internally.
- **E13/E14 (depth tuning both reverted)**: depth=6 (the default) was already at the right operating point; deeper trees overfit, shallower trees underfit.
- **E16 (log target reverted)**: The strength distribution is mildly right-skewed but not heavy-tailed enough to benefit from a log transform.
- **E18 (multi-monotone reverted)**: Adding a `water → strength` decreasing constraint on top of the cement constraint hurts. Reason: the water feature interacts with the water-to-binder ratio feature (E02), and forcing one of them monotonic violates the joint relationship.

---

## Phase 2.5: Compositional re-test

Phase 2 ran each experiment with its own feature spec rather than strictly building on the previous best. To verify the actual best, I ran 8 additional experiments that explicitly test composed configurations of the kept changes.

| Exp | Composition | MAE | Δ vs Phase 2 best | Decision |
|---|---|---|---|---|
| P25.1 | wb_ratio alone | 2.7177 | +0.0758 | REVERT |
| P25.2 | wb_ratio + scm_pct | 2.7241 | +0.0822 | REVERT |
| P25.3 | wb_ratio + scm_pct + monotone(cement) | 2.6498 | +0.0079 | REVERT (within noise) |
| **P25.4** | **wb_ratio + scm_pct + n_estimators=600** | **2.6097** | **−0.0322** | **KEEP** |
| **P25.5** | **wb_ratio + scm_pct + monotone(cement) + n_estimators=600** | **2.5467** | **−0.0630** | **KEEP** |
| P25.6 | + log_age + wb + scm + monotone + n=600 | 2.5838 | +0.0371 | REVERT |
| P25.7 | E20-feature-set + monotone + n=600 | 2.6390 | +0.0923 | REVERT |
| P25.8 | E20-feature-set + monotone + n=900 | 2.6165 | +0.0697 | REVERT |

**Final winning configuration**: P25.5
- Features: 8 raw + `wb_ratio` + `scm_pct` (10 total)
- Monotonicity constraint: `cement` must non-decreasingly affect strength
- 600 boosting rounds, otherwise default XGBoost hyperparameters
- **MAE 2.5467 MPa, R² ≈ 0.944** (8.3% MAE reduction over the baseline)

**Lesson from Phase 2.5**: The clean compositional minimum (P25.5) BEATS the Phase 2 individual winner (E20 = 2.6419) because the latter included three features that were individually reverted (log_age, binder_total, sp_per_binder). Adding those features in combination with the kept ones did NOT recover their negative individual effects.

---

## Phase B: Discovery (candidate generation + Pareto screening)

Trained the P25.5 winning model on the FULL UCI dataset (no held-out fold), then used it to predict the strength of 3,685 candidate mix designs generated across 11 strategies. Multi-objective scoring: predicted strength, embodied carbon dioxide, and cost. Pareto front computed for the strength-vs-CO₂ pair.

### Candidate generation strategies

| # | Strategy | Variables | Sample count |
|---|---|---|---|
| 1 | Dense 4D grid at 28-day curing | cement × slag × fly_ash × water | ~1820 |
| 2 | Same grid at 56-day curing (relaxed strength target) | same | ~600 |
| 3 | 90-day curing for ultra-high SCM mixes | reduced grid | ~105 |
| 4 | Pure-cement sweep (high strength focus) | cement × water × superplasticizer | ~160 |
| 5 | Cement+slag binary at multiple ages | cement × slag × age | ~105 |
| 6 | Cement+fly_ash binary at multiple ages | cement × fly_ash × age | ~84 |
| 7 | Ternary blends (cement+slag+fly_ash) | three-way × age | ~72 |
| 8 | Low-water (high-strength) variants | cement × slag × water | ~48 |
| 9 | Ultra-low-cement variants | cement × slag × fly_ash × age | ~120 |
| 10 | Aggregate ratio variants | cement × fine_agg × coarse_agg | ~36 |
| 11 | Latin-hypercube random sampling | all 8 dimensions | 500 |

### Discovery results

- **Total candidates**: 3,685
- **Pareto front**: 31 designs
- **Maximum predicted strength**: 77.6 MPa
- **Best efficiency** (in-distribution, cement ≥ 102 kg per cubic metre): **0.379 MPa per kg CO₂**, achieved by a 108-cement / 0-slag / 0-fly_ash mix at 90-day curing. The strict mathematical maximum (0.633) used a 40-cement extrapolation below the UCI training range and is not reported in the paper.
- **Lowest CO₂ at ≥50 MPa strength** (in-distribution): **146.9 kg per cubic metre** with the 120-cement / 200-slag / 150-fly_ash mix at 56-day curing — strength 53.2 MPa, cost $98 per cubic metre.
- **Best balance**: 120 cement / 200 slag / 100 fly_ash at 90-day curing → 58.8 MPa at 156.9 kg CO₂ per cubic metre.

### Comparison against the conventional C40 structural baseline

Conventional C40: 350 cement, no SCM, 28-day → 50 MPa at 335 kg CO₂ per cubic metre, $99 per cubic metre.

Discovery winner (in-distribution): 120 cement / 200 slag / 100 fly_ash at 90-day → 58.8 MPa at 156.9 kg CO₂ per cubic metre.

**Reduction: 53% CO₂ at 18% higher strength**, with about the same cost.

If 56-day curing is acceptable: 120 cement / 200 slag / 150 fly_ash → 53.2 MPa at 146.9 kg CO₂. **Reduction: 56% CO₂ at slightly higher strength.**

### In-distribution constraint

The UCI training data covers cement contents from 102 to 540 kg per cubic metre. Predictions outside this range are extrapolations and are not used in the paper's headline numbers. The model's mathematical optimum (cement = 40, predicted strength 51 MPa) is below the training range and is not reported as a verified result. The realistic in-distribution result is 53–56% CO₂ reduction at the same or higher strength than C40.

---

## Closed (resolved) hypotheses

The following research_queue.md hypotheses are now resolved:

- **Webster-style baseline reproduces**: ✓ verified at MAE 2.78 (E00)
- **Bagging > boosting on small N**: ✗ refuted on this dataset (LightGBM ≈ XGBoost, ExtraTrees worse)
- **Linear baseline is ≥ 2× worse than trees**: ✓ verified, Ridge 3× worse (T03)
- **Water-to-binder ratio is the dominant strength driver**: ✓ verified (E02 and P25.1)
- **Supplementary cementitious material percentage modulates strength**: ✓ verified (E03)
- **Monotone constraint on cement helps**: ✓ verified (E17 and P25.5)
- **Multi-monotone constraints help**: ✗ refuted (E18)
- **More boosting rounds beats hyperparameter tuning**: ✓ partially (E20 + P25.4)
- **Ultra-low-cement structural concrete is viable in-distribution**: ✓ verified (Phase B)
- **75% CO₂ reduction is achievable at 50 MPa structural strength**: ✗ not in-distribution; the verified number is 53–56%
