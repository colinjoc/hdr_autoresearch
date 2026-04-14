# Design Variables — Candidate Features

**CRITICAL leakage rule**: every feature must be computable using ONLY
information available at time t to predict crash in window [t, t+h]
for h ∈ {3, 6, 12, 24} months. The most common bug in this literature
is using the realised peak date (which requires future data) to define
features. Any feature with a `LEAK` flag is banned from primary
analysis.

**Release-lag convention**: a "lag" below is the calendar delay between
the event and data availability. We additionally apply a conservative
+1 month buffer on top of published lags when constructing time t
features.

---

## Source 1: Zillow ZHVI (primary price series)

Release lag: ~1 month. Feature availability: month-end previous month.

| id | feature | definition | lag (mo) | leakage risk |
|----|---------|------------|---------:|---|
| Z01 | ZHVI_LVL | current metro ZHVI level | 1 | OK |
| Z02 | RET_1M | 1-month return | 1 | OK |
| Z03 | RET_3M | 3-month return | 1 | OK |
| Z04 | RET_6M | 6-month return | 1 | OK |
| Z05 | RET_12M | 12-month return | 1 | OK |
| Z06 | RET_24M | 24-month return | 1 | OK |
| Z07 | ACCEL_3M | 3m return minus prior-3m return (momentum deceleration) | 1 | OK |
| Z08 | VOL_12M | rolling 12m std of monthly returns | 1 | OK |
| Z09 | PEAK_DIST | current level / trailing 60m max | 1 | OK |
| Z10 | MEAN_REV | deviation from trailing 120m trend | 1 | OK |
| Z11 | TIER_SPREAD | top-tier ZHVI / bottom-tier ZHVI | 1 | OK |
| Z12 | PI_LOG | log(ZHVI / median HH income) | 4-12 | OK (income lag) |
| Z13 | PI_DEV | PI - metro's own 20y mean | 4-12 | OK |
| Z14 | PR_LOG | log(ZHVI / Zillow ZRI) — price-to-rent | 1 | OK |
| Z15 | PR_DEV | PR - metro's own 20y mean | 1 | OK |
| **LEAK_Z01** | PEAK_TO_TROUGH | realised peak-to-trough decline | future | BANNED |
| **LEAK_Z02** | SMOOTHED_FUTURE | ZHVI smoother uses future months | 3 | use unsmoothed raw ZHVI series |

## Source 2: Realtor.com inventory (leading indicators)

Release lag: ~1 month. Coverage: 2016-07 onward only.

| id | feature | definition | lag | leakage risk |
|----|---------|------------|-----:|---|
| R01 | ACTIVE_LISTINGS | count of active listings | 1 | OK |
| R02 | ACTIVE_YOY | YoY change in active listings | 1 | OK |
| R03 | NEW_LIST_YOY | YoY change in new listings | 1 | OK |
| R04 | DOM | median days on market | 1 | OK |
| R05 | DOM_YOY | YoY change in DOM | 1 | OK |
| R06 | PR_REDUCE | share of listings with price reduction | 1 | OK |
| R07 | PR_REDUCE_YOY | YoY change in PR_REDUCE | 1 | OK |
| R08 | MED_LIST_PRICE | median list price | 1 | OK |
| R09 | LIST_PRICE_YOY | YoY list-price change | 1 | OK |
| R10 | INV_TO | active listings / monthly sales | 1 | OK |
| R11 | INV_TO_YOY | YoY change in INV_TO | 1 | OK |
| R12 | SALE_LIST_RATIO | sale price / list price (lag by settlement time) | 2 | OK |
| R13 | PEND_SALES_YOY | pending-sales YoY | 1 | OK |
| R14 | PEND_CLOSE_SPREAD | pending - closed sales (widening spread = weakness) | 1 | OK |

## Source 3: FRED (macro covariates)

| id | feature | definition | lag | leakage risk |
|----|---------|------------|-----:|---|
| F01 | MORT30 | 30-year fixed rate | <1 (weekly) | OK |
| F02 | DMORT_3M | 3-month change in MORT30 | 0 | OK |
| F03 | DMORT_12M | 12-month change in MORT30 | 0 | OK |
| F04 | MORT_AFFORD | metro affordability index (ZHVI × 0.8 × rate) / income | 4-12 | OK |
| F05 | UNRATE | metro unemployment rate (BLS LAUS) | 1 | OK |
| F06 | UNRATE_YOY | YoY change in UNRATE | 1 | OK |
| F07 | CS_NAT | Case-Shiller national YoY | 3 | OK |
| F08 | TREAS10 | 10-year Treasury yield | 0 | OK |
| F09 | TERM_SPREAD | 10y − 2y Treasury | 0 | OK |
| F10 | SP500_YOY | S&P 500 YoY | 0 | OK |
| F11 | CPI_YOY | CPI YoY (real-rate adjustment) | 1 | OK |
| F12 | FED_FUNDS | effective federal funds rate | 0 | OK |

## Source 4: Census ACS (income denominators and demographics)

Release lag: ACS 5-year 2009-2022 in Dec, ~12 months after period end.
Use `as_of_year = t-2` to be safe.

