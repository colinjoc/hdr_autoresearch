# Author Response to Adversarial Review

**Date**: 2026-04-10

---

## CRITICAL-1: Headline improvement may be inflated by cross-validation protocol mismatch

**Response**: Accepted. The reviewer is correct that comparing PTPIE against a GP re-evaluated under a harder protocol (5-fold CV vs. the original single 55/10 split) conflates "stricter evaluation" with "better model." We have added explicit language in Section 5.6 noting this caveat: the GP's 5-fold MAE values are somewhat higher than what the original single-split evaluation would produce, and the improvement percentages are relative to the GP under the same harder protocol, not against the originally published numbers. We do not have the original published single-split MAE values in natural units (the published paper reports MSE on normalised targets), so a direct comparison is not possible. The framing is now honest about this limitation.

**Changes made**: Section 5.6 now includes a paragraph titled "Important caveat on cross-validation protocol" explaining the mismatch.

---

## CRITICAL-2 / MINOR-3: Phase B headline candidate is physically impossible

**Response**: Accepted. The headline Pareto point had matting_agent=0.50 + pigment_paste=0.80 = 1.30, giving a negative binder fraction. This is physically impossible and should have been caught by a composition feasibility filter.

**Changes made**:
1. Added a `matting_agent + pigment_paste <= 1.0` filter to `phase_b_discovery.py` (line 307).
2. Re-ran Phase B discovery. The valid candidate count drops from 7784 to 4765 (3019 infeasible candidates removed).
3. The corrected headline: crosslink=1.00, cyc_nco_frac=0.67, matting_agent=0.50, pigment_paste=0.40, predicted gloss=81.3 GU, estimated VOC=106.4 g/L (was 72.8 g/L before the fix).
4. Pareto front sizes updated: gloss x VOC drops from 24 to 21 points (16 of the original 24 were infeasible).
5. Section 5.7, the abstract, and Section 7 (Conclusion) all updated with the corrected numbers.

---

## MAJOR-1: Scratch hardness R-squared=0.22 framed misleadingly

**Response**: Accepted. We have added explicit language in Section 5.5 stating: "This model has no practical predictive value for unseen formulations at this sample size — a data-scarcity ceiling, not a modelling failure." The per-fold MAE table now makes the high fold-level variance visible (std = 0.577 N on a mean of 1.800 N, coefficient of variation 32%).

**Changes made**: Section 5.5 rewritten to include the explicit "no practical predictive value" statement.

---

## MAJOR-2: See CRITICAL-2 above (merged)

---

## MAJOR-3: No leave-one-campaign-out (LOCO) evaluation

**Response**: Accepted. We ran a 6-fold LOCO evaluation.

**New results**:

| Target | Random 5-fold CV MAE | LOCO MAE | Degradation |
|---|---|---|---|
| scratch_hardness_N | 1.800 | 1.877 | +4.3% |
| gloss_60 | 10.036 | 11.347 | +13.1% |
| hiding_power_pct | 2.187 | 2.223 | +1.6% |
| cupping_mm | 1.519 | 1.727 | +13.7% |

The improvements survive LOCO evaluation (R-squared remains positive for all targets), but the 13% degradation for gloss and cupping confirms within-campaign correlation inflates the random-CV estimates. Campaign i2 is consistently the hardest to predict.

**Changes made**: New Section 5.6.1 added with full LOCO results. Section 6.4 "Cross-validation overlap" updated to reference the LOCO results instead of dismissing the analysis.

---

## MAJOR-4: No confidence intervals or significance tests

**Response**: Accepted. We now report per-fold MAE standard deviations for both the GP baseline and PTPIE models in Section 5.5 and 5.6. With only 5 folds, formal significance tests have limited power. We added qualitative fold-level analysis: cupping improvement is robust (PTPIE wins all 5 folds), gloss and hiding win 4/5 folds, scratch hardness is within noise.

**Changes made**: Section 5.6 table now includes fold-level standard deviations. New paragraph on statistical significance added.

---

## MAJOR-5: No per-fold MAE table

**Response**: Accepted. A per-fold MAE table is now included in Section 5.5 for the final PTPIE models and in Section 5.6 for the GP baseline comparison.

**Changes made**: Section 5.5 now includes the full fold-level MAE table with standard deviations.

---

## MAJOR-6: No predicted-vs-actual plots for three other targets

**Response**: Accepted. Figure 1 has been replaced with a 2x2 panel showing all four targets. The scratch hardness scatter (R-squared=0.221) now visually confirms the lack of predictive pattern, and the gloss scatter shows the systematic over-prediction at low values that the reviewer identified in MAJOR-7.

**Changes made**: Generated `plots/pred_vs_actual_all.png` with all four targets. Figure 1 caption and text updated to reference all four panels.

---

## MAJOR-7: Systematic gloss bias at low values unaddressed

**Response**: Accepted. The gloss model systematically over-predicts in the 10-30 GU range. We have added discussion of this bias in Section 6.3 (Limitations) as a new bullet point explaining the likely cause (micro-scale surface texture from matting silica not captured by normalised loading) and noting the model's utility is strongest above 50 GU.

**Changes made**: New limitation bullet in Section 6.3.

---

## MINOR-1: Abstract says "five performance properties"

**Response**: Accepted. The Introduction sentence has been corrected to "four composition variables, film thickness, four performance properties" to disambiguate film thickness (process variable) from the four prediction targets.

**Changes made**: Line 9 of paper.md updated.

---

## MINOR-2: Noise floor calibration not documented

**Response**: Accepted. Section 6.4 now specifies: "The noise floors (0.02 N, 0.20 GU, 0.05 %, 0.03 mm) are set at approximately 1% of the target's observed range, calibrated against the standard deviation of fold-level MAE residuals from the Phase 0.5 XGBoost baseline."

**Changes made**: Section 6.4 updated.

---

## MINOR-4: Abstract too long

**Response**: Noted but not changed. The abstract is intentionally comprehensive to serve as a standalone summary for readers who may not read the full paper. We acknowledge this exceeds typical journal limits.

---

## MINOR-5: Figure numbering inconsistent

**Response**: Noted. The figure numbering reflects the order of creation, not the order of presentation. We leave the numbering as-is since the paper is not targeting journal submission.

---

## MINOR-6: "12-28%" vs "13-28%" inconsistency

**Response**: The gloss improvement is 12.7%, which rounds to 13% in text. The plot shows the unrounded value. This is a rounding ambiguity, not a factual error.

---

## MINOR-7: ERROR experiments in results.tsv

**Response**: Noted. The ERROR rows (E016, E090) are intentionally preserved in results.tsv as part of the complete experiment record. The underlying NaN issue was in Ridge's inability to handle log-ratio features that produce -inf when a composition column is exactly 0. The add_features function already clips to eps=1e-3 before logging, but these two experiments predated the fix. The fix is present in the current codebase.

---

## MINOR-8: No requirements.txt

**Response**: Noted. The project uses a local venv. A requirements freeze would be good practice for reproducibility but is not added in this revision.

---

## Summary of changes

1. **phase_b_discovery.py**: Added composition feasibility filter (matting + pigment <= 1.0). Re-ran discovery.
2. **paper.md**: Revised abstract, Sections 5.5, 5.6, 5.7, 6.3, 6.4, and 7 to address all CRITICAL and MAJOR findings.
3. **plots/pred_vs_actual_all.png**: New 2x2 predicted-vs-actual panel for all four targets.
4. **New experiments run**: Per-fold MAE breakdown (PTPIE and GP baseline), leave-one-campaign-out cross-validation.
5. All 36 existing tests pass after changes.
