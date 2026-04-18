# Blind Review: AARO Case Resolution Analysis

**Reviewer**: Independent sub-agent (Phase 2.75)
**Date**: 2026-04-16
**Paper**: "What 1,652 Reports to the Pentagon's UAP Office Actually Tell Us"

---

## Summary

The paper extracts aggregate statistics from four U.S. government UAP reports and performs resolution-rate analysis, backlog modeling, Bayesian inference, historical base-rate comparison, and cross-database comparison with NUFORC data. The analysis is competent and the writing is clear. However, five issues require either correction, additional experiments, or explicit acknowledgment before the paper can proceed.

---

## ISSUE 1 (BLOCKING): Bayesian likelihood model assumes P(unresolved | anomalous) = 1.0 — this is wrong

**Concern**: The Bayesian posterior (Section 4.5, Section 5.4) sets P(unresolved | anomalous) = 1.0, asserting that a genuinely anomalous object would always remain unresolved. This is false. A genuinely anomalous object could produce high-quality sensor data (e.g., clear radar track, IR signature, multiple witnesses) and be correctly *resolved as anomalous* — meaning identified, investigated thoroughly, and classified as "merit IC/S&T analysis" or even as a novel phenomenon. In fact, AARO's 21 IC-merit cases are plausibly the subset where the data was good enough to recognize something unusual. A truly anomalous object with clear data would be *more* resolvable, not less.

**Mandated experiment**: `RV_BAYES_LIKELIHOOD` — Re-run Bayesian analysis with P(unresolved | anomalous) = {0.5, 0.7, 0.8, 0.9, 1.0} as a sensitivity parameter. Report the full posterior surface across both prior and likelihood dimensions. Document the assumption explicitly and justify the chosen value. The 21 IC-merit cases suggest P(resolved-as-anomalous | anomalous) > 0, which means P(unresolved | anomalous) < 1.0.

---

## ISSUE 2 (BLOCKING): "Backlog growing at 2.6x" uses inconsistent denominators

**Concern**: The 2.6x ratio (Section 5.2, E02) compares intake of 58.2/month (which includes 272 prior-period catch-up reports, inflating the numerator) against resolution of 22.5/month (current-period only). The paper notes the catch-up issue in Section 3 but still headlines the 2.6x figure in the abstract and conclusion. With catch-up excluded, intake is 37.3/month, giving a ratio of 37.3/22.5 = 1.66x. Both figures should be reported prominently, and the abstract/conclusion should use the more conservative 1.66x or explicitly state which denominator is used.

**Mandated experiment**: `CONTROL_BACKLOG_RATIO` — Compute and report the backlog ratio under both denominators side-by-side. Update abstract and conclusion to use the adjusted ratio (37.3/22.5 = 1.66x) as the primary figure, with the unadjusted 2.6x as a secondary/worst-case bound. Add a row to results.tsv.

---

## ISSUE 3 (BLOCKING): "100% of resolved cases are prosaic" is selection-biased — paper must acknowledge tautology

**Concern**: The paper repeatedly emphasizes that 100% of resolved cases are prosaic (abstract, Section 5.1, Section 6.1, Section 7). But this is partially tautological: AARO resolves cases by identifying them as known objects. Cases that cannot be identified as known objects are, by definition, not resolved — they go to Active Archive or IC-merit. The resolution process itself selects for prosaic outcomes. The 100% figure tells us about AARO's resolution methodology, not about the underlying population. A fair analogy: "100% of fish caught in a net with 10cm mesh are larger than 10cm" is true but tells you about the net, not the ocean.

The paper's Section 6.5 ("What We Cannot Answer") partially addresses this, but the abstract and conclusion present the 100% figure as a positive finding rather than a methodological artifact. The selection bias must be flagged each time the 100% figure appears.

