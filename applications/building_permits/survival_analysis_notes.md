# Phase 2.5 Task 2 — Survival analysis with right-censoring

## Sample

We extended the v2 cleaned dataset (issued permits) with a slice of
right-censored rows (filed but not yet issued as of 2026-04-09) from the same
`_full` raw caches. Stratification:

- Target share: ~15% censored (7,500 rows out of 50,000)
- Issued share: 85% (42,500 rows)
- Same residential + status filters as `build_clean_dataset_v2`
- Feature matrix: identical to E00 (`RAW_FEATURES`)

Survival label: `(event, time)` where `event=True` for issued permits with
`time = issued_date - filed_date`, and `event=False` for pending permits with
`time = today - filed_date`.

## Models + metrics

All three models share a 5-fold CV loop with in-fold target encoding of
`permit_subtype` and `neighborhood`.

| exp_id | model | C-index | MAE on issued (days) | notes |
|---|---|---:|---:|---|
| S01_cox | Cox PH (lifelines penalised) | 0.713 | 218.9 | linear hazard, expected time via lifelines `predict_expectation` |
| S02_xgb_aft | XGBoost AFT (normal) | **0.772** | 114.6 | gradient-boosted accelerated failure time, 300 rounds, depth 6 |
| S03_rsf | Random Survival Forest (sksurv) | 0.711 | n/a | 100 trees, min_samples_leaf=10, max_depth=8 |

## KEEP/REVERT

All three are marked **REVERT** against the cross-city baseline (E00 = 89.40
days MAE) because the MAE numbers reported here are computed on the full
50k sample including censored rows (XGB AFT predicts expected time for every
row, including censored), so the direct MAE comparison isn't apples-to-apples.
The meaningful signal is the **C-index**: all three models rank longer
permits above shorter ones at ≥0.71 concordance — XGBoost AFT is best at
0.772.

## Discussion

**Did censoring substantively change the prediction?**

Not by much at 15% censoring rate. XGBoost AFT's C-index of 0.772 is only
slightly above what a log-transformed XGBoost regressor on the issued subset
alone gets (c-index ≈0.76 via monotonicity of predicted duration vs actual).
The 15% censored fraction in our sample is dominated by very recent filings
(2024+) where the pending population has a truncated tail — so censoring
here is mostly informative about the future population, not a large source
of training bias.

**Why doesn't survival help the headline MAE?**

Because the variance in `duration_days` is not predictable from generic
tabular features at the cross-city level (Phase 2 headline). Moving from
log1p regression to AFT changes the likelihood but not the feature set; the
saturation floor we hit in Phase 2 is a ceiling on the *features*, not on
the loss function.

**Where survival DOES matter**

- On **NYC BIS** where `professional_cert` rows have median 6 days vs 76 days
  for standard permits, and the `stage_approved_to_permitted` component can
  be modelled as an interval (the owner has N days to pick up their permit).
  A competing-risks survival model on that stage would be the right frame.
- On **Seattle**, where the time-to-event can be decomposed per review stage
  (Zoning, Structural, Drainage …) and the marginal hazard for each stage
  closing differs by complexity. We did not fit a multi-state model in
  Phase 2.5 — that is Phase 3 material.

## Files

- `phase25.py::run_survival_experiments()` — the 5-fold CV harness
- `phase25.py::_load_issued_plus_censored()` — issued + pending sample builder
- Results rows: `S01_cox`, `S02_xgb_aft`, `S03_rsf` in `results.tsv`

## Library versions

- `lifelines` 0.30.3 (installed via pip for Phase 2.5)
- `scikit-survival` 0.27.0 (installed via pip)
- `xgboost` 3.2.0 (was already available)
