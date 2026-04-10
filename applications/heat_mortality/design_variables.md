# Design Variables — Heat-Mortality HDR

Structured catalogue of features that the HDR loop can manipulate. Each entry
lists type, units, range, provenance in `data_loaders.py`, mechanistic
justification (citing paper IDs from `papers.csv`), whether the variable is a
Phase B discovery lever, and implementation gotchas.

Paper ID citations are in `[n]` or `[n, m]` format and point to `papers.csv`.

Unit of analysis throughout: one row per `(city, iso_week_start)`. The city is
from `data_loaders.CITIES`; the week key is an ISO-8601 Monday.

## Legend

- **Type**: `continuous` (real-valued), `count` (non-negative integer),
  `categorical` (finite labels), `binary` (0/1), `date`, `cyclic`
  (encodable as sin/cos pair).
- **Phase B dimension** `yes`: should be exposed as a lever in the HDR
  discovery sweep (Phase B composition/optimisation). `no`: fixed by data
  pipeline; `loader-only`: may be swapped at the loader level but not at the
  model level.
- **Baseline / Phase 2 / Phase B columns** in the summary table (§13):
  - *baseline*: Phase 0.5 feature set
    (`tmax_c_mean`, `tmin_c_mean`, `tavg_c`).
  - *Phase 2*: single-change candidate features (flagship theme is
    night-time wet-bulb, §3).
  - *Phase B*: candidate discovery lever in the composition sweep.

---

## 1. Atmospheric primary variables

These are the raw meteorological inputs the loaders expose. They are the
substrate on which all derived exposure metrics are built.

### t2m_c
- **Type**: continuous
- **Units**: degrees Celsius
- **Range / typical values**: −30 to +50 C at hourly resolution; weekly mean
  typically −5 to +35 C across the 30-city panel.
- **Source**: `data_loaders.load_isd_city_hourly` → `t2m_c` column (parsed
  from ISD TMP); also `data_loaders.load_era5_city` → `t2m_c` (from ERA5
  `2m_temperature`, converted from K to C); also
  `data_loaders.load_ghcnd_city_daily` → `tmax_c`, `tmin_c`, `tavg_c`
  (GHCN-Daily TMAX/TMIN/TAVG in tenths of C).
- **Mechanism**: dry-bulb 2 m air temperature is the universally available
  exposure variable. Temperature–mortality curves are U-shaped with
  minimum-mortality temperature (MMT) near the 75–85th percentile of local
  climatology [6, 124]. A 1 C increase above the local 95th percentile raises
  all-cause daily mortality by ~1–4% [6, 8, 9]. This is the substrate of
  every subsequent exposure metric.
- **Phase B dimension**: no (always included; never turned off)
- **Notes**: ISD stores tenths of C with `9999` sentinel; `_parse_isd_tenths`
  handles this. ERA5 is in Kelvin; loader subtracts 273.15. GHCN-D stores
  tenths of C; loader divides by 10.

### tmax_c_mean
- **Type**: continuous
- **Units**: degrees Celsius
- **Range / typical values**: weekly mean of daily max, typically −5 to
  +42 C. Phoenix July ~42; Paris August 2003 ~40.
- **Source**: `data_loaders.aggregate_hourly_to_weekly` (daily max of
  `t2m_c`, then weekly mean) or `aggregate_daily_to_weekly` (from GHCN-D
  `tmax_c`).
- **Mechanism**: daily maximum temperature is the workhorse trigger of
  nearly every operational HHWS [95, 96, 101, 106]. It correlates with heat
  stroke, ED visits, and same-day cardiovascular mortality [9, 10, 90, 95].
- **Phase B dimension**: no (baseline lock)
- **Notes**: a weekly *mean* of daily max is smoother than `max-of-week` and
  is the Phase 0.5 baseline feature. Phase 2 can test the max-of-week
  variant.

### tmin_c_mean
- **Type**: continuous
- **Units**: degrees Celsius
- **Range / typical values**: weekly mean of daily min, typically −10 to
  +28 C. Tropical nights (≥20 C) in Mediterranean August are routine;
  Phoenix 2023 W30 saw Tmin ≥ 30 C for multiple days.
- **Source**: `data_loaders.aggregate_hourly_to_weekly` and
  `aggregate_daily_to_weekly`.
- **Mechanism**: overnight recovery is a physiological requirement;
  elevated Tmin prevents resetting of core body temperature between hot
  days [28, 34, 35, 121, 169]. A 1 C increase in Tmin above the local 80th
  percentile is associated with ~2–4% next-day mortality increase in
  southern Europe and London [28, 35]. Hot nights are the focus of the
  compound day–night hypothesis [31, 32, 33].
- **Phase B dimension**: no (baseline lock); but Phase 2 tests alternative
  summaries (max-of-week, consecutive-nights-above-threshold).
- **Notes**: Tmin from ISD hourly is real; Tmin from GHCN-D is the
  observation-day min, which is slightly different.

### tavg_c
- **Type**: continuous
- **Units**: degrees Celsius
- **Range / typical values**: weekly mean of hourly or daily means,
  typically −5 to +33 C.
- **Source**: `aggregate_hourly_to_weekly` (`t2m_c.mean`) and
  `aggregate_daily_to_weekly` (GHCN `tavg_c` or the midpoint of
  `tmax_c`/`tmin_c` as a fallback).
- **Mechanism**: the ensemble mean of daily mean temperatures is what DLNM
  papers most commonly use on the exposure axis [3, 6, 124]. It is the
  standard summary of heat load and is the least noisy temperature aggregate.
- **Phase B dimension**: no
- **Notes**: beware of mixing ISD-hourly-derived `tavg` (24-h mean) with
  GHCN-D-derived `tavg` (often `(tmax+tmin)/2`); the two differ by ~0.5 K
  typically.

### td2m_c
- **Type**: continuous
- **Units**: degrees Celsius (dew point)
- **Range / typical values**: −25 to +27 C; rarely >28 C at sea level
  historical records, though Persian Gulf values approach 30+ C [22, 171].
- **Source**: `load_isd_city_hourly` (parsed from ISD DEW), `load_era5_city`
  (from `2m_dewpoint_temperature`, K→C), `load_ghcnd_city_daily` (GHCN-D
  ADPT; US stations only).
- **Mechanism**: dew point is the direct measurement of atmospheric
  moisture content, and together with air temperature it determines all
  human-health humidity metrics (wet-bulb, heat index, UTCI, WBGT)
  [22, 43, 44, 46, 49, 51]. When dry-bulb alone is used, the humidity
  signal that distinguishes "survivable" from "uncompensable" heat is
  thrown away [18, 19, 20, 21, 25].
- **Phase B dimension**: yes (can be replaced by relative humidity, by
  specific humidity, or suppressed as an ablation).
