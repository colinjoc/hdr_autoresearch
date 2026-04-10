"""
Enhanced model with HDR loop features for flight delay propagation.

Key additions over baseline prepare.py:
- Carrier buffer factor (derived from real carrier statistics)
- prev_delay x buffer interaction
- Log-transformed previous delay
- Morning/evening binary features
- Hub-to-hub route indicator
- Regional carrier flag
- Schedule buffer minutes

This file is the ONLY thing that changes during HDR iterations.
"""
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from prepare import load_clean, build_features, get_feature_columns, temporal_cv_splits

# Major US hub airports (top 30 by passenger volume)
HUB_AIRPORTS = {
    'ATL', 'DFW', 'DEN', 'ORD', 'LAX', 'CLT', 'MCO', 'LAS', 'PHX', 'MIA',
    'SEA', 'IAH', 'JFK', 'EWR', 'SFO', 'FLL', 'MSP', 'BOS', 'DTW', 'LGA',
    'PHL', 'SLC', 'DCA', 'SAN', 'BWI', 'TPA', 'IAD', 'MDW', 'HNL', 'DAL',
}

# Regional carrier codes
REGIONAL_CARRIERS = {'MQ', 'OO', 'YX', '9E', 'G4', 'QX', 'ZW', 'OH'}


def compute_carrier_buffer_factor(df):
    """
    Compute carrier-specific schedule buffer factor from real data.

    For each carrier, measure the ratio of actual turnaround time to the
    minimum feasible turnaround. Carriers that pad more have lower
    propagation risk.

    Returns a Series mapping carrier -> buffer_factor.
    """
    # Only use flights with valid rotation data (not first leg)
    mask = df['prior_flight_arr_delay'].notna() & df['turnaround_time'].notna()
    valid = df[mask].copy()

    if len(valid) == 0:
        return pd.Series(dtype=float)

    # Median turnaround per carrier (higher = more buffer)
    carrier_turnaround = valid.groupby('Reporting_Airline')['turnaround_time'].median()

    # Normalize: global median turnaround is 1.0
    global_median = carrier_turnaround.median()
    if global_median == 0:
        return carrier_turnaround * 0 + 1.0

    # Invert: carriers with SHORT turnarounds get HIGH buffer factor
    # (meaning they propagate MORE delay)
    buffer_factor = global_median / carrier_turnaround
    buffer_factor = buffer_factor.clip(0.5, 2.0)

    return buffer_factor


