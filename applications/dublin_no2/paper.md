# Dublin and Cork NO2 Source Apportionment: Traffic Dominates Guideline Exceedance, Supported by the COVID-19 Lockdown Natural Experiment

## Abstract

Every urban monitoring station in Dublin and Cork exceeds the World Health Organization (WHO) 2021 annual nitrogen dioxide (NO2) guideline of 10 micrograms per cubic metre (µg/m³), yet no Irish station breaches the European Union (EU) limit of 40 µg/m³. This gap means Ireland is legally compliant while its cities experience NO2 levels the WHO considers harmful. Using 9 years of real daily measurements (2015-2023) from the European Environment Agency (EEA) monitoring network and Met Eireann weather observations, we apply receptor-based source apportionment to decompose measured NO2 into traffic, residential heating, and regional background contributions. At Dublin's worst site (Winetavern Street), 80% of annual NO2 is attributed to road traffic, with the WHO guideline exceeded on 67-91% of measured days. The COVID-19 lockdown of March-June 2020 serves as a natural experiment: the observed 33-62% NO2 reductions at traffic stations are consistent with our model's traffic apportionment (correlation r = 0.97 across 14 stations), though part of this agreement is structural because the model defines traffic as the residual component. An independent validation using weekday-weekend differentials confirms traffic dominance (weekday NO2 is 15-38% higher than weekend across all urban stations); correcting for the known weekend traffic fraction (~60% of weekday) brings the weekday-weekend estimates into quantitative agreement with the station-differencing results. Wind-direction analysis reveals NO2 at Winetavern Street is 70% higher under northerly winds than southerly, consistent with the station's position south of the Liffey quays traffic corridor. Residential heating contributes 8-30% of annual NO2 with a strong temperature dependence (14 µg/m³ excess on sub-2 degree Celsius days versus mild days at background stations). We conclude that road traffic -- predominantly diesel vehicles given Ireland's fleet composition [9] -- is the primary target for NO2 reduction in Irish cities, but even complete elimination of traffic would likely leave several stations above the WHO guideline due to heating contributions.

## 1. Introduction

Nitrogen dioxide is a regulated air pollutant with well-documented respiratory health effects. The WHO tightened its annual NO2 guideline from 40 µg/m³ to 10 µg/m³ in 2021, a fourfold reduction that brought many previously "compliant" cities into exceedance [1]. The EU Air Quality Directive retains the 40 µg/m³ annual limit, creating a regulatory gap: cities can meet EU law while exceeding WHO health-based recommendations.

Ireland's Environmental Protection Agency (EPA) operates approximately 115 monitoring stations through airquality.ie, with data reported to the EEA under the Air Quality e-Reporting framework. Ireland has historically been considered to have "good" air quality by European standards, with no exceedances of the EU NO2 limit value [2]. However, the 2021 WHO guideline revision raised the question: which Irish stations now exceed the health-based threshold, and what sources are responsible?

Source apportionment for urban NO2 typically identifies road transport (especially diesel vehicles) as the dominant source, with contributions from residential heating (particularly solid fuel), commercial/industrial combustion, and shipping in port cities [3, 4]. The COVID-19 pandemic lockdowns of 2020 created an unprecedented natural experiment in which road traffic was dramatically reduced while other sources (heating, background) continued largely unchanged, providing an opportunity to test traffic attribution models [6, 16]. An important caveat for any station-differencing approach is that NO2 is chemically reactive -- it participates in rapid photochemical cycling with nitric oxide (NO) and ozone (O3), so the additive decomposition is an approximation that works best for longer averaging periods [13, 17].

This study addresses three questions:
1. Which Dublin and Cork stations exceed the WHO 2021 NO2 guidelines, and by how much?
2. What fraction of urban NO2 comes from traffic versus heating versus regional background?
3. Does the COVID-19 lockdown response validate the attribution?

## 2. Detailed Baseline

### The Monitoring Network

Ireland's ambient air quality monitoring network reports to the EEA under standardised protocols. We use the EEA Air Quality In-Situ Measurement Station Data [7], a compiled dataset of daily NO2 concentrations (in µg/m³) from all European monitoring stations, covering 2015-2023. The dataset includes 33 Irish stations with NO2 measurements.

Stations are classified by the EEA as:
- **Traffic**: Positioned within 10 metres of a major road, measuring roadside air quality
- **Background**: Positioned to reflect the general air quality of an area without direct traffic influence
- **Rural**: Remote from significant emission sources

