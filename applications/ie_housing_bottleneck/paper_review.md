# Phase 2.75 Blind Review — Irish Housing Bottleneck Meta-Analysis

**Reviewer role**: Independent blind reviewer. No prior involvement with the project.

**Date**: 2026-04-16

**Paper reviewed**: `paper.md` — "Where Does the Binding Constraint on Irish Housing Delivery Actually Sit? A Meta-Analytic Bottleneck Ranking"

---

## Overall Assessment

The paper presents a well-structured Theory of Constraints (TOC) synthesis of thirteen predecessor studies, ranking ten candidate bottlenecks in the Irish housing pipeline. The headline finding — that permission volume is the binding constraint — is plausible and directionally supported. However, several critical methodological gaps undermine the claimed ranking precision and the stated confidence in the 37% gap-closure figure. The paper must address four mandatory experiments before publication.

**Verdict: REVISE — four mandatory experiments required.**

---

## Major Issues

### M1. Opt-out sensitivity: the ranking depends on an untested assumption

The paper's central reframing — from "CCC filing is the bottleneck" to "permission volume is the bottleneck" — depends entirely on the 90% opt-out build rate assumption (Section 2.3, Caveat 6). This is the single most consequential parameter in the analysis.

**Problem**: If the opt-out build rate is 50% rather than 90%, the effective yield drops from 60.9% to approximately 47%, and the effective completions fall from 23,143 to approximately 18,800. At 47% yield, reaching 50,500 completions requires 107,000 permissions — but more critically, CCC filing becomes a much larger contributor to the gap, and the bottleneck ranking between #1 (permission volume) and #3 (CCC filing rate) may swap under plausible parameter assumptions.

The paper acknowledges this in Caveat 6 but does not run the sensitivity sweep. The claim "permission volume is the binding constraint" requires demonstrating that this holds across the plausible range of opt-out build rates.

**Mandate R1**: Run an opt-out sensitivity sweep at build rates {50%, 70%, 90%, 100%}. For each, report: (a) effective yield, (b) effective completions, (c) marginal units/yr for permission volume (+10k) and CCC filing (+10pp), (d) whether the #1/#3 ranking swaps. Add a table to Section 5.

### M2. Ranking robustness: no uncertainty quantification on the ranking itself

The paper presents a deterministic ranking (Table in Section 3.2) with no confidence intervals on the marginal-units-per-year figures. The Monte Carlo analysis (Section 5.7) propagates uncertainty on completions but does not propagate uncertainty through the ranking. With 10 parameters each having wide CIs (lapse rate CI spans 4.4-15.6%), the ranking order may not be stable.

**Problem**: The reader is told that permission volume is rank #1 and CCC filing is rank #3, but the marginal-units-per-year for permission volume (+3,516 certified) and CCC filing (+3,267) are separated by only 249 units — less than 7%. Given the parameter uncertainty, these two could easily swap. The paper's policy conclusion ("push on permission volume, not CCC filing") rests on a ranking that may not be robust.

**Mandate R2**: Run a Monte Carlo ranking robustness test. Draw 5,000 parameter sets from the stated CIs (lapse from triangular [4.4%, 9.5%, 15.6%]; CCC from normal [40.9%, sigma=1%]; permission volume from normal [38k, sigma=3k]; opt-out build rate from uniform [50%, 100%]; CCC-to-occupied from triangular [90%, 95%, 99%]). For each draw, compute the marginal-units-per-year for each bottleneck and record the rank order. Report: (a) fraction of draws where permission volume is #1, (b) fraction where CCC filing outranks permission volume, (c) 90% CI on marginal-units-per-year for each bottleneck.

### M3. Double-counting in the combined-intervention scenario

Section 5.3 claims that "all efficiency combined" produces approximately 6,100 additional completions per year. The individual interventions listed sum to: ABP (1,060) + JR (1,060) + lapse halved (701) + CCC +10pp (3,267) = 6,088. But:

- ABP speed and JR removal use the **same** S-2 counterfactual. ABP at 18 weeks includes the JR channel (faster ABP partly because fewer JRs). Summing both double-counts the JR-ABP feedback.
- The S-2 paper itself states that the 1,060 figure for JR removal uses the 35k-cap counterfactual, which already incorporates ABP speed improvement. Listing ABP and JR as separate additive interventions is inconsistent with S-2's own model.

