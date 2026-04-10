# Data sources — heat-wave excess mortality

Phase 0 inventory of the open datasets we can combine to answer:
> Which heat waves cause measurable excess mortality and which are merely
> uncomfortable? Days-to-weeks-ahead. Is **night-time wet-bulb temperature**
> the missing variable in current heat-health early-warning systems?

The unit of analysis is **city / NUTS-3 region / week**. Predictors are
atmospheric (temperature, dewpoint, wet-bulb, day-night patterns); target is
weekly all-cause mortality, with excess computed against a seasonal baseline.

All live probes below were run with `requests.get(...)` and `cdsapi`-style
manual HTTP on **2026-04-09**. The row counts, date ranges, and schema samples
are what the APIs returned that day. Where a dataset name in the task brief was
ambiguous (`demo_r_mwk_05`), the actually-valid endpoint is recorded and the
ambiguity noted.

--------------------------------------------------------------------------------
## Table of contents

### Exposure (meteorology)
1. ERA5 reanalysis — hourly single levels (Copernicus CDS)
2. ERA5-Land — hourly, 0.1° land-only (Copernicus CDS)
3. ERA5-HEAT / Thermal Comfort Indices (Copernicus CDS, DOI cds.553b7518)
4. HadISDH + HadISDH.extremes (UK Met Office / CEDA)
5. GHCN-Daily — NOAA NCEI station-daily
6. NOAA NCEI Integrated Surface Database (ISD) — hourly, **global**, **has dewpoint**
7. (optional) NOAA NWS HeatRisk — operational + archive
8. (optional) NOAA Storm Events Database — heat-event ground truth

### Mortality (target)
9. Eurostat `demo_r_mweek3` — weekly deaths at NUTS-3 by sex / 5-year age
10. Eurostat `demo_r_mwk3_t` — weekly deaths at NUTS-3, total only
11. Eurostat `demo_r_mwk_10` / `demo_r_mwk_20` — weekly deaths, country-level, coarser ages
12. CDC NCHS Socrata `r8kw-7aab` — provisional US weekly all-cause + `percent_of_expected_deaths` by state
13. CDC NCHS Socrata `3yf8-kanr` — 2014–2019 US weekly all-cause by state
14. CDC NCHS Socrata `muzy-jte6` — 2020–2023 US weekly by cause, state
15. CDC WONDER `ucd-icd10-expanded` — **monthly** (not weekly) US county
16. EuroMOMO — aggregated weekly z-scores, limited download
17. MoMo Spain (ISCIII) — daily excess deaths by province
18. MCC Network (Multi-Country Multi-City) — **not openly redistributable**

### Population / geometry
19. Eurostat `demo_r_pjanaggr3` — NUTS-3 population
20. US Census ACS 5-year (`B01003_001E`) — county population
21. Cities-by-lat-lon lookup — inline in `data_loaders.CITIES`

--------------------------------------------------------------------------------

## 1. ERA5 hourly single levels

| field | value |
|---|---|
| Owner | ECMWF / Copernicus Climate Change Service (C3S) |
| Dataset name | ERA5 hourly data on single levels from 1940 to present |
| CDS dataset ID | `reanalysis-era5-single-levels` |
| DOI | 10.24381/cds.adbb2d47 |
| Landing URL | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels |
| API | `cdsapi` Python package (`pip install "cdsapi>=0.7.7"`) |
| License | CC-BY-4.0, but **each dataset requires manual "Agree to terms"** from a logged-in CDS account before the API will serve it |
| Registration | Mandatory. Create account at https://cds.climate.copernicus.eu, generate a personal access token from the profile page, write it to `~/.cdsapirc` |
| Time range | 1940-01-01 → present, ~5-day latency |
| Grid | 0.25° × 0.25° lat-lon (~28 km at the equator); uncertainty ensemble at 0.5° |
| Temporal | Hourly |
| Update cadence | Daily (rolling 5-day lag) |
| Row count | Globally: (721 × 1440) × 24 × ~30 000 days ≈ 7.5 × 10^11 cell-hours. Per city-year: 8760 hourly rows per variable |

### Key variables used here

| purpose | CDS short name | units | notes |
|---|---|---|---|
| 2 m air temperature | `2m_temperature` / `t2m` | K | subtract 273.15 |
| 2 m dewpoint | `2m_dewpoint_temperature` / `d2m` | K | fed to Stull (2011) wet-bulb approximation |
| mean sea-level pressure | `mean_sea_level_pressure` / `msl` | Pa | only needed if using a pressure-dependent wet-bulb solver |
| surface pressure | `surface_pressure` / `sp` | Pa | ditto |
| 10 m u / v wind | `10m_u_component_of_wind` / `10m_v_component_of_wind` | m/s | for UTCI / apparent temp baselines |
| total precipitation | `total_precipitation` / `tp` | m | not primary but cheap to co-retrieve |

### Schema sample (netCDF coordinate convention)

An ERA5 netCDF slice for a single city grid cell, 3 hours:

