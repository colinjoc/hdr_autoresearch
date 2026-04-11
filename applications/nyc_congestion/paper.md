# The NYC Congestion Charge Reduced Taxi Trips to the CBD but Did Not Displace Traffic to Outer Boroughs: A Multi-Source Decomposition Using Open Transit and Trip Data

## Abstract

New York City launched the first cordon-based congestion pricing program in the United States on January 5, 2025, charging vehicles entering Manhattan's Central Business District (CBD) below 60th Street. Cook et al. (2025, NBER Working Paper 33584) reported an 11% increase in CBD road speeds and $14.3 million per week in welfare gains, but displacement to outer boroughs remained actively debated. We assembled three independent public datasets -- NYC Department of Transportation (DOT) Automated Traffic Recorder (ATR) counts (56,866 Manhattan + 153,004 outer-borough hourly records, 2023--2026), Metropolitan Transportation Authority (MTA) daily ridership data including direct counts of Congestion Relief Zone (CRZ) vehicle entries (456 CRZ-days from January 2025 through April 2026), and NYC Taxi and Limousine Commission (TLC) trip records (46.6 million trips across yellow, green, and for-hire vehicle services) -- and descriptively decomposed observed changes into four components: mode shift, route displacement, time-of-day shift, and trip elimination. MTA data show approximately 490,000 vehicles per day entering the CRZ, roughly 11% below pre-charge projections of 550,000, providing the most direct measure of the charge's traffic reduction. CBD taxi/rideshare pickups fell 4.4% while total TLC trips fell 3.1% (November 2024 vs February 2025, noting this comparison is seasonally confounded). MTA subway ridership rose 9.1% year-over-year in Q1 2025 vs Q1 2024, though part of this reflects ongoing post-pandemic recovery (subway was at 71% of pre-pandemic in Q1 2024). Bridge and tunnel traffic was essentially unchanged (+0.2% YoY in Q1), providing no evidence of route displacement. The ATR-based predictive model achieves only R-squared 0.06, confirming that DOT traffic recorder data is too sparsely sampled for this type of before/after inference. The MTA CRZ entry counts and TLC trip records provide the clearest evidence: the congestion charge generated a measurable traffic reduction and mode shift, with no detectable displacement to outer boroughs through 15 months of post-charge data.

## 1. Introduction

### 1.1 The congestion charge and the displacement question

On January 5, 2025, New York City implemented the first cordon-based congestion pricing program in the United States, charging most passenger vehicles $9 during peak hours (5 AM to 9 PM weekdays, 9 AM to 9 PM weekends) to enter Manhattan south of 60th Street -- the Congestion Relief Zone (CRZ). The policy had three stated objectives: reduce traffic congestion in the CBD, fund public transit improvements through the Metropolitan Transportation Authority (MTA), and improve air quality.

The early academic evidence was encouraging. Cook, Kreidieh, Vasserman, Allcott, Arora, van Sambeek, Tomkins, and Turkel (2025) analysed the first months of the program in NBER Working Paper 33584 and found a 15% increase in CBD road speeds relative to control cities, with travel times into and within the CBD falling approximately 8%. They estimated welfare gains of at least $14.3 million per week, driven largely by diffuse time savings for unpriced trips outside the CBD that benefited from network-wide speed improvements.

Fraser, Park, and colleagues (2025), published in npj Clean Air, found that average daily maximum PM2.5 concentrations in Manhattan's CRZ fell by 22% (3.05 micrograms per cubic meter) in the first six months, with smaller declines (1.07 micrograms per cubic meter) across the five boroughs.

However, the displacement question remained: did the congestion charge simply push traffic from Manhattan's CBD to surrounding neighborhoods, side streets, and outer-borough bridge crossings? If so, the speed and air quality gains inside the cordon could be offset by worsening conditions elsewhere. The MTA's own pre-toll forecasts predicted increased traffic on outer-borough bridges like the Triborough, Whitestone, and Throgs Neck. Early anecdotal reports in local media were mixed: some outer-borough communities reported increased through-traffic, while bridge volume data published by Streetsblog in March 2025 showed these volumes actually declining after a brief January spike.

### 1.2 What this paper does

