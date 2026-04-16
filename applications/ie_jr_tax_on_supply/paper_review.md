# Phase 2.75 Blind Review: The Judicial-Review Tax on Irish Housing Supply

**Reviewer**: Blind reviewer agent (Phase 2.75)
**Date**: 2026-04-16
**Paper under review**: `paper.md` (current version, treated as `paper_draft.md`)
**Verdict**: MAJOR REVISIONS

---

## Summary assessment

The paper synthesises three predecessor projects into a unified "JR tax" metric. The direct-delay accounting (T01) is the most defensible component. The counterfactual (T05) and indirect channel (E03) are weaker and, in several places, the paper does not adequately distinguish between claims it can support and claims that require stronger identification than the data allow.

---

## Concern-by-concern analysis

### C1: 13 of 22 cases have imputed unit counts — sensitivity is material

The paper reports E11 sensitivity [79,704, 134,304] unit-months but the central 105,504 figure appears in the abstract, title-equivalent, and throughout without qualification. The 9 cases with stated units contribute a fixed 67,908 unit-months — so the imputed 13 cases contribute 37,596 of the central 105,504 (36%). The imputation rule varies ad hoc: some cases get 100 (SHD minimum), some get 200, one gets 300, one gets 400 (Spencer Place), with no documented selection rule beyond case-specific prose. This is not a sensitivity analysis — it is the primary estimate with embedded judgement.

**R1**: Run a structured three-scenario imputation: (a) all imputed cases = 100 (floor), (b) all imputed cases = median of stated cases (median of 9 stated = 450), (c) all imputed cases = 200 (current ad hoc midpoint). Report direct unit-months for each. The abstract must quote the range, not just the point estimate. Additionally, compute the share of total direct unit-months attributable to imputed vs stated cases under each scenario.

### C2: The indirect channel (0-50% JR attribution) is judgement, not estimation

The paper acknowledges this in section 6.2 and caveat 3. However, the abstract reports the combined total [105,504, 110,156, 114,809] as though the three bounds are equally weighted scenarios. The lower bound (0% JR attribution) is arguably the most defensible given that PL-3 could not identify the JR channel from the capacity channel (PL-3 caveat 11). The central 25% figure has no empirical basis — it is not derived from any regression, decomposition, or calibration exercise.

**R2**: Add a results.tsv row explicitly stating the evidential basis for each attribution bound. The paper must state that the 25% central figure is an assumption, not a finding, in the abstract. The indirect channel should be reported as "bounded at [0, 9,305] unit-months" without a "central" point estimate, or the central estimate must be explicitly labelled as illustrative.

### C3: T05 counterfactual assumes exogenous intake — endogenous response narrows the gap

The counterfactual formula is: `shifted_units = completions_Y * (excess_weeks / 52) * housing_share`. This assumes that if ABP had processed cases in 18 weeks, the same number of completions would have occurred, plus the shifted ones. But faster ABP processing would have induced more developer applications (positive feedback), while also potentially increasing the JR filing rate (as more permissions issued = more targets). More fundamentally, the formula treats CSO completions as ABP-determined output, but completions are a 2-3 year lagged function of permissions, construction starts, labour availability, and materials supply. ABP processing time is one input among many. The 16,638-unit gap conflates "ABP delay" with "housing completions shortfall attributable to ABP."

**R3**: Compute the counterfactual under an elasticity-adjusted scenario where faster processing induces (a) 0% additional intake (current assumption), (b) 10% additional intake, (c) 20% additional intake. The additional intake increases the disposed count but also increases the queue, partially offsetting the speed gain. Also note in the paper that completions are a multi-year lag from permissions and that construction-sector capacity constraints bind independently of ABP processing time.

### C4: EUR 52.8M holding cost — discount rate and per-unit assumptions

The EUR 500/unit/month holding cost is attributed to "land finance cost only" at "2% monthly equivalent of 6% annual" on a EUR 300K unit. But 6% annual on EUR 300K = EUR 18K/year = EUR 1,500/month, not EUR 500. The EUR 500 figure appears to assume only the land component of the development cost (roughly one-third of total in Dublin). This should be made explicit. Additionally, the holding cost is applied to the outcome-weighted unit-months (105,504), which includes cases weighted at 0.5 and 0.25 — but the finance cost is borne by the developer regardless of outcome. A refused JR (weight 0.5) still imposes full finance cost during the litigation period.

**R4**: Clarify the EUR 500 derivation in the paper (land-share of development cost, not total unit cost). Test sensitivity: (a) EUR 500 (current), (b) EUR 1,000 (land + part construction), (c) EUR 1,500 (full development cost finance). Also note that the outcome weighting should arguably not apply to the holding cost calculation — a developer pays finance costs whether the JR succeeds or fails.

