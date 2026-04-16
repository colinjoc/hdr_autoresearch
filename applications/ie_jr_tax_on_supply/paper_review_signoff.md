# Phase 3.5 Signoff: The Judicial-Review Tax on Irish Housing Supply

**Date**: 2026-04-16
**Reviewer**: Phase 3.5 signoff agent
**Paper**: `paper.md` (final, post-R1-R7)
**Review**: `paper_review.md` (Phase 2.75)

---

## R-mandate verification

| R# | Mandate | In results.tsv | In paper | Discharged? |
|----|---------|----------------|----------|-------------|
| R1 | Three-scenario imputation sensitivity | R1a, R1b, R1c | Section 5.8, Abstract, s5.1, s5.4 | YES. Floor=85,404; median=174,396; ad-hoc=105,504. Abstract quotes range. |
| R2 | Indirect 25% labelled as assumption | R2 | Section 5.3, Abstract, s6.2, caveat 3 | YES. Rebranded "illustrative midpoint"; no central in bounds table. |
| R3 | Endogenous-intake counterfactual | R3a, R3b, R3c | Section 5.5 | YES. 10% boost=15,806; 20%=14,973. |
| R4 | Holding-cost sensitivity and derivation | R4a, R4b, R4c, R4d | Section 5.7, caveat 8 | YES. EUR 500/1000/1500 table; land-share derivation; outcome-weighting caveat. |
| R5 | Construction-capacity ceiling | R5a, R5b, R5c | Section 5.5, Abstract, s6.3, caveat 5 | YES. 35K=7,421; 38K=13,421. **Headline revised** from 16,638 to [7,421-16,638]. |
| R6 | JR multiplier sensitivity | R6a, R6b, R6c, R6d | Section 5.9, caveat 12-13 | YES. 3x-10x range; 7x flagged as assumption; rho not used to support 25%. |
| R7 | Reconcile inconsistencies | R7a-R7f | Sections 5.1, 5.2, 5.6, 5.8 | YES. All six errors corrected: 2020 um, Dublin count, 2018-2021 total, E11 range, stated-um, cross-check. |

Total R-rows in results.tsv: 22 (R1a-R7f). All trace to paper sections.

---

## Headline survival assessment

| Original headline | Survived? | Revised to |
|-------------------|-----------|------------|
| 105,504 direct unit-months | YES with range | 105,504 [85,404-150,204] |
| 16,638-unit counterfactual gap | REVISED | [7,421-16,638] depending on capacity ceiling |
| EUR 52.8M holding cost | YES with range | EUR 52.8-158.3M depending on cost base |
| 25% indirect attribution | DOWNGRADED | "Illustrative midpoint"; bounds [0, 9,305] with no preferred point |
| JR explains 16.5% of rho | RETAINED as accounting | Flagged as assumption (7x multiplier); not used to support 25% |

---

## Residual concerns (non-blocking)

1. The imputation rule for the 13 cases remains ad-hoc (100-400 per case). A future project could cross-reference SHD applications in ABP's online planning register to obtain actual unit counts. This would collapse the [85,404-150,204] range to near-zero uncertainty.

2. The endogenous-intake feedback (R3) is modelled as a simple multiplicative offset. A formal two-equation model (ABP queue length -> developer filing -> ABP queue length) would be more rigorous, but the 5-10% sensitivity suggests this is second-order.

3. The paper still selects T05 as champion despite the capacity-ceiling sensitivity reducing it by up to 55%. T01 (direct accounting) is arguably the more robust deliverable. The paper acknowledges this ("T01 is the most robust") but retains T05 for policy relevance. This is a defensible editorial choice.

---

## Verdict

**NO FURTHER BLOCKING ISSUES.**

Every R-mandate from `paper_review.md` is discharged with results.tsv rows and paper text. The headline direct-delay figure (105,504 unit-months) survives with an honest sensitivity range. The counterfactual gap has been materially revised from a single point (16,638) to a range ([7,421-16,638]) that acknowledges construction-capacity constraints. The indirect channel is honestly bounded with the 25% labelled as illustrative. Numerical inconsistencies between paper and data are resolved. The paper no longer over-claims causation from the rho accounting identity.
