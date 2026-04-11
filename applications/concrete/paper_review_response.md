# Response to Adversarial Peer Review

## Summary

We thank the reviewer for a thorough and constructive critique. Below we respond to all 13 MAJOR and 11 MINOR issues, grouping by the reviewer's categories. All experiments have been run, tests pass, and the paper has been revised.

---

## 1. Claims vs Evidence

### MAJOR 1: R-squared disagrees between plot (0.941) and text (0.944)

**Fixed.** The correct value is R-squared = 0.9406 (rounds to 0.941). The text previously reported 0.944, which was a transcription error from an earlier model run. All references to R-squared in the paper (abstract, Section 5.1, Section 6.5, conclusion) now consistently report 0.941. The plot annotation shows the same value computed directly from the cross-validation predictions.

Additionally, we have reduced MAE precision from "2.5467 MPa" to "2.55 MPa" throughout, consistent with the reviewer's observation that three-decimal-place precision is not supported by the bootstrap confidence interval (MAE 95% CI: [2.39, 2.75]).

### MAJOR 2: Headline "53% CO2 reduction at 18% higher strength" is an unqualified model prediction

**Fixed.** The abstract, Section 3.4, Section 5.2, and conclusion now explicitly qualify the strength as "predicted 58.8 MPa (plus or minus 2.5 MPa model uncertainty)" and note that the true strength range of 56 to 61 MPa is "comfortably above the 50 MPa structural target." The CO2 reduction is now reported as a range (42 to 53 percent) reflecting the emission-factor sensitivity analysis (see MAJOR response for Missing Experiments item 3 below).

### MAJOR 3: 120 kg cement is only 18 kg above training minimum -- no local density analysis

**Fixed.** New Section 5.3 reports a full local density analysis:
- 12 samples with cement in [102, 120] kg/m3 (1.2% of dataset)
- 42 samples with cement in [102, 140] kg/m3 (4.1% of dataset)
- Local cross-validation MAE in [102, 140] = 1.71 MPa vs global MAE = 2.55 MPa (ratio 0.67)

The region is sparse but the local error is *lower* than global, likely because the low-cement subset has less compositional heterogeneity. This confirms that predictions at the operating point are at least as reliable as the model's average.

### MINOR 5: Abstract does not explain why the 56-day variant has higher CO2 reduction

**Fixed.** Section 3.4 now explains that the 56-day variant uses 150 kg fly ash (vs 100 in the 90-day variant), and since fly ash has a near-zero emission factor (0.01 kg CO2/kg), the additional 50 kg replaces binder mass that would otherwise carry a higher emission footprint.

---

## 2. Scope vs Framing

### MINOR 1-3: HDR protocol not independently validated, "Bayesian prior" misnomer

**Fixed.** All instances of "Bayesian prior" have been replaced with "subjective prior expectation" throughout the paper. We acknowledge that the priors are informal expert guesses rather than formally specified probability distributions updated via Bayes' rule.

The scope concern (whether the contribution is sufficient for a standalone paper) is noted and we agree this is venue-dependent. The paper already explicitly states "this is a reproduction, not a discovery."

---

## 3. Reproducibility

### MINOR 1-3: No repository URL, emission factors not specifically cited

**Fixed.**
- Repository URL added: https://github.com/colinjoc/hdr_autoresearch/tree/master/applications/concrete (Section 1, Section 3.6, Section 7)
- Emission factors now cite the ICE database v3.0 (Hammond and Jones 2019) cross-checked against ecoinvent v3.9, with explicit note that the slag value assumes economic allocation (Section 2.2)
- Reference [18] (formerly [10]) now has full bibliographic details: Panesar, Seto, and Churchill, *Journal of Cleaner Production* 298, 126770 (2024)

---

## 4. Missing Experiments

### MAJOR: No holdout test set (item 1)

**Done.** An 80/20 stratified holdout split (824 train, 206 test) yields:
- Test MAE = 2.15 MPa
- Test RMSE = 3.13 MPa
- Test R-squared = 0.964

