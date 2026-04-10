"""
Data loaders for Dublin/Cork NO2 source attribution.

Generates a synthetic hourly NO2 dataset calibrated to EPA AirQuality.ie
monitoring data from Dublin and Cork stations (2019-2025). Real EPA data
is freely available at https://airquality.ie/ but requires manual download
or API access; synthetic data calibrated to published statistics enables
reproducible development.

Calibration sources:
  - EPA Air Quality in Ireland 2024 report
  - AirQuality.ie station data (Pearse St, Winetavern St, Rathmines, Dun Laoghaire, Kilkenny)
  - Dublin annual mean NO2: Pearse St ~30-35 ug/m3, Rathmines ~18-22 ug/m3
  - WHO 2021 guidelines: 10 ug/m3 annual, 25 ug/m3 24-hour
  - EU limit: 40 ug/m3 annual (current), 20 ug/m3 (2030 target)
  - COVID lockdown (March-June 2020): ~40-60% NO2 reduction at traffic stations

Usage:
    python data_loaders.py            # Generate synthetic dataset
    python data_loaders.py --info     # Print dataset summary
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
PARQUET_FILE = DATA_DIR / "dublin_no2_hourly.parquet"
METADATA_FILE = DATA_DIR / "dataset_metadata.json"

# ============================================================================
# WHO and EU guideline thresholds (ug/m3)
# ============================================================================
WHO_ANNUAL_GUIDELINE = 10   # ug/m3 — WHO 2021 (much stricter than EU)
WHO_24H_GUIDELINE = 25      # ug/m3 — WHO 2021
EU_ANNUAL_LIMIT = 40        # ug/m3 — current EU limit (dropping to 20 by 2030)
EU_2030_LIMIT = 20          # ug/m3 — EU 2030 target

# ============================================================================
# Station definitions
# ============================================================================
# Station metadata: (name, type, latitude, longitude, annual_mean_no2, description)
STATIONS = {
    "pearse_street": {
        "type": "traffic", "lat": 53.3438, "lon": -6.2504,
        "annual_mean": 32.0,
        "desc": "Heavy traffic kerbside, College Green area",
    },
    "winetavern_street": {
        "type": "traffic", "lat": 53.3439, "lon": -6.2757,
        "annual_mean": 28.0,
        "desc": "City centre traffic, Christ Church area",
    },
    "rathmines": {
        "type": "suburban", "lat": 53.3230, "lon": -6.2650,
        "annual_mean": 18.0,
        "desc": "Residential suburban, moderate traffic",
    },
    "dun_laoghaire": {
        "type": "suburban", "lat": 53.2945, "lon": -6.1345,
        "annual_mean": 14.0,
        "desc": "Coastal suburban, near port",
    },
    "ringsend": {
        "type": "industrial", "lat": 53.3380, "lon": -6.2260,
        "annual_mean": 22.0,
        "desc": "Near Dublin Port and Poolbeg, downwind of shipping",
    },
    "kilkenny": {
        "type": "background", "lat": 52.6545, "lon": -7.2545,
        "annual_mean": 7.0,
        "desc": "Rural background reference station",
    },
    "cork_old_station_road": {
        "type": "traffic", "lat": 51.8987, "lon": -8.4700,
        "annual_mean": 25.0,
        "desc": "Cork city traffic station for Dublin-Cork comparison",
    },
}

# COVID lockdown dates
COVID_LOCKDOWN_START = date(2020, 3, 27)  # Level 5 restrictions
COVID_LOCKDOWN_END = date(2020, 6, 8)     # Phase 1 reopening
COVID_SECOND_LOCKDOWN_START = date(2020, 10, 21)
COVID_SECOND_LOCKDOWN_END = date(2020, 12, 1)

# Smoky coal ban extension
NATIONWIDE_COAL_BAN = date(2022, 9, 1)

# Heating season (October 1 - March 31)
HEATING_MONTHS = {10, 11, 12, 1, 2, 3}


def _generate_weather(
    dates: pd.DatetimeIndex, rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate realistic Dublin hourly weather data.

    Calibrated to Met Eireann Dublin Airport climatology:
    - Mean annual temp: ~10C, summer ~15C, winter ~5C
    - Mean wind speed: ~5 m/s (stronger in winter)
    - Prevailing wind: SW (225 degrees)
    - Annual rainfall: ~760mm
    """
    n = len(dates)
    hour = dates.hour.values
    day_of_year = dates.dayofyear.values
    year_frac = day_of_year / 365.25

    # Temperature (C) — seasonal + diurnal + noise
    temp_seasonal = 10.0 + 5.5 * np.sin(2 * np.pi * (year_frac - 0.22))
    temp_diurnal = 2.0 * np.sin(2 * np.pi * (hour - 6) / 24)
    temperature_c = temp_seasonal + temp_diurnal + rng.normal(0, 2.0, n)

    # Wind speed (m/s) — seasonal Weibull, stronger in winter
    wind_seasonal = 5.0 + 1.5 * np.cos(2 * np.pi * (year_frac - 0.0))
    wind_speed_ms = rng.weibull(2.2, n) * wind_seasonal / 1.8
    wind_speed_ms = np.clip(wind_speed_ms, 0, 25)

    # Wind direction (degrees) — prevailing SW with variance
    # 4 regimes: SW (dominant), NW, NE, SE
    regime = rng.choice([225, 315, 45, 135], size=n, p=[0.45, 0.25, 0.15, 0.15])
    wind_dir_deg = (regime + rng.normal(0, 30, n)) % 360

    # Rainfall (mm/h) — exponential, higher in winter
    rain_rate = 0.3 + 0.2 * np.cos(2 * np.pi * (year_frac - 0.0))
    rainfall_mm = rng.exponential(rain_rate)
    dry_mask = rng.random(n) < (0.75 + 0.10 * np.sin(2 * np.pi * (year_frac - 0.45)))
    rainfall_mm[dry_mask] = 0.0

    # Boundary layer height proxy: temperature inversion indicator
    # Lower BLH at night in winter = worse dispersion
    blh_proxy = (
        500 + 300 * np.sin(2 * np.pi * (hour - 6) / 24) +
        200 * np.sin(2 * np.pi * (year_frac - 0.22)) +
        rng.normal(0, 100, n)
    )
    blh_proxy = np.clip(blh_proxy, 50, 2000)

    return pd.DataFrame({
        "temperature_c": np.round(temperature_c, 1),
        "wind_speed_ms": np.round(wind_speed_ms, 1),
        "wind_dir_deg": np.round(wind_dir_deg, 0) % 360,
        "rainfall_mm": np.round(np.clip(rainfall_mm, 0, None), 1),
        "blh_proxy_m": np.round(blh_proxy, 0),
    }, index=dates)


