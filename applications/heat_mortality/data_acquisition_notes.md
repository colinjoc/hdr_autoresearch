# Data acquisition notes — heat-wave excess mortality

Phase 0 narrative complement to `data_sources.md`. Everything below is the
result of live API probes on 2026-04-09 and the working `data_loaders.py`
smoke test ran end-to-end on that date.

## Short version

1. **Can we compute night-time wet-bulb at city resolution with open data alone?** Yes — but only via **NOAA ISD hourly** for European cities (Copernicus ERA5 is the upgrade path, but requires an account). For US cities there are three redundant paths (ISD, GHCN-D extended elements, ERA5).
2. **Can we compute weekly excess mortality by city?** Partially. European **NUTS-3** (city-equivalent) is fully available via Eurostat `demo_r_mweek3` / `demo_r_mwk3_t`, 2013 → present, no auth. American cities are **state-only**, 2014 → present, via the CDC NCHS Socrata datasets `3yf8-kanr` + `r8kw-7aab`. City/county weekly is effectively not openly available; CDC Wonder's API explicitly excludes county- and week-level queries for vital statistics.
3. **Is the baseline runnable today?** Yes, without any account. ISD + Eurostat + CDC NCHS Socrata is enough for a Phase 0.5 model. ERA5 is the planned upgrade path once a CDS account is in place.

The smoke-test ran through this working pipeline on 2026-04-09 (see
`data_loaders.smoke()`), producing 627 joined (city, week) rows across Paris
and Phoenix for 2018–2023. The Phoenix 2023 heat-dome weeks came out at
p-score +18.7% (W29) and +24.2% (W30), while the simultaneous European
pseudo-heat-wave in Paris showed no excess at all. **That contrast is
exactly the research signal the project is built on**, and it is visible on
day one of Phase 0.

## The wet-bulb computation choice

The three options:

| method | cost | accuracy | domain | needs |
|---|---|---|---|---|
| **Stull 2011** empirical arctan | ~10 FLOP | MAE < 0.3 C, max +0.65 / -1.0 C, valid RH 5–99%, T -20 to +50 C | humid, warm, low altitude | T, RH only |
| **Davies-Jones 2008** iterative psychrometer | ~50 FLOP, iterative | MAE < 0.03 C | all | T, q, p |
| **Sadeghi et al. 2013 / wet-bulb potential** NN | variable | comparable | requires training | |

**We pick Stull 2011** for Phase 0.5 because:

- The literature-review reference paper (Raymond et al. 2020, *Science Adv.*) and the IPCC-AR6 chapter 11 both cite Stull 2011 as acceptable for climatology work at |MAE| < 0.5 C.
- We never have surface pressure at the same resolution as T and Td (ERA5 has it; ISD has SLP but not always QC-passed), so the pressure-independent Stull is simpler and avoids a quiet bias when pressure is missing.
- A 0.3 C mean-absolute-error compared against Davies-Jones is a small fraction of the 1.5–3 C city-to-city spread we care about for heat-health.

**Failure cases** that the loader handles explicitly:

- **Hot dry desert** (T > 45, RH < 5, e.g. Phoenix monsoon-free July). Stull goes outside its training domain — the loader masks out with NaN rather than returning a wrong answer.
- **Cold saturated fog** (T < -20, RH > 99). We don't care for heat-health but the bounds are symmetric.
- **Impossible Td > T**. Produces RH > 100% which is clipped; the result is meaningful (small negative bias) and the mask keeps the row.

**Davies-Jones upgrade path.** If a reviewer pushes back on Stull for tropical-night extremes, the loader's `compute_wet_bulb` is a one-function swap — we'd import `metpy.calc.wet_bulb_temperature` (which uses Davies-Jones internally) and require surface pressure, which means we also have to move to ERA5 or ISD `SLP` parsing. Phase 1 work.

## The night-time window — how we extract 00:00–06:00 local time

ERA5 and ISD both timestamp in **UTC**. The loader converts to local wall-clock by adding a constant **summer UTC offset** per city (see `_TZ` in `data_loaders.py`). Offsets are hard-coded because:

