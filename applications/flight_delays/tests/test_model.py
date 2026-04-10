"""Tests for enhanced model features (HDR loop)."""
import pytest
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCarrierBufferFactor:
    """Test carrier-specific buffer factor computation."""

    def test_buffer_factor_computed(self):
        from model import prepare_enhanced_data
        df = prepare_enhanced_data(2024, [1])
        assert 'carrier_buffer_factor' in df.columns
        assert df['carrier_buffer_factor'].notna().all()

    def test_buffer_factor_range(self):
        from model import prepare_enhanced_data
        df = prepare_enhanced_data(2024, [1])
        # Buffer factors should be between 0.5 and 2.0
        assert df['carrier_buffer_factor'].min() >= 0.5
        assert df['carrier_buffer_factor'].max() <= 2.0

    def test_carriers_differ(self):
        from model import prepare_enhanced_data
        df = prepare_enhanced_data(2024, [1])
        unique_factors = df.groupby('Reporting_Airline')['carrier_buffer_factor'].first()
        # At least some carriers should have different buffer factors
        assert unique_factors.nunique() > 3


class TestInteractionFeatures:
    """Test prev_delay x buffer interaction."""

    def test_interaction_computed(self):
        from model import prepare_enhanced_data
        df = prepare_enhanced_data(2024, [1])
        assert 'prev_delay_x_buffer' in df.columns

    def test_interaction_zero_when_no_prior(self):
        from model import prepare_enhanced_data
        df = prepare_enhanced_data(2024, [1])
        # First leg flights have no prior delay, so interaction should be 0
        first_legs = df[df['rotation_position'] == 1]
        # prior_flight_arr_delay is NaN for first legs, filled to 0
        assert (first_legs['prev_delay_x_buffer'] == 0).all()

    def test_log_prev_delay(self):
        from model import prepare_enhanced_data
        df = prepare_enhanced_data(2024, [1])
        assert 'log_prev_delay' in df.columns
        # log1p(0) = 0 for first legs
        assert df['log_prev_delay'].min() >= 0


class TestHubFeatures:
    """Test hub airport identification."""

    def test_hub_flags_computed(self):
        from model import prepare_enhanced_data
        df = prepare_enhanced_data(2024, [1])
        assert 'origin_is_hub' in df.columns
        assert 'dest_is_hub' in df.columns
        assert 'is_hub_to_hub' in df.columns

    def test_known_hubs_flagged(self):
        from model import prepare_enhanced_data
        df = prepare_enhanced_data(2024, [1])
        # ATL is definitely a hub
        atl_flights = df[df['Origin'] == 'ATL']
        assert len(atl_flights) > 0
        assert atl_flights['origin_is_hub'].all()

    def test_hub_to_hub_subset(self):
        from model import prepare_enhanced_data
        df = prepare_enhanced_data(2024, [1])
        # Hub-to-hub should be subset of hub origins AND hub destinations
        h2h = df[df['is_hub_to_hub'] == 1]
        assert h2h['origin_is_hub'].all()
        assert h2h['dest_is_hub'].all()


class TestEnhancedFeatureColumns:
    """Test that all expected columns are present."""

    def test_all_enhanced_columns(self):
        from model import prepare_enhanced_data, get_enhanced_feature_columns
        df = prepare_enhanced_data(2024, [1])
        expected = get_enhanced_feature_columns()
        for col in expected:
            assert col in df.columns, f"Missing enhanced feature: {col}"


class TestSuperSpreaderRoutes:
    """Test super-spreader route identification."""

    def test_returns_routes(self):
        from model import prepare_enhanced_data, find_super_spreader_routes
        df = prepare_enhanced_data(2024, [1])
        routes = find_super_spreader_routes(df, min_flights=100)
        assert isinstance(routes, pd.DataFrame)
        assert len(routes) > 0
        assert 'Origin' in routes.columns
        assert 'Dest' in routes.columns
        assert 'propagation_score' in routes.columns

    def test_routes_sorted_by_score(self):
        from model import prepare_enhanced_data, find_super_spreader_routes
        df = prepare_enhanced_data(2024, [1])
        routes = find_super_spreader_routes(df, min_flights=100)
        scores = routes['propagation_score'].values
        assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))


class TestCarrierPropagation:
    """Test carrier-level propagation analysis."""

    def test_returns_carriers(self):
        from model import prepare_enhanced_data, carrier_propagation_analysis
        df = prepare_enhanced_data(2024, [1])
        carriers = carrier_propagation_analysis(df)
        assert isinstance(carriers, pd.DataFrame)
        assert len(carriers) > 5  # Multiple carriers in data
        assert 'Reporting_Airline' in carriers.columns
        assert 'propagation_rate' in carriers.columns


class TestHourlyAccumulation:
    """Test hourly delay accumulation."""

    def test_returns_hours(self):
        from model import prepare_enhanced_data, hourly_delay_accumulation
        df = prepare_enhanced_data(2024, [1])
        hourly = hourly_delay_accumulation(df)
        assert isinstance(hourly, pd.DataFrame)
        assert len(hourly) >= 18  # Most hours of day should have flights


class TestAirportScores:
    """Test airport propagation scores."""

    def test_returns_airports(self):
        from model import prepare_enhanced_data, airport_propagation_scores
        df = prepare_enhanced_data(2024, [1])
        airports = airport_propagation_scores(df, min_flights=500)
        assert isinstance(airports, pd.DataFrame)
        assert len(airports) > 20
        assert 'airport' in airports.columns
        assert 'propagation_score' in airports.columns