- **Notes**: ISD DEW often has more quality-controlled entries than US
  GHCN-D ADPT. Td > T is physically impossible; loader clips RH to ≤100%.
  European cities have NO dew-point data in GHCN-D — the ISD path is the
  only no-auth route [data_acquisition_notes].

### rh_pct
- **Type**: continuous
- **Units**: percent (0–100)
- **Range / typical values**: 5–100%; summer daytime in temperate cities
  40–70%, Mediterranean desert 10–30%, tropical coastal 70–95%.
- **Source**: derived inside `compute_wet_bulb` via the Alduchov–Eskridge
  Magnus formula: `RH = 100 · e^(a·Td/(b+Td)) / e^(a·T/(b+T))` with
  `a=17.625, b=243.04`. Can be exposed as its own column by the user.
- **Mechanism**: relative humidity is the input to Stull [44] and to
  simplified heat-index / sWBGT formulations [45, 46]. Its role is to
  scale the latent-heat sink available to evaporative cooling, which
  dominates human heat regulation at T ≳ 30 C.
- **Phase B dimension**: yes (interchangeable with dew point and specific
  humidity as the humidity lever).
- **Notes**: RH can saturate (≈100%) during cold fog but the loader
  treats >99% as out-of-Stull-domain and masks Tw to NaN.

### sp_hpa / msl_hpa
- **Type**: continuous
- **Units**: hectopascals
- **Range / typical values**: sp 850–1040 hPa (low at altitude); msl
  980–1040 hPa.
- **Source**: `load_era5_city` only (`surface_pressure`, `mean_sea_level_pressure`).
  Not exposed by ISD or GHCN-D paths currently.
- **Mechanism**: pressure enters the Davies-Jones [43] wet-bulb via
  mixing-ratio / equivalent potential temperature, not the Stull [44]
  approximation. Matters most at altitude (e.g. Denver 1600 m, Madrid
  650 m) where sea-level assumption introduces a systematic bias.
  Also indirectly useful as a heat-dome detector: 500 hPa anomaly is the
  canonical heat-dome signature [15, 16, 42, 219, 220] but surface
  pressure correlates.
- **Phase B dimension**: loader-only (needed if Davies-Jones swap-in is
  tested; otherwise unused in Phase 0.5).
- **Notes**: only available via ERA5, so Phase 2 tests that require
  Davies-Jones Tw are blocked until the CDS account is live.

### wind_ms
- **Type**: continuous
- **Units**: metres per second
- **Range / typical values**: 0–20 m/s; calm nights → stagnation → UHI
  intensification.
- **Source**: ISD has a wind field but loader does not currently parse it.
  ERA5 has `10m_u_component_of_wind` and `10m_v_component_of_wind`. This
  is a Phase 1 loader extension.
- **Mechanism**: wind affects natural wet-bulb (T_nw) and globe
  temperature via forced convection, and therefore WBGT via Liljegren
  [49, 50]. Low-wind calm nights amplify urban heat-island effect and
  reduce overnight recovery [85, 86, 172, 235]. UTCI also uses 10 m wind
  [51, 133].
- **Phase B dimension**: loader-only (Phase 1 addition)
- **Notes**: not in Phase 0.5 loaders. Listed for completeness and to
  reserve a Phase B slot.

### ssrd_wm2
- **Type**: continuous
- **Units**: W m⁻² (surface solar radiation downwards, daily mean)
- **Range / typical values**: 0 at night; 200–1000 W m⁻² daytime; weekly
  means ~100–350 W m⁻².
- **Source**: ERA5 `surface_solar_radiation_downwards`. Not currently
  loaded (Phase 1).
- **Mechanism**: solar radiation enters WBGT via globe temperature [49,
  50]; PET [52] and UTCI [51, 133] both require radiation. High-solar
  days with moderate air temperature can still produce dangerous WBGT
  for outdoor workers [130, 131, 132].
- **Phase B dimension**: loader-only
- **Notes**: ERA5-HEAT [55] pre-computes UTCI using ERA5 radiation fields
  and can be pulled as a derived drop-in instead of recomputing.

---

## 2. Atmospheric derived: humid-heat composite metrics

Composite exposure metrics that combine T with humidity, wind, and/or
radiation. The HDR hypothesis is that at least one of these outperforms raw
dry-bulb T on high-mortality weeks.

### tw_c (Stull 2011)
- **Type**: continuous
- **Units**: degrees Celsius (wet-bulb temperature)
- **Range / typical values**: −15 to +31 C at sea level historically; >31 C
  is rare outside the Persian Gulf and 2024 Mecca [22, 171, 201, 202].
- **Source**: `data_loaders.compute_wet_bulb(t2m_c, td2m_c)` — Stull 2011
  arctan fit. Masked to NaN outside (T ∈ [−20, 50], RH ∈ [5, 99]).
  Populated hourly in `load_isd_city_hourly` and `load_era5_city`, daily
  in `aggregate_daily_to_weekly` (from `tavg_c` + `adpt_c`).
- **Mechanism**: wet-bulb temperature is the canonical human-tolerance
  metric [18, 21, 22, 25]. It integrates latent-heat and sensible-heat
  sinks into one number. The Sherwood-Huber 35 C [18] theoretical ceiling
  has been revised down to ~30.55 C empirically for humid conditions in
  young healthy adults [19, 20, 27, 207, 208]; older adults have even
  lower critical values [209]. This is the flagship exposure metric of
  the HDR hypothesis.
- **Phase B dimension**: yes (core lever; alternatives are Davies-Jones,
  HI, UTCI, WBGT).
- **Notes**: Stull has MAE < 0.3 C vs Davies-Jones [43] in the
  meteorological domain. The loader masks out-of-domain to NaN rather
  than returning extrapolated answers.

### tw_c_mean
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: weekly mean of daily mean wet-bulb, −10 to
  +28 C.
- **Source**: `aggregate_hourly_to_weekly` (daily mean of hourly
  `tw_c`, then weekly mean).
- **Mechanism**: weekly-average wet-bulb is the simplest wet-bulb feature
  and is a direct substitute for `tavg_c` in a DLNM. Lo et al. 2023 [53]
  showed that humid-heat metrics including Tw win in some climates but
  not all.
- **Phase B dimension**: yes
- **Notes**: less responsive to extreme days than `tw_c_max`.

### tw_c_max
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: weekly max of daily max Tw, −5 to +32 C.
- **Source**: `aggregate_hourly_to_weekly` (daily max of hourly `tw_c`,
  then weekly max).
- **Mechanism**: peak wet-bulb is the closest operational surrogate to
  the PSU HEAT critical-limit framework [19, 20, 209]. A week with
  `tw_c_max ≥ 30` is approaching the empirical danger threshold even if
  the dry-bulb max is unexceptional [21, 25, 170].