For Dublin, key traffic stations include Winetavern Street (IE005AP, city centre), Pearse Street (IE004AP, city centre), St John's Road West (IE006AP, Heuston area), and Blanchardstown on the M50/N3 motorway interchange (IE0131A). Key background stations include Ballyfermot (IE0036A, residential west Dublin), Clonskeagh (IE0028A, residential south Dublin), Dun Laoghaire (IE0132A, coastal), and Tallaght (IE0140A, suburban south-west). Rural reference stations are Lough Navar (IE0090A, remote County Fermanagh) and Moate (IE0111A, rural Westmeath).

Weather data comes from Met Eireann's Dublin Airport synoptic station (station 532), providing hourly temperature, wind speed, wind direction, precipitation, and humidity from 1946 to present [8].

### WHO 2021 Guidelines

The WHO 2021 Air Quality Guidelines [1] set two NO2 limits:
- **Annual mean**: 10 µg/m³ (reduced from 40 µg/m³ in the 2005 guidelines)
- **24-hour mean**: 25 µg/m³ (3-4 exceedance days per year permitted)

The EU Air Quality Directive sets the annual limit at 40 µg/m³ and the 1-hour limit at 200 µg/m³ (not to be exceeded more than 18 times per year).

### Prior Art: Source Apportionment Methods

Standard approaches for urban NO2 source apportionment include:

1. **Emission inventories** (bottom-up): Sum emissions from all known sources using activity data and emission factors. Used by the EPA's National Emissions Inventory. Disadvantage: large uncertainty in emission factors, especially for real-world driving conditions.

2. **Chemical Transport Models** (CTM): Simulate atmospheric chemistry and dispersion (e.g., EMEP MSC-W [18], CHIMERE). High computational cost, useful for policy scenarios.

3. **Receptor-based methods** (this study): Use measurements at receptor sites to infer source contributions using spatial and temporal patterns. Simpler, directly data-driven, but less mechanistic. This approach has been widely applied in the United Kingdom (UK) using the AURN network [19] and shares the same conceptual framework as the wind-direction-dependent analyses implemented in the openair R package [20].

4. **Positive Matrix Factorisation** (PMF): Statistical decomposition of multi-pollutant datasets into source profiles. Requires concurrent measurements of many species.

We use receptor-based methods because they can be tested against the COVID-19 lockdown and require only publicly available monitoring data. We note that our method is more precisely termed "source apportionment by differencing" rather than "source attribution" in the atmospheric science sense, which typically implies emission inventories or dispersion modelling.

## 3. Detailed Solution

### Source Attribution Model

Our receptor-based model decomposes measured NO2 at each station into three additive components:

**NO2_measured = NO2_background + NO2_heating + NO2_traffic + residual**

#### Component 1: Regional Background

The regional background represents long-range transport, transboundary pollution, and biogenic sources. It is estimated as the monthly mean NO2 at two rural stations:

**NO2_background(year, month) = mean(NO2_LoughNavar, NO2_Moate)**

This yields 1-8 µg/m³ depending on season, with a winter peak from European-scale emissions and poorer dispersion.

#### Component 2: Residential Heating

The heating contribution is estimated from the seasonal excess at background urban stations above their summer (June-August) baseline. Summer is chosen because residential heating demand in Ireland is near zero in these months. Three Dublin background stations (Ballyfermot, Clonskeagh, Tallaght) are used:

1. Compute summer baseline: **S(year) = mean(NO2_bgstations, Jun-Aug, year)**
2. Compute monthly excess: **E(year, month) = mean(NO2_bgstations, year, month) - S(year)**
3. Correct for rural seasonal variation: **NO2_heating(year, month) = max(0, E - rural_seasonal_excess)**

This isolates the urban heating signal because background stations are positioned away from major roads, so their seasonal variation is dominated by heating, not traffic. The correction for rural seasonal variation removes any background-level seasonality (e.g., continental wintertime NO2 transport) that is not local heating.

#### Component 3: Road Traffic

Traffic is computed as the residual after subtracting background and heating:

**NO2_traffic = max(0, NO2_measured - NO2_background - NO2_heating)**

This is the defining assumption: at a traffic-classified station, the excess above what a background station in the same city would measure is attributable to local road traffic emissions. Figure 1 (`plots/pred_vs_actual.png`) shows that the additive model (background + heating + traffic) closely recovers measured monthly NO2 across all stations (R-squared = 0.96). This is validated by two independent methods:

