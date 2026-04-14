# Reviewer Experiments Spec — Phase 2.75

All experiments reuse `data/panel.parquet`, the `fit_l2` routine in `hdr_loop.py`, and the existing `classifier_metrics` in `evaluate.py`. Default train-end is 2022-06-01, default threshold is -10%, default features = `BASE_FEATURES`.

---

## RV-1 — Metro-clustered block bootstrap on PR-AUC

**Inputs**: trained L2 model (reuse `fit_l2(train, test, features)` to get `prob_te`, `y_te`), test set's `cbsa_code` column.

**Code sketch**:
```python
rng = np.random.default_rng(17)
metros = test["cbsa_code"].unique()
boots = np.empty(2000)
for b in range(2000):
    sampled = rng.choice(metros, size=len(metros), replace=True)
    idx = np.concatenate([np.where(test["cbsa_code"].values == m)[0] for m in sampled])
    boots[b] = average_precision_score(y_te[idx], prob_te[idx])
ci_lo, ci_hi = np.quantile(boots, [0.025, 0.975])
```

**Metrics**: 95% CI of PR-AUC under metro-clustered resampling; point estimate vs base rate (0.0093).

**Acceptance criterion**: PASS if CI lower bound > 2x base rate (>0.019). FAIL if CI includes base rate.

**Expected result (reviewer prediction)**: CI ~[0.015, 0.085], point 0.044; lower bound below 2x base rate — fails.

---

## RV-2 — Within-metro block-permutation null

**Rationale**: E20 shuffles crash labels IID, which is too weak (destroys both feature-outcome map AND metro structure). For an autocorrelated panel the right null is "permute crash status at the metro level, preserving within-metro temporal clustering."

**Code sketch**:
```python
rng = np.random.default_rng(17)
tr = train.copy()
# Build one outcome per metro (did metro EVER crash in train?)
metro_has_crash = tr.groupby("cbsa_code")["crash_next_12mo"].any()
crash_labels = metro_has_crash.values.astype(int)
perm_prs = []
for b in range(500):
    shuffled = rng.permutation(crash_labels)
    mapping = dict(zip(metro_has_crash.index, shuffled))
    # A row is labelled 1 iff its metro was drawn as "crash" AND the row was
    # originally in the crash window (keeps clustering structure)
    tr2 = tr.copy()
    tr2["fake_y"] = tr2.apply(lambda r: r["crash_next_12mo"] if mapping[r["cbsa_code"]] else 0, axis=1)
    tr2["crash_next_12mo"] = tr2["fake_y"]
    prob2, _, _, _, _ = fit_l2(tr2, test, features)
    perm_prs.append(average_precision_score(y_te, prob2))
p_block = float((np.array(perm_prs) >= 0.0439).mean())
```

**Metrics**: block-perm p-value vs observed PR-AUC = 0.0439.

**Acceptance criterion**: PASS if p < 0.10. FAIL otherwise.

**Expected result**: p in [0.3, 0.6]; block permutation gives even weaker rejection than IID's 0.235.

---

## RV-3 — Collapse test positives to metro-events

**Rationale**: Each crashing metro contributes up to 16 rows of the same crash event (overlapping 12mo windows). True effective n is metro-episode count, not row count.

**Code sketch**:
```python
# For each metro with any crash in test: take ONE row per contiguous crash run
# (use the row with maximum prob_te to be generous to the model).
te2 = test.copy()
te2["prob"] = prob_te
crashed_metros = te2[te2["crash_next_12mo"] == 1].groupby("cbsa_code")
pos_rows = crashed_metros.apply(lambda g: g.loc[g["prob"].idxmax()])
neg_rows = te2[te2["crash_next_12mo"] == 0]
# For negatives also collapse to one row per metro to be fair
neg_by_metro = neg_rows.groupby("cbsa_code").apply(lambda g: g.loc[g["prob"].idxmax()])
collapsed = pd.concat([pos_rows, neg_by_metro])
m = classifier_metrics(collapsed["crash_next_12mo"].values, collapsed["prob"].values)
```

**Metrics**: PR-AUC, ROC-AUC, lift on collapsed-to-metro-events test set; compare to author's row-level 0.0439.

**Acceptance criterion**: PASS if collapsed PR-AUC lift > 2x. FAIL if collapse halves or worse.

