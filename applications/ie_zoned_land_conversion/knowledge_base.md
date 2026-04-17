# Knowledge Base: IE Zoned Land Conversion

## Established Facts

1. **National zoned residential land stock**: 7,911 hectares (Goodbody 2024), down from 17,434 ha in 2014 — a 54.6% decline over 10 years.
2. **National application intensity**: 2.72 residential permission applications per hectare of zoned land per year [95% CI: 2.59, 2.94].
3. **Annual residential permission applications**: ~21,500 (2018-2024 mean).
4. **Annual capacity utilization**: 8.6% — only 8.6% of the theoretical 417,000-unit capacity enters the planning pipeline each year.
5. **Implied stock exhaustion**: At current rates, ~19.5 years to exhaust remaining zoned land.
6. **Regional variation**: Southern region (3.65 apps/ha/yr) > East+Midlands (3.09) > Northern+Western (1.63).
7. **Dublin paradox**: Dublin LAs have low intensity (0.61 apps/ha/yr) because Fingal's 3,519 ha dominates the denominator. Non-Dublin: 5.76 apps/ha/yr.
8. **Fingal anomaly**: 0.08 apps/ha/yr — the lowest in the country despite the largest zoned land stock. This is the single most important finding.
9. **Spatial clustering**: Moran's I = 0.37 (p = 0.004) — application intensity is spatially clustered.
10. **Median decision lag**: 63 days for residential applications.
11. **Approval rate**: ~88% of decided residential applications are granted.
12. **One-off housing dominance**: 43.8% of residential applications are one-off houses; only 10.0% are apartments.
13. **Units per application**: Mean 2.8, median 1. The modal residential application is a single dwelling.
14. **Large schemes**: 50+ unit applications rose from 16/yr (2015) to ~120-140/yr (2018-2024).
15. **Viability ratio**: National median sale price / construction cost = 1.26, barely above the ~1.2 viability threshold.
16. **RZLT effect**: -7.1% change in applications post-announcement (2022-2024 vs 2018-2021), not statistically significant (p=0.40).
17. **Seasonal pattern**: Statistically significant (chi-squared=2425, p<0.001) but mild — ratio of peak to trough month is modest.
18. **Land price**: National median EUR 571,235 per hectare (RZLPA02).
19. **Pipeline latency**: Predecessor PL-5 found 1,096-day (3-year) median total pipeline from permission to completion.
20. **Build yield**: 59.6% of permissions become homes (PL-5). At this yield, need ~85,000 permissions/yr for 50,500 homes.

## Key Mechanisms

1. **Real option hold-out**: Landowners rationally delay development when uncertainty is high and the viability ratio is marginal (Titman 1985; Cunningham 2006).
2. **RZLT as option-value reducer**: The 3% annual tax is designed to impose a holding cost that shifts the development trigger downward.
3. **Infrastructure constraint**: Some RZLT-mapped land is zoned but lacks wastewater/transport capacity (Irish Water 2023).
4. **Viability constraint**: At viability ratio 1.26, small cost increases can render projects unviable.
5. **Fragmented ownership**: Multiple small landowners on zoned land reduce probability of coordinated development.
6. **Loss-aversion hold-out**: Landowners who purchased at Celtic Tiger prices may hold out rather than realize a loss (Kahneman and Tversky 1979).
7. **One-off dominance**: The prevalence of one-off applications (1 unit on what may be a large site) suggests landowners develop minimally, preserving options on the remainder.

## What Doesn't Work / Null Results

1. **Approval rate does not predict intensity**: r = -0.07 (p = 0.70). High-refusal LAs do not systematically receive fewer applications.
2. **Decision lag does not predict intensity**: r = 0.15 (p = 0.45). Longer processing times are not associated with fewer applications.
3. **One-off rate does not predict intensity**: r = -0.004 (p = 0.98). Infrastructure proxy (one-off housing share) is uninformative.
4. **Refusal rate does not predict intensity**: r = 0.076 (p = 0.69). Regulatory burden (proxied by refusals) shows no effect.
5. **Zoned land area does not predict application volume**: r = 0.02 (p = 0.91). LAs with more zoned land do not file more applications. This is a key finding — having land zoned is necessary but not sufficient.

## Pitfalls and Limitations

1. **Zoned land data is cross-sectional**: We have one national snapshot (Goodbody 2024) and one historical benchmark (2014). We cannot track individual parcels over time.
2. **LA-level zoned land allocation is approximate**: We distributed regional Goodbody figures to LAs proportionally by population, except for Fingal (known figure). This introduces measurement error.
3. **Planning register completeness**: Some LAs have incomplete data before 2017. We use 2018-2024 as the primary window.
4. **Application Type field is messy**: 71 distinct values requiring normalization. We filter on "PERMISSION" variants.
5. **Residential classification relies on text matching**: Description keyword search + NumResidentialUnits > 0. May over- or under-count.
6. **The ~38,000 figure in the research question includes all applications; residential permission applications are ~21,500/yr.**