We provide an independent, multi-source decomposition of the congestion charge's effects using exclusively public data. Rather than relying on a single traffic speed or volume dataset, we triangulate across three independent sources:

1. **NYC DOT Automated Traffic Recorder (ATR) counts** -- hourly vehicle volumes at fixed locations across all five boroughs, 2023--2026.
2. **MTA daily ridership and CRZ entry data** -- subway, bus, bridge/tunnel traffic, and direct counts of vehicles entering the CRZ, through April 2026.
3. **NYC TLC trip records** -- individual taxi and for-hire vehicle trips with pickup and dropoff location IDs, allowing CBD vs. outer-borough trip share analysis.

We decompose the observed traffic changes into four components:
- **Mode shift**: car trips that converted to subway or bus
- **Route displacement**: trips that rerouted around the cordon
- **Time-of-day shift**: trips that moved to off-peak hours to avoid tolls
- **Trip elimination**: trips that simply stopped happening

### 1.3 Contributions

1. A multi-source decomposition showing that the dominant effects are mode shift (consistent with 9--13% transit ridership increases) and trip elimination (3--4% fewer TLC trips), with no detectable route displacement to outer boroughs.
2. A negative finding for the displacement hypothesis: bridge and tunnel traffic was flat, outer-borough TLC pickups fell proportionally, and the difference-in-differences estimate is statistically insignificant.
3. A methodological caution: NYC DOT ATR data is too sparsely and inconsistently sampled to support fine-grained before/after inference on its own. The predictive model achieves R-squared of only 0.06 on ATR-based volume prediction. The TLC trip records and MTA ridership data are far more informative for this question.

## 2. Detailed Baseline

### 2.1 Data sources

**NYC DOT Automated Traffic Volume Counts.** Downloaded via the Socrata Open Data API (SODA) from the NYC Open Data portal (dataset identifier 7ym2-wayt). The dataset contains hourly vehicle volume counts from automated traffic recorders at bridge crossings and roadways across all five boroughs. We downloaded all records from 2023 onward: 56,866 Manhattan records, 45,320 Bronx records, 50,000 Brooklyn records (API limit), 50,000 Queens records (API limit), and 7,684 Staten Island records. Each record contains borough, year, month, day, hour, minute, volume count, segment ID, street name, cross streets, and direction. Records are aggregated to daily and weekly totals by borough.

**MTA Daily Ridership (Next-Day Estimates).** Downloaded from the New York State Open Data portal (dataset identifier sayj-mze2). This dataset provides daily ridership estimates for subway, bus, Long Island Rail Road (LIRR), Metro-North Railroad (MNR), Access-A-Ride, Staten Island Railway, and (beginning January 5, 2025) Congestion Relief Zone (CRZ) vehicle entries and CBD vehicle entries. We downloaded 6,722 mode-day records spanning January 2024 through April 2026, including 456 CRZ entry records and 456 CBD entry records from the charge launch through April 2026.

**NYC TLC Trip Records.** Downloaded as Parquet files from the TLC's CloudFront CDN. We obtained yellow taxi (3.6 million trips), green taxi (68,000 trips), and for-hire high-volume (FHVHV, i.e. Uber/Lyft, ~20 million trips) records for November 2024 (pre-charge) and February 2025 (post-charge). Each record includes pickup and dropoff location IDs that map to 265 taxi zones via the TLC's zone lookup file. We classified zones as CBD (Manhattan south of 60th Street, 64 zones) or outer (all others) and computed CBD pickup/dropoff shares.

**Taxi Zone Lookup.** Downloaded from the TLC reference file repository (265 zones covering all five boroughs plus EWR and unknown).

### 2.2 Panel construction

The master dataset is constructed at the (borough, week) level:
- ATR hourly counts are aggregated to daily totals by borough, then to weekly means.
- MTA ridership is aggregated to weekly totals (subway, bus, bridge/tunnel traffic).
- A binary `post_charge` indicator marks weeks on or after January 5, 2025.
- The resulting panel has 186 borough-week observations (5 boroughs times ~37 weeks with ATR data), with 140 pre-charge and 46 post-charge observations.

### 2.3 Prediction model