**Expected result**: PR-AUC ~0.15 at n=(19 pos + ~885 neg), but with 19 effective positives the CI from RV-1 on this collapsed set will dominate — show both.

---

## RV-4 — Single-feature momentum-only baseline

**Rationale**: E18 (naive threshold-rule at -5% past return) gave ROC 0.64 / PR-AUC 0.025. But the PROPER test is "use zhvi_12mo_ret as a continuous score" — not a threshold rule.

**Code sketch**:
```python
y_te = test["crash_next_12mo"].values
score = -test["zhvi_12mo_ret"].values  # more negative past return = higher score
m = classifier_metrics(y_te, score)
# Compare to L2's 0.0439
```

**Metrics**: single-feature PR-AUC and ROC.

**Acceptance criterion**: PASS (L2 adds value) if L2 PR-AUC / single-feature PR-AUC > 1.5. FAIL if ratio < 1.2.

**Expected result**: single-feature PR-AUC ~0.035-0.045; ratio ~1.0. L2 is essentially the momentum feature plus noise.

---

## RV-5 — Leave-one-metro-out sensitivity

**Code sketch**:
```python
impacts = {}
for metro in test[test["crash_next_12mo"] == 1]["cbsa_code"].unique():
    mask = test["cbsa_code"] != metro
    m = classifier_metrics(y_te[mask], prob_te[mask])
    impacts[metro] = m["pr_auc"]
# Rank by PR-AUC drop
sorted(impacts.items(), key=lambda kv: kv[1])
```

**Metrics**: PR-AUC when each crashing metro is removed; identify any metro whose removal drops PR-AUC by >30%.

**Acceptance criterion**: PASS if no single metro removal drops PR-AUC by more than 25%. FAIL if any single metro removal drops PR-AUC by >30%.

**Expected result**: Clarksdale MS removal will drop PR-AUC substantially (it has 16 of 95 positive rows).

---

## RV-6 — Population-weighted evaluation

**Rationale**: size_rank is present; rural micropolitans get the same weight as Boise or Phoenix. A population-weighted PR-AUC tells us whether the signal matters for metros people actually live in.

**Code sketch**:
```python
from sklearn.metrics import average_precision_score
# Invert size_rank to get approximate pop weight (small rank = big metro)
w = 1.0 / np.sqrt(test["size_rank"].values.astype(float))
# Normalised
w = w / w.mean()
m_weighted = average_precision_score(y_te, prob_te, sample_weight=w)
```

**Metrics**: population-weighted PR-AUC vs unweighted 0.0439.

**Acceptance criterion**: PASS if weighted PR-AUC > 0.02. FAIL otherwise.

**Expected result**: weighted PR-AUC drops to <0.015 because the crashing metros are the small, low-weight ones.

---

## RV-7 — Within-month detrended features

**Rationale**: E02's collapse (ROC 0.59) suggests mortgage features do the work. But mortgage rate is one national time series — it only helps because 2022-23 is uniformly a rate-shock era. Within-month standardise every feature to test if cross-sectional info exists.

**Code sketch**:
```python
panel2 = panel.copy()
for f in BASE_FEATURES:
    g = panel2.groupby("month")[f]
    panel2[f] = (panel2[f] - g.transform("mean")) / g.transform("std").replace(0, 1)
tr, te, feats = split(panel2)
p, y, yt, _, _ = fit_l2(tr, te, feats)
log_exp("RV-7", "L2 on within-month standardised features", y, p, len(tr), float(yt.mean()))
```

**Metrics**: PR-AUC, ROC on demeaned features.

**Acceptance criterion**: PASS if PR-AUC > 0.02 and ROC > 0.62. FAIL if ROC collapses toward 0.55.

**Expected result**: ROC ~0.55-0.60, PR-AUC ~0.012-0.015 — essentially at base rate, confirming the "signal" is mostly a macro-regime indicator not a cross-sectional predictor.

---

## Execution order

1. RV-4 (1 min) — fastest, most damaging if it lands.
2. RV-3 (2 min).
3. RV-6 (2 min).
4. RV-1 (5 min).
5. RV-7 (5 min).
6. RV-5 (10 min).
7. RV-2 (15 min).

Total wall time ~40 min. All reuse existing `fit_l2` and `classifier_metrics`; no new data ingestion, no new dependencies.
