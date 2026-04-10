"""Heat-mortality open-data loaders. One row per (city, iso_week_start).
APIs verified live 2026-04-09; URLs and gotchas in data_sources.md."""
from __future__ import annotations
import csv, io, os
from pathlib import Path
from typing import Dict, List, Optional, Sequence
import numpy as np
import pandas as pd
import requests

# --------------------------------- schema
TARGET_COLUMNS = [
    "city", "country", "lat", "lon", "iso_week_start", "iso_year_week",
    "deaths_all_cause", "expected_baseline", "excess_deaths",
    "p_score", "population", "age_group",
]
EXPOSURE_COLUMNS = [
    "city", "iso_week_start",
    "tmax_c_mean", "tmax_c_max", "tmin_c_mean", "tavg_c", "tdew_c",
    "tw_c_mean", "tw_c_max", "tw_night_c_mean", "tw_night_c_max",
    "tw_anomaly_c", "heat_dome_flag", "consecutive_days_above_p95",
]
RAW_DIR = Path(__file__).parent / "data" / "raw"
for _sub in ("era5", "isd", "ghcnd", "eurostat", "cdc"):
    (RAW_DIR / _sub).mkdir(parents=True, exist_ok=True)
SESSION = requests.Session()
SESSION.headers["User-Agent"] = "hdr-heat-mortality/0.1"
if os.environ.get("SOCRATA_APP_TOKEN"):
    SESSION.headers["X-App-Token"] = os.environ["SOCRATA_APP_TOKEN"]

# city inventory — fields: name, country, lat, lon, ghcnd, isd, nuts3_or_state.
# Verified on NCEI isd-history.csv and Eurostat NUTS-2021 on 2026-04-09.
_CITY_ROWS = [
    ("new_york","US",40.7831,-73.9712,"USW00094728","72505394728","New York"),
    ("los_angeles","US",34.0522,-118.2437,"USW00023174","72295023174","California"),
    ("chicago","US",41.8781,-87.6298,"USW00094846","72530094846","Illinois"),
    ("houston","US",29.7604,-95.3698,"USW00012960","72243012960","Texas"),
    ("phoenix","US",33.4484,-112.074,"USW00023183","72278023183","Arizona"),
    ("las_vegas","US",36.1699,-115.1398,"USW00023169","72386023169","Nevada"),
    ("atlanta","US",33.749,-84.388,"USW00013874","72219013874","Georgia"),
    ("miami","US",25.7617,-80.1918,"USW00012839","72202012839","Florida"),
    ("seattle","US",47.6062,-122.3321,"USW00024233","72793024233","Washington"),
    ("boston","US",42.3601,-71.0589,"USW00014739","72509014739","Massachusetts"),
    ("san_diego","US",32.7157,-117.1611,"USW00023188","72290023188","California"),
    ("dallas","US",32.7767,-96.797,"USW00013960","72259003927","Texas"),
    ("philadelphia","US",39.9526,-75.1652,"USW00013739","72408013739","Pennsylvania"),
    ("denver","US",39.7392,-104.9903,"USW00003017","72565003017","Colorado"),
    ("st_louis","US",38.627,-90.1994,"USW00013994","72434013994","Missouri"),
    ("paris","FR",48.8566,2.3522,None,"07149099999","FR101"),
    ("london","GB",51.5074,-0.1278,None,"03772099999","UKI31"),
    ("madrid","ES",40.4168,-3.7038,None,"08221099999","ES300"),
    ("rome","IT",41.9028,12.4964,None,"16242099999","ITI43"),
    ("berlin","DE",52.52,13.405,None,"10385099999","DE3"),
    ("milan","IT",45.4642,9.19,None,"16080099999","ITC4C"),
    ("athens","GR",37.9838,23.7275,None,"16716099999","EL303"),
    ("lisbon","PT",38.7223,-9.1393,None,"08536099999","PT170"),
    ("bucharest","RO",44.4268,26.1025,None,"15420099999","RO321"),
    ("vienna","AT",48.2082,16.3738,None,"11035099999","AT130"),
    ("warsaw","PL",52.2297,21.0122,None,"12375099999","PL911"),
    ("stockholm","SE",59.3293,18.0686,None,"02462099999","SE110"),
    ("copenhagen","DK",55.6761,12.5683,None,"06180099999","DK011"),
    ("dublin","IE",53.3498,-6.2603,None,"03969099999","IE0"),
    ("amsterdam","NL",52.3676,4.9041,None,"06240099999","NL329"),
]

