# Review Sign-Off: Paint Formulation HDR Paper

**Date**: 2026-04-10
**Status**: ACCEPTED with minor reservations

---

## Resolution of CRITICAL findings

### CRITICAL-1: Cross-validation protocol mismatch framing
**Status**: RESOLVED. Section 5.6 now includes an explicit caveat paragraph explaining that the improvement percentages are measured against the GP baseline re-evaluated under the same 5-fold protocol, not against the originally published single-split numbers. The framing is honest.

### CRITICAL-2: Physically impossible headline discovery candidate
**Status**: RESOLVED. A composition feasibility filter (`matting_agent + pigment_paste <= 1.0`) was added to `phase_b_discovery.py`. Phase B was re-run. The headline candidate is now physically feasible (binder fraction = 0.10). Discovery numbers updated throughout the paper. All 36 tests pass.

---

## Resolution of MAJOR findings

### MAJOR-1: Scratch hardness framing
**Status**: RESOLVED. Section 5.5 now explicitly states "no practical predictive value" for scratch hardness at this sample size.

### MAJOR-3: No LOCO evaluation
**Status**: RESOLVED. New Section 5.6.1 reports full LOCO results. Improvements survive cross-batch evaluation with bounded degradation (2-14%).

### MAJOR-4: No confidence intervals
**Status**: RESOLVED. Per-fold MAE standard deviations now reported for both GP baseline and PTPIE. Qualitative fold-level significance analysis added.

### MAJOR-5: No per-fold MAE table
**Status**: RESOLVED. Fold-level MAE table added to Section 5.5.

### MAJOR-6: Only one pred-vs-actual plot
**Status**: RESOLVED. New 2x2 panel (plots/pred_vs_actual_all.png) shows all four targets.

### MAJOR-7: Systematic gloss bias unaddressed
**Status**: RESOLVED. New limitation bullet in Section 6.3 discusses the over-prediction at low gloss values and its likely physical cause.

---

## Minor findings

All MINOR findings addressed or acknowledged in the author response. MINOR-4 (abstract length) and MINOR-5 (figure numbering) noted but not changed, with justification provided.

---

## Remaining reservations

1. The abstract remains long (now slightly longer with the LOCO mention). This is acceptable for a technical report but would need trimming for journal submission.
2. The per-fold standard deviations for hiding power (0.981 on a mean of 2.187) suggest the hiding power improvement claim should be interpreted cautiously despite the 23% headline number.
3. The noise floor calibration (MINOR-2) is now documented but remains somewhat ad hoc. A bootstrap-based noise floor would be more principled.

---

## Verdict

The two CRITICAL findings are fully resolved. All six MAJOR findings are addressed with new experiments, new plots, and revised text. The paper now honestly represents its contributions and limitations. The Phase B discovery, while less impressive after feasibility filtering (106 g/L VOC vs. the previous 73 g/L), remains a valid low-VOC candidate identification within the feasible composition space.

**ACCEPTED** for publication in the project repository and website summary.
