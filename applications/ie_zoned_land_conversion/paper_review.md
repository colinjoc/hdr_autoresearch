# Paper Review: Blind Review (Phase 2.75)

**Reviewer**: Automated blind reviewer agent
**Date**: 2026-04-16
**Paper**: "Why Does Zoned Land Sit Idle? Measuring the Conversion Rate from Residential Zoning to Planning Application in Ireland"

---

## Overall Assessment

The paper provides a useful first estimate of the zoned-land-to-application conversion rate for Ireland. However, four issues — one blocking, two major, one moderate — undermine the headline claims and must be resolved before publication.

---

## Issue A (BLOCKING): Fingal 3,519 ha is likely RZLT-scoped, not purely residential zoned

**Finding**: Fingal's 3,519 ha figure (attributed to Fingal County Council 2024) *exceeds* the entire Goodbody East+Midlands regional allocation of 2,611 ha by 908 ha. This is a data inconsistency that cannot be correct if both figures use the same definition. The RZLT map includes land zoned for mixed use, town centres, and major town centres — categories broader than "residentially zoned and serviced" in the Goodbody definition.

**Impact**: Fingal's intensity (0.08 apps/ha/yr) is mechanically deflated by a denominator from a different and broader definition than the Goodbody numerator framework. The "44% of national stock" claim, the counterfactual scenarios (S4: +10,600 apps), and the "34x below national average" statistic are all unreliable. All national averages that include Fingal at 3,519 ha are distorted.

**Mandated experiment**: **EXP-A1** — Flag the Fingal denominator inconsistency explicitly. Recompute E00, E02, E13, E14 with Fingal excluded. Report both with-Fingal and without-Fingal results. Add a caveat that the Fingal 3,519 ha figure uses a broader RZLT scope than the Goodbody residential-only definition.

---

## Issue B (MAJOR): r = 0.02 for zoned-land-vs-applications is a Fingal-outlier artefact

**Finding**: Excluding Fingal, the correlation between zoned land area and applications is r = 0.64 (p = 0.0002), not r = 0.02 (p = 0.91). The central claim — "having zoned land does not predict applications" — is driven entirely by a single outlier whose denominator is likely from a different definition.

**Impact**: This invalidates Finding 1 (Section 3.2), the conclusion's headline claim ("the quantity of zoned land does not predict the volume of applications"), and undermines the real-options framing as the primary explanation.

**Mandated experiment**: **EXP-B1** — Recompute E13 excluding Fingal. Report both correlations. Revise Finding 1 to: "Zoned land area positively predicts applications (r = 0.64, p < 0.001) once the Fingal outlier is excluded. The Fingal anomaly reflects a denominator mismatch rather than a genuine supply-demand disconnect."

---

## Issue C (MAJOR): Application filter includes retention and consequent types

**Finding**: The `PERMISSION` substring match in `AppType_clean` catches "PERMISSION FOR RETENTION" (195), "RETENTION PERMISSION" (1,027), "PERMISSION CONSEQUENT" (888), and "EXTENSION OF DURATION OF PERMISSION" (177) over 2018-2024. These are not new development applications — retention is for already-built structures, consequent is conditional follow-up, and extensions are renewals.

**Impact**: Approximately 3.6% of counted applications are not genuine new residential permission applications. The effect on E00 is modest (21,512 -> 20,731 apps/yr; intensity drops from 2.72 to 2.62) but the filtering error is a methodological flaw that should be corrected.

**Mandated experiment**: **EXP-C1** — Recompute E00 using only `AppType_clean == "PERMISSION"` (pure new permission). Report the corrected intensity and note the 3.6% overcount. Include SHD and LRD as they are genuine new permissions but exclude retention, consequent, and extension types.

---

## Issue D (MODERATE): Approval-rate-as-deterrent confounded by urbanization

**Finding**: E10 reports r = -0.07 (p = 0.70) for approval rate vs intensity. However, both variables are correlated with population/urbanization. The partial correlation controlling for population is r = -0.065 (p = 0.73) — essentially unchanged, confirming the null. This is actually reassuring but should be reported as a robustness check.

**Mandated experiment**: **EXP-D1** — Report the partial correlation (approval rate vs intensity | population) alongside the simple correlation. No change to the conclusion needed, but the confound should be acknowledged.

---

## Summary of Mandated Experiments

| ID | Description | Blocking? |
|----|-------------|-----------|
| EXP-A1 | Recompute E00, E02, E13, E14 excluding Fingal; flag denominator inconsistency | YES |
| EXP-B1 | Report r(zoned_ha, apps) with and without Fingal | YES |
| EXP-C1 | Recompute E00 with pure PERMISSION filter only | YES |
| EXP-D1 | Report partial correlation (approval vs intensity | population) | NO |

**All three blocking experiments must be executed and the paper revised before signoff.**