| id | feature | definition | lag | leakage risk |
|----|---------|------------|-----:|---|
| C01 | HH_INCOME_MED | median household income | 12-24 | OK |
| C02 | HH_INCOME_GROWTH | 5-year income growth | 12-24 | OK |
| C03 | POP | metro population | 12-24 | OK |
| C04 | POP_YOY | YoY population change | 12-24 | OK |
| C05 | MIG_NET | net migration (ACS migration tables) | 12-24 | OK |
| C06 | EDU_SHARE | share population with college degree | 12-24 | OK |
| C07 | TECH_EMP_SHARE | employment share in info/tech NAICS | 12-24 | OK |
| C08 | AGE_MEDIAN | median age | 12-24 | OK |
| C09 | RENTER_SHARE | share rental tenure | 12-24 | OK |
| C10 | COMMUTE_WFH | share working from home (ACS S0801) | 12-24 | OK |

## Source 5: Census BPS (building permits)

Release lag: ~1-2 months.

| id | feature | definition | lag | leakage risk |
|----|---------|------------|-----:|---|
| B01 | PERMIT_CNT | monthly new residential permits | 2 | OK |
| B02 | PERMIT_YOY | YoY change in permits | 2 | OK |
| B03 | PERMIT_PCAP | permits per 1000 residents | 2 | OK |
| B04 | PERMIT_SALES | permits / monthly sales | 2 | OK |
| B05 | PERMIT_ACC | MoM acceleration in permits | 2 | OK |
| B06 | PERMIT_12M_SMOOTH | 12-month rolling permits | 2 | OK |

## Source 6: FHFA HPI (cross-check and extended history)

Release lag: 2 months quarterly. Coverage: all counties 1991-onward.

| id | feature | definition | lag | leakage risk |
|----|---------|------------|-----:|---|
| H01 | FHFA_RET_12M | FHFA metro 12-month return | 3 | OK |
| H02 | FHFA_PEAK_DIST | distance from trailing 60m peak | 3 | OK |
| H03 | ZHVI_FHFA_GAP | ZHVI - FHFA disagreement (quality flag) | 3 | OK |

## Source 7: Supply-elasticity (static, Saiz 2010)

| id | feature | definition | lag | leakage risk |
|----|---------|------------|-----:|---|
| S01 | SAIZ_ELAS | metro supply elasticity | static | OK |
| S02 | SAIZ_QUARTILE | quartile assignment | static | OK |
| S03 | WRLURI | Wharton regulatory index | static | OK |
| S04 | UNDEV_LAND | undevelopable-land share (Saiz input) | static | OK |

## Source 8: Derived cross-source interactions

| id | feature | definition | lag | leakage risk |
|----|---------|------------|-----:|---|
| X01 | PI_ELAS | PI × (1 - SAIZ_ELAS) | 4-12 | OK |
| X02 | DMORT_PI | DMORT_12M × PI | 4-12 | OK |
| X03 | INV_DOM | INV_TO × DOM | 1 | OK |
| X04 | MIG_WFH | MIG_NET × COMMUTE_WFH | 12-24 | OK |
| X05 | CREDITPROXY | HMDA mortgage-originations YoY × metro population (requires HMDA pull, optional) | 12 | OK if HMDA |
| X06 | INVESTOR_SHARE | non-occupant purchase share (Zillow) | 2 | OK if available |

## Banned / leakage features (documented to avoid)

- `LEAK_A` using the realised peak date in any feature
- `LEAK_B` using smoothed ZHVI (which uses trailing 3m including current) and then treating t as clean
- `LEAK_C` using 20-year peak-to-trough as a moderator
- `LEAK_D` using forward returns as features (obvious but worth stating)
- `LEAK_E` using any index that is revised ex-post (CoreLogic HPI revises first-release numbers — use vintage-appropriate data)
- `LEAK_F` using ACS 5-year estimate that includes the prediction year in its 5-year window
- `LEAK_G` using survey-based "crash expectations" fielded after the observed crash

## Feature count summary

| source | count |
|---|--:|
| Zillow ZHVI | 15 |
| Realtor.com | 14 |
| FRED macro | 12 |
| Census ACS | 10 |
| Census BPS | 6 |
| FHFA | 3 |
| Saiz / supply | 4 |
| Interactions | 6 |
| **TOTAL candidate features** | **70** |

Exceeds the 40-60 floor. Not all will be used — most will be dropped in
Phase 2 feature selection. The full 70 are documented so the reviewer
sees what was considered.

## Primary feature set (pre-registered)

For the primary logit baseline we pre-register the following 10
features:

1. Z12 PI_LOG (price-to-income log)
2. Z14 PR_LOG (price-to-rent log)
3. Z05 RET_12M (12-month return)
4. Z07 ACCEL_3M (deceleration)
5. Z09 PEAK_DIST (distance from trailing peak)
6. R11 INV_TO_YOY (inventory turnover YoY)
7. R05 DOM_YOY (days on market YoY)
8. R07 PR_REDUCE_YOY (price-reduction YoY)
9. F03 DMORT_12M (mortgage-rate 12m change)
10. S01 SAIZ_ELAS (supply elasticity)

All 10 have coefficient signs pinned to literature predictions (see
research_queue.md H3 on monotone constraints). Everything beyond these
10 is secondary / LightGBM-only.
