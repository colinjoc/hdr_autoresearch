# Phase 2.75 Blind Review: IE Housing Pipeline E2E

**Reviewer**: Automated blind reviewer agent
**Date**: 2026-04-16
**Paper**: "For Every 100 Irish Planning Permissions, How Many Become Homes?"

---

## Overall Assessment

The paper is a well-structured synthesis of four predecessor cohort studies into a three-stage pipeline yield model. The headline finding (35.1% CCC-yield) is computationally correct given its inputs. However, the paper has a critical framing problem: the 35.1% figure and the derived 144,000-permissions headline measure *CCC-certified yield*, not *build-yield*. Because the dominant attrition (opt-out non-filing) consists of homes that ARE built but DON'T file a CCC, the paper risks being read as "only 35% of permissions become homes" when the true build-completion rate is substantially higher. This distinction affects every policy conclusion.

---

## BLOCKING Issues (Mandated Experiments Required)

### R1: CCC-yield vs build-yield distinction must be foregrounded

**Problem**: The title asks "How Many Become Homes?" but the 35.1% answers "How many produce a *certified* home." Opt-out self-builds (31.6% of the cohort) ARE homes — they are built, occupied, and connected to utilities — they simply never file a CCC. The paper acknowledges this in Section 6.2 but the Abstract, Section 5.1 headline, and Section 7 conclusion all say "35 produce a certified completed home" without immediately distinguishing this from "35 become homes."

**Mandated experiment**: Add a parallel "build-yield" estimate. If opt-out homes are assumed to complete at the same rate as non-opt-out commenced projects minus the CCC filing step (i.e., they commence and are built but skip the CCC), the build-yield is approximately:
- Opt-out path: (1-lapse) x opt_out_share x build_completion_rate_for_self_builds
- Non-opt-out path: (1-lapse) x (1-opt_out_share) x non_opt_CCC_rate x CCC_to_occupied

Estimate the build-yield under the assumption that ~90% of opt-out commenced projects are actually built (a reasonable assumption given they are self-builds who filed a CN and thus started construction). Report both CCC-yield (35.1%) and estimated build-yield side by side. Revise the 144,000 figure to show the policy-relevant permissions-needed under build-yield.

### R2: The "144,000 permissions needed" headline is misleading as stated

**Problem**: If actual build-yield is ~70-80% (because opt-out homes ARE built), the permissions needed for 50,500 completions is ~63,000-72,000, not 144,000. The 144,000 figure is only correct if the policy target is "50,500 CCC-certified homes" which is not what Housing for All targets (it targets completions measured by ESB connections, which DO count opt-out homes).

**Mandated experiment**: Compute permissions-needed under build-yield as well as CCC-yield. Present both. The paper's existing Section 5.6 non-opt-out yield of 51.4% already implies 98,000 — but even this uses CCC as the completion criterion. The true build-yield scenario needs explicit computation.

### R3: Stage 2-to-3 attrition decomposition is incomplete

**Problem**: The paper states 59.1% non-filing at stage 2-to-3 but does not explicitly decompose this into:
(a) Opt-out projects that don't file by design (0% CCC rate, 31.6% of cohort = ~27,068 projects)
(b) Non-opt-out projects that SHOULD file but haven't yet or won't (~40.2% non-filing among non-opt-out = ~23,534 projects)

The paper has E15 (opt-out vs non-opt-out) and the non-opt-out rate (59.8%) but the Discussion does not explicitly present the decomposed attrition waterfall.

**Mandated experiment**: Add an explicit decomposition table to Section 5.2 showing how the 59.1% non-filing breaks down into regulatory opt-out vs genuine/pending non-completion among non-opt-out projects. Quantify what fraction of the 50,602 non-CCC projects are opt-out vs non-opt-out.

### R4: PL-4 join-failure caveats are insufficiently inherited

**Problem**: The 9.5% lapse rate from PL-4 is described as "NRU>0 2017-2019" but PL-4's own paper (Section 7, Caveat 1) is emphatic that this is still an *upper bound* on genuine lapse because it conflates real lapse with residual join failure. The PL-4 cluster-bootstrap CI is [4.4%, 15.6%], much wider than the E2E paper's implied precision. The E2E paper uses 9.5% as a point estimate with a separate upper bound of 27.4%, but does not propagate the PL-4 cluster-bootstrap CI.