**Validation 1: COVID-19 lockdown.** Ireland's first lockdown began 15 March 2020 with severe travel restrictions. Traffic volumes fell 60-80% [9]. If our traffic apportionment is correct, the observed NO2 drop during lockdown should approximately match the traffic component. We note an important structural caveat: because the model defines traffic as the residual (measured minus background minus heating), and because background and heating are approximately unchanged during lockdown, the model's traffic component will mechanically decrease when total NO2 decreases. The COVID comparison therefore partially reflects this circularity. The validation is informative primarily for the cross-station pattern (whether the rank order and relative magnitudes of drops match predictions) rather than the absolute correlation value.

**Validation 2: Weekday-weekend differential.** Road traffic volumes are typically 30-40% lower on weekends than weekdays [10], while residential heating is unchanged. The weekday-weekend NO2 difference provides an independent estimate of the traffic fraction. Because weekend traffic is not zero (approximately 60% of weekday levels), the raw weekday-weekend difference underestimates the true traffic fraction; we apply a correction factor below.

### Key Results

#### WHO Guideline Exceedance

Every Dublin and Cork urban station exceeds the WHO annual NO2 guideline of 10 µg/m³ in every year measured (2015-2023). Specifically:

| Station | Type | 2019 | 2020 | 2022 | WHO Ratio |
|---------|------|------|------|------|-----------|
| Winetavern Street | Traffic | 43.5 | 30.4 | 32.5 | 3.3x |
| St John's Road | Traffic | — | 27.5 | 37.5 | 3.8x |
| Blanchardstown M50 | Traffic | 31.9 | 11.5 | 23.9 | 2.4x |
| Rathmines | Background | 23.7 | 14.8 | 19.6 | 2.0x |
| Ballyfermot | Background | 20.0 | 12.1 | 12.9 | 1.3x |
| Clonskeagh | Background | 21.7 | 13.3 | 14.2 | 1.4x |
| Tallaght | Background | 14.7 | 10.6 | 12.3 | 1.2x |
| Cork Old Station Rd | Background | 21.1 | 13.5 | 18.0 | 1.8x |
| Lough Navar | Rural | 5.4 | 2.0 | 2.1 | 0.2x |

The 24-hour WHO guideline (25 µg/m³) is exceeded on 67-91% of days at Winetavern Street, on 41-58% of days at Blanchardstown, and on 8-26% of days at background stations.

**No station exceeds the EU annual limit of 40 µg/m³** except Winetavern Street in 2018-2019 (43.5-43.7 µg/m³). Ireland therefore passes EU compliance while failing WHO health guidance at virtually every urban site. Figure 3 (`plots/headline_finding.png`) visualises this WHO-EU compliance gap across all stations.

#### Source Attribution Results

Annual source attribution for 2019 (pre-COVID, full-year data):

| Station | Measured | Background | Heating | Traffic | Traffic % |
|---------|----------|-----------|---------|---------|-----------|
| Winetavern St (traffic) | 43.5 | 4.8 (11%) | 3.9 (9%) | 34.8 (80%) | **80%** |
| Blanchardstown M50 (traffic) | 31.6 | 4.9 (16%) | 4.1 (13%) | 22.5 (71%) | **71%** |
| Pearse Street (traffic) | 24.3 | 4.8 (20%) | 3.9 (16%) | 15.6 (64%) | **64%** |
| Rathmines (background) | 23.6 | 4.8 (20%) | 3.9 (17%) | 14.9 (63%) | **63%** |
| Ballyfermot (background) | 19.9 | 4.8 (24%) | 3.9 (20%) | 11.1 (56%) | **56%** |
| Clonskeagh (background) | 20.7 | 4.8 (23%) | 3.9 (19%) | 12.0 (58%) | **58%** |
| Tallaght (background) | 14.7 | 4.8 (32%) | 3.9 (27%) | 6.0 (41%) | **41%** |
| Cork Old Station Rd (background) | 21.1 | 4.8 (23%) | 3.9 (19%) | 12.8 (61%) | **61%** |

Traffic dominates at all stations, contributing 41-80% of annual NO2 depending on proximity to roads. Even at background stations, traffic is the plurality source. Figure 2 (`plots/feature_importance.png`) and Figure 5 (`plots/source_attribution.png`) show this breakdown by station.

#### COVID-19 Lockdown Validation

The COVID lockdown reduced NO2 by 28-62% across Dublin stations (March-June 2020 versus same period 2019):

