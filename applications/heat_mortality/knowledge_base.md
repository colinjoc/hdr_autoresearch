# Knowledge Base: Heat-Mortality Prediction

Paper ID references point to `papers.csv` in this directory.

## 1. Wet-bulb temperature: definitions and computation

### 1.1 Definitions

- **Psychrometric (adiabatic) wet-bulb temperature T_w**: the temperature an air parcel reaches if cooled adiabatically to saturation at constant pressure by evaporating water into it. This is the value a well-ventilated wet-bulb thermometer measures in shade. It is the most widely used "wet-bulb" in the human-tolerance literature.
- **Thermodynamic wet-bulb temperature T_w,thermo**: the temperature to which a volume of air would cool if water were evaporated into it until saturation under strictly thermodynamic reversibility. Differs from psychrometric by <~0.1 K under typical surface conditions and is usually treated as equivalent in climate applications [43, 216].
- **Natural wet-bulb temperature T_nw**: the temperature of a wetted thermometer exposed to ambient wind and radiation rather than actively ventilated. T_nw is always ≥ T_w under sun and low wind; it feeds into the WBGT calculation [49].
- **Wet-bulb globe temperature (WBGT)**: ISO 7243 occupational heat stress index, a weighted combination of T_nw, globe temperature T_g, and dry-bulb T_a. Not the same as T_w.
- **Dew-point temperature T_d**: the temperature at which, if air were cooled isobarically without changing water vapour content, it would reach saturation. Related to T_w via the wet-bulb depression T − T_w vs the dew-point depression T − T_d.

### 1.2 Davies-Jones 2008 algorithm [43]

Given dry-bulb T (K), pressure p (hPa), and mixing ratio r or specific humidity q, compute equivalent potential temperature θ_E via Bolton (1980):

    θ_E ≈ T · (1000/p)^(0.2854 (1 − 0.28 r_s)) · exp( r_s (1 + 0.81 r_s) · (3376/T_L − 2.54) )

where T_L is the lifting condensation level temperature and r_s is the saturation mixing ratio at T. The wet-bulb temperature T_w is then obtained by inverting θ_E along the saturated pseudoadiabat at pressure p using a Newton iteration with an initial guess good to ~0.34 K for θ_w ≤ 40 C. One iteration reduces the relative error below 0.002 K over the normal meteorological range (Davies-Jones 2008; see PyTw and WetBulb GitHub implementations for ported code).

### 1.3 Stull 2011 approximation [44]

For fast calculation at sea-level pressure with dry-bulb T (C) and relative humidity RH (percent), valid 5% ≤ RH ≤ 99%, −20 C ≤ T ≤ 50 C:

    T_w = T · atan(0.151977 · (RH + 8.313659)^0.5)
        + atan(T + RH)
        − atan(RH − 1.676331)
        + 0.00391838 · RH^1.5 · atan(0.023101 · RH)
        − 4.686035

T_w in C. Mean absolute error < 0.3 K; worst-case error −1 to +0.65 K. Not valid at high altitude or under extreme cold.

### 1.4 Buzan-Huber HumanIndexMod [45]

The HumanIndexMod in CLM4.5 implements 13 heat stress quantities, including T_w (Davies-Jones method), simplified WBGT (sWBGT), Heat Index, Apparent Temperature, Humidex, Discomfort Index, and others. It exposes each metric for each time step and land grid cell. It is the reference implementation for physically consistent wet-bulb calculation in a climate-model setting.

### 1.5 WBGT computation (Liljegren 2008 [49])

Outdoor WBGT (ISO 7243):

    WBGT_out = 0.7 · T_nw + 0.2 · T_g + 0.1 · T_a

where T_a is dry-bulb air temperature, T_nw is natural wet-bulb temperature (natural ventilation), and T_g is globe temperature (black globe radiant temperature). Indoor or no-sun WBGT drops the globe term and weights T_nw 0.7 and T_a 0.3.