- **Phase B dimension**: yes
- **Notes**: this is the closest Phase 0.5 feature to the HDR hypothesis
  signal.

### heat_index_c (NWS Steadman polynomial)
- **Type**: continuous
- **Units**: degrees C (apparent temperature)
- **Range / typical values**: equal to T below ~27 C; above that, HI
  ≥ T increasing with RH.
- **Source**: not currently in loaders; derived candidate from `t2m_c`
  and `rh_pct` via the NWS polynomial (Rothfusz regression, a Steadman
  fit [46, 47, 48]).
- **Mechanism**: Heat Index is the US operational heat metric, used by
  NWS HeatRisk [106] and by the CDC heat-health messaging. It is a
  sedentary-shaded-adult proxy and under-weights wet-bulb in extreme
  humidity [48, 53].
- **Phase B dimension**: yes (candidate composite metric)
- **Notes**: implementable in ~10 lines; add as a Phase 2 single-add.

### apparent_temp_c (Steadman wind-inclusive)
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: ±5 C around T depending on wind.
- **Source**: not in Phase 0.5 loaders; needs wind.
- **Mechanism**: Steadman Part II [47] adds wind and radiation to the HI
  calculation. Australian BoM and NWS use forms of apparent T for heat
  and wind-chill together. Lo et al. 2023 [53] found apparent T was
  locally optimal in ~40% of 39 countries.
- **Phase B dimension**: yes
- **Notes**: requires wind parser — Phase 1 loader addition.

### humidex_c (Canadian)
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: 25–50 C in warm humid conditions.
- **Source**: not in Phase 0.5 loaders; derived from `t2m_c` and `td2m_c`
  via the Masterton–Richardson formula.
- **Mechanism**: Humidex is Canada's public heat alert metric, uses T and
  Td directly. Closely related to HI but different algebra.
- **Phase B dimension**: yes
- **Notes**: cheap addition — Phase 2 single-add candidate.

### swbgt_c (simplified WBGT)
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: 15–34 C.
- **Source**: not in Phase 0.5 loaders; derived from T and RH via
  `sWBGT = 0.567·T + 0.393·e + 3.94` where `e` is water-vapour pressure.
- **Mechanism**: sWBGT is the humidity-modified-T approximation of full
  WBGT used in ISO 7243 occupational heat-stress guidance when
  radiation and wind are unknown [45, 50]. Kong-Huber [50] warned that
  sWBGT under-estimates extreme exposure by several degrees.
- **Phase B dimension**: yes
- **Notes**: the cheapest WBGT surrogate. Phase 2 add.

### wbgt_full_c (Liljegren 2008)
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: 15–34 C outdoor.
- **Source**: not in Phase 0.5 loaders; requires wind, solar radiation,
  zenith angle, pressure, cloud cover. `pywbgt` Python package
  implements [49]. Available from ERA5 inputs; Brimicombe 2022 [136]
  pre-computed a global gridded product.
- **Mechanism**: full WBGT is the ISO 7243 occupational exposure
  standard, RMSE < 1 C against field measurements [49]. Kong-Huber
  2022 [50] showed it is materially more accurate than sWBGT for
  labour-productivity assessments in extreme heat.
- **Phase B dimension**: yes (requires ERA5)
- **Notes**: Phase 1 addition; gated on CDS account.

### utci_c (ERA5-HEAT)
- **Type**: continuous
- **Units**: degrees C (UTCI equivalent temperature)
- **Range / typical values**: −40 to +50 C; heat categories 26–32
  moderate, 32–38 strong, 38–46 very strong, >46 extreme [51, 133].
- **Source**: `load_era5_city` could be extended to pull ERA5-HEAT [55]
  UTCI directly.
- **Mechanism**: UTCI is derived from a multi-node Fiala thermoregulation
  model [51, 133]; Pappenberger 2015 [134] showed good forecast skill.
  It is the canonical European bioclimatology metric.
- **Phase B dimension**: yes (ERA5-HEAT pull)
- **Notes**: Phase 1 addition.

### pet_c (Physiological Equivalent Temperature)
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: 18–23 comfortable, 29–35 moderate stress,
  >41 extreme [52].
- **Source**: not in loaders; needs full MEMI input set.
- **Mechanism**: used in urban climate and urban planning literature
  [52, 77, 78, 81]. Less common in mortality time-series than UTCI but
  appears in neighbourhood-level vulnerability studies.
- **Phase B dimension**: no (too many inputs to be practical Phase 2)

### tw_davies_jones_c
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: same as `tw_c` but without Stull's domain
  mask.
- **Source**: not in loaders; candidate swap via
  `metpy.calc.wet_bulb_temperature` (Davies-Jones internally) or PyTw.
- **Mechanism**: Davies-Jones 2008 [43] is the canonical high-accuracy
  wet-bulb algorithm, MAE < 0.03 C, valid at altitude and low
  pressure where Stull [44] starts to drift. Buzan-Huber [216] review.
- **Phase B dimension**: yes (direct comparison to Stull; needed for
  hypothesis H014)
- **Notes**: requires surface pressure, so gated on ERA5 access or ISD
  pressure parsing.

---

## 3. Day–night decomposition (flagship HDR lever)

These features split the diurnal cycle into day and night windows. The
night window is defined as local-time `00:00–06:00` per
`data_acquisition_notes.md` (based on Bouchama-Knochel 2002 and Gasparrini-
Armstrong 2010 findings that early-morning minima drive the signal). They
are the heart of the HDR flagship hypothesis: night-time wet-bulb is the
missing variable.

### tw_night_c_mean
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: −5 to +27 C; tropical nights at Tw ≥ 26 C
  are the danger zone.
- **Source**: `aggregate_hourly_to_weekly` nights block: filter
  `local_hour < 6`, mean of hourly `tw_c` by `local_date`, then weekly
  mean.
- **Mechanism**: night-time wet-bulb directly quantifies the overnight
  evaporative-cooling sink [18, 21, 25]. A high `tw_night_c_mean` means
  the body cannot shed accumulated heat overnight, producing the
  hyperthermia accumulation that drives compound day-night mortality
  [28, 31, 32, 33, 34, 35, 121, 169]. This is the single variable most
  closely aligned with the HDR research question.
- **Phase B dimension**: yes (flagship)
- **Notes**: only populated by ISD/ERA5 hourly path, not by GHCN-D daily
  path (which leaves it NaN). Quality depends on report frequency —
  Paris Orly has 12 obs/night, some smaller synoptic stations only 1–2.

### tw_night_c_max
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: −5 to +30 C.
- **Source**: `aggregate_hourly_to_weekly` nights block: max of hourly
  `tw_c` within local `00:00–06:00`, weekly max.