class City:
    __slots__ = ("name","country","lat","lon","ghcnd_station","isd_usaf_wban","nuts3","us_state")
    def __init__(self, name, country, lat, lon, ghcnd, isd, last):
        self.name, self.country, self.lat, self.lon = name, country, lat, lon
        self.ghcnd_station, self.isd_usaf_wban = ghcnd, isd
        self.nuts3, self.us_state = (None, last) if country == "US" else (last, None)
CITIES: Dict[str, City] = {r[0]: City(*r) for r in _CITY_ROWS}
_TZ: Dict[str, int] = {  # summer UTC offset hours
    "California": -7, "New York": -4, "Illinois": -5, "Texas": -5,
    "Arizona": -7, "Nevada": -7, "Georgia": -4, "Florida": -4,
    "Washington": -7, "Massachusetts": -4, "Pennsylvania": -4,
    "Colorado": -6, "Missouri": -5,
    "FR": 2, "GB": 1, "ES": 2, "IT": 2, "DE": 2, "GR": 3, "PT": 1,
    "RO": 3, "AT": 2, "PL": 2, "SE": 2, "DK": 2, "IE": 1, "NL": 2,
}
def _utc_offset(c: City) -> int:
    if c.country == "US":
        return _TZ.get(c.us_state or "", -5)
    return _TZ.get(c.country, 1)

# --------------------------------- Stull 2011 wet-bulb
def compute_wet_bulb(t2m_c, td2m_c):
    """Wet-bulb (C) from air temp + dewpoint (C), Stull 2011 JAMC 50(11).
    Arctan fit valid for RH in [5,99]%, T in [-20,+50] C; MAE<0.3C, max
    +0.65/-1.0 C. Td -> RH via Alduchov-Eskridge Magnus. OOB -> NaN."""
    t = np.asarray(t2m_c, dtype=float); td = np.asarray(td2m_c, dtype=float)
    a, b = 17.625, 243.04
    rh = np.clip(100.0 * np.exp(a*td/(b+td)) / np.exp(a*t/(b+t)), 1e-6, 100.0)
    tw = (t * np.arctan(0.151977 * np.sqrt(rh + 8.313659))
          + np.arctan(t + rh) - np.arctan(rh - 1.676331)
          + 0.00391838 * np.power(rh, 1.5) * np.arctan(0.023101 * rh)
          - 4.686035)
    return np.where((t < -20) | (t > 50) | (rh < 5) | (rh > 99), np.nan, tw)

# --------------------------------- ISO-week helpers
def _iso_week_start(d):
    d = pd.to_datetime(d)
    return (d - pd.to_timedelta(d.dt.isocalendar().day - 1, unit="D")).dt.normalize()

def _iso_year_week(d):
    iso = pd.to_datetime(d).dt.isocalendar()
    return iso.year.astype(str) + "-W" + iso.week.astype(str).str.zfill(2)

# --------------------------------- Eurostat JSON-stat
_EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