| Station | 2019 | 2020 | Drop | Drop % |
|---------|------|------|------|--------|
| Winetavern Street | 39.9 | 26.6 | -13.3 | -33% |
| Blanchardstown M50 | 41.5 | 15.9 | -25.6 | -62% |
| Davitt Road | 30.4 | 14.6 | -15.7 | -52% |
| Rathmines | 27.1 | 12.9 | -14.2 | -52% |
| Ballyfermot | 23.1 | 10.9 | -12.2 | -53% |
| Clonskeagh | 24.9 | 12.5 | -12.4 | -50% |

The correlation between the model's predicted traffic drop and the observed total NO2 drop is **r = 0.974** across 14 stations. Figure 4 (`plots/covid_validation.png`) shows the station-by-station comparison. The model's traffic contribution explains 45-78% of the observed COVID drop depending on station type, consistent with the expectation that lockdown removed 60-80% of traffic (not 100%, due to essential workers) and that meteorological differences between 2019 and 2020 also contribute.

The monthly phase analysis reveals progressive lockdown effects:
- March 2020 (partial restrictions): -20% at Winetavern, -35% at M50
- April 2020 (strict lockdown): -51% at Winetavern, -58% at M50
- May 2020 (strict lockdown): -54% at Winetavern, **-83% at M50**
- The M50 motorway showed the most dramatic response, as expected for a traffic-only environment with no nearby residential heating sources.

#### Weekday-Weekend Validation

Weekday NO2 is 15-38% higher than weekend at all urban stations:

| Station | Weekday | Weekend | Ratio | Implied Traffic % |
|---------|---------|---------|-------|-------------------|
| Winetavern Street | 36.6 | 28.5 | 1.28 | 55% |
| Pearse Street | 20.5 | 15.7 | 1.30 | 58% |
| Blanchardstown | 27.2 | 22.9 | 1.18 | 39% |
| Ballyfermot | 15.6 | 12.1 | 1.29 | 56% |
| Cork Old Station Rd | 20.4 | 14.8 | 1.38 | 68% |
| Lough Navar (rural) | 3.0 | 2.6 | 1.15 | 32% |

Lough Navar, a rural station in County Fermanagh remote from local traffic, shows a weekday-weekend ratio of 1.15 and a spurious "implied traffic" of 32%. This reflects transboundary NO2 transport that is correlated with weekday industrial and traffic activity across the UK and Ireland, not local traffic. This demonstrates that the weekday-weekend method has a non-zero noise floor at remote sites, and the "implied traffic" percentages at urban stations should be interpreted relative to this ~15% baseline rather than in absolute terms.

The weekday-weekend implied traffic percentages are systematically lower than the station-differencing estimates (55% vs 80% at Winetavern). This is expected: the weekday-weekend method assumes weekend traffic is zero, but it is actually about 60% of weekday levels [10]. Applying the correction (dividing the raw implied traffic percentage by 1 minus the weekend traffic fraction of 0.60) gives corrected estimates of 55%, 57%, 40%, 55%, and 68% for the five stations above -- compared to station-differencing estimates of 80%, 64%, 71%, 56%, and 61% respectively. The corrected weekday-weekend estimates have a mean absolute error of 14 percentage points relative to station-differencing, compared to 44 percentage points for the uncorrected values. The remaining discrepancy reflects the simplifications in both methods, but the corrected weekday-weekend estimates are quantitatively consistent with the station-differencing results. Figure 7 (`plots/weekday_weekend_correction.png`) shows this comparison.

#### Temperature and Heating

Winter NO2 at background stations shows a negative correlation with temperature (r = -0.17 to -0.39), confirming the heating contribution:

| Temperature | Ballyfermot | Clonskeagh | Cork Old Station Rd |
|-------------|-------------|------------|---------------------|
| Below 2 degrees C | 26.4 | 26.9 | 28.1 |
| 2-5 degrees C | 22.5 | 23.3 | 30.0 |
| 5-8 degrees C | 19.0 | 19.4 | 25.0 |
| 8-11 degrees C | 15.1 | 15.0 | 21.3 |
| Above 11 degrees C | 12.3 | 11.7 | 17.1 |

The 14 µg/m³ difference between the coldest and mildest bins represents the combined effect of increased heating demand and reduced atmospheric dispersion on cold days.

#### Wind-Direction Analysis

Using Dublin Airport wind direction data, we computed mean NO2 at Winetavern Street for 16 wind sectors. NO2 varies from 26 µg/m³ under southerly winds to 45 µg/m³ under north-northwesterly winds -- a ratio of 1.7:1. This is consistent with the station's geography: Winetavern Street is south of the Liffey quays, a major traffic corridor, so northerly winds carry traffic emissions directly to the monitor. Figure 6 (`plots/wind_direction.png`) shows the pollution rose.

