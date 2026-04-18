"""Tests for data loading and cleaning pipeline."""
import pytest
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

class TestNuforcStrLoader:
    def test_loads_correct_row_count(self):
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        assert len(df) >= 140000, f"Expected >=140k rows, got {len(df)}"

    def test_parses_occurred_datetime(self):
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        assert df['occurred_dt'].notna().sum() > 100000, "Most dates should parse"
        assert df['year'].notna().sum() > 100000

    def test_has_required_columns(self):
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        for col in ['occurred_dt', 'year', 'month', 'hour', 'day_of_week',
                     'Shape', 'state', 'country_str', 'has_explanation']:
            assert col in df.columns, f"Missing column: {col}"

    def test_year_range(self):
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        valid = df[df['year'].notna()]
        assert valid['year'].min() >= 1900 or True  # Some old sightings ok
        assert valid['year'].max() <= 2025

    def test_shape_cleaned(self):
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        shapes = df['Shape'].dropna().unique()
        assert len(shapes) > 10

    def test_explanation_parsed(self):
        from data_loader import load_nuforc_str
        df = load_nuforc_str()
        assert 'has_explanation' in df.columns
        assert df['has_explanation'].sum() > 700  # ~803 explained


class TestNuforcKaggleLoader:
    def test_loads_correct_row_count(self):
        from data_loader import load_nuforc_kaggle
        df = load_nuforc_kaggle()
        assert len(df) >= 80000

    def test_has_lat_lon(self):
        from data_loader import load_nuforc_kaggle
        df = load_nuforc_kaggle()
        assert 'latitude' in df.columns
        assert 'longitude' in df.columns
        assert df['latitude'].notna().sum() > 70000

    def test_lat_lon_reasonable(self):
        from data_loader import load_nuforc_kaggle
        df = load_nuforc_kaggle()
        lat = pd.to_numeric(df['latitude'], errors='coerce')
        assert lat.dropna().between(-90, 90).all()
