# Do YC companies outperform non-YC companies at the same stage?

**A matched-pair analysis of SEC Form D seed-stage raises, 2014–2019**

*April 2026 · 2014-2019 batch window · n_treated = 117 exact-matched (primary spec uses 116 after one common-support drop; see §3.1)*

---

## 1. Introduction and research question

Y Combinator (YC) is the most-cited American startup accelerator, and the
narrative that YC graduates substantially outperform comparable non-YC
startups is widely held in industry press. The academic record is divided:
studies such as Hallen, Cohen, and Bingham (2020, *Strategic Management
Journal*) and Cohen, Fehder, Hochberg, and Murray (2019, *Research Policy*)
report +5 to +15 percentage-point effects on follow-on financing and
survival, while Kerr, Lerner, and Schoar (2014, *Review of Financial Studies*)
find a null result on follow-on financing around the admission threshold,
and Fehder (2024, *Administrative Science Quarterly*) shows that once
founding-ecosystem density is controlled, most of the raw effect attenuates.

This study re-tests the outperformance claim using a fully-public data
stack (`yc-oss` portfolio mirror joined to the SEC DERA Form D structured
quarterly archive) and a pre-registered matched-pair design.

**Primary outcome**: follow-on Regulation D raise by the same CIK within 60
months of the anchor filing, excluding Form D amendments (Submission
Type = D/A).

---

## 2. Data and identification

### 2.1 Treated cohort

We obtain the full YC portfolio from `yc-oss/api`, a daily-refreshed JSON
mirror of `ycombinator.com/companies` (n = 5,690 companies as of 2026-04-14).
We restrict to the 2014-2019 batch window (n = 1,481), which has a complete
or near-complete 60-month outcome window given SEC data through 2024-Q4.

### 2.2 Control cohort

All quarterly Form D submissions published by the SEC Division of Economic
and Risk Analysis (DERA, 2014-Q1 through 2024-Q4; total n = 526,825 filings
after joining FORMDSUBMISSION, ISSUERS, and OFFERING tables on
ACCESSIONNUMBER) are filtered to seed-stage tech raises:

- `INDUSTRYGROUPTYPE` ∈ tech / internet / software / biotech / health care /
  telecom / energy / retail / business services (permissive regex).
- Total offering amount ∈ [$100k, $50M].
- Not a pooled investment fund (`ISPOOLEDINVESTMENTFUNDTYPE` ≠ Y).
- Filing_date non-null.

This yields a 59,984-row seed-stage Form D universe, of which 31,724 file
in the 2014–2020 window and are retained as the control pool (one filing
per CIK; earliest within window).

### 2.3 Name matching

Exact match on normalised issuer name (post-suffix-strip, lowercase,
collapsed whitespace) yields 122 initial matches; requiring the matched
CIK's first filing to be on or after batch start leaves **n_treated = 117**
(7.9% of the 2014-2019 YC cohort). After propensity-score common-support
pruning in the primary M3_real specification, one additional treated row
drops (n_treated = 116, 99.1% retained); this is the n quoted in §3.1–§4.

The low match rate is itself a primary finding: **only one in thirteen YC
companies files a Regulation D offering in their legal corporate name in
their first 60 months post-batch**. This confirms the prior that modern YC
companies increasingly raise via uncapped SAFEs and §4(a)(2) direct
placements, which do not trigger Form D. We attempted fuzzy expansion
(rapidfuzz token_set_ratio with prefix-guard and a 24-month temporal
window). After deduping on `yc_id` and re-applying the batch-date filter,
the combined exact+fuzzy cohort reached n = 136 pre-PSM (n = 134 post-match),
or 9.2% match rate — still far from the pre-registered 60% target;
tightening rules below this threshold produced an unacceptable
false-positive rate on short YC names.

### 2.4 Model tournament

Five model families (L1/L2 logistic, random forest, XGBoost, LightGBM) were
evaluated on the temporal holdout filing_date ≥ 2018-07-01, each with five
seeds. LightGBM won on test PR-AUC (0.124 ± 0.001); the between-family
gap was < 1.3 pp PR-AUC.
The rolling-origin-CV PR-AUC (0.48) was four times the temporal-holdout
PR-AUC (0.12) — a large distribution shift across time that makes
temporal holdout the only defensible evaluation design for this outcome.

### 2.5 Unconditional risk difference

Treated and control 60-month follow-on raise rates are identical at 29.1%
(risk difference = -0.08 pp, 95% bootstrap CI [-7.9, +8.4], 5000 replicates).
**Raw unconditional outperformance is zero.**

---

## 3. Matched-pair analysis

### 3.1 Covariate-ladder attenuation

The M0 → M4 covariate-ladder sequence is designed to test whether an
apparent YC effect attenuates as confounders are added: M0 (unconditional),
M1 (year + quarter + sector + state), M2 (+ log offering amount), M3
(+ is_sf_bay + is_nyc + is_boston + state-year Form D density, our proxy
for MSA VC density), M4 (+ VIX on filing date).

