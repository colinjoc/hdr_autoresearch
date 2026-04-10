# Research Queue — Dublin/Cork NO2 Source Attribution

## OPEN

### HIGH IMPACT

**Q1**: Does using the weekend/weekday NO2 ratio as an independent traffic proxy agree with the station-differencing method?
- **Prior**: 70% — weekday/weekend patterns are well-established in literature
- **Mechanism**: Weekdays have ~30% more traffic than weekends; heating is constant. The weekday excess at each station is an independent estimate of the traffic fraction.
- **Source**: Domain knowledge; EEA station classification guidelines
- **Impact**: HIGH — independent validation of the main finding

**Q2**: Does the PM2.5/NO2 ratio distinguish diesel traffic from solid fuel heating?
- **Prior**: 60% — diesel NO2/PM2.5 is high (~5-10), solid fuel is low (~1-2)
- **Mechanism**: Diesel engines produce high NOx relative to PM. Solid fuel (peat, coal, wood) produces high PM relative to NOx. The ratio should shift seasonally and between station types.
- **Source**: Carslaw et al. (2011) atmospheric composition; EPA Air Quality in Ireland reports
- **Impact**: HIGH — would add a chemical fingerprint to the attribution

**Q3**: Can we detect the Dublin Port shipping signal using wind-direction-conditional analysis at Tolka Quay (IE076) vs Dun Laoghaire?
- **Prior**: 40% — port emissions are diffuse and Tolka Quay data may not cover study period
- **Mechanism**: When winds blow from the port (NE at city centre), NO2 should be elevated at nearby stations. Compare with Dun Laoghaire which has no port.
- **Source**: Viana et al. (2014) port emission impacts; Dublin Port Company reports
- **Impact**: HIGH — answers whether port/shipping is a significant separate source

**Q4**: Does the COVID lockdown response differ between phases (strict lockdown Mar-May vs partial reopening May-Jun)?
- **Prior**: 75% — well-established in other cities (London, Barcelona, Delhi)
- **Mechanism**: Traffic returned gradually; heating didn't change. Monthly decomposition of the lockdown period should show progressive traffic recovery.
- **Source**: Venter et al. (2020) Nature; Shi & Brasseur (2020)
- **Impact**: HIGH — strengthens the traffic attribution validation

**Q5**: Does adding temperature as a predictor improve the heating attribution (cold days = more heating)?
- **Prior**: 65% — temperature is a direct driver of heating demand
- **Mechanism**: On cold days, more heating is used, producing more NO2. The temperature-NO2 correlation at background stations should be negative (colder = more NO2) and stronger in winter.
- **Source**: Met Eireann data; degree-day heating models
- **Impact**: HIGH — moves from crude monthly to daily-resolution heating estimate

### MEDIUM IMPACT

**Q6**: Does the Pearse Street 2021 anomaly (8.5 µg/m³ annual) reflect real conditions or instrument failure?
- **Prior**: 30% real, 70% instrument — the drop from 24 to 8.5 in one year is extreme
- **Mechanism**: If instrument failure, other nearby stations (Winetavern, Clonskeagh) should not show a similar drop in 2021.
- **Source**: EEA data quality flags; EPA annual reports
- **Impact**: MEDIUM — affects data quality for one station-year

**Q7**: Does using EU hourly NO2 data (4 GB download) enable rush-hour peak analysis that refines the traffic attribution?
- **Prior**: 60% — hourly data captures diurnal cycle
- **Mechanism**: Traffic peaks at 7-9am and 5-7pm. Heating peaks at 6-9pm and 7-9am. The distinct timing should separate the two.
- **Source**: Standard transport engineering; SUMO traffic models
- **Impact**: MEDIUM — significant effort (4GB download) for incremental improvement

**Q8**: Is the heating signal stronger in areas with high solid fuel usage (west Dublin) vs areas with gas heating (south Dublin)?
- **Prior**: 55% — depends on data availability for heating fuel type by area
- **Mechanism**: Solid fuel (coal, peat, turf) produces much more NO2 per unit heat than gas. Areas with smoky coal bans may show lower heating-attributed NO2.
- **Source**: EPA smoky coal ban reports; CSO census heating fuel data
- **Impact**: MEDIUM — would refine the heating attribution by fuel type

**Q9**: Does the long-term trend (2015-2023) show improvement from fleet electrification or policy changes?
- **Prior**: 50% — some improvement expected but fleet turnover is slow
- **Mechanism**: Increasing EV share, Euro 6 fleet penetration, and smoky coal ban expansion should reduce traffic and heating NO2 over time.
- **Source**: SIMI vehicle registration data; EPA annual reports
- **Impact**: MEDIUM — adds a trend dimension to the story

**Q10**: Does the wind speed affect the traffic-background differential (lower wind = worse dispersion = higher traffic signal)?
- **Prior**: 65% — well-established in boundary layer meteorology
- **Mechanism**: Low wind speed means poor ventilation, trapping emissions near the surface. The traffic increment should be larger on calm days.
- **Source**: Seinfeld & Pandis (2016) textbook; Vardoulakis et al. (2003)
- **Impact**: MEDIUM — adds a meteorological dimension

### LOW IMPACT

**Q11**: Does including O3 (anti-correlated with NO2 via photochemistry) improve source separation?
- **Prior**: 45% — O3-NO2 titration is well-known but complex
- **Mechanism**: Near traffic, fresh NO reacts with O3 to form NO2. Higher O3 depletion = closer to traffic source. Background stations should have higher O3.
- **Source**: Seinfeld & Pandis (2016); Clapp & Jenkin (2001)
- **Impact**: LOW — adds complexity for modest improvement

**Q12**: Does the analysis change if we use median instead of mean for annual statistics?
- **Prior**: 35% — means and medians usually agree for NO2
- **Mechanism**: If the distribution is heavily skewed (e.g., episodic high pollution events), median may be more representative.
- **Source**: Statistics; WHO guideline methodology
- **Impact**: LOW — robustness check

## RESOLVED

## RETIRED
