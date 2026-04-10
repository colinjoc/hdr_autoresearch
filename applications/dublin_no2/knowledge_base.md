# Knowledge Base — Dublin/Cork NO2 Source Attribution

## Established Facts

1. **Dublin NO2 exceeds WHO 2021 guidelines at all urban stations.** The WHO annual guideline of 10 ug/m3 is exceeded at every Dublin station except possibly background sites. Pearse Street averages ~32 ug/m3 — 3.2x the WHO guideline. However, all stations are below the current EU limit of 40 ug/m3.

2. **The EU 2030 limit of 20 ug/m3 will be binding.** Under the revised EU Air Quality Directive, the annual NO2 limit drops to 20 ug/m3 by 2030. Dublin traffic stations (Pearse St ~32, Winetavern ~28, Cork ~25) will all exceed this limit without intervention. The EPA's 2024 report projects Ireland at only 78% compliance.

3. **Traffic is the dominant NO2 source at kerbside stations.** COVID lockdown reduced NO2 by 25% at traffic stations (Pearse St, Winetavern) with 34% reduction during rush hours. Weekend reduction was only 20%, confirming the weekday commuter traffic component. Background stations showed no reduction — confirming the traffic signal is real.

4. **Station identity explains most of the prediction variance.** Adding station fixed effects improved holdout MAE from 7.36 to 2.20 ug/m3 (70% reduction). This confirms that station-level factors (proximity to traffic, building canyon effects, local emission sources) dominate over hour-to-hour meteorological variation.

5. **Heating season increases NO2 by ~28% at all stations.** The heating/non-heating ratio is 1.28 for both Dublin and Cork. This is separate from meteorological effects (lower BLH in winter) — the heating proxy captures combustion from residential solid fuel.

6. **Wind and boundary layer height control dispersion.** Wind speed and BLH proxy account for 12% of feature importance. Low-wind, low-BLH conditions (temperature inversions) trap NO2 near the surface. This is why the worst episodes occur on cold, calm winter nights.

7. **The year-over-year declining trend is real but slow.** Pearse Street declined from 34.0 (2019) to 31.1 (2025) ug/m3, roughly -0.5 ug/m3/year. This reflects gradual fleet electrification and tighter Euro emission standards. At this rate, Pearse Street will still exceed the EU 2030 limit in 2030.

8. **Bus electrification alone is insufficient.** Counterfactual analysis: electrifying all Dublin Bus vehicles reduces Pearse Street by ~3.2 ug/m3 (10%). This helps but leaves Pearse Street at ~29 ug/m3, still well above both WHO (10) and EU 2030 (20) limits.

9. **Dublin Port shipping has minimal impact on city-centre NO2.** Port emissions primarily affect Ringsend (within 1km) where cold-ironing would reduce NO2 by ~2.2 ug/m3. Impact on city-centre stations is negligible — wind direction and distance dilute the signal.

10. **The smoky-coal ban addressed PM2.5 but not NO2.** The nationwide extension of the smoky-coal ban in September 2022 targeted particulate matter. Smokeless coal, peat, and wood still emit NOx when burned. The heating contribution to NO2 is through combustion NOx, not through coal smoke specifically.

## Key Findings from HDR Loop

- XGBoost slightly outperforms LightGBM, ExtraTrees, and Ridge on this dataset
- Station fixed effects are by far the most important single feature group
- Tree-based models automatically learn the interactions that explicit feature engineering targets (wind direction x source, rush hour x weekday, temperature x heating), making most manual interaction features redundant
- The weekday rush hour signal is the clearest traffic signature and the one feature that trees do not fully capture from base features alone
- The COVID lockdown natural experiment validates the source attribution: traffic stations responded proportionally to the traffic reduction

## Open Questions

- Exact diesel car vs petrol car vs bus vs truck decomposition within the traffic fraction (requires fleet-specific data or number-plate recognition)
- Dublin Port shipping contribution on specific wind patterns (requires AIS berth data)
- Building canyon amplification at Pearse Street vs College Green
- Effect of BusConnects route changes on NO2 redistribution across the city
- Seasonal variation in port activity (cruise ship season May-October)
