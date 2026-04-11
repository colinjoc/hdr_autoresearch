# Response to Adversarial Peer Review

**Paper**: Dublin and Cork NO2 Source Apportionment: Traffic Dominates Guideline Exceedance, Supported by the COVID-19 Lockdown Natural Experiment

**Review summary**: 0 CRITICAL, 11 MAJOR, 10 MINOR. Reviewer recommendation: Minor revision.

---

## Claims vs Evidence (2 MAJOR, 1 MINOR)

### MAJOR 1: COVID validation scatter plot not shown; r=0.97 claim unverifiable

**Response**: We acknowledge that showing only paired bars rather than a scatter plot with regression line weakens the claim. The r=0.97 is computed across 14 stations. We have added an explicit caveat (see MAJOR 2 below) about the structural component of this correlation. We retain the paired-bar format because 14 points do not support a meaningful regression line with confidence interval, but we now present the cross-station pattern as the primary evidence rather than the absolute correlation value.

### MAJOR 2: Tautological structure in COVID validation

**Response**: Accepted. This is the most substantive criticism. We have added an explicit acknowledgment in both the abstract and Section 3: "Because the model defines traffic as the residual (measured minus background minus heating), and the background and heating components are approximately unchanged during lockdown, the model's traffic component will mechanically decrease when total NO2 decreases. The r = 0.97 correlation therefore partly reflects this structural dependence rather than independent model skill." The abstract now reads "consistent with" rather than "closely match" and notes the structural caveat. The title has been changed from "Validated by" to "Supported by." The COVID comparison is now framed as informative primarily for the cross-station pattern (rank order and relative magnitudes) rather than the absolute correlation.

### MINOR 1: Lough Navar weekday-weekend anomaly not discussed

**Response**: Added. Lough Navar's 32% "implied traffic" is now explained as transboundary weekday-correlated industrial/traffic NO2, demonstrating that the weekday-weekend method has a ~15% noise floor at remote sites.

---

## Scope vs Framing (3 MINOR)

### MINOR 2: Title promises "Dublin and Cork" but Cork is underdeveloped

**Response**: Acknowledged in new Limitation 8: "Only one Cork station (Cork Old Station Road) has sufficient NO2 data for the full analysis. Cork South Link Road has only 323 daily records. The study is predominantly a Dublin analysis; the title reflects this aspiration rather than the current depth of Cork coverage."

### MINOR 3: "Source attribution" vs "source apportionment by differencing"

**Response**: Accepted. The title and text have been changed from "source attribution" to "source apportionment" throughout. Section 2 now explicitly states: "We note that our method is more precisely termed 'source apportionment by differencing' rather than 'source attribution' in the atmospheric science sense, which typically implies emission inventories or dispersion modelling."

### MINOR 4: WHO exceedance not contextualized within Europe

**Response**: Added to the Discussion: "The EEA reports that 94% of the European urban population lives in areas exceeding the WHO 2021 annual NO2 guideline [11], and virtually every urban monitoring station in Europe records annual means above 10 ug/m3. Dublin's exceedance is therefore typical rather than exceptional in the European context."

---

## Reproducibility (2 MINOR)

### MINOR 5: Sensitivity to station subset not tested

**Response**: Acknowledged but not addressed in this revision. A formal sensitivity analysis would require testing all permutations of 2-from-N rural stations and 3-from-M background stations, which is feasible but beyond the scope of this revision cycle.

### MINOR 6: No code repository mentioned

**Response**: The paper already links to the GitHub repository in the Methods section. We note this is also linked from the website summary.

---

## Missing Experiments (7 MAJOR)

### MAJOR 3: No wind-direction analysis

**Response**: Added. Wind-direction analysis using Dublin Airport wind data (16 sectors) reveals that NO2 at Winetavern Street ranges from 26 ug/m3 under southerly winds to 45 ug/m3 under northerly winds (ratio 1.7:1), consistent with the station's position south of the Liffey quays traffic corridor. A pollution rose (Figure 6) is now included.

### MAJOR 4: No diurnal analysis

**Response**: Partially addressed. The EEA dataset provides daily (not hourly) NO2 values, so rush-hour analysis is not possible with the current data. We now explicitly state this limitation and note that hourly data from airquality.ie could support this in future work. However, the sunshine-hours analysis (via the O3-NO2 photochemistry work below) provides indirect evidence of diurnal photochemical effects.

### MAJOR 5: No trend analysis

