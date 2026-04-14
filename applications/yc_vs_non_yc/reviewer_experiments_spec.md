# Reviewer Experiment Specifications — RV01..RV07

Each experiment appends one row to `results.tsv` with `status="REVIEW"` and
`exp_id` as listed. Author implements verbatim.

## RV01 — Real ecosystem covariates

**Goal.** Test whether M3 attenuation claim survives actually populating the
ecosystem covariates defined in `design_variables.md` rows 43–50.

**Inputs.** `data/panel.parquet`; a state-year MSA VC density table (preferred:
NVCA PitchBook Venture Monitor state aggregates; acceptable proxy: Census
Business Dynamics statistics `firms_vc_backed_by_state_year.csv`). FRED VIXCLS
daily (free, `pandas_datareader`).

**Code sketch.** Extend `hdr_loop.COV_SETS`:
```python
"M3_real": M2 + ["msa_vc_density_state_year", "is_sf_bay", "is_nyc",
                 "is_boston", "vix_at_filing"]
"M4_real": M3_real + ["quarter_year_vc_total_raised"]
```
Derive `is_sf_bay` from `stateorcountry == "CA"` AND issuer city/state matches
the 9-county Bay Area list; approximate as `state == "CA"` if city
unavailable. Join VIX on `filing_date`. Re-run `run_e06_covariate_ladder`.

**Metrics.** ATT, 95% CI, standardised mean difference on each new covariate.

**Acceptance.** Attenuation claim survives iff |ATT(M3_real) − ATT(M2)| < 1 pp.

## RV02 — Fuzzy-matched treated sample

**Goal.** Test whether expanding beyond exact-name matching changes the ATT.

**Inputs.** `data/yc_companies_raw.json`, `fuzzy_matcher.py`, panel.parquet.

**Code sketch.** Call `fuzzy_matcher.match_yc_to_formd(yc_cohort, seed,
threshold=0.88, state_sanity=True)`. Use rapidfuzz token_set_ratio, require
state match (YC firms tend to DE-incorporate — relax and require at least
sector group match). Rebuild panel with larger treated set. Re-run E02 and
E06 ladder.

**Metrics.** Match rate, n_treated, ATT with CI, overlap with exact-match set.

**Acceptance.** Report results at thresholds {0.85, 0.88, 0.92}. Null holds
iff ATT at match-rate ≥ 30% remains within ±3 pp of current +2.2 pp.

## RV03 — Censoring-corrected ATT

**Goal.** Remove right-censored anchors and re-estimate.

**Inputs.** panel.parquet; horizon H ∈ {24, 36, 60, 84} months.

**Code sketch.**
```python
max_obs = pd.Timestamp("2024-12-31")
eligible = panel[panel.filing_date + pd.DateOffset(months=H) <= max_obs]
```
Re-run `run_e02_psm` and `run_e07_outcome_window` on `eligible`.

**Metrics.** n_treated, ATT, CI per horizon. Report fraction dropped.

**Acceptance.** Null holds iff censoring-corrected ATT(T+5y) within ±2 pp of
uncensored estimate.

## RV04 — Correct-scale randomisation inference

**Goal.** Fix E14: permute within matched strata, re-running matching each
permutation.

**Code sketch.** For each of 1000 perms: (i) stratify panel by
(industrygrouptype, filing_year); (ii) within each stratum permute `is_yc`;
(iii) refit propensity, run PSM, compute ATT. Build permutation distribution.

**Metrics.** Permutation p-value (two-sided) against observed +2.2 pp.

**Acceptance.** Report raw p-value; no strict threshold — this replaces the
current p=0.608 which is at the wrong scale. Budget up to 2 h runtime; if
too slow, reduce to 500 perms with logging.

## RV05 — Balance and overlap diagnostics

**Goal.** Produce the balance table the reader needs.

**Code sketch.** After `psm_nn_match`, compute per-covariate
`smd = (mean_t − mean_c) / sqrt((var_t + var_c)/2)` pre- and post-match. Plot
propensity histograms for treated vs matched controls, and vs unmatched
controls. Compute Hirano-Imbens common-support criterion: fraction of treated
propensities inside `[min(ps|C), max(ps|C)]`.

**Metrics.** SMD per covariate (raw + matched), % treated on common support,
caliper-drop count.

**Acceptance.** All post-match SMD < 0.25; ≥ 95% of treated on common support;
caliper drops reported (currently silently 0). Save to `plots/balance_rv05.png`
and `data/balance_rv05.csv`.

## RV06 — Alternative-accelerator placebo (M3)

**Goal.** Sanity check via Techstars/500 (research_queue M3).

**Inputs.** Scrape Techstars portfolio from their public website; or use
Seed-DB historical snapshot. Same fuzzy-match pipeline as RV02.

**Code sketch.** Replace `yc_cohort` with Techstars 2014–2019 cohort; otherwise
reuse pipeline. Pre-register: if ATT(Techstars) ≈ ATT(YC), interpret both as
selection; if ATT(YC) >> ATT(Techstars), interpret as YC-specific treatment.

**Acceptance.** Report both ATTs with CIs; no strict threshold.

## RV07 — Cox survival of time-to-next-raise

**Goal.** Replace the dichotomised outcome with a survival model (C7 in queue).

**Code sketch.** Use `lifelines.CoxPHFitter`. Event = any later non-amendment D
by same CIK. Duration = days from anchor to next D, or days to 2024-12-31 if
censored. Covariates = M3_real covariates + `is_yc`. Stratify by filing year.

**Metrics.** HR for `is_yc` with 95% CI; proportional-hazards test p-value.

**Acceptance.** Null holds iff HR 95% CI includes 1.0. Report HR regardless.
