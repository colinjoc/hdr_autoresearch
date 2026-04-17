# Phase 3.5 Signoff: U-3 Infrastructure Capacity Blocks

## Review Issues and Resolution

| # | Issue | Severity | Resolution | Verified |
|---|-------|----------|------------|----------|
| R1 | Ecological inference in headline estimate | MAJOR | Added Section 5.8 (plant-size sensitivity): range 954-1,701 ha; abstract now reports range with central estimate; Limitation #2 rewritten to explain ecological inference explicitly | YES |
| R2 | Dublin/Ringsend too optimistic | MODERATE | Section 5.4 rewritten: now states GREEN treatment status does not imply unconstrained development; quotes register's own network-exclusion disclaimer; notes Dublin's Victorian sewer vulnerability | YES |
| R3 | Network capacity caveat not prominent | MODERATE | Added as Limitation #1 (moved to top position); quotes the register verbatim: "provides wastewater treatment capacity information only and does not provide an indication of network capacity" | YES |
| R4 | One-off houses not quantified | MODERATE | E17 run: 23.7% of residential applications are one-off houses (27,939 of 117,793); figure added to Limitation #7 | YES |
| R5 | Fingal plant-level estimates implausible | MINOR | Section 6.3 rewritten: county-level rankings preferred over plant-level; Turvey Cottages / Newtown Cottages flagged as A-prefix hamlets unlikely to sit on 33 ha of zoned land; Limitation #8 added | YES |

## CSS Color Spot-Check (5 plants)

| Plant | County | CSV | HTML CSS | Match |
|-------|--------|-----|----------|-------|
| Ringsend WWTP | Dublin City | GREEN | `color:rgb(0, 128, 0)` = Green | YES |
| Turvey Cottages WWTP | Fingal | RED | `color:#C8102E` = Red | YES |
| Newtown Cottages WWTP | Fingal | RED | `color:#C8102E` = Red | YES |
| Palatine WWTP | Carlow | AMBER | `color:#FF8C00` = Amber | YES |
| Abbeydorney WWTP | Kerry | RED | `color:#C8102E` = Red | YES |

## Tests

All 12 tests pass (`python -m pytest tests/ -x --tb=short`).

## Signoff

The paper now:
- Reports a sensitivity range (954-1,701 ha) alongside the central estimate (1,524 ha)
- Explicitly flags ecological inference as the methodology, not parcel-level matching
- Distinguishes treatment capacity (measured) from network capacity (excluded)
- Quantifies the one-off house share (23.7%) that is WWTP-independent
- Caveats plant-level investment priorities as illustrative
- Passes all data verification spot-checks

SIGNED OFF.