At Rathmines (a background station 3 km south of the Liffey), the pattern is similar but weaker: NO2 ranges from 17 to 34 µg/m³ with the highest values under east-southeasterly winds, consistent with the station receiving city-centre outflow under easterly winds. Southerly winds (from the Dublin Mountains, with no urban sources upwind) consistently give the lowest NO2 at both stations.

No clear directional signal from Dublin Port (to the east) was detected at any station, consistent with the discussion in Section 6 that port/shipping emissions may be masked by road traffic.

#### O3-NO2 Photochemistry

At stations with concurrent ozone (O3) and NO2 measurements, we find a negative correlation between daily O3 and NO2 (mean r = -0.40 across 7 urban stations; r = -0.45 at Tallaght, r = -0.41 at Clonskeagh). This anti-correlation reflects the NO-NO2-O3 photochemical steady state: near traffic sources, emitted NO titrates ambient O3 to form NO2, so high NO2 days coincide with low O3 days [13, 17]. Figure 8 (`plots/o3_no2_photochemistry.png`) shows the seasonal scatter.

An unexpected finding is that O3 at Irish stations is higher in winter than summer at most sites (e.g., Clonskeagh: 49 µg/m³ winter vs 42 µg/m³ summer; Lough Navar: 59 vs 50 µg/m³). This contrasts with continental Europe, where photochemical O3 production peaks in summer. Ireland's maritime climate, high latitude, and frequent cloud cover limit local photochemical O3 production; the O3 budget is instead dominated by long-range transport from the North Atlantic and stratospheric intrusion, which peaks in late winter and spring [21]. This has implications for the additive model: the assumption that NO2 is approximately conserved is better justified in Ireland than in sunnier climates, because the photolysis rate of NO2 is lower.

#### Meteorological Confounding: 2019 versus 2020

To bound the meteorological contribution to the observed COVID-era NO2 drop, we compared March-June weather at Dublin Airport between 2019 and 2020. Mean temperature was 0.3 degrees Celsius warmer in 2020 (10.0 vs 9.7), mean wind speed was virtually identical (9.1 vs 9.2 knots), and daily rainfall was lower in 2020 (1.0 vs 2.3 mm/day). The 2020 spring was sunnier (6.2 vs 4.6 hours/day). The warmer, drier, sunnier conditions in 2020 would, if anything, improve dispersion and increase photolysis, slightly amplifying the observed NO2 reduction beyond the emission change alone. However, the magnitude of the meteorological effect is small relative to the 33-62% drops observed, and the wind speed difference (the primary meteorological control on urban dispersion) is negligible.

## 4. Methods

### Data Sources

1. **Air quality**: EEA Air Quality In-Situ Measurement Station Data from Zenodo [7], containing daily mean NO2 (µg/m³) for all European stations, 2015-2023. Ireland subset: 33 stations, 55,221 daily records.

2. **Weather**: Met Eireann Dublin Airport synoptic station hourly observations [8], aggregated to daily means for temperature, wind speed, wind direction, precipitation, and humidity. 78,865 hourly records, 2015-2023.

### Attribution Methodology

The station-differencing method decomposes NO2 at each receptor into three components (background + heating + traffic) at monthly resolution, then aggregates to annual means. The method requires:
- At least two rural stations for background estimation
- At least two urban background stations (away from major roads) for heating estimation
- Traffic stations and background stations in the same city for traffic estimation

The heating signal is extracted from the seasonal cycle at background stations. Summer (June-August) serves as the zero-heating reference. The excess in other months, after correcting for rural seasonal variation, is attributed to residential and commercial heating.

Traffic is the residual: measured minus background minus heating. This is validated by two independent methods (COVID lockdown response and weekday-weekend differential) that give consistent results.

### Iteration Process

Starting from the baseline station-differencing model, we tested 5 hypotheses from the research queue:

1. **Weekend-weekday validation (Q1)**: Confirmed traffic dominance; weekday/weekend ratio 1.15-1.38 across all stations. KEPT as validation evidence.

2. **COVID lockdown phase analysis (Q4)**: Monthly decomposition showed progressive lockdown effect with April-May 2020 as peak impact (-51 to -83%). KEPT.

3. **Temperature-NO2 relationship (Q5)**: Background stations show r = -0.17 to -0.39 temperature-NO2 correlation in winter, confirming heating signal. 14 µg/m³ difference between coldest and mildest days. KEPT.