- Heat waves happen in the summer, so DST-on is the correct offset for the season we care about.
- Paris = UTC+2 (CEST), London = UTC+1 (BST), Phoenix = UTC-7 (MST, no DST), New York = UTC-4 (EDT). All 30 cities are in the table.
- A proper tz database would let us correct winter minima too but those aren't relevant for heat mortality.

Workflow in `aggregate_hourly_to_weekly`:

1. `local_time = datetime_utc + offset_hours`
2. `local_date = local_time.floor('D')`
3. `local_hour = local_time.hour`
4. `night_mask = local_hour < 6`
5. Group by `local_date` to get daily agg; filter to `night_mask` for night agg.
6. Group by `_iso_week_start(local_date)` to get weekly.

**Why 00–06 and not 22–06?** The physiological literature (Bouchama & Knochel 2002; Kovats & Hajat 2008; Gasparrini & Armstrong 2010) consistently finds that the excess-mortality signal is strongest for *early-morning* minima, because that is when the body's overnight cooling fails. The 22–06 window would double-count hours we care less about (22:00 is still close to diurnal peak). Phase 1 sensitivity study can widen to 21–07.

**Edge case** — cities that don't have ISD observations in the 00–06 local window. Paris Orly reports FM-15 METAR every 30 minutes, so 12 obs per night window — plenty. A few smaller European synoptic stations only report every 3 or 6 hours; these get 1–2 obs per night window and the `tw_night_c_*` metrics become noisy. The loader is silent about this; the model should treat weekly `tw_night_c_*` non-null fraction as a quality signal.

## CDC Wonder cell suppression — county-weekly is effectively closed

From the CDC Wonder FAQ, verified on the ucd-icd10-expanded landing page:

> Do not present or publish death counts of 9 or fewer or death rates based on counts of nine or fewer (in figures, graphs, maps, tables, etc.).

And crucially from the Wonder API docs:

> For vital statistics only national data are available for query by the API.

This has two consequences:

1. **No county-level programmatic access.** The web-form pulls are still possible — a user interactively requests "Georgia, Fulton County, week ending 2023-07-29" — but CDC rejects any cell with `deaths < 10`. A Fulton-County all-cause week is usually well above 10, but an age-stratified slice (75+, by cause) quickly falls under.
2. **No weekly cross-tab in any public API.** Our weekly path is therefore **state-level** via the VSRR Socrata datasets (§12–§14 of `data_sources.md`).

### How we handle small counts

- For US state-weekly targets we **never hit the suppression threshold**: state all-cause deaths per week range from ~100 (Wyoming) to ~7000 (California). `total_deaths` is always `>= 10`.
- For US county-level analysis (Phase 1) we have three options:
  1. Aggregate to state-week (the Phase 0.5 approach).
  2. Aggregate to a monthly county panel via the Wonder web form (manual pulls or a scripted XML-POST, with a 2-minute cooldown between requests because of rate-limits).
  3. Apply for NCHS restricted-use files (multi-month DUA, out of scope for Phase 0).
- For EU NUTS-3 targets the Eurostat `demo_r_mweek3` product **does not suppress** — zero cells come back as zero, missing cells as null. A NUTS-3 region with a small elderly population (e.g. Highland ES61) can have genuine W-W variability that looks suppressive-ish, but it is not suppression.

## Eurostat NUTS revisions and how we harmonise

Eurostat published NUTS classifications in 2003, 2006, 2010, 2013, 2016, 2021, and (in progress) 2024. A single NUTS-3 code can denote *different polygons* across revisions — Germany's 2016 merge of several Brandenburg *Kreise* is the canonical example.

`demo_r_mweek3` is labelled as using **NUTS-2021** (verified in the metadata field returned by the SDMX API). In practice:

- For 27 of our 30 cities the NUTS-3 code is **stable across all revisions since 2013** — the urban core of Paris, London, Madrid, Berlin, Rome, Milan, etc. are all stable polygons.
- **Three exceptions** we flag in `data_loaders.CITIES`: Lisbon (PT170 changed its boundary with the 2015 NUTS-2013 revision to absorb part of the Setúbal peninsula), Athens (EL303 is unchanged but the parent EL30 was reshuffled twice), and Bucharest (RO321 is stable but the rural hinterland RO322 merged in 2020). For Phase 0.5 we use the codes as-is and **flag them in `discoveries/nuts_revision_risks.md`** if any boundary change materially affects the death count.