**Mandated experiment**: Replace the current CI on yield (28.0%-35.4%) with a properly propagated CI that uses PL-4's cluster-bootstrap range [4.4%, 15.6%] for the lapse rate. The yield range should be:
- Upper yield: (1-0.044) x CCC_rate x 0.95
- Lower yield: (1-0.156) x CCC_rate x 0.95
This gives a wider range that honestly inherits PL-4's uncertainty.

### R5: Cox multi-state champion selection is weakly justified

**Problem**: The Cox model has a C-index of 0.500 for comm-to-CCC — exactly chance. It produces the same yield estimate as the binomial (0.3513) by using the KM-estimated CCC rate. Selecting it as "champion" on the grounds that it "provides a principled framework for incorporating covariates" when it demonstrably fails to do so (C=0.5) is misleading. The Cox model adds nothing over the binomial for yield estimation.

**Mandated experiment**: Either (a) downgrade the Cox model to "framework recommendation for future work with richer covariates" and select the Binomial as the primary yield model (since it produces the same answer with less machinery), or (b) explain honestly that C=0.5 means the survival model cannot discriminate between projects and the champion designation is aspirational, not empirical.

---

## NON-BLOCKING Issues (Should Fix)

### R6: E07 apartment CCC rate of 0.0% is suspicious

The results show `apt=0.0000; dwell=0.4086` (E07). A 0% CCC rate for ALL apartments in an 85,565-row dataset is implausible given that 10-49 and 50-199 unit schemes (which include apartments) have CCC rates of 86-89% (E01). This likely reflects a bug in the `apartment_flag` definition — the flag is based on `CN_Proposed_use_of_building` or `CN_Dwelling_House_Type` containing "apartment|flat", which may not match BCMS field conventions. The apartment CCC rate should be high, not zero.

**Recommendation**: Audit the apartment_flag definition. Check how many rows it matches and cross-reference with size strata. If the flag is broken, either fix it or remove E07 from the paper.

### R7: Stage independence assumption

The paper correctly notes (Section 6.3, Limitation 6) that the model assumes stage independence. The DES validation (T04: 35.2% vs 35.1%) appears to confirm this, but the DES also assumes independence by construction (it draws lapse/abandon independently). The validation is therefore circular. Note this in the text.

### R8: LDA double-counting caveat

The paper correctly handles LDA attribution vs additionality (Section 5.8). However, it should explicitly note that the PL-3 paper's own Phase 2.75 review flagged the same issue, and that the E2E paper inherits the corrected framing. This strengthens provenance.

### R9: The 95% CCC-to-occupied proxy

The paper acknowledges this is a proxy (Section 3.1) but does not provide any empirical basis for the 95% figure. A cross-check would be: CSO NDA12 completions (which use ESB connections) vs BCMS CCC filings for the same year. If BCMS CCC filings are available by year, a ratio of CSO-completions / CCC-filings would empirically calibrate Stage 3-to-4.

**Recommendation**: Add an empirical cross-check for the 95% estimate, or widen the CI to reflect that it could be anywhere from 85% to 100%.

---

## Summary of Mandated Experiments

| ID | Description | Blocking? |
|----|-------------|-----------|
| R1 | Add build-yield estimate alongside CCC-yield; revise title/abstract/conclusion framing | YES |
| R2 | Compute permissions-needed under build-yield scenario | YES |
| R3 | Decompose Stage 2-3 attrition into opt-out vs genuine non-completion | YES |
| R4 | Propagate PL-4 cluster-bootstrap CI [4.4%, 15.6%] into yield CI | YES |
| R5 | Justify or downgrade Cox champion designation given C=0.5 | YES |
| R6 | Audit apartment_flag (E07 apt=0.0% is likely a bug) | Non-blocking |
| R7 | Note DES independence validation is circular | Non-blocking |
| R8 | Note LDA caveat inheritance from PL-3 | Non-blocking |
| R9 | Cross-check or widen CI on 95% CCC-to-occupied proxy | Non-blocking |

---

## Verdict

**REVISE AND RESUBMIT.** The paper's computation is correct but its framing overstates attrition by conflating CCC-yield with build-yield. The five blocking issues must be resolved before the paper's headlines can be cited in policy contexts.
