# Review Signoff: BER Energy Gap Paper

**Reviewer recommendation after revision: Accept with Minor Revisions**

---

## Assessment of Revisions

### CRITICAL issues: All addressed substantively

1. **Chimney sealing claim (C1):** The OOD extrapolation bug (negative chimney count) has been identified and documented. The corrected per-dwelling analysis produces a more honest estimate (21.1 +/- 10.5 vs the original 25.1). The claim is now hedged as a model prediction requiring field validation. The SHAP/counterfactual discrepancy is explained: SHAP averages over all dwellings (58% with zero chimneys), while the perturbation conditions on having a chimney. **Resolved.**

2. **R2 near-tautology (C2):** The DEAP reconstruction baseline (MAE 6.96) is now in the paper, demonstrating that the ML model does not outperform the formula itself. The framing has been thoroughly revised: R2 is no longer foregrounded, and the paper explicitly states the model is function approximation. **Resolved.**

3. **Title/energy gap mismatch (C3):** Title changed. "Energy gap" removed from framing. The paper now honestly describes itself as a sensitivity analysis of the DEAP formula. **Resolved.**

4. **Missing DEAP comparison (C4):** DEAP reconstruction baseline added to the model tournament table with full discussion. **Resolved.**

### MAJOR issues: All addressed

- M1 (title): Covered under C3.
- M2 (Question 3): Research question reworded to describe model sensitivity, not retrofit effectiveness.
- M3 (CIs): Bootstrap CIs added; per-dwelling savings include SDs.
- M4 (archetype counterfactuals): Four archetypes presented.
- M5 (sh_fraction ablation): Full ablation table added showing 1.08 of 1.09 MAE improvement from partially endogenous feature.
- M6 (wall insulation by era): Stratified results for all six construction eras.
- M7 (EPC literature): Pasichnyi, Hong, Cozza cited.
- M8 (causal inference literature): Fowlie, Allcott and Greenstone cited; predictive-vs-causal distinction made explicit.
- M9 (heat pump overclaiming): Language corrected throughout.

### MINOR issues: Mostly addressed

- m1 (all bands): All 15 bands shown.
- m2 (column mapping): Addressed in text.
- m3 (hyperparameters): Tuning procedure described.
- m4 (physics-informed): Changed to "domain-knowledge."
- m5 (OOD/NI): Not feasible; noted as future work. Acceptable.
- m6 (assessor effects): Not in public dataset; noted as limitation. Acceptable.
- m7 (performance gap literature): Majcen, Galvin and Sunikka-Blank added.
- m8 (multi-measure interactions): Not attempted; noted as limitation. Acceptable.
- m9 (temporal validation): Temporal holdout experiment run; results show substantial degradation (MAE 27.50 vs 18.05), which is an important honest addition.

### New findings from the revision

The revision surfaced two important results not in the original:

1. **The DEAP reconstruction baseline** makes the ML model's contribution honest: it is interpretability (SHAP) and rapid screening, not accuracy.
2. **The temporal holdout degradation** (MAE 18.05 to 27.50) reveals the model is not robust to regulatory regime changes. This is a valuable caution for policy applications.

### Remaining concerns (minor)

1. The corrected chimney saving (21.1 kWh/m2/yr) is still large and unvalidated by field measurement. The paper appropriately hedges this as a hypothesis, but the number will inevitably be quoted without the caveat. Consider adding a prominently placed warning box or bolded sentence.
2. The sh_fraction ablation reveals that most of the HDR loop's contribution comes from a partially endogenous feature. The paper should consider whether to report the composition MAE (18.05) or the clean-feature MAE (19.44) as the headline number, since the former may overstate the model's genuine contribution.
3. The per-dwelling counterfactual for heat pumps (86.7 kWh/m2/yr) seems implausibly large for some dwellings and may reflect model extrapolation for dwellings with very low baseline efficiency. Adding a physical plausibility filter (cap at some reasonable maximum) would strengthen the analysis.

These are minor points that do not prevent acceptance. The paper has been transformed from one that overclaimed systematically to one that is honest about its contributions and limitations.

---

**Signed off:** 2026-04-10
**Verdict:** The revisions are thorough and honest. The paper is now a competent sensitivity analysis of the DEAP formula with appropriate caveats. Accept with the minor suggestions above.