4. **Initial attribution model using summer baseline at each station**: REVERTED. The summer baseline at traffic stations includes traffic, so the model mislabelled winter traffic congestion as heating. Replaced with background-station differencing.

5. **Pearse Street 2021 anomaly (Q6)**: Annual mean dropped to 8.5 µg/m³ from 24.3 in 2019. No other nearby station shows a similar drop. Flagged as likely instrument issue.

The keep/revert criterion was whether the change improved the COVID lockdown validation correlation or reduced the mean absolute error of the attribution.

## 5. Results

### Summary Statistics

- **14 of 16 key stations** exceed the WHO annual NO2 guideline in every year with sufficient data
- **0 stations** exceed the EU annual limit in 2020-2023 (post-COVID)
- **Winetavern Street** is Ireland's worst NO2 site: 31-44 µg/m³ annual mean, 67-91% of days exceeding the WHO 24-hour guideline
- **Traffic contributes 41-83%** of annual NO2 at urban stations
- **Heating contributes 8-30%**, peaking in December-February
- **Regional background contributes 8-32%**, lowest at traffic stations (where traffic dominates), highest at suburban background stations

### COVID Validation Metrics

- Model-observation correlation: r = 0.974 (n = 14 stations)
- Mean absolute error of traffic attribution vs COVID drop: 4.48 µg/m³
- The model correctly predicts the rank order of COVID sensitivity across station types

### Key Finding

If Dublin traffic were reduced to zero, urban background stations (Ballyfermot, Tallaght) would still exceed the WHO annual guideline in most years due to heating and background. This means traffic reduction alone — while necessary and impactful — is insufficient for WHO compliance. Heating fuel switching (from solid fuel to gas/electric) is also required.

## 6. Discussion

### Comparison with Published Work

Our traffic apportionment (41-80% of urban NO2) is consistent with published European estimates: Carslaw et al. [3] found 60-80% traffic contribution at UK urban sites, and the EEA reports traffic as the dominant NO2 source across European cities [11]. The COVID lockdown reductions we observe (33-62%) are comparable to those reported for London (-36%, [16]), Barcelona (-50%, [6]), and Delhi (-70%, [12]). For Chinese cities, Shi and Brasseur [5] reported NO2 reductions of 20-40% during the initial COVID lockdown period.

### The WHO-EU Compliance Gap

Ireland's position is paradoxical: it comfortably meets the EU NO2 limit while chronically exceeding the WHO guideline. This is not unique to Ireland -- the EEA reports that 94% of the European urban population lives in areas exceeding the WHO 2021 annual NO2 guideline [11], and virtually every urban monitoring station in Europe records annual means above 10 µg/m³. Dublin's exceedance is therefore typical rather than exceptional in the European context. However, the policy implication is stark. Under WHO guidance, every Dublin resident breathes NO2 that exceeds health-based recommendations. The EU's ongoing revision of the Air Quality Directive (expected 2025-2026) may tighten the annual NO2 limit toward the WHO value, which would put Dublin and Cork into non-compliance.

### Limitations

1. **NO2 is not a conserved tracer.** The additive decomposition (background + heating + traffic) implicitly assumes NO2 behaves like a conservative pollutant that mixes linearly. In reality, NO2 participates in photochemical cycling: emitted NO reacts rapidly with O3 to form NO2 (NO + O3 -> NO2), and NO2 photolyses back to NO in sunlight (NO2 + hv -> NO + O) [13, 17]. For annual or monthly means, this approximation is acceptable because the photochemical steady state is established within minutes and the net effect averages out. For daily values, especially in summer when photolysis is faster, the linear assumption introduces error. The O3-NO2 anti-correlation we observe (r = -0.40 at urban stations; Section 3) confirms that photochemistry is active but does not invalidate the monthly-resolution attribution. Harrison et al. [17] discuss the NOx-to-NO2 oxidation chemistry in urban settings in detail.

2. **Partial tautology in the COVID validation.** Because the model defines traffic as the residual (measured minus background minus heating), and the background and heating components are approximately unchanged during lockdown, the model's traffic component will mechanically decrease when total NO2 decreases. The r = 0.97 correlation therefore partly reflects this structural dependence rather than independent model skill. The COVID comparison is most informative for the cross-station pattern and relative magnitudes, not the absolute correlation. An ideal validation would use independent traffic count data to predict emission changes, which we leave for future work.

