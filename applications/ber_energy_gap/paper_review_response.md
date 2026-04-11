# Author Response to Peer Review

We thank the reviewer for a thorough and constructive critique. The review identified fundamental problems with our framing, a flawed counterfactual methodology, and several missing experiments. We agree with the vast majority of the criticism and have made substantial revisions. Below we address every point, grouped by severity.

---

## CRITICAL Issues

### C1. Chimney sealing claim is extraordinary but inadequately supported

**Reviewer concern:** The headline claim of 25.1 kWh/m2/yr saving at 200 EUR relies on a single counterfactual perturbation of the "average dwelling." The SHAP value (8.4) is 3x smaller, creating an unexplained discrepancy.

**Finding on investigation:** The reviewer was correct to flag this. The 3x discrepancy has a specific cause: the "average dwelling" has a mean chimney count of 0.52 (because 58% of dwellings have zero chimneys). Subtracting 1 from 0.52 yields -0.48 -- a negative chimney count that is physically impossible and out of distribution. The model extrapolates wildly in this region.

**Corrected analysis:** We re-ran the counterfactual using per-dwelling predictions instead of the mean dwelling. For the 563,145 dwellings that actually have chimneys, setting chimney count to zero and adjusting the correlated ventilation loss proxy yields:
- Mean saving: 21.1 kWh/m2/yr (median: 19.2, SD: 10.5)

We also ran archetype-specific counterfactuals:
- Pre-1930 detached: 26.3 +/- 13.6 kWh/m2/yr
- 1930-1977 semi-detached: 24.9 +/- 10.6
- 1978-2005 any: 18.5 +/- 7.8
- Post-2006 any: 14.9 +/- 8.9

The corrected per-dwelling saving (21.1) is still large but more honestly bounded, and the archetype stratification shows expected variation. We no longer claim 25.1 from the mean-dwelling extrapolation.

**Paper change:** Replaced the mean-dwelling counterfactual table with per-dwelling results including confidence intervals. Downgraded the chimney claim from "dramatically undervalued" to "the model predicts large chimney-related savings that warrant validation through field trials." Added explicit discussion of the OOD extrapolation problem.

### C2. R2=0.951 is near-tautological

**Reviewer concern:** The BER score is a deterministic calculation from the input features. High R2 is expected, not impressive. The paper frames it as if ML is discovering something about building physics.

**Finding on investigation:** The reviewer is entirely correct. We reconstructed the BER rating directly from the DEAP primary energy components already present in the dataset (sum of primary energy for space heating, water heating, lighting, pumps, secondary heating, and supplementary water, divided by floor area). This reconstruction achieves:
- MAE: 6.96 kWh/m2/yr
- RMSE: 29.07
- R2: 0.942

The ML model achieves MAE 18.05 (worse by 2.6x) and R2 0.951 (marginally better due to lower RMSE from fewer extreme outliers in the renewable-energy subset). The DEAP intermediate outputs, already in the dataset, reconstruct the BER rating more accurately than the ML model. The high R2 is indeed near-tautological -- it reflects the ML model learning an approximation to a known physics formula.

**Paper change:** Added explicit DEAP-reconstruction baseline to Section 3.2 and the results table. Reframed the contribution: the ML model's value is not accuracy but interpretability (SHAP attribution) and the ability to predict from building characteristics alone without running the full DEAP calculation. R2 is no longer foregrounded as a headline result. The 44% MAE improvement over Ridge is retained as the meaningful metric, with the caveat that even this represents function approximation, not scientific discovery.

### C3. Title promises "energy gap" but paper delivers DEAP prediction

**Reviewer concern:** The paper cannot study the actual performance gap because it has no metered consumption data.

**Agreement:** Fully agree. The title was misleading.

**Paper change:** Title changed from "Predicting Ireland's Building Energy Ratings: What the DEAP Model Reveals About Retrofit Priorities" to "Predicting Ireland's DEAP-Calculated BER Scores: What Building Characteristics Drive the Rating and Where the Formula Is Most Sensitive." Removed all "energy gap" framing from the introduction and abstract. The performance gap is now discussed only in Section 5.2 as important context, not as something this paper studies.