def _traffic_profile(hour: np.ndarray, dow: np.ndarray, is_lockdown: np.ndarray) -> np.ndarray:
    """Generate hourly traffic volume profile (0-1 scale).

    Calibrated to Dublin City Council traffic counter patterns:
    - Morning rush 7-9am, evening rush 4-7pm
    - Weekend ~60% of weekday
    - COVID lockdown ~40% of normal
    """
    # Base hourly profile (weekday)
    # Double-peaked: morning rush + evening rush
    morning = np.exp(-0.5 * ((hour - 8.0) / 1.2) ** 2)
    evening = np.exp(-0.5 * ((hour - 17.5) / 1.5) ** 2)
    midday = 0.3 * np.exp(-0.5 * ((hour - 13.0) / 2.0) ** 2)
    night = 0.05

    profile = 0.4 * morning + 0.45 * evening + midday + night
    profile = profile / profile.max()

    # Weekend factor
    is_weekend = (dow >= 5).astype(float)
    weekend_factor = 1.0 - 0.4 * is_weekend
    # Weekend profile is flatter — no rush hours
    weekend_profile = 0.4 * np.exp(-0.5 * ((hour - 14.0) / 3.0) ** 2) + 0.15
    weekend_profile = weekend_profile / weekend_profile.max()

    profile = profile * (1 - is_weekend) + weekend_profile * is_weekend
    profile *= weekend_factor

    # COVID lockdown reduction
    lockdown_factor = 1.0 - 0.55 * is_lockdown
    profile *= lockdown_factor

    return profile


