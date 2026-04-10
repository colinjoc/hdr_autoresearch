"""Data loaders for Dublin/Cork NO2 source attribution project.

All data is REAL, downloaded from:
- EEA Air Quality (Zenodo): https://zenodo.org/records/14513586
- Met Eireann Dublin Airport: https://data.gov.ie/dataset/dublin-airport-hourly-data

NO synthetic data is generated anywhere in this module.
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# WHO 2021 Air Quality Guidelines for NO2
WHO_ANNUAL = 10   # µg/m³ annual mean
WHO_24H = 25      # µg/m³ 24-hour mean

# EU Limit Values for NO2
EU_ANNUAL = 40    # µg/m³ annual mean
EU_1H = 200       # µg/m³ 1-hour (not to be exceeded >18 times/year)

# Key station mapping: EEA code -> (EPA name, type, city)
KEY_STATIONS = {
    'IE005AP': ('Winetavern Street', 'traffic', 'Dublin'),
    'IE0098A': ('Rathmines', 'background', 'Dublin'),
    'IE004AP': ('Pearse Street', 'traffic', 'Dublin'),
    'IE006AP': ("St John's Road West", 'traffic', 'Dublin'),
    'IE0131A': ('Blanchardstown (M50/N3)', 'traffic', 'Dublin'),
    'IE0132A': ('Dun Laoghaire', 'background', 'Dublin'),
    'IE0036A': ('Ballyfermot', 'background', 'Dublin'),
    'IE0028A': ('Clonskeagh', 'background', 'Dublin'),
    'IE0140A': ('Tallaght', 'background', 'Dublin'),
    'IE001AP': ('Davitt Road', 'traffic', 'Dublin'),
    'IE001BP': ('Cork Old Station Road', 'background', 'Cork'),
    'IE013CK': ('Cork South Link Road', 'traffic', 'Cork'),
    'IE0090A': ('Lough Navar', 'rural-remote', 'Rural'),
    'IE0111A': ('Moate', 'rural-regional', 'Rural'),
    'IE0118A': ('Castlebar', 'background', 'Rural'),
    'IE0147A': ('Kilkenny', 'background', 'Rural'),
}


def load_ireland_daily() -> pd.DataFrame:
    """Load daily Ireland NO2 data from EEA parquet extract.

    Returns DataFrame with columns: date, station, NO2, PM10, PM2.5, O3, SO2,
    station_type, station_area, lat, lon.
    """
    path = DATA_DIR / "daily_ireland.parquet"
    if not path.exists():
        # Extract from full EU dataset
        df = pd.read_parquet(
            DATA_DIR / "daily_eu.parquet",
            filters=[('Countrycode', '==', 'IE')]
        )
        df.to_parquet(path, index=False)
    else:
        df = pd.read_parquet(path)

    # Create proper date column from year + doy
    df['date'] = pd.to_datetime(
        df['year'].astype(int).astype(str) +
        df['doy'].astype(int).astype(str).str.zfill(3),
        format='%Y%j'
    )

    # Rename for clarity
    df = df.rename(columns={
        'Air.Quality.Station.EoI.Code': 'station',
        'Station.Type': 'station_type',
        'Station.Area': 'station_area',
        'Latitude': 'lat',
        'Longitude': 'lon',
        'PM2.5': 'PM25',
    })

    return df[['date', 'station', 'NO2', 'PM10', 'PM25', 'O3', 'SO2',
               'station_type', 'station_area', 'lat', 'lon']].copy()


def load_weather() -> pd.DataFrame:
    """Load Dublin Airport hourly weather data (2015-2023).

    Returns DataFrame with columns: datetime, temp, wdsp (knots), wddir (degrees),
    rain (mm), rhum (%), msl (hPa), vis (m), sun (hours).
    """
    path = DATA_DIR / "dublin_airport_weather.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"Weather data not found at {path}. "
            "Download from https://clidata.met.ie/cli/climate_data/webdata/hly532.csv"
        )
    return pd.read_parquet(path)


def load_daily_weather() -> pd.DataFrame:
    """Aggregate hourly weather to daily means/sums for merging with NO2.

    Returns DataFrame with columns: date, temp_mean, temp_max, temp_min,
    wdsp_mean, wddir_mode, rain_sum, rhum_mean, msl_mean.
    """
    wx = load_weather()
    wx['date'] = wx['datetime'].dt.date

    daily = wx.groupby('date').agg(
        temp_mean=('temp', 'mean'),
        temp_max=('temp', 'max'),
        temp_min=('temp', 'min'),
        wdsp_mean=('wdsp', 'mean'),
        wdsp_max=('wdsp', 'max'),
        rain_sum=('rain', 'sum'),
        rhum_mean=('rhum', 'mean'),
        msl_mean=('msl', 'mean'),
        sun_sum=('sun', 'sum'),
        vis_mean=('vis', 'mean'),
    ).reset_index()

    # Wind direction mode (most common direction)
    wddir_mode = wx.groupby('date')['wddir'].agg(
        lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else np.nan
    ).reset_index()
    wddir_mode.columns = ['date', 'wddir_mode']
    daily = daily.merge(wddir_mode, on='date', how='left')

    daily['date'] = pd.to_datetime(daily['date'])
    return daily


def load_merged_daily(station: str = 'IE005AP') -> pd.DataFrame:
    """Load daily NO2 for a station merged with daily weather.

    Returns DataFrame with NO2 + weather features for a single station.
    """
    no2 = load_ireland_daily()
    no2 = no2[no2['station'] == station].copy()

    wx = load_daily_weather()
    merged = no2.merge(wx, on='date', how='inner')
    return merged


def load_all_stations_daily() -> pd.DataFrame:
    """Load daily NO2 for all key stations merged with weather.

    Returns long-format DataFrame.
    """
    no2 = load_ireland_daily()
    wx = load_daily_weather()

    # Filter to key stations only
    key_codes = list(KEY_STATIONS.keys())
    no2 = no2[no2['station'].isin(key_codes)].copy()

    merged = no2.merge(wx, on='date', how='inner')

    # Add station metadata
    merged['station_name'] = merged['station'].map(
        lambda x: KEY_STATIONS.get(x, ('Unknown',))[0]
    )
    merged['source_type'] = merged['station'].map(
        lambda x: KEY_STATIONS.get(x, ('', 'unknown'))[1]
    )
    merged['city'] = merged['station'].map(
        lambda x: KEY_STATIONS.get(x, ('', '', 'unknown'))[2]
    )

    return merged