### C5: The 16,638-unit gap presupposes all delayed units complete within the counterfactual window

The counterfactual adds `shifted_units` to observed completions, implying that faster ABP processing would have resulted in those units being completed in that calendar year. But construction capacity is finite — Ireland has approximately 30,000-35,000 completions/year at current capacity. The 2023-2024 counterfactual (6,036 + 6,309 = 12,345 units) would require 38,731 and 40,486 completions respectively, which is 15-20% above peak observed output. This may exceed construction-sector absorptive capacity. The gap in 2023-2024 is driven almost entirely by the 24-week excess in those years — but if ABP had been faster, would construction firms have had labour and materials to deliver an additional 12,000 units?

**R5**: Compute the counterfactual with a construction-capacity ceiling of (a) 35,000 (current trajectory), (b) 38,000 (optimistic), (c) no ceiling (current assumption). Report the gap under each scenario. The 2023-2024 figures are the most affected.

### C6: Over-claiming causation from the rho accounting identity (inherited from PL-3)

Section 5.9 reports the JR component of rho as 0.165, then section 6.2 uses this to argue the 25% JR attribution is "consistent with" the queueing evidence. But PL-3's own paper (section 5.5, caveat 11) explicitly states: "with n = 10 annual observations we cannot separate the JR-feedback channel from the capacity-queueing channel." The rho decomposition is an accounting exercise (JR defense work = X% of total case-equivalents), not a causal identification. The 7x case-multiplier for JR defense work is a calibration assumption with no stated source.

**R6**: Add a results.tsv row documenting the 7x case-multiplier source (or flag it as an assumption). The paper must not use the rho decomposition to support the 25% indirect attribution — at most it can be cited as "not inconsistent with" a non-zero JR share. The 7x multiplier sensitivity: run T03 at 3x, 5x, 7x, 10x and report the rho_jr_component for each.

### C7: Paper internal inconsistencies

Several numerical inconsistencies between the paper and results.tsv:

- Section 5.1 says "For the clean 2018-2021 window only: 93,708 unit-months (16 cases)" but E02 in results.tsv says 88,422 for 2018-2021. The annual decomposition (E14.*) sums to 6,432 + 5,346 + 58,818 + 17,826 = 88,422, matching E02 but not section 5.1.
- Section 5.2 says 2020 was "67,434 unit-months" but E14.2020 says 58,818. The sum of the section 5.2 table (6,432 + 5,346 + 67,434 + 14,496 + 11,796 = 105,504) equals the total, suggesting the table was reverse-engineered to sum to 105,504 rather than computed from the case data.
- Section 5.6 says "17 of 22" Dublin cases; E05 says "18/22 cases, 5041 units." The case list shows 17 Dublin cases (counting the list in analysis.py).
- Section 5.8 reports [79,704, 134,304] for E11 sensitivity, but E11 in results.tsv says [90,804, 150,204]. These are materially different.

**R7**: Reconcile all numbers between paper and results.tsv. Every figure in the paper must trace to a specific results.tsv row. Fix the 2020 unit-months figure, the Dublin count, and the sensitivity range. Add a cross-check experiment that sums E14.* and verifies it equals E01.

---

## Mandated experiments

| R# | Mandate | Type |
|----|---------|------|
| R1 | Three-scenario imputation sensitivity (floor/median/ad-hoc) with imputed-vs-stated share | Sensitivity |
| R2 | Indirect channel: explicitly label 25% as assumption; report without central point estimate or label it illustrative | Writing + results.tsv |
| R3 | Endogenous-intake counterfactual at 0%/10%/20% additional intake; note completions lag and construction constraints | Sensitivity |
| R4 | Holding-cost derivation and sensitivity at EUR 500/1000/1500; discuss outcome-weighting for costs | Sensitivity + writing |
| R5 | Construction-capacity-ceiling counterfactual at 35K/38K/no-ceiling | Sensitivity |
| R6 | 7x case-multiplier source or flag; rho decomposition sensitivity at 3x/5x/7x/10x; do not use rho to support 25% attribution | Sensitivity + writing |
| R7 | Reconcile all paper-vs-results.tsv inconsistencies; cross-check E14.* sum = E01 | Data quality |

---

## Decision

**MAJOR REVISIONS.** The direct-delay accounting (105,504 unit-months) is the paper's strongest claim but requires the imputation sensitivity in the abstract (R1) and numerical reconciliation (R7). The indirect channel and counterfactual are currently over-stated relative to their evidential support (R2, R3, R5, R6). The holding-cost figure has an arithmetic issue that must be resolved (R4). No mandated experiment is expected to contradict the directional finding, but the headline numbers may narrow significantly under the capacity-ceiling and endogenous-intake adjustments.
