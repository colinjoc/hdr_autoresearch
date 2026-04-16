# Blind Reviewer Report — UK Gender Pay Gap 2017-2025

**Reviewer**: Independent Phase 2.75 (retroactive, blind to authors)
**Artefact under review**: `paper.md` (v. Phase 3, dated 2026-04-16), `analysis.py`, `discoveries/*.csv`
**Date of review**: 2026-04-15

---

## Decision

**Major revisions required.** The descriptive findings appear reproducible from the code, and the question is well motivated. However, the paper makes quantitative claims ("1.2pp narrowing", "61.1% of firms narrowed", "late filers have smaller gaps", "0.25pp/year") without a single confidence interval, hypothesis test, or controlled comparison. None of the causal language in §5.1 ("mandatory-disclosure mechanism … driving modest genuine reform") is supported by the analysis as run. Existing CSVs are sufficient to fix most of this without any new data collection. I therefore decline to accept until the four mandated experiments below are completed and integrated into §4/§6.

---

## Headline concerns

1. **No uncertainty quantification anywhere.** The headline 1.19pp population narrowing and 2.10pp within-firm narrowing are reported as point estimates, but the paper does not say whether either is statistically distinguishable from zero, nor how sensitive the 61.1%-narrowed share is to sampling noise. With n=5,259 within-firm pairs and n≈10k annual cross-sections, bootstrap CIs are cheap and should be mandatory before any "measurable progress" claim.

2. **"Late filers have smaller gaps" is an uncontrolled comparison and likely a size confound.** The paper already shows that (a) smaller/mid-size bands (250-999) have the *largest* gaps, (b) the largest employers have the smallest gaps, and (c) late-filer cohort differs by size/newness. The raw 7.0% vs 9.4% comparison ignores this. It could equally reflect "late filers are disproportionately the very-largest or sub-250 voluntary filers" — i.e. Simpson's-paradox territory. The paper acknowledges this informally ("late filers are smaller, newer") but does not condition on `EmployerSize`. Readers will take away the headline, not the caveat.

3. **COVID filing waiver (2019 at 0% late, 2020 reopening) is flagged but not handled.** The 2019-2021 window straddles a structural regime break. The "monotonic post-COVID decline" claim in §4.1 needs either (a) exclusion of 2019-2021 from the trend fit or (b) a piecewise fit with a COVID dummy. The current unconditional median-of-medians trajectory confounds secular narrowing with COVID composition effects (e.g. 2019 has only 7,055 rows vs ~10.5k in other years — an obvious compositional shock).

4. **Firm-identity by string match is a known-weak link that is never quantified.** The paper uses `EmployerName` for the 5,259-firm panel but also has `EmployerId`, `CompanyNumber`, and `CurrentName` in the schema (I can see these in the 2025 CSV header). There is no sensitivity analysis on which identifier is used, and no estimate of how many firms are lost / double-counted under each. This matters because the within-firm headline is the paper's strongest claim.

5. **SicCodes sit unused.** The paper explicitly flags "not sector-specific" as a limitation (§5.2) but `SicCodes` is in the schema, already loaded, and sufficient for at least a 1-digit SIC division cut. This is a 20-line addition and would convert a limitation into a result.

6. **No formal hypothesis test on the within-firm change.** A sign test or Wilcoxon signed-rank on the 5,259 paired deltas is trivial and would let the paper state "median within-firm reduction is significant at p<…". Without this, the 2.10pp number is a summary statistic with no inferential content.

7. **"Entry/exit compositional effect accounts for about half of progress" (§4.2) is stated without a decomposition.** A proper Oaxaca-Blinder-style or simple panel-unbalanced-vs-balanced side-by-side is needed to back the 50/50 claim.

---

## Mandated experiments

All four use existing CSVs in `data/raw/` — no new downloads needed.