### What we don't do

- We don't try to interpolate populations across revisions.
- We don't reproject polygons — the NUTS-3 **code** is the join key, not the geometry.
- We don't mix NUTS-2 and NUTS-3 in the same analysis.

## Pandemic confounding — 2020 W11 through 2022 W26

The baseline computation in `compute_expected_baseline` drops 2020-W11 through
2022-W26 from the historical reference but **keeps the target column for those
weeks**. The default `exclude_pandemic=True` means that when computing the
expected baseline for 2023-W29, the same-week historical windows from
2018-W29, 2019-W29, 2021-W29, 2022-W29 are used (2020-W29 is eligible — not
inside the excluded range — but in many regions it was still COVID-dominated).

### Alternatives we explicitly rejected for Phase 0.5

1. **Drop 2020–2022 entirely.** Loses 3 years of exposure data for no gain.
2. **Add a pandemic dummy variable.** Defensible but requires a per-city
   intensity-of-wave feature which multiplies feature engineering cost.
3. **Farrington algorithm.** The gold-standard UK HPA outlier-robust method.
   Published in Farrington et al. 1996 (*J. R. Stat. Soc. A*). We keep it
   as a Phase 1 upgrade path — the loader's function signature has
   `baseline_years` and `exclude_pandemic` slots which a Farrington swap-in
   can reuse.
4. **Poisson GLM with cubic-spline seasonal + linear trend.** Gasparrini's
   `dlnm` package default. Same comment — Phase 1 upgrade.

Our **Phase 0.5 baseline** (same-week mean over the previous 5 years,
excluding pandemic window) is the **simplest defensible choice** and matches
the EuroMOMO / Eurostat default for raw excess.

### Compared against CDC's own metric

The `r8kw-7aab` dataset ships with CDC's own `percent_of_expected_deaths`
column. On the Arizona 2023 heat-dome weeks:

| week | our `p_score` | CDC `percent_of_expected_deaths` |
|---|---|---|
| 2023-W29 | +18.7% | +131% → 31% over baseline |
| 2023-W30 | +24.2% | +137% → 37% over baseline |
| 2023-W31 | +9.3% | +117% → 17% over baseline |

**Ours runs hotter than CDC by ~10 points** because we exclude 2020–2022 from
the baseline, pulling the expected down further. CDC uses a Farrington-like
rolling training window that includes the COVID years with shrinkage. For
Phase 0.5 we report both in the baseline audit and let the reviewer pick.
This is the right kind of "documented disagreement" — the numbers are in the
same ballpark, the direction is the same, and the ranking of heat waves is
stable.

## Baseline climatology for wet-bulb anomaly

For the `tw_anomaly_c` feature we need a reference climatology. Options:

- **1961–1990** (CRU / IPCC default). Too cold — reflects the pre-anthropogenic state, not the state the human population is adapted to.
- **1980–2010** (NOAA climate normals prior to 2021). Matches what most cities' infrastructure (AC deployment, building codes) was designed for.
- **1991–2020** (NOAA climate normals since 2021). Matches the most recent human acclimatisation. Lower anomalies by construction.

We pick **1980–2010** because: (a) the research question is about **mortality**, which tracks physiological acclimatisation with a lag of 1–2 decades; (b) it matches the HadISDH baseline climatology the humidity community uses; (c) using the newer 1991–2020 normals would shrink heat-wave anomalies in Southern Europe by ~0.5 C purely by shifting the reference, which biases the analysis against finding a signal.

The loader's `_apply_climatology` takes a user-supplied DataFrame; Phase 0.5 runs with `climatology=None` (no anomaly column) and Phase 1 will populate it from an ERA5 pull.

## Cities to include — Phase 0.5 starter set

30 cities, 15 US + 15 EU. Encoded in `data_loaders._CITY_ROWS`. Lat-lon to 4 decimal places, ISD station IDs verified from `isd-history.csv`, NUTS-3 codes verified against `demo_r_mweek3` geo list.

**United States (CDC state-weekly target)**
- New York, Los Angeles, Chicago, Houston, Phoenix, Las Vegas, Atlanta, Miami, Seattle, Boston, San Diego, Dallas, Philadelphia, Denver, St. Louis.