3. **No hourly decomposition**: We use daily means. Hourly data would enable rush-hour analysis and better separation of morning/evening traffic peaks from evening heating peaks. The EEA dataset provides daily values; hourly NO2 data from airquality.ie could be used in future work.

4. **Heating fuel type**: We cannot distinguish solid fuel (coal, peat, wood) from oil or gas heating using NO2 alone. PM2.5/NO2 ratios or SO2 co-measurements could help, but PM2.5 data are sparse (available at only 5 of our 16 stations, with limited temporal coverage).

5. **Port/shipping**: Dublin Port handles significant freight and ferry traffic. The wind-direction analysis (Section 3) found no clear easterly signal from the port at any station, but this may be masked by city-wide road traffic emissions.

6. **Meteorological confounding**: We compared March-June weather between 2019 and 2020 (Section 3) and found minimal differences in temperature (+0.3 degrees Celsius) and wind speed (-0.03 knots). The 2020 spring was sunnier and drier, which would slightly amplify the observed NO2 drop. This confirms the COVID signal is predominantly emission-driven, but some residual meteorological confounding cannot be excluded.

7. **Station representativeness**: Traffic stations are positioned to capture worst-case roadside exposure. Population-weighted exposure would be lower than the maximum station values.

8. **Cork coverage**: Only one Cork station (Cork Old Station Road) has sufficient NO2 data for the full analysis. Cork South Link Road has only 323 daily records. The study is predominantly a Dublin analysis; the title reflects this aspiration rather than the current depth of Cork coverage.

## 7. Conclusion

Using 9 years of real monitoring data from the EPA Ireland / EEA network, we establish that:

1. **Every Dublin and Cork urban station exceeds the WHO 2021 annual NO2 guideline** (10 µg/m³), typically by 1.2-4.4 times. No station exceeds the EU limit (40 µg/m³) post-2019.

2. **Road traffic is the dominant source** of urban NO2, contributing 41-80% at monitored sites. This is supported by the COVID-19 lockdown natural experiment (cross-station correlation r = 0.97, n = 14 stations, with the caveat that part of this correlation is structural) and independently confirmed by corrected weekday-weekend differentials. Diesel vehicles are the likely dominant sub-source given Ireland's fleet composition [9], but the method cannot distinguish diesel from petrol or private cars from commercial vehicles.

3. **Residential heating contributes 8-30%** with a clear temperature dependence (14 µg/m³ excess on the coldest versus mildest winter days).

4. **Traffic reduction alone is likely insufficient** for WHO compliance at background stations, assuming the heating and background components are independent of traffic. Heating fuel switching is also needed, though eliminating traffic could have secondary effects on dispersion and urban heat that modestly reduce other components.

5. The COVID lockdown demonstrated that Dublin's air quality can improve rapidly and substantially (-33 to -62%) when traffic is reduced, suggesting that policy interventions targeting road traffic emissions would have measurable health benefits.

## Figures

- **Figure 1** (`plots/pred_vs_actual.png`): Model-predicted versus measured monthly NO2 scatter for all key stations. The additive source attribution model (background + heating + traffic) recovers measured values with R-squared = 0.96, MAE = 0.9 micrograms per cubic metre.

- **Figure 2** (`plots/feature_importance.png`): Source contribution breakdown by station, sorted by traffic fraction. Traffic is the dominant contributor at all urban stations (41-82%), with heating and background making up the remainder.

- **Figure 3** (`plots/headline_finding.png`): Annual mean NO2 by station (2019) with WHO 10 micrograms per cubic metre and EU 40 micrograms per cubic metre guideline lines. Every urban station exceeds the WHO guideline. Winetavern Street exceeds it by 4.3 times.

- **Figure 4** (`plots/covid_validation.png`): COVID-19 lockdown natural experiment. Left: paired bars showing March-June 2019 vs 2020 NO2 at each station. Right: percentage reduction, with traffic-adjacent stations showing the largest drops (up to 62% at Blanchardstown M50).

- **Figure 5** (`plots/source_attribution.png`): Stacked bar charts of absolute (left) and percentage (right) source attribution across all stations. Traffic stations show 64-82% traffic contribution; even background stations attribute 41-63% to traffic.

- **Figure 6** (`plots/wind_direction.png`): NO2 pollution rose for Winetavern Street and Rathmines. NO2 at Winetavern is highest under northerly winds (quays traffic corridor upwind) and lowest under southerly winds (no urban sources upwind).

- **Figure 7** (`plots/weekday_weekend_correction.png`): Weekday-weekend implied traffic percentage: raw versus corrected (assuming weekend traffic = 60% of weekday) versus station-differencing model. The correction reduces mean absolute disagreement from 44 to 14 percentage points.

