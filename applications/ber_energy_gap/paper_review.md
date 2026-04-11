# Adversarial Peer Review: "Predicting Ireland's Building Energy Ratings"

**Reviewer recommendation: Major Revision**

---

## 1. Claims vs Evidence

### The chimney sealing claim is extraordinary but inadequately supported [CRITICAL]

The paper's headline policy finding is that chimney sealing at 200 EUR yields 25.1 kWh/m2/yr savings -- an order of magnitude more cost-effective than any other measure. This is an extraordinary claim that warrants extraordinary evidence. The evidence provided is a single counterfactual perturbation on the "average dwelling" from a model trained on observational BER data. No sensitivity analysis is presented. No confidence interval is given. No comparison to any engineering calculation or field trial is cited. The 200 EUR cost figure is presented without citation.

Critically, the chimney sealing counterfactual conflates correlation with causation. If homes with chimneys are older, less insulated, and less efficient in many correlated ways, the model may attribute some of the multivariate penalty to the chimney feature alone. The SHAP value for chimney count (8.4 kWh/m2/yr) is far smaller than the counterfactual saving (25.1 kWh/m2/yr), which means the counterfactual perturbation is somehow extracting 3x the average SHAP contribution. This discrepancy is not explained and raises questions about whether the counterfactual methodology is double-counting correlated features.

### R2 = 0.951 overstates model contribution [MAJOR]

The paper frames R2 = 0.951 as a strong result, but the target (BER score) is itself a deterministic calculation from the input features. DEAP is a physics formula; the model is learning an approximation to a known function. The residual 4.9% is acknowledged to reflect assessor variation and unmeasured parameters, but the framing throughout implies ML is "discovering" something about building physics. In reality, this is function approximation of a quasi-linear formula, and the high R2 is a near-tautology. The 44% MAE reduction over Ridge is more meaningful but should be foregrounded instead.

### Per-band accuracy table is selective [MINOR]

Table in Section 4.2 shows only 7 of 15 bands (A2, A3, B3, C1, D2, F, G). The omitted bands (A1, B1, B2, C2, C3, D1, E1, E2) may show different patterns. The selection appears to cherry-pick bands that show a clean monotonic degradation narrative. Show all bands.

---

## 2. Scope vs Framing

### Title promises "energy gap" but paper delivers DEAP prediction [MAJOR]

The title includes the phrase "Energy Gap" but the paper explicitly states it cannot study the performance gap because metered data is unavailable. The paper is fundamentally a regression study predicting a calculated score from its own inputs. The title is misleading; a more honest title would be "Predicting Ireland's DEAP-Calculated BER Scores from Building Characteristics." The performance gap framing in the introduction (Section 1) and discussion (Section 5.2) reads as window dressing around a relatively straightforward ML exercise.

### The paper cannot answer its own Question 3 [MAJOR]

Question 3 asks "Which single-measure retrofits offer the largest DEAP improvement per euro?" The counterfactual methodology answers a different question: "If we change one feature in the model and re-predict, what does the model say?" This is not the same as a retrofit impact because (a) real retrofits change multiple correlated building properties simultaneously, (b) the model was trained on cross-sectional data, not before/after retrofit pairs, and (c) the cost figures are unverified national averages. The paper acknowledges point (a) in Limitation 5 but still presents the results as retrofit recommendations.

---

## 3. Reproducibility

### Data access is clear and laudable [POSITIVE]

The SEAI BER dataset is publicly available under CC-BY-4.0, and the download date and record count are specified. This is a strength.

### Feature engineering details are sufficient but code is not provided [MINOR]

The 22 numeric and 5 categorical features are listed, and the 4 retained HDR features are described. However, specific column names from the SEAI dataset are not mapped to feature names. Without the code or a column mapping table, reproducing the HLP proxy or ventilation loss proxy from the raw data requires guesswork.

### Hyperparameter selection is underspecified [MINOR]

The final model uses "learning rate 0.05, 600 trees, max depth 10, L2 regularisation lambda 1.0" but no tuning procedure is described. Were these selected by grid search, Bayesian optimization, or manual iteration? The HDR loop methodology is mentioned but not detailed enough to reproduce the hyperparameter choices.

---

## 4. Missing Experiments

1. **Before/after retrofit validation.** Ireland has administered over 500,000 BER certificates for the same dwelling at different dates (pre- and post-retrofit). Using matched pairs to validate the counterfactual predictions would be straightforward and would dramatically strengthen the retrofit claims. [CRITICAL]

2. **Confidence intervals on all predictions.** No uncertainty quantification is presented anywhere. Bootstrap CIs on the SHAP values, cross-validation MAE standard deviations per band, and confidence intervals on the counterfactual savings are all absent. [MAJOR]

3. **Dwelling-type-specific counterfactuals.** The paper acknowledges (Limitation 3) that the "average dwelling" counterfactual is misleading for specific archetypes but does not provide archetype-specific results (e.g., pre-1930 detached, post-2006 semi-detached). Given that construction era is the dominant driver, this is a critical omission. [MAJOR]