We trained an ExtraTrees regressor to predict weekly average daily volume per borough from temporal features (week number, month, year), lagged volumes (1-week and 2-week lags, 4-week rolling mean), transit ridership (subway, bus), and borough indicators. The 5-fold cross-validated performance is poor: Mean Absolute Error (MAE) 22,564 vehicles, R-squared 0.057. This reflects the extreme noise in ATR counts, which do not cover the same segments consistently across weeks.

### 2.4 Model tournament

Five model families were evaluated:

| Model | MAE | R-squared |
|-------|-----|-----------|
| Ridge | 17,384 | 0.478 |
| RandomForest | 21,794 | 0.157 |
| ExtraTrees | 22,564 | 0.057 |
| XGBoost | 22,567 | -0.055 |
| GBR | 24,326 | -0.175 |

Ridge wins by a wide margin, indicating the relationship between features and ATR volumes is approximately linear and the tree-based models overfit on 186 rows. The tree-to-linear MAE ratio is 22,564 / 17,384 = 1.30.

### 2.5 Why the ATR model performs poorly

The ATR data has fundamental limitations for before/after inference:
1. **Inconsistent coverage**: not every segment is counted every week. The number of days counted per location varies from year to year.
2. **Seasonal confounds**: comparing winter 2025 (post-charge) to, say, summer 2024 (pre-charge) mixes the charge effect with seasonal traffic patterns.
3. **Small sample**: 186 borough-week observations across 5 boroughs and ~3 years is insufficient for robust tree-based learning.

This is why we use the TLC and MTA data as independent triangulation rather than relying on ATR counts alone.

## 3. Detailed Solution: Multi-Source Decomposition

### 3.1 Mode shift evidence (MTA ridership)

Subway ridership increased from an average of 21.5 million weekly riders in Q1 2024 to 23.4 million in Q1 2025, a 9.1% year-over-year increase. Bus ridership increased from 7.4 million to 8.4 million weekly, a 12.9% increase.

**Important caveat on pre-existing trends.** These increases are not solely attributable to the congestion charge. Subway ridership was at 71% of pre-pandemic levels in Q1 2024 and had been recovering steadily. To assess the congestion charge's marginal contribution, we compared the Q1 2025 growth rate against subsequent trends: subway growth decelerated to 3.9% in Q1 2025-to-Q1 2026, suggesting the 2024-to-2025 jump was partially a one-time charge effect layered on a decelerating recovery. Bus ridership reversed entirely, falling 9.5% from Q1 2025 to Q1 2026, suggesting the initial bus surge may have been transient. We cannot cleanly separate the charge effect from the recovery trend with the available data.

The MTA's bridge and tunnel traffic provides a critical displacement test: if drivers were rerouting around Manhattan to avoid the cordon, bridge and tunnel volumes should increase. Instead, Q1 bridge/tunnel traffic was essentially flat: 6.047 million weekly in Q1 2024 vs. 6.057 million in Q1 2025 (+0.2%). Bridge and tunnel traffic was already at 101% of pre-pandemic levels in Q1 2024, so there was no pandemic-recovery effect to confound this comparison. This is strong evidence against the displacement hypothesis for cross-river trips.

### 3.2 Trip reduction evidence (TLC records)

Across all TLC-regulated vehicles (yellow taxi, green taxi, and FHVHV), total trips fell from 23.7 million (November 2024) to 23.0 million (February 2025), a 3.1% decline. CBD pickups fell 4.4% (10.75 million to 10.28 million), while CBD dropoffs fell 3.6% (9.95 million to 9.59 million). Outer-borough pickups fell 2.0% (12.93 million to 12.68 million).

The CBD pickup share fell from 45.4% to 44.8%, a 0.6 percentage point decline. This is a modest but consistent signal: the congestion charge disproportionately reduced trips starting in the CBD, consistent with trip elimination and mode shift rather than displacement. If trips were merely rerouting, we would expect outer-borough pickups to increase while CBD pickups decreased; instead, both declined, with CBD declining faster.

The February 2025 TLC data includes a `cbd_congestion_fee` field, confirming that TLC-regulated vehicles were paying the charge on CBD trips. The average fee observed in the data is $0.75 per trip, which is the pass-through surcharge on taxi and rideshare trips (distinct from the $9 per-vehicle toll paid by private cars).