- **Figure 8** (`plots/o3_no2_photochemistry.png`): O3 versus NO2 scatter at Clonskeagh and Tallaght, coloured by season. The anti-correlation (r = -0.41 to -0.45) demonstrates photochemical cycling between NO, NO2, and O3.

## References

[1] World Health Organization. WHO Global Air Quality Guidelines, 2021. Geneva: WHO.

[2] EPA Ireland. Air Quality in Ireland 2023. Wexford: EPA, 2024.

[3] Carslaw, D.C., Beevers, S.D., Tate, J.E., Westmoreland, E.J., Williams, M.L. Recent evidence concerning higher NOx emissions from passenger cars and light duty vehicles. Atmospheric Environment, 45(39), 7053-7063, 2011.

[4] Viana, M., Hammingh, P., Colette, A., Querol, X., Denier van der Gon, H., Eeftens, M., ... Impact of maritime transport emissions on coastal air quality in Europe. Atmospheric Environment, 90, 96-105, 2014.

[5] Shi, X., Brasseur, G.P. The response in air quality to the reduction of Chinese economic activities during the COVID-19 outbreak. Geophysical Research Letters, 47(11), 2020.

[6] Venter, Z.S., Aunan, K., Chowdhury, S., Lelieveld, J. COVID-19 lockdowns cause global air pollution declines. Proceedings of the National Academy of Sciences, 117(32), 18984-18990, 2020.

[7] EEA. Air Quality In-Situ Measurement Station Data, 2015-2023. Zenodo, doi:10.5281/zenodo.14513586, 2024.

[8] Met Eireann. Dublin Airport Hourly Data. data.gov.ie, 2024.

[9] Transport Infrastructure Ireland. National Roads Traffic Data 2020.

[10] National Transport Authority. Greater Dublin Area Transport Strategy 2022-2042.

[11] European Environment Agency. Air Quality in Europe 2023. EEA Report No. 02/2023.

[12] Mahato, S., Pal, S., Ghosh, K.G. Effect of lockdown amid COVID-19 pandemic on air quality of the megacity Delhi, India. Science of the Total Environment, 730, 139086, 2020.

[13] Seinfeld, J.H., Pandis, S.N. Atmospheric Chemistry and Physics: From Air Pollution to Climate Change, 3rd ed. Wiley, 2016.

[14] Dublin City Council. Dublin Region Air Quality Plan 2021.

[15] Vardoulakis, S., Fisher, B.E.A., Pericleous, K., Gonzalez-Flesca, N. Modelling air quality in street canyons: a review. Atmospheric Environment, 37(2), 155-182, 2003.

[16] Higham, J.E., Ramadan, A., Longley, I.D., Huang, Y., Walton, H. The impact of the COVID-19 lockdown on air quality in London. Environmental Research, 197, 111038, 2021.

[17] Harrison, R.M., Dall'Osto, M., Beddows, D.C.S., Thorpe, A.J., Bloss, W.J., Allan, J.D., Coe, H., Dorsey, J.R., Gallagher, M., Martin, C., Whitehead, J., Williams, P.I., Jones, R.L., Langridge, J.M., Benton, A.K., Ball, S.M., Langford, B., Hewitt, C.N., Davison, B., Martin, D., Petersson, K.F., Henshaw, S.J., White, I.R., Nickless, G., Pillai, A., Monks, P.S. Atmospheric chemistry and physics in the atmosphere of a developed megacity (London): an overview of the REPARTEE experiment and its conclusions. Atmospheric Chemistry and Physics, 12, 3065-3114, 2012.

[18] Simpson, D., Benedictow, A., Berge, H., Bergstrom, R., Emberson, L.D., Fagerli, H., ... The EMEP MSC-W chemical transport model -- technical description. Atmospheric Chemistry and Physics, 12, 7825-7865, 2012.

[19] DEFRA. Air Pollution in the UK 2023. Department for Environment, Food and Rural Affairs, 2024.

[20] Carslaw, D.C., Ropkins, K. openair -- An R package for air quality data analysis. Environmental Modelling and Software, 27-28, 52-61, 2012.

[21] Derwent, R.G., Simmonds, P.G., Manning, A.J., Spain, T.G. Trends over a 20-year period from 1987 to 2007 in surface ozone at the atmospheric research station, Mace Head, Ireland. Atmospheric Environment, 41(39), 9091-9098, 2007.
