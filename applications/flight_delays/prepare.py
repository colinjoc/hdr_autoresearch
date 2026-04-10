"""
Data loading, cleaning, feature engineering for BTS On-Time Performance data.

Key technical contribution: tail-number rotation chain reconstruction to track
how delays propagate through an aircraft's daily schedule.
"""
import pandas as pd
import numpy as np
import os
import glob

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'raw')

REQUIRED_COLUMNS = [
    'FlightDate', 'Reporting_Airline', 'Tail_Number',
    'Flight_Number_Reporting_Airline', 'Origin', 'Dest',
    'CRSDepTime', 'DepTime', 'DepDelay', 'DepDelayMinutes',
    'CRSArrTime', 'ArrTime', 'ArrDelay', 'ArrDelayMinutes',
    'Cancelled', 'Diverted',
    'CarrierDelay', 'WeatherDelay', 'NASDelay',
    'SecurityDelay', 'LateAircraftDelay',
    'Distance', 'TaxiOut', 'TaxiIn',
]

# Columns we actually load to save memory
LOAD_COLUMNS = REQUIRED_COLUMNS + [
    'Year', 'Month', 'DayofMonth', 'DayOfWeek',
    'OriginAirportID', 'DestAirportID',
    'OriginCityName', 'DestCityName',
    'OriginState', 'DestState',
]


def _csv_path(year, month):
    """Construct path to raw BTS CSV."""
    pattern = os.path.join(
        DATA_DIR,
        f'On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_{year}_{month}.csv'
    )
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    raise FileNotFoundError(f"No BTS CSV found for {year}-{month:02d} at {pattern}")


def load_raw_month(year, month):
    """Load a single month of raw BTS data."""
    path = _csv_path(year, month)
    # Only load columns we need to save memory
    available_cols = pd.read_csv(path, nrows=0).columns.tolist()
    use_cols = [c for c in LOAD_COLUMNS if c in available_cols]
    df = pd.read_csv(path, usecols=use_cols, low_memory=False)
    df['FlightDate'] = pd.to_datetime(df['FlightDate'])
    return df


def load_raw_months(year, months):
    """Load multiple months and concatenate."""
    frames = [load_raw_month(year, m) for m in months]
    return pd.concat(frames, ignore_index=True)


def load_clean(year, months):
    """Load data, drop cancelled flights, basic cleaning."""
    df = load_raw_months(year, months)
    # Remove cancelled flights — they don't have delay times
    df = df[df['Cancelled'] == 0].copy()
    # Remove rows with no tail number (can't build rotation chains)
    df = df[df['Tail_Number'].notna()].copy()
    # Remove rows with no arrival delay (diverted without arrival)
    df = df[df['ArrDelay'].notna()].copy()
    # Sort by date and scheduled departure time for chain building
    df = df.sort_values(['FlightDate', 'CRSDepTime']).reset_index(drop=True)
    return df


def build_rotation_chains(df, date=None):
    """
    Build aircraft rotation chains: for each tail number on a given date,
    return the ordered sequence of flights.

    Parameters
    ----------
    df : DataFrame
        Clean flight data
    date : str or None
        If provided, filter to this date. Otherwise use all dates.

    Returns
    -------
    dict : {tail_number: DataFrame of flights sorted by CRSDepTime}
    """
    if date is not None:
        date = pd.Timestamp(date)
        mask = df['FlightDate'] == date
        day_df = df[mask].copy()
    else:
        day_df = df.copy()

    day_df = day_df.sort_values(['Tail_Number', 'CRSDepTime'])
    chains = {}
    for tail, group in day_df.groupby('Tail_Number'):
        chains[tail] = group.sort_values('CRSDepTime').reset_index(drop=True)
    return chains


def compute_rotation_features(df):
    """
    For each flight, compute features from the aircraft's prior flight(s) that day.

    This is the key technical contribution: tracking how delays propagate through
    an aircraft's rotation (sequence of flights in a day).

    Features:
    - prior_flight_arr_delay: arrival delay of the previous flight on this aircraft
    - prior_flight_dep_delay: departure delay of the previous flight on this aircraft
    - rotation_position: which leg of the day this is (1st, 2nd, 3rd, ...)
    - cumulative_delay: total delay accumulated by this aircraft today before this flight
    - turnaround_time: scheduled time between arrival of prior flight and departure of this one
    - prior_flight_late_aircraft: LateAircraftDelay from the prior flight
    """
    df = df.copy()
    df = df.sort_values(['FlightDate', 'Tail_Number', 'CRSDepTime']).reset_index(drop=True)

    # Group by date and tail number to identify rotation chains
    df['_group'] = df['FlightDate'].astype(str) + '_' + df['Tail_Number'].astype(str)

    # Within each group, compute position and prior flight delay
    df['rotation_position'] = df.groupby(['FlightDate', 'Tail_Number']).cumcount() + 1

    # Shift within group to get prior flight's delays
    for col in ['ArrDelay', 'DepDelay', 'ArrTime', 'LateAircraftDelay']:
        shifted = df.groupby(['FlightDate', 'Tail_Number'])[col].shift(1)
        prefix = 'prior_flight_'
        new_col = prefix + col.lower().replace('arr_delay', 'arr_delay')
        if col == 'ArrDelay':
            df['prior_flight_arr_delay'] = shifted
        elif col == 'DepDelay':
            df['prior_flight_dep_delay'] = shifted
        elif col == 'ArrTime':
            df['prior_flight_arr_time'] = shifted
        elif col == 'LateAircraftDelay':
            df['prior_flight_late_aircraft'] = shifted

    # Cumulative delay within chain
    df['cumulative_delay'] = df.groupby(['FlightDate', 'Tail_Number'])['DepDelay'].cumsum() - df['DepDelay']

    # Turnaround time: scheduled departure minus prior actual arrival
    # CRSDepTime is in HHMM format (e.g., 1430 = 2:30pm)
    # This is approximate since ArrTime may be in different timezone
    mask = df['prior_flight_arr_time'].notna()
    df.loc[mask, 'turnaround_time'] = (
        df.loc[mask, 'CRSDepTime'] - df.loc[mask, 'prior_flight_arr_time']
    )
    df.loc[~mask, 'turnaround_time'] = np.nan

    df.drop(columns=['_group'], inplace=True)
    return df