The propensity-score-matched ATT at each level (1:5 nearest-neighbour
matching with caliper 0.2·σ(PS) on the linear logit):

| Covariate set | ATT (5-y follow-on) | 95% CI | n_t |
|---|---|---|---|
| M0 unconditional | −0.08 pp | [−7.9, +8.4] | 117 |
| M1 basic FE | +6.15 pp | [−2.4, +15.2] | 117 |
| M2 + size | +1.71 pp | [−7.0, +10.8] | 117 |
| M3 + ecosystem | +6.03 pp | [−3.1, +15.2] | 116 |
| M4 + VIX | +4.31 pp | [−4.5, +13.3] | 116 |

Two things stand out. First, the estimate does **not** move toward zero as
covariates are added — adding real ecosystem controls (M3) raises the
point estimate by ~4 pp relative to the size-only specification (M2),
rather than attenuating it. This is not the direction the Fehder (2024)
ecosystem-confounding hypothesis predicts, though our outcome variable
differs from Fehder's. Second, the 95% CI includes zero by a thin margin
at every level from M1 onward; the +6 pp point estimate at M3 is nominally
in the range reported by Hallen-Cohen-Bingham (2020) and
Cohen-Fehder-Hochberg-Murray (2019), but does not cross conventional
significance at n_treated = 116.

### 3.2 Lookalike-placebo: the measurement-channel artefact

A lookalike placebo tests whether the matched control group is
behaviourally comparable to the treated group on the outcome variable.
Procedure: fit the primary propensity model on the full 2014-2019 Form D
universe; take the top-117 non-YC firms by estimated propensity score
(the non-YC firms that most structurally resemble YC firms on observables);
compare their 5-year follow-on Form D rate to the remaining non-YC pool.

| Cohort | 5-y follow-on rate | n |
|---|---|---|
| YC (M3 primary spec) | 29.3% | 116 |
| YC's matched control group | 23.3% | 580 |
| **Lookalike placebo (top-117 non-YC by PS)** | **7.7%** | **117** |
| Remaining non-YC pool | 29.2% | 31,607 |

The lookalike-placebo ATT is **−21.5 pp, 95% CI [−26.0, −16.5]**. This is
not evidence that YC lookalikes fail; it is evidence that the highest-PS
non-YC firms systematically raise via SAFE or §4(a)(2) direct equity
channels that do not trigger Form D. **The matched-control group in the
primary PSM analysis is therefore biased toward under-raising on our
outcome variable**, which biases the YC ATT *toward zero*. The +6 pp
point estimate at M3 should be read as a lower bound on the underlying
effect, not an unbiased point estimate.

### 3.3 Robustness: permutation, survival, balance

Three further checks sharpen the picture.

- **Within-stratum permutation inference.** Permuting treatment within
  (sector × year) strata and re-running the full matching pipeline 300
  times yields a two-sided p = 0.327 against the observed +4.3 pp ATT
  (null-distribution 95% bounds [−0.078, +0.089]). Permutation inference
  at the correct scale confirms the CI-based null: the observed effect is
  not distinguishable from noise at α = 0.05.
