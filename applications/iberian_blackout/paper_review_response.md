# Author Response to Adversarial Peer Review

We thank the reviewer for a thorough and technically rigorous review. The identification of the circular labeling issue was the most important contribution of this review. We have made extensive revisions to address all 3 CRITICAL, 6 MAJOR, and 10 MINOR issues. Below we address each point.

---

## CRITICAL Issues

### C1: Circular Labeling

**Reviewer concern:** The positive labels are derived from a 95th-percentile threshold on the same features used for prediction, creating circular evaluation that inflates all metrics.

**Response:** The reviewer is correct, and this is the most significant flaw in the original manuscript. We have:

1. Added an explicit "Critical methodological note on circular labeling" to Section 3.3, explaining the circularity prominently at the point where labels are defined.
2. Conducted a **simple threshold rule baseline** (Section 5.8): a direct threshold on the composite risk score achieves F1 = 0.933 without any machine learning, confirming that the ML model is recovering its own labeling threshold.
3. Conducted a **threshold sensitivity analysis** (Section 5.7): results range from F1 = 0.968 (85th percentile) to F1 = 0.000 (99th percentile), showing the 95th-percentile choice drives the results.
4. Reframed all claims throughout the paper from "cascade risk prediction" to "grid stress detection."
5. Changed the title from "Predicting Overvoltage-Driven Cascade Risk" to "Detecting Overvoltage Stress Conditions."
6. Rewrote the abstract, conclusion, and discussion to foreground this limitation.

We acknowledge that this circularity cannot be fully resolved without independent labels (ENTSO-E grid warnings, SCADA voltage exceedance records, operator intervention logs). No such data is publicly available for the study period. This is documented as an unresolved limitation.

### C2: N=1 Actual Blackout

**Reviewer concern:** The model has never been tested on an unseen cascade event.

**Response:** Fully accepted. We conducted two additional experiments:

1. **Temporal holdout** (Section 5.10): Training on January-March and predicting April-May was impossible because all 8 positive labels fall in April-May (stress conditions are seasonal). This itself reveals a fundamental problem: the model cannot be validated prospectively.
2. **Leave-one-week-out** (Section 5.10): When April 21-28 is held out, the GBM correctly flags stress-labeled days but assigns probability 0.000 to April 28, the actual blackout date. This is because April 28's composite stress score (0.293) falls below the 95th-percentile threshold (0.330) -- it was labeled positive only because it is the known blackout date, not because of extreme feature values.

The conclusion now explicitly states: "With N = 1 actual cascade event and no independent label source, the claim of 'cascade prediction' is not supported."

### C3: Overclaiming "Cascade Risk Prediction"

**Reviewer concern:** The paper claims to predict cascade risk when it actually predicts stress score exceedances.

**Response:** Fully accepted. Changes throughout:
- Title changed to "Detecting Overvoltage Stress Conditions"
- Research question (Section 1.3) reframed to "detect grid stress conditions" rather than "predict grid states proximate to cascading collapse"
- Abstract rewritten to lead with the limitation
- Conclusion rewritten to distinguish between what is supported (stress detection) and what is not (cascade prediction)
- Section 7.5 rewritten to remove operational early warning claims and instead list what would be needed for a genuine early warning system

---

## MAJOR Issues

### M1: AUC-ROC Inconsistency

**Reviewer concern:** Text reports ensemble AUC-ROC = 0.954, plot shows 0.948.

**Response:** Corrected. The plot value (0.948) is computed directly from the ROC curve; the text value (0.954) was from sklearn's roc_auc_score which uses a different computation method. We have standardized all text values to match the ROC curve computation (0.948) and added a note explaining the minor discrepancy in Figure 1's caption.

### M2: "Perfect Precision" Headlined Despite Fragility

**Reviewer concern:** Perfect precision on 6 true positives is a small-sample artifact, not a robust finding.

**Response:** Accepted. We have:
1. Added bootstrap 95% CIs (Section 5.11): GBM precision CI is [1.000, 1.000] only because bootstrap resamples the same 6 TPs and 0 FPs -- but one additional FP drops precision to 0.857.
2. Removed "perfect precision" from the abstract and conclusion.
3. Added the F1 CI [0.571, 1.000] to the conclusion to convey the uncertainty.

### M3: Feature Importance Contradicts "Voltage Stress Dominates" Narrative

**Reviewer concern:** The feature importance plot shows composite risk score, renewable fraction, and synchronous fraction dominating, not voltage-specific features.

**Response:** Fully accepted. We have:
1. Rewritten Section 7.2 ("The Voltage Stress Signal" renamed to "The Feature Importance Signal") to accurately describe what the plot shows.
2. Removed the claim "voltage stress proxy dominates feature importance" from the abstract and conclusion.
3. Clarified that the ablation finding ("voltage-focused features are sufficient") means sufficiency, not dominance.
4. Added Section 8.7 noting this as a threat to validity.

### M4: Title Claims "Real Grid Data" but Labels Are Synthetic

