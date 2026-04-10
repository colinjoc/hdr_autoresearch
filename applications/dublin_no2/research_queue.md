# Research Queue — Dublin NO2

## Status Legend
- OPEN: not yet tested
- TESTED-KEEP: tested and kept
- TESTED-REVERT: tested and reverted
- CLOSED: no longer relevant

## Tested Hypotheses

| # | Status | Hypothesis | Prior | Result | Notes |
|---|--------|-----------|-------|--------|-------|
| H01 | TESTED-KEEP | Station fixed effects improve prediction | 90% | MAE 7.36→2.20 | Dominant improvement |
| H02 | TESTED-REVERT | Rush hour indicator helps | 50% | No improvement | XGBoost learns hour splits |
| H03 | TESTED-KEEP | Rush hour x weekday interaction | 60% | MAE 2.20→2.14 | Clean traffic timing signal |
| H04 | TESTED-REVERT | Wind from traffic corridor direction | 40% | No improvement | Tree learns wind_dir splits |
| H05 | TESTED-REVERT | Wind from port direction | 35% | No improvement | Same as H04 |
| H06 | TESTED-REVERT | Cold evening heating indicator | 45% | No improvement | Tree learns season x temp x hour |
| H07 | TESTED-REVERT | Temperature x heating interaction | 50% | No improvement | Same as H06 |
| H08 | TESTED-REVERT | Calm wind indicator | 40% | No improvement | Tree learns wind splits |
| H09 | TESTED-REVERT | Wind x BLH ventilation index | 45% | No improvement | Tree learns independently |
| H10 | TESTED-REVERT | Inverse ventilation coefficient | 45% | No improvement | Tree handles it |
| H11 | TESTED-REVERT | Rain washout | 30% | No improvement | Weak signal |
| H12 | TESTED-REVERT | COVID lockdown indicator | 35% | No improvement | Too few data points |
| H13 | TESTED-KEEP | Year trend for fleet electrification | 55% | MAE 2.14→2.01 | Captures gradual decline |
| H14 | TESTED-REVERT | Weekend early morning as background | 25% | No improvement | Sparse |
| H15 | TESTED-REVERT | Rush x wind direction interaction | 40% | No improvement | Tree learns it |
| H16 | TESTED-REVERT | Temperature inversion proxy | 35% | Marginal, below noise | |

## Open Hypotheses (for future work)

| # | Status | Hypothesis | Prior | Mechanism |
|---|--------|-----------|-------|-----------|
| H17 | OPEN | Actual DCC traffic counts improve over synthetic proxy | 70% | Real data has station-specific traffic load |
| H18 | OPEN | AIS-derived ship berth data helps at Ringsend | 55% | Direct shipping emission proxy |
| H19 | OPEN | Lagged NO2 from neighbouring stations | 60% | Plume transport between stations |
| H20 | OPEN | TROPOMI column as additional predictor | 40% | Satellite provides spatial context |
| H21 | OPEN | Boundary layer height from radiosonde | 65% | Real BLH better than proxy |
| H22 | OPEN | Dublin Bus GTFS vehicle count on nearby routes | 50% | Direct bus emission proxy |
| H23 | OPEN | Diesel share of fleet by year (CSO data) | 55% | Explains year trend mechanistically |
| H24 | OPEN | Building canyon effect proxy (station aspect ratio) | 30% | Street geometry traps NO2 |
| H25 | OPEN | O3-NO2 photochemistry coupling | 45% | NO2 = f(NOx, O3, UV) |
| H26 | OPEN | School term × rush hour interaction | 35% | School run adds traffic |
| H27 | OPEN | Congestion index from TomTom/Google | 60% | Congested traffic emits more NOx |
| H28 | OPEN | Wind persistence (rolling mean wind) | 35% | Sustained calm → accumulation |
| H29 | OPEN | Night-time vs daytime separate models | 30% | Different emission profiles |
| H30 | OPEN | Station-specific temporal patterns | 45% | Each station has unique diurnal profile |
| H31-H100 | OPEN | (See feature_candidates.md for full list of 100+ candidates) | Various | |