```
Coordinates:
    longitude  float32  2.25          # nearest grid to Paris 2.35E
    latitude   float32  48.75         #                     48.85N
    time       datetime64[ns]  2023-07-15 00:00, 2023-07-15 01:00, 2023-07-15 02:00
Data variables:
    t2m        float32  (time)        K   [296.12, 295.47, 294.88]
    d2m        float32  (time)        K   [289.05, 288.71, 288.14]
    msl        float32  (time)        Pa  [101725., 101717., 101710.]
    sp         float32  (time)        Pa  [100388., 100380., 100374.]
```

After subtraction and Stull(T, RH):
```
iso_datetime_utc     t2m_c  d2m_c   rh_pct  tw_c_stull
2023-07-15 00:00     22.97  15.90   65.3    18.34
2023-07-15 01:00     22.32  15.56   66.8    17.98
2023-07-15 02:00     21.73  14.99   66.1    17.50
```

### Gotchas

- **License agreement is per-dataset**. If your code issues `client.retrieve("reanalysis-era5-single-levels", ...)` and you have not clicked "Accept terms" on the dataset landing page while logged in, you get a 403. The loader emits a clear error pointing at the URL.
- **Kelvin, not Celsius.** Every temperature field comes in kelvin; convert before anything else.
- **grib vs netCDF.** For this project we always request `format=netcdf` because `xarray.open_dataset` handles time / coord extraction for free.
- **CDS queue**. There is no published rate limit; "costly requests receive a lower priority". A request for `t2m + d2m` for one city-year is trivial and returns in seconds. A global hourly 1940–present pull will queue for days.
- **Best-effort temporal coverage.** "Present" data (within ~5 days) is labelled "ERA5T" and may change when the final re-analysis replaces it ~3 months later.
- **Leap seconds / sub-hourly.** ERA5 is on-the-hour; sub-hourly night-time resolution (needed for the 00–06 local window) is constructed from the 7 hourly samples per night.

--------------------------------------------------------------------------------

## 2. ERA5-Land hourly

| field | value |
|---|---|
| Owner | ECMWF / C3S |
| Dataset name | ERA5-Land hourly data from 1950 to present |
| CDS dataset ID | `reanalysis-era5-land` |
| DOI | 10.24381/cds.e2161bac |
| Landing URL | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land |
| License | CC-BY-4.0, same per-dataset acceptance step |
| Time range | 1950-01-01 → present |
| Grid | 0.1° × 0.1° regular lat-lon (~9 km native); **land-only** (ocean cells are `NaN`) |
| Temporal | Hourly |
| Update cadence | Daily |

### Why use it at all over single-levels

- 0.1° vs 0.25°: the Paris–Montsouris cell at 0.1° separates from Bois-de-Boulogne which is distinct from La Défense. At 0.25°, a single cell covers the entire Paris metro.
- Includes a **lapse-rate elevation correction**, which materially improves T2m for mountainous cities (Madrid, Athens, Phoenix, Denver).
- Land-component replay uses ERA5 atmospheric forcing but re-runs the soil / canopy / snow model, so it is *not* just a bilinear interpolation.

### Gotchas

- **Ocean cells are NaN.** Coastal cities (Lisbon, San Diego, Miami) sometimes get unlucky with centroid rounding. The loader snaps to the nearest *land* cell within 0.15° if the centroid returns NaN.
- Missing a few variables that single-levels has (no `msl` on land-only product). Use single-levels for pressure.
- **No ensemble.** ERA5-Land is a single deterministic run.

--------------------------------------------------------------------------------

## 3. ERA5-HEAT — Thermal Comfort Indices derived from ERA5

| field | value |
|---|---|
| Owner | ECMWF / C3S |
| Dataset name | Thermal comfort indices derived from ERA5 reanalysis |
| CDS dataset ID | `derived-utci-historical` |
| DOI | 10.24381/cds.553b7518 |
| Landing URL | https://cds.climate.copernicus.eu/datasets/derived-utci-historical |
| License | Copernicus Products licence (free after account + terms acceptance) |
| Time range | 1940-01 → near real time (intermediate dataset updated daily, consolidated monthly with 2–3 month lag) |
| Grid | 0.25° × 0.25°, global **except Antarctica** (90°N–60°S) |
| Variables | **UTCI** (Universal Thermal Climate Index, K), **mean radiant temperature** (K); plus UTCI daily / monthly / seasonal / yearly stats and "tropical nights" counters |

### Why we keep it anyway

- UTCI is a defensible, internationally-used human-comfort aggregate. It is **not a wet-bulb**, but a function of (T, RH, wind, radiation). Useful as a *baseline* against which to test whether plain night-time wet-bulb carries additional predictive power.
- Saves us from separately loading wind and radiation fields just to reproduce a UTCI-like signal.

### Gotchas

- UTCI and wet-bulb are **not interchangeable**. UTCI includes radiation and wind adjustments; wet-bulb does not. The Gasparrini et al. literature and the IPCC-AR6 heat-health chapters use different indicators and it is important to report both.
- Tropical-nights counters are based on T2m thresholds (typically 20 °C min nightly temp), not wet-bulb. Rebuild our own T_w nocturnal counters from the hourly ERA5 pulls.