**Reviewer concern:** The features are real (REE API) but 7 of 8 labels are synthetic (threshold-derived).

**Response:** Accepted. The title now reads "Detecting Overvoltage Stress Conditions in the Iberian Peninsula Using Domain-Informed Machine Learning on Real Grid Data" -- the "real grid data" refers to the features, which are genuinely from the REE API, and the stress detection framing is honest about what is being detected.

### M5: "Voltage Stress Dominates" Claim (Overclaiming Section)

**Response:** Addressed under M3 above.

### M6: "Demonstrates That Daily Data Can Identify Grid States Proximate to Cascading Collapse"

**Response:** Removed. The conclusion now states: "Whether monitoring these features constitutes a useful component of an early warning system remains an open question."

---

## MINOR Issues

### m1: "Physics-Informed" Overstates Physics Content

**Response:** Changed to "domain-informed" throughout the paper. The features are motivated by the ENTSO-E root cause analysis, which constitutes domain knowledge, not physics in the sense of power flow equations or voltage stability analysis.

### m2: "Novel Failure Mode" Framing vs Generic ML Methodology

**Response:** Acknowledged in the revised discussion. The methodology is standard classification; the contribution is the domain-specific feature engineering and the honest analysis of what public data can and cannot tell us about cascade risk.

### m3: REE API Endpoints Not Fully Specified

**Response:** The exact endpoints, date ranges, and data files are available in the project repository. We have clarified the data documentation in Section 3.1.

### m4: 95th Percentile Threshold is a Hyperparameter

**Response:** Addressed by the threshold sensitivity analysis (Section 5.7), which evaluates six percentile choices from 85th to 99th.

### m5: Section Numbering Broken

**Response:** Fixed. Sections 2.1/2.2 corrected to 3.1/3.2, and the missing 3.3 gap eliminated.

### m6: "First Continental European Overvoltage Cascade" Attribution

**Response:** Reworded to "A 2026 paper in Electric Power Systems Research described the Iberian blackout as the first documented overvoltage-driven cascading blackout in the Continental European synchronous area."

### m7: Missing Engagement with Early Warning System Literature

**Response:** Section 7.5 now lists specific requirements for a genuine early warning system (independent labels, multi-event validation, temporal holdout, sub-daily resolution).

### m8: Disproportionate Related Work

**Response:** We retain the related work as context for a novel failure mode, but have ensured the discussion and conclusion do not promise more than the methodology delivers.

### m9: No Comparison with Nakarmi et al. (2025)

**Response:** Acknowledged as a limitation of scope. The simulated-cascade approach of Nakarmi et al. uses fundamentally different (and potentially more appropriate) labels; our approach uses real operational data but with circular labels. A direct comparison would require access to both label types.

### m10: Missing Domain-Expert Heuristic Comparison

**Response:** The simple threshold rule baseline (Section 5.8) serves this purpose. The domain-expert heuristic (threshold on composite stress score) achieves F1 = 0.933, exceeding the GBM.

---

## Missing Experiments (Reviewer Section 4)

| Experiment | Status | Finding |
|-----------|--------|---------|
| 1. Threshold sensitivity | Done (Section 5.7) | Results highly sensitive to threshold; 85th pct gives F1=0.968, 99th pct gives F1=0.000 |
| 2. Temporal holdout | Done (Section 5.10) | Impossible (0 positives in training); alternative holdout shows GBM assigns P=0.000 to Apr 28 |
| 3. Simple threshold rule | Done (Section 5.8) | CRS > 0.330 gives F1=0.933, beating GBM (F1=0.857) |
| 4. Portuguese data | Not done | ENTSO-E publishes Portuguese data; would require separate data collection |
| 5. Permutation test | Done (Section 5.9) | p < 0.005; significant but meaningless given circular labeling |
| 6. Hourly resolution | Not done | Deferred to future work; REE hourly data available but requires restructuring |
| 7. Calibration plot | Not done | Deferred; 94 samples insufficient for reliable calibration bins |
| 8. Bootstrap CIs | Done (Section 5.11) | GBM F1 CI: [0.571, 1.000]; extremely wide |
| 9. Alternative labels | Not done | No public source for ENTSO-E warnings, reactor activations, or curtailment events |
| 10. Power flow simulation | Not done | Requires network topology data not publicly available |

---

## Summary of Changes

1. **Title changed** from "Predicting Cascade Risk" to "Detecting Stress Conditions"
2. **Abstract rewritten** to lead with limitations
3. **"Physics-informed" changed to "domain-informed"** throughout
4. **Circular labeling prominently acknowledged** in Sections 3.3, 5.8, 8.1, and conclusion
5. **Five new experimental sections** added (5.7-5.11)
6. **Feature importance narrative corrected** (Sections 7.2, 8.7)
7. **Section numbering fixed**
8. **AUC-ROC values standardized** to 0.948
9. **Threats to Validity expanded** from 5 to 7 subsections
10. **Conclusion rewritten** to distinguish supported claims from unsupported ones
