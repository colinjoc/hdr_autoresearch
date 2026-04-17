# Paper Review Signoff (Phase 3.5)

**Reviewer**: Automated blind reviewer agent
**Date**: 2026-04-16
**Paper**: "Why Does Zoned Land Sit Idle?"

---

## Review of Mandated Experiments

### EXP-A1: Exclude Fingal from E00
**Status**: EXECUTED. National intensity excluding Fingal = 4.83 apps/ha/yr on 4,392 ha. Paper revised: Finding 3, Section 5.3, Section 6.2, Caveat section, Limitations 7.

### EXP-B1: Correlation with and without Fingal
**Status**: EXECUTED. r = 0.64 (p < 0.001) excluding Fingal vs r = 0.02 including. Paper revised: Finding 1, abstract, conclusion. Both values now reported.

### EXP-C1: Pure PERMISSION filter
**Status**: EXECUTED. Pure new permission = 21,148 apps/yr (intensity 2.67), a 1.7% reduction. Noted in Section 4.1 and Limitation 8.

### EXP-D1: Partial correlation for approval rate
**Status**: EXECUTED. Partial r = -0.065 (p = 0.73) controlling for population, confirming the null. Reported in Section 5.6.

---

## Verification Checklist

- [x] Fingal denominator mismatch flagged in abstract, findings, discussion, limitations, and caveats
- [x] Both with-Fingal and without-Fingal correlations reported for E13
- [x] Application filter limitation documented with robustness check
- [x] Partial correlation reported for approval-rate confound
- [x] Caveats section added
- [x] Change log added
- [x] Four new rows (EXP-A1, EXP-B1, EXP-C1, EXP-D1) appended to results.tsv
- [x] Finding 1 no longer claims "zoned land does not predict applications" without qualification
- [x] Finding 3 no longer treats 3,519 ha as comparable to Goodbody figures
- [x] Conclusion revised to reflect nuanced finding

---

## Verdict

**NO FURTHER BLOCKING ISSUES.**

The paper now honestly reports the Fingal denominator mismatch, presents both with-Fingal and without-Fingal results, documents the application-type filter limitation, and controls for urbanization in the approval-rate analysis. The headline narrative has shifted from "zoned land does not predict applications" to a more accurate "zoned land predicts applications once the Fingal outlier is excluded." The remaining limitations (cross-sectional zoned land data, RZLT timing, viability approximation) are acknowledged and do not constitute blocking issues.