- **Mechanism**: the maximum night-time wet-bulb within a week is a
  conservative danger signal: even one night with Tw_night ≥ 26 C can
  produce next-day excess mortality [28, 35, 121, 169]. Operationally
  this is the variable closest to a "night-time HeatRisk" addition.
- **Phase B dimension**: yes (flagship)
- **Notes**: correlates strongly with `tw_night_c_mean` but responds to
  single-night extremes.

### tw_day_c_max
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: 0 to +32 C.
- **Source**: not currently in loaders; derived by filtering
  `local_hour >= 12 & local_hour < 18` and taking max Tw in that window.
- **Mechanism**: daytime peak wet-bulb bounds the compensable-stress
  window during the active period when heat accumulates. Combining
  day-peak with night-min gives the compound signature.
- **Phase B dimension**: yes
- **Notes**: add in Phase 2 as one-line extension to
  `aggregate_hourly_to_weekly`.

### tw_day_night_spread_c
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: 2–15 C; very low spreads (<3 C) are the
  danger signature — the night is not cooling down.
- **Source**: derived as `tw_c_max − tw_night_c_mean` (or
  `tw_day_c_max − tw_night_c_min`).
- **Mechanism**: a small day–night wet-bulb spread is the meteorological
  fingerprint of a compound day-night heat wave [28, 32, 33, 121]. It
  captures the heat-dome regime [15, 42, 220, 221] where both day and
  night exceed local climatology and the body cannot recover.
- **Phase B dimension**: yes
- **Notes**: small spread is *more* dangerous, so sign is negative in
  the mortality regression.

### tropical_night_count_week
- **Type**: count (0–7)
- **Units**: days per week
- **Range / typical values**: 0 most of year; 0–7 in summer, common
  in Mediterranean August.
- **Source**: derived. Count of days in week where
  `tmin_c ≥ 20` (classical Mediterranean definition) or where
  `tw_night_c_max ≥ 22` (humid-heat variant).
- **Mechanism**: tropical nights (Tmin ≥ 20) are the long-standing
  WMO definition used in European heat-health monitoring [93, 101, 169].
  The wet-bulb equivalent is novel and directly tests the HDR
  hypothesis.
- **Phase B dimension**: yes
- **Notes**: classical and Tw-weighted variants are two separate
  variables to compare.

### consecutive_nights_above_tw_thresh
- **Type**: count
- **Units**: nights
- **Range / typical values**: 0–7 (within a week) or unbounded for
  running multi-week streaks.
- **Source**: derived via streak detection in
  `aggregate_hourly_to_weekly`.
- **Mechanism**: physiological hyperthermia accumulates; the cumulative
  count of consecutive hot nights drives the super-linear mortality
  response in compound heat waves [29, 31, 32, 33, 121]. Mukherjee-Mishra
  [29] defines concurrent-hot-day-and-hot-night events with 1-day,
  3-day, 5-day variants.
- **Phase B dimension**: yes
- **Notes**: threshold is a second lever — absolute (`tw ≥ 26`),
  city-percentile (`tw ≥ city p90`), or PSU-HEAT-derived.

### tmin_week_max
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: −10 to +32 C.
- **Source**: `aggregate_hourly_to_weekly` — need to add `tmin` max
  over the week. Candidate extension.
- **Mechanism**: the hottest night of the week is a tail signal for hot-
  night mortality [28, 35, 169]. Weekly-mean Tmin loses this extreme.
- **Phase B dimension**: yes
- **Notes**: complements `tw_night_c_max`.

---

## 4. Lag / window features

Mortality response to heat is distributed over several days. These features
pre-compute lag summaries so that a tree model can approximate DLNM without
fitting the full cross-basis.

### tmax_lag01_c_max
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: same as `tmax_c_mean`.
- **Source**: derived. `max(tmax_c_day[t], tmax_c_day[t-1])` rolled
  into the week.
- **Mechanism**: heat effects on mortality are strongest at lag 0 and
  lag 1 for cardiovascular / respiratory deaths [3, 6, 68, 120, 166].
  Including lag-0/1 explicitly lets non-DLNM models absorb the primary
  heat signal.
- **Phase B dimension**: yes
- **Notes**: week boundary complicates lag 0/1 across weeks; use daily
  within-week rolling and then take weekly summaries.

### tw_lag03_c_mean / lag07 / lag14 / lag21
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: −10 to +30 C.
- **Source**: derived. Rolling 3 / 7 / 14 / 21-day mean of daily Tw,
  aligned to the last day of the week.
- **Mechanism**: heat has same-day effects, 1–3 day cumulative effects,
  and a 2-week tail that includes mortality displacement [3, 4, 6, 120].
  Pre-extracting the DLNM cross-basis as hand-crafted lags lets tree
  models approximate the DLNM answer [140, 141, 142].
- **Phase B dimension**: yes
- **Notes**: multi-collinear with each other; tree models handle this
  but linear models need Ridge.

### tw_lag07_c_max / lag14_c_max
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: −5 to +32 C.
- **Source**: derived. Rolling max over the window.
- **Mechanism**: a hot week in the previous 7 days primes the elderly
  population for the next hot week (wave-priming / harvesting
  interaction [4, 10, 122]). The rolling max captures "has there been a
  single really hot day recently" better than rolling mean.
- **Phase B dimension**: yes

### dlnm_cross_basis_feat_{k}
- **Type**: continuous
- **Units**: dimensionless (basis function evaluation)
- **Range / typical values**: varies by basis.
- **Source**: derived. Use `dlnm` R package or a Python port
  (patsy splines × natural lag basis) to generate cross-basis columns
  from daily Tw or T up to lag 21, then feed to tree model.
- **Mechanism**: Gasparrini's DLNM [1, 2, 3, 4, 5] is the gold standard
  for heat-mortality regression. Pre-extracting basis features and
  feeding them to a flexible model is the "best of both worlds"
  approach Boudreault et al. [140, 141, 142] evaluated.
- **Phase B dimension**: yes
- **Notes**: 3 × 5 = 15 cross-basis columns is a typical
  exposure-response × lag configuration [6, 120].

### ma7_p_score_lag1
- **Type**: continuous
- **Units**: dimensionless
- **Range / typical values**: −0.2 to +0.5.
- **Source**: derived. 7-day rolling mean of target p-score, lagged 1
  week.
- **Mechanism**: autocorrelation in weekly excess mortality captures
  ongoing wave dynamics and short-horizon persistence. Prior-week
  mortality is a strong covariate in wave detection [138, 140, 142].
- **Phase B dimension**: yes
- **Notes**: leakage risk — must strictly lag 1+ week in validation
  split.

---

## 5. Percentile / anomaly features

Converts raw variables into local-climatology-relative values so that a
single model can pool across heterogeneous cities.