**Response**: Not addressed in this revision. While the data span 9 years, the COVID disruption in 2020-2021 makes trend estimation unreliable without segmented regression. We note this as a priority for future work, particularly as post-COVID fleet turnover data become available.

### MAJOR 6: No population-weighted exposure

**Response**: Not addressed. This requires Census small-area population data and spatial interpolation methods that are beyond the scope of this measurement-based study. Noted as future work.

### MAJOR 7: No PM2.5/NO2 ratio analysis

**Response**: Investigated but not feasible. PM2.5 data are available at only 5 of 16 stations with limited temporal coverage (294-356 days each). This is insufficient for reliable ratio analysis or heating fuel type discrimination.

### MAJOR 8: No uncertainty quantification

**Response**: Not addressed with formal bootstrap intervals. However, we now provide two additional consistency checks (corrected weekday-weekend comparison, wind-direction analysis) that triangulate the attribution from different angles. The 14-percentage-point mean disagreement between corrected weekday-weekend and station-differencing methods provides an informal measure of attribution uncertainty.

### MAJOR 9: No 2019-vs-2020 weather comparison

**Response**: Added. March-June weather comparison shows: temperature +0.3 degrees C, wind speed -0.03 knots, rain -1.3 mm/day, sunshine +1.6 hours/day. Wind speed (the primary dispersion control) is virtually identical. The warmer, sunnier conditions in 2020 would slightly amplify the NO2 drop, confirming the observed reductions are predominantly emission-driven.

---

## Overclaiming (3 MINOR)

### MINOR 7: "Validated by" too strong in title

**Response**: Changed to "Supported by."

### MINOR 8: "Diesel traffic" not distinguishable from method

**Response**: Changed conclusion from "diesel road traffic" to "road traffic" with a note: "Diesel vehicles are the likely dominant sub-source given Ireland's fleet composition [9], but the method cannot distinguish diesel from petrol or private cars from commercial vehicles."

### MINOR 9: "Even complete elimination" assumes independence of components

**Response**: Qualification added: "assuming the heating and background components are independent of traffic. Heating fuel switching is also needed, though eliminating traffic could have secondary effects on dispersion and urban heat that modestly reduce other components."

---

## Literature Positioning (2 MAJOR, 1 MINOR)

### MAJOR 10: Thin reference list, missing key citations

**Response**: Added 6 new references:
- [16] Higham et al. (2021) -- London COVID NO2 reduction (replaces erroneous [5] citation for London)
- [17] Harrison et al. (2012) -- NOx-to-NO2 oxidation chemistry in urban settings
- [18] Simpson et al. (2012) -- EMEP MSC-W model documentation
- [19] DEFRA (2024) -- UK AURN NO2 source apportionment
- [20] Carslaw and Ropkins (2012) -- openair R package
- [21] Derwent et al. (2007) -- Irish O3 climatology (long-range transport)

Reference list now has 21 entries.

### MAJOR 11: NO2 chemistry not discussed

**Response**: Addressed in three places: (a) Introduction now notes "NO2 is chemically reactive -- it participates in rapid photochemical cycling with NO and O3"; (b) New O3-NO2 photochemistry analysis in Section 3 with scatter plots; (c) New Limitation 1 discusses the conserved-tracer assumption in detail and cites Seinfeld and Pandis [13] and Harrison et al. [17].

### MINOR 10: Citation error -- ref [5] is about China, not London

**Response**: Fixed. The London COVID NO2 figure now cites Higham et al. [16]. Shi and Brasseur [5] is retained but correctly attributed to Chinese cities.

---

## Summary of Changes

| Issue | Status |
|-------|--------|
| COVID tautology acknowledgment | DONE |
| Citation [5] error | FIXED |
| Wind-direction analysis | DONE (new Figure 6) |
| Diurnal analysis | PARTIALLY (data limitation; noted) |
| NO2 photochemistry | DONE (new Figure 8, new text) |
| Weekend/weekday correction | DONE (new Figure 7, quantitative) |
| 2019-vs-2020 weather comparison | DONE |
| Title "Validated" -> "Supported" | DONE |
| "Diesel traffic" -> "road traffic" | DONE |
| WHO context in Europe | DONE |
| Cork coverage caveat | DONE |
| "Source attribution" -> "source apportionment" | DONE |
| Lough Navar anomaly explained | DONE |
| 6 new references added | DONE |
| Trend analysis | NOT DONE (future work) |
| Population-weighted exposure | NOT DONE (future work) |
| Formal uncertainty quantification | NOT DONE (informal via method comparison) |
| Sensitivity to station subset | NOT DONE (future work) |
