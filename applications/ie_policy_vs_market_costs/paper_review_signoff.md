# Phase 3.5 Signoff: Policy-Set vs Market-Driven Costs in Irish Residential Development

## Review Mandate Checklist

| Issue | Mandate | Status | Evidence |
|:---|:---|:---|:---|
| A: VAT calculation | Clarify VAT is on output (reclaimed inputs) | DONE | Section 2.2 now explains input VAT reclaim |
| B: Part V cost | Reconcile fixed EUR 20k vs computed EUR 13.8k | DONE | Section 2.3 added; Section 3.7 updated with explicit reconciliation; cost stack labelled as conservative upper bound |
| C: Viability gap provenance | Confirm scheme-cost basis (0.85 factor) | DONE | Abstract, Section 2.1, Section 3.6, Section 5 all confirm scheme-cost basis |
| D: Static price assumption | Run E31 with 50% pass-through | DONE | E31 in results.tsv; new Section 3.8 reports: VAT zeroed goes from 3 to 0 viable counties; all-policy-zeroed from 4 to 3 |
| E: Developer margin classification | Add paragraph on POLICY-MARKET boundary | DONE | Section 2.4 classification note; new Section 4.4 discusses margin as boundary concept with E13 cross-reference |

## E31 Results Summary

- VAT zeroed with 50% pass-through: 0/26 counties viable (was 3/26 static)
- All policy zeroed with 50% pass-through: 3/26 counties viable (was 4/26 static)
- These results strengthen the central argument: even the headline VAT finding is fragile to pass-through assumptions

## Code Changes

- `run_experiments.py`: Added E31 pass-through experiment (lines 393-413)
- `tests/test_cost_model.py`: Added `TestPassThrough` class validating that pass-through reduces viable counties
- All 25 tests pass

## Paper Changes

- Abstract: Updated with pass-through caveat and scheme-cost confirmation
- Section 2.1: Added sentence on scheme-cost basis
- Section 2.2: Added VAT input-reclaim explanation
- Section 2.3: New section on Part V cost estimation with reconciliation
- Section 2.4: Added developer margin classification note
- Section 3.3: Added pass-through cross-reference
- Section 3.7: Updated with cross-subsidy reconciliation
- Section 3.8: New section on pass-through sensitivity (E31)
- Section 3.9: Renamed/reorganised margin compression results
- Section 4.1: Updated with pass-through finding
- Section 4.2: Added pass-through caution
- Section 4.4: New section on developer margin as policy-market boundary
- Section 4.5: Expanded limitations with pass-through and Part V notes
- Section 5: Updated conclusion with pass-through and scheme-cost language

## Signoff

All five mandated issues from paper_review.md have been addressed with code, tests, and text changes. The E31 pass-through experiment is the most significant addition: it materially weakens the claim that VAT reform can improve viability, strengthening the paper's central thesis that the crisis is market-driven.

**SIGNED OFF**: Paper ready for submission.