### tw_anomaly_c
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: −5 to +8 C relative to 1980–2010 climatology
  week-of-year reference.
- **Source**: `aggregate_hourly_to_weekly._apply_climatology` —
  `tw_c_mean − clim[week_of_year]` given a user-supplied climatology
  table. Phase 0.5 runs with `climatology=None` (Phase 1 addition).
- **Mechanism**: heat-mortality slope is ~2–5% per degree above the
  local 95th percentile, and cities adapt to their own climate; MMT
  rises with climate [6, 7, 124, 125, 126]. A raw Tw of 25 C is
  trivial in Dubai and unprecedented in Dublin. The anomaly form
  pools cities onto a common scale.
- **Phase B dimension**: yes
- **Notes**: the choice of reference period (1961-1990 / 1980-2010 /
  1991-2020) is itself a Phase B lever [7, 125, 126].

### tw_percentile_city_climatology
- **Type**: continuous
- **Units**: dimensionless (0–1)
- **Range / typical values**: 0–1.
- **Source**: derived. Rank-transform `tw_c_mean` within a city's
  1980–2010 week-of-year distribution (15-day moving window around
  the calendar day, per [31, 32, 121]).
- **Mechanism**: city-specific percentiles are how MCC Network cross-
  country comparisons are typically normalised [6, 7, 32, 127, 193].
  It is how EuroHEAT [95] and UK HHAS [103] trigger.
- **Phase B dimension**: yes
- **Notes**: sensitive to the climatology length; Phase 0.5 uses
  placeholder None.

### tmax_anomaly_c / tmin_anomaly_c
- **Type**: continuous
- **Units**: degrees C
- **Range / typical values**: −10 to +15 C.
- **Source**: derived analogously.
- **Mechanism**: dry-bulb anomalies are the standard comparators against
  which the HDR Tw anomaly must prove itself. Without a dry-bulb
  anomaly baseline the ablation story is weaker.
- **Phase B dimension**: yes

### tw_z_score_global
- **Type**: continuous
- **Units**: dimensionless
- **Range / typical values**: −3 to +5.
- **Source**: derived. `(tw_c - global_mean) / global_std` over the
  full city panel.
- **Mechanism**: alternative to city-specific anomalies; collapses
  the "rare-globally" aspect into one dimension. Matthews et al.
  2025 [88] argues rare atmospheric analogs encode mass-mortality
  potential in a non-city-specific way.
- **Phase B dimension**: yes (alternative to the city-relative form)

---

## 6. Heat-wave indicator features

Binary or categorical flags for "is this a heat wave" under various
definitions. These are the operational triggers that the HDR loop will
benchmark against.

### heat_dome_flag
- **Type**: binary
- **Units**: 0/1
- **Range / typical values**: ~2–5% of weeks in the panel.
- **Source**: `aggregate_hourly_to_weekly._heat_dome` — true if the
  longest run of consecutive days with
  `tw_c_max ≥ p95_threshold` in the week is ≥ 3.
- **Mechanism**: cooks the Tang / Lee / Yin compound-heatwave concept
  [31, 32, 33] down to a binary flag. The user supplies `p95_threshold`
  at call time; Phase 0.5 defaults to None (all false).
- **Phase B dimension**: yes
- **Notes**: the 3-day cutoff is the Anderson-Bell [10] standard; the
  threshold choice is the real lever.

### consecutive_days_above_p95
- **Type**: count
- **Units**: days
- **Range / typical values**: 0–7 within a week.
- **Source**: `_heat_dome` streak computation.
- **Mechanism**: see `heat_dome_flag`. Count form preserves information
  the binary loses — 7 days of streak is very different from 3.
- **Phase B dimension**: yes
- **Notes**: threshold lever is the same as above.

### euroheat_flag
- **Type**: binary
- **Units**: 0/1
- **Range / typical values**: ~3% of weeks.
- **Source**: derived. True if in the week there exist ≥ 2 consecutive
  days with both Tmax ≥ city-p90(Tmax) and Tmin ≥ city-p90(Tmin)
  within the May–September warm season [95, 101].
- **Mechanism**: EuroHEAT / D'Ippoliti 2010 [95] is the canonical
  European operational heat-wave definition; 9-city results reported
  7.6–33.6% mortality increases. This is a direct operational baseline
  to compare against.
- **Phase B dimension**: yes

### nws_heatrisk_level
- **Type**: categorical (0–4)
- **Units**: integer ordinal
- **Range / typical values**: 0 (no risk) to 4 (extreme).
- **Source**: not in loaders; optional pull from NWS HeatRisk archive
  [106, 107]. US-only.
- **Mechanism**: NWS HeatRisk is the direct operational benchmark the
  HDR loop wants to beat. Including it as a feature converts the HDR
  hypothesis into "does adding night-time Tw improve on HeatRisk".
- **Phase B dimension**: yes (CONUS only)
- **Notes**: Phase 1 addition; gated on data pull.

### uk_hhas_level
- **Type**: categorical (0–4)
- **Units**: integer ordinal
- **Range / typical values**: 0 green to 4 red.
- **Source**: not in loaders; UK-only scrape.
- **Mechanism**: UK Heat-Health Alert System is the UK operational
  benchmark [103]; Thompson 2022 [103] showed 2020 mortality patterns.
- **Phase B dimension**: no (UK only)

### mukherjee_mishra_compound_flag
- **Type**: binary
- **Units**: 0/1
- **Source**: derived. Tmax ≥ city-p90 AND Tmin ≥ city-p90 on same day,
  at least 2 consecutive days [29, 31].
- **Mechanism**: Mukherjee-Mishra 2018 [29] is the canonical "concurrent
  hot day + hot night" definition; projected sixfold rise under 2 C
  warming.
- **Phase B dimension**: yes

### tw_compound_flag
- **Type**: binary
- **Units**: 0/1
- **Source**: derived. Tw_day_max ≥ city-p90(Tw_day_max) AND
  Tw_night_max ≥ city-p90(Tw_night_max), at least 2 consecutive days.
- **Mechanism**: wet-bulb analogue of Mukherjee-Mishra, not yet in
  published operational systems. Directly operationalises the HDR
  hypothesis.
- **Phase B dimension**: yes (flagship)

---

## 7. Mortality target variants

Dependent variables. Phase B dimension includes target choice.

### deaths_all_cause
- **Type**: count
- **Units**: deaths / week
- **Range / typical values**: ~100 (Wyoming) to ~7000 (California) per
  state-week; NUTS-3 ~50–2000 per week.
- **Source**: `load_cdc_weekly_deaths` (US state-weekly VSRR Socrata
  `3yf8-kanr` + `r8kw-7aab`); `load_eurostat_weekly_deaths`
  (`demo_r_mwk3_t`, `demo_r_mweek3`).