--------------------------------------------------------------------------------

## 4. HadISDH and HadISDH.extremes

| field | value |
|---|---|
| Owner | Met Office Hadley Centre |
| Dataset name | HadISDH — gridded global surface humidity; HadISDH.extremes — gridded wet-bulb & dry-bulb extremes indices |
| Landing URL | https://www.metoffice.gov.uk/hadobs/hadisdh/ |
| CEDA catalogue | https://catalogue.ceda.ac.uk/uuid/2d1613955e1b4cd1b156e5f3edbd7e66/ (extremes, DOI 10.5285/2d1613955e1b4cd1b156e5f3edbd7e66) |
| Download portal | https://data.ceda.ac.uk (free, registration) |
| License | Open Government Licence v3 (OGL) |
| Time range | 1973-01 → 2024-12 (stable v1.2.0.2024f); provisional 2025 extension available |
| Grid | **5° × 5°** land-only gridboxes centred on ±87.5° / ±177.5° — coarse but long baseline |
| Temporal | Monthly |
| Variables | Specific humidity q, relative humidity RH, dewpoint Td, **wet-bulb Tw**, vapour pressure e, DPD; plus 29 extremes indices (Tw percentiles, number-of-days above Tw thresholds, etc.) |

### Why we use it

- It is the canonical *long* global wet-bulb reference and the one humidity-extreme community has been calibrating against. The 2024 .extremes release explicitly includes Tw extreme indices — tailor-made for climatology anomalies.
- 5° is way too coarse for city-level prediction, but it gives us a credible **50-year climatology baseline** and a sanity check for our own Stull-from-ERA5 wet-bulb time series.

### Gotchas

- **5° is not a city; it is a region.** Do not use HadISDH to predict Paris mortality. Use it to compute the 1980–2010 reference field against which the ERA5 (0.25°) city-level anomaly is measured.
- Monthly only — no sub-monthly, no nights.
- CEDA login is free but required even for anonymous download of the largest grids; small subsets via the catalogue GUI do not need it.

--------------------------------------------------------------------------------

## 5. GHCN-Daily

| field | value |
|---|---|
| Owner | NOAA NCEI |
| Dataset name | Global Historical Climatology Network — daily |
| Landing URL | https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily |
| Bulk HTTPS | https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/ |
| Station list | https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt (11 MB fixed-width) |
| Per-station CSV (gz) | https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/access/by_station/&lt;STATIONID&gt;.csv.gz |
| JSON access API | https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=&lt;id&gt;&startDate=YYYY-MM-DD&endDate=YYYY-MM-DD&dataTypes=TMAX,TMIN,TAVG,ADPT,AWBT,RHAV&format=json |
| License | Public domain (US federal work); CC0-equivalent |
| Time range | 1732-01 (earliest station) → present; most US/EU core stations 1950 → present |
| Station count | ~100,000 globally, 180 countries |

### Key variables (units!)

| code | meaning | GHCN unit | our unit |
|---|---|---|---|
| TMAX | daily max temperature | tenths of °C (e.g. `311` = 31.1 °C) | °C |
| TMIN | daily min temperature | tenths of °C | °C |
| TAVG | daily mean temperature | tenths of °C | °C |
| ADPT | daily **average dewpoint** | tenths of °C | °C |
| AWBT | daily **average wet-bulb** | tenths of °C | °C |
| RHAV | average relative humidity | % | % |
| PRCP | precipitation | tenths of mm | mm |
| Missing | all | **`-9999`** | NaN |

### Schema sample (JSON access API, Central Park USW00094728)

```
[{"DATE":"2023-07-15","STATION":"USW00094728","TMAX":"  311","TMIN":"  217","AWBT":"  233","ADPT":"  228","RHAV":"   83"},
 {"DATE":"2023-07-16","STATION":"USW00094728","TMAX":"  256","TMIN":"  233","AWBT":"  239","ADPT":"  233","RHAV":"   91"},
 {"DATE":"2023-07-17","STATION":"USW00094728","TMAX":"  311","TMIN":"  233","AWBT":"  228","ADPT":"  206","RHAV":"   70"}]
```

### The big gotcha: ADPT/AWBT/RHAV are **US-only**

**Verified on 2026-04-09** across `USW00094728` (NYC), `USW00023174` (LAX),
`USW00023188` (San Diego), `USW00012839` (Miami), `USW00013874` (Atlanta),
and also the European stations `UKM00003772` (London Heathrow),
`SPE00120287` (Madrid Retiro), `FRM00007156` (Paris Montsouris),
`GME00122614` (Berlin Tempelhof), `ITE00100550` (Rome), `GRE00105257` (Greece).