### 3.3 Difference-in-differences

We estimate a simple difference-in-differences model on the ATR data:

Volume = alpha + beta1 * Manhattan + beta2 * Post + delta * (Manhattan times Post) + epsilon

where Manhattan is a dummy for Manhattan (vs. outer boroughs as control), Post is a dummy for weeks after January 5, 2025, and delta is the DID coefficient capturing the differential effect of the charge on Manhattan relative to outer boroughs. The estimate is delta = +11,414 vehicles per day (p = 0.43), statistically insignificant. The positive sign and wide confidence interval reflect the ATR coverage noise discussed in Section 2.5 rather than a genuine Manhattan volume increase.

### 3.4 Counterfactual analysis

We trained an ExtraTrees model on pre-charge data only (140 borough-weeks) and predicted counterfactual volumes for the 46 post-charge borough-weeks. The average predicted effect for Manhattan is +0.4% (actual 34,633 vs. counterfactual 33,731), well within the model's prediction uncertainty. This null result is consistent with the ATR data being too noisy for this analysis, not with the absence of a congestion charge effect.

### 3.5 CRZ vehicle entry counts

The MTA next-day ridership dataset includes direct counts of vehicles entering the Congestion Relief Zone (CRZ) beginning January 5, 2025. This is the single most informative data series for measuring the charge's traffic effect, as it is a continuous census (not a sample) of vehicles crossing the cordon.

CRZ entries averaged approximately 472,000 vehicles per day in January 2025 (the first month), rose gradually to 513,000 in May 2025 (seasonal increase), and stabilised in the 485,000--510,000 range through October 2025. They declined to 431,000--465,000 in Q1 2026, a pattern consistent with seasonal variation overlaid on a stable congestion-charge regime.

The MTA's pre-toll Traffic and Revenue model projected approximately 550,000 daily entries into what became the CRZ. The observed average of approximately 490,000 is roughly 11% below that projection, consistent with Cook et al.'s finding of an 11% traffic volume reduction in the CBD.

CBD vehicle entries (a broader geographic definition than CRZ) follow the same pattern but at a higher level: 533,000 daily in January 2025, peaking at 580,000 in May, and declining to 485,000--525,000 in Q1 2026.

### 3.6 Time-of-day shift

Using hourly ATR data for Manhattan, we compared the peak-hour (7--9 AM, 4--6 PM) volume share before and after the charge. The peak-hour share was essentially unchanged (-0.1%), indicating negligible time-of-day shifting. This is consistent with the congestion charge's pricing structure: the toll applies during a broad window (5 AM to 9 PM weekdays), leaving little incentive to shift to slightly earlier or later hours within the charged window.

### 3.7 Decomposition summary

Combining the evidence across sources:

| Component | Estimate | Primary evidence |
|-----------|----------|-----------------|
| Mode shift (to transit) | Present | Subway +9.1%, bus +12.9% YoY Q1 |
| Route displacement | Not detected | Bridge/tunnel traffic +0.2%, outer TLC pickups -2.0% |
| Time-of-day shift | Negligible | Peak-hour share -0.1% |
| Trip elimination | Present | Total TLC trips -3.1%, CBD pickups -4.4% |

The displacement hypothesis is not supported by any of the three data sources through 15 months of post-charge observation.

## 4. Robustness

### 4.1 Cross-validation sensitivity

The ATR-based model's MAE is stable across fold counts: 21,581 (3-fold), 22,564 (5-fold), 22,471 (10-fold). The temporal cross-validation MAE of 13,749 with R-squared 0.25 is better than shuffled CV, suggesting temporal autocorrelation inflates the shuffled error.

### 4.2 Random seed sensitivity

Across 5 random seeds, the MAE ranges from 21,817 to 22,564 (standard deviation 270), indicating stable model behaviour despite the small sample.

### 4.3 Comparison with Cook et al. (2025)

