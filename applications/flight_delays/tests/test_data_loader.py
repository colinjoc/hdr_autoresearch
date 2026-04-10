"""Tests for BTS data loading and preprocessing."""
import pytest
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestLoadRawData:
    """Test that we can load and clean raw BTS CSVs."""

    def test_load_single_month(self):
        from prepare import load_raw_month
        df = load_raw_month(2024, 1)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 500_000  # ~547k flights in Jan 2024
        assert 'FlightDate' in df.columns
        assert 'Tail_Number' in df.columns
        assert 'DepDelay' in df.columns
        assert 'ArrDelay' in df.columns

    def test_load_multiple_months(self):
        from prepare import load_raw_months
        df = load_raw_months(2024, [1, 2])
        assert len(df) > 1_000_000  # Two months combined

    def test_required_columns_present(self):
        from prepare import load_raw_month, REQUIRED_COLUMNS
        df = load_raw_month(2024, 1)
        for col in REQUIRED_COLUMNS:
            assert col in df.columns, f"Missing required column: {col}"

    def test_flight_date_is_datetime(self):
        from prepare import load_raw_month
        df = load_raw_month(2024, 1)
        assert pd.api.types.is_datetime64_any_dtype(df['FlightDate'])

    def test_cancelled_flights_excluded_from_delay_analysis(self):
        from prepare import load_clean
        df = load_clean(2024, [1])
        # Clean data should exclude cancelled flights for delay analysis
        assert df['Cancelled'].sum() == 0


class TestTailNumberRotation:
    """Test reconstruction of aircraft rotation chains from tail numbers."""

    def test_build_rotation_chain(self):
        from prepare import build_rotation_chains
        # Use a small slice of real data
        from prepare import load_clean
        df = load_clean(2024, [1])
        # Pick a tail number that has multiple flights
        sample_tail = df.groupby('Tail_Number').size().idxmax()
        chains = build_rotation_chains(df, date='2024-01-15')
        assert isinstance(chains, dict)
        # Chains should map tail_number -> sorted list of flights
        assert len(chains) > 0

    def test_chain_is_chronologically_sorted(self):
        from prepare import build_rotation_chains, load_clean
        df = load_clean(2024, [1])
        chains = build_rotation_chains(df, date='2024-01-15')
        for tail, flights in list(chains.items())[:10]:
            dep_times = flights['CRSDepTime'].values
            assert all(dep_times[i] <= dep_times[i+1] for i in range(len(dep_times)-1)), \
                f"Chain for {tail} not sorted by departure time"

    def test_prior_flight_delay_feature(self):
        """The key feature: was the previous flight on this aircraft delayed?"""
        from prepare import compute_rotation_features
        from prepare import load_clean
        df = load_clean(2024, [1])
        df_feat = compute_rotation_features(df)
        assert 'prior_flight_arr_delay' in df_feat.columns
        assert 'prior_flight_dep_delay' in df_feat.columns
        # Not all flights have a prior flight (first of day), so some NaN expected
        assert df_feat['prior_flight_arr_delay'].notna().sum() > 0
        assert df_feat['prior_flight_arr_delay'].notna().mean() > 0.3  # Most flights should have prior

    def test_rotation_position_feature(self):
        """How many legs has this aircraft already flown today?"""
        from prepare import compute_rotation_features
        from prepare import load_clean
        df = load_clean(2024, [1])
        df_feat = compute_rotation_features(df)
        assert 'rotation_position' in df_feat.columns
        assert df_feat['rotation_position'].min() >= 1
        assert df_feat['rotation_position'].max() <= 15  # Aircraft rarely do >10 legs/day


class TestFeatureEngineering:
    """Test all feature categories."""

    def test_airport_congestion_features(self):
        from prepare import compute_airport_features, load_clean
        df = load_clean(2024, [1])
        df_feat = compute_airport_features(df)
        assert 'origin_dep_delay_mean_1h' in df_feat.columns
        assert 'origin_flights_1h' in df_feat.columns
        assert 'dest_arr_delay_mean_1h' in df_feat.columns

    def test_temporal_features(self):
        from prepare import compute_temporal_features, load_clean
        df = load_clean(2024, [1])
        df_feat = compute_temporal_features(df)
        assert 'hour_of_day' in df_feat.columns
        assert 'day_of_week' in df_feat.columns
        assert 'month' in df_feat.columns

    def test_delay_cause_decomposition(self):
        """BTS provides 5 delay cause categories for delayed flights."""
        from prepare import load_clean
        df = load_clean(2024, [1])
        cause_cols = ['CarrierDelay', 'WeatherDelay', 'NASDelay',
                      'SecurityDelay', 'LateAircraftDelay']
        for col in cause_cols:
            assert col in df.columns


class TestTargetVariable:
    """Test that we define the target correctly."""

    def test_binary_delay_target(self):
        from prepare import make_target
        from prepare import load_clean
        df = load_clean(2024, [1])
        y = make_target(df, threshold_minutes=15)
        assert set(y.unique()).issubset({0, 1})
        # Some flights should be delayed
        assert y.mean() > 0.1
        assert y.mean() < 0.5

    def test_continuous_delay_target(self):
        from prepare import load_clean
        df = load_clean(2024, [1])
        # ArrDelay should be the continuous target
        assert df['ArrDelay'].dtype in [np.float64, np.float32, np.int64]


class TestTemporalCV:
    """Test temporal cross-validation split."""

    def test_temporal_split(self):
        from prepare import temporal_cv_splits
        from prepare import load_clean
        df = load_clean(2024, [1, 2, 3])
        splits = temporal_cv_splits(df, n_folds=3)
        assert len(splits) == 3
        for train_idx, test_idx in splits:
            train_dates = df.iloc[train_idx]['FlightDate']
            test_dates = df.iloc[test_idx]['FlightDate']
            # All training dates must be before all test dates
            assert train_dates.max() <= test_dates.min()