- **All 5 US stations** returned `TMAX, TMIN, ADPT, AWBT, RHAV` for 2023-07-15 — wet-bulb and dewpoint are just there.
- **All 6 European stations** returned `TMAX, TMIN, TAVG` only — the extended humidity elements are absent. Either the raw station reports did not flow the humidity elements through GHCN-D's "All Elements" quality control, or they never submitted hourly data to NCEI.

**Implication.** For US cities, GHCN-Daily alone is enough to compute daily
wet-bulb without ever touching ERA5 or Copernicus. For European cities, GHCN-D
gives us dry-bulb only — and we must get dewpoint from ISD (§6) or ERA5 (§1).

### Other gotchas

- Fixed-width station file: station ID in cols 1–11, lat cols 13–20, lon cols 22–30, elev cols 32–37, name cols 42–71.
- About half of all stations only report PRCP.
- `GHCNd` element list has ~60 codes; most are rare. Stick to the core seven above.
- The JSON access API silently returns an empty list `[ ]` if a station has none of the requested elements. Always also request a known-present element (`TMAX`) as a canary.

--------------------------------------------------------------------------------

## 6. NOAA Integrated Surface Database (ISD) — hourly, global, **has dewpoint**

| field | value |
|---|---|
| Owner | NOAA NCEI |
| Dataset name | Integrated Surface Database (ISD) |
| Bulk CSV | https://www.ncei.noaa.gov/data/global-hourly/access/&lt;YEAR&gt;/&lt;USAF&gt;&lt;WBAN&gt;.csv |
| Station list | https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv |
| License | Public domain (US federal work) |
| Time range | 1901 → present for oldest stations; Paris Orly `07149099999` is 1973 → 2025 |
| Coverage | ~14 000 active stations, global, airport / military / synoptic |
| Temporal | Hourly or sub-hourly (6 to 72 reports per day per station depending on automation) |

### Key fields

| column | content | format | our use |
|---|---|---|---|
| `STATION` | `USAF` + `WBAN` composite ID | 11-char string | join |
| `DATE` | ISO timestamp | `2023-07-15T01:00:00` | primary key |
| `LATITUDE`, `LONGITUDE`, `ELEVATION` | station location | decimal degrees | snap to city |
| `REPORT_TYPE` | FM-12, FM-15, SAO, etc. | string | prefer FM-12 for synoptic hourly |
| `TMP` | air temperature | `+0234,1` = +23.4 °C quality 1 | strip, parse |
| `DEW` | **dewpoint** | `+0111,1` = +11.1 °C quality 1 | **needed for wet-bulb** |
| `SLP` | sea-level pressure | `10110,1` = 1011.0 hPa | |
| `WND` | wind | `V020` / `1 90,1,N,0020,1` | optional |

### Schema sample (verified: Paris Orly `07149099999`, 2023)

```
STATION,DATE,LATITUDE,LONGITUDE,ELEVATION,NAME,REPORT_TYPE,TMP,DEW,SLP
"07149099999","2023-07-15T00:00:00","48.725278","2.359444","88.69","ORLY, FR","FM-12","+0234,1","+0111,1","10110,1"
"07149099999","2023-07-15T00:30:00","48.725278","2.359444","88.69","ORLY, FR","FM-15","+0230,1","+0120,1","10112,1"
"07149099999","2023-07-15T01:00:00","48.725278","2.359444","88.69","ORLY, FR","FM-12","+0223,1","+0131,1","10110,1"
```

### Why this is the hero for European cities

ISD is the **only open source** that gives us *hourly* dewpoint for European
airports without a Copernicus account. Combined with Stull(T, RH) or a Td-based
wet-bulb derivation, it is sufficient for the night-time wet-bulb question.

### Gotchas

- **Quoted-CSV parser required.** The `NAME` field contains commas (`"ORLY, FR"`); naive `line.split(",")` breaks. Use `csv.DictReader`.
- `TMP` and `DEW` are encoded **in tenths of °C** just like GHCN-D, but prefixed with sign and suffixed with a quality flag: `"+0234,1"`. Quality `1` = passed all QC; `2` = suspect; `9` = missing.
- **Missing value sentinel is `+9999,9` for TMP and DEW.** Discard it.
- **Multiple report types per hour.** A station with METAR (FM-15) and SYNOP (FM-12) will emit 2 rows per hour. Deduplicate on `(STATION, floor(DATE, 1h), REPORT_TYPE=FM-12)` first, then fall back to whatever is left.
- Yearly file size for a major European airport: ~10 MB gzipped, ~25 000 rows (Paris Orly 2023 = 25 741 rows).
- Some stations report only 6 times per day (synoptic) and will not resolve the 00–06 local-time window properly — prefer airport stations with `FM-15` METAR coverage.

--------------------------------------------------------------------------------

## 7. (optional) NOAA NWS HeatRisk

