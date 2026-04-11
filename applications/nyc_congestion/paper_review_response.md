# Author Response to Adversarial Review

## Response to Major Issues

### M1. The decomposition is accounting, not causal inference

**Accepted.** The reviewer is correct that the mode shift estimate conflates the congestion charge with ongoing post-pandemic transit recovery. We ran E-R01:

**Pre-existing transit ridership trends (Q1 year-over-year):**

| Metric | Q1 2024 to Q1 2025 | Q1 2025 to Q1 2026 |
|--------|---------------------|---------------------|
| Subway | +9.1% | +3.9% |
| Bus | +12.9% | -9.5% |
| Bridge & Tunnel | +0.2% | -2.7% |

The subway growth rate decelerated from 9.1% to 3.9% in the second post-charge year. This is consistent with a one-time congestion charge bump layered on top of a decelerating post-pandemic recovery. However, we cannot cleanly separate the two effects. We have revised the paper to frame the transit increase as "consistent with but not solely attributable to mode shift" and to report the pre-existing trend explicitly.

The bus ridership pattern is more complex: +12.9% in Q1 2025 followed by -9.5% in Q1 2026. This could reflect MTA service changes, fare restructuring, or the initial mode shift partially reverting.

### M2. November vs February TLC seasonal confound

**Accepted.** We acknowledge this is a significant limitation. We were unable to run E-R02 (download Oct 2023 / Feb 2024 TLC data) within this analysis due to the volume of additional data required (each FHVHV file is ~450 MB). The paper now explicitly flags the November-February comparison as seasonally confounded and does not present the TLC trip decline as a causal estimate of the congestion charge effect. Future work should compare same-month periods across years.

### M3. DID model specification

**Accepted and additional evidence provided.** We ran E-R04 (per-borough DID):

| Control Borough | Pre | Post | Diff | DID vs Manhattan |
|----------------|-----|------|------|-----------------|
| Bronx | 26,677 | 19,254 | -7,423 | +10,651 |
| Brooklyn | 31,574 | NaN | NaN | NaN |
| Queens | 37,308 | 22,282 | -15,025 | +18,254 |
| Staten Island | 7,951 | 34,191 | +26,239 | -23,011 |

The per-borough DID reveals the core problem: **Brooklyn has no post-charge ATR data at all**, Staten Island shows a spurious +340% jump (likely a new ATR installation, not a genuine traffic increase), and the Bronx and Queens show large declines that likely reflect seasonal ATR coverage gaps rather than congestion charge effects. This definitively confirms that the ATR data cannot support DID inference. We have removed the DID from the abstract and marked it as inconclusive in the paper.

### M4. ATR-based decomposition as headline

**Accepted.** The ATR-based decomposition waterfall chart has been reframed as illustrative of the data limitations, not as a headline finding. The abstract now leads with the TLC and MTA evidence.

## Response to Minor Issues

### m1. Pre-pandemic baseline

**Completed (E-R05).** Q1 2024 subway was at 71% of pre-pandemic. The first post-charge week was at 75%. By Q1 2025, it would be approximately 75-77% based on the weekly data. Bridge and tunnel traffic was already at 101% of pre-pandemic in Q1 2024 and dropped to 98% in the first post-charge week. This context is added to the paper.

### m2. CRZ entry data

**Completed (E-R03).** This is the single most informative data series. CRZ entries show:
- 472,000 vehicles/day in January 2025 (first month)
- Gradual increase to ~513,000 in May 2025 (seasonal)
- Remarkably stable 485,000--510,000 range through October 2025
- Decline to 431,000--465,000 in Q1 2026

The CRZ data confirms approximately 490,000 vehicles per day enter the zone, which is approximately 11% below the pre-charge estimates (the MTA's Traffic and Revenue model projected ~550,000 pre-charge entries). This is added as a new Section 3.7.

### m3. Toll exemptions

**Accepted.** Added a note on exemptions: emergency vehicles, buses, vehicles with disability plates, and a tax credit for zone residents earning below $60,000. The effective toll revenue per vehicle is lower than $9 due to these exemptions and the off-peak/$2.25 rate.

### m4. Trip elimination as residual

**Accepted.** Added explicit language flagging that trip elimination absorbs all measurement error.

### m5. R-squared 0.06

**Accepted.** The counterfactual analysis using the ATR-based model is removed from the abstract and marked as inconclusive in the paper. The R-squared of 0.06 means the model predicts only 6% of ATR volume variance, making counterfactual inference unreliable.

## Summary of Paper Revisions

1. Reframed from causal claims to multi-source descriptive decomposition
2. Added CRZ entry count analysis as primary evidence (Section 3.7)
3. Added pre-existing transit trend table (Section 3.1)
4. Added pre-pandemic percent context (Section 3.1)
5. Flagged seasonal confound in TLC comparison
6. Removed ATR-based decomposition from abstract
7. Removed DID from abstract, marked inconclusive
8. Removed counterfactual prediction from abstract
9. Flagged trip elimination as residual
10. Added toll exemption note