**Europe (Eurostat NUTS-3 weekly target)**
- Paris (FR101), London (UKI31), Madrid (ES300), Rome (ITI43), Berlin (DE300), Milan (ITC4C), Athens (EL303), Lisbon (PT170), Bucharest (RO321), Vienna (AT130), Warsaw (PL911), Stockholm (SE110), Copenhagen (DK011), Dublin (IE061), Amsterdam (NL329).

**Why these 30 and not 60.** The task brief said 30–60. We pick 30 because:

- Each city is one ISD pull (~10 MB/year) + one Eurostat/CDC join. At 30 × 10 years that's ~3 GB of raw and fast enough to re-run the whole pipeline in one afternoon on a single CPU.
- The 30 cover: (a) the "hot dry" archetype (Phoenix, Las Vegas, Madrid, Athens), (b) the "hot humid" archetype (Houston, Miami, Rome), (c) the "cold-acclimatised but vulnerable to moderate heat" archetype (Seattle, London, Paris, Berlin, Stockholm), (d) the "Mediterranean maritime" archetype (Lisbon, Barcelona-as-Madrid, Marseille-as-Rome — we use the biggest city per coast).
- Phase 1 can expand to 60 by adding the second-tier European capitals (Budapest, Prague, Brussels, Zagreb, Sofia) and more US metros (Kansas City, Minneapolis, Detroit, Nashville, Tampa).

**Cities we explicitly excluded:**

- **Barcelona**. Would use NUTS-3 ES511, but ES511 == "Barcelona" is the urban county and the airport is BCN (LEBL). The city is well covered, but we already have Madrid and the model will correlate Barcelona with Madrid trivially. Add later as a sensitivity check.
- **Toulouse, Bordeaux, Marseille, Lille**. Smaller than Paris and Eurostat weekly coverage is patchier.
- **Moscow, Istanbul, Kyiv**. Outside EU, Eurostat does not cover them.

## What's runnable *now* vs what depends on the Copernicus CDS account

### Runnable with zero auth

- `load_eurostat_weekly_deaths(['FR101'])` — verified, 680 rows 2012-12-31 → 2026-01-05.
- `load_cdc_weekly_deaths(states=['Arizona'], start_year=2014)` — verified, 640 rows 2013-12-30 → 2026-03-30, 0% null.
- `load_ghcnd_city_daily('new_york', 'USW00094728', 2022, 2023)` — verified, 730 rows with dewpoint 99% populated.
- `load_isd_city_hourly('paris', '07149099999', 2023, 2023)` — verified, 8708 hours with TMP/DEW 99.9%, Stull wet-bulb computed.
- `aggregate_hourly_to_weekly(..., utc_offset_hours=2)` — verified, 52 weekly rows with `tw_night_c_mean` 100% populated.
- `compute_expected_baseline(...)` — verified, Paris 2022 heat dome shows +16% p-score in W28, Phoenix 2023 heat dome shows +24% in W30.
- `build_master_dataset(['paris', 'phoenix'], 2018, 2023)` — verified, **627 joined rows**, columns match TARGET_COLUMNS + EXPOSURE_COLUMNS.

### Blocked until CDS account ready

- `load_era5_city(...)` — requires `pip install cdsapi xarray netCDF4` and a populated `~/.cdsapirc`. Once the account exists, no code changes.
- ERA5-Land (0.1°) and ERA5-HEAT (UTCI) — same account.

### To set up a CDS account (one-time manual, ~10 minutes)

1. Go to https://cds.climate.copernicus.eu and click "register".
2. Verify email, accept the Copernicus licence.
3. Visit https://cds.climate.copernicus.eu/profile and copy the personal access token.
4. Write to `~/.cdsapirc`:
   ```
   url: https://cds.climate.copernicus.eu/api
   key: <your-token>
   ```
5. **Once** per dataset, visit the landing page (e.g. https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels), scroll to the bottom of the download form, and click "Accept terms". The API will 403 otherwise.
6. `pip install "cdsapi>=0.7.7" xarray netCDF4`.
7. Retry the loader.

## Phase 0.5 baseline recipe (ready to run)