- **Mechanism**: all-cause mortality is the epidemiologically preferred
  outcome because heat-related deaths are under-coded in ICD-10
  [60, 61, 68, 120, 158]. Gasparrini 2015 Lancet [6] confirms the
  all-cause choice.
- **Phase B dimension**: yes (vs cause-specific, vs elderly-only)
- **Notes**: CDC Wonder suppresses county-weekly counts below 10;
  therefore the state-weekly level is the practical US resolution. EU
  NUTS-3 is available with no suppression.

### expected_baseline
- **Type**: continuous
- **Units**: deaths / week
- **Source**: `data_loaders.compute_expected_baseline` — same-ISO-week
  mean over the previous 5 years, excluding the pandemic window
  (2020-W11 to 2022-W26 by default).
- **Mechanism**: Karlinsky-Kobak [60] P-score uses a simple same-week
  rolling mean; WHO [61, 156] and Acosta-Irizarry [158] use spline-on-
  trend. The Phase 0.5 baseline is the simplest defensible choice,
  matching EuroMOMO / Eurostat convention [154, 155].
- **Phase B dimension**: yes (swap to Farrington, Poisson-GLM, case-
  time-series [120]).

### excess_deaths
- **Type**: continuous
- **Units**: deaths / week (signed)
- **Source**: `deaths_all_cause − expected_baseline`.
- **Mechanism**: the raw observed-minus-expected [60, 63, 156, 157].
  This is the target that operational HHWS systems care about.
- **Phase B dimension**: yes

### p_score
- **Type**: continuous
- **Units**: dimensionless (fraction)
- **Range / typical values**: −0.3 to +0.5 typically, up to +1.0 in
  extreme events (2003 Paris, 2023 Phoenix).
- **Source**: `(deaths − expected) / expected`. Karlinsky-Kobak [60].
- **Mechanism**: P-score is the dimensionless excess, comparable across
  cities of different size without a population denominator
  [60, 61, 154, 155]. The World Mortality Dataset [60] is built on it.
- **Phase B dimension**: yes

### log_rate
- **Type**: continuous
- **Units**: log(deaths per population)
- **Source**: `log((deaths + 0.5) / population)`. Requires population
  data (Eurostat `demo_r_pjanaggr3`, US Census ACS).
- **Mechanism**: log-rate transforms are the canonical GLM link for
  Poisson time-series [3, 6, 68]. Allows cross-city pooling and the
  DLNM framework to be applied directly.
- **Phase B dimension**: yes
- **Notes**: needs population column; not in Phase 0.5 loaders.

### lethal_binary (p_score ≥ 0.10)
- **Type**: binary
- **Units**: 0/1
- **Source**: `(p_score ≥ 0.10)`.
- **Mechanism**: binarised classification target — "was this week lethal
  relative to baseline". Classification lets the HDR loop evaluate AUC,
  true positive / false positive ratios, precision at top-k, all
  metrics that matter more for HHWS skill than RMSE does
  [138, 140, 142, 198]. Jones-Fleck [138] built exactly this
  classifier.
- **Phase B dimension**: yes
- **Notes**: 0.10 threshold is the Phase 0.5 default; Phase B explores
  0.05, 0.10, 0.15, 0.20.

### asmr_weekly
- **Type**: continuous
- **Units**: age-standardised deaths per 100k
- **Source**: not in Phase 0.5; requires age-stratified deaths
  (`demo_r_mweek3` with `age`) and reference population weights
  (ESP2013 or WHO).
- **Mechanism**: age-standardised mortality rates are the preferred
  comparator when population age structure drifts across the evaluation
  window [63]. The Lancet Countdown uses this frame [37, 38].
- **Phase B dimension**: yes (Phase 1 addition)

### deaths_age_65p
- **Type**: count
- **Units**: deaths / week in age ≥ 65
- **Source**: `load_eurostat_weekly_deaths(dataset='demo_r_mweek3', age='Y_GE65')`.
- **Mechanism**: age 65+ is the strongest single vulnerability factor
  [9, 37, 90, 100, 163, 209]. The 2024 Lancet Countdown [37] reported
  a 167% rise in 65+ heat-mortality vs the 1990s.
- **Phase B dimension**: yes
- **Notes**: EU only; US CDC VSRR is all-ages at state-weekly.

---

## 8. Vulnerability moderators

City-level time-varying or time-invariant covariates that modify the
temperature–mortality slope.

### population_nuts3
- **Type**: count
- **Units**: people
- **Source**: Eurostat `demo_r_pjanaggr3` — NUTS-3 population. Not in
  Phase 0.5 loaders but referenced in §19 of `data_sources.md`.
- **Mechanism**: population is the denominator for rates and the scale
  parameter in Poisson GLMs [3, 6, 68].
- **Phase B dimension**: no (not a lever, a normaliser)

### pct_age_65p
- **Type**: continuous
- **Units**: fraction (0–1)
- **Source**: Eurostat population by age or US Census ACS.
- **Mechanism**: elderly share drives population-level heat-mortality
  slope [9, 37, 90, 163]. Sera 2019 [193] found it as a first-order
  meta-regressor.
- **Phase B dimension**: yes (Phase 1 addition)

### ac_penetration_pct
- **Type**: continuous
- **Units**: fraction of households with AC
- **Range / typical values**: 0.02 (Ireland) to 0.95 (Phoenix).
- **Source**: Gross et al. 2025 [212] dataset (US); ORNL county-level
  [213]; Sera et al. [75] multi-country.
- **Mechanism**: AC is the strongest known protective factor. Barreca
  et al. [76] estimates an 80% reduction in hot-day mortality since
  1960 due to AC diffusion. Sera et al. [75] multi-country panel
  confirms cross-country pattern.
- **Phase B dimension**: yes (Phase 1 addition)

### uhi_intensity_c
- **Type**: continuous
- **Units**: degrees C (summer nocturnal urban minus rural)
- **Range / typical values**: 1–6 C.
- **Source**: derived from station-pair differences or from Iungman et
  al. [85, 86] estimates.
- **Mechanism**: UHI is 4–5% of summer mortality across European cities
  [85, 86]; 38% of 2022 London heatwave deaths attributable [84];
  Paris 2003 UHI contribution [235, 236]. UHI is strongest at night —
  directly relevant to the compound-night HDR hypothesis.
- **Phase B dimension**: yes
- **Notes**: Phase 1 addition.

### deprivation_index
- **Type**: continuous
- **Units**: standardised z-score
- **Source**: Eurostat / UK IMD / US CDC Social Vulnerability Index.
- **Mechanism**: low SES is a heat-mortality risk factor via AC access,
  housing quality, isolation [74, 78, 122, 210]. Sera et al. [193]
  meta-regression confirms across MCC.
- **Phase B dimension**: yes (Phase 1)

