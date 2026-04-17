# Phase 3.5 Signoff

**Date:** 2026-04-16

## Review Issues Resolution

| Issue | Severity | Status | Resolution |
|-------|----------|--------|------------|
| A: BEA04 volume index misused as physical output | CRITICAL | FIXED | Paper now states BEA04 is a deflated production index (+9%) and contrasts with CSO dwelling completions (+139%). Productivity narrative reversed: completions grew faster than employment, suggesting flat/positive productivity. E23 added to results.tsv. |
| B: NZEB causal claims confounded | MAJOR | FIXED | Difference-in-differences (E21) added with control group (cement, steel, plaster, blocks). DiD estimate is -4.0pp — control group inflated MORE than NZEB group. Paper now states NZEB did not cause material price inflation; possible quantity-per-dwelling effect acknowledged as limitation. E22 recomputed E20 with CAGR. |
| C: WPM28 input price vs installed cost | MAJOR | FIXED | Baseline section now explicitly states WPM28 tracks wholesale input prices per unit, not installed cost per dwelling. Limitations section explains that specification-driven quantity changes (thicker insulation, triple glazing) are invisible to WPM28. |
| D: PCA components uninterpreted | MINOR | FIXED | Factor Structure section now interprets all 3 PCs: PC1 = common inflation, PC2 = mineral vs. organic, PC3 = manufactured vs. bulk. Notes that NZEB materials do not form a distinct factor. |

## Additional Corrections Applied

- Abstract: Changed "structural steel fabricated metal (8.2%)" to "structural steel (7.8%)" — the parent category rather than the sub-sub-category.
- Removed duplicate references ([44]/[28] and [45]/[29]); renumbered.
- Expanded all abbreviations on first use (NZEB, HVAC, VAT, PCA, CAGR, SCSI, SEAI).
- T02 variance decomposition: added caveat that covariance-based shares do not sum to 100%.
- CAGR spread range corrected from "23-fold" to "16-fold" (using parent steel category).

## Mandated Experiments Executed

| ID | Result | Impact on Conclusions |
|----|--------|-----------------------|
| E21 | DiD = -4.0pp (NZEB group: +3.5pp excess; Control: +7.6pp excess) | Reverses NZEB narrative: regulatory effect is zero or negative after controlling for COVID/Ukraine. |
| E22 | CAGR-based excess: Insulation +3.86pp, Glass +3.59pp, HVAC +2.12pp, Electrical +4.56pp | Lower than E20 simple-percentage estimates (was +4.15, +3.60, +2.25, +5.11pp). Still confounded without DiD. |
| E23 | BEA04 volume +9%, value +48%, deflator +36%; Completions +139% vs Employment +103% | Apparent productivity decline was measurement artifact. Physical output grew faster than employment. |

## Test Suite

All 38 tests pass. No forbidden reviewer language in paper.md.

## Signoff

The paper is cleared for publication. All four review issues have been addressed with new experiments and substantive text changes. The most significant correction is the NZEB finding: the difference-in-differences analysis demonstrates that the naive pre/post comparison was dominated by COVID/Ukraine confounding, and that NZEB-affected materials actually inflated less than unaffected materials. The paper now correctly frames NZEB cost impact as a potential quantity-per-dwelling effect (not captured by WPM28) rather than a price-per-unit effect.