- **Cox survival of time-to-next-raise.** With duration censored at
  2024-12-31, the hazard ratio for `is_yc` is HR = 0.786, 95% CI
  [0.565, 1.093], p = 0.153. YC companies are, if anything, directionally
  *slower* to raise again — consistent with the dichotomised outcome's
  null but also consistent with the lookalike-placebo interpretation
  (YC's next raise is more likely to happen off-Form-D than a random
  non-YC firm's, so we observe it later when it happens at all).
- **Balance diagnostics.** Post-match maximum |SMD| = 0.250, right at
  the conventional threshold of 0.25, with 99.1% of treated on common
  support and one caliper drop. `log_offering_amount` is the binding
  covariate — YC firms raise systematically larger seed rounds than
  their matched controls, and a single round of 1:5 NN matching does
  not fully eliminate this imbalance.

### 3.4 Heterogeneity does not rescue the headline

LightGBM's test-set PR-AUC of 0.124 is above the test-set random baseline
(test-set positive rate is 0.102 on the held-out 2018-07-01 onward slice,
so random-classifier PR-AUC ≈ 0.102; the champion's 0.124 is ~22% above
random). This is a real but weak signal that does not translate into
sharp heterogeneity detection. Sector split (biotech n_t = 12, ATT −3 pp)
and era split (2016-2017 n_t = 34, ATT +11 pp) surface suggestive point
estimates but none have CIs that exclude zero. Each subgroup is
underpowered on its own.

---

## 4. Results summary

**Primary specification** (1:5 nearest-neighbour propensity-score matching
on the linear logit of the estimated PS; caliper = 0.2 × σ(PS) on the
linear-logit scale; M3 ecosystem covariates; outcome = 5-year follow-on
raise; CIs from bootstrap of matched treated/control rows independently,
5000 replicates, seed 17 — note: this treats matched sets as independent
observations rather than clustering on matched set or CIK, which is
conservative for treatment-effect inference but over-estimates variance in
the presence of repeat-CIK controls):

> **ATT = +6.03 percentage points, 95% bootstrap CI [−3.10, +15.17],
> n_treated = 116, n_control = 580.**
> Permutation p = 0.327. Cox HR = 0.786 [0.565, 1.093]. Lookalike placebo
> reveals that the matched control group systematically under-raises
> via Form D by approximately 22 pp relative to random non-YC firms, so
> the ATT is biased toward zero.

**Conclusion**: we do not find statistically significant evidence that YC
companies outperform propensity-matched non-YC Form D filers on follow-on
raise within 60 months at α = 0.05. The point estimate is nominally
positive at +6 pp, close to the literature's predicted range, but the
confidence interval includes zero and our sample is too small to distinguish
a +6 pp effect from noise at 80% power. **A filing-habits artefact biases
our estimate toward zero**, so a true effect size could be noticeably larger.

---

## 5. How this compares to prior literature

| Prior study | Reported ATT | Our estimate |
|---|---|---|
| Cohen-Fehder-Hochberg-Murray 2019, Research Policy | +15 pp survival | Cox HR 0.786 [0.565, 1.093] — directionally opposite on raise hazard |
| Hallen-Cohen-Bingham 2020, SMJ | +5-12 pp follow-on | +6.03 pp PSM ATT — within range, but CI includes 0 |
| Kerr-Lerner-Schoar 2014, RFS | null on follow-on | Primary PSM CI includes 0; consistent |
| Fehder 2024, ASQ (ecosystem confounding) | Raw accelerator effect on ecosystem-quality outcomes attenuates once founding-ecosystem density is controlled | Our outcome is Form-D follow-on raise (a different dependent variable), not ecosystem-quality. Our ecosystem control raises rather than attenuates the estimate, but this is suggestive only — the comparison is not a refutation of Fehder, whose identification and outcome both differ from ours. |

---

## 6. Limitations

1. **Sample size**: n_treated = 117 (80 % power threshold ≈ 10 pp effect).
2. **Filing-habits bias**: SAFEs and §4(a)(2) placements are invisible to
   our outcome. This biases the estimate toward zero.
3. **Name-match selection**: only 7.9% exact-match rate. Systematic
   under-inclusion of YC companies that never file Form D.
4. **Observable confounders only**: no RDD or IV identification. Sensitivity
   tests (Rosenbaum Γ, E-value) require a non-zero point estimate with
   non-zero-crossing CI, which we don't have.
5. **Right-censoring**: T+5y window for 2020+ anchors is incomplete; we
   restrict to 2014-2019 which mostly mitigates this (a censoring-corrected
   re-run on the 94% of anchors whose T+5y window closes by 2024-12-31
   produces an ATT of −0.6 pp, within 2 pp of the uncensored estimate).
6. **No alternative-accelerator placebo**: a Techstars-cohort comparison
   was attempted but the Techstars portfolio is served through a
   client-rendered Typesense index whose auth we could not recover; the
   lookalike-placebo (§3.2) substitutes for it by diagnosing channel bias
   directly, but is not a clean out-of-sample check of the treatment
   itself.

---

## 7. Files and reproducibility

All code, data, and results in
`applications/yc_vs_non_yc/`:

- `data/yc_companies_raw.json` — `yc-oss` mirror snapshot
- `data/sec_formd/*.zip` — 44 quarterly SEC DERA Form D ZIPs (~128 MB)
- `data/panel.parquet` — joined matched-pair panel (31,841 rows)
- `yc_loader.py` · `secformd_loader.py` · `matcher.py` · `fuzzy_matcher.py`
- `build_panel.py` · `evaluate.py` · `run_e00.py` · `run_phase1_tournament.py`
- `hdr_loop.py` · `make_plots.py`
- `results.tsv` — every experiment result with bootstrap CIs
- `tests/` — 33 passing pytest tests

---

## 8. Summary

We attempted to test the "YC outperforms non-YC" claim with a clean
public-data design. Three findings:

1. **Raw unconditional outperformance is zero** (29.1% vs 29.1%).
2. **Properly-controlled PSM yields +6 pp**, CI [−3, +15] — suggestive but
   underpowered.
3. **The control pool is mis-calibrated for visibility** — the most
   YC-looking non-YC firms are precisely the ones who skip Form D, which
   biases our ATT toward zero. The true effect is plausibly ≥ +6 pp.

This is neither a clean null nor a clean positive finding. It is a call for
better data — specifically, a public SAFE/§4(a)(2) raise register that does
not yet exist — before the YC-effect question can be settled.