Liljegren et al. 2008 solve T_nw and T_g from standard meteorological inputs (T_a, RH, wind speed, solar zenith angle, direct beam solar flux, diffuse solar flux, cloud cover or surface pressure) via iterative mass and energy balance. The algorithm has RMSE < 1 C against direct field measurements. It is the NWS reference and is available as the pywbgt Python package and in PyWBGT. Approximations (e.g. Bernard's model or sWBGT) can differ by several degrees under high sun and low wind and therefore understate extreme-heat occupational exposure [50].

### 1.6 Typical value ranges

- Sea-level T_w never exceeds ~31 C in most historical records; values approaching 35 C are rare (but have been observed in Persian Gulf stations [22, 171] and the 2024 Mecca Hajj [201, 202]).
- WBGT occupational limits per ACGIH: 28 C for heavy work, 30 C for moderate work, 31.5 C for light work (acclimatised).
- UTCI categories: < 9 C no thermal stress; 26–32 C moderate heat stress; 32–38 C strong heat stress; 38–46 C very strong; > 46 C extreme.
- PET categories: 18–23 C comfortable; 23–29 C slight heat stress; 29–35 C moderate; 35–41 C strong; > 41 C extreme.

## 2. Heat-exposure metrics summary table

| Metric | Inputs | Output unit | Primary use | Reference |
|---|---|---|---|---|
| Dry-bulb T_a | T_a | C | Baseline meteorology | — |
| Wet-bulb T_w | T, RH (or q), p | C | Human survivability ceiling | [18, 22, 43, 44] |
| Dew point T_d | T, RH | C | Humidity comfort, dewpoint forecasts | — |
| Heat Index (Steadman/NWS) | T, RH | C (apparent) | US public alerts | [46, 48] |
| Apparent Temperature | T, T_d, wind | C | Australia/NWS | [47] |
| Humidex (Canada) | T, T_d | C | Canadian public alerts | — |
| Simplified WBGT (sWBGT) | T, RH | C | Quick estimate | [45, 50] |
| Full WBGT (Liljegren) | T, RH, wind, solar, p | C | ISO 7243 occupational | [49] |
| UTCI | T, T_d, wind, radiation | C | European biometeo | [51, 133] |
| PET | T, T_d, wind, radiation, clothing, metabolic rate | C | Urban planning | [52] |
| Universal climate index categories | UTCI C | 10 stress classes | Operational warnings | [51, 134] |

Lo et al. 2023 [53]: across 604 locations in 39 countries, no single metric is optimal. Dry-bulb or weakly humidity-modified metrics win ~40% of countries; apparent temperature wins another ~40%. The optimal metric is location- and climate-specific, which implies that a metric-agnostic HDR model should test several and select per-city.

## 3. Excess mortality methodology

### 3.1 P-score (Karlinsky-Kobak [60])

    P_t = (D_t − E_t) / E_t

where D_t is observed weekly deaths and E_t is expected deaths under a baseline model. The baseline E_t is typically a Poisson or negative-binomial regression on week-of-year fixed effects plus a long-term trend term, fit to a pre-crisis training period (e.g. 2015–2019). Linear extrapolation of the pre-crisis trend into the evaluation period is the Karlinsky-Kobak convention.

### 3.2 Alternative baseline estimators

- **WHO baseline** [61]: spline-on-trend with country-specific seasonality, Bayesian hierarchical pooling for countries with sparse data.
- **Acosta-Irizarry** [158]: uses a Gaussian process or fPCA-based seasonality plus a flexible trend.
- **Nepomuceno et al.** [63]: P-score aggregated to age-standardised all-cause mortality.
- **Gasparrini et al.** [120] case time-series: converts the design to a case–crossover-style within-subject (within-area) comparison, absorbing all time-invariant confounders.

### 3.3 Age standardisation

    ASMR = sum_k  (D_k / N_k) · w_k

where D_k is deaths in age stratum k, N_k the stratum population, and w_k the weight from a reference population (e.g. ESP2013 European Standard Population or WHO World Standard). Excess mortality at the all-age level is sensitive to population ageing; for HDR the age-standardised rate comparison is preferred when age structure drifts across the evaluation window.

### 3.4 Time-series Poisson regression for heat

Standard model (Bhaskaran et al. [68], Gasparrini et al. [3, 6]):

    D_t ~ Poisson(μ_t)
    log μ_t = α + ns(time, df·years) + DOW_t + cb(temp_{t, t-L}) + β·X_t

where ns(time) is a natural cubic spline with 7–10 df per year capturing season and long-term trend, DOW is day-of-week fixed effects, cb(temp) is the DLNM cross-basis over current and lagged temperature up to lag L (typically 21 days for heat+cold, 3–5 for heat-only), and X_t includes covariates like PM2.5 and public holidays. The cross-basis cb() is the outer product of a smooth basis in the temperature dimension (typically natural spline with 2–4 interior knots) and a smooth basis in the lag dimension (typically natural spline with log-spaced knots).

### 3.5 Two-stage meta-analysis (MCC Network [3, 6, 32, 127, 193])

Stage 1: fit a city-specific DLNM and extract a reduced city-specific exposure-response curve (overall cumulative over lags).

Stage 2: pool these curves across cities using multivariate meta-regression (mvmeta R package), with city-level moderators (climate, GDP, AC prevalence, population age structure, PM2.5) as meta-regressors. This is how MCC publishes heat-mortality results consistently across 1,150+ locations in 53 countries.

## 4. The 35 C wet-bulb threshold revision in plain English

- **Sherwood-Huber 2010** [18]: proposed T_w = 35 C as a theoretical upper limit, reasoning from physics that humans cannot dissipate metabolic heat when ambient wet-bulb exceeds ~35 C (because skin temperature is regulated near 35 C). They emphasised it was a theoretical ceiling, but the literature treated it as a de facto survivability threshold.
- **Vecellio et al. 2022 PSU HEAT** [19]: the first empirical test on 24 young healthy adults (18–34) walking at ~3 metabolic equivalents (METs), in climate-controlled chambers across humid (36–40 C, variable RH) and hot-dry (38–50 C, low RH) combinations. They measured the critical environmental limit (T_w,crit) at which core temperature could no longer be held steady, i.e., heat storage became positive. The mean critical T_w in warm-humid environments was 30.55 ± 0.98 C — approximately 4.5 C below the Sherwood-Huber theoretical ceiling. In hotter, drier environments T_w,crit fell further (i.e., the equivalent T_w was even lower because radiation and low humidity shifted the balance).
- **Wolf et al. 2023** [20]: extended to older adults, showing even lower critical limits consistent with age-related thermoregulatory decline, and showing that activity level matters — older sedentary adults have different critical limits than older active ones.
- **Vanos et al. 2023 PNAS** [21]: reworked global exposure arithmetic under ~31 C T_w threshold and showed several-fold higher "dangerous humid heat" exposure than under the 35 C ceiling.
- **Matthews et al. 2023** [25]: confirmed the pattern at station and gridded scale.
- **Wolf et al. 2025** [27]: additional validation.

**Plain-English summary**: the wet-bulb temperature at which heat stress becomes uncompensable for a *young healthy exercising* adult is around 30–31 C in humid air, not 35 C. For an *older adult* it is lower. For a *sedentary young adult* it may be slightly higher. For population-level forecasting this means that (a) the 35 C Sherwood-Huber ceiling is not an operationally useful alert threshold and (b) exposure metrics based on T_w should be interpreted with population- and activity-specific critical values, not a single global number.

**What this means for HHWS design**: T_w ≥ 30 C sustained over multiple daytime hours, or T_w_min (night-time minimum wet-bulb) failing to drop below some local recovery threshold, is closer to the empirically measured physiological danger zone than T_w ≥ 35 C.

## 5. Compound day–night heat: formal definitions

### 5.1 Concurrent hot day and hot night (Mukherjee-Mishra [29])

A "concurrent hot day and hot night" event is one on which both:

- Daily maximum temperature Tmax(t) ≥ 90th percentile of local climatology, AND
- Daily minimum temperature Tmin(t) ≥ 90th percentile of local climatology.

Multi-day events are defined by consecutive days meeting the criterion. The 1-day, 3-day, and 5-day versions are standard.

### 5.2 Compound day-night heatwave (Tang et al. [31], Lee et al. [32], Yin et al. [33])

Daytime-only heatwave: Tmax ≥ Q95(Tmax, local calendar-day climatology) on ≥ 2 consecutive days.
Nighttime-only heatwave: Tmin ≥ Q95(Tmin, local calendar-day climatology) on ≥ 2 consecutive days.
Compound day-night heatwave: both criteria met simultaneously on ≥ 2 consecutive days.

The literature uses percentiles computed on a 15-day moving window centred on each calendar day to avoid early-summer / late-summer artefacts.

### 5.3 WMO/EuroHEAT criterion [95]

EuroHEAT defines a heat wave as a period of at least 2 consecutive days during which both Tmax and Tmin exceed city-specific 90th-percentile climatological thresholds, integrated over the May–September warm season. This is effectively a compound day–night criterion, though it is not always interpreted that way operationally.

### 5.4 UK Heat-Health Alert thresholds

Tmax and Tmin region-specific thresholds; levels 1–4; level 3 ("Heatwave action") triggers on thresholds met for at least 2 consecutive days and an intervening night. Tmin component is explicit.

### 5.5 NWS HeatRisk [106]

A 0–4 scale computed from forecast temperature percentiles relative to local daily climatology, blended with CDC heat-health guidance. Does not explicitly use a wet-bulb or minimum-T_w criterion. This is precisely the operational gap the HDR research question targets.

## 6. Glossary

- **All-cause mortality**: every death regardless of stated cause; the preferred outcome for heat-mortality epidemiology because heat-related deaths are under-coded.
- **Apparent temperature**: Steadman's temperature index approximating what the weather "feels like".
- **Case-crossover design**: a within-person design comparing exposure on a case day with exposure on nearby control days.
- **Case time-series design**: Gasparrini 2022 [120] extension applying DLNM cross-basis within a within-unit (area or person) framework.
- **Cross-basis**: the bi-dimensional smooth basis over the exposure dimension and the lag dimension used in DLNM.
- **DLNM**: distributed lag non-linear model (Gasparrini-Armstrong) [1, 2, 4].
- **DLNM reduced curve**: the exposure-response function at cumulative lag, obtained by integrating the cross-basis along the lag dimension.
- **Excess mortality**: observed minus expected deaths, where expected is estimated from a pre-crisis baseline.
- **Harvesting / mortality displacement**: the phenomenon where deaths during an acute exposure are partly forward-displacement of deaths that would have occurred within days anyway.
- **HHWS / HHAP**: heat-health warning system / heat-health action plan.
- **Heat Index (HI)**: Steadman's US formula relating T and RH to apparent temperature.
- **Humidex**: Canadian metric similar to HI, uses T and dew point.
- **MMT**: minimum mortality temperature, the daily temperature at which the U-shaped mortality curve is lowest.
- **MCC Network**: Multi-Country Multi-City Collaborative Research Network, curated by LSHTM.
- **MoMo**: Spanish mortality monitoring system [152].
- **EuroMOMO**: European mortality monitoring network across 24 countries [154, 155].
- **NDVI**: normalised difference vegetation index, used as a proxy for urban greenness.
- **P-score**: (observed − expected) / expected mortality.
- **PET**: physiological equivalent temperature [52].
- **Q95**: 95th percentile.
- **Relative humidity (RH)**: ratio of vapour pressure to saturation vapour pressure at current T.
- **Specific humidity (q)**: mass of water vapour per mass of moist air.
- **Tmax / Tmin**: daily maximum / minimum air temperature.
- **T_w**: wet-bulb temperature.
- **T_w,crit**: the critical wet-bulb temperature above which heat storage in a working human becomes positive under given metabolic and environmental conditions (PSU HEAT) [19, 20].
- **UHI**: urban heat island, the tendency of urban cores to be warmer than surrounding rural areas, especially at night.
- **UTCI**: Universal Thermal Climate Index [51].
- **WBGT**: wet-bulb globe temperature [49].

## 7. Vulnerability factors (≥14 from the consensus literature)

1. Age 65+ (strongest risk factor) [9, 37, 90, 100, 209]
2. Age 75+ (even stronger) [9, 91]
3. Pre-existing cardiovascular disease [9, 92, 94]
4. Pre-existing respiratory disease [9, 92]
5. Renal disease (dehydration risk amplifier) [94, 228]
6. Psychiatric illness and psychotropic medication [94, 227]
7. Anticholinergic medication [227]
8. Diuretic medication [227]
9. Social isolation / living alone [71, 196, 229]
10. Low-income, low-education SES [74, 78, 122, 210]
11. Ethnic minority status (as proxy for structural AC and housing disparities) [73, 210]
12. No working AC [71, 75, 76, 212]
13. Top-floor apartment [71, 211]
14. Poorly insulated / single-glazed housing [211]
15. Homelessness / unsheltered [129]
16. Outdoor occupation in hot climate [130, 131, 132]
17. Bed confinement / inability to self-care [71, 100]
18. Obesity (BMI > 30) or very low BMI [164, 204]
19. Recent migration to hot climate / unacclimatised [7, 124]
20. Pregnancy [128, 191, 192]

## 8. Standard rules of thumb

- **Marginal temperature-mortality slope**: a 1 C increase above the local 95th percentile of mean daily temperature increases all-cause daily mortality by approximately 1–4%, with substantial city-level variation [6, 8, 9]. The largest slopes are in temperate-climate cities with low adaptation and low AC penetration; the smallest are in warm-climate cities with high AC (e.g., Phoenix).
- **Heat wave additional effect**: heat-wave days carry a mortality excess beyond the single-day temperature effect, of the order of 2–5% extra at population level, attributed to cumulative exposure / compound day-night / harvesting interaction [10, 93].
- **Night-time minimum additional effect**: a 1 C increase in night-time T above the local climatological 80th percentile increases next-day mortality by ~2–4% in southern Europe and London data [28, 35].
- **AC protective effect**: going from 20% to 80% household AC prevalence is associated with an ~80% reduction in hot-day mortality based on long-run US county panels (Barreca et al. [76]).
- **UHI contribution**: 4–5% of summer mortality in European cities is attributable to the urban heat island [85, 86]; in extreme-event summers (e.g. 2022 London) the UHI share can reach ~38% of heat-wave deaths [84].
- **Minimum mortality temperature**: MMT is typically 75–85th percentile of local temperature distribution [6, 124]. This is higher than the climatological mean because the U-shape is asymmetric.
- **Adaptation**: US heat-mortality risk fell ~63% from 1987 to 2005 [11]; MMT rises roughly 0.5–1 C per 1 C of climate warming in some locations but much less in others [125, 126].
- **Climate attribution fraction**: ~37% of warm-season heat-related deaths globally are attributable to anthropogenic warming over 1991–2018 [12]; ~54% of 2023 global excess heat deaths are attributable [39]; ~167% increase in 65+ heat deaths vs the 1990s is higher than the 65% that would be expected from temperature rise alone [37].
- **Heat wave return period**: heat-mortality return periods have shrunk from 1-in-100 years in the 2000 climate to 1-in-10 to 1-in-20 years in the 2020 climate [29, 233], and continue to shorten with warming.

## 9. Failure modes of current heat early-warning systems

1. **Trigger-temperature only**: most systems alert on Tmax and a local percentile; a heat wave with unremarkable Tmax but high T_w, high Tmin, and long duration may not trigger [96, 101, 161].
2. **Ignoring night-time minimum**: HeatRisk and many systems use daily climatology on Tmax rather than a separate Tmin criterion [106]. This misses compound day-night events that drive the super-linear mortality response [31, 32, 33].
3. **Short-lead forecasts only**: operational alerts are usually 1–3 day; public-health response (cooling centre staffing, outreach to isolated elderly) needs 5–10 day lead times [95, 97].
4. **Single threshold not slope-aware**: binary alerts lose information that cities with steep heat-mortality slopes would benefit from at lower trigger values, and those with shallow slopes could tolerate higher ones [7, 193].
5. **No vulnerable-population targeting**: population-average thresholds under-protect elderly / isolated / low-income residents [71, 94, 228].
6. **Poor handling of unusual-season events**: early-season heat (June, before acclimatization) produces more mortality per degree than late-season heat, but most systems use fixed rather than season-adjusted thresholds [127].
7. **No AC-access adjustment**: cities with low AC penetration are under-warned relative to their vulnerability [75, 76].
8. **No compound-exposure memory**: multi-day events produce cumulative risk that single-day trigger systems treat as independent [4, 32].
9. **Verification on average metrics**: HHWS evaluations often use RMSE or MAE on summer daily mortality, which misses tail-event performance [140, 142, 198].

## 10. Standard data ranges for major datasets

| Dataset | Coverage | Spatial resolution | Temporal resolution | Variables relevant to heat-mortality | Reference |
|---|---|---|---|---|---|
| ERA5 (reanalysis) | 1940–present | ~31 km global | Hourly | T_2m, T_d, q, p, wind, radiation | [54] |
| ERA5-Land | 1950–present | ~9 km global land | Hourly | T_2m, q, LST | [56] |
| ERA5-HEAT | 1940–present | ~31 km global | Hourly | UTCI, MRT | [55] |
| HadISDH.land | 1973–present | 5 deg grid | Monthly | q, RH, T_d, T_w, e | [57] |
| HadISDH.extremes | 1973–present | 5 deg grid | Monthly | T_w extremes indices (TwX90p etc.) | [58, 59] |
| HadCRUT5 | 1850–present | 5 deg grid | Monthly | T anomaly | [165] |
| CDC Wonder / NCHS Multiple Cause of Death | 1999–present | County, census tract | Weekly / monthly / annual | ICD-10 cause-coded deaths | — |
| Eurostat weekly deaths (demo_r_mweek3) | 2000–present | NUTS-3 region | Weekly | All-cause death counts by age and sex | [155] |
| EuroMOMO | 2008–present | 24 countries | Weekly | All-cause excess mortality | [154, 155] |
| MoMo Spain | 2004–present | Province | Daily/weekly | All-cause excess mortality | [151, 152] |
| MCC database | 1985–present (varies) | 1,150+ cities, 53 countries | Daily | All-cause mortality, weather | [6, 32] |
| World Mortality Dataset | 2015–present | 103+ countries | Weekly/monthly | All-cause | [60] |
| NWS HeatRisk operational | 2020–present | US 2.5 km | Daily forecast to 7 days | Heat-risk category 0–4 | [106, 107] |
| ISD (Integrated Surface Database) | 1901–present | Station | Hourly | T, RH, p, wind | — |

### 10.1 CDC Wonder suppression rules (important for HDR)

CDC Wonder multiple cause of death suppresses cell counts < 10 deaths and sub-national rates based on fewer than 20 deaths. This means that county-level daily counts cannot be retrieved; the practical resolution for US mortality is weekly state-level or monthly county-level. This forces the HDR unit of analysis to be at least city-week, not city-day.

### 10.2 Eurostat weekly deaths ranges

Eurostat `demo_r_mweek3` provides weekly deaths by NUTS-3 region, five-year age group, and sex from 2000 onwards. Not every country reports at NUTS-3 level every week; some report at NUTS-2. The "excess" calculation is usually done against a 2015–2019 baseline. For the HDR, this provides 800+ regions × 25 years × 52 weeks ≈ 10^6 observations.

### 10.3 ERA5 pitfalls for heat-mortality

- ERA5 T_2m is 2 metre air temperature over a 31 km grid cell. It under-represents urban heat island effects; ERA5 temperature should be corrected with a local UHI offset or supplemented with station data [84, 86].
- Heatwave maxima in ERA5 tend to be slightly underestimated relative to station Tmax due to grid-box averaging. The ERA5-HEAT product [55] addresses this for UTCI but not for all metrics.
- T_w calculated from ERA5 q and p via Davies-Jones is robust; Stull approximation is also fine at ERA5 sea-level grid cells but less accurate at altitude.
- Hourly output is necessary for computing daily maximum T_w and minimum T_w, not just mean values.

## 11. Summary of the physical-mortality chain

Atmospheric forcing (T, RH, wind, radiation) → exposure metric (T_w, HI, WBGT, UTCI, compound day-night criteria) → physiological strain (heat storage, dehydration, sleep disruption, cardiovascular load) → vulnerability moderation (age, comorbidity, AC, housing, isolation) → observable outcome (all-cause mortality, cause-specific mortality, ED visits, hospital admissions).

The HDR loop hypothesis is that adding compound day-night wet-bulb exposure metrics to the exposure step materially improves the prediction of the outcome step beyond what current heat-health early-warning systems achieve using dry-bulb Tmax-based metrics.