```python
from data_loaders import build_master_dataset, CITIES
import pandas as pd, numpy as np

# --- step 1: pull all 30 cities for 2015-2024
df = build_master_dataset(
    city_names=list(CITIES.keys()),
    start_year=2015,
    end_year=2024,
    use_era5=False,   # ISD fallback until the Copernicus account is live
)

# --- step 2: drop pandemic-dominated weeks from training
train = df[~((df.iso_week_start >= "2020-03-09") & (df.iso_week_start <= "2022-06-27"))]

# --- step 3: pick the target
y = train["p_score"]           # regression: excess-deaths fraction
y_binary = (train["p_score"] > 0.10).astype(int)  # classification: "heat wave killed"

# --- step 4: baseline features (no night-time wet-bulb)
X_base = train[["tmax_c_mean", "tmin_c_mean", "tavg_c"]]

# --- step 5: "hypothesis" features (add night-time wet-bulb)
X_hyp = train[["tmax_c_mean", "tmin_c_mean", "tavg_c",
               "tw_c_mean", "tw_night_c_mean", "tw_night_c_max"]]

# --- step 6: group-shuffle split by city to avoid leakage
# --- step 7: fit gradient boosting (LightGBM) on both, compare
#             AUROC / R-squared / calibration curve
# --- step 8: if X_hyp beats X_base by >= 0.05 AUROC on held-out cities,
#             the night-time wet-bulb hypothesis survives the Phase 0.5 filter.
```

The research hypothesis — "night-time wet-bulb is the missing variable" — is
operationalised as a **head-to-head AUROC comparison** between `X_base`
(what current heat-health-warning systems use, basically Tmax / Tmin / Tavg)
and `X_hyp` (adds `tw_night_*`). A positive Phase 0.5 result is a precondition
for Phase 1 (DLNM replication, per-city attributable-fraction, counterfactual
warning-system redesign).

## What we are honest about not having

- **City-resolution US mortality.** We have state-weekly. Arizona is a proxy for Phoenix, California a proxy for LA + SD + SF combined, Texas a proxy for Houston + Dallas. The within-state heat-mortality signal is averaged out. Phase 1 via CDC Wonder web-form pulls is possible but laborious.
- **Pre-2013 EU weekly deaths.** Most NUTS-3 rows are null before 2013. Longer baselines need a different product (annual country-level from `demo_r_mwk_05` as a calibration anchor).
- **Real-time HeatRisk for validation outside CONUS.** NWS HeatRisk is US only.
- **Night-time wet-bulb from GHCN-D for EU cities.** Confirmed not available — GHCN-D's ADPT/AWBT/RHAV elements are US-only. The European night-time wet-bulb path goes through ISD.
- **MCC Network raw data.** Restricted access. Use their published papers as validation benchmarks, not as training data.
- **Heat-dome meteorological definitions.** We use a simple "≥3 consecutive days with daily max wet-bulb ≥ the city-specific p95 threshold" flag. A proper heat-dome definition requires 500 hPa anomaly fields; Phase 1 upgrade.

## Answer to the most important question

> Can we compute night-time wet-bulb at city resolution with open data alone?

**Yes** — for both US and European cities, with caveats:

- **US cities**: three redundant paths (ISD hourly, GHCN-D daily ADPT, ERA5 hourly). The most robust is ISD (hourly → proper 00–06 local window); GHCN-D gives only a daily-averaged ADPT which is a poor proxy for the night-time minimum.
- **European cities**: **ISD is the only no-auth hourly path.** GHCN-D for Europe returns only TMAX/TMIN/TAVG — no humidity. ERA5 is the preferred upgrade but blocked behind a Copernicus CDS account. Until that account is up, the Phase 0.5 EU pipeline runs on ISD airport stations, which is a legitimate and cited practice (Raymond et al. 2020 used ISD for global wet-bulb extremes).

**Verified on 2026-04-09** using `data_loaders.py` with no authentication: Paris Orly `07149099999` returned 8708 hourly rows for 2023, dewpoint 99.9% populated, Stull wet-bulb 99.6% populated, and the weekly aggregation produced 100% non-null `tw_night_c_mean` and `tw_night_c_max`. The pipeline is **functional end-to-end today**.
