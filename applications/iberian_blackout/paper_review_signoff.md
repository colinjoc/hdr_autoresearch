# Reviewer Second Pass: Sign-Off Assessment

**Date:** 2026-04-10
**Paper:** "Detecting Overvoltage Stress Conditions in the Iberian Peninsula Using Domain-Informed Machine Learning on Real Grid Data"

---

## Disposition: Accept with Noted Limitation

The authors have made extensive and honest revisions that address the substance of all three CRITICAL issues. The paper is now scientifically defensible, though it describes a fundamentally more modest contribution than the original submission claimed.

---

## Assessment of CRITICAL Issue Resolutions

### C1: Circular Labeling -- ACKNOWLEDGED (not resolved)

The circular labeling cannot be resolved without independent labels that do not exist in the public domain. The authors have:
- Prominently flagged the circularity in Section 3.3 at the point of label definition
- Added a simple threshold baseline (Section 5.8) that achieves F1 = 0.933 without ML, definitively demonstrating the circularity
- Added threshold sensitivity analysis showing results are driven by the threshold choice
- Reframed all claims from "cascade prediction" to "stress detection"

**Verdict:** The limitation is now transparently acknowledged and the claims are appropriately scoped. This is the best resolution possible without access to SCADA or TSO operational data.

### C2: N=1 Actual Blackout -- ACKNOWLEDGED (not resolved)

This is inherent to the problem (there is only one Iberian blackout in the dataset). The authors have:
- Demonstrated that temporal holdout is impossible (all positives in April-May)
- Shown the model assigns P=0.000 to the actual blackout date when held out
- Removed claims of "cascade prediction capability" from the conclusion

**Verdict:** Appropriately acknowledged. The paper now correctly identifies this as a fundamental limitation rather than glossing over it.

### C3: Overclaiming -- RESOLVED

The title, abstract, research question, discussion, and conclusion have all been rewritten to claim "grid stress detection" rather than "cascade risk prediction." The distinction is now clear throughout the paper.

**Verdict:** Resolved.

---

## Assessment of MAJOR Issue Resolutions

| Issue | Resolution | Status |
|-------|-----------|--------|
| AUC-ROC inconsistency | Standardized to 0.948 throughout | Resolved |
| "Perfect precision" headlined | Removed from abstract/conclusion; bootstrap CIs added | Resolved |
| Feature importance contradicts narrative | Section 7.2 rewritten to match plot; overclaim removed | Resolved |
| "Real Grid Data" but synthetic labels | Title reframed; "stress detection" honest about what is detected | Resolved |
| "Voltage stress dominates" overclaim | Removed from abstract and conclusion | Resolved |
| "Demonstrates cascade identification" | Removed; replaced with honest scoping | Resolved |

---

## Assessment of MINOR Issue Resolutions

All 10 MINOR issues addressed: section numbering fixed, "physics-informed" changed to "domain-informed", attribution clarified, simple baseline added, threshold sensitivity conducted.

---

## Remaining Concerns

1. **No Portuguese data validation.** The reviewer suggested applying the model to Portuguese ENTSO-E data, which would have been a strong out-of-distribution test. This was not done. Acceptable for the scope of the revision, but would strengthen a future version.

2. **No hourly resolution experiment.** The REE API provides hourly data. This was deferred to future work. Given the daily granularity limitation acknowledged throughout, this is acceptable but represents unused potential.

3. **No calibration plot.** With 94 samples, a reliability diagram would have wide bins but would still be informative. Minor omission.

4. **The paper's contribution is now very modest.** After honest reframing, the paper demonstrates that: (a) domain-informed features capture the conditions identified by the ENTSO-E investigation, (b) these features can be computed from public REE data, (c) a threshold on these features identifies extreme-stress days, and (d) the inertia proxy is redundant for this failure mode. This is a valid but incremental contribution. The literature review remains disproportionately large for this scope.

---

## Sign-Off

The revised paper is honest about its limitations. The circular labeling and N=1 issues are acknowledged rather than resolved, which is the appropriate treatment when independent labels are unavailable. The reframing from "cascade prediction" to "stress detection" brings claims into alignment with evidence.

**Recommendation:** Accept. The core contribution -- demonstrating that public REE data combined with domain-informed feature engineering can detect extreme grid stress conditions, and that inertia is not the binding constraint for this failure mode -- is defensible and useful. The comprehensive self-assessment of limitations (particularly the circular labeling acknowledgment and the simple threshold baseline that exposes it) demonstrates scientific integrity that strengthens rather than weakens the paper.

**Unresolved limitation for the record:** The circular labeling means all reported classification metrics (F1, precision, recall, AUC-ROC) should be interpreted as measures of the model's ability to recover its own labeling threshold, not as measures of cascade prediction capability. This cannot be resolved without independent labels from TSO operational data.