### C4. Missing comparison with DEAP formula itself

**Reviewer concern:** The relevant baseline is DEAP itself, not Ridge regression. If the ML model merely approximates DEAP, the exercise adds nothing.

**Finding on investigation:** See C2 above. The DEAP reconstruction from intermediate outputs in the dataset achieves MAE 6.96 -- substantially better than the ML model's 18.05. The ML model does NOT outperform the DEAP formula.

**Paper change:** Added the DEAP-reconstruction baseline to the model tournament table. The framing now explicitly acknowledges that the ML model is a lossy approximation to DEAP, and its value lies in (a) identifying which input features matter most via SHAP, (b) enabling rapid BER screening from building characteristics without a full assessor visit, and (c) quantifying interaction effects between features that the linear DEAP formulation handles implicitly.

---

## MAJOR Issues

### M1. Title/scope mismatch (covered under C3 above)

Title changed. "Energy gap" removed from title. Scope honestly described as DEAP prediction and sensitivity analysis.

### M2. Paper cannot answer its own Question 3

**Reviewer concern:** The counterfactual methodology answers "what does the model predict if we change one feature?" not "what happens after a real retrofit?" These are different questions.

**Agreement:** Correct. We revised Question 3 from "Which single-measure retrofits offer the largest DEAP improvement per euro?" to "Which building characteristics does the DEAP model weigh most heavily, and what does perturbing them individually predict?" The distinction between model perturbation and real retrofit impact is now explicit throughout.

### M3. Confidence intervals missing

**New experiment:** Bootstrap confidence intervals (10 iterations of 5-fold CV on 200k subsamples):
- Overall MAE: 18.26 +/- 0.05 (95% CI: [18.17, 18.33])

Per-dwelling counterfactual savings now reported with standard deviations (see C1 above). All key results now include uncertainty estimates.

### M4. Dwelling-type-specific counterfactuals missing

**New experiment:** See archetype-specific results under C1. Added stratified results for pre-1930 detached, 1930-1977 semi-detached, 1978-2005 general, and post-2006 general.

### M5. Space heating fraction ablation

**New experiment:** Full ablation study:
- Full model (all HDR features): MAE 18.36, R2 0.9489
- Without sh_fraction: MAE 19.44, R2 0.9430
- Without sh_fraction AND primary_energy_factor: MAE 19.42, R2 0.9431
- Original features only (no HDR additions): MAE 19.44, R2 0.9430

sh_fraction contributes 1.08 MAE improvement (5.6%). It is partially endogenous (derived from DEAP outputs), and the paper now flags this explicitly. The other three HDR features (compactness ratio, ventilation loss proxy, primary energy factor) contribute negligibly once sh_fraction is removed. The honest model without any DEAP-derived features achieves MAE 19.44.

**Paper change:** Added ablation table to Section 3.3. Flagged sh_fraction as providing the bulk of the HDR improvement and being partially endogenous.

### M6. Wall insulation sensitivity by dwelling type

**New experiment:** Wall insulation counterfactual by construction era (reducing U-value by up to 0.3, minimum 0.21):
- Pre-1930: 2.1 kWh/m2/yr (mean wall U = 1.34)
- 1930-1977: 1.3 (mean wall U = 1.04)
- 1978-2005: 1.0 (mean wall U = 0.49)
- 2006-2011: 2.0 (mean wall U = 0.37)
- 2012-2020: 0.2 (mean wall U = 0.19)
- 2021+: 0.1 (mean wall U = 0.18)

The counterintuitive result persists: even for pre-1930 homes with wall U-values of 1.34, the model predicts only 2.1 kWh/m2/yr saving from a 0.3 U-value improvement. This is because the model has learned that chimney/ventilation losses dominate in older homes, and wall insulation alone does not address the primary heat loss pathway.

**Paper change:** Added era-stratified wall insulation results. Removed the original "near-zero marginal effect" headline claim which was misleading because it averaged across all eras.

### M7. Missing EPC prediction literature

**Paper change:** Added references to Pasichnyi et al. (2019), Hong et al. (2020), and Cozza et al. (2020). Positioned our work relative to the European EPC prediction literature.

### M8. Missing causal inference literature