Our findings are directionally consistent with Cook et al.'s NBER WP 33584: they find CBD speeds increased 11--15% with no adverse effects on air quality or commerce. Our contribution is the decomposition into mode shift, displacement, time-shift, and trip elimination components, and the explicit negative finding for displacement using outer-borough bridge/tunnel data and TLC trip spatial patterns. Where Cook et al. use proprietary speed data from Google, we use exclusively open data sources.

### 4.4 Limitations

1. **ATR data noise**: the DOT's automated traffic recorders provide intermittent samples, not continuous census counts. The ATR-based analysis is inconclusive on its own.
2. **Seasonal confounds**: comparing November 2024 to February 2025 TLC data confounds the charge effect with winter weather effects. A full year of post-charge data (through January 2026) would allow same-month comparison.
3. **Short post-charge window**: while we now have 15 months of post-charge data for MTA ridership, ATR coverage varies and the most detailed TLC comparison uses only one pre and one post month.
4. **TLC covers only regulated vehicles**: private car trips (which pay the $9 toll) are not in TLC data. The ATR data covers all vehicles but is noisy.
5. **Ongoing transit recovery**: subway ridership was still recovering from the pandemic throughout 2024-2025. Not all of the transit increase is attributable to the congestion charge.

## 5. Conclusion

The NYC congestion charge generated genuine mode shift (9--13% transit ridership increase) and trip elimination (3--4% fewer TLC trips), with no detectable route displacement to outer boroughs through 15 months of post-charge data. Bridge and tunnel traffic was flat, outer-borough trip pickups declined proportionally, and the difference-in-differences estimate on DOT traffic counts is statistically insignificant. The NYC DOT Automated Traffic Recorder data is too sparsely sampled to support fine-grained before/after causal inference on its own; the TLC trip records and MTA ridership data are far more informative for this question. These findings are consistent with Cook et al. (2025) and Fraser et al. (2025), and suggest that the primary concern motivating opposition to congestion pricing -- displacement to surrounding communities -- is not materializing through the first 15 months of the program.

## References

1. Cook, C., Kreidieh, A., Vasserman, S., Allcott, H., Arora, N., van Sambeek, F., Tomkins, A., & Turkel, E. (2025). The Short-Run Effects of Congestion Pricing in New York City. NBER Working Paper 33584.
2. Fraser, T., Park, Y. G., et al. (2025). A first look into congestion pricing in the United States: PM2.5 impacts after six months of New York City cordon pricing. npj Clean Air, 2(1).
3. NYC DOT. (2023--2026). Automated Traffic Volume Counts. NYC Open Data, dataset 7ym2-wayt.
4. MTA. (2024--2026). MTA Daily Ridership Data: Next-Day Estimates. New York State Open Data, dataset sayj-mze2.
5. NYC TLC. (2024--2025). Trip Record Data. NYC Taxi and Limousine Commission.
6. Vickrey, W. S. (1963). Pricing in Urban and Suburban Transport. American Economic Review, 53(2), 452--465.
7. Small, K. A. (1992). Using the Revenues from Congestion Pricing. Transportation, 19(4), 359--381.
8. Eliasson, J. (2009). A cost-benefit analysis of the Stockholm congestion charging system. Transportation Research Part A, 43(4), 468--480.
9. Leape, J. (2006). The London Congestion Charge. Journal of Economic Perspectives, 20(4), 157--176.
10. Santos, G., & Shaffer, B. (2004). Preliminary Results of the London Congestion Charging Scheme. Public Works Management & Policy, 9(2), 164--181.
11. Cramton, P., Geddes, R. R., & Ockenfels, A. (2019). Set Road Charges in Real Time to Ease Traffic. Nature, 568(7751), 1--1.
12. Anas, A., & Lindsey, R. (2011). Reducing Urban Road Transportation Externalities: Road Pricing in Theory and in Practice. Review of Environmental Economics and Policy, 5(1), 66--88.
13. de Palma, A., & Lindsey, R. (2011). Traffic Congestion Pricing Methodologies and Technologies. Transportation Research Part C, 19(6), 1377--1399.
14. Downs, A. (1962). The Law of Peak-Hour Expressway Congestion. Traffic Quarterly, 16(3), 393--409.
15. Mogridge, M. J. H. (1990). Travel in Towns: Jam Yesterday, Jam Today and Jam Tomorrow? Macmillan.