def _eurostat_unflatten(resp: dict) -> pd.DataFrame:
    dims = resp["id"]; sizes = resp["size"]
    codes = [sorted(resp["dimension"][d]["category"]["index"].items(),
                    key=lambda kv: kv[1]) for d in dims]
    strides = [1] * len(sizes)
    for i in range(len(sizes) - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]
    values = resp.get("value", {})
    if isinstance(values, list):
        values = {str(i): v for i, v in enumerate(values) if v is not None}
    rows = []
    for k, v in values.items():
        flat = int(k); row = {}
        for d, code_list, stride in zip(dims, codes, strides):
            row[d] = code_list[(flat // stride) % len(code_list)][0]
        row["value"] = v
        rows.append(row)
    return pd.DataFrame(rows)

def load_eurostat_weekly_deaths(
    nuts_codes: Sequence[str], dataset: str = "demo_r_mwk3_t",
    sex: str = "T", age: Optional[str] = None, force: bool = False,
) -> pd.DataFrame:
    """Weekly all-cause deaths for NUTS-3 codes. Default `demo_r_mwk3_t`
    is total-only (sex=T). For age-stratified pass `dataset='demo_r_mweek3'`
    and `age='TOTAL'` / `'Y_GE65'`. Verified 2026-04-09: FR101 returns 680
    non-null weeks from 2013-W01. (Task brief said `demo_r_mwk_05` but
    that dataset is country-level, not NUTS-3.)

    Cache is a union: when ``cache`` exists but doesn't hold every requested
    NUTS code, the missing codes are fetched and merged in. This lets Phase
    0.5 grow the panel city-by-city without refetching the whole dataset.
    """
    cache = RAW_DIR / "eurostat" / f"{dataset}_{sex}_{age or 'none'}.parquet"
    cached_df = pd.DataFrame()
    if cache.exists() and not force:
        cached_df = pd.read_parquet(cache)
        have = set(cached_df.get("nuts_code", pd.Series(dtype=str)).unique())
        missing = [g for g in nuts_codes if g not in have]
        if not missing:
            return cached_df[cached_df["nuts_code"].isin(list(nuts_codes))].copy()
    else:
        missing = list(nuts_codes)
    frames: List[pd.DataFrame] = []
    has_sexage = dataset != "demo_r_mwk3_t"
    import time as _time
    for geo in missing:
        p = {"format": "JSON", "lang": "EN", "geo": geo}
        if has_sexage:
            p["sex"] = sex
            if age is not None:
                p["age"] = age
        # Retry with exponential backoff on 413/429/5xx transient errors.
        last_status = None
        resp = None
        for attempt in range(4):
            r = SESSION.get(f"{_EUROSTAT}/{dataset}", params=p, timeout=90)
            last_status = r.status_code
            if r.status_code == 200:
                resp = r
                break
            if r.status_code in (413, 429, 500, 502, 503, 504):
                _time.sleep(2 * (attempt + 1))
                continue
            break
        if resp is None:
            print(f"  eurostat {dataset} {geo}: {last_status}")
            continue
        df = _eurostat_unflatten(resp.json())
        if df.empty:
            continue
        frames.append(df[df["value"].notna()])
        _time.sleep(0.3)  # gentle rate-limit
    if not frames and cached_df.empty:
        return pd.DataFrame(columns=TARGET_COLUMNS + ["nuts_code"])
    fetched = pd.DataFrame()
    if frames:
        fetched = pd.concat(frames, ignore_index=True)
        # '2023-W28' + '-1' -> '2023-W28-1' (ISO Monday) via %G-W%V-%u.
        fetched["iso_week_start"] = pd.to_datetime(fetched["time"] + "-1",
            format="%G-W%V-%u", errors="coerce")
        fetched["iso_year_week"] = fetched["time"]
        fetched = fetched.rename(columns={"value": "deaths_all_cause", "geo": "nuts_code"})
        fetched["deaths_all_cause"] = pd.to_numeric(fetched["deaths_all_cause"], errors="coerce")
        fetched["age_group"] = fetched.get("age", "all")
    # Union with any prior cache.
    if not cached_df.empty and not fetched.empty:
        out = pd.concat([cached_df, fetched], ignore_index=True)
        # Align columns across the union so parquet is happy.
        common = [c for c in cached_df.columns if c in fetched.columns]
        out = out[common + [c for c in out.columns if c not in common]]
        out = out.drop_duplicates(subset=["nuts_code", "iso_year_week"], keep="last")
    elif not fetched.empty:
        out = fetched
    else:
        out = cached_df
    out.to_parquet(cache, index=False)
    return out[out["nuts_code"].isin(list(nuts_codes))].copy()

# --------------------------------- CDC NCHS Socrata
def _soda_get(url: str, where: Optional[str] = None) -> List[dict]:
    rows: List[dict] = []
    page, offset = 50_000, 0
    while True:
        p: Dict[str, object] = {"$limit": page, "$offset": offset}
        if where:
            p["$where"] = where
        r = SESSION.get(url, params=p, timeout=120)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch); offset += len(batch)
        if len(batch) < page:
            break
    return rows

def load_cdc_weekly_deaths(
    states: Optional[Sequence[str]] = None,
    start_year: int = 2014, force: bool = False,
) -> pd.DataFrame:
    """Union of `3yf8-kanr` (2014-2019) + `r8kw-7aab` (2020-present).
    Row counts verified 2026-04-09: 16902 + 22194. CDC's
    `percent_of_expected_deaths` is preserved for the 2020+ rows."""
    cache = RAW_DIR / "cdc" / "weekly_deaths_state.parquet"
    if not cache.exists() or force:
        old = pd.DataFrame(_soda_get("https://data.cdc.gov/resource/3yf8-kanr.json")).rename(
            columns={"jurisdiction_of_occurrence": "state",
                     "weekendingdate": "week_ending_date",
                     "allcause": "total_deaths"})
        old["percent_of_expected_deaths"] = None
        new = pd.DataFrame(_soda_get(  # `group` is a SoQL reserved word -> backticks
            "https://data.cdc.gov/resource/r8kw-7aab.json",
            where="`group`='By Week'"))
        cols = ["state", "week_ending_date", "total_deaths", "percent_of_expected_deaths"]
        df = pd.concat([old[cols], new[cols]], ignore_index=True)
        df["week_ending_date"] = pd.to_datetime(df["week_ending_date"], errors="coerce")
        for c in ("total_deaths", "percent_of_expected_deaths"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df.to_parquet(cache, index=False)
    df = pd.read_parquet(cache)
    df = df[df["week_ending_date"].dt.year >= start_year].copy()
    if states is not None:
        df = df[df["state"].isin(list(states))]
    # MMWR week ends Saturday; iso_week_start is the Monday 5 days earlier.
    df["iso_week_start"] = df["week_ending_date"] - pd.to_timedelta(5, unit="D")
    df["iso_year_week"] = _iso_year_week(df["iso_week_start"])
    df = df.rename(columns={"total_deaths": "deaths_all_cause"})
    df["age_group"] = "all"
    return df.reset_index(drop=True)

# --------------------------------- GHCN-Daily
_GHCND_API = "https://www.ncei.noaa.gov/access/services/data/v1"

def load_ghcnd_city_daily(
    city: str, station_id: str, start_year: int, end_year: int,
    elements: Sequence[str] = ("TMAX", "TMIN", "TAVG", "ADPT", "AWBT", "RHAV"),
    force: bool = False,
) -> pd.DataFrame:
    """Daily GHCN-D. Tenths-of-degC -> degC. ADPT/AWBT/RHAV are US-only
    (verified 2026-04-09: US stations populated, EU stations empty)."""
    cache = RAW_DIR / "ghcnd" / f"{city}_{station_id}_{start_year}_{end_year}.parquet"
    if cache.exists() and not force:
        return pd.read_parquet(cache)
    p = {
        "dataset": "daily-summaries", "stations": station_id,
        "startDate": f"{start_year}-01-01", "endDate": f"{end_year}-12-31",
        "dataTypes": ",".join(elements), "format": "json", "units": "metric",
    }
    r = SESSION.get(_GHCND_API, params=p, timeout=180)
    r.raise_for_status()
    raw = r.json()
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    df["date"] = pd.to_datetime(df["DATE"])
    for col in elements:
        if col not in df.columns:
            continue
        vals = pd.to_numeric(df[col], errors="coerce")
        if col in ("TMAX", "TMIN", "TAVG", "ADPT", "AWBT"):
            df[col.lower() + "_c"] = vals / 10.0
        else:
            df[col.lower()] = vals
        df = df.drop(columns=[col])
    df["city"] = city
    df.to_parquet(cache, index=False)
    return df

# --------------------------------- ISD hourly
_ISD_BASE = "https://www.ncei.noaa.gov/data/global-hourly/access"

def _parse_isd_tenths(s: str) -> float:
    if not s:
        return np.nan
    try:
        val_str, q = s.split(",")
    except (ValueError, AttributeError):
        return np.nan
    if q not in ("0", "1", "4", "5"):
        return np.nan
    try:
        val = int(val_str)
    except ValueError:
        return np.nan
    return np.nan if val == 9999 else val / 10.0

def load_isd_city_hourly(
    city: str, station_id: str, start_year: int, end_year: int,
    force: bool = False,
) -> pd.DataFrame:
    """Hourly ISD (TMP + DEW) with Stull wet-bulb. One row per hour,
    FM-12 preferred over FM-15. Paris Orly (07149099999) -> 25 741
    rows for 2023, verified 2026-04-09."""
    cache = RAW_DIR / "isd" / f"{city}_{station_id}_{start_year}_{end_year}.parquet"
    if cache.exists() and not force:
        return pd.read_parquet(cache)
    frames = []
    for year in range(start_year, end_year + 1):
        url = f"{_ISD_BASE}/{year}/{station_id}.csv"
        r = SESSION.get(url, timeout=240)
        if r.status_code != 200:
            print(f"  isd {station_id} {year}: {r.status_code}")
            continue
        reader = csv.DictReader(io.StringIO(r.text))
        year_rows = [{
            "datetime_utc": row["DATE"],
            "report_type": row.get("REPORT_TYPE", "").strip(),
            "t2m_c": _parse_isd_tenths(row.get("TMP", "")),
            "td2m_c": _parse_isd_tenths(row.get("DEW", "")),
        } for row in reader]
        frames.append(pd.DataFrame(year_rows))
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["datetime_utc"] = pd.to_datetime(df["datetime_utc"])
    df["_h"] = df["datetime_utc"].dt.floor("h")
    df["_r"] = df["report_type"].map({"FM-12": 0, "FM-15": 1}).fillna(2)
    df = (df.sort_values(["_h", "_r"])
            .drop_duplicates("_h", keep="first")
            .drop(columns=["_h", "_r"]).reset_index(drop=True))
    df["city"] = city
    df["tw_c"] = compute_wet_bulb(df["t2m_c"].to_numpy(), df["td2m_c"].to_numpy())
    df.to_parquet(cache, index=False)
    return df

# --------------------------------- ERA5 (optional cdsapi path)
def load_era5_city(
    city: str, lat: float, lon: float, start_year: int, end_year: int,
    variables: Sequence[str] = ("2m_temperature", "2m_dewpoint_temperature",
                                "mean_sea_level_pressure", "surface_pressure"),
    force: bool = False,
) -> pd.DataFrame:
    """Hourly ERA5 single-levels for a 0.5x0.5 bbox. Requires cdsapi+xarray
    and ~/.cdsapirc with a Copernicus CDS token (see data_sources.md #1)."""
    cache = RAW_DIR / "era5" / f"{city}_{start_year}_{end_year}.parquet"
    if cache.exists() and not force:
        return pd.read_parquet(cache)
    try:
        import cdsapi  # type: ignore
        import xarray as xr  # type: ignore
    except ImportError as e:
        raise ImportError("ERA5 loading needs `pip install cdsapi xarray "
            "netCDF4` + ~/.cdsapirc. Fall back to load_isd_city_hourly.") from e
    nc_path = RAW_DIR / "era5" / f"{city}_{start_year}_{end_year}.nc"
    if not nc_path.exists():
        cdsapi.Client().retrieve("reanalysis-era5-single-levels", {
            "product_type": "reanalysis", "format": "netcdf",
            "variable": list(variables),
            "year": [str(y) for y in range(start_year, end_year + 1)],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "day": [f"{d:02d}" for d in range(1, 32)],
            "time": [f"{h:02d}:00" for h in range(24)],
            "area": [lat + 0.25, lon - 0.25, lat - 0.25, lon + 0.25],
        }, str(nc_path))
    ds = xr.open_dataset(nc_path)
    df = ds.mean(dim=[d for d in ("latitude", "longitude") if d in ds.dims]).to_dataframe().reset_index()
    df["datetime_utc"] = pd.to_datetime(df["time"])
    df["t2m_c"] = df["t2m"] - 273.15
    df["td2m_c"] = df["d2m"] - 273.15
    df["msl_hpa"] = df.get("msl", np.nan) / 100.0
    df["sp_hpa"] = df.get("sp", np.nan) / 100.0
    df["city"] = city
    df["tw_c"] = compute_wet_bulb(df["t2m_c"].to_numpy(), df["td2m_c"].to_numpy())
    out = df[["city", "datetime_utc", "t2m_c", "td2m_c", "msl_hpa", "sp_hpa", "tw_c"]]
    out.to_parquet(cache, index=False)
    return out

# --------------------------------- aggregators
def _apply_climatology(weekly, climatology):
    if climatology is None:
        weekly["tw_anomaly_c"] = np.nan
        return weekly
    wk = weekly["iso_week_start"].dt.isocalendar().week
    clim_map = climatology.set_index("week_of_year")["tw_clim_c"].to_dict()
    weekly["tw_anomaly_c"] = weekly["tw_c_mean"] - wk.map(clim_map)
    return weekly

def _heat_dome(weekly, day_frame, value_col, date_col, p95):
    if p95 is None or value_col not in day_frame.columns:
        weekly["consecutive_days_above_p95"] = 0
        weekly["heat_dome_flag"] = False
        return weekly
    d = day_frame.copy()
    d["above_p95"] = (d[value_col] >= p95).astype(int)
    runs = (d.sort_values(date_col)
             .assign(grp=lambda f: (f["above_p95"] != f["above_p95"].shift()).cumsum())
             .groupby(["iso_week_start", "grp", "above_p95"]).size()
             .reset_index(name="run_len"))
    hot = runs[runs["above_p95"] == 1]
    streak = hot.groupby("iso_week_start")["run_len"].max().rename("consecutive_days_above_p95")
    weekly = weekly.merge(streak.reset_index(), on="iso_week_start", how="left")
    weekly["consecutive_days_above_p95"] = weekly["consecutive_days_above_p95"].fillna(0).astype(int)
    weekly["heat_dome_flag"] = weekly["consecutive_days_above_p95"] >= 3
    return weekly

def aggregate_hourly_to_weekly(
    hourly: pd.DataFrame, city: str, utc_offset_hours: int = 0,
    climatology: Optional[pd.DataFrame] = None,
    p95_threshold: Optional[float] = None,
) -> pd.DataFrame:
    """ISD/ERA5 hourly -> EXPOSURE_COLUMNS. `utc_offset_hours` shifts UTC
    to local wall-clock so the 00:00-06:00 night window is local.
    `climatology`: DataFrame with columns week_of_year, tw_clim_c."""
    if hourly.empty:
        return pd.DataFrame(columns=EXPOSURE_COLUMNS)
    df = hourly.copy()
    df["local_time"] = df["datetime_utc"] + pd.to_timedelta(utc_offset_hours, unit="h")
    df["local_date"] = df["local_time"].dt.normalize()
    df["local_hour"] = df["local_time"].dt.hour
    daily = df.groupby("local_date").agg(
        tmax_c=("t2m_c", "max"), tmin_c=("t2m_c", "min"),
        tavg_c=("t2m_c", "mean"), tdew_c=("td2m_c", "mean"),
        tw_c_mean=("tw_c", "mean"), tw_c_max=("tw_c", "max"),
    ).reset_index()
    nights = df[df["local_hour"] < 6].groupby("local_date").agg(
        tw_night_c_mean=("tw_c", "mean"), tw_night_c_max=("tw_c", "max"),
    ).reset_index()
    daily = daily.merge(nights, on="local_date", how="left")
    daily["iso_week_start"] = _iso_week_start(daily["local_date"])
    weekly = daily.groupby("iso_week_start").agg(
        tmax_c_mean=("tmax_c", "mean"), tmax_c_max=("tmax_c", "max"),
        tmin_c_mean=("tmin_c", "mean"),
        tavg_c=("tavg_c", "mean"), tdew_c=("tdew_c", "mean"),
        tw_c_mean=("tw_c_mean", "mean"), tw_c_max=("tw_c_max", "max"),
        tw_night_c_mean=("tw_night_c_mean", "mean"),
        tw_night_c_max=("tw_night_c_max", "max"),
    ).reset_index()
    weekly["city"] = city
    weekly = _apply_climatology(weekly, climatology)
    weekly = _heat_dome(weekly, daily, "tw_c_max", "local_date", p95_threshold)
    for c in EXPOSURE_COLUMNS:
        if c not in weekly.columns:
            weekly[c] = np.nan
    return weekly[EXPOSURE_COLUMNS]

def aggregate_daily_to_weekly(
    daily: pd.DataFrame, city: str,
    climatology: Optional[pd.DataFrame] = None,
    p95_threshold: Optional[float] = None,
) -> pd.DataFrame:
    """GHCN-D path. No night split; tw_night_* stays NaN. Uses ADPT
    (dewpoint) if present, else AWBT (direct wet-bulb), else NaN."""
    if daily.empty:
        return pd.DataFrame(columns=EXPOSURE_COLUMNS)
    d = daily.copy()
    d["iso_week_start"] = _iso_week_start(d["date"])
    if "adpt_c" in d.columns and d["adpt_c"].notna().any():
        d["tw_c_daily"] = compute_wet_bulb(d["tavg_c"].to_numpy(), d["adpt_c"].to_numpy())
    elif "awbt_c" in d.columns and d["awbt_c"].notna().any():
        d["tw_c_daily"] = d["awbt_c"]
    else:
        d["tw_c_daily"] = np.nan
    tdew_agg = ("adpt_c", "mean") if "adpt_c" in d.columns else ("tavg_c", lambda _: np.nan)
    weekly = d.groupby("iso_week_start").agg(
        tmax_c_mean=("tmax_c", "mean"), tmin_c_mean=("tmin_c", "mean"),
        tavg_c=("tavg_c", "mean"), tdew_c=tdew_agg,
        tw_c_mean=("tw_c_daily", "mean"), tw_c_max=("tw_c_daily", "max"),
    ).reset_index()
    weekly["city"] = city
    weekly["tw_night_c_mean"] = np.nan
    weekly["tw_night_c_max"] = np.nan
    weekly = _apply_climatology(weekly, climatology)
    weekly = _heat_dome(weekly, d, "tw_c_daily", "date", p95_threshold)
    for c in EXPOSURE_COLUMNS:
        if c not in weekly.columns:
            weekly[c] = np.nan
    return weekly[EXPOSURE_COLUMNS]

# --------------------------------- expected baseline
def compute_expected_baseline(
    deaths: pd.DataFrame, baseline_years: int = 5,
    exclude_pandemic: bool = True,
    group_cols: Sequence[str] = ("city",),
) -> pd.DataFrame:
    """Same-ISO-week mean over the previous `baseline_years`, excluding
    2020-W11..2022-W26 if `exclude_pandemic`. Adds expected_baseline,
    excess_deaths, p_score. Alternatives (Farrington, Poisson-GLM) in
    data_acquisition_notes.md."""
    df = deaths.copy()
    df["iso_week_start"] = pd.to_datetime(df["iso_week_start"])
    df["iso_year"] = df["iso_week_start"].dt.isocalendar().year
    df["iso_week"] = df["iso_week_start"].dt.isocalendar().week
    pandemic = ((df["iso_week_start"] >= pd.Timestamp("2020-03-09"))
                & (df["iso_week_start"] <= pd.Timestamp("2022-06-27")))
    df["_eligible"] = ~pandemic if exclude_pandemic else True
    pieces = []
    for _k, g in df.groupby(list(group_cols)):
        g = g.sort_values("iso_week_start").reset_index(drop=True)
        exp = np.full(len(g), np.nan)
        for i, row in g.iterrows():
            hist = g[(g["iso_week"] == row["iso_week"])
                     & (g["iso_year"] < row["iso_year"])
                     & (g["iso_year"] >= row["iso_year"] - baseline_years)
                     & (g["_eligible"]) & (g["deaths_all_cause"].notna())]
            if len(hist) >= max(2, baseline_years - 2):
                exp[i] = hist["deaths_all_cause"].mean()
        g["expected_baseline"] = exp
        pieces.append(g)
    out = pd.concat(pieces, ignore_index=True)
    out["excess_deaths"] = out["deaths_all_cause"] - out["expected_baseline"]
    out["p_score"] = np.where(out["expected_baseline"] > 0,
                              out["excess_deaths"] / out["expected_baseline"], np.nan)
    return out.drop(columns=["iso_year", "iso_week", "_eligible"])

# --------------------------------- master join
def build_master_dataset(
    city_names: Sequence[str],
    start_year: int,
    end_year: int,
    use_era5: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """Join weekly mortality (Eurostat for EU, CDC for US) with weekly
    exposure (ISD/ERA5 hourly -> weekly aggregates). Computes expected
    baseline and returns one row per (city, iso_week_start) ready for
    modelling."""
    eu = [c for c in city_names if CITIES[c].country != "US"]
    us = [c for c in city_names if CITIES[c].country == "US"]
    keep = ["city", "country", "iso_week_start", "iso_year_week",
            "deaths_all_cause", "age_group"]
    mort_frames: List[pd.DataFrame] = []
    if eu and (nuts := [CITIES[c].nuts3 for c in eu if CITIES[c].nuts3]):
        df = load_eurostat_weekly_deaths(nuts)
        nuts_map = {CITIES[c].nuts3: c for c in eu if CITIES[c].nuts3}
        df["city"] = df["nuts_code"].map(nuts_map)
        df["country"] = df["city"].map(lambda c: CITIES[c].country if c in CITIES else None)
        mort_frames.append(df[keep])
    if us:
        states = sorted({CITIES[c].us_state for c in us if CITIES[c].us_state})
        df = load_cdc_weekly_deaths(states=states, start_year=start_year)
        # Fan out multi-city states (California -> los_angeles AND san_diego;
        # Texas -> houston AND dallas) so each city gets its own state-weekly
        # target rows.
        state_to_cities: Dict[str, List[str]] = {}
        for c in us:
            st = CITIES[c].us_state
            if st:
                state_to_cities.setdefault(st, []).append(c)
        fanned: List[pd.DataFrame] = []
        for state, city_list in state_to_cities.items():
            sub = df[df["state"] == state]
            for city_name in city_list:
                s = sub.copy()
                s["city"] = city_name
                fanned.append(s)
        df = pd.concat(fanned, ignore_index=True) if fanned else df.iloc[0:0]
        df["country"] = "US"
        mort_frames.append(df[keep])
    mortality = pd.concat(mort_frames, ignore_index=True) if mort_frames else pd.DataFrame()
    exp_frames: List[pd.DataFrame] = []
    for name in city_names:
        c = CITIES[name]
        if verbose:
            print(f"  exposure: {name} ({c.country})")
        try:
            if use_era5:
                hourly = load_era5_city(name, c.lat, c.lon, start_year, end_year)
                weekly = aggregate_hourly_to_weekly(hourly, name, utc_offset_hours=_utc_offset(c))
            elif c.isd_usaf_wban:
                hourly = load_isd_city_hourly(name, c.isd_usaf_wban, start_year, end_year)
                weekly = aggregate_hourly_to_weekly(hourly, name, utc_offset_hours=_utc_offset(c))
            elif c.ghcnd_station:
                daily = load_ghcnd_city_daily(name, c.ghcnd_station, start_year, end_year)
                weekly = aggregate_daily_to_weekly(daily, name)
            else:
                continue
            exp_frames.append(weekly)
        except Exception as exc:  # noqa: BLE001
            print(f"    {name}: FAILED {type(exc).__name__}: {exc}")
    exposure = pd.concat(exp_frames, ignore_index=True) if exp_frames else pd.DataFrame()
    if mortality.empty or exposure.empty:
        return pd.DataFrame()
    mortality = compute_expected_baseline(mortality)
    master = mortality.merge(exposure, on=["city", "iso_week_start"], how="inner")
    master["lat"] = master["city"].map(lambda c: CITIES[c].lat if c in CITIES else np.nan)
    master["lon"] = master["city"].map(lambda c: CITIES[c].lon if c in CITIES else np.nan)
    for col in TARGET_COLUMNS:
        if col not in master.columns:
            master[col] = np.nan
    return master

# --------------------------------- smoke test
def smoke(n_cities: int = 3, n_years: int = 2) -> None:
    end_y = 2023; start_y = end_y - n_years + 1
    names = ["new_york", "paris", "phoenix"][:n_cities]
    print(f"=== smoke: {names}  {start_y}-{end_y} ===")
    fr = load_eurostat_weekly_deaths(["FR101"])
    if not fr.empty:
        print(f"[eurostat FR101] rows={len(fr)} non-null={fr['deaths_all_cause'].notna().sum()} "
              f"range={fr['iso_week_start'].min().date()}..{fr['iso_week_start'].max().date()}")
    else:
        print("[eurostat FR101] empty")
    cdc = load_cdc_weekly_deaths(states=["New York", "Arizona"], start_year=start_y)
    print(f"[cdc weekly]     rows={len(cdc)} null[deaths]={cdc['deaths_all_cause'].isna().mean():.1%}")
    ghcn = load_ghcnd_city_daily("new_york", "USW00094728", start_y, end_y)
    cols = list(ghcn.columns)[:10] if not ghcn.empty else []
    print(f"[ghcn nyc]       rows={len(ghcn)} cols={cols}")
    if not ghcn.empty and "adpt_c" in ghcn.columns:
        print(f"   adpt_c non-null: {ghcn['adpt_c'].notna().mean():.1%}")
    isd = load_isd_city_hourly("paris", "07149099999", start_y, end_y)
    if not isd.empty:
        print(f"[isd paris orly] rows={len(isd)} td2m_c non-null={isd['td2m_c'].notna().mean():.1%}")
        wk = aggregate_hourly_to_weekly(isd, "paris", utc_offset_hours=2)
        print(f"   weekly rows={len(wk)} tw_night_c_mean non-null={wk['tw_night_c_mean'].notna().mean():.1%}")
    else:
        print("[isd paris orly] empty")
    tw = compute_wet_bulb(np.array([25.0, 35.0, 40.0]), np.array([20.0, 25.0, 28.0]))
    print(f"[stull] T=(25,35,40) Td=(20,25,28) -> Tw={tw.round(2).tolist()} (~22.0, 27.7, 30.4)")
    if not cdc.empty:
        cdc2 = cdc.copy()
        cdc2["city"] = cdc2["state"].map({"New York": "new_york", "Arizona": "phoenix"})
        cdc2 = cdc2.dropna(subset=["city"])
        bl = compute_expected_baseline(cdc2)
        print(f"[baseline]       rows={len(bl)} "
              f"exp non-null={bl['expected_baseline'].notna().mean():.1%} "
              f"p_score non-null={bl['p_score'].notna().mean():.1%}")
if __name__ == "__main__":
    smoke(n_cities=3, n_years=2)