def compute_airport_features(df):
    """
    Compute airport-level congestion features.

    For each flight, compute statistics about the origin and destination airports
    in the hour before this flight's scheduled departure.
    """
    df = df.copy()

    # Convert CRSDepTime to a sortable minute-of-day
    df['dep_minutes'] = (df['CRSDepTime'] // 100) * 60 + (df['CRSDepTime'] % 100)

    # For each flight, compute rolling airport stats
    # Group by date and origin, sort by time, then rolling window
    origin_stats = []
    dest_stats = []

    # Pre-compute per-date-airport hourly stats for efficiency
    # Bin flights into hourly windows
    df['dep_hour_bin'] = df['dep_minutes'] // 60

    # Origin airport: mean delay and count in same hour bin
    origin_hourly = df.groupby(['FlightDate', 'Origin', 'dep_hour_bin']).agg(
        origin_dep_delay_mean_1h=('DepDelay', 'mean'),
        origin_flights_1h=('DepDelay', 'count'),
        origin_dep_delay_std_1h=('DepDelay', 'std'),
    ).reset_index()

    df = df.merge(origin_hourly, on=['FlightDate', 'Origin', 'dep_hour_bin'], how='left')

    # Destination airport: mean arrival delay in same hour bin
    arr_minutes = (df['CRSArrTime'] // 100) * 60 + (df['CRSArrTime'] % 100)
    df['arr_hour_bin'] = arr_minutes // 60

    dest_hourly = df.groupby(['FlightDate', 'Dest', 'arr_hour_bin']).agg(
        dest_arr_delay_mean_1h=('ArrDelay', 'mean'),
        dest_flights_1h=('ArrDelay', 'count'),
    ).reset_index()

    df = df.merge(dest_hourly, on=['FlightDate', 'Dest', 'arr_hour_bin'], how='left')

    return df


def compute_temporal_features(df):
    """Compute time-based features."""
    df = df.copy()
    df['hour_of_day'] = df['CRSDepTime'] // 100
    df['day_of_week'] = df['FlightDate'].dt.dayofweek
    df['month'] = df['FlightDate'].dt.month
    df['day_of_month'] = df['FlightDate'].dt.day
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    # Late flights tend to be more delayed (cascading delays accumulate)
    df['is_evening'] = (df['hour_of_day'] >= 17).astype(int)
    df['is_redeye'] = ((df['hour_of_day'] >= 21) | (df['hour_of_day'] <= 5)).astype(int)
    return df


def make_target(df, threshold_minutes=15):
    """
    Create binary delay target: 1 if arrival delay >= threshold, 0 otherwise.
    """
    return (df['ArrDelay'] >= threshold_minutes).astype(int)


def temporal_cv_splits(df, n_folds=3):
    """
    Temporal cross-validation: train on past, test on future.

    Splits by date so that all training data is temporally before test data.
    """
    dates = sorted(df['FlightDate'].unique())
    n_dates = len(dates)
    fold_size = n_dates // (n_folds + 1)

    splits = []
    for i in range(n_folds):
        # Training: all dates up to fold boundary
        train_end = dates[(i + 1) * fold_size]
        # Test: next fold_size dates
        test_start = train_end
        test_end = dates[min((i + 2) * fold_size, n_dates - 1)]

        train_mask = df['FlightDate'] <= train_end
        test_mask = (df['FlightDate'] > test_start) & (df['FlightDate'] <= test_end)

        train_idx = df.index[train_mask].tolist()
        test_idx = df.index[test_mask].tolist()

        if len(train_idx) > 0 and len(test_idx) > 0:
            splits.append((train_idx, test_idx))

    return splits


def build_features(df):
    """
    Full feature engineering pipeline.

    Returns DataFrame with all features and the original columns.
    """
    df = compute_rotation_features(df)
    df = compute_airport_features(df)
    df = compute_temporal_features(df)
    return df


def get_feature_columns(df):
    """Return list of feature column names for modeling."""
    feature_cols = [
        # Rotation features (key contribution)
        'prior_flight_arr_delay',
        'prior_flight_dep_delay',
        'rotation_position',
        'cumulative_delay',
        'turnaround_time',
        'prior_flight_late_aircraft',
        # Airport congestion features
        'origin_dep_delay_mean_1h',
        'origin_flights_1h',
        'origin_dep_delay_std_1h',
        'dest_arr_delay_mean_1h',
        'dest_flights_1h',
        # Temporal features
        'hour_of_day',
        'day_of_week',
        'month',
        'is_weekend',
        'is_evening',
        'is_redeye',
        # Flight characteristics
        'Distance',
        'TaxiOut',
    ]
    return [c for c in feature_cols if c in df.columns]