**Paper change:** Added explicit acknowledgment that our counterfactual perturbations are predictive, not causal. Added references to Fowlie et al. (2018) and Allcott & Greenstone (2012). The discussion now distinguishes between model sensitivity analysis and causal retrofit evaluation.

### M9. "Heat pump yielded second-largest improvement" overclaims

**Paper change:** Reworded all counterfactual results to use "the model predicts" rather than implying measured effects. Heat pump section now includes the caveat about real-world COP variability.

---

## MINOR Issues

### m1. Per-band accuracy table is selective

**New experiment:** All 15 bands now shown:
| Band | N | MAE |
|------|---|-----|
| A1 | 1,538 | 19.9 |
| A2 | 161,387 | 5.1 |
| A3 | 86,941 | 10.5 |
| B1 | 42,246 | 23.6 |
| B2 | 67,679 | 18.3 |
| B3 | 120,562 | 15.5 |
| C1 | 140,409 | 15.2 |
| C2 | 144,329 | 16.3 |
| C3 | 130,751 | 17.8 |
| D1 | 121,633 | 19.2 |
| D2 | 103,241 | 21.9 |
| E1 | 59,837 | 24.8 |
| E2 | 47,008 | 27.5 |
| F | 48,575 | 30.9 |
| G | 53,886 | 41.0 |

Notable: A1 has very high MAE (19.9) despite being the best band, because it contains only 1,538 records (0.1% of data) and the model struggles with this sparse category. B1 also has surprisingly high MAE (23.6) relative to adjacent bands. The original paper's selective presentation concealed these anomalies.

### m2. Feature engineering details / column mapping

**Paper change:** Added a column mapping table in Section 3.1 linking SEAI dataset column names to our feature names.

### m3. Hyperparameter selection underspecified

**Paper change:** Added description of tuning procedure. The HDR loop tested learning rate 0.05 vs 0.1, tree counts 300 vs 600, and max depth 8 vs 10. Selection was by 5-fold CV MAE on a 200k subsample.

### m4. "Physics-informed features" overclaims

**Paper change:** Changed to "domain-knowledge features" throughout. Removed any implication of connection to PINN literature.

### m5. Out-of-distribution test / Northern Ireland

Not feasible with current data (NI BER certificates are not publicly available in the same format). Noted as future work.

### m6. Assessor effects

The public dataset does not include assessor identity. Noted as a limitation.

### m7. Performance gap literature

**Paper change:** Added Majcen et al. (2013) and Galvin & Sunikka-Blank (2016) to the literature discussion.

### m8. Multi-measure interactions

Not addressed in this revision. Noted as future work. The paper now explicitly states that single-measure perturbations cannot capture interaction effects.

### m9. Temporal validation

**New experiment:** Training on pre-2020 certificates (657,882) and testing on 2020+ (672,138):
- Temporal holdout MAE: 27.50 (vs CV MAE: 18.05)
- Temporal holdout R2: 0.884 (vs CV R2: 0.951)

The model degrades substantially on post-2020 data, losing 52% of its MAE advantage over the Ridge baseline. This likely reflects (a) the rapid shift to heat pumps and nZEB standards post-2019, and (b) the model overfitting to the regulatory regime represented in the training data. This is an important finding that strengthens the reviewer's concern about generalization.

**Paper change:** Added temporal holdout results to Section 4 with discussion of the implications for the model's real-world applicability.

---

## Summary of Changes

1. **Title changed** to remove "energy gap" framing
2. **DEAP reconstruction baseline added** showing the ML model does not outperform DEAP itself
3. **Chimney counterfactual corrected** using per-dwelling predictions; OOD extrapolation bug documented
4. **R2 reframed** as expected function approximation, not a contribution
5. **sh_fraction ablation** showing most HDR improvement comes from a partially endogenous feature
6. **Temporal holdout** revealing substantial degradation on post-2020 data
7. **All 15 bands** shown in accuracy table
8. **Archetype-specific counterfactuals** added
9. **Bootstrap confidence intervals** added
10. **Wall insulation stratified by era**
11. **Literature expanded** with EPC prediction and causal inference references
12. **Language tightened** throughout: "model predicts" replaces implied causal claims