### prior_week_pscore
- **Type**: continuous
- **Units**: dimensionless
- **Source**: derived — lag-1-week p-score.
- **Mechanism**: autocorrelation captures ongoing wave dynamics and
  harvesting dynamics [4, 10].
- **Phase B dimension**: yes
- **Notes**: leakage risk if the split is time-based and not group-based.

---

## 9. Co-stressor features

Features not directly related to heat but that modify its mortality impact.

### pm25_ug_m3
- **Type**: continuous
- **Units**: micrograms per cubic metre
- **Range / typical values**: 5–100, extreme fire events >500.
- **Source**: not in Phase 0.5 loaders. Candidate sources: OpenAQ, EEA
  AQ-e, US EPA AirNow, ECMWF CAMS reanalysis.
- **Mechanism**: PM2.5 amplifies heat mortality via additive or super-
  additive cardiovascular stress [110, 113, 114, 237]. Russia 2010
  wildfire-heat co-exposure was exceptionally lethal [110, 111].
- **Phase B dimension**: yes
- **Notes**: Phase 1 addition.

### o3_ppb
- **Type**: continuous
- **Units**: parts per billion
- **Range / typical values**: 10–120 ppb, warm-season peaks.
- **Source**: not in Phase 0.5 loaders. Same candidate sources as PM2.5.
- **Mechanism**: ozone co-varies with heat (photochemistry) and adds
  independent respiratory mortality effect [110, 113, 114, 237].
- **Phase B dimension**: yes

### wildfire_smoke_flag
- **Type**: binary
- **Units**: 0/1
- **Source**: not in Phase 0.5. HMS smoke plume archive or NOAA HMS.
- **Mechanism**: wildfire smoke PM2.5 spikes with heat-dome conditions
  [110, 112]. The Russian 2010 event [110] and 2023 Canadian fire
  smoke are paradigms.
- **Phase B dimension**: yes

### drought_index (SPI / PDSI)
- **Type**: continuous
- **Units**: standardised (−3 to +3) or Palmer (−6 to +6)
- **Source**: not in Phase 0.5. SPEI / CHIRPS / GridMET.
- **Mechanism**: drought modulates soil moisture and latent heat flux,
  worsening heat wave intensity and persistence [30, 219]. Moist
  soil regulates near-surface T; dry soil amplifies it.
- **Phase B dimension**: yes

### antecedent_precipitation_mm
- **Type**: continuous
- **Units**: mm
- **Source**: GHCN-D PRCP (available in loader by adding 'PRCP' to
  elements tuple) or ERA5 `total_precipitation`.
- **Mechanism**: 30-day antecedent precipitation modulates soil
  moisture; dry antecedents amplify heat dome persistence [30, 219].
- **Phase B dimension**: yes
- **Notes**: one-line extension to `load_ghcnd_city_daily`.

---

## 10. Temporal confounders

Time-varying covariates that must be controlled to avoid confounding by
season, week-of-year effects, holidays, and the pandemic.

### week_of_year_sin / week_of_year_cos
- **Type**: cyclic pair
- **Units**: dimensionless ∈ [−1, 1]
- **Source**: derived from `iso_week_start`.
- **Mechanism**: weekly seasonality captures holidays, flu season, and
  the annual mortality cycle [3, 6, 68]. Cyclic encoding avoids the
  week-52-to-week-1 wraparound seam.
- **Phase B dimension**: yes (include vs remove)

### year_index
- **Type**: count
- **Units**: years since 2013 (say)
- **Source**: derived.
- **Mechanism**: long-term trend in mortality (ageing, adaptation,
  baseline drift) [3, 6, 11, 125, 126]. Standard `ns(time, 7df/year)`
  DLNM spline [3] approximated here by a linear trend.
- **Phase B dimension**: yes

### holiday_flag
- **Type**: binary
- **Units**: 0/1
- **Source**: derived from national holiday calendars (e.g. `holidays`
  Python package).
- **Mechanism**: public holidays confound both mortality reporting and
  the number of heat-exposed days. Gasparrini DLNM papers use a
  holiday dummy in the control term [3, 6, 68].
- **Phase B dimension**: yes

### pandemic_indicator
- **Type**: binary
- **Units**: 0/1
- **Source**: derived from `iso_week_start` — true on 2020-W11 to
  2022-W26.
- **Mechanism**: COVID-19 weeks have massively elevated baseline
  mortality, confound the expected baseline, and break seasonal
  patterns [60, 61, 62, 63, 156, 158]. Excluding them from training is
  the Phase 0.5 default; Phase 2 tests including them with a dummy.
- **Phase B dimension**: yes

### weeks_since_last_heatwave
- **Type**: continuous
- **Units**: weeks
- **Source**: derived from a compound flag.
- **Mechanism**: recent prior heat exposure can cause depletion (tail-
  event harvesting — less vulnerable population remaining) or
  acclimatisation (physiological adaptation over days–weeks) [4, 10,
  127]. Short gap → depletion; longer gap → fresh wave.
- **Phase B dimension**: yes

---

## 11. City-level static covariates

Time-invariant city-level features.

### lat
- **Type**: continuous
- **Units**: degrees N
- **Range / typical values**: 25 (Miami) to 59 (Stockholm).
- **Source**: `data_loaders.CITIES[city].lat`.
- **Mechanism**: latitude determines climate zone, day length, solar
  load and therefore baseline heat-adaptation [6, 7, 124].
- **Phase B dimension**: yes

### lon
- **Type**: continuous
- **Units**: degrees E
- **Range / typical values**: −122 (Seattle) to +26 (Bucharest).
- **Source**: `CITIES[city].lon`.
- **Phase B dimension**: yes (coastal vs continental)

### country
- **Type**: categorical (ISO2)
- **Source**: `CITIES[city].country`.
- **Mechanism**: country-level fixed effects absorb health system
  differences, mortality coding, and reporting conventions [6, 7, 13,
  63, 154, 155].
- **Phase B dimension**: yes

### climate_zone (Köppen)
- **Type**: categorical (Cfa / Csa / BWh / Dfb etc.)
- **Source**: derived from lat/lon via Köppen-Geiger classification.
- **Mechanism**: Köppen class predicts both baseline climate and heat
  adaptation [6, 124, 127]. Lo et al. 2023 [53] showed metric-optimality
  is climate-dependent.
- **Phase B dimension**: yes

### elevation_m
- **Type**: continuous
- **Units**: metres
- **Source**: from GHCN-D / ISD station metadata or SRTM.
- **Mechanism**: elevation affects pressure and therefore Stull vs
  Davies-Jones wet-bulb divergence [43, 44]. Denver (1600 m) and Madrid
  (650 m) are the altitude-sensitive cases.
- **Phase B dimension**: yes (especially for Stull-vs-Davies-Jones
  ablation)

---