**Problem**: If ABP speed and JR removal overlap by even 50%, the combined efficiency figure drops from approximately 6,100 to approximately 5,600, and the "37% gap closure" drops to approximately 34%.

**Mandate R3**: Audit the ABP/JR overlap. Determine whether the S-2 counterfactual for ABP speed (E03a) is independent of the JR-removal counterfactual (E04). If they overlap, compute the non-overlapping combined effect and revise Section 5.3.

### M4. Bootstrap CIs on marginal-units-per-year for each bottleneck

The paper reports point estimates for each bottleneck's marginal impact but provides no uncertainty bands. Inherited CIs from predecessor studies are not propagated.

**Mandate R4**: For each of the top 5 bottlenecks (permission volume, construction capacity, CCC filing, ABP speed, JR removal), compute bootstrap 95% CIs on the marginal-units-per-year figure by sampling the underlying parameters from their stated CIs. Report in a table.

---

## Minor Issues

### m1. Construction capacity: hard constraint vs market equilibrium

The paper treats the 35,000-unit ceiling as a physical capacity constraint (Section 5.2), but 34,177 completions in 2024 may reflect equilibrium output under current demand conditions, not a supply ceiling. If developers face demand uncertainty or financing constraints, observed output could be below physical capacity. The CIF workforce gap (20%) is one input among many (materials, finance, land).

**Recommendation**: Add a sentence to Section 5.2 or Caveat 2 noting that the "capacity ceiling" is an observed ceiling, not a measured physical constraint. The paper already partially does this in Caveat 2 but should be more explicit in the results section.

### m2. Waterfall arithmetic self-consistency

The waterfall (Section 2.2) should verify: permissions - lapse - CCC non-filing - CCC-to-occupied loss = completions. Check: 38,000 - 3,610 - 20,324 - 703 = 13,363. The paper says 13,362. This is a rounding error of 1 unit — acceptable. The waterfall is self-consistent.

### m3. Inherited caveats insufficiently flagged

The paper acknowledges predecessor caveats in Section 7 but should explicitly list the key inherited uncertainties:
- PL-4 join-failure: the 9.5% lapse rate is an upper bound on genuine lapse (may be as low as 4.4%)
- S-2 indirect-channel attribution: the [0%, 50%] range on JR's indirect effect
- PL-1 channel-definition: the dark-permission rate ranges from 0.67% to 39% depending on definition

**Recommendation**: Add a short "Inherited Caveats" subsection to Section 7.

### m4. "Permission volume is a stock variable measured as a flow" (Caveat 7)

This caveat is important. The 38,000 figure is gross new permissions, not net new developable permissions. Extensions, modifications, and replacements mean the effective new-site permissions may be lower. The paper should note that the marginal-units-per-year calculation assumes each additional permission maps to a new site.

### m5. Missing bootstrap on the waterfall yield CI

The headline yield (35.2%) has no stated CI in the paper. The predecessor e2e paper reports [32.8%, 37.1%]. This should be cited here.

---

## Mandated Experiments Summary

| ID | Description | Status |
|----|-------------|--------|
| R1 | Opt-out sensitivity sweep (50%/70%/90%/100%) with ranking check | **MANDATORY** |
| R2 | Monte Carlo ranking robustness (5,000 draws, rank stability) | **MANDATORY** |
| R3 | ABP/JR double-count audit on combined-intervention scenario | **MANDATORY** |
| R4 | Bootstrap 95% CIs on marginal-units-per-year for top 5 bottlenecks | **MANDATORY** |

---

## Conditional Acceptance Criteria

The paper may proceed to Phase 3.5 signoff when:

1. R1 shows the opt-out sensitivity sweep and reports whether the ranking swaps at any tested build rate.
2. R2 shows the fraction of Monte Carlo draws where the ranking is preserved.
3. R3 resolves the ABP/JR overlap and revises the combined-intervention figure if needed.
4. R4 reports bootstrap CIs on each bottleneck's marginal-units-per-year.
5. The paper text is updated to reflect these results (new tables, revised claims if warranted).
