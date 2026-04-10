# Observations — Dublin/Cork NO2 Source Attribution

## Data Quality
- EEA Zenodo dataset is excellent: 9 years (2015-2023), daily resolution, 33 Irish stations with NO2
- Coverage varies by station: some have gaps (Pearse St 2021 shows anomalously low 8.5 µg/m³ — possible instrument issue)
- Met Eireann Dublin Airport hourly weather data is very complete for the study period
- Daily data coverage indicators (cov.day.NO2) show >90% coverage for most station-years

## Surprising Findings
1. **Winetavern Street is 3-4x the WHO guideline every single year** — this is a traffic-dominated site that would be in violation under any jurisdiction applying WHO guidelines
2. **Even background stations exceed WHO** — Ballyfermot, Tallaght are residential/suburban but still 10-20 µg/m³
3. **COVID lockdown dropped rural NO2 by 56%** at Lough Navar — this suggests transboundary transport is significant even in remote locations
4. **No station exceeds the EU limit (40 µg/m³)** — the EU limit is 4x the WHO guideline, explaining why Ireland "complies" with EU law while health impacts persist
5. **Wind direction signal is counterintuitive** — NW/W winds (not NE, where the port is) give highest NO2 at Winetavern, suggesting city-generated emissions trapped under western weather patterns

## Data Gaps
- No hourly NO2 data used yet (only daily) — hourly would enable rush-hour peak analysis
- No traffic count data downloaded — would strengthen traffic attribution
- No fuel sales data — would help quantify heating contribution
- No shipping AIS data — would help separate port emissions
- Cork has very limited station coverage (only 2 stations with NO2, one only has 2022)

## Signal Ideas
- Use diurnal pattern (morning/evening rush hours) to further decompose traffic vs heating
- Use weekend/weekday ratio as independent traffic validator
- Compare Dublin Port wind-direction signal with Dun Laoghaire (coastal, no port)
- Use PM2.5/NO2 ratio to distinguish diesel (high NO2/PM2.5) from solid fuel (low NO2/PM2.5)