## 12. Identifiers and join keys

### city
- **Type**: categorical
- **Source**: `data_loaders._CITY_ROWS` — 30 cities.
- **Notes**: primary group key. Must be used for group-shuffle split
  to avoid leakage.

### iso_week_start
- **Type**: date (ISO Monday)
- **Source**: derived from `_iso_week_start()`.
- **Notes**: primary time key.

### iso_year_week
- **Type**: categorical (`YYYY-Www`)
- **Source**: derived from `_iso_year_week()`.
- **Notes**: join key for Eurostat `time` column.

---

## 13. Summary table

| variable | type | source | baseline | Phase 2 | Phase B |
|---|---|---|:---:|:---:|:---:|
| tmax_c_mean | continuous | ISD/GHCN-D→aggregate | yes | yes | no |
| tmin_c_mean | continuous | ISD/GHCN-D→aggregate | yes | yes | no |
| tavg_c | continuous | ISD/GHCN-D→aggregate | yes | yes | no |
| tdew_c | continuous | ISD/GHCN-D | no | yes | yes |
| rh_pct | continuous | derived | no | yes | yes |
| sp_hpa / msl_hpa | continuous | ERA5 | no | no | loader |
| wind_ms | continuous | ERA5 Phase 1 | no | no | loader |
| ssrd_wm2 | continuous | ERA5 Phase 1 | no | no | loader |
| tw_c | continuous | compute_wet_bulb (Stull) | no | yes | yes |
| tw_c_mean | continuous | aggregate_hourly | no | yes | yes |
| tw_c_max | continuous | aggregate_hourly | no | yes | yes |
| heat_index_c | continuous | derived | no | yes | yes |
| apparent_temp_c | continuous | ERA5 Phase 1 | no | no | yes |
| humidex_c | continuous | derived | no | yes | yes |
| swbgt_c | continuous | derived | no | yes | yes |
| wbgt_full_c | continuous | ERA5 Phase 1 | no | no | yes |
| utci_c | continuous | ERA5-HEAT Phase 1 | no | no | yes |
| pet_c | continuous | Phase 2+ | no | no | no |
| tw_davies_jones_c | continuous | metpy + ERA5 Phase 1 | no | yes | yes |
| tw_night_c_mean | continuous | aggregate_hourly night block | no | **yes (flagship)** | **yes** |
| tw_night_c_max | continuous | aggregate_hourly night block | no | **yes (flagship)** | **yes** |
| tw_day_c_max | continuous | derived | no | yes | yes |
| tw_day_night_spread_c | continuous | derived | no | yes | yes |
| tropical_night_count_week | count | derived | no | yes | yes |
| consecutive_nights_above_tw_thresh | count | derived | no | yes | yes |
| tmin_week_max | continuous | derived | no | yes | yes |
| tmax_lag01_c_max | continuous | derived | no | yes | yes |
| tw_lag03/07/14/21_c_mean | continuous | derived | no | yes | yes |
| tw_lag07/14_c_max | continuous | derived | no | yes | yes |
| dlnm_cross_basis_feat_k | continuous | patsy/dlnm | no | yes | yes |
| ma7_p_score_lag1 | continuous | derived | no | yes | yes |
| tw_anomaly_c | continuous | _apply_climatology | no | yes | yes |
| tw_percentile_city_climatology | continuous | derived | no | yes | yes |
| tmax_anomaly_c | continuous | derived | no | yes | yes |
| tmin_anomaly_c | continuous | derived | no | yes | yes |
| tw_z_score_global | continuous | derived | no | yes | yes |
| heat_dome_flag | binary | _heat_dome | no | yes | yes |
| consecutive_days_above_p95 | count | _heat_dome | no | yes | yes |
| euroheat_flag | binary | derived | no | yes | yes |
| nws_heatrisk_level | categorical | Phase 1 pull (US only) | no | no | yes |
| uk_hhas_level | categorical | Phase 1 (UK only) | no | no | no |
| mukherjee_mishra_compound_flag | binary | derived | no | yes | yes |
| tw_compound_flag | binary | derived | no | **yes (flagship)** | **yes** |
| deaths_all_cause | count | CDC VSRR / Eurostat | **target** | target | target |
| expected_baseline | continuous | compute_expected_baseline | no | yes | yes |
| excess_deaths | continuous | computed | yes | yes | yes |
| p_score | continuous | computed | yes | yes | yes |
| log_rate | continuous | needs population | no | yes | yes |
| lethal_binary | binary | derived | no | yes | yes |
| asmr_weekly | continuous | Phase 1 | no | no | yes |
| deaths_age_65p | count | demo_r_mweek3 age='Y_GE65' | no | yes | yes |
| population_nuts3 | count | demo_r_pjanaggr3 Phase 1 | no | no | no |
| pct_age_65p | continuous | Phase 1 | no | yes | yes |
| ac_penetration_pct | continuous | Phase 1 (Gross et al 2025 [212]) | no | yes | yes |
| uhi_intensity_c | continuous | Phase 1 | no | yes | yes |
| deprivation_index | continuous | Phase 1 | no | yes | yes |
| prior_week_pscore | continuous | derived | no | yes | yes |
| pm25_ug_m3 | continuous | Phase 1 (OpenAQ / CAMS) | no | yes | yes |
| o3_ppb | continuous | Phase 1 | no | yes | yes |
| wildfire_smoke_flag | binary | Phase 1 (HMS) | no | yes | yes |
| drought_index | continuous | Phase 1 (SPEI / GridMET) | no | yes | yes |
| antecedent_precipitation_mm | continuous | GHCN-D PRCP | no | yes | yes |
| week_of_year_sin / cos | cyclic | derived | yes | yes | yes |
| year_index | count | derived | yes | yes | yes |
| holiday_flag | binary | derived | no | yes | yes |
| pandemic_indicator | binary | derived | yes | yes | yes |
| weeks_since_last_heatwave | continuous | derived | no | yes | yes |
| lat | continuous | CITIES | yes | yes | yes |
| lon | continuous | CITIES | yes | yes | yes |
| country | categorical | CITIES | yes | yes | yes |
| climate_zone | categorical | derived | no | yes | yes |
| elevation_m | continuous | station metadata | no | yes | yes |
| city | categorical | CITIES (group key) | — | — | — |
| iso_week_start | date | derived (join key) | — | — | — |
| iso_year_week | categorical | derived (join key) | — | — | — |

Bold rows (flagship) are the HDR primary hypothesis variables. The HDR
Phase 0.5 baseline comparison is `X_base = {tmax_c_mean, tmin_c_mean,
tavg_c}` vs `X_hyp = X_base + {tw_c_mean, tw_night_c_mean, tw_night_c_max}`
per `data_acquisition_notes.md` §"Phase 0.5 baseline recipe".