### M1 — Bootstrap CIs on every headline number *(status: RUN_RV)*
Generate 1,000 bootstrap resamples (firm-level cluster bootstrap for annual medians; pair-level bootstrap for the within-firm panel). Report 95% CIs on:
- Annual median-of-medians for 2017 and 2025 (and the 2025 − 2017 delta)
- Within-firm median delta (5,259 pairs)
- Share of firms with Δ<0 (currently 61.1%)
- Late vs on-time median gap difference
**Acceptance**: Every point estimate in §4 is replaced with "X [95% CI: lo, hi]". Any CI that crosses zero must be flagged in the abstract.

### M2 — Size-stratified late-filer analysis *(status: CONTROL)*
Recompute the "late filers have smaller gaps" claim within each `EmployerSize` bucket (6 strata). Report median gap for late vs on-time *within each size band*, plus an overall estimate from a size-weighted average. If the within-stratum difference reverses or vanishes, the §4.3 narrative is wrong and must be rewritten. Also report a logit/OLS regression of `DiffMedianHourlyPercent` on `SubmittedAfterTheDeadline` controlling for `EmployerSize` and `reporting_year` fixed effects.
**Acceptance**: Table analogous to §4.4 but split by late/on-time. Concern #2 resolved either way.

### M3 — COVID regime handling on the trend *(status: TEMPORAL)*
Refit the population trend with three specifications:
(a) OLS of annual median on year, 2017-2025, no dummy
(b) Same, excluding 2019-2021
(c) OLS with `covid_period` indicator (2019-2021) and linear trend
Report all three slope coefficients and CIs. If the "0.25pp/year" headline survives only specification (a), the abstract claim is fragile and must be qualified.
**Acceptance**: New §4.1 subsection "COVID sensitivity". The slope in §5.1 becomes a range.

### M4 — Firm-identity robustness + SIC 1-digit sectoral cut *(status: DIAG)*
Two deliverables in one experiment:
(a) Re-run the 2017-vs-2025 within-firm panel three times, using `EmployerName`, `CompanyNumber`, and `EmployerId` respectively as the join key. Report n-matched and median delta under each. Any divergence >10% in n-matched or >0.3pp in median delta is a material finding.
(b) Extract the first SIC code per row, map to 1-digit SIC division (A-U), and report annual median `DiffMedianHourlyPercent` by division for 2017 and 2025. At minimum, identify the top-3 best-improving and worst-improving divisions.
**Acceptance**: New §4.5 "Firm identity robustness" + new §4.6 "Sectoral breakdown". §5.2 limitation on SIC is removed.

### M5 (optional, stretch) — Signed-rank test on within-firm deltas *(status: RUN_RV)*
Wilcoxon signed-rank on the 5,259 paired (2017, 2025) gaps. One line of code. Lets §4.2 state significance.

---

## Things done well

1. **Real data, full archive.** Nine years, ~94k rows, all downloaded from the primary source. No synthetic shortcuts. Complies with the "real data first" principle.
2. **Clear primary question.** "Has the gap moved, and is it composition or within-firm?" is a sharp, tractable framing that the data can in principle answer.
3. **Honest limitations section.** §5.2 and §6 openly flag threshold truncation, lack of intersectionality, lack of causal identification, and the 2019 COVID anomaly. This is better-than-average self-criticism.
4. **Sensible dual reporting of median-of-medians and mean-of-medians** as a robustness check on the population summary.
5. **Code is readable and reproducible.** `analysis.py` is ~140 lines, runs end-to-end from `data/raw/*.csv` to `discoveries/*.csv` and charts, and the numbers in the paper match the CSVs I was able to inspect.
6. **The within-firm panel framing** (5,259 firms appearing in both 2017 and 2025) is the right methodological move for separating composition from reform. It just needs uncertainty and an identifier-robustness check.
7. **Ireland DiD flagged as the natural follow-up** (§5.2) — correct identification strategy, appropriately deferred rather than faked.

---

**Reviewer sign-off pending**: re-review after M1-M4 completed and paper updated. Expect resubmission within one iteration cycle.