**Mandated experiment**: `DIAG_SELECTION_BIAS` — Add a diagnostic analysis: compute the fraction of the total caseload that has been subjected to full investigation (i.e., cases with sufficient data that went through the resolution pipeline). If only ~20% of cases have sufficient data for investigation, then "100% of the 20% we could investigate are prosaic" is a very different claim from "100% are prosaic." Compute and report: (a) number of cases with sufficient data, (b) resolution rate among data-sufficient cases, (c) explicit selection-bias caveat on every use of the 100% figure.

---

## ISSUE 4 (MAJOR, NON-BLOCKING): Blue Book 5.6% as baseline — methodological concerns not adequately discussed

**Concern**: The paper uses Blue Book's 5.6% unidentified rate as the Bayesian prior and as the primary historical benchmark (Section 3, Component 3). However, Blue Book was widely criticized for methodological problems: the Condon Committee's own assessment was mixed, the Robertson Panel (1953) explicitly recommended debunking, and Hynek himself later repudiated Blue Book's dismissive approach. The 5.6% figure may be artificially low because Blue Book investigators were incentivized to explain cases away. Conversely, Hendry's 11.4% (from a more rigorous independent study) is higher.

The paper cites the Condon Report [6] but does not discuss Blue Book's well-documented methodological problems. Using 5.6% as "the" base rate without this context is misleading.

**Required revision**: Add 2-3 sentences to Section 4.4 acknowledging Blue Book's methodological criticisms (Robertson Panel bias, Hynek's later dissent). Use the Hendry 11.4% as an upper bound and GEIPAN 3.5% as a lower bound. The 5% prior is defensible but the reader needs to know the range and the controversy.

---

## ISSUE 5 (MAJOR, NON-BLOCKING): NUFORC comparison — "convergent patterns" overstates the finding

**Concern**: The paper claims "convergent patterns" between AARO (military/institutional sensor data from trained observers) and NUFORC (civilian self-reports via web form). But these are fundamentally different populations: different observers (trained military vs. general public), different sensors (radar/IR/EO vs. naked eye/phone camera), different reporting incentives (duty-bound vs. voluntary), different geographic coverage (military bases vs. population centers). Finding that both see "lights and orbs" is expected — most aerial stimuli at distance look like lights, regardless of the observer. The convergence tells us about human perception, not about the underlying phenomenon.

The "Starlink effect in both" finding is genuinely interesting but not "convergent" — it is the same stimulus visible to everyone. That is trivially expected.

**Required revision**: Reframe Section 5.6 to distinguish (a) trivially expected convergence (similar shapes because human vision has similar limitations) from (b) genuinely informative convergence (if any). Remove or qualify "convergent patterns" language in the abstract. The NUFORC comparison is worth including for completeness but should not be presented as corroborating evidence.

---

## ISSUE 6 (MINOR): Missing sensitivity on resolution-rate counting convention

**Concern**: Section 4.2 mentions two counting conventions (7.1% formal-only vs. 17.7% including pending) but the paper exclusively uses 17.7% in the abstract and all subsequent analysis. The 174 pending-closure cases have not been formally closed. The sensitivity to this choice should be noted more prominently.

**Required revision**: Add the 7.1%-17.7% range to the abstract, not just the 17.7% point estimate.

---

## Mandated Experiments Summary

| ID | Type | Description | Status |
|----|------|-------------|--------|
| RV_BAYES_LIKELIHOOD | RUN_RV | Bayesian sensitivity across P(unresolved\|anomalous) = {0.5-1.0} | REQUIRED |
| CONTROL_BACKLOG_RATIO | CONTROL | Backlog ratio with/without catch-up reports | REQUIRED |
| DIAG_SELECTION_BIAS | DIAG | Selection-bias diagnostic: resolution rate among data-sufficient cases only | REQUIRED |

## Required Paper Revisions (Non-Experiment)

1. Add Blue Book methodological criticism to Section 4.4
2. Reframe NUFORC "convergent patterns" language in abstract and Section 5.6
3. Add resolution-rate range (7.1%-17.7%) to abstract
4. Add selection-bias caveat wherever "100% prosaic" appears