def compute_enhanced_features(df):
    """
    Add HDR loop features on top of base features.

    Parameters
    ----------
    df : DataFrame with base features already computed (from build_features)

    Returns
    -------
    DataFrame with additional columns
    """
    df = df.copy()

    # --- Carrier buffer factor ---
    buffer_factors = compute_carrier_buffer_factor(df)
    if len(buffer_factors) > 0:
        df['carrier_buffer_factor'] = df['Reporting_Airline'].map(buffer_factors)
        df['carrier_buffer_factor'] = df['carrier_buffer_factor'].fillna(1.0)
    else:
        df['carrier_buffer_factor'] = 1.0

    # --- Interaction: previous delay x buffer ---
    prev_delay = df['prior_flight_arr_delay'].fillna(0)
    df['prev_delay_x_buffer'] = prev_delay * df['carrier_buffer_factor']

    # --- Log-transformed previous delay ---
    df['log_prev_delay'] = np.log1p(np.maximum(prev_delay, 0))

    # --- Hub features ---
    df['origin_is_hub'] = df['Origin'].isin(HUB_AIRPORTS).astype(int)
    df['dest_is_hub'] = df['Dest'].isin(HUB_AIRPORTS).astype(int)
    df['is_hub_to_hub'] = (df['origin_is_hub'] & df['dest_is_hub']).astype(int)

    # --- Regional carrier flag ---
    df['is_regional'] = df['Reporting_Airline'].isin(REGIONAL_CARRIERS).astype(int)

    # --- Schedule buffer: time between scheduled arrival of prior flight
    #     and scheduled departure of this one ---
    # Using turnaround_time as proxy (already computed in base features)
    # Additional: explicit buffer relative to minimum turnaround
    if 'turnaround_time' in df.columns:
        # Min turnaround by distance bucket
        df['_dist_bucket'] = pd.cut(df['Distance'], bins=[0, 500, 1000, 2000, 10000],
                                     labels=['short', 'medium', 'long', 'xlong'])
        min_turnaround = df.groupby('_dist_bucket', observed=False)['turnaround_time'].transform('quantile', 0.1)
        df['buffer_over_min'] = df['turnaround_time'] - min_turnaround
        df.drop(columns=['_dist_bucket'], inplace=True)
    else:
        df['buffer_over_min'] = 0.0

    # --- Morning clean start indicator (first-wave flights) ---
    df['morning_flight'] = ((df['hour_of_day'] >= 6) & (df['hour_of_day'] <= 9)).astype(int)

    # --- Cyclic time encoding ---
    df['dep_hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
    df['dep_hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
    df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

    return df


def get_enhanced_feature_columns():
    """Return full list of enhanced feature columns."""
    return [
        # Base rotation features
        'prior_flight_arr_delay',
        'prior_flight_dep_delay',
        'rotation_position',
        'cumulative_delay',
        'turnaround_time',
        'prior_flight_late_aircraft',
        # Enhanced rotation features (HDR)
        'carrier_buffer_factor',
        'prev_delay_x_buffer',
        'log_prev_delay',
        'buffer_over_min',
        # Airport features
        'origin_dep_delay_mean_1h',
        'origin_flights_1h',
        'origin_dep_delay_std_1h',
        'dest_arr_delay_mean_1h',
        'dest_flights_1h',
        # Hub/route features
        'origin_is_hub',
        'dest_is_hub',
        'is_hub_to_hub',
        'is_regional',
        # Temporal features
        'morning_flight',
        'is_evening',
        'dep_hour_sin',
        'dep_hour_cos',
        'dow_sin',
        'dow_cos',
        'month_sin',
        'month_cos',
        # Flight characteristics
        'Distance',
        'TaxiOut',
    ]


def prepare_enhanced_data(year, months):
    """Full pipeline: load, clean, base features, enhanced features."""
    df = load_clean(year, months)
    df = build_features(df)
    df = compute_enhanced_features(df)
    return df


def find_super_spreader_routes(df, min_flights=100):
    """
    Identify routes where delays are most contagious.

    A 'super-spreader' route is one where:
    1. Delays are frequent
    2. Delays propagate deeply through subsequent flights

    Returns DataFrame of routes sorted by propagation risk score.
    """
    # Only look at flights with rotation data
    mask = df['prior_flight_arr_delay'].notna()
    valid = df[mask].copy()

    # For each route (Origin-Dest), compute:
    # - Mean arrival delay
    # - Fraction of flights delayed >= 15 min
    # - Mean propagated delay (LateAircraftDelay)
    # - Traffic volume
    route_stats = valid.groupby(['Origin', 'Dest']).agg(
        mean_arr_delay=('ArrDelay', 'mean'),
        delay_rate=('ArrDelay', lambda x: (x >= 15).mean()),
        mean_late_aircraft=('LateAircraftDelay', lambda x: x.fillna(0).mean()),
        mean_prev_delay=('prior_flight_arr_delay', 'mean'),
        n_flights=('ArrDelay', 'count'),
    ).reset_index()

    # Filter to routes with enough traffic
    route_stats = route_stats[route_stats['n_flights'] >= min_flights]

    # Propagation risk score: delay_rate * mean_late_aircraft * log(n_flights)
    route_stats['propagation_score'] = (
        route_stats['delay_rate'] *
        route_stats['mean_late_aircraft'] *
        np.log1p(route_stats['n_flights'])
    )

    route_stats = route_stats.sort_values('propagation_score', ascending=False)

    return route_stats


def carrier_propagation_analysis(df):
    """
    Analyze how different carriers handle delay propagation.

    Returns DataFrame with per-carrier propagation statistics.
    """
    mask = df['prior_flight_arr_delay'].notna() & (df['rotation_position'] > 1)
    valid = df[mask].copy()

    carrier_stats = valid.groupby('Reporting_Airline').agg(
        mean_arr_delay=('ArrDelay', 'mean'),
        delay_rate=('ArrDelay', lambda x: (x >= 15).mean()),
        mean_prev_delay=('prior_flight_arr_delay', 'mean'),
        mean_late_aircraft=('LateAircraftDelay', lambda x: x.fillna(0).mean()),
        mean_turnaround=('turnaround_time', lambda x: x.dropna().mean()),
        buffer_factor=('carrier_buffer_factor', 'first'),
        n_flights=('ArrDelay', 'count'),
    ).reset_index()

    # Propagation rate: fraction of incoming delay that appears in current delay
    carrier_stats['propagation_rate'] = (
        carrier_stats['mean_late_aircraft'] / carrier_stats['mean_prev_delay'].clip(1)
    )

    carrier_stats = carrier_stats.sort_values('propagation_rate', ascending=False)
    return carrier_stats


def hourly_delay_accumulation(df):
    """
    Measure how delays accumulate through the day by hour.

    Returns DataFrame with per-hour statistics.
    """
    hourly = df.groupby('hour_of_day').agg(
        mean_arr_delay=('ArrDelay', 'mean'),
        delay_rate=('ArrDelay', lambda x: (x >= 15).mean()),
        mean_late_aircraft=('LateAircraftDelay', lambda x: x.fillna(0).mean()),
        n_flights=('ArrDelay', 'count'),
    ).reset_index()

    return hourly


def airport_propagation_scores(df, min_flights=500):
    """
    Compute propagation scores for individual airports.

    Returns DataFrame with per-airport propagation statistics.
    """
    mask = df['prior_flight_arr_delay'].notna()
    valid = df[mask].copy()

    origin_stats = valid.groupby('Origin').agg(
        mean_dep_delay=('DepDelay', 'mean'),
        delay_rate=('DepDelay', lambda x: (x >= 15).mean()),
        mean_late_aircraft=('LateAircraftDelay', lambda x: x.fillna(0).mean()),
        n_flights=('DepDelay', 'count'),
    ).reset_index()

    origin_stats = origin_stats[origin_stats['n_flights'] >= min_flights]
    origin_stats['propagation_score'] = (
        origin_stats['delay_rate'] *
        origin_stats['mean_late_aircraft'] *
        np.log1p(origin_stats['n_flights'])
    )
    origin_stats = origin_stats.sort_values('propagation_score', ascending=False)
    origin_stats.rename(columns={'Origin': 'airport'}, inplace=True)

    return origin_stats
