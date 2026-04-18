"""Data loading and cleaning for NUFORC UFO sighting datasets."""
import pandas as pd
import numpy as np
import os
import re

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cached")


def _parse_nuforc_datetime(s):
    """Parse NUFORC datetime strings like '2014-09-21 13:00:00 Local'."""
    if pd.isna(s):
        return pd.NaT
    s = str(s).strip()
    # Remove timezone suffixes
    for tz in [' Local', ' Pacific', ' Eastern', ' Central', ' Mountain', ' UTC']:
        s = s.replace(tz, '')
    try:
        return pd.to_datetime(s)
    except:
        return pd.NaT


def _parse_state_country(location):
    """Parse location string like 'Huntsville, TX, USA' into (state, country)."""
    if pd.isna(location):
        return None, None
    parts = [p.strip() for p in str(location).split(',')]
    if len(parts) >= 3:
        return parts[-2].strip(), parts[-1].strip()
    elif len(parts) == 2:
        return parts[-1].strip(), 'USA'
    return None, None


def load_nuforc_str(cache=True):
    """Load and clean the primary NUFORC structured dataset (147k rows)."""
    cache_path = os.path.join(CACHE_DIR, "nuforc_str_clean.parquet")
    if cache and os.path.exists(cache_path):
        return pd.read_parquet(cache_path)

    df = pd.read_csv(os.path.join(RAW_DIR, "nuforc_str.csv"))

    # Parse datetimes
    df['occurred_dt'] = df['Occurred'].apply(_parse_nuforc_datetime)
    df['reported_dt'] = df['Reported'].apply(_parse_nuforc_datetime)
    df['posted_dt'] = pd.to_datetime(df['Posted'], errors='coerce')

    # Extract temporal features
    df['year'] = df['occurred_dt'].dt.year
    df['month'] = df['occurred_dt'].dt.month
    df['hour'] = df['occurred_dt'].dt.hour
    df['day_of_week'] = df['occurred_dt'].dt.dayofweek  # 0=Monday
    df['day_of_year'] = df['occurred_dt'].dt.dayofyear

    # Parse location
    loc_parsed = df['Location'].apply(lambda x: pd.Series(_parse_state_country(x)))
    df['state'] = loc_parsed[0]
    df['country_str'] = loc_parsed[1]

    # Explanation field
    df['has_explanation'] = df['Explanation'].notna().astype(int)
    df['explanation_type'] = df['Explanation'].str.extract(r'^([^-]+)')[0].str.strip()
    df['explanation_certainty'] = df['Explanation'].str.extract(r'- (\w+)$')[0].str.strip()

    # Text length as quality proxy
    df['text_length'] = df['Text'].fillna('').str.len()
    df['summary_length'] = df['Summary'].fillna('').str.len()

    # Reporting lag in days (handle overflow for extreme dates)
    try:
        lag = (df['reported_dt'] - df['occurred_dt'])
        df['reporting_lag_days'] = lag.dt.total_seconds() / 86400
    except OverflowError:
        df['reporting_lag_days'] = np.nan
        mask = df['reported_dt'].notna() & df['occurred_dt'].notna()
        # Only compute for reasonable date ranges (both after 1900)
        mask &= df['occurred_dt'].dt.year >= 1900
        mask &= df['reported_dt'].dt.year >= 1900
        idx = df[mask].index
        lag_vals = (df.loc[idx, 'reported_dt'] - df.loc[idx, 'occurred_dt']).dt.total_seconds() / 86400
        df.loc[idx, 'reporting_lag_days'] = lag_vals

    # Duration parsing (attempt to extract seconds)
    df['duration_seconds'] = df['Duration'].apply(_parse_duration)

    # Cache
    os.makedirs(CACHE_DIR, exist_ok=True)
    if cache:
        df.to_parquet(cache_path)

    return df


def _parse_duration(s):
    """Parse duration strings like '2 minutes', 'several seconds', '1 hour'."""
    if pd.isna(s):
        return np.nan
    s = str(s).lower().strip()

    # Try to find a number
    num_match = re.search(r'(\d+\.?\d*)', s)
    if not num_match:
        # Handle words
        word_nums = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                     'ten': 10, 'fifteen': 15, 'twenty': 20, 'thirty': 30,
                     'several': 5, 'few': 3, 'couple': 2}
        for word, val in word_nums.items():
            if word in s:
                num = val
                break
        else:
            return np.nan
    else:
        num = float(num_match.group(1))

    # Determine unit
    if 'hour' in s:
        return num * 3600
    elif 'min' in s:
        return num * 60
    elif 'sec' in s:
        return num
    else:
        return num * 60  # default to minutes


def load_nuforc_kaggle(cache=True):
    """Load the geocoded Kaggle dataset (80k rows with lat/lon)."""
    cache_path = os.path.join(CACHE_DIR, "nuforc_kaggle_clean.parquet")
    if cache and os.path.exists(cache_path):
        return pd.read_parquet(cache_path)

    df = pd.read_csv(
        os.path.join(RAW_DIR, "nuforc_kaggle.csv"),
        header=None,
        names=['datetime', 'city', 'state', 'country', 'shape',
               'duration_sec', 'duration_text', 'description',
               'date_posted', 'latitude', 'longitude'],
        low_memory=False
    )

    # Parse coordinates
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    # Parse datetime
    df['dt'] = pd.to_datetime(df['datetime'], errors='coerce')
    df['year'] = df['dt'].dt.year
    df['month'] = df['dt'].dt.month

    # Duration
    df['duration_sec'] = pd.to_numeric(df['duration_sec'], errors='coerce')

    os.makedirs(CACHE_DIR, exist_ok=True)
    if cache:
        df.to_parquet(cache_path)

    return df