4. **Ablation study for space heating fraction.** Section 5.4 Limitation 6 acknowledges that space heating fraction is "partially endogenous." This feature reduced MAE by 5.5% -- the largest single feature improvement. A full ablation showing model performance with and without this potentially leaky feature is essential. [MAJOR]

5. **Comparison with DEAP formula itself.** The paper never compares the ML model against the actual DEAP formula. Since the BER score is computed by DEAP from largely the same inputs, the relevant baseline is the DEAP calculation itself, not Ridge regression. If the ML model merely approximates DEAP, the entire exercise adds nothing. [CRITICAL]

6. **Out-of-distribution test.** Training on 1.33M records and testing by cross-validation on the same population does not test generalization. Testing on Northern Ireland BER certificates (a different jurisdiction with different assessors but similar building stock) would be informative. [MINOR]

7. **Assessor effects.** BER assessor identity is likely available in the dataset. Assessor-level random effects or clustering could explain a meaningful fraction of the residual variance. [MINOR]

8. **Wall insulation sensitivity by dwelling type.** The finding that wall insulation has "near-zero marginal effect" is presented as a general finding but is clearly an artifact of averaging over the stock (most of which is post-2006 with reasonable walls). Stratified results by construction era are needed to avoid misleading policy conclusions. [MAJOR]

9. **Temporal validation.** BER certificates span 2009-2026. Training on pre-2020 and testing on 2020-2026 (or vice versa) would test whether the model generalizes across regulatory regime changes. [MINOR]

10. **Multi-measure interaction effects.** The paper acknowledges this limitation but does not even attempt pairwise combinations (e.g., chimney sealing + boiler upgrade). Given the policy context, this is a significant gap. [MINOR]

---

## 5. Overclaiming

### "Chimney sealing is dramatically undervalued" [CRITICAL]

This is a strong policy claim based entirely on a counterfactual perturbation of a supervised model with no causal identification strategy. The paper does not cite any field trial, engineering simulation, or before/after study supporting this magnitude of saving. Saying a model predicts something is not evidence that it is "undervalued" in policy. The claim needs to be hedged to: "The model predicts chimney features have high importance, suggesting that ventilation management deserves further investigation through field trials."

### "Heat pump installation yielded the second-largest absolute improvement" [MAJOR]

This phrasing implies a measured effect. It is a model prediction from a counterfactual perturbation. The distinction matters because heat pump performance in real Irish conditions is highly variable (COP depends on outdoor temperature, hot water demand, radiator sizing) and the BER model uses fixed assumptions.

### Abstract claims "physics-informed features" [MINOR]

The features are motivated by physics but there is nothing physics-informed about the model architecture. The features are standard domain knowledge transformations applied to a black-box gradient booster. Calling them "physics-informed" borrows prestige from the physics-informed neural network (PINN) literature, which refers to embedding physical laws as constraints or loss terms.

---

## 6. Literature Positioning

### Missing key literature on ML for BER/EPC prediction [MAJOR]

The paper cites only two ML-for-building-energy references (Hundi & Shahsavar 2020; Amasyali & El-Gohary 2018). The literature on predicting Energy Performance Certificate ratings from building features is substantial, including:
- Pasichnyi et al. (2019) on Swedish EPC prediction
- Arcipowska et al. (2014) on EU-wide EPC analysis
- Fabbri et al. (2014) on Italian EPC clusters
- Hong et al. (2020) on English EPC data
- Cozza et al. (2020) on the Swiss performance gap

The paper does not position itself relative to any of these, making it impossible to assess whether the methodology or findings are novel in the broader European context.

### No mention of causal inference in retrofit evaluation [MAJOR]

The retrofit cost-effectiveness analysis is presented without any reference to the causal inference literature on building retrofit evaluation (e.g., Fowlie et al. 2018 on weatherization programs; Allcott & Greenstone 2012 on energy efficiency interventions). The counterfactual approach used here is a prediction perturbation, not a causal estimand. The paper should acknowledge this distinction and cite the relevant literature on the gap between predictive and causal estimates.

### Performance gap literature is adequate but narrow [MINOR]

The paper cites Sunikka-Blank & Galvin (2012), Galvin (2014), and Moran et al. (2020), which are the core Irish references. However, the broader European performance gap literature (Majcen et al. 2013 for Netherlands; Cozza et al. 2020 for Switzerland; Galvin & Sunikka-Blank 2016 for Germany) would strengthen the framing.

---

## Severity Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 4 |
| MAJOR    | 9 |
| MINOR    | 8 |

The paper is well-written and commendably honest about the DEAP-vs-reality limitation. However, the chimney sealing claim is inadequately supported and potentially misleading for policy, the title overpromises relative to content, the missing comparison with the DEAP formula itself is a fundamental gap, and the absence of before/after retrofit validation -- when such data likely exists in the SEAI database -- is a critical missed opportunity. Major revision required with particular attention to validating the counterfactual claims and positioning relative to the EPC prediction literature.