| field | value |
|---|---|
| Owner | NOAA NWS / WPC |
| Dataset name | NWS HeatRisk — 5-level (0–4) operational heat forecast |
| Landing URL | https://www.wpc.ncep.noaa.gov/heatrisk/ |
| Current files | `HeatRisk_Day{1–7}_Fcst.kml`, `HeatRisk_{1–7}_Mercator.tif` |
| Archive URL | https://www.wpc.ncep.noaa.gov/heatrisk/data/archive/ |
| Archive coverage (verified 2026-04-09) | `HeatRisk_CONUS_YYYYMMDD.{png,kml,tif}`, **617 days, 2024-08-01 → 2026-04-09** |
| Longer archive | "NWS Historical HeatRisk 2005–2024" via Datalumos (https://www.datalumos.org/datalumos/project/223525, requires registration) |
| License | Public domain (US federal work) |
| Spatial coverage | CONUS only |
| Resolution | Nominally ~2.5 km (inherited from NDFD) |

### Why it's optional

- It is **the operational system we want to benchmark against.** Our model needs to beat or complement HeatRisk.
- But the freely downloadable archive only goes back to 2024-08, so for a multi-year baseline the Datalumos back-fill is required. The loader skips it until we confirm project access.
- CONUS only — useless for European cities.

--------------------------------------------------------------------------------

## 8. (optional) NOAA Storm Events Database

| field | value |
|---|---|
| Owner | NOAA NWS |
| Dataset name | Storm Events Database |
| Bulk URL | https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/ |
| File convention | `StormEvents_details-ftp_v1.0_dYYYY_c&lt;version&gt;.csv.gz` |
| Time range | 1950 → 2025 (228 files as of 2026-04-09) |
| Verified | 2023 file = 12.9 MB, 75 593 rows, **8347 `Heat`/`Excessive Heat` rows, 879 heat-related deaths reported** |
| License | Public domain |

### Key fields

| column | notes |
|---|---|
| `EVENT_TYPE` | `Heat`, `Excessive Heat`, `Drought`, `Tornado`, … |
| `STATE`, `STATE_FIPS` | US state |
| `CZ_TYPE`, `CZ_FIPS`, `CZ_NAME` | county / forecast zone |
| `BEGIN_DATE_TIME`, `END_DATE_TIME` | event window, mixed-case e.g. `06-JUL-23 11:00:00` |
| `DEATHS_DIRECT`, `DEATHS_INDIRECT` | **event-level** — these are NWS-attributed deaths, not population-level all-cause |
| `INJURIES_DIRECT`, `INJURIES_INDIRECT` | as above |

### Why this is **ground truth, not target**

`DEATHS_DIRECT + DEATHS_INDIRECT` is dramatically under-counted vs
epidemiological excess-mortality estimates. In 2023, Storm Events logged 879
heat deaths — whereas the NOAA / CDC excess-mortality estimate for the same
year is >2 000 in the US alone. Treat it as a per-event flag ("did NWS attribute
at least one death?") and as a positive label for heat-wave severity, **not**
as a regression target.

--------------------------------------------------------------------------------

## 9. Eurostat `demo_r_mweek3` — weekly deaths, NUTS-3, sex × age

| field | value |
|---|---|
| Owner | Eurostat / ESTAT |
| Dataset code | `demo_r_mweek3` |
| Label | "Deaths by week, sex, 5-year age group and NUTS 3 region" |
| Landing | https://ec.europa.eu/eurostat/databrowser/view/demo_r_mweek3 |
| JSON-stat API | `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_r_mweek3?format=JSON&lang=EN&geo=<NUTS3>&sex=T&age=TOTAL` |
| SDMX API | `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_r_mweek3/...` |
| License | Eurostat Open Data policy (attribution required, free for any use) |
| Time range (metadata) | 2000-W01 → 2026-W06 |
| Time range (actual data for most NUTS-3 regions) | **~2013-W01** → present; only a handful of countries back-fill to 2000 |
| Row count per NUTS-3 × age × sex | ~680 non-null weeks × `(A × S)` where A ≈ 22 age groups, S = 3 sexes |
| Geo count | 1528 (mix of NUTS-0/1/2/3 plus EU aggregates) |
| Updated | 2026-04-09 23:00 CEST (verified from API `updated` field) |

### Schema sample (actual API output for Paris NUTS-3 FR101, sex=T, age=TOTAL)

After unflattening the JSON-stat response:

```
geo     nuts_label                           sex  age     iso_year_week  value
FR101   Paris                                T    TOTAL   2023-W28        232
FR101   Paris                                T    TOTAL   2023-W29        248
FR101   Paris                                T    TOTAL   2023-W30        241
FR101   Paris                                T    TOTAL   2020-W14        914   <- COVID spike
FR101   Paris                                T    TOTAL   2022-W30        295   <- 2022 heat dome
```

### Gotchas

- **The task brief said `demo_r_mwk_05`. That's country-level, not NUTS-3.** On 2026-04-09 I probed `demo_r_mwk_05` and found 39 geos, all length-2 (country) codes. The correct NUTS-3 dataset is **`demo_r_mweek3`** (or `demo_r_mwk3_t` for total-only). Using the wrong one silently loses 1489 regional rows.
- **JSON-stat "value" object is keyed by flattened index**, not by `(time, age, sex, geo)`. The loader computes the strides from `dimension[i]['size']` and indexes manually.
- **Age codes**: `TOTAL`, `Y_LT5`, `Y5-9`, …, `Y85-89`, `Y_GE90`, `UNK`. Stick to `TOTAL` or `Y_GE65` for the baseline; the 5-year age groups inflate response size 22×.
- **NUTS revisions 2003 → 2006 → 2010 → 2013 → 2016 → 2021 → 2024**. A single NUTS-3 code can denote different polygons across revisions. The weekly-deaths table claims to use NUTS-2021 but older time points reuse the historical code if the geometry is stable. For 90+% of our cities, the code is revision-stable. Lisbon, Athens, and several Polish cities have had boundary changes; drop those from the baseline and revisit later.
- **Pandemic confounding.** Weeks 2020-W13 → 2022-W26 are dominated by COVID, not heat. Either drop or add a pandemic dummy (see `data_acquisition_notes.md`).
- `value` can be `null` (reported as "missing", e.g. pre-2013 for most NUTS-3). Do not confuse with zero.
- **JSON response is slow** for multi-geo queries (~15 s for 100 NUTS-3 codes). Pull per-geo in parallel or cache aggressively.

--------------------------------------------------------------------------------

## 10. Eurostat `demo_r_mwk3_t` — weekly deaths NUTS-3, total only

Lighter sibling of §9, without sex/age dimensions. 1506 geos, returns faster
because the response size is 1/66 smaller. Use this for the exposure-join
baseline; upgrade to `demo_r_mweek3` once we need `Y_GE65` for sensitivity
analysis.

--------------------------------------------------------------------------------

## 11. Eurostat `demo_r_mwk_05` / `demo_r_mwk_10` / `demo_r_mwk_20` — country-level weekly deaths

| code | description | geo level | verified |
|---|---|---|---|
| `demo_r_mwk_05` | Deaths by week, sex, 5-year age group | **country** (39 geos) | ✔ labelled as "NUTS" in brief but actually not |
| `demo_r_mwk_10` | Deaths by week, sex, 10-year age group | country | ✔ |
| `demo_r_mwk_20` | Deaths by week, sex, 20-year age group | country | ✔ |
| `demo_r_mwk2_ts` | Deaths by week, sex, NUTS-2 | NUTS-2 (438 geos) | ✔ |
| `demo_r_mwk_ts` | Deaths by week and sex | country | ✔ |

**Conclusion.** For NUTS-3 use **`demo_r_mweek3`** (or `demo_r_mwk3_t`). For NUTS-2 use **`demo_r_mwk2_ts`**. For country-level, use `demo_r_mwk_05`.

--------------------------------------------------------------------------------

## 12. CDC NCHS VSRR Socrata — `r8kw-7aab` **state-weekly with pre-computed `percent_of_expected_deaths`**

| field | value |
|---|---|
| Owner | CDC NCHS / Division of Vital Statistics |
| Dataset name | Provisional COVID-19 Death Counts by Week Ending Date and State |
| Socrata 4x4 | `r8kw-7aab` |
| JSON endpoint | https://data.cdc.gov/resource/r8kw-7aab.json |
| License | Public Domain — U.S. Government |
| Time range (verified 2026-04-09) | 2020-01-04 → 2026-04-04 |
| Row count | 22 194 |
| Spatial unit | US + 50 states + DC + territories |
| Temporal unit | MMWR week |

### Key columns

| column | content | notes |
|---|---|---|
| `data_as_of` | ETL timestamp | |
| `start_date`, `end_date` | MMWR week window | both ISO timestamps |
| `group` | `By Week`, `By Month`, `By Year` | **filter to `By Week`** |
| `year`, `mmwr_week` | MMWR calendar | |
| `week_ending_date` | Saturday of MMWR week | primary key with `state` |
| `state` | string incl. `United States`, state names, territories | |
| **`total_deaths`** | all-cause deaths that week | **the target** |
| `covid_19_deaths` | COVID u071 multi-cause | |
| **`percent_of_expected_deaths`** | CDC's own ratio (%) | pre-computed, **use as sanity check, not replacement** |
| `pneumonia_deaths`, `influenza_deaths`, `pneumonia_and_covid_19_deaths`, `pneumonia_influenza_or_covid_19_deaths` | | |
| `footnote` | suppression reason for sparse cells | string |

### Schema sample (verified)

```
data_as_of           2026-04-09T00:00:00.000
start_date           2019-12-29T00:00:00.000
end_date             2020-01-04T00:00:00.000
group                By Week
year                 2019/2020
mmwr_week            1
week_ending_date     2020-01-04T00:00:00.000
state                United States
covid_19_deaths      0
total_deaths         60170
percent_of_expected_deaths  98.00
```

### Gotchas

- **State, not city.** We join ERA5 at the state capital and treat the state
  as the unit. This loses a lot of signal (Phoenix vs Flagstaff within
  Arizona) — use CDC Wonder `ucd-icd10-expanded` for county resolution, but
  bear its **monthly** limit.
- **Starts 2020.** Pre-pandemic data lives in the sibling dataset
  `3yf8-kanr` (Weekly Counts of Deaths by State and Select Causes,
  2014–2019). The loader unions them for the 2014 → present target.
- `percent_of_expected_deaths` uses CDC's own Farrington-derived baseline with
  a rolling training window. Treat it as a **benchmark** for our custom
  baseline, not as the target.
- Dates are ISO timestamps with ".000" — parse as `pd.to_datetime`.
- Row suppression: cells where `total_deaths < 10` are reported as `null` with
  a `footnote` string explaining why. Check both.
- Socrata default page size is 1000; the loader pages at 50 000 like the
  building-permits loader.

--------------------------------------------------------------------------------

## 13. CDC NCHS Socrata — `3yf8-kanr` — **2014–2019 weekly by state, pre-pandemic**

| field | value |
|---|---|
| Owner | CDC NCHS |
| Dataset name | Weekly Counts of Deaths by State and Select Causes, 2014-2019 |
| Socrata 4x4 | `3yf8-kanr` |
| JSON | https://data.cdc.gov/resource/3yf8-kanr.json |
| Time range (verified) | 2014-01-04 → 2019-12-28 |
| Row count | 16 902 |
| Date column | `weekendingdate` (note: **no underscore** — unlike `muzy-jte6`) |
| All-cause column | `all__cause` (two underscores — Socrata mangled the space) |

### Schema sample

```
jurisdiction_of_occurrence  Florida
mmwryear                    2014
mmwrweek                    43
weekendingdate              2014-10-25T00:00:00.000
allcause                    3381
naturalcause                3149
...
```

### Gotcha

- Column names differ subtly from `r8kw-7aab`. The loader normalises both into
  the shared schema.

--------------------------------------------------------------------------------

## 14. CDC NCHS Socrata — `muzy-jte6` — 2020–2023 weekly by cause, state

| field | value |
|---|---|
| Dataset name | Weekly Provisional Counts of Deaths by State and Select Causes, 2020-2023 |
| Socrata 4x4 | `muzy-jte6` |
| Time range (verified) | 2020-01-04 → 2023-09-16 |
| Row count | 10 476 |

Use this for the *cause-of-death breakdown* (cardiovascular, respiratory,
neurological) — heat deaths tend to show up as cardiovascular and respiratory
secondary causes, so the breakdown is a useful feature.

--------------------------------------------------------------------------------

## 15. CDC WONDER `ucd-icd10-expanded` — **county-level but monthly, not weekly**

| field | value |
|---|---|
| Owner | CDC NCHS |
| Dataset | Underlying Cause of Death (Expanded), 2018–present |
| Landing | https://wonder.cdc.gov/ucd-icd10-expanded.html |
| Web form | Yes — returns CSV / tab-delimited after interactive query |
| API | CDC WONDER XML POST API at `https://wonder.cdc.gov/controller/datarequest/<DB>` **but** the docs state: *"for vital statistics only national data are available for query by the API"* — meaning **county and weekly slices cannot be retrieved programmatically** |
| Suppression rule (verified) | *"Do not present or publish death counts of 9 or fewer or death rates based on counts of nine or fewer"* — any cell with `< 10` deaths is returned as `"Suppressed"` |
| Time stratification | year, month, weekday — **no week-of-year** in the web form either |
| License | Public domain, but the DUA check-box is mandatory before every query |

### Implications for this project

- **County-weekly all-cause mortality is not openly available** for the US. The closest paths are:
  1. CDC Wonder web form pulls at the **monthly** level by county (manual, can be scripted via the XML POST but only for national totals). Convert monthly → weekly by proportional allocation — lossy.
  2. The **state-weekly** Socrata datasets (§12–§14). These give us weekly but only at state granularity.
  3. The **NCHS "Weekly counts" Socrata** dataset (§12) which already pre-aggregates at state-week level.
- For the wet-bulb hypothesis, **state-weekly is sufficient** for the baseline — we sacrifice spatial resolution but keep the temporal resolution that matters for heat waves. Higher-res analysis requires an access agreement with NCHS for the restricted-use files (out of scope for Phase 0).

--------------------------------------------------------------------------------

## 16. EuroMOMO — public bulletins only

| field | value |
|---|---|
| Owner | EuroMOMO / Statens Serum Institut (Denmark) |
| Landing | https://www.euromomo.eu |
| Data page | https://www.euromomo.eu/graphs-and-maps |
| License | Citation required ("EuroMOMO (euromomo.eu) 2026"), no redistribution |
| Time range | weekly, ~2015 → present (pooled), 2020-W16 → current in the interactive graphs |
| Download | interactive graphs expose a "Download data" button that returns CSV of the *plotted* subset; **there is no public bulk API** |
| Countries | 28 participating European countries + sub-national regions in a subset |
| Variables | **weekly z-scores only** (not raw counts) for all-ages and by age bucket (0-14, 15-44, 45-64, 65-74, 75-84, 85+, 65+) |
| Baseline method | Farrington-like 5-year historical with seasonal Fourier terms |

### Why we keep it

- The z-scores are the *canonical* European heat-health excess-mortality
  metric. Our baseline comparison table ("did the heat wave cause detectable
  excess mortality?") should report both our Eurostat-derived metric and the
  EuroMOMO z-score.

### Gotchas

- z-scores only, not counts; and only at country level, not NUTS-3.
- No API — the loader documents the manual download steps and caches whatever
  the user drops into `data/raw/euromomo/<country>.csv`.

--------------------------------------------------------------------------------

## 17. MoMo Spain (Instituto de Salud Carlos III)

| field | value |
|---|---|
| Owner | ISCIII |
| Landing | https://momo.isciii.es/public/momo/dashboard/momo_dashboard.html |
| Data | daily observed vs expected deaths by province |
| License | Open for academic use; cite ISCIII |
| Endpoint | Interactive dashboard; data not exposed as a documented REST API as of 2026-04-09 (probe timed out) |

Treated as an optional Phase 1 data source — sub-daily Spanish resolution is
a nice-to-have once the baseline is running.

--------------------------------------------------------------------------------

## 18. MCC Network (Multi-Country Multi-City Collaborative Research Network)

| field | value |
|---|---|
| Owner | Antonio Gasparrini et al., LSHTM |
| GitHub | https://github.com/gasparrini |
| Public pkgs | `dlnm`, `mixmeta`, `Extended2stage`, `CaseTimeSeries` — **R packages, not data** |
| Data status | The MCC *raw* mortality data are **not openly redistributable** — each paper's replication code contains *simulated* or aggregated versions, not the original city-day counts |

### What to actually do

- Use Gasparrini's R package `dlnm` and the Extended2stage model family as the
  *method* reference.
- Use their published attributable-fraction tables (in the papers) as
  validation benchmarks for our own predictions.
- Do **not** promise MCC data in the loader. Document that MCC access requires
  a data request to LSHTM and is out of scope for Phase 0.

--------------------------------------------------------------------------------

## 19. Eurostat `demo_r_pjanaggr3` — NUTS-3 population

| field | value |
|---|---|
| Code | `demo_r_pjanaggr3` |
| Label | "Population on 1 January by broad age group, sex and NUTS 3 region" |
| Verified 2026-04-09 | 2142 geos, code lengths {2, 3, 4, 5, 6, 9} |
| Age groups | `TOTAL`, `Y_LT15`, `Y15-64`, `Y_GE65`, `Y_GE80` |
| Time | annual, 1990 → 2024 for most regions |

Used for (a) converting weekly death counts to mortality rates per 100k and
(b) as a `Y_GE65` denominator for the age-stratified target.

--------------------------------------------------------------------------------

## 20. US Census — ACS 5-year county population

| field | value |
|---|---|
| Owner | US Census Bureau |
| Endpoint | `https://api.census.gov/data/<YEAR>/acs/acs5?get=B01003_001E,NAME&for=county:*&in=state:<FIPS>` |
| Verified 2026-04-09 | 2019 PEP and 2022 ACS-5 both return CA county population |
| License | Public domain |
| Auth | Optional Census API key (free, speeds up 500+ req/day) |

Used for the US `population` column. `B01003_001E` is total population; for
age-stratified baselines use `B01001_020E` through `B01001_049E` (65+ male/female).

--------------------------------------------------------------------------------

## 21. Cities-by-lat-lon

Inline Python dict in `data_loaders.CITIES`. 60 cities total (30 US + 30 EU),
lat-lon to 4 decimal places, plus NUTS-3 code (EU) or FIPS state+county (US),
plus ISD primary + fallback station IDs and GHCN-D station IDs. See the
`CITIES` dict at the top of `data_loaders.py`.

--------------------------------------------------------------------------------

## Summary — what is runnable right now

| source | city-resolution exposure for US? | city-resolution exposure for EU? | auth needed? |
|---|---|---|---|
| ERA5 single levels | yes (0.25°) | yes (0.25°) | **CDS account + accept terms** |
| ERA5-Land | yes (0.1°) | yes (0.1°) | CDS account |
| GHCN-D TMAX/TMIN/ADPT/AWBT/RHAV | **yes** — dewpoint and wet-bulb direct | **no** — dry-bulb only | no |
| ISD hourly TMP+DEW | yes | **yes** — the hero for EU night-time wet-bulb | no |
| Eurostat weekly deaths NUTS-3 | — | yes (2013 →) | no |
| CDC Socrata weekly deaths | **state-level only** (2014 →) | — | no |
| NWS HeatRisk archive | yes (2024-08 →) | — | no |
| Storm Events Heat | yes (1996 → present) | — | no |

**Runnable without any auth today**: GHCN-D + ISD + Eurostat + CDC Socrata +
Storm Events + HeatRisk-recent. This is enough to train a Phase 0.5 baseline.
ERA5 is the upgrade path once the CDS account is ready.