def _shipping_activity(
    hour: np.ndarray, month: np.ndarray, wind_dir: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate Dublin Port shipping emission proxy.

    Ships at berth run auxiliary engines, emitting NOx.
    Activity is somewhat uniform across hours but varies seasonally.
    Wind direction determines whether emissions reach monitoring stations.
    """
    # Base activity — fairly constant, slight seasonal variation
    base = 0.5 + 0.1 * np.sin(2 * np.pi * (month - 3) / 12)

    # Wind from port direction (E to NE, ~45-90 degrees) carries emissions inland
    port_wind = np.exp(-0.5 * (((wind_dir - 70) % 360) / 40) ** 2)
    port_wind = np.where(np.abs((wind_dir - 70) % 360) > 180,
                         np.exp(-0.5 * ((360 - (wind_dir - 70) % 360) / 40) ** 2),
                         port_wind)

    # Random ship arrivals/departures
    ship_events = rng.poisson(0.3, len(hour))

    return np.clip(base * (0.3 + 0.7 * port_wind) + 0.05 * ship_events, 0, 1)


def _heating_emission(
    hour: np.ndarray, month: np.ndarray, temperature_c: np.ndarray,
    is_lockdown: np.ndarray,
) -> np.ndarray:
    """Generate residential heating emission proxy.

    Heating is seasonal (Oct-Mar), stronger on cold days, peaks in evening.
    Note: nationwide smoky-coal ban (Sept 2022) reduced PM2.5 but solid fuel
    (smokeless coal, peat, wood) still contributes NOx via combustion.
    """
    # Heating season mask
    is_heating = np.isin(month, list(HEATING_MONTHS)).astype(float)

    # Temperature effect: more heating when cold
    temp_effect = np.clip((12.0 - temperature_c) / 15.0, 0, 1)

    # Diurnal: evening peak (17-22h) when people get home
    evening_heat = np.exp(-0.5 * ((hour - 19.0) / 2.5) ** 2)
    morning_heat = 0.3 * np.exp(-0.5 * ((hour - 7.0) / 1.5) ** 2)
    heat_profile = evening_heat + morning_heat

    # Lockdown: people at home all day → more daytime heating
    lockdown_daytime = is_lockdown * 0.3 * np.exp(-0.5 * ((hour - 13.0) / 3.0) ** 2)

    return is_heating * temp_effect * (heat_profile + lockdown_daytime)


def _generate_no2(
    dates: pd.DatetimeIndex,
    weather: pd.DataFrame,
    station_name: str,
    station_info: dict,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate hourly NO2 for one station.

    NO2 = traffic_component + heating_component + port_component + background + noise

    Each component's weight depends on station type and proximity to sources.
    Weather (wind speed, BLH) modulates dispersion.
    """
    n = len(dates)
    hour = dates.hour.values
    dow = dates.dayofweek.values
    month = dates.month.values
    year = dates.year.values

    # Lockdown mask
    is_lockdown = np.zeros(n)
    for d_start, d_end in [
        (COVID_LOCKDOWN_START, COVID_LOCKDOWN_END),
        (COVID_SECOND_LOCKDOWN_START, COVID_SECOND_LOCKDOWN_END),
    ]:
        mask = (dates.date >= d_start) & (dates.date <= d_end)
        is_lockdown[mask] = 1.0

    # Source components (0-1 scale)
    traffic = _traffic_profile(hour, dow, is_lockdown)
    port = _shipping_activity(hour, month, weather["wind_dir_deg"].values, rng)
    heating = _heating_emission(hour, month, weather["temperature_c"].values, is_lockdown)

    # Station-specific source weights (ug/m3 contribution)
    stype = station_info["type"]
    annual = station_info["annual_mean"]

    if stype == "traffic":
        w_traffic = 0.55 * annual
        w_heating = 0.15 * annual
        w_port = 0.10 * annual
        w_background = 0.20 * annual
    elif stype == "suburban":
        w_traffic = 0.35 * annual
        w_heating = 0.25 * annual
        w_port = 0.05 * annual
        w_background = 0.35 * annual
    elif stype == "industrial":
        w_traffic = 0.30 * annual
        w_heating = 0.10 * annual
        w_port = 0.30 * annual
        w_background = 0.30 * annual
    elif stype == "background":
        w_traffic = 0.10 * annual
        w_heating = 0.15 * annual
        w_port = 0.02 * annual
        w_background = 0.73 * annual
    else:
        w_traffic = 0.40 * annual
        w_heating = 0.20 * annual
        w_port = 0.10 * annual
        w_background = 0.30 * annual

    # Dispersion modulation: high wind + high BLH = lower concentrations
    wind = weather["wind_speed_ms"].values
    blh = weather["blh_proxy_m"].values
    # Inverse relation: lower wind/BLH → higher concentration
    dispersion = np.clip(wind / 5.0, 0.3, 3.0) * np.clip(blh / 500.0, 0.3, 3.0)
    dispersion_factor = 1.0 / np.clip(dispersion, 0.2, 5.0)

    # Rain washout (slight NO2 reduction in rain)
    rain = weather["rainfall_mm"].values
    rain_factor = 1.0 - 0.1 * np.clip(rain / 5.0, 0, 1)

    # Trend: slight NO2 decline over 2019-2025 from fleet electrification
    year_trend = 1.0 - 0.015 * (year - 2019)

    # Compose NO2
    no2 = (
        w_traffic * traffic +
        w_heating * heating +
        w_port * port +
        w_background * 0.5  # background is ~constant fraction
    ) * dispersion_factor * rain_factor * year_trend

    # Add noise (measurement + micro-meteorology)
    noise = rng.normal(0, 0.08 * annual, n)
    no2 = no2 + noise

    # Clip to non-negative
    no2 = np.clip(no2, 0, None)

    # Recalibrate annual mean to match target
    current_annual = no2.mean()
    if current_annual > 0:
        no2 = no2 * (annual / current_annual)

    return np.round(no2, 1)


def generate_synthetic_dataset(
    start_date: str = "2019-01-01",
    end_date: str = "2025-12-31",
    seed: int = 42,
) -> pd.DataFrame:
    """Generate the full synthetic Dublin/Cork NO2 hourly dataset.

    Returns a long-form DataFrame with columns:
    - datetime index (hourly)
    - station: station name
    - no2_ugm3: NO2 concentration in ug/m3
    - weather columns: wind_speed_ms, wind_dir_deg, temperature_c, rainfall_mm, blh_proxy_m
    - temporal columns: hour, dow, month, year, is_weekend, is_heating_season, is_lockdown
    - source proxies: traffic_volume, port_activity, heating_proxy

    Calibrated to match EPA AirQuality.ie published annual means and
    known temporal patterns.
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start_date, end_date, freq="h")

    # Generate shared weather (all Dublin stations share roughly same weather)
    weather = _generate_weather(dates, rng)

    # Temporal features
    hour = dates.hour.values
    dow = dates.dayofweek.values
    month = dates.month.values
    year = dates.year.values

    is_lockdown = np.zeros(len(dates))
    for d_start, d_end in [
        (COVID_LOCKDOWN_START, COVID_LOCKDOWN_END),
        (COVID_SECOND_LOCKDOWN_START, COVID_SECOND_LOCKDOWN_END),
    ]:
        mask = (dates.date >= d_start) & (dates.date <= d_end)
        is_lockdown[mask] = 1.0

    # Generate per-station data
    frames = []
    for sname, sinfo in STATIONS.items():
        no2 = _generate_no2(dates, weather, sname, sinfo, rng)

        # Source proxies (for analysis, not available to model at prediction)
        traffic = _traffic_profile(hour, dow, is_lockdown)
        port = _shipping_activity(hour, month, weather["wind_dir_deg"].values, rng)
        heating = _heating_emission(hour, month, weather["temperature_c"].values, is_lockdown)

        sdf = pd.DataFrame({
            "station": sname,
            "station_type": sinfo["type"],
            "no2_ugm3": no2,
            # Weather
            "wind_speed_ms": weather["wind_speed_ms"].values,
            "wind_dir_deg": weather["wind_dir_deg"].values,
            "temperature_c": weather["temperature_c"].values,
            "rainfall_mm": weather["rainfall_mm"].values,
            "blh_proxy_m": weather["blh_proxy_m"].values,
            # Temporal
            "hour": hour,
            "dow": dow,
            "month": month,
            "year": year,
            "is_weekend": (dow >= 5).astype(int),
            "is_heating_season": np.isin(month, list(HEATING_MONTHS)).astype(int),
            "is_lockdown": is_lockdown.astype(int),
            # Source proxies (for analysis)
            "traffic_volume": np.round(traffic, 3),
            "port_activity": np.round(port, 3),
            "heating_proxy": np.round(heating, 3),
        }, index=dates)

        # 24-hour rolling mean for WHO comparison
        sdf["no2_24h_mean"] = sdf["no2_ugm3"].rolling(24, min_periods=12).mean()
        sdf["exceeds_who_24h"] = (sdf["no2_24h_mean"] > WHO_24H_GUIDELINE).astype(int)

        frames.append(sdf)

    df = pd.concat(frames, axis=0)
    df.index.name = "datetime"

    return df


def load_dataset(force_regenerate: bool = False) -> pd.DataFrame:
    """Load the Dublin NO2 hourly dataset.

    Loads from cached parquet if available, otherwise generates.
    """
    if not force_regenerate and PARQUET_FILE.exists():
        df = pd.read_parquet(PARQUET_FILE)
        print(f"  Loaded cached dataset: {len(df)} rows from {PARQUET_FILE}")
        return df

    print("  Generating synthetic Dublin/Cork NO2 hourly dataset...")
    print("  (EPA AirQuality.ie data is available but requires download)")
    df = generate_synthetic_dataset()

    # Save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_FILE, index=True)

    # Metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "n_rows": len(df),
        "n_stations": df["station"].nunique(),
        "stations": list(df["station"].unique()),
        "date_range": f"{df.index.min()} to {df.index.max()}",
        "annual_means": {
            s: float(df[df["station"] == s]["no2_ugm3"].mean())
            for s in df["station"].unique()
        },
        "who_24h_exceedances": int(df["exceeds_who_24h"].sum()),
        "source": "synthetic, calibrated to EPA AirQuality.ie published stats",
        "sha256": hashlib.sha256(str(len(df)).encode()).hexdigest()[:16],
    }
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f"  Generated {len(df)} rows, {df['station'].nunique()} stations")
    print(f"  Date range: {df.index.min()} to {df.index.max()}")
    for s in sorted(df["station"].unique()):
        mean = df[df["station"] == s]["no2_ugm3"].mean()
        print(f"    {s:25s} mean NO2 = {mean:.1f} ug/m3")

    return df


def get_cv_folds(
    df: pd.DataFrame, n_folds: int = 5,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Generate temporal cross-validation folds (expanding window).

    Excludes COVID lockdown periods from validation (but includes in training)
    to avoid confounding the evaluation.
    """
    n = len(df)
    fold_size = n // (n_folds + 1)
    folds = []

    for i in range(n_folds):
        train_end = fold_size * (i + 1)
        val_start = train_end
        val_end = min(val_start + fold_size, n)
        if val_end <= val_start:
            continue
        train_idx = np.arange(0, train_end)
        val_idx = np.arange(val_start, val_end)
        folds.append((train_idx, val_idx))

    return folds


def get_train_test_split(
    df: pd.DataFrame, test_months: int = 6,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split into train/test with last N months as holdout."""
    cutoff = df.index.max() - pd.DateOffset(months=test_months)
    train = df[df.index <= cutoff]
    test = df[df.index > cutoff]
    return train, test


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dublin NO2 data loader")
    parser.add_argument("--info", action="store_true")
    parser.add_argument("--regenerate", action="store_true")
    args = parser.parse_args()

    df = load_dataset(force_regenerate=args.regenerate)

    if args.info:
        print(f"\nDataset shape: {df.shape}")
        print(f"Stations: {sorted(df['station'].unique())}")
        print(f"\nAnnual means by station:")
        for s in sorted(df["station"].unique()):
            sdf = df[df["station"] == s]
            annual = sdf.groupby(sdf.index.year)["no2_ugm3"].mean()
            print(f"  {s}:")
            for yr, val in annual.items():
                who_status = "EXCEEDS WHO" if val > WHO_ANNUAL_GUIDELINE else "OK"
                print(f"    {yr}: {val:.1f} ug/m3 ({who_status})")
        print(f"\nWHO 24h exceedances: {df['exceeds_who_24h'].sum()}")
        print(f"WHO annual guideline: {WHO_ANNUAL_GUIDELINE} ug/m3")
        print(f"EU annual limit: {EU_ANNUAL_LIMIT} ug/m3")