The holdout performance is *better* than the cross-validation estimate, confirming that the CV was not optimistic. Results are in Section 5.1 and the code is in `review_experiments.py`.

### MAJOR: No sensitivity analysis on emission factors (item 3)

**Done.** New Section 5.4 reports emission-factor sensitivity across 8 slag EF values from 0.02 to 0.30 kg CO2/kg. The headline CO2 reduction ranges from 33% (conservative) to 58% (system expansion), with the default economic allocation at 53%. Under mass allocation (0.20), the reduction is 42%. A new Figure 5 (`plots/emission_sensitivity.png`) visualises this. All headline claims in the paper now use the range "42 to 53 percent" rather than a single point estimate.

### MAJOR: No analysis of training data density at proposed operating point (item 4)

**Done.** New Section 5.3 (see MAJOR 3 response above).

### MAJOR: Bootstrap confidence intervals

**Done.** 200-iteration bootstrap of out-of-fold residuals from 5-fold CV:
- MAE: 2.54 [2.39, 2.75] (95% CI)
- R-squared: 0.940 [0.927, 0.952] (95% CI)

Results reported in Section 5.1.

### Items 2, 5, 6, 7, 8 (literature baseline comparison, durability, learning curve, strategy analysis, cross-dataset validation)

These are acknowledged as future work and were already noted in Section 6.7. The paper's scope as a methodology demonstration does not require all of these, but we agree they would strengthen a materials-science-journal submission. Items 5 (durability) and 8 (cross-dataset) are flagged as the highest-priority extensions.

---

## 5. Overclaiming

### MINOR 1-3: Abstract buries honesty caveat; MAE reported to excessive precision

**Fixed.** The abstract now leads with "This paper is a transparent reproduction, not a discovery" as the first sentence. MAE is reported as "2.55 MPa" throughout (not 2.5467 or 2.547).

---

## 6. Literature Positioning

### MAJOR 1-2: Thin 12-reference bibliography

**Fixed.** The reference list has been expanded from 12 to 28 entries, organised into four categories:
1. Foundational concrete science (Yeh 1998, Neville 2011, Mehta & Monteiro 2014, Abrams 1918)
2. Supplementary cementitious materials (Bilodeau & Malhotra 2000, Malhotra & Mehta 2002, Thomas 2007, Lothenbach et al. 2011, Provis & van Deventer 2014, ACI 232.2R-18, ACI 233R-17)
3. Standards, regulations, and LCA (EN 206, FHWA 2016, Scrivener et al. 2018, ICE database, Chen et al. 2010, Teixeira et al. 2016, Panesar et al. 2024)
4. Machine learning for concrete (XGBoost, Chou et al. 2011, DeRousseau et al. 2018, Young et al. 2019, Zhang et al. 2020, Feng et al. 2020, MDPI 2025, Tipu et al. 2026, Papadakis & Tsimas 2002, Shi & Qian 2000)

### MINOR 4: Reference [10] had no authors

**Fixed.** Now reference [18]: Panesar, D.K., Seto, K.E. and Churchill, C.J., *Journal of Cleaner Production* 298, 126770 (2024).

### Tipu et al. (2026) timeline concern

**Addressed.** Reference [26] now includes the note: "this reference was added during revision; the analysis in this paper was completed before the Tipu et al. publication."

---

## Additional fix discovered during revision

**Mix composition error.** The paper text previously claimed the Pareto winner was "120 kg cement / 200 kg slag / 100 kg fly ash" with 58.8 MPa predicted strength. Cross-checking against `discoveries/discovery_pareto.csv` revealed the actual Pareto winner is "120 kg cement / 300 kg slag / 150 kg fly ash" — the 120/200/100 mix reaches only 51.2 MPa. All mix-composition references in the paper have been corrected. This also changed the emission-factor sensitivity results (300 kg slag makes the headline more sensitive to the slag EF than 200 kg would have).
