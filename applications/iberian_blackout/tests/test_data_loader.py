"""Tests for the data loader module."""
import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_generation_daily,
    load_demand_hourly,
    load_exchange_daily,
    load_prices_hourly,
    build_daily_feature_matrix,
    compute_grid_stress_indicators,
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class TestLoadGenerationDaily:
    def test_returns_dataframe(self):
        df = load_generation_daily(DATA_DIR, "apr2025")
        assert isinstance(df, pd.DataFrame)

    def test_has_expected_columns(self):
        df = load_generation_daily(DATA_DIR, "apr2025")
        # Must have at least these technology types
        expected = {"Hydro", "Nuclear", "Solar photovoltaic", "Wind"}
        assert expected.issubset(set(df.columns)), f"Missing: {expected - set(df.columns)}"

    def test_has_date_index(self):
        df = load_generation_daily(DATA_DIR, "apr2025")
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_values_are_positive_or_zero(self):
        df = load_generation_daily(DATA_DIR, "apr2025")
        # Generation values should be non-negative (MWh daily)
        assert (df >= 0).all().all(), "Negative generation values found"

    def test_april_has_30_days(self):
        df = load_generation_daily(DATA_DIR, "apr2025")
        assert len(df) == 30

    def test_multiple_months_loadable(self):
        for month in ["jan2025", "feb2025", "mar2025", "apr2025", "may2025"]:
            df = load_generation_daily(DATA_DIR, month)
            assert len(df) > 25, f"{month} has too few rows: {len(df)}"


class TestLoadDemandHourly:
    def test_returns_dataframe(self):
        df = load_demand_hourly(DATA_DIR, "apr2025")
        assert isinstance(df, pd.DataFrame)

    def test_has_demand_columns(self):
        df = load_demand_hourly(DATA_DIR, "apr2025")
        assert "demand_MW" in df.columns or "Demand" in df.columns

    def test_has_datetime_index(self):
        df = load_demand_hourly(DATA_DIR, "apr2025")
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_demand_values_reasonable(self):
        df = load_demand_hourly(DATA_DIR, "apr2025")
        col = "demand_MW" if "demand_MW" in df.columns else "Demand"
        # Spanish demand typically 18-40 GW
        valid = df[col].dropna()
        assert valid.max() < 50000, f"Max demand {valid.max()} MW too high"
        # Demand can drop very low during blackout (Apr 28 2025)
        assert valid.min() > 0, f"Min demand {valid.min()} MW negative"


class TestLoadExchangeDaily:
    def test_returns_dataframe(self):
        df = load_exchange_daily(DATA_DIR, "france", "apr")
        assert isinstance(df, pd.DataFrame)

    def test_has_export_import(self):
        df = load_exchange_daily(DATA_DIR, "france", "apr")
        assert "exports" in df.columns or "Exports" in df.columns
        assert "imports" in df.columns or "Imports" in df.columns

    def test_all_countries(self):
        for country in ["france", "portugal", "morocco"]:
            df = load_exchange_daily(DATA_DIR, country, "apr")
            assert len(df) > 0, f"No data for {country}"


class TestLoadPricesHourly:
    def test_returns_dataframe(self):
        df = load_prices_hourly(DATA_DIR, "apr")
        assert isinstance(df, pd.DataFrame)

    def test_has_price_column(self):
        df = load_prices_hourly(DATA_DIR, "apr")
        price_cols = [c for c in df.columns if "price" in c.lower() or "spot" in c.lower() or "EUR" in c]
        assert len(price_cols) > 0, f"No price column found in {df.columns.tolist()}"


class TestBuildDailyFeatureMatrix:
    def test_returns_dataframe(self):
        df = build_daily_feature_matrix(DATA_DIR)
        assert isinstance(df, pd.DataFrame)

    def test_has_many_features(self):
        df = build_daily_feature_matrix(DATA_DIR)
        assert df.shape[1] >= 10, f"Only {df.shape[1]} features"

    def test_no_all_nan_columns(self):
        df = build_daily_feature_matrix(DATA_DIR)
        nan_cols = df.columns[df.isna().all()]
        assert len(nan_cols) == 0, f"All-NaN columns: {nan_cols.tolist()}"

    def test_has_blackout_day(self):
        df = build_daily_feature_matrix(DATA_DIR)
        # April 28 should be in the index
        apr28 = pd.Timestamp("2025-04-28")
        assert apr28 in df.index or any(d.date() == apr28.date() for d in df.index)


class TestGridStressIndicators:
    def test_returns_dataframe(self):
        features = build_daily_feature_matrix(DATA_DIR)
        stress = compute_grid_stress_indicators(features)
        assert isinstance(stress, pd.DataFrame)

    def test_has_stress_columns(self):
        features = build_daily_feature_matrix(DATA_DIR)
        stress = compute_grid_stress_indicators(features)
        # Should have indicators like renewable_fraction, sync_gen_fraction, etc.
        assert stress.shape[1] >= 3

    def test_stress_values_bounded(self):
        features = build_daily_feature_matrix(DATA_DIR)
        stress = compute_grid_stress_indicators(features)
        # Fraction-based indicators should be 0-1
        frac_cols = [c for c in stress.columns if "fraction" in c]
        for c in frac_cols:
            valid = stress[c].dropna()
            if len(valid) > 0:
                assert valid.min() >= -0.1, f"{c} min={valid.min()}"
                assert valid.max() <= 1.5, f"{c} max={valid.max()}"
